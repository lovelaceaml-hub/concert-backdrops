"""Ten films, film 03: CONSTELLATIONS (60 seconds, a promo for the Healing Concert "The Words of Mother's Love").

LOGLINE
  Scattered stars are only scattered stars until a word of love joins them. People made of stars stand on a
  black mirror under the night; every word that passes between two of them is a constellation that draws
  itself, then climbs to its place in the sky as one of the nine lights. The lines stay. After the breath a
  chain reaction of lines crosses the whole lake; the arch of nine lights is drawn dot to dot, turns, and
  sweeps out a globe of light that the mirror completes; the sun breaks behind it and the day comes.

RULES OF THIS WORLD
  People are plexus bodies (points joined by fine lines, refs 03 and 12) with their joints as bright stars
  joined by lines: a constellation in human form, clothed in garments of light, featureless. Sky above and
  the same sky in a still mirror below; no hills, no shore. The camera always revolves. Heavenly Mother
  appears once, at the breath, as a great far constellation seen only from behind, veiled, arms opening low.

TIMELINE (medley sections 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 (breath to 42.51), 49.47; hit 58.11)
  0.0   No black: the camera falls through a field of stars toward one warm star. Scattered stars swing into
        line as it arrives (1.0): a woman in profile, head and shoulders. It revolves round her head.
  2.4   A coral line leaves her hand to the man she greets; the Greeting writes itself with a star (read
        3.3 to 6.3), then climbs to light 1 of the arch.
  6.84  Dive to the mirror: a walker comes to a kneeling, tired worker. Gratitude (stars out of the deep sky
        settle into letters, read 8.7 to 11.7) rains into her: she fills with light and rises.
  13.30 Two stand back to back. Apology rises out of its own reflection in the lake (read 14.2 to 16.8); they
        turn, reach, and their hands TOUCH: Inclusiveness is born at the touch (read 17.3 to 19.9).
  19.85 The bass: a flock of stars wheels in as Concession, while one steps aside and offers the way (read
        21.0 to 23.6); the other is listened to: Respect is woven from threads of light (read 24.0 to 26.6).
  26.79 A youth sinks to one knee, an elder raises both arms: Encouragement comes down a shaft of light
        (read 27.8 to 30.4). A woman forms from dust and reaches down: Consideration is blown from her open
        palm (read 30.7 to 33.3); their hands clasp.
  33.36 The clasp bursts: Compliment, the largest words, burned out of the air by rays (read 34.3 to 37.7);
        the joined hands are raised. The camera is thrown back and up; the lake fills with faint people.
  40.21 THE BREATH. The nine lights stand in the sky, a thread from every stage to its light. Beyond the arch
        a great constellation draws itself: Heavenly Mother from behind, veiled, her arms opening low.
  42.51 THE WEB. Lines race from everyone to everyone across the lake while the camera is pulled back.
  45.64 The arch is drawn dot to dot, flares, and turns: its lights and its curve sweep out a globe of light
        that the mirror completes; lights spread over it like cities at night.
  49.47 The sun breaks behind the globe; the sky floods to day. 52.0 the title draws itself as a
        constellation; 54.0 the date, church and address rise; the end card is whole and readable from 55.0
        to the last frame, bright to the end (no fade). The last hit (58.11) lifts the light.

THE NINE EXPRESSIONS: words.EXPRESSIONS by name (exact campaign wording), each a word of particles in the 3D
world (engine/p3d/words.py) with a reading moment of at least 2.5 s, laid out on the picture of the camera.
"""
import numpy as np

import songs.s03_original as _base
from track import Track

TOTAL_SECONDS = 60.0
_ZERO = Track([(0.0, 0.0), (TOTAL_SECONDS, 0.0)])
_base.TOTAL = TOTAL_SECONDS
_base.NFRAMES = int(round(TOTAL_SECONDS * _base.FPS))
_base.MUSIC_END = 59.9
_base.SONG_END = 60.0
_base.FADE = Track([(0.0, 1.0), (TOTAL_SECONDS, 1.0)])            # never black: first frame to last
_base.EXPOSURE = Track([(0.0, 1.0), (58.05, 1.0), (58.2, 1.10), (59.0, 1.0), (TOTAL_SECONDS, 1.0)])
_base.ZOOM = Track([(0.0, 1.0), (TOTAL_SECONDS, 1.0)])
for _k in ("RAIN", "AURORA", "PETALS", "LANTERNS", "MOTES", "RAYS", "PART", "TRAIL", "CLOUDS", "STARS", "MILKY"):
    setattr(_base, _k, _ZERO)
for _p in _base.PHRASES:                      # the flat expressions stay off: the words are particles here
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402
from p3d import lin  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.camera import Rig, dolly, fly, orbit  # noqa: E402
from p3d.world import arch_points  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = TOTAL_SECONDS
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 59.9
SONG_END = 60.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0          # nothing dark behind any text

# ------------------------------------------------------------------------------------------------ the music
SECTIONS = [0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47]
BREATH = (40.21, 42.51)
WEB = 42.51                 # the biggest jump of the mix
ARCH_DRAWN = 45.64
ARCH_TURNS = 46.0
SUN_BREAK = 49.47
FINAL_HIT = 58.11

# ---------------------------------------------------------------------------------------------- the geometry
SILVER, STEEL, ELECTRIC = "#cfe0ff", "#7f96c8", "#4f9bff"
COL = {e["label"]: e["color"] for e in PW.EXPRESSIONS}
ARCH_C = np.array([0.0, 0.0, -110.0])      # the arch (and the globe) stands here, a half circle of radius 85
ARCH_R = 85.0
ARCH = dict(span=2 * ARCH_R, height=ARCH_R, z=0.0, center=tuple(ARCH_C))
LIGHTS = arch_points(ARCH["span"], ARCH["height"], 0.0, center=ARCH["center"])
STAGES = [-32.0, -16.0, 0.0, 16.0, 32.0]     # x of the five places on the mirror, left to right


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _yaw(t):
    """The arch's turn about the vertical, degrees: still until 46.0, a half turn by 49.6, then on slowly."""
    if t <= ARCH_TURNS:
        return 0.0
    if t <= 49.6:
        u = (t - ARCH_TURNS) / (49.6 - ARCH_TURNS)
        return float(180.0 * (u * u * (3.0 - 2.0 * u) * 0.75 + 0.25 * u))
    return float(180.0 + 14.0 * (t - 49.6))


