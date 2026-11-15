"""The two approved looks of the people, crystal_light and gold_glitter (engine/p3d/styles.py; engine/UPGRADE-
HOWTO.md, section Y2), in five short heavenly tableaux on the sections of the concert medley
(audio/promo/concert-medley.mp3). A proof, not a concert video: no words. Every touching moment is between two
people of the same gender (Anthony's rule; a parent with a child is the one exception).

   0.00  a woman of crystal light opens her arms under god rays pouring through glowing clouds
   6.84  two women of gold walk to each other and embrace; light blooms from the embrace
  13.30  an elder of crystal sinks to her knees in prayer in a soft beam of falling light
  19.85  a woman of gold lifts a woman of crystal from her knees, by a river of light under glowing clouds
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
# each tableau has its own place on the lake (every set of it shows only in its own time); all well inside
# the shore (1400 m from the middle: beyond it the lake gives way to a plain)
X = [0.0, 220.0, -220.0, 440.0, -440.0]
S = SECTIONS


def win(k):
    return (S[k] - 0.02, (S[k + 1] if k < 4 else END + 1.0) + 0.02)


# ------------------------------------------------------------------------------------------------ the tableaux
def t1_cathedral(scene):
    """A woman of crystal light, arms opening, face lifting, under god rays pouring through glowing clouds;
    directly behind her the sky stays deep, so she glows."""
    x = X[0]
    ST.person(scene, "crystal_light", "c1", shape="woman", at=(x, 0.0), facing=0.0, garment="robe", hair="tied",
              show=win(0), fade=0.01, seed=3.0,
              gesture=[(0.6, 9.0, "open_arms", dict(lift=0.28, ease=2.2)),
                       (2.2, 9.0, "look_up", dict(amount=18.0, ease=2.0))])
    sun = (x - 150.0, 175.0, -330.0)
    scene.add("c1_clouds", K.CloudBank((x - 20.0, 98.0, -240.0), size=(380.0, 40.0, 80.0), billows=34, n=12000,
                                       light=sun, gaps=[(x - 95.0, -240.0)], gap=22.0, alpha=0.016, show=win(0)))
    scene.add("c1_rays", K.GodRays(sun, targets=[(x - 70.0 + 13.0 * i, -120.0 - 9.0 * (i % 3)) for i in range(9)],
                                   width=(4.0, 13.0), reach=1.0, sprites=520, motes=0, bright=1.5, shimmer=0.3,
                                   show=win(0), seed=5.0))
    scene.add("c1_motes", K.Sparkles((x, 1.6, -0.5), box=(2.5, 1.6, 2.0), n=420, stars=14, size=0.025,
                                     color="#fff2d0", color2="#ffd08a", bright=0.6, drift=0.05, show=win(0), seed=4.0))


def t2_embrace(scene):
    """Two women of gold walk to each other and hold each other, cheek past shoulder; light blooms between them."""
    x = X[1]
    t = S[1] + 2.4
    lt = (x, 4.4, 3.0)
    a, b = pairs.embrace(t, at=(x, 0.0), facing=90.0, approach=1.6, speed=0.7, ease=1.4,
                         a=ST.keys("gold_glitter", shape="woman", garment="dress", hair="bun", height=1.60,
                                   show=win(1), fade=0.01, seed=5.0, light=lt, bright=0.8, shed=500),
                         b=ST.keys("gold_glitter", shape="woman", garment="robe", hair="tied", height=1.66,
                                   build=0.95, show=win(1), fade=0.01, seed=6.0, light=lt, bright=0.8, shed=500,
                                   color="#f0a088", color2="#ffe6dc"))
    a.add(scene, "g2a")
    b.add(scene, "g2b")
    ST.dress(scene, "g2a", a, "gold_glitter", heart=0.4, bloom=0.0, trails=0.8)
    ST.dress(scene, "g2b", b, "gold_glitter", heart=0.4, bloom=0.0, trails=0.8, wind=(-0.18, 0.0, 0.10))

    def meet(tt):
        return 0.5 * (np.asarray(a.where(tt, "heart")) + np.asarray(b.where(tt, "heart")))
    scene.add("g2_bloom", K.Bloom(meet, t + 0.7, dur=4.5, radius=1.4, n=500, bright=0.3, seed=7.0))
    scene.add("g2_clouds", K.CloudBank((x - 170.0, 40.0, 0.0), size=(80.0, 30.0, 320.0), billows=30, n=12000,
                                       light=(x - 330.0, 30.0, -40.0), alpha=0.016, show=win(1), seed=3.0))
    return a, b


def t3_prayer(scene):
    """An elder of crystal sinks to her knees in prayer in a soft beam of light falling on her."""
    x = X[2]
    ST.person(scene, "crystal_light", "c3", shape="woman", height=1.56, stoop=0.3, build=1.05, at=(x, 0.0),
              facing=25.0, garment="robe", hair="covered", show=win(2), fade=0.01, seed=8.0,
              motion=[(S[2] - 1.0, "stand"), (S[2] + 0.6, "kneel", dict(dur=2.4, hands="pray", sit=0.2))],
              dress=dict(bloom=0.6))
    scene.add("c3_beam", K.GodRays((x - 5.0, 6.5, -4.5), targets=[(x - 0.1, 0.0, 0.1)], width=(0.5, 1.6),
                                   reach=1.0, tail=0.15, sprites=900, motes=500, bright=0.9, shimmer=0.15,
                                   show=win(2), seed=9.0))
    scene.add("c3_fall", K.Sparkles((x, 3.0, 0.0), box=(1.8, 3.0, 1.8), n=700, stars=40, size=0.03,
                                    color="#ffd890", color2="#ffb050", bright=0.8, drift=-0.25, show=win(2), seed=9.0))
    scene.add("c3_clouds", K.CloudBank((x, 60.0, -190.0), size=(320.0, 30.0, 70.0), billows=24, n=6000,
                                       light=(x, 120.0, -300.0), color="#ffd8a0", color2="#c878b0",
                                       alpha=0.010, reflect=False, show=win(2), seed=4.0))


def t4_lifted(scene):
    """A woman of gold reaches down and lifts a woman of crystal to her feet; a river of light flows behind."""
    x = X[3]
    t = S[3] + 2.6
    lt = (x, 4.2, 3.5)
    a, b = pairs.helped_up(t, at=(x, 0.0), facing=90.0, rise=2.0, reach=1.1,
                           a=ST.keys("gold_glitter", shape="woman", garment="dress", hair="bob", height=1.66,
                                     show=win(3), fade=0.01, seed=11.0, light=lt),
                           b=ST.keys("crystal_light", shape="woman", garment="tunic", hair="tied", height=1.58,
                                     show=win(3), fade=0.01, seed=12.0, light=lt))
    a.add(scene, "g4a")
    b.add(scene, "c4b")
    ST.dress(scene, "g4a", a, "gold_glitter")
    ST.dress(scene, "c4b", b, "crystal_light")
    path = [(x - 90.0, -160.0), (x - 45.0, -70.0), (x - 18.0, -24.0), (x - 4.0, -7.5), (x + 8.0, -5.5),
            (x + 22.0, -13.0), (x + 50.0, -40.0)]
    scene.add("r4_river", K.LightRiver(path, width=3.6, n=60000, speed=1.4, color="#ffc860", color2="#fff0d0",
                                       bright=1.0, show=win(3)))
    sun = (x - 170.0, 120.0, -340.0)
    scene.add("r4_clouds", K.CloudBank((x, 60.0, -220.0), size=(360.0, 36.0, 80.0), billows=32, n=12000,
                                       light=sun, gaps=[(x - 110.0, -240.0)], gap=22.0, alpha=0.016,
                                       show=win(3), seed=5.0))
    scene.add("r4_rays", K.GodRays(sun, targets=[(x - 90.0 + 14.0 * i, -130.0 - 8.0 * (i % 3)) for i in range(8)],
                                   width=(4.0, 12.0), reach=1.0, sprites=520, motes=0, bright=1.3,
                                   show=win(3), seed=6.0))
    return a, b


def t5_aurora(scene):
    """A man, a woman, a child and an elder, crystal and gold, raise lights that float up under an aurora."""
    x = X[4]
    t0 = S[4]
    people = [
        ("gold_glitter", "g5man", dict(shape="man", at=(x - 1.35, -0.2), facing=-12.0, garment="tunic",
                                        hair="short", build=1.1), 0.7),
        ("crystal_light", "c5woman", dict(shape="woman", at=(x - 0.42, 0.2), facing=-4.0, garment="dress",
                                           hair="tied"), 1.3),
        ("gold_glitter", "g5child", dict(shape="child", at=(x + 0.42, 0.4), facing=8.0, hair="bob"), 1.0),
        ("crystal_light", "c5elder", dict(shape="man", height=1.68, stoop=0.35, at=(x + 1.35, -0.1), facing=14.0,
                                          garment="coat"), 1.6),
    ]
    for k, (style, name, kw, lag) in enumerate(people):
        up = t0 + lag
        g = [(t0 - 1.0, 40.0, "cup", dict(ease=0.6)),
             (up, 40.0, "raise_hand", dict(side="R", ease=1.1)),
             (up + 0.4, 40.0, "look_up", dict(amount=22.0, ease=1.4))]
        st = ST.person(scene, style, name, show=win(4), fade=0.01, seed=20.0 + k, gesture=g,
                       dress=dict(motes=0.6, trails=0.7, bloom=0.5), **kw)
        scene.add(name + "_light", K.HandLight(st.main, "palm.R", born=t0 - 0.5, release=up + 1.7 + 0.25 * k,
                                               rise=0.55, seed=30.0 + k))
    scene.add("a5_aurora", K.Aurora(center=(x, -520.0), span=1500.0, height=(110.0, 420.0), curtains=3, rays=1500,
                                    folds=90.0, bright=1.0, show=win(4)))
    scene.add("a5_lanterns", K.Sparkles((x, 7.0, -14.0), box=(16.0, 6.0, 10.0), n=500, stars=24, size=0.08,
                                        color="#ffe2a8", color2="#ffb070", bright=0.6, drift=0.25, show=win(4),
                                        seed=12.0))


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
        # low, slowly sweeping round her: she fills most of the height against the deep sky
        orbit((x[0], 1.0, 0.0), radius=(3.3, 2.6), height=(0.75, 0.95), a0=-24.0, a1=12.0, t0=S[0], t1=S[1],
              look=lambda t: (x[0], 1.12 + 0.03 * (t - S[0]), 0.0), fov=40, aperture=0.02),
        # half figures: the two women in profile, the camera turning slowly round them
        orbit((x[1], 1.2, 0.0), radius=(3.8, 2.3), height=(1.30, 1.45), a0=34.0, a1=90.0, t0=S[1], t1=S[2],
              look=(x[1], 1.28, 0.0), fov=38, aperture=0.02),
        # three quarters from the front, close: she kneels into the frame
        orbit((x[2], 0.8, 0.0), radius=(2.6, 2.1), height=(1.35, 1.0), a0=40.0, a1=62.0, t0=S[2], t1=S[3],
              look=lambda t: (x[2], 1.05 - 0.04 * (t - S[2]), 0.0), fov=40, aperture=0.02),
        orbit((x[3], 1.0, 0.0), radius=(3.4, 2.8), height=(1.05, 1.15), a0=-16.0, a1=10.0, t0=S[3], t1=S[4],
              look=(x[3], 0.95, -0.3), fov=40, aperture=0.008),
        dolly((x[4] + 0.3, 0.55, 5.0), (x[4] + 0.05, 0.75, 4.2), S[4], END, look=((x[4], 1.55, -1.5), (x[4], 2.2, -3.0)),
              fov=46, aperture=0.012, ease="smooth"),
    ]


LOOKS = dict(
    # deep, rich and warm: room for the light of the people (light only adds), never a pale wash
    cathedral=dict(base="dawn", sky_top="#070a30", sky_mid="#24185a", sky_hor="#9a5068", sun_color="#ffd8a0",
                   sun_int=0.5, sun_el=-4.0, sun_az=180.0, clouds=0.12, haze=0.45, haze_color="#4a2c58",
                   mist=0.10, mist_height=1.0, mist_color="#3a2856", hills=0.6, hill_color="#0c0818",
                   water="#04030a", rays=0.0, dust=0.5, dust_color="#ffe0a8", dust_color2="#ffc0b0", bokeh=0.5,
                   stars=0.6, milky=0.2),
    embrace=dict(base="dusk", sky_top="#0c0e36", sky_mid="#3a2266", sky_hor="#c46a64", sun_color="#ffb890",
                 sun_int=0.55, sun_el=-3.0, sun_az=270.0, clouds=0.15, haze=0.55, haze_color="#6a3a64", mist=0.25,
                 mist_color="#4e3062", hills=0.8, hill_color="#0a0716", water="#030208", rays=0.0, stars=0.55,
                 milky=0.25, dust=0.5, dust_color="#ffd8a0", dust_color2="#ffb8c8", bokeh=0.6),
    prayer=dict(base="predawn", sky_top="#080e38", sky_mid="#28245e", sky_hor="#9a5a74", sun_color="#ffc0a0",
                sun_int=0.35, sun_el=-5.0, sun_az=200.0, stars=0.8, milky=0.4, clouds=0.1, haze=0.5,
                haze_color="#4a3a68", mist=0.2, mist_color="#3e3666", hills=0.7, hill_color="#0a0818",
                water="#03030a", dust=0.4, dust_color="#ffe6b8", dust_color2="#e8c8ff", bokeh=0.5),
    river=dict(base="dawn", sky_top="#101848", sky_mid="#40286a", sky_hor="#c87068", sun_color="#ffd498",
               sun_int=0.7, sun_el=-1.5, sun_az=200.0, clouds=0.15, haze=0.55, haze_color="#8a4e66", mist=0.2,
               mist_color="#5a3a64", hills=0.7, hill_color="#100a1e", water="#04030a", rays=0.2, dust=0.4,
               stars=0.3, milky=0.1),
    aurora=dict(base="night", sky_top="#03061e", sky_mid="#141842", sky_hor="#5a3458", sun_color="#ffb090",
                sun_int=0.25, sun_el=-7.0, sun_az=180.0, stars=1.0, milky=0.5, clouds=0.05, haze=0.5,
                haze_color="#3a2a52", mist=0.25, mist_color="#30284e", hills=0.8, hill_color="#04030a",
                water="#020206", dust=0.4, dust_color="#ffe2a8", dust_color2="#ffc8e0", bokeh=0.5),
)

P3D = dict(
    camera=Rig(_cams(), blend=0.0),
    world=dict(
        look=[(S[0], "cathedral", 0.0), (S[1], "embrace", 0.0), (S[2], "prayer", 0.0), (S[3], "river", 0.0),
              (S[4], "aurora", 0.0)],
        looks=LOOKS,
        # a star of light high above the embrace only (the other tableaux have their god rays)
        light=dict(pos=(X[1] - 16.0, 7.0, -2.0), color="#ffe2b0", strength=lambda t: 0.18 if S[1] <= t < S[2] else 0.0,
                   size=0.8, rays=1.0),
    ),
    setup=_setup,
)
