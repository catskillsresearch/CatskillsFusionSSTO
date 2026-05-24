"""
Shared helpers for the Orbitron first-principles proof chain (fixed paths under build/orbitron/chain).
"""
from __future__ import annotations

import json
import math
import os
import shlex
import subprocess
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from ssto.orbitron.simulator.injectants import normalize_injectants_cfg
from ssto.orbitron.simulator.types import (
    DeviceGeometry,
    OperatingPoint,
    PadStartupState,
    SimulatorInputs,
    UnobtaniumParams,
)

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

CHAIN_ROOT = _REPO / "build" / "orbitron" / "chain"
GENERATED_ROOT = _REPO / "build" / "orbitron" / "generated"
CONFIG_PATH = CHAIN_ROOT / "chain_config.json"


def repo_root() -> Path:
    return _REPO


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {CONFIG_PATH}. Run Proof Suite step 00 or tools/orbitron_proof_chain/chain_00_spec.sh."
        )
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def compile_picmi_overrides_json() -> Path:
    """Build generated + chain copies of picmi_overrides.json from physics surrogate YAML."""
    (CHAIN_ROOT / "00_spec").mkdir(parents=True, exist_ok=True)
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    out_json = GENERATED_ROOT / "picmi_overrides.json"
    compile_script = repo_root() / "tools" / "compile_physics_surrogate_spec.py"
    py = shlex.split(os.environ.get("CHAIN_PYTHON", "poetry run python"))
    subprocess.run(
        [*py, str(compile_script), "--out-json", str(out_json)],
        check=True,
        cwd=str(repo_root()),
    )
    chain_ov = CHAIN_ROOT / "00_spec" / "picmi_overrides.json"
    chain_ov.write_bytes(out_json.read_bytes())
    return chain_ov


def ensure_picmi_overrides(*, compile_if_missing: bool = True) -> Path:
    """Guarantee ``build/orbitron/chain/00_spec/picmi_overrides.json`` exists."""
    chain_ov = CHAIN_ROOT / "00_spec" / "picmi_overrides.json"
    if chain_ov.is_file():
        return chain_ov
    gen = GENERATED_ROOT / "picmi_overrides.json"
    (CHAIN_ROOT / "00_spec").mkdir(parents=True, exist_ok=True)
    if gen.is_file():
        chain_ov.write_bytes(gen.read_bytes())
        return chain_ov
    if not compile_if_missing:
        raise FileNotFoundError(
            f"Missing {chain_ov}. Run Proof Suite step 00 first."
        )
    return compile_picmi_overrides_json()


# AMReX 26.04 / WarpX default blocking_factor for Cartesian2D (must divide domain size).
AMREX_BLOCKING_FACTOR = 8


def align_pic_grid_cells(n: int, *, blocking_factor: int = AMREX_BLOCKING_FACTOR) -> int:
    """Round up to the next cell count divisible by AMReX ``blocking_factor``."""
    n = max(blocking_factor, int(n))
    rem = n % blocking_factor
    if rem == 0:
        return n
    return n + (blocking_factor - rem)


def pic_grid_cells(cfg: dict[str, Any]) -> int:
    """Square PIC grid resolution from chain_config (Proof Suite step 01)."""
    raw = max(AMREX_BLOCKING_FACTOR, int(cfg.get("pic", {}).get("grid_cells", 512)))
    return align_pic_grid_cells(raw)


def stabilize_pic_settings(cfg: dict[str, Any]) -> list[str]:
    """
    Clamp PIC grid/steps for local AMReX 26.04 / pywarpx stability.

    Default max grid 128² (stable through 400+ steps). Override with env
    ``WARPX_MAX_PIC_GRID`` (e.g. 256 — steps are capped automatically).
    """
    notes: list[str] = []
    pic = cfg.setdefault("pic", {})
    max_cells = int(os.environ.get("WARPX_MAX_PIC_GRID", "128"))
    requested = align_pic_grid_cells(int(pic.get("grid_cells", max_cells)))
    if requested > max_cells:
        capped = align_pic_grid_cells(max_cells)
        notes.append(
            f"PIC grid_cells {requested} → {capped} (AMReX 26.04 stability; "
            f"export WARPX_MAX_PIC_GRID to allow larger grids)."
        )
        pic["grid_cells"] = capped
    else:
        pic["grid_cells"] = requested

    ov_path = patch_geometry_into_picmi_overrides(cfg)
    overrides = json.loads(ov_path.read_text(encoding="utf-8"))
    steps = int(pic.get("steps", 400))
    capped_steps = cap_pic_steps_for_stability(steps, overrides)
    if capped_steps < steps:
        notes.append(f"PIC steps {steps} → {capped_steps} for {pic['grid_cells']}² grid.")
        pic["steps"] = capped_steps
    return notes


