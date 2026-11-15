"""PETALS: film 05 of the ten concert promos for the Healing Concert "The Words of Mother's Love" (60 s).

A kind word is a petal: you cannot keep it, only open your hand. The wind takes it, and wherever it lands
someone blossoms. The camera rides one gust of petals through a spring water meadow, from person to person,
nine words, home to a great tree of light whose nine boughs bloom in the nine colours, and the tree lets go.

Audio: audio/promo/concert-medley.mp3 (sections 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 with the breath
to 42.51, 49.47; the loudest moment about 54.3; the final hit 58.11). Every section start is a gust: the petals
in the air surge and the camera is thrown to the next place.

  0.00  A young woman of light in close profile, palm raised, petals already leaving it; the low sun behind
        her head. 0.25: the gust. She unwinds into petals and the camera is torn off with them, skimming the
        mirror; the stream lands as "How are you?" in front of a man standing on the water.        Greeting
  6.84  Thrown up and over: straight down onto the lake, where the petals thrown up by a child write thanks
        on the water, beside the woman she ran to.                                                  Gratitude
 13.30  A spinning dive to two friends under a bare tree. The apology rises out of its own reflection
        between them. 18.20: their hands meet, the tree bursts into blossom and the words turn pink: the
        apology becomes its own answer (19.85, the bass).                         Apology, Inclusiveness
 22.60  Stepping stones: one person sweeps an open arm, the other walks on ahead.                Concession
 26.79  Two people on the water, one speaking, one kneeling to listen; the lens opens until the whole world
        behind them has melted into soft light.                                                        Respect
 33.36  The gale: a full barrel roll down behind a runner; the words ride ahead of her at her own speed
        while the world streaks past; two people cheer and pray as she passes.                  Encouragement
 38.40  The wind drops (the breath): an elder kneeling by the water, a hand offered to him.     Consideration
 42.51  The biggest hit: the words fly on and open over a child who jumps into the light.         Compliment
 46.60  The great gust round the tree: Heavenly Mother, only from behind, veiled, at the foot of the tree,
        the sun through her veil; she opens her arms and turns to petals that rise into the boughs.
 49.47  The spiral climb: the nine boughs burst into blossom in the nine colours, one after another.
 54.30  The peak: the tree lets go of everything at once; the camera pulls back over the lake, and the end
        card holds from 55.4 to the last frame on a cream sky, petals still drifting (no fade to black).

House rules kept: no faces (profiles and figures from behind only), everyone clothed in garments of light,
Heavenly Mother only from behind, the nine expressions in their exact wording from words.EXPRESSIONS, each read
for 2.6 s or more, nothing dark behind text, no lyrics, no em or en dash.
"""
import numpy as np

import songs.s03_original as _base

TOTAL = 60.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 59.6
_base.SONG_END = 60.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])          # frame 0 is a picture, the end is never black
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:                       # the flat expressions stay off: the words are particles here
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402
from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d import ten_05_petals as K  # noqa: E402
from p3d.camera import Rig, dolly, fly, hold, orbit  # noqa: E402
from p3d.effects import Flare, Wind  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))  # noqa: F405
MUSIC_END = 59.6
SONG_END = 60.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0                 # nothing dark behind any text

# ---- the medley (scratchpad medley2/SECTION-MAP.md)
HIT0, S2, S3, S4, S5, S6, S7, BIG, S8 = 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 42.51, 49.47
PEAK, FINAL = 54.3, 58.11
TOUCH = 18.20                     # a measured hit in section 3: the friends' hands meet
GUST2 = 22.75                     # on to the stepping stones (between the bar starts 22.17 and 24.45)
CALM = 38.40                      # the runner has gone through her words; the wind drops
HOME = 46.60                      # the great gust round the tree

# ---- the end card (the standard end card: coral title by a ribbon, navy lines rising)
FORM_DUR = 2.5
TITLE_HIT = 54.6
T_FORM = TITLE_HIT - FORM_DUR - 0.75
TAG_T0, TAG_T1 = 54.4, 55.4
_base.FORM_DUR, _base.TITLE_HIT = FORM_DUR, TITLE_HIT
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=TAG_T0, t1=TAG_T1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
FRAGMENTS = []
_base.TITLE, _base.TAGLINE = TITLE, TAGLINE


