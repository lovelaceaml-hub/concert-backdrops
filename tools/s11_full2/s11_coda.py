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

# Two leftovers of the base song (songs.s03_original) show over the world finale: its title words ("Beginning of
# Peace / The Words of Mother's Love", formed at 3:45.9 and held) and its tagline (3:56 to 4:00.5). The core
# should switch them off (TITLE form/hold and TAGLINE t0/t1 to 1e9); until it does, they are switched off here.
import songs.s03_original as _B  # noqa: E402
for _d, _ks in ((_B.TITLE, ("form", "hold", "star")), (_B.TAGLINE, ("t0", "t1"))):
    for _k in _ks:
        if _k in _d:
            _d[_k] = 1e9 + (1.0 if _k in ("hold", "t1") else 0.0)

SKY_C = SKY_STAGE + _v(0.0, 1.0, -5.0)       # the middle of the sky orchestra

def _orb(c, r, az, h):
    """A camera place on a circle round c: radius r, azimuth az (degrees, from +z toward +x), height h above c."""
    a = np.radians(az)
    return c + _v(r * np.sin(a), h, r * np.cos(a))


SHOULDER = ZC + _v(95.0, 46.0, -110.0)     # Zion's right shoulder as seen from the sea, where the sun comes
H_SUN = _v(2600.0 * np.sin(np.radians(163.0)), 30.0, ZC[2] + 2600.0 * np.cos(np.radians(163.0)))

