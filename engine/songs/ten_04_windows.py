"""Ten films, film 04: WINDOWS (60 seconds, a promo for The Words of Mother's Love Healing Concert).

LOGLINE
  Every person is a window onto a sky. One of Mother's words flies to them as a flock of birds, and we fly
  through the window into the world inside: one unbroken forward flight, where each world holds people who
  act out the next of the nine words, until Heavenly Mother, seen from behind, a silhouette full of stars,
  takes in every bird and the day floods out.

THE THREE LAWS OF THIS FILM
  1. A person is a window (refs 08, 02; refs2 p07, p02). Inside a silhouette is the next world, at real
     depth (it moves with parallax), with a glowing rim and light streaming off the edge.
  2. A word is a flock. Each expression arrives as birds (or stars, petals) that land on crisp letters, is
     carried at the camera's pace while it is read, and leaves as birds.
  3. The camera only goes forward, in one unbroken flight: it surges into a window on a section's downbeat
     and comes out, from the very same place, inside the world it saw through it.

THE ACTING PLAN (every expression acted while it reads; style and scale change every time)
  1 Greeting "How are you?" (0.0, pearl morning). EXTREME CLOSE and FAR at once: a woman's profile as tall
    as a headland, filled with the sunrise (p07). Inside her, far off on the shore of the sunrise world, a
    man looks out over the water; a woman comes up behind him and lays her hand on his shoulder; he turns
    round to her and lifts his hand in greeting. Small sparkling figures (p09), seen only through her.
  2 Concession "Please, after you." (6.84, sunrise clouds). FULL FIGURES, MID: a door of light stands on the
    water, a window onto the sea. A man beside the path steps back and opens his palm toward it; a woman
    walks past him and through the door first. Plexus wireframe people (p01, refs 03, 12). We follow her in.
  3 Respect "I'd love to hear more about your thoughts." (13.30, the sea at blue hour). HALF FIGURES,
    CLOSE: two people face each other over the sea. He speaks with an open hand raised, a stream of light
    flowing from it; she leans in, her head tilted, listening, and nods. Profiles outlined in sparks (p06),
    filled with the starry night. Into his head.
  4 Gratitude "Thank you..." (19.85, a field of stars). MANY: a man stands on the starry shore and the
    people round him bow to him, one after another, in thanks; he bows back. Gold glitter (p08); he is a
    window onto the harvest. Into his heart.
  5 Consideration "Can I give you a hand with anything?" (26.79, harvest dusk). EXTREME CLOSE, HANDS: a
    blue hand reaches down from above, a gold hand reaches up from below; they clasp on the beat and the
    upper hand lifts the lower one up (helping someone up, told by the hands alone, ref 04).
  6 Apology "I'm sorry..." (33.36, rain at night). FULL FIGURES, LIFE SIZE, CLOSE: two people kneel face to
    face in the rain; she is bowed and coming apart into flakes (p03); he bows his head, his open hands low.
    Inclusiveness "It's okay. I understand." (37.7): her flakes fly back, both rise and hold each other. The
    breath (40.21): they hold on while the rain stops in the air and the date is written in light above them.
    42.51, the biggest hit: the drops turn to warm light and rise, and we fly into their embrace. Both are windows onto the blossom morning, with a rim of light.
  7 Encouragement "I'll pray (or root) for you..." (42.51, blossom morning). PARTIAL, CLOSE: a young woman
    kneels in profile, hands joined in prayer, head bowed, a small sparkling figure in the rising lights
    (p09). Compliment "You're amazing..." (47): FULL FIGURES: a father lifts his little daughter into his
    arms; embers of joy burst off her (p04).
  8 The day (49.47). FAR, A GIANT: Heavenly Mother, only from behind, veiled, a silhouette full of stars
    (p02), rays fanning from behind her head (ref 10). She opens her arms and every bird pours into her;
    52.26 the day floods out of her; the arch of nine lights wakes low behind her; the end card is whole by
    55.0 and held to the last frame. No fade to black.

TITLE AND DATE (PHASEB UPDATE 7, the TITLES key): A, the opening title over the sky above the giant profile
(0 to 4 s); B, a discreet signature in three calm stretches between the words (bottom corners, night palette);
C, "December 6" in light across the rain sky in the breath (40.21), over the two who hold each other, bursting
on the biggest hit (42.51). The end card as it is.

HOUSE RULES: artistic, never photorealistic people; Heavenly Mother only from behind; everyone clothed in
garments of light; all nine expressions from words.EXPRESSIONS by name (exact wording), each read for 2.5 s
or more, one at a time, never mirrored; the end card readable for 5 s; nothing dark behind text; no lyrics;
no em or en dash; no fade to black; frame 0 not black; no white-out.
"""
import numpy as np

import songs.s03_original as _base

# ------------------------------------------------------------------------------------------------ timing
X1, X2, X3, X4, X5, X6 = 6.84, 13.30, 19.85, 26.79, 33.36, 42.51      # the six crossings, on the downbeats
CLASP = 29.79              # the two hands clasp (a strong hit of song 05)
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

# ---- the title and the date (PHASEB UPDATE 7; drawn by the engine's TITLES once it lands, the corner badge is
# gone): A the opening title over the first image (the profile stands below it, the sky above her is free),
# B a discreet signature in three calm stretches between the words, on calm night sky or water, C "December 6"
# in light across the sky in the breath, over the two who hold each other, bursting on the biggest hit.
TITLES = dict(
    opening=dict(t_end=4.0, y=0.20, palette="night"),
    signature=dict(windows=[(11.6, 13.2, "br", "night"), (24.7, 26.6, "br", "night"), (31.4, 33.0, "bl", "night")]),
    date_light=dict(t_form=BREATH, t_burst=X6, y=0.30, palette="night"),
)
CREDIT = dict(song="The Words of Mother’s Love", concert="Healing Concert",   # the old corner badge: off
              t_in=1e9, t_full=1e9 + 1.0, t_move=1e9 + 2.0, t_rest=1e9 + 3.0, scale=0.34, alpha_rest=0.0,
              margin_x=0.03, margin_top=0.048)


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


