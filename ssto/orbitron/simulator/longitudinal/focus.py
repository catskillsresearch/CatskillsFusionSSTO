"""
Focus levels for Sprint 2 longitudinal / cross-section views.

Physics note
------------
Orbitron fusion physics (E×B, orbitrap) is naturally simulated in the **transverse**
plane (radius × azimuth), with **B along the bore axis**. WarpX ``laminar_flow_2d_arcjet.py``
uses an (x, z) transverse slice (z along bore axis). The proof-suite lower panel projects
r = |x| for **cylindrical** axial-uniformity views; √(x²+z²) is not used (that wedge is wrong for a cylinder).

**Level 1 (fusion channel)** — **s–r** fusion fuel density + reaction rate with **laminar relaminarization**
hack (breaks clumps; video-style validation). See ``fusion_channel_sr.py``.

**Level 2–3** use transverse PIC timelapse (WarpX) cropped to the tube / magnet bore.

**Level 4** adds **s–r annulus air**: intake (−X) → hot core jacket → nozzle (+X).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ssto.orbitron.simulator.types import DeviceGeometry, SimulatorInputs


class LongitudinalFocus(str, Enum):
    """Zoom level — build innermost first, then pull back."""

    FUSION_CHANNEL_SR = "fusion_channel_sr"
    CORE_TUBE = "core_tube"
    CORE_PLUS_MAGNET = "core_plus_magnet"
    FULL_DUCT_AIR = "full_duct_air"


FOCUS_COMBO_ORDER: tuple[LongitudinalFocus, ...] = (
    LongitudinalFocus.FUSION_CHANNEL_SR,
    LongitudinalFocus.CORE_TUBE,
    LongitudinalFocus.CORE_PLUS_MAGNET,
    LongitudinalFocus.FULL_DUCT_AIR,
)


def resolve_longitudinal_focus(
    data: object | None,
    index: int = -1,
    *,
    default: LongitudinalFocus = LongitudinalFocus.FULL_DUCT_AIR,
) -> LongitudinalFocus:
    """Map QComboBox item data back to enum (Qt stores str Enum values as str)."""
    if isinstance(data, LongitudinalFocus):
        return data
    if isinstance(data, str):
        return LongitudinalFocus(data)
    if 0 <= index < len(FOCUS_COMBO_ORDER):
        return FOCUS_COMBO_ORDER[index]
    return default


@dataclass(frozen=True)
class FocusDomain:
    """Axisymmetric s–r bounds (s = axial, r = radius). Lab propulsion: −X intake → +X nozzle."""

    focus: LongitudinalFocus
    s_min_m: float
    s_max_m: float
    r_max_m: float
    r_anode_m: float
    r_cathode_m: float
    r_magnet_od_m: float
    r_duct_m: float
    label: str


def focus_domain(
    focus: LongitudinalFocus,
    inputs: SimulatorInputs,
    *,
    duct_length_m: float = 3.2,
    intake_length_m: float = 0.6,
    nozzle_length_m: float = 0.8,
) -> FocusDomain:
    """Build display / simulation bounds for a focus level."""
    from ssto.orbitron.simulator.blender_layout import engine_axial_layout

    g = inputs.geometry
    r_a = g.r_anode_m
    r_c = g.r_cathode_m
    r_mag = max(0.15, r_a * 2.2)
    r_duct = 0.18
    layout = engine_axial_layout(g, duct_length_m=duct_length_m)
    s_core0, s_core1 = layout.s_core0, layout.s_core1

    if focus == LongitudinalFocus.FUSION_CHANNEL_SR:
        return FocusDomain(
            focus=focus,
            s_min_m=s_core0,
            s_max_m=s_core1,
            r_max_m=r_a * 1.02,
            r_anode_m=r_a,
            r_cathode_m=r_c,
            r_magnet_od_m=r_mag,
            r_duct_m=r_duct,
            label="Fusion channel s–r (laminar hack + p-¹¹B reaction)",
        )
    if focus == LongitudinalFocus.CORE_TUBE:
        return FocusDomain(
            focus=focus,
            s_min_m=s_core0,
            s_max_m=s_core1,
            r_max_m=r_a * 1.05,
            r_anode_m=r_a,
            r_cathode_m=r_c,
            r_magnet_od_m=r_mag,
            r_duct_m=r_duct,
            label="Core tube (plasma transverse PIC + anode bore)",
        )
    if focus == LongitudinalFocus.CORE_PLUS_MAGNET:
        return FocusDomain(
            focus=focus,
            s_min_m=s_core0 - 0.1,
            s_max_m=s_core1 + 0.1,
            r_max_m=r_mag * 1.05,
            r_anode_m=r_a,
            r_cathode_m=r_c,
            r_magnet_od_m=r_mag,
            r_duct_m=r_duct,
            label="Core + magnet bore (PIC + HTS jacket outline)",
        )
    return FocusDomain(
        focus=focus,
        s_min_m=0.0,
        s_max_m=duct_length_m,
        r_max_m=r_duct * 1.08,
        r_anode_m=r_a,
        r_cathode_m=r_c,
        r_magnet_od_m=r_mag,
        r_duct_m=r_duct,
        label="Full duct — annulus air s–r (intake → nozzle)",
    )
