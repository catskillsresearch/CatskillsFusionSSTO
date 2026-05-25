"""Rebuild REPORT.md / REPORT.html from a completed experiment run directory."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ssto.orbitron.experiment.config import load_experiment_yaml
from ssto.orbitron.experiment.report import write_experiment_report
from ssto.orbitron.experiment.runner import ExperimentRunResult

_STEP_JSON = re.compile(
    r"^step_(?P<id>\d{2}(?:_gap)?|physics|forward|09)\.json$"
)


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _report_timestamp(report_dir: Path, summary: dict[str, Any]) -> datetime | None:
    finished = summary.get("finished_utc")
    if isinstance(finished, str) and finished.strip():
        try:
            return datetime.fromisoformat(finished.replace("Z", "+00:00"))
        except ValueError:
            pass
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})", report_dir.name)
    if m:
        y, mo, d, h, mi = (int(x) for x in m.groups())
        return datetime(y, mo, d, h, mi)
    return None


def _load_step_results(report_dir: Path, summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results_dir = report_dir / "results"
    if not results_dir.is_dir():
        raise FileNotFoundError(f"missing results/: {report_dir}")

    step_results: dict[str, dict[str, Any]] = {}
    ids = summary.get("step_ids")
    if isinstance(ids, list) and ids:
        for sid in ids:
            key = str(sid)
            path = results_dir / f"step_{key}.json"
            if path.is_file():
                step_results[key] = _read_json(path)
        return step_results

    for path in sorted(results_dir.glob("step_*.json")):
        m = _STEP_JSON.match(path.name)
        if not m:
            continue
        step_results[m.group("id")] = _read_json(path)
    return step_results


def load_run_from_report_dir(report_dir: Path) -> ExperimentRunResult:
    """
    Reconstruct ``ExperimentRunResult`` from ``run_summary.json``, ``parameters.json``,
    ``experiment.yaml``, and ``results/step_*.json``.
    """
    report_dir = report_dir.resolve()
    summary_path = report_dir / "run_summary.json"
    params_path = report_dir / "parameters.json"
    exp_path = report_dir / "experiment.yaml"

    if not summary_path.is_file():
        raise FileNotFoundError(f"not a report run directory (no run_summary.json): {report_dir}")

    summary = _read_json(summary_path)
    if not params_path.is_file():
        raise FileNotFoundError(f"missing parameters.json: {report_dir}")
    parameters = _read_json(params_path)

    if exp_path.is_file():
        experiment = load_experiment_yaml(exp_path)
    else:
        from ssto.orbitron.experiment.config import ExperimentConfig

        name = str(summary.get("experiment_name") or "Orbitron experiment")
        experiment = ExperimentConfig(experiment_name=name, source_path=None)

    gap_path = summary.get("gap_analysis_path")
    if isinstance(gap_path, str):
        gap_rel = Path(gap_path)
        if not gap_rel.is_file() and (report_dir / "UNOBTANIUM_GAP.md").is_file():
            gap_path = str(report_dir / "UNOBTANIUM_GAP.md")
    elif (report_dir / "UNOBTANIUM_GAP.md").is_file():
        gap_path = str(report_dir / "UNOBTANIUM_GAP.md")

    figures = summary.get("figures") or {}
    if not isinstance(figures, dict):
        figures = {}

    return ExperimentRunResult(
        report_dir=report_dir,
        experiment=experiment,
        parameters=parameters,
        step_results=_load_step_results(report_dir, summary),
        figures={str(k): (str(v) if v is not None else None) for k, v in figures.items()},
        gap_analysis_path=str(gap_path) if gap_path else None,
        gap_analysis_mode=summary.get("gap_analysis_mode"),
        gap_agent_timing=summary.get("gap_agent_timing"),
        physics_evidence=summary.get("physics_evidence"),
        tier1_design_validated=summary.get("tier1_design_validated"),
        started_utc=str(summary.get("started_utc") or ""),
        finished_utc=str(summary.get("finished_utc") or ""),
        success=bool(summary.get("success")),
        error=summary.get("error"),
    )


def regenerate_experiment_report(
    report_dir: Path,
    *,
    run_date: datetime | None = None,
    refresh_assembly: bool = False,
) -> Path:
    """Rewrite ``REPORT.md`` and ``REPORT.html`` using saved run artifacts."""
    report_dir = report_dir.resolve()
    summary = _read_json(report_dir / "run_summary.json")
    when = run_date or _report_timestamp(report_dir, summary)
    result = load_run_from_report_dir(report_dir)
    return write_experiment_report(
        result,
        run_date=when,
        refresh_assembly=refresh_assembly,
    )
