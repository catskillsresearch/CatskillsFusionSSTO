"""
Single fusion + air-breathing arcjet engine assembly (one glTF unit).

Horizontal layout (ground test stand): sled deck stays in the XY plane; the duct
(bellmouth → compressor → Orbitron stack → nozzle → blast detuner) is rotated +90°
about deck Y through the bell foot so the flow axis is roughly +X (intake toward
-X, exhaust/detuner toward +X). Fuel farm, HV umbilical, and gas lines use
LabInfrastructure; the operator console is shifted farther from the stand center.

Exports lab glTF (default filename orbitron_lab_v5.gltf) for build_ac3d.py; path set via ORBITRON_LAB_GLTF or Makefile → Aircraft/.../build/.
"""
from __future__ import annotations

import cadquery as cq

from arcjet_test_stand_cad import (
    bellmouth_flare,
    blast_detuner,
    compressor_housing,
    load_cell_puck,
    nozzle_stub,
    rail_beam,
    thrust_sled_frame,
)
from full_reactor_cad import IntegratedOrbitronTube, LabInfrastructure

# --- Sled / deck (must match thrust_sled_frame + placement) ---
RAIL_H = 0.08
SLED_Z_OFFSET = -0.12  # drop frame slightly into pad
# thrust_sled_frame: deck center z = RAIL_H * 3, thickness 0.06
_DECK_CENTER_LOCAL = RAIL_H * 3
_DECK_HALF = 0.03
# World-space top of deck slab (bellmouth mounts here)
DECK_TOP_Z = SLED_Z_OFFSET + _DECK_CENTER_LOCAL + _DECK_HALF

# Engine stack (meters above deck top)
COMPRESSOR_Z0 = 0.35  # bellmouth length
COMPRESSOR_LENGTH = 0.25
REACTOR_ANODE_HEIGHT = 2.0
Z_REACTOR_BASE = COMPRESSOR_Z0 + COMPRESSOR_LENGTH  # 0.6 from bell base
NOZZLE_LENGTH = 0.2
DETUNER_LENGTH = 2.0

# Shift operator console / desk farther from engine centerline (-Y = “back”, -X = away from +X exhaust)
CONSOLE_OFFSET_M = (-1.4, -2.3, 0.0)


def _horizontal_about_deck_y(solid: cq.Workplane, deck_z: float, angle: float = 90.0) -> cq.Workplane:
    """Rotate duct geometry from vertical +Z stack to horizontal +X (pivot at deck bell foot)."""
    p = (0.0, 0.0, float(deck_z))
    p1 = (0.0, 1.0, float(deck_z))
    return solid.rotate(p, p1, float(angle))


