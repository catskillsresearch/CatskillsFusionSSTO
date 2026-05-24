"""Execute the full proof chain for a headless experiment."""
from __future__ import annotations

import shutil
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO

from ssto.orbitron.experiment.config import (
    ExperimentConfig,
    apply_experiment_to_chain,
    snapshot_parameters,
    write_json,
)
from ssto.orbitron.experiment.gap_analyst import run_gap_agent_analysis
from ssto.orbitron.experiment.gap_pipeline import (
    apply_solved_knobs_to_chain,
    rerun_analytics_with_gap_knobs,
    run_inverse_gap_solve,
)
from ssto.orbitron.experiment.plots import generate_all_figures, generate_gap_figures
from ssto.orbitron.simulator.proof_chain.runners import (
    run_step_00,
    run_step_01,
    run_step_02,
    run_step_03_compare_pair,
    run_step_04,
    run_step_05,
    run_step_06,
    run_step_07,
    run_step_08,
)
from tools.orbitron_proof_chain.chain_lib import (
    CHAIN_ROOT,
    CONFIG_PATH,
    _json_safe,
    enable_proof_env,
    load_config,
    utc_now,
)


def _step_payload_for_report(payload: Any) -> Any:
    """Drop GUI-only keys and make JSON-safe."""
    if isinstance(payload, dict):
        return _json_safe({k: v for k, v in payload.items() if not str(k).startswith("_")})
    return _json_safe(payload)


@dataclass
class ExperimentRunResult:
    report_dir: Path
    experiment: ExperimentConfig
    parameters: dict[str, Any]
    step_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    figures: dict[str, str | None] = field(default_factory=dict)
    gap_analysis_path: str | None = None
    gap_analysis_mode: str | None = None
    started_utc: str = ""
    finished_utc: str = ""
    success: bool = False
    error: str | None = None


def _log(log: TextIO | None, msg: str) -> None:
    if log:
        log.write(msg)
        if not msg.endswith("\n"):
            log.write("\n")
        log.flush()


def _copy_chain_artifacts(results_dir: Path) -> None:
    """Copy step JSON artifacts and key NPZ/YAML into report results/."""
    cfg = load_config()
    for step_id, step_def in cfg.get("steps", {}).items():
        rel = step_def.get("artifact")
        if not rel:
            continue
        src = CHAIN_ROOT / rel
        if src.is_file():
            dest = results_dir / f"step_{step_id}_{src.name}"
            shutil.copy2(src, dest)
    # NPZ caches and validation YAML
    extras = [
        "03_fusion_channel/fields_laminar_on.npz",
        "03_fusion_channel/fields_laminar_off.npz",
        "03_fusion_channel/fields.npz",
        "08_export/design_validation.yaml",
        "09_solve/solve.json",
    ]
    for rel in extras:
        src = CHAIN_ROOT / rel
        if src.is_file():
            shutil.copy2(src, results_dir / src.name.replace("/", "_"))


