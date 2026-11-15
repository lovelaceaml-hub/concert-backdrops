"""The two approved looks of the people, crystal_light and gold_glitter (engine/p3d/styles.py; engine/UPGRADE-
HOWTO.md, section Y2), in five short heavenly tableaux on the sections of the concert medley
(audio/promo/concert-medley.mp3). A proof, not a concert video: no words.

   0.00  a woman of crystal light in a cathedral of light shafts among golden clouds
   6.84  two people of gold meet and embrace, and light blooms from the embrace
  13.30  an elder of crystal kneels in prayer under falling light
  19.85  a man of gold lifts a woman of crystal from her knees, by a river of light
  26.79  a man, a woman, a child and an elder, crystal and gold, raise lights under an aurora
"""
import songs.s03_original as _base

SECTIONS = (0.0, 6.84, 13.30, 19.85, 26.79, 33.36)
END = 34.9
_base.TOTAL = END
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = _base.TOTAL - 0.1
_base.FADE = _base.Track([(0.0, 0.0), (0.5, 1.0), (SECTIONS[5], 1.0), (END - 0.05, 0.0)])
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

from p3d import pairs  # noqa: E402
from p3d import styles as ST  # noqa: E402
from p3d import stylekit as K  # noqa: E402
from p3d.camera import Rig, dolly, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
GAP = 160.0
X = [k * GAP for k in range(5)]
S = SECTIONS


def _in(k, t, pad=0.0):
    return S[k] - pad <= t < (S[k + 1] if k < 4 else END + 1.0) + pad


def win(k):
    return (S[k] - 0.02, (S[k + 1] if k < 4 else END + 1.0) + 0.02)


def _on(k, v=1.0):
    return lambda t: v if _in(k, t) else 0.0


# ------------------------------------------------------------------------------------------------ the tableaux
def t1_cathedral(scene):
    """A woman of crystal light, arms opening, face lifting to the light, in a cathedral of light shafts."""
    x = X[0]
    me = ST.person(scene, "crystal_light", "c1", shape="woman", at=(x, 0.0), facing=0.0, garment="robe",
                   show=win(0), fade=0.01, seed=3.0,
                   gesture=[(0.8, 9.0, "open_arms", dict(lift=0.22, ease=1.6)),
                            (2.6, 9.0, "look_up", dict(amount=16.0, ease=1.8))])
    scene.add("c1_clouds", K.CloudBank((x, 22.0, -110.0), size=(170.0, 22.0, 30.0), n=700, light=(x, 4.0, -300.0),
                                       color="#ffc070", color2="#d0609a", bright=1.0, show=win(0)))
    scene.add("c1_fall", K.Sparkles((x, 2.6, -1.0), box=(4.0, 2.6, 3.0), n=500, stars=16, size=0.03, color="#fff2d0",
                                    color2="#ffd08a", bright=0.7, drift=-0.12, show=win(0), seed=4.0))
    return me


def t2_embrace(scene):
    """Two people of gold walk in and hold each other; light blooms from the embrace."""
    x = X[1]
    t = S[1] + 1.6
    # (pairs.embrace's approach= walks them in from metres away: they stand close and open their arms instead)
    arms = [(S[1] - 0.5, t + 0.2, "open_arms", dict(lift=0.05, ease=1.2))]
    a, b = pairs.embrace(t, at=(x, 0.0), facing=90.0, gap=0.34, ease=1.6,
                         a=ST.keys("gold_glitter", shape="woman", garment="dress", show=win(1), fade=0.01, seed=5.0,
                                   gesture=list(arms), light=(x, 4.2, 3.2)),
                         b=ST.keys("gold_glitter", shape="man", garment="tunic", show=win(1), fade=0.01, seed=6.0,
                                   gesture=list(arms), light=(x, 4.2, 3.2)))
    a.add(scene, "g2a")
    b.add(scene, "g2b")
    ST.dress(scene, "g2a", a, "gold_glitter")
    ST.dress(scene, "g2b", b, "gold_glitter", wind=(-0.25, 0.0, 0.10))

    def meet(tt):
        return 0.5 * (np.asarray(a.where(tt, "chest")) + np.asarray(b.where(tt, "chest")))
    scene.add("g2_bloom", K.Bloom(meet, t + 0.6, dur=4.5, radius=1.5, n=700, bright=0.5, seed=7.0))
    scene.add("g2_clouds", K.CloudBank((x, 20.0, -120.0), size=(180.0, 20.0, 30.0), n=700, light=(x, 4.0, -300.0),
                                       color="#ffb870", color2="#c0588a", bright=0.9, show=win(1), seed=3.0))
    return a, b


