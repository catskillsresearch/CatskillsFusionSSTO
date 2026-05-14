"""
Arcjet / outdoor test-stand parts (used by YAML ``templates_registry``).

Standalone export: ``arcjet_outdoor_stand.gltf`` (+ sibling ``.bin``) under
``Aircraft/<aircraft.package_dir>/build/`` by default (override with ``ORBITRON_ARCJET_GLTF``).
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


def _horizontal_about_deck_y(solid: cq.Workplane, deck_z: float = 0.0, angle: float = 90.0) -> cq.Workplane:
    """Rotate duct geometry from vertical +Z stack to horizontal +X (pivot at deck bell foot)."""
    p = (0.0, 0.0, float(deck_z))
    return solid.rotate(p, (0.0, 1.0, float(deck_z)), float(angle))


def build_assembly() -> cq.Assembly:
    c_steel = cq.Color(0.35, 0.35, 0.38)
    c_ti = cq.Color(0.55, 0.58, 0.62)
    c_ablative = cq.Color(0.2, 0.2, 0.22)
    c_sensor = cq.Color(0.9, 0.75, 0.1)

    z_deck = 0.0
    bell = _horizontal_about_deck_y(bellmouth_flare(), z_deck)
    comp = _horizontal_about_deck_y(compressor_housing().translate((0, 0, 0.35)), z_deck)
    z_n = 2.75
    zd = 2.95
    noz1 = _horizontal_about_deck_y(nozzle_inlet_plenum().translate((0, 0, z_n)), z_deck)
    noz2 = _horizontal_about_deck_y(nozzle_cd_contour().translate((0, 0, z_n + 0.07)), z_deck)
    noz3 = _horizontal_about_deck_y(nozzle_exit_hardware().translate((0, 0, z_n + 0.07 + 0.05)), z_deck)
    d1 = _horizontal_about_deck_y(bd_annulus_sleeve().translate((0, 0, zd)), z_deck)
    d2 = _horizontal_about_deck_y(bd_shock_core_insert().translate((0, 0, zd + 0.2)), z_deck)
    d3 = _horizontal_about_deck_y(bd_bracket_seal_flange().translate((0, 0, zd + 1.88)), z_deck)
    sled = thrust_sled_frame().translate((0, 0, -0.12))
    left_rail = rail_beam().translate((0, 0.55, -0.06))
    right_rail = rail_beam().translate((0, -0.55, -0.06))

    assy = cq.Assembly(name="Arcjet_Outdoor_Test_Sled")
    assy.add(bell, name="Bellmouth", color=c_ti)
    assy.add(comp, name="Compressor_Can", color=c_ti)
    assy.add(noz1, name="Nozzle_Inlet_Plenum", color=c_ablative)
    assy.add(noz2, name="Nozzle_CD_Contour", color=c_ablative)
    assy.add(noz3, name="Nozzle_Exit_Hardware", color=c_ablative)
    assy.add(sled, name="Thrust_Sled_Frame", color=c_steel)
    assy.add(left_rail, name="Rail_Left", color=c_steel)
    assy.add(right_rail, name="Rail_Right", color=c_steel)
    assy.add(d1, name="BD_Annulus_Sleeve", color=c_steel)
    assy.add(d2, name="BD_Shock_Detuner_Core", color=c_steel)
    assy.add(d3, name="BD_Bracket_Seals", color=c_steel)

    lc_positions = [(0.7, 0.35), (-0.7, 0.35), (0.7, -0.35), (-0.7, -0.35)]
    for i, (px, py) in enumerate(lc_positions):
        puck = load_cell_puck().translate((px, py, 0.09))
        assy.add(puck, name=f"LoadCell_{i}", color=c_sensor)

    return assy


if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path

    _repo = Path(__file__).resolve().parent.parent.parent
    _tools = _repo / "tools"
    if str(_tools) not in sys.path:
        sys.path.insert(0, str(_tools))
    from orbitron_aircraft_pkg import aircraft_package_dir  # noqa: E402

    _default = _repo / "Aircraft" / aircraft_package_dir(_repo) / "build" / "arcjet_outdoor_stand.gltf"
    out = Path(os.environ.get("ORBITRON_ARCJET_GLTF", _default))
    out.parent.mkdir(parents=True, exist_ok=True)
    build_assembly().save(str(out))
    print(f"Wrote {out}")
