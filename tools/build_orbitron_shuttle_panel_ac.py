#!/usr/bin/env python3
"""Build orbitron_panel_shuttle.ac — three shuttle guarded toggles on the Orbitron panel plane."""
from __future__ import annotations

import argparse
import math
import re
import shutil
from pathlib import Path

# Mount row on orbitron.ac — below Screen (y≈1.6), aligned with Panel_Label_* meshes.
# Labels sit ~0.05 m above each switch on the slanted panel face.
TARGETS = {
    "Panel_Switch_APU": (-1.615, -0.06, 5.12),
    "Panel_Switch_Starter": (-1.480, -0.095, 5.12),
    "Panel_Switch_Bleed": (-1.338, -0.130, 5.12),
    "Big_Red_Button": (-1.200, -0.110, 5.15),
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

LEVER_SCALE = 1.85
# One U-rail per MN-bus toggle (~280 verts); full R1-guards is the whole panel rack.
GUARD_BBOX_HALF = (0.028, 0.042, 0.022)
# Compact backplate behind the four controls (shuttle FwdCockpit grey, no schematic).
BACKPLATE_MARGIN_X = 0.06
BACKPLATE_MARGIN_Y = 0.05
BACKPLATE_BEHIND_M = 0.012


def _kabsch_rotation(src, dst) -> list[list[float]]:
    import numpy as np

    h = sum(np.outer(np.array(src[i]), np.array(dst[i])) for i in range(3))
    u, _, vt = np.linalg.svd(h)
    r = vt.T @ u.T
    if np.linalg.det(r) < 0:
        vt = vt.copy()
        vt[2, :] *= -1
        r = vt.T @ u.T
    return r.tolist()


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


def _panel_frame_orbitron() -> tuple[tuple[float, float, float], list[list[float]]]:
    """Orbitron panel: row +X, face normal toward operator (+Z, slight +Y)."""
    apu = TARGETS["Panel_Switch_APU"]
    bleed = TARGETS["Panel_Switch_Bleed"]
    row = (bleed[0] - apu[0], bleed[1] - apu[1], bleed[2] - apu[2])
    rl = math.sqrt(sum(c * c for c in row)) or 1.0
    row = tuple(c / rl for c in row)
    # Face normal: perpendicular to row, leaning toward +Z (operator side).
    normal = (0.0, 0.42, 0.91)
    nl = math.sqrt(sum(c * c for c in normal))
    normal = tuple(c / nl for c in normal)
    # Re-orthogonalize up = normal × row
    up = (
        normal[1] * row[2] - normal[2] * row[1],
        normal[2] * row[0] - normal[0] * row[2],
        normal[0] * row[1] - normal[1] * row[0],
    )
    origin = TARGETS["Panel_Switch_Starter"]
    rot = [
        [row[0], up[0], normal[0]],
        [row[1], up[1], normal[1]],
        [row[2], up[2], normal[2]],
    ]
    return origin, rot


def _shuttle_to_panel_rotation(objects: dict[str, list[str]]) -> list[list[float]]:
    src_pts = [_object_centroid(objects[s]) for s in SOURCE_SWITCHES]
    dst_pts = [TARGETS[SOURCE_SWITCHES[s]] for s in SOURCE_SWITCHES]
    src_c = tuple(sum(p[i] for p in src_pts) / 3 for i in range(3))
    dst_c = tuple(sum(p[i] for p in dst_pts) / 3 for i in range(3))
    src_rel = [(p[0] - src_c[0], p[1] - src_c[1], p[2] - src_c[2]) for p in src_pts]
    dst_rel = [(p[0] - dst_c[0], p[1] - dst_c[1], p[2] - dst_c[2]) for p in dst_pts]
    return _kabsch_rotation(src_rel, dst_rel)


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


def _make_backplate(
    center: tuple[float, float, float],
    row: tuple[float, float, float],
    up: tuple[float, float, float],
    half_w: float,
    half_h: float,
) -> list[str]:
    def corner(su: float, sv: float) -> tuple[float, float, float]:
        return (
            center[0] + su * half_w * row[0] + sv * half_h * up[0],
            center[1] + su * half_w * row[1] + sv * half_h * up[1],
            center[2] + su * half_w * row[2] + sv * half_h * up[2],
        )

    verts = [corner(-1, -1), corner(1, -1), corner(1, 1), corner(-1, 1)]
    vert_lines = [f"{v[0]:.5f} {v[1]:.5f} {v[2]:.5f}" for v in verts]
    return [
        "OBJECT poly",
        'name "Panel_Backplate"',
        "data 0",
        "FwdCockpit",
        "crease 0.0",
        'texture "fwd-cockpit-text-map-x.png"',
        "texrep 1 1",
        "numvert 4",
        *vert_lines,
        "numsurf 1",
        "SURF 0X20",
        "mat 0",
        "refs 4",
        "0 0 0",
        "1 0 0",
        "2 0 0",
        "3 0 0",
        "kids 0",
    ]


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


def build_panel_ac(cockpit_ac: Path, out_ac: Path) -> dict[str, tuple[float, float, float]]:
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

    src_pts = [_object_centroid(objects[s]) for s in SOURCE_SWITCHES]
    dst_pts = [TARGETS[SOURCE_SWITCHES[s]] for s in SOURCE_SWITCHES]
    src_c = tuple(sum(p[i] for p in src_pts) / 3 for i in range(3))
    dst_c = tuple(sum(p[i] for p in dst_pts) / 3 for i in range(3))
    rot = _shuttle_to_panel_rotation(objects)
    trans = (
        dst_c[0] - _mat_vec(rot, src_c)[0],
        dst_c[1] - _mat_vec(rot, src_c)[1],
        dst_c[2] - _mat_vec(rot, src_c)[2],
    )

    out_objects: list[str] = []
    centers: dict[str, tuple[float, float, float]] = {}
    knob_axis = _transform_axis(rot, (1.0, 0.3, 0.0))

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
                        scale=LEVER_SCALE,
                        scale_center=lever_c,
                    ),
                    TARGETS[dst],
                ),
                guard_name,
            )
            out_objects.extend(guard)

        lever = _rename_object(
            _snap_object_to_target(
                _transform_object(
                    objects[src],
                    rot,
                    trans,
                    scale=LEVER_SCALE,
                    scale_center=lever_c,
                ),
                TARGETS[dst],
            ),
            dst,
        )
        out_objects.extend(lever)
        centers[dst] = _object_centroid(lever)

    # Ignite: shuttle abort guarded slider → Big_Red_Button
    if ABORT_LEVER in objects:
        abort_c = _object_centroid(objects[ABORT_LEVER])
        tgt = TARGETS["Big_Red_Button"]
        abort_trans = (
            tgt[0] - _mat_vec(rot, abort_c)[0],
            tgt[1] - _mat_vec(rot, abort_c)[1],
            tgt[2] - _mat_vec(rot, abort_c)[2],
        )
        brb = _snap_object_to_target(
            _transform_object(
                objects[ABORT_LEVER],
                rot,
                abort_trans,
                scale=LEVER_SCALE * 1.1,
                scale_center=abort_c,
            ),
            tgt,
        )
        out_objects.extend(_rename_object(brb, "Big_Red_Button"))
        centers["Big_Red_Button"] = _object_centroid(brb)
        if ABORT_LIGHT in objects:
            light_c = _object_centroid(objects[ABORT_LIGHT])
            light_trans = (
                tgt[0] - _mat_vec(rot, light_c)[0],
                tgt[1] - _mat_vec(rot, light_c)[1],
                tgt[2] - _mat_vec(rot, light_c)[2],
            )
            light = _snap_object_to_target(
                _transform_object(
                    objects[ABORT_LIGHT],
                    rot,
                    light_trans,
                    scale=LEVER_SCALE * 1.1,
                    scale_center=light_c,
                ),
                tgt,
            )
            out_objects.extend(_rename_object(light, "Big_Red_Button_Light"))

    apu_t = centers["Panel_Switch_APU"]
    bleed_t = centers["Panel_Switch_Bleed"]
    ignite_t = centers["Big_Red_Button"]
    row_vec = (bleed_t[0] - apu_t[0], bleed_t[1] - apu_t[1], bleed_t[2] - apu_t[2])
    rl = math.sqrt(sum(c * c for c in row_vec)) or 1.0
    row_unit = tuple(c / rl for c in row_vec)
    _, frame_rot = _panel_frame_orbitron()
    up_unit = (frame_rot[0][1], frame_rot[1][1], frame_rot[2][1])
    normal_unit = (frame_rot[0][2], frame_rot[1][2], frame_rot[2][2])
    half_w = (
        max(
            abs(ignite_t[0] - apu_t[0]),
            abs(ignite_t[1] - apu_t[1]),
            abs(ignite_t[2] - apu_t[2]),
        )
        / 2
        + BACKPLATE_MARGIN_X
    )
    half_h = 0.055 + BACKPLATE_MARGIN_Y
    plate_c = (
        (apu_t[0] + ignite_t[0]) / 2,
        (apu_t[1] + ignite_t[1]) / 2,
        (apu_t[2] + ignite_t[2]) / 2,
    )
    plate_c = (
        plate_c[0] - BACKPLATE_BEHIND_M * normal_unit[0],
        plate_c[1] - BACKPLATE_BEHIND_M * normal_unit[1],
        plate_c[2] - BACKPLATE_BEHIND_M * normal_unit[2],
    )
    out_objects = _make_backplate(plate_c, row_unit, up_unit, half_w, half_h) + out_objects

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
    return centers


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
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[1]
    cockpit_ac = (repo / args.cockpit_ac).resolve()
    out_ac = (repo / args.out_ac).resolve()
    centers = build_panel_ac(cockpit_ac, out_ac)
    tex_dst = (repo / args.out_dir / args.cockpit_texture.name).resolve()
    tex_src = (repo / args.cockpit_texture).resolve()
    if tex_src.is_file():
        shutil.copy2(tex_src, tex_dst)
    print(f"Wrote {out_ac}")
    axis = centers.pop("knob_axis", None)
    if axis:
        print(f"  knob_axis=({axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f})")
    for k, v in sorted(centers.items()):
        print(f"  {k} center=({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
