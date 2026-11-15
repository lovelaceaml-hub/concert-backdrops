"""Film 06 of the ten concert promos: ASCENSION (60 seconds, the 3D layer: engine/UPGRADE-HOWTO.md V, W, X).

LOGLINE
Every word of Mother's love lifts someone. One unbroken rising spiral carries a traveller from a dark lake up
through mist, past hundreds of pillars of light and into a closing cloud, to sunrise above the clouds. On every
level someone is met; a word of love is spoken, the flakes of light that leave the speaker become the words,
and the words carry everyone up to the next level. In the cloud a hand reaches down to hers; above the clouds
Heavenly Mother stands (from behind, veiled) against the rising sun under the arch of nine lights.

WHAT MAKES IT THIS FILM AND NO OTHER
 - The only vertical film. The camera never cuts and its height never falls: it climbs and turns the whole
   way (about 130 m and one and a half turns). Height is warmth: cold blue at the lake, violet under the
   cloud, lilac inside it, rose and gold above it, the pale campaign day on the card.
 - Every launch upward lands on a hit of the medley (6.84, 13.30, 19.85, 26.79, 33.36, 42.51).
 - The look of the traveller is how loved she is: a dark body with a cold rim at the lake, more light at
   every level, radiant at the top.

THE LEVELS (metres above the lake; the shaft of light stands on the y axis)
   0  the lake: the traveller from behind in a cold shaft; a woman of coral dots blows the GREETING to her
  12  ring 1 in the mist: a man bows (APOLOGY); she opens her arms (INCLUSIVENESS); both rise
  30  ring 2: the wide reveal of a lake full of pillars; an old man kneels, her hand on his shoulder (GRATITUDE)
  50  ring 3: a man in a hurry; she offers him the way up first (CONCESSION); he rises first, she follows
  68  ring 4: a young man sits; she kneels and listens (RESPECT, stars of his thoughts)
  86  ring 5: a child under a darkening sky; she kneels and prays (ENCOURAGEMENT comes down a shaft)
 105  inside the cloud, the breath of the medley: two hands, hers blue from below, Mother's gold from above
      (CONSIDERATION); they touch on the biggest hit (42.51) and the flare carries us through the cloud top
 122  above the clouds at sunrise: Mother from behind, veiled, her head over the sun, rays fanning round it;
      the COMPLIMENT is burned into the sky by the rays and streams into the last light of the arch
      the card: the camera pulls back over a white sea of cloud; fountains of gold burst from it; the end card
      under the arch of nine lights in the campaign day (readable from 53.6 s to the end)

House rules kept: no lyrics, no facial features (everyone from behind or in profile, checked below), everyone
clothed, Heavenly Mother only as a hand and from behind, nothing dark behind any text, never a black frame,
all nine expressions with their exact wording from p3d.words.EXPRESSIONS (named, never retyped).
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 60.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 59.9
_base.SONG_END = 60.0
_base.FADE = _base.Track([(0.0, 1.0), (60.0, 1.0)])          # never black: not at frame 0, not at the end
_base.EXPOSURE = _base.Track([(0.0, 1.0), (60.0, 1.0)])
_base.RAIN = _base.Track([(0.0, 0.0), (60.0, 0.0)])
_base.AURORA = _base.Track([(0.0, 0.0), (60.0, 0.0)])
_base.PART = _base.Track([(0.0, 0.0), (60.0, 0.0)])
_base.ZOOM = _base.Track([(0.0, 1.0), (60.0, 1.0)])
for _p in _base.PHRASES:                       # the flat expressions stay off: the words are particles here
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402
from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d import effects as FX  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d import bodymath as BM  # noqa: E402
from p3d.body import Body  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402
from p3d.world import arch_points  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 59.9
SONG_END = 60.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0          # nothing dark behind any text

# ---------------------------------------------------------------------------------------------------------
# The medley (scratchpad/medley2/SECTION-MAP.md): eight sections, the breath 40.21 to 42.51, the final hit.
# ---------------------------------------------------------------------------------------------------------
S = [0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47]
BIG_HIT = 42.51            # the biggest jump of the mix: the hands touch, through the cloud top
FINAL_HIT = 58.11
TITLE_HIT = 52.26          # the title is whole on a bar start of the last song
FORM_DUR = 2.6
T_FORM = TITLE_HIT - FORM_DUR
TAG_T0, TAG_T1 = TITLE_HIT + 0.15, TITLE_HIT + 1.35   # the end card lines: readable from 53.6 s to 60 s
NINTH = 49.4               # the arch is complete

# ---------------------------------------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------------------------------------
Y = [0.0, 12.0, 30.0, 50.0, 68.0, 86.0, 104.0, 122.0]   # the level of each act (feet), metres
C = [0.0, 70.0, 140.0, 210.0, 280.0, 350.0, 420.0, 500.0]   # the camera's azimuth while each act is read
TOP = Y[7]                                              # the top of the cloud: Mother and the traveller stand
SUN_AZ = (C[7] + 180.0) % 360.0                         # the sun rises straight ahead of the last set-up
HANDS_AT = np.array([0.0, Y[6] + 1.3, 0.0])            # where the two fingertips meet in the cloud


def P(az, dist, height=0.0):
    """The point at azimuth az (degrees from +z toward +x), dist metres from the shaft, height metres up."""
    a = np.radians(az)
    return np.array([np.sin(a) * dist, height, np.cos(a) * dist])


def right_of(az):
    """The picture's right for a camera standing at azimuth az and looking at the shaft."""
    a = np.radians(az)
    return np.array([np.cos(a), 0.0, -np.sin(a)])


def pair(k, gap=1.1):
    """Two people of act k face each other across the shaft, square to the camera (both in profile):
    (left place, its facing), (right place, its facing)."""
    r = right_of(C[k])
    return ((-0.5 * gap * r + [0.0, Y[k], 0.0], C[k] + 90.0), (0.5 * gap * r + [0.0, Y[k], 0.0], C[k] - 90.0))


def curve(keys):
    """A smooth function of t through (t, value) keys that never overshoots a key (monotone cubic, Fritsch and
    Carlson): a height that rises from key to key rises at every instant between them."""
    ts = np.array([k[0] for k in keys], dtype=np.float64)
    vs = np.array([np.atleast_1d(np.asarray(k[1], dtype=np.float64)) for k in keys])
    h = np.diff(ts)
    d = np.diff(vs, axis=0) / h[:, None]
    m = np.zeros_like(vs)
    m[0], m[-1] = d[0], d[-1]
    if len(ts) > 2:
        w1 = (2 * h[1:] + h[:-1])[:, None]
        w2 = (h[1:] + 2 * h[:-1])[:, None]
        same = d[:-1] * d[1:] > 0
        den = w1 / np.where(same, d[:-1], 1.0) + w2 / np.where(same, d[1:], 1.0)
        m[1:-1] = np.where(same, (w1 + w2) / den, 0.0)

    def f(t):
        t = min(max(float(t), ts[0]), ts[-1])
        i = min(int(np.searchsorted(ts, t, side="right")) - 1, len(ts) - 2)
        u = (t - ts[i]) / h[i]
        h00, h10 = (1 + 2 * u) * (1 - u) ** 2, u * (1 - u) ** 2
        h01, h11 = u * u * (3 - 2 * u), u * u * (u - 1)
        v = h00 * vs[i] + h10 * h[i] * m[i] + h01 * vs[i + 1] + h11 * h[i] * m[i + 1]
        return float(v[0]) if v.shape[0] == 1 else v
    return f


