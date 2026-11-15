"""THE WORDS THAT BRING PEACE: the masterpiece. A 60 second promo for the Healing Concert "The Words of Mother's
Love That Bring Peace" (Sunday, December 6, 4:30 PM, World Mission Society Church of God, Las Vegas), on the
concert medley (audio/promo/concert-medley.mp3), built on the 3D layer (engine/p3d; UPGRADE-HOWTO sections V,
W, X, X2, Y). Approved treatment: scratchpad MASTER-TREATMENT.md.

THE IDEA
  Heavenly Mother's words of love fall from heaven as light. Wherever a word lands, light, colour and peace
  bloom: in people, in nature, across the whole world, until the Earth itself glows and settles between two
  hearts as the logo. Heavenly Mother appears only as hands of light: her open hands release the first word
  at the start, and cradle the glowing world at the end.

THE JOURNEY (the medley's sections: 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, the breath 40.21 to 42.51, the
biggest hit 42.51, the finale 49.47, the final hit 58.11)
  0.00   The opening title over a vast twilight sky above a sea of glowing clouds; Mother's hands of light
         hold a drop of gold. They open; the drop falls; we dive with it through the clouds; it lands on a
         still sea of light (6.15) and a ring of gold races to the horizon.
  6.84   GREETING: a gold man lays a hand on a crystal woman's shoulder; she turns, lights up and greets him.
         GRATITUDE: a gold woman bows, her hand on her heart, as golden light pours down on her.
  13.30  APOLOGY: in a soft rain of light a gold man kneels by a crystal woman who kneels alone, head bowed,
         and lays his hand on her shoulder. INCLUSIVENESS: they rise into an embrace; the sun rises behind
         them and the rain turns to warm sparks.
  19.85  The bass slams in: we surge along a river of light. CONCESSION: at a doorway of light a crystal man
         steps aside with an open palm; petals of light stream through. We fly through the door: RESPECT,
         two seated under a tree of light lean in to listen.
  26.79  ENCOURAGEMENT: under a cathedral of falling light one kneels in prayer, another lays a hand on her
         shoulder; hundreds of lights rise round them.
  33.36  Nine rivers of coloured light sweep across the sky. CONSIDERATION: a hand reaches down and lifts
         someone up. COMPLIMENT: a joyful twirl bursts into hearts; a crowd of light applauds.
  40.21  The breath: stillness; "December 6" written in light across the sky (TITLES date_light).
  42.51  The date bursts; we launch upward through golden clouds lit from within, the nine colours spiralling
         up with us, into a radiant sky.
  49.47  The whole Earth, luminous: hearts in the nine colours bloom across the continents, joined by arcs of
         light; Mother's hands of light cradle the world. At the peak (54.3 to 55) it settles between two
         hearts and becomes the logo; the light blooms into a soft pastel day; the end card (55 to 60).

HOUSE RULES: people only in the two radiant looks (crystal light, warm gold glitter), whole, few, tender,
acted, with living hands; Heavenly Mother only as hands of light; all nine expressions by name from
words.EXPRESSIONS (exact wording, website colours), each read 2.5 s or more, one at a time, never mirrored;
nothing dark behind text; no white-outs; frame 0 striking; no fade to black.
"""
import numpy as np

import songs.s03_original as _base

TOTAL = 60.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 59.6
_base.SONG_END = 60.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])          # no fade in, no fade out
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9                     # the nine are particle words in 3D
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.camera import Move, Rig, fly  # noqa: E402
from p3d import master_sky as MS  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))  # noqa: F405
MUSIC_END = 59.6
SONG_END = 60.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0           # nothing dark behind any text
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

SEC = [0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47]
BREATH_END = 42.51
FINAL_HIT = 58.11
LAND_T = 6.15               # the drop touches the sea (a bar start of the first song)
RELEASE_T = 2.50            # Mother's hands let the drop go (a hit)

# the nine colours of the campaign website (words.COLORS); a lighter glow for the deep ones
COL = dict(PW.COLORS)
GLOWC = dict(COL, Respect="#8a9cff", Compliment="#6f86d8")
NINE = [COL[k] for k in PW.LABELS]
NINE_GLOW = [GLOWC[k] for k in PW.LABELS]

# The two radiant looks. Until STYLES delivers crystal_light (coordinator), both are warm gold glitter: a deep
# gold, and a lighter gold for the second person of a pair, so the two stay apart.
GOLD = dict(look="glitter", color="#f2a640", color2="#ffdc96", bright=1.45)
CRYSTAL = dict(look=dict(name="glitter", seams=0.6), color="#ffc664", color2="#fff0c8", bright=1.45)


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _unit(a):
    a = np.asarray(a, np.float64)
    return a / max(float(np.linalg.norm(a)), 1e-9)


def ss(a, b, x):
    return MS.ss(a, b, x)


def sc(a, b, x):
    return MS.sc(a, b, x)


def lerp(a, b, u):
    return np.asarray(a, np.float64) * (1.0 - u) + np.asarray(b, np.float64) * u


UP = _v(0.0, 1.0, 0.0)


def _pchip_1d(x, y):
    """Monotone cubic slopes (Fritsch and Carlson): no overshoot between keys."""
    h = np.diff(x)
    d = np.diff(y) / h
    m = np.zeros_like(y)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(y) - 1):
        if d[i - 1] * d[i] <= 0.0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    return m


def _pchip(keys):
    """A camera path through keys [(t, pos, target), ...] with no overshoot: f(t) -> (pos, target)."""
    ts = np.array([k[0] for k in keys], np.float64)
    P = np.array([np.r_[k[1], k[2]] for k in keys], np.float64)       # (K, 6)
    M = np.stack([_pchip_1d(ts, P[:, j]) for j in range(6)], 1)

    def f(t):
        if t <= ts[0]:
            v = P[0]
        elif t >= ts[-1]:
            v = P[-1]
        else:
            i = int(np.searchsorted(ts, t, side="right") - 1)
            h = ts[i + 1] - ts[i]
            u = (t - ts[i]) / h
            h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
            h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
            v = h00 * P[i] + h10 * h * M[i] + h01 * P[i + 1] + h11 * h * M[i + 1]
        return v[:3], v[3:]
    return f


class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


# =============================================================================================================
# GEOGRAPHY (metres, y up, the sea of light is y = 0; the light of dawn lies toward -z)
# =============================================================================================================
D0 = _v(0.0, 0.0, 7.6)                  # where the drop lands
H0 = _v(0.0, 50.75, 7.6)                # Mother's cupped hands, high above it
HAND_S = 5.0                            # their scale (hands of light, larger than life)
C0 = _v(0.0, 51.45, 10.9)              # frame 0's camera, in front of the hands
P1 = _v(-2.4, 0.0, -6.0)               # Greeting: the pair
P1b = _v(3.6, 0.0, -9.5)               # Gratitude: the gold woman under the pouring light
P2 = _v(0.0, 0.0, -40.0)               # Apology and Inclusiveness: the two kneeling in the rain, then the embrace
P3 = _v(2.0, 0.0, -96.0)               # Concession: the doorway of light on the river
P3b = _v(2.0, 0.0, -114.0)             # Respect: the tree of light beyond the door
P4 = _v(-60.0, 0.0, -170.0)            # Encouragement: the cathedral of falling light
P5 = _v(60.0, 0.0, -230.0)             # Consideration
P5b = _v(66.0, 0.0, -238.0)            # Compliment: the dancer and the crowd of light
A7 = _v(66.0, 0.0, -262.0)             # the axis of the ascent
EARTH_Y = 230.0                        # the finale stands high above the clouds


def drop_pos(t):
    """The drop: held in the palms, released on the hit, falling (slowly at first) to the sea at LAND_T."""
    hold = H0 + _v(0.0, 0.10 * HAND_S * 0.5, 0.0) + _v(0.0, 0.015 * np.sin(1.3 * t), 0.0)
    if t <= RELEASE_T:
        return hold
    u = min((t - RELEASE_T) / (LAND_T - RELEASE_T), 1.0)
    y = float(hold[1]) * (1.0 - u * u)
    return _v(float(hold[0]), y, float(hold[2]))


# =============================================================================================================
# THE CAMERA
# =============================================================================================================
def _s0(t):
    """Frame 0 to the landing: hold on the hands under the title, tilt down after the falling drop, dive with
    it through the clouds and level out over the sea as it lands."""
    look0 = _v(0.0, 54.2, -40.0)            # looking a little up: the title stands on the deep sky
    if t < 2.9:
        return C0 + _v(0.0, 0.02 * t, -0.03 * t), look0
    d = drop_pos(t)
    u = sc(2.9, 3.9, t)                                    # the gaze turns down to the drop
    look = lerp(look0, d, u)
    v = sc(3.5, 6.0, t)                                    # and the camera dives after it
    pos = lerp(C0 + _v(0.0, 0.02 * t, -0.03 * t), d + _v(1.2, 4.0, 10.0), v * v * (3 - 2 * v))
    w = sc(5.6, 6.6, t)                                    # pulls out level over the sea
    end = D0 + _v(3.0, 1.7, 15.0)
    pos = lerp(pos, end + _v(0.0, 0.0, -1.5 * max(t - 6.6, 0.0)), w)
    look = lerp(look, D0 + _v(0.0, 0.6, 0.0), sc(5.4, 6.4, t))
    return pos, look


