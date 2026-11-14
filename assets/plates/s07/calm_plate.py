"""Song 07 only: calm the lower third of a plate (Astra / attacker finding: busy reflections under the performers).
Below `top` (fraction of the height from the bottom, default 0.35) the picture is smeared sideways (softens the
reflection streaks), its saturation halved and its brightness brought to `level` (default 0.5), with a soft ramp.
Usage: python calm_plate.py src dst [top] [level]
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
top = float(sys.argv[3]) if len(sys.argv) > 3 else 0.35
level = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
im = Image.open(src).convert("RGB")
w, h = im.size
a = np.asarray(im).astype(np.float32) / 255.0
# sideways smear: a wide horizontal blur blended with a light overall blur
hb = np.asarray(im.filter(ImageFilter.BoxBlur(0)).resize((w // 24, h), Image.BILINEAR).resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
sb = np.asarray(im.filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
smear = 0.6 * hb + 0.4 * sb
lum = (smear @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
calm = (lum + 0.5 * (smear - lum)) * level
yb = 1.0 - (np.arange(h, dtype=np.float32) + 0.5) / h          # height from the bottom
k = np.clip((top + 0.04 - yb) / 0.08, 0.0, 1.0)
k = (k * k * (3 - 2 * k))[:, None, None]
out = a * (1 - k) + calm * k
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst, quality=88)
print(dst)