# ---------------------------------------------------------------------------------------------- the camera
A_HEAD = (-33.15, 1.52, 0.0)
CAMERA = Rig([
    # S0 first light: fall through the star field, arrive at her profile, revolve, swing out to the two
    fly([(0.0, (-12.0, 11.0, 54.0), A_HEAD), (0.55, (-27.5, 3.6, 12.0), A_HEAD),
         (1.0, (-33.05, 1.56, 1.75), A_HEAD), (2.2, (-34.7, 1.72, 1.45), (-31.4, 1.5, -0.2)),
         (3.3, (-33.4, 2.05, 6.9), (-32.0, 2.25, -0.2)), (6.84, (-31.3, 2.0, 7.4), (-32.0, 2.3, -0.2))],
        fov=Track([(0.0, 62.0), (0.95, 34.0), (2.2, 38.0), (3.3, 42.0), (6.84, 42.0)]),
        aperture=Track([(0.0, 0.0), (0.9, 0.035), (2.4, 0.03), (3.3, 0.012), (6.84, 0.012)])),
    # S1 the mirror: dive to the water, skim along the line to the two, close on her as she rises
    fly([(6.84, (-27.0, 0.45, 9.0), (-16.5, 1.6, 0.0)), (8.6, (-18.6, 1.15, 8.8), (-16.1, 2.45, 0.0)),
         (11.8, (-16.4, 1.45, 8.1), (-16.0, 2.5, 0.0)), (13.3, (-14.4, 1.35, 4.4), (-15.0, 1.4, 0.0))],
        fov=Track([(6.84, 56.0), (8.4, 42.0), (11.8, 42.0), (13.3, 38.0)]), aperture=0.012, blend=0.5),
    # S2 falling stars: revolve round the two who turn back to each other and touch
    orbit((0.0, 1.7, 0.0), radius=(9.8, 6.2), height=(2.6, 1.75), a0=-30.0, a1=22.0, t0=13.3, t1=19.85,
          look=(0.0, 2.2, 0.0), fov=42.0, aperture=0.012, blend=0.6),
    # S3 the bass slams in: whip to the third place and revolve the other way
    orbit((15.8, 1.7, 0.0), radius=(10.5, 7.6), height=(2.3, 1.9), a0=28.0, a1=-18.0, t0=19.85, t1=26.79,
          look=(15.8, 2.25, -0.2), fov=42.0, aperture=0.012, blend=0.45),
    # S4 the stair of the night: round the kneeling youth, the elder and the hand held down
    orbit((31.6, 1.6, 0.0), radius=(9.5, 6.8), height=(3.4, 2.0), a0=-26.0, a1=14.0, t0=26.79, t1=33.36,
          look=(31.6, 2.1, 0.0), fov=42.0, aperture=0.012, blend=0.45),
    # S5 thrown back by the burst, then up and away toward the arch
    fly([(33.36, (32.2, 1.9, 5.6), (31.9, 2.0, 0.0)), (33.9, (31.9, 2.6, 10.5), (31.7, 3.6, -0.5)),
         (34.3, (31.6, 3.3, 14.5), (31.5, 4.3, -1.0))], fov=Track([(33.36, 40.0), (34.3, 44.0)]), aperture=0.006,
        blend=0.35),
    dolly((31.6, 3.3, 14.5), (30.7, 3.8, 16.3), 34.3, 37.8, look=((31.5, 4.3, -1.0), (31.0, 4.5, -1.0)), fov=44.0,
          aperture=0.006, blend=0.4),
    fly([(37.8, (30.7, 3.8, 16.3), (31.0, 4.5, -1.0)), (39.0, (26.0, 7.0, 34.0), (16.0, 20.0, -60.0)),
         (40.21, (17.0, 13.0, 62.0), (6.0, 32.0, -120.0))], fov=Track([(37.8, 44.0), (40.21, 50.0)]),
        aperture=0.0, blend=0.6),
    # the breath: drift and tilt up to the nine lights and the far constellation beyond them
    dolly((13.0, 15.0, 72.0), (9.0, 19.0, 86.0), 40.21, 42.51, look=((4.0, 52.0, -200.0), (2.0, 64.0, -240.0)),
          fov=50.0, aperture=0.0, blend=1.0),
    # the web: pulled back fast, revolving, past people at many depths
    orbit((0.0, 40.0, -110.0), radius=(205.0, 425.0), height=(22.0, 15.0), a0=4.0, a1=-12.0, t0=42.51, t1=45.64,
          look=(0.0, 46.0, -150.0), fov=48.0, aperture=0.0, blend=0.35,
          pace=[(42.51, 0.0), (43.3, 0.48), (45.64, 1.0)]),
    # the world: far out, low on the water, revolving against the globe's turn
    orbit((0.0, 0.0, -110.0), radius=(425.0, 395.0), height=(14.0, 8.0), a0=-12.0, a1=3.0, t0=45.64, t1=52.0,
          look=(0.0, 30.0, -110.0), fov=42.0, aperture=0.0, blend=1.2),
    # day: tilt up into the light, room for the title, a slow lean to the last frame
    orbit((0.0, 0.0, -110.0), radius=(395.0, 370.0), height=(8.0, 12.0), a0=3.0, a1=9.0, t0=52.0, t1=60.0,
          look=lambda t: (0.0, 30.0 + 42.0 * float(_ss(52.0, 55.5, t)), -110.0), fov=42.0, aperture=0.0,
          blend=1.5),
], blend=0.6, fov=42.0, aperture=0.0, handheld=0.2, min_height=0.3)