# One shot per edit block the coda owns (blocks_of("coda")): exact block times; each a long flowing flight
# (spline keys), often chasing the coda's comets; the core paces each move with the music, shakes on slams and
# punches the lens on hits.
SHOTS = [
    # 3:08.27 thanks to Mother: hearts and lanterns rise: up off the sea, climbing the face of Zion with the
    # comets spiralling up round it, then over the terraces looking down on the hearts rising to the lens
    dict(name="hearts_rise", kind="local", t0=188.27, t1=195.2, fov=52.0, aperture=0.0,
         roll=(-6.0, 9.0),
         keys=[(188.27, _v(80.0, 8.0, -80.0), ZC + _v(0.0, 28.0, 0.0)),
               (190.0, _v(70.0, 40.0, -120.0), ZC + _v(0.0, 52.0, 0.0)),
               (192.0, _v(10.0, 100.0, -170.0), ZC + _v(0.0, 70.0, 20.0)),
               (193.7, _v(-80.0, 150.0, -190.0), ZC + _v(0.0, 50.0, 90.0)),
               (195.2, _v(-110.0, 190.0, -250.0), ZC + _v(10.0, 45.0, 120.0))]),
    # the last build: racing low over the sea past Zion behind the comets, toward the horizon's gathering light
    dict(name="hearts_rise", kind="local", t0=197.2, t1=199.62, fov=58.0, aperture=0.0, roll=(-10.0, 7.0),
         keys=[(197.2, _v(340.0, 4.0, -120.0), H_SUN), (198.4, _v(326.0, 3.0, -300.0), H_SUN),
               (199.62, _v(300.0, 7.0, -500.0), H_SUN)]),
    # the last moment before the sun: a rush up toward Zion's right shoulder
    dict(name="hearts_rise", kind="local", t0=200.7, t1=201.73, fov=50.0, aperture=0.0, roll=(8.0, -4.0),
         keys=[(200.7, _v(150.0, 20.0, 120.0), SHOULDER), (201.73, _v(130.0, 44.0, 30.0), SHOULDER + _v(0, 8, 0))]),
    # SLAM 3: the sun bursts over Zion's shoulder: low on the sea, craning up and sweeping in toward the sun
    dict(name="sunrise", kind="local", t0=201.73, t1=205.98, fov=56.0, aperture=0.0, roll=(0.0, -10.0),
         keys=[(201.73, _v(-30.0, 8.0, 160.0), ZC + _v(10.0, Y + 2.0, -40.0)),
               (203.2, _v(-24.0, 26.0, 110.0), ZC + _v(14.0, Y + 10.0, -40.0)),
               (204.6, _v(-6.0, 40.0, 60.0), ZC + _v(16.0, Y + 16.0, -40.0)),
               (205.98, _v(20.0, 52.0, 20.0), ZC + _v(20.0, Y + 20.0, -40.0))]),
    # the orchestra on clouds of light round the sun: a swooping orbit round the players, chasing the comets
    # that weave round them; the sun swings in behind them, then out to the right edge before the words
    dict(name="sky_stage", kind="sky", t0=205.98, t1=210.3, fov=52.0, aperture=0.0, blend=0.35, roll=(14.0, 0.0),
         keys=[(205.98, _orb(SKY_C, 26.0, 78.0, 10.0), SKY_C + _v(0.0, 0.8, 0.0)),
               (207.4, _orb(SKY_C, 18.0, 44.0, 4.5), SKY_C + _v(0.0, 1.0, -1.0)),
               (208.8, _orb(SKY_C, 15.0, 10.0, 2.6), SKY_C + _v(0.0, 1.4, -1.5)),
               (210.3, _orb(SKY_C, 18.0, 26.0, 3.6), SKY_C + _v(-2.0, 1.6, -2.0))]),
    # the third climb: in from far and high over the whole mountain (the words on the sky, the church below
    # them), then down over everyone on the avenue, arms raised, the comets circling above them
    dict(name="summit", kind="local", t0=211.6, t1=218.1, fov=54.0, aperture=0.0,
         roll=lambda t: -9.0 * _sc(213.8, 216.5, t) * (1.0 - _sc(216.5, 218.1, t)),
         keys=[(211.6, _v(12.0, 182.0, FZ + 290.0), _v(0.0, 130.0, FZ - 13.0)),
               (213.7, _v(8.0, 150.0, FZ + 205.0), _v(0.0, 128.0, FZ - 13.0)),
               (215.8, _v(-24.0, 104.0, FZ + 130.0), _v(0.0, 80.0, FZ + 20.0)),
               (218.1, _v(-8.0, Y + 12.0, FZ + 94.0), _v(0.0, Y + 3.0, FZ + 40.0))]),
    # the summit and the sun: a sweeping arc high round the side, the sun coming in at the right edge
    dict(name="summit", kind="local", t0=220.2, t1=222.0, fov=54.0, aperture=0.0, roll=(-8.0, 0.0),
         keys=[(220.2, _v(160.0, 130.0, FZ + 130.0), _v(0.0, 118.0, FZ - 13.0)),
               (221.1, _v(110.0, 138.0, FZ + 200.0), _v(0.0, 122.0, FZ - 13.0)),
               (222.0, _v(40.0, 146.0, FZ + 240.0), _v(0.0, 126.0, FZ - 13.0))]),
    # devotion: the world finale: a fast pull back from Korea, then a spiral round the Earth as the comets
    # stream in from every land to Zion
    dict(name="earth_finale", kind="globe", t0=224.03, t1=228.6, fov=50.0, aperture=0.0, roll=(0.0, 14.0),
         keys=[(224.03, G + _v(6.0, 34.0, -74.0), G + _v(0.0, 40.0, 0.0)),
               (225.6, G + _v(-20.0, 22.0, -138.0), G + _v(0.0, 32.0, 0.0)),
               (227.1, G + _v(-62.0, 8.0, -118.0), G + _v(0.0, 34.0, 0.0)),
               (228.6, G + _v(30.0, 22.0, -136.0), G + _v(0.0, 48.0, 0.0))]),
    # the glory line over the Earth, hearts across the continents: the Earth low, the words over space, a slow
    # arc down beside it, then skimming toward its top edge
    dict(name="earth_finale", kind="globe", t0=228.6, t1=235.6, fov=48.0, aperture=0.0,
         keys=[(228.6, G + _v(12.0, 18.0, -152.0), G + _v(0.0, 50.0, 0.0)),
               (231.0, G + _v(-6.0, 26.0, -142.0), G + _v(0.0, 55.0, 0.0)),
               (233.3, G + _v(-50.0, 8.0, -108.0), G + _v(-7.0, 52.0, 0.0)),
               (235.6, G + _v(-6.0, 34.0, -70.0), G + _v(0.0, 63.0, 60.0))]),
    # the peak: the sunrise over the Earth's edge, the camera rising and drawing back
    dict(name="earth_finale", kind="globe", t0=235.6, t1=238.8, fov=52.0, aperture=0.0, roll=(-6.0, 4.0),
         keys=[(235.6, G + _v(-18.0, 16.0, -70.0), G + _v(0.0, 56.0, 80.0)),
               (237.2, G + _v(-14.0, 22.0, -88.0), G + _v(0.0, 57.0, 60.0)),
               (238.8, G + _v(-8.0, 30.0, -110.0), G + _v(0.0, 58.0, 40.0))]),
    # the last chord: the slow pull-out to the whole Earth glowing under the end card (calm)
    dict(name="earth_end", kind="globe", t0=254.07, t1=TOTAL + 1.0, fov=46.0, aperture=0.0, pace="linear",
         keys=[(254.07, _gcam(150.0, 6.0), G), (TOTAL + 1.0, _gcam(185.0, 8.0), G)]),
]


