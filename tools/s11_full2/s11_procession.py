"""Song 11 v2: Mother as light alone leading everyone across the sea of glass toward Zion (2:05.9),
the march (2:14.54), hearts lighting in the walkers on fulfilled, the kings laying down their crowns, the held
breath before the second slam.

Owned by the procession thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.

The story of the shot (125.92 to 162.86):
  125.92  a light comes down out of the sky onto the sea of glass ahead of everyone (Mother, light alone)
  127.64  it touches the sea (the third strings pulse): a ring of light runs out over the sea, and people of
          light gather behind it from every side (sparks fly in and become people)
  134.54  "march ahead": everyone steps out together behind her light toward Mount Zion
  144.4   "fulfilled": hearts light up in every person, a wave from her light back through the procession
  148.6   kings in gold walk in the aisle, crowns of light on their heads
  154.2   the kings kneel and lay their crowns down; 155.34 the crowns rise as sparks toward Zion
  156.0   the held breath: everyone stands still, the light gathers to her, then the slam cuts away
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

T0, T1 = 125.92, 162.86
LAND = STRINGS[2]          # 127.64: the light touches the sea on the third strings pulse
MARCH = HIT["march"]       # 134.54: everyone steps out together
HALT = DROP2               # 156.0: the held breath, everyone stands still
MOTHER_Z0 = -55.0          # where Mother's light comes down on the sea, ahead of everyone
M_H = 4.2                  # how high her light rides over the sea
WALK = 1.3                 # metres per second toward Zion, from "march ahead"
AISLE = 4.0                # the aisle down the middle (the kings walk and kneel in it)
KNEEL = HIT["kings1"]      # 154.2
RISE = HIT["kings2"]       # 155.34
K_STOP = KNEEL - 0.05      # the kings stop walking and go down
K_IN = 148.6               # the kings appear in the aisle
LAY0, LAY1 = 154.75, 155.28   # the crowns go from the heads down onto the sea before the kings


def walked(t):
    """How far everyone has walked at t (metres)."""
    return WALK * float(np.clip(t - MARCH, 0.0, HALT - MARCH))


def mother_pos(t):
    e = float(np.clip((t - T0) / (LAND - T0), 0.0, 1.0))
    d = (1.0 - e) ** 2                                  # comes down fast, settles gently
    y = M_H + 72.0 * d + 0.18 * np.sin(1.3 * t) * e
    return _v(0.0, y, MOTHER_Z0 - 22.0 * d - walked(t))


def _keys():
    """The camera: high behind the gathering as the light comes down; tilting down over the procession for
    "This hope was engraved"; down among the walkers for the hearts; close behind the kings; then all but still
    for the held breath."""
    k = [(125.92, (7.0, 24.0, 52.0), (0.0, 16.0, -160.0)),
         (129.5, (4.0, 21.0, 32.0), (0.0, 6.0, -150.0)),
         (132.5, (2.0, 28.5, 20.0), (0.0, -6.0, -60.0)),
         (135.0, (0.5, 30.0, 4.4), (0.0, 0.0, -31.4)),
         (138.0, (0.0, 30.0, 0.5), (0.0, 0.0, -35.3)),
         (141.0, (0.0, 29.5, -3.4), (0.0, 0.0, -38.6)),
         (143.8, (-2.0, 12.0, -36.0), (0.0, 1.0, -105.0)),
         (147.0, (-2.5, 9.0, -44.0), (0.0, 0.0, -95.0)),
         (150.4, (-4.0, 18.0, -48.0), (0.0, -6.0, -74.0)),
         (154.2, (-3.5, 17.0, -53.0), (0.0, -7.0, -78.0)),
         (156.0, (-3.3, 16.8, -54.0), (0.0, -7.0, -79.5)),
         (160.3, (-3.0, 16.5, -55.5), (0.0, -6.0, -80.5)),
         (162.86, (-2.8, 16.0, -57.0), (0.0, -2.5, -84.0))]
    return [(t, _v(*p), _v(*q)) for t, p, q in k]


SHOTS = [
    # Mother's light leads everyone across the sea of glass toward Mount Zion; the kings; the held breath
    dict(name="procession", kind="local", t0=T0, t1=T1, fov=50.0, aperture=0.0, keys=_keys()),
]


def proc_k(t):
    return local_k(t) if T0 <= t < T1 and shot_name(t) == "procession" else 0.0


# ---------------------------------------------------------------------------------------------------------
# Where everyone walks: rows behind her light, fanning out, an aisle down the middle
# ---------------------------------------------------------------------------------------------------------
def _proc_places(seed=51):
    r = np.random.default_rng(seed)
    out = []
    z, row = MOTHER_Z0 + 5.0, 0
    while z < MOTHER_Z0 + 100.0:
        u = (z - MOTHER_Z0) / 100.0
        half = 7.5 + 19.0 * u ** 0.8
        xs = np.arange(AISLE, half, 1.75) + 0.85 * (row % 2)
        for s in (-1.0, 1.0):
            x = s * (xs + r.uniform(-0.3, 0.3, len(xs)))
            zz = z + r.uniform(-0.45, 0.45, len(xs))
            keep = r.random(len(xs)) > 0.12 + 0.25 * (np.abs(x) > half - 3.0)     # ragged edges
            out.append(np.stack([x, np.zeros(len(xs)), zz], 1)[keep])
        z += 1.9
        row += 1
    return np.concatenate(out)


PROC_P = _proc_places()
_R0 = np.random.default_rng(52)
_D0 = np.hypot(PROC_P[:, 0], PROC_P[:, 2] - MOTHER_Z0)
ARRIVE = LAND + 0.5 + 2.6 * (_D0 / _D0.max()) ** 0.85 + _R0.uniform(0.0, 0.6, len(PROC_P))


def _ahead(crowd):
    """Unit walking directions of a crowd's people (their facing, jitter included)."""
    f = crowd.facing
    return np.stack([np.sin(f), np.zeros(len(f)), np.cos(f)], 1)