# ---------------------------------------------------------------------------------------------------------
# Space: the great tree stands at the origin; the stations lie round it on the water.
# ---------------------------------------------------------------------------------------------------------
def _d(az):
    a = np.radians(az)
    return np.array([np.sin(a), 0.0, np.cos(a)])


def _r(az):
    """Screen right for a camera looking toward azimuth az."""
    a = np.radians(az)
    return np.array([-np.cos(a), 0.0, np.sin(a)])


def az_of(v):
    return float(np.degrees(np.arctan2(v[0], v[2])))


class St:
    """A station: a place on the water (x, z) and the azimuth the camera looks along there."""

    def __init__(self, x, z, view):
        self.c, self.view = np.array([x, 0.0, z], np.float64), float(view)

    def __call__(self, f=0.0, s=0.0, u=0.0):
        """f metres forward (away from the camera), s metres to screen right, u metres up."""
        return self.c + _d(self.view) * f + _r(self.view) * s + np.array([0.0, u, 0.0])


SUN_AZ = 200.0
A = St(6.0, 46.0, 180.0)          # the giver: into the low sun
B = np.array([22.0, 0.0, 40.0])   # the lake page (Gratitude, from straight above)
C = St(34.0, 26.0, 20.0)          # two friends under a small tree
D = St(44.0, 8.0, 20.0)           # the stepping stones
E = St(26.0, -24.0, 310.0)        # the one who speaks and the one who listens (the great tree far behind)
RUN_AZ, RUN_V, RUN_T0 = 280.0, 5.2, 32.9
RUN_P0 = np.array([14.0, 0.0, -40.0])
G = St(-32.0, -14.0, 150.0)       # the breath: an elder, a helping hand; then the child in the light
M = St(0.0, 9.5, 180.0)           # Heavenly Mother at the foot of the tree, facing it (from behind only)


def runner(t):
    return RUN_P0 + _d(RUN_AZ) * RUN_V * max(t - RUN_T0, 0.0)


def _chase(t):
    p = runner(t)
    return (p - _d(RUN_AZ) * 4.2 + _r(RUN_AZ) * 1.1 + np.array([0.0, 1.15, 0.0]),
            p + _d(RUN_AZ) * 10.0 + np.array([0.0, 2.3, 0.0]))


def _smooth_keys(keys):
    k = sorted(keys)
    tt = np.array([a for a, _ in k])
    vv = np.array([b for _, b in k])

    def f(t):
        if t <= tt[0]:
            return float(vv[0])
        if t >= tt[-1]:
            return float(vv[-1])
        i = int(np.searchsorted(tt, t)) - 1
        u = (t - tt[i]) / (tt[i + 1] - tt[i])
        u = u * u * (3 - 2 * u)
        return float(vv[i] + (vv[i + 1] - vv[i]) * u)
    return f


# the camera's roll: a bank on the first gust, a spin in the dive, a full barrel roll in the gale
ROLL = _smooth_keys([(0.0, 0.0), (HIT0, 0.0), (1.05, -20.0), (1.9, 6.0), (2.7, 0.0),
                     (S2, 0.0), (7.7, 12.0), (8.9, 0.0),
                     (S3, 0.0), (13.95, -40.0), (14.7, -8.0), (15.3, 0.0),
                     (S4 - 0.05, 0.0), (S4 + 0.5, 5.0), (21.0, 0.0),
                     (GUST2, 0.0), (23.3, -10.0), (24.0, 0.0),
                     (S5, 0.0), (27.5, 12.0), (28.4, 0.0),
                     (S6, 0.0), (34.35, 360.0), (CALM, 360.0), (39.3, 352.0), (40.21, 360.0),
                     (BIG, 360.0), (43.2, 366.0), (44.2, 360.0),
                     (HOME - 0.2, 360.0), (47.1, 335.0), (47.8, 360.0),
                     (S8, 360.0), (52.0, 352.0), (PEAK, 360.0), (TOTAL, 360.0)])


