#!/usr/bin/env bash
# Build Orbitron test stand mesh + config (CadQuery -> glTF -> Blender .ac -> UV fix -> surrogate).
# To run FlightGear after: ./fs.sh from repo root (or ../../fs.sh from this directory)
set -euo pipefail
cd "$(dirname "$0")"
exec ./prototype_build.sh "$@"
