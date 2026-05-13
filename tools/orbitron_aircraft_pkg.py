"""Shared: FlightGear aircraft package directory from orbitron_aircraft_flightgear.yaml."""
from __future__ import annotations

from pathlib import Path

import yaml


def aircraft_package_dir(repo_root: Path) -> str:
    """Return ``aircraft.package_dir`` (e.g. ``Orbitron-TestStand``)."""
    spec = (
        repo_root
        / "ssto"
        / "orbitron"
        / "assembly_specs"
        / "orbitron_aircraft_flightgear.yaml"
    )
    data = yaml.safe_load(spec.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return "Orbitron-TestStand"
    ac = data.get("aircraft")
    if not isinstance(ac, dict):
        return "Orbitron-TestStand"
    pkg = ac.get("package_dir")
    if isinstance(pkg, str) and pkg.strip():
        return pkg.strip()
    return "Orbitron-TestStand"
