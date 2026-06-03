"""
Capture GUI frames to MP4 for presentation export.

Uses in-memory PNG grabs from :class:`~pb11_reactor_sim.gui.canvas.ReactorCanvas`.
Writes via ``imageio`` when installed, otherwise falls back to ``ffmpeg`` or a
numbered PNG sequence.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PySide6 import QtWidgets


class FrameRecorder:
    """Accumulates PNG frames; exports on :meth:`stop`."""

    def __init__(self) -> None:
        self._frames: list[bytes] = []
        self.active = False

    def start(self) -> None:
        self._frames.clear()
        self.active = True

    def add_png(self, png: bytes | None) -> None:
        if self.active and png:
            self._frames.append(png)

    def stop(self, parent: QtWidgets.QWidget | None = None) -> str | None:
        """Prompt for save path and write the movie. Returns path or ``None``."""
        self.active = False
        if not self._frames:
            return None
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent,
            "Save simulation recording",
            str(Path.home() / "pb11_reactor_shot.mp4"),
            "MP4 video (*.mp4);;PNG sequence (*.png)",
        )
        if not path:
            return None
        out = Path(path)
        if out.suffix.lower() == ".png":
            return self._write_png_sequence(out)
        return self._write_mp4(out)

    def _write_mp4(self, path: Path) -> str | None:
        try:
            import imageio.v3 as iio  # type: ignore[import-untyped]
            import numpy as np
            from io import BytesIO
            from PIL import Image

            imgs = []
            for png in self._frames:
                imgs.append(np.asarray(Image.open(BytesIO(png))))
            iio.imwrite(path, imgs, fps=30, codec="libx264")
            return str(path)
        except ImportError:
            pass

        if shutil.which("ffmpeg"):
            return self._write_mp4_ffmpeg(path)
        return self._write_png_sequence(path.with_suffix(".png"))

    def _write_mp4_ffmpeg(self, path: Path) -> str | None:
        with tempfile.TemporaryDirectory(prefix="pb11_frames_") as tmp:
            td = Path(tmp)
            for i, png in enumerate(self._frames):
                (td / f"frame_{i:05d}.png").write_bytes(png)
            cmd = [
                "ffmpeg",
                "-y",
                "-framerate",
                "30",
                "-i",
                str(td / "frame_%05d.png"),
                "-pix_fmt",
                "yuv420p",
                str(path),
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        return str(path)

    def _write_png_sequence(self, path: Path) -> str:
        """Write ``stem_00000.png`` … next to ``path`` when no MP4 backend exists."""
        stem = path.with_suffix("")
        stem.parent.mkdir(parents=True, exist_ok=True)
        for i, png in enumerate(self._frames):
            (stem.parent / f"{stem.name}_{i:05d}.png").write_bytes(png)
        return str(stem.parent / f"{stem.name}_00000.png")
