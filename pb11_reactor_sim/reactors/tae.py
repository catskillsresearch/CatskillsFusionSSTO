"""
TAE Technologies Field-Reversed Configuration (FRC) core model.

2D XY slice through a cylindrical confinement chamber. ``x`` is the machine
axis (axial), ``y`` is the radial-like coordinate across the field-reversal
plane. The chamber is bounded by a solid conducting wall; the interior holds the
FRC plasma. An Inverse Cyclotron Converter (ICC) collector sits at the +x end,
where escaping alpha particles cross segmented electrodes and induce an AC
signal.

Design physics
--------------
* FRC axial field profile:        ``B_z(y) = B0 * tanh(y / y_s)``
* FRC density profile:            ``n(y)   = n0 * sech^2(y / y_s)``
* ICC induction: alphas streaming axially past segmented electrodes induce an
  alternating current as the image charge moves segment to segment.

Controls: Neutral Beam Injection (NBI) current and background field ``B0``.
"""
from __future__ import annotations

import numpy as np

from pb11_reactor_sim.engine.base import (
    BoundaryShape,
    ControlSpec,
    Grid,
    ReactorSimulation,
    StructureLabel,
)
from pb11_reactor_sim.engine.shot_sequence import FirePhase, ShotOps
from pb11_reactor_sim.engine.particles import ParticleSpecies
from pb11_reactor_sim.physics import constants as C
from pb11_reactor_sim.physics import processes as P

_RNG = np.random.default_rng(7)


