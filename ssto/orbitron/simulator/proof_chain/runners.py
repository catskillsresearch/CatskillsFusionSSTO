"""Execute proof-chain steps (CLI scripts and Proof Suite GUI)."""
from __future__ import annotations

import json
import math
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from ssto.orbitron.simulator.warpx_env import (  # noqa: E402
    apply_warpx_env,
    ensure_warpx_env,
    warpx_python_executable,
)

from tools.orbitron_proof_chain.chain_lib import (  # noqa: E402
    CHAIN_ROOT,
    GENERATED_ROOT,
    base_inputs,
    enable_proof_env,
    load_config,
    load_step_json,
    repo_root,
    save_config,
    save_step,
    steady_to_dict,
    validation_checks_to_dict,
    write_chain_config_template,
)


def run_step_00(*, throttle: float | None = None, compressor: float | None = None, cathode_pulse: float | None = None) -> dict[str, Any]:
    CHAIN_ROOT.mkdir(parents=True, exist_ok=True)
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    compile_script = repo_root() / "tools" / "compile_physics_surrogate_spec.py"
    out_json = GENERATED_ROOT / "picmi_overrides.json"
    py = shlex.split(os.environ.get("CHAIN_PYTHON", "poetry run python"))
    subprocess.run([*py, str(compile_script), "--out-json", str(out_json)], check=True, cwd=str(repo_root()))
    chain_ov = CHAIN_ROOT / "00_spec" / "picmi_overrides.json"
    chain_ov.write_bytes(out_json.read_bytes())
    cfg = write_chain_config_template()
    if throttle is not None:
        cfg["pad"]["throttle"] = throttle
    if compressor is not None:
        cfg["pad"]["compressor"] = compressor
    if cathode_pulse is not None:
        cfg["pad"]["cathode_pulse"] = cathode_pulse
    save_config(cfg)
    save_step(
        "00",
        {
            "message": "Compiled picmi_overrides.json",
            "picmi_overrides": str(chain_ov),
            "spec_yaml": str(repo_root() / "ssto/orbitron/assembly_specs/orbitron_physics_surrogate.yaml"),
        },
    )
    return load_step_json("00")


def build_warpx_command(
    cfg: dict[str, Any] | None = None,
    *,
    n_steps: int | None = None,
) -> tuple[list[str], Path, Path]:
    """Return (argv, cwd, diags_dir) for laminar_flow_2d_arcjet."""
    cfg = cfg or load_config()
    chain_root = Path(cfg["chain_root"])
    diags = chain_root / "01_pic" / "diags"
    pad = cfg["pad"]
    overrides = chain_root / "00_spec" / "picmi_overrides.json"
    script = repo_root() / "ssto" / "orbitron" / "laminar_flow_2d_arcjet.py"
    steps = n_steps if n_steps is not None else int(cfg["pic"]["steps"])
    diags.mkdir(parents=True, exist_ok=True)
    cmd = [
        warpx_python_executable(),
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
        str(steps),
        "--diag-period",
        str(cfg["pic"]["diag_period"]),
    ]
    return cmd, script.parent, diags


def run_step_01(*, skip_pic: bool = False, n_steps: int | None = None) -> dict[str, Any]:
    cfg = load_config()
    pad = cfg["pad"]
    if skip_pic or os.environ.get("SKIP_PIC", "0") == "1":
        save_step("01", {"skipped": True, "reason": "SKIP_PIC"})
        return load_step_json("01")
    ensure_warpx_env()
    cmd, cwd, diags = build_warpx_command(cfg, n_steps=n_steps)
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=apply_warpx_env(),
    )
    if proc.returncode != 0:
        save_step("01", {"ok": False, "stderr": proc.stderr[-8000:]})
        raise RuntimeError(proc.stderr or proc.stdout or "WarpX failed")
    save_step(
        "01",
        {
            "diags_dir": str(diags),
            "plotfiles": [p.name for p in list_pic_plotfiles(diags)],
            "throttle": pad["throttle"],
            "compressor": pad["compressor"],
            "cathode_pulse": pad["cathode_pulse"],
            "n_steps": n_steps or int(cfg["pic"]["steps"]),
        },
    )
    return load_step_json("01")


def _save_fusion_npz(path: Path, fc: object) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        s_m=fc.s_m,
        r_m=fc.r_m,
        time_s=fc.time_s,
        density=fc.density,
        reaction_rate=fc.reaction_rate,
        clump_index=fc.clump_index,
    )


