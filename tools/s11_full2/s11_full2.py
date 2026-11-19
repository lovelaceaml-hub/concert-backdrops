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


# Round 7 (Anthony: "The earth land can be a different color than gold so it's easier to see the lights"; he chose
# deep emerald land and navy oceans): the land is painted deep emerald (it adds no light of its own), the oceans
# navy, so the cities' gold and white lights (GlobeFX) and the rivers of people stand out on it, by day and night.
EARTH_LOOK = dict(ocean_c="#132f6c", ocean_e="#081843", land="#0b6e46", land2="#1f9a66", land_base="#0a5a3a",
                  rim="#8fd6ff", cloud="#d6e6ff", paint_land=True, rim_k=0.3, cloud_k=0.16, glow_k=0.0, land_k=1.0)
LAND_NIGHT = np.array([0.004, 0.030, 0.020])       # the emerald land on the night side: just a dim green


GLOBE = Globe(pos=tuple(GLOBE_C), radius=GLOBE_R, face="camera", camera=None, look=EARTH_LOOK, spin=1.2,
              front=ZION_LL[1] - 1.2 * 60.0 - 18.0, tilt=24.0, amount=_globe_amount,
              hearts=dict(t0=226.0, t1=236.5, n=64, size=0.11, start=ZION_LL, colors="nine", pulse=1.0),
              arcs=True, n=70000, bright=1.1)


# Anthony (page request, 2026-11-19): the Earth in verse 1 opens on its night side (deep ocean, city lights) and
# lights up as the music builds. Round 6 (his words): "the earth should be dark, and then the sun should rise
# from the east, which is where Korea is. The point is, the light is supposed to come from Jerusalem, which is
# heavenly Jerusalem in Korea. As the lights begin to light up the rest of the world, the world will turn to
# daytime." So the day is a circle of dawn centred on Korea (ZION_LL) that spreads outward over the sphere with
# a glowing golden edge: Korea ignites first (0:41.6, on Father's pulse rolling out), the dawn spreads through
# the first Earth shots, again through the second, and the whole world is in day by 1:17.46; the world finale
# stays lit. earth_day(t) is the progress 0..1; the dawn's angular radius is DAWN_MAX * progress.
DAY_KEYS = [(41.6, 0.0), (42.6, 0.02), (53.78, 0.30), (70.54, 0.30), (76.9, 1.0)]
DAWN_MAX = 200.0                                     # degrees: past 180 + the edge's width the world is all day
DAWN_SOFT = 11.0                                     # degrees: the width of the dawn's edge


def earth_day(t):
    return float(np.interp(t, [k[0] for k in DAY_KEYS], [k[1] for k in DAY_KEYS]))


def dawn_angle(t):
    """The dawn circle's angular radius round Korea at t (radians)."""
    return np.radians(DAWN_MAX * earth_day(t))


def _dawn_edge(t, c, R, zw, cam):
    """The glowing edge of the dawn: a soft golden band and glitter on the circle round Korea, only on the face
    toward the camera; it breathes on the beat. And Korea itself: a sun igniting on it."""
    out = []
    ang = dawn_angle(t)
    eye = np.asarray(cam.pos if hasattr(cam, "pos") else cam["pos"], np.float64)
    gone = 1.0 - _sc(np.radians(170.0), np.radians(DAWN_MAX), ang)
    pul = 1.0 + 0.45 * beat_pulse(t)
    small = 0.2 + 0.8 * _sc(np.radians(10.0), np.radians(70.0), ang)   # round 7: a small circle stacks its glows
    if 0.02 < ang and gone > 0.0:
        n = int(np.clip(1600 * np.sin(min(ang, np.pi / 2)) + 60, 60, 1800))
        v = _sphere_ring(zw, ang, n)
        p = c + R * 1.012 * v
        f = ((eye[None, :] - p) * v).sum(1) > 0.0
        # round 7 (review f21): seen edge-on at the Earth's limb the glows stack into a white band: fade them there
        vv = eye[None, :] - p
        face = np.clip((vv * v).sum(1) / np.maximum(np.linalg.norm(vv, axis=1), 1e-6), 0.0, 1.0)
        fk = (0.1 + 0.9 * _ss(0.05, 0.5, face)).astype(np.float32)
        if f.any():
            out.append(dict(pos=p[f], size=R * (0.06 + 0.04 * small), color=lin("#ffb060"), alpha=0.022 * gone * pul * small * fk[f], kind="soft",
                            emit=1.8, dof=0.0, fog=0.0, reflect=False))
            out.append(dict(pos=p[f], size=R * 0.012, color=lin("#ffd49a"), alpha=0.08 * gone * pul * small * fk[f], kind="spark",
                            emit=2.6, twinkle=0.7, dof=0.0, fog=0.0, reflect=False))
    zp = c + R * 1.02 * zw
    if ((eye - zp) @ zw) > 0.0:
        # the sun rising on Korea: it ignites as the camera arrives on the Earth, then glows on as the source
        # round 7 (task: the glow at 0:45 hid the first lights): a small warm sun, a short ignition, no big halo
        k = (1.0 * hit_pulse(t, [41.6], rise=0.05, fall=0.9) + 0.45 * gone + 0.5 * hit_pulse(t, [70.54], fall=1.0)) * pul
        out.append(dict(pos=zp[None, :], size=R * 0.13, color=lin("#ffc680"), alpha=0.05 * k, kind="soft", emit=1.8,
                        dof=0.0, fog=0.0, reflect=False))
        out.append(dict(pos=zp[None, :], size=R * 0.035, color=lin("#fff0d8"), alpha=0.22 * k, kind="soft", emit=2.4,
                        dof=0.0, fog=0.0, reflect=False))
    return out


def _night_side(sample):
    def wrapped(t, cam=None):
        out = sample(t, cam)
        p = earth_day(t)
        if out is None or p >= 0.999:
            return out
        if cam is None:
            cam = CAMERA.state(t)
        c, M, R = GLOBE._view(t, cam)
        zw = (M @ GLOBE.turn(t)) @ _earth(*ZION_LL)      # Korea's direction from the Earth's centre (world)
        zw = zw / np.linalg.norm(zw)
        ang = dawn_angle(t)
        soft = np.radians(DAWN_SOFT)
        full = float(_sc(np.radians(170.0), np.radians(DAWN_MAX), ang))
        face = float(np.clip(ang / np.radians(150.0), 0.0, 1.0))      # how much of the world is in day
        for b in out:
            pos = np.asarray(b.get("pos"), np.float64)
            if pos.ndim != 2 or len(pos) == 0 or b.get("kind") not in ("disc", "soft", "spark"):
                continue
            rel = pos - c[None, :]
            rr = np.linalg.norm(rel, axis=1) / R
            on = (rr > 0.97) & (rr < 1.03)
            if not on.any():
                continue
            if b["kind"] == "soft" and on.mean() < 0.9:      # the air's halo, laid flat over the face: dim at night
                al = b["alpha"]
                al = np.full(len(pos), float(al)) if not np.ndim(al) else np.asarray(al, np.float64)
                b["alpha"] = (al * (0.08 + 0.92 * face)).astype(np.float32)
                continue
            n = rel / np.maximum(np.linalg.norm(rel, axis=1, keepdims=True), 1e-9)
            da = np.arccos(np.clip(n @ zw, -1.0, 1.0))     # angle from Korea
            d = np.clip((ang - da) / soft + 0.5, 0.0, 1.0)
            d = d * d * (3 - 2 * d)
            d = d * (1 - full) + full
            d = np.where(on, d, 1.0)
            edge = np.exp(-((da - ang) / soft) ** 2) * (1.0 - full) * (ang > 0.01)
            edge = edge * (0.25 + 0.75 * _sc(np.radians(12.0), np.radians(60.0), ang))   # round 7: a young dawn is no gold disc
            if b["kind"] == "spark":                      # city lights: brighter on the night side
                m = 1.0 + 0.6 * (1.0 - d)
                b["alpha"] = np.asarray(b["alpha"], np.float64) * m if np.ndim(b["alpha"]) else b["alpha"] * m
                continue
            col = np.asarray(b["color"], np.float64)
            if col.ndim == 1:
                col = np.repeat(col[None, :], len(pos), axis=0)
            if b["kind"] == "disc":                       # the ocean: deep navy at night, gold on the dawn's edge
                night = col * 0.05 + np.array([0.001, 0.003, 0.012])[None, :]
                if abs(float(np.max(b["size"])) - R * GLOBE.cell * 1.8) < 1e-6 * R:   # (round 7) the emerald land
                    night = col * 0.04 + LAND_NIGHT[None, :]
                dawn = np.array([0.95, 0.62, 0.30])[None, :]
                cc = col * d[:, None] + night * (1 - d[:, None])
                b["color"] = np.clip(cc + (dawn - cc) * (0.22 * edge)[:, None], 0, 1)
            else:                                         # the land glow, its warm halo and the clouds dim at night
                al = b["alpha"]
                al = np.full(len(pos), float(al)) if not np.ndim(al) else np.asarray(al, np.float64)
                # round 7 (task: Korea's dawn at 0:45 glowed as one big halo over the first city lights): while the
                # dawn is young its lit land and clouds glow low, so the lights read; full glow once the world is lit
                young = 0.3 + 0.7 * _sc(0.32, 0.95, p)
                b["alpha"] = (al * (0.05 + 0.95 * d * young) * (1.0 + 0.15 * edge)).astype(np.float32)
        out = list(out) + _dawn_edge(t, c, R, zw, cam)
        return out
    return wrapped


