"""3D layer windows test (8 seconds; engine/UPGRADE-HOWTO.md, section V). Not a concert video.

The mask layers, each once:
  0 to 4 s   a tall figure that is a window onto the night world (its own sky, stars and lake), and inside it a
             smaller figure that is a window inside the window, filled with one flat colour (nested windows);
             birds live in the night world (window="tall")
  4 to 8 s   two independent windows side by side: the tall figure onto the night world, and a word-like
             block of points filled with a flat coral, crisp (soft 0.5: the silhouettes are drawn at full size)
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

from p3d import Mask, StandIn, hash01, lin  # noqa: E402
from p3d.camera import Rig, dolly  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0


class Block:
    """Points filling a few letter-like strokes (a stand-in for a word made of points)."""

    def __init__(self, x0=1.4, y0=1.2, z=1.0, h=1.1):
        rects = [(0.0, 0.0, 0.16, 1.0), (0.48, 0.0, 0.16, 1.0), (0.0, 0.42, 0.64, 0.16),     # H
                 (0.86, 0.0, 0.16, 1.0),                                                       # I
                 (1.24, 0.0, 0.16, 1.0), (1.24, 0.84, 0.6, 0.16), (1.24, 0.42, 0.5, 0.16)]     # F
        n = 30000
        u, v, k = hash01(n, 71), hash01(n, 72), (hash01(n, 73) * len(rects)).astype(int)
        r = np.array(rects)[k]
        x = x0 + (r[:, 0] + u * r[:, 2]) * h
        y = y0 + (r[:, 1] + v * r[:, 3]) * h
        self.pos = np.stack([x, y, np.full(n, z)], axis=1)

    def sample(self, t):
        return dict(pos=self.pos, size=0.012, color=lin("#ffffff"), alpha=0.05)


class Birds:
    def sample(self, t):
        k = np.arange(30)
        s = np.mod(k / 30.0 + t * 0.07, 1.0)
        pos = np.stack([-3.2 + 2.4 * s, 1.2 + 2.0 * np.abs(np.sin(k * 1.7)) + 0.2 * np.sin(t + k), -0.6 + 0.3 * np.cos(k)], axis=1)
        return dict(pos=pos, size=0.16, color=lin("#ffffff"), kind="bird", alpha=0.9, rot=np.full(30, 0.2), seed=k / 30.0)


def _setup(scene):
    scene.add("tall", StandIn(pos=(-2.0, 0.0, -0.5), n=30000, height=3.6, color="#ffffff", bright=0.12, seed=6),
              mask=Mask("sky", sky="world", look="night", grow=0.07, edge=0.25))
    scene.add("birds", Birds(), window="tall")
    scene.add("inner", StandIn(pos=(-1.6, 0.0, 1.2), n=16000, height=1.7, color="#ffffff", bright=0.1, seed=8),
              window="tall", mask=Mask("sky", sky="flat", color="#ffd060", grow=0.05, soft=1.5,
                                       strength=lambda t: 1.0 if t < 4.0 else 0.0))
    scene.add("word", Block(), mask=Mask("sky", sky="flat", color="#f0566a", grow=0.02, soft=0.5,
                                         strength=lambda t: 1.0 if t >= 4.0 else 0.0))


P3D = dict(
    camera=Rig([dolly((0.0, 1.8, 9.5), (0.6, 1.8, 8.5), 0.0, 8.0, look=(0.0, 1.7, 0.0), fov=42, aperture=0.02)]),
    world=dict(look="day", sun_az=200.0),
    setup=_setup,
)
