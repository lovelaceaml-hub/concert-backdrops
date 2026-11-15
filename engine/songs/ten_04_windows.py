"""Ten films, film 04: WINDOWS (60 seconds, a promo for The Words of Mother's Love Healing Concert).

LOGLINE
  Every person is a window onto a sky. One of Mother's words flies to them as a flock of birds, and we fly
  through the person into the sky inside them: six crossings in one forward dive that never turns back,
  until Heavenly Mother, seen from behind, opens over us as the day.

THE THREE LAWS OF THIS FILM
  1. A person is a window (refs 08, 02). People are giants of light, 15 to 160 m tall, standing in the lake.
     Inside each silhouette is another whole world, seen through it with its own parallax: the world the
     camera flies into next (the 3D layer's window world, one per frame).
  2. A word is a flock. Each expression arrives as birds (or stars, petals) and is carried at the camera's
     pace while it is read, so it holds its size on screen while the world rushes by; it leaves as birds
     that fly ahead of us into the person it is for.
  3. The camera only goes forward. It glides while a word is read and surges into the person on the
     section's downbeat; a flash of the next world's light covers the threshold and we come out inside.

SHOT BY SHOT (the medley's section starts: 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 42.51, 49.47)
  0.0   PEARL MORNING. Frame 0: a woman's profile as tall as a headland over a pearl lake; inside her the
        sunrise clouds. A flock streaks past the lens to her: "How are you?" We surge into her temple.
  6.84  SUNRISE CLOUDS. We burst out high in her sunrise, swoop down: an Elder opens his arms low and lets a
        Runner go first. "Please, after you." We chase the Runner and dive into his back.
  13.30 THE SEA. Low over a teal sea: a boy blows light from his open palm, a woman kneels to listen. "I'd
        love to hear more about your thoughts." Into the boy's head.
  19.85 A FIELD OF STARS. The fastest flight, the stars doubled in the lake. A worker kneels, a woman bows to
        him. "Thank you..." Into his heart.
  26.79 HARVEST GOLD. Close on two hands, gold and blue, reaching through golden dust (ref 04). "Can I give
        you a hand with anything?" They touch and flare on the beat; we fly into the flare.
  33.36 RAIN AT NIGHT. Silver rain. One kneels, head bowed; the other stands turned away, coming apart.
        "I'm sorry..." The breath (40.21): the rain slows and hangs in the air, she turns and opens her
        arms: "It's okay. I understand." 42.51, the biggest hit: every drop turns to warm light and rises
        as we fly into her heart.
  42.51 BLOSSOM MORNING. Blossom streaming into our face, the rain's lights still rising. A woman kneels in
        prayer: "I'll pray (or root) for you..." A child runs into a father's open arms: "You're amazing..."
  49.47 THE DAY. The haze parts: Heavenly Mother from behind, veiled, rays fanning from behind her head
        (ref 10), opens her arms; 52.26 the day floods out of her; the arch of nine lights wakes over her;
        the end card is whole by 55.0 and held to the last frame. No fade to black.

HOUSE RULES: no facial features (profiles are featureless silhouettes), everyone clothed in garments of
light, Heavenly Mother only from behind, all nine expressions from words.EXPRESSIONS by name (exact wording),
each read for 2.5 s or more, the end card readable for 5 s, nothing dark behind text, no lyrics, no em or
en dash, no fade to black, frame 0 not black.
"""
import numpy as np

import songs.s03_original as _base

# ------------------------------------------------------------------------------------------------ timing
SEC = [0.0, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 42.51, 49.47]    # medley section starts (SECTION-MAP)
X1, X2, X3, X4, X5, X6 = 6.84, 13.30, 19.85, 26.79, 33.36, 42.51      # the six crossings, on the downbeats
BREATH = 40.21
REVEAL = 49.47             # the haze parts on Heavenly Mother
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
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import Mask, lin, show  # noqa: E402,F401
from p3d import words as PW  # noqa: E402
from p3d.camera import Rig, fly  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0          # nothing dark behind any text


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


