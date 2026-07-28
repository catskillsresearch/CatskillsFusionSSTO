# Plan A FDM pack (JSBSim)

Makes the **simulator** see Plan A size/weight. Visual mesh is still heritage Shuttle.

Source: `arxiv.md` §1.2b. File: `shuttle.xml`.

## Scaled metrics

| Quantity | Heritage | Plan A |
|----------|----------|--------|
| Wing area | 2691 ft² (250 m²) | **5167 ft² (480 m²)** |
| Span | 78.1 ft (23.8 m) | **108.3 ft (33 m)** |
| Chord | 34.5 ft | **47.7 ft** |
| Empty weight | 180 000 lb | **378 534 lb (~171.7 t dry, no cargo)** |
| Ixx / Iyy / Izz | stock | × ~4.07 (`m_ratio × size²`) |
| CG / AERORP x | 2.70 m | **3.77 m** (×1.396 length) |

## Gear

- Nose x **−20.94 m**, mains x **5.03 m**, track y **±5.82 m**
- z kept **−7.97 m** (level park)
- Spring/damping × ~2.10 (mass ratio)

## What is *not* changed

- Aero **coefficient** tables (Shuttle CL/CD/Cm) — first-order flyability only
- Exterior AC mesh — still looks stock-sized
- Grenadier thrust model — same peak force → lower T/W at Plan A mass (expected)

## How to sniff-test

1. `./fs.sh` → KEDW 22L, cold level park  
2. Check `/fdm/jsbsim/metrics/Sw-sqft` ≈ 5167, `/fdm/jsbsim/inertia/empty-weight-lbs` ≈ 378534  
3. Bring plant up, roll / rotate / climb — judge wing loading and inertia feel vs stock OV