# ------------------------------------------------------------------------------------------------ worlds
# Each section is a world (a look of the 3D world); its windows open onto the next one. Every world keeps a
# deep sky overhead, where the words are read; only the horizon is pale, and no sun stands behind a word.
LOOKS = dict(
    pearl=dict(base="golden", sky_top="#16245e", sky_mid="#4a5498", sky_hor="#f2bfa6", sun_az=203.0, sun_el=3.0,
               sun_color="#ffe6cc", sun_int=0.6, sun_glow=0.4, clouds=0.30, haze=0.55, haze_color="#c49aa0",
               mist=0.5, mist_height=10.0, mist_color="#d8b4b4", hill_color="#3a3a6a", water="#1e2650",
               rays=0.15, dust=0.6, dust_color="#fff1dc", dust_color2="#ffd0b8"),
    ember=dict(base="sunrise", sky_top="#0a1646", sky_mid="#3c3a86", sky_hor="#f08a4e", sun_az=176.0, sun_el=3.0,
               sun_color="#ffb46e", sun_int=0.9, clouds=0.85, rays=0.7, stars=0.25, haze_color="#b46a5a",
               mist=0.4, mist_height=10.0, mist_color="#a8604a", water="#120e22", hill_color="#160c22"),
    sea=dict(base="golden", sky_top="#081a4a", sky_mid="#1f5590", sky_hor="#9fd4d0", sun_az=222.0, sun_el=1.5,
             sun_color="#fff0cc", sun_int=0.5, sun_glow=0.3, clouds=0.35, haze=0.3, haze_color="#3d7c90",
             mist=0.35, mist_height=6.0, mist_color="#6aa8b4", hills=0.25, hill_color="#12304e", water="#0a3448",
             mirror=0.8, ripple=1.4, rays=0.2, stars=0.25, dust=0.5, dust_color="#fffbe8", dust_color2="#bff4ff"),
    stars=dict(base="night", sky_top="#02041a", sky_mid="#0a1444", sky_hor="#283270", stars=1.0, milky=1.0,
               hills=0.55, ripple=0.12, mirror=1.0, haze_color="#141a4a", mist=0.25, dust=0.9,
               dust_color="#cfd8ff", dust_color2="#ffe2a8", bokeh=0.9),
    harvest=dict(base="golden", sky_top="#0e0a34", sky_mid="#3a1c5e", sky_hor="#ff9e4a", sun_az=208.0, sun_el=1.5,
                 sun_color="#ffc870", sun_int=0.9, sun_glow=0.4, clouds=0.30, rays=0.6, haze=0.4,
                 haze_color="#a8506a", mist=0.4, mist_height=3.0, mist_color="#c86a60", water="#1a1022",
                 hill_color="#1c0e26", stars=0.2, dust=1.0, dust_color="#ffd27a", dust_color2="#ffb060", bokeh=1.0),
    rain=dict(base="night", sky_top="#0b0d2e", sky_mid="#231f52", sky_hor="#4a4470", sun_el=-5.0, stars=0.0,
              milky=0.0, clouds=0.65, haze=0.7, haze_color="#2a2858", mist=0.5, mist_height=2.0,
              mist_color="#3a3a70", ripple=1.8, water="#0e1034", dust=0.3, dust_color="#cfd6ff"),
    blossom=dict(base="golden", sky_top="#0a2468", sky_mid="#2a56a8", sky_hor="#ffd2bc", sun_az=146.0,
                 sun_el=2.0, sun_color="#fff0dc", sun_int=0.6, sun_glow=0.3, clouds=0.30, rays=0.25, haze=0.3,
                 haze_color="#9a8ab8", mist=0.3, mist_height=2.0, mist_color="#e8c8d0", water="#123a7a",
                 hill_color="#22325e", dust=0.6, dust_color="#fff4f0", dust_color2="#ffc2cf"),
    dayend=dict(base="day", sun_az=232.0, sun_el=30.0, sun_disc=1.2, haze=0.35, mist=0.08),
)
MAIN_LOOK = [(0.0, "pearl"), (X1, "ember", 0.0), (X2, "sea", 0.0), (X3, "stars", 0.0), (X4, "harvest", 0.0),
             (X5, "rain", 0.0), (X6, "blossom", 0.0), (FLOOD, "dayend", 1.8)]
_WIN = [(-9.0, "ember"), (X1, "sea"), (X2, "stars"), (X3, "harvest"), (X4, "rain"), (X5, "blossom"),
        (X6, "stars")]


def window_look(t):
    """The world seen through every window in this frame: the world the camera flies into next."""
    name = _WIN[0][1]
    for t0, n in _WIN:
        if t >= t0:
            name = n
    return name


# ------------------------------------------------------------------------------------------------ the path
# Each section is laid out in its own local frame; the frames stand one after the other along the flight, so
# each section starts exactly where the last one crossed into a window. Crossing points are measured on the
# bodies (Body.where at the crossing, scratchpad probe).
_A = np.array


def _keys(origin, keys):
    o = _A(origin, float)
    return [(t, tuple(_A(p) + o), tuple(_A(q) + o)) for t, p, q in keys]


def _after(cross, start, y=0.0):
    """The origin of the next section's frame: its local start lies on the crossing point."""
    o = _A(cross, float) - _A(start, float)
    o[1] = y
    return o


# S1 pearl morning: the giant profile (scale 100); inside her, a greeting far off on the sunrise shore
O1 = _A([0.0, 0.0, 650.0])
BUST_AT, BUST_HEAD = _A([0.0, -98.0, -250.0]), _A([0.1, 55.6, -248.9])
K1 = [(0.0, (-12.0, 44.0, -100.0), (0.0, 74.0, -250.0)), (2.0, (-8.0, 46.0, -146.0), (0.0, 60.0, -250.0)),
      (4.9, (-4.0, 48.0, -182.0), (0.0, 58.0, -250.0)), (X1, (0.0, 55.0, -246.0), (0.0, 55.0, -290.0))]
C1 = O1 + _A(K1[-1][1])

# S2 sunrise clouds: a door of light (a window onto the sea) and two people (scale 12)
O2 = _after(C1, (-20.0, 0.0, 110.0))
DOOR = dict(c=_A([6.0, 0.0, -95.0]), w=26.0, h=34.0)          # centre of the sill, width, height to the arch
K2 = [(X1, (-20.0, C1[1], 110.0), (0.0, 25.0, -80.0)), (8.6, (-8.0, 20.0, 45.0), (2.0, 18.0, -80.0)),
      (11.6, (2.0, 18.0, 10.0), (6.0, 20.0, -95.0)), (X2, (6.0, 22.0, -94.0), (6.0, 22.0, -140.0))]
C2 = O2 + _A(K2[-1][1])

# S3 the sea at blue hour: two people face each other (scale 26); into his head
O3 = _after(C2, (-6.0, 0.0, 120.0))
K3 = [(X2, (-6.0, C2[1], 120.0), (0.0, 36.0, -70.0)), (15.2, (-3.0, 34.0, 62.0), (0.0, 38.0, -70.0)),
      (18.2, (2.0, 37.0, 22.0), (6.0, 40.0, -70.0)), (X3, (10.56, 43.2, -71.0), (10.56, 43.2, -110.0))]
C3 = O3 + _A(K3[-1][1])

# S4 the field of stars: the crowd that bows (scale 12) and the man they thank (scale 16); into his heart
O4 = _after(C3, (-18.0, 0.0, 160.0))
WORKER_AT = _A([0.0, 0.0, -100.0])
K4 = [(X3, (-18.0, C3[1], 160.0), (0.0, 14.0, -100.0)), (21.6, (-8.0, 18.0, 70.0), (0.0, 15.0, -100.0)),
      (24.9, (-2.0, 17.0, 8.0), (0.0, 17.0, -100.0)), (X4, (0.0, 19.6, -97.6), (0.0, 19.6, -140.0))]
