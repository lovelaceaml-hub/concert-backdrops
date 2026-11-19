"""Song 11, Almighty God Who Knows the Future: the full-length concert backdrop, version 2 ("The Future
Fulfilled"), designed with Anthony in the song 11 planner (project-docs/backdrops/s11-full2/TIMELINE.md).

Loaded by tools/s11_full2/render.py as the engine song `songs.s11_full2` on the pinned Film 10 engine (commit
d928ff9) with Claude Final v1's words, people and crowds (commit f43f451) and the repo's brand modules (the
globe of light). Fully rendered: no painted plates and no generated images anywhere.

The journey: the waiting heavenly city on Mount Zion, out over the whole Earth, back to Mount Zion (higher at
each "standing firm" line), the sun rising over Zion, the whole world, and home to everyone on Mount Zion.
Times are song seconds (0 is the first sample of the recording; the music runs 0.84 to 259.95; the video
holds 15 s more, calm, to 275.0). Every number of the music below was measured on the recording.
No em dash or en dash anywhere in this file.
"""
import os
import sys
from pathlib import Path

import numpy as np

import songs.s03_original as _base

S11_HERE = Path(__file__).resolve().parent
REPO = S11_HERE.parents[1]

FPS = 60
LIVE = 260.0
TOTAL = LIVE + 15.0
_base.FPS = FPS
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * FPS))
_base.MUSIC_END = 259.95
_base.SONG_END = LIVE
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])          # never black
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9                     # all words here are particle words in 3D
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.api import ribbon  # noqa: E402
from p3d.camera import Move, Rig, fly  # noqa: E402
from p3d import brand as _brand  # noqa: E402,F401  (import order: brand first, then its world)
from p3d.brand_world import Globe, _earth  # noqa: E402

sys.path.insert(0, str(REPO / "tools/nine_colours_minor"))
import reference  # noqa: E402,F401  (Claude Final v1 as package nine_reference_p3d)
from nine_reference_p3d import words as PW  # noqa: E402
from nine_reference_p3d import master_acting  # noqa: E402,F401
from nine_reference_p3d.crowd import Crowd  # noqa: E402

AUDIO_FILE = os.environ.get("AUDIO", "")
FPS = 60
TOTAL = LIVE + 15.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 259.95
SONG_END = LIVE
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# =========================================================================================================
# The music (measured on the recording; TIMELINE.md)
# =========================================================================================================
BEATS = None                                   # filled from the features below
SLAM1, SLAM2, SLAM3 = 82.08, 162.86, 201.73    # the low end comes back in at once
DROP1, DROP2, DROP3 = 75.2, 156.0, 197.2       # the builds: the low end drops out
CODA = 199.62
STEP_DOWN = 240.19
HELD = (247.5, 249.5)                          # the held breath before the last "the Church of God"
LAST_CHORD = 254.07                            # V to I lands (4:14.1)
HIT = dict(first=2.32, call1=21.52, call2=31.11, father=40.54, glory=53.78, step1=64.2, step2=65.94,
           step3=69.4, nations=70.54, stream=74.56, firm1=90.72, sacrifice=105.14, thanks=109.18,
           mother=121.32, trust=130.29, march=134.54, fulfilled=146.7, kings1=154.2, kings2=155.34,
           firm2=171.48, love=185.92, thanks2=189.96, coda=199.62, devotion=224.03, peak=235.6,
           final=249.43)
FULFIL = [144.4, 145.0, 146.7, 149.6, 150.2]   # verse 2 "fulfilled": a quickening heartbeat of accents
STRINGS = [121.32, 124.18, 127.64]             # verse 2 opening: strings pulse

COL9 = [PW.COLORS[k] for k in PW.LABELS]       # the nine campaign colours
GOLD = "#ffc664"
GOLD2 = "#fff0c8"
WHITE = "#fff6e6"
SILVER = "#b9cdf5"
CRYSTAL = "#d8ecff"
ROSE = "#ffb3c4"
VIOLET = "#c9b3ff"


def _ss(a, b, x):
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    if a.ndim == 0 and b.ndim == 0 and b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / np.maximum(b - a, 1e-9), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _win(t, a, b, fi=1.0, fo=1.0):
    """1 inside [a, b], easing in over fi and out over fo seconds."""
    return _sc(a - fi, a, t) * (1.0 - _sc(b, b + fo, t))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _unit(a):
    a = np.asarray(a, np.float64)
    return a / max(float(np.linalg.norm(a)), 1e-9)


# loudness 0..1 and the beat grid from the engine's own features of the score
_F = np.load(os.environ["FEATURES"])
_FT = _F["times"]
_FR = _F["rms"].astype(np.float64)
_FR = np.convolve(_FR, np.ones(25) / 25.0, mode="same")
_FR = (_FR - np.percentile(_FR, 5)) / max(np.percentile(_FR, 98) - np.percentile(_FR, 5), 1e-9)
_FR = np.clip(_FR, 0.0, 1.0)
BEATS = np.asarray(_F["beat_t"], np.float64)
BEATS = BEATS[BEATS < LIVE]


def loud(t):
    return float(np.interp(t, _FT, _FR, left=0.0, right=0.0))


def beat_pulse(t, width=0.09):
    """1 on each beat, falling off quickly (a soft pulse of light on every beat)."""
    if t > LIVE:
        return 0.0
    i = np.searchsorted(BEATS, t)
    d = min(abs(t - BEATS[max(i - 1, 0)]), abs(BEATS[min(i, len(BEATS) - 1)] - t))
    return float(np.exp(-d / width))


