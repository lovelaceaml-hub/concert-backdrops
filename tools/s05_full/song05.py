"""Song 05 "God Bless You!": the full-length concert backdrop (song module for the pinned Film 10 engine).

Loaded by tools/s05_full/render05.py as the engine song "s05_full". Built on the 3D layer of the pinned engine
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

MUSIC_END = 153.15
HOLD = 15.0
FPS = 30
NFRAMES = int(round((MUSIC_END + HOLD) * FPS))          # 5045 frames
TOTAL = NFRAMES / FPS
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
import words05  # noqa: E402

AUDIO_FILE = os.environ.get("AUDIO", "")
TOTAL = NFRAMES / FPS
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
ARCH05 = dict(span=46.0, height=21.0, z=-42.0)
_arch_u = np.linspace(0.0, 1.0, 9)


def arch_point(k):
    th = np.radians(172.0 - 164.0 * _arch_u[k])
    return _v(0.5 * ARCH05["span"] * np.cos(th), ARCH05["height"] * np.sin(th), ARCH05["z"])


# ---------------------------------------------------------------------------------------------- the camera
# (time, position, target): calm, slow, level; performers stand in front, so the bottom third stays quiet
KEYS = [
    (0.0, _v(0.6, 1.10, 21.0), _v(0.2, 2.45, 0.0)),
    (13.5, _v(-0.6, 0.95, 16.0), _v(-0.9, 2.20, 0.0)),
    (24.0, _v(-1.4, 0.90, 15.2), _v(-2.2, 2.15, 0.0)),
    (37.0, _v(-2.0, 0.88, 14.8), _v(-2.9, 2.15, 0.0)),
    (55.0, _v(-2.2, 0.90, 14.8), _v(-3.0, 2.15, 0.0)),
    (66.0, _v(-3.0, 0.90, 14.6), _v(-3.7, 2.15, 0.0)),
    (78.0, _v(-1.6, 0.92, 15.0), _v(-2.2, 2.17, 0.0)),
    (92.0, _v(1.0, 0.92, 15.2), _v(1.2, 2.17, 0.0)),
    (106.0, _v(1.6, 0.92, 15.0), _v(1.8, 2.17, 0.0)),
    (126.0, _v(2.0, 0.92, 15.0), _v(2.3, 2.17, 0.0)),
    (137.5, _v(2.9, 0.92, 14.8), _v(3.1, 2.17, 0.0)),
    (146.0, _v(0.0, 0.98, 16.0), _v(-0.6, 2.30, 0.0)),
    (152.5, _v(-0.4, 1.40, 17.5), _v(-0.9, 2.85, 0.0)),
    (158.0, _v(-0.3, 1.15, 18.5), _v(-0.7, 2.85, 0.0)),
    (TOTAL + 1.0, _v(-0.3, 1.13, 18.7), _v(-0.7, 2.83, 0.0)),
]
FOV = 40.0


def _rig(focus=None):
    return Rig([fly(KEYS, fov=FOV, aperture=0.012, focus=focus if focus is not None else "target")],
               blend=1.0, fov=FOV, aperture=0.012, handheld=0.04, min_height=0.3)


LAYOUT = _rig()

# ---------------------------------------------------------------------------------------------- people
CAST = cast05.Cast()
TREE_FX = FX.Tree(TREE_AT, height=2.7)
FRUITS = TREE_FX.fruit

# ---------------------------------------------------------------------------------------------- words
STAR_ENC, STAR_CONS = 6, 7
WORDS = words05.build(LAYOUT, stars={"Encouragement": tuple(arch_point(STAR_ENC)),
                                     "Consideration": tuple(arch_point(STAR_CONS))})


def _focus(t):
    cam = LAYOUT.state(t)
    return WORDS.focus_point(t, lambda t: np.asarray(cam.pos) + 17.0 * np.asarray(cam.basis()[2]))


CAMERA = _rig(lambda t: _focus(t))


# ---------------------------------------------------------------------------------------------- light of the story
def _hands(k):
    return lambda t: 0.5 * (CAST.where(k, t, "palm.R") + CAST.where(k, t, "palm.L"))


def _neck(k, up=0.0):
    return lambda t: CAST.where(k, t, "neck") + _v(0.0, up, 0.0)


def _mid(a, b, lift):
    return lambda t: 0.5 * (a(t) + b(t)) + _v(0.0, lift, 0.0)


def _star(k):
    p = arch_point(k)
    return lambda t: p


def _trio_hands(t):
    return (_hands("A")(t) + _hands("B")(t) + _hands("C")(t)) / 3.0


PRAYER1 = FX.Stream(_hands("A"), _mid(_hands("A"), _neck("B"), 1.6), _neck("B", -0.12),
                    T["cloak"][0], T["cloak"][1], T["rise_B"] + 2.0, FX.VIOLET, seed=31)
ANSWER2 = FX.Stream(_star(STAR_ENC), lambda t: _trio_hands(t) + _v(0.0, 6.0, -2.0), _trio_hands,
                    96.6, 99.4, 99.8, FX.VIOLET, seed=33, around=0.5)
PRAYER2 = FX.Stream(_trio_hands, _mid(_trio_hands, _neck("D"), 1.4), _neck("D", -0.10),
                    99.6, 102.6, T["getup_D"] + 3.0, FX.VIOLET, seed=35)


def _petal_amount(t):
    return (0.10 + 0.10 * _ss(76.0, 82.0, t) + 0.25 * _ss(83.0, 92.0, t) + 0.30 * _ss(112.0, 118.0, t)
            + 0.25 * _ss(146.0, 147.5, t) * (1.0 - _ss(150.0, 157.0, t)) - 0.15 * _ss(155.0, 160.0, t))


WAVES_FX = FX.Waves([(13.6, cast05.TREE), (37.6, cast05.HOME["B"]), (68.8, cast05.HOME["B"]),
                     (107.6, cast05.HOME["D"]), (139.2, cast05.HOME["D"])])


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
    scene.add("s05 scatter", WORDS.clear(FX.Scatter(lambda t: CAST.where("B", t, "palm.R"), _neck("D", -0.1),
                                                    T["reach_B"][0] + 0.6, T["reach_B"][1])))
    scene.add("s05 halos", WORDS.clear(FX.Halos(lambda t: CAST.where("D", t, "head"), _hands("C"),
                                                108.4, 124.0)), reflect=False)
    scene.add("s05 petals", WORDS.clear(FX.Petals(_petal_amount)))
    scene.add("s05 shores", FX.Shores())
    scene.add("s05 road", WORDS.clear(FX.Road(TREE_FX.tip_top(), arch_point(4) + _v(0, -2.0, 0))), reflect=False)
    scene.add("s05 drift", FX.Drift(FRUITS))
    CAST.add(scene)
    WORDS.add_to(scene)


# ---------------------------------------------------------------------------------------------- the world
def _arch_lit(t):
    """Nine (brightness, age): lit from the start 3, 4, 7, 9; 8 lit at the first Consideration; 7 flares again
    after each Encouragement and 8 after the second Consideration."""
    out = []
    enc_t = [-30.0, 37.6, 107.4]
    cons_t = [68.6, 139.0]
    for k in range(9):
        if k in (2, 3, 8):
            out.append((1.0, t + 30.0))
        elif k == STAR_ENC:
            last = max([x for x in enc_t if x <= t])
            out.append((1.0, t - last))
        elif k == STAR_CONS:
            past = [x for x in cons_t if x <= t]
            out.append((1.0, t - past[-1]) if past else (0.0, 0.0))
        else:
            out.append((0.0, 0.0))
    return out


LOOKS = dict(
    # song 04's warm apricot late morning, the hand-off frame
    morning=dict(base="golden", sky_top="#1d3a78", sky_mid="#5d6fa6", sky_hor="#c8905a", sun_color="#fff0d6",
                 sun_int=0.75, sun_el=9.0, sun_az=221.0, clouds=0.30, haze=0.24, haze_color="#8a6c5c",
                 mist=0.05, mist_color="#c8a088", hills=0.8, hill_height=0.55, hill_color="#1c1d36",
                 water="#050b18", rays=0.25, dust_color="#fff0d0", dust_color2="#ffe0b8", ripple=0.25,
                 exposure=0.52),
    # the hazy spring afternoon of verse 1
    haze=dict(base="golden", sky_top="#18336e", sky_mid="#556a9e", sky_hor="#c49468", sun_color="#fff2d8",
              sun_int=0.60, sun_el=9.5, sun_az=221.0, clouds=0.45, haze=0.24, haze_color="#8a6c5c",
              mist=0.05, mist_color="#b8a090", hills=0.8, hill_height=0.55, hill_color="#1c1d36",
              water="#050b18", rays=0.22, dust_color="#fff4dc", dust_color2="#e8f0b0", ripple=0.35,
              exposure=0.50),
    # the bright clear afternoon of verse 2
    bright=dict(base="golden", sky_top="#173a7c", sky_mid="#5a76b0", sky_hor="#cc955e", sun_color="#fff4dc",
                sun_int=0.85, sun_el=9.0, sun_az=221.0, clouds=0.25, haze=0.24, haze_color="#8a6c5c",
                mist=0.05, mist_color="#d0a888", hills=0.8, hill_height=0.55, hill_color="#1c1d36",
                water="#050b18", rays=0.30, dust_color="#fff4dc", dust_color2="#ffd6e0", ripple=0.30,
                exposure=0.54),
    # the climax: the sun breaks through the haze
    glory=dict(base="golden", sky_top="#1e3a7a", sky_mid="#7a6fa8", sky_hor="#e0a060", sun_color="#fff0cc",
               sun_int=1.15, sun_el=8.0, sun_az=221.0, sun_glow=0.9, clouds=0.30, haze=0.40,
               haze_color="#8a6c5c", mist=0.05, mist_color="#e0a878", hills=0.8, hill_height=0.55,
               hill_color="#1c1d36", water="#050b18", rays=0.75, dust_color="#fff4dc", dust_color2="#ffe0b0",
               ripple=0.25, exposure=0.58),
    # the hold: warm late afternoon, the hand-off to song 06 (sun lower, light haze)
    late=dict(base="golden", sky_top="#1c3c7c", sky_mid="#6676a8", sky_hor="#cc9460", sun_color="#ffe9b8",
              sun_int=0.85, sun_el=7.0, sun_az=221.0, sun_glow=0.8, clouds=0.25, haze=0.24, haze_color="#8a6c5c",
              mist=0.05, mist_color="#d0a080", hills=0.8, hill_height=0.55, hill_color="#1c1d36",
              water="#050b18", rays=0.40, dust_color="#fff0d0", dust_color2="#ffe0b8", ripple=0.15,
              exposure=0.52),
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
    arch=dict(lit=_arch_lit, colors=FX.NINE, span=ARCH05["span"], height=ARCH05["height"], z=ARCH05["z"], bright=1.25,
              line=1.0),
    lights=[dict(pos=lambda t: TREE_AT + _v(0.0, 1.8, 0.0), color="#ffd890",
                 strength=lambda t: 0.2 + 0.5 * _ss(52.0, 82.0, t) + 0.6 * _ss(146.0, 148.0, t), radius=4.0),
            dict(pos=lambda t: CAST.where("B", t, "chest"), color="#ffd27a",
                 strength=lambda t: 0.6 * _ss(37.5, 48.0, t) * (1.0 - _ss(68.0, 76.0, t)), radius=3.0)],
    react=dict(beat=0.10, level=0.25),
)

P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=[],
    motion_blur=0.3,
)

# ---------------------------------------------------------------------------------------------- titles
TITLE = dict(label="Healing Concert", lines=["God Bless You"], size=120, y=0.27, label_size=40, form=1e9,
             hold=1e9, star=1e9, color="#ffffff", glow="#ffffff", anim="ribbon")     # never shown
TAGLINE = dict(text="God Bless You", sizes=(60, 60), t0=1e9, t1=1e9 + 1.0, color="#ffffff", glow="#ffffff",
               anim="rise")                                                         # never shown
TITLES = dict(signature=dict(windows=[(12.5, TOTAL + 5.0, "bl", "night")], fade=1.2))
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
