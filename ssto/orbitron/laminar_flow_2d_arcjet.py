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
import json
import math
import sys
from pathlib import Path
from typing import Any

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


def scaled_densities(
    throttle: float, compressor: float, o: dict[str, Any] | None = None
) -> tuple[float, float]:
    o = o or {}
    t = max(0.0, min(1.0, float(throttle)))
    c = max(0.0, min(1.0, float(compressor)))
    base_ne = float(o.get("base_n_e", BASE_N_E))
    base_arc = float(o.get("base_arc_seed", BASE_ARC_SEED))
    rs = o.get("ring_density_scale") or {"throttle_offset": 0.15, "throttle_gain": 0.85}
    acs = o.get("arc_seed_scale") or {"compressor_offset": 0.15, "compressor_gain": 0.85}
    n_e = base_ne * (float(rs["throttle_offset"]) + float(rs["throttle_gain"]) * t)
    arc_seed_density = base_arc * (
        float(acs["compressor_offset"]) + float(acs["compressor_gain"]) * c
    )
    return n_e, arc_seed_density


def run_arcjet_picmi(
    *,
    throttle: float,
    compressor: float,
    write_dir: str,
    n_steps: int,
    diag_period: int,
    picmi_overrides: dict[str, Any] | None = None,
) -> None:
    o = picmi_overrides or {}
    n_e, arc_seed_density = scaled_densities(throttle, compressor, o)

    print("==================================================")
    print("  ORBITRON 2D + ARC CHANNEL SEED (PICMI)         ")
    print(
        f"  throttle={throttle:g} compressor={compressor:g} "
        f"n_e={n_e:g} arc_seed={arc_seed_density:g}"
    )
    print(f"  write_dir={write_dir}")
    print("==================================================")

    r_anode = float(o.get("r_anode_m", o.get("domain_half_extent_m", 0.05)))
    r_cathode = float(o.get("r_cathode_m", 0.005))
    V_cathode = float(o.get("V_cathode_v", -600e3))
    B_axial = float(o.get("B_axial_tesla", 2.0))
    # Cylindrical radial E magnitude (computed in Python; avoids log() in parser edge cases)
    E0 = -(V_cathode / math.log(r_anode / r_cathode))
    r_ca = _wx(r_cathode)
    r_ca2 = _wx(r_cathode * r_cathode)
    E0s = _wx(E0)
    Bys = _wx(B_axial)

    n_cells = o.get("number_of_cells") or [256, 256]
    nx, nz = int(n_cells[0]), int(n_cells[1])
    grid = picmi.Cartesian2DGrid(
        number_of_cells=[nx, nz],
        lower_bound=[-r_anode, -r_anode],
        upper_bound=[r_anode, r_anode],
        lower_boundary_conditions=["dirichlet", "dirichlet"],
        upper_boundary_conditions=["dirichlet", "dirichlet"],
        lower_boundary_conditions_particles=["absorbing", "absorbing"],
        upper_boundary_conditions_particles=["absorbing", "absorbing"],
    )

    n_es = _wx(n_e)
    r_ring_in = _wx(float(o.get("electron_ring_inner_m", 0.01)))
    r_ring_out = _wx(float(o.get("electron_ring_outer_m", 0.03)))
    arc_s = _wx(arc_seed_density)
    r_arc_in = _wx(float(o.get("arc_channel_inner_m", 0.035)))

    _repo = Path(__file__).resolve().parents[2]
    _tools = str(_repo / "tools")
    if _tools not in sys.path:
        sys.path.insert(0, _tools)
    from warpx_expression_presets import PicmiEmitContext, emit_picmi_expressions, validate_expression_bundle

    vb = validate_expression_bundle(o.get("expression_bundle"))
    r_floor_m = float(vb["electron_ring_momentum"]["slots"].get("r_floor_m", 1e-4))
    r_eps = _wx(r_floor_m)
    r_os = float(vb["arc_channel_seed_density"]["slots"].get("r_outer_scale", 0.98))
    r_arc_out_s = _wx(r_anode * r_os)
    ctx = PicmiEmitContext(
        E0s=E0s,
        r_ca=r_ca,
        r_ca2=r_ca2,
        Bys=Bys,
        r_eps=r_eps,
        n_es=n_es,
        r_ring_in=r_ring_in,
        r_ring_out=r_ring_out,
        arc_s=arc_s,
        r_arc_in=r_arc_in,
        r_arc_out=r_arc_out_s,
    )
    xp = emit_picmi_expressions(vb, ctx)

    applied_E = picmi.AnalyticAppliedField(
        Ex_expression=xp["Ex_expression"],
        Ey_expression=xp["Ey_expression"],
        Ez_expression=xp["Ez_expression"],
    )
    applied_B = picmi.AnalyticAppliedField(
        Bx_expression="0.0", By_expression=Bys, Bz_expression="0.0"
    )

    electron_ring = picmi.AnalyticDistribution(
        density_expression=xp["electron_density_expression"],
        momentum_expressions=list(xp["electron_momentum_expressions"]),
    )
    electrons = picmi.Species(
        particle_type="electron", name="electrons", initial_distribution=electron_ring
    )

    arc_seed = picmi.AnalyticDistribution(
        density_expression=xp["arc_density_expression"],
        momentum_expressions=["0.0", "0.0", "0.0"],
    )
    arc_channel_seed = picmi.Species(
        particle_type="electron",
        name="arc_channel_seed",
        initial_distribution=arc_seed,
    )

    bl = o.get("beam_list") or {}
    bx = float(bl.get("x_m", 0.04))
    zhalf = float(bl.get("z_half_span_m", 0.01))
    n_beam = int(bl.get("n_particles", 100))
    ux0 = float(bl.get("ux_m_s", -3e6))
    w0 = float(bl.get("weight", 1e10))
    beam_injector = picmi.ParticleListDistribution(
        x=[bx] * n_beam,
        y=[0.0] * n_beam,
        z=np.linspace(-zhalf, zhalf, n_beam).tolist(),
        ux=[ux0] * n_beam,
        uy=[0.0] * n_beam,
        uz=[0.0] * n_beam,
        weight=[w0] * n_beam,
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

    cfl = float(o.get("cfl", 0.9))
    dt = float(o.get("time_step_size", 1e-12))
    sim = picmi.Simulation(
        solver=picmi.ElectromagneticSolver(grid=grid, cfl=cfl),
        max_steps=n_steps,
        verbose=1,
        time_step_size=dt,
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
    p.add_argument(
        "--overrides",
        type=Path,
        default=None,
        help="JSON with PICMI numeric overrides (from orbitron_physics_surrogate.yaml compiler)",
    )
    args = p.parse_args(argv)

    picmi_overrides: dict[str, Any] | None = None
    if args.overrides is not None:
        picmi_overrides = json.loads(args.overrides.read_text(encoding="utf-8"))

    run_arcjet_picmi(
        throttle=args.throttle,
        compressor=args.compressor,
        write_dir=args.write_dir,
        n_steps=args.steps,
        diag_period=args.diag_period,
        picmi_overrides=picmi_overrides,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
