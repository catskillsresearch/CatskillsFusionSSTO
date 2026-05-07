# ssto_fuselage.py
import cadquery as cq

def generate_sleek_ssto():
    # CadQuery lofting: We define cross-sections and let the math stretch a smooth skin over them.
    ssto = (
        cq.Workplane("YZ")
        # Nose cone tip (point)
        .workplane(offset=0).circle(0.01)
        # Cockpit cross-section (oval)
        .workplane(offset=-4).ellipse(1.5, 2.0)
        # Mid-body Methane tank (large circle)
        .workplane(offset=-10).circle(2.0)
        # Tail section (flattened oval for engine mounts)
        .workplane(offset=-18).ellipse(2.5, 1.0)
        # Instruct CadQuery to mathematically loft a smooth aerodynamic skin over these profiles
        .loft(ruled=False) 
    )
    
    # Smooth the whole body
    ssto = ssto.edges().fillet(0.5)
    return ssto
