#!/usr/bin/env python3
"""Build orbitron_panel_shuttle.ac — three shuttle guarded toggles on the Orbitron panel plane."""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from pathlib import Path

import numpy as np

# Switch offsets in Operator_Panel local frame: (along row, along up on slanted face).
# Row is the panel long axis (+X); up tilts toward Screen. Do not use mesh XYZ deltas.
PANEL_SWITCH_ROW: dict[str, tuple[float, float]] = {
    "Panel_Switch_APU": (-0.22, 0.0),
    "Panel_Switch_Starter": (-0.08, 0.0),
    "Panel_Switch_Bleed": (0.06, 0.0),
    # IGNITE: CadQuery Big_Red_Button on orbitron.ac (not shuttle abort_cmd)
    # Same R1 MN-bus levers as toggles (full scale + guards) — analog row below
    "Panel_Lever_Beam": (-0.10, -0.075),
    "Panel_Lever_Compressor": (0.10, -0.075),
}

# Display dimmer knob (DIM/BRT stripe pointer) — cockpit.xml L1-disp-dim.
SHUTTLE_DIM_KNOB = "L1-disp-dim"
SHUTTLE_DIM_KNOB_AXIS = (1.0, 0.0, 0.266)
RATE_KNOB_NAMES = ("Panel_Lever_Beam", "Panel_Lever_Compressor")
# Upscale ~2 cm shuttle knob to ~5–6 cm on the Orbitron panel.
DIM_KNOB_SCALE_MULT = 2.15
# Fallback when orbitron.ac is missing (matches -30° X slanted panel in mesh coords).
PANEL_FRAME_FALLBACK: dict[str, tuple[float, float, float]] = {
    "row": (1.0, 0.0, 0.0),
    "up": (0.0, 0.5, -0.8660254),
    "normal": (0.0, 0.8660254, 0.5),
    "centroid": (-1.4, 1.3, 4.9),
}

SOURCE_SWITCHES = {
    "cont-bus-pwr-mn-a": "Panel_Switch_APU",
    "cont-bus-pwr-mn-b": "Panel_Switch_Starter",
    "cont-bus-pwr-mn-c": "Panel_Switch_Bleed",
}

GUARD_SOURCE = "R1-guards"
GUARD_TEMPLATE_LEVER = "cont-bus-pwr-mn-a"
ABORT_LEVER = "abort_cmd"
ABORT_LIGHT = "indicator_light_abort"

# Scale shuttle levers to Orbitron row spacing.
# Single U-rail crop around cont-bus-pwr-mn-a (~120 verts at this half-extent).
GUARD_BBOX_HALF = (0.018, 0.028, 0.015)
SWITCH_STANDOFF_M = 0.042  # proud of panel along +normal (toward operator)
LEVER_SCALE_MIN = 1.55
LEVER_SCALE_MAX = 2.35
# Mount on grey Operator_Panel in orbitron.ac — no extra backplate mesh.


def _normalize(v: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / length for c in v)


