#!/usr/bin/env bash
# Repo-local WarpX (pywarpx) paths — sourced by stand.sh, proof chain, and launch wrappers.
#
# Usage (after REPO_ROOT is set, or let this script set it):
#   source "$(dirname "$0")/warpx_paths.sh"
#
# Optional overrides:
#   WARPX_PYTHONPATH  — prepend to PYTHONPATH
#   WARPX_PYTHON      — interpreter for PIC subprocesses (Proof Suite sets via Poetry when active)

_warpx_paths() {
  local root="${REPO_ROOT:-}"
  if [[ -z "${root}" ]]; then
    root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    REPO_ROOT="${root}"
    export REPO_ROOT
  fi

  local pyver
  pyver="$(python -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
  local site_flat="${root}/WarpX/build/lib/site-packages"
  local site_ver="${root}/WarpX/build/lib/python${pyver}/site-packages"
  local lib="${root}/WarpX/build/lib"

  if [[ -n "${WARPX_PYTHONPATH:-}" ]]; then
    export PYTHONPATH="${WARPX_PYTHONPATH}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${site_flat}" ]]; then
    export PYTHONPATH="${site_flat}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${site_ver}" ]]; then
    export PYTHONPATH="${site_ver}${PYTHONPATH:+:${PYTHONPATH}}"
  elif [[ -d "${lib}" ]]; then
    export PYTHONPATH="${lib}${PYTHONPATH:+:${PYTHONPATH}}"
  fi
  if [[ -d "${lib}" ]]; then
    export LD_LIBRARY_PATH="${lib}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
  fi
}

_warpx_paths