C4 = O4 + _A(K4[-1][1])

# S5 harvest dusk, life size: two hands meet 1.5 m over the water, 12 m ahead; we dive down to them
O5 = _after(C4, (0.0, 0.0, 0.0))
MEET = O5 + _A([0.0, 1.5, -12.0])
LIFT = 0.35                    # how far the upper hand lifts the lower one after the clasp


def _lift(t):
    return LIFT * _ss(CLASP + 0.15, CLASP + 1.7, t)


K5 = [(X4, (0.0, C4[1], 0.0), (0.0, 1.5, -12.0)), (27.6, (0.2, 7.0, -5.5), (0.0, 1.5, -12.0)),
      (28.4, (0.25, 2.3, -8.6), (0.0, 1.5, -12.0)), (CLASP, (0.08, 1.62, -10.4), (0.0, 1.55, -12.0)),
      (31.9, (0.03, 1.8, -11.1), (0.0, 1.85, -12.0)),
      (X5, (0.0, 1.5 + LIFT, -11.97), (0.0, 1.5 + LIFT, -14.0))]
C5 = O5 + _A(K5[-1][1])

# S6 rain at night, life size: the two who kneel, rise and hold each other; into their embrace
O6 = _after(C5, (0.0, 0.0, 9.0))
PAIR6 = _A([0.0, 0.0, 0.0])
K6 = [(X5, (0.0, C5[1], 9.0), (0.0, 0.9, 0.0)), (35.2, (-0.7, 1.25, 5.4), (0.0, 0.75, 0.0)),
      (38.4, (-0.5, 1.15, 4.2), (0.0, 0.8, 0.0)), (41.3, (0.15, 1.4, 2.3), (0.0, 1.3, 0.0)),
      (X6, (0.0, 1.22, -0.03), (0.0, 1.22, -3.0))]
C6 = O6 + _A(K6[-1][1])

# S7 blossom morning, life size, then S8: the camera rises toward Heavenly Mother far ahead (scale 45)
O7 = _after(C6, (0.0, 0.0, 3.0))
PRAYER_AT, FATHER_AT = _A([-1.3, 0.0, -2.6]), _A([1.7, 0.0, -6.8])
MOTHER_AT = _A([0.0, 0.0, -380.0])
MOTHER_HEAD, MOTHER_HEART = _A([0.3, 69.1, -379.9]), _A([-2.4, 52.4, -386.5])
K7 = [(X6, (0.0, C6[1], 3.0), (-1.3, 0.9, -2.6)), (44.6, (-0.55, 0.95, -0.4), (-1.3, 0.8, -2.6)),
      (46.6, (0.55, 1.15, -2.2), (1.6, 1.0, -6.8)), (48.4, (0.9, 1.3, -3.3), (1.7, 1.25, -6.8)),
      (REVEAL, (0.6, 2.2, -4.6), (0.0, 10.0, -200.0)), (FLOOD, (0.0, 22.0, -110.0), (0.0, 58.0, -380.0)),
      (TITLE_HIT, (0.0, 34.0, -150.0), (0.0, 94.0, -380.0)), (60.0, (0.0, 37.0, -165.0), (0.0, 98.0, -380.0))]


def _kick(t0, t1, a, b):
    """A field of view that widens as the camera surges into a window."""
    return lambda t: a + (b - a) * _ss(t0, t1, t)


CAMERA = Rig([
    fly(_keys(O1, K1), fov=_kick(5.7, X1, 38.0, 50.0), aperture=0.35, focus="target"),
    fly(_keys(O2, K2), fov=_kick(12.4, X2, 42.0, 54.0), aperture=0.3, focus=90.0, blend=0.25),
    fly(_keys(O3, K3), fov=_kick(18.9, X3, 42.0, 54.0), aperture=0.3, focus=80.0, blend=0.25),
    fly(_keys(O4, K4), fov=_kick(25.8, X4, 42.0, 54.0), aperture=0.3, focus=100.0, blend=0.25),
    fly(_keys(O5, K5), fov=40.0, aperture=0.012, focus="target", blend=0.25, near=0.02),
    fly(_keys(O6, K6), fov=42.0, aperture=0.02, focus="target", blend=0.25, near=0.02),
    fly(_keys(O7, K7), fov=42.0, aperture=lambda t: 0.02 * (1.0 - _ss(REVEAL, FLOOD, t)), focus="target",
        blend=0.25, near=0.02),
], fov=42.0, handheld=0.12, shutter=0.5)


def _ground_point(t, sx, sy):
    """Where on the lake the camera sees the screen place (sx, sy) at time t (for the greeting inside her)."""
    cam = CAMERA.state(t)
    r, u, f = cam.basis()
    fl = 1.0 / np.tan(np.radians(cam.fov) * 0.5)
    d = f + r * (2.0 * sx - 1.0) * cam.aspect / fl + u * (2.0 * sy - 1.0) / fl
    p = np.asarray(cam.pos, float)
    k = -p[1] / d[1]
    return p + d * k, k


GREET_AT, _GD = _ground_point(4.0, 0.535, 0.20)
GREET_SCALE = float(np.clip(150.0 * _GD / (1.73 * 1569.0), 8.0, 90.0))   # about 150 px tall in the picture

# ------------------------------------------------------------------------------------------------ words
# One reading moment at a time, carried at the camera's pace a little ahead of the lens (nothing comes
# between us and a word); the badge holds the top left and the words keep 40 px from it.


def _clean(t, info):
    """The letters never fly apart: they stay in place, crisp, and fade in as the birds (or stars, petals) of
    the arrival land on them, and fade out as the birds of the leaving lift off (no broken letter shapes)."""
    w, st = info["word"], info["state"]
    if st == "arrive":
        a = (t - w.t_in) / max(w.t_read0 - w.t_in, 1e-6)
        return dict(pos=info["home"], alpha=_ss(0.45, 1.0, a), assist=1.0)
    if st == "leave":
        lv = (t - w.t_read1) / max(w.t_out - w.t_read1, 1e-6)
        return dict(pos=info["home"], alpha=1.0 - _ss(0.0, 0.55, lv), assist=1.0)
    return None


def _ride(expr, y, px, t_in, r0, r1, t_out, depth=6.0, **kw):
    tm = 0.5 * (r0 + r1)
    return dict(expr=expr, ride=(0.5, y, depth), em=PW.em_for(CAMERA, tm, depth, px), t_in=t_in, t_read0=r0,
                t_read1=r1, t_out=t_out, halo=0.9, reflect=False, drive=_clean, **kw)


