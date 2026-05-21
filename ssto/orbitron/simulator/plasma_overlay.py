"""
Plasma / injector / fusion-event overlay on the Blender longitudinal device graphic.

Coarse 2D proxies for GUI timelapse — not PIC-grade. WarpX transverse PIC can replace
density structure when ``pic_rho_e_norm`` is available from a completed run.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from matplotlib.axes import Axes
from matplotlib import cm

from typing import TYPE_CHECKING

from ssto.orbitron.simulator.blender_layout import EngineLongitudinalLayout
from ssto.orbitron.simulator.pad_startup import PadStartupStatus
from ssto.orbitron.simulator.types import SteadyStateResult

if TYPE_CHECKING:
    from ssto.orbitron.simulator.pic_session import PicSession


@dataclass
class PlasmaViewState:
    """Time-varying view for live mode (seconds since ignite or sim start)."""

    time_s: float = 0.0
    phase: float = 0.0  # 0–1 orbitron-like bunching phase


def _core_grid(layout: EngineLongitudinalLayout, n_s: int = 80, n_r: int = 40):
    g = layout.geometry
    s0, s1 = layout.s_core0, layout.s_core1
    r_max = g.r_anode_m * 0.98
    s = np.linspace(s0, s1, n_s)
    r = np.linspace(-r_max, r_max, n_r)
    return s, r, np.meshgrid(s, r, indexing="xy")


def draw_plasma_overlay(
    ax: Axes,
    layout: EngineLongitudinalLayout,
    pad_status: PadStartupStatus,
    result: SteadyStateResult | None,
    view: PlasmaViewState,
    *,
    pic_rho_norm: float = float("nan"),
    pic_session: PicSession | None = None,
) -> None:
    """Draw density colormap, injectors, and fusion sparks on existing layout axes."""
    g = layout.geometry
    armed = pad_status.reactor_armed
    s0, s1 = layout.s_core0, layout.s_core1
    s_mid = layout.s_core_mid

    # --- Tangential injectors (NBI at core ends) ---
    inj_s = (s0 + 0.05, s1 - 0.05)
    for s_inj, color, label in (
        (inj_s[0], "#38bdf8", "H⁺"),
        (inj_s[1], "#fb923c", "B⁺"),
    ):
        ax.annotate(
            "",
            xy=(s_inj, g.r_anode_m * 0.55),
            xytext=(s_inj, g.r_anode_m * 0.92),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.8),
        )
        ax.text(s_inj, g.r_anode_m * 0.95, label, ha="center", fontsize=7, color=color)

    if not pad_status.state.bleed_air_open and not armed:
        ax.text(
            s_mid,
            0.0,
            "Bleed closed — no air / plasma path",
            ha="center",
            va="center",
            fontsize=9,
            color="#94a3b8",
            bbox=dict(boxstyle="round", facecolor="#1e293b", alpha=0.8),
        )
        return

    if not armed:
        # Pre-ignite: faint annulus airflow hint only
        ax.axvspan(s0, s1, ymin=0.0, ymax=g.r_anode_m * 0.15, color="#64748b", alpha=0.25)
        ax.text(
            s_mid,
            g.r_anode_m * 0.35,
            "Spin-up — ignite to arm fusion",
            ha="center",
            fontsize=8,
            color="#cbd5e1",
        )
        return

    # --- Plasma density blob (E×B orbitron proxy: hollow-ish core + azimuthal ripple) ---
    log10_n = result.log10_density if result else 9.0
    rho_norm = 1.0
    if math.isfinite(pic_rho_norm):
        rho_norm = max(0.1, min(3.0, pic_rho_norm))
    elif result:
        rho_norm = max(0.2, (log10_n - 8.0) / 4.0)

    s, r, S, R = _core_grid(layout)
    rs = np.abs(R)

    if pic_session is not None and pic_session.available:
        try:
            r_pic, rho_e_prof, rho_b_prof = pic_session.radial_profiles()
            rho_prof = rho_e_prof + 0.5 * rho_b_prof
            if rho_prof.max() > 0:
                rho_prof = rho_prof / rho_prof.max()
            field = np.interp(rs.ravel(), r_pic, rho_prof, left=0.0, right=0.0).reshape(rs.shape)
            along = 0.7 + 0.3 * np.sin(math.pi * (S - s0) / max(s1 - s0, 0.1))
            field = field * along * rho_norm
            field = np.clip(field, 0.0, None)
        except Exception:
            pic_session = None  # fall through to heuristic

    if pic_session is None or not pic_session.available:
        r_norm = rs / max(g.r_anode_m, 1e-6)
        ripple = 0.15 * math.sin(2.0 * math.pi * (view.phase + (S - s0) / max(s1 - s0, 0.1) * 3.0))
        hollow = np.exp(-3.5 * r_norm**2) * (0.35 + 0.65 * (1.0 - r_norm**1.5))
        along = 0.7 + 0.3 * np.sin(math.pi * (S - s0) / max(s1 - s0, 0.1))
        field = rho_norm * hollow * along * (1.0 + ripple)
        field = np.clip(field, 0.0, None)

    ax.pcolormesh(
        s,
        r,
        field,
        cmap=cm.magma,
        alpha=0.55,
        shading="auto",
        vmin=0.0,
        vmax=max(0.5, rho_norm * 1.2),
        zorder=5,
    )

    # --- Synthetic beam particles (tangential injectant mixing) ---
    rng = np.random.default_rng(int(view.phase * 1000) % 2**31)
    n_pts = int(40 + 80 * pad_status.state.throttle)
    s_pts = rng.uniform(s0 + 0.02, s1 - 0.02, n_pts)
    r_pts = rng.normal(0.0, g.r_anode_m * 0.35, n_pts)
    r_pts = np.clip(r_pts, -g.r_anode_m * 0.9, g.r_anode_m * 0.9)
    colors = np.where(s_pts < s_mid, "#38bdf8", "#fb923c")
    ax.scatter(s_pts, r_pts, s=6, c=colors, alpha=0.65, edgecolors="none", zorder=6)

    # --- Fusion events (³He production proxy): sparse sparks along bore ---
    n_fusion = int(8 + 24 * (result.gross_power_mw if result else 0.0) / 3.5)
    fs = rng.uniform(s0 + 0.1, s1 - 0.1, n_fusion)
    fr = rng.uniform(-g.r_cathode_m * 2, g.r_cathode_m * 2, n_fusion)
    ax.scatter(
        fs,
        fr,
        s=28,
        marker="*",
        c="#4ade80",
        alpha=0.75,
        edgecolors="#14532d",
        linewidths=0.3,
        zorder=7,
        label="fusion events",
    )

    pic_note = "  |  PIC overlay" if pic_session is not None and pic_session.available else ""
    ax.text(
        s_mid,
        -g.r_anode_m * 0.82,
        (
            f"plasma log₁₀ n ≈ {log10_n:.2f}  |  P ≈ {result.gross_power_mw:.2f} MW{pic_note}"
            if result
            else ""
        ),
        ha="center",
        fontsize=8,
        color="#e2e8f0",
        zorder=8,
    )
