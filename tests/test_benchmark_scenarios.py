"""Three-scenario benchmark tests."""
from __future__ import annotations

from ssto.orbitron.experiment.benchmark_scenarios import evaluate_benchmark_scenarios
from ssto.orbitron.simulator.physics_evidence import solve_stress_inverse
from ssto.orbitron.simulator.types import SimulatorInputs


def _base_inputs() -> SimulatorInputs:
    from tools.orbitron_proof_chain.chain_lib import base_inputs as chain_base

    inp, _ = chain_base()
    return inp


def test_benchmark_today_much_lower_than_pretend():
    inp = _base_inputs()
    payload = evaluate_benchmark_scenarios(inp)
    by_id = {r["id"]: r for r in payload["scenarios"]}
    pretend = by_id["pretend"]["gross_power_mw"]
    today = by_id["today"]["gross_power_mw"]
    assert pretend > today
    assert today < inp.scales.target_gross_power_mw  # (b) must not close 3.5 MW target


def test_stress_inverse_reports_branch_or_infeasible():
    inp = _base_inputs()
    stress = solve_stress_inverse(inp, target_mw=3.5)
    assert stress["sigma_v_design_over_literature"] > 100.0
    if stress["success"]:
        assert abs(float(stress["residual_mw"])) < 0.25
        assert float(stress["fusion_reactivity_scale_required"]) >= 1.0
    else:
        assert stress["success"] is False


def test_stress_inverse_module_reports_branch():
    inp = _base_inputs()
    stress = solve_stress_inverse(inp, target_mw=3.5)
    assert stress["sigma_v_design_over_literature"] > 100.0