def _points_of(crowd, t, ii=None):
    """The world points (I, P, 3) of people ii of a crowd at t (all of one prototype)."""
    ii = np.arange(crowd.n) if ii is None else np.asarray(ii)
    pr = crowd.protos[crowd.kind[ii[0]]]
    pr.bake()
    age = np.maximum(t - crowd.start[ii], 0.0)
    P = pr.frames(t, age, crowd.rate[ii], crowd.phase[ii], crowd.act[ii], crowd.act_end[ii],
                  crowd.irate[ii]).astype(np.float64)
    return crowd._place(P, ii, age, pr)


# ---------------------------------------------------------------------------------------------------------
# Mother as light alone
# ---------------------------------------------------------------------------------------------------------
def gather_k(t):
    """The light gathering to her in the held breath (0 to 1 just before the slam)."""
    return _sc(157.5, 162.8, t) ** 1.6


class MotherLight:
    """Mother as light alone (never a figure): a light that comes down out of the sky onto the sea, a ring of
    light running out from where it touches, a pool of light on the sea under it, and it leads everyone."""

    def __init__(self):
        r = np.random.default_rng(61)
        self.s = r.random((420, 4))
        a = np.linspace(0, 2 * np.pi, 1400, endpoint=False)
        self.cs = np.stack([np.sin(a), np.cos(a)], 1)
        self.rs = r.random(1400)

    def sample(self, t):
        k = proc_k(t)
        if k <= 0.0:
            return None
        m = mother_pos(t)
        hits = [MARCH] + FULFIL + [RISE]
        held = _sc(HALT, HALT + 1.0, t)
        g = gather_k(t)
        pulse = (1.0 + 0.5 * hit_pulse(t, hits, fall=0.8) + 0.12 * (1.0 - held) * beat_pulse(t)
                 + 0.08 * held * np.sin(2.0 * np.pi * 0.45 * t) + 1.0 * g)
        s = self.s
        ang = 2 * np.pi * s[:, 0] + 0.35 * t * (0.5 + s[:, 1])
        rad = (1.0 + 2.8 * s[:, 2]) * (1.0 - 0.45 * g)
        halo = m[None, :] + np.stack([rad * np.cos(ang), 1.3 * (s[:, 3] - 0.5) * rad, rad * np.sin(ang)], 1)
        warm = lin("#ffe2b4")
        out = [dict(pos=m[None, :], size=20.0 + 6.0 * g, color=warm, alpha=0.06 * k * pulse, kind="soft", emit=1.5),
               dict(pos=m[None, :], size=8.0, color=lin("#ffe8c8"), alpha=0.28 * k * pulse, kind="soft", emit=2.0),
               dict(pos=m[None, :], size=2.4, color=lin(WHITE), alpha=0.9 * k, kind="soft", emit=3.5 * pulse),
               dict(pos=m[None, :], size=0.45, color=lin(WHITE), alpha=k, kind="spark", emit=7.0 * pulse),
               dict(pos=halo, size=0.07, color=lin("#ffe6b8"), alpha=0.75 * k, kind="spark", emit=2.6, twinkle=0.8,
                    seed=s[:, 0])]
        # coming down: a trail of light behind it
        if t < LAND + 0.4:
            back = np.linspace(0.02, 0.9, 60)
            P = np.stack([mother_pos(t - b) for b in back])
            a = np.exp(-back / 0.3) * (1.0 - _sc(LAND - 0.1, LAND + 0.4, t))
            out.append(dict(pos=P, size=0.5 * (1.0 - 0.6 * back), color=lin("#fff0d8"), alpha=0.8 * k * a,
                            kind="soft", emit=2.5, reflect=False))
        # touching the sea: rings of light run out over it (the people gather inside them)
        for t0, v, a0 in ((LAND, 16.0, 0.9), (LAND + 0.55, 11.0, 0.5)):
            u = t - t0
            if 0.0 <= u < 5.0:
                rr = 1.0 + v * u
                p = np.stack([self.cs[:, 0] * rr, np.full(len(self.cs), 0.08), MOTHER_Z0 + self.cs[:, 1] * rr], 1)
                a = a0 * np.exp(-u / 1.4) * _sc(0.0, 0.08, u) * k
                out.append(dict(pos=p, size=0.22 + 0.04 * u, color=lin("#ffe4b8"), alpha=a, emit=2.4, kind="spark",
                                twinkle=0.4, seed=self.rs, reflect=False))
        # a pool of light on the sea under her
        if t > LAND - 0.3:
            a = _sc(LAND - 0.3, LAND + 0.3, t) * k
            out.append(dict(pos=_v(m[0], 0.06, m[2])[None, :], size=7.0, color=warm, alpha=0.16 * a * pulse,
                            kind="soft", emit=1.6, reflect=False))
        return out


