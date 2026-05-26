"""Template id → CadQuery geometry builders (params from YAML only; no layout constants here)."""

from __future__ import annotations

from typing import Any, Callable

import cadquery as cq

from arcjet_test_stand_cad import (
    bay_inlet_annulus_shroud,
    bd_annulus_sleeve,
    bd_bracket_seal_flange,
    bd_shock_core_insert,
    bellmouth_flare,
    blast_detuner,
    compressor_bleed_port,
    compressor_housing,
    turbine_housing,
    pad_starter_motor_pod,
    pad_startup_cart,
    pad_startup_cable_params,
    pad_startup_connector_anchors,
    lab_fuel_feed_valve,
    engine_mount_frame,
    load_cell_puck,
    nozzle_cd_contour,
    nozzle_exit_hardware,
    nozzle_inlet_plenum,
    nozzle_stub,
    rail_beam,
    thrust_sled_frame,
)
from full_reactor_cad import (
    IntegratedOrbitronTube,
    LabInfrastructure,
    build_magnet_feedthrough_bosses,
    fusion_exhaust_outlet_ring,
    lab_b10h14_injectant_trunk_params,
    lab_b2h6_injectant_trunk_params,
    lab_h2_injectant_trunk_params,
    lab_helium_ash_vent_params,
)

from yaml_assembly.connector_routing import build_connector_routing


def _tube() -> tuple[cq.Workplane, ...]:
    return IntegratedOrbitronTube().build()


def tpl_bellmouth_flare(**params: Any) -> cq.Workplane:
    return bellmouth_flare(
        inlet_r=float(params.get("inlet_r", 0.18)),
        throat_r=float(params.get("throat_r", 0.05)),
        length=float(params.get("length", 0.35)),
    )


def tpl_compressor_housing(**params: Any) -> cq.Workplane:
    return compressor_housing(
        od=float(params.get("od", 0.14)),
        length=float(params.get("length", 0.25)),
    )


def tpl_compressor_bleed_port(**params: Any) -> cq.Workplane:
    return compressor_bleed_port(
        housing_od=float(params.get("housing_od", 0.16)),
        port_od=float(params.get("port_od", 0.045)),
        port_length=float(params.get("port_length", 0.08)),
    )


def tpl_turbine_housing(**params: Any) -> cq.Workplane:
    return turbine_housing(
        od=float(params.get("od", 0.16)),
        length=float(params.get("length", 0.18)),
    )


def tpl_pad_starter_motor(**params: Any) -> cq.Workplane:
    return pad_starter_motor_pod(
        motor_length=float(params.get("motor_length", 0.14)),
        motor_od=float(params.get("motor_od", 0.10)),
        shaft_radius=float(params.get("shaft_radius", 0.02)),
        shaft_length=float(params.get("shaft_length", 0.07)),
    )


def tpl_pad_startup_cart(**params: Any) -> cq.Workplane:
    return pad_startup_cart(
        deck_lx=float(params.get("deck_lx", 0.58)),
        deck_ly=float(params.get("deck_ly", 0.44)),
        box_h=float(params.get("box_h", 0.38)),
    )


def tpl_lab_pad_startup_power_cable(**params: Any) -> cq.Workplane:
    merged = {**pad_startup_cable_params(), **params}
    return build_connector_routing(merged, pad_startup_connector_anchors())


def tpl_bay_inlet_annulus_shroud(**params: Any) -> cq.Workplane:
    return bay_inlet_annulus_shroud(
        x0=float(params.get("x0", -0.31)),
        length=float(params.get("length", 0.175)),
        outer_r=float(params.get("outer_r", 0.149)),
        inner_r=float(params.get("inner_r", 0.088)),
    )


def tpl_nozzle_stub(**params: Any) -> cq.Workplane:
    return nozzle_stub(
        throat_r=float(params.get("throat_r", 0.045)),
        exit_r=float(params.get("exit_r", 0.09)),
        length=float(params.get("length", 0.2)),
    )


def tpl_blast_detuner(**params: Any) -> cq.Workplane:
    return blast_detuner(
        inner_r=float(params.get("inner_r", 0.35)),
        wall=float(params.get("wall", 0.04)),
        length=float(params.get("length", 2.0)),
    )


