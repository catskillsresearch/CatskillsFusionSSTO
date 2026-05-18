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
FG_HOME="${HOME}/.fgfs"
FGDATA="${FG_ROOT:-${FG_HOME}/fgdata_2024_1}"
SCENERY="${FG_SCENERY:-${FGDATA}/Scenery}"
if [[ ! -d "${SCENERY}/Terrain/w030n60/w022n63" ]]; then
  echo "error: BIKF scenery missing at ${SCENERY}/Terrain/w030n60/w022n63" >&2
  echo "  Install fgdata 2024.1 or set FG_ROOT / FG_SCENERY to your scenery tree." >&2
  exit 1
fi
pkill -f 'fgfs.*Orbitron-TestStand' 2>/dev/null || true
rm -f "${FG_HOME}/fgfs_lock.pid"

TERRASYNC_ARGS=(--disable-terrasync --terrasync-dir=/tmp/fg-terrasync-unused)
SCENERY_ARGS=(--fg-scenery="${SCENERY}")

echo "[fs.sh] Nasal $(md5sum "${AC}/${PKG}/Nasal/orbitron_ops.nas" | awk '{print $1}')"
if [[ "${FS_SOFTWARE_GL:-0}" == "1" ]]; then
  export LIBGL_ALWAYS_SOFTWARE=1
  echo "[fs.sh] LIBGL_ALWAYS_SOFTWARE=1 (AMD black-screen test)"
fi

# Spawn: lat/lon only at BIKF East-Apron-119 (63.98187, -22.5884). No parkpos (breaks 0-engine rigs).
# Do NOT use --ignore-autosave — it restores fgdata defaults including ai scenario nimitz_demo.
exec fgfs --fg-aircraft="${AC}" --aircraft="${PKG}" \
  --composite-viewer=0 \
  --lat=63.98187 --lon=-22.5884 --altitude=158 --heading=0 \
  --timeofday=noon \
  --fg-scenery="${SCENERY}" \
  --disable-terrasync --terrasync-dir=/tmp/fg-terrasync-unused \
  --splash-screen=0 \
  --ai-traffic=0 --ai-models=0 \
  --real-weather-fetch=0 --clouds3d=0 \
  --prop:/sim/presets/trim=false \
  --prop:/sim/presets/latitude-deg=63.98187 \
  --prop:/sim/presets/longitude-deg=-22.5884 \
  --prop:/sim/presets/heading-deg=0 \
  --prop:/sim/presets/onground=false \
  --prop:/sim/presets/altitude-ft=158 \
  --prop:/sim/ai/enabled=false \
  --prop:/sim/ai/scenarios-enabled=false \
  --prop:/sim/atc/enabled=false \
  --prop:/sim/mp-carriers/enabled=false \
  --prop:/sim/mp-carriers/auto-attach=false \
  --prop:/sim/mp-carriers/latch-always=false \
  --prop:/sim/multiplay/enabled=false \
  --prop:/sim/model/reactor/debug-ui-window=false \
  --prop:/sim/current-view/view-number=2