def _cam_keys_s1():
    a = P1 + _v(0.0, 1.45, 0.0)
    b = P1b + _v(0.0, 1.50, 0.0)
    return [(6.84, D0 + _v(2.6, 1.7, 13.4), D0 + _v(-1.0, 0.8, -4.0)),
            (7.7, P1 + _v(0.25, 1.62, 2.5), a),                     # half figures, both in profile
            (9.9, P1 + _v(0.05, 1.60, 2.0), a + _v(0.0, 0.02, 0.0)),
            (10.75, P1b + _v(-0.75, 1.55, 2.5), b),
            (13.0, P1b + _v(-0.55, 1.50, 2.05), b + _v(0.0, -0.03, 0.0))]


def _cam_keys_s2():
    c = P2 + _v(0.0, 0.95, 0.0)
    e = P2 + _v(0.0, 1.30, 0.0)
    return [(13.3, P1b + _v(-0.5, 1.8, 2.2), P1b + _v(0.0, 1.3, -4.0)),
            (14.4, P2 + _v(0.3, 0.75, 3.0), c),                      # low, looking up at them and the storm of light
            (16.6, P2 + _v(0.2, 0.72, 2.5), c + _v(0.0, 0.05, 0.0)),
            (18.2, P2 + _v(1.75, 1.85, 2.75), e + _v(0.0, -0.1, 0.0)),
            (19.6, P2 + _v(1.45, 1.80, 2.4), e + _v(0.0, -0.05, -0.6))]


RIVER = [P2 + _v(0.0, 0.0, -1.0), P2 + _v(1.5, 0.0, -14.0), P2 + _v(-2.0, 0.0, -30.0), P2 + _v(1.0, 0.0, -44.0),
         P3 + _v(0.0, 0.0, 3.0), P3 + _v(0.0, 0.0, -4.0), P3b + _v(-0.5, 0.0, 1.5), P3b + _v(-3.0, 0.0, -10.0),
         P3b + _v(4.0, 0.0, -40.0), P3b + _v(-6.0, 0.0, -90.0), P3b + _v(10.0, 0.0, -180.0),
         P3b + _v(-10.0, 0.0, -420.0), P3b + _v(30.0, 0.0, -900.0)]


def _cam_keys_s3():
    door = P3 + _v(0.3, 1.5, 0.0)
    tree = P3b + _v(0.0, 0.85, 0.0)
    return [(19.85, P2 + _v(0.2, 1.4, 2.8), P2 + _v(0.0, 1.0, -6.0)),
            (20.25, P2 + _v(0.6, 1.6, -12.0), P2 + _v(0.0, 1.2, -40.0)),
            (20.75, P3 + _v(-1.2, 1.5, 11.0), door),
            (21.4, P3 + _v(-0.9, 1.60, 6.6), door + _v(-0.7, -0.15, 0.0)),
            (23.3, P3 + _v(-0.6, 1.60, 5.4), door + _v(-0.5, -0.15, -1.0)),
            (23.85, P3 + _v(0.0, 1.55, 0.5), P3 + _v(0.0, 1.4, -8.0)),
            (24.5, P3b + _v(-3.3, 1.40, 1.9), tree),
            (26.6, P3b + _v(-2.7, 1.32, 1.5), tree + _v(0.0, 0.05, 0.0))]


def _cam_keys_s4():
    c = P4 + _v(0.0, 0.95, 0.0)
    return [(26.79, P4 + _v(0.3, 0.55, 34.0), P4 + _v(0.0, 18.0, -16.0)),   # vast: tiny people under the light
            (28.4, P4 + _v(0.5, 0.80, 17.0), P4 + _v(0.0, 7.0, -6.0)),
            (29.6, P4 + _v(0.85, 1.25, 2.9), c + _v(0.0, 0.05, 0.0)),        # close: the hand on the shoulder
            (31.3, P4 + _v(0.95, 1.22, 2.45), c),
            (33.36, P4 + _v(2.6, 2.4, 6.0), c + _v(0.0, 7.0, -6.0))]


def _cam_keys_s5():
    g = P5 + _v(0.0, 0.85, 0.0)                     # where the two hands meet
    d = P5b + _v(0.0, 1.25, 0.0)
    return [(33.36, P5 + _v(-9.0, 24.0, 26.0), P5 + _v(0.0, 2.0, -12.0)),     # high over the sea, the nine rivers
            (34.45, P5 + _v(-1.0, 1.45, 2.4), g),                             # down to the hands
            (36.6, P5 + _v(-0.7, 1.30, 1.85), g + _v(0.0, 0.15, 0.0)),
            (37.3, P5b + _v(-1.7, 1.55, 3.6), d),
            (40.0, P5b + _v(-1.0, 1.60, 3.0), d + _v(0.0, 0.1, 0.0))]


def _s6(t):
    """The breath: still, the camera drifts back and the gaze lifts to the sky where the date is written."""
    u = sc(40.0, 42.4, t)
    p0, q0 = P5b + _v(-1.1, 1.65, 4.6), P5b + _v(0.0, 1.35, 0.0)
    p1, q1 = P5b + _v(-0.6, 1.8, 9.5), P5b + _v(0.0, 4.5, -12.0)
    return lerp(p0, p1, u), lerp(q0, q1, u)


ASC0 = BREATH_END
ASC1 = SEC[7]


def _climb(t):
    u = max(t - ASC0, 0.0)
    return 2.0 + 3.0 * u + 3.6 * u * u          # 2 m to about 195 m at 49.47


def _s7(t):
    """The ascent: a corkscrew up round the column of light, through golden clouds lit from within, out into a
    radiant sky."""
    u = max(t - ASC0, 0.0)
    a = np.radians(200.0 + 52.0 * u + 4.0 * u * u)
    r = 14.0 + 4.0 * np.exp(-u / 0.6)
    y = _climb(t)
    p = A7 + _v(np.sin(a) * r, y, np.cos(a) * r)
    look = A7 + _v(0.0, y + 1.5 + 2.5 * sc(ASC0, ASC0 + 1.5, t), 0.0)
    tilt = sc(46.4, 48.8, t)
    ahead = A7 + _v(0.0, y + 7.0, 0.0)              # across the column (the nine colours) into the radiant sky
    return p, lerp(look, ahead, tilt)


# ---- the finale: the Earth, the hands, the logo (built from where the logo will stand in the end card) -----
END_FOV = 50.0
END_PITCH = 4.0
CAM_END = _v(float(A7[0]), EARTH_Y, float(A7[2]) + 30.0)
LOGO_D = 60.0
EC_SCALE = 1.0                                        # TITLES end card scale (see TITLES below)
SLOT_Y = (48.0 + 85.0 - 540.0) * EC_SCALE / 1080.0 + 0.5   # the end card logo's middle, from the top
SLOT_H = 170.0 * EC_SCALE / 1080.0


def _end_basis():
    a = np.radians(END_PITCH)
    f = _v(0.0, np.sin(a), -np.cos(a))
    r = _v(1.0, 0.0, 0.0)
    return r, np.cross(r, f), f


def _logo_frame():
    r, u, f = _end_basis()
    th = np.tan(np.radians(END_FOV) * 0.5)
    c = CAM_END + LOGO_D * _unit(f + u * (0.5 - SLOT_Y) * 2.0 * th)
    h = SLOT_H * 2.0 * th * float(np.dot(c - CAM_END, f))
    n = _unit(CAM_END - c)
    return c, n, h


LOGO_C, LOGO_N, LOGO_H = _logo_frame()


# BRAND's logo geometry (p3d/brand.py, in logo units: 1.0 high, centred): the globe's centre and its coloured
# disc. Written out here so that this file imports with numpy only (the workflow's first job).
_RL = 1.0 / np.sqrt(2.0)
_A_H = 1.5 + _RL
GLOBE_XY = (-0.034 / _A_H, (1.462 - 0.5 * _A_H) / _A_H)
GLOBE_DISC = (0.725 - 0.050) / _A_H
LOGO_R = _v(1.0, 0.0, 0.0)
LOGO_U = _unit(np.cross(LOGO_N, LOGO_R))


def _globe_static():
    """The logo's globe in the world: where the Earth stands, so that it becomes the logo's globe."""
    return LOGO_C + LOGO_H * (GLOBE_XY[0] * LOGO_R + GLOBE_XY[1] * LOGO_U), GLOBE_DISC * LOGO_H


GC, RG = _globe_static()
EARTH_T0 = SEC[7]
HEARTS_T0, HEARTS_T1 = 50.1, 53.2
CRADLE = (50.2, 53.5)
LOGO_T0, LOGO_T1 = 53.75, 54.95       # the logo builds round the world
DAY_T = 54.55                         # the bloom into a pastel day
END_T = 56.0


