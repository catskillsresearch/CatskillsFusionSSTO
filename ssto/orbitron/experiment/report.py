"""Assemble narrative Markdown experiment report (publication arc for physics readers)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ssto.orbitron.experiment.assembly_build import ensure_assembly_heroes
from ssto.orbitron.experiment.assembly_narrative import stage_assembly_figures
from ssto.orbitron.experiment.linkedin_html import write_report_linkedin_html
from ssto.orbitron.experiment.report_narrative import (
    render_baseline_overview,
    render_baseline_physics,
    render_benchmark_scenarios_section,
    render_brayton_air_cycle_section,
    render_combined_references_section,
    render_conclusion_gap,
    render_fidelity_section,
    render_gap_closed_performance,
    render_governing_equations_section,
    render_introduction,
    render_inverse_section,
    render_pb11_fusion_reaction_section,
    render_physics_design_section,
    render_test_stand_section,
    render_unobtanium_section,
)
from ssto.orbitron.experiment.runner import ExperimentRunResult


def write_experiment_report(
    result: ExperimentRunResult,
    *,
    run_date: datetime | None = None,
    refresh_assembly: bool = True,
) -> Path:
    """Write ``REPORT.md`` and ``REPORT.html`` (LinkedIn-safe)."""
    report_dir = result.report_dir
    when = run_date or datetime.now()
    date_str = when.strftime("%Y-%m-%d %H:%M")

    if refresh_assembly:
        ensure_assembly_heroes(log=report_dir / "run.log")
    staged = stage_assembly_figures(report_dir)

    lines: list[str] = []
    lines.append(f"# {result.experiment.experiment_name}\n\n")
    lines.append(f"*In-silico benchmark — {date_str}*\n\n")

    lines.append(render_introduction(result))
    brayton_section, brayton_refs = render_brayton_air_cycle_section()
    lines.append(brayton_section)
    lines.append(render_pb11_fusion_reaction_section())
    lines.append(render_test_stand_section(staged, report_dir=report_dir))
    lines.append(render_governing_equations_section())
    lines.append(render_physics_design_section(result.parameters))
    lines.append(render_unobtanium_section(result.parameters))
    lines.append(render_fidelity_section())
    lines.append(render_benchmark_scenarios_section(result))
    lines.append(render_baseline_overview(result))
    lines.append(render_baseline_physics(result, report_dir))
    lines.append(render_inverse_section(result, report_dir))
    lines.append(render_gap_closed_performance(result, report_dir))
    conclusion_body, gap_refs = render_conclusion_gap(result, report_dir)
    lines.append(conclusion_body)
    lines.append(render_combined_references_section(brayton_refs, gap_refs))

    report_path = report_dir / "REPORT.md"
    report_path.write_text("".join(lines), encoding="utf-8")

    write_report_linkedin_html(
        report_path,
        title=result.experiment.experiment_name,
        log=report_dir / "run.log",
    )
    return report_path
