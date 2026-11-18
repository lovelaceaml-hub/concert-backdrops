"""Everything at once (engine-epic, 2026-11-15): a 30 second test that switches on every new engine feature in one
song file, to prove they work together. Not a promo and not a design: a real film gives each moment one hero
image. Built on the living figures test (engine/songs/test_living.py: its sky from dusk to the bright campaign
day, its theme colours, bubbles, leaves and coloured words). See engine/UPGRADE-HOWTO.md, section S.

What it shows (seconds):
 0 to 9    dusk: a person of light walks the far shore (rig); a tree grows at the right; a falling star touches
           the lake and its ripple spreads; the Encouragement expression blooms and is held; doves and the first
           of a crowd come in
 9 to 14   Heavenly Mother from behind; the crowd gathers; the tree blossoms; clouds, and god rays as the sun
           comes up
 13 to 21  still dusk, turning to dawn: a flame comes down from the arch and passes from hand to hand; the emblem
           is drawn over the crowd and mirrored in the rippling lake, then flies to its light; the crowd lifts
           its lights; a painted pair walks in, warped alive
 22 to 30  bright campaign day: bubbles and leaves; the lights reach the arch; the end card in coral and navy
           (ribbon and rise)
All the way through: one slow camera move (the land settles, a push in, a drift right) that the people, the crowd,
the doves, the tree and the emblem follow at their own depths, and gentle music reactivity.

Audio: audio/test/s03-newsong-first-60s.mp3 (only its first 30 seconds are used).
"""
import songs.test_living as _base
from songs.test_living import *  # noqa: F401,F403
from songs.test_living import FIGURES as _FIGS, PHRASES as _PHR, STAR_POS, TOTAL, Track, theme


def params(song, t):
    # song.py installs the arch (star_state, link_state) in this module; the base file's params() reads its own
    _base.star_state, _base.link_state = star_state, link_state   # noqa: F405
    return _base.params(song, t)


# ---- the sky stays dark longer than in the base file, so the people of light read: dusk to 15.5 s, dawn at 20.5
# to 22 s, the bright campaign day from 24.5 s. The base file's params() reads these from its own module.
_keys = [(0.0, "dusk"), (15.5, "dusk"), (20.5, "dawn"), (22.0, "dawn"), (24.5, "day"), (TOTAL, "day")]
_base.SKY_TOP, _base.SKY_MID, _base.SKY_HOR, _base.GLOW = (
    Track([(t, _base.lin(_base.PAL[p][k])) for t, p in _keys]) for k in range(4))
_base.SUN_Y = Track([(0, 0.335), (7.0, 0.34), (11.0, 0.365), (16.0, 0.385), (24.5, 0.41), (TOTAL, 0.41)])
_base.SUN_INT = Track([(0, 0.20), (9.0, 0.24), (13.0, 0.38), (21.0, 0.45), (TOTAL, 0.45)])
_base.STARS = Track([(0, 0.0), (0.3, 0.0), (2.0, 0.9), (15.5, 0.8), (20.5, 0.25), (23.0, 0.08), (TOTAL, 0.08)])
_base.CLOUDS = Track([(0, 0.10), (15.5, 0.12), (21.0, 0.30), (24.5, 0.40), (TOTAL, 0.40)])
_base.RAYS = Track([(0, 0.0), (TOTAL, 0.0)])   # the old flat rays stay off: GOD_RAYS below draws the shafts
SKY_THEME = Track([(0, 0.0), (21.5, 0.0), (24.5, 0.55), (TOTAL, 0.55)])
BUBBLES = Track([(0, 0.0), (21.5, 0.0), (24.5, 0.5), (TOTAL, 0.5)])
LEAVES = Track([(0, 0.0), (22.0, 0.0), (25.0, 0.3), (TOTAL, 0.3)])


def MOTE_COLORS(t):
    return ("#ffe2a8", "#ff9f8a") if t < 21.0 else (theme.WHITE_GLOW, theme.GOLD)


CREDIT = dict(_base.CREDIT, song="Everything at once (engine test)")

