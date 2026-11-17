# Film 10 snapshot from 3d8dbc4, adapted only outside protected engine files.
"""Film 10 of ten: NINE COLOURS. A 60 second promo for the Healing Concert "The Words of Mother's Love",
on the high-energy medley (audio/promo/concert-medley.mp3), built on the 3D layer (engine/p3d: camera, world,
particle people, particle words; engine/UPGRADE-HOWTO.md sections V, W, X, X2).

LOGLINE
  Mother's love is one white light and her nine words are its colours. A white seed bursts into nine comets,
  one in each campaign colour; we chase them like a rollercoaster while each one writes its words in the
  air and wraps the people who live them; where two colours touch there is a flash of white; at the end all
  nine braid back into one white light, which becomes the morning and the arch of nine lights.

THE RIDE (song sections of the medley: 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 with the breath to
42.51, 49.47; final hit 58.11)
  0.00   THE PRISM. Frame 0: a white seed blazes over a black mirror lake, rays fanning from it. On the
         opening hit (0.25) it bursts into nine comets that fan out across the sky.
  1.2    LAUNCH, coral. We are launched after the coral comet, low over the water at 24 m/s; it loops up and
         writes the Greeting ahead of us; the words ride with us, then unspool back into it.
  6.84   THE GATE, sky blue. The blue comet streaks in from the far shore, writes the Concession, then races
         ahead stitching half hoops over the water, one per beat; the mirror closes each into a ring. We
         fly through the tunnel; the words part like doors and let us through.
  13.30  THE EMBRACE, apricot and pink. We brake into a spiral round two people in warm mist: one kneels,
         head bowed (Apology, written by the apricot comet); the other lays a hand on the shoulder: white
         flare; the Apology turns into Inclusiveness while the two comets wrap them in a double helix.
  19.85  THE DANCER, lavender (bass slam). A dancer turns on the black mirror leading the lavender ribbon
         from her hand like a gymnast's ribbon; it flicks up and writes the Compliment. Then the HALF LOOP:
         we ride up the wall and over, upside down, the starred lake above us.
  26.79  THE DROP, rose and gold. Over the crest and down the dive with the Consideration riding ahead; a
         helper reaches a hand to a child: white flare; the child blows gold from an open palm that settles
         into the Gratitude while lanterns rise all round.
  33.36  THE TWO PROFILES, clay. Head and shoulders, two featureless profiles face each other against a sea
         of gold lanterns; the clay comet weaves between them and writes the Respect above them.
  40.21  THE BREATH, violet. Someone kneels in prayer in a shaft of violet light, seen from behind; the
         Encouragement comes down the shaft and is whole on the biggest hit (42.51), when the eight other
         comets race in from every side and circle. The one who prays rises into light; the nine comets
         braid round the column and we corkscrew straight up inside them until they fuse into white.
  49.47  MORNING. Out of the white into the campaign day: the lake by day, the arch of nine lights each in
         its own colour, lights flying in from the sky; the end card forms and is whole from 54.8 s to the
         last frame (no fade).

HOUSE RULES kept: no facial features (mannequin heads, profiles are outlines), everyone clothed in garments
of light, Heavenly Mother does not appear (only her light: the seed), all nine expressions with their exact
campaign wording from words.EXPRESSIONS, each read 2.5 s or more, no lyrics, nothing dark behind text, no
fade to black, frame 0 bright, colours from words.COLORS.
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

import theme  # noqa: E402
from track import Track  # noqa: E402
from p3d import lin, show  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.camera import Move, Rig, fly  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 59.6
SONG_END = 60.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0           # nothing dark behind any text
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# the medley's sections and hits (scratchpad/medley2/SECTION-MAP.md)
SEC = [0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47]
BREATH_END = 42.51
FINAL_HIT = 58.11

# ---------------------------------------------------------------------------------------------------------
# The nine colours: words.COLORS (DESIGN-SYSTEM section 5). Index = the order of words.EXPRESSIONS.
# ---------------------------------------------------------------------------------------------------------
LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)
WHITE = "#fff6e6"


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


# ---------------------------------------------------------------------------------------------------------
# Geography (metres, y up, the lake is y = 0). Each section has its stage.
# ---------------------------------------------------------------------------------------------------------
SEED = _v(0.0, 2.2, 300.0)          # the white seed
SPEED = 24.0                        # the chase over the lake, metres a second
Z22 = 296.0                         # the camera's z at 2.2 s; from then on it flies at SPEED toward -z


def zcam(t):
    return Z22 - SPEED * (t - 2.2)


HOOP_R = 6.5                        # the gate: half hoops of the blue comet's trail
HOOP_GAP = SPEED * 60.0 / 84.0      # one hoop a beat at 84 bpm
HOOPS = 6
TUNNEL_T0 = 8.15                    # the blue comet starts stitching
TUNNEL_Z0 = zcam(TUNNEL_T0) - 34.0
TUNNEL_V = 50.0                     # its speed along the tunnel
C3 = _v(0.0, 0.0, 6.0)              # the embrace
PAIR_AT = (C3[0] - 1.6, C3[2] - 0.2)  # the shared placement of the pull-up pair (centred on C3)
PAIR_T0 = 14.6                      # the pull-up clip starts: the hands meet at about 17.0, both stand by 19.0
TOUCH3 = 17.0
H5 = None                           # set below with E5: where the two hands meet (Consideration)
HANDS_T = 29.15                     # the hands clasp
D4 = _v(-90.0, 0.0, -60.0)          # the dancer
E5 = _v(90.0, 0.0, -70.0)           # the child and the helper; the lantern field
F6 = _v(90.0, 0.0, -40.0)           # the two profiles (looking -z: the lanterns behind them)
G7 = _v(0.0, 0.0, 2.0)              # the one who prays; the foot of the braid; the arch stands at z = 0
H5 = E5 + _v(0.0, 1.25, 11.0)       # the two hands of the Consideration, on the line of the dive

# ---------------------------------------------------------------------------------------------------------
# The camera: moves of the engine plus `Path`, a move given by a function of time.
# ---------------------------------------------------------------------------------------------------------


class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


# S1 and S2: one flight along -z over the lake
def _flight_keys():
    keys = [(0.00, _v(0.35, 2.30, 307.6), SEED + _v(0, 1.45, 0)),      # the seed low, the badge above it
            (0.25, _v(0.35, 2.30, 307.4), SEED + _v(0, 1.40, 0)),
            (0.85, _v(-1.4, 3.30, 311.0), _v(0.0, 3.2, 292.0)),
            (1.50, _v(-0.9, 2.50, 307.5), _v(0.0, 2.6, 284.0)),
            (2.20, _v(0.3, 1.90, Z22), _v(0.0, 2.2, Z22 - 24.0))]
    for t in np.arange(2.7, 13.31, 0.5):
        tun = _sc(8.6, 9.6, t) * (1.0 - _sc(12.6, 13.3, t))
        x = 1.3 * np.sin(0.85 * t + 0.4) * (1.0 - 0.75 * tun)
        y = 2.1 + 0.25 * np.sin(1.3 * t) + 0.7 * tun
        z = zcam(t)
        keys.append((float(t), _v(x, y, z), _v(0.35 * x, y + 0.45 - 0.2 * tun, z - 24.0)))
    return keys


def _roll_s12(t):
    return 7.0 * np.sin(0.85 * t + 1.9) * _sc(2.0, 3.0, t) + 9.0 * np.sin(1.1 * t) * _sc(8.6, 9.6, t)


# S3: brake into a descending spiral round the two
def _s3(t):
    u = t - SEC[2]
    r = 4.35 - 0.11 * u + 20.0 * np.exp(-u / 0.34)
    h = 1.75 + 0.5 * np.exp(-u / 1.0) - 0.03 * u
    a = np.radians(-52.0 + 32.0 * (1.0 - np.exp(-u / 0.6)) + 9.0 * u)
    p = C3 + _v(np.sin(a) * r, h, np.cos(a) * r)
    return p, C3 + _v(0.0, 2.32, 0.0)


# S4: round the dancer, then the half loop
_BODIES = {}


def _dancer_ground(t):
    """Where the dancer stands, smoothed (her dance travels a little)."""
    b = _bodies().get("dancer")
    if b is None:
        return D4.copy()
    acc = np.zeros(3)
    for dt in (-0.4, -0.2, 0.0, 0.2, 0.4):
        tt = min(max(t + dt, SEC[3] - 0.2), 27.0)
        p = np.asarray(b.where(tt, "pelvis"), np.float64)
        acc += p
    acc /= 5.0
    acc[1] = 0.0
    return acc


LOOP_T0, LOOP_T1 = 25.0, SEC[4]
S4_EYE = 1.6                         # the height of the orbit's centre over the dancer's mark


def _s4_az(t):
    u = t - SEC[3]
    return np.radians(25.0 + 24.0 * u)


def _s4_r(t):
    return 4.9 - 0.12 * min(t - SEC[3], LOOP_T0 - SEC[3])


def _loop_phi(t):
    """0 level with her, pi/2 straight over her head, pi on the far side upside down."""
    u = float(np.clip((t - LOOP_T0) / (LOOP_T1 - LOOP_T0), 0.0, 1.0))
    return np.pi * 0.97 * u * u * (2.2 - 1.2 * u)


def _s4(t):
    """Close round the dancer, then the flip: over her head and down the far side, always looking at her,
    upside down at the end (the lake above, the stars below)."""
    a, r, phi = _s4_az(t), _s4_r(t), _loop_phi(t)
    h = _v(np.sin(a), 0.0, np.cos(a))
    c = D4 + _v(0.0, S4_EYE, 0.0)
    look = D4 + _v(0.0, 2.45 - 1.05 * _sc(LOOP_T0, LOOP_T0 + 1.0, t), 0.0)
    return c + r * (np.cos(phi) * h + np.sin(phi) * UP) + _v(0.0, -0.35, 0.0) * (1.0 - _sc(0.0, 0.3, phi)), look


def _s4_up(t):
    a, phi = _s4_az(t), _loop_phi(t)
    h = _v(np.sin(a), 0.0, np.cos(a))
    return _unit(-np.sin(phi) * h + np.cos(phi) * UP)


# S5: over the crest and down the dive to the child, then a slow rise round them
def _s5_keys():
    up = _v(0.0, 0.30, 0.0)            # the hands sit low in the picture, the riding words above them
    return [(SEC[4], E5 + _v(-4.0, 30.0, 52.0), E5 + _v(-2.0, 27.0, 20.0)),
            (27.30, E5 + _v(-3.5, 26.5, 45.0), H5 + _v(0.0, 4.0, 0.0)),
            (28.15, H5 + _v(-1.4, 7.0, 9.0), H5 + up),
            (28.85, H5 + _v(-0.25, 0.70, 1.70), H5 + up),
            (29.40, H5 + _v(-0.05, 0.66, 1.55), H5 + up),
            (29.95, H5 + _v(0.15, 0.62, 1.45), H5 + up),
            (30.12, H5 + _v(0.2, 0.75, 1.9), H5 + up + _v(0.0, 0.3, -2.0)),
            (30.6, E5 + _v(-0.9, 1.75, 5.4), E5 + _v(0.0, 1.95, 0.0)),
            (31.60, E5 + _v(0.2, 1.65, 4.4), E5 + _v(0.0, 1.95, 0.0)),
            (33.40, E5 + _v(1.6, 1.75, 3.9), E5 + _v(0.0, 2.0, 0.0))]


# S6: an arc round the two profiles, head and shoulders
def _s6(t):
    u = (t - SEC[5]) / (SEC[6] - SEC[5])
    a = np.radians(-24.0 + 46.0 * u)
    r = 2.75 - 0.35 * u
    return F6 + _v(np.sin(a) * r, 1.72, np.cos(a) * r), F6 + _v(0.0, 1.93, 0.0)


# S7: the breath, the orbit on the biggest hit, the corkscrew up the braid
def _s7_breath(t):
    u = _sc(SEC[6], 42.0, t)
    p = G7 + _v(9.0, 3.4, 15.5) * (1.0 - u) + at3(ORB7_A0, 7.7, 2.1) * u     # far behind her, gliding in
    return p, G7 + _v(0.0, 2.6, 0.0)


ORB7_A0 = 30.0
BRAID_T0 = 45.65


def _orb7_angle(t):
    u = max(t - BREATH_END, 0.0)
    return np.radians(ORB7_A0 - 30.0 * u - 1.0 * u * u - 14.0 * max(t - BRAID_T0, 0.0) ** 2)


def _orb7_radius(t):
    return 7.7 - 0.25 * max(t - BREATH_END, 0.0)


def _y_climb(t):
    u = max(t - BRAID_T0, 0.0)
    return 2.1 + 2.0 * u + 7.4 * u * u


def _s7_orbit(t):
    a, r = _orb7_angle(t), _orb7_radius(t)
    p = G7 + _v(np.sin(a) * r, 2.1, np.cos(a) * r)
    return p, G7 + _v(0.0, 2.6, 0.0)


def _s7_braid(t):
    u = max(t - BRAID_T0, 0.0)
    a = _orb7_angle(t)
    r = 0.7 + (_orb7_radius(BRAID_T0) - 0.7) * np.exp(-u / 0.55)
    p = G7 + _v(np.sin(a) * r, _y_climb(t), np.cos(a) * r)
    h = _unit(_v(G7[0] - p[0], 0.0, G7[2] - p[2]))
    b = np.radians(88.0) * _sc(BRAID_T0 + 0.1, BRAID_T0 + 1.5, t) + np.radians(3.0)
    f = np.cos(b) * h + np.sin(b) * UP
    return p, p + 20.0 * f


def _s7_up(t):
    if t < BRAID_T0:
        return UP
    p, _ = _s7_braid(t)
    h = _unit(_v(G7[0] - p[0], 0.0, G7[2] - p[2]))
    b = np.radians(88.0) * _sc(BRAID_T0 + 0.1, BRAID_T0 + 1.5, t) + np.radians(3.0)
    return _unit(-np.sin(b) * h + np.cos(b) * UP)


# S8: morning: down from the sky, a glide to rest in front of the arch
ARCH = dict(span=64.0, height=30.0, z=0.0)


def _rig(focus):
    def fo(default):
        return (lambda t: focus(t, default)) if focus is not None else "target"

    return Rig([
        fly(_flight_keys(), fov=lambda t: 50.0 + 12.0 * _sc(0.3, 2.2, t) - 4.0 * _sc(8.0, 9.0, t),
            roll=_roll_s12, aperture=lambda t: 0.03 * (1.0 - _sc(0.4, 1.6, t)) + 0.004,
            focus=fo(lambda t: SEED if t < 1.2 else np.asarray(PW.place(_LAYOUT_SIMPLE, t, 0.5, 0.5, 14.0)))),
        Path(_s3, SEC[2], SEC[3], blend=0.9, fov=lambda t: 56.0 - 10.0 * _sc(13.3, 14.4, t), roll=0.0,
             aperture=0.03, focus=fo(C3 + _v(0, 1.0, 0))),
        Path(_s4, SEC[3], SEC[4], blend=0.0, fov=lambda t: 54.0 + 10.0 * _sc(LOOP_T0, LOOP_T1, t),
             up=_s4_up, aperture=lambda t: 0.02 * (1.0 - _sc(LOOP_T0, LOOP_T0 + 0.6, t)),
             focus=fo(lambda t: D4 + _v(0, 1.4, 0))),
        fly(_s5_keys(), blend=0.0, fov=lambda t: 62.0 - 14.0 * _sc(28.2, 28.9, t),
            aperture=lambda t: 0.004 + 0.010 * _sc(28.3, 28.9, t) + 0.012 * _sc(30.2, 30.6, t), near=0.03,
            roll=lambda t: -10.0 * np.sin(np.pi * _sc(26.9, 29.6, t)),
            focus=fo(lambda t: H5 if t < 30.15 else E5 + _v(0, 1.3, 0))),
        Path(_s6, SEC[5], SEC[6], blend=0.0, fov=38.0, aperture=0.035, focus=fo(F6 + _v(0, 1.55, 0))),
        Path(_s7_breath, SEC[6], 41.9, blend=0.0, fov=48.0, aperture=0.03, focus=fo(G7 + _v(0, 1.2, 0))),
        Path(_s7_orbit, 41.9, BRAID_T0, blend=0.9, fov=52.0, aperture=0.02, focus=fo(G7 + _v(0, 1.2, 0))),
        Path(_s7_braid, BRAID_T0, SEC[7], blend=0.5, up=_s7_up, fov=lambda t: 64.0 + 30.0 * _sc(46.0, 49.4, t),
             aperture=0.0, focus=30.0),
        fly([(SEC[7], _v(0.0, 36.0, 96.0), _v(0.0, 24.0, 0.0)), (51.4, _v(0.0, 15.0, 64.0), _v(0.0, 15.0, 0.0)),
             (54.6, _v(0.0, 4.8, 45.5), _v(0.0, 13.6, 0.0)), (TOTAL, _v(0.0, 4.2, 42.0), _v(0.0, 13.6, 0.0))],
            blend=0.0, ease="out", fov=50.0, aperture=0.0, focus=40.0),
    ], blend=0.6, fov=50.0, aperture=0.02, handheld=0.15, min_height=0.3)


_LAYOUT_SIMPLE = None
_LAYOUT_SIMPLE = _rig(None)          # the camera without the words' focus: for layout and comet paths
_LAYOUT = _LAYOUT_SIMPLE


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


# ---------------------------------------------------------------------------------------------------------
# The people (built when the scene is set up: the workflow's first job imports this file with numpy only)
# ---------------------------------------------------------------------------------------------------------
# THE ACTING PLAN (UPDATE 6): every ribbon wraps the people who ACT its words while they read, each in a
# different style and framing.
#   Greeting       a man on the water turns to us and waves across the distance: a constellation (plexus),
#                  full figure, far to near as the chase passes him
#   Concession     a line of six people parting along the gate, each holding an open palm toward the path:
#                  silhouettes that are windows onto a day sky, releasing birds; many
#   Apology        a man stands with his head bowed and his hands low, shedding glass shards; half figure
#   Inclusiveness  the woman who waited walks to him and they embrace: a dotted body and the shard body; close
#   Compliment     a dancer twirls, embers bursting off her, while three far figures applaud (plexus); full, far
#   Consideration  hands only: a rose hand reaches down to a gold hand reaching up, and takes it; extreme close-up
#   Gratitude      a woman bows with her hand on her heart: gold glitter dissolving; half figure
#   Respect        two people face each other, one speaking with an open hand, one leaning in to listen:
#                  a profile filled with a sunrise and a profile outlined in sparks; close, head and shoulders
#   Encouragement  someone kneels in prayer, a small sparkling figure in mist, and on the biggest hit eight people
#                  in the other colours gather round and raise a hand for her; far, then many
#   Morning        none: only the nine lights and the end card
_REFS = {}


def at3(az, r, h=0.0):
    a = np.radians(az)
    return _v(np.sin(a) * r, h, np.cos(a) * r)


def _bodies():
    if _BODIES:
        return _BODIES
    from p3d.body import Body, Hands
    from p3d import pairs
    w = (0.25, 0.0, -0.2)
    B = _BODIES
    # S1 Greeting: a constellation of a man who turns to the oncoming light and waves
    B["walker"] = Body("man", at=(2.4, 193.0), facing=8.0, motion="stand", garment="coat", look="plexus",
                       color=COL[GREET], color2="#fff0e6", points=40000, show=(3.3, 7.0), fade=0.3, wind=w,
                       seed=12.0, gesture=[(3.9, 9.0, "wave", dict(side="R"))],
                       effects=[dict(kind="form", t=3.3, dur=1.2)])
    # S2 Concession: a line of people parting along the gate, an open palm toward the path
    for i in range(6):
        side = -1.0 if i % 2 == 0 else 1.0
        z = TUNNEL_Z0 - HOOP_GAP * (0.25 + 0.55 * i)
        B["gate%d" % i] = Body("woman" if i % 3 != 1 else "man", at=(side * 3.3, z),
                               facing=90.0 if side < 0 else 270.0, motion="stand", garment="robe", look="window",
                               color=COL[CONC], color2="#ffffff", points=30000, show=(6.9 + 0.15 * i, 11.9),
                               fade=0.35, wind=w, seed=20.0 + i,
                               gesture=[(7.2 + 0.25 * i, 14.0, "offer", dict(side="L" if side < 0 else "R"))],
                               effects=[dict(kind="form", t=6.9 + 0.15 * i, dur=1.1),
                                        dict(kind="birds", t=8.6 + 0.3 * i, dur=2.0, n=10, size=0.16,
                                             color="#eaf3ff", speed=2.0)])
    # S3 Apology and Inclusiveness: he stands bowed, hands low, glass falling from him; she comes and holds him
    # (pairs.embrace's own approach counts the walk from t = 0 in a long song: the walk-in is given here)
    sorry, kind = pairs.embrace(
        TOUCH3 + 0.3, at=(C3[0], C3[2]), facing=90.0, approach=0.0,
        a=dict(shape="man", garment="tunic", look="glitter", color=COL[APOL], color2="#fff1e0", points=60000,
               at=(C3[0] - 0.17, C3[2]),
               show=(SEC[2] - 0.3, 20.4), fade=0.3, wind=w, seed=3.0,
               gesture=[(SEC[2], TOUCH3 - 0.5, "bow", dict(amount=24.0)),
                        (SEC[2] + 0.3, TOUCH3 - 0.6, "offer", dict(side="R"))],
               effects=[dict(kind="form", t=SEC[2] - 0.2, dur=1.3),
                        dict(kind="shed", t=13.8, until=17.2, n=1800, life=1.6, sprite="flake", size=1.6,
                             speed=0.15, rise=-0.45, spread=0.2, color="#ffc79a", bright=0.8)]),
        b=dict(shape="woman", garment="dress", look="dots", color=COL[INCL], color2="#ffd9ea", points=60000,
               at=(C3[0] + 0.17 + 0.90, C3[2]),
               motion=[(-1e9, "stand"), (15.9, "walk", dict(speed=0.9)), (16.95, "stand", dict(blend=0.8))],
               show=(SEC[2] - 0.3, 20.4), fade=0.3, wind=w, seed=4.0,
               effects=[dict(kind="form", t=SEC[2] + 0.1, dur=1.4)]))
    B["sorry"], B["kind"] = sorry, kind
    # S4 Compliment: a dancer twirls with embers bursting off her; three far figures applaud
    B["dancer"] = Body("woman", at=(D4[0], D4[2]), facing=30.0, motion=[(17.5, "dance")], garment="dress",
                       look="glitter", color=COL[COMP], color2="#f4ecff", points=75000, bright=1.25,
                       show=(SEC[3] - 0.1, LOOP_T1 + 0.3), fade=0.15, wind=(0.0, 0.0, 0.0), seed=6.0,
                       effects=[dict(kind="form", t=SEC[3] - 0.1, dur=0.9),
                                dict(kind="disperse", amount=Track([(0.0, 0.0), (21.2, 0.0), (22.6, 0.22),
                                                                    (24.0, 0.30), (25.2, 0.05), (TOTAL, 0.0)]),
                                     share=0.6, color="#ffd2a8", color2=COL[COMP], speed=1.2, rise=0.5)])
    for i, (az, r) in enumerate(((205.0, 7.5), (235.0, 8.5), (262.0, 7.8))):
        p = D4 + at3(az, r)
        B["fan%d" % i] = Body(("man", "woman", "man")[i], at=(p[0], p[2]), facing=(az + 180.0) % 360.0,
                              motion="stand", garment=("coat", "dress", "tunic")[i], look="plexus", color=COL[COMP],
                              color2="#ffffff", points=26000, show=(SEC[3], LOOP_T0 + 0.5), fade=0.3, seed=30.0 + i,
                              gesture=[(20.6 + 0.2 * i, 26.0, "clap", dict(period=0.46 + 0.03 * i, height=0.6))])
    # S5 Consideration: hands only, a rose hand reaching down takes a gold hand reaching up
    hs = Hands(meet=tuple(H5), t_touch=HANDS_T, axis=90.0, color=COL[GRAT], color2=COL[CONS], approach=2.6,
               apart=0.55, tilt=32.0, points=60000)
    B["hand_gold"], B["hand_rose"] = hs["left"], hs["right"]
    for hb in (hs["left"], hs["right"]):          # the hands exist only in their section
        hb.show = (SEC[4], 30.35)
    _REFS["hands_flare"] = hs["flare"]
    # S5 Gratitude: a bow with a hand on the heart, gold glitter dissolving
    B["bower"] = Body("woman", at=(E5[0], E5[2]), facing=6.0, motion="stand", garment="dress", look="glitter",
                      color=COL[GRAT], color2="#fff4d8", points=70000, show=(29.9, SEC[5] + 0.2), fade=0.3, seed=7.0,
                      gesture=[(30.4, 40.0, "touch", dict(side="R", palm="in",
                                                           to=lambda t: _REFS["bower"].where(t, "heart", raw=True))),
                               (30.9, 40.0, "bow", dict(amount=26.0))],
                      effects=[dict(kind="form", t=29.9, dur=1.0),
                               dict(kind="shed", t=30.6, dir=(0.0, 1.0, -0.3), speed=0.25, rise=0.25, n=5000)])
    _REFS["bower"] = B["bower"]
    # S6 Respect: one speaks with an open hand, one leans in to listen; a profile of sunrise, a profile of sparks
    B["speaker"] = Body("woman", at=(F6[0] - 0.45, F6[2]), facing=90.0, motion="stand", garment="dress",
                        look="window", color=COL[RESP], color2="#ffe8d6", points=60000,
                        show=(SEC[5] - 0.2, SEC[6] + 0.2), fade=0.2, seed=9.0,
                        gesture=[(34.2, 40.0, "offer", dict(side="L"))],
                        effects=[dict(kind="form", t=SEC[5] - 0.2, dur=1.2)])
    B["listener"] = Body("man", at=(F6[0] + 0.45, F6[2]), facing=270.0, motion="stand", garment="coat",
                         look=["rim", dict(name="glitter", bright=0.5)], color=COL[RESP], color2="#fff0e0",
                         points=80000, detail=dict(head=3), show=(SEC[5] - 0.2, SEC[6] + 0.2), fade=0.2, seed=10.0,
                         effects=[dict(kind="form", t=SEC[5], dur=1.2),
                                  dict(kind="shed", t=SEC[5] + 0.5, where="back", dir=(1, 0.3, 0), speed=0.3,
                                       n=3000)],
                         gesture=[(34.6, 40.0, "listen", dict(side="R"))])
    # S7 Encouragement: a small sparkling figure kneeling in prayer in mist; a crowd raises a hand for her
    B["praying"] = Body("woman", at=(G7[0], G7[2]), facing=180.0, motion=[(37.0, "kneel")],
                        gesture=[(37.0, 60.0, "pray")], garment="robe", veil=True, look="glitter", color=COL[ENC],
                        color2="#e8dcff", points=50000, bright=0.75, show=(SEC[6] - 0.1, 49.0), fade=0.3, seed=11.0,
                        effects=[dict(kind="form", t=SEC[6], dur=1.6),
                                 dict(kind="shed", t=SEC[6] + 0.5, speed=0.12, rise=0.18, n=6000, life=3.5),
                                 dict(kind="dissolve", t=BRAID_T0 + 0.1, dur=2.6)])
    others = [k for k in range(9) if k != ENC]
    for j, k in enumerate(others):
        az = 118.0 + 124.0 * j / 7.0
        p = G7 + at3(az, 10.5 + 0.8 * (j % 2))
        B["crowd%d" % j] = Body(("woman", "man", "child", "woman", "man", "woman", "man", "woman")[j],
                                at=(p[0], p[2]), facing=(az + 180.0) % 360.0, motion="stand",
                                garment=("robe", "coat", "tunic")[j % 3], look="glitter", color=COL[k],
                                color2="#ffffff", points=24000, bright=0.9,
                                show=(BREATH_END - 0.25, BRAID_T0 + 1.0), fade=0.35, seed=40.0 + j,
                                gesture=[(BREATH_END + 0.2 + 0.08 * j, 60.0, "raise_hand",
                                          dict(side="R" if j % 2 else "L"))],
                                effects=[dict(kind="form", t=BREATH_END - 0.25, dur=0.9),
                                         dict(kind="dissolve", t=BRAID_T0 - 0.2, dur=1.6)])
    return _BODIES


# ---------------------------------------------------------------------------------------------------------
# The nine comets: each head is a function of time made of legs blended into a base path.
# ---------------------------------------------------------------------------------------------------------
BURST_AZ = [180.0 + (k - 4) * 26.0 for k in range(9)]
BURST_EL = [8.0 + 6.0 * ((k * 5) % 4) for k in range(9)]
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
    if t < SEC[0]:                      # before the opening hit the nine colours rush into the seed
        v = SEC[0] - t
        a = 1.4 * v * (1.0 if k % 2 == 0 else -1.0)
        d0 = _burst_dir(k)
        d = _v(d0[0] * np.cos(a) + d0[2] * np.sin(a), d0[1] + 0.35, -d0[0] * np.sin(a) + d0[2] * np.cos(a))
        return SEED + (130.0 * v + 60.0 * v * v) * _unit(d)
    u = max(t - SEC[0], 0.0)
    d = 95.0 * (1.0 - np.exp(-u * 1.6)) + 30.0 * u
    return SEED + d * _burst_dir(k) + _v(0.0, -2.0 * u, 0.0)


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
    return lambda t: WORDS[name].pen(t)


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
    """The lavender ribbon's head: led by the dancer's hand, flying wide circles round her."""
    a = 3.1 * t
    return _dancer_hand(t) + _v(0.9 * np.sin(a), 0.5 + 0.35 * np.sin(1.7 * t), 0.9 * np.cos(a))


def _loop_ahead(t):
    """The lavender ribbon leads the flip: a wider arc over the dancer, ahead of the camera."""
    a, phi = _s4_az(t) + 0.35, min(_loop_phi(t) + 0.6, np.pi)
    h = _v(np.sin(a), 0.0, np.cos(a))
    return D4 + _v(0.0, S4_EYE, 0.0) + 2.6 * (np.cos(phi) * h + np.sin(phi) * UP)


def _palm5(t):
    return np.asarray(_bodies()["child"].where(t, "palm.R"), np.float64)


def _gold_stream(t):
    """Gold blown from the child's palm, spiralling up through the waking lanterns."""
    u = max(t - 30.4, 0.0)
    a = 2.2 * u
    return _palm5(min(t, 30.4)) + _v(np.sin(a) * (1.0 + 2.5 * u), 0.6 * u + 0.8 * u * u, -np.cos(a) * (1.0 + 2.5 * u) - 1.5 * u)


