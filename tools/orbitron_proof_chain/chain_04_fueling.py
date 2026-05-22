#!/usr/bin/env python3
"""Step 4: fueling -> n_p, n_B, T_i (forward, no MW knob)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import base_inputs, enable_proof_env, require_step, save_step


def main() -> int:
    require_step("02")
    enable_proof_env()
    inp, _ = base_inputs()

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
        laser_ablation_hz=op.laser_ablation_hz,
        fusion_reactivity_scale=inp.unobtanium.fusion_reactivity_scale,
        pic_rho_e_norm=inp.pic_rho_e_norm,
    )

    save_step(
        "04",
        {
            "n_proton_m3": fus.n_proton_m3,
            "n_boron_m3": fus.n_boron_m3,
            "ion_temperature_kev": fus.ion_temperature_kev,
            "sigma_v_m3_s": fus.sigma_v_m3_s,
            "plasma_volume_m3": fus.plasma_volume_m3,
            "confinement_factor": fus.confinement_factor,
            "fueling_mix_scale": fus.fueling_mix_scale,
            "fusion_reactivity_scale": inp.unobtanium.fusion_reactivity_scale,
        },
    )
    print(f"n_p={fus.n_proton_m3:.3e} n_B={fus.n_boron_m3:.3e} T_i={fus.ion_temperature_kev:.1f} keV")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
