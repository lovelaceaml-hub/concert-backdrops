"""One continuous original fan-and-silk trio over a luminous mirror lake.

Available reference posters inform the broad fan fabric and ensemble staging.
The choreography is authored here; the linked reference motion was unavailable.
"""
import os
from pathlib import Path

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

from p3d.api import lin, ribbon
from p3d.body import Body
from p3d import looks
from p3d.camera import Rig, dolly
from tools.concert_fan.performance import install_performance
from tools.concert_fan.props import FanSilk
from tools.concert_kit.models import Willow, Flowers, Lantern, segments, smooth

TOTAL = 20.0
CUTS = ()
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
_PERFORMERS = None
_FANS = None


class Song:
    """A restrained visual envelope; no source instrument analysis is claimed."""
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


def _garment_palette(body, upper, lower):
    """Give the ordinary golden figures modest lavender and pearl garments."""
    for layer in body.layers:
        idx = layer["idx"]
        part = body.cloud["part"][idx]
        h = body.cloud["h"][idx]
        colour = np.array(layer["color"], copy=True)
        colour = np.broadcast_to(colour, (len(idx), 3)).copy()
        cloth = (part == looks.CLOTH) | (part == looks.VEIL)
        mix = smooth(.43, .63, h)
        tint = lin(lower)[None] * (1 - mix[:, None]) + lin(upper)[None] * mix[:, None]
        colour[cloth] = tint[cloth]
        layer["color"] = colour
        layer["alpha"] = np.asarray(layer["alpha"]) * np.where(
            part == looks.HAND, .43, np.where(part == looks.FOOT, .62, 1.0))


def performers():
    global _PERFORMERS
    if _PERFORMERS is None:
        common = dict(points=82000, detail=dict(hand=3.8, head=1.8, foot=2.2),
                      bright=1.34, wind=(.045, 0, .014), gust=.025,
                      look=[dict(name="glitter", bright=1.03, seams=.50, glints=.00020),
                            dict(name="rim", bright=.28, power=3.8)])
        spec = [((-1.55, 0, .40), 1.65, "dress", "#ceb3e9", "#f0dfc8", 43),
                ((1.50, 0, -.05), 1.69, "robe", "#b2bfe3", "#ecdfd3", 67),
                ((0, 0, -1.90), 1.62, "dress", "#e2b3c9", "#f1dcc1", 89)]
        result = []
        for role, (at, height, garment, upper, lower, seed) in enumerate(spec):
            body = Body("woman", height=height, at=at, facing=0, garment=garment,
                        hair="bun", color="#ecc88c", color2="#ffe8bf",
                        build=.95 + role * .015, seed=seed, **common)
            _garment_palette(body, upper, lower)
            performance = install_performance(body, role=role, duration=TOTAL)
            result.append((body, performance))
        _PERFORMERS = tuple(result)
    return _PERFORMERS


def fans():
    global _FANS
    if _FANS is None:
        # The prop owns a content-and-motion cache key. Camera and palette
        # iteration should not discard an unchanged physical bake.
        cache_dir = Path(__file__).resolve().parents[2] / "work/fan-silk-performance/cloth-cache"
        _FANS = tuple(FanSilk(performers()[role][0], side="R", duration=TOTAL,
                             color=colour, cache_dir=cache_dir)
                      for role, colour in ((0, "#c9a8ef"), (1, "#efdac5")))
    return _FANS


class Terrace:
    """A quiet circular support plane with space for the complete fan shapes."""
    static = True

    def __init__(self):
        a = np.linspace(0, 2 * np.pi, 280)
        self.rims = [np.stack([r * 4.75 * np.cos(a), np.full(len(a), .008),
                              -.25 + r * 3.70 * np.sin(a)], 1) for r in (1, 1.018, 1.045)]
        rng = np.random.default_rng(20261121)
        a = rng.uniform(0, 2 * np.pi, 8200)
        r = np.sqrt(rng.random(len(a)))
        self.floor = np.stack([4.72 * r * np.cos(a), np.full(len(a), .002),
                               -.25 + 3.67 * r * np.sin(a)], 1)

    def sample(self, t):
        return [segments(self.rims, "#a7a0cd", .006, .14),
                dict(pos=self.floor, size=.010, color=lin("#a5a7cc"), alpha=.042,
                     kind="soft", twinkle=0)]


class CalmStars:
    static, dome, turns = True, True, True

    def __init__(self, original):
        self.original = original

    def sample(self, t):
        batch = dict(self.original.sample(t)[0])
        batch["alpha"] = batch["alpha"] * smooth(.05, .35, batch["pos"][:, 1])
        batch["size"] = batch["size"] * .78
        batch["twinkle"] = .14
        return batch

    def gain(self, t):
        return self.original.gain(t)


