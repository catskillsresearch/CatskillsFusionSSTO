"""
GOAL 2 — 2D Orbitron electron-ring PICMI case (proof-chain step 01).

Default mode (**electron ring only** — proof chain step 01):
  * ring_density_scale (τ)  → initial electron annulus density n_e
  * cathode_pulse (p)       → n_e at t=0 and E-field time ramp α(t, p)
  * No fuel, no compressor, no arc seed, no H⁺/B⁺ inject beams in the deck.

Legacy **full deck** (surrogate sweeps only; ``--full-deck``):
  * compressor → arc_channel_seed density (not used by proof chain step 01)
  * inject beams → tangential H⁺/B⁺ proxies (not plotted in step 01 movie)

CLI examples:
  cd ssto/orbitron && python laminar_flow_2d_arcjet.py --write-dir diags \\
      --ring-density-scale 0.85 --cathode-pulse 0.8

Surrogate sweep driver: tools/build_surrogate_map.py (passes ``--full-deck``).
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
DEFAULT_V_CATHODE_V = -600000.0
INCLUDE_NITROGEN_TRACER = False

# PICMI/WarpX passes non-special ``particle_type`` strings to
# ``periodictable.elements.symbol()`` (expects symbols: H, B, N, …), not full names.
_PICMI_ELEMENT_ALIASES: dict[str, str] = {
    "boron": "B",
    "nitrogen": "N",
    "hydrogen": "H",
    "helium": "He",
    "oxygen": "O",
    "argon": "Ar",
}


def _normalize_picmi_particle_type(ptype: str) -> str:
    """Map human-readable names to periodic symbols for PICMI Species."""
    key = ptype.strip()
    return _PICMI_ELEMENT_ALIASES.get(key.lower(), key)


# Deposited charge density field names (reduction sums these for viewport ROI).
BEAM_RHO_FIELD_NAMES = (
    "rho_h_inject_beam",
    "rho_b_inject_beam",
    "rho_stabilizing_beam",
)


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


def ring_electron_density(
    ring_density_scale: float,
    cathode_pulse: float,
    o: dict[str, Any] | None = None,
) -> float:
    """Initial electron annulus density for species ``electrons`` (step 01 SSOT)."""
    o = o or {}
    tau = max(0.0, min(1.0, float(ring_density_scale)))
    p = max(0.0, min(1.0, float(cathode_pulse)))
    base_ne = float(o.get("base_n_e", BASE_N_E))
    rs = o.get("ring_density_scale") or {"throttle_offset": 0.15, "throttle_gain": 0.85}
    cp = o.get("cathode_pulse_density") or {"offset": 0.65, "gain": 0.35}
    return base_ne * (float(rs["throttle_offset"]) + float(rs["throttle_gain"]) * tau) * (
        float(cp["offset"]) + float(cp["gain"]) * p
    )


def arc_channel_seed_density(
    compressor: float,
    o: dict[str, Any] | None = None,
) -> float:
    """Legacy arc precursor seed — **not** used in proof-chain step 01."""
    o = o or {}
    c = max(0.0, min(1.0, float(compressor)))
    base_arc = float(o.get("base_arc_seed", BASE_ARC_SEED))
    acs = o.get("arc_seed_scale") or {"compressor_offset": 0.15, "compressor_gain": 0.85}
    return base_arc * (float(acs["compressor_offset"]) + float(acs["compressor_gain"]) * c)


def scaled_densities(
    throttle: float,
    compressor: float,
    cathode_pulse: float,
    o: dict[str, Any] | None = None,
) -> tuple[float, float]:
    """Full-deck helper (surrogate sweeps). Prefer ``ring_electron_density`` for step 01."""
    n_e = ring_electron_density(throttle, cathode_pulse, o)
    arc_seed_density = arc_channel_seed_density(compressor, o)
    return n_e, arc_seed_density


def _cathode_ramp_expression(dt_s: float, n_steps: int, cathode_pulse: float, o: dict[str, Any]) -> str:
    """Time multiplier on analytic E (PSP2/Jin-style cathode spin-up proxy)."""
    cp = o.get("cathode_pulse_ramp") or {}
    frac = float(cp.get("ramp_step_fraction", 0.35))
    v_start = float(cp.get("v_start_scale", 0.30))
    v_end = float(cp.get("v_end_scale", 0.88)) + 0.12 * max(0.0, min(1.0, cathode_pulse))
    t_end = max(dt_s, frac * n_steps * dt_s)
    te = _wx(t_end)
    vs = _wx(v_start)
    ve = _wx(v_end)
    return f"(t <= {te}) * ({vs} + ({ve} - {vs}) * t / {te}) + (t > {te}) * {ve}"


def _scaled_field_expr(base_expr: str, ramp_expr: str) -> str:
    b = base_expr.strip()
    if not b:
        return ramp_expr
    return f"({b}) * ({ramp_expr})"


def _inject_beam_configs(o: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Resolve H⁺ / B⁺ tangential injectors from overrides (p-¹¹B Orbitron)."""
    ib = o.get("inject_beams")
    if isinstance(ib, dict) and ib:
        return {str(k): dict(v) for k, v in ib.items()}

    # Legacy single radial proton list → H beam only.
    bl = o.get("beam_list") or {}
    if bl:
        return {
            "h_beam": {
                "x_m": bl.get("x_m", 0.04),
                "z_half_span_m": bl.get("z_half_span_m", 0.01),
                "n_particles": bl.get("n_particles", 100),
                "u_tangential_m_s": float(bl.get("uz_m_s", 3.0e6)),
                "u_radial_m_s": float(bl.get("ux_m_s", -3.0e6)) * 0.15,
                "weight": bl.get("weight", 1.0e10),
                "particle_type": "proton",
                "charge_state": 1,
            }
        }

    return {
        "h_beam": {
            "x_m": 0.04,
            "z_half_span_m": 0.01,
            "n_particles": 60,
            "u_tangential_m_s": 3.0e6,
            "u_radial_m_s": -4.5e5,
            "weight": 5.0e9,
            "particle_type": "proton",
            "charge_state": 1,
        },
        "b_beam": {
            "x_m": 0.041,
            "z_half_span_m": 0.009,
            "n_particles": 40,
            "u_tangential_m_s": -2.8e6,
            "u_radial_m_s": -4.0e5,
            "weight": 8.0e9,
            "particle_type": "B",
            "charge_state": 5,
        },
    }


