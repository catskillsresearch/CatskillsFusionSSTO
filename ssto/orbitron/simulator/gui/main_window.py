"""Main window: inputs, run 0D / WarpX, solve for 3.5 MW, plots."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import time

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.physics_spec import load_plant_scales
from ssto.orbitron.simulator.solve import (
    solve_for_target_power,
    solve_unobtanium_requirements,
    sweep_geometry_radius,
)
from ssto.orbitron.simulator.export_validation import export_validation_yaml
from ssto.orbitron.simulator.validation import validate_design, validate_startup_step
from ssto.orbitron.simulator.gui.validation_panel import ValidationPanel
from ssto.orbitron.simulator.types import (
    DeviceGeometry,
    OperatingPoint,
    PlantScales,
    SimulatorInputs,
    SteadyStateResult,
    UnobtaniumParams,
)
from ssto.orbitron.simulator.viz import (
    power_sweep_figure,
    render_device_cross_section,
    results_bar_figure,
)
from ssto.orbitron.simulator.gui.startup_panel import StartupPanel
from ssto.orbitron.simulator.gui.timelapse_panel import TimelapsePanel
from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.pic_session import PicSession
from ssto.orbitron.simulator.plasma_overlay import PlasmaViewState
from ssto.orbitron.simulator.longitudinal.focus import (
    LongitudinalFocus,
    focus_domain,
    resolve_longitudinal_focus,
)
from ssto.orbitron.simulator.warpx_backend import inputs_with_pic_proxy, repo_root


def _spin(
    lo: float,
    hi: float,
    val: float,
    decimals: int = 4,
    step: float = 0.01,
    suffix: str = "",
) -> QDoubleSpinBox:
    s = QDoubleSpinBox()
    s.setRange(lo, hi)
    s.setDecimals(decimals)
    s.setSingleStep(step)
    s.setValue(val)
    if suffix:
        s.setSuffix(suffix)
    return s


class WarpXWorker(QThread):
    finished = Signal(object, object)  # SimulatorInputs, log dict

    def __init__(self, inputs: SimulatorInputs, work_dir: Path) -> None:
        super().__init__()
        self._inputs = inputs
        self._work_dir = work_dir

    def run(self) -> None:
        updated, log = inputs_with_pic_proxy(self._inputs, self._work_dir, n_steps=150)
        self.finished.emit(updated, log)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("p-¹¹B Orbitron — design validation simulator")
        self.resize(1280, 820)

        self._inputs = SimulatorInputs(scales=load_plant_scales())
        self._last_pic_log: dict = {}
        self._last_steady: SteadyStateResult | None = None
        self._plasma_t0 = time.monotonic()
        self._pic_session = PicSession()
        self._live_timer = QTimer(self)
        self._live_timer.setInterval(500)
        self._live_timer.timeout.connect(self._on_live_tick)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # --- Left: inputs ---
        left = QScrollArea()
        left.setWidgetResizable(True)
        left_w = QWidget()
        left.setWidget(left_w)
        left_layout = QVBoxLayout(left_w)

        tabs = QTabWidget()
        left_layout.addWidget(tabs)

        self.startup = StartupPanel(self._on_pad_changed)
        tabs.addTab(self.startup, "Pad startup")

        geo_box = QGroupBox("Device geometry")
        geo_form = QFormLayout(geo_box)
        self.r_anode = _spin(0.02, 0.15, 0.05, 4, 0.001, " m")
        self.r_cathode = _spin(0.001, 0.02, 0.005, 4, 0.0005, " m")
        self.length = _spin(0.5, 5.0, 2.0, 2, 0.1, " m")
        self.v_cathode = _spin(-900.0, -100.0, -600.0, 0, 10.0, " kV")
        self.b_field = _spin(0.5, 5.0, 2.0, 2, 0.1, " T")
        geo_form.addRow("Anode radius", self.r_anode)
        geo_form.addRow("Cathode radius", self.r_cathode)
        geo_form.addRow("Length", self.length)
        geo_form.addRow("Cathode potential", self.v_cathode)
        geo_form.addRow("Axial B", self.b_field)
        tabs.addTab(geo_box, "Geometry")

        op_box = QGroupBox("Injectants (NBI fuel)")
        op_form = QFormLayout(op_box)
        self.h2_sccm = _spin(0.0, 200.0, 80.0, 1, 5.0, " sccm")
        self.laser_hz = _spin(0.0, 50.0, 10.0, 1, 1.0, " Hz")
        op_form.addRow("H₂ flow (proton)", self.h2_sccm)
        op_form.addRow("¹¹B laser pulse rate", self.laser_hz)
        op_form.addRow(
            QLabel("Beam / compressor / pulse levers are on the Pad startup tab (same as FlightGear).")
        )
        tabs.addTab(op_box, "Injectants")
        self.h2_sccm.valueChanged.connect(self._on_pad_changed)
        self.laser_hz.valueChanged.connect(self._on_pad_changed)

        u_box = QGroupBox("Unobtanium parameters")
        u_form = QFormLayout(u_box)
        self.u1_emission = _spin(0.1, 5.0, 1.0, 2, 0.1)
        self.u2_flux = _spin(1e5, 1e7, 2e6, 0, 1e5, " W/m²")
        self.u2_ch4 = _spin(0.1, 2.0, 1.0, 2, 0.05)
        self.u3_hts = _spin(0.1, 3.0, 1.0, 2, 0.1)
        self.u4_fusion = _spin(0.1, 5.0, 1.0, 2, 0.1)
        self.u4_beam = _spin(0.1, 5.0, 1.0, 2, 0.1)
        u_form.addRow("U1 field-emission margin", self.u1_emission)
        u_form.addRow("U2 max wall heat flux", self.u2_flux)
        u_form.addRow("U2 CH₄ cooling factor", self.u2_ch4)
        u_form.addRow("U3 HTS capability scale", self.u3_hts)
        u_form.addRow("U4 fusion reactivity scale", self.u4_fusion)
        u_form.addRow("U4 beam coupling scale", self.u4_beam)
        tabs.addTab(u_box, "Unobtanium")

        plant_box = QGroupBox("Plant / target")
        plant_form = QFormLayout(plant_box)
        self.target_mw = _spin(0.5, 10.0, 3.5, 2, 0.1, " MW")
        self.eta_jet = _spin(0.1, 0.9, 0.55, 2, 0.05)
        plant_form.addRow("Target gross power", self.target_mw)
        plant_form.addRow("Jet η", self.eta_jet)
        tabs.addTab(plant_box, "Plant")

        btn_row = QHBoxLayout()
        self.btn_run = QPushButton("Run 0D steady state")
        self.btn_solve = QPushButton("Solve unobtanium → target MW")
        self.btn_sweep_r = QPushButton("Sweep r_anode → solve")
        self.btn_warpx = QPushButton("Run WarpX PIC (slow)")
        self.chk_use_pic = QCheckBox("Use last PIC proxies in 0D")
        btn_row.addWidget(self.btn_run)
        btn_row.addWidget(self.btn_solve)
        btn_row.addWidget(self.btn_sweep_r)
        btn_row.addWidget(self.btn_warpx)
        left_layout.addLayout(btn_row)
        left_layout.addWidget(self.chk_use_pic)
        left_layout.addStretch()

        splitter.addWidget(left)

        # --- Right: plots + log ---
        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(140)
        right_layout.addWidget(QLabel("Log / constraints"))
        right_layout.addWidget(self.log)

        plot_tabs = QTabWidget()
        self.validation_panel = ValidationPanel(self._run_validation, self._export_validation_yaml)
        plot_tabs.addTab(self.validation_panel, "Validation")
        self.canvas_device = FigureCanvasQTAgg(Figure(figsize=(9, 4.2)))
        self.canvas_results = FigureCanvasQTAgg(Figure(figsize=(5, 3)))
        self.canvas_sweep = FigureCanvasQTAgg(Figure(figsize=(5, 3)))
        plot_tabs.addTab(self._build_device_tab(), "Device")
        plot_tabs.addTab(self._wrap_canvas(self.canvas_results), "Outputs")
        plot_tabs.addTab(self._wrap_canvas(self.canvas_sweep), "Sweep")
        self.timelapse = TimelapsePanel(
            self._gather_inputs,
            get_pic_session=lambda: self._pic_session,
            get_plasma_phase=lambda: self._plasma_view().phase,
        )
        plot_tabs.addTab(self.timelapse, "Longitudinal 2D")
        right_layout.addWidget(plot_tabs, stretch=1)
        splitter.addWidget(right)
        splitter.setSizes([420, 860])

        self.btn_run.clicked.connect(self._on_run_0d)
        self.btn_solve.clicked.connect(self._on_solve)
        self.btn_sweep_r.clicked.connect(self._on_sweep_radius)
        self.btn_warpx.clicked.connect(self._on_warpx)
        self._on_pad_changed()
        self._on_run_0d()

    @staticmethod
    def _wrap_canvas(canvas: FigureCanvasQTAgg) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(canvas)
        return w

    def _build_device_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(4, 4, 4, 4)
        row = QHBoxLayout()
        self.device_focus_combo = QComboBox()
        for label, foc in (
            ("1 — Core tube (anode + cathode)", LongitudinalFocus.CORE_TUBE),
            ("2 — Core + magnet bore", LongitudinalFocus.CORE_PLUS_MAGNET),
            ("3 — Full engine (intake → nozzle)", LongitudinalFocus.FULL_DUCT_AIR),
        ):
            self.device_focus_combo.addItem(label, foc)
        self.device_focus_combo.setCurrentIndex(2)
        row.addWidget(QLabel("Layout zoom:"))
        row.addWidget(self.device_focus_combo, stretch=1)
        lay.addLayout(row)
        lay.addWidget(self.canvas_device, stretch=1)
        self.device_focus_combo.currentIndexChanged.connect(self._redraw_device)
        for spin in (
            self.r_anode,
            self.r_cathode,
            self.length,
            self.v_cathode,
            self.b_field,
        ):
            spin.valueChanged.connect(self._redraw_device)
        return w

    def _device_focus(self) -> LongitudinalFocus:
        return resolve_longitudinal_focus(
            self.device_focus_combo.currentData(),
            self.device_focus_combo.currentIndex(),
        )

    def _gather_inputs(self) -> SimulatorInputs:
        base = self._inputs
        geo = DeviceGeometry(
            r_anode_m=self.r_anode.value(),
            r_cathode_m=self.r_cathode.value(),
            length_m=self.length.value(),
            V_cathode_v=self.v_cathode.value() * 1000.0,
            B_axial_tesla=self.b_field.value(),
        )
        op = OperatingPoint(
            h2_sccm=self.h2_sccm.value(),
            laser_ablation_hz=self.laser_hz.value(),
        )
        pad = self.startup.pad_state()
        if hasattr(self, "timelapse"):
            pad = replace(pad, laminar_relaminarization=self.timelapse.chk_laminar.isChecked())
        u = UnobtaniumParams(
            field_emission_margin=self.u1_emission.value(),
            max_wall_heat_flux_W_m2=self.u2_flux.value(),
            ch4_cooling_effectiveness=self.u2_ch4.value(),
            hts_capability_scale=self.u3_hts.value(),
            fusion_reactivity_scale=self.u4_fusion.value(),
            beam_coupling_scale=self.u4_beam.value(),
        )
        scales = replace(
            base.scales,
            target_gross_power_mw=self.target_mw.value(),
            jet_propulsive_efficiency=self.eta_jet.value(),
        )
        inp = SimulatorInputs(geometry=geo, operating=op, pad=pad, unobtanium=u, scales=scales)
        if self.chk_use_pic.isChecked() and self._last_pic_log.get("ok"):
            inp = replace(
                inp,
                pic_rho_e_norm=float(self._last_pic_log.get("rho_e_norm", float("nan"))),
                pic_beam_rho_norm=float(self._last_pic_log.get("rho_beam_norm", float("nan"))),
            )
        run = getattr(self.timelapse, "_run", None)
        if run is not None and run.meta.get("model") == "fusion_channel_sr":
            p_fc = float(run.meta.get("integrated_fusion_power_mw", 0.0) or 0.0)
            if p_fc > 0:
                inp = replace(inp, fusion_channel_power_mw=p_fc)
        return inp

    def _log_result(self, res: object) -> None:
        from ssto.orbitron.simulator.types import SteadyStateResult

        assert isinstance(res, SteadyStateResult)
        lines = [
            f"P_gross = {res.gross_power_mw:.3f} MW",
            f"P_jet   = {res.jet_kinetic_power_mw:.3f} MW",
            f"Q_wall  = {res.wall_heat_kw:.1f} kW  (flux {res.wall_heat_flux_W_m2:.2e} W/m²)",
            f"I_beam  = {res.beam_current_ma:.2f} mA  ({res.beam_power_kw:.2f} kW)",
            f"log10 n = {res.log10_density:.2f}  ({res.plasma_density_cm3:.2e} cm⁻³)",
            f"Thrust  = {res.thrust_lbf:.0f} lbf  |  ṁ = {res.mass_flow_kgps:.2f} kg/s",
            f"v_e     = {res.equiv_exhaust_velocity_mps:.1f} m/s",
            f"E_cath  = {res.cathode_surface_field_V_m:.2e} V/m",
            f"Feasible: {res.feasible}",
        ]
        for v in res.violations:
            lines.append(f"  ✗ {v}")
        self.log.setPlainText("\n".join(lines))

    def _plasma_view(self) -> PlasmaViewState:
        t = time.monotonic() - self._plasma_t0
        return PlasmaViewState(time_s=t, phase=(t * 0.35) % 1.0)

    def _run_validation(self):
        inp = self._gather_inputs()
        res = self._last_steady or evaluate_steady_state(inp)
        self._last_steady = res
        vrep = validate_design(inp, res)
        step_lines = [f"  {c.spec_id}: {c.achieved} ({c.status.value})" for c in validate_startup_step(inp, res)]
        self.log.setPlainText(vrep.to_text() + "\n\nStartup steps:\n" + "\n".join(step_lines))
        return vrep

    def _export_validation_yaml(self, path: Path) -> Path:
        inp = self._gather_inputs()
        res = self._last_steady or evaluate_steady_state(inp)
        vrep = validate_design(inp, res)
        return export_validation_yaml(
            path,
            inp,
            res,
            vrep,
            title="Catskills p-¹¹B Orbitron — design validation",
        )

    def _on_pad_changed(self) -> None:
        inp = self._gather_inputs()
        self._last_steady = evaluate_steady_state(inp)
        self._log_result(self._last_steady)
        vrep = validate_design(inp, self._last_steady)
        self.validation_panel.show_report(vrep)
        self._redraw_device()
        self.timelapse.notify_pad_changed()
        if inp.pad.live_simulation and inp.pad.bleed_air_open:
            self._live_timer.start()
            self.timelapse._update_auto_play()
        else:
            self._live_timer.stop()
            self.timelapse._update_auto_play()

    def _on_live_tick(self) -> None:
        inp = self._gather_inputs()
        if not inp.pad.live_simulation:
            self._live_timer.stop()
            return
        if self._pic_session.available:
            self._pic_session.set_phase(self._plasma_view().phase)
        self._last_steady = evaluate_steady_state(inp)
        self._redraw_device()
        self.timelapse.on_live_tick()

    def _redraw_device(self) -> None:
        inp = self._gather_inputs()
        pad_status = evaluate_pad_status(inp.pad)
        fig = self.canvas_device.figure
        fig.clear()
        ax = fig.add_subplot(111)
        render_device_cross_section(
            ax,
            inp.geometry,
            self._device_focus(),
            pad_status=pad_status,
            steady_result=self._last_steady,
            plasma_view=self._plasma_view(),
            pic_rho_norm=inp.pic_rho_e_norm,
            pic_session=self._pic_session,
        )
        fig.tight_layout()
        self.canvas_device.draw()

    def _redraw_results(self, res: object) -> None:
        from ssto.orbitron.simulator.types import SteadyStateResult

        assert isinstance(res, SteadyStateResult)
        fig = results_bar_figure(res)
        self.canvas_results.figure = fig
        self.canvas_results.draw()

    def _redraw_sweep(self) -> None:
        fig = power_sweep_figure(self._gather_inputs())
        self.canvas_sweep.figure = fig
        self.canvas_sweep.draw()

    def _on_run_0d(self) -> None:
        self._inputs = self._gather_inputs()
        res = evaluate_steady_state(self._inputs)
        self._last_steady = res
        self._log_result(res)
        self._redraw_device()
        self._redraw_results(res)
        self._redraw_sweep()

    def _on_solve(self) -> None:
        self._inputs = self._gather_inputs()
        report = solve_unobtanium_requirements(self._inputs, self.target_mw.value())
        self._inputs = report.inputs
        u = report.inputs.unobtanium
        self.startup.set_run_levers(report.inputs.pad.throttle, report.inputs.pad.compressor)
        self.u1_emission.setValue(u.field_emission_margin)
        self.u2_flux.setValue(u.max_wall_heat_flux_W_m2)
        self.u2_ch4.setValue(u.ch4_cooling_effectiveness)
        self.u3_hts.setValue(u.hts_capability_scale)
        self.u4_fusion.setValue(u.fusion_reactivity_scale)
        self.u4_beam.setValue(u.beam_coupling_scale)
        self._last_steady = report.result
        self._log_result(report.result)
        if report.validation:
            self.validation_panel.show_report(report.validation)
        self.log.append(
            f"\n--- Unobtanium solve ---\n{report.message}\nresidual = {report.residual_mw:+.3f} MW"
        )
        self._redraw_device()
        self._redraw_results(report.result)
        self._redraw_sweep()
        if not report.success:
            QMessageBox.warning(
                self,
                "Solve",
                f"Could not validate design at {self.target_mw.value():.2f} MW.\n"
                f"Residual {report.residual_mw:+.3f} MW — see Validation tab.",
            )

    def _on_sweep_radius(self) -> None:
        self._inputs = self._gather_inputs()
        r = self.r_anode.value()
        report = sweep_geometry_radius(self._inputs, r, self.target_mw.value())
        self._inputs = report.inputs
        self.startup.set_run_levers(
            report.inputs.pad.throttle,
            report.inputs.pad.compressor,
        )
        self.u4_fusion.setValue(report.inputs.unobtanium.fusion_reactivity_scale)
        self._log_result(report.result)
        self.log.append(f"\n--- r_anode = {r:.4f} m sweep ---\nresidual {report.residual_mw:+.3f} MW")

    def _on_warpx(self) -> None:
        self.btn_warpx.setEnabled(False)
        self.log.append("\nWarpX PIC started…")
        work = repo_root() / "build" / "simulator_pic"
        self._warpx_worker = WarpXWorker(self._gather_inputs(), work)
        self._warpx_worker.finished.connect(self._on_warpx_done)
        self._warpx_worker.start()

    def _on_warpx_done(self, inputs: object, log: object) -> None:
        self.btn_warpx.setEnabled(True)
        assert isinstance(log, dict)
        self._last_pic_log = log
        if not log.get("ok"):
            self.log.append(f"WarpX failed:\n{log.get('error', log)}")
            QMessageBox.critical(self, "WarpX", str(log.get("error", "unknown error")))
            return
        from ssto.orbitron.simulator.types import SimulatorInputs

        assert isinstance(inputs, SimulatorInputs)
        self._inputs = inputs
        self.chk_use_pic.setChecked(True)
        diags = repo_root() / "build" / "simulator_pic" / "diags"
        try:
            domain = focus_domain(LongitudinalFocus.CORE_TUBE, inputs)
            self._pic_session.load_from_diags(diags, domain)
            self.log.append(
                f"WarpX OK — rho_e_norm={log.get('rho_e_norm')} "
                f"beam_norm={log.get('rho_beam_norm')} "
                f"({self._pic_session.n_frames} PIC frames cached)"
            )
            self.timelapse.notify_pic_loaded()
        except Exception as exc:
            self.log.append(f"WarpX OK (reduction only); frame load failed: {exc}")
        self._on_run_0d()
        self._redraw_device()