def _weave6(t):
    a = 2.4 * t
    return F6 + _v(0.78 * np.sin(a), 1.30 + 0.12 * np.sin(2.0 * a), -0.30 + 0.45 * np.sin(2.0 * a))


def _thread7(t):
    u = max(t - SEC[6], 0.0)
    return G7 + _v(0.15 * np.sin(3.0 * t), 1.05 + 0.9 * u, -0.05)


def _circle7(k):
    def f(t):
        a = 1.25 * t + 2.0 * np.pi * k / 9.0
        return G7 + _v(np.sin(a) * 13.0, 1.6 + 2.2 * np.sin(1.3 * t + k), np.cos(a) * 13.0)
    return f


def _braid(k):
    def f(t):
        u = max(t - BRAID_T0, 0.0)
        a = 1.25 * t + 2.0 * np.pi * k / 9.0 + 1.6 * u + 0.9 * u * u
        r = 0.9 + 12.1 * np.exp(-u / 0.9)
        y = (_y_climb(t) - _y_climb(BRAID_T0) + 1.6 + 2.2 * np.sin(1.3 * t + k) * (1.0 - _sc(BRAID_T0, BRAID_T0 + 1.0, t))
             + 14.0 * _sc(BRAID_T0, BRAID_T0 + 1.4, t))
        return G7 + _v(np.sin(a) * r, y, np.cos(a) * r)
    return f


