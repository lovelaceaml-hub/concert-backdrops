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
# The camera: one shot after another, cut on the music's hits (each cut hidden in a soft flash of light)
# =========================================================================================================
class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


Y = SUMMIT
FZ = FACADE_Z
G = GLOBE_C


def _gcam(d, up=0.0, side=0.0):
    """A camera place in front of the Earth of light (it looks toward +z at it)."""
    return G + _v(side, up, -d)


CUTS = [41.6, 53.78, 70.54, 77.46, 82.08, 86.70, 90.72, 117.0, 121.32, 125.92, 162.86, 165.16, 185.92,
        188.27, 201.73, 205.98, 211.6, 224.03, 238.8, 254.07]

SHOTS = [
    # (t0, t1, keys [(t, pos, target)], fov, aperture)
    # A. the waiting city: wide over its edge (the title on the calm sky), down the avenue, close on the steps
    (0.0, 41.6, [(0.0, _v(0.0, Y + 16.0, FZ + 150.0), _v(0.0, Y + 34.0, CHURCH[2])),
                 (11.9, _v(0.0, Y + 11.0, FZ + 118.0), _v(0.0, Y + 22.0, CHURCH[2])),
                 (21.3, _v(0.0, Y + 3.4, FZ + 40.0), _v(0.0, Y + 6.0, FACADE_Z)),
                 (31.0, _v(-2.0, Y + 3.0, FZ + 22.0), _v(0.0, Y + 3.2, FACADE_Z)),
                 (38.8, _v(-1.0, Y + 3.2, FZ + 19.0), _v(0.0, Y + 4.0, FACADE_Z)),
                 (40.54, _v(0.0, Y + 7.0, FZ + 22.0), _v(0.0, Y + 30.0, FACADE_Z + 10.0)),
                 (41.6, _v(0.0, Y + 40.0, FZ + 50.0), _v(0.0, Y + 140.0, FZ + 10.0))], 50.0, 0.02),
    # B. the whole Earth: Father's pulse rolls out over it
    (41.6, 53.78, [(41.6, _gcam(175.0, 6.0), G), (53.78, _gcam(150.0, 14.0, 10.0), G + _v(0, 4, 0))], 46.0, 0.0),
    # C. high over Mount Zion: the crown of light; the city fills with gold
    (53.78, 70.54, [(53.78, ZC + _v(160.0, 140.0, 420.0), ZC + _v(0.0, Y + 22.0, 0.0)),
                    (70.54, ZC + _v(110.0, 120.0, 360.0), ZC + _v(0.0, Y + 16.0, 0.0))], 50.0, 0.0),
    # D. the Earth again: rivers of people from every continent; the camera rises as the horizon glows
    (70.54, 77.46, [(70.54, _gcam(140.0, 10.0), G + _v(0, 6, 0)), (75.2, _gcam(132.0, 12.0), G + _v(0, 8, 0)),
                    (77.46, _gcam(128.0, 30.0), G + _v(0, 16, 0))], 46.0, 0.0),
    # the choir breathes in (cut-in)
    (77.46, 82.08, [(77.46, _v(-3.0, Y + 1.6, FZ + 12.0), _v(-1.0, Y + 3.4, FZ + 2.0)),
                    (82.08, _v(-1.5, Y + 1.7, FZ + 10.5), _v(-0.5, Y + 3.5, FZ + 2.0))], 34.0, 0.03),
    # E. the first slam: the full choir and orchestra, the sunrise jumps behind them
    (82.08, 86.70, [(82.08, _v(0.0, Y + 6.0, FZ + 52.0), _v(0.0, Y + 8.0, FZ - 20.0)),
                    (86.70, _v(0.0, Y + 8.0, FZ + 44.0), _v(0.0, Y + 9.0, FZ - 20.0))], 50.0, 0.0),
    # waves of praise: the whole land ripples with light
    (86.70, 90.72, [(86.70, _v(0.0, 24.0, 160.0), ZC + _v(0.0, 40.0, 0.0)),
                    (90.72, _v(0.0, 26.0, 140.0), ZC + _v(0.0, 42.0, 0.0))], 48.0, 0.0),
    # first climb: Mount Zion wide, the nations standing on it; sacrifice, devotion, thanks
    (90.72, 117.0, [(90.72, _v(0.0, 105.0, 120.0), ZC + _v(0.0, 38.0, 20.0)),
                    (117.0, _v(0.0, 118.0, 20.0), ZC + _v(0.0, 46.0, 0.0))], 50.0, 0.0),
    # the breath: the choir still and glowing, light falling like snow
    (117.0, 121.32, [(117.0, _v(4.0, Y + 2.0, FZ + 15.0), _v(0.0, Y + 3.2, FZ + 2.0)),
                     (121.32, _v(2.5, Y + 2.0, FZ + 13.5), _v(0.0, Y + 3.2, FZ + 2.0))], 34.0, 0.03),
    # verse 2 opens: the strings pulse (cut-in)
    (121.32, 125.92, [(121.32, _v(-14.0, Y + 3.0, FZ + 30.0), _v(-4.0, Y + 1.0, FZ + 14.0)),
                      (125.92, _v(-11.0, Y + 2.6, FZ + 27.0), _v(-3.0, Y + 1.0, FZ + 14.0))], 44.0, 0.02),
    # Mother's light leads everyone across the sea of glass toward Mount Zion; the kings; the held breath
    (125.92, 162.86, [(125.92, _v(-20.0, 7.0, 150.0), ZC + _v(0.0, 40.0, 0.0)),
                      (150.0, _v(-6.0, 9.0, 40.0), ZC + _v(0.0, 42.0, 0.0)),
                      (156.0, _v(-2.0, 10.0, 18.0), ZC + _v(0.0, 45.0, 0.0)),
                      (162.86, _v(0.0, 11.0, 14.0), ZC + _v(0.0, 46.0, 0.0))], 50.0, 0.0),
    # the second slam: brass and timpani blaze (cut-in)
    (162.86, 165.16, [(162.86, _v(12.0, Y + 3.2, FZ + 31.0), _v(4.0, Y + 1.4, FZ + 15.0)),
                      (165.16, _v(10.5, Y + 3.0, FZ + 29.5), _v(4.0, Y + 1.4, FZ + 15.0))], 42.0, 0.02),
    # the shockwave across the land; second climb: the whole mountain full of people
    (165.16, 185.92, [(165.16, _v(0.0, 40.0, 60.0), ZC + _v(0.0, 46.0, 0.0)),
                      (170.0, _v(20.0, 60.0, -60.0), ZC + _v(0.0, 52.0, 0.0)),
                      (185.92, _v(40.0, 84.0, -150.0), ZC + _v(0.0, Y + 6.0, 0.0))], 52.0, 0.0),
    # "wondrous love": brass and timpani (cut-in)
    (185.92, 188.27, [(185.92, _v(-12.0, Y + 3.2, FZ + 31.0), _v(-4.0, Y + 1.4, FZ + 15.0)),
                      (188.27, _v(-10.5, Y + 3.0, FZ + 29.5), _v(-4.0, Y + 1.4, FZ + 15.0))], 42.0, 0.02),
    # thanks to Mother: hearts rise; the last build: light gathers at the horizon behind Zion
    (188.27, 201.73, [(188.27, _v(30.0, 80.0, -140.0), ZC + _v(0.0, Y + 8.0, 0.0)),
                      (201.73, _v(10.0, 60.0, -40.0), ZC + _v(0.0, Y + 14.0, -60.0))], 52.0, 0.0),
    # the coda: the sun rises over Mount Zion
    (201.73, 205.98, [(201.73, _v(0.0, 22.0, 120.0), ZC + _v(0.0, Y + 14.0, -40.0)),
                      (205.98, _v(0.0, 26.0, 100.0), ZC + _v(0.0, Y + 18.0, -40.0))], 54.0, 0.0),
    # the orchestra on clouds of light round the rising sun
    (205.98, 211.6, [(205.98, SKY_STAGE + _v(0.0, 4.0, 46.0), SKY_STAGE + _v(0.0, 6.0, -20.0)),
                     (211.6, SKY_STAGE + _v(0.0, 6.0, 38.0), SKY_STAGE + _v(0.0, 7.0, -20.0))], 50.0, 0.0),
    # third climb: the summit, everyone, the church of light, the sun
    (211.6, 224.03, [(211.6, _v(30.0, Y + 4.0, FZ + 80.0), _v(0.0, Y + 20.0, CHURCH[2])),
                     (224.03, _v(8.0, Y + 6.0, FZ + 56.0), _v(0.0, Y + 24.0, CHURCH[2]))], 54.0, 0.0),
    # the world finale
    (224.03, 238.8, [(224.03, _gcam(150.0, 30.0), G + _v(0, 10, 0)), (238.8, _gcam(170.0, 8.0), G + _v(0, 12, 0))],
     48.0, 0.0),
    # home to everyone on Mount Zion: the final calls, the held breath, the last chord
    (238.8, 254.07, [(238.8, _v(0.0, Y + 4.0, FZ + 40.0), _v(0.0, Y + 6.0, FZ - 10.0)),
                     (254.07, _v(0.0, Y + 5.0, FZ + 30.0), _v(0.0, Y + 7.0, FZ - 10.0))], 50.0, 0.0),
    # the last chord: out to the whole Earth glowing, the end card
    (254.07, TOTAL + 1.0, [(254.07, _gcam(150.0, 6.0), G), (TOTAL + 1.0, _gcam(185.0, 8.0), G)], 46.0, 0.0),
]


