"""Song 11 v2: Mother as light alone leading everyone across the sea of glass toward Zion (2:05.9),
the march (2:14.54), hearts lighting in the walkers on fulfilled, the kings laying down their crowns.

Owned by the procession thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

SHOTS = [
    # Mother's light leads everyone across the sea of glass toward Mount Zion; the kings; the held breath
    dict(name="procession", kind="local", t0=125.92, t1=162.86, fov=50.0, aperture=0.0,
         keys=[(125.92, _v(-20.0, 7.0, 150.0), ZC + _v(0.0, 40.0, 0.0)),
                          (150.0, _v(-6.0, 9.0, 40.0), ZC + _v(0.0, 42.0, 0.0)),
                          (156.0, _v(-2.0, 10.0, 18.0), ZC + _v(0.0, 45.0, 0.0)),
                          (162.86, _v(0.0, 11.0, 14.0), ZC + _v(0.0, 46.0, 0.0))]),
]


MOTHER_Z0 = -55.0          # where Mother's light comes down on the sea, ahead of everyone
WALK = 1.3                 # metres per second toward Zion, from "march ahead" (2:14.54)


def mother_pos(t):
    z = MOTHER_Z0 - WALK * max(t - HIT["march"], 0.0)
    return _v(0.0, 5.5 + 0.25 * np.sin(1.3 * t), z)


def _proc_places(n=900, seed=51):
    r = np.random.default_rng(seed)
    side = np.where(r.random(n) < 0.5, -1.0, 1.0)
    z = MOTHER_Z0 + 8.0 + 150.0 * r.random(n) ** 0.9
    fan = 0.55 + 0.45 * (z - MOTHER_Z0) / 158.0          # the column fans out behind Mother's light
    x = side * (4.5 + 22.0 * fan * r.random(n) ** 1.2)   # an aisle down the middle (the kings kneel in it)
    return np.stack([x, np.zeros(n), z], 1)


PROC_P = _proc_places()


def proc_k(t):
    return local_k(t) if 125.92 <= t < 162.86 and shot_name(t) == "procession" else 0.0


class MotherLight:
    """Mother as light alone (no figure): a light that comes down on the sea at 2:05.9, everyone gathers behind
    it, and it leads them toward Zion from "march ahead"."""

    def __init__(self):
        r = np.random.default_rng(61)
        self.s = r.random((500, 4))

    def sample(self, t):
        k = proc_k(t) * _sc(125.92, 127.5, t)
        if k <= 0.0:
            return None
        m = mother_pos(t)
        pulse = 1.0 + 0.6 * hit_pulse(t, [HIT["march"]] + FULFIL, fall=0.8) + 0.2 * beat_pulse(t)
        s = self.s
        # a slow halo of sparks round the light, and a trail on the sea behind it
        ang = 2 * np.pi * s[:, 0] + 0.4 * t * (0.5 + s[:, 1])
        rad = 1.2 + 2.6 * s[:, 2]
        halo = m[None, :] + np.stack([rad * np.cos(ang), 1.6 * (s[:, 3] - 0.5) * rad, rad * np.sin(ang)], 1)
        return [dict(pos=m[None, :], size=9.0, color=lin("#ffe8c4"), alpha=0.30 * k * pulse, kind="soft", emit=2.0),
                dict(pos=m[None, :], size=2.4, color=lin(WHITE), alpha=0.9 * k, kind="soft", emit=4.0),
                dict(pos=m[None, :], size=0.6, color=lin(WHITE), alpha=k, kind="spark", emit=8.0 * pulse),
                dict(pos=halo, size=0.08, color=lin("#ffe6b8"), alpha=0.8 * k, kind="spark", emit=3.0, twinkle=0.8,
                     seed=s[:, 0])]


class FulfilHearts:
    """Verse 2 "fulfilled" (2:24.4 to 2:30.2): on each accent of the quickening heartbeat, hearts light up in
    the people walking behind Mother's light, in the nine colours."""

    def __init__(self, walkers):
        self.w = walkers
        r = np.random.default_rng(71)
        n = len(walkers.place)
        self.when = np.asarray(FULFIL)[r.integers(0, len(FULFIL), n)] + r.uniform(0.0, 0.12, n)
        self.col = np.asarray([lin(COL9[i]) for i in r.integers(0, 9, n)])
        from p3d.brand_hearts import heart_points
        self.h = heart_points(22)

    def sample(self, t):
        if proc_k(t) <= 0.0 or t < FULFIL[0] - 0.1:
            return None
        w = self.w
        age = np.maximum(t - w.start, 0.0)
        base = w.place + np.stack([np.sin(w.facing), np.zeros(len(w.place)), np.cos(w.facing)], 1) * (w.walk * age)[:, None]
        on = t >= self.when
        if not on.any():
            return None
        u = t - self.when[on]
        a = np.clip(u / 0.15, 0.0, 1.0) * (0.55 + 0.45 * np.exp(-u / 0.5))
        c = base[on] + _v(0.0, 1.30, 0.0)
        hs = 0.20
        hx = self.h[:, 0] * hs
        hy = self.h[:, 1] * hs
        P = c[:, None, :] + np.stack([hx, hy, np.zeros_like(hx)], 1)[None, :, :]
        cols = np.repeat(self.col[on], len(self.h), axis=0)
        return [dict(pos=P.reshape(-1, 3), size=0.035, color=cols, alpha=np.repeat(a, len(self.h)), emit=3.0,
                     kind="spark"),
                dict(pos=c, size=0.6, color=self.col[on], alpha=0.35 * a, emit=2.0, kind="soft")]


