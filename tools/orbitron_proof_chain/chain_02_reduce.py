#!/usr/bin/env python3
"""Step 2: reduce last WarpX plotfile → rho_e_norm (electron ring only)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import require_step  # noqa: E402


def main() -> int:
    require_step("01")
    from ssto.orbitron.simulator.proof_chain.runners import run_step_02  # noqa: E402

    out = run_step_02()
    print(f"rho_e_norm={out.get('rho_e_norm')} (fuel coupling → step 03)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