# ------------------------------------------------------------------------------------------- the nine words
def _word(t_read0, t_read1, x, y, depth, px, **kw):
    """A word laid out on the picture at the middle of its reading moment: screen place (x, y) of its centre,
    `depth` metres ahead of the lens, one em `px` pixels of a 1080p frame."""
    tm = 0.5 * (t_read0 + t_read1)
    return dict(pos=tuple(PW.place(CAMERA, tm, x, y, depth)), em=PW.em_for(CAMERA, tm, depth, px),
                t_read0=t_read0, t_read1=t_read1, **kw)


_MEET = (0.0, 1.22, 0.14)                   # where the two hands touch (S2)
_CLASP = (32.1, 0.95, 0.12)                  # where the hand held down meets the hand reaching up (S4)
_P = {}                                      # the people, made in build()


class _BodyPoints:
    """A light stand-in for a person as a goal for words (`give`): a share of her points at t."""

    def __init__(self, name):
        self.name = name

    def sample(self, t):
        p, _ = _P[self.name].shape_points(t)
        return dict(pos=p[::6], size=0.01, color=lin("#ffffff"), alpha=0.0)


def _palm_M(t):
    return np.asarray(_P["M"].where(t, "palm.R"), np.float64) if "M" in _P else np.array(_CLASP)


_SPECS = [
    _word(3.3, 6.3, 0.50, 0.73, 7.6, 112, expr="Greeting", t_in=2.3, t_out=7.6, arrive="pen",
          leave="arch", to=tuple(LIGHTS[0])),
    _word(8.7, 11.7, 0.50, 0.74, 8.4, 84, expr="Gratitude", t_in=7.1, t_out=13.3, arrive="stars",
          leave="give", to=_BodyPoints("D")),
    _word(14.2, 16.8, 0.50, 0.75, 8.6, 94, expr="Apology", t_in=13.3, t_out=18.2, arrive="lake",
          leave="arch", to=tuple(LIGHTS[2])),
    _word(17.2, 19.75, 0.50, 0.69, 6.4, 116, expr="Inclusiveness", t_in=16.4, t_out=21.0, arrive="touch",
          source=_MEET, touch_at=0.45, leave="arch", to=tuple(LIGHTS[3])),
    _word(21.0, 23.6, 0.50, 0.74, 9.6, 118, expr="Concession", t_in=19.85, t_out=24.6, arrive="flock",
          leave="arch", to=tuple(LIGHTS[4])),
    _word(24.0, 26.65, 0.50, 0.70, 8.0, 100, expr="Respect", t_in=23.0, t_out=27.6, arrive="weave",
          leave="arch", to=tuple(LIGHTS[5])),
    _word(27.8, 30.4, 0.50, 0.74, 8.8, 88, expr="Encouragement", t_in=26.79, t_out=31.4, arrive="shaft",
          leave="arch", to=tuple(LIGHTS[6])),
    _word(30.7, 33.3, 0.50, 0.69, 7.0, 100, expr="Consideration", t_in=29.7, t_out=34.2, arrive="palm",
          source=_palm_M, leave="arch", to=tuple(LIGHTS[7])),
    _word(34.3, 37.7, 0.50, 0.62, 15.0, 138, expr="Compliment", t_in=33.36, t_out=40.0, arrive="rays",
          source=(31.6, 2.0, -3.0), leave="arch", to=tuple(LIGHTS[8]), n=110000, n_label=12000),
]
WORDS = PW.Words(_SPECS, face="camera")
LIT = [WORDS[lab].t_out - 0.3 for lab in PW.LABELS]      # each light wakes as its word's stream reaches it
LIT[1] = 13.0                                              # the Gratitude went into the worker; its light wakes


# ---------------------------------------------------------------------------------------------- point sets
class StarField:
    """Near stars round the opening flight (they streak as the camera falls through them) and over the lake."""
    static = True

    def __init__(self, n=7000, seed=3):
        rng = np.random.default_rng(seed)
        p = np.stack([rng.uniform(-60.0, 50.0, n), rng.uniform(0.6, 34.0, n), rng.uniform(-40.0, 75.0, n)], 1)
        keep = np.linalg.norm(p - np.array(A_HEAD), axis=1) > 3.0
        p = p[keep]
        self.n = len(p)
        self.p = p
        self.s = rng.random((self.n, 3))

    def sample(self, t):
        s = self.s
        warm = s[:, 0] > 0.86
        col = np.where(warm[:, None], lin("#ffd9a0")[None], lin(SILVER)[None]) * (0.6 + 0.6 * s[:, 1:2])
        return dict(pos=self.p, size=0.035 + 0.06 * s[:, 2] ** 3, color=col, alpha=0.9, kind="spark",
                    twinkle=0.8, emit=1.0 + 2.0 * (s[:, 1] > 0.93))

    def gain(self, t):
        return float(0.35 + 0.65 * (1.0 - _ss(2.0, 6.0, t)) + 0.0 * t) * float(1.0 - 0.8 * _ss(44.0, 47.0, t))


