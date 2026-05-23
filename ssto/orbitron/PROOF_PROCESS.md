# Orbitron proof process — professional concept sketch

This document is the **operator-facing process SSOT** for the Catskills p-¹¹B Orbitron test stand. It ties together bench practice (UHV, laser ablation, HV), the proof chain (Tier 2–3 physics), and Phase 2 aeronautics (Brayton on ingested air). The CAD/BOM narrative is **Reply 19** in `proton_boron_rand.md`; fuel is **solid elemental ¹¹B + 355 nm laser ablation**, not decaborane or B₂H₆ gas.

---

## What we claim vs what we defer (fidelity ladder)

| Tier | Claim | Tooling |
|------|--------|---------|
| **0** | Geometry, mass, panel sequence, thrust-sled bookkeeping | `./stand.sh` → YAML → glTF → FlightGear |
| **1** | Pad interlocks, H₂ + laser Hz fueling, 600 kV class electrostatics | Proof Suite pad + `pad_startup.py` |
| **2** | E×B ring and tangential H⁺/B⁺ deposit **proxies** from 2D WarpX | Steps 01–02 |
| **3** | p-¹¹B ⟨σv⟩ burn, U1–U4 material gates, 0D plant, jet closure | Steps 04–08 |
| **4** | Laser plume kinetics, measured ⟨σv⟩ tables, 3D transport, certified thrust | **Not claimed** in this repo |

A trained reviewer should read the proof chain as **concept validation with explicit limits**, not as a published fusion performance demonstration.

---

## Phase 1 — Benchtop (stationary UHV)

Physical order matches standard UHV fusion-lab practice:

| Step | Operator action | Engineering basis |
|------|-----------------|-------------------|
| **P1-A** | Close chamber; **roughing** then **turbo** pump | Base pressure before high-voltage |
| **P1-B** | **Full-range gauge** ≤ ~10⁻⁶ Torr; assert **VACUUM OK** | Prevents charge-exchange neutrals destroying confinement |
| **P1-C** | Align **355 nm** Nd:YAG path; **power meter** at viewport | Cold UV ablation of ¹¹B — avoids molten B corrosion |
| **P1-D** | **Arm laser**; spot on **Solid Boron-11 Target** | Fuel enters as ablation plume; laser does not steer ions |
| **P1-E** | Enable **600 kV class** bias via interlocks + feedthrough | Electrostatic trap accelerates B⁺/H⁺ to keV orbits |
| **P1-F** | Open **H₂**; pulse laser; **Faraday cup / MCA** | p-¹¹B inventory and 3α signature check |

**After ablation:** the **−600 kV orbitrap** (with weak axial **B** for E×B electron neutralization and tangential **NBI** geometry) impels and confines ions — not the laser beam itself.

---

## Phase 2 — Wind-tunnel rig (ground Brayton)

| Step | Operator action | Engineering basis |
|------|-----------------|-------------------|
| **P2-A** | Ground **blower** + honeycomb / S-duct | Simulated ram air — reaction mass is **air**, not tanked propellant |
| **P2-B** | **Pneumatic starter** or pad APU → **compressor** | Spool light-off before fusion-heated gas |
| **P2-C** | Bleed → **IGVs** → **containment jacket** annulus | Fusion heat deposits via bremsstrahlung, alphas, CX — not thermalized “8 GK” bulk |
| **P2-D** | Phase 1 interlocks + **Marx/HV** when flow stable | Hot mixed gas drives turbine → sustains compressor |
| **P2-E** | Ignite; DAQ thermocouples, pitot, mass flow | Instrumented closure, not hand-waved thrust |
| **P2-F** | **Turbine** + exhaust silencer | Brayton offload path for MW-class concept |

---

## Proof Suite chain (software steps 00–09)

The GUI uses **physics-chain step IDs** (not one GUI screen per P1-A…P1-F). Map bench phases to controls as follows:

| Proof step | Bench / physics role |
|------------|----------------------|
| **00** | Freeze SSOT: geometry, H₂ + **laser_ablation_hz**, PICMI overrides |
| **01** | WarpX 2D slice at pad point — set **VAC → LASER → HV → ignite** on step 01 pad |
| **02** | Extract ρ_e_norm, ρ_beam_norm |
| **03** | Laminar shear vs clump (instability mitigation narrative) |
| **04** | n_p, n_B from H₂ + laser (solid ¹¹B, no borane SCCM) |
| **05** | Forward p-¹¹B power (reactivity scale = 1) |
| **06** | 0D plant, U1–U4 (field emission, wall, HTS, beam) |
| **07** | Jet closure F² ≈ 2ηPṁ (aero bookkeeping) |
| **08** | Validation YAML for review |
| **09** | Inverse solve — **gap analysis only** (disables proof mode) |

Launch: `./scripts/run_orbitron_proof_suite.sh`  
Build CAD/FG: `./stand.sh` (separate artifact tree)

---

## Proof-mode discipline (for reviewers)

- `fusion_reactivity_scale = 1.0` — no knob to fake 3.5 MW  
- No surrogate CSV blend on headline burn in proof mode  
- Step **09** documents **minimum unobtanium** if forward chain misses targets — not a substitute for Tier 4  

---

## References in repo

| Topic | File |
|-------|------|
| Fuel SSOT | `SOLID_B11_LASER_FUEL.md` |
| Operating phases | `OPERATING_PHASES.md` |
| Core physics | `assembly_specs/orbitron_avalanche_core.yaml` |
| Proof GUI | `PROOF_SUITE.md` |
| Chain scripts | `validation_steps.md` |
