"""Longitudinal s–r preview for Proof Suite step 01 (pad-synced, no separate app)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Circle

from ssto.orbitron.simulator.blender_layout import draw_blender_underlay, engine_axial_layout
from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus, focus_domain
from ssto.orbitron.simulator.longitudinal.fusion_channel_sr import (
    fusion_channel_to_longitudinal_run,
    laminar_hack_from_inputs,
    run_fusion_channel_sr,
)
from ssto.orbitron.simulator.longitudinal.run import LongitudinalRun, run_longitudinal
from ssto.orbitron.simulator.longitudinal.warpx_frames import load_warpx_density_frames
from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.proof_chain.runners import list_pic_plotfiles
from ssto.orbitron.simulator.types import SimulatorInputs

def _align_pcolormesh_grid(
    x: np.ndarray,
    y: np.ndarray,
    field: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Match 1D axis lengths to 2D field for matplotlib pcolormesh (shading='auto')."""
    f = np.asarray(field, dtype=float)
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    if f.shape == (len(y), len(x)):
        return x, y, f
    if f.shape == (len(x), len(y)):
        return x, y, f.T
    if f.shape[1] == len(x) and f.shape[0] != len(y):
        y = np.linspace(float(y[0]), float(y[-1]), f.shape[0])
        return x, y, f
    if f.shape[0] == len(y) and f.shape[1] != len(x):
        x = np.linspace(float(x[0]), float(x[-1]), f.shape[1])
        return x, y, f
    x = np.linspace(float(x[0]), float(x[-1]), f.shape[1])
    y = np.linspace(float(y[0]), float(y[-1]), f.shape[0])
    return x, y, f


# Step 01 GUI: x–z only. Cylindrical r–z (r = |x|) lives in warpx_frames.py for future 3D/RZ handoff.
STEP01_MAP_EQUATION_HTML = (
    "<b>Map from upper → lower (cylindrical bore):</b> upper cell at (<i>x</i>, <i>z</i>) shows "
    "|ρ<sub>e</sub>| on the WarpX transverse slice (<i>z</i> = tube axis).<br>"
    "Lower cell at (<i>r</i>, <i>z</i>) sums upper cells with <i>r</i> = |<i>x</i>| and the same "
    "<i>z</i> — a flat rectangular grid (vertical bands for a hollow ring), not a spherical "
    "√(<i>x</i>²+<i>z</i>²) wedge."
)

LONGITUDINAL_FOCUS_LABELS: tuple[tuple[str, LongitudinalFocus], ...] = (
    ("Full engine — duct s–r (intake → nozzle)", LongitudinalFocus.FULL_DUCT_AIR),
    ("Fusion channel — core bore s–r + p-¹¹B", LongitudinalFocus.FUSION_CHANNEL_SR),
    ("Core tube — PIC transverse (after WarpX)", LongitudinalFocus.CORE_TUBE),
)


def data_source_caption(run: LongitudinalRun) -> str:
    """Human-readable provenance for the plot title."""
    model = str(run.meta.get("model", "unknown"))
    src = run.meta.get("source", "")
    if model in ("pic_frames", "warpx_xy_slices") or "WarpX" in str(run.meta.get("note", "")):
        base = "Data: WarpX PIC (density_diag plotfiles"
        if src:
            return f"{base}, {src})"
        return f"{base})"
    if model == "heuristic_pic":
        return "Data: heuristic preview (NOT WarpX)"
    if model == "fusion_channel_sr":
        return "Data: analytical fusion-channel model (NOT WarpX)"
    if model == "annulus_flow_2d":
        return "Data: analytical annulus-air model (NOT WarpX)"
    return f"Data: {model}"


def load_warpx_xy_stack(diags: Path, inputs: SimulatorInputs) -> LongitudinalRun:
    """Direct x–z slices from WarpX plotfiles (no polar histogram)."""
    import yt

    from ssto.orbitron.simulator.longitudinal.run import LongitudinalRun

    plotfiles = list_pic_plotfiles(diags)
    if not plotfiles:
        raise FileNotFoundError(f"No density_diag plotfiles in {diags}")

    yt.funcs.mylog.setLevel(50)
    domain = focus_domain(LongitudinalFocus.CORE_TUBE, inputs)
    times: list[float] = []
    frames: list[np.ndarray] = []
    x_ref: np.ndarray | None = None
    z_ref: np.ndarray | None = None

    for pf in plotfiles:
        ds = yt.load(str(pf))
        times.append(float(ds.current_time.to_value()))
        grid = ds.covering_grid(level=0, left_edge=ds.domain_left_edge, dims=ds.domain_dimensions)
        rho = np.abs(grid[("boxlib", "rho_electrons")].v.squeeze())
        if rho.ndim != 2:
            rho = np.squeeze(rho)
        nz, nx = int(rho.shape[0]), int(rho.shape[1])
        le = np.asarray(ds.domain_left_edge.to_value(), dtype=float).ravel()
        re = np.asarray(ds.domain_right_edge.to_value(), dtype=float).ravel()
        x1d = np.linspace(float(le[0]), float(re[0]), nx)
        z1d = np.linspace(float(le[1] if le.size > 1 else 0), float(re[1] if re.size > 1 else 1), nz)
        if x_ref is None:
            x_ref, z_ref = x1d, z1d
        frames.append(rho)

    primary = np.stack(frames, axis=0)
    return LongitudinalRun(
        focus=LongitudinalFocus.CORE_TUBE,
        domain=domain,
        time_s=np.asarray(times, dtype=np.float64),
        primary=primary,
        secondary=None,
        axis_horizontal=x_ref if x_ref is not None else np.array([0.0]),
        axis_vertical=z_ref if z_ref is not None else np.array([0.0]),
        primary_label="|ρ_e| (WarpX)",
        secondary_label="",
        horizontal_label="x [m] (WarpX transverse)",
        vertical_label="z [m] (WarpX transverse)",
        meta={
            "model": "warpx_xy_slices",
            "source": str(diags),
            "note": "Direct WarpX density_diag — same physics as laminar_flow_2d_arcjet",
        },
    )


