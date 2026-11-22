"""Explicit registration of the complete advanced five-person performance."""
from functools import partial
from tools.advanced_dance.render import (COLOR_CONTRACT,DURATION,FPS,SOURCE_START,
    fonts_path,source_hashes,frame,make_renderer as _make_renderer,cut_times)

CUTS=cut_times("ensemble")
make_renderer=partial(_make_renderer,mode="ensemble")