def _cross(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _basis_matrix(
    row: tuple[float, float, float],
    up: tuple[float, float, float],
    normal: tuple[float, float, float],
) -> list[list[float]]:
    return [
        [row[0], up[0], normal[0]],
        [row[1], up[1], normal[1]],
        [row[2], up[2], normal[2]],
    ]


def _transpose(m: list[list[float]]) -> list[list[float]]:
    return [[m[j][i] for j in range(3)] for i in range(3)]


def _mat_mul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [
        [sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]


def _mat_vec(m, v):
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    )


def _parse_objects(ac_text: str) -> dict[str, list[str]]:
    lines = ac_text.splitlines()
    objects: dict[str, list[str]] = {}
    i = 0
    while i < len(lines):
        if lines[i].strip() == "OBJECT poly" and i + 1 < len(lines):
            name_m = re.match(r'name\s+"(.*)"', lines[i + 1].strip())
            if not name_m:
                i += 1
                continue
            name = name_m.group(1)
            start = i
            i += 2
            while i < len(lines):
                if lines[i].strip() == "kids 0":
                    objects[name] = lines[start : i + 1]
                    i += 1
                    break
                i += 1
            continue
        i += 1
    return objects


def _object_numvert(obj_lines: list[str]) -> tuple[int, int]:
    for i, ln in enumerate(obj_lines):
        m = re.match(r"numvert\s+(\d+)", ln.strip())
        if m:
            return int(m.group(1)), i + 1
    return 0, -1


def _object_centroid(obj_lines: list[str]) -> tuple[float, float, float]:
    nvert, nv_i = _object_numvert(obj_lines)
    if nvert <= 0:
        return (0.0, 0.0, 0.0)
    xs = ys = zs = 0.0
    c = 0
    for j in range(nv_i, min(nv_i + nvert, len(obj_lines))):
        p = obj_lines[j].split()
        if len(p) == 3:
            x, y, z = map(float, p)
            xs += x
            ys += y
            zs += z
            c += 1
    return (xs / c, ys / c, zs / c) if c else (0.0, 0.0, 0.0)


def _object_vertices(obj_lines: list[str]) -> list[tuple[float, float, float]]:
    nvert, nv_i = _object_numvert(obj_lines)
    verts: list[tuple[float, float, float]] = []
    for j in range(nv_i, min(nv_i + nvert, len(obj_lines))):
        p = obj_lines[j].split()
        if len(p) == 3:
            verts.append(tuple(map(float, p)))
    return verts


PanelFrame = tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]


def _operator_panel_frame(
    panel_obj: list[str],
    screen_obj: list[str] | None = None,
) -> PanelFrame:
    """Orthonormal frame from Operator_Panel mesh (row, up, normal, centroid)."""
    verts = _object_vertices(panel_obj)
    if len(verts) < 4:
        fb = PANEL_FRAME_FALLBACK
        return fb["row"], fb["up"], fb["normal"], fb["centroid"]
    pc = _object_centroid(panel_obj)
    arr = np.array(verts, dtype=float) - pc
    _, _, vh = np.linalg.svd(arr, full_matrices=False)
    row = tuple(float(c) for c in vh[0])
    normal = tuple(float(c) for c in vh[2])
    if normal[2] < 0.0:
        normal = tuple(-c for c in normal)
    if row[0] < 0.0:
        row = tuple(-c for c in row)
    up = _normalize(_cross(normal, row))
    if screen_obj is not None:
        sc = _object_centroid(screen_obj)
        to_screen = (sc[0] - pc[0], sc[1] - pc[1], sc[2] - pc[2])
        if _dot(up, to_screen) < 0.0:
            up = tuple(-c for c in up)
            normal = tuple(-c for c in normal)
    return row, up, normal, pc


def _targets_on_panel(
    frame: PanelFrame,
    offsets: dict[str, tuple[float, float]],
) -> dict[str, tuple[float, float, float]]:
    row, up, normal, pc = frame
    out: dict[str, tuple[float, float, float]] = {}
    for switch, (dr, du) in offsets.items():
        out[switch] = (
            pc[0] + dr * row[0] + du * up[0] + SWITCH_STANDOFF_M * normal[0],
            pc[1] + dr * row[1] + du * up[1] + SWITCH_STANDOFF_M * normal[1],
            pc[2] + dr * row[2] + du * up[2] + SWITCH_STANDOFF_M * normal[2],
        )
    return out


def _fallback_panel_frame() -> PanelFrame:
    fb = PANEL_FRAME_FALLBACK
    return fb["row"], fb["up"], fb["normal"], fb["centroid"]


