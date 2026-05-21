"""
Pad startup sequence — mirrors FlightGear / JSBSim / ``orbitron_operator_console_spec.yaml``.

Discrete steps: APU → starter → bleed → ignite (BRB), then continuous throttle / compressor /
cathode pulse. Interlocks match generated ``OrbitronOps`` in ``compile_orbitron_nasal.py``.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ssto.orbitron.simulator.types import OperatingPoint, PadStartupState


@dataclass
class PadStartupStatus:
    """Resolved pad state after interlocks + effective air path."""

    state: PadStartupState
    reactor_armed: bool
    compressor_effective: float
    spool_drive_factor: float
    interlock_messages: list[str] = field(default_factory=list)
    step_labels: list[str] = field(default_factory=list)


def apply_pad_interlocks(state: PadStartupState) -> PadStartupState:
    """Enforce starter-requires-APU and ignite-requires-bleed."""
    s = PadStartupState(**{f.name: getattr(state, f.name) for f in PadStartupState.__dataclass_fields__.values()})
    if s.starter_engage and not s.pad_apu_online:
        s.starter_engage = False
    if s.startup_trigger and not s.bleed_air_open:
        s.startup_trigger = False
    return s


def compressor_effective(bleed_on: bool, starter_on: bool, armed: bool, comp: float) -> float:
    """Same closure as ``OrbitronOps.compressor_effective`` in Nasal."""
    if not bleed_on:
        return 0.0
    spool = 1.0 if armed else (0.42 if starter_on else 0.12)
    return max(0.0, min(1.0, comp)) * spool


def spool_drive_factor(bleed_on: bool, starter_on: bool, armed: bool) -> float:
    """JSBSim ``spool-drive-factor`` intent: starter cranks spool before ignite."""
    if not bleed_on:
        return 0.0
    if armed:
        return 1.0
    return 0.42 if starter_on else 0.12


def evaluate_pad_status(state: PadStartupState) -> PadStartupStatus:
    """Full pad resolution with human-readable step status."""
    raw = state
    s = apply_pad_interlocks(state)
    msgs: list[str] = []
    if raw.starter_engage and not s.starter_engage:
        msgs.append("Interlock: starter requires APU ON")
    if raw.startup_trigger and not s.startup_trigger:
        msgs.append("Interlock: ignite requires BLEED AIR")

    armed = s.startup_trigger
    comp_eff = compressor_effective(s.bleed_air_open, s.starter_engage, armed, s.compressor)
    spool = spool_drive_factor(s.bleed_air_open, s.starter_engage, armed)

    labels = [
        f"1 APU: {'ON' if s.pad_apu_online else 'off'}",
        f"2 Starter: {'ENGAGED' if s.starter_engage else 'off'}",
        f"3 Bleed: {'OPEN' if s.bleed_air_open else 'closed'}",
        f"4 Ignite: {'ARMED' if armed else 'safe'}",
        f"5 Run: throttle={s.throttle:.2f}  comp_eff={comp_eff:.2f}  pulse={s.cathode_pulse:.2f}",
    ]

    return PadStartupStatus(
        state=s,
        reactor_armed=armed,
        compressor_effective=comp_eff,
        spool_drive_factor=spool,
        interlock_messages=msgs,
        step_labels=labels,
    )


def injectant_mixing_scale(h2_sccm: float, b2h6_sccm: float) -> float:
    """
    0D proxy for tangential H⁺ / B⁺ injector balance (p-¹¹B fueling).

    Peaks near a coarse H:B flow ratio; collapses if either stream is off.
    """
    if h2_sccm < 1.0 or b2h6_sccm < 0.5:
        return 0.05
    ratio = h2_sccm / max(b2h6_sccm, 0.1)
    optimal = 4.0
    return max(0.05, min(1.0, float(__import__("math").exp(-0.08 * (ratio - optimal) ** 2))))


def effective_operating_point(
    op: OperatingPoint,
    pad: PadStartupState,
) -> tuple[OperatingPoint, PadStartupStatus]:
    """Map console levers + pad gates into the 0D plant ``OperatingPoint``."""
    status = evaluate_pad_status(pad)
    s = status.state
    mix = injectant_mixing_scale(op.h2_sccm, op.b2h6_sccm)
    fusion_gate = 1.0 if status.reactor_armed else 0.0
    # Pre-ignite: air path only; no beam throttle until armed
    throttle = s.throttle if status.reactor_armed else 0.0
    return (
        OperatingPoint(
            throttle=throttle,
            compressor=status.compressor_effective,
            cathode_pulse=s.cathode_pulse if status.reactor_armed else s.cathode_pulse * 0.25,
            h2_sccm=op.h2_sccm * mix * fusion_gate,
            b2h6_sccm=op.b2h6_sccm * mix * fusion_gate,
        ),
        status,
    )
