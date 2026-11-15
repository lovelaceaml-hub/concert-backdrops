"""The masterpiece's brand pieces (engine/songs/master_peace.py): hearts of light drifting off the words, the
nine expression symbols traced in light as subtle scenery, the nine rivers of colour, the luminous Earth with
hearts across its continents, and the campaign logo made of light (BRAND's exact geometry, p3d/brand.py).
Pure numpy point sets; pillow is loaded only when the scene is built.
"""
import numpy as np

from .api import lin, ribbon
from .master_sky import TAU, sc, ss

WHITE = "#fff6e6"


def heart_curve(m=36):
    """A heart outline, centred, about 1 high."""
    a = np.linspace(0.0, TAU, m, endpoint=False)
    x = 16.0 * np.sin(a) ** 3
    y = 13.0 * np.cos(a) - 5.0 * np.cos(2 * a) - 2.0 * np.cos(3 * a) - np.cos(4 * a)
    return np.stack([x, y + 2.5], axis=1) / 30.0


def inside(poly, q):
    q = np.asarray(q, np.float64)
    x, y = q[:, 0], q[:, 1]
    x0, y0 = poly[:, 0], poly[:, 1]
    x1, y1 = np.roll(x0, -1), np.roll(y0, -1)
    c = np.zeros(len(q), bool)
    for i in range(len(poly)):
        cond = (y0[i] > y) != (y1[i] > y)
        xi = x0[i] + (y - y0[i]) * (x1[i] - x0[i]) / (y1[i] - y0[i] + 1e-12)
        c ^= cond & (x < xi)
    return c


# ---------------------------------------------------------------------------------------------------- hearts
class WordHearts:
    """Small hearts of light that drift off each expression in its colour while it is read (UPDATE 9).
    words: the song's PW.Words; colors: {label: display hex}; per: hearts per word."""
    wants_camera = True

    def __init__(self, words, colors, per=9, seed=77, names=None):
        r = np.random.default_rng(seed)
        self.shape = heart_curve(40)
        fill = r.uniform(-0.5, 0.5, (600, 2))
        fill = fill[inside(self.shape, fill)][:50]
        self.local = np.concatenate([self.shape, fill * 0.9])
        self.items = []
        for w in words:
            if names is not None and w.name not in names:
                continue
            if w.name not in colors:
                continue
            col = lin(colors[w.name])
            for i in range(per):
                t0 = w.t_read0 - 0.3 + (w.t_read1 - w.t_read0 + 0.2) * (i + r.random()) / per
                side = -1.0 if i % 2 == 0 else 1.0
                self.items.append((w, t0, side * (0.64 + 0.12 * r.random()), r.random() - 0.5, r.random(), col))

    def sample(self, t, cam=None):
        if cam is None:
            return None
        pts, cols, al, sz = [], [], [], []
        for w, t0, sx, sy, sd, col in self.items:
            age = t - t0
            if not (0.0 <= age <= 2.6) or not (w.t_in <= t <= w.t_out):
                continue
            o, r_, u_, _n = w.frame(t, cam)
            x0, x1, y0, y1 = w.extent()
            wdt = float(x1 - x0)
            size = 0.075 * wdt * (0.75 + 0.5 * sd)
            c = o + r_ * (sx * wdt + 0.10 * wdt * np.sign(sx) * age) + u_ * (sy * (y1 - y0) + 0.14 * wdt * age)
            ang = 0.3 * np.sin(1.7 * age + 6.0 * sd)
            ca, sa = np.cos(ang), np.sin(ang)
            sh = self.local @ np.array([[ca, sa], [-sa, ca]])
            p = c[None, :] + size * (sh[:, :1] * r_[None, :] + sh[:, 1:2] * u_[None, :])
            k = float(ss(0.0, 0.4, age) * (1.0 - ss(1.7, 2.6, age)) * (1.0 - ss(w.t_read1, w.t_out, t)))
            pts.append(p)
            cols.append(np.broadcast_to(0.7 * col + 0.3 * lin(WHITE), p.shape))
            al.append(np.full(len(p), k))
            sz.append(np.full(len(p), 0.010 * wdt))
        if not pts:
            return None
        return dict(pos=np.concatenate(pts), size=np.concatenate(sz), color=np.concatenate(cols),
                    alpha=np.concatenate(al), emit=2.0, kind="spark", twinkle=0.3, dof=0.2, reflect=False)


