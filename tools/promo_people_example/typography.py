"""Separate clean title overlays for the luminous-people motion example.

Composite after glow. There are no panels or opaque backgrounds. The opening
and compact closing reserve the left third; the gesture caption reserves sky.
"""
from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
FONT_ROOT = ROOT / "fonts"


def _font(filename, pixels):
    return ImageFont.truetype(str(FONT_ROOT / filename), max(1, round(pixels)))


def build_overlay(width=1920, height=1080, kind="opening"):
    """Return a PIL RGBA image of one named overlay at the native resolution.

    kind is opening, signature, greeting, or closing. Caller controls timing
    and opacity. All placement uses a centred 1920x1080 design coordinate set.
    """
    if width <= 0 or height <= 0:
        raise ValueError("Overlay dimensions must be positive.")
    if kind not in ("opening", "signature", "greeting", "closing"):
        raise ValueError(f"Unknown overlay kind: {kind}")
    ss = 2
    scale = min(width / 1920, height / 1080) * ss
    image = Image.new("RGBA", (width * ss, height * ss))
    draw = ImageDraw.Draw(image)
    ox = (image.width - 1920 * scale) / 2
    oy = (image.height - 1080 * scale) / 2

    def point(x, y):
        return ox + x * scale, oy + y * scale

    def text(x, y, words, name, size, colour, anchor="lt"):
        draw.text(point(x, y), words, font=_font(name, size * scale),
                  fill=colour, anchor=anchor)

    def tracked(x, y, words, name, size, colour, spacing, centred=False):
        font = _font(name, size * scale)
        advance = sum(draw.textlength(c, font=font) for c in words)
        advance += max(0, len(words)-1) * spacing * scale
        px, py = point(x, y)
        if centred:
            px -= advance / 2
        baseline = py - font.getbbox("H", anchor="ls")[1]
        for c in words:
            draw.text((px, baseline), c, font=font, fill=colour, anchor="ls")
            px += draw.textlength(c, font=font) + spacing * scale

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from engine.p3d import brand

    def logo(x, y, h):
        mark = brand.logo_image(height=round(h * scale), pad=.025, glow=0,
                                palette="brand", ss=3)
        px, py = point(x, y)
        image.alpha_composite(mark, (round(px), round(py)))

    serif = "cormorant-garamond-latin-500-normal.ttf"
    italic = "cormorant-garamond-latin-500-italic.ttf"
    sans = "jost-latin-500-normal.ttf"
    light = "jost-latin-400-normal.ttf"
    ivory = (255, 244, 222, 255)
    gold = (245, 209, 154, 255)
    soft = (248, 231, 205, 255)

    if kind == "opening":
        logo(100, 202, 67)
        tracked(102, 309, "HEALING CONCERT", sans, 21, gold, 4.1)
        text(98, 359, "The Words of", serif, 57, ivory)
        text(95, 427, "Mother\u2019s Love", serif, 86, ivory)
        text(101, 530, "That Bring Peace", italic, 57, soft)
        for i, colour in enumerate(brand.NINE):
            x, y = point(104 + i * 16, 611)
            r = 1.8 * scale
            draw.ellipse((x-r, y-r, x+r, y+r), fill=colour)
        tracked(102, 650, "SUNDAY, DECEMBER 6 \u00b7 4:30 PM", sans, 20, ivory, 1.0)
        tracked(102, 695, "LAS VEGAS", light, 19, gold, 5.1)
    elif kind == "signature":
        logo(66, 937, 47)
        text(137, 929, "The Words of Mother\u2019s Love", serif, 29, ivory)
        tracked(139, 968, "DEC 6 \u00b7 4:30 PM", sans, 16, gold, 2.0)
        tracked(139, 996, "HEALING CONCERT \u00b7 LAS VEGAS", light, 13, soft, 2.0)
    elif kind == "greeting":
        tracked(960, 137, "GREETING", sans, 21, (246, 174, 166, 255), 5.1, True)
        text(960, 187, "How are you?", serif, 66, ivory, "mt")
    else:
        logo(100, 193, 67)
        tracked(102, 300, "HEALING CONCERT", sans, 20, gold, 3.8)
        text(99, 351, "The Words of", serif, 54, ivory)
        text(96, 417, "Mother\u2019s Love", serif, 80, ivory)
        text(102, 513, "That Bring Peace", italic, 53, soft)
        tracked(103, 602, "SUNDAY, DECEMBER 6", sans, 22, gold, 1.1)
        tracked(103, 643, "4:30 PM \u00b7 LAS VEGAS", sans, 22, ivory, 1.1)
        text(103, 702, "World Mission Society Church of God", light, 22, soft)
        text(103, 740, "6720 W Sahara Ave, Las Vegas", light, 21, soft)

    return image.resize((width, height), Image.Resampling.LANCZOS)
