"""NINE COLOURS FINAL: Film 10 render 1 (run 43726203825, ten/10-nine-colours at d928ff9), remade with every
improvement since (Anthony: "make the same video but with all the improvements such as better models and
animation, the text additions, beginning and ending cards"). A 62 second promo for the Healing Concert "The
Words of Mother's Love That Bring Peace", on the original eight-song medley with a 2 s quiet lead-in
(audio/promo/concert-medley-leadin.mp3).

THE IDEA (as in render 1)
  Mother's love is one white light and her nine words are its colours. A white seed bursts into nine comets,
  one in each campaign colour; we chase them like a rollercoaster while each one writes its words in the air
  and wraps the people who live them; at the end all nine braid round us as we corkscrew up to the whole Earth,
  which they wrap and leave with hearts until it becomes the logo, and the day blooms into the end card.

THE CLOCK. Render 1's cues are kept on their own clock (the "old" time, every constant below) and played 2.0 s
later (OFF): the medley's first hit (old 0.25) lands at 2.25. Times below are old (add 2.0 for the film):
  -2.0   Frame 0: the white seed blazes low over a black mirror lake under the opening title (logo, title,
         date and time, Las Vegas), the camera drifting in through the quiet lead-in.
  0.25   On the opening hit it bursts flat into nine comets that fan out low across the sky (never over the
         title); we launch after the coral comet, low over the water at 24 m/s. The title holds to 5.0.
  5.0    The coral comet writes the GREETING as we ride on.
  6.84   THE GATE: the blue comet writes the CONCESSION, then races ahead stitching half hoops over the water,
         one a beat; we fly through the tunnel.
  13.30  THE EMBRACE: we brake into a spiral round two women in warm mist: one sits back, head bowed (APOLOGY,
         written by the yellow comet); the other kneels and lays a hand gently on her back; she lifts her head;
         they rise and hold each other (INCLUSIVENESS) while the two comets wrap them in a double helix.
  19.85  THE DANCER (bass slam): she turns, her arms opening in a soft arc, leading the navy ribbon from her
         hand; it writes the COMPLIMENT. Then the HALF LOOP: up the wall and over, the starred lake above us.
  26.79  THE DROP: over the crest and down the dive with the CONSIDERATION riding ahead; a helper reaches a hand
         to a child; the child blows gold from an open palm (GRATITUDE) while lanterns wake and rise.
  33.36  THE TWO: an arc round two people of light, one speaking, one listening; the comet weaves between them
         and writes the RESPECT.
  40.21  THE BREATH: someone kneels in prayer in a shaft of violet light; the ENCOURAGEMENT is whole on the
         biggest hit (42.51), when the eight other comets race in and circle; the nine braid round the column
         and we corkscrew straight up inside them.
  49.47  THE WORLD: out of the braid to the whole Earth hanging in the night; the comets wrap it and leave hearts,
         the nine symbols swirl round it; it becomes the logo between two hearts, light blooms into a soft
         pastel day, and the logo glides into the end card, whole from 53.0 (55.0 in the film) to the last frame,
         alive, with a warm glow on the final chord.

HOUSE RULES: people only in warm gold glitter, whole, with living hands; the greeting and every embrace between
two of the same gender (UPDATE 15), except parent and child; Heavenly Mother only as light (the seed); all nine
expressions by name, written by their own comets as the pen, website colours, pills, read 2.5 s or more, one at
a time, upper middle, never mirrored, nothing crossing them; nothing dark behind text; no white-outs; frame 0
striking; no fade to black. The signature stays on in the bottom left (effects may pass behind it).
"""
import numpy as np

import songs.s03_original as _base

OFF = 2.0                   # the quiet lead-in: render 1's clock runs this much later
TOTAL = 62.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 61.6
_base.SONG_END = 62.0
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
from p3d import brand as BR  # noqa: E402
from p3d.camera import Move, Rig, fly  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley-leadin.mp3"
TOTAL = 62.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 61.6
SONG_END = 62.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0           # nothing dark behind any text
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE
OLD_END = TOTAL - OFF

# the medley's sections and hits (scratchpad/medley2/SECTION-MAP.md), on render 1's clock
SEC = [0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47]
BREATH_END = 42.51
FINAL_HIT = 58.11

# the nine colours (words.COLORS, the campaign website), in words.LABELS order; the deep navy glows brighter
LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]
GLOW = list(COL)
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)
GLOW[COMP] = "#5872D2"
WHITE = "#fff6e6"
GOLD = dict(look="glitter", color="#f2a640", color2="#ffdc96", bright=1.45)          # the one radiant look
GOLD2 = dict(look=dict(name="glitter", seams=0.6), color="#ffc664", color2="#fff0c8", bright=1.45)


def deepen(hexs, k=1.35):
    """The same hue with more saturation (linear light): a ribbon trail that stays its colour when it glows."""
    c = lin(hexs)
    m = float(c.max())
    return m * (c / m) ** k


def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


UP = _v(0.0, 1.0, 0.0)


def _unit(a):
    a = np.asarray(a, np.float64)
    return a / max(float(np.linalg.norm(a)), 1e-9)


def lerp(a, b, u):
    return np.asarray(a, np.float64) * (1.0 - u) + np.asarray(b, np.float64) * u


def _slerp(d0, d1, u):
    om = float(np.arccos(np.clip(d0 @ d1, -1.0, 1.0)))
    return d0 if om < 1e-6 else (np.sin((1.0 - u) * om) * d0 + np.sin(u * om) * d1) / np.sin(om)


# ---------------------------------------------------------------------------------------------------------
# The places
# ---------------------------------------------------------------------------------------------------------
SEED = _v(0.0, 2.2, 300.0)          # the white seed
SPEED = 24.0                        # the chase over the lake, metres a second
Z22 = 296.0                         # the camera's z at 2.2 s; from then on it flies at SPEED toward -z


def zcam(t):
    return Z22 - SPEED * (t - 2.2)


HOOP_R = 6.5                        # the gate: half hoops of the blue comet's trail
HOOP_GAP = SPEED * 60.0 / 84.0      # one hoop a beat at 84 bpm
HOOPS = 6
TUNNEL_T0 = 9.3                     # the blue comet starts stitching (after it has written the Concession)
TUNNEL_Z0 = zcam(8.7) - 34.0
TUNNEL_V = 50.0                     # its speed along the tunnel
C3 = _v(0.0, 0.0, 6.0)              # the embrace
D4 = _v(-90.0, 0.0, -60.0)          # the dancer
E5 = _v(90.0, 0.0, -70.0)           # the child and the helper; the lantern field
F6 = _v(90.0, 0.0, -40.0)           # the two (looking -z: the lanterns behind them)
G7 = _v(0.0, 0.0, 2.0)              # the one who prays; the foot of the braid

# ---------------------------------------------------------------------------------------------------------
# The camera (render 1's journey; the lead-in drifts in on the seed, which sits low under the title)
# ---------------------------------------------------------------------------------------------------------


class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _flight_keys():
    lift = _v(0.0, 1.7, 0.0)                       # look above the seed: it blazes low, under the title
    keys = [(-2.0, _v(0.35, 2.45, 310.4), SEED + lift),
            (0.00, _v(0.35, 2.32, 307.8), SEED + lift),
            (0.25, _v(0.35, 2.30, 307.4), SEED + lift),
            (0.85, _v(-1.4, 3.30, 311.0), _v(0.0, 4.2, 292.0)),
            (1.50, _v(-0.9, 2.50, 307.5), _v(0.0, 3.2, 284.0)),
            (2.20, _v(0.3, 1.90, Z22), _v(0.0, 2.6, Z22 - 24.0))]
    for t in np.arange(2.7, 13.31, 0.5):
        tun = _sc(9.1, 10.1, t) * (1.0 - _sc(12.6, 13.3, t))
        x = 1.3 * np.sin(0.85 * t + 0.4) * (1.0 - 0.75 * tun)
        y = 1.65 + 0.25 * np.sin(1.3 * t) + 1.05 * tun
        z = zcam(t)
        keys.append((float(t), _v(x, y, z), _v(0.35 * x, y + 0.45 - 0.2 * tun, z - 24.0)))
    return keys


def _roll_s12(t):
    return 7.0 * np.sin(0.85 * t + 1.9) * _sc(5.0, 6.0, t) + 9.0 * np.sin(1.1 * t) * _sc(9.1, 10.1, t)


def _s3(t):
    """Brake into a descending spiral round the two."""
    u = t - SEC[2]
    r = 3.85 - 0.1 * u + 20.0 * np.exp(-u / 0.42)
    h = 1.75 + 0.5 * np.exp(-u / 1.0) - 0.03 * u
    a = np.radians(-38.0 + 36.0 * (1.0 - np.exp(-u / 0.6)) + 17.0 * u)
    p = C3 + _v(np.sin(a) * r, h, np.cos(a) * r)
    return p, C3 + _v(0.0, 1.2 + 0.5 * _sc(16.4, 18.2, t), 0.0)     # the gaze rises as they stand


LOOP_T0, LOOP_T1, LOOP_R = 25.0, SEC[4], 12.0


def _s4_orbit(t):
    u = t - SEC[3]
    r = 6.0 - 0.15 * u
    h = 1.25 + 0.08 * u
    a = np.radians(25.0 + 24.0 * u)
    return D4 + _v(np.sin(a) * r, h, np.cos(a) * r), D4 + _v(0.0, 1.6, 0.0)


def _loop_frame():
    p0, q0 = _s4_orbit(LOOP_T0)
    p1, _ = _s4_orbit(LOOP_T0 + 0.05)
    h = _unit(_v(p1[0] - p0[0], 0.0, p1[2] - p0[2]))    # the orbit's direction of travel
    return p0, h


def _loop_phi(t):
    u = np.clip((t - LOOP_T0) / (LOOP_T1 - LOOP_T0), 0.0, 1.0)
    return np.pi * (0.15 * u + 0.85 * u * u) * 1.02


