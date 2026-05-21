#!/usr/bin/env python3
"""Launch the Orbitron Proof Suite GUI."""
from __future__ import annotations

import os
import sys


def main() -> int:
    os.environ.setdefault("ORBITRON_PROOF_CHAIN", "1")
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "figure.facecolor": "#1a1b26",
            "axes.facecolor": "#24283b",
            "axes.edgecolor": "#414868",
            "axes.labelcolor": "#c0caf5",
            "text.color": "#c0caf5",
            "xtick.color": "#a9b1d6",
            "ytick.color": "#a9b1d6",
        }
    )
    from PySide6.QtWidgets import QApplication

    from ssto.orbitron.simulator.proof_suite.main_window import ProofSuiteMainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("OrbitronProofSuite")
    app.setStyle("Fusion")
    win = ProofSuiteMainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
