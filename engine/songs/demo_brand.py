"""The brand pieces, one after another (60 seconds on the medley; engine/UPGRADE-HOWTO.md, section Z).

Not a concert video: a proof of what helper BRAND built for the five films (engine/p3d/brand*.py).

   0.0 to  8.0   THE LOGO builds itself out of light over a night lake: the two hearts sweep in from either
                 side, the globe's disc fills and its ring and grid draw themselves, the olive branches grow;
                 it turns from light to its exact colours, holds, and lifts apart into sparks
   8.0 to 16.0   HEARTS: heart bokeh near the lens, small sparkling hearts, heart petals on the wind, hearts
                 drifting off a light in the Greeting's colour, fireflies gathering into a heart
  16.0 to 40.0   THE NINE SYMBOLS as quiet scenery, each in its website colour and each a different recipe:
                 16.4 Greeting traced by fireflies, 19.0 Gratitude a constellation, 21.6 Apology over the
                 water, its reflection rippling, 24.2 Inclusiveness made of petals, 26.8 Concession a flock
                 of birds passing, 29.4 Respect a light trail, 32.0 Encouragement traced by sparks, 34.6 Consideration made of
                 heart petals, 37.2 Compliment a drift of embers
  40.0 to 47.5   THE WORLD by day: a clear blue and green Earth with white clouds on a bright sky, hearts
                 lighting up across it
  47.5 to 60.0   THE FINALE: the world of light at night (golden continents, drifting clouds, a soft air),
                 hearts in the nine colours blooming across it from Las Vegas, joined by arcs, a warm light
                 rising from below it where hands would cradle it (49.6 to 53.2); it slows
                 and settles (52.2 to 54.0) and becomes the logo (53.0 to 55.0): the hearts sweep in behind it,
                 the ring and the grid draw themselves over the Earth, the logo's globe spreads over it, the
                 branches grow; light blooms from it into a pastel day (54.3), and the logo rises into the end
                 card's place at the top of the frame (55.0 to 56.4), held to the end
  demo_brand_finale.py plays 40.0 to 60.0 of this song as a 20 second proof (the same pieces).
"""
import numpy as np

import songs.s03_original as _base

TOTAL = 60.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 59.6
_base.SONG_END = 60.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import brand as BR  # noqa: E402
from p3d.camera import Rig, dolly, orbit  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 59.6
SONG_END = 60.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

GLOBE_AT = (0.0, 13.0, -44.0)


# ------------------------------------------- the world by day and the finale (shared with demo_brand_finale)
def world_moves(o=0.0):
    """The camera for the world by day (40.0 to 47.5) and the finale (47.5 to 60.0), `o` seconds later."""
    return [
        # the world by day, then the finale: a slow push toward the globe
        dolly((0.0, 7.0, 6.0), (0.0, 8.5, 2.0), 40.0 + o, 47.5 + o, look=(GLOBE_AT, GLOBE_AT), fov=40.0,
              aperture=0.0, blend=0.0),
        dolly((0.0, 9.0, 8.0), (0.0, 11.0, 0.0), 47.5 + o, 60.0 + o, look=(GLOBE_AT, GLOBE_AT), fov=40.0,
              aperture=0.0, blend=0.0, ease="out"),
    ]


def world_pieces(camera, o=0.0):
    """The day globe and the finale, `o` seconds later than in this song."""
    day = BR.Globe(pos=GLOBE_AT, radius=9.0, camera=camera, look="day", spin=7.0, front=-60.0, t_in=40.0 + o,
                   t_out=46.6 + o, fade=0.8, hearts=dict(t0=41.0 + o, t1=45.6 + o, n=36))
    fin = BR.Finale(pos=GLOBE_AT, radius=11.5, shrink=0.47, camera=camera, look="night", t_world=47.6 + o,
                    spin=8.0, front=-150.0, hearts=dict(t0=48.4 + o, t1=52.6 + o, n=44),
                    t_settle=(52.2 + o, 54.0 + o), t_logo=(53.0 + o, 55.0 + o), bloom=dict(t=54.3 + o),
                    end=dict(t=(55.0 + o, 56.4 + o), ride=(0.5, 0.74, 14.0), frac=0.27),
                    cradle=dict(t0=49.6 + o, t1=53.2 + o))       # light rising from where hands would cradle it
    return day, fin


def world_p3d(camera, fin, looks, o=0.0):
    """The P3D world and bursts for these pieces: `looks` before the day globe, then day, then night (each
    change a short blend through dusk, never a flash)."""
    world = fin.world(dict(look=list(looks) + [(40.0 + o, "day", 0.8), (47.5 + o, "night", 0.8)], arch=None,
                           react=dict(beat=0.3, level=0.2)))
    return world, fin.bursts()


# --------------------------------------------------------------------------------------------- the camera
LOGO_AT = (0.0, 6.2, -6.0)
CAMERA = Rig([
    orbit((0.0, 5.0, -6.0), radius=(26.0, 22.0), height=(3.0, 4.2), a0=-10.0, a1=8.0, t0=0.0, t1=8.0,
          look=(0.0, 6.0, -6.0), fov=40.0, aperture=0.04, focus="target"),
    # hearts: the lens on the middle distance; the near hearts are bokeh
    dolly((-1.5, 3.4, 17.0), (1.5, 3.8, 15.0), 8.0, 16.0, look=((0.0, 4.6, 0.0), (0.3, 4.8, 0.0)), fov=42.0,
          aperture=0.09, focus=15.5, blend=0.0),
    # the symbols: a slow drift along the shore; for the Apology the camera comes down toward the water
    dolly((-3.0, 4.6, 21.0), (-1.5, 4.5, 20.5), 16.0, 21.0, look=((-1.0, 6.0, -4.0), (-0.5, 5.9, -4.0)), fov=46.0,
          aperture=0.02, focus=24.0, blend=0.0),
    dolly((0.0, 3.6, 20.0), (0.5, 3.8, 19.0), 21.0, 24.4, look=((0.0, 1.2, 2.0), (0.3, 1.2, 2.0)), fov=46.0,
          aperture=0.0, blend=1.0),
    dolly((-1.0, 4.5, 20.5), (3.0, 4.2, 19.0), 24.4, 40.0, look=((-0.5, 5.9, -4.0), (1.0, 5.6, -4.0)), fov=46.0,
          aperture=0.02, focus=24.0, blend=1.0),
] + world_moves(), blend=1.5, handheld=0.12)

