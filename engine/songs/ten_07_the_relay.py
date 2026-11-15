"""Film 07 of ten: THE RELAY. One light, carried by many.
A 60 second promo for the Healing Concert "The Words of Mother's Love", on the 3D layer (engine/p3d).

LOGLINE
  A flame is carried down a causeway of light across a dark lake, from one person to the next. Every hand-over
  is a Word of Mother's Love acted out: the runner stops, the two of them DO the word while it is read, the
  flame changes hands, and the next one runs on into a new world. The fastest falls and the flame is scattered;
  a stranger kneels, lifts him up and holds him; the embers come together in a child's hands. She carries the
  flame to Heavenly Mother (only from behind, or as hands), who raises it, and the day breaks from her hands.

THE RULE OF THE FILM
  Running only between the words. Each word is read while it is acted, by people who stand, kneel, bow and
  hold each other; the flame passes at the end of the act and the next carrier runs into the next song.
  Every carrier is a different kind of light (refs and refs2 of the brief), and the framing changes with the
  act: two in profile, hands close, a far crane, a close embrace.

THE ACTING PLAN (word: what is acted, by whom, style, framing)
  Greeting       (3.9 to 6.4)   A runner of gold glitter (p08) slows behind a stranger and touches his
                                shoulder; he turns to her; face to face she lifts the flame between them and he
                                leans in. Two half figures in profile; then their hands close as he takes it.
  Concession     (9.65 to 12.15) In the rain of sparks he (a constellation of points, p01) stops beside a woman
                                waiting at the roadside, gives her the flame and, with an open palm sweeping down
                                the road and a small bow, lets her go first. Full figures from the other side.
  Gratitude      (15.95 to 19.0) On the shore she (a dancer shedding embers, p04) gives the light with both
                                hands to an old man (dotted light, ref 14); he takes it, lays his hand on his
                                heart and bows; she joins her hands. Two in profile, slow arc.
  Respect        (21.4 to 24.35) On the sea wall the old man stops before a boy; the boy speaks with an open
                                hand, the old man leans in, listening, and nods. Close profiles, half figures.
  Encouragement  (27.0 to 29.5) In the field of lights the boy kneels before a woman who kneels praying for him,
                                hands joined; the whole field lifts its lights for him. A far crane: two small
                                kneeling figures in ten thousand lights, the words across the sky.
  Apology        (32.3 to 34.8) He runs on and falls; the flame bursts into embers and he breaks a little like
                                glass. She runs to him, kneels before him and lays a hand on his shoulder.
                                Low side shot, two kneeling figures; the words come up out of the dark water.
  Consideration  (34.95 to 37.45) She stands and reaches down; their hands meet and she pulls him to his feet
                                (standing on the hit at 37.42); his broken light mends. Medium side shot.
  Inclusiveness  (37.6 to 40.1) They hold each other. Close, half figures.
  (the breath, 40.21 to 42.51)  No word: "December 6" is written in light across the sky (TITLES date_light)
                                while the embers stream into a child's cupped hands; on the hit the date bursts
                                and the flame is whole in her hands.
  Compliment     (44.55 to 47.15) She runs among lanterns into a crowd that applauds her, and twirls with the
                                flame held high. Raised three-quarter view of the crowd and the child.
  (day, 49.47)                  She lifts the flame into Heavenly Mother's lowered hand (from behind and above:
                                hands close); Mother raises it, rays round her head; on the bar the day leaves
                                her hands as a ring across the lake; the end card is whole from 54.3 to the end.

TITLE AND DATE (UPDATE 7): the opening lockup over frame 0 (the flame low in the frame, the night sky above
it empty for the title), a discreet signature in two calm walks between words, the date in light in the breath.
The TITLES dict below holds the times and places for the engine's version; until it lands the corner badge
(CREDIT) stays.

THE MUSIC (medley map, branch epic-medley2): sections 0.00 6.84 13.30 19.85 26.79 33.36 40.21 49.47, the
  opening hit 0.25, the breath 40.21 to 42.51, the biggest jump 42.51, the loudest passage 54.3, last hit 58.11.

HOW IT IS BUILT
  The road runs toward -z (toward the arch over the origin). Every person is a Body (engine/p3d/body.py) with
  motion capture (run, walk, kneel, rise, twirl) and acted gestures (touch, offer, reach, bow, listen, pray,
  handshake, embrace, cup). Where each one is at any time is worked out here by the same arithmetic the actor
  uses (`Person`), so the camera and the words can follow them with numpy alone (the workflow's prepare step
  imports this file with numpy only; bodies are built in `_setup`). The flame, the embers, the road of light,
  the rain and birds, the sea spray, the field of lights and the ring of day are this film's own point sets.
  The nine expressions come from engine/p3d/words.py by name.
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


# Title and date as designed (UPDATE 7), for the engine's TITLES: the opening lockup over frame 0 (the flame low
# in the frame, the sky above it empty), the signature in two calm walks between words (top right, over sky),
# "December 6" in light across the sky in the breath, bursting on the hit. Until the engine draws these, the
# corner badge above stands in.
TITLES = dict(
    opening=dict(t_end=3.3, y=0.24, palette="night"),
    signature=dict(windows=[(19.25, 21.05, "tr", "night"), (47.45, 48.9, "tr", "night")]),
    date_light=dict(t_form=40.21, t_burst=42.51, y=0.27, palette="night"),
)


def params(song, t):
    """The base film's params, with the arch functions this song was given by engine/song.py."""
    g = globals()
    if "star_state" in g:
        _base.star_state, _base.link_state = g["star_state"], g["link_state"]
    return _base.params(song, t)


