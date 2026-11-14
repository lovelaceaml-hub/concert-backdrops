"""Pipeline test only: the original song 03 timeline cut to 8 seconds so a full cloud video run is quick."""
import songs.s03_original as _base

_base.TOTAL = 8.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
from songs.s03_original import *  # noqa: E402,F401,F403
