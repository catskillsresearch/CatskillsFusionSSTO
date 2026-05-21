"""Load ``orbitron_physics_surrogate.yaml`` engineering scales for the 0D plant."""
from __future__ import annotations

from pathlib import Path

import yaml

from ssto.orbitron.simulator.types import PlantScales


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def physics_spec_path() -> Path:
    return repo_root() / "ssto" / "orbitron" / "assembly_specs" / "orbitron_physics_surrogate.yaml"


def load_plant_scales(path: Path | None = None) -> PlantScales:
    path = path or physics_spec_path()
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    eng = doc.get("surrogate_engineering") or {}
    return PlantScales(
        target_gross_power_mw=float(eng.get("design_gross_fusion_power_mw", 3.5)),
        jet_propulsive_efficiency=float(eng.get("jet_propulsive_efficiency", 0.55)),
        heat_kw_at_full=float(eng.get("heat_kw_scale", 400.0)),
        beam_screen_kw_per_ma=float(eng.get("beam_screen_kw_per_ma", 0.6)),
        thrust_lbf_at_full=float(eng.get("thrust_lbf_scale", 4040.0)),
        mass_flow_kgps_at_full=float(eng.get("mass_flow_kgps_scale", 84.0)),
        density_log10_at_full=float(eng.get("density_log10_at_full", 11.0)),
    )
