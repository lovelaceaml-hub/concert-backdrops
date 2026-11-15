"""Film 09 of ten: THE VEIL. A 60 second promo for the Healing Concert "The Words of Mother's Love".

We follow Heavenly Mother from behind as she walks over a night lake toward the first light. Her veil streams
back across the water as a river of light. Wherever it reaches, people rise out of it and say the nine Words
of Mother's Love to one another, until at sunrise she lifts her arms and the veil rises to become the sky and
the arch of nine lights, and the end card stands in the day.

World    one cloth: the veil is road, roof, river, loom and at last the sky (VeilRiver below, this file's own
         point set, about 170 thousand points and a warp of threads, mirrored in the lake).
Camera   always behind her (never more than 60 degrees off straight behind), riding the cloth; a hard cut on
         every song change, each one a new shape of the veil.
People   lifelike bodies of light (engine/p3d/body.py) in garments of light, gathered out of the river, in
         pairs, with real contact. Heavenly Mother only from behind, veiled, or her hand.
Words    the nine expressions (engine/p3d/words.py, never retyped), each read for 2.6 s or more.

Sections on the medley (audio/promo/concert-medley.mp3, section starts 0.25, 6.84, 13.30, 19.85, 26.79, 33.36,
40.21 with the breath to 42.51, 49.47; last hit 58.11):
 1  0.00  THE CAST      close behind her, rays round her head; on the first hit the veil unrolls across the
                        lake and we are swept back along it; two people rise out of it and clasp hands:
                        Greeting (written by the flare of their hands)
 2  6.84  THE ROAD      a fast low skim up the river; someone kneels, spent; another stoops to help:
                        Consideration (from the open palm)
 3  13.30 THE CANOPY    the veil heaves up into a roof of light over us; one sits coming apart, one kneels
                        beside her: Apology; the embrace mends her (every particle flies home): Inclusiveness
 4  19.85 THE RIVER     up through the roof, 30 m over the river of light; dive to the narrows where one
                        steps aside with an open palm for the other: Concession
 5  26.79 THE LOOM      the veil unwoven into a warp of strings; a barrel roll through it; two in profile,
                        one gives her thoughts as a stream from her palm, one listens: Respect (woven)
 6  33.36 THE PROCESSION  people walk in her veil behind her; one bows to another: Gratitude; the veil
                        narrows to one thread and we rush along it to her hand
 7  40.21 THE THREAD    the breath: her hand from behind holding the thread; a child walks the thread to her:
                        Encouragement; 42.51 the sun breaks the horizon ahead of her, the veil floods rose
                        gold; a half circle behind her and the child: Compliment (burnt out by the rays)
 8  49.47 THE LIFTING   she raises her arms; the whole veil lifts off the lake over our heads and becomes the
                        sky; the arch of nine lights stands; the end card, whole from 55.0 s to the last frame
No lyrics, no faces, no dark behind text, no fade to black, frame 0 is a picture.
"""
import numpy as np

import theme

import songs.s03_original as _base

# ------------------------------------------------------------------------------------------------ the frame
TOTAL = 60.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 59.6
_base.SONG_END = 60.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])       # frame 0 is a picture; no fade at the end
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:                                    # the flat expressions stay off: the words are particles
    _p["form"] = _p["hold"] = _p["star"] = 1e9

# the sections of the medley
S = (0.0, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47)
HIT0, BIG, LAST = 0.25, 42.51, 58.11

# the end card (the existing style: coral title with the ribbon, navy lines rising)
FORM_DUR = 2.4
TITLE_HIT = 54.30                       # the loudest moment of the medley: the title is whole
T_FORM = TITLE_HIT - FORM_DUR - 0.75    # 51.15
TAG_T0, TAG_T1 = 52.6, 55.0
_base.FORM_DUR = FORM_DUR
_base.TITLE_HIT = TITLE_HIT
_base.NINTH = 1e9
_base.TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
                   form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
_base.TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                          "6720 W Sahara Ave, Las Vegas",
                     sizes=(78, 77), t0=TAG_T0, t1=TAG_T1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
# the concert badge (Anthony: the concert title and the date from the beginning and throughout): large over
# the first image, settled into the top left corner by 2.8 s, gone as the end card forms
_base.CREDIT = dict(song="The Words of Mother’s Love",
                    concert="Healing Concert · Sunday, December 6 · 4:30 PM",
                    t_in=-1.0, t_full=0.0, t_move=1.6, t_rest=2.8, scale=0.52, alpha_rest=0.92,
                    margin_x=0.035, margin_top=0.05, y_first=0.765)


def credit_state(t, bbox):
    """Centre, scale and strength of the concert badge; bbox is its size at full card size."""
    c = CREDIT
    x0, x1, y0, y1 = bbox

    def sm(a, b, x):
        u = min(max((x - a) / (b - a), 0.0), 1.0)
        return u * u * (3 - 2 * u)

    a_in = sm(c["t_in"], c["t_full"], t)
    m = sm(c["t_move"], c["t_rest"], t)
    scale = c["scale"] ** m
    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    fx, fy = cx0, c["y_first"]                       # on the first image it stands in the sky above her
    tx = c["margin_x"] + c["scale"] * (x1 - x0) / 2.0
    ty = 1.0 - c["margin_top"] - c["scale"] * (y1 - y0) / 2.0
    cx, cy = fx * (1 - m) + tx * m, fy * (1 - m) + ty * m
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - sm(T_FORM, T_FORM + 1.0, t))
    # the card is drawn about (cx0, cy0); move it so that its centre lands on (cx, cy)
    return (cx, cy, scale, alpha), (cx0, cy0)


_base.credit_state = credit_state
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.actor import Actor  # noqa: E402
from p3d.camera import Move, Rig, fly, orbit  # noqa: E402

TOTAL = 60.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FRAGMENTS = []


def ss(a, b, x):
    """Smoothstep from a to b (works on arrays)."""
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _level(t):
    """The music's slow loudness 0..1 (0.6 when the analysis is not at hand)."""
    try:
        from audio_react import audio
        return float(audio.level(t))
    except Exception:
        return 0.6


def _beat(t):
    try:
        from audio_react import audio
        return float(audio.beat(t))
    except Exception:
        return 0.0


# ------------------------------------------------------------------------------------- Heavenly Mother's path
# She walks toward -z (toward the light on the horizon, azimuth 180) from z = 62, stops for the breath and
# stands to the end. The skeleton alone (numpy only) gives her place for the camera and the veil; the body in
# build() is made with the same settings, so it stands exactly there.
_WALK = dict(at=(0.0, 62.0), facing=180.0, seed=3.0,
             motion=[(0.0, "walk", dict(speed=0.78)), (38.4, "stand", dict(blend=1.4))])
