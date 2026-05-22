"""Orbitron Proof Suite — iterative step-by-step design validation GUI."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.steps.step_00_02 import (
    Step00SpecPanel,
    Step01PicPanel,
    Step02ReducePanel,
)
from ssto.orbitron.simulator.proof_suite.steps.step_03_05 import (
    Step03FusionPanel,
    Step04FuelingPanel,
    Step05BurnPanel,
)
from ssto.orbitron.simulator.proof_suite.steps.step_06_09 import (
    Step06PlantPanel,
    Step07ClosurePanel,
    Step08ExportPanel,
    Step09SolvePanel,
)

_STATUS_ICON = {
    "pending": "○",
    "ok": "✓",
    "warn": "△",
    "skipped": "⊘",
}


class ProofSuiteMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Orbitron Proof Suite — iterative design validation")
        self.resize(1440, 920)
        self._state = ProofSuiteState()
        try:
            self._state.ensure_initialized()
        except Exception as exc:
            QMessageBox.warning(self, "Chain config", str(exc))

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        # --- Navigator ---
        nav = QWidget()
        nav.setMaximumWidth(320)
        nav_lay = QVBoxLayout(nav)
        title = QLabel("Proof chain")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #7aa2f7;")
        nav_lay.addWidget(title)
        sub = QLabel(
            "Run a step, then stay on it to change levers (no auto-advance). "
            "Pad sliders: step 01. Geometry: step 00. "
            "Artifacts: build/orbitron/chain/"
        )
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #565f89; font-size: 11px;")
        nav_lay.addWidget(sub)

        self.step_list = QListWidget()
        self.step_list.setStyleSheet(
            "QListWidget { background: #1a1b26; color: #c0caf5; }"
            "QListWidget::item:selected { background: #414868; }"
        )
        nav_lay.addWidget(self.step_list, stretch=1)

        btn_row = QVBoxLayout()
        self.btn_open_chain = QPushButton("Open chain folder")
        self.btn_doc = QPushButton("Open PROOF_SUITE.md")
        btn_row.addWidget(self.btn_open_chain)
        btn_row.addWidget(self.btn_doc)
        nav_lay.addLayout(btn_row)

        splitter.addWidget(nav)

        # --- Step panels ---
        self.stack = QStackedWidget()
        self._panels: list[QWidget] = []
        panel_classes = [
            Step00SpecPanel,
            Step01PicPanel,
            Step02ReducePanel,
            Step03FusionPanel,
            Step04FuelingPanel,
            Step05BurnPanel,
            Step06PlantPanel,
            Step07ClosurePanel,
            Step08ExportPanel,
            Step09SolvePanel,
        ]
        for cls in panel_classes:
            p = cls(self._state)
            if hasattr(p, "step_completed"):
                p.step_completed.connect(self._on_step_completed)
            if hasattr(p, "status_changed"):
                p.status_changed.connect(self._refresh_nav)
            if hasattr(p, "go_to_step"):
                p.go_to_step.connect(self.go_to_step)
            self._panels.append(p)
            self.stack.addWidget(p)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)

        for sid, name, _ in self._state.STEPS:
            item = QListWidgetItem(f"{_STATUS_ICON['pending']}  {sid} — {name}")
            item.setData(Qt.ItemDataRole.UserRole, sid)
            self.step_list.addItem(item)

        self.step_list.currentRowChanged.connect(self._on_step_selected)
        self.step_list.setCurrentRow(0)
        self.btn_open_chain.clicked.connect(self._open_chain)
        self.btn_doc.clicked.connect(self._open_doc)
        self._refresh_nav()

    def _on_step_selected(self, row: int) -> None:
        """Switch panel and stop step-01 snapshot playback when leaving WarpX PIC."""
        prev = self.stack.currentIndex()
        self.stack.setCurrentIndex(row)
        if prev == 1 and row != 1:
            pic = self._panels[1]
            if hasattr(pic, "stop_snapshot_playback"):
                pic.stop_snapshot_playback()

    def _refresh_nav(self) -> None:
        self._state.reload()
        for i, (sid, name, _) in enumerate(self._state.STEPS):
            st = self._state.step_status(sid)
            icon = _STATUS_ICON.get(st, "○")
            self.step_list.item(i).setText(f"{icon}  {sid} — {name}")

    def _on_step_completed(self, step_id: str) -> None:
        self._refresh_nav()
        # Stay on the step you just ran so pad/geometry controls remain visible.

    def go_to_step(self, step_id: str) -> None:
        row = next(i for i, (s, _, _) in enumerate(self._state.STEPS) if s == step_id)
        self.step_list.setCurrentRow(row)

    def _open_chain(self) -> None:
        from tools.orbitron_proof_chain.chain_lib import CHAIN_ROOT

        subprocess.run(["xdg-open", str(CHAIN_ROOT)], check=False)

    def _open_doc(self) -> None:
        for name in ("PROOF_SUITE.md", "validation_steps.md"):
            doc = Path(__file__).resolve().parents[2] / name
            if doc.is_file():
                subprocess.run(["xdg-open", str(doc)], check=False)
                return

