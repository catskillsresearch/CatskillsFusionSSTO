"""Proof suite steps 00–02: SSOT, PIC, reduce."""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from matplotlib.patches import Circle
from PySide6.QtCore import Qt, QTimer, Signal
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
from ssto.orbitron.simulator.proof_suite.workers import WarpXWorker
from ssto.orbitron.simulator.types import PadStartupState

from ssto.orbitron.simulator.proof_chain.runners import (
    list_pic_plotfiles,
    run_step_00,
    run_step_02,
)
from tools.orbitron_proof_chain.chain_lib import align_pic_grid_cells
from ssto.orbitron.simulator.proof_suite.steps.base import ProofStepPanel
from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.widgets import MetricGrid, MplCanvas
from ssto.orbitron.simulator.proof_suite.workers import StepWorker
from ssto.orbitron.simulator.injectants import normalize_injectants_cfg
from ssto.orbitron.simulator.types import DeviceGeometry
from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
from ssto.orbitron.simulator.proof_suite.inputs_builder import simulator_inputs_from_state
from ssto.orbitron.simulator.proof_suite.longitudinal_viz import (
    compute_longitudinal_preview,
    data_source_caption,
    draw_step01_placeholder,
    draw_step01_warpx_xz,
)
from ssto.orbitron.simulator.viz import render_device_cross_section


def _spin(lo: float, hi: float, val: float, *, dec: int = 4, suf: str = "") -> QDoubleSpinBox:
    s = QDoubleSpinBox()
    s.setRange(lo, hi)
    s.setDecimals(dec)
    s.setValue(val)
    if suf:
        s.setSuffix(suf)
    return s