def _moves(focus):
    """The camera, as one list of moves. focus: the rig's focus (a world point function or "target")."""
    a1 = (A(-4.6, 8.6, 1.15), A(1.0, 12.4, 2.35))      # the Greeting set-up (camera, target)
    b0 = (B + np.array([0.0, 11.0, 3.4]), B + np.array([0.0, 0.0, 0.3]))
    b1 = (B + np.array([0.8, 12.7, 3.0]), B + np.array([0.4, 0.0, 0.0]))
    c0 = (C(-7.4, -0.3, 1.35), C(0.0, 0.0, 2.05))
    d0 = (D(-8.6, -0.6, 1.2), D(2.6, 0.0, 2.05))
    e0 = (E(-7.2, -0.4, 1.25), E(0.0, 0.0, 1.75))
    g0 = (G(-5.6, -0.3, 1.6), G(0.0, 0.0, 1.5))
    m0 = (M(-2.5, 0.45, 1.5), M(0.0, 0.0, 1.8))
    ch = [(t, *_chase(t)) for t in np.arange(S6 + 0.25, CALM + 0.01, 0.5)]
    return [
        # 1. close profile; the gust tears the camera off downwind; hover on the Greeting
        hold(A(-1.75, 0.18, 1.50), A(0.0, 0.22, 1.56), -1.0, HIT0, drift=(0.05, 0.0, 0.0), fov=30, aperture=0.035),
        fly([(HIT0, A(-1.75, 0.25, 1.50), A(0.0, 0.3, 1.56)), (1.1, A(-2.4, 2.6, 1.25), A(0.6, 5.5, 1.7)),
             (1.9, A(-3.6, 6.0, 1.05), A(1.5, 10.5, 2.1)), (2.8, *a1)],
            fov=lambda t: 30.0 + 12.0 * float(K._ss(HIT0, 2.6, t)), aperture=0.02, blend=0.25),
        hold(a1[0], a1[1], 2.8, S2, drift=(0.22, 0.03, -0.08), fov=42, aperture=0.05, blend=0.8),
        # 2. thrown up and over: straight down on the lake page
        fly([(S2, a1[0] + np.array([0.22, 0.03, -0.08]) * 4.0, a1[1]),
             (7.7, B + np.array([-4.0, 6.5, 7.5]), B + np.array([0.0, 0.0, -1.0])), (9.0, *b0)],
            fov=(44, 50), aperture=0.01, blend=0.35),
        dolly(b0[0], b1[0], 9.0, S3, look=(b0[1], b1[1]), fov=50, aperture=0.0, blend=0.8),
        # 3. a spinning dive to the two friends; push in on their hands; blown back by the blossom
        fly([(S3, b1[0], b1[1]), (14.1, C(-4.0, 2.5, 5.0), C(0.0, 0.0, 1.0)), (15.2, *c0)],
            fov=(50, 38), aperture=0.02, blend=0.35),
        hold(c0[0], c0[1], 15.2, 17.4, drift=_d(C.view) * 0.18, fov=38, aperture=0.05, blend=0.7),
        dolly(C(-7.0, -0.25, 1.32), C(-3.9, -0.1, 1.22), 17.4, S4, look=(C(0.0, 0.0, 1.9), C(0.0, 0.0, 1.45)),
              fov=(38, 33), aperture=0.05, ease="smooth", blend=0.6),
        dolly(C(-4.2, 0.0, 1.1), C(-7.2, 0.4, 0.75), S4, GUST2, look=C(0.7, 0.0, 2.85),
              fov=36, aperture=0.05, ease="out", blend=0.3),
        # 4. on to the stepping stones
        fly([(GUST2, C(-7.2, 0.4, 0.75), C(0.7, 0.0, 2.85)), (23.3, D(-12.0, -4.0, 2.6), D(0.0, 0.0, 1.6)),
             (24.0, *d0)], fov=(40, 40), aperture=0.02, blend=0.35),
        dolly(d0[0], D(-6.2, -0.2, 1.25), 24.0, S5, look=(d0[1], D(3.0, 0.0, 2.0)), fov=40, aperture=0.04,
              blend=0.6),
        # 5. the two who talk: the lens opens
        fly([(S5, D(-6.2, -0.2, 1.25), D(3.0, 0.0, 2.0)), (27.6, E(-12.0, 3.0, 3.0), E(0.0, 0.0, 1.5)),
             (28.4, *e0)], fov=(42, 36), aperture=0.02, blend=0.35),
        hold(e0[0], e0[1], 28.4, S6, drift=_d(E.view) * 0.12, fov=36, focus=7.2,
             aperture=Track([(28.4, 0.04), (29.2, 0.05), (31.6, 0.22), (S6, 0.22)]), blend=0.7),
        # 6. the gale: a barrel roll down behind the runner, then the chase
        fly(ch, fov=lambda t: 56.0 - 18.0 * float(K._ss(S6, 34.6, t)), aperture=0.02, focus=4.4, blend=0.6),
        # 7. the breath: hang and sink toward an elder and a helping hand
        fly([(CALM, *_chase(CALM)), (39.3, G(-8.0, -1.2, 3.4), G(0.0, 0.0, 1.3)), (S7, *g0)],
            fov=(40, 38), aperture=0.04, blend=0.5),
        hold(g0[0], g0[1], S7, BIG, drift=np.array([0.0, -0.06, 0.0]) + _d(G.view) * 0.12, fov=38, aperture=0.08,
             blend=0.8),
        # the biggest hit: thrown low and wide into the light over a jumping child
        dolly(G(-5.2, -0.2, 1.45), G(-8.4, 2.4, 0.55), BIG, HOME, look=(G(0.6, 1.0, 2.0), G(1.4, 1.6, 2.7)),
              fov=(44, 40), aperture=0.03, ease="out", blend=0.25),
        # 8. home: round the tree to Heavenly Mother, from behind
        fly([(HOME, G(-8.4, 2.4, 0.55), G(1.4, 1.6, 2.7)), (47.1, np.array([-14.0, 2.4, 9.0]),
                                                              np.array([0.0, 3.0, 12.0])), (47.9, *m0)],
            fov=(52, 34), aperture=0.02, blend=0.3),
        hold(m0[0], m0[1], 47.9, S8, drift=(0.05, 0.08, 0.15), fov=34, aperture=0.04, blend=0.6),
        # 9. the spiral climb past the nine boughs
        orbit((0.0, 8.0, 0.0), radius=(11.6, 8.6), height=(2.0, 18.0), a0=8.0, a1=118.0, t0=S8, t1=PEAK,
              look=lambda t: (0.0, 4.5 + 2.4 * (t - S8), 0.0), fov=52, aperture=0.03, blend=0.9),
        # 10. the tree lets go; pull back over the lake to the end card
        fly([(PEAK, np.array([0.0, 18.0, 0.0]) + _d(118.0) * 8.6, np.array([0.0, 16.0, 0.0])),
             (55.4, _d(116.0) * 30.0 + np.array([0.0, 9.0, 0.0]), np.array([0.0, 19.5, 0.0])),
             (56.7, _d(112.0) * 56.0 + np.array([0.0, 4.2, 0.0]), np.array([0.0, 22.5, 0.0])),
             (TOTAL + 0.5, _d(109.0) * 63.5 + np.array([0.0, 3.4, 0.0]), np.array([0.0, 23.0, 0.0]))],
            fov=46, aperture=0.0, blend=0.4),
    ]