# =========================================================================================================
# The coda's comets of light (nine colours), the sun as the great ray source, the comets over the Earth
# =========================================================================================================
def _dir(az, el):
    a, e = np.radians(az), np.radians(el)
    return _v(np.sin(a) * np.cos(e), np.sin(e), np.cos(a) * np.cos(e))


def sun_point(t):
    """A point far along the sun's direction from the camera (for the ray source): the world's own sun."""
    import songs.s11_light as L
    import songs.s11_full2 as H
    cam = H.CAMERA.state(t)
    return np.asarray(cam.pos, np.float64) + 4000.0 * _dir(L.sun_az(t), L.sun_el(t))


def sun_rays(t):
    """The sun as the great ray source: the biggest burst on SLAM 3, then over the clouds, the summit, the
    Earth's edge at the peak."""
    kick = hit_pulse(t, KICKS, rise=0.02, fall=0.5)
    if 199.0 <= t < 201.73:
        return 0.25 + 0.45 * _sc(199.0, 201.6, t)          # the horizon glows before the sun
    if 201.73 <= t < 206.0:
        return 1.05 + 1.1 * hit_pulse(t, [SLAM3], rise=0.02, fall=1.2) + 0.25 * beat_pulse(t)
    if 206.0 <= t < 211.6 and shot_name(t) == "sky_stage":
        return 0.75 + 0.3 * kick + 0.15 * beat_pulse(t)
    if 211.6 <= t < 224.03 and shot_name(t) == "summit":
        return 0.55 + 0.3 * kick
    if 235.0 <= t < 238.8 and globe_view(t):
        return 0.35 + 0.85 * _sc(235.0, 235.8, t) + 0.5 * hit_pulse(t, [HIT["peak"]], fall=1.0)
    return 0.0


def _helix(c, r0, r1, y0, y1, w, a0, t0, t1):
    def head(t):
        u = np.clip((t - t0) / (t1 - t0), -0.2, 1.2)
        a = a0 + w * (t - t0)
        r = r0 + (r1 - r0) * u
        return c + _v(r * np.sin(a), y0 + (y1 - y0) * u + 0.08 * r * np.sin(2.3 * a), r * np.cos(a))
    return head


def _weave(c, r, w, a0, h0, hamp, hw):
    def head(t):
        a = a0 + w * t
        rr = r * (1.0 + 0.18 * np.sin(1.7 * a + a0))
        return c + _v(rr * np.sin(a), h0 + hamp * np.sin(hw * t + a0), rr * np.cos(a) * 0.75)
    return head


def _race(p0, v, t0, lane):
    def head(t):
        u = t - t0
        return p0 + v * u + _v(6.0 * np.sin(2.1 * u + lane), 3.0 * np.sin(1.6 * u + 2 * lane), 0.0)
    return head


def _ring_round(cfn, r, w, a0, tilt):
    def head(t):
        c = cfn(t)
        a = a0 + w * t
        return c + _v(r * np.cos(a), r * np.sin(a) * tilt, r * 0.3 * np.sin(a + 1.0))
    return head


SKY_SUN = SKY_STAGE + 700.0 * _dir(163.0, 3.5)          # where the sun stands, seen from the sky stage


def _comets():
    out = []
    # thanks to Mother: five comets spiral up round Zion with the hearts
    for i in range(5):
        out.append(Comet(_helix(ZC, 260.0, 120.0, 12.0, 170.0, 0.42, i * 2 * np.pi / 5, 188.27, 197.2),
                         COL9[(2 * i) % 9], 188.27, 197.4, trail=1.6, width=1.8, bright=1.1, light=(i == 0),
                         seed=10 + i))
    # the last build: three comets race low over the sea toward the gathering light, leading the camera
    for i in range(3):
        p0 = _v(320.0 - 26.0 * i, 9.0 + 5.0 * i, -170.0 - 20.0 * i)
        v = _unit(H_SUN - p0) * (190.0 + 20.0 * i)
        out.append(Comet(_race(p0, v, 197.2, i), COL9[(3 * i + 1) % 9], 197.2, 201.9, trail=0.9, width=1.4,
                         bright=1.2, light=(i == 1), seed=20 + i))
    # the orchestra on the clouds: five comets weave round the players, four circle the sun
    for i in range(5):
        out.append(Comet(_weave(SKY_C, 17.0 + 2.0 * i, 0.9 + 0.08 * i, i * 1.26, 3.0 + 0.6 * i, 2.6, 1.1),
                         COL9[i], 205.98, 211.7, trail=1.1, width=0.28, bright=1.1, light=(i == 2), seed=30 + i))
    for i in range(4):
        out.append(Comet(_ring_round(lambda t: SKY_SUN, 80.0 + 14.0 * i, 0.8 + 0.1 * i, i * 1.57, 0.85),
                         COL9[5 + i], 205.98, 211.7, trail=1.2, width=4.0, bright=1.0, seed=40 + i))
    # the summit: five comets circle above everyone, round the church
    for i in range(5):
        c = _v(0.0, Y + 0.0, FZ + 30.0)
        out.append(Comet(_weave(c, 46.0 + 6.0 * i, 0.55 + 0.05 * i, i * 1.26, 26.0 + 5.0 * i, 9.0, 0.7),
                         COL9[(i + 4) % 9], 211.6, 224.1, trail=1.5, width=0.9, bright=1.1, light=(i == 0),
                         seed=50 + i))
    return out


