#!/usr/bin/env python3
"""Step 2: reduce last WarpX plotfile -> rho_e_norm, rho_beam_norm."""
from __future__ import annotations

import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))
_TOOLS = _REPO / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from tools.orbitron_proof_chain.chain_lib import load_config, require_step, save_step  # noqa: E402


def main() -> int:
    require_step("01")
    cfg = load_config()
    chain_root = Path(cfg["chain_root"])
    diags = chain_root / "01_pic" / "diags"

    import json

    step01 = json.loads((chain_root / cfg["steps"]["01"]["artifact"]).read_text(encoding="utf-8"))
    if step01.get("skipped"):
        save_step(
            "02",
            {
                "skipped": True,
                "rho_e_norm": 1.0,
                "rho_beam_norm": 1.0,
                "note": "SKIP_PIC — using unity norms; rerun with PIC for Tier-2 coupling",
            },
        )
        print("SKIP_PIC: wrote unity pic norms")
        return 0

    from build_surrogate_map import (  # noqa: E402
        reduce_last_plotfile_beam_screen_kw_proxy,
        reduce_last_plotfile_mean_rho,
    )

    rho_e = reduce_last_plotfile_mean_rho(diags)
    rho_screen, rho_dom = reduce_last_plotfile_beam_screen_kw_proxy(diags)
    ref_e = 1.0e15
    ref_b = 1.0e10
    rho_e_norm = max(0.05, min(3.0, rho_e / ref_e)) if math.isfinite(rho_e) and rho_e > 0 else 1.0
    rho_beam_norm = (
        max(0.05, min(3.0, rho_screen / ref_b))
        if math.isfinite(rho_screen) and rho_screen > 0
        else (
            max(0.05, min(3.0, rho_dom / ref_b))
            if math.isfinite(rho_dom) and rho_dom > 0
            else 1.0
        )
    )

    save_step(
        "02",
        {
            "rho_e_mean": rho_e,
            "rho_beam_screen_mean": rho_screen,
            "rho_beam_domain_mean": rho_dom,
            "rho_e_norm": rho_e_norm,
            "rho_beam_norm": rho_beam_norm,
            "refs": {"rho_e_ref": ref_e, "rho_beam_ref": ref_b},
        },
    )
    print(f"rho_e_norm={rho_e_norm:.4f} rho_beam_norm={rho_beam_norm:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
