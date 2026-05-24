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
    Step 09 — **stress** unobtanium inverse (literature ⟨σv⟩, pessimistic start).

    This is the primary unobtanium goal for reports: minimum performance scales
    needed when reactivity is **not** calibrated to 3.5 MW.

    Also records a **margin** inverse (design σv) when forward Tier-1 already passes.
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

    from ssto.orbitron.simulator.physics_evidence import (
        confirm_at_required_knobs,
        solve_margin_inverse,
        solve_stress_inverse,
    )
    from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
    from ssto.orbitron.simulator.validation import validate_design

    target_mw = inp.scales.target_gross_power_mw
    stress = solve_stress_inverse(inp, target_mw=target_mw)

    req = stress.get("unobtanium_required") or {}
    nom = stress.get("unobtanium_nominal") or _unobtanium_dict(inp.unobtanium)

    # Evaluate solved point under literature model for step JSON steady state
    from dataclasses import replace

    from ssto.orbitron.simulator.types import UnobtaniumParams

    u_req = UnobtaniumParams(
        fusion_reactivity_scale=float(req.get("fusion_reactivity_scale", 1.0)),
        field_emission_margin=float(req.get("field_emission_margin", 1.0)),
        max_wall_heat_flux_W_m2=float(req.get("max_wall_heat_flux_W_m2", 2e6)),
        ch4_cooling_effectiveness=float(req.get("ch4_cooling_effectiveness", 1.0)),
        hts_capability_scale=float(req.get("hts_capability_scale", 1.0)),
        beam_coupling_scale=float(req.get("beam_coupling_scale", 1.0)),
    )
    pad_solved = stress.get("pad_solved") or {}
    solved_inp = replace(
        inp,
        unobtanium=u_req,
        pad=replace(
            inp.pad,
            throttle=float(pad_solved.get("throttle", inp.pad.throttle)),
            compressor=float(pad_solved.get("compressor", inp.pad.compressor)),
            cathode_pulse=float(pad_solved.get("cathode_pulse", inp.pad.cathode_pulse)),
        ),
    )
    os.environ["ORBITRON_REACTIVITY_MODEL"] = "literature"
    try:
        res = evaluate_steady_state(solved_inp)
        vrep = validate_design(solved_inp, res)
    finally:
        os.environ.pop("ORBITRON_REACTIVITY_MODEL", None)

    conf_mw, conf_ok = confirm_at_required_knobs(inp, req, target_mw=target_mw)
    # Same threshold as physics audit: ≥ target − tolerance on design σv

    margin: dict[str, Any] | None = None
    s8 = load_step_json("08")
    if s8.get("design_validated"):
        margin = solve_margin_inverse(inp, target_mw=target_mw)

    payload = {
        "success": bool(stress.get("success")),
        "message": (
            "Stress inverse (literature σv, pessimistic start)"
            + (" OK" if stress.get("success") else " — see spec_checks")
        ),
        "inverse_mode": "stress",
        "residual_mw": stress.get("residual_mw"),
        "target_mw": target_mw,
        "unobtanium_required": req,
        "unobtanium_nominal": nom,
        "gap_factors": stress.get("gap_factors") or {},
        "pad_solved": pad_solved,
        "steady_state": steady_to_dict(res),
        "spec_checks": validation_checks_to_dict(vrep) if vrep else [],
        "design_validated_at_solve": bool(vrep and vrep.design_validated),
        "stress_inverse": stress,
        "margin_inverse": margin,
        "forward_confirmation_mw": conf_mw,
        "forward_confirmation_passes": conf_ok,
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
    cfg.setdefault("experiment", {})["gap_closed_reactivity_model"] = "design"
    save_config(cfg)
    return cfg


def rerun_analytics_with_gap_knobs() -> dict[str, dict[str, Any]]:
    """
    Re-run steps 05–08 with solved unobtanium (proof mode off, design σv).

    Returns payloads keyed ``05_gap`` … ``08_gap``.
    """
    from ssto.orbitron.simulator.proof_chain.runners import (
        run_step_05,
        run_step_06,
        run_step_07,
        run_step_08,
    )

    os.environ.pop("ORBITRON_PROOF_CHAIN", None)
    os.environ["ORBITRON_REACTIVITY_MODEL"] = "design"
    out: dict[str, dict[str, Any]] = {}
    try:
        for step_id, fn in (
            ("05_gap", run_step_05),
            ("06_gap", run_step_06),
            ("07_gap", run_step_07),
            ("08_gap", run_step_08),
        ):
            out[step_id] = fn()
    finally:
        os.environ.pop("ORBITRON_REACTIVITY_MODEL", None)
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
