"""Proof suite steps 03–05: fusion channel, fueling, burn."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
)

from ssto.orbitron.simulator.injectants import normalize_injectants_cfg
from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.types import PadStartupState

from ssto.orbitron.simulator.fusion_pb11 import pb11_reactivity_m3_s
from ssto.orbitron.simulator.proof_chain.runners import (
    run_step_03,
    run_step_03_compare_pair,
    run_step_04,
    run_step_05,
)
from ssto.orbitron.simulator.proof_suite.longitudinal_viz import (
    draw_fusion_channel_heatmap,
    fusion_channel_colorbar,
    fusion_field_color_limits,
    fusion_off_on_log_ratio,
)
from ssto.orbitron.simulator.proof_suite.steps.base import ProofStepPanel
from ssto.orbitron.simulator.proof_suite.state import ProofSuiteState
from ssto.orbitron.simulator.proof_suite.widgets import MetricGrid, MplCanvas, apply_dark_axes
from ssto.orbitron.simulator.proof_suite.workers import StepWorker
from ssto.orbitron.simulator.types import DeviceGeometry


def _spin(lo: float, hi: float, val: float, *, dec: int = 2, suf: str = "") -> QDoubleSpinBox:
    s = QDoubleSpinBox()
    s.setRange(lo, hi)
    s.setDecimals(dec)
    s.setValue(val)
    if suf:
        s.setSuffix(suf)
    return s


class Step03FusionPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "03",
            "Fusion channel (s–r)",
            "Longitudinal n(s,r) with fuel inject rates (H₂ sccm, laser Hz) and axial-stir proxy "
            "c_eff (compressor×bleed×spool). Laminar OFF uses stochastic mid-bore clumps — "
            "equations: validation_steps.md § State evolution → Step 3.",
            "Laminar ON: clump index ≤ 2.8 and OFF/ON reduction ≥ 1.25× (validation channel).",
            state,
            parent,
        )
        cfg = state.config
        inj = normalize_injectants_cfg(cfg["injectants"])
        pad = cfg["pad"]
        fc_cfg = cfg.get("fusion_channel") or {}

        inputs = QGroupBox("Run inputs — change rates, then Run or Cache OFF+ON pair")
        inputs_lay = QVBoxLayout(inputs)
        dep = QLabel(
            "Injection amplitude scales with H₂ and √laser Hz. Compressor (U/J) is <b>not</b> fuel — "
            "it sets c_eff for axial advection only (Brayton mdot is step 06). "
            "Use <b>Cache laminar OFF+ON pair</b> and scrub Time past frame ~10 to see blobs on OFF."
        )
        dep.setWordWrap(True)
        dep.setTextFormat(Qt.TextFormat.RichText)
        dep.setStyleSheet("color: #e0af68; font-size: 11px; font-weight: bold;")
        inputs_lay.addWidget(dep)

        rates = QGroupBox("Fuel injection rates (step 03)")
        rf = QFormLayout(rates)
        self.h2 = _spin(0, 500, inj["h2_sccm"], dec=1, suf=" sccm")
        self.laser_hz = _spin(0, 50, inj["laser_ablation_hz"], dec=1, suf=" Hz")
        self.compressor = _spin(0, 1, pad["compressor"], dec=2)
        self.compressor.setToolTip("Pad compressor command (U/J) — scales axial u_s via c_eff")
        self.lbl_c_eff = QLabel("c_eff = —")
        self.lbl_c_eff.setStyleSheet("color: #7aa2f7; font-size: 11px;")
        self.lbl_rate_scale = QLabel("inject scale = —")
        self.lbl_rate_scale.setStyleSheet("color: #9ece6a; font-size: 11px;")
        rf.addRow("H₂ flow", self.h2)
        rf.addRow("¹¹B laser ablation", self.laser_hz)
        rf.addRow("Compressor cmd c", self.compressor)
        rf.addRow("Axial stir", self.lbl_c_eff)
        rf.addRow("Rate scale λ", self.lbl_rate_scale)
        inputs_lay.addWidget(rates)

        adv = QGroupBox("Clump physics (laminar OFF)")
        af = QFormLayout(adv)
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 999_999)
        self.seed_spin.setValue(int(fc_cfg.get("stochastic_seed", 42)))
        self.noise = _spin(0, 0.5, float(fc_cfg.get("noise_fraction_off", 0.14)), dec=3)
        self.noise.setToolTip("Fractional Gaussian noise on n(s,r) each step when laminar OFF")
        af.addRow("RNG seed", self.seed_spin)
        af.addRow("Noise fraction", self.noise)
        inputs_lay.addWidget(adv)
        self.place_inputs_above_run(inputs)

        for w in (self.h2, self.laser_hz, self.compressor, self.noise):
            w.valueChanged.connect(self._on_rates_changed)
        self.seed_spin.valueChanged.connect(self._on_rates_changed)
        self._on_rates_changed()

        ctrl = QHBoxLayout()
        self.chk_laminar = QCheckBox("Laminar relaminarization ON")
        self.chk_laminar.setChecked(state.config["pad"].get("laminar_relaminarization", True))
        self.btn_cache_pair = QPushButton("Cache laminar OFF+ON pair (for side-by-side)")
        self.btn_cache_pair.setToolTip(
            "Runs fusion channel twice (ON and OFF) and saves both NPZ files. "
            "Side-by-side view then works without re-running."
        )
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Single panel", "Side-by-side OFF | ON"])
        self.field_combo = QComboBox()
        self.field_combo.addItems(["Fuel density n(s,r)", "Reaction rate R(s,r)"])
        ctrl.addWidget(self.chk_laminar)
        ctrl.addWidget(self.btn_cache_pair)
        ctrl.addStretch()
        ctrl.addWidget(QLabel("View:"))
        ctrl.addWidget(self.view_combo)
        ctrl.addWidget(QLabel("Field:"))
        ctrl.addWidget(self.field_combo)
        self._layout.addLayout(ctrl)

        self.canvas = MplCanvas(14, 3.8)
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
        self._npz_on: dict | None = None
        self._npz_off: dict | None = None
        self.chk_laminar.toggled.connect(self._on_laminar_toggled)
        self.view_combo.currentIndexChanged.connect(self._draw_frame)
        self.field_combo.currentIndexChanged.connect(self._draw_frame)
        self.toolbar.btn_run.clicked.connect(self._run)
        self.btn_cache_pair.clicked.connect(self._run_cache_pair)
        self.refresh_from_artifacts()

    def _on_rates_changed(self) -> None:
        import math

        p = self._state.config["pad"]
        pad_st = PadStartupState(
            pad_apu_online=bool(p.get("pad_apu_online", True)),
            starter_engage=bool(p.get("starter_engage", True)),
            bleed_air_open=bool(p.get("bleed_air_open", True)),
            vacuum_interlock_ok=bool(p.get("vacuum_interlock_ok", True)),
            laser_armed=bool(p.get("laser_armed", True)),
            hv_enabled=bool(p.get("hv_enabled", True)),
            startup_trigger=bool(p.get("startup_trigger", True)),
            throttle=float(p["throttle"]),
            compressor=float(self.compressor.value()),
            cathode_pulse=float(p["cathode_pulse"]),
        )
        st = evaluate_pad_status(pad_st)
        h2 = self.h2.value()
        laser = self.laser_hz.value()
        fc = self._state.config.get("fusion_channel") or {}
        lam = math.sqrt(laser / max(float(fc.get("laser_ref_hz", 10)), 0.1))
        rate = (h2 / max(float(fc.get("h2_ref_sccm", 80)), 1.0)) * lam
        rate = max(0.05, min(4.0, rate))
        self.lbl_c_eff.setText(f"c_eff = {st.compressor_effective:.2f}  (c × bleed × spool)")
        self.lbl_rate_scale.setText(f"λ = {rate:.2f}  (H₂/80 × √(laser/10))")

    def _on_laminar_toggled(self) -> None:
        self._sync_config()

    def _sync_config(self) -> None:
        p = self._state.config["pad"]
        self._state.update_injectants(
            h2_sccm=self.h2.value(),
            laser_ablation_hz=self.laser_hz.value(),
            b11_target_index=int(p.get("b11_target_index", 0)),
        )
        self._state.update_pad(
            throttle=float(p["throttle"]),
            compressor=float(self.compressor.value()),
            cathode_pulse=float(p["cathode_pulse"]),
            laminar=self.chk_laminar.isChecked(),
        )
        self._state.update_fusion_channel(
            stochastic_seed=int(self.seed_spin.value()),
            noise_fraction_off=float(self.noise.value()),
        )
        self._state.save()
        self._on_rates_changed()

    def _load_npz_file(self, path: Path | None) -> dict | None:
        if path is None or not path.is_file():
            return None
        z = np.load(path)
        return {k: z[k] for k in z.files}

    def _load_all_npz(self) -> bool:
        data = self._state.try_load_step("03")
        if not data:
            self._npz = self._npz_on = self._npz_off = None
            return False
        self._npz = self._load_npz_file(Path(data["fields_npz"])) if data.get("fields_npz") else None
        on_p = data.get("fields_laminar_on_npz")
        off_p = data.get("fields_laminar_off_npz")
        self._npz_on = self._load_npz_file(Path(on_p) if on_p else None)
        self._npz_off = self._load_npz_file(Path(off_p) if off_p else None)
        if self._npz_on is None and self._npz is not None:
            self._npz_on = self._npz
        return self._npz is not None or self._npz_on is not None

    def _has_compare_pair(self) -> bool:
        return self._npz_on is not None and self._npz_off is not None

    def _run(self) -> None:
        self._sync_config()
        self.log.append_line("Running fusion channel (single laminar state)…")
        self.toolbar.btn_run.setEnabled(False)
        self.btn_cache_pair.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(
            run_step_03,
            laminar_on=self.chk_laminar.isChecked(),
            compare_hack=True,
        )
        w.finished.connect(self._on_run_done)
        w.start()
        self._worker = w

    def _run_cache_pair(self) -> None:
        self._sync_config()
        self.log.append_line("Caching laminar ON + OFF pair (two runs)…")
        self.toolbar.btn_run.setEnabled(False)
        self.btn_cache_pair.setEnabled(False)
        self.toolbar.progress.show()
        w = StepWorker(run_step_03_compare_pair)
        w.finished.connect(self._on_cache_pair_done)
        w.start()
        self._worker = w

    def on_step_finished(self, result, error) -> None:
        self.btn_cache_pair.setEnabled(True)
        super().on_step_finished(result, error)

    def _on_run_done(self, result, error) -> None:
        if result and "_fusion_channel" in result:
            self._fc = result.pop("_fusion_channel")
        self.on_step_finished(result, error)
        if error is None:
            self.view_combo.setCurrentIndex(0)

    def _on_cache_pair_done(self, result, error) -> None:
        if result and "_fusion_channel" in result:
            self._fc = result.pop("_fusion_channel")
        self.on_step_finished(result, error)
        if error is None:
            self.view_combo.setCurrentIndex(1)
            self.log.append_line("Compare pair cached — use side-by-side view and scrub time.")

    def _plot_heatmap(
        self,
        ax,
        npz: dict,
        idx: int,
        *,
        title: str,
        geo: DeviceGeometry,
        vmin: float | None = None,
        vmax: float | None = None,
    ) -> None:
        use_r = self.field_combo.currentIndex() == 1
        data = npz["reaction_rate"] if use_r else npz["density"]
        if use_r and vmax is not None and vmax <= 0.0:
            ax.text(
                0.5,
                0.5,
                "R(s,r) = 0 — enable IGNITE interlocks\nand re-run coupled chain",
                ha="center",
                va="center",
                color="#f7768e",
                fontsize=10,
                transform=ax.transAxes,
            )
            apply_dark_axes(ax)
            ax.set_title(title, color="#c0caf5")
            return None
        im = draw_fusion_channel_heatmap(
            ax,
            npz["s_m"],
            npz["r_m"],
            data[idx],
            r_anode_m=geo.r_anode_m,
            title=title,
            vmin=vmin,
            vmax=vmax,
        )
        apply_dark_axes(ax)
        return im

    def _draw_frame(self) -> None:
        if not self._load_all_npz():
            return
        side_by_side = self.view_combo.currentIndex() == 1 and self._has_compare_pair()
        ref = self._npz_on if side_by_side else (self._npz or self._npz_on)
        if ref is None:
            return
        idx = self.time_slider.value()
        nt = len(ref["time_s"])
        idx = max(0, min(idx, nt - 1))
        g = self._state.config["geometry"]
        geo = DeviceGeometry(
            g["r_anode_m"], g["r_cathode_m"], g["length_m"], g["V_cathode_v"], g["B_axial_tesla"]
        )
        fig = self.canvas.figure
        fig.clear()
        use_r = self.field_combo.currentIndex() == 1
        field_key = "reaction_rate" if use_r else "density"
        stacks = [ref[field_key]]
        if side_by_side and self._npz_off is not None and self._npz_on is not None:
            stacks = [self._npz_off[field_key], self._npz_on[field_key]]
        vmin, vmax = fusion_field_color_limits(*stacks)
        if side_by_side and self._npz_off is not None and self._npz_on is not None:
            vmin_off, vmax_off = fusion_field_color_limits(self._npz_off[field_key])
            vmin_on, vmax_on = fusion_field_color_limits(self._npz_on[field_key])
            ax_off = fig.add_subplot(131)
            ax_on = fig.add_subplot(132)
            ax_ratio = fig.add_subplot(133)
            im0 = self._plot_heatmap(
                ax_off,
                self._npz_off,
                idx,
                title="Laminar OFF (clumping)",
                geo=geo,
                vmin=vmin_off,
                vmax=vmax_off,
            )
            im1 = self._plot_heatmap(
                ax_on,
                self._npz_on,
                idx,
                title="Laminar ON (smoothed)",
                geo=geo,
                vmin=vmin_on,
                vmax=vmax_on,
            )
            ratio = fusion_off_on_log_ratio(
                self._npz_off[field_key][idx], self._npz_on[field_key][idx]
            )
            r_vmin, r_vmax = fusion_field_color_limits(ratio[np.newaxis, ...])
            im2 = draw_fusion_channel_heatmap(
                ax_ratio,
                self._npz_on["s_m"],
                self._npz_on["r_m"],
                ratio,
                r_anode_m=geo.r_anode_m,
                title="log10(OFF/ON)",
                vmin=r_vmin,
                vmax=r_vmax,
                cmap="RdBu_r",
            )
            if im0 is not None:
                fusion_channel_colorbar(fig, ax_off, im0)
            if im1 is not None:
                fusion_channel_colorbar(fig, ax_on, im1)
            if im2 is not None:
                fusion_channel_colorbar(fig, ax_ratio, im2)
            fig.subplots_adjust(left=0.05, right=0.94, top=0.92, bottom=0.12, wspace=0.38)
        else:
            ax = fig.add_subplot(111)
            laminar = "ON" if self.chk_laminar.isChecked() else "OFF"
            im = self._plot_heatmap(
                ax,
                ref,
                idx,
                title=f"Fusion channel s–r  |  laminar {laminar}",
                geo=geo,
                vmin=vmin,
                vmax=vmax,
            )
            if im is not None:
                fusion_channel_colorbar(fig, ax, im)
        t = float(ref["time_s"][idx])
        d0 = ref[field_key][0]
        delta = float(np.max(np.abs(ref[field_key][idx] - d0)))
        self.time_label.setText(
            f"t = {t:.3e} s  frame {idx + 1}/{nt}  |Δ{field_key}|={delta:.2e}"
        )
        fig.tight_layout()
        self.canvas.draw()

    def refresh_from_artifacts(self) -> None:
        inj = normalize_injectants_cfg(self._state.config["injectants"])
        pad = self._state.config["pad"]
        fc = self._state.config.get("fusion_channel") or {}
        self.h2.blockSignals(True)
        self.laser_hz.blockSignals(True)
        self.compressor.blockSignals(True)
        self.h2.setValue(inj["h2_sccm"])
        self.laser_hz.setValue(inj["laser_ablation_hz"])
        self.compressor.setValue(pad["compressor"])
        self.seed_spin.setValue(int(fc.get("stochastic_seed", 42)))
        self.noise.setValue(float(fc.get("noise_fraction_off", 0.14)))
        self.h2.blockSignals(False)
        self.laser_hz.blockSignals(False)
        self.compressor.blockSignals(False)
        self._on_rates_changed()
        data = self._state.try_load_step("03")
        has_pair = bool(data and data.get("has_compare_pair"))
        self.view_combo.setItemText(1, "Side-by-side OFF | ON" + (" ✓" if has_pair else " (cache pair first)"))
        if self._load_all_npz():

            ref = self._npz or self._npz_on
            nt = len(ref["time_s"])
            self.time_slider.setMaximum(max(0, nt - 1))
            mid = max(0, nt // 2)
            self.time_slider.blockSignals(True)
            self.time_slider.setValue(mid)
            self.time_slider.blockSignals(False)
            self._draw_frame()
            figc = self.canvas_clump.figure
            figc.clear()
            axc = figc.add_subplot(111)
            if self._npz_on is not None:
                axc.plot(
                    self._npz_on["time_s"],
                    self._npz_on["clump_index"],
                    color="#9ece6a",
                    label="ON",
                )
            if self._npz_off is not None:
                axc.plot(
                    self._npz_off["time_s"],
                    self._npz_off["clump_index"],
                    color="#f7768e",
                    label="OFF",
                )
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
            last = ref["density"][-1]
            r_axis = ref["r_m"]
            axr.plot(r_axis, np.mean(last, axis=0), color="#9ece6a")
            axr.set_xlabel("r [m]")
            axr.set_ylabel("⟨n⟩_s")
            axr.set_title("Axial-averaged density (final)", color="#c0caf5")
            figr.tight_layout()
            self.canvas_radial.draw()

        if data:
            ci = data.get("clump_index_final", 0)
            red = data.get("clump_reduction_ratio", 1)
            p = data.get("integrated_fusion_power_mw", 0)
            fuel_x = data.get("fuel_coupling_norm")
            ok_ci = ci <= 2.8
            ok_red = red >= 1.25
            ok = ok_ci and ok_red
            fuel_s = f"{float(fuel_x):.2f}" if fuel_x is not None else "—"
            lam_s = f"{float(data.get('inject_rate_scale', 0)):.2f}" if data.get("inject_rate_scale") else "—"
            h2s = data.get("h2_sccm")
            ci_off = data.get("clump_index_off")
            self.metrics.set_metrics(
                [
                    ("Clump ON", f"{ci:.2f}", "≤ 2.8", "#9ece6a" if ok_ci else "#f7768e"),
                    ("OFF/ON", f"{red:.2f}×", "≥ 1.25×", "#9ece6a" if ok_red else "#f7768e"),
                    ("Clump OFF", f"{float(ci_off):.2f}" if ci_off else "—", "cache pair", "#a9b1d6"),
                    ("λ inject", lam_s, f"H₂={h2s} sccm" if h2s else "run step", "#7aa2f7"),
                ]
            )
            if ok:
                gate = "Gate: laminar hack breaks up clumps."
            elif not ok_ci and not ok_red:
                gate = (
                    "Gate: raise step 01 cathode pulse (shear) and noise fraction; "
                    "re-cache OFF+ON pair."
                )
            elif not ok_ci:
                gate = (
                    f"Gate: laminar-ON clump {ci:.2f} > 2.8 — on step 01 raise "
                    "Cathode pulse / shear (I/K), then re-cache OFF+ON."
                )
            else:
                gate = (
                    f"Gate: OFF/ON ratio {red:.2f}× < 1.25× — raise noise fraction or "
                    "step 01 pulse; lower ON clump with higher shear."
                )
            self.gate.set_gate(gate, ok=ok)
        else:
            self.gate.set_gate(self._gate_hint, ok=None)


class Step04FuelingPanel(ProofStepPanel):
    def __init__(self, state: ProofSuiteState, parent=None) -> None:
        super().__init__(
            "04",
            "Fueling → densities",
            "H₂ sccm (proton inventory) + laser ablation Hz (solid ¹¹B delivery) at ignited pad point; "
            "PIC ρ_e_norm scales confinement. No borane gas path — see ``injectants.py``.",
            "Finite n_p, n_B; T_i from 600 kV class; τ and bore volume explicit in fusion_pb11.",
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
            "Volume-integrated ⟨σv⟩ power at proof settings (fusion_reactivity_scale = 1). "
            "Shortfall vs 3.5 MW headline is expected in Tier-2/3 — record gap, do not tune knobs.",
            "Honest P_fusion documented; shortfall_mw is a design margin signal, not failure to hide.",
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
