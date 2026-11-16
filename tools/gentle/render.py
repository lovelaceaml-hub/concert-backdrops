"""Load the independent film without editing the shared songs directory."""
from pathlib import Path
import importlib.util
import os
import runpy
import sys

ROOT=Path(__file__).resolve().parents[2]


def load():
    # This entry point always selects this independent film, even in a shell
    # previously configured for another renderer. Feature overrides are useful
    # when reproducing an export in a separate private work directory.
    os.environ['SONG']='gentle_film'
    os.environ.setdefault('FEATURES',str(ROOT/'work/gentle/features.npz'))
    os.environ.setdefault('OUT_FPS','60')
    os.environ.setdefault('OUT_RES','1080p')
    os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE','1')
    for key in ('LP_NUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):
        os.environ[key]='1'
    os.environ.setdefault('P3D_CACHE',str(ROOT/'work/gentle/p3d-cache'))
    os.environ.setdefault('NUMBA_CACHE_DIR',str(ROOT/'work/gentle/numba'))
    os.environ.setdefault('MESA_SHADER_CACHE_DIR',str(ROOT/'work/gentle/mesa-cache'))
    sys.path.insert(0,str(ROOT/'engine'))
    spec=importlib.util.spec_from_file_location('songs.gentle_film',Path(__file__).with_name('film.py'))
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


if __name__=='__main__':
    load()
    runpy.run_path(str(ROOT/'engine/render.py'),run_name='__main__')