# =====================================================================================================
# THE PEOPLE: where each one is at any time (the same arithmetic as engine/p3d/actor.py: motion keys give
# the speed, facing keys the heading, `at` keys a place that is moved, eased, between keys)
# =====================================================================================================
GRID = 1.0 / 60.0


def _smoother(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6.0 * x - 15.0) + 10.0)


def _ease_keys(keys, t):
    """Value of [(t, v), ...] at t, eased between keys (actor.py heading and _origin_raw)."""
    if t <= keys[0][0]:
        return np.asarray(keys[0][1], np.float64)
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            u = float(_smoother((t - t0) / (t1 - t0)))
            return np.asarray(v0, np.float64) * (1.0 - u) + np.asarray(v1, np.float64) * u
    return np.asarray(keys[-1][1], np.float64)


class Person:
    """One person: `at` (x, z) or keys [(t, (x, z))], `facing` degrees or keys, motion keys
    [(t, name, dict(speed, blend, ...))], `show` (t_in, t_out). Placed later by moving `at` as a whole."""

    def __init__(self, name, shape, height, at, keys, show, facing=180.0, **body):
        self.name, self.shape, self.height = name, shape, height
        self.at = [(-1e9, tuple(at))] if not isinstance(at[0], (tuple, list)) else [(float(k[0]), tuple(k[1])) for k in at]
        self.face = [(-1e9, float(facing))] if isinstance(facing, (int, float)) else [(float(a), float(b)) for a, b in facing]
        self.keys = sorted([(float(k[0]), k[1], dict(k[2]) if len(k) > 2 else {}) for k in keys], key=lambda k: k[0])
        self.show = (float(show[0]), float(show[1]))
        self.body = body
        self._table()

    def heading(self, t):
        return float(_ease_keys(self.face, t))

    def _table(self):
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
        hd = np.radians([self.heading(x) for x in tt])
        vx, vz = speed * np.sin(hd), speed * np.cos(hd)
        cum = lambda v: np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * GRID)])   # noqa: E731
        self.tt, self.px, self.pz, self.speed = tt, cum(vx), cum(vz), speed

    def move(self, dx, dz):
        self.at = [(k[0], (k[1][0] + dx, k[1][1] + dz)) for k in self.at]

    def base(self, t):
        b = _ease_keys(self.at, t)
        return np.array([b[0], 0.0, b[1]])

    def root(self, t):
        return self.base(t) + np.array([np.interp(t, self.tt, self.px), 0.0, np.interp(t, self.tt, self.pz)])

    def at_arg(self):
        return self.at[0][1] if len(self.at) == 1 else self.at

    def face_arg(self):
        return self.face[0][1] if len(self.face) == 1 else self.face


# ---- the timeline of the acts (each expression is read while it is acted; running only between them)
G_TOUCH, G_READ = 2.6, (3.7, 6.2)             # Greeting: a touch on the shoulder, he turns, they meet
PASS1 = 6.45                                  # the flame passes from her right hand to his left
C_STOP, C_READ = 9.75, (9.65, 12.15)          # Concession: he stops beside her and lets her go first
PASS2 = HIT["tape1"]                          # 10.44: his left hand to her right
GR_STOP, GR_READ = 15.3, (15.95, 18.75)       # Gratitude: she gives the light; he, hand on heart, bows
PASS3 = 15.85
R_STOP, R_READ = 21.1, (21.4, 24.35)          # Respect: the boy speaks, the old man listens and nods
PASS4 = 24.6
E_STOP, E_READ = 26.3, (27.6, 30.1)           # Encouragement: he kneels; she prays for him; the field lifts its lights
FALL = HIT["dive"]                            # 31.62: he falls, the flame bursts into embers
A_READ = (32.1, 34.6)                          # Apology: she kneels before him, a hand on his shoulder
K_READ = (34.9, 37.4)                         # Consideration: she stands and pulls him up by the hand
I_READ = (37.7, 40.2)                          # Inclusiveness: they hold each other
# 40.21 to 42.51, the breath: no expression; the date is written in light across the sky (TITLES date_light) while
# the embers gather into a child's cupped hands; on the hit the date bursts and the flame is whole in her hands
P_STOP, P_READ = 44.3, (44.55, 47.15)         # Compliment: the crowd applauds, the child twirls with the flame
RISE = 35.95                                  # he rises from his knee, standing on the hit at 37.42

P = {}
P["sprinter"] = Person("sprinter", "woman", 1.66, (0.0, 0.0),
                       [(0.0, "run", dict(speed=6.2)), (2.3, "walk", dict(speed=1.3, blend=0.55)),
                        (2.85, "stand", dict(blend=0.5))], (0.0, 9.5))
