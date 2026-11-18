"""3D layer, second feature test (16 seconds; engine/UPGRADE-HOWTO.md, section V). Not a concert video.

The parts added for the ten films, each once:
  0 to 8 s    night with a sky of two looks (dawn on one side), a turning star dome, a storm lake with a
              disc of glass under the arch, the arch in nine colours whose lights fly in and which turns,
              two moving coloured lights (mist glow, pools on the water, colour on a `lit` figure), a ring
              of points lighting up one by one (birth times on a static set), comet ribbons with travelling
              pulses, plexus lines with pulses. Camera: an orbit whose speed follows `pace` keys, a camera
              that carries its own up through a loop (free=True), a shake at 6 s.
  8 to 16 s   day (a cut inside a burst): petals painted in their true colour beside the same petals as
              light alone, a figure that is a window onto the night world with birds living inside it, a
              keep-clear box in the upper middle, a dolly zoom, a rack focus, the camera riding a frame.
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 16.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 15.6
_base.FADE = _base.Track([(0.0, 0.0), (0.4, 1.0), (15.4, 1.0), (15.95, 0.0)])
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
from p3d import Frame, Mask, Parented, StandIn, Trail, lin, show  # noqa: E402
from p3d.camera import Rig, dolly, fly, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

NINE = ["#f0566a", "#4f8ff0", "#ffb070", "#ff8fc0", "#b79cff", "#ff6f91", "#ffd060", "#c98a6a", "#8f6cff"]


class BirthRing:
    """A ring of points on the water that light up one after the other (a static set with birth times)."""
    static = True

    def sample(self, t):
        k = np.arange(3000)
        a = k / 3000.0 * 2 * np.pi
        r = 16.0 + 0.5 * np.sin(k * 0.37)
        return dict(pos=np.stack([r * np.sin(a), np.full(3000, 0.25), r * np.cos(a)], axis=1), size=0.07,
                    color=lin("#ffe2a8"), alpha=0.9, birth=1.0 + 5.0 * k / 3000.0, fade=0.3, flash=4.0, twinkle=0.5)


class Plexus:
    """Lines with a pulse travelling along them."""

    def __init__(self):
        rng = np.random.default_rng(2)
        self.p = np.stack([rng.uniform(-5, 5, 260), rng.uniform(0.6, 5.5, 260), rng.uniform(-9, -4, 260)], axis=1)
        d = np.linalg.norm(self.p[:, None] - self.p[None], axis=2)
        near = np.argsort(d, axis=1)[:, 1:4]
        self.pairs = np.unique(np.sort(np.stack([np.repeat(np.arange(260), 3), near.reshape(-1)], axis=1), axis=1), axis=0)

    def sample(self, t):
        a, b = self.p[self.pairs[:, 0]], self.p[self.pairs[:, 1]]
        return [dict(pos=self.p, size=0.05, color=lin("#bfe0ff"), kind="spark", alpha=0.9),
                dict(pos=a, pos2=b, size=0.012, color=lin("#7fb8ff"), alpha=0.5, kind="line", u=a[:, 0] + a[:, 1],
                     u2=b[:, 0] + b[:, 1], pulse=(3.0, 0.5, 5.0, 6.0))]


class Petals:
    """The same drifting petals twice: painted (left) and as light alone (right)."""

    def __init__(self, x, paint):
        rng = np.random.default_rng(9)
        self.s, self.x, self.paint = rng.random((500, 4)), x, paint

    def sample(self, t):
        s = self.s
        a = s[:, 0] * 6.28 + t * (0.3 + 0.4 * s[:, 1])
        pos = np.stack([self.x + 1.6 * np.cos(a) * s[:, 2], 0.4 + 2.6 * np.mod(s[:, 3] + 0.04 * t, 1.0),
                        2.0 + 1.6 * np.sin(a) * s[:, 2]], axis=1)
        return dict(pos=pos, size=0.09 + 0.05 * s[:, 1], color=show("#f0566a"), kind="petal", alpha=0.95,
                    rot=np.stack([a, s[:, 2] * 6.28 + t * (1 + s[:, 0])], axis=1), paint=self.paint, paint_light=0.25)


class Birds:
    def sample(self, t):
        k = np.arange(40)
        s = np.mod(k / 40.0 + t * 0.06, 1.0)
        pos = np.stack([-3.0 + 6.0 * s, 0.6 + 1.8 * np.abs(np.sin(k * 1.7)) + 0.3 * np.sin(t + k), 0.0 + 0.5 * np.cos(k * 2.3)], axis=1)
        return dict(pos=pos, size=0.22, color=lin("#ffffff"), kind="bird", alpha=0.9, rot=np.full(40, 0.2), seed=k / 40.0)


def _comet(k):
    return lambda t: (9.0 * np.cos(0.9 * t + k * 2.1), 3.0 + 2.0 * np.sin(1.3 * t + k), -3.0 + 9.0 * np.sin(0.9 * t + k * 2.1))


def _setup(scene):
    scene.add("ring", BirthRing())
    scene.add("plexus", Plexus())
    for k in range(3):
        scene.add(f"comet{k}", Trail(_comet(k), length=1.6, width=0.22, color=lin(NINE[k * 3]), emit=2.0,
                                     pulse=(6.0, 0.8, 3.0, 5.0)))
    scene.add("lit", StandIn(pos=(0.0, 0.0, 3.0), look="rim", color="#9aa0b0", bright=0.6, seed=5))
    scene.get("lit").sample = (lambda f: lambda t: dict(f(t), lit=1.0, rim=(0.0, 2.0)))(scene.get("lit").sample)
    scene.add("petals_painted", Petals(-3.4, 1.0))
    scene.add("petals_light", Petals(3.4, 0.0))
    scene.add("window", StandIn(pos=(0.0, 0.0, 0.0), n=30000, height=3.4, color="#ffffff", bright=0.25, seed=6),
              mask=Mask("sky", sky="world", look="night", grow=0.07, edge=0.3, strength=lambda t: 1.0 if t >= 8.0 else 0.0))
    scene.add("birds", Birds(), window=True)


RIDE = Frame(origin=lambda t: (0.6 * np.sin(0.5 * t), 0.0, 0.0))
CAMERA = Rig([
    orbit((0.0, 5.0, 0.0), radius=(36.0, 26.0), height=(3.0, 7.0), a0=-30.0, a1=80.0, t0=0.0, t1=4.5, fov=46,
          pace=[(0.0, 0.0), (0.6, 0.35), (3.0, 0.55), (4.5, 1.0)]),
    fly([(4.5, (25.0, 7.0, 5.0), (0.0, 6.0, 0.0)), (5.6, (6.0, 16.0, 6.0), (0.0, 0.0, 0.0)),
         (6.6, (-8.0, 9.0, -6.0), (0.0, 20.0, 0.0)), (8.0, (-14.0, 3.0, 16.0), (0.0, 5.0, 0.0))], fov=50, blend=1.0),
    dolly((0.0, 1.7, 20.0), (0.0, 1.7, 7.5), 8.0, 12.0, look=(0.0, 1.6, 0.0), keep_width=9.0, blend=0.0,
          aperture=0.06, focus=Track([(8.0, 4.0), (10.0, 4.0), (11.0, 9.0)]), near=0.02),
    dolly((-7.0, 2.4, 9.0), (-5.5, 2.0, 8.0), 12.0, 16.0, look=(0.0, 1.7, 0.5), fov=38, blend=0.4, ease="out",
          aperture=0.04),
], free=True, shake=Track([(5.8, 0.0), (6.0, 1.6), (6.7, 0.0)]), parent=RIDE, handheld=0.2)

P3D = dict(
    camera=CAMERA,
    bursts=[dict(t=8.0, strength=6.0, rise=0.3, fall=0.6)],
    clear=[dict(box=(0.30, 0.62, 0.70, 0.92), t0=8.5, t1=15.5, soft=0.05)],
    world=dict(
        look=[(0.0, "night"), (8.0, "day", 0.0)],
        split=dict(look="dawn", toward=90.0, soft=0.4, amount=Track([(0.0, 1.0), (7.9, 1.0), (8.0, 0.0)])),
        sun_az=Track([(0.0, 90.0), (7.9, 90.0), (8.0, 200.0)]),
        star_turn=lambda t: 6.0 * t,
        ripple=Track([(0.0, 2.6), (7.9, 2.6), (8.0, 0.5)]),
        calm=[dict(center=(0.0, 0.0), radius=lambda t: 6.0 + 2.5 * t, ripple=0.0, mirror=1.0)],
        lights=[dict(pos=lambda t: (7.0 * np.cos(t), 1.6, 3.0 + 7.0 * np.sin(t)), color="#ff5a3c", strength=1.6, radius=3.0),
                dict(pos=lambda t: (-7.0 * np.cos(t), 2.2, 3.0 - 7.0 * np.sin(t)), color="#3c8cff", strength=1.6, radius=3.0)],
        arch=dict(lit=[1.0 + 0.4 * k for k in range(9)], colors=NINE, z=-2.0, yaw=lambda t: 25.0 * np.sin(0.4 * t),
                  line=Track([(0.0, 0.0), (5.0, 0.0), (6.0, 1.0)]),
                  travel=dict(start=(0.0, 0.3, 14.0), t=[1.6 + 0.4 * k for k in range(9)], dur=1.4)),
        floats=0.5,
    ),
    setup=_setup,
)
