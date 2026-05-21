#!/usr/bin/env python3
"""Step 0: write chain_config.json and copy picmi overrides."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import (  # noqa: E402
    CHAIN_ROOT,
    CONFIG_PATH,
    GENERATED_ROOT,
    repo_root,
    save_step,
    write_chain_config_template,
)


def main() -> int:
    CHAIN_ROOT.mkdir(parents=True, exist_ok=True)
    (CHAIN_ROOT / "00_spec").mkdir(parents=True, exist_ok=True)
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)

    out_json = GENERATED_ROOT / "picmi_overrides.json"
    compile_script = repo_root() / "tools" / "compile_physics_surrogate_spec.py"
    import shlex

    py = shlex.split(os.environ.get("CHAIN_PYTHON", "poetry run python"))
    subprocess.run([*py, str(compile_script), "--out-json", str(out_json)], check=True, cwd=str(repo_root()))

    chain_ov = CHAIN_ROOT / "00_spec" / "picmi_overrides.json"
    chain_ov.write_bytes(out_json.read_bytes())

    cfg = write_chain_config_template()
    cfg["pad"]["throttle"] = float(os.environ.get("CHAIN_THROTTLE", "0.85"))
    cfg["pad"]["compressor"] = float(os.environ.get("CHAIN_COMPRESSOR", "0.7"))
    cfg["pad"]["cathode_pulse"] = float(os.environ.get("CHAIN_CATHODE_PULSE", "0.75"))
    cfg["pic"]["steps"] = int(os.environ.get("CHAIN_PIC_STEPS", "500"))
    cfg["pic"]["diag_period"] = int(os.environ.get("CHAIN_PIC_DIAG_PERIOD", "100"))
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    save_step(
        "00",
        {
            "message": "Compiled picmi_overrides.json from orbitron_physics_surrogate.yaml",
            "picmi_overrides": str(chain_ov),
            "spec_yaml": str(
                repo_root() / "ssto/orbitron/assembly_specs/orbitron_physics_surrogate.yaml"
            ),
        },
    )
    print("Wrote", CONFIG_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