_zs = P["sprinter"].root(4.0)[2]
P["coat"] = Person("coat", "man", 1.80, (0.05, _zs - 0.62),
                   [(0.0, "stand"), (6.6, "run", dict(speed=5.6, blend=0.8)),
                    (C_STOP - 0.45, "walk", dict(speed=1.2, blend=0.5)), (C_STOP, "stand", dict(blend=0.5))],
                   (0.0, 13.6), facing=[(0.0, 180.0), (2.95, 180.0), (3.7, 0.0), (6.4, 0.0), (6.95, 180.0),
                                        (C_STOP, 180.0), (C_STOP + 0.5, 90.0)])
_zc = P["coat"].root(C_STOP + 1.0)
P["shawl"] = Person("shawl", "woman", 1.64, (_zc[0] + 0.85, _zc[2] - 0.30),
                    [(7.5, "stand"), (12.05, "run", dict(speed=5.6, blend=0.8)),
                     (GR_STOP - 0.45, "walk", dict(speed=1.2, blend=0.5)), (GR_STOP, "stand", dict(blend=0.5))],
                    (7.5, 21.0), facing=[(0.0, 270.0), (11.55, 270.0), (12.15, 180.0)])
_zh = P["shawl"].root(GR_STOP + 1.0)
P["elder"] = Person("elder", "man", 1.70, (_zh[0], _zh[2] - 0.72),
                    [(12.5, "stand"), (19.3, "walk", dict(speed=1.35, blend=0.6)),
                     (R_STOP - 0.4, "stand", dict(blend=0.6))],
                    (12.5, 27.0), facing=[(0.0, 0.0), (19.0, 0.0), (19.55, 180.0)], stoop=0.3)
_ze = P["elder"].root(R_STOP + 1.0)
P["youth"] = Person("youth", "man", 1.76, (_ze[0], _ze[2] - 0.86),
                    [(18.5, "stand"), (24.9, "run", dict(speed=5.6, blend=0.7)),
                     (E_STOP - 0.3, "stand", dict(blend=0.5)), (E_STOP + 0.15, "kneel", dict(one=True, blend=0.6)),
                     (30.2, "rise", dict(one=True, dur=0.5, blend=0.2)),
                     (30.6, "run", dict(speed=6.8, blend=0.5)),
                     (FALL - 0.05, "kneel", dict(one=True, blend=0.45)),
                     (RISE, "rise", dict(one=True, dur=1.5, blend=0.05))],
                    (18.5, T6 + 1.2), facing=[(0.0, 0.0), (24.65, 0.0), (25.15, 180.0), (E_STOP - 0.1, 180.0),
                                              (E_STOP + 0.45, 90.0), (30.25, 90.0), (30.7, 180.0)])
_zk = P["youth"].root(E_STOP + 1.0)
Z_FALL = P["youth"].root(FALL + 1.5)[2]
X_FALL = P["youth"].root(FALL + 1.5)[0]
P["helper"] = Person("helper", "woman", 1.64,
                     [(0.0, (_zk[0] + 1.0, _zk[2]))],
                     [(24.0, "kneel", dict(hands="pray", dur=0.01)),
                      (30.35, "rise", dict(one=True, dur=0.6, blend=0.2)),
                      (30.85, "run", dict(speed=5.6, blend=0.5)),
                      (31.95, "walk", dict(speed=1.0, blend=0.5)), (32.2, "stand", dict(blend=0.4)),
                      (32.35, "kneel", dict(one=True, blend=0.7)),
                      (34.15, "rise", dict(one=True, dur=0.7, blend=0.15)),
                      (37.25, "shuffle", dict(blend=0.4)), (38.0, "stand", dict(blend=0.4))],
                     (24.0, T6 + 1.2), facing=[(0.0, 270.0), (30.4, 270.0), (30.85, 180.0),
                                               (31.9, 180.0), (32.35, 0.0)])
# she lands right in front of him, facing him: correct her ground place while she runs
_hz = P["helper"].root(33.0)
_tx, _tz = X_FALL + 0.02, Z_FALL - 0.80
P["helper"].at = [(0.0, (_zk[0] + 1.0, _zk[2])), (30.85, (_zk[0] + 1.0, _zk[2])),
                  (32.1, (_zk[0] + 1.0 + (_tx - _hz[0]), _zk[2] + (_tz - _hz[2]))),
                  (37.25, (_zk[0] + 1.0 + (_tx - _hz[0]), _zk[2] + (_tz - _hz[2]))),
                  (38.0, (_zk[0] + 1.0 + (_tx - _hz[0]), _zk[2] + (_tz - _hz[2]) + 0.42))]
P["child"] = Person("child", "child", 1.15, (X_FALL + 0.95, Z_FALL - 2.1),
                    [(37.0, "kneel", dict(dur=0.01)), (T6 + 0.05, "stand", dict(blend=0.35)),
                     (T6 + 0.35, "run", dict(speed=4.0, blend=0.8)),
                     (P_STOP - 0.4, "stand", dict(blend=0.5)), (P_STOP + 0.05, "twirl", dict(blend=0.4)),
                     (P_READ[1] + 0.25, "walk", dict(speed=1.15, blend=0.7)), (T7 - 0.15, "stand", dict(blend=0.6))],
                    (37.0, 60.0))