SUNRISE_P = ZC + 1900.0 * _dir(163.0, 2.0)               # the sun over Zion's shoulder, as a place to fan from


def _fan(i, n):
    """A comet fanning out of the sun on SLAM 3: launched on the slam, flying out and toward us in an arc."""
    ang = np.radians(-70.0 + 140.0 * i / (n - 1))
    v = 520.0 * _unit(_v(0.55 * np.sin(ang), 0.35 + 0.55 * np.cos(ang), 1.0))
    def head(t):
        u = max(t - SLAM3, 0.0)
        return SUNRISE_P + v * u + _v(0.0, -18.0 * u * u, 0.0)
    return head


def _sun_comets():
    return [Comet(_fan(i, 7), COL9[(i * 4) % 9], SLAM3 - 0.05, 206.2, trail=0.9, width=9.0, bright=1.4, fade=0.3,
                  seed=60 + i) for i in range(7)]


class SpaceComet(Comet):
    """A comet in space round the Earth of light (the core's Comet stays on Zion's side of the film)."""

    def sample(self, t):
        k = self.k(t)
        if k <= 0.0 or not globe_view(t):
            return None
        P = np.array([self.head(t - self.trail * x) for x in np.linspace(0.0, 1.0, self.n)])
        u = np.linspace(0.0, 1.0, self.n)
        col = lin(self.color)
        pulse = 1.0 + 0.5 * beat_pulse(t) * intensity(t) + 0.8 * hit_pulse(t, KICKS, fall=0.4)
        a = k * (1.0 - u) ** 1.4
        w = self.width * (1.0 - 0.85 * u)
        return [dict(pos=P, size=w * 2.2, color=col, alpha=0.30 * a * self.bright, kind="soft", emit=2.0, dof=0.0),
                dict(pos=P, size=w * 0.5, color=col * 0.5 + lin(WHITE) * 0.5, alpha=a * self.bright, kind="spark",
                     emit=3.0 * pulse, dof=0.0),
                dict(pos=P[:1], size=self.width * 5.0, color=col, alpha=0.45 * k * pulse, kind="soft", emit=3.0),
                dict(pos=P[:1], size=self.width * 1.2, color=lin(WHITE), alpha=k, kind="spark", emit=6.0 * pulse)]


def _space_comets():
    out = []
    for i in range(5):
        out.append(SpaceComet(_weave(G, 92.0 + 12.0 * i, 0.55 + 0.06 * i, i * 1.26, 10.0 * i - 20.0, 30.0, 0.5),
                              COL9[(2 * i + 1) % 9], 224.03, 238.8, trail=1.8, width=2.2, bright=1.2, seed=70 + i))
    return out


class SummitPillars(Pillars):
    """Pillars of light falling round everyone on the summit (they land on the plateau, not the sea)."""

    def sample(self, t):
        out = super().sample(t)
        if not out:
            return out
        for b in out:
            b["pos"] = b["pos"] + _v(0.0, SUMMIT - 0.2, 0.0)
        return out


def _pillar_gain(t):
    if globe_view(t) or not (211.0 <= t < 224.1):
        return 0.0
    return (_sc(211.0, 212.2, t) * (1.0 - _sc(223.4, 224.1, t))) * (0.75 + 0.35 * intensity(t))