def _s4(t):
    if t <= LOOP_T0:
        return _s4_orbit(t)
    p0, h = _loop_frame()
    phi = _loop_phi(t)
    pos = p0 + LOOP_R * np.sin(phi) * h + LOOP_R * (1.0 - np.cos(phi)) * UP
    tan = np.cos(phi) * h + np.sin(phi) * UP
    cen = -np.sin(phi) * h + np.cos(phi) * UP
    w = _sc(LOOP_T0, LOOP_T0 + 1.0, t)
    _, q0 = _s4_orbit(t)
    look = pos + 20.0 * _unit(np.cos(0.35) * tan + np.sin(0.35) * cen)
    return pos, q0 * (1.0 - w) + look * w


def _s4_up(t):
    if t <= LOOP_T0:
        return UP
    _, h = _loop_frame()
    phi = _loop_phi(t)
    return _unit(-np.sin(phi) * h + np.cos(phi) * UP)


def _s5_keys():
    return [(SEC[4], E5 + _v(-4.0, 30.0, 52.0), E5 + _v(-2.0, 27.0, 20.0)),
            (27.30, E5 + _v(-3.5, 27.5, 46.0), E5 + _v(0.0, 8.0, 4.0)),
            (28.30, E5 + _v(-2.6, 18.0, 33.0), E5 + _v(0.0, 4.0, 0.0)),
            (29.30, E5 + _v(-1.6, 8.0, 18.0), E5 + _v(0.0, 2.6, 0.0)),
            (30.15, E5 + _v(-1.0, 2.6, 7.6), E5 + _v(0.0, 1.9, 0.0)),
            (31.20, E5 + _v(1.0, 2.0, 5.9), E5 + _v(0.0, 2.0, 0.0)),
            (32.30, E5 + _v(2.4, 2.2, 5.6), E5 + _v(0.0, 2.1, 0.0)),
            (33.40, E5 + _v(3.6, 2.6, 5.2), E5 + _v(0.0, 2.2, 0.0))]


def _s6(t):
    """An arc round the two, waist up, the lanterns behind them."""
    u = (t - SEC[5]) / (SEC[6] - SEC[5])
    a = np.radians(-24.0 + 46.0 * u)
    r = 3.4 - 0.35 * u
    return F6 + _v(np.sin(a) * r, 1.6, np.cos(a) * r), F6 + _v(0.0, 1.35, 0.0)


def _s7_breath(t):
    u = _sc(SEC[6], BREATH_END + 0.2, t)
    p = _v(6.5, 6.2, 18.0) * (1.0 - u) + _v(2.4, 2.1, 9.6) * u
    return p, G7 + _v(0.0, 1.6, 0.0)


ORB7_A0 = float(np.degrees(np.arctan2(2.4, 9.6 - G7[2])))
BRAID_T0 = 45.4


def _orb7_tables():
    ts = np.arange(BREATH_END, OLD_END + 2.0, 0.004)
    u = ts - BREATH_END
    e = _ss(BRAID_T0, BRAID_T0 + 1.5, ts)
    cam = (44.0 + 8.0 * u) * (1.0 - e) + 22.0 * e                  # degrees a second
    ext = 0.0 * e                                                   # the comets' extra turn, radians a second
    ang = ORB7_A0 + np.concatenate([[0.0], np.cumsum(0.5 * (cam[1:] + cam[:-1]) * np.diff(ts))])
    ex = np.concatenate([[0.0], np.cumsum(0.5 * (ext[1:] + ext[:-1]) * np.diff(ts))])
    return ts, np.radians(ang), ex


_ORB7_T, _ORB7_A, _BRAID_X = _orb7_tables()


def _orb7_angle(t):
    return float(np.interp(t, _ORB7_T, _ORB7_A))


def _orb7_radius(t):
    return 7.7 - 0.25 * max(t - BREATH_END, 0.0)


def _y_climb(t):
    u = max(t - BRAID_T0, 0.0)
    return 2.1 + 2.0 * u + 7.4 * u * u


def _s7_orbit(t):
    a, r = _orb7_angle(t), _orb7_radius(t)
    p = G7 + _v(np.sin(a) * r, 2.1, np.cos(a) * r)
    return p, G7 + _v(0.0, 1.9, 0.0)


def _braid_tilt(t):
    return np.radians(88.0) * _sc(BRAID_T0 + 0.1, BRAID_T0 + 2.0, t) + np.radians(3.0)


def _s7_braid(t):
    u = max(t - BRAID_T0, 0.0)
    a = _orb7_angle(t)
    r = 0.7 + (_orb7_radius(BRAID_T0) - 0.7) * np.exp(-u / 0.55)
    p = G7 + _v(np.sin(a) * r, _y_climb(t), np.cos(a) * r)
    h = _unit(_v(G7[0] - p[0], 0.0, G7[2] - p[2]))
    b = _braid_tilt(t)
    return p, p + 20.0 * (np.cos(b) * h + np.sin(b) * UP)


def _s7_up(t):
    if t < BRAID_T0:
        return UP
    p, _ = _s7_braid(t)
    h = _unit(_v(G7[0] - p[0], 0.0, G7[2] - p[2]))
    b = _braid_tilt(t)
    return _unit(-np.sin(b) * h + np.cos(b) * UP)


# ---- the finale: out of the braid to the whole Earth; it becomes the logo, the day blooms, the end card --------
SUN_AZ = 180.0
HV = _v(np.sin(np.radians(SUN_AZ)), 0.0, np.cos(np.radians(SUN_AZ)))
FIN_R = 9.0
FIN_SHRINK = 0.47
FIN_C = G7 + _v(0.0, 205.0, 0.0) + HV * 50.0      # it hangs in the night above the braid
FIN_T = 49.5
SWIRL = (49.5, 51.2)
HEARTS_T0, HEARTS_T1 = 49.7, 51.0
SETTLE = (50.5, 51.9)
LOGO_T = (51.2, 52.3)
BLOOM_T = 51.85
END_FOV = 50.0
EC_SCALE = 1.0
SLOT_Y = (48.0 + 85.0 - 540.0) * EC_SCALE / 1080.0 + 0.5   # the end card logo's middle, from the top
SLOT_H = 170.0 * EC_SCALE / 1080.0
END_T0, END_T = 52.3, 52.8                       # the logo glides into the end card's logo slot
EC_IN, EC_FADE = 52.3, 0.7                       # the end card: whole from 53.0 (55.0 in the film) to the end
LIFT_END = 51.0
FOV_TOP = 82.0
PUSH = (EC_IN + EC_FADE, OLD_END)


def _end_fov(t):
    return END_FOV * (1.0 - 0.03 * _sc(PUSH[0], PUSH[1], t))


def _fin_scale(t):
    return 1.0 - (1.0 - FIN_SHRINK) * _sc(SETTLE[0] - 0.4, SETTLE[1], t)


def _fin_cam(az, el, d):
    a, e = np.radians(az), np.radians(el)
    back = -HV
    side = _unit(np.cross(UP, back))
    return FIN_C + d * (np.cos(e) * (np.cos(a) * back + np.sin(a) * side) + np.sin(e) * UP)


_LOGO_DROP = 0.1624 * FIN_R * FIN_SHRINK / 0.3058
FIN_LIFT = 0.17 * FIN_R


def _hermite(p0, v0, p1, v1, T, x):
    x = float(np.clip(x, 0.0, 1.0))
    return ((2 * x ** 3 - 3 * x ** 2 + 1) * p0 + (x ** 3 - 2 * x ** 2 + x) * T * v0
            + (3 * x ** 2 - 2 * x ** 3) * p1 + (x ** 3 - x ** 2) * T * v1)


def _s8(t):
    """Out of the braid with its climb carried on (never a stop), easing round to the world as it settles, then
    a slow drift in as it becomes the logo, and the gentle rise under the end card."""
    p_a, q_a = _s7_braid(SEC[7])
    v_a = (p_a - _s7_braid(SEC[7] - 0.02)[0]) / 0.02
    p_c = _fin_cam(4.0, -3.0, 4.2 * FIN_R)
    p_d = _fin_cam(8.0, 1.0, 3.9 * FIN_R) - _v(0.0, _LOGO_DROP, 0.0)
    T1, T2 = LOGO_T[0] - SEC[7], LOGO_T[1] - LOGO_T[0]
    v_c = 1.2 * (p_d - p_c) / T2
    tgt = FIN_C - _v(0.0, FIN_LIFT, 0.0)
    tgt_logo = FIN_C - _v(0.0, _LOGO_DROP + 1.0 * FIN_LIFT, 0.0)
    if t < LOGO_T[0]:
        pos = _hermite(p_a, v_a, p_c, v_c, T1, (t - SEC[7]) / T1)
        d = _slerp(_unit(q_a - p_a), _unit(tgt - pos), _sc(SEC[7] - 0.1, LOGO_T[0] - 0.1, t))
        return pos, pos + 30.0 * d
    if t < LOGO_T[1]:
        e = _sc(LOGO_T[0] - 0.1, LOGO_T[1], t)
        return _hermite(p_c, v_c, p_d, 0.0 * v_c, T2, (t - LOGO_T[0]) / T2), lerp(tgt, tgt_logo, e)
    e = _sc(LOGO_T[1], OLD_END, t)
    return p_d + e * _v(0.0, 1.5, 0.0) + e * 2.0 * HV, tgt_logo + e * _v(0.0, 2.5, 0.0)


def _s8_up(t):
    """From the braid's up (we look straight up as we leave it) back to the world's up as the gaze comes down."""
    u0 = _s7_up(SEC[7])
    p, q = _s8(t)
    f = _unit(q - p)
    u = _unit(lerp(u0, UP, _sc(SEC[7], LIFT_END - 0.1, t)))
    u = u - (u @ f) * f
    n = np.linalg.norm(u)
    return u / n if n > 1e-6 else UP


