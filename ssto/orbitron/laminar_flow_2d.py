"""Orbitron laminar-flow WarpX PIC case (2D crossed-field slice).

Engineering rationale, limitations, and post-processing notes for this deck (vs the
YAML-driven ``laminar_flow_2d_arcjet.py`` sweep) live in
``assembly_specs/orbitron_physics_surrogate.yaml`` under ``formal:`` —
``laminar_flow_2d_py_case_review``, ``design_brief_gaps_fusion_arcjet``,
``postprocessing_animate_plasma_note``.
"""
import numpy as np
from pywarpx import picmi

print("==================================================")
print("  ORBITRON LAMINAR FLOW (X-Z PLANE ROTATION FIX)  ")
print("==================================================")

# --- DEVICE GEOMETRY & FIELDS ---
r_anode = 0.05
r_cathode = 0.005
V_cathode = -600e3
B_axial = 2.0  # Will be applied to the Y-axis (out of the page)

# WarpX 2D uses the X and Z axes. Y is ignored/invariant.
grid = picmi.Cartesian2DGrid(
    number_of_cells=[256, 256], 
    lower_bound=[-r_anode, -r_anode],
    upper_bound=[r_anode, r_anode],
    lower_boundary_conditions=['dirichlet', 'dirichlet'],
    upper_boundary_conditions=['dirichlet', 'dirichlet'],
    lower_boundary_conditions_particles=['absorbing', 'absorbing'],
    upper_boundary_conditions_particles=['absorbing', 'absorbing']
)

# --- CROSSED E and B FIELDS (Mapped to X-Z plane) ---
E_field_expr = f"-({V_cathode}/log({r_anode}/{r_cathode}))"

# Using x*x + z*z for AMReX C++ parser safety
Ex_expr = f"({E_field_expr} * x / max(sqrt(x*x + z*z), {r_cathode})) * ( (x*x + z*z) >= {r_cathode*r_cathode} )"
Ez_expr = f"({E_field_expr} * z / max(sqrt(x*x + z*z), {r_cathode})) * ( (x*x + z*z) >= {r_cathode*r_cathode} )"

applied_E = picmi.AnalyticAppliedField(Ex_expression=Ex_expr, Ey_expression="0.0", Ez_expression=Ez_expr)

# B-field points OUT OF THE PAGE (Y-axis) to create rotation in the X-Z plane
applied_B = picmi.AnalyticAppliedField(Bx_expression="0.0", By_expression=str(B_axial), Bz_expression="0.0")

# --- THE HOLLOW ELECTRON RING ---
n_e = 5e15 
electron_ring = picmi.AnalyticDistribution(
    density_expression=f"{n_e} * (sqrt(x*x + z*z) > 0.01) * (sqrt(x*x + z*z) < 0.03)",
    # E x B drift in X-Z plane with B in Y:
    # vx = -Ez / By   |   vz = Ex / By
    momentum_expressions=[
        f"-({E_field_expr} * z / max(sqrt(x*x + z*z), 1e-4)) / {B_axial}",  # ux
        "0.0",                                                             # uy
        f"({E_field_expr} * x / max(sqrt(x*x + z*z), 1e-4)) / {B_axial}"    # uz
    ]
)

electrons = picmi.Species(particle_type='electron', name='electrons', initial_distribution=electron_ring)

# --- THE LAMINAR FIX: BEAM INJECTION ---
beam_injector = picmi.ParticleListDistribution(
    x=[0.04] * 100,  
    y=[0.0] * 100, 
    z=np.linspace(-0.01, 0.01, 100).tolist(), # Spread across the Z axis
    ux=[-3e6] * 100, # Shoot inwards to create shear
    uy=[0.0] * 100,
    uz=[0.0] * 100,
    weight=[1e10] * 100
)

stabilizing_beam = picmi.Species(particle_type='proton', name='stabilizing_beam', initial_distribution=beam_injector)

# --- ASSEMBLE AND RUN ---
sim = picmi.Simulation(solver=picmi.ElectromagneticSolver(grid=grid, cfl=0.9),
                       max_steps=500, # Running 500 steps to quickly prove stability
                       verbose=1, time_step_size=1e-12)

sim.add_applied_field(applied_E)
sim.add_applied_field(applied_B)

sim.add_species(electrons, layout=picmi.GriddedLayout(n_macroparticle_per_cell=[4,4], grid=grid))
sim.add_species(stabilizing_beam, layout=None) 

diag = picmi.FieldDiagnostic(
    name='density_diag',
    grid=grid,
    period=100,
    data_list=['rho_electrons'],
    write_dir='diags'
)
sim.add_diagnostic(diag)

print("Running ExB Relaminarization physics...")
sim.step(500)
print("Simulation complete. Check 'diags' folder for Diocotron vortex data.")