# ------------------------------------------------------------------------------------------------ worlds
# Each section is a world (a look of the 3D world); the people of a world are windows onto the next one.
LOOKS = dict(
    pearl=dict(base="golden", sky_top="#3f5f9e", sky_mid="#a9a6c8", sky_hor="#f6d8c4", sun_az=184.0, sun_el=9.0,
               sun_color="#fff0dc", sun_int=0.75, clouds=0.30, haze=0.65, haze_color="#e6cfc6", mist=0.55,
               mist_height=14.0, mist_color="#efdcd2", hill_color="#7a7898", water="#3a4566", rays=0.30,
               dust=0.6, dust_color="#fff1dc", dust_color2="#ffd0b8"),
    ember=dict(base="sunrise", sky_top="#0a1646", sky_mid="#3c3a86", sky_hor="#f08a4e", sun_az=176.0, sun_el=3.0,
               sun_color="#ffb46e", sun_int=1.0, clouds=0.85, rays=0.95, stars=0.25, haze_color="#b46a5a",
               mist=0.4, mist_height=10.0, mist_color="#a8604a", water="#120e22", hill_color="#160c22"),
    sea=dict(base="golden", sky_top="#1d4f8e", sky_mid="#78b4cc", sky_hor="#f2ecd6", sun_az=190.0, sun_el=13.0,
             sun_color="#fff3d0", sun_int=0.8, clouds=0.30, haze=0.6, haze_color="#cfe4e2", mist=0.5,
             mist_height=8.0, mist_color="#d6ece8", hills=0.25, water="#1d6872", mirror=0.75, ripple=1.5,
             rays=0.35, dust=0.5, dust_color="#fffbe8", dust_color2="#d8fff4"),
    stars=dict(base="night", sky_top="#02041a", sky_mid="#0a1444", sky_hor="#283270", stars=1.0, milky=1.0,
               hills=0.55, ripple=0.12, mirror=1.0, haze_color="#141a4a", mist=0.25, dust=0.9,
               dust_color="#cfd8ff", dust_color2="#ffe2a8", bokeh=0.9),
    harvest=dict(base="golden", sky_top="#2c2c7a", sky_mid="#c27a64", sky_hor="#ffbe60", sun_az=180.0, sun_el=3.5,
                 sun_color="#ffd48a", sun_int=1.0, clouds=0.30, rays=0.85, haze=0.7, haze_color="#e0a060",
                 mist=0.45, mist_height=3.0, mist_color="#e8b070", water="#3a2a30", hill_color="#4a2a3a",
                 dust=1.0, dust_color="#ffd27a", dust_color2="#ffb060", bokeh=1.0),
    rain=dict(base="night", sky_top="#0b0d2e", sky_mid="#231f52", sky_hor="#4a4470", sun_el=-5.0, stars=0.0,
              milky=0.0, clouds=0.65, haze=0.7, haze_color="#2a2858", mist=0.6, mist_height=6.0,
              mist_color="#3a3a70", ripple=1.8, water="#0e1034", dust=0.3, dust_color="#cfd6ff"),
    blossom=dict(base="golden", sky_top="#1b4898", sky_mid="#76a4dc", sky_hor="#ffe0cc", sun_az=180.0,
                 sun_el=16.0, sun_color="#fff4e0", sun_int=0.85, clouds=0.25, rays=0.5, haze=0.6,
                 haze_color="#f0dcd8", mist=0.4, mist_color="#f8e8e0", water="#2a5a9a", hill_color="#5a7aa8",
                 dust=0.6, dust_color="#fff4f0", dust_color2="#ffc2cf"),
)
MAIN_LOOK = [(0.0, "pearl"), (X1, "ember", 0.0), (X2, "sea", 0.0), (X3, "stars", 0.0), (X4, "harvest", 0.0),
             (X5, "rain", 0.0), (X6, "blossom", 0.0), (FLOOD, "day", 1.6)]
_WIN = [(0.0, "ember"), (X1, "sea"), (X2, "stars"), (X3, "harvest"), (X4, "rain"), (X5, "blossom"), (X6, "ember")]


def window_look(t):
    """The world seen through every window in this frame: the world the camera flies into next."""
    name = _WIN[0][1]
    for t0, n in _WIN:
        if t >= t0:
            name = n
    return name


