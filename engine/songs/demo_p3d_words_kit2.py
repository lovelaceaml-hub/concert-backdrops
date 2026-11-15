"""Particle words, the directors' kit, part two (24 seconds, the 3D layer: engine/UPGRADE-HOWTO.md, X and X2).

Not a concert video: a test of the kit items that part one (demo_p3d_words_kit.py) leaves out, set to the
first 24 seconds of the song 01 promo clip (audio/promo/s01.mp3). One thing after another, cut together:

   0 to  6   a veiled woman from behind (helper BODY); the Greeting lies in a fold of her veil
             (PW.on_cloth) and moves with it; a spark someone else flies writes it (arrive="pen",
             source=...): a pen on a word bound to a moving surface; it unravels into the sky
   6 to 11   macro: an open hand (BODY, part "hand.R"); the Consideration, the size of a hand, rises from the palm
             (arrive="palm", source=the palm) and goes up as flakes
  10 to 15   the Gratitude revealed behind an edge of the song's own (gate=: a bar of light that sinks),
             turning to the camera, tilting back and rolling level over time (facing=, tilt=, roll= as
             functions of t); while it is read a ripple runs through it (drive=)
  14 to 20   three words born from other point fields (arrive="morph", carry=): the Apology from drifting
             petals ("petal"), the Concession from a flock that lands ("bird"), the Inclusiveness from
             floating lanterns ("soft")
  19 to 24   window words: the Respect a window onto clouds, then the Compliment onto a sunrise
  every word chooses its own number of points from its size on screen (n="auto", the default)

No lyrics, no faces. The engine's flat text is switched off.
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 24.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 23.8
_base.FADE = _base.Track([(0.0, 1.0), (23.3, 1.0), (23.95, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (24.0, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import lin  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.camera import Rig, dolly, hold, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

MOTHER_AT = (0.0, 30.0)                 # each stage stands far from the others
PALM_AT = np.array([40.0, 1.3, 0.0])
CENTER = (0.0, 6.0, -10.0)


def _rig(focus="target"):
    return Rig([
        orbit((MOTHER_AT[0], 1.0, MOTHER_AT[1]), radius=(1.8, 1.55), height=(1.15, 1.25), a0=170.0, a1=188.0,
              t0=0.0, t1=6.0, look=(MOTHER_AT[0], 1.08, MOTHER_AT[1]), fov=34.0, aperture=0.012, near=0.02),
        hold(PALM_AT + np.array([0.06, 0.26, 0.42]), PALM_AT + np.array([0.0, 0.12, 0.0]), 6.0, 11.0,
             drift=(0.02, 0.01, 0.01), fov=40.0, aperture=0.004, near=0.02, blend=0.0),
        orbit(CENTER, radius=40.0, height=(2.4, 3.0), a0=-6.0, a1=6.0, t0=11.0, t1=24.0,
              look=(0.0, 6.6, -10.0), fov=42.0, aperture=0.05, blend=0.0, focus=focus),
    ], blend=1.0, handheld=0.15, focus=focus)


_LAYOUT = _rig()


def _word(x, y, depth, px, t_in, t_read0, t_read1, t_out, **kw):
    tm = 0.5 * (t_read0 + t_read1)
    return dict(pos=tuple(PW.place(_LAYOUT, tm, x, y, depth)), em=PW.em_for(_LAYOUT, tm, depth, px),
                t_in=t_in, t_read0=t_read0, t_read1=t_read1, t_out=t_out, **kw)


def _people():
    from p3d.body import Body
    mother = Body("woman", at=MOTHER_AT, facing=0.0, garment="robe", veil=dict(length=1.5, wide=1.15),
                  look="glitter", color="#f2c88f", color2="#ffeccc", points=70000, show=(0.0, 6.2), fade=0.3, bright=0.45,
                  gesture=[(0.5, 30.0, "open_arms", dict(amount=0.35))], wind=(0.25, 0.0, 0.1))
    hand = Body("woman", part="hand.R", look="glitter", color="#ffcf8a", color2="#ffffff", points=50000,
                show=(5.9, 11.1), fade=0.1,
                hand=dict(side="R", at=tuple(PALM_AT), aim=(0.0, 0.25, -1.0), palm=(0.0, 1.0, 0.0), pose="open",
                          anchor="palm"))
    return mother, hand


MOTHER, HAND = _people()


def comet(t):
    """A spark that crosses the veil from left to right while it writes the word, then rises away."""
    u = (t - 0.7) / 2.4
    c = np.array([MOTHER_AT[0], 1.08, MOTHER_AT[1] - 0.35])
    if u < 1.0:
        return c + np.array([-0.38 + 0.76 * u, 0.05 * np.sin(u * 19.0), 0.0])
    return c + np.array([0.38 + 0.2 * (u - 1.0), 0.6 * (u - 1.0), 0.0])


class _Comet:
    def sample(self, t):
        if not 0.4 < t < 5.8:
            return None
        k = float(np.clip((t - 0.4) / 0.4, 0.0, 1.0) * np.clip((5.8 - t) / 0.4, 0.0, 1.0))
        tail = np.array([comet(t - 0.03 * i) for i in range(12)], np.float32)
        return [dict(pos=tail[:1], size=0.012, color=lin("#fff1d0"), alpha=k, emit=5.0, kind="spark"),
                dict(pos=tail[1:], pos2=tail[:-1], size=0.006, color=lin("#ffc890"), alpha=k * np.linspace(0.8, 0, 11),
                     alpha2=k * np.linspace(0.9, 0.05, 11), kind="ribbon")]


class _Field:
    """A drifting field of points (petals, a flock, lanterns) for a word to be born from."""

    def __init__(self, centre, size, n, kind, colors, t0, t1, seed, speed=(0.25, 0.05, 0.0), dot=0.10):
        r = np.random.default_rng(seed)
        self.p = (np.asarray(centre) + (r.random((n, 3)) - 0.5) * np.asarray(size)).astype(np.float32)
        self.s = r.random((n, 3)).astype(np.float32)
        self.kind, self.t0, self.t1, self.v, self.dot = kind, t0, t1, np.asarray(speed, np.float32), dot
        self.cols = np.stack([lin(c) for c in colors]).astype(np.float32)

    def at(self, t):
        s = self.s
        return self.p + self.v[None, :] * (t - self.t0) + 0.4 * np.stack(
            [np.sin(t * 0.7 + s[:, 0] * 6.28), 0.5 * np.sin(t * 0.9 + s[:, 1] * 6.28), np.sin(t * 0.5 + s[:, 2] * 6.28)], 1)

    def sample(self, t):
        if not self.t0 - 0.5 < t < self.t1:
            return None
        b = dict(pos=self.at(t), size=self.dot * (0.7 + 0.6 * self.s[:, 0]), color=self.cols[(self.s[:, 1] * len(self.cols)).astype(int)],
                 alpha=0.8, kind=self.kind, seed=self.s[:, 2])
        if self.kind in ("petal", "bird"):
            b["rot"] = (np.stack([self.s[:, 0] * 6.28 + t, self.s[:, 1] * 6.28 + 2 * t], 1) if self.kind == "petal"
                        else np.zeros(len(self.p), np.float32))
        return b

    def gain(self, t):
        return float(np.clip((t - self.t0 + 0.5) / 0.5, 0.0, 1.0))


class _Source:
    """The field as a source for the word (its places at t)."""

    def __init__(self, field):
        self.f = field

    def sample(self, t):
        return dict(pos=self.f.at(t))


_PETALS = _Field(PW.place(_LAYOUT, 15.0, 0.25, 0.55, 30.0), (16.0, 6.0, 6.0), 900, "petal",
                 ("#ff8fa3", "#ffb19a", "#ffd9c9"), 12.8, 16.4, 3, dot=0.30)
_FLOCK = _Field(PW.place(_LAYOUT, 16.5, 0.85, 0.70, 30.0), (10.0, 4.0, 6.0), 160, "bird", ("#fff4dc",), 14.0, 17.6,
                4, speed=(-0.6, 0.1, 0.0), dot=0.45)
_LANTERNS = _Field(PW.place(_LAYOUT, 18.0, 0.55, 0.30, 26.0), (18.0, 1.5, 8.0), 500, "soft", ("#ffcf8a", "#ffb070"),
                   14.5, 19.0, 5, speed=(0.0, 0.15, 0.0), dot=0.22)


_GRAT = PW.place(_LAYOUT, 13.75, 0.50, 0.70, 30.0)        # where the Gratitude is read
_GRAT_EM = PW.em_for(_LAYOUT, 13.75, 30.0, 100)


def _bar(t):
    """The height of a bar of light that sinks through the Gratitude while it arrives."""
    top, bottom = _GRAT[1] + 2.2 * _GRAT_EM, _GRAT[1] - 1.6 * _GRAT_EM
    return top + (bottom - top) * float(np.clip((t - 11.0) / 1.8, 0.0, 1.0))


def _gate(pts, t):
    return np.clip((pts[:, 1] - _bar(t)) / 0.35 + 0.5, 0.0, 1.0)


def _ease(x, d):
    u = float(np.clip(x / d, 0.0, 1.0))
    return u * u * (3.0 - 2.0 * u)


def _ripple(t, info):
    if info["state"] != "read":
        return None
    w = info["word"]
    o, r, u, n = info["frame"]
    h = w.home()
    k = float(np.clip((t - w.t_read0) / 0.6, 0.0, 1.0) * np.clip((w.t_read1 - t) / 0.6, 0.0, 1.0))
    ph = (t - w.t_read0) * 1.3 % 1.0
    xn = (h["x"] - h["x"].min()) / max(float(np.ptp(h["x"])), 1e-6)
    bump = np.exp(-((xn - (ph * 1.4 - 0.2)) / 0.06) ** 2) * k
    return dict(pos=info["pos"] + u.astype(np.float32)[None, :] * (0.10 * w.metres_per_em() * bump)[:, None],
                emit=1.0 + 0.9 * bump)


_SPECS = [
    dict(expr="Greeting", name="veil", bind=PW.on_cloth(MOTHER, "veil", u=0.5, v=0.30), em=0.11, bright=1.4,
         t_in=0.6, t_read0=3.2, t_read1=5.0, t_out=6.0, arrive="pen", source=comet, leave="unravel",
         to=lambda t: np.array([MOTHER_AT[0] + 0.3, 2.4, MOTHER_AT[1] - 0.6]), tint=0.75),
    dict(expr="Consideration", name="palm", pos=tuple(PALM_AT + np.array([0.0, 0.17, -0.02])), em=0.026,
         face="camera", t_in=6.2, t_read0=8.0, t_read1=10.2, t_out=11.0, arrive="palm",
         source=lambda t: HAND.where(t, "palm.R") + np.array([0.0, 0.01, 0.0]), leave="rise"),
    _word(0.50, 0.70, 30.0, 100, 11.0, 12.9, 14.6, 15.2, expr="Gratitude", arrive="reveal", gate=_gate,
          facing=lambda t: 55.0 * _ease(12.9 - t, 1.9),
          tilt=lambda t: 30.0 * _ease(12.9 - t, 1.9) - 35.0 * _ease(t - 14.6, 0.6),
          roll=lambda t: 12.0 * _ease(12.9 - t, 1.9) - 14.0 * _ease(t - 14.6, 0.6),
          drive=_ripple, leave="fade"),
    _word(0.30, 0.50, 30.0, 82, 14.6, 16.0, 18.0, 19.0, expr="Apology", arrive="morph", source=_Source(_PETALS),
          carry="petal", leave="fade"),
    _word(0.74, 0.70, 30.0, 92, 15.0, 16.8, 19.0, 20.0, expr="Concession", arrive="morph", source=_Source(_FLOCK),
          carry="bird", leave="fade"),
    _word(0.64, 0.31, 26.0, 88, 15.8, 17.6, 19.8, 20.6, expr="Inclusiveness", arrive="morph",
          source=_Source(_LANTERNS), carry="soft", leave="fade"),
    _word(0.50, 0.66, 30.0, 124, 19.6, 20.8, 22.0, 22.6, expr="Respect", window="clouds", arrive="reveal",
          edge="up", leave="fade"),
    _word(0.50, 0.60, 30.0, 124, 22.0, 22.6, 23.6, 24.0, expr="Compliment", window="sunrise", arrive="reveal",
          edge="out", leave="fade"),
]
WORDS = PW.Words(_SPECS, camera=_LAYOUT)
def _rest_focus(t):
    """Where the lens rests between reading moments: on each stage in turn."""
    if t < 6.0:
        return (MOTHER_AT[0], 1.05, MOTHER_AT[1] - 0.2)
    if t < 11.0:
        return tuple(PALM_AT + np.array([0.0, 0.12, 0.0]))
    return (0.0, 6.0, 10.0)


CAMERA = _rig(focus=lambda t: WORDS.focus_point(t, _rest_focus))


class _Show:
    wants_camera = True

    def __init__(self, ps, t0, t1):
        self.ps, self.t0, self.t1 = ps, t0, t1

    def sample(self, t, cam=None):
        return self.ps.sample(t, cam) if self.t0 <= t <= self.t1 else []


def _setup(scene):
    scene.add("mother", _Show(MOTHER, 0.0, 6.2), reflect=False)
    scene.add("hand", _Show(HAND, 5.9, 11.1), reflect=False)
    scene.add("comet", _Comet(), reflect=False)
    scene.add("petals", _PETALS)
    scene.add("flock", _FLOCK)
    scene.add("lanterns", _LANTERNS)
    WORDS.add_to(scene)
    WORDS.check(CAMERA, need_all=False, min_read=1.0)


P3D = dict(
    camera=CAMERA,
    world=dict(look="night", arch=None, react=dict(beat=0.4, level=0.25),
               light=dict(pos=(MOTHER_AT[0], 1.62, MOTHER_AT[1] + 1.2), color="#ffd29a", strength=0.8, size=0.4,
                          rays=1.0)),
    setup=_setup,
)
