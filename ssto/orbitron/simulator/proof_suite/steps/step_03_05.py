"""Proof suite steps 03–05: fusion channel, fueling, burn."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
)

from ssto.orbitron.simulator.fusion_pb11 import pb11_reactivity_m3_s
from ssto.orbitron.simulator.proof_chain.runners import run_step_03, run_step_04, run_step_05
from ssto.orbitron.simulator.proof_suite.steps.base import ProofStepPanel
from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.widgets import MetricGrid, MplCanvas
from ssto.orbitron.simulator.proof_suite.workers import StepWorker
from ssto.orbitron.simulator.blender_layout import draw_blender_underlay, engine_axial_layout
from ssto.orbitron.simulator.longitudinal.focus import LongitudinalFocus
from ssto.orbitron.simulator.types import DeviceGeometry


class Step03FusionPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "03",
            "Fusion channel (s–r)",
            "Longitudinal fusion-relevant density and p-¹¹B reaction rate. Toggle laminar "
            "relaminarization to break up clumps (Orbitron-video intent).",
            "Laminar ON: clump index ≤ 2.8 and OFF/ON reduction ≥ 1.25×.",
            state,
            parent,
        )
        ctrl = QHBoxLayout()
        self.chk_laminar = QCheckBox("Laminar relaminarization ON")
        self.chk_laminar.setChecked(state.config["pad"].get("laminar_relaminarization", True))
        self.btn_compare = QPushButton("Run OFF vs ON compare")
        self.field_combo = QComboBox()
        self.field_combo.addItems(["Fuel density n(s,r)", "Reaction rate R(s,r)"])
        ctrl.addWidget(self.chk_laminar)
        ctrl.addWidget(self.btn_compare)
        ctrl.addStretch()
        ctrl.addWidget(QLabel("Field:"))
        ctrl.addWidget(self.field_combo)
        self._layout.addLayout(ctrl)

        self.canvas = MplCanvas(8, 4.8)
        self._layout.addWidget(self.canvas, stretch=1)

        scrub = QHBoxLayout()
        scrub.addWidget(QLabel("Time"))
        self.time_slider = QSlider()
        self.time_slider.setOrientation(Qt.Orientation.Horizontal)
        self.time_slider.valueChanged.connect(self._draw_frame)
        self.time_label = QLabel("t = —")
        scrub.addWidget(self.time_slider, stretch=1)
        scrub.addWidget(self.time_label)
        self._layout.addLayout(scrub)

        split = QSplitter()
        self.canvas_clump = MplCanvas(5, 2.8)
        self.canvas_radial = MplCanvas(5, 2.8)
        split.addWidget(self.canvas_clump)
        split.addWidget(self.canvas_radial)
        self._layout.addWidget(split)

        self.metrics = MetricGrid(4)
        self._layout.addWidget(self.metrics)

        self._fc = None
        self._npz: dict | None = None
        self.chk_laminar.toggled.connect(self._on_laminar_toggled)
        self.field_combo.currentIndexChanged.connect(self._draw_frame)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.btn_compare.clicked.connect(self._run_compare)
        self.refresh_from_artifacts()

    def _on_laminar_toggled(self) -> None:
        p = self._state.config["pad"]
        self._state.update_pad(
            throttle=p["throttle"],
            compressor=p["compressor"],
            cathode_pulse=p["cathode_pulse"],
            laminar=self.chk_laminar.isChecked(),
        )
        self._state.save()

    def _sync_config(self) -> None:
        p = self._state.config["pad"]
        self._state.update_pad(
            throttle=p["throttle"],
            compressor=p["compressor"],
            cathode_pulse=p["cathode_pulse"],
            laminar=self.chk_laminar.isChecked(),
        )
        self._state.save()

    def _load_npz(self) -> bool:
        data = self._state.try_load_step("03")
        if not data or "fields_npz" not in data:
            self._npz = None
            return False
        path = Path(data["fields_npz"])
        if not path.is_file():
            return False
        z = np.load(path)
        self._npz = {k: z[k] for k in z.files}
        return True

    def _run(self) -> None:
        self._sync_config()
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_03, laminar_on=self.chk_laminar.isChecked(), compare_hack=False)
        w.finished.connect(self._on_run_done)
        w.start()
        self._worker = w

    def _run_compare(self) -> None:
        self._sync_config()
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_03, laminar_on=True, compare_hack=True)
        w.finished.connect(self._on_run_done)
        w.start()
        self._worker = w

    def _on_run_done(self, result, error) -> None:
        if result and "_fusion_channel" in result:
            self._fc = result.pop("_fusion_channel")
        self.on_step_finished(result, error)

    def _draw_frame(self) -> None:
        if self._npz is None and not self._load_npz():
            return
        idx = self.time_slider.value()
        nt = len(self._npz["time_s"])
        idx = max(0, min(idx, nt - 1))
        use_r = self.field_combo.currentIndex() == 1
        data = self._npz["reaction_rate"] if use_r else self._npz["density"]
        s, r = self._npz["s_m"], self._npz["r_m"]
        g = self._state.config["geometry"]
        geo = DeviceGeometry(
            g["r_anode_m"], g["r_cathode_m"], g["length_m"], g["V_cathode_v"], g["B_axial_tesla"]
        )
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        layout = engine_axial_layout(geo)
        draw_blender_underlay(ax, layout, LongitudinalFocus.FUSION_CHANNEL_SR, symmetric=False)
        im = ax.pcolormesh(s, r, data[idx], shading="auto", cmap="magma", alpha=0.75)
        fig.colorbar(im, ax=ax)
        laminar = "ON" if self.chk_laminar.isChecked() else "OFF"
        ax.set_title(f"Fusion channel s–r  |  laminar {laminar}", color="#c0caf5")
        ax.set_xlabel("Axial s [m]")
        ax.set_ylabel("Radius r [m]")
        t = float(self._npz["time_s"][idx])
        self.time_label.setText(f"t = {t:.3e} s  frame {idx + 1}/{nt}")
        fig.tight_layout()
        self.canvas.draw()

    def refresh_from_artifacts(self) -> None:
        data = self._state.try_load_step("03")
        if self._load_npz():
            nt = len(self._npz["time_s"])
            self.time_slider.setMaximum(max(0, nt - 1))
            self._draw_frame()
            clump = self._npz["clump_index"]
            figc = self.canvas_clump.figure
            figc.clear()
            axc = figc.add_subplot(111)
            axc.plot(self._npz["time_s"], clump, color="#7aa2f7")
            axc.axhline(2.8, color="#e0af68", ls="--", label="pass threshold")
            axc.set_xlabel("Time [s]")
            axc.set_ylabel("Clump index")
            axc.set_title("Clump index vs time", color="#c0caf5")
            axc.legend(fontsize=8)
            figc.tight_layout()
            self.canvas_clump.draw()

            figr = self.canvas_radial.figure
            figr.clear()
            axr = figr.add_subplot(111)
            last = self._npz["density"][-1]
            axr.plot(r, np.mean(last, axis=0), color="#9ece6a")
            axr.set_xlabel("r [m]")
            axr.set_ylabel("⟨n⟩_s")
            axr.set_title("Axial-averaged density (final)", color="#c0caf5")
            figr.tight_layout()
            self.canvas_radial.draw()

        if data:
            ci = data.get("clump_index_final", 0)
            red = data.get("clump_reduction_ratio", 1)
            p = data.get("integrated_fusion_power_mw", 0)
            ok = ci <= 2.8 and red >= 1.25
            self.metrics.set_metrics(
                [
                    ("Clump index", f"{ci:.2f}", "≤ 2.8", "#9ece6a" if ci <= 2.8 else "#f7768e"),
                    ("OFF/ON ratio", f"{red:.2f}×", "≥ 1.25×", "#9ece6a" if red >= 1.25 else "#f7768e"),
                    ("P_int", f"{p:.4g} MW", "Tier-3 headline", "#7aa2f7"),
                    ("Laminar", "ON" if data.get("laminar_enabled") else "OFF", "", None),
                ]
            )
            self.gate.set_gate(
                "Gate: laminar hack breaks up clumps." if ok else "Gate: clump metrics not met — tune pad/shear.",
                ok=ok,
            )
        else:
            self.gate.set_gate(self._gate_hint, ok=None)


class Step04FuelingPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "04",
            "Fueling → densities",
            "Map H₂/B₂H₆ injectants and PIC ρ_e into n_p, n_B and effective T_i. "
            "Forward only — no power tuning knob.",
            "Finite n_p, n_B at ignited pad point; document τ and volume in fusion_pb11.",
            state,
            parent,
        )
        split = QSplitter()
        self.canvas_species = MplCanvas(5, 3.5)
        self.canvas_sv = MplCanvas(5, 3.5)
        split.addWidget(self.canvas_species)
        split.addWidget(self.canvas_sv)
        self._layout.addWidget(split, stretch=1)
        self.metrics = MetricGrid(4)
        self._layout.addWidget(self.metrics)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _run(self) -> None:
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_04)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        data = self._state.try_load_step("04")
        fig1 = self.canvas_species.figure
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        if data:
            np_p = data["n_proton_m3"]
            np_b = data["n_boron_m3"]
            ax1.bar(["n_p (H⁺)", "n_B"], [np_p, np_b], color=["#7aa2f7", "#bb9af7"])
            ax1.set_yscale("log")
            ax1.set_ylabel("m⁻³")
            ax1.set_title("Reactant densities", color="#c0caf5")
            ax1.grid(True, axis="y", alpha=0.3)

            T = data["ion_temperature_kev"]
            temps = np.linspace(20, 800, 200)
            sv = [pb11_reactivity_m3_s(t) for t in temps]
            fig2 = self.canvas_sv.figure
            fig2.clear()
            ax2 = fig2.add_subplot(111)
            ax2.semilogy(temps, sv, color="#9ece6a")
            ax2.axvline(T, color="#f7768e", ls="--", label=f"T_i={T:.0f} keV")
            ax2.scatter([T], [data["sigma_v_m3_s"]], color="#f7768e", s=60, zorder=5)
            ax2.set_xlabel("T_i [keV]")
            ax2.set_ylabel("⟨σv⟩ [m³/s]")
            ax2.set_title("p-¹¹B reactivity (analytical fit)", color="#c0caf5")
            ax2.legend(fontsize=8)
            fig2.tight_layout()
            self.canvas_sv.draw()

            self.metrics.set_metrics(
                [
                    ("T_i", f"{T:.1f} keV", "from 600 kV class", "#7aa2f7"),
                    ("⟨σv⟩", f"{data['sigma_v_m3_s']:.2e}", "m³/s", "#9ece6a"),
                    ("Volume", f"{data['plasma_volume_m3']:.4f} m³", "fill factor", "#a9b1d6"),
                    ("η_conf", f"{data['confinement_factor']:.3f}", "incl. PIC", "#e0af68"),
                ]
            )
            self.gate.set_gate("Gate: fueling path defined — run burn step.", ok=np_p > 0 and np_b > 0)
        else:
            ax1.text(0.5, 0.5, "Run fueling step", ha="center", color="#565f89")
            self.gate.set_gate(self._gate_hint, ok=None)
        fig1.tight_layout()
        self.canvas_species.draw()


class Step05BurnPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "05",
            "p-¹¹B burn",
            "Integrated fusion power at proof settings (reactivity scale = 1). "
            "Shortfall vs 3.5 MW is expected until Tier 4 / improved confinement.",
            "Power computed, not tuned; record shortfall honestly.",
            state,
            parent,
        )
        self.canvas = MplCanvas(6, 4)
        self._layout.addWidget(self.canvas, stretch=1)
        self.metrics = MetricGrid(3)
        self._layout.addWidget(self.metrics)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.refresh_from_artifacts()

    def _run(self) -> None:
        self.toolbar.btn_run.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_05)
        w.finished.connect(self.on_step_finished)
        w.start()
        self._worker = w

    def refresh_from_artifacts(self) -> None:
        data = self._state.try_load_step("05")
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if data:
            target = data["target_gross_power_mw"]
            achieved = data["fusion_power_mw"]
            short = data["shortfall_mw"]
            ax.bar(
                ["Target", "P_fusion (proof)"],
                [target, achieved],
                color=["#565f89", "#9ece6a" if short < 0.5 else "#f7768e"],
            )
            ax.set_ylabel("MW")
            ax.set_title("Fusion power vs design target", color="#c0caf5")
            if achieved > 0:
                ax.set_yscale("log")
            self.metrics.set_metrics(
                [
                    ("P_fusion", f"{achieved:.4g} MW", "proof mode", None),
                    ("Target", f"{target:.2f} MW", "design", "#565f89"),
                    ("Shortfall", f"{short:.4g} MW", "Tier 3 gap", "#f7768e" if short > 0.5 else "#9ece6a"),
                ]
            )
            self.gate.set_gate(
                "Gate: burn computed — shortfall documents physics gap (not a failure of the chain).",
                ok=True,
            )
        else:
            ax.text(0.5, 0.5, "Run burn step", ha="center", color="#565f89")
            self.gate.set_gate(self._gate_hint, ok=None)
        fig.tight_layout()
        self.canvas.draw()