def hit_pulse(t, times, rise=0.03, fall=0.6):
    """Sum of sharp pulses at the given times."""
    v = 0.0
    for h in times:
        d = t - h
        if -rise < d < 6.0 * fall:
            v += (_sc(-rise, 0.0, d) if d < 0 else np.exp(-d / fall))
    return float(v)


# =========================================================================================================
# The places (metres, y up, the sea of glass is y = 0; the camera mostly looks toward -z)
# =========================================================================================================
ZC = _v(0.0, 0.0, -420.0)          # the foot of Mount Zion
N_TIER = 7
SUMMIT = 70.0                      # the summit plateau's height
R_TOP = 92.0                       # the summit plateau's radius
TIER_STEP = 33.0                   # each terrace below is this much wider


def tier_r(k):
    """Outer radius of terrace k (0 the lowest, N_TIER-1 the summit plateau)."""
    return R_TOP + (N_TIER - 1 - k) * TIER_STEP


def tier_y(k):
    return SUMMIT * (k + 1) / N_TIER


CHURCH = ZC + _v(0.0, SUMMIT, -10.0)   # the church of light at the heart of the city (its footprint centre)
CH_W, CH_D, CH_H, CH_TOWER = 46.0, 26.0, 28.0, 60.0
FACADE_Z = CHURCH[2] + CH_D / 2.0       # its front faces +z, down the great avenue
SQUARE = _v(0.0, SUMMIT, FACADE_Z + 16.0)   # the square in front of it: the orchestra plays here
CHOIR_STEPS = [(SUMMIT + 0.6 + 0.55 * i, FACADE_Z + 4.5 - 1.3 * i) for i in range(4)]

GLOBE_C = _v(0.0, 150.0, 1700.0)    # the Earth of light, far behind the home view (the camera turns to it)
GLOBE_R = 46.0
ZION_LL = (37.40, 127.10)           # where Mount Zion lies on the Earth: the main temple in Korea
SKY_STAGE = _v(0.0, 230.0, -1150.0)  # the orchestra on clouds of light round the rising sun (the coda)


def globe_point(t, lat, lon, h=0.0, cam=None):
    """A place on the Earth of light at t (lat, lon in degrees; h in globe radii above the land)."""
    c, M, R = GLOBE._view(t, cam if cam is not None else CAMERA.state(t))
    T = M @ GLOBE.turn(t)
    v = _earth(np.asarray(lat, np.float64), np.asarray(lon, np.float64)) @ T.T
    return c + (R * (1.0 + h)) * v


# =========================================================================================================
# Building in light: helpers (static point sets: sampled once, kept on the graphics card)
# =========================================================================================================
_R = np.random.default_rng(1105)


def _seg(a, b, step):
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    n = max(int(np.linalg.norm(b - a) / step), 1)
    u = (np.arange(n) + 0.5) / n
    return a[None, :] + (b - a)[None, :] * u[:, None]


def _ring(c, r, y, step, a0=0.0, a1=2.0 * np.pi):
    n = max(int(abs(a1 - a0) * r / step), 3)
    a = a0 + (a1 - a0) * (np.arange(n) + 0.5) / n
    return np.stack([c[0] + r * np.sin(a), np.full(n, y), c[2] + r * np.cos(a)], 1)


def _box(c, w, d, h, step):
    """The twelve edges of a box standing on c (x, y, z: the middle of its floor)."""
    x0, x1, z0, z1, y0, y1 = c[0] - w / 2, c[0] + w / 2, c[2] - d / 2, c[2] + d / 2, c[1], c[1] + h
    P = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    out = []
    for i in range(4):
        (ax, az), (bx, bz) = P[i], P[(i + 1) % 4]
        out += [_seg((ax, y0, az), (bx, y0, bz), step), _seg((ax, y1, az), (bx, y1, bz), step),
                _seg((ax, y0, az), (ax, y1, az), step)]
    return np.concatenate(out)


def _windows(c, w, d, h, floor=3.4, bay=2.6):
    """Warm windows on the four faces of a box."""
    out = []
    nf = max(int((h - 1.0) / floor), 1)
    for f in range(nf):
        y = c[1] + 1.8 + f * floor
        for side in range(4):
            L = w if side % 2 == 0 else d
            nb = max(int(L / bay), 1)
            for b in range(nb):
                s = -L / 2 + (b + 0.5) * L / nb
                if side == 0:
                    p = (c[0] + s, y, c[2] + d / 2 + 0.05)
                elif side == 1:
                    p = (c[0] + w / 2 + 0.05, y, c[2] + s)
                elif side == 2:
                    p = (c[0] + s, y, c[2] - d / 2 - 0.05)
                else:
                    p = (c[0] - w / 2 - 0.05, y, c[2] + s)
                out.append(p)
    return np.asarray(out, np.float64)


def _dome(c, r, step):
    out = []
    for el in np.linspace(0.05, 1.45, 8):
        out.append(_ring(c, r * np.cos(el), c[1] + r * np.sin(el), step))
    for a in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        e = np.linspace(0.0, 1.5, 24)
        out.append(np.stack([c[0] + r * np.cos(e) * np.sin(a), c[1] + r * np.sin(e), c[2] + r * np.cos(e) * np.cos(a)], 1))
    return np.concatenate(out)


