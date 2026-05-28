#!/usr/bin/env python3
"""Build CORE-01 layer-by-layer assembly movie (peel screenshots + ChatTTS narration)."""
from __future__ import annotations

import logging
import os
import subprocess
import math
import re
from pathlib import Path
from typing import NamedTuple

import numpy as np
import scipy.io.wavfile as wavfile
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PEEL_DIR = REPO / "ssto" / "orbitron" / "media" / "core01_peel_frames"
_CHAT_STATE: dict[str, object] = {}
CHAT_VOICE_SEED = 1983
CHAT_SPEED_LEVEL = 1
_DIGIT_WORDS = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}

# User-curated peel sequence (outer -> inner) from chat attachments.
PEEL_SEQUENCE = [
    "image-c1a22670-2f8e-4db5-a055-ef1f288e9df8.png",
    "image-f295f5c5-aa00-4b0f-a45d-cb84bc913f90.png",
    "image-dcdab1c0-f8c6-4fc8-a39f-334f5c25a313.png",
    "image-515e4774-2de6-47d9-a0fc-18b472212bb3.png",
    "image-f1f7f5b6-122d-42bc-9a87-5824d6b1c787.png",
    "image-afea6560-5934-43a6-a278-d9b5482b6a83.png",
    "image-7a03621d-ff67-4387-87cf-53cc65bc0775.png",
    "image-98ca6c52-d2cb-403e-9b41-2c04b2fa5b76.png",
    "image-c62e9292-c866-4616-9af7-3d9eb8e8d6d7.png",
    "image-c0a2afb3-cce1-4296-aa05-5b7367f5c2b2.png",
    "image-c28a2d68-910d-4e16-be0f-f9623cea4db9.png",
    "image-32ff82b6-6107-4ef9-b640-14fd816f9f23.png",
    "image-2f61d1a1-be5c-445d-bfea-1a7eee2a7e42.png",
    "image-d4acc4d0-5bb3-43eb-83c9-8c0dc8b7995b.png",
]

# Build order is reverse of peel.
BUILD_SEQUENCE = list(reversed(PEEL_SEQUENCE))

COMMENTARY = [
    "Step 1: Begin with innermost hardware and feedthrough stubs.",
    "Step 2: Add central cathode path through insulator stack.",
    "Step 3: Extend on-axis electrode and support sleeves.",
    "Step 4: Add core spacer and feedthrough collars.",
    "Step 5: Add inner confinement tube around cathode path.",
    "Step 6: Add first structured support bands.",
    "Step 7: Add first-wall/anode boundary tube section.",
    "Step 8: Add longer first-wall body segment.",
    "Step 9: Add cryostat-side sleeve around the hot wall.",
    "Step 10: Add annulus boundary section toward reactor mid-body.",
    "Step 11: Add upstream coupling hardware.",
    "Step 12: Add external jacket and service interface pieces.",
    "Step 13: Add remaining outer body and coupler shells.",
    "This is the final CORE-01 assembly view.",
]

# After this build-step index (0-based), show radial/axial callout for one thermal zone.
# 14 Blender peel frames map to mechanical assembly steps; only five frames get a zone
# callout when narration text best matches that radial layer (not 1:1 per frame).
LAYER_CALLOUT_AFTER_STEP: dict[int, str] = {
    1: "Central_Cathode_Wire",  # Step 2: cathode path
    6: "Outer_Anode_Grid",  # Step 7: first-wall / anode boundary
    9: "Air_Annulus_Channel",  # Step 10: annulus boundary
    10: "Cryostat_Vacuum_Gap",  # Step 11: outer coupling / jacket region
    12: "Magnet",  # Step 13: outer body shells
}
LAYER_ORDER = (
    "Central_Cathode_Wire",
    "Outer_Anode_Grid",
    "Air_Annulus_Channel",
    "Cryostat_Vacuum_Gap",
    "Magnet",
)
LAYER_COLORS = {
    "Central_Cathode_Wire": "#6b7280",
    "Outer_Anode_Grid": "#ef4444",
    "Air_Annulus_Channel": "#38bdf8",
    "Cryostat_Vacuum_Gap": "#a8a29e",
    "Magnet": "#1d4ed8",
}


class Segment(NamedTuple):
    image: Image.Image
    note: str
    hold_frames: int
    is_step: bool


