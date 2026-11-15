"""Camera test, revolving (28.5 seconds, the 3D layer: engine/UPGRADE-HOWTO.md, section V).

Not a concert video: a test of the camera in the 3D world, set to 28.5 seconds of the song 01 promo clip
(audio/test/camera-test-28s.mp3). One unbroken move: skim low over the lake toward the arch, rise and revolve
a full turn round it while its nine lights wake on the beat, fly through it, crane up through rising
lanterns into the stars, then pull back wide as the sun comes up behind the arch. No words.
"""
import songs.s03_original as _base

_base.TOTAL = 28.5
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 28.2
_base.FADE = _base.Track([(0.0, 0.0), (0.7, 1.0), (27.3, 1.0), (28.45, 0.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (28.5, 1.0)])
for _p in _base.PHRASES:                       # no expressions in this test
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ", t0=1e9, t1=1e9 + 4.0)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d import StandIn  # noqa: E402
from p3d.camera import Rig, crane, dolly, orbit  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

# the clip's landmarks (seconds): a pulse of 0.488 s, new sections at 5.2, 15.67 and 19.57
BEAT = 0.488
T_ORBIT, T_THROUGH, T_CRANE, T_BACK = 5.2, 15.67, 19.57, 23.6
# the nine lights wake during the turn, from the two feet of the arch up to its crown, every second beat
_order = [0, 8, 1, 7, 2, 6, 3, 5, 4]
_LIT = [None] * 9
for _k, _i in enumerate(_order):
    _LIT[_i] = T_ORBIT + BEAT + _k * 2 * BEAT

CENTER = (0.0, 6.5, 0.0)
CAMERA = Rig([
    dolly((-7.0, 0.7, 168.0), (-5.0, 1.5, 44.0), 0.0, T_ORBIT, look=((0.0, 5.0, 0.0), (0.0, 7.0, 0.0)), fov=(52, 46),
          aperture=0.05, focus=(60.0, 40.0)),
    orbit(CENTER, radius=(34.0, 27.0), height=(2.2, 12.5), a0=-8.0, a1=352.0, t0=T_ORBIT, t1=T_THROUGH, fov=44,
          aperture=0.10, blend=2.8),
    dolly((-2.0, 10.5, 34.0), (0.0, 3.4, -36.0), T_THROUGH, T_CRANE, look="ahead", fov=(48, 58), aperture=0.08,
          focus=9.0, blend=2.0),
    crane((0.0, 3.4, -38.0), 48.0, T_CRANE, T_BACK, look=((0.0, 14.0, -120.0), (0.0, 110.0, -150.0)), fov=52,
          aperture=0.07, focus=(12.0, 60.0), blend=1.8),
    dolly((0.0, 46.0, -34.0), (0.0, 6.5, 84.0), T_BACK, 28.5, look=((0.0, 30.0, -200.0), (0.0, 7.5, 0.0)),
          fov=(50, 40), aperture=0.05, focus="target", ease="smooth", blend=1.6),
], handheld=0.25)


def _setup(scene):
    # stand-ins until the real bodies land: one figure under the crown of the arch, two further out
    scene.add("figure", StandIn(pos=(0.0, 0.0, 0.0), height=1.75, color="#ffe2b0"))
    scene.add("figure_l", StandIn(pos=(-4.2, 0.0, 3.0), height=1.68, color="#ffd0a0", facing=25.0, seed=8, n=16000))
    scene.add("figure_r", StandIn(pos=(4.6, 0.0, -2.5), height=1.72, color="#cfd8ff", facing=-30.0, seed=9, n=16000))


P3D = dict(
    camera=CAMERA,
    world=dict(
        look=[(0.0, "night"), (20.0, "predawn", 4.0), (23.8, "dawn", 3.0), (26.2, "sunrise", 3.0)],
        sun_az=180.0,
        lanterns=_base.Track([(0.0, 0.0), (13.5, 0.0), (17.5, 1.0), (28.5, 1.0)]),
        lantern_field=dict(count=520, radius=(5.0, 75.0), center=(0.0, -25.0), height=52.0),
        arch=dict(lit=_LIT),
        react=dict(beat=0.5, level=0.3),
    ),
    setup=_setup,
)
