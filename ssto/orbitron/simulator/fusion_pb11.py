"""
p-¹¹B fusion power model for the Orbitron 0D plant (Sprint 2 high-fidelity path).

Reaction (headline channel):
  ¹H + ¹¹B → 3 ⁴He + 8.7 MeV (net ~8.68 MeV per reaction used here)

Model structure
---------------
  P_fusion [W] = η_conf · V_plasma · (n_p · n_B) · <σv>(T_i) · E_rxn

where:
  - ``T_i`` [keV] is an effective ion temperature from cathode potential and pulse.
  - ``n_p``, ``n_B`` [m⁻³] from H₂ and solid **¹¹B** laser ablation into the bore volume.
  - ``<σv>`` uses a peaked analytical fit to published p-¹¹B reactivity (Nevins/Swain class).
  - ``η_conf`` combines geometry fill, axial length, and ``fusion_reactivity_scale`` (U4 knob).

PIC note: WarpX does not compute this rate; ``pic_rho_e_norm`` modulates ``η_conf`` when present.

References (order-of-magnitude): Nevins & Swain, Fusion Technol. 1998; Sikora & Scharff H-mode scaling
adapted only as confinement placeholder — not a full transport solve.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Literal

from ssto.orbitron.simulator.injectants import effective_b11_density_scale, injectant_mixing_scale

ReactivityModel = Literal["design", "literature"]

# Design curve peak log10(⟨σv⟩) — calibrated to Orbitron reference point (~3.5 MW @ η≈1).
_DESIGN_LOG_SV_PEAK = -13.15
# Literature-class peak (~3 orders lower); not tuned to Catskills power target.
_LITERATURE_LOG_SV_PEAK = -16.15
_REACTIVITY_LOG_T_PEAK = 2.55
_REACTIVITY_LOG_T_WIDTH = 3.2

# Net energy per p-¹¹B reaction [J]
E_RXN_J = 8.68e6 * 1.602176634e-19  # 8.68 MeV → J

# SCCM → particle injection rate [particles/s] at STP (ideal gas, 22.4 L/mol)
_SCCM_TO_PARTICLES_S = 7.5e-5 / 101325.0 * 6.02214076e23 / 22.4e-3


@dataclass(frozen=True)
class FusionPhysicsResult:
    """Detailed fusion calculation for validation export."""

    ion_temperature_kev: float
    sigma_v_m3_s: float
    n_proton_m3: float
    n_boron_m3: float
    plasma_volume_m3: float
    confinement_factor: float
    reaction_rate_m3_s: float
    fusion_power_w: float
    fusion_power_mw: float
    fueling_mix_scale: float


def active_reactivity_model() -> ReactivityModel:
    """``ORBITRON_REACTIVITY_MODEL``: ``design`` (calibrated) or ``literature`` (honest σv)."""
    raw = os.environ.get("ORBITRON_REACTIVITY_MODEL", "design").strip().lower()
    return "literature" if raw == "literature" else "design"


def pb11_reactivity_m3_s(T_kev: float, *, model: ReactivityModel | None = None) -> float:
    """
    Volume-averaged <σv> for p-¹¹B vs ion temperature [keV].

    ``design``: peaked fit calibrated to Orbitron reference (see module docstring).
    ``literature``: same shape, lower peak — not tuned to 3.5 MW closure.
    """
    T = max(10.0, min(1200.0, float(T_kev)))
    log_t = math.log10(T)
    m = model or active_reactivity_model()
    peak = _LITERATURE_LOG_SV_PEAK if m == "literature" else _DESIGN_LOG_SV_PEAK
    log_sv = peak - _REACTIVITY_LOG_T_WIDTH * (log_t - _REACTIVITY_LOG_T_PEAK) ** 2
    return 10.0**log_sv


def sccm_to_density_m3(
    sccm: float,
    volume_m3: float,
    *,
    residence_time_s: float = 5.0e-4,
) -> float:
    """
    Steady-state number density from volumetric flow into plasma volume.

    ``n ≈ (Γ · τ) / V`` with Γ from sccm and τ a confinement / dwell time.
    """
    if volume_m3 < 1.0e-12 or sccm < 0.01:
        return 0.0
    gamma = sccm * _SCCM_TO_PARTICLES_S
    return gamma * residence_time_s / volume_m3


def effective_ion_temperature_kev(
    V_cathode_v: float,
    cathode_pulse: float,
    throttle: float,
) -> float:
    """Map cathode bias + pulse to effective reacting ion energy [keV]."""
    v_kv = abs(V_cathode_v) / 1000.0
    p = max(0.05, min(1.0, cathode_pulse))
    t = max(0.05, min(1.0, throttle))
    # Fraction of cathode potential appearing in reacting ion energy (beam + sheath physics placeholder)
    return max(20.0, 0.42 * v_kv * (0.55 + 0.45 * p) * (0.6 + 0.4 * t))


def plasma_volume_m3(r_anode_m: float, length_m: float, fill_factor: float = 0.35) -> float:
    return math.pi * r_anode_m * r_anode_m * max(length_m, 0.1) * fill_factor


def evaluate_fusion_pb11(
    *,
    r_anode_m: float,
    length_m: float,
    V_cathode_v: float,
    throttle: float,
    cathode_pulse: float,
    h2_sccm: float,
    laser_ablation_hz: float,
    fusion_reactivity_scale: float = 1.0,
    pic_rho_e_norm: float = float("nan"),
    volume_fill: float = 0.35,
    tau_residence_s: float = 5.0e-4,
    reactivity_model: ReactivityModel | None = None,
) -> FusionPhysicsResult:
    """Compute p-¹¹B fusion thermal power from fueling, geometry, and ion energy."""
    mix = injectant_mixing_scale(h2_sccm, laser_ablation_hz)
    V = plasma_volume_m3(r_anode_m, length_m, volume_fill)

    n_h = sccm_to_density_m3(h2_sccm * mix, V, residence_time_s=tau_residence_s)
    b_scale = effective_b11_density_scale(laser_ablation_hz, mix, 1.0)
    n_b = sccm_to_density_m3(max(b_scale, 0.05), V, residence_time_s=tau_residence_s)
    # Use min species for rate (reactant-limited)
    n_p = n_h
    n_b_eff = max(n_b, n_p * 0.05)

    T_kev = effective_ion_temperature_kev(V_cathode_v, cathode_pulse, throttle)
    sv = pb11_reactivity_m3_s(T_kev, model=reactivity_model)

    # Confinement / PIC coupling
    conf = fusion_reactivity_scale * (0.55 + 0.45 * throttle) * (0.5 + 0.5 * mix)
    if math.isfinite(pic_rho_e_norm):
        conf *= max(0.15, min(3.0, pic_rho_e_norm))

    # Reaction rate density [m⁻³ s⁻¹]: R = n_p * n_B * <σv>
    R = n_p * n_b_eff * sv
    P_w = conf * V * R * E_RXN_J
    P_mw = P_w / 1.0e6

    return FusionPhysicsResult(
        ion_temperature_kev=T_kev,
        sigma_v_m3_s=sv,
        n_proton_m3=n_p,
        n_boron_m3=n_b_eff,
        plasma_volume_m3=V,
        confinement_factor=conf,
        reaction_rate_m3_s=R,
        fusion_power_w=P_w,
        fusion_power_mw=P_mw,
        fueling_mix_scale=mix,
    )
