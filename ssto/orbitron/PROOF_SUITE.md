# Orbitron Proof Suite — interactive design validation

The **Proof Suite** is a step-by-step interactive application for the first-principles proof chain. Each stage has its own controls, matplotlib visualizations, metric cards, and gate text so you can **linger, tinker, and re-run** before moving on. It writes the same artifacts as the batch pipeline under `build/orbitron/chain/`.

**Companion docs:**

- Full chain specification (paths, gates, Tier 4): [`validation_steps.md`](validation_steps.md)
- Fidelity ladder & classic simulator: [`simulator/SIMULATOR.md`](simulator/SIMULATOR.md)
- Unobtanium specs: [`UNOBTANIUM.md`](UNOBTANIUM.md)

---

## Launch

```bash
poetry install --with simulator
./scripts/run_orbitron_proof_suite.sh
```

Uses the same Poetry + WarpX paths as [`stand.sh`](../stand.sh) (`tools/warpx_paths.sh`).

**Python version:** use **3.12 or 3.13** (not 3.15+). The project pins `python = ">=3.12,<3.15"` because PySide6 does not support 3.15 yet. If `poetry lock` fails with a PySide6 / Python 3.15 conflict, run `poetry env use python3.12` then `poetry lock` and `poetry install --with simulator`.

Entry point: [`scripts/run_orbitron_proof_suite.py`](../scripts/run_orbitron_proof_suite.py)  
Implementation: [`ssto/orbitron/simulator/proof_suite/`](simulator/proof_suite/)

---

## Window layout

| Area | Purpose |
|------|---------|
| **Left — Proof chain** | Step list with status icons; buttons to open chain folder, this doc, or the classic simulator |
| **Right — Step panel** | Banner, **Run this step** / **Refresh from artifacts**, gate strip, plots, metrics, log |

**Status icons**

| Icon | Meaning |
|------|---------|
| ○ | Pending — not run yet |
| ✓ | OK — step completed, gates look reasonable |
| △ | Warn — completed but shortfall / clump / validation issue |
| ⊘ | Skipped — e.g. PIC skipped (`SKIP_PIC`) |

After a successful **Run this step**, the navigator advances to the next step automatically. You can always click back to earlier steps to change inputs and re-run.

---

## Proof-mode rules (default)

When the suite runs (and when `ORBITRON_PROOF_CHAIN=1`):

| Rule | Effect |
|------|--------|
| `fusion_reactivity_scale = 1.0` | No tuned reactivity knob to force 3.5 MW |
| 100% physics blend | No surrogate / CSV calibration on gross power |
| No fusion-channel blend | Channel power does not inflate headline MW in proof mode |

**Step 09 (inverse solve)** temporarily disables proof mode so knobs can move. Use it only to document **minimum unobtanium** required if the forward chain misses target — that is **gap analysis**, not first-principles proof.

---

## Step-by-step: what to tinker and what you see

| Step | What you control | What you visualize |
|------|------------------|-------------------|
| **00 — Design SSOT** | r_anode, r_cathode, length, cathode kV, B, H₂ / B₂H₆ sccm | Full engine **s–r** layout, core cross-section, PICMI override status |
| **01 — WarpX PIC** | Pad console, **Live longitudinal s–r** (2 Hz), laminar ON/OFF, view (full duct / fusion channel / PIC), PIC steps | **Longitudinal heatmap** (full engine cut) + **transverse WarpX donut** + live log |
| **02 — PIC reduce** | Run after step 01 | ρ_e_norm / ρ_beam_norm bar chart and clamp band (0.2–3.0) |
| **03 — Fusion channel** | Laminar ON/OFF, **Cache OFF+ON pair**, view **Side-by-side**, time scrubber | **s–r** single or **OFF \| ON** heatmaps (cached), clump ON/OFF curves |
| **04 — Fueling** | Uses chain config + step 02 norms | n_p / n_B bars (log scale), ⟨σv⟩(T) curve with your T_i marked |
| **05 — p-¹¹B burn** | Proof burn only | Target MW vs computed P_fusion (honest shortfall) |
| **06 — 0D plant** | Proof plant | Steady-state output bars, U1–U4 stress chart, violations list |
| **07 — Jet closure** | Uses step 06 | P_jet vs P_from_thrust (F² discipline) |
| **08 — Validation export** | Full `validate_design` + YAML | Spec check table, **Open YAML** / **Open chain folder** |
| **09 — Inverse solve** | Optional | Required unobtanium scale factors vs nominal = 1 |