def cap_pic_steps_for_stability(n_steps: int, overrides: dict[str, Any]) -> int:
    """
    Avoid known AMReX 26.04 SIGSEGV on large 2D grids (local pywarpx).

    128² is stable through 400+ steps; 256² can fail near step 440; 512² is untested
    and capped more aggressively. Reduction uses the last plotfile only.
    """
    cells = overrides.get("number_of_cells") or [128, 128]
    nx = int(cells[0]) if cells else 128
    if nx >= 512:
        return min(int(n_steps), 300)
    if nx >= 256:
        return min(int(n_steps), 400)
    return int(n_steps)


def patch_geometry_into_picmi_overrides(cfg: dict[str, Any]) -> Path:
    """Merge chain_config geometry into the chain PICMI overrides file."""
    path = ensure_picmi_overrides()
    g = cfg.get("geometry", {})
    overrides = json.loads(path.read_text(encoding="utf-8"))
    cells = pic_grid_cells(cfg)
    overrides.update(
        {
            "r_anode_m": float(g.get("r_anode_m", overrides.get("r_anode_m", 0.04))),
            "r_cathode_m": float(g.get("r_cathode_m", overrides.get("r_cathode_m", 0.01))),
            "V_cathode_v": float(g.get("V_cathode_v", overrides.get("V_cathode_v", -600_000))),
            "B_axial_tesla": float(g.get("B_axial_tesla", overrides.get("B_axial_tesla", 2.0))),
            "domain_half_extent_m": max(
                float(g.get("r_anode_m", 0.04)),
                float(overrides.get("domain_half_extent_m", 0.05)),
            ),
            "number_of_cells": [cells, cells],
        }
    )
    path.write_text(json.dumps(overrides, indent=2), encoding="utf-8")
    return path


def ensure_config() -> dict[str, Any]:
    """Load chain config or create default template on disk."""
    CHAIN_ROOT.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.is_file():
        cfg = write_chain_config_template()
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    else:
        cfg = load_config()
    inj = cfg.get("injectants", {})
    if "laser_ablation_hz" not in inj and (
        "b2h6_sccm" in inj or "b10h14_equiv_sccm" in inj
    ):
        cfg["injectants"] = normalize_injectants_cfg(inj)
        save_config(cfg)
    ensure_picmi_overrides()
    pic = cfg.setdefault("pic", {})
    migrated = False
    if "grid_cells" not in pic:
        pic["grid_cells"] = 128
        migrated = True
    elif int(pic.get("grid_cells", 128)) > int(os.environ.get("WARPX_MAX_PIC_GRID", "128")):
        migrated = True
    if stabilize_pic_settings(cfg):
        migrated = True
    if migrated:
        save_config(cfg)
    else:
        patch_geometry_into_picmi_overrides(cfg)
    return cfg


def save_config(cfg: dict[str, Any]) -> None:
    cfg["generated_utc"] = utc_now()
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def step_completed(step: str) -> bool:
    try:
        cfg = load_config()
    except FileNotFoundError:
        return False
    ok = CHAIN_ROOT / cfg["steps"][step]["ok_marker"]
    if not ok.is_file():
        return False
    try:
        data = load_step_json(step)
        if data.get("ok") is False:
            return False
    except Exception:
        pass
    return True


def step_artifact_path(step: str) -> Path:
    cfg = load_config()
    return CHAIN_ROOT / cfg["steps"][step]["artifact"]


