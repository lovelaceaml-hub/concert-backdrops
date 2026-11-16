"""Run local software renders in exclusive ranges, concatenate, mux and encode a 60 fps review."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/sol61'


def run_part(bounds):
    a,b=bounds
    out=OUT/f'part-{a:04}-{b:04}.mp4'
    started=time.time()
    with (OUT/f'part-{a:04}-{b:04}.log').open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'tools/sol61/render.py'),'--range',str(a),str(b),
                        '--out',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    return dict(start=a,end=b,file=out.name,seconds=time.time()-started)


def command(args):
    subprocess.run(args,cwd=ROOT,check=True)


def main():
    sys.path.insert(0,str(ROOT/'engine'))
    import song as S
    assert S.FPS==60 and S.NFRAMES==3720
    step=S.NFRAMES//5
    bounds=[(i,min(i+step,S.NFRAMES)) for i in range(0,S.NFRAMES,step)]
    start=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        report=list(pool.map(run_part,bounds))
    (OUT/'render-cost.json').write_text(json.dumps(dict(parts=report,wall_seconds=time.time()-start),indent=2)+'\n')
    concat=OUT/'parts.txt'
    concat.write_text(''.join(f"file '{(OUT/r['file']).as_posix()}'\n" for r in report))
    command(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(OUT/'sol61-silent.mp4')])
    command(['ffmpeg','-v','error','-y','-i',str(OUT/'sol61-silent.mp4'),'-i',str(OUT/'sol61-medley.wav'),
             '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t','62',
             '-metadata','title=Concert comparison - GPT-6.1 Sol','-movflags','+faststart',str(OUT/'Sol61-Concert-1080p60.mp4')])
    command(['ffmpeg','-v','error','-y','-i',str(OUT/'Sol61-Concert-1080p60.mp4'),'-vf','scale=1280:720',
             '-c:v','libx264','-threads','2','-preset','medium','-crf','23','-pix_fmt','yuv420p','-fps_mode','passthrough',
             '-c:a','aac','-b:a','160k','-metadata','title=Concert review - GPT-6.1 Sol - 60 fps',
             '-movflags','+faststart',str(OUT/'Sol61-Concert-review-720p60.mp4')])
    print('finished',OUT,flush=True)

if __name__=='__main__':main()