class TAEReactor(ReactorSimulation):
    """Field-reversed configuration with neutral-beam drive and an ICC collector."""

    display_name = "TAE FRC"
    display_field_kind = "bz"

    #: FRC scale length [m] (separatrix half-width).
    Y_S = 0.12
    #: Number of ICC collector electrode segments.
    N_SEGMENTS = 8

    def __init__(self, grid: Grid | None = None, field_solver=None) -> None:
        if grid is None:
            grid = Grid(nx=181, ny=121, x0=-0.6, y0=-0.4, Lx=1.2, Ly=0.8)
        if field_solver is None:
            from pb11_reactor_sim.engine.pic_backend import make_backend

            field_solver = make_backend()
        # ICC running phase accumulator and induced-signal history.
        self._icc_phase = 0.0
        self.icc_signal: float = 0.0
        self._b_scale: float = 0.0
        self._nbi_scale: float = 0.0
        super().__init__(grid, field_solver)

    # -- declarations -------------------------------------------------------
    @classmethod
    def control_specs(cls) -> list[ControlSpec]:
        return [
            ControlSpec("nbi_current", "NBI Current", 0.0, 120.0, 40.0, units="A"),
            ControlSpec("b0", "Background B0", 0.1, 5.0, 1.5, units="T"),
        ]

    def default_dt(self) -> float:
        return 2.0e-9  # 2 ns

    @classmethod
    def shot_ops(cls) -> ShotOps:
        return ShotOps(
            requires_rearm_between_shots=False,
            arm_callout="ARMED — vacuum pumped, gas puffed, coils standby.",
            fire_phases=(
                FirePhase("gas_fill", 0.8e-6, "T−5 s: Gas fill / fuel inventory"),
                FirePhase("field_ramp", 2.0e-6, "T−3 s: Coil ramp — B_z rising"),
                FirePhase("formation", 3.0e-6, "T−2 s: FRC formation — plasma appears"),
                FirePhase("nbi_heat", 4.0e-6, "T−1 s: NBI on — beam heating"),
                FirePhase("flat_top", 25.0e-6, "T−0: FLAT-TOP — discharge"),
                FirePhase("ramp_down", 4.0e-6, "Ramp-down — beams off, field falling"),
            ),
            refire_phases=(
                FirePhase("field_ramp", 1.5e-6, "Re-ramp — field restore"),
                FirePhase("nbi_heat", 3.0e-6, "NBI on — re-heat"),
                FirePhase("flat_top", 20.0e-6, "FLAT-TOP — repeat discharge"),
                FirePhase("ramp_down", 3.0e-6, "Ramp-down"),
            ),
            quiescent_callout="Quiescent — FRC decaying (Fire again without re-Arm).",
        )

    def enter_unarmed(self) -> None:
        self.species.clear()
        self._b_scale = 0.0
        self._nbi_scale = 0.0
        self.T_i_keV = 0.05
        self.T_e_keV = 0.05
        self.n_e = 1.0e16
        self.n_p = 5.0e15
        self.n_B = 5.0e14
        self.icc_signal = 0.0
        self.bz = self.grid.zeros()

    def enter_armed(self) -> None:
        self._b_scale = 0.12
        self._nbi_scale = 0.0
        self.T_i_keV = 0.2
        self.T_e_keV = 0.15
        self.n_e = 5.0e18
        self.n_p = 2.0e18
        self.n_B = 3.0e17
        self.icc_signal = 0.0
        self._update_bz_field()

    def enter_quiescent(self) -> None:
        self._nbi_scale = 0.0
        self._b_scale = max(self._b_scale * 0.35, 0.08)
        self._update_bz_field()

    def on_fire_phase_begin(self, phase_key: str) -> None:
        if phase_key == "formation" and not self.species:
            self.seed_particles()

    def on_fire_phase_tick(self, phase_key: str, dt: float) -> None:
        if phase_key == "gas_fill":
            self.n_e = min(self.n_e * (1.0 + dt / 1.0e-6), 8.0e18)
        elif phase_key == "field_ramp":
            self._b_scale = min(self._b_scale + dt / 5.0e-6, 1.0)
            self._update_bz_field()
        elif phase_key == "formation":
            self._b_scale = min(self._b_scale + dt / 8.0e-6, 0.85)
            self._update_bz_field()
            if self.species and self.species["p"].count < 400:
                self.seed_particles()
        elif phase_key == "nbi_heat":
            self._nbi_scale = min(self._nbi_scale + dt / 12.0e-6, 1.0)
            self._b_scale = 1.0
            self._update_bz_field()
        elif phase_key in ("flat_top",):
            self._b_scale = 1.0
            self._nbi_scale = 1.0
            self._update_bz_field()
        elif phase_key == "ramp_down":
            self._nbi_scale = max(self._nbi_scale - dt / 8.0e-6, 0.0)
            self._b_scale = max(self._b_scale - dt / 10.0e-6, 0.15)
            self._update_bz_field()
        elif phase_key == "quiescent":
            self._b_scale = max(self._b_scale - dt / 25.0e-6, 0.05)
            self.T_i_keV = max(self.T_i_keV - dt / 8.0e-6, 0.5)
            self.T_e_keV = max(self.T_e_keV - dt / 5.0e-6, 0.2)
            self._update_bz_field()
            self._drain_particles(dt)

    def _update_bz_field(self) -> None:
        _, Y = self.grid.meshgrid()
        b0 = self.controls.get("b0", 1.5) * self._b_scale
        self.bz = b0 * np.tanh(Y / self.Y_S)

    def _drain_particles(self, dt: float) -> None:
        for sp in self.species.values():
            if sp.count == 0:
                continue
            if sp.count > 200 and _RNG.random() < dt / 2.0e-5:
                drop = _RNG.choice(sp.count, min(40, sp.count // 8), replace=False)
                keep = np.ones(sp.count, dtype=bool)
                keep[drop] = False
                sp.keep(keep)

    # -- geometry -----------------------------------------------------------
    def build_geometry(self) -> None:
        g = self.grid
        X, Y = g.meshgrid()
        self.conductor_mask = np.zeros((g.ny, g.nx), dtype=bool)
        self.conductor_potential = g.zeros()

        # Solid cylindrical wall: a thin conducting border around the chamber.
        border = 3
        self.conductor_mask[:border, :] = True
        self.conductor_mask[-border:, :] = True
        self.conductor_mask[:, :border] = True

        # ICC segmented collector electrodes at the +x end (right edge).
        seg_h = g.ny // self.N_SEGMENTS
        for s in range(self.N_SEGMENTS):
            y0 = s * seg_h
            y1 = g.ny if s == self.N_SEGMENTS - 1 else (s + 1) * seg_h
            self.conductor_mask[y0:y1, -border:] = True

        # Plasma occupies the interior.
        self.plasma_mask = ~self.conductor_mask

        self._update_bz_field()

        y_top = g.y0 + g.Ly - 0.02
        y_bot = g.y0 + 0.02
        x_left = g.x0 + 0.02
        x_icc = g.x0 + g.Lx - 0.04
        wall_c = (150, 210, 255)
        icc_c = (170, 200, 255)
        self.boundaries = [
            BoundaryShape("line", (x_left, y_top, x_icc, y_top), wall_c),
            BoundaryShape("line", (x_left, y_bot, x_icc, y_bot), wall_c),
            BoundaryShape("line", (x_left, y_bot, x_left, y_top), wall_c),
            BoundaryShape("line", (x_icc, y_bot, x_icc, y_top), icc_c),
        ]
        self.labels = [
            StructureLabel("Cylindrical Conducting Wall", x_left + 0.02, y_top - 0.025,
                           wall_c, angle=0.0, anchor=(0.0, 0.5)),
            StructureLabel("ICC Segmented Collector", x_icc - 0.018, 0.0,
                           icc_c, angle=90.0, anchor=(0.5, 0.5)),
            StructureLabel("Field Reversal Plane (B_z = 0)", -0.02, 0.012,
                           (210, 255, 210), angle=0.0, anchor=(0.0, 0.5)),
            StructureLabel("FRC Plasma (field-reversed core)", -0.02, -0.03,
                           (255, 190, 140), angle=0.0, anchor=(0.0, 0.5)),
        ]

    # -- particles ----------------------------------------------------------
    def _density_profile_y(self, n: int) -> np.ndarray:
        """Sample ``n`` radial positions from a ``sech^2`` FRC density profile."""
        # sech^2 is well approximated for sampling by a normal of width ~ y_s.
        y = _RNG.normal(0.0, self.Y_S, size=n)
        return np.clip(y, self.grid.y0 + 0.02, self.grid.y0 + self.grid.Ly - 0.02)

    def _thermal_velocity(self, T_keV: float, mass: float) -> float:
        return float(np.sqrt(T_keV * C.KEV_TO_JOULE / mass))

    def seed_particles(self) -> None:
        g = self.grid
        n_ions = 1500
        n_elec = 1500
        xs = _RNG.uniform(g.x0 + 0.05, g.x0 + g.Lx - 0.30, size=n_ions)

        def maxwellian(n: int, T: float, mass: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            vth = self._thermal_velocity(T, mass)
            return (
                _RNG.normal(0.0, vth, n),
                _RNG.normal(0.0, vth, n),
                _RNG.normal(0.0, vth, n),
            )

        protons = ParticleSpecies(C.PROTON, macro_weight=1.0e12)
        vx, vy, vz = maxwellian(n_ions, self.T_i_keV, C.PROTON.mass)
        protons.spawn(xs, self._density_profile_y(n_ions), vx, vy, vz)

        boron = ParticleSpecies(C.BORON11, macro_weight=1.0e11)
        nb = n_ions // 4
        vx, vy, vz = maxwellian(nb, self.T_i_keV, C.BORON11.mass)
        boron.spawn(
            _RNG.uniform(g.x0 + 0.05, g.x0 + g.Lx - 0.30, nb),
            self._density_profile_y(nb),
            vx, vy, vz,
        )

        electrons = ParticleSpecies(C.ELECTRON, macro_weight=1.0e12)
        vx, vy, vz = maxwellian(n_elec, self.T_e_keV, C.ELECTRON.mass)
        electrons.spawn(
            _RNG.uniform(g.x0 + 0.05, g.x0 + g.Lx - 0.30, n_elec),
            self._density_profile_y(n_elec),
            vx, vy, vz,
        )

        alphas = ParticleSpecies(C.ALPHA, macro_weight=1.0e10)

        self.species = {"p": protons, "B": boron, "e": electrons, "alpha": alphas}

    # -- dynamics -----------------------------------------------------------
    def on_controls(self) -> None:
        self._update_bz_field()

    def display_field_levels(self) -> tuple[float, float]:
        """Symmetric limits so the FRC reversal plane stays at the colour-map centre."""
        b0 = float(self.controls.get("b0", 1.5))
        return (-b0, b0)

    def advance_particles(self, dt: float) -> None:
        g = self.grid
        # Magnetized push: gather the FRC B_z at particle positions, no in-plane E.
        for sym, sp in self.species.items():
            if sp.count == 0:
                continue
            bz_p = sp.gather_scalar(self.bz, g.x0, g.y0, g.dx, g.dy)
            sp.push_boris(np.zeros(sp.count), np.zeros(sp.count), bz_p, dt)

        # Alphas stream axially toward the ICC collector (+x drift).
        alpha = self.species["alpha"]
        if alpha.count:
            alpha.x = alpha.x + 0.0  # position already advanced by Boris
        self._reflect_and_collect(dt)
        self._inject_nbi(dt)
        self._fusion_alpha_production(dt)
        self._update_icc_signal(dt)
        # Keep the electrostatic field current for completeness / display option.
        self.solve_fields()

    def _reflect_and_collect(self, dt: float) -> None:
        g = self.grid
        x_min, x_max = g.x0 + g.dx, g.x0 + g.Lx - g.dx
        y_min, y_max = g.y0 + g.dy, g.y0 + g.Ly - g.dy
        collector_x = g.x0 + g.Lx - 0.04
        for sym, sp in self.species.items():
            if sp.count == 0:
                continue
            # Reflect at radial walls (specular).
            below = sp.y < y_min
            above = sp.y > y_max
            sp.vy[below | above] *= -1.0
            sp.y = np.clip(sp.y, y_min, y_max)
            # Axial: reflect at -x wall, collect alphas at +x ICC.
            left = sp.x < x_min
            sp.vx[left] *= -1.0
            sp.x = np.maximum(sp.x, x_min)
            if sym == "alpha":
                collected = sp.x >= collector_x
                if np.any(collected):
                    # Induced ICC signal proportional to collected axial momentum.
                    self.icc_signal += float(np.sum(np.abs(sp.vx[collected]))) * 1.0e-9
                    sp.keep(~collected)
            else:
                right = sp.x > x_max
                sp.vx[right] *= -1.0
                sp.x = np.minimum(sp.x, x_max)

    def _inject_nbi(self, dt: float) -> None:
        if self._nbi_scale <= 0.0:
            return
        """Neutral-beam injection: add fast protons proportional to NBI current."""
        i_nbi = self.controls.get("nbi_current", 40.0) * self._nbi_scale
        # Number of macroparticles injected this step scales with current.
        n_new = int(i_nbi * 0.05)
        if n_new <= 0:
            return
        g = self.grid
        protons = self.species["p"]
        x = _RNG.uniform(g.x0 + 0.05, g.x0 + 0.15, n_new)
        y = _RNG.normal(0.0, self.Y_S, n_new)
        # Beam directed inward (+x) and fast (tangential drive).
        v_beam = 1.2e6 + 5.0e3 * i_nbi
        vx = np.full(n_new, v_beam)
        vy = _RNG.normal(0.0, 2.0e5, n_new)
        vz = _RNG.normal(0.0, 2.0e5, n_new)
        protons.spawn(x, np.clip(y, g.y0 + 0.02, g.y0 + g.Ly - 0.02), vx, vy, vz)
        # Cap population to keep the GUI fast.
        self._cap_population("p", 4000)

    def _cap_population(self, sym: str, cap: int) -> None:
        sp = self.species[sym]
        if sp.count > cap:
            keep = _RNG.choice(sp.count, cap, replace=False)
            mask = np.zeros(sp.count, dtype=bool)
            mask[keep] = True
            sp.keep(mask)

    def _fusion_alpha_production(self, dt: float) -> None:
        """Spawn alpha macroparticles at a rate set by the fusion power density."""
        if not self.shot_physics_enabled:
            return
        rate = self.last_p_fusion
        n_new = int(min(20, rate * 1.0e-4))
        if n_new <= 0:
            return
        g = self.grid
        alpha = self.species["alpha"]
        x = _RNG.uniform(-0.1, 0.1, n_new)
        y = _RNG.normal(0.0, self.Y_S * 0.5, n_new)
        # Born-alpha speeds from the real p-11B spectrum (alpha0/alpha1 branches),
        # streaming axially toward the +x ICC collector.
        speed = P.alpha_speeds_from_energies(P.sample_alpha_energies_J(n_new, _RNG))
        theta = _RNG.normal(0.0, 0.25, n_new)  # narrow forward (+x) cone
        vx = speed * np.cos(theta)
        vy = speed * np.sin(theta)
        alpha.spawn(x, np.clip(y, g.y0 + 0.02, g.y0 + g.Ly - 0.02), vx, vy, np.zeros(n_new))
        self._cap_population("alpha", 1500)

    def _update_icc_signal(self, dt: float) -> None:
        """Model the AC pickup as the collected charge crosses segment boundaries."""
        i_nbi = self.controls.get("nbi_current", 40.0)
        self._icc_phase += 2.0 * np.pi * (1.0e6 + 2.0e4 * i_nbi) * dt
        # Decay the accumulated charge signal and impose AC modulation.
        self.icc_signal *= 0.97
        self.icc_signal += 0.01 * np.sin(self._icc_phase)

    def update_plasma_state(self, dt: float) -> None:
        i_nbi = self.controls.get("nbi_current", 40.0)
        b0 = self.controls.get("b0", 1.5)
        # Ion temperature rises with NBI drive and confinement (B0), relaxes slowly.
        t_target = 80.0 + 2.0 * i_nbi + 30.0 * b0
        self.T_i_keV += (t_target - self.T_i_keV) * min(1.0, dt / 5.0e-7)
        # Electrons heated by ion-electron collisions; kept cooler (non-thermal FRC).
        self.T_e_keV += (0.35 * self.T_i_keV - self.T_e_keV) * min(1.0, dt / 1.0e-6)
        # Peak densities scale weakly with confinement.
        self.n_e = 3.0e20 * (0.6 + 0.4 * b0 / 5.0)
        self.n_p = 0.55 * self.n_e
        self.n_B = 0.09 * self.n_e

    def energy_confinement_time(self) -> float:
        # Better confinement at higher B0.
        return 5.0e-4 * (0.5 + self.controls.get("b0", 1.5) / 5.0)
