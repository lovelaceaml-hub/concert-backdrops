"""Shared song clock for one isolated twenty-second cinematic film."""
import os
import numpy as np
import songs.s03_original as _base

_base.FPS = int(os.environ.get("OUT_FPS", "60"))
_base.TOTAL = 20.0
_base.NFRAMES = round(_base.TOTAL * _base.FPS)
_base.MUSIC_END = 20.0
_base.FADE = _base.Track([(0, 1), (20, 1)])
_base.EXPOSURE = _base.Track([(0, 1), (20, 1)])
for _phrase in _base.PHRASES:
    _phrase["form"] = _phrase["hold"] = _phrase["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 1)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

TOTAL = 20.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FILM_ID = int(os.environ["CINEMATIC_FILM"])


class Song:
    """A steady exposure envelope; choreography is driven by absolute time."""
    def __init__(self):
        self.env = np.full(NFRAMES, .38)
        self.env_slow = np.full(NFRAMES, .38)
        self.hi = np.full(NFRAMES, .16)
        self.pulse = np.zeros(NFRAMES)
        self.ridge = np.full(2048, .02, dtype="f4")

    def lantern(self, t):
        return .5, .3

    def rings_at(self, t):
        return []


if FILM_ID in (1, 2, 4):
    from tools.cinematic_ten.dancers import build
elif FILM_ID in (3, 9):
    from tools.cinematic_ten.cosmos import build
elif FILM_ID in (6, 7, 8):
    from tools.cinematic_ten.nature import build
elif FILM_ID in (5, 10):
    from tools.cinematic_ten.people_worlds import build
else:
    raise ValueError("Film must be in 1..10")

P3D = build(FILM_ID)
CUTS = tuple(P3D.pop("cuts", ()))
P3D.setdefault("sky_res", .5)
