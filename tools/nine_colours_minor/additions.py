"""Targeted Film 10 additions and the owner-requested Claude reference revisions."""
import numpy as np
from p3d import brand as B
from p3d.camera import Rig
import expressions
import respect
import finale as ending


def ease(a, b, t):
    x = np.clip((t-a)/(b-a), 0, 1)
    return x*x*(3-2*x)


class OpeningRig(Rig):
    """Lower the opening light below the card; rejoin the original camera."""

    def __init__(self, original):
        self.__dict__.update(original.__dict__)

    def state(self, t, aspect=16.0/9.0):
        cam = super().state(t, aspect)
        if t < 1.4:
            cam.target[1] += 1.5*(1-ease(.45, 1.4, t))
        return cam


def install(film):
    expressions.install(film)
    respect.install(film)
    original_setup = film.P3D['setup']
    camera = OpeningRig(film.CAMERA)
    finale, swirl = ending.install(film, camera)

    def setup(scene):
        original_setup(scene)
        for name in ('comets', 'hoops', 'lanterns'):
            entry = next(e for e in scene.entries() if e.name == name)
            entry.pointset = expressions.Clear(entry.pointset, film.WORDS)
        scene.remove('_arch')
        for i, word in enumerate(film.WORDS):
            x = .13 if i % 2 == 0 else .87
            symbol = B.Traced(word.name, camera=camera, ride=(x, .48, 20),
                              face='screen', frac=.065, t0=word.t_read0,
                              dur=.75, hold=max(.5, word.t_read1-word.t_read0-1.1),
                              out=.5, intensity=.32, n=600, dof=False, reflect=False)
            scene.add('addition symbol '+word.name, symbol, reflect=False)
        scene.add('addition world', finale.globe, reflect=False)
        scene.add('addition logo', ending.Fade(finale.logo,52.5,53), reflect=False)
        scene.add('addition symbol swirl', swirl, reflect=False)

    world = dict(film.P3D['world'])
    looks = dict(world['looks'])
    looks['ember'] = dict(base='night', sky_top='#03030f', sky_mid='#080d29',
                         sky_hor='#101a3d', haze=.12, haze_color='#181638',
                         mist=.12, mist_color='#151b38', stars=.3, milky=0)
    looks['globe_chapter'] = dict(base='night', sky_top='#03091c', sky_mid='#0c2051',
                                  sky_hor='#27234a', stars=1.0, milky=.8,
                                  sun_int=0, sun_glow=0, mist=.08, haze=.1)
    looks['pastel_card'] = dict(base='day', sky_top='#9bdbf6', sky_mid='#efcfeb',
                                sky_hor='#ffd9b6', sun_int=.3, sun_glow=.3,
                                hill_color='#e7afaa', mist=.14, haze=.14, stars=.2)
    look_keys = []
    for key in world['look']:
        if abs(key[0]-33.36) < .001:
            look_keys.append((key[0], 'ember', .4))
        elif abs(key[0]-49.47) < .001:
            look_keys.append((key[0], 'globe_chapter', .5))
        else:
            look_keys.append(key)
    look_keys.append((52.0, 'pastel_card', .8))
    world.update(looks=looks, look=look_keys)
    bursts = [dict(b) for b in film.P3D['bursts']]
    for burst in bursts:
        if abs(burst['t']-.25) < .001:
            burst.update(strength=.25)
        elif abs(burst['t']-33.36) < .001:
            burst.update(strength=.35)
        elif abs(burst['t']-49.47) < .001:
            burst.update(strength=.18, rise=.4, fall=.55)
    film.P3D = dict(film.P3D, setup=setup, camera=camera, world=world, bursts=bursts)
    return finale
