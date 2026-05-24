#!/usr/bin/env python3
"""Trim near-uniform background from assembly hero PNGs (default #ECECEC)."""
from __future__ import annotations

import argparse
from pathlib import Path


def trim_png(
    path: Path,
    *,
    bg_hex: str = "#ECECEC",
    tolerance: int = 12,
    padding_px: int = 8,
) -> tuple[int, int, int, int] | None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow required: pip install Pillow") from exc

    img = Image.open(path).convert("RGBA")
    bg = tuple(int(bg_hex.strip("#")[i : i + 2], 16) for i in (0, 2, 4))
    w, h = img.size
    pixels = img.load()
    mask = [
        [
            sum(abs(pixels[x, y][c] - bg[c]) for c in range(3)) > tolerance
            for y in range(h)
        ]
        for x in range(w)
    ]
    xs = [x for x in range(w) if any(mask[x][y] for y in range(h))]
    ys = [y for y in range(h) if any(mask[x][y] for x in range(w))]
    if not xs or not ys:
        return None
    left = max(0, min(xs) - padding_px)
    right = min(w, max(xs) + 1 + padding_px)
    top = max(0, min(ys) - padding_px)
    bottom = min(h, max(ys) + 1 + padding_px)
    cropped = img.crop((left, top, right, bottom))
    cropped.save(path)
    return (left, top, right, bottom)


def main() -> int:
    parser = argparse.ArgumentParser(description="Trim assembly PNG whitespace")
    parser.add_argument("png", type=Path, nargs="+")
    parser.add_argument("--bg", default="#ECECEC")
    parser.add_argument("--tolerance", type=int, default=12)
    parser.add_argument("--padding", type=int, default=8)
    args = parser.parse_args()
    for p in args.png:
        box = trim_png(
            p.resolve(),
            bg_hex=args.bg,
            tolerance=args.tolerance,
            padding_px=args.padding,
        )
        print(f"{p}: {box or 'no trim'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
