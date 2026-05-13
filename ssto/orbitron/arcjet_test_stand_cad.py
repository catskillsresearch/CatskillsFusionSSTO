"""
Arcjet / outdoor test-stand parts (used by YAML ``templates_registry``).

Standalone export: ``arcjet_outdoor_stand.gltf`` (+ sibling ``.bin``) under
``Aircraft/Orbitron-TestStand/build/`` by default (override with ``ORBITRON_ARCJET_GLTF``).
"""
from __future__ import annotations

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
    reactor_mount_z = 0.35 + 0.25 + 1.0
    noz = _horizontal_about_deck_y(nozzle_stub().translate((0, 0, reactor_mount_z + 0.85)), z_deck)
    det = _horizontal_about_deck_y(blast_detuner().translate((0, 0, reactor_mount_z + 1.15)), z_deck)
    sled = thrust_sled_frame().translate((0, 0, -0.12))
    left_rail = rail_beam().translate((0, 0.55, -0.06))
    right_rail = rail_beam().translate((0, -0.55, -0.06))

    assy = cq.Assembly(name="Arcjet_Outdoor_Test_Sled")
    assy.add(bell, name="Bellmouth", color=c_ti)
    assy.add(comp, name="Compressor_Can", color=c_ti)
    assy.add(noz, name="CD_Nozzle_Stub", color=c_ablative)
    assy.add(sled, name="Thrust_Sled_Frame", color=c_steel)
    assy.add(left_rail, name="Rail_Left", color=c_steel)
    assy.add(right_rail, name="Rail_Right", color=c_steel)
    assy.add(det, name="Blast_Detuner", color=c_steel)

    lc_positions = [(0.7, 0.35), (-0.7, 0.35), (0.7, -0.35), (-0.7, -0.35)]
    for i, (px, py) in enumerate(lc_positions):
        puck = load_cell_puck().translate((px, py, 0.09))
        assy.add(puck, name=f"LoadCell_{i}", color=c_sensor)

    return assy


if __name__ == "__main__":
    import os
    from pathlib import Path

    _repo = Path(__file__).resolve().parent.parent.parent
    _default = _repo / "Aircraft" / "Orbitron-TestStand" / "build" / "arcjet_outdoor_stand.gltf"
    out = Path(os.environ.get("ORBITRON_ARCJET_GLTF", _default))
    out.parent.mkdir(parents=True, exist_ok=True)
    build_assembly().save(str(out))
    print(f"Wrote {out}")
