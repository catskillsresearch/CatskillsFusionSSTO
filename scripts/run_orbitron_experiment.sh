#!/usr/bin/env bash
# Launch headless experiment with Poetry + repo-local WarpX paths (same as Proof Suite).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

if ! command -v poetry >/dev/null 2>&1; then
  echo "error: poetry not found in PATH" >&2
  exit 1
fi
eval "$(poetry env activate)"
export REPO_ROOT="${ROOT}"
# shellcheck source=tools/warpx_paths.sh
source "${ROOT}/tools/warpx_paths.sh"
# Use the active Poetry interpreter for WarpX subprocesses (not bare ``python`` from chain_config.sh).
export WARPX_PYTHON="${WARPX_PYTHON:-$(command -v python)}"

exec python "${ROOT}/scripts/run_orbitron_experiment.py" "$@"
