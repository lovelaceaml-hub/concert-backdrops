"""Particle words, the proof (31.5 seconds, the 3D layer: engine/UPGRADE-HOWTO.md, sections V, X and X2).

Not a concert video: a test of the nine Words of Mother's Love as light in the 3D world, set to the first
31.5 seconds of the song 01 promo clip (audio/promo/s01.mp3). All nine expressions appear, are read and are
handed on, each arriving and leaving in its own way, while the camera never stops moving:

  0 to 1.3     macro: two hands of light (helper BODY), gold and blue, reach; their fingertips touch on the
               first beat and the flare writes the Greeting in the air behind them
  1.3 to 5.5   the camera pulls back and rises (rack focus to the words); a woman of light in profile on
               the water raises her open palm and blows: the Consideration
  5.5 to 27    the camera revolves round the lake and climbs while the words hand themselves on
  27 to 31.5   it pushes in on the title

  the chains (what each leaving becomes)
    Greeting (the touch) -> its birds -> Concession (a flock in formation) -> the wind
    Consideration (her palm) -> its petals -> Gratitude (petals land) -> a light of the arch
      -> Encouragement (a shaft from that light) -> rising flakes -> Respect (stars joined by lines) -> stars
    Apology (out of the lake) -> rain on the water -> Inclusiveness (lights walk in over it) -> a person
      -> Compliment (rays from behind her head) -> morph -> the title -> past the camera as bokeh
  each light of the arch wakes when its expression is whole.

No lyrics, no faces (the people are seen in profile or from behind). The words are particles
(engine/p3d/words.py); the engine's flat text is switched off.
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 31.5
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 31.3
_base.FADE = _base.Track([(0.0, 1.0), (30.7, 1.0), (31.45, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (31.5, 1.0)])
for _p in _base.PHRASES:                       # the flat expressions stay off: the words are particles here
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import words as PW  # noqa: E402
from p3d.camera import Rig, dolly, hold, orbit  # noqa: E402
from p3d.world import arch_points  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

B0, BEAT = 0.93, 0.4878          # the clip's first beat and its pulse (123 beats a minute)


def _b(k):
    """The time of beat k of the clip."""
    return round(B0 + BEAT * k, 3)


HANDS = np.array([0.0, 1.55, 18.0])            # where the fingertips meet
STAGE = (0.0, 5.0, -4.0)                       # what the camera revolves round
_PULL_END = (1.2, 3.4, 27.0)


def _rig(focus="target"):
    """Macro on the hands, a pull back that rises, a long revolve that climbs, a push in on the title."""
    az0 = float(np.degrees(np.arctan2(_PULL_END[0] - STAGE[0], _PULL_END[2] - STAGE[2])))
    r0 = float(np.hypot(_PULL_END[0] - STAGE[0], _PULL_END[2] - STAGE[2]))
    return Rig([
        hold(HANDS + np.array([0.20, 0.08, 1.20]), HANDS + np.array([0.0, 0.0, -0.3]), 0.0, 1.3,
             drift=(0.05, 0.02, 0.10), fov=40.0, aperture=0.016, near=0.02),
        dolly(HANDS + np.array([0.30, 0.25, 1.9]), _PULL_END, 1.3, 5.5,
              look=(HANDS + np.array([0.0, 0.3, -2.0]), (0.0, 4.4, -4.0)), fov=42.0, aperture=0.05, blend=1.1),
        orbit(STAGE, radius=(r0, 26.0), height=(3.4, 6.2), a0=az0, a1=az0 - 40.0, t0=5.5, t1=27.0,
              look=(0.0, 5.2, -4.0), fov=42.0, aperture=0.07, blend=1.6),
        dolly((-15.5, 6.0, 15.5), (-11.0, 5.8, 10.0), 27.0, 31.5, look=(0.0, 5.6, -6.0), fov=42.0, aperture=0.06,
              blend=1.8),
    ], blend=1.5, fov=42.0, handheld=0.22, focus=focus)


_LAYOUT = _rig()                 # the same moves without the words' focus, for laying the words out


def _word(x, y, depth, px, t_in, t_read0, t_read1, t_out, **kw):
    """A word laid out by where it is read: the screen place (x, y) of its centre and the pixels of one em
    (1080p) at the middle of its reading moment, `depth` metres from the camera. Times in beats."""
    tm = 0.5 * (_b(t_read0) + _b(t_read1))
    return dict(pos=tuple(PW.place(_LAYOUT, tm, x, y, depth)), em=PW.em_for(_LAYOUT, tm, depth, px),
                t_in=_b(t_in), t_read0=_b(t_read0), t_read1=_b(t_read1), t_out=_b(t_out), **kw)


def _ground(t, x, y, depth):
    """The place on the water seen at screen (x, y) `depth` metres away at time t."""
    p = PW.place(_LAYOUT, t, x, y, depth)
    return (float(p[0]), float(p[2]))


ARCH = dict(span=112.0, height=38.0, z=-45.0)       # a great arc far behind the words
LIGHTS = arch_points(ARCH["span"], ARCH["height"], ARCH["z"])

# ---- the people (helper BODY): two hands, a woman who blows the Consideration from her palm, a woman the
# Inclusiveness becomes, with the Compliment's rays behind her head
_GIVER_AT = _ground(4.2, 0.13, 0.30, 9.5)
_PERSON_AT = _ground(21.5, 0.80, 0.30, 15.0)


def _people():
    from p3d.body import Body, Hands
    hands = Hands(meet=tuple(HANDS), t_touch=B0, approach=1.7, axis=90.0, apart=0.55, points=45000)
    giver = Body("woman", at=_GIVER_AT, facing=96.0, garment="dress", hair=True, look="glitter",
                 color="#ffc98f", color2="#ffe9c4", points=60000, show=(0.0, 12.5), fade=0.8,
                 gesture=[(1.6, 8.6, "blow", dict(side="R"))])
    person = Body("woman", at=_PERSON_AT, facing=200.0, garment="robe", hair=True, look="glitter",
                  color="#ffd9a0", color2="#fff1d6", points=60000, show=(_b(40.0), 31.5), fade=0.4,
                  effects=[dict(kind="form", t=_b(40.0), dur=2.2, source=lambda t: WORDS["Inclusiveness"].targets(t))])
    return hands, giver, person


class _Show:
    """A point set seen only between two times (it costs nothing outside them), fading at both ends."""
    wants_camera = True

    def __init__(self, ps, t0, t1, fade=0.5):
        self.ps, self.t0, self.t1, self.fade = ps, float(t0), float(t1), float(fade)

    def sample(self, t, cam=None):
        if not self.t0 <= t <= self.t1:
            return []
        return self.ps.sample(t, cam) if getattr(self.ps, "wants_camera", False) else self.ps.sample(t)

    def gain(self, t):
        g = getattr(self.ps, "gain", None)
        k = float(np.clip((self.t1 - t) / self.fade, 0.0, 1.0))
        return k * (float(g(t)) if g else 1.0)


HANDS_SET, GIVER, PERSON = _people()
_HEAD = lambda t: PERSON.where(t, "head") + np.array([0.0, 0.05, 0.0])    # noqa: E731
_PALM = lambda t: GIVER.where(t, "palm.R")                                # noqa: E731

_SPECS = [
    # ---- the hands touch on the first beat: the Greeting; its birds become the Concession
    _word(0.50, 0.63, 11.5, 104, t_in=-B0 / BEAT, t_read0=3, t_read1=8.5, t_out=12.5, expr="Greeting",
          arrive="touch", source=tuple(HANDS), touch_at=B0 / _b(3), flare_size=0.18, leave="flock",
          away=(0.85, 0.40, -0.35)),
    _word(0.76, 0.58, 20.0, 90, t_in=9, t_read0=13.5, t_read1=19, t_out=23, expr="Concession",
          arrive="flock", leave="wind", flock_from=3.6, wind=(1.0, 0.18, -0.5), speed=0.7),
    # ---- the sky: the open palm, petals, a light of the arch, the shaft, the stars
    _word(0.40, 0.75, 32.0, 92, t_in=3.5, t_read0=8, t_read1=13.5, t_out=17.5, expr="Consideration",
          arrive="palm", source=_PALM, leave="petals", wind=(-0.8, 0.5, -0.3), reach=0.32),
    _word(0.50, 0.80, 34.0, 92, t_in=14, t_read0=19, t_read1=24.5, t_out=28, expr="Gratitude",
          arrive="petals", leave="arch", to=tuple(LIGHTS[1])),
    _word(0.50, 0.79, 34.0, 90, t_in=28, t_read0=32, t_read1=37.5, t_out=41, expr="Encouragement",
          arrive="shaft", leave="rise"),
    _word(0.50, 0.79, 34.0, 94, t_in=40, t_read0=44, t_read1=49.5, t_out=53, expr="Respect",
          arrive="stars", leave="stars"),
    # ---- the lake: out of the water, the gathering lights, a person, the rays
    _word(0.47, 0.47, 24.0, 86, t_in=17, t_read0=22, t_read1=27.5, t_out=30.5, expr="Apology",
          arrive="lake", leave="sink"),
    _word(0.44, 0.47, 24.0, 96, t_in=30.5, t_read0=34.5, t_read1=40, t_out=43.5, expr="Inclusiveness",
          arrive="gather", leave="give", to=PERSON),
    _word(0.42, 0.50, 22.0, 92, t_in=43.5, t_read0=47, t_read1=52.5, t_out=52.5, expr="Compliment",
          arrive="rays", leave="morph", source=_HEAD),
    # ---- all nine become the title
    _word(0.50, 0.60, 21.0, 118, t_in=52.5, t_read0=56, t_read1=61.5, t_out=64.0, label="Healing Concert",
          lines=["The Words of Mother’s Love"], name="Title", font="title", color="#ffd27a",
          arrive="morph", source="Compliment", leave="bokeh"),
]

WORDS = PW.Words(_SPECS, face="camera")
CAMERA = _rig(focus=lambda t: WORDS.focus_point(t, HANDS if t < 2.0 else (0.0, 4.0, 4.0)))

# each light of the arch wakes when its expression is whole
_LIT = [WORDS[lab].t_read0 for lab in PW.LABELS]


def _setup(scene):
    for k in ("left", "right"):              # the words draw the flare of the touch themselves
        scene.add("hand " + k, _Show(HANDS_SET[k], 0.0, 4.0, fade=1.2), reflect=False)
    scene.add("giver", _Show(GIVER, 0.0, 12.5, fade=1.0))
    scene.add("person", _Show(PERSON, _b(40.0), 31.5, fade=0.5))
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


P3D = dict(
    camera=CAMERA,
    world=WORDS.world(dict(
        look=[(0.0, "night"), (24.0, "predawn", 6.0)],
        arch=dict(lit=_LIT, line=0.45, **ARCH),
        react=dict(beat=0.4, level=0.25),
    )),
    bursts=[dict(t=WORDS["Title"].t_in, at=tuple(WORDS["Compliment"].centre(0.0)), strength=0.35, radius=0.12,
                 color="#fff0d6", rise=0.3, fall=0.8)],
    setup=_setup,
)
