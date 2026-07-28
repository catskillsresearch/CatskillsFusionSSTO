# Grenadier control map (assembly → cockpit)

Operator-facing systems vs flightdeck switches. CHARM mode string
`OFF/CRYO/ARM/LIGHT/POWER/SCRAM` is **derived** — not a physical rotary.

Prefixes: `C=/fdm/jsbsim/systems/grenadier/charm/` · `E=.../engine/`

## REMAP (wired in `Nasal/grenadier/grenadier_ops.nas`)

| Assembly / function | Switch object | Hover label (Grenadier) | Property |
|---------------------|---------------|-------------------------|----------|
| Ground cart | `apu-operate-1` | Ground cart | `C/ground-cart` |
| Flight battery | `apu-operate-2` | Flight battery | `C/battery-online` |
| Cryo plant | `apu-operate-3` | Cryo enable | `C/cryo-enable` |
| Magnets | `apu-ctrl-pwr-1` | Magnet arm | `C/magnet-arm` |
| Fuel services | `apu-ctrl-pwr-2` | Fuel enable | `C/fuel-enable` |
| RF | `apu-ctrl-pwr-3` | RF enable | `C/rf-enable` |
| CHARM light-off | `ctrl-pwr-sys-a-ac2-left` | CHARM LIGHT | `C/light-cmd` |
| DEC | `ctrl-pwr-sys-a-ac1-ctr` | DEC online | `C/dec-online` |
| Vacuum | `ctrl-pwr-sys-a-ac3-right` | Vacuum ready | `C/vacuum-ready` |
| SCRAM | `main-eng-limit-shut-dn` Enable | CHARM SCRAM | `C/scram` |
| Stage down | `oms-eng-left` | Stage - | `E/sigma` |
| Stage up | `oms-eng-right` | Stage + | `E/sigma` |
| Throttle | engine[0] lever | Engine throttle | `E/throttle` |

Mode progression: cart+batt → cryo → magnet+fuel+vac → RF+LIGHT → DEC → POWER.

## KEEP (airframe / avionics)

Flight controls, gear, brakes, NWS, RHC/THC, DAP/RCS jet selects, HUD/ADI/HSI,
GPC/IDP/MDU power, lighting, cabin fans, abort CWS (messages TBD).

## INERT (unwired / tooltip-marked; mesh stays)

| Family | Examples | Why |
|--------|----------|-----|
| Fuel cells | `fuel-cell-reac-vlv*` | CHARM bus + battery |
| ET / SRB | umbilicals, booster | No stack |
| OMS engines (except Stage ±) | OMS TVC | Deleted |
| MPS propellant story | He/Pc/LO2/LH2 (except remapped ctrl A) | Single Stage nozzle |
| APU hydrazine / hyd pumps | fuel qty, hyd press (except operate/ctrl aliases) | No hyd TVC story |

## CRT map

| Softkey | Page | Content |
|---------|------|---------|
| STAGE | `p_meds_oms_mps` | Stage, throttle, seal, water, thrust, bus |
| CHARM | `p_meds_apu` | Mode, cart/batt/cryo/mag/fuel/RF/DEC, bus MW |
| SPI | `p_meds_spi` | Keep (RCS-adjacent later) |

## Physical engraving

`fwd-cockpit-text-map-x.png` still shows Shuttle lettering on many keys. Hover
tooltips for obsolete families are **blank** so unused switches do not advertise
false systems. Remapped switches keep Grenadier hover names. UV blanking of
engraved text is a follow-on pass.
