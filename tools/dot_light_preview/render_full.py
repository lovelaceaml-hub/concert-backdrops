"""Render only local isolated outputs, never GitHub Actions."""
import os,sys,types,importlib.util,json,time,subprocess,argparse
from pathlib import Path
ROOT=Path(os.environ.get('DOT_ENGINE_ROOT',str(Path(__file__).resolve().parents[2])))
OUT=Path(os.environ.get('DOT_PREVIEW_OUT',str(ROOT/'work/dot-light-full')));OUT.mkdir(parents=True,exist_ok=True)
os.chdir(ROOT)
os.environ.update(SONG='dot_full',OUT_FPS='60',FEATURES=os.environ.get('FEATURES',str(ROOT/'work/master_peace/features.npz')),
    LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MESA_SHADER_CACHE_DIR=str(OUT/'mesa'),NUMBA_CACHE_DIR=str(OUT/'numba'))
sys.path.insert(0,str(ROOT/'engine'))
spec=importlib.util.spec_from_file_location('songs.dot_full',Path(__file__).with_name('film.py'));m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
import render
p=argparse.ArgumentParser();p.add_argument('--stills');p.add_argument('--range',nargs=2,type=int,default=[0,3720]);p.add_argument('--name',default='part');a=p.parse_args()
R=render.Renderer(960,540)
def frame(t,i):
    raw=R.out.frame(t,i)
    if t>=55:
        from PIL import Image
        scale=1+.008*float(m.smooth(55,61,t))
        image=Image.frombytes('RGB',(960,540),raw)
        w,h=960/scale,540/scale
        image=image.transform((960,540),Image.Transform.EXTENT,((960-w)/2,(540-h)/2,(960+w)/2,(540+h)/2),Image.Resampling.BICUBIC)
        return image.tobytes()
    return raw
if a.stills:
    from PIL import Image
    for t in map(float,a.stills.split(',')):
        raw=frame(t,round(t*60));Image.frombytes('RGB',(960,540),raw).save(OUT/f't{t:.2f}.png')
else:
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','960x540','-r','60','-i','-','-c:v','libx264','-threads','1','-preset','fast','-crf','20','-pix_fmt','yuv420p',str(OUT/(a.name+'.mp4'))],stdin=subprocess.PIPE)
    st=time.monotonic()
    for i in range(*a.range):
        ff.stdin.write(frame(i/60,i))
        if i%120==0:print(i,round(time.monotonic()-st,2),flush=True)
    ff.stdin.close()
    if ff.wait():raise RuntimeError('encode failed')
    (OUT/(a.name+'.json')).write_text(json.dumps(dict(first=a.range[0],last=a.range[1],seconds=time.monotonic()-st)))
