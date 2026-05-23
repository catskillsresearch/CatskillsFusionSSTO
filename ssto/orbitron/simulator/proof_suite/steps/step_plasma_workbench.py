"""
Unified plasma workbench — steps 01, 02, 03 on one screen with a single coupled run.

Changing pad/shear (τ, p) or inject/PIC settings marks results STALE until
«Run coupled chain» completes 01 → 02 → 03 together.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ssto.orbitron.simulator.gui.startup_panel import StartupPanel
from ssto.orbitron.simulator.injectants import normalize_injectants_cfg
from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.proof_suite.coupled_fingerprint import (
    coupled_run_fingerprint,
    is_coupled_stale,
    last_coupled_fingerprint,
)
from ssto.orbitron.simulator.proof_suite.longitudinal_viz import (
    _align_pcolormesh_grid,
    compute_longitudinal_preview,
    draw_step01_placeholder,
    draw_step01_warpx_xz,
    fusion_field_color_limits,
)
from ssto.orbitron.simulator.proof_suite.steps.base import ProofStepPanel
from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.widgets import MetricGrid, MplCanvas, apply_dark_axes
from ssto.orbitron.simulator.proof_suite.workers import CoupledPlasmaWorker
from ssto.orbitron.simulator.proof_suite.inputs_builder import simulator_inputs_from_state
from ssto.orbitron.simulator.proof_chain.runners import list_pic_plotfiles
from ssto.orbitron.simulator.types import DeviceGeometry, PadStartupState
from ssto.orbitron.simulator.blender_layout import draw_blender_underlay, engine_axial_layout
from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
from tools.orbitron_proof_chain.chain_lib import align_pic_grid_cells, load_config, pad_startup_from_cfg


def _spin(lo: float, hi: float, val: float, *, dec: int = 2, suf: str = "") -> QDoubleSpinBox:
    s = QDoubleSpinBox()
    s.setRange(lo, hi)
    s.setDecimals(dec)
    s.setValue(val)
    if suf:
        s.setSuffix(suf)
    return s


class PlasmaWorkbenchPanel(ProofStepPanel):
    """Steps 01–03 coupled: WarpX |ρ_e|, ρ_e_norm, fusion s–r."""

    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "01",
            "Plasma workbench (steps 01–03)",
            "One screen, one coupled run: WarpX electron ring → ρ_e_norm → laminar s–r channel. "
            "τ and p (pad/shear) and inject rates must match across all three — no stale partials.",
            "Run coupled chain after changing τ, p, H₂, laser, or PIC grid.",
            state,
            parent,
        )
        self.log.setMaximumHeight(140)
        self._controls_ready = False

        cfg = state.config
        inj = normalize_injectants_cfg(cfg["injectants"])
        pad = cfg["pad"]
        fc = cfg.get("fusion_channel") or {}
        pic = cfg["pic"]

        # --- Controls (left column) ---
        ctrl_wrap = QWidget()
        ctrl_wrap.setMaximumWidth(380)
        ctrl_lay = QVBoxLayout(ctrl_wrap)

        self.lbl_stale = QLabel()
        self.lbl_stale.setWordWrap(True)
        self.lbl_stale.setTextFormat(Qt.TextFormat.RichText)
        self._update_stale_banner()
        ctrl_lay.addWidget(self.lbl_stale)

        self.btn_run_coupled = QPushButton("Run coupled chain (01 → 02 → 03)")
        self.btn_run_coupled.setStyleSheet(
            "font-weight: bold; padding: 10px; background: #414868; color: #c0caf5;"
        )
        self.btn_run_coupled.setToolTip(
            "Atomic run: WarpX PIC, reduce ρ_e_norm, fusion channel OFF+ON cache. "
            "Required after changing ring density τ, cathode pulse p, or inject/PIC settings."
        )
        ctrl_lay.addWidget(self.btn_run_coupled)

        self.chk_skip = QCheckBox("Skip WarpX (dev — placeholder norms)")
        self.chk_skip.setChecked(bool(cfg.get("gui", {}).get("skip_pic", False)))
        ctrl_lay.addWidget(self.chk_skip)

        self.startup = StartupPanel(
            self._on_controls_changed, include_live_checkbox=False, lever_profile="pic_electron_ring"
        )
        ctrl_lay.addWidget(self.startup)

        inj_g = QGroupBox("Fuel inject (step 03)")
        inj_f = QFormLayout(inj_g)
        self.h2 = _spin(0, 500, inj["h2_sccm"], dec=1, suf=" sccm")
        self.laser_hz = _spin(0, 50, inj["laser_ablation_hz"], dec=1, suf=" Hz")
        self.compressor = _spin(0, 1, pad["compressor"], dec=2)
        self.lbl_c_eff = QLabel("c_eff = —")
        self.lbl_rate = QLabel("λ = —")
        inj_f.addRow("H₂", self.h2)
        inj_f.addRow("Laser Hz", self.laser_hz)
        inj_f.addRow("Compressor c", self.compressor)
        inj_f.addRow("", self.lbl_c_eff)
        inj_f.addRow("", self.lbl_rate)
        ctrl_lay.addWidget(inj_g)

        pic_g = QGroupBox("WarpX grid")
        pf = QFormLayout(pic_g)
        self.pic_steps = QSpinBox()
        self.pic_steps.setRange(50, 5000)
        self.pic_steps.setValue(int(pic["steps"]))
        self.pic_grid = QSpinBox()
        self.pic_grid.setRange(8, 2048)
        self.pic_grid.setSingleStep(8)
        self.pic_grid.setKeyboardTracking(False)
        self.pic_grid.setValue(align_pic_grid_cells(int(pic.get("grid_cells", 512))))
        self.pic_diag = QSpinBox()
        self.pic_diag.setRange(10, 500)
        self.pic_diag.setValue(int(pic.get("diag_period", 40)))
        pf.addRow("PIC steps", self.pic_steps)
        pf.addRow("Grid N×N", self.pic_grid)
        pf.addRow("Snapshot every", self.pic_diag)
        ctrl_lay.addWidget(pic_g)

        lam_g = QGroupBox("Laminar / clump (step 03)")
        lf = QFormLayout(lam_g)
        self.chk_laminar = QCheckBox("Laminar relaminarization ON")
        self.chk_laminar.setChecked(pad.get("laminar_relaminarization", True))
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 999_999)
        self.seed_spin.setValue(int(fc.get("stochastic_seed", 42)))
        self.noise = _spin(0, 0.5, float(fc.get("noise_fraction_off", 0.14)), dec=3)
        lf.addRow(self.chk_laminar)
        lf.addRow("RNG seed", self.seed_spin)
        lf.addRow("Noise (OFF)", self.noise)
        ctrl_lay.addWidget(lam_g)
        ctrl_lay.addStretch()

        for w in (
            self.h2,
            self.laser_hz,
            self.compressor,
            self.noise,
            self.pic_steps,
            self.pic_grid,
            self.pic_diag,
        ):
            if hasattr(w, "valueChanged"):
                w.valueChanged.connect(self._on_controls_changed)
        self.seed_spin.valueChanged.connect(self._on_controls_changed)
        self.chk_laminar.toggled.connect(self._on_controls_changed)
        self.chk_skip.toggled.connect(self._on_controls_changed)

        # --- Visuals (right, large) ---
        viz = QSplitter(Qt.Orientation.Vertical)

        warpx_w = QWidget()
        warpx_lay = QVBoxLayout(warpx_w)
        warpx_lay.addWidget(QLabel("<b>Step 01 — WarpX |ρ_e|</b>"))
        self.canvas_warpx = MplCanvas(10, 3.8)
        warpx_lay.addWidget(self.canvas_warpx, stretch=1)
        warpx_scrub = QHBoxLayout()
        self.btn_play = QPushButton("Play")
        self.btn_pause = QPushButton("Pause")
        self.lon_time = QSlider(Qt.Orientation.Horizontal)
        self.lon_lbl = QLabel("t = —")
        warpx_scrub.addWidget(self.btn_play)
        warpx_scrub.addWidget(self.btn_pause)
        warpx_scrub.addWidget(self.lon_time, stretch=1)
        warpx_scrub.addWidget(self.lon_lbl)
        warpx_lay.addLayout(warpx_scrub)
        viz.addWidget(warpx_w)

        norm_w = QWidget()
        norm_lay = QHBoxLayout(norm_w)
        norm_lay.addWidget(QLabel("<b>Step 02 — ρ_e_norm</b>"))
        self.canvas_norm = MplCanvas(4, 2.2)
        norm_lay.addWidget(self.canvas_norm, stretch=1)
        viz.addWidget(norm_w)

        fus_w = QWidget()
        fus_lay = QVBoxLayout(fus_w)
        fus_lay.addWidget(QLabel("<b>Step 03 — Fusion channel n(s,r) OFF | ON</b>"))
        self.field_combo = QComboBox()
        self.field_combo.addItems(["Fuel density n(s,r)", "Reaction rate R(s,r)"])
        fus_lay.addWidget(self.field_combo)
        self.canvas_fus = MplCanvas(12, 4.5)
        fus_lay.addWidget(self.canvas_fus, stretch=1)
        fus_bottom = QSplitter(Qt.Orientation.Horizontal)
        self.canvas_clump = MplCanvas(5, 2.5)
        self.canvas_radial = MplCanvas(5, 2.5)
        fus_bottom.addWidget(self.canvas_clump)
        fus_bottom.addWidget(self.canvas_radial)
        fus_lay.addWidget(fus_bottom)
        fus_scrub = QHBoxLayout()
        fus_scrub.addWidget(QLabel("Time"))
        self.fus_time = QSlider(Qt.Orientation.Horizontal)
        self.fus_lbl = QLabel("t = —")
        fus_scrub.addWidget(self.fus_time, stretch=1)
        fus_scrub.addWidget(self.fus_lbl)
        fus_lay.addLayout(fus_scrub)
        viz.addWidget(fus_w)
        viz.setStretchFactor(0, 2)
        viz.setStretchFactor(2, 4)

        body = QSplitter(Qt.Orientation.Horizontal)
        body.addWidget(ctrl_wrap)
        body.addWidget(viz)
        body.setStretchFactor(1, 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)
        self.place_inputs_above_run(scroll)

        self.metrics = MetricGrid(4)
        self._layout.insertWidget(self._layout.indexOf(self.toolbar), self.metrics)

        self._lon_xy = None
        self._npz_on = None
        self._npz_off = None
        self._live_timer = QTimer(self)
        self._live_timer.setInterval(350)
        self._live_timer.timeout.connect(self._on_play_tick)

        self.btn_run_coupled.clicked.connect(self._run_coupled)
        self.toolbar.btn_run.hide()
        self.toolbar.btn_refresh.clicked.connect(self.refresh_from_artifacts)
        self.btn_play.clicked.connect(self._start_play)
        self.btn_pause.clicked.connect(self._stop_play)
        self.lon_time.valueChanged.connect(self._draw_warpx)
        self.fus_time.valueChanged.connect(self._draw_fusion)
        self.field_combo.currentIndexChanged.connect(self._draw_fusion)

        self._controls_ready = True
        self._load_controls_from_config()
        self.refresh_from_artifacts()

    def _load_controls_from_config(self) -> None:
        p = self._state.config["pad"]
        self.startup.apply_pad_state(
            PadStartupState(
                pad_apu_online=bool(p.get("pad_apu_online", True)),
                starter_engage=bool(p.get("starter_engage", True)),
                bleed_air_open=bool(p.get("bleed_air_open", True)),
                vacuum_interlock_ok=bool(p.get("vacuum_interlock_ok", True)),
                laser_armed=bool(p.get("laser_armed", True)),
                hv_enabled=bool(p.get("hv_enabled", True)),
                startup_trigger=bool(p.get("startup_trigger", True)),
                throttle=float(p["throttle"]),
                compressor=float(p["compressor"]),
                cathode_pulse=float(p["cathode_pulse"]),
            )
        )
        inj = normalize_injectants_cfg(self._state.config["injectants"])
        self.h2.setValue(inj["h2_sccm"])
        self.laser_hz.setValue(inj["laser_ablation_hz"])
        self.compressor.setValue(p["compressor"])
        fc = self._state.config.get("fusion_channel") or {}
        self.seed_spin.setValue(int(fc.get("stochastic_seed", 42)))
        self.noise.setValue(float(fc.get("noise_fraction_off", 0.14)))
        self.chk_laminar.setChecked(bool(p.get("laminar_relaminarization", True)))

    def _sync_config(self) -> None:
        pad = self.startup.pad_state()
        self._state.update_pad(
            throttle=pad.throttle,
            compressor=float(self.compressor.value()),
            cathode_pulse=pad.cathode_pulse,
            laminar=self.chk_laminar.isChecked(),
            vacuum_interlock_ok=pad.vacuum_interlock_ok,
            laser_armed=pad.laser_armed,
            hv_enabled=pad.hv_enabled,
        )
        p = self._state.config["pad"]
        p["pad_apu_online"] = pad.pad_apu_online
        p["starter_engage"] = pad.starter_engage
        p["bleed_air_open"] = pad.bleed_air_open
        p["startup_trigger"] = pad.startup_trigger
        self._state.update_injectants(
            h2_sccm=self.h2.value(),
            laser_ablation_hz=self.laser_hz.value(),
        )
        self._state.update_fusion_channel(
            stochastic_seed=int(self.seed_spin.value()),
            noise_fraction_off=float(self.noise.value()),
        )
        aligned = align_pic_grid_cells(int(self.pic_grid.value()))
        if aligned != self.pic_grid.value():
            self.pic_grid.setValue(aligned)
        self._state.update_pic_settings(
            steps=self.pic_steps.value(),
            diag_period=self.pic_diag.value(),
            grid_cells=self.pic_grid.value(),
            skip_pic=self.chk_skip.isChecked(),
        )
        self._state.save()
        self._update_rate_labels()

    def _on_controls_changed(self) -> None:
        if not self._controls_ready:
            return
        self._sync_config()
        self._update_stale_banner()
        self.refresh_from_artifacts()

    def _update_rate_labels(self) -> None:
        p = self._state.config["pad"]
        pad_st = PadStartupState(
            pad_apu_online=bool(p.get("pad_apu_online", True)),
            starter_engage=bool(p.get("starter_engage", True)),
            bleed_air_open=bool(p.get("bleed_air_open", True)),
            vacuum_interlock_ok=bool(p.get("vacuum_interlock_ok", True)),
            laser_armed=bool(p.get("laser_armed", True)),
            hv_enabled=bool(p.get("hv_enabled", True)),
            startup_trigger=bool(p.get("startup_trigger", True)),
            throttle=float(p["throttle"]),
            compressor=float(self.compressor.value()),
            cathode_pulse=float(p["cathode_pulse"]),
        )
        st = evaluate_pad_status(pad_st)
        fc = self._state.config.get("fusion_channel") or {}
        h2, laser = self.h2.value(), self.laser_hz.value()
        lam = math.sqrt(laser / max(float(fc.get("laser_ref_hz", 10)), 0.1))
        rate = (h2 / max(float(fc.get("h2_ref_sccm", 80)), 1.0)) * lam
        self.lbl_c_eff.setText(f"c_eff = {st.compressor_effective:.2f}")
        self.lbl_rate.setText(f"λ = {max(0.05, min(4.0, rate)):.2f}")

    def _update_stale_banner(self) -> None:
        stale = is_coupled_stale(self._state.config)
        cur = coupled_run_fingerprint(self._state.config)
        pad_status = evaluate_pad_status(pad_startup_from_cfg(self._state.config["pad"]))
        interlock_note = ""
        if not pad_status.reactor_armed:
            interlock_note = (
                '<br><span style="color:#e0af68;">Reactor not armed — step 03 fuel and R(s,r) '
                "need APU→starter→bleed→vacuum→laser→HV→IGNITE. "
                f"{' '.join(pad_status.interlock_messages)}</span>"
            )
        if stale or last_coupled_fingerprint(self._state.config) is None:
            self.lbl_stale.setText(
                '<span style="color:#f7768e; font-weight:bold;">STALE — plots may not match '
                "current τ, p, or inject settings. Click <b>Run coupled chain</b>.</span>"
                + interlock_note
            )
            self.lbl_stale.setStyleSheet(
                "background:#3b2240; padding:8px; border-radius:4px; border:1px solid #f7768e;"
            )
        else:
            self.lbl_stale.setText(
                f'<span style="color:#9ece6a;">Coupled run matches controls '
                f"(τ={cur['throttle']:.2f}, p={cur['cathode_pulse']:.2f}).</span>"
                + interlock_note
            )
            self.lbl_stale.setStyleSheet(
                "background:#1f2e24; padding:8px; border-radius:4px; border:1px solid #9ece6a;"
            )

    def _pic_diags_dir(self) -> Path:
        return Path(load_config()["chain_root"]) / "01_pic" / "diags"

    def _run_coupled(self) -> None:
        self._sync_config()
        self.log.clear()
        self.btn_run_coupled.setEnabled(False)
        self.toolbar.progress.show()
        w = CoupledPlasmaWorker(
            skip_pic=self.chk_skip.isChecked(),
            n_steps=self.pic_steps.value(),
        )
        w.log_line.connect(self.log.append_line)
        w.finished.connect(self._on_coupled_done)
        w.start()
        self._worker = w

    def _on_coupled_done(self, result: dict | None, error: str | None) -> None:
        self.toolbar.progress.hide()
        self.btn_run_coupled.setEnabled(True)
        if error:
            self.log.append_line(f"ERROR: {error}")
            self.gate.set_gate(f"Coupled run failed: {error[:120]}", ok=False)
            return
        self.log.append_line("Coupled chain finished OK.")
        self._state.reload()
        self._update_stale_banner()
        self.refresh_from_artifacts()
        self.step_completed.emit("01")
        self.status_changed.emit()

    def _gather_inputs(self):
        pad = self.startup.pad_state()
        pad = PadStartupState(
            pad_apu_online=pad.pad_apu_online,
            starter_engage=pad.starter_engage,
            bleed_air_open=pad.bleed_air_open,
            vacuum_interlock_ok=pad.vacuum_interlock_ok,
            laser_armed=pad.laser_armed,
            hv_enabled=pad.hv_enabled,
            startup_trigger=pad.startup_trigger,
            throttle=pad.throttle,
            compressor=float(self.compressor.value()),
            cathode_pulse=pad.cathode_pulse,
            laminar_relaminarization=self.chk_laminar.isChecked(),
        )
        return simulator_inputs_from_state(self._state, pad)

    def _draw_warpx(self) -> None:
        stale = is_coupled_stale(self._state.config)
        if self._lon_xy is None:
            msg = "No WarpX data — run coupled chain."
            if stale:
                msg += " (controls changed since last run.)"
            draw_step01_placeholder(self.canvas_warpx.figure, msg)
            self.canvas_warpx.draw()
            return
        inputs = self._gather_inputs()
        idx = self.lon_time.value()
        draw_step01_warpx_xz(
            self.canvas_warpx.figure,
            self._lon_xy,
            idx,
            inputs=inputs,
            delta_vs_first=False,
        )
        t = self._lon_xy.time_s[idx]
        n = len(self._lon_xy.time_s)
        self.lon_lbl.setText(f"Snapshot {idx + 1}/{n}  t={t:.3e} s")
        if stale:
            self.canvas_warpx.figure.text(
                0.5,
                0.02,
                "STALE vs current τ/p",
                ha="center",
                color="#f7768e",
                fontsize=11,
                fontweight="bold",
            )
        self.canvas_warpx.draw()

    def _load_npz(self, path: Path | None) -> dict | None:
        if path is None or not path.is_file():
            return None
        z = np.load(path)
        return {k: z[k] for k in z.files}

    def _draw_fusion(self) -> None:
        stale = is_coupled_stale(self._state.config)
        if self._npz_on is None or self._npz_off is None:
            fig = self.canvas_fus.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "Run coupled chain for OFF|ON fusion channel.",
                ha="center",
                va="center",
                color="#f7768e" if stale else "#565f89",
            )
            self.canvas_fus.draw()
            return
        idx = self.fus_time.value()
        use_r = self.field_combo.currentIndex() == 1
        field_key = "reaction_rate" if use_r else "density"
        vmin, vmax = fusion_field_color_limits(self._npz_off[field_key], self._npz_on[field_key])
        all_zero_r = use_r and vmax is not None and vmax <= 0.0
        g = self._state.config["geometry"]
        geo = DeviceGeometry(
            g["r_anode_m"],
            g["r_cathode_m"],
            g["length_m"],
            g["V_cathode_v"],
            g["B_axial_tesla"],
        )
        fig = self.canvas_fus.figure
        fig.clear()
        ax_off = fig.add_subplot(121)
        ax_on = fig.add_subplot(122)
        im = None
        for ax, npz, title in (
            (ax_off, self._npz_off, "Laminar OFF"),
            (ax_on, self._npz_on, "Laminar ON"),
        ):
            data = npz[field_key]
            s, r = npz["s_m"], npz["r_m"]
            layout = engine_axial_layout(geo)
            draw_blender_underlay(ax, layout, LongitudinalFocus.FUSION_CHANNEL_SR, symmetric=False)
            if all_zero_r:
                ax.text(
                    0.5,
                    0.5,
                    "R(s,r) = 0\nRe-run coupled chain with\nIGNITE interlocks satisfied",
                    ha="center",
                    va="center",
                    color="#f7768e",
                    fontsize=10,
                    transform=ax.transAxes,
                )
                apply_dark_axes(ax)
                ax.set_title(title, color="#c0caf5")
                continue
            xh, yv, sl = _align_pcolormesh_grid(s, r, data[idx])
            im = ax.pcolormesh(
                xh, yv, sl, shading="auto", cmap="magma", alpha=0.75, vmin=vmin, vmax=vmax
            )
            apply_dark_axes(ax)
            ax.set_title(title, color="#c0caf5")
            ax.set_xlabel("s [m]")
            ax.set_ylabel("r [m]")
        if im is not None:
            fig.colorbar(im, ax=[ax_off, ax_on], fraction=0.046, pad=0.04)
        t = float(self._npz_on["time_s"][idx])
        nt = len(self._npz_on["time_s"])
        d0 = self._npz_on[field_key][0]
        d_now = self._npz_on[field_key][idx]
        delta = float(np.max(np.abs(d_now - d0)))
        self.fus_lbl.setText(
            f"Frame {idx + 1}/{nt}  t={t:.3e} s  |Δ{field_key}|={delta:.2e}"
        )
        if stale:
            fig.text(0.5, 0.01, "STALE vs current controls", ha="center", color="#f7768e", fontsize=11)
        fig.tight_layout()
        self.canvas_fus.draw()

    def _draw_norm_bar(self) -> None:
        stale = is_coupled_stale(self._state.config)
        data = self._state.try_load_step("02")
        fig = self.canvas_norm.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if data and not data.get("skipped"):
            re = float(data.get("rho_e_norm", 1))
            color = "#7aa2f7" if 0.2 <= re <= 3.0 else "#f7768e"
            ax.bar(["ρ_e_norm"], [re], color=color, width=0.4)
            ax.axhspan(0.2, 3.0, color="#9ece6a", alpha=0.12)
            ax.set_ylim(0, max(3.5, re * 1.15))
            ax.set_ylabel("Electron ring ×")
        else:
            ax.text(0.5, 0.5, "—", ha="center", color="#565f89")
        if stale:
            ax.set_title("STALE", color="#f7768e")
        fig.tight_layout()
        self.canvas_norm.draw()

    def _draw_clump_charts(self) -> None:
        if self._npz_on is None:
            return
        figc = self.canvas_clump.figure
        figc.clear()
        axc = figc.add_subplot(111)
        axc.plot(self._npz_on["time_s"], self._npz_on["clump_index"], color="#9ece6a", label="ON")
        if self._npz_off is not None:
            axc.plot(
                self._npz_off["time_s"],
                self._npz_off["clump_index"],
                color="#f7768e",
                label="OFF",
            )
        axc.axhline(2.8, color="#e0af68", ls="--", label="pass")
        axc.legend(fontsize=8)
        axc.set_title("Clump index", color="#c0caf5")
        figc.tight_layout()
        self.canvas_clump.draw()

        figr = self.canvas_radial.figure
        figr.clear()
        axr = figr.add_subplot(111)
        last = self._npz_on["density"][-1]
        axr.plot(self._npz_on["r_m"], np.mean(last, axis=0), color="#9ece6a")
        axr.set_title("⟨n⟩_s(r) final", color="#c0caf5")
        figr.tight_layout()
        self.canvas_radial.draw()

    def refresh_from_artifacts(self) -> None:
        self._update_stale_banner()
        self._update_rate_labels()
        stale = is_coupled_stale(self._state.config)
        diags = self._pic_diags_dir()
        if list_pic_plotfiles(diags):
            try:
                inputs = self._gather_inputs()
                self._lon_xy = compute_longitudinal_preview(
                    inputs,
                    LongitudinalFocus.CORE_TUBE,
                    laminar_on=True,
                    pic_diags=diags,
                    use_heuristic_pic=False,
                    warpx_xy_direct=True,
                )
                n = len(self._lon_xy.time_s)
                self.lon_time.setMaximum(max(0, n - 1))
                self.lon_time.setValue(min(self.lon_time.value(), max(0, n - 1)))
            except Exception as exc:
                self._lon_xy = None
                draw_step01_placeholder(self.canvas_warpx.figure, str(exc))
                self.canvas_warpx.draw()
        else:
            self._lon_xy = None
        self._draw_warpx()
        self._draw_norm_bar()

        d3 = self._state.try_load_step("03")
        if d3:
            self._npz_on = self._load_npz(
                Path(d3["fields_laminar_on_npz"]) if d3.get("fields_laminar_on_npz") else None
            )
            self._npz_off = self._load_npz(
                Path(d3["fields_laminar_off_npz"]) if d3.get("fields_laminar_off_npz") else None
            )
            if self._npz_on is not None:
                nt = len(self._npz_on["time_s"])
                self.fus_time.setMaximum(max(0, nt - 1))
                self.fus_time.setValue(min(self.fus_time.value(), max(0, nt - 1)))
        else:
            self._npz_on = self._npz_off = None
        self._draw_fusion()
        self._draw_clump_charts()

        d2 = self._state.try_load_step("02")
        d3 = self._state.try_load_step("03")
        if d3 and not stale:
            ci = float(d3.get("clump_index_final", 0))
            red = float(d3.get("clump_reduction_ratio", 1))
            ok = ci <= 2.8 and red >= 1.25
            self.gate.set_gate(
                "Coupled chain OK — laminar gate passed."
                if ok
                else f"Coupled run done; tune p/noise (ON clump={ci:.2f}, OFF/ON={red:.2f}×).",
                ok=ok,
            )
            self.metrics.set_metrics(
                [
                    ("ρ_e_norm", f"{float(d2.get('rho_e_norm', 0)):.2f}" if d2 else "—", "step 02", "#7aa2f7"),
                    ("Clump ON", f"{ci:.2f}", "≤2.8", "#9ece6a" if ci <= 2.8 else "#f7768e"),
                    ("OFF/ON", f"{red:.2f}×", "≥1.25", "#9ece6a" if red >= 1.25 else "#f7768e"),
                    ("λ", f"{float(d3.get('inject_rate_scale', 0)):.2f}", "inject", "#a9b1d6"),
                ]
            )
        elif stale:
            self.gate.set_gate("STALE — run coupled chain to sync 01–03.", ok=None)
            self.metrics.set_metrics(
                [
                    ("Status", "STALE", "run coupled", "#f7768e"),
                    ("τ", f"{self._state.config['pad']['throttle']:.2f}", "pad", "#a9b1d6"),
                    ("p", f"{self._state.config['pad']['cathode_pulse']:.2f}", "shear", "#a9b1d6"),
                    ("", "", "", "#a9b1d6"),
                ]
            )
        else:
            self.gate.set_gate(self._gate_hint, ok=None)

    def _start_play(self) -> None:
        if self._lon_xy is None or len(self._lon_xy.time_s) <= 1:
            return
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self._live_timer.start()

    def _stop_play(self) -> None:
        self._live_timer.stop()
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(False)

    def _on_play_tick(self) -> None:
        if self._lon_xy is None:
            return
        n = len(self._lon_xy.time_s)
        nxt = (self.lon_time.value() + 1) % n
        self.lon_time.blockSignals(True)
        self.lon_time.setValue(nxt)
        self.lon_time.blockSignals(False)
        self._draw_warpx()

    def stop_snapshot_playback(self) -> None:
        self._stop_play()
