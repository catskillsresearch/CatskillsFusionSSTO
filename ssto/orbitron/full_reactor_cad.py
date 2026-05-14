import math
from typing import Any

import cadquery as cq

# Shared pose for reactor stack instances in ``orbitron_lab.yaml`` (CadQuery → world).
_FUSION_STACK_TRANSFORMS: list[dict[str, object]] = [
    {"op": "translate", "xyz": [0.0, 0.0, 0.75]},
    {"op": "rotate_y_about_point", "pivot": [0.0, 0.0, 0.15], "angle_deg": 90.0},
]


def _hv_seg_along_x(y: float, z: float, x0: float, x1: float, radius: float = 0.02) -> cq.Workplane:
    lo, hi = (x0, x1) if x0 < x1 else (x1, x0)
    length = hi - lo
    if length < 1e-4:
        return cq.Workplane("XY")
    cx = (lo + hi) * 0.5
    return cq.Workplane("YZ").cylinder(length, radius).translate((cx, y, z))


def _hv_seg_along_y(x: float, z: float, y0: float, y1: float, radius: float = 0.02) -> cq.Workplane:
    lo, hi = (y0, y1) if y0 < y1 else (y1, y0)
    length = hi - lo
    if length < 1e-4:
        return cq.Workplane("XY")
    cy = (lo + hi) * 0.5
    return cq.Workplane("XZ").cylinder(length, radius).translate((x, cy, z))


def _hv_seg_along_z(x: float, y: float, z0: float, z1: float, radius: float = 0.02) -> cq.Workplane:
    lo, hi = (z0, z1) if z0 < z1 else (z1, z0)
    length = hi - lo
    if length < 1e-4:
        return cq.Workplane("XY")
    cz = (lo + hi) * 0.5
    return cq.Workplane("XY").cylinder(length, radius).translate((x, y, cz))


def fusion_exhaust_outlet_ring(
    outer_r: float = 0.082,
    inner_r: float = 0.055,
    thickness: float = 0.016,
) -> cq.Workplane:
    """Thin annular flange at the anode / bay exhaust plane (coarse commissioning mesh)."""
    disc = cq.Workplane("XY").circle(outer_r).extrude(thickness)
    bore = cq.Workplane("XY").circle(inner_r).extrude(thickness + 0.01)
    return disc.cut(bore)


def orbitron_anode_pressure_shell(r: float = 0.05, h: float = 2.0) -> cq.Workplane:
    """Thin-wall niobium shell with **asymmetric ends**: −Z = compressor / inlet clamp flange

    (+Z = exhaust boss toward ``fusion_exhaust_outlet_ring``), plus shallow OD jacket rings.

    Local **+Z** is the hot-gas outlet end after ``orbitron_lab.yaml`` fusion-stack rotation.
    """
    inner_r = r - 0.005  # legacy bore: hole diameter ``r*2 - 0.01``
    z_lo = -h * 0.5
    z_hi = h * 0.5

    outer = cq.Workplane("XY").cylinder(h, r)
    inner_bore = cq.Workplane("XY").cylinder(h + 0.08, inner_r)
    tube = outer.cut(inner_bore)

    # Inlet (−Z): wide bolted flange (reads as turbofan / duct mate, not a hose barb).
    flange_od = 0.10
    flange_t = 0.026
    bolt_circle_r = 0.068
    bolt_d = 0.011
    flange = cq.Workplane("XY").workplane(offset=z_lo - flange_t).circle(flange_od * 0.5).extrude(flange_t)
    flange = flange.faces(">Z").workplane().circle(inner_r + 0.0005).cutThruAll()

    bolts: cq.Workplane | None = None
    for k in range(6):
        ang = (math.tau / 6.0) * k
        bx, by = bolt_circle_r * math.cos(ang), bolt_circle_r * math.sin(ang)
        seg = (
            cq.Workplane("XY")
            .transformed(offset=(bx, by, z_lo - flange_t * 0.5))
            .circle(bolt_d * 0.5)
            .extrude(flange_t + 0.04)
        )
        bolts = seg if bolts is None else bolts.union(seg)
    flange = flange.cut(bolts)

    # Outlet (+Z): shorter, heavier lip (exhaust hardware narrative).
    boss_r = 0.075
    boss_t = 0.024
    boss = cq.Workplane("XY").workplane(offset=z_hi).circle(boss_r).extrude(boss_t)
    boss = boss.faces(">Z").workplane().circle(inner_r + 0.0005).cutThruAll()

    tube = tube.union(flange).union(boss)

    def _od_ring(zc: float, dro: float, rz: float) -> cq.Workplane:
        ro = r + dro
        ring_o = cq.Workplane("XY").transformed(offset=(0, 0, zc - rz * 0.5)).circle(ro).extrude(rz)
        ring_i = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, zc - rz * 0.5 - 0.001))
            .circle(r - 0.001)
            .extrude(rz + 0.002)
        )
        return ring_o.cut(ring_i)

    for i in range(5):
        zc = z_lo + 0.32 + i * 0.34
        if zc > z_hi - 0.18:
            break
        tube = tube.union(_od_ring(zc, 0.0045, 0.014))

    return tube