_zch = P["child"].root(60.0)
MOTHER_Z = 14.0
MOTHER_POS = np.array([_zch[0] + 0.62, 0.0, MOTHER_Z])          # the child ends at her left side
_shift = MOTHER_Z + 0.05 - _zch[2]
for _p in P.values():
    _p.move(0.0, _shift)
MOTHER_POS = np.array([P["child"].root(60.0)[0] + 0.62, 0.0, MOTHER_Z])
Z_FALL += _shift
Z_START = P["sprinter"].root(0.0)[2]
Z_CHILD = P["child"].root(BREATH)[2]
CROWD_AT = P["child"].root(P_STOP + 0.5)
SNAP = HIT["snap"]


def root(who, t):
    if who == "mother":
        return MOTHER_POS.copy()
    return P[who].root(t)


# who holds the flame, and in which hand
HOLDERS = [(-1.0, "sprinter", "R"), (PASS1, "coat", "L"), (PASS2, "shawl", "R"), (PASS3, "elder", "L"),
           (PASS4, "youth", "R"), (FALL, None, None), (T6, "child", "R"), (T7, "mother", "L")]


def holder(t):
    k = max(i for i, h in enumerate(HOLDERS) if t >= h[0])
    return HOLDERS[k][1], HOLDERS[k][2], k


def flame_guess(t):
    """Where the flame is at t, worked out without the bodies (for the road, rain, bursts and light)."""
    who, side, k = holder(t)
    if who is None:
        return EMBER_HOME.copy()
    if who == "mother":
        return MOTHER_POS + np.array([0.0, 2.15, -0.15])
    p = P[who]
    r = p.root(t)
    hd = np.radians(p.heading(t))
    fwd = np.array([np.sin(hd), 0.0, np.cos(hd)])
    left = np.array([np.cos(hd), 0.0, -np.sin(hd)])
    sg = 1.0 if side == "L" else -1.0
    moving = float(np.interp(t, p.tt, p.speed)) > 0.5
    up = p.height + 0.30 if moving else p.height * 0.62
    return r + left * sg * 0.20 + fwd * (0.05 if moving else 0.30) + np.array([0.0, up, 0.0])


EMBER_HOME = np.array([X_FALL + 0.1, 0.05, Z_FALL - 1.3])

# =====================================================================================================
# THE BODIES (built in _setup: they need scipy and the assets) and the flame's real place
# =====================================================================================================
BODIES = {}


def _palm_up(name, t, side="R", up=0.11):
    b = BODIES[name]
    return np.asarray(b.where(t, "palm." + side), np.float64) + np.array([0.0, up, 0.0])


def _held(name, side, t):
    if name not in BODIES:
        return flame_guess(t)
    if name == "child" and t < T6 + 0.3:
        b = BODIES["child"]
        return 0.5 * (np.asarray(b.where(t, "palm.L")) + np.asarray(b.where(t, "palm.R"))) + [0.0, 0.10, 0.0]
    if name == "mother":
        b = BODIES["mother"]
        r = _palm_up("mother", t, "L", 0.10)
        both = 0.5 * (np.asarray(b.where(t, "palm.L")) + np.asarray(b.where(t, "palm.R"))) + [0.0, 0.16, 0.0]
        u = float(_smoother((t - (T7 + 0.5)) / 0.9))
        return r * (1.0 - u) + both * u
    return _palm_up(name, t, side)


def flame_pos(t):
    """Where the flame is at t: in the holder's hand (crossing over in 0.16 s from hand to hand)."""
    who, side, k = holder(t)
    if who is None:
        return EMBER_HOME.copy()
    p = _held(who, side, t)
    t0 = HOLDERS[k][0]
    prev = HOLDERS[k - 1][1] if k > 0 else None
    if prev is not None and t - t0 < 0.16:
        u = float(_smoother((t - t0) / 0.16))
        p = _held(prev, HOLDERS[k - 1][2], t) * (1.0 - u) + p * u
    return p


FLAME_SIZE = Track([(0.0, 0.17), (PASS1, 0.18), (PASS2, 0.19), (PASS3, 0.20), (PASS4, 0.22), (FALL - 0.1, 0.24),
                    (FALL + 0.25, 0.0), (T6 - 0.12, 0.0), (T6 + 0.35, 0.27), (T7, 0.28), (REL, 0.34), (60.0, 0.34)],
                   name="FLAME_SIZE")


# =====================================================================================================
# THE CAMERA: moves that follow someone (or the flame), blended by the rig
# =====================================================================================================
from p3d.camera import Move, Rig  # noqa: E402


