"""The style presets of engine/p3d/styles.py, one after another (engine/UPGRADE-HOWTO.md, section Y2, "People
styles"). Not a concert video: a proving ground for every artistic look of the people, each on its own stage far
from the others, 3.75 seconds each, cut hard, set to the concert medley (audio/promo/concert-medley.mp3).

Stages (start times; `python -c "import songs.demo_styles as s; s.listing()"` prints them):
   0.00  constellation          night   p01
   3.75  spark_profile          night   p06
   7.50  nebula_profile         day     p07
  11.25  butterflies            day     p02
  15.00  glass_shatter          day     p05
  18.75  ember_dancer           day     p04
  22.50  ash_dissolve           day     p03 (a second, whole figure beside him)
  26.25  gold_glitter           day     p08
  30.00  mist_figure            night   p09
  33.75  dark_silhouette        night   (a glow behind)
  37.50  sky_window             night   (ref 08)
  41.25  star_silhouette        day
  45.00  glitter_profile        night
  48.75  constellation_profile  day
  52.50  nebula_figure          night
  56.25  dark_silhouette        day     (frayed edge)

STYLES_FLIP=1 in the environment turns every day stage to night and every night stage to day (to check that
each preset works on both skies; not for the proof video). No lyrics, no words: the flat text is switched off.
"""
import os

import songs.s03_original as _base

