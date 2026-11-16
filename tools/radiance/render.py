"""Load The Light That Reaches You without editing shared song files."""
from pathlib import Path
import importlib.util
import os
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]


def load():
    os.environ['SONG'] = 'radiance_film'
    os.environ.setdefault('FEATURES', str(ROOT/'work/radiance/features.npz'))
    os.environ.setdefault('OUT_FPS', '60')
    os.environ.setdefault('OUT_RES', '1080p')
    os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE', '1')
    for name in ('LP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS'):
        os.environ[name] = '1'
    for name, folder in [('P3D_CACHE','p3d-cache'), ('NUMBA_CACHE_DIR','numba'),
                         ('MESA_SHADER_CACHE_DIR','mesa-cache')]:
        os.environ.setdefault(name, str(ROOT/'work/radiance'/folder))
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT/'engine'))
    spec = importlib.util.spec_from_file_location('songs.radiance_film', Path(__file__).with_name('film.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    import titles

    class RadianceTitles(titles.Titles):
        def _op_points(self, t, front):
            if t >= 8.1:
                return []
            amount = 1-float(module.smooth(7, 8.1, t))
            return [((xy, size, rgba*amount), additive)
                    for (xy, size, rgba), additive in super()._op_points(t, front)]

    titles.Titles = RadianceTitles
    return module


if __name__ == '__main__':
    load()
    runpy.run_path(str(ROOT/'engine/render.py'), run_name='__main__')
