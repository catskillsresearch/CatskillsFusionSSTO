"""
Main application window.

:class:`PlasmaSimApp` assembles the control panel, the 2D spatial canvas, and
the 1D diagnostic panel into a single dashboard, owns the active
:class:`~pb11_reactor_sim.engine.base.ReactorSimulation`, and drives the
simulation loop with a :class:`QtCore.QTimer`. Multiple physics substeps are run
per GUI frame so the visualization stays smooth while the simulation advances at
its native (sub-nanosecond) timestep.
"""
from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from pb11_reactor_sim.engine.base import ReactorSimulation
from pb11_reactor_sim.engine.pic_backend import make_backend
from pb11_reactor_sim.gui.canvas import ReactorCanvas
from pb11_reactor_sim.gui.controls import ControlPanel
from pb11_reactor_sim.gui.diagnostics import DiagnosticsPanel
from pb11_reactor_sim.reactors import REACTOR_REGISTRY

#: Physics substeps advanced per GUI frame.
_SUBSTEPS_PER_FRAME = 4
#: GUI refresh interval [ms].
_FRAME_INTERVAL_MS = 33


class PlasmaSimApp(QtWidgets.QMainWindow):
    """Top-level dashboard window for the p-11B reactor simulator."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("p-11B Reactor Core Simulator -- TAE FRC / HB11 Laser / LPP DPF")
        self.resize(1500, 900)

        # One shared field-solve backend (WarpX if opted-in and available).
        self.backend = make_backend()

        self._reactor: ReactorSimulation | None = None
        self._playing = False
        self._frame = 0

        # --- widgets ---
        self.controls = ControlPanel(list(REACTOR_REGISTRY.keys()))
        self.canvas = ReactorCanvas()
        self.diagnostics = DiagnosticsPanel()

        # --- layout: controls | canvas | diagnostics ---
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.addWidget(self.controls)
        splitter.addWidget(self.canvas)
        splitter.addWidget(self.diagnostics)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([320, 880, 380])
        self.setCentralWidget(splitter)

        self.statusBar().showMessage(f"Field-solve engine: {self.backend.label}")

        # --- signals ---
        self.controls.reactorChanged.connect(self._on_reactor_changed)
        self.controls.controlsChanged.connect(self._on_controls_changed)
        self.controls.playToggled.connect(self._on_play_toggled)
        self.controls.resetRequested.connect(self._on_reset)

        # --- simulation timer ---
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(_FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._on_tick)

        # Boot the first reactor.
        self._on_reactor_changed(self.controls.reactor_combo.currentText())

    # -- reactor management -------------------------------------------------
    def _on_reactor_changed(self, name: str) -> None:
        cls = REACTOR_REGISTRY[name]
        self.controls.rebuild_sliders(cls.control_specs())
        self._reactor = cls(field_solver=self.backend)
        self._reactor.apply_controls(self.controls.current_values())
        self.canvas.attach(self._reactor, self.backend.label)
        self.diagnostics.update_from(self._reactor.diagnostics)
        self.canvas.refresh()
        self._update_readout()

    def _on_controls_changed(self, values: dict) -> None:
        if self._reactor is not None:
            self._reactor.apply_controls(values)
            # Geometry may have changed (HB11/LPP rebuild on control change).
            self.canvas.attach(self._reactor, self.backend.label)
            self.canvas.refresh()

    def _on_play_toggled(self, playing: bool) -> None:
        self._playing = playing
        if playing:
            self._timer.start()
        else:
            self._timer.stop()

    def _on_reset(self) -> None:
        if self._reactor is None:
            return
        self._reactor.reset()
        self._reactor.apply_controls(self.controls.current_values())
        self.canvas.attach(self._reactor, self.backend.label)
        self.diagnostics.update_from(self._reactor.diagnostics)
        self.canvas.refresh()
        self._update_readout()

    # -- main loop ----------------------------------------------------------
    def _on_tick(self) -> None:
        if self._reactor is None:
            return
        for _ in range(_SUBSTEPS_PER_FRAME):
            self._reactor.step()
        self.canvas.refresh()
        self.diagnostics.update_from(self._reactor.diagnostics)
        self._frame += 1
        if self._frame % 3 == 0:
            self._update_readout()

    def _update_readout(self) -> None:
        r = self._reactor
        if r is None:
            return
        lines = [
            f"t        = {r.time * 1e6:10.4f} us",
            f"step     = {r.step_index}",
            f"T_i      = {r.T_i_keV:10.2f} keV",
            f"T_e      = {r.T_e_keV:10.2f} keV",
            f"n_e      = {r.n_e:10.3e} m^-3",
            f"P_fusion = {r.last_p_fusion:10.3e} W/m^3",
            f"P_Brems  = {r.last_p_brems:10.3e} W/m^3",
            f"P_cond   = {r.last_p_cond:10.3e} W/m^3",
            f"Q_net    = {r.last_q_net:10.3e}",
        ]
        lines += self._reactor_specific_readout(r)
        self.controls.update_readout("\n".join(lines))

    @staticmethod
    def _reactor_specific_readout(r: ReactorSimulation) -> list[str]:
        out: list[str] = []
        icc = getattr(r, "icc_signal", None)
        if icc is not None:
            out.append(f"ICC sig  = {icc:10.3e} a.u.")
        coll = getattr(r, "collected_charge", None)
        if coll is not None:
            out.append(f"Collected= {coll:10.3e} C")
        cur = getattr(r, "current", None)
        if cur is not None:
            out.append(f"I(t)     = {cur:10.3e} A")
        bp = getattr(r, "b_pinch", None)
        if bp is not None:
            out.append(f"B_pinch  = {bp:10.3e} T")
        return out


def main() -> int:
    """Application entry point."""
    import sys

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = PlasmaSimApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