def build_fusion_arcjet_engine_assembly() -> cq.Assembly:
    c_steel = cq.Color(0.35, 0.35, 0.38)
    c_ti = cq.Color(0.55, 0.58, 0.62)
    c_ablative = cq.Color(0.2, 0.2, 0.22)
    c_sensor = cq.Color(0.9, 0.75, 0.1)

    c_niobium = cq.Color(0.8, 0.8, 0.85)
    c_dec = cq.Color(0.8, 0.6, 0.1)
    c_cath = cq.Color(0.2, 0.8, 0.9)
    c_ceramic = cq.Color(0.9, 0.9, 0.9)
    c_magnet = cq.Color(0.2, 0.2, 0.2)
    c_nbi = cq.Color(0.3, 0.6, 0.4)

    c_h2 = cq.Color(0.8, 0.1, 0.1)
    c_b2h6 = cq.Color(0.1, 0.6, 0.2)
    c_dewar = cq.Color(0.7, 0.7, 0.8)
    c_hv = cq.Color(0.9, 0.4, 0.0)
    c_stencil_w = cq.Color(0.9, 0.9, 0.9)
    c_stencil_b = cq.Color(0.1, 0.1, 0.1)

    c_table = cq.Color(0.15, 0.15, 0.15)
    c_screen = cq.Color(0.05, 0.05, 0.05)
    c_red_btn = cq.Color(0.9, 0.0, 0.0)

    z0 = DECK_TOP_Z  # bell lower lip flush with deck

    assy = cq.Assembly(name="Fusion_Arcjet_Engine")

    bell = _horizontal_about_deck_y(bellmouth_flare().translate((0, 0, z0)), z0)
    comp = _horizontal_about_deck_y(
        compressor_housing().translate((0, 0, z0 + COMPRESSOR_Z0)), z0
    )
    assy.add(bell, name="Bellmouth_Inlet", color=c_ti)
    assy.add(comp, name="Compressor_Can", color=c_ti)

    tube = IntegratedOrbitronTube()
    anode, dec, cath, ins, mag, nbi = tube.build()
    zr = (0, 0, z0 + Z_REACTOR_BASE)
    assy.add(_horizontal_about_deck_y(anode.translate(zr), z0), name="Anode", color=c_niobium)
    assy.add(_horizontal_about_deck_y(dec.translate(zr), z0), name="DEC_Grid", color=c_dec)
    assy.add(_horizontal_about_deck_y(cath.translate(zr), z0), name="Cathode", color=c_cath)
    assy.add(_horizontal_about_deck_y(ins.translate(zr), z0), name="Insulators", color=c_ceramic)
    assy.add(_horizontal_about_deck_y(mag.translate(zr), z0), name="Magnet", color=c_magnet)
    assy.add(_horizontal_about_deck_y(nbi.translate(zr), z0), name="NBI_Injector", color=c_nbi)

    z_noz = z0 + Z_REACTOR_BASE + REACTOR_ANODE_HEIGHT
    noz = _horizontal_about_deck_y(
        nozzle_stub(length=NOZZLE_LENGTH).translate((0, 0, z_noz)), z0
    )
    assy.add(noz, name="CD_Nozzle_Stub", color=c_ablative)

    det = _horizontal_about_deck_y(
        blast_detuner(length=DETUNER_LENGTH).translate((0, 0, z_noz + NOZZLE_LENGTH)), z0
    )
    assy.add(det, name="Blast_Detuner", color=c_steel)

    sled = thrust_sled_frame().translate((0, 0, SLED_Z_OFFSET))
    rail_z = SLED_Z_OFFSET + 0.02
    left_rail = rail_beam().translate((0, 0.55, rail_z))
    right_rail = rail_beam().translate((0, -0.55, rail_z))
    assy.add(sled, name="Thrust_Sled_Frame", color=c_steel)
    assy.add(left_rail, name="Rail_Left", color=c_steel)
    assy.add(right_rail, name="Rail_Right", color=c_steel)

    infra = LabInfrastructure()
    h2, b2h6, dewar, t_h2, t_b2, t_ch4 = infra.build_fuel_farm()
    hv, gas, meth = infra.build_rigid_plumbing()
    assy.add(h2, name="Tank_Hydrogen", color=c_h2)
    assy.add(b2h6, name="Tank_Diborane", color=c_b2h6)
    assy.add(dewar, name="Tank_Cryo_Methane", color=c_dewar)
    assy.add(t_h2, name="Decal_H2", color=c_stencil_w)
    assy.add(t_b2, name="Decal_B2H6", color=c_stencil_w)
    assy.add(t_ch4, name="Decal_CH4", color=c_stencil_b)
    assy.add(hv, name="High_Voltage_Umbilical", color=c_hv)
    assy.add(gas, name="Fuel_Gas_Lines", color=cq.Color(0.2, 0.2, 0.2))
    assy.add(meth, name="Cryo_Methane_Piping", color=c_niobium)

    ox, oy, oz = CONSOLE_OFFSET_M
    desk, screen, brb = infra.build_console()
    assy.add(desk.translate((ox, oy, oz)), name="Operator_Console", color=c_table)
    assy.add(screen.translate((ox, oy, oz)), name="Screen", color=c_screen)
    assy.add(brb.translate((ox, oy, oz)), name="Big_Red_Button", color=c_red_btn)

    lc_z = DECK_TOP_Z + 0.02
    lc_positions = [(0.7, 0.35), (-0.7, 0.35), (0.7, -0.35), (-0.7, -0.35)]
    for i, (px, py) in enumerate(lc_positions):
        puck = load_cell_puck().translate((px, py, lc_z))
        assy.add(puck, name=f"LoadCell_{i}", color=c_sensor)

    return assy


def save_fusion_arcjet_engine(output_file: str = "orbitron_lab_v5.gltf") -> None:
    build_fusion_arcjet_engine_assembly().save(output_file)
    print(f"Fusion arcjet engine assembly saved to {output_file}")


if __name__ == "__main__":
    save_fusion_arcjet_engine()
