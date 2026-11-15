"""Particle words: the nine Words of Mother's Love as light in the 3D world (engine/p3d).

A Word is a point set (engine/p3d/api.py): a label and one or two lines of text turned into tens of thousands
of points on a plane (or a gentle curve) that stands anywhere in space. The text is drawn with the engine's own
fonts (the files and the tracked label of engine/text.py), then laid out as an even lattice of points with
antialiased edges, so that the settled word is crisp enough to read on a phone.

Every word has four times (seconds of song time):

    t_in      the first particle appears              t_read0   the word is whole: the reading moment starts
    t_read1   the reading moment ends                 t_out     the last particle is gone

Between t_in and t_read0 the word ARRIVES, between t_read1 and t_out it LEAVES. Nine ways each (ARRIVALS,
LEAVINGS below), plus "morph": the particles of one word become the next. Words may overlap in time: one can
arrive while another is read, two can be read at once at different depths. `check()` tells whether every
expression gets its reading time and whether two reading moments ever cover each other on screen.

Everything is a pure function of t (and of the camera at t). Nothing here needs a graphics context.
How a song file uses it: engine/UPGRADE-HOWTO.md, section X.
"""
import os
import zlib

import numpy as np

from .api import MASK_SKIES, CameraState, Mask, lin

TAU = 2.0 * np.pi

# The nine expressions: exact campaign wording (project-docs/DESIGN-SYSTEM.md section 5), line breaks and
# typographic quotes as in the PHRASES of engine/songs/epic_concert.py, colours from DESIGN-SYSTEM section 5.
EXPRESSIONS = [
    dict(label="Greeting", lines=["“How are you?”"], color="#FF977C"),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"],
         color="#FFD05F"),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], color="#FFAD69"),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], color="#F582AF"),
    dict(label="Concession", lines=["“Please, after you.”"], color="#82B0ED"),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], color="#CE927E"),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"],
         color="#B293E7"),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], color="#EF7A96"),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], color="#BE9CEB"),
]
LABELS = [e["label"] for e in EXPRESSIONS]

# the way each expression arrives and leaves when a song does not choose (matched to what it means)
DEFAULT_STYLE = {
    "Greeting": ("touch", "flock"),          # two hands meet: the flare writes the words; they leave as birds
    "Gratitude": ("petals", "arch"),         # flowers given in thanks; the thanks rise to a light of the arch
    "Apology": ("lake", "sink"),             # out of the still water of reflection; back into it
    "Inclusiveness": ("gather", "give"),     # many small lights come together; they become a person
    "Concession": ("flock", "wind"),         # birds give way to each other; the wind takes the words
    "Respect": ("stars", "stars"),           # thoughts joined point by point; they return to the sky
    "Encouragement": ("shaft", "rise"),      # light answers from above; the prayer goes up
    "Consideration": ("palm", "petals"),     # given from an open hand; it leaves as petals
    "Compliment": ("rays", "bokeh"),         # rays burn the words out of mist; they rush past us as light
}
ARRIVALS = ("palm", "petals", "flock", "stars", "touch", "shaft", "lake", "gather", "rays", "morph",
            "pen", "reveal", "stitch", "weave")
LEAVINGS = ("wind", "rise", "arch", "flock", "petals", "sink", "bokeh", "give", "stars", "morph", "fade",
            "stream", "doors", "unravel")

WARM = "#fff4dc"
NINE = [e["color"] for e in EXPRESSIONS]

# reading on a phone: the frame imagined 6 cm wide, so 1 mm is 32 px of a 1080p picture
PHONE_PX_PER_MM = 1920.0 / 60.0
X_HEIGHT = 0.40        # x-height of the phrase face, in em
CAP_HEIGHT = 0.70      # capital height of the label face, in em


# ---------------------------------------------------------------------------------------------- the letters
def _text_tools():
    """Font files and the tracked label of the engine's rasteriser (engine/text.py). Falls back to the same
    font files by path when text.py cannot be loaded (outside a render)."""
    try:
        import text as T
        return T.F_PHRASE, T.F_LABEL, T._tracked
    except Exception:
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        fonts = os.path.join(root, "fonts")

        def tracked(draw, xy_center, text, font, tracking, fill):
            widths = [font.getlength(c) for c in text]
            total = sum(widths) + tracking * (len(text) - 1)
            x = xy_center[0] - total / 2.0
            for c, w in zip(text, widths):
                draw.text((x, xy_center[1]), c, font=font, fill=fill, anchor="ls")
                x += w + tracking
            return total

        return (os.path.join(fonts, "cormorant-garamond-latin-700-italic.ttf"),
                os.path.join(fonts, "jost-latin-500-normal.ttf"), tracked)


def _font_file(font):
    """font= of a Word: None or "phrase" (the expressions' italic), "title" (the end card's upright bold),
    "tag" (the lighter italic), or a path to a font file."""
    if font in (None, "phrase"):
        return None
    if font in ("title", "tag"):
        try:
            import text as T
            return T.F_TITLE if font == "title" else T.F_TAG
        except Exception:
            base = os.path.dirname(_text_tools()[0])
            return os.path.join(base, "cormorant-garamond-latin-700-normal.ttf" if font == "title"
                                else "cormorant-garamond-latin-600-italic.ttf")
    return font


def _lattice(cov, rng, b=3, min_cov=0.10, jitter=0.22):
    """An even lattice of points over a coverage picture (0..1, top row first): one point per cell of b x b
    pixels that holds ink, placed at the centre of the ink inside the cell (so edges stay crisp), its weight
    the share of the cell that is inked (so edges are antialiased). Returns x, y (pixels) and weight."""
    h, w = cov.shape
    h2, w2 = h - h % b, w - w % b
    blk = cov[:h2, :w2].reshape(h2 // b, b, w2 // b, b)
    m = blk.mean(axis=(1, 3))
    off = np.arange(b, dtype=np.float32) + 0.5
    tot = np.maximum(blk.sum(axis=(1, 3)), 1e-6)
    cx = (blk.sum(axis=1) * off[None, None, :]).sum(axis=2) / tot
    cy = (blk.sum(axis=3) * off[None, :, None]).sum(axis=1) / tot
    iy, ix = np.nonzero(m > min_cov)
    k = iy.size
    x = ix * b + cx[iy, ix] + (rng.random(k) - 0.5) * b * jitter
    y = iy * b + cy[iy, ix] + (rng.random(k) - 0.5) * b * jitter
    return x.astype(np.float32), y.astype(np.float32), np.clip(m[iy, ix] * 1.12, 0.0, 1.0).astype(np.float32)


_GLYPHS = {}


def glyphs(label, lines, n=42000, n_label=6000, label_size=0.36, font=None):
    """The points of a text, in em of the phrase face: x to the right and y up from the centre of the phrase
    block. Returns a dict: x, y, w (weight 0..1), lab (True for label points), line (line number),
    cell (lattice spacing of each point, em), and the extents x0, x1, y0, y1, width (widest phrase line),
    block (height of the phrase block), label_cap (capital height of the label, em)."""
    key = (label, tuple(lines), int(n), int(n_label), float(label_size), font)
    if key in _GLYPHS:
        return _GLYPHS[key]
    from PIL import Image, ImageDraw, ImageFont
    f_phrase, f_label, tracked = _text_tools()
    lines = [str(l) for l in lines]
    rng = np.random.default_rng(zlib.crc32((label + "|" + "|".join(lines)).encode("utf-8")))

    def phrase(px):
        f = ImageFont.truetype(_font_file(font) or f_phrase, int(px))
        asc, _ = f.getmetrics()
        line_h = int(px * 1.08)                       # the line spacing of engine/text.py
        wl = [f.getlength(l) for l in lines]
        wc, hc = int(max(wl) + 2 * px), int(line_h * len(lines) + 1.6 * px)
        top = int(0.6 * px)
        im = Image.new("L", (wc, hc), 0)
        d = ImageDraw.Draw(im)
        for i, l in enumerate(lines):
            d.text((wc / 2.0, top + i * line_h + asc * 0.80), l, font=f, fill=255, anchor="ms")
        pre = [[f.getlength(l[:k]) for k in range(len(l) + 1)] for l in lines]   # where each letter starts
        return np.asarray(im, np.float32) / 255.0, dict(px=int(px), cx=wc / 2.0, top=top, line_h=line_h,
                                                        cy=top + line_h * len(lines) / 2.0, w=max(wl), pre=pre)

    b = 3
    cov, m = phrase(240)
    px = int(np.clip(240.0 * np.sqrt(n * b * b / max(float(cov.sum()), 1.0)), 90, 1100))
    cov, m = phrase(px)
    x, y, w = _lattice(cov, rng, b)
    ex = (x - m["cx"]) / px
    ey = (m["cy"] - y) / px
    line = np.clip(((y - m["top"]) / m["line_h"]).astype(np.int32), 0, len(lines) - 1)
    lab = np.zeros(x.size, bool)
    cell = np.full(x.size, b / px, np.float32)
    block = m["line_h"] * len(lines) / px
    out_x, out_y, out_w, out_lab, out_line, out_cell = [ex], [ey], [w], [lab], [line], [cell]
    # which glyph and which word each point belongs to, and how far along the writing it is
    chars, g_line, g_word = [], [], []
    glyph = np.zeros(x.size, np.int32)
    frac = np.zeros(x.size, np.float32)
    n_words = 0
    for li, l in enumerate(lines):
        pre = np.asarray(m["pre"][li], np.float64)
        ids = np.full(len(l), -1, np.int64)
        prev_space = True
        for k, c in enumerate(l):
            if c.isspace():
                prev_space = True
                continue
            if prev_space:
                n_words += 1
                prev_space = False
            ids[k] = len(chars)
            chars.append(c)
            g_line.append(li)
            g_word.append(n_words - 1)
        sel = np.nonzero(line == li)[0]
        xr = x[sel] - (m["cx"] - pre[-1] / 2.0)
        k = np.clip(np.searchsorted(pre, xr, side="right") - 1, 0, len(l) - 1)
        for _ in range(3):                             # ink that overhangs a space belongs to the nearer letter
            sp = ids[k] < 0
            if not sp.any():
                break
            nearer_left = (xr - pre[k]) < (pre[k + 1] - xr)
            k = np.where(sp, np.clip(np.where(nearer_left, k - 1, k + 1), 0, len(l) - 1), k)
        k = np.where(ids[k] < 0, np.clip(k - 1, 0, len(l) - 1), k)
        glyph[sel] = np.maximum(ids[k], 0)
        frac[sel] = np.clip((xr - pre[k]) / np.maximum(pre[k + 1] - pre[k], 1e-6), 0.0, 1.0)
    n_glyphs = len(chars)
    order = ((glyph + frac) / max(n_glyphs, 1)).astype(np.float32)
    out_glyph, out_order = [glyph], [order]
    label_cap = 0.0
    if label:
        def lab_img(lpx):
            lf = ImageFont.truetype(f_label, int(lpx))
            text = label.upper()
            track = 0.47 * lpx                         # the letter spacing of engine/text.py (15 at size 32)
            tw = sum(lf.getlength(c) for c in text) + track * (len(text) - 1)
            wc, hc = int(tw + 2 * lpx), int(2.2 * lpx)
            im = Image.new("L", (wc, hc), 0)
            base = int(1.5 * lpx)
            tracked(ImageDraw.Draw(im), (wc / 2.0, base), text, lf, track, 255)
            adv = [lf.getlength(c) for c in text]
            edges = [wc / 2.0 - tw / 2.0 - track / 2.0]
            for a_ in adv:
                edges.append(edges[-1] + a_ + track)
            return np.asarray(im, np.float32) / 255.0, dict(px=int(lpx), cx=wc / 2.0, base=base, edges=edges,
                                                            text=text)

        lc, lm = lab_img(200)
        lpx = int(np.clip(200.0 * np.sqrt(n_label * b * b / max(float(lc.sum()), 1.0)), 60, 900))
        lc, lm = lab_img(lpx)
        lx, ly, lw = _lattice(lc, rng, b)
        s = float(label_size) / lpx                    # label pixels to em of the phrase
        base_y = block / 2.0 + 0.30                    # the label's baseline sits above the phrase block
        out_x.append((lx - lm["cx"]) * s)
        out_y.append(base_y + (lm["base"] - ly) * s)
        out_w.append(lw)
        out_lab.append(np.ones(lx.size, bool))
        out_line.append(np.zeros(lx.size, np.int32))
        out_cell.append(np.full(lx.size, b * s, np.float32))
        label_cap = CAP_HEIGHT * float(label_size)
        edges = np.asarray(lm["edges"], np.float64)
        text = lm["text"]
        k = np.clip(np.searchsorted(edges, lx, side="right") - 1, 0, len(text) - 1)
        ids = np.full(len(text), -1, np.int64)
        prev_space = True
        for kk, c in enumerate(text):
            if c.isspace():
                prev_space = True
                continue
            if prev_space:
                n_words += 1
                prev_space = False
            ids[kk] = len(chars)
            chars.append(c)
            g_line.append(-1)
            g_word.append(n_words - 1)
        k = np.where(ids[k] < 0, np.clip(k - 1, 0, len(text) - 1), k)
        lg = np.maximum(ids[k], n_glyphs)
        lf_ = np.clip((lx - edges[k]) / np.maximum(edges[k + 1] - edges[k], 1e-6), 0.0, 1.0)
        out_glyph.append(lg.astype(np.int32))
        out_order.append(((lg - n_glyphs + lf_) / max(len(chars) - n_glyphs, 1)).astype(np.float32))
    x = np.concatenate(out_x).astype(np.float32)
    y = np.concatenate(out_y).astype(np.float32)
    perm = rng.permutation(x.size)                     # any leading part of the points is spread evenly
    g = dict(x=x[perm], y=y[perm], w=np.concatenate(out_w)[perm], lab=np.concatenate(out_lab)[perm],
             line=np.concatenate(out_line)[perm], cell=np.concatenate(out_cell)[perm],
             glyph=np.concatenate(out_glyph)[perm], order=np.concatenate(out_order)[perm],
             chars=chars, glyph_line=np.asarray(g_line, np.int32), glyph_word=np.asarray(g_word, np.int32),
             n_glyphs=n_glyphs, n_words=n_words,
             x0=float(x.min()), x1=float(x.max()), y0=float(y.min()), y1=float(y.max()),
             width=float(m["w"] / px), block=float(block), label_cap=label_cap, lines=len(lines))
    _GLYPHS[key] = g
    return g


def estimate_extent(label, lines, label_size=0.36):
    """Rough extents in em when the fonts are not at hand (timing checks before a render): (x0, x1, y0, y1)."""
    w = 0.40 * max(len(l) for l in lines)
    block = 1.08 * len(lines)
    return -w / 2.0, w / 2.0, -block / 2.0, block / 2.0 + (0.30 + CAP_HEIGHT * label_size if label else 0.0)


# ------------------------------------------------------------------------------------------------- helpers
def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float32) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _unit(v):
    v = np.asarray(v, np.float64)
    return v / max(float(np.linalg.norm(v)), 1e-9)


def _num(v, t):
    """A setting that may be a number or a function of t."""
    return float(v(t)) if callable(v) else float(v)


def _col(c):
    if c is None:
        return None
    if isinstance(c, str):
        return lin(c).astype(np.float32)
    return np.asarray(c, np.float32)


def _swirl(p, t, k, ph=0.0):
    """A soft turbulence without sources or sinks (each component ignores its own axis), metres in, about -1.5
    to 1.5 out. Pure function of place and time."""
    x, y, z = p[:, 0] * k, p[:, 1] * k, p[:, 2] * k
    out = np.empty_like(p)
    out[:, 0] = np.sin(y * 1.7 + t * 0.9 + ph) + 0.5 * np.sin(z * 2.3 - t * 0.7 + 1.3 * ph)
    out[:, 1] = np.sin(z * 1.9 + t * 0.8 + 2.1 * ph) + 0.5 * np.sin(x * 2.1 + t * 0.6 + 0.7 * ph)
    out[:, 2] = np.sin(x * 1.5 - t * 0.75 + 3.3 * ph) + 0.5 * np.sin(y * 2.7 + t * 0.5 + 1.9 * ph)
    return out


def _h(n, salt):
    """n fixed numbers in 0..1 (the same on every machine and run)."""
    return np.random.default_rng(1000 + int(salt)).random(n).astype(np.float32)