_STAND = np.asarray(Actor("woman", **_WALK).where(41.0, "ground"), np.float64)   # where she stands still
HAND_AT = tuple(_STAND + np.array([-0.40, 0.80, 0.16]))    # her left hand, low and a little back, on the thread
MOTHER_KW = dict(_WALK, gesture=[(0.12, 3.6, "open_arms", dict(ease=0.45, lift=0.15)),
                                 (38.0, 48.4, "touch", dict(side="L", to=HAND_AT, palm="down", fingers="pinch",
                                                            look=False, ease=1.1)),
                                 (49.6, 60.0, "raise", dict(ease=1.7))])
_ACT = Actor("woman", **MOTHER_KW)
_STEP = 0.1
_GRID = np.arange(-1.0, TOTAL + 1.01, _STEP)
_MPATH = np.array([_ACT.where(float(t), "ground") for t in _GRID])
_MBACK = np.array([_ACT.where(float(t), "back") for t in _GRID])
_MPINCH = np.array([_ACT.where(float(t), "pinch.L") for t in _GRID])


def _interp(tab, t):
    x = (float(t) - _GRID[0]) / _STEP
    k = int(np.clip(np.floor(x), 0, len(_GRID) - 2))
    f = min(max(x - k, 0.0), 1.0)
    return tab[k] * (1 - f) + tab[k + 1] * f


def M(t):
    """Heavenly Mother's feet at t (world metres)."""
    return _interp(_MPATH, t)


def MB(t):
    """Her upper back, where the veil river leaves her."""
    return _interp(_MBACK, t)


def MH(t):
    """Her left hand (the thread is held between thumb and finger)."""
    return _interp(_MPINCH, t)


def mz(t):
    return float(M(t)[2])


# stations: places on the lake where the veil gathers two people (world z), set behind where she is then
ZG = mz(1.6) + 12.0          # 1 the greeting
ZH = mz(8.3) + 10.0          # 2 the help
ZC = mz(14.0) + 10.5         # 3 the mending, under the canopy
ZN = mz(22.4) + 9.0          # 4 the narrows
ZL = mz(29.3) + 9.5          # 5 the loom
ZP = mz(35.0) + 9.0          # 6 the procession
ZSTOP = mz(40.0)             # where she stands from the breath on
ARCH_Z = ZSTOP - 21.0        # the arch stands ahead of her at the end


def W3(x, y, z):
    return np.array([x, y, z], np.float64)


