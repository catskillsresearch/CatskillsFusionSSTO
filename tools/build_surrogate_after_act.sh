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
