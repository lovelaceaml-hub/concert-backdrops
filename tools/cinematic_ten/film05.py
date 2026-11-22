"""Explicit production registration for cinematic film 05."""
from functools import partial
from tools.cinematic_ten.render import (COLOR_CONTRACT, DURATION, FPS, SOURCE_START,
    fonts_path, source_hashes as _source_hashes, frame, make_renderer as _make_renderer)

CUTS = ()
make_renderer = partial(_make_renderer, film_id=5)
source_hashes = partial(_source_hashes, film_id=5)