_AWAY = dict(away=(0.1, -0.15, -1.0), speed=1.4)
_SPECS = [
    _ride("Greeting", 0.72, 104, 3.4, 4.0, 6.9, 7.3, arrive="flock", leave="flock", **_AWAY),
    _ride("Concession", 0.72, 98, 7.6, 8.4, 11.2, 11.5, arrive="flock", leave="flock", **_AWAY),
    _ride("Respect", 0.72, 86, 13.8, 14.8, 17.8, 18.2, arrive="stars", leave="flock", **_AWAY),
    _ride("Gratitude", 0.72, 78, 20.3, 21.3, 24.3, 24.6, arrive="petals", leave="flock", **_AWAY),
    _ride("Consideration", 0.74, 88, 27.4, 28.3, 31.0, 31.3, depth=2.5, arrive="flock", leave="flock",
          away=(0.0, 0.3, -1.0), speed=0.5),
    _ride("Apology", 0.72, 84, 33.7, 34.3, 36.8, 37.05, depth=1.2, arrive="flock", leave="flock", **_AWAY),
    _ride("Inclusiveness", 0.72, 94, 37.15, 37.7, 40.2, 40.45, depth=0.9, arrive="flock", leave="flock", **_AWAY),
    _ride("Encouragement", 0.72, 80, 42.9, 43.6, 46.2, 46.5, depth=1.0, arrive="petals", leave="petals"),
    _ride("Compliment", 0.72, 92, 46.7, 47.5, 50.1, 50.5, depth=1.0, arrive="flock", leave="flock",
          away=(0.0, -0.2, -1.0), speed=1.8),
]
WORDS = PW.Words(_SPECS, camera=CAMERA)


# ------------------------------------------------------------------------------------------------ point sets
class _Gate:
    """A point set drawn only from t0 to t1: it gathers in over `rise` seconds and is gone at t1 exactly (the
    frame the camera passes through it). gain() also drives a person's window."""
    wants_camera = True

    def __init__(self, ps, t0, t1, rise=0.6, fall=0.05, dim=0.0):
        self.ps, self.t0, self.t1, self.rise, self.fall, self.dim = ps, t0, t1, rise, fall, dim

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

    def light(self, t):
        """The gain of the points: as gain(), but out over `dim` seconds before t1 (the window stays)."""
        g = self.gain(t)
        return g * (1.0 - _ss(self.t1 - self.dim, self.t1 - 0.04, t)) if self.dim > 0 else g


class _Lit:
    """The points of a gated person, with their own gain (the window keeps the gate's)."""
    wants_camera = True

    def __init__(self, gate):
        self.gate = gate

    def sample(self, t, cam=None):
        return self.gate.sample(t, cam)

    def gain(self, t):
        return self.gate.light(t)


class Motes:
    """Lights drifting in a box of the world: the depth inside a window (seen only through it) or the air
    of a world. kind soft or spark; sizes in metres."""

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
                                    np.cos(0.3 * t + 6.28 * s[:, 4])], axis=1) * 0.02 * self.h[1]
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
                 color="#fff4e0", seed=5, alpha=0.85, swing=(40.0, 22.0, 30.0)):
        rng = np.random.default_rng(seed)
        self.target = _A(target, float)
        self.s = rng.random((n, 8))
        self.p0 = _A(start_center, float) + (self.s[:, :3] * 2.0 - 1.0) * _A(start_half, float)
        self.dur = dur[0] + (dur[1] - dur[0]) * self.s[:, 3]
        self.ts = t0 + (t1 - t0 - self.dur) * self.s[:, 4]
        mid = 0.5 * (self.p0 + self.target[None, :])
        self.c = mid + (self.s[:, 5:8] * 2.0 - 1.0) * _A(swing, float)
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


class Stream:
    """A soft stream of light flowing from one moving point to another along an arc (a thought passed from a
    speaker's open hand to a listener)."""

    def __init__(self, src, dst, t0, t1, n=900, size=0.25, color="#ffe8c0", arc=0.25, seed=12):
        rng = np.random.default_rng(seed)
        self.s = rng.random((n, 5))
        self.src, self.dst, self.t0, self.t1 = src, dst, t0, t1
        self.size, self.col, self.arc = size, lin(color), arc

    def sample(self, t):
        if t < self.t0 or t > self.t1:
            return []
        a, b = _A(self.src(t), float), _A(self.dst(t), float)
        s = self.s
        u = np.mod(s[:, 0] + 0.45 * (t - self.t0), 1.0)
        L = float(np.linalg.norm(b - a))
        mid = 0.5 * (a + b) + _A([0.0, self.arc * L, 0.0])
        uu = u[:, None]
        p = (1 - uu) ** 2 * a + 2 * (1 - uu) * uu * mid + uu * uu * b
        p = p + (s[:, 1:4] - 0.5) * (0.06 * L) * np.sin(np.pi * uu)
        g = _ss(self.t0, self.t0 + 0.6, t) * (1.0 - _ss(self.t1 - 0.6, self.t1, t))
        return dict(pos=p, size=self.size * (0.5 + s[:, 4]), color=self.col, alpha=0.8 * g * np.sin(np.pi * u),
                    kind="spark", twinkle=0.8, emit=1.5)


class Door:
    """A door of light standing on the water: a bright frame (sill, posts and a round arch), its opening a
    window onto the next world. sample() is the frame; .fill is the opening (the window's shape)."""

    def __init__(self, c, w, h, n=6000, color="#ffe2b0", t0=0.0):
        self.c, self.w, self.h, self.t0 = _A(c, float), w, h, t0
        rng = np.random.default_rng(31)
        r = w * 0.5
        u = rng.random(n)
        L1, L2 = h, np.pi * r                  # each post, and the arch
        tot = 2 * L1 + L2 + w
        d = u * tot
        x, y = np.zeros(n), np.zeros(n)
        m = d < L1
        x[m], y[m] = -r, d[m]
        m2 = (d >= L1) & (d < L1 + L2)
        ang = np.pi - (d[m2] - L1) / r
        x[m2], y[m2] = r * np.cos(ang), h + r * np.sin(ang)
        m3 = (d >= L1 + L2) & (d < 2 * L1 + L2)
        x[m3], y[m3] = r, h - (d[m3] - L1 - L2)
        m4 = d >= 2 * L1 + L2
        x[m4], y[m4] = -r + (d[m4] - 2 * L1 - L2), 0.0
        jit = (rng.random((n, 2)) - 0.5) * 0.9
        self.frame = np.stack([x + jit[:, 0], y + jit[:, 1] + 0.3, np.zeros(n)], axis=1) + self.c
        self.sd = rng.random(n)
        self.col = lin(color)
        gx, gy = np.meshgrid(np.arange(-r, r, 0.6), np.arange(0.3, h + r, 0.6))
        gx, gy = gx.ravel(), gy.ravel()
        inside = (gy <= h) | (gx ** 2 + (gy - h) ** 2 <= r * r)
        self.fill = _Fill(np.stack([gx[inside], gy[inside], np.zeros(inside.sum())], axis=1) + self.c)

    def sample(self, t):
        g = _ss(self.t0, self.t0 + 0.8, t)
        return dict(pos=self.frame, size=0.25 + 0.5 * self.sd ** 4, color=self.col, alpha=0.9 * g,
                    kind="spark", twinkle=0.7, emit=2.0)


