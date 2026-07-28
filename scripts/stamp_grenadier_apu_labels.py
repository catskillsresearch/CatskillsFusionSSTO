#!/usr/bin/env python3
"""Stamp Grenadier labels onto heritage Shuttle panel paint.

Heritage paint still says APU / ENGINE POWER; hover tooltips + these short
logos carry the Grenadier meaning:

  APU OPERATE 1/2/3     →  CART / BATT / CRYO
  APU CNTLR PWR 1/2/3   →  MAGNET / FUEL / RF
  ENGINE POWER          →  REACTOR POWER
  LEFT AC2 / CTR AC1 / RIGHT AC3  →  CHARM / DEC / VACUUM

Edits Models/fwd-cockpit-text-map-x.png in place.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "Models" / "fwd-cockpit-text-map-x.png"


def _font(size: int) -> ImageFont.ImageFont:
    for fp in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ):
        try:
            return ImageFont.truetype(fp, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _panel_gray(arr: np.ndarray, x: int, y: int, r: int = 6) -> tuple[int, int, int]:
    patch = arr[y - r : y + r + 1, x - r : x + r + 1].reshape(-1, 3)
    mid = patch[patch.max(axis=1) < 180]
    if len(mid):
        return tuple(int(v) for v in mid.mean(axis=0))
    return (110, 110, 112)


def _stamp_row(
    img: Image.Image,
    arr: np.ndarray,
    centers_x: list[int],
    labels: list[str],
    y: int,
    *,
    cover_w: int,
    cover_h: int,
    font_size: int,
) -> None:
    d = ImageDraw.Draw(img)
    font = _font(font_size)
    gray = _panel_gray(arr, centers_x[1], y)
    for cx, lab in zip(centers_x, labels):
        d.rectangle(
            [cx - cover_w // 2, y - cover_h // 2, cx + cover_w // 2, y + cover_h // 2],
            fill=gray,
        )
        bbox = d.textbbox((0, 0), lab, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text((int(cx - tw / 2), int(y - th / 2 - 1)), lab, fill=(245, 245, 245), font=font)


def _stamp_centered(
    img: Image.Image,
    arr: np.ndarray,
    label: str,
    cx: int,
    y: int,
    *,
    cover_w: int,
    cover_h: int,
    font_size: int,
) -> None:
    d = ImageDraw.Draw(img)
    font = _font(font_size)
    gray = _panel_gray(arr, cx, y)
    d.rectangle(
        [cx - cover_w // 2, y - cover_h // 2, cx + cover_w // 2, y + cover_h // 2],
        fill=gray,
    )
    bbox = d.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((int(cx - tw / 2), int(y - th / 2 - 1)), label, fill=(245, 245, 245), font=font)


def main() -> None:
    img = Image.open(TEX).convert("RGB")
    arr = np.asarray(img)
    # Pixel centers measured on fwd-cockpit-text-map-x.png (4096²).
    _stamp_row(
        img,
        arr,
        [701, 761, 820],
        ["CART", "BATT", "CRYO"],
        1404,
        cover_w=24,
        cover_h=11,
        font_size=8,
    )
    _stamp_row(
        img,
        arr,
        [825, 884, 948],
        ["MAGNET", "FUEL", "RF"],
        1732,
        cover_w=28,
        cover_h=11,
        font_size=8,
    )
    # ENGINE POWER → REACTOR POWER (header + LEFT AC2 / CTR AC1 / RIGHT AC3)
    _stamp_centered(
        img,
        arr,
        "REACTOR POWER",
        551,
        1061,
        cover_w=168,
        cover_h=12,
        font_size=9,
    )
    _stamp_row(
        img,
        arr,
        [443, 524, 606],
        ["CHARM", "DEC", "VACUUM"],
        1076,
        cover_w=44,
        cover_h=20,
        font_size=8,
    )
    img.save(TEX)
    print(f"wrote {TEX}")


if __name__ == "__main__":
    main()
