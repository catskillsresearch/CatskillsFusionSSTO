"""
Blender-inspired longitudinal half-section (s–r) of the fusion_arcjet_engine.

Matches coarse lab CAD intent (``orbitron_lab.yaml`` / ``arcjet_test_stand_cad.py``):
  intake −X (left) → fusion core + magnet → turbine + nozzle +X (right).

Used as schematic underlay in the simulator GUI and timelapse views.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Polygon, Rectangle

from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
from ssto.orbitron.simulator.types import DeviceGeometry


class SegmentKind(str, Enum):
    BELLMOUTH = "bellmouth"
    COMPRESSOR = "compressor"
    REACTOR_INLET = "reactor_inlet_jacket"
    FUSION_CORE = "fusion_core"
    MAGNET_BORE = "magnet_bore"
    TURBINE = "turbine"
    NOZZLE = "nozzle"
    CATHODE = "cathode"
    PLASMA = "plasma_zone"
    INSULATOR = "insulator"
    NBI = "nbi_port"


# Blender-like palette (half-section view, r ≥ 0)
_COLORS = {
    SegmentKind.BELLMOUTH: "#9ca3af",
    SegmentKind.COMPRESSOR: "#6b7280",
    SegmentKind.REACTOR_INLET: "#64748b",
    SegmentKind.FUSION_CORE: "#3f3f46",
    SegmentKind.MAGNET_BORE: "#18181b",
    SegmentKind.TURBINE: "#71717a",
    SegmentKind.NOZZLE: "#a1a1aa",
    SegmentKind.CATHODE: "#ca8a04",
    SegmentKind.PLASMA: "#22c55e",
    SegmentKind.INSULATOR: "#7dd3fc",
    SegmentKind.NBI: "#c2763a",
}


@dataclass(frozen=True)
class AxialSegment:
    kind: SegmentKind
    s0: float
    s1: float
    r_inner: float
    r_outer: float
    label: str = ""


@dataclass(frozen=True)
class EngineLongitudinalLayout:
    """Full engine extent along propulsion axis (s)."""

    s_intake: float
    s_nozzle: float
    s_core_mid: float
    s_core0: float
    s_core1: float
    segments: tuple[AxialSegment, ...]
    geometry: DeviceGeometry

    @property
    def total_length_m(self) -> float:
        return self.s_nozzle - self.s_intake

    @property
    def duct_length_m(self) -> float:
        return self.total_length_m


def engine_axial_layout(
    geometry: DeviceGeometry,
    *,
    duct_length_m: float = 3.2,
    bellmouth_len: float = 0.35,
    compressor_len: float = 0.25,
    inlet_jacket_len: float = 0.175,
    turbine_len: float = 0.18,
    nozzle_len: float = 0.45,
) -> EngineLongitudinalLayout:
    """Piecewise constant radii along s (intake at s=0, nozzle at s=duct_length)."""
    g = geometry
    r_a = g.r_anode_m
    r_c = g.r_cathode_m
    r_mag = max(0.15, r_a * 2.2)
    r_duct = 0.18
    r_comp = 0.07
    core_len = max(g.length_m, 0.5)

    s0 = 0.0
    s_bell = s0 + bellmouth_len
    s_comp = s_bell + compressor_len
    s_inlet = s_comp + inlet_jacket_len
    s_core0 = s_inlet
    s_core1 = s_core0 + core_len
    s_turb = s_core1 + turbine_len
    s_end = duct_length_m
    nozzle_len = max(0.08, s_end - s_turb)

    segs: list[AxialSegment] = [
        AxialSegment(SegmentKind.BELLMOUTH, s0, s_bell, 0.0, r_duct, "Bellmouth"),
        AxialSegment(SegmentKind.COMPRESSOR, s_bell, s_comp, 0.0, r_comp, "Compressor"),
        AxialSegment(SegmentKind.REACTOR_INLET, s_comp, s_inlet, r_a, r_mag, "Annulus jacket"),
        AxialSegment(SegmentKind.MAGNET_BORE, s_core0, s_core1, 0.0, r_mag, "Magnet"),
        AxialSegment(SegmentKind.FUSION_CORE, s_core0, s_core1, 0.0, r_a, "Anode bore"),
        AxialSegment(SegmentKind.TURBINE, s_core1, s_turb, 0.0, 0.08, "Turbine"),
        AxialSegment(SegmentKind.NOZZLE, s_turb, s_end, 0.0, r_duct, "CD nozzle"),
    ]
    return EngineLongitudinalLayout(
        s_intake=s0,
        s_nozzle=s_end,
        s_core_mid=0.5 * (s_core0 + s_core1),
        s_core0=s_core0,
        s_core1=s_core1,
        segments=tuple(segs),
        geometry=g,
    )


def _mirror_patch_y(ax: Axes, patch) -> None:
    """Duplicate a patch across the centerline (r → −r) for symmetric section view."""
    import copy

    from matplotlib.transforms import Affine2D

    trans = Affine2D().scale(1.0, -1.0) + ax.transData
    twin = copy.copy(patch)
    twin.set_transform(trans)
    ax.add_patch(twin)


def draw_blender_underlay(
    ax: Axes,
    layout: EngineLongitudinalLayout,
    focus: LongitudinalFocus,
    *,
    show_centerline: bool = True,
    symmetric: bool = True,
) -> None:
    """Draw longitudinal section (r ≥ 0; optional mirror for Blender-style full cut)."""
    g = layout.geometry
    r_mag = max(0.15, g.r_anode_m * 2.2)
    r_duct = 0.18

    if focus == LongitudinalFocus.CORE_TUBE:
        s_lo = layout.s_core0 - 0.05
        s_hi = layout.s_core1 + 0.05
        r_hi = g.r_anode_m * 1.15
    elif focus == LongitudinalFocus.CORE_PLUS_MAGNET:
        s_lo = layout.s_core0 - 0.12
        s_hi = layout.s_core1 + 0.12
        r_hi = r_mag * 1.1
    else:
        s_lo, s_hi = layout.s_intake, layout.s_nozzle
        r_hi = r_duct * 1.12

    ax.set_facecolor("#2b2b2f")
    added: list = []

    for seg in layout.segments:
        if seg.s1 < s_lo or seg.s0 > s_hi:
            continue
        s0 = max(seg.s0, s_lo)
        s1 = min(seg.s1, s_hi)
        color = _COLORS.get(seg.kind, "#555")
        if seg.kind == SegmentKind.BELLMOUTH and focus == LongitudinalFocus.FULL_DUCT_AIR:
            # Conical flare (half)
            n = 12
            s_vals = np.linspace(s0, s1, n)
            r_vals = np.linspace(r_duct * 0.28, r_duct, n)
            poly = np.column_stack(
                [
                    np.concatenate([s_vals, s_vals[::-1]]),
                    np.concatenate([np.zeros(n), r_vals[::-1]]),
                ]
            )
            p = Polygon(poly, closed=True, facecolor=color, edgecolor="#cbd5e1", lw=0.8)
            ax.add_patch(p)
            added.append(p)
            continue
        if seg.kind in (SegmentKind.FUSION_CORE, SegmentKind.MAGNET_BORE):
            if focus == LongitudinalFocus.CORE_TUBE and seg.kind == SegmentKind.MAGNET_BORE:
                continue
            alpha = 0.95 if seg.kind == SegmentKind.MAGNET_BORE else 0.55
            p = Rectangle(
                (s0, 0.0),
                s1 - s0,
                min(seg.r_outer, r_hi),
                facecolor=color,
                edgecolor="#94a3b8",
                lw=0.6,
                alpha=alpha,
            )
            ax.add_patch(p)
            added.append(p)
            continue
        p = Rectangle(
            (s0, seg.r_inner),
            s1 - s0,
            min(seg.r_outer, r_hi) - seg.r_inner,
            facecolor=color,
            edgecolor="#94a3b8",
            lw=0.5,
            alpha=0.85,
        )
        ax.add_patch(p)
        added.append(p)

    if symmetric:
        for p in added:
            _mirror_patch_y(ax, p)

    # Cathode wire (gold centerline tube)
    if focus in (LongitudinalFocus.CORE_TUBE, LongitudinalFocus.CORE_PLUS_MAGNET):
        cs0 = layout.s_core_mid - g.length_m / 2
        cs1 = layout.s_core_mid + g.length_m / 2
        ax.plot([cs0, cs1], [g.r_cathode_m * 0.5, g.r_cathode_m * 0.5], color=_COLORS[SegmentKind.CATHODE], lw=3)
        ax.add_patch(
            Circle(
                (layout.s_core_mid, 0.0),
                g.r_cathode_m * 1.2,
                fill=False,
                ec="#7dd3fc",
                lw=1.2,
                ls="--",
            )
        )
        ax.add_patch(
            Circle(
                (layout.s_core_mid, 0.0),
                min(g.r_anode_m, r_hi) * 0.35,
                facecolor=_COLORS[SegmentKind.PLASMA],
                alpha=0.35,
                ec="none",
            )
        )
        # NBI ports (orange) at core ends
        for s_nb in (cs0 + 0.04, cs1 - 0.04):
            ax.add_patch(
                Rectangle(
                    (s_nb - 0.02, g.r_anode_m * 0.85),
                    0.04,
                    r_hi * 0.12,
                    facecolor=_COLORS[SegmentKind.NBI],
                    edgecolor="#78350f",
                    lw=0.5,
                )
            )

    if show_centerline:
        ax.axhline(0.0, color="#7dd3fc", lw=0.8, alpha=0.7)
    ax.set_xlim(s_lo, s_hi)
    if symmetric:
        ax.set_ylim(-r_hi, r_hi)
    else:
        ax.set_ylim(0.0, r_hi)
    ax.set_xlabel("Axial s [m]  (intake → nozzle)")
    ax.set_ylabel("Radius r [m]")
    ax.set_aspect("equal", adjustable="box")


def blender_longitudinal_figure(
    geometry: DeviceGeometry,
    focus: LongitudinalFocus = LongitudinalFocus.FULL_DUCT_AIR,
    *,
    symmetric: bool = True,
) -> Figure:
    """Standalone schematic matching Blender longitudinal cross-section."""
    layout = engine_axial_layout(geometry)
    fig, ax = plt.subplots(figsize=(9.0, 4.2), dpi=100)
    draw_blender_underlay(ax, layout, focus, symmetric=symmetric)
    titles = {
        LongitudinalFocus.CORE_TUBE: "Core tube — anode bore + cathode (Blender-style)",
        LongitudinalFocus.CORE_PLUS_MAGNET: "Core + magnet bore (Blender-style)",
        LongitudinalFocus.FULL_DUCT_AIR: "Full engine — intake to nozzle (Blender-style)",
    }
    ax.set_title(titles.get(focus, "Engine longitudinal section"))
    fig.tight_layout()
    return fig
