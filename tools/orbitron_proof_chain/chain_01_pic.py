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

from ssto.orbitron.simulator.warpx_env import (  # noqa: E402
    apply_warpx_env,
    ensure_warpx_env,
    warpx_python_executable,
)

from ssto.orbitron.simulator.proof_chain.runners import build_warpx_command  # noqa: E402

from tools.orbitron_proof_chain.chain_lib import (  # noqa: E402
    load_config,
    save_step,
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

    ensure_warpx_env()
    cmd, cwd, diags, n_cleared = build_warpx_command(cfg)
    if n_cleared:
        print(f"Cleared {n_cleared} old density_diag plotfile(s) under {diags}")
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(cwd), env=apply_warpx_env(), check=False)
    if proc.returncode != 0:
        save_step("01", {"ok": False, "returncode": proc.returncode})
        return proc.returncode

    pad = cfg["pad"]
    save_step(
        "01",
        {
            "warpx_python": warpx_python_executable(),
            "diags_dir": str(diags),
            "ring_density_scale": pad["throttle"],
            "cathode_pulse": pad["cathode_pulse"],
            "electron_ring_only": True,
            "plotfiles": [p.name for p in sorted(diags.glob("density_diag*"))],
        },
    )
    print("OK:", diags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
