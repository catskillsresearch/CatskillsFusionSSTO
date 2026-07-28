# Shuttle panel audit — Grenadier keep / obsolete / repurpose

Source inventory: 542 `set-tooltip` bindings in
`Models/cockpit.xml` (raw export: [panel_tooltips_raw.csv](panel_tooltips_raw.csv)).

Heuristic keyword pass: ~89 clearly MPS/OMS/APU/ET-class obsolete, ~196 flight/avionics keep,
~257 need human review (many lighting/DAP/GPC — keep by default).

## Locked decisions (common sense; changeable later)

1. **APU row = pad / plant services** — Keep APU1/2/3 = ground cart / flight battery / cryo, and APU controller power = magnet / fuel / RF. Reason: that row already means “start the machinery,” same metaphor as the Orbitron pad panel; leave the MPS controller row for light-off steps.
2. **SCRAM on Main Engine Limit Shutdown → Enable** — Not on SSME-right (too easy to bump next to LIGHT/DEC). Reason: the limit-shutdown switch is already a three-position “don’t kill the engine / allow kill” control; Enable is the deliberate SCRAM gesture. Canvas SCRAM button remains as backup.
3. **Fuel cells stay obsolete / inert** — Do not mimic the battery. Reason: battery already has APU2 + fuel screen; dual UI would confuse; FC reactant valves stay heritage wallpaper until we delete or cover them.

Also: SSME-right controller A = **vacuum ready** (needed for go-fuel), not SCRAM.

## Keep (current for Grenadier TA)

- Flight controls: RHC/THC, rudder pedals, speedbrake, body flap, gear, brakes, nosewheel
- Displays: MDU power/dim, HUD, ADI/HSI-related, DPS/GPC/IDP, master alarm
- RCS / DAP / COAS / navigation / IMU / star tracker (attitude still needed)
- Cabin / av-bay fans, lighting, radios/Ku as available
- Abort / CWS annunciators (will gain new Grenadier messages later)

## Obsolete (leave inert; do not drive Grenadier thrust)

| Family | Examples | Why |
|--------|----------|-----|
| SSME / MPS (most) | MPS He/Pc, MES lights, LO2/LH2, Sys B controllers | Single combined-cycle + CHARM |
| ET / SRB | ET umbilicals, ET static, booster | No stack |
| OMS (except arm→σ) | OMS TVC CWS, etc. | Vacuum Δv from σ3 / RCS |
| APU / HYD (as hydraulics) | APU fuel, hyd pumps (aliases only on operate/ctrl) | No SSME TVC hyd story |
| **Fuel cells** | `fuel-cell-reac-vlv*`, FC CWS | CHARM bus + flight battery; **inert** |
| Hypergol He for OMS/RCS | OMS He on MEDS | **LMP-103S** + Bradford/ECAPS-class HPGP (locked) |

## Repurpose (v1 bindings — implemented)

| Shuttle object / prop | Grenadier function | Property |
|----------------------|--------------------|----------|
| `apu-operate-1` | Ground cart ONLINE | `charm/ground-cart` |
| `apu-operate-2` | Flight battery ONLINE | `charm/battery-online` |
| `apu-operate-3` | Cryo ENABLE | `charm/cryo-enable` |
| `apu-ctrl-pwr-1` | Magnet ARM | `charm/magnet-arm` |
| `apu-ctrl-pwr-2` | Fuel services ENABLE | `charm/fuel-enable` |
| `apu-ctrl-pwr-3` | RF ENABLE | `charm/rf-enable` |
| `ctrl-pwr-sys-a-ac2-left` | CHARM LIGHT | `charm/light-cmd` |
| `ctrl-pwr-sys-a-ac1-ctr` | DEC ONLINE | `charm/dec-online` |
| `ctrl-pwr-sys-a-ac3-right` | Vacuum READY | `charm/vacuum-ready` |
| `main-eng-limit-shut-dn` → Enable | **SCRAM** | `charm/scram` |
| `oms-eng-left` / `oms-eng-right` | σ − / σ + | `engine/sigma` |
| Throttle axis | Engine throttle | `engine/throttle` (preferred) |

Tooltips for remapped switches are Grenadier-named (see [control_map.md](control_map.md)).
MEDS softkeys: STAGE / CHARM. Physical text-map engraving still Shuttle until UV pass.
Fuel-cell reactant valves are unwired to inert props.
