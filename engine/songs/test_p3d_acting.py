"""The acting proof (engine/p3d/acting.py): tender moments of the nine expressions, acted by warm gold glitter
people (and one of crystal-pale light) in a warm, luminous sunrise over the lake, each on its own stage far from
the others, cut hard. Mostly close and half shots with the hands large in the frame; one far shot. Not a concert
video.

Each stage runs its own seconds: the people are already there and alive at the cut, the act begins ACT seconds
in, its clear pose is reached about a second later and held to the next cut.
`python -c "import songs.test_p3d_acting as s; s.listing()"` prints the stages and their times.
"""
import songs.s03_original as _base

ACT = 0.35
GOLD = dict(look="glitter", color="#f6c46e", color2="#fff0cc")
CRYSTAL = dict(look=dict(name="glitter", glints=0.004), color="#e4f2ff", color2="#fff4fa")
HAND = dict(points=95000, detail=dict(hand=4.0, head=2.0))
HALF = dict(points=85000, detail=dict(hand=2.5, head=1.5))
# label, variant, seconds, framing, camera, keys
#   camera for "far", "full", "half": (distance, height, look-at height, look-at depth, fov, side offset)
#   camera for "close": (places to look at as (person, place), seconds after the act, offset from there, fov,
#                        how far above them to aim)
#   keys: style (both), style_a, style_b, crowd, shaft (a shaft of light falling on the stage)
ORDER = [
    ("Inclusiveness", "embrace", 4.4, "half", (2.15, 1.48, 1.32, 0.0, 34, 0.5),
     dict(style=HALF, style_b=CRYSTAL)),
    ("Consideration", "help_up", 4.6, "full", (3.0, 1.05, 0.85, 0.0, 38, -0.45), dict(style=HALF)),
    ("Encouragement", "pray", 4.4, "close", (((0, "palm.L"), (0, "palm.R")), 2.0, (0.62, 0.30, 1.22), 34, 0.22),
     dict(style=HAND, shaft=True)),
    ("Encouragement", "shoulder", 4.0, "half", (2.2, 1.30, 0.95, -0.05, 34, -0.35), dict(style=HALF)),
    ("Gratitude", "heart", 4.0, "half", (1.7, 1.42, 1.25, 0.0, 34, 0.3), dict(style=HALF)),
    ("Gratitude", "clasp", 4.0, "close", (((0, "palm.L"), (0, "palm.R"), (1, "palm.R")), 1.7, (0.24, 0.16, 0.85), 32,
                                          0.06), dict(style=HAND, style_b=CRYSTAL)),
    ("Compliment", "clap", 3.6, "close", (((0, "palm.L"), (0, "palm.R")), 1.5, (-0.42, 0.16, 0.78), 34, 0.12),
     dict(style=HAND)),
    ("Consideration", "lift_child", 4.6, "full", (3.2, 1.25, 0.95, 0.0, 38, 0.4), dict(style=HALF)),
    ("Encouragement", "lights", 4.4, "far", (8.0, 2.1, 0.8, -2.2, 42, 0.5),
     dict(crowd=dict(n=20, points=3600), shaft=True)),
]
_N = len(ORDER)
STARTS = [sum(o[2] for o in ORDER[:k]) for k in range(_N)]
_base.TOTAL = STARTS[-1] + ORDER[-1][2]
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

import numpy as np  # noqa: E402

from p3d import acting  # noqa: E402
from p3d.body import Body  # noqa: E402
from p3d.camera import Move, Rig, hold  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
GAP = 70.0                 # metres between stages along x
_SETS = {}


def listing():
    for k, (lab, var, dur, fr, _c, _x) in enumerate(ORDER):
        s = STARTS[k]
        print("%5.1f  %-14s %-10s %-5s %.1f s, act %.1f, held from about %.1f" % (s, lab, var, fr, dur, s + ACT,
                                                                                  s + ACT + 1.2))


def stage_sets(k):
    """The point sets of stage k (made once)."""
    if k not in _SETS:
        lab, var, dur, _fr, _cam, extra = ORDER[k]
        s = STARTS[k]
        style = dict(GOLD)
        style.update(extra.get("style", {}))
        _SETS[k] = acting.perform(lab, s + ACT, s + dur, at=(k * GAP, 0.0), view=0.0, variant=var, style=style,
                                  style_a=extra.get("style_a"), style_b=extra.get("style_b"),
                                  crowd=extra.get("crowd"), pre=1.4, post=0.4, seed=2.0 + k)
    return _SETS[k]


def stage_setup(scene, k):
    for i, ps in enumerate(stage_sets(k)):
        name = "act%d_%d" % (k, i)
        if isinstance(ps, Body):
            ps.add(scene, name)
        else:
            scene.add(name, ps)


def _setup(scene):
    for k in range(_N):
        stage_setup(scene, k)


class _Close(Move):
    """A close shot on places of a stage's people (their hands), aimed where those are at the hold. Worked out
    on first use, so importing the song builds nobody (the render's prepare step has numpy only)."""

    def __init__(self, k, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.k = k
        self.at = None

    def pose(self, t):
        if self.at is None:
            places, dt, off, _fov = ORDER[self.k][4][:4]
            cam = ORDER[self.k][4]
            sets = stage_sets(self.k)
            tg = np.mean([sets[i].where(STARTS[self.k] + ACT + dt, nm) for i, nm in places], axis=0)
            tg[1] += cam[4] if len(cam) > 4 else 0.0
            self.at = (tg + np.asarray(off, np.float64), tg)
        pos, tg = self.at
        drift = np.array([-0.008, 0.004, -0.012]) * (t - 0.5 * (self.t0 + self.t1))
        return pos + drift, tg


def camera_move(k):
    _lab, _var, dur, fr, cam, _x = ORDER[k]
    x = k * GAP
    s = STARTS[k]
    if fr == "close":
        return _Close(k, s, s + dur, fov=cam[3], aperture=0.008)
    d, h, ly, lz, fov, side = cam
    ap = 0.012 if fr == "far" else 0.018
    return hold((x + side, h, lz + d), (x, ly, lz), s, s + dur, drift=(-0.035 * (1 if side > 0 else -1), 0.0, -0.05),
                fov=fov, aperture=ap)


def _stage_at(t):
    k = int(np.searchsorted(STARTS, t, side="right")) - 1
    return min(max(k, 0), _N - 1)


def _shaft_base(t):
    k = _stage_at(t)
    return (k * GAP + 0.1, -0.4 if ORDER[k][1] == "pray" else -2.2)


def _shaft_on(t):
    k = _stage_at(t)
    if not ORDER[k][5].get("shaft"):
        return 0.0
    u = (t - STARTS[k]) / 1.2
    return 0.9 * min(max(u, 0.0), 1.0) + 0.25


P3D = dict(
    camera=Rig([camera_move(k) for k in range(_N)], blend=0.0),
    world=dict(look="sunrise", clouds=0.6, rays=0.8, dust=0.9, dust_color="#ffe0a0", dust_color2="#ffc8a8",
               lanterns=0.35, floats=0.45, stars=0.0, exposure=1.0,
               shafts=[dict(base=_shaft_base, radius=0.8, top=26.0, spread=0.18, color="#ffd89a",
                            strength=_shaft_on)]),
    setup=_setup,
)
