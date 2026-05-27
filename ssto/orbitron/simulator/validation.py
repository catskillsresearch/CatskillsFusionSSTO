"""
Design validation — quantify unobtanium specs and check 3.5 MW plant closure.

Fidelity (honest):
  - **0D plant** enforces U1–U4 *inequality* constraints and surrogate power bookkeeping.
  - **WarpX PIC** supplies density/beam *coupling proxies* — it does **not** integrate p-¹¹B fusion yield.
  - **Design validated** means: at your geometry + pad run point, all spec gates pass *and*
    gross power / thrust / mdot close the documented 0D jet identity within tolerance.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from ssto.orbitron.simulator.pad_startup import PadStartupStatus, evaluate_pad_status
from ssto.orbitron.simulator.physics_constants import (
    BEAM_CURRENT_MIN_MA,
    EMISSION_FIELD_LIMIT_V_M,
    LOG10_DENSITY_MIN,
)
from ssto.orbitron.simulator.types import SimulatorInputs, SteadyStateResult

LBF_TO_N = 4.4482216152605


class SpecStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    N_A = "n/a"
    WARN = "warn"


@dataclass(frozen=True)
class SpecCheck:
    """One quantified requirement vs model result."""

    spec_id: str
    title: str
    required: str
    achieved: str
    margin: str
    status: SpecStatus
    notes: str = ""


@dataclass
class DesignValidationReport:
    """Full validation snapshot for GUI / export."""

    checks: list[SpecCheck] = field(default_factory=list)
    design_validated: bool = False
    fusion_operating_point: bool = False
    power_target_mw: float = 3.5
    power_achieved_mw: float = 0.0
    power_residual_mw: float = 0.0
    jet_closure_rel_error: float = float("nan")
    pic_coupling_used: bool = False
    summary: str = ""

    def to_text(self) -> str:
        lines = [
            self.summary,
            "",
            f"Tier-1 design validated: {self.design_validated}",
            f"Physics evidence (strict): {self.physics_evidence}",
            f"Fusion run point (ignited + power): {self.fusion_operating_point}",
            f"P_gross: {self.power_achieved_mw:.3f} MW  (target {self.power_target_mw:.3f}, "
            f"Δ {self.power_residual_mw:+.3f} MW)",
            f"Jet closure rel. error: {self.jet_closure_rel_error:.3%}"
            if math.isfinite(self.jet_closure_rel_error)
            else "Jet closure: n/a (no flow)",
            "",
            "Spec checks:",
        ]
        for c in self.checks:
            mark = "✓" if c.status == SpecStatus.PASS else ("○" if c.status == SpecStatus.N_A else "✗")
            lines.append(f"  {mark} [{c.spec_id}] {c.title}")
            lines.append(f"      need {c.required}  |  have {c.achieved}  |  {c.margin}")
            if c.notes:
                lines.append(f"      {c.notes}")
        return "\n".join(lines)


def _jet_closure_rel_error(result: SteadyStateResult, eta_jet: float) -> float:
    """|P_jet - F²/(2ṁ)| / P_jet  using 0D outputs."""
    mdot = result.mass_flow_kgps
    if mdot < 1.0e-9:
        return float("nan")
    thrust_n = result.thrust_lbf * LBF_TO_N
    p_jet_w = eta_jet * result.gross_power_mw * 1.0e6
    p_from_thrust = (thrust_n * thrust_n) / (2.0 * mdot)
    if p_jet_w < 1.0:
        return float("nan")
    return abs(p_from_thrust - p_jet_w) / p_jet_w


def validate_design(
    inputs: SimulatorInputs,
    result: SteadyStateResult,
    *,
    power_tolerance_mw: float = 0.2,
    closure_tolerance: float = 0.12,
    run_fusion_channel: bool = True,
) -> DesignValidationReport:
    """Quantify U1–U4 and plant targets for the current operating point."""
    g = inputs.geometry
    u = inputs.unobtanium
    sc = inputs.scales
    pad_status = evaluate_pad_status(inputs.pad)
    armed = pad_status.reactor_armed

    fc_meta: dict = {}
    if armed and run_fusion_channel:
        from ssto.orbitron.simulator.longitudinal.focus import focus_domain, LongitudinalFocus
        from ssto.orbitron.simulator.longitudinal.fusion_channel_sr import (
            laminar_hack_from_inputs,
            run_fusion_channel_sr,
        )

        dom = focus_domain(LongitudinalFocus.FUSION_CHANNEL_SR, inputs)
        laminar = laminar_hack_from_inputs(
            inputs,
            force_off=not inputs.pad.laminar_relaminarization,
        )
        fc = run_fusion_channel_sr(dom, inputs, laminar=laminar, compare_without_hack=True)
        fc_meta = fc.meta
        from dataclasses import replace

        result = replace(
            result,
            fusion_channel_power_mw=fc.integrated_fusion_power_mw,
            clump_index=fc.clump_index_final,
            clump_reduction_ratio=fc.clump_reduction_ratio,
            laminar_hack_enabled=laminar.enabled,
            fusion_power_mw_physics=fc.integrated_fusion_power_mw,
        )

    pic_used = math.isfinite(inputs.pic_rho_e_norm) or math.isfinite(inputs.pic_beam_rho_norm)
    target_mw = sc.target_gross_power_mw
    res_mw = result.gross_power_mw - target_mw
    jerr = _jet_closure_rel_error(result, sc.jet_propulsive_efficiency)

    checks: list[SpecCheck] = []

    # --- Pad / startup gates ---
    checks.append(
        SpecCheck(
            "PAD",
            "Reactor armed (ignite)",
            "startup-trigger ON",
            "ON" if armed else "off",
            "—",
            SpecStatus.PASS if armed else SpecStatus.N_A,
            "Power/thrust specs apply only after bleed + ignite.",
        )
    )

    # --- U1 cathode field ---
    gap_m = max(g.r_anode_m - g.r_cathode_m, 1e-6)
    e_lim = EMISSION_FIELD_LIMIT_V_M * u.field_emission_margin
    e_ok = result.cathode_surface_field_V_m <= e_lim
    checks.append(
        SpecCheck(
            "U1",
            "Cathode surface field (no arc)",
            f"|E| ≤ {e_lim:.2e} V/m",
            f"{result.cathode_surface_field_V_m:.2e} V/m",
            f"margin {(e_lim / max(result.cathode_surface_field_V_m, 1)):.2f}×",
            SpecStatus.PASS if e_ok else SpecStatus.FAIL,
            f"Gap {gap_m*1e3:.1f} mm @ {abs(g.V_cathode_v)/1e3:.0f} kV "
            f"(program limit {EMISSION_FIELD_LIMIT_V_M:.1e} V/m @ margin 1). "
            "Margin scale >1 relaxes allowable |E|.",
        )
    )

    # --- U2 wall + CH4 ---
    q_allow = u.max_wall_heat_flux_W_m2 * u.ch4_cooling_effectiveness
    q_ok = result.wall_heat_flux_W_m2 <= q_allow
    checks.append(
        SpecCheck(
            "U2a",
            "Wall heat flux vs CH₄ loop",
            f"q ≤ {q_allow:.2e} W/m²",
            f"{result.wall_heat_flux_W_m2:.2e} W/m²",
            f"Q_wall = {result.wall_heat_kw:.1f} kW",
            SpecStatus.PASS if q_ok else SpecStatus.FAIL,
            "Raise max flux or CH₄ effectiveness if fail — sizes first-wall / cooler.",
        )
    )
    checks.append(
        SpecCheck(
            "U2b",
            "Wall load anchor (design)",
            f"~{sc.heat_kw_at_full:.0f} kW @ full",
            f"{result.wall_heat_kw:.1f} kW",
            f"{result.wall_heat_kw / max(sc.heat_kw_at_full, 1):.2f}× anchor",
            SpecStatus.PASS if result.wall_heat_kw <= sc.heat_kw_at_full * 1.25 else SpecStatus.WARN,
        )
    )

    # --- U3 magnet ---
    b_max = 2.0 * u.hts_capability_scale
    b_ok = g.B_axial_tesla <= b_max + 1e-3
    checks.append(
        SpecCheck(
            "U3",
            "HTS bore field capability",
            f"B ≤ {b_max:.2f} T",
            f"{g.B_axial_tesla:.2f} T",
            f"scale {u.hts_capability_scale:.2f}",
            SpecStatus.PASS if b_ok else SpecStatus.FAIL,
            "Scale <1 = weaker HTS tape / cryo budget than 2 T nominal.",
        )
    )

    # --- U4 fusion operating point ---
    beam_ok = result.beam_current_ma >= BEAM_CURRENT_MIN_MA or result.gross_power_mw < 0.5
    dens_ok = result.log10_density >= LOG10_DENSITY_MIN or result.gross_power_mw < 0.5
    checks.append(
        SpecCheck(
            "U4a",
            "Ion beam integration",
            f"≥ {BEAM_CURRENT_MIN_MA:.0f} mA @ meaningful power",
            f"{result.beam_current_ma:.2f} mA",
            f"P_beam = {result.beam_power_kw:.2f} kW",
            SpecStatus.PASS if beam_ok else SpecStatus.FAIL,
            "Beam coupling scale sizes extracted beam vs PIC proxy.",
        )
    )
    checks.append(
        SpecCheck(
            "U4b",
            "Plasma density (proxy)",
            f"log₁₀ n ≥ {LOG10_DENSITY_MIN:.0f} @ meaningful power",
            f"{result.log10_density:.2f}",
            f"{result.plasma_density_cm3:.2e} cm⁻³",
            SpecStatus.PASS if dens_ok else SpecStatus.FAIL,
            "PIC ρ_e norm overrides heuristic when WarpX has run.",
        )
    )
    checks.append(
        SpecCheck(
            "U4c",
            "Gross fusion-thermal power",
            f"{target_mw:.2f} MW ± {power_tolerance_mw:.2f}",
            f"{result.gross_power_mw:.3f} MW",
            f"reactivity scale {u.fusion_reactivity_scale:.3f}",
            SpecStatus.PASS
            if armed and abs(res_mw) <= power_tolerance_mw
            else (SpecStatus.N_A if not armed else SpecStatus.FAIL),
            "Blended p-¹¹B physics + surrogate map (see fusion_physics_pb11 in export YAML).",
        )
    )
    if armed and result.fusion_power_mw_physics > 0:
        checks.append(
            SpecCheck(
                "U4d",
                "p-¹¹B fusion model (reactivity × fueling)",
                f"> 0 MW physics path",
                f"{result.fusion_power_mw_physics:.3f} MW",
                f"<σv>={result.sigma_v_m3_s:.2e} m³/s @ {result.ion_temperature_kev:.0f} keV",
                SpecStatus.PASS,
                "¹H + ¹¹B → ³He channel; see fusion_pb11.py.",
            )
        )
        checks.append(
            SpecCheck(
                "U2c",
                "CH₄ loop sizing",
                f"ṁ_CH₄ sized for Q_wall",
                f"{result.ch4_mdot_kgps:.4f} kg/s  ΔT={result.ch4_delta_T_K:.1f} K",
                f"effectiveness {u.ch4_cooling_effectiveness:.2f}",
                SpecStatus.PASS if u.ch4_cooling_effectiveness >= 0.5 else SpecStatus.WARN,
            )
        )
        checks.append(
            SpecCheck(
                "U3b",
                "HTS cryo load",
                f"≤ 0.5 kW class @ scale=1",
                f"{result.hts_cryo_kw:.3f} kW",
                f"B={g.B_axial_tesla:.2f} T",
                SpecStatus.PASS if result.hts_cryo_kw <= 0.5 / max(u.hts_capability_scale, 0.1) else SpecStatus.WARN,
            )
        )

    # --- Plant closure ---
    mdot_ok = result.mass_flow_kgps > 0.01 if armed else True
    checks.append(
        SpecCheck(
            "PLANT",
            "Air Brayton mdot",
            f"~{sc.mass_flow_kgps_at_full:.0f} kg/s class @ full",
            f"{result.mass_flow_kgps:.2f} kg/s",
            f"compressor_eff {pad_status.compressor_effective:.2f}",
            SpecStatus.PASS if mdot_ok else SpecStatus.FAIL,
        )
    )
    for msg in result.thermal_warnings:
        checks.append(
            SpecCheck(
                "THERMAL",
                "Radial zoning (first wall → air vs CH₄)",
                "Brayton enthalpy vs gross — see report",
                msg[:120],
                "—",
                SpecStatus.WARN,
                "Wall-coupled Brayton may be << gross MW until HX tier is modeled.",
            )
        )
        break

    if armed and math.isfinite(jerr):
        checks.append(
            SpecCheck(
                "CLOSURE",
                "Jet power identity F²/(2ṁ) ≈ η·P_gross",
                f"rel. error ≤ {closure_tolerance:.0%}",
                f"{jerr:.1%}",
                f"η_jet = {sc.jet_propulsive_efficiency:.2f}",
                SpecStatus.PASS if jerr <= closure_tolerance else SpecStatus.WARN,
                "From orbitron_physics_surrogate traceability_chain.",
            )
        )

    if pic_used:
        checks.append(
            SpecCheck(
                "PIC",
                "WarpX coupling proxies in 0D",
                "ρ_e and/or beam norm finite",
                f"ρ_e={inputs.pic_rho_e_norm:.3g} beam={inputs.pic_beam_rho_norm:.3g}",
                "—",
                SpecStatus.PASS,
                "PIC validates fields/density — not fusion reaction rate.",
            )
        )

    if armed and fc_meta:
        cfg_pass = 2.8
        clump_ok = result.clump_index <= cfg_pass
        red_ok = result.clump_reduction_ratio >= 1.25
        checks.append(
            SpecCheck(
                "LAMINAR",
                "Clump index (s–r channel)",
                f"≤ {cfg_pass:.1f} with hack ON",
                f"{result.clump_index:.2f}",
                f"OFF/ON ratio {result.clump_reduction_ratio:.2f}×",
                SpecStatus.PASS if clump_ok else SpecStatus.FAIL,
                "High p95/median in bore = clumping (video red-blob case). "
                "Enable laminar relaminarization on Longitudinal 2D tab.",
            )
        )
        checks.append(
            SpecCheck(
                "LAMINAR2",
                "Laminar hack breaks up clumps",
                "clump_index(hack OFF) / clump(ON) ≥ 1.25",
                f"{result.clump_reduction_ratio:.2f}×",
                "hack "
                + ("ON" if result.laminar_hack_enabled else "OFF"),
                SpecStatus.PASS if red_ok else SpecStatus.WARN,
                "Compare level-1 timelapse with laminar checkbox OFF vs ON.",
            )
        )
        checks.append(
            SpecCheck(
                "FCH",
                "Fusion channel integrated power",
                f"~{target_mw:.1f} MW class",
                f"{result.fusion_channel_power_mw:.3f} MW",
                f"⟨σv⟩={fc_meta.get('sigma_v_m3_s', 0):.2e}",
                SpecStatus.PASS
                if abs(result.fusion_channel_power_mw - target_mw) < power_tolerance_mw * 2
                else SpecStatus.WARN,
                "Longitudinal s–r integral of R=n_p n_B ⟨σv⟩ E_rxn.",
            )
        )

    fusion_op = armed and result.gross_power_mw >= 0.5
    hard_fail = any(c.status == SpecStatus.FAIL for c in checks)
    validated = (
        fusion_op
        and not hard_fail
        and abs(res_mw) <= power_tolerance_mw
        and (not math.isfinite(jerr) or jerr <= closure_tolerance)
    )

    summary = (
        "VALIDATED: design meets unobtanium gates and power target."
        if validated
        else (
            "NOT VALIDATED: adjust geometry, unobtanium knobs, or run Solve — see failing specs."
            if armed
            else "PRE-IGNITE: complete pad startup (bleed → ignite) then validate burn."
        )
    )

    return DesignValidationReport(
        checks=checks,
        design_validated=validated,
        fusion_operating_point=fusion_op,
        power_target_mw=target_mw,
        power_achieved_mw=result.gross_power_mw,
        power_residual_mw=res_mw,
        jet_closure_rel_error=jerr,
        pic_coupling_used=pic_used,
        summary=summary,
    )


def validate_startup_step(
    inputs: SimulatorInputs,
    result: SteadyStateResult,
) -> list[SpecCheck]:
    """Physics allowed at current pad step (for step-through console)."""
    st = evaluate_pad_status(inputs.pad)
    checks: list[SpecCheck] = []

    checks.append(
        SpecCheck(
            "S1",
            "Pad APU",
            "energized",
            "ON" if st.state.pad_apu_online else "off",
            "—",
            SpecStatus.PASS if st.state.pad_apu_online else SpecStatus.N_A,
        )
    )
    checks.append(
        SpecCheck(
            "S2",
            "Starter",
            "engaged (APU on)",
            "ON" if st.state.starter_engage else "off",
            "—",
            SpecStatus.PASS if st.state.starter_engage and st.state.pad_apu_online else SpecStatus.N_A,
        )
    )
    checks.append(
        SpecCheck(
            "S3",
            "Bleed / compressor path",
            "open",
            "OPEN" if st.state.bleed_air_open else "closed",
            f"comp_eff={st.compressor_effective:.2f}",
            SpecStatus.PASS if st.state.bleed_air_open else SpecStatus.N_A,
            f"ṁ ≈ {result.mass_flow_kgps:.2f} kg/s",
        )
    )
    checks.append(
        SpecCheck(
            "S4",
            "Fusion armed",
            "ignite",
            "ARMED" if st.reactor_armed else "safe",
            f"P={result.gross_power_mw:.3f} MW",
            SpecStatus.PASS if st.reactor_armed else SpecStatus.N_A,
        )
    )
    return checks
