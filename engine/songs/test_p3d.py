"""3D layer feature test (16 seconds; engine/UPGRADE-HOWTO.md, section V). Not a concert video.

One scene that uses every part of the 3D layer once, for stills and a short video:
  0 to 8 s    night. A slow close orbit with a shallow depth of field round three stand-in figures: one seen
              from behind as a dark body with a bright rim (Mask "dark") and a light with rays behind its head,
              one whose silhouette is a window onto a sunrise sky (Mask "sky"), one of glitter standing in a
              shaft of light. Flakes rise from the glitter figure, petals circle the window figure, birds
              leave it, a plexus ball and a ribbon float in front. The classic 2D words form over it all.
  8 s         a burst of light; inside it the world cuts to dawn and the camera whips to a second set-up.
  8 to 16 s   dawn, the same figures from the side, the end of the words.
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 16.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 15.6
_base.FADE = _base.Track([(0.0, 0.0), (0.6, 1.0), (15.2, 1.0), (15.95, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (16.0, 1.0)])
for _k, _p in enumerate(_base.PHRASES):
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.PHRASES[0].update(form=4.6, hold=13.0, star=14.5)        # one expression, to see the words over the 3D picture
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["song"] = "3D layer test"
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import Mask, StandIn, hash01, lin  # noqa: E402
from p3d.camera import Rig, dolly, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0


class Kinds:
    """Every kind of sprite once (a test, not a design)."""

    def __init__(self):
        rng = np.random.default_rng(5)
        self.f = rng.random((700, 4))          # flakes rising from the glitter figure
        self.p = rng.random((320, 4))          # petals round the window figure
        self.b = rng.random((16, 4))           # birds leaving it
        d = rng.normal(size=(220, 3))
        self.ball = d / np.linalg.norm(d, axis=1, keepdims=True)
        dist = np.linalg.norm(self.ball[:, None, :] - self.ball[None, :, :], axis=2)
        near = np.argsort(dist, axis=1)[:, 1:4]
        self.pairs = np.unique(np.sort(np.stack([np.repeat(np.arange(220), 3), near.reshape(-1)], axis=1), axis=1), axis=0)

    def sample(self, t):
        out = []
        # flakes: up from the head of the glitter figure, in a widening spiral (ref 05, 11, 13)
        f = self.f
        age = np.mod(f[:, 0] * 6.0 + t * 0.5, 6.0)
        ang = f[:, 1] * 6.2832 + age * (0.6 + f[:, 2])
        rad = 0.10 + 0.22 * age * (0.4 + f[:, 3])
        pos = np.stack([rad * np.cos(ang), 1.55 + 0.75 * age, -4.0 + rad * np.sin(ang)], axis=1)
        out.append(dict(pos=pos, size=0.035 + 0.05 * f[:, 3], color=lin("#ffe7b8"), kind="flake",
                        alpha=np.clip(age / 0.5, 0, 1) * np.clip((6.0 - age) / 2.0, 0, 1) * 0.9,
                        rot=np.stack([f[:, 1] * 6.28 + t * (0.5 + f[:, 2]), f[:, 2] * 6.28 + t * (1.0 + 2.0 * f[:, 0])], axis=1),
                        seed=f[:, 0]))
        # petals: a slow helix round the window figure (ref 07)
        p = self.p
        a2 = p[:, 0] * 6.2832 + t * (0.35 + 0.3 * p[:, 1])
        r2 = 0.45 + 0.5 * p[:, 2]
        pos = np.stack([2.2 + r2 * np.cos(a2), 0.3 + 1.6 * np.mod(p[:, 3] + t * 0.05, 1.0), r2 * np.sin(a2)], axis=1)
        out.append(dict(pos=pos, size=0.05 + 0.04 * p[:, 1], color=lin("#ff5a78"), kind="petal", alpha=0.85,
                        rot=np.stack([a2 * 1.3, p[:, 2] * 6.28 + t * (0.8 + p[:, 0])], axis=1), seed=p[:, 3]))
        # birds: leaving the window figure toward the upper right (ref 08)
        b = self.b
        s = np.mod(b[:, 0] + t * 0.07, 1.0)
        pos = np.stack([2.5 + 6.0 * s + 0.6 * b[:, 1], 1.7 + 2.6 * s + 0.5 * np.sin(b[:, 2] * 6.28 + t), 0.4 - 3.0 * s * b[:, 3]], axis=1)
        out.append(dict(pos=pos, size=0.22 + 0.12 * b[:, 1], color=lin("#dfe8ff"), kind="bird", alpha=0.9 * np.clip(s / 0.1, 0, 1) * np.clip((1 - s) / 0.2, 0, 1),
                        rot=np.full(16, 0.35), seed=b[:, 2]))
        # a plexus ball: points and lines to their nearest neighbours (ref 03, 12)
        c = np.array([-0.6, 1.15, 1.6])
        ca, sa = np.cos(t * 0.4), np.sin(t * 0.4)
        ball = self.ball @ np.array([[ca, 0, sa], [0, 1, 0], [-sa, 0, ca]]).T * 0.42 + c
        out.append(dict(pos=ball, size=0.022, color=lin("#bfe0ff"), kind="spark", alpha=0.9, emit=1.6, seed=hash01(220)))
        out.append(dict(pos=ball[self.pairs[:, 0]], pos2=ball[self.pairs[:, 1]], size=0.004, color=lin("#8fc4ff"),
                        kind="line", alpha=0.55))
        # a ribbon of light and a ring of flat dots (ref 14)
        u = np.linspace(0.0, 1.0, 90)
        rp = np.stack([0.9 + 0.5 * np.cos(u * 9.0 + t), 0.6 + 1.2 * u, 1.9 + 0.5 * np.sin(u * 9.0 + t)], axis=1)
        out.append(dict(pos=rp[:-1], pos2=rp[1:], size=0.05, color=lin("#ffc890"), kind="ribbon", alpha=0.7 * u[:-1], alpha2=0.7 * u[1:]))
        k = np.arange(40)
        dp = np.stack([-0.6 + 0.75 * np.cos(k * 0.157 + t * 0.2), np.full(40, 0.35), 1.6 + 0.75 * np.sin(k * 0.157 + t * 0.2)], axis=1)
        cols = np.stack([lin("#ff5fa8"), lin("#40d8e8"), lin("#b070ff"), lin("#ffd060")])[k % 4]
        out.append(dict(pos=dp, size=0.045, color=cols, kind="disc", alpha=0.9))
        return out


def _setup(scene):
    scene.add("rim", StandIn(pos=(-2.2, 0.0, 0.0), look="rim", facing=180.0, color="#ffb070", bright=1.6),
              mask=Mask("dark", strength=0.92))
    scene.add("window", StandIn(pos=(2.2, 0.0, 0.0), look="rim", color="#ffe9c8", bright=0.8, facing=20.0, seed=3),
              mask=Mask("sky", sky="sunrise", edge=0.5, grow=0.035))
    scene.add("glitter", StandIn(pos=(0.0, 0.0, -4.0), color="#ffe2b0", seed=4))
    scene.add("kinds", Kinds())


P3D = dict(
    camera=Rig([
        orbit((0.0, 1.15, 0.0), radius=(8.0, 6.6), height=(1.5, 1.8), a0=-22.0, a1=30.0, t0=0.0, t1=8.0, fov=36,
              aperture=0.07),
        dolly((7.5, 1.5, 2.6), (6.3, 1.6, 4.4), 8.0, 16.0, look=(0.6, 1.2, -0.6), fov=34, aperture=0.07, blend=0.4),
    ], handheld=0.3),
    bursts=[dict(t=8.0, strength=6.0, rise=0.3, fall=0.7, color="#fff1d8")],
    world=dict(
        look=[(0.0, "night"), (8.0, "dawn", 0.0)],
        sun_az=200.0,
        shafts=[dict(base=(0.0, -4.0), radius=1.2, top=26.0, spread=0.8, color="#9fc4ff", strength=0.6)],
        light=dict(pos=(-2.2, 1.62, -0.7), color="#ffd29a", strength=1.0, size=0.45, rays=1.0),
        arch=dict(z=-16.0, lit=[-5.0] * 9),
        lanterns=0.5,
        lantern_field=dict(center=(0.0, -30.0), radius=(10.0, 60.0)),
    ),
    setup=_setup,
)