class _Fill:
    def __init__(self, pos):
        self.pos = pos

    def sample(self, t):
        return dict(pos=self.pos, size=0.9, color=lin("#ffffff"), alpha=1.0, kind="soft")


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
    """Silver rain round the two in the night world, life size; in the breath it stops in the air, and on the
    biggest hit every drop turns to a warm light and rises (into the blossom world, where it fades)."""
    wants_camera = True

    def __init__(self, origin, n=12000):
        rng = np.random.default_rng(44)
        self.s = rng.random((n, 4))
        self.o = _A(origin, float)

    def sample(self, t, cam=None):
        if t < X5 - 0.05 or t > 47.0:
            return []
        s = self.s
        tau = _rain_tau(t)
        hh = 14.0
        x = -14.0 + 28.0 * s[:, 0]
        z = -24.0 + 36.0 * s[:, 1]
        y = hh - np.mod(s[:, 2] * hh + 9.0 * tau, hh)
        pos = np.stack([x, y, z], axis=1) + self.o
        near = 1.0
        if cam is not None:
            d = np.linalg.norm(pos - np.asarray(cam.pos, np.float64)[None, :], axis=1)
            near = np.clip((d - 1.2) / 2.0, 0.0, 1.0)
        if t < X6:
            ln = 0.32 * min(1.0, max(0.0, (BREATH + 1.2 - t) / 1.0)) + 0.03
            pos2 = pos + np.array([0.0, ln, 0.0])
            g = _ss(X5 - 0.05, X5 + 0.5, t)
            return dict(pos=pos, pos2=pos2, size=0.006, color=lin("#d6dcff"), alpha=0.45 * near * g, kind="line")
        g = 1.0 - _ss(45.0, 47.0, t)
        flash = 1.0 + 2.0 * np.exp(-(t - X6) / 0.35)
        col = lin("#ffd9a0") * (1 - s[:, 3:4]) + lin("#ffb4c8") * s[:, 3:4]
        return dict(pos=pos, size=0.03 + 0.03 * s[:, 3], color=col, alpha=0.85 * g * near, emit=flash,
                    kind="spark", twinkle=0.6)


class Blossom:
    """Blossom drifting toward the camera in the blossom world, life size (painted in its true colours); the
    same petals as light only inside the windows of the rain world."""

    def __init__(self, origin, paint=True, n=1400):
        rng = np.random.default_rng(71)
        self.s = rng.random((n, 6))
        self.o, self.paint = _A(origin, float), paint

    def sample(self, t):
        s = self.s
        d = t - X6
        x = -9.0 + 18.0 * s[:, 0] + 0.5 * np.sin(1.3 * d + 6.28 * s[:, 3])
        y = 0.2 + 6.0 * s[:, 1] + 0.3 * np.sin(0.9 * d + 6.28 * s[:, 4])
        z = -16.0 + np.mod(22.0 * s[:, 2] + 1.6 * d, 22.0)
        pos = np.stack([x, y, z], axis=1) + self.o
        rot = np.stack([6.28 * s[:, 3] + d * (0.6 + s[:, 4]), 6.28 * s[:, 5] + d * (1.5 + s[:, 0])], axis=1)
        if not self.paint:
            return dict(pos=pos, size=0.06 + 0.03 * s[:, 4], color=lin("#ffd0dc"), alpha=0.8, kind="petal", rot=rot)
        col = np.where(s[:, 5:6] < 0.55, show("#f0566a"), show("#ffc2cf"))
        g = 1.0 - _ss(49.5, 51.0, t)
        return dict(pos=pos, size=0.045 + 0.03 * s[:, 4], color=col, alpha=0.95 * g, kind="petal", rot=rot,
                    paint=1.0, paint_light=0.3)


# ------------------------------------------------------------------------------------------------ people
def _style(name, color, color2, bright=1.0):
    """The looks of each style of person (refs and refs2): window (filled with the next world, a rim of
    light), sparks (a profile outlined in sparks, filled with the next world), plexus, glitter."""
    if name == "window":
        return [dict(name="window", bright=1.3 * bright, size=1.4, color=color, color2=color2),
                dict(name="rim", bright=0.6 * bright, color=color2, color2=color)]
    if name == "sparks":
        return [dict(name="window", bright=0.7 * bright, size=1.2, color=color, color2=color2),
                dict(name="rim", bright=1.5 * bright, power=4.0, color=color2, color2=color)]
    if name == "plexus":
        return [dict(name="plexus", bright=1.2 * bright, color=color, color2=color2),
                dict(name="rim", bright=0.4 * bright, color=color2, color2=color)]
    return [dict(name="glitter", bright=bright, color=color, color2=color2)]


def _place(at, origin):
    o = _A(origin, float)
    if callable(at):
        return (lambda f: lambda t: tuple(_A(f(t), float) + o))(at)
    if isinstance(at, list):
        return [(k[0], tuple(_A(_xyz(k[1]), float) + o)) for k in at]
    return tuple(_A(_xyz(at), float) + o)


def _xyz(p):
    return (p[0], 0.0, p[1]) if len(p) == 2 else tuple(p)


def _add(scene, name, body, t0, t1, window=False, edge=0.55, grow=None, rise=0.6, tint=(1.0, 1.0, 1.0),
         inside=False, dim=None):
    """Adds a body, gated to [t0, t1): as a window onto the next world (its mask follows the gate), or as
    light only. inside=True: it lives inside the windows (seen only through them)."""
    gate = _Gate(body, t0, t1, rise=rise, dim=(0.45 if t1 < 60.0 else 0.0) if dim is None else dim)
    ps = PW.KeepClear(_Lit(gate), WORDS, floor=0.0)
    if window:
        mk = dict(sky="world", look=window_look, edge=edge, strength=gate.gain, tint=tint)
        if grow is not None:
            mk["grow"] = grow
        scene.add(name, ps, mask=body.mask(**mk))
    elif inside:
        scene.add(name, ps, window=True, reflect=False)
    else:
        scene.add(name, ps)
    return body


def _person(shape, at, origin, style="window", color="#ffe0b0", color2="#ffffff", bright=1.0, scale=1.0,
            shed=None, **kw):
    from p3d.body import Body
    fx = list(kw.pop("effects", []))
    if shed is not None:
        fx.append(dict(kind="shed", t=shed, n=4000, speed=0.25, rise=0.1, where="back"))
    return Body(shape, at=_place(at, origin), scale=scale, look=_style(style, color, color2, bright), effects=fx,
                color=color, color2=color2, **kw)


