"""A restrained photographic gold grade, isolated by the actual animated bodies."""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sol_edits.v3.bootstrap import load
S,film=load()
from render import Renderer
from sol_edits.v3.surfaces import Surfaces,VERT

MASK='''#version 330
in vec3 world;in vec3 normal;
uniform vec3 eye,tint;uniform float coverage;
out vec4 frag;
void main(){float a=coverage+1e-20*(eye.x+tint.x+world.x+normal.x);frag=vec4(a,a,a,a);}
'''

class Empty:
    def draw(self,*args):pass
    def shadows(self,*args):pass
    def petals(self,*args):return np.empty((0,3)),np.empty((0,3)),np.empty((0,3),int)

class BodyMask(Surfaces):
    def __init__(self,r):
        super().__init__(r,film)
        self.environments=Empty();self.atmosphere=Empty()
        self.prog=self.ctx.program(vertex_shader=VERT,fragment_shader=MASK)
        self.vao=self.ctx.vertex_array(self.prog,[(self.buf,'3f 3f','in_pos','in_normal')])
    def sample(self,t,j):
        self.fbo.use();self.fbo.clear(0,0,0,0,depth=1)
        film.SHOT=j
        if 8<t<43:super().draw(t,dict(exposure=1))
        raw=self.fbo.read(components=4,alignment=1,dtype='f1')
        return np.frombuffer(raw,np.uint8).reshape(self.R.h,self.R.w,4)[::-1,:,3].copy()/255.
    def at(self,t):
        for j,c in enumerate(film.CUTS):
            if abs(t-c)<film.DISSOLVE/2:
                u=(t-c)/film.DISSOLVE+.5;u=u*u*(3-2*u)
                return self.sample(t,j)*(1-u)+self.sample(t,j+1)*u
        return self.sample(t,film.shot_at(t))


def grade(frame,mask):
    # Preserve the scene and point highlights while giving pale gold real depth.
    x=frame.astype(np.float32)/255
    gold=x*np.array([.96,.84,.67],np.float32)
    gold=np.clip((gold-.5)*1.10+.5,0,1)
    m=np.clip(mask*.88,0,1)[...,None]
    return np.rint(np.clip(x*(1-m)+gold*m,0,1)*255).astype(np.uint8)


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--still',type=float);a=p.parse_args()
    r=Renderer(S.W,S.H);mask=BodyMask(r)
    if a.still is not None:
        frame=np.asarray(Image.open(a.input).convert('RGB'))
        Image.fromarray(grade(frame,mask.at(a.still))).save(a.out);return
    decoder=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',str(a.input),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{S.W}x{S.H}',
        '-r',str(S.FPS),'-i','-','-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-threads','1',
        '-preset','medium','-crf','16','-pix_fmt','yuv420p','-g','60','-bf','2','-color_primaries','bt709',
        '-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(a.out)],stdin=subprocess.PIPE)
    start=time.time();nbytes=S.W*S.H*3
    for i in range(S.NFRAMES):
        raw=decoder.stdout.read(nbytes)
        assert len(raw)==nbytes,'Missing source frame in the photographic finish'
        x=np.frombuffer(raw,np.uint8).reshape(S.H,S.W,3)
        y=grade(x,mask.at(i/S.FPS)) if 8<i/S.FPS<43 else x
        encoder.stdin.write(y.tobytes())
        if i%120==0:print('grade',i,'elapsed',round(time.time()-start,1),flush=True)
    assert decoder.stdout.read(1)==b'','Unexpected extra source frame'
    decoder.stdout.close();encoder.stdin.close()
    assert decoder.wait()==0 and encoder.wait()==0
    usage=resource.getrusage(resource.RUSAGE_SELF);children=resource.getrusage(resource.RUSAGE_CHILDREN)
    a.out.with_suffix('.cost.json').write_text(json.dumps(dict(frames=S.NFRAMES,seconds=time.time()-start,
        cpu_seconds=usage.ru_utime+usage.ru_stime+children.ru_utime+children.ru_stime),indent=2)+'\n')

if __name__=='__main__':main()
