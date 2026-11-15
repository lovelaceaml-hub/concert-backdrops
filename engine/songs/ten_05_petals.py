"""PETALS: film 05 of the concert promos for the Healing Concert "The Words of Mother's Love" (60 s).

A kind word is a petal: you cannot keep it, only open your hand. The wind takes it, and wherever it lands
someone blossoms. The camera rides one gust of petals through a spring water meadow, from person to person,
nine words acted out by nine kinds of people, home to a great tree of light whose nine boughs bloom in the
nine colours; the tree lets go and the end card holds.

Audio: audio/promo/concert-medley.mp3 (sections 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 with the breath
to 42.51, 49.47; the loudest moment about 54.3; the final hit 58.11). Every section start is a gust: the
petals in the air surge and the camera is thrown to the next place. Each section has its own light.

THE ACTING PLAN (who acts each expression, how, in which style and framing; UPDATE 6)
 Greeting       0 to 6.8   A young woman in close profile, her silhouette a window onto a sunrise (p07), blows
                           petals from her open palm (ref 14) under the opening title. The petals cross the water
                           to a man of gold glitter (p08) who stands with his back to her; touched by them he
                           TURNS and WAVES across the distance. Extreme close-up, then a full figure.
 Gratitude      6.8 to 13  Straight down on the lake: the thanks float on the water, and a ring of small people of
                           light round it BOW together (many, far: a crowd seen from above).
 Apology        13 to 19.8 A man drawn as a constellation (p01) stands with his HEAD BOWED and his OPEN HANDS LOW;
                           the petals fall from them into the words. She has her back to him; she turns.
 Inclusiveness  18.2 to 23 She walks into his arms: an EMBRACE that BLOOMS (a front of blossom runs out from where
                           they hold each other and both become blossom), and the bare tree over them bursts
                           into flower. Half figures, then blown back to the whole tree.
 Concession     23 to 27   A woman whose silhouette is a window onto the stars (p02) STEPS ASIDE onto the water
                           with an OPEN PALM toward a path of petals; butterflies leave her; a man of gold walks
                           on along the path toward the far tree.
 Respect        27 to 33   Two people SEATED under a small white tree, one speaking with open hands, the other
                           LEANING IN to listen, his profile outlined in sparks (p06); the lens opens until the
                           world melts round them. Half figures in profile.
 Encouragement  33 to 38   The gale: a barrel roll down to a woman KNEELING IN PRAYER under falling blossom, her
                           prayer rising as embers (p03, p08); a friend drawn as a constellation stands with a
                           HAND ON HER SHOULDER. Half figures, close.
 (the breath)   40 to 42.5 The camera rises over the whole meadow: "December 6" written in light across the sky,
                           bursting on the biggest hit.
 Consideration  42.5 to 46 An elder kneeling on the water, drawn as a constellation, is HELPED UP by a young woman
                           of gold: she reaches down, takes his hand and pulls him to his feet; light runs from
                           the clasp through him.
 Compliment     46 to 49.5 A girl TWIRLS and throws petals into the air, dispersing into them like embers (p04),
                           while a few people round her APPLAUD.
 (home)         49.5 to 60 Heavenly Mother, only from behind and veiled, at the foot of the great tree, opens her
                           arms and turns to petals that rise into the boughs; the camera climbs as the nine
                           boughs bloom in the nine colours; a crowd under the tree raises its arms; the tree lets
                           go on the loudest moment and the end card holds from 55.4 s to the last frame.

TITLE AND DATE (UPDATE 7, drawn by the engine's TITLES once it lands): the opening lockup over the sunrise sky
(0 to 3 s), the signature in two calm stretches, "December 6" in light in the breath; the end card as before.

House rules kept: Heavenly Mother only from behind; artistic faces only (profiles of light, never photographic);
everyone clothed in garments of light; the nine expressions in their exact wording from words.EXPRESSIONS, each
read for 2.5 s or more, one at a time; on bright skies the words are painted in a deep shade of their colour,
on deep skies they are light; nothing dark behind text; no words mirrored in the water; no lyrics; no em or en
dash; no fade to black.
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
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0     # no corner badge (UPDATE 7)
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402
from track import Track  # noqa: E402
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
WHIP1 = 2.50                      # a measured hit: the camera follows the petals to the man
TOUCH = 18.20                     # a measured hit: the embrace
GUST2 = 22.75                     # on to the path of petals
WIDE = 37.60                      # the gale calms: up over the whole meadow
HELP = 43.00                      # the elder rises (pairs.helped_up), on the heels of the biggest hit
TWIRL = 46.20                     # the girl begins to twirl
CLIMB = 51.30                     # the climb past the nine boughs

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

# ---- title and date (UPDATE 7; drawn by the engine's TITLES when it lands on engine-p3d-words). This film is
# bright day: navy with gold accents, except the signature over the violet gale.
TITLES = dict(
    opening=dict(t_end=3.0, y=0.20, palette="day"),
    signature=dict(windows=[(32.35, 33.45, "tr", "day"), (38.55, 40.05, "br", "night")]),
    date_light=dict(t_form=S7, t_burst=BIG, y=0.30, palette="day"),
)


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
A = St(6.0, 46.0, 165.0)          # the giver in close profile, the low sun just off the left of the picture
B = np.array([22.0, 0.0, 40.0])   # the lake page (Gratitude, from straight above)
C = St(34.0, 26.0, 20.0)          # the apology and the embrace, under a small tree
D = St(44.0, 8.0, 20.0)           # the path of petals
E = St(26.0, -24.0, 130.0)        # two seated under a small white tree
F = St(6.0, -40.0, 280.0)         # the prayer in the gale
G = St(-32.0, -14.0, 150.0)       # the elder helped up; the girl who twirls
M = St(0.0, 9.5, 180.0)           # Heavenly Mother at the foot of the tree, facing it (from behind only)


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


# the camera's roll: a bank on the whips, a spin in the dive, a full barrel roll into the gale
ROLL = _smooth_keys([(0.0, 0.0), (WHIP1, 0.0), (2.9, -8.0), (3.4, 0.0),
                     (S2, 0.0), (7.7, 12.0), (8.9, 0.0),
                     (S3, 0.0), (13.85, -36.0), (14.5, -6.0), (15.0, 0.0),
                     (S4 - 0.05, 0.0), (S4 + 0.5, 4.0), (21.0, 0.0),
                     (GUST2, 0.0), (23.2, -9.0), (23.8, 0.0),
                     (S5, 0.0), (27.4, 10.0), (28.1, 0.0),
                     (S6, 0.0), (34.3, 360.0), (WIDE, 360.0), (BIG, 360.0), (42.95, 352.0), (43.4, 360.0),
                     (TWIRL - 0.4, 360.0), (S8, 360.0), (49.85, 346.0), (50.3, 360.0), (TOTAL, 360.0)])


def _moves(focus):
    """The camera, as one list of moves."""
    a0 = (A(-1.9, -0.05, 1.45), A(0.0, -0.25, 1.64))    # the close profile (frame 0)
    a1 = (A(-4.6, 8.6, 1.15), A(1.0, 12.4, 2.35))       # the Greeting
    b0 = (B + np.array([0.0, 9.6, 3.0]), B + np.array([0.0, 0.0, 0.6]))
    b1 = (B + np.array([0.7, 11.0, 2.6]), B + np.array([0.4, 0.0, 0.3]))
    c0 = (C(-5.6, -0.3, 1.45), C(0.0, 0.0, 1.62))       # half figures
    d0 = (D(-8.2, -0.6, 1.25), D(2.6, 0.0, 1.95))
    e0 = (E(-1.75, 0.0, 1.62), E(0.0, 0.0, 1.56))       # two faces in profile, close
    f0 = (F(-4.0, -0.7, 1.05), F(0.0, 0.0, 1.25))       # the prayer, close
    w0 = (F(-16.0, 3.0, 9.0), F(22.0, 0.0, 7.5))        # high over the meadow
    w1 = (F(-17.0, 4.0, 9.6), F(22.0, 2.0, 12.5))       # the breath: up into the sky
    g0 = (G(-5.0, -0.3, 1.25), G(0.0, 0.0, 1.15))       # the elder helped up
    g1 = (G(-4.6, 3.2, 0.85), G(1.0, 3.6, 1.75))        # the girl who twirls, low
    m0 = (M(-2.5, 0.45, 1.5), M(0.0, 0.0, 1.8))
    return [
        # 1. close profile under the title; the camera follows the petals to the man who turns and waves
        hold(a0[0], a0[1], -1.0, WHIP1, drift=(0.06, 0.0, 0.0), fov=30, aperture=0.035),
        fly([(WHIP1, a0[0] + np.array([0.06, 0.0, 0.0]) * 3.5, a0[1]), (2.95, A(-3.0, 4.5, 1.25), A(0.6, 8.0, 1.9)),
             (3.4, *a1)], fov=(30, 42), aperture=0.02, blend=0.3),
        hold(a1[0], a1[1], 3.4, S2, drift=(0.22, 0.03, -0.08), fov=42, aperture=0.05, blend=0.6),
        # 2. thrown up and over: straight down on the lake page
        fly([(S2, a1[0] + np.array([0.22, 0.03, -0.08]) * 3.4, a1[1]),
             (7.7, B + np.array([-4.0, 6.5, 7.5]), B + np.array([0.0, 0.0, -1.0])), (9.0, *b0)],
            fov=(44, 50), aperture=0.01, blend=0.35),
        dolly(b0[0], b1[0], 9.0, S3, look=(b0[1], b1[1]), fov=50, aperture=0.0, blend=0.8),
        # 3. a spinning dive to the two under the bare tree; push in on the embrace; blown back by the blossom
        fly([(S3, b1[0], b1[1]), (14.0, C(-3.5, 2.5, 4.5), C(0.0, 0.0, 1.0)), (14.8, *c0)],
            fov=(50, 36), aperture=0.02, blend=0.35),
        hold(c0[0], c0[1], 14.8, 17.6, drift=_d(C.view) * 0.15, fov=36, aperture=0.05, blend=0.6),
        dolly(C(-5.2, -0.25, 1.45), C(-3.9, -0.1, 1.4), 17.6, S4, look=(C(0.0, 0.0, 1.62), C(0.0, 0.0, 1.45)),
              fov=(36, 32), aperture=0.05, ease="smooth", blend=0.6),
        dolly(C(-4.2, 0.0, 1.1), C(-7.2, 0.4, 0.75), S4, GUST2, look=C(0.7, 0.0, 2.85),
              fov=36, aperture=0.05, ease="out", blend=0.3),
        # 4. on to the path of petals
        fly([(GUST2, C(-7.2, 0.4, 0.75), C(0.7, 0.0, 2.85)), (23.2, D(-12.0, -4.0, 2.6), D(0.0, 0.0, 1.6)),
             (23.8, *d0)], fov=(40, 40), aperture=0.02, blend=0.35),
        dolly(d0[0], D(-6.0, -0.2, 1.3), 23.8, S5, look=(d0[1], D(3.0, 0.0, 1.9)), fov=40, aperture=0.04,
              blend=0.6),
        # 5. two seated under the white tree: the lens opens round them
        fly([(S5, D(-6.0, -0.2, 1.3), D(3.0, 0.0, 1.9)), (27.4, E(-7.0, 2.0, 2.4), E(0.0, 0.0, 1.5)),
             (28.1, *e0)], fov=(42, 34), aperture=0.02, blend=0.35),
        hold(e0[0], e0[1], 28.1, S6, drift=_d(E.view) * 0.03, fov=34, focus=1.75,
             aperture=Track([(28.1, 0.04), (29.0, 0.05), (31.6, 0.20), (S6, 0.20)]), blend=0.6),
        # 6. the gale: a barrel roll down to the prayer; a slow turn round it; then up over the whole meadow
        fly([(S6, e0[0] + _d(E.view) * 0.16, e0[1]), (33.9, F(-9.0, 2.0, 4.0), F(0.0, 0.0, 1.2)), (34.4, *f0)],
            fov=(46, 36), aperture=0.02, blend=0.3),
        orbit(F(0.0, 0.0, 0.0), radius=4.05, height=(1.05, 1.15), a0=F.view + 180.0 - 10.0,
              a1=F.view + 180.0 + 14.0, t0=34.4, t1=WIDE, look=F(0.0, 0.0, 1.25), fov=36, aperture=0.04, blend=0.5),
        dolly(f0[0], w0[0], WIDE, S7, look=(f0[1], w0[1]), fov=(36, 48), aperture=0.0, ease="smooth", blend=0.5),
        # the breath: hang over the meadow and look up into the sky, where the date is written
        dolly(w0[0], w1[0], S7, BIG, look=(w0[1], w1[1]), fov=48, aperture=0.0, ease="smooth", blend=0.6),
        # 7. the biggest hit: down to the elder who is helped up; then low beside the girl who twirls
        fly([(BIG, w1[0], w1[1]), (42.95, G(-11.0, -2.0, 4.0), G(0.0, 0.0, 1.0)), (43.4, *g0)],
            fov=(48, 38), aperture=0.02, blend=0.25),
        hold(g0[0], g0[1], 43.4, 45.9, drift=_d(G.view) * 0.1, fov=38, aperture=0.05, blend=0.5),
        dolly(G(-5.0, 1.2, 1.1), g1[0], 45.9, S8, look=(G(0.3, 1.8, 1.4), g1[1]), fov=(38, 42), aperture=0.04,
              ease="out", blend=0.6),
        # 8. home: the great gust round the tree to Heavenly Mother, from behind
        fly([(S8, g1[0], g1[1]), (49.9, np.array([-12.0, 2.4, 10.0]), np.array([0.0, 3.0, 12.0])), (50.4, *m0)],
            fov=(52, 34), aperture=0.02, blend=0.3),
        hold(m0[0], m0[1], 50.4, CLIMB, drift=(0.05, 0.08, 0.15), fov=34, aperture=0.04, blend=0.5),
        # 9. the climb: a rising revolve that shows the whole tree as its boughs bloom one by one
        orbit((0.0, 7.0, 0.0), radius=(16.0, 20.0), height=(2.2, 12.0), a0=4.0, a1=96.0, t0=CLIMB, t1=PEAK,
              look=lambda t: (0.0, 5.0 + 1.6 * (t - CLIMB), 0.0), fov=54, aperture=0.02, blend=0.8),
        # 10. the tree lets go; pull back over the lake to the end card
        fly([(PEAK, np.array([0.0, 12.0, 0.0]) + _d(96.0) * 20.0, np.array([0.0, 9.8, 0.0])),
             (55.4, _d(104.0) * 28.0 + np.array([0.0, 7.0, 0.0]), np.array([0.0, 16.0, 0.0])),
             (56.7, _d(110.0) * 38.0 + np.array([0.0, 3.6, 0.0]), np.array([0.0, 20.5, 0.0])),
             (TOTAL + 0.5, _d(108.0) * 41.5 + np.array([0.0, 3.2, 0.0]), np.array([0.0, 21.0, 0.0]))],
            fov=46, aperture=0.0, blend=0.4),
    ]


def _rig(focus="target"):
    return Rig(_moves(focus), roll=ROLL, handheld=0.22, shutter=0.35, min_height=0.3, focus=focus)


_LAYOUT = _rig()


# ---------------------------------------------------------------------------------------------------------
# The words: laid out by where they are read in the picture (the screen place of the block's centre, its
# depth and the pixels of one em at 1080p, at the middle of the reading moment). On a bright sky a word is
# painted in a deep shade of its own colour; on a deep sky (the lake from above, the azure, the gale) it is light.
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


WIND = Wind(base=(2.0, 0.25, -0.6), gusts=[(t, 3.2, 1.4) for t in (HIT0, WHIP1, S2, S3, S4, GUST2, S5, S6, BIG,
                                                                      S8, PEAK)], sway=0.3, seed=2.0)

_GRAT_EM = PW.em_for(_LAYOUT, 10.5, 10.4, 90)        # flat on the lake page, read from the +z side

INK = dict(Greeting="#c23e28", Apology="#a8500e", Inclusiveness="#b0225f", Respect="#8a452f",
           Consideration="#a3203f", Compliment="#6a3fc0")

_SPECS = [
    _w("Greeting", 0.52, 0.62, 7.0, 104, 1.5, 3.5, 6.3, 7.1, arrive="petals",
       source=lambda t: BODIES["giver"].where(t, "lips") if "giver" in BODIES else np.zeros(3),
       leave="petals", wind=(1.0, 0.35, -0.2), paint=INK["Greeting"]),
    dict(expr="Gratitude", pos=(float(B[0]), 0.04, float(B[2])), em=_GRAT_EM, face="flat", facing=0.0,
         t_in=7.6, t_read0=9.0, t_read1=11.9, t_out=12.7, arrive="petals",
         source=(float(B[0]), 2.0, float(B[2]) + 4.5), leave="petals", wind=(0.8, 0.9, -0.3)),
    _w("Apology", 0.46, 0.57, 6.4, 92, 14.4, 15.4, 18.1, 18.2, arrive="petals", source=_palm("friend_m", "R"),
       leave="morph", paint=INK["Apology"]),
    _w("Inclusiveness", 0.44, 0.58, 7.8, 100, TOUCH, S4 + 0.25, GUST2, 23.5, arrive="morph", source="Apology",
       leave="petals", wind=(1.0, 0.4, -0.3), paint=INK["Inclusiveness"]),
    _w("Concession", 0.52, 0.63, 9.5, 104, 23.3, 24.2, S5 - 0.07, 27.5, arrive="petals",
       source=_palm("yielder", "R"), leave="wind", wind=(1.0, 0.2, -0.4)),
    _w("Respect", 0.52, 0.70, 3.6, 92, 28.0, 29.0, 31.7, 32.3, arrive="palm", source=_palm("speaker", "R"),
       leave="petals", wind=(1.0, 0.5, -0.2), paint=INK["Respect"]),
    _w("Encouragement", 0.52, 0.66, 6.2, 92, 33.7, 34.6, 37.4, 38.2, arrive="petals",
       source=lambda t: F(0.0, 0.0, 6.0), leave="petals", wind=(-0.4, 0.9, 0.2)),
    _w("Consideration", 0.53, 0.63, 6.4, 102, 42.6, 43.5, 45.9, 46.0, arrive="palm", source=_palm("helper", "R"),
       leave="morph", paint=INK["Consideration"]),
    _w("Compliment", 0.55, 0.64, 6.6, 104, 46.0, 46.8, 49.3, 50.1, arrive="morph", source="Consideration",
       leave="petals", wind=(-0.6, 0.8, 0.5), paint=INK["Compliment"]),
]
WORDS = PW.Words(_SPECS, face="camera", camera=_LAYOUT, tint=0.6, bright=1.25)

_FOCUS_DEFAULT = lambda t: _LAYOUT.state(t).target       # noqa: E731
CAMERA = _rig(focus=lambda t: WORDS.focus_point(t, _FOCUS_DEFAULT))

# ---------------------------------------------------------------------------------------------------------
# The great tree: nine boughs that bloom in the nine colours as the camera climbs past them; each word buds
# its bough when it leaves
# ---------------------------------------------------------------------------------------------------------
_COL9 = [e["color"] for e in PW.EXPRESSIONS]
_BLOOM = [CLIMB + 0.15 + 0.32 * i for i in range(9)]
_BOUGH_AZ = [4.0 + 92.0 * (b - CLIMB) / (PEAK - CLIMB) + 22.0 for b in _BLOOM]
_BUD = [WORDS[e["label"]].t_read1 for e in PW.EXPRESSIONS]


def _setup(scene):
    from p3d import pairs
    from p3d import styles as ST
    from p3d.body import Body
    from p3d.crowd import Crowd
    from p3d.stylekit import Dressed
    w = WIND
    shed = dict(kind="shed", sprite="petal", n=1400, life=2.6, speed=0.5, size=7.0, rise=0.12, turb=0.4)

    def wrap(name, fill=None):
        """The named set again, its shed petals painted and kept out of the words being read (and, with fill, a
        coat of colour under its light)."""
        e = scene._entries[name]
        scene.add(name, K.Painted(e.pointset, fill=fill, fill_alpha=0.26, words=WORDS), mask=e.mask,
                  reflect=e.reflect, depth_of_field=e.depth_of_field)

    def style(name, preset, sky, **kw):
        if preset not in ("glitter_profile", "constellation_profile", "nebula_profile", "spark_profile"):
            kw["effects"] = list(kw.get("effects", [])) + [dict(shed)]
            kw.setdefault("wind", w)
            # keys over time go to the body itself; the preset gets a plain value for its own sums
            body = dict(kw.pop("body", None) or {})
            if isinstance(kw.get("facing"), list):
                body["facing"] = kw["facing"]
                kw["facing"] = kw["facing"][-1][1]
            if isinstance(kw.get("at"), list):
                body["at"] = kw["at"]
                kw["at"] = kw["at"][0][1]
            if body:
                kw["body"] = body
        if preset == "gold_glitter":
            kw.setdefault("t", 1e6)                 # whole: no blowing apart unless asked
        st = ST.add(scene, preset, name=name, sky=sky, **kw)
        BODIES[name] = st.main
        wrap(name)
        return st

    def pair_body(name, b, paint=0.85, light=1.0, fill=None):
        BODIES[name] = b
        scene.add(name, K.Painted(Dressed(b, paint=paint, paint_light=light), fill=fill, fill_alpha=0.22,
                                  words=WORDS), mask=None)
        return b

    # ---- 1. Greeting: a young woman's face in close profile, gold glitter (p08), breathes a stream of petals
    # across the water to a man of gold who has his back to her; touched by them he turns and waves
    head = A(0.0, -0.05, 1.50)
    style("giver", "glitter_profile", "day", shape="woman", at=tuple(head), facing=az_of(-_r(A.view)),
          height=0.30, show=(-1.0, 3.4), tilt=lambda t: 6.0 + 4.0 * float(K._ss(-0.5, 0.6, t)))
    man = PW.place(_LAYOUT, 4.9, 0.30, 0.42, 7.4)
    toward = az_of(_d(A.view) * -1.0 + _r(A.view) * 1.4)
    style("stranger", "gold_glitter", "day", shape="man", at=(man[0], man[2]),
          facing=[(0.0, toward + 160.0), (2.9, toward + 160.0), (3.7, toward)], garment="coat",
          gesture=[(3.5, 6.6, "wave", dict(side="R"))], show=(1.6, 7.4))
    # ---- 2. Gratitude: a ring of people round the thanks on the water, bowing together (from above)
    scene.add("bowing", Crowd(n=22, area=dict(center=(B[0], B[2] + 0.3), radius=(4.0, 5.2), arc=(-62.0, 62.0)),
                              facing="center", kinds=("bow",), start=dict(t=7.6, dur=1.0), until=12.9, points=6000,
                              color="#ffd98a", color2="#fff6e0", bright=1.6, seed=3.0))
    # ---- 3. Apology and Inclusiveness: a man drawn as a constellation in navy and gold, head bowed and hands
    # open low; she turns, walks into his arms, and the embrace blooms into blossom
    meet = C(0.0, 0.0, 0.0)
    ax = _r(C.view)                                    # their axis runs across the picture
    bloom = dict(bloom=dict(t=TOUCH + 0.1, at="chest", speed=1.1, width=0.35, flash=2.0))
    she, he = pairs.embrace(
        TOUCH, at=(meet[0], meet[2]), facing=az_of(ax), approach=1.1,
        a=dict(shape="woman", garment="dress", hair=True, color="#d86a90", color2="#ffd8e6", wind=w, fade=0.7,
               points=60000, bright=1.3, show=(S3, 24.0), sweeps=bloom,
               facing=[(0.0, az_of(ax) + 180.0), (16.6, az_of(ax) + 180.0), (17.1, az_of(ax))],
               look=[dict(name="glitter", before="bloom"), dict(name="glitter", after="bloom", color="#e85a90",
                                                                color2="#ffd0e2", bright=1.2)],
               effects=[dict(shed)]),
        b=dict(shape="man", garment="tunic", color="#22357e", color2="#c38a1e", wind=w, fade=0.7, points=64000,
               bright=1.1, show=(S3, 24.0), sweeps=bloom,
               look=[dict(name="plexus", before="bloom", detail=1.0, share=0.075, links=3, reach=0.10),
                     dict(name="glitter", after="bloom", color="#e05a8c", color2="#ffd0e2", bright=1.2)],
               gesture=[(13.0, 17.9, "bow", dict(amount=18.0)), (13.0, 17.9, "offer")], effects=[dict(shed)]))
    pair_body("friend_w", she, paint=0.85, fill="#e88aac")
    pair_body("friend_m", he, paint=1.0, light=0.6)
    scene.add("touch", Flare(lambda t: 0.5 * (she.where(t, "chest") + he.where(t, "chest")), TOUCH + 0.1,
                             color="#ffd0e0", color2="#fff6d8", strength=0.6))
    st = K.Tree(base=C(2.4, 6.3, 0.0), height=6.5, boughs=6, colors=("#F582AF", "#FFD0E0", "#ffffff"),
                bloom=[TOUCH + 0.12 * i for i in range(6)], crown_t=TOUCH + 0.1,
                crown_colors=("#ffffff", "#FFC4DA", "#F582AF"), n_bloom=1500, n_crown=7000, n_bark=9000, seed=12,
                bloom_glow=0.16, petal_light=0.1)
    scene.add("small_tree", st)
    scene.add("small_tree_glow", st.glow_set())
    # ---- 4. Concession: a starry silhouette with long hair (p02) steps aside with an open palm toward a path
    # of petals, butterflies leaving her; a man of gold walks on along the path
    p0, p1 = D(0.2, -0.2, 0.0), D(0.2, -1.3, 0.0)
    scene.add("path", K.PetalPath(D(0.3, 0.1, 0.0), _d(D.view), length=34.0, width=1.2, t0=GUST2 - 0.2, dur=1.6))
    style("yielder", "butterflies", "day", shape="woman", at=[(23.6, (p0[0], p0[2])), (24.4, (p1[0], p1[2]))],
          motion=[(0.0, "stand"), (23.6, "shuffle"), (24.5, "stand")],
          facing=[(0.0, az_of(-_d(D.view))), (23.6, az_of(-_d(D.view))), (24.4, az_of(_r(D.view)))],
          garment="robe", gesture=[(23.9, 27.4, "offer")], show=(GUST2 - 0.2, 27.6), t=24.4)
    q0 = D(-1.6, 0.6, 0.0)
    style("passer", "gold_glitter", "day", shape="man", at=(q0[0], q0[2]),
          facing=az_of(_d(D.view) + _r(D.view) * 0.05), motion=[(0.0, "stand"), (24.6, "walk", dict(speed=1.1))],
          garment="tunic", show=(GUST2 - 0.2, 27.6))
    # ---- 5. Respect: two faces in profile, close: she speaks (gold glitter), he leans in to listen (a
    # constellation in navy and gold); a small white tree behind them
    hs, hl = E(0.0, -0.36, 1.45), E(0.0, 0.36, 1.45)
    style("speaker", "glitter_profile", "day", shape="woman", at=tuple(hs), facing=az_of(hl - hs), height=0.30,
          show=(S5 - 0.3, 33.6), tilt=lambda t: 4.0 + 2.0 * np.sin(1.7 * t))
    style("listener", "constellation_profile", "day", shape="man", at=tuple(hl), facing=az_of(hs - hl), height=0.31,
          show=(S5 - 0.3, 33.6), tilt=lambda t: -2.0 - 8.0 * float(K._ss(28.2, 29.6, t)))
    wt = K.Tree(base=E(3.4, 3.4, 0.0), height=5.6, boughs=5, colors=("#ffffff", "#FFE9D6", "#FFD9E4"),
                bloom=[-5.0] * 5, crown_t=-5.0, crown_colors=("#ffffff", "#FFF3E6", "#FFE1EA"), n_bloom=1300,
                n_crown=6000, n_bark=8000, seed=14, bloom_glow=0.08, petal_light=0.08)
    scene.add("white_tree", wt)
    scene.add("white_tree_glow", wt.glow_set(lambda t: 1.0 if S5 - 1.0 < t < S6 + 0.5 else 0.0))
    # ---- 6. Encouragement: kneeling in prayer under falling blossom, her prayer rising as embers (gold
    # glitter); a friend drawn as a constellation with a hand on her shoulder (the gale: night palettes)
    kp, fp = F(0.0, -0.25, 0.0), F(0.55, 0.55, 0.0)
    kneel = style("kneeler", "gold_glitter", "night", shape="woman", at=(kp[0], kp[2]), facing=az_of(-_r(F.view)),
                  garment="robe", motion=[(0.0, "kneel", dict(hands="pray", dur=0.01))], show=(S6 - 0.3, 38.6),
                  effects=[dict(kind="shed", sprite="flake", n=2200, life=2.8, speed=0.15, rise=0.7, turb=0.3,
                                where="top", color="#ffb04a", size=2.5)]).main
    style("friend", "constellation", "night", shape="man", at=(fp[0], fp[2]), facing=az_of(kp - fp), garment="coat",
          show=(S6 - 0.3, 38.6),
          gesture=[(33.6, 38.6, "hand_on_shoulder", dict(side="R", to=lambda t: kneel.where(t, "shoulder.R", raw=True)))])
    scene.add("rain", K.Rain(F(0.0, 0.0, 0.0), S6, 38.4, radius=4.5, top=6.5))
    # ---- 7. Consideration: an elder drawn as a constellation, kneeling, is helped up by a young woman of gold;
    # light runs from the clasp through him and he turns to gold
    help_at = G(0.0, 0.0, 0.0)
    warm = dict(warm=dict(t=HELP - 0.6, at="palm.R", speed=1.1, width=0.3, flash=2.0))
    helper, elder = pairs.helped_up(
        HELP, at=(help_at[0], help_at[2]), facing=az_of(_r(G.view)), rise=1.7,
        a=dict(shape="woman", garment="robe", look="glitter", color="#c8783a", color2="#ffe2b8", wind=w, fade=0.7,
               points=60000, bright=1.2, show=(41.4, S8 + 0.4), effects=[dict(shed)]),
        b=dict(shape="man", garment="coat", stoop=0.3, color="#22357e", color2="#c38a1e", wind=w, fade=0.7,
               points=64000, bright=1.1, show=(41.4, S8 + 0.4), sweeps=warm,
               look=[dict(name="plexus", before="warm", detail=1.0, share=0.075, links=3, reach=0.10),
                     dict(name="glitter", after="warm", color="#c8843a", color2="#ffe2b8", bright=1.2)],
               effects=[dict(shed)]))
    pair_body("helper", helper, paint=0.85, fill="#e0a070")
    pair_body("elder", elder, paint=1.0, light=0.7)
    # ---- 8. Compliment: a girl twirls and throws petals into the air (p04); a few people applaud
    gp = G(1.0, 3.6, 0.0)
    style("dancer", "gold_glitter", "day", shape="woman", at=(gp[0], gp[2]), facing=az_of(-_r(G.view)),
          garment="dress", motion=[(0.0, "stand"), (TWIRL, "twirl")], color="#d8603a", color2="#ffd2b0",
          show=(45.2, S8 + 0.5), t=TWIRL + 0.6, dur=2.6, share=0.3,
          effects=[dict(kind="petals", t=TWIRL + 0.5, dur=2.4, share=0.35, color="#ff5a4a", color2="#ffc0a8")])
    scene.add("applause", Crowd(n=9, area=dict(center=(gp[0], gp[2]), radius=(3.4, 5.0),
                                               arc=(G.view - 60.0, G.view + 60.0)),
                                facing="center", kinds=("clap",), start=dict(t=45.6, dur=0.8), until=S8 + 0.3,
                                points=9000, color="#ffd98a", color2="#fff6e0", bright=1.5, seed=5.0))
    # ---- 9. Heavenly Mother, only from behind, at the foot of the tree; she opens her arms and turns to petals
    mother = Body("woman", at=(M.c[0], M.c[2]), facing=180.0, garment="robe", veil=dict(length=1.5, wide=1.1),
                  look="glitter", color="#d8a050", color2="#fff2d8", gesture=[(49.9, 53.0, "open_arms", dict(lift=0.35))],
                  show=(S8 - 0.3, 52.4), bright=1.4, points=80000, wind=w, fade=0.7,
                  effects=[dict(kind="petals", t=50.9, dur=1.4, color="#ffd0a0", color2="#fff4e0"), dict(shed)])
    pair_body("mother", mother, paint=0.7, light=1.0, fill="#f0c070")
    # ---- the world: the great tree, the crowd under it, the meadow, the petals in the air, the release
    tree = K.Tree(colors=_COL9, bough_az=_BOUGH_AZ, bud=_BUD, bloom=_BLOOM, crown_t=PEAK - 0.4,
                  crown_colors=tuple(_COL9) + ("#ffffff", "#ffffff", "#FFE9D6"))
    scene.add("tree", tree)

    def tree_glow(t):
        d = float(np.linalg.norm(CAMERA.state(t).pos - np.array([0.0, 8.0, 0.0])))
        return float(np.clip((40.0 - d) / 20.0, 0.0, 1.0))
    scene.add("tree_glow", tree.glow_set(tree_glow))
    scene.add("crowd", Crowd(n=64, area=dict(center=(0.0, 0.0), radius=(11.0, 16.0)), facing="center",
                             kinds=("raise", "open", "stand"), start=dict(t=CLIMB, center=(0.0, 0.0), speed=7.0),
                             points=5000, color="#ffe2a0", color2="#fff6e6", bright=1.5, seed=7.0))
    scene.add("meadow", K.Meadow())
    scene.add("wind_petals", PW.KeepClear(K.PetalWind(WIND, n=9000, amount=lambda t: min(
        1.0, 0.8 * PETAL_AMOUNT(t) + 0.12 * WIND.gust(t))), WORDS))
    scene.add("palm_stream", K.Stream(lambda t: BODIES["giver"].where(t, "lips"), lambda t: WORDS["Greeting"].centre(t),
                                      -1.5, 2.6,
                                      wind=WIND, n=1600, flight=1.2, arc=0.4))
    scene.add("release", K.Release(tree.bloom_pts, PEAK, WIND, _COL9 + ["#ffffff", "#FFE9D6"]))
    K.paint_word_petals(WORDS)
    WORDS.add_to(scene, reflect=False)          # no words mirrored in the water
    _gate_masks(scene)
    WORDS.check(CAMERA)


def _gate_masks(scene):
    """A frame holds two sky fills (windows, flat paint): every mask is switched off outside the time its set
    is on screen, so the fills of sets that are not there never take a layer."""
    for e in scene.entries():
        if e.mask is None:
            continue
        win = None
        if e.name.startswith("word "):
            w = WORDS[e.name[5:].replace(" light", "")]
            nxt = getattr(w.to, "t_in", None) if w.leave == "morph" else None
            win = (w.t_in - 0.3, (nxt if nxt is not None else w.t_out) + 0.3)
        else:
            sh = getattr(e.pointset, "show", None)
            if sh:
                win = (sh[0] - 0.2, sh[1] + 0.2)
        if win is not None:
            base = e.mask.strength
            e.mask.strength = (lambda t, b=base, a=win[0], z=win[1]:
                               0.0 if (t < a or t > z) else (b(t) if callable(b) else float(b)))


PETAL_AMOUNT = Track([(0.0, 0.5), (S2, 0.6), (S4, 0.75), (S6, 0.9), (WIDE, 0.9), (S7, 0.45), (BIG, 1.0),
                      (TOTAL, 1.0)])


def _L(top, mid, hor, haze_c, water, hills, sun, **kw):
    """A look of this film (display colours: the picture shows them so)."""
    D_ = theme.display
    d = dict(base="day", sky_top=D_(top) * 0.92, sky_mid=D_(mid) * 0.85, sky_hor=D_(hor) * 0.64,
             haze_color=D_(haze_c) * 0.5, water=D_(water) * 0.45, hill_color=D_(hills) * 0.5, sun_color=D_(sun) * 0.32,
             sun_az=SUN_AZ, sun_el=14.0, sun_int=0.95, rays=0.3, clouds=0.2, haze=0.5, mist=0.15,
             dust=0.5, dust_color="#fff4e0", dust_color2="#ffd2b8", sun_disc=3.0, sun_glow=0.35)
    if "mist_color" in kw:
        kw["mist_color"] = D_(kw["mist_color"]) * 0.55
    d.update(kw)
    return d


# one look per section: the light changes with every song of the medley. Bright skies carry painted words,
# deep ones (the lake from above, the azure, the gale) light words.
LOOKS = dict(
    dawn=_L("#a8cdf0", "#ffe6cc", "#ffd4a0", "#ffe2c4", "#7aa6d8", "#c9a99a", "#ffd08a", sun_el=5.0, sun_int=1.0,
            sun_glow=0.45, rays=0.5, clouds=0.15, mist=0.25, mist_color="#ffe8cc"),
    sapphire=_L("#1d54c0", "#5b9be6", "#e8f2fa", "#e4eef6", "#1a4aa8", "#5f86b0", "#fff6e6", sun_el=24.0,
                sun_int=0.9, rays=0.2, clouds=0.25),
    pearl=_L("#a9bcd8", "#dfe4ec", "#f2ede8", "#e6e6e8", "#8aa2c4", "#9aa6b4", "#fff8f0", sun_int=0.55, rays=0.1,
             clouds=0.7, mist=0.3, mist_color="#eceef2"),
    blush=_L("#8cbcec", "#ffdce6", "#fff0ee", "#ffe8ec", "#7aa8dc", "#8fbf90", "#fff2ea", sun_int=0.9, rays=0.3),
    azure=_L("#1048b8", "#3f8ae2", "#d8ecfc", "#dcecf8", "#1550b8", "#5f9a72", "#ffffff", sun_el=30.0, sun_int=0.9,
             rays=0.15, clouds=0.15),
    ivory=_L("#9fc8ee", "#f8eadb", "#f4e0c8", "#f2e4d4", "#82acdc", "#a8b48c", "#fff0dc", sun_el=22.0),
    gale=_L("#2e2f86", "#6a62bc", "#e2cdec", "#d8c8e8", "#2a2f78", "#4e4a80", "#f8f0ff", sun_int=0.7, rays=0.25,
            clouds=0.85, cloud_speed=6.0, mist=0.25, mist_color="#c8b8e8"),
    breath=_L("#b8cfee", "#ffe2d2", "#ffd8c2", "#ffe6d6", "#8eaedc", "#c0aab0", "#ffe2c0", sun_el=8.0, sun_int=0.7,
              mist=0.55, mist_color="#fff0e4", haze=0.8, rays=0.35),
    radiance=_L("#9cc8f2", "#fff0d6", "#ffe2a8", "#fff0cc", "#7eaee6", "#a8b89c", "#fff0b0", sun_el=9.0,
                sun_int=1.0, sun_glow=0.4, rays=0.6),
    gold=_L("#5a86c8", "#ffd8a8", "#ffc070", "#ffcf96", "#5a7cb0", "#9a8480", "#ffc878", sun_el=7.0, sun_int=0.8,
            sun_glow=0.35, rays=0.45, mist=0.25, mist_color="#ffd8a8", exposure=0.92),
)
LOOK_KEYS = [(0.0, "dawn"), (S2, "sapphire", 0.8), (S3, "pearl", 0.8), (TOUCH + 0.2, "blush", 1.2),
             (GUST2, "azure", 0.8), (S5, "ivory", 0.8), (S6, "gale", 0.6), (S7, "breath", 1.4), (BIG, "radiance", 0.4),
             (S8, "gold", 1.0), (PEAK - 0.6, "cream", 3.2)]


def _clear(t):
    """Keep-clear boxes of the 3D layer: the end card (and, when TITLES lands, the title and date)."""
    if t >= PEAK - 0.5:
        return [dict(box=(0.08, 0.40, 0.92, 0.86), t0=PEAK, t1=TOTAL + 1.0, soft=0.06, amount=0.92)]
    return []


P3D = dict(
    camera=CAMERA,
    world=dict(
        looks=LOOKS,
        look=LOOK_KEYS,
        light=dict(pos=tuple(M(2.6, 0.25, 2.0)), color="#ffe6b0", size=0.7, rays=1.0,
                   strength=lambda t: float(K._ss(S8 + 0.4, 50.6, t) * (1.0 - K._ss(CLIMB + 0.2, CLIMB + 1.2, t))) * 0.3),
        react=dict(beat=0.3, level=0.25),
    ),
    bursts=[dict(t=TOUCH + 0.1, strength=0.25, at=None, radius=0.16, color="#fff0f4", rise=0.15, fall=0.6),
            dict(t=PEAK, strength=0.3, radius=0.3, color="#fff8ee", rise=0.15, fall=0.8)],
    clear=_clear,
    setup=_setup,
)
