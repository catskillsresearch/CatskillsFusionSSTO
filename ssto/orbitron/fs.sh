#!/usr/bin/env bash
# Launch FlightGear for Orbitron-TestStand. Prefer aircraft built under repo ./Aircraft (make / stand.sh).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_AIRCRAFT="${HERE}/../../Aircraft"
if [[ -d "${REPO_AIRCRAFT}/Orbitron-TestStand" ]]; then
  FG_AIRCRAFT="${REPO_AIRCRAFT}"
else
  FG_AIRCRAFT="${HERE}"
fi
exec fgfs --fg-aircraft="${FG_AIRCRAFT}" --aircraft=Orbitron-TestStand --airport=BIKF --parkpos=East-Apron-119 \
  --timeofday=noon --ai-traffic=0 --real-weather-fetch=0 --clouds3d=0 \
  --prop:/sim/sound/chatter/volume=0.0 --prop:/sim/sound/atc/volume=0.0 \
  --prop:/instrumentation/comm/volume=0.0