# ------------------------------------------------------------------------------------------------ people
# Giants: (shape, scale) -> height. Head centre is about 0.93 of the height, the chest 0.72; kneeling 0.66
# and 0.47. Places are the feet (x, z); the camera comes from +z and looks toward -z, so facing 90 looks to
# screen right, 270 to screen left, 180 away from us.
HEIGHTS = dict(woman=1.59, man=1.73, child=1.31)
BUST = dict(at=(0.0, -98.0, -250.0), head=(0.0, 50.0, -250.0))            # S1, scale 100


def _runner_at(t):
    u = min(max((t - X1) / (X2 - X1), 0.0), 1.0)
    return (-20.0 + 38.0 * u, 0.0, 10.0 - 130.0 * u)


def _child_at(t):
    u = _ss(45.0, 48.3, t)
    return (-2.0 + 14.0 * u, 0.0, -36.0 - 26.0 * u)


# ------------------------------------------------------------------------------------------------ camera
def _kick(t0, t1, a, b):
    """A field of view that kicks from a to b as the camera surges into a person."""
    return lambda t: a + (b - a) * _ss(t0, t1, t)


CAMERA = Rig([
    # S1 pearl morning: she is big from frame 0; glide for the Greeting; surge into her temple
    fly([(0.0, (-10.0, 46.0, -105.0), BUST["head"]), (2.0, (-6.0, 48.0, -150.0), BUST["head"]),
         (4.9, (-3.0, 49.5, -186.0), BUST["head"]), (X1, (0.0, 50.0, -234.0), (0.0, 50.0, -262.0))],
        fov=_kick(5.6, X1, 38.0, 52.0), aperture=0.35, focus="target"),
    # S2 sunrise clouds: burst out high, swoop down past the Elder, chase the Runner into his back
    fly([(X1, (-40.0, 34.0, 70.0), (-16.0, 14.0, -60.0)), (8.7, (-34.0, 17.0, 40.0), (-6.0, 16.0, -60.0)),
         (11.7, (-14.0, 15.0, 10.0), (4.0, 16.0, -80.0)), (X2, (18.0, 17.0, -110.0), (18.0, 17.0, -140.0))],
        fov=_kick(12.2, X2, 40.0, 54.0), aperture=0.3, focus=60.0, blend=0.0),
    # S3 the sea: low over the swell; glide; rise into the boy's head
    fly([(X2, (-6.0, 5.0, 70.0), (0.0, 14.0, -70.0)), (15.1, (-2.0, 5.0, 40.0), (2.0, 15.0, -70.0)),
         (18.1, (2.0, 6.0, 5.0), (6.0, 17.0, -70.0)), (X3, (10.0, 22.0, -60.0), (10.0, 22.0, -90.0))],
        fov=_kick(18.6, X3, 40.0, 54.0), aperture=0.3, focus=70.0, blend=0.0),
    # S4 a field of stars: the fastest flight; glide; into the worker's heart
    fly([(X3, (-20.0, 18.0, 160.0), (0.0, 12.0, -80.0)), (21.7, (-10.0, 12.0, 60.0), (2.0, 13.0, -80.0)),
         (25.0, (-2.0, 12.0, 10.0), (8.0, 13.0, -80.0)), (X4, (12.0, 13.0, -70.0), (12.0, 13.0, -100.0))],
        fov=_kick(25.5, X4, 42.0, 56.0), aperture=0.3, focus=80.0, blend=0.0),
    # S5 harvest gold: close on two hands; they touch on the beat (31.62); into the flare
    fly([(X4, (0.3, 1.7, 1.2), (0.0, 1.3, -4.0)), (28.4, (0.2, 1.55, 0.2), (0.0, 1.3, -4.0)),
         (31.4, (0.05, 1.42, -2.2), (0.0, 1.3, -4.0)), (X5, (0.0, 1.3, -3.85), (0.0, 1.3, -6.0))],
        fov=_kick(32.3, X5, 36.0, 50.0), aperture=0.02, focus="target", blend=0.0, near=0.02),
    # S6 rain at night, and the breath: the push slows to a glide; then into her heart on the biggest hit
    fly([(X5, (0.0, 14.0, 80.0), (0.0, 14.0, -60.0)), (35.1, (0.0, 15.0, 52.0), (0.0, 15.0, -60.0)),
         (38.3, (0.0, 15.0, 28.0), (0.0, 15.0, -60.0)), (41.2, (3.0, 15.0, 8.0), (8.0, 15.0, -64.0)),
         (X6, (11.0, 16.0, -54.0), (11.0, 16.0, -80.0))],
        fov=42.0, aperture=0.3, focus=60.0, blend=0.0),
    # S7 blossom morning: low and forward among the people
    fly([(X6, (0.0, 10.0, 70.0), (0.0, 12.0, -60.0)), (44.0, (0.0, 9.0, 45.0), (0.0, 12.0, -60.0)),
         (REVEAL, (0.0, 9.0, -2.0), (0.0, 16.0, -60.0))],
        fov=42.0, aperture=0.25, focus=50.0, blend=0.0),
    # S8 the day: the haze parts; rise toward Heavenly Mother; she sinks to the lower part of the picture as
    # the end card forms above her; still drifting forward on the last frame
    fly([(REVEAL, (0.0, 9.0, -2.0), (0.0, 30.0, -380.0)), (FLOOD, (0.0, 24.0, -110.0), (0.0, 58.0, -380.0)),
         (TITLE_HIT, (0.0, 34.0, -150.0), (0.0, 96.0, -380.0)), (60.0, (0.0, 37.0, -165.0), (0.0, 100.0, -380.0))],
        fov=42.0, aperture=0.0, focus="target", blend=1.0),
], fov=40.0, handheld=0.15, shutter=0.5)