class follow(Move):
    """Ride with `who` (a person, "flame", "mother" or "world"): pos and look are offsets in metres (x right of
    the road, y up, z back along the road), or pairs (start, end) eased over the move (or by its pace)."""

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
    # ---- night road: she runs; a touch on a stranger's shoulder; he turns; the Greeting; the flame passes
    follow(F, (1.45, 0.10, 0.85), (0.0, 0.36, -0.2), 0.0, 0.32, fov=40, aperture=0.03, near=0.02),
    follow("sprinter", (4.6, 1.25, 0.4), (0.0, 1.35, -0.8), 0.32, 2.1, fov=42, blend=0.45),
    follow("coat", ((3.6, 1.30, 0.5), (3.0, 1.38, 0.38)), (0.0, 1.40, 0.31), 2.35, 6.3, fov=40, blend=0.9),
    follow(F, (0.75, 0.05, 0.30), (0.0, -0.05, 0.0), 6.35, 6.85, fov=40, aperture=0.015, blend=0.35),
    follow("coat", (1.8, 1.6, 3.4), (0.0, 1.6, -10.0), 6.9, 7.5, fov=46, blend=0.45, focus=3.9),
    # ---- rain of sparks: he runs; he stops beside a woman, gives her the flame and lets her go first
    follow("coat", (2.8, 1.2, 0.6), (0.0, 1.3, -1.0), 7.5, 9.2, fov=44, blend=0.8),
    follow("coat", ((0.2, 1.45, 3.6), (0.35, 1.4, 3.0)), (0.45, 1.25, -0.6), 9.3, 12.3, fov=42, blend=0.6),
    follow("shawl", (1.6, 1.5, 3.2), (0.0, 1.5, -10.0), 12.35, 13.25, fov=46, blend=0.5, focus=3.5),
    # ---- shore of birds: she runs; she gives the light to an old man; hand on heart, he bows
    follow("shawl", ((4.2, 0.8, 1.0), (4.6, 1.6, 0.6)), (0.0, 1.5, -1.2), 13.35, 14.9, fov=46, blend=0.5),
    follow("elder", ((3.2, 1.2, 0.9), (2.8, 1.38, 0.1)), (0.0, 1.32, 0.38), 15.05, 19.0, fov=40, blend=0.7),
    follow("elder", (1.2, 1.7, 3.0), (0.0, 1.5, -8.0), 19.1, 20.4, fov=46, blend=0.7, focus=3.3),
    # ---- the sea: they stop; the boy speaks, the old man listens; time returns; the flame passes
    follow("youth", ((2.6, 1.42, 0.55), (2.3, 1.48, 0.45)), (0.0, 1.48, 0.43), 20.6, 24.4, fov=36, blend=0.7),
    follow(F, (0.8, 0.05, 0.3), (0.0, 0.0, 0.0), 24.4, 25.0, fov=40, aperture=0.015, blend=0.4),
    follow("youth", ((2.9, 0.75, 1.6), (2.4, 1.1, 0.4)), (0.0, 1.35, -2.0), 25.05, 26.1, fov=48, aperture=0.015,
           blend=0.45),
    # ---- field of lights: he kneels before a woman who prays for him; the whole field lifts its lights for him
    follow("youth", ((1.2, 1.25, 3.4), (7.0, 8.0, 11.0)), ((0.5, 0.8, 0.0), (-5.0, 6.0, -40.0)), 26.2, 30.1, fov=50,
           blend=0.6, pace=[(26.2, 0.0), (27.0, 0.25), (27.8, 0.75), (29.0, 0.95), (30.1, 1.0)]),
    follow("youth", (1.6, 0.9, 2.8), (0.0, 1.0, -6.0), 30.35, 31.5, fov=54, aperture=0.012, blend=0.5, focus=3.1),
    # ---- the fall: she kneels before him; she pulls him up; they hold each other
    follow("youth", (3.0, 0.65, -0.35), (0.0, 0.85, -0.42), 31.75, 34.85, fov=40, aperture=0.02, blend=0.45),
    follow("youth", (2.7, 0.95, -0.45), (0.0, 1.05, -0.45), 34.85, 37.5, fov=38, aperture=0.02, blend=1.2),
    follow("youth", ((2.7, 1.35, -0.6), (2.5, 1.3, -0.9)), (0.0, 1.2, -0.95), 37.55, 40.45, fov=40, aperture=0.02,
           blend=0.8),
    # ---- the breath: a child kneels with cupped hands; the embers come to her; the date is written in the sky
    follow("child", ((3.4, 0.8, 1.0), (2.8, 0.75, 0.55)), (0.0, 1.75, -0.35), 40.45, 42.6, fov=44, aperture=0.02,
           blend=0.7),
    # ---- lanterns: the flame is whole; she runs; the crowd applauds and she twirls with it
    follow("child", (0.6, 0.8, 2.3), (0.0, 2.0, -10.0), 42.7, 43.05, fov=52, blend=0.4, focus=2.5),
    follow("child", (3.0, 1.0, 0.6), (0.0, 0.95, -1.5), 43.1, 44.2, fov=42, blend=0.5),
    follow("child", ((4.8, 2.4, 3.6), (4.2, 2.1, 2.6)), (0.0, 1.0, -0.6), 44.3, 47.3, fov=46, blend=0.6),
    follow("child", (0.9, 1.3, 3.0), (0.0, 1.5, -12.0), 47.35, 48.9, fov=44, blend=0.9, focus=3.2),
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
# THE NINE EXPRESSIONS (engine/p3d/words.py by name), each read while it is acted, fixed in the world over
# the people who act it, to the right of the badge
# =====================================================================================================
from p3d import words as PW  # noqa: E402
from p3d.world import arch_points  # noqa: E402

ARCH = arch_points()


