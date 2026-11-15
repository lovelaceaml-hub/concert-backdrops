"""Sky and camera demo (30 seconds, to the first minute of the song 03 New Song recording): night to dawn with
god rays through moving clouds and a slow crane up (engine/UPGRADE-HOWTO.md, section I7).

Not a concert video. The song 03 original look and its first two expressions, with the new keys on top:
TIME_OF_DAY from night to just after dawn, CLOUDS3D, GOD_RAYS from the rising sun, and a camera that cranes up,
pushes in a little and drifts sideways while the sky, the clouds, the three ranges, the lake and the near motes
move at their own depths. The words stay where they are.
"""
import songs.s03_original as _base

_base.TOTAL = 30.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 29.5   # the skyline is the loudness of this cut, not the whole song
_base.RIDGE_X0, _base.RIDGE_W = 0.02, 1.0   # and reaches past the right edge, so the camera never shows its end
_base.FADE = _base.Track([(0, 0.0), (1.0, 1.0), (28.5, 1.0), (29.9, 0.0)])
from songs.s03_original import *  # noqa: E402,F401,F403
from track import Track  # noqa: E402

TIME_OF_DAY = Track([(0.0, 0.02), (4.0, 0.06), (20.0, 0.48), (30.0, 0.66)])
CLOUDS3D = Track([(0.0, 0.75), (30.0, 0.85)])
CLOUDS_SPEED = 1.6
CLOUDS_LIGHT = 1.1
GOD_RAYS = Track([(0.0, 0.0), (8.0, 0.0), (16.0, 1.0), (30.0, 1.15)])
RAYS_DECAY = 0.99
TEXT_SHADOW = 0.0
FIGURES = [
    dict(poses=["assets/figures/greeting_a.png", "assets/figures/greeting_b.png"], pose_times=[15.0], t0=3.0,
         t1=28.0, x=0.74, y=0.19, height=0.28, leave="drift"),   # moves with the camera (CAMERA_LIGHT_DEPTH)
]
CAMERA_CRANE = Track([(0.0, -0.03), (30.0, 0.09)])
CAMERA_ZOOM = Track([(0.0, 1.0), (30.0, 1.07)])
CAMERA_PAN = Track([(0.0, -0.015), (30.0, 0.02)])
PARALLAX = 1.0
CAMERA_MOTES = 0.6
BOTTOM_CALM = 1.0