# ------------------------------------------------------------------------------------------------ the camera
class Path(Move):
    """A camera move from a function of time giving (position, target)."""

    def __init__(self, fn, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.fn = fn

    def pose(self, t):
        p, q = self.fn(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _mrel(t, d):
    return M(t) + np.asarray(d, np.float64)


_K1 = [  # 1 THE CAST
    (0.00, _mrel(0.00, (0.0, 1.22, 2.00)), _mrel(0.00, (0.0, 1.90, -6.0))),
    (0.30, _mrel(0.30, (-0.05, 1.24, 2.06)), _mrel(0.30, (0.0, 1.88, -6.0))),
    (1.30, _mrel(1.30, (-0.9, 1.45, 10.0)), _mrel(1.30, (0.0, 1.25, 0.0))),
    (2.45, _mrel(2.45, (-3.6, 7.8, 33.0)), _mrel(2.45, (0.0, 0.6, -3.0))),
    (3.35, W3(1.25, 1.75, ZG + 7.3), W3(0.0, 2.05, ZG - 2.0)),
    (6.20, W3(0.80, 1.72, ZG + 6.5), W3(0.0, 2.05, ZG - 2.0)),
    (6.84, W3(0.50, 1.85, ZG + 4.9), W3(0.0, 2.20, ZG - 3.0)),
]
_K2 = [  # 2 THE ROAD
    (6.84, _mrel(6.84, (2.3, 0.55, 46.0)), _mrel(6.84, (0.0, 1.0, 0.0))),
    (7.56, _mrel(7.56, (-1.5, 0.70, 26.0)), _mrel(7.56, (0.0, 1.2, 0.0))),
    (8.30, W3(1.30, 1.38, ZH + 5.2), W3(0.0, 1.55, ZH - 1.5)),
    (11.30, W3(0.70, 1.32, ZH + 4.4), W3(0.0, 1.55, ZH - 1.5)),
    (12.30, W3(0.3, 3.40, ZH + 2.6), _mrel(12.3, (0.0, 1.6, 0.0))),
    (13.30, _mrel(13.3, (0.0, 2.60, 6.5)), _mrel(13.3, (0.0, 1.5, 0.0))),
]
_K3 = [  # 3 THE CANOPY
    (13.30, W3(-1.9, 0.95, ZC + 5.0), W3(0.3, 1.70, ZC - 3.0)),
    (16.90, W3(1.2, 1.05, ZC + 3.9), W3(0.3, 1.70, ZC - 3.0)),
    (17.70, W3(0.95, 1.20, ZC + 3.5), W3(0.15, 1.50, ZC - 2.0)),
    (19.50, W3(0.3, 1.75, ZC + 5.0), W3(0.2, 2.10, ZC - 3.0)),
    (19.85, W3(0.1, 2.30, ZC + 5.2), W3(0.0, 2.80, ZC - 6.0)),
]
_K4 = [  # 4 THE RIVER (no cut: we burst up through the roof)
    (19.85, W3(0.1, 2.30, ZC + 5.2), W3(0.0, 2.80, ZC - 6.0)),
    (21.10, _mrel(21.1, (-5.0, 17.0, 50.0)), _mrel(21.1, (0.0, 0.0, 4.0))),
    (22.45, W3(1.30, 1.70, ZN + 6.2), W3(0.0, 1.95, ZN - 3.0)),
    (25.60, W3(0.50, 1.65, ZN + 5.2), W3(0.0, 1.95, ZN - 3.0)),
    (26.79, W3(0.15, 1.45, ZN + 1.8), W3(0.0, 1.60, ZN - 6.0)),
]
_K5 = [  # 5 THE LOOM
    (26.79, _mrel(26.79, (0.0, 2.20, 40.0)), _mrel(26.79, (0.0, 1.8, 0.0))),
    (28.30, W3(0.3, 2.30, ZL + 13.0), W3(0.0, 2.00, ZL - 4.0)),
    (29.35, W3(0.0, 1.70, ZL + 5.4), W3(0.0, 1.90, ZL - 2.0)),
    (32.30, W3(-0.45, 1.62, ZL + 4.6), W3(0.0, 1.90, ZL - 2.0)),
    (33.36, W3(0.25, 1.45, ZL + 2.5), W3(0.0, 1.70, ZL - 4.0)),
]
_K6 = [  # 6 THE PROCESSION, then the rush along the one thread to her hand
    (33.36, W3(6.0, 3.6, ZP + 13.0), W3(0.0, 1.2, ZP - 4.0)),
    (35.00, W3(1.6, 1.65, ZP + 5.8), W3(0.0, 1.95, ZP - 2.0)),
    (38.10, W3(0.8, 1.58, ZP + 4.9), W3(0.0, 1.95, ZP - 2.0)),
    (39.20, W3(-0.9, 0.80, ZP - 2.0), _mrel(39.2, (-0.3, 0.85, 0.0))),
    (40.21, _mrel(40.21, (-1.70, 0.55, 3.30)), _mrel(40.21, (-0.30, 0.95, 0.0))),
]
_K7 = [  # 7 THE THREAD (the breath), the sunrise
    (40.21, _mrel(40.21, (-1.70, 0.55, 3.30)), _mrel(40.21, (-0.30, 0.95, 0.0))),
    (41.55, _mrel(41.55, (-1.50, 0.62, 3.00)), _mrel(41.55, (-0.30, 0.98, 0.0))),
    (42.45, _mrel(42.45, (-0.75, 1.45, 5.6)), _mrel(42.45, (-0.3, 1.55, 0.0))),
    (45.20, _mrel(45.2, (-0.55, 1.45, 5.7)), _mrel(45.2, (-0.25, 1.60, 0.0))),
]
_ORBIT_C = M(45.0) + np.array([-0.25, 0.0, 0.0])
_K8 = [  # 8 THE LIFTING (after the half circle)
    (49.47, None, None),
    (51.00, _mrel(51.0, (1.4, 2.6, 7.5)), W3(0.0, 6.5, ARCH_Z)),
    (55.00, _mrel(55.0, (0.6, 4.4, 13.0)), W3(0.0, 7.4, ARCH_Z)),
    (60.00, _mrel(60.0, (0.3, 5.6, 17.5)), W3(0.0, 8.2, ARCH_Z)),
]


def _fly(keys, **kw):
    return fly([(t, tuple(p), tuple(q)) for t, p, q in keys], **kw)


def _half_circle_end():
    a = np.radians(34.0)
    return W3(_ORBIT_C[0] + 4.6 * np.sin(a), 2.1, _ORBIT_C[2] + 4.6 * np.cos(a))


_K8[0] = (49.47, _half_circle_end(), M(49.47) + np.array([0.0, 2.4, -3.0]))

ROLL5 = Track([(26.79, 0.0), (27.35, 0.0), (28.85, 360.0), (TOTAL, 360.0)])


def _station_focus(t):
    """What the lens is focused on: Heavenly Mother, or the two people of the section (the words stay sharp
    whatever the lens does)."""
    mm = M(t) + np.array([0.0, 1.45, 0.0])
    keys = [(-1.0, mm), (2.7, mm), (3.1, MEET), (6.84, MEET), (6.85, mm), (7.9, mm), (8.3, W3(0.0, 1.0, ZH)),
            (12.0, W3(0.0, 1.0, ZH)), (12.8, mm), (13.29, mm), (13.30, W3(0.0, 0.9, ZC)), (19.85, W3(0.0, 0.9, ZC)),
            (20.5, mm), (21.8, mm), (22.4, W3(0.0, 1.3, ZN + 1.5)), (26.79, W3(0.0, 1.3, ZN + 1.5)), (26.8, mm),
            (28.6, mm), (29.3, W3(0.0, 1.4, ZL)), (33.36, W3(0.0, 1.4, ZL)), (33.37, mm), (34.3, mm),
            (35.0, W3(0.0, 1.3, ZP)), (38.2, W3(0.0, 1.3, ZP)), (39.6, mm), (40.21, MH(40.21)), (41.2, MH(41.2)),
            (42.4, CHILD(42.4) + np.array([0.0, 0.9, 0.0])), (45.0, CHILD(45.0) + np.array([0.0, 0.9, 0.0])),
            (45.9, mm), (TOTAL + 1.0, mm)]
    for (ta, pa), (tb, pb) in zip(keys[:-1], keys[1:]):
        if ta <= t < tb:
            u = ss(0.0, 1.0, (t - ta) / (tb - ta))
            return np.asarray(pa, np.float64) * (1.0 - u) + np.asarray(pb, np.float64) * u
    return mm


def CHILD(t):
    """Where the child's feet are (an estimate for the lens: she walks the thread toward Heavenly Mother)."""
    u = float(np.clip((t - 41.2) / (47.9 - 41.2), 0.0, 1.0))
    return np.array([-0.82, 0.0, ZSTOP + 2.7 - 2.0 * u])


def _rigs(focus):
    return Rig([
        _fly(_K1, fov=Track([(0.0, 40.0), (0.3, 40.0), (1.3, 54.0), (2.45, 60.0), (3.35, 40.0), (6.84, 42.0)]),
             aperture=Track([(0.0, 0.035), (1.0, 0.02), (3.0, 0.04), (6.84, 0.04)]), focus=focus),
        _fly(_K2, blend=0.0, fov=Track([(6.84, 60.0), (8.3, 40.0), (12.0, 40.0), (13.3, 52.0)]),
             roll=Track([(6.84, 12.0), (7.56, -9.0), (8.3, 0.0), (13.3, 0.0)]), aperture=0.04, focus=focus),
        _fly(_K3, blend=0.0, fov=44.0, aperture=0.045, focus=focus),
        _fly(_K4, blend=0.3, fov=Track([(19.85, 44.0), (21.1, 58.0), (22.45, 40.0), (26.79, 42.0)]),
             roll=Track([(19.85, 0.0), (21.1, -6.0), (21.8, -14.0), (22.45, 0.0), (26.79, 0.0)]),
             aperture=Track([(19.85, 0.04), (21.0, 0.01), (22.4, 0.04)]), focus=focus),
        _fly(_K5, blend=0.0, fov=Track([(26.79, 58.0), (28.3, 54.0), (29.35, 42.0), (33.36, 42.0)]),
             roll=ROLL5, aperture=0.04, focus=focus),
        _fly(_K6, blend=0.0, fov=Track([(33.36, 50.0), (35.0, 42.0), (38.1, 42.0), (39.2, 50.0), (40.21, 36.0)]),
             roll=Track([(33.36, 360.0), (TOTAL, 360.0)]), aperture=Track([(33.36, 0.04), (39.5, 0.04),
                                                                            (40.21, 0.02)]), focus=focus,
             near=0.03),
        _fly(_K7, blend=0.0, fov=Track([(40.21, 36.0), (41.55, 35.0), (42.45, 42.0), (45.2, 42.0)]),
             roll=Track([(40.21, 360.0), (TOTAL, 360.0)]), aperture=Track([(40.21, 0.03), (41.4, 0.035)]),
             focus=focus, near=0.03),
        orbit(_ORBIT_C, radius=(5.6, 4.6), height=(1.45, 2.1), a0=-30.0, a1=34.0, t0=45.2, t1=49.47,
              look=lambda t: M(t) + np.array([-0.15, 2.0, -3.0]), fov=46.0, roll=360.0, aperture=0.03,
              focus=lambda t: M(t) + np.array([0.0, 1.5, 0.0]), blend=1.0),
        _fly(_K8, blend=1.2, fov=Track([(49.47, 46.0), (51.0, 54.0), (60.0, 54.0)]), roll=360.0,
             aperture=0.02, focus=lambda t: M(t) + np.array([0.0, 1.5, 0.0])),
    ], blend=1.0, fov=44.0, aperture=0.04, handheld=0.22, min_height=0.3)


LAYOUT = _rigs("target")


# -------------------------------------------------------------------------------------- the nine expressions
def _word(x, y, depth, px, t_in, t0, t1, t_out, **kw):
    """A word laid out by where it is read: the screen place of its centre and the pixels of one em (1080p)
    at the middle of its reading moment, `depth` metres from the camera."""
    tm = 0.5 * (t0 + t1)
    return dict(pos=tuple(PW.place(LAYOUT, tm, x, y, depth)), em=PW.em_for(LAYOUT, tm, depth, px),
                t_in=t_in, t_read0=t0, t_read1=t1, t_out=t_out, **kw)


MEET = W3(0.0, 1.12, ZG)                                # where the greeting hands meet
PULL_AT, PULL_T0 = (0.07, ZH + 1.58), 6.60                # the pair of the Consideration (motion capture)
_PULL = Actor("woman", at=PULL_AT, facing=180.0, motion=[(PULL_T0, "pull_up")], seed=22.0)
_SPECS = [
    _word(0.5, 0.675, 7.6, 104, 1.30, 3.40, 6.20, 7.10, expr="Greeting", arrive="touch", source=tuple(MEET),
          touch_at=(2.50 - 1.30) / (3.40 - 1.30), leave="bokeh"),
    _word(0.5, 0.675, 7.0, 84, 7.40, 8.50, 11.20, 12.50, expr="Consideration", arrive="palm",
          source=lambda t: _PULL.where(t, "palm.L"), palm_light=True, leave="petals", wind=(0.0, 0.5, -1.0),
          reach=0.3),
    _word(0.5, 0.68, 7.2, 84, 13.30, 14.30, 16.90, 16.90, expr="Apology", arrive="stitch", leave="morph"),
    _word(0.5, 0.68, 7.2, 92, 16.90, 17.35, 19.95, 21.0, expr="Inclusiveness", arrive="morph",
          source="Apology", leave="bokeh"),
    _word(0.5, 0.675, 7.6, 104, 21.10, 22.80, 25.55, 26.70, expr="Concession", arrive="flock",
          leave="wind", wind=(0.2, 0.3, -1.0)),
    _word(0.5, 0.675, 7.0, 86, 27.60, 29.55, 32.30, 33.30, expr="Respect", arrive="weave", leave="unravel",
          to=tuple(M(32.5) + np.array([0.0, 1.4, 0.0]))),
    _word(0.5, 0.68, 7.4, 76, 33.70, 35.20, 37.95, 39.30, expr="Gratitude", arrive="petals", leave="stream",
          to=tuple(MH(39.5))),
    _word(0.5, 0.685, 6.3, 82, 41.00, 42.55, 45.15, 45.95, expr="Encouragement", arrive="shaft", leave="rise",
          halo=1.5, bright=1.15),
    dict(expr="Compliment", ride=(0.5, 0.69, 6.4), em=PW.em_for(LAYOUT, 48.0, 6.4, 90), face="screen",
         t_in=45.95, t_read0=46.95, t_read1=49.60, t_out=50.40, arrive="rays", leave="rise", halo=1.5, bright=1.15,
         source=tuple(M(46.0) + np.array([0.0, 1.75, -60.0]))),
]

WORDS = PW.Words(_SPECS, camera=LAYOUT, face="camera", tint=0.5)


def _focus_default(t):
    return M(t) + np.array([0.0, 1.5, 0.0])


CAMERA = _rigs(_station_focus)
WORDS.camera = CAMERA
for _w in WORDS:
    _w.camera = CAMERA


# ------------------------------------------------------------------------------------------------- the veil
GOLD, WHITE_GOLD, AMBER, COOL = "#ffd27a", "#fff1d6", "#ffb860", "#a9c8ff"
ROSE, ROSE_WHITE = "#ffb4c4", "#ffe6e0"
_CT = [(0.0, (WHITE_GOLD, GOLD)), (S[1] - 0.01, (WHITE_GOLD, GOLD)), (S[1], ("#fff6e4", "#ffd88a")),
       (S[2] - 0.6, ("#fff6e4", "#ffd88a")), (S[2] + 0.4, ("#ffe2b0", AMBER)), (S[3], ("#ffe2b0", AMBER)),
       (S[3] + 1.0, (WHITE_GOLD, GOLD)), (S[5] - 0.01, (WHITE_GOLD, GOLD)), (S[5], ("#fff4dc", "#ffe2b0")),
       (BIG - 0.2, ("#fff4dc", "#ffe2b0")), (BIG + 0.8, (ROSE_WHITE, ROSE)), (52.0, (ROSE_WHITE, ROSE)),
       (55.0, ("#fff4ee", "#ffd0d8")), (TOTAL, ("#fff4ee", "#ffd0d8"))]
VEIL_CORE = Track([(t, lin(c[0])) for t, c in _CT])
VEIL_EDGE = Track([(t, lin(c[1])) for t, c in _CT])

S_MAX = 340.0
LENGTH = Track([(0.0, 1.8), (HIT0, 1.8), (1.1, 26.0), (2.4, 200.0), (3.4, S_MAX + 30.0), (TOTAL, S_MAX + 30.0)])
CANOPY = Track([(0.0, 0.0), (12.95, 0.0), (13.65, 1.0), (19.85, 1.0), (20.55, 0.0), (TOTAL, 0.0)])
LOOM = Track([(0.0, 0.0), (S[4] - 0.01, 0.0), (S[4], 1.0), (S[5] - 0.01, 1.0), (S[5], 0.0), (38.0, 0.0),
              (39.2, 0.85), (BIG - 0.3, 0.85), (BIG + 0.6, 0.0), (TOTAL, 0.0)])
ONE = Track([(0.0, 0.0), (38.0, 0.0), (39.4, 1.0), (BIG - 0.3, 1.0), (BIG + 0.8, 0.35), (49.5, 0.35),
             (50.5, 0.0), (TOTAL, 0.0)])
SHEET = Track([(0.0, 1.0), (S[4] - 0.01, 1.0), (S[4], 0.12), (S[5] - 0.01, 0.12), (S[5], 1.0), (38.0, 1.0),
               (39.4, 0.06), (BIG - 0.3, 0.06), (BIG + 0.9, 1.15), (TOTAL, 1.15)])
LIFT_T0, LIFT_DUR, LIFT_SPREAD = 49.9, 2.6, 2.2
LOOM_TALL = Track([(0.0, 1.0), (29.0, 1.0), (29.7, 0.28), (32.3, 0.28), (33.1, 1.0), (TOTAL, 1.0)])


class VeilRiver:
    """Heavenly Mother's veil as a river of light: a sheet of flowing points on a centre line that leaves her
    upper back, falls to the water and runs back across the lake, widening, with travelling folds; a warp of
    fine threads in it; one thread from her hand for the breath; and, at the end, the whole cloth lifting off
    the lake into the sky ahead of her. A pure function of t."""

    wants_camera = True

    def __init__(self, n=170000, threads=30, k=150, seed=9):
        rng = np.random.default_rng(seed)
        self.n = n
        self.u = rng.random(n)
        v = rng.random(n) * 2.0 - 1.0
        hem = rng.random(n) < 0.12
        v[hem] = np.sign(v[hem]) * (0.97 + 0.03 * rng.random(hem.sum()))
        self.v = v
        self.hem = hem
        self.sd = rng.random(n)
        self.ph = rng.random(n) * 6.283
        self.spark = rng.random(n) < 0.10
        self.nt, self.k = threads, k
        self.tv = np.linspace(-0.92, 0.92, threads)
        self.th = 0.35 + 4.6 * rng.random(threads)          # each thread's height on the loom
        self.tcool = (np.arange(threads) % 3) == 1           # a cool thread among the warm ones on the loom
        self.j0 = threads // 2                               # the one thread of the breath
        q = np.linspace(0.0, 1.0, k + 1)
        self.ts = S_MAX * q ** 2.0

    # ---- the shape of the cloth at (s, v): s metres back from her, v across (-1..1)
    def shape(self, s, v, t, hem_pos=None):
        b = MB(t) if hem_pos is None else hem_pos
        c = float(CANOPY(t))
        lo = float(LOOM(t))
        lvl = _level(t)
        A = 15.0 * ss(10.0, 170.0, s) * (1.0 - c)
        xc = A * (np.sin(s / 41.0 + 0.6) + 0.45 * np.sin(s / 17.0 + 2.1)) + b[0] * np.exp(-s / 3.0)
        yc = 0.24 + (b[1] - 0.24) * np.exp(-s / 1.25)
        half = 0.5 * (0.42 + 0.17 * s)
        amp = np.minimum(0.04 + 0.03 * s, 1.5) * (1.0 - 0.85 * c) * (1.0 - lo) * (0.75 + 0.5 * lvl)
        lam = 3.2 + 0.07 * s
        fold = amp * (np.sin(6.283 * (s / lam) - 3.3 * t + 2.4 * v) + 0.3 * np.sin(5.0 * v + 1.3 * t + 0.21 * s))
        y = np.maximum(yc + fold + 0.04 * half * v ** 4, 0.05)
        x = xc + v * half
        if c > 0.0:
            g = c * ss(0.0, 3.0, s) * (1.0 - ss(58.0, 92.0, s))
            roof = (b[1] + (4.7 - b[1]) * ss(0.0, 3.4, s)) - 2.3 * v ** 2 * ss(1.0, 6.0, s) \
                + 0.22 * np.sin(0.55 * s - 1.4 * t + 3.0 * v)
            hw = np.maximum(half, 5.2 * ss(0.0, 5.0, s) + 0.3)
            x = x * (1.0 - g) + (v * hw) * g
            y = y * (1.0 - g) + roof * g
        z = b[2] + s
        return x, y, z

    def sample(self, t, cam=None):
        b = MB(t)
        eye = None if cam is None else np.asarray(cam.pos, np.float64)
        L = float(LENGTH(t))
        core, edge = VEIL_CORE(t), VEIL_EDGE(t)
        sheet = float(SHEET(t))
        lo, one = float(LOOM(t)), float(ONE(t))
        out = []
        # ---- the sheet of flowing points
        q = np.mod(self.u + 0.010 * t, 1.0)
        s = S_MAX * q ** 2.2
        x, y, z = self.shape(s, self.v, t, b)
        pos = np.stack([x, y, z], axis=1)
        a = (0.30 + 0.25 * self.hem) * ss(0.0, 0.5, s) * (1.0 - ss(S_MAX * 0.9, S_MAX, s))
        a = a * (0.22 + 0.78 * ss(0.3, 9.0, s))          # the cloth is dense near her: keep it from burning out
        a = a * (1.0 - ss(L - 3.0, L, s)) * sheet
        front = np.exp(-((s - L) / 2.5) ** 2) * (L < S_MAX)
        tw = 0.75 + 0.25 * np.sin(self.ph + 2.1 * t + 0.3 * s)
        a = a * tw
        size = (0.020 + 0.035 * self.sd ** 3) * (1.0 + s / 70.0)
        mix = (np.abs(self.v) ** 2)[:, None]
        col = core[None] * (1.0 - mix) + edge[None] * mix
        pos, a, size = self._lift(pos, s, self.v, t, a, size)
        if eye is not None:                               # no giant discs right at the lens
            d = np.linalg.norm(pos - eye, axis=1)
            a = a * ss(0.9, 3.2, d)
        keep = a > 0.004
        sp = keep & self.spark
        so = keep & ~self.spark
        emit = 1.0 + 2.5 * front
        if so.any():
            out.append(dict(pos=pos[so], size=size[so], color=col[so], alpha=a[so], kind="soft", emit=emit[so]))
        if sp.any():
            out.append(dict(pos=pos[sp], size=size[sp] * 1.3, color=col[sp], alpha=a[sp] * 1.4, kind="spark",
                            twinkle=0.8, emit=emit[sp]))
        # ---- the warp: fine threads along the cloth, which become taut strings on the loom
        th = self.threads(t, b, L, lo, one, core, edge, eye)
        if th is not None:
            out.append(th)
        return out

    def _lift(self, pos, s, v, t, a, size):
        """The end: the cloth peels off the lake from its far end toward her and streams over our heads into
        the sky ahead of her, where it spreads as a vast canopy of light."""
        if t < LIFT_T0:
            return pos, a, size
        delay = LIFT_SPREAD * (1.0 - np.clip(s / S_MAX, 0.0, 1.0) ** 0.5)
        f = ss(0.0, 1.0, (t - LIFT_T0 - delay) / LIFT_DUR)
        if not np.any(f > 0):
            return pos, a, size
        m = M(t)
        sky = np.stack([v * (10.0 + 0.28 * s) + 4.0 * np.sin(s / 23.0),
                        13.0 + 0.06 * s + 2.0 * np.sin(v * 3.0 + s / 30.0 + 0.4 * t),
                        np.full_like(s, m[2]) - 26.0 - 0.50 * s], axis=1)
        arc = (4.0 * f * (1.0 - f) * (8.0 + 0.04 * s))[:, None] * np.array([0.0, 1.0, 0.0])
        p = pos * (1.0 - f[:, None]) + sky * f[:, None] + arc
        # near her (s < 4) the cloth stays on her shoulders
        hold = ss(1.0, 5.0, s)
        p = pos * (1.0 - hold[:, None]) + p * hold[:, None]
        calm = 1.0 - 0.6 * float(ss(52.6, 55.0, t))
        return p, a * (1.0 + 0.3 * f * hold) * calm, size * (1.0 + 1.5 * f * hold)

    def threads(self, t, b, L, lo, one, core, edge, eye=None):
        nt, k = self.nt, self.k
        s = np.tile(self.ts, (nt, 1))                        # (nt, k+1)
        v = np.repeat(self.tv[:, None], k + 1, axis=1)
        x, y, z = self.shape(s.ravel(), v.ravel(), t, b)
        x, y, z = x.reshape(nt, -1), y.reshape(nt, -1), z.reshape(nt, -1)
        if lo > 0.0:
            fan = 0.25 + (0.30 + 0.25 * (1.0 - float(LOOM_TALL(t)))) * s
            xl = b[0] + v * fan * 0.5
            th = 0.24 + (self.th[:, None] - 0.24) * float(LOOM_TALL(t))
            hl = 0.24 + (th - 0.24) * ss(0.0, 14.0, s) + (b[1] - 0.24) * np.exp(-s / 1.3)
            hl = hl + 0.03 * np.sin(31.0 * t + np.arange(nt)[:, None] * 1.7) * (0.3 + _beat(t)) * ss(0.0, 4.0, s)
            x = x * (1.0 - lo) + xl * lo
            y = y * (1.0 - lo) + hl * lo
        if one > 0.0:
            h = MH(t)
            j = self.j0
            xo = h[0] * np.exp(-s[j] / 2.5) + (1.0 - np.exp(-s[j] / 2.5)) * (-0.5)
            yo = 0.18 + (h[1] - 0.18) * np.exp(-s[j] / 1.1)
            zo = h[2] + s[j]
            x[j] = x[j] * (1.0 - one) + xo * one
            y[j] = y[j] * (1.0 - one) + yo * one
            z[j] = z[j] * (1.0 - one) + zo * one
        p = np.stack([x, y, z], axis=2)
        lf = 0.0
        if t >= LIFT_T0:
            lf = float(ss(LIFT_T0, LIFT_T0 + 1.2, t))
        a0 = (0.07 + 0.70 * lo) * (1.0 - lf)
        al = np.full((nt, k), a0)
        if one > 0.0:
            keep = np.zeros(nt)
            keep[self.j0] = 1.0
            al = al * (1.0 - one) + (keep[:, None] * (1.6 + 0.8 * one)) * one
        sm = 0.5 * (s[:, :-1] + s[:, 1:])
        al = al * (1.0 - ss(L - 3.0, L, sm)) * ss(0.0, 0.6, sm) * (1.0 - ss(S_MAX * 0.85, S_MAX, sm))
        if not np.any(al > 0.003):
            return None
        col = np.repeat(edge[None], nt, axis=0)
        if one > 0.0:
            col[self.j0] = col[self.j0] * (1.0 - one) + lin("#ffd890") * one
        if lo > 0.0:
            cool = lin(COOL)
            col = col * (1.0 - lo * self.tcool[:, None]) + cool[None] * (lo * self.tcool[:, None])
        col = np.repeat(col[:, None, :], k, axis=1).reshape(-1, 3)
        a, b2 = p[:, :-1].reshape(-1, 3), p[:, 1:].reshape(-1, 3)
        al = al.ravel()
        if eye is not None:
            al = al * ss(0.5, 2.5, np.linalg.norm(0.5 * (a + b2) - eye, axis=1))
        keep = al > 0.003
        u = s[:, :-1].ravel()
        return dict(pos=a[keep], pos2=b2[keep], size=0.0045 + 0.004 * lo, color=col[keep], alpha=al[keep],
                    kind="line", u=u[keep], u2=s[:, 1:].ravel()[keep], pulse=(9.0, 3.0, 2.5, 4.0), emit=1.4)


VEIL = VeilRiver()


def river_points(z0, n=900, spread=1.4, seed=0):
    """Points lying in the river round a station (where a person gathers from)."""
    rng = np.random.default_rng(seed)
    return np.stack([rng.normal(0.0, spread, n), 0.24 + 0.05 * rng.random(n), z0 + rng.normal(0.0, 2.2, n)], axis=1)


# ----------------------------------------------------------------------------------------------- the people
def _people():
    from p3d.body import Body
    P = {}

    def body(name, shape, x, z, facing, show, color, color2, garment, look="glitter", motion="stand", gesture=(),
             effects=(), points=52000, seed=1.0, form=True, local=False, **kw):
        eff = list(effects)
        if form:
            src = river_points(z, seed=int(seed * 7), spread=0.5) + np.array([x, 0.0, 0.0]) if local else \
                river_points(z, seed=int(seed * 7))
            eff.insert(0, dict(kind="form", t=show[0], dur=1.3, source=src, travel=1.0))
        P[name] = Body(shape, at=(x, z), facing=facing, motion=motion, gesture=list(gesture), garment=garment,
                       look=look, color=color, color2=color2, effects=eff, points=points, seed=seed,
                       show=show, fade=0.35, **kw)
        return P[name]

    # 1 Greeting: two rise out of the river and clasp hands on the hit at 2.50
    body("greet_a", "woman", -0.48, ZG, 90.0, (0.9, 7.3), GOLD, "#fff0d0", "dress", seed=11.0,
         gesture=[(1.6, 7.2, "handshake", dict(side="R", to=tuple(MEET), grip=1.0, ease=0.7))])
    body("greet_b", "man", 0.48, ZG, 270.0, (0.9, 7.3), COOL, "#e8f0ff", "coat", seed=12.0,
         gesture=[(1.6, 7.2, "handshake", dict(side="R", to=tuple(MEET), grip=1.0, ease=0.7))])
    # 2 Consideration: one sits spent on the water; the other comes, gives a hand and pulls them up (a pair
    # captured together in motion capture, so their hands really meet)
    body("weary", "man", PULL_AT[0], PULL_AT[1], 180.0, (6.84, 13.5), COOL, "#e8f0ff", "coat", seed=21.0,
         motion=[(PULL_T0, "helped_up")], form=False)
    body("helper", "woman", PULL_AT[0], PULL_AT[1], 180.0, (6.84, 13.5), GOLD, "#fff0d0", "dress", seed=22.0,
         motion=[(PULL_T0, "pull_up")], form=False)
    # 3 Apology, Inclusiveness: one sits, coming apart; one kneels beside her; the embrace mends her
    hurt = body("hurt", "woman", -0.42, ZC, 90.0, (13.30, 20.4), COOL, "#eef2ff", "dress", seed=31.0, form=False,
                motion=[(12.5, "sit", dict(dur=0.2))],
                effects=[dict(kind="disperse", t=13.6, amount=Track([(13.6, 0.0), (16.4, 0.42), (16.9, 0.42),
                                                                      (18.3, 0.0)]), reach=2.5)])
    body("sorry", "man", 0.42, ZC + 0.05, 270.0, (13.30, 20.4), GOLD, "#fff0d0", "tunic", seed=32.0, form=False,
         motion=[(12.5, "kneel", dict(dur=0.2))],
         gesture=[(13.9, 16.9, "hand_on_shoulder", dict(side="L", to=lambda t: hurt.where(t, "shoulder.R"),
                                                       ease=0.8)),
                  (16.9, 20.4, "embrace", dict(to=lambda t: hurt.where(t, "blade.R"),
                                               to2=lambda t: hurt.where(t, "blade.L"), ease=0.8))])
    # 4 Concession: two walk up the narrows; one steps aside and opens a palm, the other walks on
    body("yield", "man", -0.70, ZN + 1.0, 160.0, (20.6, 27.0), GOLD, "#fff0d0", "coat", seed=41.0,
         motion=[(20.6, "walk", dict(speed=0.6)), (22.2, "stand")],
         gesture=[(22.4, 26.8, "offer", dict(side="L", ease=0.8)), (22.6, 24.0, "bow", dict(amount=14.0))])
    body("first", "woman", 0.55, ZN + 2.2, 180.0, (20.6, 27.0), COOL, "#eef2ff", "dress", seed=42.0,
         motion=[(20.6, "walk", dict(speed=0.62))])
    # 5 Respect: two in profile; she gives her thoughts as a stream from her palm, he listens
    sp = body("speaker", "woman", -1.05, ZL, 90.0, (26.79, 33.6), GOLD, "#fff0d0", "dress", seed=51.0, form=False,
              gesture=[(27.6, 31.6, "blow", dict(side="R", ease=0.7))],
              effects=[dict(kind="blow", t=28.0, dur=3.2, side="R", n=4000, reach=2.0,
                            dir=(1.0, 0.12, 0.0))])
    body("listener", "man", 1.05, ZL, 270.0, (26.79, 33.6), COOL, "#e8f0ff", "tunic", seed=52.0, form=False,
         gesture=[(27.4, 33.6, "listen", dict(side="L", ease=0.8))])
    # 6 Gratitude: people walk in her veil behind her; one bows to another, who bows back
    body("thank", "man", -0.62, ZP, 90.0, (33.36, 38.9), GOLD, "#fff0d0", "coat", seed=61.0, form=False,
         gesture=[(34.0, 38.6, "bow", dict(amount=32.0, ease=0.9))])
    body("thanked", "woman", 0.62, ZP, 270.0, (33.36, 38.9), COOL, "#eef2ff", "dress", seed=62.0, form=False,
         gesture=[(35.0, 38.6, "bow", dict(amount=14.0, ease=0.9))])
    for i, (x, dz, sh, c) in enumerate(((-1.6, -4.0, "woman", "#ffe2b0"), (1.7, -5.5, "man", "#ffd9a0"),
                                        (-0.9, -9.0, "man", "#dfe8ff"), (1.1, -11.5, "woman", "#ffe8c8"))):
        body(f"walker{i}", sh, x, ZP + dz + 1.0, 180.0, (33.36, 38.9), c, "#fff4e0",
             "robe" if sh == "woman" else "tunic", seed=70.0 + i, form=False, points=34000,
             motion=[(33.0, "walk", dict(speed=0.75, phase=0.27 * i))])
    # 7 the child walks the thread to her and takes her hand
    body("child", "child", -0.82, ZSTOP + 2.7, 180.0, (40.4, TOTAL), "#e8f0ff", "#fff6e6", "tunic", seed=81.0,
         form=True, points=40000,
         motion=[(41.2, "walk", dict(speed=0.30)), (47.9, "stand", dict(blend=0.8))],
         gesture=[(48.0, TOTAL, "touch", dict(side="R", to=lambda t: MH(t) + np.array([0.0, -0.04, 0.05]),
                                               end="palm", palm="up", ease=1.0))])
    # 8 at the sunrise the veil gives everyone back: they rise out of it on both sides of her, at many depths,
    # facing the sun with her, and lift their arms with her
    ring = ((-2.0, 0.9, "woman", GOLD), (2.1, 0.7, "man", COOL), (-4.3, -1.6, "man", "#ffe2b0"),
            (4.4, -1.9, "woman", "#ffd9a0"), (-6.6, -4.6, "woman", "#dfe8ff"), (6.8, -4.9, "man", "#ffe8c8"),
            (-9.4, -8.5, "man", "#ffd9a0"), (9.6, -8.8, "woman", "#e8eeff"))
    for i, (x, dz, sh, c) in enumerate(ring):
        t0 = BIG + 0.12 + 0.28 * i
        body(f"risen{i}", sh, x, ZSTOP + dz, 180.0 + (6.0 if x < 0 else -6.0), (t0 - 0.05, TOTAL), c, "#fff6e8",
             "robe" if sh == "woman" else "coat", seed=90.0 + i, points=30000, local=True, bright=0.8,
             gesture=[(46.3 + 0.2 * i, TOTAL, "raise", dict(ease=1.6))])
    return P


def _mother():
    from p3d.body import Body
    # a body of light, warm gold and white, with a soft rim; the head is only her veil (no head beneath it, so
    # from behind there is nothing but the veil); light streams off her back into the river
    return Body("woman", garment="robe", veil=dict(length=1.5, wide=1.6),
                look=[dict(name="glitter", bright=0.9), dict(name="rim", bright=0.7)],
                color="#ffd9a0", color2="#fff4e0", points=90000, detail=dict(hand=3.0, head=0.02), light=None,
                wind=(0.0, 0.0, 0.6),
                effects=[dict(kind="shed", t=0.0, n=3500, life=3.0, dir=(0.0, 0.55, 1.0), speed=0.40)],
                **MOTHER_KW)


def _setup(scene):
    mother = _mother()
    mother.add(scene, "mother", mask=dict(strength=0.35))
    scene.add("veil", PW.KeepClear(VEIL, WORDS))
    for name, b in _people().items():
        b.add(scene, name)
    WORDS.add_to(scene)
    try:
        WORDS.check(CAMERA)
    except Exception as e:          # the check only advises
        print("words check failed:", e)


# ------------------------------------------------------------------------------------------------ the world
LOOKS = dict(
    veilnight=dict(base="night", sky_mid="#0a1546", sky_hor="#24357a", sun_az=180.0, sun_el=6.0, dust=0.35,
                   bokeh=0.25,
                   sun_color="#ffd9a0", sun_int=0.6, sun_size=0.7, sun_disc=0.0, sun_glow=0.9, rays=0.9, mist=0.25,
                   haze_color="#22306e", mist_color="#26336e", milky=1.0, stars=1.0),
    mist=dict(base="night", dust=0.35, bokeh=0.25, sky_mid="#11205a", sky_hor="#33488f", sun_az=180.0, sun_el=0.9, sun_color="#ffe0b0",
              sun_int=0.55, sun_size=0.8, rays=0.5, mist=0.85, mist_height=1.6, mist_color="#33488f",
              haze=0.8, haze_color="#2b3d84", stars=0.8, milky=0.5),
    canopy=dict(base="night", dust=0.35, bokeh=0.25, sky_mid="#1a1850", sky_hor="#4a3270", sun_az=180.0, sun_el=1.2, sun_color="#ffc880",
                sun_int=0.7, sun_size=0.8, rays=0.8, mist=0.35, mist_color="#3a2c6a", haze_color="#3a2c6a",
                stars=0.9, milky=0.6),
    high=dict(base="night", dust=0.35, bokeh=0.25, sky_top="#050a2e", sky_mid="#16307a", sky_hor="#6a5a9e", sun_az=180.0, sun_el=0.6,
              sun_color="#ffd0a0", sun_int=0.7, sun_size=0.8, rays=0.5, mist=0.3, mist_color="#3a4890",
              haze_color="#4a4a8e", stars=0.9, milky=1.0),
    loom=dict(base="night", dust=0.35, bokeh=0.25, sky_top="#04082a", sky_mid="#1f3a8c", sky_hor="#9a6aa8", sun_az=180.0, sun_el=0.8,
              sun_color="#ffd6a8", sun_int=0.7, sun_size=0.8, rays=0.6, mist=0.25, mist_color="#40509a",
              haze_color="#6a5aa0", stars=0.8, milky=0.7),
    hush=dict(base="night", dust=0.35, bokeh=0.25, sky_top="#081040", sky_mid="#2a3f8a", sky_hor="#c0809c", sun_az=180.0, sun_el=-0.4,
              sun_color="#ffe2c0", sun_int=0.55, sun_size=0.9, rays=0.3, mist=0.3, mist_color="#6a5a90",
              haze_color="#a07090", stars=0.55, milky=0.3, ripple=0.05),
    veildawn=dict(base="sunrise", sky_top="#08113e", sky_mid="#262a70", sky_hor="#d8707a", sun_az=180.0,
                  sun_el=-0.6, sun_color="#ffc8a0", sun_int=0.55, sun_size=1.0, sun_disc=0.0, sun_glow=0.3, rays=0.4,
                  stars=0.35, milky=0.0, mist=0.3, mist_color="#6a4a78", haze=0.35, haze_color="#7a4a78",
                  ripple=0.2, exposure=0.95, dust=0.3, bokeh=0.2, clouds=0.25),
    veilsun=dict(base="sunrise", sky_top="#0a1748", sky_mid="#363680", sky_hor="#e8806e", sun_az=180.0,
                 sun_el=1.0, sun_color="#ffd9a8", sun_int=0.75, sun_size=1.0, sun_disc=5.0, sun_glow=0.3, rays=0.7,
                 stars=0.2, milky=0.0, mist=0.3, mist_color="#8a5a78", haze=0.35, haze_color="#9a5a7a", ripple=0.25,
                 exposure=0.93, dust=0.3, bokeh=0.2, clouds=0.3),
    veilgold=dict(base="golden", sky_top="#16337e", sky_mid="#5d6cb8", sky_hor="#f2b08c", sun_az=180.0, sun_el=6.0,
                  rays=0.55, haze_color="#c89a90", mist_color="#c8a0a0"),
    veilday=dict(base="day", sun_az=180.0, sun_el=14.0, rays=0.25),
)
WORLD = WORDS.world(dict(
    looks=LOOKS,
    look=[(0.0, "veilnight"), (S[1], "mist", 0.0), (S[2], "canopy", 0.0), (S[3] + 0.8, "high", 1.6),
          (S[4], "loom", 0.0), (S[5], "veilnight", 0.0), (S[6], "hush", 0.0), (BIG, "veildawn", 0.6), (46.0, "veilsun", 1.4),
          (51.0, "veilgold", 2.5), (53.6, "veilday", 2.6)],
    arch=dict(lit=[50.6 + 0.16 * k for k in range(9)], span=26.0, height=15.0, z=ARCH_Z,
              line=Track([(0.0, 0.0), (50.4, 0.0), (52.0, 1.0)])),
    exposure=Track([(0.0, 1.0), (LAST - 0.1, 1.0), (LAST + 0.15, 1.16), (LAST + 1.0, 1.0), (TOTAL, 1.0)]),
    react=dict(beat=0.4, level=0.3),
))

P3D = dict(
    camera=CAMERA,
    world=WORLD,
    setup=_setup,
    bursts=[dict(t=S[1], strength=1, rise=0.06, fall=0.45, color="#ffe6b8", radius=0.24),
            dict(t=S[2], strength=1, rise=0.06, fall=0.45, color="#ffd9a0", radius=0.24),
            dict(t=S[4], strength=1, rise=0.06, fall=0.45, color="#ffe6b8", radius=0.24),
            dict(t=S[5], strength=1, rise=0.06, fall=0.45, color="#fff0d0", radius=0.24),
            dict(t=BIG, strength=0.9, rise=0.08, fall=0.8, color="#ffe0c8", radius=0.20,
                 at=tuple(M(BIG) + np.array([0.0, 1.0, -260.0]))),
            dict(t=LAST, strength=0.5, rise=0.08, fall=0.8, color="#fff6e8", radius=0.3)],
)
