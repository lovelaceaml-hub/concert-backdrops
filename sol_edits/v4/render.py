"""Render the faithful Film 10 upgrade at native 60 fps in exclusive ranges."""
import argparse,hashlib,json,resource,subprocess,sys,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sol_edits.v4.bootstrap import load
S,film=load()
from render import Renderer
import titles
_signature=titles.Titles._signature
def smaller_signature(self,corner,palette):
    old=self.s;self.s*=.60
    try:return _signature(self,corner,palette)
    finally:self.s=old
titles.Titles._signature=smaller_signature

def make_renderer(w,h):
    r=Renderer(w,h)
    from sol_edits.v4.surfaces import install
    install(r,film)
    font=ImageFont.truetype(str(ROOT/'fonts/outfit-latin-500-normal.ttf'),max(8,round(17*h/1080)))
    r.sol_labels=[]
    for color in ['#fff4de','#272751']:
        layer=Image.new('RGBA',(w,h));draw=ImageDraw.Draw(layer)
        draw.text((.965*w,.975*h),'GPT-6.1 SOL | NINE COLOURS',font=font,anchor='rs',fill=color)
        r.sol_labels.append(layer)
    return r

def frame(r,i):
    actual=i/S.FPS;t=max(0,actual-2)
    for cut in [19.85,26.79,33.36,40.21,49.47]:
        if abs(t-cut)<.2:
            u=(t-cut+.2)/.4;u=u*u*(3-2*u)
            r.p3d._frame=None
            a=np.frombuffer(r.out.frame(t-.205,i),np.uint8).astype(np.float32)
            r.p3d._frame=None
            b=np.frombuffer(r.out.frame(t+.205,i),np.uint8).astype(np.float32)
            raw=np.rint(a*(1-u)+b*u).astype(np.uint8)
            break
    else:raw=np.frombuffer(r.out.frame(t,i),np.uint8)
    im=Image.fromarray(raw.reshape(r.h,r.w,3)).convert('RGBA')
    im.alpha_composite(r.sol_labels[int(actual>53)])
    im=im.convert('RGB')
    if actual<2 or actual>54.6:
        z=1+.003*actual/2 if actual<2 else 1+.015*film.O._sc(54.6,61.9,actual)
        im=im.transform((r.w,r.h),Image.Transform.AFFINE,
            (1/z,0,r.w*(1-1/z)/2,0,1/z,r.h*(1-1/z)/2),resample=Image.Resampling.BICUBIC)
    data=im.tobytes();assert len(data)==r.w*r.h*3
    return data

def main():
    p=argparse.ArgumentParser();p.add_argument('--range',nargs=2,type=int)
    p.add_argument('--stills',default='');p.add_argument('--out',required=True)
    p.add_argument('--scale',type=float,default=1);p.add_argument('--step',type=int,default=1)
    a=p.parse_args();w=int(S.W*a.scale)//2*2;h=int(S.H*a.scale)//2*2;r=make_renderer(w,h)
    if a.stills:
        Path(a.out).mkdir(parents=True,exist_ok=True)
        for t in map(float,a.stills.split(',')):
            Image.frombytes('RGB',(w,h),frame(r,round(t*S.FPS))).save(Path(a.out)/f't{t:06.2f}.png')
            print('still',t,flush=True)
        return
    first,last=a.range;assert 0<=first<last<=S.NFRAMES
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}',
        '-r',str(S.FPS/a.step),'-i','-','-vf','scale=out_color_matrix=bt709:out_range=tv',
        '-c:v','libx264','-threads','1','-preset','medium','-crf','16','-pix_fmt','yuv420p',
        '-g','60','-bf','2','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
        '-color_range','tv','-movflags','+faststart',a.out],stdin=subprocess.PIPE)
    start=time.time();hashes={}
    for i in range(first,last,a.step):
        raw=frame(r,i)
        if i<first+2 or i>=last-2:hashes[i]=hashlib.sha256(raw).hexdigest()
        ff.stdin.write(raw)
        if (i-first)%120==0:print('frame',i,last,'elapsed',round(time.time()-start,1),flush=True)
    ff.stdin.close();assert ff.wait()==0
    me=resource.getrusage(resource.RUSAGE_SELF);children=resource.getrusage(resource.RUSAGE_CHILDREN)
    cost=dict(frames=len(range(first,last,a.step)),width=w,height=h,fps=S.FPS/a.step,
        loop_seconds=time.time()-start,cpu_seconds=me.ru_utime+me.ru_stime+children.ru_utime+children.ru_stime,
        peak_rss_kib=me.ru_maxrss)
    Path(a.out).with_suffix('.cost.json').write_text(json.dumps(cost,indent=2)+'\n')
    Path(a.out).with_suffix('.hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(cost,flush=True)
if __name__=='__main__':main()
