"""The song kit's film module: Song 11's core ("Almighty God Who Knows the Future", tools/s11_full2/s11_full2.py),
generalized so any song can be made the same way. Loaded by tools/song_kit/render.py as the engine song
`songs.kit_film` on the pinned Film 10 engine (d928ff9) with Claude Final v1's words, people and crowds (f43f451).

Every number of the music comes from the song's own data module (`song_data`, tools/song_kit/songs/<id>/):
hits, key moments, the edit list, phrases, the Words of Mother's Love, looks. The generic sections below are
copied unchanged from Song 11's core (its delivered source is not modified). The sets (kit_light, kit_words,
kit_love and the song's own world and sets) star-import this module part way through its load, exactly as
Song 11's threads do. No em dash or en dash anywhere in this file.
"""
import importlib
import os
import sys
from pathlib import Path

import numpy as np

import song_data as D
import songs.s03_original as _base

KIT = Path(__file__).resolve().parents[1]
REPO = KIT.parents[1]

FPS = 60
LIVE = float(D.LIVE)                       # the music part of the video (the recording, unstretched)
HOLD = float(getattr(D, "HOLD", 15.0))     # the calm hold after the music
TOTAL = LIVE + HOLD
_base.FPS = FPS
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * FPS))
_base.MUSIC_END = float(D.MUSIC_END)
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
from p3d.api import ribbon  # noqa: E402,F401
from p3d.camera import Move, Rig, fly  # noqa: E402
from p3d import brand as _brand  # noqa: E402,F401  (import order: brand first, then its symbols and world)

sys.path.insert(0, str(REPO / "tools/nine_colours_minor"))
import reference  # noqa: E402,F401  (Claude Final v1 as package nine_reference_p3d)
from nine_reference_p3d import words as PW  # noqa: E402
from nine_reference_p3d import master_acting  # noqa: E402,F401
from nine_reference_p3d.crowd import Crowd  # noqa: E402

AUDIO_FILE = os.environ.get("AUDIO", "")
FPS = 60
TOTAL = LIVE + HOLD
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = float(D.MUSIC_END)
SONG_END = LIVE
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# =========================================================================================================
# The music (measured on the recording, from the song's data)
# =========================================================================================================
SONG_NAME = D.TITLE                           # (the engine keeps TITLE for its own title settings)
SLAMS = list(getattr(D, "SLAMS", []))          # where the low end comes back in at once
HIT = dict(D.HIT)                              # the big hits, by name
LAST_CHORD = float(D.LAST_CHORD)               # the last chord: the end card dissolves in here

COL9 = [PW.COLORS[k] for k in PW.LABELS]       # the nine campaign colours (Greeting .. Compliment)
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
    if t > LIVE or not len(BEATS):
        return 0.0
    i = np.searchsorted(BEATS, t)
    d = min(abs(t - BEATS[max(i - 1, 0)]), abs(BEATS[min(i, len(BEATS) - 1)] - t))
    return float(np.exp(-d / width))


# =========================================================================================================
# The light budget (Song 11 round 8, Anthony: "Not everything needs to be so washed out and bright all the time.
# Key timings should be highlighted. Do not saturate everything. Do not wash out."): a calm, darker baseline,
# and the big light kept for the key moments. light_budget(t) is 1 on a key moment and LIGHT_REST between them.
# =========================================================================================================
LIGHT_REST = float(getattr(D, "LIGHT_REST", 0.5))
KEY_MOMENTS = list(D.KEY_MOMENTS)              # (start, hold)
INTRO_FULL = float(getattr(D, "INTRO_FULL", 0.0))   # before this the intro builds on its own (budget 1)


def key_moment(t):
    """0..1: how much t is inside a key moment (a quick rise just before it, a 1.2 s release after its hold)."""
    v = 0.0
    for k, d in KEY_MOMENTS:
        if k - 0.3 <= t <= k + d + 1.2:
            v = max(v, _sc(k - 0.3, k, t) * (1.0 - _sc(k + d, k + d + 1.2, t)))
    return v


def light_budget(t):
    """LIGHT_REST at rest, rising to 1 on the key moments; 1 during the intro and from the end card on."""
    if t < INTRO_FULL or t >= LAST_CHORD + 2.0:
        return 1.0
    return LIGHT_REST + (1.0 - LIGHT_REST) * key_moment(t)


def hit_pulse(t, times, rise=0.03, fall=0.6):
    """Sum of sharp pulses at the given times."""
    v = 0.0
    for h in times:
        d = t - h
        if -rise < d < 6.0 * fall:
            v += (_sc(-rise, 0.0, d) if d < 0 else np.exp(-d / fall))
    return float(v)


