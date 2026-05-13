#!/usr/bin/env python3
"""Emit ``build/orbitron/generated/picmi_overrides.json`` from orbitron_physics_surrogate.yaml."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO / "tools") not in sys.path:
    sys.path.insert(0, str(_REPO / "tools"))

import orbitron_physics_spec as ops  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--spec",
        type=Path,
        default=None,
        help="orbitron_physics_surrogate.yaml (default: assembly_specs path)",
    )
    ap.add_argument(
        "--out-json",
        type=Path,
        default=_REPO / "build" / "orbitron" / "generated" / "picmi_overrides.json",
    )
    args = ap.parse_args()
    spec_path = args.spec or ops.default_physics_spec_path(_REPO)
    if not spec_path.is_file():
        print(f"error: spec not found: {spec_path}", file=sys.stderr)
        return 1
    ph = ops.load_physics_spec(spec_path)
    ops.write_picmi_overrides(args.out_json.resolve(), ph)
    print("Wrote", args.out_json.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
