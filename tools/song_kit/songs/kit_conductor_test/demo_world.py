"""Song kit test song: its world (the dusk sea, cloud banks, pillars and comets) and the shots of its blocks.
No em dash or en dash anywhere in this file.
"""
from songs.kit_film import *  # noqa: F401,F403
import songs.kit_film as H

OWNER = "world"
C = H._v(0.0, 0.0, -30.0)          # where the acts happen, on the mirror sea


def _shot(b):
    t0, t1, note = b
    if t0 < 1.0:          # the opening: low over the water, drifting toward the place of the acts
        keys = [(t0, H._v(0.0, 2.2, 32.0), H._v(0.0, 6.0, -260.0)), (t1, H._v(0.0, 2.0, 6.0), H._v(0.0, 3.0, -260.0))]
        return dict(name="opening", kind="local", t0=t0, t1=t1, fov=52.0, aperture=0.0, keys=keys, pace="linear")
    if t0 < 30.0:         # the glide: banking slowly round the place of the acts
        keys = [(t0, H._v(-14.0, 4.0, -6.0), C + H._v(0.0, 2.0, 0.0)), (t1, H._v(-4.0, 3.0, 2.0), C + H._v(0.0, 1.5, 0.0))]
        return dict(name="glide", kind="local", t0=t0, t1=t1, fov=46.0, aperture=0.0, keys=keys, roll=(4.0, 0.0))
    keys = [(t0, H._v(0.0, 4.0, 4.0), H._v(0.0, 8.0, -300.0)), (t1, H._v(0.0, 6.0, 20.0), H._v(0.0, 10.0, -300.0))]
    return dict(name="wide", kind="local", t0=t0, t1=t1, fov=50.0, aperture=0.0, keys=keys, pace="linear")


SHOTS = [_shot(b) for b in H.blocks_of(OWNER)]
SHAFTS = []


def add(scene):
    for k, (x, z) in enumerate(((-160.0, -380.0), (160.0, -380.0))):
        scene.add(f"cloud {k}", H.CloudBank(H._v(x, 20.0, z), size=(220.0, 70.0, 90.0), puffs=30, seed=10 + k,
                                            gain=lambda t: 0.6 * H.sky_gain(t)))
    scene.add("pillars", H.Pillars([(-60.0, -300.0), (60.0, -300.0)], top=260.0,
                                   gain=lambda t: 0.5 * H._sc(18.0, 21.0, t) * H.light_budget(t)))
    for k in range(3):
        def head(t, k=k):
            a = 0.25 * t + 2.1 * k
            return H._v(120.0 * H.np.sin(a), 70.0 + 12.0 * k, -320.0 + 60.0 * H.np.cos(a))
        scene.add(f"comet {k}", H.Comet(head, H.COL9[(k * 3 + 1) % 9], 8.0, 36.0, trail=2.0, width=0.9, light=True,
                                        seed=k))
