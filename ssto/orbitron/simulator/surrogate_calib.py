"""
Calibration layer: map PIC proxies + controls to engineering scalars (``build_surrogate_map``).
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from ssto.orbitron.simulator.physics_spec import load_plant_scales, repo_root


@dataclass(frozen=True)
class SurrogateScalars:
    """Bilinear-style engineering outputs (thrust, mdot, power, heat)."""

    thrust_lbf: float
    mass_flow_kgps: float
    gross_power_mw: float
    wall_heat_kw: float
    rho_norm: float


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def yaml_scale_scalars(
    throttle: float,
    compressor: float,
    rho_norm: float = 1.0,
) -> SurrogateScalars:
    """Same closure as ``build_surrogate_map.scalar_outputs`` / ``surrogate_closure_check``."""
    sc = load_plant_scales()
    t = _clamp01(throttle)
    c = _clamp01(compressor)
    rn = max(0.15, min(3.0, rho_norm)) if math.isfinite(rho_norm) else 1.0
    return SurrogateScalars(
        thrust_lbf=sc.thrust_lbf_at_full * t * c * rn,
        mass_flow_kgps=sc.mass_flow_kgps_at_full * t * c * rn,
        gross_power_mw=sc.target_gross_power_mw * t * c * rn,
        wall_heat_kw=sc.heat_kw_at_full * t * c * rn,
        rho_norm=rn,
    )


def default_surrogate_csv() -> Path:
    return repo_root() / "build" / "orbitron" / "surrogate_sweep_results.csv"


def load_median_rho_norm(csv_path: Path | None = None) -> float:
    """Median ρ_e/ρ_ref from surrogate sweep CSV if present."""
    path = csv_path or default_surrogate_csv()
    if not path.is_file():
        return 1.0
    ratios: list[float] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rm = float(row.get("rho_mean", row.get("rho_e_mean", "nan")))
                rr = float(row.get("rho_ref", "1"))
                if math.isfinite(rm) and rr > 0:
                    ratios.append(rm / rr)
            except (TypeError, ValueError):
                continue
    if not ratios:
        return 1.0
    ratios.sort()
    return ratios[len(ratios) // 2]


def calibration_factor_from_csv(csv_path: Path | None = None) -> float:
    """
    Scale physics fusion power so full-command surrogate corner ≈ design MW.

    Returns multiplier applied to ``evaluate_fusion_pb11`` at reference knobs.
    """
    path = csv_path or default_surrogate_csv()
    if not path.is_file():
        return 1.0
    # Use row nearest T=C=1 if available
    best_rn = 1.0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t = float(row.get("throttle", 0))
                c = float(row.get("compressor", 0))
                if abs(t - 1.0) < 0.05 and abs(c - 1.0) < 0.05:
                    rm = float(row.get("rho_mean", "nan"))
                    rr = float(row.get("rho_ref", "1"))
                    if math.isfinite(rm) and rr > 0:
                        best_rn = rm / rr
            except (TypeError, ValueError):
                continue
    return max(0.15, min(3.0, best_rn))


def blended_gross_power_mw(
    fusion_physics_mw: float,
    surrogate_mw: float,
    *,
    physics_weight: float = 0.65,
    calibration_factor: float = 1.0,
) -> tuple[float, float, float]:
    """
    Blend physics p-¹¹B power with surrogate map power.

    Returns (gross_mw, P_physics_used, P_surrogate_used).
    """
    w = max(0.0, min(1.0, physics_weight))
    p_phys = max(0.0, fusion_physics_mw * calibration_factor)
    p_sur = max(0.0, surrogate_mw)
    gross = w * p_phys + (1.0 - w) * p_sur
    return gross, p_phys, p_sur
