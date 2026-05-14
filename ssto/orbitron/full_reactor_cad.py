import cadquery as cq

# Shared pose for reactor stack instances in ``orbitron_lab.yaml`` (CadQuery → world).
_FUSION_STACK_TRANSFORMS: list[dict[str, object]] = [
    {"op": "translate", "xyz": [0.0, 0.0, 0.75]},
    {"op": "rotate_y_about_point", "pivot": [0.0, 0.0, 0.15], "angle_deg": 90.0},
]


def fusion_exhaust_outlet_ring(
    outer_r: float = 0.082,
    inner_r: float = 0.055,
    thickness: float = 0.016,
) -> cq.Workplane:
    """Thin annular flange at the anode / bay exhaust plane (coarse commissioning mesh)."""
    disc = cq.Workplane("XY").circle(outer_r).extrude(thickness)
    bore = cq.Workplane("XY").circle(inner_r).extrude(thickness + 0.01)
    return disc.cut(bore)


class IntegratedOrbitronTube:
    """The 3.5 MW p-B11 Reactor Core"""
    def build(self):
        r = 0.05
        h = 2.0
        anode = cq.Workplane("XY").cylinder(h, r).faces(">Z").workplane().hole(r*2 - 0.01)
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
        """HV umbilical: operator console → magnet shell top (schematic feed; sim logic is XML/Nasal)."""
        mag_ports = self.magnet_shell_connector_anchors()
        console_hv = (-1.22, -2.32, 1.22)
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
        # CHANGED: Jogged the HV line 0.45m to the right so it doesn't block the screen
        hv1 = cq.Workplane("XY").cylinder(0.6, 0.02).translate((0.45, -2.5, 1.6))  
        hv2 = cq.Workplane("XZ").cylinder(2.5, 0.02).translate((0.45, -1.25, 1.9)) 
        hv3 = cq.Workplane("YZ").cylinder(0.45, 0.02).translate((0.225, 0.0, 1.9)) # Jog to center
        hv4 = cq.Workplane("XY").cylinder(0.5, 0.02).translate((0.0, 0.0, 1.65))   # Drop down
        
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

        hv = hv1.union(hv2).union(hv3).union(hv4)
        gas = h2_1.union(h2_2).union(h2_3).union(h2_4).union(b2_1).union(b2_2).union(b2_3).union(b2_4)
        meth = ch4_1.union(ch4_2).union(ch4_3).union(ch4_4)
        
        return hv, gas, meth

if __name__ == "__main__":
    raise SystemExit(
        "Lab glTF is built only via Makefile: assembly YAML → tools/compile_assembly_yaml.py. "
        "This file supplies CadQuery templates for the YAML compiler."
    )