class HeartBurst:
    """Hearts of light bursting out of a place (a joyful twirl) in the nine colours, rising and drifting."""

    def __init__(self, at, t0, colors, n=26, reach=2.6, seed=79, size=0.22):
        r = np.random.default_rng(seed)
        self.at = at
        self.t0 = t0
        self.shape = heart_curve(32)
        a = r.uniform(0.0, TAU, n)
        el = r.uniform(0.2, 1.2, n)
        sp = reach * r.uniform(0.5, 1.0, n)
        self.v = np.stack([np.sin(a) * np.cos(el), np.sin(el), np.cos(a) * np.cos(el)], 1) * sp[:, None]
        self.col = np.array([lin(colors[i % len(colors)]) for i in range(n)]) * 0.75 + 0.25 * lin(WHITE)
        self.s = r.random(n)
        self.size = size

    def sample(self, t):
        u = t - self.t0
        if u < 0.0 or u > 3.0:
            return None
        c0 = np.asarray(self.at(self.t0) if callable(self.at) else self.at, np.float64)
        e = 1.0 - np.exp(-u * 2.2)
        cen = c0 + self.v * e[..., None] * 1.0 + np.array([0.0, 0.35, 0.0]) * u
        k = ss(0.0, 0.15, u) * (1.0 - ss(2.0, 3.0, u))
        pts, cols = [], []
        for i in range(len(cen)):
            s = self.size * (0.7 + 0.6 * self.s[i]) * (0.6 + 0.4 * e)
            p = cen[i] + s * np.stack([self.shape[:, 0], self.shape[:, 1], np.zeros(len(self.shape))], 1)
            pts.append(p)
            cols.append(np.broadcast_to(self.col[i], p.shape))
        P = np.concatenate(pts)
        return dict(pos=P, size=0.012, color=np.concatenate(cols), alpha=0.9 * k, emit=2.2, kind="spark",
                    twinkle=0.4)


# ---------------------------------------------------------------------------------------------------- symbols
def _arc(cx, cy, r, a0, a1, n=24):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1)


def _line(x0, y0, x1, y1, n=10):
    u = np.linspace(0.0, 1.0, n)[:, None]
    return np.array([x0, y0]) * (1 - u) + np.array([x1, y1]) * u


def _palm(sgn=1.0, tilt=0.0):
    """A tall open palm (praying or clapping hands), fingers up; sgn mirrors it."""
    pts = np.array([[0.0, -0.42], [0.0, 0.30], [-0.03, 0.40], [-0.09, 0.42], [-0.13, 0.36], [-0.15, 0.10],
                    [-0.21, 0.0], [-0.17, -0.12], [-0.13, -0.42]])
    pts = pts * np.array([sgn, 1.0])
    if tilt:
        a = np.radians(tilt * sgn)
        pts = pts @ np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
    u = np.linspace(0.0, len(pts) - 1, 60)
    i = np.minimum(u.astype(int), len(pts) - 2)
    f = (u - i)[:, None]
    return pts[i] * (1 - f) + pts[i + 1] * f


def _rot(pts, deg, about=(0.0, -0.42)):
    a = np.radians(deg)
    c = np.asarray(about)
    m = np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
    return (np.asarray(pts) - c) @ m + c


