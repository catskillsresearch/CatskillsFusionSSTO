"""Background workers for long proof-chain steps."""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from ssto.orbitron.simulator.proof_chain.runners import (
    build_warpx_command,
    list_pic_plotfiles,
    load_config,
    save_step,
)
from ssto.orbitron.simulator.warpx_env import apply_warpx_env, ensure_warpx_env, warpx_env_summary


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


class WarpXWorker(QThread):
    """Run WarpX with live stdout/stderr streamed to the GUI."""

    log_line = Signal(str)
    finished = Signal(object, object)  # result dict | None, error str | None

    def __init__(self, *, skip_pic: bool = False, n_steps: int | None = None) -> None:
        super().__init__()
        self._skip = skip_pic
        self._n_steps = n_steps

    def run(self) -> None:
        if self._skip or os.environ.get("SKIP_PIC", "0") == "1":
            save_step("01", {"skipped": True, "reason": "SKIP_PIC"})
            self.log_line.emit("SKIP_PIC=1 — skipping WarpX.\n")
            self.finished.emit(load_step_json_safe("01"), None)
            return

        try:
            ensure_warpx_env()
            cfg = load_config()
            cmd, cwd, diags, n_cleared = build_warpx_command(cfg, n_steps=self._n_steps)
            pad = cfg["pad"]
            env = apply_warpx_env()
            self.log_line.emit(warpx_env_summary() + "\n\n")
            if n_cleared:
                self.log_line.emit(
                    f"Cleared {n_cleared} old density_diag plotfile(s) under {diags}\n"
                )
            self.log_line.emit(f"Command: {' '.join(cmd)}\n")
            self.log_line.emit(f"Working directory: {cwd}\n")
            self.log_line.emit("— WarpX output —\n")
            t0 = time.monotonic()
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                self.log_line.emit(line.rstrip("\n"))
            rc = proc.wait()
            elapsed = time.monotonic() - t0
            self.log_line.emit(f"\n— finished in {elapsed:.1f} s (exit {rc}) —\n")
            if rc != 0:
                save_step("01", {"ok": False, "returncode": rc})
                self.finished.emit(None, f"WarpX exited with code {rc}")
                return
            plotfiles = [p.name for p in list_pic_plotfiles(diags)]
            self.log_line.emit(f"Plotfiles: {len(plotfiles)}\n")
            save_step(
                "01",
                {
                    "diags_dir": str(diags),
                    "plotfiles": plotfiles,
                    "ring_density_scale": pad["throttle"],
                    "cathode_pulse": pad["cathode_pulse"],
                    "electron_ring_only": True,
                    "n_steps": self._n_steps or int(cfg["pic"]["steps"]),
                    "elapsed_s": elapsed,
                },
            )
            from ssto.orbitron.simulator.proof_chain.runners import load_step_json

            self.finished.emit(load_step_json("01"), None)
        except Exception as exc:
            self.finished.emit(None, str(exc))


def load_step_json_safe(step: str) -> dict:
    from ssto.orbitron.simulator.proof_chain.runners import load_step_json

    return load_step_json(step)


class CoupledPlasmaWorker(QThread):
    """
    Run steps 01 → 02 → 03 (OFF+ON cache) as one atomic unit.
    Emits log_line during WarpX; finished carries combined result dict.
    """

    log_line = Signal(str)
    finished = Signal(object, object)

    def __init__(
        self,
        *,
        skip_pic: bool = False,
        n_steps: int | None = None,
    ) -> None:
        super().__init__()
        self._skip_pic = skip_pic
        self._n_steps = n_steps

    def run(self) -> None:
        from ssto.orbitron.simulator.proof_chain.runners import (
            load_step_json,
            run_step_02,
            run_step_03_compare_pair,
        )
        from ssto.orbitron.simulator.proof_suite.coupled_fingerprint import (
            coupled_run_fingerprint,
            save_coupled_fingerprint,
        )

        try:
            cfg = load_config()
            fp = coupled_run_fingerprint(cfg)
            self.log_line.emit("=== Coupled plasma chain 01 → 02 → 03 ===\n")
            self.log_line.emit(f"Fingerprint: τ={fp['throttle']:.3f} p={fp['cathode_pulse']:.3f} "
                               f"H₂={fp['h2_sccm']:.1f} laser={fp['laser_ablation_hz']:.1f}\n\n")

            if self._skip_pic or os.environ.get("SKIP_PIC", "0") == "1":
                save_step("01", {"skipped": True, "reason": "SKIP_PIC"})
                self.log_line.emit("Step 01: SKIP_PIC\n")
            else:
                ensure_warpx_env()
                cmd, cwd, diags, n_cleared = build_warpx_command(
                    cfg, n_steps=self._n_steps
                )
                pad = cfg["pad"]
                env = apply_warpx_env()
                self.log_line.emit(warpx_env_summary() + "\n\n")
                if n_cleared:
                    self.log_line.emit(
                        f"Cleared {n_cleared} old plotfile(s) under {diags}\n"
                    )
                self.log_line.emit(f"Step 01 WarpX: {' '.join(cmd)}\n")
                t0 = time.monotonic()
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(cwd),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                assert proc.stdout is not None
                for line in proc.stdout:
                    self.log_line.emit(line.rstrip("\n"))
                rc = proc.wait()
                elapsed = time.monotonic() - t0
                self.log_line.emit(f"\nStep 01 finished in {elapsed:.1f} s (exit {rc})\n")
                if rc != 0:
                    save_step("01", {"ok": False, "returncode": rc})
                    self.finished.emit(
                        None, f"WarpX exited with code {rc} — steps 02–03 not run."
                    )
                    return
                plotfiles = [p.name for p in list_pic_plotfiles(diags)]
                save_step(
                    "01",
                    {
                        "diags_dir": str(diags),
                        "plotfiles": plotfiles,
                        "ring_density_scale": pad["throttle"],
                        "cathode_pulse": pad["cathode_pulse"],
                        "electron_ring_only": True,
                        "n_steps": self._n_steps or int(cfg["pic"]["steps"]),
                        "coupled_fingerprint": fp,
                    },
                )

            self.log_line.emit("\nStep 02: reduce ρ_e_norm…\n")
            p2 = run_step_02()
            self.log_line.emit(f"  ρ_e_norm = {p2.get('rho_e_norm')}\n")

            self.log_line.emit("\nStep 03: fusion channel OFF+ON pair…\n")
            p3 = run_step_03_compare_pair()
            self.log_line.emit(
                f"  clump ON={p3.get('clump_index_final')} OFF={p3.get('clump_index_off')} "
                f"ratio={p3.get('clump_reduction_ratio'):.2f}×\n"
            )

            cfg = load_config()
            save_coupled_fingerprint(cfg)
            from tools.orbitron_proof_chain.chain_lib import save_config

            save_config(cfg)

            self.finished.emit(
                {
                    "01": load_step_json("01"),
                    "02": load_step_json("02"),
                    "03": load_step_json("03"),
                    "fingerprint": fp,
                },
                None,
            )
        except Exception as exc:
            self.finished.emit(None, str(exc))
