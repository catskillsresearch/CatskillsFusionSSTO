"""Design validation report — unobtanium spec quantification (primary simulator output)."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ssto.orbitron.simulator.validation import DesignValidationReport


class ValidationPanel(QWidget):
    def __init__(
        self,
        on_validate: Callable[[], DesignValidationReport],
        on_export_yaml: Callable[[Path], Path],
    ) -> None:
        super().__init__()
        self._on_validate = on_validate
        self._on_export_yaml = on_export_yaml
        self._last_report: DesignValidationReport | None = None

        layout = QVBoxLayout(self)
        self.headline = QLabel("Run pad startup, then Validate design.")
        self.headline.setWordWrap(True)
        layout.addWidget(self.headline)

        btn_row = QWidget()
        brow = QHBoxLayout(btn_row)
        self.btn_validate = QPushButton("Validate design at current point")
        self.btn_validate.setToolTip(
            "Check U1–U4 specs, p-¹¹B fusion model, 3.5 MW target, and jet closure."
        )
        self.btn_export = QPushButton("Export YAML…")
        self.btn_export.setToolTip("Write validation report for UNOBTANIUM / spec documents.")
        brow.addWidget(self.btn_validate)
        brow.addWidget(self.btn_export)
        layout.addWidget(btn_row)

        self.report = QTextEdit()
        self.report.setReadOnly(True)
        layout.addWidget(self.report, stretch=1)

        self.btn_validate.clicked.connect(self._run)
        self.btn_export.clicked.connect(self._export)

    def show_report(self, vrep: DesignValidationReport) -> None:
        self._last_report = vrep
        color = "#22c55e" if vrep.design_validated else "#fbbf24"
        self.headline.setText(
            f'<span style="color:{color}; font-weight:bold;">{vrep.summary}</span>'
        )
        self.report.setPlainText(vrep.to_text())

    def _run(self) -> None:
        vrep = self._on_validate()
        self.show_report(vrep)

    def _export(self) -> None:
        if self._last_report is None:
            self._run()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export validation YAML",
            str(Path.home() / "orbitron_design_validation.yaml"),
            "YAML (*.yaml *.yml)",
        )
        if not path:
            return
        try:
            out = self._on_export_yaml(Path(path))
            QMessageBox.information(self, "Export", f"Wrote:\n{out}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
