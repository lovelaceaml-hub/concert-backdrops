"""Song 11, Almighty God Who Knows the Future: the full-length concert backdrop (the finale, concert item 12).

Loaded by tools/s11_full/render.py as the engine song `songs.s11_backdrop` on the pinned Film 10 engine
(commit d928ff9) with Claude Final v1's words and people (commit f43f451), in the approved Nine Colours
Revision 3 look: warm gold glitter people, cream Cormorant serif phrases with coloured capsule labels, nine
coloured comets, warm heavenly light.

Design: project-docs/designs/11 Almighty God Who Knows the Future.md ("The Gate of Mother's Love").
Timeline on the real recording: project-docs/backdrops/s11-full/TIMELINE.md. Every time below is song
seconds (0 is the first sample of the audio file; the music is heard from 0.5 to about 260.5; the file is
268.18 s; the video holds 15 s more, calm, to 283.18).

Backdrop rules kept: a calm camera (performers stand in front), a calm bottom third, the phrases large and
in the upper middle (centre 0.345 of the height from the top) for 9 seconds or more, nothing crossing a word,
no word mirrored in the water, a small signature, no lyrics beyond the design's short fragments. Heavenly
Mother is only ever seen from behind. Every touch is between people of the same gender or parent and child.
No em dash or en dash anywhere in this file.
"""
import os
import sys
from pathlib import Path

import numpy as np

import songs.s03_original as _base

S11_HERE = Path(__file__).resolve().parent
REPO = S11_HERE.parents[1]

FPS = 30
MUSIC_LEN = 268.18
MUSIC_END = 260.5
TOTAL = MUSIC_LEN + 15.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * FPS))
_base.MUSIC_END = MUSIC_END
_base.SONG_END = MUSIC_LEN
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])          # never black
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9                     # the words are particle words in 3D
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.api import ribbon  # noqa: E402
from p3d.camera import Rig, fly  # noqa: E402

sys.path.insert(0, str(REPO / "tools/nine_colours_minor"))
import reference  # noqa: E402,F401  (Claude Final v1 as package nine_reference_p3d)
from nine_reference_p3d import words as PW  # noqa: E402
from nine_reference_p3d import master_acting  # noqa: E402,F401
from nine_reference_p3d.body import Body  # noqa: E402
from nine_reference_p3d.crowd import Crowd  # noqa: E402

AUDIO_FILE = os.environ.get("AUDIO", "")
TOTAL = MUSIC_LEN + 15.0
NFRAMES = int(round(TOTAL * FPS))
SONG_END = MUSIC_LEN
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# ---------------------------------------------------------------------------------------------- the music
# Measured on the recording (TIMELINE.md): section changes, choir accents and the big hits.
HIT = dict(call1=21.7, call2=31.3, father=40.7, glory=53.9, nations=70.7, chorus=74.7, firm=90.9,
           thanks=109.3, breath=117.0, mother=121.5, march=130.4, road=134.7, lift=155.5, forever=160.2,
           firm2=171.6, climax=179.0, gate=199.8, embrace=217.1, hands=224.2, calls=232.6, last=240.3,
           final=249.6, release=257.0)
PRAISE = [74.7, 79.3, 82.0, 85.9, 90.9]          # waves of praise across the lake (verse 1)

LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]             # website colours, words.EXPRESSIONS order
GLO = [PW.GLOWS[k] for k in LABELS]
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)
GOLD = "#ffc664"
GOLD2 = "#fff0c8"
WHITE = "#fff6e6"
SILVER = "#a9c4ff"


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


# loudness 0..1 from the engine's own features (smoothed), for breathing towers and the sky
_F = np.load(os.environ["FEATURES"])
_FT = _F["times"]
_FR = _F["rms"].astype(np.float64)
_k = np.ones(25) / 25.0
_FR = np.convolve(_FR, _k, mode="same")
_FR = (_FR - np.percentile(_FR, 5)) / max(np.percentile(_FR, 98) - np.percentile(_FR, 5), 1e-9)
_FR = np.clip(_FR, 0.0, 1.0)


def loud(t):
    return float(np.interp(t, _FT, _FR, left=0.0, right=0.0))


# ---------------------------------------------------------------------------------------------- the place
CITY_Z = -260.0                    # the heavenly city on the far shore (Mount Zion)
TER = [(0.0, 4.0, 150.0), (4.0, 8.0, 104.0), (8.0, 11.0, 66.0)]   # terraces: (y0, y1, width)
GATE_Y = 11.0                      # the gate stands on the top terrace
GATE_SPAN, GATE_H = 18.0, 15.0
SKY_ARCH = dict(c=(0.0, 0.0, CITY_Z), span=270.0, height=104.0)
GATE_ARCH = dict(c=(0.0, GATE_Y, CITY_Z + 0.5), span=GATE_SPAN, height=GATE_H)
STAR = _v(0.0, 3.0, CITY_Z)        # the warm horizon star, Mother's lamp: the first light of the city
SHORE = _v(-6.0, 0.0, -10.0)         # where Heavenly Mother gathers her children (near shore, left)
ROAD_END = _v(0.0, 0.0, CITY_Z + 18.0)
DESCEND = (186.0, 199.8)           # the arch comes down onto the gate
RISE = (HIT["final"] + 1.5, HIT["final"] + 9.5)   # the nine lights rise back into the sky


# ---------------------------------------------------------------------------------------------- camera
HOME = (_v(0.0, 2.7, 40.0), _v(0.0, 9.0, -200.0))
CAM_KEYS = [
    (0.0, _v(0.0, 9.0, 44.0), _v(0.0, 7.0, -200.0)),
    (60.0, _v(0.0, 9.0, 39.0), _v(0.0, 7.0, -200.0)),
    (100.0, _v(0.0, 8.0, 35.0), _v(0.0, 7.0, -200.0)),
    (120.0, _v(-1.5, 1.7, 13.0), _v(-3.0, 6.5, -200.0)),    # low and near Mother and her children
    (152.0, _v(-1.5, 1.8, 10.0), _v(-3.0, 6.5, -200.0)),
    (178.0, _v(0.0, 12.0, 22.0), _v(0.0, 8.0, -200.0)),     # the slow rise onto Mount Zion
    (200.0, _v(0.0, 9.5, -20.0), _v(0.0, 12.0, -220.0)),    # the slow glide toward the gate
    (240.0, _v(0.0, 8.5, -38.0), _v(0.0, 12.5, -220.0)),
    (263.0, _v(0.0, 9.0, 38.0), _v(0.0, 7.0, -200.0)),      # settle back to the home view
    (TOTAL + 1.0, _v(0.0, 9.0, 35.0), _v(0.0, 7.0, -200.0)),
]
CAMERA = Rig([fly(CAM_KEYS, ease="smooth")], fov=40.0, aperture=0.0, handheld=0.12, shutter=0.4)
_LAYOUT = CAMERA


# ---------------------------------------------------------------------------------------------- the words
READ_Y = 1.0 - 0.345               # centre of every text block, from the bottom of the frame
DEPTH = 7.0


