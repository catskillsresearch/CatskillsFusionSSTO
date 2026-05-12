"""
GOAL 2 — Arc-heating oriented extension of the 2D Orbitron PICMI case.

Throttle/compressor map to PIC inputs:
  * throttle  → scales reactor-side electron ring density (NBI / fuel proxy).
  * compressor → scales arc_channel_seed density (air path / arc precursor proxy).

CLI examples:
  cd ssto/orbitron && python laminar_flow_2d_arcjet.py --write-dir diags --throttle 0.5 --compressor 1.0

Surrogate sweep driver: tools/build_surrogate_map.py (repo root).
"""
from __future__ import annotations

import argparse
import math
import sys

import numpy as np

try:
    from pywarpx import picmi
except ImportError as e:
    raise SystemExit(
        "pywarpx not installed in this interpreter. Typical WarpX build paths:\n"
        "  export PYTHONPATH=/path/to/WarpX/build/lib/python3.12/site-packages:$PYTHONPATH\n"
        "or tools/build_surrogate_map.sh sets this automatically when WarpX lives under repo WarpX/.\n"
        f"Original error: {e}"
    ) from e

BASE_N_E = 5e15
BASE_ARC_SEED = 1e14
INCLUDE_NITROGEN_TRACER = False


def _wx(x: float) -> str:
    """
    Format numbers for WarpX / AMReX math parser strings.

    Scientific literals like ``1e-4`` (no '.' before ``e``) can trigger
    ``parser_exe_eval: unknown node type`` in recent AMReX; use fixed-point
    or ``1.e-4``-style exponents. We prefer plain decimals when compact.
    """
    xf = float(x)
    if xf == 0.0:
        return "0.0"
    ax = abs(xf)
    if ax >= 1e9 or (ax < 1e-4 and ax > 0.0):
        sign = "-" if xf < 0 else ""
        mant, exp = f"{ax:.15e}".lower().split("e")
        exp_i = int(exp)
        if "." not in mant:
            mant += ".0"
        return f"{sign}{mant}e{exp_i}"
    s = format(xf, ".12f").rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0.0"


def scaled_densities(throttle: float, compressor: float) -> tuple[float, float]:
    t = max(0.0, min(1.0, float(throttle)))
    c = max(0.0, min(1.0, float(compressor)))
    n_e = BASE_N_E * (0.15 + 0.85 * t)
    arc_seed_density = BASE_ARC_SEED * (0.15 + 0.85 * c)
    return n_e, arc_seed_density


