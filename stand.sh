#!/usr/bin/env bash
# Poetry env + repo-local WarpX (pywarpx) paths, then GNU make.
#
# Full test-stand build (one command):  ./stand.sh
#   → make all (fg-ready): orbitron_lab.yaml → glTF/PNG → orbitron.ac, surrogate, sounds, …
#   CORE-01 assembly movie is built into each experiment report run (not a shared reports/ file).
#   No extra merge/patch steps — Reply 19 geometry lives in ssto/orbitron/assembly_specs/orbitron_lab.yaml.
#   Clean rebuild:  make clean && ./stand.sh
# Preview lab mesh in Blender: ./bl.sh
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
