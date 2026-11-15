"""The nine expression symbols drawn in light, and six ways to set one in the world as a quiet effect
(engine/p3d; pure numpy). How a song uses it: engine/UPGRADE-HOWTO.md, section Z.

Each symbol is redrawn by hand as clean strokes (no picture is traced): a list of polylines in symbol units,
1.0 high, centred, y up, in the order a pen draws them. The website's icons were only looked at for what each
shows: a waving hand, a bowing person, a face with a tear, a hugging face, a person gesturing "after you", a
hand cupped at the ear, praying hands, two open hands holding a heart, clapping hands with confetti.

  SYMBOLS                 the nine names (the expressions' labels)
  strokes(name)           the strokes: list of (n, 2) arrays
  symbol_points(name, n)  n points spread evenly along the strokes, with `order` (0..1 along the drawing),
                          `stroke` (which stroke) and `tangent`
  symbol_image(name, h)   a crisp 2D picture of the line art (PIL RGBA), for checking or a title of your own

  The recipes (point sets; every one takes the keys below):
    Traced(name, ...)        fireflies or sparks fly in and trace the symbol over 1 to 2 s, it glows, it fades
    Constellation(name, ...) stars come out among the stars and are joined by fine lines, then go
    PetalShape(name, ...)    petals (or any particles) blow in on the wind, settle into the shape, blow on
    LightTrail(name, ...)    one light draws the whole symbol as a continuous ribbon, which then fades
    Ripples(name, ...)       the symbol lies on the water as lines of light that waver with a spreading ripple
                             and break into glints (no rings: rings read as UI)
    Flock(name, ...)         a cluster of birds or embers passes through and makes the shape as it goes

  Shared keys:
    pos, size, facing, face, tilt, roll, ride, frac, keys   where it stands (see brand.Place; size is the
                             symbol's height in metres); camera: the song's Rig for face="camera"/"screen"/ride
    color                    the expression's colour by default (the website colours, brand.EXPRESSION_COLORS)
    t0                       when it starts; dur: how long the forming takes (1 to 2 s); hold: seconds it stays
                             whole; out: seconds it takes to go
    intensity                0..1, default 0.35: subtle, part of the scenery. 1.0 is a feature.
    paint                    0..1 for a bright day sky (the lines painted in their colour)
"""
import math

import numpy as np

from . import brand as B
from .api import lin

Image, ImageDraw = B.Image, B.ImageDraw       # PIL, loaded on first use

TAU = 2.0 * math.pi
SYMBOLS = list(B.LABELS)


# ------------------------------------------------------------------------------------------- drawing kit
def _bez(p0, p1, p2, p3, n=24):
    u = np.linspace(0.0, 1.0, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, np.float64) for p in (p0, p1, p2, p3))
    return ((1 - u) ** 3) * p0 + 3 * ((1 - u) ** 2) * u * p1 + 3 * (1 - u) * u * u * p2 + (u ** 3) * p3


def _arc(c, r, a0, a1, n=None, ry=None):
    """An arc of a circle (or ellipse with ry) from angle a0 to a1 (degrees, counter clockwise)."""
    ry = r if ry is None else ry
    n = n or max(int(abs(a1 - a0) / 6) + 2, 4)
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([c[0] + r * np.cos(a), c[1] + ry * np.sin(a)], axis=1)


def _line(a, b, n=8):
    u = np.linspace(0.0, 1.0, n)[:, None]
    return np.asarray(a, np.float64) * (1 - u) + np.asarray(b, np.float64) * u


def _join(*parts):
    out = [np.asarray(parts[0], np.float64)]
    for p in parts[1:]:
        p = np.asarray(p, np.float64)
        out.append(p[1:] if np.allclose(out[-1][-1], p[0], atol=1e-6) else p)
    return np.vstack(out)


def _rot(p, deg, c=(0.0, 0.0)):
    a = math.radians(deg)
    m = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return (np.asarray(p, np.float64) - c) @ m.T + c


def _finger(base, ang, length, width, n=10):
    """A finger as an open path: up the left side, round the tip, down the right side (base at the knuckle
    line, pointing at `ang` degrees from straight up, clockwise positive)."""
    a = math.radians(ang)
    d = np.array([math.sin(a), math.cos(a)])
    s = np.array([math.cos(a), -math.sin(a)])
    b = np.asarray(base, np.float64)
    h = 0.5 * width
    tipc = b + d * (length - h)
    left = _line(b - s * h, tipc - s * h, n)
    tip = np.array([tipc + h * (math.cos(t) * -s + math.sin(t) * d) for t in np.linspace(0, math.pi, 9)])
    right = _line(tipc + s * h, b + s * h, n)
    return _join(left, tip, right)


def _heart(c, h, n=48):
    p = B.heart_shape(n * 2)
    return np.asarray(c) + p * h


def _drop(c, h, n=28):
    """A tear drop, point up."""
    t = np.linspace(0, TAU, n)
    x = 0.5 * h * np.sin(t) * np.sin(0.5 * t) ** 1.0 * 1.15
    y = -0.5 * h * np.cos(t) * 0.95
    return np.stack([c[0] + x, c[1] + y], axis=1)


def _norm(strokes):
    """Scale and centre the strokes to 1.0 high (y up), keeping their order."""
    allp = np.vstack(strokes)
    lo, hi = allp.min(axis=0), allp.max(axis=0)
    c = 0.5 * (lo + hi)
    k = 1.0 / max(hi[1] - lo[1], 1e-9)
    return [(np.asarray(s) - c) * k for s in strokes]