# =========================================================================================================
# The places: each song's world names its own; the core keeps only the sea of glass (y = 0) and the home view
# =========================================================================================================
HOME = _v(*getattr(D, "HOME", (0.0, 0.0, -420.0)))         # the centre of the song's world on the sea


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

# =========================================================================================================
# The camera: one shot after another, cut on the music's hits (each cut hidden in a soft flash of light).
# Every set gives its own shots; the core gathers them below. A shot: dict(name, kind ("local", "stage", "sky"),
# t0, t1, keys [(t, pos, target)], fov, aperture, focus, pace, blend, roll).
# =========================================================================================================
class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


SHOTS = []
_SHOT_T0 = [0.0]


def shot_of(t):
    """Index of the shot at t (in time order)."""
    return int(max(np.searchsorted(_SHOT_T0, t, side="right") - 1, 0))


def shot_name(t):
    return SHOTS[shot_of(t)]["name"] if SHOTS else ""


def shot_kind(t):
    return SHOTS[shot_of(t)]["kind"] if SHOTS else "local"


def globe_view(t):
    return shot_kind(t) == "globe"


def stage_view(t):
    return shot_kind(t) == "stage"


def local_k(t):
    """1 while the camera is in the song's world (not on the Earth of light)."""
    return 0.0 if globe_view(t) else 1.0


# =========================================================================================================
# The edit: who owns each stretch of the film (the song's data). Each block: from its time to the next.
# =========================================================================================================
EDIT = list(D.EDIT)                            # (t0, owner, note)
EDIT_T = [e[0] for e in EDIT] + [TOTAL + 1.0]
BLOCKS = [dict(t0=e[0], t1=EDIT_T[i + 1], owner=e[1], note=e[2]) for i, e in enumerate(EDIT)]


def blocks_of(owner):
    """The blocks a set owns: [(t0, t1, note)]."""
    return [(b["t0"], b["t1"], b["note"]) for b in BLOCKS if b["owner"] == owner]


# The music's intensity, 0..1 (sections from the measured map; loudness on top)
LEVELS = list(D.LEVELS)


def intensity(t):
    ts, vs = zip(*LEVELS)
    i = int(np.searchsorted(ts, t, side="right")) - 1
    return float(min(1.0, 0.75 * vs[max(i, 0)] + 0.35 * loud(t)))


KICKS = sorted(set(SLAMS + list(HIT.values()) + [LAST_CHORD]))


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
        R, k = _ray_pick(t)
        if R is None or k <= 0.0:
            return k
        # round 8 (f35, f18): calmed where it paled the picture; never blazing from behind a phrase
        k *= S_LIGHT.glare_calm(t)
        m = keep_out_of_words(t, np.asarray(_val_at(R["pos"], t), np.float64)[None, :], soft=0.10)
        if m is not None:
            k *= 0.3 + 0.7 * float(m[0])
        return k

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


def keep_out_of_words(t, pos, soft=0.06, pad=0.04):
    """1 where a point may show, falling to 0 inside the box of a phrase on screen (soft edge, screen units)."""
    boxes = word_boxes(t)
    if not boxes:
        return None
    xy, z = CAMERA.state(t).project(np.asarray(pos, np.float64))
    m = np.ones(len(xy))
    for x0, y0, x1, y1, k in boxes:
        x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
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



# the lanterns of thanks rise on the song's lantern spans
LANTERN_SPANS = list(getattr(D, "LANTERN_SPANS", []))


def lantern_amount(t):
    if globe_view(t):
        return 0.0
    return max([_sc(a, a + 1.5, t) * (1.0 - _sc(b - 1.0, b, t)) for a, b in LANTERN_SPANS] + [0.0])


# =========================================================================================================
# THE HEAVENLY BACKGROUND (as Song 11): far hills, a mirror sea full of glittering lights, rich stars, the nine
# expression symbols as constellations, soft comet ribbons; it grows more glorious through the song (glory(t)).
# =========================================================================================================
GLORY = list(D.GLORY)


def glory(t):
    ts, vs = zip(*GLORY)
    return float(np.interp(t, ts, vs))


def _mix_hex(a, b, k):
    a = np.array([int(a[i:i + 2], 16) for i in (1, 3, 5)], np.float64)
    b = np.array([int(b[i:i + 2], 16) for i in (1, 3, 5)], np.float64)
    c = np.clip(a + (b - a) * float(k), 0, 255).astype(int)
    return "#%02x%02x%02x" % tuple(c)