def _hands_help(meet, lift, t_clasp, approach=3.2, colors=("#ffcf8a", "#8fd0ff"), points=60000):
    """Two hands of light: a gold hand reaching up from below and a blue hand reaching down from above; they
    clasp at t_clasp and the upper one lifts the lower (helping someone up, told by the hands alone). The
    two hands as Bodies (part arm), placed by their fingertips (engine/p3d/body.py, hand=)."""
    from p3d.body import Body
    meet = _A(meet, float)
    out = []
    t0 = t_clasp - approach
    for j, (shape, side, col, aim, palm, poses) in enumerate((
            ("woman", "L", colors[0], _A([0.42, 0.91, 0.0]), (0.0, 0.0, 1.0), [(0.0, "offer"), (t_clasp, "hold")]),
            ("man", "R", colors[1], _A([-0.42, -0.91, 0.0]), (0.0, 0.0, -1.0), [(0.0, "open"), (t_clasp, "hold")]))):
        aim = aim / np.linalg.norm(aim)

        def at(t, aim=aim, j=j):
            u = _ss(t0, t_clasp, t)
            gap = 0.30 * (1.0 - u)
            drift = _A([0.006 * np.sin(2.1 * t + j), 0.008 * np.sin(1.7 * t + 2 * j), 0.0]) * (1.0 - u)
            return meet - aim * gap + drift + _A([0.0, lift(t), 0.0])

        fx = [dict(kind="shed", n=4000, life=2.2, where=[1], dir=tuple(-aim), speed=0.35, rise=0.03, turb=0.2,
                   spread=0.05)]
        out.append(Body(shape, part="arm." + side, look="glitter", color=col, points=points, effects=fx,
                        seed=40.0 + j, hand=dict(side=side, at=at, aim=tuple(aim), palm=palm, pose=poses,
                                                 anchor="fingertips")))
    return out


def _embrace_pair(origin, t_rise, t_hold, look_a, look_b, scale=1.0):
    """Two people kneel face to face (life size); at t_rise both get up; at t_hold they step in and hold each
    other. The woman (b) is bowed and comes apart into flakes until the breath, then her flakes fly home."""
    from p3d.body import Body
    from track import Track
    refs = {}
    o = _A(origin, float)
    d0, d1 = 0.50, 0.19                  # half the distance between them: kneeling, and holding
    step = lambda sgn: [(0.0, (o[0] + sgn * d0, o[1], o[2])), (t_hold - 0.55, (o[0] + sgn * d0, o[1], o[2])),
                        (t_hold + 0.2, (o[0] + sgn * d1, o[1], o[2]))]
    ka = dict(shape="man", at=step(-1.0), facing=90.0, garment="coat",
              motion=[(-1e9, "kneel", dict(dur=0.01, hands="free")), (t_rise, "rise", dict(dur=1.1, blend=0.1)),
                      (t_hold - 0.55, "shuffle"), (t_hold + 0.3, "stand")],
              gesture=[(33.5, t_rise + 0.2, "bow", dict(amount=22.0)), (33.8, t_rise, "cup", dict(height=-0.25)),
                       (t_hold - 0.2, 61.0, "embrace", dict(to=lambda tt: refs["b"].where(tt, "blade.R", raw=True),
                                                            to2=lambda tt: refs["b"].where(tt, "blade.L", raw=True),
                                                            head="L", ease=1.0))],
              look=look_a, seed=61.0)
    kb = dict(shape="woman", at=step(1.0), facing=270.0, garment="dress",
              motion=[(-1e9, "kneel", dict(dur=0.01, hands="lap")), (t_rise + 0.15, "rise", dict(dur=1.1, blend=0.1)),
                      (t_hold - 0.55, "shuffle"), (t_hold + 0.3, "stand")],
              gesture=[(33.4, t_rise + 0.3, "bow", dict(amount=34.0)),
                       (t_hold - 0.2, 61.0, "embrace", dict(to=lambda tt: refs["a"].where(tt, "blade.R", raw=True),
                                                            to2=lambda tt: refs["a"].where(tt, "blade.L", raw=True),
                                                            head="L", ease=1.0))],
              effects=[dict(kind="dissolve", amount=Track([(0.0, 0.0), (33.8, 0.0), (35.8, 0.32), (37.3, 0.32),
                                                           (38.5, 0.0), (61.0, 0.0)]), reach=2.5)],
              look=look_b, seed=62.0)
    refs["a"] = Body(color="#cfd6ff", color2="#ffffff", **ka)
    refs["b"] = Body(color="#e8dcff", color2="#ffffff", **kb)
    return refs["a"], refs["b"]