# ---------------------------------------------------------------------------------------------------------
# THE CAMERA: one unbroken rising spiral. Keys (t, azimuth, distance from the shaft, height, look at, fov,
# aperture). Azimuth, distance and height are interpolated separately, so the path is a true spiral, and the
# height never falls (monotone keys).
# ---------------------------------------------------------------------------------------------------------
_HM = HANDS_AT
_MEET_LOOK = _HM + np.array([0.0, 0.10, 0.0])


def _far(az, dist, h, look, reach=8.0):
    """A look target far beyond a near one, on the same line (the view turns smoothly into a close-up; the
    focus is set apart, see _focus)."""
    c = P(az, dist, h)
    d = np.asarray(look, np.float64) - c
    return c + d / np.linalg.norm(d) * reach


CAM_KEYS = [
    # act 0, the lake: worm's eye behind her, up the shaft; slide round to the two in profile
    (0.00, -90.0, 1.55, 0.42, (0.0, 3.2, 0.0), 66, 0.0),
    (1.20, -28.0, 2.90, 0.82, (0.0, 2.25, 0.0), 60, 0.02),
    (3.00, -10.0, 4.00, 1.20, (0.0, 1.95, 0.0), 47, 0.03),
    (5.70, 7.0, 4.25, 1.70, (0.0, 2.10, 0.0), 46, 0.03),
    (6.84, 16.0, 4.00, 2.00, (0.0, 2.75, 0.0), 50, 0.02),
    # launch 1 (6.84): she breaks upward into flakes; up through the mist with them
    (7.25, 23.0, 3.90, 3.30, (0.0, 5.0, 0.0), 56, 0.01),
    (7.80, 36.0, 3.90, 7.80, (0.0, 12.0, 0.0), 62, 0.0),
    (8.40, 47.0, 4.50, Y[1] + 1.15, (0.0, Y[1] + 1.95, 0.0), 48, 0.02),
    (11.0, 66.0, 4.65, Y[1] + 1.40, (0.0, Y[1] + 2.05, 0.0), 48, 0.03),
    (13.30, 80.0, 4.60, Y[1] + 1.75, (0.0, Y[1] + 2.35, 0.0), 48, 0.03),
    (14.75, 92.0, 4.9, Y[1] + 3.6, (0.0, Y[1] + 4.6, 0.0), 52, 0.02),
    # launch 2: swing out wide over a lake full of pillars, then swoop in to the old man
    (15.45, 104.0, 9.5, 21.0, (0.0, 22.5, 0.0), 62, 0.0),
    (16.25, 114.0, 12.5, 26.0, (0.0, 26.8, 0.0), 64, 0.0),
    (17.05, 122.0, 4.6, Y[2] + 1.10, (0.0, Y[2] + 1.75, 0.0), 46, 0.02),
    (18.60, 138.0, 4.5, Y[2] + 1.35, (0.0, Y[2] + 1.85, 0.0), 46, 0.03),
    (19.85, 152.0, 4.4, Y[2] + 2.00, (0.0, Y[2] + 2.9, 0.0), 50, 0.02),
    # launch 3 (19.85, the bass slams in)
    (20.25, 158.0, 4.3, Y[2] + 3.0, (0.0, Y[2] + 4.6, 0.0), 54, 0.01),
    (20.75, 170.0, 4.2, 42.0, (0.0, 48.0, 0.0), 60, 0.0),
    (21.40, 183.0, 4.5, Y[3] + 1.15, (0.0, Y[3] + 1.90, 0.0), 47, 0.02),
    (24.80, 212.0, 4.5, Y[3] + 1.55, (0.0, Y[3] + 2.00, 0.0), 47, 0.03),
    (26.79, 228.0, 4.3, Y[3] + 2.40, (0.0, Y[3] + 3.6, 0.0), 50, 0.02),
    # launch 4 (26.79)
    (27.20, 234.0, 4.2, Y[3] + 3.4, (0.0, Y[3] + 5.0, 0.0), 54, 0.01),
    (27.70, 245.0, 4.0, 61.0, (0.0, 67.0, 0.0), 60, 0.0),
    (28.40, 255.0, 4.3, Y[4] + 1.00, (0.0, Y[4] + 1.55, 0.0), 46, 0.02),
    (31.80, 284.0, 4.3, Y[4] + 1.35, (0.0, Y[4] + 1.70, 0.0), 46, 0.03),
    (33.36, 300.0, 4.1, Y[4] + 2.20, (0.0, Y[4] + 3.4, 0.0), 50, 0.02),
    # launch 5 (33.36): under the darkening sky, the child
    (33.75, 306.0, 4.1, Y[4] + 3.2, (0.0, Y[4] + 4.8, 0.0), 54, 0.01),
    (34.20, 315.0, 4.0, 79.0, (0.0, 85.0, 0.0), 60, 0.0),
    (34.90, 325.0, 4.2, Y[5] + 1.00, (0.0, Y[5] + 1.55, 0.0), 46, 0.02),
    (38.20, 355.0, 4.2, Y[5] + 1.45, (0.0, Y[5] + 1.85, 0.0), 46, 0.03),
    # launch 6 (38.2): up into the cloud; the breath: two hands, close
    (39.00, 372.0, 2.4, 96.0, tuple(_MEET_LOOK), 56, 0.0),
    (39.45, 388.0, 2.0, _HM[1] - 0.6, tuple(_far(388.0, 2.0, _HM[1] - 0.6, _MEET_LOOK)), 44, 0.03),
    (39.95, 397.0, 1.25, _HM[1] - 0.12, tuple(_far(397.0, 1.25, _HM[1] - 0.12, _MEET_LOOK)), 38, 0.04),
    (42.40, 417.0, 1.15, _HM[1] + 0.10, tuple(_far(417.0, 1.15, _HM[1] + 0.10, _MEET_LOOK + [0, 0.03, 0])), 37,
     0.05),
    # launch 7 (42.51, the biggest hit): through the cloud top into sunrise, behind Mother
    (42.70, 424.0, 1.6, _HM[1] + 1.2, tuple(P(424.0, 1.6, _HM[1] + 6.2) + 8.0 * P(244.0, 1.0)), 52, 0.0),
    (43.20, 455.0, 3.0, 114.0, tuple(P(455.0, 3.0, 117.5) + 10.0 * P(282.0, 1.0)), 58, 0.0),
    (43.90, 490.0, 5.5, TOP + 1.30, tuple(P(SUN_AZ, 30.0, TOP + 4.0)), 48, 0.02),
    (45.60, 500.0, 7.2, TOP + 1.60, tuple(P(SUN_AZ, 30.0, TOP + 5.2)), 46, 0.02),
    (48.00, 504.0, 12.0, TOP + 3.0, tuple(P(SUN_AZ, 26.0, TOP + 7.2)), 50, 0.0),
    # the card: pull back and rise over the sea of cloud to the arch of nine lights
    (49.47, 506.0, 18.0, TOP + 5.0, tuple(P(SUN_AZ, 45.0, TOP + 17.0)), 52, 0.0),
    (52.26, 508.0, 26.0, TOP + 8.5, tuple(P(SUN_AZ, 60.0, TOP + 23.0)), 58, 0.0),
    (60.00, 513.0, 30.0, TOP + 10.0, tuple(P(SUN_AZ, 60.0, TOP + 18.0)), 60, 0.0),
]
_ck = [(k[0], (k[1], k[2], k[3])) for k in CAM_KEYS]
_cyl = curve(_ck)
_tgt = curve([(k[0], k[4]) for k in CAM_KEYS])
_fov = curve([(k[0], k[5]) for k in CAM_KEYS])
_ape = curve([(k[0], k[6]) for k in CAM_KEYS])


