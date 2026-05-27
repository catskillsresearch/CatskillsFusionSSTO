# Unobtainium — p-¹¹B Orbitron (Catskills design basis)

**Context:** Avalanche Energy’s public **Orbitron** work uses **deuterium (D₂)** only. We do **not**
assume they have analyzed p-¹¹B on that hardware. We borrow **topology** (orbitrap + magnetron + tangential
keV beams + cathode pulse), not their **300 kV D₂** operating point as canon for p-¹¹B.

**Design voltage:** **~−600 kV** cathode class for p-¹¹B (we take **~300 kV** as adequate for **D₂** on a
real Orbitron, but **not** for our fuel).

**Energy offload:** **Fusion-heated Brayton** on ingested **air** (test stand + SSTO). No multi‑MV grid
tie, no DEC-as-primary-power, no multi‑MV arc in the intake duct.

**Design-validation goal:** A **step-through design validation simulator** that answers:

> With this geometry and these operating parameters, does the plant meet **3.5 MW** and pass
> quantified **U1–U4** performance specs—and what unobtanium margins are required?

**GUI simulator:** [`simulator/`](simulator/) — see **[`simulator/SIMULATOR.md`](simulator/SIMULATOR.md)** for full
documentation (workflow, physics, validation, YAML export, limitations).

```bash
poetry install --with simulator
poetry run python scripts/run_orbitron_simulator.py
```

### Fidelity ladder (what “validated” means)

| Tier | Mechanism | Validates |
|------|-----------|-----------|
| **0** | Pad interlocks | Correct startup sequence only |
| **1** | `plant_0d` + `validation.py` | U1–U4 inequalities, **3.5 MW** headline, jet closure F²≈2ηPṁ |
| **2** | WarpX PIC → ρ proxies | Density / beam coupling at 600 kV — **not** p-¹¹B fusion Q |
| **3** | `fusion_pb11.py` | p-¹¹B <σv>(T_i) × n_p n_B × V × E_rxn; blended with surrogate map |
| **4** | Future | Transport / PIC-integrated reactivity (replace analytical fit) |

**Important:** PIC does **not** compute fusion yield today. Tier-1 “fusion” means the **0D surrogate**
at your knobs reaches power/beam/density milestones **without violating** cathode, wall, or magnet limits.

### Proof chain (iterative suite + batch scripts)

**Interactive (recommended):** one rich panel per step — linger, visualize, re-run:

```bash
poetry run python scripts/run_orbitron_proof_suite.py
```

**Batch / CI:** same artifacts under `build/orbitron/chain/`:

```bash
tools/orbitron_proof_chain/run_all.sh
```

Guides: [`PROOF_SUITE.md`](PROOF_SUITE.md) (interactive) · [`validation_steps.md`](validation_steps.md) (full chain spec).

### Workflow

1. **Pad startup** — step 1→4 (same as FlightGear); each step updates allowed physics (air only → burn).
2. **Validate design** — **Validation** tab lists pass/fail per U1–U4 with numbers.
3. **Solve unobtanium → target MW** — finds required knobs (emission margin, wall flux, HTS scale, reactivity, …).
4. **Run WarpX PIC** (optional) — tightens density/beam proxies used in tier-1 checks.
5. **Export YAML…** on the Validation tab — writes `orbitron_design_validation.yaml` for spec documents
   (geometry, pad state, unobtanium knobs, fusion physics, CH₄/HTS sizing, pass/fail table).

Default export path suggestion: `build/orbitron/design_validation.yaml`

### Fusion physics module

`ssto/orbitron/simulator/fusion_pb11.py` implements:

- **¹H + ¹¹B → 3 ⁴He** with 8.68 MeV per reaction  
- **<σv>(T_i)** peaked analytical fit (ion energy from 600 kV class cathode)  
- Fueling from **H₂ / B₂H₆ sccm** into confined bore volume  
- Blended with **surrogate map** scalars (`surrogate_calib.py`, optional CSV from `build_surrogate_map.py`)

