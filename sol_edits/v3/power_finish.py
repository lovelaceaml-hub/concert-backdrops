"""Finish the directed aerial flight and a grand concert cadence at real 60 fps."""
import argparse,json,math,resource,subprocess,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/sol3/power-finale'
BASE=ROOT/'work/sol3/nine-colors/Sol-V3-Nine-Colors-One-Love-1080p60.mp4'
START,END=2522,2693
ACCENT=60.418061
COLORS=['#ea5a5e','#f2b25e','#f6ce46','#5aba5a','#62b2fa','#667af6','#9e6af6','#ee62a6','#5872d2']


def smooth(a,b,t):
    u=float(np.clip((t-a)/(b-a),0,1));return u*u*(3-2*u)

class Crown:
    def __init__(self,w,h):
        self.w=w;self.h=h;self.s=h/1080
        yy,xx=np.mgrid[0:h,0:w];x=xx/w;y=yy/h
        # Preserve the exact logo and every line of the approved invitation.
        self.keep=np.ones((h,w),np.float32)
        for left,right,top,bottom in [(.115,.885,.208,.915),(.405,.595,.018,.205)]:
            distance=np.maximum.reduce([(left-x)*w,(x-right)*w,(top-y)*h,(y-bottom)*h])
            u=np.clip(distance/(70*self.s),0,1)
            self.keep*=u*u*(3-2*u)
    def apply(self,frame,t):
        rise=smooth(55.35,56.1,t)
        release=1-smooth(61.2,61.98,t)
        if rise*release<.001:return frame
        build=smooth(55.6,ACCENT,t)
        pulse=math.exp(-((t-ACCENT)/.23)**2)
        g=rise*release*(.32+.55*build+.35*pulse)
        layer=Image.new('RGBA',(self.w,self.h));d=ImageDraw.Draw(layer)
        for k,color in enumerate(COLORS):
            phase=2*math.pi*k/9+.85*(t-55.35)
            pts=[]
            for u in np.linspace(0,1,84):
                r=(.94*(1-u)+.165)*(1-.04*pulse)
                a=phase+1.25*u
                pts.append(((.5+math.sin(a)*r)*self.w,(.13+math.cos(a)*r*.73)*self.h))
            rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
            for j in range(len(pts)-1):
                u=(j+1)/len(pts);alpha=round(min(235,g*210*u*u))
                d.line((pts[j],pts[j+1]),fill=rgb+(alpha,),width=max(1,round((1+3*u)*self.s)))
            x,y=pts[-1];rad=(2+3*pulse)*self.s
            d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=(255,247,224,round(min(245,g*230))))
        glow=layer.filter(ImageFilter.GaussianBlur(12*self.s))
        glow.alpha_composite(layer)
        arr=np.array(glow);arr[:,:,3]=np.rint(arr[:,:,3]*self.keep).astype(np.uint8)
        picture=Image.fromarray(frame).convert('RGBA');picture.alpha_composite(Image.fromarray(arr))
        return np.asarray(picture.convert('RGB'))


def command(args):subprocess.run(args,check=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--still',type=float);p.add_argument('--input',type=Path)
    p.add_argument('--out',type=Path);a=p.parse_args()
    w,h,fps,n=1920,1080,60,3720;crown=Crown(w,h)
    if a.still is not None:
        frame=np.asarray(Image.open(a.input).convert('RGB'));Image.fromarray(crown.apply(frame,a.still)).save(a.out);return
    started=time.time()
    decoder=lambda path:subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',str(path),'-an',
        '-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    source=decoder(BASE);flight=decoder(OUT/'flight-graded-60.mp4')
    silent=OUT/'grand-finale-silent.mp4'
    encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}',
        '-r',str(fps),'-i','-','-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-threads','2',
        '-preset','medium','-crf','16','-pix_fmt','yuv420p','-g','60','-bf','2','-color_primaries','bt709',
        '-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE)
    count=0;replaced=0;size=w*h*3;edges={}
    import hashlib
    for i in range(n):
        raw=source.stdout.read(size);assert len(raw)==size,'Missing base frame'
        if START<=i<END:
            raw=flight.stdout.read(size);assert len(raw)==size,'Missing flight frame';replaced+=1
        if i in [START-2,START-1,START,START+1,END-2,END-1,END,END+1]:
            edges[i]=hashlib.sha256(raw).hexdigest()
        if i/fps>=55.35:
            frame=np.frombuffer(raw,np.uint8).reshape(h,w,3);raw=crown.apply(frame,i/fps).tobytes()
        encoder.stdin.write(raw);count+=1
        if i%240==0:print('finish',i,'elapsed',round(time.time()-started,1),flush=True)
    assert source.stdout.read(1)==b'' and flight.stdout.read(1)==b''
    source.stdout.close();flight.stdout.close();encoder.stdin.close()
    assert source.wait()==0 and flight.wait()==0 and encoder.wait()==0
    assert count==n and replaced==END-START
    (OUT/'patch-boundaries.json').write_text(json.dumps(edges,indent=2)+'\n')
    score=OUT/'concert-grand-finale.wav'
    master=OUT/'Sol-V3-Nine-Colors-Grand-Finale-1080p60.mp4'
    review=OUT/'Sol-V3-Nine-Colors-Grand-Finale-review-720p60.mp4'
    command(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(score),'-map','0:v:0','-map','1:a:0',
        '-c:v','copy','-c:a','aac','-b:a','320k','-t','62','-metadata','title=GPT-6.1 Sol - Nine Colors - Grand Finale',
        '-movflags','+faststart',str(master)])
    # A predictable phone download size, while keeping every one of the 60 fps frames.
    common=['ffmpeg','-v','error','-y','-i',str(master),'-i',str(score),'-map','0:v:0','-map','1:a:0',
        '-vf','scale=1280:720','-c:v','libx264','-threads','2','-preset','medium','-b:v','2800k','-pix_fmt','yuv420p',
        '-fps_mode','passthrough','-passlogfile',str(OUT/'review-pass')]
    command(common+['-pass','1','-an','-f','null','/dev/null'])
    command(common+['-pass','2','-c:a','aac','-b:a','160k','-t','62','-metadata',
        'title=GPT-6.1 Sol - Grand Finale - 60 fps review','-movflags','+faststart',str(review)])
    usage=resource.getrusage(resource.RUSAGE_SELF);children=resource.getrusage(resource.RUSAGE_CHILDREN)
    report=dict(frames=count,flight_frames=replaced,fps=fps,width=w,height=h,seconds=time.time()-started,
        cpu_seconds=usage.ru_utime+usage.ru_stime+children.ru_utime+children.ru_stime,
        master_bytes=master.stat().st_size,review_bytes=review.stat().st_size)
    (OUT/'power-finish-cost.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':main()
