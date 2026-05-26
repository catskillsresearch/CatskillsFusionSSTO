"""
Constrained unobtanium inverse — U1–U4 gates are hard constraints.

Uses ``scipy.optimize.least_squares`` (TRF / Levenberg–Marquardt class) on constraint
residuals. Stress mode: binary search on ``fusion_reactivity_scale`` for the minimum
η that admits a feasible point; margin mode: soft stay-near-nominal on design σv.
"""
from __future__ import annotations

import math
from dataclasses import replace
from typing import Literal

import numpy as np
from scipy.optimize import least_squares

from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.solve import SolveReport, _pack_unobtanium
from ssto.orbitron.simulator.types import SimulatorInputs, UnobtaniumParams
from ssto.orbitron.simulator.validation import SpecStatus, validate_design

SolveMode = Literal["stress", "margin"]

_BOUNDS_LOW = np.array([0.05, 0.05, 0.1, 1.0e5, 0.1, 0.1, 1.0, 0.1])
_BOUNDS_HIGH = np.array([1.0, 1.0, 50.0, 1.0e8, 50.0, 50.0, 5000.0, 50.0])
_CONSTRAINT_WEIGHT = 25.0


def _inputs_from_x(base: SimulatorInputs, x: np.ndarray) -> SimulatorInputs:
    throttle, comp = float(x[0]), float(x[1])
    return replace(
        base,
        pad=replace(
            base.pad,
            pad_apu_online=True,
            bleed_air_open=True,
            startup_trigger=True,
            throttle=max(0.05, min(1.0, throttle)),
            compressor=max(0.05, min(1.0, comp)),
        ),
        unobtanium=_pack_unobtanium(x.tolist(), fusion_scale_max=5000.0),
    )


def _hard_constraint_values(
    inp: SimulatorInputs,
    *,
    target_mw: float,
    power_tolerance_mw: float = 0.2,
) -> tuple[np.ndarray, object, object]:
    """Inequality constraints c(x) >= 0."""
    res = evaluate_steady_state(inp)
    vrep = validate_design(inp, res, power_tolerance_mw=power_tolerance_mw)
    g = inp.geometry
    u = inp.unobtanium

    from ssto.orbitron.simulator.physics_constants import (
        BEAM_CURRENT_MIN_MA,
        EMISSION_FIELD_LIMIT_V_M,
        LOG10_DENSITY_MIN,
    )

    e_lim = EMISSION_FIELD_LIMIT_V_M * u.field_emission_margin
    q_allow = u.max_wall_heat_flux_W_m2 * u.ch4_cooling_effectiveness
    b_max = 2.0 * u.hts_capability_scale

    c = np.array(
        [
            res.gross_power_mw - (target_mw - power_tolerance_mw),
            e_lim - res.cathode_surface_field_V_m,
            q_allow - res.wall_heat_flux_W_m2,
            b_max - g.B_axial_tesla + 1e-3,
            res.beam_current_ma - BEAM_CURRENT_MIN_MA
            if res.gross_power_mw >= 0.5
            else 1.0,
            res.log10_density - LOG10_DENSITY_MIN if res.gross_power_mw >= 0.5 else 1.0,
        ],
        dtype=float,
    )
    return c, res, vrep


def _residual_vector(
    x: np.ndarray,
    base: SimulatorInputs,
    *,
    target_mw: float,
    power_tolerance_mw: float,
    mode: SolveMode,
    u0: UnobtaniumParams,
) -> np.ndarray:
    inp = _inputs_from_x(base, x)
    c, res, _ = _hard_constraint_values(inp, target_mw=target_mw, power_tolerance_mw=power_tolerance_mw)
    r_power = (res.gross_power_mw - target_mw) / max(power_tolerance_mw, 0.05) * (
        3.0 if mode == "margin" else 1.0
    )
    r_con = np.array([max(0.0, -float(ci)) * _CONSTRAINT_WEIGHT for ci in c], dtype=float)
    if mode == "margin":
        wall_nom = u0.max_wall_heat_flux_W_m2
        wall_ratio = x[3] / wall_nom if wall_nom > 0 else 1.0
        r_nom = np.array(
            [
                (x[2] - 1.0) * 0.15,
                (wall_ratio - 1.0) * 0.15,
                (x[4] - 1.0) * 0.15,
                (x[5] - 1.0) * 0.15,
                (x[6] - 1.0) * 0.15,
                (x[7] - 1.0) * 0.15,
            ],
            dtype=float,
        )
        return np.concatenate(([r_power], r_con, r_nom))
    # stress: bias toward lower η_react when constraints are slack
    r_eta = np.array([(x[6] - 1.0) / max(float(x[6]), 1.0) * 0.05], dtype=float)
    return np.concatenate(([r_power], r_con, r_eta))


def _is_feasible(
    x: np.ndarray,
    base: SimulatorInputs,
    *,
    target_mw: float,
    power_tolerance_mw: float,
) -> bool:
    inp = _inputs_from_x(base, x)
    c, res, vrep = _hard_constraint_values(inp, target_mw=target_mw, power_tolerance_mw=power_tolerance_mw)
    if any(ci < -1e-6 for ci in c):
        return False
    if abs(res.gross_power_mw - target_mw) > power_tolerance_mw:
        return False
    if any(ch.status == SpecStatus.FAIL for ch in vrep.checks):
        return False
    return bool(vrep.design_validated)


