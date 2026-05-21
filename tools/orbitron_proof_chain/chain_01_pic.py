#!/usr/bin/env python3
"""Step 1: run WarpX PICMI slice (optional SKIP_PIC=1)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_CHAIN_DIR = Path(__file__).resolve().parent
_REPO = _CHAIN_DIR.parents[1]
sys.path.insert(0, str(_REPO))

from ssto.orbitron.simulator.warpx_env import apply_warpx_env, ensure_warpx_env, warpx_python_executable  # noqa: E402

from tools.orbitron_proof_chain.chain_lib import (  # noqa: E402
    load_config,
    repo_root,
    save_step,
    utc_now,
)


def main() -> int:
    cfg = load_config()
    chain_root = Path(cfg["chain_root"])
    diags = chain_root / "01_pic" / "diags"
    ok_marker = chain_root / cfg["steps"]["01"]["ok_marker"]

    if os.environ.get("SKIP_PIC", "0") == "1":
        save_step("01", {"skipped": True, "reason": "SKIP_PIC=1"})
        print("SKIP_PIC=1 — marked step 01 ok without running WarpX")
        return 0

    if cfg["pic"].get("skip_if_ok") and ok_marker.is_file() and list(diags.glob("density_diag*")):
        print("PIC diags present; skipping rerun (delete 01_pic to force)")
        return 0

    pad = cfg["pad"]
    overrides = chain_root / "00_spec" / "picmi_overrides.json"
    if not overrides.is_file():
        raise FileNotFoundError(f"Missing {overrides}; run chain_00_spec.sh")

    script = repo_root() / "ssto" / "orbitron" / "laminar_flow_2d_arcjet.py"
    ensure_warpx_env()
    warpx_py = warpx_python_executable()
    diags.mkdir(parents=True, exist_ok=True)
    cmd = [
        warpx_py,
        str(script),
        "--overrides",
        str(overrides),
        "--throttle",
        str(pad["throttle"]),
        "--compressor",
        str(pad["compressor"]),
        "--cathode-pulse",
        str(pad["cathode_pulse"]),
        "--write-dir",
        str(diags),
        "--steps",
        str(cfg["pic"]["steps"]),
        "--diag-period",
        str(cfg["pic"]["diag_period"]),
    ]
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(script.parent), env=apply_warpx_env(), check=False)
    if proc.returncode != 0:
        save_step("01", {"ok": False, "returncode": proc.returncode})
        return proc.returncode

    save_step(
        "01",
        {
            "warpx_python": warpx_py,
            "diags_dir": str(diags),
            "throttle": pad["throttle"],
            "compressor": pad["compressor"],
            "cathode_pulse": pad["cathode_pulse"],
            "plotfiles": [p.name for p in sorted(diags.glob("density_diag*"))],
        },
    )
    print("OK:", diags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
