#!/usr/bin/env bash
# Poetry env + repo-local WarpX (pywarpx) paths, then GNU make.
#
# Default build: unified assembly YAML → orbitron_lab.gltf + sub-assembly glTFs → Blender → orbitron.ac,
# surrogate, sounds from orbitron_sound_assets.yaml, Mermaid graphs. See Makefile GLTF_LAB / GLTF_LAB_SUBASSEMBLIES.
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
export REPO_ROOT="${ROOT}"
# shellcheck source=tools/warpx_paths.sh
source "${ROOT}/tools/warpx_paths.sh"

exec make "$@"