HILLS = getattr(D, "HILLS", ("#0c0a22", "#3a2c66"))     # the far hills: dark, and lit by glory


def hill_color(t):
    return _mix_hex(HILLS[0], HILLS[1], min(1.0, glory(t) * 1.15))


SEA_CLEAR = getattr(D, "SEA_CLEAR", None)            # (x, z, radius): no glitter there (an island, a shore)


def _sea_glitter():
    r = np.random.default_rng(2002)
    n = 16000
    rr = 120.0 + 2400.0 * r.random(n) ** 1.6
    a = 2 * np.pi * r.random(n)
    x = HOME[0] + rr * np.sin(a)
    z = HOME[2] + 220.0 + rr * np.cos(a)
    keep = np.ones(n, bool) if SEA_CLEAR is None else np.hypot(x - SEA_CLEAR[0], z - SEA_CLEAR[1]) > SEA_CLEAR[2]
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


CONSTELLATIONS = list(getattr(D, "CONSTELLATIONS", []))   # nine times: each symbol appears (empty: none)


def _constellations():
    """The nine expression symbols as constellations in the sky (as in Anthony's references), each in its
    colour, appearing one by one at the song's turning points: bright stars joined by fine lines."""
    from p3d import brand_symbols as BS
    r = np.random.default_rng(909)
    stars, scol, sbirth, la, lb, lcol, lbirth = [], [], [], [], [], [], []
    when = CONSTELLATIONS
    if len(when) < 9:
        return []
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



CLOUD_RAMP = getattr(D, "CLOUD_RAMP", (0.0, 1.0))     # the horizon clouds grow from 25 to 100 percent here


def _horizon_clouds():
    """Banks of cloud of light along the horizon all round, in symmetric pairs framing the home view."""
    out = []
    layout = [(180.0 + s * a, d, wd, ht) for a, d, wd, ht in ((24.0, 1450.0, 380.0, 70.0), (46.0, 1300.0, 420.0, 90.0),
                                                         (72.0, 1200.0, 360.0, 60.0), (105.0, 1250.0, 460.0, 45.0))
              for s in (-1.0, 1.0)]
    a0, a1 = CLOUD_RAMP
    for k, (azd, d, wd, ht) in enumerate(layout):
        az = np.radians(azd)
        c = _v(HOME[0] + d * np.sin(az), 0.0, HOME[2] + 220.0 + d * np.cos(az))
        out.append(CloudBank(c, size=(wd, ht, 120.0), puffs=22,
                             seed=k, gain=lambda t: (0.25 + 0.75 * _sc(a0, a1, t)) * sky_gain(t)
                             * (0.3 if stage_view(t) else 1.0)))
    return out



__all__ = [k for k in list(globals()) if not k.startswith("__")]
import songs.kit_light as S_LIGHT  # noqa: E402  (looks, sun and rays from the song's data)
import songs.kit_words as S_WORDS  # noqa: E402  (the phrases: the approved promo's word style)
import songs.kit_love as S_LOVE  # noqa: E402  (the Words of Mother's Love: arch, expressions, acts)
THREADS = [importlib.import_module("songs." + name) for name in D.SETS] + [S_LOVE, S_WORDS]
CORE_SHOTS = list(getattr(D, "CORE_SHOTS", []))
HOLD_VIEW = getattr(D, "HOLD_VIEW", ((0.0, 6.0, 40.0), (0.0, 8.0, -200.0)))


