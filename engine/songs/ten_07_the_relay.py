"""Film 07 of ten: THE RELAY. One light, carried by many.
A 60 second promo for the Healing Concert "The Words of Mother's Love", on the 3D layer (engine/p3d).

LOGLINE
  A flame is carried flat out down a causeway of light across a dark lake by one ordinary person after
  another. Every time it changes hands the world changes, and a Word of Mother's Love bursts from the touch.
  The fastest runner falls and the flame is scattered into embers; a stranger kneels and gives him her hand,
  and the embers come back together, larger, in the hands of a child. She carries it to Heavenly Mother
  (only ever seen from behind, or as hands), who raises it, and the day breaks from her hands as a ring.

WHAT MAKES IT ITSELF
  Shot like a sports film: the camera runs beside the carrier at her speed, so she holds her place large in
  the frame while the world streaks past. One rule, repeated: hand-over = contact = a flash = a word = a new
  world. Gold belongs to the flame: every world before the last is cool, the road behind the flame stays lit
  gold, so the gold grows through the film until the day.

THE MUSIC (medley map, branch epic-medley2): sections 0.00 6.84 13.30 19.85 26.79 33.36 40.21 49.47, the
  opening hit 0.25, the breath 40.21 to 42.51, the biggest jump 42.51, the loudest passage 54.3, last hit 58.11.

TIMELINE
  0.00  NIGHT ROAD      frame 0 is the flame in close-up, already running; on the hit the camera whips out to
                        the sprinter in profile. GREETING bursts from the flame and rides above her.
  6.84  RAIN OF SPARKS  hand-over 1 in a flash: a man in a long coat. Sparks rain on the mirror. CONCESSION
                        hangs over the road ahead; on the hit it rushes past the lens.
  13.30 SHORE OF BIRDS  hand-over 2: a woman. The rain stops in mid air and rises as birds. GRATITUDE streams
                        out of the spent man behind her as petals and settles over the shore.
  19.85 THE SEA         hand-over 3: an old man takes it at a walk; the sea stands up in walls of spray on both
                        sides. RESPECT comes out of the stars. On the bar he breaks into a run, the spray falls.
  26.79 FIELD OF LIGHTS hand-over 4: the boy, the fastest. Thousands of held lights wake to the horizon and lift
                        in a wave that races him. ENCOURAGEMENT is written across the sky.
  33.36 THE FALL        he falls; the flame bursts into embers. APOLOGY rises cold out of the dark water. A
                        young woman kneels facing him and offers her hand: CONSIDERATION pours from her palm.
  40.21 THE BREATH      a child kneels in a shaft of light with empty cupped hands; the words become
                        INCLUSIVENESS and the embers stream into her hands.
  42.51 LANTERNS        the flame is whole, three times the size; lanterns rise; she runs. COMPLIMENT is burned
                        out of the air by the flame's own rays.
  49.47 DAY             Heavenly Mother, from behind, lowers a hand to take the flame and raises it high; rays
                        round her head. On the bar the day leaves her hands as a ring across the lake. The end
                        card is whole from 54.3 to the last frame (no fade).

HOW IT IS BUILT
  The road runs toward -z (toward the arch over the origin). Every carrier is a Body (engine/p3d/body.py) with
  real run, walk and kneel motions; where each one is at any time is worked out here by the same arithmetic
  the actor uses (`Runner`), so the camera and the words can follow them with numpy alone (the workflow's
  prepare step imports this file with numpy only; bodies are built in `_setup`). The flame, the embers, the
  road of light, the rain and birds, the sea spray, the field of lights and the ring of day are this film's
  own point sets (below). The nine expressions come from engine/p3d/words.py by name.
"""
import numpy as np

import songs.epic_concert as _base
from track import Track

# =====================================================================================================
# THE MUSIC
# =====================================================================================================
S = [0.00, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47]
HIT = dict(open=0.25, tape1=10.44, birds=14.14, swoop=18.20, snap=24.45, wave1=27.97, dive=31.62, grip=37.42,
           up=39.12, jump=42.51, tape9=45.64, release=52.26, peak=54.30, final=58.11)
T0 = HIT["open"]
T1, T2, T3, T4, T5 = S[1], S[2], S[3], S[4], S[5]
BREATH, T6, T7 = S[6], HIT["jump"], S[7]
REL = HIT["release"]
TITLE_AT = HIT["peak"]                 # the title is whole on the loudest passage

# ---- the end card (the existing style of the epic promo): set on the base before its names are copied
_base.TITLE_HIT = TITLE_AT
_base.TITLE = dict(_base.TITLE, form=TITLE_AT - 3.75)
_base.TAGLINE = dict(_base.TAGLINE, t0=53.05, t1=TITLE_AT - 0.05)
_base.FADE = Track([(0.0, 1.0), (60.0, 1.0)])           # never black: not at the start, not at the end
_base.EXPOSURE = Track([(0.0, 1.0), (60.0, 1.0)])
for _p in _base.PHRASES:                                 # the flat 2D expressions are off: the words are 3D
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.FRAGMENTS = []
_base.WAVES = []
_base.NOTE_RINGS = Track([(0.0, 0.0), (60.0, 0.0)])
_base.DOVES = Track([(0.0, 0.0), (60.0, 0.0)])
_base.MOTES = Track([(0.0, 0.0), (60.0, 0.0)])
_base.BUBBLES = Track([(0.0, 0.0), (REL + 0.4, 0.0), (TITLE_AT, 0.16), (60.0, 0.16)])
_base.LEAVES = Track([(0.0, 0.0), (REL + 0.8, 0.0), (TITLE_AT + 0.5, 0.14), (60.0, 0.14)])
from songs.epic_concert import *  # noqa: E402,F401,F403

# the 2D layers of the epic promo that this film does not use
FIGURES = []
GATHERING = None
PASS_LIGHT = None
SYMBOLS = []
FALLING_STARS = []
RIPPLES = []
RIPPLES_AUTO = None
FIGURE_LOOK = None
CAMERA_ZOOM = CAMERA_PAN = CAMERA_CRANE = None          # the 3D layer owns the camera
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
TITLE, TAGLINE, FADE, EXPOSURE = _base.TITLE, _base.TAGLINE, _base.FADE, _base.EXPOSURE
TITLE_HIT = _base.TITLE_HIT


# The concert badge (Anthony: "The concert title and the date should show from the beginning and throughout"):
# large on frame 0, settled into the top left corner by 2.8 s, gone as the end card forms.
class _Badge(dict):
    """The badge's settings. Its colour follows the sky: the engine's warm white light on the night worlds, navy
    letters with a soft white glow from the jump (42.51 s) on, when the lantern sky turns pale pink. The engine
    reads the colour with .get() each frame after credit_state(t), which sets the time."""
    now = None

    def get(self, key, default=None):
        if key in ("color", "glow"):
            if _Badge.now is None or _Badge.now >= BADGE_INK_AT:
                return {"color": "#1f2a6b", "glow": "#ffffff"}[key]
            return default
        return dict.get(self, key, default)


