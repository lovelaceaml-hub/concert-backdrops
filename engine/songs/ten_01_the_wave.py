"""Film 01: THE WAVE (60 seconds, a promo for The Words of Mother's Love Healing Concert).

LOGLINE
  One word falls into a sleeping black sea and becomes the edge of morning. In one unbroken flight we ride
  that wave of light as it wakes everyone it touches, grows with each of the nine Words of Mother's Love, and
  breaks on the far shore as the sunrise.

THE RULES OF THIS FILM
  1. One shot, no cuts: the camera always travels with the wave (drop in, cutback, stall, barrel, trim, run,
     hang, break), fast on the section starts, slower round the people.
  2. The wave is the edge of morning: night and black glass ahead, glittering water and dawn behind.
  3. Everything the wave touches wakes. As the crest passes, people form out of light and ACT the expression
     it carries, and hold that act while the words are read. No two expressions look alike: each has its own
     style of people (refs2 p01 to p09) and its own framing (a profile, a pair, figures on the crest, a crowd,
     tiny people along a vast shore).
  4. Gold only. The nine campaign colours tint each expression's glow, never the wave.
  5. No Heavenly Mother figure: the first word falls from above down a thin shaft of light; the morning at the
     end is hers; the title says whose words these are.

THE ACTING PLAN (the medley's sections: 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 (breath to 42.51), 49.47)
  0 to 4      OPENING TITLE over the spark falling down its shaft to its mirror image (TITLES "opening").
  GREETING    "How are you?"  A woman asleep on the black glass, half figure in profile, white gold glitter.
              The crest sweeps past her feet, the light climbs her to the face, she lifts her head toward the
              light and waves one hand: a face lighting up. Read 4.75 to 7.25.
  GRATITUDE   We swing round her and look back for the first time. An older man in the wake bows to her with
              his hand on his heart (gold glitter, p08); behind him a whole crowd the wave has woken bows too.
              She turns to him and opens her hand. Read 8.95 to 11.8. Signature 12.45 to 13.5.
  APOLOGY     In the mist among lanterns that catch in a sweep: two soft figures of pearl and rose dust (p09).
              One stands with head bowed and open hands low; the other has turned away. Read 14.35 to 16.95.
  INCLUSIVENESS  The words turn into their answer: the other turns round, they walk in and hold each other; a
              warm flare where they meet. Read 17.8 to 20.35.
  CONCESSION  The bass slams in, the wave folds over and we glide down a tunnel of streaks. Before the mouth of
              the barrel (a door of light) two people of clear glass-white light: one steps aside with an open
              palm toward the door and lets the other walk through first. Read 22.0 to 24.7.
  RESPECT     Out of the mouth into the strait. Two people seated on the crest of the moving wave, drawn as
              constellations of points and fine lines (p01): one speaks with small open hands, the other leans
              in and listens; we revolve round them. Read 27.9 to 30.6. Signature 31.3 to 33.4.
  CONSIDERATION  The wave doubles its speed over a bay of sleepers. On its crest one reaches down to someone
              kneeling, takes their hand and pulls them up (coloured dots, ref 14); then we rise over the crest
              and see the bay light up row after row. Read 34.7 to 37.6.
  THE BREATH  40.21 to 42.51: the wave crouches low and waits for one person kneeling on the water; "December 6"
              is written in light across the sky above it (TITLES "date_light"); on the biggest hit the date
              bursts and the wave rears up into a wall of light 24 m high and carries the burst.
  ENCOURAGEMENT  Before the wall the kneeling one prays; another walks to them and lays a hand on their
              shoulder (white gold, a little light rising off them). Read 43.45 to 45.95.
  COMPLIMENT  The words turn into the compliment as the wall is released. We climb over its lip: the people
              the wave carries stand along the crest and fling up their arms in a wave of cheering, and at
              their front a dancer twirls in joy, sparks streaming off her dress. Read 47.15 to 49.65.
  THE BREAK   49.47: the wave breaks on the shore under the arch of nine lights: a plume of gold, the sun comes
              up warm through it, the night is swept off the sky. The people stand tiny along the vast shore;
              the end card, readable from 55.5 s to the last frame. No fade: the last frame is full daylight.

Rules kept: no lyrics, artistic faces only (never photorealistic), everyone clothed in garments of light, no
Heavenly Mother figure, all nine expressions from words.EXPRESSIONS, one read at a time and nothing crossing
them, nothing dark behind any text, no white-outs, no em dash or en dash, the first frame is a picture, the
last frame is daylight.
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 60.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 59.9
_base.SONG_END = 60.0
_base.FADE = _base.Track([(0.0, 1.0), (60.0, 1.0)])          # no fade in, no fade out: frame 0 is a picture
_base.EXPOSURE = _base.Track([(0.0, 1.0), (60.0, 1.0)])
for _p in _base.PHRASES:                                       # the flat expressions stay off: words are light
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.api import lin  # noqa: E402
from p3d.body import Body  # noqa: E402
from p3d import effects as fx  # noqa: E402
from p3d import pairs  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402
from p3d import ten_01_wave as WV  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))  # noqa: F405
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

# ---- the music (scratchpad medley2/SECTION-MAP.md)
SECTION_STARTS = [0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47]
HIT0, IMPACT = 0.25, 0.97
BREATH, BIG = 40.21, 42.51
FINAL_HIT = 58.11
BREAK = 49.47

ss = WV.smoothstep


def lerp(a, b, u):
    return np.asarray(a, np.float64) * (1.0 - u) + np.asarray(b, np.float64) * u


# ---------------------------------------------------------------------------------------------------------
# THE WAVE: speed (m/s, linear between keys), height (m) and curl (0 a swell, 1 a barrel), eased
# ---------------------------------------------------------------------------------------------------------
SPEED = [(0.0, 0.0), (IMPACT, 0.0), (IMPACT + 0.06, 15.0), (1.9, 10.0), (5.6, 8.0), (6.4, 3.0), (8.0, 0.9),
         (12.7, 0.9), (13.30, 22.0), (14.2, 16.0), (14.9, 3.0), (19.3, 2.5), (19.85, 12.0), (20.6, 15.0),
         (26.0, 15.0), (26.79, 22.0), (33.0, 22.0), (33.36, 32.0), (39.6, 32.0), (40.21, 8.0), (41.2, 1.0),
         (42.4, 1.0), (42.6, 2.5), (46.05, 2.0), (46.6, 30.0), (49.3, 34.0), (BREAK, 36.0), (50.6, 90.0),
         (52.0, 260.0), (54.0, 600.0), (60.0, 900.0)]
HEIGHT = [(0.0, 0.0), (IMPACT, 0.02), (1.4, 0.14), (6.0, 0.24), (6.84, 0.40), (12.8, 0.55), (13.6, 1.0),
          (19.3, 1.25), (19.85, 1.6), (20.9, 4.2), (26.0, 4.4), (27.3, 5.6), (33.0, 6.6), (33.9, 8.0),
          (39.8, 9.0), (40.5, 7.5), (41.3, 4.6), (42.45, 4.4), (43.25, 24.0), (46.0, 26.0), (46.8, 18.0), (BREAK, 14.0), (50.6, 7.0),
          (52.5, 4.0), (60.0, 3.0)]
CURL = [(0.0, 0.0), (19.85, 0.0), (20.9, 1.0), (25.2, 1.0), (26.6, 0.0), (45.9, 0.0), (46.6, 0.25),
        (47.4, 0.0), (60.0, 0.0)]
_K0 = WV.Kinematics(SPEED, HEIGHT, CURL, drop=(0.0, 0.0), t_impact=IMPACT)
SHORE = 62.0                                    # the crest breaks this far in front of the arch (z)
Z0 = float(_K0.R(BREAK)) + SHORE
X0 = 0.0
KIN = WV.Kinematics(SPEED, HEIGHT, CURL, drop=(X0, Z0), t_impact=IMPACT)
HGT = KIN.height                                # the wave's height (H is the frame height)


def wp(u, b, h, t):
    """A place in the wave's own frame at t (see engine/p3d/ten_01_wave.py)."""
    return KIN.point(u, b, h, t)


