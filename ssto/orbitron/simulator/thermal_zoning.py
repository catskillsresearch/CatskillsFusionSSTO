"""
Radial thermal zoning and power splits for the Orbitron 0D plant.

See ``ssto/orbitron/THERMAL_ZONING.md``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from ssto.orbitron.simulator.types import DeviceGeometry

# Default annulus and cryostat thickness [m] beyond r_anode (Phase-1 benchmark).
AIR_ANNULUS_THICKNESS_M = 0.02
CRYOSTAT_GAP_THICKNESS_M = 0.015
MAGNET_THICKNESS_M = 0.025

# Fraction of first-wall load removed by internal CH₄ intercept (rest to air annulus).
CH4_WALL_INTERCEPT_FRACTION = 0.55

# Ash / core bleed enthalpy into nozzle plenum as fraction of gross fusion thermal.
ASH_MIXER_FRACTION_OF_GROSS = 0.02


@dataclass(frozen=True)
class RadialZones:
    """Inside-out radii [m] for documentation and cryostat outer radius."""

    r_cathode_m: float
    r_first_wall_m: float
    r_air_channel_outer_m: float
    r_cryostat_outer_m: float
    r_magnet_outer_m: float

    @property
    def reactor_outer_diameter_m(self) -> float:
        return 2.0 * self.r_magnet_outer_m


def radial_zones_from_geometry(g: DeviceGeometry) -> RadialZones:
    r_fw = max(g.r_anode_m, g.r_cathode_m * 1.5)
    return RadialZones(
        r_cathode_m=g.r_cathode_m,
        r_first_wall_m=r_fw,
        r_air_channel_outer_m=r_fw + AIR_ANNULUS_THICKNESS_M,
        r_cryostat_outer_m=r_fw + AIR_ANNULUS_THICKNESS_M + CRYOSTAT_GAP_THICKNESS_M,
        r_magnet_outer_m=r_fw + AIR_ANNULUS_THICKNESS_M + CRYOSTAT_GAP_THICKNESS_M + MAGNET_THICKNESS_M,
    )


@dataclass(frozen=True)
class ThermalPowerSplit:
    first_wall_kw: float
    ch4_wall_intercept_kw: float
    air_annulus_kw: float
    magnet_cryo_kw: float
    cryostat_radiation_budget_kw: float
    ash_mixer_kw: float
    brayton_thermal_kw: float

    def brayton_thermal_mw(self) -> float:
        return self.brayton_thermal_kw / 1000.0


def split_first_wall_power(
    first_wall_kw: float,
    *,
    gross_power_mw: float = 0.0,
    ch4_intercept_fraction: float = CH4_WALL_INTERCEPT_FRACTION,
) -> tuple[float, float, float]:
    """Return (ch4_intercept_kw, air_annulus_kw, ash_mixer_kw)."""
    fw = max(0.0, first_wall_kw)
    ch4 = fw * max(0.0, min(1.0, ch4_intercept_fraction))
    air = max(0.0, fw - ch4)
    ash = max(0.0, gross_power_mw * 1000.0 * ASH_MIXER_FRACTION_OF_GROSS)
    return ch4, air, ash


def estimate_cryostat_radiation_kw(
    *,
    hot_face_temp_k: float = 1100.0,
    cold_face_temp_k: float = 113.0,
    emissivity: float = 0.12,
    view_factor: float = 0.35,
) -> float:
    """Order-of-magnitude radiative leak across MLI gap [kW] — placeholder for U3 budgeting."""
    sigma = 5.67e-8
    q_w_m2 = (
        emissivity
        * view_factor
        * sigma
        * (hot_face_temp_k**4 - cold_face_temp_k**4)
    )
    # ~0.015 m gap × 2π r ~ 0.06 m × 1.2 m length ≈ 0.45 m² wetted proxy
    area_proxy_m2 = 0.45
    return q_w_m2 * area_proxy_m2 / 1000.0


def evaluate_thermal_split(
    *,
    first_wall_kw: float,
    gross_power_mw: float,
    magnet_cryo_kw: float,
    ch4_intercept_fraction: float = CH4_WALL_INTERCEPT_FRACTION,
) -> ThermalPowerSplit:
    ch4, air, ash = split_first_wall_power(
        first_wall_kw,
        gross_power_mw=gross_power_mw,
        ch4_intercept_fraction=ch4_intercept_fraction,
    )
    rad = estimate_cryostat_radiation_kw()
    brayton = air + ash
    return ThermalPowerSplit(
        first_wall_kw=first_wall_kw,
        ch4_wall_intercept_kw=ch4,
        air_annulus_kw=air,
        magnet_cryo_kw=magnet_cryo_kw,
        cryostat_radiation_budget_kw=rad,
        ash_mixer_kw=ash,
        brayton_thermal_kw=brayton,
    )


def check_thermal_zoning(
    split: ThermalPowerSplit,
    *,
    gross_power_mw: float,
    target_gross_mw: float = 3.5,
) -> list[str]:
    """Warnings when Brayton enthalpy is inconsistent with fusion headline."""
    out: list[str] = []
    if gross_power_mw < 0.1:
        return out
    brayton_mw = split.brayton_thermal_mw()
    if brayton_mw < 0.25 * gross_power_mw:
        out.append(
            f"Thermal zoning: Brayton enthalpy {brayton_mw:.2f} MW < 25% of gross "
            f"{gross_power_mw:.2f} MW — annulus + ash may not close turbine T3 at target {target_gross_mw:g} MW"
        )
    if split.magnet_cryo_kw > 2.0 * split.cryostat_radiation_budget_kw + 0.5:
        out.append(
            f"Thermal zoning: magnet cryo {split.magnet_cryo_kw:.2f} kW exceeds radiative budget "
            f"{split.cryostat_radiation_budget_kw:.2f} kW — check cryostat MLI"
        )
    return out