def _batch(pos, size, color, alpha, kind="spark", emit=1.0, **kw):
    n = len(pos)
    d = dict(pos=np.asarray(pos, np.float64), size=size, color=color, alpha=alpha, kind=kind, emit=emit)
    d.update(kw)
    if "seed" not in d:
        d["seed"] = _R.random(n)
    return d


class Static:
    """A point set made once (static) with a strength over time."""
    static = True

    def __init__(self, batches, gain):
        self.b = batches
        self.g = gain

    def sample(self, t):
        return self.b

    def gain(self, t):
        return float(self.g(t))


class GCrowd(Crowd):
    """A crowd with a strength over time (nothing is sampled while it is 0)."""

    def __init__(self, gain=None, **kw):
        super().__init__(**kw)
        self.g = gain or local_k

    def gain(self, t):
        return float(self.g(t))

    def sample(self, t):
        if self.g(t) <= 0.0:
            return []
        return super().sample(t)


def _env(t, a, b, fi=1.0, fo=1.0):
    return _sc(a, a + fi, t) * (1.0 - _sc(b - fo, b, t))


# =========================================================================================================
# The camera: one shot after another, cut on the music's hits (each cut hidden in a soft flash of light).
# Every thread's file gives its own shots; the core gathers them below. Until then these lookups see nothing.
# A shot: dict(name, kind ("local", "stage", "sky" or "globe"), t0, t1, keys [(t, pos, target)], fov, aperture,
# focus (optional, a point; default: the target)).
# =========================================================================================================
class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _gcam(d, up=0.0, side=0.0):
    """A camera place in front of the Earth of light (it looks toward +z at it)."""
    return GLOBE_C + _v(side, up, -d)


SHOTS = []
_SHOT_T0 = [0.0]


def shot_of(t):
    """Index of the shot at t (in time order)."""
    return int(max(np.searchsorted(_SHOT_T0, t, side="right") - 1, 0))


def shot_name(t):
    return SHOTS[shot_of(t)]["name"]


def shot_kind(t):
    return SHOTS[shot_of(t)]["kind"]


def globe_view(t):
    return shot_kind(t) == "globe"


def stage_view(t):
    return shot_kind(t) == "stage"


def local_k(t):
    """1 while the camera is on Mount Zion (not looking at the Earth of light)."""
    return 0.0 if globe_view(t) else 1.0


def city_k(t):
    """The city and the church behind the choir and orchestra stay soft in the close shots of them."""
    if globe_view(t):
        return 0.0
    if stage_view(t):
        return 0.3
    if shot_name(t) == "city":
        return 1.0 - 0.6 * _sc(19.0, 22.0, t)
    return 1.0


def _globe_amount(t):
    if not globe_view(t):
        return 0.0
    return 1.0


GLOBE = Globe(pos=tuple(GLOBE_C), radius=GLOBE_R, face="camera", camera=None, look="night", spin=1.2,
              front=ZION_LL[1] - 1.2 * 60.0 - 18.0, tilt=24.0, amount=_globe_amount,
              hearts=dict(t0=226.0, t1=236.5, n=64, size=0.11, start=ZION_LL, colors="nine", pulse=1.0),
              arcs=True, n=70000, bright=1.1)


def _sphere_ring(cv, ang, n):
    """n points on the unit sphere at angle `ang` (radians) round the unit vector cv."""
    a = _unit(np.cross(cv, _v(0.0, 1.0, 0.0)) if abs(cv[1]) < 0.95 else np.cross(cv, _v(1.0, 0.0, 0.0)))
    b = np.cross(cv, a)
    ph = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.cos(ang) * cv[None, :] + np.sin(ang) * (np.cos(ph)[:, None] * a[None, :] + np.sin(ph)[:, None] * b[None, :])


