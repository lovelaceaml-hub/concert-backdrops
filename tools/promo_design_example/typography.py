"""Quiet, full-resolution opening typography for the ten-second design example.

All lettering uses the installed campaign fonts. The mark comes directly from
the existing procedural campaign geometry and retains its approved colours.
No photographic or generated image is used. Composite this straight-alpha
overlay after scene bloom so the fine lettering stays clear throughout the shot.
"""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
FONT_ROOT = ROOT / "fonts"


def _font(filename: str, pixels: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_ROOT / filename), max(1, round(pixels)))


def _tracked(draw: ImageDraw.ImageDraw, position, text, font, fill, tracking):
    """Left-aligned lettering with tracking measured from actual glyph advances."""
    x, y = position
    baseline = y - font.getbbox("H", anchor="ls")[1]
    for char in text:
        draw.text((x, baseline), char, font=font, fill=fill, anchor="ls")
        x += draw.textlength(char, font=font) + tracking
    return x


def build_overlay(width: int = 1920, height: int = 1080) -> Image.Image:
    """Return an RGBA title overlay, scaled from a 1920 by 1080 composition.

    The content occupies the left third, leaving the Earth's reveal unobstructed
    on the right. Text remains fully legible from frame zero to the last frame.
    The caller owns timing and blending; no state accumulates between frames.
    """
    if width <= 0 or height <= 0:
        raise ValueError("Overlay dimensions must be positive.")
    # Font and mark geometry are rasterised at double size before downsampling.
    supersample = 2
    scale = min(width / 1920, height / 1080) * supersample
    canvas = Image.new("RGBA", (width * supersample, height * supersample))
    draw = ImageDraw.Draw(canvas)
    offset_x = (canvas.width - 1920 * scale) / 2
    offset_y = (canvas.height - 1080 * scale) / 2

    def xy(x, y):
        return offset_x + x * scale, offset_y + y * scale

    def text(x, y, value, name, size, colour):
        draw.text(xy(x, y), value, font=_font(name, size * scale),
                  fill=colour, anchor="lt")

    # Import the same vector mark used by the approved opening and signature.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from engine.p3d import brand

    logo = brand.logo_image(height=round(78 * scale), pad=.025, glow=0,
                            palette="brand", ss=3)
    logo_x, logo_y = xy(147, 184)
    canvas.alpha_composite(logo, (round(logo_x), round(logo_y)))

    ivory = (255, 244, 222, 255)
    champagne = (245, 210, 153, 255)
    soft_ivory = (248, 231, 205, 255)
    _tracked(draw, xy(150, 309), "HEALING CONCERT",
             _font("jost-latin-500-normal.ttf", 27 * scale), champagne,
             tracking=6.5 * scale)

    text(146, 373, "The Words of", "cormorant-garamond-latin-500-normal.ttf",
         76, ivory)
    text(142, 452, "Mother\u2019s Love", "cormorant-garamond-latin-500-normal.ttf",
         120, ivory)
    text(148, 593, "That Bring Peace", "cormorant-garamond-latin-500-italic.ttf",
         74, soft_ivory)

    # A small nine-colour detail ties the restrained lockup to the moving streams.
    for index, colour in enumerate(brand.NINE):
        x, y = xy(151 + index * 18, 704)
        radius = 2.15 * scale
        draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                     fill=colour)

    _tracked(draw, xy(150, 748), "SUNDAY, DECEMBER 6 \u00b7 4:30 PM",
             _font("jost-latin-500-normal.ttf", 27 * scale), ivory,
             tracking=2.2 * scale)
    _tracked(draw, xy(150, 807), "LAS VEGAS",
             _font("jost-latin-400-normal.ttf", 23 * scale), champagne,
             tracking=7 * scale)

    return canvas.resize((width, height), Image.Resampling.LANCZOS)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build_overlay(args.width, args.height).save(args.output)
