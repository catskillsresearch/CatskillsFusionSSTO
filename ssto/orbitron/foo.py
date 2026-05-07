import cadquery as cq

class IntegratedOrbitronTube:
    """The 3.5 MW p-B11 Reactor Core and Support Hardware"""
    def __init__(self):
        self.tube_r = 0.05
        self.tube_h = 2.0

    def build_core(self):
        anode = cq.Workplane("XY").cylinder(height=self.tube_h, radius=self.tube_r)
        anode = anode.faces(">Z").workplane().hole(diameter=self.tube_r*2 - 0.01)
        dec_grid = cq.Workplane("XY").cylinder(height=self.tube_h, radius=self.tube_r - 0.005)
        dec_grid = dec_grid.faces(">Z").workplane().hole(diameter=(self.tube_r - 0.005)*2 - 0.002)
        cathode = cq.Workplane("XY").cylinder(height=self.tube_h + 0.8, radius=0.005)
        return anode, dec_grid, cathode

    def build_insulators(self):
        ins = cq.Workplane("XY").cylinder(height=0.3, radius=0.03)
        for i in range(5):
            rib = cq.Workplane("XY").workplane(offset=-0.1 + i*0.05).cylinder(height=0.02, radius=0.045)
            ins = ins.union(rib)
        return ins.translate((0, 0, self.tube_h/2 + 0.15)).union(ins.translate((0, 0, -self.tube_h/2 - 0.15)))

    def build_magnet(self):
        mag_h = self.tube_h - 0.5
        magnet = cq.Workplane("XY").cylinder(height=mag_h, radius=0.15)
        magnet = magnet.faces(">Z").workplane().hole(diameter=self.tube_r*2 + 0.01)
        band1 = cq.Workplane("XY").workplane(offset=mag_h/2 - 0.1).cylinder(height=0.05, radius=0.16)
        band2 = cq.Workplane("XY").workplane(offset=-mag_h/2 + 0.1).cylinder(height=0.05, radius=0.16)
        return magnet.union(band1).union(band2)

    def build_nbi(self):
        nbi_housing = cq.Workplane("YZ").cylinder(height=0.4, radius=0.04).translate((0.2, 0, 0))
        nbi_flange = cq.Workplane("YZ").cylinder(height=0.05, radius=0.06).translate((0.4, 0, 0))
        nbi_feed = cq.Workplane("YZ").box(0.2, 0.05, 0.05).translate((0.5, 0, 0))
        return nbi_housing.union(nbi_flange).union(nbi_feed)

