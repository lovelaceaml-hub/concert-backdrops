"""Song 07 only: poses made from the shared library (assets/figures/), kept on the same 1536x1024 canvas.
- s07_helper_greet_a / _b: only the helper (left person) of greeting_a / greeting_b, so the seated traveler on the
  bench is the one being greeted (no second, standing lonely figure).
- s07_lantern_pair: two walking helpers from greeting_a, each holding up a lantern (the lantern drawn from
  Heavenly Mother's lamp picture, Drive Assets/s07/figures), the front pair of the lantern procession.
Usage: python helpers.py <repo root> <mother lamp source picture>
"""
import sys
import numpy as np
from PIL import Image

root, lamp_src = sys.argv[1], sys.argv[2]
lib = root + "/assets/figures/"
dst = root + "/assets/song_figures/s07/"


def load(name):
    return np.asarray(Image.open(lib + name).convert("L")).astype(np.float32)


def save(a, name):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(dst + name, optimize=True)


ga, gb = load("greeting_a.png"), load("greeting_b.png")
a = ga.copy(); a[:, 900:] = 0
save(a, "s07_helper_greet_a.png")
b = gb.copy(); b[:, 812:] = 0
save(b, "s07_helper_greet_b.png")

# the lantern: cut from the lamp picture (682x1024), scaled to about 120 px tall
lm = np.asarray(Image.open(lamp_src).convert("L")).astype(np.float32)
lan = lm[60:185, 430:520]
lan = np.where(lan > 40, lan, 0)
li = Image.fromarray(lan.astype(np.uint8)).resize((104, 145), Image.LANCZOS)
lan = np.asarray(li).astype(np.float32)

bearer = ga.copy(); bearer[:, 900:] = 0
hx, hy = 712, 228          # the raised hand of the walking helper
y0, x0 = hy, hx - lan.shape[1] // 2
bearer[y0:y0 + lan.shape[0], x0:x0 + lan.shape[1]] = np.maximum(bearer[y0:y0 + lan.shape[0], x0:x0 + lan.shape[1]], lan)
pair = bearer.copy()
shift = 520
pair[:, shift:] = np.maximum(pair[:, shift:], bearer[:, :-shift])
# keep the drawing inside the canvas width and centred like the library poses
ys, xs = np.nonzero(pair > 60)
cx = (xs.min() + xs.max()) // 2
pair = np.roll(pair, 768 - cx, axis=1)
save(pair, "s07_lantern_pair.png")
print("ok", xs.min(), xs.max())