def _earth_reading(t):
    """Round 7 (review f21: phrases sat light on light over the Earth): 1 while a phrase reads over an Earth view."""
    v = 0.0
    try:
        for _lines, (a, b, c, d), *_rest in PHRASE_LIST:      # (defined further down this file)
            if a - 0.5 <= t <= d + 0.5:
                v = max(v, _sc(a - 0.5, b, t) * (1.0 - _sc(c, d, t)))
    except Exception:
        return 0.0
    return v


def _veil(t, out, cam, c, R, k=0.55):
    """Darken the upper part of the Earth (where the words sit) while a phrase reads: painted colours dim, lights
    and glows lose alpha; the lower part and the rim stay as they are."""
    r = _earth_reading(t)
    if r <= 0.0 or not out:
        return out
    up = np.asarray(cam.basis()[1] if hasattr(cam, "basis") else (0.0, 1.0, 0.0), np.float64)
    for b in out:
        pos = np.asarray(b.get("pos"), np.float64)
        if pos.ndim != 2 or len(pos) == 0 or b.get("kind") not in ("disc", "soft", "spark", "line"):
            continue
        s = ((pos - c[None, :]) @ up) / R
        m = 1.0 - k * r * _ss(-0.45, 0.25, s)
        if b["kind"] == "disc":
            col = np.asarray(b["color"], np.float64)
            col = np.repeat(col[None, :], len(pos), axis=0) if col.ndim == 1 else col
            b["color"] = col * m[:, None]
        else:
            al = b["alpha"]
            al = np.full(len(pos), float(al)) if not np.ndim(al) else np.asarray(al, np.float64)
            b["alpha"] = (al * m).astype(np.float32)
    return out


def _word_veil(sample):
    def wrapped(t, cam=None):
        out = sample(t, cam)
        if out is None:
            return out
        cam = cam if cam is not None else CAMERA.state(t)
        c, _M, R = GLOBE._view(t, cam)
        return _veil(t, list(out), cam, c, R)
    return wrapped


