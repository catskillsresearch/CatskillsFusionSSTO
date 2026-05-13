"""Load assembly YAML (with hierarchical includes) and build a nested CadQuery Assembly."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cadquery as cq
import yaml

from yaml_assembly.templates_registry import build_template
from yaml_assembly.transform_ops import apply_transform_chain


def _color(rgb: list[Any] | tuple[Any, ...]) -> cq.Color:
    return cq.Color(float(rgb[0]), float(rgb[1]), float(rgb[2]))


def build_assembly_from_yaml(spec_path: Path, visiting: set[str] | None = None) -> cq.Assembly:
    """Recursively load ``spec_path`` and return a nested ``cq.Assembly`` (names for glTF / Blender outliner)."""
    resolved = spec_path.resolve()
    key = str(resolved)
    if visiting is None:
        visiting = set()
    if key in visiting:
        raise RuntimeError(f"YAML include cycle detected at {resolved}")
    visiting.add(key)
    try:
        data: dict[str, Any] = yaml.safe_load(resolved.read_text(encoding="utf-8"))
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


def compile_to_gltf(spec_path: Path, out_gltf: Path) -> None:
    """Build assembly from YAML and write glTF (same path CadQuery uses for downstream .ac tooling)."""
    out_gltf.parent.mkdir(parents=True, exist_ok=True)
    build_assembly_from_yaml(spec_path).save(str(out_gltf))