def _resolve_targets_and_frame(
    orbitron_ac: Path | None,
) -> tuple[dict[str, tuple[float, float, float]], PanelFrame]:
    if orbitron_ac is not None and orbitron_ac.is_file():
        objs = _parse_objects(orbitron_ac.read_text(encoding="utf-8", errors="replace"))
        if "Operator_Panel" in objs:
            frame = _operator_panel_frame(
                objs["Operator_Panel"], objs.get("Screen")
            )
            return _targets_on_panel(frame, PANEL_SWITCH_ROW), frame
    frame = _fallback_panel_frame()
    return _targets_on_panel(frame, PANEL_SWITCH_ROW), frame


def _shuttle_r1_basis(objects: dict[str, list[str]]) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]:
    """Shuttle R1 MN-bus row in cockpit.ac (panel faces +Y in shuttle coords)."""
    sa = _object_centroid(objects["cont-bus-pwr-mn-a"])
    sc = _object_centroid(objects["cont-bus-pwr-mn-c"])
    row = _normalize((sc[0] - sa[0], sc[1] - sa[1], sc[2] - sa[2]))
    shuttle_face = (0.0, 1.0, 0.0)
    normal = _normalize(_cross(row, shuttle_face))
    if normal[1] < 0.0:
        normal = tuple(-c for c in normal)
    up = _normalize(_cross(normal, row))
    return row, up, normal


def _fit_lever_scale(
    objects: dict[str, list[str]],
    row: tuple[float, float, float],
    row_span_m: float,
) -> float:
    """Scale R1 levers so MN-a→MN-c spacing matches Orbitron switch row span."""
    sa = _object_centroid(objects["cont-bus-pwr-mn-a"])
    sc = _object_centroid(objects["cont-bus-pwr-mn-c"])
    delta = (sc[0] - sa[0], sc[1] - sa[1], sc[2] - sa[2])
    src_span = abs(_dot(delta, row))
    if src_span < 1e-6:
        return 1.6
    scale = row_span_m / src_span
    return max(LEVER_SCALE_MIN, min(LEVER_SCALE_MAX, scale))


def _shuttle_to_panel_rotation(
    objects: dict[str, list[str]],
    row: tuple[float, float, float],
    up: tuple[float, float, float],
    normal: tuple[float, float, float],
) -> list[list[float]]:
    """Map shuttle lever basis → Operator_Panel mesh basis (no reflection)."""
    d_row, d_up, d_normal = row, up, normal
    # R1 levers protrude opposite panel +normal; 180° about row faces the operator.
    d_up = tuple(-c for c in d_up)
    d_normal = tuple(-c for c in d_normal)
    s_row, s_up, s_normal = _shuttle_r1_basis(objects)
    dst = _basis_matrix(d_row, d_up, d_normal)
    src = _basis_matrix(s_row, s_up, s_normal)
    return _mat_mul(dst, _transpose(src))


def _snap_object_to_target(
    obj_lines: list[str], target: tuple[float, float, float]
) -> list[str]:
    c = _object_centroid(obj_lines)
    return _translate_object_local(
        obj_lines,
        (target[0] - c[0], target[1] - c[1], target[2] - c[2]),
    )


def _transform_axis(rot: list[list[float]], axis: tuple[float, float, float]) -> tuple[float, float, float]:
    ax = _mat_vec(rot, axis)
    al = math.sqrt(sum(c * c for c in ax)) or 1.0
    return (ax[0] / al, ax[1] / al, ax[2] / al)


def _transform_point(
    p: tuple[float, float, float],
    rot: list[list[float]],
    trans: tuple[float, float, float],
    *,
    scale: float = 1.0,
    scale_center: tuple[float, float, float] | None = None,
) -> tuple[float, float, float]:
    if scale_center and scale != 1.0:
        p = (
            scale_center[0] + scale * (p[0] - scale_center[0]),
            scale_center[1] + scale * (p[1] - scale_center[1]),
            scale_center[2] + scale * (p[2] - scale_center[2]),
        )
    rx, ry, rz = _mat_vec(rot, p)
    return (rx + trans[0], ry + trans[1], rz + trans[2])