def crest_z(t):
    return float(KIN.crest_z(t))


def place_where_crest(u, t, b=0.0):
    """The world point on the water (x, 0, z) that the crest reaches at time t, u metres along it."""
    p = KIN.point(u, b, 0.0, t)
    p[1] = 0.0
    return p


# ---- the spark that falls
SPARK_TOP = 2.6


def spark_y(t):
    if t >= IMPACT:
        return 0.0
    return SPARK_TOP * (1.0 - (max(t, -0.5) / IMPACT) ** 2) if t > 0 else SPARK_TOP * (1.0 - (t / IMPACT))


class Spark:
    """The first word: a white gold spark with a comet tail, falling to its own mirror image; on impact a
    crown of droplets of light."""

    def __init__(self, seed=4):
        rng = np.random.default_rng(seed)
        self.h = rng.normal(0.0, 1.0, (500, 3))
        self.tail = rng.random(1400)
        self.tj = rng.normal(0.0, 1.0, (1400, 3))
        n = 2600
        a = rng.uniform(0.0, 2 * np.pi, n)
        sp = rng.uniform(0.8, 3.2, n)
        self.dv = np.stack([np.sin(a) * sp, rng.uniform(1.2, 4.6, n) * (0.5 + 0.5 * (sp / 3.2)), np.cos(a) * sp], 1)
        self.dseed = rng.random(n)
        self.col = lin("#fff4dc")
        self.gold = lin("#ffcf7a")

    def sample(self, t):
        out = []
        c = np.array([X0, spark_y(t), Z0])
        if t < IMPACT + 0.02:
            flare = 1.0 + 1.5 * np.exp(-((t - HIT0) / 0.09) ** 2)
            pos = c + self.h * 0.016
            out.append(dict(pos=pos, size=0.012, color=self.col, alpha=0.8 * flare, kind="soft", emit=3.0,
                            dof=0.4))
            out.append(dict(pos=c[None], size=0.004, color=self.col, alpha=0.8 * flare, kind="spark", emit=1.5,
                            dof=0.4))
            out.append(dict(pos=c[None], size=0.16, color=self.gold, alpha=0.22 * flare, kind="soft", emit=1.5,
                            dof=0.4))
            # the comet tail above it (longer while it falls faster)
            ln = 0.25 + 0.9 * min(t / IMPACT, 1.0) if t > 0 else 0.25
            q = self.tail ** 1.6
            pos = c + np.stack([self.tj[:, 0] * 0.004 * (1 + 4 * q), q * ln, self.tj[:, 2] * 0.004 * (1 + 4 * q)], 1)
            out.append(dict(pos=pos, size=0.008, color=self.gold, alpha=0.5 * (1.0 - q) ** 1.5 * flare,
                            kind="soft", emit=2.0, dof=0.4))
        tt = t - IMPACT
        if 0.0 <= tt < 2.2:
            T = tt * (0.6 + 0.8 * self.dseed)
            pos = np.array([X0, 0.0, Z0]) + self.dv * T[:, None] - np.array([0.0, 4.9, 0.0]) * (T ** 2)[:, None]
            pos[:, 1] = np.maximum(pos[:, 1], 0.0)
            a = np.exp(-tt / 0.7) * (pos[:, 1] > 0.002)
            out.append(dict(pos=pos, size=0.012, color=self.col, alpha=0.8 * a, kind="spark", emit=2.5,
                            seed=self.dseed, twinkle=0.6))
        return out


# ---------------------------------------------------------------------------------------------------------
# THE PEOPLE: where they stand (each where the crest reaches them, or on the crest itself)
# ---------------------------------------------------------------------------------------------------------
T_W1 = 4.70                                     # the crest reaches the first sleeper (Greeting)
W1 = place_where_crest(2.2, T_W1)
M1 = W1 + np.array([-1.4, 0.0, 2.6])            # an older man in the wake behind her (Gratitude)
T_M1 = float(KIN.time_at(M1[0], M1[2]))
FACE_W1_TO_M1 = float(np.degrees(np.arctan2(M1[0] - W1[0], M1[2] - W1[2])))
FACE_M1_TO_W1 = float(np.degrees(np.arctan2(W1[0] - M1[0], W1[2] - M1[2])))
T_PAIR = 15.25                                  # the two in the mist (Apology, then Inclusiveness)
PC = place_where_crest(0.0, T_PAIR)
T_EMBRACE = 17.75
U_DOOR = 25.0                                   # the two in the barrel, before its mouth (Concession)
U_WALK = 33.0                                   # the two seated on the crest (Respect)
U_MAIN = U_WALK                                 # from the barrel on, the camera rides this part of the crest
T_K = 46.75                                     # the kneeling one: the released wall reaches them
KN = place_where_crest(U_MAIN + 0.5, T_K)       # (Encouragement)
HP0 = KN + np.array([2.3, 0.0, -0.4])           # where the one who comes to them starts walking
T_HELP = 35.3                                   # on the crest: one helps another up (Consideration)
T_TWIRL = 47.6                                  # on the crest: a dancer twirls for joy (Compliment)


def walk_frame(t):
    """The top of the crest where the seated pair are (moving ground)."""
    p = wp(U_WALK, 0.15, 0.0, t)
    p[1] = float(HGT(t)) * 0.985
    return p


def crest_frame(u, b=0.25):
    def f(t):
        p = wp(u, b, 0.0, t)
        p[1] = float(HGT(t)) * 0.985
        return p
    return f


def door_frame(t):
    """The floor of the barrel near its mouth: the water inside the tube."""
    p = wp(U_DOOR, -0.62 * float(HGT(t)), 0.0, t)
    p[1] = 0.0
    return p


# ---------------------------------------------------------------------------------------------------------
# THE CAMERA: one unbroken flight. Each move is a function of t in the world (most of them in the wave's
# frame); the rig blends one into the next.
# ---------------------------------------------------------------------------------------------------------
class Path(Move):
    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, g = self.f(t)
        return np.asarray(p, np.float64), np.asarray(g, np.float64)


