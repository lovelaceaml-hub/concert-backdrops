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
PAIR_T = 37.70                    # the helper starts toward the elder (the pair clip): clasp 41.6, he rises 41.7 to 42.7

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

# ---- the concert badge (Anthony: the concert title and the date show from the beginning and throughout): large
# on frame 0, settled into the top left corner by 2.8 s, gone as the end card forms (it carries the same words).
# Warm white on this film's deep upper skies; every shot keeps the top left sky open behind it.
CREDIT = dict(song="The Words of Mother’s Love",
              concert="Healing Concert · Sunday, December 6 · 4:30 PM",
              t_in=-1.0, t_full=0.0, t_move=1.6, t_rest=2.8, scale=0.55, alpha_rest=0.92,
              margin_x=0.035, margin_top=0.05)
BADGE_OUT = (T_FORM, T_FORM + 1.0)
BADGE_BBOX = (0.132, 0.869, 0.497, 0.686)      # the card at full size (text.render_credit), screen fractions, y up


def _ss1(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3 - 2 * u)


def credit_state(t, bbox):
    """Centre, scale and strength of the badge; bbox is its size at full card size."""
    c = CREDIT
    x0, x1, y0, y1 = bbox
    a_in = _ss1(c["t_in"], c["t_full"], t)
    m = _ss1(c["t_move"], c["t_rest"], t)
    scale = c["scale"] ** m
    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    tx = c["margin_x"] + c["scale"] * (x1 - x0) / 2.0
    ty = 1.0 - c["margin_top"] - c["scale"] * (y1 - y0) / 2.0
    cx, cy = cx0 * (1 - m) + tx * m, cy0 * (1 - m) + ty * m
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - _ss1(BADGE_OUT[0], BADGE_OUT[1], t))
    return (cx, cy, scale, alpha), (cx0, cy0)


