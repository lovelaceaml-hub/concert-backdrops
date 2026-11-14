"""Song 07 only: turn a filled glowing figure into outline art, then size it like tools/prepare_figure.py
(1536x1024, 940 px tall, feet on y = 1000) without the row wipe that erased filled figures.
Usage: python prep_outline.py src dst [row@x0:x1] [y0:y1,x0:x1]
The optional cuts erase a drawn ground line after the outline is made (so the cut leaves no edge of its own):
everything below `row` except columns x0:x1 (the feet), and a rectangle.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

CANVAS_W, CANVAS_H, CONTENT_H, FEET_Y = 1536, 1024, 940, 1000

src, dst = sys.argv[1], sys.argv[2]
g = np.asarray(Image.open(src).convert("L")).astype(np.float32) / 255.0
sm = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
gy, gx = np.gradient(sm)
e = np.hypot(gx, gy)
e = np.clip(e / np.percentile(e[e > 0.004], 97), 0, 1) ** 0.8
out = np.clip(np.maximum(e, 0.22 * g), 0, 1)
out[g < 0.04] = 0.0
if len(sys.argv) > 3:
    row, keep = sys.argv[3].split("@")
    row = int(row)
    x0, x1 = map(int, keep.split(":"))
    sub = out[row:, x0:x1].copy()
    out[row:] = 0.0
    out[row:, x0:x1] = sub
if len(sys.argv) > 4:
    (a, b), (c, d) = [tuple(map(int, p.split(":"))) for p in sys.argv[4].split(",")]
    out[a:b, c:d] = 0.0
ys, xs = np.nonzero(out > 0.2)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
crop = Image.fromarray((out[y0:y1, x0:x1] * 255).astype(np.uint8))
s = CONTENT_H / (y1 - y0)
cw, ch = int(round((x1 - x0) * s)), int(round((y1 - y0) * s))
crop = crop.resize((cw, ch), Image.LANCZOS)
canvas = Image.new("L", (CANVAS_W, CANVAS_H), 0)
canvas.paste(crop, ((CANVAS_W - cw) // 2, FEET_Y - ch))
canvas.save(dst, optimize=True)
print(dst, (x1 - x0, y1 - y0))