def _word(x, y, depth, px, t_in, t_read0, t_read1, t_out, **kw):
    """A word laid out at the middle of its reading moment at picture place (x, y), `depth` metres ahead, with
    an em of `px` pixels; it stays there in the world."""
    tm = 0.5 * (t_read0 + t_read1)
    p = np.asarray(PW.place(CAMERA, tm, x, y, depth), np.float64)
    em = PW.em_for(CAMERA, tm, depth, px)
    return dict(pos=tuple(p), em=em, t_in=t_in, t_read0=t_read0, t_read1=t_read1, t_out=t_out, **kw)


def _flame_at(tt):
    return lambda t: flame_pos(tt)


def _src(name, place, fallback):
    def f(t):
        if name in BODIES:
            return np.asarray(BODIES[name].where(t, place), np.float64)
        return np.asarray(fallback(t) if callable(fallback) else fallback, np.float64)
    return f


_SPECS = [
    dict(expr="Greeting", arrive="touch", source=_src("coat", "shoulder.L", lambda t: root("coat", t) + [0, 1.5, 0]),
         leave="wind", wind=(0.0, 0.15, 1.0), **_word(0.50, 0.80, 7.0, 100, G_READ[0] - 0.6, *G_READ, 6.95)),
    dict(expr="Concession", arrive="touch", source=_flame_at(C_STOP - 0.6), leave="bokeh",
         **_word(0.50, 0.80, 7.5, 96, C_STOP - 0.6, *C_READ, 12.9)),
    dict(expr="Gratitude", arrive="petals", source=_flame_at(PASS3), leave="flock",
         **_word(0.50, 0.78, 7.5, 84, PASS3 - 0.55, *GR_READ, 19.8)),
    dict(expr="Respect", arrive="stars", leave="sink", **_word(0.50, 0.80, 6.5, 94, 20.2, *R_READ, 25.1)),
    dict(expr="Encouragement", arrive="touch", source=_flame_at(E_STOP + 0.3), leave="arch", to=tuple(ARCH[6]),
         **_word(0.50, 0.72, 50.0, 90, E_STOP + 0.25, *E_READ, 30.9)),
    dict(expr="Apology", arrive="lake", leave="morph", color="#e6ecff", glow="#9fb4ff",
         **_word(0.50, 0.79, 6.0, 84, FALL + 0.08, *A_READ, A_READ[1])),
    dict(expr="Consideration", arrive="morph", source="Apology", leave="morph",
         **_word(0.50, 0.79, 6.0, 84, A_READ[1], *K_READ, K_READ[1])),
    dict(expr="Inclusiveness", arrive="morph", source="Consideration", leave="stream",
         to=lambda t: flame_pos(t) if t > T6 else root("child", t) + np.array([0.0, 0.62, -0.2]),
         **_word(0.50, 0.80, 6.0, 96, K_READ[1], *I_READ, 40.85)),
    dict(expr="Compliment", arrive="rays", source=lambda t: flame_pos(t), leave="arch", to=tuple(ARCH[8]),
         **_word(0.50, 0.80, 11.0, 94, P_STOP - 0.6, *P_READ, 47.9)),
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
        if self.sparks and FALL - 0.05 <= t < T6 + 0.5:
            out.append(self._embers(t))
        if self.sparks:
            out = out[2:] if len(out) > 2 and h > 0.004 else [b for b in out if b.get("kind") == "spark"]
        else:
            out = out[:2] if h > 0.004 else []
        return out

    def _embers(self, t):
        e = self.e
        p0 = flame_guess(FALL - 0.05)
        fly = _ss(FALL, FALL + 0.9 + 0.5 * e[:, 2], t)[:, None]
        hop = np.abs(np.sin(fly[:, 0] * np.pi * (1.0 + 2.0 * e[:, 3]))) * (1.0 - fly[:, 0]) * 0.6
        pos = p0 * (1.0 - fly) + self.rest * fly
        pos[:, 1] += hop
        # lifted in open hands (a share of them), then streamed into the child's cupped hands
        lift = np.zeros(len(e))
        pos[:, 1] += lift * (0.55 + 0.45 * e[:, 2])
        go = _ss(40.1 + 1.5 * e[:, 4], 41.9 + 0.55 * e[:, 4], t)[:, None]
        tgt = root("child", t) + np.array([0.0, 0.62, -0.22])
        mid = 0.5 * (pos + tgt) + np.array([0.0, 1.2, 0.0])
        q = go
        pos = (1 - q) ** 2 * pos + 2 * (1 - q) * q * mid + q * q * tgt
        cool = _ss(FALL + 0.5, FALL + 2.8, t)
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
        za, zb = P["elder"].root(T3 - 1.0)[2] + 10.0, P["elder"].root(T4)[2] - 14.0
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
        za, zb = P["youth"].root(E_STOP)[2] + 40.0, Z_FALL - 90.0
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
        fz = flame_guess(min(t, FALL))[2]
        dz = self.base[:, 2] - fz
        wave = np.exp(-((dz + 7.0) / 11.0) ** 2) * np.exp(-np.abs(self.base[:, 0]) / 40.0) * (1.0 - _ss(FALL, FALL + 1.0, t))
        dark = _ss(FALL, FALL + 1.6, t)
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
             (T4, "r_field", 0.0), (FALL + 0.4, "r_fall", 1.2), (BREATH, "r_circle", 1.2), (T6, "r_lanterns", 0.0),
             (T7 + 1.0, "predawn", 2.0), (REL + 0.7, "r_day", 1.8)]