# ------------------------------------------------------------------------------------------ the nine
def _greeting():
    # a right hand, palm to us, raised and tilted as it waves; two short arcs of the wave at the top right
    f1 = _finger((-0.165, 0.10), -8, 0.36, 0.105)
    f2 = _finger((-0.055, 0.12), -2, 0.42, 0.105)
    f3 = _finger((0.055, 0.11), 5, 0.39, 0.105)
    f4 = _finger((0.155, 0.07), 14, 0.30, 0.095)
    thumb = _join(_bez((-0.215, -0.20), (-0.30, -0.12), (-0.40, 0.00), (-0.385, 0.075), 12),
                  _arc((-0.335, 0.065), 0.052, 170, 10, 6),
                  _bez((-0.284, 0.06), (-0.27, 0.02), (-0.24, 0.0), (-0.218, 0.04), 8))
    palm_r = _bez((0.20, 0.05), (0.26, -0.05), (0.24, -0.25), (0.15, -0.40), 14)
    wrist = _bez((-0.215, -0.20), (-0.22, -0.30), (-0.17, -0.38), (-0.12, -0.42), 8)
    hand = _join(wrist[::-1], thumb, _line((-0.218, 0.04), (-0.218, 0.10), 3), f1, f2, f3, f4, palm_r)
    hand = _rot(hand, -16, (0.0, 0.0))
    w1 = _arc((0.27, 0.36), 0.14, -5, 70)
    w2 = _arc((0.27, 0.36), 0.23, 0, 62)
    return [hand, w1, w2]


def _gratitude():
    # someone bowing deeply, seen from the side: the head lowered in front, the back level, the arm hanging,
    # standing straight; one hand laid on the heart
    head = _arc((-0.355, -0.01), 0.11, 0, 360, 30)
    body = _join(_bez((-0.25, 0.04), (-0.18, 0.14), (-0.02, 0.19), (0.12, 0.18), 14),       # neck and back
                 _bez((0.12, 0.18), (0.24, 0.17), (0.31, 0.11), (0.30, 0.00), 10),          # the hips
                 _bez((0.30, 0.00), (0.29, -0.14), (0.27, -0.26), (0.27, -0.36), 8),         # back of the legs
                 _line((0.27, -0.36), (0.26, -0.50), 4),
                 _bez((0.26, -0.50), (0.21, -0.52), (0.14, -0.52), (0.11, -0.50), 6),        # the feet
                 _bez((0.11, -0.50), (0.12, -0.36), (0.14, -0.22), (0.14, -0.08), 8),         # front of the legs
                 _bez((0.14, -0.08), (0.04, -0.06), (-0.10, -0.07), (-0.24, -0.08), 12))     # chest under the bow
    arm = _join(_bez((-0.10, -0.07), (-0.10, -0.15), (-0.08, -0.24), (-0.06, -0.30), 8),
                _arc((-0.05, -0.33), 0.03, 150, -60, 6))
    return [head, body, arm]


def _apology():
    face = _arc((0.0, 0.0), 0.48, 90, 450, 64)
    eye_l = _arc((-0.16, 0.10), 0.05, 0, 360, 14)
    eye_r = _arc((0.16, 0.10), 0.05, 0, 360, 14)
    mouth = _bez((-0.11, -0.22), (-0.04, -0.17), (0.04, -0.17), (0.11, -0.22), 10)
    brow_l = _bez((-0.25, 0.20), (-0.21, 0.22), (-0.15, 0.24), (-0.10, 0.27), 8)       # raised inner ends: sorry
    brow_r = brow_l * np.array([-1.0, 1.0])
    tear = _drop((-0.20, -0.08), 0.15)
    return [face, eye_l, eye_r, brow_l, brow_r, mouth, tear]


def _open_hand(c, flip=1.0, scale=1.0, ang=0.0):
    """A small open hand with four fingers and a thumb, palm to us (for the hugging face)."""
    fs = [_finger((-0.09, 0.05), -12, 0.15, 0.055), _finger((-0.03, 0.07), -4, 0.18, 0.055),
          _finger((0.03, 0.07), 4, 0.17, 0.055), _finger((0.09, 0.05), 12, 0.14, 0.05)]
    thumb = _bez((-0.115, 0.02), (-0.18, 0.0), (-0.22, -0.06), (-0.17, -0.09), 8)
    base = _bez((0.115, 0.03), (0.13, -0.08), (0.07, -0.14), (0.0, -0.14), 8)
    p = _join(thumb[::-1], fs[0], fs[1], fs[2], fs[3], base)
    p = p * np.array([flip, 1.0]) * scale
    return _rot(p, ang) + np.asarray(c)


def _inclusiveness():
    face = _arc((0.0, 0.06), 0.42, 90, 450, 60)
    eye_l = _arc((-0.15, 0.13), 0.075, 20, 160, 10)          # closed, smiling eyes
    eye_r = _arc((0.15, 0.13), 0.075, 20, 160, 10)
    smile = _arc((0.0, -0.02), 0.17, 200, 340, 14)
    hand_l = _open_hand((-0.30, -0.30), 1.0, 1.15, 18)
    hand_r = _open_hand((0.30, -0.30), -1.0, 1.15, -18)
    return [face, eye_l, eye_r, smile, hand_l, hand_r]