def _gather_shots():
    """One shot per edit block: the owner's shot with exactly the block's times; else its shot that covers the
    block, clipped to it; else a held wide view (so the film always renders)."""
    pool = {"core": CORE_SHOTS}
    for m in THREADS:
        if getattr(m, "OWNER", None):
            pool.setdefault(m.OWNER, []).extend(getattr(m, "SHOTS", []))
    shots, missing = [], []
    for b in BLOCKS:
        own = pool.get(b["owner"], [])
        hit = [s for s in own if abs(s["t0"] - b["t0"]) < 1e-3 and abs(s["t1"] - b["t1"]) < 1e-3]
        if hit:
            s = dict(hit[0])
        else:
            cover = [s for s in own if s["t0"] - 1e-3 <= b["t0"] < s["t1"]] or [s for s in own if s["t0"] < b["t1"]]
            missing.append(b)
            if cover:
                s = dict(cover[-1], t0=b["t0"], t1=b["t1"], clipped=True)
            else:
                p, q = _v(*HOLD_VIEW[0]), _v(*HOLD_VIEW[1])
                s = dict(name="hold_" + b["owner"], kind="local", t0=b["t0"], t1=b["t1"], fov=50.0, aperture=0.0,
                         keys=[(b["t0"], p, q), (b["t1"], p + _v(0.0, 0.5, -4.0), q)], clipped=True)
        s["block"] = b
        shots.append(s)
    if missing and os.environ.get("KIT_EDIT_REPORT"):
        print(f"edit: {len(missing)} of {len(BLOCKS)} blocks have no exact shot yet", flush=True)
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
            mv.t0, mv.t1 = s["t0"], s["t1"]
        else:
            pace = s.get("pace", "music")
            kw = dict(pace=music_pace(s["t0"], s["t1"])) if pace == "music" else (
                dict(pace=pace) if pace not in (None, "linear") else dict(ease="linear"))
            mv = fly(keys, blend=float(s.get("blend", 0.0)), fov=s["fov"], aperture=s["aperture"], focus=foc,
                     roll=s.get("roll", 0.0), **kw)
        moves.append(mv)
    return MusicRig(moves, blend=0.0, fov=50.0, aperture=0.0, handheld=0.12, min_height=0.4, shake=cam_shake)


CAMERA = _rig()
WORLD = S_LIGHT.world()
WORLD["lights"] = [_light_slot(i) for i in range(4)]
WORLD["light"] = ray_light()
WORLD["lantern_field"] = dict(getattr(D, "LANTERN_FIELD", dict(count=320, center=(float(HOME[0]), float(HOME[2]) + 120.0),
                                                                radius=(60.0, 420.0))))
WORLD["lanterns"] = lantern_amount
WORLD["lantern_color"] = GOLD
WORLD["hills"] = lambda t: 0.0 if globe_view(t) else 1.0
WORLD["hill_height"] = float(getattr(D, "HILL_HEIGHT", 0.8))
WORLD["hill_color"] = hill_color
WORLD["floats"] = lambda t: 0.0 if globe_view(t) else 0.15 + 0.85 * glory(t)
WORLD["float_field"] = dict(count=4200, center=(float(HOME[0]), float(HOME[2]) + 300.0), radius=(300.0, 2600.0),
                            size=1.1)
WORLD["shafts"] = [sh for m in THREADS for sh in getattr(m, "SHAFTS", [])][:4]
_arch = S_LOVE.arch_world()
if _arch:
    WORLD["arch"] = _arch


def _deep(t):
    """The picture's exposure follows the light budget (calm and darker between the key moments, full on them)."""
    if t < INTRO_FULL:
        return 1.0 if stage_view(t) else 0.85
    slam = 1.0 - 0.5 * hit_pulse(t, SLAMS, rise=0.02, fall=0.7)    # a burst of colour, not a white frame
    return (0.02 + 0.98 * light_budget(t) ** 1.6) * slam


PHRASE_LIST = list(getattr(D, "PHRASES", []))     # (lines, (t_in, t_read0, t_read1, t_out), strong, style, leave)


def _read_windows():
    """Every word read on screen: the phrases and the expressions (t_in, t_read0, t_read1, t_out)."""
    return [w for _l, w, *_x in PHRASE_LIST] + S_LOVE.read_windows()


def _calm_words(t):
    """While words are read the picture's exposure comes down a little so they stand out (Song 11 round 8)."""
    r = 0.0
    for a, b, c, d in _read_windows():
        if a - 0.6 <= t <= d + 0.6:
            r = max(r, _sc(a - 0.6, b, t) * (1.0 - _sc(c, d + 0.6, t)))
    return 1.0 - (0.33 if stage_view(t) else 0.18) * r


WORLD["exposure"] = lambda t: _calm_words(t) * _deep(t)


def _wordcam(t):
    return CAMERA


def _width(ts, depth, frac):
    """The words' width so they fill `frac` of the frame at the narrowest lens they are seen through."""
    fov = min(CAMERA.state(float(t)).fov for t in ts)
    cam = CAMERA.state(float(ts[0]))
    return float(2.0 * depth * np.tan(np.radians(fov) * 0.5) * cam.aspect * frac)


_SPECS = S_WORDS.specs(PHRASE_LIST, _width) + S_LOVE.specs(_width)
WORDS = PW.Words(_SPECS, camera=CAMERA)


