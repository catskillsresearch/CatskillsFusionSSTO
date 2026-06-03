"""
Generic reactor-simulation scaffolding shared by all three concepts.

This module defines:

* :class:`Grid`          -- uniform 2D grid metadata + coordinate helpers.
* :class:`ControlSpec`   -- declarative slider description for the GUI.
* :class:`StructureLabel`-- a persistent text annotation drawn on the canvas.
* :class:`Diagnostics`   -- rolling time-history buffers for the 1D plots.
* :class:`ReactorSimulation` -- abstract base class managing grid allocation,
  conductor masks, the PIC field-solve backend, the generic step loop, and the
  coupled auxiliary process equations (Bremsstrahlung, ion-electron relaxation,
  fusion power, Q_net).

Concrete reactors (TAE / HB11 / LPP) subclass :class:`ReactorSimulation` and
implement the abstract hooks for geometry, particle seeding, control handling,
and their design-specific physics.
"""
from __future__ import annotations

import abc
from collections import deque
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

from pb11_reactor_sim.engine.particles import ParticleSpecies
from pb11_reactor_sim.engine.poisson import PoissonSolver
from pb11_reactor_sim.physics import processes as P

FloatArray = npt.NDArray[np.float64]
BoolArray = npt.NDArray[np.bool_]


# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Grid:
    """Uniform rectangular 2D grid covering ``[x0, x0+Lx] x [y0, y0+Ly]``."""

    nx: int
    ny: int
    x0: float
    y0: float
    Lx: float
    Ly: float

    @property
    def dx(self) -> float:
        return self.Lx / (self.nx - 1)

    @property
    def dy(self) -> float:
        return self.Ly / (self.ny - 1)

    @property
    def extent(self) -> tuple[float, float, float, float]:
        """``(x_min, x_max, y_min, y_max)`` in metres (for pyqtgraph image rect)."""
        return (self.x0, self.x0 + self.Lx, self.y0, self.y0 + self.Ly)

    def meshgrid(self) -> tuple[FloatArray, FloatArray]:
        """Return ``(X, Y)`` node-coordinate arrays of shape ``(ny, nx)``."""
        xs = np.linspace(self.x0, self.x0 + self.Lx, self.nx)
        ys = np.linspace(self.y0, self.y0 + self.Ly, self.ny)
        return np.meshgrid(xs, ys)

    def zeros(self) -> FloatArray:
        return np.zeros((self.ny, self.nx), dtype=np.float64)


# ---------------------------------------------------------------------------
# GUI control declaration
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ControlSpec:
    """Declarative description of one GUI slider.

    The slider reports a float in ``[minimum, maximum]``; ``key`` is the name
    used in the control dictionary passed to :meth:`ReactorSimulation.apply_controls`.
    """

    key: str
    label: str
    minimum: float
    maximum: float
    default: float
    units: str = ""
    log: bool = False


@dataclass(frozen=True)
class StructureLabel:
    """Persistent text annotation for a structural element on the 2D canvas."""

    text: str
    x: float
    y: float
    color: tuple[int, int, int] = (235, 235, 235)


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
@dataclass
class Diagnostics:
    """Rolling time-history buffers feeding the 1D diagnostic plots."""

    maxlen: int = 2000
    time: deque[float] = field(default_factory=lambda: deque(maxlen=2000))
    T_i: deque[float] = field(default_factory=lambda: deque(maxlen=2000))
    T_e: deque[float] = field(default_factory=lambda: deque(maxlen=2000))
    p_fusion: deque[float] = field(default_factory=lambda: deque(maxlen=2000))
    p_brems: deque[float] = field(default_factory=lambda: deque(maxlen=2000))
    p_cond: deque[float] = field(default_factory=lambda: deque(maxlen=2000))
    q_net: deque[float] = field(default_factory=lambda: deque(maxlen=2000))

    def append(
        self,
        t: float,
        T_i: float,
        T_e: float,
        p_fusion: float,
        p_brems: float,
        p_cond: float,
        q_net: float,
    ) -> None:
        self.time.append(t)
        self.T_i.append(T_i)
        self.T_e.append(T_e)
        self.p_fusion.append(p_fusion)
        self.p_brems.append(p_brems)
        self.p_cond.append(p_cond)
        self.q_net.append(q_net)

    def clear(self) -> None:
        for d in (self.time, self.T_i, self.T_e, self.p_fusion, self.p_brems, self.p_cond, self.q_net):
            d.clear()


