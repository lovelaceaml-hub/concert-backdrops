"""Chooses which song the engine draws.

Set the environment variable SONG to the name of a file in engine/songs/ (without .py), for example
SONG=s05_god_bless_you. Without it the engine draws the original song 03 version (s03_original).
Everything that file defines (timeline, palettes, expressions, fragments, titles) becomes available as song.*.
The arch of nine lights (star_state, link_state) always comes from engine/arch.py so every song behaves the same.
"""
import importlib
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import arch as _arch  # noqa: E402

SONG_NAME = os.environ.get("SONG", "s03_original")
_m = importlib.import_module("songs." + SONG_NAME)
_m.star_state, _m.link_state = _arch.make(_m)   # params() in the song file looks these up at call time
if not hasattr(_m, "FRAGMENTS"):
    _m.FRAGMENTS = []
globals().update({k: v for k, v in vars(_m).items() if not k.startswith("__")})
