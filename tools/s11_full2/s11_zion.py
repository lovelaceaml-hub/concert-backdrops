"""Song 11 v2: Mount Zion, a terraced mountain of light: the terraces filling with gold, the crown of
light, the nations standing on it, light pouring down, the column of light to heaven, rings of light over the land.

Owned by the zion thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

SHOTS = [
    # C. high over Mount Zion: the crown of light; the city fills with gold
    dict(name="zion_crown", kind="local", t0=53.78, t1=70.54, fov=50.0, aperture=0.0,
         keys=[(53.78, ZC + _v(160.0, 140.0, 420.0), ZC + _v(0.0, Y + 22.0, 0.0)),
                        (70.54, ZC + _v(110.0, 120.0, 360.0), ZC + _v(0.0, Y + 16.0, 0.0))]),
    # waves of praise: the whole land ripples with light
    dict(name="praise_ripples", kind="local", t0=86.70, t1=90.72, fov=48.0, aperture=0.0,
         keys=[(86.70, _v(0.0, 24.0, 160.0), ZC + _v(0.0, 40.0, 0.0)),
                        (90.72, _v(0.0, 26.0, 140.0), ZC + _v(0.0, 42.0, 0.0))]),
    # first climb: Mount Zion wide, the nations standing on it; sacrifice, devotion, thanks
    dict(name="zion_wide", kind="local", t0=90.72, t1=117.0, fov=50.0, aperture=0.0,
         keys=[(90.72, _v(0.0, 105.0, 120.0), ZC + _v(0.0, 38.0, 20.0)),
                        (117.0, _v(0.0, 118.0, 20.0), ZC + _v(0.0, 46.0, 0.0))]),
    # the shockwave across the land; second climb: the whole mountain full of people
    dict(name="zion_full", kind="local", t0=165.16, t1=185.92, fov=52.0, aperture=0.0,
         keys=[(165.16, _v(0.0, 40.0, 60.0), ZC + _v(0.0, 46.0, 0.0)),
                          (170.0, _v(20.0, 60.0, -60.0), ZC + _v(0.0, 52.0, 0.0)),
                          (185.92, _v(40.0, 84.0, -150.0), ZC + _v(0.0, Y + 6.0, 0.0))]),
]


FILL_T = [64.2, 64.2, 64.2, 65.94, 65.94, 69.4, 69.4]     # "being fulfilled": the terraces fill with gold


def _mountain():
    r = np.random.default_rng(7)
    rings, walls, gardens, birth_r, birth_g = [], [], [], [], []
    for k in range(N_TIER):
        R0, y = tier_r(k), tier_y(k)
        y0 = tier_y(k - 1) if k > 0 else 0.0
        e = _ring(ZC, R0, y, 0.55)
        rings.append(e)
        birth_r.append(np.full(len(e), FILL_T[k]))
        n = int(R0 * 70)
        a = r.random(n) * 2 * np.pi
        hh = y - (y - y0) * r.random(n) ** 1.8
        walls.append(np.stack([ZC[0] + R0 * np.sin(a), hh, ZC[2] + R0 * np.cos(a)], 1))
        Ri = tier_r(k + 1) if k < N_TIER - 1 else 0.0
        m = int((R0 ** 2 - Ri ** 2) * 0.012) + 200
        a = r.random(m) * 2 * np.pi
        rr = np.sqrt(Ri ** 2 + (R0 ** 2 - Ri ** 2) * r.random(m))
        g = np.stack([ZC[0] + rr * np.sin(a), np.full(m, y + 0.4) + 0.8 * r.random(m), ZC[2] + rr * np.cos(a)], 1)
        if k == N_TIER - 1:
            g = g[np.hypot(g[:, 0] - ZC[0], g[:, 2] - ZC[2]) > 80.0]
        gardens.append(g)
        birth_g.append(np.full(len(g), FILL_T[k] + 0.25))
    # the great stairs down the front of the mountain (toward +z), one flight per terrace
    stairs = []
    for k in range(N_TIER - 1):
        za, zb = ZC[2] + tier_r(k + 1), ZC[2] + tier_r(k)
        ya, yb = tier_y(k + 1), tier_y(k)
        for s in range(10):
            u = (s + 0.5) / 10
            stairs.append(_seg((-7.0, ya + (yb - ya) * u, za + (zb - za) * u), (7.0, ya + (yb - ya) * u, za + (zb - za) * u), 0.5))
    stairs = np.concatenate(stairs)
    R_, W_, G_ = np.concatenate(rings), np.concatenate(walls), np.concatenate(gardens)
    dim = [
        _batch(R_, 0.75, lin("#e8b860") * 0.55, 0.85, emit=1.4, twinkle=0.3),
        _batch(W_, 0.65, lin("#d8a868") * 0.45, 0.6, kind="soft", emit=1.0),
        _batch(G_, 0.70, lin("#ffd9a0") * 0.45, 0.7, emit=1.2, twinkle=0.5),
        _batch(stairs, 0.22, lin(GOLD2) * 0.6, 0.8, emit=1.2),
    ]
    gold = [
        _batch(R_, 0.95, lin(GOLD), 1.0, emit=2.2, birth=np.concatenate(birth_r), fade=0.5, flash=4.0, twinkle=0.5),
        _batch(G_, 0.85, lin("#ffe2a0"), 0.9, emit=1.8, birth=np.concatenate(birth_g), fade=0.7, flash=3.0,
               twinkle=0.6),
    ]
    return dim, gold


class Crown:
    """The crown of light that ignites over the city on "The glory of Jerusalem Mother shines!" (0:53.78)."""

    def __init__(self):
        r = np.random.default_rng(31)
        pts, base = [], []
        top = ZC + _v(0.0, SUMMIT + 66.0, 0.0)
        for k in range(28):
            a = 2 * np.pi * k / 28
            rr = 70.0
            b = top + _v(rr * np.sin(a), 0.0, rr * np.cos(a))
            h = 34.0 if k % 2 == 0 else 20.0
            tip = b + _v(0.0, h, 0.0) + _v(-np.sin(a), 0.0, -np.cos(a)) * 6.0
            pts.append(_seg(b, tip, 0.35))
            nb = top + _v(rr * np.sin(a + np.pi / 28), 0.0, rr * np.cos(a + np.pi / 28))
            pts.append(_seg(tip, nb + _v(0.0, 4.0, 0.0), 0.35))
        pts.append(_ring(top, 70.0, top[1], 0.4))
        self.P = np.concatenate(pts)
        self.d = (self.P[:, 1] - top[1]) / 34.0
        self.s = r.random(len(self.P))

    def sample(self, t):
        if not (53.0 <= t < 71.0) or globe_view(t):
            return None
        u = t - HIT["glory"]
        grow = np.clip(u / 0.9 - self.d, 0.0, 1.0)
        a = grow * (0.55 + 0.45 * np.exp(-max(u, 0.0) / 2.5)) * (1.0 - _sc(69.4, 70.5, t))
        return dict(pos=self.P, size=0.9, color=lin("#ffe7b0"), alpha=a, emit=3.5 + 4.0 * np.exp(-max(u, 0) / 0.6),
                    kind="spark", twinkle=0.6, seed=self.s)


def _terrace_rows(tiers, rows=2, spacing=1.3, arc=65.0, seed=41):
    """People along the front edge of the terraces (the side that faces the sea and the camera)."""
    r = np.random.default_rng(seed)
    pts = []
    for k in tiers:
        for j in range(rows):
            R0 = tier_r(k) - 2.0 - 1.6 * j
            n = int(R0 * np.radians(2 * arc) / spacing)
            a = np.radians(np.linspace(-arc, arc, n)) + r.uniform(-0.002, 0.002, n)
            pts.append(np.stack([ZC[0] + R0 * np.sin(a), np.full(n, tier_y(k)), ZC[2] + R0 * np.cos(a)], 1))
    return np.concatenate(pts)


def _terrace_glow(tiers, n_per, t0, seed):
    """The vast crowds further back on each terrace: a glitter of many small lights in the nine colours and
    gold (born tier by tier, from the top down)."""
    r = np.random.default_rng(seed)
    P, C, B = [], [], []
    for k in tiers:
        R0, Ri = tier_r(k) - 5.0, (tier_r(k + 1) if k < N_TIER - 1 else 34.0)
        a = np.radians(r.uniform(-80.0, 80.0, n_per))
        rr = np.sqrt(Ri ** 2 + (R0 ** 2 - Ri ** 2) * r.random(n_per))
        p = np.stack([ZC[0] + rr * np.sin(a), tier_y(k) + 0.9 + 0.7 * r.random(n_per), ZC[2] + rr * np.cos(a)], 1)
        if k == N_TIER - 1:
            keep = (np.abs(p[:, 0]) > 30.0) | (p[:, 2] < CHURCH[2] - 20.0)
            p = p[keep]
        m = len(p)
        c = np.where(r.random(m)[:, None] < 0.35, np.asarray([lin(COL9[i % 9]) for i in r.integers(0, 9, m)]),
                     lin("#ffd9a0")[None, :])
        P.append(p)
        C.append(c)
        B.append(t0 + 0.35 * (N_TIER - 1 - k) + 0.4 * r.random(m))
    P, C, B = np.concatenate(P), np.concatenate(C), np.concatenate(B)
    return [_batch(P, 0.55, C, 0.8, emit=1.6, birth=B, fade=0.8, flash=2.0, twinkle=0.8)]


def nations_k(t):
    """The nations on Zion: on from the first climb, in every view of the mountain (not the stage cut-ins'
    blur is enough there)."""
    return local_k(t) * _sc(89.0, 90.72, t) if t < 254.07 else 0.0


class Pour:
    """Streaks of light falling on Zion (1:39.4 to 1:49.4) and the column of sparks rising to heaven (1:49.8)."""

    def __init__(self):
        r = np.random.default_rng(91)
        self.f = r.random((1200, 4))
        self.c = r.random((1800, 4))

    def sample(self, t):
        if local_k(t) <= 0.0 or shot_name(t) != "zion_wide":
            return None
        out = []
        k = _env(t, 99.0, 110.0, 1.0, 1.5) * (0.6 + 0.4 * loud(t))
        if k > 0.0:
            s = self.f
            a = 2 * np.pi * s[:, 0]
            rr = 240.0 * np.sqrt(s[:, 1])
            y = 420.0 - np.mod(t * 60.0 * (0.7 + 0.6 * s[:, 2]) + 600.0 * s[:, 3], 420.0)
            p = np.stack([ZC[0] + rr * np.sin(a), y + SUMMIT * 0.5, ZC[2] + rr * np.cos(a)], 1)
            out.append(dict(pos=p, pos2=p + _v(0.0, 5.0, 0.0), size=0.12, color=lin("#ffdca0"), alpha=0.35 * k,
                            emit=1.6, kind="line"))
        k = _env(t, 109.8, 117.0, 1.0, 0.3)
        if k > 0.0:
            s = self.c
            a = 2 * np.pi * s[:, 0]
            rr = 12.0 * np.sqrt(s[:, 1])
            y = CHURCH[1] + np.mod((t - 109.8) * 90.0 * (0.6 + 0.8 * s[:, 2]) + 900.0 * s[:, 3], 900.0)
            p = np.stack([CHURCH[0] + rr * np.sin(a), y, CHURCH[2] + rr * np.cos(a)], 1)
            out.append(dict(pos=p, size=0.9, color=lin("#fff4dc"), alpha=k, emit=3.0, kind="spark", twinkle=0.6,
                            seed=s[:, 3]))
        return out or None


RINGS = [(86.70, 90.0, 0.6), (88.0, 90.0, 0.45), (89.3, 90.0, 0.35),        # waves of praise ripple the land
         (162.86, 75.0, 1.0), (165.16, 70.0, 0.7), (171.48, 70.0, 0.6)]    # the shockwave of the second slam


class Rings:
    """Rings of light rolling out over the land and the sea from the foot of Mount Zion."""

    def __init__(self):
        a = np.linspace(0, 2 * np.pi, 5000, endpoint=False)
        self.cs = np.stack([np.sin(a), np.cos(a)], 1)
        self.s = np.random.default_rng(111).random(5000)

    def sample(self, t):
        if local_k(t) <= 0.0 or stage_view(t):
            return None
        out = []
        for t0, v, k in RINGS:
            u = t - t0
            if not (0.0 <= u < 9.0):
                continue
            r = tier_r(0) + v * u
            p = np.stack([ZC[0] + r * self.cs[:, 0], np.full(len(self.cs), 0.35), ZC[2] + r * self.cs[:, 1]], 1)
            a = k * np.exp(-u / 3.5) * _sc(0.0, 0.2, u)
            out.append(dict(pos=p, size=0.9 + 0.08 * u, color=lin("#ffe2b0"), alpha=a, emit=2.6, kind="spark",
                            twinkle=0.4, seed=self.s))
            out.append(dict(pos=p[::5], size=6.0, color=lin("#ffcf8a"), alpha=0.10 * a, emit=1.5, kind="soft"))
        return out or None


SHAFTS = [
    # "sacrifice / devotion" (1:39.4 to 1:49.4): light pours down over the people on Zion
    dict(base=(float(ZC[0]), float(ZC[2]) + 40.0), radius=110.0, top=900.0, spread=-0.4, color="#ffe6bf",
         strength=lambda t: local_k(t) * (shot_name(t) == "zion_wide") * _env(t, 99.0, 110.0, 1.5, 1.5) * 0.004),
    # thanks to Father (1:49.8 to 1:57): a column of light rises from the church to heaven
    dict(base=(float(CHURCH[0]), float(CHURCH[2])), radius=16.0, top=3000.0, spread=-0.2, color="#fff2d8",
         strength=lambda t: local_k(t) * (shot_name(t) == "zion_wide") * _env(t, 109.8, 117.0, 1.2, 0.3) * 0.06),
]


def add(scene):
    dim, gold = _mountain()
    scene.add("zion dim", Static(dim, local_k))
    scene.add("zion gold", Static(gold, local_k))
    scene.add("crown", Crown())
    # the nations on Mount Zion: the upper terraces from the first climb (1:30.7), the whole mountain from 2:51.5
    scene.add("nations glow 1", Static(_terrace_glow(range(2, N_TIER), 2600, 90.0, 171), nations_k))
    scene.add("nations glow 2", Static(_terrace_glow(range(0, 2), 2600, 170.9, 172), nations_k))
    scene.add("nations 1", GCrowd(gain=nations_k, places=_terrace_rows(range(2, N_TIER)), facing="out",
                                  kinds=(("stand", 3.0), ("raise", 1.0)), people=dict(woman=1.0, man=1.0),
                                  start=dict(t=89.6, center=(ZC[0], ZC[2]), speed=80.0), color="#ffcf7a",
                                  color2="#fff0d0", bright=1.6, points=120, flash=1.5, seed=11.0))
    scene.add("nations 2", GCrowd(gain=nations_k, places=_terrace_rows(range(0, 2), seed=42), facing="out",
                                  kinds=(("stand", 3.0), ("raise", 1.0)), people=dict(woman=1.0, man=1.0),
                                  start=dict(t=168.3, center=(ZC[0], ZC[2]), speed=80.0), color="#ffcf7a",
                                  color2="#fff0d0", bright=1.6, points=120, flash=1.5, seed=12.0))
    scene.add("pour", Pour())
    scene.add("rings", Rings())
