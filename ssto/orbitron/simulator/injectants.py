"""p-¹¹B fueling: H₂ proton feed + solid elemental ¹¹B via UV laser ablation (Reply 9, 19)."""
from __future__ import annotations

from typing import Any


def normalize_injectants_cfg(inj: dict[str, Any]) -> dict[str, Any]:
    """
    Canonical injectant keys for chain_config / proof suite.

    Migrates legacy keys:
    - ``b2h6_sccm`` / ``b10h14_equiv_sccm`` → ``laser_ablation_hz`` proxy only
    - ``reservoir_temp_C`` ignored (solid ¹¹B, not heated decaborane)
    """
    out = dict(inj)
    if "laser_ablation_hz" not in out:
        if "b10h14_equiv_sccm" in out:
            out["laser_ablation_hz"] = max(1.0, float(out["b10h14_equiv_sccm"]) * 5.0)
        elif "b2h6_sccm" in out:
            out["laser_ablation_hz"] = max(1.0, float(out["b2h6_sccm"]) * 1.25)
    out.setdefault("laser_ablation_hz", 10.0)
    out.setdefault("h2_sccm", 80.0)
    out.setdefault("b11_target_index", 0)
    return out


def boron_atoms_per_pulse() -> float:
    """Schematic ¹¹B atoms delivered per laser pulse into the bore (tunable scale)."""
    return 1.0


def injectant_mixing_scale(h2_sccm: float, laser_ablation_hz: float) -> float:
    """
    0D proxy for H⁺ / B⁺ balance with solid **¹¹B** laser ablation.

    Peaks near H₂ sccm : laser_hz ≈ 8:1 (benchtop Phase 1 operating point).
    """
    if h2_sccm < 1.0 or laser_ablation_hz < 0.5:
        return 0.05
    ratio = h2_sccm / max(laser_ablation_hz, 0.1)
    optimal = 8.0
    return max(0.05, min(1.0, float(__import__("math").exp(-0.08 * (ratio - optimal) ** 2))))


def b11_laser_delivery_scale(
    *,
    laser_ablation_hz: float,
    reactor_armed: bool,
    vacuum_ok: bool = True,
    laser_armed: bool = True,
) -> float:
    """Laser ablation gate — requires vacuum interlock and explicit laser arm (Reply 19 §1.1–1.3)."""
    if not reactor_armed or not vacuum_ok or not laser_armed:
        return 0.0
    return max(0.05, min(1.0, laser_ablation_hz / 10.0))


def effective_b11_density_scale(laser_ablation_hz: float, mix: float, delivery: float) -> float:
    """Boron inventory proxy for fusion_pb11 (pulses/s × mix × delivery)."""
    return laser_ablation_hz * 0.02 * mix * delivery * boron_atoms_per_pulse()