def _bez(p0, p1, p2, p3, e):
    e = e[:, None]
    k = 1.0 - e
    return k * k * k * p0 + 3.0 * k * k * e * p1 + 3.0 * k * e * e * p2 + e * e * e * p3


def _mix(a, b, u):
    return a + (b - a) * u


def points_of(obj, t, cam=None):
    """World positions (M, 3) of a source or a goal: a Word (its letters), a point set (its first batch),
    a function of t, an array of points, or one point."""
    if obj is None:
        return None
    if isinstance(obj, Word):
        return obj.targets(t, cam)
    if hasattr(obj, "sample"):
        res = obj.sample(t, cam) if getattr(obj, "wants_camera", False) else obj.sample(t)
        res = res if isinstance(res, (list, tuple)) else [res]
        for b in res:
            if b is not None and len(b["pos"]):
                return np.asarray(b["pos"], np.float32).reshape(-1, 3)
        return None
    if callable(obj):
        obj = obj(t)
    return np.asarray(obj, np.float32).reshape(-1, 3)


# -------------------------------------------------------------------------------------------------- a word
class Word:
    """One text as particles in space. See the module text and engine/UPGRADE-HOWTO.md section X.

    expr          one of the nine labels ("Greeting" ...) or 1..9: fills label, lines and colour
    label, lines  any other text (lines: one or two strings)
    pos           the centre of the phrase block, metres (or a function of t)
    width         metres across the widest line of the phrase (or em= metres per em of the phrase face)
    facing        azimuth the words face, degrees (0 faces +z, as in api.at)
    face          "fixed" (use facing), "camera" (turn about the vertical to face the camera) or "screen"
                  (always flat to the picture)
    tilt          degrees the plane leans back;  curve: radius in metres of a gentle curve (0: flat; positive
                  bends the ends toward the reader)
    t_in, t_read0, t_read1, t_out   the four times
    arrive, leave  names from ARRIVALS and LEAVINGS (default: the pair of DEFAULT_STYLE for the expression)
    source        where the arrival comes from: a point, a function of t, a point set, another Word (morph)
    to            where the leaving goes: a point (an arch light), a point set (a person), another Word
    color, glow   letter light and halo (display hex); tint: how much of the colour the letters keep
    bright, halo, sparkle   amounts (1 is the default look)
    sharp         0..1: how far the settled letters ignore the lens blur (1: always sharp while they are read)
    n, n_label    how many points for the phrase and for the label
    """
    wants_camera = True

    def __init__(self, label="", lines=(), expr=None, pos=(0.0, 3.0, 0.0), width=8.0, em=None, facing=0.0,
                 face=None, tilt=0.0, curve=0.0, t_in=0.0, t_read0=2.5, t_read1=5.5, t_out=8.0, arrive=None,
                 leave=None, source=None, to=None, color=None, glow=None, tint=0.45, bright=1.0, halo=1.0,
                 sparkle=1.0, sharp=1.0, fog=0.0, n=42000, n_label=6000, label_size=0.36, dot=1.9, name=None,
                 wind=None, font=None, roll=0.0, ride=None, bind=None, camera=None, drive=None, reflect=None,
                 **opts):
        if expr is not None:
            e = EXPRESSIONS[expr - 1] if isinstance(expr, int) else EXPRESSIONS[LABELS.index(expr)]
            label, lines = e["label"], e["lines"]
            color = color or e["color"]
        if not lines:
            raise ValueError("a Word needs lines (or expr)")
        self.label, self.lines = label, list(lines)
        self.name = name or label or self.lines[0]
        style = DEFAULT_STYLE.get(label, ("palm", "wind"))
        self.arrive, self.leave = arrive or style[0], leave or style[1]
        if self.arrive not in ARRIVALS:
            raise ValueError(f"word {self.name!r}: arrive must be one of {ARRIVALS}, got {self.arrive!r}")
        if self.leave not in LEAVINGS:
            raise ValueError(f"word {self.name!r}: leave must be one of {LEAVINGS}, got {self.leave!r}")
        self.pos, self.width, self.em = pos, float(width), em
        face = face or ("screen" if ride is not None else "fixed")   # a word that rides with the camera lies flat to the picture
        self.facing, self.face, self.tilt, self.curve, self.roll = facing, face, tilt, float(curve), roll
        if face not in ("fixed", "camera", "screen", "flat"):
            raise ValueError(f"word {self.name!r}: face must be fixed, camera, screen or flat")
        self.ride, self.bind, self.camera, self.drive = ride, bind, camera, drive
        # letters as a mask (CORE's mask pass): a window onto a sky, dark ink, or paint in the word's colour
        self.window, self.ink, self.paint = opts.pop("window", None), bool(opts.pop("ink", False)), opts.pop("paint", None)
        if self.window is not None and self.window not in MASK_SKIES:
            raise ValueError(f"word {self.name!r}: window must be one of {MASK_SKIES}, got {self.window!r}")
        self.masked = bool(self.window or self.ink or self.paint)
        self._kept = None
        self.avoid = bool(opts.pop("avoid", True))                 # flying particles keep clear of words being read
        self.avoid_floor = float(opts.pop("avoid_floor", 0.12))
        self.reflect = (face != "flat") if reflect is None else bool(reflect)   # a word lying on the water has no mirror image
        self._others = []
        self.t_in, self.t_read0, self.t_read1, self.t_out = (float(t_in), float(t_read0), float(t_read1),
                                                             float(t_out))
        self.source, self.to = source, to
        self.hex = color or "#ffd27a"
        self.tint, self.bright, self.halo, self.sparkle = float(tint), float(bright), float(halo), float(sparkle)
        self.glow_hex = glow or self.hex
        self.sharp = float(np.clip(sharp, 0.0, 1.0))
        self.fog = float(np.clip(fog, 0.0, 1.0))
        self.n, self.n_label, self.label_size, self.dot = int(n), int(n_label), float(label_size), float(dot)
        self.wind = _unit(wind if wind is not None else (1.0, 0.22, 0.10))
        self.font, self.opts = font, opts
        self._g = None

    # ------------------------------------------------------------------ geometry
    def metres_per_em(self):
        if self.em:
            return float(self.em)
        try:
            return self.width / self._glyphs()["width"]
        except Exception:
            x0, x1, _, _ = estimate_extent(self.label, self.lines, self.label_size)
            return self.width / (x1 - x0)

    def _glyphs(self):
        return glyphs(self.label, self.lines, self.n, self.n_label, self.label_size, self.font)

    def extent(self):
        """(x0, x1, y0, y1) of the whole text (label included) in metres on its plane, from its centre."""
        try:
            g = self._glyphs()
            e = (g["x0"], g["x1"], g["y0"], g["y1"])
        except Exception:
            e = estimate_extent(self.label, self.lines, self.label_size)
        k = self.metres_per_em()
        return tuple(v * k for v in e)

    def _cam(self, t, cam=None):
        """The camera at t: the one given, else the word's own (`camera=`, or the one its Words set knows)."""
        if cam is not None:
            return cam
        return _cam_at(self.camera, t) if self.camera is not None else None

    def centre(self, t, cam=None):
        """The centre of the phrase block in the world at t."""
        if self.ride is not None:
            c = self._cam(t, cam)
            if c is None:
                raise ValueError(f"word {self.name!r}: ride needs a camera (give camera= to the word or to Words)")
            rd = self.ride(t) if callable(self.ride) else self.ride
            return place(c, t, float(rd[0]), float(rd[1]), float(rd[2]))
        if self.bind is not None:
            return np.asarray(self.bind(np.zeros(1), np.zeros(1), t), np.float64).reshape(-1, 3)[0]
        p = self.pos(t) if callable(self.pos) else self.pos
        return np.asarray(p, np.float64)

    def frame(self, t, cam=None):
        """(centre, right, up, normal) of the plane at t: unit vectors in the world. The words read from left
        to right for someone the normal points at."""
        cam = self._cam(t, cam)
        o = self.centre(t, cam)
        if self.bind is not None:
            # a word bound to a moving surface: the frame is the surface's own at the word's centre
            e = 0.5 * self.metres_per_em()
            q = np.asarray(self.bind(np.array([0.0, e, 0.0]), np.array([0.0, 0.0, e]), t), np.float64).reshape(3, 3)
            r, u = _unit(q[1] - q[0]), _unit(q[2] - q[0])
            n = _unit(np.cross(r, u))
            return q[0], r, _unit(np.cross(n, r)), n
        if self.face == "screen" and cam is not None:
            r, u, f = cam.basis()
            n = -f
        else:
            if self.face == "camera" and cam is not None:
                d = np.asarray(cam.pos, np.float64) - o
                a = np.arctan2(d[0], d[2])
            else:
                a = np.radians(_num(self.facing, t))
            n = np.array([np.sin(a), 0.0, np.cos(a)])
            r = np.array([np.cos(a), 0.0, -np.sin(a)])
            u = np.array([0.0, 1.0, 0.0])
            if self.face == "flat":                    # lying on the water, read from above
                u, n = -n, np.array([0.0, 1.0, 0.0])
        tilt, roll = _num(self.tilt, t), _num(self.roll, t)
        if tilt:
            k = np.radians(tilt)
            u, n = u * np.cos(k) - n * np.sin(k), n * np.cos(k) + u * np.sin(k)
        if roll:
            k = np.radians(roll)
            r, u = r * np.cos(k) + u * np.sin(k), u * np.cos(k) - r * np.sin(k)
        return o, r, u, n

    def _build(self):
        if self._g is not None:
            return
        g = self._glyphs()
        k = self.metres_per_em()
        n = g["x"].size
        self.N = n
        self.xl = (g["x"] * k).astype(np.float32)
        self.yl = (g["y"] * k).astype(np.float32)
        self.zl = np.zeros(n, np.float32)
        if self.curve:
            rad = float(self.curve)
            self.zl = (rad * (1.0 - np.cos(self.xl / rad))).astype(np.float32)
            self.xl = (rad * np.sin(self.xl / rad)).astype(np.float32)
        self.wt = g["w"]
        self.lab = g["lab"]
        self.cell = (g["cell"] * k).astype(np.float32)             # lattice spacing in metres
        self.size0 = (self.cell * self.dot).astype(np.float32)     # sprite diameter in metres
        self.W = float((g["x1"] - g["x0"]) * k)
        self.Ht = float((g["y1"] - g["y0"]) * k)
        self.ymid = float((g["y1"] + g["y0"]) * 0.5 * k)
        self.ytop, self.ybot = float(g["y1"] * k), float(g["y0"] * k)
        rng = np.random.default_rng(zlib.crc32(self.name.encode("utf-8")) + 17)
        self.s = rng.random((n, 4)).astype(np.float32)
        xn = (self.xl - self.xl.min()) / max(float(np.ptp(self.xl)), 1e-6)
        self.xn = xn.astype(np.float32)
        self.yn = ((self.yl - self.ybot) / max(self.Ht, 1e-6)).astype(np.float32)
        nl = g["lines"]
        self.ord = np.where(self.lab, 0.5 * xn / nl, (g["line"] + xn) / nl).astype(np.float32)   # reading order
        self.glyph, self.gline, self.gword, self.chars = g["glyph"], g["glyph_line"], g["glyph_word"], g["chars"]
        self.order = g["order"]                                    # 0..1 along the phrase (the label: along itself)
        # one writing order for everything: the label is written first, then the phrase
        share = 0.14 if self.lab.any() else 0.0
        self.worder = np.where(self.lab, share * self.order, share + (1.0 - share) * self.order).astype(np.float32)
        self.rho = np.hypot(self.xl, self.yl - self.ymid).astype(np.float32)
        self.rho_max = float(self.rho.max())
        self.phi = np.arctan2(self.yl - self.ymid, self.xl).astype(np.float32)
        # carriers: an even share of the points that fly as petals, birds, flakes, walkers, stars; each of the
        # other points belongs to its nearest carrier and shows when that carrier lands
        from scipy.spatial import cKDTree
        m = int(np.clip(n // 40, 300, 1400))
        self.M = m
        loc = np.stack([self.xl, self.yl], axis=1)
        tree = cKDTree(loc[:m])
        d, self.ci = tree.query(loc)
        self.cd = np.clip(d / max(float(np.percentile(d, 96)), 1e-6), 0.0, 1.0).astype(np.float32)
        dn, nb = tree.query(loc[:m], k=4)
        lim = 2.4 * float(np.median(dn[:, 1]))
        pairs = set()
        for j in range(m):
            for q in (1, 2, 3):
                if dn[j, q] < lim:
                    pairs.add((min(j, int(nb[j, q])), max(j, int(nb[j, q]))))
        self.edges = np.array(sorted(pairs), np.int32).reshape(-1, 2)
        # rays: a fixed fan of directions; letters along a ray burn first
        fan = TAU * (np.arange(11) + rng.random(11) * 0.6) / 11.0
        self.fan = fan.astype(np.float32)
        dphi = self.phi[:, None] - fan[None, :]
        self.ray = (np.maximum(np.cos(dphi), 0.0) ** 26).max(axis=1).astype(np.float32)
        # the pen's path: where the writing is at each share of its order (a smooth line through the ink)
        kq = 320
        b_ = np.minimum((self.worder * kq).astype(np.int64), kq - 1)
        cnt = np.bincount(b_, minlength=kq).astype(np.float64)
        px_ = np.bincount(b_, weights=self.xl, minlength=kq) / np.maximum(cnt, 1.0)
        py_ = np.bincount(b_, weights=self.yl, minlength=kq) / np.maximum(cnt, 1.0)
        have = cnt > 0
        qs = (np.arange(kq) + 0.5) / kq
        px_, py_ = np.interp(qs, qs[have], px_[have]), np.interp(qs, qs[have], py_[have])
        ker = np.array([0.25, 0.5, 0.25])
        self.pen_q = qs
        self.pen_x = np.convolve(np.pad(px_, 1, mode="edge"), ker, mode="valid")
        self.pen_y = np.convolve(np.pad(py_, 1, mode="edge"), ker, mode="valid")
        self._pen_cache = None
        white = lin(WARM).astype(np.float32)
        base = _col(self.hex)
        if self.paint:
            base = _col(self.paint) if isinstance(self.paint, str) else base
            self.c_letter = (base * self.bright).astype(np.float32)       # paint: the colour itself, no white in it
        else:
            self.c_letter = (_mix(white, base, self.tint) * self.bright).astype(np.float32)
        self.c_glow = (_col(self.glow_hex) * self.bright).astype(np.float32)
        self.c_base = base
        self.i_spark = np.nonzero(self.s[:, 3] < 0.012)[0]
        self.n_halo = min(n, 2600)
        self._g = g

    def targets(self, t, cam=None):
        """World positions (N, 3) of the settled letters at t: every point's home place."""
        self._build()
        if self.bind is not None:
            return np.asarray(self.bind(self.xl, self.yl, t), np.float32).reshape(-1, 3)
        o, r, u, nrm = self.frame(t, cam)
        return (o[None, :] + self.xl[:, None] * r[None, :] + self.yl[:, None] * u[None, :]
                + self.zl[:, None] * nrm[None, :]).astype(np.float32)

    def home(self):
        """Every point's fixed place in the word, for directors who drive reveals and morphs themselves.

        A dict of arrays, one entry per point (label included), in a fixed order that never changes:
          x, y, z   metres on the word's plane from the centre of the phrase block (x right, y up, z out)
          line      the line of the phrase (0, 1); -1 for the label
          word      which word of the text (0.. in reading order; the label's words come after the phrase's)
          glyph     which letter (0.. in reading order; the label's letters come after the phrase's)
          order     0..1 along the writing of the phrase (for label points: along the label)
          write     0..1 along the writing of everything (the label first, then the phrase)
          label     True for the label's points
          weight    0..1 (edge points weigh less: the antialiasing), size: the sprite's diameter in metres
        and: chars (the letter of each glyph), glyph_line, glyph_word (per glyph), n, n_glyphs, n_words.
        `targets(t, cam)` gives the same points in the world at t; `frame(t, cam)` the plane itself."""
        self._build()
        g = self._g
        return dict(x=self.xl, y=self.yl, z=self.zl, line=np.where(self.lab, -1, g["line"]).astype(np.int32),
                    word=self.gword[self.glyph], glyph=self.glyph, order=self.order, write=self.worder,
                    label=self.lab, weight=self.wt, size=self.size0, chars=list(self.chars),
                    glyph_line=self.gline, glyph_word=self.gword, n=self.N, n_glyphs=int(g["n_glyphs"]),
                    n_words=int(g["n_words"]))

    def corners(self, t, cam=None, pad=0.0):
        """The four corners of the text (label included) in the world: for screen checks."""
        x0, x1, y0, y1 = self.extent()
        cs = ((x0, -1, y0, -1), (x1, 1, y0, -1), (x1, 1, y1, 1), (x0, -1, y1, 1))
        if self.bind is not None:
            return np.asarray(self.bind(np.array([c[0] + c[1] * pad for c in cs]),
                                        np.array([c[2] + c[3] * pad for c in cs]), t), np.float64).reshape(4, 3)
        o, r, u, _ = self.frame(t, cam)
        return np.array([o + (x + sx * pad) * r + (y + sy * pad) * u for x, sx, y, sy in cs])

    def state(self, t):
        """'out', 'arrive', 'read' or 'leave' at t."""
        if t < self.t_in or t > self.t_out:
            return "out"
        if t < self.t_read0:
            return "arrive"
        if t <= self.t_read1 or (self.leave == "morph" and isinstance(self.to, Word) and t < self.to.t_in):
            return "read"
        return "leave"

    def gain(self, t):
        return 1.0

    def _read_end(self):
        """When the reading moment really ends: a word that hands its particles on is held until then."""
        if self.leave == "morph" and isinstance(self.to, Word):
            return max(self.to.t_in, self.t_read1)
        return self.t_read1

    def _env(self, t, hold_level, rise=0.2):
        """How strongly the light of an arrival (shaft, rays) shines at t: up during the arrival, fainter
        while the words are read, gone as they leave (or just before the particles are handed on)."""
        a = (t - self.t_in) / max(self.t_read0 - self.t_in, 1e-6)
        end = self._read_end()
        if a <= 0.0 or t >= max(self.t_out, end):
            return 0.0
        k = float(_ss(0.0, rise, a))
        if t > self.t_read0:
            k *= 1.0 - (1.0 - hold_level) * float(_ss(0.0, 1.5, t - self.t_read0))
        if self.leave == "morph":
            k *= 1.0 - float(_ss(end - 0.9, end - 0.1, t))
        elif t > self.t_read1:
            k *= 1.0 - float(_ss(0.0, 0.6, (t - self.t_read1) / max(self.t_out - self.t_read1, 1e-6)))
        return k

    def shaft(self, color="#cfe0ff", strength=1.0):
        """A shaft of light for P3D world["shafts"]: it stands where the word is, from above it down to the
        lake, bright while the word arrives and fainter while it is read."""
        x0, x1, y0, y1 = self.extent()
        w = x1 - x0

        def base(t):
            c = self.centre(t)
            return (float(c[0]), float(c[2]))

        rad = 0.20 * w
        k = 0.8 / rad            # the column's glow grows with its width: keep it gentle whatever the size
        return dict(base=base, radius=rad, top=float(self.centre(self.t_read0)[1] + y1 + 1.6 * w),
                    spread=-0.6, color=color, strength=lambda t: strength * k * self._env(t, 0.5, rise=0.55))

    def light(self, color=None, strength=1.0, size=None):
        """The world's light (P3D world["light"]) standing behind the word: its rays fan out past the letters
        while the word arrives by `rays`."""
        x0, x1, y0, y1 = self.extent()

        def pos(t):
            if self.source is not None and not isinstance(self.source, Word):
                q = points_of(self.source, t)
                return tuple(float(v) for v in np.asarray(q, np.float64).mean(axis=0))
            c = self.centre(t)
            return (float(c[0]), float(c[1] + 0.5 * (y0 + y1)), float(c[2]))

        return dict(pos=pos, strength=lambda t: strength * self._env(t, 0.35), rays=1.0,
                    size=size or 0.10 * (x1 - x0), color=color or self.glow_hex)

    # ------------------------------------------------------------------ sampling
    def sample(self, t, cam=None):
        st = self.state(t)
        if st == "out":
            return []
        self._build()
        cam = self._cam(t, cam)
        o, r, u, nrm = self.frame(t, cam)
        F = (o, r, u, nrm)
        if self.bind is not None:
            tg = np.asarray(self.bind(self.xl, self.yl, t), np.float32).reshape(-1, 3)
        else:
            tg = (o[None, :] + self.xl[:, None] * r[None, :] + self.yl[:, None] * u[None, :]
                  + self.zl[:, None] * nrm[None, :]).astype(np.float32)
        out = []
        n = self.N
        P = dict(pos=tg, alpha=np.ones(n, np.float32), assist=np.ones(n, np.float32),
                 emit=np.ones(n, np.float32), color=None, size=self.size0, extra=out, split=None)
        if st == "arrive":
            a = (t - self.t_in) / max(self.t_read0 - self.t_in, 1e-6)
            getattr(self, "_arr_" + self.arrive)(P, a, t, cam, F, tg)
            self._ambient(out, self.arrive, a, t, F, True)
        elif st == "read":
            end = self._read_end()
            # a word that hands its particles on lets its own light (shaft, rays) go just before
            gone = float(_ss(end - 0.9, end - 0.1, t)) if self.leave == "morph" else 0.0
            self._ambient(out, self.arrive, 1.0, t, F, True, hold=(t - self.t_read0), fade=gone * 0.5)
            # a slow wave of brightness runs through the held words
            ph = ((t - self.t_read0) / 3.4) % 1.0 * 1.6 - 0.3
            amp = 0.30 * float(_ss(0.0, 0.5, t - self.t_read0) * (1.0 - _ss(end - 0.5, end, t)))
            P["emit"] = 1.0 + amp * np.exp(-((self.xn - ph) / 0.10) ** 2).astype(np.float32)
        else:
            if self.leave == "morph":
                return []          # the next word carries the particles on
            l = (t - self.t_read1) / max(self.t_out - self.t_read1, 1e-6)
            getattr(self, "_lea_" + self.leave)(P, l, t, cam, F, tg)
            self._ambient(out, self.arrive, 1.0, t, F, False, fade=l)
        if self.drive is not None:
            # the director's own hand on the points: pos replaces, alpha and emit multiply, assist replaces
            d = self.drive(t, dict(state=st, pos=P["pos"], home=tg, frame=F, cam=cam, word=self)) or {}
            if d.get("pos") is not None:
                P["pos"] = np.asarray(d["pos"], np.float32)
            if d.get("alpha") is not None:
                P["alpha"] = (P["alpha"] * np.asarray(d["alpha"], np.float32)).astype(np.float32)
            if d.get("emit") is not None:
                P["emit"] = (P["emit"] * np.asarray(d["emit"], np.float32)).astype(np.float32)
            if d.get("assist") is not None:
                P["assist"] = np.broadcast_to(np.asarray(d["assist"], np.float32), (n,)).astype(np.float32)
            if d.get("color") is not None:
                P["color"] = np.asarray(d["color"], np.float32)
        if self.avoid and self._others:
            # what flies keeps clear of every other word that is being read
            flying = P["assist"] < 0.999
            if flying.any():
                k = clear(P["pos"][flying], t, self._others, cam, floor=self.avoid_floor)
                if k is not None:
                    P["alpha"] = P["alpha"].copy()
                    P["alpha"][flying] *= k
            for b in out:
                k = clear(b["pos"], t, self._others, cam, floor=self.avoid_floor)
                if k is None:
                    continue
                b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float32) * k
                if b.get("alpha2") is not None and b.get("pos2") is not None:
                    b["alpha2"] = np.asarray(b["alpha2"], np.float32) * clear(b["pos2"], t, self._others, cam,
                                                                             floor=self.avoid_floor)
        if not self.masked:
            self._emit(out, P, cam, t)
            return out
        letters = []
        self._emit(out, P, cam, t, letters)
        self._kept = (t, out)
        return letters

    def mask(self):
        """The mask a masked word is added to the scene with (Words.add_to does it): its letters become a
        window onto a sky (window=), dark ink (ink=True) or the base for paint (paint=)."""
        if not self.masked:
            return None
        self._build()
        grow = float(self.opts.get("mask_grow", 0.0)) * float(np.median(self.cell))
        soft = float(self.opts.get("mask_soft", 1.0))
        if self.window:
            return Mask("sky", sky=self.window, grow=grow, soft=soft, edge=float(self.opts.get("window_edge", 0.5)),
                        tint=tuple(self.opts.get("window_tint", (1.0, 1.0, 1.0))))
        return Mask("dark", grow=grow, soft=soft)

    @property
    def lights(self):
        """The rest of a masked word (halo, glints, petals, birds, threads) as its own point set, drawn
        without the mask."""
        return _Lights(self)

    def keep_clear(self, t, cam=None, pad=0.8):
        """The box other layers should keep clear of while this word is read: (strength 0..1, the four
        corners of the box in the world, the plane's normal). The strength eases in half a second before the
        reading moment and out after it; pad: how far the box reaches beyond the text, in em."""
        end = self._read_end()
        k = float(_ss(self.t_read0 - 0.5, self.t_read0, t) * (1.0 - _ss(end, end + 0.4, t)))
        if k <= 0.0:
            return 0.0, None, None
        cam = self._cam(t, cam)
        return k, self.corners(t, cam, pad=pad * self.metres_per_em()), self.frame(t, cam)[3]

    def pen(self, t, cam=None):
        """Where the writing is at t, in the world: the nib of arrive="pen" and the needle of "stitch" while
        the word arrives, the thread's free end of leave="unravel" while it leaves. For a comet head or a
        fingertip that should do the writing."""
        self._build()
        cam = self._cam(t, cam)
        F = self.frame(t, cam)
        if t <= self.t_read0:
            a = (t - self.t_in) / max(self.t_read0 - self.t_in, 1e-6)
            q = float(np.clip((a - 0.04) / 0.88, 0.0, 1.0))
        else:
            q = 1.0
        return self._local(F, t, np.array([np.interp(q, self.pen_q, self.pen_x)]),
                           np.array([np.interp(q, self.pen_q, self.pen_y)]))[0].astype(np.float64)

    def _local(self, F, t, x, y, z=None):
        """World places of points given on the word's plane (metres from its centre)."""
        if self.bind is not None:
            pos = np.asarray(self.bind(np.asarray(x, np.float64), np.asarray(y, np.float64), t), np.float32).reshape(-1, 3)
        else:
            o, r, u, nrm = F
            pos = (o[None, :] + np.asarray(x, np.float64)[:, None] * r[None, :]
                   + np.asarray(y, np.float64)[:, None] * u[None, :]).astype(np.float32)
        if z is not None:
            pos = pos + np.asarray(z, np.float32)[:, None] * F[3].astype(np.float32)[None, :]
        return pos

    def _emit(self, out, P, cam, t, letters=None):
        """Turns the state of the letters' points into batches: the letters, their halo, their glints."""
        letters = out if letters is None else letters
        pos, alpha, size, emit, assist = (P["pos"], P["alpha"] * P.get("wt", self.wt), P["size"], P["emit"],
                                          P["assist"])
        color = P["color"]
        glow = P.get("glow", self.c_glow)
        col = self.c_letter if color is None else color
        level = 1.15
        mk = 1.0
        if self.masked:
            if self.paint:
                # paint: the letters' own light fills what the dark base lacks of the colour
                base = np.asarray(self.opts.get("paint_base", (0.10, 0.20, 0.30)), np.float32)
                col = np.maximum(col - base, 0.0) / (1.1 * level) * float(self.opts.get("mask_light", 1.0)) + 1e-4
            else:
                level *= float(self.opts.get("mask_light", 0.0))   # a window or ink word is not its own light
            # The mask pass draws every point as a disc of at least 1.2 pixels of its half size picture and
            # adds the discs up; full weights would fatten the letters by that much. Each point is given a
            # weight at which the sum passes the mask's threshold close to the letter's own edge (thin
            # strokes still pass after the mask's blur), and its light is kept.
            if cam is not None:
                depth = max(float(np.dot(np.asarray(pos[:: max(len(pos) // 64, 1)], np.float64).mean(axis=0)
                                         - np.asarray(cam.pos, np.float64), cam.basis()[2])), 0.05)
                pxm = 0.5 * 1080.0 / np.tan(np.radians(cam.fov) * 0.5) / depth       # 1080p pixels per metre
                cell = float(np.median(self.cell))
                rad = max(0.95 * cell * pxm, 2.4)
                n_disc = max(np.pi * rad * rad / max(cell * pxm, 1e-6) ** 2, 1.0)
                wgt = min(1.04 / n_disc * float(self.opts.get("mask_weight", 2.2 if self.window else 3.4)), 1.0)
                mk = 0.02 + 0.18 * float(np.sqrt(wgt / 3.0)) if wgt < 0.5 else 1.0
            else:
                mk = 0.05
        vis = alpha > 0.004
        split = P["split"]            # optional: points below the water are kept out of the mirror

        def put(sel, dof, reflect=True, a_mul=1.0, s_new=None):
            if not sel.any():
                return
            # settled letters keep clear of the haze and of the motion blur; flying particles take both
            letters.append(dict(pos=pos[sel], size=(size[sel] if s_new is None else s_new),
                            color=(col if col.ndim == 1 else col[sel]) * level,
                            alpha=(alpha[sel] * a_mul * mk), emit=emit[sel] / mk, kind="soft", dof=dof,
                            reflect=reflect,
                            seed=self.s[sel, 0], twinkle=0.12, fog=1.0 if dof else self.fog,
                            streak=1.0 if dof else 0.0))

        lens = cam is not None and getattr(cam, "aperture", 0.0) > 0.0 and self.sharp > 0.0
        groups = [(vis, True)] if split is None else [(vis & ~split, True), (vis & split, False)]
        for sel, refl in groups:
            if not lens:
                held = sel & (assist >= 0.999)
                put(held, False, refl)
                put(sel & ~held, True, refl)
                continue
            held = sel & (assist > 0.0)
            put(sel & ~held, True, refl)
            if held.any():
                # the letters' own lens: the blur the camera would give, eased away as a point settles
                r_, u_, f_ = cam.basis()
                depth = np.maximum((pos[held] - np.asarray(cam.pos, np.float32)) @ f_.astype(np.float32), 0.05)
                coc = 2.0 * cam.coc_radius(depth) * 2.0 * depth * np.tan(np.radians(cam.fov) * 0.5)
                coc = coc * (1.0 - self.sharp * assist[held])
                s0 = size[held]
                s1 = np.sqrt(s0 * s0 + coc * coc).astype(np.float32)
                put(held, False, refl, a_mul=(s0 / s1) ** 2, s_new=s1)
        # halo: a soft coloured light round the letters, carried by an even share of the points
        if self.halo > 0.0 and not self.masked:
            k = self.n_halo
            a = alpha[:k]
            sel = a > 0.01
            if sel.any():
                out.append(dict(pos=pos[:k][sel], size=size[:k][sel] * 9.0, color=glow,
                                alpha=a[sel] * (0.050 * self.halo * self.N / k / 16.0), kind="soft",
                                seed=self.s[:k][sel, 1], fog=self.fog, streak=0.0))
        # glints: a few points sparkle like glitter
        if self.sparkle > 0.0 and not self.ink:
            i = self.i_spark
            a = alpha[i] * np.clip(assist[i] * 1.5, 0.25, 1.0)
            sel = a > 0.02
            if sel.any():
                out.append(dict(pos=pos[i][sel], size=self.size0[i][sel] * 2.6, color=self.c_letter,
                                alpha=a[sel] * 0.8 * self.sparkle, emit=2.4, kind="spark", twinkle=1.0,
                                seed=self.s[i][sel, 2]))

    # ------------------------------------------------------------------ shared pieces
    def _world(self, F, dx, dy, dz):
        o, r, u, nrm = F
        return (np.asarray(dx, np.float32)[:, None] * r[None, :].astype(np.float32)
                + np.asarray(dy, np.float32)[:, None] * u[None, :].astype(np.float32)
                + np.asarray(dz, np.float32)[:, None] * nrm[None, :].astype(np.float32))

    def _point(self, obj, t, cam, default):
        if obj is None or isinstance(obj, Word):
            return np.asarray(default, np.float64)
        p = points_of(obj, t, cam)
        return np.asarray(p, np.float64).mean(axis=0) if p is not None else np.asarray(default, np.float64)

    def _patches(self, P, a, land, spread=0.035, flash=1.6, rise=0.045):
        """Every point shows when its carrier has landed (land: per carrier, in units of the arrival)."""
        rev = land[self.ci] + self.cd * spread
        dt = a - rev
        P["alpha"] = _ss(0.0, rise, dt)
        P["emit"] = 1.0 + flash * np.exp(-np.maximum(dt, 0.0) / 0.05) * (dt > 0.0)
        return rev

    def _screen_rot(self, cam, vel):
        """Heading in the picture plane of world velocities (for birds)."""
        if cam is None:
            return np.arctan2(vel[:, 1], vel[:, 0])
        r, u, _ = cam.basis()
        return np.arctan2(vel @ u.astype(np.float32), vel @ r.astype(np.float32))

    def _ambient(self, out, style, a, t, F, arriving, hold=0.0, fade=0.0):
        """The light that belongs to an arrival and stays while the words are read: the shaft of light, the
        rays and their mist."""
        o, r, u, nrm = F
        w = self.W
        if style == "shaft":
            env = _ss(0.0, 0.18, a) * (1.0 - 0.6 * _ss(0.0, 1.5, hold)) * (1.0 - _ss(0.0, 0.5, fade))
            if env <= 0.003:
                return
            k = 9
            h = _h(k, 31)
            top = o + u * (self.ytop + 1.9 * w) + r * ((h - 0.5) * 0.22 * w)[:, None]
            bot = o + u * (self.ybot - 0.25 * self.Ht) + r * ((h - 0.5) * 1.05 * w)[:, None]
            flick = 0.75 + 0.25 * np.sin(t * (0.6 + h * 0.9) + h * 20.0)
            out.append(dict(pos=top, pos2=bot, size=(0.07 + 0.30 * _h(k, 32)) * w,
                            color=lin("#bcd8ff") * 0.9 + self.c_glow * 0.25, alpha=0.085 * env * flick,
                            alpha2=0.012 * env * flick, kind="ribbon", dof=False, reflect=False))
        elif style == "rays":
            env = (_ss(0.0, 0.25, a) * (1.0 - 0.55 * _ss(0.0, 1.2, hold))) * (1.0 - _ss(0.0, 0.5, fade))
            if env <= 0.003:
                return
            src = self._ray_source(t, None, F)
            ang = self.fan + 0.10 * np.sin(t * 0.35 + self.fan * 3.0)
            reach = (0.45 + 1.25 * float(_ss(0.0, 0.6, a))) * w
            d = (np.cos(ang)[:, None] * r[None, :] + np.sin(ang)[:, None] * u[None, :]) * reach + nrm * (0.42 * w)
            h = _h(len(ang), 33)
            flick = 0.65 + 0.35 * np.sin(t * (0.8 + h) + h * 30.0)
            out.append(dict(pos=np.repeat(src[None, :], len(ang), 0), pos2=src[None, :] + d,
                            size=(0.02 + 0.04 * h) * w, color=_mix(lin(WARM), self.c_glow, 0.45),
                            alpha=0.085 * env * flick, alpha2=0.0, kind="ribbon", dof=False, reflect=False))
            # the light itself, behind the words
            out.append(dict(pos=src[None, :], size=0.55 * w, color=_mix(lin(WARM), self.c_glow, 0.5),
                            alpha=0.10 * env, kind="soft", dof=False))
            # mist that the rays burn away
            m = 700
            hx, hy, hz, hs = _h(m, 41), _h(m, 42), _h(m, 43), _h(m, 44)
            thin = 1.0 - 0.8 * float(_ss(0.25, 1.0, a))
            if arriving and thin > 0.02:
                p = (o[None, :] + ((hx - 0.5) * 1.5 * w + 0.05 * w * np.sin(t * 0.2 + hs * 9.0))[:, None] * r
                     + (self.ymid + (hy - 0.5) * 1.9 * self.Ht)[:, None] * u
                     + ((hz - 0.75) * 0.5 * w)[:, None] * nrm)
                out.append(dict(pos=p, size=(0.06 + 0.12 * hs) * w, color=_mix(lin("#9fb4d8"), self.c_glow, 0.3),
                                alpha=0.030 * thin * float(_ss(0.0, 0.12, a)), kind="soft", lod=False))

    # ------------------------------------------------------------------ nine ways of arriving
    def _arr_palm(self, P, a, t, cam, F, tg):
        """Blown from an open palm: a stream of dust that settles into the letters in reading order."""
        o, r, u, nrm = F
        w = self.W
        src = self._point(self.source, t, cam, o - r * (0.72 * w) + u * (self.ybot - 0.35 * self.Ht)
                          + nrm * (0.25 * w))
        ctr = o + u * self.ymid
        ln = float(np.linalg.norm(ctr - src)) + 1e-6
        ax = (ctr - src) / ln
        blow = _unit(self.opts.get("blow", ax * 0.75 + u * 0.65 + nrm * 0.15))
        s = self.s
        p = np.clip((a - (0.03 + 0.52 * (0.8 * self.ord + 0.2 * s[:, 0]))) / 0.43, 0.0, 1.0)
        e = 1.0 - (1.0 - p) ** 2.4
        jit = (s[:, 1:4] - 0.5)
        p0 = (src[None, :] + jit * 0.03 * w).astype(np.float32)
        p1 = (src + blow * (0.42 * ln))[None, :].astype(np.float32) + jit * (0.22 * ln)
        p2 = tg - (ax * (0.28 * ln))[None, :].astype(np.float32) + self._world(F, 0 * e, (s[:, 2] - 0.3) * 0.10 * ln,
                                                                               (s[:, 3] - 0.3) * 0.16 * ln)
        pos = _bez(p0, p1, p2, tg, e)
        amp = (np.maximum(np.sin(np.pi * e), 0.0) ** 1.3) * (0.06 * ln)
        pos += _swirl(pos, t, 1.9 / max(w, 1e-6) * 4.0, 1.7) * amp[:, None]
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = _ss(0.0, 0.05, p)
        P["assist"] = _ss(0.78, 1.0, p)
        P["emit"] = 1.0 + 1.2 * np.exp(-np.abs(p - 1.0) / 0.03) * (p < 1.0)
        if self.source is None or self.opts.get("palm_light", False):
            g = float(_ss(0.0, 0.08, a) * (1.0 - _ss(0.62, 0.95, a)))
            if g > 0.01:     # the giving hand as a small warm light, when no body gives it
                P["extra"].append(dict(pos=src[None, :], size=0.018 * w, color=lin(WARM), alpha=0.9 * g, emit=2.0,
                                       kind="spark", twinkle=0.5))
                P["extra"].append(dict(pos=src[None, :], size=0.16 * w, color=self.c_glow, alpha=0.08 * g,
                                       kind="soft"))

    def _fly_petals(self, a, t, F, k_of, turn=1.0, lift=1.0, reach=1.0):
        """Offsets (plane frame) of the carriers on their spiral: k is 1 far away, 0 in place."""
        m = self.M
        s = self.s[:m]
        k = k_of
        w = self.W
        # every petal's path is a spiral between its place and one far point of the sky (the arm): together
        # they make one swirling stream
        arm = self.opts.get("arm", 2.3)                               # the direction the stream comes from (radians)
        gap = np.mod(arm - self.phi[:m] + 0.5 * (s[:, 2] - 0.5), TAU) + TAU * self.opts.get("swirl", 1.0)
        rho = self.rho[:m] + (1.05 * w * reach * (0.8 + 0.4 * s[:, 1]) - self.rho[:m]) * k
        phi = self.phi[:m] + turn * gap * k ** 1.25
        dx = rho * np.cos(phi) - self.xl[:m]
        dy = rho * np.sin(phi) + self.ymid - self.yl[:m] + lift * 0.25 * self.Ht * k * k
        dz = w * reach * (0.55 * (s[:, 3] - 0.2) + 0.35) * k
        return dx, dy, dz

    def _arr_petals(self, P, a, t, cam, F, tg):
        """Petals spiral in and land; where each lands, its part of the letters lights."""
        m = self.M
        s = self.s[:m]
        st = 0.02 + 0.50 * (0.7 * self.ord[:m] + 0.3 * s[:, 0])
        p = np.clip((a - st) / 0.44, 0.0, 1.0)
        e = 1.0 - (1.0 - p) ** 2.0
        dx, dy, dz = self._fly_petals(a, t, F, 1.0 - e)
        delta = self._world(F, dx, dy, dz)
        if self.source is not None and not isinstance(self.source, Word):
            src = points_of(self.source, t, cam)       # petals that come from a body or a hand
            j = (np.arange(m) * len(src)) // m
            k = ((1.0 - e) ** 0.7)[:, None]
            delta = delta * (1.0 - k) * 0.6 + (src[j] - tg[:m]) * k + delta * (k * (1 - k)) * 1.2
        pc = tg[:m] + delta
        self._patches(P, a, st + 0.44)
        fol = self.s[:, 3] < 0.16                       # fine dust that rides with each petal
        fly = fol & (P["alpha"] < 1.0)
        if fly.any():
            cj = self.ci[fly]
            P["pos"] = tg.copy()
            P["pos"][fly] = tg[fly] + delta[cj] * (1.0 + 0.3 * (self.s[fly, 1] - 0.5))[:, None]
            a0 = _ss(0.0, 0.06, p[cj]) * 0.5
            P["alpha"][fly] = np.maximum(P["alpha"][fly], a0)
            P["assist"] = np.where(fly, _ss(0.85, 1.0, p[self.ci]), 1.0).astype(np.float32)
        vis = (p > 0.0) & (p < 1.0)
        if vis.any():
            big = (0.020 + 0.016 * s[:, 1]) * self.W * self.opts.get("petal_size", 1.0)
            size = _mix(big, self.size0[:m] * 2.0, e ** 3)
            cols = np.stack([lin("#ff8fa3"), lin("#ffb19a"), lin("#ffd9c9")]).astype(np.float32)
            pc_col = _mix(cols[(s[:, 2] * 3).astype(int) % 3], self.c_letter[None, :], (e ** 4)[:, None])
            al = _ss(0.0, 0.07, p) * (1.0 - _ss(0.93, 1.0, p))
            rot = np.stack([s[:, 0] * TAU + t * (1.2 + 2.0 * s[:, 1]), s[:, 2] * TAU + t * (2.0 + 3.0 * s[:, 3])], 1)
            P["extra"].append(dict(pos=pc[vis], size=size[vis], color=pc_col[vis], alpha=al[vis] * 0.95,
                                   rot=rot[vis], kind="petal", seed=s[vis, 0]))

    def _fly_flock(self, a, t, F):
        """Offsets (plane frame, from the word's centre) of the birds while they wheel as one flock."""
        m = self.M
        s = self.s[:m]
        w = self.W
        turns = self.opts.get("turns", 1.15)
        lag = 0.10 * s[:, 0]
        th = TAU * turns * (a - lag) + self.opts.get("flock_from", 2.6)
        rad = 0.85 * w * (1.0 - 0.40 * a)
        cx, cz = rad * np.cos(th), 0.9 * rad * np.sin(th)
        cy = self.ymid + self.opts.get("flock_lift", 0.15) * self.Ht + 0.09 * w * np.sin(th * 1.7 + 0.6)
        wave = 1.0 + 0.35 * np.sin(t * 1.6 + s[:, 1] * TAU)
        ox = (s[:, 1] - 0.5) * 0.80 * w * wave
        oy = (s[:, 2] - 0.5) * 0.20 * w * wave + 0.04 * w * np.sin(t * 2.3 + s[:, 3] * TAU)
        oz = (s[:, 3] - 0.5) * 0.45 * w * wave
        return cx + ox, cy + oy, cz + oz

    def _arr_flock(self, P, a, t, cam, F, tg):
        """A flock of birds wheels round, then each bird peels off to its place: the words in formation."""
        m = self.M
        s = self.s[:m]
        st = 0.30 + 0.36 * (0.75 * self.ord[:m] + 0.25 * s[:, 0])
        dur = 0.30

        def place(a_, t_):
            p_ = np.clip((a_ - st) / dur, 0.0, 1.0)
            e_ = p_ * p_ * (3.0 - 2.0 * p_)
            fx, fy, fz = self._fly_flock(a_, t_, F)
            k_ = 1.0 - e_
            return self._world(F, (fx - self.xl[:m]) * k_, (fy - self.yl[:m]) * k_, fz * k_), p_, e_

        delta, p, e = place(a, t)
        da = 0.012
        ta = max(self.t_read0 - self.t_in, 1e-6)
        d2, _, _ = place(a + da, t + da * ta)
        pc = tg[:m] + delta
        rot = self._screen_rot(cam, (d2 - delta))
        hold = 0.035                                    # the birds stand as the letters for a moment
        self._patches(P, a, st + dur + hold, spread=0.03)
        seen = _ss(0.0, 0.08, a)
        gone = 1.0 - _ss(st + dur + hold, st + dur + hold + 0.05, a)
        big = (0.018 + 0.012 * s[:, 2]) * self.W * self.opts.get("bird_size", 1.0)
        size = _mix(big, np.maximum(self.size0[:m] * 4.0, big * 0.45), e)
        vis = (seen * gone) > 0.01
        if vis.any():
            P["extra"].append(dict(pos=pc[vis], size=size[vis], color=_mix(lin(WARM), self.c_letter, 0.4),
                                   alpha=(seen * gone)[vis] * 0.75, rot=rot[vis], kind="bird", seed=s[vis, 3]))

    def _arr_stars(self, P, a, t, cam, F, tg):
        """Stars come out of the deep sky onto the letters, fine lines join them, then the letters fill."""
        m = self.M
        s = self.s[:m]
        w = self.W
        k = (1.0 - _ss(0.0, 0.5, a - 0.2 * s[:, 0])) ** 1.5
        deep = (0.5 + 3.2 * s[:, 1] ** 2) * w
        delta = self._world(F, (s[:, 2] - 0.5) * 1.5 * w * k, (s[:, 3] - 0.35) * 1.1 * w * k, -deep * k)
        pc = tg[:m] + delta
        seen = _ss(0.0, 0.10, a - 0.14 * s[:, 3])
        fill = 0.68 + 0.24 * self.cd ** 0.7 + 0.04 * self.ord
        dt = a - fill
        P["alpha"] = _ss(0.0, 0.06, dt)
        P["emit"] = 1.0 + 1.2 * np.exp(-np.maximum(dt, 0.0) / 0.05) * (dt > 0.0)
        fade = 1.0 - float(_ss(0.72, 1.0, a))
        P["extra"].append(dict(pos=pc, size=self.size0[:m] * (2.2 + 2.2 * s[:, 1]) * (1.0 - 0.4 * (1.0 - fade)),
                               color=_mix(lin(WARM), self.c_letter, 0.3), alpha=seen * fade, emit=2.2, kind="spark",
                               twinkle=0.8, seed=s[:, 0]))
        if len(self.edges):
            ea, eb = self.edges[:, 0], self.edges[:, 1]
            oe = 0.5 * (self.ord[ea] + self.ord[eb])
            grow = _ss(0.0, 0.07, a - (0.30 + 0.30 * oe))
            al = grow * (1.0 - float(_ss(0.86, 1.0, a))) * 0.9
            vis = al > 0.01
            if vis.any():
                pa, pb = pc[ea[vis]], pc[eb[vis]]
                P["extra"].append(dict(pos=pa, pos2=pa + (pb - pa) * grow[vis][:, None], size=0.003 * w,
                                       color=_mix(lin(WARM), self.c_glow, 0.5), alpha=al[vis], kind="line"))

    def _arr_touch(self, P, a, t, cam, F, tg):
        """Where two hands touch a flare is born; it writes the words outward from that point."""
        o, r, u, nrm = F
        w = self.W
        f = self._point(self.source, t, cam, o + u * self.ymid).astype(np.float32)
        s = self.s
        d = tg - f[None, :]
        dist = np.linalg.norm(d, axis=1)
        dmax = float(dist.max()) + 1e-6
        ta = float(self.opts.get("touch_at", 0.10))        # the share of the arrival before the touch
        rest = 1.0 - ta
        p = np.clip((a - (ta + rest * 0.56 * (dist / dmax) ** 0.85)) / (rest * 0.42), 0.0, 1.0)
        e = 1.0 - (1.0 - p) ** 2.6
        side = np.cross(d, nrm.astype(np.float32)[None, :]) * np.where(s[:, 0] < 0.5, -1.0, 1.0)[:, None]
        arc = np.sin(np.pi * e)
        pos = f[None, :] + d * e[:, None] + side * (arc * 0.22)[:, None] \
            + nrm.astype(np.float32)[None, :] * (arc * dist * 0.35 * (s[:, 2] - 0.3))[:, None]
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = _ss(0.0, 0.04, p)
        P["assist"] = _ss(0.75, 1.0, p)
        two = np.where((s[:, 1] < 0.5)[:, None], lin("#ffd27a")[None, :], lin("#7ec8ff")[None, :]).astype(np.float32)
        P["color"] = _mix(two * 1.2, self.c_letter[None, :], (e ** 2)[:, None])
        P["emit"] = 1.0 + 1.5 * np.exp(-np.abs(p - 1.0) / 0.04) * (p < 1.0)
        if a < ta + 0.03 and (self.source is None or self.opts.get("comets", False)):
            # two lights of two colours come together (helper BODY's two hands, when a film has them)
            q = float(np.clip(a / ta, 0.0, 1.0))
            for sgn, hexc in ((-1.0, "#ffd27a"), (1.0, "#7ec8ff")):
                def at_(qq):
                    k = (1.0 - qq) ** 1.6
                    return f + (r * (sgn * 0.85 * w * k) + u * (0.10 * w * np.sin(np.pi * qq) * sgn)
                                + nrm * (0.25 * w * k)).astype(np.float32)

                head, tail = at_(q), at_(max(q - 0.22, 0.0))
                al = float(_ss(0.0, 0.25, q) * (1.0 - _ss(ta, ta + 0.03, a)))
                P["extra"].append(dict(pos=head[None, :], size=0.035 * w, color=lin(hexc), alpha=al, emit=4.0,
                                       kind="spark", twinkle=0.3))
                P["extra"].append(dict(pos=tail[None, :], pos2=head[None, :], size=0.022 * w, color=lin(hexc),
                                       alpha=0.0, alpha2=0.8 * al, kind="ribbon"))
        fl = float(_ss(ta - 0.04, ta + 0.01, a) * (1.0 - _ss(ta + 0.04, ta + 0.5 * rest, a)))
        if fl > 0.01:
            P["extra"].append(dict(pos=f[None, :], size=0.05 * w, color=lin(WARM), alpha=fl, emit=8.0, kind="spark",
                                   dof=False))
            P["extra"].append(dict(pos=f[None, :], size=0.55 * w, color=_mix(lin("#ffd27a"), lin("#7ec8ff"), 0.5),
                                   alpha=0.10 * fl, kind="soft", dof=False))
        ray = np.nonzero((s[:, 3] < 0.012) & (p > 0.0) & (p < 0.98))[0]
        if ray.size:
            P["extra"].append(dict(pos=np.repeat(f[None, :], ray.size, 0), pos2=pos[ray], size=0.0012 * w,
                                   color=two[ray], alpha=0.0, alpha2=0.45 * (1.0 - e[ray]), kind="line"))

    def _arr_shaft(self, P, a, t, cam, F, tg):
        """Flakes come down a shaft of light from above and assemble into the words."""
        m = self.M
        s = self.s[:m]
        w = self.W
        st = 0.03 + 0.45 * (0.5 * self.ord[:m] + 0.5 * s[:, 0])
        p = np.clip((a - st) / 0.50, 0.0, 1.0)
        e = 1.0 - (1.0 - p) ** 1.8
        k = 1.0 - e
        fall = (0.7 + 1.5 * s[:, 1]) * 1.05 * w
        dx = -self.xl[:m] * 0.78 * k ** 0.8 + 0.05 * w * np.sin(t * 1.1 + s[:, 2] * TAU) * k
        dz = 0.06 * w * np.sin(t * 0.9 + s[:, 3] * TAU) * k
        delta = self._world(F, dx, fall * k, dz)
        pc = tg[:m] + delta
        self._patches(P, a, st + 0.50)
        vis = (p > 0.0) & (p < 1.0)
        if vis.any():
            big = (0.013 + 0.016 * s[:, 2]) * w * self.opts.get("flake_size", 1.0)
            size = _mix(big, self.size0[:m] * 2.0, e ** 3)
            cols = np.stack([lin("#ffe2a8"), lin("#fff3d8"), lin("#cfe2ff")]).astype(np.float32)
            col = _mix(cols[(s[:, 3] * 3).astype(int) % 3], self.c_letter[None, :], (e ** 4)[:, None])
            al = _ss(0.0, 0.10, p) * (1.0 - _ss(0.94, 1.0, p))
            rot = np.stack([s[:, 0] * TAU + t * (0.8 + 1.6 * s[:, 1]), s[:, 2] * TAU + t * (1.5 + 2.5 * s[:, 3])], 1)
            P["extra"].append(dict(pos=pc[vis], size=size[vis], color=col[vis], alpha=al[vis], rot=rot[vis],
                                   kind="flake", seed=s[vis, 0], emit=1.4))

    def _arr_lake(self, P, a, t, cam, F, tg):
        """The words show first as a reflection in the still water, then rise out of it, column by column."""
        s = self.s
        level = float(self.opts.get("water", 0.0))
        p = np.clip((a - (0.24 + 0.48 * self.xn)) / 0.27, 0.0, 1.0)
        e = 1.0 - (1.0 - p) ** 3 + 0.05 * np.sin(np.pi * p) * (1.0 - p)
        top = float(tg[:, 1].max()) - level
        pos = tg.copy()
        pos[:, 1] = tg[:, 1] - (1.0 - e) * (top + 0.10 * self.Ht)
        depth = pos[:, 1] - level
        under = depth < 0.0
        near = np.exp(-np.abs(depth) / (0.035 * self.Ht + 1e-6))
        P["pos"] = pos
        P["alpha"] = np.where(under, 0.9 * _ss(-0.10 * self.Ht, 0.0, depth), 1.0).astype(np.float32)
        P["emit"] = (1.0 + 2.2 * near * (p < 1.0)).astype(np.float32)
        P["assist"] = _ss(0.55, 1.0, p)
        P["split"] = under
        # the reflection that is there before the words
        k = (1.0 - e) * float(_ss(0.0, 0.20, a))
        vis = k > 0.01
        if vis.any():
            rp = tg[vis].copy()
            rp[:, 1] = 2.0 * level - rp[:, 1]
            d = (level - rp[:, 1])
            rp[:, 0] += 0.012 * self.W * np.sin(d * 9.0 / max(self.Ht, 1e-6) + t * 1.7) * (0.3 + d / max(self.Ht, 1e-6))
            P["extra"].append(dict(pos=rp, size=self.size0[vis] * 1.5, color=_mix(self.c_letter, lin("#9fc4ff"), 0.35),
                                   alpha=k[vis] * self.wt[vis] * 0.40, kind="soft", reflect=False,
                                   seed=s[vis, 1], twinkle=0.5))

    def _arr_gather(self, P, a, t, cam, F, tg):
        """Many small lights walk in over the water from every side, stand under the words and rise into them."""
        o, r, u, nrm = F
        m = self.M
        s = self.s[:m]
        w = self.W
        ground = float(self.opts.get("water", 0.0)) + float(self.opts.get("carry", 1.15))
        st = 0.30 * s[:, 0]
        p = np.clip((a - st) / 0.62, 0.0, 1.0)
        walk = _ss(0.0, 0.62, p)
        lift = _ss(0.58, 1.0, p)
        ang = TAU * s[:, 1]
        rad = (0.75 + 1.7 * s[:, 2]) * w
        foot = tg[:m].copy()
        foot[:, 1] = ground
        start = foot + (np.cos(ang) * rad)[:, None] * r.astype(np.float32) \
            + (np.sin(ang) * rad * 0.9)[:, None] * nrm.astype(np.float32)
        if self.source is not None and not isinstance(self.source, Word):
            src = points_of(self.source, t, cam)
            start = src[(np.arange(m) * len(src)) // m].copy()
            start[:, 1] = ground
        pc = start + (foot - start) * walk[:, None]
        pc[:, 1] += 0.035 * np.abs(np.sin(t * 5.5 + s[:, 3] * TAU)) * (1.0 - lift) * (p > 0.0)
        pc = pc + (tg[:m] - foot) * lift[:, None]
        pc[:, 0] += 0.04 * w * np.sin(t * 1.3 + s[:, 2] * TAU) * np.sin(np.pi * lift) * 0.5
        self._patches(P, a, st + 0.62, spread=0.05, flash=1.2)
        nine = np.stack([lin(c) for c in NINE]).astype(np.float32)
        col = _mix(nine[np.arange(m) % 9], self.c_letter[None, :], (lift ** 3)[:, None])
        seen = _ss(0.0, 0.08, a) * (1.0 - _ss(0.92, 1.0, p))
        size = _mix(np.full(m, 0.010 * w, np.float32), self.size0[:m] * 2.5, lift ** 2)
        vis = (seen > 0.01) & (np.arange(m) % 3 == 0)      # one light in three is seen; each brings its neighbours
        if vis.any():
            P["extra"].append(dict(pos=pc[vis], size=size[vis], color=col[vis], alpha=seen[vis], emit=1.8,
                                   kind="soft", twinkle=0.35, seed=s[vis, 0], lod=False))
            P["extra"].append(dict(pos=pc[vis], size=size[vis] * 5.0, color=col[vis], alpha=seen[vis] * 0.06,
                                   kind="soft", seed=s[vis, 0]))

    def _ray_source(self, t, cam, F):
        o, r, u, nrm = F
        return self._point(self.source, t, cam, o + u * self.ymid - nrm * (0.30 * self.W))

    def _arr_rays(self, P, a, t, cam, F, tg):
        """Rays from a light behind burn the words out of mist: along the rays first, then outward."""
        if self.source is not None and not isinstance(self.source, Word):
            # the light stands somewhere else (behind a person's head): burn outward from there
            o, r, u, nrm = F
            d = tg - self._ray_source(t, cam, F).astype(np.float32)[None, :]
            dx, dy = d @ r.astype(np.float32), d @ u.astype(np.float32)
            rho = np.hypot(dx, dy)
            rho = (rho - rho.min()) / max(float(np.ptp(rho)), 1e-6)
            ray = (np.maximum(np.cos(np.arctan2(dy, dx)[:, None] - self.fan[None, :]), 0.0) ** 26).max(axis=1)
        else:
            rho, ray = self.rho / self.rho_max, self.ray
        rev = np.clip(0.14 + 0.62 * rho ** 0.9 - 0.16 * ray, 0.03, 0.9)
        dt = a - rev
        heat = np.exp(-np.maximum(dt, 0.0) / 0.07) * (dt > 0.0)
        P["alpha"] = _ss(0.0, 0.03, dt)
        P["emit"] = 1.0 + 5.0 * heat
        white = lin("#fff8ec").astype(np.float32)
        P["color"] = _mix(self.c_letter[None, :], white[None, :] * 1.3, heat[:, None])

    def _arr_morph(self, P, a, t, cam, F, tg):
        """The particles of another word (or of any point set) fly over and become this word."""
        src = points_of(self.source, t, cam)
        if src is None:
            return self._arr_palm(P, a, t, cam, F, tg)
        if self.opts.get("carry"):
            return self._morph_carried(P, a, t, cam, F, tg, src, self.opts["carry"])
        n, w = self.N, self.W
        s = self.s
        j = (np.arange(n, dtype=np.int64) * len(src)) // n
        p0 = src[j]
        p = np.clip((a - 0.42 * (0.7 * self.ord + 0.3 * s[:, 0])) / 0.55, 0.0, 1.0)
        e = p * p * (3.0 - 2.0 * p)
        arc = np.sin(np.pi * e)
        pos = p0 + (tg - p0) * e[:, None]
        pos += _swirl(p0, t, 2.5 / max(w, 1e-6) * 4.0, 0.9) * (arc * 0.07 * w)[:, None]
        pos += F[3].astype(np.float32)[None, :] * (arc * 0.10 * w * (s[:, 2] - 0.2))[:, None]
        P["pos"] = pos.astype(np.float32)
        P["assist"] = np.maximum(1.0 - _ss(0.0, 0.2, p), _ss(0.8, 1.0, p))
        if isinstance(self.source, Word):
            other = self.source
            ratio = float(np.clip(len(src) / n * (float(np.median(other.size0)) / float(np.median(self.size0))) ** 2,
                                  0.3, 2.5))
            P["alpha"] = _mix(ratio, 1.0, e).astype(np.float32)
            P["wt"] = _mix(other.wt[j], self.wt, e).astype(np.float32)
            P["color"] = _mix(other.c_letter[None, :], self.c_letter[None, :], e[:, None])
            P["size"] = _mix(other.size0[j], self.size0, e).astype(np.float32)
            P["glow"] = _mix(other.c_glow * other.halo / max(self.halo, 1e-6), self.c_glow,
                             float(np.clip((a - 0.05) / 0.5, 0.0, 1.0)))
        else:
            P["alpha"] = _ss(0.0, 0.05, a) * np.ones(n, np.float32)

    # ------------------------------------------------------------------ more arrivals (for the ten films)
    def _pen_times(self, t, cam, F):
        """For a pen that someone else moves (source: a comet head, a fingertip): when each point is written
        (the moment the pen passes nearest to it, as a share of the arrival) and where the pen was then, on
        the word's plane. Worked out once."""
        if self._pen_cache is None:
            k = 220
            ts = np.linspace(self.t_in, self.t_read0 - 0.12 * (self.t_read0 - self.t_in), k)
            loc = np.zeros((k, 3))
            for j, tj in enumerate(ts):
                c = self._cam(tj, None)
                o, r, u, nrm = self.frame(tj, c)
                pw = self._point(self.source, tj, c, o)
                d = pw - o
                loc[j] = (d @ r, d @ u, d @ nrm)
            best = np.zeros(self.N, np.int64)
            dmin = np.full(self.N, 1e30)
            for j0 in range(0, k, 20):                       # the nearest passage of the pen to every point
                dx = self.xl[:, None] - loc[None, j0:j0 + 20, 0]
                dy = self.yl[:, None] - loc[None, j0:j0 + 20, 1]
                d2 = dx * dx + dy * dy
                jj = d2.argmin(axis=1)
                dj = d2[np.arange(self.N), jj]
                better = dj < dmin
                best[better] = jj[better] + j0
                dmin[better] = dj[better]
            rev = (ts[best] - self.t_in) / max(self.t_read0 - self.t_in, 1e-6)
            self._pen_cache = (rev.astype(np.float32), loc[best].astype(np.float32))
        return self._pen_cache

    def _arr_pen(self, P, a, t, cam, F, tg):
        """Written by a moving pen: the ink leaves the nib and runs to its place, in writing order. The pen
        is the word's own (pen(t) tells where it is) or someone else's (source: a comet head, a fingertip)."""
        s = self.s
        w = self.W
        if self.source is not None and not isinstance(self.source, Word):
            rev, loc = self._pen_times(t, cam, F)
            start = self._local(F, t, loc[:, 0], loc[:, 1], loc[:, 2])
            nib = None
        else:
            q = self.worder
            rev = 0.04 + 0.88 * q
            start = self._local(F, t, np.interp(q, self.pen_q, self.pen_x), np.interp(q, self.pen_q, self.pen_y))
            nib = self.pen(t, cam) if self.opts.get("nib", True) else None
        dt = a - rev
        k = _ss(0.0, self.opts.get("flow", 0.06), dt - 0.01 * s[:, 0])
        pos = start + (tg - start) * k[:, None]
        pos += F[3].astype(np.float32)[None, :] * (np.sin(np.pi * k) * 0.02 * w * (s[:, 2] - 0.3))[:, None]
        heat = np.exp(-np.maximum(dt, 0.0) / 0.04) * (dt > 0.0)
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = _ss(0.0, 0.01, dt)
        P["emit"] = 1.0 + 3.5 * heat
        P["assist"] = _ss(0.6, 1.0, k)
        P["color"] = _mix(self.c_letter[None, :], lin("#fff8ec").astype(np.float32)[None, :] * 1.3, heat[:, None])
        if nib is not None and 0.03 < a < 0.95:
            P["extra"].append(dict(pos=nib[None, :], size=0.012 * w, color=lin(WARM), alpha=1.0, emit=5.0,
                                   kind="spark", twinkle=0.3))
            P["extra"].append(dict(pos=nib[None, :], size=0.10 * w, color=self.c_glow, alpha=0.12, kind="soft"))

    def _arr_reveal(self, P, a, t, cam, F, tg):
        """Revealed behind a moving edge: edge= "right", "left", "up", "down" (a lowering height), "out",
        "in", or gate= a function (places in the world (N, 3), t) -> 0..1 for an edge of the director's own
        (a wave's crest, a veil's hem, a falling height). The edge itself glows."""
        gate = self.opts.get("gate")
        if gate is not None:
            g = np.clip(np.asarray(gate(tg, t), np.float32), 0.0, 1.0)
        else:
            edge = self.opts.get("edge", "right")
            c = {"right": self.xn, "left": 1.0 - self.xn, "up": self.yn, "down": 1.0 - self.yn,
                 "out": self.rho / self.rho_max, "in": 1.0 - self.rho / self.rho_max}[edge]
            soft = float(self.opts.get("soft", 0.07))
            front = -soft + (1.0 + 2.0 * soft) * float(_ss(0.02, 0.96, a))
            g = np.clip((front - c) / soft, 0.0, 1.0).astype(np.float32)
        P["alpha"] = g
        P["emit"] = (1.0 + self.opts.get("edge_glow", 3.0) * 4.0 * g * (1.0 - g)).astype(np.float32)

    def _thread(self, P, F, t, q_head, alpha, n_st=110, amp=0.05, needle=True):
        """A sewing thread along the writing as far as q_head: short stitches that show, with gaps between."""
        if alpha <= 0.01 or q_head <= 0.0:
            return
        w = self.W
        em = self.metres_per_em()
        qs = np.linspace(0.0, 1.0, n_st + 1)
        x = np.interp(qs, self.pen_q, self.pen_x)
        drop = np.where(qs < (0.14 if self.lab.any() else 0.0), 0.5 * self.label_size, 0.40) * em   # under the letters
        y = np.interp(qs, self.pen_q, self.pen_y) - drop + amp * em * np.where(np.arange(n_st + 1) % 2 == 0, 1.0, -1.0)
        pts = self._local(F, t, x, y, np.full(n_st + 1, 0.01 * w))
        vis = np.clip((q_head - qs[:-1]) * n_st, 0.0, 1.0)             # how much of each stitch is drawn
        ln = np.hypot(np.diff(x), np.diff(y))
        on = (np.arange(n_st) % 2 == 0) & (vis > 0.0) & (ln < 2.5 * np.median(ln))   # no stitch across a line break
        if on.any():
            a_, b_ = pts[:-1][on], pts[1:][on]
            P["extra"].append(dict(pos=a_, pos2=a_ + (b_ - a_) * vis[on][:, None], size=0.0035 * w,
                                   color=_mix(lin(WARM), self.c_glow, 0.35), alpha=0.9 * alpha, kind="line"))
        if needle and q_head < 1.0:
            nd = self._local(F, t, np.array([np.interp(q_head, self.pen_q, self.pen_x)]),
                             np.array([np.interp(q_head, self.pen_q, self.pen_y)]), np.array([0.01 * w]))
            P["extra"].append(dict(pos=nd, size=0.012 * w, color=lin(WARM), alpha=alpha, emit=5.0, kind="spark",
                                   twinkle=0.3))

    def _arr_stitch(self, P, a, t, cam, F, tg):
        """Stitched in: a needle runs along the writing, its thread shows as short stitches, and the letters
        are pulled tight behind it."""
        s = self.s
        w = self.W
        q = self.worder
        head = float(np.clip((a - 0.04) / 0.84, 0.0, 1.0))
        dt = a - (0.04 + 0.84 * q)
        k = _ss(0.0, 0.07, dt)
        loose = (1.0 - k)
        pos = tg + F[3].astype(np.float32)[None, :] * (loose * 0.05 * w)[:, None]
        pos += F[2].astype(np.float32)[None, :] * (loose * 0.03 * w * (s[:, 1] - 0.5))[:, None]
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = _ss(0.0, 0.015, dt)
        P["emit"] = 1.0 + 2.0 * np.exp(-np.maximum(dt, 0.0) / 0.05) * (dt > 0.0)
        P["assist"] = _ss(0.5, 1.0, k)
        self._thread(P, F, t, head, float(1.0 - _ss(0.86, 1.0, a)))

    def _arr_weave(self, P, a, t, cam, F, tg):
        """Woven in: threads run across and down like warp and weft; a letter shows where both have passed."""
        w = self.W
        nr, nc = int(self.opts.get("rows", 14)), int(self.opts.get("cols", 34))
        x0, x1 = float(self.xl.min()), float(self.xl.max())
        y0, y1 = self.ybot, self.ytop
        jr = np.minimum((self.yn * nr).astype(np.int64), nr - 1)          # the row of each point (0 at the bottom)
        jc = np.minimum((self.xn * nc).astype(np.int64), nc - 1)
        row_dir = np.where(np.arange(nr) % 2 == 0, 1.0, -1.0)            # rows run to and fro
        ar = 0.04 + 0.44 * (nr - 1 - np.arange(nr)) / max(nr - 1, 1)     # from the top row down
        bc = 0.28 + 0.44 * np.arange(nc) / max(nc - 1, 1)
        dr, dc = 0.22, 0.22
        along_r = np.where(row_dir[jr] > 0, self.xn, 1.0 - self.xn)
        tr = ar[jr] + dr * along_r
        tc = bc[jc] + dc * (1.0 - self.yn)
        dt = a - np.maximum(tr, tc)
        P["alpha"] = _ss(0.0, 0.03, dt)
        P["emit"] = 1.0 + 1.8 * np.exp(-np.maximum(dt, 0.0) / 0.05) * (dt > 0.0)
        fade = float(1.0 - _ss(0.86, 1.0, a))
        if fade > 0.01:
            col = _mix(lin(WARM), self.c_glow, 0.4)
            g = np.clip((a - ar) / dr, 0.0, 1.0)
            on = g > 0.0
            if on.any():
                ys = y0 + (np.arange(nr) + 0.5) / nr * (y1 - y0)
                xa = np.where(row_dir > 0, x0, x1)
                xb = xa + (np.where(row_dir > 0, x1, x0) - xa) * g
                pa = self._local(F, t, xa[on], ys[on])
                pb = self._local(F, t, xb[on], ys[on])
                P["extra"].append(dict(pos=pa, pos2=pb, size=0.0025 * w, color=col, alpha=0.5 * fade, kind="line"))
            g = np.clip((a - bc) / dc, 0.0, 1.0)
            on = g > 0.0
            if on.any():
                xs = x0 + (np.arange(nc) + 0.5) / nc * (x1 - x0)
                pa = self._local(F, t, xs[on], np.full(int(on.sum()), y1))
                pb = self._local(F, t, xs[on], y1 + (y0 - y1) * g[on])
                P["extra"].append(dict(pos=pa, pos2=pb, size=0.0025 * w, color=col, alpha=0.4 * fade, kind="line"))

    def _morph_carried(self, P, a, t, cam, F, tg, src, kind):
        """Born from someone else's point field: its points fly in as petals, birds, flakes or lights and
        land as letters; each lights its part of the word."""
        m = self.M
        s = self.s[:m]
        w = self.W
        j = (np.arange(m, dtype=np.int64) * len(src)) // m
        st = 0.02 + 0.48 * (0.6 * self.ord[:m] + 0.4 * s[:, 0])
        dur = 0.46

        def place(a_, t_):
            p_ = np.clip((a_ - st) / dur, 0.0, 1.0)
            e_ = p_ * p_ * (3.0 - 2.0 * p_)
            arc = np.sin(np.pi * e_)
            q_ = src[j] + (tg[:m] - src[j]) * e_[:, None]
            q_ += _swirl(src[j], t_, 2.5 / max(w, 1e-6) * 4.0, 1.3) * (arc * 0.06 * w)[:, None]
            q_ += F[2].astype(np.float32)[None, :] * (arc * 0.10 * w * (s[:, 2] - 0.2))[:, None]
            return q_, p_, e_

        pc, p, e = place(a, t)
        self._patches(P, a, st + dur)
        vis = (p < 1.0)
        al = _ss(0.0, 0.04, a) * (1.0 - _ss(0.93, 1.0, p))
        if not vis.any():
            return
        if kind == "bird":
            da = 0.012
            p2, _, _ = place(a + da, t + da * max(self.t_read0 - self.t_in, 1e-6))
            rot = self._screen_rot(cam, p2 - pc)
            big = (0.018 + 0.012 * s[:, 2]) * w * self.opts.get("bird_size", 1.0)
            P["extra"].append(dict(pos=pc[vis], size=_mix(big, np.maximum(self.size0[:m] * 4.0, big * 0.45), e)[vis],
                                   color=_mix(lin(WARM), self.c_letter, 0.4), alpha=al[vis] * 0.75, rot=rot[vis],
                                   kind="bird", seed=s[vis, 3]))
            return
        rot = np.stack([s[:, 0] * TAU + t * (1.0 + 1.8 * s[:, 1]), s[:, 2] * TAU + t * (1.8 + 2.6 * s[:, 3])], 1)
        if kind == "petal":
            big = (0.020 + 0.016 * s[:, 1]) * w * self.opts.get("petal_size", 1.0)
            cols = np.stack([lin("#ff8fa3"), lin("#ffb19a"), lin("#ffd9c9")]).astype(np.float32)
        elif kind == "flake":
            big = (0.007 + 0.009 * s[:, 2]) * w * self.opts.get("flake_size", 1.0)
            cols = np.stack([lin("#ffe2a8"), lin("#fff3d8"), lin("#cfe2ff")]).astype(np.float32)
        else:
            kind = "soft"
            big = (0.008 + 0.006 * s[:, 2]) * w
            cols = np.stack([self.c_base, lin(WARM), self.c_base]).astype(np.float32)
        if self.opts.get("carry_colors"):
            cols = np.stack([lin(c) for c in self.opts["carry_colors"]]).astype(np.float32)
        col = _mix(cols[(s[:, 2] * len(cols)).astype(int) % len(cols)], self.c_letter[None, :], (e ** 4)[:, None])
        size = _mix(big, self.size0[:m] * 2.0, e ** 3)
        b = dict(pos=pc[vis], size=size[vis], color=col[vis], alpha=al[vis] * 0.8, kind=kind, seed=s[vis, 0])
        if kind != "soft":
            b["rot"] = rot[vis]
        else:
            b["emit"] = 2.0
        P["extra"].append(b)

    # ------------------------------------------------------------------ nine ways of leaving
    def _own(self, l, start):
        """Per point progress of leaving, 0 at its own start, 1 when everything is gone."""
        return np.clip((l - start) / np.maximum(1.0 - start, 1e-3), 0.0, 1.0)

    def _lea_wind(self, P, l, t, cam, F, tg):
        """The wind takes the words from one side: they stream off into the air as dust."""
        o, r, u, nrm = F
        s = self.s
        w = self.W
        tl = self.t_out - self.t_read1
        wd = self.wind
        along = (self.xl * float(wd @ r) + (self.yl - self.ymid) * float(wd @ u))
        along = (along - along.min()) / max(float(np.ptp(along)), 1e-6)
        st = 0.50 * (1.0 - along) + 0.08 * s[:, 0]
        lp = self._own(l, st)
        sec = np.maximum(l - st, 0.0) * tl
        v = self.opts.get("speed", 0.42) * w
        dist = v * (0.35 * sec + 0.85 * sec * sec) * (0.55 + 0.9 * s[:, 1])
        pos = tg + wd.astype(np.float32)[None, :] * dist[:, None]
        pos += _swirl(tg, t, 3.0 / max(w, 1e-6) * 4.0, 2.3) * (0.10 * w * _ss(0.0, 1.0, sec))[:, None]
        pos += nrm.astype(np.float32)[None, :] * ((s[:, 2] - 0.4) * v * sec * 0.8)[:, None]
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = 1.0 - _ss(0.30, 1.0, lp)
        P["assist"] = 1.0 - _ss(0.0, 0.12, lp)
        P["size"] = self.size0 * (1.0 + 0.9 * lp)

    def _lea_rise(self, P, l, t, cam, F, tg):
        """The words dissolve upward from the top into flakes and sparks."""
        s = self.s
        w = self.W
        tl = self.t_out - self.t_read1
        st = 0.45 * (1.0 - self.yn) + 0.12 * s[:, 0]
        lp = self._own(l, st)
        sec = np.maximum(l - st, 0.0) * tl
        v = self.opts.get("speed", 0.30) * w
        up = v * (0.4 * sec + 0.7 * sec * sec) * (0.5 + 1.0 * s[:, 1])
        pos = tg.copy()
        pos[:, 1] += up
        pos += self._world(F, -self.xl * 0.30 * _ss(0.0, 1.0, lp), 0 * lp, (s[:, 2] - 0.5) * 0.25 * w * lp)
        pos += _swirl(tg, t, 3.0 / max(w, 1e-6) * 4.0, 4.1) * (0.06 * w * _ss(0.0, 1.0, sec))[:, None]
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = 1.0 - _ss(0.10, 0.75, lp)
        P["assist"] = 1.0 - _ss(0.0, 0.12, lp)
        m = self.M
        al = _ss(0.0, 0.10, lp[:m]) * (1.0 - _ss(0.55, 1.0, lp[:m]))
        vis = al > 0.01
        if vis.any():
            sm = s[:m]
            size = (0.006 + 0.012 * sm[:, 2]) * w * self.opts.get("flake_size", 1.0) * _ss(0.0, 0.25, lp[:m])
            cols = np.stack([lin("#ffe2a8"), lin("#fff3d8"), self.c_base]).astype(np.float32)
            rot = np.stack([sm[:, 0] * TAU + t * (0.8 + 1.6 * sm[:, 1]), sm[:, 2] * TAU + t * (1.5 + 2.5 * sm[:, 3])], 1)
            P["extra"].append(dict(pos=pos[:m][vis], size=size[vis], color=cols[(sm[:, 3] * 3).astype(int) % 3][vis],
                                   alpha=al[vis] * 0.8, rot=rot[vis], kind="flake", seed=sm[vis, 0]))

    def _lea_arch(self, P, l, t, cam, F, tg, star=True):
        """The words stream into one light of the arch (to= its place) and wake it."""
        o, r, u, nrm = F
        s = self.s
        w = self.W
        goal = self._point(self.to, t, cam, o + u * (self.ytop + 0.9 * w) - nrm * (0.4 * w)).astype(np.float32)
        p = np.clip((l - 0.44 * (0.6 * self.ord + 0.4 * s[:, 0])) / 0.50, 0.0, 1.0)
        e = (p * p * (3.0 - 2.0 * p)) ** 1.35
        d = goal[None, :] - tg
        p1 = tg + self._world(F, (s[:, 1] - 0.5) * 0.15 * w, 0.10 * w + 0 * e, (s[:, 2] - 0.3) * 0.30 * w)
        p2 = goal[None, :] - d * 0.30 + _swirl(tg, t, 2.0 / max(w, 1e-6) * 4.0, 3.0) * (0.06 * w)
        pos = _bez(tg, p1, p2, np.repeat(goal[None, :], self.N, 0), e)
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = 1.0 - _ss(0.90, 1.0, p)
        P["assist"] = 1.0 - _ss(0.0, 0.12, p)
        P["size"] = self.size0 * (1.0 - 0.4 * e)
        got = float((p >= 1.0).mean())
        star = (0.15 + 0.85 * got) * float(_ss(0.05, 0.30, l) * (1.0 - _ss(0.90, 1.0, l))) if star else 0.0
        if star > 0.01:
            P["extra"].append(dict(pos=goal[None, :], size=0.10 * w, color=_mix(lin(WARM), self.c_base, 0.35),
                                   alpha=star, emit=4.0 + 8.0 * got, kind="spark", twinkle=0.3, dof=False))
            P["extra"].append(dict(pos=goal[None, :], size=0.6 * w, color=self.c_glow, alpha=0.12 * star,
                                   kind="soft", dof=False))

    def _lea_flock(self, P, l, t, cam, F, tg):
        """The letters lift off as birds and fly away together."""
        o, r, u, nrm = F
        m = self.M
        s = self.s[:m]
        w = self.W
        tl = self.t_out - self.t_read1
        st = 0.42 * (0.6 * self.ord[:m] + 0.4 * s[:, 0])
        away = _unit(self.opts.get("away", self.wind + np.array([0.0, 0.45, 0.0]) - nrm * 0.5))
        v = self.opts.get("speed", 0.55) * w

        def place(l_, t_):
            sec = np.maximum(l_ - st, 0.0) * tl
            d = v * (0.5 * sec + 0.5 * sec * sec) * (0.45 + 1.1 * s[:, 1])
            q = away.astype(np.float32)[None, :] * d[:, None]
            wob = _ss(0.0, 1.0, sec) * 0.10 * w
            q += self._world(F, wob * np.sin(t_ * 1.9 + s[:, 2] * TAU),
                             wob * (0.8 * np.sin(t_ * 1.3 + s[:, 3] * TAU) + 0.15 * sec),
                             wob * np.cos(t_ * 1.6 + s[:, 1] * TAU))
            return q

        delta = place(l, t)
        dl = 0.01
        rot = self._screen_rot(cam, place(l + dl, t + dl * tl) - delta)
        lp = self._own(l, st)
        dt = l - (st[self.ci] + 0.02 * self.cd)
        P["alpha"] = 1.0 - _ss(0.0, 0.05, dt)
        al = _ss(0.0, 0.06, lp) * (1.0 - _ss(0.72, 1.0, lp)) * (l > st)
        vis = al > 0.01
        if vis.any():
            big = (0.018 + 0.012 * s[:, 2]) * w * self.opts.get("bird_size", 1.0)
            size = _mix(np.maximum(self.size0[:m] * 4.0, big * 0.45), big, _ss(0.0, 0.2, lp))
            P["extra"].append(dict(pos=(tg[:m] + delta)[vis], size=size[vis],
                                   color=_mix(lin(WARM), self.c_letter, 0.4), alpha=al[vis] * 0.75, rot=rot[vis],
                                   kind="bird", seed=s[vis, 3]))

    def _lea_petals(self, P, l, t, cam, F, tg):
        """The letters turn to petals that spiral away."""
        m = self.M
        s = self.s[:m]
        st = 0.42 * (0.6 * self.ord[:m] + 0.4 * s[:, 0])
        lp = self._own(l, st)
        k = lp ** 1.6
        dx, dy, dz = self._fly_petals(l, t, F, k, turn=-1.0, lift=0.6, reach=self.opts.get("reach", 0.4))
        tl = self.t_out - self.t_read1
        drift = self.wind.astype(np.float32)[None, :] * (self.opts.get("speed", 0.45) * self.W
                                                         * np.maximum(l - st, 0.0) * tl)[:, None]
        pc = tg[:m] + self._world(F, dx, dy, dz) + drift
        dt = l - (st[self.ci] + 0.02 * self.cd)
        P["alpha"] = 1.0 - _ss(0.0, 0.05, dt)
        al = _ss(0.0, 0.06, lp) * (1.0 - _ss(0.70, 1.0, lp)) * (l > st)
        vis = al > 0.01
        if vis.any():
            big = (0.020 + 0.016 * s[:, 1]) * self.W * self.opts.get("petal_size", 1.0)
            size = _mix(self.size0[:m] * 2.0, big, _ss(0.0, 0.25, lp))
            cols = np.stack([lin("#ff8fa3"), lin("#ffb19a"), lin("#ffd9c9")]).astype(np.float32)
            col = _mix(self.c_letter[None, :], cols[(s[:, 2] * 3).astype(int) % 3], _ss(0.0, 0.2, lp)[:, None])
            rot = np.stack([s[:, 0] * TAU + t * (1.2 + 2.0 * s[:, 1]), s[:, 2] * TAU + t * (2.0 + 3.0 * s[:, 3])], 1)
            P["extra"].append(dict(pos=pc[vis], size=size[vis], color=col[vis], alpha=al[vis] * 0.95, rot=rot[vis],
                                   kind="petal", seed=s[vis, 0]))

    def _lea_sink(self, P, l, t, cam, F, tg):
        """The words fall like rain into the lake and spread over it as rings of light."""
        s = self.s
        w = self.W
        level = float(self.opts.get("water", 0.0))
        tl = self.t_out - self.t_read1
        st = 0.38 * (0.55 * self.xn + 0.45 * s[:, 0])
        sec = np.maximum(l - st, 0.0) * tl
        h = np.maximum(tg[:, 1] - level, 0.01)
        tfall = np.minimum(0.34 * tl, 1.4) * (0.75 + 0.25 * s[:, 1])
        q = np.clip(sec / tfall, 0.0, 1.0)
        pos = tg.copy()
        pos[:, 1] = level + h * (1.0 - q * q)
        after = np.maximum(sec - tfall, 0.0)
        hit = after > 0.0
        ang = TAU * s[:, 2]
        run = 0.30 * w * (1.0 - np.exp(-after * 1.3)) * (0.4 + 0.6 * s[:, 3])
        pos[:, 0] += np.cos(ang) * run * hit
        pos[:, 2] += np.sin(ang) * run * hit
        pos[:, 1] = np.where(hit, level + 0.004, pos[:, 1])
        end = 1.0 - float(_ss(0.86, 1.0, l))
        P["pos"] = pos
        P["alpha"] = np.where(hit, 0.8 * np.exp(-after * 1.5), 1.0).astype(np.float32) * end
        P["emit"] = (1.0 + 3.0 * np.exp(-after / 0.10) * hit).astype(np.float32)
        P["assist"] = 1.0 - _ss(0.0, 0.3, q)
        P["split"] = hit

    def _lea_bokeh(self, P, l, t, cam, F, tg):
        """The words rush toward us and past, opening into great soft discs of light."""
        o, r, u, nrm = F
        s = self.s
        w = self.W
        if cam is not None:
            cr, cu, cf = cam.basis()
            eye = np.asarray(cam.pos, np.float64)
        else:
            cr, cu, cf, eye = r, u, -nrm, o + nrm * (2.5 * w)
        st = 0.35 * s[:, 0]
        lp = self._own(l, st)
        e = lp ** 2.2
        goal = (eye - cf * 0.6)[None, :] + ((s[:, 1] - 0.5) * 1.6)[:, None] * cr[None, :] \
            + ((s[:, 2] - 0.5) * 1.0)[:, None] * cu[None, :]
        pos = tg + (goal.astype(np.float32) - tg) * e[:, None]
        pos += _swirl(tg, t, 2.0 / max(w, 1e-6) * 4.0, 5.0) * (0.05 * w * np.sin(np.pi * e))[:, None]
        keep = s[:, 3] < 0.12
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = np.where(keep, (1.0 - _ss(0.58, 0.90, lp)) * (1.0 + 2.2 * _ss(0.1, 0.5, lp)),
                              1.0 - _ss(0.05, 0.45, lp)).astype(np.float32)
        P["assist"] = 1.0 - _ss(0.0, 0.10, lp)

    def _lea_give(self, P, l, t, cam, F, tg):
        """The particles fly to another body of light (to= a point set, a person) and become part of it."""
        dst = points_of(self.to, t, cam) if not isinstance(self.to, Word) else None
        if dst is None:
            return self._lea_fade(P, l, t, cam, F, tg)
        s = self.s
        w = self.W
        j = (np.arange(self.N, dtype=np.int64) * len(dst)) // self.N
        p = np.clip((l - 0.46 * (0.6 * self.ord + 0.4 * s[:, 0])) / 0.52, 0.0, 1.0)
        e = p * p * (3.0 - 2.0 * p)
        arc = np.sin(np.pi * e)
        pos = tg + (dst[j] - tg) * e[:, None]
        pos += _swirl(tg, t, 2.5 / max(w, 1e-6) * 4.0, 6.0) * (arc * 0.08 * w)[:, None]
        pos += F[3].astype(np.float32)[None, :] * (arc * 0.12 * w * (s[:, 2] - 0.3))[:, None]
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = 1.0 - _ss(0.80, 1.0, p)
        P["assist"] = 1.0 - _ss(0.0, 0.12, p)

    def _lea_stars(self, P, l, t, cam, F, tg):
        """The letters thin to a few stars joined by lines; the stars drift back into the sky."""
        m = self.M
        s = self.s[:m]
        w = self.W
        dt = l - (0.03 + 0.30 * (1.0 - self.cd ** 0.7))
        P["alpha"] = 1.0 - _ss(0.0, 0.07, dt)
        k = _ss(0.22, 1.0, l - 0.1 * s[:, 0]) ** 1.5
        deep = (0.5 + 3.2 * s[:, 1] ** 2) * w
        pc = tg[:m] + self._world(F, (s[:, 2] - 0.5) * 1.2 * w * k, (0.2 + s[:, 3]) * 0.9 * w * k, -deep * k)
        seen = _ss(0.0, 0.12, l) * (1.0 - _ss(0.72 + 0.2 * s[:, 3], 1.0, l))
        vis = seen > 0.01
        if vis.any():
            P["extra"].append(dict(pos=pc[vis], size=(self.size0[:m] * (2.2 + 2.2 * s[:, 1]))[vis],
                                   color=_mix(lin(WARM), self.c_letter, 0.3), alpha=seen[vis], emit=2.2, kind="spark",
                                   twinkle=0.8, seed=s[vis, 0]))
        if len(self.edges):
            ea, eb = self.edges[:, 0], self.edges[:, 1]
            al = float(_ss(0.04, 0.16, l) * (1.0 - _ss(0.30, 0.62, l))) * 0.5
            if al > 0.01:
                P["extra"].append(dict(pos=pc[ea], pos2=pc[eb], size=0.003 * w,
                                       color=_mix(lin(WARM), self.c_glow, 0.5), alpha=al, kind="line"))

    def _lea_stream(self, P, l, t, cam, F, tg):
        """The words leave as one stream: to a point that may move (to= a point or a function of t: a comet,
        a runner's hand), or along a curve (path= points (K, 3), or a function of t that gives them)."""
        path = self.opts.get("path")
        if path is None:
            return self._lea_arch(P, l, t, cam, F, tg, star=bool(self.opts.get("star", False)))
        s = self.s
        w = self.W
        c = np.asarray(path(t) if callable(path) else path, np.float64).reshape(-1, 3)
        seg = np.linalg.norm(np.diff(c, axis=0), axis=1)
        d = np.concatenate([[0.0], np.cumsum(seg)])
        d /= max(d[-1], 1e-9)
        p = np.clip((l - 0.40 * (0.6 * self.ord + 0.4 * s[:, 0])) / 0.56, 0.0, 1.0)
        u_ = _ss(0.12, 1.0, p) ** 1.25
        on = np.stack([np.interp(u_, d, c[:, k]) for k in range(3)], axis=1).astype(np.float32)
        spread = (1.0 - 0.75 * u_) * 0.05 * w
        on += self._world(F, (s[:, 1] - 0.5) * spread, (s[:, 2] - 0.5) * spread, (s[:, 3] - 0.5) * spread)
        join = _ss(0.0, 0.32, p)
        pos = tg + (on - tg) * join[:, None]
        pos += _swirl(tg, t, 2.0 / max(w, 1e-6) * 4.0, 3.7) * (np.sin(np.pi * join) * 0.04 * w)[:, None]
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = 1.0 - _ss(0.90, 1.0, p)
        P["assist"] = 1.0 - _ss(0.0, 0.12, p)
        P["size"] = self.size0 * (1.0 - 0.3 * u_)

    def _lea_doors(self, P, l, t, cam, F, tg):
        """The word parts like a pair of doors: each half swings open on its outer edge and lets us through."""
        s = self.s
        x0, x1 = float(self.xl.min()), float(self.xl.max())
        xs = x0 + float(self.opts.get("split", 0.5)) * (x1 - x0)
        left = self.xl < xs
        hinge = np.where(left, x0, x1)
        ang = np.radians(float(self.opts.get("swing", 100.0))) * float(_ss(0.0, 0.85, l))
        away = -1.0 if self.opts.get("inward", True) else 1.0           # inward: the doors open away from the reader
        dx = self.xl - hinge
        x = hinge + dx * np.cos(ang)
        z = away * np.abs(dx) * np.sin(ang)
        P["pos"] = self._local(F, t, x, self.yl, z + self.zl)
        P["alpha"] = np.full(self.N, 1.0 - float(_ss(0.45, 1.0, l)), np.float32)
        P["assist"] = np.full(self.N, 1.0 - float(_ss(0.25, 0.7, l)), np.float32)
        P["emit"] = np.full(self.N, 1.0 + 1.5 * float(np.sin(np.pi * _ss(0.0, 0.35, l))), np.float32)

    def _lea_unravel(self, P, l, t, cam, F, tg):
        """The word unravels: the end of the writing is pulled away as a thread (to= where it is pulled to)
        and everything written before it runs after it, along the writing, until nothing is left."""
        o, r, u, nrm = F
        s = self.s
        w = self.W
        q = self.worder
        run = 1.35 * float(l) ** 1.4                         # how far the thread has been pulled (the writing is 1 long)
        sq = q + run
        on_word = sq < 1.0
        cx = np.interp(np.minimum(sq, 1.0), self.pen_q, self.pen_x)
        cy = np.interp(np.minimum(sq, 1.0), self.pen_q, self.pen_y)
        ox = self.xl - np.interp(q, self.pen_q, self.pen_x)  # each point's place beside the thread's line
        oy = self.yl - np.interp(q, self.pen_q, self.pen_y)
        thin = 1.0 - 0.85 * float(_ss(0.0, 0.10, run))        # the letters draw together into the thread
        pos = self._local(F, t, cx + ox * thin, cy + oy * thin)
        end = self._local(F, t, np.array([self.pen_x[-1]]), np.array([self.pen_y[-1]]))[0]
        goal = self._point(self.to, t, cam, end.astype(np.float64) + r * (0.7 * w) + u * (0.35 * w)).astype(np.float32)
        beyond = np.clip((sq - 1.0) / 0.35, 0.0, 1.0)
        off = (~on_word)
        if off.any():
            bz = beyond[off][:, None]
            jit = self._world(F, ox[off] * 0.15, oy[off] * 0.15, 0 * ox[off])
            pos[off] = end[None, :] + (goal[None, :] - end[None, :]) * bz + jit * (1.0 - bz)
        P["pos"] = pos.astype(np.float32)
        P["alpha"] = ((1.0 - _ss(0.75, 1.0, beyond)) * (0.45 + 0.55 * thin)).astype(np.float32)
        P["assist"] = np.full(self.N, 1.0 - float(_ss(0.0, 0.08, run)), np.float32)
        tip = self._local(F, t, np.array([self.pen_x[-1]]), np.array([self.pen_y[-1]]))[0]
        k = float(_ss(0.0, 0.05, l) * (1.0 - _ss(0.85, 1.0, l)))
        if k > 0.01:
            lead = tip + (goal - tip) * float(np.clip(run / 0.35, 0.0, 1.0))
            P["extra"].append(dict(pos=lead[None, :], size=0.012 * w, color=lin(WARM), alpha=k, emit=4.0,
                                   kind="spark", twinkle=0.3))

    def _lea_fade(self, P, l, t, cam, F, tg):
        """The words drift back and go soft."""
        s = self.s
        P["pos"] = (tg - F[3].astype(np.float32)[None, :] * (0.25 * self.W * l * (0.5 + s[:, 1]))[:, None]).astype(np.float32)
        P["alpha"] = (1.0 - _ss(0.2 + 0.4 * s[:, 0], 1.0, l)).astype(np.float32)
        P["assist"] = np.full(self.N, 1.0 - float(_ss(0.0, 0.3, l)), np.float32)

    _lea_morph = _lea_fade


class _Lights:
    """What a masked word draws beside its letters (the Word keeps it from its own sample of the same t)."""
    wants_camera = True

    def __init__(self, word):
        self.word = word

    def sample(self, t, cam=None):
        w = self.word
        if w._kept is None or w._kept[0] != t:
            w.sample(t, cam)
        return w._kept[1] if w._kept is not None and w._kept[0] == t else []


# ------------------------------------------------------------------------------------------- a set of words
class Words:
    """The words of a song: a list of Word settings (dicts) or Words. `source` and `to` may name another word
    of the set (its `name`, by default its label). add_to(scene) puts each word into the 3D scene."""

    def __init__(self, specs, camera=None, **common):
        self.words = []
        self.camera = camera
        for s in specs:
            self.words.append(s if isinstance(s, Word) else Word(**dict(common, **s)))
        for w in self.words:
            if w.camera is None:
                w.camera = camera
            w._others = [o for o in self.words if o is not w]
        by = {w.name: w for w in self.words}
        for w in self.words:
            if isinstance(w.source, str):
                w.source = by[w.source]
            if isinstance(w.to, str):
                w.to = by[w.to]
            if w.arrive == "morph" and isinstance(w.source, Word) and w.source.leave == "morph" \
                    and w.source.to is None:
                w.source.to = w

    def __iter__(self):
        return iter(self.words)

    def __len__(self):
        return len(self.words)

    def __getitem__(self, name):
        for w in self.words:
            if w.name == name:
                return w
        raise KeyError(name)

    def add_to(self, scene, reflect=True, prefix="word "):
        for w in self.words:
            scene.add(prefix + w.name, w, reflect=reflect and w.reflect, depth_of_field=True, mask=w.mask())
            if w.masked:
                scene.add(prefix + w.name + " light", w.lights, reflect=reflect and w.reflect)
        return self

    def reading(self, t):
        """The words whose reading moment holds t."""
        return [w for w in self.words if w.t_read0 <= t <= w.t_read1]

    def focus(self, t, eye, default=None, ease=0.8):
        """A focus distance for the camera that pulls to the word being read (eases in and out over `ease`
        seconds round each reading moment). eye: the camera position at t. default: the distance otherwise."""
        best, wgt = None, 0.0
        for w in self.words:
            k = float(_ss(w.t_read0 - ease, w.t_read0, t) * (1.0 - _ss(w.t_read1, w.t_read1 + ease, t)))
            if k > wgt:
                best, wgt = float(np.linalg.norm(w.centre(t) - np.asarray(eye, np.float64))), k
        if best is None:
            return default
        if default is None:
            return best
        return float(default + (best - default) * wgt)

    def focus_point(self, t, default=(0.0, 6.0, 0.0), ease=0.8):
        """A world point for the camera to focus on: the word being read, easing from and back to `default`
        (a point or a function of t). Give it to a camera move as focus=lambda t: WORDS.focus_point(t, ...)."""
        d = np.asarray(default(t) if callable(default) else default, np.float64)
        acc, wsum, top = np.zeros(3), 0.0, 0.0
        for w in self.words:
            end = w.to.t_in if (w.leave == "morph" and isinstance(w.to, Word)) else w.t_read1
            k = float(_ss(w.t_read0 - ease, w.t_read0, t) * (1.0 - _ss(end, end + ease, t)))
            if k > 0.0:
                acc += k * w.centre(t)
                wsum += k
                top = max(top, k)
        if wsum <= 0.0:
            return d
        return d + (acc / wsum - d) * top

    def world(self, world=None):
        """The song's P3D world settings with the light that belongs to the words added: a real shaft of
        light for every word that arrives by `shaft` (up to four) and the world's light with rays behind the
        word that arrives by `rays` (one). Give the result as P3D["world"]."""
        out = dict(world or {})
        shafts = list(out.get("shafts") or [])
        for w in self.words:
            if w.arrive == "shaft" and len(shafts) < 4:
                shafts.append(w.shaft())
            if w.arrive == "rays" and not out.get("light"):
                out["light"] = w.light()
        if shafts:
            out["shafts"] = shafts
        return out

    def clear(self, points, t, cam=None, **kw):
        """How much of each world point may show so that the words being read stay clear (see `clear`)."""
        k = clear(points, t, self.words, cam if cam is not None else _cam_at(self.camera, t), **kw)
        return np.ones(len(np.asarray(points).reshape(-1, 3)), np.float32) if k is None else k

    def keep_clear(self, t, cam=None, pad=0.8):
        """The boxes to keep clear at t: a list of (word, strength 0..1, corners (4, 3), normal)."""
        cam = cam if cam is not None else _cam_at(self.camera, t)
        out = []
        for w in self.words:
            k, box, nrm = w.keep_clear(t, cam, pad)
            if k > 0.0:
                out.append((w, k, box, nrm))
        return out

    def check(self, camera=None, **kw):
        return check(self, camera if camera is not None else self.camera, **kw)


def place(camera, t, x, y, depth):
    """The world point seen at the screen place (x, y) (0..1 from the left and from the bottom) `depth` metres
    in front of the camera at time t. For laying words out by where they should be read on screen."""
    cam = _cam_at(camera, t)
    r, u, f = cam.basis()
    half = np.tan(np.radians(cam.fov) * 0.5) * depth
    return (np.asarray(cam.pos, np.float64) + f * depth + r * ((x - 0.5) * 2.0 * half * cam.aspect)
            + u * ((y - 0.5) * 2.0 * half))


def em_for(camera, t, depth, px):
    """Metres per em so that an em is `px` pixels of a 1080p picture at `depth` metres from the camera at t
    (80 px is easy to read on a phone)."""
    cam = _cam_at(camera, t)
    return float(px) * 2.0 * np.tan(np.radians(cam.fov) * 0.5) * depth / 1080.0


def clear(points, t, words, cam=None, pad=0.8, floor=0.12, soft=1.1):
    """How much of each point may show so that the words being read stay clear: 1 everywhere except in front
    of and behind a reading word's box on screen, where it falls to `floor`. points: (N, 3) in the world.
    Returns (N,) factors, or None when no word is being read at t. Without a camera the box is taken along
    the word's own normal. pad and soft: the box's margin and its soft border, in em of the word."""
    pts = None
    out = None
    for w in words:
        k, box, nrm = w.keep_clear(t, cam, pad)
        if k <= 0.0:
            continue
        if pts is None:
            pts = np.asarray(points, np.float32).reshape(-1, 3)
            out = np.ones(len(pts), np.float32)
            if cam is not None:
                r_, u_, f_ = cam.basis()
                dp = pts - np.asarray(cam.pos, np.float32)
                zc = np.maximum(dp @ f_.astype(np.float32), 1e-3)
                fl = 1.0 / np.tan(np.radians(cam.fov) * 0.5)
                sx, sy = (dp @ r_.astype(np.float32)) * fl / zc, (dp @ u_.astype(np.float32)) * fl / zc
        em = w.metres_per_em()
        if cam is not None:
            bd = box - np.asarray(cam.pos, np.float64)
            bz = np.maximum(bd @ f_, 1e-3)
            bx, by = (bd @ r_) * fl / bz, (bd @ u_) * fl / bz
            sm = soft * em * fl / float(bz.mean())
            inx = np.clip(np.minimum(sx - bx.min(), bx.max() - sx) / max(sm, 1e-6), 0.0, 1.0)
            iny = np.clip(np.minimum(sy - by.min(), by.max() - sy) / max(sm, 1e-6), 0.0, 1.0)
            inside = inx * iny * (zc > 0.01)
        else:
            o = box.mean(axis=0)
            ex, ey = box[1] - box[0], box[3] - box[0]
            hx, hy = 0.5 * np.linalg.norm(ex), 0.5 * np.linalg.norm(ey)
            d = pts - o.astype(np.float32)
            px_, py_ = d @ (ex / (2 * hx)).astype(np.float32), d @ (ey / (2 * hy)).astype(np.float32)
            sm = soft * em
            inside = np.clip((hx - np.abs(px_)) / sm, 0.0, 1.0) * np.clip((hy - np.abs(py_)) / sm, 0.0, 1.0)
        out *= 1.0 - (1.0 - floor) * k * inside.astype(np.float32)
    return out


class KeepClear:
    """Wraps any point set so that its points dim where a word is being read: scene.add("petals",
    PW.KeepClear(petals, WORDS)). floor: how much light is left inside a reading word's box."""
    wants_camera = True

    def __init__(self, pointset, words, floor=0.12, pad=0.8):
        self.inner, self.words, self.floor, self.pad = pointset, words, float(floor), float(pad)
        if hasattr(pointset, "gain"):
            self.gain = pointset.gain

    def sample(self, t, cam=None):
        ps = self.inner
        res = ps.sample(t, cam) if getattr(ps, "wants_camera", False) else ps.sample(t)
        if res is None:
            return res
        batches = res if isinstance(res, (list, tuple)) else [res]
        out = []
        for b in batches:
            if b is None:
                continue
            k = clear(b["pos"], t, self.words, cam, pad=self.pad, floor=self.floor)
            if k is not None:
                b = dict(b)
                b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float32) * k
                if b.get("pos2") is not None:
                    b["alpha2"] = np.asarray(b.get("alpha2", b["alpha"]), np.float32) * clear(
                        b["pos2"], t, self.words, cam, pad=self.pad, floor=self.floor)
            out.append(b)
        return out


def _cam_at(camera, t):
    if camera is None:
        return None
    if isinstance(camera, CameraState):
        return camera
    for name in ("at", "state", "sample"):
        f = getattr(camera, name, None)
        if callable(f):
            return f(t)
    return camera(t)


def screen_box(word, cam, t):
    """(x0, x1, y0, y1) of a word on screen (0..1, y up), whether it is in front of the camera, the height of
    one em in 1080p pixels, and how squarely it faces the camera (1: flat on)."""
    xy, z = cam.project(word.corners(t, cam))
    o, r, u, nrm = word.frame(t, cam)
    k = word.metres_per_em()
    pe, _ = cam.project(np.array([o, o + u * k]))
    em_px = float(np.linalg.norm((pe[1] - pe[0]) * np.array([1080.0 * cam.aspect, 1080.0])))
    view = _unit(np.asarray(cam.pos, np.float64) - o)
    return (float(xy[:, 0].min()), float(xy[:, 0].max()), float(xy[:, 1].min()), float(xy[:, 1].max()),
            bool(z.min() > 0.0), em_px, float(abs(view @ nrm)))


def check(words, camera=None, min_read=2.5, need_all=True, min_x_mm=0.9, min_cap_mm=0.55, margin=0.02,
          step=0.25, calm=None, raise_on_error=False, quiet=False):
    """Checks the timing of a set of words. Returns (problems, notes): lists of sentences.

    Always: the four times are in order, every word is read for at least `min_read` seconds, all nine
    expressions are there (need_all), a morph starts when its source's reading ends.
    With camera (a function of t, or an object with at(t), giving a CameraState): during every reading moment
    the word is inside the picture, faces the camera, and is large enough to read on a phone (x-height at
    least `min_x_mm` of a 6 cm wide frame; the label's capitals at least `min_cap_mm`); and two words that
    are read at the same time never cover each other on screen (their boxes, grown by `margin`, stay apart).
    calm: a height (0..1 from the bottom) below which no reading word may sit (the calm lower third), or None.
    """
    ws = list(words)
    problems, notes = [], []
    for w in ws:
        if not (w.t_in < w.t_read0 <= w.t_read1 <= w.t_out):
            problems.append(f"{w.name}: the times must be in order (t_in {w.t_in:g} < t_read0 {w.t_read0:g} <= "
                            f"t_read1 {w.t_read1:g} <= t_out {w.t_out:g})")
        end = w.to.t_in if (w.leave == "morph" and isinstance(w.to, Word)) else w.t_read1
        read = end - w.t_read0
        if read < min_read - 1e-6:
            problems.append(f"{w.name}: read for {read:.2f} s, less than {min_read:g} s")
        notes.append(f"{w.name}: arrives {w.t_in:g} ({w.arrive}), read {w.t_read0:g} to {end:g} ({read:.2f} s), "
                     f"gone {w.t_out:g} ({w.leave})")
        if w.arrive == "morph" and isinstance(w.source, Word) and abs(w.t_in - w.source.t_read1) > 1e-3 \
                and w.source.leave == "morph":
            notes.append(f"{w.name}: its source {w.source.name} is held until {w.t_in:g}, when the morph starts")
    if need_all:
        missing = [l for l in LABELS if l not in [w.label for w in ws]]
        if missing:
            problems.append("expressions missing: " + ", ".join(missing))
    pairs = []
    for i, a in enumerate(ws):
        for b in ws[i + 1:]:
            t0, t1 = max(a.t_read0, b.t_read0), min(a.t_read1, b.t_read1)
            if t1 > t0:
                pairs.append((a, b, t0, t1))
    if camera is None:
        for a, b, t0, t1 in pairs:
            notes.append(f"{a.name} and {b.name} are both read from {t0:g} to {t1:g}: give a camera to check "
                         f"that they do not cover each other")
    else:
        for w in ws:
            worst_em, worst_face, bad = 1e9, 1.0, None
            for t in np.arange(w.t_read0, w.t_read1 + 1e-6, step):
                cam = _cam_at(camera, float(t))
                x0, x1, y0, y1, front, em_px, facing = screen_box(w, cam, float(t))
                worst_em, worst_face = min(worst_em, em_px), min(worst_face, facing)
                if not front or x0 < margin or x1 > 1.0 - margin or y0 < margin or y1 > 1.0 - margin:
                    bad = bad or f"{w.name}: not wholly inside the picture at {t:.2f} s " \
                                 f"(x {x0:.2f} to {x1:.2f}, y {y0:.2f} to {y1:.2f})"
                if calm is not None and y0 < calm:
                    bad = bad or f"{w.name}: reaches into the calm lower part at {t:.2f} s (y {y0:.2f})"
            if bad:
                problems.append(bad)
            x_mm = worst_em * X_HEIGHT / PHONE_PX_PER_MM
            cap_mm = worst_em * w.label_size * CAP_HEIGHT / PHONE_PX_PER_MM
            notes.append(f"{w.name}: smallest while read: x-height {x_mm:.2f} mm on a 6 cm wide phone "
                         f"({worst_em * X_HEIGHT:.0f} px at 1080p), label capitals {cap_mm:.2f} mm, facing "
                         f"{worst_face:.2f}")
            if x_mm < min_x_mm:
                problems.append(f"{w.name}: too small to read on a phone (x-height {x_mm:.2f} mm, need {min_x_mm:g})")
            if w.label and cap_mm < min_cap_mm:
                problems.append(f"{w.name}: its label is too small on a phone (capitals {cap_mm:.2f} mm, need "
                                f"{min_cap_mm:g})")
            if worst_face < 0.72:
                problems.append(f"{w.name}: seen too much from the side while read (facing {worst_face:.2f})")
        for a, b, t0, t1 in pairs:
            hit = None
            for t in np.arange(t0, t1 + 1e-6, step):
                cam = _cam_at(camera, float(t))
                ax0, ax1, ay0, ay1 = screen_box(a, cam, float(t))[:4]
                bx0, bx1, by0, by1 = screen_box(b, cam, float(t))[:4]
                if ax0 - margin < bx1 and bx0 - margin < ax1 and ay0 - margin < by1 and by0 - margin < ay1:
                    hit = float(t)
                    break
            if hit is not None:
                problems.append(f"{a.name} and {b.name} cover each other on screen at {hit:.2f} s while both are read")
            else:
                notes.append(f"{a.name} and {b.name} are read together from {t0:g} to {t1:g} and stay apart")
    if not quiet:
        for s in notes:
            print("words:", s)
        for s in problems:
            print("words: PROBLEM:", s)
    if problems and raise_on_error:
        raise ValueError("particle words: " + "; ".join(problems))
    return problems, notes


if __name__ == "__main__":
    # a quick self check without graphics: python -m p3d.words (from engine/)
    ws = Words([dict(expr=i + 1, pos=(0.0, 3.0, -2.0), width=7.0, t_in=4.0 * i, t_read0=4.0 * i + 2.0,
                     t_read1=4.0 * i + 4.6, t_out=4.0 * i + 6.5) for i in range(9)])
    cam = CameraState(pos=np.array([0.0, 2.6, 9.0]), target=np.array([0.0, 3.0, -2.0]), fov=42.0, focus=11.0,
                      aperture=0.03)
    check(ws, lambda t: cam)
    for w in ws:
        for tt in (w.t_in + 1.0, w.t_read0 + 1.0, w.t_read1 + 1.0):
            res = w.sample(tt, cam)
            print(w.name, w.state(tt), [(b["kind"], len(b["pos"])) for b in res])
    print("ok")
