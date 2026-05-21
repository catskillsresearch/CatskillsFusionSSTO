"""
CH₄ wall cooling and HTS magnet cryogenic load sizing (U2 / U3 spec quantification).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Ch4LoopSizing:
    """Liquid methane annulus loop for first-wall heat removal."""

    wall_heat_w: float
    mdot_ch4_kgps: float
    volume_flow_lps: float
    delta_T_K: float
    inlet_T_K: float
    outlet_T_K: float
    required_effectiveness: float  # vs unobtanium ch4_cooling_effectiveness knob
    passes: bool


@dataclass(frozen=True)
class HtsCryoSizing:
    """Coarse HTS solenoid cryogenic heat leak + AC loss proxy."""

    B_tesla: float
    bore_length_m: float
    bore_radius_m: float
    cryo_load_w: float
    cryo_load_kw: float
    implied_capability_scale: float  # vs required B
    passes: bool


# Liquid CH₄ near −160 °C: approximate liquid Cp [J/(kg·K)]
CP_CH4_LIQ = 3480.0
RHO_CH4_LIQ = 422.0  # kg/m³
T_CH4_IN_K = 113.0  # ~−160 °C
DELTA_T_ALLOW_K = 12.0  # allowable rise through wall jacket


def size_ch4_loop(
    wall_heat_kw: float,
    *,
    ch4_effectiveness: float = 1.0,
    delta_T_allow_K: float = DELTA_T_ALLOW_K,
) -> Ch4LoopSizing:
    """Size CH₄ mass flow to absorb wall heat at allowable ΔT."""
    q_w = max(0.0, wall_heat_kw) * 1000.0
    eff = max(0.05, ch4_effectiveness)
    dT = max(2.0, delta_T_allow_K)
    mdot = q_w / (CP_CH4_LIQ * dT * eff)
    vol_lps = mdot / RHO_CH4_LIQ * 1000.0
    required_eff = q_w / max(mdot * CP_CH4_LIQ * dT, 1.0)
    return Ch4LoopSizing(
        wall_heat_w=q_w,
        mdot_ch4_kgps=mdot,
        volume_flow_lps=vol_lps,
        delta_T_K=dT,
        inlet_T_K=T_CH4_IN_K,
        outlet_T_K=T_CH4_IN_K + dT,
        required_effectiveness=required_eff,
        passes=eff >= required_eff / max(required_eff, 1e-9) and eff >= 0.5,
    )


# Baseline cryo load at 2 T, 2 m bore, 5 cm radius [W] before HTS scale
_CRYO_BASE_W_AT_NOMINAL = 180.0


def size_hts_cryo(
    B_tesla: float,
    length_m: float,
    r_bore_m: float,
    *,
    hts_capability_scale: float = 1.0,
) -> HtsCryoSizing:
    """
    Cryogenic load scales ~ B² · L · r (AC + conduction placeholder).

    ``hts_capability_scale`` ≥ 1 means stronger HTS / lower loss than nominal.
    """
    B = max(0.1, B_tesla)
    L = max(0.1, length_m)
    r = max(0.02, r_bore_m)
    scale = max(0.1, hts_capability_scale)
    load_w = _CRYO_BASE_W_AT_NOMINAL * (B / 2.0) ** 2 * (L / 2.0) * (r / 0.05) / scale
    b_max = 2.0 * scale
    return HtsCryoSizing(
        B_tesla=B,
        bore_length_m=L,
        bore_radius_m=r,
        cryo_load_w=load_w,
        cryo_load_kw=load_w / 1000.0,
        implied_capability_scale=scale,
        passes=B <= b_max + 1e-3,
    )
