#!/usr/bin/env bash
# One-shot surrogate map: WarpX sweep -> CSV -> engine_surrogate.json for FlightGear.
#
# Full FlightGear prep (mesh + surrogate + sounds): ./tools/prepare_orbitron_teststand.sh
#
# From repo root:
#   act
#   ./tools/build_surrogate_map.sh
#
# If Poetry is already active (`act`), you can use instead:
#   ./tools/build_surrogate_after_act.sh
#
# pywarpx is usually NOT in Poetry; set paths for your WarpX build:
#   PYTHONPATH .../WarpX/build/lib/site-packages
#   LD_LIBRARY_PATH .../WarpX/build/lib  (shared libs for pywarpx extension modules)
# Priority:
#   1) $WARPX_PYTHONPATH
#   2) $ROOT/WarpX/build/lib/site-packages (your layout)
#   3) $ROOT/WarpX/build/lib/pythonX.Y/site-packages
#   4) $ROOT/WarpX/build/lib
#
# Optional: export WARPX_PYTHON=/path/to/python  (must match WarpX build ABI)
#
# Quick test without WarpX:
#   ./tools/build_surrogate_map.sh --dry-run --grid 3

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
eval "$(poetry env activate)"

export REPO_ROOT="${ROOT}"
# shellcheck source=warpx_paths.sh
source "${ROOT}/tools/warpx_paths.sh"

exec python tools/build_surrogate_map.py "$@"
