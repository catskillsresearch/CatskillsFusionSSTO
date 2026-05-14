#!/usr/bin/env python3
"""Compile WAV assets from ``orbitron_sound_assets.yaml`` (sole sound truth for Orbitron beds).

Each YAML entry supplies narrative copy, a formal ``description_formal`` block for humans
and tooling, ``file`` basename, ``compile: { recipe, params }``, and ``flightgear:`` for
FlightGear ``sound.xml`` generation (see ``tools/compile_sound_xml_from_yaml.py``).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np
import yaml
from orbitron_aircraft_pkg import aircraft_package_dir
from scipy.io import wavfile

SAMPLE_RATE = 44100


def _write_mono_wav(path: Path, samples: np.ndarray) -> None:
    x = np.clip(samples.astype(np.float64), -1.0, 1.0)
    path.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(path), SAMPLE_RATE, np.int16(x * 32767.0))


def _one_second_deterministic_texture(seed: int, weights: tuple[float, ...]) -> np.ndarray:
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


def _seamless_plasma_bed(_params: dict[str, Any]) -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    core = (
        0.22 * np.sin(2 * np.pi * 60 * t)
        + 0.12 * np.sin(2 * np.pi * 120 * t)
        + 0.08 * np.sin(2 * np.pi * 180 * t)
        + 0.06 * np.sin(2 * np.pi * 240 * t)
    )
    core += 0.04 * _one_second_deterministic_texture(1, (1,) * 28)
    core += 0.025 * np.sin(2 * np.pi * 15 * t) * np.sin(2 * np.pi * 90 * t)
    return np.tanh(core * 2.2)


def _seamless_inlet_hiss(_params: dict[str, Any]) -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    hiss = 0.12 * _one_second_deterministic_texture(2, (1,) * 48)
    hiss += 0.08 * np.sin(2 * np.pi * 400 * t) * np.sin(2 * np.pi * 11 * t)
    hiss += 0.05 * np.sin(2 * np.pi * 1200 * t)
    return np.tanh(hiss * 2.8)


def _seamless_jet_rumble(_params: dict[str, Any]) -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    jet = (
        0.2 * np.sin(2 * np.pi * 55 * t)
        + 0.14 * np.sin(2 * np.pi * 73 * t)
        + 0.1 * np.sin(2 * np.pi * 97 * t)
        + 0.12 * np.sin(2 * np.pi * 31 * t) * np.sin(2 * np.pi * 140 * t)
    )
    jet += 0.08 * _one_second_deterministic_texture(3, (1,) * 22)
    return np.tanh(jet * 2.0)


def _seamless_dec_arc(_params: dict[str, Any]) -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    arc = 0.18 * np.sin(2 * np.pi * 120 * t) * np.sin(2 * np.pi * 37 * t)
    arc += 0.14 * _one_second_deterministic_texture(4, (1,) * 36)
    arc += 0.1 * np.sin(2 * np.pi * 240 * t) * np.sin(2 * np.pi * 7 * t)
    arc += 0.06 * np.sin(2 * np.pi * 1800 * t) * np.sin(2 * np.pi * 3 * t)
    return np.tanh(arc * 2.4)


def _seamless_screen_sputter(_params: dict[str, Any]) -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    sp = 0.1 * _one_second_deterministic_texture(5, (0,) * 60 + (1,) * 18)
    sp += 0.12 * np.sin(2 * np.pi * 2200 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 17 * t))
    sp += 0.08 * np.sin(2 * np.pi * 880 * t) * np.sin(2 * np.pi * 29 * t)
    return np.tanh(sp * 2.2)


def _seamless_motor_whine(_params: dict[str, Any]) -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    wh = (
        0.2 * np.sin(2 * np.pi * 220 * t)
        + 0.1 * np.sin(2 * np.pi * 440 * t)
        + 0.05 * np.sin(2 * np.pi * 660 * t)
    )
    wh += 0.04 * np.sin(2 * np.pi * 330 * t) * np.sin(2 * np.pi * 6.5 * t)
    wh += 0.03 * _one_second_deterministic_texture(6, (1,) * 12)
    return np.tanh(wh * 2.0)


def _seamless_duct_heat(_params: dict[str, Any]) -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    dh = (
        0.16 * np.sin(2 * np.pi * 68 * t)
        + 0.12 * np.sin(2 * np.pi * 142 * t)
        + 0.1 * np.sin(2 * np.pi * 41 * t) * np.sin(2 * np.pi * 210 * t)
    )
    dh += 0.07 * _one_second_deterministic_texture(7, (1,) * 26)
    dh *= 0.85 + 0.15 * np.sin(2 * np.pi * 3 * t)
    return np.tanh(dh * 2.1)


def _seamless_stressor(_params: dict[str, Any]) -> np.ndarray:
    t = np.linspace(0.0, 1.0, SAMPLE_RATE, endpoint=False)
    st = (
        0.22 * np.sin(2 * np.pi * 42 * t)
        + 0.14 * np.sin(2 * np.pi * 51 * t)
        + 0.1 * np.sin(2 * np.pi * 38 * t) * np.sin(2 * np.pi * 2.3 * t)
    )
    st += 0.06 * _one_second_deterministic_texture(8, (1,) * 16)
    return np.tanh(st * 1.9)


def _commissioning_timeline(params: dict[str, Any]) -> np.ndarray:
    duration = float(params.get("duration_s", 10.0))
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


RECIPES: dict[str, Callable[[dict[str, Any]], np.ndarray]] = {
    "seamless_plasma_bed": _seamless_plasma_bed,
    "seamless_inlet_hiss": _seamless_inlet_hiss,
    "seamless_jet_rumble": _seamless_jet_rumble,
    "seamless_dec_arc": _seamless_dec_arc,
    "seamless_screen_sputter": _seamless_screen_sputter,
    "seamless_motor_whine": _seamless_motor_whine,
    "seamless_duct_heat": _seamless_duct_heat,
    "seamless_stressor": _seamless_stressor,
    "commissioning_timeline": _commissioning_timeline,
}


def compile_sounds(spec_path: Path, out_dir: Path) -> None:
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "sounds" not in data:
        raise ValueError(f"Expected mapping with 'sounds' list: {spec_path}")
    sounds = data["sounds"]
    if not isinstance(sounds, list):
        raise TypeError("'sounds' must be a list")

    for i, entry in enumerate(sounds):
        if not isinstance(entry, dict):
            raise TypeError(f"sounds[{i}] must be a mapping")
        fname = entry.get("file")
        if not fname:
            raise ValueError(f"sounds[{i}] missing file")
        comp = entry.get("compile") or {}
        recipe = comp.get("recipe")
        if not recipe:
            raise ValueError(f"sounds[{i}] missing compile.recipe")
        params = comp.get("params") or {}
        if not isinstance(params, dict):
            raise TypeError(f"sounds[{i}].compile.params must be a mapping")
        fn = RECIPES.get(str(recipe))
        if fn is None:
            raise KeyError(f"Unknown recipe {recipe!r}; known: {sorted(RECIPES)}")
        wav = fn(params)
        out_path = out_dir / str(fname)
        _write_mono_wav(out_path, wav)
        print("Wrote", out_path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", type=Path, required=True, help="orbitron_sound_assets.yaml")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output Sounds directory (default: Aircraft/<aircraft.package_dir>/Sounds from repo root)",
    )
    args = ap.parse_args()
    spec = args.spec.resolve()
    if not spec.is_file():
        print(f"error: spec not found: {spec}", file=sys.stderr)
        return 1

    root = Path(__file__).resolve().parents[1]
    _pkg = aircraft_package_dir(root)
    out_dir = args.out_dir
    if out_dir is None:
        out_dir = Path(
            os.environ.get(
                "ORBITRON_SOUNDS_OUT",
                str(root / "Aircraft" / _pkg / "Sounds"),
            )
        )
    out_dir = out_dir.resolve()
    print("Compiling sounds from", spec, "→", out_dir)
    compile_sounds(spec, out_dir)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