def _least_squares_point(
    base: SimulatorInputs,
    x0: np.ndarray,
    *,
    target_mw: float,
    mode: SolveMode,
    power_tolerance_mw: float,
    fusion_scale_max: float,
    fixed_eta: float | None = None,
) -> np.ndarray:
    u0 = base.unobtanium
    high = _BOUNDS_HIGH.copy()
    high[6] = fusion_scale_max
    free_idx = [0, 1, 2, 3, 4, 5, 7] if fixed_eta is not None else list(range(8))
    x_full = np.clip(x0.copy(), _BOUNDS_LOW, high)
    if fixed_eta is not None:
        x_full[6] = fixed_eta

    def pack(x_free: np.ndarray) -> np.ndarray:
        out = x_full.copy()
        for i, j in enumerate(free_idx):
            out[j] = x_free[i]
        return out

    def fun(x_free: np.ndarray) -> np.ndarray:
        return _residual_vector(
            pack(x_free),
            base,
            target_mw=target_mw,
            power_tolerance_mw=power_tolerance_mw,
            mode=mode,
            u0=u0,
        )

    x_free0 = np.array([x_full[j] for j in free_idx], dtype=float)
    lo = [_BOUNDS_LOW[j] for j in free_idx]
    hi = [high[j] for j in free_idx]
    out = least_squares(
        fun,
        x_free0,
        bounds=(lo, hi),
        method="trf",
        ftol=1e-6,
        xtol=1e-6,
        max_nfev=60,
    )
    return np.clip(pack(out.x), _BOUNDS_LOW, high)


def _stress_minimum_eta(
    base: SimulatorInputs,
    *,
    target_mw: float,
    fusion_scale_max: float,
    power_tolerance_mw: float,
) -> tuple[float, np.ndarray] | None:
    """Binary search minimum fusion_reactivity_scale with feasible least-squares sub-solve."""
    u0 = base.unobtanium
    x0 = np.array(
        [
            base.pad.throttle or 0.85,
            base.pad.compressor or 0.85,
            u0.field_emission_margin,
            u0.max_wall_heat_flux_W_m2,
            u0.ch4_cooling_effectiveness,
            u0.hts_capability_scale,
            1.0,
            u0.beam_coupling_scale,
        ],
        dtype=float,
    )

    def trial(eta: float) -> np.ndarray | None:
        x = _least_squares_point(
            base,
            x0,
            target_mw=target_mw,
            mode="stress",
            power_tolerance_mw=power_tolerance_mw,
            fusion_scale_max=fusion_scale_max,
            fixed_eta=eta,
        )
        if _is_feasible(x, base, target_mw=target_mw, power_tolerance_mw=power_tolerance_mw):
            return x
        return None

    if trial(fusion_scale_max) is None:
        return None

    lo, hi = 1.0, fusion_scale_max
    best_x = trial(hi)
    assert best_x is not None
    for _ in range(22):
        mid = math.sqrt(lo * hi)
        xm = trial(mid)
        if xm is not None:
            hi = mid
            best_x = xm
        else:
            lo = mid
    return hi, best_x


def solve_unobtanium_constrained(
    base: SimulatorInputs,
    target_mw: float | None = None,
    *,
    mode: SolveMode = "stress",
    fusion_scale_max: float = 5000.0,
    power_tolerance_mw: float = 0.2,
) -> SolveReport:
    """
    Constrained inverse: ``success=True`` only if U1–U4 pass and power is on target.

    Stress: minimum ``fusion_reactivity_scale`` (literature σv). Margin: near-nominal knobs (design σv).
    """
    target = target_mw if target_mw is not None else base.scales.target_gross_power_mw
    u0 = base.unobtanium
    x0 = np.array(
        [
            base.pad.throttle or 0.85,
            base.pad.compressor or 0.85,
            u0.field_emission_margin,
            u0.max_wall_heat_flux_W_m2,
            u0.ch4_cooling_effectiveness,
            u0.hts_capability_scale,
            max(1.0, u0.fusion_reactivity_scale),
            u0.beam_coupling_scale,
        ],
        dtype=float,
    )

    if mode == "stress":
        found = _stress_minimum_eta(
            base,
            target_mw=target,
            fusion_scale_max=fusion_scale_max,
            power_tolerance_mw=power_tolerance_mw,
        )
        if found is None:
            x_best = _least_squares_point(
                base,
                x0,
                target_mw=target,
                mode="stress",
                power_tolerance_mw=power_tolerance_mw,
                fusion_scale_max=fusion_scale_max,
            )
            solved = _inputs_from_x(base, x_best)
            res = evaluate_steady_state(solved)
            vrep = validate_design(solved, res, power_tolerance_mw=power_tolerance_mw)
            return SolveReport(
                success=False,
                message="Constrained stress inverse — INFEASIBLE on literature σv + U1–U4",
                inputs=solved,
                result=res,
                residual_mw=res.gross_power_mw - target,
                validation=vrep,
            )
        _eta_min, x_best = found
        solved = _inputs_from_x(base, x_best)
    else:
        x_best = _least_squares_point(
            base,
            x0,
            target_mw=target,
            mode="margin",
            power_tolerance_mw=power_tolerance_mw,
            fusion_scale_max=min(fusion_scale_max, 5.0),
        )
        solved = _inputs_from_x(base, x_best)

    res = evaluate_steady_state(solved)
    vrep = validate_design(solved, res, power_tolerance_mw=power_tolerance_mw)
    hard_fail = any(c.status == SpecStatus.FAIL for c in vrep.checks)
    feasible = vrep.design_validated and not hard_fail

    return SolveReport(
        success=feasible,
        message=(
            f"Constrained {mode} inverse (least_squares)"
            + (" OK" if feasible else " — INFEASIBLE: gates or power not met")
        ),
        inputs=solved,
        result=res,
        residual_mw=res.gross_power_mw - target,
        validation=vrep,
    )
