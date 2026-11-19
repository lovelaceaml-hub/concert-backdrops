"""Song 11 v2: from thanks to Mother to the end: hearts rising, light gathering at the horizon, the
sun rising over Zion, the orchestra on clouds of light, everyone on the summit, the world finale on the Earth, the
held breath, the last chord and the end card's Earth.

Owned by the coda thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
from songs.s11_stage import Instruments, ORCH_P  # noqa: E402

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

SHOTS = [
    # thanks to Mother: hearts rise; the last build: light gathers at the horizon behind Zion
    dict(name="hearts_rise", kind="local", t0=188.27, t1=201.73, fov=52.0, aperture=0.0,
         keys=[(188.27, _v(30.0, 80.0, -140.0), ZC + _v(0.0, Y + 8.0, 0.0)),
                          (201.73, _v(10.0, 60.0, -40.0), ZC + _v(0.0, Y + 14.0, -60.0))]),
    # the coda: the sun rises over Mount Zion
    dict(name="sunrise", kind="local", t0=201.73, t1=205.98, fov=54.0, aperture=0.0,
         keys=[(201.73, _v(0.0, 22.0, 120.0), ZC + _v(0.0, Y + 14.0, -40.0)),
                          (205.98, _v(0.0, 26.0, 100.0), ZC + _v(0.0, Y + 18.0, -40.0))]),
    # the orchestra on clouds of light round the rising sun
    dict(name="sky_stage", kind="sky", t0=205.98, t1=211.6, fov=50.0, aperture=0.0,
         keys=[(205.98, SKY_STAGE + _v(0.0, 4.0, 46.0), SKY_STAGE + _v(0.0, 6.0, -20.0)),
                         (211.6, SKY_STAGE + _v(0.0, 6.0, 38.0), SKY_STAGE + _v(0.0, 7.0, -20.0))]),
    # third climb: the summit, everyone, the church of light, the sun
    dict(name="summit", kind="local", t0=211.6, t1=224.03, fov=54.0, aperture=0.0,
         keys=[(211.6, _v(30.0, Y + 4.0, FZ + 80.0), _v(0.0, Y + 20.0, CHURCH[2])),
                         (224.03, _v(8.0, Y + 6.0, FZ + 56.0), _v(0.0, Y + 24.0, CHURCH[2]))]),
    # the world finale
    dict(name="earth_finale", kind="globe", t0=224.03, t1=238.8, fov=48.0, aperture=0.0,
         keys=[(224.03, _gcam(150.0, 30.0), G + _v(0, 10, 0)), (238.8, _gcam(170.0, 8.0), G + _v(0, 12, 0))]),
    # the last chord: out to the whole Earth glowing, the end card
    dict(name="earth_end", kind="globe", t0=254.07, t1=TOTAL + 1.0, fov=46.0, aperture=0.0,
         keys=[(254.07, _gcam(150.0, 6.0), G), (TOTAL + 1.0, _gcam(185.0, 8.0), G)]),
]


class RisingHearts:
    """Thanks to Mother (3:09.5 to 3:17): hearts in the nine colours rise from everyone on the mountain."""
    wants_camera = True

    def __init__(self):
        r = np.random.default_rng(121)
        n = 220
        k = r.integers(0, N_TIER, n)
        a = np.radians(r.uniform(-75.0, 75.0, n))
        rr = np.asarray([tier_r(i) - 3.0 - 20.0 * r.random() for i in k])
        self.p0 = np.stack([ZC[0] + rr * np.sin(a), np.asarray([tier_y(i) for i in k]) + 2.0, ZC[2] + rr * np.cos(a)], 1)
        self.t0 = 189.5 + 7.0 * r.random(n)
        self.sz = 2.2 + 2.6 * r.random(n)
        self.v = 5.0 + 4.0 * r.random(n)
        self.col = np.asarray([lin(COL9[i % 9]) for i in range(n)])
        from p3d.brand_hearts import heart_points
        self.h = heart_points(36)
        self.ph = r.random(n) * 6.0

    def sample(self, t, cam=None):
        if cam is None or local_k(t) <= 0.0 or not (189.0 <= t < 202.0) or shot_name(t) != "hearts_rise":
            return None
        u = t - self.t0
        on = u > 0.0
        if not on.any():
            return None
        rgt, up, _f = cam.basis()
        u = u[on]
        c = self.p0[on] + up[None, :] * 0.0 + _v(0.0, 1.0, 0.0) * (self.v[on] * u)[:, None]
        c = c + rgt[None, :] * (1.5 * np.sin(0.9 * u + self.ph[on]))[:, None]
        a = _sc(0.0, 0.5, u) * (1.0 - _sc(5.0, 9.0, u)) * (1.0 - _sc(200.5, 201.7, t))
        sz = self.sz[on]
        hx, hy = self.h[:, 0], self.h[:, 1]
        P = (c[:, None, :] + sz[:, None, None] * (hx[None, :, None] * rgt[None, None, :] + hy[None, :, None] * up[None, None, :]))
        m = len(self.h)
        return [dict(pos=P.reshape(-1, 3), size=np.repeat(0.09 * sz, m), color=np.repeat(self.col[on], m, axis=0),
                     alpha=np.repeat(a, m), emit=3.0, kind="spark"),
                dict(pos=c, size=2.2 * sz, color=self.col[on], alpha=0.18 * a, emit=1.6, kind="soft")]


class Horizon:
    """The last build (3:17.2 to 3:21.7): light gathers along the horizon behind Zion, where the sun will rise."""

    def __init__(self):
        r = np.random.default_rng(131)
        n = 3000
        a = np.radians(163.0 + r.normal(0.0, 22.0, n))
        d = 2600.0 + 300.0 * r.random(n)
        self.P = np.stack([d * np.sin(a), 4.0 + 50.0 * r.random(n) ** 3, d * np.cos(a)], 1)
        self.s = r.random(n)

    def sample(self, t):
        if local_k(t) <= 0.0 or not (195.0 <= t < 206.0) or stage_view(t):
            return None
        k = _sc(196.5, 201.6, t) * (1.0 - 0.6 * _sc(202.0, 206.0, t))
        return [dict(pos=self.P, size=7.0, color=lin("#ffd29a"), alpha=0.35 * k, emit=2.0, kind="soft", dof=0.0),
                dict(pos=self.P[::3], size=2.2, color=lin("#fff0d0"), alpha=0.7 * k, emit=3.0, kind="spark",
                     twinkle=0.6, seed=self.s[::3], dof=0.0)]


SKY_OFF = SKY_STAGE - SQUARE


def sky_k(t):
    return 1.0 if shot_kind(t) == "sky" else 0.0


class Clouds:
    """The clouds of light the orchestra plays on, round the rising sun (the coda)."""

    def __init__(self):
        r = np.random.default_rng(141)
        n = 9000
        a = 2 * np.pi * r.random(n)
        rr = 60.0 * np.sqrt(r.random(n))
        self.P = np.stack([SKY_STAGE[0] + rr * np.sin(a) * 1.4, SKY_STAGE[1] - 0.6 - 2.5 * r.random(n) ** 2,
                           SKY_STAGE[2] + rr * np.cos(a) * 0.8 - 10.0], 1)
        self.s = r.random(n)
        m = 2500
        a = 2 * np.pi * r.random(m)
        rr = 120.0 + 260.0 * r.random(m)
        self.F = np.stack([SKY_STAGE[0] + rr * np.sin(a), SKY_STAGE[1] - 20.0 - 40.0 * r.random(m),
                           SKY_STAGE[2] + rr * np.cos(a)], 1)

    def sample(self, t):
        if sky_k(t) <= 0.0:
            return None
        drift = _v(0.4 * np.sin(0.2 * t), 0.0, 0.0)
        return [dict(pos=self.P + drift, size=1.4 + 1.6 * self.s, color=lin("#ffe4c6"), alpha=0.16, emit=1.2,
                     kind="soft", seed=self.s),
                dict(pos=self.P[::4], size=0.06, color=lin(WHITE), alpha=0.6, emit=2.2, kind="spark", twinkle=0.8,
                     seed=self.s[::4]),
                dict(pos=self.F, size=14.0, color=lin("#f6c9a8"), alpha=0.10, emit=1.0, kind="soft")]


def summit_k(t):
    """Everyone on the summit: from the coda's sunrise to the last chord (not in the close stage shots)."""
    if globe_view(t) or not (201.73 <= t < 254.07):
        return 0.0
    return 1.0


