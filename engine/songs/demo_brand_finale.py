"""The world and the finale of demo_brand on their own: a 20 second proof (engine/UPGRADE-HOWTO.md, section Z).

   0.0 to  7.5   the world by day (demo_brand 40.0 to 47.5)
   7.5 to 20.0   the finale (demo_brand 47.5 to 60.0): the world of light at night with its hearts and arcs,
                 world to logo (13.0 to 15.0), the bloom into the pastel day (14.3), the logo into the end
                 card's place (15.0 to 16.4)
"""
import songs.s03_original as _base
from songs import demo_brand as _D  # noqa: E402  (it sets the base song up for 60 s; set again below)

O = -40.0          # these pieces play 40 s earlier than in demo_brand
TOTAL = 20.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 19.6
_base.SONG_END = 20.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d.camera import Rig  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
TOTAL = 20.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 19.6
SONG_END = 20.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

CAMERA = Rig(_D.world_moves(O), blend=1.5, handheld=0.12)
DAY_GLOBE, FINALE = _D.world_pieces(CAMERA, O)


def _setup(scene):
    scene.add("day globe", DAY_GLOBE)
    FINALE.add_to(scene)


_WORLD, _BURSTS = _D.world_p3d(CAMERA, FINALE, [(0.0, "day")], O)
P3D = dict(camera=CAMERA, world=_WORLD, setup=_setup, bursts=_BURSTS)
