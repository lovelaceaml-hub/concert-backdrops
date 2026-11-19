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
import songs.s11_full2 as _CORE  # noqa: E402  (the camera, for f19)
from songs.s11_stage import Instruments, ORCH_P, Players  # noqa: E402
from songs.s11_zion import WaveCrowd, mx, reading, wave_u  # noqa: E402  (the waves of raised arms; the music map)

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
         keys=[(205.98, _orb(SKY_C, 28.0, 78.0, 13.0), SKY_C + _v(0.0, 0.6, 2.0)),
               (207.4, _orb(SKY_C, 21.0, 44.0, 8.0), SKY_C + _v(0.0, 0.8, 2.0)),
               (208.8, _orb(SKY_C, 18.0, 10.0, 6.5), SKY_C + _v(0.0, 1.0, 1.5)),
               (210.3, _orb(SKY_C, 20.0, 26.0, 7.0), SKY_C + _v(-2.0, 1.2, 1.0))]),
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
        # round 6: the burst blazes on the slam itself, then settles within half a second to a steady glory
        # behind the words ("Joy of salvation!" reads from the slam), swelling a little on the beat
        return 0.72 + 1.3 * hit_pulse(t, [SLAM3], rise=0.02, fall=0.22) + 0.15 * beat_pulse(t)
    if 206.0 <= t < 211.6 and shot_name(t) == "sky_stage":
        return 0.75 + 0.3 * kick + 0.15 * beat_pulse(t)
    if 211.6 <= t < 224.03 and shot_name(t) == "summit":
        # (round 8, f35: 3:34 to 3:39.5 stayed pale) half the steady glory, the light swells only on the beats
        q = _win(t, 213.5, 219.5, 0.6, 0.6)
        return (0.55 - 0.32 * q) + (0.3 + 0.1 * q) * kick + 0.12 * q * beat_pulse(t)
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


def _under_thanks(P, t):
    """(round 8, f19) while the thanks line reads in the top third (3:47.0 to 3:56) the comets' streaks keep
    below it: points high in the frame fade out. 1 elsewhere."""
    w = _win(t, 226.8, 236.4, 0.3, 0.4)
    if w <= 0.0 or len(P) == 0:
        return np.ones(len(P))
    xy, z = _CORE.CAMERA.state(t).project(P)
    return 1.0 - w * _ss(0.46, 0.53, xy[:, 1]) * (z > 0.0)


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
        q = _under_thanks(P, t)
        a = a * q
        w = self.width * (1.0 - 0.85 * u)
        return [dict(pos=P, size=w * 2.2, color=col, alpha=0.30 * a * self.bright, kind="soft", emit=2.0, dof=0.0),
                dict(pos=P, size=w * 0.5, color=col * 0.5 + lin(WHITE) * 0.5, alpha=a * self.bright, kind="spark",
                     emit=3.0 * pulse, dof=0.0),
                dict(pos=P[:1], size=self.width * 5.0, color=col, alpha=0.45 * k * pulse * q[0], kind="soft", emit=3.0),
                dict(pos=P[:1], size=self.width * 1.2, color=lin(WHITE), alpha=k * q[0], kind="spark", emit=6.0 * pulse)]


def _space_comets():
    out = []
    for i in range(5):
        out.append(SpaceComet(_weave(G, 92.0 + 12.0 * i, 0.55 + 0.06 * i, i * 1.26, 10.0 * i - 20.0, 30.0, 0.5),
                              COL9[(2 * i + 1) % 9], 224.03, 238.8, trail=1.8, width=2.2, bright=1.2, seed=70 + i))
    return out