class Gather:
    """People of light gathering behind her light from every side: a spark flies in for each person and
    becomes them (each person appears as their spark arrives)."""

    def __init__(self):
        r = np.random.default_rng(62)
        n = len(PROC_P)
        d = PROC_P - _v(0.0, 0.0, MOTHER_Z0)[None, :]
        out = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
        side = np.stack([np.sign(PROC_P[:, 0]), np.zeros(n), np.zeros(n)], 1)
        dirn = 0.55 * out + 0.45 * side + 0.35 * np.stack([r.normal(0, 1, n), np.zeros(n), r.normal(0, 1, n)], 1)
        dirn = dirn / np.maximum(np.linalg.norm(dirn, axis=1, keepdims=True), 1e-6)
        self.end = PROC_P + _v(0.0, 1.1, 0.0)
        self.beg = self.end + dirn * r.uniform(22.0, 55.0, n)[:, None] + np.stack(
            [np.zeros(n), r.uniform(2.0, 9.0, n), np.zeros(n)], 1)
        self.mid = 0.5 * (self.beg + self.end) + np.stack([np.zeros(n), r.uniform(3.0, 8.0, n), np.zeros(n)], 1)
        self.dur = r.uniform(1.3, 2.0, n)
        self.t1 = ARRIVE
        self.seed = r.random(n)

    def _at(self, u):
        u = u[:, None]
        return (1 - u) ** 2 * self.beg[self.on] + 2 * u * (1 - u) * self.mid[self.on] + u * u * self.end[self.on]

    def sample(self, t):
        if proc_k(t) <= 0.0 or t > ARRIVE.max() + 0.2:
            return None
        u = (t - (self.t1 - self.dur)) / self.dur
        self.on = (u > 0.0) & (u < 1.0)
        if not self.on.any():
            return None
        uu = u[self.on]
        e = 1.0 - (1.0 - uu) ** 1.6
        p = self._at(e)
        q = self._at(np.maximum(e - 0.07, 0.0))
        a = _sc(0.0, 0.15, uu) * (0.6 + 0.8 * uu)
        col = lin("#fff0d6")
        return [dict(pos=p, pos2=q, size=0.10, color=col, alpha=0.6 * a, emit=2.4, kind="line", reflect=False),
                dict(pos=p, size=0.28, color=col, alpha=a, emit=3.2, kind="spark", seed=self.seed[self.on])]


