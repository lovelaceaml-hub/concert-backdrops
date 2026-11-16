"""The nine comets of colour: the thread of the masterpiece (lifted from Film 10, engine/songs/ten_10_nine_colours.py
on ten/10-nine-colours: Comets._one, Head and its legs, Seed's flat burst, Hoops).

A comet is a head that moves along a path, drawn as a white-hot core ribbon, a deep-colour body, a broad soft
glow, a head spark with a bloom, and sparks shed along its tail. Each head has a base path (far away, unseen)
and legs [(t0, t1, f, blend in, blend out)] that pull it in to do something: write a word (the word's pen),
stream past the camera, stitch hoops, wrap a helix round two people, braid round the climb.
"""
import numpy as np

from p3d import lin

WHITE = "#fff6e6"


def deepen(hexs, k=1.35):
    """The same hue with more saturation (linear light): a trail that stays its colour when it glows."""
    c = lin(hexs)
    m = float(c.max())
    return m * (c / m) ** k


def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


class Head:
    """A comet head: a base path with legs [(t0, t1, f, blend in, blend out)] blended over it, and how much it
    is a lead near the camera (0 on its base path: unseen)."""

    def __init__(self, base):
        self.base = base
        self.legs = []

    def leg(self, t0, t1, f, bi=0.6, bo=0.8):
        self.legs.append((float(t0), float(t1), f, float(bi), float(bo)))
        return self

    def weight(self, leg, t):
        t0, t1, _, bi, bo = leg
        if t < t0 - bi or t > t1 + bo:
            return 0.0
        return (_sc(t0 - bi, t0, t) if bi > 0 else float(t >= t0)) * \
            (1.0 - (_sc(t1, t1 + bo, t) if bo > 0 else float(t > t1)))

    def near(self, t):
        n = 0.0
        for lg in self.legs:
            n = max(n, self.weight(lg, t))
        return n

    def __call__(self, t):
        p = np.asarray(self.base(t), np.float64)
        for lg in self.legs:
            w = self.weight(lg, t)
            if w > 0.0:
                p = p * (1.0 - w) + np.asarray(lg[2](t), np.float64) * w
        return p


def _rib(pts, width, color, alpha, emit=1.0, **kw):
    from p3d.api import ribbon
    return ribbon(pts, width=width, color=color, alpha=alpha, emit=emit, **kw)