GLOBE.sample = _word_veil(_night_side(GLOBE.sample))


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
    # round 7: more and more people going to Zion: more rivers join as the film goes on (every continent)
    MORE = [(40.7, -74.0), (19.4, -99.1), (-23.5, -46.6), (51.5, -0.1), (6.5, 3.4), (28.6, 77.2),
            (-34.6, -58.4), (-1.3, 36.8), (35.7, 139.7), (-33.9, 151.2), (30.0, 31.2), (14.6, 121.0)]
    RIVER_N = 700
    NINE = [(40.7, -74.0, 0.42), (-23.5, -46.6, -0.38), (51.5, -0.1, 0.30), (6.5, 3.4, -0.34), (-1.3, 36.8, 0.36),
            (28.6, 77.2, -0.30), (-33.9, 151.2, 0.40), (55.7, 37.6, -0.36), (19.4, -99.1, 0.34)]   # (lat, lon, bend)
    # (round 7) the cities: gold and white lights on the emerald land, thickest where people live
    METROS = [(40, -75, 1.0, 6), (34, -118, 0.7, 4), (42, -88, 0.6, 5), (32, -90, 0.4, 7), (46, -122, 0.3, 4),
              (19, -99, 0.8, 5), (5, -74, 0.4, 5), (-12, -77, 0.3, 4), (-23, -46, 0.9, 6), (-34, -58, 0.5, 4),
              (51, 0, 0.9, 6), (49, 8, 0.9, 7), (52, 20, 0.5, 6), (42, 13, 0.6, 5), (40, -4, 0.5, 5), (55, 37, 0.5, 6),
              (30, 31, 0.6, 4), (7, 4, 0.8, 5), (-1, 37, 0.4, 5), (-26, 28, 0.5, 4), (25, 46, 0.3, 5),
              (35, 51, 0.4, 5), (25, 68, 0.4, 4), (28, 77, 1.0, 7), (19, 73, 0.8, 5), (13, 80, 0.6, 5),
              (23, 90, 0.8, 4), (31, 121, 1.0, 6), (39, 116, 0.9, 6), (23, 113, 0.9, 5), (30, 104, 0.6, 5),
              (37.5, 127, 1.0, 3), (35, 137, 0.9, 5), (14, 121, 0.6, 4), (-6, 107, 0.8, 5), (13, 100, 0.5, 4),
              (10, 106, 0.5, 4), (-34, 151, 0.4, 3), (-38, 145, 0.3, 3), (1, 104, 0.4, 2)]

    def __init__(self):
        r = np.random.default_rng(23)
        self.src = list(self.STARTS) + list(self.MORE)
        self.s = r.random((len(self.src), self.RIVER_N, 6))
        # review f27 (approved): the 24 straight rivers met in a white star as rainbow spokes. Now nine slow
        # curved arcs, one per colour, from every continent toward Korea (more people in each)
        self.nine = list(self.NINE)
        self.s9 = r.random((9, 2 * self.RIVER_N, 6))
        self.city = None

    # how full the rivers of people are (1: every river, every lane; past 1 the finale's rivers widen)
    RIVER_KEYS = [(41.6, 0.10), (47.5, 0.17), (53.78, 0.26), (70.3, 0.34), (70.54, 0.58), (74.3, 0.72),
                  (74.56, 0.97), (77.46, 1.05), (224.03, 1.1), (236.0, 1.3), (238.8, 1.3)]

    @classmethod
    def river_k(cls, t):
        if not (41.6 <= t < 77.46 or 224.03 <= t < 238.8):
            return 0.0
        return float(np.interp(t, [x[0] for x in cls.RIVER_KEYS], [x[1] for x in cls.RIVER_KEYS]))

    def _cities(self):
        """Land points chosen as city lights (Earth frame unit vectors, colours, sizes, seeds), made once."""
        if self.city is None:
            r = np.random.default_rng(29)
            lat, lon = GLOBE.l_lat, GLOBE.l_lon
            w = np.full(len(lat), 0.05)
            for la, lo, k, rad in self.METROS:
                cosd = (np.sin(np.radians(lat)) * np.sin(np.radians(la))
                        + np.cos(np.radians(lat)) * np.cos(np.radians(la)) * np.cos(np.radians(lon - lo)))
                d = np.degrees(np.arccos(np.clip(cosd, -1.0, 1.0)))
                w += k * np.exp(-(d / rad) ** 2)
            w = w * (np.abs(lat) < 66.0)
            pick = r.random(len(lat)) < np.clip(0.3 * w, 0.0, 0.5)
            v = GLOBE.l_v[pick]
            ww = w[pick]
            m = len(v)
            white = r.random(m) < 0.35
            col = np.where(white[:, None], lin("#fff6e6")[None, :], lin("#ffc95e")[None, :])
            self.city = dict(v=v, col=col, size=0.16 + 0.22 * np.clip(ww, 0, 1.2) * r.random(m),
                             seed=r.random(m), big=(ww > 0.65) & (r.random(m) < 0.25))
        return self.city

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
                    v = _sphere_ring(zv, ang, int(160 + 740 * np.sin(ang))) @ T.T     # even spacing: no hard small ring
                    p = c + R * 1.01 * v
                    f = front(p)
                    a = np.exp(-u / 2.2) * (0.38 if t0 == 41.6 else 0.22)
                    out.append(dict(pos=p[f], size=0.45, color=lin("#ffd8a0"), alpha=a, emit=2.4, kind="spark",
                                    dof=0.0, reflect=False))
        # Zion itself: a warm light on Korea
        zp = c + R * 1.01 * (zv @ T.T)
        if ((eye - zp) @ (zp - c)) > 0:
            k = 0.8 + 1.4 * hit_pulse(t, [HIT["stream"]], fall=1.5) + 0.4 * beat_pulse(t)
            out.append(dict(pos=zp[None, :], size=1.8, color=lin("#ffe2a8"), alpha=0.22 * k, kind="soft", emit=1.8,
                            reflect=False))
            out.append(dict(pos=zp[None, :], size=0.6, color=lin(WHITE), alpha=0.8 * min(k, 1.3), kind="spark", emit=4.0,
                            reflect=False))
        # (round 7) the cities: gold and white lights on the emerald land, brighter on the night side
        cy = self._cities()
        cv = cy["v"] @ T.T
        cp = c + R * 1.006 * cv
        cf = front(cp)
        if cf.any():
            zw = _unit(T @ zv)
            da = np.arccos(np.clip(cv[cf] @ zw, -1.0, 1.0))
            nt = 1.0 - np.clip((dawn_angle(t) - da) / np.radians(DAWN_SOFT) + 0.5, 0.0, 1.0)   # 1 on the night side
            a = (0.75 + 0.55 * nt) * (1.0 + 0.2 * beat_pulse(t))
            out.append(dict(pos=cp[cf], size=cy["size"][cf], color=cy["col"][cf], alpha=a, emit=2.4, kind="spark",
                            twinkle=0.35, seed=cy["seed"][cf], dof=0.0, reflect=False))
            bg = cf & cy["big"]
            if bg.any():
                nb = 1.0 - np.clip((dawn_angle(t) - np.arccos(np.clip(cv[bg] @ zw, -1.0, 1.0)))
                                   / np.radians(DAWN_SOFT) + 0.5, 0.0, 1.0)
                out.append(dict(pos=cp[bg], size=1.1, color=lin("#ffcf7a"), alpha=0.07 + 0.08 * nb, kind="soft",
                                emit=1.6, dof=0.0, reflect=False))
        # the rivers of people (round 7: "more and more people going to Zion"): streams of people of light from
        # every continent flowing along the Earth to Zion, from Father's pulse on; a few thin rivers at first,
        # more rivers, more people and wider and brighter in every Earth view, jumping on "all nations" (1:10.54)
        # and on the strongest onset (1:14.56); in the world finale the whole Earth flows to Zion
        k = self.river_k(t)
        if k > 0.0:
            hit = hit_pulse(t, [HIT["nations"], HIT["stream"]], rise=0.03, fall=0.9)
            n_on = 5.0 + 19.0 * float(np.clip((k - 0.08) / 0.62, 0.0, 1.0))
            kk = min(k, 1.0)
            wid = 0.005 + 0.013 * min(k, 1.3)
            br = (0.35 + 0.35 * kk) * (1.0 + 0.6 * hit + 0.2 * beat_pulse(t))
            up = np.asarray(cam.basis()[1], np.float64)
            rd = _earth_reading(t)
            n_on = 3.0 + 6.0 * float(np.clip((k - 0.08) / 0.62, 0.0, 1.0))
            for i, (la, lo, bend) in enumerate(self.nine):
                on_i = float(np.clip(n_on - i, 0.0, 1.0))
                if on_i <= 0.0:
                    continue
                sv = _earth(la, lo)
                s = self.s9[i]
                f = np.mod(s[:, 1] + 0.055 * t * (0.8 + 0.4 * s[:, 2]), 1.0)      # slow: people walking
                om = np.arccos(np.clip(sv @ zv, -1, 1))
                w0 = np.sin((1 - f) * om) / np.sin(om)
                w1 = np.sin(f * om) / np.sin(om)
                v = w0[:, None] * sv[None, :] + w1[:, None] * zv[None, :]
                v = v / np.linalg.norm(v, axis=1, keepdims=True)
                side = np.cross(sv, zv)
                side = side / max(np.linalg.norm(side), 1e-9)
                v = v + (bend * np.sin(np.pi * f))[:, None] * side[None, :]          # a curved arc, not a spoke
                v = v / np.linalg.norm(v, axis=1, keepdims=True)
                v = v + wid * (1.0 - 0.6 * f[:, None]) * (s[:, 3:6] - 0.5)
                v = v / np.linalg.norm(v, axis=1, keepdims=True)
                lift = 1.010 + 0.006 * np.sin(np.pi * f)
                p = c + R * lift[:, None] * (v @ T.T)
                vis = (s[:, 0] < kk * on_i) & front(p)
                if not vis.any():
                    continue
                # they fade in from the edge and out before they meet, so Korea is no white star
                fa = _ss(0.0, 0.10, f[vis]) * (1.0 - _ss(0.62, 0.88, f[vis]))
                sup = ((p[vis] - c[None, :]) @ up) / R                              # kept below the words
                fa = fa * (1.0 - 0.85 * rd * _ss(-0.05, 0.35, sup))
                col = lin(COL9[i % 9]) * 0.88 + lin(WHITE) * 0.12
                out.append(dict(pos=p[vis], size=0.14 + 0.10 * kk + 0.12 * s[vis, 2], color=col,
                                alpha=(0.8 * br * fa).astype(np.float32), emit=2.4, kind="spark", dof=0.0,
                                reflect=False, twinkle=0.5, seed=s[vis, 1]))
                g = np.where(vis)[0][::5]
                if len(g):
                    fg = fa[::5][:len(g)]
                    out.append(dict(pos=p[g], size=1.0 + 0.6 * kk, color=col, alpha=(0.035 * br * fg).astype(np.float32),
                                    emit=1.5, kind="soft", dof=0.0, reflect=False))
        # the build (1:15.2): the Earth's rim glows brighter as if the sun were coming
        if 74.0 <= t < 77.46:
            k = _sc(75.2, 77.4, t)
            rim = _sphere_ring(_unit(np.linalg.inv(T) @ _unit(eye - c)), np.pi / 2 * 0.985, 1600) @ T.T
            p = c + R * 1.03 * rim
            out.append(dict(pos=p, size=0.7, color=lin("#ffd9a0"), alpha=0.16 * k, kind="soft", emit=1.6,
                            reflect=False))
        return _veil(t, out, cam, c, R) or None


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
    (0.0, "church", "title over the waiting city, night and mist, comets far off"),
    (11.9, "church", "one long flight in from the plateau edge down the great avenue, the comets lead"),
    (21.52, "church", "call 1: the choir forms out of shafts of light on the steps"),
    (26.33, "stage", "the orchestra wakes, the comets weave through it"),
    (31.11, "church", "call 2: a long rise up the church of light with the comets"),
    (38.24, "church", "brightest moment; Father's bell-like pulse from the church (40.54), rays fan out"),
    (41.6, "core", "the whole Earth: Father's pulse rolls out"),
    (47.5, "core", "the Earth turns toward Zion, the comets streak down to Korea"),
    (53.78, "zion", "glory: the crown of light ignites, rays fan from it"),
    (58.4, "church", "the church under the crown"),
    (61.3, "zion", "as Father prophesied: flight over the city"),
    (64.2, "zion", "fulfilled: the terraces fill with gold step by step (64.2, 65.94, 69.4)"),
    (69.4, "zion", "the city full of gold"),
    (70.54, "core", "all nations: rivers of light on the Earth"),
    (74.56, "church", "streaming: the church of light shines out"),
    (75.2, "core", "the drop: the Earth's rim glows"),
    (77.46, "stage", "the choir breathes in, light gathering, the comets spiral in"),
    (80.94, "church", "the church gathering light"),
    (81.51, "stage", "the last half bar into the slam"),
    (82.08, "stage", "SLAM 1: the full choir and orchestra blaze, rays and a huge burst"),
    (86.7, "zion", "waves of praise roll over the land"),
    (90.72, "zion", "standing firm: the first climb, the nations on Zion"),
    (97.7, "dance", "the ring of dancers: their ribbons braid into one spiral climbing to the sky"),
    (99.4, "zion", "sacrifice: light pours over the people"),
    (103.6, "zion", "devotion: the golden waterfall"),
    (105.14, "stage", "the brass and timpani blaze"),
    (108.4, "church", "the church glowing"),
    (109.8, "zion", "thanks to Father: the column of light rises, lanterns rise all round"),
    (117.0, "dance", "the breath: one dancer of light, slow, her ribbon a slow spiral, light falling like snow"),
    (121.32, "dance", "verse 2: the dancer quickens, her ribbon flicks up on the strings' pulses"),
    (125.92, "proc", "Mother: her light comes down out of the sky, rays fan from it"),
    (130.29, "proc", "let's trust Father: everyone gathered behind her light"),
    (134.54, "proc", "march ahead: everyone steps out together"),
    (139.2, "church", "the church waiting for them"),
    (141.5, "proc", "among the walkers"),
    (144.4, "proc", "fulfilled: hearts light in every person"),
    (148.6, "proc", "the kings walk in the aisle"),
    (154.2, "proc", "the kings kneel; the crowns rise as sparks"),
    (156.0, "proc", "the held breath: everyone still, sparks gather into her light"),
    (160.6, "stage", "the choir draws breath"),
    (161.7, "proc", "her light grows into the slam"),
    (162.86, "stage", "SLAM 2: brass and timpani blaze, rays and a huge burst"),
    (165.16, "zion", "the shockwave across the land and sea"),
    (171.48, "zion", "standing firm: the whole mountain full of people"),
    (178.4, "church", "the church over the crowds"),
    (180.7, "zion", "sacrifice: the mountain blazing"),
    (183.0, "stage", "the brass rising"),
    (185.92, "dance", "wondrous love: two dancers, their ribbons cross and draw a heart of light"),
    (188.27, "coda", "thanks to Mother: hearts and lanterns rise"),
    (195.2, "church", "the church in the gathering glow"),
    (197.2, "coda", "the last build: light gathers at the horizon"),
    (199.62, "stage", "the coda hit: the choir"),
    (200.7, "coda", "the last moment before the sun"),
    (201.73, "coda", "SLAM 3: the sun rises over Zion, the biggest burst"),
    (205.98, "coda", "the orchestra on clouds of light round the sun"),
    (210.3, "stage", "the choir in the sunrise"),
    (211.6, "coda", "the third climb: the summit, everyone, arms raised"),
    (218.1, "stage", "sacrifice: the brass"),
    (220.2, "coda", "the summit and the sun"),
    (222.0, "church", "the church blazing"),
    (224.03, "coda", "devotion: the world finale, light from every land flows to Zion"),
    (228.6, "coda", "the glory line over the Earth, hearts across the continents"),
    (235.6, "coda", "the peak: sunrise over the Earth's edge"),
    (238.8, "stage", "home: Oh, the Church of God; the step down, hymn-like"),
    (242.5, "church", "the church at peace, lanterns"),
    (244.8, "stage", "the choir"),
    (247.5, "dance", "the held breath: the dancer still, sparks gather into her, her ribbon flies up"),
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