class GlobeFX:
    """On the Earth: Father's pulse (rings of light rolling out from Zion, 0:40.5), the rivers of people from
    every continent flowing to Zion (1:10.5 to 1:17), the light from every land to Zion (the world finale)."""
    wants_camera = True
    STARTS = [(42.0, -100.0), (-12.0, -55.0), (50.0, 8.0), (6.0, 20.0), (-28.0, 25.0), (28.0, 46.0),
              (22.0, 78.0), (-25.0, 134.0), (60.0, 95.0), (14.0, 101.0), (-6.0, 110.0), (55.0, 40.0)]

    def __init__(self):
        r = np.random.default_rng(23)
        self.s = r.random((len(self.STARTS), 360, 3))

    def _frame(self, t, cam):
        c, M, R = GLOBE._view(t, cam)
        return c, M @ GLOBE.turn(t), R

    def sample(self, t, cam=None):
        if not globe_view(t) or cam is None:
            return None
        c, T, R = self._frame(t, cam)
        zv = _earth(*ZION_LL)
        out = []
        eye = np.asarray(cam.pos, np.float64)

        def front(p):
            n = (p - c) / np.linalg.norm(p - c, axis=1, keepdims=True)
            return ((eye[None, :] - p) * n).sum(1) > 0.0

        # Father's pulse: rings from Zion, one on the bell (0:40.5), echoes on the next bars
        for t0 in (41.6, 44.4, 47.5):
            u = t - t0
            if 41.6 <= t < 53.78 and 0.0 < u < 7.0:
                ang = np.radians(4.0 + 26.0 * u)
                if ang < np.pi * 0.95:
                    v = _sphere_ring(zv, ang, 900) @ T.T
                    p = c + R * 1.01 * v
                    f = front(p)
                    a = np.exp(-u / 3.0) * (1.0 if t0 == 41.6 else 0.55)
                    out.append(dict(pos=p[f], size=0.55, color=lin("#ffe6b8"), alpha=a, emit=3.0, kind="spark",
                                    dof=0.0, reflect=False))
        # Zion itself: a warm light on Korea
        zp = c + R * 1.01 * (zv @ T.T)
        if ((eye - zp) @ (zp - c)) > 0:
            k = 0.8 + 1.4 * hit_pulse(t, [HIT["stream"]], fall=1.5) + 0.4 * beat_pulse(t)
            out.append(dict(pos=zp[None, :], size=3.0, color=lin("#ffe2a8"), alpha=0.35 * k, kind="soft", emit=2.0,
                            reflect=False))
            out.append(dict(pos=zp[None, :], size=0.9, color=lin(WHITE), alpha=min(k, 1.5), kind="spark", emit=5.0,
                            reflect=False))
        # the rivers of people (1:10.5 to 1:17.5): streams of light along the Earth to Zion, meeting on 1:14.56
        if 70.0 <= t < 77.46 or 226.0 <= t < 238.8:
            meet = HIT["stream"] if t < 100 else 236.0
            start = 70.3 if t < 100 else 226.0
            for i, (la, lo) in enumerate(self.STARTS):
                sv = _earth(la, lo)
                s = self.s[i]
                prog = np.clip((t - start) / (meet - start), 0.0, 1.0)
                f = np.clip(prog * (1.0 + 0.6 * s[:, 0]) - 0.6 * s[:, 0], 0.0, 1.0)
                f = f * 0.98 + 0.02 * s[:, 1]
                om = np.arccos(np.clip(sv @ zv, -1, 1))
                w0 = np.sin((1 - f) * om) / np.sin(om)
                w1 = np.sin(f * om) / np.sin(om)
                v = w0[:, None] * sv[None, :] + w1[:, None] * zv[None, :]
                v = v / np.linalg.norm(v, axis=1, keepdims=True)
                v = v + 0.012 * (s - 0.5)
                lift = 1.012 + 0.05 * np.sin(np.pi * f)
                p = c + R * lift[:, None] * (v @ T.T)
                on = (f > 0.0) & front(p)
                col = lin(COL9[i % 9]) * 0.6 + lin(WHITE) * 0.4
                a = 0.9 * (1.0 - _sc(meet + 0.3, meet + 1.6, t))
                out.append(dict(pos=p[on], size=0.30 + 0.25 * s[on, 2], color=col, alpha=a, emit=2.6,
                                kind="spark", dof=0.0, reflect=False, twinkle=0.6, seed=s[on, 1]))
        # the build (1:15.2): the Earth's rim glows brighter as if the sun were coming
        if 74.0 <= t < 77.46:
            k = _sc(75.2, 77.4, t)
            rim = _sphere_ring(_unit(np.linalg.inv(T) @ _unit(eye - c)), np.pi / 2 * 0.985, 1600) @ T.T
            p = c + R * 1.03 * rim
            out.append(dict(pos=p, size=1.2, color=lin("#ffd9a0"), alpha=0.35 * k, kind="soft", emit=2.0,
                            reflect=False))
        return out or None


