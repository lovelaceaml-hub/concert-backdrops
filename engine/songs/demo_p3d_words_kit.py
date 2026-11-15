"""Particle words, the directors' kit (30 seconds, the 3D layer: engine/UPGRADE-HOWTO.md, sections V and X).

Not a concert video: a test of what the ten films asked of the words, set to the first 30 seconds of the
song 01 promo clip (audio/promo/s01.mp3). One thing after another:

   0 to  7   Greeting        written by the word's own pen; parts like doors                    (fixed in space)
   3 to 10   Concession      revealed behind a lowering height; leaves as a stream along a curve
   6 to 13   Apology         stitched in; unravels
   9 to 16   Respect         rides ahead of the camera; written by a comet that someone else flies;
                             leaves as a stream into that comet
  12 to 20   Gratitude       lies flat on the lake, read from above; woven in
  17 to 24   Encouragement   bound to the face of a moving wave; born from rain that hangs in the air
  22 to 30   day breaks      Consideration as a window onto a field of stars, the Compliment painted
                             in its own colour, Inclusiveness in dark ink
  all the way: drifting petals keep clear of every word that is being read (PW.KeepClear).

No lyrics, no faces. The engine's flat text is switched off.
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 30.5
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 30.2
_base.FADE = _base.Track([(0.0, 0.0), (0.5, 1.0), (29.7, 1.0), (30.45, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (30.5, 1.0)])
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
from p3d.camera import Rig, dolly, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
CENTER = (0.0, 6.0, -10.0)


def _rig(focus="target"):
    return Rig([
        orbit(CENTER, radius=44.0, height=(2.0, 2.6), a0=-8.0, a1=0.0, t0=0.0, t1=12.6, look=(0.0, 6.6, -10.0),
              fov=42.0, aperture=0.06, focus=focus),
        dolly((0.0, 25.0, 19.0), (0.0, 27.0, 16.0), 12.6, 19.6, look=((0.0, 0.0, 5.0), (0.0, 0.0, 4.5)), fov=42.0,
              aperture=0.0),                                             # over the lake, looking down
        orbit(CENTER, radius=42.0, height=(2.4, 3.2), a0=0.0, a1=8.0, t0=19.6, t1=30.5, look=(0.0, 6.6, -10.0),
              fov=42.0, aperture=0.05, focus=focus),
    ], blend=2.0, handheld=0.2)


_LAYOUT = _rig()


def _word(x, y, depth, px, t_in, t_read0, t_read1, t_out, **kw):
    """A word laid out by where it is read (see demo_p3d_words.py)."""
    tm = 0.5 * (t_read0 + t_read1)
    return dict(pos=tuple(PW.place(_LAYOUT, tm, x, y, depth)), em=PW.em_for(_LAYOUT, tm, depth, px),
                t_in=t_in, t_read0=t_read0, t_read1=t_read1, t_out=t_out, **kw)


# the comet that writes the Respect and that the Respect then follows: a point flown by "someone else"
_RIDE = (0.50, 0.70, 20.0)                      # where the riding word sits in the picture, and how far ahead


def comet(t):
    """The comet's place at t: in from the left, across the word while it is written, then off up to the right."""
    u = (t - 9.4) / 2.1
    if u < 0.0:
        x, y = 0.18 + 0.30 * u, 0.70 + 0.10 * u
    elif u < 1.0:
        x, y = 0.18 + 0.64 * u, 0.70 + 0.045 * np.sin(u * 15.0)
    else:
        v = u - 1.0
        x, y = 0.82 + 0.05 * v + 0.02 * np.sin(v * 2.2), 0.70 + 0.07 * np.sin(v * 1.3)
    return PW.place(_LAYOUT, t, x, y, _RIDE[2])


class _Comet:
    def sample(self, t):
        if not 7.6 < t < 16.4:
            return None
        k = float(np.clip((t - 7.6) / 0.6, 0.0, 1.0) * np.clip((16.4 - t) / 0.5, 0.0, 1.0))
        tail = np.array([comet(t - 0.035 * i) for i in range(14)], np.float32)
        return [dict(pos=tail[:1], size=0.22, color=lin("#fff1d0"), alpha=k, emit=5.0, kind="spark"),
                dict(pos=tail[1:], pos2=tail[:-1], size=0.10, color=lin("#ffc890"), alpha=k * np.linspace(0.8, 0.0, 13),
                     alpha2=k * np.linspace(0.9, 0.06, 13), kind="ribbon")]


# rain that hangs in the air where the Encouragement will be: its drops fly together as the words
class _Rain:
    def __init__(self, centre, size, n=7000):
        r = np.random.default_rng(5)
        self.p = (np.asarray(centre) + (r.random((n, 3)) - 0.5) * np.asarray(size)).astype(np.float32)
        self.seed = r.random(n).astype(np.float32)

    def sample(self, t):
        return dict(pos=self.p, pos2=self.p + np.array([0.0, 0.28, 0.0], np.float32), size=0.03,
                    color=lin("#bcd6ff"), alpha=0.75, alpha2=0.0, kind="ribbon", seed=self.seed, twinkle=0.6)

    def gain(self, t):
        return float(np.clip((t - 15.6) / 1.0, 0.0, 1.0) * np.clip((19.6 - t) / 1.4, 0.0, 1.0))


