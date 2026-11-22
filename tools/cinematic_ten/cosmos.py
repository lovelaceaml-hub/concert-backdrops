"""The globe-to-people and celestial instrument films in the native 3D suite."""
from __future__ import annotations

import numpy as np

from p3d.body import Body
from p3d import looks
from p3d.camera import Rig, fly, dolly
from tools.concert_kit.models import Willow, Flowers, Lantern
from tools.cinematic_ten.cosmic_models import (
    TimedSet, ThresholdGlow, Constellations, Colonnade, GatheringLight, Orrery, Observatory,
    ContinentGlobe)


def _human(shape, at, seed, side):
    b = Body(shape, at=at, height=1.68 if shape == "woman" else 1.76,
        garment="dress" if shape == "woman" else "coat", hair="bun" if shape == "woman" else "short",
        motion=[(9.0, "walk", dict(speed=.52, phase=.11 * seed % 1, blend=.2)),
                (15.5 + side * .18, "stand", dict(blend=1.2))],
        facing=[(9, 0), (15.5, 0), (17.5, -side * 16)],
        gesture=[(13.4 + .25 * side, 17.4 + .25 * side, "wave", dict(side="R", ease=.7)),
                 (17, 22, "hand_on_heart", dict(side="R", bow=5, ease_in=1.2))],
        show=(8.8, 22), fade=.45, points=50000 if abs(side) <= 1 else 28000,
        detail=dict(hand=2.4, head=1.4), bright=1.12,
        color="#e7bb7d", color2="#ffe4bb", build=.96, seed=seed,
        look=[dict(name="glitter", bright=.95, seams=.55, glints=.00018),
              dict(name="rim", bright=.24, power=3.4)], wind=(.055, 0, .018), gust=.04)
    for layer in b.layers:
        part = b.cloud["part"][layer["idx"]]
        layer["alpha"] = np.asarray(layer["alpha"]) * np.where(
            part == looks.HAND, .5, np.where(part == looks.FOOT, .67, 1))
    return b


