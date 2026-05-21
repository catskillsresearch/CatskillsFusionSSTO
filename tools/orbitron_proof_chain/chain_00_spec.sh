#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/chain_config.sh"
echo "== chain_00_spec =="
"${CHAIN_PYTHON}" "${ORBITRON_CHAIN_DIR}/chain_00_spec.py"