ON_GLOBE = {1, 3, 18, 20}           # the shots that look at the Earth of light
ON_STAGE = {4, 5, 8, 9, 11, 13, 19}  # the shots of the choir and orchestra on the square of Zion
SKY = {16}                           # the orchestra on the clouds


def _rig():
    moves = []
    for i, (t0, t1, keys, fov, ap) in enumerate(SHOTS):
        if i in ON_STAGE:
            focus = _v(0.0, SUMMIT + 2.0, FACADE_Z + 3.0) if i in (4, 8) else _v(0.0, SUMMIT + 1.0, FACADE_Z + 14.0)
            moves.append(fly(keys, blend=0.0, ease="linear", fov=fov, aperture=0.09, focus=focus))
        else:
            moves.append(fly(keys, blend=0.0, ease="linear", fov=fov, aperture=ap, focus="target"))
    return Rig(moves, blend=0.0, fov=50.0, aperture=0.0, handheld=0.12, min_height=0.4)


CAMERA = _rig()


def shot_of(t):
    for i, s in enumerate(SHOTS):
        if s[0] <= t < s[1]:
            return i
    return len(SHOTS) - 1




def globe_view(t):
    return shot_of(t) in ON_GLOBE


# =========================================================================================================
# The light of the world: one long sunrise (pre-dawn in the waiting city, full sunrise over Zion at the coda)
# =========================================================================================================
LOOKS = dict(
    city=dict(base="predawn", hills=0.0, stars=0.55, milky=0.25, clouds=0.18, haze=0.45, mist=0.10,
              sky_top="#0a1236", sky_mid="#3a2c6a", sky_hor="#c4786e", water="#05061a", ripple=0.25),
    space=dict(base="night", hills=0.0, stars=1.0, milky=0.75, clouds=0.0, sky_top="#02040f",
               sky_mid="#081236", sky_hor="#1a2a5e", sun_int=0.0, mist=0.02, haze=0.15, haze_color="#1a2a5e",
               water="#03061a", ripple=0.15, rays=0.0),
    zion=dict(base="dawn", hills=0.0, clouds=0.25, mist=0.2, ripple=0.3, water="#0a0a1e"),
    sunrise=dict(base="sunrise", hills=0.0, clouds=0.30, mist=0.12, ripple=0.35, sky_top="#0f2560",
                 sky_mid="#5a3f86", sky_hor="#f09a5c", rays=0.6, exposure=0.82, water="#0a0820", haze=0.4, sun_glow=0.45, sun_disc=5.0),
    golden=dict(base="golden", hills=0.0, clouds=0.25, sky_top="#123a86", sky_mid="#4f6fb4",
                sky_hor="#f2b27a", rays=0.5, sun_glow=0.45, sun_disc=5.0, mist=0.12, ripple=0.3, exposure=0.8,
                water="#0b1838", haze=0.35, haze_color="#b8907a"),
    glory=dict(base="golden", hills=0.0, clouds=0.15, sky_top="#1a4ea6", sky_mid="#5f8fd0",
               sky_hor="#ffcf8f", sun_color="#fff2d6", rays=0.6, sun_glow=0.5, sun_disc=5.5, mist=0.10,
               ripple=0.3, water="#0e2148", haze=0.3, haze_color="#d8b090", exposure=0.8),
    pastel_card=dict(base="day", hills=0.0, sky_top="#9bdbf6", sky_mid="#efcfeb", sky_hor="#ffd9b6",
                     sun_int=0.3, sun_glow=0.3, mist=0.14, haze=0.14, stars=0.2, water="#8ab4e0"),
)