def cam_pos(t):
    az, dist, h = _cyl(t)
    return P(az, dist, h)


def cam_target(t):
    return np.asarray(_tgt(t), np.float64)


class Spiral(Move):
    """The film's one camera move: the spiral of CAM_KEYS."""

    def pose(self, t):
        return cam_pos(t), cam_target(t)


def _focus(t):
    """Focus on the look target, except on the two hands in the cloud (their target is set far beyond them)."""
    p = cam_pos(t)
    far = float(np.linalg.norm(cam_target(t) - p))
    near = float(np.linalg.norm(HANDS_AT - p))
    k = float(np.clip((t - 39.0) / 0.6, 0.0, 1.0) * np.clip((42.75 - t) / 0.3, 0.0, 1.0))
    return far + (near - far) * k


CAMERA = Rig([Spiral(0.0, TOTAL, fov=lambda t: _fov(t), aperture=lambda t: max(_ape(t), 0.0), focus=_focus)],
             handheld=0.18, min_height=0.3)

# ---------------------------------------------------------------------------------------------------------
# THE PEOPLE (engine/p3d/body.py). Nobody is ever seen from the front: two who meet face each other across
# the shaft, square to the camera, and the camera stays within about 35 degrees of that square view.
# ---------------------------------------------------------------------------------------------------------
_RISE = dict(kind="dissolve", dur=1.5, rise=2.4, speed=0.0, swirl=0.45, noise=0.3)


def _dissolve(t, dur=1.5, **kw):
    d = dict(_RISE, t=float(t), dur=dur)
    d.update(kw)
    return d


def _form(t, dur=1.1):
    return dict(kind="form", t=float(t), dur=dur, travel=0.8)


_L0, _R0 = pair(0)
_L1, _R1 = pair(1)
_L2, _R2 = pair(2, gap=1.0)
_L3, _R3 = pair(3, gap=1.25)
_L4, _R4 = pair(4, gap=0.95)
_L5, _R5 = pair(5, gap=0.80)

PEOPLE = {}                 # filled by _cast() when the scene is built (cloth needs scipy; the workflow's
                            # first job imports this file with numpy only)
_RT = right_of(C[7])
MOTHER_AT = 0.38 * _RT + [0.0, TOP, 0.0]
MOTHER_HEAD = MOTHER_AT + [0.0, 1.58, 0.0]
T_ECLIPSE = 45.6            # the camera sees her head right over the sun
_EYE = None


def _eclipse_dir():
    """The direction from the camera through Mother's head at T_ECLIPSE: where the sun stands."""
    d = MOTHER_HEAD - cam_pos(T_ECLIPSE)
    return d / np.linalg.norm(d)


_SD = _eclipse_dir()
SUN_AZ_TRUE = float(np.degrees(np.arctan2(_SD[0], _SD[2])))
SUN_EL_TRUE = float(np.degrees(np.arcsin(_SD[1])))
SUN_LIGHT = MOTHER_HEAD + _SD * 24.0          # the light with rays, right behind her head from the camera


def _hand(j, meet, t_touch, axis, tilt, approach, color, show, apart=0.5, bright=1.0, color2="#ffffff"):
    """One of two hands reaching to touch (as p3d.body.Hands, but with a time window): j=0 from below, 1 above."""
    a = np.radians(axis)
    d = np.array([np.sin(a), 0.0, np.cos(a)])
    tl = np.radians(tilt)
    sgn = 1.0 if j == 0 else -1.0
    side = "R" if j == 0 else "L"
    aim = sgn * d * np.cos(tl) + np.array([0.0, np.sin(tl) * (1.0 if j == 0 else -1.0), 0.0])
    t0 = t_touch - approach

    def at(t):
        u = BM.smoother((t - t0) / approach)
        gap = 0.5 * apart * (1.0 - u)
        drift = np.array([0.0, 0.010 * BM.wobble(t, 3.0 + j, 0.9), 0.010 * BM.wobble(t, 5.0 + j, 0.7)]) * (1.0 - u)
        return meet - aim * gap + drift

    from p3d import looks as _looks
    fxs = [dict(kind="shed", n=4000, life=2.4, where=[_looks.HAND], dir=-aim, speed=0.5, rise=0.25, turb=0.22,
                spread=0.05)]
    return Body("woman", part="arm." + side, look="glitter", color=color, color2=color2, points=50000,
                effects=fxs, seed=80.0 + j, show=show, fade=0.6, bright=bright,
                hand=dict(side=side, at=at, aim=aim, palm=(0.0, 1.0, 0.0) if j == 0 else (0.0, -1.0, 0.0),
                          pose="offer" if j == 0 else "open", anchor="fingertips"))


_HAND_AXIS = (C[6] - 15.0 + 90.0)            # the hands reach across the picture
FLARE = FX.Flare(tuple(HANDS_AT), BIG_HIT, color="#fff1d0", color2="#9fd0ff", strength=0.8, reach=0.7)


