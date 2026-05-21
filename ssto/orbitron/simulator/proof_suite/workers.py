"""Background workers for long proof-chain steps."""
from __future__ import annotations

from PySide6.QtCore import QThread, Signal


class StepWorker(QThread):
    finished = Signal(object, object)  # result dict | None, error str | None

    def __init__(self, fn, *args, **kwargs) -> None:
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            out = self._fn(*self._args, **self._kwargs)
            self.finished.emit(out, None)
        except Exception as exc:
            self.finished.emit(None, str(exc))
