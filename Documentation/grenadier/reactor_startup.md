# CHARM reactor startup — CATSKILLS-SSTO-TA-GRENADIER

Operator checklist for **Earth first light** of the bay-mounted CHARM plant.
Anchors: vehicle paper plant schematic (flight battery / ground cart → magnet PSU,
RF, cryo); space restart energy class 50–500 kWh; continuous \(p\)-¹¹B to ~1 GW bus.

FG property root: `/fdm/jsbsim/systems/grenadier/charm/`  
FG checklist: `CatskillsGrenadier-reactor-checklists.xml` (aircraft repo).

Legend: **INPUT** = crew/ground action. **√** = monitor/measurement go/no-go.

---

## 0. Preconditions (pad / hangar)

| Step | Action / measurement | INPUT / √ | Property / note |
|------|----------------------|-----------|-----------------|
| 0.1 | Vehicle cold / plant mode OFF | √ | `mode` = `OFF` |
| 0.2 | Bay doors status as required for cooling/access | INPUT | ops choice; not FDM-critical |
| 0.3 | √ Water tank quantity (shield buffer + engine feed) | √ | `../engine/water-kg` |
| 0.4 | √ p-¹¹B fuel services inventory | √ | `fuel-b11-kg`, `fuel-proton-kg` |
| 0.5 | √ Flight battery SoC ≥ restart reserve | √ | `battery-kwh` ≥ `battery-min-kwh` |
| 0.6 | Ground cart available (Earth first light) | INPUT | `ground-cart` = 1 |
| 0.7 | √ No active SCRAM latch (or reset authorized) | √ | `scram` = 0 |

---

## 1. Power path arm

| Step | Action / measurement | INPUT / √ | Property |
|------|----------------------|-----------|----------|
| 1.1 | Select startup source GROUND CART (Earth) | INPUT | `startup-source` = `CART` |
| 1.2 | Tie cart to magnet PSU / RF / cryo buses | INPUT | `cart-tied` = 1 |
| 1.3 | √ Bus voltage present on plant aux | √ | `aux-bus-v` in band |
| 1.4 | Flight battery ONLINE (float / backup) | INPUT | `battery-online` = 1 |

*(Space restart: set `startup-source` = `BATTERY`, skip cart; budget ≤ ~300–500 kWh.)*

---

## 2. Cryo and magnets

| Step | Action / measurement | INPUT / √ | Property |
|------|----------------------|-----------|----------|
| 2.1 | Cryo compressor bay ENABLE | INPUT | `cryo-enable` = 1 |
| 2.2 | √ Cryo load / cold-head proxy in band | √ | `cryo-kw`, `magnet-t-k` |
| 2.3 | Magnet PSU ARM | INPUT | `magnet-arm` = 1 |
| 2.4 | √ Magnet current ramp complete | √ | `magnet-i-frac` ≥ 0.95 |
| 2.5 | Mode → CRYO | auto / √ | `mode` = `CRYO` |

---

## 3. Fuel and vacuum

| Step | Action / measurement | INPUT / √ | Property |
|------|----------------------|-----------|----------|
| 3.1 | Fuel services ENABLE (proton + ¹¹B feed) | INPUT | `fuel-enable` = 1 |
| 3.2 | √ Injector / tank pressures nominal | √ | `fuel-ready` = 1 |
| 3.3 | Vacuum / chamber READY | INPUT | `vacuum-ready` = 1 |
| 3.4 | Mode → ARM | INPUT | `mode` = `ARM` |

---

## 4. RF / rotation light-off

| Step | Action / measurement | INPUT / √ | Property |
|------|----------------------|-----------|----------|
| 4.1 | RF rack ENABLE | INPUT | `rf-enable` = 1 |
| 4.2 | CHARM LIGHT (pilot chamber) | INPUT | `light-cmd` = 1 |
| 4.3 | √ Plasma / confinement proxies rising | √ | `plasma-proxy` rising |
| 4.4 | Mode → LIGHT | auto | `mode` = `LIGHT` |
| 4.5 | DEC ONLINE when ordered α/wave channel ready | INPUT | `dec-online` = 1 |
| 4.6 | √ Gross bus power climbing | √ | `bus-mw` > 0 |
| 4.7 | Mode → POWER | auto when bus ≥ threshold | `mode` = `POWER` |
| 4.8 | Detie ground cart; plant self-sustaining | INPUT | `cart-tied` = 0 |

---

## 5. Aborts / safing

| Condition | Action |
|-----------|--------|
| Any hard trip | `scram` = 1 → mode SCRAM; RF/magnets/fuel inhibit |
| Bus undervolt in POWER | derate engine demand; CWS |
| Water empty (engine σ3) | engine inhibit; plant may remain POWER |
| Planned shutdown | POWER → ARM → CRYO → OFF per reverse sequence |

---

## Measurements summary (startup screen)

- Tanks: `fuel-b11-kg`, `fuel-proton-kg`, `../engine/water-kg`, `battery-kwh`
- State: `mode`, `scram`, `cryo-enable`, `magnet-arm`, `magnet-i-frac`, `rf-enable`, `dec-online`
- Power: `aux-bus-v`, `bus-mw`, `cryo-kw`, `recirc-mw`