STAGE = 3.75
_N = 16
_base.TOTAL = STAGE * _N
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = _base.TOTAL - 0.1
_base.FADE = _base.Track([(0.0, 1.0), (_base.TOTAL - 0.3, 1.0), (_base.TOTAL - 0.02, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (_base.TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import numpy as np  # noqa: E402

from p3d import styles as ST  # noqa: E402
from p3d.api import show  # noqa: E402
from p3d.camera import Rig, hold, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
GAP = 80.0                 # metres between stages along x
FLIP = os.environ.get("STYLES_FLIP", "") not in ("", "0")

STAGES = []                # (name, setup(scene, x, t0, sky), camera(x, t0, t1), look, sky)


def stage(name, cam, sky="night", look=None):
    if FLIP:
        sky = "day" if sky == "night" else "night"
        look = None
    look = look or ("night" if sky == "night" else "pale")

    def deco(fn):
        STAGES.append((name, fn, cam, look, sky))
        return fn
    return deco


def listing():
    for k, st in enumerate(STAGES):
        print("%6.2f  %-22s %s" % (k * STAGE, st[0], st[4]))


def win(t0):
    return dict(show=(t0, t0 + STAGE), fade=0.01)


# ------------------------------------------------------------------------------------------------ the stages
@stage("constellation", lambda x, t0, t1: orbit((x, 1.0, 0.0), radius=(3.3, 3.1), height=1.15, a0=12.0, a1=24.0,
                                                t0=t0, t1=t1, fov=40, aperture=0.0))
def s_constellation(scene, x, t0, sky):
    ST.add_parked(scene, "constellation", name="c", sky=sky, shape="man", at=(x, 0.0), facing=110.0, **win(t0))


@stage("spark_profile", lambda x, t0, t1: hold((x + 0.06, 1.69, 1.30), (x + 0.06, 1.66, 0.0), t0, t1, fov=34,
                                               aperture=0.025, drift=(0.03, 0.01, -0.05)))
def s_spark(scene, x, t0, sky):
    ST.add_parked(scene, "spark_profile", name="sp", sky=sky, at=(x, 1.70, 0.0), facing=90.0, height=0.40,
           tilt=lambda t: 9.0 + 3.0 * np.sin((t - t0) * 0.6), eye_glow=0.4, **win(t0))


@stage("nebula_profile", lambda x, t0, t1: hold((x - 0.05, 1.98, 1.45), (x - 0.05, 1.93, 0.0), t0, t1, fov=36,
                                                aperture=0.02, drift=(-0.04, 0.0, -0.06)), sky="day", look="pale")
def s_nebula_profile(scene, x, t0, sky):
    ST.add_parked(scene, "nebula_profile", name="np", sky=sky, at=(x, 2.0, 0.0), facing=-90.0, height=0.50, tilt=7.0,
           t=t0 + 0.6, **win(t0))


@stage("butterflies", lambda x, t0, t1: hold((x - 0.10, 1.95, 1.65), (x - 0.10, 1.88, 0.0), t0, t1, fov=40,
                                             aperture=0.02, drift=(0.03, 0.0, -0.05)), sky="day", look="pastel")
def s_butterflies(scene, x, t0, sky):
    ST.add_parked(scene, "butterflies", name="bf", sky=sky, at=(x, 2.0, 0.0), facing=90.0, height=0.45, t=t0 + 0.3,
           **win(t0))


@stage("glass_shatter", lambda x, t0, t1: hold((x + 0.35, 1.30, 2.7), (x + 0.25, 1.25, 0.0), t0, t1, fov=42,
                                               aperture=0.02), sky="day", look="mistgreen")
def s_glass(scene, x, t0, sky):
    ST.add_parked(scene, "glass_shatter", name="gs", sky=sky, at=(x, 0.0), facing=-25.0, t=t0 + 0.9, **win(t0))


@stage("ember_dancer", lambda x, t0, t1: hold((x + 0.2, 1.05, 4.6), (x + 0.2, 1.0, 0.0), t0, t1, fov=40,
                                              aperture=0.02), sky="day", look="amber")
def s_ember(scene, x, t0, sky):
    ST.add_parked(scene, "ember_dancer", name="ed", sky=sky, at=(x + 0.4, 0.0), facing=90.0, t=t0 + 0.4,
           **win(t0))


@stage("ash_dissolve", lambda x, t0, t1: hold((x + 0.2, 1.25, 4.0), (x + 0.2, 1.1, 0.0), t0, t1, fov=40,
                                              aperture=0.02), sky="day", look="mistgreen")
def s_ash(scene, x, t0, sky):
    ST.add_parked(scene, "ash_dissolve", name="ad", sky=sky, at=(x - 0.15, -0.2), facing=20.0, t=t0 + 0.3, **win(t0))
    ST.add_parked(scene, "dark_silhouette", name="ad2", sky=sky, shape="woman", at=(x + 0.55, 0.1), facing=-35.0,
           edge=None, **win(t0))


@stage("gold_glitter", lambda x, t0, t1: hold((x - 0.1, 1.25, 3.1), (x + 0.1, 1.15, 0.0), t0, t1, fov=38,
                                              aperture=0.04), sky="day", look="pale")
def s_gold(scene, x, t0, sky):
    ST.add_parked(scene, "gold_dispersal", name="gg", sky=sky, at=(x, 0.0), facing=-10.0, t=t0 + 0.6, **win(t0))


@stage("mist_figure", lambda x, t0, t1: hold((x, 1.25, 7.0), (x, 1.05, -6.0), t0, t1, fov=34, aperture=0.05,
                                             drift=(0.0, 0.0, -0.3)), look="mistnight")
def s_mist(scene, x, t0, sky):
    ST.add_parked(scene, "mist_figure", name="mf", sky=sky, at=(x, -6.0), facing=180.0, **win(t0))


@stage("dark_silhouette", lambda x, t0, t1: hold((x + 0.1, 1.15, 3.8), (x + 0.1, 1.05, 0.0), t0, t1, fov=38,
                                                 aperture=0.02))
def s_dark_night(scene, x, t0, sky):
    ST.add_parked(scene, "dark_silhouette", name="dn", sky=sky, shape="man", garment="coat", at=(x, 0.0), facing=70.0,
           t=t0, **win(t0))


@stage("sky_window", lambda x, t0, t1: hold((x + 0.12, 1.40, 2.1), (x + 0.12, 1.32, 0.0), t0, t1, fov=36,
                                            aperture=0.02))
def s_window(scene, x, t0, sky):
    ST.add_parked(scene, "sky_window", name="sw", sky=sky, at=(x, 0.0), facing=90.0, t=t0 + 0.4,
           gesture=[(t0 - 1.0, t0 + 30.0, "look_up", dict(amount=12))], **win(t0))


@stage("star_silhouette", lambda x, t0, t1: hold((x, 1.0, 3.8), (x, 0.95, 0.0), t0, t1, fov=40, aperture=0.02),
       sky="day", look="pastel")
def s_star(scene, x, t0, sky):
    ST.add_parked(scene, "star_silhouette", name="ss", sky=sky, at=(x, 0.0), facing=-90.0,
           gesture=[(t0 - 1.0, t0 + 30.0, "open_arms", dict(lift=0.5))], **win(t0))


@stage("glitter_profile", lambda x, t0, t1: hold((x + 0.05, 1.80, 1.40), (x + 0.05, 1.76, 0.0), t0, t1, fov=36,
                                                 aperture=0.025, drift=(0.03, 0.0, -0.05)))
def s_glitter_profile(scene, x, t0, sky):
    ST.add_parked(scene, "glitter_profile", name="gp", sky=sky, shape="man", at=(x, 1.80, 0.0), facing=90.0,
           height=0.45, tilt=lambda t: 3.0 + 4.0 * np.sin((t - t0) * 0.5), **win(t0))


@stage("constellation_profile", lambda x, t0, t1: hold((x - 0.05, 1.80, 1.40), (x - 0.05, 1.76, 0.0), t0, t1,
                                                       fov=36, aperture=0.0, drift=(-0.03, 0.0, -0.05)),
       sky="day", look="pale")
def s_constellation_profile(scene, x, t0, sky):
    ST.add_parked(scene, "constellation_profile", name="cp", sky=sky, at=(x, 1.80, 0.0), facing=-90.0, height=0.45,
           tilt=6.0, **win(t0))


@stage("nebula_figure", lambda x, t0, t1: hold((x + 0.1, 1.30, 2.5), (x + 0.1, 1.22, 0.0), t0, t1, fov=38,
                                               aperture=0.02))
def s_nebula_figure(scene, x, t0, sky):
    ST.add_parked(scene, "nebula_figure", name="nf", sky=sky, at=(x, 0.0), facing=90.0, t=t0 + 0.8,
           gesture=[(t0 - 1.0, t0 + 30.0, "look_up", dict(amount=10))], **win(t0))


@stage("dark_silhouette, frayed", lambda x, t0, t1: hold((x + 0.1, 1.15, 3.6), (x + 0.1, 1.05, 0.0), t0, t1,
                                                          fov=38, aperture=0.02), sky="day", look="amber")
def s_dark_day(scene, x, t0, sky):
    ST.add_parked(scene, "dark_silhouette", name="dd", sky=sky, at=(x, 0.0), facing=-80.0, t=t0, share=0.35,
           gesture=[(t0 - 1.0, t0 + 30.0, "raise_hand", dict(side="R"))], **win(t0))


# ------------------------------------------------------------------------------------------------ build
def _setup(scene):
    for k, st in enumerate(STAGES):
        st[1](scene, k * GAP, k * STAGE, st[4])


def _d(hexs, k=1.0):
    return tuple(float(v) * k for v in show(hexs))


LOOKS = dict(
    pale=dict(base="cream", sky_top=_d("#c6ccd2"), sky_mid=_d("#e4e2dc"), sky_hor=_d("#efede7"),
              haze_color=_d("#e8e6e0"), mist=0.35, mist_color=_d("#ebe8e2"), hills=0.35, hill_color=_d("#c4c8cc"),
              water=_d("#c8ccd0"), sun_int=0.35, sun_el=24.0, sun_az=120.0, clouds=0.12, dust=0.0, rays=0.0),
    pastel=dict(base="cream", sky_top=_d("#9fb0e2"), sky_mid=_d("#d4c4e8"), sky_hor=_d("#f8dccc"),
                haze_color=_d("#f2d8d8"), mist=0.3, mist_color=_d("#f0dcd8"), hills=0.25, hill_color=_d("#c8b8d8"),
                water=_d("#c8c0e0"), sun_int=0.5, sun_el=12.0, sun_az=60.0, sun_color=_d("#fff2e0"), clouds=0.05,
                dust=0.3, rays=0.0),
    mistgreen=dict(base="cream", sky_top=_d("#55686a"), sky_mid=_d("#9aaca8"), sky_hor=_d("#c9d2cc"),
                   haze=1.0, haze_color=_d("#b9c6c0"), mist=0.9, mist_height=3.0, mist_color=_d("#b4c2bc"),
                   hills=0.2, hill_color=_d("#8a9a96"), water=_d("#7a8c8a"), sun_int=0.25, sun_el=18.0,
                   clouds=0.25, dust=0.2, rays=0.0),
    amber=dict(base="cream", sky_top=_d("#e9b45a"), sky_mid=_d("#f8d890"), sky_hor=_d("#fff0cc"),
               haze_color=_d("#fbe6b8"), mist=0.3, mist_color=_d("#fbe4b4"), hills=0.2, hill_color=_d("#e0b880"),
               water=_d("#e8c890"), sun_int=0.9, sun_el=8.0, sun_az=100.0, sun_color=_d("#fff4d8"), clouds=0.05,
               dust=0.3, rays=0.0),
    mistnight=dict(base="night", sky_top="#03050f", sky_mid="#121a3a", sky_hor="#3a4772", haze=1.0,
                   haze_color="#3a4670", mist=1.0, mist_height=3.0, mist_color="#3c4a78", stars=0.5, milky=0.2,
                   bokeh=1.2, dust=1.0),
)

P3D = dict(
    camera=Rig([st[2](k * GAP, k * STAGE, (k + 1) * STAGE) for k, st in enumerate(STAGES)], blend=0.0),
    world=dict(look=[(k * STAGE, st[3], 0.0) for k, st in enumerate(STAGES)], looks=LOOKS),
    setup=_setup,
)
