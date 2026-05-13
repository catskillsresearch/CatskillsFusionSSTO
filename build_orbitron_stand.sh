#!/usr/bin/env bash
# Build everything for the Orbitron FG test stand in FlightGear.
# Preferred: ./stand.sh (Poetry + WarpX paths + make). See Makefile for targets.
# Legacy wrapper: tools/prepare_orbitron_teststand.sh (-h for options).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "${ROOT}/tools/prepare_orbitron_teststand.sh" "$@"
