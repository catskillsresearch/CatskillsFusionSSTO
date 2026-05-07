# test_stand_reactor.py
import cadquery as cq
from reactor_module import OrbitronCore

class ReactorTestStand:
    def __init__(self):
        # INHERIT THE SUBASSEMBLY
        self.test_article = OrbitronCore(power_gw=3.5)
        
    def generate_cad(self):
        # 1. Get the reactor CAD
        reactor_cad = self.test_article.generate_cad()
        
        # 2. Build a concrete floor and steel gantry using CadQuery
        floor = cq.Workplane("XY").box(10, 10, 0.5).translate((0, 0, -2.5))
        gantry = cq.Workplane("XY").rect(2, 2).extrude(2).translate((0,0,-2))
        
        # 3. Snap them together using the reactor's interface mounts
        assembly = cq.Assembly()
        assembly.add(floor, color=cq.Color("gray"))
        assembly.add(gantry, color=cq.Color("yellow"))
        assembly.add(reactor_cad, loc=cq.Location(self.test_article.interfaces["mount_points"][0]))
        
        return assembly

# Export directly to a 3D format
stand = ReactorTestStand()
stand.generate_cad().save("reactor_test_stand.gltf")