def _coda_clouds():
    """Towering clouds of light: round Zion for the hearts and lanterns, the canyon of the last build, banks
    under the sky orchestra and round the sun."""
    def g_hearts(t):
        return 0.0 if globe_view(t) else _sc(187.8, 188.5, t) * (1.0 - _sc(196.6, 197.2, t)) * (0.9 + 0.3 * beat_pulse(t))

    def g_canyon(t):
        return 0.0 if globe_view(t) else _sc(196.8, 197.2, t) * (1.0 - _sc(199.4, 199.62, t)) * (0.8 + 0.3 * beat_pulse(t))

    def g_sky(t):
        return sky_k(t) * (0.9 + 0.25 * beat_pulse(t))

    def g_rise(t):
        return 0.0 if globe_view(t) else _sc(201.6, 202.2, t) * (1.0 - _sc(205.6, 206.0, t))

    out = []
    for i, az in enumerate((-50.0, 50.0)):          # one tower each side, framing Zion
        c = ZC + 380.0 * _dir(az, 0.0) + _v(0.0, 4.0, 0.0)
        out.append(CloudBank(c, size=(260.0, 210.0, 120.0), puffs=34, seed=80 + i, gain=g_hearts, bright=1.0))
    for i, x in enumerate((190.0, 470.0)):                  # the canyon of the last build
        c = _v(x, 2.0, -760.0)
        out.append(CloudBank(c, size=(80.0, 170.0, 1100.0), puffs=46, seed=90 + i, gain=g_canyon, bright=0.65))
    for i in range(3):                                      # under and behind the sky orchestra
        c = SKY_STAGE + _v(-320.0 + 320.0 * i, -150.0, -420.0 - 80.0 * i)
        out.append(CloudBank(c, size=(320.0, 120.0, 160.0), puffs=30, seed=100 + i, gain=g_sky, bright=0.3))
    for i, da in enumerate((-14.0, 13.0)):                  # banks either side of the rising sun, far behind Zion
        c = ZC + 1000.0 * _dir(163.0 + da, 0.0)
        c[1] = 2.0
        out.append(CloudBank(c, size=(420.0, 170.0, 160.0), puffs=34, seed=110 + i, gain=g_rise, bright=0.9))
    return out


class GlobeComets:
    """The world finale: comets of light in the nine colours stream in from every land to Zion (Korea), one
    after another, arcing high over the Earth, each arriving with a flash."""
    wants_camera = True

    def __init__(self, n=9, launch=224.4, every=1.05, fly=3.2):
        self.starts = [_earth(*ll) for ll in GlobeFX.STARTS[:n]]
        self.cols = [lin(c) for c in COL9[:n]]
        self.L = [launch + every * i for i in range(n)]
        self.fly = fly
        r = np.random.default_rng(71)
        self.s = r.random((n, 120, 4))

    def sample(self, t, cam=None):
        if cam is None or not globe_view(t) or not (224.03 <= t < 238.8):
            return None
        c, M, R = GLOBE._view(t, cam)
        T = M @ GLOBE.turn(t)
        zv = _earth(*ZION_LL)
        eye = np.asarray(cam.pos, np.float64)
        u = np.linspace(0.0, 1.0, 60)
        out = []
        pulse = 1.0 + 0.5 * beat_pulse(t) + 0.8 * hit_pulse(t, KICKS, fall=0.4)
        for i, sv in enumerate(self.starts):
            ts = t - 0.9 * u
            f = np.clip((ts - self.L[i]) / self.fly, 0.0, 1.0)
            live = (ts >= self.L[i]) & (ts <= self.L[i] + self.fly + 0.05)
            k = _sc(self.L[i], self.L[i] + 0.3, t) * (1.0 - _sc(self.L[i] + self.fly, self.L[i] + self.fly + 0.8, t))
            if k <= 0.0 or not live.any():
                continue
            om = np.arccos(np.clip(sv @ zv, -1, 1))
            w0 = np.sin((1 - f) * om) / np.sin(om)
            w1 = np.sin(f * om) / np.sin(om)
            v = w0[:, None] * sv[None, :] + w1[:, None] * zv[None, :]
            v = v / np.linalg.norm(v, axis=1, keepdims=True)
            lift = 1.02 + 0.22 * np.sin(np.pi * f)
            P = c + R * lift[:, None] * (v @ T.T)
            nrm = (P - c) / np.linalg.norm(P - c, axis=1, keepdims=True)
            vis = live & ((((eye[None, :] - P) * nrm).sum(1) > -0.15 * R) | (lift > 1.08))
            if not vis.any():
                continue
            a = k * (1.0 - u) ** 1.3
            col = self.cols[i]
            Pv, av, uv = P[vis], a[vis], u[vis]
            w = 1.1 * (1.0 - 0.8 * uv)
            out += [dict(pos=Pv, size=w * 2.4, color=col, alpha=0.3 * av, kind="soft", emit=2.0, dof=0.0, reflect=False),
                    dict(pos=Pv, size=w * 0.45, color=col * 0.5 + lin(WHITE) * 0.5, alpha=av, kind="spark",
                         emit=3.0 * pulse, dof=0.0, reflect=False)]
            if vis[0]:
                out += [dict(pos=P[:1], size=6.0, color=col, alpha=0.5 * k * pulse, kind="soft", emit=3.0, dof=0.0,
                             reflect=False),
                        dict(pos=P[:1], size=1.4, color=lin(WHITE), alpha=k, kind="spark", emit=6.0 * pulse, dof=0.0,
                             reflect=False)]
            # the arrival: a flash of its colour on Zion
            d = t - (self.L[i] + self.fly)
            if 0.0 <= d < 1.2:
                zp = c + R * 1.02 * (zv @ T.T)
                out.append(dict(pos=zp[None, :], size=8.0 + 10.0 * d, color=col, alpha=0.5 * np.exp(-d / 0.4),
                                kind="soft", emit=3.0, dof=0.0, reflect=False))
        return out or None


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
        self.t0 = 188.3 + 7.6 * r.random(n) ** 1.4
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
        a = _ss(0.0, 0.5, u) * (1.0 - _ss(5.0, 9.0, u)) * (1.0 - _sc(200.5, 201.7, t))
        # the music: the hearts beat with the pulse, flare on the hits, burn brighter as the music grows
        kick = hit_pulse(t, KICKS, rise=0.02, fall=0.4)
        beat = beat_pulse(t)
        glow = 0.75 + 0.5 * intensity(t) + 0.9 * kick
        sz = self.sz[on] * (1.0 + 0.16 * beat + 0.25 * kick)
        hx, hy = self.h[:, 0], self.h[:, 1]
        P = (c[:, None, :] + sz[:, None, None] * (hx[None, :, None] * rgt[None, None, :] + hy[None, :, None] * up[None, None, :]))
        m = len(self.h)
        return [dict(pos=P.reshape(-1, 3), size=np.repeat(0.09 * sz, m), color=np.repeat(self.col[on], m, axis=0),
                     alpha=np.repeat(a, m), emit=3.0 * glow, kind="spark"),
                dict(pos=c, size=2.2 * sz, color=self.col[on], alpha=(0.14 + 0.12 * beat + 0.2 * kick) * a,
                     emit=1.6 * glow, kind="soft")]


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
        k = _sc(196.5, 201.6, t) * (1.0 - 0.6 * _sc(202.0, 206.0, t)) * (0.85 + 0.3 * beat_pulse(t))
        return [dict(pos=self.P, size=7.0, color=lin("#ffd29a"), alpha=0.35 * k, emit=2.0, kind="soft", dof=0.0),
                dict(pos=self.P[::3], size=2.2, color=lin("#fff0d0"), alpha=0.7 * k, emit=3.0, kind="spark",
                     twinkle=0.6, seed=self.s[::3], dof=0.0)]