# ---- people (section H): the walker and Heavenly Mother as in the base; the painted pair, warped; no hands
FIGURES = [dict(_FIGS[0]), dict(_FIGS[1], x=0.78), dict(_FIGS[3], x=(0.08, 0.20))]

# ---- the arch: the emblem flies to light 5 (index 4); the crowd's lights wake the rest at the end
PHRASES = [dict(p) for p in _PHR]
PHRASES[6] = dict(PHRASES[6], form=3.0, hold=13.0, star=14.2)   # Encouragement: solid from 6.75 to 13.0
PHRASES[4] = dict(PHRASES[4], star=22.1)                        # the emblem arrives
for _i, _t in ((3, 24.8), (5, 24.8), (1, 25.1), (0, 25.4)):     # the crowd's lights reach the arch
    PHRASES[_i] = dict(PHRASES[_i], star=_t)
FRAGMENTS = []   # the base file's two fragments would sit on the expression and on the emblem

# ---- gathering and the passed light (section K)
GATHERING = dict(t0=5.0, count=30, center=(0.46, 0.343), spread=(0.22, 0.035), rows=2, hole=0.0,
                 height=(0.14, 0.10), speed=1.3, arrive_by=11.0, sides=("left", "right"),
                 colors=("#ffcf9a", "#ffd9b8", "#ffe6c4", "#ffc6a0", "#f2d0ff", "#cfe0ff"))
PASS_LIGHT = dict(t0=13.0, speed=0.60, hold=0.15, reach=0.30, path="crowd", start="center", source="arch",
                  descent=1.6, color="#ffe2a0", lift=True, rise=True, arch=1.0)

# ---- water and symbols (section L)
SYMBOLS = [dict(kind="emblem", t0=14.5, t1=18.0, out=19.5, x=0.46, y=0.60, size=0.20, leave="to_star", star=4)]
RIPPLES = [(18.1, 0.46, 1.0), (18.7, 0.40, 0.6), (19.2, 0.53, 0.7)]
RIPPLES_AUTO = 1.0
FALLING_STARS = [(3.0, 0.34, 0.17)]

# ---- creatures (section M)
DOVES = Track([(0, 0.0), (4.0, 0.0), (6.5, 1.0), (24.0, 1.0), (27.0, 0.0), (TOTAL, 0.0)])
DOVES_COUNT = 9
DOVES_FROM = (-0.04, 0.48)
DOVES_PATH = [(4.0, (0.22, 0.62)), (11.0, (0.66, 0.84)), (18.0, (0.26, 0.84)), (26.0, STAR_POS[4])]
DOVES_ORBIT = 0.10
DOVES_SIZE = 0.028

# ---- nature (section N)
TREE = 1.0
TREE_GROW = Track([(0, 0.0), (0.8, 0.0), (9.0, 1.0)])
TREE_X, TREE_Y, TREE_HEIGHT = 0.91, 0.338, 0.40
BLOSSOM = Track([(0, 0.0), (11.0, 0.0), (18.0, 1.0)])
WIND = Track([(0, 0.25), (14.0, 0.45), (TOTAL, 0.35)])

# ---- sky and camera (section O): clouds, god rays from the rising sun, one slow move
CLOUDS3D = Track([(0, 0.35), (10.0, 0.70), (20.0, 0.60), (TOTAL, 0.45)])
CLOUDS_SPEED = 1.4
GOD_RAYS = Track([(0, 0.0), (9.5, 0.0), (13.0, 0.85), (20.0, 0.85), (24.5, 0.45), (TOTAL, 0.35)])
RAYS_DECAY = 0.988
# the land starts a little high and settles as the camera pushes in, so the far shore ends just above the calm third
CAMERA_CRANE = Track([(0, -0.05), (TOTAL, 0.0)])
CAMERA_ZOOM = Track([(0, 1.0), (TOTAL, 1.06)])
CAMERA_PAN = Track([(0, -0.015), (TOTAL, 0.015)])
CAMERA_MOTES = 0.5

# ---- music reactivity (section P)
AUDIO_REACT = 1.0
REACT_GLOW = 0.8
REACT_SPARKLE = 0.8
REACT_ARCH = 1.0
REACT_CHORUS = 0.8
