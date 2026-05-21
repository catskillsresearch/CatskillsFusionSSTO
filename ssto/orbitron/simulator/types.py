"""Typed inputs/outputs for the Orbitron steady-state simulator."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DeviceGeometry:
    """Coarse reactor + duct scale (lab defaults from orbitron_physics_surrogate.yaml)."""

    r_anode_m: float = 0.05
    r_cathode_m: float = 0.005
    length_m: float = 2.0
    V_cathode_v: float = -600_000.0
    B_axial_tesla: float = 2.0


@dataclass
class OperatingPoint:
    """Pad / console commands (0–1 unless noted)."""

    throttle: float = 1.0
    compressor: float = 1.0
    cathode_pulse: float = 0.6
    h2_sccm: float = 80.0
    b2h6_sccm: float = 20.0


@dataclass
class UnobtaniumParams:
    """
    Tunable material / physics knobs (Sprint 2 inverse-solve targets).

    These stand in for properties not available off-the-shelf (see UNOBTANIUM.md).
    """

    # U1 — cathode: multiplier on literature-like field-emission limit (1 = nominal model limit)
    field_emission_margin: float = 1.0
    # U2 — wall: max tolerable heat flux (W/m²) before CH₄ loop is insufficient
    max_wall_heat_flux_W_m2: float = 2.0e6
    # U2 — CH₄ cooling effectiveness (1 = nominal; <1 under-sized loop)
    ch4_cooling_effectiveness: float = 1.0
    # U3 — magnet: current-density capability scale for 2 T bore (1 = nominal HTS story)
    hts_capability_scale: float = 1.0
    # U4 — fusion / beam: scales net fusion-heating proxy (reactivity × confinement)
    fusion_reactivity_scale: float = 1.0
    beam_coupling_scale: float = 1.0


@dataclass
class PlantScales:
    """0D headline scales from orbitron_physics_surrogate.yaml surrogate_engineering."""

    target_gross_power_mw: float = 3.5
    jet_propulsive_efficiency: float = 0.55
    heat_kw_at_full: float = 400.0
    beam_screen_kw_per_ma: float = 0.6
    thrust_lbf_at_full: float = 4040.0
    mass_flow_kgps_at_full: float = 84.0
    density_log10_at_full: float = 11.0


@dataclass
class PadStartupState:
    """Pad console switches / levers (see ``pad_startup.py``)."""

    pad_apu_online: bool = False
    starter_engage: bool = False
    bleed_air_open: bool = False
    startup_trigger: bool = False
    throttle: float = 0.0
    compressor: float = 0.0
    cathode_pulse: float = 0.6
    live_simulation: bool = False
    laminar_relaminarization: bool = True


@dataclass
class SimulatorInputs:
    geometry: DeviceGeometry = field(default_factory=DeviceGeometry)
    operating: OperatingPoint = field(default_factory=OperatingPoint)
    pad: PadStartupState = field(default_factory=PadStartupState)
    unobtanium: UnobtaniumParams = field(default_factory=UnobtaniumParams)
    scales: PlantScales = field(default_factory=PlantScales)
    # Optional PIC proxy overrides (from last WarpX reduction); NaN = use heuristic
    pic_rho_e_norm: float = float("nan")
    pic_beam_rho_norm: float = float("nan")
    # Last fusion-channel s–r run (optional coupling into 0D plant)
    fusion_channel_power_mw: float = float("nan")


@dataclass
class SteadyStateResult:
    """Single steady-state evaluation."""

    gross_power_mw: float
    wall_heat_kw: float
    beam_current_ma: float
    beam_power_kw: float
    plasma_density_cm3: float
    log10_density: float
    thrust_lbf: float
    mass_flow_kgps: float
    jet_kinetic_power_mw: float
    equiv_exhaust_velocity_mps: float
    cathode_surface_field_V_m: float
    wall_heat_flux_W_m2: float
    feasible: bool
    violations: list[str] = field(default_factory=list)
    # p-¹¹B physics + thermal sizing (high-fidelity path)
    fusion_power_mw_physics: float = 0.0
    fusion_power_mw_surrogate: float = 0.0
    ion_temperature_kev: float = 0.0
    sigma_v_m3_s: float = 0.0
    ch4_mdot_kgps: float = 0.0
    ch4_delta_T_K: float = 0.0
    hts_cryo_kw: float = 0.0
    fueling_mix_scale: float = 0.0
    fusion_channel_power_mw: float = 0.0
    clump_index: float = 1.0
    clump_reduction_ratio: float = 1.0
    laminar_hack_enabled: bool = True