def cam_drop(t):
    # frame 0: the spark falling down its shaft under the opening title, the sleepers on the glass beyond
    y = spark_y(t)
    return (np.array([X0 + 0.45, 0.36 + 0.62 * y, Z0 + 3.2 - 0.4 * min(max(t, 0.0), 1.0)]),
            np.array([X0, y + 0.72 * max(0.0, 1.0 - max(t, 0.0) / IMPACT) + 0.05, Z0 - 0.5]))


def cam_ride(t):
    # low beside the crest, looking along it: night ahead on the left, the lit wake on the right; then we lift
    # toward the first sleeper as the crest runs at her
    h = 0.30 + 0.9 * float(ss(2.6, 3.9, t))
    pos = wp(-0.9, 0.45, h, t)
    look = wp(7.0, -3.2, 0.15 + 0.4 * float(ss(2.6, 3.9, t)), t)
    her = W1 + np.array([0.0, 1.2, 0.3])
    return pos, lerp(look, her, float(ss(2.9, 3.9, t)))


def cam_face(t):
    # her profile, half figure: the crest sweeps past her feet and she lights up from the feet to the face
    k = float(ss(3.9, 6.84, t))
    pos = W1 + np.array([1.62 - 0.12 * k, 1.36, 0.62 - 0.22 * k])
    return pos, W1 + np.array([0.0, 1.16, 0.46 - 0.1 * k])


def cam_orbit_w1(t):
    # swing out to her side and back: a two-shot in profile, she turns to him and he bows to her with his hand
    # on his heart, and beyond them the crowd the wave has woken bows too
    u = float(ss(6.84, 12.6, t))
    mid = 0.5 * (W1 + M1)
    c = lerp(W1 + np.array([0.0, 1.15, 0.45]), mid + np.array([0.0, 1.05, 0.0]), float(ss(6.84, 8.6, t)))
    a = np.radians(70.0 + 25.0 * u)
    r = lerp(1.75, 4.6, float(ss(6.84, 8.8, t))) + 0.5 * u
    pos = c + np.array([np.sin(a) * r, 0.25 + 0.2 * u, np.cos(a) * r])
    return pos, c


def cam_surge(t):
    # ride behind the crest as it surges into the lanterns, then fall back and stall beside the pair
    ride = wp(0.6, 2.4, 1.25, t), wp(0.0, -14.0, 0.5, t)
    u = float(ss(14.3, 15.6, t))
    w = float(ss(15.4, 19.85, t))
    a = np.radians(14.0 + 50.0 * w)
    r = 4.4 - 1.5 * w
    c = PC + np.array([0.0, 1.15, 0.0])
    orb = c + np.array([np.sin(a) * r, 0.35, np.cos(a) * r]), c
    return lerp(ride[0], orb[0], u), lerp(ride[1], orb[1], u)


U_MOUTH = 36.0


def mouth(t):
    return U_MOUTH


def cam_barrel(t):
    Hh = float(HGT(t))
    k = float(ss(19.9, 20.9, t))                     # through the wall
    ub = 1.5 + 6.6 * max(t - 20.9, 0.0)
    out = wp(0.0, 2.6, 1.6, t), wp(0.0, -12.0, 0.8, t)
    tube = wp(ub, -0.66 * Hh, 0.42 * Hh, t), wp(ub + 14.0, -0.60 * Hh, 0.36 * Hh, t)
    pos, tgt = lerp(out[0], tube[0], k), lerp(out[1], tube[1], k)
    # spat out of the mouth: out ahead of the wave, turning to look back at it
    e = float(ss(25.3, 26.79, t))
    if e > 0.0:
        ex = wp(ub, -5.0 - 2.0 * e, 2.4 + 2.0 * e, t), wp(ub + 3.0, 0.0, 0.6 * Hh, t)
        pos, tgt = lerp(pos, ex[0], e), lerp(tgt, ex[1], e)
    return pos, tgt


def cam_trim(t):
    # one slow revolve round the two seated on the crest while the hills race past
    u = (t - 26.79) / (33.36 - 26.79)
    a = np.radians(-150.0 + 230.0 * float(ss(-0.1, 1.05, u)))
    c = walk_frame(t) + np.array([0.0, 0.75, 0.0])
    r = 3.2
    pos = c + np.array([np.sin(a) * r, 0.55 + 0.35 * np.sin(np.pi * u), np.cos(a) * r])
    return pos, c


def cam_run(t):
    # level with the crest just ahead of it, the two on its top; then rise and pass high over it to see the bay
    # of sleepers ahead light up
    Hh = float(HGT(t))
    k2 = float(ss(37.4, 39.4, t))
    pair = wp(U_MAIN, 0.25, Hh + 0.85, t)
    pos = wp(U_MAIN - 1.0 - 1.5 * k2, -4.9 - 7.0 * k2, Hh + 0.6 + 11.0 * k2, t)
    tgt = lerp(pair, wp(U_MAIN, 7.0, 0.0, t), k2)
    return pos, tgt


def cam_hang(t):
    # behind the kneeling one; the wave crouches low in the breath (the date is written in the sky above it),
    # then rears up into a wall on the hit, and we crane up its face
    c = float(ss(42.65, 46.0, t))
    pos = KN + np.array([0.6 + 0.3 * c, 1.3 + 1.4 * c, -3.5 - 1.2 * c])
    up = float(ss(42.4, 43.4, t))                    # the view lifts with the wall as it rears up
    wall = np.array([KN[0], 2.4 + 2.6 * up + 1.5 * c, crest_z(t)])
    return pos, wall


def cam_drop2(t):
    # the released wall: fly backward before it, rise above its lip, then come over behind the people on it
    Hh = float(HGT(t))
    k1 = float(ss(46.6, 47.5, t))
    k2 = float(ss(47.2, 48.5, t))
    pos = wp(U_MAIN + 1.0, -20.0 + 32.0 * k2, 7.0 + (Hh + 2.5) * k1, t)
    tgt = lerp(wp(U_MAIN, 0.0, (0.5 + 0.4 * k1) * Hh, t), wp(U_MAIN + 1.0, -30.0, Hh * 0.2, t), k2)
    return pos, tgt


END_POS = np.array([2.0, 2.4, 118.0])
END_LOOK = np.array([0.0, 14.0, 0.0])


def cam_break(t):
    # the wave runs out to the horizon and the camera climbs with it: the ring of light races across the
    # whole sea and lights it gold behind it; then the view lifts to the morning sky for the end card
    tb = min(t, BREAK + 0.3)
    Hh = float(HGT(tb))
    start = wp(U_MAIN + 1.0, 12.0, Hh + 9.5, tb)
    c = float(ss(BREAK, 54.6, t))
    h = start[1] + 640.0 * c ** 1.6
    pos = np.array([start[0] * (1.0 - c), h, start[2] - 260.0 * c - 20.0 * max(t - 54.6, 0.0)])
    down = np.array([0.0, -np.tan(np.radians(lerp(14.0, 32.0, float(ss(BREAK, 52.6, t))))), -1.0])
    level = np.array([0.0, np.tan(np.radians(9.0)), -1.0])
    d = lerp(down, level, float(ss(53.2, 55.2, t)))
    return pos, pos + 400.0 * d / np.linalg.norm(d)