class Constellation:
    """A person's joints as bright stars joined by lines (their constellation), over the plexus body. For the
    first woman, the stars come from scattered depths and slide into line as the camera reaches its place."""

    def __init__(self, name, color, star_color, show, align=None, bright=1.0):
        self.name, self.show, self.align, self.bright = name, show, align, bright
        self.color, self.star = lin(color), lin(star_color)
        rng = np.random.default_rng(len(name) * 7 + 1)
        self.k = np.exp(rng.uniform(np.log(0.3), np.log(5.0), 20))
        self.r = rng.random(20)

    def sample(self, t):
        a0, a1, b0, b1 = self.show
        g = float(_ss(a0, a1, t) * (1.0 - _ss(b0, b1, t))) * self.bright
        if g <= 0.002:
            return None
        c = _P[self.name].constellation(t)
        pos, pairs = np.asarray(c["pos"], np.float64), np.asarray(c["pairs"])
        line_a = 0.55
        if self.align is not None:
            eye, t_snap = self.align
            u = float(_ss(t_snap - 1.0, t_snap, t))
            k = self.k + (1.0 - self.k) * u
            pos = np.asarray(eye)[None] + (pos - np.asarray(eye)[None]) * k[:, None]
            line_a = 0.55 * float(_ss(t_snap - 0.08, t_snap + 0.1, t)) * (1.0 + 1.6 * (1.0 - _ss(t_snap, t_snap + 0.9, t)))
            g = max(g, float(_ss(0.0, 0.25, t)))
        size = 0.028 + 0.02 * self.r
        out = [dict(pos=pos, size=size, color=self.star * (1.2 + 0.8 * self.r[:, None]), alpha=0.95 * g,
                    kind="spark", emit=2.6, twinkle=0.5, dof=0.6)]
        if line_a > 0.0:
            a, b = pos[pairs[:, 0]], pos[pairs[:, 1]]
            out.append(dict(pos=a, pos2=b, size=0.006, color=self.color, alpha=line_a * g, kind="line", dof=0.6,
                            u=np.zeros(len(a)), u2=np.ones(len(a)), pulse=(2.0, 0.35, 2.0, 3.0)))
        return out


def _arc(a, b, lift, n=24):
    u = np.linspace(0.0, 1.0, n)[:, None]
    p = np.asarray(a)[None] * (1 - u) + np.asarray(b)[None] * u
    p[:, 1] += lift * np.sin(np.pi * u[:, 0])
    return p


# lines drawn between people: (from, to, t0, t1, colour, lift). A line once drawn never goes out.
LINKS = [
    ((-33.0, 1.35, 0.1), (-30.9, 1.35, -0.2), 2.4, 3.0, COL["Greeting"], 0.7),
    ((-30.9, 1.35, -0.2), (-17.3, 1.3, 0.2), 6.3, 7.2, SILVER, 1.5),
    ((-17.1, 1.3, 0.2), (-14.9, 0.8, 0.0), 9.4, 10.6, COL["Gratitude"], 0.4),
    ((-14.9, 1.2, 0.0), (-0.8, 1.3, 0.0), 12.9, 13.7, SILVER, 1.5),
    ((-0.75, 1.3, 0.0), (0.75, 1.3, 0.0), 16.6, 17.0, COL["Apology"], 0.25),
    ((0.75, 1.3, 0.0), (13.4, 1.3, 0.8), 19.6, 20.3, SILVER, 1.5),
    ((16.0, 1.3, -1.2), (18.1, 1.3, -0.3), 23.7, 24.3, COL["Respect"], 0.4),
    ((18.1, 1.3, -0.3), (31.1, 0.8, 0.0), 26.4, 27.2, SILVER, 1.5),
    ((29.5, 1.5, -0.8), (31.1, 0.9, 0.0), 27.2, 27.9, COL["Encouragement"], 0.5),
    ((33.0, 1.2, 0.0), (31.1, 0.9, 0.0), 30.4, 31.0, COL["Consideration"], 0.3),
]


class Lines:
    """The lines between people, and a thread from every place up to the light its word became."""

    def __init__(self):
        segs = []
        for a, b, t0, t1, c, lift in LINKS:
            segs.append((_arc(a, b, lift), t0, t1, c, 0.010))
        threads = [((-32.0, 2.6, 0.0), 0, 7.4), ((-16.0, 2.6, 0.0), 1, 13.0), ((0.0, 2.6, 0.0), 2, 18.0),
                   ((0.0, 2.4, 0.0), 3, 21.0), ((16.0, 2.6, 0.0), 4, 24.4), ((16.0, 2.4, 0.0), 5, 27.4),
                   ((31.6, 2.6, 0.0), 6, 31.2), ((31.6, 2.4, 0.0), 7, 34.0), ((31.6, 2.8, 0.0), 8, 39.8)]
        for p, i, tt in threads:
            e = np.asarray(LIGHTS[i])
            segs.append((_arc(p, e, 6.0, 40), tt, tt + 1.4, COL[PW.LABELS[i]], 0.05))
        A, B, T0, T1, C, U, W = [], [], [], [], [], [], []
        for p, t0, t1, c, w in segs:
            m = len(p) - 1
            A.append(p[:-1])
            B.append(p[1:])
            k = np.arange(m)
            T0.append(t0 + (t1 - t0) * k / m)
            T1.append(t0 + (t1 - t0) * (k + 1) / m)
            C.append(np.repeat(lin(c)[None], m, 0))
            U.append(np.stack([k / m, (k + 1) / m], 1) * np.linalg.norm(p[-1] - p[0]))
            W.append(np.full(m, w))
        self.a, self.b = np.concatenate(A), np.concatenate(B)
        self.t0, self.t1 = np.concatenate(T0), np.concatenate(T1)
        self.c, self.u, self.w = np.concatenate(C), np.concatenate(U), np.concatenate(W)

    def sample(self, t):
        on = t >= self.t0
        if not on.any():
            return None
        a, b = self.a[on], self.b[on]
        f = np.clip((t - self.t0[on]) / np.maximum(self.t1[on] - self.t0[on], 1e-6), 0.0, 1.0)
        b = a + (b - a) * f[:, None]
        fresh = 1.0 - _ss(0.0, 1.5, t - self.t1[on])
        alpha = (0.35 + 0.65 * fresh) * (1.0 - 0.7 * _ss(52.0, 55.0, t))
        col = self.c[on] * (1.0 + 1.5 * fresh[:, None])
        return dict(pos=a, pos2=b, size=self.w[on], color=col, alpha=alpha, kind="line",
                    u=self.u[on, 0], u2=self.u[on, 1], pulse=(6.0, 1.2, 2.5, 4.0))


