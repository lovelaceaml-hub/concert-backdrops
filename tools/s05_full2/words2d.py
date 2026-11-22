"""Song 05 "God Bless You!", version 2: the words on screen, laid out once (no drawing here; overlay05.py draws).

Why 2D: song 05 is the concert's bright spring afternoon, and on a bright sky the words are navy #1f2a6b with a
soft white glow (DESIGN-SYSTEM 7, PHASEB). The approved Revision 3 words are made of light (additive points),
which can never be navy, so this song keeps their craft (Cormorant serif phrase, a coloured capsule label above,
upper middle of the frame, still while read, never mirrored) and draws them as one crisp layer over the picture.

Every time here is REFERENCE time r (see timing.py; stage time is timing.K * r). Sizes are 1080p pixels.

    bless           "God bless you!"        verse 1, line 1     petals blow in and settle into the letters
    Encouragement   (exact campaign words)  verse 1, line 2     the one who prays kneels for his brother
    father          "Father's great love"   verse 1, line 3     a shaft of afternoon sun writes it, top down
    Consideration   (exact campaign words)  verse 1, line 4     a hand offered to the brother
    fruit           "good fruit"            verse 1, line 6     golden fruit ripen into the letters
    Encouragement2  (the same words)        verse 2, line 2     all three pray for the sister
    Respect         (exact campaign words)  verse 2, line 3     "In her tender voice": the brother listens
    Consideration2  (the same words)        verse 2, line 4     a young woman helps the sister up
    blessing        "God bless you!"        the calm hold       seeds of light rise from the tree into it

Only one of these is ever on screen at a time (checked by check()). Expressions leave by gathering into their
star of the arch; fragments leave in their own way.
No em dash or en dash anywhere in this file.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "fonts"
NAVY = (31, 42, 107)

# the exact campaign wording, from engine/p3d/words.py EXPRESSIONS at the approved tag (never retyped)
_EXPR = None


def expressions():
    global _EXPR
    if _EXPR is None:
        src = (ROOT / "engine/p3d/words.py").read_text()
        a = src.index("EXPRESSIONS = [")
        b = src.index("]\n", a) + 1
        lst = eval(compile(src[a + len("EXPRESSIONS = "):b], "words.py", "eval"), {"__builtins__": {}, "dict": dict})
        _EXPR = {e["label"]: e for e in lst}
    return _EXPR


# name: (kind, expression label or text, arrive, leave, t_in, t_read0, t_read1, t_out)
TIMELINE = [
    ("bless", "frag", "God bless you!", "petals", "petals_away", 15.4, 17.4, 21.6, 23.8),
    ("Encouragement", "expr", "Encouragement", "pen", "star", 24.8, 26.4, 35.4, 37.4),
    ("father", "frag", "Father’s great love", "sunbeam", "rise", 43.4, 45.4, 51.2, 53.2),
    ("Consideration", "expr", "Consideration", "pen", "star", 55.8, 57.4, 66.4, 68.4),
    ("fruit", "frag", "good fruit", "ripen", "fall", 76.4, 78.0, 82.4, 84.2),
    ("Encouragement2", "expr", "Encouragement", "pen", "star", 94.4, 96.0, 105.0, 107.0),
    ("Respect", "expr", "Respect", "pen", "star", 109.4, 111.0, 119.6, 121.6),
    ("Consideration2", "expr", "Consideration", "pen", "star", 126.6, 128.0, 136.8, 138.8),
    ("blessing", "frag", "God bless you!", "seeds", "fade", 155.8, 158.0, 164.4, 166.2),
]
STAR = {"Encouragement": 6, "Consideration": 7, "Respect": 5}     # index in the arch (0 = Greeting)
CENTRE_Y = 0.38            # the block's centre, share of the frame height from the top (PHASEB 16: about 1/3)
FRAG_CENTRE_Y = 0.375


def font(family, weight, size, italic=False):
    style = "italic" if italic else "normal"
    name = {"cg": "cormorant-garamond", "jo": "jost", "of": "outfit"}[family]
    return ImageFont.truetype(str(FONTS / f"{name}-latin-{weight}-{style}.ttf"), max(int(round(size)), 4))


def tracked(draw, xy, text, fnt, fill, track, align="center"):
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x, y = xy
    if align == "center":
        x -= total / 2.0
    elif align == "right":
        x -= total
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + track
    return total


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


class Item:
    """One moment of words: its picture (built at a render size on demand) and its times."""

    def __init__(self, name, kind, what, arrive, leave, t_in, t_read0, t_read1, t_out):
        self.name, self.kind, self.arrive, self.leave = name, kind, arrive, leave
        self.t_in, self.t_read0, self.t_read1, self.t_out = t_in, t_read0, t_read1, t_out
        if kind == "expr":
            e = expressions()[what]
            self.label, self.lines, self.color = e["label"], list(e["lines"]), e["color"]
            self.star = STAR[e["label"]]
        else:
            self.label, self.lines, self.color, self.star = "", [what], None, None
        self._built = {}

    # ------------------------------------------------------------------ the picture
    def build(self, s=1.0):
        """(rgba uint8 picture of the block, x0, y0 of its top left on a 1920s x 1080s frame). Navy letters, a
        capsule in the expression's colour with the label in white."""
        if s in self._built:
            return self._built[s]
        W, H = int(round(1920 * s)), int(round(1080 * s))
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx = W / 2.0
        if self.kind == "expr":
            fl = font("jo", 500, 27 * s)
            lab = self.label.upper()
            tw = sum(d.textlength(c, font=fl) for c in lab) + 9 * s * (len(lab) - 1)
            ch, pad = 54 * s, 32 * s
            fp = font("cg", 500, 80 * s, italic=True)
            lh = 88 * s
            block = ch + 18 * s + lh * len(self.lines)
            top = CENTRE_Y * H - block / 2.0
            col = _hex(self.color)
            d.rounded_rectangle((cx - tw / 2 - pad, top, cx + tw / 2 + pad, top + ch), radius=ch / 2,
                                fill=col + (240,), outline=tuple(min(255, int(v * 0.8)) for v in col) + (255,),
                                width=max(1, int(round(1.5 * s))))
            tracked(d, (cx, top + ch / 2 - 17 * s), lab, fl, (255, 255, 255, 255), 9 * s)
            y = top + ch + 18 * s
            for ln in self.lines:
                d.text((cx, y), ln, font=fp, fill=NAVY + (255,), anchor="ma")
                y += lh
        else:
            fp = font("cg", 600, 100 * s, italic=True)
            y = FRAG_CENTRE_Y * H - 52 * s
            d.text((cx, y), self.lines[0], font=fp, fill=NAVY + (255,), anchor="ma")
        a = np.asarray(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        m = int(round(40 * s))
        x0, x1 = max(xs.min() - m, 0), min(xs.max() + m + 1, W)
        y0, y1 = max(ys.min() - m, 0), min(ys.max() + m + 1, H)
        out = (np.ascontiguousarray(a[y0:y1, x0:x1]), int(x0), int(y0))
        self._built[s] = out
        return out

    def box(self, s=1.0):
        """The reading box (x0, y0, x1, y1) in frame pixels, y down: the ink of the block."""
        a, x0, y0 = self.build(s)
        ys, xs = np.nonzero(a[..., 3] > 8)
        return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1)

    def on(self, r):
        return self.t_in <= r <= self.t_out