# =========================================================================================================
# The threads' scenes (each in its own file; see the docstring of each)
# =========================================================================================================
# =========================================================================================================
# THE EDIT: music-video pace. Every cut lands on a measured bar or hit; quiet parts hold 2 to 4 bars, builds
# cut every bar and speed up into the slam, choruses and the coda cut every bar with intercuts of choir and
# orchestra, Mount Zion, the church, the procession and the Earth. (start time, owner, what the block shows)
# Each thread gives one shot per block it owns, with exactly that t0 and t1 (core falls back to an older
# shot of that owner, clipped, until it does). Owners: church, stage, zion, proc, coda, core (the Earth).
# =========================================================================================================
EDIT = [
    (0.0, "church", "title over the waiting city"),
    (11.9, "church", "paths of light reach out; glide toward the city"),
    (16.7, "church", "down the great avenue toward the church"),
    (21.52, "church", "call 1: the choir forms out of the light on the steps"),
    (26.33, "stage", "the orchestra wakes at dawn, choir behind (D minor)"),
    (31.11, "church", "call 2: the church of light, the choir before it"),
    (35.9, "stage", "harps and strings, low F pedal"),
    (38.24, "church", "brightest moment of the intro; rise toward the sky"),
    (40.54, "church", "Father's bell-like pulse from the church"),
    (41.6, "core", "the whole Earth: Father's pulse rolls out"),
    (45.6, "core", "closer on the Earth, echoes of the pulse"),
    (49.8, "core", "the Earth turns toward Zion"),
    (53.78, "zion", "glory: the crown of light ignites"),
    (56.7, "zion", "G lift: the crown seen closer"),
    (58.4, "church", "the church under the crown"),
    (61.3, "zion", "the city on the summit"),
    (64.2, "zion", "fulfilled: step 1, the terraces fill with gold"),
    (65.94, "zion", "step 2"),
    (67.6, "stage", "timpani and strings"),
    (69.4, "zion", "step 3: the city full of gold"),
    (70.54, "core", "all nations: rivers of light on the Earth"),
    (72.84, "core", "the rivers closer"),
    (74.56, "church", "streaming: the church of light shines out"),
    (75.2, "core", "the drop: the Earth's rim glows"),
    (77.46, "stage", "the choir breathes in"),
    (78.62, "stage", "light gathering in the choir"),
    (79.78, "stage", "the orchestra holds its breath"),
    (80.94, "church", "the church gathering light"),
    (81.51, "stage", "the last half bar into the slam"),
    (82.08, "stage", "SLAM 1: the full choir and orchestra"),
    (84.4, "stage", "the choir in full voice"),
    (86.7, "zion", "waves of praise ripple over the land"),
    (88.0, "stage", "brass and strings"),
    (89.3, "zion", "waves of praise, closer"),
    (90.72, "zion", "standing firm: the first climb, the nations on Zion"),
    (93.0, "stage", "the choir"),
    (95.4, "zion", "the nations on the terraces"),
    (97.7, "church", "the church above the nations"),
    (99.4, "zion", "sacrifice: light pours over the people"),
    (101.7, "stage", "the orchestra in full"),
    (103.6, "zion", "devotion: the golden waterfall"),
    (105.14, "stage", "the brass and timpani blaze"),
    (106.5, "zion", "the people lit by the pouring light"),
    (108.4, "church", "the church glowing"),
    (109.8, "zion", "thanks to Father: the column of light rises"),
    (112.1, "church", "the column from the church"),
    (114.4, "zion", "the column to heaven over Zion"),
    (117.0, "stage", "the breath: the choir still, light falling like snow"),
    (121.32, "stage", "verse 2: the strings pulse"),
    (124.18, "stage", "strings and harp"),
    (125.92, "proc", "Mother: her light comes down out of the sky"),
    (127.64, "proc", "her light touches the sea; everyone gathers"),
    (130.29, "proc", "let's trust Father"),
    (132.5, "proc", "everyone ready behind her light"),
    (134.54, "proc", "march ahead: everyone steps out together"),
    (136.9, "proc", "the procession from above"),
    (139.2, "church", "the church waiting for them"),
    (141.5, "proc", "among the walkers"),
    (144.4, "proc", "fulfilled: hearts light in every person"),
    (146.7, "proc", "the hearts in the nine colours"),
    (148.6, "proc", "the kings walk in the aisle"),
    (150.4, "stage", "the choir: all kings worship You"),
    (152.0, "proc", "the kings before Zion"),
    (154.2, "proc", "the kings kneel"),
    (155.34, "proc", "the crowns rise as sparks"),
    (156.0, "proc", "the held breath: everyone still"),
    (159.0, "proc", "sparks gather into her light"),
    (160.6, "stage", "the choir draws breath"),
    (161.7, "proc", "her light grows"),
    (162.3, "stage", "the last half bar"),
    (162.86, "stage", "SLAM 2: brass and timpani blaze"),
    (165.16, "zion", "the shockwave across the land"),
    (167.5, "stage", "the choir"),
    (169.2, "zion", "the shockwave reaches the sea"),
    (171.48, "zion", "standing firm: the whole mountain full of people"),
    (173.8, "stage", "the orchestra"),
    (176.1, "zion", "the nations, closer"),
    (178.4, "church", "the church over the crowds"),
    (180.7, "zion", "sacrifice: the mountain blazing"),
    (183.0, "stage", "the brass rising"),
    (185.92, "stage", "wondrous love: brass and timpani"),
    (188.27, "coda", "thanks to Mother: hearts rise"),
    (190.6, "stage", "the choir"),
    (192.9, "coda", "hearts rising over Zion"),
    (195.2, "church", "the church in the gathering glow"),
    (197.2, "coda", "the last build: light gathers at the horizon"),
    (198.5, "coda", "the horizon brightens"),
    (199.62, "stage", "the coda hit: the choir"),
    (200.7, "coda", "the last moment before the sun"),
    (201.73, "coda", "SLAM 3: the sun rises over Zion"),
    (203.9, "stage", "the choir and orchestra in the sunrise"),
    (205.98, "coda", "the orchestra on clouds of light"),
    (208.1, "coda", "the clouds round the sun"),
    (210.3, "stage", "the choir"),
    (211.6, "coda", "the third climb: the summit, everyone"),
    (213.8, "church", "the church in the sunrise"),
    (215.9, "coda", "the summit crowd, arms raised"),
    (218.1, "stage", "sacrifice: the brass"),
    (220.2, "coda", "the summit and the sun"),
    (222.0, "church", "the church blazing"),
    (224.03, "coda", "devotion: the world finale, the Earth"),
    (226.3, "coda", "light from every land flows to Zion"),
    (228.6, "coda", "the glory line over the Earth"),
    (231.0, "coda", "hearts across the continents"),
    (233.3, "coda", "the Earth's edge brightens"),
    (235.6, "coda", "the peak: sunrise over the Earth's edge"),
    (238.8, "stage", "home: Oh, the Church of God"),
    (240.19, "stage", "the step down, hymn-like"),
    (242.5, "church", "the church at peace"),
    (244.8, "stage", "the choir"),
    (247.5, "stage", "the held breath: sparks gather"),
    (249.43, "stage", "the final rise"),
    (251.7, "church", "the church on the last swell"),
    (254.07, "coda", "the last chord: the whole Earth, the end card"),
]
EDIT_T = [e[0] for e in EDIT] + [TOTAL + 1.0]
BLOCKS = [dict(t0=e[0], t1=EDIT_T[i + 1], owner=e[1], note=e[2]) for i, e in enumerate(EDIT)]


