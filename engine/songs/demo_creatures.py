"""Creatures of light demo (36 seconds, to the first minute of the song 03 New Song recording).

Not a concert video. It shows the creature layers (engine/UPGRADE-HOWTO.md, section I1) in the original look:
a flock of doves rises across a dawn sky, wheels, and turns toward the first light of the arch when it is lit;
butterflies meander and land on the shore; fireflies blink low over the water at dusk. The Greeting and
Gratitude expressions form as usual, so the text protection and the calm lower third can be checked too.
"""
import songs.s03_original as _base

_base.TOTAL = 36.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
from songs.s03_original import *  # noqa: E402,F401,F403
from songs.s03_original import PAL, STAR_POS, TOTAL, Track, lin  # noqa: E402

# the sky: dawn for the doves, then dusk for the fireflies
_pal_keys = [(0.0, "dawn"), (12.0, "dawnpk"), (20.0, "dawn"), (27.0, "dusk"), (TOTAL, "dusk")]
_base.SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
_base.SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
_base.SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
_base.GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
_base.SUN_INT = Track([(0, 0.70), (12, 1.0), (20, 0.85), (28, 0.35), (TOTAL, 0.25)])
_base.SUN_Y = Track([(0, 0.30), (12, 0.36), (20, 0.34), (30, 0.27), (TOTAL, 0.26)])
_base.STARS = Track([(0, 0.15), (18, 0.12), (28, 0.6), (TOTAL, 0.85)])
_base.MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
_base.RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
_base.AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
_base.MOTES = Track([(0, 0.06), (TOTAL, 0.10)])
_base.RAYS = Track([(0, 0.2), (12, 0.45), (22, 0.2), (28, 0.0), (TOTAL, 0.0)])
_base.FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 2.5, 1.0), (TOTAL - 0.3, 0.0)])
BOTTOM_CALM = 1.0

CREDIT = _base.CREDIT = dict(_base.CREDIT, song="Creatures of Light Demo")

# I1. creatures of light
DOVES = Track([(0, 0.0), (1.5, 0.0), (4.0, 1.0), (31.0, 1.0), (34.5, 0.0)])
DOVES_COUNT = 16
DOVES_FROM = (-0.04, 0.36)                 # they rise in from the lower left
DOVES_PATH = [(0.0, (0.40, 0.60)), (7.0, (0.78, 0.74)), (12.0, (0.66, 0.84)), (16.0, STAR_POS[0])]
DOVES_ORBIT = 0.08                          # then they wheel round the first light, lit at 15.1 s
DOVES_SIZE = 0.036
DOVES_SPEED = 1.0
DOVES_COLOR = "#fff1da"

BUTTERFLIES = Track([(0, 0.0), (8.0, 0.0), (12.0, 1.0), (32.0, 1.0), (35.0, 0.0)])
BUTTERFLIES_COUNT = 4
BUTTERFLIES_COLOR = ("#ffd2ec", "#c4e4ff")

FIREFLIES = Track([(0, 0.0), (21.0, 0.0), (27.0, 1.0), (TOTAL, 1.0)])