class SummitPillars(Pillars):
    """Pillars of light falling round everyone on the summit (they land on the plateau, not the sea).

    Round 6: solid soft beams, not dotted columns: the points along each beam lie much closer than their own
    size (densest low down, where the camera sees them), each point's alpha set by its spacing so the beam is
    even. They pulse with the music: the whole beam swells on every beat and flares on the hits, and on each
    beat a band of brighter light runs down the beam and lands in its pool on the plateau."""

    N = 420
    wants_camera = True

    def __init__(self, bases, top=300.0, color="#ffe2b8", width=3.0, gain=None, seed=2):
        super().__init__(bases, top=top, color=color, width=width, gain=gain, seed=seed)
        s = np.linspace(0.0, 1.0, self.N)
        self.y = self.top * s ** 1.7                                  # dense low down, sparser high up
        dy = np.gradient(self.y)
        self.uu = self.y / self.top
        self.glow_s = self.width * (1.3 + 1.1 * self.uu)            # the soft beam
        self.core_s = self.width * (0.42 + 0.35 * self.uu)          # its bright core
        # alpha per point by its spacing (overlapping points add up): an even beam from foot to top
        self.glow_w = np.clip(dy / (0.5 * self.glow_s), 0.0, 1.0)
        self.core_w = np.clip(dy / (0.5 * self.core_s), 0.0, 1.0)

    def sample(self, t, cam=None):
        g = float(self.g(t))
        if g <= 0.0 or globe_view(t):
            return None
        eye = np.asarray(cam.pos, np.float64) if cam is not None else _v(0.0, 1e4, 0.0)
        beat = beat_pulse(t, 0.12)
        kick = hit_pulse(t, KICKS, rise=0.02, fall=0.45)
        k = g * (0.62 + 0.38 * beat + 0.75 * kick)
        # the band of light falling down each beam from the last beats (220 m/s)
        i = int(np.searchsorted(BEATS, t))
        band = np.zeros(self.N)
        for b in BEATS[max(i - 3, 0):i]:
            yb = self.top - 220.0 * (t - b)
            if yb > -20.0:
                band = band + np.exp(-((self.y - yb) / 26.0) ** 2) * np.exp(-(t - b) / 1.2)
        land = sum(np.exp(-(t - (b + self.top / 220.0)) / 0.25) for b in BEATS[max(i - 4, 0):i + 1]
                   if 0.0 <= t - (b + self.top / 220.0) < 1.5)
        # bright where they fall among the people, fading up into the sky (the words read over the upper sky)
        prof = (0.02 + 0.98 * np.exp(-self.y / 38.0)) * (1.0 + 0.9 * band)
        out = []
        for j, (x, z) in enumerate(self.bases):
            P = np.stack([np.full(self.N, x), self.y + SUMMIT - 0.2, np.full(self.N, z)], 1)
            # a beam the camera flies right beside softens, so it never fills the frame with white
            near = _sc(6.0, 26.0, float(np.hypot(eye[0] - x, eye[2] - z)))
            br = k * (0.88 + 0.12 * np.sin(2.0 * t + 6.0 * self.ph[j])) * (0.25 + 0.75 * near)
            out.append(dict(pos=P, size=self.glow_s, color=self.col, alpha=0.11 * br * prof * self.glow_w,
                            kind="soft", emit=1.8, dof=0.0))
            # (round 8, from STAGE: dotted columns close up) the bright core is one continuous line of light, a
            # chain of segments with no gaps, like the stage's pillars; a fainter soft core keeps its width
            ac = np.minimum(0.55 * br * prof, 1.0)
            out.append(dict(pos=P[:-1], pos2=P[1:], size=self.width * 0.10, color=self.col * 0.6 + lin(WHITE) * 0.4,
                            alpha=ac[:-1], alpha2=ac[1:], kind="line", emit=2.6, dof=0.0))
            out.append(dict(pos=P, size=self.core_s, color=self.col * 0.6 + lin(WHITE) * 0.4,
                            alpha=0.07 * br * prof * self.core_w, kind="soft", emit=2.4, dof=0.0))
            out.append(dict(pos=np.array([[x, SUMMIT + 0.15, z]]), size=self.width * (6.0 + 2.0 * land),
                            color=self.col, alpha=(0.12 + 0.2 * land) * k, kind="soft", emit=2.0, reflect=False))
        return out


def _pillar_gain(t):
    if globe_view(t) or not (211.0 <= t < 224.1):
        return 0.0
    q = _win(t, 213.5, 219.5, 0.6, 0.6)          # (f35) half, swelling only on the beats, through the pale stretch
    return ((_sc(211.0, 212.2, t) * (1.0 - _sc(223.4, 224.1, t))) * (0.75 + 0.35 * intensity(t))
            * (1.0 - q * (0.5 - 0.4 * beat_pulse(t))))


def _coda_clouds():
    """Towering clouds of light: round Zion for the hearts and lanterns, the canyon of the last build, banks
    under the sky orchestra and round the sun."""
    def g_hearts(t):
        return 0.0 if globe_view(t) else _sc(187.8, 188.5, t) * (1.0 - _sc(196.6, 197.2, t)) * (0.9 + 0.3 * beat_pulse(t))

    def g_canyon(t):
        return 0.0 if globe_view(t) or stage_view(t) else _sc(196.8, 197.2, t) * (1.0 - _sc(199.4, 199.62, t)) * (0.8 + 0.3 * beat_pulse(t))



    def g_rise(t):
        return 0.0 if globe_view(t) or stage_view(t) else _sc(201.6, 202.2, t) * (1.0 - _sc(205.6, 206.0, t))

    out = []
    for i, az in enumerate((-50.0, 50.0)):          # one tower each side, framing Zion
        c = ZC + 380.0 * _dir(az, 0.0) + _v(0.0, 4.0, 0.0)
        out.append(CloudBank(c, size=(260.0, 210.0, 120.0), puffs=34, seed=80 + i, gain=g_hearts, bright=1.0))
    for i, x in enumerate((190.0, 470.0)):                  # the canyon of the last build
        c = _v(x, 2.0, -760.0)
        out.append(CloudBank(c, size=(80.0, 170.0, 1100.0), puffs=46, seed=90 + i, gain=g_canyon, bright=0.65))
    # (round 6: the three banks under and behind the sky orchestra are gone: seen from beside the players they
    # lay as a white band across them; the sea of cloud far below (Clouds) gives the depth)
    for i, da in enumerate((-14.0, 13.0)):                  # banks either side of the rising sun, far behind Zion
        c = ZC + 1000.0 * _dir(163.0 + da, 0.0)
        c[1] = 2.0
        out.append(CloudBank(c, size=(420.0, 170.0, 160.0), puffs=34, seed=110 + i, gain=g_rise, bright=0.9))
    return out