class IntegratedOrbitronTube:
    """The 3.5 MW p-B11 Reactor Core"""
    def build(self):
        r = 0.05
        h = 2.0
        anode = orbitron_anode_pressure_shell(r=r, h=h)
        dec = cq.Workplane("XY").cylinder(h, r-0.005).faces(">Z").workplane().hole((r-0.005)*2 - 0.002)
        cathode = cq.Workplane("XY").cylinder(h + 0.6, 0.005)
        
        ins = cq.Workplane("XY").cylinder(0.3, 0.03)
        for i in range(5):
            ins = ins.union(cq.Workplane("XY").workplane(offset=-0.1 + i*0.05).cylinder(0.02, 0.045))
        ins_top = ins.translate((0, 0, h/2 + 0.15))
        ins_bot = ins.translate((0, 0, -h/2 - 0.15))
        
        mag = cq.Workplane("XY").cylinder(h-0.5, 0.15).faces(">Z").workplane().hole(r*2 + 0.01)
        
        # NBI sticks out of the side
        nbi = cq.Workplane("XZ").cylinder(0.2, 0.04).translate((0, 0.1, 0))
        nbi_flange = cq.Workplane("XZ").cylinder(0.05, 0.06).translate((0, 0.2, 0))
        
        return anode, dec, cathode, ins_top.union(ins_bot), mag, nbi.union(nbi_flange)

