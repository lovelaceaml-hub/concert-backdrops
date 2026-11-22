"""Traveling lantern procession and an acted reunion in native 3D light."""
from __future__ import annotations

import numpy as np

from p3d.api import lin, ribbon
from p3d.body import Body
from p3d import looks
from p3d.camera import Rig, fly
from p3d.crowd import Crowd
from p3d.master_fx import RingWave
from p3d.words import Word
from tools.concert_kit.models import Path, Willow, Flowers, Lantern, segments, smooth


def _body(shape, at, seed, points=42000, **kw):
    body = Body(shape, at=at, height=1.67 if shape == "woman" else 1.78,
        garment="dress" if shape == "woman" else "coat",
        hair="bun" if shape == "woman" else "short", seed=seed, points=points,
        detail=dict(hand=2.8, head=1.7, foot=1.8),
        color="#ebc18a", color2="#ffe3b7", bright=1.12,
        look=[dict(name="glitter", bright=.92, seams=.52, glints=.00018),
              dict(name="rim", bright=.24, power=3.8)],
        wind=(.06, 0, .018), gust=.025, **kw)
    for layer in body.layers:
        part = body.cloud["part"][layer["idx"]]
        layer["alpha"] = np.asarray(layer["alpha"]) * np.where(
            part == looks.HAND, .46, np.where(part == looks.FOOT, .67, 1))
    return body


class HeldLantern:
    """A modeled lantern hangs from the solved palm during walking and raising."""
    def __init__(self, body, seed):
        self.body, self.seed = body, seed
        self.lamp = Lantern(size=.24, variant="hanging", lit=-2, seed=seed)

    def sample(self, t):
        palm = self.body.where(t, "palm.R")
        self.lamp.at = palm + np.array([.018 * np.sin(t * 2.1 + self.seed), -.43, 0])
        out = self.lamp.sample(t)
        out.append(segments([np.array([palm, self.lamp.at + (0, .155, 0)])],
                            "#f4c575", .004, .62))
        return out


class Arcades:
    """Successive vaulted thresholds retain visible thickness and perspective."""
    static = True
    def __init__(self, count=8, start=-4, spacing=4.7, width=5.2, height=6.4):
        self.curves, self.dots = [], []
        rng = np.random.default_rng(3201)
        for i in range(count):
            z = start - i * spacing
            for depth in (0, -.25):
                a = np.linspace(0, np.pi, 80)
                for k in (1, 1.018):
                    x = width * k * np.cos(a)
                    y = 2.5 + (height - 2.5) * np.sin(a)
                    self.curves.append(np.stack([x, y, np.full(len(a), z + depth)], 1))
                for side in (-1, 1):
                    for off in (-.07, .07):
                        self.curves.append(np.array([[side * width + off, .02, z + depth],
                                                     [side * width + off, 2.5, z + depth]]))
            for side in (-1, 1):
                yy = rng.uniform(0, 2.5, 330)
                aa = rng.uniform(0, 2 * np.pi, len(yy))
                self.dots.append(np.stack([side * width + .08 * np.cos(aa), yy,
                                            z + .08 * np.sin(aa)], 1))
        self.dots = np.concatenate(self.dots)

    def sample(self, t):
        return [segments(self.curves, "#a5b4d4", .012, .34, emit=1.05),
                dict(pos=self.dots, size=.011, color=lin("#d8c296"), alpha=.27, kind="spark")]


class LanternSky:
    """Lanterns leave the moving procession in staggered airborne paths."""
    def __init__(self, start=5, n=70):
        rng = np.random.default_rng(3211)
        self.birth = rng.uniform(start, 16.5, n)
        self.x = rng.uniform(-4.6, 4.6, n)
        self.z = rng.uniform(-29, -7, n)
        self.rate = rng.uniform(.4, .75, n)
        self.phase = rng.uniform(0, 6.28, n)
        self.size = rng.uniform(.07, .16, n)

    def sample(self, t):
        age = t - self.birth
        keep = age >= 0
        if not np.any(keep):
            return None
        a = age[keep]
        p = np.stack([self.x[keep] + .22 * np.sin(.5 * a + self.phase[keep]),
                      1.9 + a * self.rate[keep], self.z[keep] - .12 * a], 1)
        return [dict(pos=p, size=self.size[keep], color=lin("#ffc478"),
                     alpha=.64 * smooth(0, 1.2, a), emit=1.35, kind="spark", twinkle=.1),
                dict(pos=p, size=self.size[keep] * 2.7, color=lin("#eeb588"),
                     alpha=.055 * smooth(0, 1.2, a), kind="soft")]