class EpicSun:
    """(Round 8, Anthony: "the sun needs to be way more epic looking") the coda's sunrise (3:19.6 on, over Zion) as a
    huge radiant sun on the core's sun direction: a blazing disc, white-gold at its heart; a layered corona in gold,
    rose and lavender that breathes on the beats; long rays, long and short in turn, turning slowly and reaching
    further on the brass and the kicks; and a band of light breaking along the horizon. Nothing of it crosses the
    words: while a phrase reads, whatever falls in its band of the frame fades (the disc keeps low by the horizon)."""
    wants_camera = True
    D = 3000.0

    def __init__(self):
        r = np.random.default_rng(203)
        n = 1400
        rr = np.sqrt(r.random(n))
        a = r.uniform(0, 2 * np.pi, n)
        self.disc = np.stack([rr * np.cos(a), rr * np.sin(a)], 1)
        self.disc_c = lin("#fff6e0") * (1.0 - rr[:, None] ** 2) + lin("#ffc070") * rr[:, None] ** 2
        self.ring = [(1.5, "#ffe2a0", 0.10), (2.3, "#ffb0a0", 0.07), (3.4, "#d8b0ff", 0.05), (5.0, "#ffd0e8", 0.035)]
        m = 260
        a = np.linspace(0, 2 * np.pi, m, endpoint=False)
        self.cs = np.stack([np.cos(a), np.sin(a)], 1)
        self.jit = r.uniform(0.85, 1.15, m)
        self.nray = 28
        self.ray_len = np.where(np.arange(self.nray) % 2 == 0, 16.0, 8.5) * r.uniform(0.85, 1.15, self.nray)
        self.ray_ph = r.random(self.nray)
        self.hz = r.normal(0.0, 1.0, (900, 2))

    def k(self, t):
        if globe_view(t) or stage_view(t) or local_k(t) <= 0.0 or not (199.6 <= t < 224.03):
            return 0.0
        return _sc(199.6, 201.73, t) * (1.0 - _sc(223.4, 224.03, t))

    def sample(self, t, cam=None):
        k = self.k(t)
        if k <= 0.0 or cam is None:
            return None
        import songs.s11_light as L
        e = np.asarray(cam.pos, np.float64)
        d = _dir(L.sun_az(t), L.sun_el(t))
        c = e + self.D * d
        rgt, up, _f = cam.basis()
        # the sun's own axes in the sky (right along the horizon, up toward the zenith)
        sx = _unit(np.cross(d, _v(0.0, 1.0, 0.0)) * -1.0)
        sy = _unit(np.cross(sx, d))
        R = self.D * np.tan(np.radians(2.4))                   # the disc: about 5 degrees across
        kick = hit_pulse(t, KICKS, rise=0.02, fall=0.45)
        slam = hit_pulse(t, [SLAM3], rise=0.02, fall=0.6)
        beat = beat_pulse(t)
        swell = 1.0 + 0.25 * beat + 0.4 * kick + mx(t, brass=0.5)
        # (f35) over the summit at 3:33.5 to 3:39.5 the sun burns at half, swelling only on the beats
        q = _win(t, 213.5, 219.5, 0.6, 0.6)
        k = k * (1.0 - q * (0.55 - 0.35 * beat - 0.3 * kick))
        rd = reading(t)

        def guard(P):
            """Fade what falls in the words' band (the middle of the frame) while a phrase reads."""
            if rd <= 0.0:
                return np.ones(len(P))
            xy, z = cam.project(P)
            band = _ss(0.24, 0.32, xy[:, 1]) * (1.0 - _ss(0.72, 0.8, xy[:, 1]))
            return 1.0 - 0.85 * rd * band * (z > 0.0)
        out = []
        P = c + R * (self.disc[:, :1] * sx + self.disc[:, 1:] * sy)
        out.append(dict(pos=P, size=R * 0.22, color=self.disc_c, alpha=k * guard(P) ** 0.5, emit=6.0 + 3.0 * slam,
                        kind="soft", fog=False, dof=0.0, reflect=False))
        out.append(dict(pos=c[None], size=R * 3.2, color=lin("#ffd9a0"), alpha=np.array([0.35 * k * swell]),
                        emit=2.5, kind="soft", fog=False, dof=0.0, reflect=False))
        for i, (f, col, a0) in enumerate(self.ring):        # the corona
            rr = R * f * (1.0 + 0.06 * np.sin(2.0 * t + i) + 0.08 * beat) * self.jit
            P = c + rr[:, None] * (self.cs[:, :1] * sx + self.cs[:, 1:] * sy)
            out.append(dict(pos=P, size=R * (0.5 + 0.35 * f), color=lin(col), alpha=3.0 * a0 * k * swell * guard(P),
                            emit=2.2, kind="soft", fog=False, dof=0.0, reflect=False))
        # the rays: long and short in turn, turning slowly, reaching further on the brass and the kicks
        u = np.linspace(0.0, 1.0, 70)
        for j in range(self.nray):
            ang = 2 * np.pi * j / self.nray + 0.03 * t + 0.02 * np.sin(1.3 * t + 6.0 * self.ray_ph[j])
            ln = self.ray_len[j] * (0.8 + 0.35 * swell + 0.6 * slam)
            rr = R * (1.1 + ln * u)
            dv = np.cos(ang) * sx + np.sin(ang) * sy
            P = c + rr[:, None] * dv[None, :]
            a = k * (1.0 - u) ** 1.6 * (0.55 + 0.45 * np.sin(np.pi * self.ray_ph[j] + 0.7 * t) ** 2)
            a = a * (0.6 if np.sin(ang) > 0.0 else 1.0)              # the upward rays a little softer
            g = guard(P)
            out.append(dict(pos=P[:-1], pos2=P[1:], size=R * (0.05 + 0.03 * u[:-1]), color=lin("#fff0cc"),
                            alpha=np.minimum(0.9 * a[:-1] * g[:-1], 1.0), alpha2=np.minimum(0.9 * a[1:] * g[1:], 1.0),
                            emit=2.6 + 1.5 * slam, kind="line", fog=False, dof=0.0, reflect=False))
            out.append(dict(pos=P[::3], size=R * 0.35, color=lin("#ffd9a8"), alpha=0.10 * a[::3] * g[::3],
                            emit=1.5, kind="soft", fog=False, dof=0.0, reflect=False))
        # light breaking along the horizon on either side of the sun
        hz = self.hz
        P = c + R * (hz[:, :1] * 14.0 * sx + hz[:, 1:] * 0.35 * sy) - R * 0.8 * sy
        w = np.exp(-np.abs(hz[:, 0]) / 1.4)
        out.append(dict(pos=P, size=R * 0.9, color=lin("#ffc890") * 0.9 + lin("#ff9ab0") * 0.1,
                        alpha=0.18 * k * w * swell * guard(P), emit=1.8, kind="soft", fog=False, dof=0.0, reflect=False))
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
            a = k * (1.0 - u) ** 1.3 * _under_thanks(P, t)
            col = self.cols[i]
            Pv, av, uv = P[vis], a[vis], u[vis]
            w = 1.1 * (1.0 - 0.8 * uv)
            out += [dict(pos=Pv, size=w * 2.4, color=col, alpha=0.3 * av, kind="soft", emit=2.0, dof=0.0, reflect=False),
                    dict(pos=Pv, size=w * 0.45, color=col * 0.5 + lin(WHITE) * 0.5, alpha=av, kind="spark",
                         emit=3.0 * pulse, dof=0.0, reflect=False)]
            if vis[0]:
                kh = k * float(_under_thanks(P[:1], t)[0])
                out += [dict(pos=P[:1], size=6.0, color=col, alpha=0.5 * kh * pulse, kind="soft", emit=3.0, dof=0.0,
                             reflect=False),
                        dict(pos=P[:1], size=1.4, color=lin(WHITE), alpha=kh, kind="spark", emit=6.0 * pulse, dof=0.0,
                             reflect=False)]
            # the arrival: a flash of its colour on Zion
            d = t - (self.L[i] + self.fly)
            if 0.0 <= d < 1.2:
                zp = c + R * 1.02 * (zv @ T.T)
                out.append(dict(pos=zp[None, :], size=8.0 + 10.0 * d, color=col, alpha=0.5 * np.exp(-d / 0.4),
                                kind="soft", emit=3.0, dof=0.0, reflect=False))
        return out or None


