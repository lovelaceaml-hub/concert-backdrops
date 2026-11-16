"""Local, restartable 720p60 export. No workflow dispatch or network calls."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'work/dot_nine_r1'
WORK.mkdir(parents=True,exist_ok=True)
ENV=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',LP_NUM_THREADS='2')

def valid(path, frames):
    try:
        data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
            '-show_entries','stream=nb_frames,width,height,r_frame_rate','-of','json',str(path)],stderr=subprocess.DEVNULL))['streams'][0]
        return int(data['nb_frames'])==frames and data['width']==1280 and data['height']==720 and data['r_frame_rate']=='60/1'
    except (subprocess.CalledProcessError,ValueError,KeyError,IndexError):
        return False

def chunk(pair):
    start,end=pair
    path=WORK/f'part-{start:04d}-{end:04d}.mp4'
    if valid(path,end-start):
        print('verified existing',path.name,flush=True)
        return path
    partial=path.with_suffix('.partial.mp4')
    with (WORK/f'part-{start:04d}.log').open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'tools/dot_nine_r1/render.py'),'--range',str(start),str(end),
            '--scale','0.666666667','--preset','fast','--out',str(partial)],cwd=ROOT,env=ENV,
            stdout=log,stderr=subprocess.STDOUT,check=True)
    if not valid(partial,end-start): raise RuntimeError('Incomplete chunk '+str(start))
    partial.replace(path)
    print('complete',path.name,flush=True)
    return path

if __name__=='__main__':
    spans=[(i,min(i+620,3720)) for i in range(0,3720,620)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        paths=list(pool.map(chunk,spans))
    listing=WORK/'concat.txt'
    listing.write_text(''.join("file '"+str(p)+"'\n" for p in paths))
    out=WORK/'nine-colours-r1-dot.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),
        '-i',str(WORK/'score.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k',
        '-t','62','-movflags','+faststart',str(out)],check=True)
    if not valid(out,3720): raise RuntimeError('Final verification failed')
    subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
    print('VERIFIED',out,flush=True)