def _cast():
    """Everyone in the film, in order of appearance (built once)."""
    if PEOPLE:
        return PEOPLE
    pp = PEOPLE
    # act 0, the lake: the traveller, gold in a cold shaft (ref 13); the greeter of coral dots in profile (ref 14)
    pp["traveller 0"] = Body("woman", at=_L0[0], facing=_L0[1], garment="coat", look="glitter", color="#f2b865",
                             color2="#ffe2b0", points=60000, seed=61.0, bright=1.2,
                             gesture=[(3.2, 9.0, "look_up", dict(amount=10)), (5.9, 9.0, "open_arms")],
                             effects=[_dissolve(S[1], dur=1.6)], show=(-2.0, 9.6), fade=0.3)
    pp["greeter"] = Body("woman", at=_R0[0], facing=_R0[1], garment="dress", hair=True, look=dict(name="dots", bright=0.45),
                         color="#ff977c", color2="#ffd9a0", points=45000, seed=62.0,
                         gesture=[(1.5, 4.6, "blow")], effects=[_form(1.3, 0.9), _dissolve(S[1] + 0.25)],
                         show=(1.25, 9.6), fade=0.15)
    # act 1, ring 1: the man who bows (Apology), the traveller who opens her arms (Inclusiveness)
    pp["man 1"] = Body("man", at=_R1[0], facing=_R1[1], garment="coat", look="glitter", color="#ffad69",
                       color2="#ffe0c0", points=45000, seed=63.0, gesture=[(8.5, 12.4, "bow")],
                       effects=[_form(8.1, 1.0), _dissolve(S[2] - 0.1)], show=(8.0, 16.2), fade=0.15)
    pp["traveller 1"] = Body("woman", at=_L1[0], facing=_L1[1], garment="coat", look="glitter", color="#ecc68a",
                             color2="#d6e2ff", points=50000, seed=64.0, gesture=[(10.0, 15.0, "open_arms")],
                             effects=[_form(7.1, 1.3), _dissolve(S[2] + 0.05)], show=(7.0, 16.2), fade=0.15)
    # act 2, ring 2: the old man kneels; her hand on his shoulder (Gratitude)
    pp["elder"] = Body("man", at=_R2[0], facing=_R2[1], garment="tunic", look="glitter", color="#ffd05f",
                       color2="#fff0c8", points=45000, seed=65.0, stoop=0.7,
                       motion=[(13.0, "kneel", dict(one=True))],
                       effects=[_form(15.0, 1.1), _dissolve(S[3])], show=(14.9, 22.6), fade=0.15)
    pp["traveller 2"] = Body("woman", at=_L2[0], facing=_L2[1], garment="coat", look="glitter", color="#f2d3a0",
                             color2="#fff0d0", points=50000, seed=66.0,
                             gesture=[(15.6, 20.2, "hand_on_shoulder",
                                       dict(side="R", to=lambda t: PEOPLE["elder"].where(t, "shoulder.R")))],
                             effects=[_form(14.8, 1.2), _dissolve(S[3] + 0.1)], show=(14.7, 22.6), fade=0.15)
    # act 3, ring 3: a man in a hurry; she offers him the way up first (Concession); he rises first
    pp["hurried"] = Body("man", at=_R3[0], facing=_R3[1], garment="coat", look="glitter", color="#82b0ed",
                         color2="#e0f0ff", points=45000, seed=67.0, gesture=[(22.0, 24.6, "bow", dict(amount=0.4))],
                         effects=[_form(21.5, 0.9), _dissolve(24.9, dur=1.4)], show=(21.4, 27.6), fade=0.15)
    pp["traveller 3"] = Body("woman", at=_L3[0], facing=_L3[1], garment="coat", look="glitter", color="#ffdcb0",
                             color2="#ffffff", points=50000, seed=68.0, gesture=[(21.0, 27.5, "offer")],
                             effects=[_form(20.4, 1.0), _dissolve(S[4])], show=(20.3, 29.0), fade=0.15)
    # act 4, ring 4: a young man sits; she kneels and listens (Respect)
    pp["thinker"] = Body("man", at=_R4[0], facing=_R4[1], garment="tunic", look=dict(name="dots", bright=0.45), color="#ce927e",
                         color2="#ffe2d0", points=45000, seed=69.0, motion=[(25.0, "sit")],
                         effects=[_form(28.2, 1.0), _dissolve(S[5])], show=(28.1, 35.2), fade=0.15)
    pp["traveller 4"] = Body("woman", at=_L4[0], facing=_L4[1], garment="coat", look="glitter", color="#ffe2b8",
                             color2="#ffffff", points=50000, seed=70.0, motion=[(25.0, "kneel")],
                             gesture=[(28.4, 34.0, "listen")],
                             effects=[_form(27.3, 1.2), _dissolve(S[5] + 0.15)], show=(27.2, 35.2), fade=0.15)
    # act 5, ring 5: a child; she kneels beside her and prays (Encouragement); the child rises first
    pp["child"] = Body("child", at=_R5[0], facing=_R5[1], garment="dress", look="glitter",
                       color="#b293e7", color2="#f2e6ff", points=40000, seed=71.0, bright=1.35,
                       gesture=[(35.2, 40.0, "look_up", dict(amount=16))],
                       effects=[_form(34.8, 1.0), _dissolve(38.2, dur=1.4)], show=(34.7, 40.6), fade=0.15)
    pp["traveller 5"] = Body("woman", at=_L5[0], facing=_L5[1], garment="coat", look="glitter", color="#fff0d0",
                             color2="#ffd27a", points=50000, seed=72.0, motion=[(32.0, "kneel")],
                             gesture=[(34.8, 39.0, "pray")],
                             effects=[_form(34.1, 1.1), _dissolve(38.55, dur=1.4)], show=(34.0, 40.8), fade=0.15)
    # act 6, the breath: her hand from below (cold blue), Mother's hand from above (gold)
    pp["her hand"] = _hand(0, HANDS_AT, BIG_HIT, _HAND_AXIS, 26.0, 2.9, "#4f8fff", (39.0, 43.4), bright=1.4,
                           color2="#9cc4ff")
    pp["Mother's hand"] = _hand(1, HANDS_AT, BIG_HIT, _HAND_AXIS, 26.0, 2.9, "#ffb040", (39.3, 43.4), bright=1.5,
                                color2="#ffe0a0")
    # act 7 and the card: above the clouds. Mother from behind, veiled; the traveller at her side, radiant
    pp["Mother"] = Body("woman", at=MOTHER_AT, facing=SUN_AZ, garment="robe", veil=dict(length=1.3),
                        look=["rim", "glitter"], color="#ffe2a8", color2="#fff8ec", points=70000, seed=90.0,
                        gesture=[(45.4, 70.0, "open_arms")], effects=[_form(42.6, 1.3)], show=(42.5, 60.5),
                        fade=0.2)
    pp["traveller 7"] = Body("woman", at=-0.38 * _RT + [0.0, TOP, 0.0], facing=SUN_AZ, garment="coat",
                             look=["rim", dict(name="glitter", bright=1.5)], color="#fff2d8", color2="#ffd27a",
                             points=55000, seed=91.0,
                             gesture=[(44.0, 70.0, "look_up", dict(amount=12))], effects=[_form(42.7, 1.3)],
                             show=(42.6, 60.5), fade=0.2)
    return pp


# ---------------------------------------------------------------------------------------------------------
# THE ARCH OF NINE LIGHTS above the cloud sea, toward the sun
# ---------------------------------------------------------------------------------------------------------
ARCH_SET = dict(span=172.0, height=74.0, center=tuple(P(SUN_AZ, 62.0, TOP - 2.0)), yaw=C[7] % 360.0, bright=2.2)
LIGHTS = arch_points(ARCH_SET["span"], ARCH_SET["height"], 0.0, center=ARCH_SET["center"], yaw=ARCH_SET["yaw"])

# ---------------------------------------------------------------------------------------------------------
# THE WORDS (engine/p3d/words.py): the nine expressions, named, never retyped. The flakes leave the speaker
# and settle into the letters above the two; they leave rising (or stream into their light of the arch).
# ---------------------------------------------------------------------------------------------------------


def _em(t, depth, px):
    return PW.em_for(CAMERA, t, depth, px)


def _depth(t, p):
    return float(np.linalg.norm(np.asarray(p) - cam_pos(t)))


def _w(expr, pos, px, t_in, r0, r1, t_out, **kw):
    tm = 0.5 * (r0 + r1)
    pos = np.asarray(pos, np.float64)
    return dict(expr=expr, pos=tuple(pos), em=_em(tm, _depth(tm, pos), px), t_in=t_in, t_read0=r0, t_read1=r1,
                t_out=t_out, **kw)


