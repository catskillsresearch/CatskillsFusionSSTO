"""
0D steady-state plant: p-¹¹B fusion physics + surrogate calibration + U1–U4 gates.

Power headline
--------------
  Primary: ``fusion_pb11.evaluate_fusion_pb11`` (reactivity × fueling × volume).
  Blend: ``surrogate_calib.blended_gross_power_mw`` with YAML/CSV-calibrated PIC proxy.
  Off when pad not ignited (no fusion armed).
"""
from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ssto.orbitron.simulator.types import SimulatorInputs, SteadyStateResult


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def evaluate_steady_state(inputs: SimulatorInputs) -> SteadyStateResult:
    """Evaluate one steady operating point and check unobtanium constraints."""
    from ssto.orbitron.simulator.fusion_pb11 import evaluate_fusion_pb11
    from ssto.orbitron.simulator.pad_startup import effective_operating_point, evaluate_pad_status
    from ssto.orbitron.simulator.surrogate_calib import (
        blended_gross_power_mw,
        calibration_factor_from_csv,
        yaml_scale_scalars,
    )
    from ssto.orbitron.simulator.thermal_systems import size_ch4_loop, size_hts_cryo
    from ssto.orbitron.simulator.types import SteadyStateResult

    g = inputs.geometry
    op, _pad_status = effective_operating_point(inputs.operating, inputs.pad)
    pad_status = evaluate_pad_status(inputs.pad)
    u = inputs.unobtanium
    sc = inputs.scales

    t = _clamp01(op.throttle)
    c = _clamp01(op.compressor)
    p = _clamp01(op.cathode_pulse)
    armed = pad_status.reactor_armed

    violations: list[str] = []

    # --- U1: cathode surface field ---
    gap_m = max(g.r_anode_m - g.r_cathode_m, 1.0e-4)
    e_surface = abs(g.V_cathode_v) / gap_m
    e_limit = 3.0e9 * u.field_emission_margin
    if e_surface > e_limit:
        violations.append(
            f"U1 cathode: |E|={e_surface:.2e} V/m exceeds emission limit {e_limit:.2e} V/m"
        )

    rho_norm = 1.0
    if math.isfinite(inputs.pic_rho_e_norm):
        rho_norm = max(0.15, min(3.0, inputs.pic_rho_e_norm))

    # --- p-¹¹B fusion physics ---
    fusion = evaluate_fusion_pb11(
        r_anode_m=g.r_anode_m,
        length_m=g.length_m,
        V_cathode_v=g.V_cathode_v,
        throttle=t if armed else 0.0,
        cathode_pulse=p,
        h2_sccm=op.h2_sccm,
        b2h6_sccm=op.b2h6_sccm,
        fusion_reactivity_scale=u.fusion_reactivity_scale,
        pic_rho_e_norm=inputs.pic_rho_e_norm,
    )

    proof_chain = os.environ.get("ORBITRON_PROOF_CHAIN") == "1"
    sur = yaml_scale_scalars(t, c, rho_norm)
    cal = 1.0 if proof_chain else calibration_factor_from_csv()
    gross_mw, p_phys_mw, p_sur_mw = blended_gross_power_mw(
        fusion.fusion_power_mw if armed else 0.0,
        sur.gross_power_mw if armed else 0.0,
        physics_weight=1.0 if proof_chain else 0.7,
        calibration_factor=cal,
    )
    if (
        not proof_chain
        and armed
        and math.isfinite(inputs.fusion_channel_power_mw)
        and inputs.fusion_channel_power_mw > 0
    ):
        fc_mw = inputs.fusion_channel_power_mw
        gross_mw = 0.55 * gross_mw + 0.45 * fc_mw
        p_phys_mw = fc_mw

    # Plasma density from physics + heuristic floor
    n_cm3 = max(fusion.n_proton_m3, fusion.n_boron_m3) / 1.0e6
    log10_n = math.log10(max(n_cm3, 1.0))
    if log10_n < 9.0 and armed:
        log10_n = 9.0 + 1.8 * t + 1.2 * p + 0.3 * c + math.log10(max(rho_norm, 0.05))

    v_kv = abs(g.V_cathode_v) / 1000.0
    kw_per_ma = sc.beam_screen_kw_per_ma * (v_kv / 600.0)
    beam_ma = max(5.0 * t * u.beam_coupling_scale, 0.0)
    if math.isfinite(inputs.pic_beam_rho_norm):
        beam_ma *= max(0.2, min(3.0, inputs.pic_beam_rho_norm))
    beam_kw = beam_ma * kw_per_ma

    wall_kw = sc.heat_kw_at_full * t * (0.5 + 0.5 * rho_norm) * (v_kv / 600.0) ** 0.5
    if armed:
        wall_kw = max(wall_kw, gross_mw * 1000.0 * 0.11)

    anode_area_m2 = 2.0 * math.pi * g.r_anode_m * max(g.length_m, 0.1)
    q_wall = (wall_kw * 1000.0) / max(anode_area_m2, 1.0e-6)

    ch4 = size_ch4_loop(wall_kw, ch4_effectiveness=u.ch4_cooling_effectiveness)
    hts = size_hts_cryo(g.B_axial_tesla, g.length_m, g.r_anode_m, hts_capability_scale=u.hts_capability_scale)

    q_allow = u.max_wall_heat_flux_W_m2 * u.ch4_cooling_effectiveness
    if q_wall > q_allow:
        violations.append(
            f"U2 wall: heat flux {q_wall:.2e} W/m² > allowed {q_allow:.2e} W/m² (CH₄ loop)"
        )
    if not ch4.passes and armed and wall_kw > 50.0:
        violations.append(
            f"U2 CH₄: loop undersized — need effectiveness ≥ {ch4.required_effectiveness:.2f}"
        )

    if not hts.passes:
        violations.append(f"U3 magnet: B={g.B_axial_tesla:.2f} T > HTS scale limit {2.0 * u.hts_capability_scale:.2f} T")
    if hts.cryo_load_kw > 0.5 / max(u.hts_capability_scale, 0.1) and armed:
        violations.append(
            f"U3 cryo: load {hts.cryo_load_kw:.2f} kW high for HTS scale {u.hts_capability_scale:.2f}"
        )

    if beam_ma < 1.0 and gross_mw > 0.5:
        violations.append(f"U4 beam: {beam_ma:.2f} mA < 1 mA integration target at meaningful power")

    if log10_n < 11.0 and gross_mw > 0.5:
        violations.append(f"U4 density: log10(n)={log10_n:.2f} < 11 (Series-A-scale goal)")

    if armed and gross_mw < 0.1:
        violations.append("U4 fusion: ignited but p-¹¹B model reports negligible fusion power")

    mdot = sc.mass_flow_kgps_at_full * c * (0.2 + 0.8 * t)
    jet_mw = sc.jet_propulsive_efficiency * gross_mw
    thrust_n = math.sqrt(max(0.0, 2.0 * jet_mw * 1.0e6 * mdot))
    thrust_lbf = thrust_n * 0.224809
    v_e = thrust_n / mdot if mdot > 1.0e-9 else 0.0

    return SteadyStateResult(
        gross_power_mw=gross_mw,
        wall_heat_kw=wall_kw,
        beam_current_ma=beam_ma,
        beam_power_kw=beam_kw,
        plasma_density_cm3=n_cm3,
        log10_density=log10_n,
        thrust_lbf=thrust_lbf,
        mass_flow_kgps=mdot,
        jet_kinetic_power_mw=jet_mw,
        equiv_exhaust_velocity_mps=v_e,
        cathode_surface_field_V_m=e_surface,
        wall_heat_flux_W_m2=q_wall,
        feasible=len(violations) == 0,
        violations=violations,
        fusion_power_mw_physics=p_phys_mw,
        fusion_power_mw_surrogate=p_sur_mw,
        ion_temperature_kev=fusion.ion_temperature_kev,
        sigma_v_m3_s=fusion.sigma_v_m3_s,
        ch4_mdot_kgps=ch4.mdot_ch4_kgps,
        ch4_delta_T_K=ch4.delta_T_K,
        hts_cryo_kw=hts.cryo_load_kw,
        fueling_mix_scale=fusion.fueling_mix_scale,
        fusion_channel_power_mw=inputs.fusion_channel_power_mw
        if math.isfinite(inputs.fusion_channel_power_mw)
        else p_phys_mw,
        clump_index=1.0,
        clump_reduction_ratio=1.0,
        laminar_hack_enabled=inputs.pad.laminar_relaminarization,
    )