def _json_safe(value: Any) -> Any:
    """Convert numpy/scalar types for ``json.dumps``."""
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def save_step(step: str, payload: dict[str, Any]) -> Path:
    """Write step artifact JSON; step_ok marker only when the step succeeded."""
    cfg = load_config()
    rel = cfg["steps"][step]["artifact"]
    out = CHAIN_ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    body = {"step": step, "generated_utc": utc_now(), **_json_safe(payload)}
    out.write_text(json.dumps(body, indent=2), encoding="utf-8")
    ok_path = CHAIN_ROOT / cfg["steps"][step]["ok_marker"]
    succeeded = payload.get("ok", True) is not False
    if succeeded:
        ok_path.write_text(json.dumps({"ok": True, "artifact": str(out)}, indent=2), encoding="utf-8")
    elif ok_path.is_file():
        ok_path.unlink()
    return out


def require_step(step: str) -> None:
    cfg = load_config()
    ok = CHAIN_ROOT / cfg["steps"][step]["ok_marker"]
    if not ok.is_file():
        raise RuntimeError(f"Prerequisite step {step} not complete (missing {ok})")


def load_step_json(step: str) -> dict[str, Any]:
    cfg = load_config()
    path = CHAIN_ROOT / cfg["steps"][step]["artifact"]
    return json.loads(path.read_text(encoding="utf-8"))


def pad_startup_from_cfg(pad_cfg: dict[str, Any]) -> PadStartupState:
    """
    Build ``PadStartupState`` from ``chain_config.json`` pad block.

    Single source of truth for batch chain runners and Proof Suite GUI — every
    interlock switch must be read here so step 03 fuel/R are not silently zeroed.
    """
    return PadStartupState(
        pad_apu_online=bool(pad_cfg.get("pad_apu_online", False)),
        starter_engage=bool(pad_cfg.get("starter_engage", False)),
        bleed_air_open=bool(pad_cfg.get("bleed_air_open", False)),
        vacuum_interlock_ok=bool(pad_cfg.get("vacuum_interlock_ok", False)),
        laser_armed=bool(pad_cfg.get("laser_armed", False)),
        hv_enabled=bool(pad_cfg.get("hv_enabled", False)),
        startup_trigger=bool(pad_cfg.get("startup_trigger", False)),
        throttle=float(pad_cfg.get("throttle", 0.0)),
        compressor=float(pad_cfg.get("compressor", 0.0)),
        cathode_pulse=float(pad_cfg.get("cathode_pulse", 0.75)),
        laminar_relaminarization=bool(pad_cfg.get("laminar_relaminarization", True)),
    )


def _operating_from_cfg(cfg: dict[str, Any]) -> OperatingPoint:
    inj = normalize_injectants_cfg(cfg["injectants"])
    pad_cfg = cfg["pad"]
    return OperatingPoint(
        throttle=float(pad_cfg.get("throttle", 0.85)),
        compressor=float(pad_cfg.get("compressor", 0.7)),
        cathode_pulse=float(pad_cfg.get("cathode_pulse", 0.75)),
        h2_sccm=float(inj["h2_sccm"]),
        laser_ablation_hz=float(inj["laser_ablation_hz"]),
        b11_target_index=int(inj.get("b11_target_index", 0)),
    )


def plant_scales_from_cfg(cfg: dict[str, Any]) -> "PlantScales":
    """Merge ``chain_config.json`` ``plant_scales`` over assembly-spec defaults."""
    from ssto.orbitron.simulator.physics_spec import load_plant_scales
    from ssto.orbitron.simulator.types import PlantScales

    base = load_plant_scales()
    overrides = cfg.get("plant_scales") or {}
    if not overrides:
        return base
    return PlantScales(
        target_gross_power_mw=float(
            overrides.get("target_gross_power_mw", base.target_gross_power_mw)
        ),
        jet_propulsive_efficiency=float(
            overrides.get("jet_propulsive_efficiency", base.jet_propulsive_efficiency)
        ),
        heat_kw_at_full=float(overrides.get("heat_kw_at_full", base.heat_kw_at_full)),
        beam_screen_kw_per_ma=float(
            overrides.get("beam_screen_kw_per_ma", base.beam_screen_kw_per_ma)
        ),
        thrust_lbf_at_full=float(
            overrides.get("thrust_lbf_at_full", base.thrust_lbf_at_full)
        ),
        mass_flow_kgps_at_full=float(
            overrides.get("mass_flow_kgps_at_full", base.mass_flow_kgps_at_full)
        ),
        density_log10_at_full=float(
            overrides.get("density_log10_at_full", base.density_log10_at_full)
        ),
    )


