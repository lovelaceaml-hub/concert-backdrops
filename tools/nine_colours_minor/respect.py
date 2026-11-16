"""The two golden listening figures from Claude's Final v1 reference."""
import numpy as np
import reference  # noqa: F401
from nine_reference_p3d import master_acting  # noqa: F401
from nine_reference_p3d.body import Body


def install(film):
    original = film._bodies

    def bodies():
        all_bodies = original()
        if getattr(bodies, 'ready', False):
            return all_bodies
        common = dict(motion='stand', garment='dress', points=80000,
                      show=(33.16,40.41), fade=.4, bright=1.45)
        all_bodies['speaker'] = Body('woman', at=(film.F6[0]-.43,film.F6[2]),
            facing=90, hair='bun', seed=9.5, color='#ffc664', color2='#fff0c8',
            look=dict(name='glitter',seams=.6),
            gesture=[(33.36,40,'offer',dict(side='L'))], **common)
        all_bodies['listener'] = Body('woman', at=(film.F6[0]+.43,film.F6[2]),
            facing=270, hair='bob', seed=10, color='#f2a640', color2='#ffdc96',
            look='glitter', gesture=[(34.36,40,'listen',dict(side='L'))], **common)
        bodies.ready = True
        return all_bodies

    film._bodies = bodies

    def shot(t):
        u = (t-33.36)/(40.21-33.36)
        a = np.radians(-24+46*u)
        r = 3.4-.35*u
        return film.F6+np.array([np.sin(a)*r,1.6,np.cos(a)*r]), film.F6+np.array([0,1.35,0])

    film.CAMERA.moves[4] = film.Path(shot,33.36,40.21,blend=0,fov=40,
                                    aperture=.015,focus=3.3)
    return bodies
