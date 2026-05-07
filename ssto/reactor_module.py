# reactor_module.py
import cadquery as cq

class OrbitronCore:
    def __init__(self, power_gw=3.5):
        self.power = power_gw
        self.mass = 12000 # kg
        # Define the attachment points (Interfaces)
        self.interfaces = {
            "coolant_inlet": (0, 0, 1.0),
            "exhaust_outlet": (0, 0, -1.0),
            "mount_points":[(1,0,0), (-1,0,0)]
        }

    def generate_cad(self):
        """Uses CadQuery to generate the physical reactor geometry"""
        # Create a sleek, filleted cylindrical housing
        core = cq.Workplane("XY").circle(1.7).extrude(2.0).edges().fillet(0.2)
        # Cut the coolant inlet ports
        core = core.faces(">Z").workplane().circle(0.5).cutThruAll()
        return core
