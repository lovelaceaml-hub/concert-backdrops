"""Dot concept: The Light We Share. Eight-second opening study, not final film.
Uses the existing engine and approved brand lockup; the light garden is new.
Soundtrack is a reused excerpt, not a new seven-song edit.
"""
import os, sys, types, subprocess, time, json, hashlib
from pathlib import Path
import numpy as np
ROOT=Path(os.environ.get('DOT_ENGINE_ROOT', str(Path(__file__).resolve().parents[2])))
OUT=Path(os.environ.get('DOT_PREVIEW_OUT', str(ROOT/'work/dot-light-preview')))
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(ROOT)
os.environ.update(SONG='dot_preview', OUT_FPS='60', FEATURES=os.environ.get('FEATURES',str(ROOT/'work/master_peace/features.npz')),
    LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
    XDG_CACHE_HOME=str(OUT/'cache'), NUMBA_CACHE_DIR=str(OUT/'numba'),
    MESA_SHADER_CACHE_DIR=str(OUT/'mesa'))
sys.path.insert(0,str(ROOT/'engine'))
from songs import demo_titles as base
from p3d.camera import Rig, hold
from p3d import lin
from track import Track
module=types.ModuleType('songs.dot_preview')
module.__dict__.update({k:v for k,v in vars(base).items() if not k.startswith('__')})
module.TOTAL=8.0; module.NFRAMES=480; module.FPS=60
module.FADE=Track([(0,1),(8,1)])
module.EXPOSURE=Track([(0,1),(8,1)])
module.TITLES=dict(opening=dict(t_end=10, dissolve=1, y=.32, palette='day'),logo=None)
class LightGarden:
    def __init__(self):
        self.u=np.linspace(0,1,500)
    def sample(self,t):
        out=[]
        for i in range(9):
            a=i*2*np.pi/9
            u=self.u
            bloom=.84+.07*np.sin(t*.35)
            radius=3.5*np.sin(np.pi*u)*bloom
            # Arcs unfurl above the water, below the brand lockup.
            p=np.stack([radius*np.cos(a),.12+1.05*np.sin(np.pi*u)**2,
                        -2+radius*np.sin(a)],1)
            out.append(dict(pos=p, size=.019, color=lin(['#e9a04b','#f8c768','#dfaf78'][i%3]),
                            alpha=.55+.12*np.sin(u*9-t*.6+i),emit=.65,kind='soft',reflect=True))
        u=self.u
        angle=2*np.pi*u
        r=4.2+.12*np.sin(t*.28)
        out.append(dict(pos=np.stack([r*np.cos(angle),np.full_like(u,.05),-2+r*np.sin(angle)],1),
                        size=.027,color=lin('#f4b567'),alpha=.55,emit=.6,kind='soft'))
        return out

def setup(scene):scene.add('nine petals of light',LightGarden())
module.P3D=dict(camera=Rig([hold((0,3.8,12),(0,3.0,-2),0,8,drift=(.2,.04,-.12))],
                           fov=42,handheld=0,aperture=.015),
                world=dict(look='cream',arch=None,clouds=.4,stars=0,dust=.05,bokeh=.02,
                           sun_int=.4,sun_disc=0,rays=.15,water='#f6d9bb',mirror=.45),setup=setup)
sys.modules['songs.dot_preview']=module
import render
R=render.Renderer(960,540)
path=OUT/'The-Light-We-Share-silent.mp4'
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','960x540',
                     '-r','60','-i','-','-c:v','libx264','-threads','2','-preset','fast','-crf','20',
                     '-pix_fmt','yuv420p',str(path)],stdin=subprocess.PIPE)
start=time.monotonic()
for i in range(480):
    raw=R.out.frame(i/60,i)
    ff.stdin.write(raw)
    if i in (0,240,479):
        from PIL import Image
        Image.frombytes('RGB',(960,540),raw).save(OUT/f'frame-{i}.png')
    if i%60==0:print(i,round(time.monotonic()-start,2),flush=True)
ff.stdin.close()
if ff.wait():raise RuntimeError('encode failed')
(OUT/'render-metrics.json').write_text(json.dumps(dict(frames=480,fps=60,width=960,height=540,
    wall_seconds=time.monotonic()-start,concept='The Light We Share',
    limitation='Eight-second opening design study; not the full62-second film. Existing soundtrack excerpt reused.'),indent=2))
