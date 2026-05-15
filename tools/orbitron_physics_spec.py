"""Load ``orbitron_physics_surrogate.yaml`` for build_surrogate_map + laminar overrides."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from warpx_expression_presets import merge_expression_bundle_into_picmi_json


def default_physics_spec_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "ssto"
        / "orbitron"
        / "assembly_specs"
        / "orbitron_physics_surrogate.yaml"
    )


def load_physics_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("physics spec root must be a mapping")
    return data


def picmi_overrides_json(spec: dict[str, Any]) -> dict[str, Any]:
    """Flatten ``picmi:`` for laminar_flow_2d_arcjet --overrides."""
    pic = spec.get("picmi") or {}
    if not isinstance(pic, dict):
        raise TypeError("picmi must be a mapping")
    grid = pic.get("grid") or {}
    dom = pic.get("domain") or {}
    es = pic.get("electrostatic") or {}
    sg = pic.get("species_geometry") or {}
    ts = pic.get("timestep") or {}
    bl = pic.get("beam_list") or {}
    ib = pic.get("inject_beams") or {}
    cpd = pic.get("cathode_pulse_density") or {}
    cpr = pic.get("cathode_pulse_ramp") or {}
    rs = pic.get("ring_density_scale") or {}
    acs = pic.get("arc_seed_scale") or {}
    result = {
        "base_n_e": float(pic["base_n_e"]),
        "base_arc_seed": float(pic["base_arc_seed"]),
        "ring_density_scale": {k: float(v) for k, v in rs.items()},
        "arc_seed_scale": {k: float(v) for k, v in acs.items()},
        "number_of_cells": list(grid["number_of_cells"]),
        "domain_half_extent_m": float(dom["half_extent_m"]),
        "r_anode_m": float(es["r_anode_m"]),
        "r_cathode_m": float(es["r_cathode_m"]),
        "V_cathode_v": float(es["V_cathode_v"]),
        "B_axial_tesla": float(es["B_axial_tesla"]),
        "electron_ring_inner_m": float(sg["electron_ring_inner_m"]),
        "electron_ring_outer_m": float(sg["electron_ring_outer_m"]),
        "arc_channel_inner_m": float(sg["arc_channel_inner_m"]),
        "time_step_size": float(ts["dt_s"]),
        "cfl": float(ts["cfl"]),
        "beam_list": {k: (int(v) if k == "n_particles" else float(v)) for k, v in bl.items()},
    }
    if ib:
        beams_out: dict[str, dict[str, Any]] = {}
        for bk, bv in ib.items():
            row: dict[str, Any] = {}
            for k, v in bv.items():
                if k in ("n_particles", "charge_state"):
                    row[k] = int(v)
                elif k == "particle_type":
                    row[k] = str(v)
                elif isinstance(v, (int, float)):
                    row[k] = float(v)
                else:
                    row[k] = v
            beams_out[str(bk)] = row
        result["inject_beams"] = beams_out
    if cpd:
        result["cathode_pulse_density"] = {k: float(v) for k, v in cpd.items()}
    if cpr:
        result["cathode_pulse_ramp"] = {k: float(v) for k, v in cpr.items()}
    merge_expression_bundle_into_picmi_json(result, spec)
    return result


def beam_roi_tuple(spec: dict[str, Any]) -> tuple[float, float, float, float]:
    red = spec.get("reductions") or {}
    roi = red.get("beam_viewport_roi") or {}
    return (
        float(roi["x_cutoff_m"]),
        float(roi["z_half_width_m"]),
        float(roi["r_inner_m"]),
        float(roi["r_outer_m"]),
    )


def engineering_scalars(spec: dict[str, Any]) -> dict[str, float]:
    eng = spec.get("surrogate_engineering") or {}
    return {k: float(v) for k, v in eng.items()}


def write_picmi_overrides(path: Path, spec: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(picmi_overrides_json(spec), indent=2), encoding="utf-8")