def base_inputs():
    """Build SimulatorInputs from chain config + completed prior steps."""
    cfg = load_config()
    g = cfg["geometry"]
    pad_cfg = cfg["pad"]
    proof = cfg.get("proof_mode", True)

    pic_e = float("nan")
    pic_b = float("nan")
    fc_mw = float("nan")
    clump_index = 1.0
    clump_reduction = 1.0
    laminar = bool(pad_cfg.get("laminar_relaminarization", True))

    if (CHAIN_ROOT / cfg["steps"]["02"]["ok_marker"]).is_file():
        p2 = load_step_json("02")
        pic_e = float(p2.get("rho_e_norm", float("nan")))
    if (CHAIN_ROOT / cfg["steps"]["03"]["ok_marker"]).is_file():
        p3 = load_step_json("03")
        fc_norm = p3.get("fuel_coupling_norm")
        if fc_norm is not None:
            pic_b = float(fc_norm)
        fc_mw = float(p3.get("integrated_fusion_power_mw", float("nan")))
        clump_index = float(p3.get("clump_index_final", 1.0))
        clump_reduction = float(p3.get("clump_reduction_ratio", 1.0))
        laminar = bool(p3.get("laminar_enabled", laminar))

    u = UnobtaniumParams(
        fusion_reactivity_scale=1.0 if proof else float(cfg["unobtanium"].get("fusion_reactivity_scale", 1.0)),
        field_emission_margin=float(cfg["unobtanium"].get("field_emission_margin", 1.0)),
        max_wall_heat_flux_W_m2=float(cfg["unobtanium"].get("max_wall_heat_flux_W_m2", 2.0e6)),
        ch4_cooling_effectiveness=float(cfg["unobtanium"].get("ch4_cooling_effectiveness", 1.0)),
        hts_capability_scale=float(cfg["unobtanium"].get("hts_capability_scale", 1.0)),
        beam_coupling_scale=float(cfg["unobtanium"].get("beam_coupling_scale", 1.0)),
    )

    inp = SimulatorInputs(
        geometry=DeviceGeometry(
            r_anode_m=float(g["r_anode_m"]),
            r_cathode_m=float(g["r_cathode_m"]),
            length_m=float(g["length_m"]),
            V_cathode_v=float(g["V_cathode_v"]),
            B_axial_tesla=float(g["B_axial_tesla"]),
        ),
        operating=_operating_from_cfg(cfg),
        pad=replace(pad_startup_from_cfg(pad_cfg), laminar_relaminarization=laminar),
        unobtanium=u,
        scales=plant_scales_from_cfg(cfg),
        pic_rho_e_norm=pic_e,
        pic_beam_rho_norm=pic_b,
        fusion_channel_power_mw=fc_mw if proof else fc_mw,
    )
    meta = {
        "clump_index": clump_index,
        "clump_reduction_ratio": clump_reduction,
        "proof_mode": proof,
    }
    return inp, meta


def steady_to_dict(res) -> dict[str, Any]:
    return _json_safe({k: getattr(res, k) for k in res.__dataclass_fields__})


def step08_blocks_inverse(step08: dict[str, Any] | None) -> tuple[bool, str]:
    """
    Step 09 is gap-fill after a completed export, not a substitute for failed forward specs.
    Returns (allowed, message).
    """
    if not step08:
        return False, "Step 08 not complete — run validation export first."
    fails = [
        c["spec_id"]
        for c in step08.get("spec_checks", [])
        if str(c.get("status", "")).upper() == "FAIL"
    ]
    if fails:
        return False, (
            f"Step 08 has FAIL checks ({', '.join(fails)}) — fix the forward chain "
            "(e.g. U3: B ≤ 2 T at HTS scale 1; FCH/U4: power & coupling) before inverse solve."
        )
    return True, "OK"