class Web:
    """Hundreds of faint people of stars on the lake; after the breath a chain reaction of lines runs from
    everyone to everyone and each person it reaches lights up."""

    def __init__(self, templates, n=170, seed=11):
        rng = np.random.default_rng(seed)
        pts = []
        while len(pts) < n:
            p = np.array([rng.uniform(-330.0, 330.0), 0.0, rng.uniform(-330.0, 300.0)])
            if abs(p[0]) < 48.0 and -12.0 < p[2] < 40.0:
                continue                                       # keep the five places clear
            if abs(p[0] - 0.0) < 9.0 and p[2] > 60.0:
                continue                                       # keep the pull-back corridor clear
            if np.linalg.norm(p - ARCH_C) < ARCH_R + 6.0:
                continue                                       # keep the globe clear
            pts.append(p)
        self.base = np.array(pts)
        self.scale = rng.uniform(2.2, 6.0, n)
        self.yaw = rng.uniform(0.0, 2 * np.pi, n)
        self.tpl = rng.integers(0, len(templates), n)
        stars, pairs = [], []
        for i in range(n):
            T = templates[self.tpl[i]]
            c, s = np.cos(self.yaw[i]), np.sin(self.yaw[i])
            q = T["pos"] * self.scale[i]
            q = np.stack([q[:, 0] * c + q[:, 2] * s, q[:, 1], -q[:, 0] * s + q[:, 2] * c], 1) + self.base[i]
            pairs.append(T["pairs"] + 20 * i)
            stars.append(q)
        self.stars = np.concatenate(stars)
        self.pairs = np.concatenate(pairs)
        self.owner = np.repeat(np.arange(n), 20)
        self.chest = np.array([self.stars[20 * i + 2] for i in range(n)])
        # the graph: everyone to their three nearest, and the five places as the seeds
        seeds = np.array([[x, 1.3, 0.0] for x in STAGES])
        nodes = np.concatenate([seeds, self.chest])
        d = np.linalg.norm(nodes[:, None] - nodes[None], axis=2)
        near = np.argsort(d, axis=1)[:, 1:4]
        e = np.unique(np.sort(np.stack([np.repeat(np.arange(len(nodes)), 3), near.reshape(-1)], 1), axis=1), axis=0)
        reach = np.full(len(nodes), np.inf)
        reach[:5] = 0.0
        for _ in range(60):
            for i, j in e:
                L = d[i, j]
                if reach[i] + L < reach[j]:
                    reach[j] = reach[i] + L
                if reach[j] + L < reach[i]:
                    reach[i] = reach[j] + L
        speed = 150.0
        reach = np.where(np.isfinite(reach), reach, reach[np.isfinite(reach)].max())
        self.reach = WEB + np.minimum(reach / speed, 2.7)
        self.reach += 0.05 * rng.random(len(nodes))
        # an edge starts where the chain reaction arrives first and runs to the other end
        ea, eb = e[:, 0].copy(), e[:, 1].copy()
        swap = self.reach[ea] > self.reach[eb]
        ea[swap], eb[swap] = e[swap, 1], e[swap, 0]
        self.ea, self.eb = nodes[ea], nodes[eb]
        self.et0 = self.reach[ea]
        self.et1 = self.et0 + d[ea, eb] / speed
        self.elen = d[ea, eb]
        self.person_reach = self.reach[5:]
        self.r = rng.random(len(self.stars))

    def sample(self, t):
        if t < 37.5:
            return None
        appear = float(_ss(37.5, 40.0, t))
        day = float(_ss(50.5, 54.0, t))
        lit = _ss(0.0, 0.25, t - self.person_reach[self.owner])
        flash = np.exp(-np.maximum(t - self.person_reach[self.owner], 0.0) * 3.0) * (t >= self.person_reach[self.owner])
        star_col = lin(STEEL)[None] * (1 - lit[:, None]) + lin(SILVER)[None] * lit[:, None]
        out = [dict(pos=self.stars, size=0.09 * self.scale[self.owner] * (0.7 + 0.6 * self.r),
                    color=star_col * (1.0 + 2.0 * flash[:, None]), alpha=appear * (0.35 + 0.6 * lit) * (1 - 0.6 * day),
                    kind="spark", emit=1.5 + 2.0 * flash, twinkle=0.7)]
        la, lb = self.stars[self.pairs[:, 0]], self.stars[self.pairs[:, 1]]
        lo = self.owner[self.pairs[:, 0]]
        llit = _ss(0.0, 0.4, t - self.person_reach[lo])
        out.append(dict(pos=la, pos2=lb, size=0.02 * self.scale[lo], color=lin(SILVER) * (0.6 + 0.8 * llit[:, None]),
                        alpha=appear * (0.12 + 0.4 * llit) * (1 - 0.6 * day), kind="line"))
        on = t >= self.et0
        if on.any():
            f = np.clip((t - self.et0[on]) / np.maximum(self.et1[on] - self.et0[on], 1e-6), 0.0, 1.0)
            a = self.ea[on]
            b = a + (self.eb[on] - a) * f[:, None]
            fresh = 1.0 - _ss(0.0, 1.2, t - self.et1[on])
            col = lin(ELECTRIC)[None] * fresh[:, None] + lin(SILVER)[None] * (1 - fresh[:, None])
            out.append(dict(pos=a, pos2=b, size=0.12, color=col * (1.2 + 1.8 * fresh[:, None]),
                            alpha=(0.3 + 0.6 * fresh) * (1 - 0.75 * day), kind="line",
                            u=np.zeros(on.sum()), u2=self.elen[on], pulse=(60.0, 8.0, 3.0, 12.0)))
        return out