# =========================================================================================================
# HEAVENLY LIGHT (round 3, like the approved promo): comets of light in the nine colours, moving coloured
# lights that tint the mist and the people, one great light whose rays fan out, lanterns, big bursts.
# Threads register their own light sources; the core hands them to the world at render time.
# =========================================================================================================
MOVING_LIGHTS = []        # dicts: pos(t) -> (3,), color (hex or fn), strength(t) -> 0.., radius
RAY_SOURCES = []          # dicts: pos(t) -> (3,), color, strength(t) -> 0.., size (metres)


def add_light(pos, color, strength, radius=4.0):
    """A moving coloured light (comet heads, Mother's light, a glowing instrument). It glows in the mist,
    lays a pool on the sea and colours points that take `lit`. The world shows the 4 strongest at a time."""
    MOVING_LIGHTS.append(dict(pos=pos, color=color, strength=strength, radius=radius))


def add_rays(pos, strength, color="#fff1d8", size=0.6):
    """A great light whose rays fan out over everything (Mother's light, the church crown, the choir's
    blaze). The world shows the strongest one at each moment."""
    RAY_SOURCES.append(dict(pos=pos, strength=strength, color=color, size=size))


def _val_at(v, t):
    return v(t) if callable(v) else v


def _active_lights(t):
    out = []
    for L in MOVING_LIGHTS:
        k = float(_val_at(L["strength"], t))
        if k > 0.002:
            out.append((k, L))
    out.sort(key=lambda kl: -kl[0])
    return out[:4]


def _light_slot(i):
    def pick(t):
        a = _active_lights(t)
        return a[i] if i < len(a) else None

    def pos(t):
        p = pick(t)
        return np.asarray(_val_at(p[1]["pos"], t), np.float64) if p else np.array([0.0, -1000.0, 0.0])

    def col(t):
        p = pick(t)
        return _val_at(p[1]["color"], t) if p else "#000000"

    def strength(t):
        p = pick(t)
        return float(p[0]) if p else 0.0

    def radius(t):
        p = pick(t)
        return float(_val_at(p[1]["radius"], t)) if p else 1.0

    return dict(pos=pos, color=col, strength=strength, radius=radius)


def _ray_pick(t):
    best, bk = None, 0.0
    for R in RAY_SOURCES:
        k = float(_val_at(R["strength"], t))
        if k > bk:
            best, bk = R, k
    return best, bk


def ray_light():
    """The world's one light with rays: the strongest registered ray source at each moment."""
    def pos(t):
        R, k = _ray_pick(t)
        return np.asarray(_val_at(R["pos"], t), np.float64) if R else np.array([0.0, -1000.0, 0.0])

    def strength(t):
        return _ray_pick(t)[1]

    def color(t):
        R, k = _ray_pick(t)
        return _val_at(R["color"], t) if R else "#fff1d8"

    return dict(pos=pos, strength=strength, color=color, size=0.6, rays=1.0)


_WBOX = {}


def word_boxes(t):
    """Review f19 (approved): the screen boxes (x0, y0, x1, y1, strength) of the phrases arriving or being read
    at t, so comets keep out of them from the first stroke of the writing to the end of the reading."""
    key = round(float(t), 4)
    if key in _WBOX:
        return _WBOX[key]
    out = []
    try:
        cam = CAMERA.state(t)
        for w in WORDS:
            if not (w.t_in - 0.4 <= t <= w.t_out):
                continue
            k = _sc(w.t_in - 0.4, w.t_in, t) * (1.0 - _sc(w.t_read1, w.t_out, t))
            if k <= 0.0:
                continue
            xy, z = cam.project(w.corners(t, cam, pad=0.5 * w.metres_per_em()))
            if np.all(z > 0.1):
                out.append((float(xy[:, 0].min()), float(xy[:, 1].min()), float(xy[:, 0].max()),
                            float(xy[:, 1].max()), float(k)))
    except NameError:          # (before the words exist)
        pass
    if len(_WBOX) > 64:
        _WBOX.clear()
    _WBOX[key] = out
    return out


def keep_out_of_words(t, pos, soft=0.04):
    """1 where a point may show, falling to 0 inside the box of a phrase on screen (soft edge, screen units)."""
    boxes = word_boxes(t)
    if not boxes:
        return None
    xy, z = CAMERA.state(t).project(np.asarray(pos, np.float64))
    m = np.ones(len(xy))
    for x0, y0, x1, y1, k in boxes:
        d = np.minimum(np.minimum(xy[:, 0] - x0, x1 - xy[:, 0]), np.minimum(xy[:, 1] - y0, y1 - xy[:, 1]))
        m *= 1.0 - k * _ss(-soft, soft, d)
    return np.where(z > 0.1, m, 1.0)