def _rig(focus="target"):
    return Rig(_moves(focus), roll=ROLL, handheld=0.22, shutter=0.45, min_height=0.3, focus=focus)


_LAYOUT = _rig()


# ---------------------------------------------------------------------------------------------------------
# The words: laid out by where they are read in the picture (the screen place of the block's centre, its
# depth and the pixels of one em at 1080p, at the middle of the reading moment)
# ---------------------------------------------------------------------------------------------------------
def _w(expr, x, y, depth, px, t_in, r0, r1, t_out, **kw):
    tm = 0.5 * (r0 + r1)
    return dict(expr=expr, pos=tuple(PW.place(_LAYOUT, tm, x, y, depth)), em=PW.em_for(_LAYOUT, tm, depth, px),
                t_in=t_in, t_read0=r0, t_read1=r1, t_out=t_out, **kw)


BODIES = {}


def _palm(name, side="R", lift=0.0):
    def f(t):
        b = BODIES.get(name)
        if b is None:
            return np.zeros(3)
        p = np.asarray(b.where(t, "palm." + side), np.float64)
        return p + np.array([0.0, lift, 0.0])
    return f


WIND = Wind(base=(2.0, 0.25, -0.6), gusts=[(t, 3.2, 1.4) for t in (HIT0, S2, S3, S4, GUST2, S5, S6, BIG, HOME,
                                                                      S8, PEAK)], sway=0.3, seed=2.0)

