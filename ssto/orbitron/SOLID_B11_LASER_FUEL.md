# Solid elemental ¹¹B + UV laser ablation (design SSOT)

Canonical fueling per **proton_boron_rand.md Reply 9** (commercial ¹¹B supply) and **Reply 18–19**
(Phase 1 benchtop BOM). **Not decaborane** — solid enriched boron disks ablated in vacuum.

## Fuel path

| Leg | Medium | Delivery |
| :--- | :--- | :--- |
| Protons | H₂ gas | Tangential NBI / injectors (integrated pad extension) |
| Boron-11 | **Solid ¹¹B** disks (99.9% enriched) | **Q-switched Nd:YAG 355 nm** through **UV Fused Silica Viewport** onto **Solid Boron-11 Target** in **Solid B-11 Target Holder** |
| Wall thermal (SSTO) | CH₄ cryo | Phase 2 / integrated pad — not core fuel |

## Phase 1 subassemblies (Reply 19)

| ID | Name | Key parts |
| :--- | :--- | :--- |
| 1.1 | Vacuum & Chamber System | Vacuum_Chamber, Turbomolecular_Pump, Roughing_Pump, Full_Range_Vacuum_Gauge, UV_Fused_Silica_Viewport, Solid_B11_Target_Holder |
| 1.2 | Electrostatic Orbitron Core | Central_Cathode_Wire, Outer_Anode_Grid, HV_Vacuum_Feedthrough, Solid_Boron_11_Target ×2, Magnet, NBI_Injector |
| 1.3 | Laser Ablation System | Q_Switched_NdYAG_Laser, Optical_Breadboard, UV_Focusing_Lens, Laser_Power_Meter, Kinematic_Mirror_Mounts |
| 1.4 | High-Voltage Power & Safety | Precision_DC_HVPS, High_Voltage_Cable, Ballast_Resistor, Interlock_Safety_Controller |
| 1.5 | Diagnostics & Particle Detection | Charged_Particle_Detector, Preamplifier, Spectroscopy_Amplifier, Multichannel_Analyzer_MCA, Faraday_Cup |

## Phase 2 subassemblies (Reply 19)

| ID | Name | Key parts |
| :--- | :--- | :--- |
| 2.1 | Full-Scale Engine Core & Heat Exchanger | Containment_Vessel_Jacket, Heat_Exchanger_Channels, Aerodynamic_Centerbody, High_Temp_Metallic_Seals |
| 2.2 | Turbomachinery & Air Flow Conditioning | Compressor_Assembly, Turbine_Assembly, Compressor_Shaft_Bearings, Inlet_Guide_Vanes_IGVs |
| 2.3 | Ground Support Blower | Industrial_Blower, S_Duct_Intake_Simulation, Exhaust_Silencer_Ducting, Airflow_Honeycomb_Filter |
| 2.4 | Megawatt-Scale Power & Starting | Pneumatic_Air_Starter, Solid_State_Marx_Generator, HV_Bushing_Feedthrough, Vacuum_Turbo_Pump_Array |
| 2.5 | Thermal & Aerodynamic Instrumentation | High_Temp_Thermocouples, Pitot_Static_Tubes, Mass_Flow_Sensor, Infrared_Pyrometer, Data_Acquisition_Chassis |

**Grand total (Reply 19):** $788,400

## Operating sequence (Reply 15 + 19)

See ``OPERATING_PHASES.md``. Proof suite steps 01–05 map to Phase 1; steps 06–07 to Phase 2 plant / Brayton.

## Simulator keys

```json
"injectants": {
  "h2_sccm": 80.0,
  "laser_ablation_hz": 10.0,
  "b11_target_index": 0
},
"pad": {
  "vacuum_interlock_ok": false,
  "laser_armed": false,
  "hv_enabled": false
}
```