def run_step_02() -> dict[str, Any]:
    cfg = load_config()
    chain_root = Path(cfg["chain_root"])
    step01 = load_step_json("01")
    if step01.get("skipped"):
        save_step(
            "02",
            {"skipped": True, "rho_e_norm": 1.0, "rho_beam_norm": 1.0, "note": "SKIP_PIC"},
        )
        return load_step_json("02")
    _tools = repo_root() / "tools"
    if str(_tools) not in sys.path:
        sys.path.insert(0, str(_tools))
    from build_surrogate_map import (  # noqa: E402
        reduce_last_plotfile_beam_inject_plane,
        reduce_last_plotfile_beam_screen_kw_proxy,
        reduce_last_plotfile_rho_e_annulus,
    )
    from ssto.orbitron.laminar_flow_2d_arcjet import scaled_densities

    diags = chain_root / "01_pic" / "diags"
    g = cfg["geometry"]
    pad = cfg["pad"]
    rho_p95, rho_ring_mean, rho_dom_mean = reduce_last_plotfile_rho_e_annulus(
        diags,
        r_inner_m=float(g["r_cathode_m"]) * 0.9,
        r_outer_m=float(g["r_anode_m"]) * 0.95,
    )
    rho_screen, rho_beam_dom = reduce_last_plotfile_beam_screen_kw_proxy(diags)
    rho_inject = reduce_last_plotfile_beam_inject_plane(diags)
    throttle = float(pad["throttle"])
    if math.isfinite(rho_inject) and rho_inject > 0:
        rho_beam_metric = rho_inject
        beam_source = "inject_plane_2d"
    elif math.isfinite(rho_screen) and rho_screen > 0:
        rho_beam_metric = rho_screen
        beam_source = "viewport_screen"
    elif math.isfinite(rho_beam_dom) and rho_beam_dom > 0:
        rho_beam_metric = rho_beam_dom
        beam_source = "domain_mean"
    else:
        # 2D slice often has no deposited beam charge — use pad throttle as honest dial.
        rho_beam_metric = 0.0
        beam_source = "pad_throttle_fallback"

    overrides_path = chain_root / "00_spec" / "picmi_overrides.json"
    overrides: dict[str, Any] = {}
    if overrides_path.is_file():
        overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

    n_e, _ = scaled_densities(
        float(pad["throttle"]),
        float(pad["compressor"]),
        float(pad.get("cathode_pulse", 0.35 + 0.65 * pad["throttle"])),
        overrides,
    )
    e_charge = 1.602176634e-19
    ref_e_phys = max(n_e * e_charge, 1e-30)
    ref_e_design = 1.0e15
    ref_b_design = 1.0e10

    def _norm(rho_val: float, ref_phys: float, ref_design: float) -> tuple[float, str]:
        if not (math.isfinite(rho_val) and rho_val > 0):
            return 1.0, "default"
        ratio = rho_val / ref_phys if ref_phys > 0 else float("inf")
        if 1e-4 < ratio < 1e4:
            ref = ref_phys
            mode = "n_e*e"
        elif rho_val > 0:
            ref = rho_val
            mode = "self_p95"
        else:
            ref = ref_design
            mode = "design_1e15"
        return max(0.05, min(3.0, rho_val / ref)), mode

    rho_e_norm, norm_e_mode = _norm(rho_p95, ref_e_phys, ref_e_design)
    if beam_source == "pad_throttle_fallback":
        rho_beam_norm = max(0.2, min(3.0, 0.2 + 0.8 * throttle))
        norm_b_mode = "pad_throttle_fallback"
    else:
        rho_beam_norm, norm_b_mode = _norm(rho_beam_metric, ref_b_design * 1e-5, ref_b_design)

    payload = {
        "rho_e_mean": rho_dom_mean,
        "rho_e_ring_mean": rho_ring_mean,
        "rho_e_p95_annulus": rho_p95,
        "rho_beam_screen_mean": rho_screen,
        "rho_beam_inject_plane_mean": rho_inject,
        "rho_beam_domain_mean": rho_beam_dom,
        "rho_e_norm": rho_e_norm,
        "rho_beam_norm": rho_beam_norm,
        "beam_metric_source": beam_source,
        "norm_ref_e": ref_e_phys if norm_e_mode == "n_e*e" else rho_p95,
        "norm_mode_e": norm_e_mode,
        "norm_mode_beam": norm_b_mode,
        "pad_throttle": pad["throttle"],
        "pad_compressor": pad["compressor"],
        "pad_cathode_pulse": pad.get("cathode_pulse"),
    }
    save_step("02", payload)
    return load_step_json("02")


