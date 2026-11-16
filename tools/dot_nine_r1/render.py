"""Render the original choreography at 60 fps, delayed two seconds for music."""
import os
import pathlib
import sys
import importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'engine'))
sys.path.insert(0,str(pathlib.Path(__file__).parent))
os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE','1')
os.environ.setdefault('MESA_SHADER_CACHE_DIR',str(ROOT/'work/dot_nine_r1/mesa'))
os.environ.setdefault('NUMBA_CACHE_DIR',str(ROOT/'work/dot_nine_r1/numba'))
os.environ.setdefault('FEATURES',str(ROOT/'work/dot_nine_r1/features.npz'))
os.environ['OUT_FPS']='60'
os.environ['SONG']='dot_nine_r1'
import film
sys.modules['songs.dot_nine_r1']=film
spec=importlib.util.spec_from_file_location('render',ROOT/'engine/render.py')
engine_render=importlib.util.module_from_spec(spec)
sys.modules['render']=engine_render
spec.loader.exec_module(engine_render)

class ClockTitles:
    def __init__(self,inner): self.inner=inner; self.now=0.0
    def __getattr__(self,name): return getattr(self.inner,name)
    def protect(self,t): return self.inner.protect(self.now)
    def overlay(self,t): return self.inner.overlay(self.now)

BaseRenderer=engine_render.Renderer
class Renderer(BaseRenderer):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.titles=ClockTitles(self.titles)
    def frame(self,t,index=0):
        self.titles.now=t
        return super().frame(max(0.0,t-2.0),index)
engine_render.Renderer=Renderer
if __name__=='__main__': engine_render.main()
