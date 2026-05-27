# Radial thermal zoning — Orbitron p-¹¹B direct-cycle

Normative layout for the **fusion-heated Brayton** engine. Resolves the apparent contradiction between
**cryogenic HTS magnets** and **hot compressed air** by **inside-out zoning** with vacuum insulation.

## Not a neutron-heated blanket

p-¹¹B is **aneutronic**: energy leaves as **⁴He alphas**, **bremsstrahlung X-rays**, and **charge-exchange /
lost ions** — not as a significant neutron flux. The **first wall (anode sheath)** absorbs this load; there is
no tokamak-style **8 GK bulk** fluid thermalizing against the magnet.

## Inside-out radial stack (design default)

Axisymmetric radii for the Phase-1 benchmark (`r_anode_m = 0.04 m`, `r_cathode_m = 0.01 m`):

| Zone | Radius [m] | Role |
|------|------------|------|
| Cathode wire | 0 → 0.01 | On-axis **−600 kV** emitter |
| Plasma orbit volume | 0.01 → 0.04 | High-vacuum E×B + beams; **not** Brayton working fluid |
| **First wall / anode** | **0.04** | Catches **α**, **X-ray**, **CX**; runs **800–1000 °C** class |
| **Air annulus** | 0.04 → **0.06** | Compressed **air** convects on hot wall; **heats air** for Brayton |
| **Cryostat vacuum + MLI** | 0.06 → **0.075** | Blocks conduction/convection; limits radiative leak to magnet |
| **HTS solenoid** | 0.075 → **0.10** | **2 T** field; **~113 K** via liquid **CH₄** (U3) |
| Outer casing | > 0.10 | Structure, feedthroughs, services |

**Total bore OD ≈ 20 cm** at the magnet — tight but intentional for compact SSTO class.

```
  [cathode] — [plasma vacuum] — [FIRST WALL hot]
                                    |
                         [AIR annulus  T~compressor→turbine]
                                    |
                    ===== cryostat vacuum + MLI =====
                                    |
                         [HTS magnet  cold, B through vacuum]
```

## Two thermal systems (never one “jacket”)

| System | Fluid | Temperature | Job |
|--------|-------|-------------|-----|
| **U2 — First-wall intercept** | Liquid **CH₄** | ~113 K | Remove **high-grade** wall load (X-ray / α / CX) so the sheath does not melt |
| **Brayton — Propulsion** | Compressed **air** | T₂ → T₃ | Pick up enthalpy from **hot first-wall outer face** + **ash mixer**; **never** wash the HTS pack |
| **U3 — Magnet cryostat** | Liquid **CH₄** (closed loop) | ~113 K | Remove **parasitic leak** through MLI (~0.1–0.5 kW class in 0D placeholder) |

The magnet is **outside** the hot air path. **B** passes through vacuum and structure; **heat** does not.

## Energy accounting (0D plant)

At armed operation the model splits:

1. **`first_wall_kw`** — boundary deposition anchor (~400 kW scale at full command).
2. **`ch4_wall_intercept_kw`** — fraction removed by internal CH₄ (must close U2 flux limits).
3. **`air_annulus_kw`** — remainder delivered to the Brayton air stream (convection on hot wall).
4. **`magnet_cryo_kw`** — HTS cryostat load (U3), independent of air temperature.
5. **`brayton_thermal_kw`** — `air_annulus_kw` + small **ash mixer** enthalpy; drives jet surrogate, **not** the full fusion `gross_mw` unless explicitly stated.

**Honesty:** Level-1 closure can pass while **cryostat mass, refrigeration power, and HX area** remain underspecified — flagged in gap analysis.

## R&D gaps (benchmark)

- Cryostat + MLI mass/volume at the radial budget above
- Intermediate **CH₄ vapor / secondary loop** to a **liquid-to-air HX** if annulus convection is insufficient for T₃
- Measured **effective ⟨σv⟩** in the well (still the dominant MW gap on literature σv)
