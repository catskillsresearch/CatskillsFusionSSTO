#!/usr/bin/bash -x
# Open Blender with the nested Orbitron lab glTF (logical root fusion_arcjet_engine).
# Requires a prior build: ./stand.sh
#
# Usage (repo root):
#   ./bl.sh
#   ./bl.sh Aircraft/<pkg>/build/methane_tank_assy.gltf   # optional glTF path (repo-relative or absolute)
#   BLENDER=/path/to/blender ./bl.sh
#
# Optional: open a different lab glTF (e.g. a debug export path); overridden by a CLI path:
#   ORBITRON_LAB_GLTF=/path/to/orbitron_lab.gltf ./bl.sh
#
# Optional: after import, run viewport collections helper (VIEW__* collections):
#   ./bl.sh --collections
#   ./bl.sh --collections Aircraft/<pkg>/build/tank_assy.gltf

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PKG="$(python3 "${ROOT}/tools/orbitron_aircraft_paths.py" package_dir --repo-root "${ROOT}")"
DEFAULT_GLTF="${ROOT}/Aircraft/${PKG}/build/orbitron_lab.gltf"

_resolve_gltf() {
  # $1 = path (absolute or relative to repo root, same rules as ORBITRON_LAB_GLTF)
  local p="$1"
  if [[ "${p}" == /* ]]; then
    printf '%s' "${p}"
  else
    printf '%s' "${ROOT}/${p}"
  fi
}

_collections=0
gltf_cli=""
_extra=()
for a in "$@"; do
  if [[ "${a}" == "--collections" ]]; then
    _collections=1
  elif [[ -z "${gltf_cli}" ]]; then
    gltf_cli="${a}"
  else
    _extra+=("${a}")
  fi
done

GLTF="${DEFAULT_GLTF}"
if [[ -n "${gltf_cli}" ]]; then
  GLTF="$(_resolve_gltf "${gltf_cli}")"
elif [[ -n "${ORBITRON_LAB_GLTF:-}" ]]; then
  GLTF="$(_resolve_gltf "${ORBITRON_LAB_GLTF}")"
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