# flat words on the lake page: the block's centre on the water, read from the +z side
_GRAT_EM = PW.em_for(_LAYOUT, 11.1, 11.6, 90)

_SPECS = [
    _w("Greeting", 0.52, 0.64, 7.0, 104, HIT0, 2.6, 6.6, 8.2, arrive="petals", source=_palm("giver", "R"),
       leave="petals", wind=(1.0, 0.35, -0.2)),
    dict(expr="Gratitude", pos=(float(B[0]), 0.04, float(B[2])), em=_GRAT_EM, face="flat", facing=0.0,
         t_in=7.3, t_read0=9.4, t_read1=12.9, t_out=14.6, arrive="petals", source=_palm("child", "R", 0.1),
         leave="petals", wind=(0.8, 0.9, -0.3)),
    _w("Apology", 0.5, 0.66, 7.4, 92, S3 + 0.2, 15.0, 18.0, 18.2, arrive="lake", leave="morph"),
    _w("Inclusiveness", 0.5, 0.64, 7.8, 104, TOUCH, S4 + 0.25, GUST2, 24.0, arrive="morph", source="Apology",
       leave="petals", wind=(1.0, 0.4, -0.3)),
    _w("Concession", 0.5, 0.68, 9.5, 104, 23.0, 24.15, S5 - 0.07, 28.2, arrive="petals",
       source=_palm("yielder", "R"), leave="wind", wind=(1.0, 0.2, -0.4)),
    _w("Respect", 0.5, 0.69, 7.0, 96, S5 + 0.4, 28.6, 31.7, 33.2, arrive="palm", source=_palm("speaker", "R"),
       leave="petals", wind=(1.0, 0.5, -0.2)),
    dict(expr="Encouragement", ride=(0.5, 0.67, 9.0), face="screen",
         em=PW.em_for(_LAYOUT, 36.0, 9.0, 92), t_in=S6 + 0.2, t_read0=34.6, t_read1=37.5, t_out=CALM + 0.2,
         arrive="petals", leave="petals", wind=(-0.4, 0.8, 0.2)),
    _w("Consideration", 0.5, 0.68, 6.6, 102, CALM, 39.9, 42.45, 42.5, arrive="palm", source=_palm("helper", "L"),
       leave="morph"),
    _w("Compliment", 0.56, 0.70, 8.0, 104, BIG, 43.6, HOME - 0.2, 48.0, arrive="morph", source="Consideration",
       leave="petals", wind=(-0.6, 0.8, 0.5)),
]
WORDS = PW.Words(_SPECS, face="camera", camera=_LAYOUT, tint=0.6, bright=1.25)

_FOCUS_DEFAULT = lambda t: _LAYOUT.state(t).target       # noqa: E731
CAMERA = _rig(focus=lambda t: WORDS.focus_point(t, _FOCUS_DEFAULT))

# ---------------------------------------------------------------------------------------------------------
# The great tree: nine boughs that bloom in the nine colours as the camera climbs past them; each word buds
# its bough when it leaves
# ---------------------------------------------------------------------------------------------------------
_COL9 = [e["color"] for e in PW.EXPRESSIONS]
_BLOOM = [S8 + 0.25 + 0.5 * i for i in range(9)]
_BOUGH_AZ = [8.0 + 110.0 * (b - S8) / (PEAK - S8) + 28.0 for b in _BLOOM]
_BUD = [WORDS[e["label"]].t_read1 for e in PW.EXPRESSIONS]


