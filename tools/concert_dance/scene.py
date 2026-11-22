"""A continuous dance duet in a quiet, luminous lakeside amphitheatre.

Captured whole-body movement leads. The hand trails inherit actual posed hand
positions, while the shore response follows the end of the physical phrase.
"""
import os
import numpy as np
import songs.s03_original as _base

_base.FPS = int(os.environ.get("OUT_FPS", "60"))
_base.TOTAL = 18.0
_base.NFRAMES = round(_base.TOTAL * _base.FPS)
_base.MUSIC_END = 18.0
_base.FADE = _base.Track([(0, 1), (18, 1)])
_base.EXPOSURE = _base.Track([(0, 1), (18, 1)])
for _phrase in _base.PHRASES:
    _phrase["form"] = _phrase["hold"] = _phrase["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 1)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d.api import lin, ribbon
from p3d.body import Body
from p3d import looks
from p3d.camera import Rig, dolly
from tools.concert_dance.performance import install_dance
from tools.concert_kit.models import Willow, Flowers, Lantern, segments, smooth

TOTAL = 18.0
CUTS = ()
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
_PERFORMERS = None
_HAND_TRACKS = {}


class Song:
    """Authored visual envelopes, not inferred instrument separation."""
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


def performers():
    global _PERFORMERS
    if _PERFORMERS is None:
        common = dict(points=82000, detail=dict(hand=3.8, head=1.8, foot=2.2),
                      bright=1.08, wind=(.055, 0, .018), gust=.035,
                      look=[dict(name="glitter", bright=.88, seams=.55, glints=.00025),
                            dict(name="rim", bright=.22, power=3.8)])
        a = Body("woman", height=1.65, at=(-1.30, 0, .12), facing=12,
                 garment="dress", hair="bun", color="#eab875", color2="#ffe6c3",
                 build=.96, seed=43,
                 gesture=[(14.1, 21.0, "hand_on_heart",
                           dict(side="R", bow=6, ease_in=1.7, antic=0, over=0))],
                 **common)
        b = Body("man", height=1.76, at=(1.40, 0, -.18), facing=16,
                 garment="coat", hair="short", color="#eec994", color2="#fff0cb",
                 build=.94, seed=67,
                 gesture=[(14.8, 21.0, "after_you",
                           dict(side="R", bow=5, ease_in=1.7, antic=0, over=0))],
                 **common)
        # Dense sampling preserves fingers; regional exposure keeps their
        # overlapping particles from becoming white gloves or white shoes.
        for body in (a, b):
            for layer in body.layers:
                part = body.cloud["part"][layer["idx"]]
                gain = np.where(part == looks.HAND, .43,
                                np.where(part == looks.FOOT, .65, 1.0))
                layer["alpha"] = np.asarray(layer["alpha"]) * gain
        pa = install_dance(a, start=2.0, rate=1.0, prepare_seconds=2.0, settle_seconds=2.5)
        pb = install_dance(b, start=2.6, rate=1.0, prepare_seconds=2.6, settle_seconds=2.5)
        _PERFORMERS = ((a, pa), (b, pb))
    return _PERFORMERS


class Terrace:
    """An open ellipse at the true support plane, without crossing vegetation."""
    static = True

    def __init__(self):
        a = np.linspace(0, 2 * np.pi, 240)
        self.rims = [np.stack([r * 4.10 * np.cos(a), np.full(len(a), .008),
                              .65 + r * 3.20 * np.sin(a)], 1) for r in (1, 1.018, 1.055)]
        rng = np.random.default_rng(20261121)
        a = rng.uniform(0, 2 * np.pi, 7000)
        r = np.sqrt(rng.uniform(0, 1, len(a)))
        self.floor = np.stack([4.08 * r * np.cos(a), np.full(len(a), .002),
                               .65 + 3.18 * r * np.sin(a)], 1)

    def sample(self, t):
        return [segments(self.rims, "#a1a4ca", .006, .17),
                dict(pos=self.floor, size=.011, color=lin("#9ca7c6"), alpha=.052,
                     kind="soft", twinkle=0)]


class HandSilk:
    """History-derived ribbons, with tails that float after the actual wrists."""
    def __init__(self, body, performance, color, side="R", flow=0):
        self.body, self.performance, self.color = body, performance, color
        self.side = side
        self.flow = float(flow)
        key = id(body)
        if key not in _HAND_TRACKS:
            times = np.arange(0, TOTAL + 1 / 60, 1 / 60)
            # Both hands share each solved pose, avoiding a second full seek.
            pairs = np.array([[body.where(float(t), "palm." + s)
                               for s in ("L", "R")] for t in times])
            _HAND_TRACKS[key] = times, pairs
        self.times, pairs = _HAND_TRACKS[key]
        self.points = pairs[:, 0 if side == "L" else 1]

    def sample(self, t):
        gain = float(smooth(1.3, 3.3, t) * (1 - smooth(13.2, 16.5, t)))
        if gain < .002:
            return None
        age = np.linspace(2.20 if self.side == "R" else 1.20, 0, 260)
        sampled = np.clip(t - age, self.times[0], self.times[-1])
        p = np.stack([np.interp(sampled, self.times, self.points[:, axis]) for axis in range(3)], 1)
        # The endpoint is exact; only detached older material drifts in the air.
        p[:, 0] += self.flow * .35 * age ** 1.5
        p[:, 1] += .30 * age ** 1.2
        p[:, 2] -= .10 * age ** 1.5
        p[-1] = self.body.where(t, "palm." + self.side)
        w = .006 + (.070 if self.side == "R" else .025) * np.sin(
            np.pi * np.linspace(0, 1, len(p))) ** .8
        alpha = gain * np.linspace(0, .34 if self.side == "R" else .20, len(p))
        # Overlapping soft grains avoid visible rectangular joins on broad
        # curved bands. Arc-length weighting keeps tight bends from flaring.
        ds = np.linalg.norm(np.gradient(p, axis=0), axis=1)
        haze = alpha * np.minimum(ds / np.maximum(w, .008), .5) * 1.6
        return [dict(pos=p, size=w * 1.5, color=lin(self.color), alpha=haze,
                     kind="soft", emit=1.1, twinkle=0, streak=False),
                ribbon(p, width=.006, color=lin(self.color), alpha=alpha * .72,
                       emit=1.1, twinkle=0, streak=False)]


class CalmStars:
    """Small celestial points above the horizon, clear of the performance floor."""
    static, dome, turns = True, True, True

    def __init__(self, original):
        self.original = original

    def sample(self, t):
        batch = dict(self.original.sample(t)[0])
        batch["alpha"] = batch["alpha"] * smooth(.05, .35, batch["pos"][:, 1])
        batch["size"] = batch["size"] * .8
        batch["twinkle"] = .18
        return batch

    def gain(self, t):
        return self.original.gain(t)


class ShoreAnswer:
    """A large quiet arc follows the completed human phrase."""
    def sample(self, t):
        reveal = float(smooth(11.6, 15.8, t))
        if reveal < .002:
            return None
        out = []
        for i, col in enumerate(("#9f87dd", "#c6b3e7", "#edc795")):
            u = np.linspace(0, reveal, 160)
            p = np.stack([-6.8 + 13.6 * u, 1.4 + (4.3 + i * .15) * np.sin(np.pi * u),
                          -4.8 - 1.2 * np.sin(np.pi * u) - i * .10], 1)
            out.append(ribbon(p, width=.014 - .002 * i, color=lin(col), alpha=.30 - .045 * i, emit=1.1))
        for i in range(3):
            age = t - 12.0 - .65 * i
            if age <= 0:
                continue
            a = np.linspace(0, 2 * np.pi, 180)
            radius = .6 + age * 1.05
            p = np.stack([radius * np.cos(a), np.full(len(a), .01), .8 + radius * np.sin(a)], 1)
            out.append(ribbon(p, width=.013, color=lin("#ada2e5"), alpha=.16 * np.exp(-age / 3.0)))
        return out


def setup(scene):
    scene.add("_stars", CalmStars(scene.get("_stars")), reflect=False, fog=False)
    scene.add("open_performance_terrace", Terrace())
    for i, (body, performance) in enumerate(performers()):
        body.add(scene, "dancer_" + str(i))
        scene.add("silk_right_" + str(i), HandSilk(body, performance, "#b69be6", "R",
                                                flow=1 if i == 0 else -1))
        scene.add("silk_left_" + str(i), HandSilk(body, performance, "#f1c890", "L"))
    scene.add("shore_answer", ShoreAnswer())
    for i, (x, z) in enumerate(((-5.5, -4.0), (6.3, -6.0))):
        tree = Willow(at=(x, 0, z), height=4.0 + i * .7, spread=2.3,
                      variant="blossom", bloom=12.0 + i * .4, seed=91 + i)
        tree.gain = lambda t: .52
        scene.add("perimeter_tree_" + str(i), tree)
    for i, (x, z) in enumerate(((-5.0, 1.4), (5.0, .8), (-5.5, -2.8), (5.7, -3.8))):
        flower = Flowers(at=(x, 0, z), count=14, radius=.8, height=.33,
                         bloom=11.8 + i * .2, seed=112 + i)
        flower.gain = lambda t: .60
        scene.add("perimeter_flowers_" + str(i), flower)
    for i, (x, z) in enumerate(((-4.6, -2.8), (4.9, -4.2), (-6.5, -6.2), (6.7, -8))):
        scene.add("shore_lantern_" + str(i), Lantern(at=(x, .36, z), size=.19,
                  seed=140 + i, lit=0, variant="cup"))


CAMERA = Rig([
    dolly((.65, 1.85, 7.05), (-.35, 1.90, 7.20), 0, 14.0,
          look=(-.10, 1.03, .65), fov=34, aperture=.006, ease="smooth", blend=0),
    dolly((-.35, 1.90, 7.20), (1.20, 3.00, 10.3), 14.0, 18.0,
          look=[(-.10, 1.03, .65), (-.10, 1.45, -.1)], fov=36,
          aperture=.007, ease="smooth", blend=1.8),
], blend=1.8, shutter=.34, handheld=0, near=.1)

P3D = dict(camera=CAMERA, setup=setup, motion_samples=2, bokeh_max=.025, world=dict(
    look="night", sky_top="#020510", sky_mid="#0c1530", sky_hor="#39304c",
    sun_int=.08, sun_el=-8, sun_az=175, sun_glow=.30, sun_disc=0,
    stars=.20, milky=.16, clouds=.10, haze=.07, mist=.035, mist_height=.22,
    water="#040717", mirror=.82, mirror_min=.22, ripple=.15,
    dust=.012, bokeh=.006, lanterns=0, floats=.020, hills=1, hill_height=.7,
    exposure=.97, keep_hue=.62, dust_field=dict(n=520, n_bokeh=10),
    float_field=dict(count=60, center=(0, -12), radius=(8, 60)), lights=[]))
