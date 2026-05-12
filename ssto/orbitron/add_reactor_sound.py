#!/usr/bin/env python3
"""
Synthesize Orbitron / arcjet test-stand audio assets.

Not part of the default mesh pipeline: run manually, prototype_build.sh --with-sounds, or `make` (writes to ../../Aircraft/Orbitron-TestStand/Sounds by default).

Outputs (mono 44.1 kHz, suitable for FlightGear <mode>looped</mode>):
  - orbitron_core_loop.wav           — fusion / core plasma bed
  - orbitron_inlet_loop.wav          — bellmouth + compressor ingestion
  - orbitron_jet_loop.wav            — nozzle / cell exhaust broadband
  - orbitron_dec_arc_loop.wav        — DEC / magnet bus arc crackle
  - orbitron_screen_sputter_loop.wav — beam on viewport / sputter hiss
  - orbitron_motor_whine_loop.wav    — battery motor + bleed / generator rise
  - orbitron_duct_heat_loop.wav      — heated air / duct turbulence
  - orbitron_stressor_loop.wav       — off-design moan (thermal vs thrust mismatch)

Legacy one-shot (10 s “commissioning” theatre):
  - reactor_audio_heavy.wav

Runtime mix (SpaceShuttle pattern): JSBSim system orbitron_soundscape writes
systems/orbitron_sfx/*_volume (0..1) from reactor + arcjet + environment; Sounds/sound.xml
binds volumes/pitches to these properties — reactive to user controls without a scripted timeline.
"""
from __future__ import annotations

import argparse
import os
import subprocess
from typing import Tuple

import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100


def _write_mono_wav(path: str, samples: np.ndarray) -> None:
    """samples float in [-1, 1], shape (n,) mono."""
    x = np.clip(samples.astype(np.float64), -1.0, 1.0)
    wavfile.write(path, SAMPLE_RATE, np.int16(x * 32767.0))


def _one_second_deterministic_texture(seed: int, weights: Tuple[float, ...]) -> np.ndarray:
    """Exactly one period at SAMPLE_RATE — seamless loop."""
    n = SAMPLE_RATE
    t = np.linspace(0.0, 1.0, n, endpoint=False)
    rng = np.random.default_rng(seed)
    out = np.zeros(n, dtype=np.float64)
    freqs = rng.integers(40, 2200, size=len(weights))
    for f, w in zip(freqs, weights):
        if w == 0:
            continue
        out += float(w) * np.sin(2.0 * np.pi * float(f) * t)
    return out


def build_core_loop() -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    # Electrical / magnet line + low “plasma” wash (integer Hz → seamless)
    core = (
        0.22 * np.sin(2 * np.pi * 60 * t)
        + 0.12 * np.sin(2 * np.pi * 120 * t)
        + 0.08 * np.sin(2 * np.pi * 180 * t)
        + 0.06 * np.sin(2 * np.pi * 240 * t)
    )
    core += 0.04 * _one_second_deterministic_texture(1, (1,) * 28)
    core += 0.025 * np.sin(2 * np.pi * 15 * t) * np.sin(2 * np.pi * 90 * t)
    return np.tanh(core * 2.2)


def build_inlet_loop() -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    # Mid/high “ingestion” texture (deterministic partials)
    hiss = 0.12 * _one_second_deterministic_texture(2, (1,) * 48)
    hiss += 0.08 * np.sin(2 * np.pi * 400 * t) * np.sin(2 * np.pi * 11 * t)
    hiss += 0.05 * np.sin(2 * np.pi * 1200 * t)
    return np.tanh(hiss * 2.8)


def build_jet_loop() -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    # Low broadband “nozzle / cell” rumble
    jet = (
        0.2 * np.sin(2 * np.pi * 55 * t)
        + 0.14 * np.sin(2 * np.pi * 73 * t)
        + 0.1 * np.sin(2 * np.pi * 97 * t)
        + 0.12 * np.sin(2 * np.pi * 31 * t) * np.sin(2 * np.pi * 140 * t)
    )
    jet += 0.08 * _one_second_deterministic_texture(3, (1,) * 22)
    return np.tanh(jet * 2.0)