def run_step_03(*, laminar_on: bool | None = None, compare_hack: bool = True) -> dict[str, Any]:
    enable_proof_env()
    inp, _ = base_inputs()
    if laminar_on is not None:
        from dataclasses import replace

        inp = replace(inp, pad=replace(inp.pad, laminar_relaminarization=laminar_on))
    from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus, focus_domain
    from ssto.orbitron.simulator.longitudinal.fusion_channel_sr import (
        laminar_hack_from_inputs,
        run_fusion_channel_sr,
    )

    dom = focus_domain(LongitudinalFocus.FUSION_CHANNEL_SR, inp)
    laminar = laminar_hack_from_inputs(inp, force_off=not inp.pad.laminar_relaminarization)
    fc = run_fusion_channel_sr(dom, inp, laminar=laminar, compare_without_hack=compare_hack)
    cache_dir = CHAIN_ROOT / "03_fusion_channel"
    cache_on = cache_dir / "fields_laminar_on.npz"
    cache_off = cache_dir / "fields_laminar_off.npz"
    cache_primary = cache_dir / "fields.npz"

    _save_fusion_npz(cache_on if laminar.enabled else cache_off, fc)
    _save_fusion_npz(cache_primary, fc)

    clump_off_val = fc.clump_index_final
    if compare_hack:
        from dataclasses import replace

        inp_off = replace(inp, pad=replace(inp.pad, laminar_relaminarization=False))
        fc_off = run_fusion_channel_sr(
            dom,
            inp_off,
            laminar=laminar_hack_from_inputs(inp_off, force_off=True),
            compare_without_hack=False,
        )
        _save_fusion_npz(cache_off, fc_off)
        clump_off_val = fc_off.clump_index_final

    payload = {
        "integrated_fusion_power_mw": fc.integrated_fusion_power_mw,
        "fusion_pb11_power_mw": fc.meta.get("fusion_pb11_power_mw"),
        "clump_index_final": fc.clump_index_final,
        "clump_index_off": clump_off_val,
        "clump_reduction_ratio": fc.clump_reduction_ratio,
        "laminar_enabled": laminar.enabled,
        "channel_power_ratio": fc.meta.get("channel_power_ratio"),
        "fields_npz": str(cache_primary),
        "fields_laminar_on_npz": str(cache_on),
        "fields_laminar_off_npz": str(cache_off),
        "has_compare_pair": cache_on.is_file() and cache_off.is_file(),
    }
    save_step("03", payload)
    return {**payload, "_fusion_channel": fc}


def run_step_03_compare_pair() -> dict[str, Any]:
    """Run laminar ON and OFF once; cache both NPZ for side-by-side UI (no re-run on scrub)."""
    enable_proof_env()
    from dataclasses import replace

    inp, _ = base_inputs()
    from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus, focus_domain
    from ssto.orbitron.simulator.longitudinal.fusion_channel_sr import (
        laminar_hack_from_inputs,
        run_fusion_channel_sr,
    )

    dom = focus_domain(LongitudinalFocus.FUSION_CHANNEL_SR, inp)
    cache_dir = CHAIN_ROOT / "03_fusion_channel"
    cache_on = cache_dir / "fields_laminar_on.npz"
    cache_off = cache_dir / "fields_laminar_off.npz"

    inp_on = replace(inp, pad=replace(inp.pad, laminar_relaminarization=True))
    fc_on = run_fusion_channel_sr(
        dom, inp_on, laminar=laminar_hack_from_inputs(inp_on), compare_without_hack=False
    )
    inp_off = replace(inp, pad=replace(inp.pad, laminar_relaminarization=False))
    fc_off = run_fusion_channel_sr(
        dom, inp_off, laminar=laminar_hack_from_inputs(inp_off, force_off=True), compare_without_hack=False
    )
    _save_fusion_npz(cache_on, fc_on)
    _save_fusion_npz(cache_off, fc_off)
    _save_fusion_npz(cache_dir / "fields.npz", fc_on)

    reduction = float(fc_off.clump_index_final) / max(float(fc_on.clump_index_final), 1.0e-6)
    payload = {
        "integrated_fusion_power_mw": fc_on.integrated_fusion_power_mw,
        "clump_index_final": fc_on.clump_index_final,
        "clump_index_off": fc_off.clump_index_final,
        "clump_reduction_ratio": reduction,
        "fields_npz": str(cache_dir / "fields.npz"),
        "fields_laminar_on_npz": str(cache_on),
        "fields_laminar_off_npz": str(cache_off),
        "has_compare_pair": True,
        "compare_pair_cached": True,
    }
    save_step("03", payload)
    return {**payload, "_fusion_channel": fc_on, "_fusion_channel_off": fc_off}