class RibbonSky:
    """Nine separated ribbons sweep into a crown above the gathering."""
    def sample(self, t):
        colors = ("#EA5A5E", "#F2B25E", "#F6CE46", "#5ABA5A", "#62B2FA",
                  "#97A5FA", "#9E6AF6", "#EE62A6", "#8C9FEA")
        out = []
        for i, color in enumerate(colors):
            amount = float(smooth(8 + .22 * i, 15 + .18 * i, t))
            if amount < .002:
                continue
            u = np.linspace(0, amount, 190)
            a = (-1.1 + i * .275) + u * 1.18
            r = 4.1 + i * .12
            p = np.stack([r * np.sin(a), 1.3 + 3.5 * np.sin(np.pi * u * .64),
                          -6.0 - r * np.cos(a)], 1)
            p[:, 1] += .055 * np.sin(u * 19 - t * 1.7 + i)
            out.append(ribbon(p, width=.023, color=lin(color), alpha=.42, emit=1.35, twinkle=.04))
            out.append(dict(pos=p[::3], size=.018, color=lin(color), alpha=.48,
                            kind="spark", emit=1.1, twinkle=.2))
        return out


class City:
    """A layered skyline of geometric towers and domes at true world depth."""
    static = True
    def __init__(self):
        curves = []
        rng = np.random.default_rng(3280)
        for row in range(3):
            for i in range(9):
                x = (i - 4) * 3.8 + .8 * row
                z = -24 - row * 8
                h = rng.uniform(3, 6.5) + row * 1.0
                w = rng.uniform(.55, 1.05)
                for depth in (0, -1.3):
                    curves.append(np.array([[x-w, .05, z+depth], [x-w, h, z+depth],
                                            [x+w, h, z+depth], [x+w, .05, z+depth]]))
                    a = np.linspace(0, np.pi, 36)
                    curves.append(np.stack([x + w * np.cos(a), h + w * np.sin(a),
                                            np.full(len(a), z+depth)], 1))
                for y in np.arange(.9, h-.4, .9):
                    for xx in (-.32, .32):
                        curves.append(np.array([[x+xx-.1, y, z+.01], [x+xx-.1, y+.38, z+.01],
                                                [x+xx+.1, y+.38, z+.01], [x+xx+.1, y, z+.01]]))
        self.curves = curves

    def sample(self, t):
        return segments(self.curves, "#b7a8d9", .014, .28, emit=1.05)


def _procession():
    camera = Rig([fly([
        (0, (-3.6, 1.95, 1.3), (-.55, 1.1, -2.6)),
        (5, (-2.8, 2.1, 3.2), (-.25, 1.15, -.3)),
        (11, (.8, 2.6, 7.0), (0, 1.3, 2.0)),
        (16, (3.8, 3.8, 11.6), (0, 1.8, 2.7)),
        (20, (2.3, 5.6, 15.7), (0, 2.1, -.4)),
    ], fov=43, aperture=.003, blend=0, ease="smooth")], shutter=.34, blend=0, near=.1)

    def setup(scene):
        scene.add("lantern_avenue", Path(at=(0, 0, -8), width=4.0, length=48))
        scene.add("deep_vaults", Arcades())
        specs = [("woman", (-.55, 0, -2.4), 3321, 65000),
                 ("man", (.9, 0, -3.2), 3322, 54000),
                 ("woman", (-1.1, 0, -5.8), 3323, 31000),
                 ("man", (.7, 0, -6.5), 3324, 31000),
                 ("woman", (-.6, 0, -9.1), 3325, 26000)]
        for i, (shape, at, seed, pts) in enumerate(specs):
            body = _body(shape, at, seed, points=pts,
                motion=[(0, "walk", dict(speed=.46, phase=i*.17)),
                        (16.3 + i*.18, "stand", dict(blend=1.2))],
                gesture=[(0, 23, "raise_hand", dict(side="R", palm="up", fingers="hold", ease_in=.01)),
                         (13.4 + i*.3, 20.5, "hand_on_heart", dict(side="L", bow=3, ease_in=1.0))])
            body.actor.gest[0][3]["to"] = lambda t, b=body: b.actor.travel(t)[1] + np.array([
                -.51, 1.54 + .30 * smooth(12, 16, t), .20 + .025 * np.sin(1.7*t)])
            body.actor._cache.clear()
            body.add(scene, "lantern_bearer_%d" % i, mask=dict(strength=.36, grow=0))
            scene.add("held_lantern_%d" % i, HeldLantern(body, seed))
        crowd = Crowd(places=np.array([[x, 0, z] for z in (-12, -15, -18, -21)
                                       for x in (-.8, .8)]),
            kinds=("walk",), people=dict(woman=1, man=1), facing=0, walk=.44,
            points=3500, bright=.9, seed=3370, start=-1, color="#dfbb80", color2="#f5d7a6")
        scene.add("following_procession", crowd)
        scene.add("ascending_lanterns", LanternSky(), reflect=False)
        for i, x in enumerate((-6.2, 6.2)):
            scene.add("avenue_tree_%d" % i, Willow(at=(x, 0, -9), height=5.6, spread=2.4,
                      variant="willow", bloom=3, seed=3390+i))

    return dict(camera=camera, setup=setup, motion_samples=2, bokeh_max=.022,
        world=dict(look="night", sky_top="#030617", sky_mid="#111b3f", sky_hor="#665577",
            sun_int=.06, sun_el=-7, sun_az=190, stars=.15, milky=.1, clouds=.08,
            haze=.045, mist=.025, water="#060b1f", mirror=.68, ripple=.12, dust=.012,
            bokeh=.004, lanterns=0, floats=0, hills=.06, exposure=1.07, keep_hue=.88))


