#!/usr/bin/env bash
# Poetry env + repo-local WarpX (pywarpx) paths, then GNU make.
#
# Default build: unified assembly YAML → orbitron_lab.gltf → Blender → orbitron.ac,
# surrogate, sounds from orbitron_sound_assets.yaml, Mermaid graphs. See Makefile GLTF_LAB.
# Preview nested lab in Blender: ./bl.sh   (or ./bl.sh --collections)
#
# Usage (repo root):
#   ./stand.sh
#   ./stand.sh SURROGATE=mesh
#   ./stand.sh graph
#   ./stand.sh run-fgfs
#
# Full from-scratch regression (default SURROGATE=warpx in Makefile): move Aircraft aside,
# then ./stand.sh — see Makefile help "Cold-tree regression".

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "${ROOT}"

if ! command -v poetry >/dev/null 2>&1; then
  echo "error: poetry not found in PATH" >&2
  exit 1
fi
eval "$(poetry env activate)"

_PYVER="$(python -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
_WPX_SITE_VER="${ROOT}/WarpX/build/lib/python${_PYVER}/site-packages"
_WPX_SITE_FLAT="${ROOT}/WarpX/build/lib/site-packages"
_WPX_LIB="${ROOT}/WarpX/build/lib"

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

exec make "$@"
