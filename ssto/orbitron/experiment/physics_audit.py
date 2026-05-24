"""Experiment-runner hook for physics evidence audit."""
from __future__ import annotations

from typing import Any

from ssto.orbitron.simulator.physics_evidence import run_physics_audit
from tools.orbitron_proof_chain.chain_lib import base_inputs


def run_experiment_physics_audit(
    *,
    tier1_validated: bool,
    require_pic: bool = False,
) -> dict[str, Any]:
    inp, _meta = base_inputs()
    report = run_physics_audit(
        inp,
        tier1_validated=tier1_validated,
        require_pic=require_pic,
        include_margin_inverse=tier1_validated,
    )
    return report.to_dict()