class Comet:
    """A comet of light: a bright head with a long glowing trail that follows head(t) back in time, like the
    promo's nine comets. head(t) -> position; t0/t1 when it flies (it fades in and out over `fade` s);
    trail in seconds; width in metres. It can carry a moving light (light=True) that colours the mist."""

    def __init__(self, head, color, t0, t1, trail=1.4, width=0.35, bright=1.0, fade=0.6, light=False, n=90,
                 sparks=True, seed=0, clear=True):
        self.head, self.color, self.t0, self.t1 = head, color, float(t0), float(t1)
        self.clear = bool(clear)          # False for a comet that writes a phrase
        self.trail, self.width, self.bright, self.fade, self.n = float(trail), float(width), float(bright), float(fade), n
        r = np.random.default_rng(int(seed * 97) + 5)
        self.s = r.random((240, 4))
        self.sparks = sparks
        if light:
            add_light(head, color, lambda t: 0.12 * self.k(t) * (0.8 + 0.4 * beat_pulse(t)), radius=5.0)

    def k(self, t):
        return _sc(self.t0, self.t0 + self.fade, t) * (1.0 - _sc(self.t1 - self.fade, self.t1, t))

    def sample(self, t):
        k = self.k(t)
        if k <= 0.0 or local_k(t) <= 0.0:
            return None
        u = np.linspace(0.0, 1.0, self.n)
        P = np.array([self.head(t - self.trail * x) for x in u])
        col = lin(self.color) if isinstance(self.color, str) else np.asarray(self.color)
        pulse = 1.0 + 0.5 * beat_pulse(t) * intensity(t) + 0.8 * hit_pulse(t, KICKS, fall=0.4)
        a = k * (1.0 - u) ** 1.4
        m = keep_out_of_words(t, P) if self.clear else None
        if m is not None:
            a = a * m
            if m[0] < 0.999:
                k = k * float(m[0])
        w = self.width * (1.0 - 0.85 * u)
        out = [dict(pos=P, size=w * 2.2, color=col, alpha=0.30 * a * self.bright, kind="soft", emit=2.0, dof=0.4),
               dict(pos=P, size=w * 0.5, color=col * 0.5 + lin(WHITE) * 0.5, alpha=a * self.bright, kind="spark",
                    emit=3.0 * pulse, dof=0.4),
               dict(pos=P[:1], size=self.width * 5.0, color=col, alpha=0.45 * k * pulse, kind="soft", emit=3.0),
               dict(pos=P[:1], size=self.width * 1.2, color=lin(WHITE), alpha=k, kind="spark", emit=6.0 * pulse)]
        if self.sparks:
            s = self.s
            idx = (s[:, 0] * (self.n - 1)).astype(int)
            age = s[:, 0] * self.trail
            drift = (s[:, 1:4] - 0.5) * (0.4 + 2.2 * s[:, :1]) * self.width * 6.0
            sa = k * (1.0 - s[:, 0]) ** 2 * (m[idx] if m is not None else 1.0)
            out.append(dict(pos=P[idx] + drift, size=0.05 + 0.08 * s[:, 2], color=col * 0.6 + lin(WHITE) * 0.4,
                            alpha=sa, kind="spark", emit=2.5, twinkle=0.8, seed=s[:, 3]))
        return out


def comet_colors():
    return list(COL9)


# the lanterns of thanks: they rise all round Zion on the thanks lines (like the promo's sea of lanterns)
LANTERN_SPANS = [(109.8, 117.5), (188.27, 197.2), (238.8, 254.07)]


def lantern_amount(t):
    if globe_view(t):
        return 0.0
    return max([_sc(a, a + 1.5, t) * (1.0 - _sc(b - 1.0, b, t)) for a, b in LANTERN_SPANS] + [0.0])


# =========================================================================================================
# THE HEAVENLY BACKGROUND (Anthony's reference: the song 02 backdrop): misty lavender mountains on the horizon,
# a mirror sea full of glittering lights, rich stars, constellations of hearts in the nine colours and soft
# comet ribbons far off in the sky. It starts dim and quiet and grows brighter and more glorious at each
# point of the song (glory(t), 0.2 to 1).
# =========================================================================================================
GLORY = [(0.0, 0.18), (11.9, 0.25), (21.5, 0.32), (40.54, 0.40), (53.78, 0.48), (75.2, 0.50), (82.08, 0.68),
         (110.0, 0.72), (117.0, 0.55), (121.32, 0.58), (134.54, 0.66), (156.0, 0.62), (162.86, 0.82),
         (188.27, 0.80), (197.2, 0.86), (201.73, 1.0), (238.8, 0.92), (247.5, 0.80), (249.43, 0.95),
         (254.07, 0.90), (275.0, 0.85)]


def glory(t):
    ts, vs = zip(*GLORY)
    return float(np.interp(t, ts, vs))


def _mix_hex(a, b, k):
    a = np.array([int(a[i:i + 2], 16) for i in (1, 3, 5)], np.float64)
    b = np.array([int(b[i:i + 2], 16) for i in (1, 3, 5)], np.float64)
    c = np.clip(a + (b - a) * float(k), 0, 255).astype(int)
    return "#%02x%02x%02x" % tuple(c)


def hill_color(t):
    """The far mountains: deep violet in the dark, misty lavender as the light grows (rose-gold at sunrise)."""
    g = glory(t)
    c = _mix_hex("#0c0a22", "#3a2c66", min(1.0, g * 1.15))
    return _mix_hex(c, "#6a4a6a", _sc(197.0, 204.0, t) * 0.6)


def _sea_glitter():
    r = np.random.default_rng(2002)
    n = 16000
    rr = 120.0 + 2400.0 * r.random(n) ** 1.6
    a = 2 * np.pi * r.random(n)
    x = rr * np.sin(a)
    z = -200.0 + rr * np.cos(a)
    keep = np.hypot(x - ZC[0], z - ZC[2]) > tier_r(0) + 8.0          # not on the mountain
    x, z, rr = x[keep], z[keep], rr[keep]
    m = len(x)
    P = np.stack([x, np.full(m, 0.12), z], 1)
    k = r.random(m)
    col = np.where(k[:, None] < 0.55, lin("#ffd9a0")[None, :],
                   np.where(k[:, None] < 0.8, lin("#c9b3ff")[None, :],
                            np.asarray([lin(COL9[i]) for i in r.integers(0, 9, m)])))
    size = 0.12 + 0.0016 * rr
    return [_batch(P, size, col, 0.75, kind="spark", emit=2.0, twinkle=1.0, reflect=False),
            _batch(P[::6], size[::6] * 5.0, col[::6] * 0.6, 0.10, kind="soft", emit=1.0, reflect=False)]


def _constellations():
    """The nine expression symbols as constellations in the sky (as in Anthony's references), each in its
    colour, appearing one by one at the song's turning points: bright stars joined by fine lines."""
    from p3d import brand_symbols as BS
    r = np.random.default_rng(909)
    stars, scol, sbirth, la, lb, lcol, lbirth = [], [], [], [], [], [], []
    when = [11.9, 21.5, 40.54, 53.78, 82.08, 121.32, 162.86, 201.73, 224.03]
    for k, name in enumerate(BS.SYMBOLS):
        az = np.radians(150.0 + 70.0 * ((k * 5) % 9) / 8.0 - 35.0 + (180.0 if k in (2, 6) else 0.0))
        el = np.radians(10.0 + 18.0 * r.random())
        d = 2600.0
        c = _v(d * np.cos(el) * np.sin(az), d * np.sin(el), d * np.cos(el) * np.cos(az))
        right = _unit(_v(np.cos(az), 0.0, -np.sin(az)))
        up = -_unit(np.cross(right, c / np.linalg.norm(c)))
        s = 150.0 + 50.0 * r.random()
        col = lin(COL9[k])

        def to3(p2):
            return c[None, :] + s * (p2[:, 0:1] * right[None, :] + p2[:, 1:2] * up[None, :])
        for stroke in BS.strokes(name):
            st = np.asarray(stroke, np.float64)
            L = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(st, axis=0), axis=1))])
            m = max(2, int(L[-1] / 0.30) + 1)
            u = np.linspace(0.0, L[-1], m)
            q = np.stack([np.interp(u, L, st[:, 0]), np.interp(u, L, st[:, 1])], 1)
            P = to3(q)
            stars.append(P)
            scol.append(np.repeat(col[None, :], len(P), 0))
            sbirth.append(when[k] + 0.08 * np.arange(len(P)))
            la.append(P[:-1])
            lb.append(P[1:])
            lcol.append(np.repeat(col[None, :], len(P) - 1, 0))
            lbirth.append(when[k] + 0.4 + 0.08 * np.arange(len(P) - 1))
    S, SC, SB = np.concatenate(stars), np.concatenate(scol), np.concatenate(sbirth)
    A, B2, LC, LB = np.concatenate(la), np.concatenate(lb), np.concatenate(lcol), np.concatenate(lbirth)
    return [_batch(S, 11.0, SC * 0.4 + lin(WHITE) * 0.6, 0.9, kind="spark", emit=3.0, birth=SB, fade=1.2, flash=2.0,
                   twinkle=0.9, dof=0.0),
            _batch(S, 34.0, SC, 0.10, kind="soft", emit=1.2, birth=SB, fade=1.2, dof=0.0),
            _batch(A, 2.5, LC, 0.22, kind="line", pos2=B2, emit=1.4, birth=LB, fade=1.5, dof=0.0)]


