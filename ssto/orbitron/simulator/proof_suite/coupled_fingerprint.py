"""Coupled-run fingerprint for steps 01–03 — detect stale partial artifacts."""
from __future__ import annotations

from typing import Any


def coupled_run_fingerprint(cfg: dict[str, Any]) -> dict[str, float | int | bool]:
    """Hash of all inputs that must match across steps 01, 02, 03."""
    pad = cfg["pad"]
    inj = cfg["injectants"]
    fc = cfg.get("fusion_channel") or {}
    pic = cfg["pic"]
    return {
        "throttle": float(pad["throttle"]),
        "cathode_pulse": float(pad["cathode_pulse"]),
        "compressor": float(pad["compressor"]),
        "h2_sccm": float(inj["h2_sccm"]),
        "laser_ablation_hz": float(inj["laser_ablation_hz"]),
        "laminar": bool(pad.get("laminar_relaminarization", True)),
        "noise_fraction_off": float(fc.get("noise_fraction_off", 0.14)),
        "stochastic_seed": int(fc.get("stochastic_seed", 42)),
        "pic_steps": int(pic["steps"]),
        "grid_cells": int(pic["grid_cells"]),
        "diag_period": int(pic.get("diag_period", 40)),
    }


def last_coupled_fingerprint(cfg: dict[str, Any]) -> dict[str, float | int | bool] | None:
    raw = cfg.get("gui", {}).get("last_coupled_run")
    if not isinstance(raw, dict):
        return None
    return raw


def fingerprints_match(a: dict[str, Any], b: dict[str, Any] | None) -> bool:
    if b is None:
        return False
    fp_a = coupled_run_fingerprint(a) if "pad" in a else a
    fp_b = b if "throttle" in b else coupled_run_fingerprint(b)
    return fp_a == fp_b


def is_coupled_stale(cfg: dict[str, Any]) -> bool:
    return not fingerprints_match(cfg, last_coupled_fingerprint(cfg))


def save_coupled_fingerprint(cfg: dict[str, Any]) -> None:
    cfg.setdefault("gui", {})["last_coupled_run"] = coupled_run_fingerprint(cfg)