def _summit_places(n=700, seed=151):
    r = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        x = r.uniform(-60.0, 60.0)
        z = r.uniform(FACADE_Z + 22.0, FACADE_Z + 74.0)
        if abs(x) < 9.0 or np.hypot(x - ZC[0], z - ZC[2]) > R_TOP - 3.0:
            continue
        pts.append((x, SUMMIT, z))
    return np.asarray(pts)


class Gather:
    """The held breath (4:07.5 to 4:09.5): sparks gather above the choir, then open on the final rise."""

    def __init__(self):
        r = np.random.default_rng(161)
        n = 1600
        d = r.normal(0.0, 1.0, (n, 3))
        self.d = d / np.linalg.norm(d, axis=1, keepdims=True)
        self.r = 8.0 + 22.0 * r.random(n)
        self.s = r.random(n)
        self.c = _v(0.0, SUMMIT + 10.0, FACADE_Z + 2.0)

    def sample(self, t):
        if not (245.5 <= t < 252.0) or local_k(t) <= 0.0:
            return None
        if t < HIT["final"]:
            u = _sc(245.5, HIT["final"], t)
            rr = self.r * (1.0 - 0.94 * u)
            a = _sc(245.5, 246.5, t) * (0.6 + 0.4 * u)
        else:
            u = t - HIT["final"]
            rr = self.r * (0.06 + 0.6 * u)
            a = np.exp(-u / 0.9)
        P = self.c + self.d * rr[:, None]
        return dict(pos=P, size=0.10, color=lin("#ffe9c0"), alpha=a, emit=3.5, kind="spark", twinkle=0.7, seed=self.s)


SHAFTS = []


def add(scene):
    scene.add("rising hearts", RisingHearts())
    scene.add("horizon", Horizon())
    # the orchestra on clouds of light round the rising sun
    scene.add("clouds", Clouds())
    scene.add("sky orchestra", GCrowd(gain=sky_k, places=ORCH_P + SKY_OFF, facing=0.0, kinds=("sit",),
                                      people=dict(woman=1.0, man=1.0), start=0.0, color=CRYSTAL, color2="#ffffff",
                                      bright=1.3, points=1600, glints=0.006, seed=4.0))
    scene.add("sky instruments", Instruments(offset=SKY_OFF, gain=sky_k))
    # everyone on the summit, from the coda's sunrise to the last chord
    scene.add("summit", GCrowd(gain=summit_k, places=_summit_places(), facing=0.0,
                               kinds=(("raise", 2.0), ("stand", 2.0), ("cheer", 1.0)),
                               people=dict(woman=1.0, man=1.0, child=0.2),
                               start=dict(t=201.0, center=(0.0, FACADE_Z), speed=40.0), color="#ffc870",
                               color2="#fff2d8", bright=1.5, points=500, seed=41.0))
    scene.add("gather", Gather())