def _ribbon_head(k):
    """Soft comet ribbons drifting far off in the sky (like the reference's faint sky comets)."""
    az0 = np.radians(120.0 + 45.0 * k)
    def head(t):
        a = az0 + 0.035 * t
        el = np.radians(22.0 + 9.0 * np.sin(0.05 * t + k))
        d = 2200.0
        return _v(d * np.cos(el) * np.sin(a), d * np.sin(el), d * np.cos(el) * np.cos(a))
    return head


def sky_gain(t):
    return 0.0 if globe_view(t) else glory(t)


# =========================================================================================================
# GRAND (round 4, the promo's scenes): billowing clouds of light, pillars of light from the clouds to the sea.
# CloudBank and Pillars are helpers any thread can place in its own scenes (canyons of cloud to fly through,
# pillars round Zion); the core keeps banks of cloud on the horizon all film, growing with glory.
# =========================================================================================================
CLOUD_COLORS = ("#ffd2a8", "#f4a8c8", "#c0a4f4", "#fff0e0")


class CloudBank:
    """A billowing cloud of light (soft glowing puffs with glitter inside, gold below, rose and lavender
    above), like the promo's clouds. center (3,), size (w, h, d) metres; gain(t) its strength (0 hides it)."""
    static = True

    def __init__(self, center, size=(300.0, 90.0, 120.0), puffs=40, seed=1, gain=None, bright=1.0, colors=None,
                 look="glow"):
        r = np.random.default_rng(int(seed * 101) + 3)
        c = np.asarray(center, np.float64)
        w, h, d = size
        cols = [lin(x) for x in (colors or CLOUD_COLORS)]
        P, S, C, HG = [], [], [], []
        # Anthony (2026-11-19): clouds placed thoughtfully, not random: each bank is one shaped cloud with a flat
        # base, its puffs set in order along its length, tallest in the middle and tapering to the ends
        span = max(w, d)
        along = np.array([1.0, 0.0, 0.0]) if w >= d else np.array([0.0, 0.0, 1.0])
        across = np.array([0.0, 0.0, 1.0]) if w >= d else np.array([1.0, 0.0, 0.0])
        thick = min(w, d)
        for k in range(puffs):
            x = (k + 0.5) / puffs - 0.5 + r.uniform(-0.25, 0.25) / puffs
            env = max(0.0, 1.0 - (2.0 * x) ** 2) ** 0.6
            pc = (c + along * x * span + across * r.uniform(-0.25, 0.25) * thick
                  + np.array([0.0, (0.1 + 0.55 * r.random() ** 1.6) * env * h, 0.0]))
            rad = (0.7 + 0.3 * env) * (0.35 + 0.25 * r.random()) * min(thick, 0.7 * h)
            m = 160
            q = pc + r.normal(0.0, rad * 0.45, (m, 3)) * np.array([1.0, 0.65, 1.0])
            q[:, 1] = np.maximum(q[:, 1], c[1] + 2.0)
            hgt = np.clip((q[:, 1] - c[1]) / max(h, 1.0), 0.0, 1.0)
            col = (cols[0][None, :] * (1 - hgt[:, None]) + cols[1 + k % 2][None, :] * hgt[:, None])
            P.append(q)
            S.append(rad * (0.35 + 0.5 * r.random(m)))
            C.append(col)
            HG.append(np.clip((q[:, 1] - c[1]) / max(np.max(q[:, 1]) - c[1], 1.0), 0.0, 1.0))
        P, S, C, HG = np.concatenate(P), np.concatenate(S), np.concatenate(C), np.concatenate(HG)
        g = r.random(len(P)) < 0.35
        if look == "rim":
            # review f31 (approved): a body of lavender-grey cloud at about half the light, and only the upper
            # rims of each puff lit gold, so a bank frames the view instead of glowing near white
            body = lin("#7c74a0") * 0.55 + C * 0.25
            top = _ss(0.55, 0.95, HG)
            gold = lin("#ffcc88")
            Cb = body * (1.0 - top[:, None]) + gold[None, :] * 0.8 * top[:, None]
            rim = g & (HG > 0.6)
            self.b = [_batch(P, S, Cb * bright * 0.5, 0.02, kind="soft", emit=1.2, dof=0.2),
                      _batch(P[rim], 0.45 + 0.004 * S[rim] * 10, gold * 0.7 + lin(WHITE) * 0.3, 0.45 * bright,
                             kind="spark", emit=2.2, twinkle=0.7, dof=0.2)]
            self.g = gain or (lambda t: sky_gain(t))
            return
        self.b = [_batch(P, S, C * bright, 0.02, kind="soft", emit=1.4, dof=0.2),   # larger puffs: thinner
                  _batch(P[g], 0.5 + 0.004 * S[g] * 10, C[g] * 0.5 + lin(WHITE) * 0.5, 0.7 * bright, kind="spark",
                         emit=2.5, twinkle=0.9, dof=0.2)]
        self.g = gain or (lambda t: sky_gain(t))

    def sample(self, t):
        return self.b

    def gain(self, t):
        return float(self.g(t))


class Pillars:
    """Pillars of light falling from the sky (or a cloud) onto the sea, like the promo's: bright cores with
    soft glowing columns and pools of light where they land; they pulse with the beat.
    bases: list of (x, z); top: height; gain(t) their strength."""

    def __init__(self, bases, top=300.0, color="#ffe2b8", width=3.0, gain=None, seed=2):
        self.bases = np.asarray(bases, np.float64)
        self.top, self.width = float(top), float(width)
        self.col = lin(color)
        self.g = gain or (lambda t: 0.0)
        r = np.random.default_rng(seed)
        self.ph = r.random(len(self.bases))
        n = 90
        self.u = np.linspace(0.0, 1.0, n)

    def sample(self, t):
        g = float(self.g(t))
        if g <= 0.0 or globe_view(t):
            return None
        out = []
        k = g * (0.8 + 0.3 * beat_pulse(t) + 0.5 * hit_pulse(t, KICKS, fall=0.4))
        for i, (x, z) in enumerate(self.bases):
            y = self.u * self.top
            P = np.stack([np.full_like(y, x), y, np.full_like(y, z)], 1)
            a = k * (0.35 + 0.65 * self.u ** 0.3) * (0.85 + 0.15 * np.sin(2.0 * t + 6.0 * self.ph[i]))
            out.append(dict(pos=P, size=self.width * (1.6 + 0.8 * self.u), color=self.col, alpha=0.10 * a,
                            kind="soft", emit=1.8, dof=0.3))
            out.append(dict(pos=P, size=self.width * 0.25, color=self.col * 0.5 + lin(WHITE) * 0.5, alpha=0.5 * a,
                            kind="soft", emit=3.0, dof=0.3))
            out.append(dict(pos=np.array([[x, 0.3, z]]), size=self.width * 9.0, color=self.col, alpha=0.35 * k,
                            kind="soft", emit=2.0, reflect=False))
        return out


