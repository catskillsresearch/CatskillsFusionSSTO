"""Shared: FlightGear aircraft package directory from orbitron_aircraft_flightgear.yaml."""
from __future__ import annotations

import re
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    yaml = None  # type: ignore[misc, assignment]


def _package_dir_scan_yaml(text: str) -> str:
    """Parse ``aircraft.package_dir`` without PyYAML (e.g. Blender's bundled Python)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        rest = line[indent:]
        if not re.match(r"aircraft:\s*$", rest):
            continue
        base = indent
        for j in range(i + 1, len(lines)):
            l2 = lines[j]
            if not l2.strip() or l2.lstrip().startswith("#"):
                continue
            ind2 = len(l2) - len(l2.lstrip())
            if ind2 <= base:
                break
            m = re.match(r"package_dir:\s*(.+?)\s*$", l2.strip())
            if m:
                val = m.group(1).strip().strip("\"'")
                if val:
                    return val
        break
    raise ValueError("could not find aircraft.package_dir (PyYAML absent; scan failed)")


def aircraft_package_dir(repo_root: Path) -> str:
    """Return ``aircraft.package_dir`` from ``orbitron_aircraft_flightgear.yaml``."""
    spec = (
        repo_root
        / "ssto"
        / "orbitron"
        / "assembly_specs"
        / "orbitron_aircraft_flightgear.yaml"
    )
    if not spec.is_file():
        raise FileNotFoundError(f"aircraft spec not found: {spec}")
    raw = spec.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            raise ValueError(f"aircraft spec root must be a mapping: {spec}")
        ac = data.get("aircraft")
        if not isinstance(ac, dict):
            raise ValueError(f"aircraft spec missing 'aircraft' mapping: {spec}")
        pkg = ac.get("package_dir")
        if not isinstance(pkg, str) or not pkg.strip():
            raise ValueError(
                f"aircraft.package_dir must be a non-empty string in {spec}"
            )
        return pkg.strip()
    pkg = _package_dir_scan_yaml(raw)
    if not pkg.strip():
        raise ValueError(f"aircraft.package_dir must be a non-empty string in {spec}")
    return pkg.strip()
