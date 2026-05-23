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

## Proof Suite mapping (software steps 00–09)

The interactive Proof Suite implements a **physics validation chain**, not a 1:1 wizard for each P1-* row. Use the pad console on **step 01** for interlocks P1-B through ignite; set fuel on **step 00**.

| Proof step | Operator / physics role |
| :--- | :--- |
| 00 | Design SSOT — geometry, H₂ sccm, **laser_ablation_hz**, PICMI |
| 01 | WarpX PIC — set **APU → starter → bleed → VAC → LASER → HV → ignite**, then Run |
| 02 | PIC norms — ρ_e and beam coupling |
| 03 | Fusion channel — laminar vs clump (s–r) |
| 04 | Fueling — n_p, n_B from H₂ + laser (solid ¹¹B) |
| 05 | p-¹¹B burn — forward power, honest shortfall |
| 06 | 0D plant — U1–U4, wall, CH₄, HTS |
| 07 | Jet closure — Brayton F² discipline |
| 08 | Validation export |
| 09 | Inverse solve (gap analysis only) |

Full narrative: [`PROOF_PROCESS.md`](PROOF_PROCESS.md).