class Comets:
    """The nine ribbons of colour.

    heads    nine Head objects
    glow     nine colours (hex) they glow with
    dim      dim(points (N, 3), cam, t, k) -> (N,) factors: what keeps them out of the words (the pen may write)
    width    width(k, t) -> ribbon width in metres (a lead: about 0.3)
    tail     tail(k, t) -> seconds of trail
    cut      cut(t) -> the earliest time a tail may reach back to (no tail across a jump)
    """
    wants_camera = True

    def __init__(self, heads, glow, dim=None, width=None, tail=None, cut=None, alpha=None, seed=10):
        r = np.random.default_rng(seed)
        self.heads, self.glow = heads, list(glow)
        self.sp = r.random((len(heads), 140, 4)).astype(np.float64)
        self.dim = dim
        self.width = width or (lambda k, t: 0.30)
        self.tail = tail or (lambda k, t: 0.85)
        self.cut = cut or (lambda t: -1e9)
        self.alpha = alpha or (lambda k, t: 1.0)

    def sample(self, t, cam=None):
        out = []
        eye = None if cam is None else np.asarray(cam.pos, np.float64)
        for k in range(len(self.heads)):
            a = float(self.alpha(k, t)) * self.heads[k].near(t)
            if a <= 0.002:
                continue
            start = len(out)
            self._one(out, k, t, a, eye)
            if self.dim is not None and cam is not None:
                for b in out[start:]:
                    P = np.asarray(b["pos"], np.float64).reshape(-1, 3)
                    f = self.dim(P, cam, t, k)
                    if b.get("pos2") is not None:      # a segment: its two ends and its middle (a long segment
                        P2 = np.asarray(b["pos2"], np.float64).reshape(-1, 3)      # may span a word's box)
                        f2 = self.dim(P2, cam, t, k)
                        fm = self.dim(0.5 * (P + P2), cam, t, k)
                        if min(f.min(), f2.min(), fm.min()) < 0.999:
                            b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * np.minimum(f, fm)
                            b["alpha2"] = np.asarray(b.get("alpha2", 1.0), np.float64) * np.minimum(f2, fm)
                    elif f is not None and f.min() < 0.999:
                        b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * f
        return out or None

    def _one(self, out, k, t, a, eye):
        tail = float(self.tail(k, t))
        w = float(self.width(k, t))
        n = 56
        ts = np.linspace(max(t - tail, self.cut(t)), t, n)
        if ts[-1] - ts[0] < 1e-3:
            return
        head = self.heads[k]
        pts = np.array([head(float(x)) for x in ts])
        if eye is not None:                             # a head right at the lens would fill the picture
            dist = float(np.linalg.norm(pts[-1] - eye))
            a = a * _sc(1.2, 3.5, dist)
            if a <= 0.0:
                return
            w = w * float(np.clip(dist / 6.0, 0.35, 1.0))        # close by, a finer ribbon
            dd = np.linalg.norm(pts - eye[None, :], axis=1)
            near = _ss(0.8, 2.5, dd)                    # the tail thins away where it passes the lens
        else:
            near = np.ones(n)
        age = (t - ts) / max(tail, 1e-6)                # 0 at the head, 1 at the far end
        kk = 1.0 - age
        c = lin(self.glow[k])
        deep = deepen(self.glow[k])
        core = 0.35 * c + 0.65 * lin(WHITE)
        out.append(_rib(pts, w * 4.2 * (0.25 + 0.75 * kk), c, a * 0.09 * np.clip(kk * 1.3, 0, 1) * near, emit=1.0))
        out.append(_rib(pts, w * (0.12 + 0.88 * kk), deep, a * 0.55 * np.clip(kk * 1.4, 0, 1) * near, emit=1.6))
        out.append(_rib(pts, w * 0.22 * (0.15 + 0.85 * kk), core, a * 0.95 * np.clip(kk * 1.6, 0, 1) * near,
                        emit=2.6))
        hp = pts[-1:]
        out.append(dict(pos=hp, size=w * 0.65, color=core, alpha=a, emit=7.0, kind="spark"))
        out.append(dict(pos=hp, size=w * 5.0, color=c, alpha=a * 0.16, kind="soft"))
        sp = self.sp[k]
        f = np.mod(sp[:, 0] + t * (0.9 + 0.4 * sp[:, 1]), 1.0)          # where along the tail
        idx = f * (n - 1)
        i0 = np.floor(idx).astype(int)
        i1 = np.minimum(i0 + 1, n - 1)
        fr = (idx - i0)[:, None]
        base = pts[i0] * (1.0 - fr) + pts[i1] * fr
        drift = (sp[:, 1:4] - 0.5) * (w * 3.5) * (1.0 - f)[:, None]
        pos = base + drift - _v(0.0, 0.6 * w, 0.0) * (1.0 - f)[:, None]
        nf = near[i0]
        out.append(dict(pos=pos, size=w * (0.10 + 0.12 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                        alpha=a * 0.9 * f ** 1.5 * nf, emit=2.0, kind="spark", twinkle=0.6, seed=sp[:, 3]))


class Hoops:
    """A gate: a comet's trail left standing as hoops (a static set with birth times: each point lights as the
    comet passes it, and the hoops stay until `until`)."""

    def __init__(self, path, t0, t1, color, until, n=7000, seed=12, fade=0.8):
        self.ts = np.linspace(t0, t1, n)
        rng = np.random.default_rng(seed)
        self.pos = np.array([path(float(x)) for x in self.ts]) + rng.normal(size=(n, 3)) * 0.04
        self.size = 0.06 + 0.05 * rng.random(n)
        self.seed = rng.random(n)
        self.col = deepen(color, 1.2)
        self.t0, self.until, self.fade = t0, until, fade

    def gain(self, t):
        return float(_sc(self.t0 - 0.1, self.t0, t) * (1.0 - _sc(self.until - self.fade, self.until, t)))

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.002:
            return None
        return dict(pos=self.pos, size=self.size, color=self.col, alpha=0.55 * g, birth=self.ts, fade=0.25,
                    flash=4.0, twinkle=0.5, seed=self.seed, kind="spark", emit=1.8)


class Burst:
    """The seed's flat burst: sparks in the nine colours flung out low over the water (the sky above stays calm)."""

    def __init__(self, at, t0, glow, n=1300, seed=3, reach=22.0):
        r = np.random.default_rng(seed)
        d = r.normal(size=(n, 3))
        d[:, 1] = np.abs(d[:, 1]) * 0.12
        self.d = d / np.linalg.norm(d, axis=1, keepdims=True)
        self.s = r.random((n, 3))
        self.col = np.array([lin(glow[i % 9]) for i in range(n)]) * 0.6 + 0.4 * lin(WHITE)
        self.at, self.t0, self.reach = np.asarray(at, np.float64), float(t0), float(reach)

    def sample(self, t):
        u = t - self.t0
        if u < 0.0 or u > 2.6:
            return None
        dist = (1.0 + self.reach * self.s[:, :1]) * (1.0 - np.exp(-u * 2.2))
        pos = self.at + self.d * dist - _v(0.0, 0.5, 0.0) * u * u
        pos[:, 1] = np.maximum(pos[:, 1], 0.03)
        al = np.exp(-u / (0.45 + 0.6 * self.s[:, 1])) * _sc(0.0, 0.08, u)
        return dict(pos=pos, size=0.04 + 0.05 * self.s[:, 2], color=self.col, alpha=al, emit=1.6, kind="spark",
                    twinkle=0.5, seed=self.s[:, 2])
