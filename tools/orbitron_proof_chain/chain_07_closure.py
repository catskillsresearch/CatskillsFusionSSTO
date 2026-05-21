#!/usr/bin/env python3
"""Step 7: jet closure F² ≈ 2 η P ṁ from proof-chain plant outputs."""
from __future__ import annotations

import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import enable_proof_env, load_step_json, require_step, save_step

LBF_TO_N = 4.4482216152605


def main() -> int:
    require_step("06")
    enable_proof_env()
    p6 = load_step_json("06")
    s = p6["steady_state"]
    gross_mw = float(s["gross_power_mw"])
    thrust_lbf = float(s["thrust_lbf"])
    mdot = float(s["mass_flow_kgps"])
    jet_mw = float(s["jet_kinetic_power_mw"])
    eta = jet_mw / gross_mw if gross_mw > 1e-9 else 0.0

    thrust_n = thrust_lbf * LBF_TO_N
    p_from_thrust_w = (thrust_n**2) / (2.0 * mdot) if mdot > 1e-9 else 0.0
    p_jet_w = jet_mw * 1.0e6
    rel_err = abs(p_from_thrust_w - p_jet_w) / max(p_jet_w, 1.0)
    f2 = thrust_n**2
    f2_target = 2.0 * p_jet_w * mdot
    f2_rel = abs(f2 - f2_target) / max(f2_target, 1.0)

    save_step(
        "07",
        {
            "gross_power_mw": gross_mw,
            "jet_kinetic_power_mw": jet_mw,
            "jet_propulsive_efficiency": eta,
            "thrust_lbf": thrust_lbf,
            "mass_flow_kgps": mdot,
            "p_from_thrust_w": p_from_thrust_w,
            "p_jet_w": p_jet_w,
            "closure_rel_error": rel_err,
            "f2_rel_error": f2_rel,
            "passes_12pct": rel_err <= 0.12,
        },
    )
    print(f"closure_rel_error={rel_err:.4f} passes_12pct={rel_err <= 0.12}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
