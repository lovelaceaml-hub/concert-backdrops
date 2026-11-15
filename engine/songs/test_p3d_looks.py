"""The looks of the 3D world, one after the other (16 seconds; engine/UPGRADE-HOWTO.md, section V).

Not a concert video: a reference for choosing looks. Eight looks of two seconds each, cut hard, seen by a
camera that drifts slowly over the lake toward the lit arch: night, dusk, predawn, dawn, sunrise, golden, day,
cream. Stills at 1, 3, 5, 7, 9, 11, 13 and 15 seconds show one look each.
"""
import songs.s03_original as _base

_base.TOTAL = 16.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 15.6
_base.FADE = _base.Track([(0.0, 0.0), (0.4, 1.0), (15.5, 1.0), (15.95, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (16.0, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import StandIn  # noqa: E402
from p3d.camera import Rig, dolly  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

LOOK_ORDER = ["night", "dusk", "predawn", "dawn", "sunrise", "golden", "day", "cream"]


def _setup(scene):
    scene.add("figure", StandIn(pos=(0.0, 0.0, 6.0), height=1.75, color="#ffe2b0"))


P3D = dict(
    camera=Rig([dolly((-6.0, 2.2, 62.0), (4.0, 3.0, 46.0), 0.0, 16.0, look=(0.0, 7.0, 0.0), fov=44, aperture=0.05)]),
    world=dict(
        look=[(2.0 * k, name, 0.0) for k, name in enumerate(LOOK_ORDER)],
        sun_az=188.0,
        arch=dict(lit=[-5.0] * 9),
        lanterns=0.6,
        floats=0.7,
        lantern_field=dict(center=(0.0, -20.0), radius=(8.0, 70.0)),
    ),
    setup=_setup,
)