CAMERA = Rig([
    Path(cam_drop, 0.0, 1.55, fov=50.0, aperture=0.003, focus=3.2),
    Path(cam_ride, 1.55, 3.9, fov=60.0, aperture=0.004, blend=0.75, focus=4.0),
    Path(cam_face, 3.9, 6.84, fov=42.0, aperture=0.012, blend=1.0, focus=1.7),
    Path(cam_orbit_w1, 6.84, 13.30, fov=48.0, aperture=0.014, blend=1.0),
    Path(cam_surge, 13.30, 19.85, fov=50.0, aperture=0.012, blend=0.8),
    Path(cam_barrel, 19.85, 26.79, fov=lambda t: 52.0 + 18.0 * float(ss(20.35, 21.3, t)), aperture=0.002,
         blend=0.5, focus=6.0),
    Path(cam_trim, 26.79, 33.36, fov=48.0, aperture=0.012, blend=1.1),
    Path(cam_run, 33.36, 40.21, fov=54.0, aperture=0.008, blend=0.6, focus=7.0),
    Path(cam_hang, 40.21, 46.35, fov=56.0, aperture=0.008, blend=1.6, focus=9.0),
    Path(cam_drop2, 46.35, BREAK, fov=62.0, aperture=0.004, blend=0.7, focus=14.0),
    Path(cam_break, BREAK, 60.0, fov=(62.0, 58.0), aperture=0.0, blend=0.8, focus=400.0),
], handheld=0.25, min_height=0.12, near=0.05)

# ---------------------------------------------------------------------------------------------------------
# THE NINE EXPRESSIONS (words.EXPRESSIONS by name; each read for 2.5 s or more). They ride with the camera,
# flat to the picture and in the sky part of it, so every one is whole and sharp while it is read; none has a
# mirror image in the lake; only one is read at a time.
# ---------------------------------------------------------------------------------------------------------


def _fade(t, info):
    """Words leave by fading as their dust streams away, so no frame shows broken letters."""
    w = info["word"]
    if info["state"] == "leave":
        q = (t - w.t_read1) / max(w.t_out - w.t_read1, 1e-6)
        return dict(alpha=float((1.0 - ss(0.0, 0.38, q)) ** 2.0))
    return None


def _ride(x, y, depth, px, t_read0, t_read1, **kw):
    tm = 0.5 * (t_read0 + t_read1)
    return dict(ride=(x, y, depth), em=PW.em_for(CAMERA, tm, depth, px), t_read0=t_read0, t_read1=t_read1,
                face="screen", reflect=False, **kw)


_SPECS = [
    _ride(0.36, 0.76, 6.0, 96, 4.75, 7.25, expr="Greeting", t_in=4.0, t_out=7.95, arrive="pen",
          leave="wind", wind=(1.0, 0.25, 0.4), drive=_fade),
    _ride(0.50, 0.77, 8.0, 80, 8.95, 11.8, expr="Gratitude", t_in=8.0, t_out=12.45, arrive="pen",
          leave="wind", wind=(-1.0, 0.3, 0.2), drive=_fade),
    # the apology, and its answer made of the same light (one reads at a time)
    _ride(0.50, 0.77, 8.0, 84, 14.35, 16.95, expr="Apology", t_in=13.55, t_out=17.0, arrive="reveal",
          edge="right", leave="morph"),
    _ride(0.50, 0.78, 8.0, 96, 17.80, 20.35, expr="Inclusiveness", t_in=16.95, t_out=21.2, arrive="morph",
          source="Apology", leave="wind", wind=(1.0, 0.3, 0.3), drive=_fade),
    _ride(0.50, 0.72, 7.0, 116, 22.0, 24.7, expr="Concession", bright=1.3, t_in=21.2, t_out=25.5, arrive="pen",
          leave="wind", wind=(1.0, 0.1, 0.4), drive=_fade),
    _ride(0.50, 0.77, 9.0, 84, 27.9, 30.6, expr="Respect", t_in=27.0, t_out=31.3, arrive="pen", leave="wind",
          wind=(-1.0, 0.1, 0.6), drive=_fade),
    _ride(0.50, 0.77, 10.0, 84, 34.7, 37.6, expr="Consideration", t_in=33.6, t_out=38.4, arrive="reveal",
          edge="right", leave="wind", wind=(1.0, 0.2, 0.3), drive=_fade),
    # the encouragement over the kneeling one; the compliment over the people on the released wall
    _ride(0.50, 0.70, 14.0, 84, 43.45, 45.95, expr="Encouragement", t_in=42.7, t_out=46.55, arrive="pen",
          leave="wind", wind=(0.3, 1.0, 0.2), drive=_fade),
    _ride(0.50, 0.77, 12.0, 92, 47.15, 49.65, expr="Compliment", t_in=46.45, t_out=50.4, arrive="pen",
          bright=1.3, leave="wind", wind=(1.0, 0.4, 0.2), drive=_fade),
]
WORDS = PW.Words(_SPECS, camera=CAMERA)

# ---------------------------------------------------------------------------------------------------------
# TITLE AND DATE (UPDATE 7): the opening title over the spark drop, a discreet signature in two calm stretches
# between expressions, "December 6" written in light across the sky in the breath and burst on the biggest
# hit (the wave rears up and carries the burst). Drawn by the engine's TITLES once it lands.
# ---------------------------------------------------------------------------------------------------------
TITLES = dict(
    opening=dict(t_end=4.0, y=0.30, palette="night"),
    signature=dict(windows=[(12.45, 13.35, "tr", "night"), (31.3, 33.4, "tr", "night")]),
    date_light=dict(t_form=39.45, t_burst=BIG, y=0.27, palette="night"),
    end_card=dict(t_in=55.0),
)
T_TITLE = 55.0                                  # the end card (the engine's, from TITLES) from here to the end

# the arch of nine lights stands over the shore; a light wakes as each expression is whole; its arc and links
# are drawn only once the wave has broken (seen from far away they made a ring with their mirror image)
ARCH = dict(span=74.0, height=42.0, z=0.0, bright=1.4, line=lambda t: float(0.8 * ss(BREAK + 0.5, 53.5, t)))
_LIT = [WORDS[lab].t_read0 for lab in PW.LABELS]


# ---------------------------------------------------------------------------------------------------------
# THE SCENE
# ---------------------------------------------------------------------------------------------------------
def _glow(t):
    # the near crest gives way to the whole ring as we climb; the ring fades under the end card
    return float(1.0 - ss(51.0, 53.0, t))


def _plume(t):
    return 0.0


def _lanterns(rng):
    n = 900
    ts = rng.uniform(13.4, 19.6, n)
    u = rng.normal(0.0, 1.0, n) * 16.0 + rng.uniform(-40, 40, n) * (rng.random(n) < 0.35)
    pts = np.array([place_where_crest(uu, tt) for uu, tt in zip(u, ts)])
    keep = np.hypot(pts[:, 0] - PC[0], pts[:, 2] - PC[2]) > 1.6           # clear round the pair
    pts = pts[keep]
    pts[:, 1] = 0.06
    m = len(pts)
    flame = pts + np.array([0.0, 0.1, 0.0])
    cols = np.where(rng.random(m)[:, None] < 0.5, lin("#ffb45e"), lin("#ff8a3c"))
    gain = lambda t: float(1.0 - ss(26.0, 28.0, t))   # noqa: E731
    return (WV.Field(KIN, pts, 0.22, cols, alpha=0.5, kind="soft", delay=rng.uniform(0.0, 0.5, m), flash=2.5,
                     fade=0.5, twinkle=0.3, gain=gain),
            WV.Field(KIN, flame, 0.03, lin("#fff0c8"), alpha=0.9, kind="spark", delay=rng.uniform(0.0, 0.5, m),
                     flash=3.0, fade=0.3, twinkle=0.8, emit=2.0, gain=gain))


