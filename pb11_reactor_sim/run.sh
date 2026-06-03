#!/usr/bin/env bash
# Launch the p-11B reactor core simulator inside the Poetry environment, with
# the repo-local WarpX (pywarpx) paths configured exactly like ./stand.sh.
#
# Usage (from anywhere):
#   ./pb11_reactor_sim/run.sh
#
# Force the real WarpX electrostatic field-solve backend (otherwise the
# self-consistent scipy fallback drives the GUI):
#   PB11_USE_WARPX=1 ./pb11_reactor_sim/run.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT}"

if ! command -v poetry >/dev/null 2>&1; then
  echo "error: poetry not found in PATH" >&2
  exit 1
fi

export REPO_ROOT="${ROOT}"
# shellcheck source=../tools/warpx_paths.sh
source "${ROOT}/tools/warpx_paths.sh"

exec poetry run python -m pb11_reactor_sim "$@"