# ---------------------------------------------------------------------------------------------------------
# The words: all nine, exact campaign wording from words.EXPRESSIONS
# ---------------------------------------------------------------------------------------------------------
def _width(t, depth, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _dist(t, p):
    return float(np.linalg.norm(np.asarray(p, np.float64) - PW._cam_at(_LAYOUT, t).pos))


_RIDE1 = (0.5, 0.60, 14.0)
_RIDE2 = (0.5, 0.67, 12.0)
_RIDE5 = (0.5, 0.56, 15.0)
_AT3 = C3 + _v(0.0, 2.62, 0.0)
_AT4 = D4 + _v(0.0, 2.78, 0.0)
_AT5 = E5 + _v(0.0, 2.48, 0.0)
_AT6 = F6 + _v(0.0, 2.17, -0.05)
_AT7 = G7 + _v(0.0, 3.35, 0.0)

_SPECS = [            # every leaving is a clean fade (no broken letters in any frame); one expression at a time
    dict(expr="Greeting", ride=_RIDE1, face="screen", width=_width(4.6, _RIDE1[2], 0.34),
         t_in=3.6, t_read0=4.1, t_read1=6.6, t_out=6.84, arrive="pen", nib=False, leave="fade"),
    dict(expr="Concession", ride=_RIDE2, face="screen", width=_width(9.5, _RIDE2[2], 0.50),
         t_in=6.84, t_read0=8.15, t_read1=10.7, t_out=10.95, arrive="pen", nib=False, leave="fade"),
    dict(expr="Apology", pos=_AT3, face="camera", width=_width(15.6, _dist(15.6, _AT3), 0.74),
         t_in=13.35, t_read0=14.2, t_read1=16.75, t_out=17.0, arrive="pen", nib=False, leave="fade"),
    dict(expr="Inclusiveness", pos=_AT3 + _v(0.0, -0.1, 0.0), face="camera",
         width=_width(18.5, _dist(18.5, _AT3), 0.62),
         t_in=17.0, t_read0=17.3, t_read1=19.83, t_out=19.95, arrive="reveal", edge="right", leave="fade"),
    dict(expr="Compliment", pos=_AT4, face="camera", width=_width(23.5, _dist(23.5, _AT4), 0.60),
         t_in=20.15, t_read0=21.45, t_read1=24.6, t_out=25.0, arrive="pen", nib=False, leave="fade"),
    dict(expr="Consideration", ride=_RIDE5, face="screen", width=_width(28.9, _RIDE5[2], 0.56),
         t_in=26.85, t_read0=27.4, t_read1=29.9, t_out=30.15, arrive="pen", nib=False, leave="fade"),
    dict(expr="Gratitude", pos=_AT5, face="camera", width=_width(32.0, _dist(32.0, _AT5), 0.70),
         t_in=30.15, t_read0=30.8, t_read1=33.32, t_out=33.45, arrive="pen", nib=False, leave="fade"),
    dict(expr="Respect", pos=_AT6, face="camera", width=_width(36.8, _dist(36.8, _AT6), 0.48),
         t_in=33.9, t_read0=35.1, t_read1=37.8, t_out=38.05, arrive="pen", nib=False, leave="fade"),
    dict(expr="Encouragement", pos=_AT7, face="camera", width=_width(43.9, _dist(43.9, _AT7), 0.66),
         t_in=42.6, t_read0=43.0, t_read1=45.5, t_out=45.75, arrive="reveal", edge="down", leave="fade"),
    # C: the date in light across the sky in the breath (its small line beneath it, see _date_drive)
    dict(label="Healing Concert · 4:30 PM", lines=["December 6"], name="Date", ride=(0.5, 0.70, 18.0),
         face="screen", width=_width(41.5, 18.0, 0.50), color="#ffd27a", tint=0.25, label_size=0.30,
         t_in=40.25, t_read0=40.95, t_read1=BREATH_END, t_out=42.9, arrive="pen", leave="bokeh"),
]
def _clean_leave(t, info):
    """Every word leaves in place and sharp, thinning out evenly: never smeared, drifting or broken letters.
    The date (C) instead bursts apart on the hit, and its small line sits beneath it."""
    w = info["word"]
    if w.name == "Date":
        return _date_drive(t, info)
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)
    return None


