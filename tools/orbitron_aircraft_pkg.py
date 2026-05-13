"""Shared: FlightGear aircraft package directory from orbitron_aircraft_flightgear.yaml."""
from __future__ import annotations

from pathlib import Path

import yaml


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
    data = yaml.safe_load(spec.read_text(encoding="utf-8"))
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
