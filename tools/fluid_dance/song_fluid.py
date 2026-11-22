"""Twelve-second uninterrupted performance clock, without inherited song text."""
import os
import numpy as np
import songs.s03_original as _base

_base.FPS = int(os.environ.get("OUT_FPS", "60"))
_base.TOTAL = 12.0
_base.NFRAMES = round(_base.TOTAL * _base.FPS)
_base.MUSIC_END = 12.0
_base.FADE = _base.Track([(0, 1), (12, 1)])
_base.EXPOSURE = _base.Track([(0, 1), (12, 1)])
for _phrase in _base.PHRASES:
    _phrase["form"] = _phrase["hold"] = _phrase["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 1)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

TOTAL = 12.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0


class Song:
    def __init__(self):
        self.env = np.full(NFRAMES, .30)
        self.env_slow = np.full(NFRAMES, .30)
        self.hi = np.full(NFRAMES, .10)
        self.pulse = np.zeros(NFRAMES)
        self.ridge = np.full(2048, .02, dtype="f4")

    def lantern(self, t):
        return .5, .3

    def rings_at(self, t):
        return []


from tools.fluid_dance.scene import build
P3D = build(mode=os.environ.get("FLUID_DANCE_MODE", "beauty"))
CUTS = P3D.pop("cuts", ())
