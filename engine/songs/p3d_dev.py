"""Development stage for the particle bodies (a scratch scene while they are built; not a concert video).

Several small stages far apart, one per stretch of time, so one stills job shows them all:
  0 to 5     a veiled figure from behind, arms opening, a light behind her head
  5 to 10    a man walking, shedding light
  10 to 15   two hands meeting
  15 to 20   a profile, head and shoulders
"""
import songs.s03_original as _base

_base.TOTAL = 20.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 19.8
_base.FADE = _base.Track([(0.0, 1.0), (19.4, 1.0), (19.95, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (20.0, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d.body import Body, Hands  # noqa: E402
from p3d.camera import Rig, hold, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
X = (0.0, 60.0, 120.0, 180.0)        # where each stage stands


def _setup(scene):
    Body("woman", at=(X[0], 0), facing=180, garment="robe", veil=True, look="glitter", color="#f2b865",
         color2="#ffe6b8", gesture=[(1.0, 30.0, "open_arms")], points=70000, wind=(0.3, 0, -0.5),
         show=(0.0, 5.0), fade=0.01).add(scene, "mother")
    Body("man", at=(X[1] - 2.5, 0), facing=90, motion="walk", garment="tunic", look="glitter", color="#ffcf8a",
         effects=[dict(kind="shed", t=5.0)], show=(5.0, 10.0), fade=0.01).add(scene, "walker")
    for k, v in Hands(meet=(X[2], 1.3, 0), t_touch=13.0, approach=3.0).items():
        scene.add("hand_" + k, v)
    Body("woman", at=(X[3], 0), facing=90, garment="dress", hair=True, look="rim", color="#ffb060",
         color2="#ffe2b0", gesture=[(15.0, 30.0, "look_up", dict(amount=14))], points=90000, detail=dict(head=4),
         effects=[dict(kind="shed", t=15.0, where="back", dir=(-1, 0.25, 0), speed=0.6)],
         show=(15.0, 20.0), fade=0.01).add(scene, "profile")


P3D = dict(
    camera=Rig([
        orbit((X[0], 1.2, 0.0), radius=2.5, height=1.4, a0=-10.0, a1=10.0, t0=0.0, t1=5.0, fov=36, aperture=0.04),
        hold((X[1], 1.1, 5.5), (X[1], 0.9, 0.0), 5.0, 10.0, fov=34, aperture=0.05, blend=0.0),
        hold((X[2], 1.3, 1.15), (X[2], 1.3, 0.0), 10.0, 15.0, fov=30, aperture=0.02, blend=0.0),
        hold((X[3] + 0.05, 1.45, 1.25), (X[3] + 0.05, 1.42, 0.0), 15.0, 20.0, fov=30, aperture=0.03, blend=0.0),
    ]),
    world=dict(look="night", light=dict(pos=(X[0], 1.62, -1.0), color="#ffd29a", strength=1.0, size=0.5, rays=1.0)),
    setup=_setup,
)
