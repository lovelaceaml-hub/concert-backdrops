"""Builds song 06's own pose pictures from the shared library (assets/figures/), so its acts differ from other songs.
Run: python3 assets/song_figures/s06/make_poses.py  (writes the PNGs next to this file; same size and feet line as the
library, so no tools/prepare_figure.py pass is needed).

Concession, "Please, after you." (they meet from opposite sides on the narrow path):
  s06_concession_1.png  both arrive at the same spot from opposite sides and stop (library concession_a)
  s06_concession_2.png  the left one steps aside with an open arm; the other still waits, facing them
  s06_concession_3.png  the other has walked past to the left, bowing in thanks; the one who yielded turns to see them off
Inclusiveness, "It's okay. I understand." (the young one dropped the family's lantern in the lake):
  s06_inclusiveness_1.png  the young one (veiled) kneels at the water's edge, sorry; the older one stands over them
  s06_inclusiveness_2.png  the older one rests a hand on their back and lifts the relit lantern high
  s06_inclusiveness_3.png  standing, hands joined, the lantern hangs between them: it is given back
"""
import os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "..", "figures")


def load(name):
    return np.asarray(Image.open(os.path.join(LIB, name + ".png")).convert("L")).astype(np.float32)


def people(img, split):
    """Splits a two-person pose into (left, right) by connected strokes, grouped by their centre."""
    lab, n = ndimage.label(img > 24, structure=np.ones((3, 3)))
    left = np.zeros_like(img)
    right = np.zeros_like(img)
    for k, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        m = lab[sl] == k
        cx = (sl[1].start + sl[1].stop) / 2
        tgt = left if cx < split else right
        tgt[sl][m] = img[sl][m]
    # faint fill between strokes goes with the nearer side
    rest = (img > 0) & (left == 0) & (right == 0)
    xs = np.arange(img.shape[1])[None, :].repeat(img.shape[0], 0)
    left[rest & (xs < split)] = img[rest & (xs < split)]
    right[rest & (xs >= split)] = img[rest & (xs >= split)]
    return left, right


def shift(a, dx):
    out = np.zeros_like(a)
    if dx >= 0:
        out[:, dx:] = a[:, :a.shape[1] - dx]
    else:
        out[:, :dx] = a[:, -dx:]
    return out


def place(a, cx):
    """Moves a single person so the centre of their drawing is at column cx."""
    cols = np.nonzero(a.max(axis=0) > 24)[0]
    return shift(a, int(cx - (cols[0] + cols[-1]) / 2))


def lantern(img, cx, top, w=46, h=64, handle=True):
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    if handle:
        d.arc([cx - w * 0.35, top - h * 0.30, cx + w * 0.35, top + h * 0.20], 180, 360, fill=235, width=4)
    d.rectangle([cx - w * 0.45, top, cx + w * 0.45, top + 8], fill=235)
    d.rounded_rectangle([cx - w / 2, top + 8, cx + w / 2, top + h], radius=10, fill=170, outline=245, width=4)
    d.line([cx, top + 12, cx, top + h - 4], fill=245, width=3)
    d.rectangle([cx - w * 0.45, top + h, cx + w * 0.45, top + h + 8], fill=235)
    return np.asarray(im).astype(np.float32)


def save(a, name):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(HERE, name))
    print("wrote", name)


if __name__ == "__main__":
    ca, cb = load("concession_a"), load("concession_b")
    a_l, a_r = people(ca, 790)
    b_l, b_r = people(cb, 760)
    save(ca, "s06_concession_1.png")
    save(np.maximum(b_l, a_r), "s06_concession_2.png")
    # both mirrored: the elder has walked past to the left, bowing; the one who yielded, a step further aside,
    # turns with the open arm to see them on their way
    save(np.maximum(place(b_r[:, ::-1], 360), place(b_l[:, ::-1], 800)), "s06_concession_3.png")

    ea, eb, ac = load("encouragement_a"), load("encouragement_b"), load("apology_c")
    save(ea, "s06_inclusiveness_1.png")
    save(lantern(eb, int(os.environ.get("HX", 335)), int(os.environ.get("HY", 172)) - 80), "s06_inclusiveness_2.png")
    save(lantern(ac, int(os.environ.get("JX", 762)), int(os.environ.get("JY", 470)), handle=False),
         "s06_inclusiveness_3.png")
