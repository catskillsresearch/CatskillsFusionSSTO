"""
Arcjet / outdoor test-stand **geometry builders** (used by ``tools/yaml_assembly/templates_registry``).

Lab layout and export are **only** via ``orbitron_lab.yaml`` → ``make orbitron-lab-gltf``; this module
does not write glTF on its own.
"""
from __future__ import annotations

import math

import cadquery as cq


def bellmouth_flare(inlet_r: float = 0.18, throat_r: float = 0.05, length: float = 0.35) -> cq.Workplane:
    """Single lofted frustum as a coarse bellmouth."""
    return cq.Workplane("XY").circle(inlet_r).workplane(offset=length).circle(throat_r).loft(combine=True)


def compressor_housing(od: float = 0.14, length: float = 0.25) -> cq.Workplane:
    """Simple motor/compressor can around the duct."""
    shell = cq.Workplane("XY").circle(od / 2).extrude(length)
    bore = cq.Workplane("XY").circle(od / 2 - 0.02).extrude(length + 0.01)
    return shell.cut(bore)


def bay_inlet_annulus_shroud(
    x0: float = -0.31,
    length: float = 0.175,
    outer_r: float = 0.149,
    inner_r: float = 0.088,
) -> cq.Workplane:
    """Hollow shell along +X bridging compressor housing and solenoid OD.

    Coarse stand-in for **compressor discharge into the reactor-bay annulus** (working
    air outside the niobium plasma boundary). Built in lab axes: bore clears the
    anode + inlet flange; OD matches the magnet shell radius band used in
    ``IntegratedOrbitronTube``.
    """
    shell = cq.Workplane("YZ").workplane(offset=x0).circle(outer_r).extrude(length)
    bore = cq.Workplane("YZ").workplane(offset=x0 - 0.001).circle(inner_r).extrude(length + 0.02)
    return shell.cut(bore)


def thrust_sled_frame(
    length: float = 2.2, width: float = 1.0, rail_h: float = 0.08
) -> cq.Workplane:
    """Open frame from long rails, short cross ties, and a thin deck."""
    long1 = cq.Workplane("XY").box(length, rail_h, rail_h).translate((0, width / 2, rail_h / 2))
    long2 = cq.Workplane("XY").box(length, rail_h, rail_h).translate((0, -width / 2, rail_h / 2))
    ties = long1.union(long2)
    z_tie = rail_h * 2
    for x in (-length / 2 + 0.25, 0.0, length / 2 - 0.25):
        tie = cq.Workplane("XY").box(width, rail_h, rail_h).translate((x, 0, z_tie))
        ties = ties.union(tie)
    deck = cq.Workplane("XY").box(length * 0.85, width * 0.75, 0.06).translate((0, 0, rail_h * 3))
    return ties.union(deck)


def rail_beam(span: float = 3.5) -> cq.Workplane:
    return cq.Workplane("XY").box(span, 0.12, 0.06).edges("|Z").fillet(0.015)


def load_cell_puck() -> cq.Workplane:
    return cq.Workplane("XY").cylinder(0.04, 0.06)


def blast_detuner(inner_r: float = 0.35, wall: float = 0.04, length: float = 4.0) -> cq.Workplane:
    outer = cq.Workplane("XY").circle(inner_r + wall).extrude(length)
    inner = cq.Workplane("XY").circle(inner_r).extrude(length + 0.01)
    return outer.cut(inner)


def nozzle_stub(throat_r: float = 0.045, exit_r: float = 0.09, length: float = 0.2) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(throat_r)
        .workplane(offset=length)
        .circle(exit_r)
        .loft(combine=True)
    )


def nozzle_inlet_plenum(
    inlet_r: float = 0.056, mid_r: float = 0.048, length: float = 0.07
) -> cq.Workplane:
    """Converging adapter / plenum stub ahead of the throat segment."""
    return cq.Workplane("XY").circle(inlet_r).workplane(offset=length).circle(mid_r).loft(combine=True)


def nozzle_cd_contour(r0: float = 0.048, throat_r: float = 0.045, length: float = 0.05) -> cq.Workplane:
    """Throat-forward CD segment (coarse stand-in for contoured wall)."""
    return cq.Workplane("XY").circle(r0).workplane(offset=length).circle(throat_r).loft(combine=True)


def nozzle_exit_hardware(throat_r: float = 0.045, exit_r: float = 0.09, length: float = 0.08) -> cq.Workplane:
    """Divergent section plus implicit exit plane / flange bosses (simplified)."""
    return cq.Workplane("XY").circle(throat_r).workplane(offset=length).circle(exit_r).loft(combine=True)


def bd_annulus_sleeve(
    inner_flow_r: float = 0.34,
    annulus_gap: float = 0.048,
    wall: float = 0.042,
    length: float = 0.75,
) -> cq.Workplane:
    """Outer annulus shell: gas in the gap between inner bore and outer duct wall."""
    outer_r = inner_flow_r + annulus_gap + wall
    shell = cq.Workplane("XY").circle(outer_r).extrude(length)
    bore = cq.Workplane("XY").circle(inner_flow_r + annulus_gap - 0.002).extrude(length + 0.02)
    return shell.cut(bore)


def bd_shock_core_insert(radius: float = 0.29, length: float = 0.9) -> cq.Workplane:
    """Central porous / insert volume represented as a short dense plug."""
    return cq.Workplane("XY").circle(radius).extrude(length)


def bd_bracket_seal_flange(
    outer_r: float = 0.42, inner_r: float = 0.33, thickness: float = 0.06, n_bolts: int = 8
) -> cq.Workplane:
    """Mounting flange with bolt bosses — load path + seal land to nozzle / duct."""
    disc = cq.Workplane("XY").circle(outer_r).extrude(thickness)
    hole = cq.Workplane("XY").circle(inner_r).extrude(thickness + 0.02)
    base = disc.cut(hole)
    bolt_circle_r = outer_r - 0.028
    bosses: cq.Workplane | None = None
    for i in range(n_bolts):
        ang = math.radians((360.0 / n_bolts) * i)
        x, y = bolt_circle_r * math.cos(ang), bolt_circle_r * math.sin(ang)
        b = cq.Workplane("XY").circle(0.012).extrude(thickness).translate((x, y, 0.0))
        bosses = b if bosses is None else bosses.union(b)
    return base if bosses is None else base.union(bosses)


def lab_fuel_feed_valve(body_r: float = 0.045, stem_r: float = 0.018, stem_h: float = 0.055) -> cq.Workplane:
    """Compact service valve / flex-jumper boss at a tank top (one mesh per species)."""
    base = cq.Workplane("XY").circle(body_r).extrude(0.04)
    stem = cq.Workplane("XY").circle(stem_r).extrude(stem_h).translate((0.0, 0.0, 0.04))
    return base.union(stem)

