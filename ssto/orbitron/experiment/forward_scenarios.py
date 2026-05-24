"""Forward plant performance for named unobtanium scenarios (not inverse solve)."""
from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.types import SimulatorInputs, UnobtaniumParams
from ssto.orbitron.simulator.validation import validate_design

_SCENARIOS_YAML = Path(__file__).resolve().parents[1] / "unobtanium_scenarios.yaml"


def load_scenario_catalog(path: Path | None = None) -> dict[str, Any]:
    p = path or _SCENARIOS_YAML
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return dict((data or {}).get("scenarios") or {})


def _apply_knobs(inp: SimulatorInputs, knobs: dict[str, float]) -> SimulatorInputs:
    u = inp.unobtanium
    return replace(
        inp,
        unobtanium=UnobtaniumParams(
            fusion_reactivity_scale=float(
                knobs.get("fusion_reactivity_scale", u.fusion_reactivity_scale)
            ),
            field_emission_margin=float(
                knobs.get("field_emission_margin", u.field_emission_margin)
            ),
            max_wall_heat_flux_W_m2=float(
                knobs.get("max_wall_heat_flux_W_m2", u.max_wall_heat_flux_W_m2)
            ),
            ch4_cooling_effectiveness=float(
                knobs.get("ch4_cooling_effectiveness", u.ch4_cooling_effectiveness)
            ),
            hts_capability_scale=float(
                knobs.get("hts_capability_scale", u.hts_capability_scale)
            ),
            beam_coupling_scale=float(knobs.get("beam_coupling_scale", u.beam_coupling_scale)),
        ),
    )


def evaluate_forward_scenarios(
    inp: SimulatorInputs,
    *,
    experiment_unobtanium: dict[str, float] | None = None,
    stress_required: dict[str, float] | None = None,
    catalog_path: Path | None = None,
) -> dict[str, Any]:
    """
    Forward-evaluate unobtanium scenarios with **design** ⟨σv⟩ (predicted rig performance).

    Also records literature-σv MW @ nominal for contrast (one row).
    """
    catalog = load_scenario_catalog(catalog_path)
    scenarios_out: list[dict[str, Any]] = []

    # Merge experiment nominal into catalog copy
    if experiment_unobtanium:
        cat_nom = catalog.get("nominal", {})
        knobs = dict((cat_nom.get("knobs") or {}))
        knobs.update(experiment_unobtanium)
        catalog = dict(catalog)
        catalog["nominal"] = {**cat_nom, "knobs": knobs}

    if stress_required:
        catalog = dict(catalog)
        catalog["stress_inverse_minimum"] = {
            "label": "Stress inverse minimum (literature σv solve)",
            "description": (
                "Optimizer output: minimum knobs that pass U1–U4 while hitting target MW "
                "under literature-class reactivity. Use with forward confirmation (design σv)."
            ),
            "knobs": stress_required,
        }

    os.environ["ORBITRON_REACTIVITY_MODEL"] = "design"
    try:
        for key, spec in catalog.items():
            knobs = dict(spec.get("knobs") or {})
            eval_inp = _apply_knobs(inp, knobs)
            res = evaluate_steady_state(eval_inp)
            vrep = validate_design(eval_inp, res)
            scenarios_out.append(
                {
                    "id": key,
                    "label": spec.get("label", key),
                    "description": (spec.get("description") or "").strip(),
                    "knobs": knobs,
                    "gross_power_mw": float(res.gross_power_mw),
                    "fusion_physics_mw": float(res.fusion_power_mw_physics),
                    "design_validated": bool(vrep.design_validated),
                    "power_residual_mw": float(vrep.power_residual_mw),
                    "feasible": bool(res.feasible),
                    "violations": list(res.violations),
                }
            )
    finally:
        os.environ.pop("ORBITRON_REACTIVITY_MODEL", None)

  # Literature contrast at experiment nominal only
    os.environ["ORBITRON_REACTIVITY_MODEL"] = "literature"
    try:
        lit_res = evaluate_steady_state(inp)
    finally:
        os.environ.pop("ORBITRON_REACTIVITY_MODEL", None)

    return {
        "target_mw": float(inp.scales.target_gross_power_mw),
        "literature_forward_nominal_mw": float(lit_res.gross_power_mw),
        "scenarios": scenarios_out,
        "interpretation": (
            "Scenarios use design-calibrated reactivity (predicted rig performance if knobs are achieved). "
            "literature_forward_nominal_mw shows the same fuel/geometry with honest σv — typically far below target."
        ),
    }


def scenarios_table_md(payload: dict[str, Any]) -> str:
    lines = [
        "| Scenario | η_react | E-margin | q_wall [MW/m²] | P_gross [MW] | Tier-1 valid |",
        "|----------|---------|----------|----------------|--------------|--------------|",
    ]
    for row in payload.get("scenarios") or []:
        k = row.get("knobs") or {}
        q = float(k.get("max_wall_heat_flux_W_m2", 0)) / 1e6
        lines.append(
            f"| {row.get('label', row.get('id'))} | "
            f"{k.get('fusion_reactivity_scale', '—')} | "
            f"{k.get('field_emission_margin', '—')} | "
            f"{q:.2f} | "
            f"{row.get('gross_power_mw', 0):.3f} | "
            f"{row.get('design_validated')} |"
        )
    lit = payload.get("literature_forward_nominal_mw")
    tgt = payload.get("target_mw")
    lines.append(
        f"\n*Literature σv @ nominal knobs (honest reactivity): **{lit:.4f} MW** "
        f"(target {tgt} MW).*\n"
    )
    return "\n".join(lines) + "\n"
