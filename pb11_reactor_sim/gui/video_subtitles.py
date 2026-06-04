"""
White subtitle overlay for exported MP4 frames.
"""
from __future__ import annotations

from io import BytesIO

from pb11_reactor_sim.gui.chattts_narration import wrap_subtitle_lines


def burn_subtitle(png: bytes, text: str | None) -> bytes:
    """Return ``png`` with centered white subtitle bar when ``text`` is non-empty."""
    if not text or not text.strip():
        return png
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return png

    img = Image.open(BytesIO(png)).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size
    margin = max(12, w // 80)
    font_size = max(18, w // 52)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    lines = wrap_subtitle_lines(text, max_chars=54)
    line_h = font_size + 6
    block_h = len(lines) * line_h + 2 * margin
    y0 = h - block_h - margin
    draw.rectangle((margin, y0, w - margin, y0 + block_h), fill=(0, 0, 0, 150))
    y = y0 + margin
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, y), line, fill=(255, 255, 255, 255), font=font)
        y += line_h

    out = Image.alpha_composite(img, overlay).convert("RGB")
    buf = BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()