SYMBOLS = {
    # waving hand: a palm, four fingers, a thumb, two motion arcs
    "Greeting": [_arc(0.0, -0.10, 0.17, 200, 340), _line(-0.16, -0.16, -0.17, 0.12),
                 _line(-0.11, 0.0, -0.13, 0.36), _line(-0.03, 0.02, -0.03, 0.42), _line(0.05, 0.02, 0.07, 0.40),
                 _line(0.13, 0.0, 0.16, 0.30), _line(0.16, -0.16, 0.30, 0.02),
                 _arc(-0.05, 0.10, 0.44, 25, 70), _arc(-0.05, 0.10, 0.54, 25, 70)],
    # a person bowing: head, bent back, legs, an arm hanging
    "Gratitude": [_arc(0.20, 0.16, 0.08, 0, 360, 30), _line(0.12, 0.12, -0.10, 0.02),
                  _line(-0.10, 0.02, -0.12, -0.45), _line(-0.08, 0.0, -0.02, -0.45),
                  _line(0.08, 0.10, 0.12, -0.18)],
    # a face with a tear
    "Apology": [_arc(0.0, 0.0, 0.36, 0, 360, 60), _arc(-0.13, 0.12, 0.06, 200, 340), _arc(0.13, 0.12, 0.06, 200, 340),
                _arc(0.0, -0.20, 0.12, 30, 150), _arc(0.18, -0.06, 0.035, 180, 360, 12),
                _line(0.145, -0.06, 0.18, 0.03, 6), _line(0.215, -0.06, 0.18, 0.03, 6)],
    # a hugging face: a smiling face with two open hands
    "Inclusiveness": [_arc(0.0, 0.05, 0.32, 0, 360, 56), _arc(0.0, -0.02, 0.15, 200, 340),
                      _arc(-0.30, -0.25, 0.12, 0, 360, 26), _arc(0.30, -0.25, 0.12, 0, 360, 26)],
    # "after you": a doorway, and an open hand held out toward it
    "Concession": [np.concatenate([_line(0.12, -0.42, 0.12, 0.12, 12), _arc(0.27, 0.12, 0.15, 180, 0, 20),
                                   _line(0.42, 0.12, 0.42, -0.42, 12)]),
                   _line(-0.48, -0.26, -0.20, -0.16, 8), _line(-0.20, -0.16, 0.02, -0.10, 8),
                   _line(-0.20, -0.20, 0.00, -0.20, 6), _line(-0.18, -0.12, -0.02, -0.02, 6),
                   _line(-0.30, -0.20, -0.26, -0.06, 5)],
    # a hand cupped behind the ear, the sound coming in
    "Respect": [_arc(0.0, 0.04, 0.17, 95, 285, 26), _arc(0.02, 0.05, 0.07, 110, 260, 14),
                _arc(0.10, 0.02, 0.28, -75, 75, 26), _line(0.17, 0.29, 0.10, 0.40, 5), _line(0.24, 0.24, 0.20, 0.36, 5),
                _line(0.29, 0.16, 0.30, 0.28, 5),
                _arc(-0.05, 0.04, 0.32, 150, 210, 10), _arc(-0.05, 0.04, 0.44, 155, 205, 12)],
    # praying hands
    "Encouragement": [_palm(1.0), _palm(-1.0), _line(-0.18, -0.42, 0.18, -0.42, 8)],
    # two hands holding a heart
    "Consideration": [heart_curve(48) * 0.42 + np.array([0.0, 0.10]),
                      _arc(-0.18, -0.08, 0.26, 180, 300, 26), _arc(0.18, -0.08, 0.26, 240, 360, 26)],
    # clapping hands with a little burst
    "Compliment": [_rot(_palm(1.0), 14.0) + np.array([-0.03, 0.0]), _rot(_palm(-1.0), -14.0) + np.array([0.03, 0.0]),
                   _line(0.0, 0.50, 0.0, 0.62, 4), _line(-0.16, 0.46, -0.23, 0.55, 4), _line(0.16, 0.46, 0.23, 0.55, 4)],
}


class SymbolLight:
    """One of the nine symbols drawn in the world as light, subtly: fireflies (or sparks) trace its strokes one
    after another, the lines glow a moment in the expression's colour, twinkle, and drift apart into the air.
    place(t) -> (centre, right, up) in the world (the symbol is about `size` metres high)."""

    def __init__(self, label, place, t0, color, size=1.6, draw=1.6, hold=1.2, fade=1.2, n=900, seed=91,
                 bright=1.0, flies=6):
        r = np.random.default_rng(seed)
        strokes = SYMBOLS[label]
        lens = np.array([np.sum(np.linalg.norm(np.diff(s, axis=0), axis=1)) for s in strokes])
        tot = float(lens.sum())
        P, O = [], []
        acc = 0.0
        for s, L in zip(strokes, lens):
            seg = np.linalg.norm(np.diff(s, axis=0), axis=1)
            cs = np.concatenate([[0.0], np.cumsum(seg)])
            m = max(int(n * L / tot), 8)
            u = np.sort(r.random(m)) * cs[-1]
            i = np.clip(np.searchsorted(cs, u, side="right") - 1, 0, len(s) - 2)
            f = ((u - cs[i]) / np.maximum(seg[i], 1e-9))[:, None]
            P.append(s[i] * (1 - f) + s[i + 1] * f)
            O.append((acc + u) / tot)
            acc += L
        self.xy = np.concatenate(P)
        self.order = np.concatenate(O)
        self.jit = r.normal(size=(len(self.xy), 3))
        self.s = r.random(len(self.xy))
        self.place, self.t0, self.size = place, t0, size
        self.draw, self.hold, self.fade = draw, hold, fade
        self.col = lin(color) * 0.7 + lin(WHITE) * 0.3
        self.bright = bright
        self.flies = flies

    def sample(self, t):
        u = t - self.t0
        end = self.draw + self.hold + self.fade
        if u < 0.0 or u > end:
            return None
        c, rt, up = (np.asarray(v, np.float64) for v in self.place(t))
        nrm = np.cross(rt, up)
        born = self.order * self.draw
        age = u - born
        on = age > 0.0
        if not on.any():
            return None
        k = ss(0.0, 0.25, age) * (1.0 - ss(self.draw + self.hold - 0.2, end, u))
        drift = ss(self.draw + self.hold * 0.6, end, u)
        off = self.jit * (0.04 + 0.35 * drift) * self.size
        off[:, 1] += 0.4 * drift * self.size
        xy = self.xy * self.size
        pos = c + xy[:, :1] * rt + xy[:, 1:2] * up + off[:, :1] * rt + off[:, 1:2] * up + off[:, 2:3] * nrm * 0.3
        flash = 1.0 + 1.5 * np.exp(-np.maximum(age, 0.0) / 0.25)
        al = np.where(on, k * flash, 0.0) * 0.55 * self.bright
        out = [dict(pos=pos, size=0.012 * self.size, color=self.col, alpha=al, emit=1.6, kind="spark",
                    twinkle=0.6, seed=self.s, reflect=False)]
        if u < self.draw + 0.1:                                  # the fireflies that draw it
            q = np.clip(u / self.draw, 0.0, 1.0)
            heads = []
            for j in range(self.flies):
                qq = np.clip(q - 0.03 * j, 0.0, 1.0)
                i = int(np.argmin(np.abs(self.order - qq)))
                heads.append(pos[i])
            out.append(dict(pos=np.array(heads), size=0.03 * self.size, color=self.col, alpha=0.9 * self.bright,
                            emit=3.0, kind="spark", reflect=False))
        return out