def _wake(rng):
    """Glints on the water where the crest has passed: a floor of gold behind the wave, sparse near the lens."""
    n = 200000
    z = rng.uniform(crest_z(BREAK + 0.5), Z0 - 0.3, n)
    x = rng.laplace(0.0, 16.0, n) + np.where(rng.random(n) < 0.5, 0.0, float(wp(U_MAIN, 0.0, 0.0, 30.0)[0]))
    pos = np.stack([x, np.full(n, 0.01), z], 1)
    r = np.hypot(x - X0, z - Z0)
    pos = pos[r > 0.6]
    m = len(pos)
    cols = lin("#ffb84a") * (0.6 + 0.8 * rng.random(m))[:, None]
    return WV.Field(KIN, pos, 0.016, cols, alpha=0.13, kind="spark", delay=rng.uniform(0.0, 0.3, m), flash=2.4,
                    fade=0.2, twinkle=0.9, emit=1.2, reflect=False, gain=lambda t: 1.0 - 0.8 * ss(BREAK, 54.0, t))


def _ridges(rng):
    """Two headlands of the strait: thin lines of light race up the spurs of their dark slopes as the crest
    passes below, like dawn catching ridges. They fade once the strait is behind us."""
    pts = []
    xc = float(wp(U_MAIN, 0.0, 0.0, 30.0)[0])
    for side in (-1.0, 1.0):
        for k in range(22):
            z0 = crest_z(26.4 + 0.33 * k + rng.uniform(0, 0.25))
            x_foot = xc + side * rng.uniform(55.0, 68.0)
            top = rng.uniform(24.0, 44.0)
            run = rng.uniform(45.0, 70.0)
            n = 2200
            s = np.sort(rng.random(n))
            wig = 3.0 * np.sin(s * rng.uniform(4.0, 8.0) + k) * s
            x = x_foot + side * s * run
            y = top * np.sin(np.pi * 0.5 * s) ** 0.8
            z = z0 + wig - 10.0 * s + rng.normal(0.0, 0.12, n)
            pts.append(np.stack([x + rng.normal(0.0, 0.12, n), y + rng.normal(0.0, 0.08, n), z], 1))
    pts = np.concatenate(pts)
    delay = pts[:, 1] / 18.0 + 0.2
    return WV.Field(KIN, pts, 0.10, lin("#ffb060"), alpha=0.6, kind="spark", delay=delay, flash=3.0,
                    fade=0.25, twinkle=0.7, emit=1.5,
                    gain=lambda t: float(1.0 - ss(33.6, 35.2, t)))


HEROES = []                                     # where the hero bodies stand: the crowds keep clear of them


def _people(rng, baked, name, n, t0, t1, u_mid, u_spread, near=None, gain=None, poses=("stand",), yaw=None,
            min_gap=0.9, scale=(0.9, 1.1), avoid=None, dynamic=True):
    """People asleep on the water where the wave will pass, at many depths, some close to the camera's path:
    cold sparse blue dust until the crest reaches them, then they form out of gold light from the feet up."""
    feet, chosen = [], []
    tries = 0
    while len(feet) < n and tries < n * 30:
        tries += 1
        tc = rng.uniform(t0, t1)
        if near is not None and rng.random() < near[0]:
            u = near[1] + rng.uniform(-near[2], near[2])
        else:
            u = u_mid + rng.normal(0.0, u_spread)
        if avoid is not None and avoid[0] < u < avoid[1]:
            continue
        p = place_where_crest(u, tc)
        if any(np.hypot(p[0] - q[0], p[2] - q[2]) < 1.4 for q in HEROES):
            continue
        if any(np.hypot(p[0] - q[0], p[2] - q[2]) < min_gap for q in feet):
            continue
        feet.append(p)
        chosen.append(tc)
    warm, delay, cols = [], [], []
    palette = [lin(c) for c in ("#ffd9a0", "#ffc070", "#ffe6c0", "#ffb868", "#ffd0b0")]
    for m, p0 in enumerate(feet):
        shape = baked[rng.integers(0, len(baked))]
        pose = poses[rng.integers(0, len(poses))]
        pts = shape[pose] if pose in shape else shape["stand"]
        keep = pts[:: (1 if near is not None and m % 3 == 0 else 2)]
        a = rng.uniform(0, 2 * np.pi) if yaw is None else np.radians(yaw(rng))
        cy, sy = np.cos(a), np.sin(a)
        q = np.stack([keep[:, 0] * cy + keep[:, 2] * sy, keep[:, 1], -keep[:, 0] * sy + keep[:, 2] * cy], 1)
        q = q * rng.uniform(*scale) + p0
        warm.append(q)
        delay.append(keep[:, 1] * 0.42 + rng.uniform(0.0, 0.25) + rng.normal(0.0, 0.03, len(keep)))
        cols.append(np.broadcast_to(palette[rng.integers(0, len(palette))] * rng.uniform(0.8, 1.15), q.shape))
    warm = np.concatenate(warm)
    delay = np.concatenate(delay)
    cols = np.concatenate(cols)
    cold = warm[::3]
    cold_set = WV.Static(dict(pos=cold, size=0.016, color=lin("#86a2ff") * 0.45, alpha=0.38, kind="spark",
                              twinkle=0.5), gain=gain, static=not dynamic)
    warm_set = WV.Field(KIN, warm, 0.017, cols, alpha=0.6, kind="spark", delay=delay, flash=3.2, fade=0.35,
                        twinkle=0.6, emit=1.3, gain=gain, static=not dynamic)
    return [(name + "_cold", cold_set), (name + "_warm", warm_set)]


def _crest_line(rng, baked):
    """The people the wave carries: a ragged line along the crest (two or three deep, all heights), backs to
    us, lifting their arms in a wave that runs along it; after the break, set down on the water by the shore."""
    us, bs = [], []
    u = U_MAIN - 95.0
    while u < U_MAIN + 95.0:
        u += rng.uniform(0.6, 2.1)
        us.append(u)
        bs.append(rng.choice([0.4, 0.4, 1.5, 2.6]) + rng.uniform(-0.3, 0.3))
    places = np.stack([us, bs], 1)
    shapes = []
    for sh in baked:
        stand = sh["stand"][::3]
        up = sh["raise"][::3]
        m = min(len(stand), len(up))
        shapes.append((stand[:m], up[:m]))

    def place(uu, bb, t):
        tb = min(t, BREAK + 0.5)
        k = float(ss(BREAK, 51.6, t))
        h = float(HGT(min(t, BREAK))) * (1.0 - k) * 0.97
        p = KIN.world(uu, bb, np.zeros_like(uu), tb)
        p[:, 1] = h
        return p
    return WV.Crowd(shapes, places, place, ["#ffd9a0", "#ffc070", "#ffe6c0", "#ffcf90"], t_lift=47.9,
                    lift_speed=50.0, alpha=0.6, size=0.02, show=(46.4, 60.1), center=U_MAIN,
                    gain=lambda t: float(ss(46.5, 47.3, t) * (1.0 - ss(51.5, 52.5, t))))


