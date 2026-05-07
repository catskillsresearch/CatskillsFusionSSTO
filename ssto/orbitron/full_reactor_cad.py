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
        
        # 3D Placard Decal facing the operator (0.001 thick)
        label = cq.Workplane("XZ").text("ORBITRON p-B11", 0.08, 0.001).translate((0, -0.401, 1.025))
        return legs.union(top).union(mounts), label

    def build_console(self):
        # Console at Y = -2.5 (8 feet away from the reactor)
        base = cq.Workplane("XY").box(0.8, 0.8, 1.2).translate((0, -2.5, 0.6))
        panel = cq.Workplane("XY").box(0.8, 0.6, 0.05).rotate((1,0,0), (0,0,0), -30).translate((0, -2.6, 1.3))
        screen = cq.Workplane("XY").box(0.7, 0.05, 0.5).translate((0, -2.2, 1.6))
        brb = cq.Workplane("XY").cylinder(0.04, 0.05).rotate((1,0,0),(0,0,0),-30).translate((0.2, -2.65, 1.35))
        batt = cq.Workplane("XY").box(0.7, 0.6, 0.4).translate((0, -2.5, 0.2))
        return base.union(panel).union(screen).union(brb).union(batt)

    def build_fuel_farm(self):
        # Tanks at Y=1.2. 
        h2 = cq.Workplane("XY").circle(0.15).extrude(1.2).edges(">Z").fillet(0.1).translate((0.6, 1.2, 0))
        b2h6 = cq.Workplane("XY").circle(0.15).extrude(1.2).edges(">Z").fillet(0.1).translate((0.0, 1.2, 0))
        dewar = cq.Workplane("XY").circle(0.25).extrude(0.9).edges(">Z").fillet(0.1).translate((-0.7, 1.2, 0))
        
        # ULTRA-THIN "PAINT" DECALS (0.001m thick, positioned just off the surface to prevent clipping)
        txt_h2 = cq.Workplane("XZ").text("HYDROGEN", 0.05, 0.001).translate((0.6, 1.049, 0.8))
        txt_b2 = cq.Workplane("XZ").text("DIBORANE", 0.05, 0.001).translate((0.0, 1.049, 0.8))
        txt_ch4 = cq.Workplane("XZ").text("LIQUID METHANE", 0.05, 0.001).translate((-0.7, 0.949, 0.45))
        
        return h2, b2h6, dewar, txt_h2, txt_b2, txt_ch4

    def build_rigid_plumbing(self):
        """Builds rigid, 90-degree industrial piping to guarantee no flying splines"""
        # 1. HV Cable (Console to Magnet)
        hv1 = cq.Workplane("XY").cylinder(0.6, 0.02).translate((0, -2.5, 1.6))  # Up from console
        hv2 = cq.Workplane("XZ").cylinder(2.5, 0.02).translate((0, -1.25, 1.9)) # Across the gap
        hv3 = cq.Workplane("XY").cylinder(0.5, 0.02).translate((0, 0, 1.65))    # Down to magnet
        
        # 2. Hydrogen Gas Line
        h2_1 = cq.Workplane("XY").cylinder(0.4, 0.015).translate((0.6, 1.2, 1.4))  # Up from tank
        h2_2 = cq.Workplane("YZ").cylinder(0.5, 0.015).translate((0.35, 1.2, 1.6)) # Left to center
        h2_3 = cq.Workplane("XZ").cylinder(1.1, 0.015).translate((0.1, 0.65, 1.6)) # Forward to NBI
        h2_4 = cq.Workplane("XY").cylinder(0.3, 0.015).translate((0.1, 0.1, 1.45)) # Down to NBI
        
        # 3. Diborane Gas Line
        b2_1 = cq.Workplane("XY").cylinder(0.3, 0.015).translate((0.0, 1.2, 1.35))
        b2_2 = cq.Workplane("XZ").cylinder(1.1, 0.015).translate((0.0, 0.65, 1.5))
        b2_3 = cq.Workplane("YZ").cylinder(0.1, 0.015).translate((-0.05, 0.1, 1.5))
        b2_4 = cq.Workplane("XY").cylinder(0.2, 0.015).translate((-0.1, 0.1, 1.4))

        # 4. Methane Cryo Coolant Line
        ch4_1 = cq.Workplane("XY").cylinder(0.5, 0.025).translate((-0.7, 1.2, 1.15))
        ch4_2 = cq.Workplane("XZ").cylinder(1.2, 0.025).translate((-0.7, 0.6, 1.4))
        ch4_3 = cq.Workplane("YZ").cylinder(0.65, 0.025).translate((-0.375, 0.0, 1.4))
        ch4_4 = cq.Workplane("XY").cylinder(0.15, 0.025).translate((-0.05, 0.0, 1.325))

        hv = hv1.union(hv2).union(hv3)
        gas = h2_1.union(h2_2).union(h2_3).union(h2_4).union(b2_1).union(b2_2).union(b2_3).union(b2_4)
        meth = ch4_1.union(ch4_2).union(ch4_3).union(ch4_4)
        
        return hv, gas, meth

