"""Three-scenario benchmark evaluation per BENCHMARK_METHODOLOGY.md."""
from __future__ import annotations

import math
import os
from dataclasses import replace
from pathlib import Path
from typing import Any, Literal

import yaml

from ssto.orbitron.simulator.fusion_pb11 import (
    effective_ion_temperature_kev,
    pb11_reactivity_m3_s,
)
from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.types import SimulatorInputs, UnobtaniumParams
from ssto.orbitron.simulator.validation import validate_design

_ANCHORS_YAML = Path(__file__).resolve().parents[1] / "scenario_anchors.yaml"
ReactivityModel = Literal["design", "literature"]


def load_scenario_anchors(path: Path | None = None) -> dict[str, Any]:
    p = path or _ANCHORS_YAML
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return dict((data or {}).get("scenarios") or {})


def _apply_scenario(
    base: SimulatorInputs,
    spec: dict[str, Any],
    *,
    knob_overrides: dict[str, float] | None = None,
) -> SimulatorInputs:
    geo = base.geometry
    g_over = dict(spec.get("geometry") or {})
    if g_over:
        geo = replace(
            geo,
            **{k: float(v) for k, v in g_over.items() if hasattr(geo, k)},
        )
    knobs = dict(spec.get("knobs") or {})
    if knob_overrides:
        knobs.update(knob_overrides)
    u = base.unobtanium
    if knobs:
        u = UnobtaniumParams(
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
        )
    return replace(base, geometry=geo, unobtanium=u)


def _sigma_v_branch_ratio(inp: SimulatorInputs) -> float:
    pad = inp.pad
    t_kev = effective_ion_temperature_kev(
        inp.geometry.V_cathode_v,
        pad.cathode_pulse if pad.startup_trigger else inp.operating.cathode_pulse,
        pad.throttle if pad.startup_trigger else inp.operating.throttle,
    )
    d = pb11_reactivity_m3_s(t_kev, model="design")
    lit = pb11_reactivity_m3_s(t_kev, model="literature")
    return float(d / max(lit, 1e-30))


