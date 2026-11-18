"""3D layer checks (16 seconds; engine/UPGRADE-HOWTO.md, section V). Not a concert video.

One small set-up per two seconds (cuts between them), each for one still:
  0 to 2     a keep-clear box in the upper middle of a field of lights, ribbons and lines; hexagonal bokeh
  2 to 4     a figure lit by two moving coloured lights (lit=1, with normals) close by; the blue light throws
             rays past the figure (lights rays=1)
  4 to 6     macro: the camera 5 cm from a cluster of points the size of a fingertip (near 0.02, focus 0.06)
  6 to 8     night: lines with strong travelling pulses, the star dome turning fast (star_turn), a ring of
             points riding a moving frame (Parented) and the camera riding the same frame (Rig parent)
  8 to 10    bright coloured lights with keep_hue 1 (they keep their colour)
  10 to 12   the same lights with keep_hue 0 (they bleach toward white)
  12 to 14   the arch of nine lights close up, nine colours, all lit, at full size
  14 to 16   night with a dawn behind a world point (split toward a place, cover 0.65)
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 16.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 15.6
_base.FADE = _base.Track([(0.0, 0.0), (0.2, 1.0), (15.7, 1.0), (15.98, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (16.0, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import Frame, Parented, StandIn, hash01, lin, ribbon  # noqa: E402
from p3d.camera import Rig, hold  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

NINE = ["#FF977C", "#FFD05F", "#FFAD69", "#F582AF", "#82B0ED", "#CE927E", "#B293E7", "#EF7A96", "#BE9CEB"]


def _during(t0, t1):
    return lambda t: 1.0 if t0 <= t < t1 else 0.0


class Field:
    """Lights, ribbons and lines all over the view (0 to 2 s), for the keep-clear box."""

    def __init__(self):
        n = 6000
        self.p = np.stack([(hash01(n, 1) - 0.5) * 16.0, 0.3 + hash01(n, 2) * 7.0, -6.0 - hash01(n, 3) * 10.0], axis=1)

    def sample(self, t):
        if t >= 2.0:
            return None
        u = np.linspace(0.0, 1.0, 120)
        rib = ribbon(np.stack([-7 + 14 * u, 3.5 + 2.5 * np.sin(u * 7 + t), -5.0 + 0 * u], axis=1), width=0.12,
                     color=lin("#ffb070"), emit=2.0)
        a, b = self.p[:400], self.p[400:800]
        return [dict(pos=self.p, size=0.05, color=lin("#ffe2b0"), alpha=0.8, emit=1.5),
                dict(pos=self.p[:60] + np.array([0.0, 0.0, 7.0]), size=0.25, color=lin("#bcd0ff"), alpha=0.9, emit=2.0),
                rib, dict(pos=a, pos2=b, size=0.006, color=lin("#9fc8ff"), alpha=0.4, kind="line")]


class LitFigure(StandIn):
    def sample(self, t):
        b = super().sample(t)
        return dict(b, lit=1.0, rim=(0.0, 2.0)) if 2.0 <= t < 4.0 else None


class Tip:
    """A fingertip-sized cluster of points (4 to 6 s)."""

    def __init__(self):
        n = 2500
        d = np.stack([hash01(n, 11), hash01(n, 12), hash01(n, 13)], axis=1) * 2.0 - 1.0
        d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
        self.p = d * np.array([0.008, 0.012, 0.008]) * (0.85 + 0.15 * hash01(n, 14)[:, None]) + np.array([0.0, 1.0, 0.0])

    def sample(self, t):
        if not 4.0 <= t < 6.0:
            return None
        return dict(pos=self.p, size=0.0003, color=lin("#ffd9a0"), alpha=0.35, twinkle=0.6)


class Pulses:
    """Lines with strong pulses, round the camera's frame (6 to 8 s)."""

    def __init__(self):
        k = 240
        a = np.linspace(0, 2 * np.pi, k, endpoint=False)
        self.p = np.stack([6.0 * np.cos(a), 1.5 + 1.2 * np.sin(a * 5.0), -14.0 + 6.0 * np.sin(a)], axis=1)

    def sample(self, t):
        if not 6.0 <= t < 8.0:
            return None
        a, b = self.p, np.roll(self.p, -1, axis=0)
        u = np.cumsum(np.r_[0.0, np.linalg.norm(np.diff(self.p, axis=0), axis=1)])
        return dict(pos=a, pos2=b, size=0.02, color=lin("#8fc4ff"), alpha=0.5, kind="line", u=u, u2=u + np.linalg.norm(b - a, axis=1),
                    pulse=(8.0, 1.0, 6.0, 12.0))


