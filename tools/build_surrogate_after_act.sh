#!/usr/bin/env bash
# WarpX surrogate sweep (build_surrogate_map.py) -> CSV -> engine_surrogate.json.
#
# Assumes `act` (Poetry venv) is already active so `python` resolves to the project venv.
# If pywarpx lives in a local WarpX build, this script prepends PYTHONPATH and
# LD_LIBRARY_PATH when they are not already set (same rules as build_surrogate_map.sh).
#
# From repo root:
#   act
#   ./tools/build_surrogate_after_act.sh
#   ./tools/build_surrogate_after_act.sh --dry-run --grid 3
#
# Override WarpX site-packages: export WARPX_PYTHONPATH=/path/to/site-packages
# Use a different interpreter for WarpX child runs: export WARPX_PYTHON=/path/to/python

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export REPO_ROOT="${ROOT}"
# shellcheck source=warpx_paths.sh
source "${ROOT}/tools/warpx_paths.sh"

exec python tools/build_surrogate_map.py "$@"
