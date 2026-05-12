#!/usr/bin/env python3
"""
Build multivariate surrogate surfaces for Orbitron test-stand runtime.

Primary fit form (bilinear in throttle T and compressor C):
    y = c0 + c_t*T + c_c*C + c_tc*T*C

CSV expected columns (minimum):
  throttle, compressor, thrust_lbf, mass_flow_kgps
Optional CSV columns (WarpX beam / viewport model, see tools/build_surrogate_map.py):
  beam_screen_kw, beam_current_ma  (fit uses beam_screen_kw; current = P/8 mA at 8 MV equivalent)

Run from repo root (activate Poetry first; ``act`` is
``eval "$(poetry env activate)"``):

  act
  python tools/warpx_to_jsbsim_surrogate.py --placeholder --out-json ...
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _float(row: dict[str, str], key: str) -> float | None:
    raw = row.get(key)
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _solve_4x4(a: list[list[float]], b: list[float]) -> list[float]:
    """Solve A x = b using Gauss-Jordan elimination with pivoting."""
    m = [row[:] + [rhs] for row, rhs in zip(a, b)]
    n = 4
    for col in range(n):
        pivot = col
        max_abs = abs(m[col][col])
        for r in range(col + 1, n):
            v = abs(m[r][col])
            if v > max_abs:
                max_abs = v
                pivot = r
        if math.isclose(max_abs, 0.0):
            return [0.0, 0.0, 0.0, 0.0]
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        for k in range(col, n + 1):
            m[col][k] /= div
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            if math.isclose(factor, 0.0):
                continue
            for k in range(col, n + 1):
                m[r][k] -= factor * m[col][k]
    return [m[i][n] for i in range(n)]


def fit_bilinear(points: list[tuple[float, float, float]]) -> dict[str, float]:
    """
    Fit y = c0 + c_t*T + c_c*C + c_tc*T*C via normal equations.
    Falls back to zeros if system is singular.
    """
    if len(points) < 4:
        # Not enough points to support a true 2D fit.
        y0 = sum(p[2] for p in points) / len(points) if points else 0.0
        return {"c0": y0, "c_t": 0.0, "c_c": 0.0, "c_tc": 0.0}

    xtx = [[0.0] * 4 for _ in range(4)]
    xty = [0.0] * 4
    for t, c, y in points:
        x = [1.0, t, c, t * c]
        for i in range(4):
            xty[i] += x[i] * y
            for j in range(4):
                xtx[i][j] += x[i] * x[j]

    c0, c_t, c_c, c_tc = _solve_4x4(xtx, xty)
    return {"c0": c0, "c_t": c_t, "c_c": c_c, "c_tc": c_tc}


def _surface_block(coeffs: dict[str, float]) -> dict[str, object]:
    return {"type": "bilinear", "coeffs": coeffs}


def _print_set_xml(doc: dict[str, object]) -> None:
    def coeffs(name: str) -> dict[str, float]:
        block = doc.get(name, {})
        if not isinstance(block, dict):
            return {"c0": 0.0, "c_t": 0.0, "c_c": 0.0, "c_tc": 0.0}
        coeff = block.get("coeffs", {})
        if not isinstance(coeff, dict):
            return {"c0": 0.0, "c_t": 0.0, "c_c": 0.0, "c_tc": 0.0}
        return {
            "c0": float(coeff.get("c0", 0.0)),
            "c_t": float(coeff.get("c_t", 0.0)),
            "c_c": float(coeff.get("c_c", 0.0)),
            "c_tc": float(coeff.get("c_tc", 0.0)),
        }

    t = coeffs("thrust_lbf_surface")
    m = coeffs("mass_flow_kgps_surface")
    p = coeffs("gross_power_mw_surface")
    h = coeffs("heat_kw_surface")
    b = coeffs("beam_screen_kw_surface")
    print(
        "\n<!-- Paste under <model> to keep defaults aligned with JSON -->\n"
        "<orbitron>\n"
        "  <surrogate>\n"
        f'    <thrust-c0 type="double">{t["c0"]}</thrust-c0>\n'
        f'    <thrust-ct type="double">{t["c_t"]}</thrust-ct>\n'
        f'    <thrust-cc type="double">{t["c_c"]}</thrust-cc>\n'
        f'    <thrust-ctc type="double">{t["c_tc"]}</thrust-ctc>\n'
        f'    <mdot-c0 type="double">{m["c0"]}</mdot-c0>\n'
        f'    <mdot-ct type="double">{m["c_t"]}</mdot-ct>\n'
        f'    <mdot-cc type="double">{m["c_c"]}</mdot-cc>\n'
        f'    <mdot-ctc type="double">{m["c_tc"]}</mdot-ctc>\n'
        f'    <power-c0 type="double">{p["c0"]}</power-c0>\n'
        f'    <power-ct type="double">{p["c_t"]}</power-ct>\n'
        f'    <power-cc type="double">{p["c_c"]}</power-cc>\n'
        f'    <power-ctc type="double">{p["c_tc"]}</power-ctc>\n'
        f'    <heat-c0 type="double">{h["c0"]}</heat-c0>\n'
        f'    <heat-ct type="double">{h["c_t"]}</heat-ct>\n'
        f'    <heat-cc type="double">{h["c_c"]}</heat-cc>\n'
        f'    <heat-ctc type="double">{h["c_tc"]}</heat-ctc>\n'
        f'    <beam-screen-kw-c0 type="double">{b["c0"]}</beam-screen-kw-c0>\n'
        f'    <beam-screen-kw-ct type="double">{b["c_t"]}</beam-screen-kw-ct>\n'
        f'    <beam-screen-kw-cc type="double">{b["c_c"]}</beam-screen-kw-cc>\n'
        f'    <beam-screen-kw-ctc type="double">{b["c_tc"]}</beam-screen-kw-ctc>\n'
        "  </surrogate>\n"
        "</orbitron>\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Build multivariate surrogate JSON from CSV.")
    ap.add_argument("--csv", type=Path, help="Sweep results CSV")
    ap.add_argument("--out-json", type=Path, required=True, help="Output JSON path")
    ap.add_argument("--placeholder", action="store_true", help="Write demo surfaces")
    ap.add_argument(
        "--print-set-xml",
        action="store_true",
        help="Print Orbitron-TestStand-set.xml default block matching the JSON",
    )
    args = ap.parse_args()

    if args.placeholder:
        doc = {
            "meta": {
                "source": "placeholder",
                "model": "bilinear",
                "note": "Replace with WarpX-reduced CSV fit; y=c0+c_t*T+c_c*C+c_tc*T*C",
                "beam_model": (
                    "beam_screen_kw bilinear(T,C); beam_current_ma = beam_screen_kw/8 (8 MV equiv.). "
                    "WarpX path: rho_stabilizing_beam in screen ROI (build_surrogate_map.reduce_*)."
                ),
            },
            "thrust_lbf_surface": _surface_block(
                {"c0": 0.0, "c_t": 0.0, "c_c": 0.0, "c_tc": 4000.0}
            ),
            "mass_flow_kgps_surface": _surface_block(
                {"c0": 0.0, "c_t": 0.0, "c_c": 0.0, "c_tc": 2.5}
            ),
            "gross_power_mw_surface": _surface_block(
                {"c0": 0.0, "c_t": 0.0, "c_c": 0.0, "c_tc": 3.5}
            ),
            "heat_kw_surface": _surface_block(
                {"c0": 0.0, "c_t": 0.0, "c_c": 0.0, "c_tc": 400.0}
            ),
            "beam_screen_kw_surface": _surface_block(
                {"c0": 0.0, "c_t": 55.0, "c_c": 48.0, "c_tc": 320.0}
            ),
        }
    else:
        if not args.csv or not args.csv.is_file():
            print("error: --csv required unless --placeholder", file=sys.stderr)
            return 2
        rows = load_csv(args.csv)
        if not rows:
            print("error: empty CSV", file=sys.stderr)
            return 2

        thrust_points: list[tuple[float, float, float]] = []
        mdot_points: list[tuple[float, float, float]] = []
        power_points: list[tuple[float, float, float]] = []
        heat_points: list[tuple[float, float, float]] = []
        beam_kw_points: list[tuple[float, float, float]] = []

        for r in rows:
            t = _float(r, "throttle")
            c = _float(r, "compressor")
            if t is None or c is None:
                continue
            y_thrust = _float(r, "thrust_lbf")
            y_mdot = _float(r, "mass_flow_kgps")
            y_power = _float(r, "gross_power_mw")
            y_heat = _float(r, "heat_kw")
            y_beam_kw = _float(r, "beam_screen_kw")
            if y_thrust is not None:
                thrust_points.append((t, c, y_thrust))
            if y_mdot is not None:
                mdot_points.append((t, c, y_mdot))
            if y_power is not None:
                power_points.append((t, c, y_power))
            if y_heat is not None:
                heat_points.append((t, c, y_heat))
            if y_beam_kw is not None:
                beam_kw_points.append((t, c, y_beam_kw))

        doc = {
            "meta": {
                "source_csv": str(args.csv.resolve()),
                "n_rows": len(rows),
                "model": "bilinear",
                "equation": "y=c0+c_t*T+c_c*C+c_tc*T*C",
                "beam_model": (
                    "beam_screen_kw from WarpX rho_stabilizing_beam screen ROI + mapping in "
                    "build_surrogate_map.beam_screen_kw_from_rho; beam_current_ma = beam_screen_kw/8."
                ),
            },
            "thrust_lbf_surface": _surface_block(fit_bilinear(thrust_points)),
            "mass_flow_kgps_surface": _surface_block(fit_bilinear(mdot_points)),
            "gross_power_mw_surface": _surface_block(fit_bilinear(power_points)),
            "heat_kw_surface": _surface_block(fit_bilinear(heat_points)),
            "beam_screen_kw_surface": _surface_block(fit_bilinear(beam_kw_points)),
        }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_json}")

    if args.print_set_xml:
        _print_set_xml(doc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
