#!/usr/bin/env bash
# Build everything for Orbitron-TestStand in FlightGear.
# Preferred: ./stand.sh (Poetry + WarpX paths + make). See Makefile for targets.
# Legacy wrapper: tools/prepare_orbitron_teststand.sh (-h for options).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "${ROOT}/tools/prepare_orbitron_teststand.sh" "$@"
