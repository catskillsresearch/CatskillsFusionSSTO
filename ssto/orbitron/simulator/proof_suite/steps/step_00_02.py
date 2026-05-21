"""Proof suite steps 00–02: SSOT, PIC, reduce."""
from __future__ import annotations

import json
import os

import numpy as np
from matplotlib.patches import Circle
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ssto.orbitron.simulator.gui.startup_panel import StartupPanel
from ssto.orbitron.simulator.proof_suite.workers import WarpXWorker
from ssto.orbitron.simulator.types import PadStartupState

from ssto.orbitron.simulator.proof_chain.runners import (
    list_pic_plotfiles,
    load_pic_slice_2d_with_error,
    run_step_00,
    run_step_02,
)
from ssto.orbitron.simulator.proof_suite.steps.base import ProofStepPanel
from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.widgets import MetricGrid, MplCanvas
from ssto.orbitron.simulator.proof_suite.workers import StepWorker
from ssto.orbitron.simulator.types import DeviceGeometry
from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
from ssto.orbitron.simulator.viz import render_device_cross_section


def _spin(lo: float, hi: float, val: float, *, dec: int = 4, suf: str = "") -> QDoubleSpinBox:
    s = QDoubleSpinBox()
    s.setRange(lo, hi)
    s.setDecimals(dec)
    s.setValue(val)
    if suf:
        s.setSuffix(suf)
    return s


class Step00SpecPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "00",
            "Design SSOT",
            "Freeze geometry, injectants, and compile PICMI overrides from "
            "orbitron_physics_surrogate.yaml. This is the single source of truth for all later steps.",
            "picmi_overrides.json exists and matches your bore / 600 kV / 2 T intent.",
            state,
            parent,
        )
        self._state.ensure_initialized()
        cfg = self._state.config
        g = cfg["geometry"]
        inj = cfg["injectants"]

        form = QGroupBox("Geometry & fueling")
        fl = QFormLayout(form)
        self.r_anode = _spin(0.01, 0.2, g["r_anode_m"], suf=" m")
        self.r_cathode = _spin(0.002, 0.05, g["r_cathode_m"], suf=" m")
        self.length = _spin(0.2, 5.0, g["length_m"], suf=" m")
        self.v_kv = _spin(50, 1200, g["V_cathode_v"] / 1000, dec=0, suf=" kV")
        self.b_t = _spin(0.1, 15, g["B_axial_tesla"], dec=2, suf=" T")
        self.h2 = _spin(0, 500, inj["h2_sccm"], dec=1, suf=" sccm")
        self.b2h6 = _spin(0, 100, inj["b2h6_sccm"], dec=1, suf=" sccm")
        fl.addRow("Anode radius", self.r_anode)
        fl.addRow("Cathode radius", self.r_cathode)
        fl.addRow("Active length", self.length)
        fl.addRow("Cathode bias", self.v_kv)
        fl.addRow("Axial B", self.b_t)
        fl.addRow("H₂", self.h2)
        fl.addRow("B₂H₆", self.b2h6)
        self._layout.addWidget(form)

        split = QSplitter()
        self.canvas_layout = MplCanvas(6.5, 3.8)
        self.canvas_cross = MplCanvas(4.5, 3.8)
        split.addWidget(self.canvas_layout)
        split.addWidget(self.canvas_cross)
        self._layout.addWidget(split, stretch=1)

        self.ov_label = QLabel("PICMI overrides (preview)")
        self.ov_label.setStyleSheet("color: #565f89; font-size: 11px;")
        self._layout.addWidget(self.ov_label)

        self.metrics = MetricGrid(3)
        self._layout.addWidget(self.metrics)

        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _sync_config(self) -> None:
        self._state.update_geometry(
            r_anode_m=self.r_anode.value(),
            r_cathode_m=self.r_cathode.value(),
            length_m=self.length.value(),
            V_cathode_v=self.v_kv.value() * 1000,
            B_axial_tesla=self.b_t.value(),
        )
        self._state.update_injectants(h2_sccm=self.h2.value(), b2h6_sccm=self.b2h6.value())
        self._state.save()

    def _run(self) -> None:
        self._sync_config()
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_00)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        self._sync_config()
        geo = DeviceGeometry(
            r_anode_m=self.r_anode.value(),
            r_cathode_m=self.r_cathode.value(),
            length_m=self.length.value(),
            V_cathode_v=self.v_kv.value() * 1000,
            B_axial_tesla=self.b_t.value(),
        )
        fig1 = self.canvas_layout.figure
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        from ssto.orbitron.simulator.blender_layout import draw_blender_underlay, engine_axial_layout

        layout = engine_axial_layout(geo)
        draw_blender_underlay(ax1, layout, LongitudinalFocus.FULL_DUCT_AIR, symmetric=True)
        ax1.set_title("Engine layout (s–r)", color="#c0caf5")
        fig1.tight_layout()
        self.canvas_layout.draw()

        fig2 = self.canvas_cross.figure
        fig2.clear()
        ax2 = fig2.add_subplot(111)
        render_device_cross_section(ax2, geo, LongitudinalFocus.CORE_TUBE)
        ax2.set_aspect("equal")
        fig2.tight_layout()
        self.canvas_cross.draw()

        txt = self._state.picmi_overrides_text()
        self.ov_label.setText(f"PICMI overrides ({len(txt)} bytes) — run step to refresh")
        data = self._state.try_load_step("00")
        if data:
            self.metrics.set_metrics(
                [
                    ("Status", "Compiled", data.get("generated_utc", "")[:19], "#9ece6a"),
                    ("Overrides", "On disk", "00_spec/picmi_overrides.json", "#7aa2f7"),
                    ("Spec", "YAML", "orbitron_physics_surrogate.yaml", "#a9b1d6"),
                ]
            )
            self.gate.set_gate("Gate: SSOT compiled — proceed to WarpX PIC.", ok=True)
        else:
            self.metrics.set_metrics([("Status", "Pending", "Run this step", "#e0af68")] * 3)
            self.gate.set_gate(self._gate_hint, ok=None)


