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
    """Transverse (x, z) PIC fields projected to cylindrical r–z with r = |x| (z = bore axis)."""

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
    ref_hist_shape: tuple[int, int] | None = None
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
        le = np.asarray(ds.domain_left_edge.to_value(), dtype=float).ravel()
        re_edge = np.asarray(ds.domain_right_edge.to_value(), dtype=float).ravel()
        x = np.linspace(float(le[0]), float(re_edge[0]), nx)
        z_ax = 1 if le.size > 1 else 0
        z = np.linspace(float(le[z_ax]), float(re_edge[z_ax]), nz)
        if z_ref is None:
            z_ref = z.copy()
        X, _Z = np.meshgrid(x, z, indexing="xy")
        # Cylindrical 2D slice: z is axial (tube axis), r = |x| is radial — not sqrt(x²+z²).
        R = np.abs(X)
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
        frame_e = hist_e.T
        frame_b = hist_b.T
        if ref_hist_shape is None:
            ref_hist_shape = frame_e.shape
            z_ref = z.copy()
        elif frame_e.shape != ref_hist_shape:
            continue
        stacks_e.append(frame_e)
        stacks_b.append(frame_b)

    if not stacks_e:
        raise ValueError(f"No plotfiles with consistent shape under {diags_dir}")

    rho_e = np.stack(stacks_e, axis=0)
    rho_b = np.stack(stacks_b, axis=0)
    return PicFrameStack(
        time_s=np.asarray(times, dtype=np.float64),
        r_m=r_centers,
        z_m=z_ref if z_ref is not None else np.array([0.0]),
        rho_e=rho_e,
        rho_beam=rho_b,
        meta={
            "n_frames": len(plotfiles),
            "source": str(diags_dir),
            "projection": "cylindrical_r_abs_x",
            "note": "r–z panel: r=|x|, z unchanged (axial uniformity view for cylinder bore)",
        },
    )