# petals drifting through the whole picture: wrapped in PW.KeepClear they leave the read words alone
class _Petals:
    def __init__(self, n=1100):
        r = np.random.default_rng(9)
        self.s = r.random((n, 5)).astype(np.float32)

    def sample(self, t):
        s = self.s
        x = (np.mod(s[:, 0] + 0.035 * t * (0.6 + 0.8 * s[:, 3]), 1.0) - 0.5) * 46.0
        y = 0.5 + 15.0 * s[:, 1] + 0.6 * np.sin(t * 0.7 + s[:, 4] * 6.28)
        z = -4.0 + 26.0 * s[:, 2]
        rot = np.stack([s[:, 0] * 6.28 + t * (0.8 + s[:, 3]), s[:, 1] * 6.28 + t * (1.5 + 2.0 * s[:, 4])], axis=1)
        cols = np.stack([lin("#ff8fa3"), lin("#ffb19a"), lin("#ffd9c9")]).astype(np.float32)
        return dict(pos=np.stack([x, y, z], axis=1), size=0.16 + 0.14 * s[:, 3], color=cols[(s[:, 4] * 3).astype(int) % 3],
                    alpha=0.8, rot=rot, kind="petal", seed=s[:, 2])

    def gain(self, t):
        return float(np.clip(t / 1.0, 0.0, 1.0) * np.clip((13.2 - t) / 1.2, 0.0, 1.0))


# the face of a wave for the Encouragement to lie on: an upright sheet with a swell running along it
_WAVE_AT = np.asarray(PW.place(_LAYOUT, 22.3, 0.50, 0.66, 30.0))


def wave(x, y, t):
    x, y = np.asarray(x, np.float64), np.asarray(y, np.float64)
    ph = x * 0.42 - t * 1.6
    return np.stack([_WAVE_AT[0] + x, _WAVE_AT[1] + y + 0.45 * np.sin(ph), _WAVE_AT[2] + 0.9 * np.cos(ph)], axis=-1)


_RAIN = _Rain(_WAVE_AT, (26.0, 9.0, 8.0))
_CURVE = [PW.place(_LAYOUT, 8.8, x, y, d) for x, y, d in ((0.50, 0.80, 34.0), (0.72, 0.90, 30.0), (0.94, 0.80, 22.0),
                                                           (1.02, 0.55, 14.0), (0.90, 0.30, 8.0), (1.15, 0.20, 3.0))]

_SPECS = [
    _word(0.27, 0.56, 19.0, 100, 0.3, 2.4, 5.0, 6.8, expr="Greeting", arrive="pen", leave="doors"),
    _word(0.50, 0.80, 34.0, 96, 3.0, 5.2, 7.8, 9.8, expr="Concession", arrive="reveal", edge="down",
          leave="stream", path=_CURVE),
    _word(0.46, 0.455, 25.0, 80, 6.0, 8.4, 11.0, 13.0, expr="Apology", arrive="stitch", leave="unravel"),
    dict(expr="Respect", ride=_RIDE, face="screen", em=PW.em_for(_LAYOUT, 12.9, _RIDE[2], 84), t_in=9.4, t_read0=11.6, t_read1=14.2,
         t_out=16.0, arrive="pen", source=comet, leave="stream", to=comet),
    dict(expr="Gratitude", pos=(0.0, 0.03, 4.5), width=24.0, face="flat", t_in=12.6, t_read0=15.2, t_read1=17.9,
         t_out=19.8, arrive="weave", leave="wind", wind=(1.0, 0.25, -0.2)),
    dict(expr="Encouragement", bind=wave, em=PW.em_for(_LAYOUT, 22.3, 30.0, 84), t_in=17.4, t_read0=21.0,
         t_read1=23.6, t_out=25.2, arrive="morph", source=_RAIN, carry="flake", leave="rise"),
    _word(0.50, 0.76, 30.0, 122, 23.4, 25.2, 27.9, 29.8, expr="Consideration", window="stars", arrive="reveal",
          edge="out", leave="doors"),
    _word(0.30, 0.42, 22.0, 84, 24.4, 26.2, 28.9, 30.3, expr="Compliment", paint=True, arrive="pen", leave="fade"),
    _word(0.74, 0.44, 18.0, 74, 25.4, 27.0, 29.6, 30.4, expr="Inclusiveness", ink=True, arrive="reveal",
          edge="right", leave="fade"),
]
WORDS = PW.Words(_SPECS, camera=_LAYOUT, face="camera")
CAMERA = _rig(focus=lambda t: WORDS.focus_point(t, (0.0, 6.0, 10.0)))


def _setup(scene):
    scene.add("petals", PW.KeepClear(_Petals(), WORDS))
    scene.add("comet", _Comet())
    scene.add("rain", _RAIN)
    WORDS.add_to(scene)
    WORDS.check(CAMERA, need_all=False)


P3D = dict(
    camera=CAMERA,
    world=dict(look=[(0.0, "night"), (20.5, "predawn", 3.0), (23.8, "day", 2.6)], arch=None,
               react=dict(beat=0.4, level=0.25)),
    setup=_setup,
)
