# Orbitron assembly specs (YAML SSOT)

YAML files in this directory are the **single source of truth** for lab geometry, FlightGear
shell, Nasal UI, physics/surrogate, and sound. Compilers under `tools/` emit artifacts into
`Aircraft/<package_dir>/`.

## Spec index

| File | Consumed by | Purpose |
|------|-------------|---------|
| `orbitron_lab.yaml` | `compile_assembly_yaml.py` | CadQuery meshes + logical assembly tree (schema v2) |
| `orbitron_avalanche_core.yaml` | (reference) | Avalanche Orbitron fusion-core design basis (stability, fields, fuel) |
| `orbitron_reference_plant.yaml` | (reference) | **Propulsion mechanism** — fusion-heated Brayton spool, heat paths, pad APU start |
| `orbitron_physics_surrogate.yaml` | `build_surrogate_map.py`, `compile_orbitron_aircraft_runtime.py`, **`surrogate_closure_check.py`** | WarpX sweep, surrogate scales, **0D traceability** (`formal.traceability_chain`), thrust-sled load model |
| `orbitron_aircraft_flightgear.yaml` | `compile_orbitron_aircraft_runtime.py` | `*-set.xml`, `Orbitron.xml`, JSBSim template copy |
| `orbitron_nasal.yaml` | `compile_orbitron_nasal.py` | `surrogate_load.nas`, `reactor_ui.nas` (operator screen) |
| `orbitron_sound_assets.yaml` | `sound_compiler.py`, `compile_sound_xml_from_yaml.py` | WAV beds + `sound.xml` |

## Thrust and thrust-sled load measurement

**Intent:** Pad-credible **thrust bookkeeping** and **four corner load cells** on the
`thrust_sled` assembly (`LoadCell_0` … `LoadCell_3` in `orbitron_lab.yaml`), shown on the
operator **Screen** in FlightGear.

### Data flow

```
Controls (W/S throttle, U/J compressor, SPACE startup)
    → JSBSim arcjet_airbreather (every FDM frame)
        → thrust-lbf, mass-flow-kgps  (bilinear surrogate)
        → sled-load-total-lbf, load-cell-0..3-lbf  (corner split + tare)
    → Nasal ReactorUI @ 10 Hz (read-only display on Screen mesh)
```

### CAD load path (meshes)

On `thrust_sled`: four `LoadCell_*` pucks on the deck → `Engine_Mount_Frame` posts on the
cell tops → top plate → air-breathing engine stack (pivot at `ENGINE_MOUNT_TOP_Z` in
`arcjet_test_stand_cad.py`, typically **z ≈ 0.32 m**). Regenerate glTF after pose changes:
`make orbitron-lab-gltf` or `./stand.sh`.

### Corner layout (lab coordinates)

Matches `thrust_sled_load_cells.corners` in `orbitron_physics_surrogate.yaml`:

| Cell | Label | Mesh instance |
|------|-------|----------------|
| 0 | +X+Y | `LoadCell_0` |
| 1 | −X+Y | `LoadCell_1` |
| 2 | +X−Y | `LoadCell_2` |
| 3 | −X−Y | `LoadCell_3` |

Intake / compressor narrative is on **−X**; higher compressor command shifts thrust share to **−X** corners.

### Model (summary)

Coefficients in `orbitron_physics_surrogate.yaml` → `thrust_sled_load_cells`:

- `tare_lbf` — static engine weight on the sled (split `tare/4` per corner when active)
- `compressor_moment_gain` — redistributes thrust share with `/controls/orbitron/compressor`
- `throttle_moment_gain` — redistributes thrust share with `/controls/reactor/throttle`

Per corner weight (example cell 0, +X+Y):

`w₀ = 0.25 − k_cx·compressor − k_cy·throttle`

Other corners flip signs on `k_cx` / `k_cy` per the `corners` table.  
`load-cell-i-lbf = active · (tare/4 + thrust · wᵢ)`  
`sled-load-total-lbf = active · (thrust + tare)`

Implementation: `tools/templates/orbitron-jsbsim.xml` (`arcjet_airbreather` channel).  
FG coefficients: `/sim/model/orbitron/thrust-sled/*` in `*-set.xml` from `compile_orbitron_aircraft_runtime.py`.

### Operator display

Rows are declared in `orbitron_nasal.yaml` under `reactor_ui.telemetry` and compiled into
`reactor_ui.nas`. Debug window (`M` key) lists the same properties.

### Tuning

1. Edit `thrust_sled_load_cells` in `orbitron_physics_surrogate.yaml`.
2. Run `./stand.sh` (regenerates `*-set.xml` and Nasal).
3. Fly the stand; use **W/S** and **U/J** to see thrust and corner loads move.

Thrust/mdot **scale** (magnitude) comes from `surrogate_engineering` and `engine_surrogate.json`, not from the load-cell block.

## Reference propulsion plant

Canonical mechanism (air = reaction mass, turbine drives compressor after pad start):

- **Spec:** [`orbitron_reference_plant.yaml`](orbitron_reference_plant.yaml)
- **Summary:** [`../../../gas_flow.md`](../../../gas_flow.md)

Meshes: `Pad_Startup_Cart` → `Pad_Startup_Power_Cable` → `Pad_Startup_Motor` (pad APU chain) ·
`Bellmouth_Inlet` → `Compressor_Can` → annulus / core → `Turbine_Can` → nozzle train.

### `logical_only` policy (schema v2)

Use **`logical_only: true` only on composite groups** that organize **child groups which already
export meshes** — never on hardware that could have a CadQuery ``instances`` entry. If it can be
built, add an **instance** and list it under ``parts`` (or under a member assembly’s ``parts``).
Do **not** create empty placeholder groups; remove them from the tree instead.

## Gas flow (supply vs fusion ash)

Human-readable record: [`../../../gas_flow.md`](../../../gas_flow.md).  
Machine-readable: `orbitron_lab.yaml` (`connections`, `logical.groups`, instance narratives).

| Fluid | Assembly / meshes | Notes |
|-------|-------------------|--------|
| **H₂** | `hydrogen_tank_assy` → `Hydrogen_Trunk_Line` → `NBI_Injector` | p-¹¹B core (D₂ Orbitron-class hardware) |
| **B₂H₆** | `boron_tank_assy` → `Boron_Trunk_Line` → `NBI_Injector` | p-¹¹B core boron carrier |
| **⁴He ash** | `Helium_Ash_Vent_Line` → nozzle | p-¹¹B fusion product |
| **CH₄** | `methane_tank_assy` (optional) | SSTO wall thermal only |

**Core physics:** `orbitron_avalanche_core.yaml`. **Controls:** W/S ion beam, I/K cathode pulse (PSP2–Jin shear), U/J compressor (arcjet).

Sub-glTF exports: `make orbitron-lab-gltf` builds `hydrogen_tank_assy.gltf` and `boron_tank_assy.gltf`.
