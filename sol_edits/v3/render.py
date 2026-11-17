"""Render an exclusive global frame range with complete-picture moving dissolves."""
import argparse
import hashlib
import json
import os
import resource
import sys
import subprocess
import time
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sol_edits.v3.bootstrap import load
S,film=load()
from render import Renderer
from sol_edits.v3.phrases import Phrases,smaller_signature
smaller_signature()


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
    im=Image.fromarray(buf.reshape(r.h,r.w,3))
    im=r.sol_phrases.apply(im,t).convert('RGB')
    buf=np.asarray(im).reshape(-1)
    if t>54.95:
        u=film.film.sc(54.95,61.4,t)
        z=1+0.020*u
        im=Image.fromarray(buf.reshape(r.h,r.w,3))
        im=im.transform((r.w,r.h),Image.Transform.AFFINE,
                        (1/z,0,r.w*(1-1/z)/2,0,1/z,r.h*(1-1/z)/2),
                        resample=Image.Resampling.BICUBIC)
        buf=np.asarray(im).reshape(-1)
    assert buf.size==r.w*r.h*3,'Output must contain exactly one RGB frame'
    return buf.tobytes()


def make_renderer(w,h):
    r=Renderer(w,h)
    from sol_edits.v3.surfaces import install
    install(r,film)
    r.sol_phrases=Phrases(w,h,film)
    return r


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--range',nargs=2,type=int)
    p.add_argument('--stills',default='')
    p.add_argument('--out',required=True)
    p.add_argument('--scale',type=float,default=1)
    p.add_argument('--crf',default='16')
    p.add_argument('--step',type=int,default=1,help='Preview sampling only; master uses 1')
    a=p.parse_args()
    w,h=int(S.W*a.scale)//2*2,int(S.H*a.scale)//2*2
    r=make_renderer(w,h)
    if a.stills:
        Path(a.out).mkdir(parents=True,exist_ok=True)
        for t in map(float,a.stills.split(',')):
            raw=frame(r,round(t*S.FPS))
            Image.frombytes('RGB',(w,h),raw).save(Path(a.out)/f't{t:06.2f}.png')
            print('still',t,flush=True)
        return
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(S.FPS/a.step),'-i','-',
         '-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-threads','1','-preset','medium',
         '-crf',a.crf,'-pix_fmt','yuv420p','-g','60','-bf','2','-color_primaries','bt709',
         '-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',a.out]
    ff=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    start=time.time()
    f0,f1=a.range
    assert 0<=f0<f1<=S.NFRAMES
    hashes={}
    for i in range(f0,f1,a.step):
        raw=frame(r,i)
        if i<f0+2 or i>=f1-2:
            hashes[i]=hashlib.sha256(raw).hexdigest()
        ff.stdin.write(raw)
        if (i-f0)%60==0: print(f'frame {i}/{f1} elapsed {time.time()-start:.1f}s',flush=True)
    ff.stdin.close()
    if ff.wait(): raise RuntimeError('ffmpeg failed')
    Path(a.out).with_suffix('.hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    elapsed=time.time()-start
    usage=resource.getrusage(resource.RUSAGE_SELF)
    children=resource.getrusage(resource.RUSAGE_CHILDREN)
    cost=dict(frames=len(range(f0,f1,a.step)),width=w,height=h,fps=S.FPS/a.step,
              loop_seconds=elapsed,cpu_seconds=usage.ru_utime+usage.ru_stime+children.ru_utime+children.ru_stime,
              peak_rss_kib=usage.ru_maxrss)
    Path(a.out).with_suffix('.cost.json').write_text(json.dumps(cost,indent=2)+'\n')
    print(f'done {cost["frames"]} frames in {elapsed:.1f}s',flush=True)

if __name__=='__main__': main()
