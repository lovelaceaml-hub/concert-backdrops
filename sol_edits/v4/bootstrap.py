"""Load the faithful Nine Colours upgrade outside the protected song directory."""
import importlib,importlib.abc,importlib.util,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Finder(importlib.abc.MetaPathFinder):
    def find_spec(self,name,path=None,target=None):
        if name=='songs.sol_v4':
            return importlib.util.spec_from_file_location(name,Path(__file__).with_name('film.py'))
def load():
    sys.path.insert(0,str(ROOT/'engine'));sys.meta_path.insert(0,Finder())
    os.environ.update(SONG='sol_v4',OUT_FPS='60',OUT_RES='1080p',LIBGL_ALWAYS_SOFTWARE='1')
    return importlib.import_module('song'),importlib.import_module('songs.sol_v4')