def t3_prayer(scene):
    """An elder of crystal kneels in prayer; light falls round her like a slow snow of gold."""
    x = X[2]
    me = ST.person(scene, "crystal_light", "c3", shape="woman", height=1.56, stoop=0.3, at=(x, 0.0), facing=25.0,
                   garment="robe", show=win(2), fade=0.01, seed=8.0,
                   motion=[(S[2] - 1.0, "stand"), (S[2] + 0.5, "kneel", dict(dur=2.4, hands="pray", sit=0.2))],
                   dress=dict(bloom=1.3))
    scene.add("c3_fall", K.Sparkles((x, 3.2, 0.0), box=(2.2, 3.2, 2.2), n=1100, stars=50, size=0.035,
                                    color="#ffd890", color2="#ffb050", bright=0.9, drift=-0.30, show=win(2), seed=9.0))
    scene.add("c3_fall2", K.Sparkles((x, 6.0, -6.0), box=(9.0, 6.0, 6.0), n=1400, stars=40, size=0.06,
                                     color="#ffd8a0", color2="#ffa8b8", bright=0.7, drift=-0.45, show=win(2), seed=10.0))
    scene.add("c3_clouds", K.CloudBank((x, 34.0, -130.0), size=(180.0, 20.0, 30.0), n=600, light=(x, 80.0, -100.0),
                                       color="#ffd090", color2="#9a70c8", bright=0.8, show=win(2), seed=4.0))
    return me


def t4_lifted(scene):
    """A man of gold reaches down and lifts a woman of crystal to her feet; a river of light flows past."""
    x = X[3]
    t = S[3] + 2.6
    a, b = pairs.helped_up(t, at=(x, 0.0), facing=90.0, rise=1.9, reach=1.1,
                           a=ST.keys("gold_glitter", shape="man", garment="tunic", show=win(3), fade=0.01, seed=11.0,
                                     light=(x, 4.2, 3.5)),
                           b=ST.keys("crystal_light", shape="woman", garment="tunic", show=win(3), fade=0.01,
                                     seed=12.0, light=(x, 4.2, 3.5)))
    a.add(scene, "g4a")
    b.add(scene, "c4b")
    ST.dress(scene, "g4a", a, "gold_glitter")
    ST.dress(scene, "c4b", b, "crystal_light")
    path = [(x - 90.0, -160.0), (x - 45.0, -70.0), (x - 18.0, -22.0), (x - 4.0, -6.5), (x + 8.0, -4.5),
            (x + 22.0, -12.0), (x + 50.0, -40.0)]
    scene.add("r4_river", K.LightRiver(path, width=3.6, n=60000, speed=1.4, color="#ffc860", color2="#fff0d0",
                                       bright=1.0, show=win(3)))
    scene.add("r4_clouds", K.CloudBank((x, 24.0, -130.0), size=(180.0, 20.0, 30.0), n=700,
                                       light=(x - 40.0, 6.0, -300.0), color="#ffc070", color2="#c8609a", bright=0.9,
                                       show=win(3), seed=5.0))
    return a, b