# ------------------------------------------------------------------------------------------------ words
_GAP = dict(away=(0.25, 0.35, -1.0))


def _ride(expr, x, y, px, t_in, r0, r1, t_out, depth=40.0, **kw):
    """A word carried at the camera's pace: it keeps the screen place (x, y) `depth` metres ahead, at an em of
    `px` pixels (1080p) in the middle of its reading moment."""
    tm = 0.5 * (r0 + r1)
    return dict(expr=expr, ride=(x, y, depth), em=PW.em_for(CAMERA, tm, depth, px), t_in=t_in, t_read0=r0,
                t_read1=r1, t_out=t_out, **kw)


_SPECS = [
    _ride("Greeting", 0.5, 0.60, 104, 0.0, 1.9, 4.9, 6.7, arrive="flock", leave="flock", **_GAP),
    _ride("Concession", 0.5, 0.75, 98, 7.2, 8.7, 11.7, 13.2, arrive="flock", leave="flock", **_GAP),
    _ride("Respect", 0.5, 0.74, 86, 13.6, 15.1, 18.1, 19.7, arrive="stars", leave="flock", **_GAP),
    _ride("Gratitude", 0.5, 0.74, 76, 20.1, 21.7, 25.0, 26.6, arrive="petals", leave="flock", **_GAP),
    _ride("Consideration", 0.5, 0.76, 86, 27.0, 28.4, 31.4, 33.2, depth=8.0, arrive="flock", leave="flock",
          **_GAP),
    _ride("Apology", 0.5, 0.75, 82, 33.6, 35.1, 38.3, 39.9, arrive="flock", leave="sink"),
    _ride("Inclusiveness", 0.5, 0.73, 92, 39.0, 40.4, 43.4, 45.0, arrive="flock", leave="bokeh"),
    _ride("Encouragement", 0.5, 0.75, 78, 42.8, 44.0, 46.6, 48.0, arrive="petals", leave="petals"),
    _ride("Compliment", 0.5, 0.75, 90, 45.4, 46.8, 49.4, 51.0, arrive="flock", leave="flock", **_GAP),
]
WORDS = PW.Words(_SPECS, camera=CAMERA)


# ------------------------------------------------------------------------------------------------ point sets
class _Gated:
    """Any point set, drawn only between t0 and t1 (bodies made by helpers that have no show= of their own)."""
    wants_camera = True

    def __init__(self, ps, t0, t1):
        self.ps, self.t0, self.t1 = ps, t0, t1

    def sample(self, t, cam=None):
        if t < self.t0 or t > self.t1:
            return []
        return self.ps.sample(t, cam) if getattr(self.ps, "wants_camera", False) else self.ps.sample(t)

    def gain(self, t):
        g = _ss(self.t0, self.t0 + 0.4, t) * (1.0 - _ss(self.t1 - 0.4, self.t1, t))
        return g * (float(self.ps.gain(t)) if hasattr(self.ps, "gain") else 1.0)