def _evaluate_one(
    inp: SimulatorInputs,
    *,
    scenario_id: str,
    label: str,
    description: str,
    reactivity_model: ReactivityModel,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    os.environ["ORBITRON_REACTIVITY_MODEL"] = reactivity_model
    try:
        res = evaluate_steady_state(inp)
        vrep = validate_design(inp, res)
    finally:
        os.environ.pop("ORBITRON_REACTIVITY_MODEL", None)

    branch = _sigma_v_branch_ratio(inp)
    eta = float(inp.unobtanium.fusion_reactivity_scale)
    combined = branch * eta

    return {
        "id": scenario_id,
        "label": label,
        "description": (description or "").strip(),
        "reactivity_model": reactivity_model,
        "geometry": {
            "V_cathode_v": float(inp.geometry.V_cathode_v),
            "B_axial_tesla": float(inp.geometry.B_axial_tesla),
            "r_anode_m": float(inp.geometry.r_anode_m),
        },
        "knobs": {
            "fusion_reactivity_scale": float(inp.unobtanium.fusion_reactivity_scale),
            "field_emission_margin": float(inp.unobtanium.field_emission_margin),
            "max_wall_heat_flux_W_m2": float(inp.unobtanium.max_wall_heat_flux_W_m2),
            "ch4_cooling_effectiveness": float(inp.unobtanium.ch4_cooling_effectiveness),
            "hts_capability_scale": float(inp.unobtanium.hts_capability_scale),
            "beam_coupling_scale": float(inp.unobtanium.beam_coupling_scale),
        },
        "gross_power_mw": float(res.gross_power_mw),
        "fusion_physics_mw": float(res.fusion_power_mw_physics),
        "design_validated": bool(vrep.design_validated),
        "power_residual_mw": float(vrep.power_residual_mw),
        "feasible": bool(res.feasible),
        "violations": list(res.violations),
        "sigma_v_design_over_literature": branch,
        "effective_reactivity_multiplier": combined,
        "provenance": provenance or {},
    }


def evaluate_benchmark_scenarios(
    inp: SimulatorInputs,
    *,
    stress_required: dict[str, float] | None = None,
    stress_geometry: dict[str, float] | None = None,
    stress_infeasible: bool = False,
    margin_required: dict[str, float] | None = None,
    anchors_path: Path | None = None,
) -> dict[str, Any]:
    """
    Evaluate (a) pretend, (b) today, (c) minimum per BENCHMARK_METHODOLOGY.md.

    ``margin_required`` optional row: margin inverse @ design σv (back-solve ≈ pretend check).
    """
    catalog = load_scenario_anchors(anchors_path)
    target = float(inp.scales.target_gross_power_mw)
    rows: list[dict[str, Any]] = []

    pretend_spec = catalog.get("pretend", {})
    pretend_inp = _apply_scenario(inp, pretend_spec)
    rows.append(
        _evaluate_one(
            pretend_inp,
            scenario_id="pretend",
            label=str(pretend_spec.get("label", "(a) Pretend")),
            description=str(pretend_spec.get("description", "")),
            reactivity_model="design",
            provenance=dict(pretend_spec.get("provenance") or {}),
        )
    )

    today_spec = catalog.get("today", {})
    today_inp = _apply_scenario(inp, today_spec)
    rows.append(
        _evaluate_one(
            today_inp,
            scenario_id="today",
            label=str(today_spec.get("label", "(b) Today")),
            description=str(today_spec.get("description", "")),
            reactivity_model="literature",
            provenance=dict(today_spec.get("provenance") or {}),
        )
    )

    if stress_required is not None:
        min_spec = catalog.get("minimum", {})
        geo_over = dict(stress_geometry or {})
        infeasible = bool(stress_infeasible)
        if infeasible:
            rows.append(
                {
                    "id": "minimum",
                    "label": str(min_spec.get("label", "(c) Minimum")),
                    "description": (
                        "No literature-σv operating point meets **3.5 MW** and **U1–U4** "
                        "simultaneously. Values below are the constrained optimizer’s best "
                        "effort — not a validated solution."
                    ),
                    "reactivity_model": "literature",
                    "geometry": geo_over or {
                        "V_cathode_v": float(inp.geometry.V_cathode_v),
                        "B_axial_tesla": float(inp.geometry.B_axial_tesla),
                    },
                    "knobs": dict(stress_required),
                    "gross_power_mw": float("nan"),
                    "fusion_physics_mw": float("nan"),
                    "design_validated": False,
                    "power_residual_mw": float("nan"),
                    "feasible": False,
                    "violations": ["INFEASIBLE under literature σv + U1–U4"],
                    "sigma_v_design_over_literature": _sigma_v_branch_ratio(inp),
                    "effective_reactivity_multiplier": float("nan"),
                    "provenance": {"solver": "constrained stress inverse — infeasible"},
                    "infeasible": True,
                }
            )
        else:
            min_inp = _apply_scenario(
                inp,
                {**min_spec, "geometry": geo_over, "knobs": stress_required},
                knob_overrides=stress_required,
            )
            rows.append(
                _evaluate_one(
                    min_inp,
                    scenario_id="minimum",
                    label=str(min_spec.get("label", "(c) Minimum")),
                    description=str(
                        min_spec.get(
                            "description",
                            "Constrained stress inverse (literature σv, U1–U4 satisfied).",
                        )
                    ),
                    reactivity_model="literature",
                    provenance={
                        **dict(min_spec.get("provenance") or {}),
                        "solver": "constrained stress inverse step 09",
                    },
                )
            )

    margin_row: dict[str, Any] | None = None
    if margin_required:
        margin_inp = _apply_scenario(inp, pretend_spec, knob_overrides=margin_required)
        margin_row = _evaluate_one(
            margin_inp,
            scenario_id="margin_inverse",
            label="Margin inverse @ design σv (back-solve check)",
            description="Required knobs from margin inverse with design σv — should ≈ (a).",
            reactivity_model="design",
        )

    pretend_mw = rows[0]["gross_power_mw"] if rows else 0.0
    today_mw = rows[1]["gross_power_mw"] if len(rows) > 1 else 0.0

    return {
        "target_mw": target,
        "scenarios": rows,
        "margin_inverse_row": margin_row,
        "pretend_mw": pretend_mw,
        "today_mw": today_mw,
        "today_shortfall_mw": target - today_mw,
        "sigma_v_branch_at_design_V": _sigma_v_branch_ratio(pretend_inp),
        "interpretation": (
            "(a) calibrated design closure; (b) literature σv + experimental anchors; "
            "(c) minimum literature-σv knobs from stress inverse. "
            "Dominant gap is usually σv_design/σv_literature (~10³×), not 5% material knobs."
        ),
    }


def benchmark_scenarios_table_md(payload: dict[str, Any]) -> str:
    """Markdown comparison table for REPORT.md."""
    tgt = payload.get("target_mw", 3.5)
    lines = [
        "## Three-scenario benchmark\n\n",
        f"Target gross power **{tgt:g} MW**.\n\n",
        "| Scenario | σv | V_cathode | η_react scale | Reactivity gap vs lit. | P_gross [MW] | Level-1 gates |\n",
        "|----------|-----|-----------|---------------|-------------------------|--------------|--------------|\n",
    ]
    for row in payload.get("scenarios") or []:
        geo = row.get("geometry") or {}
        k = row.get("knobs") or {}
        v_kv = abs(float(geo.get("V_cathode_v", 0))) / 1000.0
        branch = float(row.get("sigma_v_design_over_literature", 1.0))
        eta = float(k.get("fusion_reactivity_scale", 1.0))
        if row.get("infeasible"):
            gap_col = "— (infeasible)"
            p_str = "—"
        elif row.get("reactivity_model") == "literature":
            gap_col = f"{branch * eta:.2g}× (branch×η)"
            pg = row.get("gross_power_mw", 0)
            p_str = f"{pg:.3f}" if isinstance(pg, (int, float)) and math.isfinite(pg) else "—"
        else:
            gap_col = f"branch {branch:.2g}× @ η=1"
            pg = row.get("gross_power_mw", 0)
            p_str = f"{pg:.3f}" if isinstance(pg, (int, float)) else "—"
        lines.append(
            f"| {row.get('label', row.get('id'))} | "
            f"{row.get('reactivity_model', '—')} | "
            f"{v_kv:.0f} kV | "
            f"{eta:.3g}× | "
            f"{gap_col} | "
            f"{p_str} | "
            f"{row.get('design_validated')} |\n"
        )
    mi = payload.get("margin_inverse_row")
    if mi:
        geo = mi.get("geometry") or {}
        k = mi.get("knobs") or {}
        v_kv = abs(float(geo.get("V_cathode_v", 0))) / 1000.0
        eta = float(k.get("fusion_reactivity_scale", 1.0))
        lines.append(
            f"| {mi.get('label', 'margin')} | "
            f"design | "
            f"{v_kv:.0f} kV | "
            f"{eta:.3g}× | "
            f"back-solve vs (a) | "
            f"{mi.get('gross_power_mw', 0):.3f} | "
            f"{mi.get('design_validated')} |\n"
        )
    today = payload.get("today_mw")
    short = payload.get("today_shortfall_mw")
    branch = payload.get("sigma_v_branch_at_design_V")
    lines.append(
        f"\n*(b) today forward: **{today:.4f} MW** (shortfall **{short:+.2f} MW** vs target). "
        f"At (a) voltage, design/literature ⟨σv⟩ branch ≈ **{branch:.1f}×**.*\n\n"
    )
    return "".join(lines)