def tpl_nozzle_inlet_plenum(**params: Any) -> cq.Workplane:
    return nozzle_inlet_plenum(
        inlet_r=float(params.get("inlet_r", 0.056)),
        mid_r=float(params.get("mid_r", 0.048)),
        length=float(params.get("length", 0.07)),
    )


def tpl_nozzle_cd_contour(**params: Any) -> cq.Workplane:
    return nozzle_cd_contour(
        r0=float(params.get("r0", 0.048)),
        throat_r=float(params.get("throat_r", 0.045)),
        length=float(params.get("length", 0.05)),
    )


def tpl_nozzle_exit_hardware(**params: Any) -> cq.Workplane:
    return nozzle_exit_hardware(
        throat_r=float(params.get("throat_r", 0.045)),
        exit_r=float(params.get("exit_r", 0.09)),
        length=float(params.get("length", 0.08)),
    )


def tpl_bd_annulus_sleeve(**params: Any) -> cq.Workplane:
    return bd_annulus_sleeve(
        inner_flow_r=float(params.get("inner_flow_r", 0.34)),
        annulus_gap=float(params.get("annulus_gap", 0.048)),
        wall=float(params.get("wall", 0.042)),
        length=float(params.get("length", 0.75)),
    )


def tpl_bd_shock_core_insert(**params: Any) -> cq.Workplane:
    return bd_shock_core_insert(
        radius=float(params.get("radius", 0.29)),
        length=float(params.get("length", 0.9)),
    )


def tpl_bd_bracket_seal_flange(**params: Any) -> cq.Workplane:
    return bd_bracket_seal_flange(
        outer_r=float(params.get("outer_r", 0.42)),
        inner_r=float(params.get("inner_r", 0.33)),
        thickness=float(params.get("thickness", 0.06)),
        n_bolts=int(params.get("n_bolts", 8)),
    )


def tpl_lab_fuel_feed_valve(**params: Any) -> cq.Workplane:
    return lab_fuel_feed_valve(
        body_r=float(params.get("body_r", 0.045)),
        stem_r=float(params.get("stem_r", 0.018)),
        stem_h=float(params.get("stem_h", 0.055)),
    )


def tpl_orbitron_exhaust_outlet_ring(**params: Any) -> cq.Workplane:
    return fusion_exhaust_outlet_ring(
        outer_r=float(params.get("outer_r", 0.082)),
        inner_r=float(params.get("inner_r", 0.055)),
        thickness=float(params.get("thickness", 0.016)),
    )


def tpl_thrust_sled_frame(**params: Any) -> cq.Workplane:
    return thrust_sled_frame(
        length=float(params.get("length", 2.2)),
        width=float(params.get("width", 1.0)),
        rail_h=float(params.get("rail_h", 0.08)),
    )


def tpl_rail_beam(**params: Any) -> cq.Workplane:
    return rail_beam(span=float(params.get("span", 3.5)))


def tpl_load_cell_puck(**params: Any) -> cq.Workplane:
    return load_cell_puck()


def tpl_engine_mount_frame(**params: Any) -> cq.Workplane:
    return engine_mount_frame(**params)


def tpl_orbitron_anode(**_: Any) -> cq.Workplane:
    a, *_ = _tube()
    return a


def tpl_orbitron_cathode(**_: Any) -> cq.Workplane:
    return _tube()[1]


def tpl_orbitron_insulators(**_: Any) -> cq.Workplane:
    return _tube()[2]


def tpl_orbitron_magnet(**_: Any) -> cq.Workplane:
    return _tube()[3]


def tpl_orbitron_nbi(**_: Any) -> cq.Workplane:
    return _tube()[4]


def _infra() -> LabInfrastructure:
    return LabInfrastructure()


def tpl_lab_tank_hydrogen(**_: Any) -> cq.Workplane:
    h2, *_ = _infra().build_fuel_farm()
    return h2


def tpl_lab_tank_deuterium(**_: Any) -> cq.Workplane:
    return tpl_lab_tank_hydrogen()


def tpl_lab_tank_decaborane(**_: Any) -> cq.Workplane:
    _, b10, *_ = _infra().build_fuel_farm()
    return b10


def tpl_lab_tank_diborane(**_: Any) -> cq.Workplane:
    return tpl_lab_tank_decaborane()


def tpl_lab_tank_cryo_methane(**_: Any) -> cq.Workplane:
    _, _, d, *_ = _infra().build_fuel_farm()
    return d


