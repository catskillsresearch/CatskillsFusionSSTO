#!/usr/bin/env bash
# One entry point: WarpX surrogate → CadQuery → Blender → sounds → FlightGear.
#
# Prefer incremental builds: ./stand.sh (or: eval "$(poetry env activate)" && make).
# See Makefile for SURROGATE=warpx|dry|mesh, graph, run-fgfs.
#
# Default (slow, full fidelity): full WarpX sweep (tools/build_surrogate_map.py), then
# prototype_build.sh --skip-surrogate --with-sounds, then exec ./fs.sh from repo root.
#
# Fast / partial:
#   --mesh-only       Skip WarpX; CadQuery → Blender → placeholder surrogate + sounds → fgfs
#   --surrogate-dry-run   WarpX-free surrogate grid (yt + CSV fit), then mesh → fgfs
#   --no-fgfs         Stop after build (no FlightGear launch)
#
# Does:
#   - eval "$(poetry env activate)"  (Poetry on PATH; same as `act`)
#   - Prepends PYTHONPATH / LD_LIBRARY_PATH for repo-local WarpX when present
#
# From repo root:
#   ./tools/prepare_orbitron_teststand.sh
#   ./tools/prepare_orbitron_teststand.sh --mesh-only
#   ./tools/prepare_orbitron_teststand.sh --surrogate-dry-run --grid 3
#   ./tools/prepare_orbitron_teststand.sh --no-fgfs --grid 4
#   ./tools/prepare_orbitron_teststand.sh -- --skip-blender
#
# With default WarpX mode, extra args before '--' go to build_surrogate_map.py; after '--'
# go to prototype_build.sh. Example:
#   ./tools/prepare_orbitron_teststand.sh --steps 600 -- --skip-cad
#
# Env: WARPX_PYTHONPATH, WARPX_PYTHON, BLENDER=...

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ORBITRON="${ROOT}/ssto/orbitron"
cd "${ROOT}"

usage() {
  cat <<'EOF'
prepare_orbitron_teststand.sh — WarpX → CAD → Blender → FlightGear

Default: FULL WarpX surrogate sweep (long), then mesh build + sounds, then launches fgfs.

Options:
  --mesh-only         Skip WarpX; placeholder surrogate inside prototype_build (fast).
  --surrogate-dry-run No pywarpx; dry grid + yt reduction + fit, then mesh + fgfs.
  --surrogate-warpx   Same as default (explicit full WarpX sweep).
  --no-fgfs           Do not launch FlightGear at the end.
  -h, --help          This message.

Argument split (dry / warpx / default WarpX):
  Before '--' : passed to build_surrogate_map.py
  After  '--' : passed to prototype_build.sh

  With --mesh-only, all non-option args go to prototype_build.sh (no '--' needed).

Examples:
  ./tools/prepare_orbitron_teststand.sh
  ./tools/prepare_orbitron_teststand.sh --mesh-only
  ./tools/prepare_orbitron_teststand.sh --no-fgfs --grid 5
  ./tools/prepare_orbitron_teststand.sh --steps 800 --diag-period 100 -- --skip-blender
EOF
}

# Default: full WarpX sweep (user expects a long run when WarpX is configured).
MODE=warpx
SUR_ARGS=()
P_ARGS=()
NO_FGFS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mesh-only)
      MODE=mesh
      shift
      ;;
    --surrogate-dry-run)
      MODE=dry
      shift
      ;;
    --surrogate-warpx)
      MODE=warpx
      shift
      ;;
    --no-fgfs)
      NO_FGFS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        P_ARGS+=("$1")
        shift
      done
      break
      ;;
    *)
      if [[ "${MODE}" == mesh ]]; then
        P_ARGS+=("$1")
      else
        SUR_ARGS+=("$1")
      fi
      shift
      ;;
  esac
done

if ! command -v poetry >/dev/null 2>&1; then
  echo "error: poetry not found in PATH (run from a shell where Poetry is installed)" >&2
  exit 1
fi
eval "$(poetry env activate)"

_PYVER="$(python -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
_WPX_SITE_VER="${ROOT}/WarpX/build/lib/python${_PYVER}/site-packages"
_WPX_SITE_FLAT="${ROOT}/WarpX/build/lib/site-packages"
_WPX_LIB="${ROOT}/WarpX/build/lib"

_warp_paths() {
  if [[ -n "${WARPX_PYTHONPATH:-}" ]]; then
    export PYTHONPATH="${WARPX_PYTHONPATH}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${_WPX_SITE_FLAT}" ]]; then
    export PYTHONPATH="${_WPX_SITE_FLAT}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${_WPX_SITE_VER}" ]]; then
    export PYTHONPATH="${_WPX_SITE_VER}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${_WPX_LIB}" ]]; then
    export PYTHONPATH="${_WPX_LIB}${PYTHONPATH:+:${PYTHONPATH}}"
  fi
  if [[ -d "${_WPX_LIB}" ]]; then
    export LD_LIBRARY_PATH="${_WPX_LIB}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
  fi
}
_warp_paths

case "${MODE}" in
  mesh)
    echo "=== [1/3] Orbitron: mesh + placeholder surrogate + sounds (WarpX skipped) ==="
    ;;
  dry)
    echo "=== [1/3] Orbitron: surrogate dry-run (no pywarpx) + fit → engine_surrogate.json ==="
    python "${ROOT}/tools/build_surrogate_map.py" --dry-run --grid 4 "${SUR_ARGS[@]}"
    P_ARGS=(--skip-surrogate --with-sounds "${P_ARGS[@]}")
    ;;
  warpx)
    echo "=== [1/3] Orbitron: WarpX surrogate sweep (slow) → engine_surrogate.json ==="
    python "${ROOT}/tools/build_surrogate_map.py" "${SUR_ARGS[@]}"
    P_ARGS=(--skip-surrogate --with-sounds "${P_ARGS[@]}")
    ;;
esac

if [[ "${MODE}" == mesh ]]; then
  HAS_WITH=0
  for a in "${P_ARGS[@]}"; do
    if [[ "$a" == "--with-sounds" ]]; then HAS_WITH=1; break; fi
  done
  if [[ "${HAS_WITH}" -eq 0 ]]; then
    P_ARGS=(--with-sounds "${P_ARGS[@]}")
  fi
fi

echo "=== [2/3] Orbitron: CadQuery → Blender → .ac → UV → surrogate (per flags) ==="
echo "=== prototype_build.sh $(printf '%q ' "${P_ARGS[@]}") ==="
"${ORBITRON}/prototype_build.sh" "${P_ARGS[@]}"

echo ""
echo "=== [3/3] Orbitron: FlightGear ==="
if [[ "${NO_FGFS}" -ne 0 ]]; then
  echo "Skipped (--no-fgfs). Launch manually:"
  echo "  cd ${ROOT} && ./fs.sh"
  exit 0
fi

cd "${ROOT}"
exec ./fs.sh
