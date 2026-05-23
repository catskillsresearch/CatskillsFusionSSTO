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
from ssto.orbitron.experiment.plots import generate_all_figures
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
    run_step_09,
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
        if exp.run_inverse:
            steps.append(("09", run_step_09))

        for step_id, fn in steps:
            emit(f"\n--- Step {step_id} ---\n")
            raw = fn()
            payload = _step_payload_for_report(raw)
            out.step_results[step_id] = payload
            write_json(report_dir / "results" / f"step_{step_id}.json", payload)
            emit(f"Step {step_id} OK\n")

        _copy_chain_artifacts(report_dir / "results")
        cfg = load_config()
        emit("\n--- Figures ---\n")
        out.figures = generate_all_figures(report_dir / "figures", cfg)
        for name, png in out.figures.items():
            emit(f"  {name}: {png or '(skipped)'}\n")

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
            },
        )
