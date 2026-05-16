# CatskillsFusionSSTO

A high-performance Single-Stage-to-Orbit (SSTO) aircraft for FlightGear, powered by fusion propulsion.

## Orbitron lab test stand (design basis)

The **Orbitron fusion arcjet laboratory** is specified in
`ssto/orbitron/assembly_specs/orbitron_lab.yaml` (schema v2: geometry + logical tree SSOT).

**Purpose:** **SSTO** imagining built on Avalanche’s **Orbitron** machine class (orbitrap + **E×B**
electrons, tangential keV injection, cathode-pulse stability)—with an **unobtainium p-¹¹B fuel**
leap (**H₂ + B₂H₆** injectants, ``¹H + ¹¹B → 3 ⁴He``) instead of their published **D₂** path.
Air-breathing + CD-nozzle energy offload; FlightGear telemetry. Core spec:
[`ssto/orbitron/assembly_specs/orbitron_avalanche_core.yaml`](ssto/orbitron/assembly_specs/orbitron_avalanche_core.yaml).

**Propulsion plant:** Single-spool **fusion-heated Brayton** — air ingested at **−X**,
compressed, heated on **hot reactor walls** and in a **plenum mixer** (core exhaust + ⁴He ash),
expanded through a **turbine** that drives the **compressor** after pad **electric start**, then
through a **CD nozzle** for thrust. Canonical spec:
[`orbitron_reference_plant.yaml`](ssto/orbitron/assembly_specs/orbitron_reference_plant.yaml).
**Energy offload** is this thermodynamic path (not multi-MV on inlet air). **CH₄** is optional
wall thermal only.

**Fuels and services:**

| Supply | Role |
|--------|------|
| **H₂** | p-¹¹B core — proton / stability tangential keV injectant |
| **B₂H₆** | p-¹¹B core — boron carrier to same injectors |
| **⁴He** | Fusion ash → nozzle plenum (`Helium_Ash_Vent_Line`) |
| **Air** | Arcjet / nozzle energy offload (SSTO layer) |
| **CH₄** | Optional SSTO wall thermal only |

**Operation:** Intended **continuous steady state** while consumables last, with orderly
shutdown before starvation.

Build: `make orbitron-lab-gltf` / `./stand.sh` (see repository `Makefile`).

**Gas routing (full paths, ash vent, mermaid):** [`gas_flow.md`](gas_flow.md).

### Thrust and thrust-sled load telemetry (FlightGear)

The operator **Screen** shows live **thrust**, **airflow (surrogate mass flow)**, **total sled load**, and **four corner load-cell readings** that respond to test-stand controls. This is a **0D bookkeeping model** (not a structural FEA solve): JSBSim evaluates it every frame; Nasal only displays properties.

| Control (keyboard / panel) | Property | Effect on telemetry |
|--------------------------|----------|---------------------|
| **1** / APU switch | `/sim/model/orbitron/pad-apu-online` | Pad cart energizes starter bus |
| **2** / starter switch | `/sim/model/orbitron/starter-engage` | Crank spool (requires APU); crank SFX |
| **3** / bleed switch | `/sim/model/orbitron/bleed-air-open` | Intake path open → compressor effective |
| **SPACE** / red button | `/sim/model/reactor/startup-trigger` | Ignite → **thrust** / load outputs (requires bleed) |
| **W / S** | `/controls/reactor/throttle` | Ion beam → **mA**, **thrust**, **mdot** (after ignite) |
| **I / K** | `/controls/orbitron/cathode-pulse` | Cathode pulse / shear (PSP2–Jin stability proxy) |
| **U / J** | `/controls/orbitron/compressor` | Air-path command (× bleed × spool factor) |

Sequence spec: [`orbitron_operator_console_spec.yaml`](ssto/orbitron/assembly_specs/orbitron_operator_console_spec.yaml).

**JSBSim outputs** (prefix `/fdm/jsbsim/systems/arcjet/`):

- `thrust-lbf` — axial thrust from surrogate surface (throttle × compressor)
- `mass-flow-kgps` — air-path mass flow (shown as “Airflow (mdot)” on screen)
- `sled-load-total-lbf` — thrust + engine tare on the sled
- `load-cell-0-lbf` … `load-cell-3-lbf` — corner shares (+X+Y, −X+Y, +X−Y, −X−Y)

**Where documented / configured:**

| File | Role |
|------|------|
| `ssto/orbitron/assembly_specs/orbitron_physics_surrogate.yaml` | Model coeffs (`thrust_sled_load_cells`), formal narrative |
| `ssto/orbitron/assembly_specs/orbitron_nasal.yaml` | Operator screen rows (`reactor_ui.telemetry`) |
| `ssto/orbitron/assembly_specs/orbitron_aircraft_flightgear.yaml` | FG property wiring notes |
| `tools/templates/orbitron-jsbsim.xml` | JSBSim FCS implementation |
| `ssto/orbitron/assembly_specs/README.md` | Assembly-spec index (includes this feature) |

Regenerate after YAML edits: `./stand.sh` (or `make` for Nasal, `*-set.xml`, and `orbitron-jsbsim.xml`).

## Origin & Provenance

This project is a fork of the **FlightGear Space Shuttle**, originally developed by Thorsten Renk and the FlightGear development team. It is built upon the stable 2020.3 release source code.

## The Mission
The goal of this project is to re-engineer the Shuttle's complex systems (GPCs, APUs, and thermal protection) into a modern, fusion-powered SSTO capable of rapid deployment and recovery.

## Technical Details
- **Base Model:** FlightGear Space Shuttle (GPL v2)
- **FDM:** JSBSim
- **Primary Systems:** Nasal-based GPC emulation

## Installation
1. Make a folder called "Aircraft".  Clone this repository under "Aircraft".
2. Open the FlightGear Launcher
```
fgfs --launcher
```
3. Go to **Add-ons** > **Additional aircraft folders**.
4. Click **Add** and select your new "Aircraft" folder.
5. The "Catskills Fusion SSTO" should now appear in your aircraft list.