def run_step_04() -> dict[str, Any]:
    enable_proof_env()
    inp, _ = base_inputs()
    from ssto.orbitron.simulator.fusion_pb11 import evaluate_fusion_pb11
    from ssto.orbitron.simulator.pad_startup import effective_operating_point

    g, op = inp.geometry, effective_operating_point(inp.operating, inp.pad)[0]
    fus = evaluate_fusion_pb11(
        r_anode_m=g.r_anode_m,
        length_m=g.length_m,
        V_cathode_v=g.V_cathode_v,
        throttle=op.throttle,
        cathode_pulse=op.cathode_pulse,
        h2_sccm=op.h2_sccm,
        b2h6_sccm=op.b2h6_sccm,
        fusion_reactivity_scale=inp.unobtanium.fusion_reactivity_scale,
        pic_rho_e_norm=inp.pic_rho_e_norm,
    )
    save_step(
        "04",
        {
            "n_proton_m3": fus.n_proton_m3,
            "n_boron_m3": fus.n_boron_m3,
            "ion_temperature_kev": fus.ion_temperature_kev,
            "sigma_v_m3_s": fus.sigma_v_m3_s,
            "plasma_volume_m3": fus.plasma_volume_m3,
            "confinement_factor": fus.confinement_factor,
            "fueling_mix_scale": fus.fueling_mix_scale,
        },
    )
    return load_step_json("04")


def run_step_05() -> dict[str, Any]:
    p4 = run_step_04()
    inp, _ = base_inputs()
    from ssto.orbitron.simulator.fusion_pb11 import evaluate_fusion_pb11
    from ssto.orbitron.simulator.pad_startup import effective_operating_point

    g, op = inp.geometry, effective_operating_point(inp.operating, inp.pad)[0]
    fus = evaluate_fusion_pb11(
        r_anode_m=g.r_anode_m,
        length_m=g.length_m,
        V_cathode_v=g.V_cathode_v,
        throttle=op.throttle,
        cathode_pulse=op.cathode_pulse,
        h2_sccm=op.h2_sccm,
        b2h6_sccm=op.b2h6_sccm,
        fusion_reactivity_scale=inp.unobtanium.fusion_reactivity_scale,
        pic_rho_e_norm=inp.pic_rho_e_norm,
    )
    target = inp.scales.target_gross_power_mw
    save_step(
        "05",
        {
            "fusion_power_mw": fus.fusion_power_mw,
            "target_gross_power_mw": target,
            "shortfall_mw": target - fus.fusion_power_mw,
            "reaction_rate_m3_s": fus.reaction_rate_m3_s,
        },
    )
    return load_step_json("05")


def run_step_06() -> dict[str, Any]:
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
    return load_step_json("06")


def run_step_07() -> dict[str, Any]:
    run_step_06()
    p6 = load_step_json("06")
    s = p6["steady_state"]
    LBF_TO_N = 4.4482216152605
    gross_mw = float(s["gross_power_mw"])
    thrust_lbf = float(s["thrust_lbf"])
    mdot = float(s["mass_flow_kgps"])
    jet_mw = float(s["jet_kinetic_power_mw"])
    thrust_n = thrust_lbf * LBF_TO_N
    p_from_thrust_w = (thrust_n**2) / (2.0 * mdot) if mdot > 1e-9 else 0.0
    p_jet_w = jet_mw * 1.0e6
    rel_err = abs(p_from_thrust_w - p_jet_w) / max(p_jet_w, 1.0)
    f2_rel = abs(thrust_n**2 - 2.0 * p_jet_w * mdot) / max(2.0 * p_jet_w * mdot, 1.0)
    save_step(
        "07",
        {
            "closure_rel_error": rel_err,
            "f2_rel_error": f2_rel,
            "passes_12pct": rel_err <= 0.12,
            "gross_power_mw": gross_mw,
            "jet_kinetic_power_mw": jet_mw,
            "thrust_lbf": thrust_lbf,
            "mass_flow_kgps": mdot,
        },
    )
    return load_step_json("07")


