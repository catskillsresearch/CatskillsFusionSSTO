#!/usr/bin/env python3
"""Step 9 (optional): inverse solve — minimum unobtanium to hit target MW."""
from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import (
    base_inputs,
    load_config,
    require_step,
    save_step,
    steady_to_dict,
    validation_checks_to_dict,
)


def main() -> int:
    require_step("08")
    inp, _ = base_inputs()
    cfg = load_config()
    target = inp.scales.target_gross_power_mw

    from ssto.orbitron.simulator.solve import solve_unobtanium_requirements

    # Inverse pass: allow knobs to move (not proof-mode plant for gap quantification)
    import os

    os.environ.pop("ORBITRON_PROOF_CHAIN", None)
    report = solve_unobtanium_requirements(inp, target_mw=target)

    u = report.inputs.unobtanium
    save_step(
        "09",
        {
            "success": report.success,
            "message": report.message,
            "residual_mw": report.residual_mw,
            "target_mw": target,
            "unobtanium_required": {
                "fusion_reactivity_scale": u.fusion_reactivity_scale,
                "field_emission_margin": u.field_emission_margin,
                "max_wall_heat_flux_W_m2": u.max_wall_heat_flux_W_m2,
                "ch4_cooling_effectiveness": u.ch4_cooling_effectiveness,
                "hts_capability_scale": u.hts_capability_scale,
                "beam_coupling_scale": u.beam_coupling_scale,
            },
            "pad": {
                "throttle": report.inputs.pad.throttle,
                "compressor": report.inputs.pad.compressor,
            },
            "steady_state": steady_to_dict(report.result),
            "spec_checks": validation_checks_to_dict(report.validation)
            if report.validation
            else [],
        },
    )
    print(f"solve success={report.success} residual_mw={report.residual_mw:.4f}")
    return 0 if report.success else 2


if __name__ == "__main__":
    raise SystemExit(main())
