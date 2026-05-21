#!/usr/bin/env python3
"""Step 6: 0D plant + U1–U4 (proof chain env)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import (
    base_inputs,
    enable_proof_env,
    require_step,
    save_step,
    steady_to_dict,
)


def main() -> int:
    require_step("05")
    enable_proof_env()
    inp, meta = base_inputs()

    from ssto.orbitron.simulator.plant_0d import evaluate_steady_state

    res = evaluate_steady_state(inp)
    save_step(
        "06",
        {
            "steady_state": steady_to_dict(res),
            "violations": list(res.violations),
            "feasible": res.feasible,
            "clump_index": meta["clump_index"],
            "clump_reduction_ratio": meta["clump_reduction_ratio"],
        },
    )
    print(f"P_gross={res.gross_power_mw:.6f} MW feasible={res.feasible} violations={len(res.violations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