# the website's expression colours (UPDATE 9), for the hearts that drift off each act; the compliment's navy is
# lifted toward white so that it shows as light on the night sky
HEX = dict(Greeting="#EA5A5E", Gratitude="#F2B25E", Apology="#F6CE46", Inclusiveness="#5ABA5A",
           Concession="#62B2FA", Respect="#667AF6", Encouragement="#9E6AF6", Consideration="#EE62A6",
           Compliment="#7f93d6")


def C(ps, pad=0.9):
    """A point set that keeps clear of every expression being read."""
    return WV.Clear(ps, WORDS, None, pad=pad)


def _add_body(scene, name, body, ignite=None, rise=0.9, mask=None):
    """A body of light, kept clear of the words (and with the mask its look needs, if any)."""
    ps = WV.Ignite(body, ignite, rise=rise) if ignite is not None else body
    m = body.mask(**(mask or {})) if mask is not False else None
    scene.add(name, C(ps), mask=m)


def _performances(scene):
    """THE ACTING: each expression is done by the people the crest has just woken, in its own style."""
    # 1 GREETING: a face lighting up. A woman asleep on the black glass, seen in profile at half figure, in
    # white gold glitter; the crest sweeps past her feet, the light climbs her to the face, she lifts her head
    # toward the light and waves one hand in greeting.
    w1 = Body("woman", at=(W1[0], W1[2]), facing=[(0.0, 180.0), (7.3, 180.0), (8.6, FACE_W1_TO_M1)],
              garment="dress", hair=True, look=dict(name="glitter", bright=1.15), color="#fff0d2", color2="#ffd890",
              points=90000, detail=dict(head=3, hand=3), show=(2.2, 14.2), fade=0.5,
              gesture=[(4.9, 7.4, "look_up", dict(amount=16)), (5.3, 7.6, "wave", dict(side="L")),
                       (8.8, 13.6, "offer", dict(side="L"))],
              effects=[dict(kind="shed", t=4.8, n=6000, life=2.2, where="back", dir=(0.0, 0.35, 1.0), speed=0.55)],
              seed=3)
    _add_body(scene, "greeting", w1, ignite=T_W1, rise=1.1)
    hearts = [WV.Hearts(lambda t: w1.where(t, "palm.L"), 5.4, 7.2, HEX["Greeting"], n=8, rise=0.3)]

    # 2 GRATITUDE: an older man in the wake bows to her with his hand on his heart (gold glitter, p08), and
    # behind him a whole crowd woken by the wave bows too.
    refs = {}
    m1 = Body("man", at=(M1[0], M1[2]), facing=FACE_M1_TO_W1, garment="coat", stoop=0.25, look="glitter",
              color="#ffc77a", color2="#fff0cc", points=70000, show=(4.0, 14.2), fade=0.5, seed=4,
              gesture=[(8.4, 13.8, "touch", dict(side="R", to=lambda t: refs["m1"].where(t, "heart", raw=True),
                                                  palm="in", fingers="flat")),
                       (8.7, 13.8, "bow", dict(amount=34))])
    refs["m1"] = m1
    _add_body(scene, "gratitude", m1, ignite=T_M1)
    hearts.append(WV.Hearts(lambda t: m1.where(t, "heart"), 9.0, 11.8, HEX["Gratitude"], n=10))
    rng = np.random.default_rng(5)
    pts, starts = [], []
    while len(pts) < 70:
        x = W1[0] + rng.uniform(-24.0, 24.0)
        z = W1[2] + rng.uniform(4.5, 38.0)
        if np.hypot(x - M1[0], z - M1[2]) < 1.5 or any(np.hypot(x - q[0], z - q[1]) < 1.2 for q in pts):
            continue
        pts.append((x, z))
        starts.append(float(KIN.time_at(x, z)))
    from p3d.crowd import Crowd
    crowd = Crowd(places=np.array(pts), facing=np.array([180.0 + rng.normal(0.0, 12.0) for _ in pts]),
                  kinds=(("bow", 3), ("stand", 1)), start=np.array(starts), until=15.0, fade=0.5, flash=0.9,
                  points=2600, color="#ffc977", color2="#fff0d0", seed=2.0)
    scene.add("bowing", C(crowd))

    # 3 APOLOGY then 4 INCLUSIVENESS: two people in the mist among the lanterns (soft figures of pearl and rose
    # dust, p09). One stands with head bowed and open hands low; the other has turned away. Then the other
    # turns, they walk in and hold each other; a warm flare where they meet.
    # (pairs.embrace measures the walk in from t = 0 when the walk starts late, which put them 30 m apart;
    # here each is placed by its own walk with a standing start, and pairs.embrace only adds the hold)
    from p3d import actor as act
    keys_in = [(0.0, "stand"), (T_EMBRACE - 0.15 - 1.1, "walk", dict(speed=0.9)),
               (T_EMBRACE - 0.6, "stand", dict(blend=0.9))]
    walked = {sh: float(act.Actor(sh, None, at=(0.0, 0.0), facing=0.0, motion=keys_in).travel(T_EMBRACE + 1.5)[0])
              for sh in ("man", "woman")}
    a_at = PC + np.array([-(0.17 + walked["man"]), 0.0, 0.0])
    b_at = PC + np.array([0.17 + walked["woman"], 0.0, 0.0])
    a, b = pairs.embrace(T_EMBRACE, at=(PC[0], PC[2]), facing=90.0, approach=0.0, until=21.5,
                         a=dict(shape="man", garment="tunic", look=dict(name="glitter", bright=0.85),
                                at=(a_at[0], a_at[2]), motion=keys_in,
                                color="#ffe6cf", color2="#ffffff", points=60000, show=(12.6, 21.4), fade=0.5,
                                gesture=[(15.5, 16.75, "bow", dict(amount=26)), (15.6, 16.75, "offer"),
                                         (15.6, 16.75, "offer", dict(side="L"))],
                                effects=[dict(kind="shed", t=15.3, n=5000, life=3.0, where="top", dir=(0, 1, 0),
                                              speed=0.18)], seed=5),
                         b=dict(shape="woman", garment="robe", look=dict(name="glitter", bright=0.85),
                                at=(b_at[0], b_at[2]), motion=keys_in,
                                color="#ffb8c8", color2="#fff0f4", points=60000, show=(12.6, 21.4), fade=0.5,
                                facing=[(0.0, 90.0), (15.9, 90.0), (16.5, 270.0)],
                                effects=[dict(kind="shed", t=15.3, n=5000, life=3.0, where="top", dir=(0, 1, 0),
                                              speed=0.18)], seed=6))
    _add_body(scene, "apology_a", a, ignite=T_PAIR)
    _add_body(scene, "apology_b", b, ignite=T_PAIR + 0.1)
    hearts.append(WV.Hearts(lambda t: a.where(t, "heart"), 15.4, 16.9, HEX["Apology"], n=5, size=(0.08, 0.15)))
    hearts.append(WV.Hearts(lambda t: 0.5 * (a.where(t, "heart") + b.where(t, "heart")), 17.9, 20.3,
                            HEX["Inclusiveness"], n=12))
    scene.add("embrace_flare", C(fx.Flare(lambda t: np.array([PC[0], 1.35, PC[2]]), T_EMBRACE + 0.15,
                                          color="#ffd6b0", color2="#ffb0c8", scale=1.6, strength=0.8)))

    # 5 CONCESSION: in the barrel, before its mouth (a door of light): one steps aside with an open palm toward
    # the door and lets the other go through first. Constellation wireframes (p01) in the tunnel of streaks.
    for name, shape, at, facing, motion, gest, seed in (
            ("concession_a", "man", (0.0, 0.55), [(0.0, 90.0), (21.6, 90.0), (22.3, 180.0)], "stand",
             [(22.2, 26.5, "offer", dict(side="L")), (22.2, 26.5, "bow", dict(amount=12))], 7),
            ("concession_b", "woman", (-0.3, -0.35), 90.0,
             [(0.0, "stand"), (22.9, "walk", dict(speed=1.0))], [], 8)):
        body = Body(shape, at=at, facing=facing, motion=motion, gesture=gest, frame=door_frame,
                    look=dict(name="glitter", bright=1.25), color="#e4f2ff", color2="#ffffff", points=60000,
                    show=(20.2, 26.9), fade=0.4, effects=[dict(kind="form", t=20.5, dur=1.4)], seed=seed)
        _add_body(scene, name, body)
        if name == "concession_a":
            hearts.append(WV.Hearts(lambda t, bd=body: bd.where(t, "palm.L"), 22.3, 24.6, HEX["Concession"], n=8))

    # 6 RESPECT: two people seated on the crest of the moving wave; one speaks with small open hands, the other
    # leans in and listens. Constellations of points and fine lines (p01).
    for name, shape, at, facing, gest, seed in (
            ("respect_a", "woman", (-0.42, 0.0), 90.0,
             [(27.5, 29.4, "offer", dict(side="R")), (29.2, 33.6, "offer", dict(side="L"))], 9),
            ("respect_b", "man", (0.42, 0.0), 270.0, [(27.4, 33.6, "listen", dict(side="R"))], 10)):
        body = Body(shape, at=at, facing=facing, motion=[(0.0, "sit", dict(dur=0.01))], gesture=gest,
                    frame=walk_frame, look=dict(name="plexus", bright=1.3), color="#fff2dc", color2="#c8d2ff",
                    points=60000, show=(26.2, 33.9), fade=0.5, effects=[dict(kind="form", t=26.4, dur=1.2)],
                    seed=seed)
        _add_body(scene, name, body)
        if name == "respect_b":
            hearts.append(WV.Hearts(lambda t, bd=body: bd.where(t, "head"), 28.2, 30.5, HEX["Respect"], n=8))

    # 7 CONSIDERATION: on the crest, one reaches down to someone kneeling, takes their hand and pulls them up;
    # the one helped up lays a hand on the helper's shoulder. Coloured dots (ref 14).
    ha, hb = pairs.helped_up(T_HELP, at=(0.0, 0.0), facing=90.0,
                             a=dict(shape="man", garment="coat", frame=crest_frame(U_MAIN, 0.25), look="dots",
                                    color="#ffcf8a", color2="#ff9f8a", points=60000, show=(32.9, 40.4), fade=0.5,
                                    effects=[dict(kind="form", t=33.2, dur=1.2)], seed=11),
                             b=dict(shape="woman", garment="dress", frame=crest_frame(U_MAIN, 0.25), look="dots",
                                    color="#ffd9a0", color2="#ef7a96", points=60000, show=(32.9, 40.4), fade=0.5,
                                    effects=[dict(kind="form", t=33.2, dur=1.2)], seed=12))
    _add_body(scene, "consider_a", ha)
    _add_body(scene, "consider_b", hb)
    hearts.append(WV.Hearts(lambda t: ha.where(t, "palm.R"), 35.6, 37.6, HEX["Consideration"], n=10))

    # 8 ENCOURAGEMENT: one kneels in prayer before the standing wall; another walks to them and lays a hand on
    # their shoulder. White gold, light rising off them like flakes (ref 13).
    kn = Body("man", at=(KN[0], KN[2]), facing=0.0, motion=[(0.0, "kneel", dict(hands="pray", dur=0.01))],
              garment="tunic", look="glitter", color="#fff0d0", color2="#ffd890", points=65000,
              show=(39.0, 48.2), fade=0.5, seed=13,
              effects=[dict(kind="shed", t=39.2, n=4000, life=2.0, where="top", dir=(0, 1, 0), speed=0.25)])
    face_in = float(np.degrees(np.arctan2(KN[0] - HP0[0], KN[2] - HP0[2])))
    hp = Body("woman", at=(HP0[0], HP0[2]), facing=[(0.0, face_in), (42.6, face_in), (43.2, face_in + 60.0)],
              motion=[(0.0, "stand"), (40.9, "walk", dict(speed=0.95)), (42.45, "stand", dict(blend=0.8))],
              garment="robe", look="glitter", color="#ffe6b0", color2="#fff6e0", points=65000,
              show=(39.0, 48.2), fade=0.5, seed=14,
              gesture=[(42.7, 48.0, "hand_on_shoulder", dict(side="R", to=lambda t: kn.where(t, "shoulder.R")))],
              effects=[dict(kind="shed", t=39.2, n=3000, life=2.0, where="top", dir=(0, 1, 0), speed=0.25)])
    _add_body(scene, "encourage_k", kn)
    _add_body(scene, "encourage_h", hp)
    hearts.append(WV.Hearts(lambda t: kn.where(t, "chest"), 43.7, 45.9, HEX["Encouragement"], n=10))

    # 9 COMPLIMENT: the people the wave carries cheer (arms flung up in a wave along the crest), and at their
    # front a dancer twirls in joy, sparks streaming off her dress (warm, luminous and whole).
    tw = Body("woman", at=(0.0, 0.0), facing=180.0, frame=crest_frame(U_MAIN + 1.2, -0.6),
              motion=[(0.0, "stand"), (T_TWIRL, "twirl")], garment="dress", hair=True, look="glitter",
              color="#ffb070", color2="#ffe0b0", points=60000, show=(46.4, 50.6), fade=0.4, seed=15,
              gesture=[(46.6, T_TWIRL + 0.2, "open_arms", dict(lift=0.6))],
              effects=[dict(kind="shed", t=T_TWIRL, n=7000, life=1.6, where="back", dir=(0.4, 0.5, 1.0), speed=0.9)])
    _add_body(scene, "compliment", tw)
    hearts.append(WV.Hearts(lambda t: tw.where(t, "chest"), 47.3, 49.6, HEX["Compliment"], n=14))
    for k, h in enumerate(hearts):
        scene.add(f"hearts{k}", C(h))


