"""Song 05 "God Bless You!": the full-length concert backdrop, version 2 (song module for the pinned Film 10 engine).

Loaded by tools/s05_full2/render05.py as the engine song "s05_full". Every time in this file is REFERENCE time
(the organisers' recording, 153.152 s); the stage video shows reference time r at stage time timing.K * r
(timing.py). The 2D layer (opening card, signature, the navy words, the calm bottom third) is overlay05.py.
Version 2 changes: a bright spring afternoon (DESIGN-SYSTEM 6), a closer calm camera so the people read from the
back of the hall, the arch high across the top of the sky, Respect (star 6) at "In her tender voice", the
expression symbols in the world and hearts drifting off each expression, 60 fps.

Built on the 3D layer of the pinned engine
(commit d928ff9) in the approved Revision 3 look: Claude Final v1 words and bodies (commit f43f451).

The picture (design: project-docs/designs/05 God Bless You!.md, adapted; times: TIMELINE.md):
  a golden spring afternoon over a mirror lake, the arch of nine lights high behind; a seed of hope drifts to
  the shore and grows, with every practised word, into the tree of blessing. Verse 1: a brother bowed and alone
  is prayed for (Encouragement) and helped (Consideration). Verse 2: he joins in praying for his sister, and a
  young woman crosses to help her. The climax: the sun breaks through the haze, the nine fruits shine in the
  nine colours, the far shores fill with people of light, a road of light rises toward the arch. The hold:
  both words return, calm, for the audience to carry home.

No em dash or en dash anywhere in this file.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import songs.s03_original as _base  # noqa: E402

import timing  # noqa: E402

MUSIC_END = timing.REF_LENGTH
HOLD = timing.HOLD / timing.K
FPS = timing.FPS
TOTAL = timing.TOTAL_REF             # 167.6 s of reference time = 174.0 s on stage
NFRAMES = int(round(TOTAL * FPS))
_base.TOTAL = TOTAL
_base.NFRAMES = NFRAMES
_base.MUSIC_END = MUSIC_END
_base.SONG_END = MUSIC_END
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d.camera import Rig, fly  # noqa: E402

import cast05  # noqa: E402
import effects05 as FX  # noqa: E402
import words2d  # noqa: E402
from p3d import world as _W  # noqa: E402

AUDIO_FILE = os.environ.get("AUDIO", "")
SONG_END = MUSIC_END
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE
WAVES = []
FRAGMENTS = []
T = cast05.T


def _ss(a, b, x):
    return float(FX._ss(a, b, x))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


# ---------------------------------------------------------------------------------------------- geography
TREE_AT = _v(cast05.TREE[0], 0.0, cast05.TREE[1])
# the arch of nine lights across the top of the sky. Like the sky itself it keeps its place in the picture while
# the camera drifts (its centre follows the camera's view), so its lights never cross the signature or a word:
# ends about (354, 369) and (1579, 363), top about (960, 206) in a 1080p frame (searched, see TIMELINE.md)
ARCH_Z = -46.0


def _arch_center(t):
    cam = LAYOUT.state(t)
    p, q = np.asarray(cam.pos, np.float64), np.asarray(cam.target, np.float64)
    return (float(p[0] + (q[0] - p[0]) / (p[2] - q[2]) * (p[2] - ARCH_Z)), 12.0, 0.0)


ARCH05 = dict(span=52.0, height=8.0, z=ARCH_Z, center=_arch_center)


def arch_point(k, t=0.0):
    return np.asarray(_ARCH.homes(t)[k], np.float64)


# ---------------------------------------------------------------------------------------------- the camera
# (time, position, target): calm, slow, level; performers stand in front, so the bottom third stays quiet
KEYS = [                                   # low over the water: people stand between the words and the calm
    (0.0, _v(0.4, 0.66, 14.6), _v(0.0, 1.95, 0.0)),            # bottom third, the horizon about 0.62 down
    (13.5, _v(-0.6, 0.63, 13.7), _v(-0.9, 1.86, 0.0)),
    (24.0, _v(-1.6, 0.62, 13.2), _v(-2.3, 1.84, 0.0)),
    (37.0, _v(-2.2, 0.62, 13.1), _v(-3.0, 1.84, 0.0)),
    (55.0, _v(-2.4, 0.62, 13.1), _v(-3.2, 1.84, 0.0)),
    (66.0, _v(-3.0, 0.62, 13.1), _v(-3.8, 1.84, 0.0)),
    (78.0, _v(-1.4, 0.62, 13.2), _v(-2.0, 1.84, 0.0)),
    (90.0, _v(1.2, 0.62, 13.3), _v(1.6, 1.84, 0.0)),
    (106.0, _v(2.4, 0.62, 13.2), _v(3.0, 1.84, 0.0)),
    (122.0, _v(3.0, 0.62, 13.1), _v(3.7, 1.84, 0.0)),
    (137.5, _v(3.2, 0.62, 13.1), _v(3.8, 1.84, 0.0)),
    (146.0, _v(0.4, 0.64, 15.2), _v(-0.2, 1.90, 0.0)),
    (152.5, _v(-0.2, 0.68, 15.8), _v(-0.6, 2.02, 0.0)),
    (158.0, _v(-0.2, 0.70, 16.0), _v(-0.6, 2.05, 0.0)),
    (TOTAL + 1.0, _v(-0.2, 0.70, 16.2), _v(-0.6, 2.05, 0.0)),
]
FOV = 40.0


def _rig(focus=None):
    return Rig([fly(KEYS, fov=FOV, aperture=0.012, focus=focus if focus is not None else "target")],
               blend=1.0, fov=FOV, aperture=0.012, handheld=0.04, min_height=0.3)


LAYOUT = _rig()
_ARCH = _W.Arch(None, **ARCH05)

# ---------------------------------------------------------------------------------------------- people
CAST = cast05.Cast()
TREE_FX = FX.Tree(TREE_AT, height=2.7)
FRUITS = TREE_FX.fruit

# the arch's light colours: the website colours, the two dark ones (Respect, Compliment) by their lighter glow so
# they still read as light on a bright sky (engine/p3d/words.py GLOWS)
ARCH_COLORS = [words2d.expressions()[k].get("glow", words2d.expressions()[k]["color"])
               for k in ("Greeting", "Gratitude", "Apology", "Inclusiveness", "Concession", "Respect",
                         "Encouragement", "Consideration", "Compliment")]

# ---------------------------------------------------------------------------------------------- words
STAR_RESP, STAR_ENC, STAR_CONS = 5, 6, 7
WORDS = words2d.Words()
WORDS.check()
CAMERA = LAYOUT


# ---------------------------------------------------------------------------------------------- light of the story
def _hands(k):
    return lambda t: 0.5 * (CAST.where(k, t, "palm.R") + CAST.where(k, t, "palm.L"))


def _neck(k, up=0.0):
    return lambda t: CAST.where(k, t, "neck") + _v(0.0, up, 0.0)


def _mid(a, b, lift):
    return lambda t: 0.5 * (a(t) + b(t)) + _v(0.0, lift, 0.0)


def _star(k):
    return lambda t: arch_point(k, t)


def _trio_hands(t):
    return (_hands("A")(t) + _hands("B")(t) + _hands("C")(t)) / 3.0


PRAYER1 = FX.Stream(_hands("A"), _mid(_hands("A"), _neck("B"), 1.6), _neck("B", -0.12),
                    T["cloak"][0], T["cloak"][1], T["rise_B"] + 2.0, FX.VIOLET, seed=31)
ANSWER2 = FX.Stream(_star(STAR_ENC), lambda t: _trio_hands(t) + _v(0.0, 6.0, -2.0), _trio_hands,
                    96.6, 99.4, 99.8, FX.VIOLET, seed=33, around=0.5)
PRAYER2 = FX.Stream(_trio_hands, _mid(_trio_hands, _neck("D"), 1.4), _neck("D", -0.10),
                    99.6, 102.6, 109.0, FX.VIOLET, seed=35)


def _petal_amount(t):
    return (0.10 + 0.10 * _ss(76.0, 82.0, t) + 0.25 * _ss(83.0, 92.0, t) + 0.30 * _ss(112.0, 118.0, t)
            + 0.25 * _ss(146.0, 147.5, t) * (1.0 - _ss(150.0, 157.0, t)) - 0.15 * _ss(155.0, 160.0, t))


WAVES_FX = FX.Waves([(13.6, cast05.TREE), (37.6, cast05.HOME["B"]), (68.8, cast05.HOME["B"]),
                     (107.6, cast05.HOME["D"]), (139.2, cast05.HOME["D"])])


def _symbols():
    """The expression symbols in the world, subtly, in the expression's colour, around each moment (PHASEB
    UPDATE 9 point 4): each a different recipe, never inside a reading box (WORDS.clear), never an icon."""
    from p3d import brand  # noqa: F401  (brand first: it imports brand_symbols)
    from p3d import brand_symbols as BS
    paint = 0.65                                       # a bright day sky: the lines painted in their colour
    return [
        # Encouragement, verse 1: praying hands traced by violet fireflies above the brother
        BS.Traced("Encouragement", pos=(-6.2, 3.55, -1.4), size=1.1, t0=29.0, dur=2.0, hold=4.5, out=1.6,
                  intensity=0.45, paint=paint, camera=LAYOUT, seed=3),
        # Consideration, verse 1: two open hands holding a heart, in rose petals over the clasped hands
        BS.PetalShape("Consideration", pos=(-5.6, 3.7, -0.9), size=1.0, t0=63.2, dur=2.0, hold=3.0, out=1.8,
                      intensity=0.45, paint=paint, camera=LAYOUT, seed=5),
        # Encouragement, verse 2: one light draws the praying hands above the sister
        BS.LightTrail("Encouragement", pos=(7.3, 3.5, -1.2), size=1.0, t0=99.5, dur=2.2, hold=3.5, out=1.6,
                      intensity=0.45, paint=paint, camera=LAYOUT, seed=7),
        # Respect: a small flock of birds passes and makes the hand cupped at the ear
        BS.Flock("Respect", pos=(8.0, 4.0, -2.5), size=1.4, t0=112.5, dur=2.2, hold=2.4, out=2.0,
                 intensity=0.35, paint=paint, camera=LAYOUT, seed=9),
        # Consideration, verse 2: the two hands and the heart traced in rose sparks over the two women
        BS.Traced("Consideration", pos=(6.6, 3.6, -0.4), size=1.0, t0=134.4, dur=2.0, hold=2.6, out=1.6,
                  style="sparks", intensity=0.45, paint=paint, camera=LAYOUT, seed=11),
    ]


# Hearts in the expression colours drift off each expression (PHASEB UPDATE 9 point 5), from the hands that
# practise it: (expression, source on a person, t0, t1). Drawn by overlay05.py (the pinned engine has no heart
# sprite), at the projected place of the source.
HEARTS = [
    ("Encouragement", ("A", "palm.R"), 27.5, 35.0),
    ("Consideration", ("A", "palm.R"), 64.8, 68.0),
    ("Encouragement", ("B", "palm.R"), 97.0, 104.8),
    ("Respect", ("B", "chest"), 112.0, 119.4),
    ("Consideration", ("C", "palm.R"), 134.0, 138.4),
]


def _setup(scene):
    scene.add("s05 island", FX.Island(TREE_AT))
    scene.add("s05 tree", WORDS.clear(TREE_FX))
    scene.add("s05 seed", FX.Seed(_v(0.3, 0.12, 6.0), TREE_AT + _v(0.0, 0.10, 0.0)))
    w1, w2 = CAST.walk1, CAST.walk2
    scene.add("s05 stones", FX.Stones([(w1[0], w1[1], w1[2], w1[3], 5.0), (w2[0], w2[1], w2[2], w2[3], 5.0)]),
              reflect=True)
    scene.add("s05 waves", WAVES_FX, reflect=False)
    scene.add("s05 load", FX.Load(CAST, t_thin=(T["cloak"][0] + 2.0, T["rise_B"]), t_off=T["load_off"]))
    for name, s in (("prayer1", PRAYER1), ("answer2", ANSWER2), ("prayer2", PRAYER2)):
        scene.add("s05 " + name, WORDS.clear(s))
    # her tender voice: soft halos from the sister to her brother, who listens (Respect)
    scene.add("s05 halos", WORDS.clear(FX.Halos(lambda t: CAST.where("D", t, "head"), _neck("B", 0.1),
                                                108.4, 122.0)), reflect=False)
    scene.add("s05 petals", WORDS.clear(FX.Petals(_petal_amount)))
    scene.add("s05 shores", FX.Shores())
    scene.add("s05 road", WORDS.clear(FX.Road(TREE_FX.tip_top(), arch_point(4, 150.0) + _v(0, -2.0, 0))), reflect=False)
    scene.add("s05 drift", FX.Drift(FRUITS))
    for i, fx in enumerate(_symbols()):
        scene.add(f"s05 symbol {i}", WORDS.clear(fx), reflect=False)
    CAST.add(scene)


# ---------------------------------------------------------------------------------------------- the world
def _arch_lit(t):
    """Nine (brightness, age). Lit from the start: 3 Apology, 4 Inclusiveness, 7 Encouragement, 9 Compliment
    (song 04's end). 7 relights after each Encouragement (a brief flare and one new ring), 8 Consideration is lit
    for the first time by the first Consideration and relights after the second, 6 Respect is lit for the first
    time at "In her tender voice". Lit at the end: 3, 4, 6, 7, 8, 9 (song 06's start)."""
    out = []
    times = {STAR_ENC: [-30.0] + [WORDS[n].t_out for n in ("Encouragement", "Encouragement2")],
             STAR_CONS: [WORDS[n].t_out for n in ("Consideration", "Consideration2")],
             STAR_RESP: [WORDS["Respect"].t_out]}
    for k in range(9):
        if k in (2, 3, 8):
            out.append((1.0, t + 30.0))
        elif k in times:
            past = [x for x in times[k] if x <= t]
            out.append((1.0, t - past[-1]) if past else (0.0, 0.0))
        else:
            out.append((0.0, 0.0))
    return out


def _day(h, k):
    return _W._day(h, k)


_SPRING = dict(base="day", sky_top=_day("#5aa0e0", 0.86), sky_mid=_day("#a8d0ee", 0.78),
               sky_hor=_day("#f4e6c4", 0.56), sun_color=_day("#fff0cc", 0.26), sun_int=0.85, sun_el=20.0,
               sun_az=156.0, sun_disc=2.0, sun_glow=0.55, clouds=0.45, haze=0.26, haze_color=_day("#d8e6ee", 0.44),
               mist=0.0, mist_color=_day("#f4ecd8", 0.50), hills=1.0, hill_height=0.75,
               hill_color=_day("#2f9a52", 0.32), water=_day("#5590c4", 0.40), mirror_min=0.45, rays=0.38,
               dust=0.45, dust_color="#fff6e0", dust_color2="#ffd2de", ripple=0.30, stars=0.0, milky=0.0)


def _spring(**kw):
    d = dict(_SPRING)
    d.update(kw)
    return d


LOOKS = dict(
    # song 04's thawed apricot late morning, the hand-off frame
    morning=_spring(sky_top=_day("#78b4e6", 0.84), sky_mid=_day("#c6dcee", 0.80), sky_hor=_day("#f8d8b6", 0.62),
                    sun_el=18.0, haze_color=_day("#f0dcc6", 0.46), hill_color=_day("#5a9468", 0.34), rays=0.25),
    # the fresh spring afternoon of verse 1, a soft warm haze
    haze=_spring(clouds=0.45, haze=0.62),
    # the clear bright afternoon of verse 2, blossom in the air
    bright=_spring(sky_top=_day("#5aa4e4", 0.88), sky_hor=_day("#faeed4", 0.64), clouds=0.28, rays=0.28,
                   dust_color2="#ffc8d8"),
    # the climax: the sun breaks through the haze, a warm gold bloom on a visible scene (never a white-out)
    glory=_spring(sky_top=_day("#5c9ede", 0.88), sky_mid=_day("#c4dcee", 0.82), sky_hor=_day("#fbe2b0", 0.66),
                  sun_color=_day("#ffe6b0", 0.30), sun_int=1.15, sun_el=20.0, sun_glow=0.9, rays=0.55,
                  haze_color=_day("#f6e2be", 0.50)),
    # the hold: warm late afternoon, the hand-off to song 06 (the design's #2b5a98, #8fa8c8, #efd3a0)
    late=_spring(sky_top=_day("#3a6cb0", 0.92), sky_mid=_day("#9ab4d4", 0.86), sky_hor=_day("#efd3a0", 0.66),
                 sun_color=_day("#ffe4b0", 0.28), sun_el=12.0, sun_glow=0.8, rays=0.35, ripple=0.15,
                 haze_color=_day("#ecd8b4", 0.46), hill_color=_day("#4e8460", 0.34)),
)

# the lake: a perfect mirror during each prayer and each reading, gently alive otherwise
RIPPLE = Track([(0.0, 0.22), (24.0, 0.25), (26.0, 0.0), (36.4, 0.0), (39.0, 0.25), (56.0, 0.20), (58.0, 0.06),
                (66.5, 0.06), (69.0, 0.25), (94.0, 0.22), (96.0, 0.0), (106.4, 0.0), (109.0, 0.25),
                (126.0, 0.22), (128.0, 0.06), (137.0, 0.06), (140.0, 0.25), (153.0, 0.18), (156.0, 0.08),
                (TOTAL + 1.0, 0.08)])

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "morning"), (12.0, "haze", 10.0), (70.0, "haze"), (84.0, "bright", 12.0), (138.0, "bright"),
          (146.4, "glory", 2.4), (152.0, "glory"), (156.0, "late", 6.0)],
    ripple=RIPPLE,
    mirror=0.72,
    arch=dict(lit=_arch_lit, colors=ARCH_COLORS, bright=1.25, line=1.0, **ARCH05),
    lights=[dict(pos=lambda t: TREE_AT + _v(0.0, 1.8, 0.0), color="#ffd890",
                 strength=lambda t: 0.2 + 0.5 * _ss(52.0, 82.0, t) + 0.6 * _ss(146.0, 148.0, t), radius=4.0),
            dict(pos=lambda t: CAST.where("B", t, "chest"), color="#ffd27a",
                 strength=lambda t: 0.6 * _ss(37.5, 48.0, t) * (1.0 - _ss(68.0, 76.0, t)), radius=3.0)],
    react=dict(beat=0.10, level=0.25),
)

P3D = dict(
    camera=CAMERA,
    world=WORLD,
    setup=_setup,
    bursts=[],
    motion_blur=0.3,
)

# ---------------------------------------------------------------------------------------------- titles
TITLE = dict(label="Healing Concert", lines=["God Bless You"], size=120, y=0.27, label_size=40, form=1e9,
             hold=1e9, star=1e9, color="#ffffff", glow="#ffffff", anim="ribbon")     # never shown
TAGLINE = dict(text="God Bless You", sizes=(60, 60), t0=1e9, t1=1e9 + 1.0, color="#ffffff", glow="#ffffff",
               anim="rise")                                                         # never shown
TITLES = {}                         # the opening card and the signature are drawn by overlay05.py
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
