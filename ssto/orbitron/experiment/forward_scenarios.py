"""Forward benchmark scenarios — delegates to benchmark_scenarios (a/b/c)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ssto.orbitron.experiment.benchmark_scenarios import (
    benchmark_scenarios_table_md,
    evaluate_benchmark_scenarios,
    load_scenario_anchors,
)
from ssto.orbitron.simulator.types import SimulatorInputs

# Back-compat alias
load_scenario_catalog = load_scenario_anchors
scenarios_table_md = benchmark_scenarios_table_md


def evaluate_forward_scenarios(
    inp: SimulatorInputs,
    *,
    experiment_unobtanium: dict[str, float] | None = None,
    stress_required: dict[str, float] | None = None,
    stress_infeasible: bool = False,
    margin_required: dict[str, float] | None = None,
    catalog_path: Path | None = None,
) -> dict[str, Any]:
    """Evaluate (a) pretend, (b) today, (c) minimum per BENCHMARK_METHODOLOGY.md."""
    if experiment_unobtanium:
        from dataclasses import replace

        from ssto.orbitron.simulator.types import UnobtaniumParams

        u = inp.unobtanium
        inp = replace(
            inp,
            unobtanium=UnobtaniumParams(
                fusion_reactivity_scale=float(
                    experiment_unobtanium.get("fusion_reactivity_scale", u.fusion_reactivity_scale)
                ),
                field_emission_margin=float(
                    experiment_unobtanium.get("field_emission_margin", u.field_emission_margin)
                ),
                max_wall_heat_flux_W_m2=float(
                    experiment_unobtanium.get(
                        "max_wall_heat_flux_W_m2", u.max_wall_heat_flux_W_m2
                    )
                ),
                ch4_cooling_effectiveness=float(
                    experiment_unobtanium.get(
                        "ch4_cooling_effectiveness", u.ch4_cooling_effectiveness
                    )
                ),
                hts_capability_scale=float(
                    experiment_unobtanium.get("hts_capability_scale", u.hts_capability_scale)
                ),
                beam_coupling_scale=float(
                    experiment_unobtanium.get("beam_coupling_scale", u.beam_coupling_scale)
                ),
            ),
        )
    payload = evaluate_benchmark_scenarios(
        inp,
        stress_required=stress_required,
        stress_infeasible=stress_infeasible,
        margin_required=margin_required,
        anchors_path=catalog_path,
    )
    # Legacy key for audit rows
    today_mw = float(payload.get("today_mw", 0.0))
    payload["literature_forward_nominal_mw"] = today_mw
    return payload
