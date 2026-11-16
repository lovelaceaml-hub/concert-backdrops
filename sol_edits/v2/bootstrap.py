"""Load a song outside engine/songs without changing the shared song loader."""
import importlib.abc
import importlib.util
import importlib
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
NAME = 'sol_v2'

class SongFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'songs.' + NAME:
            return importlib.util.spec_from_file_location(fullname, Path(__file__).with_name('film.py'))
        return None


def load():
    sys.path.insert(0, str(ROOT / 'engine'))
    sys.meta_path.insert(0, SongFinder())
    os.environ['SONG'] = NAME
    os.environ.setdefault('OUT_FPS', '60')
    os.environ.setdefault('OUT_RES', '1080p')
    os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE', '1')
    song = importlib.import_module('song')
    return song, importlib.import_module('songs.' + NAME)
