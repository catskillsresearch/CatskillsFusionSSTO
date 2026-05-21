"""Interactive timelapse scrubber — pad-synced and PIC-aware."""
from __future__ import annotations

from typing import Callable

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ssto.orbitron.simulator.blender_layout import draw_blender_underlay, engine_axial_layout
from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus, resolve_longitudinal_focus
from ssto.orbitron.simulator.longitudinal.run import LongitudinalRun, run_longitudinal
from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.pic_session import PicSession
from ssto.orbitron.simulator.types import SimulatorInputs


class LongitudinalWorker(QThread):
    finished = Signal(object, object)  # LongitudinalRun | None, error str | None

    def __init__(
        self,
        focus: LongitudinalFocus,
        inputs: SimulatorInputs,
        *,
        pic_steps: int,
        use_heuristic_pic: bool,
        pic_stack: object | None,
    ) -> None:
        super().__init__()
        self._focus = focus
        self._inputs = inputs
        self._pic_steps = pic_steps
        self._use_heuristic = use_heuristic_pic
        self._pic_stack = pic_stack

    def run(self) -> None:
        try:
            run = run_longitudinal(
                self._focus,
                self._inputs,
                pic_steps=self._pic_steps,
                use_heuristic_pic=self._use_heuristic,
                pic_stack=self._pic_stack,
            )
            self.finished.emit(run, None)
        except Exception as exc:
            self.finished.emit(None, str(exc))