def _concession():
    # a person, half figure, the head turned a little, one arm held out low to the side, palm up: "after you"
    head = _arc((-0.20, 0.25), 0.15, 0, 360, 30)
    hair = _bez((-0.35, 0.29), (-0.33, 0.43), (-0.12, 0.47), (-0.06, 0.32), 10)
    body = _join(_bez((-0.50, -0.42), (-0.50, -0.15), (-0.42, 0.02), (-0.28, 0.05), 12),
                 _bez((-0.28, 0.05), (-0.20, 0.06), (-0.12, 0.05), (-0.07, 0.00), 8),
                 _bez((-0.07, 0.00), (0.06, -0.10), (0.18, -0.08), (0.30, 0.02), 12))       # shoulder and arm out
    under = _bez((0.30, -0.08), (0.16, -0.20), (0.02, -0.22), (-0.06, -0.20), 12)            # underside of the arm
    hand = _join(_bez((0.30, 0.02), (0.33, 0.07), (0.36, 0.12), (0.37, 0.16), 6),            # the thumb, up
                 _arc((0.385, 0.155), 0.018, 160, -20, 5),
                 _bez((0.40, 0.15), (0.40, 0.10), (0.40, 0.07), (0.41, 0.05), 5),
                 _bez((0.41, 0.05), (0.46, 0.06), (0.51, 0.06), (0.54, 0.05), 6),             # the open palm, up
                 _arc((0.54, 0.025), 0.026, 90, -90, 6),
                 _bez((0.54, 0.0), (0.46, -0.03), (0.38, -0.06), (0.30, -0.08), 8))
    side = _line((-0.06, -0.20), (-0.04, -0.42), 6)
    return [head, hair, body, hand, under, side]


def _respect():
    # a face turned to us with long hair, one hand raised and cupped behind the ear: listening
    face = _join(_bez((-0.30, 0.10), (-0.32, -0.20), (-0.18, -0.36), (-0.02, -0.36), 14),
                 _bez((-0.02, -0.36), (0.12, -0.36), (0.20, -0.22), (0.20, 0.00), 12))
    hair = _join(_bez((-0.30, 0.10), (-0.36, 0.40), (-0.05, 0.50), (0.12, 0.38), 16),
                 _bez((0.12, 0.38), (0.20, 0.32), (0.22, 0.20), (0.20, 0.10), 8))
    fringe = _bez((-0.28, 0.16), (-0.18, 0.26), (-0.02, 0.26), (0.10, 0.20), 10)
    eye_l = _arc((-0.17, -0.02), 0.035, 0, 360, 10)
    eye_r = _arc((0.04, -0.02), 0.035, 0, 360, 10)
    mouth = _arc((-0.06, -0.18), 0.05, 200, 340, 8)
    ear = _arc((0.22, -0.04), 0.05, -80, 110, 10)
    f = [_finger((0.30, 0.08), 6, 0.20, 0.07), _finger((0.37, 0.09), 12, 0.22, 0.07),
         _finger((0.44, 0.08), 18, 0.20, 0.07), _finger((0.50, 0.05), 26, 0.16, 0.065)]
    hand = _join(_bez((0.26, -0.20), (0.24, -0.08), (0.24, 0.02), (0.265, 0.08), 8), f[0], f[1], f[2], f[3],
                 _bez((0.535, 0.03), (0.55, -0.08), (0.50, -0.20), (0.42, -0.28), 10))
    thumb = _bez((0.265, 0.02), (0.20, 0.04), (0.17, 0.00), (0.21, -0.07), 8)
    return [face, hair, fringe, eye_l, eye_r, mouth, ear, hand, thumb]


def _encouragement():
    # two hands pressed together, fingers up, the line between them, the thumbs, the forearms going down and
    # apart (open lines: no boxes or rings, which read as UI)
    arm_out = _bez((-0.36, -0.50), (-0.30, -0.44), (-0.23, -0.37), (-0.22, -0.28), 8)
    left = _join(arm_out,
                 _line((-0.22, -0.28), (-0.22, -0.02), 6),
                 _bez((-0.22, -0.02), (-0.22, 0.20), (-0.12, 0.38), (-0.05, 0.47), 14),
                 _arc((-0.022, 0.462), 0.03, 160, 0, 6))
    right = left[::-1] * np.array([-1.0, 1.0])
    arm_in = _bez((0.0, -0.24), (-0.02, -0.33), (-0.08, -0.43), (-0.15, -0.50), 8)
    mid = _join(_line((0.0, 0.43), (0.0, -0.24), 10), arm_in)
    arm_in_r = arm_in * np.array([-1.0, 1.0])
    thumb_l = _join(_bez((-0.22, -0.06), (-0.14, -0.02), (-0.09, 0.06), (-0.07, 0.16), 8),
                    _arc((-0.045, 0.16), 0.025, 180, 0, 5))
    thumb_r = thumb_l[::-1] * np.array([-1.0, 1.0])
    return [left, right, mid, arm_in_r, thumb_l, thumb_r]


def _cupped(c, flip=1.0):
    """An open hand, palm up and tilted in, fingers up at the side (one of two that hold a heart)."""
    f = [_finger((-0.16, 0.02), -20, 0.20, 0.06), _finger((-0.10, 0.05), -10, 0.23, 0.06),
         _finger((-0.04, 0.06), -2, 0.22, 0.06), _finger((0.02, 0.05), 6, 0.18, 0.058)]
    palm = _join(_bez((-0.19, -0.02), (-0.24, -0.20), (-0.10, -0.32), (0.02, -0.30), 10),
                 _bez((0.02, -0.30), (0.10, -0.28), (0.12, -0.16), (0.09, -0.05), 8))
    thumb = _bez((0.09, -0.05), (0.14, 0.02), (0.18, 0.10), (0.16, 0.14), 8)
    p = _join(palm[::-1][::-1], thumb)
    hand = _join(f[3][::-1], f[2][::-1], f[1][::-1], f[0][::-1], _bez((-0.19, -0.02), (-0.19, -0.01), (-0.19, 0.0),
                                                                      (-0.19, 0.0), 2))
    out = [hand, p]
    return [np.asarray(c) + q * np.array([flip, 1.0]) for q in out]


def _consideration():
    heart = _heart((0.0, 0.24), 0.36)
    hl = _cupped((-0.20, -0.16), 1.0)
    hr = _cupped((0.20, -0.16), -1.0)
    return [heart] + hl + hr


