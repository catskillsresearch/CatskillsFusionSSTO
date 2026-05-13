#!/usr/bin/env bash
# Open Blender with the nested Orbitron lab glTF (logical root fusion_arcjet_engine).
# Requires a prior build: ./stand.sh
#
# Usage (repo root):
#   ./bl.sh
#   BLENDER=/path/to/blender ./bl.sh
#
# Optional: open a different lab glTF (e.g. make yaml-lab-gltfs master):
#   ORBITRON_LAB_GLTF=Aircraft/Orbitron-TestStand/build/orbitron_lab_flat.gltf ./bl.sh
#
# Optional: after import, run viewport collections helper (VIEW__* collections):
#   ./bl.sh --collections

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
GLTF="${ROOT}/Aircraft/Orbitron-TestStand/build/orbitron_lab.gltf"
if [[ -n "${ORBITRON_LAB_GLTF:-}" ]]; then
  if [[ "${ORBITRON_LAB_GLTF}" == /* ]]; then
    GLTF="${ORBITRON_LAB_GLTF}"
  else
    GLTF="${ROOT}/${ORBITRON_LAB_GLTF}"
  fi
fi
BLENDER_BIN="${BLENDER:-blender}"
OPEN_PY="${ROOT}/tools/blender_open_orbitron_lab_gltf.py"
COL_PY="${ROOT}/tools/blender_orbitron_viewport_collections.py"

if [[ ! -f "${GLTF}" ]]; then
  echo "error: nested glTF not found: ${GLTF}" >&2
  echo "Build it first from repo root: ./stand.sh" >&2
  exit 1
fi
if [[ ! -f "${OPEN_PY}" ]]; then
  echo "error: missing ${OPEN_PY}" >&2
  exit 1
fi

_collections=0
_extra=()
for a in "$@"; do
  if [[ "${a}" == "--collections" ]]; then
    _collections=1
  else
    _extra+=("${a}")
  fi
done

if [[ "${_collections}" -eq 1 ]]; then
  if [[ ! -f "${COL_PY}" ]]; then
    echo "error: missing ${COL_PY}" >&2
    exit 1
  fi
  exec "${BLENDER_BIN}" --factory-startup \
    --python "${COL_PY}" -- "${GLTF}" "${_extra[@]}"
fi

exec "${BLENDER_BIN}" --factory-startup \
  --python "${OPEN_PY}" -- "${GLTF}" "${_extra[@]}"
