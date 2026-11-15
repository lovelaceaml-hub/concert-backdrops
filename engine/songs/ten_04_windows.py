"""Ten films, film 04: WINDOWS (60 seconds, a promo for The Words of Mother's Love Healing Concert).

LOGLINE
  Every person is a window onto a sky. One of Mother's words flies to them as a flock of birds, and we fly
  through the person into the sky inside them: one unbroken forward flight through six people, until
  Heavenly Mother, seen from behind, a window onto the sunrise, takes in every bird and the day floods out.

THE THREE LAWS OF THIS FILM
  1. A person is a window (refs 08, 02). People are giants of light, 30 to 160 m tall, standing in the lake.
     Each is a double exposure: a glowing rim and glitter on the edge, light streaming off them, and inside
     the silhouette the next world, with its own sky, hills and lights at real depth (it moves with parallax).
  2. A word is a flock. Each expression arrives as birds (or stars, petals), is carried at the camera's pace
     while it is read (so it holds its place while the world rushes by), and leaves as birds that fly ahead
     of us into the person it is for.
  3. The camera only goes forward, in one unbroken flight. Each world stands further along the path; the
     camera surges into a person on the section's downbeat and comes out inside the world it saw through
     them, from the very same place: the window covers the whole frame at the threshold, so nothing cuts.

SHOT BY SHOT (the medley's section starts: 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 42.51, 49.47)
  0.0   PEARL MORNING. Frame 0: the concert badge large over a woman's profile as tall as a headland, a
        flock streaming past the lens into her; inside her, the sunrise. "How are you?" Into her head.
  6.84  SUNRISE CLOUDS. Out inside her sunrise. An Elder opens his arms low; a Runner goes first (inside
        them, the sea). "Please, after you." We chase the Runner and dive into his back.
  13.30 THE SEA AT BLUE HOUR. A boy blows light from his open palm; a woman kneels to listen (inside them,
        the stars). "I'd love to hear more about your thoughts." Into the boy's head.
  19.85 A FIELD OF STARS. The fastest flight. A worker kneels; a woman bows to him (inside them, the
        harvest). "Thank you..." Into his heart.
  26.79 HARVEST DUSK. Out of his heart, close on two hands of light, gold and blue, reaching through golden
        dust (ref 04). "Can I give you a hand with anything?" They touch and flare on the beat (31.62).
  33.36 RAIN AT NIGHT. Out of the flare into silver rain. One kneels; the other stands turned away, coming
        apart. "I'm sorry..." The breath (40.21): the rain slows and hangs in the air; she turns and opens
        her arms: "It's okay. I understand." 42.51, the biggest hit: into her heart; the drops become warm
        lights and rise.
  42.51 BLOSSOM MORNING. Blossom streaming into our face. A woman kneels in prayer: "I'll pray (or root)
        for you..." A child runs into a father's open arms: "You're amazing..."
  49.47 THE DAY. Heavenly Mother appears far ahead, from behind, veiled, a window onto the sunrise, rays
        fanning from behind her head (ref 10). She opens her arms and every bird pours into her; 52.26 the
        day floods out of her; the arch of nine lights wakes low behind her; the end card is whole by 55.0
        and held to the last frame. No fade to black.

THE BADGE: "The Words of Mother's Love" over "Healing Concert · Sunday, December 6 · 4:30 PM" (CREDIT), large
on frame 0, settled top left by 2.8 s, faded as the end card forms.

HOUSE RULES: no facial features (profiles are featureless silhouettes), everyone clothed in garments of
light, Heavenly Mother only from behind, all nine expressions from words.EXPRESSIONS by name (exact wording),
each read for 2.5 s or more, one at a time, the end card readable for 5 s, nothing dark behind text, no
lyrics, no em or en dash, no fade to black, frame 0 not black.
"""
import numpy as np

import songs.s03_original as _base

# ------------------------------------------------------------------------------------------------ timing
X1, X2, X3, X4, X5, X6 = 6.84, 13.30, 19.85, 26.79, 33.36, 42.51      # the six crossings, on the downbeats
TOUCH = 31.62              # the two hands touch (a bar start of song 05)
BREATH = 40.21
REVEAL = 49.47             # Heavenly Mother appears
FLOOD = 52.26              # the day floods out of her (bar start of the last song)
TITLE_HIT = 55.0           # the end card is whole (the loudest moment is 54.3 to 55.0)
FORM_DUR = 3.0
T_FORM = TITLE_HIT - FORM_DUR - 0.75
TAG_T0, TAG_T1 = 53.35, TITLE_HIT - 0.08

_base.TOTAL = 60.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 59.6
_base.FADE = _base.Track([(0.0, 1.0), (60.0, 1.0)])          # never black: no fade in, no fade out
_base.EXPOSURE = _base.Track([(0.0, 1.0), (60.0, 1.0)])
for _p in _base.PHRASES:                                     # the flat expressions stay off: the words are light
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27,
                   label_size=48, form=T_FORM, hold=1e9, star=1e9, color="#f0566a", glow="#fff8ec",
                   anim="ribbon")
_base.TITLE_HIT = TITLE_HIT
_base.NINTH = 1e9
_base.TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                          "6720 W Sahara Ave, Las Vegas",
                     sizes=(78, 77), t0=TAG_T0, t1=TAG_T1, color="#1f2a6b", glow="#fff8ec", anim="rise")
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import lin, show  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.camera import Rig, fly  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0          # nothing dark behind any text

