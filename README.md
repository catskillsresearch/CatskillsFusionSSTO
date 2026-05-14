# CatskillsFusionSSTO

A high-performance Single-Stage-to-Orbit (SSTO) aircraft for FlightGear, powered by fusion propulsion.

## Orbitron lab test stand (design basis)

The **Orbitron fusion arcjet laboratory** is specified in
`ssto/orbitron/assembly_specs/orbitron_lab.yaml` (schema v2: geometry + logical tree SSOT).

**Purpose:** Ground-integration article for a compact **p-¹¹B** crossed-field fusion
machine in an **air-breathing + CD-nozzle** flowpath—pad-credible plumbing, thermal
services, and operator-visible hardware. **FlightGear** export is a **discipline step**
(named meshes, interfaces, telemetry hooks), not the end product.

**Energy offload:** The design basis **vents fusion-derived energy by thermodynamic work
on a gas path** (not multi-MV direct grid tie at utility scale). That makes **wall heat
removal** and **cryogen loops** first-class—including **liquid CH₄** for **anode /
boundary thermal management**.

**Three gases (roles):**

| Gas | Primary role in this spec |
|-----|---------------------------|
| **B₂H₆** | Gaseous **boron carrier** to the **NBI / injector** path; headline channel after dissociation: **¹H + ¹¹B → 3 ⁴He** |
| **H₂** | **NBI co-injectant** (stability / hydrogenic inventory including protons for p-¹¹B) |
| **CH₄** (liquid) | **Thermal management** working fluid—not the boron carrier |

**Operation:** Intended **continuous steady state** while consumables last, with orderly
shutdown before starvation.

Build: `make orbitron-lab-gltf` / `./stand.sh` (see repository `Makefile`).

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
