"""Draws the light shapes used by engine/songs/s11_v4.py (white on black, read by the engine's figure layer).

  s11v4_city_outline.png  the promised city as thin lines: walls, towers and the open gate in the middle
  s11v4_city_gold.png     the same city filled: lit walls, windows and a bright gate (the city filled with gold)
  s11v4_glow.png          one soft glow (nine copies sit on the lake at the end, one under each light)

Run from the repository root: python3 assets/song_figures/s11/make_v4_shapes.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 2400, 300
BASE = 292
CX = W // 2


def battlements(draw, x0, top, n, step, fill):
    for k in range(n):
        mx = x0 + 6 + k * step
        draw.rectangle([mx, top - 12, mx + 12, top], fill=fill, outline=255, width=3)


def city(draw, filled):
    lw = 5
    fill = 105 if filled else 0
    # outer wall with battlements, stepping up toward the centre
    blocks = []
    x = 150
    while x < W - 150:
        d = abs(x + 50 - CX) / (CX - 150)
        blocks.append((x, int(200 + 40 * d), x + 100))
        x += 100
    for (x0, top, x1) in blocks:
        if filled:
            draw.rectangle([x0, top, x1, BASE], fill=fill)
        battlements(draw, x0, top, 4, 25, fill)
    pts = [(150, BASE)]
    for (x0, top, x1) in blocks:
        pts += [(x0, top), (x1, top)]
    pts += [(W - 150, BASE)]
    draw.line(pts, fill=255, width=lw)
    draw.line([(140, BASE), (W - 140, BASE)], fill=255, width=lw)
    # towers along the wall
    for tx, top in ((330, 120), (620, 95), (900, 70), (1500, 70), (1780, 95), (2070, 120)):
        draw.rectangle([tx - 30, top, tx + 30, BASE], fill=fill, outline=255, width=lw)
        battlements(draw, tx - 32, top, 3, 20, fill)
        if filled:
            for wy in range(top + 25, BASE - 20, 40):
                draw.rectangle([tx - 7, wy, tx + 7, wy + 16], fill=255)
    # the gate house: two tall towers, the wall between them and a high round arch, open in the middle
    for gx in (CX - 150, CX + 150):
        draw.rectangle([gx - 45, 20, gx + 45, BASE], fill=fill, outline=255, width=lw)
        battlements(draw, gx - 47, 20, 4, 22, fill)
        if filled:
            for wy in range(50, BASE - 30, 45):
                draw.rectangle([gx - 9, wy, gx + 9, wy + 20], fill=255)
    draw.rectangle([CX - 105, 60, CX + 105, BASE], fill=fill, outline=255, width=lw)
    r = 70
    draw.rectangle([CX - r, 150, CX + r, BASE], fill=0)
    draw.pieslice([CX - r, 150 - r, CX + r, 150 + r], 180, 360, fill=0)
    draw.arc([CX - r, 150 - r, CX + r, 150 + r], 180, 360, fill=255, width=lw + 2)
    draw.line([(CX - r, 150), (CX - r, BASE)], fill=255, width=lw + 2)
    draw.line([(CX + r, 150), (CX + r, BASE)], fill=255, width=lw + 2)
    draw.arc([CX - r - 18, 150 - r - 18, CX + r + 18, 150 + r + 18], 180, 360, fill=255, width=3)
    if filled:
        # the open gate full of light
        draw.rectangle([CX - r + 8, 150, CX + r - 8, BASE - 3], fill=150)
        draw.pieslice([CX - r + 8, 150 - r + 8, CX + r - 8, 150 + r - 8], 180, 360, fill=150)


for name, filled in (("s11v4_city_outline.png", False), ("s11v4_city_gold.png", True)):
    im = Image.new("L", (W, H), 0)
    city(ImageDraw.Draw(im), filled)
    im.filter(ImageFilter.GaussianBlur(1.0)).convert("RGB").save(os.path.join(OUT, name), optimize=True)

# one soft glow, a little taller than wide, like a light resting on still water
n = 240
yy, xx = np.mgrid[0:n, 0:n].astype(np.float64)
cx, cy = n / 2, n * 0.62
g = np.exp(-(((xx - cx) / 26.0) ** 2 + ((yy - cy) / 34.0) ** 2))
g += 0.35 * np.exp(-(((xx - cx) / 9.0) ** 2 + ((yy - cy) / 80.0) ** 2))
g = np.clip(g / g.max(), 0, 1)
Image.fromarray((g * 255).astype(np.uint8)).convert("RGB").save(os.path.join(OUT, "s11v4_glow.png"), optimize=True)