def _rig(focus):
    def fo(default):
        return (lambda t: focus(t, default)) if focus is not None else "target"

    return Rig([
        fly(_flight_keys(), fov=lambda t: 50.0 + 12.0 * _sc(0.3, 2.2, t) - 4.0 * _sc(8.5, 9.5, t),
            roll=_roll_s12, aperture=lambda t: 0.012 * (1.0 - _sc(0.4, 1.6, t)) + 0.004,
            focus=fo(lambda t: SEED if t < 1.2 else np.asarray(PW.place(_LAYOUT_SIMPLE, t, 0.5, 0.5, 14.0)))),
        Path(_s3, SEC[2], SEC[3], blend=0.9, fov=lambda t: 56.0 - 10.0 * _sc(13.3, 14.4, t), roll=0.0,
             aperture=0.015, focus=fo(C3 + _v(0, 1.0, 0))),
        Path(_s4, SEC[3], SEC[4], blend=0.0, fov=lambda t: 52.0 + 22.0 * _sc(LOOP_T0, LOOP_T1, t),
             up=_s4_up, aperture=lambda t: 0.015 * (1.0 - _sc(LOOP_T0 - 0.7, LOOP_T0, t)),
             focus=fo(lambda t: D4 + _v(0, 1.2, 0))),
        fly(_s5_keys(), blend=0.0, fov=lambda t: 62.0 - 14.0 * _sc(29.0, 30.6, t),
            aperture=lambda t: 0.004 + 0.012 * _sc(29.5, 30.5, t),
            roll=lambda t: -10.0 * np.sin(np.pi * _sc(26.9, 29.6, t)), focus=fo(E5 + _v(0, 1.1, 0))),
        Path(_s6, SEC[5], SEC[6], blend=0.0, fov=40.0, aperture=0.015, focus=fo(F6 + _v(0, 1.4, 0))),
        Path(_s7_breath, SEC[6], BREATH_END, blend=0.0, fov=48.0, aperture=0.012, focus=fo(G7 + _v(0, 1.0, 0))),
        Path(_s7_orbit, BREATH_END, BRAID_T0, blend=0.9, fov=52.0, aperture=0.01, focus=fo(G7 + _v(0, 1.0, 0))),
        Path(_s7_braid, BRAID_T0, SEC[7], blend=0.5, up=_s7_up, fov=lambda t: 64.0 + (FOV_TOP - 64.0) * _sc(46.0, 49.4, t),
             aperture=0.0, focus=30.0),
        Path(_s8, SEC[7], OLD_END + 1.0, blend=0.0, up=_s8_up,
             fov=lambda t: (FOV_TOP + (END_FOV - FOV_TOP) * _sc(SEC[7], LIFT_END, t)) if t < PUSH[0] else _end_fov(t),
             aperture=0.0, focus=40.0),
    ], blend=0.6, fov=50.0, aperture=0.01, handheld=0.12, min_height=0.3)


_LAYOUT_SIMPLE = None
_LAYOUT_SIMPLE = _rig(None)          # the camera without the words' focus: for layout and comet paths
_LAYOUT = _LAYOUT_SIMPLE


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


# ---------------------------------------------------------------------------------------------------------
# The people: warm gold glitter, whole, with living hands and the refined acting (master_acting)
# ---------------------------------------------------------------------------------------------------------
_BODIES = {}


EMB_TURN = 85.0


def _embrace_pair(o, t_touch, t_look, t_rise, t_hold, until):
    """APOLOGY then INCLUSIVENESS (two women). One sits back on her heels, head bowed, hands in her lap; the
    other kneels beside her, leans in and lays her hand gently on her back, the arm rounded; after a beat the
    seated one lifts her head toward her; they rise together, turn to each other and hold each other."""
    from p3d import pairs
    from p3d.body import Body
    refs = {}
    gap, side = 0.24, 0.085
    kb_k, fb_k = (o[0] + 0.25, o[2] + 0.02), 58.0
    ka_k, fa_k = (o[0] - 0.30, o[2] - 0.06), 74.0
    ph = np.radians(EMB_TURN)           # the embrace is turned so that the spiral sees it in profile
    cph, sph = np.cos(ph), np.sin(ph)

    def turned(dx, dz):
        return (o[0] + dx * cph + dz * sph, o[2] - dx * sph + dz * cph)
    ka_e = turned(-0.5 * gap, -side)
    kb_e = turned(0.5 * gap, side)
    up_a, up_b = 1.45, 1.55
    t_ra, t_rb = t_rise, t_rise + 0.2
    s0 = t_hold - 0.9
    show = (t_touch - 1.6, until)

    def on(name, fn, guess):
        return lambda tt: fn(refs[name], tt) if name in refs else np.asarray(guess, np.float64)

    def her_back(B, tt):
        bl, n = B.where(tt, "blade.R", normal=True, raw=True)
        sh = B.where(tt, "shoulder.R", raw=True)
        return 0.6 * bl + 0.4 * sh + 0.015 * n
    a = dict(shape="woman", garment="dress", hair="bun",
             at=[(0.0, ka_k), (s0, ka_k), (t_hold + 0.1, ka_e)],
             facing=[(0.0, fa_k), (s0 - 0.3, fa_k), (t_hold + 0.2, 90.0 + EMB_TURN)],
             motion=[(-1e9, "kneel", dict(dur=0.01, sit=0.85, hands="free")),
                     (t_ra, "rise_up", dict(dur=up_a, sit=0.85, blend=0.15)),
                     (s0, "shuffle", dict(blend=0.45, amount=0.3)), (t_hold + 0.15, "stand", dict(blend=0.6))],
             gesture=[(-1e9, t_ra + 0.3, "lap", dict(ease_out=0.9)),
                      (t_touch, t_ra + 0.35, "comfort",
                       dict(side="R", to=on("b", her_back, o + _v(0.12, 1.0, 0.08)), lean=9.0, bow=8.0,
                            ease_in=1.3, ease_out=0.9))],
             points=75000, show=show, fade=0.6, seed=61.0, wind=(0.2, 0.0, -0.1), **GOLD)
    b = dict(shape="woman", garment="dress", hair="bob",
             at=[(0.0, kb_k), (s0, kb_k), (t_hold + 0.1, kb_e)],
             facing=[(0.0, fb_k), (s0 - 0.3, fb_k), (t_hold + 0.2, -90.0 + EMB_TURN)],
             motion=[(-1e9, "kneel", dict(dur=0.01, sit=0.85, hands="free")),
                     (t_rb, "rise_up", dict(dur=up_b, sit=0.85, blend=0.15)),
                     (s0, "shuffle", dict(blend=0.45, amount=0.35)), (t_hold + 0.15, "stand", dict(blend=0.6))],
             gesture=[(-1e9, t_rb + 0.35, "lap", dict(ease_out=1.0)),
                      (-1e9, t_look + 0.4, "bow", dict(amount=24.0, ease_out=1.2)),
                      (t_look, t_hold + 0.2, "look_to",
                       dict(to=on("a", lambda A, tt: A.where(tt, "head", raw=True), o + _v(-0.30, 1.0, -0.04)),
                            up=2.0, ease_in=1.4, ease_out=0.8))],
             points=75000, show=show, fade=0.6, seed=62.0, wind=(0.2, 0.0, -0.1), **GOLD2)

    def back(name, side_, drop):
        def f(X, tt):
            bl, br = X.where(tt, "blade.L", raw=True), X.where(tt, "blade.R", raw=True)
            c = 0.5 * (bl + br)
            u = (bl - br) if side_ == "L" else (br - bl)
            return c + 0.38 * u - _v(0.0, drop, 0.0)
        return on(name, f, o + _v(0.0, 1.1, 0.0))
    end = until + 1.0
    a["gesture"] = a["gesture"] + [
        (t_hold, end, "embrace", dict(to=back("b", "R", 0.0), to2=back("b", "L", 0.0), head="L", ease=1.1)),
        (t_hold + 1.0, end, "sway", dict(period=3.6, amount=1.6, ease_in=1.2))]
    b["gesture"] = b["gesture"] + [
        (t_hold + 0.12, end, "embrace", dict(to=back("a", "R", 0.10), to2=back("a", "L", 0.10), head="L",
                                             ease=1.15)),
        (t_hold + 1.0, end, "sway", dict(period=3.6, amount=1.6, phase=0.5, ease_in=1.2))]
    A = Body(**a)
    refs["a"] = A
    B = Body(**b)
    refs["b"] = B
    pairs._built(A, B)
    return A, B


GREET_AT = _v(-7.5, 0.0, 296.0 - SPEED * (8.3 - 2.2))     # we ride past them on the left at 8.3
GREET_BOW = (7.3, 8.6)


def _greeting_pair(o, t0, t1):
    """GREETING (two men): they stand on the water facing each other and each gives a slight, warm bow, a gentle
    dip of the head and shoulders that comes back up to a small nod, as we ride past; no touch."""
    from p3d.body import Body
    a = Body("man", at=(o[0] - 0.55, o[2]), facing=90.0, garment="tunic", points=70000, show=(t0 - 1.0, t1 + 0.8),
             fade=0.6, seed=21.0,
             gesture=[(t0, t1 + 0.8, "greet_bow", dict(amount=17.0, down=0.95, hold=0.55, up=1.1, ease_in=0.5,
                                                       ease_out=1.0)),
                      (t0 + 2.4, t1 + 0.8, "nod", dict(period=2.6, amount=4.0, ease_in=1.0))], **GOLD)
    b = Body("man", at=(o[0] + 0.55, o[2]), facing=270.0, garment="coat", points=70000, show=(t0 - 1.0, t1 + 0.8),
             fade=0.6, seed=22.0,
             gesture=[(t0 + 0.4, t1 + 0.8, "greet_bow", dict(amount=15.0, down=1.0, hold=0.5, up=1.1, ease_in=0.5,
                                                             ease_out=1.0)),
                      (t0 + 2.8, t1 + 0.8, "nod", dict(period=2.9, amount=4.0, ease_in=1.0))], **GOLD2)
    return a, b