class Words:
    def __init__(self):
        self.items = [Item(*row) for row in TIMELINE]

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, name):
        return next(i for i in self.items if i.name == name)

    def on(self, r):
        return [i for i in self.items if i.on(r)]

    def boxes(self, r, cam=None, pad=(.02, .035)):
        """Screen boxes (x0, x1, y0, y1; 0..1, y UP) of the words on screen at r, padded: for the Clear wrapper
        that keeps the scene's light out of them."""
        out = []
        for it in self.on(r):
            x0, y0, x1, y1 = it.box(1.0)
            out.append((x0 / 1920 - pad[0], x1 / 1920 + pad[0], 1 - y1 / 1080 - pad[1], 1 - y0 / 1080 + pad[1]))
        return out

    def calm(self, r, ease=1.0):
        k = 0.0
        for it in self.items:
            u = min(max((r - it.t_read0 + ease) / ease, 0.0), 1.0) * min(max((it.t_read1 + ease - r) / ease, 0.0), 1.0)
            k = max(k, u)
        return k

    def clear(self, pointset):
        return Clear(pointset, self)

    def check(self):
        """Only one moment of words at a time (with its arrival and leaving)."""
        its = sorted(self.items, key=lambda i: i.t_in)
        for a, b in zip(its, its[1:]):
            assert a.t_out <= b.t_in, (a.name, b.name)
        return True


class Clear:
    """Wrap a point set so its light dims inside the reading boxes: nothing crosses a word (Revision 3 rule)."""
    wants_camera = True

    def __init__(self, inner, words):
        self.inner, self.words = inner, words

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = self.words.boxes(t, cam)
        if not boxes:
            return got
        out = []
        for source in got if isinstance(got, (list, tuple)) else [got]:
            if source is None:
                continue
            b = dict(source)
            p = np.asarray(b["pos"]).reshape(-1, 3)
            xy, z = cam.project(p)
            end = None
            if b.get("pos2") is not None:
                end, _ = cam.project(np.asarray(b["pos2"]).reshape(-1, 3))
            gain = np.ones(len(p))
            for u in (np.linspace(0, 1, 9) if end is not None else [0]):
                q = xy if end is None else xy * (1 - u) + end * u
                for x0, x1, y0, y1 in boxes:
                    dx = np.minimum(q[:, 0] - x0, x1 - q[:, 0])
                    dy = np.minimum(q[:, 1] - y0, y1 - q[:, 1])
                    f = np.clip(np.minimum(dx, dy) / .02 + .5, 0, 1)
                    gain = np.minimum(gain, 1 - .98 * f * (z > 0))
            b["alpha"] = np.asarray(b.get("alpha", 1)) * gain
            if "alpha2" in b:
                b["alpha2"] = np.asarray(b["alpha2"]) * gain
            out.append(b)
        return out