### Thermal sizing

`ssto/orbitron/simulator/thermal_systems.py` sizes **CH₄ mdot/ΔT** (U2) and **HTS cryo load** (U3) from wall heat and bore field.

Auxiliary: **Device** / **Longitudinal 2D** views (optional; not required for spec quantification).

---

## U1 — Non-arcing cathode (−600 kV)

| Spec | Value |
|------|--------|
| Geometry | ~**5 mm** radius on-axis wire, ~**5–10 cm** radial gap to anode |
| Potential | **−600 kV** DC (design), **400–600 kV** operating band |
| Environment | High vacuum bore, no sustained vacuum arc |
| Material (concept) | **Tungsten–rhenium** core with **defect-free / CNT-class** surface treatment |
| Performance | Field emission suppressed so the well is electrostatic, not a lightning short to the wall |

**The simulator derives:** allowable surface field (V/m), emission current density, and whether **600 kV** is
consistent with gap geometry without arc — feeds U1 acceptance criteria.

---

## U2 — First wall (hot) + CH₄ intercept

| Spec | Value |
|------|--------|
| Location | **First wall / anode sheath** at plasma radius — catches **α**, **X-ray**, **CX** (not neutrons) |
| Wall load (design anchor) | **~400 kW** steady boundary deposition (0D `heat_kw_scale`) |
| Wall material (concept) | **Niobium C-103**-class pressure boundary (or equivalent) |
| Face temperature | **800–1000 °C** class toward plasma; outer face feeds **air annulus** |
| Coolant | **Liquid methane** ~**−160 °C** in **internal channels** — removes ~55% of wall load in 0D split |
| Limit | Metal stays below failure; **CH₄** must close flux limits independent of Brayton air |

**The simulator derives:** CH₄ ṁ for the **intercept fraction** of `first_wall_kw`, not for cooling compressed air.

---

## U3 — HTS solenoid outside cryostat (cold zone)

| Spec | Value |
|------|--------|
| Layout | **Outside** vacuum cryostat; **B** penetrates bore; **no** direct α / X-ray flux on tape |
| Field | **2.0 T** axial **B** in the plasma bore (PIC / core YAML) |
| Magnet (concept) | **YBCO-class** HTS tape solenoid (~7.5–10 cm outer radius in zoning budget) |
| Temperature | **~113 K** via liquid **CH₄** cryostat loop (parasitic leak only — not the 400 kW wall stream) |
| Insulation | Vacuum gap + **MLI** between **hot air annulus** and coil |
| Mass | Light enough for SSTO vs copper — **cryostat + MLI mass not fully sized in 0D** |

**The simulator derives:** cryo load vs `hts_capability_scale`; radiative leak budget vs air-channel temperature.
See **`THERMAL_ZONING.md`** for the inside-out stack.

---

## U4 — p-¹¹B plasma regime (physics, not a shelf material)

| Spec | Value |
|------|--------|
| Headline channel | **¹H + ¹¹B → 3 ⁴He** (+ energy) |
| Injectants | **H₂** + **B₂H₆** (dissociated in discharge) to tangential keV injectors |
| Power headline | **3.5 MW** gross thermal at full command (surrogate scale; model must derive conditions) |
| Beam | **> 1 mA** class ion beam integration target |
| Density | **10¹¹–10¹² cm⁻³** class goals |

**The simulator derives:** required fusion power density, beam power, and confinement time — this is the
**largest** unknown; U1–U3 must survive whatever power and wall load that solution demands.

---

## Removed from design (Category E — not in repo SSOT)

- **+4 MV DEC grid** as primary **3.5 MW electrical** extraction  
- **8 MV → grid** step-down / diamond inverters  
- **Multi‑MV arc** in the combustor as the main energy coupling  

Thrust and pad energy bookkeeping use **air Brayton** only.