def t5_aurora(scene):
    """A man, a woman, a child and an elder, crystal and gold, raise lights that float up under an aurora."""
    x = X[4]
    t0 = S[4]
    people = [
        ("gold_glitter", "g5man", dict(shape="man", at=(x - 1.7, -0.3), facing=-14.0, garment="tunic"), 0.7),
        ("crystal_light", "c5woman", dict(shape="woman", at=(x - 0.45, 0.25), facing=-4.0, garment="dress"), 1.3),
        ("gold_glitter", "g5child", dict(shape="child", at=(x + 0.55, 0.45), facing=8.0), 1.0),
        ("crystal_light", "c5elder", dict(shape="man", height=1.68, stoop=0.35, at=(x + 1.65, -0.15), facing=16.0,
                                          garment="coat"), 1.6),
    ]
    out = []
    for k, (style, name, kw, lag) in enumerate(people):
        up = t0 + lag
        g = [(t0 - 1.0, 40.0, "cup", dict(ease=0.6)),
             (up, 40.0, "raise_hand", dict(side="R", ease=1.1)),
             (up + 0.4, 40.0, "look_up", dict(amount=22.0, ease=1.4))]
        st = ST.person(scene, style, name, show=win(4), fade=0.01, seed=20.0 + k, gesture=g,
                       dress=dict(motes=0.6, trails=0.7), **kw)
        scene.add(name + "_light", K.HandLight(st.main, "palm.R", born=t0 - 0.5, release=up + 1.7 + 0.25 * k,
                                               rise=0.55, seed=30.0 + k))
        out.append(st)
    scene.add("a5_aurora", K.Aurora(center=(x, -460.0), span=1300.0, height=(95.0, 340.0), n=700, folds=80.0,
                                    colors=("#9affd0", "#ffb8e0", "#b89cff"), bright=0.9, show=win(4)))
    scene.add("a5_lanterns", K.Sparkles((x, 7.0, -14.0), box=(16.0, 6.0, 10.0), n=600, stars=30, size=0.08,
                                        color="#ffe2a8", color2="#ffb070", bright=0.7, drift=0.25, show=win(4),
                                        seed=12.0))
    return out


def _setup(scene):
    t1_cathedral(scene)
    t2_embrace(scene)
    t3_prayer(scene)
    t4_lifted(scene)
    t5_aurora(scene)


# ---------------------------------------------------------------------------------------------- camera and world
def _cams():
    x = X
    return [
        dolly((x[0] + 0.9, 0.95, 5.6), (x[0] + 0.3, 1.30, 2.5), S[0], S[1], look=((x[0], 1.20, 0.0), (x[0], 1.40, 0.0)),
              fov=36, aperture=0.03, ease="smooth"),
        orbit((x[1], 1.15, 0.0), radius=(4.4, 3.2), height=(1.25, 1.40), a0=-8.0, a1=12.0, t0=S[1], t1=S[2],
              look=(x[1], 1.25, 0.0), fov=38, aperture=0.03),
        dolly((x[2] + 3.3, 2.2, 1.9), (x[2] + 2.8, 1.15, 1.2), S[2], S[3], look=((x[2], 1.0, 0.0), (x[2], 0.80, 0.0)),
              fov=40, aperture=0.03, ease="smooth"),
        orbit((x[3], 1.0, 0.0), radius=(4.6, 4.0), height=(1.05, 1.25), a0=-12.0, a1=6.0, t0=S[3], t1=S[4],
              look=(x[3], 1.0, -0.6), fov=40, aperture=0.025),
        dolly((x[4] + 0.3, 0.75, 7.6), (x[4] + 0.1, 0.95, 6.4), S[4], END, look=((x[4], 1.6, -2.0), (x[4], 2.6, -4.0)),
              fov=48, aperture=0.015, ease="smooth"),
    ]


