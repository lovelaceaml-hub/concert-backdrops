"""Local native renders, exclusive ranges, soundtrack mux and genuine 60 fps review."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/sol3/nine-colors'
SCORE=ROOT/'work/sol3/sol-v3-score.wav'


def run_part(bounds):
    a,b=bounds;out=OUT/f'part-{a:04}-{b:04}.mp4';started=time.time()
    with (OUT/f'part-{a:04}-{b:04}.log').open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'sol_edits/v3/render.py'),'--range',str(a),str(b),
                        '--out',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    return dict(start=a,end=b,file=out.name,seconds=time.time()-started,
                **json.loads(out.with_suffix('.cost.json').read_text()))


def command(args):
    subprocess.run(args,cwd=ROOT,check=True)


def validate_part(path,expected):
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0',
        '-show_entries','stream=width,height,avg_frame_rate,nb_read_frames','-of','json',str(path)]))['streams'][0]
    assert (meta['width'],meta['height'])==(1920,1080)
    assert meta['avg_frame_rate']=='60/1' and int(meta['nb_read_frames'])==expected


def finish(S,bounds,report=None):
    parts=[]
    for a,b in bounds:
        path=OUT/f'part-{a:04}-{b:04}.mp4';validate_part(path,b-a)
        cost=json.loads(path.with_suffix('.cost.json').read_text())
        assert cost['frames']==b-a and cost['fps']==S.FPS
        parts.append(dict(start=a,end=b,file=path.name,**cost))
    production=json.loads((OUT/'production-start.json').read_text())
    elapsed=time.time()-production['start_epoch']
    discarded=production.get('discarded',[])
    result=dict(parts=parts,wall_seconds=elapsed,
                native_cpu_seconds=sum(q['cpu_seconds'] for q in parts),
                discarded_sections=discarded,
                discarded_cpu_seconds=sum(q['cpu_seconds'] for q in discarded))
    if report:result['worker_wall_seconds']=[r['seconds'] for r in report]
    (OUT/'render-cost.json').write_text(json.dumps(result,indent=2)+'\n')
    concat=OUT/'parts.txt'
    concat.write_text(''.join(f"file '{(OUT/r['file']).as_posix()}'\n" for r in parts))
    command(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(OUT/'sol-v3-silent.mp4')])
    beauty=OUT/'sol-v3-photographic-finish.mp4'
    command([sys.executable,str(ROOT/'sol_edits/v3/grade_people.py'),'--input',str(OUT/'sol-v3-silent.mp4'),'--out',str(beauty)])
    result['photographic_finish']=json.loads(beauty.with_suffix('.cost.json').read_text())
    (OUT/'render-cost.json').write_text(json.dumps(result,indent=2)+'\n')
    duration=str(S.NFRAMES/S.FPS)
    master=OUT/'Sol-V3-Nine-Colors-One-Love-1080p60.mp4'
    command(['ffmpeg','-v','error','-y','-i',str(beauty),'-i',str(SCORE),
             '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t',duration,
             '-metadata','title=Concert comparison - GPT-6.1 Sol V3 - Nine Colors, One Love','-movflags','+faststart',str(master)])
    command(['ffmpeg','-v','error','-y','-i',str(master),'-i',str(SCORE),
             '-map','0:v:0','-map','1:a:0','-vf','scale=1280:720','-c:v','libx264','-threads','2',
             '-preset','medium','-crf','23','-pix_fmt','yuv420p','-fps_mode','passthrough',
             '-c:a','aac','-b:a','160k','-t',duration,'-metadata','title=Concert review - GPT-6.1 Sol V3 - Nine Colors, One Love - 60 fps',
             '-movflags','+faststart',str(OUT/'Sol-V3-Nine-Colors-One-Love-review-720p60.mp4')])
    print('finished',OUT,flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--mux-only',action='store_true');p.add_argument('--workers',type=int,default=5)
    a=p.parse_args();sys.path.insert(0,str(ROOT))
    from sol_edits.v3.bootstrap import load
    S,_=load();assert S.FPS==60 and S.NFRAMES==3720
    step=S.NFRAMES//5;bounds=[(i,min(i+step,S.NFRAMES)) for i in range(0,S.NFRAMES,step)]
    report=None
    if not a.mux_only:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'production-start.json').write_text(json.dumps(dict(start_epoch=time.time(),discarded=[]))+'\n')
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:report=list(pool.map(run_part,bounds))
    finish(S,bounds,report)

if __name__=='__main__':main()
