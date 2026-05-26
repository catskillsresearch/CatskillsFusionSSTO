### Purpose

Reproducible **integration + physics-envelope** benchmark: CAD layout, WarpX PIC electron loading,
0D plant closure with U1–U4 gates, and unobtanium inverse. **Not** a license to operate a reactor or a
claim that p-¹¹B Orbitron fusion is demonstrated at 3.5 MW.

### Validation levels

Claims in this report are tagged by **level** — what each part of the toolchain is allowed to prove:

| Level | Mechanism | What it proves |
|-------|-----------|----------------|
| **0** | Pad interlock sequence | Correct startup order before fueling and reaction |
| **1** | 0D plant + U1–U4 gates | **3.5 MW** headline, jet closure, materials limits (per σv branch) |
| **2** | WarpX PIC (electron ring) | Density and E×B loading at design voltage — **not** fusion gain |
| **3** | p-¹¹B channel + burn models | ⟨σv⟩(T_i) × fueling × volume; laminar / clump checks |
| **4** | *Future* | Transport-integrated reactivity without analytical surrogate blend |

Never write “WarpX proves 3.5 MW.” Level **2** validates electrons in prescribed fields only; level **1**
is plant accounting at the chosen reactivity branch.

**HTS** — **high-temperature superconductor** bore magnet (U3). **REBCO** — **rare-earth barium copper
oxide** tape; **YBCO** (yttrium barium copper oxide) is the common member of that family. Both are used
below as published anchors for achievable field in compact solenoids.

### Three scenarios (only these)

| ID | Name | σv model | Geometry / knobs |
|----|------|----------|------------------|
| **pretend** | (a) Design target | design (calibrated) | 600 kV, 2 T, unity U1–U4 |
| **today** | (b) COTS + experiment | literature | Avalanche-class **300 kV**; same pad fueling as (a); wall/HTS at published limits |
| **minimum** | (c) Inverse minimum | literature | Constrained stress inverse (literature σv) |

**No** aspirational “5-year SOTA” forward row. R&D narrative lives in gap analysis, not a second pretend run.

#### (a) Pretend

- Primary **proof chain** (steps 0–8) runs here.
- **Design validated** at level **1** means **calibrated plant closure**, not measured fusion yield.
- WarpX step 01 figures are labeled **design-point (a)** (level **2**).

#### (b) Today

- **Fusion:** literature ⟨σv⟩ only (literature peak in the p-¹¹B reactivity model).
- **Pad fueling:** same H₂ flow, laser rate, and throttle as (a) — shortfall is physics/materials, not retuned fuel.
- **Voltage:** Avalanche Orbitron public milestone **300 kV sustained** (D₂ hardware; topology anchor for Orbitron-class, not p-¹¹B yield).
- **U2 wall:** ~**1.0 MW/m²** steady limit class (tokamak/DEMO PFC scoping).
- **U3 HTS:** **0.8 T** effective bore vs 2 T design → HTS capability scale **0.4** (REBCO ~0.8 T @ 77 K class demos).

#### (c) Minimum

- **Constrained stress inverse** on literature σv: minimize fusion reactivity scale η_react subject to gross power ≥ target and U1–U4 inequalities (Levenberg–Marquardt / trust-region least squares on constraint residuals).
- **success = true** only if design validated and no hard spec FAIL — otherwise **(c) is infeasible**.
- **Margin inverse:** design σv; minimize knob distance from nominal under the same gates — should approximate **(a)**.

### Inverse solver rules

- **Stress (c):** find the **minimum** η_react (on literature σv) for which a feasible point exists; do not treat power-only fits as solutions.
- **Margin (a check):** design σv; prefer knobs near 1.0×.
- **Forward confirmation:** design σv at margin-inverse knobs — internal consistency only.

### Report outputs

1. **Scenario comparison table** — (a)(b)(c): gross power, σv branch ratio, effective gap, level-1 gates pass.
2. **Stress section** — η_react required, design/literature ⟨σv⟩ ratio at operating ion temperature.
3. **PIC** — design-point (a) unless a second run is added later.

**Gate before publishing:** (b) gross power must be **much** lower than (a). If not, (b) anchors are wrong.

### Non-goals

- No secondary “judgment” scenario row beyond (a)(b)(c).
- Gap narrative does not override solver numbers.