LOOKS = dict(
    # deep, rich and warm: room for the light of the people (light only adds), never a pale wash
    cathedral=dict(base="dawn", sky_top="#0e1446", sky_mid="#3e2868", sky_hor="#c87a64", sun_color="#ffd8a0",
                   sun_int=0.65, sun_el=-2.5, sun_az=180.0, clouds=0.35, haze=0.5, haze_color="#6a3c62",
                   mist=0.15, mist_height=1.2, mist_color="#4a3260", hills=0.7, hill_color="#120c22",
                   water="#05040c", rays=0.45, dust=0.6, dust_color="#ffe0a8", dust_color2="#ffc0b0", bokeh=0.7,
                   stars=0.35, milky=0.1),
    embrace=dict(base="dusk", sky_top="#0c0e36", sky_mid="#3a2266", sky_hor="#c46a64", sun_color="#ffb890",
                 sun_int=0.55, sun_el=-3.0, sun_az=180.0, clouds=0.30, haze=0.55, haze_color="#6a3a64", mist=0.30,
                 mist_color="#4e3062", hills=0.8, hill_color="#0a0716", water="#030208", rays=0.3, stars=0.55,
                 milky=0.25, dust=0.6, dust_color="#ffd8a0", dust_color2="#ffb8c8", bokeh=0.7),
    prayer=dict(base="predawn", sky_top="#080e38", sky_mid="#28245e", sky_hor="#9a5a74", sun_color="#ffc0a0",
                sun_int=0.4, sun_el=-5.0, sun_az=200.0, stars=0.8, milky=0.4, clouds=0.2, haze=0.5,
                haze_color="#4a3a68", mist=0.35, mist_color="#3e3666", hills=0.7, hill_color="#0a0818",
                water="#03030a", dust=0.5, dust_color="#ffe6b8", dust_color2="#e8c8ff", bokeh=0.6),
    river=dict(base="dawn", sky_top="#101848", sky_mid="#4a2c6e", sky_hor="#e08a5e", sun_color="#ffd498",
               sun_int=0.8, sun_el=-1.5, sun_az=200.0, clouds=0.38, haze=0.55, haze_color="#8a4e66", mist=0.25,
               mist_color="#5a3a64", hills=0.7, hill_color="#100a1e", water="#04030a", rays=0.45, dust=0.5,
               stars=0.3, milky=0.1),
    aurora=dict(base="night", sky_top="#03061e", sky_mid="#141842", sky_hor="#5a3458", sun_color="#ffb090",
                sun_int=0.25, sun_el=-7.0, sun_az=180.0, stars=1.0, milky=0.5, clouds=0.10, haze=0.5,
                haze_color="#3a2a52", mist=0.3, mist_color="#30284e", hills=0.8, hill_color="#04030a",
                water="#020206", dust=0.5, dust_color="#ffe2a8", dust_color2="#ffc8e0", bokeh=0.6),
)

_SHAFT = "#ffe2a8"
P3D = dict(
    camera=Rig(_cams(), blend=0.0),
    world=dict(
        look=[(S[0], "cathedral", 0.0), (S[1], "embrace", 0.0), (S[2], "prayer", 0.0), (S[3], "river", 0.0),
              (S[4], "aurora", 0.0)],
        looks=LOOKS,
        shafts=[dict(base=(X[0] - 7.0, -16.0), radius=1.8, top=70.0, spread=0.25, color=_SHAFT, strength=_on(0, 0.55)),
                dict(base=(X[0] + 8.0, -22.0), radius=2.2, top=70.0, spread=0.25, color=_SHAFT, strength=_on(0, 0.5)),
                dict(base=(X[0] - 18.0, -42.0), radius=2.6, top=80.0, spread=0.3, color=_SHAFT, strength=_on(0, 0.42)),
                dict(base=(X[2] - 0.6, -3.0), radius=1.4, top=60.0, spread=0.35, color="#ffe8c0",
                     strength=_on(2, 0.55))],
        light=dict(pos=lambda t: (X[0] + 0.2, 3.4, -9.0) if t < S[1] else (X[1], 5.5, -14.0) if t < S[2] else
                   (X[2] - 0.6, 6.0, -5.0) if t < S[3] else (X[3] - 3.0, 4.5, -20.0) if t < S[4] else (X[4], 3.0, -40.0),
                   color="#ffe2b0", strength=lambda t: 0.10 if t < S[1] else 0.22 if t < S[4] else 0.10, size=0.8,
                   rays=1.0),
    ),
    setup=_setup,
)