def _s8(t):
    """Round the luminous Earth (it fills much of the picture), then back to frame the logo as it forms, then
    down to the end card's camera while the day blooms."""
    def orbit(x):
        u = sc(SEC[7] - 0.3, 53.4, x)
        d = RG * (6.5 - 2.4 * u)
        az = np.radians(-60.0 + 70.0 * u)
        el = np.radians(-11.0 + 8.0 * u)            # from a little below: the heavens behind the world
        return GC + d * (np.cos(el) * (np.cos(az) * LOGO_N + np.sin(az) * _v(1.0, 0.0, 0.0)) + np.sin(el) * UP), GC

    th = np.tan(np.radians(END_FOV) * 0.5)
    d1 = LOGO_H / (0.42 * 2.0 * th)
    p_logo = LOGO_C + d1 * LOGO_N
    end_tgt = CAM_END + 100.0 * _end_basis()[2]
    if t < 53.4:
        return orbit(t)
    if t < DAY_T + 0.2:
        e = sc(53.4, DAY_T + 0.2, t)
        p0, q0 = orbit(53.4)
        return lerp(p0, p_logo, e), lerp(q0, LOGO_C, e)
    e = sc(DAY_T + 0.2, END_T, t)
    return lerp(p_logo, CAM_END, e), lerp(LOGO_C, end_tgt, e)


def _rig(focus):
    def fo(default):
        return (lambda t: focus(t, default)) if focus is not None else "target"
    return Rig([
        Path(_s0, 0.0, SEC[1], fov=lambda t: 50.0 + 8.0 * sc(3.4, 5.4, t) - 6.0 * sc(5.6, 6.6, t), aperture=0.0,
             focus=fo(lambda t: drop_pos(t) if t < 6.2 else D0 + _v(0, 1.0, 0))),
        Path(_pchip(_cam_keys_s1()), SEC[1], SEC[2], blend=0.6, fov=46.0, aperture=0.012, focus=fo(lambda t: P1 + _v(0, 1.2, 0)
                                                                          if t < 10.2 else P1b + _v(0, 1.3, 0))),
        Path(_pchip(_cam_keys_s2()), SEC[2], SEC[3], blend=0.8, fov=44.0, aperture=0.012, focus=fo(P2 + _v(0, 0.9, 0))),
        Path(_pchip(_cam_keys_s3()), SEC[3], SEC[4], blend=0.35, fov=lambda t: 46.0 + 14.0 * sc(19.85, 20.1, t) * (1.0 - sc(20.3, 20.9, t)),
            aperture=0.01, focus=fo(lambda t: P3 + _v(0, 1.4, 0) if t < 23.7 else P3b + _v(0, 0.9, 0))),
        Path(_pchip(_cam_keys_s4()), SEC[4], SEC[5], blend=0.45, whip=True, fov=lambda t: 58.0 - 10.0 * sc(26.79, 28.4, t), aperture=0.01,
            focus=fo(P4 + _v(0, 1.0, 0))),
        Path(_pchip(_cam_keys_s5()), SEC[5], 40.0, blend=0.45, whip=True, fov=48.0, aperture=0.01,
            focus=fo(lambda t: P5 + _v(0, 1.0, 0) if t < 37.0 else P5b + _v(0, 1.1, 0))),
        Path(_s6, 40.0, BREATH_END, blend=0.6, fov=48.0, aperture=0.0),
        Path(_s7, BREATH_END, SEC[7], blend=0.35, fov=lambda t: 56.0 + 10.0 * sc(42.5, 43.3, t), aperture=0.0),
        Path(_s8, SEC[7], TOTAL + 1.0, blend=0.6, fov=END_FOV, aperture=0.0),
    ], blend=0.6, fov=48.0, aperture=0.0, handheld=0.12, min_height=0.4)


_LAYOUT = _rig(None)


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


# =============================================================================================================
# THE WORDS (all nine, by name; exact wording and colours from words.EXPRESSIONS; never mirrored; one at a time)
# =============================================================================================================
def _width(t, depth, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _dist(t, p):
    return float(np.linalg.norm(np.asarray(p, np.float64) - PW._cam_at(_LAYOUT, t).pos))


def _at(t, x, y, depth):
    """The world point seen at (x, y) of the picture (0..1, from the left and the bottom) `depth` metres away,
    at the middle of a reading moment (the words stand still in the world; the camera drifts gently)."""
    return place(t, x, y, depth)


def _w(expr, t_in, r0, r1, t_out, x, y, depth, frac, **kw):
    """A word that rides with the camera: it keeps its place in the picture (x, y from the left and the bottom)
    `depth` metres ahead of the lens whatever the camera does, `frac` of the picture's width wide."""
    tm = 0.5 * (r0 + r1)
    d = dict(expr=expr, ride=(x, y, depth), face="screen", width=_width(tm, depth, frac), t_in=t_in, t_read0=r0,
             t_read1=r1, t_out=t_out, leave="fade", pill=True)
    d.update(kw)
    return d


_REVEAL = dict(arrive="reveal", edge="right", soft=0.16, edge_glow=2.2)
_PEN = dict(arrive="pen", nib=False)

_SPECS = [
    _w("Greeting", 7.0, 7.6, 10.1, 10.35, 0.50, 0.80, 7.0, 0.30, **_REVEAL),
    _w("Gratitude", 10.4, 10.85, 13.35, 13.6, 0.50, 0.79, 7.0, 0.62, **_PEN),
    _w("Apology", 13.95, 14.45, 16.95, 17.15, 0.50, 0.79, 7.0, 0.54, **_REVEAL),
    _w("Inclusiveness", 17.15, 17.25, 19.75, 19.85, 0.50, 0.80, 7.0, 0.50, **_PEN),
    _w("Concession", 20.6, 21.0, 23.5, 23.7, 0.50, 0.80, 7.0, 0.42, **_REVEAL),
    _w("Respect", 23.95, 24.2, 26.7, 26.79, 0.50, 0.765, 7.0, 0.52, **_PEN),
    _w("Encouragement", 27.5, 28.0, 31.3, 31.6, 0.50, 0.79, 7.0, 0.58, **_REVEAL),
    _w("Consideration", 33.6, 34.1, 36.6, 36.85, 0.50, 0.79, 7.0, 0.52, **_PEN),
    _w("Compliment", 36.95, 37.4, 39.9, 40.15, 0.50, 0.765, 7.0, 0.48, **_REVEAL),
]


def _clean_leave(t, info):
    """Every word leaves in place and sharp, thinning out evenly: never smeared, drifting or broken letters."""
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)
    return None


WORDS = PW.Words(_SPECS, camera=_LAYOUT, reflect=False, drive=_clean_leave)


def _focus(t, default, ease=0.6):
    """Rack to the word being read only when it lies near the subject's depth; else keep the subject sharp (the
    words are sharp whatever the lens does)."""
    return np.asarray(default(t) if callable(default) else default, np.float64)


CAMERA = _rig(_focus)


