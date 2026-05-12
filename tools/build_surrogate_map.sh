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

_PYVER="$(python -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
_WPX_SITE_VER="${ROOT}/WarpX/build/lib/python${_PYVER}/site-packages"
_WPX_SITE_FLAT="${ROOT}/WarpX/build/lib/site-packages"
_WPX_LIB="${ROOT}/WarpX/build/lib"

_warp_paths() {
  if [[ -n "${WARPX_PYTHONPATH:-}" ]]; then
    export PYTHONPATH="${WARPX_PYTHONPATH}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${_WPX_SITE_FLAT}" ]]; then
    export PYTHONPATH="${_WPX_SITE_FLAT}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${_WPX_SITE_VER}" ]]; then
    export PYTHONPATH="${_WPX_SITE_VER}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${_WPX_LIB}" ]]; then
    export PYTHONPATH="${_WPX_LIB}${PYTHONPATH:+:${PYTHONPATH}}"
  fi
  if [[ -d "${_WPX_LIB}" ]]; then
    export LD_LIBRARY_PATH="${_WPX_LIB}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
  fi
}
_warp_paths

exec python tools/build_surrogate_map.py "$@"