# ---------------------------------------------------------------------------------------------- the logo
LOGO = BR.Logo(pos=LOGO_AT, size=6.0, face="camera", camera=CAMERA, t_in=0.4, t_full=4.6, t_out=6.6,
               leave_dur=1.6, arrive="build", leave="rise", paint=lambda t: float(np.clip((t - 4.4) / 0.8, 0, 1)))

# -------------------------------------------------------------------------------------------- the hearts
ORB = (-3.6, 4.2, 0.5)          # stands in for an expression being read: hearts drift off it in its colour


class _Orb:
    """A soft light where a word would be (the hearts drift off it)."""

    def sample(self, t):
        a = float(np.clip((t - 8.8) / 0.6, 0, 1) * np.clip((14.8 - t) / 0.6, 0, 1))
        if a <= 0:
            return None
        return [dict(pos=np.array([ORB]), size=0.25, color=BR.lin("#EA5A5E") * 2.0, alpha=a, kind="spark", emit=2.0),
                dict(pos=np.array([ORB]), size=1.6, color=BR.lin("#EA5A5E") * 0.6, alpha=0.25 * a, kind="soft")]


HEARTS = [
    ("bokeh", BR.Hearts("bokeh", n=14, center=(0.0, 4.5, 9.0), box=(12.0, 6.0, 4.0), size=(0.25, 0.45),
                        t0=8.0, t1=16.0, fade=0.6)),
    ("sparkle", BR.Hearts("sparkle", n=40, center=(0.0, 6.0, -4.0), box=(22.0, 7.0, 6.0), t0=8.0, t1=16.0,
                          fade=0.6)),
    ("petals", BR.Hearts("petal", n=50, center=(0.0, 4.0, 2.0), box=(22.0, 7.0, 8.0), drift=(0.6, -0.15, 0.1),
                         colors=["#EE62A6", "#F2B25E", "#EA5A5E", "#ffc6d9"], t0=8.0, t1=16.0, fade=0.6)),
    ("drift", BR.HeartDrift(ORB, 9.2, 14.2, color="Greeting", rate=11.0, life=2.6, style="sparkle")),
    ("form", BR.HeartForm((3.2, 5.4, -1.0), size=3.4, face="camera", camera=CAMERA, n=180, scatter=5.0,
                          t0=9.0, t1=11.4, hold=2.6, release=1.4, then="up", color="#ffd98a")),
    ("orb", _Orb()),
]

# ------------------------------------------------------------------------------------------ the symbols
_K = 0.55          # stronger than the default (0.35) so that every recipe can be judged in the proof stills
SYMS = [
    BR.Traced("Greeting", pos=(-6.5, 7.6, -6.0), size=4.0, camera=CAMERA, t0=16.4, intensity=_K),
    BR.Constellation("Gratitude", pos=(30.0, 70.0, -190.0), size=46.0, camera=CAMERA, t0=19.0, dur=1.8,
                     intensity=_K),
    BR.Ripples("Apology", pos=(0.3, 2.9, 2.0), size=4.0, camera=CAMERA, t0=21.6, intensity=_K),
    BR.PetalShape("Inclusiveness", pos=(6.0, 6.2, -5.0), size=4.2, camera=CAMERA, t0=24.2, intensity=_K),
    BR.Flock("Concession", pos=(-5.0, 9.0, -14.0), size=7.0, camera=CAMERA, t0=26.4, dur=2.6, intensity=_K),
    BR.LightTrail("Respect", pos=(0.5, 7.0, -8.0), size=5.0, camera=CAMERA, t0=29.4, intensity=_K),
    BR.Traced("Encouragement", style="sparks", pos=(6.0, 7.2, -6.0), size=5.0, camera=CAMERA, t0=32.0,
              intensity=_K),
    BR.PetalShape("Consideration", carrier="heart", petal_size=0.05, wind=(-1.0, 0.2), pos=(-5.5, 6.6, -5.0),
                  size=4.2, camera=CAMERA, t0=34.6, intensity=_K),
    BR.Flock("Compliment", carrier="ember", pos=(4.0, 7.6, -8.0), size=5.6, camera=CAMERA, t0=37.0, dur=2.6,
             intensity=_K),
]

# ---------------------------------------------------------------------- the world by day and the finale
DAY_GLOBE, FINALE = world_pieces(CAMERA)


def _setup(scene):
    scene.add("logo", LOGO)
    for name, s in HEARTS:
        scene.add("hearts " + name, s)
    for i, s in enumerate(SYMS):
        scene.add("symbol %d" % i, s, reflect=False)
    scene.add("day globe", DAY_GLOBE)
    FINALE.add_to(scene)


_WORLD, _BURSTS = world_p3d(CAMERA, FINALE, [(0.0, "night")])
P3D = dict(camera=CAMERA, world=_WORLD, setup=_setup, bursts=_BURSTS)