def run_step_08() -> dict[str, Any]:
    enable_proof_env()
    inp, _ = base_inputs()
    from ssto.orbitron.simulator.export_validation import export_validation_yaml
    from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
    from ssto.orbitron.simulator.validation import validate_design

    res = evaluate_steady_state(inp)
    report = validate_design(inp, res)
    out_yaml = CHAIN_ROOT / "08_export" / "design_validation.yaml"
    export_validation_yaml(out_yaml, inp, res, report, title="p-¹¹B Orbitron proof-chain validation")
    save_step(
        "08",
        {
            "design_validation_yaml": str(out_yaml),
            "design_validated": report.design_validated,
            "summary": report.summary,
            "spec_checks": validation_checks_to_dict(report),
        },
    )
    return load_step_json("08")


def run_step_09() -> dict[str, Any]:
    from tools.orbitron_proof_chain.chain_lib import step08_blocks_inverse

    require_step("08")
    s8 = load_step_json("08")
    allowed, msg = step08_blocks_inverse(s8)
    if not allowed:
        raise RuntimeError(msg)

    inp, _ = base_inputs()
    os.environ.pop("ORBITRON_PROOF_CHAIN", None)
    from ssto.orbitron.simulator.solve import solve_unobtanium_requirements

    report = solve_unobtanium_requirements(inp, target_mw=inp.scales.target_gross_power_mw)
    u = report.inputs.unobtanium
    save_step(
        "09",
        {
            "success": bool(report.success),
            "message": report.message,
            "residual_mw": report.residual_mw,
            "unobtanium_required": {
                "fusion_reactivity_scale": u.fusion_reactivity_scale,
                "field_emission_margin": u.field_emission_margin,
                "ch4_cooling_effectiveness": u.ch4_cooling_effectiveness,
                "hts_capability_scale": u.hts_capability_scale,
                "beam_coupling_scale": u.beam_coupling_scale,
            },
            "steady_state": steady_to_dict(report.result),
        },
    )
    enable_proof_env()
    return load_step_json("09")


def list_pic_plotfiles(diags: Path) -> list[Path]:
    """WarpX density_diag plotfiles (prefer final frames over *.old.* backups)."""
    files = sorted(diags.glob("density_diag*"))
    canon = [p for p in files if ".old." not in p.name]
    return canon if canon else files


def load_pic_slice_2d(chain_root: Path | None = None) -> tuple[Any, Any, Any] | None:
    """Last WarpX |rho_e| slice for GUI (x, z, field). None if missing data or load error."""
    data, _err = load_pic_slice_2d_with_error(chain_root)
    return data


def load_pic_slice_2d_with_error(
    chain_root: Path | None = None,
) -> tuple[tuple[Any, Any, Any] | None, str | None]:
    """Return (x, z, rho) or (None, user-facing reason)."""
    cfg = load_config()
    root = chain_root or Path(cfg["chain_root"])
    diags = root / "01_pic" / "diags"
    if not diags.is_dir():
        return None, f"No diags folder: {diags}"
    plotfiles = list_pic_plotfiles(diags)
    if not plotfiles:
        return None, f"No density_diag plotfiles in {diags} (WarpX may have failed or not finished)"
    try:
        import numpy as np
        import yt
    except ImportError as exc:
        return None, f"yt not importable in {sys.executable}: {exc}"
    try:
        yt.funcs.mylog.setLevel(50)
        ds = yt.load(str(plotfiles[-1]))
        grid = ds.covering_grid(level=0, left_edge=ds.domain_left_edge, dims=ds.domain_dimensions)
        rho = np.abs(grid[("boxlib", "rho_electrons")].v.squeeze())
        le = np.asarray(ds.domain_left_edge.to_value(), dtype=float).ravel()
        re = np.asarray(ds.domain_right_edge.to_value(), dtype=float).ravel()
        nx, nz = rho.shape
        x1d = np.linspace(le[0], re[0], nx)
        z1d = np.linspace(le[1] if le.size > 1 else 0, re[1] if re.size > 1 else 1, nz)
        return (x1d, z1d, rho), None
    except Exception as exc:
        return None, f"yt could not load {plotfiles[-1].name}: {exc}"
