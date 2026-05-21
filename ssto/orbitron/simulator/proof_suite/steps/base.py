"""Base class for proof-chain step panels."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.widgets import GateStrip, LogPane, StepBanner, StepToolBar


class ProofStepPanel(QWidget):
    """One step in the iterative design suite."""

    step_completed = Signal(str)
    status_changed = Signal()

    def __init__(
        self,
        step_id: str,
        title: str,
        blurb: str,
        gate_hint: str,
        state: ProofSuiteState,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.step_id = step_id
        self._state = state
        self._gate_hint = gate_hint

        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        scroll.setWidget(body)
        self._layout = QVBoxLayout(body)
        outer.addWidget(scroll)

        self.banner = StepBanner(step_id, title, blurb)
        self._layout.addWidget(self.banner)
        self.toolbar = StepToolBar()
        self._layout.addWidget(self.toolbar)
        self.gate = GateStrip()
        self._layout.addWidget(self.gate)
        self.log = LogPane()
        self._layout.addWidget(self.log)

        self.toolbar.btn_refresh.clicked.connect(self.refresh_from_artifacts)
        self.gate.set_gate(f"Gate: {gate_hint}", ok=None)

    def _sync_config(self) -> None:
        """Override: push widget values into chain_config before run."""

    def refresh_from_artifacts(self) -> None:
        """Override: load JSON/NPZ and redraw."""
        self.status_changed.emit()

    def on_step_finished(self, result: dict | None, error: str | None) -> None:
        self.toolbar.progress.hide()
        self.toolbar.btn_run.setEnabled(True)
        if error:
            self.log.append_line(f"ERROR: {error}")
            self.gate.set_gate(f"Failed: {error[:200]}", ok=False)
            return
        self.log.append_line("Step finished OK.")
        self.refresh_from_artifacts()
        self.step_completed.emit(self.step_id)
        self.status_changed.emit()