# =============================================================================================================
# THE WORLD: heavenly looks, section by section (never dark, never cold)
# =============================================================================================================
LOOKS = dict(
    # above the sea of clouds at twilight: a deep blue-violet zenith, a band of gold and coral low down
    opening=dict(base="dawn", sky_top="#0d1250", sky_mid="#3a2e86", sky_hor="#e88a6a", sun_color="#ffc88a",
                 sun_int=0.7, sun_el=-1.5, sun_disc=0.0, sun_glow=0.65, stars=0.85, milky=0.4, clouds=0.0,
                 haze=0.65, haze_color="#c87a72", mist=0.35, mist_height=30.0, mist_color="#b0708a", hills=0.0,
                 water="#2a1838", mirror=0.6,
                 ripple=0.2, rays=0.25, dust=0.3, dust_color="#ffe0a8", dust_color2="#ffc0c8", bokeh=0.3,
                 keep_hue=0.8),
    # the sea of light: deep and clear, the warm light of the dawn off to one side
    shore=dict(base="dawn", sky_top="#0b1046", sky_mid="#2a2470", sky_hor="#b8625e", sun_color="#ffc890",
               sun_int=0.7, sun_el=-1.5, sun_disc=0.0, sun_glow=0.6, stars=0.75, milky=0.35, clouds=0.25,
               haze=0.3, haze_color="#7a4a6a", mist=0.12, mist_color="#6a4a7a", hills=0.0, water="#070818",
               mirror=1.0, ripple=0.25, rays=0.3, dust=0.6, dust_color="#ffe0a8", dust_color2="#ffc0c8",
               bokeh=0.6, keep_hue=0.8),
    rain=dict(base="dusk", sky_top="#0a0c3a", sky_mid="#28226a", sky_hor="#9a5a7a", sun_color="#ffb8a0",
              sun_int=0.45, sun_el=-3.5, sun_disc=0.0, sun_glow=0.7, stars=0.6, milky=0.3, clouds=0.35,
              haze=0.3, haze_color="#5a3a6a", mist=0.25, mist_color="#4a3a6a", hills=0.0, water="#060716",
              mirror=1.0, ripple=0.35, rays=0.05, dust=0.4, dust_color="#e8e8ff", dust_color2="#ffd0d8",
              bokeh=0.5, keep_hue=0.8),
    # the embrace: the dawn breaks to the side, a warm amber glow over the sea
    sunrise=dict(base="sunrise", sky_top="#0c1048", sky_mid="#3c2670", sky_hor="#d8703e", sun_color="#ffb860",
                 sun_int=0.55, sun_el=0.5, sun_disc=2.0, sun_glow=0.45, stars=0.4, milky=0.15, clouds=0.3,
                 haze=0.22, haze_color="#8a4a4a", mist=0.12, mist_color="#6a4060", hills=0.0, water="#080716",
                 mirror=1.0, ripple=0.25, rays=0.35, dust=0.6, dust_color="#ffe2a8", dust_color2="#ffcfa8",
                 bokeh=0.6, keep_hue=0.8, exposure=0.9),
    river=dict(base="sunrise", sky_top="#0e1254", sky_mid="#3e2c80", sky_hor="#f09a5a", sun_color="#ffd090",
               sun_int=0.75, sun_el=2.0, sun_disc=2.5, sun_glow=0.55, stars=0.3, milky=0.1, clouds=0.35,
               haze=0.3, haze_color="#9a5a5a", mist=0.1, mist_color="#8a5a6a", hills=0.0, water="#0a0a1c",
               mirror=1.0, ripple=0.3, rays=0.4, dust=0.6, dust_color="#ffe6b0", dust_color2="#ffd0b0",
               bokeh=0.6, keep_hue=0.8, exposure=0.92),
    cathedral=dict(base="dusk", sky_top="#080a34", sky_mid="#241c62", sky_hor="#b0606a", sun_color="#ffcf8a",
                   sun_int=0.5, sun_el=-2.0, sun_disc=0.0, sun_glow=0.6, stars=0.9, milky=0.6, clouds=0.2,
                   haze=0.3, haze_color="#5a3a6a", mist=0.25, mist_color="#4a3a6a", hills=0.0, water="#060616",
                   mirror=1.0, ripple=0.2, rays=0.15, dust=0.7, dust_color="#ffe2a8", dust_color2="#e0c8ff",
                   bokeh=0.7, keep_hue=0.8),
    rivers=dict(base="predawn", sky_top="#080a3a", sky_mid="#22206a", sky_hor="#a05a80", sun_color="#ffc0a0",
                sun_int=0.45, sun_el=-3.0, sun_disc=0.0, sun_glow=0.7, stars=1.0, milky=0.8, clouds=0.12,
                haze=0.3, haze_color="#4a3a72", mist=0.15, mist_color="#4a3a7a", hills=0.0, water="#060618",
                mirror=1.0, ripple=0.2, rays=0.0, dust=0.6, dust_color="#ffe2a8", dust_color2="#c8d0ff",
                bokeh=0.6, keep_hue=0.8),
    breath=dict(base="predawn", sky_top="#070a36", sky_mid="#1e1e62", sky_hor="#8a5a86", sun_color="#ffc0a0",
                sun_int=0.4, sun_el=-3.5, sun_disc=0.0, sun_glow=0.7, stars=1.0, milky=0.9, clouds=0.0,
                haze=0.3, haze_color="#3e3a72", mist=0.12, mist_color="#3e3a7a", hills=0.0, water="#050616",
                mirror=1.0, ripple=0.05, rays=0.0, dust=0.4, dust_color="#ffe2a8", dust_color2="#c8d0ff",
                bokeh=0.4, keep_hue=0.8),
    ascent=dict(base="sunrise", sky_top="#121c66", sky_mid="#4c3a8a", sky_hor="#f0a060", sun_color="#ffd890",
                sun_int=0.8, sun_el=5.0, sun_disc=3.0, sun_glow=0.55, stars=0.2, milky=0.0, clouds=0.25,
                haze=0.3, haze_color="#b07a6a", mist=0.0, hills=0.0, water="#100c24", mirror=0.8,
                rays=0.6, dust=0.5, dust_color="#fff0d0", dust_color2="#ffe0b0", bokeh=0.4, keep_hue=0.8,
                exposure=0.92),
    radiant=dict(base="golden", sky_top="#1e48a8", sky_mid="#5e86d0", sky_hor="#ffcf9a", sun_color="#fff0d0",
                 sun_int=0.75, sun_el=12.0, sun_disc=2.5, sun_glow=0.55, stars=0.0, milky=0.0, clouds=0.2,
                 haze=0.35, haze_color="#e0c0a0", mist=0.0, hills=0.0, water="#1a2448", rays=0.45, dust=0.4,
                 dust_color="#fff4dc", dust_color2="#ffe0b0", bokeh=0.3, keep_hue=0.8, exposure=0.9),
    heaven=dict(base="night", sky_top="#060a30", sky_mid="#121a5a", sky_hor="#3a3486", sun_color="#c8b8ff",
                sun_int=0.0, sun_el=40.0, sun_disc=0.0, stars=1.0, milky=0.9, clouds=0.0, haze=0.2,
                haze_color="#3a3a86", mist=0.0, hills=0.0, water="#060820", mirror=0.4, rays=0.0, dust=0.15,
                bokeh=0.15, keep_hue=0.8),
    pastel=dict(base="cream", sky_top="#8ec0ec", sky_mid="#efdcd6", sky_hor="#fbd8c4", mist=0.2,
                mist_color="#f6dcd2", haze_color="#efd8cc", clouds=0.25, dust=0.3, rays=0.0, sun_el=40.0,
                sun_disc=0.0, hills=0.0, water="#98bce0", keep_hue=0.8, exposure=0.92),
)

LOOK_KEYS = [(0.0, "opening"), (5.6, "shore", 1.6), (SEC[2], "rain", 1.4), (17.6, "sunrise", 2.2),
             (SEC[3], "river", 0.6), (SEC[4], "cathedral", 0.0), (SEC[5], "rivers", 0.0), (SEC[6], "breath", 1.2),
             (43.6, "ascent", 1.6), (47.4, "radiant", 1.6), (SEC[7] + 0.4, "heaven", 1.2), (DAY_T + 0.5, "pastel", 1.0)]

STAGES = [(6.4, P1), (10.3, P1b), (13.3, P2), (20.3, P3), (23.8, P3b), (26.79, P4), (33.36, P5), (36.9, P5b)]


def _calm(t):
    """A calm disc of clean mirror under the people of the moment (the sparkle carpet stays away from them)."""
    c = STAGES[0][1]
    for t0, p in STAGES:
        if t >= t0 - 0.3:
            c = p
    return [dict(center=(float(c[0]), float(c[2])), radius=6.0, soft=4.0, ripple=0.0, mirror=0.75)]


WORLD = dict(
    looks=LOOKS,
    calm=_calm,
    look=LOOK_KEYS,
    sun_az=228.0,              # the dawn lies ahead and to the left: its glow never stands behind the people
    lanterns=0.0,
    arch=None,
    react=dict(beat=0.3, level=0.2),
)


def _shaft(segs, radius=1.0, color="#ffd89a", top=26.0):
    """One of the world's four shafts of light, moved from place to place over time: segs is a list of
    (place, t0, t1, strength); it fades in and out at each."""
    segs = sorted(segs, key=lambda s: s[1])

    def which(t):
        best = segs[0]
        for sg in segs:
            if t >= sg[1] - 1.0:
                best = sg
        return best

    def base(t):
        p = which(t)[0]
        return (float(p[0]), float(p[2]))

    def strength(t):
        p, t0, t1, k = which(t)
        return k * sc(t0, t0 + 0.8, t) * (1.0 - sc(t1 - 0.5, t1, t))
    return dict(base=base, radius=radius, top=top, spread=-0.4, color=color, strength=strength)


# =============================================================================================================
# THE CAST (built when the scene is set up: the workflow's first job imports this file with numpy only)
# =============================================================================================================
_CAST = {}


def _view(at, cam_pos):
    d = np.asarray(cam_pos, np.float64) - np.asarray(at, np.float64)
    return float(np.degrees(np.arctan2(d[0], d[2])))