class LabInfrastructure:
    """The Test Facility (Rigid Pipes + Decals)"""

    @staticmethod
    def fusion_stack_transforms() -> list[dict[str, object]]:
        return list(_FUSION_STACK_TRANSFORMS)

    def _magnet_world_bbox(self):
        """Axis-aligned bbox of the solenoid ``Magnet`` solid after the fusion stack pose."""
        from yaml_assembly.transform_ops import apply_transform_chain

        *_, mag, _ = IntegratedOrbitronTube().build()
        mag_w = apply_transform_chain(mag, _FUSION_STACK_TRANSFORMS)
        return mag_w.val().BoundingBox()

    def magnet_shell_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """Service points on the **magnet** shell (reference lab art: HV on top, fuel on farm side).

        Tanks sit at +Y; the magnet’s +Y-facing surface is used for three separated process
        gas inlets. HV terminates above the core; cryo CH₄ uses a high-Z / −X “rim” tap.
        """
        bb = self._magnet_world_bbox()
        cx = (bb.xmin + bb.xmax) * 0.5
        cy = (bb.ymin + bb.ymax) * 0.5
        cz = (bb.zmin + bb.zmax) * 0.5
        skin = 0.018
        y_farm = bb.ymax + skin
        z_top = bb.zmax + skin
        # Spread along +X with the H₂ tank (decks +Y): right-ish, center, left-ish for CH₄ dewar.
        return {
            "reactor_magnet_fuel_h2_in": (cx + 0.24, y_farm, cz + 0.06),
            "reactor_magnet_fuel_b2h6_in": (cx + 0.02, y_farm, cz + 0.02),
            "reactor_magnet_fuel_ch4_in": (cx - 0.26, y_farm, cz - 0.02),
            "reactor_magnet_hv_feed": (cx, cy, z_top),
            "reactor_magnet_cryo_ch4_tap": (bb.xmin + 0.22, cy - 0.06, z_top),
        }

    def build_table(self):
        legs = (cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((0.6, 0.3, 0.5))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((-0.6, 0.3, 0.5)))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((0.6, -0.3, 0.5)))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((-0.6, -0.3, 0.5))))
        top = cq.Workplane("XY").box(1.5, 0.8, 0.05).translate((0, 0, 1.0))
        mounts = (cq.Workplane("XY").box(0.1, 0.2, 0.25).translate((0.5, 0, 1.125))
                  .union(cq.Workplane("XY").box(0.1, 0.2, 0.25).translate((-0.5, 0, 1.125))))
        
        label = cq.Workplane("XZ").text("ORBITRON p-B11", 0.08, 0.001).translate((0, -0.401, 1.025))
        return legs.union(top).union(mounts), label

    def build_console(self):
        # CHANGED: We now return the desk, screen, and button as SEPARATE parts!
        base = cq.Workplane("XY").box(0.8, 0.8, 1.2).translate((0, -2.5, 0.6))
        panel = cq.Workplane("XY").box(0.8, 0.6, 0.05).rotate((1,0,0), (0,0,0), -30).translate((0, -2.6, 1.3))
        batt = cq.Workplane("XY").box(0.7, 0.6, 0.4).translate((0, -2.5, 0.2))
        desk = base.union(panel).union(batt)
        
        screen = cq.Workplane("XY").box(0.7, 0.05, 0.5).translate((0, -2.2, 1.6))
        brb = cq.Workplane("XY").cylinder(0.04, 0.05).rotate((1,0,0),(0,0,0),-30).translate((0.2, -2.65, 1.35))
        
        return desk, screen, brb

    def build_fuel_farm(self):
        h2 = cq.Workplane("XY").circle(0.15).extrude(1.2).edges(">Z").fillet(0.1).translate((0.6, 1.2, 0))
        b2h6 = cq.Workplane("XY").circle(0.15).extrude(1.2).edges(">Z").fillet(0.1).translate((0.0, 1.2, 0))
        dewar = cq.Workplane("XY").circle(0.25).extrude(0.9).edges(">Z").fillet(0.1).translate((-0.7, 1.2, 0))
        
        txt_h2 = cq.Workplane("XZ").text("HYDROGEN", 0.05, 0.001).translate((0.6, 1.049, 0.8))
        txt_b2 = cq.Workplane("XZ").text("DIBORANE", 0.05, 0.001).translate((0.0, 1.049, 0.8))
        txt_ch4 = cq.Workplane("XZ").text("LIQUID METHANE", 0.05, 0.001).translate((-0.7, 0.949, 0.45))
        
        return h2, b2h6, dewar, txt_h2, txt_b2, txt_ch4

    def fuel_line_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """World-space points for fuel routing (tank tops + magnet-shell inlets).

        Tank tops match ``build_fuel_farm()``. Reactor-side points sit on the solenoid
        ``Magnet`` bbox after the same ``transform_chain`` as the fusion reactor instances in ``orbitron_lab.yaml``,
        on the +Y farm-facing shell with X spread so the three services stay distinct.
        """
        z_trim = 0.035
        h2_top = (0.6, 1.2, 1.2 - z_trim)
        b2_top = (0.0, 1.2, 1.2 - z_trim)
        ch4_top = (-0.7, 1.2, 0.9 - z_trim)

        mag_ports = self.magnet_shell_connector_anchors()
        return {
            "fuel_farm_h2_tank_top": h2_top,
            "fuel_farm_b2h6_tank_top": b2_top,
            "fuel_farm_ch4_dewar_top": ch4_top,
            "reactor_fuel_h2_in": mag_ports["reactor_magnet_fuel_h2_in"],
            "reactor_fuel_b2h6_in": mag_ports["reactor_magnet_fuel_b2h6_in"],
            "reactor_fuel_ch4_in": mag_ports["reactor_magnet_fuel_ch4_in"],
        }

    def hv_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """HV umbilical: operator console → magnet shell top (schematic feed; sim logic is XML/Nasal).

        ``console_hv_header`` is placed on the **shifted** console cluster (same basis as
        ``orbitron_lab.yaml`` instance translate for ``Operator_Console``): desk local
        centre (~0, -2.5, 0.6) plus stand offset (-1.4, -2.3, 0) → breakout toward +X / +Y
        toward the reactor.
        """
        mag_ports = self.magnet_shell_connector_anchors()
        # Operator_Console transform_chain in orbitron_lab.yaml: translate(-1.4, -2.3, 0)
        # Desk base local centre (build_console): (0, -2.5, 0.6) → world ~(-1.4, -4.8, 0.6).
        console_hv = (-1.05, -4.45, 1.28)
        return {
            "console_hv_header": console_hv,
            "reactor_magnet_hv_feed": mag_ports["reactor_magnet_hv_feed"],
        }

    def cryo_methane_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """Cryostat / CH₄ fill path: dewar roof → magnet high-side tap (reference lab layout)."""
        z_trim = 0.035
        dewar_top = (-0.7, 1.2, 0.9 - z_trim)
        mag_ports = self.magnet_shell_connector_anchors()
        return {
            "cryo_ch4_dewar_out": dewar_top,
            "reactor_magnet_cryo_ch4_tap": mag_ports["reactor_magnet_cryo_ch4_tap"],
        }

    def build_rigid_plumbing(self):
        """HV umbilical: hardwired path from ``console_hv_header`` to ``reactor_magnet_hv_feed``."""
        anchors = self.hv_connector_anchors()
        sx, sy, sz = anchors["console_hv_header"]
        ex, ey, ez = anchors["reactor_magnet_hv_feed"]
        rr = 0.02
        # Axis-aligned polyline: leave console cluster (+X), jog toward reactor (+Y),
        # run forward (+X), adjust Z, then descend to magnet crown feed.
        hv = _hv_seg_along_x(sy, sz, sx, -0.22, rr)
        hv = hv.union(_hv_seg_along_y(-0.22, sz, sy, -0.42, rr))
        hv = hv.union(_hv_seg_along_x(-0.42, sz, -0.22, 0.44, rr))
        hv = hv.union(_hv_seg_along_z(0.44, -0.42, sz, 1.18, rr))
        hv = hv.union(_hv_seg_along_y(0.44, 1.18, -0.42, 0.0, rr))
        hv = hv.union(_hv_seg_along_z(0.44, 0.0, 1.18, 0.62, rr))
        hv = hv.union(_hv_seg_along_x(0.0, 0.62, 0.44, ex, rr))
        hv = hv.union(_hv_seg_along_z(ex, ey, 0.62, ez, rr))

        h2_1 = cq.Workplane("XY").cylinder(0.4, 0.015).translate((0.6, 1.2, 1.4))  
        h2_2 = cq.Workplane("YZ").cylinder(0.5, 0.015).translate((0.35, 1.2, 1.6)) 
        h2_3 = cq.Workplane("XZ").cylinder(1.1, 0.015).translate((0.1, 0.65, 1.6)) 
        h2_4 = cq.Workplane("XY").cylinder(0.3, 0.015).translate((0.1, 0.1, 1.45)) 
        
        b2_1 = cq.Workplane("XY").cylinder(0.3, 0.015).translate((0.0, 1.2, 1.35))
        b2_2 = cq.Workplane("XZ").cylinder(1.1, 0.015).translate((0.0, 0.65, 1.5))
        b2_3 = cq.Workplane("YZ").cylinder(0.1, 0.015).translate((-0.05, 0.1, 1.5))
        b2_4 = cq.Workplane("XY").cylinder(0.2, 0.015).translate((-0.1, 0.1, 1.4))

        ch4_1 = cq.Workplane("XY").cylinder(0.5, 0.025).translate((-0.7, 1.2, 1.15))
        ch4_2 = cq.Workplane("XZ").cylinder(1.2, 0.025).translate((-0.7, 0.6, 1.4))
        ch4_3 = cq.Workplane("YZ").cylinder(0.65, 0.025).translate((-0.375, 0.0, 1.4))
        ch4_4 = cq.Workplane("XY").cylinder(0.15, 0.025).translate((-0.05, 0.0, 1.325))

        gas = h2_1.union(h2_2).union(h2_3).union(h2_4).union(b2_1).union(b2_2).union(b2_3).union(b2_4)
        meth = ch4_1.union(ch4_2).union(ch4_3).union(ch4_4)
        
        return hv, gas, meth