def _setup(scene):
    scene.add("sea glitter", Static(_sea_glitter(), sky_gain))
    cs = _constellations()
    if cs:
        scene.add("constellations", Static(cs, sky_gain))
    for k, cb in enumerate(_horizon_clouds()):
        scene.add(f"horizon clouds {k}", cb)
    for k in range(3):
        scene.add(f"sky ribbon {k}", Comet(_ribbon_head(k), COL9[(3 * k + 1) % 9], 0.0, TOTAL, trail=12.0, width=16.0,
                                           bright=0.35, fade=3.0, n=120, sparks=False, seed=50 + k))
    for m in THREADS:
        if hasattr(m, "add"):
            m.add(scene)
    WORDS.add_to(scene)
    WORDS.check(CAMERA, need_all=False)


def _reading_k(t):
    """1 while words land or are read (from 0.3 s before the reading starts to its end)."""
    v = 0.0
    for a, b, c, d in _read_windows():
        if b - 0.6 <= t <= c:
            v = max(v, _sc(b - 0.6, b - 0.3, t))
    return v


BAR_GLOWS = list(getattr(D, "BAR_GLOWS", []))     # (from, to, bar seconds): a faint glow on each downbeat


def _bursts():
    """Light that follows the music (as Song 11): a short warm flash hides each cut (stronger on the slams),
    every big hit flashes in one of the nine colours, each bar's downbeat glows faintly in the strong parts,
    and every flash that falls while words land or are read is held low."""
    out = []
    for c in CUTS:
        strong = any(abs(c - s) < 0.05 for s in SLAMS)
        out.append(dict(t=c, strength=0.45 if strong else 0.16 + 0.12 * intensity(c), rise=0.03 if strong else 0.04,
                        fall=0.15 if strong else 0.22, color="#ffd9a8" if strong else "#fff4e0"))
    for i, h in enumerate(sorted(HIT.values())):
        if any(abs(h - s) < 0.05 for s in SLAMS):
            continue
        out.append(dict(t=h + 0.01, strength=0.35 + 0.45 * intensity(h), rise=0.03, fall=0.5, color=COL9[i % 9]))
    for a, b, bar in BAR_GLOWS:
        k, x = 0, a + bar
        while x < b - 0.3:
            out.append(dict(t=x, strength=0.10, rise=0.03, fall=0.3, color=COL9[(k * 4) % 9]))
            x += bar
            k += 1
    for d in out:
        k = _reading_k(d["t"])
        if k > 0.0 and not any(abs(d["t"] - s) < 0.05 for s in SLAMS):
            d["strength"] *= 1.0 - 0.75 * k
    return sorted(out, key=lambda d: d["t"])


P3D = dict(camera=CAMERA, world=WORDS.world(WORLD), setup=_setup, bursts=_bursts(), motion_blur=0.35)


# Anthony (2026-11-19): the logo stays bottom left all film; the song title and the event title appear beside it
# now and then (about every 40 s, 8 s each), never under the opening title or the end card.
SIG_CORNER = "bl"
OPENING_END = float(getattr(D, "OPENING_END", 8.0))
SIG_TEXT = list(getattr(D, "SIG_TEXT", []))


def _sig_palette(t0):
    f = getattr(D, "sig_palette", None)
    return f(t0) if f else "night"


def _sig_windows():
    logo = []
    for s in SHOTS:
        t0, t1 = s["t0"], s["t1"]
        a = max(t0, OPENING_END - 0.3)
        if t1 <= a or t0 >= LAST_CHORD:
            continue
        t1 = min(t1, LAST_CHORD)
        pal = _sig_palette(t0)
        if logo and logo[-1][3] == pal and abs(logo[-1][1] - a) < 1e-6:
            logo[-1] = (logo[-1][0], t1, SIG_CORNER, pal)
        else:
            logo.append((a, t1, SIG_CORNER, pal))
    w = [(a, b, c, p + ":logo") for a, b, c, p in logo]
    for ta, tb in SIG_TEXT:
        for a, b, c, p in logo:
            x0, x1 = max(a, ta), min(b, tb)
            if x1 - x0 > 0.05:
                w.append((x0, x1, c, p + ":text", 0.9 if x0 == ta else 0.12, 0.9 if x1 == tb else 0.12))
    return w


TITLES = dict(
    opening=dict(t_end=OPENING_END, y=0.42, palette="night", dissolve=1.4, build=1.2),
    signature=dict(windows=_sig_windows(), fade=0.12),
    end_card=dict(t_in=LAST_CHORD, fade=1.6, scale=0.94, veil=0.6, backdrop=False),
)
