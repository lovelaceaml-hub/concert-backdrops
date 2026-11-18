"""3D layer load test (8 seconds; engine/UPGRADE-HOWTO.md, section V). Not a concert video.

Heavy on purpose, to measure the time a frame takes and to see that nothing breaks under load:
  - a field of 2 million small points (a glittering meadow of light over the lake, static on the card)
  - 400 thousand points that move every frame (a churning cloud, sent each frame like a body or a wave)
  - 60 thousand line segments (a plexus net) with travelling pulses
  - everything mirrored in the lake, with a moving camera (motion blur) and a shallow depth of field
The counts can be changed for a measurement with the environment variables P3D_LOAD_STATIC, P3D_LOAD_MOVING
and P3D_LOAD_LINES (numbers of points and segments).
"""
import os

import numpy as np

import songs.s03_original as _base

_base.TOTAL = 8.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 7.8
_base.FADE = _base.Track([(0.0, 0.0), (0.3, 1.0), (7.7, 1.0), (7.98, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (8.0, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import hash01, lin  # noqa: E402
from p3d.camera import Rig, dolly, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

N_STATIC = int(os.environ.get("P3D_LOAD_STATIC", "2000000"))
N_MOVING = int(os.environ.get("P3D_LOAD_MOVING", "400000"))
N_LINES = int(os.environ.get("P3D_LOAD_LINES", "60000"))


class Meadow:
    """Two million small points over the water, lit from the far side (static: sent to the card once)."""
    static = True

    def sample(self, t):
        n = N_STATIC
        u, v, w, s = hash01(n, 1), hash01(n, 2), hash01(n, 3), hash01(n, 4)
        r = 4.0 + 90.0 * np.sqrt(u)
        a = v * 2 * np.pi
        pos = np.stack([r * np.sin(a), 0.15 + 2.2 * w ** 2, -20.0 + r * np.cos(a)], axis=1)
        col = np.stack([1.0 + 0.0 * s, 0.78 + 0.12 * s, 0.45 + 0.35 * s], axis=1) * 0.8
        return dict(pos=pos, size=0.012 + 0.02 * s ** 3, color=col, alpha=0.55, seed=s, twinkle=0.6,
                    birth=1.0 * w, fade=0.8)


class Churn:
    """Points that move every frame (sent each frame, as a body or a wave would be)."""

    def __init__(self):
        n = N_MOVING
        self.a, self.b, self.c = hash01(n, 11) * 6.2832, hash01(n, 12), hash01(n, 13)

    def sample(self, t):
        a = self.a + t * (0.3 + 0.5 * self.b)
        r = 1.5 + 2.5 * self.c + 0.3 * np.sin(t * 2.0 + self.b * 9.0)
        y = 1.0 + 3.0 * self.b + 0.4 * np.sin(a * 3.0 + t)
        pos = np.stack([r * np.cos(a), y, -6.0 + r * np.sin(a)], axis=1)
        vel = np.stack([-r * np.sin(a) * (0.3 + 0.5 * self.b), np.zeros_like(a), r * np.cos(a) * (0.3 + 0.5 * self.b)], axis=1)
        return dict(pos=pos, size=0.008 + 0.01 * self.c, color=lin("#9fc8ff"), alpha=0.5, vel=vel, twinkle=0.4)


class Net:
    """Line segments between near neighbours on a slowly turning shell, with pulses."""

    def __init__(self):
        n = N_LINES
        k = max(n // 3, 4)
        d = np.stack([hash01(k, 21), hash01(k, 22), hash01(k, 23)], axis=1) * 2.0 - 1.0
        d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
        self.p = d
        order = np.argsort(np.arctan2(d[:, 2], d[:, 0]) * 4.0 + d[:, 1])
        i = order
        self.ia = np.concatenate([i, i, i])[:n]
        self.ib = np.concatenate([np.roll(i, 1), np.roll(i, 7), np.roll(i, 31)])[:n]

    def sample(self, t):
        c, s = np.cos(t * 0.3), np.sin(t * 0.3)
        p = self.p @ np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]).T * 3.2 + np.array([5.0, 3.6, -9.0])
        a, b = p[self.ia], p[self.ib]
        return dict(pos=a, pos2=b, size=0.004, color=lin("#ffc890"), alpha=0.35, kind="line",
                    u=a[:, 1] * 3.0, u2=b[:, 1] * 3.0, pulse=(4.0, 0.6, 4.0, 5.0))


def _setup(scene):
    scene.add("meadow", Meadow())
    scene.add("churn", Churn())
    scene.add("net", Net())


P3D = dict(
    camera=Rig([
        dolly((-6.0, 1.6, 12.0), (2.0, 2.2, 6.0), 0.0, 4.0, look=(0.0, 2.0, -8.0), fov=50, aperture=0.05),
        orbit((0.0, 2.0, -8.0), radius=(14.0, 10.0), height=(2.5, 4.0), a0=10.0, a1=70.0, t0=4.0, t1=8.0, fov=46,
              aperture=0.04, blend=0.8),
    ], handheld=0.2),
    world=dict(look="dawn", sun_az=180.0),
    setup=_setup,
)
