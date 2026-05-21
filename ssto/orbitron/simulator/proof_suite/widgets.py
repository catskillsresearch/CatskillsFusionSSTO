"""Shared widgets for the Orbitron Proof Suite GUI."""
from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

_FIG_FACE = "#1a1b26"
_AXES_FACE = "#24283b"


def apply_dark_axes(ax) -> None:
    """Style axes after add_subplot (Figure() does not accept axes.facecolor)."""
    ax.set_facecolor(_AXES_FACE)
    for spine in ax.spines.values():
        spine.set_color("#414868")
    ax.tick_params(colors="#a9b1d6")
    ax.xaxis.label.set_color("#c0caf5")
    ax.yaxis.label.set_color("#c0caf5")
    title = ax.get_title()
    if title:
        ax.set_title(title, color="#c0caf5")


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width: float = 7.0, height: float = 4.5, dpi: int = 100) -> None:
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor=_FIG_FACE)
        super().__init__(self.figure)
        self.setMinimumHeight(int(height * dpi * 0.85))

    def add_subplot(self, *args, **kwargs):
        ax = self.figure.add_subplot(*args, **kwargs)
        apply_dark_axes(ax)
        return ax


class MetricCard(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "MetricCard { background: #24283b; border: 1px solid #414868; border-radius: 6px; }"
        )
        lay = QVBoxLayout(self)
        self._title = QLabel(title)
        self._title.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        self._value = QLabel("—")
        self._value.setStyleSheet("color: #c0caf5; font-size: 15px; font-weight: bold;")
        self._sub = QLabel("")
        self._sub.setStyleSheet("color: #565f89; font-size: 10px;")
        self._sub.setWordWrap(True)
        lay.addWidget(self._title)
        lay.addWidget(self._value)
        lay.addWidget(self._sub)

    def set_value(self, text: str, *, sub: str = "", color: str | None = None) -> None:
        self._value.setText(text)
        self._sub.setText(sub)
        if color:
            self._value.setStyleSheet(f"color: {color}; font-size: 15px; font-weight: bold;")


class MetricGrid(QWidget):
    def __init__(self, columns: int = 4, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setSpacing(8)
        self._cols = columns
        self._cards: list[MetricCard] = []

    def set_metrics(self, items: list[tuple[str, str, str, str | None]]) -> None:
        """(title, value, sub, optional hex color)."""
        while self._cards:
            w = self._cards.pop()
            self._grid.removeWidget(w)
            w.deleteLater()
        for i, (title, val, sub, color) in enumerate(items):
            card = MetricCard(title)
            card.set_value(val, sub=sub, color=color)
            self._grid.addWidget(card, i // self._cols, i % self._cols)
            self._cards.append(card)


class StepBanner(QWidget):
    def __init__(self, step_id: str, title: str, blurb: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        head = QLabel(f"<b>Step {step_id}</b> — {title}")
        head.setStyleSheet("color: #7aa2f7; font-size: 14px;")
        head.setTextFormat(Qt.TextFormat.RichText)
        body = QLabel(blurb)
        body.setWordWrap(True)
        body.setStyleSheet("color: #a9b1d6; font-size: 12px;")
        lay.addWidget(head)
        lay.addWidget(body)


class GateStrip(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label = QLabel("Gate: not evaluated")
        self._label.setWordWrap(True)
        self._label.setStyleSheet(
            "padding: 8px; background: #1f2335; border-radius: 4px; color: #a9b1d6;"
        )
        lay = QVBoxLayout(self)
        lay.addWidget(self._label)

    def set_gate(self, text: str, *, ok: bool | None = None) -> None:
        if ok is True:
            bg, fg = "#1a3d2e", "#9ece6a"
        elif ok is False:
            bg, fg = "#3d1a1a", "#f7768e"
        else:
            bg, fg = "#1f2335", "#a9b1d6"
        self._label.setStyleSheet(
            f"padding: 8px; background: {bg}; border-radius: 4px; color: {fg};"
        )
        self._label.setText(text)


class LogPane(QTextEdit):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(120)
        self.setStyleSheet("font-family: monospace; font-size: 11px; background: #16161e; color: #a9b1d6;")

    def append_line(self, line: str) -> None:
        self.append(line)


class StepToolBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from PySide6.QtWidgets import QPushButton

        lay = QHBoxLayout(self)
        self.btn_run = QPushButton("Run this step")
        self.btn_run.setStyleSheet("font-weight: bold; padding: 6px 14px;")
        self.btn_refresh = QPushButton("Refresh from artifacts")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        lay.addWidget(self.btn_run)
        lay.addWidget(self.btn_refresh)
        lay.addStretch(1)
        lay.addWidget(self.progress)
