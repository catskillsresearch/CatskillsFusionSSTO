# Engine operator model — CATSKILLS-SSTO-TA-GRENADIER

Three-cycle electric rocket: σ1 EDF (air), σ2 air-plasma, σ3 water-plasma (intakes sealed).
Plant couples **only** by power cable (`charm/bus-mw`).

## Property bus

Prefix: `/fdm/jsbsim/systems/grenadier/engine/`

| Property | Type | Meaning |
|----------|------|---------|
| `sigma` | int | Commanded stage 1/2/3 |
| `sigma-recommended` | int | From altitude (and optional Q) |
| `sigma-allowed` | int | Max stage permitted by sensors + plant |
| `inlet-sealed` | bool | Intakes sealed (required for σ3) |
| `throttle` | double | 0–1 thrust demand |
| `thrust-kn` | double | Surrogate thrust |
| `power-draw-mw` | double | Bus demand |
| `water-kg` | double | Carried water |
| `water-flow-kgps` | double | σ3 mass flow |
| `alt-ft` | double | Mirror of `/position/altitude-ft` |
| `q-psf` | double | Dynamic pressure (optional gate) |
| `stage-go` | bool | Commanded stage is allowed |
| `plant-ok` | bool | CHARM mode POWER and not scrammed |

## Stage gates (v1)

| Stage | Sensor gate (default) | Other |
|-------|----------------------|-------|
| σ1 | Always when plant-ok | Inlet open |
| σ2 | `alt-ft` ≥ `sigma2-alt-ft` (default 25000) | Inlet open |
| σ3 | `alt-ft` ≥ `sigma3-alt-ft` (default 120000) **or** operator override with inhibit warn | `inlet-sealed` = 1; water > 0 |

Altitude thresholds are editable props for tuning. Crew may command a higher stage;
UI shows INHIBIT if sensors say no; hard block only when water empty (σ3) or plant not POWER.

## Screens

`Nasal/canvas/cdlg_grenadier_engine.nas`:

- Stage commanded / recommended / allowed
- Altimeter (primary sensor strip)
- Inlet sealed, water kg, thrust, power draw, plant-ok
- Buttons: σ1 / σ2 / σ3, SEAL, throttle ±
