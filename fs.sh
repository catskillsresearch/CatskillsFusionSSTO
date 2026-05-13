#!/usr/bin/env bash
# Launch FlightGear for the Orbitron test stand using the Makefile output under ./Aircraft.
# Run from repo root (this script lives there).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
AC="${ROOT}/Aircraft"
PKG="$(python3 "${ROOT}/tools/orbitron_aircraft_paths.py" package_dir --repo-root "${ROOT}")"
if [[ ! -d "${AC}/${PKG}" ]]; then
  echo "error: ${AC}/${PKG} not found — build first, e.g. ./stand.sh SURROGATE=mesh" >&2
  exit 1
fi
exec fgfs --fg-aircraft="${AC}" --aircraft="${PKG}" --airport=BIKF --parkpos=East-Apron-119 \
  --timeofday=noon --ai-traffic=0 --real-weather-fetch=0 --clouds3d=0 \
  --prop:/sim/sound/chatter/volume=0.0 --prop:/sim/sound/atc/volume=0.0 \
  --prop:/instrumentation/comm/volume=0.0
