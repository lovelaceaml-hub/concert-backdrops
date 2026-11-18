"""Song 06 "Heavenly Mother Tells Us to Be Grains": the full-length concert backdrop.

Design: project-docs/designs/06 Heavenly Mother Tells Us to Be Grains.md ("The Field That Grew From One
Grain"), in the approved Nine Colours Revision 3 look (warm gold glitter people, cream serif phrases with
coloured capsule labels, warm heavenly light), with the backdrop rules: calm camera, calm bottom third,
expression phrases large and readable 8 to 10 s in the upper middle, a small signature, a calm hold after
the music. Times here are REFERENCE TIME in seconds on the 134.85 s concert recording. The renderer
(tools/s06_full2/render.py) maps every live frame onto this clock: the live length is 137.0 s, so the music
part runs 137.0 / 134.85 slower (every section scaled by the same factor, the conformed audio with it), and the
15 s calm hold runs at normal speed. TIMELINE.md (project-docs/backdrops/s06-full2/) gives the live times.

Loaded by tools/s06_full2/render.py as engine song "s06_full2_song" inside the pinned Film 10 engine
(commit d928ff9), exactly as the approved promo loads ten_10_nine_colours. Everything is a pure function of
time, so any frame renders on its own and parts can render in parallel.

No em dash or en dash anywhere in this file.
"""
import os

import numpy as np

import songs.s03_original as _base

FPS = 60
MUSIC_END = 134.8467           # the reference recording's decoded length (it stops at full strength at about 134.3)
HOLD = 15.0                   # the calm hold after the music
LIVE = 137.0                  # the live length (DESIGN-SYSTEM 4); the stage video is LIVE + HOLD = 152.0 s
K = LIVE / MUSIC_END          # live seconds per reference second in the music part
NFRAMES = int(round((LIVE + HOLD) * FPS))     # 9120 frames at 60 fps
TOTAL = MUSIC_END + HOLD      # the end of the reference clock (149.85)


def ref_time(t_live):
    """The reference clock for a live time: scaled in the music, normal speed in the hold."""
    return t_live / K if t_live <= LIVE else MUSIC_END + (t_live - LIVE)


def live_time(t_ref):
    return t_ref * K if t_ref <= MUSIC_END else LIVE + (t_ref - MUSIC_END)

_base.TOTAL = TOTAL
_base.NFRAMES = NFRAMES
_base.MUSIC_END = MUSIC_END
_base.SONG_END = MUSIC_END
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])          # never a fade to black
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9                   # the words are particle words in 3D
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402

TOTAL = MUSIC_END + HOLD
MUSIC_END = 134.8467
SONG_END = 134.8467
BOTTOM_CALM = 1.0             # the choir and orchestra stand in front: a calm lower third
TEXT_SHADOW = 0.0             # nothing dark behind any text
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# ---------------------------------------------------------------------------------------------------------
# The music (measured on the concert recording, TIMELINE.md). Verse 2 repeats verse 1 exactly 62.5 s later.
# ---------------------------------------------------------------------------------------------------------
V1, V2 = 10.0, 72.5           # verse starts (the grains line)
REFRAIN1, REFRAIN2 = 46.3, 108.8
PEAK1, PEAK2 = 64.4, 126.3    # the loudest moments of each half
LAST_NOTE = 134.35            # the music stops here, at full strength
HITS = (18.2, 80.6, 126.3)    # sync checkpoints (a breath and its downbeat, the second breath, the big hit)