def blocks_of(owner):
    """The blocks a thread owns: [(t0, t1, note)]."""
    return [(b["t0"], b["t1"], b["note"]) for b in BLOCKS if b["owner"] == owner]


# The music's intensity, 0..1 (sections from the measured map; loudness on top)
LEVELS = [(0.0, 0.10), (11.9, 0.20), (21.5, 0.30), (40.5, 0.35), (52.1, 0.55), (75.2, 0.62), (82.08, 0.85),
          (117.0, 0.15), (121.32, 0.40), (130.0, 0.55), (156.0, 0.45), (162.86, 0.88), (197.2, 0.70),
          (201.73, 1.0), (238.8, 0.55), (247.5, 0.15), (249.43, 0.75), (254.07, 0.20), (260.0, 0.05)]


def intensity(t):
    ts, vs = zip(*LEVELS)
    i = int(np.searchsorted(ts, t, side="right")) - 1
    return float(min(1.0, 0.75 * vs[max(i, 0)] + 0.35 * loud(t)))


SLAMS = [SLAM1, SLAM2, SLAM3]
KICKS = sorted(set(SLAMS + [HIT[k] for k in ("first", "call1", "call2", "father", "glory", "step1", "step2",
                                             "step3", "nations", "stream", "firm1", "sacrifice", "thanks",
                                             "mother", "trust", "march", "fulfilled", "kings1", "kings2",
                                             "firm2", "love", "thanks2", "coda", "devotion", "peak", "final")]
                   + [LAST_CHORD]))


def cam_speed(t):
    """How fast the camera travels at t (relative): slow drifts in the quiet, fast in builds and choruses,
    a surge on every hit."""
    return 0.25 + 1.6 * intensity(t) ** 1.6 + 1.2 * hit_pulse(t, KICKS, rise=0.02, fall=0.45)


def music_pace(t0, t1, n=240):
    """A pace for a camera move from t0 to t1: progress 0..1, fast where the music is strong."""
    ts = np.linspace(t0, t1, n)
    v = np.array([cam_speed(x) for x in ts])
    c = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(ts))])
    c /= max(c[-1], 1e-9)
    return lambda t: float(np.interp(t, ts, c))


def cam_shake(t):
    """A hard shake on the slams and a small kick on the big hits, a breath of it on the beat in choruses."""
    return (0.9 * hit_pulse(t, SLAMS, rise=0.01, fall=0.35) + 0.35 * hit_pulse(t, KICKS, rise=0.01, fall=0.25)
            + 0.10 * intensity(t) * beat_pulse(t))


def fov_punch(t):
    """The lens punches in on the slams and hits, and breathes with the beat when the music is strong."""
    return (1.0 - 0.10 * hit_pulse(t, SLAMS, rise=0.02, fall=0.6) - 0.04 * hit_pulse(t, KICKS, rise=0.02, fall=0.4)
            - 0.012 * intensity(t) * beat_pulse(t))


__all__ = [k for k in list(globals()) if not k.startswith("__")]
import songs.s11_church as S_CHURCH  # noqa: E402
import songs.s11_stage as S_STAGE  # noqa: E402
import songs.s11_zion as S_ZION  # noqa: E402
import songs.s11_procession as S_PROC  # noqa: E402
import songs.s11_coda as S_CODA  # noqa: E402
import songs.s11_light as S_LIGHT  # noqa: E402

THREADS = [S_CHURCH, S_STAGE, S_ZION, S_PROC, S_CODA]
Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C
CORE_SHOTS = [
    # Father's pulse rolls out over the whole Earth: a fast pull-back from close over Korea to the whole globe
    dict(name="earth_father", kind="globe", t0=41.6, t1=45.6, fov=46.0, aperture=0.0,
         keys=[(41.6, _gcam(95.0, 10.0, -14.0), G + _v(0, 8, 0)), (45.6, _gcam(170.0, 4.0, 6.0), G)]),
    # closer, from below, the echoes of the pulse crossing the oceans
    dict(name="earth_father", kind="globe", t0=45.6, t1=49.8, fov=44.0, aperture=0.0,
         keys=[(45.6, _gcam(120.0, -34.0, 30.0), G + _v(0, 6, 0)), (49.8, _gcam(112.0, -20.0, 10.0), G + _v(0, 8, 0))]),
    # the Earth turns toward Zion: a swing over the top
    dict(name="earth_father", kind="globe", t0=49.8, t1=53.78, fov=46.0, aperture=0.0,
         keys=[(49.8, _gcam(130.0, 40.0, -30.0), G + _v(0, 4, 0)), (53.78, _gcam(100.0, 24.0, 4.0), G + _v(0, 10, 0))]),
    # all nations: rivers of light from every continent, the camera racing round
    dict(name="earth_rivers", kind="globe", t0=70.54, t1=72.84, fov=46.0, aperture=0.0,
         keys=[(70.54, _gcam(140.0, 10.0, 40.0), G + _v(0, 6, 0)), (72.84, _gcam(118.0, 14.0, -10.0), G + _v(0, 8, 0))]),
    # the rivers closer, skimming over the land toward Korea
    dict(name="earth_rivers", kind="globe", t0=72.84, t1=74.56, fov=40.0, aperture=0.0,
         keys=[(72.84, _gcam(92.0, 22.0, -20.0), G + _v(0, 14, 0)), (74.56, _gcam(84.0, 18.0, 6.0), G + _v(0, 16, 0))]),
    # the drop: the Earth's rim glows, the camera rising over it
    dict(name="earth_rivers", kind="globe", t0=75.2, t1=77.46, fov=46.0, aperture=0.0,
         keys=[(75.2, _gcam(132.0, 8.0), G + _v(0, 8, 0)), (77.46, _gcam(126.0, 34.0), G + _v(0, 18, 0))]),
]


