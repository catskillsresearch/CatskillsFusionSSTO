"""
Fast synthetic transverse PIC frames when WarpX diags are not available.

Used for pad-synced Longitudinal 2D level 1–2 preview (not a physics substitute).
"""
from __future__ import annotations

import numpy as np

from ssto.orbitron.simulator.longitudinal.focus import FocusDomain
from ssto.orbitron.simulator.longitudinal.warpx_frames import PicFrameStack
from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.types import SimulatorInputs


def run_heuristic_pic_frames(
    domain: FocusDomain,
    inputs: SimulatorInputs,
    *,
    n_frames: int = 48,
    total_time_s: float = 0.01,
) -> PicFrameStack:
    """Orbitron-like hollow plasma + injectant beams vs pad state."""
    status = evaluate_pad_status(inputs.pad)
    g = inputs.geometry
    r_max = domain.r_max_m
    nr = 64
    nz = 64
    r_edges = np.linspace(0.0, r_max, nr + 1)
    r_centers = 0.5 * (r_edges[:-1] + r_edges[1:])
    z = np.linspace(-r_max, r_max, nz)
    time_s = np.linspace(0.0, total_time_s, n_frames)

    armed = status.reactor_armed
    spin = status.compressor_effective if status.state.bleed_air_open else 0.0
    throttle = status.state.throttle if armed else 0.0

    stacks_e: list[np.ndarray] = []
    stacks_b: list[np.ndarray] = []

    for it, t in enumerate(time_s):
        phase = (it / max(n_frames - 1, 1) + throttle * 0.2) % 1.0
        R, Z = np.meshgrid(r_centers, z, indexing="xy")
        r_norm = R / max(g.r_anode_m, 1e-6)
        ripple = 1.0 + 0.2 * np.sin(2 * np.pi * (phase + Z / max(r_max, 0.01) * 2.0))
        hollow = np.exp(-3.0 * r_norm**2) * (0.3 + 0.7 * (1.0 - np.clip(r_norm, 0, 1) ** 1.2))
        amp = spin * (0.15 + 0.85 * throttle) if armed else spin * 0.08
        re = amp * hollow * ripple
        # Injectant beams at ±z band
        beam_z = 0.012 * g.r_anode_m
        h_beam = amp * throttle * np.exp(-((Z - beam_z) ** 2) / (2 * (0.15 * g.r_anode_m) ** 2))
        h_beam += amp * throttle * np.exp(-((Z + beam_z) ** 2) / (2 * (0.15 * g.r_anode_m) ** 2))
        b_beam = amp * throttle * 0.7 * np.exp(-(Z**2) / (2 * (0.2 * g.r_anode_m) ** 2)) * (R / max(g.r_anode_m, 1e-6))
        stacks_e.append(re)
        stacks_b.append(h_beam + b_beam)

    rho_e = np.stack(stacks_e, axis=0)
    rho_b = np.stack(stacks_b, axis=0)
    return PicFrameStack(
        time_s=time_s,
        r_m=r_centers,
        z_m=z,
        rho_e=rho_e,
        rho_beam=rho_b,
        meta={"model": "heuristic_pic", "armed": armed, "compressor_effective": spin},
    )
