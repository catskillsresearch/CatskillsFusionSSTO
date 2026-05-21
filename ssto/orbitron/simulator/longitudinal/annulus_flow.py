"""
2D axisymmetric annulus flow along duct length (s) — Sprint 2 level 3.

Coarse finite-volume style update for demonstration / GUI timelapse:
  - s: axial (−X intake at s≈0, +X nozzle at s≈L)
  - r: radius from centerline (0 = axis, r_anode = plasma bore, r_duct = outer wall)
  - Annulus r_anode < r < r_duct carries air; core r < r_anode is plasma placeholder T_core

Not CFD-grade; couples to ``evaluate_steady_state`` for mdot and wall heat.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.longitudinal.focus import FocusDomain
from ssto.orbitron.simulator.types import SimulatorInputs


@dataclass
class AnnulusFlowConfig:
    n_s: int = 120
    n_r: int = 48
    n_frames: int = 60
    total_time_s: float = 0.01
    rho_air: float = 1.2


@dataclass
class AnnulusFlowResult:
    s_m: np.ndarray
    r_m: np.ndarray
    time_s: np.ndarray
    # (nt, ns, nr)
    temperature_k: np.ndarray
    velocity_s_mps: np.ndarray
    density_kg_m3: np.ndarray
    pressure_pa: np.ndarray


def run_annulus_flow(
    domain: FocusDomain,
    inputs: SimulatorInputs,
    cfg: AnnulusFlowConfig | None = None,
) -> AnnulusFlowResult:
    cfg = cfg or AnnulusFlowConfig()
    pad_status = evaluate_pad_status(inputs.pad)
    steady = evaluate_steady_state(inputs)
    mdot = max(steady.mass_flow_kgps, 0.01)
    q_wall = steady.wall_heat_kw * 1000.0
    t_in = 300.0
    cp = 1005.0
    r_a = domain.r_anode_m
    r_d = domain.r_duct_m
    s0, s1 = domain.s_min_m, domain.s_max_m
    s = np.linspace(s0, s1, cfg.n_s)
    r = np.linspace(0.0, domain.r_max_m, cfg.n_r)
    ds = (s1 - s0) / max(cfg.n_s - 1, 1)
    annulus_area = math.pi * (r_d * r_d - r_a * r_a)
    u_in = mdot / (cfg.rho_air * max(annulus_area, 1e-6))

    nt = cfg.n_frames
    time_s = np.linspace(0.0, cfg.total_time_s, nt)
    T = np.zeros((nt, cfg.n_s, cfg.n_r), dtype=np.float64)
    us = np.zeros_like(T)
    rho = np.full_like(T, cfg.rho_air)
    p = np.zeros_like(T)

    bleed = pad_status.state.bleed_air_open
    armed = pad_status.reactor_armed
    comp_eff = pad_status.compressor_effective

    for it, t in enumerate(time_s):
        t_ramp = t / (cfg.total_time_s * 0.35 + 1e-12)
        spin = min(1.0, comp_eff * t_ramp) if bleed else 0.0
        if pad_status.state.starter_engage and not armed:
            spin = max(spin, min(1.0, 0.42 * t_ramp))
        ignite = 1.0 if armed and t > cfg.total_time_s * 0.4 else 0.0
        for i, si in enumerate(s):
            # Wall heating ramps in hot section (middle 60% of core length)
            core_mid = 0.5 * (s0 + s1)
            core_half = 0.3 * (s1 - s0)
            in_hot = abs(si - core_mid) < core_half
            q_local = q_wall * ignite * (1.0 if in_hot else 0.15)
            for j, rj in enumerate(r):
                if rj < r_a:
                    T[it, i, j] = t_in + 800.0 * ignite * spin
                    us[it, i, j] = 0.0
                else:
                    # Annulus: plug flow + radial mixing proxy
                    blend = (rj - r_a) / max(r_d - r_a, 1e-6)
                    T_wall = t_in + q_local / (mdot * cp + 1.0)
                    T[it, i, j] = t_in + spin * (T_wall - t_in) * (0.4 + 0.6 * blend)
                    us[it, i, j] = u_in * spin * (1.0 + 0.2 * (si - s0) / max(s1 - s0, 1e-6))
                p[it, i, j] = rho[it, i, j] * 287.0 * T[it, i, j]

    return AnnulusFlowResult(
        s_m=s,
        r_m=r,
        time_s=time_s,
        temperature_k=T,
        velocity_s_mps=us,
        density_kg_m3=rho,
        pressure_pa=p,
    )