class LabInfrastructure:
    """The Balance of Plant: Tanks, Batteries, Controls"""
    
    def build_table_and_rack(self):
        table = cq.Workplane("XY").box(1.5, 1.0, 0.1).translate((0, 0, -1.0))
        legs = (cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((0.65, 0.4, -1.5))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((-0.65, 0.4, -1.5)))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((0.65, -0.4, -1.5)))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((-0.65, -0.4, -1.5))))
        mounts = cq.Workplane("XY").box(0.2, 0.2, 0.7).translate((0.5, 0, -0.65)).union(cq.Workplane("XY").box(0.2, 0.2, 0.7).translate((-0.5, 0, -0.65)))
        rack = cq.Workplane("XY").box(0.8, 0.6, 1.8).translate((0, 1.2, -0.6))
        return table.union(legs).union(mounts), rack

    def build_battery(self):
        battery = cq.Workplane("XY").box(0.7, 0.5, 0.4).translate((0, 1.2, -1.3))
        terminals = cq.Workplane("XY").cylinder(0.05, 0.02).translate((0.2, 1.0, -1.1)).union(
                    cq.Workplane("XY").cylinder(0.05, 0.02).translate((-0.2, 1.0, -1.1)))
        return battery.union(terminals)

    def build_fuel_farm(self):
        cyl_h2 = cq.Workplane("XY").circle(0.15).extrude(1.2).edges(">Z").fillet(0.14).translate((-1.2, -0.2, -1.5))
        cyl_b = cq.Workplane("XY").circle(0.15).extrude(1.2).edges(">Z").fillet(0.14).translate((-1.2, 0.2, -1.5))
        dewar = cq.Workplane("XY").circle(0.3).extrude(0.9).edges(">Z").fillet(0.05).translate((-1.2, 0.9, -1.5))
        return cyl_h2, cyl_b, dewar

    def build_control_panel(self):
        panel = cq.Workplane("XY").box(0.8, 0.5, 0.05).rotate((1,0,0), (0,0,0), 30).translate((0, 0.9, 0.3))
        screen = cq.Workplane("XY").box(0.7, 0.05, 0.5).translate((0, 1.15, 0.9))
        
        brb_base = cq.Workplane("XY").cylinder(0.02, 0.04).rotate((1,0,0),(0,0,0),30).translate((0.25, 0.85, 0.35))
        brb_top = cq.Workplane("XY").cylinder(0.02, 0.03).rotate((1,0,0),(0,0,0),30).translate((0.25, 0.84, 0.37))
        button = brb_base.union(brb_top)
        
        dial1 = cq.Workplane("XY").cylinder(0.03, 0.02).rotate((1,0,0),(0,0,0),30).translate((-0.25, 0.95, 0.4))
        dial2 = cq.Workplane("XY").cylinder(0.03, 0.02).rotate((1,0,0),(0,0,0),30).translate((-0.15, 0.95, 0.4))
        dial3 = cq.Workplane("XY").cylinder(0.03, 0.02).rotate((1,0,0),(0,0,0),30).translate((-0.05, 0.95, 0.4))
        
        slider_track = cq.Workplane("XY").box(0.02, 0.2, 0.01).rotate((1,0,0),(0,0,0),30).translate((0.1, 0.85, 0.32))
        slider_knob = cq.Workplane("XY").box(0.04, 0.02, 0.05).rotate((1,0,0),(0,0,0),30).translate((0.1, 0.85, 0.35))
        
        controls = panel.union(screen).union(button).union(dial1).union(dial2).union(dial3).union(slider_track).union(slider_knob)
        return controls, button, slider_knob

    def build_routing_splines(self):
        # 1. High Voltage Cable (Orange) - Console to Magnet
        path_elec = cq.Workplane("XY").spline([(0, 0.9, 0.5), (0, 0.5, 0.1), (0, 0.1, -0.15)])
        cable_elec = cq.Workplane("YZ").workplane(offset=0).circle(0.025).sweep(path_elec)
        
        # 2. Hydrogen Gas Line (Red) - Tank to NBI
        path_h2 = cq.Workplane("XY").spline([(-1.2, -0.2, -0.3), (-0.6, -0.2, -0.4), (0.0, 0.0, -0.15)])
        hose_h2 = cq.Workplane("YZ").workplane(offset=-1.2).circle(0.015).sweep(path_h2)
        
        # 3. Diborane Gas Line (Green) - Tank to NBI
        path_b2h6 = cq.Workplane("XY").spline([(-1.2, 0.2, -0.3), (-0.6, 0.2, -0.4), (0.0, 0.1, -0.15)])
        hose_b2h6 = cq.Workplane("YZ").workplane(offset=-1.2).circle(0.015).sweep(path_b2h6)
        
        # 4. Methane Cryo Coolant Line (Silver) - Dewar to Reactor Jacket
        path_ch4 = cq.Workplane("XY").spline([(-1.2, 0.9, -0.6), (-0.6, 0.5, -0.5), (-0.2, 0.0, -0.15)])
        pipe_ch4 = cq.Workplane("YZ").workplane(offset=-1.2).circle(0.03).sweep(path_ch4)
        
        return cable_elec, hose_h2, hose_b2h6, pipe_ch4

