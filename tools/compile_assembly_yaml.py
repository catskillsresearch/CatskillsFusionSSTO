#!/usr/bin/env python3
"""Compile hierarchical assembly YAML → glTF (nested CadQuery Assembly).

The Makefile lab mesh path uses this as the **sole layout source** for
``orbitron_lab_flat.gltf`` / ``orbitron_lab.gltf`` (after stem copy and
``gltf_nest_from_assemblies.py``).

Usage (repo root, with Poetry env that has cadquery + pyyaml)::

  poetry run python tools/compile_assembly_yaml.py \\
    --spec ssto/orbitron/assembly_specs/orbitron_lab.yaml \\
    --out /tmp/orbitron_lab_flat.gltf

Sub-assemblies only (same YAML files referenced by the root)::

  poetry run python tools/compile_assembly_yaml.py \\
    --spec ssto/orbitron/assembly_specs/air_breathing_intake.yaml \\
    --out /tmp/intake_only.gltf

Why glTF: matches the existing Orbitron pipeline (Blender ``build_ac3d.py`` → ``.ac`` for FlightGear).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _bootstrap_paths() -> Path:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "ssto" / "orbitron"))
    sys.path.insert(0, str(root / "tools"))
    return root


def main() -> int:
    _bootstrap_paths()
    from yaml_assembly.compiler import compile_to_gltf

    ap = argparse.ArgumentParser(description="Compile assembly YAML tree to glTF")
    ap.add_argument(
        "--spec",
        type=Path,
        required=True,
        help="Root assembly YAML (or any included leaf for a single-file build)",
    )
    ap.add_argument("--out", type=Path, required=True, help="Output .gltf path")
    args = ap.parse_args()
    spec = args.spec.resolve()
    if not spec.is_file():
        print(f"error: spec not found: {spec}", file=sys.stderr)
        return 1
    compile_to_gltf(spec, args.out.resolve())
    print(f"Wrote {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