# ---------------------------------------------------------------------------------------------------- rivers of colour
class Rivers:
    """Ribbons of coloured light (comets): a white-hot core, a coloured glow, a head that blooms and sparks shed
    behind. heads: list of (path(t), color hex, active(t) 0..1, width metres). cuts: times a tail never crosses."""
    wants_camera = True

    def __init__(self, heads, cuts=(), tail=0.9, seed=10, boxes=None):
        r = np.random.default_rng(seed)
        self.heads = heads
        self.sp = r.random((len(heads), 120, 4))
        self.cuts = list(cuts)
        self.tail = tail
        self.boxes = boxes

    def sample(self, t, cam=None):
        out = []
        cut = max([c for c in self.cuts if c <= t] + [-1e9])
        eye = None if cam is None else np.asarray(cam.pos, np.float64)
        for k, (path, hexs, active, width) in enumerate(self.heads):
            a = float(active(t))
            if a <= 0.002:
                continue
            tail = self.tail(t) if callable(self.tail) else self.tail
            w = width(t) if callable(width) else width
            n = 40
            ts = np.linspace(max(t - tail, cut), t, n)
            if ts[-1] - ts[0] < 1e-3:
                continue
            pts = np.array([path(float(x)) for x in ts])
            if eye is not None:
                dist = float(np.linalg.norm(pts[-1] - eye))
                a *= sc(1.0, 3.0, dist)
                if a <= 0.0:
                    continue
            age = (t - ts) / max(tail, 1e-3)
            kk = 1.0 - age
            c = lin(hexs)
            m = float(c.max())
            deep = m * (c / m) ** 1.35
            core = 0.35 * c + 0.65 * lin(WHITE)
            out.append(ribbon(pts, width=w * 4.0 * (0.25 + 0.75 * kk), color=c, alpha=a * 0.08 * np.clip(kk * 1.3, 0, 1),
                              emit=1.0))
            out.append(ribbon(pts, width=w * (0.12 + 0.88 * kk), color=deep, alpha=a * 0.5 * np.clip(kk * 1.4, 0, 1),
                              emit=1.5))
            out.append(ribbon(pts, width=w * 0.22 * (0.15 + 0.85 * kk), color=core,
                              alpha=a * 0.9 * np.clip(kk * 1.6, 0, 1), emit=2.4))
            head = pts[-1:]
            out.append(dict(pos=head, size=w * 0.6, color=core, alpha=a, emit=6.0, kind="spark"))
            out.append(dict(pos=head, size=w * 4.5, color=c, alpha=a * 0.14, kind="soft"))
            sp = self.sp[k]
            f = np.mod(sp[:, 0] + t * (0.9 + 0.4 * sp[:, 1]), 1.0)
            idx = f * (n - 1)
            i0 = np.floor(idx).astype(int)
            i1 = np.minimum(i0 + 1, n - 1)
            fr = (idx - i0)[:, None]
            base = pts[i0] * (1.0 - fr) + pts[i1] * fr
            drift = (sp[:, 1:4] - 0.5) * (w * 3.5) * (1.0 - f)[:, None]
            out.append(dict(pos=base + drift, size=w * (0.10 + 0.12 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                            alpha=a * 0.9 * f ** 1.5, emit=2.0, kind="spark", twinkle=0.6, seed=sp[:, 3]))
        if self.boxes is not None and cam is not None and out:
            out = self.boxes(out, t, cam)
        return out or None


# ---------------------------------------------------------------------------------------------------- the Earth
def _land_lonlat(n, seed=21):
    """n random places on land (longitude, latitude in degrees), from BRAND's land mask."""
    import os
    from PIL import Image
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "..", "assets", "p3d", "brand", "land_2048.png")
    m = np.asarray(Image.open(path).convert("L"), np.float64) > 127
    H, W = m.shape
    r = np.random.default_rng(seed)
    out = []
    while sum(len(o) for o in out) < n:
        z = r.uniform(-1.0, 1.0, 6 * n)
        lon = r.uniform(-180.0, 180.0, 6 * n)
        lat = np.degrees(np.arcsin(z))
        ix = np.clip(((lon + 180.0) / 360.0 * W).astype(int), 0, W - 1)
        iy = np.clip(((90.0 - lat) / 180.0 * H).astype(int), 0, H - 1)
        k = m[iy, ix] & (lat > -62.0)
        out.append(np.stack([lon[k], lat[k]], 1))
    return np.concatenate(out)[:n]