def _emblem_template(stride=4):
    """(Round 8, Anthony: "Instead of having hearts use the church logo") the church emblem as a sprite of points
    in its own colours, traced from EMBLEM_MASK (read-only from s11_church): the sky-blue band and globe, lighter
    toward the top, the white lettering and globe lines, the soft white ring. Unit size (x, y in -0.5..0.5).
    Returns (xy, colour, size factor)."""
    cache = getattr(_emblem_template, "cache", {})
    if stride in cache:
        return cache[stride]
    from songs.s11_church import emblem_mask
    m = emblem_mask()[::stride, ::stride]
    n = m.shape[0]
    out_xy, out_c, out_s = [], [], []
    for cls, sz in ((1, 0.45), (3, 0.6), (2, 1.0)):            # (size factor doubles as the class's strength)
        r, c = np.nonzero(m == cls)
        xy = np.stack([(c - (n - 1) / 2.0) / n, -(r - (n - 1) / 2.0) / n], 1)
        if cls == 1:
            u = np.clip(xy[:, 1] + 0.5, 0.0, 1.0)[:, None]
            col = lin("#3c9ff0") * (1.0 - u) + lin("#86d4ff") * u
        elif cls == 2:
            col = np.broadcast_to(lin("#ffffff"), (len(xy), 3))
        else:
            col = np.broadcast_to(lin("#dcefff") * 0.8, (len(xy), 3))
        out_xy.append(xy)
        out_c.append(np.asarray(col))
        out_s.append(np.full(len(xy), sz))
    cache[stride] = tuple(np.concatenate(x) for x in (out_xy, out_c, out_s))
    _emblem_template.cache = cache
    return cache[stride]