# ---------------------------------------------------------------------------
# Abstract reactor simulation
# ---------------------------------------------------------------------------
class ReactorSimulation(abc.ABC):
    """Abstract base managing grid, masks, PIC backend, and the process loop.

    Subclasses must define :attr:`display_name` and implement the abstract
    hooks. The public :meth:`step` and :meth:`reset` methods orchestrate the
    generic loop and should not normally be overridden.
    """

    #: Human-readable name shown in the reactor dropdown.
    display_name: str = "Reactor"
    #: Field shown on the 2D canvas: ``"phi"`` (potential) or ``"bz"`` (B-field).
    display_field_kind: str = "phi"

    def __init__(self, grid: Grid, field_solver: "FieldSolveBackend") -> None:
        self.grid = grid
        self.backend = field_solver
        self.poisson = PoissonSolver(grid.nx, grid.ny, grid.dx, grid.dy)

        # Field storage (ny, nx).
        self.phi: FloatArray = grid.zeros()
        self.ex: FloatArray = grid.zeros()
        self.ey: FloatArray = grid.zeros()
        self.bz: FloatArray = grid.zeros()
        self.rho: FloatArray = grid.zeros()

        # Geometry.
        self.conductor_mask: BoolArray = np.zeros((grid.ny, grid.nx), dtype=bool)
        self.conductor_potential: FloatArray = grid.zeros()
        self.plasma_mask: BoolArray = np.ones((grid.ny, grid.nx), dtype=bool)
        self.labels: list[StructureLabel] = []

        # Particle species keyed by symbol.
        self.species: dict[str, ParticleSpecies] = {}

        # 0D plasma state (scalars), evolved by the energy model.
        self.T_i_keV: float = 50.0
        self.T_e_keV: float = 20.0
        self.n_e: float = 1.0e20
        self.n_p: float = 5.0e19
        self.n_B: float = 5.0e18

        # Control values (filled from defaults).
        self.controls: dict[str, float] = {c.key: c.default for c in self.control_specs()}

        # Diagnostics + bookkeeping.
        self.diagnostics = Diagnostics()
        self.time: float = 0.0
        self.dt: float = self.default_dt()
        self.step_index: int = 0

        # Latest auxiliary power densities [W/m^3] for display / readout.
        self.last_p_fusion: float = 0.0
        self.last_p_brems: float = 0.0
        self.last_p_cond: float = 0.0
        self.last_q_net: float = 0.0

        self.build_geometry()
        self.seed_particles()

    # -- abstract hooks -----------------------------------------------------
    @classmethod
    @abc.abstractmethod
    def control_specs(cls) -> list[ControlSpec]:
        """Return the slider declarations for this reactor."""

    @abc.abstractmethod
    def default_dt(self) -> float:
        """Return the simulation timestep [s]."""

    @abc.abstractmethod
    def build_geometry(self) -> None:
        """Populate conductor mask/potential, plasma mask, and labels."""

    @abc.abstractmethod
    def seed_particles(self) -> None:
        """Create the initial macroparticle populations in :attr:`species`."""

    @abc.abstractmethod
    def advance_particles(self, dt: float) -> None:
        """Advance fields + particles one step (design-specific physics).

        Implementations should use :meth:`solve_fields` for the electrostatic
        solve and the :class:`ParticleSpecies` pushers, then handle boundaries,
        collection, and fusion product creation.
        """

    @abc.abstractmethod
    def update_plasma_state(self, dt: float) -> None:
        """Update the 0D plasma state (``T_i``, ``T_e``, densities) for this step.

        This sets the scalars consumed by :meth:`compute_processes`.
        """

    # -- shared services ----------------------------------------------------
    def solve_fields(self) -> None:
        """Deposit charge, solve for the potential via the active backend, get E."""
        self.rho.fill(0.0)
        for sp in self.species.values():
            sp.deposit_charge(self.rho, self.grid.x0, self.grid.y0, self.grid.dx, self.grid.dy)
        self.phi = self.backend.solve_potential(
            self.rho, self.poisson, self.conductor_mask, self.conductor_potential
        )
        self.ex, self.ey = self.poisson.electric_field(self.phi)

    def compute_processes(self) -> None:
        """Evaluate the coupled auxiliary process equations (Step 1).

        Uses the current 0D plasma state to produce representative core power
        densities and the net gain Q, appending them to diagnostics.
        """
        z_eff = P.z_effective({1: self.n_p, 5: self.n_B}, self.n_e)
        p_brems = float(P.bremsstrahlung_power_density(z_eff, self.n_e, self.T_e_keV))
        p_brems = self.apply_brems_suppression(p_brems)

        p_fusion = float(
            P.fusion_power_density(self.n_p, self.n_B, self.T_i_keV)
        )
        p_cond = float(P.conduction_loss_density(self.n_e, self.T_e_keV, self.energy_confinement_time()))
        q = float(P.q_net(p_fusion, p_brems, p_cond))

        self.last_p_fusion = p_fusion
        self.last_p_brems = p_brems
        self.last_p_cond = p_cond
        self.last_q_net = q

        self.diagnostics.append(
            self.time * 1.0e6,  # display time in microseconds
            self.T_i_keV,
            self.T_e_keV,
            p_fusion,
            p_brems,
            p_cond,
            q,
        )

    # Overridable physics knobs --------------------------------------------
    def energy_confinement_time(self) -> float:
        """Energy confinement time [s] used by the conduction loss term."""
        return 1.0e-3

    def apply_brems_suppression(self, p_brems: float) -> float:
        """Hook for reactor-specific Bremsstrahlung suppression (LPP overrides)."""
        return p_brems

    # -- generic loop -------------------------------------------------------
    def step(self) -> None:
        """Advance the simulation by one timestep (generic orchestration)."""
        self.advance_particles(self.dt)
        self.update_plasma_state(self.dt)
        self.compute_processes()
        self.time += self.dt
        self.step_index += 1

    def reset(self) -> None:
        """Reset particles, fields, plasma state, and diagnostics."""
        self.time = 0.0
        self.step_index = 0
        self.species.clear()
        self.phi = self.grid.zeros()
        self.ex = self.grid.zeros()
        self.ey = self.grid.zeros()
        self.bz = self.grid.zeros()
        self.rho = self.grid.zeros()
        self.diagnostics.clear()
        self.build_geometry()
        self.seed_particles()

    def apply_controls(self, values: dict[str, float]) -> None:
        """Merge new slider values; subclasses may react via :meth:`on_controls`."""
        self.controls.update(values)
        self.on_controls()

    def on_controls(self) -> None:
        """Hook called after controls change (subclasses may rebuild geometry)."""

    # -- display helpers ----------------------------------------------------
    def display_field(self) -> tuple[FloatArray, str]:
        """Return the 2D field to render and its label."""
        if self.display_field_kind == "bz":
            return self.bz, "B_z [T]"
        return self.phi, "Phi [V]"

    def particle_overlay(self) -> dict[str, tuple[FloatArray, FloatArray, tuple[int, int, int]]]:
        """Return ``{symbol: (x, y, rgb)}`` for the scatter overlay."""
        out: dict[str, tuple[FloatArray, FloatArray, tuple[int, int, int]]] = {}
        for sym, sp in self.species.items():
            out[sym] = (sp.x, sp.y, sp.species.color)
        return out


# Backend protocol is imported lazily to avoid a circular import at module load.
from pb11_reactor_sim.engine.pic_backend import FieldSolveBackend  # noqa: E402