def _local_look(t):
    if t < 53.78:
        return "city"
    if t < 82.08:
        return "zion"
    if t < 162.86:
        return "sunrise"
    if t < 201.73:
        return "golden"
    return "glory"


def _look_keys():
    keys = []
    for i, (t0, t1, *_r) in enumerate(SHOTS):
        if i in ON_GLOBE:
            name = "pastel_card" if t0 >= 254.0 else "space"
        else:
            name = _local_look(t0)
        keys.append((t0, name, 0.0))
    # gentle blends inside the long shots
    keys.append((150.0, "golden", 8.0)) if False else None
    return keys


def sun_el(t):
    if globe_view(t):
        if t >= 254.0:
            return 30.0
        if t >= 224.03:          # the world finale: the same sun rises over the Earth's edge at the peak
            return -4.0 + 26.0 * _sc(226.0, 235.6, t)
        return -12.0 + 10.0 * _sc(75.2, 77.46, t)
    k = [(0.0, -7.0), (53.78, -3.5), (80.0, -1.5), (82.08, 2.6), (160.0, 4.0), (162.86, 6.0), (197.0, 6.8),
         (201.73, 7.0), (206.0, 12.0), (224.0, 16.0), (275.0, 18.0)]
    ts, vs = zip(*k)
    v = float(np.interp(t, ts, vs))
    v += 1.4 * _sc(81.9, 82.3, t) * (1.0 - _sc(82.3, 86.0, t))      # the sun jumps on the slam
    return v


def sun_az(t):
    return 0.0 if globe_view(t) else 163.0          # behind Zion's right shoulder, clear of the words


def sun_int(t):
    if globe_view(t):
        return 0.9 if t >= 224.03 else 0.0
    return 0.40 + 0.25 * _sc(53.0, 82.08, t) + 0.15 * _sc(160.0, 201.73, t) + 0.08 * loud(t)


def rays(t):
    if globe_view(t):
        return 0.6 * _sc(232.0, 236.0, t) if t < 254.0 else 0.0
    base = 0.12 + 0.35 * _sc(80.0, 83.0, t) + 0.2 * _sc(197.0, 202.0, t)
    return base * (0.85 + 0.3 * loud(t)) + 0.2 * hit_pulse(t, [SLAM1, SLAM2, SLAM3], fall=1.2)


WORLD = dict(
    looks=LOOKS,
    look=_look_keys(),
    sun_el=sun_el, sun_az=sun_az, sun_int=sun_int, rays=rays,
    react=dict(beat=0.25, level=0.25),
)


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


def local_k(t):
    """1 while the camera is on Mount Zion (not looking at the Earth of light)."""
    return 0.0 if globe_view(t) else 1.0


def city_k(t):
    """The city and the church behind the choir and orchestra stay soft in the close shots of them."""
    if globe_view(t):
        return 0.0
    i = shot_of(t)
    if i in ON_STAGE:
        return 0.3
    if i == 0:
        return 1.0 - 0.6 * _sc(19.0, 22.0, t)
    return 1.0


# =========================================================================================================
# Mount Zion: a terraced mountain of light; the city on its summit; the church of light at its heart
# =========================================================================================================
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


