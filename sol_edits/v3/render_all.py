"""Run local software renders in exclusive ranges, concatenate, mux and encode a 60 fps review."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/sol3'


def run_part(bounds):
    a,b=bounds
    out=OUT/f'part-{a:04}-{b:04}.mp4'
    started=time.time()
    with (OUT/f'part-{a:04}-{b:04}.log').open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'sol_edits/v3/render.py'),'--range',str(a),str(b),
                        '--out',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    return dict(start=a,end=b,file=out.name,seconds=time.time()-started,
                **json.loads(out.with_suffix('.cost.json').read_text()))


def command(args):
    subprocess.run(args,cwd=ROOT,check=True)


def main():
    sys.path.insert(0,str(ROOT))
    from sol_edits.v3.bootstrap import load
    S,_=load()
    assert S.FPS==60 and S.NFRAMES==3720
    step=S.NFRAMES//5
    bounds=[(i,min(i+step,S.NFRAMES)) for i in range(0,S.NFRAMES,step)]
    start=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        report=list(pool.map(run_part,bounds))
    (OUT/'render-cost.json').write_text(json.dumps(dict(parts=report,wall_seconds=time.time()-start),indent=2)+'\n')
    concat=OUT/'parts.txt'
    concat.write_text(''.join(f"file '{(OUT/r['file']).as_posix()}'\n" for r in report))
    command(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(OUT/'sol-v3-silent.mp4')])
    command(['ffmpeg','-v','error','-y','-i',str(OUT/'sol-v3-silent.mp4'),'-i',str(OUT/'sol-v3-score.wav'),
             '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t',str(S.NFRAMES/S.FPS),
             '-metadata','title=Concert comparison - GPT-6.1 Sol V3','-movflags','+faststart',str(OUT/'Sol-V3-When-Love-Becomes-Light-1080p60.mp4')])
    command(['ffmpeg','-v','error','-y','-i',str(OUT/'Sol-V3-When-Love-Becomes-Light-1080p60.mp4'),'-i',str(OUT/'sol-v3-score.wav'),'-map','0:v:0','-map','1:a:0','-vf','scale=1280:720',
             '-c:v','libx264','-threads','2','-preset','medium','-crf','23','-pix_fmt','yuv420p','-fps_mode','passthrough',
             '-c:a','aac','-b:a','160k','-t',str(S.NFRAMES/S.FPS),'-metadata','title=Concert review - GPT-6.1 Sol V3 - 60 fps',
             '-movflags','+faststart',str(OUT/'Sol-V3-When-Love-Becomes-Light-review-720p60.mp4')])
    print('finished',OUT,flush=True)

if __name__=='__main__':main()
