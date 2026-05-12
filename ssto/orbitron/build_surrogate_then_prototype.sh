#!/usr/bin/env bash
# Thin wrapper: same as repo ./tools/prepare_orbitron_teststand.sh (default = full WarpX + mesh + fgfs).
# Prefer: ./stand.sh (see Makefile).

set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec "${REPO}/tools/prepare_orbitron_teststand.sh" "$@"