def _gather_shots():
    """One shot per edit block: the owner's shot with exactly the block's times; until a thread has one, its
    older shot that covers the block, clipped to it; else a held wide view (so the film always renders)."""
    pool = {"core": CORE_SHOTS, "church": S_CHURCH.SHOTS, "stage": S_STAGE.SHOTS, "zion": S_ZION.SHOTS,
            "proc": S_PROC.SHOTS, "coda": S_CODA.SHOTS}
    shots, missing = [], []
    for b in BLOCKS:
        own = pool[b["owner"]]
        hit = [s for s in own if abs(s["t0"] - b["t0"]) < 1e-3 and abs(s["t1"] - b["t1"]) < 1e-3]
        if hit:
            s = dict(hit[0])
        else:
            cover = [s for s in own if s["t0"] - 1e-3 <= b["t0"] < s["t1"]] or [s for s in own if s["t0"] < b["t1"]]
            missing.append(b)
            if cover:
                s = dict(cover[-1], t0=b["t0"], t1=b["t1"], clipped=True)
            else:
                s = dict(name="hold_" + b["owner"], kind="local", t0=b["t0"], t1=b["t1"], fov=50.0, aperture=0.0,
                         keys=[(b["t0"], _v(0.0, 40.0, 120.0), ZC + _v(0.0, 50.0, 0.0)),
                               (b["t1"], _v(0.0, 42.0, 110.0), ZC + _v(0.0, 50.0, 0.0))], clipped=True)
        s["block"] = b
        shots.append(s)
    if missing and os.environ.get("S11_EDIT_REPORT"):
        print(f"edit: {len(missing)} of {len(BLOCKS)} blocks have no exact shot yet (owners: "
              + ", ".join(sorted({m['owner'] for m in missing})) + ")", flush=True)
    return shots


SHOTS[:] = _gather_shots()
_SHOT_T0[:] = [s["t0"] for s in SHOTS]
CUTS = [s["t0"] for s in SHOTS[1:]]


class MusicRig(Rig):
    """The rig with the music in it: the lens punches in on the slams and hits and breathes with the beat."""

    def state(self, t, aspect=16.0 / 9.0):
        st = super().state(t, aspect)
        st.fov = float(st.fov * fov_punch(t))
        return st


def _rig():
    moves = []
    for s in SHOTS:
        foc = s.get("focus", "target")
        keys = s["keys"]
        if s.get("clipped"):
            mv = fly(keys, blend=0.0, ease="linear", fov=s["fov"], aperture=s["aperture"], focus=foc)
            mv.t0, mv.t1 = s["t0"], s["t1"]          # an older shot cut down to its block: as it was, no pace
        else:
            pace = s.get("pace", "music")
            kw = dict(pace=music_pace(s["t0"], s["t1"])) if pace == "music" else (
                dict(pace=pace) if pace not in (None, "linear") else dict(ease="linear"))
            mv = fly(keys, blend=float(s.get("blend", 0.0)), fov=s["fov"], aperture=s["aperture"], focus=foc, **kw)
        moves.append(mv)
    return MusicRig(moves, blend=0.0, fov=50.0, aperture=0.0, handheld=0.12, min_height=0.4, shake=cam_shake)


CAMERA = _rig()
WORLD = S_LIGHT.world()
WORLD["shafts"] = [sh for m in THREADS for sh in getattr(m, "SHAFTS", [])][:4]

# =========================================================================================================
# The phrases on screen: Anthony's list, timed to where each is sung on this recording.
# Strong and powerful ones are huge and blaze in gold (rays burn them out of the light); the gentle ones are
# written by light. (t_in, t_read0, t_read1, t_out)
# =========================================================================================================
PHRASE_LIST = [
    # text lines, times, strong, arrive, leave
    (["The glory of Jerusalem", "Mother shines!"], (53.9, 55.4, 60.0, 61.2), False, "gather", "rise"),
    (["All nations and all peoples"], (70.6, 71.4, 74.0, 74.5), False, "weave", "wind"),
    (["to the great Church of God!"], (74.56, 75.7, 79.0, 79.9), False, "pen", "rise"),
    (["Joy of salvation!"], (80.3, 82.08, 85.6, 86.6), True, "rays", "bokeh"),
    (["For Your sacrifice"], (99.4, 100.3, 103.0, 103.6), True, "rays", "rise"),
    (["For Your devotion"], (103.6, 105.14, 108.4, 109.4), True, "rays", "rise"),
    (["This hope was engraved", "deep in all our hearts"], (133.6, 135.6, 140.6, 141.6), False, "reveal", "rise"),
    (["All kings worship You"], (150.4, 151.5, 154.0, 154.8), False, "pen", "wind"),
    (["to the great Church of God!"], (154.9, 156.0, 159.4, 160.3), False, "pen", "rise"),
    (["Joy of salvation!"], (161.0, 162.86, 166.6, 167.6), True, "rays", "bokeh"),
    (["Your sacrifice"], (179.2, 180.2, 182.8, 183.5), True, "rays", "rise"),
    (["Your wondrous love"], (183.6, 185.4, 188.2, 188.9), True, "rays", "rise"),
    (["Joy of salvation!"], (199.9, 201.73, 205.4, 206.2), True, "rays", "bokeh"),
    (["Joy of salvation!"], (209.4, 210.4, 213.6, 214.4), True, "rays", "rise"),
    (["Your sacrifice"], (218.4, 219.3, 222.4, 223.1), True, "rays", "rise"),
    (["For Your devotion"], (223.2, 223.9, 226.5, 226.95), True, "rays", "rise"),
    (["We give eternal glory, praise, and thanks", "to Our Father Ahnsahnghong and Mother!"],
     (227.0, 228.8, 234.8, 236.0), True, "rays", "rise"),
    (["Oh, the Church of God"], (239.0, 240.2, 244.6, 245.8), False, "pen", "rise"),
]