class Step00SpecPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "00",
            "Design SSOT",
            "Freeze bore geometry, H₂ + solid ¹¹B laser fueling, and compile PICMI overrides "
            "(600 kV class, 2 T surrogate, tangential H⁺/B⁺ inject beams). "
            "Benchtop SSOT: Reply 19 Phase 1 + ``SOLID_B11_LASER_FUEL.md``.",
            "picmi_overrides.json on disk; cathode kV and inject_beams match p-¹¹B Orbitron intent.",
            state,
            parent,
        )
        self._state.ensure_initialized()
        cfg = self._state.config
        g = cfg["geometry"]
        inj = cfg["injectants"]

        inputs = QGroupBox("Run inputs (change these, then Run this step below)")
        inputs_lay = QVBoxLayout(inputs)
        dep = QLabel(
            "Re-run step 00 after geometry or fueling changes. "
            "Step 01: set Phase 1 interlocks (VAC → LASER → HV) on the pad before WarpX."
        )
        dep.setWordWrap(True)
        dep.setStyleSheet("color: #e0af68; font-size: 11px; font-weight: bold;")
        inputs_lay.addWidget(dep)
        geom = QGroupBox("Geometry & fueling")
        fl = QFormLayout(geom)
        self.r_anode = _spin(0.01, 0.2, g["r_anode_m"], suf=" m")
        self.r_cathode = _spin(0.002, 0.05, g["r_cathode_m"], suf=" m")
        self.length = _spin(0.2, 5.0, g["length_m"], suf=" m")
        self.v_kv = _spin(50, 1200, g["V_cathode_v"] / 1000, dec=0, suf=" kV")
        self.b_t = _spin(0.1, 15, g["B_axial_tesla"], dec=2, suf=" T")
        inj = normalize_injectants_cfg(inj)
        self.h2 = _spin(0, 500, inj["h2_sccm"], dec=1, suf=" sccm")
        self.laser_hz = _spin(0, 50, inj["laser_ablation_hz"], dec=1, suf=" Hz")
        self.b11_target = _spin(0, 1, inj.get("b11_target_index", 0), dec=0, suf="")
        fl.addRow("Anode radius", self.r_anode)
        fl.addRow("Cathode radius", self.r_cathode)
        fl.addRow("Active length", self.length)
        fl.addRow("Cathode bias", self.v_kv)
        fl.addRow("Axial B", self.b_t)
        fl.addRow("H₂", self.h2)
        fl.addRow("UV laser (1.3)", self.laser_hz)
        fl.addRow("¹¹B target #", self.b11_target)
        inputs_lay.addWidget(geom)
        self.place_inputs_above_run(inputs)

        split = QSplitter()
        self.canvas_layout = MplCanvas(6.5, 3.8)
        self.canvas_cross = MplCanvas(4.5, 3.8)
        split.addWidget(self.canvas_layout)
        split.addWidget(self.canvas_cross)
        self._layout.addWidget(split, stretch=1)

        self.ov_label = QLabel("PICMI overrides (preview)")
        self.ov_label.setStyleSheet("color: #565f89; font-size: 11px;")
        self._layout.addWidget(self.ov_label)

        self.metrics = MetricGrid(3)
        self._layout.addWidget(self.metrics)

        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _sync_config(self) -> None:
        self._state.update_geometry(
            r_anode_m=self.r_anode.value(),
            r_cathode_m=self.r_cathode.value(),
            length_m=self.length.value(),
            V_cathode_v=self.v_kv.value() * 1000,
            B_axial_tesla=self.b_t.value(),
        )
        self._state.update_injectants(
            h2_sccm=self.h2.value(),
            laser_ablation_hz=self.laser_hz.value(),
            b11_target_index=int(self.b11_target.value()),
        )
        self._state.save()

    def _run(self) -> None:
        self._sync_config()
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_00)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        self._sync_config()
        geo = DeviceGeometry(
            r_anode_m=self.r_anode.value(),
            r_cathode_m=self.r_cathode.value(),
            length_m=self.length.value(),
            V_cathode_v=self.v_kv.value() * 1000,
            B_axial_tesla=self.b_t.value(),
        )
        fig1 = self.canvas_layout.figure
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        from ssto.orbitron.simulator.blender_layout import draw_blender_underlay, engine_axial_layout

        layout = engine_axial_layout(geo)
        draw_blender_underlay(ax1, layout, LongitudinalFocus.FULL_DUCT_AIR, symmetric=True)
        ax1.set_title("Engine layout (s–r)", color="#c0caf5")
        fig1.tight_layout()
        self.canvas_layout.draw()

        fig2 = self.canvas_cross.figure
        fig2.clear()
        ax2 = fig2.add_subplot(111)
        render_device_cross_section(ax2, geo, LongitudinalFocus.CORE_TUBE)
        ax2.set_aspect("equal")
        fig2.tight_layout()
        self.canvas_cross.draw()

        txt = self._state.picmi_overrides_text()
        self.ov_label.setText(f"PICMI overrides ({len(txt)} bytes) — run step to refresh")
        data = self._state.try_load_step("00")
        if data:
            self.metrics.set_metrics(
                [
                    ("Status", "Compiled", data.get("generated_utc", "")[:19], "#9ece6a"),
                    ("Overrides", "On disk", "00_spec/picmi_overrides.json", "#7aa2f7"),
                    ("Spec", "YAML", "orbitron_physics_surrogate.yaml", "#a9b1d6"),
                ]
            )
            self.gate.set_gate("Gate: SSOT compiled — proceed to WarpX PIC.", ok=True)
        else:
            self.metrics.set_metrics([("Status", "Pending", "Run this step", "#e0af68")] * 3)
            self.gate.set_gate(self._gate_hint, ok=None)