def build_dec_arc_loop() -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    arc = 0.18 * np.sin(2 * np.pi * 120 * t) * np.sin(2 * np.pi * 37 * t)
    arc += 0.14 * _one_second_deterministic_texture(4, (1,) * 36)
    arc += 0.1 * np.sin(2 * np.pi * 240 * t) * np.sin(2 * np.pi * 7 * t)
    arc += 0.06 * np.sin(2 * np.pi * 1800 * t) * np.sin(2 * np.pi * 3 * t)
    return np.tanh(arc * 2.4)


def build_screen_sputter_loop() -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    # Sparse “impact” partials + HF hiss (MeV beam on glass / gas)
    sp = 0.1 * _one_second_deterministic_texture(5, (0,) * 60 + (1,) * 18)
    sp += 0.12 * np.sin(2 * np.pi * 2200 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 17 * t))
    sp += 0.08 * np.sin(2 * np.pi * 880 * t) * np.sin(2 * np.pi * 29 * t)
    return np.tanh(sp * 2.2)


def build_motor_whine_loop() -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    # Tonal motor + weak upper harmonics (pitch-shifted in FG from compressor)
    wh = (
        0.2 * np.sin(2 * np.pi * 220 * t)
        + 0.1 * np.sin(2 * np.pi * 440 * t)
        + 0.05 * np.sin(2 * np.pi * 660 * t)
    )
    wh += 0.04 * np.sin(2 * np.pi * 330 * t) * np.sin(2 * np.pi * 6.5 * t)
    wh += 0.03 * _one_second_deterministic_texture(6, (1,) * 12)
    return np.tanh(wh * 2.0)


def build_duct_heat_loop() -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    # Low-mid “roar” modulated by slow beat (heated air / secondary turbulence)
    dh = (
        0.16 * np.sin(2 * np.pi * 68 * t)
        + 0.12 * np.sin(2 * np.pi * 142 * t)
        + 0.1 * np.sin(2 * np.pi * 41 * t) * np.sin(2 * np.pi * 210 * t)
    )
    dh += 0.07 * _one_second_deterministic_texture(7, (1,) * 26)
    dh *= 0.85 + 0.15 * np.sin(2 * np.pi * 3 * t)
    return np.tanh(dh * 2.1)


def build_stressor_loop() -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    # Ominous sub + beating partials (off-design / thermal stress)
    st = (
        0.22 * np.sin(2 * np.pi * 42 * t)
        + 0.14 * np.sin(2 * np.pi * 51 * t)
        + 0.1 * np.sin(2 * np.pi * 38 * t) * np.sin(2 * np.pi * 2.3 * t)
    )
    st += 0.06 * _one_second_deterministic_texture(8, (1,) * 16)
    return np.tanh(st * 1.9)