def _place(name, part):
    return lambda t: PEOPLE[name].where(t, part)


_SPECS = [
    _w("Greeting", (0.0, 2.50, 0.0), 92, 1.9, 3.0, 5.85, 7.4, arrive="palm", source=_place("greeter", "palm.R"),
       leave="rise"),
    _w("Apology", (0.0, Y[1] + 2.30, 0.0), 84, 8.15, 9.0, 11.5, 11.5, arrive="palm",
       source=_place("man 1", "head"), leave="morph"),
    _w("Inclusiveness", (0.0, Y[1] + 2.30, 0.0), 88, 11.5, 12.2, 14.75, 15.9, arrive="morph", source="Apology",
       leave="rise"),
    _w("Gratitude", (0.0, Y[2] + 2.40, 0.0), 84, 16.25, 17.2, 19.85, 21.2, arrive="palm",
       source=_place("elder", "shoulder.R"), leave="arch", to=tuple(LIGHTS[1])),
    _w("Concession", (0.0, Y[3] + 2.45, 0.0), 96, 21.2, 22.05, 24.85, 26.2, arrive="palm",
       source=_place("traveller 3", "palm.R"), leave="rise"),
    _w("Respect", (0.0, Y[4] + 2.05, 0.0), 84, 28.35, 29.2, 31.85, 33.2, arrive="palm",
       source=_place("thinker", "head"), leave="rise"),
    _w("Encouragement", (0.0, Y[5] + 2.20, 0.0), 84, 34.75, 35.6, 38.25, 39.5, arrive="shaft", leave="rise"),
    _w("Consideration", HANDS_AT + [0.0, 0.175, 0.0] - 0.09 * right_of(C[6] - 12.0), 84, 39.1, 39.92, 42.47, 43.6, arrive="palm",
       source=_place("Mother's hand", "fingertips.L"), leave="rise"),
    _w("Compliment", P(SUN_AZ, 17.0, TOP + 7.2), 96, 44.0, 45.0, 48.0, NINTH, arrive="rays",
       source=tuple(SUN_LIGHT), leave="arch", to=tuple(LIGHTS[8])),
]


def _riding(base, t0):
    """A place that rises with the camera from t0 on (the words go up with us on the launch)."""
    h0 = float(cam_target(t0)[1])
    base = np.asarray(base, np.float64)
    return lambda t: tuple(base + [0.0, max(float(cam_target(t)[1]) - h0, 0.0), 0.0])


for _s in _SPECS:
    if _s["expr"] == "Inclusiveness":
        _s["pos"] = _riding(_s["pos"], 13.3)
WORDS = PW.Words(_SPECS, camera=CAMERA, face="camera")

# each light of the arch wakes when its expression has risen (or arrives in it)
_LIT = []
for _lab in PW.LABELS:
    _wd = WORDS[_lab]
    _LIT.append(_wd.t_out if _wd.leave == "arch" else _wd.t_read1 + 0.8)

# ---------------------------------------------------------------------------------------------------------
# THE WORLD'S OWN POINT SETS (this film's helpers)
# ---------------------------------------------------------------------------------------------------------


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


class RingWave:
    """The opening hit: a ring of light races out over the black mirror from the traveller's feet."""

    def __init__(self, t0, at, n=5000, speed=16.0, life=3.2, color="#cfe0ff"):
        self.t0, self.at, self.n, self.speed, self.life = t0, np.asarray(at, np.float64), n, speed, life
        rng = np.random.default_rng(606)
        self.a = rng.random(n) * 2 * np.pi
        self.j = rng.normal(size=n) * 0.06
        self.c = lin(color)

    def sample(self, t):
        age = t - self.t0
        if age < 0.0 or age > self.life:
            return []
        r = 0.4 + self.speed * age ** 0.8
        k = 1.0 - age / self.life
        p = np.stack([self.at[0] + np.cos(self.a) * (r + self.j * r * 0.05), np.full(self.n, 0.03),
                      self.at[2] + np.sin(self.a) * (r + self.j * r * 0.05)], axis=1)
        return dict(pos=p, size=0.05 + 0.006 * r, color=self.c, alpha=0.55 * k * k, kind="soft", twinkle=0.3,
                    reflect=False)


class Rings:
    """Rings of still light hung in the air, one under each meeting (a ripple of the lake lifted up)."""

    def __init__(self):
        rng = np.random.default_rng(616)
        self.items = []
        spans = [(6.6, 16.0), (13.6, 22.4), (19.6, 29.0), (26.4, 35.4), (33.2, 41.0)]
        cols = ["#b8c8f0", "#ffe2a8", "#bfe4ff", "#e8b89c", "#d8b8ff"]
        for k in range(1, 6):
            n = 3200
            a = rng.random(n) * 2 * np.pi
            band = rng.random(n)
            rad = np.where(band < 0.55, 1.65 + 0.025 * rng.normal(size=n), 1.62 * np.sqrt(rng.random(n)))
            rad = np.where((band > 0.55) & (band < 0.7), 2.1 + 0.02 * rng.normal(size=n), rad)
            p = np.stack([np.cos(a) * rad, np.full(n, Y[k] - 0.02), np.sin(a) * rad], axis=1).astype(np.float32)
            br = np.where(band < 0.55, 1.0, np.where(band < 0.7, 0.5, 0.18)).astype(np.float32)
            self.items.append((spans[k - 1], p, br, lin(cols[k - 1]), rng.random(n).astype(np.float32)))

    def sample(self, t):
        out = []
        for (t0, t1), p, br, c, sd in self.items:
            g = float(_ss(t0, t0 + 0.9, t) * (1.0 - _ss(t1 - 1.4, t1, t)))
            if g <= 0.0:
                continue
            out.append(dict(pos=p, size=0.028, color=c, alpha=0.75 * g * br, kind="soft", twinkle=0.6, seed=sd))
        return out


class ShaftFlakes:
    """Flakes rising slowly up the shaft of light, always around the camera's height."""

    def __init__(self, n=4200, radius=2.4, win=34.0):
        rng = np.random.default_rng(626)
        self.n, self.win = n, win
        self.a = rng.random(n) * 2 * np.pi
        self.r = radius * np.sqrt(rng.random(n))
        self.ph = rng.random(n) * win
        self.v = 0.6 + 1.6 * rng.random(n)
        self.sz = (0.007 + 0.016 * rng.random(n) ** 2).astype(np.float32)
        self.sd = rng.random(n).astype(np.float32)
        self.rot = rng.random((n, 2)).astype(np.float32) * 6.28
        warm = rng.random(n)[:, None]
        self.col = lin("#cfe0ff")[None] * (1 - warm) + lin("#ffe2b0")[None] * warm

    def sample(self, t):
        g = float(1.0 - _ss(38.6, 40.4, t))
        if g <= 0.0:
            return []
        base = float(cam_pos(t)[1]) - 0.45 * self.win
        y = base + np.mod(self.ph + self.v * t - base, self.win)
        a = self.a + 0.08 * t
        p = np.stack([np.cos(a) * self.r, y, np.sin(a) * self.r], axis=1)
        edge = np.minimum(y - base, base + self.win - y) / 5.0
        near = np.linalg.norm(p - cam_pos(t), axis=1)
        al = np.clip(edge, 0.0, 1.0) * np.clip((near - 0.9) / 1.2, 0.0, 1.0) * 0.9 * g
        return dict(pos=p, size=self.sz, color=self.col, alpha=al, kind="soft", seed=self.sd, twinkle=0.7,
                    reflect=False)