SKY_OFF = SKY_STAGE - SQUARE


def sky_k(t):
    return 1.0 if shot_kind(t) == "sky" else 0.0


def _sun_dir_coda(el=4.0, az=163.0):
    e, a = np.radians(el), np.radians(az)
    return _v(np.sin(a) * np.cos(e), np.sin(e), np.cos(a) * np.cos(e))


class Clouds:
    """The clouds of light the orchestra plays on, round the rising sun (the coda): a low billow of cloud under
    the players (kept thin, so the players read on it), a sea of cloud far below in rose, violet and gold, and
    banks of cloud lit gold round the sun."""

    def __init__(self):
        r = np.random.default_rng(141)
        # the billow under the orchestra: an ellipse round the players, thickest at its rim
        n = 5200
        a = 2 * np.pi * r.random(n)
        u = np.sqrt(r.random(n))
        u = 0.55 + 0.45 * u                      # most of the cloud lies round the players, not under them
        bill = 0.6 * np.sin(3.0 * a + 1.3) + 0.4 * np.sin(7.0 * a)
        rx, rz = 20.0 + 3.0 * bill, 10.0 + 2.0 * bill
        self.P = np.stack([SKY_C[0] + rx * u * np.sin(a),
                           SKY_STAGE[1] - 1.2 - 2.4 * u ** 3 - 1.2 * r.random(n) ** 2 + 1.0 * (u - 0.55),
                           SKY_C[2] + rz * u * np.cos(a)], 1)
        self.s = r.random(n)
        self.pu = u
        warm = np.asarray([lin("#ffe2c8"), lin("#ffc8d0"), lin("#e8d0ff")])
        self.pc = warm[r.integers(0, 3, n)]
        # the sea of cloud far below, coloured by where it lies against the sun
        m = 2600
        a = 2 * np.pi * r.random(m)
        rr = 80.0 + 520.0 * np.sqrt(r.random(m))
        self.F = np.stack([SKY_STAGE[0] + rr * np.sin(a), SKY_STAGE[1] - 40.0 - 30.0 * r.random(m),
                           SKY_STAGE[2] + rr * np.cos(a)], 1)
        sd = _sun_dir_coda()
        toward = np.clip((np.sin(a) * sd[0] + np.cos(a) * sd[2]), -1.0, 1.0)
        w = (0.5 + 0.5 * toward)[:, None] ** 2
        cool = np.where((r.random(m) < 0.5)[:, None], lin("#8a5aa0")[None, :], lin("#5a4aa8")[None, :])
        self.fc = cool * (1.0 - w) + lin("#e8a070")[None, :] * w
        self.fs = 16.0 + 14.0 * r.random(m)
        # banks of cloud round the sun, far away, lit gold on their sunward side
        k = 1400
        az = 163.0 + r.normal(0.0, 14.0, k)
        el = -1.0 + 6.0 * r.random(k) ** 1.5
        dd = 900.0 + 300.0 * r.random(k)
        e, aa = np.radians(el), np.radians(az)
        self.B = SKY_STAGE + np.stack([np.sin(aa) * np.cos(e), np.sin(e), np.cos(aa) * np.cos(e)], 1) * dd[:, None]
        near = np.exp(-((az - 163.0) / 10.0) ** 2)[:, None]
        self.bc = lin("#e6a0b8")[None, :] * (1.0 - near) + lin("#ffd08a")[None, :] * near
        self.bs = 30.0 + 40.0 * r.random(k)

    def sample(self, t):
        if sky_k(t) <= 0.0:
            return None
        drift = _v(0.4 * np.sin(0.2 * t), 0.0, 0.0)
        pulse = 1.0 + 0.25 * beat_pulse(t)
        rim = 0.25 + 0.75 * self.pu ** 2
        return [dict(pos=self.P + drift, size=1.0 + 1.2 * self.s, color=self.pc, alpha=0.03 * rim, emit=1.0,
                     kind="soft", seed=self.s, dof=0.0),
                dict(pos=self.P[::3] + drift, size=0.05, color=lin(GOLD2), alpha=0.55 * pulse, emit=2.0,
                     kind="spark", twinkle=0.8, seed=self.s[::3]),
                dict(pos=self.F, size=self.fs, color=self.fc, alpha=0.04, emit=1.0, kind="soft", dof=0.0,
                     reflect=False),
                dict(pos=self.B, size=self.bs, color=self.bc, alpha=0.06, emit=1.2, kind="soft", dof=0.0,
                     reflect=False)]


