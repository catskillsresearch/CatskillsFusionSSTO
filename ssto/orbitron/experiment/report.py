"""Assemble narrative Markdown experiment report (LinkedIn-ready arc: intro → stand → baseline → gap → conclusion)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ssto.orbitron.experiment.assembly_build import ensure_assembly_heroes
from ssto.orbitron.experiment.assembly_narrative import stage_assembly_figures
from ssto.orbitron.experiment.narrative import load_validation_narratives, narrative_for_step
from ssto.orbitron.experiment.report_formatting import parameters_tables_md, step_results_md
from ssto.orbitron.experiment.report_narrative import (
    render_appendix,
    render_baseline_overview,
    render_conclusion_gap,
    render_gap_closed_performance,
    render_introduction,
    render_inverse_section,
    render_operation_section,
    render_test_stand_section,
    render_unobtanium_section,
)
from ssto.orbitron.experiment.linkedin_html import write_report_linkedin_html
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

STEP_FIGURES: dict[int, list[tuple[str, str]]] = {
    0: [("step00", "Engine layout (fusion channel focus)")],
    1: [
        ("step01", "WarpX |ρ_e| — final snapshot (annotated)"),
        ("step01_evidence", "Frame audit: t=0 vs final vs Δρ"),
    ],
    2: [("step02", "Electron ring normalization")],
    3: [
        ("step03_density", "Fuel density n(s,r) — OFF | ON | log10(OFF/ON)"),
        ("step03_reaction", "Reaction rate R(s,r) — OFF | ON | log10(OFF/ON)"),
        ("step03_clump", "Clump index C_k vs time"),
        ("step03_radial", "⟨n⟩_s(r) at final frame"),
    ],
    4: [("step04", "Proton and boron densities")],
    5: [("step05", "P_fusion vs 3.5 MW target")],
    6: [
        ("step06_outputs", "Plant outputs (MW, mA, kN, kg/s)"),
        ("step06_u", "U1–U4 stress ratios"),
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


def _embed_figure(report_dir: Path, figures: dict[str, str | None], key: str, caption: str) -> str:
    name = figures.get(key)
    if not name:
        return f"*(Figure unavailable: {caption})*\n\n"
    rel = f"figures/{name}"
    return f"![{caption}]({rel})\n\n*{caption}*\n\n"


def _render_baseline_stages(
    result: ExperimentRunResult,
    report_dir: Path,
    *,
    equations: str,
    operations: str,
) -> str:
    lines = ["### Baseline stages (detail)\n\n"]
    for step_num in range(9):
        sid = f"{step_num:02d}"
        if sid not in result.step_results:
            continue
        title = STEP_TITLES.get(step_num, sid)
        lines.append(f"#### Stage {step_num} — {title}\n\n")
        lines.append(narrative_for_step(step_num, equations=equations, operations=operations))
        lines.append("\n\n")
        lines.append(step_results_md(sid, result.step_results[sid]))
        for fig_key, caption in STEP_FIGURES.get(step_num, []):
            lines.append(_embed_figure(report_dir, result.figures, fig_key, caption))
        lines.append("\n")
    return "".join(lines)


def write_experiment_report(
    result: ExperimentRunResult,
    *,
    run_date: datetime | None = None,
) -> Path:
    """Write ``REPORT.md`` — narrative arc for publication; appendix holds internal detail."""
    report_dir = result.report_dir
    when = run_date or datetime.now()
    date_str = when.strftime("%Y-%m-%d %H:%M")
    equations, operations = load_validation_narratives()

    ensure_assembly_heroes(log=report_dir / "run.log")
    staged = stage_assembly_figures(report_dir)

    lines: list[str] = []
    lines.append(f"# {result.experiment.experiment_name}\n\n")
    lines.append(f"*Simulation report — {date_str}*\n\n")

    # 1 — Introduction
    lines.append(render_introduction(result))

    # 2 — Test stand prototype
    lines.append(render_test_stand_section(staged))

    # 3 — Operation
    lines.append(render_operation_section(result.parameters))

    # 4 — Design parameters
    lines.append("## Design parameters\n\n")
    lines.append(parameters_tables_md(result.parameters))
    lines.append("\n")

    # 5 — Unobtanium assumptions
    lines.append(render_unobtanium_section(result.parameters))

    # 6 — Baseline proof-forward
    lines.append(render_baseline_overview(result))
    lines.append(_render_baseline_stages(result, report_dir, equations=equations, operations=operations))

    # 7 — Inverse solve
    lines.append(render_inverse_section(result, report_dir))

    # 8 — Gap-closed performance
    lines.append(render_gap_closed_performance(result, report_dir))

    # 9 — Conclusion (gap analysis / R&D program)
    lines.append(render_conclusion_gap(result, report_dir))

    # Appendix — methodology, physics audit, forward scenarios, artifacts
    lines.append(render_appendix(result, report_dir))

    report_path = report_dir / "REPORT.md"
    report_path.write_text("".join(lines), encoding="utf-8")

    write_report_linkedin_html(
        report_path,
        title=result.experiment.experiment_name,
        log=report_dir / "run.log",
    )
    return report_path
