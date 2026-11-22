"""Dedicated native scene for the independent procedural model prototypes."""
import os
import numpy as np
import songs.s03_original as _base

_base.FPS = int(os.environ.get("OUT_FPS", "60"))
_base.TOTAL = 6.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 6.0
_base.FADE = _base.Track([(0, 1), (6, 1)])
_base.EXPOSURE = _base.Track([(0, 1), (6, 1)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9+1)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9+1
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d.camera import Rig, dolly
from tools.concert_addons.models import Dove, Rose, Wheat
from tools.concert_addons.geometry import LineSet, ry

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
TOTAL = 6.0
MODE = os.environ.get("CONCERT_ADDONS_SCENE", "flight")
_DOVE = None


class Song:
    """Neutral envelope for a silent model proof, not an instrument analysis."""
    def __init__(self):
        self.env = np.full(NFRAMES, .32)
        self.env_slow = np.full(NFRAMES, .32)
        self.hi = np.full(NFRAMES, .16)
        self.pulse = np.zeros(NFRAMES)
        self.ridge = np.full(2048, .02, dtype="f4")

    def lantern(self, t):
        return .4, .3

    def rings_at(self, t):
        return []


def dove():
    global _DOVE
    if _DOVE is None:
        _DOVE = Dove()
    return _DOVE


def perch(at, yaw):
    """An original small branch beneath each actual foot-contact anchor."""
    at = np.asarray(at, float)
    v = np.linspace(0, 1, 25)
    a = at + [-.35, -.62, .06]
    b = at + [-.19, -.25, .03]
    trunk = ((1-v)**2)[:, None]*a + 2*((1-v)*v)[:, None]*b + (v*v)[:, None]*at
    cap = at + np.stack([np.linspace(-.16, .16, 20), np.zeros(20), .014*np.ones(20)], 1) @ ry(yaw).T
    offshoot = np.stack([trunk[10], at+[-.45, -.19, -.07], at+[-.55, -.04, -.09]])
    return LineSet([trunk, cap, offshoot], "#b8b58b", width=.014, alpha=.34)


def setup(scene):
    if MODE == "flight":
        scene.add("dove", dove())
        scene.add("launch_branch", perch(dove().at, dove()._state(dove().launch)["yaw"]))
        scene.add("landing_branch", perch(dove().land_at, dove()._state(dove().land)["yaw"]))
        scene.add("rose_blush", Rose(at=(-1.75, 0, -.1), height=.75, radius=.11, bloom_at=.5))
        scene.add("wheat", Wheat(at=(1.6, 0, .35), height=.70, radius=.16, count=7))
    elif MODE == "rose":
        for i, variant in enumerate(("blush", "crimson", "golden")):
            scene.add("rose_"+variant, Rose(at=(-.58+.58*i, 0, -.10*i), height=.85+.07*i,
                                           radius=.145, variant=variant, bloom_at=.5, seed=2+i))
    elif MODE == "wheat":
        scene.add("ripe_wheat", Wheat(at=(-.40, 0, 0), count=13, radius=.20, height=1.05))
        scene.add("green_wheat", Wheat(at=(.43, 0, -.2), count=11, radius=.19,
                                        height=.88, variant="green", seed=17))
    else:
        raise ValueError("Unknown prototype scene: "+MODE)


if MODE == "flight":
    camera = Rig([dolly((4.9, 4.8, 1.6), (4.9, 4.8, 1.6), 0, 6,
                       look=(.0, 1.45, -.38), fov=34, aperture=.006, ease="smooth", blend=0)],
                 blend=0, shutter=.30, handheld=0, near=.05)
elif MODE == "rose":
    camera = Rig([dolly((1.7, 1.6, 3.0), (1.7, 1.6, 3.0), 0, 6,
                       look=(0, .65, -.06), fov=33, aperture=.006, blend=0)],
                 blend=0, shutter=.30, handheld=0, near=.05)
else:
    camera = Rig([dolly((1.7, 1.7, 3.4), (1.7, 1.7, 3.4), 0, 6,
                       look=(.0, .68, -.05), fov=34, aperture=.005, blend=0)],
                 blend=0, shutter=.30, handheld=0, near=.05)

P3D = dict(camera=camera, setup=setup, motion_samples=2, bokeh_max=.025, world=dict(
    look="night", sky_top="#01030b", sky_mid="#101a2b", sky_hor="#373047",
    sun_int=.025, sun_el=-7, sun_az=170, sun_glow=.15, sun_disc=0,
    stars=.35, milky=.12, clouds=.12, haze=.06, mist=.04, mist_height=.3,
    water="#02050c", mirror=.65, mirror_min=.15, ripple=.16,
    dust=.04, bokeh=.025, lanterns=0, floats=0, hills=1, hill_height=.75,
    exposure=.88, keep_hue=.62, dust_field=dict(n=200, n_bokeh=4),
    float_field=dict(count=0, center=(0, -10), radius=(6, 60)), lights=[]))
