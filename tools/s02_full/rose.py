"""Song 02 "The Rose", full-length concert backdrop (song module for the pinned engine d928ff9).

"The Seed Under the Snow" (project-docs/designs/02 The Rose.md) in the approved Nine Colours Revision 3 look:
warm gold glitter people, cream Cormorant phrases with a coloured capsule label (Claude Final v1 words,
commit f43f451), nine coloured comets, warm heavenly light. Every time below is SONG time in seconds on the
measured recording (212.29 s), see project-docs/backdrops/s02-full/TIMELINE.md. The picture runs on for a
15 second calm hold after the music.

Loaded by tools/s02_full/render.py as the engine song "s02_rose_full" (it is put on the engine's songs path).
Nothing here needs a graphics context. No em dash or en dash anywhere in this file.
"""
import importlib
import sys
from pathlib import Path

import numpy as np

import songs.s03_original as _base

MUSIC_END = 212.29
HOLD = 15.0
TOTAL = round(MUSIC_END + HOLD, 1)            # 227.3 s, 6819 frames at 30 fps
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = MUSIC_END
_base.SONG_END = TOTAL
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402
from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
importlib.import_module("reference")                       # registers nine_reference_p3d (Claude Final v1)
PW = importlib.import_module("nine_reference_p3d.words")
importlib.import_module("nine_reference_p3d.master_acting")

TOTAL = round(MUSIC_END + HOLD, 1)
NFRAMES = int(round(TOTAL * FPS))
SONG_END = TOTAL
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]
ENC, COMP = LABELS.index("Encouragement"), LABELS.index("Compliment")
WHITE = "#fff6e6"
GOLD = "#ffd58a"


# ------------------------------------------------------------------------------------------------ helpers
def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _win(a, b, c, d, t):
    """0 before a, rising to 1 by b, 1 until c, falling to 0 by d."""
    return _sc(a, b, t) * (1.0 - _sc(c, d, t))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _mix(a, b, k):
    return np.asarray(a) * (1.0 - k) + np.asarray(b) * k


def _keys(keys, t):
    """Eased interpolation through [(t, value), ...] (values: numbers or arrays)."""
    if t <= keys[0][0]:
        return np.asarray(keys[0][1], np.float64)
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t <= t1:
            return _mix(np.asarray(a, np.float64), np.asarray(b, np.float64), _sc(t0, t1, t))
    return np.asarray(keys[-1][1], np.float64)


# ------------------------------------------------------------------------------------------------ the timeline
T = dict(
    title_in=2.4, title_full=4.6, title_out0=13.4, title_out1=15.4,       # "The Rose" (opening title)
    night=18.2,                                                              # dusk has become the night lake
    snow0=12.0,                                                              # the first snowflake
    star_lift=39.8, star_land=44.5,                                          # the horizon star sinks to the seed
    woman=(46.5, 101.0), cup=(48.0, 86.0), look_up=(52.5, 64.0), lift=(86.0, 99.0),
    dance=(52.0, 66.0),                                                      # a point of gold skates on the ice
    frost=(50.0, 104.0),                                                     # the freeze, near to far
    deep=(97.0, 106.0),                                                      # the longest night, a mirror of stars
    traveler=(104.5, 207.0), walk=(105.0, 117.6), kneel=119.0,
    candles=(120.5, 128.0),                                                  # the choir: lights on the ice
    ribbons=(125.5, 129.6),                                                  # three ribbons pour down
    women=(127.6, 207.0),
    head_up=134.0, hands=136.4,                                              # the traveler lifts her head; hands
    rise=146.0,                                                              # she rises with their help
    wave=(143.6, 151.0),                                                     # the violet wave across the ice
    seed_cam=(144.0, 160.0),                                                 # the camera glides to the seed
    dawn=(159.0, 182.0), thaw=(168.0, 188.0), comets=(167.5, 187.5),
    stem=(169.0, 182.0), bud=(180.0, 188.0), bloom=(187.0, 197.0),
    star_home=(200.5, 209.5), farewell=(202.5, 208.5),
    petal=(222.6, 227.3),
)
# the words (song seconds): t_in, t_read0, t_read1, t_out
WT = dict(
    lonely=(107.5, 109.4, 116.6, 119.0),
    enc=(129.6, 131.6, 141.6, 143.6),
    seed=(149.6, 151.6, 157.8, 159.8),
    rose=(188.8, 190.8, 199.2, 201.2),
    enc2=(213.2, 214.8, 224.8, 226.6),
)

# ------------------------------------------------------------------------------------------------ geography
# metres, y up, the lake is y = 0; the camera looks toward -z over the lake.
SEED = _v(-3.3, 0.0, 2.4)                    # where the star comes down: near, left of centre
HOME = _v(-62.0, 9.5, -420.0)                # the warm star resting on the horizon (left of centre)
WOMAN = _v(1.7, 0.0, 6.2)                   # verse 2
TRAV = _v(0.9, 0.0, 2.0)                    # where the traveler kneels
TRAV_START = _v(12.6, 0.0, 2.0)
ARCH = dict(span=150.0, height=47.0, z=-170.0)
SUN_AZ = 161.0                               # the dawn rises right of the words, behind the mountains


# ------------------------------------------------------------------------------------------------ the camera
class Path(Move):
    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


_CAM = [
    # (t, eye, target): quiet, close, holding its breath; about 5 percent closer per verse
    (0.0, (0.0, 1.20, 18.6), (0.0, 1.05, 0.0)),
    (44.5, (-0.1, 1.15, 17.9), (-0.1, 1.05, 0.0)),
    (50.0, (-0.1, 0.95, 17.9), (0.0, 1.0, 0.0)),
    (95.0, (0.15, 0.95, 17.2), (0.1, 1.0, 0.0)),
    (106.0, (0.3, 1.10, 16.8), (0.3, 1.02, 0.0)),
    (126.0, (0.4, 1.20, 16.0), (0.4, 0.95, 0.0)),
    (131.0, (0.55, 1.32, 14.6), (0.55, 0.92, 0.0)),        # close to the kneeling traveler, then still
    (142.5, (0.55, 1.32, 14.6), (0.55, 0.92, 0.0)),
    (152.0, (-5.6, 1.15, 11.2), (-2.9, 0.45, 0.0)),        # toward the seed under the ice, from the left
    (160.0, (-5.8, 1.12, 11.0), (-3.0, 0.50, 0.0)),
    (172.0, (-1.6, 1.25, 13.6), (-1.8, 1.15, 0.0)),        # back and up into the spring
    (198.0, (-1.4, 1.75, 12.6), (-1.7, 1.45, 0.0)),        # the slow crane: the lake, the rose, the arch
    (TOTAL, (-1.3, 1.82, 12.9), (-1.6, 1.50, 0.0)),
]


def _cam(t):
    eye = _keys([(k[0], k[1]) for k in _CAM], t)
    tgt = _keys([(k[0], k[2]) for k in _CAM], t)
    drift = 0.10 * np.sin(t * 0.045) * (1.0 - _win(129.0, 131.0, 142.5, 144.0, t))
    return eye + _v(drift, 0.0, 0.0), tgt + _v(0.6 * drift, 0.0, 0.0)


def _fov(t):
    return float(_keys([(0.0, 33.0), (46.0, 32.0), (95.0, 31.0), (128.0, 30.5), (131.0, 30.0), (142.5, 30.0),
                        (152.0, 27.0), (160.0, 27.0), (172.0, 31.0), (198.0, 33.0)], t))


CAMERA = Rig([Path(_cam, -1.0, TOTAL + 2.0, blend=0.0, fov=_fov, aperture=0.004, focus="target")],
             blend=0.0, fov=33.0, aperture=0.004, handheld=0.0, min_height=0.3)


