#!/usr/bin/env bash
# Orbitron test stand: CadQuery -> glTF -> Blender .ac -> fix_screen_uv -> surrogate JSON.
# Run: act && ./prototype_build.sh   (-h for options)
#
# Prefer from repo root: ./stand.sh SURROGATE=mesh   (writes Aircraft/Orbitron-TestStand; see Makefile).

set -euo pipefail

ORBITRON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${ORBITRON_DIR}/../.." && pwd)"
BLENDER_BIN="${BLENDER:-blender}"

SKIP_CAD=0
SKIP_ARCJET=0
SKIP_BLENDER=0
SKIP_FIX_UV=0
SKIP_SURROGATE=0
WITH_SOUNDS=0

usage() {
  cat <<'EOF'
Rerun-friendly Orbitron test stand build (CadQuery -> glTF -> Blender .ac -> UV -> surrogate).

Usage: prototype_build.sh [options]

Options:
  --skip-cad        Skip CadQuery exports
  --skip-arcjet     Skip arcjet_outdoor_stand.gltf only
  --skip-blender    Skip Blender -> orbitron.ac
  --skip-fix-uv     Skip fix_screen_uv.py
  --skip-surrogate  Skip engine_surrogate.json regen
  --with-sounds     Regenerate WAV beds in Orbitron-TestStand/Sounds (add_reactor_sound.py)
  -h, --help        Show this help

From repo root:  act && ssto/orbitron/prototype_build.sh
Env: BLENDER=/path/to/blender (default: blender)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-cad) SKIP_CAD=1 ;;
    --skip-arcjet) SKIP_ARCJET=1 ;;
    --skip-blender) SKIP_BLENDER=1 ;;
    --skip-fix-uv) SKIP_FIX_UV=1 ;;
    --skip-surrogate) SKIP_SURROGATE=1 ;;
    --with-sounds) WITH_SOUNDS=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
  shift
done

cd "${REPO_ROOT}"
if ! command -v poetry >/dev/null 2>&1; then
  echo "error: poetry not found in PATH" >&2
  exit 1
fi
eval "$(poetry env activate)"

cd "${ORBITRON_DIR}"

if [[ "${SKIP_CAD}" -eq 0 ]]; then
  echo "== [1/5] CadQuery: orbitron_lab_v5.gltf (fusion + arcjet engine + console) =="
  python full_reactor_cad.py
else
  echo "== [1/5] CadQuery: skipped =="
fi

if [[ "${SKIP_CAD}" -eq 0 && "${SKIP_ARCJET}" -eq 0 ]]; then
  echo "== [2/5] CadQuery: arcjet_outdoor_stand.gltf =="
  python arcjet_test_stand_cad.py
elif [[ "${SKIP_ARCJET}" -ne 0 ]]; then
  echo "== [2/5] CadQuery arcjet: skipped =="
else
  echo "== [2/5] CadQuery arcjet: skipped (--skip-cad) =="
fi

GLTF_LAB="${ORBITRON_DIR}/orbitron_lab_v5.gltf"
AC_OUT="${ORBITRON_DIR}/Orbitron-TestStand/Models/orbitron.ac"
SURROGATE_JSON="${ORBITRON_DIR}/Orbitron-TestStand/engine_surrogate.json"

if [[ ! -f "${GLTF_LAB}" ]]; then
  echo "error: missing ${GLTF_LAB} (run without --skip-cad or place glTF)" >&2
  exit 1
fi

if [[ "${SKIP_BLENDER}" -eq 0 ]]; then
  if ! command -v "${BLENDER_BIN}" >/dev/null 2>&1; then
    echo "error: Blender not found (${BLENDER_BIN}). Install Blender or set BLENDER=..." >&2
    exit 1
  fi
  echo "== [3/5] Blender -> Orbitron-TestStand/Models/orbitron.ac =="
  rm -f "${AC_OUT}"
  # -b: batch (no UI). build_ac3d.py loads orbitron_lab_v5.gltf from CWD.
  "${BLENDER_BIN}" -b --python "${ORBITRON_DIR}/build_ac3d.py"
  if [[ ! -f "${AC_OUT}" ]]; then
    echo "error: Blender did not produce ${AC_OUT}" >&2
    exit 1
  fi
else
  echo "== [3/5] Blender: skipped =="
  if [[ ! -f "${AC_OUT}" ]]; then
    echo "warning: ${AC_OUT} missing; fix_screen_uv may no-op or fail" >&2
  fi
fi

if [[ "${SKIP_FIX_UV}" -eq 0 ]]; then
  echo "== [4/5] Post-process AC (screen UV / texture) =="
  python fix_screen_uv.py
else
  echo "== [4/5] fix_screen_uv: skipped =="
fi

if [[ "${SKIP_SURROGATE}" -eq 0 ]]; then
  echo "== [5/5] Placeholder engine surrogate JSON =="
  cd "${REPO_ROOT}"
  python tools/warpx_to_jsbsim_surrogate.py --placeholder --out-json "${SURROGATE_JSON}"
else
  echo "== [5/5] Surrogate: skipped =="
fi

if [[ "${WITH_SOUNDS}" -ne 0 ]]; then
  echo "== [extra] Synthesize Orbitron WAV loops (Orbitron-TestStand/Sounds) =="
  python "${ORBITRON_DIR}/add_reactor_sound.py" --out-dir "${ORBITRON_DIR}/Orbitron-TestStand/Sounds"
fi

echo ""
echo "Prototype build OK."
echo "  Main mesh:  ${AC_OUT}"
echo "  Lab glTF:   ${GLTF_LAB}"
echo "  Arcjet-only glTF (optional ref): ${ORBITRON_DIR}/arcjet_outdoor_stand.gltf"
echo "  Surrogate:  ${SURROGATE_JSON}"
echo "Fly: cd ${ORBITRON_DIR} && ./fs.sh"
