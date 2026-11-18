"""Engine demo (32 seconds): the lake ripples and campaign symbols drawn in light (engine/UPGRADE-HOWTO.md, L).

Not a concert video. The original song 03 look with no expressions: the Mother's Love and Peace Day emblem draws
on over the lake, its reflection ripples, then it flies to a light on the arch; a heart draws and dissolves into
sparks; falling stars and petals touch the water; a bridge of light spans the lake and a gate of light is drawn
line by line on it and opens.
"""
import songs.s03_original as _base

_base.TOTAL = 32.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
from songs.s03_original import *  # noqa: E402,F401,F403
from songs.s03_original import PHRASES as _P, TITLE as _TI  # noqa: E402
from track import Track  # noqa: E402

TOTAL = 32.0
NFRAMES = int(round(TOTAL * FPS))  # noqa: F405
FADE = Track([(0, 0.0), (1.0, 1.0), (30.0, 1.0), (31.8, 0.0)])
WAVES = [(16.6, STAR_POS[4][0], STAR_POS[4][1], 0.6)]  # noqa: F405
# no words in this demo; light 5 (index 4) is lit when the emblem arrives in it
PHRASES = [dict(p, form=1e9, hold=1e9, star=1e9) for p in _P]
PHRASES[4] = dict(PHRASES[4], star=16.6)
TITLE = dict(_TI, form=1e9, hold=1e9, star=1e9)
PETALS = Track([(0, 0.0), (8.0, 0.0), (10.0, 0.30), (28.0, 0.30), (30.0, 0.0), (TOTAL, 0.0)])
# s03_original's params() reads these from its own module, so hand it the demo's versions
_P[:] = PHRASES
_base.WAVES = WAVES
_base.FADE = FADE
_base.PETALS = PETALS

RIPPLES = [(10.8, 0.50, 1.0), (11.6, 0.42, 0.7), (12.3, 0.58, 0.8), (13.2, 0.50, 0.6, 0.15),
           (26.4, 0.50, 1.0, 0.24), (27.2, 0.40, 0.6), (27.8, 0.61, 0.6)]
RIPPLES_AUTO = 1.0
FALLING_STARS = [(9.2, 0.24), (15.0, 0.80, 0.18), (21.5, 0.30, 0.12)]

SYMBOLS = [
    dict(kind="emblem", t0=4.5, t1=10.5, out=14.0, x=0.50, y=0.53, size=0.36, leave="to_star", star=4),
    dict(kind="heart", t0=6.0, t1=10.0, out=13.5, x=0.17, y=0.62, size=0.15, leave="sparks"),
    dict(kind="bridge", t0=13.0, t1=18.0, out=28.5, x=0.50, y=0.40, size=0.20, stretch=1.6, leave="sparks"),
    dict(kind="gate", t0=18.0, t1=23.0, out=29.0, x=0.50, y=0.59, size=0.30, open=23.8, open_dur=2.6,
         leave="sparks"),
]