# ---------------------------------------------------------------------------------------------------------
# Hearts lighting in everyone ("fulfilled") and the light gathering to her (the held breath)
# ---------------------------------------------------------------------------------------------------------
class FulfilHearts:
    """Verse 2 "fulfilled" (2:24.4 to 2:30.2): on each accent of the quickening heartbeat, hearts light up in
    the people walking behind Mother's light, in the nine colours: a wave from her light back through the
    procession. In the held breath they breathe together, and from 159 a spark leaves each heart for her."""

    def __init__(self, walkers):
        self.w = walkers
        r = np.random.default_rng(71)
        n = walkers.n
        rank = np.argsort(np.argsort(_D0 + r.uniform(0.0, 12.0, n))) / n
        acc = np.minimum((rank * len(FULFIL)).astype(int), len(FULFIL) - 1)
        self.when = np.asarray(FULFIL)[acc] + r.uniform(0.0, 0.10, n)
        self.col = np.asarray([lin(COL9[i]) for i in r.integers(0, 9, n)])
        from p3d.brand_hearts import heart_points
        self.h = np.concatenate([heart_points(26), 0.55 * heart_points(8, fill=True)])
        self.chest = None
        self.go = 159.0 + r.uniform(0.0, 2.3, n)           # sparks leave for her light
        self.fly = r.uniform(1.0, 1.6, n)
        self.bend = r.normal(0.0, 1.0, (n, 3)) * _v(2.5, 1.5, 0.0)
        self.sub = r.random(n) < 0.55

    def centres(self, t):
        w = self.w
        if self.chest is None:
            hgt = np.zeros(w.n)
            for k, pr in enumerate(w.protos):
                pr.bake()
                hgt[w.kind == k] = pr.height
            self.chest = 0.72 * hgt * w.scale
        return w.place + _ahead(w) * walked(t) + self.chest[:, None] * _v(0.0, 1.0, 0.0)[None, :]

    def sample(self, t):
        if proc_k(t) <= 0.0 or t < FULFIL[0] - 0.1:
            return None
        on = t >= self.when
        if not on.any():
            return None
        c = self.centres(t)[on]
        u = t - self.when[on]
        held = _sc(HALT, HALT + 1.0, t)
        breath = 1.0 + held * (0.18 * np.sin(2.0 * np.pi * 0.45 * t) + 0.5 * gather_k(t))
        a = np.clip(u / 0.12, 0.0, 1.0) * (0.75 + 0.9 * np.exp(-u / 0.45)) * breath
        hs = 0.28
        H = np.stack([self.h[:, 0] * hs, self.h[:, 1] * hs, np.zeros(len(self.h))], 1)
        P = c[:, None, :] + H[None, :, :]
        nh = len(self.h)
        cols = np.repeat(self.col[on], nh, axis=0)
        out = [dict(pos=P.reshape(-1, 3), size=0.03, color=cols, alpha=np.repeat(np.minimum(a, 1.6), nh), emit=3.0,
                    kind="spark", reflect=False),
               dict(pos=c, size=0.45, color=self.col[on], alpha=0.22 * a, emit=1.8, kind="soft")]
        # the held breath: light leaves the hearts and gathers to her
        if t > 159.0:
            m = mother_pos(t)
            sel = on & self.sub & (t > self.go)
            if sel.any():
                v = np.clip((t - self.go[sel]) / self.fly[sel], 0.0, 1.0)
                e = v * v * (3.0 - 2.0 * v)
                c0 = self.centres(t)[sel]
                mid = 0.5 * (c0 + m[None, :]) + self.bend[sel] + _v(0.0, 3.0, 0.0)
                ee = e[:, None]
                p = (1 - ee) ** 2 * c0 + 2 * ee * (1 - ee) * mid + ee * ee * m[None, :]
                live = v < 0.98
                col = 0.5 * self.col[sel] + 0.5 * lin(WHITE)[None, :]
                out.append(dict(pos=p[live], size=0.09, color=col[live], alpha=0.9 * np.sin(np.pi * v[live]) + 0.1,
                                emit=2.6, kind="spark", reflect=False))
        return out