_DATE_SHIFT = {}


def _date_drive(t, info):
    """The date's label ("HEALING CONCERT · 4:30 PM") is moved from above the date to beneath it."""
    w = info["word"]
    if "k" not in _DATE_SHIFT:
        hm = w.home()
        lab = np.asarray(hm["label"], bool)
        y = np.asarray(hm["y"], np.float64)
        top_lab, low_ph = float(y[lab].max()), float(y[~lab].min())
        _DATE_SHIFT["k"] = (lab, (top_lab - low_ph) + 0.35 * w.metres_per_em())
    lab, dy = _DATE_SHIFT["k"]
    u = np.asarray(info["frame"][2], np.float32)
    pos = np.asarray(info["pos"], np.float32).copy()
    pos[lab] -= u[None, :] * np.float32(dy)
    return dict(pos=pos)


WORDS = PW.Words(_SPECS, camera=_LAYOUT, reflect=False, drive=_clean_leave)   # no mirrored text in the lake


CUT_TIMES = [0.0, SEC[3], SEC[4], SEC[5], SEC[6], SEC[7]]


def _focus(t, default, ease=0.8):
    """A focus point that racks to the word being read, but only to a word of the current section that is in
    front of the camera (a word left behind at a cut would otherwise pull the focus to almost nothing)."""
    d = np.asarray(default(t) if callable(default) else default, np.float64)
    if 28.4 < t < 30.2:
        return d                        # the hands' close-up keeps the hands sharp (the words are sharp anyway)
    cut = max([c for c in CUT_TIMES if c <= t] + [-1e9])
    st = _LAYOUT_SIMPLE.state(t)
    fwd = _unit(np.asarray(st.target) - np.asarray(st.pos))
    acc, wsum, top = np.zeros(3), 0.0, 0.0
    for w in WORDS:
        if w.t_in < cut - 0.01:
            continue
        end = w.to.t_in if (w.leave == "morph" and isinstance(w.to, PW.Word)) else w.t_read1
        k = _sc(w.t_read0 - ease, w.t_read0, t) * (1.0 - _sc(end, end + ease, t))
        if k <= 0.0:
            continue
        c = np.asarray(w.centre(t), np.float64)
        if float(np.dot(c - np.asarray(st.pos), fwd)) < 0.5:
            continue
        acc += k * c
        wsum += k
        top = max(top, k)
    if wsum <= 0.0:
        return d
    return d + (acc / wsum - d) * top


