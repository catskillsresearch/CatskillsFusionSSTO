"""Proof suite steps 06–09: plant, closure, export, inverse solve."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ssto.orbitron.simulator.proof_chain.runners import run_step_06, run_step_07, run_step_08, run_step_09
from ssto.orbitron.simulator.proof_suite.steps.base import ProofStepPanel
from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.widgets import MetricGrid, MplCanvas
from ssto.orbitron.simulator.proof_suite.workers import StepWorker
class Step06PlantPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "06",
            "0D plant & U1–U4",
            "Steady-state plant at proof settings: E_cath (U1), wall/CH₄ (U2), HTS (U3), beam (U4), "
            "log₁₀ n. Phase 2 jacket heat is booked; fusion does not shove air into the plasma bore.",
            "Record violations at reactivity_scale=1 — defines unobtanium margins, not pass/fail theater.",
            state,
            parent,
        )
        self.canvas_bars = MplCanvas(6, 3.5)
        self.canvas_u = MplCanvas(6, 3.2)
        split = QSplitter()
        split.addWidget(self.canvas_bars)
        split.addWidget(self.canvas_u)
        self._layout.addWidget(split, stretch=1)
        self.violations = QTextEdit()
        self.violations.setReadOnly(True)
        self.violations.setMaximumHeight(100)
        self._layout.addWidget(QLabel("Violations / notes"))
        self._layout.addWidget(self.violations)
        self.metrics = MetricGrid(4)
        self._layout.addWidget(self.metrics)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _run(self) -> None:
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_06)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        data = self._state.try_load_step("06")
        if not data:
            self.gate.set_gate(self._gate_hint, ok=None)
            return
        s = data["steady_state"]
        figb = self.canvas_bars.figure
        figb.clear()
        axb = figb.add_subplot(111)
        labels = ["P_gross", "P_jet", "Q_wall", "I_beam", "Thrust", "ṁ"]
        values = [
            s["gross_power_mw"],
            s["jet_kinetic_power_mw"],
            s["wall_heat_kw"] / 1000,
            s["beam_current_ma"],
            s["thrust_lbf"] * 0.00444822,
            s["mass_flow_kgps"],
        ]
        axb.bar(labels, values, color="#7aa2f7", alpha=0.85)
        axb.set_title("Steady-state outputs", color="#c0caf5")
        axb.grid(True, axis="y", alpha=0.25)
        figb.tight_layout()
        self.canvas_bars.draw()

        figu = self.canvas_u.figure
        figu.clear()
        axu = figu.add_subplot(111)
        checks = [
            ("U1 E_cath", s["cathode_surface_field_V_m"] / 3e9, "max", 1.0),
            ("U2 q_wall", s["wall_heat_flux_W_m2"] / 2e6, "max", 1.0),
            ("U3 cryo", s["hts_cryo_kw"] / 0.5, "max", 1.0),
            ("U4 beam", float(s["beam_current_ma"]) / 1.0, "min", 1.0),
            ("U4 log₁₀ n", s["log10_density"] / 11.0, "min", 1.0),
        ]
        names = [c[0] for c in checks]
        ratios = [min(c[1], 2.5) for c in checks]
        colors = []
        for _name, rv, kind, lim in checks:
            if kind == "min":
                colors.append("#9ece6a" if rv >= lim else "#f7768e")
            else:
                colors.append("#9ece6a" if rv <= lim else "#f7768e")
        axu.barh(names, ratios, color=colors)
        axu.axvline(1.0, color="#e0af68", ls="--")
        axu.set_xlabel("Ratio to limit / target")
        axu.set_title("U1–U4 stress (approximate)", color="#c0caf5")
        figu.tight_layout()
        self.canvas_u.draw()

        vlist = data.get("violations", [])
        self.violations.setPlainText("\n".join(vlist) if vlist else "(no violations)")
        feasible = data.get("feasible", False)
        self.metrics.set_metrics(
            [
                ("P_gross", f"{s['gross_power_mw']:.4g} MW", "", None),
                ("Q_wall", f"{s['wall_heat_kw']:.0f} kW", "", None),
                ("Feasible", str(feasible), "", "#9ece6a" if feasible else "#f7768e"),
                ("Violations", str(len(vlist)), "", None),
            ]
        )
        self.gate.set_gate(
            "Gate: plant evaluated — review violations before claiming validation."
            if not feasible
            else "Gate: 0D plant feasible at proof point.",
            ok=feasible,
        )


class Step07ClosurePanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "07",
            "Jet closure",
            "Check F² ≈ 2 η P ṁ and P_from_thrust ≈ P_jet — propulsive discipline without free power.",
            "closure_rel_error ≤ 12%.",
            state,
            parent,
        )
        self.canvas = MplCanvas(7, 4)
        self._layout.addWidget(self.canvas, stretch=1)
        self.metrics = MetricGrid(3)
        self._layout.addWidget(self.metrics)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _run(self) -> None:
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_07)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        data = self._state.try_load_step("07")
        fig = self.canvas.figure
        fig.clear()
        if not data:
            self.gate.set_gate(self._gate_hint, ok=None)
            fig.tight_layout()
            self.canvas.draw()
            return
        ax = fig.add_subplot(111)
        p_jet = data["jet_kinetic_power_mw"] * 1e6
        mdot = data["mass_flow_kgps"]
        thrust_lbf = data["thrust_lbf"]
        thrust_n = thrust_lbf * 4.4482216152605
        p_thrust = (thrust_n**2) / (2 * mdot) if mdot > 1e-9 else 0
        labels = ["P_jet", "P from F²/2ṁ"]
        vals = [p_jet / 1e6, p_thrust / 1e6]
        ax.bar(labels, vals, color=["#7aa2f7", "#9ece6a"])
        ax.set_ylabel("MW equivalent")
        ax.set_title("Jet power closure", color="#c0caf5")
        rel = data["closure_rel_error"]
        ok = data.get("passes_12pct", rel <= 0.12)
        self.metrics.set_metrics(
            [
                ("Rel error", f"{rel:.2%}", "≤ 12%", "#9ece6a" if ok else "#f7768e"),
                ("F² error", f"{data.get('f2_rel_error', 0):.2%}", "", None),
                ("ṁ", f"{mdot:.2f} kg/s", "", "#a9b1d6"),
            ]
        )
        self.gate.set_gate("Gate: jet closure passes." if ok else "Gate: closure off — check η, thrust, mdot scales.", ok=ok)
        fig.tight_layout()
        self.canvas.draw()


class Step08ExportPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "08",
            "Validation export",
            "Full validate_design + YAML for UNOBTANIUM / test-stand specs. "
            "design_validated may be false in proof mode — that is data, not a broken pipeline.",
            "Artifact written; review spec_checks table.",
            state,
            parent,
        )
        row = QHBoxLayout()
        self.btn_open = QPushButton("Open YAML…")
        self.btn_open_folder = QPushButton("Open chain folder")
        row.addWidget(self.btn_open)
        row.addWidget(self.btn_open_folder)
        row.addStretch()
        self._layout.addLayout(row)
        self.report = QTextEdit()
        self.report.setReadOnly(True)
        self.report.setMinimumHeight(280)
        self._layout.addWidget(self.report, stretch=1)
        self.metrics = MetricGrid(2)
        self._layout.addWidget(self.metrics)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.btn_open.clicked.connect(self._open_yaml)
        self.btn_open_folder.clicked.connect(self._open_folder)
        self.refresh_from_artifacts()

    def _run(self) -> None:
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_08)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def _open_yaml(self) -> None:
        p = Path(self._state.config["chain_root"]) / "08_export" / "design_validation.yaml"
        if p.is_file():
            import webbrowser

            webbrowser.open(p.as_uri())

    def _open_folder(self) -> None:
        import subprocess

        subprocess.run(["xdg-open", str(Path(self._state.config["chain_root"]))], check=False)

    def refresh_from_artifacts(self) -> None:
        data = self._state.try_load_step("08")
        if not data:
            self.report.setPlainText("Run validation export to build the spec document.")
            self.gate.set_gate(self._gate_hint, ok=None)
            return
        lines = [data.get("summary", ""), "", "Spec checks:"]
        for c in data.get("spec_checks", []):
            lines.append(f"  {c['spec_id']}: {c['status']} — {c['achieved']} ({c['title']})")
        self.report.setPlainText("\n".join(lines))
        validated = data.get("design_validated", False)
        self.metrics.set_metrics(
            [
                ("Validated", str(validated), data.get("design_validation_yaml", ""), None),
                ("Checks", str(len(data.get("spec_checks", []))), "see above", None),
            ]
        )
        self.gate.set_gate(
            "Gate: forward chain complete — YAML ready for specs."
            if validated
            else "Gate: export done — design not fully validated in proof mode (expected). Use step 09 for gaps.",
            ok=validated,
        )


class Step09SolvePanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "09",
            "Inverse solve (gaps)",
            "After the forward chain, quantify minimum unobtanium knobs to hit 3.5 MW. "
            "This is NOT first-principles proof — it documents required component performance.",
            "Review unobtanium_required vs nominal = 1.",
            state,
            parent,
        )
        prereq = QWidget()
        prereq_lay = QVBoxLayout(prereq)
        self.lbl_prereq = QLabel()
        self.lbl_prereq.setWordWrap(True)
        self.lbl_prereq.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        prereq_lay.addWidget(self.lbl_prereq)
        self.place_inputs_above_run(prereq)

        self.canvas = MplCanvas(7, 4)
        self._layout.addWidget(self.canvas, stretch=1)
        self.knobs = QTextEdit()
        self.knobs.setReadOnly(True)
        self.knobs.setMaximumHeight(140)
        self._layout.addWidget(QLabel("Required unobtanium (inverse)"))
        self._layout.addWidget(self.knobs)
        self.metrics = MetricGrid(3)
        self._layout.addWidget(self.metrics)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _refresh_prereq(self) -> None:
        from tools.orbitron_proof_chain.chain_lib import step08_blocks_inverse

        s8 = self._state.try_load_step("08")
        allowed, msg = step08_blocks_inverse(s8)
        if allowed:
            self.lbl_prereq.setText(
                "Prerequisite: step 08 export complete with no FAIL spec checks. "
                "Inverse solve is optional gap documentation (not Tier-2 proof)."
            )
            self.lbl_prereq.setStyleSheet("color: #9ece6a; font-size: 11px;")
            self.toolbar.btn_run.setEnabled(True)
        else:
            self.lbl_prereq.setText(msg)
            self.lbl_prereq.setStyleSheet("color: #f7768e; font-size: 11px; font-weight: bold;")
            self.toolbar.btn_run.setEnabled(False)

    def _run(self) -> None:
        from tools.orbitron_proof_chain.chain_lib import step08_blocks_inverse

        allowed, msg = step08_blocks_inverse(self._state.try_load_step("08"))
        if not allowed:
            self.log.append_line(f"BLOCKED: {msg}")
            self.gate.set_gate(msg, ok=False)
            return
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_09)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        self._refresh_prereq()
        data = self._state.try_load_step("09")
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if not data:
            ax.text(0.5, 0.5, "Run inverse solve\n(optional)", ha="center", color="#565f89")
            self.gate.set_gate(self._gate_hint, ok=None)
            fig.tight_layout()
            self.canvas.draw()
            return
        u = data.get("unobtanium_required", {})
        names = list(u.keys())
        vals = [u[k] for k in names]
        colors = ["#9ece6a" if 0.9 <= v <= 1.1 else "#f7768e" for v in vals]
        ax.barh(names, vals, color=colors)
        ax.axvline(1.0, color="#e0af68", ls="--", label="nominal")
        ax.set_xlabel("Scale factor")
        ax.set_title("Unobtanium required vs nominal", color="#c0caf5")
        ax.legend(fontsize=8)
        lines = [f"{k}: {v:.4f}" for k, v in u.items()]
        lines.append(f"\nResidual MW: {data.get('residual_mw', 0):+.4f}")
        lines.append(f"Success: {data.get('success')}")
        self.knobs.setPlainText("\n".join(lines))
        self.metrics.set_metrics(
            [
                ("Success", str(data.get("success")), data.get("message", "")[:40], None),
                ("Residual", f"{data.get('residual_mw', 0):+.3f} MW", "", None),
                ("Fusion scale", f"{u.get('fusion_reactivity_scale', 1):.2f}", "×", "#e0af68"),
            ]
        )
        self.gate.set_gate(
            "Gate: inverse documented — required knobs are spec input, not proof of fusion.",
            ok=None,
        )
        fig.tight_layout()
        self.canvas.draw()