def validation_checks_to_dict(report) -> list[dict[str, Any]]:
    return [
        {
            "spec_id": c.spec_id,
            "title": c.title,
            "status": c.status.value,
            "required": c.required,
            "achieved": c.achieved,
            "margin": c.margin,
            "notes": c.notes,
        }
        for c in report.checks
    ]


def enable_proof_env() -> None:
    os.environ["ORBITRON_PROOF_CHAIN"] = "1"
    os.environ["ORBITRON_CHAIN_ROOT"] = str(CHAIN_ROOT)


def write_chain_config_template() -> dict[str, Any]:
    """Default chain_config.json contents (also written by chain_00)."""
    return {
        "schema_version": 1,
        "proof_mode": True,
        "generated_utc": utc_now(),
        "repo_root": str(_REPO),
        "chain_root": str(CHAIN_ROOT),
        "geometry": {
            "r_anode_m": 0.04,
            "r_cathode_m": 0.01,
            "length_m": 1.2,
            "V_cathode_v": 600_000.0,
            "B_axial_tesla": 2.0,
        },
        "injectants": {
            "h2_sccm": 80.0,
            "laser_ablation_hz": 10.0,
            "b11_target_index": 0,
        },
        "pad": {
            "throttle": 0.85,
            "compressor": 0.7,
            "cathode_pulse": 0.75,
            "laminar_relaminarization": True,
            "pad_apu_online": False,
            "starter_engage": False,
            "bleed_air_open": False,
            "vacuum_interlock_ok": False,
            "laser_armed": False,
            "hv_enabled": False,
            "startup_trigger": False,
        },
        "unobtanium": {
            "fusion_reactivity_scale": 1.0,
            "field_emission_margin": 1.0,
            "max_wall_heat_flux_W_m2": 2.0e6,
            "ch4_cooling_effectiveness": 1.0,
            "hts_capability_scale": 1.0,
            "beam_coupling_scale": 1.0,
        },
        "pic": {"steps": 400, "diag_period": 40, "grid_cells": 128, "skip_if_ok": True},
        "fusion_channel": {
            "n_s": 160,
            "n_r": 72,
            "n_frames": 72,
            "total_time_s": 0.002,
            "h2_ref_sccm": 80.0,
            "laser_ref_hz": 10.0,
            "stochastic_seed": 42,
            "noise_fraction_off": 0.14,
        },
        "paths": {
            "picmi_overrides_generated": "build/orbitron/generated/picmi_overrides.json",
            "picmi_overrides_chain": "build/orbitron/chain/00_spec/picmi_overrides.json",
            "design_validation_yaml": "build/orbitron/chain/08_export/design_validation.yaml",
        },
        "steps": {
            "00": {"artifact": "00_spec/step_result.json", "ok_marker": "00_spec/step_ok.json"},
            "01": {"artifact": "01_pic/step_result.json", "ok_marker": "01_pic/step_ok.json"},
            "02": {"artifact": "02_pic_norms/pic_norms.json", "ok_marker": "02_pic_norms/step_ok.json"},
            "03": {"artifact": "03_fusion_channel/fusion_channel.json", "ok_marker": "03_fusion_channel/step_ok.json"},
            "04": {"artifact": "04_fueling/fueling.json", "ok_marker": "04_fueling/step_ok.json"},
            "05": {"artifact": "05_burn/burn.json", "ok_marker": "05_burn/step_ok.json"},
            "06": {"artifact": "06_plant/plant.json", "ok_marker": "06_plant/step_ok.json"},
            "07": {"artifact": "07_closure/closure.json", "ok_marker": "07_closure/step_ok.json"},
            "08": {"artifact": "08_export/step_result.json", "ok_marker": "08_export/step_ok.json"},
            "09": {"artifact": "09_solve/solve.json", "ok_marker": "09_solve/step_ok.json"},
        },
    }
