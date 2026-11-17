"""Render restored Nine Colours with a two-second quiet lead-in."""
from pathlib import Path
import importlib.util
import os
import runpy
import sys

ROOT=Path(__file__).resolve().parents[2]


def load():
    os.environ['SONG']='nine_colours_restored'
    os.environ.setdefault('FEATURES',str(ROOT/'work/nine_colours/features.npz'))
    os.environ.setdefault('OUT_FPS','60')
    os.environ.setdefault('OUT_RES','1080p')
    os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE','1')
    for key in ('LP_NUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):
        os.environ[key]='1'
    for key,folder in [('P3D_CACHE','p3d-cache'),('NUMBA_CACHE_DIR','numba'),('MESA_SHADER_CACHE_DIR','mesa-cache')]:
        os.environ.setdefault(key,str(ROOT/'work/nine_colours'/folder))
    sys.path[:0]=[str(ROOT/'engine'),str(ROOT)]
    spec=importlib.util.spec_from_file_location('songs.nine_colours_restored',Path(__file__).with_name('film.py'))
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    # Some body APIs import song while the adaptation is being constructed.
    # Publish the completed configuration before creating any renderer.
    import output
    import song
    output.apply(module)
    song.__dict__.update({k:v for k,v in vars(module).items() if not k.startswith('__')})
    import p3d.layer
    import titles

    class DelayedLayer(p3d.layer.Layer):
        """All original 3D times stay aligned with the unchanged music at +2 s."""
        def __init__(self,R):
            super().__init__(R)
            if self.audio is not None:
                source=self.audio
                class DelayedAudio:
                    def beat(self,t):return source.beat(t+2)
                    def level(self,t):return source.level(t+2)
                self.audio=DelayedAudio()

        def adjust(self,t,P):return super().adjust(t-2,P)
        def draw(self,t,P):return super().draw(t-2,P)
        def background(self,t,P):return super().background(t-2,P)

        def _draw_batch(self,e,bi,b,cam,share,paint,blur,mirror,mask_on,boxk,win):
            if e.name.startswith('passing reflection ') and not mirror:return
            if e.name.startswith(('word ','passing reflection ')):
                b=dict(b,clear=False)
            return super()._draw_batch(e,bi,b,cam,share,paint,blur,mirror,mask_on,boxk,win)

    class UpdatedTitles(titles.Titles):
        def _signature(self,corner,pal):
            scale=self.s
            try:
                self.s=scale*.65
                return super()._signature(corner,pal)
            finally:
                self.s=scale

        def overlay(self,t):
            drew=super().overlay(t)
            if not hasattr(self,'celebration'):
                self.celebration=module.Celebration()
            batch=self.celebration.points(t,self.w,self.h)
            if batch is not None:
                self.R.f_out.use()
                self.ctx.enable(self.mgl.BLEND)
                self.ctx.blend_func=(self.mgl.ONE,self.mgl.ONE_MINUS_SRC_ALPHA)
                self._points(batch)
                self.ctx.disable(self.mgl.BLEND)
                drew=True
            return drew

        def _op_points(self,t,front):
            if t>=7.1:return []
            return super()._op_points(t,front)

    p3d.layer.Layer=DelayedLayer
    titles.Titles=UpdatedTitles
    return module


if __name__=='__main__':
    load()
    runpy.run_path(str(ROOT/'engine/render.py'),run_name='__main__')