def build_commissioning_wav(duration: float = 10.0) -> np.ndarray:
    """Original scripted 10 s timeline (one-shot demo)."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0.0, duration, n, endpoint=False)

    hum = (
        1.0 * np.sin(2 * np.pi * 60 * t)
        + 0.5 * np.sin(2 * np.pi * 120 * t)
        + 0.25 * np.sin(2 * np.pi * 240 * t)
    )
    hum = np.clip(hum * 2.0, -0.6, 0.6)

    ramp_freq = np.interp(t, [0, 2], [60, 800])
    ramp_phase = np.cumsum(ramp_freq) / SAMPLE_RATE * 2 * np.pi
    spin_up = np.sin(ramp_phase)
    spin_envelope = np.interp(t, [0, 1.8, 2.0, 2.1], [0.0, 0.8, 0.0, 0.0])
    spin_up = spin_up * spin_envelope

    clack_env = np.where(t >= 2.0, np.exp(-50 * (t - 2.0)), 0)
    clack_tone = np.sin(2 * np.pi * 40 * t)
    clack_snap = np.random.default_rng(0).uniform(-1, 1, len(t)) * np.exp(-500 * np.maximum(0, t - 2.0))
    clack = (clack_tone + clack_snap) * clack_env * 3.0

    rng = np.random.default_rng(1)
    raw_noise = rng.uniform(-1, 1, len(t))
    window = np.ones(40) / 40.0
    rumble = np.convolve(raw_noise, window, mode="same")
    chug = 1.0 + 0.5 * np.sin(2 * np.pi * 15 * t)
    roar = rumble * chug
    roar_envelope = np.clip((t - 2.0), 0, 1.0)
    roar = roar * roar_envelope * 4.0

    arcing = rng.uniform(-1, 1, len(t))
    arcing[np.abs(arcing) < 0.95] = 0
    electric_stutter = np.sin(2 * np.pi * 120 * t)
    crackle = arcing * electric_stutter
    crackle_env = np.where(t >= 4.0, 1.0, 0.0)
    crackle = crackle * crackle_env * 2.5

    master = hum + spin_up + clack + roar + crackle
    return np.tanh(master * 1.5)


def main() -> None:
    ap = argparse.ArgumentParser(description="Write Orbitron test-stand WAV assets.")
    ap.add_argument(
        "--out-dir",
        default="",
        help="Output directory (default: ../../Aircraft/Orbitron-TestStand/Sounds from this script, or $ORBITRON_SOUNDS_OUT)",
    )
    ap.add_argument(
        "--skip-commissioning",
        action="store_true",
        help="Do not write reactor_audio_heavy.wav (saves time if you only need loops)",
    )
    ap.add_argument(
        "--mux-video",
        action="store_true",
        help="If orbitron_startup_sequence.mp4 exists, mux commissioning audio to FINAL_ORBITRON_TEST.mp4",
    )
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    default_air = os.path.normpath(
        os.path.join(here, "..", "..", "Aircraft", "Orbitron-TestStand", "Sounds")
    )
    out_dir = args.out_dir or os.environ.get("ORBITRON_SOUNDS_OUT") or default_air
    os.makedirs(out_dir, exist_ok=True)

    print("Synthesizing Orbitron sound beds →", out_dir)

    _write_mono_wav(os.path.join(out_dir, "orbitron_core_loop.wav"), build_core_loop())
    _write_mono_wav(os.path.join(out_dir, "orbitron_inlet_loop.wav"), build_inlet_loop())
    _write_mono_wav(os.path.join(out_dir, "orbitron_jet_loop.wav"), build_jet_loop())
    _write_mono_wav(os.path.join(out_dir, "orbitron_dec_arc_loop.wav"), build_dec_arc_loop())
    _write_mono_wav(os.path.join(out_dir, "orbitron_screen_sputter_loop.wav"), build_screen_sputter_loop())
    _write_mono_wav(os.path.join(out_dir, "orbitron_motor_whine_loop.wav"), build_motor_whine_loop())
    _write_mono_wav(os.path.join(out_dir, "orbitron_duct_heat_loop.wav"), build_duct_heat_loop())
    _write_mono_wav(os.path.join(out_dir, "orbitron_stressor_loop.wav"), build_stressor_loop())

    if not args.skip_commissioning:
        wav_c = os.path.join(out_dir, "reactor_audio_heavy.wav")
        _write_mono_wav(wav_c, build_commissioning_wav(10.0))
        if args.mux_video:
            video_filename = os.path.join(here, "orbitron_startup_sequence.mp4")
            output_filename = os.path.join(here, "FINAL_ORBITRON_TEST.mp4")
            if os.path.exists(video_filename):
                print("Muxing commissioning audio to video...")
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    video_filename,
                    "-i",
                    wav_c,
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-strict",
                    "experimental",
                    output_filename,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("Wrote", output_filename)
            else:
                print("No", video_filename, "— skipped mux.")

    print("Done: orbitron_*_loop.wav beds + optional reactor_audio_heavy.wav.")


if __name__ == "__main__":
    main()