def _width(t, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * DEPTH * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _word(t_in, t_read0, t_read1, t_out, frac, **kw):
    spec = dict(t_in=t_in, t_read0=t_read0, t_read1=t_read1, t_out=t_out, ride=(0.5, READ_Y, DEPTH),
                face="screen", width=_width(0.5 * (t_read0 + t_read1), frac), arrive="pen", nib=False,
                leave="fade")
    spec.update(kw)
    return spec


_SPECS = [
    # the song's title over the quiet introduction
    _word(1.2, 3.6, 11.2, 12.4, 0.50, label="", lines=["Almighty God", "Who Knows the Future"],
          name="title", bright=1.0, halo=1.1),
    # lyric fragments named by the design (section 8), short and readable
    _word(53.9, 55.3, 59.9, 60.6, 0.46, label="", lines=["The glory of Jerusalem"], name="glory",
          color="#ffd98a", glow="#ffb347", tint=0.55),
    _word(70.4, 71.6, 76.2, 76.9, 0.30, label="", lines=["All nations"], name="nations", color="#ffe2a8",
          glow="#f2b25e"),
    _word(80.6, 81.8, 86.3, 87.0, 0.38, label="", lines=["Joy of salvation"], name="joy", color="#ffe2a8",
          glow="#ffc664"),
    _word(95.4, 96.6, 101.2, 101.9, 0.30, label="", lines=["Mount Zion"], name="zion", color="#ffe6b8",
          glow="#e8a64a", tint=0.5, halo=1.5),
    # Gratitude at the thanks to Father (design section 7), held into the breath between the verses
    _word(109.6, 111.9, 121.6, 122.2, 0.66, expr="Gratitude", pill=True, halo=1.4),
    # Encouragement at Mother's words to trust Father and march ahead
    _word(130.4, 132.7, 142.2, 142.8, 0.62, expr="Encouragement", pill=True, halo=1.5, tint=0.55),
    # second stage of the joy fragment: joy that stays
    _word(160.0, 161.4, 168.0, 168.8, 0.42, label="", lines=["Joy of salvation", "endures forever"],
          name="forever", color="#ffe6b8", glow="#ffc664", halo=1.5),
    # the organisers' final message, on the calm hold after the music (not lyrics)
    _word(261.5, 264.3, TOTAL + 5.0, TOTAL + 6.0, 0.54, label="",
          lines=["With gratitude and hope,", "let us move forward together."], name="closing",
          color="#fff0d2", glow="#ffc664", bright=1.05, halo=1.25),
]


def _clean_leave(t, info):
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)


WORDS = PW.Words(_SPECS, camera=_LAYOUT, reflect=False, drive=_clean_leave)
FLY_TO_STAR = [(GRAT, 121.6, 123.4, "#ffd08a"), (ENC, 142.2, 144.0, "#c7a6ff")]


def _word_boxes(t, cam):
    boxes = []
    for word in WORDS:
        if word.t_in - 0.3 <= t <= word.t_out + 0.3:
            x0, x1, y0, y1, front, *_ = PW.screen_box(word, cam, t)
            if front:
                boxes.append((x0 - 0.03, x1 + 0.03, y0 - 0.05, y1 + 0.05))
    return boxes