def _compliment():
    # two hands meeting in a clap (one behind the other, at an angle), short lines of the clap, confetti
    back = _rot(_join(_finger((-0.10, 0.05), -6, 0.34, 0.09), _finger((-0.01, 0.06), 2, 0.37, 0.09),
                      _finger((0.08, 0.05), 10, 0.33, 0.085), _bez((0.125, 0.03), (0.17, -0.10), (0.12, -0.30),
                                                                  (0.02, -0.40), 10)), 28)
    front = _rot(_join(_bez((-0.16, -0.40), (-0.22, -0.20), (-0.20, -0.05), (-0.145, 0.02), 10),
                       _finger((-0.10, 0.02), -4, 0.31, 0.09), _finger((-0.01, 0.03), 3, 0.33, 0.09),
                       _finger((0.08, 0.02), 9, 0.29, 0.085), _bez((0.125, 0.0), (0.16, -0.12), (0.10, -0.30),
                                                                   (0.0, -0.42), 10)), 42, (0.0, -0.1)) + [-0.10, -0.04]
    thumb = _rot(_bez((-0.15, -0.10), (-0.26, -0.06), (-0.30, 0.04), (-0.24, 0.10), 8), 42, (0.0, -0.1)) + [-0.1, -0.04]
    clap1 = _line((0.30, 0.34), (0.38, 0.44), 4)
    clap2 = _line((0.36, 0.24), (0.48, 0.28), 4)
    conf = [_arc((0.46, 0.46), 0.022, 0, 360, 8), _arc((0.54, 0.34), 0.018, 0, 360, 8),
            _arc((-0.40, 0.42), 0.02, 0, 360, 8),
            _join(_line((0.50, 0.12), (0.56, 0.15), 3), _line((0.56, 0.15), (0.54, 0.20), 3),
                  _line((0.54, 0.20), (0.48, 0.17), 3), _line((0.48, 0.17), (0.50, 0.12), 3)),
            _join(_line((-0.46, 0.18), (-0.41, 0.22), 3), _line((-0.41, 0.22), (-0.45, 0.27), 3),
                  _line((-0.45, 0.27), (-0.50, 0.23), 3), _line((-0.50, 0.23), (-0.46, 0.18), 3))]
    return [back, front, thumb, clap1, clap2] + conf


_MAKERS = dict(Greeting=_greeting, Gratitude=_gratitude, Apology=_apology, Inclusiveness=_inclusiveness,
               Concession=_concession, Respect=_respect, Encouragement=_encouragement, Consideration=_consideration,
               Compliment=_compliment)
_CACHE = {}


def _name(name):
    if isinstance(name, int):
        return SYMBOLS[name - 1]
    for s in SYMBOLS:
        if s.lower() == str(name).lower():
            return s
    raise ValueError("no symbol %r; the nine are %s" % (name, ", ".join(SYMBOLS)))


def strokes(name):
    """The strokes of a symbol (list of (n, 2) arrays), 1.0 high, centred, y up, in drawing order."""
    name = _name(name)
    if name not in _CACHE:
        _CACHE[name] = _norm(_MAKERS[name]())
    return _CACHE[name]


def symbol_points(name, n=600, seed=1):
    """n points along the strokes at even spacing: dict(xy (n, 2), order (n,) 0..1 along the drawing,
    stroke (n,), tangent (n, 2), length (total length in symbol units))."""
    st = strokes(name)
    segs, lens = [], []
    for s in st:
        d = np.linalg.norm(np.diff(s, axis=0), axis=1)
        segs.append(np.concatenate([[0.0], np.cumsum(d)]))
        lens.append(float(d.sum()))
    total = sum(lens)
    # a little of each stroke at least, so small details (eyes, confetti) are never lost
    share = np.maximum(np.array(lens) / total, 0.012)
    share = share / share.sum()
    counts = np.maximum((share * n).astype(int), 3)
    xy, order, sid, tg = [], [], [], []
    acc = 0.0
    for i, (s, cum, L, k) in enumerate(zip(st, segs, lens, counts)):
        u = (np.arange(k) + 0.5) / k * L
        x = np.interp(u, cum, s[:, 0])
        y = np.interp(u, cum, s[:, 1])
        dx = np.gradient(x)
        dy = np.gradient(y)
        nn = np.maximum(np.hypot(dx, dy), 1e-9)
        xy.append(np.stack([x, y], axis=1))
        tg.append(np.stack([dx / nn, dy / nn], axis=1))
        order.append((acc + u) / total)
        sid.append(np.full(k, i))
        acc += L
    return dict(xy=np.vstack(xy), order=np.concatenate(order), stroke=np.concatenate(sid), tangent=np.vstack(tg),
                length=total)