def tpl_lab_tank_farm_platform(**_: Any) -> cq.Workplane:
    return _infra().build_tank_farm_platform()


def tpl_lab_decal_h2(**_: Any) -> cq.Workplane:
    return _infra().build_fuel_farm()[3]


def tpl_lab_decal_d2(**_: Any) -> cq.Workplane:
    return tpl_lab_decal_h2()


def tpl_lab_decal_b10h14(**_: Any) -> cq.Workplane:
    return _infra().build_fuel_farm()[4]


def tpl_lab_decal_b2h6(**_: Any) -> cq.Workplane:
    return tpl_lab_decal_b10h14()


def tpl_lab_decal_ch4(**_: Any) -> cq.Workplane:
    return _infra().build_fuel_farm()[5]


def tpl_lab_hv_umbilical(**params: Any) -> cq.Workplane:
    if params.get("connector_ports") and params.get("connector_links"):
        anchors = LabInfrastructure().hv_connector_anchors()
        return build_connector_routing(params, anchors)
    hv, _, _ = _infra().build_rigid_plumbing()
    return hv


def tpl_lab_fuel_gas_lines(**params: Any) -> cq.Workplane:
    if params.get("connector_ports") and params.get("connector_links"):
        anchors = LabInfrastructure().fuel_line_connector_anchors()
        return build_connector_routing(params, anchors)
    _, gas, _ = _infra().build_rigid_plumbing()
    return gas


def tpl_lab_h2_injectant_trunk(**params: Any) -> cq.Workplane:
    anchors = LabInfrastructure().fuel_line_connector_anchors()
    merged = {**lab_h2_injectant_trunk_params(), **params}
    return build_connector_routing(merged, anchors)


def tpl_lab_d2_injectant_trunk(**params: Any) -> cq.Workplane:
    anchors = LabInfrastructure().fuel_line_connector_anchors()
    merged = {**lab_d2_injectant_trunk_params(), **params}
    return build_connector_routing(merged, anchors)


def tpl_lab_b10h14_injectant_trunk(**params: Any) -> cq.Workplane:
    anchors = LabInfrastructure().fuel_line_connector_anchors()
    merged = {**lab_b10h14_injectant_trunk_params(), **params}
    return build_connector_routing(merged, anchors)


def tpl_lab_b2h6_injectant_trunk(**params: Any) -> cq.Workplane:
    return tpl_lab_b10h14_injectant_trunk(**params)


def tpl_lab_laser_ablation_head(**_: Any) -> cq.Workplane:
    return _infra().build_laser_ablation_head()


def tpl_lab_uv_fused_silica_viewport(**_: Any) -> cq.Workplane:
    return _infra().build_uv_fused_silica_viewport()


def tpl_lab_b11_ablation_target(**_: Any) -> cq.Workplane:
    return _infra().build_b11_ablation_target()


def tpl_lab_decaborane_heater_mantle(**_: Any) -> cq.Workplane:
    """Heating collar on the solid B₁₀H₁₄ reservoir (sublimation assist)."""
    return (
        cq.Workplane("XY")
        .rect(0.34, 0.28)
        .extrude(0.06)
        .translate((0.0, 1.2, 0.54))
    )


def tpl_lab_helium_ash_vent(**params: Any) -> cq.Workplane:
    anchors = LabInfrastructure().fusion_exhaust_connector_anchors()
    merged = {**lab_helium_ash_vent_params(), **params}
    return build_connector_routing(merged, anchors)


def tpl_lab_cryo_methane_piping(**params: Any) -> cq.Workplane:
    if params.get("connector_ports") and params.get("connector_links"):
        anchors = LabInfrastructure().cryo_methane_connector_anchors()
        return build_connector_routing(params, anchors)
    _, _, meth = _infra().build_rigid_plumbing()
    return meth


def tpl_lab_operator_console_desk(**_: Any) -> cq.Workplane:
    d, _, _, _, _, _ = _infra().build_console()
    return d


def tpl_lab_operator_panel(**_: Any) -> cq.Workplane:
    return _infra().build_operator_panel()


def tpl_lab_operator_screen(**_: Any) -> cq.Workplane:
    _, s, _, _, _, _ = _infra().build_console()
    return s


def tpl_lab_big_red_button(**_: Any) -> cq.Workplane:
    return _infra().build_ignite_button()


