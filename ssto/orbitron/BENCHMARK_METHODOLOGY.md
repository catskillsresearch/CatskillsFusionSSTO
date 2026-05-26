# Orbitron in-silico benchmark methodology

Normative rules for the **Orbitron Direct Cycle p-¹¹B** experiment report. Machine-readable anchors:
[`scenario_anchors.yaml`](scenario_anchors.yaml). Proof-chain ops: [`PROOF_PROCESS.md`](PROOF_PROCESS.md).

## Purpose

Reproducible **integration + physics-envelope** benchmark: CAD, WarpX PIC (Tier 2), 0D plant (Tier 1),
and unobtanium inverse. **Not** a license to operate a reactor or a claim that p-¹¹B Orbitron fusion
is demonstrated at 3.5 MW.

## Three scenarios (only these)

| ID | Name | σv model | Geometry / knobs |
|----|------|----------|------------------|
| **pretend** | (a) Design target | `design` (calibrated) | Experiment YAML: 600 kV, 2 T, unity U1–U4 |
| **today** | (b) COTS + experiment | `literature` | Avalanche-class **300 kV**; same pad fueling as (a); wall/HTS at published limits |
| **minimum** | (c) Inverse minimum | `literature` | Stress-inverse solver output (no near-nominal penalty) |

**No** aspirational “5-year SOTA” forward row. R&D narrative lives in gap analysis, not a second pretend run.

### (a) Pretend

- Primary **proof chain** (steps 0–8) runs here.
- Tier-1 `design_validated` means **calibrated plant closure**, not measured fusion yield.
- WarpX step 01 figures are labeled **design-point (a)**.

### (b) Today

- **Fusion:** literature ⟨σv⟩ only (`fusion_pb11.py` literature peak).
- **Pad fueling:** same `h2_sccm`, laser Hz, throttle as (a) — shortfall is physics/materials, not retuned fuel.
- **Voltage:** Avalanche Orbitron public milestone **300 kV sustained** (D₂ hardware; topology anchor for Orbitron-class, not p-¹¹B yield).
- **U2 wall:** ~**1.0 MW/m²** steady limit class (tokamak/DEMO PFC scoping).
- **U3 HTS:** **0.8 T** effective bore vs 2 T design → `hts_capability_scale = 0.4` (REBCO ~0.8 T @ 77 K class demos).
- **Provenance:** every (b) override has a `source` string in `scenario_anchors.yaml`.

### (c) Minimum

- **Constrained stress inverse** (`solve_constrained.py`, least-squares + η search): literature σv;
  **minimize** `fusion_reactivity_scale` subject to power ≥ target and U1–U4 inequalities.
- **`success=True` only if** `design_validated` and no hard spec FAIL — otherwise **(c) infeasible**.
- **Margin inverse:** design σv; minimize knob distance from nominal under the same gates — should ≈ **(a)**.

## Fidelity ladder (claims)

| Tier | Mechanism | Claim |
|------|-----------|--------|
| 0 | Pad interlocks | Startup order |
| 1 | `plant_0d` + U1–U4 | MW closure **per σv branch** |
| 2 | WarpX PIC | Electron E×B loading — **not** fusion Q |
| 3 | `fusion_pb11` | Analytical ⟨σv⟩ × fueling |
| 4 | Future | Transport-integrated reactivity |

Never write “WarpX proves 3.5 MW.”

## Inverse solver rules

- **Stress (c):** minimize \(|P - P_\text{target}|\) + violation penalty; **do not** penalize large knob moves.
- **Margin (a check):** design σv; prefer knobs near 1.0×.
- **Forward confirmation:** design σv @ (c) knobs — internal consistency only.

## Report outputs

1. **Scenario comparison table** — (a)(b)(c): \(P_\text{gross}\), σv branch ratio, effective gap, Tier-1 valid.
2. **Stress section** — `fusion_reactivity_scale` required, `design_over_literature` at operating \(T_i\).
3. **PIC** — design-point (a) unless a second run is added later.

## Build / run order

```bash
./stand.sh
./scripts/run_orbitron_experiment.sh experiments/orbitron_phase1_power_target.yaml
# optional fast narrative-only:
./scripts/regenerate_orbitron_report.sh reports/<run-dir>
```

**Gate before publishing:** (b) \(P_\text{gross}\) must be **much** lower than (a). If not, (b) anchors are wrong.

## Non-goals

- No (b₂) judgment scenario YAML.
- Gap-agent prose does not override solver numbers.