def _bodies():
    if _BODIES:
        return _BODIES
    from p3d import master_acting  # noqa: F401  (registers the refined gestures: comfort, dance, look_to, ...)
    from p3d.body import Body
    _BODIES["greet_a"], _BODIES["greet_b"] = _greeting_pair(GREET_AT, *GREET_BOW)
    A, B = _embrace_pair(C3, 14.0, 15.4, 16.5, 17.7, 20.4)
    _BODIES["kind"], _BODIES["sorry"] = A, B
    view4 = 25.0                          # the orbit sees her first from 25 degrees
    _BODIES["dancer"] = Body("woman", at=(D4[0], D4[2]), garment="dress", hair="bun",
                             facing=[(0.0, view4 - 25.0), (SEC[3] + 0.9, view4 - 25.0),
                                     (SEC[3] + 2.5, view4 + 335.0)],
                             motion=[(-1e9, "stand")],
                             gesture=[(SEC[3], LOOP_T1 + 1.0, "dance", dict(ease_in=0.3, ease_out=1.3)),
                                      (SEC[3] + 2.8, LOOP_T1 + 1.0, "sway", dict(period=3.2, amount=2.0,
                                                                                  ease_in=1.0))],
                             points=95000, show=(SEC[3] - 0.15, LOOP_T1 + 0.3), fade=0.4, seed=9.0,
                             **dict(GOLD2, bright=1.8))
    _BODIES["child"] = Body("child", at=(E5[0] - 0.35, E5[2] + 0.1), facing=120.0, motion="stand", garment="tunic",
                            points=50000, show=(SEC[4] + 0.6, SEC[5] + 0.3), fade=0.4, seed=7.0,
                            gesture=[(SEC[4] + 0.6, 30.3, "offer", dict(side="R")),
                                     (30.4, 40.0, "blow", dict(side="R"))], **GOLD2)
    _BODIES["helper"] = Body("man", at=(E5[0] + 0.55, E5[2] - 0.15), facing=300.0, motion="stand",
                             garment="coat", points=60000, show=(SEC[4] + 0.6, SEC[5] + 0.3), fade=0.4, seed=8.0,
                             gesture=[(SEC[4] + 1.0, 30.9, "touch", dict(side="R", to=lambda t: _touch5(t),
                                                                         palm="down"))], **GOLD)
    _BODIES["speaker"] = Body("woman", at=(F6[0] - 0.43, F6[2]), facing=90.0, motion="stand", garment="dress",
                              hair="bun", points=80000, show=(SEC[5] - 0.2, SEC[6] + 0.2), fade=0.4, seed=9.5,
                              gesture=[(SEC[5], 40.0, "offer", dict(side="L"))], **GOLD2)
    _BODIES["listener"] = Body("woman", at=(F6[0] + 0.43, F6[2]), facing=270.0, motion="stand", garment="dress",
                               hair="bob", points=80000, show=(SEC[5] - 0.2, SEC[6] + 0.2), fade=0.4, seed=10.0,
                               gesture=[(SEC[5] + 1.0, 40.0, "listen", dict(side="L"))], **GOLD)
    _BODIES["praying"] = Body("woman", at=(G7[0], G7[2]), facing=180.0, motion=[(37.0, "kneel")],
                              gesture=[(37.0, 60.0, "pray")], garment="robe", veil=True, points=75000,
                              show=(SEC[6] - 0.1, BRAID_T0 + 0.7), fade=0.8, seed=11.0, **GOLD)
    return _BODIES


def _touch5(t):
    """Where the helper's hand and the child's hand meet: the child's open palm."""
    return np.asarray(_bodies()["child"].where(min(t, 30.3), "palm.R"), np.float64) + _v(0.0, 0.03, 0.0)


# ---------------------------------------------------------------------------------------------------------
# The nine comets: each head is a function of time made of legs blended into a base path
# ---------------------------------------------------------------------------------------------------------
BURST_AZ = [180.0 + (k - 4) * 26.0 for k in range(9)]
BURST_EL = [1.0 + 1.5 * ((k * 5) % 4) for k in range(9)]      # low over the water, under the opening title
RING_R = [470.0 + 30.0 * k for k in range(9)]
RING_Y = [10.0 + 7.0 * ((k * 2) % 5) for k in range(9)]
RING_W = [0.11 if k % 2 == 0 else -0.10 for k in range(9)]


def _burst_dir(k):
    a, e = np.radians(BURST_AZ[k]), np.radians(BURST_EL[k])
    return _v(np.sin(a) * np.cos(e), np.sin(e), np.cos(a) * np.cos(e))


def _ring0(k):
    p = SEED + 260.0 * _burst_dir(k)
    return float(np.arctan2(p[0], p[2]))


RING_A0 = [_ring0(k) for k in range(9)]


def _ring(k, t):
    a = RING_A0[k] + RING_W[k] * (t - 3.0)
    return _v(np.sin(a) * RING_R[k], RING_Y[k] + 4.0 * np.sin(0.6 * t + k), np.cos(a) * RING_R[k])


def _burst(k, t):
    u = max(t - SEC[0], 0.0)
    d = 95.0 * (1.0 - np.exp(-u * 1.6)) + 30.0 * u
    return SEED + d * _burst_dir(k) + _v(0.0, -0.4 * u, 0.0)


def _base_path(k):
    def f(t):
        w = _sc(1.4, 3.6, t)
        if w <= 0.0:
            return _burst(k, t)
        if w >= 1.0:
            return _ring(k, t)
        return _burst(k, t) * (1.0 - w) + _ring(k, t) * w
    return f


class Head:
    """A comet head: a base path with legs [(t0, t1, f, blend in, blend out)] blended over it."""

    def __init__(self, k):
        self.k = k
        self.base = _base_path(k)
        self.legs = []

    def leg(self, t0, t1, f, bi=0.6, bo=0.8):
        self.legs.append((float(t0), float(t1), f, float(bi), float(bo)))
        return self

    def __call__(self, t):
        p = self.base(t)
        for t0, t1, f, bi, bo in self.legs:
            if t < t0 - bi or t > t1 + bo:
                continue
            w = (_sc(t0 - bi, t0, t) if bi > 0 else float(t >= t0)) * \
                (1.0 - (_sc(t1, t1 + bo, t) if bo > 0 else float(t > t1)))
            if w > 0.0:
                p = p * (1.0 - w) + np.asarray(f(t), np.float64) * w
        return p


HEADS = [Head(k) for k in range(9)]


def _pen(name):
    w = [x for x in WORDS if x.name == name][0]
    return lambda t: np.asarray(w.pen(t, PW._cam_at(_LAYOUT, t)), np.float64)


def _screen(x, y, depth, wx=0.0, wy=0.0, rate=1.0):
    return lambda t: place(t, x + wx * np.sin(rate * t * 1.7), y + wy * np.sin(rate * t * 2.3 + 1.0), depth)


def _helix(c, r, y0, y1, w, ph, rate_y=1.1):
    def f(t):
        a = w * t + ph
        rr = r(t) if callable(r) else r
        return np.asarray(c, np.float64) + _v(np.sin(a) * rr, y0 + (y1 - y0) * (0.5 + 0.5 * np.sin(rate_y * t + ph)),
                                               np.cos(a) * rr)
    return f


def _tunnel(t):
    """The blue comet stitching half hoops over the water, a zigzag over the tops, upright at each hoop."""
    s = max(t - TUNNEL_T0, 0.0) * TUNNEL_V / HOOP_GAP
    n = np.floor(s)
    f = s - n
    zf = f + 0.9 * np.sin(2.0 * np.pi * f) / (2.0 * np.pi)
    th = np.pi * (f if int(n) % 2 == 0 else 1.0 - f)
    z = TUNNEL_Z0 - HOOP_GAP * (n + zf)
    return _v(-HOOP_R * np.cos(th), HOOP_R * np.sin(th) * 0.92, z)


def _dancer_hand(t):
    b = _bodies()["dancer"]
    return np.asarray(b.where(min(max(t, SEC[3]), LOOP_T1 + 0.2), "palm.R"), np.float64)


def _ribbon_from_hand(t):
    """The navy ribbon's head: led by the dancer's hand, flying wide circles round her."""
    a = 3.1 * t
    return _dancer_hand(t) + _v(0.9 * np.sin(a), 0.5 + 0.35 * np.sin(1.7 * t), 0.9 * np.cos(a))


def _loop_ahead(t):
    p0, h = _loop_frame()
    phi = min(_loop_phi(t) + 0.55, np.pi * 1.05)
    return p0 + LOOP_R * np.sin(phi) * h + LOOP_R * (1.0 - np.cos(phi)) * UP + 1.6 * _v(-h[2], 0.0, h[0])


def _palm5(t):
    return np.asarray(_bodies()["child"].where(t, "palm.R"), np.float64)


def _gold_stream(t):
    """Gold blown from the child's palm, spiralling up through the waking lanterns."""
    u = max(t - 30.9, 0.0)
    a = 2.2 * u
    return _palm5(min(t, 30.9)) + _v(np.sin(a) * (1.0 + 2.5 * u), 0.6 * u + 0.8 * u * u,
                                     -np.cos(a) * (1.0 + 2.5 * u) - 1.5 * u)


def _weave6(t):
    a = 2.4 * t
    return F6 + _v(0.78 * np.sin(a), 1.95 + 0.12 * np.sin(2.0 * a), -0.30 + 0.45 * np.sin(2.0 * a))


def _thread7(t):
    u = max(t - SEC[6], 0.0)
    return G7 + _v(0.15 * np.sin(3.0 * t), 1.05 + 0.9 * u, -0.05)


def _circle7(k):
    def f(t):
        a = 1.25 * t + 2.0 * np.pi * k / 9.0
        return G7 + _v(np.sin(a) * 13.0, 1.6 + 2.2 * np.sin(1.3 * t + k), np.cos(a) * 13.0)
    return f


