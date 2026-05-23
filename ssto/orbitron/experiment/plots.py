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
    layout = engine_axial_layout(geo)
    _dark_style()
    fig, (ax_off, ax_on) = plt.subplots(1, 2, figsize=(12, 4.5))
    im = None
    for ax, z, title in ((ax_off, z_off, "Laminar OFF"), (ax_on, z_on, "Laminar ON")):
        draw_blender_underlay(ax, layout, LongitudinalFocus.FUSION_CHANNEL_SR, symmetric=False)
        if field_key == "reaction_rate" and vmax is not None and vmax <= 0:
            ax.text(0.5, 0.5, "R = 0", ha="center", va="center", transform=ax.transAxes)
            continue
        xh, yv, sl = _align_pcolormesh_grid(z["s_m"], z["r_m"], z[field_key][idx])
        im = ax.pcolormesh(xh, yv, sl, shading="auto", cmap="magma", vmin=vmin, vmax=vmax, alpha=0.85)
        ax.set_title(title)
        ax.set_xlabel("s [m]")
        ax.set_ylabel("r [m]")
    if im is not None:
        fig.colorbar(im, ax=[ax_off, ax_on], fraction=0.046, pad=0.04)
    fig.suptitle(f"Step 03 — {field_key} (final frame)", color="#c0caf5")
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
    ax.plot(z_on["time_s"], z_on["clump_index"], color="#9ece6a", label="ON")
    z_off = np.load(paths[0])
    ax.plot(z_off["time_s"], z_off["clump_index"], color="#f7768e", label="OFF")
    ax.axhline(2.8, color="#e0af68", ls="--", label="pass ≤2.8")
    ax.legend(fontsize=8)
    ax.set_title("Clump index C_k")
    ax.set_xlabel("time [s]")
    out = figures_dir / "step03_clump_index.png"
    _save_fig(fig, out)
    return out


def plot_step03_radial_final(figures_dir: Path) -> Path | None:
    try:
        d3 = load_step_json("03")
        on_p = d3.get("fields_laminar_on_npz")
        if not on_p:
            return None
        z = np.load(on_p)
    except Exception:
        return None
    _dark_style()
    fig, ax = plt.subplots(figsize=(6, 3.5))
    last = z["density"][-1]
    ax.plot(z["r_m"], np.mean(last, axis=0), color="#9ece6a")
    ax.set_title("⟨n⟩_s(r) final (laminar ON)")
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
    fig, ax = plt.subplots(figsize=(5, 3.5))
    target = 3.5
    p_fus = float(data.get("fusion_power_mw", 0))
    ax.bar(
        ["Target", "P_fusion"],
        [target, p_fus],
        color=["#565f89", "#9ece6a" if p_fus >= target * 0.9 else "#f7768e"],
    )
    ax.set_ylabel("MW")
    ax.set_title(f"Shortfall {data.get('shortfall_mw', 0):.2f} MW")
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
    figb, axb = plt.subplots(figsize=(8, 3.5))
    labels = ["P_gross", "P_jet", "Q_wall", "I_beam", "Thrust", "ṁ"]
    values = [
        s["gross_power_mw"],
        s["jet_kinetic_power_mw"],
        s["wall_heat_kw"] / 1000,
        s["beam_current_ma"],
        s["thrust_lbf"] * 0.00444822,
        s["mass_flow_kgps"],
    ]
    axb.bar(labels, values, color="#7aa2f7", alpha=0.85)
    axb.set_title("Steady-state outputs")
    axb.tick_params(axis="x", rotation=25)
    p1 = figures_dir / "step06_plant_outputs.png"
    _save_fig(figb, p1)

    figu, axu = plt.subplots(figsize=(6, 3.5))
    checks = [
        ("U1 E_cath", s["cathode_surface_field_V_m"] / 3e9),
        ("U2 q_wall", s["wall_heat_flux_W_m2"] / 2e6),
        ("U3 cryo", s["hts_cryo_kw"] / 0.5),
        ("U4 beam", s["beam_current_ma"]),
        ("log10 n", s["log10_density"] / 11.0),
    ]
    names = [c[0] for c in checks]
    ratios = [min(c[1], 2.5) for c in checks]
    colors = ["#9ece6a" if r <= 1 else "#f7768e" for r in ratios]
    axu.barh(names, ratios, color=colors)
    axu.axvline(1.0, color="#e0af68", ls="--")
    axu.set_xlabel("Ratio to limit")
    axu.set_title("U1–U4 stress")
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
    put("step03_radial", plot_step03_radial_final(figures_dir))
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
