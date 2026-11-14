"""Song 07 only: "answered from the windows". From the calmed village plate, make variants where the warm windows,
doorways and lanterns are dark, then light up band by band from the near house to the far end of the village.
Usage: python windows.py <original village plate> <calmed village plate> <out dir>
Writes village_w0.jpg (all dark) .. village_w3.jpg (three bands lit); the calmed plate itself is the last step.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

orig = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(np.float32) / 255
calm = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(np.float32) / 255
out = sys.argv[3]
h, w, _ = orig.shape
r, g, b = orig[..., 0], orig[..., 1], orig[..., 2]
lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
warm = ((r > 0.55) & (r - b > 0.25) & (lum > 0.38)).astype(np.float32)
warm[int(h * 0.66):] = 0.0                      # leave the calmed water alone
warm[:int(h * 0.20)] = 0.0                      # and the sunset sky
warm[:int(h * 0.30), int(w * 0.38):] = 0.0
m = Image.fromarray((warm * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(14))
m = np.clip(np.asarray(m).astype(np.float32) / 255 * 1.8, 0, 1)
ll = (calm @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
dark = (ll + 0.35 * (calm - ll)) * 0.30 * np.array([0.85, 0.9, 1.15], dtype=np.float32)
xs = np.arange(w, dtype=np.float32) / w
bands = [0.0, 0.30, 0.52, 0.72, 1.01]
for k in range(4):
    # bands below k are lit, the rest dark (soft band edges)
    lit_to = bands[k]
    off = np.clip((xs - lit_to) / 0.02 + 0.5, 0, 1)[None, :] if k > 0 else np.ones((1, w), np.float32)
    mk = (m * off)[..., None]
    img = calm * (1 - mk) + dark * mk
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(f"{out}/village_w{k}.jpg", quality=86)
    print(k)