def _braid(k):
    """The nine braid round the column and climb with us; they turn about 50 degrees a second faster than the
    camera (a calm, steady wheel, never a strobe)."""
    def f(t):
        u = max(t - BRAID_T0, 0.0)
        a = 1.25 * t + 2.0 * np.pi * k / 9.0 + float(np.interp(t, _ORB7_T, _BRAID_X))
        r = 0.9 + 12.1 * np.exp(-u / 0.9)
        y_up = _y_climb(t) + 9.0 + 5.0 * _sc(BRAID_T0, BRAID_T0 + 1.5, t) + 0.6 * np.sin(2.0 * t + k)
        y_circ = 1.6 + 2.2 * np.sin(1.3 * t + k)
        y = lerp(y_circ, y_up, _sc(BRAID_T0, BRAID_T0 + 1.0, t))
        return G7 + _v(np.sin(a) * r, y, np.cos(a) * r)
    return f


def _globe(k):
    """Round the world: the nine wrap it in rings at every angle, leaving their light and hearts."""
    tilt = np.radians(-50.0 + 12.5 * k)
    ph = 2.0 * np.pi * k / 9.0

    def f(t):
        a = 1.4 * t + ph
        return FIN_C + FIN_R * _fin_scale(t) * 1.3 * _v(np.cos(a), np.sin(a) * np.sin(tilt), np.sin(a) * np.cos(tilt))
    return f


# ---------------------------------------------------------------------------------------------------------
# The words: all nine, exact campaign wording, written by their comets, upper middle, one at a time
# ---------------------------------------------------------------------------------------------------------
def _width(t, depth, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _w(expr, t_in, r0, r1, t_out, frac, x=0.5, y=0.625, depth=7.0):
    tm = 0.5 * (r0 + r1)
    return dict(expr=expr, ride=(x, y, depth), face="screen", width=_width(tm, depth, frac), t_in=t_in, t_read0=r0,
                t_read1=r1, t_out=t_out, leave="fade", pill=True, arrive="pen", nib=False)


_SPECS = [
    _w("Greeting", 5.6, 6.0, 8.55, 8.8, 0.30),
    _w("Concession", 8.8, 9.2, 11.75, 12.0, 0.40),
    _w("Apology", 13.35, 13.75, 16.7, 16.95, 0.60),
    _w("Inclusiveness", 16.95, 17.3, 19.85, 20.1, 0.48),
    _w("Compliment", 20.85, 21.3, 24.6, 24.9, 0.41),
    _w("Consideration", 26.95, 27.4, 30.05, 30.3, 0.44),
    _w("Gratitude", 30.3, 30.7, 33.3, 33.55, 0.58),
    _w("Respect", 33.9, 34.4, 38.2, 38.5, 0.45),
    _w("Encouragement", 41.9, 42.4, 45.2, 45.45, 0.51),
]


PEN_OF = {}


def _clean_leave(t, info):
    """Every word leaves in place and sharp, thinning out evenly: never smeared, drifting or broken letters."""
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)
    return None


WORDS = PW.Words(_SPECS, camera=_LAYOUT, reflect=False, drive=_clean_leave)
PEN_OF.update({LABELS.index(w.name): w for w in WORDS})


def _focus(t, default):
    return np.asarray(default(t) if callable(default) else default, np.float64)


CAMERA = _rig(_focus)

# the comets' legs (after WORDS: the pens are the words' own)
HEADS[GREET].leg(2.5, 5.2, _screen(0.56, 0.17, 34.0, wx=0.22, wy=0.03, rate=0.9), bi=0.9, bo=0.5) \
            .leg(5.6, 6.0, _pen("Greeting"), bi=0.7, bo=0.5) \
            .leg(6.3, 7.4, _screen(0.5, 0.24, 20.0, wx=0.30, wy=0.05, rate=0.8), bi=0.5, bo=1.2)
HEADS[CONC].leg(8.8, 9.2, _pen("Concession"), bi=1.0, bo=0.3) \
           .leg(9.4, 12.2, _tunnel, bi=0.3, bo=1.5)
HEADS[APOL].leg(13.35, 13.75, _pen("Apology"), bi=0.9, bo=0.6) \
           .leg(14.4, 20.2, _helix(C3, 1.45, 0.25, 1.05, 2.2, 0.0), bi=0.6, bo=1.2)
HEADS[INCL].leg(14.0, 16.5, _helix(C3, 1.75, 0.9, 1.6, 2.2, np.pi, 0.9), bi=1.0, bo=0.3) \
           .leg(16.95, 17.3, _pen("Inclusiveness"), bi=0.3, bo=0.3) \
           .leg(17.7, 20.2, _helix(C3, lambda t: 1.75 - 0.35 * _sc(17.7, 18.6, t), 0.9, 1.6, 2.2, np.pi, 0.9),
                bi=0.4, bo=1.2)
HEADS[COMP].leg(SEC[3], 20.85, _ribbon_from_hand, bi=0.0, bo=0.3) \
           .leg(20.85, 21.3, _pen("Compliment"), bi=0.3, bo=0.5) \
           .leg(21.8, LOOP_T0, _ribbon_from_hand, bi=0.5, bo=0.4) \
           .leg(LOOP_T0 + 0.2, SEC[4], _loop_ahead, bi=0.4, bo=0.0)
HEADS[CONS].leg(26.95, 27.4, _pen("Consideration"), bi=0.2, bo=0.5) \
           .leg(27.8, 30.0, _screen(0.5, 0.30, 18.0, wx=0.25, wy=0.04, rate=1.1), bi=0.4, bo=0.6) \
           .leg(30.6, SEC[5], _helix(E5, 2.4, 0.6, 2.2, 1.7, 0.5), bi=0.6, bo=0.8)
HEADS[GRAT].leg(30.3, 30.7, _pen("Gratitude"), bi=0.4, bo=0.3) \
           .leg(30.9, SEC[5], _gold_stream, bi=0.3, bo=0.8)
HEADS[RESP].leg(33.9, 34.4, _pen("Respect"), bi=0.5, bo=0.5) \
           .leg(34.8, SEC[6], _weave6, bi=0.5, bo=0.4)
HEADS[ENC].leg(SEC[6], 41.8, _thread7, bi=0.4, bo=0.0) \
          .leg(41.9, 42.4, _pen("Encouragement"), bi=0.2, bo=0.4) \
          .leg(42.7, BRAID_T0, _thread7, bi=0.4, bo=0.0)
for _k in range(9):
    if _k != ENC:
        HEADS[_k].leg(BREATH_END, BRAID_T0, _circle7(_k), bi=1.4, bo=0.0)
    HEADS[_k].leg(BRAID_T0, SEC[7] + 0.8, _braid(_k), bi=0.0 if _k != ENC else 0.8, bo=0.0)
    HEADS[_k].leg(SEC[7] + 0.7, 52.0, _globe(_k), bi=1.5, bo=0.6)       # they leave the braid gently


def _bridge(head, gap=1.0):
    """Between two of a comet's moments less than `gap` apart, it carries straight on from one to the next: the
    earlier one holds until the next is whole, so its far home never pulls it out across the sky (a flash)."""
    legs = sorted(head.legs, key=lambda lg: lg[0])
    for i in range(len(legs) - 1):
        t0, t1, f, bi, bo = legs[i]
        n0 = legs[i + 1][0]
        if t1 < n0 < t1 + gap:
            legs[i] = (t0, n0, f, bi, 0.0)
    head.legs = legs


for _h in HEADS:
    _bridge(_h)


def _lead_of(t):
    """The comet the section belongs to (its light lies on the water)."""
    for t0, t1, k in ((0.0, 6.84, GREET), (6.84, 13.3, CONC), (13.3, 19.85, APOL), (19.85, 26.79, COMP),
                      (26.79, 30.2, CONS), (30.2, 33.36, GRAT), (33.36, 40.21, RESP), (40.21, 60.0, ENC)):
        if t0 <= t < t1:
            return k
    return ENC


def _second_of(t):
    for t0, t1, k in ((13.3, 19.85, INCL), (26.79, 33.36, CONS if t >= 30.2 else GRAT), (42.51, 49.47, COMP)):
        if t0 <= t < t1:
            return k
    return None


# ---------------------------------------------------------------------------------------------------------
# Keeping the words and the opening title clear: boxes eased in and out (never a pop)
# ---------------------------------------------------------------------------------------------------------
OPEN_FULL, OPEN_END = 5.0, 5.65          # the opening title whole until 7.0 in the film, gone by 7.65
OPENING_BOX = (0.13, 0.87, 0.40, 0.98)   # the opening lockup, screen 0..1, y up


def _boxes(t, cam, k=None):
    """(x0, x1, y0, y1, strength, feather) of the words on screen now and of the opening title; the word's own
    comet (its pen) may cross it while writing it."""
    out = []
    for w in WORDS:
        if not (w.t_in - 0.5 < t < w.t_out + 0.4):
            continue
        s = _sc(w.t_in - 0.5, w.t_in + 0.02, t) * (1.0 - _sc(w.t_out, w.t_out + 0.4, t))
        if k is not None and LABELS.index(w.name) == k:       # its own pen writes it, then keeps out of it
            s *= _sc(w.t_read0 - 0.2, w.t_read0 + 0.1, t)
        b = PW.screen_box(w, cam, t)
        if b[4] and s > 0.0:
            out.append((b[0] - 0.03, b[1] + 0.03, b[2] - 0.035, b[3] + 0.04, s, 0.025))
    s = 1.0 - _sc(OPEN_FULL, OPEN_END, t)
    if s > 0.0:
        out.append(OPENING_BOX + (s, 0.03))
    return out


def _dim(pts, cam, boxes):
    xy, z = cam.project(np.asarray(pts, np.float64).reshape(-1, 3))
    f = np.ones(len(xy))
    for x0, x1, y0, y1, s, e in boxes:
        inside = (_ss(x0 - e, x0, xy[:, 0]) * (1.0 - _ss(x1, x1 + e, xy[:, 0]))
                  * _ss(y0 - e, y0, xy[:, 1]) * (1.0 - _ss(y1, y1 + e, xy[:, 1])))
        f = np.minimum(f, 1.0 - 0.96 * s * inside * (z > 0))
    return f


