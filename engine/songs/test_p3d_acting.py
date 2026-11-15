"""The acting proof (engine/p3d/acting.py): the nine expressions performed one after another, each on its own
stage far from the others, in the plain glitter look on the night lake, cut hard. Not a concert video.

Each stage is STAGE seconds: the people are already there and alive at the cut, the act begins ACT seconds in,
its clear pose is reached about a second later and held to the next cut.
`python -c "import songs.test_p3d_acting as s; s.listing()"` prints the stages and their times.
"""
import songs.s03_original as _base

STAGE = 3.4
ACT = 0.4
ORDER = [
    # label, variant, camera: (distance, height, look-at height, look-at depth, fov, side offset)
    ("Greeting", "crowd", (8.0, 1.9, 1.1, -4.0, 46, 0.6)),
    ("Gratitude", "heart", (3.2, 1.35, 1.05, 0.0, 36, 0.35)),
    ("Apology", "comfort", (3.6, 1.15, 0.6, 0.0, 38, -0.3)),
    ("Inclusiveness", "embrace", (3.4, 1.35, 1.15, 0.0, 36, 0.4)),
    ("Concession", "pass", (5.0, 1.4, 0.95, 0.0, 40, -0.2)),
    ("Respect", "listen", (3.6, 1.05, 0.55, 0.0, 38, 0.2)),
    ("Encouragement", "lights", (8.2, 2.3, 0.7, -2.2, 44, 0.5)),
    ("Consideration", "help_up", (3.8, 1.25, 0.9, 0.0, 38, -0.3)),
    ("Compliment", "applause", (7.6, 2.1, 0.9, -1.8, 44, -0.4)),
]
_N = len(ORDER)
_base.TOTAL = STAGE * _N
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = _base.TOTAL - 0.2
_base.FADE = _base.Track([(0.0, 1.0), (_base.TOTAL - 0.4, 1.0), (_base.TOTAL - 0.05, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (_base.TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import acting  # noqa: E402
from p3d.camera import Rig, hold  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
GAP = 70.0                 # metres between stages along x
STYLE = dict(look="glitter", color="#f2b865", color2="#ffe6b8")


def listing():
    for k, (lab, var, _c) in enumerate(ORDER):
        s = k * STAGE
        print("%5.1f  %-14s %-10s act %.1f, held from about %.1f" % (s, lab, var, s + ACT, s + ACT + 1.2))


def _setup(scene):
    for k, (lab, var, _c) in enumerate(ORDER):
        s = k * STAGE
        acting.add(scene, lab, s + ACT, s + STAGE, name="act%d" % k, at=(k * GAP, 0.0), view=0.0, variant=var,
                   style=STYLE, pre=1.4, post=0.4, seed=1.0 + k)


def _cam(k):
    d, h, ly, lz, fov, side = ORDER[k][2]
    x = k * GAP
    s = k * STAGE
    return hold((x + side, h, lz + d), (x, ly, lz), s, s + STAGE, drift=(-0.04 * (1 if side > 0 else -1), 0.0, -0.05),
                fov=fov, aperture=0.03)


P3D = dict(
    camera=Rig([_cam(k) for k in range(_N)], blend=0.0),
    world=dict(look="night"),
    setup=_setup,
)