def sphere(n, seed):
    r = np.random.default_rng(seed)
    d = r.normal(size=(n, 3))
    return d / np.linalg.norm(d, axis=1, keepdims=True)


class Earth:
    """The whole Earth as light: a deep blue ocean of soft light, continents of small warm lights, a rim of
    bright air round its limb, slowly turning. geo(lon, lat, r) maps to the world (the song owns the frame).
    gain(t): its strength; land_k(t): how much of the land shows."""
    wants_camera = True

    def __init__(self, geo, center, radius, gain, land_k=None, ocean="#1f4fb8", land="#ffe2a8", rim="#8fd0ff",
                 n_land=34000, n_ocean=26000, seed=31):
        r = np.random.default_rng(seed)
        self.geo, self.c, self.R = geo, np.asarray(center, np.float64), float(radius)
        self.ll = _land_lonlat(n_land, seed)
        self.lseed = r.random(len(self.ll))
        self.ocean_ll = np.stack([r.uniform(-180, 180, n_ocean), np.degrees(np.arcsin(r.uniform(-1, 1, n_ocean)))], 1)
        self.oseed = r.random(n_ocean)
        self.gain = gain
        self.land_k = land_k or (lambda t: 1.0)
        self.col_o, self.col_l, self.col_r = lin(ocean), lin(land), lin(rim)
        warm = r.random(len(self.ll))[:, None]
        self.lcol = self.col_l[None] * (1 - 0.35 * warm) + lin("#ffb98a")[None] * 0.35 * warm

    def sample(self, t, cam=None):
        g = float(self.gain(t))
        if g <= 0.002:
            return None
        out = []
        o = self.geo(self.ocean_ll[:, 0], self.ocean_ll[:, 1], 0.995, t)
        out.append(dict(pos=o, size=0.06 * self.R, color=self.col_o, alpha=0.085 * g, kind="soft", seed=self.oseed,
                        dof=0.0, reflect=False))
        lk = float(self.land_k(t)) * g
        if lk > 0.0:
            p = self.geo(self.ll[:, 0], self.ll[:, 1], 1.003, t)
            out.append(dict(pos=p, size=(0.006 + 0.006 * self.lseed) * self.R, color=self.lcol, alpha=0.9 * lk,
                            emit=1.5, kind="spark", twinkle=0.25, seed=self.lseed, dof=0.0, reflect=False))
            out.append(dict(pos=p[::6], size=0.035 * self.R, color=self.col_l, alpha=0.05 * lk, kind="soft",
                            dof=0.0, reflect=False))
        if cam is not None:                                       # the air: a bright rim round the limb
            e = np.asarray(cam.pos, np.float64) - self.c
            dist = float(np.linalg.norm(e))
            if dist > self.R * 1.05:
                e = e / dist
                ref = np.array([0.0, 1.0, 0.0]) if abs(e[1]) < 0.95 else np.array([1.0, 0.0, 0.0])
                a1 = np.cross(e, ref)
                a1 /= np.linalg.norm(a1)
                a2 = np.cross(e, a1)
                ang = np.linspace(0.0, TAU, 720, endpoint=False)
                rr = self.R * np.sqrt(1.0 - (self.R / dist) ** 2)
                c0 = self.c + e * (self.R * self.R / dist)
                ring = c0 + rr * (np.cos(ang)[:, None] * a1 + np.sin(ang)[:, None] * a2)
                out.append(dict(pos=ring, size=0.09 * self.R, color=self.col_r, alpha=0.32 * g, kind="soft", dof=0.0,
                                reflect=False))
                out.append(dict(pos=self.c + (ring - self.c) * 1.06, size=0.25 * self.R, color=lin("#7fb0ff"),
                                alpha=0.09 * g, kind="soft", dof=0.0, reflect=False))
        return out