def compute_longitudinal_preview(
    inputs: SimulatorInputs,
    focus: LongitudinalFocus,
    *,
    laminar_on: bool,
    pic_diags: Path | None = None,
    use_heuristic_pic: bool = False,
    warpx_xy_direct: bool = False,
) -> LongitudinalRun:
    """Fast enough for 2 Hz pad-sync on fusion channel / annulus; WarpX path is heavier."""
    domain = focus_domain(focus, inputs)
    if focus == LongitudinalFocus.CORE_TUBE and warpx_xy_direct and pic_diags is not None:
        if list_pic_plotfiles(pic_diags):
            return load_warpx_xy_stack(pic_diags, inputs)
    if focus == LongitudinalFocus.FUSION_CHANNEL_SR:
        laminar = laminar_hack_from_inputs(inputs, force_off=not laminar_on)
        fc = run_fusion_channel_sr(domain, inputs, laminar=laminar)
        return fusion_channel_to_longitudinal_run(fc, domain)

    if focus == LongitudinalFocus.FULL_DUCT_AIR:
        return run_longitudinal(focus, inputs, use_heuristic_pic=False)

    if pic_diags is not None and list_pic_plotfiles(pic_diags):
        stack = load_warpx_density_frames(pic_diags, domain)
        return run_longitudinal(focus, inputs, pic_stack=stack)

    return run_longitudinal(
        focus,
        inputs,
        use_heuristic_pic=use_heuristic_pic,
        pic_steps=120,
    )


def draw_longitudinal_frame(
    fig: Figure,
    run: LongitudinalRun,
    frame_idx: int,
    *,
    inputs: SimulatorInputs,
    field_index: int = 0,
    laminar_on: bool = True,
) -> None:
    """Render one timelapse frame with CAD underlay when applicable."""
    idx = max(0, min(frame_idx, len(run.time_s) - 1))
    use_secondary = field_index == 1 and run.secondary is not None
    data = run.secondary if use_secondary else run.primary
    label = run.secondary_label if use_secondary else run.primary_label

    fig.clear()
    ax = fig.add_subplot(111)
    d = run.domain
    pad_status = evaluate_pad_status(inputs.pad)
    duct_len = d.s_max_m - d.s_min_m if d.s_max_m > d.s_min_m else 3.2
    layout = engine_axial_layout(inputs.geometry, duct_length_m=duct_len)

    if run.focus in (LongitudinalFocus.FULL_DUCT_AIR, LongitudinalFocus.FUSION_CHANNEL_SR):
        draw_blender_underlay(ax, layout, run.focus, symmetric=False)
        xh, yv, sl = _align_pcolormesh_grid(
            run.axis_horizontal,
            run.axis_vertical,
            data[idx],
        )
        im = ax.pcolormesh(xh, yv, sl, shading="auto", cmap="magma", alpha=0.72)
        extra = ""
        if run.focus == LongitudinalFocus.FUSION_CHANNEL_SR:
            extra = (
                f"  |  clump={run.meta.get('clump_index_final', 0):.2f}"
                f"  laminar={'ON' if laminar_on else 'OFF'}"
            )
        ax.set_title(
            f"{d.label}  |  pad bleed={'ON' if pad_status.state.bleed_air_open else 'off'}"
            + extra
            + f"\n{data_source_caption(run)}",
            color="#c0caf5",
            fontsize=9,
        )
    else:
        # PIC stack: primary is (n_z, n_r) remapped from WarpX x–z; axes are r (X) and z (Y).
        xh, yv, sl = _align_pcolormesh_grid(
            run.axis_horizontal,
            run.axis_vertical,
            data[idx],
        )
        im = ax.pcolormesh(xh, yv, sl, shading="auto", cmap="magma")
        ax.add_patch(Circle((0, 0), d.r_cathode_m, fill=False, ec="#ca8a04", lw=1.5))
        ax.add_patch(Circle((0, 0), d.r_anode_m, fill=False, ec="#e8c547", lw=2))
        inset = fig.add_axes([0.58, 0.08, 0.38, 0.32])
        draw_blender_underlay(inset, layout, run.focus)
        inset.set_title("CAD layout (s–r)", fontsize=8, color="#e2e8f0")
        armed = "ARMED" if pad_status.reactor_armed else "spin-up"
        ax.set_title(
            f"{d.label}  |  {label}  |  {armed}\n{data_source_caption(run)}",
            color="#c0caf5",
            fontsize=9,
        )

    fig.colorbar(im, ax=ax, label=label, fraction=0.046)
    ax.set_xlabel(run.horizontal_label, color="#a9b1d6")
    ax.set_ylabel(run.vertical_label, color="#a9b1d6")
    fig.tight_layout()