def _city():
    """Buildings of light on the summit plateau, the great avenue (toward +z) and the square left open."""
    r = np.random.default_rng(11)
    edges, wins, domes = [], [], []
    for gx in np.arange(-84.0, 85.0, 15.0):
        for gz in np.arange(-84.0, 85.0, 15.0):
            x, z = gx + r.uniform(-2.5, 2.5), gz + r.uniform(-2.5, 2.5)
            rad = np.hypot(x, z)
            if rad > 84.0:
                continue
            if abs(x) < 15.0 and z > -12.0:                       # the avenue and the square
                continue
            if abs(x) < 34.0 and -32.0 < z < 22.0:                # the church and its square
                continue
            w, d = r.uniform(7, 11), r.uniform(7, 11)
            h = r.uniform(7, 13) + 16.0 * np.exp(-rad / 45.0) * r.random()
            c = ZC + _v(x, SUMMIT, z)
            edges.append(_box(c, w, d, h, 0.35))
            wins.append(_windows(c, w, d, h))
            if r.random() < 0.18:
                domes.append(_dome(c + _v(0, h, 0), min(w, d) * 0.45, 0.4))
    E, W, D = np.concatenate(edges), np.concatenate(wins), np.concatenate(domes)
    pave = []
    for x in np.arange(-84.0, 85.0, 6.0):
        h = np.sqrt(max(86.0 ** 2 - x * x, 0.0))
        pave.append(_seg(ZC + _v(x, SUMMIT + 0.02, -h), ZC + _v(x, SUMMIT + 0.02, h), 0.6))
    for z in np.arange(-84.0, 85.0, 6.0):
        h = np.sqrt(max(86.0 ** 2 - z * z, 0.0))
        pave.append(_seg(ZC + _v(-h, SUMMIT + 0.02, z), ZC + _v(h, SUMMIT + 0.02, z), 0.6))
    PV = np.concatenate(pave)
    edge = []
    for sx in (-12.0, 12.0):
        edge.append(_seg((sx, SUMMIT + 0.05, FACADE_Z + 30.0), (sx, SUMMIT + 0.05, ZC[2] + R_TOP), 0.25))
    edge.append(_ring(SQUARE, 24.0, SUMMIT + 0.05, 0.25, -np.pi / 2, np.pi / 2))
    edge.append(_ring(SQUARE, 16.0, SUMMIT + 0.05, 0.3, -np.pi / 2, np.pi / 2))
    ED = np.concatenate(edge)
    lamps = []
    for z in np.arange(FACADE_Z + 24.0, ZC[2] + R_TOP, 7.0):
        lamps += [(-10.0, SUMMIT + 4.2, z), (10.0, SUMMIT + 4.2, z)]
    lamps = np.asarray(lamps)
    poles = np.concatenate([_seg((p[0], SUMMIT, p[2]), (p[0], SUMMIT + 4.0, p[2]), 0.2) for p in lamps])
    dimk = 0.55
    return [
        _batch(E, 0.16, lin("#f2c27a") * dimk, 0.8, emit=0.8),
        _batch(W, 0.30, lin("#ffcf86") * dimk, 0.8, kind="soft", emit=0.9, twinkle=0.2),
        _batch(D, 0.16, lin("#ffe0a8") * dimk, 0.8, emit=0.8),
        _batch(lamps, 0.9, lin("#ffcf8a"), 1.0, kind="soft", emit=2.5),
        _batch(lamps, 0.25, lin("#fff2d6"), 1.0, emit=4.0),
        _batch(poles, 0.12, lin("#e8c08a") * 0.6, 0.8, emit=1.0),
        _batch(PV, 0.10, lin("#e8b870") * 0.35, 0.7, emit=0.8),
        _batch(ED, 0.16, lin(GOLD2) * 0.8, 0.9, emit=1.6),
    ], [
        _batch(E, 0.22, lin(GOLD), 0.8, emit=1.2, birth=np.full(len(E), 69.4), fade=0.6, flash=3.0),
        _batch(W, 0.36, lin("#ffe6b0"), 0.8, kind="soft", emit=1.2, birth=np.full(len(W), 69.6), fade=0.8, flash=2.0),
    ]


def _church():
    """The church of light (a placeholder in the right size until the main temple's photographs arrive):
    seven storeys, a broad front of tall arched windows, a central tower and spire, toward the avenue."""
    c = CHURCH
    pts = [_box(c, CH_W, CH_D, CH_H, 0.18)]
    # the front: columns and arched windows, seven storeys
    for f in range(7):
        y = c[1] + 1.6 + f * 3.8
        for b in range(11):
            x = -CH_W / 2 + (b + 0.5) * CH_W / 11
            if abs(x) < 6.0 and f < 3:
                continue
            a = np.linspace(0, np.pi, 14)
            arch = np.stack([x + 1.0 * np.cos(a), y + 2.2 + 0.9 * np.sin(a), np.full(14, FACADE_Z + 0.06)], 1)
            pts += [arch, _seg((x - 1.0, y, FACADE_Z + 0.06), (x - 1.0, y + 2.2, FACADE_Z + 0.06), 0.2),
                    _seg((x + 1.0, y, FACADE_Z + 0.06), (x + 1.0, y + 2.2, FACADE_Z + 0.06), 0.2)]
    for x in np.linspace(-CH_W / 2, CH_W / 2, 12):
        pts.append(_seg((x, c[1], FACADE_Z + 0.4), (x, c[1] + CH_H, FACADE_Z + 0.4), 0.15))
    # the great door: a tall arch
    a = np.linspace(0, np.pi, 40)
    pts.append(np.stack([5.0 * np.cos(a), c[1] + 9.0 + 5.0 * np.sin(a), np.full(40, FACADE_Z + 0.1)], 1))
    pts += [_seg((-5.0, c[1], FACADE_Z + 0.1), (-5.0, c[1] + 9.0, FACADE_Z + 0.1), 0.15),
            _seg((5.0, c[1], FACADE_Z + 0.1), (5.0, c[1] + 9.0, FACADE_Z + 0.1), 0.15)]
    # the tower and spire
    tz = c[2] + 2.0
    pts.append(_box(_v(0.0, c[1] + CH_H, tz), 10.0, 10.0, CH_TOWER - CH_H - 12.0, 0.15))
    top = c[1] + CH_TOWER - 12.0
    for (sx, sz) in ((-5, -5), (5, -5), (5, 5), (-5, 5)):
        pts.append(_seg((sx, top, tz + sz), (0.0, c[1] + CH_TOWER, tz), 0.12))
    for f in range(4):
        y = c[1] + CH_H + 3.0 + f * 4.0
        for x in (-2.5, 0.0, 2.5):
            a = np.linspace(0, np.pi, 10)
            pts.append(np.stack([x + 0.8 * np.cos(a), y + 1.6 + 0.6 * np.sin(a), np.full(10, tz + 5.05)], 1))
    # the steps up to the door, where the choir stands
    for i, (yy, zz) in enumerate(CHOIR_STEPS):
        pts.append(_seg((-CH_W / 2 + 2, yy - 0.05, zz + 0.65), (CH_W / 2 - 2, yy - 0.05, zz + 0.65), 0.25))
    P = np.concatenate(pts)
    return P


