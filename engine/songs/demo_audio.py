"""Music reactivity demo (engine-audio): the original song 03 look over the first 60 seconds of the New Song
recording (audio/test/s03-newsong-first-60s.mp3), with every REACT_* key on at full amount so the motion can be
judged. Not a concert video.

What to look for: the sky glow and the aurora swell slowly with the music (at most +25 percent), small warm
sparkles breathe on each beat (half time, about 78 bpm), the lit arch lights pulse gently on the beat, and the
bloom opens a little in the loud sections (about 26 to 34 s and from 44 s). Nothing should flash or strobe.
"""
import songs.s03_original as _base
from track import Track
from audio_react import audio

_base.TOTAL = 60.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 59.5   # the clip ends here: the skyline and the travelling lantern follow the clip, not the full song
# an aurora from the start (the full song only opens it at the first chorus), so its reaction shows in the minute
_base.AURORA = Track([(0, 0.0), (8, 0.0), (18, 0.30), (40, 0.40), (60, 0.46)])
_base.FADE = Track([(0, 0.0), (1.0, 1.0), (58.6, 1.0), (59.9, 0.0)])
# a helper inside a timeline: soft rays that open with the loud sections
_rays = _base.RAYS
_base.RAYS = lambda t: _rays(t) + 0.30 * audio.chorus(t)

from songs.s03_original import *  # noqa: E402,F401,F403

BOTTOM_CALM = 1.0
AUDIO_REACT = 1.0
REACT_GLOW = 1.0
REACT_SPARKLE = 1.0
REACT_ARCH = 1.0
REACT_AURORA = 1.0
REACT_CHORUS = 1.0
