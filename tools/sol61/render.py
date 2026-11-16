"""Render an exclusive global frame range with complete-picture moving dissolves."""
import argparse
import hashlib
import json
import os
import sys
import subprocess
import time
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'engine'))
os.environ.setdefault('SONG','sol61_peace')
os.environ.setdefault('OUT_FPS','60')
os.environ.setdefault('OUT_RES','1080p')
os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE','1')
import song as S
from songs import sol61_peace as film
from render import Renderer


def frame(r,i):
    t=i/S.FPS
    film.SHOT=film.shot_at(t)
    for j,c in enumerate(film.CUTS):
        if abs(t-c)<film.DISSOLVE/2:
            u=(t-c)/film.DISSOLVE+0.5
            u=u*u*(3-2*u)
            film.SHOT=j
            r.p3d._frame=None
            a=np.frombuffer(r.out.frame(t,i),np.uint8).astype(np.float32)
            film.SHOT=j+1
            r.p3d._frame=None
            b=np.frombuffer(r.out.frame(t,i),np.uint8).astype(np.float32)
            buf=np.rint(a*(1-u)+b*u).astype(np.uint8)
            break
    else:
        buf=np.frombuffer(r.out.frame(t,i),np.uint8)
    if t>54.95:
        u=film.film.sc(54.95,61.2,t)
        z=1+0.025*u
        im=Image.fromarray(buf.reshape(r.h,r.w,3))
        im=im.transform((r.w,r.h),Image.Transform.AFFINE,
                        (1/z,0,r.w*(1-1/z)/2,0,1/z,r.h*(1-1/z)/2),
                        resample=Image.Resampling.BICUBIC)
        buf=np.asarray(im).reshape(-1)
    # Release the whole picture into warm cream during the last musical resonance.
    if t>61.2:
        u=min((t-61.2)/0.65,1)
        u=u*u*(3-2*u)
        buf=np.rint(buf.reshape(-1,3)*(1-u)+np.array([255,245,232])*u).astype(np.uint8)
    return buf.tobytes()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--range',nargs=2,type=int,required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--scale',type=float,default=1)
    p.add_argument('--crf',default='16')
    a=p.parse_args()
    w,h=int(S.W*a.scale)//2*2,int(S.H*a.scale)//2*2
    r=Renderer(w,h)
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(S.FPS),'-i','-',
         '-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-threads','1','-preset','medium',
         '-crf',a.crf,'-pix_fmt','yuv420p','-g','60','-bf','2','-color_primaries','bt709',
         '-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',a.out]
    ff=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    start=time.time()
    f0,f1=a.range
    assert 0<=f0<f1<=S.NFRAMES
    hashes={}
    for i in range(f0,f1):
        raw=frame(r,i)
        if i<f0+2 or i>=f1-2:
            hashes[i]=hashlib.sha256(raw).hexdigest()
        ff.stdin.write(raw)
        if (i-f0)%120==0: print(f'frame {i}/{f1} elapsed {time.time()-start:.1f}s',flush=True)
    ff.stdin.close()
    if ff.wait(): raise RuntimeError('ffmpeg failed')
    Path(a.out).with_suffix('.hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(f'done {f1-f0} frames in {time.time()-start:.1f}s',flush=True)

if __name__=='__main__': main()
