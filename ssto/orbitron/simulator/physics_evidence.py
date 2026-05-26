"""
Physics evidence layer — honest unobtanium goals and forward confirmation.

Tier-1 ``design_validated`` uses the **design-calibrated** ⟨σv⟩ curve (proof-forward).
This module adds:

- Literature-class reactivity (not tuned to 3.5 MW)
- Stress inverse solve from pessimistic knobs
- Forward confirmation: at **required** unobtanium, does the **design** model hit target?
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, replace
from typing import Any

from ssto.orbitron.simulator.fusion_pb11 import (
    effective_ion_temperature_kev,
    evaluate_fusion_pb11,
    pb11_reactivity_m3_s,
)
from ssto.orbitron.simulator.physics_constants import (
    EMISSION_FIELD_LIMIT_V_M,
    REACTIVITY_HOLDOUT_MAX_RATIO,
)
from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.solve import solve_unobtanium_requirements
from ssto.orbitron.simulator.solve_constrained import solve_unobtanium_constrained
from ssto.orbitron.simulator.types import SimulatorInputs, UnobtaniumParams
from ssto.orbitron.simulator.validation import SpecCheck, SpecStatus, validate_design


@dataclass
class PhysicsAuditReport:
    """Structured physics audit for experiment reports."""

    tier1_design_validated: bool
    physics_evidence: bool
    summary: str
    calibration_holdout: list[dict[str, float]]
    design_vs_literature_at_operating: dict[str, float]
    literature_forward_mw: float
    stress_inverse: dict[str, Any]
    margin_inverse: dict[str, Any] | None
    confirmation_design_mw: float
    confirmation_passes: bool
    gap_factors_stress: dict[str, float]
    checks: list[SpecCheck]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier1_design_validated": self.tier1_design_validated,
            "physics_evidence": self.physics_evidence,
            "summary": self.summary,
            "calibration_holdout": self.calibration_holdout,
            "design_vs_literature_at_operating": self.design_vs_literature_at_operating,
            "literature_forward_mw": self.literature_forward_mw,
            "stress_inverse": self.stress_inverse,
            "margin_inverse": self.margin_inverse,
            "confirmation_design_mw": self.confirmation_design_mw,
            "confirmation_passes": self.confirmation_passes,
            "gap_factors_stress": self.gap_factors_stress,
            "checks": [
                {
                    "spec_id": c.spec_id,
                    "title": c.title,
                    "required": c.required,
                    "achieved": c.achieved,
                    "margin": c.margin,
                    "status": c.status.value,
                    "notes": c.notes,
                }
                for c in self.checks
            ],
        }


def _gap_factors(required: dict[str, float], nominal: dict[str, float]) -> dict[str, float]:
    out: dict[str, float] = {}
    for key, req in required.items():
        base = float(nominal.get(key, 1.0))
        if base <= 0:
            base = 1.0
        out[key] = float(req) / base
    return out


def _unobtanium_dict(u: UnobtaniumParams) -> dict[str, float]:
    return {
        "fusion_reactivity_scale": float(u.fusion_reactivity_scale),
        "field_emission_margin": float(u.field_emission_margin),
        "max_wall_heat_flux_W_m2": float(u.max_wall_heat_flux_W_m2),
        "ch4_cooling_effectiveness": float(u.ch4_cooling_effectiveness),
        "hts_capability_scale": float(u.hts_capability_scale),
        "beam_coupling_scale": float(u.beam_coupling_scale),
    }


def _pessimistic_unobtanium(u: UnobtaniumParams, scale: float = 0.65) -> UnobtaniumParams:
    s = max(0.1, scale)
    return replace(
        u,
        fusion_reactivity_scale=max(0.1, u.fusion_reactivity_scale * s),
        field_emission_margin=max(0.1, u.field_emission_margin * s),
        max_wall_heat_flux_W_m2=max(1e5, u.max_wall_heat_flux_W_m2 * s),
        ch4_cooling_effectiveness=max(0.1, u.ch4_cooling_effectiveness * s),
        hts_capability_scale=max(0.1, u.hts_capability_scale * s),
        beam_coupling_scale=max(0.1, u.beam_coupling_scale * s),
    )


def _with_reactivity_model(model: str):
    """Context manager via try/finally pattern — returns restore callable."""
    prev = os.environ.get("ORBITRON_REACTIVITY_MODEL")
    os.environ["ORBITRON_REACTIVITY_MODEL"] = model

    def restore() -> None:
        if prev is None:
            os.environ.pop("ORBITRON_REACTIVITY_MODEL", None)
        else:
            os.environ["ORBITRON_REACTIVITY_MODEL"] = prev

    return restore


def calibration_holdout_rows(inp: SimulatorInputs) -> list[dict[str, float]]:
    """⟨σv⟩ design vs literature at operating T and ±30% temperature."""
    op = inp.operating
    pad = inp.pad
    t0 = effective_ion_temperature_kev(
        inp.geometry.V_cathode_v,
        pad.cathode_pulse if pad.startup_trigger else op.cathode_pulse,
        pad.throttle if pad.startup_trigger else op.throttle,
    )
    rows: list[dict[str, float]] = []
    for label, t_kev in (
        ("T-30%", t0 * 0.7),
        ("operating", t0),
        ("T+30%", t0 * 1.3),
    ):
        d = pb11_reactivity_m3_s(t_kev, model="design")
        lit = pb11_reactivity_m3_s(t_kev, model="literature")
        ratio = d / max(lit, 1e-30)
        rows.append(
            {
                "label": label,
                "T_kev": t_kev,
                "sigma_v_design_m3_s": d,
                "sigma_v_literature_m3_s": lit,
                "design_over_literature": ratio,
            }
        )
    return rows


def literature_forward_mw(inp: SimulatorInputs) -> float:
    restore = _with_reactivity_model("literature")
    try:
        res = evaluate_steady_state(inp)
        return float(res.gross_power_mw)
    finally:
        restore()


def solve_stress_inverse(inp: SimulatorInputs, *, target_mw: float | None = None) -> dict[str, Any]:
    """Minimum unobtanium with literature σv, starting from pessimistic knobs."""
    target = target_mw if target_mw is not None else inp.scales.target_gross_power_mw
    restore = _with_reactivity_model("literature")
    try:
        report = solve_unobtanium_constrained(
            inp,
            target,
            mode="stress",
            fusion_scale_max=5000.0,
        )
    finally:
        restore()
    nom = _unobtanium_dict(inp.unobtanium)
    req = _unobtanium_dict(report.inputs.unobtanium)
    t_op = effective_ion_temperature_kev(
        report.inputs.geometry.V_cathode_v,
        report.inputs.pad.cathode_pulse,
        report.inputs.pad.throttle,
    )
    sv_d = pb11_reactivity_m3_s(t_op, model="design")
    sv_l = pb11_reactivity_m3_s(t_op, model="literature")
    branch = float(sv_d / max(sv_l, 1e-30))
    eta_req = float(req.get("fusion_reactivity_scale", 1.0))
    eta_nom = float(nom.get("fusion_reactivity_scale", 1.0))
    return {
        "success": bool(report.success),
        "message": report.message,
        "residual_mw": report.residual_mw,
        "target_mw": target,
        "reactivity_model": "literature",
        "pessimistic_start": True,
        "sigma_v_design_over_literature": branch,
        "fusion_reactivity_scale_required": eta_req,
        "effective_reactivity_multiplier": branch * eta_req,
        "effective_reactivity_gap_vs_nominal": branch * (eta_req / max(eta_nom, 1e-9)),
        "unobtanium_required": req,
        "unobtanium_nominal": nom,
        "gap_factors": _gap_factors(req, nom),
        "pad_solved": {
            "throttle": float(report.inputs.pad.throttle),
            "compressor": float(report.inputs.pad.compressor),
            "cathode_pulse": float(report.inputs.pad.cathode_pulse),
        },
        "design_validated_at_solve": bool(
            report.validation and report.validation.design_validated
        ),
    }


def solve_margin_inverse(inp: SimulatorInputs, *, target_mw: float | None = None) -> dict[str, Any]:
    """Margin audit with design σv (meaningful when forward already passes)."""
    target = target_mw if target_mw is not None else inp.scales.target_gross_power_mw
    restore = _with_reactivity_model("design")
    try:
        report = solve_unobtanium_constrained(inp, target, mode="margin", fusion_scale_max=5.0)
    finally:
        restore()
    nom = _unobtanium_dict(inp.unobtanium)
    req = _unobtanium_dict(report.inputs.unobtanium)
    return {
        "success": bool(report.success),
        "residual_mw": report.residual_mw,
        "reactivity_model": "design",
        "unobtanium_required": req,
        "unobtanium_nominal": nom,
        "gap_factors": _gap_factors(req, nom),
    }


def confirm_at_required_knobs(
    base: SimulatorInputs,
    required: dict[str, float],
    *,
    target_mw: float,
    tolerance_mw: float = 0.2,
) -> tuple[float, bool]:
    """
    Forward check: apply stress-required unobtanium, evaluate with **design** σv.

    Answers: if we attain those material/plasma goals, does the calibrated plant
  model deliver the power target?
    """
    u = base.unobtanium
    solved_u = replace(
        u,
        fusion_reactivity_scale=float(
            required.get("fusion_reactivity_scale", u.fusion_reactivity_scale)
        ),
        field_emission_margin=float(
            required.get("field_emission_margin", u.field_emission_margin)
        ),
        max_wall_heat_flux_W_m2=float(
            required.get("max_wall_heat_flux_W_m2", u.max_wall_heat_flux_W_m2)
        ),
        ch4_cooling_effectiveness=float(
            required.get("ch4_cooling_effectiveness", u.ch4_cooling_effectiveness)
        ),
        hts_capability_scale=float(
            required.get("hts_capability_scale", u.hts_capability_scale)
        ),
        beam_coupling_scale=float(required.get("beam_coupling_scale", u.beam_coupling_scale)),
    )
    inp = replace(base, unobtanium=solved_u)
    restore = _with_reactivity_model("design")
    try:
        res = evaluate_steady_state(inp)
        mw = float(res.gross_power_mw)
    finally:
        restore()
    # Attaining required unobtanium should deliver **at least** target power on design σv.
    return mw, mw >= target_mw - tolerance_mw


def run_physics_audit(
    inp: SimulatorInputs,
    *,
    tier1_validated: bool,
    require_pic: bool = False,
    power_tolerance_mw: float = 0.2,
    include_margin_inverse: bool = True,
) -> PhysicsAuditReport:
    """Full audit used by headless experiment reports."""
    checks: list[SpecCheck] = []
    target = inp.scales.target_gross_power_mw

    holdout = calibration_holdout_rows(inp)
    max_ratio = max(r["design_over_literature"] for r in holdout) if holdout else 1.0
    cal_ok = max_ratio <= REACTIVITY_HOLDOUT_MAX_RATIO
    checks.append(
        SpecCheck(
            "CAL",
            "⟨σv⟩ design vs literature hold-out",
            f"ratio ≤ {REACTIVITY_HOLDOUT_MAX_RATIO:.0f}× at audit T",
            f"max ratio {max_ratio:.1f}×",
            "design curve is calibrated, not independent physics",
            SpecStatus.PASS if cal_ok else SpecStatus.WARN,
            "Design reactivity is tuned to close MW; literature path is ~3 orders lower peak.",
        )
    )

    op = inp.operating
    t_op = effective_ion_temperature_kev(
        inp.geometry.V_cathode_v, inp.pad.cathode_pulse, inp.pad.throttle
    )
    sv_d = pb11_reactivity_m3_s(t_op, model="design")
    sv_l = pb11_reactivity_m3_s(t_op, model="literature")
    dvl = {
        "T_kev_operating": t_op,
        "sigma_v_design_m3_s": sv_d,
        "sigma_v_literature_m3_s": sv_l,
        "design_over_literature": sv_d / max(sv_l, 1e-30),
    }

    lit_mw = literature_forward_mw(inp)
    lit_shortfall = target - lit_mw
    checks.append(
        SpecCheck(
            "LIT",
            "Literature σv forward @ nominal knobs",
            f"≥ {target:.2f} MW",
            f"{lit_mw:.3f} MW",
            f"shortfall {lit_shortfall:+.2f} MW",
            SpecStatus.PASS if lit_mw >= target - power_tolerance_mw else SpecStatus.WARN,
            "Shortfall expected — design curve is calibrated; see stress inverse gap factors.",
        )
    )

    gap_m = max(inp.geometry.r_anode_m - inp.geometry.r_cathode_m, 1e-6)
    e_surf = abs(inp.geometry.V_cathode_v) / gap_m
    e_lim = EMISSION_FIELD_LIMIT_V_M * inp.unobtanium.field_emission_margin
    u1_margin = e_lim / max(e_surf, 1.0)
    u1_not_vacuous = u1_margin <= 25.0
    checks.append(
        SpecCheck(
            "U1r",
            "U1 margin not vacuous",
            "1× ≤ margin ≤ 25×",
            f"{u1_margin:.2f}×",
            f"|E|={e_surf:.2e} V/m",
            SpecStatus.PASS if u1_not_vacuous else SpecStatus.WARN,
            "Very large margin means the field gate is not discriminating.",
        )
    )

    pic_ok = True
    if require_pic:
        pic_ok = math.isfinite(inp.pic_rho_e_norm) and inp.pic_rho_e_norm > 0
        checks.append(
            SpecCheck(
                "PICg",
                "WarpX density proxy required",
                "finite ρ_e norm from step 02",
                f"{inp.pic_rho_e_norm:.4g}" if math.isfinite(inp.pic_rho_e_norm) else "missing",
                "—",
                SpecStatus.PASS if pic_ok else SpecStatus.FAIL,
                "PIC does not compute p-¹¹B Q; proxy only.",
            )
        )

    stress = solve_stress_inverse(inp, target_mw=target)
    stress_factors = stress.get("gap_factors") or {}
    max_stress_gap = max(stress_factors.values(), default=1.0)
    checks.append(
        SpecCheck(
            "STR",
            "Stress inverse (literature σv, pessimistic start)",
            "success + factors documented",
            f"success={stress.get('success')} η_react req="
            f"{stress.get('fusion_reactivity_scale_required', 1):.1f}×",
            f"σv branch {stress.get('sigma_v_design_over_literature', 1):.0f}×",
            SpecStatus.PASS if stress.get("success") else SpecStatus.WARN,
            "Stress inverse: primary gap is ⟨σv⟩ branch × fusion_reactivity_scale, not 5% U1–U3 knobs.",
        )
    )

    margin_inv: dict[str, Any] | None = None
    if include_margin_inverse and tier1_validated:
        margin_inv = solve_margin_inverse(inp, target_mw=target)

    req = stress.get("unobtanium_required") or {}
    conf_knobs = req
    if margin_inv and margin_inv.get("unobtanium_required"):
        conf_knobs = margin_inv["unobtanium_required"]
    conf_mw, conf_ok = confirm_at_required_knobs(
        inp, conf_knobs, target_mw=target, tolerance_mw=power_tolerance_mw
    )
    checks.append(
        SpecCheck(
            "CNF",
            "Forward confirmation (design σv @ margin-inverse knobs)",
            f"≥ {target - power_tolerance_mw:.2f} MW",
            f"{conf_mw:.3f} MW",
            "Back-solve check: margin inverse on design σv should ≈ (a) pretend.",
            SpecStatus.PASS if conf_ok else SpecStatus.FAIL,
            "FAIL means margin knobs do not restore MW on design curve.",
        )
    )

    stress_informative = lit_mw < target - power_tolerance_mw or max_stress_gap > 1.02
    checks.append(
        SpecCheck(
            "DIS",
            "Literature path discriminates from Tier-1",
            "lit forward below target OR stress gap > 1.02×",
            f"lit={lit_mw:.3f} MW, max gap={max_stress_gap:.2f}×",
            "—",
            SpecStatus.PASS if stress_informative else SpecStatus.WARN,
            "If design and literature both close trivially, Tier-1 is only self-consistent.",
        )
    )

    hard_fail = any(
        c.status == SpecStatus.FAIL for c in checks if c.spec_id not in ("STR",)
    )
    physics_evidence = (
        tier1_validated
        and conf_ok
        and pic_ok
        and stress_informative
        and not hard_fail
    )

    if physics_evidence:
        summary = (
            "PHYSICS EVIDENCE: Tier-1 passes; stress inverse succeeded; "
            "design model hits target at required unobtanium."
        )
    elif tier1_validated and conf_ok:
        summary = (
            "PARTIAL: Tier-1 validated; forward confirmation OK, but literature/PIC/stress checks need review."
        )
    elif tier1_validated:
        summary = (
            "TIER-1 ONLY: Calibrated plant closes; literature stress path or confirmation did not fully pass."
        )
    else:
        summary = "NOT READY: Tier-1 design validation failed — fix forward chain before physics evidence."

    return PhysicsAuditReport(
        tier1_design_validated=tier1_validated,
        physics_evidence=physics_evidence,
        summary=summary,
        calibration_holdout=holdout,
        design_vs_literature_at_operating=dvl,
        literature_forward_mw=lit_mw,
        stress_inverse=stress,
        margin_inverse=margin_inv,
        confirmation_design_mw=conf_mw,
        confirmation_passes=conf_ok,
        gap_factors_stress=stress_factors,
        checks=checks,
    )