def _setup(scene):
    rng = np.random.default_rng(21)
    scene.add("wave", C(WV.Wave(KIN, glow=_glow, mouth=mouth, plume=_plume, centers=(0.0, U_MAIN)), pad=1.6))
    scene.add("tube", C(WV.Tube(KIN, -2.0, U_MOUTH + 10.0, n=70000, mouth=mouth,
                                gain=lambda t: float(ss(19.9, 20.8, t) * (1.0 - ss(25.8, 26.7, t))
                                                     * (1.0 - 0.45 * ss(21.4, 22.0, t) * (1.0 - ss(24.7, 25.3, t))))),
                        pad=1.6))
    scene.add("spark", C(Spark()))
    scene.add("wake", _wake(rng), reflect=False)
    lan, flame = _lanterns(rng)
    scene.add("lanterns", lan)
    scene.add("lantern_flames", flame)
    baked = WV.bake_people(Body, n=2600, poses=("stand", "raise", "open_arms", "look_up"))
    HEROES.extend([W1, M1, PC, KN, HP0])
    # people asleep all over the black glass: each forms out of gold light as the crest reaches them, and the
    # people the wave carries stand on its crest at the end and are set down on the shore
    for name, args in (
            ("s1", dict(n=30, t0=1.6, t1=7.2, u_mid=2.0, u_spread=10.0, near=(0.25, 6.0, 2.5), avoid=(-2.2, 4.0),
                        gain=lambda t: float(1.0 - ss(13.6, 14.6, t)), yaw=lambda r: r.choice([180.0, 150.0, 210.0, 90.0, -90.0]) + r.normal(0.0, 12.0))),
            ("s3", dict(n=30, t0=13.4, t1=19.8, u_mid=0.0, u_spread=11.0, near=(0.25, 5.0, 2.5), avoid=(-3.0, 3.0),
                        gain=lambda t: float(ss(11.0, 12.5, t) * (1.0 - ss(22.0, 23.0, t))),
                        poses=("stand", "look_up"))),
            ("s6", dict(n=170, t0=33.5, t1=40.2, u_mid=U_MAIN, u_spread=12.0, near=(0.25, U_MAIN - 6.0, 2.5),
                        avoid=(U_MAIN - 4.8, U_MAIN + 2.0),
                        gain=lambda t: float(ss(32.4, 33.4, t) * (1.0 - ss(40.6, 41.6, t))),
                        poses=("stand", "stand", "look_up", "open_arms"), dynamic=False)),
            ("s8", dict(n=60, t0=49.7, t1=52.5, u_mid=U_MAIN - 20.0, u_spread=22.0, min_gap=1.3,
                        gain=lambda t: float(ss(48.5, 49.5, t) * (1.0 - ss(51.5, 52.5, t))),
                        yaw=lambda r: 180.0 + r.normal(0.0, 15.0),
                        poses=("stand", "raise", "open_arms"), dynamic=False))):
        for nm, st in _people(rng, baked, name, **args):
            scene.add(nm, st if st.static else C(st))
    scene.add("crest_line", C(_crest_line(rng, baked)))
    # the finale: the whole ring, and the whole sea lit gold behind it, seen from high above
    scene.add("far_ring", WV.FarRing(KIN, n=60000, gain=lambda t: float(ss(50.0, 51.4, t) * (1.0 - ss(55.0, 57.5, t)))))
    sea = WV.disc_glints(KIN, 5200.0, 220000, rng, r_min=60.0)
    scene.add("sea_lights", WV.Field(KIN, sea, 2.6, lin("#ffc066"), alpha=0.35, kind="spark", delay=0.0, flash=3.0,
                                     fade=0.4, twinkle=0.7, emit=1.4, reflect=False,
                                     gain=lambda t: float(ss(49.8, 51.2, t) * (1.0 - 0.5 * ss(55.0, 58.0, t)))))
    _performances(scene)

    WORDS.add_to(scene)
    try:
        WORDS.check(CAMERA)
    except Exception as e:                       # the check is advice; never stop a render for it
        print("words check failed:", e)