def _setup(scene):
    from p3d import pairs

    # 1 GREETING: the giant profile, a window onto the sunrise; inside her, far off, a greeting
    _add(scene, "s1_profile", _person("woman", tuple(BUST_AT), O1, scale=100.0, part="bust", facing=90.0,
                                      garment="dress", points=90000, detail=dict(head=3), color="#ffd9a0",
                                      color2="#fff4e6", bright=0.45,
                                      gesture=[(2.6, 30.0, "look_up", dict(amount=10.0))], seed=11.0),
         -1.0, X1, window=True, edge=0.7, grow=0.35, rise=0.0)
    gs, ga = GREET_SCALE, GREET_AT
    refs = {}
    man = _person("man", (ga[0], ga[2]), (0.0, 0.0, 0.0), style="glitter", color="#fff0d0", color2="#ffffff",
                  bright=1.6, scale=gs, garment="coat", facing=[(0.0, 90.0), (4.2, 90.0), (5.1, -90.0)],
                  motion=[(-1e9, "stand"), (4.1, "shuffle"), (5.2, "stand")],
                  gesture=[(4.9, 30.0, "wave", dict(side="R"))], seed=12.0)
    refs["m"] = man
    woman = _person("woman", (ga[0] - 0.62 * gs, ga[2] - 0.05 * gs), (0.0, 0.0, 0.0), style="glitter",
                    color="#ffe0c0", color2="#ffffff", bright=1.6, scale=gs, garment="dress", facing=90.0,
                    gesture=[(3.4, 5.0, "hand_on_shoulder",
                              dict(side="R", to=lambda tt: refs["m"].where(tt, "shoulder.R", raw=True)))],
                    seed=13.0)
    _add(scene, "s1_greet_man", man, -1.0, X1, inside=True, rise=0.0, dim=0.0)
    _add(scene, "s1_greet_woman", woman, -1.0, X1, inside=True, rise=0.0, dim=0.0)

    # 2 CONCESSION: a door of light onto the sea; he steps back and opens his palm toward it, she goes first
    door = Door(O2 + DOOR["c"], DOOR["w"], DOOR["h"], t0=X1)
    scene.add("s2_door", _Gate(door, X1, X2, rise=0.0, fall=0.0))
    from p3d import Mask
    scene.add("s2_door_open", _Gate(door.fill, X1, X2, rise=0.0, fall=0.0), reflect=False,
              mask=Mask("sky", sky="world", look=window_look, edge=0.4, grow=0.6,
                        strength=lambda t: _ss(X1, X1 + 0.8, t) * (1.0 if t < X2 else 0.0)))
    _add(scene, "s2_host", _person("man", (-14.0, -78.0), O2,
                                   style="plexus", color="#ffd9a0", color2="#fff4e0", scale=12.0, garment="coat",
                                   facing=100.0,
                                   gesture=[(8.1, 30.0, "offer", dict(side="L"))], seed=21.0), X1, X2)
    _add(scene, "s2_guest", _person("woman", (8.0, -24.0), O2, style="plexus", color="#ffe6c0", color2="#ffffff",
                                    scale=12.0, garment="dress", facing=180.0,
                                    motion=[(-1e9, "stand"), (8.6, "walk", dict(speed=1.6))], seed=22.0), X1, X2)

    # 3 RESPECT: he speaks with an open hand raised, light flowing from it; she leans in and listens
    speaker = _person("man", (13.0, -70.0), O3, style="sparks", color="#bfe0ff", color2="#ffffff", scale=26.0,
                      garment="tunic", facing=270.0, seed=31.0,
                      gesture=[(13.9, 30.0, "reach", dict(side="L", palm="up", height=0.12, far=0.7))])
    listener = _person("woman", (-13.0, -70.0), O3, style="sparks", color="#bfe0ff", color2="#ffffff",
                       scale=26.0, garment="dress", facing=90.0, seed=32.0,
                       gesture=[(14.0, 30.0, "listen", dict(side="R", amount=1.0)),
                                (15.8, 16.6, "bow", dict(amount=9.0, ease=0.4)),
                                (16.9, 17.7, "bow", dict(amount=7.0, ease=0.4))])
    tint3 = (1.7, 1.6, 1.9)
    _add(scene, "s3_speaker", speaker, X2, X3, window=True, edge=0.8, tint=tint3)
    _add(scene, "s3_listener", listener, X2, X3, window=True, edge=0.8, tint=tint3)
    scene.add("s3_thought", PW.KeepClear(Stream(lambda t: speaker.where(t, "palm.L"),
                                                lambda t: listener.where(t, "head"), 14.6, X3 - 0.3, size=0.30),
                                         WORDS, floor=0.0))

    # 4 GRATITUDE: the people round him bow to him, one after another; he bows back
    _add(scene, "s4_worker", _person("man", (WORKER_AT[0], WORKER_AT[2]), O4, style="window", color="#ffd27a",
                                     color2="#fff4d0", scale=16.0, garment="coat", facing=0.0,
                                     gesture=[(22.6, 30.0, "bow", dict(amount=20.0))], seed=41.0),
         X3, X4, window=True, edge=0.7)
    from p3d.crowd import Crowd
    wc = O4 + WORKER_AT
    crowd = Crowd(n=150, area=dict(center=(wc[0], wc[2]), radius=(16.0, 75.0), arc=(-125.0, 125.0)),
                  facing="center", kinds=(("bow", 3.0), ("pray", 1.0)), shapes=("woman", "man", "child"),
                  start=dict(t=X3 + 0.5, center=(wc[0], wc[2]), speed=34.0), scale=(5.5, 7.5), points=2600,
                  color="#ffd27a", color2="#fff0c0", bright=1.1, seed=4.0)
    scene.add("s4_crowd", PW.KeepClear(_Gate(crowd, X3, X4, rise=0.0, fall=0.0), WORDS, floor=0.0))

    # 5 CONSIDERATION: the helping hands
    for k, v in enumerate(_hands_help(MEET, _lift, CLASP)):
        scene.add("s5_hand%d" % k, _Gate(v, X4, X5, rise=0.5))
    from p3d.effects import Flare
    scene.add("s5_flare", _Gate(Flare(lambda t: MEET + _A([0.0, _lift(t), 0.0]), CLASP, color="#ffd9a0",
                                      color2="#bfe4ff"), X4, X5, rise=0.0))

    # 6 APOLOGY and INCLUSIVENESS: they kneel face to face in the rain; they rise and hold each other
    a6, b6 = _embrace_pair(O6 + PAIR6, 37.6, 39.0, _style("window", "#cfd6ff", "#ffffff"),
                           _style("window", "#e8dcff", "#ffffff"))
    _add(scene, "s6_him", a6, X5, X6, window=True, edge=0.7)
    _add(scene, "s6_her", b6, X5, X6, window=True, edge=0.7)

    # 7 ENCOURAGEMENT: she kneels in prayer; COMPLIMENT: a father lifts his daughter into his arms
    _add(scene, "s7_prayer", _person("woman", (PRAYER_AT[0], PRAYER_AT[2]), O7, style="glitter", color="#fff0e8",
                                     color2="#ffffff", bright=1.4, garment="dress",
                                     facing=90.0, motion=[(-1e9, "kneel", dict(dur=0.01, hands="pray"))],
                                     gesture=[(X6, 61.0, "bow", dict(amount=14.0))], seed=71.0), X6, REVEAL + 1.0)
    fa, ch = pairs.child_into_arms(47.6, at=(O7[0] + FATHER_AT[0], O7[2] + FATHER_AT[2]), facing=270.0, lift=1.0,
                                   adult=dict(shape="man", garment="coat", look=_style("glitter", "#ffd9a0", "#fff4e0", 1.2),
                                              color="#ffd9a0", seed=72.0),
                                   child=dict(look=_style("glitter", "#ffc0a0", "#fff0e0", 1.4), color="#ffc0a0",
                                              garment="dress", seed=73.0,
                                              effects=[dict(kind="shed", t=48.3, n=6000, speed=0.6, rise=0.5,
                                                            color="#ffb070", where="top")]))
    _add(scene, "s7_father", fa, X6, REVEAL + 1.5)
    _add(scene, "s7_child", ch, X6, REVEAL + 1.5)

    # 8 HEAVENLY MOTHER, only from behind, veiled: a silhouette full of stars, a rim of light
    _add(scene, "s8_mother", _person("woman", tuple(MOTHER_AT), O7, style="window", color="#fff0d8",
                                     color2="#ffffff", bright=1.2, scale=45.0, garment="robe",
                                     veil=dict(length=1.5), points=110000, facing=180.0,
                                     gesture=[(50.2, 61.0, "open_arms", dict(lift=0.25))], seed=81.0),
         REVEAL, 61.0, window=True, edge=0.9, grow=2.2, rise=1.2, tint=(1.7, 1.6, 2.0))

    # the depth inside each window, then the air of that world once we are in it
    ember2 = Motes(O2 + _A([0.0, 40.0, -40.0]), (140.0, 40.0, 160.0), 1400, ("#ffc890", "#ff9e6e", "#fff0d0"),
                   size=(0.4, 1.6), seed=2)
    sea3 = Motes(O3 + _A([0.0, 1.0, -60.0]), (160.0, 0.9, 170.0), 2400, ("#ffffff", "#d8fff4"),
                 size=(0.15, 0.45), kind="spark", alpha=0.9, drift=(0.0, 0.0, 0.0), twinkle=1.0, emit=2.0, seed=3)
    stars4 = Motes(O4 + _A([0.0, 110.0, -320.0]), (420.0, 110.0, 120.0), 1800, ("#ffffff", "#cfd8ff", "#ffe2a8"),
                   size=(0.8, 2.2), kind="spark", alpha=0.9, drift=(0.0, 0.0, 0.0), twinkle=1.0, emit=2.5, seed=4)
    gold5 = Motes(MEET + _A([0.0, 0.0, -2.0]), (4.0, 2.0, 5.0), 900, ("#ffd27a", "#ffb060", "#fff0c0"),
                  size=(0.01, 0.05), alpha=0.8, drift=(0.05, 0.03, 0.0), seed=5)
    gold5w = Motes(O5 + _A([0.0, 6.0, -40.0]), (60.0, 12.0, 50.0), 1400, ("#ffd27a", "#ffb060"), size=(0.2, 0.7),
                   seed=6)
    stars8 = Motes(O7 + _A([0.0, 60.0, -420.0]), (90.0, 60.0, 30.0), 1200, ("#ffffff", "#cfd8ff", "#ffe2a8"),
                   size=(0.3, 0.9), kind="spark", alpha=0.9, drift=(0.0, 0.0, 0.0), twinkle=1.0, emit=2.5, seed=8)
    for name, ps, a, b, win in (
            ("in_s1", ember2, -1.0, X1, True), ("air_s2", ember2, X1, X2, False),
            ("in_s2", sea3, X1, X2, True), ("air_s3", sea3, X2, X3, False),
            ("in_s3", stars4, X2, X3, True), ("air_s4", stars4, X3, X4, False),
            ("in_s4", gold5w, X3, X4, True), ("air_s5", gold5, X4, X5, False),
            ("in_s8", stars8, REVEAL, 61.0, True)):
        scene.add(name, PW.KeepClear(_Gate(ps, a, b, rise=0.0, fall=0.0), WORDS, floor=0.0), window=win,
                  reflect=not win)
    scene.add("in_s6", _Gate(Blossom(O7, paint=False), X5, X6, rise=0.0, fall=0.0), window=True, reflect=False)
    scene.add("rain", PW.KeepClear(Rain(O6 + PAIR6), WORDS, floor=0.0), reflect=False)
    scene.add("blossom", PW.KeepClear(_Gate(Blossom(O7), X6 - 0.02, 51.0, rise=0.3, fall=0.0), WORDS, floor=0.0))
    # birds: into the first profile from frame 0, and every bird of the film into Heavenly Mother at the end
    scene.add("birds_s1", PW.KeepClear(Flock(O1 + BUST_HEAD, O1 + _A([-10.0, 60.0, -80.0]), (60.0, 26.0, 40.0),
                                             260, -3.0, X1 - 0.3, dur=(2.4, 3.8), size=(1.4, 2.6), seed=8),
                                       WORDS, floor=0.0))
    scene.add("birds_s8", PW.KeepClear(Flock(O7 + MOTHER_HEART, O7 + _A([0.0, 40.0, -150.0]), (160.0, 40.0, 120.0),
                                             1600, REVEAL + 0.4, FLOOD + 1.8, dur=(1.8, 3.2), size=(1.4, 2.8),
                                             seed=9), WORDS, floor=0.0))
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