def _ss(a, b, x):
    if np.isscalar(a) and np.isscalar(b) and b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (np.asarray(b, np.float64) - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _win(a, b, c, d, t):
    """0 before a, rising to 1 at b, 1 until c, falling to 0 at d."""
    return _sc(a, b, t) * (1.0 - _sc(c, d, t))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


_FEAT = np.load(os.environ["FEATURES"]) if os.environ.get("FEATURES") else None
BEATS = np.asarray(_FEAT["beats"], np.float64) if _FEAT is not None and "beats" in _FEAT.files else \
    np.arange(0.58, MUSIC_END, 0.4645)
DOWNBEATS = BEATS[::4]

# ---------------------------------------------------------------------------------------------------------
# The words (exact campaign wording, words.EXPRESSIONS; website colours)
# ---------------------------------------------------------------------------------------------------------
import importlib  # noqa: E402
import sys  # noqa: E402

_TOOLS = os.path.dirname(os.path.abspath(__file__))
if os.path.join(os.path.dirname(_TOOLS), "nine_colours_minor") not in sys.path:
    sys.path.insert(0, os.path.join(os.path.dirname(_TOOLS), "nine_colours_minor"))
importlib.import_module("reference")
PW = importlib.import_module("nine_reference_p3d.words")
COL = PW.COLORS
GOLD = "#ffd27a"
CREAM = "#fff4dc"

# Concession lights star 5 for the first time; Inclusiveness lights star 4 again (the star flares, one ring)
CONC = dict(t_in=70.9, t_read0=72.1, t_read1=80.6, t_out=82.0)
INCL = dict(t_in=82.2, t_read0=83.3, t_read1=92.8, t_out=94.2)
FRAG = {
    "grains": dict(text="grains who will sacrifice", t_in=10.6, t_read0=11.8, t_read1=16.4, t_out=17.6),
    "love": dict(text="Love one another", t_in=18.6, t_read0=19.6, t_read1=24.6, t_out=25.6),
    "bright": dict(text="the world brightens up", t_in=41.6, t_read0=42.8, t_read1=47.6, t_out=48.8),
    "water": dict(text="waters this wilderness", t_in=94.8, t_read0=95.9, t_read1=100.4, t_out=101.4),
    "fragrance": dict(text="the fragrance of Her love", t_in=102.0, t_read0=103.2, t_read1=107.8, t_out=109.0),
}
WORD_Y = 0.640                # the middle of each text block, from the BOTTOM (0.345 from the top)
WORD_DEPTH = 7.0

# ---------------------------------------------------------------------------------------------------------
# Geography (metres, y up, the lake is y = 0, the low sun stands toward -z)
# ---------------------------------------------------------------------------------------------------------
GRAIN = _v(0.0, 6.5, -40.0)             # where the warmed grain hangs, above the middle of the lake
FAM = _v(-0.6, 0.0, -13.0)              # the family of three
PATH = _v(0.0, 0.0, -12.0)              # the narrow path ("Please, after you.")
SHORE = _v(0.0, 0.0, -9.6)              # the water's edge ("It's okay. I understand.")
WILD = _v(40.0, 0.0, -78.0)             # the dry wilderness
SPRING = WILD + _v(-4.0, 0.0, 6.0)      # where the second grain falls and the spring wells up
LAMP = _v(-3.2, 0.0, 6.5)               # the small lantern on the near shore (hand-off to song 07)
ARCH = dict(span=150.0, height=66.0, z=-115.0)

# ---------------------------------------------------------------------------------------------------------
# The camera: slow, reverent, one continuous move; performers stand in front, so nothing whips
# ---------------------------------------------------------------------------------------------------------
class EaseKeys(Move):
    """The camera glides from key to key, easing out of each and into the next (no overshoot, never a whip).
    keys: [(t, pos, target), ...]."""

    def __init__(self, keys, **kw):
        super().__init__(keys[0][0], keys[-1][0], **kw)
        self.ts = np.array([k[0] for k in keys], np.float64)
        self.P = np.array([k[1] for k in keys], np.float64)
        self.T = np.array([k[2] for k in keys], np.float64)

    def pose(self, t):
        if t <= self.ts[0]:
            return self.P[0].copy(), self.T[0].copy()
        if t >= self.ts[-1]:
            return self.P[-1].copy(), self.T[-1].copy()
        i = int(np.searchsorted(self.ts, t, side="right")) - 1
        u = (t - self.ts[i]) / (self.ts[i + 1] - self.ts[i])
        u = u * u * u * (u * (u * 6.0 - 15.0) + 10.0)
        return self.P[i] * (1 - u) + self.P[i + 1] * u, self.T[i] * (1 - u) + self.T[i + 1] * u


CAM_H = 0.95                  # eye height in the people scenes: their feet stay above the bottom third
_KEYS = [
    (0.0, _v(0.0, 2.4, 26.0), _v(0.0, 18.0, -40.0)),
    (7.6, _v(0.0, 2.4, 22.6), _v(0.0, 15.5, -40.0)),
    (12.0, _v(0.0, 2.6, 19.0), _v(0.0, 5.2, -40.0)),
    (16.4, _v(0.0, 2.5, 16.5), _v(0.0, 5.0, -40.0)),
    (19.4, _v(0.2, 2.04, -0.8), _v(-0.4, 1.51, -13.4)),
    (30.0, _v(-0.2, 2.09, -1.2), _v(-0.5, 1.56, -13.4)),
    (38.0, _v(0.0, 34.0, 26.0), _v(0.0, 8.0, -240.0)),
    (45.0, _v(0.0, 36.0, 30.0), _v(0.0, 8.0, -250.0)),
    (55.0, _v(3.0, 8.0, 10.0), _v(0.0, 6.0, -180.0)),
    (65.0, _v(1.0, 7.0, 8.0), _v(0.0, 5.5, -170.0)),
    (70.2, _v(0.0, 2.04, 0.4), _v(0.0, 1.51, -12.4)),
    (80.4, _v(0.0, 2.04, 0.1), _v(0.0, 1.51, -12.4)),
    (83.0, _v(0.0, 2.04, 2.4), _v(0.0, 1.51, -10.0)),
    (84.4, _v(0.0, 1.95, 1.8), _v(0.0, 1.45, -10.0)),
    (86.6, _v(0.0, 1.32, -1.6), _v(0.0, 0.97, -10.0)),
    (87.6, _v(0.0, 1.32, -1.75), _v(0.0, 0.97, -10.0)),
    (90.9, _v(0.0, 2.04, 2.6), _v(0.0, 1.51, -10.0)),
    (94.6, _v(0.0, 2.04, 2.8), _v(0.0, 1.51, -10.0)),
    (98.5, _v(17.0, 8.0, -38.0), _v(40.0, 2.0, -80.0)),
    (101.8, _v(19.0, 7.5, -42.0), _v(40.0, 2.0, -82.0)),
    (106.5, _v(6.0, 7.0, -16.0), _v(0.0, 4.0, -140.0)),
    (111.5, _v(0.0, 30.0, 30.0), _v(0.0, 4.0, -200.0)),
    (127.0, _v(0.0, 44.0, 46.0), _v(0.0, 4.0, -210.0)),
    (134.0, _v(0.0, 42.0, 44.0), _v(0.0, 4.0, -205.0)),
    (142.5, _v(0.0, 2.6, 21.0), _v(0.0, 8.0, -40.0)),
    (TOTAL, _v(0.0, 2.5, 19.8), _v(0.0, 7.9, -40.0)),
]


def _fov(t):
    return 50.0 - 4.0 * _win(17.5, 19.4, 30.0, 33.0, t) - 4.0 * _win(68.0, 70.2, 93.6, 97.0, t)


def _rig(focus):
    return Rig([EaseKeys(_KEYS, fov=_fov, aperture=0.012, focus=(lambda t: focus(t)) if focus else "target")],
               blend=0.0, fov=50.0, aperture=0.012, handheld=0.03, min_height=0.4)


_LAYOUT = _rig(None)


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


def _width(t, frac, depth=WORD_DEPTH):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


# ---------------------------------------------------------------------------------------------------------
# The arch of nine lights: 3, 4, 6, 7, 8, 9 lit from the start; 5 lights at Concession; 4 flares again
# ---------------------------------------------------------------------------------------------------------
STAR5_T = CONC["t_out"] - 0.1
STAR4_T = INCL["t_out"] - 0.1
_ARCH_LIT = (2, 3, 5, 6, 7, 8)


def _arch_lit(t):
    out = []
    for i in range(9):
        if i in _ARCH_LIT and i != 3:
            out.append((0.62, 99.0))
        elif i == 3:
            age = t - STAR4_T
            if age >= -0.3:
                out.append((0.62 + 1.1 * np.exp(-max(age, 0.0) * 1.1) * _sc(-0.3, 0.0, age), max(age, 0.0)))
            else:
                out.append((0.62, 99.0))
        elif i == 4:
            age = t - STAR5_T
            if age < -0.35:
                out.append((0.0, -1.0))
            else:
                g = min(max((age + 0.35) / 0.35, 0.0), 1.0)
                out.append((0.62 * g + 1.2 * np.exp(-max(age, 0.0) * 1.2) * g, max(age, 0.0)))
        else:
            out.append((0.0, -1.0))
    return out


def _arch_points():
    from p3d.world import Arch
    return Arch(None, span=ARCH["span"], height=ARCH["height"], z=ARCH["z"])


_ARCH_GEOM = None


def star_point(i, t=0.0):
    global _ARCH_GEOM
    if _ARCH_GEOM is None:
        _ARCH_GEOM = _arch_points()
    return _ARCH_GEOM.homes(t)[i]


# ---------------------------------------------------------------------------------------------------------
# Words
# ---------------------------------------------------------------------------------------------------------
_RIDE = (0.5, WORD_Y, WORD_DEPTH)


def _specs():
    specs = [
        dict(expr="Concession", ride=_RIDE, face="screen", width=_width(76.0, 0.44), pill=True,
             arrive="pen", nib=False, leave="fade", reflect=False, **CONC),
        dict(expr="Inclusiveness", ride=_RIDE, face="screen", width=_width(88.0, 0.56), pill=True,
             arrive="pen", nib=False, leave="fade", reflect=False, **INCL),
    ]
    widths = dict(grains=0.40, love=0.30, bright=0.38, water=0.38, fragrance=0.42)
    leaves = dict(grains="fade", love="fade", bright="fade", water="fade", fragrance="fade")
    for key, f in FRAG.items():
        d = dict(f)
        text = d.pop("text")
        mid = 0.5 * (d["t_read0"] + d["t_read1"])
        specs.append(dict(label="", lines=[text], name=key, ride=_RIDE, face="screen",
                          width=_width(mid, widths[key]), color=GOLD, glow="#ffb860", tint=0.30,
                          arrive="pen", nib=False, leave=leaves[key], reflect=False, **d))
    return specs


def _clean_leave(t, info):
    """As the approved Revision 3 (tools/nine_colours_minor/expressions.py): letters stay whole while they
    leave, and fade in place (no garbled or broken letters)."""
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)


WORDS = PW.Words(_specs(), camera=_LAYOUT, reflect=False, drive=_clean_leave)


def _focus(t):
    cam = PW._cam_at(_LAYOUT, t)
    d = float(np.linalg.norm(cam.target - cam.pos))
    return WORDS.focus(t, cam.pos, default=d)


CAMERA = _rig(_focus)