def _rain_tau(t):
    """Time as the rain feels it: it falls (rate 1), slows to a stop in the breath, hangs, then rises."""
    a, b = BREATH + 0.2, BREATH + 1.2          # slows from a, still at b
    if t <= a:
        return t
    if t <= b:
        u = (t - a) / (b - a)
        return a + (b - a) * (u - 0.5 * u * u)
    tau = a + 0.5 * (b - a)
    if t <= X6:
        return tau
    return tau - 0.22 * (t - X6)               # rising, slowly


class Rain:
    """Silver rain round the camera's path in the night world; in the breath it stops in the air, and on the
    biggest hit every drop turns to a warm light and rises (into the blossom world, where it fades)."""

    def __init__(self, n=7000):
        rng = np.random.default_rng(44)
        self.s = rng.random((n, 4))
        self.n = n

    def sample(self, t):
        if t < X5 - 0.1 or t > 47.5:
            return []
        s = self.s
        tau = _rain_tau(t)
        Hh = 60.0
        x = -70.0 + 140.0 * s[:, 0]
        z = -140.0 + 240.0 * s[:, 1]
        y = Hh - np.mod(s[:, 2] * Hh + 34.0 * tau, Hh)
        pos = np.stack([x, y, z], axis=1)
        if t < X6:
            ln = 1.6 * min(1.0, max(0.0, (BREATH + 1.2 - t) / 1.0)) + 0.15
            pos2 = pos + np.array([0.0, ln, 0.0])
            return dict(pos=pos, pos2=pos2, size=0.05, color=lin("#cfd6ff"), alpha=0.55, kind="line")
        g = 1.0 - _ss(45.0, 47.5, t)
        flash = 1.0 + 2.5 * np.exp(-(t - X6) / 0.35)
        col = lin("#ffd9a0") * (1 - s[:, 3:4]) + lin("#ffb4c8") * s[:, 3:4]
        return dict(pos=pos, size=0.18 + 0.12 * s[:, 3], color=col, alpha=0.9 * g, emit=flash, kind="spark",
                    twinkle=0.6)


class Blossom:
    """Blossom streaming toward the camera in the blossom world (painted in its true colours)."""

    def __init__(self, n=1600):
        rng = np.random.default_rng(71)
        self.s = rng.random((n, 6))

    def sample(self, t):
        if t < X6 - 0.2 or t > 52.0:
            return []
        s = self.s
        d = t - X6
        x = -45.0 + 90.0 * s[:, 0] + 3.0 * np.sin(1.3 * d + 6.28 * s[:, 3])
        y = 1.0 + 34.0 * s[:, 1] + 1.5 * np.sin(0.9 * d + 6.28 * s[:, 4])
        z = -110.0 + np.mod(180.0 * s[:, 2] + 9.0 * d, 180.0)
        pos = np.stack([x, y, z], axis=1)
        col = np.where(s[:, 5:6] < 0.55, show("#f0566a"), show("#ffc2cf"))
        rot = np.stack([6.28 * s[:, 3] + d * (0.6 + s[:, 4]), 6.28 * s[:, 5] + d * (1.5 + s[:, 0])], axis=1)
        g = _ss(X6 - 0.2, X6 + 0.4, t) * (1.0 - _ss(50.5, 52.0, t))
        return dict(pos=pos, size=0.55 + 0.35 * s[:, 4], color=col, alpha=0.95 * g, kind="petal", rot=rot,
                    paint=1.0, paint_light=0.3)


def _window(body, name, scene, t0, t1, edge=0.45):
    """Adds a person as a window onto the next world (the mask opens and closes with the body)."""
    body.add(scene, name, mask=dict(sky="world", look=window_look, edge=edge,
                                    strength=lambda t, b=body: float(b.gain(t))))


