#!/usr/bin/env python3
"""Launch the Orbitron Sprint 2 simulator GUI."""
from __future__ import annotations

import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from ssto.orbitron.simulator.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("OrbitronSimulator")
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