def _music_gain(t):
    """Brightness of the people of light with the music: the beat, the hits, the swell."""
    return 0.8 + 0.3 * intensity(t) + 0.18 * beat_pulse(t) + 0.45 * hit_pulse(t, KICKS, rise=0.02, fall=0.4)


def sky_gain(t):
    return sky_k(t) * _music_gain(t)


def summit_gain(t):
    return summit_k(t) * _music_gain(t)


def summit_k(t):
    """Everyone on the summit: from the coda's sunrise to the last chord (not in the close stage shots)."""
    if globe_view(t) or not (201.73 <= t < 254.07):
        return 0.0
    return 1.0


def _summit_places(n=700, seed=151):
    """Everyone on the summit, in the open ground (the church thread's buildings fill the rest of the plateau):
    the great avenue down from the square (|x| < 13), and both wings of the square beside the orchestra."""
    r = np.random.default_rng(seed)
    pts = []
    n_av = int(n * 0.62)
    while len(pts) < n_av:
        x = r.uniform(-13.0, 13.0)
        z = r.uniform(FACADE_Z + 22.0, FACADE_Z + 80.0)
        if abs(x) < 1.2 or np.hypot(x - ZC[0], z - ZC[2]) > R_TOP - 9.0:
            continue
        pts.append((x, SUMMIT, z))
    while len(pts) < n:
        x = r.uniform(16.0, 38.0) * (1.0 if r.random() < 0.5 else -1.0)
        z = r.uniform(FACADE_Z - 8.0, FACADE_Z + 20.0)
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
        if t < HIT["final"]:
            core = _sc(246.0, HIT["final"], t)
        else:
            core = np.exp(-(t - HIT["final"]) / 0.5)
        return [dict(pos=P, size=0.16, color=lin("#ffcf70"), alpha=a, emit=4.0, kind="spark", twinkle=0.7, seed=self.s,
                     dof=0.0),
                dict(pos=self.c[None, :], size=3.0 + 5.0 * core, color=lin("#ffd890"), alpha=0.35 * core, emit=2.0,
                     kind="soft", dof=0.0)]


