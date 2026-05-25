"""Headless matplotlib figures for experiment reports (Agg backend)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
from ssto.orbitron.simulator.proof_chain.runners import base_inputs, list_pic_plotfiles
from ssto.orbitron.simulator.proof_suite.longitudinal_viz import (
    _align_pcolormesh_grid,
    compute_longitudinal_preview,
    draw_fusion_channel_heatmap,
    fusion_channel_colorbar,
    draw_step01_warpx_xz,
    fusion_field_color_limits,
    fusion_off_on_log_ratio,
)
from ssto.orbitron.simulator.types import DeviceGeometry
from ssto.orbitron.simulator.viz import render_device_cross_section
from tools.orbitron_proof_chain.chain_lib import CHAIN_ROOT, load_config, load_step_json


def _save_fig(fig: plt.Figure, path: Path, dpi: int = 140) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="#1a1b26")
    plt.close(fig)


def _dark_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#1a1b26",
            "axes.facecolor": "#24283b",
            "axes.edgecolor": "#565f89",
            "axes.labelcolor": "#c0caf5",
            "text.color": "#c0caf5",
            "xtick.color": "#a9b1d6",
            "ytick.color": "#a9b1d6",
        }
    )


def _geometry_from_cfg(cfg: dict[str, Any]) -> DeviceGeometry:
    g = cfg["geometry"]
    return DeviceGeometry(
        r_anode_m=float(g["r_anode_m"]),
        r_cathode_m=float(g["r_cathode_m"]),
        length_m=float(g["length_m"]),
        V_cathode_v=float(g["V_cathode_v"]),
        B_axial_tesla=float(g["B_axial_tesla"]),
    )


def plot_step00_device(figures_dir: Path, cfg: dict[str, Any]) -> Path | None:
    _dark_style()
    geo = _geometry_from_cfg(cfg)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    render_device_cross_section(ax, geo, LongitudinalFocus.CORE_TUBE)
    out = figures_dir / "step00_device_layout.png"
    _save_fig(fig, out)
    return out


def plot_step01_warpx_last(figures_dir: Path, cfg: dict[str, Any]) -> Path | None:
    _dark_style()
    diags = CHAIN_ROOT / "01_pic" / "diags"
    plotfiles = list_pic_plotfiles(diags)
    if not plotfiles:
        return None
    inp, _ = base_inputs()
    try:
        run = compute_longitudinal_preview(
            inp,
            LongitudinalFocus.CORE_TUBE,
            laminar_on=True,
            pic_diags=diags,
            use_heuristic_pic=False,
            warpx_xy_direct=True,
        )
    except Exception:
        return None
    idx = len(run.time_s) - 1
    fig = plt.figure(figsize=(10, 5))
    draw_step01_warpx_xz(fig, run, idx, inputs=inp, delta_vs_first=False)
    pf = plotfiles[idx]
    first = np.asarray(run.primary[0], dtype=float)
    last = np.asarray(run.primary[idx], dtype=float)
    rel_l2 = float(np.linalg.norm(last - first) / max(np.linalg.norm(first), 1e-30))
    fig.text(
        0.5,
        0.96,
        f"Snapshot {idx + 1}/{len(run.time_s)}  |  t = {run.time_s[idx]:.3e} s  |  {pf.name}"
        f"  |  Δρ vs snapshot 1: {100 * rel_l2:.3f}% L2",
        ha="center",
        fontsize=8,
        color="#9ece6a",
    )
    out = figures_dir / "step01_warpx_rho_e_last.png"
    _save_fig(fig, out)
    return out


def plot_step01_warpx_evidence(figures_dir: Path, cfg: dict[str, Any]) -> Path | None:
    """First | last | Δρ panels — proves report uses final snapshot, not t=0."""
    _dark_style()
    diags = CHAIN_ROOT / "01_pic" / "diags"
    plotfiles = list_pic_plotfiles(diags)
    if not plotfiles:
        return None
    inp, _ = base_inputs()
    try:
        run = compute_longitudinal_preview(
            inp,
            LongitudinalFocus.CORE_TUBE,
            laminar_on=True,
            pic_diags=diags,
            use_heuristic_pic=False,
            warpx_xy_direct=True,
        )
    except Exception:
        return None
    if len(run.time_s) < 2:
        return None

    first = np.asarray(run.primary[0], dtype=float)
    last_idx = len(run.time_s) - 1
    last = np.asarray(run.primary[last_idx], dtype=float)
    delta = np.maximum(last - first, 0.0)
    rel_l2 = float(np.linalg.norm(last - first) / max(np.linalg.norm(first), 1e-30))
    vmax = float(run.meta.get("rho_vmax", 1.0))
    dmax = max(float(np.percentile(delta, 99.5)), vmax * 0.001, 1e-30)

    audit = {
        "n_snapshots": len(run.time_s),
        "first_plotfile": plotfiles[0].name,
        "last_plotfile": plotfiles[-1].name,
        "first_time_s": float(run.time_s[0]),
        "last_time_s": float(run.time_s[-1]),
        "report_uses_index": last_idx,
        "l2_relative_change_pct": round(100 * rel_l2, 4),
        "max_abs_delta_rho": float(np.max(np.abs(last - first))),
        "pearson_r_first_last": float(np.corrcoef(first.ravel(), last.ravel())[0, 1]),
        "electron_ring_only": True,
        "note": "Ring is nearly stationary in electron_ring_only mode; last frame ≈ first visually.",
    }
    figures_dir.mkdir(parents=True, exist_ok=True)
    (figures_dir / "step01_warpx_frame_audit.json").write_text(
        __import__("json").dumps(audit, indent=2) + "\n", encoding="utf-8"
    )

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    panels = [
        (first, 0.0, vmax, f"t=0  ({plotfiles[0].name})"),
        (last, 0.0, vmax, f"t={run.time_s[last_idx]:.2e} s  ({plotfiles[-1].name})"),
    ]
    for ax, (data, vmin, vmax_p, title) in zip(axes[:2], panels):
        xh, yv, sl = _align_pcolormesh_grid(run.axis_horizontal, run.axis_vertical, data)
        im = ax.pcolormesh(xh, yv, sl, shading="auto", cmap="magma", vmin=vmin, vmax=vmax_p)
        ax.set_title(title, fontsize=9, color="#c0caf5")
        ax.set_xlabel("x [m]", color="#a9b1d6", fontsize=8)
        ax.set_ylabel("z [m]", color="#a9b1d6", fontsize=8)
        fig.colorbar(im, ax=ax, fraction=0.046)

    xh, yv, sl = _align_pcolormesh_grid(run.axis_horizontal, run.axis_vertical, delta)
    im = axes[2].pcolormesh(xh, yv, sl, shading="auto", cmap="magma", vmin=0.0, vmax=dmax)
    axes[2].set_title(f"Δρ (last − first)  max={np.max(delta):.2e}", fontsize=9, color="#c0caf5")
    axes[2].set_xlabel("x [m]", color="#a9b1d6", fontsize=8)
    axes[2].set_ylabel("z [m]", color="#a9b1d6", fontsize=8)
    fig.colorbar(im, ax=axes[2], fraction=0.046)
    fig.suptitle(
        f"WarpX frame audit — report uses snapshot {last_idx + 1}/{len(run.time_s)} "
        f"(L2 change vs t=0: {100 * rel_l2:.3f}%)",
        color="#e0af68",
        fontsize=10,
    )
    out = figures_dir / "step01_warpx_frame_evidence.png"
    _save_fig(fig, out)
    return out


def plot_step02_rho_norm(figures_dir: Path) -> Path | None:
    try:
        data = load_step_json("02")
    except Exception:
        return None
    _dark_style()
    fig, ax = plt.subplots(figsize=(4, 3.5))
    if data.get("skipped"):
        re = float(data.get("rho_e_norm", 1.0))
        ax.bar(["ρ_e_norm"], [re], color="#565f89", width=0.4, alpha=0.6)
        ax.axhspan(0.2, 3.0, color="#9ece6a", alpha=0.12)
        ax.set_ylim(0, max(3.5, re * 1.15))
        ax.set_ylabel("Electron ring ×")
        ax.set_title("PIC skipped — unity placeholder (not measured)", color="#e0af68", fontsize=9)
        ax.text(
            0.5,
            0.92,
            "run.skip_pic or --skip-pic",
            transform=ax.transAxes,
            ha="center",
            fontsize=8,
            color="#565f89",
        )
    else:
        re = float(data.get("rho_e_norm", 1))
        color = "#7aa2f7" if 0.2 <= re <= 3.0 else "#f7768e"
        ax.bar(["ρ_e_norm"], [re], color=color, width=0.4)
        ax.axhspan(0.2, 3.0, color="#9ece6a", alpha=0.12)
        ax.set_ylim(0, max(3.5, re * 1.15))
        ax.set_ylabel("Electron ring ×")
    out = figures_dir / "step02_rho_e_norm.png"
    _save_fig(fig, out)
    return out


def _annotate_bar_values(ax, bars, *, fmt: str = "{:.3g}", color: str = "#c0caf5") -> None:
    for bar in bars:
        h = bar.get_height()
        if h <= 0:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h,
            fmt.format(h),
            ha="center",
            va="bottom",
            fontsize=9,
            color=color,
        )


def _plot_fusion_triplet(
    figures_dir: Path,
    cfg: dict[str, Any],
    *,
    off_npz: str | Path,
    on_npz: str | Path,
    field_key: str,
    basename: str,
    suptitle: str,
) -> Path | None:
    off_p, on_p = Path(off_npz), Path(on_npz)
    if not off_p.is_file() or not on_p.is_file():
        return None
    z_off = np.load(off_p)
    z_on = np.load(on_p)
    idx = len(z_on["time_s"]) - 1
    sl_off = z_off[field_key][idx]
    sl_on = z_on[field_key][idx]
    vmin_off, vmax_off = fusion_field_color_limits(z_off[field_key])
    vmin_on, vmax_on = fusion_field_color_limits(z_on[field_key])
    geo = _geometry_from_cfg(cfg)
    r_a = geo.r_anode_m
    field_label = "Fuel density n(s,r)" if field_key == "density" else "Reaction rate R(s,r)"
    _dark_style()
    fig, (ax_off, ax_on, ax_ratio) = plt.subplots(
        1, 3, figsize=(17, 2.75), gridspec_kw={"wspace": 0.38}
    )
    im_off = draw_fusion_channel_heatmap(
        ax_off,
        z_off["s_m"],
        z_off["r_m"],
        sl_off,
        r_anode_m=r_a,
        title="Laminar OFF (clumpy)",
        vmin=vmin_off,
        vmax=vmax_off,
    )
    im_on = draw_fusion_channel_heatmap(
        ax_on,
        z_on["s_m"],
        z_on["r_m"],
        sl_on,
        r_anode_m=r_a,
        title="Laminar ON (smoothed)",
        vmin=vmin_on,
        vmax=vmax_on,
    )
    ratio = fusion_off_on_log_ratio(sl_off, sl_on)
    r_vmin, r_vmax = fusion_field_color_limits(ratio[np.newaxis, ...])
    im_ratio = draw_fusion_channel_heatmap(
        ax_ratio,
        z_on["s_m"],
        z_on["r_m"],
        ratio,
        r_anode_m=r_a,
        title="log10(OFF/ON) — warm = hack reduced",
        vmin=r_vmin,
        vmax=r_vmax,
        cmap="RdBu_r",
    )
    if field_key == "reaction_rate" and (vmax_off or 0) <= 0:
        for ax in (ax_off, ax_on, ax_ratio):
            ax.text(
                0.5,
                0.5,
                "R = 0 — check IGNITE interlocks",
                ha="center",
                va="center",
                transform=ax.transAxes,
                color="#f7768e",
            )
    fusion_channel_colorbar(fig, ax_off, im_off, label=field_label)
    fusion_channel_colorbar(fig, ax_on, im_on, label=field_label)
    fusion_channel_colorbar(fig, ax_ratio, im_ratio, label="log10 ratio")
    fig.suptitle(suptitle, color="#c0caf5", y=1.02, fontsize=11)
    fig.subplots_adjust(left=0.04, right=0.93, top=0.82, bottom=0.18, wspace=0.42)
    out = figures_dir / basename
    _save_fig(fig, out)
    return out


def _plot_fusion_pair(
    figures_dir: Path,
    cfg: dict[str, Any],
    *,
    field_key: str,
    basename: str,
) -> Path | None:
    try:
        d3 = load_step_json("03")
    except Exception:
        return None
    off_p = d3.get("fields_laminar_off_npz")
    on_p = d3.get("fields_laminar_on_npz")
    if not off_p or not on_p:
        return None
    label = "Fuel density n(s,r)" if field_key == "density" else "Reaction rate R(s,r)"
    return _plot_fusion_triplet(
        figures_dir,
        cfg,
        off_npz=off_p,
        on_npz=on_p,
        field_key=field_key,
        basename=basename,
        suptitle=f"Step 03 — {label} (baseline / proof-forward; final frame)",
    )


def _plot_fusion_clump_from_npz(
    figures_dir: Path,
    *,
    off_npz: str | Path,
    on_npz: str | Path,
    d3_meta: dict[str, Any],
    basename: str,
    title: str,
) -> Path | None:
    paths = [Path(off_npz), Path(on_npz)]
    if not all(p.is_file() for p in paths):
        return None
    _dark_style()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    z_on = np.load(paths[1])
    z_off = np.load(paths[0])
    ax.plot(z_on["time_s"], z_on["clump_index"], color="#9ece6a", label="ON")
    ax.plot(z_off["time_s"], z_off["clump_index"], color="#f7768e", label="OFF")
    ax.axhline(2.8, color="#e0af68", ls="--", label="ON pass ≤ 2.8")
    ci_on = float(d3_meta.get("clump_index_final", z_on["clump_index"][-1]))
    ci_off = float(d3_meta.get("clump_index_off", z_off["clump_index"][-1]))
    ratio = float(d3_meta.get("clump_reduction_ratio", ci_off / max(ci_on, 1e-6)))
    ax.legend(fontsize=8, loc="lower right")
    ax.set_title(f"{title}  (OFF/ON={ratio:.2f}×)", color="#c0caf5")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("C_k")
    out = figures_dir / basename
    _save_fig(fig, out)
    return out


def plot_step03_clump(figures_dir: Path) -> Path | None:
    try:
        d3 = load_step_json("03")
    except Exception:
        return None
    off_p, on_p = d3.get("fields_laminar_off_npz"), d3.get("fields_laminar_on_npz")
    if not off_p or not on_p:
        return None
    return _plot_fusion_clump_from_npz(
        figures_dir,
        off_npz=off_p,
        on_npz=on_p,
        d3_meta=d3,
        basename="step03_clump_index.png",
        title="Clump index C_k (baseline)",
    )


def _plot_fusion_radial_from_npz(
    figures_dir: Path,
    cfg: dict[str, Any],
    *,
    on_npz: str | Path,
    basename: str,
    title: str,
) -> Path | None:
    on_p = Path(on_npz)
    if not on_p.is_file():
        return None
    z = np.load(on_p)
    geo = _geometry_from_cfg(cfg)
    r_a = geo.r_anode_m
    _dark_style()
    fig, ax = plt.subplots(figsize=(6, 4))
    last = z["density"][-1]
    prof = np.mean(last, axis=0)
    ax.plot(z["r_m"], prof, color="#9ece6a", lw=1.8)
    ax.axvline(r_a, color="#e0af68", ls="--", lw=1.0, label=f"r_anode={r_a:.3f} m")
    ax.set_xlim(0.0, max(float(z["r_m"][-1]), r_a * 1.15))
    ymax = float(np.max(prof[z["r_m"] <= r_a * 1.001])) if prof.size else 1.0
    ax.set_ylim(0.0, ymax * 1.12)
    ax.legend(fontsize=8)
    ax.set_title(title, color="#c0caf5")
    ax.set_xlabel("r [m]")
    ax.set_ylabel("n [m⁻³]")
    out = figures_dir / basename
    _save_fig(fig, out)
    return out


def plot_step03_radial_final(figures_dir: Path, cfg: dict[str, Any]) -> Path | None:
    try:
        d3 = load_step_json("03")
        on_p = d3.get("fields_laminar_on_npz")
    except Exception:
        return None
    if not on_p:
        return None
    return _plot_fusion_radial_from_npz(
        figures_dir,
        cfg,
        on_npz=on_p,
        basename="step03_radial_n_final.png",
        title="⟨n⟩_s(r) final — laminar ON (baseline)",
    )


def plot_step03_gap_figures(
    figures_dir: Path,
    report_dir: Path,
    cfg: dict[str, Any],
) -> dict[str, str | None]:
    """Full step-03 panel set for gap-closed fusion channel (mirrors baseline step 03)."""
    d3 = _load_report_step_json(report_dir, "03_gap")
    rel: dict[str, str | None] = {}
    if not d3:
        return rel
    off_p = d3.get("fields_laminar_off_npz")
    on_p = d3.get("fields_laminar_on_npz")
    if not off_p or not on_p:
        return rel

    def put(key: str, path: Path | None) -> None:
        rel[key] = path.name if path else None

    put(
        "step03_gap_density",
        _plot_fusion_triplet(
            figures_dir,
            cfg,
            off_npz=off_p,
            on_npz=on_p,
            field_key="density",
            basename="step03_gap_density_final.png",
            suptitle="Step 03 — fuel density (gap-closed unobtanium; final frame)",
        ),
    )
    put(
        "step03_gap_reaction",
        _plot_fusion_triplet(
            figures_dir,
            cfg,
            off_npz=off_p,
            on_npz=on_p,
            field_key="reaction_rate",
            basename="step03_gap_reaction_rate_final.png",
            suptitle="Step 03 — reaction rate (gap-closed unobtanium; final frame)",
        ),
    )
    put(
        "step03_gap_clump",
        _plot_fusion_clump_from_npz(
            figures_dir,
            off_npz=off_p,
            on_npz=on_p,
            d3_meta=d3,
            basename="step03_gap_clump_index.png",
            title="Clump index C_k (gap-closed)",
        ),
    )
    put(
        "step03_gap_radial",
        _plot_fusion_radial_from_npz(
            figures_dir,
            cfg,
            on_npz=on_p,
            basename="step03_gap_radial_n_final.png",
            title="⟨n⟩_s(r) final — laminar ON (gap-closed)",
        ),
    )
    p_int = float(d3.get("integrated_fusion_power_mw", 0))
    rel["step03_gap_meta"] = f"P_int={p_int:.3f} MW"
    return rel


def plot_step04_fueling(figures_dir: Path) -> Path | None:
    try:
        data = load_step_json("04")
    except Exception:
        return None
    _dark_style()
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.bar(
        ["n_p (H⁺)", "n_B"],
        [float(data["n_proton_m3"]), float(data["n_boron_m3"])],
        color=["#7aa2f7", "#bb9af7"],
    )
    ax.set_title(f"T_i = {data['ion_temperature_kev']:.0f} keV")
    ax.set_ylabel("m⁻³")
    out = figures_dir / "step04_fueling_densities.png"
    _save_fig(fig, out)
    return out


def plot_step05_burn(figures_dir: Path, *, file_tag: str = "step05") -> Path | None:
    try:
        data = load_step_json("05")
    except Exception:
        return None
    _dark_style()
    fig, ax = plt.subplots(figsize=(5.5, 4))
    target = float(data.get("target_gross_power_mw", 3.5))
    p_fus = float(data.get("fusion_power_mw", 0))
    short = float(data.get("shortfall_mw", target - p_fus))
    labels = ["Target", "P_fusion"]
    values = [target, p_fus]
    bars = ax.bar(
        labels,
        values,
        color=["#565f89", "#9ece6a" if abs(short) < 0.5 else "#f7768e"],
        width=0.45,
    )
    _annotate_bar_values(ax, bars, fmt="{:.3f}")
    ax.set_ylabel("MW")
    if p_fus > 0 and p_fus < target * 0.5:
        ax.set_yscale("log")
        ax.set_ylim(max(p_fus * 0.5, 0.05), target * 1.5)
    else:
        ax.set_ylim(0, max(target * 1.08, p_fus * 1.15))
    title_suffix = " (gap-closed knobs)" if file_tag != "step05" else ""
    ax.set_title(
        f"P_fusion = {p_fus:.4f} MW  |  shortfall {short:.3f} MW vs {target:.1f} MW target{title_suffix}",
        color="#c0caf5",
        fontsize=10,
    )
    out = figures_dir / f"{file_tag}_burn_power.png"
    _save_fig(fig, out)
    return out


def plot_step06_plant(figures_dir: Path, *, file_tag: str = "step06") -> tuple[Path | None, Path | None]:
    try:
        data = load_step_json("06")
    except Exception:
        return None, None
    s = data["steady_state"]
    _dark_style()
    figb, axes = plt.subplots(2, 2, figsize=(9, 6))
    power_labels = ["P_gross", "P_jet", "Q_wall"]
    power_mw = [
        s["gross_power_mw"],
        s["jet_kinetic_power_mw"],
        s["wall_heat_kw"] / 1000.0,
    ]
    ax_p = axes[0, 0]
    bars_p = ax_p.bar(power_labels, power_mw, color="#7aa2f7", alpha=0.85)
    _annotate_bar_values(ax_p, bars_p, fmt="{:.3f}")
    ax_p.set_ylabel("MW")
    ax_p.set_title("Thermal / jet power", color="#c0caf5")
    ax_p.tick_params(axis="x", rotation=20)

    ax_b = axes[0, 1]
    beam_ma = float(s["beam_current_ma"])
    bars_b = ax_b.bar(["I_beam"], [beam_ma], color="#bb9af7", width=0.35)
    _annotate_bar_values(ax_b, bars_b, fmt="{:.2f}")
    ax_b.set_ylabel("mA")
    ax_b.set_title("Beam current (U4 min 1 mA)", color="#c0caf5")
    ax_b.axhline(1.0, color="#e0af68", ls="--", label="1 mA spec floor")
    ax_b.legend(fontsize=8)

    ax_t = axes[1, 0]
    thrust_kn = float(s["thrust_lbf"]) * 4.4482216152605 / 1000.0
    bars_t = ax_t.bar(["Thrust"], [thrust_kn], color="#9ece6a", width=0.35)
    _annotate_bar_values(ax_t, bars_t, fmt="{:.2f}")
    ax_t.set_ylabel("kN")
    ax_t.set_title("Thrust (jet closure)", color="#c0caf5")

    ax_m = axes[1, 1]
    mdot = float(s["mass_flow_kgps"])
    bars_m = ax_m.bar(["ṁ air"], [mdot], color="#7dcfff", width=0.35)
    _annotate_bar_values(ax_m, bars_m, fmt="{:.2f}")
    ax_m.set_ylabel("kg/s")
    ax_m.set_title("Brayton mass flow (compressor path)", color="#c0caf5")

    figb.suptitle(
        "Steady-state plant — separate units per panel"
        + (" (gap-closed knobs)" if file_tag != "step06" else ""),
        color="#c0caf5",
        y=1.01,
    )
    figb.tight_layout()
    p1 = figures_dir / f"{file_tag}_plant_outputs.png"
    _save_fig(figb, p1)

    figu, axu = plt.subplots(figsize=(7, 4))
    # (label, ratio, pass if ratio <= limit, pass if ratio >= limit)
    stress = [
        ("U1 E_cath", s["cathode_surface_field_V_m"] / 3e9, "max", 1.0),
        ("U2 q_wall", s["wall_heat_flux_W_m2"] / 2e6, "max", 1.0),
        ("U3 cryo", s["hts_cryo_kw"] / 0.5, "max", 1.0),
        ("U4 beam", float(s["beam_current_ma"]) / 1.0, "min", 1.0),
        ("U4 log₁₀ n", s["log10_density"] / 11.0, "min", 1.0),
    ]
    names = [row[0] for row in stress]
    ratios: list[float] = []
    colors = []
    for row in stress:
        _label, raw, kind, lim = row
        rv = float(raw)
        display = min(rv, 2.5) if kind == "max" else rv
        ratios.append(display)
        if kind == "min":
            colors.append("#9ece6a" if rv >= lim else "#f7768e")
        else:
            colors.append("#9ece6a" if rv <= lim else "#f7768e")
    axu.barh(names, ratios, color=colors)
    axu.axvline(1.0, color="#e0af68", ls="--", label="limit / spec (1.0×)")
    axu.set_xlim(0, max(2.6, max(ratios) * 1.15 if ratios else 2.6))
    axu.set_xlabel("Ratio to limit / floor (1.0× = at spec)")
    axu.set_title(
        "U1–U4 stress (green = pass)" + (" — gap-closed" if file_tag != "step06" else ""),
        color="#c0caf5",
    )
    axu.legend(fontsize=8, loc="lower right")
    p2 = figures_dir / f"{file_tag}_u_stress.png"
    _save_fig(figu, p2)
    return p1, p2


def plot_step07_closure(figures_dir: Path, *, file_tag: str = "step07") -> Path | None:
    try:
        data = load_step_json("07")
    except Exception:
        return None
    _dark_style()
    fig, ax = plt.subplots(figsize=(5, 3.5))
    p_jet = data["jet_kinetic_power_mw"] * 1e6
    mdot = data["mass_flow_kgps"]
    thrust_n = data["thrust_lbf"] * 4.4482216152605
    p_thrust = (thrust_n**2) / (2 * mdot) if mdot > 1e-9 else 0
    ax.bar(["P_jet", "P from F²/2ṁ"], [p_jet / 1e6, p_thrust / 1e6], color=["#7aa2f7", "#9ece6a"])
    ax.set_ylabel("MW equivalent")
    ax.set_title(
        f"Closure rel error {data['closure_rel_error']:.2%}"
        + (" (gap-closed)" if file_tag != "step07" else "")
    )
    out = figures_dir / f"{file_tag}_jet_closure.png"
    _save_fig(fig, out)
    return out


def _load_report_step_json(report_dir: Path, stem: str) -> dict[str, Any] | None:
    """Load frozen step payload from ``report_dir/results/step_<stem>.json``."""
    path = report_dir / "results" / f"step_{stem}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


_UNOB_LABELS: dict[str, str] = {
    "field_emission_margin": "U1 emission margin",
    "max_wall_heat_flux_W_m2": "U2 max wall flux",
    "ch4_cooling_effectiveness": "U2 CH₄ effectiveness",
    "hts_capability_scale": "U3 HTS scale",
    "fusion_reactivity_scale": "U4 reactivity scale",
    "beam_coupling_scale": "U4 beam coupling",
}


def _write_inverse_audit(report_dir: Path, audit: dict[str, Any]) -> None:
    path = report_dir / "figures" / "inverse_performance_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")


def plot_step09_unobtanium_compare(figures_dir: Path, report_dir: Path) -> Path | None:
    """Gap factors (required ÷ nominal) — comparable scale for every knob."""
    from ssto.orbitron.experiment.gap_pipeline import gap_factors

    s09 = _load_report_step_json(report_dir, "09")
    if not s09:
        return None
    nom = s09.get("unobtanium_nominal") or {}
    req = s09.get("unobtanium_required") or {}
    if not req:
        return None
    factors = s09.get("gap_factors") or gap_factors(s09)
    _dark_style()

    keys = sorted(factors.keys(), key=lambda k: abs(float(factors[k]) - 1.0), reverse=True)
    fac_vals = [float(factors[k]) for k in keys]
    labels = [_UNOB_LABELS.get(k, k) for k in keys]
    x = np.arange(len(keys))

    fig, (ax_fac, ax_abs) = plt.subplots(
        1,
        2,
        figsize=(11, max(4, 0.45 * len(keys))),
        gridspec_kw={"width_ratios": [1.35, 1.0]},
    )

    colors = []
    for f in fac_vals:
        if abs(f - 1.0) <= 0.05:
            colors.append("#565f89")
        elif f < 1.0:
            colors.append("#7dcfff")
        else:
            colors.append("#f7768e")
    ax_fac.barh(x, fac_vals, height=0.55, color=colors)
    ax_fac.axvline(1.0, color="#e0af68", ls="--", lw=1.5, label="1.0× (no gap)")
    ax_fac.set_yticks(x)
    ax_fac.set_yticklabels(labels)
    ax_fac.set_xlabel("Gap factor (required ÷ nominal)")
    ax_fac.set_title(
        "Stress-inverse gap factors",
        color="#c0caf5",
        fontsize=10,
    )
    lo = min(0.55, min(fac_vals) * 0.95) if fac_vals else 0.5
    hi = max(1.15, max(fac_vals) * 1.05) if fac_vals else 1.2
    ax_fac.set_xlim(lo, hi)
    for i, (k, f) in enumerate(zip(keys, fac_vals)):
        ax_fac.text(f + 0.01, i, f"{f:.3f}×", va="center", fontsize=8, color="#9ece6a")

    # U2 wall flux is stored in W/m² (not a 1.0× scale); show absolute values separately.
    ax_abs.set_title("U2 wall flux (absolute)", color="#c0caf5", fontsize=10)
    if "max_wall_heat_flux_W_m2" in req:
        n_w = float(nom.get("max_wall_heat_flux_W_m2", 2e6))
        r_w = float(req["max_wall_heat_flux_W_m2"])
        bars = ax_abs.bar(
            ["Nominal", "Required"],
            [n_w / 1e6, r_w / 1e6],
            color=["#565f89", "#7aa2f7"],
            width=0.45,
        )
        _annotate_bar_values(ax_abs, bars, fmt="{:.2f}")
        ax_abs.set_ylabel("MW/m² (×10⁶)")
        ax_abs.set_ylim(0, max(n_w, r_w) / 1e6 * 1.15)
        gf = float(factors.get("max_wall_heat_flux_W_m2", r_w / n_w))
        ax_abs.text(
            0.5,
            0.92,
            f"Gap factor on flux limit: {gf:.3f}×",
            transform=ax_abs.transAxes,
            ha="center",
            fontsize=8,
            color="#9ece6a",
        )
    else:
        ax_abs.axis("off")

    fig.suptitle(
        "Step 09 — unobtanium knobs (dimensionless gaps + U2 absolute)",
        color="#e0af68",
        fontsize=10,
    )
    out = figures_dir / "step09_unobtanium_compare.png"
    _save_fig(fig, out)
    return out


def _plot_burn_panel(ax, data: dict[str, Any], *, title: str) -> None:
    target = float(data.get("target_gross_power_mw", 3.5))
    p_fus = float(data.get("fusion_power_mw", 0))
    short = float(data.get("shortfall_mw", target - p_fus))
    bars = ax.bar(
        ["Target", "P_fusion"],
        [target, p_fus],
        color=["#565f89", "#9ece6a" if abs(short) < 0.5 else "#f7768e"],
        width=0.45,
    )
    _annotate_bar_values(ax, bars, fmt="{:.3f}")
    ax.set_ylabel("MW")
    if p_fus > 0 and p_fus < target * 0.5:
        ax.set_yscale("log")
        ax.set_ylim(max(p_fus * 0.5, 0.05), target * 1.5)
    else:
        ax.set_ylim(0, max(target * 1.08, p_fus * 1.15))
    ax.set_title(title, color="#c0caf5", fontsize=9)


def plot_step05_burn_compare(figures_dir: Path, report_dir: Path) -> Path | None:
    base = _load_report_step_json(report_dir, "05")
    gap = _load_report_step_json(report_dir, "05_gap")
    if not base or not gap:
        return None
    _dark_style()
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    _plot_burn_panel(axes[0], base, title="Baseline (nominal knobs)")
    _plot_burn_panel(axes[1], gap, title="Gap-closed (inverse knobs)")
    p0 = float(base.get("fusion_power_mw", 0))
    p1 = float(gap.get("fusion_power_mw", 0))
    rel = 100 * abs(p1 - p0) / max(abs(p0), 1e-9)
    axes[2].bar(["ΔP_fusion"], [p1 - p0], color="#7dcfff", width=0.4)
    axes[2].axhline(0, color="#565f89", lw=0.8)
    axes[2].set_ylabel("MW")
    axes[2].set_title(f"Change ({rel:.2f}% vs baseline)", color="#c0caf5", fontsize=9)
    _annotate_bar_values(axes[2], axes[2].patches, fmt="{:.4f}")
    fig.suptitle("Step 05 — p-¹¹B burn power: baseline | gap-closed | Δ", color="#e0af68", fontsize=10)
    out = figures_dir / "step05_burn_compare.png"
    _save_fig(fig, out)
    return out


def _plant_metrics(steady: dict[str, Any]) -> dict[str, float]:
    return {
        "P_gross": float(steady.get("gross_power_mw", 0)),
        "P_jet": float(steady.get("jet_kinetic_power_mw", 0)),
        "I_beam": float(steady.get("beam_current_ma", 0)),
        "Thrust_kN": float(steady.get("thrust_lbf", 0)) * 4.4482216152605 / 1000.0,
        "mdot": float(steady.get("mass_flow_kgps", 0)),
    }


def plot_step06_plant_compare(figures_dir: Path, report_dir: Path) -> Path | None:
    base = _load_report_step_json(report_dir, "06")
    gap = _load_report_step_json(report_dir, "06_gap")
    if not base or not gap or "steady_state" not in base or "steady_state" not in gap:
        return None
    sb = base["steady_state"]
    sg = gap["steady_state"]
    mb = _plant_metrics(sb)
    mg = _plant_metrics(sg)
    _dark_style()
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    metrics = list(mb.keys())
    x = np.arange(len(metrics))
    w = 0.35
    vals_b = [mb[k] for k in metrics]
    vals_g = [mg[k] for k in metrics]
    axes[0, 0].bar(x - w / 2, vals_b, w, label="Baseline", color="#565f89")
    axes[0, 0].bar(x + w / 2, vals_g, w, label="Gap-closed", color="#7aa2f7")
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(metrics, rotation=25, ha="right")
    axes[0, 0].set_title("Plant outputs", color="#c0caf5", fontsize=9)
    axes[0, 0].legend(fontsize=7)

    # U-stress side by side
    def _stress_bars(ax, steady: dict[str, Any], title: str) -> None:
        stress = [
            ("U1 E", steady["cathode_surface_field_V_m"] / 3e9, "max"),
            ("U2 q", steady["wall_heat_flux_W_m2"] / 2e6, "max"),
            ("U3 cryo", steady["hts_cryo_kw"] / 0.5, "max"),
            ("U4 beam", float(steady["beam_current_ma"]) / 1.0, "min"),
            ("U4 log n", steady["log10_density"] / 11.0, "min"),
        ]
        names = [r[0] for r in stress]
        ratios, colors = [], []
        for _n, raw, kind in stress:
            rv = float(raw)
            display = min(rv, 2.5) if kind == "max" else rv
            ratios.append(display)
            if kind == "min":
                colors.append("#9ece6a" if rv >= 1.0 else "#f7768e")
            else:
                colors.append("#9ece6a" if rv <= 1.0 else "#f7768e")
        ax.barh(names, ratios, color=colors)
        ax.axvline(1.0, color="#e0af68", ls="--")
        ax.set_xlim(0, max(2.6, max(ratios) * 1.1 if ratios else 2.6))
        ax.set_title(title, color="#c0caf5", fontsize=9)

    _stress_bars(axes[0, 1], sb, "U-stress — baseline")
    _stress_bars(axes[0, 2], sg, "U-stress — gap-closed")

    feasible = [
        ("Baseline", bool(base.get("feasible"))),
        ("Gap-closed", bool(gap.get("feasible"))),
    ]
    axes[1, 0].bar(
        [a[0] for a in feasible],
        [1 if a[1] else 0 for a in feasible],
        color=["#9ece6a" if a[1] else "#f7768e" for a in feasible],
        width=0.45,
    )
    axes[1, 0].set_ylim(0, 1.2)
    axes[1, 0].set_ylabel("feasible (1=yes)")
    axes[1, 0].set_title("0D plant feasible flag", color="#c0caf5", fontsize=9)

    deltas = [(mg[k] - mb[k]) / max(abs(mb[k]), 1e-9) * 100 for k in metrics]
    axes[1, 1].bar(metrics, deltas, color="#7dcfff")
    axes[1, 1].axhline(0, color="#565f89", lw=0.8)
    axes[1, 1].set_ylabel("% change vs baseline")
    axes[1, 1].set_title("Relative change (gap − baseline)", color="#c0caf5", fontsize=9)
    axes[1, 1].tick_params(axis="x", rotation=25)

    axes[1, 2].axis("off")
    lines = [
        "Gap-closed uses inverse-solved unobtanium",
        "(proof_mode off, design σv).",
        "",
        f"P_gross: {mb['P_gross']:.3f} → {mg['P_gross']:.3f} MW",
        f"feasible: {base.get('feasible')} → {gap.get('feasible')}",
    ]
    if sg.get("violations"):
        lines.append("Gap violations:")
        for v in sg["violations"][:3]:
            lines.append(f"  • {v}")
    axes[1, 2].text(0.05, 0.95, "\n".join(lines), va="top", fontsize=8, color="#a9b1d6")

    fig.suptitle("Step 06 — 0D plant: baseline vs gap-closed", color="#e0af68", fontsize=10)
    out = figures_dir / "step06_plant_compare.png"
    _save_fig(fig, out)
    return out


def plot_step07_closure_compare(figures_dir: Path, report_dir: Path) -> Path | None:
    base = _load_report_step_json(report_dir, "07")
    gap = _load_report_step_json(report_dir, "07_gap")
    if not base or not gap:
        return None
    _dark_style()
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    def _closure_panel(ax, data: dict[str, Any], title: str) -> float:
        p_jet = float(data["jet_kinetic_power_mw"]) * 1e6
        mdot = float(data["mass_flow_kgps"])
        thrust_n = float(data["thrust_lbf"]) * 4.4482216152605
        p_thrust = (thrust_n**2) / (2 * mdot) if mdot > 1e-9 else 0.0
        ax.bar(["P_jet", "P from F²/2ṁ"], [p_jet / 1e6, p_thrust / 1e6], color=["#7aa2f7", "#9ece6a"])
        ax.set_ylabel("MW equivalent")
        err = float(data.get("closure_rel_error", 0))
        ax.set_title(f"{title}\nclosure err {err:.2%}", color="#c0caf5", fontsize=9)
        return err

    e0 = _closure_panel(axes[0], base, "Baseline")
    e1 = _closure_panel(axes[1], gap, "Gap-closed")
    axes[2].bar(["Δ closure err"], [e1 - e0], color="#7dcfff", width=0.4)
    axes[2].axhline(0, color="#565f89", lw=0.8)
    axes[2].set_ylabel("relative error delta")
    axes[2].set_title("Change in closure error", color="#c0caf5", fontsize=9)
    fig.suptitle("Step 07 — jet closure: baseline | gap-closed | Δ", color="#e0af68", fontsize=10)
    out = figures_dir / "step07_closure_compare.png"
    _save_fig(fig, out)
    return out


def plot_inverse_summary_compare(figures_dir: Path, report_dir: Path) -> Path | None:
    """Single-page headline metrics: baseline vs gap-closed (steps 05–07)."""
    s05b = _load_report_step_json(report_dir, "05")
    s05g = _load_report_step_json(report_dir, "05_gap")
    s06b = _load_report_step_json(report_dir, "06")
    s06g = _load_report_step_json(report_dir, "06_gap")
    s07b = _load_report_step_json(report_dir, "07")
    s07g = _load_report_step_json(report_dir, "07_gap")
    if not all((s05b, s05g, s06b, s06g, s07b, s07g)):
        return None
    _dark_style()
    labels = ["P_fusion", "P_gross", "feasible", "closure err"]
    b_vals = [
        float(s05b.get("fusion_power_mw", 0)),
        float(s06b["steady_state"]["gross_power_mw"]),
        1.0 if s06b.get("feasible") else 0.0,
        float(s07b.get("closure_rel_error", 0)) * 100,
    ]
    g_vals = [
        float(s05g.get("fusion_power_mw", 0)),
        float(s06g["steady_state"]["gross_power_mw"]),
        1.0 if s06g.get("feasible") else 0.0,
        float(s07g.get("closure_rel_error", 0)) * 100,
    ]
    audit = {
        "baseline_sources": ["results/step_05.json", "results/step_06.json", "results/step_07.json"],
        "gap_closed_sources": [
            "results/step_05_gap.json",
            "results/step_06_gap.json",
            "results/step_07_gap.json",
        ],
        "metrics": {labels[i]: {"baseline": b_vals[i], "gap_closed": g_vals[i]} for i in range(4)},
    }
    _write_inverse_audit(report_dir, audit)

    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x - w / 2, b_vals, w, label="Baseline (nominal)", color="#565f89")
    ax.bar(x + w / 2, g_vals, w, label="Gap-closed (inverse knobs)", color="#7aa2f7")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title(
        "Inverse section — headline metrics changed by gap-closed re-run",
        color="#c0caf5",
        fontsize=10,
    )
    ax.legend(fontsize=8)
    for i in range(len(labels)):
        if b_vals[i] != 0:
            pct = 100 * (g_vals[i] - b_vals[i]) / abs(b_vals[i])
            ax.text(i, max(b_vals[i], g_vals[i]) * 1.02, f"{pct:+.1f}%", ha="center", fontsize=8, color="#9ece6a")
    out = figures_dir / "inverse_summary_compare.png"
    _save_fig(fig, out)
    return out


def generate_gap_figures(figures_dir: Path, report_dir: Path) -> dict[str, str | None]:
    """Gap-closed step 03 fusion panels + baseline | gap comparisons + steps 05–07."""
    cfg = load_config()
    rel: dict[str, str | None] = {}

    def put(key: str, path: Path | None) -> None:
        rel[key] = path.name if path else None

    rel.update(plot_step03_gap_figures(figures_dir, report_dir, cfg))

    put("step09_unobtanium_compare", plot_step09_unobtanium_compare(figures_dir, report_dir))
    put("inverse_summary_compare", plot_inverse_summary_compare(figures_dir, report_dir))
    put("step05_burn_compare", plot_step05_burn_compare(figures_dir, report_dir))
    put("step06_plant_compare", plot_step06_plant_compare(figures_dir, report_dir))
    put("step07_closure_compare", plot_step07_closure_compare(figures_dir, report_dir))

    put("step05_gap", plot_step05_burn(figures_dir, file_tag="step05_gap"))
    p6a, p6b = plot_step06_plant(figures_dir, file_tag="step06_gap")
    put("step06_gap_outputs", p6a)
    put("step06_gap_u", p6b)
    put("step07_gap", plot_step07_closure(figures_dir, file_tag="step07_gap"))
    return rel


def generate_all_figures(figures_dir: Path, cfg: dict[str, Any]) -> dict[str, str | None]:
    """Return map of logical name → relative PNG path under report dir."""
    rel: dict[str, str | None] = {}

    def put(key: str, path: Path | None) -> None:
        rel[key] = path.name if path else None

    put("step00", plot_step00_device(figures_dir, cfg))
    put("step01", plot_step01_warpx_last(figures_dir, cfg))
    put("step01_evidence", plot_step01_warpx_evidence(figures_dir, cfg))
    put("step02", plot_step02_rho_norm(figures_dir))
    put("step03_density", _plot_fusion_pair(figures_dir, cfg, field_key="density", basename="step03_density_final.png"))
    put(
        "step03_reaction",
        _plot_fusion_pair(figures_dir, cfg, field_key="reaction_rate", basename="step03_reaction_rate_final.png"),
    )
    put("step03_clump", plot_step03_clump(figures_dir))
    put("step03_radial", plot_step03_radial_final(figures_dir, cfg))
    put("step04", plot_step04_fueling(figures_dir))
    put("step05", plot_step05_burn(figures_dir))
    p6a, p6b = plot_step06_plant(figures_dir)
    put("step06_outputs", p6a)
    put("step06_u", p6b)
    put("step07", plot_step07_closure(figures_dir))
    return rel


def step_result_summary(step: str) -> dict[str, Any]:
    try:
        return load_step_json(step)
    except Exception as exc:
        return {"error": str(exc)}