def church_glow(t):
    """The church of light: soft in the waiting dawn, shining out on "to the great Church of God!"."""
    return (0.45 + 0.2 * _sc(20.0, 24.0, t) + 0.8 * hit_pulse(t, [HIT["stream"]], fall=2.5)
            + 0.5 * _sc(70.0, 75.0, t) + 0.2 * beat_pulse(t))


class Church:
    static = True

    def __init__(self):
        P = _church()
        self.b = [_batch(P, 0.12, lin("#ffeccc") * 0.7, 1.0, emit=1.1, twinkle=0.25),
                  _batch(P[::3], 0.9, lin("#ffd79a"), 0.12, kind="soft", emit=1.0)]

    def sample(self, t):
        return self.b

    def gain(self, t):
        return city_k(t) * church_glow(t)


def _paths():
    """Paths of light reaching out from the waiting city toward every horizon (from 0:11.9)."""
    out, birth = [], []
    for k, az in enumerate(np.radians([0, 40, 80, 125, 165, 200, 240, 280, 320])):
        d = _v(np.sin(az), 0.0, np.cos(az))
        pts = []
        p = ZC + d * R_TOP + _v(0, SUMMIT, 0)
        q = ZC + d * (tier_r(0) + 6.0) + _v(0, 0.3, 0)
        pts.append(_seg(p, q, 0.45))
        p = q
        pts.append(_seg(p, p + d * 2400.0, 0.9))
        P = np.concatenate(pts)
        L = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        out.append(P)
        birth.append(11.9 + 1.2 * k / 9.0 + L / 70.0)
    P, B = np.concatenate(out), np.concatenate(birth)
    return [_batch(P, 0.30, lin(GOLD2), 0.85, emit=2.0, birth=B, fade=0.35, flash=3.0, twinkle=0.4)]


# =========================================================================================================
# The Earth of light
# =========================================================================================================
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


class Crown:
    """The crown of light that ignites over the city on "The glory of Jerusalem Mother shines!" (0:53.78)."""

    def __init__(self):
        r = np.random.default_rng(31)
        pts, base = [], []
        top = ZC + _v(0.0, SUMMIT + 26.0, 0.0)
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


# =========================================================================================================
# The phrases on screen: Anthony's list, timed to where each is sung on this recording.
# Strong and powerful ones are huge and blaze in gold (rays burn them out of the light); the gentle ones are
# written by light. (t_in, t_read0, t_read1, t_out)
# =========================================================================================================
PHRASE_LIST = [
    # text lines, times, strong, arrive, leave
    (["The glory of Jerusalem", "Mother shines!"], (53.9, 55.4, 60.0, 61.2), False, "gather", "rise"),
    (["All nations and all peoples"], (70.6, 71.9, 73.9, 74.5), False, "weave", "wind"),
    (["to the great Church of God!"], (74.56, 75.7, 79.0, 79.9), False, "pen", "rise"),
    (["Joy of salvation!"], (80.3, 82.08, 85.6, 86.6), True, "rays", "bokeh"),
    (["For Your sacrifice"], (99.4, 100.6, 102.9, 103.6), True, "rays", "rise"),
    (["For Your devotion"], (103.6, 105.14, 108.4, 109.4), True, "rays", "rise"),
    (["This hope was engraved", "deep in all our hearts"], (133.6, 135.6, 140.6, 141.6), False, "reveal", "rise"),
    (["All kings worship You"], (150.4, 151.5, 154.0, 154.8), False, "pen", "wind"),
    (["to the great Church of God!"], (154.9, 156.0, 159.4, 160.3), False, "pen", "rise"),
    (["Joy of salvation!"], (161.0, 162.86, 166.6, 167.6), True, "rays", "bokeh"),
    (["Your sacrifice"], (179.2, 180.2, 182.8, 183.5), True, "rays", "rise"),
    (["Your wondrous love"], (183.6, 185.92, 188.0, 188.8), True, "rays", "rise"),
    (["Joy of salvation!"], (199.9, 201.73, 205.4, 206.2), True, "rays", "bokeh"),
    (["Joy of salvation!"], (209.4, 210.4, 213.6, 214.4), True, "rays", "rise"),
    (["Your sacrifice"], (218.4, 219.3, 222.4, 223.1), True, "rays", "rise"),
    (["For Your devotion"], (223.2, 224.03, 226.2, 226.9), True, "rays", "rise"),
    (["We give eternal glory, praise, and thanks", "to Our Father Ahnsahnghong and Mother!"],
     (227.0, 228.8, 234.8, 236.0), True, "rays", "rise"),
    (["Oh, the Church of God"], (239.0, 240.2, 244.6, 245.8), False, "pen", "rise"),
]


def _wordcam(t):
    return CAMERA