class Pillars:
    """Hundreds of other shafts across the lake, each a column of rising flakes with a soft core: nobody is
    climbing alone. They light in a wave outward from us (13.3 s) and go out as the cloud closes."""

    def __init__(self, n=200, per=110):
        rng = np.random.default_rng(636)
        self.n, self.per = n, per
        az = rng.random(n) * 360.0
        d = 60.0 + 540.0 * rng.random(n) ** 1.3
        self.base = np.stack([np.sin(np.radians(az)) * d, np.zeros(n), np.cos(np.radians(az)) * d], axis=1)
        self.d = d
        self.top = 26.0 + 50.0 * rng.random(n)
        nine = [e["color"] for e in PW.EXPRESSIONS]
        cols = [lin(nine[i % 9]) if i % 3 == 0 else lin("#ffe2a8") for i in range(n)]
        self.col = np.array(cols)
        self.t_on = S[2] + 0.1 + d / 260.0
        self.t_off = 37.6 + 1.2 * (1.0 - d / 600.0)
        k = n * per
        self.pi = np.repeat(np.arange(n), per)
        self.ph = rng.random(k)
        self.jx = rng.normal(size=(k, 2)) * 0.5
        self.sd = rng.random(k).astype(np.float32)
        self.v = 0.10 + 0.08 * rng.random(k)

    def _g(self, t):
        return _ss(self.t_on, self.t_on + 1.2, t) * (1.0 - _ss(self.t_off, self.t_off + 1.0, t))

    def sample(self, t):
        g = self._g(t)
        if not (g > 0.0).any():
            return []
        pi = self.pi
        u = np.mod(self.ph + self.v * t, 1.0)
        top = self.top[pi]
        p = self.base[pi] + np.stack([self.jx[:, 0], u * top, self.jx[:, 1]], axis=1)
        al = (g[pi] * (1.0 - u) ** 0.7 * 0.9).astype(np.float32)
        flakes = dict(pos=p, size=0.20, color=self.col[pi], alpha=al, kind="soft", seed=self.sd, twinkle=0.6)
        on = g > 0.0
        b = self.base[on]
        cores = dict(pos=b, pos2=b + np.stack([np.zeros(on.sum()), self.top[on], np.zeros(on.sum())], axis=1),
                     size=1.4, color=self.col[on], alpha=(0.11 * g[on]).astype(np.float32), alpha2=0.0,
                     kind="ribbon")
        return [flakes, cores]


class CloudWisps:
    """Inside the cloud: soft lit wisps that the camera rises through, so the fog has depth and speed."""

    def __init__(self, n=1400):
        rng = np.random.default_rng(666)
        a = rng.random(n) * 2 * np.pi
        r = 2.6 + 26.0 * rng.random(n) ** 1.4
        self.p = np.stack([np.sin(a) * r, 90.0 + 36.0 * rng.random(n), np.cos(a) * r], axis=1)
        self.sz = (1.2 + 4.5 * rng.random(n)) * (0.6 + r / 30.0)
        self.v = rng.normal(size=(n, 3)) * [0.25, 0.05, 0.25] + [0.0, -0.35, 0.0]
        self.sd = rng.random(n).astype(np.float32)
        warm = rng.random(n)[:, None]
        self.col = lin("#b8a8e8")[None] * (1 - warm) + lin("#ffd6e4")[None] * warm

    def sample(self, t):
        g = float(_ss(37.8, 38.8, t) * (1.0 - _ss(39.3, 39.9, t)))
        if g <= 0.0:
            return []
        p = self.p + self.v * (t - 40.0)
        near = np.linalg.norm(p - cam_pos(t), axis=1)
        al = (0.06 * g * np.clip((near - 3.0) / 4.0, 0.0, 1.0)).astype(np.float32)
        return dict(pos=p, size=self.sz, color=self.col, alpha=al, kind="soft", seed=self.sd, reflect=False)


class CloudTop:
    """Soft lit puffs on the top of the cloud, and around the feet of the two who stand on it."""

    def __init__(self, n=2600):
        rng = np.random.default_rng(646)
        a = rng.random(n) * 2 * np.pi
        d = 14.0 + 420.0 * rng.random(n) ** 1.8
        self.p = np.stack([np.sin(a) * d, TOP - 1.8 + 1.2 * rng.normal(size=n) * (1 + d / 120.0),
                           np.cos(a) * d], axis=1)
        self.sz = (1.5 + 0.06 * d) * (0.6 + 0.8 * rng.random(n))
        self.sd = rng.random(n).astype(np.float32)
        warm = rng.random(n)[:, None]
        self.c_dawn = lin("#ffd6c0")[None] * (1 - warm) + lin("#ffe9cf")[None] * warm
        self.c_day = lin("#ffe2cc")[None] * (1 - warm) + lin("#fff0dc")[None] * warm
        m = 900
        b = rng.random(m) * 2 * np.pi
        r = 0.4 + 2.2 * np.sqrt(rng.random(m))
        self.q = np.stack([np.sin(b) * r, TOP - 0.25 + 0.2 * rng.normal(size=m), np.cos(b) * r], axis=1)

    def sample(self, t):
        g = float(_ss(BIG_HIT - 0.1, BIG_HIT + 0.9, t))
        if g <= 0.0:
            return []
        k = float(_ss(49.0, 53.0, t))
        col = self.c_dawn * (1 - k) + self.c_day * k
        return [dict(pos=self.p, size=self.sz, color=col, alpha=0.04 * g, kind="soft", seed=self.sd, dof=0.6)]


class Fountains:
    """Fountains of gold flakes burst through the sea of cloud: everyone arrives. They surge on the hits."""

    def __init__(self, n=26, per=900):
        rng = np.random.default_rng(656)
        az = SUN_AZ + (rng.random(n) - 0.5) * 150.0
        d = 14.0 + 150.0 * rng.random(n)
        self.base = np.stack([np.sin(np.radians(az)) * d, np.full(n, TOP - 1.5), np.cos(np.radians(az)) * d], 1)
        self.scale = 0.7 + 0.03 * d
        self.t0 = 45.2 + 2.5 * rng.random(n)
        k = n * per
        self.fi = np.repeat(np.arange(n), per)
        self.ph = rng.random(k)
        dirs = rng.normal(size=(k, 3)) * [0.22, 0.0, 0.22]
        dirs[:, 1] = 1.0
        self.v0 = dirs * (5.0 + 3.0 * rng.random(k))[:, None]
        self.sd = rng.random(k).astype(np.float32)
        self.rot = rng.random((k, 2)).astype(np.float32) * 6.28
        warm = rng.random(k)[:, None]
        self.col = lin("#ffd27a")[None] * (1 - warm) + lin("#fff0c8")[None] * warm
        self.life = 2.4

    def sample(self, t):
        fi = self.fi
        on = _ss(self.t0, self.t0 + 0.8, t)[fi]
        if not (on > 0).any():
            return []
        surge = 1.0 + 0.9 * np.exp(-((t - TITLE_HIT) / 0.6) ** 2) + 0.7 * np.exp(-((t - FINAL_HIT) / 0.6) ** 2)
        age = np.mod(self.ph * self.life + t * 0.9, self.life)
        sc = self.scale[fi][:, None]
        p = self.base[fi] + (self.v0 * age[:, None] + np.array([0.0, -2.6, 0.0]) * age[:, None] ** 2) * sc
        al = on * np.clip(1.0 - age / self.life, 0.0, 1.0) * 0.85 * surge
        return dict(pos=p, size=0.16 * sc[:, 0], color=self.col, alpha=al.astype(np.float32), kind="flake",
                    rot=self.rot + np.array([1.1, 1.7], np.float32) * t, seed=self.sd, twinkle=0.7)


