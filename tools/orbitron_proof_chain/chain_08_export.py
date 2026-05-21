#!/usr/bin/env python3
"""Step 8: full validation + YAML export."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import (
    CHAIN_ROOT,
    base_inputs,
    enable_proof_env,
    load_config,
    require_step,
    save_step,
    steady_to_dict,
    validation_checks_to_dict,
)


def main() -> int:
    require_step("07")
    enable_proof_env()
    inp, _ = base_inputs()
    cfg = load_config()

    from ssto.orbitron.simulator.export_validation import export_validation_yaml
    from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
    from ssto.orbitron.simulator.validation import validate_design

    res = evaluate_steady_state(inp)
    report = validate_design(inp, res)
    out_yaml = CHAIN_ROOT / "08_export" / "design_validation.yaml"
    export_validation_yaml(
        out_yaml,
        inp,
        res,
        report,
        title="p-¹¹B Orbitron proof-chain validation",
    )

    save_step(
        "08",
        {
            "design_validation_yaml": str(out_yaml),
            "design_validated": report.design_validated,
            "summary": report.summary,
            "steady_state": steady_to_dict(res),
            "spec_checks": validation_checks_to_dict(report),
        },
    )
    print(f"validated={report.design_validated} yaml={out_yaml}")
    # Pipeline succeeds even when specs fail — inspect design_validated in YAML/JSON.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
