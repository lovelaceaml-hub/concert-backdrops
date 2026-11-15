"""Particle words, the proof (35 seconds, the 3D layer: engine/UPGRADE-HOWTO.md, sections V and X).

Not a concert video: a test of the nine Words of Mother's Love as light in the 3D world, set to the first
35 seconds of the song 01 promo clip (audio/promo/s01.mp3). All nine expressions appear, are read and are
handed on, each arriving and leaving in its own way, while the camera slowly revolves and rises:

  three bands of the picture at three depths, so one expression is read while the next forms elsewhere
    the sky (far, high, large)      Consideration, Gratitude, Encouragement, Respect
    the sides (middle)              Greeting (left), Concession (right)
    the lake (near, low)            Apology, Inclusiveness, Compliment
  the chains (what each leaving becomes)
    Greeting (a flare, two colours) -> its birds -> Concession (a flock in formation) -> the wind
    Consideration (blown from a palm) -> its petals -> Gratitude (petals land) -> a light of the arch
      -> Encouragement (a shaft from that light) -> rising flakes -> Respect (stars joined by lines) -> stars
    Apology (out of the lake's reflection) -> rings on the water -> Inclusiveness (lights walk in) -> a person
      -> Compliment (rays from behind the person) -> morph -> the title -> past the camera as bokeh
  each light of the arch wakes when its expression is whole.

No lyrics, no faces. The words are particles (engine/p3d/words.py); the engine's flat text is switched off.
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 35.5
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 35.2
_base.FADE = _base.Track([(0.0, 0.0), (0.5, 1.0), (34.6, 1.0), (35.45, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (35.5, 1.0)])
for _p in _base.PHRASES:                       # the flat expressions stay off: the words are particles here
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import StandIn  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.camera import Rig, orbit  # noqa: E402
from p3d.world import arch_points  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

B0, BEAT = 0.93, 0.4878          # the clip's first beat and its pulse (123 beats a minute)


def _b(k):
    """The time of beat k of the clip."""
    return round(B0 + BEAT * k, 3)


CENTER = (0.0, 6.0, -10.0)


def _rig(focus="target"):
    """One slow move for the whole test: the camera revolves a little round the lake and rises."""
    return Rig([orbit(CENTER, radius=(46.0, 41.0), height=(1.7, 3.3), a0=-12.0, a1=13.0, t0=0.0, t1=35.5,
                      look=(0.0, 6.6, -10.0), fov=42.0, aperture=0.09, focus=focus)], handheld=0.25)


_LAYOUT = _rig()                 # the same move without the words' focus, for laying the words out


def _word(x, y, depth, px, t_in, t_read0, t_read1, t_out, **kw):
    """A word laid out by where it is read: the screen place (x, y) of its centre and the pixels of one em
    (1080p) at the middle of its reading moment, `depth` metres from the camera."""
    tm = 0.5 * (_b(t_read0) + _b(t_read1))
    return dict(pos=tuple(PW.place(_LAYOUT, tm, x, y, depth)), em=PW.em_for(_LAYOUT, tm, depth, px),
                t_in=_b(t_in), t_read0=_b(t_read0), t_read1=_b(t_read1), t_out=_b(t_out), **kw)


# three bands of the picture, at three depths: the sky (far), the sides (middle), the lake (near and low)
SKY, SIDE, LAKE = dict(y=0.775, depth=36.0), dict(y=0.560, depth=19.0), dict(y=0.455, depth=25.0)
ARCH = dict(span=112.0, height=38.0, z=-45.0)       # a great arc far behind the words, round the picture's edge
LIGHTS = arch_points(ARCH["span"], ARCH["height"], ARCH["z"])
PERSON_AT = tuple(PW.place(_LAYOUT, _b(48), 0.80, 0.33, 14.0) * np.array([1.0, 0.0, 1.0]))
_HEAD = (PERSON_AT[0], 1.62, PERSON_AT[2])
_PALM = tuple(PW.place(_LAYOUT, _b(6), 0.84, 0.36, 13.0))

_SPECS = [
    # ---- the sides: a flare where two hands touch, the Greeting; its birds become the Concession
    _word(0.29, **SIDE, px=104, t_in=-1.9, t_read0=3, t_read1=9, t_out=13, expr="Greeting",
          arrive="touch", touch_at=(B0 - 0.003) / _b(3), leave="flock", away=(1.0, 0.05, -0.15)),
    _word(0.745, 0.575, 19.0, px=88, t_in=10, t_read0=15, t_read1=21, t_out=25, expr="Concession",
          arrive="flock", leave="wind", flock_from=3.3, wind=(1.0, 0.18, -0.5), speed=0.7),
    # ---- the sky: the open palm, petals, a light of the arch, the shaft, the stars
    _word(0.50, **SKY, px=92, t_in=4, t_read0=9, t_read1=15, t_out=19, expr="Consideration",
          arrive="palm", leave="petals", source=_PALM, palm_light=True, wind=(-0.8, 0.5, -0.3)),
    _word(0.50, **SKY, px=77, t_in=16, t_read0=21, t_read1=27, t_out=31, expr="Gratitude",
          arrive="petals", leave="arch", to=tuple(LIGHTS[1])),
    _word(0.50, **SKY, px=86, t_in=28, t_read0=33, t_read1=39, t_out=43, expr="Encouragement",
          arrive="shaft", leave="rise"),
    _word(0.50, **SKY, px=92, t_in=40, t_read0=45, t_read1=51, t_out=55, expr="Respect",
          arrive="stars", leave="stars"),
    # ---- the lake: out of the water, the gathering lights, a person, the rays
    _word(0.45, **LAKE, px=80, t_in=19, t_read0=24, t_read1=30, t_out=34, expr="Apology",
          arrive="lake", leave="sink"),
    _word(0.45, **LAKE, px=92, t_in=31, t_read0=36, t_read1=42, t_out=46, expr="Inclusiveness",
          arrive="gather", leave="give", to="person"),
    _word(0.44, 0.50, 22.0, px=90, t_in=47, t_read0=51, t_read1=57, t_out=57, expr="Compliment",
          arrive="rays", leave="morph", source=_HEAD),
    # ---- all nine become the title
    _word(0.50, 0.62, 21.0, px=118, t_in=57, t_read0=61, t_read1=67, t_out=70, label="Healing Concert",
          lines=["The Words of Mother’s Love"], name="Title", font="title", color="#ffd27a",
          arrive="morph", source="Compliment", leave="bokeh"),
]

# a stand-in person on the water (helper BODY's people replace it): the Inclusiveness becomes this person,
# and the Compliment's rays come from behind them
_PERSON = StandIn(pos=PERSON_AT, height=1.75, n=20000, color="#ffd9a0", facing=-150.0, seed=12)
_T_PERSON = (_b(43), _b(46), _b(58), _b(61))     # forms, whole, starts to go, gone


class _Person:
    def sample(self, t):
        return _PERSON.sample(t)

    def gain(self, t):
        a, b, c, d = _T_PERSON
        return float(np.clip((t - a) / (b - a), 0.0, 1.0) * np.clip((d - t) / (d - c), 0.0, 1.0))


for _s in _SPECS:
    if _s.get("to") == "person":
        _s["to"] = _PERSON
WORDS = PW.Words(_SPECS, face="camera")

CAMERA = _rig(focus=lambda t: WORDS.focus_point(t, (0.0, 6.0, 10.0)))

# each light of the arch wakes when its expression is whole
_LIT = [WORDS[lab].t_read0 for lab in PW.LABELS]


def _setup(scene):
    scene.add("person", _Person())
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


P3D = dict(
    camera=CAMERA,
    world=WORDS.world(dict(
        look=[(0.0, "night"), (29.0, "predawn", 6.0)],
        arch=dict(lit=_LIT, **ARCH),
        react=dict(beat=0.4, level=0.25),
    )),
    bursts=[dict(t=B0, at=tuple(WORDS["Greeting"].centre(0.0)), strength=0.9,
                 radius=0.12, color="#ffe9c4", rise=0.2, fall=0.6),
            dict(t=WORDS["Title"].t_in, at=tuple(WORDS["Compliment"].centre(0.0)), strength=0.7, radius=0.22,
                 color="#fff0d6", rise=0.3, fall=0.8)],
    setup=_setup,
)