class TimelapsePanel(QWidget):
    def __init__(
        self,
        gather_inputs: Callable[[], SimulatorInputs],
        *,
        get_pic_session: Callable[[], PicSession],
        get_plasma_phase: Callable[[], float],
    ) -> None:
        super().__init__()
        self._gather_inputs = gather_inputs
        self._get_pic_session = get_pic_session
        self._get_plasma_phase = get_plasma_phase
        self._run: LongitudinalRun | None = None
        self._pad_revision = 0

        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        self.focus_combo = QComboBox()
        for label, foc in (
            ("1 — Fusion channel s–r (laminar hack)", LongitudinalFocus.FUSION_CHANNEL_SR),
            ("2 — Core tube (PIC transverse)", LongitudinalFocus.CORE_TUBE),
            ("3 — Core + magnet bore", LongitudinalFocus.CORE_PLUS_MAGNET),
            ("4 — Full duct air (s–r)", LongitudinalFocus.FULL_DUCT_AIR),
        ):
            self.focus_combo.addItem(label, foc)
        self.btn_run = QPushButton("Run longitudinal 2D")
        row.addWidget(QLabel("Focus:"))
        row.addWidget(self.focus_combo, stretch=1)
        row.addWidget(self.btn_run)
        layout.addLayout(row)

        sync_row = QHBoxLayout()
        self.chk_sync_pad = QCheckBox("Sync with pad startup")
        self.chk_sync_pad.setChecked(True)
        self.chk_auto_play = QCheckBox("Auto-play timelapse when Live is on")
        self.chk_auto_play.setChecked(True)
        sync_row.addWidget(self.chk_sync_pad)
        sync_row.addWidget(self.chk_auto_play)
        layout.addLayout(sync_row)

        self.chk_laminar = QCheckBox("Laminar relaminarization ON (PSP2/Jin + E×B shear)")
        self.chk_laminar.setChecked(True)
        sync_row.addWidget(self.chk_laminar)

        self.caption = QLabel(
            "Fusion channel (level 1): longitudinal s–r density + p-¹¹B rate — "
            "scrub time to see clumps break up when laminar hack is ON (Orbitron-video intent)."
        )
        self.caption.setWordWrap(True)
        layout.addWidget(self.caption)

        self.canvas = FigureCanvasQTAgg(Figure(figsize=(7, 4.5)))
        layout.addWidget(self.canvas, stretch=1)

        scrub = QHBoxLayout()
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setEnabled(False)
        self.time_label = QLabel("t = —")
        self.field_combo = QComboBox()
        self.field_combo.addItems(["Primary field", "Secondary field"])
        self.field_combo.setEnabled(False)
        scrub.addWidget(QLabel("Time"))
        scrub.addWidget(self.time_slider, stretch=1)
        scrub.addWidget(self.time_label)
        scrub.addWidget(self.field_combo)
        layout.addLayout(scrub)

        self._play_timer = QTimer(self)
        self._play_timer.setInterval(400)
        self._play_timer.timeout.connect(self._on_auto_advance)

        self.btn_run.clicked.connect(self._on_run)
        self.time_slider.valueChanged.connect(self._on_scrub)
        self.field_combo.currentIndexChanged.connect(self._on_scrub)
        self.chk_sync_pad.toggled.connect(lambda _: self._schedule_pad_refresh())
        self.chk_laminar.toggled.connect(lambda _: self._schedule_pad_refresh())
        self.focus_combo.currentIndexChanged.connect(lambda _: self._schedule_pad_refresh())

    def _suggested_focus(self, inputs: SimulatorInputs) -> LongitudinalFocus:
        pad = inputs.pad
        if pad.startup_trigger:
            return LongitudinalFocus.FUSION_CHANNEL_SR
        if pad.bleed_air_open:
            return LongitudinalFocus.FULL_DUCT_AIR
        return LongitudinalFocus.CORE_PLUS_MAGNET

    def notify_pad_changed(self) -> None:
        """Called from MainWindow when pad switches / live mode change."""
        if not self.chk_sync_pad.isChecked():
            return
        self._schedule_pad_refresh()

    def notify_pic_loaded(self) -> None:
        """After WarpX completes — refresh core view from cached stack."""
        if self.chk_sync_pad.isChecked():
            self._schedule_pad_refresh(force_heuristic=False)
        else:
            self.caption.setText("WarpX PIC loaded — enable pad sync or press Run.")

    def _schedule_pad_refresh(self, *, force_heuristic: bool = True) -> None:
        inputs = self._gather_inputs()
        if self.chk_sync_pad.isChecked():
            suggested = self._suggested_focus(inputs)
            for i in range(self.focus_combo.count()):
                if resolve_longitudinal_focus(
                    self.focus_combo.itemData(i), i, default=suggested
                ) == suggested:
                    self.focus_combo.setCurrentIndex(i)
                    break
        self._start_run(heuristic=force_heuristic)

    def _on_run(self) -> None:
        self._start_run(heuristic=False)

    def _start_run(self, *, heuristic: bool) -> None:
        focus = resolve_longitudinal_focus(
            self.focus_combo.currentData(),
            self.focus_combo.currentIndex(),
            default=LongitudinalFocus.CORE_TUBE,
        )
        inputs = self._gather_inputs()
        session = self._get_pic_session()
        pic_stack = (
            session.stack
            if session.available
            and focus not in (LongitudinalFocus.FULL_DUCT_AIR, LongitudinalFocus.FUSION_CHANNEL_SR)
            else None
        )
        use_heuristic = (
            heuristic
            and pic_stack is None
            and focus not in (LongitudinalFocus.FULL_DUCT_AIR, LongitudinalFocus.FUSION_CHANNEL_SR)
        )

        self.btn_run.setEnabled(False)
        if focus == LongitudinalFocus.FUSION_CHANNEL_SR:
            mode = "fusion s–r + laminar hack" if self.chk_laminar.isChecked() else "fusion s–r (clumping)"
        elif focus == LongitudinalFocus.FULL_DUCT_AIR:
            mode = "annulus"
        else:
            mode = (
                "heuristic PIC"
                if use_heuristic
                else ("cached PIC" if pic_stack else "WarpX PIC")
            )
        self.caption.setText(f"Running {focus.value} ({mode})…")
        steps = 120 if focus == LongitudinalFocus.FULL_DUCT_AIR else 240
        self._worker = LongitudinalWorker(
            focus,
            inputs,
            pic_steps=steps,
            use_heuristic_pic=use_heuristic,
            pic_stack=pic_stack,
        )
        self._worker.finished.connect(self._on_done)
        self._worker.start()

    def _on_done(self, run: object, err: object) -> None:
        self.btn_run.setEnabled(True)
        if err:
            self.caption.setText(f"Error: {err}")
            return
        assert isinstance(run, LongitudinalRun)
        self._run = run
        extra = ""
        if run.meta.get("model") == "fusion_channel_sr":
            extra = (
                f" | clump={run.meta.get('clump_index_final', 0):.2f}"
                f" reduction×{run.meta.get('clump_reduction_ratio', 1):.2f}"
                f" P_int={run.meta.get('integrated_fusion_power_mw', 0):.2f} MW"
            )
        self.caption.setText(
            run.domain.label
            + " — "
            + str(run.meta.get("note", run.meta.get("model", "")))
            + extra
        )
        self.time_slider.setEnabled(True)
        self.field_combo.setEnabled(True)
        self.time_slider.setMaximum(max(0, len(run.time_s) - 1))
        self._sync_slider_to_phase()
        self._draw_frame(self.time_slider.value())
        self._update_auto_play()

    def _update_auto_play(self) -> None:
        inp = self._gather_inputs()
        if self.chk_auto_play.isChecked() and inp.pad.live_simulation and inp.pad.bleed_air_open:
            self._play_timer.start()
        else:
            self._play_timer.stop()

    def _on_auto_advance(self) -> None:
        if self._run is None:
            return
        session = self._get_pic_session()
        if session.available:
            session.set_phase(self._get_plasma_phase())
        n = len(self._run.time_s)
        if n <= 1:
            return
        nxt = (self.time_slider.value() + 1) % n
        self.time_slider.blockSignals(True)
        self.time_slider.setValue(nxt)
        self.time_slider.blockSignals(False)
        self._draw_frame(nxt)

    def _sync_slider_to_phase(self) -> None:
        if self._run is None:
            return
        session = self._get_pic_session()
        n = len(self._run.time_s)
        if n <= 1:
            self.time_slider.setValue(0)
            return
        if session.available:
            fi = session.set_phase(self._get_plasma_phase())
            self.time_slider.setValue(min(fi, n - 1))
        else:
            phase = self._get_plasma_phase()
            self.time_slider.setValue(int(phase * (n - 1)) % n)

    def on_live_tick(self) -> None:
        """MainWindow live timer — keep timelapse frame aligned with Device plasma phase."""
        if self._run is None:
            return
        if not self.chk_auto_play.isChecked():
            return
        self._sync_slider_to_phase()
        self._draw_frame(self.time_slider.value())

    def _on_scrub(self) -> None:
        if self._run is None:
            return
        self._draw_frame(self.time_slider.value())

    def _draw_frame(self, idx: int) -> None:
        run = self._run
        assert run is not None
        idx = max(0, min(idx, len(run.time_s) - 1))
        use_secondary = self.field_combo.currentIndex() == 1
        data = run.secondary if use_secondary and run.secondary is not None else run.primary
        label = run.secondary_label if use_secondary else run.primary_label

        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        d = run.domain
        inputs = self._gather_inputs()
        pad_status = evaluate_pad_status(inputs.pad)
        layout = engine_axial_layout(inputs.geometry, duct_length_m=d.s_max_m - d.s_min_m)

        if run.focus in (LongitudinalFocus.FULL_DUCT_AIR, LongitudinalFocus.FUSION_CHANNEL_SR):
            draw_blender_underlay(ax, layout, run.focus, symmetric=False)
            im = ax.pcolormesh(
                run.axis_horizontal,
                run.axis_vertical,
                data[idx],
                shading="auto",
                cmap="magma",
                alpha=0.72,
            )
            title_extra = ""
            if run.focus == LongitudinalFocus.FUSION_CHANNEL_SR:
                title_extra = (
                    f"  |  clump={run.meta.get('clump_index_final', 0):.2f}"
                    f"  laminar={'ON' if self.chk_laminar.isChecked() else 'OFF'}"
                )
            ax.set_title(
                f"{d.label}  |  pad: bleed={'ON' if pad_status.state.bleed_air_open else 'off'}"
                + title_extra
            )
        else:
            im = ax.pcolormesh(
                run.axis_horizontal,
                run.axis_vertical,
                data[idx],
                shading="auto",
                cmap="magma",
            )
            ax.add_patch(Circle((0, 0), d.r_cathode_m, fill=False, ec="#ca8a04", lw=1.5))
            ax.add_patch(Circle((0, 0), d.r_anode_m, fill=False, ec="#e8c547", lw=2))
            if run.focus == LongitudinalFocus.CORE_PLUS_MAGNET:
                ax.add_patch(
                    Circle((0, 0), d.r_magnet_od_m, fill=False, ec="#18181b", ls="--", lw=1.5)
                )
            inset = fig.add_axes([0.58, 0.08, 0.38, 0.32])
            draw_blender_underlay(inset, layout, run.focus)
            inset.set_title("CAD layout (s–r)", fontsize=8, color="#e2e8f0")
            armed = "ARMED" if pad_status.reactor_armed else "spin-up"
            ax.set_title(f"{d.label}  |  {label}  |  {armed}")

        fig.colorbar(im, ax=ax, label=label, fraction=0.046)
        ax.set_xlabel(run.horizontal_label)
        ax.set_ylabel(run.vertical_label)
        t = run.time_s[idx]
        self.time_label.setText(f"t = {t:.3e} s  (frame {idx + 1}/{len(run.time_s)})")
        fig.tight_layout()
        self.canvas.draw()
