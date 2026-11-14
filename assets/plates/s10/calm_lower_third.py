"""Calms the lower third of the song 10 plates (Astra round 2: the lamp's gold road was the brightest thing under
the performers). Below 40 percent of the height from the bottom the picture is dimmed smoothly to 62 percent at
15 percent and below, and highlights there are compressed (no bright glints), so the stage stays quiet.

The originals are in Anthony's Drive folder (Assets/s10/s10_plate1 to s10_plate6). Run once on the originals:
python3 assets/plates/s10/calm_lower_third.py <in.jpg> <out.jpg>
"""
import sys

import numpy as np
from PIL import Image


def main(src, dst):
    a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255.0
    h = a.shape[0]
    yb = 1.0 - (np.arange(h) + 0.5) / h                     # height from the bottom
    u = np.clip((0.40 - yb) / 0.25, 0.0, 1.0)
    u = u * u * (3 - 2 * u)
    dim = (1.0 - 0.38 * u)[:, None, None]
    lum = a.mean(axis=2, keepdims=True)
    knee = 0.42
    comp = np.where(lum > knee, knee + (lum - knee) * 0.35, lum) / np.maximum(lum, 1e-4)
    k = u[:, None, None]
    a = a * (1 - k + k * comp) * dim
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst, quality=90)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