P3D = dict(
    camera=CAMERA,
    world=WORDS.world(dict(
        look=[(0.0, "night"), (BREAK + 0.9, "warmrise", 1.8), (52.2, "golden2", 1.6), (53.7, "cream", 1.6)],
        looks=dict(warmrise=dict(base="sunrise", sun_int=0.55, rays=0.40, exposure=0.82, sun_glow=0.6, sun_disc=5.0),
                   golden2=dict(base="golden", sun_int=0.6, rays=0.25, exposure=0.9)),
        sun_az=180.0,
        keep_hue=0.6,
        shore=2400.0,
        split=dict(look="dawn", toward=0.0, soft=0.4,
                   amount=lambda t: float(0.15 + 0.85 * ss(2.5, 12.0, t)) * float(1.0 - ss(BREAK, 51.5, t))),
        ripple=lambda t: float(0.18 + 0.4 * ss(8.0, 20.0, t)),
        mirror=1.0,
        stars=lambda t: float(1.0 - ss(BREAK, 52.5, t)),
        milky=lambda t: float(0.8 * (1.0 - ss(BREAK, 51.5, t))),
        mist=0.22,
        dust=0.25,
        bokeh=0.35,
        shafts=[dict(base=(X0, Z0), radius=0.07, top=60.0, spread=0.01, color="#fff1d0",
                     strength=lambda t: float(0.35 * (1.0 - ss(IMPACT, IMPACT + 1.2, t))))],
        lights=[dict(pos=lambda t: wp(0.0 if t < 20.0 else U_MAIN, 0.3, 0.6 * float(HGT(t)) + 0.3, t),
                     color="#ffc060", strength=lambda t: float(0.0 if t < IMPACT else 0.14 * (1.0 - ss(12.0, 14.0, t))),
                     radius=lambda t: 1.5 + 0.6 * float(HGT(t)))],
        arch=dict(lit=_LIT, **ARCH),
        react=dict(beat=0.4, level=0.3),
    )),
    bursts=[dict(t=HIT0, strength=0.25, at=(X0, spark_y(HIT0), Z0), radius=0.04, rise=0.04, fall=0.3,
                 color="#ffe9c4"),
            dict(t=IMPACT, strength=0.55, at=(X0, 0.05, Z0), radius=0.07, rise=0.05, fall=0.5, color="#ffe2b0"),
            dict(t=19.80, strength=0.45, at=(float(PC[0]), 1.3, float(PC[2])), radius=0.07, rise=0.05, fall=0.45,
                 color="#ffd9a8"),
            dict(t=20.55, strength=0.55, radius=0.3, rise=0.12, fall=0.5, color="#ffd49a")],
    setup=_setup,
)



if __name__ == "__main__":
    print("Z0", Z0, "crest at break", crest_z(BREAK))
    for t in (1.0, 2.0, 6.0, 13.3, 19.85, 26.79, 33.36, 40.21, 42.5, 46.4, BREAK):
        print(t, "R", round(float(KIN.R(t)), 1), "H", round(float(HGT(t)), 2), "speed", CAMERA.speed(t))
    WORDS.check(CAMERA)
