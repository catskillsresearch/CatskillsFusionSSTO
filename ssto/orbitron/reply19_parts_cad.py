"""
CadQuery surrogates for every part in proton_boron_rand.md Reply 18–19 (Phase 1 & 2).

Part slugs match YAML ``instances`` keys and glTF node names. Geometry is schematic
(bench-scale proxies), not procurement drawings.
"""
from __future__ import annotations

import cadquery as cq


def _box(lx: float, ly: float, lz: float, xyz: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").box(lx, ly, lz).translate(xyz)


def _cyl(r: float, h: float, xyz: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").circle(r).extrude(h).translate(xyz)


# --- Subassembly 1.1: Vacuum & Chamber System ---


def part_vacuum_chamber() -> cq.Workplane:
    body = _cyl(0.22, 0.18, (0.0, 2.0, 0.12))
    port = _cyl(0.04, 0.06, (0.18, 2.0, 0.22))
    return body.union(port)


def part_turbomolecular_pump() -> cq.Workplane:
    return _cyl(0.09, 0.14, (-0.35, 2.0, 0.05))


def part_roughing_pump() -> cq.Workplane:
    return _box(0.22, 0.18, 0.16, (-0.65, 2.0, 0.0))


def part_full_range_vacuum_gauge() -> cq.Workplane:
    return _box(0.08, 0.06, 0.12, (-0.15, 2.35, 0.35))


def part_uv_fused_silica_viewport() -> cq.Workplane:
    return _cyl(0.028, 0.012, (0.05, 2.0, 0.28))


def part_solid_b11_target_holder() -> cq.Workplane:
    stem = _cyl(0.012, 0.08, (0.0, 2.0, 0.32))
    stage = _cyl(0.04, 0.01, (0.0, 2.0, 0.40))
    return stem.union(stage)


# --- Subassembly 1.2: Electrostatic Orbitron Core ---


def part_central_cathode_wire() -> cq.Workplane:
    return cq.Workplane("XY").circle(0.0025).extrude(0.35).translate((0.0, 0.0, 0.75))


def part_outer_anode_grid() -> cq.Workplane:
    return _cyl(0.05, 0.32, (0.0, 0.0, 0.75))


def part_hv_vacuum_feedthrough() -> cq.Workplane:
    ceramic = _cyl(0.035, 0.06, (-0.42, 2.0, 0.18))
    pin = _cyl(0.008, 0.12, (-0.42, 2.0, 0.24))
    return ceramic.union(pin)


def part_solid_boron_11_target() -> cq.Workplane:
    return _cyl(0.025, 0.006, (0.02, 2.0, 0.41))


# --- Subassembly 1.3: Laser Ablation System ---


def part_q_switched_ndyag_laser() -> cq.Workplane:
    return _box(0.42, 0.18, 0.14, (0.72, 0.55, 0.38))


def part_optical_breadboard() -> cq.Workplane:
    return _box(0.9, 0.6, 0.025, (0.55, 0.2, 0.72))


def part_uv_focusing_lens() -> cq.Workplane:
    return _cyl(0.02, 0.015, (0.38, 0.55, 0.38))


def part_laser_power_meter() -> cq.Workplane:
    return _box(0.12, 0.08, 0.05, (0.25, 0.55, 0.82))


def part_kinematic_mirror_mounts() -> cq.Workplane:
    m1 = _box(0.04, 0.04, 0.06, (0.45, 0.35, 0.78))
    m2 = _box(0.04, 0.04, 0.06, (0.55, 0.45, 0.78))
    return m1.union(m2)


# --- Subassembly 1.4: High-Voltage Power & Safety ---


def part_precision_dc_hvps() -> cq.Workplane:
    return _box(0.28, 0.22, 0.18, (-1.1, 2.0, 0.0))


def part_high_voltage_cable() -> cq.Workplane:
    return cq.Workplane("XY").circle(0.012).extrude(0.55).translate((-0.75, 2.0, 0.22))


def part_ballast_resistor() -> cq.Workplane:
    return _box(0.06, 0.03, 0.03, (-0.55, 2.15, 0.30))


def part_interlock_safety_controller() -> cq.Workplane:
    return _box(0.18, 0.12, 0.08, (-1.1, 2.35, 0.0))


# --- Subassembly 1.5: Diagnostics & Particle Detection ---


def part_charged_particle_detector() -> cq.Workplane:
    d1 = _box(0.05, 0.05, 0.02, (0.35, 2.25, 0.15))
    d2 = _box(0.05, 0.05, 0.02, (0.35, 2.35, 0.15))
    return d1.union(d2)


def part_preamplifier() -> cq.Workplane:
    return _box(0.1, 0.06, 0.04, (0.5, 2.3, 0.12))


def part_spectroscopy_amplifier() -> cq.Workplane:
    return _box(0.14, 0.08, 0.06, (0.65, 2.3, 0.12))


def part_multichannel_analyzer_mca() -> cq.Workplane:
    return _box(0.2, 0.14, 0.05, (0.82, 2.3, 0.12))


def part_faraday_cup() -> cq.Workplane:
    return _cyl(0.03, 0.05, (0.2, 2.2, 0.18))


# --- Subassembly 2.1: Full-Scale Engine Core & Heat Exchanger ---


def part_containment_vessel_jacket() -> cq.Workplane:
    return _cyl(0.12, 0.45, (0.0, 0.0, 0.75))


def part_heat_exchanger_channels() -> cq.Workplane:
    return _cyl(0.105, 0.38, (0.0, 0.0, 0.76))


def part_aerodynamic_centerbody() -> cq.Workplane:
    return _cyl(0.04, 0.5, (0.0, 0.0, 0.78))


def part_high_temp_metallic_seals() -> cq.Workplane:
    import math

    s = cq.Workplane("XY")
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        s = s.union(_cyl(0.008, 0.012, (0.11 * math.cos(rad), 0.11 * math.sin(rad), 0.72)))
    return s


# --- Subassembly 2.2: Turbomachinery ---


def part_compressor_assembly() -> cq.Workplane:
    return _cyl(0.14, 0.22, (-0.55, 0.0, 0.75))


def part_turbine_assembly() -> cq.Workplane:
    return _cyl(0.13, 0.18, (0.55, 0.0, 0.75))


def part_compressor_shaft_bearings() -> cq.Workplane:
    return _cyl(0.025, 0.65, (0.0, 0.0, 0.75))


def part_inlet_guide_vanes_igvs() -> cq.Workplane:
    return _box(0.28, 0.08, 0.04, (-0.38, 0.0, 0.75))


# --- Subassembly 2.3: Ground Support Blower ---


def part_industrial_blower() -> cq.Workplane:
    return _box(0.55, 0.45, 0.4, (-1.8, -1.2, 0.0))


def part_s_duct_intake_simulation() -> cq.Workplane:
    return _box(0.35, 0.25, 0.5, (-1.2, 0.0, 0.85))


def part_exhaust_silencer_ducting() -> cq.Workplane:
    return _cyl(0.16, 0.35, (1.2, 0.0, 0.75))


def part_airflow_honeycomb_filter() -> cq.Workplane:
    return _box(0.32, 0.32, 0.06, (-1.45, 0.0, 0.72))


# --- Subassembly 2.4: Megawatt-Scale Power & Starting ---


def part_pneumatic_air_starter() -> cq.Workplane:
    return _cyl(0.06, 0.1, (-0.45, -0.25, 0.78))


def part_solid_state_marx_generator() -> cq.Workplane:
    return _box(0.5, 0.35, 0.28, (-1.5, 2.0, 0.0))


def part_hv_bushing_feedthrough() -> cq.Workplane:
    return _cyl(0.05, 0.1, (0.0, 0.0, 0.95))


def part_vacuum_turbo_pump_array() -> cq.Workplane:
    p = cq.Workplane("XY")
    for dx in (-0.12, 0.0, 0.12):
        p = p.union(_cyl(0.05, 0.12, (dx - 0.35, 2.0, 0.02)))
    return p


# --- Subassembly 2.5: Instrumentation ---


def part_high_temp_thermocouples() -> cq.Workplane:
    return _box(0.04, 0.04, 0.08, (0.14, 0.0, 0.92))


def part_pitot_static_tubes() -> cq.Workplane:
    t1 = _cyl(0.006, 0.2, (-0.2, 0.08, 0.9))
    t2 = _cyl(0.006, 0.2, (-0.2, -0.08, 0.9))
    return t1.union(t2)


def part_mass_flow_sensor() -> cq.Workplane:
    return _box(0.1, 0.08, 0.06, (-0.55, 0.15, 0.55))


def part_infrared_pyrometer() -> cq.Workplane:
    return _box(0.06, 0.05, 0.05, (0.18, 0.12, 0.95))


def part_data_acquisition_chassis() -> cq.Workplane:
    return _box(0.35, 0.22, 0.08, (1.0, 2.2, 0.0))


# --- Integrated lab extensions (proton inventory + wall thermal) ---


def part_tank_hydrogen() -> cq.Workplane:
    return _cyl(0.15, 1.2, (0.6, 1.2, 0)).edges(">Z").fillet(0.1)


def part_tank_cryo_methane() -> cq.Workplane:
    return _cyl(0.25, 0.9, (-0.7, 1.2, 0)).edges(">Z").fillet(0.1)


REPLY19_TEMPLATE_SLUGS: dict[str, str] = {
    "Vacuum_Chamber": "reply19_vacuum_chamber",
    "Turbomolecular_Pump": "reply19_turbomolecular_pump",
    "Roughing_Pump": "reply19_roughing_pump",
    "Full_Range_Vacuum_Gauge": "reply19_full_range_vacuum_gauge",
    "UV_Fused_Silica_Viewport": "reply19_uv_fused_silica_viewport",
    "Solid_B11_Target_Holder": "reply19_solid_b11_target_holder",
    "Central_Cathode_Wire": "reply19_central_cathode_wire",
    "Outer_Anode_Grid": "reply19_outer_anode_grid",
    "HV_Vacuum_Feedthrough": "reply19_hv_vacuum_feedthrough",
    "Solid_Boron_11_Target": "reply19_solid_boron_11_target",
    "Solid_Boron_11_Target_2": "reply19_solid_boron_11_target",
    "Q_Switched_NdYAG_Laser": "reply19_q_switched_ndyag_laser",
    "Optical_Breadboard": "reply19_optical_breadboard",
    "UV_Focusing_Lens": "reply19_uv_focusing_lens",
    "Laser_Power_Meter": "reply19_laser_power_meter",
    "Kinematic_Mirror_Mounts": "reply19_kinematic_mirror_mounts",
    "Precision_DC_HVPS": "reply19_precision_dc_hvps",
    "High_Voltage_Cable": "reply19_high_voltage_cable",
    "Ballast_Resistor": "reply19_ballast_resistor",
    "Interlock_Safety_Controller": "reply19_interlock_safety_controller",
    "Charged_Particle_Detector": "reply19_charged_particle_detector",
    "Preamplifier": "reply19_preamplifier",
    "Spectroscopy_Amplifier": "reply19_spectroscopy_amplifier",
    "Multichannel_Analyzer_MCA": "reply19_multichannel_analyzer_mca",
    "Faraday_Cup": "reply19_faraday_cup",
    "Containment_Vessel_Jacket": "reply19_containment_vessel_jacket",
    "Heat_Exchanger_Channels": "reply19_heat_exchanger_channels",
    "Aerodynamic_Centerbody": "reply19_aerodynamic_centerbody",
    "High_Temp_Metallic_Seals": "reply19_high_temp_metallic_seals",
    "Compressor_Assembly": "reply19_compressor_assembly",
    "Turbine_Assembly": "reply19_turbine_assembly",
    "Compressor_Shaft_Bearings": "reply19_compressor_shaft_bearings",
    "Inlet_Guide_Vanes_IGVs": "reply19_inlet_guide_vanes_igvs",
    "Industrial_Blower": "reply19_industrial_blower",
    "S_Duct_Intake_Simulation": "reply19_s_duct_intake_simulation",
    "Exhaust_Silencer_Ducting": "reply19_exhaust_silencer_ducting",
    "Airflow_Honeycomb_Filter": "reply19_airflow_honeycomb_filter",
    "Pneumatic_Air_Starter": "reply19_pneumatic_air_starter",
    "Solid_State_Marx_Generator": "reply19_solid_state_marx_generator",
    "HV_Bushing_Feedthrough": "reply19_hv_bushing_feedthrough",
    "Vacuum_Turbo_Pump_Array": "reply19_vacuum_turbo_pump_array",
    "High_Temp_Thermocouples": "reply19_high_temp_thermocouples",
    "Pitot_Static_Tubes": "reply19_pitot_static_tubes",
    "Mass_Flow_Sensor": "reply19_mass_flow_sensor",
    "Infrared_Pyrometer": "reply19_infrared_pyrometer",
    "Data_Acquisition_Chassis": "reply19_data_acquisition_chassis",
    "Tank_Hydrogen": "reply19_tank_hydrogen",
    "Tank_Cryo_Methane": "reply19_tank_cryo_methane",
}
