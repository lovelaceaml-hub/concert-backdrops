"""The particle bodies, one stage after another (engine/UPGRADE-HOWTO.md, section W). Not a concert video: a
proving ground for every look, effect and motion of engine/p3d/body.py, each on its own stage far from the
others, four seconds each, cut hard.

Stages (start times): see STAGES below; `python -c "import songs.test_p3d_bodies as s; s.listing()"` prints them.
"""
import songs.s03_original as _base

STAGE = 4.0
_N = 18
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


def stage(name, cam, light=None, shaft=False, look="night"):
    def deco(fn):
        STAGES.append((name, fn, cam, light, shaft, look))
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


# ------------------------------------------------------------------------------------------------ effects
@stage("form: a woman gathers out of drifting dust (0.2 to 3.2 s)",
       lambda x, t0, t1: hold((x + 1.2, 1.2, 3.0), (x, 0.95, 0.0), t0, t1, fov=36, aperture=0.04))
def s_form(scene, x, t0):
    Body("woman", at=(x, 0), facing=25, garment="dress", look="glitter", color="#f2b865", points=60000,
         gesture=[(t0 + 2.4, t0 + 30, "open_arms", dict(lift=0.1))],
         effects=[dict(kind="form", t=t0 + 0.2, dur=3.0)], **win(t0)).add(scene, "former")


@stage("dissolve: a man from behind rises apart into flakes in a blue shaft (from 0.6 s)",
       lambda x, t0, t1: hold((x + 0.2, 1.3, 3.6), (x, 1.6, 0.0), t0, t1, fov=42, aperture=0.03), shaft=True)
def s_dissolve(scene, x, t0):
    Body("man", at=(x, 0), facing=180, garment="tunic", look="glitter", color="#e8b45a", color2="#ffe2a8",
         points=60000, effects=[dict(kind="dissolve", t=t0 + 0.6, dur=3.0, share=0.75)], **win(t0)).add(scene, "riser")


@stage("petals: a woman turns to petals that leave in a spiral (from 0.4 s)",
       lambda x, t0, t1: hold((x + 0.6, 1.25, 2.9), (x, 1.05, 0.0), t0, t1, fov=38, aperture=0.03))
def s_petals(scene, x, t0):
    Body("woman", at=(x, 0), facing=70, garment="dress", look="glitter", color="#f0d6c0", color2="#ffffff",
         points=60000, effects=[dict(kind="petals", t=t0 + 0.4, dur=3.2, share=0.6, color="#d0182a",
                                     color2="#ff5a5a")], **win(t0)).add(scene, "petal")


@stage("birds leave a profile window (from 0.5 s), day sky",
       lambda x, t0, t1: hold((x + 0.1, 1.38, 1.9), (x + 0.1, 1.3, 0.0), t0, t1, fov=34, aperture=0.02),
       look="cream")
def s_birds(scene, x, t0):
    Body("woman", at=(x, 0), facing=-90, garment="dress", look="window", color="#ffd9b0", color2="#ffffff",
         points=60000, effects=[dict(kind="birds", t=t0 + 0.5, dur=2.5, n=40, color="#2a2a38",
                                     dir=(1.0, 0.4, 0.2))], **win(t0)).add(scene, "window", mask=dict(sky="sunrise"))


@stage("blow: dots of two colours, a palm blowing a stream of light (from 1.2 s)",
       lambda x, t0, t1: hold((x + 0.15, 1.3, 1.7), (x + 0.15, 1.25, 0.0), t0, t1, fov=36, aperture=0.015))
def s_blow(scene, x, t0):
    Body("woman", at=(x - 0.15, 0), facing=90, garment="dress", look="dots", color="#29d6e6", color2="#e83ad0",
         points=70000, gesture=[(t0, t0 + 30, "blow", dict(side="L"))],
         effects=[dict(kind="blow", t=t0 + 1.2, dur=2.6, side="L", color="#7af0ff", color2="#ff7ae6")],
         **win(t0)).add(scene, "blower")


@stage("disperse: two in mist, one blowing apart from one side (from 0.5 s)",
       lambda x, t0, t1: hold((x + 0.1, 1.15, 4.6), (x + 0.1, 1.0, 0.0), t0, t1, fov=34, aperture=0.04))
def s_disperse(scene, x, t0):
    Body("man", at=(x - 0.35, 0), facing=80, garment="coat", look="glitter", color="#c86a5a", color2="#ffb08a",
         points=50000, effects=[dict(kind="disperse", t=t0 + 0.5, dur=3.0, share=0.85, dir=(-1.0, 0.3, 0.2))],
         **win(t0)).add(scene, "goer")
    Body("woman", at=(x + 0.45, 0.2), facing=-80, garment="dress", look="glitter", color="#f2c890", points=50000,
         **win(t0)).add(scene, "stayer")


