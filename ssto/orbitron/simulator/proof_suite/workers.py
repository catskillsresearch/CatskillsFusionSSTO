"""Background workers for long proof-chain steps."""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from ssto.orbitron.simulator.proof_chain.runners import build_warpx_command, load_config, save_step


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
            cfg = load_config()
            cmd, cwd, diags = build_warpx_command(cfg, n_steps=self._n_steps)
            pad = cfg["pad"]
            self.log_line.emit(f"Command: {' '.join(cmd)}\n")
            self.log_line.emit(f"Working directory: {cwd}\n")
            self.log_line.emit("— WarpX output —\n")
            t0 = time.monotonic()
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
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
            plotfiles = [p.name for p in sorted(diags.glob("density_diag*"))]
            self.log_line.emit(f"Plotfiles: {len(plotfiles)}\n")
            save_step(
                "01",
                {
                    "diags_dir": str(diags),
                    "plotfiles": plotfiles,
                    "throttle": pad["throttle"],
                    "compressor": pad["compressor"],
                    "cathode_pulse": pad["cathode_pulse"],
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
