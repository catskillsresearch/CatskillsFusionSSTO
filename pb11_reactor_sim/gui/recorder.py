"""
Capture GUI frames to MP4 for presentation export.

Composites the spatial canvas and the diagnostics panel (temperature, power, Q)
into each frame. Writes via ``imageio`` when installed, otherwise falls back
to ``ffmpeg`` or a numbered PNG sequence.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from PySide6 import QtWidgets

from pb11_reactor_sim.gui.audio_synth import (
    FPS,
    FrameMeta,
    mix_tracks,
    pad_audio,
    synthesize_shot_audio,
    write_wav,
)
from pb11_reactor_sim.gui.chattts_narration import build_narration_track, narration_enabled

FPS = 30.0


class FrameRecorder:
    """Accumulates PNG frames; exports on :meth:`stop`."""

    def __init__(self) -> None:
        self._frames: list[bytes] = []
        self._meta: list[FrameMeta] = []
        self._reactor_name: str = ""
        self.active = False

    def start(self, *, reactor_name: str = "") -> None:
        self._frames.clear()
        self._meta.clear()
        self._reactor_name = reactor_name
        self.active = True

    def add_frame(
        self,
        png: bytes | None,
        *,
        phase: str = "",
        fast_forward: bool = False,
        intensity: float = 0.0,
    ) -> None:
        if self.active and png:
            self._frames.append(_normalize_png_for_video(png))
            self._meta.append(
                FrameMeta(phase=phase, fast_forward=fast_forward, intensity=intensity)
            )

    def add_png(self, png: bytes | None) -> None:
        """Legacy capture without phase metadata (silent/generic audio)."""
        self.add_frame(png)

    def stop(
        self,
        parent: QtWidgets.QWidget | None = None,
        *,
        default_name: str = "pb11_reactor_shot.mp4",
    ) -> tuple[str | None, str | None]:
        """Prompt for save path and write the movie.

        Returns ``(saved_path, error_message)``.
        """
        self.active = False
        if not self._frames:
            return None, None
        if not default_name.lower().endswith(".mp4"):
            default_name = f"{default_name}.mp4"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent,
            "Save simulation recording",
            str(Path.home() / default_name),
            "MP4 video (*.mp4);;PNG sequence (*.png)",
        )
        if not path:
            return None, None
        out = Path(path)
        if out.suffix.lower() == ".png":
            return self._write_png_sequence(out), None
        return self._write_mp4(out, parent=parent)

    def _write_mp4(
        self,
        path: Path,
        *,
        parent: QtWidgets.QWidget | None = None,
    ) -> tuple[str | None, str | None]:
        err = self._write_mp4_imageio(path)
        if err is None:
            return self._mux_shot_audio(path, parent=parent)

        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            ff_err = self._write_mp4_ffmpeg(path, ffmpeg)
            if ff_err is None:
                return self._mux_shot_audio(path, parent=parent)
            err = ff_err

        fallback = self._write_png_sequence(path.with_suffix(".png"))
        return fallback, (
            f"MP4 encode failed ({err}); saved PNG sequence instead:\n{fallback}"
        )

    def _mux_shot_audio(
        self,
        path: Path,
        *,
        parent: QtWidgets.QWidget | None = None,
    ) -> tuple[str | None, str | None]:
        """Add procedural bed + optional ChatTTS phase narration."""
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg or not self._meta:
            return str(path), None
        try:
            if parent is not None and narration_enabled():
                win = parent if isinstance(parent, QtWidgets.QMainWindow) else parent.window()
                if isinstance(win, QtWidgets.QMainWindow):
                    win.statusBar().showMessage("Synthesizing shot audio…")
                QtWidgets.QApplication.processEvents()

            bed = synthesize_shot_audio(self._meta, fps=FPS)
            if bed.size == 0:
                return str(path), None

            narr, audio_dur_s = build_narration_track(
                self._meta, reactor_name=self._reactor_name
            )
            if narr is not None and parent is not None:
                win = parent if isinstance(parent, QtWidgets.QMainWindow) else parent.window()
                if isinstance(win, QtWidgets.QMainWindow):
                    win.statusBar().showMessage("Generating ChatTTS phase callouts…")
                QtWidgets.QApplication.processEvents()

            n_samples = max(bed.size, narr.size if narr is not None else 0)
            bed = pad_audio(bed, n_samples)
            mixed = mix_tracks(bed, narr)

            video_dur_s = len(self._meta) / FPS
            pad_video_s = max(0.0, audio_dur_s - video_dur_s)

            with tempfile.TemporaryDirectory(prefix="pb11_mux_") as tmp:
                td = Path(tmp)
                wav = td / "shot.wav"
                out = td / "muxed.mp4"
                write_wav(wav, mixed)
                if pad_video_s > 0.05:
                    cmd = [
                        ffmpeg,
                        "-y",
                        "-i",
                        str(path),
                        "-i",
                        str(wav),
                        "-filter_complex",
                        f"[0:v]tpad=stop_mode=clone:stop_duration={pad_video_s:.3f}[v]",
                        "-map",
                        "[v]",
                        "-map",
                        "1:a",
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "-c:a",
                        "aac",
                        "-b:a",
                        "192k",
                        str(out),
                    ]
                else:
                    cmd = [
                        ffmpeg,
                        "-y",
                        "-i",
                        str(path),
                        "-i",
                        str(wav),
                        "-c:v",
                        "copy",
                        "-c:a",
                        "aac",
                        "-b:a",
                        "192k",
                        "-shortest",
                        str(out),
                    ]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.returncode != 0:
                    detail = (proc.stderr or proc.stdout or "").strip()[-400:]
                    return str(path), f"Audio mux skipped ({detail})"
                out.replace(path)

            return str(path), None
        except Exception as exc:  # noqa: BLE001
            return str(path), f"Audio mux skipped ({exc})"

    def _write_mp4_imageio(self, path: Path) -> str | None:
        try:
            import imageio.v3 as iio  # type: ignore[import-untyped]
            import numpy as np
            from PIL import Image

            imgs = [np.asarray(Image.open(BytesIO(png))) for png in self._frames]
            iio.imwrite(path, imgs, fps=30, codec="libx264")
            return None
        except ImportError:
            return "imageio/Pillow not installed"
        except Exception as exc:  # noqa: BLE001
            return f"imageio: {exc}"

    def _write_mp4_ffmpeg(self, path: Path, ffmpeg: str) -> str | None:
        with tempfile.TemporaryDirectory(prefix="pb11_frames_") as tmp:
            td = Path(tmp)
            for i, png in enumerate(self._frames):
                (td / f"frame_{i:05d}.png").write_bytes(png)
            cmd = [
                ffmpeg,
                "-y",
                "-framerate",
                "30",
                "-i",
                str(td / "frame_%05d.png"),
                # Qt widget grabs are often odd-sized; libx264/yuv420p needs even dims.
                "-vf",
                "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                "-pix_fmt",
                "yuv420p",
                str(path),
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                return None
            detail = (proc.stderr or proc.stdout or "").strip()
            tail = detail[-800:] if len(detail) > 800 else detail
            return f"ffmpeg exit {proc.returncode}: {tail}"

    def _write_png_sequence(self, path: Path) -> str:
        """Write ``stem_00000.png`` … next to ``path`` when MP4 encode fails."""
        stem = path.with_suffix("")
        stem.parent.mkdir(parents=True, exist_ok=True)
        for i, png in enumerate(self._frames):
            (stem.parent / f"{stem.name}_{i:05d}.png").write_bytes(png)
        return str(stem.parent / f"{stem.name}_00000.png")


def compose_png_horizontal(
    left: bytes | None,
    right: bytes | None,
) -> bytes | None:
    """Stitch two PNG snapshots side by side (canvas left, diagnostics right)."""
    if not left and not right:
        return None
    if not left:
        return right
    if not right:
        return left
    try:
        from PIL import Image

        a = Image.open(BytesIO(left)).convert("RGB")
        b = Image.open(BytesIO(right)).convert("RGB")
        h = a.height
        bw = max(1, int(round(b.width * h / b.height)))
        b = b.resize((bw, h), Image.Resampling.LANCZOS)
        out = Image.new("RGB", (a.width + bw, h))
        out.paste(a, (0, 0))
        out.paste(b, (a.width, 0))
        buf = BytesIO()
        out.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        return left


def _normalize_png_for_video(png: bytes) -> bytes:
    """Crop to even width/height so H.264 encoders accept the frames."""
    try:
        from PIL import Image

        img = Image.open(BytesIO(png)).convert("RGB")
        w, h = img.size
        ew, eh = w - (w % 2), h - (h % 2)
        if ew < 2 or eh < 2:
            return png
        if (ew, eh) != (w, h):
            img = img.crop((0, 0, ew, eh))
        out = BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    except ImportError:
        return png