def _tangential_beam_distribution(
    beam_cfg: dict[str, Any],
    *,
    throttle: float,
    cathode_pulse: float,
) -> picmi.ParticleListDistribution:
    """Tangential keV injectant in the X–Z slice: uz azimuthal, ux slight inward."""
    x = float(beam_cfg["x_m"])
    zhalf = float(beam_cfg.get("z_half_span_m", 0.01))
    n = int(beam_cfg.get("n_particles", 50))
    ut = float(beam_cfg.get("u_tangential_m_s", 3.0e6))
    ur = float(beam_cfg.get("u_radial_m_s", -4.5e5))
    w0 = float(beam_cfg.get("weight", 5.0e9))
    t = max(0.0, min(1.0, throttle))
    p = max(0.0, min(1.0, cathode_pulse))
    w = w0 * (0.2 + 0.8 * t) * (0.5 + 0.5 * p)
    z = np.linspace(-zhalf, zhalf, max(n, 2))
    nn = len(z)
    return picmi.ParticleListDistribution(
        x=[x] * nn,
        y=[0.0] * nn,
        z=z.tolist(),
        ux=[ur] * nn,
        uy=[0.0] * nn,
        uz=[ut] * nn,
        weight=[w] * nn,
    )


def _make_inject_species(
    name: str,
    beam_cfg: dict[str, Any],
    *,
    throttle: float,
    cathode_pulse: float,
) -> picmi.Species:
    ptype = _normalize_picmi_particle_type(str(beam_cfg.get("particle_type", "proton")))
    charge_state = int(beam_cfg.get("charge_state", 1))
    dist = _tangential_beam_distribution(beam_cfg, throttle=throttle, cathode_pulse=cathode_pulse)
    return picmi.Species(
        particle_type=ptype,
        name=name,
        charge_state=charge_state,
        initial_distribution=dist,
    )