class Globe:
    """What the turning arch leaves behind: a meridian every 20 degrees and a ring in each light's colour, so
    the half circle sweeps out a dome that the mirror makes a whole globe; then lights spread over it."""

    def __init__(self):
        th = np.radians(np.linspace(0.0, 180.0, 49))
        self.mer = np.stack([ARCH_R * np.cos(th), ARCH_R * np.sin(th), np.zeros_like(th)], 1)
        th9 = np.radians(np.linspace(172.0, 8.0, 9))
        self.light = np.stack([ARCH_R * np.cos(th9), ARCH_R * np.sin(th9)], 1)
        rng = np.random.default_rng(5)
        n = 2600
        v = rng.normal(size=(n, 3))
        v[:, 1] = np.abs(v[:, 1])
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        self.city = ARCH_C[None] + v * ARCH_R * 1.002
        self.city_t = 47.2 + 3.0 * (1.0 - v[:, 1]) + 0.6 * rng.random(n)
        self.city_c = np.array([lin(COL[PW.LABELS[k % 9]]) if k % 3 else lin("#fff2d6") for k in range(n)])
        self.city_s = 0.35 + 0.5 * rng.random(n) ** 3

    @staticmethod
    def _rot(p, deg):
        a = np.radians(deg)
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        return np.stack([x * np.cos(a) + z * np.sin(a), y, -x * np.sin(a) + z * np.cos(a)], -1)

    def sample(self, t):
        if t < ARCH_TURNS:
            return None
        yaw = min(_yaw(t), 180.0)
        warm = float(_ss(SUN_BREAK - 0.5, SUN_BREAK + 2.5, t))
        fade = 1.0 - 0.72 * float(_ss(52.0, 55.5, t))
        line_col = lin(SILVER) * (1 - warm) + lin("#ffd27a") * warm
        out = []
        A, B, Al = [], [], []
        for j in range(9):
            phi = 20.0 * j
            if yaw < phi:
                continue
            age = (yaw - phi) / 40.0
            p = self._rot(self.mer, phi) + ARCH_C
            A.append(p[:-1])
            B.append(p[1:])
            Al.append(np.full(len(p) - 1, 0.25 + 0.55 * np.exp(-age * 2.0)))
        if A:
            out.append(dict(pos=np.concatenate(A), pos2=np.concatenate(B), size=0.45, color=line_col * 1.4,
                            alpha=np.concatenate(Al) * fade, kind="line"))
        psi = np.radians(np.arange(0.0, yaw + 1e-6, 2.0))
        if len(psi) > 1:
            RA, RB, RC = [], [], []
            for i in range(9):
                x, y = self.light[i]
                p = np.stack([x * np.cos(psi), np.full_like(psi, y), -x * np.sin(psi)], 1) + ARCH_C
                RA.append(p[:-1])
                RB.append(p[1:])
                RC.append(np.repeat(lin(COL[PW.LABELS[i]])[None], len(p) - 1, 0))
            out.append(dict(pos=np.concatenate(RA), pos2=np.concatenate(RB), size=0.8,
                            color=np.concatenate(RC) * (1.6 * (1 - warm) + 1.0 * warm) + line_col * 0.4 * warm,
                            alpha=0.85 * fade, kind="line"))
        on = t >= self.city_t
        if on.any():
            age = t - self.city_t[on]
            out.append(dict(pos=self.city[on], size=self.city_s[on] * 2.0, color=self.city_c[on] * (1.0 + 4.0 * np.exp(-age * 3.0))[:, None],
                            alpha=_ss(0.0, 0.3, age) * fade, kind="spark", emit=2.0, twinkle=0.6))
        return out


class Mother:
    """Heavenly Mother at the breath, a great far constellation seen only from behind: her joints as stars
    and the lines between them over a sheer veiled body of light (the body itself is added in build)."""

    def sample(self, t):
        if not (39.6 <= t <= 50.0):
            return None
        g = float(_ss(40.1, 41.6, t) * (1.0 - _ss(46.5, 49.5, t)))
        if g <= 0.002:
            return None
        c = _P["mother"].constellation(t)
        pos, pairs = np.asarray(c["pos"]), np.asarray(c["pairs"])
        k = np.clip((t - 40.2) / 2.0 * len(pairs) - np.arange(len(pairs)), 0.0, 1.0)
        a, b = pos[pairs[:, 0]], pos[pairs[:, 1]]
        b = a + (b - a) * k[:, None]
        on = k > 0
        out = [dict(pos=pos, size=2.6, color=lin("#fff0cf") * 2.0, alpha=0.95 * g, kind="spark", emit=3.0,
                    twinkle=0.4)]
        if on.any():
            out.append(dict(pos=a[on], pos2=b[on], size=0.5, color=lin("#ffe6b8"), alpha=0.7 * g,
                            kind="line"))
        return out


