import cadquery as cq

class SingleOrbitronTube:
    """Module: A single 3.5 MW p-B11 Orbitron Tube"""
    def __init__(self):
        self.tube_radius = 0.05  # 5 cm radius (10 cm diameter)
        self.tube_length = 2.0   # 2 meters long
        self.cathode_radius = 0.005 # 5 mm central high-voltage wire

    def generate_cad(self):
        # 1. The Niobium Anode Shell (Outer Wall)
        anode_shell = (
            cq.Workplane("XY")
            .cylinder(height=self.tube_length, radius=self.tube_radius)
            .faces(">Z").workplane().hole(diameter=self.tube_radius * 2 - 0.01) # Hollow it out with 5mm walls
        )
        
        # 2. The Tungsten Cathode Wire (Runs down the center, sticks out the ends)
        cathode = cq.Workplane("XY").cylinder(height=self.tube_length + 0.4, radius=self.cathode_radius)
        
        # 3. High Voltage Ceramic Feedthroughs (Insulators at the ends)
        insulator_top = cq.Workplane("XY").workplane(offset=self.tube_length/2).cylinder(height=0.15, radius=0.03)
        insulator_bottom = cq.Workplane("XY").workplane(offset=-self.tube_length/2).cylinder(height=0.15, radius=0.03)
        
        # Combine tube elements
        tube_assembly = anode_shell.union(cathode).union(insulator_top).union(insulator_bottom)
        
        return tube_assembly

class LabTestStand:
    """Module: Optical Table and Diagnostic Mounts"""
    def __init__(self):
        pass

    def build_assembly(self, tube_cad):
        # 1. Optical Table (Standard lab table)
        table = cq.Workplane("XY").box(1.0, 1.0, 0.1).translate((0, 0, -1.0))
        table_leg1 = cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((0.4, 0.4, -1.5))
        table_leg2 = cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((-0.4, 0.4, -1.5))
        table_leg3 = cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((0.4, -0.4, -1.5))
        table_leg4 = cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((-0.4, -0.4, -1.5))
        full_table = table.union(table_leg1).union(table_leg2).union(table_leg3).union(table_leg4)
        
        # 2. V-Block Mounts (To hold the tube horizontally)
        # We rotate the tube 90 degrees to lay it flat on the table
        mount1 = cq.Workplane("XY").box(0.2, 0.2, 0.5).translate((0, 0.6, -0.7))
        mount2 = cq.Workplane("XY").box(0.2, 0.2, 0.5).translate((0, -0.6, -0.7))
        
        # 3. Assemble and apply RGB colors (0.0 to 1.0)
        assy = cq.Assembly(name="Single_Tube_Test_Rig")
        
        color_table = cq.Color(0.1, 0.1, 0.1)     # Black optical table
        color_mounts = cq.Color(0.2, 0.4, 0.8)    # Blue anodized aluminum
        color_niobium = cq.Color(0.8, 0.8, 0.85)  # Shiny metal tube
        
        assy.add(full_table, name="Optical_Table", color=color_table)
        assy.add(mount1, name="Mount_Forward", color=color_mounts)
        assy.add(mount2, name="Mount_Aft", color=color_mounts)
        
        # Rotate the tube 90 degrees on the X axis to lay it in the mounts
        assy.add(tube_cad, name="Orbitron_3_5_MW_Tube", color=color_niobium, 
                 loc=cq.Location(cq.Vector(0, 0, -0.45), cq.Vector(1, 0, 0), 90))
        
        return assy

if __name__ == "__main__":
    tube = SingleOrbitronTube()
    stand = LabTestStand()
    
    tube_cad = tube.generate_cad()
    final_assembly = stand.build_assembly(tube_cad)
    
    output_file = "single_tube_stand.gltf"
    print(f"Exporting CAD to {output_file}...")
    final_assembly.save(output_file)
    print("Export Complete! Import into Blender to view.")
