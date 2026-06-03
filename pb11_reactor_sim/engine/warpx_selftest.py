"""
Real WarpX electrostatic PIC self-test, run in an isolated subprocess.

WarpX (AMReX) aborts the *entire process* via ``SIGABRT`` on many error
conditions, and its electrostatic solver derives the potential from its own
deposited particle charge -- it is therefore unsafe and semantically wrong to
drive it as a per-frame Poisson solver for externally-deposited charge inside
the live GUI process.

Instead, this module runs a genuine, self-contained WarpX 2D electrostatic PIC
simulation (real AMReX MLMG Poisson solve + Boris particle push) for a handful
of steps and prints a one-line JSON report. The GUI launches it in a *separate*
process via :func:`run_warpx_selftest`, so any abort is fully contained and the
dashboard keeps running on the scipy engine.

Run directly with::

    python -m pb11_reactor_sim.engine.warpx_selftest
"""
from __future__ import annotations

import json
import sys


def run(nx: int = 64, ny: int = 64, steps: int = 8) -> dict[str, object]:
    """Build and step a real WarpX 2D electrostatic PIC; return a report dict."""
    import numpy as np
    from pywarpx import fields, picmi

    constants = picmi.constants

    grid = picmi.Cartesian2DGrid(
        number_of_cells=[nx, ny],
        lower_bound=[-0.1, -0.1],
        upper_bound=[0.1, 0.1],
        lower_boundary_conditions=["dirichlet", "dirichlet"],
        upper_boundary_conditions=["dirichlet", "dirichlet"],
        lower_boundary_conditions_particles=["absorbing", "absorbing"],
        upper_boundary_conditions_particles=["absorbing", "absorbing"],
        warpx_blocking_factor=1,
        warpx_max_grid_size=128,
    )
    solver = picmi.ElectrostaticSolver(grid=grid, required_precision=1e-6)

    uniform_plasma = picmi.UniformDistribution(
        density=1.0e18,
        rms_velocity=[0.01 * constants.c] * 3,
    )
    electrons = picmi.Species(
        particle_type="electron",
        name="electrons",
        initial_distribution=uniform_plasma,
    )
    protons = picmi.Species(
        particle_type="proton",
        name="protons",
        initial_distribution=uniform_plasma,
    )
    layout = picmi.PseudoRandomLayout(n_macroparticles_per_cell=4, grid=grid)

    sim = picmi.Simulation(solver=solver, time_step_size=1.0e-12, max_steps=steps, verbose=0)
    sim.add_species(electrons, layout=layout)
    sim.add_species(protons, layout=layout)
    sim.initialize_inputs()
    sim.initialize_warpx()

    sim.step(steps)

    phi = np.asarray(fields.PhiFPWrapper(level=0)[...])
    report = {
        "ok": bool(np.all(np.isfinite(phi))),
        "steps": int(steps),
        "grid": [int(nx), int(ny)],
        "phi_shape": list(phi.shape),
        "phi_abs_max": float(np.max(np.abs(phi))),
    }
    return report


def main() -> int:
    try:
        report = run()
        sys.stdout.write("WARPX_SELFTEST " + json.dumps(report) + "\n")
        sys.stdout.flush()
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write("WARPX_SELFTEST " + json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}) + "\n")
        sys.stdout.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
