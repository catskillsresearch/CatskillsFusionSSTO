#!/usr/bin/env python3
"""Step 5: p-¹¹B burn power (proof: fusion_reactivity_scale=1)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import base_inputs, enable_proof_env, load_config, require_step, save_step


def main() -> int:
    require_step("04")
    enable_proof_env()
    inp, _ = base_inputs()
    cfg = load_config()
    target_mw = inp.scales.target_gross_power_mw

    from ssto.orbitron.simulator.fusion_pb11 import evaluate_fusion_pb11
    from ssto.orbitron.simulator.pad_startup import effective_operating_point

    g = inp.geometry
    op, _ = effective_operating_point(inp.operating, inp.pad)
    fus = evaluate_fusion_pb11(
        r_anode_m=g.r_anode_m,
        length_m=g.length_m,
        V_cathode_v=g.V_cathode_v,
        throttle=op.throttle,
        cathode_pulse=op.cathode_pulse,
        h2_sccm=op.h2_sccm,
        b2h6_sccm=op.b2h6_sccm,
        fusion_reactivity_scale=inp.unobtanium.fusion_reactivity_scale,
        pic_rho_e_norm=inp.pic_rho_e_norm,
    )

    save_step(
        "05",
        {
            "fusion_power_mw": fus.fusion_power_mw,
            "target_gross_power_mw": target_mw,
            "shortfall_mw": target_mw - fus.fusion_power_mw,
            "proof_mode": cfg.get("proof_mode", True),
            "reaction_rate_m3_s": fus.reaction_rate_m3_s,
        },
    )
    print(f"P_fusion={fus.fusion_power_mw:.6f} MW (target {target_mw} MW)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