# ---------------------------------------------------------------------------------------------------------
# The kings: they walk in the aisle in gold, crowns of light on their heads, kneel and lay the crowns down
# ---------------------------------------------------------------------------------------------------------
KINGS_STOP = np.asarray([(-2.55, 0.0, -66.0), (-0.85, 0.0, -66.3), (0.85, 0.0, -66.3), (2.55, 0.0, -66.0),
                         (-1.7, 0.0, -64.1), (0.0, 0.0, -64.3), (1.7, 0.0, -64.1)])
KINGS_P = KINGS_STOP + _v(0.0, 0.0, WALK * (K_STOP - K_IN))


def _robed(crowd):
    """Kings wear long robes."""
    for pr in crowd.protos:
        pr.spec["garment"] = "robe"
        pr.spec["hair"] = "short"
    crowd.facing[:] = np.pi
    return crowd


class Crowns:
    """Crowns of gold light on the kings' heads (they follow each head as the kings walk and kneel); as the
    kings go down the crowns are laid on the sea before them (2:34.75), and on 2:35.34 they rise as sparks
    toward Zion."""

    def __init__(self, walking, kneeling):
        self.wk, self.kn = walking, kneeling
        r = np.random.default_rng(81)
        R = 0.115
        a = np.linspace(0, 2 * np.pi, 46, endpoint=False)
        ring = np.stack([R * np.cos(a), np.zeros(46), R * np.sin(a)], 1)
        tips, jewels = [], []
        for i in range(8):
            b = 2 * np.pi * i / 8
            base = _v(R * np.cos(b), 0.04, R * np.sin(b))
            top = _v(1.18 * R * np.cos(b), 0.15, 1.18 * R * np.sin(b))
            tips.append(_seg(base, top, 0.016))
            jewels.append(top)
        self.C = np.concatenate([ring, ring + _v(0, 0.045, 0)] + tips)
        self.J = np.asarray(jewels)
        n = len(KINGS_STOP)
        self.s = r.random((n, 110, 4))
        self.cache = (None, None)

    def heads(self, t):
        """The top of each king's head (x, y, z) at t."""
        if self.cache[0] == t:
            return self.cache[1]
        crowd = self.wk if t < K_STOP else self.kn
        P = _points_of(crowd, t)
        out = []
        for Q in P:
            y = Q[:, 1]
            top = y.max()
            sel = y > top - 0.09
            out.append(_v(Q[sel, 0].mean(), top - 0.06, Q[sel, 2].mean()))
        out = np.asarray(out)
        self.cache = (t, out)
        return out

    def sample(self, t):
        if proc_k(t) <= 0.0 or not (K_IN - 0.2 <= t < RISE + 6.0):
            return None
        out = []
        gold, pale = lin(GOLD), lin("#ffe6a8")
        if t < RISE:
            hd = self.heads(t)
            a = _sc(K_IN, K_IN + 0.7, t)
            lay = _sc(LAY0, LAY1, t)
            for i, h in enumerate(hd):
                ground = KINGS_STOP[i] + _v(0.0, 0.05, -0.85)
                c = h * (1 - lay) + ground * lay + _v(0.0, 0.35 * np.sin(np.pi * lay), 0.0)
                out.append(dict(pos=self.C + c, size=0.026, color=gold, alpha=a, emit=3.6, kind="spark"))
                out.append(dict(pos=self.J + c, size=0.045, color=pale, alpha=a, emit=5.0, kind="spark"))
                out.append(dict(pos=(c + _v(0, 0.07, 0))[None, :], size=0.55, color=gold, alpha=0.22 * a, emit=2.0,
                                kind="soft"))
            if t > RISE - 0.25:
                f = _sc(RISE - 0.25, RISE, t)
                P = KINGS_STOP + _v(0.0, 0.12, -0.85)
                out.append(dict(pos=P, size=1.1, color=gold, alpha=0.45 * f, emit=2.4, kind="soft"))
            return out
        u = t - RISE
        aim = CHURCH + _v(0.0, 60.0, 0.0)
        for i, p in enumerate(KINGS_STOP):
            s = self.s[i]
            c = p + _v(0.0, 0.1, -0.85)
            d0 = _unit(aim - c)
            spread = np.stack([s[:, 0] - 0.5, 0.6 * (s[:, 1] - 0.5), s[:, 2] - 0.5], 1) * 0.55
            d = d0[None, :] + spread
            d = d / np.linalg.norm(d, axis=1, keepdims=True)
            sp = 0.7 + 0.6 * s[:, 3]
            dist = (2.0 * u + 10.0 * u * u) * sp
            dist2 = (2.0 * np.maximum(u - 0.07, 0) + 10.0 * np.maximum(u - 0.07, 0) ** 2) * sp
            sw = 0.25 * np.stack([np.sin(3.0 * u + 9 * s[:, 0]), np.zeros(len(s)), np.cos(3.0 * u + 9 * s[:, 1])], 1)
            P = c + d * dist[:, None] + sw
            Q = c + d * dist2[:, None] + sw
            f = np.exp(-u / 1.8) * _sc(0.0, 0.05, u)
            out.append(dict(pos=P, pos2=Q, size=0.03, color=pale, alpha=0.5 * f, emit=2.6, kind="line"))
            out.append(dict(pos=P, size=0.06, color=pale, alpha=f, emit=3.4, kind="spark", twinkle=0.6, seed=s[:, 3]))
        f = np.exp(-u / 0.35)
        out.append(dict(pos=KINGS_STOP + _v(0.0, 0.3, -0.85), size=1.6, color=gold, alpha=0.5 * f, emit=2.4,
                        kind="soft"))
        return out


