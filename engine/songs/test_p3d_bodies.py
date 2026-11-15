"""The particle bodies, one stage after another (engine/UPGRADE-HOWTO.md, section W). Not a concert video: a
proving ground for every look, effect and motion of engine/p3d/body.py, each on its own stage far from the
others, four seconds each, cut hard.

Stages (start times): see STAGES below; `python -c "import songs.test_p3d_bodies as s; s.listing()"` prints them.
"""
import songs.s03_original as _base

STAGE = 4.0
_N = 7
_base.TOTAL = STAGE * _N
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = _base.TOTAL - 0.2
_base.FADE = _base.Track([(0.0, 1.0), (_base.TOTAL - 0.4, 1.0), (_base.TOTAL - 0.05, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (_base.TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import numpy as np  # noqa: E402

from p3d.body import Body, Hands  # noqa: E402
from p3d.camera import Rig, hold, orbit, dolly  # noqa: E402
from p3d.effects import Wind  # noqa: E402
from track import Track  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
GAP = 70.0                 # metres between stages along x

STAGES = []                # (name, setup(scene, x, t0), camera(x, t0, t1) -> move, light (dx, y, dz) or None)


def stage(name, cam, light=None):
    def deco(fn):
        STAGES.append((name, fn, cam, light))
        return fn
    return deco


def listing():
    for k, st in enumerate(STAGES):
        print("%5.1f  %s" % (k * STAGE, st[0]))


def win(t0):
    return dict(show=(t0, t0 + STAGE), fade=0.01)


# ------------------------------------------------------------------------------------------------ framings
@stage("mother from behind, veil, rays behind the head, arms opening (glitter)",
       lambda x, t0, t1: hold((x + 0.35, 1.25, 2.4), (x, 1.25, 0.0), t0, t1, fov=40, aperture=0.05),
       light=(0.0, 1.62, -1.0))
def s_mother(scene, x, t0):
    Body("woman", at=(x, 0), facing=180, garment="robe", veil=dict(length=1.5), look="glitter", color="#f2b865",
         color2="#ffe6b8", gesture=[(t0 + 0.3, t0 + 30, "open_arms", dict(lift=0.25))], points=80000,
         wind=(0.4, 0, -0.6), **win(t0)).add(scene, "mother")


@stage("profile head and shoulders, rim, streaming off the back",
       lambda x, t0, t1: hold((x + 0.05, 1.45, 1.25), (x + 0.05, 1.42, 0.0), t0, t1, fov=30, aperture=0.03))
def s_profile(scene, x, t0):
    Body("woman", at=(x, 0), facing=90, garment="dress", hair=True, look="rim", color="#ffb060", color2="#ffe2b0",
         gesture=[(t0, t0 + 30, "look_up", dict(amount=14))], points=90000, detail=dict(head=4),
         effects=[dict(kind="shed", t=t0, where="back", dir=(-1, 0.25, 0), speed=0.6)], **win(t0)).add(scene, "profile")


@stage("two hands reaching until they touch (flare at 3 s)",
       lambda x, t0, t1: hold((x, 1.3, 1.15), (x, 1.3, 0.0), t0, t1, fov=30, aperture=0.02))
def s_hands(scene, x, t0):
    for k, v in Hands(meet=(x, 1.3, 0), t_touch=t0 + 3.0, approach=2.6).items():
        scene.add("hand_" + k, v)


@stage("a man walking, shedding light",
       lambda x, t0, t1: hold((x, 1.05, 5.4), (x, 0.9, 0.0), t0, t1, fov=36, aperture=0.05))
def s_walk(scene, x, t0):
    Body("man", at=(x - 2.5, 0), facing=90, motion="walk", garment="tunic", look="glitter", color="#ffcf8a",
         effects=[dict(kind="shed", t=t0)], **win(t0)).add(scene, "walker")


@stage("five people at different depths, shallow focus",
       lambda x, t0, t1: hold((x + 0.6, 1.35, 5.2), (x - 0.5, 1.0, -2.0), t0, t1, fov=40, aperture=0.07,
                              focus=(x - 1.0, 1.1, 1.5)))
def s_crowd(scene, x, t0):
    spots = [((x - 1.0, 1.5), 25, "woman", "dress", "stand"), ((x + 2.2, -0.8), -90, "man", "coat", "walk"),
             ((x - 2.4, -3.5), 40, "man", "tunic", "stand"), ((x + 2.0, -5.5), 200, "woman", "robe", "stand"),
             ((x - 0.2, -8.0), 90, "child", "tunic", "stand")]
    for j, (at, fc, sh, g, m) in enumerate(spots):
        Body(sh, at=at, facing=fc, motion=m, garment=g, look="glitter", color="#ffd29a" if j % 2 else "#f2b865",
             seed=3.0 + j, points=50000, **win(t0)).add(scene, "p%d" % j)


@stage("mother walking away, veil from three-quarter behind",
       lambda x, t0, t1: orbit(lambda t: (x, 1.1, -0.35 * (t - t0)), radius=3.0, height=1.45, a0=28.0, a1=48.0,
                               t0=t0, t1=t1, fov=38, aperture=0.04))
def s_mother_walk(scene, x, t0):
    Body("woman", at=(x, 0), facing=180, motion=[(t0, "walk", dict(speed=0.35))], garment="robe",
         veil=dict(length=1.5), look="glitter", color="#f2b865", color2="#ffe6b8", points=80000,
         wind=(0.5, 0.0, 0.6), **win(t0)).add(scene, "mother2")


@stage("a woman (default hair, dress) and a man (tunic) walking toward the camera, three-quarter",
       lambda x, t0, t1: hold((x + 2.2, 1.2, 3.6), (x, 0.95, 0.0), t0, t1, fov=36, aperture=0.04))
def s_clothes(scene, x, t0):
    Body("woman", at=(x - 0.5, -2.0), facing=15, motion=[(t0, "walk", dict(speed=0.8))], garment="dress",
         look="glitter", color="#f2b865", points=60000, **win(t0)).add(scene, "wa")
    Body("man", at=(x + 0.6, -2.6), facing=15, motion=[(t0, "walk", dict(speed=0.8))], garment="tunic",
         look="glitter", color="#ffcf8a", points=60000, seed=2.0, **win(t0)).add(scene, "wb")


# ------------------------------------------------------------------------------------------------ build
def _setup(scene):
    for k, st in enumerate(STAGES):
        st[1](scene, k * GAP, k * STAGE)


def _light_pos(t):
    k = int(min(max(t // STAGE, 0), len(STAGES) - 1))
    lt = STAGES[k][3]
    if lt is None:
        return (k * GAP, -50.0, -400.0)          # far under the lake: no light for this stage
    return (k * GAP + lt[0], lt[1], lt[2])


def _light_strength(t):
    k = int(min(max(t // STAGE, 0), len(STAGES) - 1))
    return 1.0 if STAGES[k][3] is not None else 0.0


P3D = dict(
    camera=Rig([st[2](k * GAP, k * STAGE, (k + 1) * STAGE) for k, st in enumerate(STAGES)], blend=0.0),
    world=dict(look="night", light=dict(pos=_light_pos, color="#ffd29a", strength=_light_strength, size=0.5, rays=1.0)),
    setup=_setup,
)