def _burst(t, strength, color="#fff0d0", rise=0.06, fall=0.6, radius=0.35):
    return dict(t=t, strength=strength, rise=rise, fall=fall, color=color, at=tuple(flame_guess(t)), radius=radius)


# quick warm peaks with form and colour, never a white frame
BURSTS = [_burst(T0, 1.0, "#ffd08a", fall=0.3), _burst(T1, 0.9, "#ffd08a", fall=0.25),
          _burst(T2, 0.9, "#ffe0b0", fall=0.25), _burst(T3, 0.8, "#ffd08a", fall=0.25),
          _burst(T4, 1.0, "#ffd08a", fall=0.25), _burst(FALL, 1.2, "#ffa860", fall=0.35),
          _burst(HIT["grip"], 0.6, "#ffd9b0", fall=0.3), _burst(T6, 1.5, "#ffd08a", fall=0.4),
          _burst(T7, 0.7, "#ffe0b0", fall=0.3), dict(t=REL, strength=1.1, rise=0.06, fall=0.4, color="#ffd9a0",
                                                    at=tuple(MOTHER_POS + [0.0, 2.2, -0.2]), radius=0.5)]

_LIGHT_K = Track([(0.0, 0.14), (FALL - 0.05, 0.16), (FALL + 0.3, 0.0), (T6 - 0.1, 0.0), (T6 + 0.3, 0.12), (T7, 0.14),
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
    shafts=[dict(base=(float(P["child"].root(BREATH)[0]), Z_CHILD), radius=0.9, top=40.0, color="#dfe8ff",
                 strength=lambda t: 0.35 * float(_ss(BREATH - 1.5, BREATH, t) * (1.0 - _ss(T6, T6 + 0.8, t))))],
))

def _w(name, place):
    """A world place on another body, as that body is without its own gestures (contact, as engine/p3d/pairs)."""
    return lambda t: np.asarray(BODIES[name].where(t, place, raw=True), np.float64)


def _grip(t):
    """Where the helper's right hand and the boy's right hand meet (engine/p3d/pairs.helped_up)."""
    pa = np.asarray(BODIES["helper"].where(t, "shoulder.R", raw=True), np.float64)
    pb = np.asarray(BODIES["youth"].where(t, "shoulder.R", raw=True), np.float64)
    g = 0.5 * (pa + pb)
    g[1] -= 0.33 * BODIES["helper"].k
    return g


def _ahead(name, right=0.0, up=1.0, ahead=0.9):
    """A point in front of someone's road position: the way down the road (for "please, after you")."""
    return lambda t: root(name, t) + np.array([right, up, -ahead])


def _heart(name):
    def f(t):
        b = BODIES[name]
        p, n = b.where(t, "heart", normal=True, raw=True)
        return np.asarray(p, np.float64) + 0.07 * np.asarray(n, np.float64)
    return f


