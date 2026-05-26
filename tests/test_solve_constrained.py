"""Constrained unobtanium inverse (trust-region + hard U1–U4 gates)."""
from __future__ import annotations

import os

import pytest

from ssto.orbitron.simulator.fusion_pb11 import pb11_reactivity_m3_s
from ssto.orbitron.simulator.physics_evidence import solve_margin_inverse, solve_stress_inverse
from ssto.orbitron.simulator.solve_constrained import solve_unobtanium_constrained
from ssto.orbitron.simulator.validation import SpecStatus


def _base_inputs():
    from tools.orbitron_proof_chain.chain_lib import base_inputs as chain_base

    inp, _ = chain_base()
    return inp


def test_margin_constrained_near_nominal():
    inp = _base_inputs()
    report = solve_unobtanium_constrained(inp, 3.5, mode="margin", fusion_scale_max=5.0)
    assert report.success
    assert report.validation is not None
    assert report.validation.design_validated
    assert abs(report.residual_mw) < 0.25
    assert report.inputs.unobtanium.fusion_reactivity_scale < 5.0


def test_stress_constrained_literature_infeasible_or_feasible():
    """Literature σv at pessimistic start: if feasible, all hard specs pass."""
    inp = _base_inputs()
    os.environ["ORBITRON_REACTIVITY_MODEL"] = "literature"
    try:
        report = solve_unobtanium_constrained(inp, 3.5, mode="stress", fusion_scale_max=5000.0)
    finally:
        os.environ.pop("ORBITRON_REACTIVITY_MODEL", None)
    if report.success:
        assert report.validation is not None
        assert report.validation.design_validated
        fails = [c for c in report.validation.checks if c.status == SpecStatus.FAIL]
        assert not fails
    else:
        # Infeasible is an acceptable scientific outcome on literature path.
        assert report.validation is not None


def test_stress_inverse_integration():
    inp = _base_inputs()
    stress = solve_stress_inverse(inp, target_mw=3.5)
    assert stress["sigma_v_design_over_literature"] > 100.0
    if stress["success"]:
        assert stress["fusion_reactivity_scale_required"] >= 1.0


def test_margin_inverse_integration():
    inp = _base_inputs()
    margin = solve_margin_inverse(inp, target_mw=3.5)
    if margin.get("success"):
        gf = margin.get("gap_factors") or {}
        assert gf.get("fusion_reactivity_scale", 99) < 3.0