def lab_h2_injectant_trunk_params() -> dict[str, Any]:
    """Single-service connector spec for H₂ injectant (subset of former ``Fuel_Gas_Lines``)."""
    return {
        "include_port_markers": False,
        "connectivity_spec": {
            "physical_story": "Hydrogen NBI co-injectant trunk from H₂ cylinder to magnet farm inlet.",
            "links": [
                {
                    "link_id": "h2_service",
                    "service": "process_h2",
                    "from_region": "fuel_farm_h2_tank",
                    "to_region": "reactor_magnet_shell_farm_face",
                    "routing_intent": "arc_over_deck_then_h2_side_inlet",
                }
            ],
        },
        "connector_ports": [
            {
                "id": "tank_h2_out",
                "anchor": "fuel_farm_h2_tank_top",
                "offset": [0.0, 0.0, 0.0],
                "description": "H2 cylinder top centre (matches CadQuery fuel farm).",
            },
            {
                "id": "reactor_h2_in",
                "anchor": "reactor_fuel_h2_in",
                "offset": [0.0, 0.0, 0.0],
                "description": "Magnet +Y shell inlet on the H₂-ward side of the solenoid (spread in +X).",
            },
        ],
        "connector_links": [
            {
                "id": "h2_service",
                "service": "process_h2",
                "from_port": "tank_h2_out",
                "to_port": "reactor_h2_in",
                "radius": 0.02,
                "description": "Hydrogen — polyline clears the deck edge then meets the magnet back face.",
                "waypoints": [[0.62, 0.82, 0.98], [0.76, 0.36, 0.38]],
            }
        ],
    }


