# Reactor operator model — CATSKILLS-SSTO-TA-GRENADIER

## Property bus

Prefix: `/fdm/jsbsim/systems/grenadier/charm/`  
Controls mirror: `/controls/grenadier/charm/`  
Pad discretes: `/sim/model/grenadier/charm/`

| Property | Type | Meaning |
|----------|------|---------|
| `mode` | string | OFF, CRYO, ARM, LIGHT, POWER, SCRAM |
| `mode-index` | int | 0–5 for checklist/UI |
| `fuel-b11-kg` | double | Solid ¹¹B inventory |
| `fuel-proton-kg` | double | Proton / H inventory |
| `battery-kwh` | double | Flight battery energy |
| `battery-min-kwh` | double | Reserve floor for space restart |
| `battery-online` | bool | Battery on plant bus |
| `ground-cart` | bool | Cart present |
| `startup-source` | string | CART / BATTERY |
| `cart-tied` | bool | Cart tied to aux |
| `cryo-enable` | bool | Cryo bay running |
| `cryo-kw` | double | Cryo power draw |
| `magnet-arm` | bool | Magnets commanded |
| `magnet-i-frac` | double | 0–1 current fraction |
| `magnet-t-k` | double | Magnet thermal proxy (K) |
| `fuel-enable` | bool | Fuel services |
| `fuel-ready` | bool | Pressures OK |
| `vacuum-ready` | bool | Chamber vacuum OK |
| `rf-enable` | bool | RF rack |
| `light-cmd` | bool | Light-off command |
| `plasma-proxy` | double | 0–1 confinement proxy |
| `dec-online` | bool | DEC converting |
| `bus-mw` | double | Electrical bus output MW |
| `recirc-mw` | double | Recirculating load MW |
| `aux-bus-v` | double | Aux bus volts |
| `scram` | bool | Hard trip latch |
| `go-fuel` / `go-cryo` / `go-magnet` / `go-bus` | bool | Screen go lamps |

## Mode machine

```
OFF → (cart/batt + cryo) → CRYO → (fuel+vac+arm) → ARM
    → (rf+light) → LIGHT → (dec + bus) → POWER
Any → SCRAM (latched until reset)
```

Implemented in `Nasal/grenadier/grenadier_ops.nas`. Screens in
`Nasal/canvas/cdlg_grenadier_reactor.nas` (Fuel + Startup pages).

## Screens

1. **FUEL** — B11, proton, battery kWh, water cross-read, cart/batt source.
2. **STARTUP** — sequence lamps matching reactor_startup.md steps + mode + bus MW.