def _ring(x, n=900):
    a = np.arange(n) / n * 2 * np.pi
    return np.stack([x + 0.7 * np.cos(a), 1.6 + 0.7 * np.sin(a), np.zeros(n) - 0.3], axis=1)


@stage("hand-over: a man disperses and the particles gather into a ring of light (handed over at 1.6 s)",
       lambda x, t0, t1: hold((x, 1.3, 4.4), (x, 1.3, 0.0), t0, t1, fov=40, aperture=0.02))
def s_handover(scene, x, t0):
    Body("man", at=(x - 0.2, 0), facing=90, garment="tunic", look="glitter", color="#ffcf8a", points=50000,
         effects=[dict(kind="disperse", t=t0 + 0.2, dur=1.4, share=1.0, dir=(1.0, 0.5, 0.0),
                       to=dict(t=t0 + 1.6, targets=_ring(x), arrive=1.3, stagger=0.6))], **win(t0)).add(scene, "giver")


@stage("reversible: dissolve runs out (0.3 to 1.5 s), hangs, and runs home (2.2 to 3.4 s)",
       lambda x, t0, t1: hold((x + 0.4, 1.2, 3.4), (x, 1.05, 0.0), t0, t1, fov=38, aperture=0.03))
def s_amount(scene, x, t0):
    amt = Track([(t0 + 0.3, 0.0), (t0 + 1.5, 0.55), (t0 + 2.2, 0.55), (t0 + 3.4, 0.0)])
    Body("woman", at=(x, 0), facing=30, garment="dress", look="glitter", color="#ffd29a", points=55000,
         effects=[dict(kind="dissolve", t=t0 + 0.3, dur=2.0, amount=amt, hang=1.2)], **win(t0)).add(scene, "mender")


@stage("plexus: a runner of points and lines, gold bokeh",
       lambda x, t0, t1: orbit(lambda t: (x - 3.0 + 3.16 * (t - t0), 1.0, 0.0), radius=3.2, height=1.2, a0=60.0,
                               a1=30.0, t0=t0, t1=t1, fov=34, aperture=0.06))
def s_plexus(scene, x, t0):
    Body("man", at=(x - 3.0, 0), facing=90, motion="run", garment="tunic", look="plexus", color="#ffd08a",
         color2="#a8d8ff", points=40000, **win(t0)).add(scene, "runner")


@stage("constellation: a figure of a few stars that fills into the full plexus (detail 0 to 1 over 1 to 3 s)",
       lambda x, t0, t1: hold((x, 1.1, 3.6), (x, 1.0, 0.0), t0, t1, fov=36, aperture=0.0))
def s_const(scene, x, t0):
    Body("woman", at=(x, 0), facing=20, garment="dress", color="#cfe0ff", color2="#ffffff", points=40000,
         look=dict(name="plexus", detail=Track([(t0 + 1.0, 0.0), (t0 + 3.0, 1.0)])),
         gesture=[(t0, t0 + 30, "open_arms", dict(lift=0.6))], **win(t0)).add(scene, "stars")


@stage("cold dust ignites: a sweep from his palm turns a dark rim body to glitter, a rose wash (from 0.8 s)",
       lambda x, t0, t1: hold((x + 0.9, 1.25, 3.0), (x, 1.05, 0.0), t0, t1, fov=36, aperture=0.03))
def s_sweep(scene, x, t0):
    Body("man", at=(x, 0), facing=40, garment="coat", color="#ffcf8a", points=60000,
         gesture=[(t0, t0 + 30, "raise_hand", dict(side="R"))],
         look=[dict(name="rim", before="spark", bright=0.6), dict(name="glitter", after="spark")],
         sweeps=dict(spark=dict(t=t0 + 0.8, at="palm.R", speed=0.9, width=0.25, flash=2.5)),
         wash=dict(color="#ff9ab0", amount=Track([(t0 + 2.4, 0.0), (t0 + 3.6, 0.6)])), **win(t0)).add(scene, "igniter")


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


def _shaft_on(t):
    k = int(min(max(t // STAGE, 0), len(STAGES) - 1))
    return 1.2 if STAGES[k][4] else 0.0


def _shaft_base(t):
    k = int(min(max(t // STAGE, 0), len(STAGES) - 1))
    return (k * GAP, -0.6)


P3D = dict(
    camera=Rig([st[2](k * GAP, k * STAGE, (k + 1) * STAGE) for k, st in enumerate(STAGES)], blend=0.0),
    world=dict(look=[(k * STAGE, st[5], 0.0) for k, st in enumerate(STAGES)],
               light=dict(pos=_light_pos, color="#ffd29a", strength=_light_strength, size=0.5, rays=1.0),
               shafts=[dict(base=_shaft_base, radius=0.9, top=30.0, spread=0.15, color="#5f8cff", strength=_shaft_on)]),
    setup=_setup,
)
