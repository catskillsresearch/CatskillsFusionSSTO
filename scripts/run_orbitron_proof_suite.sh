#!/usr/bin/env bash
# Launch Proof Suite with the same Poetry + WarpX env as ./stand.sh
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

exec python "${ROOT}/scripts/run_orbitron_proof_suite.py" "$@"
