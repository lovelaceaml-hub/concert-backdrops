"""Song 03 backdrop v2: the people who act the two expressions, on black (the approved 3D layer at the tag:
engine/p3d acting.py, body.py, gestures.py). tools/s03_full2/people.py renders this with the tag's engine and
overlay2.py lays the result over the picture as light.

Warm gold glitter people of light, whole and clothed, two women in each act (every touching moment between two
people of the same gender, PHASEB 15), refined acted motion from acting.py:
  Apology, variant "comfort": one sits with her head bowed; the other kneels beside her and lays a hand gently
      on her back, her own head bowed (PHASEB 6: "head bowed with open hands low or a hand laid gently on a
      back"). The campaign: understanding the other's feelings first and reaching out first.
  Encouragement, variant "shoulder": one kneels in prayer; the other lays a hand on her shoulder, both heads
      bowed (PHASEB 6: "kneeling in prayer or a hand on the shoulder of someone kneeling"). The song's line is
      Mother praying for the soul; the campaign: knowing someone prays for us gives strength.
Each act begins about a second before its words become readable and is held, alive, through the reading.
The world is black (no sky, hills, lake, dust or lights), so only the people's light remains.
No em dash or en dash anywhere in this file.
"""
import songs.s03_original as _base

FPS = 60
TOTAL = 328.0
_base.FPS = FPS
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * FPS))
_base.MUSIC_END = 309.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import numpy as np  # noqa: E402

from p3d import acting  # noqa: E402
from p3d.body import Body  # noqa: E402
from p3d.camera import Rig, hold  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
GOLD = dict(look="glitter", color="#f6c46e", color2="#fff0cc", points=90000, detail=dict(hand=2.5, head=1.5))
WOMAN = dict(shape="woman", garment="robe")

from people_windows import ACT_TIMES, PRE, POST, WINDOWS  # noqa: E402

# (label, variant, act start, act end, stage x, camera: distance, height, look-at height, fov)
_STAGE = [(0.0, (3.3, 0.42, 0.62, 32.0)), (70.0, (3.9, 0.45, 0.80, 32.0))]
ACTS = [a + s for a, s in zip(ACT_TIMES, _STAGE)]
VIEW = [28.0, -28.0]       # the acts turned a little toward the camera, so no leg stands clear of a gown
# kneeling on both knees, so the gown covers the legs (a raised knee showed its shin clear of the gown)
# (the Apology's comforter is already kneeling beside her friend when she appears: standing, she would reach up
# into the words while they are written)
KNEEL_A = [lambda t0: dict(motion=[(-1e9, "kneel", dict(one=False, dur=0.01, hands="free"))]),
           lambda t0: {}]
KNEEL_B = [lambda t0: {},
           lambda t0: dict(motion=[(-1e9, "kneel", dict(dur=0.01, one=False, hands="pray"))])]
_SETS = {}


def act_sets(k):
    if k not in _SETS:
        lab, var, t0, t1, x, _cam = ACTS[k]
        _SETS[k] = acting.perform(lab, t0, t1, at=(x, 0.0), view=VIEW[k], variant=var, style=dict(GOLD),
                                  style_a=dict(WOMAN, **KNEEL_A[k](t0)), style_b=dict(WOMAN, **KNEEL_B[k](t0)), pre=PRE, post=POST, seed=3.0 + k)
    return _SETS[k]


def _setup(scene):
    for k in range(len(ACTS)):
        for i, ps in enumerate(act_sets(k)):
            name = "act%d_%d" % (k, i)
            if isinstance(ps, Body):
                ps.add(scene, name)
            else:
                scene.add(name, ps)


def _shot(k, t0, t1):
    _lab, _var, _a, _b, x, (d, h, ly, fov) = ACTS[k]
    a = np.radians(VIEW[k])
    return hold((x + d * np.sin(a), h, d * np.cos(a)), (x, ly, 0.0), t0, t1, drift=(0.0, 0.0, 0.0), fov=fov, aperture=0.004)


_split = 0.5 * (WINDOWS[0][1] + WINDOWS[1][0])
BLACK = "#000000"
P3D = dict(
    camera=Rig([_shot(0, 0.0, _split), _shot(1, _split, TOTAL)], blend=0.0),
    world=dict(look="night", sky_top=BLACK, sky_mid=BLACK, sky_hor=BLACK, sun_int=0.0, stars=0.0, milky=0.0,
               clouds=0.0, hills=0.0, haze=0.0, mist=0.0, water=BLACK, mirror=0.0, mirror_min=0.0, rays=0.0,
               dust=0.0, bokeh=0.0, lanterns=0.0, floats=0.0, exposure=1.0),
    setup=_setup,
)
