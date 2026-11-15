"""The brand pieces, one after another (60 seconds on the medley; engine/UPGRADE-HOWTO.md, section Z).

Not a concert video: a proof of what helper BRAND built for the five films (engine/p3d/brand*.py).

   0.0 to  8.0   the logo builds itself out of light over a night lake (hearts sweep in, the globe's ring
                 and grid draw, the branches grow), holds, and lifts apart into sparks
"""
import os

import numpy as np

import songs.s03_original as _base

TOTAL = 60.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 59.6
_base.SONG_END = 60.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import brand as BR  # noqa: E402
from p3d.camera import Rig, dolly, hold, orbit  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 59.6
SONG_END = 60.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# ---------------------------------------------------------------------------------------------- the logo
LOGO_AT = (0.0, 6.2, -6.0)
CAMERA = Rig([
    orbit((0.0, 5.0, -6.0), radius=(26.0, 22.0), height=(3.0, 4.2), a0=-10.0, a1=8.0, t0=0.0, t1=8.0,
          look=(0.0, 6.0, -6.0), fov=40.0, aperture=0.04, focus="target"),
    hold((0.0, 4.0, 22.0), (0.0, 6.0, 0.0), 8.0, 60.0, drift=(0.6, 0.2, -1.0), fov=40.0, aperture=0.03, blend=1.2),
], blend=1.5, handheld=0.15)

LOGO = BR.Logo(pos=LOGO_AT, size=6.0, face="camera", camera=CAMERA, t_in=0.4, t_full=4.6, t_out=6.6,
               leave_dur=1.6, arrive="build", leave="rise", bright=float(os.environ.get("BB", "0.45")), white=float(os.environ.get("BW", "0.35")), paint=float(os.environ.get("BP", "0")))


def _setup(scene):
    scene.add("logo", LOGO)


P3D = dict(
    camera=CAMERA,
    world=dict(look=[(0.0, "night")], arch=None, react=dict(beat=0.3, level=0.2)),
    setup=_setup,
)
