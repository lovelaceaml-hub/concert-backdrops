"""Turns the song 10 special figure (Heavenly Mother from behind, fully robed, holding the lamp low) into the
engine's figure format: white line art on black, 1536x1024, drawing 940 px tall, feet 24 px above the bottom.

The original picture is a filled white robe with grey fold lines; the engine wants lines with a faint fill, so the
outline and the folds become lines and the robe keeps a soft inner fill (tools/prepare_figure.py would erase the
filled body). Run: python3 assets/plates/s10/prepare_mother.py <s10_mother_lamp_a.png> assets/figures/s10_mother_lamp_a.png
"""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def main(src, dst):
    g = np.asarray(Image.open(src).convert("L")).astype(np.float32) / 255.0
    mask = ndi.binary_fill_holes(ndi.gaussian_filter(g, 1.0) > 0.35)
    mask = ndi.binary_opening(mask, iterations=2)
    edge = mask ^ ndi.binary_erosion(mask, iterations=3)
    folds = np.clip((0.96 - g) * 6.0, 0.0, 1.0) * ndi.binary_erosion(mask, iterations=3)
    glow = np.clip((g - 0.15) * 1.5, 0, 1) * (~mask)          # the lamp's halo by the hands
    art = np.maximum.reduce([edge.astype(np.float32), folds, 0.12 * mask.astype(np.float32), glow * 0.8])
    art = ndi.gaussian_filter(art, 0.6)
    ys, xs = np.nonzero(art > 0.05)
    art = art[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h = 940
    w = int(round(art.shape[1] * h / art.shape[0]))
    im = Image.fromarray((np.clip(art, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    out = Image.new("L", (1536, 1024), 0)
    out.paste(im, ((1536 - w) // 2, 1024 - 24 - h))
    out.save(dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