# ------------------------------------------------------------------------------------------------ the 3D layer
# Nothing drawn by the 3D layer falls on the titles (screen fractions, y up): the opening title, each
# signature's corner while it shows, the date in the breath, then the end card.
_SIG_BOX = dict(br=(0.62, 0.03, 0.98, 0.24), bl=(0.02, 0.03, 0.38, 0.24), tr=(0.62, 0.76, 0.98, 0.97),
                tl=(0.02, 0.76, 0.38, 0.97))


def _clear_boxes(t):
    out = []
    oy = 1.0 - TITLES["opening"]["y"]
    if t < TITLES["opening"]["t_end"] + 0.5:
        a = 1.0 - _ss(TITLES["opening"]["t_end"], TITLES["opening"]["t_end"] + 0.5, t)
        out.append(dict(box=(0.12, oy - 0.15, 0.88, oy + 0.15), t0=-2.0, t1=61.0, soft=0.03, amount=a))
    for a0, a1, corner, _pal in TITLES["signature"]["windows"]:
        if a0 - 0.4 <= t <= a1 + 0.4:
            out.append(dict(box=_SIG_BOX[corner], t0=a0 - 0.4, t1=a1 + 0.4, soft=0.03, amount=1.0))
    dl = TITLES["date_light"]
    if dl["t_form"] - 0.3 <= t <= dl["t_burst"]:
        dy = 1.0 - dl["y"]
        out.append(dict(box=(0.12, dy - 0.15, 0.88, dy + 0.13), t0=dl["t_form"] - 0.3, t1=dl["t_burst"], soft=0.04,
                        amount=0.9))
    if t >= T_FORM - 0.3:
        out.append(dict(box=(0.10, 0.36, 0.90, 0.88), t0=T_FORM - 0.3, t1=61.0, soft=0.05, amount=0.85))
    return out[:2]


NINE = [e["color"] for e in PW.EXPRESSIONS]
_HEAD_LIGHT = tuple(O7 + MOTHER_HEAD + _A([0.0, 3.0, -14.0]))     # behind her head: rays fan from it (ref 10)

P3D = dict(
    camera=CAMERA,
    world=dict(
        looks=LOOKS,
        look=MAIN_LOOK,
        light=dict(pos=_HEAD_LIGHT, color="#fff0d0", size=10.0, rays=1.0,
                   strength=lambda t: 1.4 * _ss(REVEAL + 0.4, REVEAL + 2.0, t)),
        # the arch of nine lights: a low arc behind Heavenly Mother, under the end card
        arch=dict(lit=[FLOOD + 0.4 + 0.22 * k for k in range(9)], span=210.0, height=72.0,
                  z=float(O7[2] + MOTHER_AT[2] - 50.0), colors=NINE, bright=1.6),
        react=dict(beat=0.35, level=0.2),
    ),
    bursts=[dict(t=X5, at=tuple(MEET + _A([0.0, LIFT, 0.0])), strength=0.9, rise=0.15, fall=0.45, color="#ffe6b8",
                 radius=0.35),
            dict(t=X6, strength=0.45, rise=0.15, fall=0.6, color="#ffe8d0", radius=0.35),
            dict(t=FLOOD, at=tuple(O7 + MOTHER_HEART), strength=0.8, rise=0.35, fall=0.9, color="#fff0d8",
                 radius=0.3)],
    clear=lambda t: _clear_boxes(t),
    setup=_setup,
)


if __name__ == "__main__":
    src = open(__file__, encoding="utf-8").read()
    assert chr(0x2013) not in src and chr(0x2014) not in src, "no en dash or em dash"
    print("ok")