def _emblem_sprites(c, sz, a, cam, glow=1.0, stride=4):
    """Glowing church emblems facing the camera at centres c (N, 3), sizes sz (N,), strength a (N,)."""
    xy, col, f = _emblem_template(stride)
    rgt, up, _f = cam.basis()
    m = len(xy)
    P = c[:, None, :] + sz[:, None, None] * (xy[None, :, 0, None] * rgt[None, None, :] + xy[None, :, 1, None] * up[None, None, :])
    step = 0.9 * stride / 128.0
    return [dict(pos=P.reshape(-1, 3), size=(sz[:, None] * step * np.ones(m)[None, :]).ravel(),
                 color=np.tile(col, (len(c), 1)), alpha=(a[:, None] * f[None, :]).ravel(), emit=1.6 * glow,
                 kind="spark"),
            dict(pos=c, size=1.0 * sz, color=lin("#5fb4ff"), alpha=0.05 * a, emit=1.2 * glow, kind="soft")]


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
        # (round 8) the church emblem rises, glowing, instead of hearts (every other one: fewer, larger)
        keep = np.arange(len(c)) % 2 == 0
        return _emblem_sprites(c[keep], 1.7 * sz[keep], a[keep], cam, glow, stride=2)


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


SKY_PC = (ORCH_P + SKY_OFF).mean(0) * _v(1.0, 0.0, 1.0) + _v(0.0, SKY_STAGE[1], 0.0)   # the players' middle
SKY_RX = float(np.abs((ORCH_P + SKY_OFF)[:, 0] - SKY_PC[0]).max()) + 3.0              # the floor's half sizes
SKY_RZ = float(np.abs((ORCH_P + SKY_OFF)[:, 2] - SKY_PC[2]).max()) + 3.0


