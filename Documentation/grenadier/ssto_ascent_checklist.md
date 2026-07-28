# SSTO ascent checklist (Grenadier TA)

Beginner path: **sit PLT (right seat)** for plant switches, use **center** for Stage ± / SCRAM / throttle. CDR can fly the stick, but the CHARM row lives on the **right sidewall (panel R2 area)** — from CDR you must look/lean right or switch seats.

CHARM mode `OFF → CRYO → ARM → LIGHT → POWER` is **derived**. You do **not** have a five-position mode switch. Watch the **CHARM** MEDS page.

## Where the live keys are

| What you need | Heritage object (hover name) | Where on the flightdeck |
|---------------|------------------------------|-------------------------|
| Ground cart | `apu-operate-1` → **Ground cart** | **Right wall** (PLT), APU operate row |
| Flight battery | `apu-operate-2` → **Flight battery** | same row |
| Cryo | `apu-operate-3` → **Cryo enable** | same row |
| Magnet | `apu-ctrl-pwr-1` → **Magnet arm** | **Right wall**, APU controller row |
| Fuel | `apu-ctrl-pwr-2` → **Fuel enable** | same |
| RF | `apu-ctrl-pwr-3` → **RF enable** | same |
| LIGHT | `ctrl-pwr-sys-a-ac2-left` → **CHARM LIGHT** | **Right wall**, Sys A controller trio |
| DEC | `ctrl-pwr-sys-a-ac1-ctr` → **DEC online** | same trio |
| Vacuum | `ctrl-pwr-sys-a-ac3-right` → **Vacuum ready** | same trio |
| Stage − / + | `oms-eng-left` / `oms-eng-right` | **Center console** (shared) |
| SCRAM | `main-eng-limit-shut-dn` → Enable | **Center** (shared) |
| Throttle | engine[0] lever | **Center** throttle |

If hover shows **nothing**, that switch is blanked (unused for Grenadier). Ignore it.

## CRT pages to use

On an MDU: **MAIN → SUBSYS STATUS**

| Softkey | Page | Use for |
|---------|------|---------|
| **CHARM** | plant | mode, cart/batt/cryo, magnet/fuel/RF, bus |
| **STAGE** | engine | Stage 1/2/3, throttle, seal, water, thrust |
| SPI | leave | not required for scramble |

Do **not** use DPS Fuel Cells or APU/HYD DISPs (titles blanked; heritage wallpaper).

## Scramble order

### 0. Seats / view
1. Prefer **PLT** view so the right-wall CHARM row is in front of you.
2. Open Cue cards → **CHARM startup** (menu) if you want the same steps as a popup.

### 1. Plant to POWER (right wall + CHARM CRT)
1. Ground cart → Online (and keep cart tied on pad if your checklist expects it).
2. Flight battery → Online.
3. Cryo enable → Enable. Wait until CHARM page shows cryo/magnet temperature going cold.
4. Magnet arm → Arm. Wait magnet current high (go-magnet).
5. Fuel enable → Enable.
6. Vacuum ready → Ready.
7. RF enable → Enable.
8. CHARM LIGHT → On.
9. DEC online → On.
10. Confirm **CHARM CRT mode = POWER** and bus MW rising.

### 2. Engine (center)
1. Stage = 1 (OMS L/R = Stage − / +).
2. Throttle up for takeoff roll.
3. Climb: Stage 2 when schedule/altitude allows (inlets open).
4. Before Stage 3: seal inlets; need water. Then Stage 3.
5. MECO / circularize on bus; RCS for attitude only (not main Δv).

### 3. If something breaks
- **SCRAM**: Main Eng Limit → **Enable** (center).
- Abort / divert cards only after that.

## CDR vs PLT — can one seat do everything?

| Function | CDR (left) | PLT (right) | Center |
|----------|------------|-------------|--------|
| Stick / flight | yes | yes | — |
| CHARM plant row | reach across / look right | **yes** | — |
| Stage ±, SCRAM, throttle | yes | yes | **yes** |
| MEDS CHARM/STAGE | yes (any MDU) | yes | — |

**Single-pilot scramble:** use **PLT** (or CDR with view slewed to the right wall). Dual-crew: PLT runs plant, CDR flies.

## Screenshots

Placeholder for FG grabs (reload aircraft after panel changes, then capture):

1. PLT view of right-wall APU/CHARM cluster with tooltips  
2. Center Stage ± and SCRAM  
3. CHARM MEDS page at POWER  
4. STAGE MEDS page at Stage 1  

Drop images next to this file as `ssto_ascent_checklist_*.png` when captured.

## Related

- [control_map.md](control_map.md) — full remap table  
- [panel_audit.md](panel_audit.md) — keep / obsolete / remapped  
- Cue cards menu: CHARM startup → Engine Stage 1/2/3 → Ascent profile (Plan A)
