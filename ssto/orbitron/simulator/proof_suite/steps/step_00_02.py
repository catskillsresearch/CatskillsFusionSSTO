"""Proof suite steps 00–02: SSOT, PIC, reduce."""
from __future__ import annotations

import json
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
    load_pic_slice_2d_with_error,
    run_step_00,
    run_step_02,
)
from ssto.orbitron.simulator.proof_suite.steps.base import ProofStepPanel
from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.widgets import MetricGrid, MplCanvas
from ssto.orbitron.simulator.proof_suite.workers import StepWorker
from ssto.orbitron.simulator.types import DeviceGeometry
from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
from ssto.orbitron.simulator.proof_suite.inputs_builder import simulator_inputs_from_state
from ssto.orbitron.simulator.proof_suite.longitudinal_viz import (
    STEP01_MAP_EQUATION_HTML,
    compute_longitudinal_preview,
    data_source_caption,
    draw_step01_placeholder,
    draw_step01_warpx_rz_remap,
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

        form = QGroupBox("Geometry & fueling")
        fl = QFormLayout(form)
        self.r_anode = _spin(0.01, 0.2, g["r_anode_m"], suf=" m")
        self.r_cathode = _spin(0.002, 0.05, g["r_cathode_m"], suf=" m")
        self.length = _spin(0.2, 5.0, g["length_m"], suf=" m")
        self.v_kv = _spin(50, 1200, g["V_cathode_v"] / 1000, dec=0, suf=" kV")
        self.b_t = _spin(0.1, 15, g["B_axial_tesla"], dec=2, suf=" T")
        self.h2 = _spin(0, 500, inj["h2_sccm"], dec=1, suf=" sccm")
        self.b2h6 = _spin(0, 100, inj["b2h6_sccm"], dec=1, suf=" sccm")
        fl.addRow("Anode radius", self.r_anode)
        fl.addRow("Cathode radius", self.r_cathode)
        fl.addRow("Active length", self.length)
        fl.addRow("Cathode bias", self.v_kv)
        fl.addRow("Axial B", self.b_t)
        fl.addRow("H₂", self.h2)
        fl.addRow("B₂H₆", self.b2h6)
        self._layout.addWidget(form)

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
        self._state.update_injectants(h2_sccm=self.h2.value(), b2h6_sccm=self.b2h6.value())
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
        self.pic_steps.setToolTip(
            "WarpX time steps for laminar_flow_2d_arcjet.py.\n"
            "Each step advances macroparticles + deposited ρ on the 2D grid; cathode E ramps over "
            "~35% of this count.\n"
            "Diagnostics every 100 steps → timelapse frames. Step 02 only uses the last plotfile.\n"
            "50–100: quick sanity check (few frames, ramp may not finish).\n"
            "500: default coupling snapshot; more steps = more timelapse, not new physics in step 02."
        )
        self.chk_skip = QCheckBox("Skip WarpX (dev — unity ρ norms in step 2)")
        self.chk_skip.setChecked(bool(state.config.get("gui", {}).get("skip_pic", False)))

        # Inputs above Run — pad levers are not live-linked to WarpX.
        inputs = QGroupBox("Run inputs (change these, then Run this step below)")
        inputs_lay = QVBoxLayout(inputs)
        dep = QLabel(
            "Yes — you must re-run step 01 after moving pad levers or PIC steps. "
            "Plots below only scrub the last WarpX output until you run again."
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
        pf.addRow("PIC steps", self.pic_steps)
        pf.addRow(self.chk_skip)
        pic_row.addWidget(pg)
        self.chk_live = QCheckBox("Auto-scrub saved frames (2 Hz)")
        self.chk_live.setToolTip(
            "Steps through cached density_diag plotfiles only. Does not re-run WarpX."
        )
        pic_row.addWidget(self.chk_live, stretch=1)
        inputs_lay.addLayout(pic_row)
        warp_hint = QLabel(
            "<b>What N steps evolve:</b> electron ring + arc seed + inject beams; cathode V ramp; "
            "|ρ_e| plotfiles every 100 steps. "
            "<b>Not</b> laminar fuel proof (step 03). Geometry / kV / B: re-run step 00 first."
        )
        warp_hint.setWordWrap(True)
        warp_hint.setTextFormat(Qt.TextFormat.RichText)
        warp_hint.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        inputs_lay.addWidget(warp_hint)

        self._layout.removeWidget(self.toolbar)
        self._layout.removeWidget(self.gate)
        self._layout.removeWidget(self.log)
        self._layout.insertWidget(1, inputs)
        self._layout.addWidget(self.toolbar)
        self._layout.addWidget(self.gate)
        self._layout.addWidget(self.log)

        right = QWidget()
        rlay = QVBoxLayout(right)

        lon_grp = QGroupBox("WarpX PIC timelapse (from plotfiles)")
        lon_lay = QVBoxLayout(lon_grp)
        lon_row = QHBoxLayout()
        self.lon_field = QComboBox()
        self.lon_field.addItems(["|ρ_e| electrons", "|ρ_beam| inject (if present)"])
        self.lon_field.setToolTip("Applies to the lower r–z histogram panel when beam diagnostics exist.")
        lon_row.addWidget(QLabel("Lower panel field"))
        lon_row.addWidget(self.lon_field, stretch=1)
        lon_lay.addLayout(lon_row)
        self.lon_source = QLabel("Data: —")
        self.lon_source.setStyleSheet("color: #9ece6a; font-size: 11px;")
        self.lon_source.setWordWrap(True)
        lon_lay.addWidget(self.lon_source)
        lon_lay.addWidget(QLabel("Primary — x–z (WarpX cell grid)"))
        self.canvas_xz = MplCanvas(7, 3.6)
        lon_lay.addWidget(self.canvas_xz, stretch=3)
        self.lon_map_eq = QLabel(STEP01_MAP_EQUATION_HTML)
        self.lon_map_eq.setWordWrap(True)
        self.lon_map_eq.setTextFormat(Qt.TextFormat.RichText)
        self.lon_map_eq.setStyleSheet("color: #a9b1d6; font-size: 11px; padding: 4px 0;")
        lon_lay.addWidget(self.lon_map_eq)
        lon_lay.addWidget(QLabel("Advanced — r–z radius histogram (bin sum)"))
        self.canvas_rz = MplCanvas(7, 2.5)
        lon_lay.addWidget(self.canvas_rz, stretch=1)
        lon_scrub = QHBoxLayout()
        lon_scrub.addWidget(QLabel("Time"))
        self.lon_time = QSlider()
        self.lon_time.setOrientation(Qt.Orientation.Horizontal)
        self.lon_time.setEnabled(False)
        self.lon_time_label = QLabel("t = —")
        lon_scrub.addWidget(self.lon_time, stretch=1)
        lon_scrub.addWidget(self.lon_time_label)
        lon_lay.addLayout(lon_scrub)
        rlay.addWidget(lon_grp, stretch=2)

        pic_grp = QGroupBox("Transverse PIC — WarpX |ρ_e| (last run)")
        pic_lay = QVBoxLayout(pic_grp)
        self.canvas = MplCanvas(6, 3.2)
        pic_lay.addWidget(self.canvas, stretch=1)
        rlay.addWidget(pic_grp, stretch=1)

        self.metrics = MetricGrid(4)
        rlay.addWidget(self.metrics)
        self._layout.addWidget(right, stretch=1)

        self._lon_xy = None
        self._lon_rz = None
        self._live_timer = QTimer(self)
        self._live_timer.setInterval(500)
        self._live_timer.timeout.connect(self._on_live_tick)

        self.chk_live.toggled.connect(self._update_live_timer)
        self.lon_field.currentIndexChanged.connect(self._draw_longitudinal)
        self.lon_time.valueChanged.connect(self._draw_longitudinal)

        self._load_pad_from_config()
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

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
        self._refresh_transverse_pic()
        # Pad levers do not re-run WarpX; cached frames stay until Run this step.

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
        self._state.update_pic_settings(steps=self.pic_steps.value(), skip_pic=self.chk_skip.isChecked())
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
            self._lon_rz = None
            self.lon_time.setEnabled(False)
            draw_step01_placeholder(self.canvas_xz.figure, empty_msg)
            draw_step01_placeholder(self.canvas_rz.figure, empty_msg)
            self.lon_source.setText("Data: none (not WarpX)")
            self.canvas_xz.draw()
            self.canvas_rz.draw()
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
            self._lon_rz = compute_longitudinal_preview(
                inputs,
                LongitudinalFocus.CORE_TUBE,
                laminar_on=True,
                pic_diags=diags,
                use_heuristic_pic=False,
                warpx_xy_direct=False,
            )
            self.lon_source.setText(data_source_caption(self._lon_xy))
            n = min(len(self._lon_xy.time_s), len(self._lon_rz.time_s))
            self.lon_time.setEnabled(n > 1)
            self.lon_time.setMaximum(max(0, n - 1))
            if self.lon_time.value() > max(0, n - 1):
                self.lon_time.setValue(0)
            self._draw_longitudinal()
        except Exception as exc:
            draw_step01_placeholder(self.canvas_xz.figure, str(exc))
            draw_step01_placeholder(self.canvas_rz.figure, str(exc))
            self.lon_source.setText(f"Data: error — {exc}")
            self.canvas_xz.draw()
            self.canvas_rz.draw()
            self._lon_xy = None
            self._lon_rz = None
            self.lon_time.setEnabled(False)

    def _draw_longitudinal(self) -> None:
        if self._lon_xy is None or self._lon_rz is None:
            return
        inputs = self._gather_inputs()
        idx = self.lon_time.value()
        draw_step01_warpx_xz(self.canvas_xz.figure, self._lon_xy, idx, inputs=inputs)
        field_idx = 1 if self.lon_field.currentIndex() == 1 and self._lon_rz.secondary is not None else 0
        draw_step01_warpx_rz_remap(
            self.canvas_rz.figure,
            self._lon_rz,
            idx,
            inputs=inputs,
            field_index=field_idx,
        )
        t = self._lon_xy.time_s[idx]
        n = min(len(self._lon_xy.time_s), len(self._lon_rz.time_s))
        self.lon_time_label.setText(f"t = {t:.3e} s  ({idx + 1}/{n})")
        self.canvas_xz.draw()
        self.canvas_rz.draw()

    def _update_live_timer(self) -> None:
        pad = self.startup.pad_state()
        if self.chk_live.isChecked() and pad.bleed_air_open:
            self._live_timer.start()
        else:
            self._live_timer.stop()

    def _on_live_tick(self) -> None:
        if self._lon_xy is None or len(self._lon_xy.time_s) <= 1:
            self._rebuild_longitudinal()
            return
        n = min(len(self._lon_xy.time_s), len(self._lon_rz.time_s) if self._lon_rz else 0)
        nxt = (self.lon_time.value() + 1) % n
        self.lon_time.blockSignals(True)
        self.lon_time.setValue(nxt)
        self.lon_time.blockSignals(False)
        self._draw_longitudinal()

    def _refresh_transverse_pic(self) -> None:
        import json
        from pathlib import Path

        from tools.orbitron_proof_chain.chain_lib import CHAIN_ROOT, load_config, step_completed

        data = None
        art = CHAIN_ROOT / load_config()["steps"]["01"]["artifact"]
        if art.is_file():
            try:
                data = json.loads(art.read_text(encoding="utf-8"))
            except Exception:
                pass
        elif step_completed("01"):
            data = self._state.try_load_step("01")

        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if data and data.get("ok") is False:
            rc = data.get("returncode", "?")
            ax.text(
                0.5,
                0.5,
                f"WarpX failed (exit {rc})\n\nSee log — fix env, then Run this step",
                ha="center",
                va="center",
                color="#f7768e",
                fontsize=11,
            )
            self.gate.set_gate("Gate: WarpX did not finish — no plotfiles to preview.", ok=False)
        elif data and not data.get("skipped"):
            slice3d, err = load_pic_slice_2d_with_error()
            if slice3d:
                x, z, rho = slice3d
                im = ax.pcolormesh(x, z, rho, shading="auto", cmap="magma")
                fig.colorbar(im, ax=ax, label="|ρ_e|")
                run_th = data.get("throttle")
                run_co = data.get("compressor")
                run_pu = data.get("cathode_pulse")
                pad_now = self.startup.pad_state()
                title = "WarpX |ρ_e| — transverse (x–z) at one bore station"
                if run_th is not None:
                    title += f"\nrun: thr={run_th:.2f} comp={run_co:.2f} pulse={run_pu:.2f}"
                ax.set_title(title, color="#c0caf5", fontsize=9)
                ax.set_xlabel("x [m]")
                ax.set_ylabel("z [m]")
                if run_th is not None and (
                    abs(pad_now.throttle - float(run_th)) > 0.02
                    or abs(pad_now.compressor - float(run_co)) > 0.02
                    or abs(pad_now.cathode_pulse - float(run_pu)) > 0.02
                ):
                    ax.text(
                        0.5,
                        0.02,
                        "Levers changed — Run this step to refresh WarpX",
                        transform=ax.transAxes,
                        ha="center",
                        va="bottom",
                        color="#e0af68",
                        fontsize=8,
                    )
            else:
                ax.text(0.5, 0.5, err or "No PIC preview", ha="center", va="center", color="#a9b1d6", fontsize=10)
            diags = Path(data.get("diags_dir", ""))
            n_pf = len(list_pic_plotfiles(diags)) if diags.is_dir() else len(data.get("plotfiles", []))
            self.metrics.set_metrics(
                [
                    ("Plotfiles", str(n_pf), str(diags) if diags else "", "#9ece6a" if n_pf else "#e0af68"),
                    ("WarpX frames", str(len(self._lon_xy.time_s)) if self._lon_xy else "0", "density_diag", "#7aa2f7"),
                    ("Throttle", f"{data.get('throttle', 0):.2f}", "pad", "#7aa2f7"),
                    ("Pulse", f"{data.get('cathode_pulse', 0):.2f}", "cathode", "#7aa2f7"),
                ]
            )
            if n_pf and slice3d:
                self.gate.set_gate("Gate: PIC + longitudinal preview — run step 02 to reduce ρ norms.", ok=True)
            elif n_pf:
                self.gate.set_gate("Gate: plotfiles on disk but transverse preview failed.", ok=None)
            else:
                self.gate.set_gate("Gate: re-run WarpX for transverse plotfiles.", ok=False)
        elif data and data.get("skipped"):
            ax.text(0.5, 0.5, "PIC skipped\n(SKIP_PIC)", ha="center", va="center", color="#e0af68", fontsize=14)
            self.gate.set_gate("Gate: skipped — step 2 will use unity norms (not Tier-2 closed).", ok=None)
        else:
            ax.text(0.5, 0.5, "Run WarpX for transverse |ρ_e|", ha="center", va="center", color="#565f89", fontsize=12)
            if self._lon_xy is not None:
                self.gate.set_gate(
                    "Gate: longitudinal preview active — Run WarpX for Tier-2 transverse PIC.",
                    ok=None,
                )
            else:
                self.gate.set_gate(self._gate_hint, ok=None)
        fig.tight_layout()
        self.canvas.draw()

    def refresh_from_artifacts(self) -> None:
        self._rebuild_longitudinal()
        self._refresh_transverse_pic()
        self._update_live_timer()


class Step02ReducePanel(ProofStepPanel):
    go_to_step = Signal(str)

    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "02",
            "PIC reduce",
            "Reduce last plotfile to ρ_e_norm and ρ_beam_norm — handoff to 0D plant and fusion channel. "
            "No pad sliders here — use the links below to change inputs, then re-run step 01.",
            "0.2 ≤ ρ_norm ≤ 3.0 (plant clamp band).",
            state,
            parent,
        )
        nav = QHBoxLayout()
        self.lbl_levers = QLabel()
        self.lbl_levers.setWordWrap(True)
        self.lbl_levers.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        nav.addWidget(self.lbl_levers, stretch=1)
        btn01 = QPushButton("Pad levers → step 01")
        btn01.setToolTip("Throttle, compressor, cathode pulse, PIC step count")
        btn01.clicked.connect(lambda: self.go_to_step.emit("01"))
        btn00 = QPushButton("Geometry / kV → step 00")
        btn00.clicked.connect(lambda: self.go_to_step.emit("00"))
        nav.addWidget(btn00)
        nav.addWidget(btn01)
        self._layout.addLayout(nav)

        split = QSplitter()
        self.canvas_bars = MplCanvas(5, 3.5)
        self.canvas_gauge = MplCanvas(4, 3.5)
        split.addWidget(self.canvas_bars)
        split.addWidget(self.canvas_gauge)
        self._layout.addWidget(split, stretch=1)
        self.metrics = MetricGrid(4)
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

    def refresh_from_artifacts(self) -> None:
        self._refresh_lever_summary()
        data = self._state.try_load_step("02")
        fig1 = self.canvas_bars.figure
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        if data:
            labels = ["ρ_e norm", "ρ_beam norm"]
            vals = [data.get("rho_e_norm", 1), data.get("rho_beam_norm", 1)]
            colors = ["#7aa2f7" if 0.2 <= v <= 3 else "#f7768e" for v in vals]
            ax1.bar(labels, vals, color=colors)
            ax1.axhline(0.2, color="#565f89", ls="--", lw=0.8)
            ax1.axhline(3.0, color="#565f89", ls="--", lw=0.8)
            ax1.set_ylabel("Normalized ρ")
            ax1.set_title("PIC coupling proxies", color="#c0caf5")
            ax1.grid(True, alpha=0.25)

            fig2 = self.canvas_gauge.figure
            fig2.clear()
            ax2 = fig2.add_subplot(111)
            re, rb = vals[0], vals[1]
            ok_e = 0.2 <= re <= 3.0
            ok_b = 0.2 <= rb <= 3.0
            ax2.barh(["ρ_e", "ρ_beam"], [re, rb], color=["#9ece6a" if ok_e else "#f7768e", "#9ece6a" if ok_b else "#f7768e"])
            ax2.set_xlim(0, max(3.5, max(vals) * 1.2))
            ax2.set_title("Clamp band", color="#c0caf5")

            self.metrics.set_metrics(
                [
                    ("ρ_e mean", f"{data.get('rho_e_mean', 0):.2e}", f"norm {re:.3f}", None),
                    ("ρ_beam screen", f"{data.get('rho_beam_screen_mean', 0):.2e}", f"norm {rb:.3f}", None),
                    ("Refs", "1e15 / 1e10", "normalization", "#565f89"),
                    (
                        "Tier 2",
                        "Coupled" if not data.get("skipped") else "Skipped",
                        "",
                        "#9ece6a" if ok_e and ok_b else "#e0af68",
                    ),
                ]
            )
            gate_ok = ok_e and ok_b
            self.gate.set_gate(
                "Gate: norms in band — feed fusion channel & plant."
                if gate_ok
                else "Gate: norms out of band — revisit PIC or geometry.",
                ok=gate_ok,
            )
        else:
            ax1.text(0.5, 0.5, "Run PIC reduce", ha="center", color="#565f89")
            self.gate.set_gate(self._gate_hint, ok=None)
        fig1.tight_layout()
        self.canvas_bars.draw()
        if data:
            fig2.tight_layout()
            self.canvas_gauge.draw()