class CelestialGarden:
    """Tall distant petal arches give depth without crossing the performers."""
    def sample(self, t):
        out = []
        reveal = .15 + .85 * float(smooth(6, 16.0, t))
        for i in range(5):
            u = np.linspace(0, 1, 190)
            phase = (i - 2) * .12
            p = np.stack([(5.0 + i * .27) * np.cos(np.pi * u) + phase,
                          .25 + (4.9 + i * .25) * np.sin(np.pi * u) ** .84,
                          np.full(len(u), -7.5 - i * .65)], 1)
            col = ("#9783ca", "#b2a0dc", "#e2bf91", "#c4b3df", "#9e93c8")[i]
            out.append(ribbon(p, width=.008 if i != 2 else .013,
                              color=lin(col), alpha=reveal * (.14 if i != 2 else .20),
                              emit=1.05, twinkle=0))
        # The quiet waves follow the ensemble's resolving phrase.
        for i in range(3):
            age = t - 13.6 - i * .7
            if age <= 0:
                continue
            a = np.linspace(0, 2 * np.pi, 200)
            radius = .35 + .65 * age
            p = np.stack([radius * np.cos(a), np.full(len(a), .012),
                          -.35 + radius * np.sin(a)], 1)
            out.append(ribbon(p, width=.010, color=lin("#c1abe5"),
                              alpha=.12 * np.exp(-age / 3.2), twinkle=0))
        return out


class SilkLight:
    """A small closing release of light born at the real cloth's free edge."""
    def __init__(self, prop, side, seed):
        self.prop, self.side = prop, side
        rng = np.random.default_rng(seed)
        self.birth = rng.uniform(13.1, 17.6, 96)
        self.life = rng.uniform(2.2, 4.2, 96)
        self.material = rng.integers(0, prop.cols, 96)
        self.start = np.array([prop.positions(float(t))[-1, int(c)]
                               for t, c in zip(self.birth, self.material)])
        self.phase = rng.uniform(0, 2 * np.pi, 96)
        self.size = rng.uniform(.010, .024, 96)

    def sample(self, t):
        age = t - self.birth
        keep = (age >= 0) & (age <= self.life)
        if not np.any(keep):
            return None
        a, phase = age[keep], self.phase[keep]
        p = self.start[keep].copy()
        p[:, 0] += self.side * .24 * a + .10 * np.sin(phase + a * 1.4) * a
        p[:, 1] += .34 * a + .045 * a * a
        p[:, 2] -= .16 * a
        fade = np.sin(np.pi * a / self.life[keep]) ** .8
        return dict(pos=p, size=self.size[keep], color=lin("#e9c6ec"),
                    alpha=.26 * fade, emit=1.35, kind="spark", twinkle=.20)


def setup(scene):
    scene.add("_stars", CalmStars(scene.get("_stars")), reflect=False, fog=False)
    scene.add("performance_terrace", Terrace())
    for i, (body, _) in enumerate(performers()):
        body.add(scene, "fan_dancer_" + str(i), mask=dict(strength=.25, grow=0.0))
    for i, prop in enumerate(fans()):
        prop.prebake()
        scene.add("held_fan_and_silk_" + str(i), prop)
        scene.add("closing_silk_light_" + str(i), SilkLight(prop, -1 if i == 0 else 1, 431 + i))
    scene.add("celestial_garden", CelestialGarden())
    for i, (x, z) in enumerate(((-6.4, -5.8), (6.8, -7.1))):
        tree = Willow(at=(x, 0, z), height=4.6 + i * .65, spread=2.35,
                      variant="blossom", bloom=10.0 + i * .5, seed=91 + i)
        tree.gain = lambda t: .43
        scene.add("distant_blossom_" + str(i), tree)
    for i, (x, z) in enumerate(((-5.1, .6), (5.3, -.3), (-5.5, -3.2), (5.8, -4.1))):
        flower = Flowers(at=(x, 0, z), count=12, radius=.65, height=.30,
                         bloom=12.2 + i * .2, seed=112 + i)
        flower.gain = lambda t: .48
        scene.add("shore_flower_" + str(i), flower)
    for i, (x, z) in enumerate(((-4.9, -2.6), (5.2, -3.5), (-6.1, -6.4), (6.3, -8))):
        scene.add("shore_lantern_" + str(i), Lantern(at=(x, .32, z), size=.17,
                  seed=140 + i, lit=0, variant="cup"))


CAMERA = Rig([
    dolly((.40, 1.85, 7.10), (-.40, 2.05, 7.60), 0, 14.0,
          look=(-.05, 1.25, -.50), fov=38, aperture=.004, ease="smooth", blend=0),
    dolly((-.40, 2.05, 7.60), (.60, 2.80, 9.20), 14.0, 20.0,
          look=[(-.05, 1.25, -.50), (-.05, 1.65, -.75)], fov=38,
          aperture=.005, ease="smooth", blend=1.8),
], blend=1.8, shutter=.34, handheld=0, near=.1)

P3D = dict(camera=CAMERA, setup=setup, motion_samples=2, bokeh_max=.025, world=dict(
    look="night", sky_top="#020510", sky_mid="#0b1530", sky_hor="#39304d",
    sun_int=.075, sun_el=-8, sun_az=175, sun_glow=.28, sun_disc=0,
    stars=.22, milky=.15, clouds=.09, haze=.06, mist=.030, mist_height=.20,
    water="#040717", mirror=.83, mirror_min=.20, ripple=.14,
    dust=.012, bokeh=.005, lanterns=0, floats=.018, hills=1, hill_height=.66,
    exposure=.97, keep_hue=.64, dust_field=dict(n=420, n_bokeh=8),
    float_field=dict(count=54, center=(0, -12), radius=(8, 60)), lights=[]))
