"""Continuous nature films using the established native concert renderer."""

import numpy as np

from p3d.camera import Rig, Move, fly
from tools.concert_addons.geometry import smooth
from tools.concert_addons.models import Rose
from tools.concert_kit.models import Willow, Lantern, Path, Flowers
from .nature_models import (
    BloomField, ButterflyFlight, PollenRiver, AirborneDove, WingWake,
    HaloCloud, Jellyfish, FishSchool, CoralGarden, OceanShafts,
)


def _world(**changes):
    settings = dict(
        look="night", sky_top="#020813", sky_mid="#101b35", sky_hor="#595371",
        sun_int=.08, sun_el=-6, sun_az=175, sun_glow=.35, sun_disc=0,
        stars=.35, milky=.17, clouds=.15, haze=.08, mist=.04, mist_height=.45,
        water="#030917", mirror=.8, mirror_min=.25, ripple=.13,
        dust=.025, bokeh=.015, lanterns=0, floats=.015, hills=1, hill_height=.8,
        exposure=.94, keep_hue=.65, dust_field=dict(n=650, n_bokeh=12),
        float_field=dict(count=25, center=(0, -15), radius=(12, 70)), lights=[],
    )
    settings.update(changes)
    return settings


def _garden(scene):
    scene.add("garden_blossoming", BloomField())
    scene.add("garden_butterflies", ButterflyFlight())
    scene.add("garden_pollen", PollenRiver())
    for j, (x, z) in enumerate([(-1, .2), (1.15, -2.1), (-1.4, -5),
                                (1.6, -8), (-1.5, -12), (1.3, -17)]):
        scene.add("garden_rose_%02d" % j, Rose(
            at=(x, 0, z), height=.95 + .1 * (j % 2), radius=.23,
            variant=("blush", "golden", "crimson")[j % 3],
            bloom_at=.3 - j * .1 + max(0, -z) * .24,
            seed=60+j, wind_strength=.7,
        ))
    for j, z in enumerate([2, -4, -10, -17, -25, -33]):
        for side in [-1, 1]:
            scene.add("garden_tree_%02d_%d" % (j, side), Willow(
                at=(side * (4.5 + .25*j), 0, z), height=5.1 + .35*(j % 3),
                spread=2.7, variant="blossom" if j % 2 else "willow",
                seed=91+j*2+side, bloom=1+max(0, -z)*.28,
            ))
    scene.add("garden_path", Path(at=(0, 0, -14), length=36, width=2.4, variant="shore"))
    for j, z in enumerate([0, -5, -10, -15, -20, -25]):
        for side in [-1, 1]:
            scene.add("garden_lantern_%02d_%d" % (j, side), Lantern(
                at=(side*1.65, .32, z), size=.2, variant="cup",
                seed=10+j*2+side, lit=j*.8,
            ))


class BirdCamera(Move):
    def __init__(self):
        super().__init__(0, 20, fov=39, aperture=.007, blend=0, ease="smooth")

    def pose(self, t):
        p = AirborneDove.lead_path(t)
        opening = smooth(0, 4, t)
        flock = smooth(3, 8, t)
        wide = smooth(12.5, 19.5, t)
        offset = np.array([5.4-.7*opening+2.4*wide,
                           1.6-.4*opening+2.0*wide,
                           1.8+5.5*flock+3.5*wide])
        return p+offset, p+np.array([0, .55, 1.0*flock])


def _birds(scene):
    hero = AirborneDove(scale=3.3, index=0)
    scene.add("dawn_hero_dove", hero)
    scene.add("dawn_wing_wake", WingWake(hero))
    for j in range(1, 8):
        scene.add("dawn_flock_%02d" % j, AirborneDove(scale=1.45+.09*(j % 3), index=j))
    scene.add("dawn_high_cloud", HaloCloud())
    for j, z in enumerate([1, -9, -20, -32, -45]):
        for side in [-1, 1]:
            scene.add("dawn_tree_%02d_%d" % (j, side), Willow(
                at=(side*(8+.6*j), 0, z), height=3.4+.45*j,
                spread=2.5, variant="willow", seed=130+j*2+side, bloom=-10,
            ))
    scene.add("dawn_launch_flowers", Flowers(
        at=(-1, 0, 2), count=22, radius=2.3, height=.36, bloom=-5,
    ))


