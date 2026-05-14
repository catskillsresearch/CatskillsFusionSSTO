"""Load unified assembly YAML (schema v2) and build a nested ``cq.Assembly`` for glTF export."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import cadquery as cq
import yaml

from yaml_assembly.templates_registry import build_template
from yaml_assembly.transform_ops import apply_transform_chain


def _color(rgb: list[Any] | tuple[Any, ...]) -> cq.Color:
    return cq.Color(float(rgb[0]), float(rgb[1]), float(rgb[2]))


def collect_group_closure(groups: dict[str, Any], root_key: str) -> list[str]:
    """Preorder list of ``root_key`` and all nested ``members`` (unique)."""
    if root_key not in groups:
        raise KeyError(f"logical group {root_key!r} not found (known: {sorted(groups)!r})")
    order: list[str] = []
    seen: set[str] = set()

    def visit(k: str) -> None:
        if k in seen:
            return
        if k not in groups:
            raise KeyError(f"group {k!r} referenced in members but not defined in logical.groups")
        seen.add(k)
        order.append(k)
        spec = groups[k]
        for mk in spec.get("members", []) or []:
            visit(str(mk))

    visit(root_key)
    return order


def prune_unified_spec_for_subassembly(data: dict[str, Any], sub_root: str) -> dict[str, Any]:
    """Return a copy of a schema v2 unified spec whose logical tree is only ``sub_root`` and descendants."""
    logical = data["logical"]
    groups = logical["groups"]
    closure_keys = collect_group_closure(groups, sub_root)
    pruned_groups = {k: copy.deepcopy(groups[k]) for k in closure_keys}
    logical_pruned = {
        **{kk: copy.deepcopy(vv) for kk, vv in logical.items() if kk != "groups"},
        "root": sub_root,
        "scene_root_name": sub_root,
        "groups": pruned_groups,
    }
    mesh_names = collect_mesh_names_from_groups(pruned_groups, sub_root)
    instances_src = data["instances"]
    missing = sorted(mesh_names - set(instances_src.keys()))
    if missing:
        raise ValueError(
            f"subassembly {sub_root!r} references instances missing from spec: {missing}"
        )
    pruned_instances = {k: copy.deepcopy(instances_src[k]) for k in mesh_names}
    out = copy.deepcopy({kk: vv for kk, vv in data.items() if kk not in ("logical", "instances")})
    out["logical"] = logical_pruned
    out["instances"] = pruned_instances
    return out


def mesh_parts_list(spec: dict[str, Any]) -> list[str]:
    mp = spec.get("mesh_parts")
    if mp is not None:
        return [str(x) for x in mp]
    return [str(x) for x in spec.get("parts", [])]


def collect_mesh_names_from_groups(groups: dict[str, Any], root_key: str) -> set[str]:
    found: set[str] = set()

    def visit(key: str) -> None:
        spec = groups[key]
        if spec.get("logical_only"):
            return
        for mk in spec.get("members", []):
            visit(str(mk))
        for p in mesh_parts_list(spec):
            found.add(p)

    visit(root_key)
    return found


def validate_gltf_mesh_names_match_logical(out_gltf: Path, logical_doc: dict[str, Any]) -> None:
    """Every mesh in glTF must appear in the logical tree under ``root``; no extras."""
    root = str(logical_doc["root"])
    groups: dict[str, Any] = logical_doc["groups"]
    gltf = json.loads(out_gltf.read_text(encoding="utf-8"))
    mesh_in_gltf = {
        str(n["name"])
        for n in gltf.get("nodes", [])
        if n.get("mesh") is not None and n.get("name")
    }
    json_meshes = collect_mesh_names_from_groups(groups, root)
    missing = sorted(mesh_in_gltf - json_meshes)
    extra = sorted(json_meshes - mesh_in_gltf)
    if missing:
        raise ValueError("logical tree missing mesh names present in glTF: " + ", ".join(missing))
    if extra:
        raise ValueError("logical tree lists mesh names not in glTF: " + ", ".join(extra))


def build_group_node(key: str, groups: dict[str, Any], instances: dict[str, Any]) -> cq.Assembly:
    if key not in groups:
        raise KeyError(f"unknown logical group {key!r}")
    spec = groups[key]
    assy = cq.Assembly(name=key)
    for m in spec.get("members", []):
        mk = str(m)
        assy.add(build_group_node(mk, groups, instances), name=mk)
    for pname in mesh_parts_list(spec):
        if pname not in instances:
            raise KeyError(f"group {key!r} references unknown instance {pname!r}")
        inst = instances[pname]
        tid = str(inst["template"])
        params = inst.get("params") or {}
        if not isinstance(params, dict):
            raise TypeError(f"instances[{pname!r}].params must be a mapping")
        solid = build_template(tid, params)
        solid = apply_transform_chain(solid, inst.get("transform_chain"))
        col = inst.get("color")
        if col is None:
            raise ValueError(f"instances[{pname!r}] missing color [r,g,b]")
        assy.add(solid, name=pname, color=_color(col))
    return assy


def build_assembly_from_unified(data: dict[str, Any]) -> cq.Assembly:
    """Schema v2: ``logical.groups`` + ``instances`` → nested CadQuery assembly (glTF tree)."""
    if int(data.get("schema_version", 1)) < 2:
        raise ValueError("build_assembly_from_unified requires schema_version >= 2")
    logical = data["logical"]
    groups = logical["groups"]
    root = str(logical["root"])
    root_scene = str(logical.get("scene_root_name") or "fusion_arcjet_engine")
    instances = data["instances"]
    if not isinstance(instances, dict):
        raise TypeError("instances must be a mapping of mesh id → instance body")
    top = cq.Assembly(name=root_scene)
    root_spec = groups.get(root)
    if root_spec is None:
        raise ValueError(f"logical.root {root!r} missing from groups")
    for m in root_spec.get("members", []):
        mk = str(m)
        top.add(build_group_node(mk, groups, instances), name=mk)
    for pname in mesh_parts_list(root_spec):
        if pname not in instances:
            raise KeyError(f"logical.root group {root!r} references unknown instance {pname!r}")
        inst = instances[pname]
        tid = str(inst["template"])
        params = inst.get("params") or {}
        if not isinstance(params, dict):
            raise TypeError(f"instances[{pname!r}].params must be a mapping")
        solid = build_template(tid, params)
        solid = apply_transform_chain(solid, inst.get("transform_chain"))
        col = inst.get("color")
        if col is None:
            raise ValueError(f"instances[{pname!r}] missing color [r,g,b]")
        top.add(solid, name=pname, color=_color(col))
    return top


def build_assembly_from_yaml(
    spec_path: Path, visiting: set[str] | None = None, *, subassembly: str | None = None
) -> cq.Assembly:
    """Schema v1 (legacy): recursive ``includes`` + list ``instances`` — kept for ad-hoc tools."""
    resolved = spec_path.resolve()
    key = str(resolved)
    if visiting is None:
        visiting = set()
    if key in visiting:
        raise RuntimeError(f"YAML include cycle detected at {resolved}")
    visiting.add(key)
    try:
        data: dict[str, Any] = yaml.safe_load(resolved.read_text(encoding="utf-8"))
        if int(data.get("schema_version", 1)) >= 2 and "logical" in data and "instances" in data:
            if subassembly:
                data = prune_unified_spec_for_subassembly(data, subassembly)
            return build_assembly_from_unified(data)
        if not isinstance(data, dict):
            raise ValueError(f"Root of YAML must be a mapping: {resolved}")
        meta = data.get("assembly") or {}
        aid = str(meta.get("id", resolved.stem))
        assy = cq.Assembly(name=aid)

        base = resolved.parent
        for inc in data.get("includes", []) or []:
            rel = inc.get("file")
            if not rel:
                raise ValueError(f"Include missing 'file' in {resolved}")
            child_path = (base / str(rel)).resolve()
            if not child_path.is_file():
                raise FileNotFoundError(f"Included assembly not found: {child_path} (from {resolved})")
            node_name = str(inc.get("node_name") or child_path.stem)
            child_assy = build_assembly_from_yaml(child_path, visiting)
            assy.add(child_assy, name=node_name)

        for inst in data.get("instances", []) or []:
            pid = str(inst.get("id") or inst.get("name"))
            if not pid:
                raise ValueError(f"Instance missing id/name in {resolved}")
            tid = str(inst["template"])
            params = inst.get("params") or {}
            if not isinstance(params, dict):
                raise TypeError(f"params for {pid} must be a mapping")
            solid = build_template(tid, params)
            solid = apply_transform_chain(solid, inst.get("transform_chain"))
            col = inst.get("color")
            if col is None:
                raise ValueError(f"Instance {pid} missing color [r,g,b]")
            assy.add(solid, name=pid, color=_color(col))
        return assy
    finally:
        visiting.discard(key)


def compile_to_gltf(spec_path: Path, out_gltf: Path, *, subassembly: str | None = None) -> None:
    """Build assembly from YAML and write glTF (nested tree for schema v2)."""
    out_gltf.parent.mkdir(parents=True, exist_ok=True)
    raw: dict[str, Any] = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if int(raw.get("schema_version", 1)) >= 2 and "logical" in raw and "instances" in raw:
        work = prune_unified_spec_for_subassembly(raw, subassembly) if subassembly else raw
        assy = build_assembly_from_unified(work)
        logical_flat = {"root": work["logical"]["root"], "groups": work["logical"]["groups"]}
    else:
        if subassembly:
            raise ValueError("--subassembly is only supported for schema_version >= 2 unified assemblies")
        assy = build_assembly_from_yaml(spec_path)
        logical_flat = None
    assy.save(str(out_gltf))
    if logical_flat is not None:
        validate_gltf_mesh_names_match_logical(out_gltf, logical_flat)