BADGE_INK_AT = HIT["jump"]
CREDIT = _Badge(song="The Words of Mother’s Love",
              concert="Healing Concert · Sunday, December 6 · 4:30 PM",
              t_in=-1.0, t_full=0.0, t_move=1.6, t_rest=2.8, scale=0.55, alpha_rest=0.92,
              margin_x=0.035, margin_top=0.05)
CARD_FORMS = TITLE["form"]


def credit_state(t, bbox):
    """Centre, scale and strength of the badge; bbox is its size at full size (as demo_gathering.py), fading
    out over one second from the moment the end card starts to form."""
    c = CREDIT
    _Badge.now = float(t)
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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(CARD_FORMS, CARD_FORMS + 1.0, t))
    return (cx, cy, scale, alpha), (cx0, cy0)


def params(song, t):
    """The base film's params, with the arch functions this song was given by engine/song.py."""
    g = globals()
    if "star_state" in g:
        _base.star_state, _base.link_state = g["star_state"], g["link_state"]
    return _base.params(song, t)


# =====================================================================================================
# THE CARRIERS: where each one is at any time (the same arithmetic as engine/p3d/actor.py's travel)
# =====================================================================================================
GRID = 1.0 / 60.0


def _smoother(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6.0 * x - 15.0) + 10.0)


class Runner:
    """A person on the road: lane x, start z, facing -z, motion keys [(t, name, dict(speed, blend, ...))]."""

    def __init__(self, name, shape, height, x, keys, show, facing=180.0, **body):
        self.name, self.shape, self.height, self.x = name, shape, height, float(x)
        self.keys = sorted([(float(k[0]), k[1], dict(k[2]) if len(k) > 2 else {}) for k in keys],
                           key=lambda k: k[0])
        self.show = (float(show[0]), float(show[1]))
        self.facing = facing
        self.body = body
        self.z0 = 0.0
        t_ref = self.show[0]
        tt = t_ref + np.arange(int((61.0 - t_ref) / GRID) + 3) * GRID
        n = len(self.keys)
        u = np.ones((n, len(tt)))
        for i in range(1, n):
            ts, _, p = self.keys[i]
            u[i] = _smoother((tt - ts) / max(p.get("blend", 0.9), 1e-3))
        w = np.zeros_like(u)
        rest = np.ones(len(tt))
        for i in range(n - 1, -1, -1):
            w[i] = rest * u[i]
            rest = rest * (1.0 - u[i])
        sp = np.array([k[2].get("speed", 0.0) if k[1] in ("walk", "run") else 0.0 for k in self.keys])
        speed = (w * sp[:, None]).sum(0)
        dist = np.concatenate([[0.0], np.cumsum(0.5 * (speed[1:] + speed[:-1]) * GRID)])
        self.tt, self.dist, self.speed = tt, dist, speed

    def d(self, t):
        return float(np.interp(t, self.tt, self.dist))

    def v(self, t):
        return float(np.interp(t, self.tt, self.speed))

    def root(self, t):
        if self.facing == 0.0:
            return np.array([self.x, 0.0, self.z0 + self.d(t)])
        return np.array([self.x, 0.0, self.z0 - self.d(t)])


V = dict(sprinter=6.2, coat=5.6, shawl=5.6, elder_walk=1.4, elder=4.6, youth=7.2, child=4.0, child_walk=1.2)
SNAP = HIT["snap"]
CHILD_WALK = T7 - 1.45
R = {}
R["sprinter"] = Runner("sprinter", "woman", 1.66, 0.0,
                       [(0.0, "run", dict(speed=V["sprinter"])), (T1 + 0.45, "stand", dict(blend=1.6))],
                       (0.0, T1 + 2.6))
R["coat"] = Runner("coat", "man", 1.80, 0.55,
                   [(T1 - 3.0, "stand"), (T1 - 1.15, "run", dict(speed=V["coat"], blend=0.9)),
                    (T2 + 0.45, "stand", dict(blend=1.6))], (T1 - 3.0, T2 + 2.8))
R["shawl"] = Runner("shawl", "woman", 1.64, 0.0,
                    [(T2 - 3.0, "stand"), (T2 - 1.15, "run", dict(speed=V["shawl"], blend=0.9)),
                     (T3 - 0.9, "stand", dict(blend=1.6))], (T2 - 3.0, SNAP + 0.6))
R["elder"] = Runner("elder", "man", 1.70, 0.55,
                    [(T3 - 3.0, "stand"), (T3 - 0.6, "walk", dict(speed=V["elder_walk"], blend=0.8)),
                     (SNAP, "run", dict(speed=V["elder"], blend=0.8)), (T4 + 0.45, "stand", dict(blend=1.6))],
                    (T3 - 3.0, T4 + 2.6))
R["youth"] = Runner("youth", "man", 1.76, 0.0,
                    [(T4 - 3.0, "stand"), (T4 - 1.2, "run", dict(speed=V["youth"], blend=0.9)),
                     (T5 - 0.05, "kneel", dict(blend=0.5)), (HIT["up"], "stand", dict(blend=1.0))],
                    (T4 - 3.0, T6 + 1.0))
R["child"] = Runner("child", "child", 1.15, 0.22,
                    [(BREATH - 2.2, "kneel"), (T6, "stand", dict(blend=0.35)),
                     (T6 + 0.3, "run", dict(speed=V["child"], blend=0.8)),
                     (CHILD_WALK, "walk", dict(speed=V["child_walk"], blend=0.7)),
                     (T7 - 0.1, "stand", dict(blend=0.6))], (BREATH - 2.2, 60.0))
ORDER = ["sprinter", "coat", "shawl", "elder", "youth"]
HANDS = [T1, T2, T3, T4]          # when the flame passes from ORDER[i] to ORDER[i + 1]
GAP = 0.7                         # the taker is this far ahead at the touch

# place everyone: each taker a step ahead of the giver at the touch; then the child and Heavenly Mother
for _i, _T in enumerate(HANDS):
    _a, _b = R[ORDER[_i]], R[ORDER[_i + 1]]
    _b.z0 = _a.root(_T)[2] - GAP + _b.d(_T)
Z_FALL = R["youth"].root(T5 + 1.5)[2]                   # where the boy comes to rest
R["child"].z0 = Z_FALL - 2.3 + R["child"].d(BREATH)      # the child kneels just beyond the two of them
_zc_end = R["child"].root(60.0)[2]
MOTHER_Z = 14.0
_shift = MOTHER_Z - 0.12 - _zc_end                       # Heavenly Mother stands 14 m in front of the arch
for _r in R.values():
    _r.z0 += _shift
Z_FALL += _shift
Z_CHILD = R["child"].root(BREATH)[2]
MOTHER_POS = np.array([R["child"].x + 0.62, 0.0, MOTHER_Z])     # the child ends at her left side
HELPER_POS = np.array([0.15, 0.0, Z_FALL - 1.15])       # she kneels facing him (facing +z)
GRIP = np.array([0.30, 0.74, Z_FALL - 0.58])             # where their hands meet
Z_START = R["sprinter"].z0