# ----------------------------------------------------------------------------------------------- the people
def _people():
    from p3d.body import Body
    plex = lambda c2, b=1.0: [dict(name="plexus", bright=1.1 * b, color2=c2), dict(name="glitter", bright=0.45 * b)]  # noqa: E731
    P = {}
    # S0: the first woman (profile) and the man she greets
    P["A"] = Body("woman", at=(-33.3, 0.0), facing=90, garment="coat", hair=True, look=plex("#ffd9a0"),
                  color=SILVER, color2="#ffd9a0", points=90000, detail=dict(head=3),
                  gesture=[(1.3, 2.3, "look_up", dict(amount=10)), (1.9, 6.5, "touch", dict(side="R", to=(-31.6, 1.35, 0.0)))],
                  show=(0.4, 8.0), fade=0.5, seed=1)
    P["B"] = Body("man", at=(-30.7, -0.2), facing=270, garment="tunic", look=plex(COL["Greeting"]),
                  color=SILVER, color2=COL["Greeting"], gesture=[(3.4, 7.0, "open_arms")], points=60000,
                  show=(2.4, 8.0), fade=0.6, seed=2)
    # S1: a walker comes to a kneeling, tired worker; the thanks fill her with light and she rises
    P["C"] = Body("man", at=[(6.84, (-20.6, 0.6)), (9.4, (-17.3, 0.2))], facing=90,
                  motion=[(6.84, "walk"), (9.4, "stand")], garment="coat", look=plex(COL["Gratitude"]),
                  color=SILVER, color2=COL["Gratitude"], gesture=[(9.6, 14.0, "open_arms")], points=60000,
                  effects=[dict(kind="shed", t=6.84)], show=(6.3, 14.2), fade=0.5, seed=3)
    P["D"] = Body("woman", at=(-14.8, 0.0), facing=270, motion=[(6.0, "kneel"), (12.3, "stand")],
                  garment="dress", look=[dict(name="plexus", bright=0.5, color2=COL["Gratitude"]),
                                         dict(name="glitter", bright=1.0, color2=COL["Gratitude"],
                                              weight=lambda t: float(_ss(11.8, 13.0, t)))],
                  color=STEEL, color2=COL["Gratitude"], gesture=[(10.5, 12.3, "look_up", dict(amount=12))],
                  points=60000, show=(6.3, 14.2), fade=0.5, seed=4)
    # S2: back to back; they turn, reach, and their hands touch
    P["E"] = Body("man", at=(-0.75, 0.0), facing=[(13.3, 270.0), (14.6, 270.0), (15.4, 90.0)],
                  motion=[(13.0, "stand"), (14.5, "shuffle"), (15.5, "stand")], garment="tunic",
                  look=plex(COL["Apology"]), color="#ffd9c0", color2=COL["Apology"], points=60000,
                  gesture=[(13.3, 14.6, "bow"), (16.0, 21.0, "touch", dict(side="R", to=_MEET, palm="in"))],
                  show=(12.8, 21.0), fade=0.5, seed=5)
    P["F"] = Body("woman", at=(0.75, 0.0), facing=[(13.3, 90.0), (15.6, 90.0), (16.4, 270.0)],
                  motion=[(13.0, "stand"), (15.5, "shuffle"), (16.5, "stand")], garment="dress", hair=True,
                  look=plex(COL["Inclusiveness"]), color="#f9d6e6", color2=COL["Inclusiveness"], points=60000,
                  gesture=[(16.2, 21.0, "touch", dict(side="L", to=_MEET, palm="in"))],
                  show=(12.8, 21.0), fade=0.5, seed=6)
    # S3: one steps aside and offers the way; the other walks past, turns, and is listened to
    P["H"] = Body("man", at=(16.0, -1.2), facing=[(19.85, 230.0), (23.6, 230.0), (24.4, 110.0)],
                  motion=[(19.5, "stand"), (23.6, "shuffle"), (24.5, "stand")], garment="coat",
                  look=plex(COL["Concession"]), color=SILVER, color2=COL["Concession"], points=60000,
                  gesture=[(20.4, 23.6, "offer", dict(side="L")), (24.4, 28.0, "listen")],
                  show=(19.4, 28.0), fade=0.5, seed=7)
    P["G"] = Body("woman", at=[(19.85, (12.6, 0.6)), (23.4, (18.1, -0.3))], facing=[(19.85, 95.0), (23.4, 95.0), (24.3, 250.0)],
                  motion=[(19.85, "walk"), (23.4, "shuffle"), (24.4, "stand")], garment="robe", hair=True,
                  look=plex(COL["Respect"]), color=SILVER, color2=COL["Respect"], points=60000,
                  effects=[dict(kind="shed", t=19.85)], gesture=[(24.6, 28.0, "offer", dict(side="R"))],
                  show=(19.4, 28.0), fade=0.5, seed=8)
    # S4: a youth on one knee, an elder raising both arms; a woman reaches down and their hands clasp
    P["K"] = Body("man", at=(31.1, 0.0), facing=90, motion=[(26.0, "kneel"), (33.2, "stand")], garment="tunic",
                  look=plex(ELECTRIC), color=STEEL, color2=ELECTRIC, points=60000,
                  gesture=[(28.6, 30.8, "look_up", dict(amount=14)), (31.2, 33.4, "touch", dict(side="R", to=_CLASP, palm="up")),
                           (33.4, 41.0, "raise_hand", dict(side="R", to=(32.05, 2.35, 0.1)))],
                  show=(26.2, 41.0), fade=0.5, seed=9)
    P["L"] = Body("woman", at=(29.3, -0.9), facing=60, stoop=0.5, garment="robe", look=plex(COL["Encouragement"]),
                  color=SILVER, color2=COL["Encouragement"], points=55000,
                  gesture=[(27.0, 32.0, "raise"), (33.6, 41.0, "open_arms")], show=(26.2, 41.0), fade=0.5, seed=10)
    P["M"] = Body("woman", at=(33.0, 0.0), facing=270, garment="dress", look=plex(COL["Consideration"]),
                  color=SILVER, color2=COL["Consideration"], points=60000,
                  gesture=[(29.8, 33.4, "touch", dict(side="R", to=_CLASP, palm="down")),
                           (33.4, 41.0, "raise_hand", dict(side="L", to=(32.05, 2.35, 0.1)))],
                  show=(29.3, 41.0), fade=0.9, seed=11)
    # Heavenly Mother: far beyond the arch, facing away (the camera never passes her), veiled, arms opening
    P["mother"] = Body("woman", at=(0.0, -470.0), facing=180, garment="robe", veil=dict(length=1.5),
                       look="glitter", color="#fff0cf", color2="#cfe0ff", bright=0.8, points=50000, scale=150.0,
                       gesture=[(40.3, 60.0, "open_arms")], show=(39.8, 49.6), fade=1.2, seed=12)
    return P


def _templates():
    from p3d.body import Body
    out = []
    for shape, g in (("woman", "open_arms"), ("man", "raise"), ("woman", "look_up"), ("man", "reach")):
        b = Body(shape, at=(0.0, 0.0), facing=0, garment="tunic" if shape == "man" else "dress", look="glitter",
                 points=3000, gesture=[(0.0, 9.0, g)])
        c = b.constellation(3.0)
        out.append(dict(pos=np.asarray(c["pos"], np.float64), pairs=np.asarray(c["pairs"])))
    return out


