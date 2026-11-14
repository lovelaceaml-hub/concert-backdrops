"""Turns a generated pose picture (white line art on black) into an engine figure pose.

Usage: python tools/prepare_figure.py <source image> <assets/figures/name.png> [--keep-lines]
--keep-lines skips the floor-line removal (for filled figures or wide groups, if a thin band is wrongly removed).
Grayscale, ground lines removed, the drawing scaled to 940 pixels tall and centred on a 1536x1024 black canvas with
the feet on the same line (y = 1000), so every pose of a figure lines up when the sparks move between poses.
"""
import sys

import numpy as np
from PIL import Image

CANVAS_W, CANVAS_H, CONTENT_H, FEET_Y = 1536, 1024, 940, 1000


MAX_LINE_ROWS = 10   # a drawn floor line is at most this many rows thick; filled bodies and wide groups are taller


def remove_floor_lines(g):
    """Erases thin, wide horizontal lines (a drawn floor). A run of bright rows thicker than MAX_LINE_ROWS is a
    filled figure or a wide group, not a line, and is kept."""
    bright = (g > 0.35).mean(axis=1) > 0.30
    y, h = 0, len(bright)
    while y < h:
        if not bright[y]:
            y += 1
            continue
        y1 = y
        while y1 < h and bright[y1]:
            y1 += 1
        if y1 - y <= MAX_LINE_ROWS:
            g[max(y - 4, 0):y1 + 4] = 0.0
        y = y1
    return g


def prepare(src, dst, keep_lines=False):
    g = np.asarray(Image.open(src).convert("L")).astype(np.float32) / 255.0
    g = np.clip((g - 0.06) / 0.94, 0.0, 1.0)
    h, w = g.shape
    if not keep_lines:   # thin long horizontal lines (a drawn floor) are not part of the people
        g = remove_floor_lines(g)
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
    args = [a for a in sys.argv[1:] if a != "--keep-lines"]
    print(prepare(args[0], args[1], keep_lines="--keep-lines" in sys.argv[1:]))
