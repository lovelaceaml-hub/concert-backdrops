"""The designed title and date (song key TITLES, engine/UPGRADE-HOWTO.md section Y): an 18 second test on the
night look. demo_titles_day.py is the same on the day look.

   0 to  4.0   the opening lockup, whole on frame 0, crumbling into dust that drifts away by 4.0
   4.6 to 7.4  the signature, bottom right
   8.0 to 11.4 "December 6" in points of light, whole from about 9.4, bursting at 11.4
  11.8 to 14.0 the signature, top left
  14.4 to 18   the end card, sweeping in, then still to the end
A band of bright lights drifts behind the titles all the way, to show the text protection. No lyrics, no faces.
"""
import os

import numpy as np

import songs.s03_original as _base

_base.TOTAL = 18.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 17.8
_base.FADE = _base.Track([(0.0, 1.0), (17.6, 1.0), (17.95, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (18.0, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import lin  # noqa: E402
from p3d.camera import Rig, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
LOOK = os.environ.get("TITLES_LOOK", "night")


class _Band:
    """Bright lights drifting across the upper sky, behind where the titles stand."""

    def __init__(self, n=900):
        r = np.random.default_rng(7)
        self.s = r.random((n, 4)).astype(np.float32)

    def sample(self, t):
        s = self.s
        x = (np.mod(s[:, 0] + 0.02 * t, 1.0) - 0.5) * 60.0
        y = 6.0 + 9.0 * s[:, 1]
        z = -18.0 - 10.0 * s[:, 2]
        return dict(pos=np.stack([x, y, z], 1), size=0.10 + 0.25 * s[:, 3], color=lin("#ffd9a0"), alpha=0.9,
                    emit=1.6, kind="spark", twinkle=0.6, seed=s[:, 2])


def _setup(scene):
    scene.add("band", _Band())


P3D = dict(
    camera=Rig([orbit((0.0, 5.0, -10.0), radius=38.0, height=(2.4, 3.2), a0=-6.0, a1=7.0, t0=0.0, t1=18.0,
                      look=(0.0, 6.0, -10.0), fov=42.0, aperture=0.04)], handheld=0.2),
    world=dict(look=LOOK, arch=None),
    setup=_setup,
)

TITLES = dict(
    opening=dict(t_end=4.0, y=0.30, palette=LOOK if LOOK in ("night", "day") else "night"),
    signature=dict(windows=[(4.6, 7.4, "br", "night" if LOOK != "day" else "day"),
                            (11.8, 14.0, "tl", "night" if LOOK != "day" else "day")]),
    date_light=dict(t_form=8.0, t_burst=11.4, y=0.30, palette="night" if LOOK != "day" else "day"),
    end_card=dict(t_in=14.4),
    # the campaign logo: until the BRAND helper's logo is in the repository, a local file can stand in
    logo=os.environ.get("TITLES_LOGO") or None,
)