class Clouds:
    """The clouds of light the orchestra plays on, round the rising sun (the coda): a thin floor of cloud
    under the players (round 6: it lies only below their feet, a flat luminous floor they sit and stand on,
    falling away in a soft billow under its rim, never round or behind them, so they read clearly), a sea of
    cloud far below in rose, violet and gold, and banks of cloud lit gold round the sun, low on the horizon."""

    def __init__(self):
        r = np.random.default_rng(141)
        # the floor under the orchestra: an ellipse just under the players, flat on top, its rim curling down
        n = 4200
        a = 2 * np.pi * r.random(n)
        u = np.sqrt(r.random(n))
        bill = 0.6 * np.sin(3.0 * a + 1.3) + 0.4 * np.sin(7.0 * a)
        rx, rz = SKY_RX * (1.0 + 0.10 * bill), SKY_RZ * (1.0 + 0.10 * bill)
        top = SKY_STAGE[1] - 0.25                # below every foot (the seated players rest on it)
        pod = SKY_STAGE + _v(0.0, 0.0, 9.5)      # the conductor's place: the risers step up behind it
        px, pz = SKY_PC[0] + rx * u * np.sin(a), SKY_PC[2] + rz * u * np.cos(a)
        rp = np.hypot(px - pod[0], pz - pod[2])
        top = top + np.where(pz < pod[2], 0.3 * _ss(6.8, 7.4, rp) + 0.3 * _ss(8.8, 9.4, rp), 0.0)
        self.P = np.stack([px, top - 0.35 * r.random(n) - 9.0 * np.clip(u - 0.78, 0.0, None) ** 1.5 * (0.5 + r.random(n)),
                           pz], 1)
        self.s = r.random(n)
        self.pu = u
        warm = np.asarray([lin("#ffe2c8"), lin("#ffc8d0"), lin("#e8d0ff")])
        self.pc = warm[r.integers(0, 3, n)]
        # the sea of cloud far below, coloured by where it lies against the sun
        m = 2600
        a = 2 * np.pi * r.random(m)
        rr = 80.0 + 520.0 * np.sqrt(r.random(m))
        self.F = np.stack([SKY_STAGE[0] + rr * np.sin(a), SKY_STAGE[1] - 70.0 - 40.0 * r.random(m),
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
        el = -3.0 + 4.0 * r.random(k) ** 1.5            # low on the horizon, under the players' line
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
        rim = 0.5 + 0.5 * self.pu ** 2
        # the floor: a thin glow (small puffs, low alpha) and a glitter of gold on it that sparkles on the beat
        return [dict(pos=self.P + drift, size=0.4 + 0.5 * self.s, color=self.pc, alpha=0.009 * rim, emit=1.0,
                     kind="soft", seed=self.s, dof=0.0),
                dict(pos=self.P[::5] + drift, size=0.045, color=lin(GOLD2), alpha=0.42 * pulse, emit=2.0,
                     kind="spark", twinkle=0.8, seed=self.s[::5]),
                dict(pos=self.F, size=self.fs, color=self.fc, alpha=0.022, emit=1.0, kind="soft", dof=0.0,
                     reflect=False),
                dict(pos=self.B, size=self.bs, color=self.bc, alpha=0.045, emit=1.2, kind="soft", dof=0.0,
                     reflect=False)]


def _music_gain(t):
    """Brightness of the people of light with the music: the beat, the hits, the swell."""
    return 0.8 + 0.3 * intensity(t) + 0.18 * beat_pulse(t) + 0.45 * hit_pulse(t, KICKS, rise=0.02, fall=0.4)


def sky_gain(t):
    return sky_k(t) * _music_gain(t) * (1.0 + mx(t, strings=0.25, brass=0.2))    # (round 8) the players glow as they play


def summit_gain(t):
    return summit_k(t) * _music_gain(t) * (1.0 + mx(t, choir=0.3))             # (round 8) everyone shines with the choir


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
        if abs(x) < 3.0 or np.hypot(x - ZC[0], z - ZC[2]) > R_TOP - 9.0:     # an aisle up the middle
            continue
        pts.append((x, SUMMIT, z))
    while len(pts) < n:
        x = r.uniform(16.0, 38.0) * (1.0 if r.random() < 0.5 else -1.0)
        z = r.uniform(FACADE_Z - 8.0, FACADE_Z + 20.0)
        pts.append((x, SUMMIT, z))
    return np.asarray(pts)


def _nine_tints(n, seed, white=0.3, group=1):
    """Colours for people: the nine colours (in groups of `group` neighbours, like nations walking together),
    softened with warm white, so a crowd reads as many peoples, not one gold mass."""
    r = np.random.default_rng(seed)
    nine = np.asarray([lin(c) for c in COL9])
    k = (np.arange(n) // group * 4) % 9 if group > 1 else r.integers(0, 9, n)
    w = white + 0.15 * r.random(n)
    return nine[k] * (1.0 - w)[:, None] + lin("#fff0d8")[None, :] * w[:, None]


def _stair_path(avenue=False):
    """The way up one of the great stairways, from the sea to the summit's edge: (length, r, y) knots (the
    same steps as the mountain's: one flight against each wall, then across the terrace above). The front
    one (avenue=True) goes on up the great avenue to the square before the church."""
    pts = [(tier_r(0) + 60.0, 0.1), (tier_r(0) + 14.0, 0.1), (tier_r(0), tier_y(0) + 0.1)]
    for k in range(1, N_TIER):
        pts.append((tier_r(k) + 14.0, tier_y(k - 1) + 0.1))
        pts.append((tier_r(k), tier_y(k) + 0.1))
    pts.append((R_TOP - 6.0, SUMMIT + 0.05))
    if avenue:
        pts.append((FACADE_Z + 34.0 - float(ZC[2]), SUMMIT + 0.05))    # to the orchestra's square
    pts = np.asarray(pts)
    L = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    return L, pts


STAIRS = np.radians([0.0, -36.0, 36.0, -72.0, 72.0])     # the great stairways (azimuth from +z), as Zion's
STAIR_HW = (8.0, 5.0, 5.0, 5.0, 5.0)                     # their half widths


def stream_k(t):
    """The multitude streaming up to the summit: in the coda's views of Zion (not the close stage shots, not
    the Earth), from thanks to Mother to the world finale."""
    if globe_view(t) or stage_view(t) or not (188.0 <= t < 224.1):
        return 0.0
    return _sc(188.0, 189.0, t) * (1.0 - _sc(223.6, 224.1, t))


class Streams:
    """Round 6 (Anthony: "more scenes where the people are streaming to Zion ... the church of God"): the
    multitude streaming up the five great stairways of Zion to the summit, and up the great avenue to the
    church, filling each stairway, the nations walking together in bands of the nine colours. Each person is
    a small figure of light (a stroke, dim at the feet and bright at the head, with a head spark) that walks
    up, bobbing with each step; they come up out of the sea and are taken into the crowd on the summit (the
    front stream walks on up the aisle of the avenue, between everyone standing there, to the church). With
    the music: on every beat a wave of light runs up each stream to the summit, the hits flare them, and the
    waves of raised arms (ARM_WAVES) reach them too."""

    SPEED = 1.5           # walking, metres per second
    WAVE = 42.0           # the beat's wave of light up the stream, metres per second
    AISLE = 2.2           # the half width of the aisle up the avenue

    def __init__(self, gain=stream_k, gap=2.6, seed=181):     # (round 8) 2.6 m apart (1.2 packed into white bands)
        r = np.random.default_rng(seed)
        self.paths = [_stair_path(avenue=(i == 0)) for i in range(len(STAIRS))]
        grp, l0, lane = [], [], []
        for i, (L, _p) in enumerate(self.paths):
            hw = STAIR_HW[i] - 1.0
            lanes = int(round(2.0 * hw / 1.4)) + 1
            ns = int(L[-1] / gap)
            m = ns * lanes
            grp.append(np.full(m, i))
            l0.append(np.repeat(np.arange(ns) * gap, lanes) + r.uniform(-0.4, 0.4, m))
            lane.append(np.tile(np.linspace(-1.0, 1.0, lanes), ns) * hw + r.uniform(-0.3, 0.3, m))
        self.grp, self.l0, self.lane = np.concatenate(grp), np.concatenate(l0), np.concatenate(lane)
        self.Lt = np.asarray([self.paths[i][0][-1] for i in self.grp])
        # of the front stream only the middle lanes walk on up the avenue's aisle; the rest join the crowd at
        # the top of the stairs
        edge = self.paths[0][0][-2]
        self.Lt = np.where((self.grp == 0) & (np.abs(self.lane) > self.AISLE), edge, self.Lt)
        self.az = STAIRS[self.grp]
        n = len(self.grp)
        self.n = n
        self.h = r.uniform(0.85, 1.08, n)
        self.ph = r.random(n) * 2.0 * np.pi
        self.sp = self.SPEED * r.uniform(0.92, 1.08, n)
        # (round 7, review f23: the rivers of people as clear coloured lines) one colour per lane, side by side
        band = (np.floor((self.lane + 8.0) / 2.8).astype(int) * 4 + 2 * self.grp) % 9
        nine = np.asarray([lin(c) for c in COL9])
        w = 0.06 + 0.08 * r.random(n)
        self.col = nine[band] * (1.0 - w)[:, None] + lin("#fff0d8")[None, :] * w[:, None]
        self.s = r.random(n)
        self.g = gain
        self.arms = None
        try:
            from songs.s11_zion import Arms
            self.arms = Arms(np.zeros((n, 3)), np.full(n, -1e9), seed + 1, gain)
            self.arms.col = self.col * 0.7 + lin(WHITE) * 0.3
        except Exception:                    # the zion thread's arms changed: the streams walk without them
            self.arms = None

    def gain(self, t):
        return float(self.g(t))

    def where(self, t):
        """Where everyone is at t: positions (n, 3), their distance along the way, their azimuth, and how far
        up the way they are (0..1)."""
        l = np.mod(self.l0 + self.sp * t, self.Lt)
        rr, y = np.zeros(self.n), np.zeros(self.n)
        for i, (L, p) in enumerate(self.paths):
            m = self.grp == i
            rr[m] = np.interp(l[m], L, p[:, 0])
            y[m] = np.interp(l[m], L, p[:, 1])
        a = self.az + self.lane / np.maximum(rr, 8.0)
        P = np.stack([ZC[0] + rr * np.sin(a), y, ZC[2] + rr * np.cos(a)], 1)
        return P, l, a

    def sample(self, t):
        g = self.g(t)
        if g <= 0.0:
            return None
        P, l, a = self.where(t)
        step = np.abs(np.sin(2.0 * np.pi * t * self.sp / self.SPEED + self.ph))
        foot = P + np.array([0.0, 0.15, 0.0])
        head = P + np.stack([0.0 * self.h, 1.6 * self.h + 0.06 * step, 0.0 * self.h], 1)
        # in out of the sea at the foot, taken into the crowd at the top of the way
        fade = _ss(0.0, 12.0, l) * (1.0 - _ss(self.Lt - 6.0, self.Lt, l))
        # the beat's waves of light running up the streams, the hits, the swell
        i = int(np.searchsorted(BEATS, t))
        wave = np.zeros(self.n)
        for b in BEATS[max(i - 18, 0):i]:
            lf = self.WAVE * (t - b)
            if lf < 400.0:
                wave = np.maximum(wave, np.exp(-((l - lf) / 7.0) ** 2))
        kick = hit_pulse(t, KICKS, rise=0.02, fall=0.45)
        # (round 8) with the strings a shimmer runs up the streams too, as on Zion's rivers
        shim = mx(t, strings=1.0, swell=0.5) * (0.5 + 0.5 * np.sin(0.06 * l - 5.0 * t)) ** 4
        # (round 8) the packed streams added up to white bands on the stairways: each walker shines less, so the
        # rivers keep the colours of their lanes
        br = 0.6 * (0.7 + 0.35 * intensity(t) + 0.55 * kick) * (1.0 + 0.6 * wave + shim) * fade
        # (round 8, "the people read as lines of dots") each walker a small figure, as on Zion's rivers: two legs
        # of light that scissor with the step, a robe up to the shoulders, the head apart above the neck
        hh = self.h[:, None]
        up = np.array([0.0, 1.0, 0.0])
        sd = np.stack([np.cos(a), 0.0 * a, -np.sin(a)], 1)
        fw = -np.stack([np.sin(a), 0.0 * a, np.cos(a)], 1)
        st = np.sin(2.0 * np.pi * t * self.sp / self.SPEED * 0.5 + self.ph)[:, None] * 0.26 * hh
        hip, neck = P + up * (0.78 * hh), P + up * (1.24 * hh)
        hem = hip - up * (0.10 * hh)
        fl, fr = P + sd * 0.10 * hh + fw * st, P - sd * 0.10 * hh - fw * st
        b2, c2 = np.concatenate([br, br]), np.concatenate([self.col, self.col])
        out = [dict(pos=np.concatenate([fl, fr]), pos2=np.concatenate([hip, hip]), size=0.22, color=c2 * 0.8,
                    alpha=0.2 * b2, alpha2=0.45 * b2, kind="line", emit=1.3, reflect=False),
               dict(pos=np.concatenate([hem - sd * 0.2 * hh, hem + sd * 0.2 * hh]), pos2=np.concatenate([neck, neck]),
                    size=0.24, color=c2 * 0.9, alpha=0.4 * b2, alpha2=0.6 * b2, kind="line", emit=1.4, reflect=False),
               dict(pos=head + np.array([0.0, 0.02, 0.0]), size=0.36, color=self.col * 0.92 + lin(WHITE) * 0.08,
                    alpha=0.62 * br, kind="spark", emit=2.2, twinkle=0.25, seed=self.s, reflect=False),
               dict(pos=head[::3], size=2.0, color=self.col[::3], alpha=0.03 * br[::3] * wave[::3],
                    kind="soft", emit=1.3, reflect=False)]
        if self.arms is not None:
            self.arms.P = P
            self.arms.u = np.clip(l / self.Lt, 0.0, 1.05)
            self.arms.side = np.stack([np.cos(a), 0.0 * a, -np.sin(a)], 1)
            self.arms.out = np.stack([np.sin(a), 0.0 * a, np.cos(a)], 1)
            arms = self.arms.sample(t)
            if arms:
                out += arms
        return out


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
        res = []
        for b in out:
            if b.get("kind") != "heart":
                res.append(b)
            elif t >= 188.0:      # (round 8, "instead of having hearts use the church logo"): the coda's are emblems
                pos = np.asarray(b["pos"], np.float64)
                n = len(pos)
                sz = np.broadcast_to(np.asarray(b["size"], np.float64), (n,)) * 1.3
                al = np.broadcast_to(np.asarray(b["alpha"], np.float64), (n,))
                for e in _emblem_sprites(pos, sz, al, cam, 1.0, stride=2):
                    e["dof"] = b.get("dof", 0.0)
                    e["reflect"] = False
                    res.append(e)
            else:
                res.append(_heart_sprites(b, cam))
        return res
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


def _quiet_horizon_in_sky(scene):
    """From the orchestra on the clouds (230 m up) the core's banks of cloud on the horizon lie below the
    players and show as stray white puffs round them; the coda hides them in its sky shot only, until the core
    does (request in the round 6 report)."""
    for name in scene.names():
        if name.startswith("horizon clouds "):
            cb = scene.get(name)
            g = cb.g
            cb.g = (lambda g0: (lambda t: 0.0 if sky_k(t) > 0.0 else g0(t)))(g)


def add(scene):
    _patch_globe_hearts()
    _quiet_horizon_in_sky(scene)
    scene.add("rising hearts", RisingHearts())
    scene.add("horizon", Horizon())
    scene.add("epic sun", EpicSun(), reflect=False)
    # the orchestra on clouds of light round the rising sun
    scene.add("clouds", Clouds())
    # (round 8, Anthony: "the orchestra is playing but also bowing down. Do not have them bow") the stage's own
    # players, upright, playing in time with their gold instruments (the generic sitting crowd leaned forward)
    scene.add("sky orchestra", Players(gain=sky_gain, offset=SKY_OFF, start=0.0, color="#6cb2ff", color2="#d2e8ff",
                                       bright=3.6, points=3400, size=1.2, glints=0.006, dof=0.35, seed=4.0))
    scene.add("sky instruments", Instruments(offset=SKY_OFF, gain=sky_k))
    # everyone on the summit, from the coda's sunrise to the last chord
    # their arms go up as each wave of praise rolls up the mountain and reaches them (the coda hit's wave
    # arrives on SLAM 3, then the waves of praise on the beat, the hits)
    sp = _summit_places()
    summit = WaveCrowd(delay=wave_u(sp), gain=summit_gain, places=sp, facing=180.0,
                       kinds=(("raise", 3.0), ("stand", 0.5), ("cheer", 1.5)),
                       people=dict(woman=1.0, man=1.0, child=0.2),
                       start=dict(t=201.0, center=(0.0, FACADE_Z), speed=40.0), color="#ffc870",
                       color2="#fff2d8", bright=1.9, size=2.8, points=500, glints=0.012, seed=41.0)
    # round 6: the people of every nation, not one gold mass: each little group in one of the nine colours
    order = np.lexsort((np.round(sp[:, 0] / 4.0), np.round(sp[:, 2] / 4.0)))
    tint = np.empty((len(sp), 3))
    tint[order] = _nine_tints(len(sp), 43, white=0.32, group=6)
    summit.tint = tint
    scene.add("summit", summit)
    # round 6: the multitude streaming up the great stairways to the summit and the church
    scene.add("streams", Streams())
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