def root(who, t):
    if who == "mother":
        return MOTHER_POS.copy()
    if who == "helper":
        return HELPER_POS.copy()
    return R[who].root(t)


HOLDERS = [(-1.0, "sprinter"), (T1, "coat"), (T2, "shawl"), (T3, "elder"), (T4, "youth"), (T5, None),
           (T6, "child"), (T7, "mother")]


def holder(t):
    k = max(i for i, (t0, _) in enumerate(HOLDERS) if t >= t0)
    return HOLDERS[k][1], k


def flame_guess(t):
    """Where the flame is at t, worked out without the bodies (held up in the right hand)."""
    who, k = holder(t)
    if who is None:
        return np.array([0.1, 0.05, Z_FALL - 1.6])
    if who == "mother":
        return MOTHER_POS + np.array([0.0, 2.15, -0.15])
    r = R[who]
    p = r.root(t) + np.array([0.20 * r.height / 1.7, r.height + 0.34 * r.height / 1.7, -0.08])
    if who == "child" and t < T6 + 0.4:
        p = r.root(t) + np.array([0.0, 0.55, -0.25])
    return p


# =====================================================================================================
# THE BODIES (built in _setup: they need scipy and the assets) and the flame's real place
# =====================================================================================================
BODIES = {}


def _palm_up(name, t, side="R", up=0.11):
    b = BODIES[name]
    return np.asarray(b.where(t, "palm." + side), np.float64) + np.array([0.0, up, 0.0])


def _held(name, t):
    if name not in BODIES:
        return flame_guess(t) if name != "child" else root("child", t) + np.array([0.0, 0.6, -0.2])
    if name == "child" and t < T6 + 0.25:
        b = BODIES["child"]
        return 0.5 * (np.asarray(b.where(t, "palm.L")) + np.asarray(b.where(t, "palm.R"))) + [0.0, 0.10, 0.0]
    if name == "mother":
        b = BODIES["mother"]
        r = _palm_up("mother", t, "L", 0.10)
        both = 0.5 * (np.asarray(b.where(t, "palm.L")) + np.asarray(b.where(t, "palm.R"))) + [0.0, 0.16, 0.0]
        u = float(_smoother((t - (T7 + 0.5)) / 0.9))
        return r * (1.0 - u) + both * u
    return _palm_up(name, t)


def flame_pos(t):
    """Where the flame is at t: in the holder's hand (crossing over in 0.14 s at a hand-over)."""
    who, k = holder(t)
    if who is None:
        return EMBER_HOME.copy()
    p = _held(who, t)
    t0 = HOLDERS[k][0]
    prev = HOLDERS[k - 1][1] if k > 0 else None
    if prev is not None and t - t0 < 0.14:
        u = float(_smoother((t - t0) / 0.14))
        p = _held(prev, t) * (1.0 - u) + p * u
    return p


EMBER_HOME = np.array([0.1, 0.05, Z_FALL - 1.6])
FLAME_SIZE = Track([(0.0, 0.17), (T1, 0.19), (T2, 0.21), (T3, 0.23), (T4, 0.26), (T5 - 0.1, 0.28), (T5 + 0.25, 0.0),
                    (T6 - 0.12, 0.0), (T6 + 0.35, 0.27), (T7, 0.28), (REL, 0.34), (60.0, 0.34)], name="FLAME_SIZE")


# =====================================================================================================
# THE CAMERA: moves that follow someone (or the flame), blended by the rig
# =====================================================================================================
from p3d.camera import Move, Rig  # noqa: E402