# ---------------------------------------------------------------------------------------------------------
# Point sets of this song
# ---------------------------------------------------------------------------------------------------------
class Grain:
    """The grain of light: warmed in the horizon star's halo, let go, falls without a splash and gives its
    light away as it sinks. A second grain falls on the wilderness; a last one falls in the calm hold."""

    T_LET, T_LAND = 9.2, 10.0
    T2_LET, T2_LAND = 67.0, 68.4
    T3_LET, T3_LAND = 136.6, 138.4

    def __init__(self):
        r = np.random.default_rng(61)
        n = 420
        d = r.normal(size=(n, 3))
        self.d = d / np.linalg.norm(d, axis=1, keepdims=True)
        self.s = r.random((n, 3))

    def _one(self, p, k, warm, t):
        out = []
        if k <= 0.003:
            return out
        col = lin("#fff0c8") * (1.0 - warm) + lin("#ffb048") * warm
        pulse = 1.0 + 0.18 * np.sin(t * 2 * np.pi / 1.4)
        out.append(dict(pos=p[None, :], size=0.45 * pulse, color=col, alpha=k, emit=5.0, kind="spark", lod=False))
        out.append(dict(pos=p[None, :], size=3.2 * pulse, color=lin("#ffc070"), alpha=0.22 * k, kind="soft",
                        lod=False, dof=0.3))
        shell = p + self.d * (0.25 + 0.8 * self.s[:, :1]) * (1.0 + 0.3 * np.sin(t * 3.0 + 6.0 * self.s[:, 1:2]))
        out.append(dict(pos=shell, size=0.04, color=lin("#ffe2a0"), alpha=0.7 * k, emit=2.0, kind="spark",
                        twinkle=0.8, seed=self.s[:, 2]))
        return out

    def sample(self, t):
        out = []
        # 1: the first grain, warmed and sent
        if t < 16.0:
            if t < self.T_LET:
                p = GRAIN + _v(0.0, 0.12 * np.sin(t * 0.9), 0.0)
            else:
                u = min((t - self.T_LET) / (self.T_LAND - self.T_LET), 1.0)
                p = GRAIN * (1.0 - u * u) + _v(GRAIN[0], 0.02, GRAIN[2]) * (u * u)
            warm = _sc(0.5, 8.0, t)
            k = 1.0 - 0.85 * _sc(self.T_LAND, 15.5, t)
            out += self._one(p, k, warm, t)
            # the horizon star's halo that holds it (a warm ring of light round the grain, a slow heartbeat)
            h = _win(0.5, 2.5, 8.6, self.T_LET + 0.4, t)
            if h > 0.0:
                beat = 1.0 + 0.10 * np.sin(t * 2 * np.pi / 1.4)
                a = np.linspace(0.0, 2 * np.pi, 220, endpoint=False)
                ring = GRAIN + np.stack([np.cos(a), np.sin(a), 0.0 * a], axis=1) * 1.9 * beat
                out.append(dict(pos=ring, size=0.10, color=lin("#ffb860"), alpha=0.5 * h, emit=1.5, kind="spark",
                                twinkle=0.4))
        # 2: the second grain onto the dry ground of the wilderness
        if self.T2_LET - 0.5 < t < 75.0:
            u = min(max((t - self.T2_LET) / (self.T2_LAND - self.T2_LET), 0.0), 1.0)
            p = (SPRING + _v(0.0, 9.0, 0.0)) * (1.0 - u * u) + (SPRING + _v(0.0, 0.05, 0.0)) * (u * u)
            k = _sc(self.T2_LET - 0.5, self.T2_LET, t) * (1.0 - 0.8 * _sc(self.T2_LAND, 74.0, t))
            out += self._one(p, k, 1.0, t)
        # 3: one ripe grain in the calm hold, exactly where the first fell
        if self.T3_LET - 0.6 < t:
            u = min(max((t - self.T3_LET) / (self.T3_LAND - self.T3_LET), 0.0), 1.0)
            u = u * u * (3.0 - 2.0 * u)
            top = GRAIN + _v(0.0, -1.2, 0.0)
            p = top * (1.0 - u) + _v(GRAIN[0], 0.02, GRAIN[2]) * u
            k = _sc(self.T3_LET - 0.6, self.T3_LET, t) * (1.0 - 0.75 * _sc(self.T3_LAND, self.T3_LAND + 4.0, t))
            out += self._one(p, 0.8 * k, 1.0, t)
        return out or None


class Rings:
    """Rings of light on the still water: one perfect ring when a grain lands, rings from people's feet."""

    def __init__(self):
        self.rings = [
            (Grain.T_LAND, GRAIN[0], GRAIN[2], 2.6, 9.0, 1.0),      # the first grain: one ring to every shore
            (Grain.T_LAND + 2.2, GRAIN[0], GRAIN[2], 1.6, 6.0, 0.45),
            (28.2, FAM[0] - 0.5, FAM[2] + 0.4, 0.6, 2.6, 0.28),      # golden rings from the family's feet
            (29.0, FAM[0] + 0.5, FAM[2] + 0.5, 0.6, 2.6, 0.28),
            (29.8, FAM[0] + 0.1, FAM[2] + 0.6, 0.6, 2.6, 0.28),
            (Grain.T3_LAND, GRAIN[0], GRAIN[2], 0.9, 12.0, 0.9),    # the last grain: one slow, widening ring
        ]
        n = 720
        self.a = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
        self.j = np.random.default_rng(5).random(n)

    def sample(self, t):
        out = []
        for t0, x, z, speed, life, k in self.rings:
            age = t - t0
            if age < 0.0 or age > life:
                continue
            r = 0.15 + speed * age * (1.0 - 0.25 * age / life)
            a = k * (1.0 - age / life) ** 1.5 * _sc(0.0, 0.15, age)
            pos = np.stack([x + r * np.cos(self.a), 0.03 + 0.0 * self.a, z + r * np.sin(self.a)], axis=1)
            out.append(dict(pos=pos, size=0.06 + 0.012 * r, color=lin("#ffcf80"), alpha=a * (0.7 + 0.3 * self.j),
                            emit=1.4, kind="spark", twinkle=0.3, seed=self.j, reflect=False))
        return out or None


def _branches(rng, root, n_br, steps, step, spread, y=0.02):
    """A network of fine branching lines from root (for roots on the lake bed and cracks in dry ground):
    returns points (N, 3) and their distance along the network from the root."""
    pts, dist = [], []
    stack = [(np.asarray(root, np.float64), rng.random() * 2 * np.pi, 0.0, steps)]
    count = 0
    while stack and count < n_br:
        p, a, d0, left = stack.pop()
        count += 1
        for s in range(left):
            a += rng.normal() * 0.35
            p = p + step * _v(np.cos(a), 0.0, np.sin(a))
            d0 += step
            pts.append(_v(p[0], y, p[2]))
            dist.append(d0)
            if rng.random() < spread and left - s > 6:
                stack.append((p.copy(), a + rng.choice([-1, 1]) * (0.5 + 0.5 * rng.random()), d0, left - s - 3))
        if not stack and count < n_br:
            stack.append((np.asarray(root, np.float64), rng.random() * 2 * np.pi, 0.0, steps))
    return np.array(pts), np.array(dist)


class Roots:
    """The grain's last light breaks open into fine gold roots on the lake bed, racing outward like slow
    lightning until the lake floor glows like a map of veins; they fade as the field rises from them."""

    def __init__(self):
        rng = np.random.default_rng(71)
        p, d = _branches(rng, (GRAIN[0], 0.0, GRAIN[2]), 70, 70, 0.55, 0.10, y=0.015)
        # fill the lines densely
        self.pos = p + rng.normal(size=p.shape) * _v(0.05, 0.0, 0.05)
        self.d = d
        self.s = rng.random(len(p))

    def sample(self, t):
        if t < Grain.T_LAND + 0.8 or t > 58.0:
            return None
        front = 7.0 * (t - Grain.T_LAND - 1.0)
        lit = _ss(-1.0, 0.0, front - self.d) * (1.0 + 1.6 * np.exp(-np.maximum(front - self.d, 0.0) / 1.5))
        k = 1.0 - _sc(44.0, 56.0, t)
        return dict(pos=self.pos, size=0.07, color=lin("#ffb64a"), alpha=0.55 * lit * k, emit=1.3, kind="spark",
                    twinkle=0.35, seed=self.s, reflect=False)


