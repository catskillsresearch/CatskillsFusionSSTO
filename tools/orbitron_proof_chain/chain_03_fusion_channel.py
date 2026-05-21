#!/usr/bin/env python3
"""Step 3: longitudinal fusion channel s–r + laminar clump metrics."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import (  # noqa: E402
    base_inputs,
    enable_proof_env,
    require_step,
    save_step,
)


def main() -> int:
    require_step("02")
    enable_proof_env()
    inp, _ = base_inputs()

    from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus, focus_domain
    from ssto.orbitron.simulator.longitudinal.fusion_channel_sr import (
        laminar_hack_from_inputs,
        run_fusion_channel_sr,
    )

    dom = focus_domain(LongitudinalFocus.FUSION_CHANNEL_SR, inp)
    laminar = laminar_hack_from_inputs(inp, force_off=not inp.pad.laminar_relaminarization)
    fc = run_fusion_channel_sr(dom, inp, laminar=laminar, compare_without_hack=True)

    save_step(
        "03",
        {
            "integrated_fusion_power_mw": fc.integrated_fusion_power_mw,
            "fusion_pb11_power_mw": fc.meta.get("fusion_pb11_power_mw"),
            "clump_index_final": fc.clump_index_final,
            "clump_reduction_ratio": fc.clump_reduction_ratio,
            "laminar_enabled": laminar.enabled,
            "channel_power_ratio": fc.meta.get("channel_power_ratio"),
            "sigma_v_m3_s": fc.meta.get("sigma_v_m3_s"),
            "T_ion_kev": fc.meta.get("T_ion_kev"),
        },
    )
    print(
        f"clump={fc.clump_index_final:.2f} reduction={fc.clump_reduction_ratio:.2f}× "
        f"P_mw={fc.integrated_fusion_power_mw:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
