#!/usr/bin/env python3
"""
Regenerate REPORT.md and REPORT.html from an existing experiment run directory.

Use this while iterating on report layout — no proof chain, PIC, inverse, plots, or gap agent.

The Cursor agent conversation is **not** cached; this script reuses the existing
``UNOBTANIUM_GAP.md`` (and all ``results/step_*.json``) already in the run folder.

Full experiment runs always call ``write_experiment_report()`` with the latest narrative code;
each new timestamped folder still runs the gap agent unless ``run.reuse_gap_analysis: true``
or ``ORBITRON_REUSE_GAP_ANALYSIS=1`` with ``--report-dir`` pointing at a folder that already
has ``UNOBTANIUM_GAP.md``.

Example:
  poetry run python scripts/regenerate_orbitron_report.py \\
    reports/orbitron-direct-cycle-p-11b3-5mw-turbojet-in-silico-benchmark/2026-05-24-23-35
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from ssto.orbitron.experiment.report_reload import (  # noqa: E402
    load_run_from_report_dir,
    regenerate_experiment_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild REPORT.md + REPORT.html from a completed run folder",
    )
    parser.add_argument(
        "report_dir",
        type=Path,
        help="Existing run directory (contains run_summary.json, results/, figures/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load artifacts only; do not write REPORT files",
    )
    parser.add_argument(
        "--refresh-assembly",
        action="store_true",
        help="Run make for missing Blender hero PNGs (default: reuse staged figures only)",
    )
    args = parser.parse_args()

    report_dir = args.report_dir.resolve()
    if not (report_dir / "run_summary.json").is_file():
        print(f"error: not a report run directory: {report_dir}", file=sys.stderr)
        return 1

    if args.dry_run:
        result = load_run_from_report_dir(report_dir)
        print(f"experiment: {result.experiment.experiment_name}")
        print(f"steps: {', '.join(sorted(result.step_results))}")
        print(f"figures: {len(result.figures)}")
        return 0

    report_md = regenerate_experiment_report(
        report_dir,
        refresh_assembly=args.refresh_assembly,
    )
    report_html = report_md.with_suffix(".html")
    print(f"Wrote {report_md}")
    if report_html.is_file():
        print(f"Wrote {report_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