def _ocean(scene):
    specimens = [
        ((-1.45, 4.8, 0), 1.5, "#d19cff"),
        ((3, 5.7, -5.8), 1.25, "#7ceaf1"),
        ((-4.6, 6.2, -11), 1.7, "#ec9cc9"),
        ((1, 5.8, -17), 1.5, "#b7c9ff"),
        ((5.4, 8.5, -25), 2.1, "#91e9ef"),
        ((-3, 8, -29), 1.4, "#e2b5e7"),
    ]
    for j, (at, scale, color) in enumerate(specimens):
        scene.add("ocean_jelly_%02d" % j, Jellyfish(
            at=at, scale=scale, color=color, seed=j*1.7,
        ), reflect=False)
    scene.add("ocean_school", FishSchool(), reflect=False)
    scene.add("ocean_coral", CoralGarden(), reflect=False)
    scene.add("ocean_currents", OceanShafts(), reflect=False)


def build(film_id):
    if film_id == 6:
        shot = fly([
            (0, (1.9, 1.45, 4.2), (-.6, 1, -.1)),
            (4, (1, 1.8, .8), (0, 1.5, -4)),
            (9, (-.6, 2.1, -5.3), (0, 1.8, -11)),
            (14, (1.9, 3.7, -11), (0, 2, -20)),
            (18, (3.5, 5.8, -14), (0, 1.8, -23)),
            (20, (4, 6.5, -14.6), (0, 1.9, -24)),
        ], fov=43, aperture=.009, ease="smooth", blend=0)
        return dict(
            camera=Rig([shot], shutter=.34, near=.08), setup=_garden,
            world=_world(sky_top="#061220", sky_mid="#252848", sky_hor="#826877",
                         sun_int=.16, sun_color="#e4c6a2", sun_el=-4,
                         water="#071620", stars=.20, milky=.10, exposure=.95),
            motion_samples=2, bokeh_max=.025,
        )
    if film_id == 7:
        return dict(
            camera=Rig([BirdCamera()], shutter=.32, near=.08), setup=_birds,
            world=_world(sky_top="#10213b", sky_mid="#4a4268", sky_hor="#c58d78",
                         sun_color="#ffd3a1", sun_int=.4, sun_az=178, sun_el=2.8,
                         sun_glow=.65, sun_disc=1.5, clouds=.25, stars=.1, milky=.04,
                         water="#102034", haze=.08, mist=.04, ripple=.14, exposure=.91),
            motion_samples=2, bokeh_max=.025,
        )
    if film_id == 8:
        shot = fly([
            (0, (1.6, 4.4, 6), (-1, 4.7, -1)),
            (5, (-.2, 4.1, 1.2), (1.5, 4.7, -7)),
            (10, (1.5, 4.2, -5.5), (-1, 4.8, -14)),
            (15, (-.4, 4.6, -11.5), (1, 5.6, -21)),
            (20, (1.6, 6.4, -13), (0, 4.8, -25)),
        ], fov=47, aperture=.008, ease="smooth", blend=0)
        return dict(
            camera=Rig([shot], shutter=.35, near=.08), setup=_ocean,
            world=_world(sky_top="#031a29", sky_mid="#031622", sky_hor="#04121c",
                         stars=0, milky=0, clouds=0, hills=0, water="#010912",
                         mirror=0, mirror_min=0, sun_int=0, sun_glow=0, sun_disc=0,
                         haze=.08, haze_color="#04121c", mist=0, dust=0, bokeh=0,
                         floats=0, exposure=1.04, ripple=0),
            motion_samples=2, bokeh_max=.025,
        )
    raise ValueError("Nature film must be 6, 7, or 8")
