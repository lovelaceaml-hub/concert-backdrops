"""Turns a generated pose picture (white line art on black) into an engine figure pose.

Usage: python tools/prepare_figure.py <source image> <assets/figures/name.png>
Grayscale, ground lines removed, the drawing scaled to 940 pixels tall and centred on a 1536x1024 black canvas with
the feet on the same line (y = 1000), so every pose of a figure lines up when the sparks move between poses.
"""
import sys

import numpy as np
from PIL import Image

CANVAS_W, CANVAS_H, CONTENT_H, FEET_Y = 1536, 1024, 940, 1000


def prepare(src, dst):
    g = np.asarray(Image.open(src).convert("L")).astype(np.float32) / 255.0
    g = np.clip((g - 0.06) / 0.94, 0.0, 1.0)
    h, w = g.shape
    # long horizontal lines (a drawn floor) are not part of the people
    bright = (g > 0.35).mean(axis=1)
    for y in np.nonzero(bright > 0.30)[0]:
        g[max(y - 4, 0):y + 5] = 0.0
    ys, xs = np.nonzero(g > 0.25)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = Image.fromarray((g[y0:y1, x0:x1] * 255).astype(np.uint8))
    s = CONTENT_H / (y1 - y0)
    cw = int(round((x1 - x0) * s))
    if cw > CANVAS_W - 40:
        s = (CANVAS_W - 40) / (x1 - x0)
        cw = CANVAS_W - 40
    ch = int(round((y1 - y0) * s))
    crop = crop.resize((cw, ch), Image.LANCZOS)
    out = Image.new("L", (CANVAS_W, CANVAS_H), 0)
    out.paste(crop, ((CANVAS_W - cw) // 2, FEET_Y - ch))
    out.save(dst, optimize=True)
    return dst


if __name__ == "__main__":
    print(prepare(sys.argv[1], sys.argv[2]))