def _heart_sprites(b, cam):
    """A "heart" batch (the repo engine's heart sprites) as hearts of points for the pinned engine, which has no
    heart kind: each heart is a filled heart of sparks facing the camera, in its exact colour."""
    from p3d.brand_hearts import heart_points
    if not hasattr(_heart_sprites, "h"):
        _heart_sprites.h = np.concatenate([heart_points(40), heart_points(60, fill=True)])
    h = _heart_sprites.h
    rgt, up, _f = cam.basis()
    pos = np.asarray(b["pos"], np.float64)
    n, m = len(pos), len(h)
    sz = np.broadcast_to(np.asarray(b["size"], np.float64), (n,))
    P = pos[:, None, :] + sz[:, None, None] * (h[None, :, 0, None] * rgt[None, None, :] + h[None, :, 1, None] * up[None, None, :])
    out = dict(b)
    out.update(pos=P.reshape(-1, 3), size=np.repeat(0.11 * sz, m), kind="spark",
               alpha=np.repeat(np.broadcast_to(np.asarray(b["alpha"], np.float64), (n,)), m))
    for k in ("color", "seed"):
        v = np.asarray(b.get(k, 0.0))
        if v.ndim >= 1 and len(v) == n:
            out[k] = np.repeat(v, m, axis=0)
    return out


def _patch_globe_hearts():
    """The core's Earth (GLOBE) draws its hearts with kind "heart", which the pinned engine does not know (the
    frame fails from 3:46 on). Until the core changes, the coda turns them into hearts of points here."""
    if getattr(GLOBE, "_coda_hearts", False):
        return
    orig = GLOBE._hearts

    def hearts(t, cam, *a, **kw):
        out = orig(t, cam, *a, **kw)
        return [(_heart_sprites(b, cam) if b.get("kind") == "heart" else b) for b in out]
    GLOBE._hearts = hearts
    GLOBE._coda_hearts = True
    # the world finale: the Earth turns so that Zion (Korea) faces us while the light of every land flows to it
    # (without this, 3:44 to 3:59 shows the Atlantic and Zion is on the far side)
    front = GLOBE._front_at

    def front_at(t):
        if 224.03 <= t < 254.0:
            return ZION_LL[1] - 4.0 - 2.6 * (t - 224.03)     # Korea at the front, then turning away right
        return front(t)
    GLOBE._front_at = front_at


SHAFTS = []


def add(scene):
    _patch_globe_hearts()
    scene.add("rising hearts", RisingHearts())
    scene.add("horizon", Horizon())
    # the orchestra on clouds of light round the rising sun
    scene.add("clouds", Clouds())
    scene.add("sky orchestra", GCrowd(gain=sky_gain, places=ORCH_P + SKY_OFF, facing=0.0, kinds=("sit",),
                                      people=dict(woman=1.0, man=1.0), start=0.0, color="#6cb2ff", color2="#d2e8ff",
                                      bright=2.6, size=1.7, points=1600, glints=0.012, seed=4.0))
    scene.add("sky instruments", Instruments(offset=SKY_OFF, gain=sky_k))
    # everyone on the summit, from the coda's sunrise to the last chord
    scene.add("summit", GCrowd(gain=summit_gain, places=_summit_places(), facing=180.0,
                               kinds=(("raise", 3.0), ("stand", 1.0), ("cheer", 1.5)),
                               people=dict(woman=1.0, man=1.0, child=0.2),
                               start=dict(t=201.0, center=(0.0, FACADE_Z), speed=40.0), color="#ffc870",
                               color2="#fff2d8", bright=1.9, size=2.8, points=500, glints=0.012, seed=41.0))
    scene.add("gather", Gather())
    for i, cm in enumerate(_comets()):
        scene.add(f"coda comet {i}", cm)
    scene.add("earth comets", GlobeComets(), reflect=False)
    for i, cm in enumerate(_sun_comets()):
        scene.add(f"sun comet {i}", cm)
    for i, cm in enumerate(_space_comets()):
        scene.add(f"space comet {i}", cm, reflect=False)
    for i, cb in enumerate(_coda_clouds()):
        scene.add(f"coda cloud {i}", cb)
    pil = [(x, FZ + z) for x, z in ((-20.0, 30.0), (20.0, 30.0), (-22.0, 60.0), (22.0, 60.0), (-34.0, 4.0),
                                     (34.0, 4.0), (-16.0, 84.0), (16.0, 84.0))]
    scene.add("summit pillars", SummitPillars(pil, top=420.0, color="#ffe6c0", width=2.6, gain=_pillar_gain))
    add_rays(sun_point, sun_rays, color="#ffe6b0", size=0.9)
