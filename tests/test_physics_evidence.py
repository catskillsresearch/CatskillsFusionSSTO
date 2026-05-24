"""Physics evidence and reactivity model tests."""
from __future__ import annotations

from ssto.orbitron.simulator.fusion_pb11 import pb11_reactivity_m3_s
from ssto.orbitron.simulator.physics_constants import EMISSION_FIELD_LIMIT_V_M


def test_literature_reactivity_lower_than_design():
    t = 300.0
    d = pb11_reactivity_m3_s(t, model="design")
    lit = pb11_reactivity_m3_s(t, model="literature")
    assert lit < d
    assert d / lit > 100.0


def test_u1_limit_is_program_gradient_class():
    gap_m = 0.03
    v = 600_000.0
    e = abs(v) / gap_m
    assert abs(e - EMISSION_FIELD_LIMIT_V_M) < 1.0e4
