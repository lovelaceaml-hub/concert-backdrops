"""Production registration for the fixed-camera movement proof."""
from functools import partial
from tools.fluid_dance.render import COLOR_CONTRACT, DURATION, FPS, SOURCE_START, CUTS
from tools.fluid_dance.render import fonts_path, source_hashes, frame, make_renderer as _make_renderer
make_renderer = partial(_make_renderer, mode="proof")
