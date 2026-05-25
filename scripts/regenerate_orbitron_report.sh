#!/usr/bin/env bash
# Regenerate REPORT.md + REPORT.html from a completed experiment run (fast iteration).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
exec poetry run python scripts/regenerate_orbitron_report.py "$@"
