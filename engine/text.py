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

# HOWTO Q: text is drawn at the output resolution. K is 1 at 1080p (everything exactly as before) and 2 at 4K, where
# every size and distance below, given in 1080p pixels, is multiplied by K.
try:
    import output as _output
    K = float(_output.scale(S))
except ImportError:
    K = 1.0
if abs(K - 1.0) < 1e-9:
    K = 1


def _k(v):
    """A 1080p distance in output pixels (unchanged at 1080p)."""
    return v if K == 1 else v * K


def _px(size):
    """A 1080p font size in output pixels (unchanged at 1080p)."""
    return int(size) if K == 1 else int(round(size * K))


W, H = (S.W, S.H) if K == 1 else (int(round(S.W * K)), int(round(S.H * K)))
Y_CENTER = 0.392 * H     # centre of the words, measured from the top
MAX_W = _k(1580)
END_TITLE_Y = 0.315      # centre of the title on a three-line end card (the lines sit under it, above the lower third)


def shield(img, reach=1.25, gain=1.6):
    """A wide, soft field round the letters (0..1, top row first), used to dim the scene and the light behind
    the text (Astra round 1, finding 3). It fills the space between lines and reaches about 70 px out."""
    from scipy import ndimage as ndi
    a = np.asarray(img).astype(np.float32) / 255.0
    h, w = a.shape
    b = 4 if K == 1 else int(round(4 * K))   # blocks of 4 px at 1080p
    small = a[: h - h % b, : w - w % b].reshape(h // b, b, w // b, b).max(axis=(1, 3))
    small = ndi.maximum_filter(small, size=int(round(7 * reach)) | 1)
    small = ndi.gaussian_filter(small, 9.0 * reach)
    small = np.clip(small * gain, 0.0, 1.0)
    big = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    return np.asarray(big)


def _fit(lines, path, size):
    while True:
        f = ImageFont.truetype(path, _px(size))
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


def render(label, lines, size, font_path=F_PHRASE, label_alpha=232, y_center=None):
    """Returns (rgb texture uint8 HxWx3 bottom-up, particle targets Nx3, bounds)."""
    font, size = _fit(lines, font_path, size)
    asc, desc = font.getmetrics()
    line_h = int(_k(size) * 1.08)
    block_h = line_h * len(lines)
    top = (Y_CENTER if y_center is None else y_center * H) - block_h / 2.0
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
        lf = ImageFont.truetype(F_LABEL, _px(32))
        ld = ImageDraw.Draw(lab)
        _tracked(ld, (W / 2.0, top - _k(34)), label.upper(), lf, _k(15.0), label_alpha)
    sharp = np.maximum(np.asarray(phrase), np.asarray(lab))
    both = Image.fromarray(sharp)
    glow = np.asarray(both.filter(ImageFilter.GaussianBlur(_k(9))))
    back = shield(both)
    tex = np.dstack([sharp, glow, back])[::-1].copy()
    # particle targets from the expression itself (not the label)
    a = np.asarray(phrase).astype(np.float64)
    area = float((a > 128).sum())
    n = int(np.clip(area / (2.0 * K * K), 9000, 22000))
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


def render_tagline(text, title_y=None):
    """Closing lines under the title. A newline starts another line; long lines shrink to the safe width.

    One or two lines: the original layout. Three or more lines (the phase 2 end card, PHASE2.md item 7): the first
    line (the peace tagline) is larger, the date and the place smaller beneath it, all above the lower third.
    """
    lines = text.split("\n")
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    if len(lines) < 3:
        f, size = _fit(lines, F_TAG, 68)
        y = Y_CENTER + _k(158)
        for k, line in enumerate(lines):
            d.text((W / 2.0, y + k * _k(size) * 1.25), line, font=f, fill=250, anchor="ms")
        wl = max(f.getlength(l) for l in lines)
    else:
        ty = (title_y if title_y is not None else END_TITLE_Y) * H
        f1, s1 = _fit(lines[:1], F_TAG, 64)
        f2, s2 = _fit(lines[1:], F_TAG, 48)
        y = ty + _k(81) + _k(82)               # under the title block (title size 150)
        d.text((W / 2.0, y), lines[0], font=f1, fill=252, anchor="ms")
        y += _k(s1) * 0.55 + _k(s2) * 1.05
        for line in lines[1:]:
            d.text((W / 2.0, y), line, font=f2, fill=238, anchor="ms")
            y += _k(s2) * 1.25
        wl = max([f1.getlength(lines[0])] + [f2.getlength(l) for l in lines[1:]])
    sharp = np.asarray(img)
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(_k(6))))
    back = shield(img)
    return np.dstack([sharp, glow, back])[::-1].copy(), ((W / 2 - wl / 2) / W, (W / 2 + wl / 2) / W)


