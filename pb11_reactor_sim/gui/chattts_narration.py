"""
ChatTTS voice narration for reactor shot MP4 export.

Pattern matches ``scripts/make_core01_build_movie.py``: lazy model load,
normalized callout text, one spoken line at each new shot phase. Lines are
scheduled sequentially so callouts never overlap; the audio track (and video,
if needed) extends to fit.
"""
from __future__ import annotations

import logging
import os
import re

import numpy as np

from pb11_reactor_sim.gui.audio_synth import FPS, SAMPLE_RATE, FrameMeta
from pb11_reactor_sim.gui.narration_scripts import PHASE_NARRATION

logger = logging.getLogger(__name__)

CHAT_SAMPLE_RATE = 24_000
CHAT_VOICE_SEED = 1983
CHAT_SPEED_LEVEL = 1
#: Silence between consecutive phase callouts [s].
NARRATION_GAP_S = 0.45

_CHAT_STATE: dict[str, object] = {}

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


def narration_enabled() -> bool:
    return os.environ.get("PB11_SKIP_NARRATION", "").strip().lower() not in ("1", "true", "yes")


def phase_segments(meta: list[FrameMeta]) -> list[tuple[str, int, int]]:
    """Return ``(phase_key, start_frame, end_frame_exclusive)`` runs."""
    if not meta:
        return []
    out: list[tuple[str, int, int]] = []
    cur = meta[0].phase
    start = 0
    for i, m in enumerate(meta[1:], 1):
        if m.phase != cur:
            out.append((cur, start, i))
            cur = m.phase
            start = i
    out.append((cur, start, len(meta)))
    return out


def build_narration_track(
    meta: list[FrameMeta],
    *,
    reactor_name: str,
    fps: float = FPS,
    sample_rate: int = SAMPLE_RATE,
) -> tuple[np.ndarray | None, float]:
    """Synthesize phase callouts without overlap.

    Returns ``(mono float32 audio, duration_seconds)``. Each line starts at
    the later of its phase boundary or the end of the previous callout (+ gap).
    """
    if not narration_enabled() or not meta:
        return None, len(meta) / fps

    scripts = PHASE_NARRATION.get(reactor_name, PHASE_NARRATION["TAE FRC"])
    video_samples = int(round(len(meta) / fps * sample_rate))
    if video_samples <= 0:
        return None, 0.0

    clips: list[tuple[int, np.ndarray]] = []
    cursor_s = 0.0
    placed = 0

    for phase, start_f, _end_f in phase_segments(meta):
        line = scripts.get(phase)
        if not line:
            continue
        try:
            speech = _resample(_synthesize_chattts(line), CHAT_SAMPLE_RATE, sample_rate)
        except Exception as exc:  # noqa: BLE001
            logger.warning("ChatTTS skipped for %r: %s", line[:60], exc)
            continue
        if speech.size == 0:
            continue
        segment_start_s = start_f / fps
        place_s = max(segment_start_s, cursor_s)
        offset = int(round(place_s * sample_rate))
        clips.append((offset, speech))
        placed += 1
        cursor_s = place_s + speech.size / sample_rate + NARRATION_GAP_S

    if placed == 0:
        return None, len(meta) / fps

    total_samples = max(video_samples, int(round(cursor_s * sample_rate)))
    track = np.zeros(total_samples, dtype=np.float32)
    for offset, speech in clips:
        end = min(total_samples, offset + speech.size)
        n = end - offset
        if n > 0:
            track[offset:end] += speech[:n]

    peak = float(np.max(np.abs(track)))
    if peak > 1e-6:
        track *= min(1.0, 0.95 / peak)
    return track, total_samples / sample_rate


def _chattts_state() -> dict[str, object]:
    state = _CHAT_STATE.get("state")
    if isinstance(state, dict):
        return state

    import ChatTTS  # type: ignore[import-untyped]
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
    units = (
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
    )
    tens = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
    if n < 20:
        return units[n]
    if n < 100:
        t, u = divmod(n, 10)
        return tens[t] if u == 0 else f"{tens[t]} {units[u]}"
    if n < 1000:
        h, r = divmod(n, 100)
        return f"{units[h]} hundred" if r == 0 else f"{units[h]} hundred {_int_to_words(r)}"
    if n < 10000:
        th, r = divmod(n, 1000)
        return f"{units[th]} thousand" if r == 0 else f"{units[th]} thousand {_int_to_words(r)}"
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
    txt = re.sub(r"([.!?])\s*", r"\1 [uv_break] ", txt).strip()
    return re.sub(r"\s+", " ", txt)


def _synthesize_chattts(note: str) -> np.ndarray:
    state = _chattts_state()
    chat = state["chat"]
    infer = state["infer"]
    normalized = _normalize_narration_text(note)
    wavs = chat.infer([normalized], params_infer_code=infer)
    wav = np.asarray(wavs[0], dtype=np.float32).squeeze()
    if wav.ndim != 1:
        wav = wav.reshape(-1)
    return wav


def _resample(wav: np.ndarray, from_rate: int, to_rate: int) -> np.ndarray:
    if from_rate == to_rate or wav.size == 0:
        return wav.astype(np.float32, copy=False)
    try:
        from scipy import signal

        n_out = int(round(wav.size * to_rate / from_rate))
        return signal.resample(wav, n_out).astype(np.float32)
    except ImportError:
        x_old = np.linspace(0.0, 1.0, wav.size, dtype=np.float64)
        n_out = int(round(wav.size * to_rate / from_rate))
        x_new = np.linspace(0.0, 1.0, n_out, dtype=np.float64)
        return np.interp(x_new, x_old, wav.astype(np.float64)).astype(np.float32)