def _reunion():
    camera = Rig([fly([
        (0, (-2.1, 1.65, 4.6), (-.5, 1.0, -.8)),
        (4, (-.6, 1.85, 5.2), (0, 1.05, -1.4)),
        (9, (1.6, 2.4, 7.6), (0, 1.25, -2.0)),
        (14, (3.3, 4.0, 12), (0, 1.65, -3.3)),
        (20, (.2, 5.7, 17), (0, 2.7, -5)),
    ], fov=40, aperture=.003, blend=0, ease="smooth")], shutter=.34, blend=0, near=.1)

    def setup(scene):
        scene.add("quiet_city", City())
        scene.add("gathering_causeway", Path(at=(0, 0, -6), length=35, width=7.2))
        lead = _body("woman", (-.95, 0, -.8), 3410, points=70000,
            facing=[(0, 147), (5, 147), (7, 115), (10, 0), (20, 0)],
            motion=[(0, "stand", {}), (6.3, "shuffle", dict(blend=.6)),
                    (10.0, "stand", dict(blend=.8))],
            gesture=[(.8, 6.4, "wave", dict(side="R", ease_in=1.0)),
                     (6.8, 12.2, "hand_on_heart", dict(side="R", bow=9, ease_in=1.0)),
                     (12.8, 22, "open_arms", dict(lift=.28, ease_in=1.4))])
        arrival = _body("man", (.8, 0, -4.6), 3411, points=58000, facing=-9,
            motion=[(0, "walk", dict(speed=.48)), (6.1, "stand", dict(blend=1.2))],
            gesture=[(1.4, 5.8, "wave", dict(side="R", ease_in=.8)),
                     (6.9, 12.4, "hand_on_heart", dict(side="R", bow=10, ease_in=1.1)),
                     (13.1, 22, "open_arms", dict(lift=.25, ease_in=1.3))])
        lead.add(scene, "welcoming_figure", mask=dict(strength=.25, grow=0))
        arrival.add(scene, "arriving_figure", mask=dict(strength=.25, grow=0))
        for i, (shape, at) in enumerate((
            ("woman", (-2.6, 0, -6.8)), ("man", (2.4, 0, -7.2)),
            ("man", (-4.1, 0, -10)), ("woman", (4.0, 0, -10.7)))):
            b = _body(shape, at, 3420+i, points=30000,
                motion=[(0, "walk", dict(speed=.36, phase=.13*i)),
                        (11.8 + .3*i, "stand", dict(blend=1.4))],
                gesture=[(10.6 + .4*i, 15.4 + .4*i, "hand_on_heart", dict(side="R", bow=5)),
                         (15.6 + .3*i, 22, "open_arms", dict(lift=.25, ease_in=1.1))])
            b.add(scene, "joining_figure_%d" % i, mask=dict(strength=.18, grow=0))
        places = np.array([[x, 0, z] for z in (-14, -17, -20) for x in (-5.5, -3, 0, 3, 5.5)])
        scene.add("community", Crowd(places=places, kinds=("open",), people=dict(woman=1, man=1),
            points=3200, bright=.84, act=dict(t=12, dur=3), seed=3440,
            color="#dfb575", color2="#f4d9a5", start=-1))
        scene.add("peace_reaches_the_water", RingWave((0, .02, -1.5), 8.5, speed=2.3,
            reach=28, n_ring=1200, n_field=7000, color="#edbd93", core="#f5d5a1"))
        scene.add("nine_colors_in_the_sky", RibbonSky())
        for i, x in enumerate((-6.0, 6.0)):
            scene.add("living_shore_%d" % i, Willow(at=(x, 0, -9.5), height=5.5, spread=2.4,
                variant="blossom", bloom=9.1+i*.7, seed=3460+i))
            scene.add("opening_flowers_%d" % i, Flowers(at=(x*.7, 0, -4), count=24,
                radius=1.4, bloom=9.5+i*.4, seed=3470+i))
        title = Word(lines=["The Words of Mother's Love"], label="", pos=(0, 5.25, -5.5),
            width=11.0, face="camera", camera=camera, t_in=14.0, t_read0=17.2,
            t_read1=24, t_out=26, arrive="gather", leave="fade", n=30000,
            color="#f4d6a3", bright=.84, halo=.34, sparkle=.08, sharp=1.15,
            source=(0, 2.2, -2.0))
        scene.add("closing_message", title, reflect=False, fog=False)

    return dict(camera=camera, setup=setup, motion_samples=2, bokeh_max=.022,
        world=dict(look="night", sky_top="#060719", sky_mid="#202246", sky_hor="#76627d",
            sun_int=.075, sun_el=-6, sun_az=185, stars=.17, milky=.1, clouds=.07,
            haze=.04, mist=.022, water="#070c20", mirror=.68, ripple=.10, dust=.012,
            bokeh=.004, lanterns=0, floats=0, hills=.07, exposure=1.05, keep_hue=.88))


def build(film_id):
    if film_id == 5:
        return _procession()
    if film_id == 10:
        return _reunion()
    raise ValueError("people_worlds builds films 5 and 10")