def _mother_hands():
    """Heavenly Mother's hands of light (never more of her): held out toward us, cupped together, palms up,
    holding the drop; on the release they part a little and tip forward, and the drop slips away."""
    from p3d.body import Body
    out = []
    for j, side in enumerate(("L", "R")):
        sg = -1.0 if side == "L" else 1.0          # L: the hand on the picture's left (fingers toward us)

        def at(t, sg=sg, j=j):
            o = sc(RELEASE_T - 0.25, RELEASE_T + 0.6, t)
            return H0 + _v(sg * (0.034 + 0.05 * o) * HAND_S, -0.03 * HAND_S * o, 0.0) + \
                _v(0.0, 0.004 * HAND_S * np.sin(1.1 * t + j), 0.0)
        aim = _unit(_v(sg * 0.18, 0.12, 1.0))       # fingers toward the camera, a little apart
        palm = _unit(_v(-sg * 0.30, 1.0, 0.45))     # palms up, turned a little toward us and toward each other
        out.append(Body("woman", part="arm." + ("R" if side == "L" else "L"), look="glitter", color="#ffcc6a",
                        color2="#fff0c8", bright=1.7, points=80000, scale=HAND_S, show=(-1.0, 4.6), fade=0.8,
                        seed=3.0 + j,
                        effects=[dict(kind="shed", t=-1.0, n=3000, life=2.0, speed=0.15, rise=0.25, spread=0.05)],
                        hand=dict(side=("R" if side == "L" else "L"), at=at, aim=aim, palm=palm, pose="cup",
                                  anchor="palm")))
    return out


def _cradle_hands():
    """Mother's hands of light again in the finale: they rise under the world and cradle it (fingertips toward
    us, the arms going away behind it), then open and fade before the logo forms."""
    from p3d.body import Body
    out = []
    S = RG * 2.4 / 0.24
    for j, side in enumerate(("L", "R")):
        sg = -1.0 if side == "L" else 1.0

        def at(t, sg=sg):
            up = sc(CRADLE[0], CRADLE[0] + 1.4, t)
            op = sc(CRADLE[1] - 0.5, CRADLE[1] + 0.3, t)
            return GC + LOGO_R * sg * (0.034 + 0.05 * op) * S - LOGO_U * RG * (1.15 + 1.4 * (1.0 - up)) + \
                LOGO_N * 0.35 * RG
        aim = _unit(sg * 0.18 * LOGO_R + 0.12 * LOGO_U + 1.0 * LOGO_N)
        palm = _unit(-sg * 0.30 * LOGO_R + 1.0 * LOGO_U + 0.45 * LOGO_N)
        hand_side = "R" if side == "L" else "L"
        out.append(Body("woman", part="arm." + hand_side, look="glitter", color="#ffcc6a", color2="#fff0c8",
                        bright=1.6, points=80000, scale=S, show=(CRADLE[0] - 0.3, CRADLE[1] + 0.5), fade=0.6,
                        seed=7.0 + j,
                        effects=[dict(kind="shed", t=CRADLE[0], n=3000, life=2.0, speed=0.12, rise=0.2,
                                      spread=0.05)],
                        hand=dict(side=hand_side, at=at, aim=aim, palm=palm, pose="cup", anchor="palm")))
    return out


def _embrace_pair(o, t_rise, t_hold, until):
    """APOLOGY then INCLUSIVENESS (two women, UPDATE 15): one kneels alone, head bowed; the other kneels beside
    her and lays a hand on her shoulder; they rise together and hold each other, cheek past shoulder (the
    engine's embrace). Life size, whole and luminous."""
    from p3d import pairs
    refs = {}
    gap, side = 0.34, 0.085
    d0 = 0.52
    # a faces +x (toward b), b faces -x; each stands a little to their own left (pairs.embrace's side)
    ka_k = (o[0] - d0, o[2] - side)
    ka_e = (o[0] - 0.5 * gap, o[2] - side)
    kb_k = (o[0] + d0, o[2] + side)
    kb_e = (o[0] + 0.5 * gap, o[2] + side)
    show = (SEC[2] - 0.4, until)

    def other(name, part, guess):
        return lambda tt: refs[name].where(tt, part, raw=True) if name in refs else np.asarray(guess, np.float64)
    a = dict(shape="woman", garment="dress", hair="bun",
             at=[(0.0, ka_k), (t_hold - 0.6, ka_k), (t_hold + 0.15, ka_e)],
             motion=[(-1e9, "kneel", dict(dur=0.01, one=True, hands="free")),
                     (t_rise, "rise", dict(dur=1.1, blend=0.1, one=True)),
                     (t_hold - 0.6, "shuffle"), (t_hold + 0.3, "stand")],
             gesture=[(14.2, t_rise - 0.1, "hand_on_shoulder",
                       dict(side="R", to=other("b", "shoulder.L", o + _v(0.3, 1.0, 0.0)))),
                      (14.6, t_rise, "bow", dict(amount=10.0))],
             points=75000, show=show, fade=0.6, seed=61.0, wind=(0.2, 0.0, -0.1), **GOLD)
    b = dict(shape="woman", garment="dress", hair=True,
             at=[(0.0, kb_k), (t_hold - 0.6, kb_k), (t_hold + 0.15, kb_e)],
             motion=[(-1e9, "kneel", dict(dur=0.01, sit=0.6, hands="lap")),
                     (t_rise + 0.15, "rise", dict(dur=1.1, blend=0.1)),
                     (t_hold - 0.6, "shuffle"), (t_hold + 0.3, "stand")],
             gesture=[(SEC[2] - 0.4, t_rise + 0.3, "bow", dict(amount=30.0))],
             points=75000, show=show, fade=0.6, seed=62.0, wind=(0.2, 0.0, -0.1), **CRYSTAL)
    A, B = pairs.embrace(t_hold, at=(o[0], o[2]), facing=90.0, a=a, b=b, until=until + 1.0, gap=gap,
                         approach=0.0, side=side)
    refs["a"], refs["b"] = A, B
    return A, B


def _greeting_pair(o, t0, t1):
    """GREETING (two men, UPDATE 15): they face each other and each gives a slight, warm bow, a gentle nod of
    the head and shoulders; no touch."""
    from p3d.body import Body
    a = Body("man", at=(o[0] - 0.55, o[2]), facing=90.0, garment="tunic", points=75000, show=(t0 - 1.0, t1 + 0.8),
             fade=0.6, seed=21.0,
             gesture=[(t0, t1 + 0.6, "bow", dict(amount=16.0, ease=0.9)),
                      (t0 + 0.9, t1 + 0.6, "nod", dict(period=2.2, amount=4.0))],
             sweeps=dict(glow=dict(t=t0 + 0.2, at="heart", speed=2.5, width=0.35, flash=1.6)), **GOLD)
    b = Body("man", at=(o[0] + 0.55, o[2]), facing=270.0, garment="coat", points=75000, show=(t0 - 1.0, t1 + 0.8),
             fade=0.6, seed=22.0,
             gesture=[(t0 + 0.35, t1 + 0.6, "bow", dict(amount=13.0, ease=0.9)),
                      (t0 + 1.2, t1 + 0.6, "nod", dict(period=2.4, amount=4.0))],
             sweeps=dict(glow=dict(t=t0 + 0.55, at="heart", speed=2.5, width=0.35, flash=1.6)), **CRYSTAL)
    return [a, b]


def _cast():
    if _CAST:
        return _CAST
    from p3d import acting
    C = _CAST
    C["hands0"] = _mother_hands()
    C["greeting"] = _greeting_pair(P1, 7.25, 10.1)
    cam1b = P1b + _v(-1.4, 1.5, 5.6)
    C["gratitude"] = acting.perform("Gratitude", 10.6, 13.4, at=(P1b[0], P1b[2]), view=_view(P1b, cam1b),
                                    variant="heart", style=dict(points=80000, **GOLD), pre=1.2, post=0.6, seed=3.0)
    C["embrace"] = list(_embrace_pair(P2, 16.75, 17.55, 20.15))
    cam3 = P3 + _v(-0.7, 1.55, 5.6)
    C["concession"] = acting.perform("Concession", 21.0, 23.6, at=(P3[0] - 1.25, P3[2] + 0.6),
                                     view=_view(P3, cam3), variant="after_you",
                                     style=dict(points=70000, **CRYSTAL), pre=1.4, post=0.4, seed=5.0)
    cam3b = P3b + _v(-3.0, 1.35, 1.7)
    C["respect"] = acting.perform("Respect", 24.2, 26.8, at=(P3b[0], P3b[2]), view=_view(P3b, cam3b),
                                  variant="listen", style=dict(points=65000), style_a=dict(CRYSTAL),
                                  style_b=dict(GOLD), pre=0.9, post=0.3, seed=6.0)
    cam4 = P4 + _v(1.2, 1.4, 3.9)
    C["encouragement"] = acting.perform("Encouragement", 27.6, 31.6, at=(P4[0], P4[2]), view=_view(P4, cam4),
                                        variant="shoulder", style=dict(points=70000),
                                        style_a=dict(GOLD, shape="woman"), style_b=dict(CRYSTAL, shape="woman"),
                                        pre=0.9, post=1.9, seed=7.0)
    cam5 = P5 + _v(-0.8, 1.3, 6.0)
    C["consideration"] = acting.perform("Consideration", 33.9, 36.9, at=(P5[0], P5[2]), view=_view(P5, cam5),
                                        variant="help_up", style=dict(points=70000),
                                        style_a=dict(GOLD, shape="man"), style_b=dict(CRYSTAL, shape="man"),
                                        pre=0.6, post=0.5, seed=8.0)
    cam5b = P5b + _v(-2.0, 1.55, 6.4)
    C["compliment"] = acting.perform("Compliment", 37.0, 40.0, at=(P5b[0], P5b[2]), view=_view(P5b, cam5b),
                                     variant="twirl", style=dict(points=75000, **CRYSTAL), pre=0.7, post=2.4,
                                     seed=9.0)
    C["cradle"] = _cradle_hands()
    return C


