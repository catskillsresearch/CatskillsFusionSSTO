# Shuttle panel audit — Grenadier keep / obsolete / repurpose

Source inventory: 542 `set-tooltip` bindings in
`Models/cockpit.xml` (raw export:
`CatskillsFusionSSTO/Documentation/grenadier/panel_tooltips_raw.csv`).

Heuristic keyword pass: ~89 clearly MPS/OMS/APU/ET-class obsolete, ~196 flight/avionics keep,
~257 need human review (many lighting/DAP/GPC — keep by default).

## Keep (current for Grenadier TA)

- Flight controls: RHC/THC, rudder pedals, speedbrake, body flap, gear, brakes, nosewheel
- Displays: MDU power/dim, HUD, ADI/HSI-related, DPS/GPC/IDP, master alarm
- RCS / DAP / COAS / navigation / IMU / star tracker (attitude still needed)
- Cabin / av-bay fans, lighting, radios/Ku as available
- Abort / CWS annunciators (will gain new Grenadier messages later)

## Obsolete (leave inert or cover; do not drive Grenadier thrust)

| Family | Examples (object / function) | Why |
|--------|------------------------------|-----|
| SSME / MPS | `ctrl-pwr-sys-a/b-*`, MPS He/Pc, MES lights, LO2/LH2 | Replaced by single combined-cycle + CHARM |
| ET / SRB | ET umbilicals, ET static, booster-related | No stack on Grenadier TA |
| OMS engines | `oms-eng-left/right`, OMS arm, OMS TVC CWS | No dual OMS; vacuum Δv from σ3 / RCS |
| APU / HYD (ascent MPS TVC) | `apu-operate-*`, `apu-ctrl-pwr-*`, APU fuel | No SSME TVC hydraulics story; electric actuation TBD |
| Fuel cells as main power | FC reactant CWS (plant is CHARM bus) | Superseded by CHARM + battery; may keep as stub |
| Hypergol He press for OMS/RCS | OMS He tanks on MEDS | Green mono + e-pump later |

## Repurpose (v1 bindings — implemented)

Physical switches keep their mesh; Grenadier reads them as aliases when
`/sim/model/grenadier/enabled` = 1.

| Shuttle object / prop | Grenadier function | Property |
|----------------------|--------------------|----------|
| `apu-operate-1` → APU1 operate | Ground cart ONLINE | `charm/ground-cart` |
| `apu-operate-2` → APU2 operate | Flight battery ONLINE | `charm/battery-online` |
| `apu-operate-3` → APU3 operate | Cryo ENABLE | `charm/cryo-enable` |
| `apu-ctrl-pwr-1` | Magnet ARM | `charm/magnet-arm` |
| `apu-ctrl-pwr-2` | Fuel services ENABLE | `charm/fuel-enable` |
| `apu-ctrl-pwr-3` | RF ENABLE | `charm/rf-enable` |
| `ctrl-pwr-sys-a-ac2-left` (SSME L ctrl A) | CHARM LIGHT command | `charm/light-cmd` |
| `ctrl-pwr-sys-a-ac1-ctr` | DEC ONLINE | `charm/dec-online` |
| `ctrl-pwr-sys-a-ac3-right` | SCRAM | `charm/scram` |
| `oms-eng-left` | Engine σ decrease | `engine/sigma` − |
| `oms-eng-right` | Engine σ increase | `engine/sigma` + |
| MPS throttle / SPD lim (if present) | Engine throttle | `engine/throttle` via existing throttle axis preferred |

Tooltips are **not** re-engraved on the 3D mesh yet; operator screens and menu dialogs
carry Grenadier labels. Mesh stencil pass is a later Blender job.

## Decision questions (for you when convenient)

1. Confirm APU triplet as cart / battery / cryo — or prefer MPS controller row instead?
2. SCRAM on SSME-right controller — OK, or want a guarded switch family?
3. Keep fuel-cell panel as “battery mimic” or blank it?