def _crop_object_bbox(
    obj_lines: list[str],
    bbox: dict[str, tuple[float, float]],
) -> list[str] | None:
    """Keep faces touching bbox verts, plus face closure (all verts of those faces)."""
    nvert, nv_i = _object_numvert(obj_lines)
    if nvert <= 0:
        return None

    seed: set[int] = set()
    for vi in range(nvert):
        p = obj_lines[nv_i + vi].split()
        if len(p) != 3:
            continue
        x, y, z = map(float, p)
        if (
            bbox["x"][0] <= x <= bbox["x"][1]
            and bbox["y"][0] <= y <= bbox["y"][1]
            and bbox["z"][0] <= z <= bbox["z"][1]
        ):
            seed.add(vi)

    if not seed:
        return None

    tail_start = nv_i + nvert
    surf_lines = list(obj_lines[tail_start:])
    surf_i = 0
    while surf_i < len(surf_lines) and not surf_lines[surf_i].strip().startswith("numsurf"):
        surf_i += 1
    if surf_i >= len(surf_lines):
        return None
    numsurf = int(surf_lines[surf_i].split()[1])
    j = surf_i + 1
    keep_faces: list[list[str]] = []
    for _ in range(numsurf):
        while j < len(surf_lines) and not surf_lines[j].strip().startswith("SURF"):
            j += 1
        if j >= len(surf_lines):
            break
        block: list[str] = []
        while j < len(surf_lines):
            st = surf_lines[j].strip()
            if st == "kids":
                break
            if st.startswith("SURF"):
                if block:
                    break
            block.append(surf_lines[j])
            j += 1
        if not block:
            continue
        refs_ln = next((b for b in block if b.strip().startswith("refs")), None)
        if not refs_ln:
            continue
        nrefs = int(refs_ln.split()[1])
        ref_i = block.index(refs_ln) + 1
        idxs = []
        for k in range(nrefs):
            parts = block[ref_i + k].split()
            if parts:
                idxs.append(int(parts[0]))
        if any(i in seed for i in idxs):
            keep_faces.append(block)
            seed.update(idxs)

    old_to_new: dict[int, int] = {}
    new_verts: list[str] = []
    for vi in sorted(seed):
        p = obj_lines[nv_i + vi].split()
        if len(p) != 3:
            continue
        old_to_new[vi] = len(new_verts)
        new_verts.append(p[0] + " " + p[1] + " " + p[2] if len(p) == 3 else " ".join(p))

    if len(new_verts) < 12 or not keep_faces:
        return None

    head = list(obj_lines[:nv_i])
    head[-1] = f"numvert {len(new_verts)}"
    head.extend(new_verts)

    new_blocks: list[str] = []
    for block in keep_faces:
        refs_ln = next((b for b in block if b.strip().startswith("refs")), None)
        if not refs_ln:
            continue
        nrefs = int(refs_ln.split()[1])
        ref_i = block.index(refs_ln) + 1
        new_refs = []
        for k in range(nrefs):
            parts = block[ref_i + k].split()
            if len(parts) < 1:
                continue
            old = int(parts[0])
            if old not in old_to_new:
                continue
            parts[0] = str(old_to_new[old])
            new_refs.append(" ".join(parts))
        if len(new_refs) < 3:
            continue
        header = []
        for b in block:
            if b.strip().startswith("refs"):
                break
            header.append(b)
        new_blocks.extend(header + [f"refs {len(new_refs)}"] + new_refs)

    nsurf = sum(1 for b in new_blocks if b.strip().startswith("SURF"))
    if nsurf == 0:
        return None
    return head + [f"numsurf {nsurf}"] + new_blocks + ["kids 0"]