class Wheat:
    """The sea of golden wheat made of light: every head of grain a tiny lamp. It rises from the roots in
    waves on the strong beats of the first refrain, sways with the music, bows and rises like a breath at
    the peaks, bends where the fragrance passes, and barely sways in the calm hold."""

    def __init__(self, n=5200):
        r = np.random.default_rng(81)
        xs, zs = [], []
        while len(xs) < n:
            x = (r.random() * 2.0 - 1.0) * 120.0
            z = 25.0 - r.random() * 250.0
            # the lake stays open in the middle (and the near water in front of the camera is calm)
            half = 7.0 + 0.10 * max(-z, 0.0)
            if abs(x) < half and z > -170.0:
                continue
            if z > -45.0:
                continue
            if abs(x - WILD[0]) < 26.0 and abs(z - WILD[2]) < 24.0:
                continue
            xs.append(x)
            zs.append(z)
        # a near band of tall wheat behind the narrow path and the water's edge
        m = 700
        px = (r.random(m) * 2.0 - 1.0) * 14.0
        pz = PATH[2] - 2.4 - r.random(m) * 7.0
        xs = np.concatenate([np.array(xs), px])
        zs = np.concatenate([np.array(zs), pz])
        self.base = np.stack([xs, np.zeros_like(xs), zs], axis=1)
        self.n = len(xs)
        self.near = np.zeros(self.n, bool)
        self.near[-m:] = True
        self.h = 0.9 + 0.6 * r.random(self.n)
        self.h[self.near] = 1.25 + 0.35 * r.random(m)
        self.s = r.random((self.n, 4))
        self.dist = np.hypot(xs - GRAIN[0], zs - GRAIN[2])
        self.k = 9                                                     # points per stalk

    def grow(self, t):
        g = _ss(REFRAIN1 - 0.5 + self.dist / 40.0, REFRAIN1 + 2.5 + self.dist / 40.0, t)
        g = np.where(self.near, _sc(66.0, 69.5, t), g)
        return g

    def sample(self, t):
        if t < REFRAIN1 - 0.6:
            return None
        g = self.grow(t)
        on = g > 0.01
        if not np.any(on):
            return None
        b = self.base[on]
        s = self.s[on]
        h = self.h[on] * g[on]
        dist = self.dist[on]
        # wind: a slow swell, the beat, the breath at the peaks, the fragrance wind, stillness in the hush
        still = 1.0 - 0.85 * _win(81.5, 83.0, 92.8, 94.2, t)
        calm = 1.0 - 0.6 * _sc(LAST_NOTE, LAST_NOTE + 6.0, t)
        sway = 0.10 * np.sin(0.8 * t + 0.05 * b[:, 0] + 0.03 * b[:, 2] + 6.0 * s[:, 0]) * still * calm
        wave = np.zeros(len(b))
        for tb in DOWNBEATS[(DOWNBEATS > t - 3.0) & (DOWNBEATS <= t)]:
            if REFRAIN1 <= tb <= 67.0 or REFRAIN2 <= tb <= LAST_NOTE:
                front = (t - tb) * 30.0
                wave += np.exp(-((dist - front) / 7.0) ** 2) * np.exp(-(t - tb) / 1.6)
        bow = 0.0
        for tp in (PEAK1, PEAK2):
            bow += 0.35 * np.exp(-((t - tp - 0.6) / 0.8) ** 2)
        fr = _win(101.0, 102.5, 107.5, 109.0, t)
        frag = fr * 0.45 * np.exp(-((b[:, 0] - (-90.0 + 22.0 * (t - 101.0))) / 14.0) ** 2)
        lean = sway + 0.12 * wave + bow + frag
        u = np.linspace(0.0, 1.0, self.k)
        # stalk points from the root to below the head, bending with the lean
        x = b[:, None, 0] + (lean * h)[:, None] * u[None, :] ** 2
        y = h[:, None] * u[None, :] * (1.0 - 0.15 * (lean ** 2)[:, None])
        z = b[:, None, 2] + 0.0 * u[None, :]
        stem = np.stack([x, y, z], axis=2).reshape(-1, 3)
        head = np.stack([x[:, -1], y[:, -1] + 0.05, z[:, -1]], axis=1)
        sun = 0.75 + 0.35 * _sc(REFRAIN2, REFRAIN2 + 4.0, t) - 0.6 * _win(68.0, 71.0, 94.0, 97.0, t)
        glow = sun * (1.0 + 0.9 * wave + 0.6 * frag / 0.45)
        near = self.near[on]
        glow = np.where(near, glow * 0.32 * (1.0 - _sc(95.0, 98.0, t)), glow)
        stem_col = lin("#e8b860")
        head_col = lin("#ffd27a") * (1.0 - 0.35 * fr) + lin("#f4b6a6") * (0.35 * fr)
        sa = ((0.32 * glow)[:, None] * (0.35 + 0.65 * u[None, :])).reshape(-1)
        out = [dict(pos=stem, size=0.035, color=stem_col, alpha=sa, emit=1.0, kind="soft", backlight=0.6),
               dict(pos=head, size=0.11, color=head_col, alpha=np.minimum(0.85 * glow, 1.6), emit=1.6,
                    kind="spark", twinkle=0.35, seed=s[:, 1], backlight=0.8)]
        return out


