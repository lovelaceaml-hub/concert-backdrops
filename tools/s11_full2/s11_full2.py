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
    # B. the whole Earth: Father's pulse rolls out over it
    dict(name="earth_father", kind="globe", t0=41.6, t1=53.78, fov=46.0, aperture=0.0,
         keys=[(41.6, _gcam(175.0, 6.0), G), (53.78, _gcam(150.0, 14.0, 10.0), G + _v(0, 4, 0))]),
    # D. the Earth again: rivers of people from every continent; the camera rises as the horizon glows
    dict(name="earth_rivers", kind="globe", t0=70.54, t1=77.46, fov=46.0, aperture=0.0,
         keys=[(70.54, _gcam(140.0, 10.0), G + _v(0, 6, 0)), (75.2, _gcam(132.0, 12.0), G + _v(0, 8, 0)),
                        (77.46, _gcam(128.0, 30.0), G + _v(0, 16, 0))]),
]


def _gather_shots():
    shots = sorted(CORE_SHOTS + [s for m in THREADS for s in m.SHOTS], key=lambda s: s["t0"])
    for a, b in zip(shots, shots[1:]):
        if abs(a["t1"] - b["t0"]) > 1e-6:
            raise ValueError(f"shots {a['name']} and {b['name']} do not meet: {a['t1']} vs {b['t0']}")
    if shots[0]["t0"] != 0.0 or shots[-1]["t1"] < TOTAL:
        raise ValueError("the shots must cover 0 to TOTAL")
    return shots


SHOTS[:] = _gather_shots()
_SHOT_T0[:] = [s["t0"] for s in SHOTS]
CUTS = [s["t0"] for s in SHOTS[1:]]


def _rig():
    moves = []
    for s in SHOTS:
        foc = s.get("focus", "target")
        moves.append(fly(s["keys"], blend=0.0, ease="linear", fov=s["fov"], aperture=s["aperture"], focus=foc))
    return Rig(moves, blend=0.0, fov=50.0, aperture=0.0, handheld=0.12, min_height=0.4)


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
    out = []
    for c in CUTS:
        strong = c in (SLAM1, SLAM2, SLAM3)
        out.append(dict(t=c, strength=0.7 if strong else 0.45, rise=0.06, fall=0.4 if strong else 0.3,
                        color="#fff3dc"))
    out.append(dict(t=HIT["father"], strength=0.8, rise=0.08, fall=0.6, color="#ffeccc",
                    at=tuple(CHURCH + _v(0.0, 20.0, 0.0))))
    out.append(dict(t=HIT["glory"] + 0.02, strength=0.4, rise=0.05, fall=0.6, color="#ffe6b8"))
    return out




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
