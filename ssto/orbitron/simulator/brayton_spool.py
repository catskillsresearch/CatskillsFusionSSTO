"""
Single-spool Brayton bookkeeping: bleed split, electric start vs turbine takeover.

Design intent matches ``orbitron_reference_plant.yaml`` and ``brayton_air_cycle.md``.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Fraction of corrected inlet mass flow routed to compressor bleed (not core/nozzle path).
DEFAULT_BLEED_MASS_FRACTION = 0.12

SPOOL_BLEED_ONLY = 0.12
SPOOL_ELECTRIC_STARTER = 0.42
SPOOL_TURBINE_TAKEOVER = 1.0


class CompressorShaftMode(str, Enum):
    OFF = "off"
    BLEED_IDLE = "bleed_idle"
    ELECTRIC_STARTER = "electric_starter"
    TURBINE = "turbine"


@dataclass(frozen=True)
class BraytonPathResult:
    """Resolved air path for 0D plant / pad status."""

    bleed_mass_fraction: float
    spool_drive_factor: float
    shaft_mode: CompressorShaftMode
    turbine_takeover: bool
    mdot_in_kgps: float
    mdot_core_kgps: float
    mdot_bleed_kgps: float


def bleed_mass_fraction(bleed_on: bool, *, beta: float = DEFAULT_BLEED_MASS_FRACTION) -> float:
    if not bleed_on:
        return 0.0
    return max(0.0, min(0.45, beta))


def turbine_takeover(bleed_on: bool, starter_on: bool, armed: bool) -> bool:
    """Cruise: fusion armed, bleed open, pad starter disengaged."""
    return bool(bleed_on and armed and not starter_on)


def spool_drive_factor(bleed_on: bool, starter_on: bool, armed: bool) -> float:
    if not bleed_on:
        return 0.0
    if turbine_takeover(bleed_on, starter_on, armed):
        return SPOOL_TURBINE_TAKEOVER
    if starter_on:
        return SPOOL_ELECTRIC_STARTER
    return SPOOL_BLEED_ONLY


def compressor_shaft_mode(bleed_on: bool, starter_on: bool, armed: bool) -> CompressorShaftMode:
    if not bleed_on:
        return CompressorShaftMode.OFF
    if turbine_takeover(bleed_on, starter_on, armed):
        return CompressorShaftMode.TURBINE
    if starter_on:
        return CompressorShaftMode.ELECTRIC_STARTER
    return CompressorShaftMode.BLEED_IDLE


def compressor_effective(bleed_on: bool, starter_on: bool, armed: bool, comp: float) -> float:
    return max(0.0, min(1.0, comp)) * spool_drive_factor(bleed_on, starter_on, armed)


def evaluate_brayton_path(
    *,
    bleed_on: bool,
    starter_on: bool,
    armed: bool,
    compressor_command: float,
    mass_flow_full_kgps: float,
    throttle: float,
    beta: float = DEFAULT_BLEED_MASS_FRACTION,
) -> BraytonPathResult:
    """Map pad state + command to inlet/core/bleed mass flows."""
    spool = spool_drive_factor(bleed_on, starter_on, armed)
    c = max(0.0, min(1.0, compressor_command))
    t = max(0.0, min(1.0, throttle))
    mdot_in = mass_flow_full_kgps * c * spool * (0.2 + 0.8 * t)
    beta_eff = bleed_mass_fraction(bleed_on, beta=beta)
    mdot_bleed = mdot_in * beta_eff
    mdot_core = mdot_in - mdot_bleed
    return BraytonPathResult(
        bleed_mass_fraction=beta_eff,
        spool_drive_factor=spool,
        shaft_mode=compressor_shaft_mode(bleed_on, starter_on, armed),
        turbine_takeover=turbine_takeover(bleed_on, starter_on, armed),
        mdot_in_kgps=mdot_in,
        mdot_core_kgps=mdot_core,
        mdot_bleed_kgps=mdot_bleed,
    )