# ---------------------------------------------------------------------------------------------------------
# THE WORLD: one look per level (sky, air, mist), blending as we climb
# ---------------------------------------------------------------------------------------------------------
LOOKS = dict(
    lake=dict(base="night", sky_top="#01030f", sky_mid="#050f36", sky_hor="#13286a", sun_az=SUN_AZ, sun_el=-14.0,
              sun_int=0.10, stars=1.0, milky=0.9, clouds=0.04, haze=0.5, haze_color="#14204e", mist=0.55,
              mist_height=2.6, mist_color="#22306a", water="#010309", ripple=0.35, dust=0.7, dust_color="#cfe0ff",
              dust_color2="#ffd9a0", bokeh=0.5),
    mist=dict(base="night", sky_top="#020620", sky_mid="#0a1a4c", sky_hor="#2c3e84", sun_az=SUN_AZ, sun_el=-14.0,
              stars=0.9, milky=0.8, clouds=0.06, haze=0.55, haze_color="#2a3a7a", mist=1.0, mist_height=7.0,
              mist_color="#3a4c8c", water="#010309", ripple=0.35, dust=0.9, dust_color="#cfe0ff",
              dust_color2="#ffcfa0", bokeh=0.5),
    pillars=dict(base="night", sky_top="#03082a", sky_mid="#0b1650", sky_hor="#2a2f7a", sun_az=SUN_AZ, sun_el=-12.0,
                 stars=0.95, milky=0.7, clouds=0.10, haze=0.45, haze_color="#232a6a", mist=0.45, mist_height=3.0,
                 mist_color="#283070", water="#010309", ripple=0.3, dust=0.8, dust_color="#ffe2a8",
                 dust_color2="#fff0c8", bokeh=0.5),
    gate=dict(base="night", sky_top="#05103a", sky_mid="#12306e", sky_hor="#3c6aa8", sun_az=SUN_AZ, sun_el=-10.0,
              stars=0.75, milky=0.45, clouds=0.25, haze=0.5, haze_color="#2c4a86", mist=0.45, mist_height=3.5,
              mist_color="#2c4a86", water="#020512", ripple=0.3, dust=0.8, dust_color="#cfeaff",
              dust_color2="#ffd2b0", bokeh=0.5),
    violet=dict(base="night", sky_top="#0c0a30", sky_mid="#1c1456", sky_hor="#4a3488", sun_az=SUN_AZ, sun_el=-9.0,
                sun_color="#d8b8ff", sun_int=0.25, stars=0.35, milky=0.05, clouds=0.62, cloud_speed=2.2, haze=0.6,
                haze_color="#3a2a70", mist=0.6, mist_height=5.0, mist_color="#3a2a80", water="#030212", ripple=0.5,
                dust=1.0, dust_color="#e0c8ff", dust_color2="#ffd0e8", bokeh=0.5),
    cloud=dict(base="night", sky_top="#1c1c40", sky_mid="#2e2c5a", sky_hor="#4a4270", sun_az=SUN_AZ, sun_el=-3.0,
               sun_color="#ffd0dc", sun_int=0.3, stars=0.0, milky=0.0, clouds=0.9, haze=0.9, haze_color="#2e2c58",
               mist=0.9, mist_height=150.0, mist_color="#302e5c", hills=0.0, water="#1a1640", dust=0.9,
               dust_color="#ffe6ee", dust_color2="#cfd8ff", bokeh=0.7),
    cloudlit=dict(base="night", sky_top="#2c2850", sky_mid="#4a4070", sky_hor="#8a6c8c", sun_az=SUN_AZ,
                  sun_el=-1.0, sun_color="#ffd0dc", sun_int=0.5, stars=0.0, milky=0.0, clouds=0.9, haze=0.9,
                  haze_color="#4a4070", mist=0.9, mist_height=150.0, mist_color="#504470", hills=0.0,
                  water="#2a2050", dust=1.0, dust_color="#ffe6ee", dust_color2="#ffd0dc", bokeh=0.7),
    above=dict(base="sunrise", sky_top="#06144c", sky_mid="#18388e", sky_hor="#ffa050", sun_az=SUN_AZ_TRUE,
               sun_el=SUN_EL_TRUE,
               sun_color="#ffc870", sun_int=0.75, sun_disc=6.0, sun_glow=0.35, stars=0.25, milky=0.0, clouds=0.30,
               hills=0.0, haze=0.12, haze_color="#e8805c", mist=4.0, mist_height=26.0, mist_color="#a05a6c",
               water="#f0a080", rays=0.5, dust=0.6, dust_color="#ffe2a8", dust_color2="#ffd0a8", bokeh=0.6,
               exposure=1.0),
    card=dict(base="day", sky_top="#2f6fd6", sky_mid="#78b2ee", sky_hor="#ffe2bc", sun_az=SUN_AZ_TRUE, sun_el=9.0,
              sun_int=0.6, sun_glow=0.4, hills=0.0, haze=0.25, haze_color="#ffe6cc", mist=4.0, mist_height=26.0,
              mist_color="#e2ac98", rays=0.3, clouds=0.25, dust=0.5, water="#a9d4f4", exposure=1.0),
)

WORLD = WORDS.world(dict(
    looks=LOOKS,
    look=[(0.0, "lake"), (7.6, "mist", 1.6), (13.6, "pillars", 1.4), (20.6, "gate", 2.0), (28.0, "violet", 3.0),
          (39.3, "cloud", 1.2), (41.4, "cloudlit", 1.6), (BIG_HIT + 0.2, "above", 0.6), (50.6, "card", 3.6)],
    arch=dict(lit=_LIT, colors=[e["color"] for e in PW.EXPRESSIONS], line=Track([(0, 0.35), (NINTH, 0.35),
                                                                                  (NINTH + 1.5, 1.0), (60, 1.0)]),
              **ARCH_SET),
    shafts=[dict(base=(0.0, 0.0), radius=0.75, top=420.0, spread=0.6, color="#9cc4ff",
                 strength=Track([(0, 0.9), (2.6, 0.6), (S[2], 0.5), (S[5], 0.45), (38.6, 0.35), (40.0, 0.0),
                                 (60, 0.0)]))],
    light=dict(pos=tuple(SUN_LIGHT), color="#ffe0b0",
               strength=Track([(0, 0.0), (BIG_HIT, 0.0), (43.6, 0.32), (49.5, 0.3), (53.0, 0.15), (60, 0.12)]),
               size=0.45, rays=0.75),
    react=dict(beat=0.4, level=0.25),
    exposure=Track([(0, 1.0), (BIG_HIT - 0.05, 1.0), (BIG_HIT + 0.1, 1.6), (BIG_HIT + 0.9, 1.0), (43.8, 0.86),
                    (48.6, 0.86), (50.6, 1.0), (TITLE_HIT - 0.1, 1.0), (TITLE_HIT + 0.08, 1.12), (TITLE_HIT + 0.8, 1.0),
                    (FINAL_HIT - 0.1, 1.0), (FINAL_HIT + 0.08, 1.08), (FINAL_HIT + 0.7, 1.0), (60, 1.0)]),
))


