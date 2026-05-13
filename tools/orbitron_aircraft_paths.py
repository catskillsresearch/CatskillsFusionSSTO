#!/usr/bin/env python3
"""Print aircraft package paths from orbitron_aircraft_flightgear.yaml (for Make / shell)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def _default_spec(repo_root: Path) -> Path:
    return (
        repo_root
        / "ssto"
        / "orbitron"
        / "assembly_specs"
        / "orbitron_aircraft_flightgear.yaml"
    )


def _load_spec(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("spec root must be a mapping")
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "query",
        choices=("package_dir", "set_xml_basename"),
        help="package_dir: aircraft folder name; set_xml_basename: <name>-set.xml",
    )
    ap.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of tools/)",
    )
    ap.add_argument(
        "--aircraft-spec",
        type=Path,
        default=None,
        help="orbitron_aircraft_flightgear.yaml path",
    )
    args = ap.parse_args()
    repo = (args.repo_root or Path(__file__).resolve().parents[1]).resolve()
    spec = (args.aircraft_spec or _default_spec(repo)).resolve()
    if not spec.is_file():
        print(f"error: aircraft spec not found: {spec}", file=sys.stderr)
        return 1
    data = _load_spec(spec)
    ac = data.get("aircraft")
    if not isinstance(ac, dict):
        print("error: missing aircraft: mapping in spec", file=sys.stderr)
        return 1
    pkg = ac.get("package_dir")
    if not isinstance(pkg, str) or not pkg.strip():
        print("error: missing aircraft.package_dir (non-empty string)", file=sys.stderr)
        return 1
    pkg = pkg.strip()
    if args.query == "package_dir":
        print(pkg)
    else:
        print(f"{pkg}-set.xml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
