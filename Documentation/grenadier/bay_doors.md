# Payload bay doors (Grenadier TA)

## Open sequence (auto)

Menu **CatskillsFusionSSTO → Mechanical** (or the Mechanical dialog):

1. Enable **SYS 1** and/or **SYS 2** (`pb-door-sys1-enable` / `pb-door-sys2-enable`) — needed for `pb-door-power`.
2. Set **Payload bay door** slider to **open** (`pb-door-auto-switch` = `1`).

Auto stages (`Nasal/housekeeping.nas` → `payload_bay_door_open_auto`):

| Stage | Action |
|------:|--------|
| 0 | Unlatch centerline gangs 5–8 & 9–12 (~24 s) |
| 1 | Unlatch centerline gangs 1–4 & 13–16 (~24 s) |
| 2 | Unlatch right door fwd/aft (~34 s) |
| 3 | Open right door (~68 s) |
| 4 | Unlatch left door fwd/aft (~34 s) |
| 5 | Open left door (~68 s) |

Close: slider to **close** (`-1`). Blocked if `|T_left − T_right| > 60 K` or no door power.

Cockpit: same props on the payload-bay door panel (`Models/cockpit.xml`).

## What you should see (Plan A TA)

Bay = **fusion plant skid** from `assembly.json` (no cargo, no assembly-name boxes):

- Forward→aft: **battery** → **water** → **fuel** (proton / B11 / injector) → **shield** → **chamber L | HEX | chamber R** + magnets, cryostats, cryocoolers, RF, DEC, MAG PSU, drive, coolant, vacuum, plant bus
- Aft wall stays; **bus hole** only to the 3-cycle (no engine poke box in the bay)
- 3-cycle is jammed in **nozzle + OMS pods**: EDF, precomp, MW farm, MW applicator, vaporizer, S3 plasma, H2O injector, inlets/plenum

OMS engine bells/bases are removed from `OMSPods_grenadier.ac` (RCS only; pod volume reused for MW/precomp).

Rebuild:

```bash
python3 Models/Grenadier/build_grenadier_bay_and_te.py
python3 Models/Grenadier/build_grenadier_propulsion_ac.py
```