# ==========================================
# ASSEMBLE AND EXPORT
# ==========================================
if __name__ == "__main__":
    print("Welding Industrial Plumbing and Finalizing 3D Layout...")
    tube = IntegratedOrbitronTube()
    infra = LabInfrastructure()
    assy = cq.Assembly(name="Orbitron_Test_Facility")

    # Colors
    c_niobium = cq.Color(0.8, 0.8, 0.85)   
    c_dec     = cq.Color(0.8, 0.6, 0.1)    
    c_cath    = cq.Color(0.2, 0.8, 0.9)    
    c_ceramic = cq.Color(0.9, 0.9, 0.9)    
    c_magnet  = cq.Color(0.2, 0.2, 0.2)    
    c_nbi     = cq.Color(0.3, 0.6, 0.4)    
    c_table   = cq.Color(0.15, 0.15, 0.15)    
    c_h2      = cq.Color(0.8, 0.1, 0.1)    
    c_b2h6    = cq.Color(0.1, 0.6, 0.2)    
    c_dewar   = cq.Color(0.7, 0.7, 0.8)    
    c_hv      = cq.Color(0.9, 0.4, 0.0)    
    
    # Stencil Paint Colors
    c_stencil_w = cq.Color(0.9, 0.9, 0.9)  # White Paint
    c_stencil_b = cq.Color(0.1, 0.1, 0.1)  # Black Paint

    # Add Lab Hardware
    table_body, table_label = infra.build_table()
    assy.add(table_body, name="Optics_Table", color=c_table)
    assy.add(table_label, name="Decal_Table_Placard", color=c_stencil_w)
    
    assy.add(infra.build_console(), name="Operator_Console", color=c_table)
    
    # Add Tanks and Stencil Decals
    h2, b2h6, dewar, t_h2, t_b2, t_ch4 = infra.build_fuel_farm()
    assy.add(h2, name="Tank_Hydrogen", color=c_h2)
    assy.add(b2h6, name="Tank_Diborane", color=c_b2h6)
    assy.add(dewar, name="Tank_Cryo_Methane", color=c_dewar)
    assy.add(t_h2, name="Decal_H2", color=c_stencil_w)
    assy.add(t_b2, name="Decal_B2H6", color=c_stencil_w)
    assy.add(t_ch4, name="Decal_CH4", color=c_stencil_b)
    
    # Add RIGID Plumbing
    hv, gas, meth = infra.build_rigid_plumbing()
    assy.add(hv, name="High_Voltage_Umbilical", color=c_hv)
    assy.add(gas, name="Fuel_Gas_Lines", color=cq.Color(0.2, 0.2, 0.2))
    assy.add(meth, name="Cryo_Methane_Piping", color=c_niobium)

    # Reactor Sub-Assembly
    anode, dec, cath, ins, mag, nbi = tube.build()
    r_assy = cq.Assembly(name="Reactor_Core")
    r_assy.add(anode, name="Anode", color=c_niobium)
    r_assy.add(dec, name="DEC_Grid", color=c_dec)
    r_assy.add(cath, name="Cathode", color=c_cath)
    r_assy.add(ins, name="Insulators", color=c_ceramic)
    r_assy.add(mag, name="Magnet", color=c_magnet)
    r_assy.add(nbi, name="NBI_Injector", color=c_nbi)
    
    # Rotate local Z to align with global X. Placed exactly at Z=1.25
    assy.add(r_assy, name="3_5MW_Tube", loc=cq.Location(cq.Vector(0, 0, 1.25), cq.Vector(0, 1, 0), 90))

    output_file = "orbitron_lab_v5.gltf"
    assy.save(output_file)
    print(f"Success! CAD saved to {output_file}")