def _transform_object(
    obj_lines: list[str],
    rot: list[list[float]],
    trans: tuple[float, float, float],
    *,
    scale: float = 1.0,
    scale_center: tuple[float, float, float] | None = None,
) -> list[str]:
    out = list(obj_lines)
    nvert, nv_i = _object_numvert(out)
    if nvert <= 0:
        return out
    sc = scale_center or _object_centroid(out)
    for vi in range(nvert):
        p = out[nv_i + vi].split()
        if len(p) != 3:
            continue
        tp = _transform_point(
            tuple(map(float, p)), rot, trans, scale=scale, scale_center=sc
        )
        out[nv_i + vi] = f"{tp[0]:.5f} {tp[1]:.5f} {tp[2]:.5f}"
    return out


def _translate_object_local(
    obj_lines: list[str], delta: tuple[float, float, float]
) -> list[str]:
    out = list(obj_lines)
    nvert, nv_i = _object_numvert(out)
    for vi in range(nvert):
        p = out[nv_i + vi].split()
        if len(p) != 3:
            continue
        x, y, z = map(float, p)
        out[nv_i + vi] = (
            f"{x + delta[0]:.5f} {y + delta[1]:.5f} {z + delta[2]:.5f}"
        )
    return out


def _force_material_index(obj_lines: list[str], mat_index: int = 0) -> list[str]:
    """Shuttle sources use mat slots that render black in Orbitron; use FwdCockpit (0)."""
    out = list(obj_lines)
    for i, ln in enumerate(out):
        st = ln.strip()
        if st.startswith("mat "):
            out[i] = f"mat {mat_index}"
    return out


def _rename_object(obj_lines: list[str], new_name: str) -> list[str]:
    out = list(obj_lines)
    for i, ln in enumerate(out):
        if ln.strip().startswith('name "'):
            out[i] = f'name "{new_name}"'
            break
    return out


def _guard_bbox_for_lever(center: tuple[float, float, float]) -> dict[str, tuple[float, float]]:
    hx, hy, hz = GUARD_BBOX_HALF
    return {
        "x": (center[0] - hx, center[0] + hx),
        "y": (center[1] - hy, center[1] + hy),
        "z": (center[2] - hz, center[2] + hz),
    }


def _cockpit_materials(ac_text: str) -> list[str]:
    """All MATERIAL lines from cockpit.ac (must precede OBJECT world in exported AC3D)."""
    return [ln for ln in ac_text.splitlines() if ln.startswith("MATERIAL ")]