KINGS_P = np.asarray([(x, 0.0, -4.0 - 0.5 * abs(x)) for x in (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)])


class Crowns:
    """The kings lay down their crowns (2:34.2): the crowns go down with them as they kneel, then rise as
    sparks toward Zion on 2:35.34."""

    def __init__(self, kings):
        self.k = kings
        r = np.random.default_rng(81)
        a = np.linspace(0, 2 * np.pi, 28, endpoint=False)
        ring = np.stack([0.13 * np.cos(a), np.zeros(28), 0.13 * np.sin(a)], 1)
        tips = []
        for i in range(7):
            b = 2 * np.pi * i / 7
            tips.append(_seg(_v(0.13 * np.cos(b), 0.0, 0.13 * np.sin(b)), _v(0.13 * np.cos(b), 0.12, 0.13 * np.sin(b)),
                             0.02))
        self.C = np.concatenate([ring, ring + _v(0, 0.04, 0)] + tips)
        self.s = r.random((len(KINGS_P), 140, 4))

    def sample(self, t):
        if proc_k(t) <= 0.0 or not (149.0 <= t < 162.0):
            return None
        out = []
        down = _sc(HIT["kings1"], HIT["kings1"] + 1.5, t)
        head = 1.86 - 0.55 * down
        rise = t - HIT["kings2"]
        for i, p in enumerate(KINGS_P):
            a = _sc(149.0, 150.2, t)
            if rise < 0.0:
                c = p + _v(0.0, head, 0.0)
                out.append(dict(pos=self.C + c, size=0.04, color=lin(GOLD), alpha=a, emit=3.5, kind="spark"))
                out.append(dict(pos=c[None, :], size=0.5, color=lin(GOLD), alpha=0.25 * a, emit=2.0, kind="soft"))
            else:
                s = self.s[i]
                d = np.stack([s[:, 0] - 0.5, 0.6 + s[:, 1], -(0.3 + s[:, 2])], 1)
                P = p + _v(0.0, head, 0.0) + d * (0.4 + 4.5 * rise * (0.6 + 0.4 * s[:, 3]))[:, None]
                f = np.exp(-rise / 2.5)
                out.append(dict(pos=P, size=0.05, color=lin("#ffe2a0"), alpha=f, emit=3.5, kind="spark",
                                twinkle=0.8, seed=s[:, 3]))
        return out


SHAFTS = [
    # Mother's light: a soft shaft from above onto the sea where she leads
    dict(base=lambda t: (0.0, float(mother_pos(t)[2])), radius=4.0, top=140.0, spread=-0.5, color="#ffe9c8",
         strength=lambda t: proc_k(t) * _sc(125.92, 128.0, t) * 0.12),
]


def add(scene):
    scene.add("mother", MotherLight())
    gather_ = dict(t=125.6, center=(0.0, MOTHER_Z0), speed=22.0)
    scene.add("procession wait", GCrowd(gain=proc_k, places=PROC_P, facing=180.0, kinds=("stand",),
                                        start=gather_, until=HIT["march"], fade=0.25, color=CRYSTAL,
                                        color2="#ffe6c0", bright=1.5, points=500, seed=21.0))
    walkers = GCrowd(gain=proc_k, places=PROC_P, facing=180.0, kinds=("walk",), start=HIT["march"], walk=WALK,
                     fade=0.25, flash=0.0, color=CRYSTAL, color2="#ffe6c0", bright=1.5, points=500, seed=21.0)
    scene.add("procession", walkers)
    scene.add("fulfil hearts", FulfilHearts(walkers))
    kings = GCrowd(gain=proc_k, places=KINGS_P, facing=180.0, kinds=("kneel",), people=dict(woman=1.0, man=1.0),
                   start=149.0, act=dict(t=HIT["kings1"], dur=0.4), color=GOLD, color2="#fff0c8", bright=2.0,
                   points=1400, seed=31.0)
    scene.add("kings", kings)
    scene.add("crowns", Crowns(kings))