def _width(t, depth, frac):
    cam = CAMERA.state(t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


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
        mid = 0.5 * (r0 + r1)
        spec = dict(label="", lines=lines, ride=ride, face="screen", width=_width(mid, depth, frac),
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
# The choir (gold glitter) and the orchestra (crystal light) on the square of Zion, before the church
# =========================================================================================================
def _choir_places():
    pts = []
    for i, (yy, zz) in enumerate(CHOIR_STEPS[:3]):
        n = 22 - i
        for j in range(n):
            x = (j - (n - 1) / 2.0) * 1.05 + (0.5 if i % 2 else 0.0)
            pts.append((x, yy, zz))
    return np.asarray(pts, np.float64)


ORCH = dict(strings_l=[], strings_r=[], cellos=[], harps=[], timpani=[], brass=[])


def _orch_places():
    """Seats in arcs on the square, facing the avenue (+z); sections: violins left, violas and cellos right,
    harps at the far left, brass and timpani at the back."""
    c = SQUARE + _v(0.0, 0.0, -2.0)
    pts = []
    for row, (r0, n) in enumerate(((7.0, 12), (10.0, 16), (13.0, 18))):
        for j in range(n):
            a = np.radians(-70.0 + 140.0 * j / (n - 1))
            p = c + _v(r0 * np.sin(a), 0.0, r0 * np.cos(a) * 0.55 - 6.0)
            pts.append(p)
            if row == 0:
                (ORCH["strings_l"] if a < 0 else ORCH["strings_r"]).append(p)
            elif row == 1:
                (ORCH["strings_l"] if a < -0.3 else ORCH["cellos"] if a > 0.3 else ORCH["strings_r"]).append(p)
            else:
                (ORCH["brass"] if abs(a) < 0.5 else ORCH["timpani"] if a > 0.9 else ORCH["strings_l"]).append(p)
    ORCH["harps"] = [c + _v(-15.5, 0.0, -2.0), c + _v(-17.0, 0.0, -5.0)]
    return np.asarray(pts, np.float64)


CHOIR_P = _choir_places()
ORCH_P = _orch_places()


def stage_k(t):
    """How present the choir and orchestra are: always there on the square (they show in the wide views of the
    city), formed in the intro (the orchestra wakes from 0:02.3, the choir out of the light from 0:21.5)."""
    return local_k(t)


def _instruments():
    """The orchestra's instruments drawn in crystal light (standing on the square, so they stay put)."""
    pts = []
    for h in ORCH["harps"]:
        a = np.linspace(0.0, 1.0, 40)
        col = _seg(h + _v(0.25, 0.0, 0.0), h + _v(0.25, 1.85, 0.0), 0.03)
        board = _seg(h + _v(-0.45, 0.15, 0.0), h + _v(0.22, 1.75, 0.0), 0.03)
        neck = np.stack([h[0] + 0.25 - 0.70 * a, h[1] + 1.85 - 0.25 * np.sin(np.pi * a) - 0.1 * a, np.full(40, h[2])], 1)
        strings = [_seg(h + _v(-0.45 + 0.67 * u, 0.15 + 1.60 * u, 0.0),
                        h + _v(-0.45 + 0.67 * u, 1.85 - 0.25 * np.sin(np.pi * (1 - u)) - 0.1 * (1 - u), 0.0), 0.04)
                   for u in np.linspace(0.05, 0.95, 16)]
        pts += [col, board, neck] + strings
    for p in ORCH["timpani"]:
        q = p + _v(0.0, 0.0, 0.9)
        pts.append(_ring(q, 0.55, q[1] + 0.85, 0.03))
        for el in np.linspace(0.2, 1.3, 5):
            pts.append(_ring(q, 0.55 * np.cos(el), q[1] + 0.85 - 0.5 * np.sin(el), 0.04))
    for p in ORCH["cellos"]:
        q = p + _v(0.0, 0.0, 0.45)
        a = np.linspace(0, 2 * np.pi, 60)
        pts.append(np.stack([q[0] + 0.22 * np.sin(a) * (1 + 0.15 * np.cos(2 * a)), q[1] + 0.48 + 0.36 * np.cos(a),
                             np.full(60, q[2])], 1))
        pts.append(_seg(q + _v(0.0, 0.84, 0.0), q + _v(0.0, 1.40, -0.05), 0.03))
    for p in ORCH["brass"]:
        q = p + _v(0.0, 0.92, 0.32)
        pts.append(_seg(q, q + _v(0.0, 0.0, 0.42), 0.03))
        pts.append(_ring(q + _v(0.0, 0.0, 0.42), 0.09, q[1], 0.02))
    return np.concatenate(pts)


INSTR_P = None


class Instruments:
    """Crystal instruments; bows of light that move with the beat; light bursting from the brass and timpani
    on the hits (bows and breath move with the beat: Anthony's choice)."""

    def __init__(self, offset=_v(0.0, 0.0, 0.0), gain=None):
        self.P = _instruments() + offset
        self.off = offset
        self.g = gain or stage_k
        r = np.random.default_rng(5)
        self.bp = np.asarray(ORCH["strings_l"] + ORCH["strings_r"], np.float64) + offset
        self.ph = r.random(len(self.bp))
        self.hitters = np.asarray(ORCH["brass"] + ORCH["timpani"], np.float64) + offset
        self.s = r.random((len(self.hitters), 60, 3))

    def sample(self, t):
        g = self.g(t)
        if g <= 0.0:
            return None
        out = [dict(pos=self.P, size=0.035, color=lin(CRYSTAL), alpha=0.9 * g, emit=2.2, kind="spark",
                    twinkle=0.3)]
        # bows: a short line above each string player, drawn back and forth with the beat
        i = np.searchsorted(BEATS, t)
        b0 = BEATS[max(i - 1, 0)] if i > 0 else 0.0
        b1 = BEATS[min(i, len(BEATS) - 1)]
        ph = np.clip((t - b0) / max(b1 - b0, 1e-3), 0.0, 1.0)
        sw = np.cos(np.pi * (ph + self.ph * 0.25)) * (0.22 if t > 2.0 else 0.0)
        c = self.bp + _v(0.18, 0.86, 0.2)
        d = _unit(_v(1.0, -0.35, 0.2))
        a = c + d[None, :] * (sw[:, None] - 0.3)
        b = c + d[None, :] * (sw[:, None] + 0.3)
        out.append(dict(pos=a, pos2=b, size=0.018, color=lin("#f4fbff"), alpha=0.9 * g, emit=2.4, kind="line"))
        # light bursts from the brass and timpani on the big hits
        hits = [HIT["glory"], HIT["stream"], SLAM1, SLAM2, HIT["love"], SLAM3, HIT["devotion"], LAST_CHORD]
        k = 0.0
        last = None
        for h in hits:
            if 0.0 <= t - h < 1.6:
                k, last = np.exp(-(t - h) / 0.45), h
        if k > 0.01:
            u = t - last
            dirs = self.s - 0.5
            dirs /= np.linalg.norm(dirs, axis=2, keepdims=True)
            pos = self.hitters[:, None, :] + _v(0.0, 1.0, 0.4) + dirs * (0.2 + 2.2 * u)
            out.append(dict(pos=pos.reshape(-1, 3), size=0.06, color=lin("#fff1cf"), alpha=k * g, emit=4.0,
                            kind="spark"))
            out.append(dict(pos=self.hitters + _v(0.0, 1.0, 0.4), size=1.6, color=lin(GOLD), alpha=0.5 * k * g,
                            kind="soft", emit=2.0))
        return out


class ChoirLight:
    """Light rising from the choir as they sing: more with the loudness, nothing while they are silent."""

    def __init__(self, places, gain=None):
        self.p = places
        r = np.random.default_rng(9)
        self.s = r.random((len(places) * 6, 4))
        self.g = gain or stage_k

    def sample(self, t):
        g = self.g(t)
        sing = 0.0
        for a, b, w in PERFORM:
            if a <= t < b and w.startswith("Choir"):
                sing = 1.0
        k = g * sing * _sc(21.4, 22.6, t) * (0.35 + 0.65 * loud(t))
        if k <= 0.01:
            return None
        s = self.s
        base = np.repeat(self.p, 6, axis=0) + _v(0.0, 1.55, 0.25)
        age = np.mod(t * (0.25 + 0.2 * s[:, 0]) + s[:, 1], 1.0)
        pos = base + np.stack([0.4 * (s[:, 2] - 0.5), 4.0 * age, 0.3 * (s[:, 3] - 0.5)], 1)
        return dict(pos=pos, size=0.05 + 0.05 * s[:, 2], color=lin("#ffe6b0"), alpha=k * (1 - age) ** 1.5,
                    emit=2.5, kind="spark", twinkle=0.7, seed=s[:, 3])


PERFORM = [(0.0, 21.5, "Orchestra (faint choir hum)"), (21.5, 29.8, "Choir and orchestra"), (29.8, 31.0, "Orchestra"),
           (31.0, 39.0, "Choir and orchestra"), (39.0, 41.0, "Orchestra"), (41.0, 247.5, "Choir and orchestra"),
           (247.5, 249.5, "Held breath"), (249.5, 259.95, "Choir and orchestra"), (259.95, 275.0, "Silence")]


# =========================================================================================================
# The people: the nations on Mount Zion, Mother's light leading everyone across the sea, the kings
# =========================================================================================================
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
    return local_k(t) if 125.92 <= t < 162.86 and shot_of(t) == 10 else 0.0


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


# =========================================================================================================
# Light: pouring down on the people, a column to heaven, snow of light, rings over the land, hearts rising
# =========================================================================================================
def _env(t, a, b, fi=1.0, fo=1.0):
    return _sc(a, a + fi, t) * (1.0 - _sc(b - fo, b, t))


def _shafts():
    return [
        # "sacrifice / devotion" (1:39.4 to 1:49.4): light pours down over the people on Zion
        dict(base=(float(ZC[0]), float(ZC[2]) + 40.0), radius=110.0, top=900.0, spread=-0.4, color="#ffe6bf",
             strength=lambda t: local_k(t) * (shot_of(t) == 7) * _env(t, 99.0, 110.0, 1.5, 1.5) * 0.004),
        # thanks to Father (1:49.8 to 1:57): a column of light rises from the church to heaven
        dict(base=(float(CHURCH[0]), float(CHURCH[2])), radius=16.0, top=3000.0, spread=-0.2, color="#fff2d8",
             strength=lambda t: local_k(t) * (shot_of(t) == 7) * _env(t, 109.8, 117.0, 1.2, 0.3) * 0.06),
        # Mother's light: a soft shaft from above onto the sea where she leads
        dict(base=lambda t: (0.0, float(mother_pos(t)[2])), radius=4.0, top=140.0, spread=-0.5, color="#ffe9c8",
             strength=lambda t: proc_k(t) * _sc(125.92, 128.0, t) * 0.12),
    ]


class Pour:
    """Streaks of light falling on Zion (1:39.4 to 1:49.4) and the column of sparks rising to heaven (1:49.8)."""

    def __init__(self):
        r = np.random.default_rng(91)
        self.f = r.random((1200, 4))
        self.c = r.random((1800, 4))

    def sample(self, t):
        if local_k(t) <= 0.0 or shot_of(t) != 7:
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


class Snow:
    """The breath (1:57 to 2:01.3): light falls like snow round the still, glowing choir."""

    def __init__(self):
        r = np.random.default_rng(101)
        self.s = r.random((1400, 5))

    def sample(self, t):
        if not (116.5 <= t < 121.9) or local_k(t) <= 0.0:
            return None
        k = _env(t, 116.8, 121.8, 0.6, 0.8)
        s = self.s
        y = SUMMIT + 13.0 - np.mod(t * (0.5 + 0.5 * s[:, 2]) + 13.0 * s[:, 3], 13.0)
        x = -16.0 + 32.0 * s[:, 0] + 0.3 * np.sin(t * 0.8 + 6.0 * s[:, 4])
        z = FACADE_Z - 4.0 + 22.0 * s[:, 1]
        return dict(pos=np.stack([x, y, z], 1), size=0.025 + 0.03 * s[:, 4], color=lin("#fff1d8"), alpha=0.6 * k,
                    emit=1.8, kind="soft", twinkle=0.5, seed=s[:, 4])


RINGS = [(86.70, 90.0, 0.6), (88.0, 90.0, 0.45), (89.3, 90.0, 0.35),        # waves of praise ripple the land
         (162.86, 75.0, 1.0), (165.16, 70.0, 0.7), (171.48, 70.0, 0.6)]    # the shockwave of the second slam


class Rings:
    """Rings of light rolling out over the land and the sea from the foot of Mount Zion."""

    def __init__(self):
        a = np.linspace(0, 2 * np.pi, 5000, endpoint=False)
        self.cs = np.stack([np.sin(a), np.cos(a)], 1)
        self.s = np.random.default_rng(111).random(5000)

    def sample(self, t):
        if local_k(t) <= 0.0 or shot_of(t) in ON_STAGE:
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
        if cam is None or local_k(t) <= 0.0 or not (189.0 <= t < 202.0) or shot_of(t) != 14:
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
        if local_k(t) <= 0.0 or not (195.0 <= t < 206.0) or shot_of(t) in ON_STAGE:
            return None
        k = _sc(196.5, 201.6, t) * (1.0 - 0.6 * _sc(202.0, 206.0, t))
        return [dict(pos=self.P, size=7.0, color=lin("#ffd29a"), alpha=0.35 * k, emit=2.0, kind="soft", dof=0.0),
                dict(pos=self.P[::3], size=2.2, color=lin("#fff0d0"), alpha=0.7 * k, emit=3.0, kind="spark",
                     twinkle=0.6, seed=self.s[::3], dof=0.0)]


SKY_OFF = SKY_STAGE - SQUARE


def sky_k(t):
    return 1.0 if shot_of(t) in SKY else 0.0


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


# =========================================================================================================
# Putting it together
# =========================================================================================================
def _setup(scene):
    dim, gold = _mountain()
    scene.add("zion dim", Static(dim, local_k))
    scene.add("zion gold", Static(gold, local_k))
    cdim, cgold = _city()
    scene.add("city dim", Static(cdim, lambda t: city_k(t) * (0.8 + 0.3 * beat_pulse(t) * _sc(20, 22, t))))
    scene.add("city gold", Static(cgold, city_k))
    scene.add("church", Church())
    scene.add("paths", Static(_paths(), lambda t: local_k(t) * (1.0 - 0.75 * _sc(40.0, 42.0, t))))
    scene.add("crown", Crown())
    choir = Crowd(places=CHOIR_P, facing=0.0, kinds=("stand",), people=dict(woman=1.0, man=1.0),
                  start=dict(t=21.3, center=(0.0, FACADE_Z), speed=9.0), color="#ffb84a", color2="#ffe9b8",
                  bright=1.7, points=2400, flash=1.2, glints=0.004, seed=3.0)
    scene.add("choir", choir)
    orch = Crowd(places=ORCH_P, facing=0.0, kinds=("sit",), people=dict(woman=1.0, man=1.0),
                 start=dict(t=2.2, dur=7.0), color=CRYSTAL, color2="#ffffff", bright=1.15, points=2200,
                 glints=0.006, seed=4.0)
    scene.add("orchestra", orch)
    scene.add("instruments", Instruments())
    scene.add("choir light", ChoirLight(CHOIR_P))
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
    # Mother's light leads everyone across the sea (2:05.9); they step out on "march ahead" (2:14.54)
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
    scene.add("pour", Pour())
    scene.add("snow", Snow())
    scene.add("rings", Rings())
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
                               kinds=(("raise", 2.0), ("stand", 2.0), ("cheer", 1.0)), people=dict(woman=1.0, man=1.0, child=0.2),
                               start=dict(t=201.0, center=(0.0, FACADE_Z), speed=40.0), color="#ffc870",
                               color2="#fff2d8", bright=1.5, points=500, seed=41.0))
    scene.add("gather", Gather())
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


WORLD["shafts"] = _shafts()
P3D = dict(camera=CAMERA, world=WORDS.world(WORLD), setup=_setup, bursts=_bursts(), motion_blur=0.35)


def _sig_windows():
    w = []
    for i, (t0, t1, *_r) in enumerate(SHOTS):
        a = max(t0, 11.6)
        if t1 <= a or t0 >= 254.07:
            continue
        pal = "night" if (i in ON_GLOBE or t0 < 162.86) else "day"
        if w and w[-1][3] == pal and abs(w[-1][1] - a) < 1e-6:
            w[-1] = (w[-1][0], t1, w[-1][2], pal)
        else:
            w.append((a, t1, "tl", pal))
    w.append((254.07, TOTAL + 1.0, "tl", "day"))
    return w


TITLES = dict(
    opening=dict(t_end=11.9, y=0.42, palette="night", dissolve=1.4, build=1.2),
    signature=dict(windows=_sig_windows(), fade=0.12),
    end_card=dict(t_in=LAST_CHORD, fade=1.6, scale=0.94, veil=0.6, backdrop=False),
)
