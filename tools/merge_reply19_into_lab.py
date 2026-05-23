#!/usr/bin/env python3
"""ONE-TIME dev utility — canonical lab SSOT is already orbitron_lab.yaml in git.

Normal builds use only:  ./stand.sh   (or  make all)

Re-run this script only if you revert orbitron_lab.yaml and need to re-apply Reply 19 groups/instances.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "ssto/orbitron/assembly_specs/orbitron_lab.yaml"

REPLY19_GROUPS = {
    "test_stand": {
        "title": "Orbitron R&D test stand (Reply 19 Phase 1 + 2)",
        "detail": (
            "CadQuery assembly mirrors **proton_boron_rand.md Reply 19** subassemblies. "
            "**Fuel:** solid **¹¹B** disks + **355 nm** laser ablation (Reply 9, 11–12)—not decaborane. "
            "Integrated pad adds **H₂** proton feed and **CH₄** wall-thermal (not in Phase 1 BOM)."
        ),
        "members": [
            "phase_1_benchtop",
            "phase_2_wind_tunnel",
            "integrated_pad_services",
        ],
    },
    "phase_1_benchtop": {
        "title": "Phase 1 — Benchtop physics demo",
        "detail": "Validate p-¹¹B cross-section and laminar Orbitron on laboratory scale (~$91k BOM).",
        "members": [
            "subassembly_1_1_vacuum_chamber_system",
            "subassembly_1_2_electrostatic_orbitron_core",
            "subassembly_1_3_laser_ablation_system",
            "subassembly_1_4_hv_power_safety",
            "subassembly_1_5_diagnostics_particle_detection",
        ],
    },
    "subassembly_1_1_vacuum_chamber_system": {
        "title": "Subassembly 1.1 — Vacuum & Chamber System",
        "detail": "UHV for electrostatic orbits and laser-ablation **¹¹B** injection.",
        "parts": [
            "Vacuum_Chamber",
            "Turbomolecular_Pump",
            "Roughing_Pump",
            "Full_Range_Vacuum_Gauge",
            "UV_Fused_Silica_Viewport",
            "Solid_B11_Target_Holder",
        ],
    },
    "subassembly_1_2_electrostatic_orbitron_core": {
        "title": "Subassembly 1.2 — Electrostatic Orbitron Core",
        "detail": "Electrostatic well for **H⁺** and **B⁺**; solid **¹¹B** targets on holder.",
        "parts": [
            "Central_Cathode_Wire",
            "Outer_Anode_Grid",
            "HV_Vacuum_Feedthrough",
            "Solid_Boron_11_Target",
            "Solid_Boron_11_Target_2",
            "Magnet",
            "NBI_Injector",
            "Insulators",
        ],
    },
    "subassembly_1_3_laser_ablation_system": {
        "title": "Subassembly 1.3 — Laser Ablation System",
        "detail": "Q-switched **Nd:YAG** 355 nm — cold ablation of solid **¹¹B** (Reply 11–12).",
        "parts": [
            "Q_Switched_NdYAG_Laser",
            "Optical_Breadboard",
            "UV_Focusing_Lens",
            "Laser_Power_Meter",
            "Kinematic_Mirror_Mounts",
        ],
    },
    "subassembly_1_4_hv_power_safety": {
        "title": "Subassembly 1.4 — High-Voltage Power & Safety",
        "detail": "Spellman-class DC bias, ballast, vacuum/interlock shutdown.",
        "parts": [
            "Precision_DC_HVPS",
            "High_Voltage_Cable",
            "Ballast_Resistor",
            "Interlock_Safety_Controller",
            "High_Voltage_Umbilical",
        ],
    },
    "subassembly_1_5_diagnostics_particle_detection": {
        "title": "Subassembly 1.5 — Diagnostics & Particle Detection",
        "detail": "3-alpha signature via PIPS + MCA; Faraday cup for beam current.",
        "parts": [
            "Charged_Particle_Detector",
            "Preamplifier",
            "Spectroscopy_Amplifier",
            "Multichannel_Analyzer_MCA",
            "Faraday_Cup",
        ],
    },
    "phase_2_wind_tunnel": {
        "title": "Phase 2 — Stationary wind tunnel rig",
        "detail": "Full-scale jacket, Brayton spool, ground blower, MW HV, DAQ (~$697k BOM).",
        "members": [
            "subassembly_2_1_engine_core_heat_exchanger",
            "subassembly_2_2_turbomachinery_airflow",
            "subassembly_2_3_ground_support_blower",
            "subassembly_2_4_mw_power_starting",
            "subassembly_2_5_thermal_aerodynamic_instrumentation",
            "air_breathing_nozzle_train",
        ],
    },
    "subassembly_2_1_engine_core_heat_exchanger": {
        "title": "Subassembly 2.1 — Full-Scale Engine Core & Heat Exchanger",
        "detail": "Inconel-class jacket; fusion heat to air (bremsstrahlung + alphas + CX).",
        "parts": [
            "Containment_Vessel_Jacket",
            "Heat_Exchanger_Channels",
            "Aerodynamic_Centerbody",
            "High_Temp_Metallic_Seals",
            "Reactor_Bay_Inlet_Shroud",
            "Fusion_Hot_Gas_Outlet",
        ],
    },
    "subassembly_2_2_turbomachinery_airflow": {
        "title": "Subassembly 2.2 — Turbomachinery & Air Flow Conditioning",
        "detail": "Brayton: compressor → hot jacket → turbine (Reply 15 startup sequence).",
        "parts": [
            "Compressor_Assembly",
            "Turbine_Assembly",
            "Compressor_Shaft_Bearings",
            "Inlet_Guide_Vanes_IGVs",
            "Bellmouth_Inlet",
        ],
    },
    "subassembly_2_3_ground_support_blower": {
        "title": "Subassembly 2.3 — Ground Support Blower (wind tunnel)",
        "detail": "Simulates ram-air / S-duct distortion before compressor.",
        "parts": [
            "Industrial_Blower",
            "S_Duct_Intake_Simulation",
            "Exhaust_Silencer_Ducting",
            "Airflow_Honeycomb_Filter",
        ],
    },
    "subassembly_2_4_mw_power_starting": {
        "title": "Subassembly 2.4 — Megawatt-Scale Power & Starting",
        "detail": "Pneumatic starter, Marx 600 kV class, turbo pump array, HV bushing.",
        "parts": [
            "Pneumatic_Air_Starter",
            "Solid_State_Marx_Generator",
            "HV_Bushing_Feedthrough",
            "Vacuum_Turbo_Pump_Array",
            "Pad_Startup_Cart",
            "Pad_Startup_Power_Cable",
            "Pad_Startup_Motor",
        ],
    },
    "subassembly_2_5_thermal_aerodynamic_instrumentation": {
        "title": "Subassembly 2.5 — Thermal & Aerodynamic Instrumentation",
        "detail": "PXIe DAQ, thermocouples, pitot, mass flow, pyrometers.",
        "parts": [
            "High_Temp_Thermocouples",
            "Pitot_Static_Tubes",
            "Mass_Flow_Sensor",
            "Infrared_Pyrometer",
            "Data_Acquisition_Chassis",
        ],
    },
    "air_breathing_nozzle_train": {
        "title": "Nozzle & bypass (lab segmentation)",
        "detail": "CD nozzle + blast detuner — lab mesh segments beyond Reply 19 tables.",
        "parts": [
            "Nozzle_Inlet_Plenum",
            "Nozzle_CD_Contour",
            "Nozzle_Exit_Hardware",
            "BD_Annulus_Sleeve",
            "BD_Shock_Detuner_Core",
            "BD_Bracket_Seals",
            "Helium_Ash_Vent_Line",
        ],
    },
    "integrated_pad_services": {
        "title": "Integrated pad services (extension)",
        "detail": "Operator station, thrust sled, **H₂** proton inventory, **CH₄** wall thermal.",
        "members": ["control_panel_stand", "thrust_sled", "proton_and_thermal_farm"],
    },
    "proton_and_thermal_farm": {
        "title": "Proton feed & wall-thermal farm",
        "detail": "**H₂** for p-¹¹B; **CH₄** for U2 cooling — not boron carriers.",
        "parts": [
            "Tank_Farm_Platform",
            "Tank_Hydrogen",
            "Decal_H2",
            "Pipe_H2_Feed",
            "Hydrogen_Trunk_Line",
            "Tank_Cryo_Methane",
            "Decal_CH4",
            "Pipe_CH4_Feed",
            "Cryo_Methane_Piping",
        ],
    },
    "control_panel_stand": {
        "title": "Control panel and operator station",
        "detail": "Reply 15/18 startup: APU → starter → bleed → vacuum OK → laser → HV → ignite.",
        "members": ["hv_umbilical"],
        "parts": [
            "Operator_Console",
            "Operator_Checklist_Plaque",
            "Operator_Checklist_Ink",
            "Operator_Panel",
            "Screen",
            "Big_Red_Button",
            "Panel_Label_APU",
            "Panel_Label_STARTER",
            "Panel_Label_BLEED",
            "Panel_Label_VAC",
            "Panel_Label_LASER",
            "Panel_Label_HV",
            "Panel_Label_IGNITE",
            "Panel_Label_BEAM",
            "Panel_Label_COMP",
        ],
    },
    "hv_umbilical": {"title": "HV umbilical", "parts": ["High_Voltage_Umbilical"]},
    "thrust_sled": {
        "title": "Thrust sled",
        "parts": [
            "Rail_Left",
            "Rail_Right",
            "Thrust_Sled_Frame",
            "LoadCell_0",
            "LoadCell_1",
            "LoadCell_2",
            "LoadCell_3",
            "Engine_Mount_Frame",
        ],
    },
}

REMOVE_INSTANCES = {
    "Tank_Decaborane",
    "Decal_B10H14",
    "Pipe_B10H14_Feed",
    "Boron_Trunk_Line",
    "Decaborane_Heater_Mantle",
    "Laser_Ablation_Head",
    "Tank_Diborane",
    "Decal_B2H6",
    "Pipe_B2H6_Feed",
    "Anode",
    "Cathode",
}

FUSION_STACK = [
    {"op": "translate", "xyz": [0.0, 0.0, 0.92]},
    {"op": "rotate_y_about_point", "pivot": [0.0, 0.0, 0.32], "angle_deg": 90.0},
]

DEFAULT_INSTANCE = {
    "params": {},
    "color": [0.35, 0.35, 0.38],
    "transform_chain": [],
}


def _inst(name: str, template: str, color: list[float] | None = None, chain: list | None = None) -> dict:
    d = {
        "narrative": f"Reply 19 BOM — see ``SOLID_B11_LASER_FUEL.md``.",
        "template": template,
        **DEFAULT_INSTANCE,
    }
    if color:
        d["color"] = color
    if chain is not None:
        d["transform_chain"] = chain
    return d


def reply19_instances() -> dict:
    from ssto.orbitron.reply19_parts_cad import REPLY19_TEMPLATE_SLUGS

    out: dict = {}
    for part, tpl in REPLY19_TEMPLATE_SLUGS.items():
        chain = FUSION_STACK if part in {
            "Containment_Vessel_Jacket",
            "Heat_Exchanger_Channels",
            "Aerodynamic_Centerbody",
            "Compressor_Assembly",
            "Turbine_Assembly",
            "Compressor_Shaft_Bearings",
            "Inlet_Guide_Vanes_IGVs",
            "HV_Bushing_Feedthrough",
            "Magnet",
            "NBI_Injector",
            "Insulators",
        } else []
        color = None
        if "Boron" in part or "B11" in part:
            color = [0.55, 0.48, 0.35]
        elif "Laser" in part or "UV" in part or "Mirror" in part or "Optical" in part:
            color = [0.22, 0.22, 0.28]
        elif "Vacuum" in part or "Pump" in part or "Chamber" in part:
            color = [0.4, 0.42, 0.45]
        out[part] = _inst(part, tpl, color=color, chain=chain or None)
    # Legacy templates for parts that need full lab mesh
    out["Magnet"] = {
        "narrative": "2 T axial solenoid (lab surrogate).",
        "template": "orbitron_magnet",
        "params": {},
        "color": [0.2, 0.25, 0.55],
        "transform_chain": FUSION_STACK,
    }
    out["NBI_Injector"] = {
        "narrative": "Tangential keV injectors — H₂ + laser-ablated ¹¹B.",
        "template": "orbitron_nbi",
        "params": {},
        "color": [0.1, 0.55, 0.25],
        "transform_chain": FUSION_STACK,
    }
    out["Insulators"] = {
        "narrative": "Ceramic standoffs.",
        "template": "orbitron_insulators",
        "params": {},
        "color": [0.85, 0.85, 0.9],
        "transform_chain": FUSION_STACK,
    }
    out["Outer_Anode_Grid"] = {
        "narrative": "Grounded anode shell (Reply 19 outer grid).",
        "template": "orbitron_anode",
        "params": {},
        "color": [0.45, 0.45, 0.5],
        "transform_chain": FUSION_STACK,
    }
    out["Central_Cathode_Wire"] = {
        "narrative": "W / W-Re cathode at ~600 kV class.",
        "template": "orbitron_cathode",
        "params": {},
        "color": [0.55, 0.55, 0.6],
        "transform_chain": FUSION_STACK,
    }
    return out


def main() -> int:
    data = yaml.safe_load(LAB.read_text(encoding="utf-8"))
    data["logical"]["groups"] = REPLY19_GROUPS
    inst = data.get("instances", {})
    for k in REMOVE_INSTANCES:
        inst.pop(k, None)
    inst.update(reply19_instances())
    data["instances"] = inst
    # Narrative header
    asm = data.setdefault("assembly", {})
    asm["title"] = "Orbitron Phase 1+2 R&D stand (Reply 19 SSOT)"
    asm["narrative"] = REPLY19_GROUPS["test_stand"]["detail"]
    LAB.write_text(yaml.dump(data, sort_keys=False, default_flow_style=False, width=88), encoding="utf-8")
    print(f"Patched {LAB}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "ssto/orbitron"))
    raise SystemExit(main())
