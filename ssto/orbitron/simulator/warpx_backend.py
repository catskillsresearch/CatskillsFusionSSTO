"""
Optional WarpX PIC backend (subprocess → laminar_flow_2d_arcjet.py → yt reduction).

Requires pywarpx in WARPX_PYTHON (see tools/build_surrogate_map.py). GUI runs this in a worker thread.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

from ssto.orbitron.simulator.pad_startup import effective_operating_point
from ssto.orbitron.simulator.types import SimulatorInputs


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def warpx_python() -> str:
    return os.environ.get("WARPX_PYTHON", sys.executable)


def run_pic_slice(
    inputs: SimulatorInputs,
    work_dir: Path,
    n_steps: int = 200,
) -> dict[str, Any]:
    """
    Run one PICMI case; return reduction dict with rho_e_norm, beam_rho_norm (or error).
    """
    root = repo_root()
    script = root / "ssto" / "orbitron" / "laminar_flow_2d_arcjet.py"
    spec_path = root / "ssto" / "orbitron" / "assembly_specs" / "orbitron_physics_surrogate.yaml"
    tools = root / "tools"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    import orbitron_physics_spec as ops  # noqa: E402

    spec = ops.load_physics_spec(spec_path)
    overrides = ops.picmi_overrides_json(spec)
    g = inputs.geometry
    op, _status = effective_operating_point(inputs.operating, inputs.pad)
    overrides.update(
        {
            "r_anode_m": g.r_anode_m,
            "r_cathode_m": g.r_cathode_m,
            "V_cathode_v": g.V_cathode_v,
            "B_axial_tesla": g.B_axial_tesla,
            "domain_half_extent_m": max(g.r_anode_m, 0.05),
        }
    )
    work_dir.mkdir(parents=True, exist_ok=True)
    ov_path = work_dir / "picmi_overrides.json"
    ov_path.write_text(json.dumps(overrides), encoding="utf-8")
    cmd = [
        warpx_python(),
        str(script),
        "--write-dir",
        str(work_dir / "diags"),
        "--n-steps",
        str(n_steps),
        "--throttle",
        str(op.throttle),
        "--compressor",
        str(op.compressor),
        "--cathode-pulse",
        str(op.cathode_pulse),
        "--overrides",
        str(ov_path),
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(root / "ssto" / "orbitron"),
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if proc.returncode != 0:
        return {
            "ok": False,
            "error": proc.stderr[-4000:] if proc.stderr else proc.stdout[-4000:],
        }
    try:
        from build_surrogate_map import (  # noqa: E402
            reduce_beam_viewport_mean_rho,
            reduce_last_plotfile_mean_rho,
        )

        diags = work_dir / "diags"
        rho_e = reduce_last_plotfile_mean_rho(diags)
        rho_b = reduce_beam_viewport_mean_rho(diags, spec)
        return {
            "ok": True,
            "rho_e_mean": rho_e,
            "rho_beam_mean": rho_b,
            "rho_e_norm": 1.0,
            "rho_beam_norm": 1.0,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def inputs_with_pic_proxy(
    base: SimulatorInputs,
    work_dir: Path,
    n_steps: int = 200,
) -> tuple[SimulatorInputs, dict[str, Any]]:
    """Run PIC and attach normalized proxies to inputs."""
    raw = run_pic_slice(base, work_dir, n_steps=n_steps)
    if not raw.get("ok"):
        return base, raw
    # Normalization: caller may refine with sweep median; use simple scale for GUI
    rho_e = float(raw.get("rho_e_mean", 1.0))
    rho_b = float(raw.get("rho_beam_mean", 1.0))
    ref_e = 1.0e15
    ref_b = 1.0e10
    updated = replace(
        base,
        pic_rho_e_norm=max(0.05, rho_e / ref_e) if rho_e > 0 else float("nan"),
        pic_beam_rho_norm=max(0.05, rho_b / ref_b) if rho_b > 0 else float("nan"),
    )
    raw["rho_e_norm"] = updated.pic_rho_e_norm
    raw["rho_beam_norm"] = updated.pic_beam_rho_norm
    return updated, raw
