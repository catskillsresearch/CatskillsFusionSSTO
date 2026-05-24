"""Headless matplotlib figures for experiment reports (Agg backend)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from ssto.orbitron.simulator.blender_layout import draw_blender_underlay, engine_axial_layout
from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
from ssto.orbitron.simulator.proof_chain.runners import base_inputs, list_pic_plotfiles
from ssto.orbitron.simulator.proof_suite.longitudinal_viz import (
    _align_pcolormesh_grid,
    compute_longitudinal_preview,
    draw_step01_warpx_xz,
    fusion_field_color_limits,
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
    if not list_pic_plotfiles(diags):
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
    out = figures_dir / "step01_warpx_rho_e_last.png"
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
        ax.text(0.5, 0.5, "SKIP_PIC", ha="center", va="center", color="#565f89")
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
    z_off = np.load(off_p)
    z_on = np.load(on_p)
    stacks = [z_off[field_key], z_on[field_key]]
    vmin, vmax = fusion_field_color_limits(*stacks)
    idx = len(z_on["time_s"]) - 1
    geo = _geometry_from_cfg(cfg)
    r_a = geo.r_anode_m
    layout = engine_axial_layout(geo)
    field_label = "Fuel density n(s,r)" if field_key == "density" else "Reaction rate R(s,r)"
    _dark_style()
    # Taller figure + bore-only r zoom so the 4 cm radius is readable.
    fig, (ax_off, ax_on) = plt.subplots(1, 2, figsize=(12, 6))
    im = None
    for ax, z, title in ((ax_off, z_off, "Laminar OFF"), (ax_on, z_on, "Laminar ON")):
        draw_blender_underlay(ax, layout, LongitudinalFocus.FUSION_CHANNEL_SR, symmetric=False)
        if field_key == "reaction_rate" and vmax is not None and vmax <= 0:
            ax.text(
                0.5,
                0.5,
                "R = 0 — check IGNITE interlocks",
                ha="center",
                va="center",
                transform=ax.transAxes,
                color="#f7768e",
            )
            continue
        xh, yv, sl = _align_pcolormesh_grid(z["s_m"], z["r_m"], z[field_key][idx])
        im = ax.pcolormesh(xh, yv, sl, shading="auto", cmap="magma", vmin=vmin, vmax=vmax, alpha=0.85)
        ax.set_ylim(0.0, r_a * 1.12)
        ax.axhline(r_a, color="#e0af68", ls="--", lw=0.9, alpha=0.85)
        ax.set_title(title, color="#c0caf5")
        ax.set_xlabel("s [m]")
        ax.set_ylabel("r [m]")
    if im is not None:
        fig.colorbar(im, ax=[ax_off, ax_on], fraction=0.046, pad=0.04)
    fig.suptitle(
        f"Step 03 — {field_label} (final frame, r ≤ r_anode dashed)",
        color="#c0caf5",
        y=0.98,
    )
    out = figures_dir / basename
    _save_fig(fig, out)
    return out


def plot_step03_clump(figures_dir: Path) -> Path | None:
    try:
        d3 = load_step_json("03")
    except Exception:
        return None
    paths = [d3.get("fields_laminar_off_npz"), d3.get("fields_laminar_on_npz")]
    if not all(paths):
        return None
    _dark_style()
    fig, ax = plt.subplots(figsize=(7, 3.5))
    z_on = np.load(paths[1])
    z_off = np.load(paths[0])
    ax.plot(z_on["time_s"], z_on["clump_index"], color="#9ece6a", label="ON")
    ax.plot(z_off["time_s"], z_off["clump_index"], color="#f7768e", label="OFF")
    ax.axhline(2.8, color="#e0af68", ls="--", label="ON pass ≤ 2.8")
    ci_on = float(d3.get("clump_index_final", z_on["clump_index"][-1]))
    ci_off = float(d3.get("clump_index_off", z_off["clump_index"][-1]))
    ratio = float(d3.get("clump_reduction_ratio", ci_off / max(ci_on, 1e-6)))
    ax.legend(fontsize=8, loc="lower right")
    ax.set_title(
        f"Clump index C_k  (OFF/ON={ratio:.2f}×, need ≥1.25×)",
        color="#c0caf5",
    )
    ax.set_xlabel("time [s]")
    ax.set_ylabel("P95/median(n) in bore")
    out = figures_dir / "step03_clump_index.png"
    _save_fig(fig, out)
    return out


def plot_step03_radial_final(figures_dir: Path, cfg: dict[str, Any]) -> Path | None:
    try:
        d3 = load_step_json("03")
        on_p = d3.get("fields_laminar_on_npz")
        if not on_p:
            return None
        z = np.load(on_p)
    except Exception:
        return None
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
    ax.set_title("⟨n⟩_s(r) final — laminar ON (drop at dashed line = bore wall)", color="#c0caf5")
    ax.set_xlabel("r [m]")
    ax.set_ylabel("n [m⁻³]")
    out = figures_dir / "step03_radial_n_final.png"
    _save_fig(fig, out)
    return out


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


def plot_step05_burn(figures_dir: Path) -> Path | None:
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
        color=["#565f89", "#9ece6a" if short < 0.5 else "#f7768e"],
        width=0.45,
    )
    _annotate_bar_values(ax, bars, fmt="{:.3f}")
    ax.set_ylabel("MW")
    if p_fus > 0 and p_fus < target * 0.5:
        ax.set_yscale("log")
        ax.set_ylim(max(p_fus * 0.5, 0.05), target * 1.5)
    else:
        ax.set_ylim(0, max(target * 1.08, p_fus * 1.15))
    ax.set_title(
        f"P_fusion = {p_fus:.4f} MW  |  shortfall {short:.3f} MW vs {target:.1f} MW target",
        color="#c0caf5",
        fontsize=10,
    )
    out = figures_dir / "step05_burn_power.png"
    _save_fig(fig, out)
    return out


def plot_step06_plant(figures_dir: Path) -> tuple[Path | None, Path | None]:
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

    figb.suptitle("Steady-state plant — separate units per panel", color="#c0caf5", y=1.01)
    figb.tight_layout()
    p1 = figures_dir / "step06_plant_outputs.png"
    _save_fig(figb, p1)

    figu, axu = plt.subplots(figsize=(7, 4))
    # (label, ratio, pass if ratio <= limit, pass if ratio >= limit)
    stress = [
        ("U1 E_cath", s["cathode_surface_field_V_m"] / 3e9, "max", 1.0),
        ("U2 q_wall", s["wall_heat_flux_W_m2"] / 2e6, "max", 1.0),
        ("U3 cryo", s["hts_cryo_kw"] / 0.5, "max", 1.0),
        ("U4 beam", float(s["beam_current_ma"]) / 1.0, "min", 1.0),
        ("log10 n", s["log10_density"] / 11.0, "max", 1.0),
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
    axu.set_xlabel("Ratio to limit (U4 = mA / 1 mA floor)")
    axu.set_title("U1–U4 stress (green = pass)", color="#c0caf5")
    axu.legend(fontsize=8, loc="lower right")
    p2 = figures_dir / "step06_u_stress.png"
    _save_fig(figu, p2)
    return p1, p2


def plot_step07_closure(figures_dir: Path) -> Path | None:
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
    ax.set_title(f"Closure rel error {data['closure_rel_error']:.2%}")
    out = figures_dir / "step07_jet_closure.png"
    _save_fig(fig, out)
    return out


def generate_all_figures(figures_dir: Path, cfg: dict[str, Any]) -> dict[str, str | None]:
    """Return map of logical name → relative PNG path under report dir."""
    rel: dict[str, str | None] = {}

    def put(key: str, path: Path | None) -> None:
        rel[key] = path.name if path else None

    put("step00", plot_step00_device(figures_dir, cfg))
    put("step01", plot_step01_warpx_last(figures_dir, cfg))
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