def run_arcjet_picmi(
    *,
    ring_density_scale: float,
    cathode_pulse: float,
    write_dir: str,
    n_steps: int,
    diag_period: int,
    picmi_overrides: dict[str, Any] | None = None,
    full_deck: bool = False,
    compressor: float = 0.0,
) -> None:
    o = picmi_overrides or {}
    n_e = ring_electron_density(ring_density_scale, cathode_pulse, o)
    arc_seed_density = arc_channel_seed_density(compressor, o) if full_deck else 0.0

    print("==================================================")
    print("  ORBITRON 2D ELECTRON RING (PICMI)             ")
    print(
        f"  ring_density_scale={ring_density_scale:g}  cathode_pulse={cathode_pulse:g}"
    )
    if full_deck:
        print(f"  full_deck=1  compressor={compressor:g}  arc_seed={arc_seed_density:g}")
    else:
        print("  full_deck=0  (no arc seed, no inject beams)")
    print(f"  n_e={n_e:g}")
    print(f"  write_dir={write_dir}")
    print("==================================================")

    r_anode = float(o.get("r_anode_m", o.get("domain_half_extent_m", 0.05)))
    r_cathode = float(o.get("r_cathode_m", 0.005))
    V_cathode = float(o.get("V_cathode_v", DEFAULT_V_CATHODE_V))
    B_axial = float(o.get("B_axial_tesla", 2.0))
    E0 = -(V_cathode / math.log(r_anode / r_cathode))
    r_ca = _wx(r_cathode)
    r_ca2 = _wx(r_cathode * r_cathode)
    E0s = _wx(E0)
    Bys = _wx(B_axial)

    n_cells = o.get("number_of_cells") or [256, 256]
    _repo_root = Path(__file__).resolve().parents[2]
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))
    from tools.orbitron_proof_chain.chain_lib import align_pic_grid_cells

    nx = align_pic_grid_cells(int(n_cells[0]))
    nz = align_pic_grid_cells(int(n_cells[1]))
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
    _repo = Path(__file__).resolve().parents[2]
    _tools = str(_repo / "tools")
    if _tools not in sys.path:
        sys.path.insert(0, _tools)
    from warpx_expression_presets import PicmiEmitContext, emit_picmi_expressions, validate_expression_bundle

    vb = validate_expression_bundle(o.get("expression_bundle"))
    r_floor_m = float(vb["electron_ring_momentum"]["slots"].get("r_floor_m", 1e-4))
    r_eps = _wx(r_floor_m)
    ctx = PicmiEmitContext(
        E0s=E0s,
        r_ca=r_ca,
        r_ca2=r_ca2,
        Bys=Bys,
        r_eps=r_eps,
        n_es=n_es,
        r_ring_in=r_ring_in,
        r_ring_out=r_ring_out,
        arc_s="0.0",
        r_arc_in="0.0",
        r_arc_out="0.0",
    )
    if full_deck:
        arc_s = _wx(arc_seed_density)
        r_arc_in = _wx(float(o.get("arc_channel_inner_m", 0.035)))
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

    dt_s = float(o.get("time_step_size", 1e-12))
    ramp_expr = _cathode_ramp_expression(dt_s, n_steps, cathode_pulse, o)

    applied_E = picmi.AnalyticAppliedField(
        Ex_expression=_scaled_field_expr(xp["Ex_expression"], ramp_expr),
        Ey_expression=_scaled_field_expr(xp.get("Ey_expression", "0.0"), ramp_expr),
        Ez_expression=_scaled_field_expr(xp["Ez_expression"], ramp_expr),
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

    species_list: list[tuple[picmi.Species, picmi.ParticleLayout | None]] = [
        (electrons, picmi.GriddedLayout(n_macroparticle_per_cell=[4, 4], grid=grid)),
    ]
    beam_rho_names: list[str] = []
    if full_deck:
        arc_seed = picmi.AnalyticDistribution(
            density_expression=xp["arc_density_expression"],
            momentum_expressions=["0.0", "0.0", "0.0"],
        )
        arc_channel_seed = picmi.Species(
            particle_type="electron",
            name="arc_channel_seed",
            initial_distribution=arc_seed,
        )
        species_list.append(
            (
                arc_channel_seed,
                picmi.GriddedLayout(n_macroparticle_per_cell=[2, 2], grid=grid),
            )
        )
        inject_cfgs = _inject_beam_configs(o)
        for key, cfg in inject_cfgs.items():
            if key.startswith("h"):
                sname = "h_inject_beam"
            elif key.startswith("b"):
                sname = "b_inject_beam"
            else:
                sname = f"{key}_inject_beam"
            spec = _make_inject_species(
                sname,
                cfg,
                throttle=ring_density_scale,
                cathode_pulse=cathode_pulse,
            )
            species_list.append((spec, None))
            beam_rho_names.append(f"rho_{sname}")

    if INCLUDE_NITROGEN_TRACER:
        n_ion = 1e13
        n2_tracer = picmi.AnalyticDistribution(
            density_expression=(
                f"{n_ion} * (sqrt(x*x + z*z) > 0.02) * (sqrt(x*x + z*z) < 0.045)"
            ),
            momentum_expressions=["0.0", "0.0", "0.0"],
        )
        nitrogen_tracer = picmi.Species(
            particle_type="N",
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
    sim = picmi.Simulation(
        solver=picmi.ElectromagneticSolver(grid=grid, cfl=cfl),
        max_steps=n_steps,
        verbose=1,
        time_step_size=dt_s,
    )

    sim.add_applied_field(applied_E)
    sim.add_applied_field(applied_B)

    for spec, layout in species_list:
        sim.add_species(spec, layout=layout)

    data_list = ["rho_electrons"]
    if full_deck:
        data_list.extend(["rho_arc_channel_seed", *beam_rho_names])
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

    if full_deck:
        print(
            "Running full-deck Orbitron slice: arc seed + inject beams + E×B ring..."
        )
    else:
        print("Running electron-ring PIC: prescribed E×B, cathode V ramp (no fuel species)...")
    sim.step(n_steps)
    print("Complete.")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Orbitron 2D electron-ring PICMI (WarpX)")
    p.add_argument(
        "--ring-density-scale",
        "--throttle",
        dest="ring_density_scale",
        type=float,
        default=1.0,
        help="0..1 initial electron annulus density scale (τ)",
    )
    p.add_argument(
        "--cathode-pulse",
        type=float,
        default=None,
        help="0..1 cathode pulse / shear (default: 0.35 + 0.65×ring_density_scale)",
    )
    p.add_argument(
        "--full-deck",
        action="store_true",
        help="Legacy surrogate mode: arc seed + H⁺/B⁺ inject beams (not proof-chain step 01)",
    )
    p.add_argument(
        "--compressor",
        type=float,
        default=1.0,
        help="0..1 arc seed scale (only with --full-deck)",
    )
    p.add_argument("--write-dir", type=str, default="diags", help="WarpX diagnostic output directory")
    p.add_argument("--steps", type=int, default=400)
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

    cathode_pulse = args.cathode_pulse
    if cathode_pulse is None:
        cathode_pulse = 0.35 + 0.65 * max(0.0, min(1.0, args.ring_density_scale))

    run_arcjet_picmi(
        ring_density_scale=args.ring_density_scale,
        cathode_pulse=cathode_pulse,
        write_dir=args.write_dir,
        n_steps=args.steps,
        diag_period=args.diag_period,
        picmi_overrides=picmi_overrides,
        full_deck=args.full_deck,
        compressor=args.compressor,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
