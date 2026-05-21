#!/usr/bin/env python3
"""Entry point: p-¹¹B Orbitron physics simulator GUI (from repo root: poetry run python scripts/run_orbitron_simulator.py)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from ssto.orbitron.simulator.gui.app import main

if __name__ == "__main__":
    raise SystemExit(main())
