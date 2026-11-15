"""Film 01 of ten: THE WAVE (60 seconds, a promo for The Words of Mother's Love Healing Concert).

LOGLINE
  One word falls into a sleeping black sea and becomes the edge of morning. In one unbroken flight we ride
  that wave of light as it wakes everyone it touches, grows with each of the nine Words of Mother's Love, and
  breaks on the far shore as the sunrise.

THE RULES OF THIS FILM
  1. One shot, no cuts: the camera always travels with the wave (surfing language: drop in, cutback, stall,
     barrel, trim, hang, big drop, break), fast on the section starts, slower round the people.
  2. The wave is the edge of morning: night and black glass ahead, glittering water and dawn behind.
  3. The wave grows: a ripple a hand high at 1 s, a wall of light 26 m high at 43 s.
  4. Whoever the wave touches wakes: cold blue dust lights gold from the feet up.
  5. Gold only. The nine campaign colours tint each expression's glow, never the wave.
  6. No Heavenly Mother figure: the first word falls from above down a thin shaft of light; the morning at
     the end is hers; the title says whose words these are.

THE TIMELINE (the medley's sections: 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 (breath to 42.51), 49.47)
  S1  0.00  THE DROP.  A spark falls down a thin shaft toward its mirror image in a black sea of stars; it
            flares on the opening hit and strikes the water at 0.97. A ring races out at the lens; a whip
            pan and we ride beside a rope of light a hand high. GREETING rises out of the foam. The first
            sleeper ahead; the crest reaches her feet and she lights gold from the feet up.
  S2  6.84  THE CUTBACK.  We swing round her and look back for the first time: lit water and dawn behind.
            An older man wakes beside her. GRATITUDE above the two.
  S3 13.30  THE STALL.  Whip forward, the wave surges into a field of lanterns that catch in a sweep. We stall
            beside two people who stood back to back; they turn to each other. APOLOGY, then its answer,
            INCLUSIVENESS. They reach for each other.
  S4 19.85  THE BARREL.  The bass slams in, the wave rears up and folds over; we punch through the wall into
            a tunnel of light and glide down it. CONCESSION hangs in the tube; it rushes past us as we are
            spat out of the mouth.
  S5 26.79  THE TRIM.  The wave runs into a strait: lines of light race up the dark hills on both sides. We
            revolve round two people of light who walk along the crest. RESPECT.
  S6 33.36  THE RUN.  The wave doubles its speed over a bay full of sleepers; we fly backward ahead of it,
            then rise over the crest and watch it light them row after row. CONSIDERATION.
  S7 40.21  THE HANG.  The music breathes: the wave slows and stands up into a wall of light, and stops for one
            person kneeling on the water. Someone lays a hand on the kneeling shoulder. On the biggest hit
            (42.51) ENCOURAGEMENT surfaces across the wall and we crane up it. The wall is released; we
            climb over its lip: a line of people of light rides the crest, backs to us, and lifts its arms
            in a wave. COMPLIMENT.
  S8 49.47  THE BREAK.  The wave breaks on the shore under the arch of nine lights: a plume of gold, the sun
            tears through, the night is swept off the sky. The people stand on the shore; the end card.
            No fade: the last frame is full daylight.

Rules kept: no lyrics, no faces (the bodies are featureless), everyone clothed in garments of light, no
Heavenly Mother figure, all nine expressions from words.EXPRESSIONS, nothing dark behind any text, no em dash
or en dash, the first frame is a picture, the last frame is daylight.
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
         (42.4, 1.0), (42.6, 2.5), (46.05, 2.0), (46.6, 30.0), (49.3, 34.0), (BREAK, 30.0), (50.6, 6.0),
         (60.0, 2.0)]
HEIGHT = [(0.0, 0.0), (IMPACT, 0.02), (1.4, 0.14), (6.0, 0.24), (6.84, 0.40), (12.8, 0.55), (13.6, 1.0),
          (19.3, 1.25), (19.85, 1.6), (20.9, 4.2), (26.0, 4.4), (27.3, 5.6), (33.0, 6.6), (33.9, 8.0),
          (39.8, 9.0), (40.4, 11.0), (42.3, 24.0), (46.0, 26.0), (46.8, 18.0), (BREAK, 14.0), (50.4, 6.0),
          (52.0, 1.2), (60.0, 0.6)]
CURL = [(0.0, 0.0), (19.85, 0.0), (20.9, 1.0), (25.2, 1.0), (26.6, 0.0), (45.9, 0.0), (46.6, 0.25),
        (47.4, 0.0), (BREAK - 0.3, 0.0), (50.1, 0.9), (51.2, 1.0), (60.0, 1.0)]
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
            flare = 1.0 + 3.0 * np.exp(-((t - HIT0) / 0.09) ** 2)
            pos = c + self.h * 0.016
            out.append(dict(pos=pos, size=0.014, color=self.col, alpha=0.9 * flare, kind="spark", emit=4.0,
                            dof=0.4))
            out.append(dict(pos=c[None], size=0.22, color=self.gold, alpha=0.35 * flare, kind="soft", emit=2.0,
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
T_W1 = 6.45                                     # the first sleeper (a woman) is reached
W1 = place_where_crest(1.1, T_W1)
M1 = W1 + np.array([-2.3, 0.0, 1.9])            # an older man, a little behind her (reached a moment before)
T_M1 = float(KIN.time_at(M1[0], M1[2]))
T_PAIR = 15.25                                  # the two who stood back to back
PC = place_where_crest(0.0, T_PAIR)
P1 = PC + np.array([-0.42, 0.0, 0.0])
P2 = PC + np.array([0.42, 0.0, 0.0])
U_WALK = 33.0                                   # the walkers on the crest (where the barrel let us out)
U_MAIN = U_WALK                                 # from the barrel on, the camera rides this part of the crest
T_K = 46.75                                     # the kneeling one: the released wall reaches them
KN = place_where_crest(U_MAIN + 0.5, T_K)
HP = KN + np.array([-0.62, 0.0, 0.22])          # the one who lays a hand on their shoulder


def walk_frame(t):
    p = wp(U_WALK, 0.15, 0.0, t)
    p[1] = float(HGT(t)) * 0.985
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
    # frame 0: the spark falling down its shaft, the sleepers far out on the black glass behind it
    y = spark_y(t)
    return (np.array([X0 + 0.45, 0.36 + 0.62 * y, Z0 + 3.2 - 0.4 * min(max(t, 0.0), 1.0)]),
            np.array([X0, y + 0.55 * max(0.0, 1.0 - max(t, 0.0) / IMPACT) + 0.05, Z0 - 0.5]))


def cam_ride(t):
    # low beside the crest, looking along it: night ahead on the left, the lit wake on the right
    h = 0.30 + 1.25 * float(ss(3.8, 6.3, t))
    pos = wp(-0.9, 0.45, h, t)
    look = wp(7.0, -3.2, 0.15 + 0.35 * float(ss(3.8, 6.3, t)), t)
    her = W1 + np.array([0.0, 1.05, 0.0])
    return pos, lerp(look, her, float(ss(4.9, 6.5, t)))


def cam_orbit_w1(t):
    u = float(ss(6.6, 13.0, t))
    a = np.radians(12.0 + 105.0 * u)
    r = 2.7 + 0.9 * u
    c = W1 + np.array([-0.6 * u, 1.2, 0.5 * u])
    pos = c + np.array([np.sin(a) * r, 0.35 + 0.25 * u, np.cos(a) * r])
    return pos, c + np.array([0.0, -0.05, 0.0])


def cam_surge(t):
    # ride behind the crest as it surges into the lanterns, then fall back and stall beside the pair
    ride = wp(0.6, 2.4, 1.25, t), wp(0.0, -14.0, 0.5, t)
    u = float(ss(14.3, 15.6, t))
    w = float(ss(15.4, 19.85, t))
    a = np.radians(10.0 + 60.0 * w)
    r = 5.0 - 2.0 * w
    c = PC + np.array([0.0, 1.25, 0.0])
    orb = c + np.array([np.sin(a) * r, 0.40, np.cos(a) * r]), c
    return lerp(ride[0], orb[0], u), lerp(ride[1], orb[1], u)


U_MOUTH = 36.0


def mouth(t):
    return U_MOUTH


def cam_barrel(t):
    Hh = float(HGT(t))
    k = float(ss(19.9, 20.9, t))                     # through the wall
    ub = 1.5 + 6.6 * max(t - 20.9, 0.0)
    out = wp(0.0, 2.6, 1.6, t), wp(0.0, -12.0, 0.8, t)
    tube = wp(ub, -0.66 * Hh, 0.42 * Hh, t), wp(ub + 14.0, -0.58 * Hh, 0.46 * Hh, t)
    pos, tgt = lerp(out[0], tube[0], k), lerp(out[1], tube[1], k)
    # spat out of the mouth: out ahead of the wave, turning to look back at it
    e = float(ss(25.3, 26.79, t))
    if e > 0.0:
        ex = wp(ub, -5.0 - 2.0 * e, 2.4 + 2.0 * e, t), wp(ub + 3.0, 0.0, 0.6 * Hh, t)
        pos, tgt = lerp(pos, ex[0], e), lerp(tgt, ex[1], e)
    return pos, tgt


def cam_trim(t):
    u = (t - 26.79) / (33.36 - 26.79)
    a = np.radians(-150.0 + 300.0 * float(ss(-0.1, 1.05, u)))
    c = walk_frame(t) + np.array([0.0, 1.05, 0.0])
    r = 3.6
    pos = c + np.array([np.sin(a) * r, 0.7 + 0.5 * np.sin(np.pi * u), np.cos(a) * r])
    return pos, c


def cam_run(t):
    # fly backward ahead of the wave through the sleepers, then rise and pass high over its crest
    Hh = float(HGT(t))
    k1 = float(ss(36.3, 37.5, t))
    k2 = float(ss(37.1, 38.9, t))
    pos = wp(U_MAIN - 3.5, -15.0 + 29.0 * k2, 2.2 + (Hh + 7.0) * k1, t)
    tgt = lerp(wp(U_MAIN, 0.0, 0.55 * Hh, t), wp(U_MAIN, -55.0, 0.0, t), k2)
    return pos, tgt


def cam_hang(t):
    c = float(ss(42.55, 46.1, t))
    pos = KN + np.array([0.75 + 0.6 * c, 1.15 + 10.5 * c, -1.7 - 8.0 * c])
    wall = np.array([KN[0], 0.42 * float(HGT(t)) + 0.6 * c * 6.0, crest_z(t)])
    return pos, wall


def cam_drop2(t):
    # the released wall: fly backward before it, rise above its lip, then come over behind the people on it
    Hh = float(HGT(t))
    k1 = float(ss(46.6, 47.5, t))
    k2 = float(ss(47.2, 48.5, t))
    pos = wp(U_MAIN + 1.0, -20.0 + 32.0 * k2, 7.0 + (Hh + 2.5) * k1, t)
    tgt = lerp(wp(U_MAIN, 0.0, 0.5 * Hh, t), wp(U_MAIN, -70.0, 3.0, t), k2)
    return pos, tgt


END_POS = np.array([2.0, 2.4, 118.0])
END_LOOK = np.array([0.0, 14.0, 0.0])


def cam_break(t):
    # over the breaking wave: carried forward above the plume toward the sun, then down to the water's edge
    tb = min(t, BREAK + 0.3)
    Hh = float(HGT(tb))
    start = wp(U_MAIN + 1.0, 12.0, Hh + 9.5, tb)
    high = np.array([0.55 * start[0], 19.0, start[2] - 14.0])
    land = END_POS + np.array([0.0, 0.0, -1.1 * max(t - 55.0, 0.0)])
    u1 = float(ss(BREAK, 51.8, t))
    u2 = float(ss(51.6, 55.2, t))
    pos = lerp(lerp(start, high, u1), land, u2)
    tgt = lerp(np.array([start[0], 9.0, start[2] - 80.0]), END_LOOK, float(ss(50.8, 54.6, t)))
    return pos, tgt


CAMERA = Rig([
    Path(cam_drop, 0.0, 1.55, fov=50.0, aperture=0.003, focus=3.2),
    Path(cam_ride, 1.55, 6.84, fov=60.0, aperture=0.004, blend=0.75, focus=4.0),
    Path(cam_orbit_w1, 6.84, 13.30, fov=46.0, aperture=0.02, blend=1.3),
    Path(cam_surge, 13.30, 19.85, fov=52.0, aperture=0.02, blend=0.8),
    Path(cam_barrel, 19.85, 26.79, fov=70.0, aperture=0.002, blend=0.5, focus=6.0),
    Path(cam_trim, 26.79, 33.36, fov=50.0, aperture=0.015, blend=1.1),
    Path(cam_run, 33.36, 40.21, fov=62.0, aperture=0.008, blend=0.6, focus=12.0),
    Path(cam_hang, 40.21, 46.35, fov=58.0, aperture=0.01, blend=1.6, focus=9.0),
    Path(cam_drop2, 46.35, BREAK, fov=62.0, aperture=0.004, blend=0.7, focus=20.0),
    Path(cam_break, BREAK, 60.0, fov=(62.0, 50.0), aperture=0.003, blend=0.8, focus=60.0),
], handheld=0.25, min_height=0.12, near=0.05)

# ---------------------------------------------------------------------------------------------------------
# THE NINE EXPRESSIONS (words.EXPRESSIONS by name; each read for 2.5 s or more). They ride with the camera,
# flat to the picture and in the sky part of it, so every one is whole and sharp while it is read; none has a
# mirror image in the lake.
# ---------------------------------------------------------------------------------------------------------


def _ride(x, y, depth, px, t_read0, t_read1, **kw):
    tm = 0.5 * (t_read0 + t_read1)
    return dict(ride=(x, y, depth), em=PW.em_for(CAMERA, tm, depth, px), t_read0=t_read0, t_read1=t_read1,
                face="screen", reflect=False, **kw)


_SPECS = [
    _ride(0.50, 0.66, 6.0, 104, 2.45, 5.55, expr="Greeting", t_in=1.35, t_out=6.75, arrive="reveal", edge="up",
          leave="wind", wind=(1.0, 0.25, 0.4)),
    _ride(0.50, 0.705, 8.0, 84, 9.30, 12.45, expr="Gratitude", t_in=7.55, t_out=13.45, arrive="pen",
          leave="rise"),
    _ride(0.50, 0.70, 8.0, 88, 15.55, 18.55, expr="Apology", t_in=14.35, t_out=19.75, arrive="reveal",
          edge="right", leave="wind", wind=(-1.0, 0.3, 0.3)),
    _ride(0.50, 0.49, 8.0, 94, 17.35, 19.95, expr="Inclusiveness", t_in=16.15, t_out=20.85, arrive="reveal",
          edge="out", leave="rise"),
    _ride(0.50, 0.63, 7.0, 108, 21.95, 24.85, expr="Concession", t_in=20.75, t_out=26.2, arrive="reveal",
          edge="out", leave="bokeh"),
    _ride(0.50, 0.695, 9.0, 86, 28.35, 31.35, expr="Respect", t_in=27.0, t_out=32.6, arrive="pen", leave="wind",
          wind=(-1.0, 0.1, 0.6)),
    _ride(0.50, 0.695, 10.0, 86, 34.85, 37.95, expr="Consideration", t_in=33.6, t_out=39.3, arrive="reveal",
          edge="left", leave="rise"),
    _ride(0.50, 0.64, 14.0, 84, 43.35, 46.0, expr="Encouragement", t_in=42.55, t_out=47.1, arrive="reveal",
          edge="up", leave="rise"),
    _ride(0.50, 0.695, 12.0, 90, 47.45, 50.05, expr="Compliment", t_in=46.6, t_out=51.2, arrive="reveal",
          edge="out", leave="rise"),
]
WORDS = PW.Words(_SPECS, camera=CAMERA)

# ---------------------------------------------------------------------------------------------------------
# THE END CARD (the existing 2D style): the title whole by 54.8 s, every line readable to the last frame
# ---------------------------------------------------------------------------------------------------------
T_TITLE = 51.8
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=T_TITLE, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=53.3, t1=54.8, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
# THE CONCERT BADGE (Anthony: "The concert title and the date should show from the beginning and throughout"):
# large on frame 0, settled in the top left corner by 2.8 s, never covered (every expression is read below it),
# gone as the end card forms (the end card carries the same words)
CREDIT = dict(song="The Words of Mother’s Love",
              concert="Healing Concert · Sunday, December 6 · 4:30 PM",
              t_in=-1.0, t_full=0.0,
              t_move=1.6, t_rest=2.8,
              scale=0.48, alpha_rest=0.92,
              margin_x=0.035, margin_top=0.05)


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
    tx = c["margin_x"] + c["scale"] * (x1 - x0) / 2.0
    ty = 1.0 - c["margin_top"] - c["scale"] * (y1 - y0) / 2.0
    cx, cy = cx0 * (1 - m) + tx * m, cy0 * (1 - m) + ty * m
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - sm(T_TITLE - 0.3, T_TITLE + 0.8, t))
    return (cx, cy, scale, alpha), (cx0, cy0)


_base.TITLE, _base.TAGLINE, _base.CREDIT = TITLE, TAGLINE, CREDIT

# the arch of nine lights stands over the shore; a light wakes as each expression is whole; its arc and links
# are drawn only once the wave has broken (seen from far away they made a ring with their mirror image)
ARCH = dict(span=74.0, height=42.0, z=0.0, bright=1.4, line=lambda t: float(0.8 * ss(BREAK + 0.5, 53.5, t)))
_LIT = [WORDS[lab].t_read0 for lab in PW.LABELS]


# ---------------------------------------------------------------------------------------------------------
# THE SCENE
# ---------------------------------------------------------------------------------------------------------
def _glow(t):
    # the wave is whole until it breaks; the broken wave runs on as a line of foam and is gone by 55.5 s
    return float(1.0 - ss(52.6, 55.5, t))


def _plume(t):
    return float(ss(BREAK - 0.1, BREAK + 0.7, t) * (1.0 - ss(52.0, 54.5, t)))


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
            min_gap=0.9, scale=(0.9, 1.1), avoid=None):
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
                              twinkle=0.5), gain=gain)
    warm_set = WV.Field(KIN, warm, 0.017, cols, alpha=0.6, kind="spark", delay=delay, flash=3.2, fade=0.35,
                        twinkle=0.6, emit=1.3, gain=gain)
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
                    gain=lambda t: float(ss(46.5, 47.3, t)))


def _setup(scene):
    rng = np.random.default_rng(21)
    scene.add("wave", WV.Wave(KIN, glow=_glow, mouth=mouth, plume=_plume, centers=(0.0, U_MAIN)))
    scene.add("tube", WV.Tube(KIN, -2.0, U_MOUTH + 10.0, n=70000, mouth=mouth,
                              gain=lambda t: float(ss(19.9, 20.8, t) * (1.0 - ss(25.8, 26.7, t)))))
    scene.add("spark", Spark())
    scene.add("wake", _wake(rng), reflect=False)
    lan, flame = _lanterns(rng)
    scene.add("lanterns", lan)
    scene.add("lantern_flames", flame)
    scene.add("ridges", _ridges(rng))
    baked = WV.bake_people(Body, n=2600, poses=("stand", "raise", "open_arms", "look_up"))

    # the hero bodies (each with real motion and garments of light)
    HEROES.extend([W1, M1, P1, P2, KN, HP])
    # people asleep all over the black glass: each forms out of gold light as the crest reaches them
    back_or_side = lambda r: r.choice([180.0, 180.0, 150.0, 210.0, 90.0, -90.0]) + r.normal(0.0, 12.0)  # noqa: E731
    for name, args in (
            ("s1", dict(n=34, t0=1.6, t1=7.2, u_mid=2.0, u_spread=9.0, near=(0.35, 3.5, 2.5), avoid=(-2.2, 0.4),
                        gain=lambda t: float(1.0 - ss(13.6, 14.6, t)), yaw=back_or_side)),
            ("s2", dict(n=26, t0=7.0, t1=13.2, u_mid=0.0, u_spread=7.0, near=(0.3, 0.0, 4.0), avoid=(-0.8, 2.0),
                        gain=lambda t: float(1.0 - ss(15.0, 16.0, t)), poses=("stand", "look_up", "open_arms"))),
            ("s3", dict(n=36, t0=13.4, t1=19.8, u_mid=0.0, u_spread=10.0, near=(0.3, 1.5, 3.5), avoid=(-0.8, 2.0),
                        gain=lambda t: float(ss(11.0, 12.5, t) * (1.0 - ss(22.0, 23.0, t))),
                        poses=("stand", "look_up"))),
            ("s6", dict(n=170, t0=33.5, t1=40.2, u_mid=U_MAIN, u_spread=11.0, near=(0.3, U_MAIN - 3.5, 3.0), avoid=(U_MAIN - 4.8, U_MAIN - 2.2),
                        gain=lambda t: float(ss(32.4, 33.4, t) * (1.0 - ss(40.6, 41.6, t))),
                        poses=("stand", "stand", "look_up", "open_arms"))),
            ("s8", dict(n=60, t0=49.7, t1=52.5, u_mid=U_MAIN - 20.0, u_spread=22.0, min_gap=1.3,
                        gain=lambda t: float(ss(48.5, 49.5, t)), yaw=lambda r: 180.0 + r.normal(0.0, 15.0),
                        poses=("stand", "raise", "open_arms")))):
        for nm, st in _people(rng, baked, name, **args):
            scene.add(nm, st)
    scene.add("crest_line", _crest_line(rng, baked))

    # the first two to wake (S1, S2)
    w1 = Body("woman", at=(W1[0], W1[2]), facing=[(0.0, 180.0), (7.4, 180.0), (9.0, 150.0)], garment="dress",
              hair=True, look="glitter", color="#ffcf8a", color2="#fff0d0", points=70000, show=(4.2, 14.2),
              fade=0.4, gesture=[(7.2, 14.5, "look_up", dict(amount=10))], seed=3)
    scene.add("w1", WV.Ignite(w1, T_W1))
    m1 = Body("man", at=(M1[0], M1[2]), facing=[(0.0, 160.0), (8.0, 160.0), (9.5, 120.0)], garment="coat",
              stoop=0.35, look="glitter", color="#ffc27a", color2="#ffe6c0", points=60000, show=(4.2, 14.2),
              fade=0.4, gesture=[(8.6, 14.5, "bow")], seed=4)
    scene.add("m1", WV.Ignite(m1, T_M1))

    # the two who stood back to back (S3): they turn to each other and reach
    p1 = Body("man", at=(P1[0], P1[2]), facing=[(0.0, -90.0), (17.6, -90.0), (18.6, 90.0)], garment="tunic",
              look="glitter", color="#ffb07a", color2="#ffe2c0", points=60000, show=(12.8, 21.0), fade=0.4,
              gesture=[(16.1, 17.4, "bow"), (18.8, 21.5, "reach")], seed=5)
    p2 = Body("woman", at=(P2[0], P2[2]), facing=[(0.0, 90.0), (16.0, 90.0), (17.0, -90.0)], garment="coat",
              look="glitter", color="#ff9fb4", color2="#ffe2ea", points=60000, show=(12.8, 21.0), fade=0.4,
              gesture=[(18.9, 21.5, "reach")], seed=6)
    t_pair = float(KIN.time_at(PC[0], PC[2]))
    scene.add("p1", WV.Ignite(p1, t_pair))
    scene.add("p2", WV.Ignite(p2, t_pair + 0.1))

    # two walking the crest (S5)
    for k, (shape, garment, col, off) in enumerate((("man", "tunic", "#ffcf8a", -0.45),
                                                    ("woman", "robe", "#ffe0a8", 0.45))):
        b = Body(shape, at=(0.0, off), facing=90.0, motion="walk", garment=garment, look="glitter", color=col,
                 color2="#fff4dc", points=60000, show=(26.3, 33.9), fade=0.5, frame=walk_frame, seed=7 + k,
                 hair=(shape == "woman"), bright=1.3)
        scene.add(f"walker{k}", b)

    # the kneeling one, and the hand on the shoulder (S7)
    kn = Body("man", at=(KN[0], KN[2]), facing=0.0, motion="kneel", garment="tunic", look="glitter",
              color="#ffd08a", color2="#fff0d8", points=60000, show=(39.4, 48.2), fade=0.5, seed=9)
    hp = Body("woman", at=(HP[0], HP[2]), facing=20.0, garment="robe", look="glitter", color="#ffe0a0",
              color2="#fff6e0", points=60000, show=(39.4, 48.2), fade=0.5, seed=10,
              gesture=[(40.5, 48.0, "hand_on_shoulder", dict(side="R", to=lambda t: kn.where(t, "shoulder.L")))])
    scene.add("kneel", WV.Ignite(kn, 41.6, rise=1.2))
    scene.add("helper", hp)

    WORDS.add_to(scene)
    try:
        WORDS.check(CAMERA)
    except Exception as e:                       # the check is advice; never stop a render for it
        print("words check failed:", e)


P3D = dict(
    camera=CAMERA,
    world=WORDS.world(dict(
        look=[(0.0, "night"), (BREAK + 0.3, "sunrise", 1.6), (51.9, "golden", 1.6), (53.6, "day", 1.6)],
        sun_az=180.0,
        split=dict(look="dawn", toward=0.0, soft=0.4,
                   amount=lambda t: float(0.15 + 0.85 * ss(2.5, 12.0, t)) * float(1.0 - ss(BREAK, 51.5, t))),
        ripple=lambda t: float(0.18 + 0.4 * ss(8.0, 20.0, t)),
        mirror=1.0,
        stars=lambda t: float(1.0 - ss(BREAK, 52.5, t)),
        milky=lambda t: float(0.8 * (1.0 - ss(BREAK, 51.5, t))),
        mist=0.22,
        dust=0.25,
        bokeh=0.35,
        shafts=[dict(base=(X0, Z0), radius=0.14, top=60.0, spread=0.02, color="#fff1d0",
                     strength=lambda t: float(0.9 * (1.0 - ss(IMPACT, IMPACT + 1.4, t))))],
        lights=[dict(pos=lambda t: wp(0.0 if t < 20.0 else U_MAIN, 0.3, 0.6 * float(HGT(t)) + 0.3, t),
                     color="#ffc060", strength=lambda t: float(0.0 if t < IMPACT else 0.28 * _glow(t)),
                     radius=lambda t: 2.0 + 1.0 * float(HGT(t)))],
        arch=dict(lit=_LIT, **ARCH),
        react=dict(beat=0.4, level=0.3),
    )),
    bursts=[dict(t=HIT0, strength=0.3, at=(X0, spark_y(HIT0), Z0), radius=0.05, rise=0.04, fall=0.3,
                 color="#fff1d0"),
            dict(t=IMPACT, strength=0.8, at=(X0, 0.05, Z0), radius=0.10, rise=0.05, fall=0.5, color="#fff1d0"),
            dict(t=19.80, strength=0.9, at=(float(PC[0]), 1.3, float(PC[2])), radius=0.09, rise=0.05, fall=0.45,
                 color="#ffe0b8"),
            dict(t=20.45, strength=1.3, radius=0.4, rise=0.12, fall=0.5, color="#ffe2a8"),
            dict(t=BIG, strength=0.7, radius=0.3, rise=0.08, fall=0.9, color="#fff0d0"),
            dict(t=BREAK + 0.2, strength=1.0, radius=0.32, rise=0.12, fall=1.0, color="#fff4dc")],
    setup=_setup,
)


if __name__ == "__main__":
    print("Z0", Z0, "crest at break", crest_z(BREAK))
    for t in (1.0, 2.0, 6.0, 13.3, 19.85, 26.79, 33.36, 40.21, 42.5, 46.4, BREAK):
        print(t, "R", round(float(KIN.R(t)), 1), "H", round(float(HGT(t)), 2), "speed", CAMERA.speed(t))
    WORDS.check(CAMERA)