def run_experiment(
    exp: ExperimentConfig,
    report_dir: Path,
    *,
    log: TextIO | None = None,
) -> ExperimentRunResult:
    """
    Apply YAML → chain_config, run steps 00–08 (+09 optional), copy artifacts, plot PNGs.
    """
    started = utc_now()
    out = ExperimentRunResult(
        report_dir=report_dir,
        experiment=exp,
        parameters={},
        started_utc=started,
    )
    run_log = report_dir / "run.log"
    log_file = run_log.open("w", encoding="utf-8")
    combined_log = log_file

    def emit(msg: str) -> None:
        _log(combined_log, msg)
        _log(log, msg)

    try:
        emit(f"=== Experiment: {exp.experiment_name} ===\n")
        emit(f"Report directory: {report_dir}\n")
        if not exp.skip_pic:
            from ssto.orbitron.simulator.warpx_env import warpx_env_summary

            emit(warpx_env_summary() + "\n\n")

        if exp.source_path and exp.source_path.is_file():
            shutil.copy2(exp.source_path, report_dir / "experiment.yaml")
        else:
            write_json(report_dir / "experiment.yaml", exp.raw)

        cfg = apply_experiment_to_chain(exp)
        for note in cfg.get("experiment", {}).get("pic_stability_notes") or []:
            emit(f"PIC stability: {note}\n")
        out.parameters = snapshot_parameters(exp, cfg)
        write_json(report_dir / "parameters.json", out.parameters)
        shutil.copy2(CONFIG_PATH, report_dir / "chain_config.json")

        enable_proof_env()
        steps: list[tuple[str, callable]] = [
            ("00", run_step_00),
            ("01", lambda: run_step_01(skip_pic=exp.skip_pic, n_steps=exp.pic_steps_override)),
            ("02", run_step_02),
            ("03", run_step_03_compare_pair),
            ("04", run_step_04),
            ("05", run_step_05),
            ("06", run_step_06),
            ("07", run_step_07),
            ("08", run_step_08),
        ]

        for step_id, fn in steps:
            emit(f"\n--- Step {step_id} (proof-forward) ---\n")
            raw = fn()
            payload = _step_payload_for_report(raw)
            out.step_results[step_id] = payload
            write_json(report_dir / "results" / f"step_{step_id}.json", payload)
            emit(f"Step {step_id} OK\n")

        cfg = load_config()
        emit("\n--- Figures (proof-forward) ---\n")
        out.figures = generate_all_figures(report_dir / "figures", cfg)
        for name, png in out.figures.items():
            emit(f"  {name}: {png or '(skipped)'}\n")

        if exp.run_inverse:
            emit("\n--- Step 09 — inverse unobtanium solve ---\n")
            step09 = run_inverse_gap_solve(allow_forward_fail=True)
            out.step_results["09"] = _step_payload_for_report(step09)
            write_json(report_dir / "results" / "step_09.json", out.step_results["09"])
            emit(f"Step 09 OK (success={step09.get('success')})\n")

            emit("\n--- Gap-closed analytics (steps 05–08 with solved knobs) ---\n")
            apply_solved_knobs_to_chain(step09)
            gap_steps = rerun_analytics_with_gap_knobs()
            for step_id, payload in gap_steps.items():
                clean = _step_payload_for_report(payload)
                out.step_results[step_id] = clean
                write_json(report_dir / "results" / f"step_{step_id}.json", clean)
                emit(f"{step_id} OK\n")

            gap_figs = generate_gap_figures(report_dir / "figures")
            out.figures.update(gap_figs)
            for name, png in gap_figs.items():
                emit(f"  {name}: {png or '(skipped)'}\n")

            if exp.run_gap_agent:
                emit("\n--- Unobtanium gap agent ---\n")
                gap_path, gap_mode = run_gap_agent_analysis(
                    report_dir=report_dir,
                    experiment_name=exp.experiment_name,
                    parameters=out.parameters,
                    step09=step09,
                    step08_proof=out.step_results.get("08"),
                )
                out.gap_analysis_path = gap_path
                out.gap_analysis_mode = gap_mode
                emit(f"  UNOBTANIUM_GAP.md ({gap_mode}): {gap_path}\n")

        _copy_chain_artifacts(report_dir / "results")

        out.success = True
        out.finished_utc = utc_now()
        emit(f"\nFinished {out.finished_utc}\n")
        return out

    except Exception as exc:
        out.success = False
        out.error = str(exc)
        out.finished_utc = utc_now()
        emit(f"\nFAILED: {exc}\n")
        emit(traceback.format_exc())
        return out
    finally:
        log_file.close()
        write_json(
            report_dir / "run_summary.json",
            {
                "experiment_name": exp.experiment_name,
                "success": out.success,
                "error": out.error,
                "started_utc": out.started_utc,
                "finished_utc": out.finished_utc,
                "step_ids": list(out.step_results.keys()),
                "figures": out.figures,
                "gap_analysis_path": out.gap_analysis_path,
                "gap_analysis_mode": out.gap_analysis_mode,
                "run_inverse": exp.run_inverse,
                "run_gap_agent": exp.run_gap_agent,
            },
        )