class Clear:
    """Any point set, dimmed to almost nothing inside the box of a word on screen: nothing crosses a word."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner
        self.static = False

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1.0

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = _word_boxes(t, cam)
        out = []
        for b in got if isinstance(got, (list, tuple)) else [got]:
            if b is None:
                continue
            if boxes:
                b = dict(b)
                p = np.asarray(b["pos"]).reshape(-1, 3)
                xy, z = cam.project(p)
                gain = np.ones(len(p))
                end = None
                if b.get("pos2") is not None:
                    end, _ = cam.project(np.asarray(b["pos2"]).reshape(-1, 3))
                for u in (np.linspace(0, 1, 7) if end is not None else [0.0]):
                    q = xy if end is None else xy * (1 - u) + end * u
                    for x0, x1, y0, y1 in boxes:
                        dx = np.minimum(q[:, 0] - x0, x1 - q[:, 0])
                        dy = np.minimum(q[:, 1] - y0, y1 - q[:, 1])
                        f = np.clip(np.minimum(dx, dy) / 0.03 + 0.5, 0, 1)
                        gain = np.minimum(gain, 1 - 0.97 * f * (z > 0))
                b["alpha"] = np.asarray(b.get("alpha", 1.0)) * gain
                if "alpha2" in b:
                    b["alpha2"] = np.asarray(b["alpha2"]) * gain
            out.append(b)
        return out


# ---------------------------------------------------------------------------------------------- the arch
def _lerp(a, b, u):
    return np.asarray(a, np.float64) * (1.0 - u) + np.asarray(b, np.float64) * u


def arch_geom(t):
    """(centre, span, height, light scale) of the arch of nine lights at t: in the sky, down onto the gate
    at the climax, back up into the sky on the release."""
    d = _sc(*DESCEND, t) * (1.0 - _sc(*RISE, t))
    c = _lerp(SKY_ARCH["c"], GATE_ARCH["c"], d)
    span = float(_lerp(SKY_ARCH["span"], GATE_ARCH["span"], d))
    h = float(_lerp(SKY_ARCH["height"], GATE_ARCH["height"], d))
    return c, span, h, 1.0 - 0.25 * d


def arch_pos(t, u=None):
    c, span, h, _ = arch_geom(t)
    th = np.radians(np.linspace(172.0, 8.0, 9)) if u is None else np.radians(172.0 - 164.0 * np.asarray(u))
    return np.stack([c[0] + 0.5 * span * np.cos(th), c[1] + h * np.sin(th), c[2] + 0.0 * th], axis=-1)


def _pulse(t, t0, rise=0.25, fall=1.6):
    if t < t0 - rise or t > t0 + 6 * fall:
        return 0.0
    if t < t0:
        return _sc(t0 - rise, t0, t)
    return float(np.exp(-(t - t0) / fall))


def arch_light(t):
    """Brightness of each of the nine lights at t (1 is steady)."""
    b = np.ones(9)
    for t0 in (HIT["call1"], HIT["call2"]):                 # a wave of light along the arch, star to star
        for k in range(9):
            b[k] += 0.9 * _pulse(t, t0 + 0.22 * k, 0.2, 0.7)
    for k in range(9):                                       # Father's voice: the stars ring in turn
        b[k] += 1.1 * _pulse(t, HIT["father"] + 1.2 + 0.30 * k, 0.15, 0.8)
    b[GRAT] += 2.2 * _pulse(t, FLY_TO_STAR[0][2], 0.1, 1.4)
    b[ENC] += 2.4 * _pulse(t, FLY_TO_STAR[1][2], 0.1, 1.5)
    b += 0.9 * _win(t, HIT["climax"] + 0.5, HIT["gate"], 2.5, 3.0)     # the climax: every star blazes
    b += 0.6 * _sc(RISE[0], RISE[1], t)                                # brighter than ever after the release
    b *= 1.0 + 0.10 * loud(t)
    return b


class Arch9:
    """The arch of nine lights, complete from the first frame, each in its own campaign colour: a sparkling
    core, a soft halo, sparks circling each light, a thin arc of gold dust and links between the lights."""
    wants_camera = False

    def __init__(self):
        r = np.random.default_rng(41)
        self.du = r.random(9000)
        self.dj = r.normal(size=(9000, 3))
        self.ds = r.random(9000)
        self.oa = r.random((9, 60)) * 2 * np.pi
        self.ow = (0.4 + r.random((9, 60))) * np.where(r.random((9, 60)) > 0.5, 1, -1)
        ax = r.normal(size=(9, 60, 3))
        self.ax = ax / np.linalg.norm(ax, axis=2, keepdims=True)
        self.orad = 0.7 + 0.8 * r.random((9, 60))
        self.cols = np.array([lin(c) for c in GLO])
        self.cols_core = 0.55 * self.cols + 0.45 * lin(WHITE)

    def sample(self, t):
        c, span, h, s = arch_geom(t)
        P = arch_pos(t)
        b = arch_light(t)
        size = 5.0 * s * (span / SKY_ARCH["span"]) ** 0.12
        out = []
        # the arc: dust along the half ellipse, coloured by the nearest light
        u = np.mod(self.du + 0.004 * t, 1.0)
        A = arch_pos(t, u) + self.dj * size * 0.12
        k = np.clip(np.round(u * 8.0).astype(int), 0, 8)
        fill = 0.30 + 0.70 * _win(t, DESCEND[0] - 2.0, RISE[0], 2.0, 2.0)   # the space fills with light
        out.append(dict(pos=A, size=size * (0.05 + 0.08 * self.ds), color=self.cols[k] * 0.7 + 0.3 * lin(GOLD2),
                        alpha=0.55 * fill * np.minimum(b[k], 2.0) / 2.0 + 0.10, emit=1.4, kind="spark",
                        twinkle=0.6, seed=self.ds))
        # the nine lights
        out.append(dict(pos=P, size=size * 0.55 * np.sqrt(b), color=self.cols_core, alpha=np.minimum(b, 2.5) / 2.5,
                        emit=6.0, kind="spark"))
        out.append(dict(pos=P, size=size * 4.6, color=self.cols, alpha=0.13 * np.minimum(b, 3.0), kind="soft"))
        # sparks circling each light
        ang = self.oa + self.ow * t * 0.8
        rad = self.orad * size * 0.9
        e1 = np.cross(self.ax, np.array([0.0, 0.0, 1.0]))
        e1 /= np.maximum(np.linalg.norm(e1, axis=2, keepdims=True), 1e-6)
        e2 = np.cross(self.ax, e1)
        O = P[:, None, :] + rad[..., None] * (np.cos(ang)[..., None] * e1 + np.sin(ang)[..., None] * e2)
        out.append(dict(pos=O.reshape(-1, 3), size=size * 0.05, color=np.repeat(self.cols_core, 60, axis=0),
                        alpha=np.repeat(np.minimum(b, 2.0) / 2.0, 60) * 0.8, emit=2.2, kind="spark", twinkle=0.7,
                        seed=self.ds[:540]))
        # links between neighbours
        out.append(dict(pos=P[:-1], pos2=P[1:], size=size * 0.035, color=lin(GOLD2) * 0.8,
                        alpha=0.30 + 0.40 * fill, emit=1.2, kind="line"))
        return out


# ---------------------------------------------------------------------------------------------- the city
def _city_shapes(r):
    """Points of the heavenly city on the far shore, in the plane facing the camera: terraces, towers with
    soft domes, windows, gardens, and the great arched gate (same curve as the arch when it comes down)."""
    pts, kind, fillt = [], [], []        # kind 0 terrace, 1 tower, 2 gate, 3 window, 4 garden
    for i, (y0, y1, w) in enumerate(TER):
        n = int(5200 * w / 150.0)
        x = (r.random(n) - 0.5) * w * (1.0 - 0.12 * (r.random(n)))
        y = y0 + (y1 - y0) * r.random(n)
        pts.append(np.stack([x, y, np.full(n, CITY_Z - 4.0 * i)], 1))
        kind.append(np.zeros(n))
        fillt.append(y / 26.0)
        m = int(900 * w / 150.0)                       # gardens of light along each terrace edge
        x = (r.random(m) - 0.5) * w
        pts.append(np.stack([x, np.full(m, y1) + 0.6 * r.random(m), np.full(m, CITY_Z - 4.0 * i + 2.0)], 1))
        kind.append(np.full(m, 4.0))
        fillt.append(np.full(m, y1 / 26.0))
    towers = [(-9, 23.0), (9, 23.0), (-17, 20.0), (17, 20.0), (-25, 17.0), (25, 17.0), (-31, 14.5), (31, 14.5),
              (-40, 11.5), (40, 11.5)]
    for x0, top in towers:
        base = GATE_Y if abs(x0) < 34 else 8.0
        n = 700
        x = x0 + (r.random(n) - 0.5) * 1.5
        y = base + (top - base) * r.random(n)
        pts.append(np.stack([x, y, np.full(n, CITY_Z - 9.0)], 1))
        kind.append(np.ones(n))
        fillt.append(y / 26.0)
        a = r.random(220) * np.pi                      # a soft dome on top
        pts.append(np.stack([x0 + 1.3 * np.cos(a) * np.sqrt(r.random(220)),
                             top + 1.6 * np.sin(a) * np.sqrt(r.random(220)), np.full(220, CITY_Z - 9.0)], 1))
        kind.append(np.ones(220))
        fillt.append(np.full(220, (top + 1.0) / 26.0))
    n = 2600                                            # the gate: a thick arch of pearl light
    th = r.random(n) * np.pi
    rr = 1.0 + 0.10 * (r.random(n) - 0.5)
    pts.append(np.stack([0.5 * GATE_SPAN * rr * np.cos(th), GATE_Y + GATE_H * rr * np.sin(th),
                         np.full(n, CITY_Z + 0.4)], 1))
    kind.append(np.full(n, 2.0))
    fillt.append(np.full(n, 0.0))
    for y0, y1, w in TER:                               # warm windows, as if every house waits for someone
        m = int(160 * w / 150.0)
        x = (r.random(m) - 0.5) * w * 0.9
        pts.append(np.stack([x, y0 + 0.3 + (y1 - y0 - 0.6) * r.random(m), np.full(m, CITY_Z + 0.8)], 1))
        kind.append(np.full(m, 3.0))
        fillt.append((y0 + 1.0) / 26.0 + np.zeros(m))
    return np.concatenate(pts), np.concatenate(kind), np.concatenate(fillt)


FILL = (61.0, 69.5)      # "fulfilled": the city fills with gold from the bottom up


class City:
    """The city: a faint silver promise from the first frame, catching the dawn at the glory (gate first,
    then the towers), filling with gold from the bottom up at the fulfilment, breathing with the music."""

    def __init__(self):
        r = np.random.default_rng(11)
        self.p, self.kind, self.f = _city_shapes(r)
        self.s = r.random(len(self.p))
        self.j = r.normal(size=self.p.shape) * 0.08
        self.n = len(self.p)

    def sample(self, t):
        L = loud(t)
        p = self.p + self.j
        tower = self.kind == 1
        breath = 1.0 + 0.06 * L * (self.p[:, 1] - GATE_Y) / 12.0
        p = p.copy()
        p[tower, 1] = GATE_Y + (p[tower, 1] - GATE_Y) * breath[tower]
        promise = 0.06 + 0.12 * max(_pulse(t, HIT["call1"], 0.3, 1.2), _pulse(t, HIT["call2"], 0.3, 1.2),
                                    _pulse(t, HIT["father"] + 0.8, 0.3, 1.5))
        # the glory: gate first, then the tallest towers catch the light
        catch = np.where(self.kind == 2, _sc(53.9, 55.5, t),
                         np.where(tower, _ss(54.5 + 2.5 * (1.0 - self.f), 56.5 + 2.5 * (1.0 - self.f), t), 0.0))
        fill = _ss(FILL[0] + (FILL[1] - FILL[0]) * self.f, FILL[0] + (FILL[1] - FILL[0]) * self.f + 1.2, t)
        gold = np.maximum(fill, 0.7 * catch)
        silver = lin(SILVER)
        g1 = lin(GOLD)
        g2 = lin(GOLD2)
        warm = g1[None, :] * (1.0 - 0.5 * self.s[:, None]) + g2[None, :] * 0.5 * self.s[:, None]
        col = silver[None, :] * (1.0 - gold)[:, None] + warm * gold[:, None]
        al = promise * (1.0 - gold) + (0.30 + 0.15 * L) * gold
        win = self.kind == 3
        col[win] = lin("#ffb35c")
        al = np.where(win, al * (0.6 + 0.6 * fill), al)
        gate = self.kind == 2
        al = np.where(gate, al * (1.0 + 0.3 * _win(t, HIT["gate"], 300.0, 3.0, 1.0)), al)
        behind = (np.abs(self.p[:, 0]) < 14.0) & (self.p[:, 1] > 6.0)
        al = np.where(behind, al * (1.0 - 0.55 * _win(t, HIT["gate"] + 3.0, HIT["final"] - 1.0, 2.0, 2.0)), al)
        # the whole city glows a little less behind the words while they are read, more at the climax
        lift = (1.0 - 0.4 * _win(t, HIT["mother"], WALK[1], 2.0, 4.0)) * (1.0 + 0.15 * _win(t, HIT["climax"], 250.0, 4.0, 6.0))
        size = np.where(self.kind == 3, 0.55, np.where(self.kind == 4, 0.30, 0.42)) * (0.6 + 0.8 * self.s)
        out = [dict(pos=p, size=size, color=col, alpha=np.clip(al * lift, 0, 1.0), emit=0.9 + 0.4 * gold,
                    kind="spark", twinkle=0.35, seed=self.s)]
        # a soft glow round the gate and city once filled
        g = _sc(FILL[0], FILL[1], t)
        out.append(dict(pos=_v(0.0, 10.0, CITY_Z - 10.0)[None, :], size=150.0, color=lin("#ffcf8a"),
                        alpha=0.02 * (0.3 + g) * (1.0 + L), kind="soft"))
        return out


class GateLight:
    """Inside the gate: the light of heaven beyond it, from when the gate opens (soft white gold), with a
    river of light flowing from beneath the gate down into the lake once the city is filled."""

    def __init__(self):
        r = np.random.default_rng(12)
        n = 3500
        th = r.random(n) * np.pi
        rad = np.sqrt(r.random(n))
        self.p = np.stack([0.5 * GATE_SPAN * 0.92 * rad * np.cos(th), GATE_Y + GATE_H * 0.92 * rad * np.sin(th),
                           np.full(n, CITY_Z - 1.0)], 1)
        self.s = r.random(n)
        m = 2400
        self.ru = r.random(m)
        self.rs = r.random(m)
        self.rj = r.normal(size=(m, 2))

    def sample(self, t):
        out = []
        o = _win(t, HIT["gate"], 300.0, 2.5, 1.0)
        if o > 0.0:
            out.append(dict(pos=self.p, size=0.6 + 0.6 * self.s, color=lin("#ffe6b4"), alpha=0.06 * o * (1.0 - 0.6 * _win(t, HIT["gate"] + 3.0, HIT["final"] - 1.0, 2.0, 2.0)), emit=1.2,
                            kind="soft"))
        g = _sc(FILL[0] + 4.0, FILL[1] + 3.0, t)
        if g > 0.0:            # the river of light from beneath the gate down the mountain into the lake
            u = np.mod(self.ru + 0.05 * t, 1.0)
            z = CITY_Z + 2.0 + 60.0 * u
            x = 2.2 * self.rj[:, 0] * (0.4 + u)
            y = np.maximum(GATE_Y * (1.0 - u * 2.2), 0.05)
            out.append(dict(pos=np.stack([x, y, z], 1), size=0.35 + 0.4 * self.rs, color=lin("#ffd890"),
                            alpha=0.6 * g * (1.0 - u), emit=1.6, kind="spark", twinkle=0.5, seed=self.rs))
        return out or None


# ---------------------------------------------------------------------------------------------- rivers and road
def _river_path(side, u):
    """The riverbeds: from the far left or right edge of the lake to the foot of the city. u 0..1."""
    u = np.asarray(u, np.float64)
    x0, z0 = 175.0 * side, -35.0
    x1, z1 = 22.0 * side, CITY_Z + 22.0
    xm, zm = 105.0 * side, -150.0
    x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * xm + u * u * x1
    z = (1 - u) ** 2 * z0 + 2 * (1 - u) * u * zm + u * u * z1
    return np.stack([x, np.full_like(u, 0.08), z], -1)


RIVER_HUES = ["#5fd0c8", "#f08aa8", "#f2b25e", "#7aa8ff", "#7ad08a"]
RIVERS_ON = (64.0, 70.7)                 # the riverbeds fill
NINE_HUES_ON = HIT["lift"]               # from the second lift the crowds come in all nine colours


class Rivers:
    """Streams of light from every land: the riverbeds faint from the first frame, filling with flowing
    lights of many soft colours that warm to gold near the mountain."""

    def __init__(self):
        r = np.random.default_rng(13)
        self.n = 5000
        self.u = r.random(self.n)
        self.side = np.where(r.random(self.n) > 0.5, 1.0, -1.0)
        self.j = r.normal(size=(self.n, 3)) * np.array([3.0, 0.0, 3.0])
        self.s = r.random(self.n)
        self.hue = r.integers(0, 5, self.n)
        self.nine = r.integers(0, 9, self.n)
        self.speed = 0.010 + 0.006 * r.random(self.n)
        self.cs = np.array([lin(c) for c in RIVER_HUES])
        self.c9 = np.array([lin(c) for c in COL])

    def sample(self, t):
        on = _sc(RIVERS_ON[0], RIVERS_ON[1], t)
        promise = 0.035 * (1.0 - on)
        u = np.mod(self.u + self.speed * t, 1.0)
        front = (t - RIVERS_ON[0]) / (RIVERS_ON[1] - RIVERS_ON[0])        # the filling runs toward the city
        filled = np.clip((front - u) / 0.15 + 0.5, 0.0, 1.0) if on < 1.0 else np.ones(self.n)
        p = _river_path(1.0, u)
        p[:, 0] = p[:, 0] * self.side
        p = p + self.j * (0.6 + 0.6 * (1.0 - u))[:, None]
        nine = _sc(NINE_HUES_ON, NINE_HUES_ON + 4.0, t)
        base = self.cs[self.hue] * (1.0 - nine) + self.c9[self.nine] * nine
        warm = _ss(0.55, 0.95, u)[:, None]
        col = base * (1.0 - warm) + lin(GOLD) * warm
        L = loud(t)
        al = (promise + (0.22 + 0.12 * L) * filled * on) * (0.5 + 0.5 * self.s)
        al *= (0.25 + 0.75 * (1.0 - u)) * (1.0 - 0.5 * _sc(RISE[0], MUSIC_END, t)) * (1.0 - 0.75 * _win(t, HIT["mother"], WALK[1], 2.0, 4.0))
        size = (0.6 + 0.8 * self.s) * (0.9 + 1.2 * (1.0 - u))
        return dict(pos=p, size=size, color=col, alpha=al, emit=1.0, kind="spark", twinkle=0.5, seed=self.s)


ROAD_FILL = (HIT["march"], HIT["road"])
ROAD_BLAZE = (151.0, 153.0)


def _road_point(u):
    u = np.asarray(u, np.float64)[..., None]
    return SHORE[None, :] * (1 - u) + ROAD_END[None, :] * u + np.array([0.0, 0.04, 0.0])


class Road:
    """The straight road across the lake from the near shore to the mountain: a faint silver line from the
    first frame; at Mother's raised hand it unrolls in violet gold from her feet to the mountain; it blazes
    gold when the walkers reach the foot of the mountain and carries the light of the open gate."""

    def __init__(self):
        r = np.random.default_rng(15)
        self.n = 4000
        self.u = r.random(self.n) ** 1.4
        self.w = (r.random(self.n) - 0.5)
        self.s = r.random(self.n)

    def sample(self, t):
        u = self.u
        front = _ss(ROAD_FILL[0], ROAD_FILL[1], t)
        on = np.clip((front * 1.15 - u) / 0.08, 0.0, 1.0)
        blaze = _sc(*ROAD_BLAZE, t)
        gate = _win(t, HIT["gate"], 252.0, 3.0, 6.0)
        p = _road_point(u)
        width = 1.6 + 3.0 * u
        p[:, 0] += self.w * width
        vio = lin("#b98cff") * 0.6 + lin(GOLD) * 0.4
        col = vio[None, :] * (1.0 - blaze) + lin(GOLD)[None, :] * blaze
        col = np.broadcast_to(col, (self.n, 3)).copy()
        al = 0.03 + (0.16 + 0.16 * blaze + 0.22 * gate) * on
        al *= 1.0 - 0.6 * _sc(RISE[0], MUSIC_END, t)
        # keep the near end (the bottom of the picture) quieter
        al *= (0.35 + 0.65 * _ss(0.0, 0.18, u)) * (1.0 - 0.85 * _sc(ROAD_BLAZE[1], ROAD_BLAZE[1] + 6.0, t) * (1.0 - _ss(0.15, 0.35, u)))
        return dict(pos=p, size=0.10 + 0.30 * self.s * (0.3 + u), color=col, alpha=al, emit=1.1, kind="spark",
                    twinkle=0.6, seed=self.s)


# ---------------------------------------------------------------------------------------------- moments of light
class Waves:
    """Golden waves of praise rolling out from the mountain across the lake at each choral accent (verse 1),
    fading before the calm near water; from 'endures forever' slow rings that keep circling the mountain."""

    def __init__(self):
        r = np.random.default_rng(16)
        self.a = r.random(1800) * 2 * np.pi
        self.s = r.random(1800)

    def sample(self, t):
        out = []
        c = _v(0.0, 0.1, CITY_Z + 20.0)
        for t0 in PRAISE + [HIT["father"]]:
            age = t - t0
            if not 0.0 <= age <= 9.0:
                continue
            R = 15.0 + 32.0 * age
            p = c + np.stack([R * np.sin(self.a), np.zeros_like(self.a), R * np.cos(self.a)], 1)
            near = np.clip((p[:, 2] + 70.0) / 50.0, 0.0, 1.0)       # gone before the calm near lake
            al = 0.75 * np.exp(-age / 3.5) * (1.0 - near) * (1.0 if t0 != HIT["father"] else 0.6)
            out.append(dict(pos=p, size=0.6 + 0.6 * self.s, color=lin(GOLD), alpha=al, emit=1.6, kind="spark",
                            twinkle=0.6, seed=self.s))
        on = _win(t, HIT["forever"], RISE[0], 2.0, 4.0)
        if on > 0.0:
            for i, R0 in enumerate((45.0, 75.0, 105.0)):
                rot = self.a + (0.05 + 0.02 * i) * t * (1 if i % 2 == 0 else -1)
                R = R0 + 3.0 * np.sin(t * 0.6 + i)
                p = c + np.stack([R * np.sin(rot), np.zeros_like(rot), R * np.cos(rot)], 1)
                near = np.clip((p[:, 2] + 90.0) / 40.0, 0.0, 1.0)
                out.append(dict(pos=p, size=0.5 + 0.6 * self.s, color=lin(GOLD), alpha=0.45 * on * (1.0 - near),
                                emit=1.5, kind="spark", twinkle=0.6, seed=self.s))
        return out or None


class Rays:
    """Father's voice: one deep pulse of warm light rolling out from the horizon star across the sky like the
    sound of a great bell (a widening shell of light over the far world)."""

    def __init__(self):
        r = np.random.default_rng(17)
        a = r.random(2400) * np.pi
        self.d = np.stack([np.cos(a), np.sin(a), np.zeros_like(a)], 1) + r.normal(size=(2400, 3)) * 0.012
        self.s = r.random(2400)

    def sample(self, t):
        age = t - HIT["father"]
        if not 0.0 <= age <= 7.0:
            return None
        R = 12.0 + 45.0 * age
        p = STAR + self.d * R * np.array([1.4, 1.0, 1.0])
        return dict(pos=p, size=0.5 + 0.6 * self.s, color=lin("#ffd9a0"), alpha=0.5 * np.exp(-age / 2.4),
                    emit=1.5, kind="spark", twinkle=0.4, seed=self.s)


class Sparks:
    """Lights rising from the people on the mountain: the thanks to Father (thousands at once), the lifted
    hands of the coda, and the soft rain of sparks rising as the crowds dissolve after the last chord."""

    def __init__(self):
        r = np.random.default_rng(18)
        self.n = 3000
        self.x = (r.random(self.n) - 0.5) * 130.0
        self.y0 = 3.0 + 9.0 * r.random(self.n)
        self.z = CITY_Z + 6.0 + 10.0 * r.random(self.n)
        self.s = r.random(self.n)
        self.ph = r.random(self.n)

    def _rise(self, t, t0, t1, strength, col):
        o = _win(t, t0, t1, 1.5, 2.5)
        if o <= 0.0:
            return None
        life = 6.0
        age = np.mod((t - t0) + self.ph * life, life)
        y = self.y0 + 3.0 * age
        p = np.stack([self.x + 1.5 * np.sin(0.7 * age + 6 * self.s), y, self.z], 1)
        al = strength * o * np.sin(np.pi * age / life) * (0.4 + 0.6 * self.s)
        return dict(pos=p, size=0.45 + 0.4 * self.s, color=lin(col), alpha=al, emit=2.0, kind="spark",
                    twinkle=0.7, seed=self.s)

    def sample(self, t):
        out = [self._rise(t, 100.5, 117.0, 0.9, "#ffd890"), self._rise(t, HIT["hands"], 236.0, 0.35, "#ffd890"),
               self._rise(t, HIT["final"], MUSIC_END + 4.0, 1.0, "#ffe2a8")]
        out = [o for o in out if o is not None]
        return out or None


class StarFlights:
    """After each expression is read its light flies up as one bright point to its star in the arch."""

    def sample(self, t, cam=None):
        out = []
        for k, t0, t1, col in FLY_TO_STAR:
            if not t0 <= t <= t1 + 0.1:
                continue
            a = PW.place(_LAYOUT, t0, 0.5, READ_Y, DEPTH)
            b = arch_pos(t1)[k]
            n = 30
            us = np.clip(np.linspace(-0.25, 0.0, n) + (t - t0) / (t1 - t0), 0.0, 1.0)
            e = us * us * (3 - 2 * us)
            mid = 0.5 * (np.asarray(a) + b) + np.array([0.0, 40.0, 0.0])
            pts = ((1 - e) ** 2)[:, None] * a + (2 * (1 - e) * e)[:, None] * mid + (e * e)[:, None] * b
            al = np.linspace(0.0, 1.0, n) * (1.0 - _sc(t1 - 0.15, t1 + 0.1, t))
            out.append(ribbon(pts, width=np.linspace(0.02, 0.9, n) * (0.2 + 0.8 * e[-1]) * (1 + 3 * e),
                              color=lin(col), alpha=al, emit=2.5))
            out.append(dict(pos=pts[-1:], size=0.12 + 3.0 * e[-1], color=lin(WHITE) * 0.5 + lin(col) * 0.5,
                            alpha=al[-1:], emit=6.0, kind="spark"))
        return out or None

    wants_camera = True


class Glows:
    """The calm after the music: nine small steady glows on the lake, one beneath each star, each mirrored:
    the words practised on earth reflected in heaven."""

    def sample(self, t):
        o = _sc(RISE[1] - 2.0, RISE[1] + 4.0, t)
        if o <= 0.0:
            return None
        P = arch_pos(t).copy()
        P[:, 1] = 0.25
        P[:, 2] = -150.0
        P[:, 0] *= 0.62
        on = np.array([_sc(RISE[1] - 2.0 + 0.5 * k, RISE[1] + 0.5 * k, t) for k in range(9)])
        cols = np.array([lin(c) for c in GLO])
        breathe = 1.0 + 0.12 * np.sin(t * 0.9 + np.arange(9))
        return [dict(pos=P, size=2.4 * breathe, color=cols * 0.6 + 0.4 * lin(WHITE), alpha=0.8 * on, emit=3.0,
                     kind="spark"),
                dict(pos=P, size=14.0, color=cols, alpha=0.10 * on, kind="soft")]


# ---------------------------------------------------------------------------------------------- the nine comets
def _comet_head(k, t):
    """Where comet k is at t, or None. Three flights: (a) nations, 63 to 74: from its star they swoop down to
    the far edges of the lake and run along the rivers to the foot of the mountain (the streams are theirs);
    (b) the second lift, 155.5 to 176: a wide slow ring round the mountain; (c) the release: following each
    light as it rises back into the sky."""
    a0, a1 = 62.5 + 0.35 * k, 73.0 + 0.35 * k
    if a0 <= t <= a1 + 0.6:
        u = _sc(a0, a1, t)
        side = -1.0 if k < 4 else (1.0 if k > 4 else (-1.0))
        star = arch_pos(a0)[k]
        src = _river_path(1.0, 0.0) * np.array([side, 1, 1]) + np.array([0, 25.0, 0])
        if u < 0.45:
            e = u / 0.45
            mid = 0.5 * (star + src) + np.array([0.0, 30.0, 60.0])
            return (1 - e) ** 2 * star + 2 * (1 - e) * e * mid + e * e * src
        e = (u - 0.45) / 0.55
        p = _river_path(1.0, e) * np.array([side, 1, 1])
        p[1] += 25.0 * (1 - e) ** 2 + 2.0
        return p
    b0, b1 = HIT["lift"] + 0.25 * k, 246.0
    if b0 - 1.0 <= t <= b1 + 1.0:
        ang = 2 * np.pi * k / 9.0 + 0.08 * (t - HIT["lift"])
        R = 80.0 + 10.0 * np.sin(0.3 * t + k)
        y = 48.0 + 8.0 * np.sin(0.21 * t + 1.7 * k)
        return _v(R * np.sin(ang), y, CITY_Z + 30.0 + 0.55 * R * np.cos(ang))
    return None


def _comet_alpha(k, t):
    a0, a1 = 62.5 + 0.35 * k, 73.0 + 0.35 * k
    a = _sc(a0, a0 + 0.6, t) * (1.0 - _sc(a1 - 0.4, a1 + 0.6, t))
    b0 = HIT["lift"] + 0.25 * k
    b = _sc(b0 - 1.0, b0 + 0.5, t) * (1.0 - _sc(243.0, 246.5, t))
    return max(a, b)


class Comets:
    """The nine ribbons of colour of Revision 3 (white-hot core, coloured glow, head bloom, shed sparks),
    flown slowly here: performers stand in front."""

    def __init__(self):
        r = np.random.default_rng(10)
        self.sp = r.random((9, 120, 4))

    def sample(self, t):
        out = []
        for k in range(9):
            a = _comet_alpha(k, t)
            if a <= 0.0 or _comet_head(k, t) is None:
                continue
            n, tail = 40, 2.4
            ts = np.linspace(t - tail, t, n)
            pts = [_comet_head(k, float(x)) for x in ts]
            ok = [i for i, p in enumerate(pts) if p is not None]
            if len(ok) < 3:
                continue
            pts = np.array([pts[i] for i in ok])
            m = len(pts)
            kk = np.linspace(0.0, 1.0, m)
            c = lin(GLO[k])
            core = 0.35 * c + 0.65 * lin(WHITE)
            w = 2.2
            out.append(ribbon(pts, width=w * (0.12 + 0.88 * kk), color=c * 1.1, alpha=a * 0.55 * kk, emit=1.6))
            out.append(ribbon(pts, width=w * 0.22 * (0.15 + 0.85 * kk), color=core, alpha=a * 0.95 * kk, emit=2.6))
            head = pts[-1:]
            out.append(dict(pos=head, size=w * 0.7, color=core, alpha=a, emit=7.0, kind="spark"))
            out.append(dict(pos=head, size=w * 5.0, color=c, alpha=a * 0.16, kind="soft"))
            sp = self.sp[k]
            f = np.mod(sp[:, 0] + t * (0.9 + 0.4 * sp[:, 1]), 1.0)
            idx = f * (m - 1)
            i0 = np.floor(idx).astype(int)
            i1 = np.minimum(i0 + 1, m - 1)
            fr = (idx - i0)[:, None]
            base = pts[i0] * (1.0 - fr) + pts[i1] * fr
            drift = (sp[:, 1:4] - 0.5) * (w * 3.0) * (1.0 - f)[:, None]
            out.append(dict(pos=base + drift, size=w * (0.10 + 0.12 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                            alpha=a * 0.9 * f ** 1.5, emit=2.0, kind="spark", twinkle=0.6, seed=sp[:, 3]))
        return out or None


# ---------------------------------------------------------------------------------------------- the people
LOOK = dict(name="glitter", seams=0.6)
MOTHER_SHOW = (HIT["mother"] - 0.5, 153.5)
WALK = (HIT["road"] + 7.8, 151.0)          # they step onto the road once the Encouragement is read
WALK_END = _v(-5.0, 0.0, -24.0)


def _toward_city(p):
    d = ROAD_END - np.asarray(p)
    return float(np.degrees(np.arctan2(d[0], d[2])))


def _walk_keys(offset):
    a = SHORE + np.asarray(offset)
    b = WALK_END + np.asarray(offset) * 0.8
    return [(0.0, (float(a[0]), float(a[2]))), (WALK[0], (float(a[0]), float(a[2]))),
            (WALK[1], (float(b[0]), float(b[2]))), (TOTAL, (float(b[0]), float(b[2])))]


_PEOPLE = {}


def people():
    """Heavenly Mother (only from behind) with a child and a young woman on the near shore, left (2:01 to
    2:33): she lays a hand on the young woman's shoulder (warming light), raises her hand toward the city,
    the road unrolls, they walk out on it toward the city and dissolve into sparks that run ahead. And at the
    open gate (3:22 to 3:58): Mother from behind with her arms open, receiving her children home."""
    if _PEOPLE:
        return _PEOPLE
    face = _toward_city(SHORE)
    common = dict(look=LOOK, show=MOTHER_SHOW, fade=0.6,
                  effects=[dict(kind="form", t=HIT["mother"] - 0.5, dur=3.0),
                           dict(kind="dissolve", t=WALK[1], dur=2.6)])
    woman_at = _walk_keys((1.15, 0.0, 0.55))
    child_at = _walk_keys((-0.75, 0.0, 0.45))
    woman = Body("woman", at=woman_at, facing=face, hair="covered", seed=21.0, points=42000,
                 color="#f2a640", color2="#ffdc96", bright=2.4, garment="dress",
                 motion=[(0.0, "stand"), (WALK[0], "walk", dict(speed=0.7)), (WALK[1], "stand")],
                 gesture=[(HIT["mother"] + 2.4, HIT["mother"] + 6.8, "bow")], **common)
    _PEOPLE["woman"] = woman
    mother = Body("woman", at=_walk_keys((0.0, 0.0, 0.0)), facing=face, garment="robe", veil=dict(length=1.5),
                  seed=20.0, points=70000, color="#f6b552", color2="#ffe6b0", bright=2.6, height=1.70,
                  motion=[(0.0, "stand"), (WALK[0], "walk", dict(speed=0.7)), (WALK[1], "stand")],
                  gesture=[(HIT["mother"] + 3.2, HIT["mother"] + 7.6, "hand_on_shoulder",
                            dict(to=lambda t: woman.where(t, "shoulder.L"), side="R")),
                           (HIT["march"] - 0.4, HIT["road"] + 6.0, "reach",
                            dict(to=(0.0, 30.0, CITY_Z), side="R"))],
                  **common)
    child = Body("child", at=child_at, facing=face, seed=22.0, points=30000, color="#ffc664", color2="#fff0c8",
                 bright=2.4, motion=[(0.0, "stand"), (WALK[0], "walk", dict(speed=0.8)), (WALK[1], "stand")],
                 gesture=[(HIT["march"] + 0.6, HIT["road"] + 5.0, "look_up")], **common)
    _PEOPLE["mother"] = mother
    _PEOPLE["child"] = child
    gate = Body("woman", at=(0.0, GATE_Y, CITY_Z + 7.0), facing=180.0, garment="robe", veil=dict(length=1.5),
                seed=23.0, points=110000, color="#f6b552", color2="#ffe6b0", bright=3.0, scale=9.0, size=4.0,
                motion="stand", gesture=[(HIT["gate"] + 6.5, 238.0, "open_arms")], look=LOOK,
                show=(HIT["gate"] + 3.0, HIT["final"] - 1.0), fade=1.5,
                effects=[dict(kind="form", t=HIT["gate"] + 3.0, dur=3.5)])
    _PEOPLE["gate_mother"] = gate
    return _PEOPLE


class Lit:
    """A point set with an extra time gain (crowds brightening on 'firm', fading out)."""

    def __init__(self, inner, g):
        self.inner, self.g = inner, g
        for k in ("static", "dome"):
            if hasattr(inner, k):
                setattr(self, k, getattr(inner, k))

    @property
    def wants_camera(self):
        return getattr(self.inner, "wants_camera", False)

    def gain(self, t):
        base = self.inner.gain(t) if hasattr(self.inner, "gain") else 1.0
        return base * self.g(t)

    def sample(self, t, cam=None):
        if getattr(self.inner, "wants_camera", False):
            return self.inner.sample(t, cam)
        return self.inner.sample(t)


def _ridge_places():
    r = np.random.default_rng(31)
    pts = []
    for y0, y1, w in TER:
        n = int(60 * w / 150.0)
        x = np.linspace(-0.47 * w, 0.47 * w, n) + r.normal(size=n) * 0.4
        keep = np.abs(x) > 0.5 * GATE_SPAN + 2.0 if y1 >= GATE_Y else np.ones(n, bool)
        x = x[keep]
        pts.append(np.stack([x, np.full(len(x), y1), np.full(len(x), CITY_Z + 6.0 - 4.0 * TER.index((y0, y1, w)))],
                            1))
    return np.concatenate(pts)


def crowds():
    ridge = Crowd(places=_ridge_places(), facing=0.0, kinds=("raise",), people=dict(woman=1, man=1, elder=0.3,
                  child=0.25), start=dict(t=HIT["firm"] - 1.0, center=(0.0, CITY_Z), speed=30.0),
                  act=dict(t=HIT["hands"], dur=2.0), act_end=HIT["final"] - 4.0, until=HIT["final"] + 1.5,
                  fade=1.5, points=2200, scale=(2.6, 3.0), color="#f2b865", color2="#ffe6b8", bright=1.25, glints=0.0, twinkle=0.3,
                  seed=3.0)
    r = np.random.default_rng(32)
    walkers = []
    for side in (-1.0, 1.0):
        u = np.sort(0.45 + 0.5 * r.random(26))
        P = _river_path(1.0, u) * np.array([side, 1, 1])
        ahead = _river_path(1.0, np.minimum(u + 0.05, 1.0)) * np.array([side, 1, 1])
        face = np.degrees(np.arctan2(ahead[:, 0] - P[:, 0], ahead[:, 2] - P[:, 2]))
        P[:, 1] = 0.0
        walkers.append(Crowd(places=P[:, [0, 2]], facing=face, kinds=("walk", "child_run", "walk"),
                             people=dict(woman=1, man=1, elder=0.4, child=0.5),
                             start=dict(t=RIVERS_ON[1] + 2.0, dur=6.0), until=HIT["final"] - 1.0, fade=2.0,
                             walk=0.45, points=1800, scale=(2.2, 2.5), color="#f2b865", color2="#ffe6b8",
                             bright=1.2, seed=4.0 + side))
    return ridge, walkers


# ---------------------------------------------------------------------------------------------- world
LOOKS = dict(
    home=dict(base="night", sky_top="#07061a", sky_mid="#1f1236", sky_hor="#5c3448", stars=1.0, milky=0.55,
              haze=0.35, haze_color="#4a2a3a", mist=0.18, mist_color="#3a2438", water="#05040c",
              hill_color="#0a0714", sun_int=0.25, sun_el=-6.0, sun_color="#ffb48c", ripple=0.15),
    violet=dict(base="predawn", sky_hor="#b06a70", stars=0.65, ripple=0.2, haze=0.4),
    rose=dict(base="dawn", sky_top="#14204c", sky_mid="#5a3678", sky_hor="#e08068", sun_el=-1.5, rays=0.35,
              ripple=0.25, haze=0.45, mist=0.3),
    gold=dict(base="sunrise", sky_top="#16245a", sky_mid="#6e4672", sky_hor="#e0904e", sun_el=-0.6,
              sun_disc=0.0, rays=0.45, stars=0.08, ripple=0.25, sun_int=0.75, haze=0.4, mist=0.2),
    hush=dict(base="golden", sky_top="#16306c", sky_mid="#3a5a94", sky_hor="#c8a888", sun_el=-0.5, sun_disc=0.0,
              sun_int=0.35, rays=0.08, clouds=0.1, ripple=0.03, haze=0.15, mist=0.08, water="#040a1c",
              mirror=0.75),
    morning=dict(base="golden", sky_top="#102864", sky_mid="#25488a", sky_hor="#d0a070", sun_el=-0.3,
                 sun_disc=0.0, sun_int=0.4, rays=0.12, clouds=0.08, ripple=0.06, haze=0.12, mist=0.06,
                 water="#040a1c", mirror=0.7),
    bright=dict(base="golden", sky_top="#1c4488", sky_mid="#4a76b8", sky_hor="#ecc896", sun_el=0.2,
                sun_disc=0.0, sun_int=0.65, rays=0.3, clouds=0.05, ripple=0.12, haze=0.3, mist=0.18,
                water="#0a1830"),
    glory=dict(base="golden", sky_top="#1c4c98", sky_mid="#4a7cc0", sky_hor="#f0c890", sun_el=3.6, sun_disc=2.0,
               sun_int=0.5, sun_size=1.0, sun_glow=0.35, rays=0.25, clouds=0.0, ripple=0.12, sun_color="#fff0d0",
               haze=0.05, mist=0.04, water="#081830", exposure=0.9, hill_color="#1e2c52",
               haze_color="#6a88b8"),
    evening=dict(base="dusk", sky_top="#120c2a", sky_mid="#3a2244", sky_hor="#b0684e", stars=0.55, sun_el=-3.0,
                 sun_int=0.55, sun_color="#ffb070", haze_color="#6a3a3a", mist_color="#5a3440", ripple=0.04),
    rest=dict(base="night", sky_top="#0a0820", sky_mid="#241538", sky_hor="#6e3c44", stars=1.0, milky=0.6,
              haze=0.4, haze_color="#5a3040", mist=0.22, mist_color="#4a2a3a", water="#05040c", sun_int=0.3,
              sun_el=-6.0, sun_color="#ffb070", ripple=0.03),
)

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "home"), (44.0, "violet", 8.0), (56.0, "rose", 6.0), (76.0, "gold", 10.0),
          (119.0, "hush", 4.0), (126.0, "morning", 6.0), (HIT["lift"], "bright", 6.0),
          (HIT["gate"] + 2.0, "glory", 8.0), (MUSIC_END - 2.0, "evening", 9.0), (MUSIC_END + 9.0, "rest", 10.0)],
    sun_az=180.0,
    sun_el=Track([(0.0, -6.0), (44.0, -6.0), (56.0, -2.0), (76.0, -0.8), (HIT["gate"] - 1.0, -0.4),
                  (HIT["gate"] + 5.0, 3.0), (HIT["gate"] + 13.0, 7.5), (HIT["final"], 9.0), (MUSIC_END, 3.0), (MUSIC_END + 12.0, -6.0),
                  (TOTAL + 1.0, -6.0)]),
    light=dict(pos=tuple(STAR), color="#ffd9a8",
               strength=Track([(0.0, 0.6), (2.0, 0.9), (HIT["father"] - 0.3, 0.9), (HIT["father"] + 0.2, 1.15),
                               (HIT["father"] + 3.0, 0.9), (53.0, 0.9), (55.0, 1.4), (70.0, 1.0),
                               (HIT["gate"], 1.0), (HIT["gate"] + 4.0, 0.0), (MUSIC_END, 0.0),
                               (MUSIC_END + 10.0, 0.7), (TOTAL + 1.0, 0.7)]),
               size=0.9, rays=0.8),
    react=dict(beat=0.15, level=0.2),
)


# ---------------------------------------------------------------------------------------------- setup
def _setup(scene):
    scene.add("arch9", Arch9())
    scene.add("city", City())
    scene.add("gatelight", GateLight())
    scene.add("rivers", Clear(Rivers()))
    scene.add("road", Road())
    scene.add("waves", Waves())
    scene.add("fatherpulse", Clear(Rays()))
    scene.add("sparks", Clear(Sparks()))
    scene.add("glows", Glows())
    scene.add("comets", Clear(Comets()), reflect=False)
    scene.add("flights", StarFlights())
    ridge, walkers = crowds()
    scene.add("ridge", Lit(ridge, lambda t: 1.0 + 0.6 * _pulse(t, HIT["firm"], 0.4, 3.0)
                           + 0.5 * _pulse(t, HIT["firm2"], 0.4, 3.0)))
    for i, w in enumerate(walkers):
        scene.add(f"walkers{i}", w)
    for name, body in people().items():
        body.add(scene, name)
    WORDS.add_to(scene)
    WORDS.check(CAMERA, need_all=False)


P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=[],
    motion_blur=0.3,
)

# ---------------------------------------------------------------------------------------------- 2D layers
TITLE = dict(_base.TITLE, form=1e9, hold=1e9, star=1e9)
TAGLINE = dict(_base.TAGLINE, t0=1e9, t1=1e9 + 1)
FRAGMENTS = []
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
WAVES = []
# the small signature, bottom left, from the end of the title to the last frame (day style on bright skies)
TITLES = dict(signature=dict(windows=[(12.4, 128.0, "bl", "night"), (128.0, MUSIC_END - 1.0, "bl", "day"),
                                      (MUSIC_END - 1.0, TOTAL + 1.0, "bl", "night")], fade=0.8))
