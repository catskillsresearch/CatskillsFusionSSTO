#!/usr/bin/env bash
# Fixed paths for the Orbitron proof chain. Source from every chain_*.sh script.
set -euo pipefail

ORBITRON_CHAIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${ORBITRON_CHAIN_DIR}/../.." && pwd)"
export REPO_ROOT ORBITRON_CHAIN_DIR

CHAIN_ROOT="${REPO_ROOT}/build/orbitron/chain"
GENERATED_ROOT="${REPO_ROOT}/build/orbitron/generated"
export CHAIN_ROOT GENERATED_ROOT

# Pad run point (override before run_all.sh)
export CHAIN_THROTTLE="${CHAIN_THROTTLE:-0.85}"
export CHAIN_COMPRESSOR="${CHAIN_COMPRESSOR:-0.7}"
export CHAIN_CATHODE_PULSE="${CHAIN_CATHODE_PULSE:-0.75}"

# PIC
export WARPX_PYTHON="${WARPX_PYTHON:-python3}"
export CHAIN_PIC_STEPS="${CHAIN_PIC_STEPS:-500}"
export CHAIN_PIC_DIAG_PERIOD="${CHAIN_PIC_DIAG_PERIOD:-100}"
export SKIP_PIC="${SKIP_PIC:-0}"

# Proof chain env for plant / export
export ORBITRON_PROOF_CHAIN="${ORBITRON_PROOF_CHAIN:-1}"
export ORBITRON_CHAIN_ROOT="${CHAIN_ROOT}"

# Poetry python for simulator steps
export CHAIN_PYTHON="${CHAIN_PYTHON:-poetry run python}"