def _wordcam(t):
    return CAMERA


def _width(ts, depth, frac):
    """The words' width so they fill `frac` of the frame at the narrowest lens they are seen through."""
    fov = min(CAMERA.state(float(t)).fov for t in ts)
    cam = CAMERA.state(float(ts[0]))
    return float(2.0 * depth * np.tan(np.radians(fov) * 0.5) * cam.aspect * frac)


def _phrase_specs():
    specs = []
    for i, (lines, (ti, r0, r1, to), strong, arr, lv) in enumerate(PHRASE_LIST):
        depth = 30.0
        long = max(len(s) for s in lines)
        if strong:
            frac = 0.66 if long > 30 else min(0.66, 0.040 * long + 0.06)
            ride = (0.5, 0.62 if len(lines) == 1 else 0.60, depth)
        else:
            frac = min(0.56, 0.026 * long + 0.05)
            ride = (0.5, 0.63 if len(lines) == 1 else 0.60, depth)
        spec = dict(label="", lines=lines, ride=ride, face="screen", width=_width(np.linspace(ti, to, 12), depth, frac),
                    t_in=ti, t_read0=r0, t_read1=r1, t_out=to, arrive=arr, leave=lv, name=f"phrase{i:02d}",
                    color=GOLD if strong else "#ffe6c0", glow=GOLD if strong else "#ffd59a",
                    tint=0.75 if strong else 0.35, bright=1.15 if strong else 1.0,
                    halo=1.3 if strong else 1.0, n=90000 if strong else 60000, reflect=False)
        if strong:
            spec["font"] = "title"

        if arr == "reveal":
            spec["edge"] = "right"
        if arr == "pen":
            spec["nib"] = True
        specs.append(spec)
    return specs
WORDS = PW.Words(_phrase_specs(), camera=CAMERA)


# =========================================================================================================
# Putting it together
# =========================================================================================================
def _setup(scene):
    for m in THREADS:
        m.add(scene)
    scene.add("earth", GLOBE, reflect=False)
    scene.add("earth fx", GlobeFX(), reflect=False)
    WORDS.add_to(scene)
    WORDS.check(CAMERA, need_all=False)


def _bursts():
    """Light that follows the music: a soft flash hides each cut (bright on the slams), every big hit flashes
    in one of the nine colours, and in the choruses and the coda each bar's downbeat glows faintly."""
    out = []
    for c in CUTS:
        strong = any(abs(c - s) < 0.05 for s in SLAMS)
        out.append(dict(t=c, strength=0.75 if strong else 0.16 + 0.12 * intensity(c), rise=0.04,
                        fall=0.45 if strong else 0.22, color="#fff3dc"))
    for i, h in enumerate(KICKS):
        if any(abs(h - s) < 0.05 for s in SLAMS):
            continue
        out.append(dict(t=h + 0.01, strength=0.22 + 0.2 * intensity(h), rise=0.03, fall=0.5, color=COL9[i % 9]))
    for a, b in ((82.08, 117.0), (162.86, 201.73), (201.73, 238.8)):
        bar = 2.30 if a < 201 else 2.16
        k = 0
        x = a + bar
        while x < b - 0.3:
            out.append(dict(t=x, strength=0.10, rise=0.03, fall=0.3, color=COL9[(k * 4) % 9]))
            x += bar
            k += 1
    out.append(dict(t=HIT["father"], strength=0.8, rise=0.08, fall=0.6, color="#ffeccc",
                    at=tuple(CHURCH + _v(0.0, 20.0, 0.0))))
    return sorted(out, key=lambda d: d["t"])


P3D = dict(camera=CAMERA, world=WORDS.world(WORLD), setup=_setup, bursts=_bursts(), motion_blur=0.35)


def _sig_windows():
    w = []
    for s in SHOTS:
        t0, t1 = s["t0"], s["t1"]
        a = max(t0, 11.6)
        if t1 <= a or t0 >= 254.07:
            continue
        pal = "night" if (s["kind"] in ("globe", "stage") or t0 < 162.86 or s["name"] == "hearts_rise") else "day"
        if w and w[-1][3] == pal and abs(w[-1][1] - a) < 1e-6:
            w[-1] = (w[-1][0], t1, w[-1][2], pal)
        else:
            w.append((a, t1, "tl", pal))
    return w                     # from the last chord the end card carries its own lockup


TITLES = dict(
    opening=dict(t_end=11.9, y=0.42, palette="night", dissolve=1.4, build=1.2),
    signature=dict(windows=_sig_windows(), fade=0.12),
    end_card=dict(t_in=LAST_CHORD, fade=1.6, scale=0.94, veil=0.6, backdrop=False),
)