def _setup(scene):
    from p3d.body import Body, Hands

    # S1: a woman's profile as tall as a headland, hair in long lines of light; inside her, the sunrise
    _window(Body("woman", at=BUST["at"], facing=90.0, scale=100.0, part="bust", hair=True, garment="dress",
                 look="window", color="#ffd9a0", color2="#fff4e6", points=90000, detail=dict(head=3),
                 gesture=[(2.6, 30.0, "look_up", dict(amount=10.0))], show=(0.0, X1 + 0.25), fade=0.05,
                 seed=11.0), "s1_profile", scene, 0.0, X1)
    # S2: the Elder opens his arms low and lets the Runner go first; both are windows onto the sea
    _window(Body("man", at=(-16.0, -60.0), facing=60.0, scale=14.0, garment="coat", stoop=0.3, look="window",
                 color="#ffd0a0", color2="#fff0dc", gesture=[(8.0, 30.0, "open_arms", dict(lift=0.05))],
                 show=(X1, X2 + 0.25), fade=0.5, seed=21.0), "s2_elder", scene, X1, X2)
    _window(Body("man", at=_runner_at, facing=164.0, scale=14.0, garment="tunic", motion="run",
                 look="window", color="#ffe0b0", color2="#ffffff", show=(X1, X2 + 0.25), fade=0.5,
                 effects=[dict(kind="shed", t=X1, n=5000)], seed=22.0), "s2_runner", scene, X1, X2)
    # S3: a boy blows light from his open palm, a woman kneels to listen; windows onto the stars
    _window(Body("child", at=(10.0, -70.0), facing=270.0, scale=18.0, garment="tunic", look="window",
                 color="#ffe6c0", color2="#ffffff", gesture=[(14.0, 30.0, "blow")], show=(X2, X3 + 0.25),
                 fade=0.5, seed=31.0), "s3_boy", scene, X2, X3)
    _window(Body("woman", at=(-12.0, -72.0), facing=90.0, scale=16.0, garment="dress", hair=True,
                 motion="kneel", look="window", color="#ffd9b0", color2="#ffffff",
                 gesture=[(13.6, 30.0, "bow", dict(amount=12.0))], show=(X2, X3 + 0.25), fade=0.5, seed=32.0),
            "s3_listener", scene, X2, X3)
    # S4: a worker kneels, a woman bows to him; windows onto the harvest
    _window(Body("man", at=(12.0, -80.0), facing=270.0, scale=16.0, garment="coat", motion="kneel",
                 look="window", color="#cfd8ff", color2="#ffffff", gesture=[(24.6, 30.0, "look_up")],
                 show=(X3, X4 + 0.25), fade=0.5, seed=41.0), "s4_worker", scene, X3, X4)
    _window(Body("woman", at=(-10.0, -78.0), facing=90.0, scale=16.0, garment="robe", look="window",
                 color="#ffe2b0", color2="#ffffff", gesture=[(21.4, 30.0, "bow", dict(amount=30.0))],
                 show=(X3, X4 + 0.25), fade=0.5, seed=42.0), "s4_thanker", scene, X3, X4)
    # S5: two hands of light, gold and blue, reach for each other and touch on the beat (ref 04)
    for k, v in Hands(meet=(0.0, 1.3, -4.0), t_touch=31.62, approach=3.6, color="#ffcf8a",
                      color2="#8fd0ff").items():
        scene.add("s5_" + k, _Gated(v, X4, X5 + 0.3))
    # S6: one kneels with his head bowed; the other stands turned away, coming apart, then turns and opens
    # her arms in the breath; windows onto the blossom morning
    _window(Body("man", at=(-11.0, -60.0), facing=90.0, scale=14.0, garment="coat", motion="kneel",
                 look="window", color="#cfd6ff", color2="#ffffff", gesture=[(33.8, 30.0, "bow")],
                 show=(X5, X6 + 0.25), fade=0.5, seed=61.0), "s6_sorry", scene, X5, X6)
    _window(Body("woman", at=(11.0, -64.0), facing=[(X5, 90.0), (39.6, 90.0), (40.9, 270.0)], scale=14.0,
                 garment="dress", hair=True, look="window", color="#dcd8ff", color2="#ffffff",
                 gesture=[(41.0, 30.0, "open_arms", dict(lift=0.15))],
                 effects=[dict(kind="shed", t=X5, until=40.0, n=6000, where="back")],
                 show=(X5, X6 + 0.25), fade=0.5, seed=62.0), "s6_hurt", scene, X5, X6)
    # S7: a woman kneels in prayer; a child runs into a father's open arms
    _window(Body("woman", at=(-15.0, -52.0), facing=90.0, scale=12.0, garment="dress", hair=True,
                 motion="kneel", look="window", color="#ffe0d0", color2="#ffffff",
                 gesture=[(X6, 30.0, "pray")], show=(X6, REVEAL + 0.6), fade=0.5, seed=71.0),
            "s7_prayer", scene, X6, REVEAL)
    _window(Body("man", at=(16.0, -66.0), facing=250.0, scale=12.0, garment="coat", look="window",
                 color="#ffe6c8", color2="#ffffff", gesture=[(45.6, 30.0, "open_arms", dict(lift=0.1))],
                 show=(X6, REVEAL + 0.6), fade=0.5, seed=72.0), "s7_father", scene, X6, REVEAL)
    _window(Body("child", at=_child_at, facing=152.0, scale=12.0, garment="tunic", look="window",
                 motion=[(X6, "stand"), (45.0, "run"), (48.3, "stand")], color="#fff0d0", color2="#ffffff",
                 gesture=[(48.2, 30.0, "open_arms", dict(lift=0.8))], show=(X6, REVEAL + 0.6), fade=0.5,
                 seed=73.0), "s7_child", scene, X6, REVEAL)
    # S8: Heavenly Mother, only from behind, veiled, in a long robe of light; she opens her arms low
    Body("woman", at=(0.0, -380.0), facing=180.0, scale=45.0, garment="robe", veil=dict(length=1.5),
         look="glitter", color="#ffd9a0", color2="#fff6e6", bright=1.3, points=110000,
         gesture=[(50.3, 61.0, "open_arms", dict(lift=0.25))], show=(REVEAL, 61.0), fade=0.8,
         seed=81.0).add(scene, "s8_mother", mask=False)

    scene.add("rain", Rain())
    scene.add("blossom", PW.KeepClear(Blossom(), WORDS))
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


