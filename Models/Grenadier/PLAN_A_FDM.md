# Plan A FDM pack (JSBSim) + visual wing stretch

Makes the **simulator** see Plan A size/weight, and the **exterior mesh** show Plan A wings.

Source: `arxiv.md` §1.2b. Files: `shuttle.xml`, `Models/shuttle_o2_plan_a.ac`.

## Scaled metrics (FDM)

| Quantity | Heritage | Plan A |
|----------|----------|--------|
| Wing area | 2691 ft² (250 m²) | **5167 ft² (480 m²)** |
| Span | 78.1 ft (23.8 m) | **108.3 ft (33 m)** |
| Chord | 34.5 ft | **47.7 ft** |
| Empty weight | 180 000 lb | **378 534 lb (~171.7 t dry, no cargo)** |
| Ixx / Iyy / Izz | stock | × ~4.07 (`m_ratio × size²`) |
| CG / AERORP x | 2.70 m | **3.77 m** (×1.396 length) |

## Visual wing (`shuttle_o2_plan_a.ac`)

Built by `Models/Grenadier/build_plan_a_wings.py` from `shuttle_o2_heritage.ac`:

- Span ×**1.387** (tip-to-tip ≈ **33 m**) — continuous map outboard of fuselage wall (|Z|≳3.6 m)
- Chord ×**1.385** about root LE (x≈−1.5 m) on wing-weighted verts
- Objects: `fuselage`, `heatshield`, elevons, gear doors
- Fuselage length / bay width **not** stretched (packaging deferred)
- Elevon hinges, wingtip vortices, wing-strike points updated in `SpaceShuttle.xml`
- After stretch, wing TE verts are pulled aft onto the elevon LE (straight flap line) — no TE overlay patches

Rebuild: `python3 Models/Grenadier/build_plan_a_wings.py`

## Gear

- Nose x **−20.94 m**, mains x **5.03 m**, track y **±5.82 m**
- z kept **−7.97 m** (level park)
- Spring/damping × ~2.10 (mass ratio)

## What is *not* changed

- Aero **coefficient** tables (Shuttle CL/CD/Cm) — first-order flyability only
- Fuselage packaging length (still heritage visual length; FDM CG uses Plan A length scale)
- Grenadier thrust model — same peak force → lower T/W at Plan A mass (expected)

## How to sniff-test

1. `./fs.sh` → KEDW 22, cold level park
2. Top-down view: wings should read clearly wider than stock OV (~33 m tip-to-tip)
3. Check `/fdm/jsbsim/metrics/Sw-sqft` ≈ 5167, `/fdm/jsbsim/inertia/empty-weight-lbs` ≈ 378534
4. Bring plant up, roll / rotate / climb — wing loading and inertia vs stock OV