class EarthShadow:
    """The solid Earth: its silhouette hides the stars behind it (a dark mask; give it Mask("dark"))."""
    static = True

    def __init__(self, center, radius, n=3000):
        self.p = np.asarray(center, np.float64) + 0.97 * radius * sphere(n, 5)

    def sample(self, t):
        return dict(pos=self.p, size=0.02, alpha=1.0, color=(0.0, 0.0, 0.0), reflect=False)


class EarthHearts:
    """Hearts in the nine colours that bloom across the continents one after another, joined by arcs of light;
    at fly(t) they lift off toward given places (the logo's hearts)."""

    def __init__(self, geo, center, radius, colors, t0, t1, n=54, seed=41, dests=None, t_fly=None, arcs=26):
        r = np.random.default_rng(seed)
        self.geo, self.c, self.R = geo, np.asarray(center, np.float64), float(radius)
        ll = _land_lonlat(4 * n, seed + 1)
        keep = (ll[:, 1] > -40.0) & (ll[:, 1] < 64.0)
        self.ll = ll[keep][:n]
        self.tb = np.sort(t0 + (t1 - t0) * r.random(len(self.ll)))
        self.col = np.array([lin(colors[i % len(colors)]) for i in range(len(self.ll))])
        self.shape = heart_curve(36) - np.array([0.0, 0.05])
        fill = r.uniform(-0.5, 0.5, (500, 2))
        fill = fill[inside(heart_curve(60), fill)][:40]
        self.local = np.concatenate([self.shape, fill * 0.9])
        self.dests = dests
        self.t_fly = t_fly
        self.fs = r.random(len(self.ll))
        idx = r.permutation(len(self.ll))
        self.arcs = [(int(a), int(b)) for a, b in zip(idx[0::2][:arcs], idx[1::2][:arcs])]

    def _place(self, i, t):
        p = self.geo(self.ll[i:i + 1, 0], self.ll[i:i + 1, 1], 1.006, t)[0]
        nrm = (p - self.c) / self.R
        up = np.array([0.0, 1.0, 0.0]) - nrm[1] * nrm
        up /= max(np.linalg.norm(up), 1e-6)
        return p, nrm, up, np.cross(up, nrm)

    def sample(self, t):
        if t < self.tb.min():
            return None
        pts, cols, al, sz = [], [], [], []
        size = 0.17 * self.R
        for i in range(len(self.ll)):
            age = t - self.tb[i]
            if age < 0.0:
                continue
            p, nrm, up, rt = self._place(i, t)
            e = 0.0
            if self.t_fly is not None:
                tf = self.t_fly + 0.35 * self.fs[i]
                e = sc(tf, tf + 0.6, t)
                if e >= 1.0:
                    continue
                if e > 0.0:
                    d = np.asarray(self.dests(i), np.float64)
                    ctrl = p + nrm * 0.6 * self.R
                    p = (1 - e) ** 2 * p + 2 * e * (1 - e) * ctrl + e * e * d
            pop = 1.0 + 0.7 * np.exp(-age / 0.12)
            s = size * pop * (1.0 - 0.5 * e)
            q = p[None, :] + s * (self.local[:, :1] * rt[None, :] + self.local[:, 1:2] * up[None, :])
            k = float(ss(0.0, 0.15, age) * (1.0 - ss(0.7, 1.0, e)))
            pts.append(q)
            cols.append(np.broadcast_to(0.85 * self.col[i] + 0.15 * lin(WHITE), q.shape))
            al.append(np.full(len(q), k))
            sz.append(np.full(len(q), 0.016 * self.R))
        fade_arcs = 1.0 if self.t_fly is None else 1.0 - sc(self.t_fly - 0.3, self.t_fly + 0.1, t)
        if fade_arcs > 0.0:
            for a, b in self.arcs:
                t0 = max(self.tb[a], self.tb[b]) + 0.15
                u = (t - t0) / 0.6
                if u <= 0.0:
                    continue
                pa = self._place(a, t)[0] - self.c
                pb = self._place(b, t)[0] - self.c
                A, B = pa / np.linalg.norm(pa), pb / np.linalg.norm(pb)
                om = np.arccos(np.clip(A @ B, -1.0, 1.0))
                if om < 1e-3:
                    continue
                s = np.linspace(0.0, min(u, 1.0), 80)
                d = (np.sin((1 - s) * om)[:, None] * A + np.sin(s * om)[:, None] * B) / np.sin(om)
                lift = 1.006 + 0.25 * np.sin(np.pi * s) * om / np.pi
                q = self.c + self.R * lift[:, None] * d
                pts.append(q)
                cols.append((1 - s)[:, None] * self.col[a] + s[:, None] * self.col[b])
                al.append(np.full(len(q), 0.55 * fade_arcs))
                sz.append(np.full(len(q), 0.018 * self.R))
        if not pts:
            return None
        return dict(pos=np.concatenate(pts), size=np.concatenate(sz), color=np.concatenate(cols),
                    alpha=np.concatenate(al), emit=2.0, kind="spark", twinkle=0.2, dof=0.0, reflect=False)


