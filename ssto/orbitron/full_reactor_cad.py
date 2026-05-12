import cadquery as cq

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

# ==========================================
# ASSEMBLE AND EXPORT — merged fusion + arcjet engine (single glTF)
# ==========================================
if __name__ == "__main__":
    import os

    from fusion_arcjet_engine_cad import save_fusion_arcjet_engine

    out = os.environ.get("ORBITRON_LAB_GLTF", "orbitron_lab_v5.gltf")
    save_fusion_arcjet_engine(out)