class Step01PicPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "01",
            "WarpX PIC",
            "Run laminar_flow_2d_arcjet at the pad run point. Produces ρ_e and inject-beam "
            "plotfiles — Tier 2 coupling, not fusion Q.",
            "Last density_diag plotfile exists (or SKIP_PIC acknowledged).",
            state,
            parent,
        )
        self.log.setMaximumHeight(220)

        self.pic_steps = QSpinBox()
        self.pic_steps.setRange(50, 5000)
        self.pic_steps.setValue(int(state.config["pic"]["steps"]))
        self.chk_skip = QCheckBox("Skip WarpX (dev — unity ρ norms in step 2)")
        self.chk_skip.setChecked(bool(state.config.get("gui", {}).get("skip_pic", False)))

        split = QSplitter()
        pad_scroll = QScrollArea()
        pad_scroll.setWidgetResizable(True)
        pad_w = QWidget()
        pad_lay = QVBoxLayout(pad_w)
        self._pad_sync_enabled = False
        self.startup = StartupPanel(self._on_pad_changed)
        self._pad_sync_enabled = True
        pad_lay.addWidget(self.startup)
        pad_lay.addStretch()
        pad_scroll.setWidget(pad_w)
        pad_scroll.setMinimumWidth(340)
        split.addWidget(pad_scroll)

        right = QWidget()
        rlay = QVBoxLayout(right)
        pg = QGroupBox("WarpX PICMI")
        pf = QFormLayout(pg)
        pf.addRow("PIC steps", self.pic_steps)
        pf.addRow(self.chk_skip)
        rlay.addWidget(pg)

        self.canvas = MplCanvas(7, 3.8)
        rlay.addWidget(self.canvas, stretch=1)
        self.metrics = MetricGrid(4)
        rlay.addWidget(self.metrics)
        split.addWidget(right)
        self._layout.addWidget(split, stretch=1)

        self._load_pad_from_config()
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _pad_from_config(self) -> PadStartupState:
        p = self._state.config["pad"]
        return PadStartupState(
            pad_apu_online=True,
            starter_engage=True,
            bleed_air_open=True,
            startup_trigger=True,
            throttle=float(p["throttle"]),
            compressor=float(p["compressor"]),
            cathode_pulse=float(p["cathode_pulse"]),
            laminar_relaminarization=bool(p.get("laminar_relaminarization", True)),
        )

    def _load_pad_from_config(self) -> None:
        self.startup.apply_pad_state(self._pad_from_config())

    def _on_pad_changed(self) -> None:
        if not getattr(self, "_pad_sync_enabled", False):
            return
        self._sync_config()
        self.refresh_from_artifacts()

    def _sync_config(self) -> None:
        pad = self.startup.pad_state()
        self._state.update_pad(
            throttle=pad.throttle,
            compressor=pad.compressor,
            cathode_pulse=pad.cathode_pulse,
            laminar=pad.laminar_relaminarization,
        )
        self._state.update_pic_settings(steps=self.pic_steps.value(), skip_pic=self.chk_skip.isChecked())
        self._state.save()
        if self.chk_skip.isChecked():
            os.environ["SKIP_PIC"] = "1"
        else:
            os.environ.pop("SKIP_PIC", None)

    def _run(self) -> None:
        self._sync_config()
        self.log.clear()
        self.log.append_line("Starting WarpX…")
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = WarpXWorker(skip_pic=self.chk_skip.isChecked(), n_steps=self.pic_steps.value())
        w.log_line.connect(self.log.append_line)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        import json
        from pathlib import Path

        from tools.orbitron_proof_chain.chain_lib import CHAIN_ROOT, load_config, step_completed

        data = None
        art = CHAIN_ROOT / load_config()["steps"]["01"]["artifact"]
        if art.is_file():
            try:
                data = json.loads(art.read_text(encoding="utf-8"))
            except Exception:
                pass
        elif step_completed("01"):
            data = self._state.try_load_step("01")
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if data and data.get("ok") is False:
            rc = data.get("returncode", "?")
            ax.text(
                0.5,
                0.5,
                f"WarpX failed (exit {rc})\n\nSee log above — fix env / PIC, then Run again",
                ha="center",
                va="center",
                color="#f7768e",
                fontsize=12,
            )
            self.metrics.set_metrics(
                [
                    ("Status", "FAILED", f"exit {rc}", "#f7768e"),
                    ("Diags", "empty", data.get("diags_dir", ""), "#e0af68"),
                ]
            )
            self.gate.set_gate("Gate: WarpX did not finish — no plotfiles to preview.", ok=False)
        elif data and not data.get("skipped"):
            slice3d, err = load_pic_slice_2d_with_error()
            if slice3d:
                x, z, rho = slice3d
                im = ax.pcolormesh(x, z, rho, shading="auto", cmap="magma")
                fig.colorbar(im, ax=ax, label="|ρ_e|")
                run_th = data.get("throttle")
                run_co = data.get("compressor")
                run_pu = data.get("cathode_pulse")
                pad_now = self.startup.pad_state()
                title = "Last PIC frame — |ρ_e| (x–z transverse cut)"
                if run_th is not None:
                    title += (
                        f"\nfrom run: thr={run_th:.2f} comp={run_co:.2f} pulse={run_pu:.2f}"
                        f"  ({data.get('n_steps', '?')} steps)"
                    )
                ax.set_title(title, color="#c0caf5", fontsize=10)
                ax.set_xlabel("x [m]")
                ax.set_ylabel("z [m]")
                if run_th is not None and (
                    abs(pad_now.throttle - float(run_th)) > 0.02
                    or abs(pad_now.compressor - float(run_co)) > 0.02
                    or abs(pad_now.cathode_pulse - float(run_pu)) > 0.02
                ):
                    ax.text(
                        0.5,
                        0.02,
                        "Sliders changed — click Run this step to update PIC",
                        transform=ax.transAxes,
                        ha="center",
                        va="bottom",
                        color="#e0af68",
                        fontsize=9,
                    )
            else:
                ax.text(
                    0.5,
                    0.5,
                    err or "No preview",
                    ha="center",
                    va="center",
                    color="#a9b1d6",
                    fontsize=11,
                    wrap=True,
                )
            diags = Path(data.get("diags_dir", ""))
            n_pf = len(list_pic_plotfiles(diags)) if diags.is_dir() else len(data.get("plotfiles", []))
            self.metrics.set_metrics(
                [
                    ("Plotfiles", str(n_pf), str(diags) if diags else "", "#9ece6a" if n_pf else "#e0af68"),
                    ("Throttle", f"{data.get('throttle', 0):.2f}", "pad", "#7aa2f7"),
                    ("Compressor", f"{data.get('compressor', 0):.2f}", "pad", "#7aa2f7"),
                    ("Pulse", f"{data.get('cathode_pulse', 0):.2f}", "cathode", "#7aa2f7"),
                ]
            )
            if n_pf and slice3d:
                self.gate.set_gate("Gate: PIC completed — run step 02 to reduce ρ norms.", ok=True)
            elif n_pf:
                self.gate.set_gate("Gate: plotfiles on disk but preview failed — see message.", ok=None)
            else:
                self.gate.set_gate("Gate: step marked done but no plotfiles — re-run WarpX.", ok=False)
        elif data and data.get("skipped"):
            ax.text(0.5, 0.5, "PIC skipped\n(SKIP_PIC)", ha="center", va="center", color="#e0af68", fontsize=14)
            self.gate.set_gate("Gate: skipped — step 2 will use unity norms (not Tier-2 closed).", ok=None)
        else:
            ax.text(0.5, 0.5, "Run WarpX PIC", ha="center", va="center", color="#565f89", fontsize=14)
            self.gate.set_gate(self._gate_hint, ok=None)
        fig.tight_layout()
        self.canvas.draw()


