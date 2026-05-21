"""Matplotlib views for the Orbitron simulator GUI."""
from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
    from ssto.orbitron.simulator.types import DeviceGeometry, SteadyStateResult


_DEVICE_TITLES = {
    "core_tube": "Core tube — anode bore + cathode (Blender-style)",
    "core_plus_magnet": "Core + magnet bore (Blender-style)",
    "full_duct_air": "Full engine — intake to nozzle (Blender-style)",
}


def render_device_cross_section(
    ax: Axes,
    geometry: DeviceGeometry,
    focus: LongitudinalFocus,
    *,
    pad_status=None,
    steady_result=None,
    plasma_view=None,
    pic_rho_norm: float = float("nan"),
    pic_session=None,
) -> None:
    """Draw Blender-style longitudinal layout on an existing axes."""
    from ssto.orbitron.simulator.blender_layout import draw_blender_underlay, engine_axial_layout
    from ssto.orbitron.simulator.plasma_overlay import PlasmaViewState, draw_plasma_overlay

    layout = engine_axial_layout(geometry)
    draw_blender_underlay(ax, layout, focus, symmetric=True)
    ax.set_title(_DEVICE_TITLES[focus.value])
    if pad_status is not None:
        draw_plasma_overlay(
            ax,
            layout,
            pad_status,
            steady_result,
            plasma_view or PlasmaViewState(),
            pic_rho_norm=pic_rho_norm,
            pic_session=pic_session,
        )
    if pic_session is not None and pic_session.available:
        r_p, z_p, rho = pic_session.transverse_slice()
        inset = ax.figure.add_axes([0.02, 0.08, 0.22, 0.35])
        inset.pcolormesh(r_p, z_p, rho, shading="auto", cmap="magma")
        inset.set_title("PIC transverse", fontsize=7, color="#e2e8f0")
        inset.set_aspect("equal")
    ax.annotate(
        f"{geometry.V_cathode_v / 1000:.0f} kV  |  B = {geometry.B_axial_tesla:.1f} T",
        xy=(0.02, 0.97),
        xycoords="axes fraction",
        fontsize=9,
        color="#e2e8f0",
        va="top",
    )


def device_cross_section_figure(
    geometry: DeviceGeometry,
    focus: LongitudinalFocus | None = None,
) -> Figure:
    """Longitudinal section (Blender-style) — intake −X (left) → nozzle +X (right)."""
    from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus as LF

    if focus is None:
        focus = LF.FULL_DUCT_AIR
    fig, ax = plt.subplots(figsize=(9.0, 4.2), dpi=100)
    render_device_cross_section(ax, geometry, focus)
    fig.tight_layout()
    return fig


def results_bar_figure(result: SteadyStateResult) -> Figure:
    """Summary bar chart of key outputs."""
    fig, ax = plt.subplots(figsize=(5.5, 3.5), dpi=100)
    labels = [
        "P_gross\n[MW]",
        "P_jet\n[MW]",
        "Q_wall\n[kW]",
        "I_beam\n[mA]",
        "Thrust\n[kN]",
        "ṁ\n[kg/s]",
    ]
    values = [
        result.gross_power_mw,
        result.jet_kinetic_power_mw,
        result.wall_heat_kw / 1000.0,
        result.beam_current_ma,
        result.thrust_lbf * 0.00444822,
        result.mass_flow_kgps,
    ]
    colors = ["#22c55e" if result.feasible else "#ef4444"] * len(labels)
    ax.bar(labels, values, color=colors, alpha=0.85)
    ax.set_title("Steady-state outputs" + (" ✓" if result.feasible else " — violations"))
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def power_sweep_figure(
    base_inputs: object,
    throttle_vals: np.ndarray | None = None,
) -> Figure:
    """Throttle sweep at fixed geometry / unobtanium."""
    from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
    from ssto.orbitron.simulator.types import SimulatorInputs

    assert isinstance(base_inputs, SimulatorInputs)
    if throttle_vals is None:
        throttle_vals = np.linspace(0.1, 1.0, 20)
    p_mw: list[float] = []
    q_kw: list[float] = []
    for tv in throttle_vals:
        from dataclasses import replace

        inp = replace(
            base_inputs,
            pad=replace(
                base_inputs.pad,
                pad_apu_online=True,
                bleed_air_open=True,
                startup_trigger=True,
                throttle=float(tv),
                compressor=max(base_inputs.pad.compressor, 0.5),
            ),
        )
        r = evaluate_steady_state(inp)
        p_mw.append(r.gross_power_mw)
        q_kw.append(r.wall_heat_kw)
    fig, ax1 = plt.subplots(figsize=(5.5, 3.5), dpi=100)
    ax2 = ax1.twinx()
    ax1.plot(throttle_vals, p_mw, "g-o", ms=4, label="P_gross [MW]")
    ax2.plot(throttle_vals, q_kw, "r-s", ms=4, label="Q_wall [kW]")
    ax1.axhline(base_inputs.scales.target_gross_power_mw, color="#666", ls="--", label="3.5 MW target")
    ax1.set_xlabel("Throttle")
    ax1.set_ylabel("Gross power [MW]", color="g")
    ax2.set_ylabel("Wall heat [kW]", color="r")
    ax1.set_title("Throttle sweep (0D model)")
    ax1.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
