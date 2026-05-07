import cadquery as cq

class OrbitronCore:
    """Module 1: The 3.5 GW p-B11 Fusion Reactor"""
    def __init__(self):
        self.radius = 1.7
        self.length = 2.0

    def generate_cad(self):
        print("Machining Orbitron Core...")
        # 1. Base Cylinder
        core = cq.Workplane("XY").cylinder(height=self.length, radius=self.radius)
        
        # 2. Hollow out the center for the plasma chamber
        core = core.faces(">Z").workplane().hole(diameter=2.0)
        
        # 3. Cut an exhaust nozzle taper at the back
        core = core.faces("<Z").workplane().circle(1.0).workplane(offset=0.5).circle(0.5).loft(combine="cut")
        
        # 4. Add an external mounting ring around the equator
        mounting_ring = cq.Workplane("XY").cylinder(height=0.2, radius=self.radius + 0.15)
        core = core.union(mounting_ring)
        
        # 5. Fillet (round) the sharp outer edges to reduce structural stress
        core = core.edges(">Z").fillet(0.1)
        
        return core

class TestStand:
    """Module 2: The Ground Test Facility Rig"""
    def __init__(self):
        pass

    def build_assembly(self, test_article_cad):
        print("Welding Test Stand and Mounting Hardware...")
        
        # 1. Heavy concrete pad
        floor = cq.Workplane("XY").box(6.0, 6.0, 0.5).translate((0, 0, -2.0))
        
        # 2. Steel mounting struts
        strut1 = cq.Workplane("XY").box(0.4, 1.0, 2.0).translate((1.8, 0, -1.0))
        strut2 = cq.Workplane("XY").box(0.4, 1.0, 2.0).translate((-1.8, 0, -1.0))
        
        # 3. Assemble hierarchically
        print("Mating components into Assembly...")
        assy = cq.Assembly(name="Reactor_Test_Stand")
        
        # FIX: Using explicit RGB floats (R, G, B) to prevent string lookup errors!
        color_concrete = cq.Color(0.2, 0.2, 0.2) # Dark Gray
        color_steel = cq.Color(0.8, 0.8, 0.1)    # Yellow Industrial
        color_metal = cq.Color(0.7, 0.7, 0.7)    # Silver
        
        # Add the ground hardware
        assy.add(floor, name="Concrete_Pad", color=color_concrete)
        assy.add(strut1, name="Strut_Left", color=color_steel)
        assy.add(strut2, name="Strut_Right", color=color_steel)
        
        # Add the reactor
        assy.add(test_article_cad, name="Orbitron_Reactor", color=color_metal)
        
        return assy

# ==========================================
# EXECUTE THE PIPELINE
# ==========================================
if __name__ == "__main__":
    reactor = OrbitronCore()
    stand = TestStand()
    
    reactor_cad = reactor.generate_cad()
    final_assembly = stand.build_assembly(reactor_cad)
    
    output_file = "reactor_test_stand.gltf"
    print(f"Exporting CAD to {output_file}...")
    final_assembly.save(output_file)
    print("Export Complete!")