CAMERA = _rig(_focus)

# the comets' legs (after WORDS: the pens are the words' own)
HEADS[GREET].leg(3.6, 4.1, _pen("Greeting"), bi=0.8, bo=0.5) \
            .leg(4.3, 6.4, _screen(0.5, 0.24, 20.0, wx=0.30, wy=0.05, rate=0.8), bi=0.5, bo=1.2)
HEADS[CONC].leg(6.84, 8.15, _pen("Concession"), bi=1.3, bo=0.25) \
           .leg(8.4, 11.6, _tunnel, bi=0.25, bo=1.5)
HEADS[APOL].leg(13.35, 14.2, _pen("Apology"), bi=0.9, bo=0.6) \
           .leg(14.7, SEC[3], _helix(C3, 1.45, 0.25, 1.05, 2.2, 0.0), bi=0.6, bo=0.0)
HEADS[INCL].leg(13.6, SEC[3], _helix(C3, lambda t: 1.9 - 0.4 * _sc(17.0, 18.5, t), 0.9, 1.7, 2.2, np.pi, 0.9),
                bi=1.0, bo=1.2)
HEADS[COMP].leg(SEC[3], 20.15, _ribbon_from_hand, bi=0.0, bo=0.3) \
           .leg(20.15, 21.45, _pen("Compliment"), bi=0.3, bo=0.5) \
           .leg(21.9, LOOP_T0, _ribbon_from_hand, bi=0.5, bo=0.4) \
           .leg(LOOP_T0 + 0.2, SEC[4], _loop_ahead, bi=0.4, bo=0.0)
HEADS[CONS].leg(SEC[4], 27.4, _pen("Consideration"), bi=0.0, bo=0.5) \
           .leg(27.8, 30.1, _helix(H5, 0.75, -0.35, 0.05, 2.4, 0.5), bi=0.6, bo=0.5) \
           .leg(30.6, SEC[5], _helix(E5, 2.6, 0.4, 1.4, 1.4, 2.5), bi=0.6, bo=0.0)
HEADS[GRAT].leg(30.15, 30.8, _pen("Gratitude"), bi=0.5, bo=0.4) \
           .leg(31.1, SEC[5], _helix(E5, 2.2, 0.5, 2.6, 1.6, 0.3), bi=0.5, bo=0.0)
