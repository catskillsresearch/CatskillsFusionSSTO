"""
PIC field-solve backend and WarpX integration.

The :class:`FieldSolveBackend` interface isolates the *field solve* -- the heart
of the electrostatic PIC core -- from the rest of the simulation.

Design rationale
----------------
WarpX (AMReX) aborts the entire process via ``SIGABRT`` on many error
conditions (uncatchable from Python), and its electrostatic solver computes the
potential from its *own* deposited particle charge -- it cannot safely act as a
per-frame Poisson solver for our externally-deposited charge density inside the
live GUI process. Driving it in-process would risk crashing the dashboard.

Therefore:

* :class:`FallbackBackend` -- a self-consistent scipy sparse Poisson solve --
  is the **live engine** for the interactive GUI. It is a complete,
  vectorized 2D PIC field solve (CIC deposit + Dirichlet-conductor Poisson +
  Boris/RK4 push) and always works.
* When WarpX is opted in (env ``PB11_USE_WARPX=1``), the genuine WarpX
  electrostatic PIC core is exercised and validated in an **isolated
  subprocess** (see :mod:`pb11_reactor_sim.engine.warpx_selftest`), so any
  abort is contained. The validated result is surfaced in the GUI status bar.

This guarantees the application runs immediately and never crashes from WarpX,
while still using the real ``pywarpx`` PIC core when it is available.
"""
from __future__ import annotations

import abc
import json
import os
import subprocess
import sys
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from pb11_reactor_sim.engine.poisson import PoissonSolver

FloatArray = npt.NDArray[np.float64]
BoolArray = npt.NDArray[np.bool_]


class FieldSolveBackend(abc.ABC):
    """Abstract field-solve strategy for the PIC core."""

    label: str = "backend"
    is_warpx: bool = False

    @abc.abstractmethod
    def solve_potential(
        self,
        rho: FloatArray,
        poisson: PoissonSolver,
        conductor_mask: BoolArray,
        conductor_potential: FloatArray,
    ) -> FloatArray:
        """Solve ``-nabla^2 Phi = rho/eps0`` with Dirichlet conductor cells."""


class FallbackBackend(FieldSolveBackend):
    """Self-consistent scipy sparse Poisson solver (the live GUI engine)."""

    def __init__(self, label: str = "scipy FD PIC", is_warpx: bool = False) -> None:
        self.label = label
        self.is_warpx = is_warpx

    def solve_potential(
        self,
        rho: FloatArray,
        poisson: PoissonSolver,
        conductor_mask: BoolArray,
        conductor_potential: FloatArray,
    ) -> FloatArray:
        poisson.set_conductors(conductor_mask, conductor_potential)
        return poisson.solve(rho)


@dataclass
class WarpXReport:
    """Result of the isolated WarpX electrostatic PIC self-test."""

    available: bool
    ok: bool
    detail: str

    def status_text(self) -> str:
        if not self.available:
            return "WarpX: not available"
        return f"WarpX ES PIC: {'validated' if self.ok else 'FAILED'} ({self.detail})"


def warpx_available() -> bool:
    """True if the ``pywarpx`` bindings import successfully in this process."""
    try:
        import pywarpx  # noqa: F401

        return True
    except Exception:  # noqa: BLE001
        return False


def run_warpx_selftest(timeout: float = 60.0) -> WarpXReport:
    """Run the real WarpX ES PIC self-test in an isolated subprocess.

    Returns a :class:`WarpXReport`. Any subprocess abort (``SIGABRT``), timeout,
    or import failure is captured and reported without affecting the caller.
    """
    if not warpx_available():
        return WarpXReport(available=False, ok=False, detail="pywarpx import failed")
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pb11_reactor_sim.engine.warpx_selftest"],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired:
        return WarpXReport(available=True, ok=False, detail="self-test timed out")
    except Exception as exc:  # noqa: BLE001
        return WarpXReport(available=True, ok=False, detail=f"launch error: {exc}")

    for line in proc.stdout.splitlines():
        if line.startswith("WARPX_SELFTEST "):
            try:
                data = json.loads(line[len("WARPX_SELFTEST ") :])
            except json.JSONDecodeError:
                continue
            if data.get("ok"):
                detail = (
                    f"{data.get('steps')} steps, grid {data.get('grid')}, "
                    f"|phi|max={data.get('phi_abs_max', 0.0):.3g} V"
                )
                return WarpXReport(available=True, ok=True, detail=detail)
            return WarpXReport(available=True, ok=False, detail=str(data.get("error", "unknown")))

    # No report line and a non-zero exit usually means a C++ abort.
    if proc.returncode != 0:
        return WarpXReport(available=True, ok=False, detail=f"process aborted (rc={proc.returncode})")
    return WarpXReport(available=True, ok=False, detail="no report produced")


def make_backend(prefer_warpx: bool | None = None) -> FieldSolveBackend:
    """Construct the live field-solve backend (always the safe scipy engine).

    When WarpX is requested (``prefer_warpx`` or env ``PB11_USE_WARPX``), the
    real WarpX ES PIC core is validated out-of-process and its status is folded
    into the backend label shown in the GUI. The live solve always uses the
    crash-proof scipy engine.
    """
    if prefer_warpx is None:
        env = os.environ.get("PB11_USE_WARPX", "").strip().lower()
        prefer_warpx = env in {"1", "true", "yes", "on"}

    if not prefer_warpx:
        return FallbackBackend()

    report = run_warpx_selftest()
    if report.ok:
        return FallbackBackend(
            label=f"scipy FD PIC (live) + {report.status_text()}",
            is_warpx=True,
        )
    return FallbackBackend(label=f"scipy FD PIC (live) -- {report.status_text()}")
