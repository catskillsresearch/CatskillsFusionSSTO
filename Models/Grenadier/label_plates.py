#!/usr/bin/env python3
"""Shared top-face label plates for Grenadier AC meshes (FG + Blender)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def write_label_png(path: Path, text: str, *, bg=(28, 30, 36), fg=(245, 245, 248)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Wider canvas for long labels; keep readable at small plate sizes
    w, h = 640, 160
    im = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(im)
    size = 72 if len(text) <= 8 else 56 if len(text) <= 12 else 44 if len(text) <= 16 else 36
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, (h - th) / 2 - 4), text, fill=fg, font=font)
    im.save(path)


def label_size(dx: float, dz: float) -> tuple[float, float]:
    """Return (length_along_long_axis, width) — compact but readable."""
    span = max(min(abs(dx), abs(dz)), 0.05)
    long = max(abs(dx), abs(dz))
    # Floor high enough that MW boxes / thin rails stay legible top-down
    lw = max(0.28, min(1.15, span * 0.70 if span < 1.5 else min(1.15, long * 0.40)))
    lh = max(0.10, min(0.34, lw * 0.40))
    # Never exceed the host face by much
    lw = min(lw, max(long * 0.90, 0.28))
    lh = min(lh, max(span * 0.85, 0.10))
    return lw, lh


def top_label_quad(
    x0: float,
    x1: float,
    y_top: float,
    z0: float,
    z1: float,
    *,
    lift: float = 0.03,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]], list[list[tuple[float, float]]]]:
    """Centered plate on box top; readable looking down (+Y).

    Texture is wide (text along U). Map U along the plate's *long* edge.
    Winding gives +Y normal. U increases along the long axis (not flipped) —
    backface viewing was the original mirror source, not U direction.
    """
    dx, dz = x1 - x0, z1 - z0
    lw, lh = label_size(dx, dz)
    cx, cz = (x0 + x1) * 0.5, (z0 + z1) * 0.5
    y = y_top + lift

    # verts 0..3: CCW from +Y → normal +Y
    if abs(dx) >= abs(dz):
        xa, xb = cx - lw * 0.5, cx + lw * 0.5
        za, zb = cz - lh * 0.5, cz + lh * 0.5
        verts = [(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)]
        # U along X — flipped so top-down text is not mirrored (Z-long is already OK)
        faces = [(0, 3, 2, 1)]
        uvs = [[(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]]
    else:
        xa, xb = cx - lh * 0.5, cx + lh * 0.5
        za, zb = cz - lw * 0.5, cz + lw * 0.5
        verts = [(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)]
        # U along +Z — 90° tilt is fine; do not flip
        faces = [(0, 3, 2, 1)]
        uvs = [[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]]

    return verts, faces, uvs
