#!/usr/bin/env bash
# Run the full Orbitron proof chain (steps 00–08). Step 09 if RUN_INVERSE=1.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${DIR}/chain_config.sh"

chmod +x "${DIR}"/chain_*.sh 2>/dev/null || true

run_step() {
  local name="$1"
  shift
  echo ""
  echo "######## ${name} ########"
  "$@"
}

run_step "chain_00_spec" "${DIR}/chain_00_spec.sh"
run_step "chain_01_pic" "${DIR}/chain_01_pic.sh"
run_step "chain_02_reduce" "${CHAIN_PYTHON}" "${DIR}/chain_02_reduce.py"
run_step "chain_03_fusion_channel" "${CHAIN_PYTHON}" "${DIR}/chain_03_fusion_channel.py"
run_step "chain_04_fueling" "${CHAIN_PYTHON}" "${DIR}/chain_04_fueling.py"
run_step "chain_05_burn" "${CHAIN_PYTHON}" "${DIR}/chain_05_burn.py"
run_step "chain_06_plant" "${CHAIN_PYTHON}" "${DIR}/chain_06_plant.py"
run_step "chain_07_closure" "${CHAIN_PYTHON}" "${DIR}/chain_07_closure.py"
run_step "chain_08_export" "${CHAIN_PYTHON}" "${DIR}/chain_08_export.py"

if [[ "${RUN_INVERSE:-0}" == "1" ]]; then
  run_step "chain_09_solve" "${CHAIN_PYTHON}" "${DIR}/chain_09_solve.py"
fi

echo ""
echo "Proof chain complete. Artifacts: ${CHAIN_ROOT}"
echo "  Validation YAML: ${CHAIN_ROOT}/08_export/design_validation.yaml"