# ---------------------------------------------------------------------------------------------------- the logo
class LogoLight:
    """The campaign logo made of light, from BRAND's exact geometry (p3d.brand.logo_points): placed by
    origin, right, up, normal and height (metres); each part draws itself in its order between its times
    (parts: dict(part name -> (t0, t1))). gain(t) overall; paint(t) 0..1 moves from light toward its true
    colours (for a day sky). Logo units: 1.0 high, centred."""

    def __init__(self, origin, right, up, normal, height, parts, gain, n=70000, seed=7, bright=1.0):
        from . import brand
        lp = brand.logo_points(n, seed)
        self.o, self.r, self.u, self.nm = (np.asarray(v, np.float64) for v in (origin, right, up, normal))
        self.h = float(height)
        x, y, z = lp["x"].astype(np.float64), lp["y"].astype(np.float64), lp["z"].astype(np.float64)
        self.pos = self.o + self.h * (x[:, None] * self.r + y[:, None] * self.u + z[:, None] * self.nm * 0.5)
        names = brand.PARTS
        birth = np.full(len(x), 1e9)
        for pi, name in enumerate(names):
            if name not in parts:
                continue
            t0, t1 = parts[name]
            sel = lp["part"] == pi
            birth[sel] = t0 + (t1 - t0) * lp["order"][sel]
        self.birth = birth
        rgb = lp["rgb"].astype(np.float64)
        self.col = rgb ** 2.2
        self.weight = lp["weight"].astype(np.float64)
        cov = lp["covered"].astype(np.float64)
        self.cov = cov.max(axis=1) if cov.ndim == 2 else cov
        self.cell = float(lp["cell"]) * self.h
        self.seed = np.random.default_rng(seed).random(len(x))
        self.gain = gain
        self.bright = bright

    def sample(self, t):
        g = float(self.gain(t))
        if g <= 0.002:
            return None
        al = g * self.weight * (1.0 - 0.85 * self.cov) * 0.5 * self.bright
        return dict(pos=self.pos, size=self.cell * 1.9, color=self.col * 1.25 + 0.04, alpha=al, birth=self.birth,
                    fade=0.25, flash=2.5, emit=1.4, kind="soft", seed=self.seed, dof=0.0, reflect=False)


