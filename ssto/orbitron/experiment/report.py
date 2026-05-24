"""Assemble narrative Markdown experiment report."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ssto.orbitron.experiment.assembly_narrative import (
    render_assembly_section_md,
    stage_assembly_figures,
    stand_build_dir,
)
from ssto.orbitron.experiment.forward_scenarios import scenarios_table_md
from ssto.orbitron.experiment.narrative import load_validation_narratives, md_math_for_preview, narrative_for_step
from ssto.orbitron.experiment.report_formatting import parameters_tables_md, step_results_md
from ssto.orbitron.experiment.runner import ExperimentRunResult


STEP_TITLES = {
    0: "Design compile (SSOT)",
    1: "Electron-ring WarpX (PIC)",
    2: "PIC reduce → ρ_e_norm",
    3: "Fusion channel (s–r)",
    4: "Fueling densities",
    5: "p-¹¹B burn power",
    6: "0D plant + U1–U4",
    7: "Jet closure",
    8: "Validation export",
    9: "Inverse unobtanium solve",
}

GAP_STEP_TITLES = {
    "05_gap": "p-¹¹B burn (gap-closed knobs)",
    "06_gap": "0D plant (gap-closed knobs)",
    "07_gap": "Jet closure (gap-closed)",
    "08_gap": "Validation export (gap-closed)",
}

# Figures to embed per step (logical key → caption)
STEP_FIGURES: dict[int, list[tuple[str, str]]] = {
    0: [("step00", "Engine layout (fusion channel focus)")],
    1: [("step01", "WarpX |ρ_e| — final snapshot")],
    2: [("step02", "Electron ring normalization")],
    3: [
        ("step03_density", "Fuel density n(s,r) — OFF | ON | log10(OFF/ON); per-panel color scale"),
        ("step03_reaction", "Reaction rate R(s,r) — OFF | ON | log10(OFF/ON); per-panel color scale"),
        ("step03_clump", "Clump index C_k vs time (OFF/ON ratio in title)"),
        ("step03_radial", "⟨n⟩_s(r) at final frame — drop at dashed line is bore wall r_anode"),
    ],
    4: [("step04", "Proton and boron densities")],
    5: [("step05", "P_fusion vs 3.5 MW target (values labeled; log scale when shortfall large)")],
    6: [
        ("step06_outputs", "Plant outputs in separate unit panels (MW, mA, kN, kg/s)"),
        ("step06_u", "U1–U4 stress ratios (U4 = mA / 1 mA minimum spec)"),
    ],
    7: [("step07", "Jet power closure")],
}

STEP_FIGURES_GAP: dict[str, list[tuple[str, str]]] = {
    "05_gap": [("step05_gap", "P_fusion with gap-closed unobtanium knobs")],
    "06_gap": [
        ("step06_gap_outputs", "Plant outputs (gap-closed)"),
        ("step06_gap_u", "U stress (gap-closed)"),
    ],
    "07_gap": [("step07_gap", "Jet closure (gap-closed)")],
}


def _render_forward_scenarios_section(fwd: dict[str, Any]) -> str:
    lines = [
        "## Forward performance (unobtanium scenarios)\n\n",
        "These are **forward** predictions with the **design-calibrated** plant model: "
        "if the rig achieves the listed knob values, what MW and Tier-1 gates result?\n\n",
        "### How this differs from step 09 inverse\n\n",
        "| Question | Step 09 stress inverse | This section |\n",
        "|----------|------------------------|--------------|\n",
        "| What is it? | Optimizer **minimum** knobs under **literature** σv | "
        "Named **engineering** knob sets you choose |\n",
        "| Reactivity model | Literature (honest, usually cannot hit 3.5 MW) | "
        "Design (predicts rig performance) |\n",
        "| Use | Gap factors vs nominal; CNF check | "
        "**5-year SOTA** planning and expected MW |\n\n",
        "**CNF (confirmation):** if stress-inverse knobs are built, the **design** model "
        "should reach ≥ target MW — that does **not** mean literature σv already hits target.\n\n",
        scenarios_table_md(fwd),
    ]
    for row in fwd.get("scenarios") or []:
        if row.get("id") in ("five_year_sota", "stretch_sota", "stress_inverse_minimum"):
            lines.append(f"#### {row.get('label')}\n\n")
            desc = (row.get("description") or "").strip()
            if desc:
                lines.append(desc + "\n\n")
            lines.append(
                f"- **P_gross:** {row.get('gross_power_mw', 0):.3f} MW  \n"
                f"- **Tier-1 validated:** {row.get('design_validated')}  \n"
            )
            if row.get("violations"):
                lines.append(f"- **Violations:** {', '.join(row['violations'][:3])}\n")
            lines.append("\n")
    lines.append(
        f"*Edit scenarios in `ssto/orbitron/unobtanium_scenarios.yaml` and re-run the experiment.*\n"
    )
    return "".join(lines)


def _render_physics_audit_section(physics: dict[str, Any]) -> str:
    lines = ["## Physics evidence audit\n\n", f"**{physics.get('summary', '')}**\n\n"]
    lit = physics.get("literature_forward_mw")
    conf = physics.get("confirmation_design_mw")
    if lit is not None:
        lines.append(f"- Literature σv forward @ nominal knobs: **{lit:.3f} MW**\n")
    if conf is not None:
        ok = physics.get("confirmation_passes")
        lines.append(
            f"- Forward confirmation (design σv @ stress-required knobs): "
            f"**{conf:.3f} MW** ({'PASS' if ok else 'FAIL'})\n"
        )
    stress = physics.get("gap_factors_stress") or {}
    if stress:
        lines.append("\n### Stress inverse gap factors (honest goals)\n\n")
        lines.append("| Knob | Required / nominal |\n|------|-------------------|\n")
        for key in sorted(stress):
            lines.append(f"| `{key}` | **{stress[key]:.3f}×** |\n")
    holdout = physics.get("calibration_holdout") or []
    if holdout:
        lines.append("\n### ⟨σv⟩ calibration hold-out\n\n")
        lines.append("| Point | T [keV] | design / literature |\n|-------|---------|---------------------|\n")
        for row in holdout:
            lines.append(
                f"| {row.get('label')} | {row.get('T_kev', 0):.0f} | "
                f"{row.get('design_over_literature', 0):.1f}× |\n"
            )
    checks = physics.get("checks") or []
    if checks:
        lines.append("\n### Audit checks\n\n")
        lines.append("| ID | Status | Required | Achieved |\n|----|--------|----------|----------|\n")
        for c in checks:
            lines.append(
                f"| {c.get('spec_id')} | {c.get('status')} | {c.get('required')} | {c.get('achieved')} |\n"
            )
    return "".join(lines)


def _render_gap_analysis_section(result: ExperimentRunResult, report_dir: Path) -> str:
    """Technology gap narrative — always near the top when step 09 ran."""
    if "09" not in result.step_results:
        return ""
    gap_md = report_dir / "UNOBTANIUM_GAP.md"
    lines: list[str] = []
    lines.append("## Technology gap analysis (step 09 inverse)\n\n")
    mode = result.gap_analysis_mode or "unknown"
    if mode == "cursor":
        lines.append(
            "*Generated by the Cursor gap agent (literature + web search). "
            "Also saved as `UNOBTANIUM_GAP.md`.*\n\n"
        )
    elif mode == "template":
        lines.append(
            "*Template gap review from step 09 stress-inverse numbers "
            "(no Cursor agent — re-run without `--no-gap-agent` for AI narrative). "
            "Also saved as `UNOBTANIUM_GAP.md`.*\n\n"
        )
    if gap_md.is_file():
        lines.append(md_math_for_preview(gap_md.read_text(encoding="utf-8")))
        lines.append("\n")
    else:
        lines.append(
            "*Gap file missing — check `run.log` for step 09 / gap agent errors.*\n\n"
        )
    return "".join(lines)


def _embed_figure(report_dir: Path, figures: dict[str, str | None], key: str, caption: str) -> str:
    name = figures.get(key)
    if not name:
        return f"*(Figure unavailable: {caption})*\n\n"
    rel = f"figures/{name}"
    return f"![{caption}]({rel})\n\n*{caption}*\n\n"


def write_experiment_report(
    result: ExperimentRunResult,
    *,
    run_date: datetime | None = None,
) -> Path:
    """Write ``REPORT.md`` into the experiment report directory."""
    report_dir = result.report_dir
    when = run_date or datetime.now()
    date_str = when.strftime("%Y-%m-%d %H:%M")
    equations, operations = load_validation_narratives()

    lines: list[str] = []
    lines.append(f"# {result.experiment.experiment_name}\n\n")
    lines.append(f"**Run date:** {date_str}  \n")
    lines.append(f"**Report directory:** `{report_dir}`  \n")
    tier1 = result.tier1_design_validated
    phys = result.physics_evidence
    if result.success and phys:
        status = "SUCCESS (Tier-1 + physics evidence)"
    elif result.success and tier1:
        status = "TIER-1 OK — physics evidence incomplete (see audit below)"
    elif result.error:
        status = f"FAILED — {result.error}"
    else:
        status = "FAILED — Tier-1 design validation"
    lines.append(f"**Status:** {status}  \n")
    if tier1 is not None:
        lines.append(f"**Tier-1 design validated:** {tier1}  \n")
    if phys is not None:
        lines.append(f"**Physics evidence:** {phys}  \n")
    if result.gap_analysis_path:
        lines.append(
            f"**Gap analysis:** embedded below ({result.gap_analysis_mode or 'unknown'}); "
            f"see also `{Path(result.gap_analysis_path).name}`  \n"
        )
    lines.append("\n")

    if result.experiment.description:
        lines.append("## Experiment description\n\n")
        lines.append(result.experiment.description.strip() + "\n\n")

    staged = stage_assembly_figures(report_dir)
    lines.append(
        render_assembly_section_md(
            staged=staged,
            stand_build=stand_build_dir(),
            parameters=result.parameters,
        )
    )

    lines.append("## Parameter settings\n\n")
    lines.append(parameters_tables_md(result.parameters))
    lines.append(
        "Pad interlocks (**CTRL-01**) must be satisfied "
        "(APU → starter → bleed → vacuum → laser → HV → IGNITE) or **INJ-***/**CORE-01** fuel "
        "injection and reaction rate stay at zero.\n\n"
    )

    if "physics" in result.step_results:
        lines.append(_render_physics_audit_section(result.step_results["physics"]))
        lines.append("\n")

    if "forward" in result.step_results:
        lines.append(_render_forward_scenarios_section(result.step_results["forward"]))
        lines.append("\n")

    gap_block = _render_gap_analysis_section(result, report_dir)
    if gap_block:
        lines.append(gap_block)

    lines.append("## Fidelity and proof-mode rules\n\n")
    lines.append(
        "### What this report can and cannot prove\n\n"
        "| Claim | Mechanism | Falsifiable? |\n"
        "|-------|-----------|-------------|\n"
        "| **Tier-1 design closure** | Calibrated `fusion_pb11` ⟨σv⟩ + U1–U4 gates + jet closure | "
        "Yes — per-spec pass/fail |\n"
        "| **Honest unobtanium goals** | Step 09 **stress inverse**: literature σv (~3× lower peak), "
        "pessimistic knob start | Yes — gap factors ≫ 1 if physics is hard |\n"
        "| **Attain goals → target power** | **CNF** check: design σv @ stress-required knobs | "
        "Yes — confirmation MW must hit 3.5 ± tol |\n"
        "| **p-¹¹B burn in hardware** | Not in this chain | No — needs experiments (α, n, beam, 600 kV) |\n"
        "| **WarpX fusion Q** | Electron-ring PIC only | No — density/beam proxies only |\n\n"
    )
    lines.append(
        "- **Proof-forward (steps 00–08):** `ORBITRON_PROOF_CHAIN=1` — design-calibrated reactivity, "
        "`fusion_reactivity_scale` fixed at 1.0.\n"
        "- **U1 gate:** program limit **2×10⁷ V/m** @ margin 1 (not legacy 3 GV/m placeholder).\n"
        "- **Step 09 (default):** **stress** inverse (literature σv), plus margin audit if Tier-1 passed; "
        "then gap-closed 05–08 with solved knobs on **design** σv. `--no-inverse` to skip.\n"
        "- **Physics audit:** runs after step 08 (`results/step_physics.json`). "
        "Set `run.require_pic: true` to require WarpX ρ_e proxy.\n"
        "- **Gap agent:** runs after step 09 by default; writes `UNOBTANIUM_GAP.md` and embeds it "
        "in **Technology gap analysis** above. `--no-gap-agent` skips Cursor but still writes the "
        "template table from inverse numbers.\n"
        "- WarpX step 01: electron-ring-only (τ, cathode pulse); not p-¹¹B fusion yield.\n\n"
    )

    lines.append("## Chain results summary\n\n")
    lines.append("| Step | Key metrics |\n|------|-------------|\n")
    for step_id in sorted(result.step_results.keys(), key=_step_sort_key):
        data = result.step_results[step_id]
        lines.append(f"| {step_id} | {_step_metrics_row(step_id, data)} |\n")
    lines.append("\n")

    for step_num in range(9):
        sid = f"{step_num:02d}"
        if sid not in result.step_results:
            continue

        lines.append(f"## Step {step_num} — {STEP_TITLES.get(step_num, sid)}\n\n")
        lines.append("### Mathematics and narrative (from validation_steps.md)\n\n")
        lines.append(narrative_for_step(step_num, equations=equations, operations=operations))
        lines.append("\n\n")

        lines.append("### Results (proof-forward)\n\n")
        lines.append(step_results_md(sid, result.step_results[sid]))

        for fig_key, caption in STEP_FIGURES.get(step_num, []):
            lines.append(_embed_figure(report_dir, result.figures, fig_key, caption))

    if "09" in result.step_results:
        lines.append("## Step 9 — Inverse unobtanium solve\n\n")
        lines.append("### Mathematics and narrative (from validation_steps.md)\n\n")
        lines.append(narrative_for_step(9, equations=equations, operations=operations))
        lines.append("\n\n")
        s09 = result.step_results["09"]
        mode = s09.get("inverse_mode", "stress")
        lines.append(
            f"**Mode: {mode}** — literature-class ⟨σv⟩, pessimistic start. "
            "Reports **honest** unobtanium scale factors. "
            "**Forward confirmation** (`forward_confirmation_passes`): at these knobs, "
            "does the **design-calibrated** plant hit target MW?\n\n"
        )
        lines.append("### Results\n\n")
        lines.append(step_results_md("09", result.step_results["09"]))

    gap_ids = [k for k in result.step_results if k.endswith("_gap")]
    if gap_ids:
        lines.append("## Gap-closed re-validation (steps 05–08)\n\n")
        lines.append(
            "Analytics re-run with inverse-solved unobtanium knobs applied (`proof_mode` off). "
            "Compare to proof-forward sections above.\n\n"
        )
        for gid in sorted(gap_ids, key=_step_sort_key):
            lines.append(f"### {GAP_STEP_TITLES.get(gid, gid)}\n\n")
            lines.append(step_results_md(gid, result.step_results[gid]))
            for fig_key, caption in STEP_FIGURES_GAP.get(gid, []):
                lines.append(_embed_figure(report_dir, result.figures, fig_key, caption))

    lines.append("## Artifacts on disk\n\n")
    lines.append("| File | Description |\n|------|-------------|\n")
    lines.append("| `experiment.yaml` | Input experiment configuration |\n")
    lines.append("| `parameters.json` | Resolved parameters snapshot |\n")
    lines.append("| `chain_config.json` | Chain config at start of run |\n")
    lines.append("| `results/step_*.json` | Per-step result payloads |\n")
    lines.append("| `figures/assemblies/*.png` | CadQuery/Blender hero renders (when `./stand.sh` built) |\n")
    lines.append("| `figures/*.png` | Analysis plots (proof-forward + `_gap` when inverse ran) |\n")
    lines.append("| `UNOBTANIUM_GAP.md` | Technology gap narrative (Cursor agent or template) |\n")
    lines.append("| `gap_agent_prompt.txt` | Prompt sent to gap agent (when inverse enabled) |\n")
    lines.append("| `run.log` | Execution log |\n")
    lines.append("| `run_summary.json` | Success / error summary |\n\n")

    report_path = report_dir / "REPORT.md"
    report_path.write_text("".join(lines), encoding="utf-8")
    return report_path


def _step_sort_key(step_id: str) -> tuple[int, str]:
    if step_id.endswith("_gap"):
        base = step_id.replace("_gap", "")
        try:
            return (100 + int(base), step_id)
        except ValueError:
            return (200, step_id)
    if step_id == "09":
        return (90, step_id)
    if step_id == "physics":
        return (85, step_id)
    if step_id == "forward":
        return (86, step_id)
    try:
        return (int(step_id), step_id)
    except ValueError:
        return (999, step_id)


def _step_metrics_row(step_id: str, data: dict[str, Any]) -> str:
    if data.get("error"):
        return f"error: {data['error']}"
    if step_id == "02":
        return f"ρ_e_norm={data.get('rho_e_norm', '—')}"
    if step_id == "03":
        ci = data.get("clump_index_final")
        ratio = data.get("clump_reduction_ratio")
        ci_s = f"{float(ci):.2f}" if ci is not None else "—"
        ratio_s = f"{float(ratio):.2f}×" if ratio is not None else "—"
        return f"clump_ON={ci_s}, OFF/ON={ratio_s}, armed={data.get('reactor_armed')}"
    if step_id in ("05", "05_gap"):
        p = data.get("fusion_power_mw", "—")
        return f"P_fusion={p:.3g} MW (CORE-01 / INJ fueling)" if isinstance(p, (int, float)) else f"P_fusion={p}"
    if step_id in ("06", "06_gap"):
        s = data.get("steady_state") or {}
        pg = s.get("gross_power_mw", "—")
        return (
            f"P_gross={pg:.3g} MW, feasible={data.get('feasible')} (CORE-01 + AIR-01 + U2-CH4-01)"
            if isinstance(pg, (int, float))
            else f"P_gross={pg}, feasible={data.get('feasible')}"
        )
    if step_id in ("07", "07_gap"):
        return f"closure={data.get('closure_rel_error', 0):.2%} (TS-01 / AIR-01)"
    if step_id in ("08", "08_gap"):
        return f"design_validated={data.get('design_validated')}"
    if step_id == "09":
        u = data.get("unobtanium_required") or {}
        fs = u.get("fusion_reactivity_scale", "—")
        conf = data.get("forward_confirmation_passes")
        base = (
            f"success={data.get('success')}, η_react={fs:.3g}×, CNF={conf}"
            if isinstance(fs, (int, float))
            else f"success={data.get('success')}, CNF={conf}"
        )
        return base
    if step_id == "physics":
        return (
            f"physics_evidence={data.get('physics_evidence')}, "
            f"lit_fwd={data.get('literature_forward_mw', '—')} MW"
        )
    if step_id == "forward":
        for row in data.get("scenarios") or []:
            if row.get("id") == "five_year_sota":
                return f"5yr SOTA P_gross={row.get('gross_power_mw', '—')} MW"
        return "see table"
    if step_id == "01" and data.get("skipped"):
        return "SKIP_PIC"
    return "OK"
