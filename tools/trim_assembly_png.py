#!/usr/bin/env python3
"""Trim near-uniform background from assembly hero PNGs.

Blender EEVEE output is often darker than nominal ``#ECECEC`` (~193 RGB); we sample corners
for the background, then crop to non-background pixels (with a luminance fallback).
"""
from __future__ import annotations

import argparse
from pathlib import Path


def sample_background_rgb(img, *, margin: int = 12) -> tuple[int, int, int]:
    """Median RGB from image corners (matches EEVEE factory-gray world)."""
    w, h = img.size
    samples: list[tuple[int, int, int]] = []
    for x, y in (
        (margin, margin),
        (w - 1 - margin, margin),
        (margin, h - 1 - margin),
        (w - 1 - margin, h - 1 - margin),
    ):
        r, g, b = img.getpixel((x, y))[:3]
        samples.append((r, g, b))
    samples.sort()
    mid = len(samples) // 2
    return samples[mid]


def _content_bbox(
    img,
    *,
    bg: tuple[int, int, int],
    tolerance: int,
    lum_delta: int,
) -> tuple[int, int, int, int] | None:
    w, h = img.size
    xs: list[int] = []
    ys: list[int] = []
    thr = tuple(max(0, c - lum_delta) for c in bg)
    for y in range(h):
        for x in range(w):
            r, g, b = img.getpixel((x, y))[:3]
            if sum(abs((r, g, b)[i] - bg[i]) for i in range(3)) > tolerance:
                xs.append(x)
                ys.append(y)
                continue
            if r < thr[0] or g < thr[1] or b < thr[2]:
                xs.append(x)
                ys.append(y)
    if not xs or not ys:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def trim_png(
    path: Path,
    *,
    bg_hex: str | None = None,
    tolerance: int = 18,
    padding_px: int = 10,
    lum_delta: int = 35,
) -> tuple[int, int, int, int] | None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow required: pip install Pillow") from exc

    img = Image.open(path).convert("RGB")
    if bg_hex:
        bg = tuple(int(bg_hex.strip("#")[i : i + 2], 16) for i in (0, 2, 4))
    else:
        bg = sample_background_rgb(img)
    w, h = img.size
    box = _content_bbox(img, bg=bg, tolerance=tolerance, lum_delta=lum_delta)
    if box is None:
        return None
    x0, y0, x1, y1 = box
    left = max(0, x0 - padding_px)
    top = max(0, y0 - padding_px)
    right = min(w, x1 + 1 + padding_px)
    bottom = min(h, y1 + 1 + padding_px)
    cropped = img.crop((left, top, right, bottom))
    cropped.save(path)

    # Second pass: EEVEE vignette can leave wide margins after the first crop.
    img2 = Image.open(path).convert("RGB")
    w2, h2 = img2.size
    bg2 = sample_background_rgb(img2) if bg_hex is None else bg
    box2 = _content_bbox(
        img2, bg=bg2, tolerance=max(10, tolerance - 4), lum_delta=max(20, lum_delta - 8)
    )
    if box2 is not None:
        x0, y0, x1, y1 = box2
        area = (x1 - x0 + 1) * (y1 - y0 + 1)
        if area < 0.62 * w2 * h2:
            pad2 = max(4, padding_px // 2)
            left = max(0, x0 - pad2)
            top = max(0, y0 - pad2)
            right = min(w2, x1 + 1 + pad2)
            bottom = min(h2, y1 + 1 + pad2)
            img2.crop((left, top, right, bottom)).save(path)
            return (left, top, right, bottom)

    return (left, top, right, bottom)


def main() -> int:
    parser = argparse.ArgumentParser(description="Trim assembly PNG whitespace")
    parser.add_argument("png", type=Path, nargs="+")
    parser.add_argument("--bg", default=None, help="Background #RRGGBB (default: sample corners)")
    parser.add_argument("--tolerance", type=int, default=18)
    parser.add_argument("--padding", type=int, default=10)
    parser.add_argument("--lum-delta", type=int, default=35, dest="lum_delta")
    args = parser.parse_args()
    for p in args.png:
        box = trim_png(
            p.resolve(),
            bg_hex=args.bg,
            tolerance=args.tolerance,
            padding_px=args.padding,
            lum_delta=args.lum_delta,
        )
        print(f"{p}: {box or 'no trim'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
