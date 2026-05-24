"""Unobtanium inverse solve + gap-closed analytics re-run for experiment reports."""
from __future__ import annotations

import os
from copy import deepcopy
from typing import Any

from tools.orbitron_proof_chain.chain_lib import (
    CONFIG_PATH,
    enable_proof_env,
    load_config,
    save_config,
    save_step,
    steady_to_dict,
    validation_checks_to_dict,
)


def _unobtanium_dict(u: Any) -> dict[str, float]:
    return {
        "fusion_reactivity_scale": float(u.fusion_reactivity_scale),
        "field_emission_margin": float(u.field_emission_margin),
        "max_wall_heat_flux_W_m2": float(u.max_wall_heat_flux_W_m2),
        "ch4_cooling_effectiveness": float(u.ch4_cooling_effectiveness),
        "hts_capability_scale": float(u.hts_capability_scale),
        "beam_coupling_scale": float(u.beam_coupling_scale),
    }


def run_inverse_gap_solve(*, allow_forward_fail: bool = True) -> dict[str, Any]:
    """
    Step 09 — minimum unobtanium knobs to hit target MW.

    Unlike the Proof Suite GUI path, ``allow_forward_fail=True`` (default for
    headless reports) runs even when step 08 has FAIL checks (e.g. U4c shortfall).
    """
    from tools.orbitron_proof_chain.chain_lib import base_inputs, load_step_json, require_step, step08_blocks_inverse

    require_step("08")
    if not allow_forward_fail:
        s8 = load_step_json("08")
        allowed, msg = step08_blocks_inverse(s8)
        if not allowed:
            raise RuntimeError(msg)

    inp, _ = base_inputs()
    os.environ.pop("ORBITRON_PROOF_CHAIN", None)
    from ssto.orbitron.simulator.solve import solve_unobtanium_requirements

    report = solve_unobtanium_requirements(inp, target_mw=inp.scales.target_gross_power_mw)
    u = report.inputs.unobtanium
    payload = {
        "success": bool(report.success),
        "message": report.message,
        "residual_mw": report.residual_mw,
        "target_mw": inp.scales.target_gross_power_mw,
        "unobtanium_required": _unobtanium_dict(u),
        "unobtanium_nominal": _unobtanium_dict(inp.unobtanium),
        "pad_solved": {
            "throttle": float(report.inputs.pad.throttle),
            "compressor": float(report.inputs.pad.compressor),
            "cathode_pulse": float(report.inputs.pad.cathode_pulse),
        },
        "steady_state": steady_to_dict(report.result),
        "spec_checks": validation_checks_to_dict(report.validation) if report.validation else [],
        "design_validated_at_solve": bool(report.validation and report.validation.design_validated),
    }
    save_step("09", payload)
    enable_proof_env()
    return payload


def apply_solved_knobs_to_chain(step09: dict[str, Any]) -> dict[str, Any]:
    """Merge inverse-solve knobs into ``chain_config.json`` for gap-closed analytics."""
    cfg = load_config()
    proof_snapshot = {
        "unobtanium": deepcopy(cfg.get("unobtanium", {})),
        "pad_levers": {
            "throttle": float(cfg["pad"].get("throttle", 0.85)),
            "compressor": float(cfg["pad"].get("compressor", 0.7)),
        },
        "proof_mode": bool(cfg.get("proof_mode", True)),
    }
    cfg.setdefault("experiment", {})["proof_forward_snapshot"] = proof_snapshot

    req = step09.get("unobtanium_required") or {}
    cfg.setdefault("unobtanium", {}).update(req)

    pad_solved = step09.get("pad_solved") or {}
    if pad_solved:
        cfg["pad"]["throttle"] = float(pad_solved.get("throttle", cfg["pad"].get("throttle", 0.85)))
        cfg["pad"]["compressor"] = float(
            pad_solved.get("compressor", cfg["pad"].get("compressor", 0.7))
        )

    cfg["proof_mode"] = False
    cfg.setdefault("experiment", {})["gap_closed_analytics"] = True
    save_config(cfg)
    return cfg


def rerun_analytics_with_gap_knobs() -> dict[str, dict[str, Any]]:
    """
    Re-run steps 05–08 with solved unobtanium (proof mode off).

    Returns payloads keyed ``05_gap`` … ``08_gap``.
    """
    from ssto.orbitron.simulator.proof_chain.runners import (
        run_step_05,
        run_step_06,
        run_step_07,
        run_step_08,
    )

    os.environ.pop("ORBITRON_PROOF_CHAIN", None)
    out: dict[str, dict[str, Any]] = {}
    for step_id, fn in (
        ("05_gap", run_step_05),
        ("06_gap", run_step_06),
        ("07_gap", run_step_07),
        ("08_gap", run_step_08),
    ):
        out[step_id] = fn()
    enable_proof_env()
    return out


def gap_factors(step09: dict[str, Any]) -> dict[str, float]:
    """Required / nominal scale for each unobtanium knob (1.0 = no gap)."""
    req = step09.get("unobtanium_required") or {}
    nom = step09.get("unobtanium_nominal") or {}
    factors: dict[str, float] = {}
    for key, required in req.items():
        baseline = float(nom.get(key, 1.0))
        if baseline <= 0:
            baseline = 1.0
        factors[key] = float(required) / baseline
    return factors
