"""3D layer scale test (8 seconds; engine/UPGRADE-HOWTO.md, section V). Not a concert video.

Kilometres, each once:
  0 to 4 s   a pull-back by a constant factor per second, from 8 m in front of a figure to 2.4 km above the lake
             looking down: the lake (shore=350: a disc 700 m across) shrinks to a pool of light, the hills
             pass below the camera and become land round it
  4 to 8 s   a flight from 3 km outside the shore at 300 m, descending toward the lake and the figure
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 8.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 7.8
_base.FADE = _base.Track([(0.0, 0.0), (0.2, 1.0), (7.7, 1.0), (7.98, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (8.0, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import StandIn  # noqa: E402
from p3d.camera import Rig, fly  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0


def _pull(t):
    """Distance from the figure grows by the same factor every second (8 m to 2.4 km in 4 s)."""
    d = 8.0 * (2400.0 / 8.0) ** (t / 4.0)
    a = np.radians(10.0 + 75.0 * min(t / 4.0, 1.0) ** 0.7)      # from level to looking almost straight down
    return (0.0, 1.6 + d * np.sin(a), d * np.cos(a)), (0.0, 1.0, 0.0)


def _setup(scene):
    scene.add("figure", StandIn(pos=(0.0, 0.0, 0.0), color="#ffe2b0", seed=4))


PULL = [(k * 0.25, *_pull(k * 0.25)) for k in range(17)]
CAMERA = Rig([
    fly(PULL, fov=42, aperture=0.0),
    fly([(4.0, (3000.0, 300.0, 1200.0), (0.0, 0.0, 0.0)), (6.0, (900.0, 60.0, 360.0), (0.0, 2.0, 0.0)),
         (8.0, (30.0, 3.0, 12.0), (0.0, 1.2, 0.0))], fov=40, blend=0.0),
], handheld=0.0, free=True)

P3D = dict(
    camera=CAMERA,
    world=dict(look="sunrise", sun_az=150.0, lanterns=0.9, floats=0.9, haze=0.25, shore=350.0,
               lantern_field=dict(count=900, center=(0.0, 0.0), radius=(6.0, 400.0), height=120.0),
               float_field=dict(count=2500, center=(0.0, 0.0), radius=(4.0, 340.0))),
    setup=_setup,
)
