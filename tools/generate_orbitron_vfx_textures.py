#!/usr/bin/env python3
"""Bake Orbitron nozzle particle textures (hot core + shear plume).

annulus.png is a white alpha-mask ring; with <emissive>true</emissive> FlightGear
often renders it as a black blob. These sprites carry color in RGB with a soft alpha falloff.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image


def _radial_grid(size: int) -> tuple[np.ndarray, np.ndarray]:
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    cx = (size - 1) * 0.5
    r = np.sqrt((x - cx) ** 2 + (y - cx) ** 2) / (size * 0.5)
    return r, np.arctan2(y - cx, x - cx)


def _hot_core_sprite(size: int = 128) -> Image.Image:
    r, _ = _radial_grid(size)
    # Bright yellow-white core → orange → transparent rim
    core = np.clip(1.0 - r * 1.15, 0.0, 1.0) ** 0.55
    rim = np.clip(1.0 - (r - 0.25) * 2.2, 0.0, 1.0) ** 1.6
    alpha = np.clip(core * 0.95 + rim * 0.35, 0.0, 1.0)

    red = np.clip(0.55 + 0.45 * core + 0.25 * rim, 0.0, 1.0)
    green = np.clip(0.35 + 0.50 * core + 0.10 * rim, 0.0, 1.0)
    blue = np.clip(0.05 + 0.18 * core, 0.0, 1.0)

    rgba = np.dstack(
        (
            (red * 255).astype(np.uint8),
            (green * 255).astype(np.uint8),
            (blue * 255).astype(np.uint8),
            (alpha * 255).astype(np.uint8),
        )
    )
    return Image.fromarray(rgba, mode="RGBA")


def _shear_plume_sprite(size: int = 128) -> Image.Image:
    r, ang = _radial_grid(size)
    # Slightly elongated soft smoke puff (works for trail + fixed align)
    stretch = 1.0 + 0.22 * np.cos(ang) ** 2
    r_eff = r * stretch
    alpha = np.clip(1.0 - (r_eff - 0.05) * 1.35, 0.0, 1.0) ** 2.0
    alpha *= np.clip(1.0 - r * 0.35, 0.35, 1.0)

    red = np.full_like(alpha, 0.82)
    green = np.full_like(alpha, 0.84)
    blue = np.full_like(alpha, 0.88)

    rgba = np.dstack(
        (
            (red * alpha * 255).astype(np.uint8),
            (green * alpha * 255).astype(np.uint8),
            (blue * alpha * 255).astype(np.uint8),
            (alpha * 255).astype(np.uint8),
        )
    )
    return Image.fromarray(rgba, mode="RGBA")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "Models" / "Effects",
        help="Write orbitron_nozzle_*.png here",
    )
    args = ap.parse_args()
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    flame = out / "orbitron_nozzle_flame.png"
    plume = out / "orbitron_nozzle_plume.png"
    _hot_core_sprite().save(flame)
    _shear_plume_sprite().save(plume)
    print("Wrote", flame)
    print("Wrote", plume)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