def _horizon_clouds():
    """Banks of cloud of light along the horizon all round (the promo's glowing horizon clouds)."""
    out = []
    r = np.random.default_rng(77)
    # in symmetric pairs, framing Zion (straight ahead down the avenue, -z) with its sky left clear above it,
    # and two long low banks out to the sides for the flights; none behind the camera's usual side
    layout = [(180.0 + s * a, d, wd, ht) for a, d, wd, ht in ((24.0, 1450.0, 380.0, 70.0), (46.0, 1300.0, 420.0, 90.0),
                                                         (72.0, 1200.0, 360.0, 60.0), (105.0, 1250.0, 460.0, 45.0))
              for s in (-1.0, 1.0)]
    for k, (azd, d, wd, ht) in enumerate(layout):
        az = np.radians(azd)
        c = _v(d * np.sin(az), 0.0, -200.0 + d * np.cos(az))
        out.append(CloudBank(c, size=(wd, ht, 120.0), puffs=22,
                             seed=k, gain=lambda t: (0.25 + 0.75 * _sc(40.0, 82.0, t)) * sky_gain(t)
                             * (0.3 if stage_view(t) else 1.0)))   # a low white band behind the choir otherwise
    return out


__all__ = [k for k in list(globals()) if not k.startswith("__")]
import songs.s11_church as S_CHURCH  # noqa: E402
import songs.s11_stage as S_STAGE  # noqa: E402
import songs.s11_zion as S_ZION  # noqa: E402
import songs.s11_procession as S_PROC  # noqa: E402
import songs.s11_coda as S_CODA  # noqa: E402
import songs.s11_light as S_LIGHT  # noqa: E402
import songs.s11_dance as S_DANCE  # noqa: E402
import songs.s11_churches as S_CHURCHES  # noqa: E402  (round 7: churches established around the world)
import songs.s11_words as S_WORDS  # noqa: E402  (round 7: the four entrances of the words and their companions)
import songs.s11_music_fx as S_MUSIC  # noqa: E402  (last: it lifts what the others placed)

THREADS = [S_CHURCH, S_STAGE, S_ZION, S_PROC, S_CODA, S_DANCE, S_CHURCHES, S_WORDS, S_MUSIC]
Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C
CORE_SHOTS = [
    # Father's pulse rolls out over the whole Earth: a long graceful pull-back from close over Korea (round 6: the
    # opening view turned a little toward Korea, right of centre, where the dawn ignites)
    dict(name="earth_father", kind="globe", t0=41.6, t1=47.5, fov=46.0, aperture=0.0,
         keys=[(41.6, _gcam(92.0, 10.0, -14.0), G + _v(-9, 8, 0)), (44.5, _gcam(140.0, -12.0, 18.0), G + _v(0, 4, 0)),
               (47.5, _gcam(175.0, 6.0, 8.0), G)]),
    # the Earth turns toward Zion: a swing over the top and down toward Korea
    dict(name="earth_father", kind="globe", t0=47.5, t1=53.78, fov=46.0, aperture=0.0,
         keys=[(47.5, _gcam(140.0, 44.0, -30.0), G + _v(0, 4, 0)), (53.78, _gcam(96.0, 22.0, 4.0), G + _v(0, 10, 0))]),
    # all nations: rivers of light from every continent, the camera sweeping round and in
    dict(name="earth_rivers", kind="globe", t0=70.54, t1=74.56, fov=44.0, aperture=0.0,
         keys=[(70.54, _gcam(140.0, 10.0, 40.0), G + _v(0, 6, 0)), (72.6, _gcam(112.0, 16.0, -6.0), G + _v(0, 10, 0)),
               (74.56, _gcam(86.0, 18.0, 6.0), G + _v(0, 16, 0))]),
    # the drop: the Earth's rim glows, the camera rising over it
    dict(name="earth_rivers", kind="globe", t0=75.2, t1=77.46, fov=46.0, aperture=0.0,
         keys=[(75.2, _gcam(132.0, 8.0), G + _v(0, 8, 0)), (77.46, _gcam(126.0, 34.0), G + _v(0, 18, 0))]),
]


def _gather_shots():
    """One shot per edit block: the owner's shot with exactly the block's times; until a thread has one, its
    older shot that covers the block, clipped to it; else a held wide view (so the film always renders)."""
    pool = {"core": CORE_SHOTS, "church": S_CHURCH.SHOTS, "stage": S_STAGE.SHOTS, "zion": S_ZION.SHOTS,
            "proc": S_PROC.SHOTS, "coda": S_CODA.SHOTS, "dance": S_DANCE.SHOTS}
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
            mv = fly(keys, blend=float(s.get("blend", 0.0)), fov=s["fov"], aperture=s["aperture"], focus=foc,
                     roll=s.get("roll", 0.0), **kw)                 # roll: degrees, a pair or a function (banking)
        moves.append(mv)
    return MusicRig(moves, blend=0.0, fov=50.0, aperture=0.0, handheld=0.12, min_height=0.4, shake=cam_shake)


CAMERA = _rig()
WORLD = S_LIGHT.world()
WORLD["lights"] = [_light_slot(i) for i in range(4)]
WORLD["light"] = ray_light()
WORLD["lantern_field"] = dict(count=320, center=(float(ZC[0]), float(ZC[2]) + 120.0), radius=(60.0, 420.0))
WORLD["lanterns"] = lantern_amount
WORLD["lantern_color"] = GOLD
# the heavenly background (Anthony's reference): misty mountains, lights floating on the sea, growing with glory
WORLD["hills"] = lambda t: 0.0 if globe_view(t) else 1.0
WORLD["hill_height"] = 0.8
WORLD["hill_color"] = hill_color
WORLD["floats"] = lambda t: 0.0 if globe_view(t) else 0.15 + 0.85 * glory(t)
WORLD["float_field"] = dict(count=4200, center=(float(ZC[0]), float(ZC[2]) + 300.0), radius=(300.0, 2600.0), size=1.1)
WORLD["shafts"] = [sh for m in THREADS for sh in getattr(m, "SHAFTS", [])][:4]


def _stage_calm(t):
    """Round 8: the white stage clips to white behind the words; while a phrase is read over a stage shot the
    picture's exposure comes down a little so the stage keeps its colour and the words stand out."""
    if globe_view(t):
        return 1.0
    r = 0.0
    for _l, (a, b, c, d), *_x in PHRASE_LIST:
        if a - 0.6 <= t <= d + 0.6:
            r = max(r, _sc(a - 0.6, b, t) * (1.0 - _sc(c, d + 0.6, t)))
    return 1.0 - (0.40 if stage_view(t) else 0.22) * r


WORLD["exposure"] = lambda t: _stage_calm(t) * S_MUSIC.choir_swell(t)

# =========================================================================================================
# The phrases on screen: Anthony's list, timed to where each is sung on this recording. Round 7 (Anthony: "The
# words that appear can definitely enter and be designed way better"): each phrase takes the entrance that fits
# its music and picture (s11_words.py): "light" (a comet writes it), "people" (lights of the nations walk in
# and become it), "blaze" (the hit's flash lands, the word burns in 0.4 s later with a shockwave across the
# sea), "fly" (large letters ahead; the camera flies through them). Entrances snap to the measured hits/beats.
# (lines, (t_in, t_read0, t_read1, t_out), strong, style, leave)
# =========================================================================================================
PHRASE_LIST = [
    (["The glory of Jerusalem", "Mother shines!"], (53.94, 55.8, 60.0, 61.2), False, "light", "rise"),
    (["All nations and all peoples"], (70.54, 71.73, 74.56, 75.2), False, "people", "morph"),
    (["to the great Church of God!"], (74.56, 75.63, 79.0, 79.9), False, "people", "scatter"),
    (["Joy of salvation!"], (82.08, 82.48, 85.6, 86.6), True, "blaze", "bokeh"),
    (["Sacrifice"], (100.26, 100.66, 103.25, 103.75), True, "blaze", "rise"),
    (["Devotion"], (105.14, 105.54, 108.4, 109.4), True, "blaze", "rise"),
    (["This hope was engraved", "deep in all our hearts"], (133.77, 135.19, 138.4, 139.2), False, "fly", "doors"),
    (["All kings worship You"], (150.23, 151.21, 153.9, 154.55), False, "people", "scatter"),
    (["to the great Church of God!"], (154.9, 156.41, 159.4, 160.3), False, "light", "unravel"),
    (["Joy of salvation!"], (162.86, 163.26, 166.6, 167.6), True, "blaze", "bokeh"),
    (["Sacrifice"], (180.7, 181.1, 183.65, 184.2), True, "blaze", "rise"),
    (["Wondrous love"], (184.65, 185.92, 188.5, 189.1), True, "light", "rise"),
    (["Joy of salvation!"], (201.73, 202.13, 205.4, 206.2), True, "blaze", "bokeh"),
    (["Joy of salvation!"], (209.42, 210.37, 213.2, 214.0), True, "fly", "doors"),
    (["Sacrifice"], (218.1, 218.5, 222.4, 223.0), True, "blaze", "rise"),
    (["Devotion"], (224.03, 224.43, 226.95, 227.4), True, "blaze", "rise"),
    (["We give eternal glory, praise, and thanks", "to Our Father Ahnsahnghong and Mother!"],
     (227.0, 228.79, 234.8, 236.0), True, "people", "scatter"),
    (["Oh, the Church of God"], (238.93, 240.35, 244.6, 245.8), False, "light", "rise"),
]