def build_panel_ac(
    cockpit_ac: Path,
    out_ac: Path,
    orbitron_ac: Path | None = None,
) -> dict[str, tuple[float, float, float]]:
    ac_text = cockpit_ac.read_text(encoding="utf-8", errors="replace")
    materials = _cockpit_materials(ac_text)
    if not materials:
        raise SystemExit(f"no MATERIAL definitions found in {cockpit_ac}")

    objects = _parse_objects(ac_text)
    missing = [s for s in SOURCE_SWITCHES if s not in objects]
    if missing:
        raise SystemExit(f"missing objects in {cockpit_ac}: {missing}")
    if GUARD_SOURCE not in objects:
        raise SystemExit(f"missing {GUARD_SOURCE}")
    if SHUTTLE_DIM_KNOB not in objects:
        raise SystemExit(f"missing {SHUTTLE_DIM_KNOB} in {cockpit_ac}")

    targets, panel_frame = _resolve_targets_and_frame(orbitron_ac)
    row_unit, up_unit, normal_unit, _panel_c = panel_frame

    row_offsets = [PANEL_SWITCH_ROW[k][0] for k in PANEL_SWITCH_ROW]
    row_span_m = max(row_offsets) - min(row_offsets)
    lever_scale = _fit_lever_scale(objects, row_unit, row_span_m)
    dim_knob_scale = lever_scale * DIM_KNOB_SCALE_MULT

    src_pts = [_object_centroid(objects[s]) for s in SOURCE_SWITCHES]
    dst_pts = [targets[SOURCE_SWITCHES[s]] for s in SOURCE_SWITCHES]
    src_c = tuple(sum(p[i] for p in src_pts) / 3 for i in range(3))
    dst_c = tuple(sum(p[i] for p in dst_pts) / 3 for i in range(3))
    rot = _shuttle_to_panel_rotation(objects, row_unit, up_unit, normal_unit)
    trans = (
        dst_c[0] - _mat_vec(rot, src_c)[0],
        dst_c[1] - _mat_vec(rot, src_c)[1],
        dst_c[2] - _mat_vec(rot, src_c)[2],
    )

    out_objects: list[str] = []
    centers: dict[str, tuple[float, float, float]] = {}
    knob_axis = _transform_axis(rot, (1.0, 0.3, 0.0))
    lever_knob_axis = _transform_axis(rot, SHUTTLE_DIM_KNOB_AXIS)

    ref_c = _object_centroid(objects[GUARD_TEMPLATE_LEVER])
    guard_template = _crop_object_bbox(
        objects[GUARD_SOURCE], _guard_bbox_for_lever(ref_c)
    )

    for src, dst in SOURCE_SWITCHES.items():
        lever_c = _object_centroid(objects[src])
        if guard_template:
            delta = (
                lever_c[0] - ref_c[0],
                lever_c[1] - ref_c[1],
                lever_c[2] - ref_c[2],
            )
            guard_src = (
                guard_template
                if src == GUARD_TEMPLATE_LEVER
                else _translate_object_local(guard_template, delta)
            )
            guard_name = dst.replace("Panel_Switch_", "Panel_Guard_")
            guard = _rename_object(
                _snap_object_to_target(
                    _transform_object(
                        guard_src,
                        rot,
                        trans,
                        scale=lever_scale,
                        scale_center=lever_c,
                    ),
                    targets[dst],
                ),
                guard_name,
            )
            out_objects.extend(_force_material_index(guard))

        lever = _rename_object(
            _force_material_index(
                _snap_object_to_target(
                    _transform_object(
                        objects[src],
                        rot,
                        trans,
                        scale=lever_scale,
                        scale_center=lever_c,
                    ),
                    targets[dst],
                )
            ),
            dst,
        )
        out_objects.extend(lever)
        centers[dst] = _object_centroid(lever)

    # Analog row: Shuttle display dimmer knobs (DIM/BRT style, no guards).
    dim_src = objects[SHUTTLE_DIM_KNOB]
    dim_c = _object_centroid(dim_src)
    for dst in RATE_KNOB_NAMES:
        if dst not in targets:
            continue
        tgt = targets[dst]
        knob_trans = (
            tgt[0] - _mat_vec(rot, dim_c)[0],
            tgt[1] - _mat_vec(rot, dim_c)[1],
            tgt[2] - _mat_vec(rot, dim_c)[2],
        )
        knob = _rename_object(
            _force_material_index(
                _snap_object_to_target(
                    _transform_object(
                        dim_src,
                        rot,
                        knob_trans,
                        scale=dim_knob_scale,
                        scale_center=dim_c,
                    ),
                    tgt,
                )
            ),
            dst,
        )
        out_objects.extend(knob)
        # Pivot at placed knob centroid (matches panel-local XML frame).
        centers[dst] = _object_centroid(knob)

    centers["lever_scale"] = (lever_scale, lever_scale, lever_scale)
    centers["dim_knob_scale"] = (dim_knob_scale, dim_knob_scale, dim_knob_scale)
    centers["lever_knob_axis"] = lever_knob_axis

    n_obj = sum(1 for ln in out_objects if ln.strip() == "OBJECT poly")
    body = (
        ["AC3Db"]
        + materials
        + ["OBJECT world", 'name "orbitron_panel_shuttle"', f"kids {n_obj}"]
        + out_objects
    )
    out_ac.parent.mkdir(parents=True, exist_ok=True)
    out_ac.write_text("\n".join(body) + "\n", encoding="utf-8")
    centers["knob_axis"] = knob_axis
    centers["panel_row_axis"] = row_unit
    return centers