# =============================================================================================================
# THE SCENE
# =============================================================================================================
def _cloud_sea(rng, center, r0, r1, n, y, wmin, wmax, bright=1.0, hk=(0.35, 0.6)):
    out = []
    for _ in range(n):
        a = rng.uniform(0.0, 2.0 * np.pi)
        r = np.sqrt(rng.uniform(r0 * r0, r1 * r1))
        w = rng.uniform(wmin, wmax) * (0.7 + 0.6 * r / r1)
        out.append(dict(center=(center[0] + np.sin(a) * r, y + rng.uniform(-3.0, 5.0), center[2] + np.cos(a) * r),
                        width=w, height=w * rng.uniform(*hk), n=int(140 + 110 * w / 100.0),
                        towers=int(rng.integers(3, 7)), bright=bright))
    return out


OPENING_BOX = (0.15, 0.85, 0.40, 0.97)       # the opening lockup (TITLES opening at y 0.30), screen 0..1, y up


def _boxes(t, cam):
    """Screen boxes (x0, x1, y0, y1; y up) of every word on screen now, padded, and of the opening title."""
    out = []
    for w in WORDS:
        if w.t_in - 0.2 <= t <= w.t_out + 0.2:
            b = PW.screen_box(w, cam, t)
            if b[4]:
                out.append((b[0] - 0.035, b[1] + 0.035, b[2] - 0.04, b[3] + 0.04))
    if t < TITLES["opening"]["t_end"] + 0.3:
        out.append(OPENING_BOX)
    return out