def _wordcam(t):
    return CAMERA


def _width(ts, depth, frac):
    """The words' width so they fill `frac` of the frame at the narrowest lens they are seen through."""
    fov = min(CAMERA.state(float(t)).fov for t in ts)
    cam = CAMERA.state(float(ts[0]))
    return float(2.0 * depth * np.tan(np.radians(fov) * 0.5) * cam.aspect * frac)


def _phrase_specs():
    return S_WORDS.specs(PHRASE_LIST, _width)


_SPECS = _phrase_specs()
WORDS = PW.Words(_SPECS, camera=CAMERA)


# =========================================================================================================
# Putting it together
# =========================================================================================================
def _setup(scene):
    scene.add("sea glitter", Static(_sea_glitter(), sky_gain))
    scene.add("constellations", Static(_constellations(), sky_gain))
    for k, cb in enumerate(_horizon_clouds()):
        scene.add(f"horizon clouds {k}", cb)
    for k in range(3):
        scene.add(f"sky ribbon {k}", Comet(_ribbon_head(k), COL9[(3 * k + 1) % 9], 0.0, TOTAL, trail=12.0, width=16.0,
                                           bright=0.35, fade=3.0, n=120, sparks=False, seed=50 + k))
    for m in THREADS:
        m.add(scene)
    scene.add("earth", GLOBE, reflect=False)
    scene.add("earth fx", GlobeFX(), reflect=False)
    WORDS.add_to(scene)
    # round 8: the words themselves are never dimmed by the calm region set up behind them (P3D "clear")
    for w in WORDS:
        e = scene._entries.get("word " + w.name)
        if e is not None:
            e.pointset.sample = _unclear(e.pointset.sample)
    WORDS.check(CAMERA, need_all=False)


def _unclear(sample):
    def wrapped(*a, **k):
        out = sample(*a, **k)
        if out is None:
            return out
        for b in (out if isinstance(out, (list, tuple)) else [out]):
            if isinstance(b, dict):
                b["clear"] = False
        return out
    return wrapped


# Round 8 (Anthony: "The text looks terrible"; the promo's words sit on calm dark sky): while a phrase arrives
# and reads, everything behind its frame region (feathered) is held to about half, and comets keep out of it
# entirely (Comet). Two regions at once at most (the engine's two keep-clear boxes).
CALM = 0.92
CALM_FEATHER = 0.06


def _calm_item(i):
    def box(t):
        b = word_boxes(t)
        if i >= len(b):
            return (0.0, 0.0, 0.0, 0.0)
        x0, y0, x1, y1, k = b[i]
        f = CALM_FEATHER
        return (x0 - f, y0 - f, x1 + f, y1 + f)

    def amount(t):
        b = word_boxes(t)
        return CALM * b[i][4] if i < len(b) else 0.0
    return dict(box=box, amount=amount, soft=CALM_FEATHER)


def _reading_k(t):
    """1 while a phrase lands or is read (from 0.3 s before its reading starts to its reading's end)."""
    v = 0.0
    for _l, (a, b, c, d), *_x in PHRASE_LIST:
        if b - 0.6 <= t <= c:
            v = max(v, _sc(b - 0.6, b - 0.3, t))
    return v


def _bursts():
    """Light that follows the music: a soft flash hides each cut (bright on the slams), every big hit flashes
    in one of the nine colours, and in the choruses and the coda each bar's downbeat glows faintly."""
    out = []
    for c in CUTS:
        strong = any(abs(c - s) < 0.05 for s in SLAMS)
        if abs(c - SLAM2) < 0.05:
            # round 7 (task: slam 2 at 2:42.86 washed with glare): a warm, shorter flash under the white stage,
            # gone before "Joy of salvation!" starts to read 0.4 s later
            out.append(dict(t=c, strength=0.42, rise=0.03, fall=0.14, color="#ffe6bc"))
            continue
        out.append(dict(t=c, strength=0.95 if strong else 0.16 + 0.12 * intensity(c), rise=0.04 if strong else 0.04,
                        fall=0.26 if strong else 0.22, color="#fff4e0"))      # a slam flash, gone within a third of a second (round 6: no white-out)
    for i, h in enumerate(KICKS):
        if any(abs(h - s) < 0.05 for s in SLAMS):
            continue
        if i == 0:      # the first chord: a warm gold glow as the star ignites over the title (not a red wash)
            out.append(dict(t=h + 0.01, strength=0.22, rise=0.05, fall=0.6, color="#ffd27a"))
            continue
        out.append(dict(t=h + 0.01, strength=0.35 + 0.45 * intensity(h), rise=0.03, fall=0.5, color=COL9[i % 9]))
    for a, b in ((82.08, 117.0), (162.86, 201.73), (201.73, 238.8)):
        bar = 2.30 if a < 201 else 2.16
        k = 0
        x = a + bar
        while x < b - 0.3:
            out.append(dict(t=x, strength=0.10, rise=0.03, fall=0.3, color=COL9[(k * 4) % 9]))
            x += bar
            k += 1
    out.append(dict(t=HIT["father"], strength=0.45, rise=0.08, fall=0.6, color="#ffeccc",
                    at=tuple(CHURCH + _v(0.0, 20.0, 0.0))))
    # round 8 (relayed from STAGE: the cut flash at 3:05.92 covered "Wondrous love" as it landed): every flash
    # that falls while a phrase lands or is read is held low (the slams keep their own settings above)
    for d in out:
        k = _reading_k(d["t"])
        if k > 0.0 and not any(abs(d["t"] - s) < 0.05 for s in SLAMS):
            d["strength"] *= 1.0 - 0.75 * k
    return sorted(out, key=lambda d: d["t"])


P3D = dict(camera=CAMERA, world=WORDS.world(WORLD), setup=_setup, bursts=_bursts(), motion_blur=0.35,
           clear=[_calm_item(0), _calm_item(1)])


# Anthony (2026-11-19): the logo stays bottom left all film; the song title and the event title appear beside it
# now and then (about every 40 s, 8 s each), never under the opening title or the end card.
SIG_CORNER = "bl"
SIG_TEXT = [(41.6, 49.6), (86.0, 94.0), (122.5, 130.5), (166.0, 174.0), (205.0, 213.0), (240.0, 248.0)]


def _sig_windows():
    logo = []
    for s in SHOTS:
        t0, t1 = s["t0"], s["t1"]
        a = max(t0, 11.6)
        if t1 <= a or t0 >= 254.07:
            continue
        pal = "night" if (s["kind"] in ("globe", "stage") or t0 < 162.86 or s["name"] == "hearts_rise") else "day"
        if logo and logo[-1][3] == pal and abs(logo[-1][1] - a) < 1e-6:
            logo[-1] = (logo[-1][0], t1, SIG_CORNER, pal)
        else:
            logo.append((a, t1, SIG_CORNER, pal))
    w = [(a, b, c, p + ":logo") for a, b, c, p in logo]
    for ta, tb in SIG_TEXT:               # the title lines, cut at the palette changes (quick fade there only)
        for a, b, c, p in logo:
            x0, x1 = max(a, ta), min(b, tb)
            if x1 - x0 > 0.05:
                w.append((x0, x1, c, p + ":text", 0.9 if x0 == ta else 0.12, 0.9 if x1 == tb else 0.12))
    return w                     # from the last chord the end card carries its own lockup


TITLES = dict(
    opening=dict(t_end=11.9, y=0.42, palette="night", dissolve=1.4, build=1.2),
    signature=dict(windows=_sig_windows(), fade=0.12),
    end_card=dict(t_in=LAST_CHORD, fade=1.6, scale=0.94, veil=0.6, backdrop=False),
)
