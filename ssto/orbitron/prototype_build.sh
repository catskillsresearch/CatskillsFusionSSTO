#!/usr/bin/env bash
# Orbitron test stand: YAML lab glTF (via make) -> Blender .ac -> fix_screen_uv -> surrogate JSON.
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
Rerun-friendly Orbitron test stand build (YAML lab glTF -> Blender .ac -> UV -> surrogate).

Usage: prototype_build.sh [options]

Options:
  --skip-cad        Skip lab + arcjet glTF generation (make / CadQuery arcjet)
  --skip-arcjet     Skip arcjet_outdoor_stand.gltf only
  --skip-blender    Skip Blender -> orbitron.ac
  --skip-fix-uv     Skip fix_screen_uv.py
  --skip-surrogate  Skip engine_surrogate.json regen
  --with-sounds     Synthesize WAV beds (orbitron_sound_assets.yaml → sound_compiler.py)
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

STAND_AIR="${REPO_ROOT}/Aircraft/Orbitron-TestStand"
mkdir -p "${STAND_AIR}/build" "${STAND_AIR}/Models" "${STAND_AIR}/Sounds"
export ORBITRON_LAB_GLTF="${STAND_AIR}/build/orbitron_lab.gltf"
export ORBITRON_ARCJET_GLTF="${STAND_AIR}/build/arcjet_outdoor_stand.gltf"
export ORBITRON_GLTF_IN="${STAND_AIR}/build/orbitron_lab.gltf"
export ORBITRON_AC_OUT="${STAND_AIR}/Models/orbitron.ac"

GLTF_LAB="${ORBITRON_LAB_GLTF}"
AC_OUT="${ORBITRON_AC_OUT}"
SURROGATE_JSON="${STAND_AIR}/engine_surrogate.json"

if [[ "${SKIP_CAD}" -eq 0 ]]; then
  echo "== [1/5] Lab glTF (YAML → nested orbitron_lab.gltf via make orbitron-lab-gltf) → ${ORBITRON_LAB_GLTF} =="
  cd "${REPO_ROOT}"
  make orbitron-lab-gltf
  cd "${ORBITRON_DIR}"
else
  echo "== [1/5] Lab glTF: skipped =="
fi

if [[ "${SKIP_CAD}" -eq 0 && "${SKIP_ARCJET}" -eq 0 ]]; then
  echo "== [2/5] CadQuery: arcjet_outdoor_stand.gltf → ${ORBITRON_ARCJET_GLTF} =="
  python arcjet_test_stand_cad.py
elif [[ "${SKIP_ARCJET}" -ne 0 ]]; then
  echo "== [2/5] CadQuery arcjet: skipped =="
else
  echo "== [2/5] CadQuery arcjet: skipped (--skip-cad) =="
fi

if [[ ! -f "${GLTF_LAB}" ]]; then
  echo "error: missing ${GLTF_LAB} (run without --skip-cad or place glTF)" >&2
  exit 1
fi

if [[ "${SKIP_BLENDER}" -eq 0 ]]; then
  if ! command -v "${BLENDER_BIN}" >/dev/null 2>&1; then
    echo "error: Blender not found (${BLENDER_BIN}). Install Blender or set BLENDER=..." >&2
    exit 1
  fi
  echo "== [3/5] Blender -> ${AC_OUT} =="
  rm -f "${AC_OUT}"
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
  echo "== [5/5] Placeholder engine surrogate JSON → ${SURROGATE_JSON} =="
  cd "${REPO_ROOT}"
  python tools/warpx_to_jsbsim_surrogate.py --placeholder --out-json "${SURROGATE_JSON}"
else
  echo "== [5/5] Surrogate: skipped =="
fi

if [[ "${WITH_SOUNDS}" -ne 0 ]]; then
  echo "== [extra] sound_compiler → ${STAND_AIR}/Sounds =="
  cd "${REPO_ROOT}"
  poetry run python tools/sound_compiler.py \
    --spec "${REPO_ROOT}/ssto/orbitron/assembly_specs/orbitron_sound_assets.yaml" \
    --out-dir "${STAND_AIR}/Sounds"
fi

echo ""
echo "Prototype build OK."
echo "  Main mesh:  ${AC_OUT}"
echo "  Lab glTF:   ${GLTF_LAB}"
echo "  Arcjet-only glTF: ${ORBITRON_ARCJET_GLTF}"
echo "  Surrogate:  ${SURROGATE_JSON}"
echo "Fly: cd ${REPO_ROOT} && ./fs.sh"
