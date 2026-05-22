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
            "Freeze geometry, injectants, and compile PICMI overrides from "
            "orbitron_physics_surrogate.yaml. This is the single source of truth for all later steps.",
            "picmi_overrides.json exists and matches your bore / 600 kV / 2 T intent.",
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
            "Re-run step 00 after changing geometry or fueling. "
            "Step 01 WarpX uses the PICMI overrides compiled here."
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
            "WarpX PIC",
            "Run laminar_flow_2d_arcjet at the pad run point. Produces ρ_e and inject-beam "
            "plotfiles — Tier 2 coupling, not fusion Q.",
            "Last density_diag plotfile exists (or SKIP_PIC acknowledged).",
            state,
            parent,
        )
        self.log.setMaximumHeight(220)

        self.pic_steps = QSpinBox()
        self.pic_steps.setRange(50, 5000)
        self.pic_steps.setValue(int(state.config["pic"]["steps"]))
        self.pic_diag_period = QSpinBox()
        self.pic_diag_period.setRange(10, 500)
        self.pic_diag_period.setValue(int(state.config["pic"].get("diag_period", 100)))
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
        self._update_snapshot_count_hint()
        self.chk_skip = QCheckBox("Skip WarpX (dev — unity ρ norms in step 2)")
        self.chk_skip.setChecked(bool(state.config.get("gui", {}).get("skip_pic", False)))

        # Inputs above Run — pad levers are not live-linked to WarpX.
        inputs = QGroupBox("Run inputs (change these, then Run this step below)")
        inputs_lay = QVBoxLayout(inputs)
        dep = QLabel(
            "Yes — re-run step 01 after pad levers or PIC steps change. "
            "Starting band that usually clears step 02 (ρ norm 0.2–3): "
            "throttle 0.75–0.95, compressor 0.65–0.90, cathode_pulse 0.70–0.90 "
            "(or leave pulse linked: 0.35 + 0.65×throttle). "
            "Step 00: keep B ≤ 2.0 T for step 08 U3."
        )
        dep.setWordWrap(True)
        dep.setStyleSheet("color: #e0af68; font-size: 11px; font-weight: bold;")
        inputs_lay.addWidget(dep)
        self._pad_sync_enabled = False
        self.startup = StartupPanel(self._on_pad_changed, include_live_checkbox=False)
        self._pad_sync_enabled = True
        inputs_lay.addWidget(self.startup)
        pic_row = QHBoxLayout()
        pg = QGroupBox("WarpX PICMI")
        pf = QFormLayout(pg)
        pf.addRow("PIC steps (simulation clock)", self.pic_steps)
        pf.addRow("Snapshot every N steps", self.pic_diag_period)
        pf.addRow(self.chk_skip)
        pic_row.addWidget(pg)
        pic_row.addWidget(self.lbl_snapshot_count, stretch=1)
        self.chk_live = QCheckBox("Play snapshots")
        self.chk_live.setToolTip(
            "Steps through saved plotfiles on disk after a WarpX run (about two pictures per second). "
            "Does not re-run WarpX — use the Time slider under the top picture."
        )
        pic_row.addWidget(self.chk_live, stretch=1)
        inputs_lay.addLayout(pic_row)
        warp_hint = QLabel(
            "<b>What N steps evolve:</b> electron ring + arc seed + inject beams; cathode V ramp; "
            "|ρ_e| plotfiles every 100 steps. "
            "<b>Not</b> laminar fuel proof (step 03). Geometry / kV / B: re-run step 00 first.<br>"
            "<b>View:</b> 2D x–z slice only. A cylindrical r–z axial-uniformity panel is deferred until "
            "3D / RZ WarpX (2D slice + projection collapses here; code kept in "
            "<code>longitudinal/warpx_frames.py</code> for handoff)."
        )
        warp_hint.setWordWrap(True)
        warp_hint.setTextFormat(Qt.TextFormat.RichText)
        warp_hint.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        inputs_lay.addWidget(warp_hint)

        self.place_inputs_above_run(inputs)

        right = QWidget()
        rlay = QVBoxLayout(right)

        lon_grp = QGroupBox("Movie panel — saved WarpX snapshots (drag Time slider)")
        lon_lay = QVBoxLayout(lon_grp)
        self.lon_movie_hint = QLabel(
            "500 PIC steps does not mean 500 pictures. WarpX saves |ρ_e| only every N steps "
            "(see «Snapshot every N steps»). Drag Time or use Play snapshots."
        )
        self.lon_movie_hint.setWordWrap(True)
        self.lon_movie_hint.setStyleSheet("color: #e0af68; font-size: 11px;")
        lon_lay.addWidget(self.lon_movie_hint)
        self.lon_source = QLabel("Data: —")
        self.lon_source.setStyleSheet("color: #9ece6a; font-size: 11px;")
        self.lon_source.setWordWrap(True)
        lon_lay.addWidget(self.lon_source)
        self.canvas_xz = MplCanvas(7, 4.2)
        lon_lay.addWidget(self.canvas_xz, stretch=1)
        lon_scrub = QHBoxLayout()
        lon_scrub.addWidget(QLabel("Time"))
        self.lon_time = QSlider()
        self.lon_time.setOrientation(Qt.Orientation.Horizontal)
        self.lon_time.setEnabled(False)
        self.lon_time_label = QLabel("t = —")
        lon_scrub.addWidget(self.lon_time, stretch=1)
        lon_scrub.addWidget(self.lon_time_label)
        lon_lay.addLayout(lon_scrub)
        rlay.addWidget(lon_grp, stretch=1)

        self.metrics = MetricGrid(4)
        rlay.addWidget(self.metrics)
        self._layout.addWidget(right, stretch=1)

        self._lon_xy = None
        self._live_timer = QTimer(self)
        self._live_timer.setInterval(500)
        self._live_timer.timeout.connect(self._on_live_tick)

        self.chk_live.toggled.connect(self._update_live_timer)
        self.lon_time.valueChanged.connect(self._draw_longitudinal)

        self._load_pad_from_config()
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _update_snapshot_count_hint(self) -> None:
        steps = int(self.pic_steps.value())
        period = max(1, int(self.pic_diag_period.value()))
        n_snaps = max(1, steps // period + 1)
        self.lbl_snapshot_count.setText(
            f"Expect ~{n_snaps} saved snapshots for {steps} PIC steps "
            f"(one plotfile every {period} steps)."
        )

    def _pad_from_config(self) -> PadStartupState:
        p = self._state.config["pad"]
        return PadStartupState(
            pad_apu_online=True,
            starter_engage=True,
            bleed_air_open=True,
            startup_trigger=True,
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
        pad = self.startup.pad_state()
        pad = PadStartupState(
            pad_apu_online=pad.pad_apu_online,
            starter_engage=pad.starter_engage,
            bleed_air_open=pad.bleed_air_open,
            startup_trigger=pad.startup_trigger,
            throttle=pad.throttle,
            compressor=pad.compressor,
            cathode_pulse=pad.cathode_pulse,
            live_simulation=self.chk_live.isChecked(),
            laminar_relaminarization=bool(self._state.config["pad"].get("laminar_relaminarization", True)),
        )
        self._state.update_pad(
            throttle=pad.throttle,
            compressor=pad.compressor,
            cathode_pulse=pad.cathode_pulse,
            laminar=pad.laminar_relaminarization,
        )
        self._state.update_pic_settings(
            steps=self.pic_steps.value(),
            diag_period=self.pic_diag_period.value(),
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
            startup_trigger=pad.startup_trigger,
            throttle=pad.throttle,
            compressor=pad.compressor,
            cathode_pulse=pad.cathode_pulse,
            live_simulation=self.chk_live.isChecked(),
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

    def _draw_longitudinal(self) -> None:
        if self._lon_xy is None:
            return
        inputs = self._gather_inputs()
        idx = self.lon_time.value()
        draw_step01_warpx_xz(self.canvas_xz.figure, self._lon_xy, idx, inputs=inputs)
        t = self._lon_xy.time_s[idx]
        n = len(self._lon_xy.time_s)
        self.lon_time_label.setText(
            f"Snapshot {idx + 1}/{n}  (t = {t:.3e} s) — not step {idx + 1} of {self.pic_steps.value()} PIC steps"
        )
        self.canvas_xz.draw()

    def stop_snapshot_playback(self) -> None:
        """Called when leaving step 01 so playback does not run in the background."""
        self._live_timer.stop()
        if self.chk_live.isChecked():
            self.chk_live.blockSignals(True)
            self.chk_live.setChecked(False)
            self.chk_live.blockSignals(False)

    def _update_live_timer(self) -> None:
        if self.chk_live.isChecked() and self._lon_xy is not None and len(self._lon_xy.time_s) > 1:
            self._live_timer.start()
        else:
            self._live_timer.stop()

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
            run_th = data.get("throttle")
            lever_note = "pad"
            if run_th is not None and (
                abs(pad_now.throttle - float(run_th)) > 0.02
                or abs(pad_now.compressor - float(data.get("compressor", run_th))) > 0.02
                or abs(pad_now.cathode_pulse - float(data.get("cathode_pulse", run_th))) > 0.02
            ):
                lever_note = "levers changed — re-run"
            self.metrics.set_metrics(
                [
                    ("Plotfiles", str(n_pf), "on disk", "#9ece6a" if n_pf else "#e0af68"),
                    ("Snapshots", str(n_frames), "scrub with Time", "#7aa2f7"),
                    ("Throttle", f"{data.get('throttle', 0):.2f}", lever_note, "#7aa2f7"),
                    ("Pulse", f"{data.get('cathode_pulse', 0):.2f}", "cathode", "#7aa2f7"),
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
                    ("Throttle", f"{pad_now.throttle:.2f}", "pad", "#7aa2f7"),
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

    def refresh_from_artifacts(self) -> None:
        self._rebuild_longitudinal()
        self._refresh_step01_status()
        self._update_live_timer()


class Step02ReducePanel(ProofStepPanel):
    go_to_step = Signal(str)

    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "02",
            "Two scale factors for later steps",
            "No movie here — only two numbers from step 01’s <b>last</b> WarpX snapshot: "
            "electron ring strength and ion-inject strength (often from throttle on this flat slice).",
            "Both scale factors should be between 0.2 and 3.0.",
            state,
            parent,
        )
        why = QWidget()
        why_lay = QVBoxLayout(why)
        lbl_why = QLabel(
            "<b>Not a movie</b> — the chart is two bar heights (multipliers), not animation frames.<br>"
            "<b>Why this step exists</b> — Step 01’s movie ends here. We read the <b>last</b> snapshot and ask: "
            "<i>how much should later steps scale the electron ring and ion inject?</i> "
            "Fuel along the full tube is <b>step 03–04</b>, not here."
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
            f"Pad: throttle={p['throttle']:.2f}  compressor={p['compressor']:.2f}  "
            f"cathode_pulse={p['cathode_pulse']:.2f}  |  PIC steps={pic['steps']}",
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

    def _beam_source_plain(self, src: str) -> str:
        return {
            "inject_plane_2d": "Measured ion deposit at the +x inject plane (good for this flat slice).",
            "viewport_screen": "Measured ion deposit at the test-stand viewport (−x side).",
            "domain_mean": "Average ion deposit over the whole slice.",
            "pad_throttle_fallback": (
                "No ion deposit on the snapshot — ion × follows your <b>throttle</b> lever "
                "(0.2–1.0 maps to ×0.2–3.0). Normal on a flat slice; fuel along the tube is step 03–04."
            ),
        }.get(src, src)

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
                "PIC skipped (SKIP_PIC)\nBoth scale factors fixed at 1.0 — not from WarpX.",
                ha="center",
                va="center",
                color="#e0af68",
                fontsize=12,
            )
            self.narrative.setText(
                "Step 01 was skipped, so there is no WarpX frame to read. "
                "The chain uses neutral multipliers (1.0). Turn off SKIP_PIC on step 01 for a real ring scale factor."
            )
            self.metrics.set_metrics(
                [
                    ("Electron ring ×", "1.00", "placeholder", "#e0af68"),
                    ("Ion inject ×", "1.00", "placeholder", "#e0af68"),
                    ("Next", "Step 03", "still runs", "#7aa2f7"),
                ]
            )
            self.gate.set_gate(
                "PIC skipped — scale factors are placeholders, not measured from step 01.",
                ok=None,
            )
        elif data:
            re = float(data.get("rho_e_norm", 1))
            rb = float(data.get("rho_beam_norm", 1))
            vals = [re, rb]
            labels = ["Electron ring ×\n(from last snapshot)", "Ion inject ×\n(H⁺/B⁺ proxy)"]
            colors = ["#7aa2f7" if 0.2 <= re <= 3.0 else "#f7768e", "#7aa2f7" if 0.2 <= rb <= 3.0 else "#e0af68"]
            ax.bar(labels, vals, color=colors, width=0.55)
            ax.axhspan(0.2, 3.0, color="#9ece6a", alpha=0.12, label="OK band for later steps")
            ax.axhline(1.0, color="#e0af68", ls="--", lw=1.0, label="Design point (1.0)")
            ax.set_ylim(0, max(3.5, max(vals) * 1.15))
            ax.set_ylabel("Strength multiplier handed to steps 03–06")
            ax.set_title(
                "Two scale factors (not a movie — two bar heights)\n"
                "1.0 = nominal design; green band = allowed range",
                color="#c0caf5",
                fontsize=10,
            )
            ax.legend(fontsize=8, loc="upper right")
            ax.grid(True, axis="y", alpha=0.25)
            for bar, v in zip(ax.patches, vals):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    f"{v:.2f}",
                    ha="center",
                    color="#c0caf5",
                    fontsize=11,
                )

            ok_e = 0.2 <= re <= 3.0
            ok_b = 0.2 <= rb <= 3.0
            gate_ok = ok_e and ok_b
            src = str(data.get("beam_metric_source", ""))
            self.narrative.setText(
                "<b>How to read this</b><br>"
                f"• <b>Electron cloud ({re:.2f})</b> — Did step 01 show a real ring? "
                f"{'Yes — in range.' if ok_e else 'Weak or strong — adjust step 01 levers or geometry.'}<br>"
                f"• <b>Ion inject × ({rb:.2f})</b> — {self._beam_source_plain(src)}<br>"
                "• <b>Why you should care</b> — Steps 03–06 multiply power, fuel, and beam estimates by "
                "these numbers. Wrong ring → rest of chain is scaled wrong. Ion × matters less on this slice.<br>"
                "• <b>Ignore</b> old “beam screen” stats — they were a −x viewport check and are usually 0 here."
            )

            self.metrics.set_metrics(
                [
                    ("Electron ring ×", f"{re:.2f}", "last WarpX snapshot", "#9ece6a" if ok_e else "#f7768e"),
                    ("Ion inject ×", f"{rb:.2f}", src.replace("_", " ")[:28], "#9ece6a" if ok_b else "#e0af68"),
                    (
                        "Next",
                        "Step 03",
                        "fuel along tube (s–r)",
                        "#7aa2f7",
                    ),
                ]
            )
            self.gate.set_gate(
                "Green light: electron ring scale OK — continue to step 03."
                if gate_ok and ok_e
                else (
                    "Adjust step 01 (electron ring) or geometry — scale factors out of allowed band."
                    if not gate_ok
                    else "Electron ring weak/strong — check step 01 movie before trusting step 03."
                ),
                ok=gate_ok,
            )
        else:
            ax.text(0.5, 0.5, "Run this step after step 01 finishes.", ha="center", color="#565f89")
            self.narrative.setText("Run this step after step 01.")
            self.gate.set_gate(self._gate_hint, ok=None)
        fig.tight_layout()
        self.canvas_bars.draw()
