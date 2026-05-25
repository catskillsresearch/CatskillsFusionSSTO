#!/usr/bin/env python3
"""
Headless Orbitron proof-chain experiment from a YAML configuration file.

Writes:
  reports/<experiment-slug>/<YYYY-MM-DD-HH-MM>/
    REPORT.md, experiment.yaml, parameters.json, chain_config.json,
    results/step_*.json, figures/*.png, run.log, run_summary.json

Example:
  ./scripts/run_orbitron_experiment.sh experiments/orbitron_phase1_baseline.yaml
  ./scripts/run_orbitron_experiment.sh experiments/orbitron_phase1_baseline.yaml --skip-pic

Direct Python (sets WarpX paths in-process; prefer the shell wrapper):
  python3 scripts/run_orbitron_experiment.py experiments/orbitron_phase1_baseline.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from ssto.orbitron.experiment.config import load_experiment_yaml  # noqa: E402
from ssto.orbitron.experiment.paths import make_report_dir  # noqa: E402
from ssto.orbitron.experiment.report import write_experiment_report  # noqa: E402
from ssto.orbitron.experiment.runner import run_experiment  # noqa: E402
from ssto.orbitron.simulator.warpx_env import bootstrap_warpx_runtime, warpx_env_summary  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Orbitron proof chain from experiment YAML")
    parser.add_argument(
        "experiment_yaml",
        type=Path,
        help="Path to experiment YAML (must include experiment_name)",
    )
    parser.add_argument(
        "--skip-pic",
        action="store_true",
        help="Override run.skip_pic — skip WarpX (fast sanity check)",
    )
    parser.add_argument(
        "--no-inverse",
        action="store_true",
        help="Skip step 09 inverse + gap-closed re-validation (on by default)",
    )
    parser.add_argument(
        "--no-gap-agent",
        action="store_true",
        help="Skip Cursor AI agent; template gap table still written after step 09",
    )
    parser.add_argument(
        "--inverse",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Use this directory instead of auto reports/<slug>/<timestamp>/",
    )
    args = parser.parse_args()

    yaml_path = args.experiment_yaml.resolve()
    if not yaml_path.is_file():
        print(f"Experiment file not found: {yaml_path}", file=sys.stderr)
        return 1

    exp = load_experiment_yaml(yaml_path)
    if args.skip_pic:
        exp.run["skip_pic"] = True
    if args.no_inverse:
        exp.run["run_inverse"] = False
    elif args.inverse:
        exp.run["run_inverse"] = True
    if args.no_gap_agent:
        exp.run["run_gap_agent"] = False

    ok, detail = bootstrap_warpx_runtime(repo_root_path=_REPO)
    if not exp.skip_pic and not ok:
        print(warpx_env_summary(), file=sys.stderr)
        print(
            "\nWarpX/pywarpx not available. Use:\n"
            "  ./scripts/run_orbitron_experiment.sh …\n"
            "or build WarpX under repo/WarpX/ and set WARPX_PYTHONPATH.\n"
            "For a fast chain without PIC: add --skip-pic\n",
            file=sys.stderr,
        )
        return 1

    report_dir = args.report_dir or make_report_dir(exp.experiment_name)
    report_dir = report_dir.resolve()
    print(f"Report directory: {report_dir}")

    result = run_experiment(exp, report_dir)
    report_path = write_experiment_report(result)
    linkedin_html = report_path.with_suffix(".html")
    print(f"Report: {report_path}")
    if linkedin_html.is_file():
        print(f"LinkedIn HTML: {linkedin_html}")

    if not result.success:
        print(f"Experiment failed: {result.error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