class follow(Move):
    """Ride with `who` (a carrier, "flame", "mother", "helper" or "world"): pos and look are offsets in metres
    (x right of the road, y up, z back along the road), or pairs (start, end) eased over the move."""

    def __init__(self, who, pos, look, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.who, self.p, self.l = who, pos, look

    def _off(self, v, t):
        if isinstance(v[0], (tuple, list)):
            if self.pace is not None:
                u = float(np.clip(self.pace(t), 0.0, 1.0))
            else:
                u = float(_smoother((t - self.t0) / (self.t1 - self.t0)))
            return np.asarray(v[0], np.float64) * (1.0 - u) + np.asarray(v[1], np.float64) * u
        return np.asarray(v, np.float64)

    def pose(self, t):
        if self.who == "world":
            base = np.zeros(3)
        elif self.who == "flame":
            base = flame_pos(t)
        else:
            base = root(self.who, t)
        return base + self._off(self.p, t), base + self._off(self.l, t)


F = "flame"
MOVES = [
    # ---- night road
    follow(F, (1.45, 0.10, 0.85), (0.0, 0.36, -0.2), 0.0, 0.32, fov=40, aperture=0.03, near=0.02),
    follow("sprinter", (4.6, 1.25, 0.4), (0.0, 1.35, -0.8), 0.32, 5.75, fov=42, blend=0.45),
    follow("sprinter", (1.0, 2.1, 4.2), (0.0, 1.5, -14.0), 5.75, 6.45, fov=46, blend=0.7, focus=4.7),
    # ---- rain of sparks
    follow(F, (2.4, -0.25, 0.55), (0.2, -0.45, -0.3), 6.55, 7.1, fov=42, aperture=0.015, blend=0.5),
    follow("coat", (1.7, 1.75, 3.5), (0.0, 2.2, -10.0), 7.15, 10.2, fov=48, blend=0.5, focus=3.9),
    follow("coat", (2.7, 1.3, 0.5), (0.0, 1.35, -0.4), 10.45, 12.5, fov=40, aperture=0.02, blend=0.4),
    follow("coat", (1.8, 1.7, 3.2), (0.0, 1.4, -10.0), 12.5, 12.95, fov=44, blend=0.9, focus=3.7),
    # ---- shore of birds
    follow(F, (2.4, -0.25, 0.55), (0.2, -0.45, -0.3), 13.05, 13.55, fov=42, aperture=0.015, blend=0.4),
    follow("shawl", ((4.0, 0.7, 1.4), (5.3, 2.4, 0.8)), (0.0, 1.8, -1.4), 13.6, 18.1, fov=46, blend=0.5),
    follow("shawl", ((3.4, 0.6, 1.0), (2.8, 1.2, 0.6)), (0.0, 1.35, -1.0), 18.25, 19.55, fov=44, aperture=0.015,
           blend=0.5),
    # ---- the sea
    follow(F, (2.4, -0.25, 0.55), (0.2, -0.45, -0.3), 19.65, 20.05, fov=42, aperture=0.015, blend=0.4),
    follow("elder", (4.4, 0.8, 0.5), (0.0, 1.6, -0.5), 20.1, 24.4, fov=46, blend=0.45),
    follow("elder", ((2.9, 0.75, 1.6), (2.4, 1.1, 0.4)), (0.0, 1.35, -2.0), 24.5, 25.6, fov=48, aperture=0.015,
           blend=0.45),
    follow("elder", (-1.0, 2.4, 4.0), (0.0, 1.5, -14.0), 25.6, 26.45, fov=46, blend=1.0, focus=4.3),
    # ---- field of lights
    follow(F, (2.4, -0.25, 0.55), (0.2, -0.45, -0.3), 26.55, 26.95, fov=42, aperture=0.015, blend=0.4),
    follow("youth", (2.0, 2.2, 3.0), (-4.0, 5.0, -45.0), 27.0, 28.3, fov=52, blend=0.45, focus=3.9),
    follow("youth", (8.0, 7.0, 9.0), (-8.0, 6.0, -40.0), 28.3, 31.6, fov=52, blend=1.2),
    follow("youth", (1.6, 0.9, 2.8), (0.0, 1.0, -6.0), 31.7, 33.3, fov=54, aperture=0.012, blend=0.5, focus=3.1),
    # ---- the fall
    follow("youth", (3.0, 0.55, 0.0), (-0.2, 0.95, -0.55), 33.6, 36.4, fov=40, aperture=0.03, blend=0.45),
    follow("youth", (2.5, 0.75, -0.4), (0.0, 1.0, -0.6), 36.4, 39.3, fov=36, aperture=0.03, blend=1.5),
    # ---- the breath
    follow("child", ((3.3, 1.3, 0.8), (2.4, 1.0, 0.3)), (0.0, 0.95, 0.0), 39.8, 42.75, fov=38, aperture=0.03,
           blend=0.7),
    # ---- lanterns
    follow("child", (0.6, 0.8, 2.3), (0.0, 2.0, -10.0), 42.75, 43.05, fov=52, blend=0.4, focus=2.5),
    follow("child", (2.7, 1.15, 2.4), (-0.6, 2.0, -6.0), 43.0, 45.7, fov=50, blend=0.6, focus=3.6),
    follow("child", (3.0, 1.0, 0.6), (0.0, 0.95, -1.5), 45.75, 47.8, fov=42, blend=0.45),
    follow("child", (0.9, 1.3, 3.0), (0.0, 1.5, -12.0), 47.8, 48.9, fov=44, blend=1.0, focus=3.2),
    # ---- day: the hands (from behind and above), Heavenly Mother raises the light, the ring of day
    follow(F, (0.0, 0.42, 1.0), (0.0, -0.10, -0.25), 48.95, 50.1, fov=42, aperture=0.02, blend=0.6),
    follow("mother", (0.15, 1.25, 2.7), (0.0, 2.05, -4.0), 50.15, REL, fov=46, blend=0.8),
    follow("mother", ((0.2, 1.6, 3.6), (6.0, 20.0, 75.0)), ((0.0, 2.2, -6.0), (0.3, 4.0, -25.0)), REL + 0.05,
           TITLE_AT, fov=48, blend=0.5, pace=[(REL + 0.05, 0.0), (REL + 0.6, 0.08), (REL + 1.6, 0.55),
                                               (TITLE_AT, 1.0)]),
    follow("mother", ((6.0, 20.0, 75.0), (6.6, 20.2, 76.5)), ((0.3, 4.0, -25.0), (0.3, 4.1, -25.0)), TITLE_AT, 60.0,
           fov=46, blend=0.8),
]
CAMERA = Rig(MOVES, blend=1.2, fov=44, aperture=0.025, handheld=0.25, shutter=0.35, min_height=0.3)


# =====================================================================================================
# THE NINE EXPRESSIONS (engine/p3d/words.py by name; laid out by where they are read in the picture)
# =====================================================================================================
from p3d import words as PW  # noqa: E402
from p3d.world import arch_points  # noqa: E402

ARCH = arch_points()


def _word(who, x, y, depth, px, t_in, t_read0, t_read1, t_out, **kw):
    """A word laid out at the middle of its reading moment at picture place (x, y), `depth` metres ahead, with
    an em of `px` pixels; it then travels with `who` (None: it stays where it is)."""
    tm = 0.5 * (t_read0 + t_read1)
    p = np.asarray(PW.place(CAMERA, tm, x, y, depth), np.float64)
    em = PW.em_for(CAMERA, tm, depth, px)
    if who is None:
        pos = tuple(p)
    else:
        r0 = root(who, tm)
        pos = (lambda p, r0, who: (lambda t: p + root(who, t) - r0))(p, r0, who)
    return dict(pos=pos, em=em, t_in=t_in, t_read0=t_read0, t_read1=t_read1, t_out=t_out, **kw)


def _flame_at(tt):
    return lambda t: flame_pos(tt)


def _src(name, place, fallback):
    def f(t):
        if name in BODIES:
            return np.asarray(BODIES[name].where(t, place), np.float64)
        return np.asarray(fallback, np.float64)
    return f


_SPECS = [
    dict(expr="Greeting", arrive="touch", source=_flame_at(1.7), leave="wind", wind=(0.0, 0.15, 1.0),
         **_word("sprinter", 0.60, 0.80, 9.0, 100, 1.7, 2.85, 5.35, 6.2)),
    dict(expr="Concession", arrive="touch", source=_flame_at(T1), leave="bokeh",
         **_word("coat", 0.60, 0.80, 13.5, 96, T1, 7.4, 9.95, 10.8)),
    dict(expr="Gratitude", arrive="petals", source=lambda t: root("coat", t) + np.array([0.0, 1.4, 0.0]),
         leave="flock", **_word("shawl", 0.60, 0.72, 10.5, 84, 12.9, 14.3, 17.9, 18.8)),
    dict(expr="Respect", arrive="stars", leave="sink",
         **_word("elder", 0.60, 0.78, 9.0, 94, 18.9, 20.6, 23.9, 24.8)),
    dict(expr="Encouragement", arrive="touch", source=_flame_at(T4), leave="arch", to=tuple(ARCH[6]), reflect=False,
         **_word("youth", 0.60, 0.78, 55.0, 90, T4, 29.0, 31.6, 32.5)),
    dict(expr="Apology", arrive="lake", leave="stars", color="#e6ecff", glow="#9fb4ff",
         **_word(None, 0.60, 0.74, 4.6, 80, T5, 33.95, 36.45, 37.1)),
    dict(expr="Consideration", arrive="palm", source=_src("helper", "palm.L", GRIP), leave="morph",
         **_word(None, 0.60, 0.79, 4.4, 84, 36.15, 36.95, 39.45, 39.45)),
    dict(expr="Inclusiveness", arrive="morph", source="Consideration", leave="stream",
         to=lambda t: flame_pos(t) if t > T6 else root("child", t) + np.array([0.0, 0.62, -0.2]),
         **_word(None, 0.60, 0.80, 4.0, 96, 39.45, 40.05, 42.55, 43.1)),
    dict(expr="Compliment", arrive="rays", source=lambda t: flame_pos(t), leave="arch", to=tuple(ARCH[8]),
         **_word("child", 0.60, 0.78, 10.5, 94, T6, 43.05, 45.64, 46.4)),
]
WORDS = PW.Words(_SPECS, camera=CAMERA, face="camera", reflect=False)    # no upside-down words in the lake
ARCH_LIT = [w["t_out"] for w in sorted(_SPECS, key=lambda s: [e["label"] for e in PW.EXPRESSIONS].index(s["expr"]))]


# =====================================================================================================
# THIS FILM'S OWN POINT SETS
# =====================================================================================================
from p3d import lin  # noqa: E402

GOLD, CORE, EMBER = lin("#ffc24a"), lin("#fff4dc"), lin("#ff7a2a")


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


class Flame:
    """The flame: a flickering teardrop of light with a glow, sparks streaming back from it as it runs; after
    the fall a scatter of embers that cool, are lifted, and stream into the child's hands."""

    wants_camera = True

    def __init__(self, n=1400, n_sp=1600, n_emb=520, sparks=False):
        self.sparks = sparks
        rng = np.random.default_rng(7)
        self.c = rng.random((n, 5))
        self.s = rng.random((n_sp, 6))
        self.e = rng.random((n_emb, 6))
        ang = self.e[:, 0] * 6.2832
        rad = 0.25 + 2.6 * self.e[:, 1] ** 0.7
        self.rest = EMBER_HOME + np.stack([rad * np.cos(ang) * 0.8, np.zeros_like(rad), rad * np.sin(ang) * 1.4], 1)
        self.rest[:, 0] = np.minimum(self.rest[:, 0], 0.6 - 0.4 * self.e[:, 5])     # none at the lens side
        self.rest[:, 1] = 0.03

    def sample(self, t, cam=None):
        out = []
        h = float(FLAME_SIZE(t))
        if h > 0.004:
            p = flame_pos(t)
            near = 1.0 if cam is None else float(_ss(0.5, 2.6, np.linalg.norm(np.asarray(cam.pos) - p)))
            vel = (flame_guess(t) - flame_guess(t - 0.05)) / 0.05
            sp = float(np.linalg.norm(vel))
            back = -vel / sp if sp > 0.2 else np.array([0.0, 0.0, 0.0])
            c = self.c
            u = c[:, 0] ** 0.8                                          # height along the flame
            rmax = 0.30 * h * np.sqrt(u + 0.02) * (1.0 - u) ** 0.6 * 1.9
            ang = c[:, 1] * 6.2832 + t * 3.0
            rr = rmax * np.sqrt(c[:, 2])
            fl = np.sin(t * 11.0 + c[:, 3] * 6.0 + u * 5.0) * 0.07 * h * u
            lean = (0.10 + 0.05 * min(sp, 8.0)) * h * u * u
            pos = p + np.stack([rr * np.cos(ang) + fl, u * h * (1.0 + 0.12 * np.sin(t * 7.0 + c[:, 4] * 9.0)),
                                rr * np.sin(ang)], 1) + back[None] * lean[:, None]
            hot = np.clip(1.0 - rr / (0.5 * h + 1e-6) - u * 0.6, 0.0, 1.0)[:, None]
            keep = (0.2 / max(h, 0.2)) ** 1.6              # a bigger flame is not a brighter one
            col = CORE * hot + (GOLD * (1.0 - u[:, None]) + EMBER * u[:, None]) * (1.0 - hot)
            out.append(dict(pos=pos, size=0.03 * h + 0.003, color=col, alpha=0.38 * keep * (0.35 + 0.65 * near),
                            emit=1.1 + 1.5 * hot[:, 0],
                            kind="soft"))
            out.append(dict(pos=np.array([p + [0.0, 0.35 * h, 0.0]] * 3), size=np.array([0.6, 1.3, 2.8]) * h,
                            color=GOLD, alpha=np.array([0.22, 0.08, 0.03]) * keep * (0.15 + 0.85 * near),
                            kind="soft", dof=1.0))
            s = self.s
            life = 0.35 + 0.45 * s[:, 0]
            age = np.mod(t * (0.9 + 0.3 * s[:, 1]) + s[:, 2] * 7.0, life)
            k = age / life
            sp_pos = (p + np.stack([(s[:, 3] - 0.5) * 0.25 * h, np.full(len(s), 0.4 * h), (s[:, 5] - 0.5) * 0.25 * h], 1)
                      - vel[None] * age[:, None] + np.stack([np.sin(s[:, 4] * 30 + t * 3) * 0.3,
                                                             0.9 + 0.8 * s[:, 4],
                                                             np.cos(s[:, 5] * 30 + t * 2) * 0.3], 1) * age[:, None])
            col = GOLD * (1.0 - k[:, None]) + EMBER * k[:, None]
            if self.sparks:
                out.append(dict(pos=sp_pos, size=0.010 + 0.012 * s[:, 1] * (1.0 - k), color=col,
                                alpha=(1.0 - k) ** 1.5 * min(1.0, h / 0.15), emit=1.4, kind="spark"))
        if self.sparks and T5 - 0.05 <= t < T6 + 0.5:
            out.append(self._embers(t))
        if self.sparks:
            out = out[2:] if len(out) > 2 and h > 0.004 else [b for b in out if b.get("kind") == "spark"]
        else:
            out = out[:2] if h > 0.004 else []
        return out

    def _embers(self, t):
        e = self.e
        p0 = flame_guess(T5 - 0.05)
        fly = _ss(T5, T5 + 0.9 + 0.5 * e[:, 2], t)[:, None]
        hop = np.abs(np.sin(fly[:, 0] * np.pi * (1.0 + 2.0 * e[:, 3]))) * (1.0 - fly[:, 0]) * 0.6
        pos = p0 * (1.0 - fly) + self.rest * fly
        pos[:, 1] += hop
        # lifted in open hands (a share of them), then streamed into the child's cupped hands
        lift = _ss(36.4 + 1.2 * e[:, 4], 37.6 + 1.2 * e[:, 4], t) * (e[:, 5] < 0.65)
        pos[:, 1] += lift * (0.55 + 0.45 * e[:, 2])
        go = _ss(39.4 + 1.9 * e[:, 4], 41.6 + 0.85 * e[:, 4], t)[:, None]
        tgt = root("child", t) + np.array([0.0, 0.62, -0.22])
        mid = 0.5 * (pos + tgt) + np.array([0.0, 1.2, 0.0])
        q = go
        pos = (1 - q) ** 2 * pos + 2 * (1 - q) * q * mid + q * q * tgt
        cool = _ss(T5 + 0.5, T5 + 2.8, t)
        warm = np.maximum(lift, go[:, 0])
        bright = (1.0 - 0.8 * cool) + warm * 0.9
        col = GOLD[None] * (1.0 - cool + warm * cool)[:, None] + EMBER[None] * (cool * (1.0 - warm))[:, None]
        a = np.clip(bright, 0.0, 1.6) * (1.0 - _ss(T6 + 0.05, T6 + 0.45, t))
        return dict(pos=pos, size=0.006 + 0.010 * e[:, 1], color=col, alpha=np.clip(0.55 * a, 0.0, 1.0),
                    emit=0.9 + 0.8 * warm, kind="spark")


def _flame_z_table():
    tt = np.arange(0.0, 60.0, 1.0 / 30.0)
    z = np.array([flame_guess(x)[2] for x in tt])
    return tt, np.minimum.accumulate(z)


class Road:
    """The causeway: gold dust laid on the water behind the flame, lit the moment the flame passes."""
    static = True

    def __init__(self, n=60000):
        rng = np.random.default_rng(11)
        tt, fz = _flame_z_table()
        z = Z_START + 2.0 - rng.random(n) * (Z_START + 2.0 - (MOTHER_Z + 0.5))
        x = 0.28 + rng.normal(size=n) * 0.42 * (1.0 + 0.6 * rng.random(n))
        born = np.interp(-z, -fz, tt)                 # fz falls with t: interp on its negative
        born = np.where(z > fz[0], 0.0, born)
        self.batch = dict(pos=np.stack([x, 0.012 + 0.03 * rng.random(n), z], 1), size=0.012 + 0.02 * rng.random(n),
                          color=GOLD * (0.6 + 0.6 * rng.random((n, 1))), alpha=0.5, emit=1.0, kind="soft",
                          birth=born + 0.05 * rng.random(n), fade=0.5, flash=2.5)

    def sample(self, t):
        return self.batch


class Posts:
    """Small lamps on posts along the far side of the causeway, every 5 m: at running speed they stream past
    behind the carrier, which is what makes the speed felt."""
    static = True

    def __init__(self):
        z = np.arange(MOTHER_Z + 6.0, Z_START + 10.0, 5.0)
        n = len(z)
        x = np.full(n, -2.3)
        top = np.stack([x, np.full(n, 0.95), z], 1)
        foot = np.stack([x, np.full(n, 0.05), z], 1)
        self.batch = dict(pos=top, size=0.09, color=lin("#d6e4ff"), alpha=0.45, emit=1.5, kind="soft")

    def sample(self, t):
        return self.batch


class Rain:
    """Sparks raining on the mirror around the runner; at the touch on the shore they stop in mid air, and on
    the hit they rise and fly ahead as birds."""

    wants_camera = True

    def __init__(self, n=3200):
        self.r = np.random.default_rng(21).random((n, 6))

    def sample(self, t, cam=None):
        if not (T1 - 0.3 < t < 19.6):
            return None
        r = self.r
        c = flame_guess(t)
        x = (r[:, 0] - 0.5) * 22.0
        zr = np.mod(r[:, 1] * 36.0 - (c[2] - Z_START), 36.0) - 26.0
        tf = min(t, T2)
        y = np.mod(r[:, 2] * 13.0 - 9.0 * tf * (0.8 + 0.4 * r[:, 3]), 13.0)
        edge = np.clip((26.0 + zr) / 4.0, 0, 1) * np.clip((10.0 - zr) / 4.0, 0, 1)
        a = edge * _ss(T1 - 0.3, T1 + 0.1, t)
        pos = np.stack([x, y, c[2] + zr], 1)
        if cam is not None:                     # no drop right at the lens: they were great bright bars
            a = a * _ss(1.6, 4.0, np.linalg.norm(pos - np.asarray(cam.pos)[None], axis=1))
        if t < HIT["birds"]:
            hang = _ss(T2 - 0.1, T2 + 0.25, t)
            streak = 0.06 + 0.25 * (1.0 - hang)
            return dict(pos=pos, pos2=pos + np.array([0.08, streak * 1.2, 0.0]),
                        size=0.0035, color=lin("#ffe9c0"), alpha=a * 0.6, emit=1.3, kind="line")
        k = t - HIT["birds"]
        fly = np.stack([0.4 * np.sin(r[:, 4] * 9 + k), 2.2 + 1.2 * r[:, 4], -(4.0 + 4.0 * r[:, 5])], 1) * k
        bp = pos + fly
        bp[:, 2] = c[2] + zr + fly[:, 2] * 0.0 - k * (4.0 + 4.0 * r[:, 5])
        rot = np.stack([0.3 * np.sin(r[:, 4] * 7), np.mod(k * 9.0 + r[:, 5] * 6.28, 6.2832)], 1)
        sel = r[:, 3] < 0.35
        return dict(pos=bp[sel], size=0.16 + 0.12 * r[sel, 4], color=lin("#eef2ff"),
                    alpha=(a * (1.0 - _ss(18.0, 19.5, t)))[sel], kind="bird", rot=rot[sel], emit=1.3)


class Spray:
    """The sea stands up in walls of spray on both sides of the road and hangs; on the bar it falls."""

    def __init__(self, n=9000):
        r = np.random.default_rng(31).random((n, 5))
        za, zb = R["elder"].root(T3 - 1.0)[2] + 10.0, R["elder"].root(T4)[2] - 14.0
        side = np.where(r[:, 0] < 0.5, -1.0, 1.0)
        ax = 2.6 + 9.0 * r[:, 1] ** 1.3
        x = side * ax + 0.3
        crest = 3.6 * np.exp(-((ax - 4.8) / 2.6) ** 2) + 0.4
        self.base = np.stack([x, crest * r[:, 2] ** 0.7, za + (zb - za) * r[:, 3]], 1)
        self.r = r

    def sample(self, t):
        if not (T3 - 0.2 < t < T4 + 0.5):
            return None
        r = self.r
        up = _ss(T3 - 0.15, T3 + 0.6, t)
        pos = self.base.copy()
        pos[:, 1] = pos[:, 1] * up + 0.08 * (t - T3) * r[:, 4]
        fall = max(t - SNAP, 0.0)
        pos[:, 1] -= 4.9 * fall * fall * (0.7 + 0.6 * r[:, 4])
        a = np.clip(pos[:, 1] / 0.3, 0.0, 1.0) * (0.35 + 0.65 * r[:, 2])
        return dict(pos=pos, size=0.02 + 0.06 * r[:, 4] ** 3, color=lin("#e8fff8"), alpha=a * 0.7, emit=1.2,
                    kind="soft")


class Field:
    """Thousands of held lights on both sides of the road. They wake in a front that runs away to the horizon,
    lift overhead and turn gold where the flame is, and sink and cool when he falls."""

    def __init__(self, n=14000):
        r = np.random.default_rng(41).random((n, 5))
        za, zb = R["youth"].root(T4)[2] + 6.0, Z_FALL - 90.0
        side = np.where(r[:, 0] < 0.5, -1.0, 1.0)
        x = side * (3.0 + 85.0 * r[:, 1] ** 1.6) + 0.3
        self.base = np.stack([x, 1.0 + 0.35 * r[:, 2], za + (zb - za) * r[:, 3]], 1)
        self.r = r
        self.wake = T4 + 0.25 + (np.abs(x) + np.abs(self.base[:, 2] - za) * 0.4) / 160.0

    def sample(self, t):
        if not (T4 - 0.2 < t < BREATH + 0.5):
            return None
        r = self.r
        on = _ss(self.wake, self.wake + 0.35, t)
        fz = flame_guess(min(t, T5))[2]
        dz = self.base[:, 2] - fz
        wave = np.exp(-((dz + 7.0) / 11.0) ** 2) * np.exp(-np.abs(self.base[:, 0]) / 40.0) * (1.0 - _ss(T5, T5 + 1.0, t))
        dark = _ss(T5, T5 + 1.6, t)
        pos = self.base.copy()
        pos[:, 1] += 0.75 * wave - 0.4 * dark
        col = lin("#bcd0ff")[None] * (1.0 - wave[:, None]) + lin("#ffd27a")[None] * wave[:, None]
        a = on * (0.55 + 0.45 * r[:, 4]) * (1.0 - 0.85 * dark) * (1.0 - _ss(BREATH - 0.5, BREATH + 0.4, t))
        return dict(pos=pos, size=0.06 + 0.05 * r[:, 4] + 0.05 * wave, color=col, alpha=np.clip(a, 0, 1),
                    emit=1.0 + 1.5 * wave, kind="soft")


class DayRing:
    """The day leaves Heavenly Mother's hands as a ring of light that runs out across the lake: a bright band
    on the water with a low wall of sparks on its front, slow enough to be seen passing under the camera."""

    wants_camera = True

    def __init__(self, n=14000):
        self.r = np.random.default_rng(51).random((n, 4))

    def sample(self, t, cam=None):
        k = t - REL
        if not (-0.02 <= k < 4.2):
            return None
        r = self.r
        rad = 0.6 + 38.0 * k ** 1.45 + (r[:, 2] - 0.5) * (0.4 + 0.08 * k * k)
        ang = r[:, 0] * 6.2832
        c = MOTHER_POS
        wall = (2.2 + 0.4 * k) * r[:, 1] ** 3
        pos = np.stack([c[0] + rad * np.cos(ang), 0.04 + wall, c[2] + rad * np.sin(ang)], 1)
        a = (1.0 - k / 4.2) ** 1.3 * (0.55 + 0.45 * r[:, 3]) * _ss(-0.02, 0.15, k) * (0.25 + 0.75 * _ss(3.0, 14.0, rad))
        if cam is not None:                 # where it passes the lens it is a soft veil, never a white wall
            a = a * (0.08 + 0.92 * _ss(2.5, 12.0, np.linalg.norm(pos - np.asarray(cam.pos)[None], axis=1)))
        col = lin("#fff2d0")[None] * (1.0 - r[:, 1:2] * 0.5) + lin("#ffd27a")[None] * (r[:, 1:2] * 0.5)
        return dict(pos=pos, size=0.06 + 0.0035 * rad, color=col, alpha=a, emit=1.8, kind="soft")


# =====================================================================================================
# THE WORLDS: a new one at each hand-over, cut inside the flash
# =====================================================================================================
LOOKS3 = dict(
    r_night=dict(base="night", sky_top="#02030f", sky_mid="#070d2e", sky_hor="#141c4a", stars=1.0, milky=0.9,
                 hills=0.5, mist=0.12, haze=0.35, ripple=0.25),
    r_rain=dict(base="night", sky_top="#0b0820", sky_mid="#1c1440", sky_hor="#3a2a66", stars=0.0, milky=0.0,
                hills=0.35, mist=0.25, haze=0.5, haze_color="#3a2a66", mist_color="#2a2050", ripple=0.6,
                clouds=0.6),
    r_shore=dict(base="night", sky_top="#0c1a3a", sky_mid="#2a4470", sky_hor="#8fa3c0", sun_color="#dfe6f5",
                 sun_int=0.3, sun_el=-3.0, stars=0.15, milky=0.0, hills=0.8, mist=0.4, mist_color="#4a6080",
                 haze_color="#6a80a0", ripple=0.15),
    r_sea=dict(base="night", sky_top="#031a22", sky_mid="#0a3d48", sky_hor="#1f6e72", stars=0.1, milky=0.0,
               hills=0.4, haze_color="#1f6e72", mist=0.3, mist_color="#1f5a60", ripple=1.0, mirror=0.55),
    r_field=dict(base="night", sky_top="#060a3a", sky_mid="#10206e", sky_hor="#2a3fa0", stars=0.5, milky=0.25,
                 hills=0.7, haze_color="#2a3fa0", mist=0.2, ripple=0.3),
    r_fall=dict(base="night", sky_top="#06080f", sky_mid="#10141f", sky_hor="#232a3a", stars=0.25, milky=0.0,
                hills=0.3, mist=0.45, haze_color="#232a3a", mist_color="#2a3040", ripple=0.2),
    r_circle=dict(base="night", sky_top="#070a14", sky_mid="#121a2e", sky_hor="#26324c", stars=0.3, milky=0.0,
                  hills=0.2, mist=0.35, mist_color="#26324c", haze_color="#26324c", ripple=0.1),
    r_day=dict(base="day", ripple=0.08),
    r_lanterns=dict(base="dusk", sky_top="#0a0830", sky_mid="#241a5c", sky_hor="#6a3a78", stars=0.6, milky=0.3,
                    hills=0.8, lanterns=1.0, sun_color="#ffb070", sun_int=0.35, sun_el=-5.0, ripple=0.3),
)
LOOK_KEYS = [(0.0, "r_night", 0.0), (T1, "r_rain", 0.0), (T2, "r_shore", 0.0), (T3, "r_sea", 0.0),
             (T4, "r_field", 0.0), (T5 + 0.6, "r_fall", 1.2), (BREATH, "r_circle", 1.2), (T6, "r_lanterns", 0.0),
             (T7 + 1.0, "predawn", 2.0), (REL + 0.7, "r_day", 1.8)]


def _burst(t, strength, color="#fff0d0", rise=0.06, fall=0.6, radius=0.35):
    return dict(t=t, strength=strength, rise=rise, fall=fall, color=color, at=tuple(flame_guess(t)), radius=radius)


# quick warm peaks with form and colour, never a white frame
BURSTS = [_burst(T0, 1.0, "#ffd08a", fall=0.3), _burst(T1, 0.9, "#ffd08a", fall=0.25),
          _burst(T2, 0.9, "#ffe0b0", fall=0.25), _burst(T3, 0.8, "#ffd08a", fall=0.25),
          _burst(T4, 1.0, "#ffd08a", fall=0.25), _burst(T5, 1.2, "#ffa860", fall=0.35),
          _burst(HIT["grip"], 0.6, "#ffd9b0", fall=0.3), _burst(T6, 1.5, "#ffd08a", fall=0.4),
          _burst(T7, 0.7, "#ffe0b0", fall=0.3), dict(t=REL, strength=1.1, rise=0.06, fall=0.4, color="#ffd9a0",
                                                    at=tuple(MOTHER_POS + [0.0, 2.2, -0.2]), radius=0.5)]

_LIGHT_K = Track([(0.0, 0.14), (T5 - 0.05, 0.16), (T5 + 0.3, 0.0), (T6 - 0.1, 0.0), (T6 + 0.3, 0.12), (T7, 0.14),
                 (T7 + 0.8, 0.40), (REL, 0.55), (REL + 1.2, 0.25), (60.0, 0.15)], name="LIGHT_K")


def LIGHT_K(t):
    """The flame's rays, weaker when the lens is right at the flame (in the close-ups they filled the frame)."""
    d = float(np.linalg.norm(CAMERA.state(t).pos - flame_pos(t)))
    return float(_LIGHT_K(t)) * (0.12 + 0.88 * float(_ss(0.8, 3.0, d)))
WORLD = WORDS.world(dict(
    look=LOOK_KEYS, looks=LOOKS3,
    arch=dict(lit=ARCH_LIT, bright=0.6),
    react=dict(beat=0.5, level=0.3),
    lantern_field=dict(count=480, center=(0.0, Z_CHILD - 14.0), radius=(4.0, 60.0), height=40.0),
    light=dict(pos=lambda t: flame_pos(t), color="#ffd9a0", strength=LIGHT_K, size=0.35, rays=1.0),
    lights=[dict(pos=lambda t: flame_pos(t), color="#ffb85a",
                 strength=lambda t: 0.28 * float(FLAME_SIZE(t) > 0.01), radius=2.5)],
    shafts=[dict(base=(R["child"].x, Z_CHILD), radius=0.9, top=40.0, color="#dfe8ff",
                 strength=lambda t: 0.35 * float(_ss(BREATH - 1.5, BREATH, t) * (1.0 - _ss(T6, T6 + 0.8, t))))],
))


def _setup(scene):
    from p3d.body import Body
    wind = (0.0, 0.0, 1.2)
    common = dict(facing=180.0, look="glitter", points=70000, wind=wind, bright=1.3)
    looks = dict(
        sprinter=dict(garment="tunic", veil=dict(length=0.55), color="#ffcf7a", color2="#fff1d6"),
        coat=dict(garment="coat", color="#a9c8ff", color2="#ffffff"),
        shawl=dict(garment="dress", veil=dict(length=0.8), color="#8fe3d6", color2="#f2fffb"),
        elder=dict(garment="coat", stoop=0.3, color="#ffd9a0", color2="#fff4e2"),
        youth=dict(garment="tunic", color="#bfe0ff", color2="#ffffff"),
        child=dict(garment="dress", veil=dict(length=0.35), color="#fff0c4", color2="#ffffff", bright=1.5),
    )
    gest = dict(
        sprinter=[(-1.0, T1 + 0.25, "raise_hand", dict(side="R", ease=0.3))],
        coat=[(T1 - 0.45, T2 + 0.25, "raise_hand", dict(side="R", ease=0.3)), (T2 + 1.2, T2 + 9.0, "bow")],
        shawl=[(T2 - 0.45, T3 + 0.25, "raise_hand", dict(side="R", ease=0.3))],
        elder=[(T3 - 0.4, T4 + 0.25, "raise_hand", dict(side="R", ease=0.35))],
        youth=[(T4 - 0.45, T5 - 0.05, "raise_hand", dict(side="R", ease=0.25)), (T5 + 0.7, 36.6, "bow"),
               (36.6, HIT["up"] + 0.8, "reach", dict(side="R", to=tuple(GRIP), ease=0.9))],
        child=[(BREATH - 2.2, T6 + 0.15, "cup", dict(ease=0.8)),
               (T6 + 0.15, T7 + 0.3, "raise_hand", dict(side="R", ease=0.35))],
    )
    for name, r in R.items():
        kw = dict(common)
        kw.update(looks[name])
        BODIES[name] = Body(r.shape, height=r.height, at=(r.x, r.z0), motion=r.keys, gesture=gest[name],
                            show=r.show, fade=0.5, seed=1.0 + len(BODIES) * 3.1,
                            effects=[dict(kind="shed", t=r.show[0], n=4500, life=1.6, speed=0.5)], **kw)
        BODIES[name].add(scene, name)
    BODIES["helper"] = Body("woman", height=1.64, at=(HELPER_POS[0], HELPER_POS[2]), facing=0.0, look="glitter",
                            garment="dress", veil=dict(length=0.7), color="#ffc3a8", color2="#fff0e6",
                            motion=[(T5 + 0.5, "stand"), (T5 + 0.8, "kneel", dict(blend=0.9)),
                                    (HIT["up"], "stand", dict(blend=1.0))],
                            gesture=[(36.0, HIT["up"] + 0.8, "reach", dict(side="L", to=tuple(GRIP), ease=0.9))],
                            show=(T5 + 0.5, T6 + 1.0), fade=1.0, points=70000, wind=wind, seed=31.0)
    BODIES["helper"].add(scene, "helper")
    BODIES["mother"] = Body("woman", height=1.70, at=(MOTHER_POS[0], MOTHER_POS[2]), facing=180.0, look="glitter",
                            garment="robe", veil=dict(length=1.5), color="#fff3d6", color2="#ffd89a",
                            gesture=[(T7 - 1.2, T7 + 0.6, "reach", dict(side="L", to=tuple(flame_guess(T7 - 0.05)
                                                                                           + [0.0, 0.0, 0.0]),
                                                                          ease=0.6)),
                                     (T7 + 0.5, 70.0, "raise", dict(ease=1.0))],
                            show=(45.0, 60.0), fade=1.5, points=90000, wind=(0.3, 0.0, 0.9), seed=41.0)
    BODIES["mother"].add(scene, "mother")
    scene.add("road", Road())
    scene.add("posts", Posts())
    scene.add("flame", Flame())                                        # the flame itself
    scene.add("sparks", PW.KeepClear(Flame(sparks=True), WORDS))       # its sparks and embers keep off the words
    scene.add("rain", PW.KeepClear(Rain(), WORDS))
    scene.add("spray", PW.KeepClear(Spray(), WORDS))
    scene.add("field", PW.KeepClear(Field(), WORDS))
    scene.add("dayring", DayRing())
    WORDS.add_to(scene)
    try:
        WORDS.check(CAMERA)
    except Exception as e:      # the check is advice; never stop a render for it
        print("words check failed:", e)


P3D = dict(camera=CAMERA, world=WORLD, setup=_setup, bursts=BURSTS, motion_blur=0.35)


if __name__ == "__main__":
    for n, r in R.items():
        print(n, "z0 %.1f" % r.z0, "show", r.show, "at T", [round(r.root(x)[2], 1) for x in (r.show[0], r.show[1])])
    print("fall", round(Z_FALL, 1), "child", round(Z_CHILD, 1), "mother", MOTHER_Z, "start", round(Z_START, 1))
    print("arch lit", [round(x, 2) for x in ARCH_LIT])