def peel_frames_dir(*, repo: Path | None = None) -> Path:
    """SSOT peel screenshots (tracked under ``ssto/orbitron/media/``)."""
    override = os.environ.get("CORE01_PEEL_FRAMES", "").strip()
    if override:
        return Path(override)
    root = repo if repo is not None else REPO
    return root / "ssto" / "orbitron" / "media" / "core01_peel_frames"


def media_paths(*, report_dir: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
    """Work files under ``report_dir/.core01-movie-work/``; finals in ``figures/assemblies/``."""
    report_dir = report_dir.resolve()
    work = report_dir / ".core01-movie-work"
    assemblies = report_dir / "figures" / "assemblies"
    assemblies.mkdir(parents=True, exist_ok=True)
    return (
        work,
        work / "frames",
        assemblies / "CORE-01_layered_build.mp4",
        assemblies / "CORE-01_layered_build.webm",
        work / "mute.mp4",
        work / "narration.wav",
    )


def _newest_mtime(paths: list[Path]) -> float:
    mt = 0.0
    for p in paths:
        if p.is_file():
            mt = max(mt, p.stat().st_mtime)
        elif p.is_dir():
            for child in p.rglob("*"):
                if child.is_file():
                    mt = max(mt, child.stat().st_mtime)
    return mt


def _write_webm_preview(out_mp4: Path, out_webm: Path) -> None:
    """VP8 + Vorbis WebM for VS Code/Cursor Markdown preview (no AAC in embedded webviews)."""
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(out_mp4),
            "-c:v",
            "libvpx",
            "-b:v",
            "1.5M",
            "-c:a",
            "libvorbis",
            "-q:a",
            "4",
            str(out_webm),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _ensure_webm_preview(out_mp4: Path, out_webm: Path, *, force: bool = False) -> None:
    if not out_mp4.is_file():
        return
    if (
        not force
        and out_webm.is_file()
        and out_webm.stat().st_mtime >= out_mp4.stat().st_mtime
    ):
        return
    _write_webm_preview(out_mp4, out_webm)


def ensure_core01_build_movie(
    report_dir: Path,
    *,
    repo: Path | None = None,
    force: bool = False,
) -> Path | None:
    """Build or refresh MP4 + WebM preview under ``<report_dir>/figures/assemblies/``."""
    report_dir = report_dir.resolve()
    _, _, out_mp4, out_webm, _, _ = media_paths(report_dir=report_dir)
    if os.environ.get("SKIP_CORE01_MOVIE", "").strip().lower() in ("1", "true", "yes"):
        return out_mp4 if out_mp4.is_file() else None
    frames_dir = peel_frames_dir(repo=repo)
    missing = [name for name in PEEL_SEQUENCE if not (frames_dir / name).is_file()]
    if missing:
        logger.warning(
            "CORE-01 movie skipped: missing %d peel frame(s) under %s (first: %s)",
            len(missing),
            frames_dir,
            missing[0],
        )
        return None
    script = Path(__file__).resolve()
    deps = [script, *[frames_dir / name for name in PEEL_SEQUENCE]]
    if out_mp4.is_file() and not force and out_mp4.stat().st_mtime >= _newest_mtime(deps):
        _ensure_webm_preview(out_mp4, out_webm, force=force)
        return out_mp4
    try:
        built = build_movie(report_dir=report_dir, repo=repo)
        _ensure_webm_preview(built, out_webm, force=True)
        return built
    except Exception:
        logger.exception("CORE-01 layered build movie failed for %s", report_dir)
        if out_mp4.is_file():
            _ensure_webm_preview(out_mp4, out_webm, force=force)
        return out_mp4 if out_mp4.is_file() else None


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _overlay_frame(src: Path, idx: int, total: int, note: str) -> Image.Image:
    """Crop to CORE-01 stack, then draw labels below the image (no overlay)."""
    raw = Image.open(src).convert("RGB")
    w0, h0 = raw.size
    # Remove left-side coupler/feedthrough clutter and keep the reactor stack body.
    crop_x0 = int(w0 * 0.22)
    core = raw.crop((crop_x0, 0, w0, h0))
    w, h = core.size
    pad = max(12, w // 110)
    footer_h = max(78, h // 2)
    canvas = Image.new("RGB", (w, h + footer_h), (8, 12, 20))
    canvas.paste(core, (0, 0))
    draw = ImageDraw.Draw(canvas)

    title_font = _font(max(20, w // 55))
    body_font = _font(max(15, w // 78))
    meta_font = _font(max(13, w // 90))

    draw.text((pad, h + 8), "CORE-01 layered assembly build", fill=(230, 237, 246), font=title_font)
    draw.text((pad, h + 38), note, fill=(224, 231, 239), font=body_font)
    draw.text(
        (w - pad - 260, h + footer_h - 24),
        f"Frame {idx + 1}/{total}  (inner -> outer)",
        fill=(147, 197, 253),
        font=meta_font,
    )
    return canvas


def _radial_callout_frame(layer_name: str, canvas_size: tuple[int, int]) -> Image.Image:
    """Compose radial cross-section slide with color-coded legend for layer callout narration."""
    w, h_total = canvas_size
    footer_h = max(78, h_total // 3)
    image_h = h_total - footer_h
    canvas = Image.new("RGB", (w, h_total), (8, 12, 20))
    top = Image.new("RGB", (w, image_h), (248, 250, 252))
    tdraw = ImageDraw.Draw(top)
    pad = max(14, w // 100)
    # Two columns: radial rings | legend (color swatches identify each layer).
    left_w = int(w * 0.48)
    legend_x0 = left_w + pad * 2
    diam = min(left_w - 2 * pad, image_h - 2 * pad)
    cx = pad + diam // 2
    cy = image_h // 2
    # Draw circles outer -> inner to keep true aspect ratio.
    radii = {
        "Magnet": 1.00,
        "Cryostat_Vacuum_Gap": 0.75,
        "Air_Annulus_Channel": 0.60,
        "Outer_Anode_Grid": 0.40,
        "Central_Cathode_Wire": 0.10,
    }
    for name in ("Magnet", "Cryostat_Vacuum_Gap", "Air_Annulus_Channel", "Outer_Anode_Grid", "Central_Cathode_Wire"):
        r = int((diam * 0.5) * radii[name])
        c = LAYER_COLORS[name]
        tdraw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c, outline=None)
    tdraw.text((pad, pad // 2), "Radial section", fill=(30, 41, 59), font=_font(max(13, w // 95)))

    legend_y = pad + 8
    leg_font = _font(max(14, w // 85))
    leg_font_hi = _font(max(15, w // 78))
    display_name = layer_name.replace("_", " ")
    for i, lname in enumerate(LAYER_ORDER):
        row_y = legend_y + i * (leg_font.size + 12)
        color = LAYER_COLORS[lname]
        tdraw.rectangle((legend_x0, row_y + 3, legend_x0 + 14, row_y + 17), fill=color)
        marker = ">> " if lname == layer_name else "   "
        label = f"{marker}{lname.replace('_', ' ')}"
        tdraw.text(
            (legend_x0 + 22, row_y),
            label,
            fill=color if lname == layer_name else (71, 85, 105),
            font=leg_font_hi if lname == layer_name else leg_font,
        )
    canvas.paste(top, (0, 0))

    draw = ImageDraw.Draw(canvas)
    pad = max(12, w // 110)
    title_font = _font(max(20, w // 55))
    body_font = _font(max(16, w // 76))
    draw.text((pad, image_h + 8), "CORE-01 radial layer callout", fill=(230, 237, 246), font=title_font)
    draw.text(
        (pad, image_h + 40),
        f"This is layer {display_name} of the core.",
        fill=(224, 231, 239),
        font=body_font,
    )
    return canvas


def _blend_frames(a: Image.Image, b: Image.Image, n: int) -> list[Image.Image]:
    if n <= 0:
        return []
    out: list[Image.Image] = []
    for k in range(1, n + 1):
        alpha = k / (n + 1)
        out.append(Image.blend(a, b, alpha))
    return out


def _chattts_state() -> dict[str, object]:
    state = _CHAT_STATE.get("state")
    if isinstance(state, dict):
        return state
    import ChatTTS
    import torch

    chat = ChatTTS.Chat()
    if not chat.load(source="huggingface"):
        raise RuntimeError("ChatTTS model load failed")
    torch.manual_seed(CHAT_VOICE_SEED)
    spk_emb = chat.sample_random_speaker()
    infer = chat.InferCodeParams(spk_emb=spk_emb, prompt=f"[speed_{CHAT_SPEED_LEVEL}]")
    state = {"chat": chat, "infer": infer}
    _CHAT_STATE["state"] = state
    return state


def _int_to_words(n: int) -> str:
    units = [
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
    ]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    if n < 20:
        return units[n]
    if n < 100:
        t, u = divmod(n, 10)
        return tens[t] if u == 0 else f"{tens[t]} {units[u]}"
    if n < 1000:
        h, r = divmod(n, 100)
        return f"{units[h]} hundred" if r == 0 else f"{units[h]} hundred { _int_to_words(r)}"
    if n < 10000:
        th, r = divmod(n, 1000)
        return f"{units[th]} thousand" if r == 0 else f"{units[th]} thousand { _int_to_words(r)}"
    return " ".join(_DIGIT_WORDS[d] for d in str(n))


def _normalize_narration_text(note: str) -> str:
    txt = note.replace("_", " ")

    def repl(m: re.Match[str]) -> str:
        token = m.group(0)
        if len(token) > 1 and token.startswith("0"):
            return " ".join(_DIGIT_WORDS[d] for d in token)
        try:
            val = int(token)
        except ValueError:
            return token
        if 0 <= val < 10000:
            return _int_to_words(val)
        return " ".join(_DIGIT_WORDS[d] for d in token)

    txt = re.sub(r"\d+", repl, txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    # Add a tiny explicit pause after each sentence to prevent word clipping.
    txt = re.sub(r"([.!?])\s*", r"\1 [uv_break] ", txt).strip()
    return re.sub(r"\s+", " ", txt)


def _synthesize_chattts(note: str, out_wav: Path) -> None:
    state = _chattts_state()
    chat = state["chat"]
    infer = state["infer"]
    normalized = _normalize_narration_text(note)
    wavs = chat.infer([normalized], params_infer_code=infer)
    wav = np.asarray(wavs[0], dtype=np.float32)
    if wav.ndim > 1:
        wav = wav[0]
    wavfile.write(out_wav, 24000, wav)


def _probe_duration_seconds(path: Path) -> float:
    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nokey=1:noprint_wrappers=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        return float(out.stdout.strip())
    except Exception:
        return 0.0


def _measure_tts_seconds(text: str, idx: int, *, out_dir: Path) -> float:
    """Generate temporary ChatTTS audio and return its measured duration (seconds)."""
    seg_dir = out_dir / "audio_segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    speech = seg_dir / f"measure_{idx:03d}.wav"
    _synthesize_chattts(text, speech)
    return _probe_duration_seconds(speech)


def _build_narration_track(
    items: list[tuple[str, float]],
    out_wav: Path,
    *,
    out_dir: Path,
    tail_silence_s: float = 0.0,
) -> None:
    """Synthesize commentary audio with ChatTTS and concat with per-item pacing."""
    seg_dir = out_dir / "audio_segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    concat = seg_dir / "concat.txt"
    rows: list[str] = []
    for i, (note, dur_s) in enumerate(items):
        speech = seg_dir / f"speech_{i:03d}.wav"
        paced = seg_dir / f"paced_{i:03d}.wav"
        _synthesize_chattts(note, speech)
        # Pad/truncate each segment to exact visual segment duration for sync.
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(speech),
                "-af",
                f"apad=pad_dur={dur_s},atrim=duration={dur_s}",
                str(paced),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        rows.append(f"file '{paced.as_posix()}'")
    if tail_silence_s > 0.0:
        silence = seg_dir / "tail_silence.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=16000:cl=mono",
                "-t",
                str(tail_silence_s),
                str(silence),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        rows.append(f"file '{silence.as_posix()}'")
    concat.write_text("\n".join(rows) + "\n", encoding="utf-8")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            str(out_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def build_movie(*, report_dir: Path, repo: Path | None = None) -> Path:
    assets = peel_frames_dir(repo=repo)
    out_dir, frames_dir, out_mp4, _out_webm, out_mute_mp4, out_wav = media_paths(
        report_dir=report_dir
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    hold_frames = 84  # ~2.8 s at 30 fps
    pause_frames = 45  # 1.5 s pause between steps at 30 fps
    pre_callout_pause_frames = 30  # 1.0 s pause before switching to radial/axial callout
    callout_silence_s = 1.5  # requested pause after layer-name readout
    fade_frames = 18  # ~0.6 s
    end_pause_frames = 150  # 5.0 s pause before ending
    fps = 30

    annotated: list[Image.Image] = []
    for i, name in enumerate(BUILD_SEQUENCE):
        src = assets / name
        if not src.is_file():
            raise FileNotFoundError(f"Missing input screenshot: {src}")
        note = COMMENTARY[i] if i < len(COMMENTARY) else f"Step {i + 1}"
        annotated.append(_overlay_frame(src, i, len(BUILD_SEQUENCE), note))

    segments: list[Segment] = []
    measure_idx = 0
    canvas_size: tuple[int, int] | None = None
    for i, step_img in enumerate(annotated):
        canvas_size = (step_img.width, step_img.height)
        step_note = COMMENTARY[i] if i < len(COMMENTARY) else f"Step {i + 1}"
        step_tts_s = _measure_tts_seconds(step_note, measure_idx, out_dir=out_dir)
        measure_idx += 1
        # Ensure visuals never cut off spoken words; keep baseline hold as a minimum.
        step_hold_frames = max(hold_frames, math.ceil((step_tts_s + 0.35) * fps))
        # 1) Show the 3D build state with the new piece added.
        segments.append(Segment(step_img, step_note, step_hold_frames, True))
        # 2) Immediately after, cross-section callout for the matching radial layer.
        layer = LAYER_CALLOUT_AFTER_STEP.get(i)
        if layer:
            callout_note = f"This is layer {layer} of the core."
            tts_s = _measure_tts_seconds(callout_note, measure_idx, out_dir=out_dir)
            measure_idx += 1
            callout_hold_frames = max(1, math.ceil((tts_s + callout_silence_s) * fps))
            segments.append(
                Segment(
                    _radial_callout_frame(layer, canvas_size),
                    callout_note,
                    callout_hold_frames,
                    False,
                )
            )

    frames: list[Path] = []
    audio_items: list[tuple[str, float]] = []
    frame_idx = 0
    for i, seg in enumerate(segments):
        cur = seg.image
        for _ in range(seg.hold_frames):
            dst = frames_dir / f"frame_{frame_idx:04d}.png"
            cur.save(dst)
            frames.append(dst)
            frame_idx += 1
        seg_total = seg.hold_frames
        nxt = segments[i + 1] if i + 1 < len(segments) else None
        # Pause only between two consecutive 3D build steps (not before a callout slide).
        if seg.is_step and nxt is not None and nxt.is_step:
            for _ in range(pause_frames):
                dst = frames_dir / f"frame_{frame_idx:04d}.png"
                cur.save(dst)
                frames.append(dst)
                frame_idx += 1
            seg_total += pause_frames
        # Keep at least 1 second before cutting from build step to callout slide.
        if seg.is_step and nxt is not None and not nxt.is_step:
            for _ in range(pre_callout_pause_frames):
                dst = frames_dir / f"frame_{frame_idx:04d}.png"
                cur.save(dst)
                frames.append(dst)
                frame_idx += 1
            seg_total += pre_callout_pause_frames
        if i < len(segments) - 1:
            nxt = segments[i + 1].image
            for blended in _blend_frames(cur, nxt, fade_frames):
                dst = frames_dir / f"frame_{frame_idx:04d}.png"
                blended.save(dst)
                frames.append(dst)
                frame_idx += 1
            seg_total += fade_frames
        audio_items.append((seg.note, seg_total / fps))

    # Final 5-second visual pause on completed assembly.
    final_frame = segments[-1].image
    for _ in range(end_pause_frames):
        dst = frames_dir / f"frame_{frame_idx:04d}.png"
        final_frame.save(dst)
        frames.append(dst)
        frame_idx += 1

    _build_narration_track(
        audio_items,
        out_wav,
        out_dir=out_dir,
        tail_silence_s=end_pause_frames / fps,
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%04d.png"),
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
        "-movflags",
        "+faststart",
        str(out_mute_mp4),
    ]
    subprocess.run(cmd, check=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(out_mute_mp4),
            "-i",
            str(out_wav),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-shortest",
            str(out_mp4),
        ],
        check=True,
    )
    return out_mp4


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report_dir",
        type=Path,
        help="Experiment run directory (writes figures/assemblies/CORE-01_layered_build.mp4)",
    )
    parser.add_argument("--force", action="store_true", help="Rebuild even if MP4 is up to date")
    args = parser.parse_args()
    out = ensure_core01_build_movie(args.report_dir.resolve(), force=args.force)
    if out is None:
        raise SystemExit(1)
    print(out)
