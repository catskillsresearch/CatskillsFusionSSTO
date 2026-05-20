#!/usr/bin/env bash
# Shared Blender launcher for Makefile, bl.sh, and build_ac3d.py pipeline.
# Override binary: BLENDER=/path/to/blender ./stand.sh
set -euo pipefail
exec "${BLENDER:-blender}" "$@"
