#!/usr/bin/env python
"""
End-to-end surrogate map generation for Orbitron FlightGear / JSBSim.

Steps:
  1) Grid over (throttle, compressor) in [0, 1]
  2) For each point: run laminar_flow_2d_arcjet.py with PICMI overrides from
     ssto/orbitron/assembly_specs/orbitron_physics_surrogate.yaml (see --physics-spec)
  3) Reduce last WarpX plotfile: mean |rho_electrons|; mean |rho_stabilizing_beam| in a
     notional viewport ROI (toward -X, horizontal stand convention) and domain mean
  4) Build CSV scalars from rho proxies using surrogate_engineering scales in YAML
  5) Run tools/warpx_to_jsbsim_surrogate.py -> engine_surrogate.json (bilinear surfaces)

WarpX Python: set WARPX_PYTHON to the interpreter that has pywarpx (often not Poetry).
Default: same as this script's interpreter.

From repo root after: act
  python tools/build_surrogate_map.py
  python tools/build_surrogate_map.py --dry-run --grid 3
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import subprocess
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import orbitron_physics_spec as _phys  # noqa: E402
from orbitron_aircraft_pkg import aircraft_package_dir  # noqa: E402


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _median(xs: list[float]) -> float:
    ys = sorted(x for x in xs if math.isfinite(x))
    if not ys:
        return 1.0
    n = len(ys)
    mid = n // 2
    if n % 2 == 1:
        return ys[mid]
    return 0.5 * (ys[mid - 1] + ys[mid])


def reduce_last_plotfile_mean_rho(diags_parent: Path) -> float:
    """Mean |rho_electrons| on last density_diag plotfile under diags_parent."""
    plotfiles = sorted(diags_parent.glob("density_diag*"))
    if not plotfiles:
        return float("nan")

    try:
        import numpy as np
        import yt
    except ImportError as e:
        raise RuntimeError(
            "yt (and numpy) required for reduction. Install in Poetry env: poetry add yt"
        ) from e

    yt.funcs.mylog.setLevel(50)
    last = plotfiles[-1]
    ds = yt.load(str(last))
    grid = ds.covering_grid(level=0, left_edge=ds.domain_left_edge, dims=ds.domain_dimensions)
    rho = np.abs(grid[("boxlib", "rho_electrons")].v.squeeze())
    return float(np.mean(rho))


def _beam_rho_field(ds) -> tuple[str, str] | None:
    """Return (ftype, fname) for deposited stabilizing_beam charge density if present."""
    for f in ds.field_list:
        if len(f) < 2:
            continue
        if f[1] in ("rho_stabilizing_beam", "rho_beam", "stabilizing_beam"):
            return f[0], f[1]
    return None


def reduce_last_plotfile_beam_screen_kw_proxy(
    diags_parent: Path,
    *,
    x_cutoff_m: float = -0.005,
    z_half_width_m: float = 0.022,
    r_inner_m: float = 0.012,
    r_outer_m: float = 0.048,
) -> tuple[float, float]:
    """
    From last WarpX density plotfile:
      * rho_beam_dom: mean |rho_stabilizing_beam| over domain (beam activity proxy)
      * rho_beam_screen: mean |rho_beam| in a notional viewport ROI (x<0 toward -X exit,
        |z| slit, excluding cathode core) — same geometry order as horizontal test stand.

    Returns (rho_beam_screen_mean, rho_beam_domain_mean). nan if no beam field / no plotfile.
    """
    plotfiles = sorted(diags_parent.glob("density_diag*"))
    if not plotfiles:
        return float("nan"), float("nan")

    try:
        import numpy as np
        import yt
    except ImportError as e:
        raise RuntimeError(
            "yt (and numpy) required for reduction. Install in Poetry env: poetry add yt"
        ) from e

    yt.funcs.mylog.setLevel(50)
    ds = yt.load(str(plotfiles[-1]))
    bf = _beam_rho_field(ds)
    if bf is None:
        return float("nan"), float("nan")

    ftype, fname = bf
    grid = ds.covering_grid(level=0, left_edge=ds.domain_left_edge, dims=ds.domain_dimensions)
    rho_b = np.abs(np.asarray(grid[(ftype, fname)].v))
    rho_b = np.squeeze(rho_b)
    if rho_b.ndim != 2:
        return float("nan"), float("nan")

    nx, nz = rho_b.shape
    le = np.asarray(ds.domain_left_edge.to_value(), dtype=float).ravel()
    re = np.asarray(ds.domain_right_edge.to_value(), dtype=float).ravel()
    dd = np.asarray(ds.domain_dimensions, dtype=int).ravel()
    # WarpX 2D: either (nx,nz) in x–z or (nx,1,nz) in plotfile
    if dd.size >= 3 and int(dd[1]) == 1:
        x1d = np.linspace(le[0], re[0], nx, endpoint=False) + 0.5 * (re[0] - le[0]) / max(nx, 1)
        zax = 2 if le.size > 2 else 1
        z1d = np.linspace(le[zax], re[zax], nz, endpoint=False) + 0.5 * (re[zax] - le[zax]) / max(nz, 1)
    else:
        x1d = np.linspace(le[0], re[0], nx, endpoint=False) + 0.5 * (re[0] - le[0]) / max(nx, 1)
        z1d = np.linspace(le[1], re[1], nz, endpoint=False) + 0.5 * (re[1] - le[1]) / max(nz, 1)
    xm, zm = np.meshgrid(x1d, z1d, indexing="ij")
    r = np.sqrt(xm * xm + zm * zm)
    # Beam injected at +x, travels -x; “screen” side: upstream half-space, slit, outside cathode
    mask = (
        (xm < x_cutoff_m)
        & (np.abs(zm) < z_half_width_m)
        & (r > r_inner_m)
        & (r < r_outer_m)
    )
    dom_mean = float(np.mean(rho_b))
    if not np.any(mask):
        return float("nan"), dom_mean
    screen_mean = float(np.mean(rho_b[mask]))
    return screen_mean, dom_mean


def beam_screen_kw_from_rho(
    rho_screen: float,
    rho_dom: float,
    rho_screen_ref: float,
    throttle: float,
    compressor: float,
    eng: dict[str, float] | None = None,
) -> tuple[float, float]:
    """
    Map reduced beam charge proxies to engineering scalars for surrogate fitting.

    beam_screen_kw: effective power deposited into notional viewport / gas in front of
    screen, from P ~ I_eff * V with V = 8 MV story (same order as Shuttle: physics in
    FDM, FG only reads levels).

    beam_current_ma: I_ma = P_kw / beam_screen_kw_per_ma (consistent with equivalent DC story).
    """
    eng = eng or {}
    k_ma = float(eng.get("beam_current_scale_ma", 95.0))
    k_kw = float(eng.get("beam_screen_kw_per_ma", 8.0))
    t = max(0.0, min(1.0, throttle))
    c = max(0.0, min(1.0, compressor))
    if math.isfinite(rho_screen) and math.isfinite(rho_screen_ref) and rho_screen_ref > 0:
        rn = max(0.0, min(5.0, rho_screen / rho_screen_ref))
    else:
        rn = max(0.15, min(2.5, 0.4 + 0.6 * t * c))
    if math.isfinite(rho_dom) and rho_dom > 0 and math.isfinite(rho_screen):
        # Penalize if beam never leaves injection side (domain mean >> screen leakage)
        leak = min(2.0, max(0.2, rho_screen / (rho_dom + 1e-30)))
        rn *= 0.35 + 0.65 * min(1.0, leak)
    # mA scale: NBI throttle opens confinement / coupling to beam line
    beam_current_ma = k_ma * rn * (0.15 + 0.85 * t) * (0.25 + 0.75 * c)
    beam_screen_kw = beam_current_ma * k_kw
    return beam_screen_kw, beam_current_ma


def grid_points(n: int) -> list[tuple[float, float]]:
    if n < 2:
        n = 2
    step = 1.0 / (n - 1)
    pts: list[tuple[float, float]] = []
    for i in range(n):
        for j in range(n):
            pts.append((round(i * step, 6), round(j * step, 6)))
    return pts


def parse_csv_floats(s: str) -> list[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def run_one_warpx(
    *,
    warpx_python: str,
    arcjet_script: Path,
    throttle: float,
    compressor: float,
    run_dir: Path,
    steps: int,
    diag_period: int,
    picmi_overrides_json: Path | None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    write_dir = str(run_dir / "diags")
    cmd = [
        warpx_python,
        str(arcjet_script),
        "--throttle",
        str(throttle),
        "--compressor",
        str(compressor),
        "--write-dir",
        write_dir,
        "--steps",
        str(steps),
        "--diag-period",
        str(diag_period),
    ]
    if picmi_overrides_json is not None:
        cmd.extend(["--overrides", str(picmi_overrides_json)])
    subprocess.run(cmd, cwd=str(arcjet_script.parent), check=True)


def scalar_outputs(
    throttle: float,
    compressor: float,
    rho_mean: float,
    rho_ref: float,
    rho_beam_screen: float,
    rho_beam_dom: float,
    rho_beam_screen_ref: float,
    eng: dict[str, float] | None = None,
) -> tuple[float, float, float, float, float, float]:
    """Map PIC proxy + controls to surrogate CSV targets (engineering placeholders)."""
    eng = eng or {}
    if math.isfinite(rho_mean) and rho_ref > 0 and math.isfinite(rho_ref):
        rn = max(0.15, min(3.0, rho_mean / rho_ref))
    else:
        rn = 1.0
    t = max(0.0, min(1.0, throttle))
    c = max(0.0, min(1.0, compressor))
    thrust_lbf = float(eng.get("thrust_lbf_scale", 4000.0)) * t * c * rn
    mass_flow_kgps = float(eng.get("mass_flow_kgps_scale", 2.5)) * t * c * rn
    gross_power_mw = float(eng.get("gross_power_mw_scale", 3.5)) * t * c * rn
    heat_kw = float(eng.get("heat_kw_scale", 400.0)) * t * c * rn
    bkw, bma = beam_screen_kw_from_rho(
        rho_beam_screen, rho_beam_dom, rho_beam_screen_ref, t, c, eng=eng
    )
    return thrust_lbf, mass_flow_kgps, gross_power_mw, heat_kw, bkw, bma


def main() -> int:
    root = _repo_root()
    _pkg = aircraft_package_dir(root)
    ap = argparse.ArgumentParser(description="Build surrogate map from WarpX sweep + fit JSON")
    ap.add_argument("--grid", type=int, default=4, help="NxN grid in [0,1] (default 4 => 16 runs)")
    ap.add_argument(
        "--throttle-points",
        type=str,
        default="",
        help='Comma-separated throttle values, e.g. "0,0.5,1" (overrides --grid)',
    )
    ap.add_argument(
        "--compressor-points",
        type=str,
        default="",
        help='Comma-separated compressor values (overrides --grid)',
    )
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--diag-period", type=int, default=100)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip WarpX; write CSV with synthetic rho proxy (tests JSON pipeline only)",
    )
    ap.add_argument(
        "--work-dir",
        type=Path,
        default=root / "build" / "orbitron" / "warpx-runs",
        help="Directory for per-run WarpX outputs",
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=root / "build" / "orbitron" / "surrogate_sweep_results.csv",
    )
    ap.add_argument(
        "--out-json",
        type=Path,
        default=root / "Aircraft" / _pkg / "engine_surrogate.json",
    )
    ap.add_argument(
        "--warpx-python",
        default=os.environ.get("WARPX_PYTHON", sys.executable),
        help="Python with pywarpx (default: $WARPX_PYTHON or this interpreter)",
    )
    ap.add_argument("--print-set-xml", action="store_true")
    ap.add_argument(
        "--physics-spec",
        type=Path,
        default=None,
        help="orbitron_physics_surrogate.yaml (default: ssto/orbitron/assembly_specs/…)",
    )
    args = ap.parse_args()

    phys_path = args.physics_spec or _phys.default_physics_spec_path(root)
    if not phys_path.is_file():
        print(f"error: physics spec not found: {phys_path}", file=sys.stderr)
        return 1
    ph = _phys.load_physics_spec(phys_path)
    picmi_json = root / "build" / "orbitron" / "generated" / "picmi_overrides.json"
    _phys.write_picmi_overrides(picmi_json, ph)
    x_cutoff_m, z_half_width_m, r_inner_m, r_outer_m = _phys.beam_roi_tuple(ph)
    eng = _phys.engineering_scalars(ph)

    warpx_sw = ph.get("warpx_sweep") or {}
    arcjet_rel = str(warpx_sw.get("arcjet_script", "ssto/orbitron/laminar_flow_2d_arcjet.py"))
    arcjet_script = (root / arcjet_rel).resolve()
    if not arcjet_script.is_file():
        print(f"error: arcjet PICMI script not found: {arcjet_script}", file=sys.stderr)
        return 1

    surrogate_tool = root / "tools" / "warpx_to_jsbsim_surrogate.py"

    if args.throttle_points and args.compressor_points:
        ts = parse_csv_floats(args.throttle_points)
        cs = parse_csv_floats(args.compressor_points)
        points = [(t, c) for t in ts for c in cs]
    else:
        points = grid_points(args.grid)

    args.work_dir.mkdir(parents=True, exist_ok=True)

    raw_rows: list[tuple[float, float, float, float, float, float, Path]] = []

    for ti, (throttle, compressor) in enumerate(points):
        tag = f"t{throttle:.4f}_c{compressor:.4f}".replace(".", "p")
        run_dir = args.work_dir / tag

        if args.dry_run:
            rho_m = 1.0
            rho_bs = 0.6 + 0.4 * throttle * compressor
            rho_bd = 1.2
        else:
            print(f"[{ti + 1}/{len(points)}] WarpX throttle={throttle} compressor={compressor}")
            try:
                run_one_warpx(
                    warpx_python=args.warpx_python,
                    arcjet_script=arcjet_script,
                    throttle=throttle,
                    compressor=compressor,
                    run_dir=run_dir,
                    steps=args.steps,
                    diag_period=args.diag_period,
                    picmi_overrides_json=picmi_json,
                )
            except subprocess.CalledProcessError as e:
                print(f"error: WarpX run failed: {e}", file=sys.stderr)
                return 1
            diags = run_dir / "diags"
            try:
                rho_m = reduce_last_plotfile_mean_rho(diags)
            except Exception as ex:
                print(f"warning: reduction failed ({ex}); using rho_mean=nan", file=sys.stderr)
                rho_m = float("nan")
            try:
                rho_bs, rho_bd = reduce_last_plotfile_beam_screen_kw_proxy(
                    diags,
                    x_cutoff_m=x_cutoff_m,
                    z_half_width_m=z_half_width_m,
                    r_inner_m=r_inner_m,
                    r_outer_m=r_outer_m,
                )
            except Exception as ex:
                print(f"warning: beam reduction failed ({ex}); beam fields nan", file=sys.stderr)
                rho_bs, rho_bd = float("nan"), float("nan")

        raw_rows.append((throttle, compressor, rho_m, rho_bs, rho_bd, run_dir))

    rho_ref = _median([r[2] for r in raw_rows])
    rho_beam_screen_ref = _median([r[3] for r in raw_rows if math.isfinite(r[3])])
    if not math.isfinite(rho_beam_screen_ref) or rho_beam_screen_ref <= 0:
        rho_beam_screen_ref = 1.0

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "throttle",
                "compressor",
                "rho_mean_electrons",
                "rho_beam_screen_mean",
                "rho_beam_domain_mean",
                "thrust_lbf",
                "mass_flow_kgps",
                "gross_power_mw",
                "heat_kw",
                "beam_screen_kw",
                "beam_current_ma",
                "run_dir",
            ]
        )
        for throttle, compressor, rho_m, rho_bs, rho_bd, run_dir in raw_rows:
            tl, md, gp, hk, bkw, bma = scalar_outputs(
                throttle, compressor, rho_m, rho_ref, rho_bs, rho_bd, rho_beam_screen_ref, eng=eng
            )
            w.writerow(
                [
                    f"{throttle:g}",
                    f"{compressor:g}",
                    f"{rho_m:g}" if math.isfinite(rho_m) else "",
                    f"{rho_bs:g}" if math.isfinite(rho_bs) else "",
                    f"{rho_bd:g}" if math.isfinite(rho_bd) else "",
                    f"{tl:g}",
                    f"{md:g}",
                    f"{gp:g}",
                    f"{hk:g}",
                    f"{bkw:g}",
                    f"{bma:g}",
                    str(run_dir),
                ]
            )

    print(f"Wrote CSV: {args.out_csv}")
    print(f"rho_ref (median abs rho_e): {rho_ref:g}")
    print(f"rho_beam_screen_ref (median beam ROI |rho|): {rho_beam_screen_ref:g}")

    cmd = [
        sys.executable,
        str(surrogate_tool),
        "--csv",
        str(args.out_csv),
        "--out-json",
        str(args.out_json),
    ]
    if args.print_set_xml:
        cmd.append("--print-set-xml")
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=str(root), check=True)
    print(f"Surrogate JSON: {args.out_json}")
    print(
        "Place engine_surrogate.json beside the aircraft *-set.xml; "
        "surrogate_load.nas loads it at startup."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