HEADS[RESP].leg(33.9, 35.1, _pen("Respect"), bi=0.5, bo=0.5) \
           .leg(35.4, SEC[6], _weave6, bi=0.5, bo=0.0)
HEADS[ENC].leg(BREATH_END, BRAID_T0, _circle7(ENC), bi=1.4, bo=0.0)
for _k in range(9):
    if _k != ENC:                         # (the violet one was given its circle above)
        HEADS[_k].leg(BREATH_END, BRAID_T0, _circle7(_k), bi=1.4, bo=0.0)
    HEADS[_k].leg(BRAID_T0, SEC[7] + 0.5, _braid(_k), bi=0.0 if _k != ENC else 0.8, bo=0.0)


def _arch_places():
    """The nine lights of the morning: a shallow arc of stars over the title, placed by the end card's own
    picture (screen x from 0.07 to 0.93, y from 0.875 at the ends to 0.96 in the middle) on the plane z = 0."""
    cam = PW._cam_at(_LAYOUT, 57.0)
    r, u, f = cam.basis()
    half = np.tan(np.radians(cam.fov) * 0.5)
    out = []
    for i in range(9):
        sx = 0.07 + 0.86 * i / 8.0
        sy = 0.875 + 0.085 * np.sin(np.pi * i / 8.0)
        d = f + r * (sx - 0.5) * 2.0 * half * cam.aspect + u * (sy - 0.5) * 2.0 * half
        k = (0.0 - cam.pos[2]) / d[2]
        out.append(cam.pos + k * d)
    return np.array(out)


ARCH_AT = _arch_places()
ARCH_ORDER = list(range(9))          # left to right: the order of words.EXPRESSIONS, as on every arch
ARCH_LAND = [SEC[7] + 0.55 + 0.1 * abs(k - 4) for k in range(9)]


def _to_arch(k):
    i = ARCH_ORDER.index(k)
    home = ARCH_AT[i]
    p0 = home + _v(0.4 * (i - 4), 46.0, 14.0)      # out of the sky above the picture, down into its place
    c1 = home + _v(0.0, 9.0, 3.0)

    def f(t):
        u = float(np.clip((t - SEC[7]) / (ARCH_LAND[k] - SEC[7]), 0.0, 1.0))
        e = 1.0 - (1.0 - u) ** 2.2
        p = (1 - e) ** 2 * p0 + 2 * e * (1 - e) * c1 + e * e * home
        return p + _v(0.0, 0.25 * np.sin(1.3 * t + i), 0.0) * _sc(ARCH_LAND[k], ARCH_LAND[k] + 1.0, t)
    return f


for _k in range(9):
    HEADS[_k].leg(SEC[7], TOTAL + 1.0, _to_arch(_k), bi=0.0, bo=0.0)


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


CUTS = [SEC[3], SEC[4], SEC[5], SEC[6], SEC[7]]
PEN_OF = {"Greeting": GREET, "Concession": CONC, "Apology": APOL, "Compliment": COMP, "Consideration": CONS,
          "Respect": RESP, "Gratitude": GRAT, "Inclusiveness": INCL, "Encouragement": ENC}


