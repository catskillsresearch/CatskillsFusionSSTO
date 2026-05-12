#!/usr/bin/env bash
# Thin wrapper: same as ./tools/prepare_orbitron_teststand.sh (default = full WarpX + mesh + fgfs).

set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
exec "${REPO}/tools/prepare_orbitron_teststand.sh" "$@"