def draw_step01_placeholder(fig: Figure, message: str) -> None:
    fig.clear()
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, message, ha="center", va="center", color="#a9b1d6", fontsize=10, wrap=True)
    ax.set_axis_off()
    fig.tight_layout()


def draw_step01_warpx_xz(
    fig: Figure,
    run: LongitudinalRun,
    frame_idx: int,
    *,
    inputs: SimulatorInputs,
) -> None:
    """Primary step-01 view: direct WarpX x–z cell grid."""
    idx = max(0, min(frame_idx, len(run.time_s) - 1))
    fig.clear()
    ax = fig.add_subplot(111)
    d = run.domain
    pad_status = evaluate_pad_status(inputs.pad)
    duct_len = d.s_max_m - d.s_min_m if d.s_max_m > d.s_min_m else 3.2
    layout = engine_axial_layout(inputs.geometry, duct_length_m=duct_len)

    xh, yv, sl = _align_pcolormesh_grid(run.axis_horizontal, run.axis_vertical, run.primary[idx])
    im = ax.pcolormesh(xh, yv, sl, shading="auto", cmap="magma")
    ax.add_patch(Circle((0, 0), d.r_cathode_m, fill=False, ec="#ca8a04", lw=1.5))
    ax.add_patch(Circle((0, 0), d.r_anode_m, fill=False, ec="#e8c547", lw=2))
    inset = fig.add_axes([0.58, 0.10, 0.38, 0.30])
    draw_blender_underlay(inset, layout, run.focus)
    inset.set_title("CAD layout (s–r)", fontsize=8, color="#e2e8f0")
    armed = "ARMED" if pad_status.reactor_armed else "spin-up"
    ax.set_title(
        f"Primary: x–z (WarpX cell grid)  |  {run.primary_label}  |  {armed}\n"
        f"{data_source_caption(run)}",
        color="#c0caf5",
        fontsize=9,
    )
    fig.colorbar(im, ax=ax, label=run.primary_label, fraction=0.046)
    ax.set_xlabel("x [m] (WarpX transverse)", color="#a9b1d6")
    ax.set_ylabel("z [m] (WarpX transverse)", color="#a9b1d6")
    fig.text(
        0.5,
        0.02,
        "WarpX transverse slice: (x, z) on the cell grid",
        ha="center",
        fontsize=8,
        color="#a9b1d6",
    )
    fig.subplots_adjust(bottom=0.14)
    fig.tight_layout(rect=(0, 0.06, 1, 1))


def draw_step01_warpx_rz_remap(
    fig: Figure,
    run: LongitudinalRun,
    frame_idx: int,
    *,
    inputs: SimulatorInputs,
    field_index: int = 0,
) -> None:
    """Step-01 cylindrical r–z view: sum |ρ|(x,z) into bins with r=|x|, same z."""
    idx = max(0, min(frame_idx, len(run.time_s) - 1))
    use_secondary = field_index == 1 and run.secondary is not None
    data = run.secondary if use_secondary else run.primary
    label = run.secondary_label if use_secondary else run.primary_label

    fig.clear()
    ax = fig.add_subplot(111)
    d = run.domain
    pad_status = evaluate_pad_status(inputs.pad)

    xh, yv, sl = _align_pcolormesh_grid(run.axis_horizontal, run.axis_vertical, data[idx])
    im = ax.pcolormesh(xh, yv, sl, shading="auto", cmap="magma")
    ax.axvline(d.r_cathode_m, color="#ca8a04", lw=1.5, ls="--", label="cathode r")
    ax.axvline(d.r_anode_m, color="#e8c547", lw=2, ls="--", label="anode r")
    armed = "ARMED" if pad_status.reactor_armed else "spin-up"
    ax.set_title(
        "Cylindrical r–z (r = |x|, z axial) — axial uniformity / end losses"
        f"  |  {label}  |  {armed}\n"
        f"{data_source_caption(run)}",
        color="#c0caf5",
        fontsize=9,
    )
    fig.colorbar(im, ax=ax, label=label, fraction=0.046)
    ax.set_xlabel("r [m]  where  r = |x|  (radial; cylinder, not √(x²+z²))", color="#a9b1d6")
    ax.set_ylabel("z [m] (tube axis — same as upper panel)", color="#a9b1d6")
    fig.text(
        0.5,
        0.02,
        "|ρ|(r,z) = Σ |ρ|(x,z) with r=|x|; hollow ring → vertical bands at r ≈ ring radius",
        ha="center",
        fontsize=8,
        color="#a9b1d6",
    )
    fig.subplots_adjust(bottom=0.14)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