def badge_box(t, pad=0.025):
    """The badge on screen at t (x0, y0, x1, y1; y up), with a margin: nothing of the 3D layer falls in it."""
    (cx, cy, sc, a), _ = credit_state(t, BADGE_BBOX)
    hw, hh = 0.5 * (BADGE_BBOX[1] - BADGE_BBOX[0]) * sc + pad, 0.5 * (BADGE_BBOX[3] - BADGE_BBOX[2]) * sc + pad
    return (cx - hw, cy - hh, cx + hw, cy + hh), a


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
A = St(6.0, 46.0, 165.0)          # the giver: the low sun just off the left of the picture
B = np.array([22.0, 0.0, 40.0])   # the lake page (Gratitude, from straight above)
C = St(34.0, 26.0, 20.0)          # two friends under a small tree
D = St(44.0, 8.0, 20.0)           # one lets the other go first
E = St(26.0, -24.0, 130.0)        # the one who speaks and the one who listens (open water behind them)
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
ROLL = _smooth_keys([(0.0, 0.0), (HIT0, 0.0), (1.05, -9.0), (1.9, 3.0), (2.7, 0.0),
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
    b0 = (B + np.array([0.0, 9.6, 3.0]), B + np.array([0.0, 0.0, 0.6]))
    b1 = (B + np.array([0.7, 11.0, 2.6]), B + np.array([0.4, 0.0, 0.3]))
    c0 = (C(-7.4, -0.3, 1.35), C(0.0, 0.0, 2.05))
    d0 = (D(-8.6, -0.6, 1.2), D(2.6, 0.0, 2.05))
    e0 = (E(-7.2, -0.4, 1.25), E(0.0, 0.0, 1.75))
    g0 = (G(-5.6, -0.3, 1.6), G(0.0, 0.0, 1.5))
    m0 = (M(-2.5, 0.45, 1.5), M(0.0, 0.0, 1.8))
    ch = [(t, *_chase(t)) for t in np.arange(S6 + 0.25, CALM + 0.01, 0.5)]
    return [
        # 1. close profile; the gust tears the camera off downwind; hover on the Greeting
        hold(A(-1.9, -0.05, 1.45), A(0.0, -0.25, 1.64), -1.0, HIT0, drift=(0.05, 0.0, 0.0), fov=30, aperture=0.035),
        fly([(HIT0, A(-1.9, 0.0, 1.45), A(0.0, -0.15, 1.62)), (1.1, A(-2.4, 2.6, 1.25), A(0.6, 5.5, 1.7)),
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
        dolly(G(-5.2, -0.2, 1.45), G(-6.8, 1.9, 0.7), BIG, HOME, look=(G(0.6, 1.0, 2.0), G(1.2, 1.4, 2.5)),
              fov=(44, 40), aperture=0.03, ease="out", blend=0.25),
        # 8. home: round the tree to Heavenly Mother, from behind
        fly([(HOME, G(-6.8, 1.9, 0.7), G(1.2, 1.4, 2.5)), (47.1, np.array([-14.0, 2.4, 9.0]),
                                                              np.array([0.0, 3.0, 12.0])), (47.9, *m0)],
            fov=(52, 34), aperture=0.02, blend=0.3),
        hold(m0[0], m0[1], 47.9, S8, drift=(0.05, 0.08, 0.15), fov=34, aperture=0.04, blend=0.6),
        # 9. the spiral climb past the nine boughs
        orbit((0.0, 7.0, 0.0), radius=(23.0, 19.0), height=(2.2, 12.0), a0=8.0, a1=98.0, t0=S8, t1=PEAK,
              look=lambda t: (0.0, 5.5 + 0.9 * (t - S8), 0.0), fov=52, aperture=0.02, blend=0.9),
        # 10. the tree lets go; pull back over the lake to the end card
        fly([(PEAK, np.array([0.0, 12.0, 0.0]) + _d(98.0) * 19.0, np.array([0.0, 9.8, 0.0])),
             (55.4, _d(106.0) * 28.0 + np.array([0.0, 7.0, 0.0]), np.array([0.0, 16.0, 0.0])),
             (56.7, _d(112.0) * 38.0 + np.array([0.0, 3.6, 0.0]), np.array([0.0, 20.5, 0.0])),
             (TOTAL + 0.5, _d(110.0) * 41.5 + np.array([0.0, 3.2, 0.0]), np.array([0.0, 21.0, 0.0]))],
            fov=46, aperture=0.0, blend=0.4),
    ]


def _rig(focus="target"):
    return Rig(_moves(focus), roll=ROLL, handheld=0.22, shutter=0.35, min_height=0.3, focus=focus)


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
_GRAT_EM = PW.em_for(_LAYOUT, 11.1, 10.4, 90)

_SPECS = [
    _w("Greeting", 0.52, 0.62, 7.0, 104, HIT0, 2.6, 6.6, 8.2, arrive="petals", source=_palm("giver", "R"),
       leave="petals", wind=(1.0, 0.35, -0.2)),
    dict(expr="Gratitude", pos=(float(B[0]), 0.04, float(B[2])), em=_GRAT_EM, face="flat", facing=0.0,
         t_in=7.3, t_read0=9.4, t_read1=12.9, t_out=14.6, arrive="petals", source=_palm("child", "R", 0.1),
         leave="petals", wind=(0.8, 0.9, -0.3)),
    _w("Apology", 0.46, 0.57, 7.4, 92, 14.5, 15.5, 18.1, 18.2, arrive="petals", source=_palm("friend_m", "R"),
       leave="morph"),
    _w("Inclusiveness", 0.44, 0.58, 7.8, 100, TOUCH, S4 + 0.25, GUST2, 24.0, arrive="morph", source="Apology",
       leave="petals", wind=(1.0, 0.4, -0.3)),
    _w("Concession", 0.52, 0.63, 9.5, 104, 23.0, 24.15, S5 - 0.07, 28.2, arrive="petals",
       source=_palm("yielder", "R"), leave="wind", wind=(1.0, 0.2, -0.4)),
    _w("Respect", 0.53, 0.63, 7.0, 96, S5 + 0.4, 28.6, 31.7, 33.2, arrive="palm", source=_palm("speaker", "R"),
       leave="petals", wind=(1.0, 0.5, -0.2)),
    dict(expr="Encouragement", ride=(0.53, 0.64, 9.0), face="screen",
         em=PW.em_for(_LAYOUT, 36.0, 9.0, 92), t_in=S6 + 0.2, t_read0=34.6, t_read1=37.5, t_out=CALM + 0.2,
         arrive="petals", leave="petals", wind=(-0.4, 0.8, 0.2)),
    _w("Consideration", 0.53, 0.62, 6.6, 102, CALM, 39.9, 42.45, 42.5, arrive="palm", source=_palm("helper", "L"),
       leave="morph"),
    _w("Compliment", 0.60, 0.60, 8.0, 104, BIG, 43.6, HOME - 0.2, 48.0, arrive="morph", source="Consideration",
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
_BOUGH_AZ = [8.0 + 90.0 * (b - S8) / (PEAK - S8) + 20.0 for b in _BLOOM]
_BUD = [WORDS[e["label"]].t_read1 for e in PW.EXPRESSIONS]


def _setup(scene):
    from p3d.body import Body
    w = WIND
    glow = dict(look="glitter", wind=w, fade=0.7, points=52000)

    def body(name, shape, fill=None, **kw):
        d = dict(glow)
        d.update(kw)
        d["bright"] = d.get("bright", 1.5) * 1.35
        # every person sheds a few petals on the wind all the time (ref 07, 15)
        d["effects"] = list(d.get("effects", [])) + [dict(kind="shed", sprite="petal", n=1600, life=2.6, speed=0.5,
                                                          size=7.0, rise=0.12, turb=0.4)]
        b = Body(shape, **d)
        BODIES[name] = b
        if fill is None:          # a translucent coat a shade deeper than the person's own colour
            c = np.array([int(d["color"][k:k + 2], 16) for k in (1, 3, 5)]) * 0.95
            fill = "#%02x%02x%02x" % tuple(int(v) for v in c)
        # the petals that leave a person keep their colour (and keep out of the words being read), and the
        # person holds form on a bright day
        scene.add(name, K.Painted(b, fill=fill, fill_alpha=0.12, words=WORDS), mask=b.mask())
        return b

    # 1. the giver and the man she greets
    body("giver", "woman", at=(A.c[0], A.c[2]), facing=az_of(-_r(A.view)), garment="dress", hair=True, color="#ffa585",
         color2="#ffe9d2", gesture=[(-3.0, 2.2, "blow")], show=(-1.0, 2.6), fade=0.3, bright=1.6, points=70000,
         fill="#f08a6a",
         effects=[dict(kind="petals", t=HIT0, dur=1.6)])
    man = PW.place(_LAYOUT, 4.6, 0.30, 0.42, 8.6)
    body("stranger", "man", at=(man[0], man[2]), facing=az_of(_d(A.view) * -1.0 + _r(A.view) * 1.4),
         garment="coat", color="#ffd2b0", color2="#fff4e4",
         gesture=[(2.2, 4.6, "look_up"), (4.4, 7.4, "reach", dict(to=tuple(WORDS["Greeting"].centre(4.0))))],
         show=(0.8, 8.4), bright=1.4)
    # 2. the child and the woman at work in the shallows (seen from above)
    body("child", "child", at=(B[0] - 3.4, B[2] + 3.3), facing=90.0, garment="tunic", color="#ffd56a",
         color2="#fff3cf", gesture=[(7.0, 11.5, "raise")], show=(6.6, 14.6), bright=1.5)
    body("worker", "woman", at=(B[0] - 2.2, B[2] + 3.9), facing=60.0, garment="robe", color="#ffe1a8",
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
    small = C(2.4, 6.3, 0.0)
    st = K.Tree(base=small, height=6.5, boughs=6, colors=("#F582AF", "#FFD0E0", "#ffffff"),
                bloom=[TOUCH + 0.12 * i for i in range(6)], crown_t=TOUCH + 0.1,
                crown_colors=("#ffffff", "#FFC4DA", "#F582AF"), n_bloom=1500, n_crown=7000, n_bark=9000, seed=12,
                bloom_glow=0.16, petal_light=0.1)
    scene.add("small_tree", st)
    scene.add("small_tree_glow", st.glow_set())
    # 4. one lets the other go first
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
    # 7. an elder sitting by the water; someone comes and pulls him up by the hands (a pair captured together:
    # both share one placement); the clasp is at about PAIR_T + 3.9, he rises with the biggest hit
    F = az_of(_r(G.view))
    a_ = np.radians(F)
    cx, cz = 0.05, 1.75
    pair_at = (G.c[0] - (cx * np.cos(a_) + cz * np.sin(a_)), G.c[2] - (-cx * np.sin(a_) + cz * np.cos(a_)))
    body("elder", "man", at=pair_at, facing=F, garment="coat", color="#f6b3c2", color2="#fff0f3",
         motion=[(PAIR_T, "helped_up")], show=(37.6, HOME + 0.4), bright=1.4)
    body("helper", "woman", at=pair_at, facing=F, garment="robe", color="#ff9fb4", color2="#ffffff",
         motion=[(PAIR_T, "pull_up")], show=(37.6, HOME + 0.4), bright=1.5)
    ch = G(1.2, 2.0, 0.0)
    body("child2", "child", at=(ch[0], ch[2]), facing=az_of(-_r(G.view)), garment="tunic", color="#d8c2ff",
         color2="#ffffff", motion=[(0.0, "stand"), (BIG + 0.1, "jump")], gesture=[(41.8, 47.0, "raise")],
         show=(41.4, 48.0), bright=1.7)
    # 8. Heavenly Mother, only from behind, at the foot of the tree; she turns to petals that rise
    body("mother", "woman", at=(M.c[0], M.c[2]), facing=180.0, garment="robe", veil=dict(length=1.5, wide=1.1),
         color="#ffd98f", color2="#fff7e6", gesture=[(47.6, 52.0, "open_arms")], show=(HOME - 0.2, 50.8),
         bright=1.7, points=70000, effects=[dict(kind="petals", t=S8 + 0.1, dur=1.4)])
    # the world: the tree, the meadow, the petals in the air, the release at the peak
    tree = K.Tree(colors=_COL9, bough_az=_BOUGH_AZ, bud=_BUD, bloom=_BLOOM, crown_t=PEAK - 0.4,
                  crown_colors=tuple(_COL9) + ("#ffffff", "#ffffff", "#FFE9D6"))
    scene.add("tree", tree)

    def tree_glow(t):
        d = float(np.linalg.norm(CAMERA.state(t).pos - np.array([0.0, 8.0, 0.0])))
        return float(np.clip((40.0 - d) / 20.0, 0.0, 1.0))
    scene.add("tree_glow", tree.glow_set(tree_glow))
    scene.add("meadow", K.Meadow())
    scene.add("wind_petals", PW.KeepClear(K.PetalWind(WIND, n=9000, amount=lambda t: min(
        1.0, 0.8 * PETAL_AMOUNT(t) + 0.12 * WIND.gust(t))), WORDS))
    scene.add("palm_stream", K.Stream(_palm("giver", "R", 0.02), lambda t: WORDS["Greeting"].centre(t), -1.5, 1.0,
                                      wind=WIND, n=1400, flight=1.2, arc=0.4))
    scene.add("release", K.Release(tree.bloom_pts, PEAK, WIND, _COL9 + ["#ffffff", "#FFE9D6"]))
    K.paint_word_petals(WORDS)
    WORDS.add_to(scene, reflect=False)          # no words mirrored in the water
    WORDS.check(CAMERA)


PETAL_AMOUNT = Track([(0.0, 0.5), (S2, 0.6), (S4, 0.75), (S6, 0.9), (CALM, 0.9), (S7, 0.45), (BIG, 1.0),
                      (TOTAL, 1.0)])
def _L(top, mid, hor, haze_c, water, hills, sun, **kw):
    """A look of this film (display colours: the picture shows them so)."""
    D = theme.display
    d = dict(base="day", sky_top=D(top) * 0.92, sky_mid=D(mid) * 0.85, sky_hor=D(hor) * 0.64,
             haze_color=D(haze_c) * 0.5, water=D(water) * 0.45, hill_color=D(hills) * 0.5, sun_color=D(sun) * 0.32,
             sun_az=SUN_AZ, sun_el=14.0, sun_int=0.95, rays=0.3, clouds=0.2, haze=0.5, mist=0.15,
             dust=0.5, dust_color="#fff4e0", dust_color2="#ffd2b8", sun_disc=3.0, sun_glow=0.35)
    for k in ("mist_color",):
        if k in kw:
            kw[k] = D(kw[k]) * 0.55
    d.update(kw)
    return d


# one look per section: the light changes with every song of the medley
LOOKS = dict(
    first_light=_L("#1f55b4", "#6aa6e0", "#ffd49a", "#ffd8ae", "#2c58a0", "#7f93a8", "#ffcf8a", sun_el=6.5,
                   sun_int=1.0, sun_glow=0.45, rays=0.55, clouds=0.15, mist=0.25, mist_color="#ffe2c0"),
    sapphire=_L("#1d54c0", "#5b9be6", "#e8f2fa", "#e4eef6", "#1a4aa8", "#5f86b0", "#fff6e6", sun_el=24.0,
                sun_int=0.9, rays=0.2, clouds=0.25),
    pearl=_L("#3d5f98", "#7f98c0", "#e9e6e2", "#e2e2e2", "#4a6a9e", "#7d8fa2", "#fff8f0", sun_int=0.55, rays=0.1,
             clouds=0.75, mist=0.3, mist_color="#e8e8ec"),
    blush=_L("#2f6cc8", "#86b6ea", "#ffe2e8", "#ffe6ea", "#3a74c6", "#7fae86", "#fff2ea", sun_int=1.0, rays=0.35),
    azure=_L("#1048b8", "#3f8ae2", "#d8ecfc", "#dcecf8", "#1550b8", "#5f9a72", "#ffffff", sun_el=30.0, sun_int=0.9,
             rays=0.15, clouds=0.15),
    clay=_L("#1d58c0", "#5c9ae0", "#f6e2cc", "#f2e4d4", "#2a62b8", "#8f9a78", "#fff0dc", sun_el=22.0),
    gale=_L("#2e2f86", "#6a62bc", "#e2cdec", "#d8c8e8", "#2a2f78", "#4e4a80", "#f8f0ff", sun_int=0.7, rays=0.25,
            clouds=0.85, cloud_speed=6.0, mist=0.25, mist_color="#c8b8e8"),
    breath=_L("#2c5cb4", "#6a9ad8", "#f6cdb6", "#ffe2cc", "#5a7cb8", "#a8a0a8", "#ffe2c0", sun_el=8.0, sun_int=0.7,
              mist=0.55, mist_color="#ffe8d8", haze=0.8, rays=0.4),
    radiance=_L("#1a5ccc", "#559ee8", "#ffe8b0", "#fff0cc", "#3a78d0", "#88a8a0", "#fff0b0", sun_el=9.0,
                sun_int=1.1, sun_glow=0.4, rays=0.7),
    gold=_L("#24529e", "#86aed8", "#ffc47a", "#ffcf96", "#36589a", "#7c7480", "#ffc878", sun_el=7.0, sun_int=0.8,
            sun_glow=0.35, rays=0.45, mist=0.25, mist_color="#ffd8a8", exposure=0.92),
)
LOOK_KEYS = [(0.0, "first_light"), (S2, "sapphire", 0.8), (S3, "pearl", 0.8), (TOUCH + 0.2, "blush", 1.2),
             (GUST2, "azure", 0.8), (S5, "clay", 0.8), (S6, "gale", 0.6), (S7, "breath", 1.4), (BIG, "radiance", 0.4),
             (HOME, "gold", 1.0), (PEAK - 0.6, "cream", 3.2)]


def _clear(t):
    """Keep-clear boxes of the 3D layer: the badge (while it shows) and the end card."""
    out = []
    box, a = badge_box(t)
    if a > 0.01:
        out.append(dict(box=box, t0=-10.0, t1=TOTAL + 10.0, soft=0.03, amount=min(1.0, 1.1 * a)))
    if t >= PEAK - 0.5:
        out.append(dict(box=(0.08, 0.40, 0.92, 0.86), t0=PEAK, t1=TOTAL + 1.0, soft=0.06, amount=0.92))
    return out


P3D = dict(
    camera=CAMERA,
    world=dict(
        looks=LOOKS,
        look=LOOK_KEYS,
        light=dict(pos=tuple(M(2.6, 0.25, 2.0)), color="#ffe6b0", size=0.7, rays=1.0,
                   strength=lambda t: float(K._ss(HOME + 0.6, 47.8, t) * (1.0 - K._ss(S8 + 0.6, S8 + 1.6, t))) * 0.3),
        react=dict(beat=0.3, level=0.25),
    ),
    bursts=[dict(t=TOUCH, strength=0.3, at=None, radius=0.18, color="#fff0f4", rise=0.15, fall=0.6),
            dict(t=PEAK, strength=0.35, radius=0.3, color="#fff8ee", rise=0.15, fall=0.8)],
    clear=lambda t: _clear(t),
    setup=_setup,
)