class Comets:
    """The nine ribbons of colour: a white-hot core, a coloured glow, a head that blooms, sparks shed behind."""

    def __init__(self):
        r = np.random.default_rng(10)
        self.sp = r.random((9, 140, 4)).astype(np.float64)

    def _alpha(self, k, t):
        return 1.0

    def _near(self, k, t):
        """1 while the comet is a lead near the camera, 0 while it is far away on the ring."""
        n = 0.0
        for t0, t1, _, bi, bo in HEADS[k].legs:
            n = max(n, _sc(t0 - bi, t0, t) * (1.0 - (_sc(t1, t1 + bo, t) if bo > 0 else float(t > t1))))
        if t < 3.4:
            n = max(n, 1.0 - _sc(1.6, 3.4, t))
        if t < SEC[0]:
            n = 1.0
        return n

    wants_camera = True

    def _boxes(self, t, cam):
        """Screen boxes of the words on screen now, padded, with the comet that may cross each (its pen)."""
        out = []
        if cam is None:
            return out
        for w in WORDS:
            if not (w.t_in - 0.2 <= t <= w.t_out):
                continue
            b = PW.screen_box(w, cam, t)
            if not b[4]:
                continue
            pen = PEN_OF.get(w.name)
            free = pen if (t < w.t_read0 + 0.3 or t > w.t_read1) else None
            out.append(((b[0] - 0.025, b[1] + 0.025, b[2] - 0.03, b[3] + 0.035), free))
        bb = _badge_box(t)
        if bb is not None:
            out.append((bb, None))
        return out

    @staticmethod
    def _dim(pts, cam, boxes, k):
        xy, z = cam.project(pts)
        f = np.ones(len(pts))
        for (x0, x1, y0, y1), free in boxes:
            if free == k:
                continue
            e = 0.02
            inside = (_ss(x0 - e, x0, xy[:, 0]) * (1.0 - _ss(x1, x1 + e, xy[:, 0]))
                      * _ss(y0 - e, y0, xy[:, 1]) * (1.0 - _ss(y1, y1 + e, xy[:, 1])))
            f = np.minimum(f, 1.0 - 0.94 * inside * (z > 0))
        return f

    def sample(self, t, cam=None):
        out = []
        cut = max([c for c in CUTS if c <= t] + [-2.0])      # tails never reach back across a cut
        boxes = self._boxes(t, cam)
        eye = None if cam is None else np.asarray(cam.pos, np.float64)
        for k in range(9):
            a = self._alpha(k, t)
            if a <= 0.0:
                continue
            start = len(out)
            self._one(out, k, t, a, cut, eye)
            if boxes:
                for b in out[start:]:
                    f = self._dim(np.asarray(b["pos"], np.float64).reshape(-1, 3), cam, boxes, k)
                    if f.min() < 0.999:
                        b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * f
                        if b.get("pos2") is not None:
                            b["alpha2"] = np.asarray(b.get("alpha2", 1.0), np.float64) * self._dim(
                                np.asarray(b["pos2"], np.float64).reshape(-1, 3), cam, boxes, k)
        return out

    def _one(self, out, k, t, a, cut, eye):
        if True:
            a = a * (1.0 - 0.45 * _sc(48.7, SEC[7] - 0.05, t) * (1.0 - _sc(SEC[7] - 0.05, SEC[7], t)))
            near = self._near(k, t)
            quiet = 0.0 if SEC[4] - 0.05 <= t < SEC[6] else 0.3
            a = a * (quiet + (1.0 - quiet) * near)
            if a <= 0.002:
                return
            tail = 0.55 * near + 2.2 * (1.0 - near)
            if BRAID_T0 - 0.2 < t:
                tail = 0.45
            w = 0.30 * near + 1.6 * (1.0 - near)
            if t > BRAID_T0:
                w = 0.30 + 0.25 * _sc(BRAID_T0, SEC[7], t)
            day = 1.0 if t >= SEC[7] else 0.0
            if day:
                tail = 1.1 * (1.0 - _sc(ARCH_LAND[k] - 0.5, ARCH_LAND[k] + 0.6, t)) + 0.02
                w = 1.5 - 0.4 * _sc(ARCH_LAND[k], ARCH_LAND[k] + 0.8, t)
            n = 40
            ts = np.linspace(max(t - tail, cut), t, n)
            if ts[-1] - ts[0] < 1e-3:
                return
            pts = np.array([HEADS[k](float(x)) for x in ts])
            if eye is not None:                         # a head right at the lens would fill the picture
                dist = float(np.linalg.norm(pts[-1] - eye))
                a = a * _sc(1.0, 3.0, dist)
                if a <= 0.0:
                    return
                if not day:
                    w = w * float(np.clip(dist / 6.0, 0.35, 1.0))     # close-ups get a finer ribbon
            age = (t - ts) / tail                       # 0 at the head, 1 at the far end
            kk = 1.0 - age
            c = lin(COL[k])
            deep = deepen(COL[k])
            core = 0.35 * c + 0.65 * lin(WHITE)
            if day:
                pc = show(COL[k])
                out.append(_rib(pts, w * (0.12 + 0.88 * kk), pc, a * 0.9 * np.clip(kk * 1.4, 0, 1), emit=1.0,
                                paint=1.0, paint_light=0.5))
                out.append(_rib(pts, w * 0.22 * (0.15 + 0.85 * kk), core, a * 0.95 * np.clip(kk * 1.6, 0, 1),
                                emit=2.6))
                head = pts[-1:]
                land = _sc(ARCH_LAND[k] - 0.2, ARCH_LAND[k] + 0.5, t)
                pulse = 1.0 + 0.12 * np.sin(5.0 * t + k)
                out.append(dict(pos=head, size=1.5 + 0.5 * land, color=pc, alpha=a * (0.55 + 0.4 * land) * pulse,
                                kind="soft", paint=1.0, paint_light=0.6))
                out.append(dict(pos=head, size=0.45, color=core, alpha=a * 0.8, emit=3.0, kind="spark"))
                out.append(dict(pos=head, size=5.0, color=c, alpha=a * 0.10 * land, kind="soft"))
                return
            out.append(_rib(pts, w * (0.12 + 0.88 * kk), deep, a * 0.55 * np.clip(kk * 1.4, 0, 1), emit=1.6))
            out.append(_rib(pts, w * 0.22 * (0.15 + 0.85 * kk), core, a * 0.95 * np.clip(kk * 1.6, 0, 1), emit=2.6))
            head = pts[-1:]
            out.append(dict(pos=head, size=w * 0.65, color=core, alpha=a, emit=7.0, kind="spark"))
            out.append(dict(pos=head, size=w * 5.0, color=c, alpha=a * 0.16, kind="soft"))
            sp = self.sp[k]
            f = np.mod(sp[:, 0] + t * (0.9 + 0.4 * sp[:, 1]), 1.0)          # where along the tail
            idx = f * (n - 1)
            i0 = np.floor(idx).astype(int)
            i1 = np.minimum(i0 + 1, n - 1)
            fr = (idx - i0)[:, None]
            base = pts[i0] * (1.0 - fr) + pts[i1] * fr
            drift = (sp[:, 1:4] - 0.5) * (w * 3.5) * (1.0 - f)[:, None]
            pos = base + drift - _v(0.0, 0.6 * w, 0.0) * (1.0 - f)[:, None]
            out.append(dict(pos=pos, size=w * (0.10 + 0.12 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                            alpha=a * 0.9 * f ** 1.5, emit=2.0, kind="spark", twinkle=0.6, seed=sp[:, 3]))
        return out


def _rib(pts, width, color, alpha, emit=1.0, **kw):
    from p3d.api import ribbon
    return ribbon(pts, width=width, color=color, alpha=alpha, emit=emit, **kw)


class Seed:
    """The white seed of light at frame 0, and its burst into sparks on the opening hit."""

    def __init__(self):
        r = np.random.default_rng(3)
        n = 2600
        d = r.normal(size=(n, 3))
        self.d = d / np.linalg.norm(d, axis=1, keepdims=True)
        self.s = r.random((n, 3))
        self.col = np.array([lin(COL[i % 9]) for i in range(n)]) * 0.6 + 0.4 * lin(WHITE)

    def sample(self, t):
        if t > 2.6:
            return None
        pre = 1.0 - _sc(SEC[0] - 0.02, SEC[0] + 0.2, t)
        out = []
        if pre > 0.0:
            pulse = 1.0 + 0.25 * np.sin(t * 40.0)
            out.append(dict(pos=SEED[None, :], size=0.22 * pulse, color=lin(WHITE), alpha=pre, emit=9.0,
                            kind="spark"))
            out.append(dict(pos=SEED[None, :], size=2.2, color=lin("#fff2dc"), alpha=0.35 * pre, kind="soft"))
            shell = SEED + self.d * (0.12 + 0.35 * self.s[:, :1]) * (1.0 + 0.4 * np.sin(t * 9.0 + 6.0 * self.s[:, 1:2]))
            out.append(dict(pos=shell[:600], size=0.012, color=lin("#fff4e2"), alpha=0.8 * pre, emit=3.0,
                            kind="spark", twinkle=0.8, seed=self.s[:600, 2]))
        u = t - SEC[0]
        if u > 0.0:
            dist = (2.0 + 26.0 * self.s[:, :1]) * (1.0 - np.exp(-u * 2.4))
            pos = SEED + self.d * dist - _v(0.0, 1.0, 0.0) * u * u
            al = np.exp(-u / (0.5 + 0.7 * self.s[:, 1]))
            out.append(dict(pos=pos, size=0.05 + 0.06 * self.s[:, 2], color=self.col, alpha=al, emit=3.0,
                            kind="spark", twinkle=0.5, seed=self.s[:, 2]))
        return out


class Hoops:
    """The gate: the blue comet's trail stays standing as half hoops over the water (birth times on a static
    set: each point lights as the comet passes it)."""

    def __init__(self):
        n = 9000
        self.ts = TUNNEL_T0 + np.linspace(0.0, HOOPS * HOOP_GAP / TUNNEL_V, n)
        rng = np.random.default_rng(12)
        self.pos = np.array([_tunnel(float(x)) for x in self.ts]) + rng.normal(size=(n, 3)) * 0.05
        self.size = 0.07 + 0.05 * rng.random(n)
        self.seed = rng.random(n)

    def sample(self, t):
        if t < TUNNEL_T0 - 0.1 or t > 14.6:
            return None
        return dict(pos=self.pos, size=self.size, color=deepen(COL[CONC], 1.2), alpha=0.85, birth=self.ts,
                    fade=0.25, flash=5.0, twinkle=0.5, seed=self.seed, kind="spark", emit=1.8)

    def gain(self, t):
        return float(_sc(TUNNEL_T0 - 0.1, TUNNEL_T0, t) * (1.0 - _sc(13.6, 14.6, t)))


class Lanterns:
    """Sleeping lanterns round the child and the helper that wake gold in a wave from the touch, and rise."""

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
        sleep = lin("#3a1c2a") * 0.5
        col = sleep[None, :] * (1.0 - lit)[:, None] + lin(COL[GRAT])[None, :] * lit[:, None]
        al = (0.25 + 0.75 * lit) * _sc(SEC[4], SEC[4] + 1.0, t)
        return dict(pos=pos, size=0.30 + 0.25 * self.s[:, 1], color=col, alpha=al, emit=1.0 + 1.5 * lit,
                    kind="soft", seed=self.s[:, 2], twinkle=0.2)


class Flares:
    """White flashes where two colours touch."""

    def __init__(self):
        from p3d.effects import Flare
        b = _bodies()
        hug = lambda t: 0.5 * (b["kind"].where(min(t, TOUCH3 + 0.3), "chest") + b["sorry"].where(min(t, TOUCH3 + 0.3), "chest"))  # noqa: E731
        self.f = [Flare(hug, TOUCH3 + 0.3, color=WHITE, color2=COL[INCL], n=900, strength=0.5, reach=0.5, life=2.0,
                        seed=4.0),
                  _REFS["hands_flare"]]

    def sample(self, t):
        out = []
        for f in self.f:
            s = f.sample(t)
            if s is None:
                continue
            out.extend(s if isinstance(s, list) else [s])
        return out or None


BADGE_BBOX = (0.132, 0.869, 0.497, 0.686)    # the badge at full size (text.render_credit), screen 0..1, y up


def _badge_box(t):
    """The badge on screen now, padded by about 40 px: nothing may cross it."""
    (cx, cy, sc, al), _ = credit_state(t, BADGE_BBOX)
    if al <= 0.01:
        return None
    x0, x1, y0, y1 = BADGE_BBOX
    hw, hh = 0.5 * (x1 - x0) * sc, 0.5 * (y1 - y0) * sc
    return (cx - hw - 0.022, cx + hw + 0.022, cy - hh - 0.037, cy + hh + 0.037)


class ScreenClear:
    """Wraps a point set: its points go dark inside the badge and inside the screen box of every word on screen."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner
        if hasattr(inner, "gain"):
            self.gain = inner.gain

    def sample(self, t, cam=None):
        ps = self.inner
        res = ps.sample(t, cam) if getattr(ps, "wants_camera", False) else ps.sample(t)
        if res is None or cam is None:
            return res
        boxes = []
        for w in WORDS:
            if w.t_in - 0.2 <= t <= w.t_out:
                b = PW.screen_box(w, cam, t)
                if b[4]:
                    boxes.append(((b[0] - 0.025, b[1] + 0.025, b[2] - 0.03, b[3] + 0.035), None))
        bb = _badge_box(t)
        if bb is not None:
            boxes.append((bb, None))
        if not boxes:
            return res
        out = []
        for b in (res if isinstance(res, (list, tuple)) else [res]):
            if b is None:
                continue
            b = dict(b)
            f = Comets._dim(np.asarray(b["pos"], np.float64).reshape(-1, 3), cam, boxes, -1)
            b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * f
            if b.get("pos2") is not None:
                b["alpha2"] = np.asarray(b.get("alpha2", 1.0), np.float64) * Comets._dim(
                    np.asarray(b["pos2"], np.float64).reshape(-1, 3), cam, boxes, -1)
            out.append(b)
        return out


def _setup(scene):
    scene.add("seed", ScreenClear(Seed()))
    scene.add("hoops", ScreenClear(PW.KeepClear(Hoops(), WORDS)))
    scene.add("lanterns", ScreenClear(PW.KeepClear(Lanterns(), WORDS)))
    b = _bodies()
    for name, body in b.items():
        if name == "listener":
            body.add(scene, name, mask=False)                      # a profile of sparks, never a dark body
        elif name == "speaker":
            body.add(scene, name, mask=dict(sky="clouds"))         # a profile filled with sunlit clouds
        else:
            body.add(scene, name)
    scene.add("flares", ScreenClear(Flares()))
    scene.add("comets", PW.KeepClear(Comets(), WORDS))
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


# ---------------------------------------------------------------------------------------------------------
# The world: night looks section by section, then the campaign day
# ---------------------------------------------------------------------------------------------------------
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
        night = 1.0 - _sc(SEC[7] - 0.05, SEC[7], t)
        calm = 1.0 - 0.6 * _sc(SEC[2] - 0.3, SEC[2] + 0.3, t) * (1.0 - _sc(SEC[3] - 0.1, SEC[3], t))
        if which == 0:
            return 0.6 * _sc(0.3, 1.2, t) * night * calm
        return (0.45 if _second_of(t) is not None else 0.0) * night * calm
    return f


LOOKS = dict(
    gate=dict(base="night", mist=0.22, mist_color="#0e2148", haze=0.25, haze_color="#0a1636", stars=0.7),
    embrace=dict(base="night", mist=0.28, mist_color="#2a1020", haze=0.3, haze_color="#1e0c1a", stars=0.5,
                 sky_top="#04020a", sky_mid="#120818", sky_hor="#2a1224"),
    floor=dict(base="night", mist=0.05, haze=0.1, stars=1.0, milky=0.8),
    drop=dict(base="night", sky_top="#05030c", sky_mid="#140a1c", sky_hor="#341426", mist=0.12,
              mist_color="#2a1020", haze=0.25, haze_color="#1e0c16", stars=0.8, milky=0.4),
    ember=dict(base="night", sky_top="#05040a", sky_mid="#1a0f0c", sky_hor="#3a2210", haze=0.5,
               haze_color="#3a2410", mist=0.35, mist_color="#2a1c10", stars=0.3, milky=0.0),
    prayer=dict(base="night", sky_top="#03020e", sky_mid="#0e0a2e", sky_hor="#1e1648", mist=0.08,
                mist_color="#1a1440", stars=1.0, milky=0.9),
    morning=dict(base="day", sun_az=180.0, sun_el=13.0, sun_int=0.9, sun_glow=0.7, mist=0.22, rays=0.25),
)

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "night"), (SEC[1], "gate", 1.2), (SEC[2], "embrace", 1.0), (SEC[3], "floor", 0.0),
          (SEC[4], "drop", 0.0), (SEC[5], "ember", 0.0), (SEC[6], "prayer", 0.0), (SEC[7], "morning", 0.0)],
    light=dict(pos=SEED, color="#fff1d8", strength=Track([(0.0, 1.1), (SEC[0], 1.1), (0.7, 0.3), (1.6, 0.0),
                                                           (TOTAL, 0.0)]), size=0.5, rays=1.0),
    lights=[dict(pos=_light_pos(0), color=_light_col(0), strength=_light_str(0), radius=2.8),
            dict(pos=_light_pos(1), color=_light_col(1), strength=_light_str(1), radius=2.4)],
    lanterns=0.0,
    arch=None,                       # the nine comets come down and are the nine lights (Comets, ARCH_AT)
    react=dict(beat=0.35, level=0.25),
)

P3D = dict(
    camera=CAMERA,
    world=dict(WORLD, shafts=[WORDS["Encouragement"].shaft(color="#c9b4ff", strength=0.9)]),
    setup=_setup,
    bursts=[
            dict(t=SEC[3], strength=1.8, rise=0.08, fall=0.28, color=COL[COMP]),
            dict(t=SEC[4], strength=1.8, rise=0.08, fall=0.28, color=COL[CONS]),
            dict(t=SEC[5], strength=1.8, rise=0.08, fall=0.28, color=COL[RESP]),
            dict(t=BREATH_END, strength=0.9, rise=0.08, fall=0.35, color="#ffd9a0"),      # the date bursts
            ],
    motion_blur=0.4,
)

# ---------------------------------------------------------------------------------------------------------
# The end card: the existing one, unchanged in style (coral title, navy date and place)
# ---------------------------------------------------------------------------------------------------------
FORM_DUR = 3.0
TITLE_FORM = 49.7                     # whole at 52.7, before the loudest moment of the medley
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=TITLE_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=51.6, t1=53.2, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
FRAGMENTS = []
TITLE_HIT = 54.4
_base.TITLE_HIT = TITLE_HIT
PHRASES = _base.PHRASES
WAVES = []

# Title and date (PHASEB UPDATE 7). The engine's TITLES (helper WORDS2) will draw these three; the times and
# places are planned here. A: the opening lockup over the first image (the seed sits low, the sky above it is
# free). B: a discreet signature only in two calm stretches between expressions. C: "December 6" written in
# light across the sky during the breath, bursting on the biggest hit (built below as a particle word).
TITLES = dict(
    opening=dict(t_end=3.6, y=0.20, palette="night"),
    signature=dict(windows=[(11.0, 13.2, "br", "night"), (38.25, 40.0, "tr", "night")]),
    date_light=dict(t_form=40.25, t_burst=BREATH_END, y=0.30, palette="night"),
)

# Until the engine's TITLES lands, the engine's credit draws A and B (title over the concert line): large and
# centred high on the first image, then small in a calm corner in each signature window. Nothing else.
CREDIT = dict(song="The Words of Mother’s Love",
              concert="Healing Concert · Sunday, December 6 · 4:30 PM · Las Vegas",
              t_in=-1.0, t_full=0.0, t_move=1e9, t_rest=1e9 + 1.0, scale=0.42, alpha_rest=0.92,
              margin_x=0.035, margin_top=0.05)


def credit_state(t, bbox):
    """Centre, scale and strength of the title lockup (bbox: its size at full card size)."""
    x0, x1, y0, y1 = bbox

    def ss(a, b, x):
        u = min(max((x - a) / (b - a), 0.0), 1.0)
        return u * u * (3 - 2 * u)

    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    op = TITLES["opening"]
    if t < op["t_end"]:
        return (0.5, 1.0 - op["y"], 0.92, 1.0 - ss(op["t_end"] - 0.6, op["t_end"], t)), (cx0, cy0)
    sc = CREDIT["scale"]
    w, h = (x1 - x0) * sc, (y1 - y0) * sc
    for a, b, corner, _pal in TITLES["signature"]["windows"]:
        if a <= t <= b:
            al = CREDIT["alpha_rest"] * ss(a, a + 0.6, t) * (1.0 - ss(b - 0.6, b, t))
            cx = CREDIT["margin_x"] + w / 2.0 if corner[1] == "l" else 1.0 - CREDIT["margin_x"] - w / 2.0
            cy = 1.0 - CREDIT["margin_top"] - h / 2.0 if corner[0] == "t" else CREDIT["margin_top"] + h / 2.0
            return (cx, cy, sc, al), (cx0, cy0)
    return (0.5, 0.5, sc, 0.0), (cx0, cy0)
