#!/usr/bin/env bash
# Step 1: WarpX PIC at pad run point
set -euo pipefail
source "$(dirname "$0")/chain_config.sh"

echo "== chain_01_pic: laminar_flow_2d_arcjet =="
"${CHAIN_PYTHON}" "${ORBITRON_CHAIN_DIR}/chain_01_pic.py"
