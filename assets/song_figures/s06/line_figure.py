"""Turns Anthony's two filled special figures (white bodies with black drawn lines, from the Drive folder Assets/s06)
into the line-art look of the shared library, so the people of light keep their drawn folds instead of glowing as
flat white shapes. Run after tools/prepare_figure.py:
  python3 assets/song_figures/s06/line_figure.py assets/song_figures/s06/s06_concession_step_aside.png
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

for path in sys.argv[1:]:
    g = np.asarray(Image.open(path).convert("L")).astype(np.float64) / 255
    body = ndimage.binary_fill_holes(ndimage.binary_closing(g > 0.5, iterations=3))
    inner = ndimage.binary_erosion(body, iterations=2)
    lines = (g < 0.45) & inner                                       # the drawn folds inside the body
    lines = ndimage.binary_dilation(lines, iterations=1)
    rim = body & ~ndimage.binary_erosion(body, iterations=3)         # the outline of the body
    out = 0.12 * body + 0.95 * (lines | rim)
    out = ndimage.gaussian_filter(out, 0.7)
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(path)
    print("lined", path)