class Step01PicPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "01",
            "WarpX PIC (Tier 2)",
            "2D PICMI electron ring after pad interlocks (VAC → LASER → HV → ignite). "
            "Proves prescribed E×B electron ρ_e on an x–z slice — not fuel, not compressor, not fusion Q. "
            "Set Phase 1 switches before Run. Equations: validation_steps.md § State evolution → Step 1.",
            "Last density_diag plotfile exists (or SKIP_PIC for dev norms only).",
            state,
            parent,
        )
        self.log.setMaximumHeight(220)

        self.pic_steps = QSpinBox()
        self.pic_steps.setRange(50, 5000)
        self.pic_steps.setValue(int(state.config["pic"]["steps"]))
        self.pic_diag_period = QSpinBox()
        self.pic_diag_period.setRange(10, 500)
        self.pic_diag_period.setValue(int(state.config["pic"].get("diag_period", 40)))
        self.pic_grid = QSpinBox()
        self.pic_grid.setRange(8, 2048)
        self.pic_grid.setSingleStep(8)
        self.pic_grid.setKeyboardTracking(False)
        self.pic_grid.setValue(
            align_pic_grid_cells(int(state.config["pic"].get("grid_cells", 512)))
        )
        self.pic_grid.setToolTip(
            "Cartesian2D PICMI grid: N×N cells (x and z).\n"
            "AMReX requires N divisible by 8 — rounded up when you leave the field "
            "or Run (e.g. 500 → 504). Type the full number, then Tab/Enter.\n"
            "512² default; 128–256² most stable on local AMReX 26.04."
        )
        self.pic_diag_period.setToolTip(
            "How often WarpX writes a density snapshot to disk (plotfile).\n"
            "Example: 500 steps with period 100 → about 6 pictures, not 500.\n"
            "Smaller period = smoother movie, slower run and bigger diags folder."
        )
        self.pic_steps.setToolTip(
            "WarpX time steps — the simulation clock ticks this many times.\n"
            "Pictures on disk = snapshots every «Snapshot every N steps» (not one picture per step).\n"
            "Step 02 only reads the last snapshot."
        )
        self.lbl_snapshot_count = QLabel()
        self.lbl_snapshot_count.setWordWrap(True)
        self.lbl_snapshot_count.setStyleSheet("color: #7aa2f7; font-size: 11px;")
        self.pic_steps.valueChanged.connect(self._update_snapshot_count_hint)
        self.pic_diag_period.valueChanged.connect(self._update_snapshot_count_hint)
        self.pic_grid.valueChanged.connect(self._update_snapshot_count_hint)
        self.pic_grid.editingFinished.connect(self._align_pic_grid_spinbox)
        self._update_snapshot_count_hint()
        self.chk_skip = QCheckBox("Skip WarpX (dev — unity ρ norms in step 2)")
        self.chk_skip.setChecked(bool(state.config.get("gui", {}).get("skip_pic", False)))

        # Inputs above Run — pad levers are not live-linked to WarpX.
        inputs = QGroupBox("Run inputs (change these, then Run this step below)")
        inputs_lay = QVBoxLayout(inputs)
        dep = QLabel(
            "Yes — re-run step 01 after ring levers (τ, p) or PIC steps change. "
            "Starting band that usually clears step 02 (ρ norm 0.2–3): "
            "τ 0.75–0.95 and cathode_pulse 0.70–0.90 (or leave p linked: 0.35 + 0.65×τ). "
            "Compressor (U/J) is not in step 01 WarpX — it enters the plant at step 06. "
            "Step 00: keep B ≤ 2.0 T for step 08 U3."
        )
        dep.setWordWrap(True)
        dep.setStyleSheet("color: #e0af68; font-size: 11px; font-weight: bold;")
        inputs_lay.addWidget(dep)
        self._pad_sync_enabled = False
        self.startup = StartupPanel(
            self._on_pad_changed, include_live_checkbox=False, lever_profile="pic_electron_ring"
        )
        self._pad_sync_enabled = True
        inputs_lay.addWidget(self.startup)
        pic_row = QHBoxLayout()
        pg = QGroupBox("WarpX PICMI")
        pf = QFormLayout(pg)
        pf.addRow("PIC steps (simulation clock)", self.pic_steps)
        pf.addRow("Grid cells (N×N)", self.pic_grid)
        pf.addRow("Snapshot every N steps", self.pic_diag_period)
        pf.addRow(self.chk_skip)
        pic_row.addWidget(pg)
        pic_row.addWidget(self.lbl_snapshot_count, stretch=1)
        inputs_lay.addLayout(pic_row)
        self.btn_play = QPushButton("Play")
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setEnabled(False)
        self.btn_play.setToolTip("Animate through saved WarpX snapshots (~3 per second).")
        self.btn_pause.setToolTip("Stop animation.")
        warp_hint = QLabel(
            "<b>What N steps evolve:</b> species <code>electrons</code> only; prescribed E(t) ramp + uniform B; "
            "movie plots <code>|ρ_e|</code> from <code>rho_electrons</code> plotfiles. "
            "No H₂, no laser, no compressor, no inject beams in this deck. "
            "Fuel enters step 03+ (s–r channel). Re-run step 00 after geometry/kV/B changes.<br>"
            "<b>View:</b> 2D x–z slice only (RZ/3D deferred). See validation_steps.md §1."
        )
        warp_hint.setWordWrap(True)
        warp_hint.setTextFormat(Qt.TextFormat.RichText)
        warp_hint.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        inputs_lay.addWidget(warp_hint)

        self.place_inputs_above_run(inputs)

        right = QWidget()
        rlay = QVBoxLayout(right)

        lon_grp = QGroupBox("Movie — WarpX |ρ_e| snapshots")
        lon_lay = QVBoxLayout(lon_grp)
        self.lon_movie_hint = QLabel(
            "<b>Run this step</b> re-runs WarpX and reloads the movie. "
            "<b>Refresh from artifacts</b> reloads plotfiles already on disk without WarpX. "
            "PIC steps ≠ snapshot count — set «Snapshot every N steps» to 20–40 for a smoother movie."
        )
        self.lon_movie_hint.setTextFormat(Qt.TextFormat.RichText)
        self.lon_movie_hint.setWordWrap(True)
        self.lon_movie_hint.setStyleSheet("color: #e0af68; font-size: 11px;")
        lon_lay.addWidget(self.lon_movie_hint)
        self.lon_source = QLabel("Data: —")
        self.lon_source.setStyleSheet("color: #9ece6a; font-size: 11px;")
        self.lon_source.setWordWrap(True)
        lon_lay.addWidget(self.lon_source)
        self.canvas_xz = MplCanvas(7, 4.2)
        lon_lay.addWidget(self.canvas_xz, stretch=1)
        lon_play = QHBoxLayout()
        lon_play.addWidget(self.btn_play)
        lon_play.addWidget(self.btn_pause)
        lon_play.addStretch()
        lon_lay.addLayout(lon_play)
        lon_opts = QHBoxLayout()
        self.chk_delta = QCheckBox("Δρ vs snapshot 1")
        self.chk_delta.setToolTip(
            "Highlight changes since the first saved frame (cathode ramp / ring build-up)."
        )
        self.chk_delta.toggled.connect(self._draw_longitudinal)
        lon_opts.addWidget(self.chk_delta)
        lon_opts.addStretch()
        lon_lay.addLayout(lon_opts)
        lon_scrub = QHBoxLayout()
        self.btn_rew = QPushButton("⏮")
        self.btn_rew.setFixedWidth(36)
        self.btn_rew.setToolTip("First snapshot")
        self.btn_rew.clicked.connect(lambda: self.lon_time.setValue(0))
        lon_scrub.addWidget(self.btn_rew)
        lon_scrub.addWidget(QLabel("Time"))
        self.lon_time = QSlider()
        self.lon_time.setOrientation(Qt.Orientation.Horizontal)
        self.lon_time.setEnabled(False)
        self.lon_time_label = QLabel("t = —")
        lon_scrub.addWidget(self.lon_time, stretch=1)
        lon_scrub.addWidget(self.lon_time_label)
        self.btn_fwd_end = QPushButton("⏭")
        self.btn_fwd_end.setFixedWidth(36)
        self.btn_fwd_end.setToolTip("Last snapshot")
        self.btn_fwd_end.clicked.connect(self._jump_last_snapshot)
        lon_scrub.addWidget(self.btn_fwd_end)
        lon_lay.addLayout(lon_scrub)
        rlay.addWidget(lon_grp, stretch=1)

        self.metrics = MetricGrid(4)
        rlay.addWidget(self.metrics)
        self._layout.addWidget(right, stretch=1)

        self._lon_xy = None
        self._live_timer = QTimer(self)
        self._live_timer.setInterval(350)
        self._live_timer.timeout.connect(self._on_live_tick)

        self.btn_play.clicked.connect(self._start_playback)
        self.btn_pause.clicked.connect(self._stop_playback)
        self.lon_time.valueChanged.connect(self._draw_longitudinal)

        self._load_pad_from_config()
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _align_pic_grid_spinbox(self) -> bool:
        """Snap grid to AMReX blocking_factor 8. Returns True if value changed."""
        raw = int(self.pic_grid.value())
        aligned = align_pic_grid_cells(raw)
        if aligned != raw:
            self.pic_grid.blockSignals(True)
            self.pic_grid.setValue(aligned)
            self.pic_grid.blockSignals(False)
            self._update_snapshot_count_hint()
            return True
        self._update_snapshot_count_hint()
        return False

    def _update_snapshot_count_hint(self) -> None:
        steps = int(self.pic_steps.value())
        period = max(1, int(self.pic_diag_period.value()))
        n_snaps = max(1, steps // period + 1)
        n = int(self.pic_grid.value())
        self.lbl_snapshot_count.setText(
            f"Grid {n}×{n} (÷8)  |  expect ~{n_snaps} snapshots for {steps} PIC steps "
            f"(plotfile every {period} steps)."
        )

    def _pad_from_config(self) -> PadStartupState:
        p = self._state.config["pad"]
        return PadStartupState(
            pad_apu_online=bool(p.get("pad_apu_online", False)),
            starter_engage=bool(p.get("starter_engage", False)),
            bleed_air_open=bool(p.get("bleed_air_open", False)),
            vacuum_interlock_ok=bool(p.get("vacuum_interlock_ok", False)),
            laser_armed=bool(p.get("laser_armed", False)),
            hv_enabled=bool(p.get("hv_enabled", False)),
            startup_trigger=bool(p.get("startup_trigger", False)),
            throttle=float(p["throttle"]),
            compressor=float(p["compressor"]),
            cathode_pulse=float(p["cathode_pulse"]),
            laminar_relaminarization=bool(p.get("laminar_relaminarization", True)),
        )

    def _load_pad_from_config(self) -> None:
        self.startup.apply_pad_state(self._pad_from_config())

    def _on_pad_changed(self) -> None:
        if not getattr(self, "_pad_sync_enabled", False):
            return
        self._sync_config()
        self._refresh_step01_status()
        # Pad levers do not re-run WarpX; cached snapshots stay until Run this step.

    def _sync_config(self) -> None:
        self._align_pic_grid_spinbox()
        pad = self.startup.pad_state()
        self._state.update_pad(
            throttle=pad.throttle,
            compressor=pad.compressor,
            cathode_pulse=pad.cathode_pulse,
            laminar=bool(self._state.config["pad"].get("laminar_relaminarization", True)),
            vacuum_interlock_ok=pad.vacuum_interlock_ok,
            laser_armed=pad.laser_armed,
            hv_enabled=pad.hv_enabled,
        )
        p = self._state.config["pad"]
        p["pad_apu_online"] = pad.pad_apu_online
        p["starter_engage"] = pad.starter_engage
        p["bleed_air_open"] = pad.bleed_air_open
        p["startup_trigger"] = pad.startup_trigger
        self._state.update_pic_settings(
            steps=self.pic_steps.value(),
            diag_period=self.pic_diag_period.value(),
            grid_cells=self.pic_grid.value(),
            skip_pic=self.chk_skip.isChecked(),
        )
        self._state.save()
        if self.chk_skip.isChecked():
            os.environ["SKIP_PIC"] = "1"
        else:
            os.environ.pop("SKIP_PIC", None)

    def _run(self) -> None:
        self._sync_config()
        self.log.clear()
        self.log.append_line("Starting WarpX…")
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = WarpXWorker(skip_pic=self.chk_skip.isChecked(), n_steps=self.pic_steps.value())
        w.log_line.connect(self.log.append_line)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def _pic_diags_dir(self) -> Path:
        from tools.orbitron_proof_chain.chain_lib import load_config

        return Path(load_config()["chain_root"]) / "01_pic" / "diags"

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
            compressor=pad.compressor,
            cathode_pulse=pad.cathode_pulse,
            live_simulation=pad.live_simulation,
            laminar_relaminarization=bool(self._state.config["pad"].get("laminar_relaminarization", True)),
        )
        return simulator_inputs_from_state(self._state, pad)

    def _rebuild_longitudinal(self) -> None:
        diags = self._pic_diags_dir()
        empty_msg = (
            "No WarpX plotfiles yet.\n\nRun this step (WarpX PIC) — "
            "heuristic / fusion-channel previews are on step 03 only."
        )
        if not list_pic_plotfiles(diags):
            self._lon_xy = None
            self.lon_time.setEnabled(False)
            draw_step01_placeholder(self.canvas_xz.figure, empty_msg)
            self.lon_source.setText("Data: none (not WarpX)")
            self.canvas_xz.draw()
            return
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
            self.lon_source.setText(data_source_caption(self._lon_xy))
            n = len(self._lon_xy.time_s)
            self.lon_time.setEnabled(n > 1)
            self.lon_time.setMaximum(max(0, n - 1))
            if self.lon_time.value() > max(0, n - 1):
                self.lon_time.setValue(0)
            self._draw_longitudinal()
        except Exception as exc:
            draw_step01_placeholder(self.canvas_xz.figure, str(exc))
            self.lon_source.setText(f"Data: error — {exc}")
            self.canvas_xz.draw()
            self._lon_xy = None
            self.lon_time.setEnabled(False)

    def _jump_last_snapshot(self) -> None:
        if self._lon_xy is None:
            return
        self.lon_time.setValue(max(0, len(self._lon_xy.time_s) - 1))

    def _draw_longitudinal(self) -> None:
        if self._lon_xy is None:
            return
        inputs = self._gather_inputs()
        idx = self.lon_time.value()
        draw_step01_warpx_xz(
            self.canvas_xz.figure,
            self._lon_xy,
            idx,
            inputs=inputs,
            delta_vs_first=self.chk_delta.isChecked(),
        )
        t = self._lon_xy.time_s[idx]
        n = len(self._lon_xy.time_s)
        self.lon_time_label.setText(
            f"Snapshot {idx + 1}/{n}  (t = {t:.3e} s) — not step {idx + 1} of {self.pic_steps.value()} PIC steps"
        )
        self.canvas_xz.draw()

    def stop_snapshot_playback(self) -> None:
        """Called when leaving step 01 so playback does not run in the background."""
        self._stop_playback()

    def _start_playback(self) -> None:
        if self._lon_xy is None or len(self._lon_xy.time_s) <= 1:
            return
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self._live_timer.start()

    def _stop_playback(self) -> None:
        self._live_timer.stop()
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(False)

    def _on_live_tick(self) -> None:
        if self._lon_xy is None or len(self._lon_xy.time_s) <= 1:
            self._rebuild_longitudinal()
            return
        n = len(self._lon_xy.time_s)
        nxt = (self.lon_time.value() + 1) % n
        self.lon_time.blockSignals(True)
        self.lon_time.setValue(nxt)
        self.lon_time.blockSignals(False)
        self._draw_longitudinal()

    def _refresh_step01_status(self) -> None:
        data = self._state.try_load_step("01")
        diags = self._pic_diags_dir()
        n_pf = len(list_pic_plotfiles(diags)) if diags.is_dir() else 0
        if data:
            n_pf = max(n_pf, len(data.get("plotfiles", [])))
        n_frames = len(self._lon_xy.time_s) if self._lon_xy else 0
        pad_now = self.startup.pad_state()

        if data and data.get("ok") is False:
            rc = data.get("returncode", "?")
            self.metrics.set_metrics(
                [
                    ("WarpX", f"exit {rc}", "see log", "#f7768e"),
                    ("Plotfiles", str(n_pf), "", "#e0af68"),
                    ("Snapshots", str(n_frames), "loaded", "#565f89"),
                    ("Status", "Failed", "", "#f7768e"),
                ]
            )
            self.gate.set_gate("Gate: WarpX did not finish — fix env and Run this step.", ok=False)
        elif data and data.get("skipped"):
            self.metrics.set_metrics(
                [
                    ("WarpX", "SKIP_PIC", "dev", "#e0af68"),
                    ("Plotfiles", "0", "", "#565f89"),
                    ("Snapshots", "0", "", "#565f89"),
                    ("Status", "Skipped", "", "#e0af68"),
                ]
            )
            self.gate.set_gate(
                "Gate: skipped — step 02 (scale factors) will use 1.0 placeholders, not WarpX.",
                ok=None,
            )
        elif data:
            run_tau = data.get("ring_density_scale", data.get("throttle"))
            lever_note = "pad"
            if run_tau is not None and (
                abs(pad_now.throttle - float(run_tau)) > 0.02
                or abs(pad_now.cathode_pulse - float(data.get("cathode_pulse", run_tau))) > 0.02
            ):
                lever_note = "levers changed — re-run"
            run_grid = data.get("grid_cells")
            grid_note = f"{run_grid}²" if run_grid else "—"
            if run_grid is not None and int(run_grid) != int(self.pic_grid.value()):
                grid_note = f"{run_grid}² — re-run"
            self.metrics.set_metrics(
                [
                    ("Plotfiles", str(n_pf), "on disk", "#9ece6a" if n_pf else "#e0af68"),
                    ("Snapshots", str(n_frames), "scrub with Time", "#7aa2f7"),
                    ("Grid", grid_note, "last run", "#7aa2f7"),
                    ("Ring τ", f"{data.get('ring_density_scale', data.get('throttle', 0)):.2f}", lever_note, "#7aa2f7"),
                ]
            )
            if n_pf and self._lon_xy is not None:
                self.gate.set_gate("Gate: WarpX snapshots loaded — run step 02 for scale factors.", ok=True)
            elif n_pf:
                self.gate.set_gate("Gate: plotfiles on disk but snapshot preview failed.", ok=None)
            else:
                self.gate.set_gate("Gate: re-run WarpX for density snapshots.", ok=False)
        elif self._lon_xy is not None:
            self.metrics.set_metrics(
                [
                    ("Plotfiles", str(n_pf), "on disk", "#9ece6a" if n_pf else "#e0af68"),
                    ("Snapshots", str(n_frames), "scrub with Time", "#7aa2f7"),
                    ("Ring τ", f"{pad_now.throttle:.2f}", "pad", "#7aa2f7"),
                    ("Pulse", f"{pad_now.cathode_pulse:.2f}", "cathode", "#7aa2f7"),
                ]
            )
            self.gate.set_gate(self._gate_hint, ok=None)
        else:
            self.metrics.set_metrics(
                [
                    ("Plotfiles", "0", "run WarpX", "#565f89"),
                    ("Snapshots", "0", "", "#565f89"),
                    ("Throttle", f"{pad_now.throttle:.2f}", "pad", "#565f89"),
                    ("Pulse", f"{pad_now.cathode_pulse:.2f}", "cathode", "#565f89"),
                ]
            )
            self.gate.set_gate(self._gate_hint, ok=None)

    def on_step_finished(self, result: dict | None, error: str | None) -> None:
        super().on_step_finished(result, error)
        if error:
            return
        n = len(self._lon_xy.time_s) if self._lon_xy is not None else 0
        if n:
            self.lon_time.setValue(0)
            self.log.append_line(
                f"Movie updated: {n} snapshots on disk (shared color scale). "
                "Use Play or drag Time; try «Δρ vs snapshot 1» if frames look similar."
            )

    def refresh_from_artifacts(self) -> None:
        self._rebuild_longitudinal()
        self._refresh_step01_status()


