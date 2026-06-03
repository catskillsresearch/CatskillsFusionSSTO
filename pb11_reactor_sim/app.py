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
from pb11_reactor_sim.engine.shot_sequence import ShotPhase
from pb11_reactor_sim.engine.optimizer import OptimizeResult, optimize_qnet
from pb11_reactor_sim.engine.pic_backend import FieldSolveBackend, make_backend
from pb11_reactor_sim.gui.canvas import ReactorCanvas
from pb11_reactor_sim.gui.controls import ControlPanel
from pb11_reactor_sim.gui.diagnostics import DiagnosticsPanel
from pb11_reactor_sim.reactors import REACTOR_REGISTRY

#: Physics substeps advanced per GUI frame.
_SUBSTEPS_PER_FRAME = 4
#: GUI refresh interval [ms].
_FRAME_INTERVAL_MS = 33


class _OptimizeWorker(QtCore.QObject):
    """Runs the Q_net control-space search off the GUI thread."""

    finished = QtCore.Signal(object)  # OptimizeResult
    failed = QtCore.Signal(str)

    def __init__(self, reactor_cls: type[ReactorSimulation], backend: FieldSolveBackend) -> None:
        super().__init__()
        self._reactor_cls = reactor_cls
        self._backend = backend

    @QtCore.Slot()
    def run(self) -> None:
        try:
            result = optimize_qnet(self._reactor_cls, self._backend)
            self.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(f"{type(exc).__name__}: {exc}")


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
        self._auto_paused_after_shot = False

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
        self.controls.armRequested.connect(self._on_arm)
        self.controls.fireRequested.connect(self._on_fire)
        self.controls.optimizeRequested.connect(self._on_optimize)

        # Optimizer worker thread handles (kept alive while running).
        self._opt_thread: QtCore.QThread | None = None
        self._opt_worker: _OptimizeWorker | None = None

        # --- simulation timer ---
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(_FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._on_tick)

        # Boot the first reactor.
        self._on_reactor_changed(self.controls.reactor_combo.currentText())

    def _reactor_needs_geometry_refresh(self) -> bool:
        """True when control changes rebuild masks (HB11/LPP), not just fields (TAE)."""
        from pb11_reactor_sim.reactors.hb11 import HB11Reactor
        from pb11_reactor_sim.reactors.lpp import LPPReactor

        return isinstance(self._reactor, (HB11Reactor, LPPReactor))

    # -- reactor management -------------------------------------------------
    def _on_reactor_changed(self, name: str) -> None:
        cls = REACTOR_REGISTRY[name]
        self.controls.rebuild_sliders(cls.control_specs())
        self._reactor = cls(field_solver=self.backend)
        self._reactor.apply_controls(self.controls.current_values())
        self.diagnostics.clear()
        self.canvas.attach(self._reactor, self.backend.label)
        self._sync_shot_ui()
        self._update_readout()

    def _on_arm(self) -> None:
        if self._reactor is None:
            return
        self._on_play_toggled(False)
        self.controls.set_playing(False)
        self._reactor.apply_controls(self.controls.current_values())
        self._reactor.arm_shot()
        if self._reactor_needs_geometry_refresh():
            self.canvas.attach(self._reactor, self.backend.label)
        else:
            self.canvas.refresh()
        self.diagnostics.clear()
        self._sync_shot_ui()
        self._update_readout()
        self.statusBar().showMessage(self._reactor.shot_callout)

    def _on_fire(self) -> None:
        if self._reactor is None or not self._reactor.fire_shot():
            return
        self._auto_paused_after_shot = False
        self.controls.set_playing(True)
        self._on_play_toggled(True)
        self._sync_shot_ui()
        self.statusBar().showMessage(self._reactor.shot_callout)

    def _sync_shot_ui(self) -> None:
        r = self._reactor
        if r is None:
            return
        self.controls.set_shot_status(r.shot_phase.value, r.shot_callout, r.can_fire())

    def _on_controls_changed(self, values: dict) -> None:
        if self._reactor is None:
            return
        self._reactor.apply_controls(values)
        # HB11/LPP rebuild conductor masks when controls change; TAE only updates B_z.
        if self._reactor_needs_geometry_refresh():
            self.canvas.attach(self._reactor, self.backend.label)
        else:
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
        self._on_play_toggled(False)
        self.controls.set_playing(False)

        defaults = {s.key: s.default for s in type(self._reactor).control_specs()}
        self.controls.set_values(defaults)
        self._reactor.apply_controls(self.controls.current_values())
        self._reactor.reset()
        self.canvas.attach(self._reactor, self.backend.label)
        self.diagnostics.clear()
        self._sync_shot_ui()
        self._update_readout()
        self.statusBar().showMessage("Reset — unarmed idle.")

    # -- optimizer ----------------------------------------------------------
    def _on_optimize(self) -> None:
        if self._reactor is None or self._opt_thread is not None:
            return
        reactor_cls = type(self._reactor)
        self.controls.set_optimizing(True)
        self.statusBar().showMessage(f"Optimizing Q_net over {reactor_cls.display_name} controls...")

        self._opt_thread = QtCore.QThread(self)
        self._opt_worker = _OptimizeWorker(reactor_cls, self.backend)
        self._opt_worker.moveToThread(self._opt_thread)
        self._opt_thread.started.connect(self._opt_worker.run)
        self._opt_worker.finished.connect(self._on_optimize_done)
        self._opt_worker.failed.connect(self._on_optimize_failed)
        self._opt_thread.start()

    def _teardown_opt_thread(self) -> None:
        if self._opt_thread is not None:
            self._opt_thread.quit()
            self._opt_thread.wait()
            self._opt_thread = None
            self._opt_worker = None
        self.controls.set_optimizing(False)

    @QtCore.Slot(object)
    def _on_optimize_done(self, result: OptimizeResult) -> None:
        self._teardown_opt_thread()
        # Apply the optimum to the sliders (which propagates to the live reactor).
        self.controls.set_values(result.controls)
        pretty = ", ".join(f"{k}={v:.3g}" for k, v in result.controls.items())
        self.statusBar().showMessage(
            f"Optimal Q_net = {result.q_net:.3e}  at  {pretty}   "
            f"({result.n_evaluations} evaluations)  |  Engine: {self.backend.label}"
        )

    @QtCore.Slot(str)
    def _on_optimize_failed(self, message: str) -> None:
        self._teardown_opt_thread()
        self.statusBar().showMessage(f"Optimization failed: {message}")

    # -- main loop ----------------------------------------------------------
    def _on_tick(self) -> None:
        if self._reactor is None:
            return
        prev_phase = self._reactor.shot_phase
        for _ in range(_SUBSTEPS_PER_FRAME):
            self._reactor.step()
        self.canvas.refresh()
        self.diagnostics.update_from(self._reactor.diagnostics)
        if prev_phase == ShotPhase.FIRING and self._reactor.shot_phase == ShotPhase.QUIESCENT:
            self._on_play_toggled(False)
            self.controls.set_playing(False)
            self._auto_paused_after_shot = True
            self.statusBar().showMessage(self._reactor.shot_callout)
        self._sync_shot_ui()
        self._frame += 1
        if self._frame % 3 == 0:
            self._update_readout()

    def _update_readout(self) -> None:
        r = self._reactor
        if r is None:
            return
        lines = [
            f"Ops      = {r.shot_phase.value}",
            f"Status   = {r.shot_callout}",
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
