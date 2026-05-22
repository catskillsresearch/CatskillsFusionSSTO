"""Build ``SimulatorInputs`` from Proof Suite chain config + pad console."""
from __future__ import annotations

from ssto.orbitron.simulator.injectants import normalize_injectants_cfg
from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.types import (
    DeviceGeometry,
    OperatingPoint,
    PadStartupState,
    PlantScales,
    SimulatorInputs,
    UnobtaniumParams,
)


def simulator_inputs_from_state(
    state: ProofSuiteState,
    pad: PadStartupState | None = None,
) -> SimulatorInputs:
    cfg = state.config
    g = cfg["geometry"]
    inj = normalize_injectants_cfg(cfg["injectants"])
    p = cfg["pad"]
    pad_state = pad or PadStartupState(
        pad_apu_online=bool(p.get("pad_apu_online", True)),
        starter_engage=bool(p.get("starter_engage", True)),
        bleed_air_open=bool(p.get("bleed_air_open", True)),
        vacuum_interlock_ok=bool(p.get("vacuum_interlock_ok", False)),
        laser_armed=bool(p.get("laser_armed", False)),
        hv_enabled=bool(p.get("hv_enabled", False)),
        startup_trigger=bool(p.get("startup_trigger", False)),
        throttle=float(p.get("throttle", 0.0)),
        compressor=float(p.get("compressor", 0.0)),
        cathode_pulse=float(p.get("cathode_pulse", 0.75)),
        laminar_relaminarization=bool(p.get("laminar_relaminarization", True)),
    )
    u = cfg.get("unobtanium", {})
    scales = cfg.get("plant_scales", {})
    return SimulatorInputs(
        geometry=DeviceGeometry(
            r_anode_m=float(g["r_anode_m"]),
            r_cathode_m=float(g["r_cathode_m"]),
            length_m=float(g["length_m"]),
            V_cathode_v=float(g["V_cathode_v"]),
            B_axial_tesla=float(g["B_axial_tesla"]),
        ),
        operating=OperatingPoint(
            throttle=pad_state.throttle,
            compressor=pad_state.compressor,
            cathode_pulse=pad_state.cathode_pulse,
            h2_sccm=float(inj["h2_sccm"]),
            laser_ablation_hz=float(inj["laser_ablation_hz"]),
            b11_target_index=int(inj.get("b11_target_index", 0)),
        ),
        pad=pad_state,
        unobtanium=UnobtaniumParams(
            field_emission_margin=float(u.get("field_emission_margin", 1.0)),
            max_wall_heat_flux_W_m2=float(u.get("max_wall_heat_flux_W_m2", 2.0e6)),
            ch4_cooling_effectiveness=float(u.get("ch4_cooling_effectiveness", 1.0)),
            hts_capability_scale=float(u.get("hts_capability_scale", 1.0)),
            fusion_reactivity_scale=float(u.get("fusion_reactivity_scale", 1.0)),
            beam_coupling_scale=float(u.get("beam_coupling_scale", 1.0)),
        ),
        scales=PlantScales(
            target_gross_power_mw=float(scales.get("target_gross_power_mw", 3.5)),
            jet_propulsive_efficiency=float(scales.get("jet_propulsive_efficiency", 0.55)),
            heat_kw_at_full=float(scales.get("heat_kw_at_full", 400.0)),
            beam_screen_kw_per_ma=float(scales.get("beam_screen_kw_per_ma", 0.6)),
            thrust_lbf_at_full=float(scales.get("thrust_lbf_at_full", 4040.0)),
            mass_flow_kgps_at_full=float(scales.get("mass_flow_kgps_at_full", 84.0)),
            density_log10_at_full=float(scales.get("density_log10_at_full", 11.0)),
        ),
    )