def _clear_batches(res, cam, boxes):
    out = []
    for b in (res if isinstance(res, (list, tuple)) else [res]):
        if b is None:
            continue
        b = dict(b)
        P = np.asarray(b["pos"], np.float64).reshape(-1, 3)
        f = _dim(P, cam, boxes)
        if b.get("pos2") is not None:
            P2 = np.asarray(b["pos2"], np.float64).reshape(-1, 3)
            fm = _dim(0.5 * (P + P2), cam, boxes)
            b["alpha2"] = np.asarray(b.get("alpha2", b.get("alpha", 1.0)), np.float64) * np.minimum(
                _dim(P2, cam, boxes), fm)
            f = np.minimum(f, fm)
        b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * f
        out.append(b)
    return out


class Clear:
    """Wraps a point set: its light goes out inside the box of every word on screen and of the opening title."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner
        for k in ("gain", "static"):
            if hasattr(inner, k):
                setattr(self, k, getattr(inner, k))

    def sample(self, t, cam=None):
        ps = self.inner
        res = ps.sample(t, cam) if getattr(ps, "wants_camera", False) else ps.sample(t)
        if res is None or cam is None:
            return res
        boxes = _boxes(t, cam)
        return _clear_batches(res, cam, boxes) if boxes else res


# ---------------------------------------------------------------------------------------------------------
# The point sets of render 1, kept: the comets, the seed, the hoops, the lanterns, the flare
# ---------------------------------------------------------------------------------------------------------
class Comets:
    """The nine ribbons of colour: a white-hot core, a deep body, a broad glow, a head that blooms, sparks shed
    behind. Out of the words (their own pen excepted) and the opening title; thinning away right at the lens."""
    wants_camera = True

    def __init__(self):
        r = np.random.default_rng(10)
        self.sp = r.random((9, 140, 4)).astype(np.float64)

    def _alpha(self, k, t):
        return _sc(SEC[0] - 0.02, SEC[0] + 0.15, t) * (1.0 - _sc(51.6, 52.3, t))

    def _near(self, k, t):
        n = 0.0
        for t0, t1, _, bi, bo in HEADS[k].legs:
            n = max(n, _sc(t0 - bi, t0, t) * (1.0 - (_sc(t1, t1 + bo, t) if bo > 0 else float(t > t1))))
        if t < 3.4:
            n = max(n, 1.0 - _sc(1.6, 3.4, t))
        return n

    def _pen(self, k, t):
        """How much the comet is writing its word now (0..1): a short, fine nib, never a smear over the letters."""
        w = PEN_OF.get(k)
        if w is None:
            return 0.0
        return _sc(w.t_in - 0.5, w.t_in, t) * (1.0 - _sc(w.t_read0 + 0.1, w.t_read0 + 0.5, t))

    def sample(self, t, cam=None):
        out = []
        eye = None if cam is None else np.asarray(cam.pos, np.float64)
        fwd = None if cam is None else cam.basis()[2]
        vcam = None
        if eye is not None:
            vcam = (np.asarray(_LAYOUT.state(t).pos, np.float64) - np.asarray(_LAYOUT.state(t - 0.02).pos,
                                                                                  np.float64)) / 0.02
        for k in range(9):
            a = self._alpha(k, t)
            if a <= 0.0:
                continue
            near = self._near(k, t)
            tail = 0.55 * near + 2.2 * (1.0 - near)
            if BRAID_T0 - 0.2 < t < SEC[7] + 0.3:
                tail = 0.45
            w = 0.30 * near + 3.2 * (1.0 - near)
            if BRAID_T0 < t < SEC[7] + 0.3:
                w = 0.30 + 0.25 * _sc(BRAID_T0, SEC[7], t)
            if t > SEC[7] + 0.3:
                w = 0.45
            pen = self._pen(k, t)
            if pen > 0.0:
                tail = tail * (1.0 - pen) + 0.14 * pen
                w = w * (1.0 - pen) + 0.12 * pen
            n = 56
            ts = np.linspace(max(t - tail, SEC[0]), t, n)
            if ts[-1] - ts[0] < 1e-3:
                continue
            pts = np.array([HEADS[k](float(x)) for x in ts])
            if eye is not None:
                dep = (pts - eye[None, :]) @ fwd            # a tail is never drawn across the lens plane
                if dep[-1] < 0.4:
                    continue
                bad = np.nonzero(dep < 0.4)[0]
                if len(bad):
                    i0 = int(bad[-1]) + 1
                    if n - i0 < 3:
                        continue
                    ts, pts = ts[i0:], pts[i0:]
                    n = len(ts)
                if near < 0.6:                              # on its way in or home: shown only when far
                    a = a * _sc(170.0, 340.0, float(np.min(np.linalg.norm(pts - eye[None, :], axis=1))))
                    if a <= 0.002:
                        continue
                else:                                       # arrived: its tail only since it came near
                    nr = np.array([self._near(k, float(x)) for x in ts])
                    bad = np.nonzero(nr < 0.6)[0]
                    if len(bad):
                        i0 = int(bad[-1]) + 1
                        if n - i0 < 3:
                            continue
                        ts, pts = ts[i0:], pts[i0:]
                        n = len(ts)
                    a = a * _sc(0.6, 0.9, near)
            nearf = np.ones(n)
            if eye is not None and t > 4.0:            # a comet in transit (racing in from far, faster than
                dt = max(float(ts[1] - ts[0]), 1e-4)    # about 80 m/s past us) is not drawn: no flash streaks
                v = np.diff(pts, axis=0) / dt
                rel = np.linalg.norm(np.vstack([v, v[-1:]]) - vcam[None, :], axis=1)
                nearf = 1.0 - _ss(80.0, 160.0, rel)
                a = a * float(nearf[-1])
                if a <= 0.002:
                    continue
            if eye is not None:
                d = float(np.linalg.norm(pts[-1] - eye))
                a = a * _sc(1.2, 3.5, d)
                if a <= 0.0:
                    continue
                w = w * float(np.clip(d / 6.0, 0.35, 1.0))          # close by, a finer ribbon
                nearf = nearf * _ss(0.8, 2.5, np.linalg.norm(pts - eye[None, :], axis=1)) * _ss(0.4, 2.5, (pts - eye[None, :]) @ fwd)
            age = (t - ts) / max(tail, 1e-6)
            kk = 1.0 - age
            c = lin(GLOW[k])
            deep = deepen(GLOW[k])
            core = 0.35 * c + 0.65 * lin(WHITE)
            out.append(_rib(pts, w * 4.2 * (0.25 + 0.75 * kk), c, a * 0.08 * np.clip(kk * 1.3, 0, 1) * nearf, emit=1.0))
            out.append(_rib(pts, w * (0.12 + 0.88 * kk), deep, a * 0.55 * np.clip(kk * 1.4, 0, 1) * nearf, emit=1.6))
            out.append(_rib(pts, w * 0.22 * (0.15 + 0.85 * kk), core, a * 0.95 * np.clip(kk * 1.6, 0, 1) * nearf,
                            emit=2.6))
            head = pts[-1:]
            out.append(dict(pos=head, size=w * 0.65, color=core, alpha=a, emit=7.0, kind="spark"))
            out.append(dict(pos=head, size=w * 5.0, color=c, alpha=a * 0.16, kind="soft"))
            sp = self.sp[k]
            f = np.mod(sp[:, 0] + t * (0.9 + 0.4 * sp[:, 1]), 1.0)
            idx = f * (n - 1)
            i0 = np.floor(idx).astype(int)
            i1 = np.minimum(i0 + 1, n - 1)
            fr = (idx - i0)[:, None]
            base = pts[i0] * (1.0 - fr) + pts[i1] * fr
            drift = (sp[:, 1:4] - 0.5) * (w * 3.5) * (1.0 - f)[:, None]
            pos = base + drift - _v(0.0, 0.6 * w, 0.0) * (1.0 - f)[:, None]
            out.append(dict(pos=pos, size=w * (0.10 + 0.12 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                            alpha=a * 0.9 * f ** 1.5 * nearf[i0], emit=2.0, kind="spark", twinkle=0.6,
                            seed=sp[:, 3]))
            if cam is not None:
                start = len(out) - 6
                out[start:] = _clear_batches(out[start:], cam, _boxes(t, cam, k))
        return out or None


def _rib(pts, width, color, alpha, emit=1.0):
    from p3d.api import ribbon
    return ribbon(pts, width=width, color=color, alpha=alpha, emit=emit)


class Seed:
    """The white seed of light from frame 0 (it breathes through the quiet lead-in), and its flat burst into
    sparks on the opening hit (across the water: the sky above stays calm for the title)."""

    def __init__(self):
        r = np.random.default_rng(3)
        n = 2600
        d = r.normal(size=(n, 3))
        d[:, 1] *= 0.15
        self.d = d / np.linalg.norm(d, axis=1, keepdims=True)
        self.s = r.random((n, 3))
        self.col = np.array([lin(GLOW[i % 9]) for i in range(n)]) * 0.6 + 0.4 * lin(WHITE)

    def sample(self, t):
        if t > 2.6:
            return None
        pre = 1.0 - _sc(SEC[0] - 0.02, SEC[0] + 0.2, t)
        out = []
        if pre > 0.0:
            pulse = 1.0 + 0.25 * np.sin(t * 40.0) * _sc(-0.8, 0.0, t) + 0.1 * np.sin(t * 3.0)
            out.append(dict(pos=SEED[None, :], size=0.22 * pulse, color=lin(WHITE), alpha=pre, emit=9.0,
                            kind="spark"))
            out.append(dict(pos=SEED[None, :], size=2.2, color=lin("#fff2dc"), alpha=0.35 * pre, kind="soft"))
            shell = SEED + self.d * (0.12 + 0.35 * self.s[:, :1]) * (1.0 + 0.4 * np.sin(t * 9.0 + 6.0 * self.s[:, 1:2]))
            out.append(dict(pos=shell[:600], size=0.012, color=lin("#fff4e2"), alpha=0.8 * pre, emit=3.0,
                            kind="spark", twinkle=0.8, seed=self.s[:600, 2]))
        u = t - SEC[0]
        if u > 0.0:
            dist = (2.0 + 26.0 * self.s[:, :1]) * (1.0 - np.exp(-u * 2.4))
            pos = SEED + self.d * dist - _v(0.0, 0.3, 0.0) * u * u
            al = np.exp(-u / (0.5 + 0.7 * self.s[:, 1]))
            out.append(dict(pos=pos, size=0.05 + 0.06 * self.s[:, 2], color=self.col, alpha=al, emit=2.4,
                            kind="spark", twinkle=0.5, seed=self.s[:, 2]))
        return out


class Hoops:
    """The gate: the blue comet's trail stays standing as half hoops over the water (asked every frame, so the
    words keep them out and they thin away at the lens)."""
    wants_camera = True

    def __init__(self):
        n = 9000
        self.ts = TUNNEL_T0 + np.linspace(0.0, HOOPS * HOOP_GAP / TUNNEL_V, n)
        rng = np.random.default_rng(12)
        self.pos = np.array([_tunnel(float(x)) for x in self.ts]) + rng.normal(size=(n, 3)) * 0.05
        self.size = 0.07 + 0.05 * rng.random(n)
        self.seed = rng.random(n)

    def sample(self, t, cam=None):
        al = 0.75
        if cam is not None:
            al = 0.75 * _ss(3.5, 9.0, np.linalg.norm(self.pos - np.asarray(cam.pos, np.float64)[None, :], axis=1))
        return dict(pos=self.pos, size=self.size, color=deepen(COL[CONC], 1.2), alpha=al, birth=self.ts,
                    fade=0.25, flash=4.0, twinkle=0.5, seed=self.seed, kind="spark", emit=1.8)

    def gain(self, t):
        return float(_sc(TUNNEL_T0 - 0.1, TUNNEL_T0, t) * (1.0 - _sc(13.6, 14.6, t)))


class Lanterns:
    """Lanterns round the child and the helper that wake gold in a wave from the touch, and rise."""

    def __init__(self, n=520):
        r = np.random.default_rng(14)
        a = r.random(n) * 2.0 * np.pi
        rad = 4.0 + 46.0 * np.sqrt(r.random(n))
        self.base = E5 + np.stack([np.sin(a) * rad, 0.6 + 7.0 * r.random(n), np.cos(a) * rad - 8.0], axis=1)
        self.wake = 30.2 + rad / 22.0 + 0.3 * r.random(n)
        self.s = r.random((n, 3))

    def sample(self, t):
        if t < SEC[4] or t > SEC[6] + 0.3:
            return None
        age = np.maximum(t - self.wake, 0.0)
        lit = _ss(0.0, 0.5, age)
        pos = self.base + _v(0.0, 1.0, 0.0) * (0.5 * age + 0.06 * age * age)[:, None]
        pos[:, 0] += 0.4 * np.sin(t * 0.7 + 6.0 * self.s[:, 0])
        sleep = lin("#7a4a3a") * 0.4
        col = sleep[None, :] * (1.0 - lit)[:, None] + lin(COL[GRAT])[None, :] * lit[:, None]
        al = (0.25 + 0.75 * lit) * _sc(SEC[4], SEC[4] + 1.0, t)
        return dict(pos=pos, size=0.30 + 0.25 * self.s[:, 1], color=col, alpha=al, emit=1.0 + 1.5 * lit,
                    kind="soft", seed=self.s[:, 2], twinkle=0.2)


class Flares:
    """A soft white flash where the helper's hand meets the child's (never a white-out)."""

    def __init__(self):
        from p3d.effects import Flare
        self.f = [Flare(_touch5, 30.15, color=WHITE, color2=COL[GRAT], n=700, strength=0.3, reach=0.45, life=1.8,
                        seed=5.0)]

    def sample(self, t):
        out = []
        for f in self.f:
            s = f.sample(t)
            if s is None:
                continue
            out.extend(s if isinstance(s, list) else [s])
        return out or None


# ---------------------------------------------------------------------------------------------------------
# The finale: BRAND's world of light, wrapped by the comets, the symbols swirling, world to logo, the end card
# ---------------------------------------------------------------------------------------------------------
LAS_VEGAS_LON = -115.1
FIN_SPIN = 6.0
FINALE = BR.Finale(pos=tuple(FIN_C), radius=FIN_R, shrink=FIN_SHRINK, camera=CAMERA, look="night", t_world=FIN_T,
                   spin=FIN_SPIN, front=LAS_VEGAS_LON - FIN_SPIN * HEARTS_T0,
                   hearts=dict(t0=HEARTS_T0, t1=HEARTS_T1, n=44), t_settle=SETTLE, t_logo=LOGO_T,
                   bloom=dict(t=BLOOM_T, dur=1.6), blend=2.4,
                   end=dict(t=(END_T0, END_T), ride=(0.5, 1.0 - SLOT_Y, 14.0), frac=SLOT_H), logo=dict(reflect=False))


class _Fade:
    def __init__(self, inner, f):
        self.inner, self.f = inner, f
        self.wants_camera = bool(getattr(inner, "wants_camera", False))

    def gain(self, t):
        g = float(self.inner.gain(t)) if hasattr(self.inner, "gain") else 1.0
        return g * float(self.f(t))

    def sample(self, t, cam=None):
        if float(self.f(t)) <= 0.0:
            return None
        ps = self.inner
        return ps.sample(t, cam) if self.wants_camera else ps.sample(t)


class _OnlyBloom:
    def __init__(self, scene):
        self.scene = scene

    def add(self, name, ps, **kw):
        if name.endswith(" bloom"):
            self.scene.add(name, ps, **kw)


def _sym_at(c, cam_t):
    """A symbol standing at c, facing the camera as it is at cam_t."""
    def f(t):
        cam = PW._cam_at(_LAYOUT, cam_t)
        d = _unit(np.asarray(cam.pos, np.float64) - c)
        rt = _unit(np.cross(UP, d))
        return c, rt, UP
    return f


def _ahead(t, x, y, depth):
    """A fixed world point that stands at (x, y) of the picture `depth` metres ahead at t."""
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


def _setup(scene):
    from p3d import master_brand as MB
    scene.add("seed", Clear(Seed()))
    scene.add("hoops", Clear(Hoops()))
    scene.add("lanterns", Lanterns())
    b = _bodies()
    for name, body in b.items():
        body.add(scene, name)
    scene.add("flares", Flares())
    scene.add("comets", Comets(), reflect=False)
    # hearts rising from the action, in each expression's colour
    for i, (lab, src, t0, t1) in enumerate([
            ("Greeting", lambda t: GREET_AT + _v(0.0, 1.5, 0.0), 7.5, 8.4),
            ("Inclusiveness", lambda t: 0.5 * (b["kind"].where(t, "chest") + b["sorry"].where(t, "chest")), 18.0,
             19.9),
            ("Compliment", lambda t: b["dancer"].where(t, "chest"), 21.5, 24.6),
            ("Gratitude", lambda t: _palm5(min(t, 30.9)), 30.8, 33.0),
            ("Respect", lambda t: F6 + _v(0.0, 1.75, 0.0), 35.0, 38.2),
            ("Encouragement", lambda t: G7 + _v(0.0, 1.1, 0.0), 42.6, 45.0)]):
        scene.add("hearts_%d" % i, Clear(BR.HeartDrift(lambda t, s=src: np.asarray(s(t), np.float64), t0, t1,
                                                       color=PW.COLORS[lab], rate=3.0, life=2.6, rise=0.42,
                                                       spread=0.35, size=(0.06, 0.12), style="heart",
                                                       seed=300 + i)), reflect=False)
    # the nine symbols, subtly, as scenery along the way
    for i, (lab, tt, at, size) in enumerate([
            ("Greeting", 6.2, _ahead(5.4, 0.78, 0.38, 26.0), 1.6),
            ("Concession", 10.6, _ahead(9.8, 0.22, 0.36, 30.0), 1.8),
            ("Apology", 15.2, C3 + _v(-3.2, 2.6, -3.0), 1.0),
            ("Inclusiveness", 18.8, C3 + _v(3.0, 2.9, -3.5), 1.0),
            ("Compliment", 23.2, D4 + _v(-3.4, 2.8, -4.0), 1.2),
            ("Consideration", 28.4, E5 + _v(-4.0, 3.2, -5.0), 1.4),
            ("Gratitude", 31.6, E5 + _v(4.2, 3.0, -4.5), 1.3),
            ("Respect", 36.2, F6 + _v(0.0, 3.1, -4.5), 1.0),
            ("Encouragement", 43.2, G7 + _v(-3.6, 3.4, -4.0), 1.2)]):
        scene.add("symbol_%d" % i, Clear(MB.SymbolLight(lab, _sym_at(at, tt), tt, PW.COLORS[lab], size=size,
                                                        seed=91 + i)))
    # the finale
    MB.rose_hearts(FINALE.logo)
    scene.add("finale globe", MB.Brighten(FINALE.globe, lambda t: 0.72 + 0.55 * _sc(SWIRL[0] + 0.2, SWIRL[1], t)))
    scene.add("finale logo", _Fade(FINALE.logo, lambda t: 1.0 - _sc(52.8, 53.2, t)))
    FINALE.add_to(_OnlyBloom(scene))
    scene.add("swirl", MB.SymbolSwirl(FIN_C, FIN_R, PW.LABELS, GLOW, SWIRL[0], SWIRL[1], CAMERA, scale=_fin_scale),
              reflect=False)

    def card(t):                    # the end card's middle, in the picture's plane, 14 m ahead of the lens
        cam = PW._cam_at(CAMERA, t)
        r, u, f = cam.basis()
        return np.asarray(cam.pos, np.float64) + 14.0 * f, r, u
    scene.add("final_glow", MB.FinalGlow(card, FINAL_HIT, ring=0.075, glint=0.085), reflect=False)
    scene.add("card_life", MB.CardLife(card, EC_IN + 0.3, OLD_END - 1.5), reflect=False, depth_of_field=False)
    try:
        MB.endcard_push(PUSH[0] + OFF, TOTAL, push=0.02)
    except Exception as e:          # pragma: no cover
        print("end card push skipped:", e)
    WORDS.add_to(scene, reflect=False)
    try:
        WORDS.check(CAMERA)
    except Exception as e:          # the check is advice; never stop a render for it
        print("words check failed:", e)


# ---------------------------------------------------------------------------------------------------------
# The world: night looks section by section (render 1), then the pastel day of the end card
# ---------------------------------------------------------------------------------------------------------
LIGHT_SWITCH = ((6.84, 13.3, 19.85, 26.79, 30.2, 33.36, 40.21), (13.3, 19.85, 26.79, 30.2, 33.36, 42.51, 49.47))


def _light_pos(which):
    def f(t):
        k = _lead_of(t) if which == 0 else _second_of(t)
        return HEADS[ENC if k is None else k](t)
    return f


def _light_col(which):
    def f(t):
        k = _lead_of(t) if which == 0 else _second_of(t)
        return COL[ENC if k is None else k]
    return f


def _light_str(which):
    def f(t):
        night = 1.0 - _sc(SEC[7] - 0.05, SEC[7] + 0.5, t)
        if which == 0:
            s = 0.5 * _sc(0.3, 1.2, t) * night
        else:
            s = (0.4 if _second_of(t) is not None else 0.0) * night
        for b in (LIGHT_SWITCH[which]):
            s *= _sc(0.0, 0.45, abs(t - b))
        if s > 0.0:                 # a comet passing the lens must not light the air round it into a wash
            eye = np.asarray(_LAYOUT.state(t).pos, np.float64)
            s *= _sc(3.0, 9.0, float(np.linalg.norm(_light_pos(which)(t) - eye)))
        return s
    return f


LOOKS = dict(
    gate=dict(base="night", mist=0.22, mist_color="#0e2148", haze=0.25, haze_color="#0a1636", stars=0.7),
    embrace=dict(base="night", mist=0.28, mist_color="#2a1020", haze=0.3, haze_color="#1e0c1a", stars=0.5,
                 sky_top="#04020a", sky_mid="#120818", sky_hor="#2a1224"),
    floor=dict(base="night", mist=0.05, haze=0.1, stars=1.0, milky=0.8),
    drop=dict(base="dusk", sky_hor="#4a2030", mist=0.3, mist_color="#3a1a26", stars=0.6),
    ember=dict(base="night", sky_top="#05040a", sky_mid="#1a0f0c", sky_hor="#3a2210", haze=0.5,
               haze_color="#3a2410", mist=0.35, mist_color="#2a1c10", stars=0.3, milky=0.0),
    prayer=dict(base="night", sky_top="#03020e", sky_mid="#0e0a2e", sky_hor="#1e1648", mist=0.25,
                mist_color="#1a1440", stars=1.0, milky=0.9),
    space=dict(base="night", sky_top="#020210", sky_mid="#0a0a2a", sky_hor="#1a1640", mist=0.0, haze=0.05,
               stars=1.0, milky=0.9),
)
LOOKS["pastel"] = dict(BR.PASTEL)

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "night"), (SEC[1], "gate", 1.2), (SEC[2], "embrace", 1.0), (SEC[3], "floor", 0.4),
          (SEC[4], "drop", 0.4), (SEC[5], "ember", 0.4), (SEC[6], "prayer", 0.4), (SEC[7], "space", 1.0)],
    light=dict(pos=SEED, color="#fff1d8", strength=Track([(0.0, 1.4), (SEC[0], 1.6), (0.9, 0.5), (1.8, 0.0),
                                                           (OLD_END, 0.0)]), size=0.5, rays=1.0),
    lights=[dict(pos=_light_pos(0), color=_light_col(0), strength=_light_str(0), radius=4.0),
            dict(pos=_light_pos(1), color=_light_col(1), strength=_light_str(1), radius=3.5)],
    lantern_field=dict(count=260, center=(E5[0], E5[2] - 10.0), radius=(10.0, 70.0)),
    lanterns=Track([(0.0, 0.0), (30.2, 0.0), (31.5, 1.0), (SEC[6] - 0.3, 1.0), (SEC[6], 0.0), (OLD_END, 0.0)]),
    lantern_color=COL[GRAT],
    react=dict(beat=0.35, level=0.25),
)


# =============================================================================================================
# THE FILM'S CLOCK: render 1's clock played 2.0 s later (the quiet lead-in)
# =============================================================================================================
class Offset:
    """W(t_new) = t_new - OFF (render 1's clock), R(t_old) = t_old + OFF."""

    def __call__(self, t):
        return float(t) - OFF

    def R(self, t):
        return t + OFF if isinstance(t, np.ndarray) else float(t) + OFF

    def rate(self, t):
        return 1.0


TW = Offset()


class WarpRig(Rig):
    def __init__(self, inner, warp):
        self.__dict__.update(inner.__dict__)
        self.inner, self.warp = inner, warp

    def state(self, t, aspect=16.0 / 9.0, ref=None):
        return self.inner.state(self.warp(t), aspect, ref=None if ref is None else self.warp(ref))

    def raw(self, t, ref=None, swing=True):
        return self.inner.raw(self.warp(t), ref=None if ref is None else self.warp(ref), swing=swing)

    def cuts(self):
        return [self.warp.R(c) for c in self.inner.cuts()]


class _Warped:
    def __init__(self, inner, warp):
        self.inner, self.warp = inner, warp
        self.wants_camera = bool(getattr(inner, "wants_camera", False))
        for k in ("static", "dome", "turns"):
            if hasattr(inner, k):
                setattr(self, k, getattr(inner, k))
        if hasattr(inner, "gain"):
            self.gain = lambda t: inner.gain(warp(t))

    def sample(self, t, cam=None):
        to = self.warp(t)
        res = self.inner.sample(to, cam) if self.wants_camera else self.inner.sample(to)
        if res is None:
            return None
        one = not isinstance(res, (list, tuple))
        out = []
        for b in ([res] if one else res):          # births are seen by the renderer on the film's clock
            if b is not None and b.get("birth") is not None:
                b = dict(b)
                b["birth"] = self.warp.R(np.asarray(b["birth"], np.float64))
            out.append(b)
        return out[0] if one else out


class _WarpScene:
    def __init__(self, scene, warp):
        self.scene, self.warp = scene, warp

    def add(self, name, ps, **kw):
        self.scene.add(name, _Warped(ps, self.warp), **kw)
        return ps

    def __getattr__(self, k):
        return getattr(self.scene, k)


def _setup_new(scene):
    _setup(_WarpScene(scene, TW))


def _shift(v):
    """A world setting on the film's clock (functions and tracks of time asked at W(t))."""
    if callable(v):
        return lambda t, f=v: f(TW(t))
    if isinstance(v, dict):
        return {k: _shift(x) for k, x in v.items()}
    if isinstance(v, list) and v and isinstance(v[0], dict):
        return [_shift(x) for x in v]
    return v


def _world_new(w):
    w = dict(w)
    keys = []
    for k in w["look"]:
        bl = float(k[2]) if len(k) > 2 else 1.5
        keys.append((TW.R(float(k[0])) if k[0] > 0.0 else 0.0, k[1], bl))
    w["look"] = keys
    for name in ("light", "lights", "lanterns", "shafts", "calm"):
        if name in w:
            w[name] = _shift(w[name])
    return w


def _bursts_new(bs):
    out = []
    for b in bs:
        b = dict(b)
        b["t"] = TW.R(float(b["t"]))
        out.append(b)
    return out


P3D = dict(
    camera=WarpRig(CAMERA, TW),
    world=_world_new(FINALE.world(WORDS.world(WORLD))),
    setup=_setup_new,
    bursts=_bursts_new(
        [dict(t=SEC[0], strength=0.3, rise=0.2, fall=0.8, color="#fff4e0", at=tuple(SEED)),
         dict(t=SEC[3], strength=0.3, rise=0.12, fall=0.5, color=COL[COMP]),
         dict(t=SEC[4], strength=0.3, rise=0.12, fall=0.5, color=COL[CONS]),
         dict(t=SEC[5], strength=0.3, rise=0.12, fall=0.5, color=COL[RESP]),
         dict(t=BREATH_END, strength=0.3, rise=0.15, fall=0.7, color=COL[ENC])] + FINALE.bursts()),
    motion_blur=0.5,
    bokeh_max=0.07,             # never a giant out-of-focus disc (a comet head passing close)
    # true motion blur through the fast flights where no person is on screen (a body asked at several moments
    # of a frame re-simulates its garments: very slow)
    motion_samples=lambda t: 3 if (2.3 <= t < 8.2 or 11.5 <= t < 14.3 or 48.2 <= t < 51.6) else 1,
)


# =============================================================================================================
# THE TITLES: the opening over the moving prism for 7 s, the signature always on, the official end card
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

SIG_CORNER = "bl"
SIG_FADE = 0.6
SIG_PALETTES = [(OPEN_FULL + 0.7, "night"), (BLOOM_T + 0.05, "day")]
SIG_END = EC_IN + 0.3


def _sig_windows():
    out = []
    for i, (a, pal) in enumerate(SIG_PALETTES):
        b = SIG_PALETTES[i + 1][0] + SIG_FADE if i + 1 < len(SIG_PALETTES) else SIG_END
        out.append((TW.R(a), TW.R(b), SIG_CORNER, pal))
    return out


TITLES = dict(
    opening=dict(t_end=TW.R(OPEN_END), dissolve=OPEN_END - OPEN_FULL, y=0.30, palette="night",
                 protect=dict(keep=0.6, blur=12.0, gain=4.0)),
    signature=dict(windows=_sig_windows(), fade=SIG_FADE, protect=dict(keep=0.7, blur=6.0, gain=3.0)),
    end_card=dict(t_in=TW.R(EC_IN), fade=EC_FADE, scale=EC_SCALE, backdrop="auto", veil=0.6),
)