def _setup(scene):
    _cast()
    scene.add("ring wave", RingWave(S[0], _L0[0]), reflect=False)
    scene.add("rings", Rings())
    scene.add("shaft flakes", ShaftFlakes(), reflect=False)
    scene.add("pillars", Pillars())
    scene.add("cloud top", CloudTop(), reflect=False)
    scene.add("cloud wisps", CloudWisps(), reflect=False)
    scene.add("fountains", Fountains(), reflect=False)
    for name, body in PEOPLE.items():
        body.add(scene, name, reflect=(Y_OF.get(name, 1.0) < 1.0))
    scene.add("flare", FLARE, reflect=False)
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


Y_OF = {"traveller 0": 0.0, "greeter": 0.0}     # only the people on the lake have a mirror image


P3D = dict(
    camera=CAMERA,
    world=WORLD,
    setup=_setup,
    bursts=[dict(t=S[0], at=tuple(_L0[0] + [0.0, 0.1, 0.0]), strength=0.55, radius=0.16, color="#cfe0ff", rise=0.15,
                 fall=0.7),
            dict(t=BIG_HIT, at=tuple(HANDS_AT), strength=1.3, radius=0.35, color="#fff0d6", rise=0.08, fall=0.9)],
)

# ---------------------------------------------------------------------------------------------------------
# THE END CARD (the existing end card style; not redesigned)
# ---------------------------------------------------------------------------------------------------------
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=TAG_T0, t1=TAG_T1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
# the concert badge (the same in all ten films): large on frame 0, in the top left corner by 2.8 s, fading as
# the end card forms (the end card carries the same lines)
CREDIT = dict(song="The Words of Mother’s Love",
              concert="Healing Concert · Sunday, December 6 · 4:30 PM",
              t_in=-1.0, t_full=0.0, t_move=1.6, t_rest=2.8, scale=0.56, alpha_rest=0.92,
              margin_x=0.035, margin_top=0.05, t_out=T_FORM, out_dur=1.0)
_CB = (0.1323, 0.8693, 0.4972, 0.6861)          # the badge's box at full size (text.render_credit)
BADGE = (CREDIT["margin_x"], CREDIT["margin_x"] + CREDIT["scale"] * (_CB[1] - _CB[0]) + 0.01, 0.0,
         CREDIT["margin_top"] + CREDIT["scale"] * (_CB[3] - _CB[2]) + 0.012)   # x0, x1, y0, y1 from the TOP


def credit_state(t, bbox):
    """Centre, scale and strength of the badge; bbox is its size at full card size (demo_gathering.py), with
    a fade as the end card starts to form."""
    c = CREDIT
    x0, x1, y0, y1 = bbox

    def ss(a, b, x):
        u = min(max((x - a) / (b - a), 0.0), 1.0)
        return u * u * (3 - 2 * u)

    a_in = ss(c["t_in"], c["t_full"], t)
    m = ss(c["t_move"], c["t_rest"], t)
    scale = c["scale"] ** m
    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    tx = c["margin_x"] + c["scale"] * (x1 - x0) / 2.0
    ty = 1.0 - c["margin_top"] - c["scale"] * (y1 - y0) / 2.0
    cx, cy = cx0 * (1 - m) + tx * m, cy0 * (1 - m) + ty * m
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(c["t_out"], c["t_out"] + c["out_dur"], t))
    return (cx, cy, scale, alpha), (cx0, cy0)


FRAGMENTS = []
_base.TITLE = TITLE
_base.TAGLINE = TAGLINE


# ---------------------------------------------------------------------------------------------------------
# The film checks itself (numpy only): python engine/songs/ten_06_ascension.py  (run from engine/)
# ---------------------------------------------------------------------------------------------------------
def _facing_check():
    """Nobody is seen from the front: the angle between a body's facing and the way to the camera."""
    worst = []
    for name, b in _cast().items():
        if b.show is None or "hand" in name:
            continue
        least = 180.0
        for t in np.arange(max(b.show[0], 0.0), min(b.show[1], TOTAL), 0.2):
            cs = CAMERA.state(t)
            at = b.where(t, "chest")
            xy, z = cs.project(at[None]) if hasattr(cs, "project") else (None, None)
            to = cs.pos - at
            if np.hypot(to[0], to[2]) < 0.6 * abs(to[1]):
                continue
            if z is not None and (z[0] <= 0.2 or np.abs(np.asarray(xy[0]) - 0.5).max() > 0.55):
                continue
            face = b.actor.heading(t) if hasattr(b.actor, "heading") else 0.0
            az = np.degrees(np.arctan2(to[0], to[2]))
            ang = abs((az - face + 180.0) % 360.0 - 180.0)
            least = min(least, ang)
        worst.append((least, name))
    return sorted(worst)


def layout(step=0.25, verbose=True):
    """Where each word sits on screen while it is read (x from the left, y from the TOP, 0..1), and whether it
    reaches the concert badge in the top left corner."""
    out = []
    for w in WORDS.words:
        top, x0, x1, y1 = 1.0, 1.0, 0.0, 0.0
        for t in np.arange(w.t_read0, w.t_read1 + 1e-6, step):
            cs = CAMERA.state(t)
            xy, z = cs.project(np.asarray(w.corners(t, cs, pad=0.0)))
            xy = np.asarray(xy)
            top = min(top, 1.0 - xy[:, 1].max())
            y1 = max(y1, 1.0 - xy[:, 1].min())
            x0, x1 = min(x0, xy[:, 0].min()), max(x1, xy[:, 0].max())
        hit = top < BADGE[3] and x0 < BADGE[1]
        out.append((w.name, top, y1, x0, x1, hit))
        if verbose:
            print("  %-14s top %.3f bottom %.3f  x %.3f to %.3f %s" % (w.name, top, y1, x0, x1,
                                                                    "COVERS THE BADGE" if hit else ""))
    return out


if __name__ == "__main__":
    layout()
    ts = np.arange(0, TOTAL + 1e-9, 1.0 / FPS)
    hs = np.array([cam_pos(t)[1] for t in ts])
    print("camera height %.2f to %.1f m, never falls: %s" % (hs[0], hs[-1], bool(np.diff(hs).min() >= -1e-9)))
    sp = [CAMERA.speed(t) for t in np.arange(0.05, TOTAL, 0.25)]
    print("speed up to %.1f m/s, turn up to %.0f deg/s" % (max(s[0] for s in sp), max(s[1] for s in sp)))
    WORDS.check(CAMERA)
    for least, name in _facing_check():
        print("  %-16s least angle to the camera %5.1f deg" % (name, least))