def _setup(scene):
    from p3d.body import Body
    w = WIND
    glow = dict(look="glitter", wind=w, fade=0.7, points=52000)

    def body(name, shape, **kw):
        d = dict(glow)
        d.update(kw)
        b = Body(shape, **d)
        BODIES[name] = b
        b.add(scene, name)
        return b

    # 1. the giver and the man she greets
    body("giver", "woman", at=(A.c[0], A.c[2]), facing=90.0, garment="dress", hair=True, color="#ff9f84",
         color2="#ffe7cf", gesture=[(-3.0, 2.2, "blow")], show=(-1.0, 2.6), fade=0.3, bright=1.5,
         effects=[dict(kind="petals", t=HIT0, dur=1.6)])
    man = PW.place(_LAYOUT, 4.6, 0.30, 0.42, 8.6)
    body("stranger", "man", at=(man[0], man[2]), facing=az_of(_d(A.view) * -1.0 + _r(A.view) * 1.4),
         garment="coat", color="#ffd2b0", color2="#fff4e4",
         gesture=[(2.2, 4.6, "look_up"), (4.4, 7.4, "reach", dict(to=tuple(WORDS["Greeting"].centre(4.0))))],
         show=(0.8, 8.4), bright=1.4)
    # 2. the child and the woman at work in the shallows (seen from above)
    body("child", "child", at=(B[0] - 6.6, B[2] + 2.8), facing=90.0, garment="tunic", color="#ffd56a",
         color2="#fff3cf", gesture=[(7.0, 11.5, "raise")], show=(6.6, 14.6), bright=1.5)
    body("worker", "woman", at=(B[0] - 5.4, B[2] + 3.8), facing=60.0, garment="robe", color="#ffe1a8",
         color2="#ffffff", motion=[(6.6, "kneel", dict(one=True))], show=(6.6, 14.6), bright=1.4)
    # 3. two friends under the small tree
    m_at, w0, w1 = C(0.0, 1.35, 0.0), C(0.25, -1.7, 0.0), C(0.1, -0.5, 0.0)
    meet = 0.5 * (m_at + w1) + np.array([0.0, 1.12, 0.0])
    body("friend_m", "man", at=(m_at[0], m_at[2]), facing=az_of(w1 - m_at), garment="coat", color="#ffbf8f",
         color2="#ffeedd", gesture=[(13.0, 17.3, "offer"), (17.3, 23.6, "reach", dict(to=tuple(meet)))],
         show=(S3, 23.8), bright=1.4)
    body("friend_w", "woman", at=[(16.8, (w0[0], w0[2])), (17.9, (w1[0], w1[2]))],
         facing=[(16.6, az_of(w0 - m_at)), (17.4, az_of(m_at - w1))],
         motion=[(0.0, "stand"), (16.8, "shuffle"), (17.9, "stand")], garment="dress", hair=True,
         color="#ffa9c4", color2="#fff0f5", gesture=[(17.4, 23.6, "reach", dict(to=tuple(meet)))],
         show=(S3, 23.8), bright=1.4)
    scene.add("touch", Flare(tuple(meet), TOUCH, color="#ffd0e0", color2="#fff6d8", strength=0.7, reach=0.7))
    small = C(3.4, 0.4, 0.0)
    scene.add("small_tree", K.Tree(base=small, height=6.5, boughs=6, colors=("#F582AF", "#FFD0E0", "#ffffff"),
                                   bloom=[TOUCH + 0.12 * i for i in range(6)], crown_t=TOUCH + 0.1,
                                   crown_colors=("#ffffff", "#FFC4DA", "#F582AF"), n_bloom=1500, n_crown=7000,
                                   n_bark=9000, seed=12))
    # 4. the stepping stones
    stones = [D(0.9 + 0.95 * k, 0.12 * np.sin(1.7 * k), 0.0) for k in range(16)]
    scene.add("stones", K.Stones(stones))
    body("yielder", "woman", at=tuple(D(0.2, -1.15, 0.0)[[0, 2]]), facing=az_of(_r(D.view)), garment="robe",
         color="#a9cdf5", color2="#ffffff", gesture=[(22.6, 27.4, "offer")], show=(GUST2 - 0.2, 28.0),
         bright=1.5)
    p0 = D(0.75, 0.15, 0.0)
    body("passer", "man", at=(p0[0], p0[2]), facing=D.view, motion=[(0.0, "stand"), (24.4, "walk", dict(speed=1.0))],
         garment="tunic", color="#cfe2ff", color2="#ffffff", show=(GUST2 - 0.2, 28.0), bright=1.5)
    # 5. the one who speaks, the one who listens
    sp, li = E(0.0, -1.0, 0.0), E(0.15, 0.95, 0.0)
    body("speaker", "woman", at=(sp[0], sp[2]), facing=az_of(li - sp), garment="robe", stoop=0.3,
         color="#f2c3ad", color2="#fff1ea", gesture=[(26.4, 33.4, "offer")], show=(S5 - 0.3, 33.6), bright=1.5)
    body("listener", "man", at=(li[0], li[2]), facing=az_of(sp - li), garment="tunic", color="#e9b9a0",
         color2="#fff3ec", motion=[(0.0, "stand"), (27.2, "kneel", dict(one=True))],
         gesture=[(28.0, 33.4, "listen")], show=(S5 - 0.3, 33.6), bright=1.5)
    # 6. the runner and two who cheer her on
    body("runner", "woman", at=(RUN_P0[0], RUN_P0[2]), facing=RUN_AZ, motion=[(RUN_T0, "run", dict(speed=RUN_V))],
         garment="tunic", hair=True, color="#c9b2f2", color2="#ffffff", show=(RUN_T0, CALM + 0.4), bright=1.6,
         effects=[dict(kind="petals", t=37.55, dur=1.0)])
    c1 = runner(35.0) + _r(RUN_AZ) * -3.4
    c2 = runner(36.3) + _r(RUN_AZ) * 3.2
    body("cheer1", "man", at=(c1[0], c1[2]), facing=az_of(runner(35.0) - c1), garment="coat", color="#d9c8ff",
         color2="#ffffff", gesture=[(33.6, 38.8, "raise_hand")], show=(33.4, 38.8), bright=1.4, points=40000)
    body("cheer2", "woman", at=(c2[0], c2[2]), facing=az_of(runner(36.3) - c2), garment="dress", color="#e6d9ff",
         color2="#ffffff", gesture=[(33.6, 38.8, "pray")], show=(33.4, 38.8), bright=1.4, points=40000)
    # 7. the elder who knelt, the hand offered to him, the child who jumps
    el, hp = G(0.1, -0.6, 0.0), G(0.0, 0.62, 0.0)
    body("elder", "man", at=(el[0], el[2]), facing=az_of(hp - el), garment="coat", stoop=0.35,
         color="#f6b3c2", color2="#fff0f3", motion=[(0.0, "kneel", dict(one=True))], show=(37.8, HOME + 0.4),
         bright=1.4)
    body("helper", "woman", at=(hp[0], hp[2]), facing=az_of(el - hp), garment="robe", color="#ff9fb4",
         color2="#ffffff", gesture=[(38.0, HOME, "offer")], show=(37.8, HOME + 0.4), bright=1.5)
    ch = G(1.2, 2.0, 0.0)
    body("child2", "child", at=(ch[0], ch[2]), facing=az_of(-_r(G.view)), garment="tunic", color="#d8c2ff",
         color2="#ffffff", motion=[(0.0, "stand"), (BIG + 0.1, "jump")], gesture=[(41.8, 47.0, "raise")],
         show=(41.4, 48.0), bright=1.7)
    # 8. Heavenly Mother, only from behind, at the foot of the tree; she turns to petals that rise
    body("mother", "woman", at=(M.c[0], M.c[2]), facing=180.0, garment="robe", veil=dict(length=1.5, wide=1.1),
         color="#ffd98f", color2="#fff7e6", gesture=[(47.6, 52.0, "open_arms")], show=(HOME - 0.2, 50.8),
         bright=1.7, points=70000, effects=[dict(kind="petals", t=S8 + 0.1, dur=1.4)])
    # the world: the tree, the meadow, the petals in the air, the release at the peak
    tree = K.Tree(colors=_COL9, bough_az=_BOUGH_AZ, bud=_BUD, bloom=_BLOOM, crown_t=PEAK - 0.4)
    scene.add("tree", tree)
    scene.add("meadow", K.Meadow())
    scene.add("wind_petals", PW.KeepClear(K.PetalWind(WIND, amount=PETAL_AMOUNT), WORDS))
    scene.add("palm_stream", K.Stream(_palm("giver", "R", 0.02), lambda t: WORDS["Greeting"].centre(t), -1.5, 1.0,
                                      wind=WIND, n=1400, flight=1.2, arc=0.4))
    scene.add("release", K.Release(tree.bloom_pts, PEAK, WIND, _COL9 + ["#ffffff", "#FFE9D6"]))
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