class Step02ReducePanel(ProofStepPanel):
    go_to_step = Signal(str)

    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "02",
            "PIC coupling norms",
            "Reduce step 01’s last WarpX plotfile to the electron-ring scale factor ρ_e_norm — "
            "Tier-2 confinement input for the fusion channel and plant. "
            "Fuel / inject coupling is step 03 (s–r channel), not a second bar here.",
            "ρ_e_norm in 0.2–3.0 (plant clamps); document if SKIP_PIC unity placeholder used.",
            state,
            parent,
        )
        why = QWidget()
        why_lay = QVBoxLayout(why)
        lbl_why = QLabel(
            "<b>Not a movie</b> — one bar: electron-ring strength from WarpX (last snapshot).<br>"
            "<b>Why this step exists</b> — Step 01’s transverse slice shows |ρ_e| from the electron ring only; "
            "we turn that into ρ_e_norm for confinement in steps 03–06. "
            "Fuel (H₂, laser ¹¹B) and compressor (Brayton mdot) are <b>not</b> in step 01 WarpX — "
            "see validation_steps.md § State evolution."
        )
        lbl_why.setWordWrap(True)
        lbl_why.setTextFormat(Qt.TextFormat.RichText)
        lbl_why.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        why_lay.addWidget(lbl_why)
        self.place_inputs_above_run(why)

        nav = QHBoxLayout()
        self.lbl_levers = QLabel()
        self.lbl_levers.setWordWrap(True)
        self.lbl_levers.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        nav.addWidget(self.lbl_levers, stretch=1)
        btn01 = QPushButton("Change levers → step 01")
        btn01.clicked.connect(lambda: self.go_to_step.emit("01"))
        btn00 = QPushButton("Geometry → step 00")
        btn00.clicked.connect(lambda: self.go_to_step.emit("00"))
        nav.addWidget(btn00)
        nav.addWidget(btn01)
        self._layout.addLayout(nav)

        self.canvas_bars = MplCanvas(7, 4)
        self._layout.addWidget(self.canvas_bars, stretch=1)
        self.narrative = QLabel("Run this step after step 01.")
        self.narrative.setWordWrap(True)
        self.narrative.setTextFormat(Qt.TextFormat.RichText)
        self.narrative.setStyleSheet(
            "color: #c0caf5; font-size: 12px; padding: 8px; background: #1f2335; border-radius: 4px;"
        )
        self._layout.addWidget(self.narrative)
        self.metrics = MetricGrid(3)
        self._layout.addWidget(self.metrics)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _run(self) -> None:
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_02)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def _refresh_lever_summary(self) -> None:
        cfg = self._state.config
        p = cfg["pad"]
        g = cfg["geometry"]
        pic = cfg["pic"]
        s01 = self._state.try_load_step("01") or {}
        lines = [
            f"Pad (step 01 levers): τ={p['throttle']:.2f}  p={p['cathode_pulse']:.2f}  "
            f"|  PIC steps={pic['steps']}",
            f"Geometry: r_anode={g['r_anode_m']:.4f} m  r_cathode={g['r_cathode_m']:.4f} m  "
            f"V={g['V_cathode_v']/1000:.0f} kV  B={g['B_axial_tesla']:.2f} T",
        ]
        if s01.get("skipped"):
            lines.append("Step 01: SKIP_PIC — norms below are placeholders, not WarpX.")
        elif s01.get("ok") is False:
            lines.append(f"Step 01: WarpX failed (exit {s01.get('returncode', '?')}) — fix on step 01.")
        elif s01:
            lines.append(
                f"Last WarpX run: {s01.get('n_steps', pic['steps'])} steps, "
                f"{len(s01.get('plotfiles', []))} plotfiles"
            )
        self.lbl_levers.setText("\n".join(lines))

    def refresh_from_artifacts(self) -> None:
        self._refresh_lever_summary()
        data = self._state.try_load_step("02")
        fig = self.canvas_bars.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if data and data.get("skipped"):
            ax.text(
                0.5,
                0.5,
                "PIC skipped (SKIP_PIC)\nElectron ring × = 1.0 placeholder — not from WarpX.",
                ha="center",
                va="center",
                color="#e0af68",
                fontsize=12,
            )
            self.narrative.setText(
                "Step 01 was skipped, so there is no WarpX frame to read. "
                "The chain uses ρ_e_norm = 1.0. Turn off SKIP_PIC on step 01 for a measured ring scale factor. "
                "Fuel coupling is computed on step 03."
            )
            self.metrics.set_metrics(
                [
                    ("Electron ring ×", "1.00", "placeholder", "#e0af68"),
                    ("Next", "Step 03", "fuel × (s–r)", "#7aa2f7"),
                    ("Pad τ", f"{self._state.config['pad']['throttle']:.2f}", "step 01", "#565f89"),
                ]
            )
            self.gate.set_gate(
                "PIC skipped — electron ring scale is a placeholder, not measured from step 01.",
                ok=None,
            )
        elif data:
            re = float(data.get("rho_e_norm", 1))
            label = "Electron ring ×\n(last WarpX snapshot)"
            color = "#7aa2f7" if 0.2 <= re <= 3.0 else "#f7768e"
            ax.bar([label], [re], color=color, width=0.45)
            ax.axhspan(0.2, 3.0, color="#9ece6a", alpha=0.12, label="OK band for later steps")
            ax.axhline(1.0, color="#e0af68", ls="--", lw=1.0, label="Design point (1.0)")
            ax.set_ylim(0, max(3.5, re * 1.15))
            ax.set_ylabel("ρ_e scale → confinement (steps 03–06)")
            ax.set_title(
                "WarpX electron ring strength (single multiplier)\n"
                "Fuel / inject coupling is step 03 — not pad throttle replay",
                color="#c0caf5",
                fontsize=10,
            )
            ax.legend(fontsize=8, loc="upper right")
            ax.grid(True, axis="y", alpha=0.25)
            for bar in ax.patches:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    f"{re:.2f}",
                    ha="center",
                    color="#c0caf5",
                    fontsize=11,
                )

            ok_e = 0.2 <= re <= 3.0
            self.narrative.setText(
                "<b>How to read this</b><br>"
                f"• <b>Electron ring × ({re:.2f})</b> — From the last step 01 |ρ_e| snapshot in the cathode–anode annulus. "
                f"{'In range for the chain.' if ok_e else 'Adjust step 01 levers or geometry.'}<br>"
                "• <b>Not shown here</b> — Ion/fuel coupling is not measurable on the flat x–z slice; "
                "step 03 reports <b>fuel ×</b> from the s–r fusion channel (H₂ + laser + inject model).<br>"
                "• <b>Pad inputs</b> — Ring density τ and cathode pulse p on step 01 set the WarpX run; "
                "compressor and fuel are deferred to later steps (see validation_steps.md)."
            )

            self.metrics.set_metrics(
                [
                    ("Electron ring ×", f"{re:.2f}", "last WarpX snapshot", "#9ece6a" if ok_e else "#f7768e"),
                    ("Next", "Step 03", "fuel × from s–r", "#7aa2f7"),
                    ("Gate", "ρ_e band", "0.2–3.0", "#9ece6a" if ok_e else "#f7768e"),
                ]
            )
            self.gate.set_gate(
                "Green light: electron ring scale OK — continue to step 03 for fuel coupling."
                if ok_e
                else "Adjust step 01 (electron ring) or geometry — ρ_e_norm out of allowed band.",
                ok=ok_e,
            )
        else:
            ax.text(0.5, 0.5, "Run this step after step 01 finishes.", ha="center", color="#565f89")
            self.narrative.setText("Run this step after step 01.")
            self.gate.set_gate(self._gate_hint, ok=None)
        fig.tight_layout()
        self.canvas_bars.draw()
