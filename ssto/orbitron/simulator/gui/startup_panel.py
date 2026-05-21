"""Pad startup console — FlightGear-equivalent switches and levers (PySide6)."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.types import PadStartupState


def _slider(lo: int, hi: int, val: int) -> QSlider:
    s = QSlider(Qt.Orientation.Horizontal)
    s.setRange(lo, hi)
    s.setValue(val)
    return s


class StartupPanel(QWidget):
    """Discrete pad steps 1–4 + run levers 5; mirrors ``orbitron_operator_console_spec.yaml``."""

    def __init__(self, on_change: Callable[[], None]) -> None:
        super().__init__()
        self._on_change = on_change

        layout = QVBoxLayout(self)

        steps = QGroupBox("Pad startup (same as FlightGear)")
        form = QFormLayout(steps)

        self.chk_apu = QCheckBox("1 — Pad APU ON")
        self.chk_starter = QCheckBox("2 — STARTER (requires APU)")
        self.chk_bleed = QCheckBox("3 — BLEED AIR")
        self.chk_ignite = QCheckBox("4 — IGNITE / BRB (requires bleed)")
        for chk in (self.chk_apu, self.chk_starter, self.chk_bleed, self.chk_ignite):
            form.addRow(chk)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        form.addRow("Status", self.status_label)

        layout.addWidget(steps)

        run = QGroupBox("5 — RUN (after ignite)")
        run_form = QFormLayout(run)

        self.slider_throttle = _slider(0, 100, 0)
        self.slider_compressor = _slider(0, 100, 0)
        self.slider_pulse = _slider(0, 100, 60)
        self.lbl_throttle = QLabel("0.00")
        self.lbl_compressor = QLabel("0.00")
        self.lbl_pulse = QLabel("0.60")

        def _row(name: str, slider: QSlider, lbl: QLabel) -> QHBoxLayout:
            row = QHBoxLayout()
            row.addWidget(slider, stretch=1)
            row.addWidget(lbl)
            run_form.addRow(name, row)
            return row

        _row("Beam throttle (W/S)", self.slider_throttle, self.lbl_throttle)
        _row("Compressor (U/J)", self.slider_compressor, self.lbl_compressor)
        _row("Cathode pulse (I/K)", self.slider_pulse, self.lbl_pulse)

        self.chk_live = QCheckBox("Live steady-state + plasma animation (2 Hz)")
        run_form.addRow(self.chk_live)

        layout.addWidget(run)
        layout.addStretch()

        for w in (
            self.chk_apu,
            self.chk_starter,
            self.chk_bleed,
            self.chk_ignite,
            self.chk_live,
        ):
            w.toggled.connect(self._changed)
        for slider in (self.slider_throttle, self.slider_compressor, self.slider_pulse):
            slider.valueChanged.connect(self._slider_changed)
        self._slider_changed()

    def _slider_changed(self) -> None:
        self.lbl_throttle.setText(f"{self.slider_throttle.value() / 100:.2f}")
        self.lbl_compressor.setText(f"{self.slider_compressor.value() / 100:.2f}")
        self.lbl_pulse.setText(f"{self.slider_pulse.value() / 100:.2f}")
        self._changed()

    def _changed(self) -> None:
        self._refresh_status()
        self._on_change()

    def _refresh_status(self) -> None:
        st = evaluate_pad_status(self.pad_state())
        lines = list(st.step_labels)
        for msg in st.interlock_messages:
            lines.append(f"⚠ {msg}")
        self.status_label.setText("\n".join(lines))

    def set_run_levers(
        self,
        throttle: float,
        compressor: float,
        *,
        pulse: float | None = None,
        arm_plant: bool = True,
    ) -> None:
        """Apply inverse-solve or preset run point to sliders."""
        if arm_plant:
            self.chk_apu.setChecked(True)
            self.chk_bleed.setChecked(True)
            self.chk_ignite.setChecked(True)
        self.slider_throttle.setValue(int(round(max(0.0, min(1.0, throttle)) * 100)))
        self.slider_compressor.setValue(int(round(max(0.0, min(1.0, compressor)) * 100)))
        if pulse is not None:
            self.slider_pulse.setValue(int(round(max(0.0, min(1.0, pulse)) * 100)))

    def apply_pad_state(self, pad: PadStartupState) -> None:
        """Load sliders/switches from a PadStartupState (e.g. chain_config)."""
        self.chk_apu.blockSignals(True)
        self.chk_starter.blockSignals(True)
        self.chk_bleed.blockSignals(True)
        self.chk_ignite.blockSignals(True)
        self.chk_live.blockSignals(True)
        self.chk_apu.setChecked(pad.pad_apu_online)
        self.chk_starter.setChecked(pad.starter_engage)
        self.chk_bleed.setChecked(pad.bleed_air_open)
        self.chk_ignite.setChecked(pad.startup_trigger)
        self.chk_live.setChecked(pad.live_simulation)
        self.slider_throttle.blockSignals(True)
        self.slider_compressor.blockSignals(True)
        self.slider_pulse.blockSignals(True)
        self.slider_throttle.setValue(int(round(pad.throttle * 100)))
        self.slider_compressor.setValue(int(round(pad.compressor * 100)))
        self.slider_pulse.setValue(int(round(pad.cathode_pulse * 100)))
        self.slider_throttle.blockSignals(False)
        self.slider_compressor.blockSignals(False)
        self.slider_pulse.blockSignals(False)
        self.chk_apu.blockSignals(False)
        self.chk_starter.blockSignals(False)
        self.chk_bleed.blockSignals(False)
        self.chk_ignite.blockSignals(False)
        self.chk_live.blockSignals(False)
        self._slider_changed()

    def pad_state(self) -> PadStartupState:
        return PadStartupState(
            pad_apu_online=self.chk_apu.isChecked(),
            starter_engage=self.chk_starter.isChecked(),
            bleed_air_open=self.chk_bleed.isChecked(),
            startup_trigger=self.chk_ignite.isChecked(),
            throttle=self.slider_throttle.value() / 100.0,
            compressor=self.slider_compressor.value() / 100.0,
            cathode_pulse=self.slider_pulse.value() / 100.0,
            live_simulation=self.chk_live.isChecked(),
            laminar_relaminarization=True,
        )