PETAL_AMOUNT = Track([(0.0, 0.5), (S2, 0.6), (S4, 0.75), (S6, 0.9), (CALM, 0.9), (S7, 0.45), (BIG, 1.0),
                      (TOTAL, 1.0)])
_SPRING = dict(base="day", sky_top=theme.display("#2b6fd2") * 0.92, sky_mid=theme.display("#6aa8e8") * 0.85,
               sky_hor=theme.display("#f6e2c6") * 0.62, sun_az=SUN_AZ, sun_el=11.0,
               sun_color=theme.display("#fff0d2") * 0.30, sun_int=0.95, rays=0.35, clouds=0.25,
               haze=0.5, haze_color=theme.display("#ece4d8") * 0.5, water=theme.display("#3a72c0") * 0.45,
               hill_color=theme.display("#5f8cc0") * 0.5, mist=0.15, dust=0.5, dust_color="#fff4e0",
               dust_color2="#ffd2b8", sun_disc=3.0, sun_glow=0.75)
LOOKS = dict(
    spring=_SPRING,
    breath=dict(_SPRING, sky_mid=theme.display("#a9c4ea") * 0.85, sky_hor=theme.display("#ffe0cf") * 0.66,
                haze=0.7, mist=0.45, mist_color=theme.display("#fff0e4") * 0.55, rays=0.45, sun_el=13.0),
    radiance=dict(_SPRING, sky_top=theme.display("#2f74d6") * 0.92, sky_mid=theme.display("#86b8ec") * 0.86,
                  sky_hor=theme.display("#ffe6b8") * 0.66, sun_int=1.2, rays=0.7, sun_el=14.0,
                  sun_color=theme.display("#fff0c8") * 0.35),
)
P3D = dict(
    camera=CAMERA,
    world=dict(
        looks=LOOKS,
        look=[(0.0, "spring"), (S7, "breath", 1.6), (BIG, "radiance", 0.5), (PEAK - 0.6, "cream", 3.2)],
        sun_az=SUN_AZ,
        light=dict(pos=tuple(M(2.6, 0.25, 2.0)), color="#ffe6b0", size=0.7, rays=1.0,
                   strength=lambda t: float(K._ss(HOME + 0.6, 47.8, t) * (1.0 - K._ss(S8 + 0.6, S8 + 1.6, t))) * 1.1),
        react=dict(beat=0.3, level=0.25),
    ),
    bursts=[dict(t=TOUCH, strength=0.6, at=None, radius=0.25, color="#fff0f4", rise=0.15, fall=0.7),
            dict(t=BIG, strength=0.8, radius=0.35, color="#fff6e0", rise=0.12, fall=0.8),
            dict(t=PEAK, strength=0.9, radius=0.4, color="#fff8ee", rise=0.15, fall=1.0)],
    clear=[dict(box=(0.08, 0.40, 0.92, 0.86), t0=PEAK, t1=TOTAL + 1.0, soft=0.06, amount=0.92)],
    setup=_setup,
)