Step **03** is the closest match to [Orbitron-style clump / laminar video](https://youtu.be/_7Hfyz-JIDA?si=IBN4ZQmWwQKrITxY) intent, in a **longitudinal s–r** cut (along the bore), not the video’s axial end-on view.

**Step 03 side-by-side:** click **Cache laminar OFF+ON pair** once (runs ON and OFF, saves `fields_laminar_on.npz` and `fields_laminar_off.npz`). Then choose **Side-by-side OFF | ON** and scrub time — both panels update from cache without re-running.

**Step 01 live log:** WarpX stdout/stderr streams into the log pane while the PIC runs (subprocess line-by-line).

---

## Fixed artifact paths

All steps read/write under `build/orbitron/chain/` (see [`validation_steps.md`](validation_steps.md) for the full table). Examples:

| Artifact | Step |
|----------|------|
| `chain_config.json` | 00 — master config |
| `00_spec/picmi_overrides.json` | 00 |
| `01_pic/diags/` | 01 — WarpX plotfiles |
| `02_pic_norms/pic_norms.json` | 02 |
| `03_fusion_channel/fields.npz` | 03 — primary timelapse cache |
| `03_fusion_channel/fields_laminar_on.npz` | 03 — laminar ON (side-by-side) |
| `03_fusion_channel/fields_laminar_off.npz` | 03 — laminar OFF (side-by-side) |
| `08_export/design_validation.yaml` | 08 — spec export |

---

## Batch pipeline (same artifacts)

For CI or a one-shot reproducible run without the GUI:

```bash
chmod +x tools/orbitron_proof_chain/*.sh
tools/orbitron_proof_chain/run_all.sh

# No WarpX (unity ρ norms in step 02):
SKIP_PIC=1 tools/orbitron_proof_chain/run_all.sh

# Optional inverse after forward chain:
RUN_INVERSE=1 tools/orbitron_proof_chain/run_all.sh
```

**WarpX / pywarpx:** Use the same env as `./stand.sh` (Poetry + `WarpX/build/lib` on `PYTHONPATH` / `LD_LIBRARY_PATH`):

```bash
./scripts/run_orbitron_proof_suite.sh
```

Or after `eval "$(poetry env activate)"` and sourcing `tools/warpx_paths.sh`. Optional: `WARPX_PYTHON`, `WARPX_PYTHONPATH`. Without WarpX, enable **Skip WarpX** on step 01.

---

## Classic simulator

The original combined GUI is still available:

```bash
poetry run python scripts/run_orbitron_simulator.py
```

From the Proof Suite nav pane: **Open classic simulator…**

| Chain step | Classic tab |
|------------|-------------|
| 00 | Geometry / Injectants |
| 01–02 | Run WarpX PIC |
| 03 | Longitudinal 2D → fusion channel |
| 04–06 | Run 0D + pad startup |
| 07–08 | Validation → Export YAML |
| 09 | Solve unobtanium → target MW |

Use the **Proof Suite** when you want one dedicated panel per chain step. Use the **classic** app for combined exploration on one screen.

---

## Why you may see “design failed”

In **proof mode** at **Tier 3**, that is often **expected**, not a broken app:

- **P_fusion** may be far below **3.5 MW** because ⟨σv⟩ is an analytical fit and fueling uses sccm×τ/V, not full PIC transport (Tier 4).
- **U4 density** or other gates may fail with `fusion_reactivity_scale = 1`.

The suite is meant to show **where** the forward model breaks so you can iterate on geometry (00), PIC coupling (01–02), and laminar / clump behavior (03) before using **step 09** to quantify unobtanium margins for specs.

A failed `design_validated` in step 08 with a complete YAML export is still a **successful pipeline run** — inspect `spec_checks` and violations, then adjust design inputs and re-run earlier steps.

---

## Nav pane actions

| Button | Action |
|--------|--------|
| **Open chain folder** | Opens `build/orbitron/chain/` in the file manager |
| **Open validation_steps.md** | Opens the full chain specification |
| **Open classic simulator…** | Launches `scripts/run_orbitron_simulator.py` in a subprocess |

---

## Source layout

| Path | Role |
|------|------|
| `simulator/proof_suite/main_window.py` | Shell: navigator + stacked step panels |
| `simulator/proof_suite/state.py` | UI ↔ `chain_config.json` sync |
| `simulator/proof_suite/steps/step_00_02.py` | Panels 00–02 |
| `simulator/proof_suite/steps/step_03_05.py` | Panels 03–05 |
| `simulator/proof_suite/steps/step_06_09.py` | Panels 06–09 |
| `simulator/proof_chain/runners.py` | Step execution (shared with batch tools) |
| `tools/orbitron_proof_chain/` | Shell scripts for batch `run_all.sh` |

---

*Catskills Fusion SSTO — Orbitron Proof Suite*