class Ring:
    def sample(self, t):
        if not 6.0 <= t < 8.0:
            return None
        a = np.linspace(0, 2 * np.pi, 400, endpoint=False)
        return dict(pos=np.stack([1.2 * np.cos(a), 1.6 + 0.3 * np.sin(3 * a), -4.0 + 1.2 * np.sin(a)], axis=1), size=0.03,
                    color=lin("#ffd060"), alpha=0.9, emit=2.0)


class Hues:
    """Very bright coloured lights (8 to 12 s)."""

    def sample(self, t):
        if not 8.0 <= t < 12.0:
            return None
        cols = np.array([lin(c) for c in ("#ff5a3c", "#3c8cff", "#ffd060", "#f582af", "#40d8a0")])
        k = np.arange(5)
        pos = np.stack([-3.2 + 1.6 * k, np.full(5, 1.6), np.full(5, -3.0)], axis=1)
        return [dict(pos=pos, size=0.35, color=cols, alpha=1.0, emit=12.0, dof=0.0),
                dict(pos=pos, size=1.6, color=cols, alpha=0.6, emit=2.5, dof=0.0)]


RIDE = Frame(origin=lambda t: (0.0, 0.0, -1.5 * max(t - 6.0, 0.0)) if 6.0 <= t < 8.0 else (0.0, 0.0, 0.0),
             yaw=lambda t: 20.0 * max(t - 6.0, 0.0) if 6.0 <= t < 8.0 else 0.0)


def _setup(scene):
    scene.add("field", Field())
    scene.add("lit", LitFigure(pos=(0.0, 0.0, 0.0), color="#b0b4c0", bright=0.7, seed=5, look="rim"))
    scene.add("tip", Tip(), lod=False)
    scene.add("pulses", Pulses())
    scene.add("ring", Parented(Ring(), RIDE))
    scene.add("hues", Hues())


def _cut(m):
    m.blend = 0.0
    return m


CAMERA = Rig([
    hold((0.0, 3.0, 8.0), (0.0, 3.5, -8.0), 0.0, 2.0, fov=50, aperture=0.08, focus=30.0),
    _cut(hold((0.4, 1.4, 3.2), (0.0, 1.0, 0.0), 2.0, 4.0, fov=34, aperture=0.02)),
    _cut(hold((0.0, 1.0, 0.055), (0.0, 1.0, 0.0), 4.0, 6.0, fov=40, aperture=0.004, focus=0.055, near=0.02)),
    _cut(hold((0.0, 1.7, 2.0), (0.0, 3.0, -10.0), 6.0, 8.0, fov=60, aperture=0.0)),
    _cut(hold((0.0, 1.6, 4.0), (0.0, 1.6, -3.0), 8.0, 10.0, fov=40, aperture=0.0)),
    _cut(hold((0.0, 1.6, 4.0), (0.0, 1.6, -3.0), 10.0, 12.0, fov=40, aperture=0.0)),
    _cut(hold((3.0, 5.0, 14.0), (0.0, 7.0, 0.0), 12.0, 14.0, fov=55, aperture=0.03)),
    _cut(hold((0.0, 2.0, 30.0), (0.0, 6.0, 0.0), 14.0, 16.0, fov=70, aperture=0.0)),
], handheld=0.0, parent=Frame(origin=lambda t: RIDE.at(t)[0], yaw=lambda t: 20.0 * max(t - 6.0, 0.0) if 6.0 <= t < 8.0 else 0.0))

P3D = dict(
    camera=CAMERA,
    clear=lambda t: [dict(box=(0.35, 0.55, 0.65, 0.85), soft=0.02)] if t < 2.0 else [],
    world=dict(
        look=[(0.0, "night"), (8.0, "night", 0.0), (12.0, "dusk", 0.0), (14.0, "night", 0.0)],
        bokeh_hex=lambda t: 1.0 if t < 2.0 else 0.0,
        star_turn=lambda t: 40.0 * max(t - 6.0, 0.0) if 6.0 <= t < 8.0 else 0.0,
        keep_hue=lambda t: 1.0 if 8.0 <= t < 10.0 else 0.0,
        lights=[dict(pos=lambda t: (0.9 * np.cos(2 * t), 1.3, 0.9 * np.sin(2 * t)), color="#ff5a3c",
                     strength=lambda t: 1.6 if 2.0 <= t < 4.0 else 0.0, radius=1.0),
                dict(pos=lambda t: (-0.4, 1.7, -1.2), color="#3c8cff", strength=lambda t: 1.4 if 2.0 <= t < 4.0 else 0.0,
                     radius=1.0, rays=1.0, size=0.5)],
        arch=dict(lit=[-5.0] * 9, colors=NINE, line=1.0),
        split=dict(look="dawn", toward=(-200.0, 0.0, -300.0), soft=0.3, cover=0.65,
                   amount=lambda t: 1.0 if t >= 14.0 else 0.0),
    ),
    setup=_setup,
)
