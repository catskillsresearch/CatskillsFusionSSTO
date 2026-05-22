# Operating phases (Reply 15, 18, 19)

## Phase 1 — Benchtop (stationary UHV)

| Step | Operator action | Parts / subassembly |
| :--- | :--- | :--- |
| P1-A | Close chamber; start **Roughing_Pump** then **Turbomolecular_Pump** | 1.1 |
| P1-B | Confirm **Full_Range_Vacuum_Gauge** ≤ target (≈10⁻⁶ Torr); set VAC interlock | 1.1 |
| P1-C | Align **Q_Switched_NdYAG_Laser** / **Kinematic_Mirror_Mounts**; check **Laser_Power_Meter** | 1.3 |
| P1-D | Arm laser; verify beam through **UV_Fused_Silica_Viewport** onto **Solid_Boron_11_Target** | 1.1, 1.2, 1.3 |
| P1-E | Enable **Precision_DC_HVPS** via **Interlock_Safety_Controller**; bias **Central_Cathode_Wire** | 1.4, 1.2 |
| P1-F | Open **H₂** (integrated pad); pulse laser; watch **Faraday_Cup** / **MCA** for alphas | 1.5, injectants |

## Phase 2 — Wind tunnel (ground Brayton)

| Step | Operator action | Parts / subassembly |
| :--- | :--- | :--- |
| P2-A | Start **Industrial_Blower** + **Airflow_Honeycomb_Filter** / **S_Duct_Intake_Simulation** | 2.3 |
| P2-B | **Pneumatic_Air_Starter** (or pad APU) spins **Compressor_Assembly** via **Compressor_Shaft_Bearings** | 2.4, 2.2 |
| P2-C | Bleed open — flow through **Inlet_Guide_Vanes_IGVs** → **Containment_Vessel_Jacket** | 2.2, 2.1 |
| P2-D | When airflow stable, run Phase 1 interlocks (vacuum, laser, **Solid_State_Marx_Generator** / HV) | 2.4 + Phase 1 |
| P2-E | Ignite fusion; monitor **High_Temp_Thermocouples**, **Pitot_Static_Tubes**, **Data_Acquisition_Chassis** | 2.5 |
| P2-F | **Turbine_Assembly** sustains compressor; exhaust via **Exhaust_Silencer_Ducting** | 2.2 |

## Proof suite mapping

| Step | Phase |
| :--- | :--- |
| 00 | Design SSOT (all subassemblies) |
| 01 | P1-A, P1-B |
| 02 | P1-C, P1-D |
| 03 | P1-E (+ 1.2 core PIC) |
| 04 | P1-F diagnostics |
| 05 | Fueling H₂ + ¹¹B laser |
| 06 | P2-D jacket / plant |
| 07 | P2-F jet closure |
