"""
Load WarpX density diagnostic plotfiles into frame stacks for timelapse scrubbing.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ssto.orbitron.simulator.longitudinal.focus import FocusDomain


@dataclass
class PicFrameStack:
    """Transverse (x, z) PIC fields remapped to polar r for display."""

    time_s: np.ndarray
    r_m: np.ndarray
    z_m: np.ndarray
    # (nt, nz, nr_bins)
    rho_e: np.ndarray
    rho_beam: np.ndarray
    meta: dict


def load_warpx_density_frames(
    diags_dir: Path,
    domain: FocusDomain,
    *,
    nr_bins: int = 96,
) -> PicFrameStack:
    plotfiles = sorted(diags_dir.glob("density_diag*"))
    if not plotfiles:
        raise FileNotFoundError(f"No density_diag plotfiles under {diags_dir}")

    import yt

    yt.funcs.mylog.setLevel(50)
    r_max = domain.r_max_m
    r_edges = np.linspace(0.0, r_max, nr_bins + 1)
    r_centers = 0.5 * (r_edges[:-1] + r_edges[1:])

    stacks_e: list[np.ndarray] = []
    stacks_b: list[np.ndarray] = []
    z_ref: np.ndarray | None = None
    times: list[float] = []

    beam_names = ("rho_h_inject_beam", "rho_b_inject_beam", "rho_stabilizing_beam")

    for pf in plotfiles:
        ds = yt.load(str(pf))
        times.append(float(ds.current_time.to_value()))
        grid = ds.covering_grid(level=0, left_edge=ds.domain_left_edge, dims=ds.domain_dimensions)
        re = np.abs(grid[("boxlib", "rho_electrons")].v.squeeze())
        rb = np.zeros_like(re)
        for bn in beam_names:
            try:
                rb += np.abs(grid[("boxlib", bn)].v.squeeze())
            except Exception:
                pass
        if re.ndim != 2:
            re = np.squeeze(re)
            rb = np.squeeze(rb)
        nz, nx = int(re.shape[0]), int(re.shape[1])
        x = np.linspace(-r_max, r_max, nx)
        z = np.linspace(-r_max, r_max, nz)
        if z_ref is None:
            z_ref = z.copy()
        X, Z = np.meshgrid(x, z, indexing="xy")
        R = np.sqrt(X * X + Z * Z)
        z_flat = np.broadcast_to(z[:, np.newaxis], (nz, nx)).ravel()
        hist_e, _, _ = np.histogram2d(
            R.ravel(),
            z_flat,
            bins=[r_edges, z],
            weights=re.ravel(),
        )
        hist_b, _, _ = np.histogram2d(
            R.ravel(),
            z_flat,
            bins=[r_edges, z],
            weights=rb.ravel(),
        )
        stacks_e.append(hist_e.T)
        stacks_b.append(hist_b.T)

    rho_e = np.stack(stacks_e, axis=0)
    rho_b = np.stack(stacks_b, axis=0)
    return PicFrameStack(
        time_s=np.asarray(times, dtype=np.float64),
        r_m=r_centers,
        z_m=z_ref if z_ref is not None else np.array([0.0]),
        rho_e=rho_e,
        rho_beam=rho_b,
        meta={"n_frames": len(plotfiles), "source": str(diags_dir)},
    )
