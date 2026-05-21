"""Cached WarpX PIC frame stack for Device overlay + Longitudinal 2D scrubber."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ssto.orbitron.simulator.longitudinal.warpx_frames import PicFrameStack, load_warpx_density_frames
from ssto.orbitron.simulator.longitudinal.focus import FocusDomain


@dataclass
class PicSession:
    """Last successful WarpX reduction loaded into memory."""

    stack: PicFrameStack | None = None
    diags_dir: Path | None = None
    frame_index: int = 0
    meta: dict = field(default_factory=dict)

    @property
    def available(self) -> bool:
        return self.stack is not None and self.stack.rho_e.size > 0

    @property
    def n_frames(self) -> int:
        if not self.available:
            return 0
        assert self.stack is not None
        return int(self.stack.rho_e.shape[0])

    def load_from_diags(self, diags_dir: Path, domain: FocusDomain) -> None:
        self.diags_dir = diags_dir
        self.stack = load_warpx_density_frames(diags_dir, domain)
        self.frame_index = 0
        self.meta = dict(self.stack.meta)

    def clear(self) -> None:
        self.stack = None
        self.diags_dir = None
        self.frame_index = 0
        self.meta = {}

    def set_phase(self, phase: float) -> int:
        """Map 0–1 live phase → frame index."""
        n = self.n_frames
        if n <= 1:
            self.frame_index = 0
            return 0
        self.frame_index = int(phase * (n - 1)) % n
        return self.frame_index

    def radial_profiles(self, frame: int | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Azimuthally averaged ρ_e and ρ_beam vs r at one PIC time step.

        Returns (r_m, rho_e, rho_beam).
        """
        if not self.available:
            raise RuntimeError("No PIC session loaded")
        assert self.stack is not None
        fi = self.frame_index if frame is None else max(0, min(frame, self.n_frames - 1))
        rho_e = np.mean(self.stack.rho_e[fi], axis=0)
        rho_b = np.mean(self.stack.rho_beam[fi], axis=0)
        return self.stack.r_m.copy(), rho_e, rho_b

    def transverse_slice(self, frame: int | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Full (r, z) ρ_e slice for inset / timelapse display."""
        if not self.available:
            raise RuntimeError("No PIC session loaded")
        assert self.stack is not None
        fi = self.frame_index if frame is None else max(0, min(frame, self.n_frames - 1))
        return self.stack.r_m, self.stack.z_m, self.stack.rho_e[fi]