def write_panel_animation_json(
    centers: dict[str, tuple[float, float, float]],
    out_path: Path,
) -> None:
    """Emit pivot + axis for Orbitron.xml (compile merges into knob_animations)."""
    switch_axis = centers.get("knob_axis")
    lever_axis = centers.get("lever_knob_axis") or centers.get("panel_row_axis") or switch_axis
    if switch_axis is None:
        return
    objects: dict[str, dict[str, list[float]]] = {}
    for name, c in centers.items():
        if name in (
            "knob_axis",
            "lever_knob_axis",
            "panel_row_axis",
            "lever_scale",
            "dim_knob_scale",
        ) or not name.startswith("Panel_"):
            continue
        is_lever = name.startswith("Panel_Lever_")
        ax = lever_axis if is_lever else switch_axis
        entry: dict[str, object] = {
            "axis": [round(ax[0], 4), round(ax[1], 4), round(ax[2], 4)],
            "center_m": [round(c[0], 4), round(c[1], 4), round(c[2], 4)],
        }
        if is_lever:
            entry["kind"] = "lever"
        objects[name] = entry
    payload: dict[str, object] = {
        "comment": "Auto from build_orbitron_shuttle_panel_ac.py — pivots from Shuttle cockpit.xml",
        "knob_factor": -35,
        "lever_factor": -36,
        "lever_offset_deg": 0,
        "objects": objects,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cockpit-ac", type=Path, default=Path("Models/cockpit.ac"))
    ap.add_argument(
        "--cockpit-texture",
        type=Path,
        default=Path("Models/fwd-cockpit-text-map-x.png"),
    )
    ap.add_argument(
        "--out-ac",
        type=Path,
        default=Path("Aircraft/Orbitron-TestStand/Models/orbitron_panel_shuttle.ac"),
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("Aircraft/Orbitron-TestStand/Models"),
    )
    ap.add_argument(
        "--orbitron-ac",
        type=Path,
        default=Path("Aircraft/Orbitron-TestStand/Models/orbitron.ac"),
        help="Read Panel_Label_* centroids for switch placement (rebuild glTF first).",
    )
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[1]
    cockpit_ac = (repo / args.cockpit_ac).resolve()
    out_ac = (repo / args.out_ac).resolve()
    orbitron_ac = (repo / args.orbitron_ac).resolve()
    if not orbitron_ac.is_file():
        orbitron_ac = None
        print("Note: orbitron.ac not found — using PANEL_FRAME_FALLBACK for switch mounts")
    centers = build_panel_ac(cockpit_ac, out_ac, orbitron_ac)
    anim_json = (repo / args.out_dir / "orbitron_panel_anims.json").resolve()
    write_panel_animation_json(centers, anim_json)
    print(f"Wrote {anim_json}")
    tex_dst = (repo / args.out_dir / args.cockpit_texture.name).resolve()
    tex_src = (repo / args.cockpit_texture).resolve()
    if tex_src.is_file():
        shutil.copy2(tex_src, tex_dst)
    print(f"Wrote {out_ac}")
    axis = centers.pop("knob_axis", None)
    lever_axis = centers.pop("lever_knob_axis", None)
    scale = centers.pop("lever_scale", None)
    dim_scale = centers.pop("dim_knob_scale", None)
    if scale:
        print(f"  lever_scale={scale[0]:.3f}")
    if dim_scale:
        print(f"  dim_knob_scale={dim_scale[0]:.3f}")
    if lever_axis:
        print(
            f"  lever_axis=({lever_axis[0]:.4f}, {lever_axis[1]:.4f}, {lever_axis[2]:.4f})"
        )
    if axis:
        print(f"  knob_axis=({axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f})")
    for k, v in sorted(centers.items()):
        print(f"  {k} center=({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