def tpl_lab_operator_checklist_plaque(**_: Any) -> cq.Workplane:
    return _infra().build_operator_checklist_plaque()


def tpl_lab_operator_checklist_ink(**_: Any) -> cq.Workplane:
    return _infra().build_operator_checklist_ink()


def tpl_lab_panel_switch_apu(**_: Any) -> cq.Workplane:
    _, _, _, sw, _, _ = _infra().build_console()
    return sw


def tpl_lab_panel_switch_starter(**_: Any) -> cq.Workplane:
    _, _, _, _, sw, _ = _infra().build_console()
    return sw


def tpl_lab_panel_switch_bleed(**_: Any) -> cq.Workplane:
    _, _, _, _, _, sw = _infra().build_console()
    return sw


def tpl_lab_panel_label_apu(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[0]


def tpl_lab_panel_label_starter(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[1]


def tpl_lab_panel_label_bleed(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[2]


def tpl_lab_panel_label_ignite(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[6]


def tpl_lab_panel_label_beam(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[7]


def tpl_lab_panel_label_comp(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[8]


def tpl_lab_panel_label_vac(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[3]


def tpl_lab_panel_label_laser(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[4]


def tpl_lab_panel_label_hv(**_: Any) -> cq.Workplane:
    return _infra().build_panel_labels()[5]


def tpl_lab_magnet_feedthrough_bosses(**_: Any) -> cq.Workplane:
    """Solenoid OD bosses for CH₄ process, cryo thermal, and HV feedthrough (world-space)."""
    return build_magnet_feedthrough_bosses()


TEMPLATE_REGISTRY: dict[str, Callable[..., cq.Workplane]] = {
    "bellmouth_flare": tpl_bellmouth_flare,
    "compressor_housing": tpl_compressor_housing,
    "compressor_bleed_port": tpl_compressor_bleed_port,
    "turbine_housing": tpl_turbine_housing,
    "pad_starter_motor": tpl_pad_starter_motor,
    "pad_startup_cart": tpl_pad_startup_cart,
    "lab_pad_startup_power_cable": tpl_lab_pad_startup_power_cable,
    "bay_inlet_annulus_shroud": tpl_bay_inlet_annulus_shroud,
    "nozzle_stub": tpl_nozzle_stub,
    "nozzle_inlet_plenum": tpl_nozzle_inlet_plenum,
    "nozzle_cd_contour": tpl_nozzle_cd_contour,
    "nozzle_exit_hardware": tpl_nozzle_exit_hardware,
    "blast_detuner": tpl_blast_detuner,
    "bd_annulus_sleeve": tpl_bd_annulus_sleeve,
    "bd_shock_core_insert": tpl_bd_shock_core_insert,
    "bd_bracket_seal_flange": tpl_bd_bracket_seal_flange,
    "lab_fuel_feed_valve": tpl_lab_fuel_feed_valve,
    "orbitron_exhaust_outlet_ring": tpl_orbitron_exhaust_outlet_ring,
    "thrust_sled_frame": tpl_thrust_sled_frame,
    "rail_beam": tpl_rail_beam,
    "load_cell_puck": tpl_load_cell_puck,
    "engine_mount_frame": tpl_engine_mount_frame,
    "orbitron_anode": tpl_orbitron_anode,
    "orbitron_cathode": tpl_orbitron_cathode,
    "orbitron_insulators": tpl_orbitron_insulators,
    "orbitron_magnet": tpl_orbitron_magnet,
    "lab_magnet_feedthrough_bosses": tpl_lab_magnet_feedthrough_bosses,
    "orbitron_nbi": tpl_orbitron_nbi,
    "lab_tank_hydrogen": tpl_lab_tank_hydrogen,
    "lab_tank_deuterium": tpl_lab_tank_deuterium,
    "lab_tank_decaborane": tpl_lab_tank_decaborane,
    "lab_tank_diborane": tpl_lab_tank_diborane,
    "lab_tank_cryo_methane": tpl_lab_tank_cryo_methane,
    "lab_tank_farm_platform": tpl_lab_tank_farm_platform,
    "lab_decal_h2": tpl_lab_decal_h2,
    "lab_decal_d2": tpl_lab_decal_d2,
    "lab_decal_b10h14": tpl_lab_decal_b10h14,
    "lab_decal_b2h6": tpl_lab_decal_b2h6,
    "lab_decal_ch4": tpl_lab_decal_ch4,
    "lab_hv_umbilical": tpl_lab_hv_umbilical,
    "lab_fuel_gas_lines": tpl_lab_fuel_gas_lines,
    "lab_h2_injectant_trunk": tpl_lab_h2_injectant_trunk,
    "lab_d2_injectant_trunk": tpl_lab_d2_injectant_trunk,
    "lab_b10h14_injectant_trunk": tpl_lab_b10h14_injectant_trunk,
    "lab_b2h6_injectant_trunk": tpl_lab_b2h6_injectant_trunk,
    "lab_laser_ablation_head": tpl_lab_laser_ablation_head,
    "lab_uv_fused_silica_viewport": tpl_lab_uv_fused_silica_viewport,
    "lab_b11_ablation_target": tpl_lab_b11_ablation_target,
    "lab_decaborane_heater_mantle": tpl_lab_decaborane_heater_mantle,
    "lab_helium_ash_vent": tpl_lab_helium_ash_vent,
    "lab_cryo_methane_piping": tpl_lab_cryo_methane_piping,
    "lab_operator_console_desk": tpl_lab_operator_console_desk,
    "lab_operator_panel": tpl_lab_operator_panel,
    "lab_operator_screen": tpl_lab_operator_screen,
    "lab_big_red_button": tpl_lab_big_red_button,
    "lab_operator_checklist_plaque": tpl_lab_operator_checklist_plaque,
    "lab_operator_checklist_ink": tpl_lab_operator_checklist_ink,
    "lab_panel_switch_apu": tpl_lab_panel_switch_apu,
    "lab_panel_switch_starter": tpl_lab_panel_switch_starter,
    "lab_panel_switch_bleed": tpl_lab_panel_switch_bleed,
    "lab_panel_label_apu": tpl_lab_panel_label_apu,
    "lab_panel_label_starter": tpl_lab_panel_label_starter,
    "lab_panel_label_bleed": tpl_lab_panel_label_bleed,
    "lab_panel_label_ignite": tpl_lab_panel_label_ignite,
    "lab_panel_label_beam": tpl_lab_panel_label_beam,
    "lab_panel_label_comp": tpl_lab_panel_label_comp,
    "lab_panel_label_vac": tpl_lab_panel_label_vac,
    "lab_panel_label_laser": tpl_lab_panel_label_laser,
    "lab_panel_label_hv": tpl_lab_panel_label_hv,
}


def _register_reply19_templates() -> None:
    from reply19_parts_cad import (
        part_aerodynamic_centerbody,
        part_airflow_honeycomb_filter,
        part_ballast_resistor,
        part_charged_particle_detector,
        part_compressor_assembly,
        part_compressor_shaft_bearings,
        part_containment_vessel_jacket,
        part_data_acquisition_chassis,
        part_exhaust_silencer_ducting,
        part_faraday_cup,
        part_full_range_vacuum_gauge,
        part_heat_exchanger_channels,
        part_high_temp_metallic_seals,
        part_high_temp_thermocouples,
        part_high_voltage_cable,
        part_hv_bushing_feedthrough,
        part_hv_vacuum_feedthrough,
        part_industrial_blower,
        part_infrared_pyrometer,
        part_inlet_guide_vanes_igvs,
        part_interlock_safety_controller,
        part_kinematic_mirror_mounts,
        part_laser_power_meter,
        part_mass_flow_sensor,
        part_multichannel_analyzer_mca,
        part_optical_breadboard,
        part_pitot_static_tubes,
        part_pneumatic_air_starter,
        part_precision_dc_hvps,
        part_preamplifier,
        part_q_switched_ndyag_laser,
        part_roughing_pump,
        part_s_duct_intake_simulation,
        part_solid_b11_target_holder,
        part_solid_boron_11_target,
        part_spectroscopy_amplifier,
        part_solid_state_marx_generator,
        part_tank_cryo_methane,
        part_tank_hydrogen,
        part_turbine_assembly,
        part_turbomolecular_pump,
        part_uv_focusing_lens,
        part_uv_fused_silica_viewport,
        part_vacuum_chamber,
        part_vacuum_turbo_pump_array,
        part_central_cathode_wire,
        part_outer_anode_grid,
    )

    pairs = [
        ("reply19_vacuum_chamber", part_vacuum_chamber),
        ("reply19_turbomolecular_pump", part_turbomolecular_pump),
        ("reply19_roughing_pump", part_roughing_pump),
        ("reply19_full_range_vacuum_gauge", part_full_range_vacuum_gauge),
        ("reply19_uv_fused_silica_viewport", part_uv_fused_silica_viewport),
        ("reply19_solid_b11_target_holder", part_solid_b11_target_holder),
        ("reply19_central_cathode_wire", part_central_cathode_wire),
        ("reply19_outer_anode_grid", part_outer_anode_grid),
        ("reply19_hv_vacuum_feedthrough", part_hv_vacuum_feedthrough),
        ("reply19_solid_boron_11_target", part_solid_boron_11_target),
        ("reply19_q_switched_ndyag_laser", part_q_switched_ndyag_laser),
        ("reply19_optical_breadboard", part_optical_breadboard),
        ("reply19_uv_focusing_lens", part_uv_focusing_lens),
        ("reply19_laser_power_meter", part_laser_power_meter),
        ("reply19_kinematic_mirror_mounts", part_kinematic_mirror_mounts),
        ("reply19_precision_dc_hvps", part_precision_dc_hvps),
        ("reply19_high_voltage_cable", part_high_voltage_cable),
        ("reply19_ballast_resistor", part_ballast_resistor),
        ("reply19_interlock_safety_controller", part_interlock_safety_controller),
        ("reply19_charged_particle_detector", part_charged_particle_detector),
        ("reply19_preamplifier", part_preamplifier),
        ("reply19_spectroscopy_amplifier", part_spectroscopy_amplifier),
        ("reply19_multichannel_analyzer_mca", part_multichannel_analyzer_mca),
        ("reply19_faraday_cup", part_faraday_cup),
        ("reply19_containment_vessel_jacket", part_containment_vessel_jacket),
        ("reply19_heat_exchanger_channels", part_heat_exchanger_channels),
        ("reply19_aerodynamic_centerbody", part_aerodynamic_centerbody),
        ("reply19_high_temp_metallic_seals", part_high_temp_metallic_seals),
        ("reply19_compressor_assembly", part_compressor_assembly),
        ("reply19_turbine_assembly", part_turbine_assembly),
        ("reply19_compressor_shaft_bearings", part_compressor_shaft_bearings),
        ("reply19_inlet_guide_vanes_igvs", part_inlet_guide_vanes_igvs),
        ("reply19_industrial_blower", part_industrial_blower),
        ("reply19_s_duct_intake_simulation", part_s_duct_intake_simulation),
        ("reply19_exhaust_silencer_ducting", part_exhaust_silencer_ducting),
        ("reply19_airflow_honeycomb_filter", part_airflow_honeycomb_filter),
        ("reply19_pneumatic_air_starter", part_pneumatic_air_starter),
        ("reply19_solid_state_marx_generator", part_solid_state_marx_generator),
        ("reply19_hv_bushing_feedthrough", part_hv_bushing_feedthrough),
        ("reply19_vacuum_turbo_pump_array", part_vacuum_turbo_pump_array),
        ("reply19_high_temp_thermocouples", part_high_temp_thermocouples),
        ("reply19_pitot_static_tubes", part_pitot_static_tubes),
        ("reply19_mass_flow_sensor", part_mass_flow_sensor),
        ("reply19_infrared_pyrometer", part_infrared_pyrometer),
        ("reply19_data_acquisition_chassis", part_data_acquisition_chassis),
        ("reply19_tank_hydrogen", part_tank_hydrogen),
        ("reply19_tank_cryo_methane", part_tank_cryo_methane),
    ]
    for tid, fn in pairs:

        def _wrap(f: Callable[..., cq.Workplane] = fn, **_kw: Any) -> cq.Workplane:
            return f()

        TEMPLATE_REGISTRY[tid] = _wrap


_register_reply19_templates()


def build_template(template_id: str, params: dict[str, Any] | None) -> cq.Workplane:
    fn = TEMPLATE_REGISTRY.get(template_id)
    if fn is None:
        keys = ", ".join(sorted(TEMPLATE_REGISTRY))
        raise KeyError(f"Unknown template {template_id!r}. Known: {keys}")
    return fn(**(params or {}))