class Step02ReducePanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "02",
            "PIC reduce",
            "Reduce last plotfile to ρ_e_norm and ρ_beam_norm — handoff to 0D plant and fusion channel.",
            "0.2 ≤ ρ_norm ≤ 3.0 (plant clamp band).",
            state,
            parent,
        )
        split = QSplitter()
        self.canvas_bars = MplCanvas(5, 3.5)
        self.canvas_gauge = MplCanvas(4, 3.5)
        split.addWidget(self.canvas_bars)
        split.addWidget(self.canvas_gauge)
        self._layout.addWidget(split, stretch=1)
        self.metrics = MetricGrid(4)
        self._layout.addWidget(self.metrics)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _run(self) -> None:
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_02)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        data = self._state.try_load_step("02")
        fig1 = self.canvas_bars.figure
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        if data:
            labels = ["ρ_e norm", "ρ_beam norm"]
            vals = [data.get("rho_e_norm", 1), data.get("rho_beam_norm", 1)]
            colors = ["#7aa2f7" if 0.2 <= v <= 3 else "#f7768e" for v in vals]
            ax1.bar(labels, vals, color=colors)
            ax1.axhline(0.2, color="#565f89", ls="--", lw=0.8)
            ax1.axhline(3.0, color="#565f89", ls="--", lw=0.8)
            ax1.set_ylabel("Normalized ρ")
            ax1.set_title("PIC coupling proxies", color="#c0caf5")
            ax1.grid(True, alpha=0.25)

            fig2 = self.canvas_gauge.figure
            fig2.clear()
            ax2 = fig2.add_subplot(111)
            re, rb = vals[0], vals[1]
            ok_e = 0.2 <= re <= 3.0
            ok_b = 0.2 <= rb <= 3.0
            ax2.barh(["ρ_e", "ρ_beam"], [re, rb], color=["#9ece6a" if ok_e else "#f7768e", "#9ece6a" if ok_b else "#f7768e"])
            ax2.set_xlim(0, max(3.5, max(vals) * 1.2))
            ax2.set_title("Clamp band", color="#c0caf5")

            self.metrics.set_metrics(
                [
                    ("ρ_e mean", f"{data.get('rho_e_mean', 0):.2e}", f"norm {re:.3f}", None),
                    ("ρ_beam screen", f"{data.get('rho_beam_screen_mean', 0):.2e}", f"norm {rb:.3f}", None),
                    ("Refs", "1e15 / 1e10", "normalization", "#565f89"),
                    (
                        "Tier 2",
                        "Coupled" if not data.get("skipped") else "Skipped",
                        "",
                        "#9ece6a" if ok_e and ok_b else "#e0af68",
                    ),
                ]
            )
            gate_ok = ok_e and ok_b
            self.gate.set_gate(
                "Gate: norms in band — feed fusion channel & plant."
                if gate_ok
                else "Gate: norms out of band — revisit PIC or geometry.",
                ok=gate_ok,
            )
        else:
            ax1.text(0.5, 0.5, "Run PIC reduce", ha="center", color="#565f89")
            self.gate.set_gate(self._gate_hint, ok=None)
        fig1.tight_layout()
        self.canvas_bars.draw()
        if data:
            fig2.tight_layout()
            self.canvas_gauge.draw()