def place(t, x, y, depth):
    return np.asarray(PW.place(CAMERA, t, x, y, depth), np.float64)


def _width(t, depth, frac):
    cam = PW._cam_at(CAMERA, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


# ------------------------------------------------------------------------------------------------ the words
RIDE = (0.5, 0.672, 7.0)            # centred 0.33 of the height from the top: the upper middle
_ENC_STYLE = dict(tint=0.62, bright=1.0, halo=1.35, pill=True, nib=False)
_FRAG = dict(color="#f4e2c0", glow="#ffd9a0", tint=0.85, bright=0.95, halo=1.15)


def _spec(name, times, width, **kw):
    a, b, c, d = times
    s = dict(ride=RIDE, face="screen", width=_width(0.5 * (b + c), RIDE[2], width), t_in=a, t_read0=b, t_read1=c,
             t_out=d, reflect=False, name=name)
    s.update(kw)
    return s


_SPECS = [
    _spec("too lonely", WT["lonely"], 0.30, label="", lines=["too lonely"], arrive="reveal", leave="wind", **_FRAG),
    _spec("Encouragement", WT["enc"], 0.58, expr="Encouragement", arrive="weave", leave="rise", **_ENC_STYLE),
    _spec("the seed", WT["seed"], 0.27, label="", lines=["the seed"], arrive="stitch", leave="sink", **_FRAG),
    _spec("becomes the rose", WT["rose"], 0.44, label="", lines=["becomes the rose"], arrive="gather",
          leave="petals", **dict(_FRAG, color="#ffe8dc", glow="#ffc0a8", tint=0.8, bright=1.0, halo=1.5)),
    _spec("Encouragement again", WT["enc2"], 0.50, expr="Encouragement", arrive="reveal", leave="fade",
          **_ENC_STYLE),
]
WORDS = PW.Words(_SPECS, camera=CAMERA)


def word_boxes(t, cam):
    """Screen boxes (x0, x1, y0, y1, from the bottom left) of the words on screen at t, with a margin."""
    out = []
    for w in WORDS:
        if w.t_in - 0.3 <= t <= w.t_out + 0.3:
            x0, x1, y0, y1, front, *_ = PW.screen_box(w, cam, t)
            if front:
                out.append((x0 - 0.03, x1 + 0.03, y0 - 0.045, y1 + 0.045))
    return out


def _clear(pos, cam, t, alpha):
    """Fade light that would cross a word (nothing crosses a word)."""
    boxes = word_boxes(t, cam)
    if not boxes or len(pos) == 0:
        return alpha
    xy, z = cam.project(np.asarray(pos, np.float64).reshape(-1, 3))
    gain = np.ones(len(xy))
    for x0, x1, y0, y1 in boxes:
        dx = np.minimum(xy[:, 0] - x0, x1 - xy[:, 0])
        dy = np.minimum(xy[:, 1] - y0, y1 - xy[:, 1])
        f = np.clip(np.minimum(dx, dy) / 0.025 + 0.5, 0.0, 1.0)
        gain = np.minimum(gain, 1.0 - f * (z > 0))
    return np.asarray(alpha) * gain


# ------------------------------------------------------------------------------------------------ the people
_BODIES = {}


LANTERN_DOWN = TRAV + _v(-0.48, 0.10, 0.08)      # set on the ice before her as she kneels


def lantern(t):
    """The traveler's small lantern: held low in her right hand, then set down on the ice before her."""
    if t >= T["kneel"] + 0.8:
        return LANTERN_DOWN
    b = bodies()["traveler"]
    held = np.asarray(b.where(t, "pinch.R"), np.float64) + _v(0.0, -0.05, 0.0)
    return _mix(held, LANTERN_DOWN, _sc(T["kneel"] - 0.6, T["kneel"] + 0.8, t))


def _woman_light(t):
    b = bodies()["woman"]
    p = 0.5 * (np.asarray(b.where(t, "palm.L"), np.float64) + np.asarray(b.where(t, "palm.R"), np.float64))
    lift = _sc(89.0, 94.5, t) * 0.32 + _sc(97.0, 104.0, t) * 9.0
    return p + _v(0.0, 0.05 + lift, 0.0)


def bodies():
    if _BODIES:
        return _BODIES
    from nine_reference_p3d.body import Body
    glitter = dict(look=dict(name="glitter", seams=0.6), bright=2.1)
    woman = Body("woman", at=(WOMAN[0], WOMAN[2]), facing=-12.0, motion="stand", garment="coat", hair="bun",
                 color="#ffc664", color2="#fff0c8", points=60000, seed=21.0, show=T["woman"], fade=1.6,
                 gesture=[(T["cup"][0], T["lift"][0], "cup", dict(height=0.0, out=0.0)),
                          (T["look_up"][0], T["look_up"][1], "look_up", dict(amount=26.0)),
                          (T["lift"][0], T["lift"][1] + 2.0, "cup", dict(height=0.30, out=0.10)),
                          (T["lift"][0] + 4.0, T["lift"][1] + 2.0, "look_up", dict(amount=34.0))],
                 effects=[dict(kind="form", t=T["woman"][0], dur=1.8)], **glitter)
    _BODIES["woman"] = woman
    walk_end = T["walk"][1]
    trav = Body("woman", at=(TRAV_START[0], TRAV_START[2]), facing=270.0,
                motion=[(T["walk"][0], "walk", dict(speed=0.93)), (walk_end, "stand"),
                        (T["kneel"], "kneel", dict(one=True)), (T["rise"], "rise", dict(dur=2.6, one=True)),
                        (T["rise"] + 2.8, "stand")],
                garment="robe", veil=True, color="#f7b24e", color2="#ffe2a8", points=60000, seed=22.0,
                show=T["traveler"], fade=2.2,
                gesture=[(T["walk"][0], T["kneel"] + 0.6, "hold_thread", dict(side="R")),
                         (T["kneel"] + 0.5, T["head_up"], "bow"),
                         (T["head_up"], 150.0, "look_up", dict(amount=14.0, turn=-20.0)),
                         (T["hands"], T["rise"], "touch", dict(side="L", to=lambda t: _hands_meet(t), palm="down")),
                         (172.0, 201.0, "look_up", dict(amount=22.0))],
                effects=[dict(kind="form", t=T["traveler"][0], dur=2.0)], **glitter)
    _BODIES["traveler"] = trav
    # the three women of the trio: warm white, pale gold, soft rose (all women: every touch is between women)
    kneel_at = TRAV + _v(-0.95, 0.0, 0.12)
    a = Body("woman", at=(kneel_at[0], kneel_at[2]), facing=90.0,
             motion=[(T["women"][0], "stand"), (129.0, "kneel", dict(one=True)),
                     (T["rise"] - 0.4, "rise", dict(dur=2.6, one=True)), (T["rise"] + 2.6, "stand")],
             garment="coat", hair="bob", color="#ffe9c8", color2="#fff8ec", points=55000, seed=23.0,
             show=T["women"], fade=2.2,
             gesture=[(130.2, T["rise"] - 0.2, "touch", dict(side="R", to=lambda t: lantern(t) + _v(0.0, 0.06, 0.0),
                                                                    palm="down")),
                      (172.0, 201.0, "look_up", dict(amount=20.0))],
             effects=[dict(kind="form", t=T["women"][0], dur=1.8)], **glitter)
    _BODIES["kneeler"] = a
    b_at = TRAV + _v(0.62, 0.0, -0.30)
    b = Body("woman", at=(b_at[0], b_at[2]), facing=250.0,
             motion=[(T["women"][0], "stand"), (129.4, "kneel", dict(one=True)),
                     (T["rise"] - 0.2, "rise", dict(dur=2.6, one=True)), (T["rise"] + 2.8, "stand")],
             garment="coat", hair=True,
             color="#ffcf6a", color2="#fff0c0", points=55000, seed=24.0, show=(T["women"][0] + 0.4, T["women"][1]),
             fade=2.2,
             gesture=[(130.6, T["rise"] - 0.6, "hand_on_shoulder",
                       dict(side="R", to=lambda t: bodies()["traveler"].where(t, "shoulder.R"))),
                      (172.0, 201.0, "look_up", dict(amount=20.0))],
             effects=[dict(kind="form", t=T["women"][0] + 0.4, dur=1.8)], **glitter)
    _BODIES["scarf"] = b
    c_at = TRAV + _v(-1.25, 0.0, -1.1)
    c = Body("woman", at=(c_at[0], c_at[2]), facing=150.0,
             motion=[(T["women"][0], "stand"), (129.8, "kneel"), (T["rise"] + 0.6, "stand", dict(blend=2.4))],
             garment="coat", hair="bun",
             color="#ffb6a0", color2="#ffe6dc", points=55000, seed=25.0, show=(T["women"][0] + 0.8, T["women"][1]),
             fade=2.2,
             gesture=[(130.0, 162.0, "pray"), (172.0, 201.0, "look_up", dict(amount=20.0))],
             effects=[dict(kind="form", t=T["women"][0] + 0.8, dur=1.8)], **glitter)
    _BODIES["prayer"] = c
    return _BODIES


def _hands_meet(t):
    return np.asarray(bodies()["kneeler"].where(t, "palm.R"), np.float64) + _v(0.0, 0.05, 0.0)


# ------------------------------------------------------------------------------------------------ point sets
def _dots(pos, size, color, alpha, emit=1.0, kind="soft", **kw):
    d = dict(pos=np.asarray(pos, np.float64).reshape(-1, 3), size=size, color=color, alpha=alpha, emit=emit,
             kind=kind)
    d.update(kw)
    return d


def snow_amount(t):
    return float(_keys([(11.0, 0.0), (18.0, 0.35), (46.0, 0.5), (66.0, 0.62), (94.0, 0.7), (100.0, 0.25),
                        (106.0, 0.25), (112.0, 0.7), (128.0, 0.55), (160.0, 0.5), (168.0, 0.22), (176.0, 0.0)], t))


def snow_speed(t):
    """How fast the snow falls (1 normal): almost a hover while the Encouragement is read."""
    return float(_keys([(0.0, 1.0), (64.0, 1.0), (65.2, 0.25), (66.6, 1.0), (128.0, 1.0), (131.0, 0.12),
                        (141.6, 0.12), (144.0, 0.8)], t))


class Snow:
    """Snow in three depths: soft warm white flakes, a glint of gold as they catch the light."""
    wants_camera = True

    def __init__(self, n=5200):
        r = np.random.default_rng(202)
        self.n = n
        z = 15.5 - 120.0 * r.random(n) ** 1.6
        x = (r.random(n) - 0.5) * (8.0 + 0.95 * (16.0 - z))
        self.base = np.stack([x, 14.0 * r.random(n), z], axis=1)
        self.s = r.random((n, 5))
        self.h = 14.0
        # the fall is integrated so the speed can change without a jump
        ts = np.arange(0.0, TOTAL + 2.0, 0.1)
        sp = np.array([snow_speed(x) for x in ts])
        self.clock_t, self.clock = ts, np.concatenate([[0.0], np.cumsum(0.5 * (sp[1:] + sp[:-1]) * 0.1)])

    def sample(self, t, cam=None):
        amt = snow_amount(t)
        if amt <= 0.003:
            return None
        u = float(np.interp(t, self.clock_t, self.clock))
        s = self.s
        fall = (0.55 + 0.5 * s[:, 0]) * u
        y = np.mod(self.base[:, 1] - fall, self.h)
        sway = 0.35 * np.sin(u * (0.6 + 0.5 * s[:, 1]) + 6.28 * s[:, 2])
        wind = 0.9 * _sc(106.0, 112.0, t) * (1.0 - _sc(126.0, 130.0, t))
        x = self.base[:, 0] + sway - wind * np.mod(u * (0.5 + s[:, 3]) + 30.0 * s[:, 4], 30.0)
        pos = np.stack([x, y + 0.05, self.base[:, 2]], axis=1)
        dist = 16.0 - self.base[:, 2]
        keep = s[:, 4] < amt
        near = dist < 4.0
        al = np.where(near, 0.35, 0.85) * (0.5 + 0.5 * s[:, 1])
        al = al * np.clip(y / 0.6, 0.0, 1.0)
        if cam is not None:
            al = _clear(pos, cam, t, al)
        col = _mix(lin("#fff8ee"), lin("#ffe0a8"), (s[:, 3] > 0.82)[:, None] * 1.0)
        dawn = _sc(160.0, 172.0, t)
        col = _mix(col, lin("#ffd8c8"), dawn)
        size = (0.018 + 0.03 * s[:, 2] ** 2) * (1.0 - 0.35 * near)
        return [_dots(pos[keep], size[keep], col[keep], al[keep], emit=1.4, kind="soft", twinkle=0.5,
                      seed=s[keep, 0])]


class HomeStar:
    """The warm star on the horizon: it sinks down across the lake to the near shore and becomes the seed, and
    at the end it rises from the open rose and floats home."""

    def __init__(self):
        r = np.random.default_rng(31)
        self.tail = r.random((240, 4))

    def where(self, t):
        if t < T["star_lift"]:
            return HOME
        if t < T["star_land"]:
            u = _sc(T["star_lift"], T["star_land"], t)
            u = 1.0 - (1.0 - u) ** 1.35
            mid = _v(-34.0, 26.0, -150.0)
            return (1 - u) ** 2 * HOME + 2 * (1 - u) * u * mid + u * u * SEED
        if t < T["star_home"][0]:
            return SEED
        u = _sc(T["star_home"][0], T["star_home"][1], t)
        mid = _v(-26.0, 20.0, -120.0)
        top = rose_top()
        return (1 - u) ** 2 * top + 2 * (1 - u) * u * mid + u * u * HOME

    def visible(self, t):
        return 1.0 - _win(T["star_land"] - 0.1, T["star_land"] + 1.2, T["star_home"][0] - 0.6,
                          T["star_home"][0] + 0.4, t)

    def sample(self, t):
        out = []
        k = self.visible(t)
        if k > 0.002:
            p = self.where(t)
            d = float(np.linalg.norm(p - _cam(t)[0]))
            scale = max(d, 8.0) / 40.0
            travelling = _win(T["star_lift"], T["star_lift"] + 0.6, T["star_land"] - 0.4, T["star_land"], t) + \
                _win(T["star_home"][0], T["star_home"][0] + 0.5, T["star_home"][1] - 1.0, T["star_home"][1], t)
            pulse = 1.0 + 0.06 * np.sin(t * 2.1)
            out.append(_dots(p, 0.22 * scale * pulse, lin("#fff2d4"), k, emit=7.0, kind="spark"))
            out.append(_dots(p, 2.6 * scale, lin(GOLD), 0.22 * k, kind="soft"))
            out.append(_dots(p, 7.0 * scale, lin("#ffcf8a"), 0.05 * k, kind="soft"))
            if travelling > 0.01:
                tt = np.linspace(t - 1.6, t, 60)
                pts = np.array([self.where(float(x)) for x in tt])
                from p3d.api import ribbon
                w = 0.35 * scale
                age = np.linspace(1.0, 0.0, 60)
                out.append(ribbon(pts, width=w * (0.2 + 0.8 * (1 - age)), color=lin("#ffd28a"),
                                  alpha=travelling * k * (1 - age) ** 1.5 * 0.8, emit=2.0))
        return out or None


class Seed:
    """The seed of light under the snow: a warm glow that breathes like a heart, roots of light reaching down,
    one small shoot curled upward. It wakes when the violet light of the words reaches it."""

    def __init__(self):
        r = np.random.default_rng(41)
        roots = []
        for k in range(9):
            a = 2 * np.pi * k / 9 + 0.4 * r.random()
            d = np.array([np.cos(a), -1.3 - 0.8 * r.random(), np.sin(a) * 0.6])
            p = SEED + _v(0.0, -0.08, 0.0)
            for i in range(120):
                d = d + 0.25 * (r.random(3) - 0.5)
                d[1] = min(d[1], -0.2)
                d = d / np.linalg.norm(d)
                p = p + d * 0.008
                roots.append((p.copy(), i / 120.0, k))
        self.roots = np.array([q for q, _, _ in roots])
        self.rr = np.array([f for _, f, _ in roots])
        self.rs = r.random(len(roots))

    def beat(self, t):
        rate = 0.55 + 0.75 * _sc(150.0, 166.0, t)
        return 0.5 + 0.5 * np.sin(2 * np.pi * (rate * t)) ** 8

    def sample(self, t):
        if t < T["star_land"] - 0.2 or t > T["stem"][1] + 4.0:
            return None
        k = _sc(T["star_land"] - 0.2, T["star_land"] + 2.0, t) * (1.0 - _sc(T["stem"][1], T["stem"][1] + 4.0, t))
        wake = _sc(148.5, 152.0, t)
        b = self.beat(t)
        out = [_dots(SEED + _v(0, -0.03, 0), 0.10 + 0.03 * b, lin("#ffb347"), k * (0.7 + 0.3 * b), emit=4.0,
                     kind="spark"),
               _dots(SEED + _v(0, 0.02, 0), 0.9 + 0.25 * b + 0.6 * wake, lin("#ffc070"), k * (0.10 + 0.06 * b),
                     kind="soft")]
        grow = _sc(46.0, 150.0, t) * 0.55 + 0.45 * wake
        show = self.rr < grow
        if show.any():
            seen = _sc(143.0, 150.0, t) * (1.0 - _sc(168.0, 176.0, t))
            al = (0.06 + 0.94 * seen) * (0.5 + 0.5 * b) * k * (1.0 - self.rr) ** 0.5
            col = _mix(lin("#ffb347"), lin("#fff0c0"), 0.3 + 0.4 * wake)
            out.append(_dots(self.roots[show], 0.012 + 0.01 * self.rs[show], col, al[show], emit=2.2, kind="spark",
                             twinkle=0.3, seed=self.rs[show]))
        return out


class Woman_light:
    """The small warm light the young woman holds against her chest, then lifts in open hands."""

    def sample(self, t):
        if t < T["woman"][0] + 0.8 or t > 106.0:
            return None
        k = _sc(T["woman"][0] + 0.8, T["cup"][0] + 1.0, t) * (1.0 - _sc(103.0, 106.0, t))
        p = _woman_light(t)
        flicker = 1.0 + 0.08 * np.sin(t * 7.3) * (1.0 - _sc(86.0, 90.0, t))
        tempted = 0.25 * _win(56.0, 58.0, 61.0, 63.5, t)
        return [_dots(p, (0.05 + 0.02 * tempted) * flicker, lin("#ffe2b0"), k, emit=6.0, kind="spark"),
                _dots(p, 0.55 * flicker, lin("#ffc27a"), 0.16 * k, kind="soft")]


class Dancer:
    """A single point of gold skating on the new ice in long curving loops, its trail cut into the frost."""

    def head(self, t):
        u = t - T["dance"][0]
        c = _v(-0.6, 0.04, -1.0)
        a = 0.62 * u
        r = 2.4 + 0.9 * np.sin(0.37 * u)
        return c + _v(r * np.cos(a) * 1.5, 0.0, r * np.sin(a) * 1.1 - 1.2 * np.sin(0.21 * u))

    def sample(self, t):
        a0, a1 = T["dance"]
        if t < a0 or t > a1 + 6.0:
            return None
        k = _win(a0, a0 + 1.2, a1 - 1.5, a1, t)
        out = []
        if k > 0.0:
            h = self.head(t)
            out += [_dots(h + _v(0, 0.06, 0), 0.07, lin("#fff0c8"), k, emit=6.0, kind="spark"),
                    _dots(h + _v(0, 0.1, 0), 0.9, lin(GOLD), 0.12 * k, kind="soft")]
        tt = np.linspace(a0, min(t, a1), 500)
        pts = np.array([self.head(float(x)) for x in tt]) + _v(0, 0.012, 0)
        age = t - tt
        al = np.exp(-age / 3.5) * _sc(a0, a0 + 1.0, t)
        out.append(_dots(pts, 0.035, lin("#ffe2a0"), 0.55 * al, emit=2.0, kind="spark"))
        return out


class Frost:
    """Frost growing over the lake from the near shore outward (the freeze), then melting from the far side as
    the sun's love arrives (the thaw). Fine glints, so the frozen lake still mirrors the stars."""
    static = True

    def __init__(self, n=26000):
        r = np.random.default_rng(51)
        z = 14.5 - 260.0 * r.random(n) ** 2.2
        x = (r.random(n) - 0.5) * (20.0 + 1.2 * (15.0 - z))
        self.pos = np.stack([x, np.full(n, 0.015), z], axis=1)
        reach = (14.5 - z) / 274.5
        self.birth = T["frost"][0] + (T["frost"][1] - T["frost"][0]) * (reach ** 0.8 + 0.06 * r.random(n))
        self.melt = T["thaw"][0] + (T["thaw"][1] - T["thaw"][0]) * (1.0 - reach) ** 0.9 + 1.5 * r.random(n)
        self.s = r.random((n, 3))
        near = z > 8.0
        self.alpha = np.where(near, 0.22, 0.55) * (0.4 + 0.6 * self.s[:, 0])
        self.size = (0.03 + 0.06 * self.s[:, 1] ** 2) * (1.0 + (14.5 - z) / 60.0)
        self.col = _mix(lin("#dfe9ff"), lin("#ffe6b8"), (self.s[:, 2] > 0.7)[:, None] * 1.0)

    def sample(self, t):
        if t < T["frost"][0] or t > T["thaw"][1] + 3.0:
            return None
        al = self.alpha * _ss(0.0, 2.5, t - self.birth) * (1.0 - _ss(0.0, 2.5, t - self.melt))
        on = al > 0.003
        if not on.any():
            return None
        return _dots(self.pos[on], self.size[on], self.col[on], al[on], emit=1.2, kind="spark", twinkle=0.8,
                     seed=self.s[on, 0])


class Candles:
    """The female choir: the snow on the ice around the kneeling traveler lights, flake by flake, until the lake
    shines like a field of small candles. The violet wave of the words passes through them; at the thaw they
    rise softly as blossoms of light."""

    def __init__(self, n=1700):
        r = np.random.default_rng(61)
        a = r.random(n) * 2 * np.pi
        rad = 1.6 + 60.0 * r.random(n) ** 1.7
        self.pos = TRAV + np.stack([np.cos(a) * rad * 1.3, np.full(n, 0.03), np.sin(a) * rad * 1.1 - 0.3 * rad],
                                   axis=1)
        keep = self.pos[:, 2] < 7.5
        self.pos, rad = self.pos[keep], rad[keep]
        self.rad = rad
        n = len(rad)
        self.light = T["candles"][0] + (T["candles"][1] - T["candles"][0]) * np.clip(
            rad / 60.0 * 0.6 + 0.4 * r.random(n), 0, 1)
        self.wave = T["wave"][0] + rad / 6.5
        self.s = r.random((n, 3))

    def sample(self, t):
        if t < T["candles"][0] or t > 190.0:
            return None
        lit = _ss(0.0, 1.2, t - self.light)
        v = np.exp(-((t - self.wave) / 0.9) ** 2)
        col = _mix(lin("#ffcf7a"), lin(COL[ENC]) * 1.2, v[:, None])
        rise = np.maximum(t - (T["thaw"][0] + 4.0 + 10.0 * self.s[:, 0]), 0.0)
        pos = self.pos + np.stack([0.2 * np.sin(rise + 6 * self.s[:, 1]), 0.35 * rise, np.zeros_like(rise)], axis=1)
        fade = 1.0 - _ss(0.0, 5.0, rise)
        al = lit * (0.45 + 0.35 * self.s[:, 2] + 0.9 * v) * fade * (1.0 - 0.4 * _sc(131.0, 132.5, t)
                                                                      * (1.0 - _sc(141.0, 143.0, t)))
        near = np.clip((pos[:, 2] - 0.0) / 7.5, 0.0, 1.0)
        al = al * (1.0 - 0.7 * near)
        size = (0.04 + 0.04 * self.s[:, 1] + 0.04 * v) * (1.0 - 0.5 * near)
        return [_dots(pos, size, col, al, emit=1.8, kind="soft", twinkle=0.35, seed=self.s[:, 0]),
                _dots(pos, size * 0.35, col, al, emit=3.0, kind="spark", seed=self.s[:, 0])]


class Ribbons:
    """The trio: three thin ribbons of light high in the sky (warm white, pale gold, soft rose). They braid and
    part with the singing and, in verse 3, pour down like falling silk to become the three women."""
    COLS = ("#fff1dc", "#ffd27a", "#ffb0a0")

    def __init__(self):
        self.targets = None

    def _sky(self, k, t):
        ph = 2.1 * k
        z = -70.0 - 6.0 * k
        x = -18.0 + 6.0 * np.sin(0.11 * t + ph) + 14.0 * k
        y = 17.0 + 2.2 * np.sin(0.07 * t + ph) + 1.5 * k
        return _v(x, y, z)

    def head(self, k, t):
        sky = self._sky(k, t)
        a0, a1 = T["ribbons"]
        u = _sc(a0, a1, t)
        if u <= 0.0:
            return sky
        name = ("kneeler", "scarf", "prayer")[k]
        b = bodies()[name]
        dest = np.asarray(b.actor.origin, np.float64) if hasattr(b.actor, "origin") else TRAV
        dest = _v(dest[0], 1.1, dest[2])
        mid = _mix(sky, dest, 0.5) + _v(0.0, 6.0, 0.0)
        return (1 - u) ** 2 * sky + 2 * (1 - u) * u * mid + u * u * dest

    def amount(self, t):
        return float(_keys([(14.0, 0.0), (20.0, 0.35), (46.0, 0.45), (95.0, 0.5), (100.0, 0.15), (118.0, 0.15),
                            (124.0, 0.6), (128.6, 0.6), (130.0, 0.0)], t))

    def sample(self, t):
        a = self.amount(t)
        if a <= 0.003:
            return None
        from p3d.api import ribbon
        out = []
        for k in range(3):
            n = 50
            span = 9.0 if t < T["ribbons"][0] else 2.2
            tt = np.linspace(t - span, t, n)
            pts = np.array([self.head(k, float(x)) for x in tt])
            if t < T["ribbons"][0]:
                pts = np.array([self._sky(k, float(x)) + _v(2.8 * (x - t), 1.6 * np.sin(0.9 * (x - t) + 0.6 * t + 2.0 * k),
                                                      0.0) for x in tt])
            age = np.linspace(1.0, 0.0, n)
            c = lin(self.COLS[k])
            env = np.sin(np.pi * (1 - age))
            falling = _sc(T["ribbons"][0], T["ribbons"][0] + 0.5, t)
            wide = 2.6 * (1.0 - falling) + 0.45 * falling
            out.append(ribbon(pts, width=wide * (0.3 + 0.7 * env ** 0.5), color=c * 0.55,
                              alpha=a * 0.16 * env, emit=1.0))
            out.append(ribbon(pts, width=0.12 * (0.3 + 0.7 * env), color=c * 0.8, alpha=a * 0.22 * env, emit=1.4))
            out.append(_dots(pts[-1:], 0.25, c, a * 0.6 * falling, emit=4.0, kind="spark"))
        return out


class Lantern:
    """The traveler's lantern and the light that two hands share on it."""

    def sample(self, t):
        if t < T["traveler"][0] + 1.0 or t > T["farewell"][1]:
            return None
        k = _sc(T["traveler"][0] + 1.0, T["traveler"][0] + 3.0, t) * (1.0 - _sc(T["farewell"][0], T["farewell"][1], t))
        dim = 1.0 - 0.55 * _win(109.0, 113.0, 119.0, 130.5, t)
        relit = 0.6 * _sc(130.6, 133.0, t) + 0.6 * _sc(T["hands"], T["hands"] + 1.5, t)
        flick = 1.0 + 0.12 * np.sin(t * 9.1) * np.sin(t * 3.7)
        p = lantern(t)
        s = (dim + relit) * flick
        out = [_dots(p, 0.06 * s, lin("#fff0c8"), k, emit=6.0, kind="spark"),
               _dots(p, 0.6 * s, lin("#ffc27a"), 0.18 * k, kind="soft")]
        glow = _win(T["hands"], T["hands"] + 1.2, 168.0, 175.0, t)
        if glow > 0.01:
            for name in ("traveler", "kneeler"):
                c = np.asarray(bodies()[name].where(t, "heart"), np.float64)
                out.append(_dots(c, 0.9, lin("#ffd9a0"), 0.10 * glow * k, kind="soft"))
        return out


class Footprints:
    """A line of faintly glowing footprints behind the traveler, fading."""

    def sample(self, t):
        a, b = T["walk"]
        if t < a + 0.5 or t > b + 9.0:
            return None
        tr = bodies()["traveler"]
        steps = np.arange(a + 0.6, min(t, b), 0.55)
        if len(steps) == 0:
            return None
        pts = []
        for i, s in enumerate(steps):
            g = np.asarray(tr.where(float(s), "ground"), np.float64)
            pts.append(g + _v(0.0, 0.02, 0.12 if i % 2 else -0.12))
        pts = np.array(pts)
        al = 0.45 * np.exp(-(t - steps) / 4.5)
        return _dots(pts, 0.09, lin("#ffd9a0"), al, emit=1.6, kind="soft")


class Wave:
    """The words' second light: a violet drop falls onto the snow and a wave spreads across the ice and down
    through the snow to the seed. Where the words reach, peace settles."""

    def __init__(self):
        r = np.random.default_rng(71)
        self.a = r.random(900) * 2 * np.pi
        self.s = r.random(900)

    def sample(self, t):
        a0, a1 = T["wave"]
        if t < a0 or t > a1 + 2.0:
            return None
        u = t - a0
        rad = 9.0 * u
        k = (1.0 - _sc(a1 - 2.0, a1 + 2.0, t))
        ring = TRAV + np.stack([np.cos(self.a) * rad * 1.2, np.full(len(self.a), 0.05), np.sin(self.a) * rad], axis=1)
        out = [_dots(ring, 0.12 + 0.1 * self.s, lin(COL[ENC]) * 1.3, 0.55 * k * np.exp(-u / 4.0), emit=2.0,
                     kind="soft", seed=self.s)]
        # the thread that goes down to the seed
        th = _sc(a0 + 0.8, a0 + 4.8, t)
        if th > 0.0:
            n = 120
            f = np.linspace(0.0, th, n)
            start = TRAV + _v(0.0, 0.05, 0.6)
            ctrl = _mix(start, SEED, 0.5) + _v(0.0, -0.6, 0.0)
            pts = (1 - f)[:, None] ** 2 * start + 2 * ((1 - f) * f)[:, None] * ctrl + (f ** 2)[:, None] * SEED
            spin = 0.06 * np.stack([np.cos(30 * f + 3 * t), np.zeros(n), np.sin(30 * f + 3 * t)], axis=1) * \
                (f > 0.85)[:, None]
            out.append(_dots(pts + spin, 0.035, lin(COL[ENC]) * 1.4, 0.8 * k * np.ones(n), emit=3.0, kind="spark"))
        return out


# ------------------------------------------------------------------------------------------------ the rose
def rose_open(t):
    return float(_sc(T["bud"][0], T["bud"][1], t) * 0.18 + _sc(T["bloom"][0], T["bloom"][1], t) * 0.82)


STEM_H = 1.6


def rose_top(t=None):
    return SEED + _v(0.0, STEM_H + 0.12, 0.0)


class Rose:
    """A rose of light opens where the seed lay: a stem with two leaves, a bud, petals that open one ring after
    another, a crimson heart and warm rose gold edges, dew on its petals. It breathes in the hold."""

    def __init__(self):
        r = np.random.default_rng(81)
        P = []
        rings = [(5, 0.10, 0.0), (6, 0.15, 0.5), (7, 0.20, 0.2), (8, 0.25, 0.7), (9, 0.30, 0.35)]
        for ri, (m, ln, ph) in enumerate(rings):
            for j in range(m):
                phi = 2 * np.pi * (j + ph) / m + 0.3 * ri
                q = 650
                u = r.random(q) ** 0.8
                v = (r.random(q) - 0.5) * 2.0
                P.append(np.stack([np.full(q, ri), np.full(q, phi), np.full(q, ln), u, v, r.random(q)], axis=1))
        self.p = np.concatenate(P)
        self.nr = len(rings)
        self.dew = r.choice(len(self.p), 160, replace=False)
        n = 1400
        self.stem_u = np.sort(r.random(n))
        self.stem_s = r.random((n, 2))
        self.leaf = r.random((2, 900, 3))

    def _petals(self, t, opening):
        ri, phi, ln, u, v, s = self.p.T
        ring = ri / (self.nr - 1)
        breathe = 1.0 + 0.015 * np.sin(t * 0.8) * _sc(205.0, 212.0, t)
        o = np.clip(opening * 1.2 - 0.2 * (1 - ring), 0.0, 1.0)
        # each petal rises from the heart along an arc: its angle from the vertical grows from a to a + b
        a = np.radians(3.0 + 5.0 * ring) + o * np.radians(5.0 + 22.0 * ring ** 1.2)
        b = np.radians(4.0) + o * np.radians(6.0 + 22.0 * ring)
        L = ln * (0.85 + 0.25 * opening) * breathe * 2.1
        th = a + b * u
        r = L * (np.cos(a) - np.cos(th)) / b
        y = L * (np.sin(th) - np.sin(a)) / b
        w = L * 0.62 * np.sin(np.pi * np.clip(u * 0.85 + 0.12, 0, 1)) ** 0.6 * (0.7 + 0.3 * ring)
        lx = v * w
        r = r - 0.30 * w * v ** 2 + 0.015 + 0.02 * ring          # the edges curve in: a cup
        x = r * np.cos(phi) - lx * np.sin(phi)
        z = r * np.sin(phi) + lx * np.cos(phi)
        base = rose_top() + _v(0.0, -0.16, 0.0)
        pos = base + np.stack([x, y, z], axis=1)
        edge = np.clip(0.6 * u + 0.4 * np.abs(v), 0, 1)
        col = _mix(lin("#c01840"), lin("#ff7a70"), edge[:, None] ** 1.6)
        col = _mix(col, lin("#ffc0a0"), (edge[:, None] > 0.94) * 0.5)
        return pos, col, s

    def sample(self, t):
        a0 = T["stem"][0]
        if t < a0:
            return None
        out = []
        g = _sc(a0, T["stem"][1], t)
        # stem of light
        su = self.stem_u[self.stem_u < g]
        if len(su):
            sway = 0.03 * np.sin(t * 0.6)
            pos = SEED + np.stack([0.03 * np.sin(su * 4.0) + sway * su, su * STEM_H, 0.02 * np.cos(su * 3.0)],
                                  axis=1)
            pos += (self.stem_s[: len(su)] - 0.5) @ np.array([[0.012, 0, 0], [0, 0, 0.012]])
            out.append(_dots(pos, 0.012, lin("#d8e8a0"), 0.42, emit=1.4, kind="spark"))
        # two leaves
        lg = _sc(T["stem"][0] + 7.0, T["stem"][1] + 2.0, t)
        if lg > 0:
            for i, (h, side) in enumerate(((0.45, 1.0), (0.66, -1.0))):
                q = self.leaf[i]
                uu, vv = q[:, 0], (q[:, 1] - 0.5) * 2
                L = 0.30 * lg
                x = side * uu * L
                y = 0.25 * uu * L + 0.03 * np.sin(np.pi * uu)
                z = vv * 0.09 * lg * np.sin(np.pi * uu)
                pos = SEED + _v(0.0, h * STEM_H, 0.0) + np.stack([x, y, z], axis=1)
                out.append(_dots(pos, 0.012, lin("#c8e090"), 0.55 * lg, emit=1.6, kind="spark"))
        # petals
        o = rose_open(t)
        bk = _sc(T["bud"][0], T["bud"][0] + 3.0, t)
        if bk > 0:
            pos, col, s = self._petals(t, o)
            keep = np.ones(len(pos), bool)
            if t > T["petal"][0]:
                keep[:650] = False                           # the lifted petal leaves the rose
            al = bk * (0.24 + 0.16 * s)
            out.append(_dots(pos[keep], 0.012, col[keep] * 1.3, al[keep], emit=0.9, kind="spark", twinkle=0.2,
                             seed=s[keep]))
            heart = rose_top() + _v(0.0, -0.02, 0.0)
            out.append(_dots(heart, 0.35 + 0.15 * o, lin("#e0506a"), 0.06 * bk * (0.5 + o), kind="soft"))
            out.append(_dots(heart, 1.8, lin("#ffb090"), 0.02 * bk * o, kind="soft"))
            dew = _sc(T["bloom"][0] + 3.0, T["bloom"][1], t) * (1.0 - 0.6 * _win(188.8, 190.8, 199.2, 201.2, t))
            if dew > 0:
                d = pos[self.dew]
                order = np.linspace(0, 1, len(d))
                on = _ss(0.0, 0.4, (t - T["bloom"][0] - 3.0) / 6.0 - order)
                out.append(_dots(d + _v(0, 0.01, 0), 0.016, lin("#fff6ea"), dew * on, emit=6.0, kind="spark",
                                 twinkle=0.7, seed=order))
            if t > T["petal"][0]:
                out.append(self._lifted(t))
        return out

    def _lifted(self, t):
        u = t - T["petal"][0]
        pos, col, s = self._petals(T["petal"][0], 1.0)
        pos, col, s = pos[:650], col[:650], s[:650]
        c = pos.mean(axis=0)
        drift = _v(0.55 * u + 0.05 * u * u, 0.55 * u + 0.08 * u * u, -0.2 * u)
        ang = 0.6 * u
        R = np.array([[np.cos(ang), -np.sin(ang), 0], [np.sin(ang), np.cos(ang), 0], [0, 0, 1]])
        p = (pos - c) @ R.T + c + drift
        apricot = _mix(col, lin("#ffb48a"), 0.5)
        return _dots(p, 0.012, apricot, 0.9 * (0.6 + 0.4 * s), emit=2.6, kind="spark", seed=s)


class Blossoms:
    """Small blossoms of light opening across the far shores at the thaw, spreading out like a wave."""

    def __init__(self, n=2600):
        r = np.random.default_rng(91)
        a = np.radians(-70.0 + 140.0 * r.random(n))
        d = 150.0 + 230.0 * r.random(n)
        self.pos = np.stack([np.sin(a) * d * 1.3, 0.5 + 6.0 * r.random(n) * (d / 380.0), -np.cos(a) * d], axis=1)
        self.birth = T["thaw"][0] + 3.0 + 14.0 * (np.abs(a) / 1.22) * 0.6 + 6.0 * r.random(n)
        self.s = r.random((n, 3))
        self.col = _mix(lin("#ffd6e0"), lin("#fff0c8"), self.s[:, :1])

    def sample(self, t):
        if t < T["thaw"][0]:
            return None
        al = _ss(0.0, 2.0, t - self.birth) * (0.35 + 0.4 * self.s[:, 1])
        al = al * (1.0 - 0.35 * _sc(214.0, TOTAL, t))
        on = al > 0.003
        if not on.any():
            return None
        return _dots(self.pos[on], 0.35 + 0.5 * self.s[on, 2], self.col[on], al[on], emit=1.6, kind="spark",
                     twinkle=0.5, seed=self.s[on, 0])


class Comets:
    """The nine coloured comets of the approved look: at the sunrise they rise from behind the mountains, fan
    out across the dawn sky in long gentle arcs and come to rest in their own places on the arch."""

    def __init__(self):
        r = np.random.default_rng(10)
        self.sp = r.random((9, 90, 4))

    def head(self, k, t):
        a0, a1 = T["comets"]
        t0 = a0 + 0.55 * k
        t1 = a1 - 4.0 + 0.45 * k
        u = _sc(t0, t1, t)
        u = 1.0 - (1.0 - u) ** 1.6
        start = _v(-10.0 + 2.5 * k, 2.0, -400.0)
        end = arch_homes()[k]
        side = -1.0 if k < 4 else (1.0 if k > 4 else 0.3)
        mid = _mix(start, end, 0.5) + _v(side * 70.0, 60.0 - 6.0 * abs(k - 4), 40.0)
        return (1 - u) ** 2 * start + 2 * (1 - u) * u * mid + u * u * end

    def sample(self, t):
        a0, a1 = T["comets"]
        if t < a0 or t > a1 + 1.0:
            return None
        from p3d.api import ribbon
        out = []
        for k in range(9):
            t0 = a0 + 0.55 * k
            a = _sc(t0, t0 + 0.8, t) * (1.0 - _sc(a1 - 3.0 + 0.45 * k, a1 + 0.45 * k - 1.0, t))
            if a <= 0.002:
                continue
            ts = np.linspace(max(t - 2.4, t0), t, 40)
            if ts[-1] - ts[0] < 1e-3:
                continue
            pts = np.array([self.head(k, float(x)) for x in ts])
            kk = np.linspace(0.0, 1.0, 40)
            c = lin(COL[k])
            m = float(c.max())
            deep = m * (c / m) ** 1.35
            core = 0.35 * c + 0.65 * lin(WHITE)
            w = 2.6
            core = 0.6 * c + 0.4 * lin(WHITE)
            out.append(ribbon(pts, width=w * (0.12 + 0.88 * kk), color=deep, alpha=a * 0.85 * kk, emit=2.2))
            out.append(ribbon(pts, width=w * 0.22 * (0.15 + 0.85 * kk), color=core, alpha=a * 0.6 * kk, emit=2.0))
            out.append(_dots(pts[-1:], w * 0.6, core, a, emit=6.0, kind="spark"))
            out.append(_dots(pts[-1:], w * 4.0, c, a * 0.14, kind="soft"))
        return out


def arch_homes():
    from p3d.world import arch_points
    return arch_points(span=ARCH["span"], height=ARCH["height"], z=ARCH["z"])


def arch_lit(t):
    """Stars 9 (Compliment) and 7 (Encouragement) lit from song 01; the seven others are dim seeds. Star 7
    flares and gains a fresh ring when the Encouragement rises into it; the comets wake each seed for a moment
    as they arrive, then it settles back."""
    dim_night = 1.0 - 0.45 * _win(96.0, 104.0, 126.0, 132.0, t)
    out = []
    for k in range(9):
        if k in (ENC, COMP):
            base = 0.6 * dim_night
            age = 30.0
            if k == ENC:
                fl = WT["enc"][3] - 0.1
                if t >= fl:
                    base += 1.4 * np.exp(-(t - fl) * 1.0)
                    age = t - fl
            out.append((base, age))
        else:
            arrive = T["comets"][1] - 3.5 + 0.45 * k
            glow = 0.08 + 0.45 * np.exp(-max(t - arrive, 0.0) * 0.6) * (t >= arrive)
            out.append((glow * _sc(10.0, 20.0, t) if t < arrive else glow, max(t - arrive, 0.0)))
    return out


def _setup(scene):
    scene.add("s02 home star", HomeStar(), reflect=True)
    scene.add("s02 seed", Seed(), reflect=False)
    scene.add("s02 frost", Frost(), reflect=False)
    scene.add("s02 dancer", Dancer(), reflect=True)
    scene.add("s02 woman light", Woman_light(), reflect=True)
    scene.add("s02 ribbons", Ribbons(), reflect=False)
    scene.add("s02 candles", Candles(), reflect=False)
    scene.add("s02 footprints", Footprints(), reflect=False)
    scene.add("s02 lantern", Lantern(), reflect=True)
    scene.add("s02 wave", Wave(), reflect=False)
    scene.add("s02 blossoms", Blossoms(), reflect=True)
    scene.add("s02 comets", Comets(), reflect=False)
    scene.add("s02 rose", Rose(), reflect=False)
    import os
    if not os.environ.get("S02_NO_PEOPLE"):                  # quick look checks only
        for name, body in bodies().items():
            body.add(scene, name)
    scene.add("s02 snow", Snow(), reflect=False)
    WORDS.add_to(scene)


# ------------------------------------------------------------------------------------------------ the world
LOOKS = dict(
    morning=dict(base="sunrise", sky_top="#173a74", sky_mid="#8c7282", sky_hor="#ffc47c", sun_az=180.0,
                 sun_el=2.0, sun_int=0.7, sun_glow=0.4, haze=0.25, haze_color="#a8786a", mist=0.08,
                 mist_color="#8a6a78", exposure=0.8,
                 hill_color="#2a2440", water="#141022", stars=0.05, milky=0.0, rays=0.45, clouds=0.35,
                 dust_color="#ffe2a8", dust_color2="#ffd0a8"),
    dusk=dict(base="dusk", sky_top="#0e1440", sky_mid="#3a2e66", sky_hor="#b0687a", sun_el=-4.0, sun_int=0.4,
              stars=0.45, milky=0.0, haze_color="#5a3a66", mist=0.3, mist_color="#4a3a68", clouds=0.25,
              water="#05050f", hill_color="#0b0a1a"),
    home=dict(base="night", sky_top="#0b1030", sky_mid="#141a44", sky_hor="#2c2e62", stars=1.0, milky=0.0,
              haze=0.45, haze_color="#2a2a5c", mist=0.28, mist_color="#30366c", hill_color="#070a1a",
              dust=0.55, dust_color="#ffe2a8", dust_color2="#ffd6b0", bokeh=0.6, clouds=0.12, sun_int=0.08,
              water="#03040e"),
    winter=dict(base="night", sky_top="#0c1236", sky_mid="#1f2a5c", sky_hor="#4a5590", stars=0.9, milky=0.0,
                haze=0.5, haze_color="#3e4884", mist=0.42, mist_color="#6670a8", hill_color="#0a0e24",
                dust=0.5, dust_color="#ffe6b8", dust_color2="#fff0dc", bokeh=0.6, clouds=0.18, sun_int=0.08,
                water="#04061a"),
    deep=dict(base="night", sky_top="#070b26", sky_mid="#121a4a", sky_hor="#323a78", stars=1.0, milky=0.0,
              haze=0.4, haze_color="#2c3470", mist=0.22, mist_color="#4a5294", hill_color="#060918",
              dust=0.55, dust_color="#ffdca0", dust_color2="#ffe8c8", bokeh=0.7, clouds=0.05, sun_int=0.05,
              water="#03040e"),
    violet=dict(base="night", sky_top="#0e0c34", sky_mid="#2a2068", sky_hor="#6a4c9c", stars=0.9, milky=0.0,
                haze=0.45, haze_color="#5a3e8c", mist=0.3, mist_color="#6c4e9c", hill_color="#0b0820",
                dust=0.6, dust_color="#ffdcae", dust_color2="#e8d0ff", bokeh=0.7, clouds=0.08, sun_int=0.05,
                water="#05040f"),
    blush=dict(base="predawn", exposure=0.85, sky_top="#1a1c52", sky_mid="#5a4486", sky_hor="#d08890", stars=0.55, milky=0.0,
               sun_az=SUN_AZ, sun_el=-3.0, sun_int=0.6, haze_color="#9a6a88", mist=0.38, mist_color="#9a7090",
               hill_color="#120e24", water="#08061a", rays=0.2, dust_color="#ffdcae", dust_color2="#ffc8c0"),
    dawn=dict(base="dawn", sky_top="#26347a", sky_mid="#8a68ac", sky_hor="#ec9a88", sun_az=SUN_AZ, sun_el=1.5,
              sun_int=0.85, sun_glow=0.6, stars=0.2, milky=0.0, haze=0.4, haze_color="#b87888", mist=0.22,
              mist_color="#c08890", exposure=0.82, hill_color="#3a2c50", water="#1a1430", rays=0.6, clouds=0.42,
              dust_color="#fff0d0", dust_color2="#ffd0c0"),
    spring=dict(base="sunrise", sky_top="#34509c", sky_mid="#c98aa8", sky_hor="#f8b48e", sun_az=SUN_AZ,
                sun_el=3.2, sun_int=0.8, sun_glow=0.5, sun_color="#ffdcb0", stars=0.05, milky=0.0, haze=0.42,
                haze_color="#c88a90", mist=0.18, mist_color="#c89098", hill_color="#3a2a52", water="#1c1630",
                rays=0.5, clouds=0.42, dust=0.5, dust_color="#fff4dc", dust_color2="#ffd8d0", exposure=0.74),
    evening=dict(base="dusk", exposure=0.8, sky_top="#1c2460", sky_mid="#563f84", sky_hor="#d48890",
                 sun_az=SUN_AZ, sun_el=-0.5, sun_int=0.55, sun_glow=0.55, stars=0.4, milky=0.0, haze=0.3,
                 haze_color="#6a4a7c", mist=0.14, mist_color="#7a5a8a", hill_color="#1a1430", water="#0a0818",
                 rays=0.2, clouds=0.3, dust_color="#ffe8cc", dust_color2="#ffd0c8"),
)

_LOOK_KEYS = [(0.0, "morning"), (6.5, "dusk", 7.0), (15.5, "home", 7.0), (60.0, "winter", 20.0),
              (100.0, "deep", 9.0), (136.0, "violet", 9.0), (163.0, "blush", 8.0), (173.0, "dawn", 9.0),
              (204.0, "spring", 7.0), (211.5, "evening", 6.0)]


def _ripple(t):
    return float(_keys([(0.0, 0.55), (50.0, 0.5), (75.0, 0.2), (99.0, 0.0), (170.0, 0.0), (186.0, 0.4),
                        (TOTAL, 0.35)], t))


def _light_pos0(t):
    """The warm light on the scene: the home star, then the seed, then the lantern."""
    if t < T["star_land"]:
        return _v(-8.0, 3.0, -40.0) if t < T["star_lift"] else HomeStar().where(t) * 0.0 + \
            _mix(_v(-8.0, 3.0, -40.0), SEED + _v(0, 1.0, 0), _sc(T["star_lift"], T["star_land"], t))
    if T["woman"][0] < t < T["woman"][1] - 2:
        return _woman_light(t)
    if T["walk"][0] < t < T["farewell"][0]:
        return lantern(t)
    if t >= T["stem"][0]:
        return rose_top() + _v(0.0, 0.3, 0.6)
    return SEED + _v(0.0, 0.6, 0.0)


def _light_str0(t):
    swap = 1.0 - 0.7 * (_win(T["woman"][1] - 3.0, T["woman"][1] - 2.0, T["walk"][0], T["walk"][0] + 1.0, t))
    return float((0.55 + 0.5 * _win(T["hands"], T["hands"] + 1.5, 160.0, 168.0, t)) * swap)


WORLD = dict(
    looks=LOOKS,
    look=_LOOK_KEYS,
    ripple=_ripple,
    mirror=lambda t: 1.0 - 0.72 * _win(124.0, 129.0, 160.0, 170.0, t),     # snow lies on the ice
    mirror_min=lambda t: 0.55 * (1.0 - 0.72 * _win(124.0, 129.0, 160.0, 170.0, t)),
    light=dict(pos=_v(-50.0, 6.0, -380.0), color="#ffe2b0", strength=Track([(0.0, 0.0), (TOTAL, 0.0)]),
               size=0.5, rays=0.0),
    lights=[dict(pos=_light_pos0, color="#ffcf8a", strength=_light_str0, radius=4.5),
            dict(pos=lambda t: SEED + _v(0.0, 0.4, 0.0), color="#ffb860",
                 strength=lambda t: 0.35 * _sc(T["star_land"], T["star_land"] + 2.0, t)
                 * (1.0 - _sc(T["stem"][0], T["stem"][1], t)), radius=2.5)],
    arch=dict(lit=arch_lit, colors=COL, span=ARCH["span"], height=ARCH["height"], z=ARCH["z"],
              line=lambda t: 0.25 + 0.15 * _sc(168.0, 186.0, t)),
    react=dict(beat=0.12, level=0.15),
)

P3D = dict(camera=CAMERA, world=WORDS.world(WORLD), setup=_setup,
           bursts=[dict(t=WT["enc"][3] - 0.1, strength=0.9, rise=0.2, fall=0.8, color=COL[ENC]),
                   dict(t=T["bloom"][1] - 1.0, strength=0.8, rise=0.6, fall=1.4, color="#ffd8c0")],
           motion_blur=0.3)

# ------------------------------------------------------------------------------------------------ titles
TITLES = dict(signature=dict(windows=[(T["title_out1"] + 0.4, 177.0, "bl", "night"),
                                      (175.8, 212.6, "bl", "day"), (211.4, TOTAL + 5.0, "bl", "night")],
                             fade=1.2))
SONG_TITLE = dict(text="The Rose", sub="The Words of Mother’s Love  ·  Healing Concert",
                  t_in=T["title_in"], t_full=T["title_full"], t_out0=T["title_out0"], t_out1=T["title_out1"],
                  y=0.30, small_in=(15.6, 17.8))

FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Rose"], size=150, y=0.27, label_size=48, form=1e9, hold=1e9, star=1e9,
             color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Sunday, December 6", sizes=(78, 77), t0=1e9, t1=1e9 + 1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
FRAGMENTS = []
TITLE_HIT = 1e9
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
WAVES = []