def _continent():
    cam = Rig([
        fly([(0, (12, 12, 25), (0, 7, -8)),
             (3.3, (6.5, 9.5, 17), (0, 7, -8)),
             (6.2, (1.2, 8.3, 9.5), (0, 6.6, -8)),
             (9, (-.6, 6.5, -1.0), (0, 6, -8))],
            fov=43, aperture=.002, roll=(0, -3), blend=0, ease="in"),
        fly([(9, (-.8, 1.7, 1.8), (-.3, 1.05, -4)),
             (12, (.7, 1.8, 2.8), (0, 1.0, -2.7)),
             (16, (1.7, 2.2, 4.2), (0, 1.1, -1.6)),
             (20, (1.3, 3.2, 7.0), (0, 1.4, -1.8))],
            fov=39, aperture=.004, blend=0, ease="smooth"),
    ], blend=0, shutter=.34, handheld=0, near=.1)

    def setup(scene):
        globe = ContinentGlobe(pos=(0, 7, -8), radius=5.3, face="fixed", camera=cam,
            n=132000, front=10, spin=2.7, tilt=8,
            t_in=-1, t_out=8.93, fade=.15, bright=.83,
            look=dict(ocean_c="#112747", ocean_e="#050e22", land="#ffc989",
                      land2="#fff1cd", land_base="#111820", land_k=.65,
                      glow_k=.14, cloud_k=.045, rim_k=.32),
            hearts=dict(t0=1.1, t1=7.2, n=20, start=(1.3, 24),
                        size=.035, colors=["#ffe4a1", "#a8e0ed", "#efb1d0"], pulse=.7),
            arcs=dict(height=.11, width=.004, dur=1.1, glow=.7),
            clouds=dict(drift=2.6))
        scene.add("earth", globe, fog=False, reflect=False)
        scene.add("orbital_depth", TimedSet(Constellations(n=1800), appear=-1, vanish=9, fade=.15),
                  fog=False, reflect=False)
        scene.add("light_match", ThresholdGlow(), reflect=False, fog=False)
        scene.add("arrival_arcades", TimedSet(Colonnade(), appear=8.9, fade=.12))
        specs = [("man", (-1.35, 0, -4.8), 211, -1),
                 ("man", (.9, 0, -4.5), 229, 1),
                 ("woman", (-2.8, 0, -7.0), 241, -2),
                 ("woman", (2.4, 0, -6.8), 257, 2),
                 ("man", (-.7, 0, -8.8), 271, -3),
                 ("man", (1.25, 0, -9.2), 283, 3)]
        for i, spec in enumerate(specs):
            _human(*spec).add(scene, "arrival_person_" + str(i), mask=dict(strength=.27, grow=0))
        scene.add("shared_canopy", GatheringLight())
        for i, (x, z) in enumerate(((-7.4, -6), (7.8, -8), (-9.2, -17), (9.8, -20))):
            tree = Willow(at=(x, 0, z), height=5.5 + i * .6, spread=3.4,
                          variant="blossom", bloom=13.2, seed=311 + i)
            scene.add("garden_tree_" + str(i), TimedSet(tree, appear=8.8, fade=.2))
        for i, (x, z) in enumerate(((-4.2, 1), (4.2, .1), (-4.6, -4), (4.8, -6))):
            scene.add("garden_flowers_" + str(i), TimedSet(
                Flowers(at=(x, 0, z), count=12, radius=.8, height=.38,
                        bloom=12, seed=331 + i), appear=8.8, fade=.2))
            scene.add("path_lamp_" + str(i), TimedSet(
                Lantern(at=(x, .35, z - .4), size=.23, lit=9, seed=351 + i),
                appear=8.8, fade=.2))

    return dict(camera=cam, setup=setup, cuts=(9.0,), motion_samples=2,
        bokeh_max=.025, world=dict(look="night", sky_top="#020619",
            sky_mid=lambda t: "#030918" if t < 9 else "#141e43",
            sky_hor=lambda t: "#030817" if t < 9 else "#5a3557",
            sun_int=lambda t: 0 if t < 9 else .09, sun_el=-8, sun_az=170, sun_glow=.25,
            sun_disc=0, stars=.24, milky=.12, clouds=lambda t: 0 if t < 9 else .05,
            haze=lambda t: 0 if t < 9 else .035, mist=lambda t: 0 if t < 9 else .025,
            mist_height=.25, water="#030817", mirror=lambda t: 0 if t < 9 else .81,
            mirror_min=lambda t: 0 if t < 9 else .16,
            ripple=.12, dust=.008, bokeh=.003, lanterns=0, floats=.012,
            hills=lambda t: 0 if t < 9 else 1, hill_height=.50, exposure=.92, keep_hue=.7,
            dust_field=dict(n=350, n_bokeh=6), float_field=dict(count=40, center=(0, -20), radius=(10, 60)),
            lights=[]))


def _orrery():
    cam = Rig([fly([
        (0, (7.8, 9.0, -.7), (0, 7.1, -8)),
        (4.5, (12.1, 11.2, 5), (0, 7.2, -8)),
        (10.0, (3.2, 13.1, 12.8), (0, 6.7, -8)),
        (14.5, (-10, 11.0, 13.5), (0, 6.5, -8)),
        (20, (-10.0, 11.0, 16.0), (0, 6.2, -8)),
    ], fov=45, aperture=.006, roll=(2, -1.5), ease="smooth", blend=0)],
        blend=0, shutter=.38, handheld=0, near=.1)

    def setup(scene):
        scene.add("celestial_instrument", Orrery(), fog=False)
        scene.add("observatory", Observatory())
        scene.add("near_constellations", Constellations(n=2400, radius=22), reflect=False, fog=False)

    return dict(camera=cam, setup=setup, cuts=(), motion_samples=2, bokeh_max=.025,
        world=dict(look="night", sky_top="#030713", sky_mid="#101936",
            sky_hor="#382f59", sun_int=.04, sun_el=-10, sun_az=155,
            sun_glow=.18, sun_disc=0, stars=.40, milky=.25,
            clouds=.07, haze=.025, mist=.025, mist_height=.25,
            water="#070b1d", mirror=.88, mirror_min=.25, ripple=.08,
            dust=.006, bokeh=.002, lanterns=0, floats=.004, hills=1,
            hill_height=.45, exposure=.93, keep_hue=.68,
            dust_field=dict(n=350, n_bokeh=4),
            float_field=dict(count=30, center=(0, -18), radius=(18, 70)), lights=[]))


def build(film_id):
    if int(film_id) == 3:
        return _continent()
    if int(film_id) == 9:
        return _orrery()
    raise ValueError("Cosmic scenes are films 3 and 9")
