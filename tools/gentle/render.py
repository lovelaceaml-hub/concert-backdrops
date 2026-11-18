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
    import titles

    class GentleTitles(titles.Titles):
        """Let the opening's dust settle before the first reading moment.

        This process-local adapter changes no shared title implementation.
        The full opening still holds through seven seconds.
        """
        def _op_points(self,t,front):
            if t>=8.0:
                return []
            amount=float(1-module.smooth(7.0,8.0,t))
            return [((xy,size,rgba*amount),additive)
                    for (xy,size,rgba),additive in super()._op_points(t,front)]

    titles.Titles=GentleTitles
    return module


if __name__=='__main__':
    load()
    runpy.run_path(str(ROOT/'engine/render.py'),run_name='__main__')
