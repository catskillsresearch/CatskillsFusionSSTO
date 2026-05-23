"""Pad startup console — Reply 15 Brayton + Reply 19 Phase 1 interlocks (PySide6)."""
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
    """
    Operator sequence aligned with ``orbitron_operator_console_spec.yaml`` and
    ``OPERATING_PHASES.md`` (Phase 1 UHV → laser → HV → ignite; Phase 2 bleed path).

    ``lever_profile="pic_electron_ring"`` (proof-chain step 01): only ring density + cathode
    pulse levers — no compressor slider (Brayton compressor enters step 06 plant).
    """

    def __init__(
        self,
        on_change: Callable[[], None],
        *,
        include_live_checkbox: bool = True,
        lever_profile: str = "plant",
    ) -> None:
        super().__init__()
        self._on_change = on_change
        self._include_live_checkbox = include_live_checkbox
        self._lever_profile = lever_profile

        layout = QVBoxLayout(self)

        air = QGroupBox("Rig air path (Reply 15 / Phase 2 pad)")
        air_form = QFormLayout(air)
        self.chk_apu = QCheckBox("1 — Pad APU ON")
        self.chk_starter = QCheckBox("2 — STARTER (requires APU)")
        self.chk_bleed = QCheckBox("3 — BLEED AIR (compressor path)")
        for chk in (self.chk_apu, self.chk_starter, self.chk_bleed):
            air_form.addRow(chk)
        layout.addWidget(air)

        phase1 = QGroupBox("Phase 1 — UHV & fuel (Reply 19 §1.1–1.4)")
        p1_form = QFormLayout(phase1)
        self.chk_vacuum = QCheckBox("4 — VACUUM OK (≤10⁻⁶ Torr class; requires bleed)")
        self.chk_laser = QCheckBox("5 — LASER ARMED (355 nm; requires vacuum)")
        self.chk_hv = QCheckBox("6 — HV ENABLED (600 kV class; requires laser)")
        self.chk_vacuum.setToolTip(
            "Interlock: turbomolecular pump-down complete; gauge in range. "
            "Required before arming UV ablation into the chamber."
        )
        self.chk_laser.setToolTip(
            "Interlock: Q-switched Nd:YAG path aligned; power meter checked. "
            "Solid ¹¹B ablation only — not a borane gas feed."
        )
        self.chk_hv.setToolTip(
            "Interlock: precision DC HVPS / feedthrough live; cathode bias applied. "
            "Electrostatic trap impels ablated B⁺ into orbitrap trajectories."
        )
        for chk in (self.chk_vacuum, self.chk_laser, self.chk_hv):
            p1_form.addRow(chk)
        layout.addWidget(phase1)

        ignite_box = QGroupBox("Fusion arm")
        ignite_form = QFormLayout(ignite_box)
        self.chk_ignite = QCheckBox("7 — IGNITE (requires HV + bleed)")
        self.chk_ignite.setToolTip(
            "Arms p-¹¹B channel at run levers; gates H₂ + laser-ablated ¹¹B inventory in 0D model."
        )
        ignite_form.addRow(self.chk_ignite)
        layout.addWidget(ignite_box)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        layout.addWidget(self.status_label)

        run = QGroupBox("Run levers (after ignite)")
        run_form = QFormLayout(run)

        self.slider_throttle = _slider(0, 100, 0)
        self.slider_compressor = _slider(0, 100, 0)
        self.slider_pulse = _slider(0, 100, 60)
        self.lbl_throttle = QLabel("0.00")
        self.lbl_compressor = QLabel("0.00")
        self.lbl_pulse = QLabel("0.60")
        self._row_compressor: tuple[str, QHBoxLayout] | None = None

        def _row(name: str, slider: QSlider, lbl: QLabel) -> None:
            row = QHBoxLayout()
            row.addWidget(slider, stretch=1)
            row.addWidget(lbl)
            run_form.addRow(name, row)

        if lever_profile == "pic_electron_ring":
            _row("Ring density scale τ (W/S)", self.slider_throttle, self.lbl_throttle)
            _row("Cathode pulse / shear p (I/K)", self.slider_pulse, self.lbl_pulse)
            self.slider_compressor.hide()
            self.lbl_compressor.hide()
            note = QLabel(
                "Step 01 WarpX: τ and p only. No fuel, no compressor — see validation_steps.md §1."
            )
            note.setWordWrap(True)
            note.setStyleSheet("color: #7aa2f7; font-size: 10px;")
            run_form.addRow(note)
        else:
            _row("Beam throttle (W/S)", self.slider_throttle, self.lbl_throttle)
            comp_row = QHBoxLayout()
            comp_row.addWidget(self.slider_compressor, stretch=1)
            comp_row.addWidget(self.lbl_compressor)
            run_form.addRow("Compressor (U/J)", comp_row)
            _row("Cathode pulse / shear (I/K)", self.slider_pulse, self.lbl_pulse)

        self.chk_live = QCheckBox("Live steady-state + plasma animation (2 Hz)")
        self.chk_live.setToolTip(
            "Classic Orbitron simulator: 0D plant + device view refresh at 2 Hz while bleed is open."
        )
        if include_live_checkbox:
            run_form.addRow(self.chk_live)
        else:
            self.chk_live.setChecked(False)
            self.chk_live.hide()

        layout.addWidget(run)
        layout.addStretch()

        toggled = [
            self.chk_apu,
            self.chk_starter,
            self.chk_bleed,
            self.chk_vacuum,
            self.chk_laser,
            self.chk_hv,
            self.chk_ignite,
        ]
        if include_live_checkbox:
            toggled.append(self.chk_live)
        for w in toggled:
            w.toggled.connect(self._changed)
        for slider in (self.slider_throttle, self.slider_pulse):
            slider.valueChanged.connect(self._slider_changed)
        if lever_profile != "pic_electron_ring":
            self.slider_compressor.valueChanged.connect(self._slider_changed)
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
            self.chk_starter.setChecked(True)
            self.chk_bleed.setChecked(True)
            self.chk_vacuum.setChecked(True)
            self.chk_laser.setChecked(True)
            self.chk_hv.setChecked(True)
            self.chk_ignite.setChecked(True)
        self.slider_throttle.setValue(int(round(max(0.0, min(1.0, throttle)) * 100)))
        self.slider_compressor.setValue(int(round(max(0.0, min(1.0, compressor)) * 100)))
        if pulse is not None:
            self.slider_pulse.setValue(int(round(max(0.0, min(1.0, pulse)) * 100)))

    def apply_pad_state(self, pad: PadStartupState) -> None:
        """Load switches/sliders from a PadStartupState (e.g. chain_config)."""
        blockers = [
            self.chk_apu,
            self.chk_starter,
            self.chk_bleed,
            self.chk_vacuum,
            self.chk_laser,
            self.chk_hv,
            self.chk_ignite,
            self.chk_live,
            self.slider_throttle,
            self.slider_compressor,
            self.slider_pulse,
        ]
        for w in blockers:
            w.blockSignals(True)
        self.chk_apu.setChecked(pad.pad_apu_online)
        self.chk_starter.setChecked(pad.starter_engage)
        self.chk_bleed.setChecked(pad.bleed_air_open)
        self.chk_vacuum.setChecked(pad.vacuum_interlock_ok)
        self.chk_laser.setChecked(pad.laser_armed)
        self.chk_hv.setChecked(pad.hv_enabled)
        self.chk_ignite.setChecked(pad.startup_trigger)
        self.chk_live.setChecked(pad.live_simulation)
        self.slider_throttle.setValue(int(round(pad.throttle * 100)))
        self.slider_compressor.setValue(int(round(pad.compressor * 100)))
        self.slider_pulse.setValue(int(round(pad.cathode_pulse * 100)))
        for w in blockers:
            w.blockSignals(False)
        self._slider_changed()

    def pad_state(self) -> PadStartupState:
        return PadStartupState(
            pad_apu_online=self.chk_apu.isChecked(),
            starter_engage=self.chk_starter.isChecked(),
            bleed_air_open=self.chk_bleed.isChecked(),
            vacuum_interlock_ok=self.chk_vacuum.isChecked(),
            laser_armed=self.chk_laser.isChecked(),
            hv_enabled=self.chk_hv.isChecked(),
            startup_trigger=self.chk_ignite.isChecked(),
            throttle=self.slider_throttle.value() / 100.0,
            compressor=self.slider_compressor.value() / 100.0,
            cathode_pulse=self.slider_pulse.value() / 100.0,
            live_simulation=self.chk_live.isChecked(),
            laminar_relaminarization=True,
        )