class Homes:
    """The plain beyond the mountains: homes, schools and workshops drawn as faint windows, waiting in the long
    shadow. A beam from the horizon star touches the town and the windows light one by one, then the light
    rolls out to the horizon like embers in the dusk."""

    T_BEAM = 39.0
    T_LIGHT = 41.4

    def __init__(self, n=3600):
        r = np.random.default_rng(91)
        cx = (r.random(n // 3) * 2.0 - 1.0) * 260.0
        cz = -150.0 - r.random(n // 3) * 260.0
        house = np.repeat(np.arange(n // 3), 3)
        self.pos = np.stack([cx[house] + r.normal(size=len(house)) * 1.4,
                             0.4 + 2.2 * r.random(len(house)),
                             cz[house] + r.normal(size=len(house)) * 1.4], axis=1)
        self.wake = self.T_LIGHT + np.hypot(self.pos[:, 0] - 10.0, self.pos[:, 2] + 230.0) / 45.0 \
            + 0.8 * r.random(len(house))
        self.s = r.random(len(house))

    def sample(self, t):
        if t < 30.0:
            return None
        age = t - self.wake
        lit = _ss(0.0, 0.6, age)
        come = _sc(30.0, 33.0, t)
        col = lin("#8a5a44") * (1.0 - lit)[:, None] + lin("#ffc066")[None, :] * lit[:, None]
        al = come * (0.5 + 0.5 * lit) * (1.0 + 1.2 * np.exp(-np.maximum(age, 0.0) / 0.8) * (age > 0))
        return dict(pos=self.pos, size=0.9 + 0.5 * self.s, color=col, alpha=al, emit=1.0 + 1.2 * lit,
                    kind="spark", twinkle=0.25, seed=self.s)


class Beam:
    """A single beam of the horizon star's light falling across the dark plain like a long shaft of morning
    through a door (the dark world), and the rivers of light that pour into the wilderness (living water)."""

    def sample(self, t):
        out = []
        k = _win(Homes.T_BEAM - 1.0, Homes.T_BEAM + 1.0, 47.0, 51.0, t)
        if k > 0.0:
            a = np.linspace(0.0, 1.0, 60)
            p0, p1 = _v(0.0, 60.0, -1200.0), _v(10.0, 0.0, -230.0)
            pts = p0[None, :] * (1.0 - a[:, None]) + p1[None, :] * a[:, None]
            from p3d.api import ribbon
            out.append(ribbon(pts, width=18.0 * (0.4 + 0.6 * a), color=lin("#ffc070"), alpha=0.18 * k * a,
                              emit=1.0))
        return out or None


class Wilderness:
    """A dry wilderness of cracked umber ground and bare branches in the hills' shadow. The second grain
    wakes it; then the horizon star's light pours in as rivers of liquid gold that fill every crack like the
    veins of a leaf; green gold shoots push up along each stream, a spring wells up, blossoms open."""

    T_WATER = 94.6

    def __init__(self):
        r = np.random.default_rng(101)
        p, d = _branches(r, (SPRING[0], 0.0, SPRING[2]), 60, 48, 0.75, 0.16, y=0.03)
        p += r.normal(size=p.shape) * _v(0.06, 0.0, 0.06)
        keep = (np.abs(p[:, 0] - WILD[0]) < 26.0) & (np.abs(p[:, 2] - WILD[2]) < 24.0)
        self.pos, self.d = p[keep], d[keep]
        self.s = r.random(len(self.pos))
        n = 9000
        self.ground = np.stack([WILD[0] + (r.random(n) * 2 - 1) * 26.0, 0.02 + 0.0 * r.random(n),
                                WILD[2] + (r.random(n) * 2 - 1) * 24.0], axis=1)
        self.gs = r.random(n)
        pick = r.choice(len(self.pos), 900)
        self.shoot = self.pos[pick]
        self.shd = self.d[pick]
        self.shs = r.random(900)
        self.fs = r.random((160, 3))

    def sample(self, t):
        if t < 60.0:
            return None
        come = _sc(60.0, 63.0, t) * (1.0 - 0.55 * _sc(106.0, 112.0, t))
        wake = _sc(Grain.T2_LAND, Grain.T2_LAND + 3.0, t)
        front = 6.0 * (t - self.T_WATER)
        lit = _ss(-1.5, 0.0, front - self.d)
        out = [dict(pos=self.ground, size=0.22, color=lin("#7a5236") * (1.0 + 0.6 * wake), alpha=0.22 * come,
                    kind="soft", seed=self.gs, twinkle=0.1)]
        crack = lin("#8a5a32") * (1.0 - lit)[:, None] + lin("#ffcc66")[None, :] * lit[:, None]
        out.append(dict(pos=self.pos, size=0.10 + 0.06 * lit, color=crack,
                        alpha=come * (0.25 + 0.25 * wake + 0.6 * lit), emit=1.0 + 1.5 * lit, kind="spark",
                        twinkle=0.3, seed=self.s))
        g = _ss(0.0, 2.5, (t - self.T_WATER - 1.5) - self.shd / 6.0)
        if np.any(g > 0.01):
            tip = self.shoot + _v(0.0, 1.0, 0.0) * (0.2 + 0.9 * self.shs * g)[:, None]
            out.append(dict(pos=tip, size=0.08, color=lin("#c9d77a"), alpha=0.8 * g, emit=1.3, kind="spark",
                            twinkle=0.4, seed=self.shs))
            bl = _ss(101.0, 104.0, t + 2.0 * self.shs)
            out.append(dict(pos=tip + _v(0.0, 0.15, 0.0), size=0.22, color=lin("#f4b6a6") * 0.7 + lin("#fff2dc") * 0.3,
                            alpha=0.75 * bl * g, emit=1.4, kind="soft", seed=self.shs))
        sp = _sc(self.T_WATER, self.T_WATER + 2.0, t)
        if sp > 0.0:
            a = self.fs
            ph = (t * 0.55 + a[:, 1]) % 1.0                       # each drop rises and falls smoothly, forever
            h = 1.6 * np.sin(np.pi * ph) ** 0.8
            fount = SPRING + np.stack([(a[:, 0] - 0.5) * 0.8 * (0.3 + ph), h, (a[:, 2] - 0.5) * 0.8 * (0.3 + ph)],
                                      axis=1)
            out.append(dict(pos=fount, size=0.06, color=lin("#ffe2a0"), alpha=0.7 * sp, emit=2.0, kind="spark"))
        return out


class Fragrance:
    """A warm rose gold wind of fragrance crossing the field (the wheat bends in its path)."""

    def __init__(self, n=2600):
        r = np.random.default_rng(111)
        self.s = r.random((n, 4))

    def sample(self, t):
        k = _win(100.6, 102.0, 107.8, 109.4, t)
        if k <= 0.0:
            return None
        s = self.s
        x = -90.0 + 22.0 * (t - 101.0) + (s[:, 0] - 0.5) * 40.0
        z = -20.0 - 150.0 * s[:, 1]
        y = 0.8 + 3.5 * s[:, 2] + 0.6 * np.sin(t * 1.3 + 9.0 * s[:, 3])
        pos = np.stack([x + 2.0 * np.sin(t + 7.0 * s[:, 3]), y, z], axis=1)
        return dict(pos=pos, size=0.12 + 0.12 * s[:, 3], color=lin("#f4b6a6"), alpha=0.55 * k, emit=1.3,
                    kind="soft", twinkle=0.5, seed=s[:, 3])


class Lamps:
    """Lanterns: the dark lantern dropped in the water and relit; the small lantern of the near shore that
    glows a little brighter than the rest in the calm hold (it becomes song 07's lone traveller's light)."""

    def sample(self, t):
        out = []
        # the family's lantern at the water's edge: dark on the water, relit from the older one's lantern
        if 80.6 < t < 98.0:
            relit = _sc(87.4, 88.2, t)
            b = BODIES.get("young")
            if t < 88.6:
                p = SHORE + _v(0.05, 0.10 + 0.03 * np.sin(t * 1.4), 0.75)
            else:
                hand = np.asarray(b.where(t, "palm.R"), np.float64) if b is not None else SHORE + _v(0, 1.0, 0.4)
                u = _sc(88.6, 89.6, t)
                p = (SHORE + _v(0.05, 0.10, 0.75)) * (1.0 - u) + (hand + _v(0.0, 0.06, 0.0)) * u
            k = _win(80.6, 81.6, 96.0, 98.0, t)
            col = lin("#5a3a2b") * (1.0 - relit) + lin("#ffb850") * relit
            out.append(dict(pos=p[None, :], size=0.09 + 0.05 * relit, color=col, alpha=k * (0.5 + 0.5 * relit),
                            emit=1.0 + 3.0 * relit, kind="spark", lod=False))
            if relit > 0.0:
                out.append(dict(pos=p[None, :], size=0.9, color=lin("#ffb048"), alpha=0.25 * relit * k, kind="soft",
                                lod=False))
            # the older one's own lantern, tipped so the flame passes across
            o = BODIES.get("older")
            if o is not None:
                hand = np.asarray(o.where(t, "palm.L"), np.float64) + _v(0.0, 0.05, 0.0)
                out.append(dict(pos=hand[None, :], size=0.10, color=lin("#ffc060"), alpha=k, emit=3.5, kind="spark",
                                lod=False))
                out.append(dict(pos=hand[None, :], size=0.8, color=lin("#ffb048"), alpha=0.22 * k, kind="soft",
                                lod=False))
        # the small lantern on the near shore (the hand-off)
        k = _sc(126.0, 132.0, t)
        if k > 0.0:
            flick = 1.0 + 0.06 * np.sin(t * 5.1) + 0.04 * np.sin(t * 8.3)
            out.append(dict(pos=(LAMP + _v(0.0, 0.35, 0.0))[None, :], size=0.10 * flick, color=lin("#ffc060"),
                            alpha=k, emit=4.0, kind="spark", lod=False))
            out.append(dict(pos=(LAMP + _v(0.0, 0.35, 0.0))[None, :], size=1.1, color=lin("#ffb048"),
                            alpha=0.25 * k, kind="soft", lod=False))
        return out or None


class Bread:
    """The loaf of light the older one breaks and shares (the fragment "Love one another")."""

    def sample(self, t):
        if not (17.5 < t < 31.0):
            return None
        o = BODIES.get("mother")
        if o is None:
            return None
        k = _win(17.5, 18.6, 29.0, 31.0, t)
        pl, pr = np.asarray(o.where(t, "palm.L"), np.float64), np.asarray(o.where(t, "palm.R"), np.float64)
        mid = 0.5 * (pl + pr) + _v(0.0, 0.06, 0.0)
        out = [dict(pos=mid[None, :], size=0.6, color=lin("#ffc878"), alpha=0.3 * k * (1.0 - _sc(23.0, 25.0, t)),
                    kind="soft", lod=False)]
        # three pieces of light passed to the young one and the child, then glowing inside them
        for name, t0, w in (("daughter", 21.6, 0.0), ("child", 22.6, 1.0)):
            b = BODIES.get(name)
            if b is None:
                continue
            u = _sc(t0, t0 + 1.2, t)
            dest = np.asarray(b.where(t, "heart"), np.float64)
            p = mid * (1.0 - u) + dest * u + _v(0.0, 0.25 * np.sin(np.pi * u), 0.0)
            kk = k * (1.0 - 0.7 * _sc(t0 + 1.2, t0 + 3.0, t))
            out.append(dict(pos=p[None, :], size=0.09, color=lin("#ffd890"), alpha=kk, emit=3.0, kind="spark",
                            lod=False))
        return out


# ---------------------------------------------------------------------------------------------------------
# People of light: warm gold glitter people, whole and radiant, no faces. Touch only between two people of
# the same gender, or parent and child.
# ---------------------------------------------------------------------------------------------------------
BODIES = {}
HURRY_X0, ELDER_X0, OLDER_X0 = -6.46, 3.56, 2.0
# the approved Revision 3 people: Claude Final v1's bodies and refined acting (master_acting), warm gold glitter
_GOLDS = (("#ffb648", "#ffe6b0"), ("#f29a34", "#ffd48a"))


def _gold(k=0, seams=True, **kw):
    c1, c2 = _GOLDS[k % 2]
    d = dict(look=dict(name="glitter", seams=0.6) if seams else "glitter", color=c1, color2=c2, bright=2.1)
    d.update(kw)
    return d


def _bodies():
    if BODIES:
        return BODIES
    importlib.import_module("nine_reference_p3d.master_acting")
    Body = importlib.import_module("nine_reference_p3d.body").Body
    w = (0.2, 0.0, -0.1)
    # verse 1, line 2: a mother, her grown daughter and a small child, as at a family table, sharing bread
    mother = Body("woman", at=(FAM[0], FAM[2]), facing=160.0, motion="stand", garment="robe", veil=True,
                  stoop=0.12, points=70000, show=(17.0, 33.0), fade=0.8, wind=w, seed=21.0,
                  gesture=[(18.6, 21.6, "cup"), (21.6, 23.8, "offer", dict(side="R")),
                           (25.0, 31.0, "arm_round", dict(side="L", to=lambda t: _child_where(t, "blade.R")))], **_gold(0))
    BODIES["mother"] = mother
    daughter = Body("woman", at=(FAM[0] + 1.0, FAM[2] + 0.3), facing=225.0, motion="stand", garment="dress",
                    points=65000, show=(17.4, 33.0), fade=0.8, wind=w, seed=22.0,
                    gesture=[(21.8, 24.6, "offer", dict(side="L")), (25.0, 31.0, "hand_on_heart", dict(side="R"))], **_gold(1))
    BODIES["daughter"] = daughter
    child = Body("child", at=(FAM[0] - 0.62, FAM[2] + 0.42), facing=120.0, motion="stand", garment="tunic",
                 points=45000, show=(17.8, 33.0), fade=0.8, wind=w, seed=23.0,
                 gesture=[(22.8, 25.0, "offer", dict(side="R")),
                          (25.2, 31.0, "look_to", dict(to=lambda t: BODIES["mother"].where(min(t, 25.0), "head")))], **_gold(0))
    BODIES["child"] = child
    # verse 2, line 1: "Please, after you." Someone in a hurry on the narrow path stops short, takes one long
    # breath, steps aside toward the wheat and opens a hand toward the way; an elder passes, bowing in thanks
    hx = PATH[0]
    # the walk carries a figure forward by itself: `at` keys stay still while walking and only move for
    # the step aside (HURRY_X0 and ELDER_X0 are set from the measured walk lengths)
    hurry = Body("man", at=[(68.4, (HURRY_X0, PATH[2])), (73.9, (HURRY_X0, PATH[2])),
                            (75.0, (HURRY_X0 - 0.15, PATH[2] - 0.8))],
                 facing=[(68.4, 90.0), (73.8, 90.0), (75.0, 120.0), (79.8, 120.0), (80.6, 90.0)],
                 motion=[(68.4, "walk", dict(speed=1.3)), (72.0, "stand"), (73.9, "shuffle"), (75.1, "stand"),
                         (80.2, "walk", dict(speed=0.8))],
                 gesture=[(72.0, 73.9, "hand_on_heart", dict(side="L")),
                          (75.1, 79.9, "after_you", dict(side="R", to=(hx - 0.35, 0.95, PATH[2] + 0.15)))],
                 garment="tunic", points=70000, show=(68.2, 82.6), fade=0.8, wind=w, seed=31.0, **_gold(1))
    BODIES["hurry"] = hurry
    elder = Body("man", at=(ELDER_X0, PATH[2] + 0.15),
                 facing=[(69.4, 270.0), (TOTAL, 270.0)],
                 motion=[(69.4, "walk", dict(speed=0.7)), (72.4, "stand"), (75.6, "walk", dict(speed=0.6))],
                 gesture=[(76.6, 79.2, "greet_bow", dict(amount=18.0, hold=0.8))], stoop=0.5, garment="robe",
                 points=65000, show=(69.2, 82.2), fade=0.8, wind=w, seed=32.0, **_gold(0))
    BODIES["elder"] = elder
    # verse 2, lines 2 and 3: "It's okay. I understand." Two women: the young one kneels at the water's edge,
    # head bowed, the lantern dark on the water; the older one kneels at her level, a hand on her shoulder,
    # relights the lantern, places it back in her hands, helps her up; they embrace
    yx0, yx1 = SHORE[0] - 0.42, SHORE[0] - 0.24
    ox0, ox1 = SHORE[0] + 0.40, SHORE[0] + 0.24
    young = Body("woman", at=[(80.0, (yx0, SHORE[2])), (89.4, (yx0, SHORE[2])), (90.2, (yx1, SHORE[2]))],
                 facing=[(80.0, 150.0), (88.6, 150.0), (89.8, 92.0)],
                 motion=[(80.0, "kneel"), (88.4, "rise", dict(dur=1.4)), (89.8, "stand")],
                 gesture=[(80.0, 85.2, "bow"), (85.2, 88.4, "look_to", dict(to=(ox0, 1.0, SHORE[2]))),
                          (90.2, 94.8, "embrace", dict(to=(ox1 + 0.06, 1.18, SHORE[2] + 0.14),
                                                       to2=(ox1 + 0.06, 1.18, SHORE[2] - 0.20)))],
                 garment="dress", points=75000, show=(81.0, 95.6), fade=1.0, wind=w, seed=41.0, **_gold(1))
    BODIES["young"] = young
    older = Body("woman", at=[(81.4, (OLDER_X0, SHORE[2] - 0.05)), (89.4, (OLDER_X0, SHORE[2] - 0.05)),
                              (90.2, (OLDER_X0 - 0.16, SHORE[2] - 0.03))],
                 facing=[(81.4, 270.0), (89.8, 270.0)],
                 motion=[(81.4, "walk", dict(speed=0.6)), (83.4, "kneel"), (88.4, "rise", dict(dur=1.4)),
                         (89.8, "stand")],
                 gesture=[(84.0, 86.8, "comfort", dict(side="R", to=lambda t: BODIES["young"].where(t, "shoulder.L"))),
                          (86.6, 88.6, "offer", dict(side="L")),
                          (90.2, 94.8, "embrace", dict(to=lambda t: BODIES["young"].where(t, "blade.R"),
                                                       to2=lambda t: BODIES["young"].where(t, "blade.L")))],
                 garment="robe", veil=True, stoop=0.1, points=75000, show=(81.2, 95.6), fade=1.0, wind=w,
                 seed=42.0, **_gold(0))
    BODIES["older"] = older
    # the refrains: a few people of light among the wheat, small and unhurried; in the final refrain the
    # pairs walk together (no touching here)
    walkers = [("woman", -9.0, -58.0, 41.0, 52.0, 66.5), ("child", -8.2, -58.4, 42.0, 52.0, 66.5),
               ("man", 10.0, -64.0, 43.0, 53.0, 66.5), ("man", 11.0, -64.5, 44.0, 53.0, 66.5),
               ("woman", -9.0, -62.0, 51.0, 112.0, 131.0), ("woman", -8.0, -61.6, 52.0, 112.0, 131.0),
               ("man", 10.0, -66.0, 53.0, 113.0, 131.0), ("man", 11.1, -66.2, 54.0, 113.0, 131.0)]
    for i, (shape, x, z, seed, t0, t1) in enumerate(walkers):
        b = Body(shape, at=[(t0, (x, z)), (t1, (x * 0.6, z - 0.8 * (t1 - t0)))],
                 facing=180.0 + (8.0 if x < 0 else -8.0), motion=[(t0, "walk", dict(speed=0.5))],
                 garment=("robe" if shape == "woman" else "tunic"), points=18000, show=(t0, t1), fade=1.2,
                 seed=seed, **_gold(i, seams=False))
        BODIES["walker%d" % i] = b
    return BODIES


def _child_where(t, place):
    return BODIES["child"].where(t, place)


class Calm:
    """The calm bottom third (DESIGN-SYSTEM 10, rule 9): the performers stand in front of it, so every point of
    light fades as it nears the bottom of the picture (to 12 percent below 0.24 of the height). Pure function of
    t and the camera, like the approved expressions.Clear."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None or cam is None:
            return got
        # nothing competes inside a reading box: the words' boxes (with a margin), as expressions.Clear does
        # (fix 1) and, while a word reads, the whole row of lights just under its box (the horizon band of
        # grain lights) sinks to faint across the full width, eased in and out, so nothing bright touches the
        # lower edge of the words
        boxes, rows = [], []
        for word in WORDS:
            if word.t_in - 0.6 <= t <= word.t_out + 0.6:
                x0, x1, y0, y1, front, *_ = PW.screen_box(word, cam, min(max(t, word.t_in), word.t_out))
                if not front:
                    continue
                if word.t_in <= t <= word.t_out:
                    boxes.append((x0 - 0.03, x1 + 0.03, y0 - 0.045, y1 + 0.045))
                env = _ss(word.t_in - 0.6, word.t_in + 0.4, t) * (1.0 - _ss(word.t_out - 0.4, word.t_out + 0.6, t))
                rows.append((y0, env))
        out = []
        for source in got if isinstance(got, (list, tuple)) else [got]:
            if source is None or source.get("pos") is None:
                out.append(source)
                continue
            b = dict(source)
            p = np.asarray(b["pos"], np.float64).reshape(-1, 3)
            xy, z = cam.project(p)
            # (fix 1) the bottom third is calm water only: every light is gone below 0.345 of the height (from
            # the bottom) and fades in by 0.42
            g = _ss(0.345, 0.42, xy[:, 1])
            for y0, env in rows:
                row = _ss(y0 - 0.13, y0 - 0.06, xy[:, 1]) * (1.0 - _ss(y0 + 0.01, y0 + 0.05, xy[:, 1]))
                g = g * (1.0 - 0.85 * env * row)
            for x0, x1, y0, y1 in boxes:
                dx = np.minimum(xy[:, 0] - x0, x1 - xy[:, 0])
                dy = np.minimum(xy[:, 1] - y0, y1 - xy[:, 1])
                g = g * (1.0 - 0.97 * np.clip(np.minimum(dx, dy) / 0.02 + 0.5, 0.0, 1.0))
            g = np.where(z > 0, g, 1.0)
            b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * g
            out.append(b)
        return out


class Flight:
    """Each expression's words, once read, go into the arch: as the letters fade, one spark of the expression's
    colour (with a short trail) rises from the words to its star, arriving as the star lights or flares."""

    def __init__(self):
        self.legs = [("Concession", 4, CONC["t_read1"] + 0.1, STAR5_T), ("Inclusiveness", 3, INCL["t_read1"] + 0.1,
                                                                          STAR4_T)]

    def sample(self, t):
        out = []
        for name, i, t0, t1 in self.legs:
            if not (t0 - 0.05 < t < t1 + 0.3):
                continue
            a = place(t0, 0.5, WORD_Y, WORD_DEPTH)
            b = np.asarray(star_point(i, t1), np.float64)
            col = lin(COL[name])
            us = np.clip((t - t0 - np.linspace(0.0, 0.35, 14)) / (t1 - t0), 0.0, 1.0)
            us = us * us * (3.0 - 2.0 * us)
            lift = np.sin(np.pi * us)[:, None] * _v(0.0, 6.0, 0.0)[None, :]
            pts = a[None, :] * (1.0 - us[:, None]) + b[None, :] * us[:, None] + lift
            k = _sc(t0 - 0.05, t0 + 0.25, t) * (1.0 - _sc(t1, t1 + 0.3, t))
            fall = np.linspace(1.0, 0.1, 14)
            out.append(dict(pos=pts, size=0.18 + 0.6 * us, color=col, alpha=k * fall, emit=3.0, kind="spark",
                            lod=False, streak=0.0))
        return out or None


class HeartSparks:
    """brand_hearts.HeartDrift draws kind="heart", which the pinned Film 10 engine does not have. This draws each
    heart as its outline in fine sparks (36 points) plus a soft glow, flat to the picture, in the same colour,
    place, size, sway and fade."""
    wants_camera = True

    def __init__(self, inner, n=36):
        from p3d import brand_hearts as BH
        self.inner = inner
        self.hp = BH.heart_points(n)
        self.hp = self.hp - self.hp.mean(axis=0)

    def gain(self, t):
        return self.inner.gain(t)

    def sample(self, t, cam=None):
        got = self.inner.sample(t)
        if not got or cam is None:
            return None
        r, u, _ = cam.basis()
        out = []
        for b in got:
            if b.get("kind") != "heart":
                out.append(b)
                continue
            pos = np.asarray(b["pos"], np.float64)
            size = np.asarray(b["size"], np.float64)
            m = len(self.hp)
            off = self.hp[None, :, 0:1] * r[None, None, :] + self.hp[None, :, 1:2] * u[None, None, :]
            pts = (pos[:, None, :] + off * size[:, None, None]).reshape(-1, 3)
            col = np.asarray(b["color"], np.float64)
            col = np.repeat(col, m, axis=0) if col.ndim == 2 else col
            al = np.repeat(np.asarray(b["alpha"], np.float64), m)
            out.append(dict(pos=pts, size=np.repeat(size * 0.07, m), color=col, alpha=al, emit=2.2, kind="spark",
                            twinkle=0.2, seed=np.repeat(np.asarray(b.get("seed", 0.5)), m) if np.ndim(b.get("seed", 0.5))
                            else 0.5, dof=0.6))
        return out or None


_CALM_SKIP = ("_stars", "_sun", "_arch")


def _setup(scene):
    scene.add("grain", Grain())
    scene.add("rings", Rings(), reflect=False)
    scene.add("roots", Roots(), reflect=False)
    scene.add("homes", Homes())
    scene.add("beam", Beam(), reflect=False)
    scene.add("wilderness", Wilderness())
    scene.add("wheat", Wheat(), reflect=False)
    scene.add("fragrance", Fragrance())
    b = _bodies()
    for name, body in b.items():
        body.add(scene, name, reflect=False)     # no bright reflections of people in the bottom third
    scene.add("lamps", Lamps(), reflect=False)
    scene.add("bread", Bread(), reflect=False)
    WORDS.add_to(scene, reflect=False)
    # each expression's symbol, IN the world, subtle, in its colour, around its moment (never over the words):
    # Concession as a passing drift of embers over the wheat to the right of the path; Inclusiveness as petals
    # that settle into its shape for a moment beside the two women, then blow on (PHASEB 9.4)
    from p3d import brand  # noqa: F401  (brand first: it pulls in brand_symbols)
    from p3d import brand_symbols as BS, brand_hearts as BH
    scene.add("sym_concession", BS.Flock("Concession", carrier="ember", heading=(1.0, 0.12), travel=2.0,
                                         ride=(0.80, 0.47, 9.0), frac=0.15, camera=_LAYOUT, t0=74.6, dur=3.0,
                                         intensity=0.45, reflect=False), reflect=False)
    scene.add("sym_inclusiveness", BS.PetalShape("Inclusiveness", wind=(-1.0, 0.1), carrier="petal",
                                                 ride=(0.19, 0.47, 8.0), frac=0.15, camera=_LAYOUT, t0=85.6,
                                                 dur=1.8, hold=2.6, out=1.6, intensity=0.24, reflect=False),
              reflect=False)
    scene.add("flight", Flight(), reflect=False)
    # hearts in the expression colours drift off each expression as its words leave for the arch (PHASEB 9.5)
    # (Concession's are short: they are gone before Inclusiveness forms, 0.2 s after Concession leaves)
    for name, spec, t1, life in (("Concession", CONC, CONC["t_read1"] + 0.6, 1.1),
                                 ("Inclusiveness", INCL, INCL["t_out"] + 0.4, 2.4)):
        src = (lambda t: place(t, 0.5, WORD_Y - 0.03, WORD_DEPTH))
        scene.add("hearts_" + name, HeartSparks(BH.HeartDrift(src, spec["t_read1"] - 0.2, t1, color=name,
                                                   rate=12.0, life=life, rise=0.35, spread=0.9, size=(0.05, 0.11),
                                                   bright=0.9, style="heart", wind=(0.0, 0.05, 0.0), seed=7)),
                  reflect=False)
    # keep the arch's light out of the words while they are read; calm the bottom third for every other light
    from expressions import Clear
    for e in scene.entries():
        if e.name == "_arch":
            e.pointset = Clear(e.pointset, WORDS)
        elif e.name not in _CALM_SKIP and not e.name.startswith(("word ", "hearts_", "flight")) \
                and e.name not in BODIES \
                and not getattr(e.pointset, "static", False):
            e.pointset = Calm(e.pointset)
            e.reflect = False   # (fix 1) no mirror images of lights: they fell into the bottom third


# ---------------------------------------------------------------------------------------------------------
# The world: a long harvest evening (DESIGN-SYSTEM section 6 for song 06). Warm always: never true night.
# ---------------------------------------------------------------------------------------------------------
_HARVEST = dict(base="night", stars=0.0, milky=0.0, clouds=0.42, cloud_speed=0.6, hills=1.0, hill_height=1.0,
                mist=0.25, mist_height=2.0, mirror=1.0, mirror_min=0.5, ripple=0.35, dust=0.85,
                dust_color="#ffd27a", dust_color2="#ff9a3c", bokeh=0.5, sun_disc=7.0, sun_size=1.7,
                lantern_color="#ffb04a", lantern_color2="#e8692a", sun_az=180.0)
LOOKS = dict(
    afternoon=dict(_HARVEST, sky_top="#2b5a98", sky_mid="#6f8ab4", sky_hor="#efd3a0", sun_color="#ffe4b0",
                   sun_int=0.45, sun_el=5.0, sun_glow=0.38, haze=0.4, haze_color="#c8b090", mist_color="#c0a888",
                   hill_color="#3e4058", water="#0c1018", rays=0.2, exposure=0.85),
    harvest=dict(_HARVEST, sky_top="#3e2440", sky_mid="#a2522e", sky_hor="#e8903e", sun_color="#ffaa5a",
                 sun_int=0.6, sun_el=3.5, sun_glow=0.6, haze=0.55, haze_color="#b8683a", mist_color="#a0603c",
                 hill_color="#2e1a22", water="#100707", rays=0.4, exposure=0.85),
    shadow=dict(_HARVEST, sky_top="#301c34", sky_mid="#7c3c2c", sky_hor="#cc6e36", sun_color="#ff9a52",
                sun_int=0.5, sun_el=1.8, sun_glow=0.6, haze=0.5, haze_color="#743a30", mist_color="#643628",
                hill_color="#22141a", water="#0c0506", rays=0.3, dust=0.5, exposure=0.88),
    glow=dict(_HARVEST, sky_top="#44284a", sky_mid="#ae5a30", sky_hor="#ee9a44", sun_color="#ffb464",
              sun_int=0.65, sun_el=4.0, sun_glow=0.65, haze=0.55, haze_color="#c07040", mist_color="#a86a40",
              hill_color="#2e1a22", water="#100707", rays=0.5, dust=0.9, exposure=0.85),
    ember=dict(_HARVEST, sky_top="#2a1626", sky_mid="#5e2a26", sky_hor="#c46430", mirror=0.7, sun_color="#ff9050",
               sun_int=0.5, sun_el=1.6, sun_glow=0.6, haze=0.45, haze_color="#80402e", mist=0.3,
               mist_color="#703a2c", hill_color="#22121a", water="#0c0506", rays=0.25, dust=0.5, exposure=0.9),
    hush=dict(_HARVEST, sky_top="#261420", sky_mid="#562624", sky_hor="#b85c2e", mirror=0.7, sun_color="#ff9050",
              sun_int=0.45, sun_el=1.3, sun_glow=0.6, haze=0.45, haze_color="#743a2c", mist=0.32,
              mist_color="#683428", hill_color="#20101a", water="#0b0506", rays=0.18, dust=0.3, exposure=0.92),
    heaven=dict(_HARVEST, sky_top="#463056", sky_mid="#b4643a", sky_hor="#f0a450", sun_color="#ffc070",
                sun_int=0.6, sun_el=3.5, sun_glow=0.6, haze=0.5, haze_color="#b8743e", mist_color="#b07a50",
                hill_color="#2e1c28", water="#110808", rays=0.55, dust=0.95, exposure=0.85),
    evening=dict(_HARVEST, sky_top="#2e2c58", sky_mid="#984e36", sky_hor="#e08a44", sun_color="#ffa860",
                 sun_int=0.55, sun_el=1.4, sun_glow=0.6, haze=0.5, haze_color="#9a5a40", mist_color="#8a5a42",
                 hill_color="#22162a", water="#0e0708", rays=0.3, dust=0.55, exposure=0.88),
)

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "afternoon"), (2.0, "harvest", 8.0), (31.0, "shadow", 4.0), (41.0, "harvest", 5.0),
          (REFRAIN1, "glow", 4.0), (65.5, "ember", 4.0), (81.0, "hush", 2.5), (93.5, "ember", 2.5),
          (98.0, "harvest", 4.0), (REFRAIN2, "heaven", 4.0), (LAST_NOTE + 1.0, "evening", 9.0)],
    arch=dict(lit=_arch_lit, colors=[PW.COLORS[k] for k in PW.LABELS], span=ARCH["span"], height=ARCH["height"],
              z=ARCH["z"], line=0.6),
    lantern_field=dict(count=300, center=(0.0, -60.0), radius=(14.0, 110.0)),
    lanterns=Track([(0.0, 0.0), (55.0, 0.0), (57.5, 0.8), (66.0, 0.8), (70.0, 0.0), (117.0, 0.0), (119.5, 1.0),
                    (134.0, 1.0), (140.0, 0.25), (TOTAL, 0.25)]),
    lantern_color="#ffb04a",
    react=dict(beat=0.12, level=0.12),
)

_BURSTS = [dict(t=Grain.T_LAND, strength=0.35, rise=0.15, fall=0.9, color="#ffd8a0", at=tuple(GRAIN * _v(1, 0, 1))),
           dict(t=PEAK1, strength=0.14, rise=0.4, fall=1.2, color="#ffc878"),
           dict(t=PEAK2, strength=0.15, rise=0.4, fall=1.3, color="#ffd08a"),
           dict(t=LAST_NOTE - 0.5, strength=0.1, rise=0.8, fall=2.6, color="#ffd8a0")]

P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=_BURSTS,
    motion_blur=0.25,
)

# the concert's title and signature (engine/titles.py): the song title opens, then a small signature
TITLES = dict(opening=dict(t_end=8.6, dissolve=0.7, build=0, y=0.32),
              signature=dict(windows=[(8.3, TOTAL + 5.0, "tl", "night")], fade=0.9))
FRAGMENTS = []
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
WAVES = []