# ------------------------------------------------------------------------------------------------ the 3D layer
NINE = [e["color"] for e in PW.EXPRESSIONS]
_HEAD_LIGHT = (0.0, 72.0, -395.0)          # behind Heavenly Mother's head: rays fan from it (ref 10)

P3D = dict(
    camera=CAMERA,
    world=dict(
        looks=LOOKS,
        look=MAIN_LOOK,
        light=dict(pos=_HEAD_LIGHT, color="#fff0d0", size=6.0, rays=1.0,
                   strength=lambda t: 1.4 * _ss(REVEAL, REVEAL + 1.5, t)),
        arch=dict(lit=[FLOOD + 0.3 + 0.22 * k for k in range(9)], span=280.0, height=165.0, z=-430.0,
                  colors=NINE, bright=1.3),
        react=dict(beat=0.4, level=0.25),
    ),
    bursts=[dict(t=X1, at=BUST["head"], strength=2.6, rise=0.18, fall=0.5, color="#ffc890", radius=0.6),
            dict(t=X2, strength=2.4, rise=0.18, fall=0.5, color="#e8fff8", radius=0.6),
            dict(t=X3, strength=2.8, rise=0.15, fall=0.5, color="#c8d4ff", radius=0.6),
            dict(t=X4, strength=2.8, rise=0.15, fall=0.5, color="#ffd890", radius=0.6),
            dict(t=X5, at=(0.0, 1.3, -4.0), strength=3.2, rise=0.15, fall=0.5, color="#fff4dc", radius=0.7),
            dict(t=X6, strength=4.0, rise=0.2, fall=0.7, color="#fff0e0", radius=0.8),
            dict(t=REVEAL, strength=1.6, rise=0.3, fall=0.8, color="#fff8ec", radius=0.8),
            dict(t=FLOOD, at=(0.0, 50.0, -380.0), strength=3.0, rise=0.35, fall=0.9, color="#fff6e0",
                 radius=0.9)],
    clear=[dict(box=(0.10, 0.36, 0.90, 0.88), t0=T_FORM - 0.3, t1=61.0, soft=0.05, amount=0.85)],
    setup=_setup,
)


if __name__ == "__main__":
    src = open(__file__, encoding="utf-8").read()
    assert chr(0x2013) not in src and chr(0x2014) not in src, "no en dash or em dash"
    print("ok")
