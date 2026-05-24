"""
Inverse solve: operating point and/or unobtanium knobs for target gross power.

``solve_unobtanium_requirements`` quantifies the minimum unobtanium performance needed
to hit the design MW target while satisfying U1–U4 gates (see ``validation.py``).
"""
from __future__ import annotations

from dataclasses import replace
from typing import NamedTuple

from scipy.optimize import minimize

from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.types import SimulatorInputs, UnobtaniumParams
from ssto.orbitron.simulator.validation import DesignValidationReport, validate_design


class SolveReport(NamedTuple):
    success: bool
    message: str
    inputs: SimulatorInputs
    result: object  # SteadyStateResult
    residual_mw: float
    validation: DesignValidationReport | None = None


def _objective(x: list[float], base: SimulatorInputs, target_mw: float) -> float:
    throttle, comp, fusion_scale, emission_margin = x
    inp = replace(
        base,
        pad=replace(
            base.pad,
            pad_apu_online=True,
            bleed_air_open=True,
            startup_trigger=True,
            throttle=max(0.05, min(1.0, throttle)),
            compressor=max(0.05, min(1.0, comp)),
        ),
        unobtanium=replace(
            base.unobtanium,
            fusion_reactivity_scale=max(0.1, fusion_scale),
            field_emission_margin=max(0.1, emission_margin),
        ),
    )
    res = evaluate_steady_state(inp)
    err = res.gross_power_mw - target_mw
    penalty = 1e3 * len(res.violations)
    return err * err + penalty


def solve_for_target_power(
    base: SimulatorInputs,
    target_mw: float | None = None,
) -> SolveReport:
    """Find throttle, compressor, and scale factors for ``target_mw`` (default 3.5)."""
    target = target_mw if target_mw is not None else base.scales.target_gross_power_mw
    x0 = [
        base.pad.throttle or 0.5,
        base.pad.compressor or 0.5,
        base.unobtanium.fusion_reactivity_scale,
        base.unobtanium.field_emission_margin,
    ]
    out = minimize(
        _objective,
        x0,
        args=(base, target),
        method="Nelder-Mead",
        options={"maxiter": 400, "xatol": 1e-3, "fatol": 1e-4},
    )
    throttle, comp, fusion_scale, emission_margin = out.x
    solved = replace(
        base,
        pad=replace(
            base.pad,
            pad_apu_online=True,
            bleed_air_open=True,
            startup_trigger=True,
            throttle=float(max(0.05, min(1.0, throttle))),
            compressor=float(max(0.05, min(1.0, comp))),
        ),
        unobtanium=replace(
            base.unobtanium,
            fusion_reactivity_scale=float(max(0.1, fusion_scale)),
            field_emission_margin=float(max(0.1, emission_margin)),
        ),
    )
    res = evaluate_steady_state(solved)
    vrep = validate_design(solved, res)
    return SolveReport(
        success=vrep.design_validated,
        message=out.message if hasattr(out, "message") else str(out),
        inputs=solved,
        result=res,
        residual_mw=res.gross_power_mw - target,
        validation=vrep,
    )


def _pack_unobtanium(x: list[float]) -> UnobtaniumParams:
    return UnobtaniumParams(
        field_emission_margin=max(0.1, x[2]),
        max_wall_heat_flux_W_m2=max(1e5, x[3]),
        ch4_cooling_effectiveness=max(0.1, x[4]),
        hts_capability_scale=max(0.1, x[5]),
        fusion_reactivity_scale=max(0.1, x[6]),
        beam_coupling_scale=max(0.1, x[7]),
    )


def solve_unobtanium_requirements(
    base: SimulatorInputs,
    target_mw: float | None = None,
    *,
    prefer_near_nominal: float = 0.15,
) -> SolveReport:
    """
    Find pad run point + all unobtanium knobs for target power with spec gates.

    Objective: hit ``target_mw``, minimize violations, keep scales near 1.0 (nominal
    = "off-the-shelf would barely work").
    """
    target = target_mw if target_mw is not None else base.scales.target_gross_power_mw
    u0 = base.unobtanium

    def objective(x: list[float]) -> float:
        throttle, comp = x[0], x[1]
        inp = replace(
            base,
            pad=replace(
                base.pad,
                pad_apu_online=True,
                bleed_air_open=True,
                startup_trigger=True,
                throttle=max(0.05, min(1.0, throttle)),
                compressor=max(0.05, min(1.0, comp)),
            ),
            unobtanium=_pack_unobtanium(x),
        )
        res = evaluate_steady_state(inp)
        err = res.gross_power_mw - target
        penalty = 2e4 * len(res.violations)
        wall_nom = u0.max_wall_heat_flux_W_m2
        wall_ratio = x[3] / wall_nom if wall_nom > 0 else 1.0
        nominal = (
            (x[2] - 1.0) ** 2
            + (wall_ratio - 1.0) ** 2
            + (x[4] - 1.0) ** 2
            + (x[5] - 1.0) ** 2
            + (x[6] - 1.0) ** 2
            + (x[7] - 1.0) ** 2
        )
        return err * err + penalty + prefer_near_nominal * nominal

    x0 = [
        base.pad.throttle or 0.85,
        base.pad.compressor or 0.85,
        u0.field_emission_margin,
        u0.max_wall_heat_flux_W_m2,
        u0.ch4_cooling_effectiveness,
        u0.hts_capability_scale,
        u0.fusion_reactivity_scale,
        u0.beam_coupling_scale,
    ]
    out = minimize(
        objective,
        x0,
        method="Nelder-Mead",
        options={"maxiter": 600, "xatol": 1e-3, "fatol": 1e-4},
    )
    throttle, comp = out.x[0], out.x[1]
    solved = replace(
        base,
        pad=replace(
            base.pad,
            pad_apu_online=True,
            bleed_air_open=True,
            startup_trigger=True,
            throttle=float(max(0.05, min(1.0, throttle))),
            compressor=float(max(0.05, min(1.0, comp))),
        ),
        unobtanium=_pack_unobtanium(out.x),
    )
    res = evaluate_steady_state(solved)
    vrep = validate_design(solved, res)
    return SolveReport(
        success=vrep.design_validated,
        message="Unobtanium requirement solve"
        + (" OK" if vrep.design_validated else f" — {vrep.summary}"),
        inputs=solved,
        result=res,
        residual_mw=res.gross_power_mw - target,
        validation=vrep,
    )


def sweep_geometry_radius(
    base: SimulatorInputs,
    r_anode_m: float,
    target_mw: float | None = None,
) -> SolveReport:
    """Solve at a new anode radius (scale study for 3.5 MW)."""
    target = target_mw if target_mw is not None else base.scales.target_gross_power_mw
    geo = replace(base.geometry, r_anode_m=r_anode_m)
    return solve_for_target_power(replace(base, geometry=geo), target_mw=target)