def lab_b2h6_injectant_trunk_params() -> dict[str, Any]:
    """Single-service connector spec for B₂H₆ injectant (subset of former ``Fuel_Gas_Lines``)."""
    return {
        "include_port_markers": False,
        "connectivity_spec": {
            "physical_story": "Diborane gaseous boron carrier trunk from B₂H₆ cylinder to magnet inlet.",
            "links": [
                {
                    "link_id": "b2h6_service",
                    "service": "diborane_nbi_boron_carrier",
                    "from_region": "fuel_farm_b2h6_tank",
                    "to_region": "reactor_magnet_shell_farm_face",
                    "routing_intent": "arc_over_deck_then_centre_inlet",
                }
            ],
        },
        "connector_ports": [
            {
                "id": "tank_b2h6_out",
                "anchor": "fuel_farm_b2h6_tank_top",
                "offset": [0.0, 0.0, 0.0],
                "description": "Diborane cylinder top centre.",
            },
            {
                "id": "reactor_b2h6_in",
                "anchor": "reactor_fuel_b2h6_in",
                "offset": [0.0, 0.0, 0.0],
                "description": "Magnet +Y shell inlet near tube centreline for the B₂H₆ / boron injectant leg.",
            },
        ],
        "connector_links": [
            {
                "id": "b2h6_service",
                "service": "diborane_nbi_boron_carrier",
                "from_port": "tank_b2h6_out",
                "to_port": "reactor_b2h6_in",
                "radius": 0.02,
                "description": "Diborane — gaseous boron carrier to NBI / injector manifold.",
                "waypoints": [[0.04, 0.82, 0.96], [0.38, 0.36, 0.32]],
            }
        ],
    }


if __name__ == "__main__":
    raise SystemExit(
        "Lab glTF is built only via Makefile: assembly YAML → tools/compile_assembly_yaml.py. "
        "This file supplies CadQuery templates for the YAML compiler."
    )
