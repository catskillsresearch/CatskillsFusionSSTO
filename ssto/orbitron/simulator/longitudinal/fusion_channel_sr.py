"""
Longitudinal (s–r) fusion-channel particle model with laminar relaminarization.

Mimics the *intent* of Orbitron-class videos (e.g. Avalanche-style axial cross-sections showing
ring + clumps): here the cut is **along the bore** (s = axial, r = radius), not the transverse
end-on view.

Design mechanisms (``orbitron_avalanche_core.yaml``):
  - **Tangential NBI** at core ends → fuel injection along s
  - **Rotational shear relaminarization** + **PSP2/Jin cathode pulse** → break up clumps
  - Without the hack: low cross-field mixing → persistent localized blobs (bad)

This is a **validation-oriented** 2D transport sketch, not a full 3D PIC. It produces:
  - Heatmaps of fusion-relevant density n(s,r,t)
  - Local p-¹¹B reaction rate R(s,r) ∝ n_p n_B ⟨σv⟩
  - **Clump index** (p95/median) — must drop when laminar hack is ON
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ssto.orbitron.simulator.fusion_pb11 import (
    E_RXN_J,
    effective_ion_temperature_kev,
    evaluate_fusion_pb11,
    pb11_reactivity_m3_s,
)
from ssto.orbitron.simulator.longitudinal.focus import FocusDomain
from ssto.orbitron.simulator.injectants import injectant_mixing_scale
from ssto.orbitron.simulator.pad_startup import effective_operating_point, evaluate_pad_status
from ssto.orbitron.simulator.types import SimulatorInputs


@dataclass
class FusionChannelConfig:
    n_s: int = 160
    n_r: int = 72
    n_frames: int = 72
    total_time_s: float = 2.0e-3
    # Clump acceptable when laminar ON (lower = smoother, video-like ring)
    clump_index_pass_below: float = 2.8


@dataclass
class LaminarHackState:
    """Controls relaminarization strength (maps to pad + design)."""

    enabled: bool = True
    cathode_pulse: float = 0.6
    throttle: float = 0.0
    B_tesla: float = 2.0
    injectant_mix: float = 1.0
    # Diffusion boost from E×B shear + cathode pulse (1 = design ON, 0 = clumping case)
    mixing_gain: float = 1.0


@dataclass
class FusionChannelResult:
    s_m: np.ndarray
    r_m: np.ndarray
    time_s: np.ndarray
    # (nt, ns, nr)
    density: np.ndarray
    reaction_rate: np.ndarray
    fusion_power_density: np.ndarray
    clump_index: np.ndarray
    laminar: LaminarHackState
    integrated_fusion_power_mw: float
    clump_index_final: float
    clump_reduction_ratio: float  # off/on if baseline computed
    meta: dict


def laminar_hack_from_inputs(inputs: SimulatorInputs, *, force_off: bool = False) -> LaminarHackState:
    """Build laminar hack from pad + injectants + B field."""
    pad = evaluate_pad_status(inputs.pad)
    mix = injectant_mixing_scale(inputs.operating.h2_sccm, inputs.operating.laser_ablation_hz)
    pulse = pad.state.cathode_pulse if pad.reactor_armed else 0.0
    thr = pad.state.throttle if pad.reactor_armed else 0.0
    enabled = (not force_off) and pad.reactor_armed
    # Design: rotational shear ∝ B·pulse·throttle; high H₂:B mix aids laminarity
    gain = 0.0
    if enabled:
        gain = (
            0.35
            + 0.45 * pulse
            + 0.25 * thr
            + 0.15 * min(1.0, inputs.geometry.B_axial_tesla / 2.0)
            + 0.2 * mix
        )
    return LaminarHackState(
        enabled=enabled,
        cathode_pulse=pulse,
        throttle=thr,
        B_tesla=inputs.geometry.B_axial_tesla,
        injectant_mix=mix,
        mixing_gain=min(3.0, gain),
    )


def _clump_index(field: np.ndarray) -> float:
    """p95/median in active cells — high means clumpy (video red blob case)."""
    f = field.ravel()
    f = f[f > 1.0e-12]
    if f.size < 8:
        return 1.0
    med = float(np.median(f))
    p95 = float(np.percentile(f, 95))
    return p95 / max(med, 1.0e-12)


def _inject_end_blobs(
    n: np.ndarray,
    s: np.ndarray,
    r: np.ndarray,
    *,
    s_targets: tuple[float, float],
    amplitude: float,
    r_sigma: float,
    s_sigma: float,
    asymmetry: float = 0.0,
) -> None:
    """Tangential NBI-style end injection (localized in s and r)."""
    S, R = np.meshgrid(s, r, indexing="ij")
    for i, s0 in enumerate(s_targets):
        sign = 1.0 if i == 0 else -1.0
        off_r = asymmetry * sign * r_sigma * 0.6
        blob = amplitude * np.exp(
            -0.5 * ((S - s0) / s_sigma) ** 2 + ((R - off_r) / r_sigma) ** 2
        )
        n += blob


def run_fusion_channel_sr(
    domain: FocusDomain,
    inputs: SimulatorInputs,
    cfg: FusionChannelConfig | None = None,
    *,
    laminar: LaminarHackState | None = None,
    compare_without_hack: bool = True,
) -> FusionChannelResult:
    """
    Evolve n(s,r) with optional laminar mixing; return timelapse + fusion power integral.
    """
    cfg = cfg or FusionChannelConfig()
    laminar = laminar or laminar_hack_from_inputs(inputs)
    g = inputs.geometry
    pad = evaluate_pad_status(inputs.pad)

    s0, s1 = domain.s_min_m, domain.s_max_m
    r_a = domain.r_anode_m
    s = np.linspace(s0, s1, cfg.n_s)
    r = np.linspace(0.0, domain.r_max_m, cfg.n_r)
    ds = (s1 - s0) / max(cfg.n_s - 1, 1)
    dr = domain.r_max_m / max(cfg.n_r - 1, 1)
    dV = ds * dr * (2.0 * math.pi * np.maximum(r, dr * 0.5))

    nt = cfg.n_frames
    time_s = np.linspace(0.0, cfg.total_time_s, nt)
    dt = time_s[1] - time_s[0] if nt > 1 else cfg.total_time_s

    n_stack = np.zeros((nt, cfg.n_s, cfg.n_r), dtype=np.float64)
    R_stack = np.zeros_like(n_stack)
    P_stack = np.zeros_like(n_stack)
    clump_hist = np.zeros(nt, dtype=np.float64)

    # Base diffusion [m²/s] — small without hack → clumps
    D_base = 2.0e-4
    D_laminar = D_base * (1.0 + 12.0 * laminar.mixing_gain)
    D_eff = D_laminar if laminar.enabled else D_base * 0.08

    u_s = 120.0 * pad.compressor_effective * (0.3 + 0.7 * laminar.throttle)
    inject_amp = 1.0 * laminar.injectant_mix * (0.2 + 0.8 * laminar.throttle)
    if not pad.reactor_armed:
        inject_amp = 0.05 * pad.compressor_effective

    op, _ = effective_operating_point(inputs.operating, inputs.pad)
    fus = evaluate_fusion_pb11(
        r_anode_m=g.r_anode_m,
        length_m=g.length_m,
        V_cathode_v=g.V_cathode_v,
        throttle=laminar.throttle,
        cathode_pulse=laminar.cathode_pulse,
        h2_sccm=op.h2_sccm,
        laser_ablation_hz=op.laser_ablation_hz,
        fusion_reactivity_scale=inputs.unobtanium.fusion_reactivity_scale,
        pic_rho_e_norm=inputs.pic_rho_e_norm,
    )
    T_kev = fus.ion_temperature_kev
    sv = fus.sigma_v_m3_s
    n_tot = fus.n_proton_m3 + fus.n_boron_m3
    h_frac = fus.n_proton_m3 / max(n_tot, 1.0e-12)
    b_frac = fus.n_boron_m3 / max(n_tot, 1.0e-12)
    conf = fus.confinement_factor

    mask_2d = r[None, :] <= r_a
    n_seed = max(n_tot * 0.25, 1.0e14)
    n = np.full((cfg.n_s, cfg.n_r), n_seed, dtype=np.float64)
    R_ref = conf * (n_seed * h_frac) * (n_seed * b_frac) * sv
    P_ref_w = float(np.sum(R_ref * E_RXN_J * dV[None, :] * mask_2d))
    asym = 0.0 if laminar.enabled else 0.85

    for it, t in enumerate(time_s):
        pulse = min(1.0, t / (cfg.total_time_s * 0.25 + 1e-12))
        # End injectors (H⁺ / B⁺ opposed tangential beams → axial smear when laminar)
        inj = inject_amp * pulse * dt * n_seed * 0.08
        _inject_end_blobs(
            n,
            s,
            r,
            s_targets=(s0 + 0.06 * (s1 - s0), s1 - 0.06 * (s1 - s0)),
            amplitude=inj * h_frac,
            r_sigma=r_a * 0.35,
            s_sigma=0.08 * (s1 - s0),
            asymmetry=asym,
        )
        _inject_end_blobs(
            n,
            s,
            r,
            s_targets=(s0 + 0.08 * (s1 - s0), s1 - 0.08 * (s1 - s0)),
            amplitude=inj * b_frac * 0.9,
            r_sigma=r_a * 0.42,
            s_sigma=0.1 * (s1 - s0),
            asymmetry=-asym * 0.7,
        )
        # Clump seed mid-bore when hack OFF (diocotron-style blob)
        if not laminar.enabled and it > nt // 4:
            S, R = np.meshgrid(s, r, indexing="ij")
            smid = 0.5 * (s0 + s1)
            n += 2.2 * n_seed * pulse * np.exp(-0.5 * ((S - smid) / (0.12 * (s1 - s0))) ** 2)
            n += 1.5 * n_seed * pulse * np.exp(-0.5 * ((R - 0.35 * r_a) / (0.18 * r_a)) ** 2)

        # Radial diffusion (laminar hack = strong)
        n_pad = np.pad(n, ((1, 1), (0, 0)), mode="edge")
        lap_r = (n_pad[2:, :] - 2.0 * n_pad[1:-1, :] + n_pad[:-2, :]) / max(dr * dr, 1e-12)
        n += dt * D_eff * lap_r

        # Axial advection + laminar axial homogenization
        if cfg.n_s > 2:
            dn_ds = np.zeros_like(n)
            dn_ds[1:-1, :] = (n[2:, :] - n[:-2, :]) / (2.0 * ds)
            dn_ds[0, :] = (n[1, :] - n[0, :]) / ds
            dn_ds[-1, :] = (n[-1, :] - n[-2, :]) / ds
            n -= dt * u_s * dn_ds
            n += dt * (D_eff * 0.4) * lap_r  # extra smear when laminar

        n = np.clip(n, 1.0e9, None)
        mask_bore = r <= r_a
        n_plasma = np.where(mask_bore, n, n * 0.15)

        n_p = n_plasma * h_frac
        n_b = n_plasma * b_frac
        R_local = conf * n_p * n_b * sv
        P_local = R_local * E_RXN_J

        n_stack[it] = n_plasma
        R_stack[it] = R_local
        P_stack[it] = P_local
        clump_hist[it] = _clump_index(n_plasma[:, mask_bore])

    # Spatial integral (diagnostic); headline MW tracks Tier-3 0D p-¹¹B at this run point
    P_total = float(np.sum(P_stack[-1] * dV[None, :] * mask_2d))
    channel_ratio = P_total / max(P_ref_w, 1.0e-6)
    P_mw = fus.fusion_power_mw if pad.reactor_armed else P_total / 1.0e6

    clump_final = float(clump_hist[-1])
    clump_off = clump_final
    if compare_without_hack and laminar.enabled:
        off = run_fusion_channel_sr(
            domain,
            inputs,
            cfg,
            laminar=laminar_hack_from_inputs(inputs, force_off=True),
            compare_without_hack=False,
        )
        clump_off = off.clump_index_final
    reduction = clump_off / max(clump_final, 1.0e-6)

    return FusionChannelResult(
        s_m=s,
        r_m=r,
        time_s=time_s,
        density=n_stack,
        reaction_rate=R_stack,
        fusion_power_density=P_stack,
        clump_index=clump_hist,
        laminar=laminar,
        integrated_fusion_power_mw=P_mw,
        clump_index_final=clump_final,
        clump_reduction_ratio=reduction,
        meta={
            "model": "fusion_channel_sr",
            "D_eff_m2_s": D_eff,
            "u_s_m_s": u_s,
            "sigma_v_m3_s": sv,
            "T_ion_kev": T_kev,
            "fusion_pb11_power_mw": fus.fusion_power_mw,
            "channel_power_ratio": channel_ratio,
            "confinement_factor": conf,
            "laminar_enabled": laminar.enabled,
            "note": "Longitudinal s–r fusion channel; compare clump index with hack OFF in Validation.",
        },
    )


def fusion_channel_to_longitudinal_run(
    result: FusionChannelResult,
    domain: FocusDomain,
) -> object:
    """Adapt to ``LongitudinalRun`` for the timelapse GUI."""
    from ssto.orbitron.simulator.longitudinal.run import LongitudinalRun

    return LongitudinalRun(
        focus=domain.focus,
        domain=domain,
        time_s=result.time_s,
        primary=result.density,
        secondary=result.reaction_rate,
        axis_horizontal=result.s_m,
        axis_vertical=result.r_m,
        primary_label="Fusion fuel density n [m⁻³] (s–r)",
        secondary_label="p-¹¹B reaction rate R [m⁻³ s⁻¹]",
        horizontal_label="Axial s [m] (intake → nozzle)",
        vertical_label="Radius r [m]",
        meta={
            **result.meta,
            "clump_index_final": result.clump_index_final,
            "integrated_fusion_power_mw": result.integrated_fusion_power_mw,
            "clump_reduction_ratio": result.clump_reduction_ratio,
        },
    )