def build(scene):
    _P.update(_people())
    scene.add("near stars", StarField())
    scene.add("lines", Lines())
    for name in ("A", "B", "C", "D", "E", "F", "G", "H", "K", "L", "M"):
        _P[name].add(scene, "person " + name)
    _P["mother"].add(scene, "mother body", reflect=True)
    cons = dict(A=(0.0, 0.3, 7.3, 8.0), B=(2.6, 3.4, 7.3, 8.0), C=(6.5, 7.2, 13.6, 14.2), D=(6.5, 7.2, 13.6, 14.2),
                E=(13.0, 13.6, 20.4, 21.0), F=(13.0, 13.6, 20.4, 21.0), G=(19.6, 20.2, 27.4, 28.0),
                H=(19.6, 20.2, 27.4, 28.0), K=(26.4, 27.0, 40.2, 41.0), L=(26.4, 27.0, 40.2, 41.0),
                M=(29.6, 30.4, 40.2, 41.0))
    star_col = dict(A="#ffe6c0", B=COL["Greeting"], C=COL["Gratitude"], D=COL["Gratitude"], E=COL["Apology"],
                    F=COL["Inclusiveness"], G=COL["Respect"], H=COL["Concession"], K="#9fc8ff",
                    L=COL["Encouragement"], M=COL["Consideration"])
    for name, show in cons.items():
        align = ((-33.05, 1.56, 1.75), 1.0) if name == "A" else None
        scene.add("stars of " + name, Constellation(name, SILVER, star_col[name], show, align=align,
                                                    bright=0.8 if name != "A" else 1.0))
    scene.add("web", Web(_templates()))
    scene.add("mother", Mother())
    scene.add("globe", Globe())
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


# ------------------------------------------------------------------------------------------------ the world
LOOKS = dict(
    constel=dict(base="night", sky_top="#02030f", sky_mid="#07103a", sky_hor="#1a2a6e", stars=1.25, milky=1.15,
                 haze=0.35, haze_color="#1c2a66", mist=0.12, mist_color="#22306a", water="#01020a",
                 dust=0.5, bokeh=0.45, dust_color2="#bcd0ff"),
    violet=dict(base="night", sky_top="#05031a", sky_mid="#160c46", sky_hor="#3a2470", stars=1.2, milky=1.0,
                haze=0.35, haze_color="#2c1e60", mist=0.12, mist_color="#2c2266", water="#02010a", dust=0.5,
                bokeh=0.45),
    deep=dict(base="night", sky_top="#010515", sky_mid="#04184a", sky_hor="#0e3f80", stars=1.2, milky=1.1,
              haze=0.35, haze_color="#123c78", mist=0.12, mist_color="#16407a", water="#010309", dust=0.5,
              bokeh=0.45),
    electric=dict(base="night", sky_top="#02041a", sky_mid="#0a1a66", sky_hor="#1840b0", stars=1.25, milky=1.2,
                  haze=0.35, haze_color="#1a3aa0", mist=0.12, mist_color="#1c3a9a", water="#01020c", dust=0.5,
                  bokeh=0.45),
    hush=dict(base="night", sky_top="#03041a", sky_mid="#0e1650", sky_hor="#2a3088", stars=1.4, milky=1.5,
              haze=0.3, haze_color="#24307a", mist=0.1, water="#01020a", dust=0.35, bokeh=0.3),
    globe=dict(base="night", sky_top="#040820", sky_mid="#0e1f5a", sky_hor="#2b4a9a", stars=1.1, milky=0.8,
               haze=0.3, haze_color="#22407e", mist=0.1, water="#01030c", dust=0.3, bokeh=0.2,
               sun_el=-5.0, sun_color="#ffc46a", sun_int=0.5),
    sunrise2=dict(base="sunrise", sun_el=4.0, sun_int=1.1, rays=0.9, clouds=0.2, mist=0.15),
)

WORLD = WORDS.world(dict(
    looks=LOOKS,
    look=[(0.0, "constel"), (13.3, "violet", 0.8), (19.85, "deep", 0.6), (26.79, "electric", 0.6),
          (33.36, "constel", 0.8), (40.6, "hush", 1.6), (45.0, "globe", 2.0), (SUN_BREAK + 0.6, "sunrise2", 2.2),
          (53.4, "day", 2.6)],
    hills=0.0, ripple=0.05, mirror=1.0, clouds=0.0,
    sun_az=180.0,
    star_turn=lambda t: 0.35 * t,
    arch=dict(lit=LIT, colors=[COL[lab] for lab in PW.LABELS], line=Track([(0.0, 0.0), (ARCH_DRAWN, 0.0), (ARCH_DRAWN + 0.6, 1.0)]),
              yaw=_yaw, bright=1.6, **ARCH),
    react=dict(beat=0.35, level=0.25),
))

P3D = dict(
    camera=CAMERA,
    world=WORLD,
    setup=build,
    bursts=[dict(t=33.36, at=_CLASP, strength=2.2, radius=0.16, color="#e6dcff", rise=0.08, fall=0.7),
            dict(t=WEB, at=(0.0, 60.0, -110.0), strength=1.0, radius=0.3, color="#cfe0ff", rise=0.1, fall=0.8),
            dict(t=ARCH_DRAWN + 0.5, at=(0.0, 85.0, -110.0), strength=0.8, radius=0.25, color="#fff0d6", rise=0.15,
                 fall=0.8)],
)

# ------------------------------------------------------------------------------------------------ end card
T_FORM = 52.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="constellation")
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=53.6, t1=55.0, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
_base.TITLE = TITLE
_base.TAGLINE = TAGLINE
FRAGMENTS = []
WAVES = []
