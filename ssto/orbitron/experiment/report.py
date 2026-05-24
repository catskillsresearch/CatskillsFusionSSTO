"""Assemble narrative Markdown experiment report."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ssto.orbitron.experiment.assembly_narrative import (
    render_assembly_section_md,
    stage_assembly_figures,
    stand_build_dir,
)
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
        ("step03_density", "Fuel density n(s,r) — final frame, laminar OFF | ON (r zoom, r_anode dashed)"),
        ("step03_reaction", "Reaction rate R(s,r) — final frame, laminar OFF | ON (r zoom)"),
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

    staged = stage_assembly_figures(report_dir)
    lines.append(
        render_assembly_section_md(
            staged=staged,
            stand_build=stand_build_dir(),
            parameters=result.parameters,
        )
    )

    lines.append("## Parameter settings (full YAML)\n\n")
    lines.append(
        "Canonical snapshot written to `parameters.json`. Designator-annotated subset appears "
        "in **Physical assemblies** above.\n\n"
    )
    lines.append(_fmt_yaml_block(result.parameters))
    lines.append(
        "Pad interlocks (**CTRL-01**) must be satisfied "
        "(APU → starter → bleed → vacuum → laser → HV → IGNITE) or **INJ-***/**CORE-01** fuel "
        "injection and reaction rate stay at zero.\n\n"
    )

    lines.append("## Proof-mode rules\n\n")
    lines.append(
        "- **Proof-forward (steps 00–08):** `ORBITRON_PROOF_CHAIN=1` — fusion reactivity scale fixed at 1.0.\n"
        "- **Step 09 + gap-closed (default):** inverse unobtanium solve, then steps 05–08 re-run with "
        "solved knobs (`proof_mode` off). Opt out with `run.run_inverse: false` or `--no-inverse`.\n"
        "- **Gap agent (default):** writes `UNOBTANIUM_GAP.md` via Cursor SDK; API key from "
        "`CURSOR_API_KEY` or `~/Desktop/tokens_ssto.yaml` (`ORBITRON_TOKENS_YAML` to override). "
        "Use `--no-gap-agent` to skip.\n"
        "- WarpX step 01 uses the electron-ring-only deck (τ ring density, p cathode pulse).\n\n"
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
        lines.append(_fmt_json_block(result.step_results[sid]))

        for fig_key, caption in STEP_FIGURES.get(step_num, []):
            lines.append(_embed_figure(report_dir, result.figures, fig_key, caption))

    if "09" in result.step_results:
        lines.append("## Step 9 — Inverse unobtanium solve\n\n")
        lines.append("### Mathematics and narrative (from validation_steps.md)\n\n")
        lines.append(narrative_for_step(9, equations=equations, operations=operations))
        lines.append("\n\n")
        lines.append(
            "Minimum performance scales on U1–U4 knobs (and pad τ/c if needed) to hit the "
            "target MW while passing spec gates. **Not** first-principles proof — gap documentation.\n\n"
        )
        lines.append("### Results\n\n")
        lines.append(_fmt_json_block(result.step_results["09"]))

    gap_ids = [k for k in result.step_results if k.endswith("_gap")]
    if gap_ids:
        lines.append("## Gap-closed re-validation (steps 05–08)\n\n")
        lines.append(
            "Analytics re-run with inverse-solved unobtanium knobs applied (`proof_mode` off). "
            "Compare to proof-forward sections above.\n\n"
        )
        for gid in sorted(gap_ids, key=_step_sort_key):
            lines.append(f"### {GAP_STEP_TITLES.get(gid, gid)}\n\n")
            lines.append(_fmt_json_block(result.step_results[gid]))
            for fig_key, caption in STEP_FIGURES_GAP.get(gid, []):
                lines.append(_embed_figure(report_dir, result.figures, fig_key, caption))

    gap_md = report_dir / "UNOBTANIUM_GAP.md"
    if gap_md.is_file():
        lines.append("## Unobtanium technology gap (AI / template)\n\n")
        if result.gap_analysis_mode:
            lines.append(f"*Mode: {result.gap_analysis_mode}*\n\n")
        lines.append(gap_md.read_text(encoding="utf-8"))
        lines.append("\n")

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
        return f"success={data.get('success')}, η_react={fs:.3g}×" if isinstance(fs, (int, float)) else f"success={data.get('success')}"
    if step_id == "01" and data.get("skipped"):
        return "SKIP_PIC"
    return "OK"