SHAFTS = [
    # Mother's light: a soft shaft from above onto the sea where she leads
    dict(base=lambda t: (0.0, float(mother_pos(t)[2])), radius=3.5, top=140.0, spread=-0.5, color="#ffe9c8",
         strength=lambda t: proc_k(t) * _sc(LAND - 0.5, LAND + 1.5, t) * (0.10 + 0.06 * gather_k(t))),
]


def add(scene):
    look = dict(color="#fff0dc", color2="#dce8ff", bright=3.2, size=1.35, points=420, seed=21.0)
    scene.add("mother", MotherLight())
    scene.add("gather", Gather())
    wait = GCrowd(gain=proc_k, places=PROC_P, facing=180.0, kinds=("stand",), start=ARRIVE, until=MARCH,
                  fade=0.3, flash=1.4, **look)
    walkers = GCrowd(gain=proc_k, places=PROC_P, facing=180.0, kinds=("walk",), start=MARCH, walk=WALK,
                     until=HALT, fade=0.3, flash=0.0, **look)
    wait.facing[:] = walkers.facing
    held = GCrowd(gain=proc_k, places=PROC_P + _ahead(walkers) * walked(HALT), facing=180.0, kinds=("stand",),
                  start=HALT - 0.3, fade=0.3, flash=0.0, **look)
    held.facing[:] = walkers.facing
    scene.add("procession wait", wait)
    scene.add("procession", walkers)
    scene.add("procession held", held)
    scene.add("fulfil hearts", FulfilHearts(walkers))
    king = dict(people=dict(man=1.0), color=GOLD, color2=GOLD2, bright=2.1, points=1300, seed=31.0)
    kings_w = _robed(GCrowd(gain=proc_k, places=KINGS_P, facing=180.0, kinds=("walk",), start=K_IN, walk=WALK,
                            until=K_STOP, fade=0.25, flash=1.2, **king))
    kings_k = _robed(GCrowd(gain=proc_k, places=KINGS_STOP, facing=180.0, kinds=("kneel",), start=K_STOP - 0.25,
                            act=dict(t=KNEEL, dur=0.3), fade=0.25, flash=0.0, **king))
    scene.add("kings", kings_w)
    scene.add("kings kneel", kings_k)
    scene.add("crowns", Crowns(kings_w, kings_k))