class Clear:
    """Wraps a point set: its light goes out inside the screen box of every word on screen and of the opening
    title, so nothing crosses a word while it is read (lines and ribbons at both ends)."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner
        if hasattr(inner, "gain"):
            self.gain = inner.gain

    @staticmethod
    def _dim(pts, cam, boxes):
        xy, z = cam.project(np.asarray(pts, np.float64).reshape(-1, 3))
        f = np.ones(len(xy))
        for x0, x1, y0, y1 in boxes:
            e = 0.025
            inside = (ss(x0 - e, x0, xy[:, 0]) * (1.0 - ss(x1, x1 + e, xy[:, 0]))
                      * ss(y0 - e, y0, xy[:, 1]) * (1.0 - ss(y1, y1 + e, xy[:, 1])))
            f = np.minimum(f, 1.0 - inside * (z > 0))
        return f

    def sample(self, t, cam=None):
        ps = self.inner
        res = ps.sample(t, cam) if getattr(ps, "wants_camera", False) else ps.sample(t)
        if res is None or cam is None:
            return res
        boxes = _boxes(t, cam)
        if not boxes:
            return res
        out = []
        for b in (res if isinstance(res, (list, tuple)) else [res]):
            if b is None:
                continue
            b = dict(b)
            P = np.asarray(b["pos"], np.float64).reshape(-1, 3)
            f = self._dim(P, cam, boxes)
            if b.get("pos2") is not None:
                f2 = self._dim(np.asarray(b["pos2"], np.float64).reshape(-1, 3), cam, boxes)
                f = np.minimum(f, f2)
                b["alpha2"] = np.asarray(b.get("alpha2", b.get("alpha", 1.0)), np.float64) * f
            b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * f
            out.append(b)
        return out


def _gain(*keys):
    tr = Track(list(keys))
    return lambda t: float(tr(t))


def _setup(scene):
    from p3d.api import Mask
    from p3d import master_fx as FX
    from p3d import master_brand as MB
    rng = np.random.default_rng(2026)

    # ---- the sky's clouds: the sea of clouds at the start (we fall through it), far banks round the
    # horizon all the way, and the high golden layer we rise through
    near = _cloud_sea(rng, D0, 24.0, 300.0, 70, 22.0, 26.0, 60.0, 1.0)
    far = _cloud_sea(rng, _v(0.0, 0.0, -120.0), 650.0, 1600.0, 230, 14.0, 70.0, 140.0, 0.9, hk=(0.28, 0.45))
    high = _cloud_sea(rng, A7, 30.0, 900.0, 160, 118.0, 40.0, 110.0, 1.0)
    scene.add("clouds_near", MS.Billows(near, gain=_gain((0.0, 1.0), (5.6, 1.0), (7.4, 0.0), (60.0, 0.0)),
                                        seed=12, alpha=0.085), depth_of_field=False)
    scene.add("clouds_far", MS.Billows(far, gain=_gain((0.0, 1.0), (13.0, 1.0), (14.0, 0.0), (40.0, 0.0), (41.0, 0.45),
                                                       (42.6, 0.45), (43.4, 0.0), (60.0, 0.0)), seed=13,
                                       alpha=0.055, body=0.2, sun_az=WORLD["sun_az"]), depth_of_field=False)
    scene.add("clouds_high", MS.Billows(high, gain=_gain((0.0, 0.0), (42.4, 0.0), (43.2, 1.0), (49.3, 1.0),
                                                         (50.0, 0.0), (60.0, 0.0)), seed=14, alpha=0.09),
              depth_of_field=False)
    # S2: towering clouds of rose light over the rain
    storm = []
    for (x, z, w, h) in ((-70, -110, 80, 120), (-20, -160, 95, 150), (45, -125, 75, 110), (100, -170, 90, 140),
                         (-125, -70, 70, 100), (140, -90, 70, 95)):
        storm += MS.tower(rng, P2 + _v(x, 20.0, z), w, h, n_layer=4, per=260)
    scene.add("clouds_storm", MS.Billows(storm, gain=_gain((0.0, 0.0), (12.9, 0.0), (13.8, 1.0), (19.9, 1.0),
                                                           (20.4, 0.0), (60.0, 0.0)), seed=16, alpha=0.07,
                                         top="#ffc8dc", warm="#f090b0", rose="#c86aa0", lilac="#6a5ad0",
                                         core="#ffe0ec", sun_az=WORLD["sun_az"]), depth_of_field=False)
    # S3: a canyon of golden clouds along the river of light
    canyon = []
    for i, z in enumerate(np.arange(-60.0, -620.0, -48.0)):
        for side in (-1.0, 1.0):
            off = side * rng.uniform(48.0, 70.0) + side * 0.06 * abs(z)
            w = rng.uniform(42.0, 66.0) * (1.0 + 0.6 * abs(z) / 600.0)
            h = rng.uniform(60.0, 110.0) * (1.0 + 0.8 * abs(z) / 600.0)
            canyon += MS.tower(rng, _v(P3[0] + off, 2.0, P3[2] + 40.0 + z), w, h, n_layer=4, per=200)
    scene.add("clouds_canyon", MS.Billows(canyon, gain=_gain((0.0, 0.0), (19.3, 0.0), (19.85, 1.0), (26.6, 1.0),
                                                             (26.79, 0.0), (60.0, 0.0)), seed=17, alpha=0.065,
                                          sun_az=WORLD["sun_az"]), depth_of_field=False)
    # the ascent: columns of golden cloud standing round the column of light
    rise = []
    for i in range(10):
        a = 2.0 * np.pi * i / 10.0 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(34.0, 60.0)
        rise += MS.tower(rng, A7 + _v(np.sin(a) * r, 8.0 + rng.uniform(0, 30), np.cos(a) * r), rng.uniform(26, 40),
                         rng.uniform(120, 170), n_layer=5, per=200)
    scene.add("clouds_rise", MS.Billows(rise, gain=_gain((0.0, 0.0), (42.4, 0.0), (42.9, 1.0), (49.0, 1.0),
                                                         (49.6, 0.0), (60.0, 0.0)), seed=18, alpha=0.075,
                                        sun_az=WORLD["sun_az"]), depth_of_field=False)

    C = _cast()

    def addp(name, sets):
        for i, ps in enumerate(sets if isinstance(sets, (list, tuple)) else [sets]):
            if hasattr(ps, "add") and hasattr(ps, "mask"):
                ps.add(scene, "%s_%d" % (name, i), mask=False)
            else:
                scene.add("%s_%d" % (name, i), PW.KeepClear(ps, WORDS))

    # ---- S0: Mother's hands, the drop, the landing, the ring of gold
    addp("hands0", C["hands0"])
    scene.add("drop", FX.Drop(drop_pos, t_show=(-1.0, LAND_T + 0.2), t_land=LAND_T, scale=1.6), reflect=True)
    scene.add("splash", FX.Splash(D0, LAND_T, scale=1.0))
    scene.add("ring", FX.RingWave(D0, LAND_T, speed=36.0, reach=1500.0, until=SEC[3] + 0.5, color="#ffb24a",
                                  core="#ffd88a"))
    scene.add("motes0", FX.Motes(n=900, box=(14.0, 8.0, 14.0), center=None,
                                 gain=_gain((0.0, 0.6), (3.0, 0.6), (4.0, 0.0), (60.0, 0.0))), reflect=False)

    # ---- S1: the greeting and the bow of thanks under pouring light
    addp("greeting", C["greeting"])
    addp("gratitude", C["gratitude"])
    scene.add("pour", PW.KeepClear(FX.LightColumns([P1b], top=9.0, per=360, fall=2.2, ring=0.95, core=False,
                                                    spark=0.028, soft=True,
                                                    gain=_gain((0.0, 0.0), (10.3, 0.0), (11.0, 1.0), (13.6, 1.0),
                                                               (14.4, 0.0), (60.0, 0.0))), WORDS))
    scene.add("motes1", PW.KeepClear(FX.Motes(n=350, box=(18.0, 6.0, 18.0), center=(P1 + P1b) * 0.5 + _v(0, 3, 0),
                                              gain=_gain((0.0, 0.0), (6.4, 0.0), (7.2, 1.0), (13.6, 1.0),
                                                         (14.6, 0.0), (60.0, 0.0))), WORDS), reflect=False)

    # ---- S2: the rain of light, the two kneeling, the embrace, the sunrise
    def rain_tau(t):
        # falls, slows at the embrace, hangs, then runs backward: the drops rise as warm sparks
        if t < 17.3:
            return t
        u = t - 17.3
        return 17.3 + 0.9 * u - 0.55 * u * u
    scene.add("rain", PW.KeepClear(FX.RainOfLight(P2, radius=11.0, top=15.0, n=6000, speed=4.0, tau=rain_tau,
                                                  warm=lambda t: sc(17.0, 18.5, t),
                                                  gain=_gain((0.0, 0.0), (12.8, 0.0), (13.8, 1.0), (19.6, 1.0),
                                                             (20.2, 0.0), (60.0, 0.0))), WORDS))
    addp("embrace", C["embrace"])

    # ---- S3: the river of light, the doorway, the tree of light
    scene.add("river", PW.KeepClear(FX.LightRiver(RIVER, width=3.2, n=30000, speed=10.0,
                                                  gain=_gain((0.0, 0.0), (18.6, 0.0), (19.85, 1.0), (23.6, 1.0),
                                                             (24.4, 0.35), (26.6, 0.35), (26.79, 0.0), (60.0, 0.0))),
                                    WORDS))
    scene.add("door", FX.Door(P3, width=1.4, height=2.5, facing=0.0, t_open=21.0,
                              gain=_gain((0.0, 0.0), (19.9, 0.0), (20.3, 1.0), (24.4, 1.0), (24.9, 0.0), (60.0, 0.0))))
    petal_path = [P3 + _v(-3.2, 1.4, 2.6), P3 + _v(-1.4, 1.35, 1.2), P3 + _v(0.0, 1.35, 0.1),
                  P3 + _v(0.2, 1.6, -3.0), P3 + _v(-0.4, 2.2, -8.0), P3 + _v(0.5, 3.4, -14.0)]
    scene.add("petals3", PW.KeepClear(FX.PetalStream(petal_path, 21.7, 23.7, n=1300, speed=3.6), WORDS),
              reflect=True)
    scene.add("tree", PW.KeepClear(FX.TreeOfLight(P3b + _v(7.0, 0.0, 2.5), height=3.4, t_bloom=23.9,
                                                  gain=_gain((0.0, 0.0), (23.4, 0.0), (23.9, 1.0), (26.6, 1.0),
                                                             (26.79, 0.0), (60.0, 0.0))), WORDS))
    addp("concession", C["concession"])
    addp("respect", C["respect"])

    # ---- S4: the cathedral of falling light, rising lights
    nave = [P4 + _v(sx * 7.5, 0.0, dz) for dz in (10.0, 0.0, -10.0, -20.0, -30.0) for sx in (-1.0, 1.0)]
    nave += [P4 + _v(0.0, 0.0, -30.0)]
    scene.add("nave", PW.KeepClear(FX.LightColumns(nave, top=95.0, per=700, core_w=0.6, fall=6.0, core_k=0.18,
                                                   spark=0.045,
                                                   gain=_gain((0.0, 0.0), (26.79, 0.0), (27.0, 1.0), (33.2, 1.0),
                                                              (33.36, 0.0), (60.0, 0.0))), WORDS))
    scene.add("pour4", PW.KeepClear(FX.LightColumns([P4], top=30.0, per=420, fall=2.4, ring=1.2, core=False,
                                                    spark=0.03, soft=True,
                                                    gain=_gain((0.0, 0.0), (26.79, 0.0), (27.3, 1.0), (33.2, 1.0),
                                                               (33.36, 0.0), (60.0, 0.0))), WORDS))
    scene.add("rising4", PW.KeepClear(FX.RisingLights(P4, 28.0, r0=2.5, r1=45.0, n=700, speed=16.0,
                                                      until=SEC[5]), WORDS))
    addp("encouragement", C["encouragement"])

    # ---- S5: the nine rivers across the sky, the help up, the twirl, the crowd of light
    def sky_river(k):
        a0 = np.radians(-80.0 + 160.0 * ((k * 4) % 9) / 8.0)
        h = 10.0 + 3.2 * ((k * 5) % 9)
        R = 80.0 + 5.0 * k

        def f(t):
            u = t - SEC[5]
            a = a0 + 0.22 * u * (1.0 if k % 2 == 0 else -1.0)
            return P5 + _v(np.sin(a) * R, h + 5.0 * np.sin(0.8 * t + k), -np.cos(a) * R)
        return f
    heads = [(sky_river(k), NINE_GLOW[k], lambda t: sc(SEC[5], SEC[5] + 0.6, t) * (1.0 - sc(39.6, 40.3, t)), 3.2)
             for k in range(9)]
    scene.add("sky_rivers", Clear(MB.Rivers(heads, cuts=[SEC[5]], tail=2.6)), reflect=False)
    scene.add("aurora", MS.Aurora(center=(float(P5[0]), float(P5[2])),
                                  gain=_gain((0.0, 0.0), (26.79, 0.0), (27.0, 0.45), (33.2, 0.45), (33.36, 1.0),
                                             (40.0, 1.0), (41.5, 0.5), (42.4, 0.0), (60.0, 0.0))),
              depth_of_field=False)
    addp("consideration", C["consideration"])
    addp("compliment", C["compliment"])
    try:
        from p3d.crowd import Crowd
        rr = np.random.default_rng(55)
        ang = np.radians(np.linspace(105.0, 255.0, 24)) + rr.normal(0.0, 0.03, 24)
        rad = 3.8 + 2.6 * rr.random(24)
        places = np.stack([P5b[0] + np.sin(ang) * rad, P5b[2] + np.cos(ang) * rad], 1)
        crowd = Crowd(n=24, places=places,
                      facing="center", kinds=(("clap", 2.0), ("cheer", 1.0)), start=dict(t=36.6, dur=0.8),
                      act=dict(t=37.4, dur=0.8), until=40.6, fade=0.6, points=4000, color="#ffcf7a",
                      color2="#fff1d6", bright=1.3)
        scene.add("crowd5", PW.KeepClear(crowd, WORDS), reflect=False)      # no tall columns in the water
    except Exception as e:          # pragma: no cover
        print("crowd skipped:", e)
    twirl = C["compliment"][0]
    scene.add("hearts5", Clear(MB.HeartBurst(lambda t: twirl.where(t, "chest"), 37.9, NINE_GLOW, n=30,
                                             reach=2.4)), reflect=False)

    # ---- the breath and the ascent: the nine colours braid up the column with us
    def braid(k):
        def f(t):
            u = max(t - ASC0, 0.0)
            a = 1.1 * t + 2.0 * np.pi * k / 9.0 + 2.2 * u + 0.3 * u * u
            r = 4.0 + 5.0 * np.exp(-u / 1.2)
            y = _climb(t) + 3.0 + 4.0 * np.sin(1.3 * t + k) * 0.3
            return A7 + _v(np.sin(a) * r, y, np.cos(a) * r)
        return f
    up_heads = [(braid(k), NINE_GLOW[k], lambda t: sc(BREATH_END, BREATH_END + 0.5, t) * (1.0 - sc(49.2, 49.7, t)),
                 0.9) for k in range(9)]
    scene.add("braid", MB.Rivers(up_heads, cuts=[BREATH_END], tail=0.8), reflect=False)
    scene.add("pillar7", FX.LightColumns([A7], top=320.0, per=4000, core_w=2.2, fall=-6.0, core_k=0.4,
                                         gain=_gain((0.0, 0.0), (42.4, 0.0), (42.8, 1.0), (49.0, 1.0), (49.6, 0.0),
                                                    (60.0, 0.0))), reflect=False)

    # ---- the biggest hit (42.51): the date bursts, a fountain of light and a ring of the nine colours
    scene.add("fountain", FX.Fountain(A7 + _v(0.0, 0.5, 0.0), BREATH_END, n=7000, colors=NINE_GLOW, speed=(12.0, 34.0)),
              reflect=True)
    scene.add("ring9", FX.ColorRing(A7, BREATH_END, NINE_GLOW, speed=70.0, reach=1400.0))

    # ---- the finale: the luminous Earth, hearts across it, Mother's hands, the logo
    ax = _unit(LOGO_U + 0.35 * LOGO_N + 0.2 * LOGO_R)
    m0 = _unit(LOGO_N - float(LOGO_N @ ax) * ax)
    e0 = np.cross(ax, m0)

    def geo(lon, lat, r=1.0, t=0.0):
        lo = np.radians(np.asarray(lon, np.float64) + 75.0 + 6.0 * (t - SEC[7]))[..., None]
        la = np.radians(np.asarray(lat, np.float64))[..., None]
        return GC + RG * r * (np.cos(la) * (np.cos(lo) * m0 + np.sin(lo) * e0) + np.sin(la) * ax)
    earth_g = _gain((0.0, 0.0), (SEC[7] - 0.1, 0.0), (SEC[7] + 0.3, 1.0), (54.2, 1.0), (54.9, 0.0), (60.0, 0.0))
    scene.add("earth", MB.Earth(geo, GC, RG, earth_g, land_k=_gain((0.0, 1.0), (53.8, 1.0), (54.4, 0.0), (60.0, 0.0))),
              reflect=False)
    scene.add("earth_shadow", MB.EarthShadow(GC, RG), reflect=False,
              mask=Mask("dark", strength=lambda t: sc(SEC[7] - 0.1, SEC[7] + 0.2, t) * (1.0 - sc(53.9, 54.5, t)),
                        grow=0.1 * RG, soft=2.0))
    from p3d import brand

    def dest(i):
        side = -0.33 if i % 2 == 0 else 0.33
        return LOGO_C + LOGO_H * (side * LOGO_R - 0.05 * LOGO_U) + LOGO_N * 0.05
    scene.add("earth_hearts", MB.EarthHearts(geo, GC, RG, NINE_GLOW, HEARTS_T0, HEARTS_T1, n=54, dests=dest,
                                             t_fly=53.55), reflect=False)
    addp("cradle", C["cradle"])
    logo = brand.Logo(pos=tuple(LOGO_C), size=LOGO_H, facing=float(np.degrees(np.arctan2(LOGO_N[0], LOGO_N[2]))),
                      tilt=float(np.degrees(np.arcsin(np.clip(LOGO_N[1], -1.0, 1.0)))), t_in=LOGO_T0, t_full=LOGO_T1, t_out=56.2, leave_dur=0.8, arrive="build",
                      leave="fade", paint=lambda t: sc(DAY_T + 0.2, DAY_T + 1.0, t), bright=0.26, glow=0.08,
                      reflect=False)
    scene.add("logo", logo, reflect=False)
    scene.add("logo_burst", MB.LogoBurst(LOGO_C, LOGO_N, 54.3, NINE_GLOW, size=LOGO_H * 0.9), reflect=False)

    pastel = _cloud_sea(rng, CAM_END, 260.0, 1600.0, 150, EARTH_Y - 34.0, 60.0, 130.0, 1.0, hk=(0.28, 0.45))
    scene.add("clouds_pastel", MS.Billows(pastel, gain=_gain((0.0, 0.0), (DAY_T, 0.0), (DAY_T + 1.0, 1.0),
                                                             (60.0, 1.0)), seed=15, alpha=0.05, body=0.2,
                                          top="#fff4e8", warm="#ffd8c0", rose="#f8c0cc", lilac="#c8c8f4",
                                          core="#fff8f0", shade=0.3, sun_az=180.0), depth_of_field=False)

    # ---- hearts off every word, the nine symbols as subtle scenery
    acts = [("Greeting", P1 + _v(0.0, 1.45, 0.0), 8.2, 10.1), ("Gratitude", None, 11.3, 13.4),
            ("Apology", P2 + _v(0.0, 0.95, 0.0), 15.0, 17.0), ("Inclusiveness", P2 + _v(0.0, 1.45, 0.0), 17.9, 19.8),
            ("Concession", P3 + _v(0.0, 1.3, 0.0), 21.5, 23.5), ("Respect", P3b + _v(0.0, 1.0, 0.0), 24.6, 26.6),
            ("Encouragement", P4 + _v(-0.05, 1.05, 0.0), 29.0, 31.3),
            ("Consideration", P5 + _v(0.0, 1.0, 0.0), 34.8, 36.7), ("Compliment", P5b + _v(0.0, 1.3, 0.0), 38.2, 40.0)]
    grat = C["gratitude"][0]
    for k, (lab, at, t0, t1) in enumerate(acts):
        src = (lambda t: grat.where(t, "heart")) if at is None else (lambda t, at=at: at)
        scene.add("hearts_%d" % k, Clear(MB.RisingHearts(src, [(t0, t1, GLOWC[lab])], rate=3.0, seed=300 + k)))
    for k, (lab, tt, anchor, size) in enumerate(SYMBOL_PLAN):
        scene.add("symbol_%d" % k, Clear(MB.SymbolLight(lab, anchor, tt, GLOWC[lab], size=size, seed=91 + k)))

    WORDS.add_to(scene, reflect=False)
    try:
        WORDS.check(CAMERA)
    except Exception as e:          # the check is advice; never stop a render for it
        print("words check failed:", e)


def _sym_place(c, cam_t):
    """A symbol standing at c, facing the camera as it is at cam_t."""
    def f(t):
        cam = PW._cam_at(_LAYOUT, cam_t)
        d = _unit(np.asarray(cam.pos, np.float64) - c)
        rt = _unit(np.cross(UP, d))
        return c, rt, UP
    return f


# each symbol drawn subtly in the world near its expression, in its colour (never over the words)
SYMBOL_PLAN = [
    ("Greeting", 8.2, _sym_place(P1 + _v(-2.6, 2.2, -3.0), 8.6), 0.9),
    ("Gratitude", 11.2, _sym_place(P1b + _v(2.6, 2.4, -4.0), 11.6), 1.0),
    ("Apology", 14.9, _sym_place(P2 + _v(-3.2, 2.0, -4.0), 15.4), 1.0),
    ("Inclusiveness", 18.2, _sym_place(P2 + _v(3.0, 2.6, -5.0), 18.6), 1.2),
    ("Concession", 21.6, _sym_place(P3 + _v(-3.0, 1.6, -2.0), 22.0), 1.1),
    ("Respect", 24.8, _sym_place(P3b + _v(-2.8, 3.4, -3.5), 25.2), 1.1),
    ("Encouragement", 28.6, _sym_place(P4 + _v(-3.6, 3.0, -6.0), 29.0), 1.4),
    ("Consideration", 34.6, _sym_place(P5 + _v(3.4, 2.4, -4.0), 35.0), 1.1),
    ("Compliment", 38.0, _sym_place(P5b + _v(-3.4, 2.8, -5.0), 38.4), 1.2),
]


P3D = dict(
    camera=CAMERA,
    world=dict(WORLD, shafts=[_shaft([(P1b, 10.3, 14.0, 0.45), (P5, 33.6, 37.2, 0.45)], radius=1.2),
                              _shaft([(P4, 27.0, 33.2, 0.32)], radius=2.0,
                                     color="#ffe6b8", top=60.0),
                              _shaft([(P3, 20.6, 23.9, 0.5), (P5b, 37.2, 40.6, 0.5)], radius=1.2, color="#ffeccc"),
                              _shaft([(P2, 17.2, 19.9, 0.35)], radius=1.0, color="#ffd8a0", top=22.0)]),
    setup=_setup,
    bursts=[dict(t=BREATH_END, strength=0.75, rise=0.06, fall=0.45, color="#ffd9a0", at=tuple(A7 + _v(0.0, 6.0, 0.0)))],
    motion_blur=0.4,
)


# =============================================================================================================
# THE TITLES (TITLES: opening, signature, the date in light, the official-style end card); old keys off
# =============================================================================================================
FORM_DUR = 3.0
TITLE_FORM = 1e9
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=1e9, hold=1e9, star=1e9)
TAGLINE = dict(text="", t0=1e9, t1=1e9 + 1.0)
FRAGMENTS = []
TITLE_HIT = 1e9
PHRASES = _base.PHRASES
WAVES = []

TITLES = dict(
    opening=dict(t_end=3.7, y=0.30, palette="night"),
    signature=dict(windows=[(31.85, 33.25, "tr", "night"), (47.8, 49.3, "tr", "night")]),
    date_light=dict(t_form=SEC[6], t_burst=BREATH_END, y=0.27, palette="night"),
    end_card=dict(t_in=55.0, scale=EC_SCALE, backdrop="auto"),
)