def render_fragment(text, dy=0.0, size=74):
    """A short lyric fragment in the light italic serif, centred, dy (fraction of height) above the expression line."""
    f = ImageFont.truetype(F_TAG, _px(size))
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    y = Y_CENTER - dy * H
    d.text((W / 2.0, y), text, font=f, fill=250, anchor="ms")
    wl = f.getlength(text)
    sharp = np.asarray(img)
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(_k(6))))
    back = shield(img, reach=1.0)
    return np.dstack([sharp, glow, back])[::-1].copy(), ((W / 2 - wl / 2) / W, (W / 2 + wl / 2) / W)


def render_credit(song_title, concert_title):
    """Song title with the concert title beneath it, centred where the expressions appear."""
    fs, _ = _fit([song_title], F_TITLE, 128)
    fc, _ = _fit([concert_title], F_TAG, 64)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    y1 = Y_CENTER + _k(10)
    d.text((W / 2.0, y1), song_title, font=fs, fill=255, anchor="ms")
    d.text((W / 2.0, y1 + _k(92)), concert_title, font=fc, fill=240, anchor="ms")
    sharp = np.asarray(img)
    ys, xs = np.nonzero(sharp > 8)
    bbox = (xs.min() / W, (xs.max() + 1) / W, 1.0 - (ys.max() + 1) / H, 1.0 - ys.min() / H)
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(_k(9))))
    back = shield(img)
    return np.dstack([sharp, glow, back])[::-1].copy(), bbox


def title_y():
    """Centre of the closing title (fraction from the top): TITLE y= if set; raised for a three-line end card."""
    if "y" in S.TITLE:
        return S.TITLE["y"]
    return END_TITLE_Y if len(S.TAGLINE["text"].split("\n")) >= 3 else None


def build_all():
    out = []
    for p in S.PHRASES:
        tex, pts, b = render(p["label"], p["lines"], p["size"], y_center=p.get("y"))   # optional y: centre, from the top
        out.append(dict(tex=tex, pts=pts, bounds=b))
    ty = title_y()
    tex, pts, b = render(S.TITLE["label"], S.TITLE["lines"], S.TITLE["size"], font_path=F_TITLE, y_center=ty)
    title = dict(tex=tex, pts=pts, bounds=b)
    ttex, tb = render_tagline(S.TAGLINE["text"], ty)
    frags = []
    for fr in getattr(S, "FRAGMENTS", []):
        ftex, fb = render_fragment(fr["text"], fr.get("dy", 0.0), fr.get("size", 74))
        frags.append(dict(tex=ftex, bounds=fb, meta=fr))
    return out, title, dict(tex=ttex, bounds=tb, frags=frags)


if __name__ == "__main__":
    ph, title, tag = build_all()
    for p, d in zip(S.PHRASES + [S.TITLE], ph + [title]):
        print(p["label"], d["pts"].shape[0], "particles, x", [round(v, 3) for v in d["bounds"]])
    Image.fromarray(ph[1]["tex"][::-1, :, 0]).save(os.path.join(S.ROOT, "work", "text_check.png"))
