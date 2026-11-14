"""Renders the words (label + expression) as textures and as particle targets."""
import os
import zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import song as S

FONTS = os.path.join(S.ROOT, "fonts")
F_PHRASE = os.path.join(FONTS, "cormorant-garamond-latin-700-italic.ttf")
F_TITLE = os.path.join(FONTS, "cormorant-garamond-latin-700-normal.ttf")
F_LABEL = os.path.join(FONTS, "jost-latin-500-normal.ttf")
F_TAG = os.path.join(FONTS, "cormorant-garamond-latin-600-italic.ttf")

W, H = S.W, S.H
Y_CENTER = 0.392 * H     # centre of the words, measured from the top
MAX_W = 1580


def _fit(lines, path, size):
    while True:
        f = ImageFont.truetype(path, size)
        wmax = max(f.getlength(l) for l in lines)
        if wmax <= MAX_W or size <= 60:
            return f, size
        size -= 2


def _tracked(draw, xy_center, text, font, tracking, fill):
    widths = [font.getlength(c) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy_center[0] - total / 2.0
    for c, w in zip(text, widths):
        draw.text((x, xy_center[1]), c, font=font, fill=fill, anchor="ls")
        x += w + tracking
    return total


def render(label, lines, size, font_path=F_PHRASE, label_alpha=232):
    """Returns (rgb texture uint8 HxWx3 bottom-up, particle targets Nx3, bounds)."""
    font, size = _fit(lines, font_path, size)
    asc, desc = font.getmetrics()
    line_h = int(size * 1.08)
    block_h = line_h * len(lines)
    top = Y_CENTER - block_h / 2.0
    phrase = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(phrase)
    x0, x1 = W, 0
    for i, l in enumerate(lines):
        base = top + i * line_h + asc * 0.80
        d.text((W / 2.0, base), l, font=font, fill=255, anchor="ms")
        wl = font.getlength(l)
        x0, x1 = min(x0, W / 2 - wl / 2), max(x1, W / 2 + wl / 2)
    lab = Image.new("L", (W, H), 0)
    if label:
        lf = ImageFont.truetype(F_LABEL, 32)
        ld = ImageDraw.Draw(lab)
        _tracked(ld, (W / 2.0, top - 34), label.upper(), lf, 15.0, label_alpha)
    sharp = np.maximum(np.asarray(phrase), np.asarray(lab))
    both = Image.fromarray(sharp)
    glow = np.asarray(both.filter(ImageFilter.GaussianBlur(9)))
    back = both.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(46))
    back = np.clip(np.asarray(back).astype(np.float32) * 2.4, 0, 255).astype(np.uint8)
    tex = np.dstack([sharp, glow, back])[::-1].copy()
    # particle targets from the expression itself (not the label)
    a = np.asarray(phrase).astype(np.float64)
    area = float((a > 128).sum())
    n = int(np.clip(area / 2.0, 9000, 22000))
    rng = np.random.default_rng(zlib.crc32(" ".join(lines).encode("utf-8")))
    p = (a / a.sum()).ravel()
    idx = rng.choice(a.size, size=n, p=p)
    ys, xs = np.divmod(idx, W)
    px = xs + rng.random(n)
    py = ys + rng.random(n)
    order = (px - x0) / max(x1 - x0, 1.0)
    targets = np.stack([px / W, 1.0 - py / H, order], axis=1).astype("f4")
    seeds = rng.random((n, 4)).astype("f4")
    return tex, np.hstack([targets, seeds]), (x0 / W, x1 / W)


def render_tagline(text):
    f = ImageFont.truetype(F_TAG, 68)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    y = Y_CENTER + 158
    d.text((W / 2.0, y), text, font=f, fill=250, anchor="ms")
    wl = f.getlength(text)
    sharp = np.asarray(img)
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(6)))
    back = img.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(36))
    back = np.clip(np.asarray(back).astype(np.float32) * 2.2, 0, 255).astype(np.uint8)
    return np.dstack([sharp, glow, back])[::-1].copy(), ((W / 2 - wl / 2) / W, (W / 2 + wl / 2) / W)


def render_credit(song_title, concert_title):
    """Song title with the concert title beneath it, centred where the expressions appear."""
    fs, _ = _fit([song_title], F_TITLE, 128)
    fc, _ = _fit([concert_title], F_TAG, 64)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    y1 = Y_CENTER + 10
    d.text((W / 2.0, y1), song_title, font=fs, fill=255, anchor="ms")
    d.text((W / 2.0, y1 + 92), concert_title, font=fc, fill=240, anchor="ms")
    sharp = np.asarray(img)
    ys, xs = np.nonzero(sharp > 8)
    bbox = (xs.min() / W, (xs.max() + 1) / W, 1.0 - (ys.max() + 1) / H, 1.0 - ys.min() / H)
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(9)))
    back = img.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(40))
    back = np.clip(np.asarray(back).astype(np.float32) * 2.2, 0, 255).astype(np.uint8)
    return np.dstack([sharp, glow, back])[::-1].copy(), bbox


def build_all():
    out = []
    for p in S.PHRASES:
        tex, pts, b = render(p["label"], p["lines"], p["size"])
        out.append(dict(tex=tex, pts=pts, bounds=b))
    tex, pts, b = render(S.TITLE["label"], S.TITLE["lines"], S.TITLE["size"], font_path=F_TITLE)
    title = dict(tex=tex, pts=pts, bounds=b)
    ttex, tb = render_tagline(S.TAGLINE["text"])
    return out, title, dict(tex=ttex, bounds=tb)


if __name__ == "__main__":
    ph, title, tag = build_all()
    for p, d in zip(S.PHRASES + [S.TITLE], ph + [title]):
        print(p["label"], d["pts"].shape[0], "particles, x", [round(v, 3) for v in d["bounds"]])
    Image.fromarray(ph[1]["tex"][::-1, :, 0]).save(os.path.join(S.ROOT, "work", "text_check.png"))
