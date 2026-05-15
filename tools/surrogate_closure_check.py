#!/usr/bin/env python3
"""Check 0D jet–power closure for the Orbitron surrogate (paper discipline).

Uses ``orbitron_physics_surrogate.yaml`` ``surrogate_engineering`` for η and, either:
  * **YAML scales** — same formulas as ``build_surrogate_map.scalar_outputs`` (thrust_lbf, ṁ, P × T·C·r_n), or
  * **engine_surrogate.json** — bilinear ``y = c0 + c_t·T + c_c·C + c_tc·T·C`` for thrust, mdot, power.

Closure (stand 0D narrative):
  P_jet = η · P_gross · 1e6   [W]
  v_e = F / ṁ,  P_from_thrust = F² / (2ṁ)  (ṁ > 0)
  Require P_from_thrust ≈ P_jet and F² ≈ 2 · P_jet · ṁ.

Examples (repo root, Poetry on):
  python tools/surrogate_closure_check.py
  python tools/surrogate_closure_check.py --surrogate-json Aircraft/Orbitron-TestStand/engine_surrogate.json
  python tools/surrogate_closure_check.py --throttle 0.7 --compressor 0.85 --rn 0.95
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import yaml

LBF_TO_N = 4.4482216152605


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_physics_spec() -> Path:
    return (
        _repo_root()
        / "ssto"
        / "orbitron"
        / "assembly_specs"
        / "orbitron_physics_surrogate.yaml"
    )


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _bilinear_eval(c: dict[str, float], t: float, cpress: float) -> float:
    return (
        float(c.get("c0", 0.0))
        + float(c.get("c_t", 0.0)) * t
        + float(c.get("c_c", 0.0)) * cpress
        + float(c.get("c_tc", 0.0)) * t * cpress
    )


def _coeffs_from_surface(doc: dict[str, object], key: str) -> dict[str, float]:
    block = doc.get(key)
    if not isinstance(block, dict):
        return {"c0": 0.0, "c_t": 0.0, "c_c": 0.0, "c_tc": 0.0}
    coeff = block.get("coeffs")
    if not isinstance(coeff, dict):
        return {"c0": 0.0, "c_t": 0.0, "c_c": 0.0, "c_tc": 0.0}
    return {
        "c0": float(coeff.get("c0", 0.0)),
        "c_t": float(coeff.get("c_t", 0.0)),
        "c_c": float(coeff.get("c_c", 0.0)),
        "c_tc": float(coeff.get("c_tc", 0.0)),
    }


def _yaml_scalars(
    eng: dict[str, float],
    *,
    throttle: float,
    compressor: float,
    rn: float,
) -> tuple[float, float, float]:
    t = _clamp01(throttle)
    c = _clamp01(compressor)
    r = max(0.0, float(rn)) if math.isfinite(rn) else 1.0
    thrust_lbf = float(eng.get("thrust_lbf_scale", 4000.0)) * t * c * r
    mdot = float(eng.get("mass_flow_kgps_scale", 2.5)) * t * c * r
    p_mw = float(eng.get("gross_power_mw_scale", 3.5)) * t * c * r
    return thrust_lbf, mdot, p_mw


def _json_scalars(
    doc: dict[str, object],
    *,
    throttle: float,
    compressor: float,
) -> tuple[float, float, float]:
    t = _clamp01(throttle)
    c = _clamp01(compressor)
    tc = _coeffs_from_surface(doc, "thrust_lbf_surface")
    mc = _coeffs_from_surface(doc, "mass_flow_kgps_surface")
    pc = _coeffs_from_surface(doc, "gross_power_mw_surface")
    return (
        _bilinear_eval(tc, t, c),
        _bilinear_eval(mc, t, c),
        _bilinear_eval(pc, t, c),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--physics-spec",
        type=Path,
        default=_default_physics_spec(),
        help="orbitron_physics_surrogate.yaml",
    )
    ap.add_argument(
        "--surrogate-json",
        type=Path,
        default=None,
        help="engine_surrogate.json (bilinear); if omitted, use YAML scales × T·C·r_n",
    )
    ap.add_argument("--throttle", type=float, default=1.0)
    ap.add_argument("--compressor", type=float, default=1.0)
    ap.add_argument(
        "--rn",
        type=float,
        default=1.0,
        help="PIC/density proxy multiplier (YAML-scale mode only; JSON mode ignores)",
    )
    ap.add_argument(
        "--tol-rel",
        type=float,
        default=0.06,
        help="Max relative error for closure checks (default 6%%)",
    )
    args = ap.parse_args()

    spec_path = args.physics_spec.resolve()
    if not spec_path.is_file():
        print(f"error: physics spec not found: {spec_path}", file=sys.stderr)
        return 1

    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("error: physics spec root must be a mapping", file=sys.stderr)
        return 1
    eng_raw = data.get("surrogate_engineering")
    if not isinstance(eng_raw, dict):
        print("error: missing surrogate_engineering", file=sys.stderr)
        return 1
    eng = {k: float(v) for k, v in eng_raw.items() if isinstance(v, (int, float))}

    eta = float(eng.get("jet_propulsive_efficiency", 0.55))
    design_mw = float(eng.get("design_gross_fusion_power_mw", eng.get("gross_power_mw_scale", 0.0)))
    scale_mw = float(eng.get("gross_power_mw_scale", 0.0))

    t = args.throttle
    c = args.compressor
    rn = args.rn

    if args.surrogate_json is not None:
        jp = args.surrogate_json.resolve()
        if not jp.is_file():
            print(f"error: surrogate JSON not found: {jp}", file=sys.stderr)
            return 1
        doc = json.loads(jp.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            print("error: surrogate JSON root must be an object", file=sys.stderr)
            return 1
        mode = f"bilinear JSON ({jp.name})"
        thrust_lbf, mdot, p_mw = _json_scalars(doc, throttle=t, compressor=c)
    else:
        mode = "YAML scales × T·C·r_n"
        thrust_lbf, mdot, p_mw = _yaml_scalars(eng, throttle=t, compressor=c, rn=rn)

    f_n = thrust_lbf * LBF_TO_N
    p_gross_w = p_mw * 1.0e6
    p_jet_target = eta * p_gross_w

    if mdot <= 1e-12:
        print("error: ṁ non-positive; cannot evaluate closure", file=sys.stderr)
        return 1

    v_e = f_n / mdot
    p_from_thrust = (f_n * f_n) / (2.0 * mdot)
    f2 = f_n * f_n
    f2_from_jet = 2.0 * p_jet_target * mdot

    rel_a = abs(p_from_thrust - p_jet_target) / max(p_jet_target, 1.0)
    rel_b = abs(f2 - f2_from_jet) / max(f2_from_jet, 1.0)
    jet_mw_derived = p_from_thrust * 1.0e-6
    jet_mw_booked = p_jet_target * 1.0e-6

    print("Orbitron surrogate closure check")
    print(f"  mode:        {mode}")
    print(f"  T, C, r_n:   {t:g}, {c:g}, {rn:g}" + ("  (r_n N/A in JSON mode)" if args.surrogate_json else ""))
    print(f"  thrust_lbf:  {thrust_lbf:.4f}  →  F = {f_n:.2f} N")
    print(f"  ṁ (kg/s):    {mdot:.6f}")
    print(f"  gross (MW):  {p_mw:.6f}")
    print(f"  η (jet):     {eta:g}")
    print(f"  P_jet book:  {jet_mw_booked:.6f} MW  (η · gross)")
    print(f"  v_e = F/ṁ:   {v_e:.3f} m/s")
    print(f"  ½ṁv_e²:      {jet_mw_derived:.6f} MW  (= F²/(2ṁ))")
    print(f"  rel err P:   {100.0 * rel_a:.3f}%   (F²/(2ṁ) vs η·P_gross)")
    print(f"  rel err F²:  {100.0 * rel_b:.3f}%   (F² vs 2·η·P_gross·ṁ)")

    if design_mw > 0 and scale_mw > 0 and abs(design_mw - scale_mw) > 0.01:
        print(
            f"  note: design_gross_fusion_power_mw ({design_mw:g}) ≠ gross_power_mw_scale ({scale_mw:g})",
            file=sys.stderr,
        )

    tol = float(args.tol_rel)
    bad = rel_a > tol or rel_b > tol
    if bad:
        print(
            f"\nFAIL: relative error exceeds --tol-rel ({100.0 * tol:.1f}%).",
            file=sys.stderr,
        )
        return 1

    print("\nOK: closure within tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