def run_arcjet_picmi(
    *,
    throttle: float,
    compressor: float,
    write_dir: str,
    n_steps: int,
    diag_period: int,
) -> None:
    n_e, arc_seed_density = scaled_densities(throttle, compressor)

    print("==================================================")
    print("  ORBITRON 2D + ARC CHANNEL SEED (PICMI)         ")
    print(
        f"  throttle={throttle:g} compressor={compressor:g} "
        f"n_e={n_e:g} arc_seed={arc_seed_density:g}"
    )
    print(f"  write_dir={write_dir}")
    print("==================================================")

    r_anode = 0.05
    r_cathode = 0.005
    V_cathode = -600e3
    B_axial = 2.0
    # Cylindrical radial E magnitude (computed in Python; avoids log() in parser edge cases)
    E0 = -(V_cathode / math.log(r_anode / r_cathode))
    r_ca = _wx(r_cathode)
    r_ca2 = _wx(r_cathode * r_cathode)
    E0s = _wx(E0)
    Bys = _wx(B_axial)
    r_eps = _wx(1e-4)

    grid = picmi.Cartesian2DGrid(
        number_of_cells=[256, 256],
        lower_bound=[-r_anode, -r_anode],
        upper_bound=[r_anode, r_anode],
        lower_boundary_conditions=["dirichlet", "dirichlet"],
        upper_boundary_conditions=["dirichlet", "dirichlet"],
        lower_boundary_conditions_particles=["absorbing", "absorbing"],
        upper_boundary_conditions_particles=["absorbing", "absorbing"],
    )

    # Parser: use infix comparisons inside if(cond, a, b); avoid if(gt(...)) (not all builds expose gt/lt).
    Ex_expr = (
        f"({E0s} * x / if(sqrt(x*x + z*z) > {r_ca}, sqrt(x*x + z*z), {r_ca})) * "
        f"if(x*x + z*z >= {r_ca2}, 1.0, 0.0)"
    )
    Ez_expr = (
        f"({E0s} * z / if(sqrt(x*x + z*z) > {r_ca}, sqrt(x*x + z*z), {r_ca})) * "
        f"if(x*x + z*z >= {r_ca2}, 1.0, 0.0)"
    )

    applied_E = picmi.AnalyticAppliedField(
        Ex_expression=Ex_expr, Ey_expression="0.0", Ez_expression=Ez_expr
    )
    applied_B = picmi.AnalyticAppliedField(
        Bx_expression="0.0", By_expression=Bys, Bz_expression="0.0"
    )

    n_es = _wx(n_e)
    r_ring_in = _wx(0.01)
    r_ring_out = _wx(0.03)
    electron_ring = picmi.AnalyticDistribution(
        density_expression=(
            f"{n_es} * if(sqrt(x*x + z*z) > {r_ring_in}, 1.0, 0.0) * "
            f"if(sqrt(x*x + z*z) < {r_ring_out}, 1.0, 0.0)"
        ),
        momentum_expressions=[
            f"-({E0s} * z / if(sqrt(x*x + z*z) > {r_eps}, sqrt(x*x + z*z), {r_eps})) / {Bys}",
            "0.0",
            f"({E0s} * x / if(sqrt(x*x + z*z) > {r_eps}, sqrt(x*x + z*z), {r_eps})) / {Bys}",
        ],
    )
    electrons = picmi.Species(
        particle_type="electron", name="electrons", initial_distribution=electron_ring
    )

    arc_s = _wx(arc_seed_density)
    r_arc_in = _wx(0.035)
    r_arc_out = _wx(r_anode * 0.98)
    arc_seed = picmi.AnalyticDistribution(
        density_expression=(
            f"{arc_s} * if(sqrt(x*x + z*z) > {r_arc_in}, 1.0, 0.0) * "
            f"if(sqrt(x*x + z*z) < {r_arc_out}, 1.0, 0.0)"
        ),
        momentum_expressions=["0.0", "0.0", "0.0"],
    )
    arc_channel_seed = picmi.Species(
        particle_type="electron",
        name="arc_channel_seed",
        initial_distribution=arc_seed,
    )

    beam_injector = picmi.ParticleListDistribution(
        x=[0.04] * 100,
        y=[0.0] * 100,
        z=np.linspace(-0.01, 0.01, 100).tolist(),
        ux=[-3e6] * 100,
        uy=[0.0] * 100,
        uz=[0.0] * 100,
        weight=[1e10] * 100,
    )
    stabilizing_beam = picmi.Species(
        particle_type="proton",
        name="stabilizing_beam",
        initial_distribution=beam_injector,
    )

    species_list = [
        (electrons, picmi.GriddedLayout(n_macroparticle_per_cell=[4, 4], grid=grid)),
        (arc_channel_seed, picmi.GriddedLayout(n_macroparticle_per_cell=[2, 2], grid=grid)),
        (stabilizing_beam, None),
    ]

    if INCLUDE_NITROGEN_TRACER:
        n_ion = 1e13
        n2_tracer = picmi.AnalyticDistribution(
            density_expression=(
                f"{n_ion} * (sqrt(x*x + z*z) > 0.02) * (sqrt(x*x + z*z) < 0.045)"
            ),
            momentum_expressions=["0.0", "0.0", "0.0"],
        )
        nitrogen_tracer = picmi.Species(
            particle_type="nitrogen",
            name="n2_tracer",
            charge_state=1,
            initial_distribution=n2_tracer,
        )
        species_list.append(
            (
                nitrogen_tracer,
                picmi.GriddedLayout(n_macroparticle_per_cell=[1, 1], grid=grid),
            )
        )

    sim = picmi.Simulation(
        solver=picmi.ElectromagneticSolver(grid=grid, cfl=0.9),
        max_steps=n_steps,
        verbose=1,
        time_step_size=1e-12,
    )

    sim.add_applied_field(applied_E)
    sim.add_applied_field(applied_B)

    for spec, layout in species_list:
        sim.add_species(spec, layout=layout)

    data_list = ["rho_electrons", "rho_arc_channel_seed", "rho_stabilizing_beam"]
    if INCLUDE_NITROGEN_TRACER:
        data_list.append("rho_n2_tracer")

    diag = picmi.FieldDiagnostic(
        name="density_diag",
        grid=grid,
        period=diag_period,
        data_list=data_list,
        write_dir=write_dir,
    )
    sim.add_diagnostic(diag)

    print("Running arc-seed + ExB reactor slice...")
    sim.step(n_steps)
    print("Complete. Post-process diags with animate_plasma.py or surrogate pipeline.")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Orbitron 2D arcjet PICMI (WarpX)")
    p.add_argument("--throttle", type=float, default=1.0, help="0..1 reactor ring density scale")
    p.add_argument("--compressor", type=float, default=1.0, help="0..1 arc seed density scale")
    p.add_argument("--write-dir", type=str, default="diags", help="WarpX diagnostic output directory")
    p.add_argument("--steps", type=int, default=500)
    p.add_argument("--diag-period", type=int, default=100)
    args = p.parse_args(argv)

    run_arcjet_picmi(
        throttle=args.throttle,
        compressor=args.compressor,
        write_dir=args.write_dir,
        n_steps=args.steps,
        diag_period=args.diag_period,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
