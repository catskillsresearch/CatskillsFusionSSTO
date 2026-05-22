"""
Shared helpers for the Orbitron first-principles proof chain (fixed paths under build/orbitron/chain).
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

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
            f"Missing {CONFIG_PATH}. Run tools/orbitron_proof_chain/chain_00_spec.sh first."
        )
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def ensure_config() -> dict[str, Any]:
    """Load chain config or create default template on disk."""
    CHAIN_ROOT.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.is_file():
        cfg = write_chain_config_template()
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return load_config()


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
    if isinstance(value, (np.floating,)):
        return float(value)
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


def base_inputs():
    """Build SimulatorInputs from chain config + completed prior steps."""
    from ssto.orbitron.simulator.types import (
        DeviceGeometry,
        OperatingPoint,
        PadStartupState,
        SimulatorInputs,
        UnobtaniumParams,
    )
    from ssto.orbitron.simulator.physics_spec import load_plant_scales

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
        pic_b = float(p2.get("rho_beam_norm", float("nan")))
    if (CHAIN_ROOT / cfg["steps"]["03"]["ok_marker"]).is_file():
        p3 = load_step_json("03")
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
        operating=OperatingPoint(
            h2_sccm=float(cfg["injectants"]["h2_sccm"]),
            b2h6_sccm=float(cfg["injectants"]["b2h6_sccm"]),
        ),
        pad=PadStartupState(
            pad_apu_online=True,
            starter_engage=True,
            bleed_air_open=True,
            startup_trigger=True,
            throttle=float(pad_cfg["throttle"]),
            compressor=float(pad_cfg["compressor"]),
            cathode_pulse=float(pad_cfg["cathode_pulse"]),
            laminar_relaminarization=laminar,
        ),
        unobtanium=u,
        scales=load_plant_scales(),
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
        "injectants": {"h2_sccm": 80.0, "b2h6_sccm": 8.0},
        "pad": {
            "throttle": 0.85,
            "compressor": 0.7,
            "cathode_pulse": 0.75,
            "laminar_relaminarization": True,
        },
        "unobtanium": {
            "fusion_reactivity_scale": 1.0,
            "field_emission_margin": 1.0,
            "max_wall_heat_flux_W_m2": 2.0e6,
            "ch4_cooling_effectiveness": 1.0,
            "hts_capability_scale": 1.0,
            "beam_coupling_scale": 1.0,
        },
        "pic": {"steps": 500, "diag_period": 100, "skip_if_ok": True},
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