class RisingHearts:
    """Hearts of light that rise from an acted moment (between two people, from a heart, from joined hands) in
    the expression's colour, drifting up and turning a little, then fading: hearts that come from the action.
    source(t) gives where they are born; windows: list of (t0, t1, color hex)."""

    def __init__(self, source, windows, rate=4.0, size=(0.09, 0.17), rise=0.55, seed=83):
        r = np.random.default_rng(seed)
        self.source = source
        self.shape = heart_curve(30)
        fill = r.uniform(-0.5, 0.5, (400, 2))
        self.fill = fill[inside(heart_curve(48), fill)][:30] * 0.85
        self.items = []
        for t0, t1, hexs in windows:
            m = int(max((t1 - t0) * rate, 1))
            for i in range(m):
                tb = t0 + (t1 - t0) * (i + r.random()) / m
                self.items.append(dict(tb=tb, col=lin(hexs) * 0.8 + 0.2 * lin(WHITE), size=r.uniform(*size),
                                       drift=r.normal(0.0, 0.18, 3), ph=r.random() * TAU))
        self.rise = rise

    def sample(self, t):
        pts, cols, al, sz = [], [], [], []
        for it in self.items:
            age = t - it["tb"]
            if not (0.0 <= age <= 3.0):
                continue
            c0 = np.asarray(self.source(it["tb"]), np.float64)
            c = c0 + np.array([0.0, self.rise, 0.0]) * age + it["drift"] * age + \
                np.array([0.06 * np.sin(1.8 * age + it["ph"]), 0.0, 0.0])
            s = it["size"] * (0.5 + 0.5 * ss(0.0, 0.6, age))
            ang = 0.25 * np.sin(1.3 * age + it["ph"])
            ca, sa = np.cos(ang), np.sin(ang)
            loc = np.concatenate([self.shape, self.fill]) @ np.array([[ca, sa], [-sa, ca]])
            p = c[None, :] + s * np.stack([loc[:, 0], loc[:, 1], np.zeros(len(loc))], 1)
            k = float(ss(0.0, 0.35, age) * (1.0 - ss(1.8, 3.0, age)))
            pts.append(p)
            cols.append(np.broadcast_to(it["col"], p.shape))
            al.append(np.full(len(p), 0.85 * k))
            sz.append(np.full(len(p), 0.09 * s))
        if not pts:
            return None
        return dict(pos=np.concatenate(pts), size=np.concatenate(sz), color=np.concatenate(cols),
                    alpha=np.concatenate(al), emit=2.0, kind="spark", twinkle=0.3, reflect=True)


class LogoBurst:
    """The peak of the film: as the world becomes the logo, light bursts out of it in every direction, sparks in
    the nine colours and gold racing past the camera, and a ring of light opening round the logo."""
    wants_camera = False

    def __init__(self, center, normal, t0, colors, n=7000, size=10.0, seed=99, life=1.6, plane=False, r0=0.0,
                 ring=True):
        r = np.random.default_rng(seed)
        self.c = np.asarray(center, np.float64)
        nm = np.asarray(normal, np.float64)
        d = r.normal(size=(n, 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        if plane:                                       # outward in the picture's plane, never across the middle
            d = d - (d @ nm)[:, None] * nm[None, :] + nm[None, :] * r.uniform(-0.12, 0.25, (n, 1))
        else:
            d = d + nm[None, :] * 0.9                   # more of it toward the camera
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        self.d = d
        self.r0 = float(r0) * r.uniform(0.9, 1.15, n)
        self.ring = ring
        self.sp = size * r.uniform(1.0, 3.2, n)
        self.s = r.random(n)
        gold = lin("#ffd890")
        self.col = np.array([lin(colors[i % len(colors)]) if r.random() < 0.55 else gold for i in range(n)])
        self.t0, self.life, self.size = t0, life, size
        ref = np.array([0.0, 1.0, 0.0]) if abs(nm[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
        a1 = np.cross(nm, ref)
        a1 /= np.linalg.norm(a1)
        self.a1, self.a2 = a1, np.cross(nm, a1)
        self.ang = np.linspace(0.0, TAU, 900, endpoint=False)

    def sample(self, t):
        u = t - self.t0
        if u < 0.0 or u > self.life:
            return None
        e = 1.0 - np.exp(-u * 2.4)
        p = self.c + self.d * (self.r0 + self.sp * e)[:, None]
        al = (1.0 - ss(0.35 * self.life, self.life, u)) * (0.5 + 0.5 * self.s)
        R = self.size * (0.6 + 2.6 * e)
        ring = self.c + R * (np.cos(self.ang)[:, None] * self.a1 + np.sin(self.ang)[:, None] * self.a2)
        kr = 1.0 - ss(0.2, 0.9 * self.life, u)
        out = [dict(pos=p, size=0.012 * self.size * (0.6 + 0.8 * self.s), color=self.col, alpha=0.9 * al,
                    emit=2.4, kind="spark", twinkle=0.4, seed=self.s, streak=1.0, dof=0.0, reflect=False)]
        if self.ring:
            out.append(dict(pos=ring, size=0.03 * self.size, color=lin("#ffe6b0"), alpha=0.5 * kr, emit=1.6,
                            kind="soft", dof=0.0, reflect=False))
        return out