def symbol_image(name, height=240, color=None, width=0.035, glow=True, pad=0.12):
    """The line art as a PIL RGBA picture (light lines with a soft glow), `height` pixels for the symbol."""
    from PIL import ImageFilter
    st = strokes(name)
    allp = np.vstack(st)
    w_units = float(np.ptp(allp[:, 0]))
    H = int(height * (1 + 2 * pad))
    W = int(height * (w_units + 2 * pad))
    ss = 4
    img = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(img)
    cx, cy = W * ss / 2.0, H * ss / 2.0
    k = height * ss
    lw = max(int(round(width * k)), 1)
    for s in st:
        pts = [(cx + x * k, cy - y * k) for x, y in s]
        d.line(pts, fill=255, width=lw, joint="curve")
        for (x, y) in (pts[0], pts[-1]):
            d.ellipse((x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2), fill=255)
    a = np.asarray(img.resize((W, H), Image.BOX), np.float32) / 255.0
    col = np.array([int(B.EXPRESSION_COLORS[_name(name)][i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0 \
        if color is None else np.array([int(color[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0
    core = np.clip(col * 0.55 + 0.45, 0, 1)
    rgb = np.broadcast_to(core, a.shape + (3,)).copy()
    alpha = a
    if glow:
        g = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(height * 0.03)),
                       np.float32) / 255.0
        ga = np.clip(g * 1.6, 0, 1) * (1 - a)
        rgb = (rgb * a[..., None] + col * ga[..., None]) / np.maximum((a + ga)[..., None], 1e-6)
        alpha = a + ga
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 1) * 255, np.clip(alpha, 0, 1) * 255]).astype(np.uint8), "RGBA")


# --------------------------------------------------------------------------------------------- recipes
def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / max(b - a, 1e-9), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _deep(c, k=1.3):
    c = np.asarray(c, np.float64)
    m = max(float(c.max()), 1e-6)
    return m * (c / m) ** k


class _SymbolFX:
    """What the six recipes share: the symbol, where it stands, its colour, its times and its strength."""
    wants_camera = True
    FACE = "camera"
    N = 700

    def __init__(self, name, pos=(0.0, 4.0, 0.0), size=2.0, facing=0.0, face=None, tilt=0.0, roll=0.0, ride=None,
                 frac=0.2, keys=None, place=None, camera=None, color=None, t0=0.0, dur=1.6, hold=0.9, out=1.2,
                 intensity=0.35, paint=0.0, n=None, seed=1, dof=1.0, reflect=True):
        self.name = _name(name)
        self.place = place or B.Place(pos=pos, size=size, facing=facing, face=face or self.FACE, tilt=tilt, roll=roll,
                                      ride=ride, frac=frac, keys=keys)
        self.camera = camera
        self.hex = color or B.EXPRESSION_COLORS[self.name]
        self.col = _deep(lin(self.hex))
        self.t0, self.dur, self.hold, self.out = float(t0), float(dur), float(hold), float(out)
        self.k = float(intensity)
        self.paint = paint
        self.dof, self.reflect = dof, reflect
        P = symbol_points(self.name, n or self.N, seed)
        self.xy, self.order, self.sid, self.tg = P["xy"], P["order"], P["stroke"], P["tangent"]
        self.nrm2 = np.stack([-self.tg[:, 1], self.tg[:, 0]], axis=1)
        self.M = len(self.xy)
        self.L = P["length"]
        rng = np.random.default_rng(seed + 31)
        self.s = rng.random((self.M, 6))
        self.lead = 0.8

    # the times
    @property
    def t_full(self):
        return self.t0 + self.dur

    @property
    def t_end(self):
        return self.t0 + self.dur + self.hold + self.out

    def gain(self, t):
        return 1.0 if self.t0 - self.lead - 0.1 <= t <= self.t_end + 0.3 else 0.0

    def _cam(self, t, cam):
        if cam is not None or self.camera is None:
            return cam
        return self.camera.state(t) if hasattr(self.camera, "state") else self.camera(t)

    def _world(self, t, cam, xy, z=None):
        c, r, u, n, s = self.place.frame(t, cam)
        p = c[None, :] + s * (xy[:, 0:1] * r[None, :] + xy[:, 1:2] * u[None, :])
        if z is not None:
            p = p + s * np.asarray(z)[:, None] * n[None, :]
        return p, s

    def _fade_out(self, t):
        return 1.0 - float(_ss(self.t_full + self.hold, self.t_end, t))

    def _paint(self, t):
        return float(np.clip(self.paint(t) if callable(self.paint) else self.paint, 0.0, 1.0))

    def where(self, t, cam=None):
        """The symbol's points in the world at t (where its lines are)."""
        return self._world(t, self._cam(t, cam), self.xy)[0]


class Traced(_SymbolFX):
    """Fireflies (or sparks) fly in and trace the symbol with light over `dur` seconds (1 to 2), the line glows,
    holds, and fades. heads: how many tracers share the drawing (3); style "fireflies" (soft warm lights that
    blink, the lines a little softer) or "sparks" (bright points with a glint, crisper lines)."""

    def __init__(self, name, heads=3, style="fireflies", **kw):
        super().__init__(name, **kw)
        self.H, self.style = max(int(heads), 1), style
        rng = np.random.default_rng(77)
        self.come = (rng.random((self.H, 3)) - 0.5) * np.array([3.0, 2.0, 1.5])
        self.go = (rng.random((self.H, 3)) - 0.5) * np.array([3.0, 2.0, 1.5]) + np.array([0.0, 1.2, 0.0])
        self.part = np.minimum((self.order * self.H).astype(int), self.H - 1)
        self.lit = self.t0 + self.dur * (self.order * self.H - self.part)        # when each point is lit

    def _head_local(self, t):
        """Each tracer's place in symbol units (H, 2) and z, and whether it is drawing."""
        out = []
        for h in range(self.H):
            sel = np.nonzero(self.part == h)[0]
            first, last = self.xy[sel[0]], self.xy[sel[-1]]
            if t < self.t0:
                v = float(_ss(self.t0 - self.lead, self.t0, t))
                p = np.r_[self.come[h, :2] * (1 - v) + first * v]
                z = self.come[h, 2] * (1 - v)
            elif t <= self.t_full:
                u = (t - self.t0) / max(self.dur, 1e-6)
                j = sel[min(int(u * len(sel)), len(sel) - 1)]
                p, z = self.xy[j], 0.0
            else:
                v = float(_ss(self.t_full, self.t_full + 1.2, t))
                p = last * (1 - v) + self.go[h, :2] * v
                z = self.go[h, 2] * v
            out.append((p, z))
        return np.array([o[0] for o in out]), np.array([o[1] for o in out])

    def sample(self, t, cam=None):
        if self.gain(t) <= 0.0:
            return None
        cam = self._cam(t, cam)
        pos, s = self._world(t, cam, self.xy)
        age = t - self.lit
        a = np.clip(age / 0.08, 0.0, 1.0) * (0.75 + 0.25 * np.exp(-np.maximum(age, 0) / 0.4))
        a = a * self._fade_out(t)
        # as it fades the line breaks up: points go one by one
        fo = _ss(self.t_full + self.hold, self.t_end, t)
        a = a * (self.s[:, 0] > fo * 0.9)
        out = []
        vis = a > 0.003
        k = self.k
        soft = self.style == "fireflies"
        if vis.any():
            sz = s * (0.016 if soft else 0.013)
            out.append(dict(pos=pos[vis], size=sz, color=self.col * 1.4, alpha=a[vis] * k * (0.9 if soft else 1.4),
                            kind="soft", seed=self.s[vis, 1], twinkle=0.25 if soft else 0.1, dof=self.dof,
                            reflect=self.reflect, paint=self._paint(t), paint_light=0.5))
            out.append(dict(pos=pos[vis][::4], size=s * 0.06, color=self.col, alpha=a[vis][::4] * k * 0.10,
                            kind="soft", seed=self.s[vis, 2][::4], dof=1.0, reflect=self.reflect, streak=0.0))
        if self.t0 - self.lead <= t <= self.t_full + 1.2:
            hp, hz = self._head_local(t)
            hpos, _ = self._world(t, cam, hp, hz)
            blink = 0.65 + 0.35 * np.sin(t * 9.0 + np.arange(self.H) * 2.1) ** 2 if soft else np.ones(self.H)
            fade = float(_ss(self.t0 - self.lead, self.t0 - self.lead + 0.3, t)) * \
                (1.0 - float(_ss(self.t_full + 0.6, self.t_full + 1.2, t)))
            hc = np.array([1.0, 0.92, 0.65]) if soft else np.array([1.0, 0.96, 0.9])
            out.append(dict(pos=hpos, size=s * (0.035 if soft else 0.03), color=hc * 1.6,
                            alpha=blink * fade * min(k * 2.2, 1.0), emit=2.0, kind="spark", twinkle=0.6,
                            dof=self.dof, reflect=self.reflect))
            out.append(dict(pos=hpos, size=s * 0.16, color=hc * 0.6 + self.col * 0.3,
                            alpha=blink * fade * 0.12 * min(k * 2.2, 1.0), kind="soft", dof=1.0, streak=0.0))
        return out


class Constellation(_SymbolFX):
    """Stars come out one by one among the stars and fine lines join them in the drawing order; it holds,
    the lines go, then the stars. Put it far off in the sky (a big size at a great distance) with face="camera".
    stars: how many (24 by default; small details keep at least one)."""
    FACE = "camera"
    N = 400

    def __init__(self, name, stars=24, **kw):
        kw.setdefault("dof", 0.0)
        super().__init__(name, **kw)
        # the stars: evenly along the drawing, with the ends of every stroke
        m = max(int(stars), 6)
        pick = set(np.linspace(0, self.M - 1, m).astype(int).tolist())
        for sidx in np.unique(self.sid):
            ii = np.nonzero(self.sid == sidx)[0]
            pick.add(int(ii[0]))
            pick.add(int(ii[-1]))
        self.st = np.array(sorted(pick))
        so = self.order[self.st]
        self.lit_star = self.t0 + self.dur * so
        same = self.sid[self.st][1:] == self.sid[self.st][:-1]
        self.links = np.nonzero(same)[0]          # star i joins star i + 1
        self.lit_link = self.t0 + self.dur * so[self.links + 1]
        self.lead = 0.2

    def sample(self, t, cam=None):
        if self.gain(t) <= 0.0:
            return None
        cam = self._cam(t, cam)
        pos, s = self._world(t, cam, self.xy[self.st])
        fo = _ss(self.t_full + self.hold, self.t_end, t)
        fo_lines = _ss(self.t_full + self.hold, self.t_full + self.hold + 0.5 * self.out, t)
        a_st = np.clip((t - self.lit_star) / 0.25, 0.0, 1.0) * (1.0 - fo)
        tw = 0.7 + 0.3 * np.sin(t * (2.0 + 3.0 * self.s[self.st, 0]) + self.s[self.st, 1] * 20.0)
        out = [dict(pos=pos, size=s * 0.022, color=np.array([1.0, 0.97, 0.92]) * 0.6 + self.col * 0.8,
                    alpha=a_st * tw * min(self.k * 2.0, 1.0), emit=1.5, kind="spark", twinkle=0.8, dof=self.dof,
                    fog=0.3, reflect=self.reflect)]
        if len(self.links):
            g = np.clip((t - self.lit_link) / 0.35, 0.0, 1.0)
            a_l = g * (1.0 - fo_lines)
            sel = a_l > 0.003
            if sel.any():
                i = self.links[sel]
                p0, p1 = pos[i], pos[i + 1]
                p1 = p0 + (p1 - p0) * g[sel][:, None]
                out.append(dict(pos=p0, pos2=p1, size=s * 0.004, color=self.col * 1.2, alpha=a_l[sel] * self.k * 1.2,
                                kind="line", dof=self.dof, fog=0.3, reflect=self.reflect))
        return out


class PetalShape(_SymbolFX):
    """Petals (or hearts, or soft lights) blow in on the wind, settle into the symbol for a moment, and blow on.
    wind: direction in the symbol's plane (x, y) they come from and go to (default from the left);
    carrier: "petal", "heart" or "soft"; petal_size: in symbol heights."""
    N = 260

    def __init__(self, name, wind=(1.0, 0.15), carrier="petal", petal_size=0.035, **kw):
        super().__init__(name, **kw)
        w = np.asarray(wind, np.float64)
        self.w = w / max(np.linalg.norm(w), 1e-9)
        self.carrier, self.psize = carrier, float(petal_size)
        self.arrive = self.t0 + self.dur * (0.15 + 0.85 * self.s[:, 0])
        self.leave = self.t_full + self.hold + 0.5 * self.out * self.s[:, 1]
        sp = np.stack([-self.w[1], self.w[0]])
        self.src = self.xy - self.w[None, :] * (1.5 + 1.0 * self.s[:, 2:3]) + sp[None, :] * (self.s[:, 3:4] - 0.5) * 1.2
        self.dst = self.xy + self.w[None, :] * (1.6 + 1.0 * self.s[:, 4:5]) + sp[None, :] * (self.s[:, 5:6] - 0.5) * 1.2
        self.lead = self.dur

    def sample(self, t, cam=None):
        if self.gain(t) <= 0.0:
            return None
        cam = self._cam(t, cam)
        fly_in = 1.1
        u = np.clip((t - (self.arrive - fly_in)) / fly_in, 0.0, 1.0)
        e = 1.0 - (1.0 - u) ** 2
        v = np.clip((t - self.leave) / 1.3, 0.0, 1.0)
        f = v * v
        sway = np.sin(t * 2.0 + self.s[:, 0] * 9.0)[:, None] * 0.03 * (1 - e[:, None] + f[:, None])
        xy = self.src * (1 - e[:, None]) + self.xy * e[:, None]
        xy = xy * (1 - f[:, None]) + self.dst * f[:, None] + sway * np.array([[-self.w[1], self.w[0]]])
        z = (self.s[:, 2] - 0.5) * 0.6 * ((1 - e) + f)
        pos, s = self._world(t, cam, xy, z)
        a = np.clip(u * 3.0, 0, 1) * (1.0 - v) * self.k * 1.6
        sel = a > 0.003
        if not sel.any():
            return None
        settled = e * (1 - f)
        rot = np.stack([self.s[:, 1] * TAU + t * (1.0 + self.s[:, 2]) * (1 - settled) + np.arctan2(self.tg[:, 1],
                        self.tg[:, 0]) * settled, (self.s[:, 3] * TAU + t * 2.5) * (1 - 0.8 * settled)], axis=1)
        paint = self._paint(t)
        col = B.show_rgb(np.array([[int(self.hex[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]]))[0] if paint > 0 \
            else self.col * 1.3
        return [dict(pos=pos[sel], size=s * self.psize, color=col, alpha=np.clip(a[sel], 0, 1), rot=rot[sel],
                     kind=self.carrier, seed=self.s[sel, 0], dof=self.dof, paint=paint, paint_light=0.4,
                     reflect=self.reflect)]


class LightTrail(_SymbolFX):
    """One light draws the whole symbol as a continuous ribbon over `dur`, moving from stroke to stroke; the
    ribbon glows, holds, and fades from where it began. width: the ribbon's width in symbol heights."""
    N = 900

    def __init__(self, name, width=0.016, **kw):
        super().__init__(name, **kw)
        self.width = float(width)
        self.lead = 0.4

    def sample(self, t, cam=None):
        if self.gain(t) <= 0.0:
            return None
        cam = self._cam(t, cam)
        pos, s = self._world(t, cam, self.xy)
        u = (t - self.t0) / max(self.dur, 1e-6)
        fo_start = (t - (self.t_full + self.hold)) / max(self.out, 1e-6)       # the fade runs along the drawing
        out = []
        for sidx in np.unique(self.sid):
            ii = np.nonzero(self.sid == sidx)[0]
            o = self.order[ii]
            drawn = o <= u
            if drawn.sum() < 2:
                continue
            jj = ii[drawn]
            a = np.clip((u - self.order[jj]) * 8.0, 0.25, 1.0) * np.clip(1.0 - (fo_start * 1.3 - self.order[jj]) * 3.0,
                                                                       0.0, 1.0)
            if a.max() <= 0.003:
                continue
            b = dict(pos=pos[jj][:-1], pos2=pos[jj][1:], size=s * self.width, size2=s * self.width,
                     alpha=a[:-1] * self.k * 1.4, alpha2=a[1:] * self.k * 1.4, color=self.col * 1.3,
                     kind="ribbon", dof=self.dof, reflect=self.reflect, paint=self._paint(t), paint_light=0.5)
            out.append(b)
        if -0.2 <= u <= 1.05:
            j = int(np.clip(np.searchsorted(self.order, np.clip(u, 0, 1)), 0, self.M - 1))
            hp = pos[j:j + 1]
            out.append(dict(pos=hp, size=s * 0.04, color=np.array([1.0, 0.95, 0.88]) * 1.5,
                            alpha=min(self.k * 2.5, 1.0), emit=2.5, kind="spark", dof=self.dof))
            out.append(dict(pos=hp, size=s * 0.2, color=self.col, alpha=0.15 * min(self.k * 2.5, 1.0), kind="soft",
                            dof=1.0, streak=0.0))
        return out


class Ripples(_SymbolFX):
    """The symbol lies on the water as thin lines of light, mirrored and moved by the water: it appears from its
    middle outward as if something had touched the lake there, its lines waver with a ripple that travels out
    and calms, and the light breaks into glints along them, as moonlight does on water. Give pos on the lake
    (y about 0.02); it lies flat (face="flat"), read from where the camera looks at the water.
    spread: how strongly the lines waver (0.35). rings: rings of light spreading from the lines (0, none: rings
    read as UI; kept for older songs)."""
    FACE = "flat"
    N = 700

    def __init__(self, name, rings=0, spread=0.35, **kw):
        kw.setdefault("reflect", False)
        super().__init__(name, **kw)
        self.R, self.spread = int(rings), float(spread)
        self.lead = 0.2
        self.rr = np.hypot(self.xy[:, 0], self.xy[:, 1])
        self.rr = self.rr / max(float(self.rr.max()), 1e-6)

    def sample(self, t, cam=None):
        if self.gain(t) <= 0.0:
            return None
        cam = self._cam(t, cam)
        u = (t - self.t0) / max(self.dur, 1e-6)
        draw = np.clip((u * 1.25 - self.rr) * 4.0, 0.0, 1.0)              # from the middle outward
        fo = self._fade_out(t)
        age = max(t - self.t0, 0.0)
        calm = 0.25 + 0.75 * math.exp(-age / max(self.dur * 1.4, 1e-6))
        wob = self.spread * 0.035 * calm * np.sin(self.rr * 26.0 - age * 5.5) \
            + 0.004 * np.sin(t * 3.0 + self.order * 40.0)
        xy = self.xy + self.nrm2 * wob[:, None]
        pos, s = self._world(t, cam, xy)
        glint = 0.55 + 0.45 * np.sin(t * 6.0 + self.s[:, 2] * 40.0 + self.rr * 12.0) ** 2
        out = [dict(pos=pos, size=s * 0.012, color=self.col * 1.3, alpha=draw * fo * self.k * 1.3 * glint,
                    kind="soft", seed=self.s[:, 0], twinkle=0.3, dof=self.dof, reflect=False)]
        gl = (self.s[:, 3] < 0.06) & (draw > 0.5)
        if gl.any():
            out.append(dict(pos=pos[gl], size=s * 0.02, color=self.col * 0.6 + 0.6, alpha=fo * self.k * 0.9 * draw[gl],
                            emit=1.6, kind="spark", twinkle=1.0, seed=self.s[gl, 4], dof=self.dof, reflect=False))
        for r in range(self.R):
            tr = self.t0 + 0.35 * r + self.dur * 0.3
            age = t - tr - self.order * self.dur * 0.6
            d = np.clip(age, 0.0, None) * self.spread / 1.6
            al = np.where(age > 0, np.exp(-age / 1.1), 0.0) * fo * self.k * (0.9 - 0.2 * r)
            if al.max() <= 0.003:
                continue
            for sgn in (1.0, -1.0):
                pp, _ = self._world(t, cam, self.xy + self.nrm2 * (sgn * d)[:, None])
                out.append(dict(pos=pp, size=s * 0.010, color=self.col * 0.9 + 0.15, alpha=al * 0.8, kind="soft",
                                seed=self.s[:, 1], dof=self.dof, reflect=False))
        return out


class Flock(_SymbolFX):
    """A loose cluster of birds (or embers) passes through and, for a moment as it goes, its members stand in
    the symbol's shape: they slow as they pass their places and speed off again. The shape is clearest at
    t0 + dur / 2. carrier: "bird" or "ember"; heading: their direction in the symbol's plane (x, y);
    travel: how far they come from and go to (symbol heights)."""
    N = 160

    def __init__(self, name, carrier="bird", heading=(1.0, 0.2), travel=2.2, **kw):
        kw.setdefault("hold", 0.0)
        kw.setdefault("out", 0.0)
        super().__init__(name, **kw)
        h = np.asarray(heading, np.float64)
        self.h = h / max(np.linalg.norm(h), 1e-9)
        self.carrier, self.travel = carrier, float(travel)
        self.mid = self.t0 + 0.5 * self.dur + (self.s[:, 0] - 0.5) * 0.12
        self.lead = 0.0

    def gain(self, t):
        return 1.0 if self.t0 - 0.1 <= t <= self.t0 + self.dur + 0.1 else 0.0

    def sample(self, t, cam=None):
        if self.gain(t) <= 0.0:
            return None
        cam = self._cam(t, cam)
        half = 0.5 * self.dur
        tau = (t - self.mid) / max(half, 1e-6)
        d = np.sign(tau) * np.abs(tau) ** 2.4 * self.travel * (0.8 + 0.4 * self.s[:, 1])
        sp = np.array([-self.h[1], self.h[0]])
        loose = np.abs(tau) ** 1.5 * 0.35
        xy = self.xy + self.h[None, :] * d[:, None] + sp[None, :] * ((self.s[:, 2] - 0.5) * loose)[:, None] \
            + sp[None, :] * (0.08 * np.sin(t * 3.0 + self.s[:, 3] * 9.0) * np.abs(tau))[:, None]
        z = (self.s[:, 4] - 0.5) * loose * 1.5
        pos, s = self._world(t, cam, xy, z)
        a = np.clip((1.0 - np.abs(tau)) * 3.0, 0.0, 1.0)
        shape = np.exp(-(tau * 2.2) ** 2)                           # how much it reads as the symbol now
        if self.carrier == "bird":
            c, r, u, n, _ = self.place.frame(t, cam)
            ang = math.atan2(self.h[1], self.h[0])
            rot = np.full(self.M, ang)
            return [dict(pos=pos, size=s * 0.05, color=self.col[None, :] * (0.9 + 0.8 * shape)[:, None], alpha=a * self.k * 2.0,
                         rot=rot, kind="bird", seed=self.s[:, 5], dof=self.dof, reflect=self.reflect)]
        warm = np.array([1.0, 0.62, 0.25])
        return [dict(pos=pos, size=s * 0.018, color=(warm * (1 - shape[:, None]) + self.col * shape[:, None]) * 1.6,
                     alpha=a * self.k * 1.8, emit=1.0 + shape, kind="spark", twinkle=0.7, seed=self.s[:, 5],
                     dof=self.dof, reflect=self.reflect),
                dict(pos=pos, size=s * 0.07, color=warm * 0.5 + self.col * 0.5, alpha=a * self.k * 0.08,
                     kind="soft", seed=self.s[:, 4], dof=1.0, streak=0.0)]


RECIPES = dict(traced=Traced, constellation=Constellation, petals=PetalShape, trail=LightTrail, ripples=Ripples,
               flock=Flock)


def recipe(kind, name, **kw):
    """A recipe by its name: "traced", "constellation", "petals", "trail", "ripples", "flock"."""
    return RECIPES[kind](name, **kw)