# ---- the concert badge (PHASEB UPDATE 3): from frame 0 to the end card, top left
CREDIT = dict(song="The Words of Mother’s Love",
              concert="Healing Concert · Sunday, December 6 · 4:30 PM",
              t_in=-1.0, t_full=0.0,
              t_move=1.6, t_rest=2.8,
              scale=0.48, alpha_rest=0.92,
              margin_x=0.035, margin_top=0.05)


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def credit_state(t, bbox):
    """Centre, scale and strength of the badge; bbox is its size at full card size (demo_gathering.py), faded
    out over a second as the end card starts to form."""
    c = CREDIT
    x0, x1, y0, y1 = bbox
    a_in = _ss(c["t_in"], c["t_full"], t)
    m = _ss(c["t_move"], c["t_rest"], t)
    scale = c["scale"] ** m
    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    tx = c["margin_x"] + c["scale"] * (x1 - x0) / 2.0
    ty = 1.0 - c["margin_top"] - c["scale"] * (y1 - y0) / 2.0
    cx, cy = cx0 * (1 - m) + tx * m, cy0 * (1 - m) + ty * m
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - _ss(T_FORM - 0.2, T_FORM + 0.8, t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# ------------------------------------------------------------------------------------------------ worlds
# Each section is a world (a look of the 3D world); the people of a world are windows onto the next one.
# Every world keeps a deep sky overhead, where the words are read; only the horizon is pale.
LOOKS = dict(
    pearl=dict(base="golden", sky_top="#18286a", sky_mid="#5560a4", sky_hor="#f2bfa6", sun_az=184.0, sun_el=6.0,
               sun_color="#ffe6cc", sun_int=0.7, sun_glow=0.5, clouds=0.30, haze=0.55, haze_color="#c49aa0",
               mist=0.5, mist_height=10.0, mist_color="#d8b4b4", hill_color="#3a3a6a", water="#1e2650",
               rays=0.15, dust=0.6, dust_color="#fff1dc", dust_color2="#ffd0b8"),
    ember=dict(base="sunrise", sky_top="#0a1646", sky_mid="#3c3a86", sky_hor="#f08a4e", sun_az=176.0, sun_el=3.0,
               sun_color="#ffb46e", sun_int=1.0, clouds=0.85, rays=0.9, stars=0.25, haze_color="#b46a5a",
               mist=0.4, mist_height=10.0, mist_color="#a8604a", water="#120e22", hill_color="#160c22"),
    sea=dict(base="golden", sky_top="#0a1f52", sky_mid="#24619a", sky_hor="#bfe4dc", sun_az=204.0, sun_el=2.5,
             sun_color="#fff0cc", sun_int=0.8, sun_glow=0.45, clouds=0.35, haze=0.4, haze_color="#5d9cac",
             mist=0.45, mist_height=6.0, mist_color="#8cc4c8", hills=0.25, hill_color="#163a5a", water="#0b3f52",
             mirror=0.8, ripple=1.4, rays=0.35, stars=0.15, dust=0.5, dust_color="#fffbe8", dust_color2="#bff4ff"),
    stars=dict(base="night", sky_top="#02041a", sky_mid="#0a1444", sky_hor="#283270", stars=1.0, milky=1.0,
               hills=0.55, ripple=0.12, mirror=1.0, haze_color="#141a4a", mist=0.25, dust=0.9,
               dust_color="#cfd8ff", dust_color2="#ffe2a8", bokeh=0.9),
    harvest=dict(base="golden", sky_top="#120c3c", sky_mid="#5a2c6e", sky_hor="#ffae52", sun_az=180.0, sun_el=1.5,
                 sun_color="#ffc870", sun_int=1.0, sun_glow=0.6, clouds=0.30, rays=0.85, haze=0.5,
                 haze_color="#a8506a", mist=0.4, mist_height=3.0, mist_color="#c86a60", water="#1a1022",
                 hill_color="#1c0e26", stars=0.2, dust=1.0, dust_color="#ffd27a", dust_color2="#ffb060", bokeh=1.0),
    rain=dict(base="night", sky_top="#0b0d2e", sky_mid="#231f52", sky_hor="#4a4470", sun_el=-5.0, stars=0.0,
              milky=0.0, clouds=0.65, haze=0.7, haze_color="#2a2858", mist=0.6, mist_height=6.0,
              mist_color="#3a3a70", ripple=1.8, water="#0e1034", dust=0.3, dust_color="#cfd6ff"),
    blossom=dict(base="golden", sky_top="#0c2a72", sky_mid="#3866b8", sky_hor="#ffd2bc", sun_az=150.0,
                 sun_el=4.0, sun_color="#fff0dc", sun_int=0.85, sun_glow=0.45, clouds=0.30, rays=0.45, haze=0.4,
                 haze_color="#9a8ab8", mist=0.35, mist_color="#e8c8d0", water="#123a7a", hill_color="#22325e",
                 dust=0.6, dust_color="#fff4f0", dust_color2="#ffc2cf"),
    dayend=dict(base="day", sun_az=232.0, sun_el=30.0, sun_disc=1.2),
)
MAIN_LOOK = [(0.0, "pearl"), (X1, "ember", 0.0), (X2, "sea", 0.0), (X3, "stars", 0.0), (X4, "harvest", 0.0),
             (X5, "rain", 0.0), (X6, "blossom", 0.0), (FLOOD, "dayend", 1.8)]
_WIN = [(-9.0, "ember"), (X1, "sea"), (X2, "stars"), (X3, "harvest"), (X4, "rain"), (X5, "blossom"),
        (X6, "ember")]


def window_look(t):
    """The world seen through every window in this frame: the world the camera flies into next."""
    name = _WIN[0][1]
    for t0, n in _WIN:
        if t >= t0:
            name = n
    return name


# ------------------------------------------------------------------------------------------------ the path
# Each section is laid out in its own local frame (people near local z = -60, the camera coming from +z);
# the frames stand one after the other along the flight, so that each section starts exactly where the last
# one crossed into a person. Crossing points (local) are measured on the bodies (Body.where at the crossing).
_A = np.array


def _keys(origin, keys):
    o = _A(origin, float)
    return [(t, tuple(_A(p) + o), tuple(_A(q) + o)) for t, p, q in keys]


def _after(cross, start):
    """The origin of the next section's frame: its local start lies on the crossing point."""
    o = _A(cross, float) - _A(start, float)
    o[1] = 0.0
    return o


O1 = _A([0.0, 0.0, 650.0])
BUST_AT, BUST_HEAD = _A([0.0, -98.0, -250.0]), _A([0.1, 55.6, -248.9])           # S1, scale 100
K1 = [(0.0, (-12.0, 44.0, -100.0), (0.0, 60.0, -250.0)), (2.0, (-8.0, 46.0, -146.0), (0.0, 60.0, -250.0)),
      (4.9, (-4.0, 48.0, -182.0), (0.0, 58.0, -250.0)), (X1, (0.0, 55.0, -246.0), (0.0, 55.0, -290.0))]
C1 = O1 + _A(K1[-1][1])

# S2 sunrise clouds: the Elder and the Runner (scale 22); the Runner's chest at X2 measured
O2 = _after(C1, (-24.0, 0.0, 120.0))
RUNNER_AT = (6.0, 5.6)            # he runs from here; his chest is at the crossing point at X2
K2 = [(X1, (-24.0, C1[1], 120.0), (-6.0, 30.0, -40.0)), (8.7, (-20.0, 32.0, 78.0), (-6.0, 24.0, -40.0)),
      (11.7, (-2.0, 28.0, 46.0), (6.0, 26.0, -60.0)), (X2, (7.3, 26.5, -68.0), (7.3, 26.5, -110.0))]
C2 = O2 + _A(K2[-1][1])

# S3 the sea: the boy and the listener; the boy's head at X3 measured
O3 = _after(C2, (-10.0, 0.0, 130.0))
K3 = [(X2, (-10.0, C2[1], 130.0), (0.0, 18.0, -60.0)), (15.3, (-4.0, 11.0, 92.0), (0.0, 18.0, -60.0)),
      (18.3, (2.0, 13.0, 46.0), (6.0, 20.0, -60.0)), (X3, (10.1, 27.2, -59.0), (10.1, 27.2, -100.0))]
C3 = O3 + _A(K3[-1][1])

# S4 the field of stars: the thanker and the worker; the worker's chest at X4 measured
O4 = _after(C3, (-20.0, 0.0, 200.0))
K4 = [(X3, (-20.0, C3[1], 200.0), (0.0, 16.0, -68.0)), (21.8, (-10.0, 17.0, 112.0), (0.0, 16.0, -68.0)),
      (25.2, (-2.0, 15.0, 46.0), (6.0, 16.0, -68.0)), (X4, (8.6, 15.6, -69.5), (8.6, 15.6, -110.0))]
C4 = O4 + _A(K4[-1][1])

# S5 harvest dusk, life size: two hands meet 5 m ahead of where we came out of the worker's heart
O5 = C4.copy()
MEET = O5 + _A([0.0, 0.0, -5.0])
K5 = [(X4, (0.0, 0.0, 0.0), (0.0, 0.0, -5.0)), (28.6, (0.12, 0.10, -3.3), (0.0, 0.0, -5.0)),
      (TOUCH, (0.03, 0.04, -4.35), (0.0, 0.0, -5.0)), (X5, (0.0, 0.0, -4.98), (0.0, 0.0, -7.0))]
C5 = O5 + _A(K5[-1][1])

# S6 rain at night (scale 20): the hurt one's chest at X6 measured
O6 = _after(C5, (0.0, 0.0, 120.0))
K6 = [(X5, (0.0, C5[1], 120.0), (0.0, 18.0, -52.0)), (35.2, (0.0, 17.0, 96.0), (0.0, 18.0, -52.0)),
      (38.3, (0.0, 18.0, 70.0), (0.0, 19.0, -52.0)), (41.3, (4.0, 21.0, 30.0), (9.0, 23.0, -53.0)),
      (X6, (9.2, 22.9, -52.5), (9.2, 22.9, -90.0))]
C6 = O6 + _A(K6[-1][1])

# S7 blossom morning and S8 the day: one move; Heavenly Mother stands far ahead (scale 45)
O7 = _after(C6, (0.0, 0.0, 130.0))
MOTHER_AT = _A([0.0, 0.0, -380.0])
MOTHER_HEAD, MOTHER_HEART = _A([0.3, 69.1, -379.9]), _A([-2.4, 52.4, -386.5])
K7 = [(X6, (0.0, C6[1], 130.0), (0.0, 18.0, -60.0)), (44.6, (0.0, 12.0, 100.0), (0.0, 18.0, -60.0)),
      (REVEAL, (0.0, 13.0, 52.0), (0.0, 24.0, -200.0)), (FLOOD, (0.0, 26.0, -88.0), (0.0, 58.0, -380.0)),
      (TITLE_HIT, (0.0, 34.0, -148.0), (0.0, 94.0, -380.0)), (60.0, (0.0, 37.0, -163.0), (0.0, 98.0, -380.0))]


def _kick(t0, t1, a, b):
    """A field of view that widens as the camera surges into a person."""
    return lambda t: a + (b - a) * _ss(t0, t1, t)


CAMERA = Rig([
    fly(_keys(O1, K1), fov=_kick(5.7, X1, 38.0, 50.0), aperture=0.35, focus="target"),
    fly(_keys(O2, K2), fov=_kick(12.4, X2, 42.0, 54.0), aperture=0.3, focus=90.0, blend=0.25),
    fly(_keys(O3, K3), fov=_kick(18.9, X3, 42.0, 54.0), aperture=0.3, focus=110.0, blend=0.25),
    fly(_keys(O4, K4), fov=_kick(25.8, X4, 42.0, 54.0), aperture=0.3, focus=110.0, blend=0.25),
    fly(_keys(O5, K5), fov=40.0, aperture=0.012, focus="target", blend=0.25, near=0.02),
    fly(_keys(O6, K6), fov=42.0, aperture=0.3, focus=100.0, blend=0.25),
    fly(_keys(O7, K7), fov=42.0, aperture=0.0, focus="target", blend=0.25),
], fov=42.0, handheld=0.12, shutter=0.5)

# ------------------------------------------------------------------------------------------------ words
# One reading moment at a time, each in the deep sky over the people, carried at the camera's pace.
# The badge holds the top left; the words stay below it.


def _ride(expr, y, px, t_in, r0, r1, t_out, depth=40.0, **kw):
    tm = 0.5 * (r0 + r1)
    return dict(expr=expr, ride=(0.5, y, depth), em=PW.em_for(CAMERA, tm, depth, px), t_in=t_in, t_read0=r0,
                t_read1=r1, t_out=t_out, tint=0.55, halo=1.3, **kw)


_AWAY = dict(away=(0.1, -0.15, -1.0), speed=1.4)
_SPECS = [
    _ride("Greeting", 0.70, 104, 1.0, 2.6, 5.6, 6.6, arrive="flock", leave="flock", **_AWAY),
    _ride("Concession", 0.71, 98, 7.3, 8.6, 11.6, 12.6, arrive="flock", leave="flock", **_AWAY),
    _ride("Respect", 0.70, 86, 13.8, 15.2, 18.2, 19.2, arrive="stars", leave="flock", **_AWAY),
    _ride("Gratitude", 0.70, 78, 20.3, 21.6, 24.9, 25.9, arrive="petals", leave="flock", **_AWAY),
    _ride("Consideration", 0.74, 88, 27.0, 28.3, 31.3, 32.3, depth=3.0, arrive="flock", leave="flock",
          away=(0.0, -0.3, -1.0), speed=0.5),
    _ride("Apology", 0.71, 84, 33.9, 35.2, 38.4, 39.3, arrive="flock", leave="sink"),
    _ride("Inclusiveness", 0.71, 94, 39.3, 40.3, 42.9, 43.6, arrive="flock", leave="bokeh"),
    _ride("Encouragement", 0.71, 80, 43.4, 44.6, 47.2, 48.0, arrive="petals", leave="petals"),
    _ride("Compliment", 0.71, 92, 47.4, 48.3, 50.8, 51.5, arrive="flock", leave="flock",
          away=(0.0, -0.2, -1.0), speed=1.8),
]
WORDS = PW.Words(_SPECS, camera=CAMERA)


# ------------------------------------------------------------------------------------------------ point sets
class _Gate:
    """A point set drawn only from t0 to t1: it gathers in over `rise` seconds and is gone at t1 exactly (the
    frame the camera passes through it). gain() also drives the person's window."""
    wants_camera = True

    def __init__(self, ps, t0, t1, rise=0.6, fall=0.05):
        self.ps, self.t0, self.t1, self.rise, self.fall = ps, t0, t1, rise, fall

    def sample(self, t, cam=None):
        if t < self.t0 or t >= self.t1:
            return []
        return self.ps.sample(t, cam) if getattr(self.ps, "wants_camera", False) else self.ps.sample(t)

    def gain(self, t):
        if t < self.t0 or t >= self.t1:
            return 0.0
        g = _ss(self.t0, self.t0 + self.rise, t) if self.rise > 0 else 1.0
        g *= (1.0 - _ss(self.t1 - self.fall, self.t1, t)) if self.fall > 0 else 1.0
        return g * (float(self.ps.gain(t)) if hasattr(self.ps, "gain") else 1.0)


class Motes:
    """Lights drifting in a box of the world: the depth inside a window (seen only through the people) or
    the air of a world. kind soft or spark; sizes in metres."""

    def __init__(self, center, half, n, colors, size=(0.3, 1.2), kind="soft", alpha=0.7, drift=(0.0, 0.4, 0.0),
                 twinkle=0.6, emit=1.0, seed=1):
        rng = np.random.default_rng(seed)
        self.c, self.h = _A(center, float), _A(half, float)
        self.s = rng.random((n, 6))
        cols = [lin(c) for c in colors]
        pick = np.clip(np.floor(self.s[:, 4] * len(cols)).astype(int), 0, len(cols) - 1)
        self.col = np.array([cols[k] for k in pick])
        self.size = size[0] + (size[1] - size[0]) * self.s[:, 5] ** 2
        self.kind, self.alpha, self.drift, self.tw, self.emit = kind, alpha, _A(drift, float), twinkle, emit

    def sample(self, t):
        s = self.s
        p = (s[:, :3] * 2.0 - 1.0) * self.h + self.drift * t
        p = np.mod(p + self.h, 2.0 * self.h) - self.h
        p = p + self.c + np.stack([np.sin(0.4 * t + 6.28 * s[:, 3]), np.zeros(len(s)),
                                    np.cos(0.3 * t + 6.28 * s[:, 4])], axis=1) * 1.5 * (self.h[1] > 2.0)
        return dict(pos=p, size=self.size, color=self.col, alpha=self.alpha, kind=self.kind, twinkle=self.tw,
                    emit=self.emit)


def _sm(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


class Flock:
    """Birds flying from a field of starts to one point (into a person), each on its own curve, as a pure
    function of time; near the lens they are big soft wings."""
    wants_camera = True

    def __init__(self, target, start_center, start_half, n, t0, t1, dur=(2.2, 3.6), size=(1.2, 2.4),
                 color="#fff4e0", seed=5, alpha=0.85):
        rng = np.random.default_rng(seed)
        self.target = _A(target, float)
        self.s = rng.random((n, 8))
        self.p0 = _A(start_center, float) + (self.s[:, :3] * 2.0 - 1.0) * _A(start_half, float)
        self.dur = dur[0] + (dur[1] - dur[0]) * self.s[:, 3]
        self.ts = t0 + (t1 - t0 - self.dur) * self.s[:, 4]
        mid = 0.5 * (self.p0 + self.target[None, :])
        self.c = mid + (self.s[:, 5:8] * 2.0 - 1.0) * _A([40.0, 22.0, 30.0])
        self.size = size[0] + (size[1] - size[0]) * self.s[:, 5]
        self.col = lin(color)
        self.alpha, self.t0, self.t1 = alpha, t0, t1

    def _at(self, u, vis):
        u = u[:, None]
        return (1 - u) ** 2 * self.p0[vis] + 2 * (1 - u) * u * self.c[vis] + u * u * self.target[None, :]

    def sample(self, t, cam=None):
        if t < self.t0 - 0.1 or t > self.t1 + 0.1:
            return []
        u = (t - self.ts) / self.dur
        vis = (u > 0.0) & (u < 1.0)
        if not vis.any():
            return []
        uu = u[vis]
        e = uu * uu * (3.0 - 2.0 * uu) * 0.35 + uu * 0.65
        p = self._at(e, vis)
        v = self._at(np.clip(e + 0.01, 0.0, 1.0), vis) - p
        if cam is not None:
            r, up, _ = cam.basis()
            rot = np.arctan2(v @ np.asarray(up, float), v @ np.asarray(r, float))
        else:
            rot = np.arctan2(v[:, 1], v[:, 0])
        a = self.alpha * _sm(uu / 0.08) * (1.0 - _sm((uu - 0.86) / 0.14))
        return dict(pos=p, size=self.size[vis] * (1.0 - 0.6 * uu), color=self.col, alpha=a, kind="bird",
                    rot=rot, seed=self.s[vis, 6])


def _rain_tau(t):
    """Time as the rain feels it: it falls (rate 1), slows to a stop in the breath, hangs, then rises."""
    a, b = BREATH + 0.2, BREATH + 1.2
    if t <= a:
        return t
    if t <= b:
        u = (t - a) / (b - a)
        return a + (b - a) * (u - 0.5 * u * u)
    tau = a + 0.5 * (b - a)
    if t <= X6:
        return tau
    return tau - 0.22 * (t - X6)


class Rain:
    """Silver rain round the flight in the night world; in the breath it stops in the air, and on the
    biggest hit every drop turns to a warm light and rises (into the blossom world, where it fades)."""
    wants_camera = True

    def __init__(self, origin, n=9000):
        rng = np.random.default_rng(44)
        self.s = rng.random((n, 4))
        self.o = _A(origin, float)

    def sample(self, t, cam=None):
        if t < X5 - 0.05 or t > 46.5:
            return []
        s = self.s
        tau = _rain_tau(t)
        hh = 60.0
        x = -70.0 + 140.0 * s[:, 0]
        z = -150.0 + 300.0 * s[:, 1]
        y = hh - np.mod(s[:, 2] * hh + 34.0 * tau, hh)
        pos = np.stack([x, y, z], axis=1) + self.o
        near = 1.0
        if cam is not None:
            d = np.linalg.norm(pos - np.asarray(cam.pos, np.float64)[None, :], axis=1)
            near = np.clip((d - 10.0) / 14.0, 0.0, 1.0)
        if t < X6:
            ln = 1.1 * min(1.0, max(0.0, (BREATH + 1.2 - t) / 1.0)) + 0.12
            pos2 = pos + np.array([0.0, ln, 0.0])
            g = _ss(X5 - 0.05, X5 + 0.5, t)
            return dict(pos=pos, pos2=pos2, size=0.025, color=lin("#d6dcff"), alpha=0.42 * near * g, kind="line")
        g = 1.0 - _ss(44.5, 46.5, t)
        flash = 1.0 + 2.5 * np.exp(-(t - X6) / 0.35)
        col = lin("#ffd9a0") * (1 - s[:, 3:4]) + lin("#ffb4c8") * s[:, 3:4]
        return dict(pos=pos, size=0.16 + 0.10 * s[:, 3], color=col, alpha=0.9 * g * near, emit=flash,
                    kind="spark", twinkle=0.6)


class Blossom:
    """Blossom streaming toward the camera in the blossom world (painted in its true colours); the same
    petals as light only inside the windows of the rain world."""

    def __init__(self, origin, paint=True, n=1600):
        rng = np.random.default_rng(71)
        self.s = rng.random((n, 6))
        self.o, self.paint = _A(origin, float), paint

    def sample(self, t):
        s = self.s
        d = t - X6
        x = -55.0 + 110.0 * s[:, 0] + 3.0 * np.sin(1.3 * d + 6.28 * s[:, 3])
        y = 1.0 + 40.0 * s[:, 1] + 1.5 * np.sin(0.9 * d + 6.28 * s[:, 4])
        z = -120.0 + np.mod(260.0 * s[:, 2] + 9.0 * d, 260.0)
        pos = np.stack([x, y, z], axis=1) + self.o
        rot = np.stack([6.28 * s[:, 3] + d * (0.6 + s[:, 4]), 6.28 * s[:, 5] + d * (1.5 + s[:, 0])], axis=1)
        if not self.paint:
            return dict(pos=pos, size=0.7 + 0.4 * s[:, 4], color=lin("#ffd0dc"), alpha=0.8, kind="petal", rot=rot)
        col = np.where(s[:, 5:6] < 0.55, show("#f0566a"), show("#ffc2cf"))
        g = 1.0 - _ss(50.5, 52.0, t)
        return dict(pos=pos, size=0.55 + 0.35 * s[:, 4], color=col, alpha=0.95 * g, kind="petal", rot=rot,
                    paint=1.0, paint_light=0.3)


# ------------------------------------------------------------------------------------------------ people
def _look(color, color2, bright=1.0):
    """A window with a glowing edge: the window look (light rim, a few stars) and a soft rim of light."""
    return [dict(name="window", bright=1.5 * bright, size=1.5, color=color, color2=color2),
            dict(name="rim", bright=0.55 * bright, color=color2, color2=color)]


def _person(scene, name, t0, t1, shape, at, origin, scale=22.0, edge=0.55, grow=None, shed=True, rise=0.6,
            **kw):
    """Adds a giant of light that is a window onto the next world, standing at `at` (local) in the section
    whose frame starts at `origin`; it gathers in after t0 and is gone at t1 (the camera has passed in)."""
    from p3d.body import Body
    o = _A(origin, float)
    if len(at) == 2:
        place = (at[0] + o[0], o[1], at[1] + o[2])
    else:
        place = tuple(_A(at, float) + o)
    fx = list(kw.pop("effects", []))
    if shed:
        fx.append(dict(kind="shed", t=t0, n=5000, speed=0.3, rise=0.12, where="back"))
    color, color2 = kw.pop("color", "#ffe0b0"), kw.pop("color2", "#ffffff")
    b = Body(shape, at=place, scale=scale, look=_look(color, color2, kw.pop("bright", 1.0)), effects=fx,
             show=(t0 - 0.02, t1 + 0.02), fade=0.02, color=color, color2=color2, **kw)
    gate = _Gate(b, t0, t1, rise=rise)
    mk = dict(sky="world", look=window_look, edge=edge, strength=gate.gain)
    if grow is not None:
        mk["grow"] = grow
    scene.add(name, gate, mask=b.mask(**mk))
    return b


def _setup(scene):
    from p3d.body import Hands

    # S1: a woman's profile as tall as a headland; inside her, the sunrise; light streams off the back of her
    _person(scene, "s1_profile", -1.0, X1, "woman", tuple(BUST_AT), O1, scale=100.0, part="bust", facing=90.0,
            garment="dress", points=90000, detail=dict(head=3), color="#ffd9a0", color2="#fff4e6", bright=0.7,
            gesture=[(2.6, 30.0, "look_up", dict(amount=10.0))], edge=0.7, grow=0.35, rise=0.0, seed=11.0)
    # S2: the Elder opens his arms low and lets the Runner go first; inside them, the sea
    _person(scene, "s2_elder", X1, X2, "man", (-18.0, -40.0), O2, facing=90.0, garment="coat", stoop=0.3,
            gesture=[(7.8, 30.0, "open_arms", dict(lift=0.05))], color="#ffd0a0", seed=21.0)
    _person(scene, "s2_runner", X1, X2, "man", RUNNER_AT, O2, facing=180.0, garment="tunic",
            motion=[(X1, "run", dict(speed=0.5))], color="#ffe0b0", seed=22.0)
    # S3: a boy blows light from his open palm; a woman kneels to listen; inside them, the stars
    _person(scene, "s3_boy", X2, X3, "child", (12.0, -60.0), O3, facing=270.0, garment="tunic",
            gesture=[(13.9, 30.0, "blow")], color="#d8f4ff", color2="#ffffff", seed=31.0,
            effects=[dict(kind="shed", t=14.4, n=4000, where=[1], dir=(0.0, 0.3, 1.0), speed=0.6, rise=0.05)])
    _person(scene, "s3_listener", X2, X3, "woman", (-16.0, -64.0), O3, facing=90.0, garment="dress", hair=True,
            motion="kneel", gesture=[(13.6, 30.0, "bow", dict(amount=12.0))], color="#d8f4ff", seed=32.0)
    # S4: a worker kneels; a woman bows to him; inside them, the harvest
    _person(scene, "s4_worker", X3, X4, "man", (12.0, -70.0), O4, facing=270.0, garment="coat", motion="kneel",
            gesture=[(24.6, 30.0, "look_up")], color="#cfd8ff", seed=41.0)
    _person(scene, "s4_thanker", X3, X4, "woman", (-12.0, -66.0), O4, facing=90.0, garment="robe",
            gesture=[(21.3, 30.0, "bow", dict(amount=30.0))], color="#ffe2b0", seed=42.0)
    # S5: two hands of light, gold and blue, reach for each other and touch on the beat (ref 04)
    for k, v in Hands(meet=tuple(MEET), t_touch=TOUCH, approach=3.4, color="#ffcf8a", color2="#8fd0ff",
                      points=60000).items():
        scene.add("s5_" + k, _Gate(v, X4, X5, rise=0.5))
    # S6: one kneels, head bowed; the other stands turned away, coming apart, then turns and opens her arms
    _person(scene, "s6_sorry", X5, X6, "man", (-12.0, -50.0), O6, scale=20.0, facing=90.0, garment="coat",
            motion="kneel", gesture=[(33.8, 30.0, "bow")], color="#cfd6ff", seed=61.0)
    _person(scene, "s6_hurt", X5, X6, "woman", (12.0, -54.0), O6, scale=20.0, garment="dress", hair=True,
            facing=[(X5, 90.0), (39.6, 90.0), (40.9, 270.0)], gesture=[(41.0, 30.0, "open_arms", dict(lift=0.15))],
            effects=[dict(kind="shed", t=X5, until=40.0, n=7000, where="back", dir=(1.0, 0.3, 0.0), speed=0.8)],
            color="#dcd8ff", seed=62.0)
    # S7: a woman kneels in prayer; a child runs into a father's open arms
    _person(scene, "s7_prayer", X6, REVEAL + 0.8, "woman", (-18.0, -50.0), O7, scale=20.0, facing=90.0,
            garment="dress", hair=True, motion="kneel", gesture=[(X6, 30.0, "pray")], color="#ffe0d0", seed=71.0)
    _person(scene, "s7_father", X6, REVEAL + 0.8, "man", (15.0, -71.0), O7, scale=20.0, facing=300.0,
            garment="coat", gesture=[(46.4, 30.0, "open_arms", dict(lift=0.1))], color="#ffe6c8", seed=72.0)
    _person(scene, "s7_child", X6, REVEAL + 0.8, "child", (-2.0, -44.0), O7, scale=20.0, facing=150.0,
            garment="tunic", motion=[(X6, "stand"), (45.6, "run", dict(speed=0.45)), (48.0, "stand")],
            gesture=[(47.8, 30.0, "open_arms", dict(lift=0.9))], color="#fff0d0", seed=73.0)
    # S8: Heavenly Mother, only from behind, veiled, in a long robe of light: a window onto the sunrise
    _person(scene, "s8_mother", REVEAL, 61.0, "woman", tuple(MOTHER_AT), O7, scale=45.0, facing=180.0,
            garment="robe", veil=dict(length=1.5), points=110000, color="#ffe2b0", color2="#fff6e6", bright=1.3,
            gesture=[(50.2, 61.0, "open_arms", dict(lift=0.25))], edge=0.9, grow=2.2, rise=1.2, shed=False,
            effects=[dict(kind="shed", t=REVEAL, n=7000, where="top", speed=0.5, rise=0.5)], seed=81.0)

    # the depth inside each window, then the air of that world once we are in it
    ember2 = Motes(O2 + _A([0.0, 40.0, -40.0]), (140.0, 40.0, 160.0), 1400, ("#ffc890", "#ff9e6e", "#fff0d0"),
                   size=(0.4, 1.6), seed=2)
    sea3 = Motes(O3 + _A([0.0, 1.0, -60.0]), (160.0, 0.9, 170.0), 2400, ("#ffffff", "#d8fff4"),
                 size=(0.15, 0.45), kind="spark", alpha=0.9, drift=(0.0, 0.0, 0.0), twinkle=1.0, emit=2.0, seed=3)
    stars4 = Motes(O4 + _A([0.0, 110.0, -320.0]), (420.0, 110.0, 120.0), 1800, ("#ffffff", "#cfd8ff", "#ffe2a8"),
                   size=(0.8, 2.2), kind="spark", alpha=0.9, drift=(0.0, 0.0, 0.0), twinkle=1.0, emit=2.5, seed=4)
    gold5 = Motes(MEET + _A([0.0, 0.0, -2.0]), (4.0, 2.0, 5.0), 900, ("#ffd27a", "#ffb060", "#fff0c0"),
                  size=(0.01, 0.05), alpha=0.8, drift=(0.05, 0.03, 0.0), seed=5)
    gold5w = Motes(O5 + _A([0.0, 0.0, -60.0]), (60.0, 18.0, 60.0), 1400, ("#ffd27a", "#ffb060"), size=(0.2, 0.7),
                   seed=6)
    ember7 = Motes(O7 + _A([0.0, 50.0, -300.0]), (180.0, 50.0, 160.0), 1600, ("#ffc890", "#ff9e6e", "#fff0d0"),
                   size=(0.6, 2.2), seed=7)
    for name, ps, a, b, win in (
            ("in_s1", ember2, -1.0, X1, True), ("air_s2", ember2, X1, X2, False),
            ("in_s2", sea3, X1, X2, True), ("air_s3", sea3, X2, X3, False),
            ("in_s3", stars4, X2, X3, True), ("air_s4", stars4, X3, X4, False),
            ("in_s4", gold5w, X3, X4, True), ("air_s5", gold5, X4, X5, False),
            ("in_s7", ember7, X6, 61.0, True)):
        scene.add(name, PW.KeepClear(_Gate(ps, a, b, rise=0.0, fall=0.0), WORDS), window=win, reflect=not win)
    scene.add("in_s6", _Gate(Blossom(O7, paint=False), X5, X6, rise=0.0, fall=0.0), window=True, reflect=False)
    scene.add("rain", Rain(O6), reflect=False)
    scene.add("blossom", PW.KeepClear(_Gate(Blossom(O7), X6 - 0.02, 52.0, rise=0.3, fall=0.0), WORDS))
    # birds: into the first profile from frame 0, and every bird of the film into Heavenly Mother at the end
    scene.add("birds_s1", PW.KeepClear(Flock(O1 + BUST_HEAD, O1 + _A([-10.0, 60.0, -80.0]), (60.0, 26.0, 40.0),
                                             260, -3.0, X1 - 0.3, dur=(2.4, 3.8), size=(1.4, 2.6), seed=8), WORDS))
    scene.add("birds_s8", PW.KeepClear(Flock(O7 + MOTHER_HEART, O7 + _A([0.0, 60.0, -120.0]),
                                             (200.0, 55.0, 150.0), 1600, REVEAL + 0.3, FLOOD + 1.6,
                                             dur=(1.8, 3.2), size=(1.6, 3.0), seed=9), WORDS))
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


# ------------------------------------------------------------------------------------------------ the 3D layer
NINE = [e["color"] for e in PW.EXPRESSIONS]
_HEAD_LIGHT = tuple(O7 + MOTHER_HEAD + _A([0.0, 3.0, -14.0]))     # behind her head: rays fan from it (ref 10)

P3D = dict(
    camera=CAMERA,
    world=dict(
        looks=LOOKS,
        look=MAIN_LOOK,
        light=dict(pos=_HEAD_LIGHT, color="#fff0d0", size=10.0, rays=1.0,
                   strength=lambda t: 2.6 * _ss(REVEAL + 0.4, REVEAL + 2.0, t)),
        # the arch of nine lights: a low arc behind Heavenly Mother, under the end card
        arch=dict(lit=[FLOOD + 0.4 + 0.22 * k for k in range(9)], span=210.0, height=72.0,
                  z=float(O7[2] + MOTHER_AT[2] - 50.0), colors=NINE, bright=1.6),
        react=dict(beat=0.35, level=0.2),
    ),
    bursts=[dict(t=X1, strength=0.7, rise=0.12, fall=0.4, color="#ffc890", radius=0.35),
            dict(t=X2, strength=0.7, rise=0.12, fall=0.4, color="#cff4f0", radius=0.35),
            dict(t=X3, strength=0.8, rise=0.10, fall=0.4, color="#c8d4ff", radius=0.35),
            dict(t=X4, strength=0.8, rise=0.10, fall=0.4, color="#ffd890", radius=0.35),
            dict(t=X5, at=tuple(MEET), strength=1.5, rise=0.15, fall=0.45, color="#fff0d0", radius=0.45),
            dict(t=X6, strength=1.0, rise=0.15, fall=0.6, color="#fff0e0", radius=0.4),
            dict(t=FLOOD, at=tuple(O7 + MOTHER_HEART), strength=1.1, rise=0.35, fall=0.9, color="#fff6e0",
                 radius=0.35)],
    clear=[dict(box=(0.10, 0.36, 0.90, 0.88), t0=T_FORM - 0.3, t1=61.0, soft=0.05, amount=0.85)],
    setup=_setup,
)


if __name__ == "__main__":
    src = open(__file__, encoding="utf-8").read()
    assert chr(0x2013) not in src and chr(0x2014) not in src, "no en dash or em dash"
    print("ok")
