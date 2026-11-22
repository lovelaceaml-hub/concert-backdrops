"""3D layer motion test (14 seconds; engine/UPGRADE-HOWTO.md, section V). Not a concert video.

Speed and blur, each once:
  0 to 4 s    a skim at 40 metres a second, 1.2 m over a storm lake, past floating lights, posts of light and a
              row of figures; a field of glass (world key lake) opens round the figures
  4 s         a whip pan (whip=True) to an orbit round the figures: the camera swings, cuts inside the blur,
              swings in; it never flies through the space between
  4 to 8 s    a fast revolve (about 60 degrees a second) with the lake field: storm outside, a ring of glass
              that widens round the figures
  8 s         a hard cut (blend 0) with no burst: the first frame after it must have no smear from before
  8 to 10 s   a turn at 120 degrees a second drawn with four moments in the shutter (motion_samples as a Track)
  10 to 14 s  a flight straight through a dense sheet of 300 thousand points (a curtain of light), then out
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 14.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 13.6
_base.FADE = _base.Track([(0.0, 0.0), (0.2, 1.0), (13.6, 1.0), (13.98, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (14.0, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import StandIn, hash01, lin  # noqa: E402
from p3d.camera import Rig, dolly, hold, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0


class Posts:
    """Posts of light standing in the water along the skim, every 12 m on both sides."""

    def sample(self, t):
        z = np.arange(-20.0, 230.0, 12.0)
        k = np.arange(len(z))
        x = np.where(k % 2 == 0, -6.0, 6.0) + 1.5 * np.sin(k * 1.3)
        h = np.linspace(0.2, 2.6, 14)
        pos = np.stack([np.repeat(x, 14), np.tile(h, len(z)), np.repeat(z, 14)], axis=1)
        col = np.where((np.arange(len(pos)) // 14 % 3 == 0)[:, None], lin("#ffcf8a"), lin("#9cc8ff"))
        return dict(pos=pos, size=0.07, color=col, alpha=0.9, emit=2.0, kind="soft")


class Sheet:
    """A curtain of 300 thousand points across the flight path at z = -40 (a dense sheet to pass through)."""
    static = True

    def sample(self, t):
        n = 300000
        x = (hash01(n, 51) - 0.5) * 30.0
        y = 0.2 + hash01(n, 52) * 9.0
        z = -40.0 + (hash01(n, 53) - 0.5) * 0.6
        s = hash01(n, 54)
        col = np.stack([0.7 + 0.3 * s, 0.75 + 0.1 * s, 1.0 - 0.3 * s], axis=1)
        return dict(pos=np.stack([x, y, z], axis=1), size=0.015 + 0.02 * s ** 2, color=col, alpha=0.6,
                    twinkle=0.5, seed=s)


def _lake(X, Z, t):
    """A storm sea with a ring of glass round the figures that widens from 4 s."""
    r = np.sqrt(X ** 2 + (Z + 2.0) ** 2)
    rad = 6.0 + 9.0 * np.clip((t - 4.0) / 4.0, 0.0, 1.0)
    calm = 1.0 - np.clip((r - rad) / 3.0, 0.0, 1.0)
    return 2.6 * (1.0 - calm), 0.55 + 0.45 * calm


def _setup(scene):
    for k, x in enumerate((-2.4, 0.0, 2.4)):
        scene.add(f"figure{k}", StandIn(pos=(x, 0.0, -2.0 - abs(x) * 0.5), color="#ffe2b0", seed=10 + k))
    scene.add("posts", Posts())
    scene.add("sheet", Sheet())


CAMERA = Rig([
    dolly((0.0, 1.2, 200.0), (0.0, 1.2, 40.0), 0.0, 4.0, look="ahead", fov=55, aperture=0.0),
    orbit((0.0, 1.2, -2.0), radius=7.0, height=(1.6, 2.4), a0=200.0, a1=440.0, t0=4.0, t1=8.0, fov=42,
          aperture=0.04, whip=True, blend=0.5),
    orbit((0.0, 1.2, -2.0), radius=9.0, height=3.0, a0=90.0, a1=330.0, t0=8.0, t1=10.0, fov=44, aperture=0.03,
          blend=0.0),
    dolly((0.0, 2.6, -10.0), (0.0, 3.0, -70.0), 10.0, 14.0, look="ahead", fov=50, aperture=0.02, blend=0.6,
          pace=[(10.0, 0.0), (11.5, 0.38), (12.5, 0.62), (14.0, 1.0)]),
], handheld=0.2)

P3D = dict(
    camera=CAMERA,
    motion_samples=Track([(0.0, 1.0), (8.0, 1.0), (8.01, 4.0), (9.99, 4.0), (10.0, 1.0)]),
    world=dict(look="dawn", sun_az=180.0, floats=1.0, ripple=2.0,
               float_field=dict(count=1600, center=(0.0, 100.0), radius=(2.0, 140.0)),
               lake=dict(field=_lake, center=(0.0, -2.0), size=60.0, res=96)),
    setup=_setup,
)
