#!/usr/bin/env bash
# Smoke test: can this Python import pywarpx (WarpX PICMI)?
#
# Uses your tree layout:
#   PYTHONPATH .../WarpX/build/lib/site-packages
#   LD_LIBRARY_PATH .../WarpX/build/lib
#
# Run from anywhere:
#   ./tools/test_pywarpx_import.sh
#
# Uses `python` on PATH (activate Poetry first if you rely on a given interpreter).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
_LIB="${ROOT}/WarpX/build/lib"
_SITE="${_LIB}/site-packages"

if [[ ! -d "${_SITE}" ]]; then
  echo "error: missing ${_SITE}" >&2
  echo "Build WarpX first or set WARPX_ROOT to your install prefix." >&2
  exit 1
fi

export PYTHONPATH="${_SITE}${PYTHONPATH:+:${PYTHONPATH}}"
export LD_LIBRARY_PATH="${_LIB}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

echo "PYTHONPATH=${PYTHONPATH%%:*} ..."
echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH%%:*} ..."
python - <<'PY'
import sys

try:
    from pywarpx import picmi
except ImportError as e:
    print("IMPORT FAILED:", e, file=sys.stderr)
    sys.exit(1)

print("OK: from pywarpx import picmi")
print("    python:", sys.executable)
try:
    import pywarpx

    print("    pywarpx:", getattr(pywarpx, "__file__", "?"))
except Exception as e:
    print("    (pywarpx file path):", e)
PY
