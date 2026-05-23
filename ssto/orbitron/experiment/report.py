"""Assemble narrative Markdown experiment report."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ssto.orbitron.experiment.narrative import load_validation_narratives, narrative_for_step
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
    9: "Inverse solve (optional)",
}

# Figures to embed per step (logical key → caption)
STEP_FIGURES: dict[int, list[tuple[str, str]]] = {
    0: [("step00", "Engine layout (fusion channel focus)")],
    1: [("step01", "WarpX |ρ_e| — final snapshot")],
    2: [("step02", "Electron ring normalization")],
    3: [
        ("step03_density", "Fuel density n(s,r) — final frame, laminar OFF | ON"),
        ("step03_reaction", "Reaction rate R(s,r) — final frame, laminar OFF | ON"),
        ("step03_clump", "Clump index vs time"),
        ("step03_radial", "Radial mean density at final frame (ON)"),
    ],
    4: [("step04", "Proton and boron densities")],
    5: [("step05", "Fusion power vs target")],
    6: [
        ("step06_outputs", "Steady-state plant outputs"),
        ("step06_u", "U1–U4 stress ratios"),
    ],
    7: [("step07", "Jet power closure")],
}


def _fmt_yaml_block(obj: Any) -> str:
    return "```yaml\n" + yaml.safe_dump(obj, sort_keys=False, default_flow_style=False) + "```\n"


def _fmt_json_block(obj: Any) -> str:
    return "```json\n" + json.dumps(obj, indent=2, default=str) + "\n```\n"


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
    status = "SUCCESS" if result.success else f"FAILED — {result.error}"
    lines.append(f"**Status:** {status}  \n\n")

    if result.experiment.description:
        lines.append("## Experiment description\n\n")
        lines.append(result.experiment.description.strip() + "\n\n")

    lines.append("## Parameter settings\n\n")
    lines.append(
        "All values below were written to `chain_config.json` before the chain ran. "
        "Pad interlocks must be satisfied (APU → starter → bleed → vacuum → laser → HV → IGNITE) "
        "or step 03 fuel injection and reaction rate stay at zero.\n\n"
    )
    lines.append(_fmt_yaml_block(result.parameters))

    lines.append("## Proof-mode rules\n\n")
    lines.append(
        "- `ORBITRON_PROOF_CHAIN=1` — fusion reactivity scale fixed at 1.0 for steps 05–08.\n"
        "- Step 09 (inverse) only runs when `run.run_inverse: true` in the experiment YAML.\n"
        "- WarpX step 01 uses the electron-ring-only deck (τ ring density, p cathode pulse).\n\n"
    )

    lines.append("## Chain results summary\n\n")
    lines.append("| Step | Key metrics |\n|------|-------------|\n")
    for step_id in sorted(result.step_results.keys(), key=lambda s: int(s)):
        data = result.step_results[step_id]
        lines.append(f"| {step_id} | {_step_metrics_row(step_id, data)} |\n")
    lines.append("\n")

    for step_num in range(10):
        step_id = f"{step_num:02d}" if step_num < 10 else str(step_num)
        if step_num <= 8 and f"{step_num:02d}" not in result.step_results and str(step_num) not in result.step_results:
            if step_num == 9 and "09" not in result.step_results:
                continue
        sid = f"{step_num:02d}" if f"{step_num:02d}" in result.step_results else str(step_num)
        if sid not in result.step_results:
            continue

        lines.append(f"## Step {step_num} — {STEP_TITLES.get(step_num, sid)}\n\n")
        lines.append("### Mathematics and narrative (from validation_steps.md)\n\n")
        lines.append(narrative_for_step(step_num, equations=equations, operations=operations))
        lines.append("\n\n")

        lines.append("### Results (this run)\n\n")
        lines.append(_fmt_json_block(result.step_results[sid]))

        for fig_key, caption in STEP_FIGURES.get(step_num, []):
            lines.append(_embed_figure(report_dir, result.figures, fig_key, caption))

    lines.append("## Artifacts on disk\n\n")
    lines.append("| File | Description |\n|------|-------------|\n")
    lines.append("| `experiment.yaml` | Input experiment configuration |\n")
    lines.append("| `parameters.json` | Resolved parameters snapshot |\n")
    lines.append("| `chain_config.json` | Chain config used for the run |\n")
    lines.append("| `results/step_*.json` | Per-step result payloads |\n")
    lines.append("| `figures/*.png` | Plots (final frame for time series) |\n")
    lines.append("| `run.log` | Execution log |\n")
    lines.append("| `run_summary.json` | Success / error summary |\n\n")

    report_path = report_dir / "REPORT.md"
    report_path.write_text("".join(lines), encoding="utf-8")
    return report_path


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
    if step_id == "05":
        return f"P_fusion={data.get('fusion_power_mw', '—'):.3g} MW"
    if step_id == "06":
        s = data.get("steady_state") or {}
        return f"P_gross={s.get('gross_power_mw', '—'):.3g} MW, feasible={data.get('feasible')}"
    if step_id == "07":
        return f"closure={data.get('closure_rel_error', 0):.2%}"
    if step_id == "08":
        return f"design_validated={data.get('design_validated')}"
    if step_id == "01" and data.get("skipped"):
        return "SKIP_PIC"
    return "OK"
