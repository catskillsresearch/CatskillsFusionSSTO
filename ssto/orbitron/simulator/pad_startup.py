"""
Pad startup — Reply 15 Brayton sequence + Reply 19 Phase 1 interlocks.

Order (ground / wind-tunnel rig):
  1. APU → 2. Pneumatic starter → 3. Bleed (compressor airflow)
  4. Vacuum OK (1.1) → 5. Laser armed (1.3) → 6. HV enabled (1.4)
  7. Ignite / fusion (1.2 + 1.5 armed)
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ssto.orbitron.simulator.brayton_spool import (
    CompressorShaftMode,
    compressor_effective as _compressor_effective,
    compressor_shaft_mode,
    spool_drive_factor as _spool_drive_factor,
    turbine_takeover,
)
from ssto.orbitron.simulator.types import OperatingPoint, PadStartupState


@dataclass
class PadStartupStatus:
    """Resolved pad state after interlocks + effective air path."""

    state: PadStartupState
    reactor_armed: bool
    compressor_effective: float
    spool_drive_factor: float
    bleed_mass_fraction: float = 0.0
    turbine_takeover: bool = False
    shaft_mode: CompressorShaftMode = CompressorShaftMode.OFF
    interlock_messages: list[str] = field(default_factory=list)
    step_labels: list[str] = field(default_factory=list)


def apply_pad_interlocks(state: PadStartupState) -> PadStartupState:
    """Enforce Reply 19 / Reply 15 interlock chain."""
    s = PadStartupState(**{f.name: getattr(state, f.name) for f in PadStartupState.__dataclass_fields__.values()})
    if s.starter_engage and not s.pad_apu_online:
        s.starter_engage = False
    if s.bleed_air_open and not s.starter_engage:
        s.bleed_air_open = False
    if s.vacuum_interlock_ok and not s.bleed_air_open:
        s.vacuum_interlock_ok = False
    if s.laser_armed and not s.vacuum_interlock_ok:
        s.laser_armed = False
    if s.hv_enabled and not s.laser_armed:
        s.hv_enabled = False
    if s.startup_trigger and not (s.hv_enabled and s.bleed_air_open):
        s.startup_trigger = False
    return s


def compressor_effective(bleed_on: bool, starter_on: bool, armed: bool, comp: float) -> float:
    return _compressor_effective(bleed_on, starter_on, armed, comp)


def spool_drive_factor(bleed_on: bool, starter_on: bool, armed: bool) -> float:
    return _spool_drive_factor(bleed_on, starter_on, armed)


def evaluate_pad_status(state: PadStartupState) -> PadStartupStatus:
    raw = state
    s = apply_pad_interlocks(state)
    msgs: list[str] = []
    if raw.starter_engage and not s.starter_engage:
        msgs.append("Interlock: starter requires APU ON (2.4 / pad cart)")
    if raw.bleed_air_open and not s.bleed_air_open:
        msgs.append("Interlock: bleed requires starter ENGAGED")
    if raw.vacuum_interlock_ok and not s.vacuum_interlock_ok:
        msgs.append("Interlock: vacuum requires bleed OPEN (1.1 pumps)")
    if raw.laser_armed and not s.laser_armed:
        msgs.append("Interlock: laser requires VACUUM OK (1.3)")
    if raw.hv_enabled and not s.hv_enabled:
        msgs.append("Interlock: HV requires LASER ARMED (1.4)")
    if raw.startup_trigger and not s.startup_trigger:
        msgs.append("Interlock: ignite requires HV + bleed (1.2 core)")

    armed = s.startup_trigger
    comp_eff = compressor_effective(s.bleed_air_open, s.starter_engage, armed, s.compressor)
    spool = spool_drive_factor(s.bleed_air_open, s.starter_engage, armed)
    takeover = turbine_takeover(s.bleed_air_open, s.starter_engage, armed)
    shaft = compressor_shaft_mode(s.bleed_air_open, s.starter_engage, armed)
    from ssto.orbitron.simulator.brayton_spool import bleed_mass_fraction

    beta = bleed_mass_fraction(s.bleed_air_open)

    labels = [
        f"1 APU / cart: {'ON' if s.pad_apu_online else 'off'}",
        f"2 Starter (2.4): {'ENGAGED' if s.starter_engage else 'off'}",
        f"3 Bleed / compressor: {'OPEN' if s.bleed_air_open else 'closed'}  eff={comp_eff:.2f}  "
        f"shaft={shaft.value}  β={beta:.2f}",
        f"4 Vacuum (1.1): {'OK' if s.vacuum_interlock_ok else 'not ready'}",
        f"5 Laser 355 nm (1.3): {'ARMED' if s.laser_armed else 'off'}",
        f"6 HV (1.4): {'ENABLED' if s.hv_enabled else 'off'}",
        f"7 Fusion ignite: {'ARMED' if armed else 'safe'}  pulse={s.cathode_pulse:.2f}",
    ]

    return PadStartupStatus(
        state=s,
        reactor_armed=armed,
        compressor_effective=comp_eff,
        spool_drive_factor=spool,
        bleed_mass_fraction=beta,
        turbine_takeover=takeover,
        shaft_mode=shaft,
        interlock_messages=msgs,
        step_labels=labels,
    )


def effective_operating_point(
    op: OperatingPoint,
    pad: PadStartupState,
) -> tuple[OperatingPoint, PadStartupStatus]:
    from ssto.orbitron.simulator.injectants import b11_laser_delivery_scale, injectant_mixing_scale

    status = evaluate_pad_status(pad)
    s = status.state
    mix = injectant_mixing_scale(op.h2_sccm, op.laser_ablation_hz)
    boron = b11_laser_delivery_scale(
        laser_ablation_hz=op.laser_ablation_hz,
        reactor_armed=status.reactor_armed,
        vacuum_ok=s.vacuum_interlock_ok,
        laser_armed=s.laser_armed,
    )
    throttle = s.throttle if status.reactor_armed else 0.0
    fuel_gate = mix * boron
    return (
        OperatingPoint(
            throttle=throttle,
            compressor=status.compressor_effective,
            cathode_pulse=s.cathode_pulse if status.reactor_armed else s.cathode_pulse * 0.25,
            h2_sccm=op.h2_sccm * fuel_gate,
            laser_ablation_hz=op.laser_ablation_hz * boron,
            b11_target_index=op.b11_target_index,
        ),
        status,
    )