# ==========================================
# ASSEMBLE AND EXPORT
# ==========================================
if __name__ == "__main__":
    print("Routing cables and initializing Systems Assembly...")
    tube = IntegratedOrbitronTube()
    infra = LabInfrastructure()
    assy = cq.Assembly(name="Orbitron_Test_Facility")

    # Defined Colors (R, G, B floats)
    col_niobium = cq.Color(0.7, 0.7, 0.75)   
    col_dec     = cq.Color(0.8, 0.6, 0.1)    
    col_cath    = cq.Color(0.2, 0.8, 0.9)    
    col_ceramic = cq.Color(0.9, 0.9, 0.9)    
    col_magnet  = cq.Color(0.7, 0.4, 0.1)    
    col_nbi     = cq.Color(0.3, 0.6, 0.4)    
    col_table   = cq.Color(0.1, 0.1, 0.1)    
    col_rack    = cq.Color(0.2, 0.2, 0.2)    
    
    col_batt    = cq.Color(0.8, 0.7, 0.1)    
    col_h2      = cq.Color(0.8, 0.1, 0.1)    
    col_b2h6    = cq.Color(0.1, 0.6, 0.2)    
    col_dewar   = cq.Color(0.8, 0.8, 0.9)    
    col_panel   = cq.Color(0.15, 0.15, 0.2)  
    col_brb     = cq.Color(0.9, 0.0, 0.0)    
    col_slider  = cq.Color(0.7, 0.7, 0.7)    
    col_cable_e = cq.Color(0.9, 0.4, 0.0)    # Orange wire

    # 1. Base Infrastructure
    table_rack, rack_body = infra.build_table_and_rack()
    assy.add(table_rack, name="Optical_Table", color=col_table)
    assy.add(rack_body, name="Equipment_Rack", color=col_rack)

    # 2. Balance of Plant (BOP)
    assy.add(infra.build_battery(), name="Startup_Battery_50kWh", color=col_batt)
    cyl_h2, cyl_b, dewar = infra.build_fuel_farm()
    assy.add(cyl_h2, name="Tank_H2_Gas", color=col_h2)
    assy.add(cyl_b, name="Tank_Diborane_Gas", color=col_b2h6)
    assy.add(dewar, name="Cryo_Methane_Dewar", color=col_dewar)

    # 3. Control Console
    controls, brb, slider = infra.build_control_panel()
    assy.add(controls, name="Control_Panel", color=col_panel)
    assy.add(brb, name="Big_Red_Button", color=col_brb)
    assy.add(slider, name="Throttle_Slider", color=col_slider)

    # 4. Reactor Core
    anode, dec_grid, cathode = tube.build_core()
    reactor_assy = cq.Assembly(name="Orbitron_3_5MW_Core")
    reactor_assy.add(anode, name="Anode_Shell", color=col_niobium)
    reactor_assy.add(dec_grid, name="DEC_Grid", color=col_dec)
    reactor_assy.add(cathode, name="Cathode_Wire", color=col_cath)
    reactor_assy.add(tube.build_insulators(), name="Ceramic_Feedthroughs", color=col_ceramic)
    reactor_assy.add(tube.build_magnet(), name="YBCO_Magnet", color=col_magnet)
    reactor_assy.add(tube.build_nbi(), name="Neutral_Beam_Injector", color=col_nbi)
    assy.add(reactor_assy, name="Reactor_Hardware", loc=cq.Location(cq.Vector(0, 0, -0.15), cq.Vector(0, 1, 0), 90))

    # 5. Routing Splines (Tubes and Wires)
    cable_elec, hose_h2, hose_b2h6, pipe_ch4 = infra.build_routing_splines()
    assy.add(cable_elec, name="HV_Umbilical", color=col_cable_e)
    assy.add(hose_h2, name="H2_Line", color=col_h2)
    assy.add(hose_b2h6, name="B2H6_Line", color=col_b2h6)
    assy.add(pipe_ch4, name="Methane_Line", color=col_dewar)

    output_file = "orbitron_lab_floor.gltf"
    print(f"Exporting Systems CAD to {output_file}...")
    assy.save(output_file)
    print("Export Complete! Open in Blender to inspect.")