GESTURES = dict(
    sprinter=[(-1.0, G_TOUCH - 0.05, "raise_hand", dict(side="R", ease=0.35)),
              (G_TOUCH, 3.7, "hand_on_shoulder", dict(side="L", to=_w("coat", "shoulder.L"), ease=0.45)),
              (2.9, PASS1 + 0.35, "offer", dict(side="R", ease=0.5)),
              (PASS1 + 0.3, 9.5, "pray", dict(ease=0.9))],
    coat=[(3.6, 5.4, "bow", dict(amount=10.0, ease=0.6)),
          (5.35, PASS1 + 0.25, "reach", dict(side="L", to=_w("sprinter", "palm.R"), palm="down", ease=0.45)),
          (PASS1 + 0.15, C_STOP + 0.05, "raise_hand", dict(side="L", ease=0.4)),
          (C_STOP - 0.2, PASS2 + 0.15, "offer", dict(side="L", ease=0.5)),
          (PASS2 + 0.1, 12.7, "reach", dict(side="L", to=_ahead("coat", 0.15, 0.95, 0.95), palm="up", far=0.95,
                                            ease=0.6)),
          (10.9, 12.3, "bow", dict(amount=14.0, ease=0.5))],
    shawl=[(PASS2 - 0.6, PASS2 + 0.3, "reach", dict(side="R", to=_w("coat", "palm.L"), ease=0.45)),
           (11.0, 11.7, "bow", dict(amount=10.0, ease=0.3)),
           (11.85, GR_STOP + 0.05, "raise_hand", dict(side="R", ease=0.4)),
           (GR_STOP - 0.15, PASS3 + 0.3, "offer", dict(side="R", ease=0.5)),
           (PASS3 + 0.45, 19.4, "pray", dict(ease=0.8))],
    elder=[(PASS3 - 0.6, PASS3 + 0.3, "reach", dict(side="L", to=_w("shawl", "palm.R"), ease=0.45)),
           (PASS3 + 0.2, PASS4 + 0.25, "offer", dict(side="L", ease=0.5)),
           (PASS3 + 0.4, 18.9, "touch", dict(side="R", to=_heart("elder"), ease=0.55)),
           (PASS3 + 0.6, 18.7, "bow", dict(amount=24.0, ease=0.6)),
           (21.3, 24.3, "listen", dict(side="R", amount=1.0, ease=0.6)),
           (22.7, 23.45, "bow", dict(amount=9.0, ease=0.3))],
    youth=[(21.25, 24.1, "offer", dict(side="L", ease=0.6)),
           (PASS4 - 0.5, PASS4 + 0.3, "reach", dict(side="R", to=_w("elder", "palm.L"), ease=0.45)),
           (PASS4 + 0.2, FALL - 0.05, "raise_hand", dict(side="R", ease=0.3)),
           (E_STOP + 0.6, 30.2, "bow", dict(amount=16.0, ease=0.6)),
           (FALL + 0.4, RISE - 0.3, "bow", dict(amount=26.0, ease=0.7)),
           (34.75, 38.0, "handshake", dict(side="R", to=_grip, grip=1.0, ease=0.6)),
           (37.5, 45.0, "embrace", dict(to=_w("helper", "blade.R"), to2=_w("helper", "blade.L"), head="L", ease=1.0))],
    helper=[(32.65, 34.35, "hand_on_shoulder", dict(side="R", to=_w("youth", "shoulder.L"), ease=0.6)),
            (34.6, 38.0, "handshake", dict(side="R", to=_grip, grip=1.0, ease=0.7)),
            (37.4, 45.0, "embrace", dict(to=_w("youth", "blade.R"), to2=_w("youth", "blade.L"), head="L", ease=1.0))],
    child=[(37.0, T6 + 0.2, "cup", dict(ease=0.8)),
           (T6 + 0.15, T7 + 0.3, "raise_hand", dict(side="R", ease=0.35))],
)
# a style of person for each carrier (refs and refs2 of the brief)
STYLES = dict(
    sprinter=dict(garment="tunic", look="glitter", color="#ffcf7a", color2="#fff1d6",              # gold glitter, p08
                  effects=[dict(kind="shed", t=0.0, n=4500, life=1.6, speed=0.5)]),
    coat=dict(garment="coat", look=dict(name="plexus", bright=1.2), color="#cfe0ff", color2="#ffffff"),  # constellation, p01
    shawl=dict(garment="dress", look="glitter", color="#ff9a4a", color2="#ffd890",                  # a dancer of embers, p04
               effects=[dict(kind="shed", t=7.5, n=9000, life=1.4, speed=0.9, color="#ff7a2a")]),
    elder=dict(garment="coat", look="dots", color="#ffd9a0", color2="#ffb070"),                     # dotted light, ref 14
    youth=dict(garment="tunic", look="glitter", color="#cfe8ff", color2="#ffffff",                   # crystal, breaks like glass
               effects=[dict(kind="disperse", t=FALL, share=0.30, dir=(0.0, 0.5, 1.0),
                             amount=Track([(0.0, 0.0), (FALL, 0.0), (FALL + 0.6, 0.20), (RISE, 0.20), (RISE + 1.3, 0.0),
                                           (60.0, 0.0)]))]),
    helper=dict(garment="dress", look="dots", color="#ffb0c4", color2="#ffe2c8"),                   # rose dots
    child=dict(garment="dress", look="glitter", color="#fff0c4", color2="#ffffff", bright=1.5),     # a small bright spark, p09
)


def _setup(scene):
    from p3d.body import Body
    wind = (0.0, 0.0, 1.0)
    for name, p in P.items():
        kw = dict(points=70000, wind=wind, bright=1.3)
        kw.update(STYLES[name])
        if "stoop" in p.body:
            kw["stoop"] = p.body["stoop"]
        BODIES[name] = Body(p.shape, height=p.height, at=p.at_arg(), facing=p.face_arg(), motion=p.keys,
                            gesture=GESTURES[name], show=p.show, fade=0.6, seed=1.0 + 3.1 * len(BODIES), **kw)
        BODIES[name].add(scene, name)
    BODIES["mother"] = Body("woman", height=1.70, at=(MOTHER_POS[0], MOTHER_POS[2]), facing=180.0, look="glitter",
                            garment="robe", veil=dict(length=1.5), color="#fff3d6", color2="#ffd89a",
                            gesture=[(T7 - 1.2, T7 + 0.6, "reach", dict(side="L", to=tuple(flame_guess(T7 - 0.05)),
                                                                          ease=0.6)),
                                     (T7 + 0.5, 70.0, "raise", dict(ease=1.0))],
                            show=(45.0, 60.0), fade=1.5, points=90000, wind=(0.3, 0.0, 0.9), seed=41.0)
    BODIES["mother"].add(scene, "mother")
    try:
        from p3d.crowd import Crowd
        crowd = Crowd(n=64, area=dict(center=(float(CROWD_AT[0]), float(CROWD_AT[2])), radius=(2.8, 15.0)),
                      facing="center", kinds=(("clap", 0.6), ("raise", 0.25), ("stand", 0.15)),
                      start=dict(t=P_STOP - 0.9, center=(float(CROWD_AT[0]), float(CROWD_AT[2])), speed=10.0),
                      until=49.6, fade=0.7, points=2600, color="#ffe6c0", color2="#bcd0ff")
        scene.add("crowd", PW.KeepClear(crowd, WORDS))
    except ImportError:          # an engine without crowds: the lanterns carry the scene alone
        pass
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
