"""Local native 1080p60 production and phone-ready delivery, never a cloud job."""
import argparse,concurrent.futures,json,resource,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/sol4'
SCORE=OUT/'Nine-Colours-original-medley.wav'

def run(args):subprocess.run(args,cwd=ROOT,check=True)

def part(bounds):
    a,b=bounds;path=OUT/f'part-{a:04}-{b:04}.mp4'
    with path.with_suffix('.log').open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'sol_edits/v4/render.py'),'--range',str(a),str(b),
                        '--out',str(path)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    return json.loads(path.with_suffix('.cost.json').read_text())

def validate(path,n):
    s=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0',
        '-show_entries','stream=width,height,avg_frame_rate,nb_read_frames','-of','json',str(path)]))['streams'][0]
    assert (s['width'],s['height'])==(1920,1080)
    assert s['avg_frame_rate']=='60/1' and int(s['nb_read_frames'])==n

def finish(bounds):
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.time()
    paths=[OUT/f'part-{a:04}-{b:04}.mp4' for a,b in bounds]
    for path,(a,b) in zip(paths,bounds):validate(path,b-a)
    concat=OUT/'parts.txt';concat.write_text(''.join(f"file '{p.as_posix()}'\n" for p in paths))
    silent=OUT/'native-silent-1080p60.mp4'
    run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(silent)])
    archive=OUT/'Sol-V4-Nine-Colours-Upgraded-render-master-1080p60.mp4'
    run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(SCORE),'-map','0:v:0','-map','1:a:0',
         '-c:v','copy','-c:a','aac','-b:a','320k','-t','62','-metadata',
         'title=Sol V4 - Nine Colours upgraded - original Film 10 medley','-movflags','+faststart',str(archive)])
    for name,bitrate,scale,audio in [('1080p60','11000k',None,'320k'),('review-720p60','2800k','1280:720','160k')]:
        common=['ffmpeg','-v','error','-y','-i',str(archive),'-i',str(SCORE),'-map','0:v:0','-map','1:a:0']
        if scale:common+=['-vf','scale='+scale]
        common+=['-c:v','libx264','-threads','2','-preset','medium','-b:v',bitrate,'-pix_fmt','yuv420p',
                 '-fps_mode','passthrough','-passlogfile',str(OUT/('pass-'+name))]
        run(common+['-pass','1','-an','-f','null','/dev/null'])
        run(common+['-pass','2','-c:a','aac','-b:a',audio,'-t','62','-metadata',
            'title=Sol V4 - Nine Colours upgraded - '+name,'-movflags','+faststart',
            str(OUT/f'Sol-V4-Nine-Colours-Upgraded-{name}.mp4')])
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    return dict(seconds=time.time()-start,cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime)

def main():
    p=argparse.ArgumentParser();p.add_argument('--finish-only',action='store_true')
    p.add_argument('--workers',type=int,default=5);a=p.parse_args()
    sys.path.insert(0,str(ROOT))
    from sol_edits.v4.bootstrap import load
    S,_=load();n=round(S.TOTAL*S.FPS);assert n==S.NFRAMES==3720 and S.FPS==60
    step=n//5;bounds=[(i,min(i+step,n)) for i in range(0,n,step)]
    OUT.mkdir(parents=True,exist_ok=True);started=time.time()
    if not a.finish_only:
        (OUT/'production-start.json').write_text(json.dumps(dict(start_epoch=started))+'\n')
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(part,bounds))
    parts=[json.loads((OUT/f'part-{x:04}-{y:04}.cost.json').read_text()) for x,y in bounds]
    native_done=time.time();report=dict(parts=parts,native_cpu_seconds=sum(x['cpu_seconds'] for x in parts))
    discarded=OUT/'discarded-native.json'
    if discarded.exists():report['discarded_cpu_seconds']=sum(x['cpu_seconds'] for x in json.loads(discarded.read_text()))
    production=json.loads((OUT/'production-start.json').read_text())['start_epoch']
    report['native_wall_seconds']=native_done-production
    (OUT/'render-cost.json').write_text(json.dumps(report,indent=2)+'\n')
    report['finish']=finish(bounds)
    report['total_cpu_seconds']=report['native_cpu_seconds']+report.get('discarded_cpu_seconds',0)+report['finish']['cpu_seconds']
    report['total_wall_seconds']=time.time()-production
    (OUT/'render-cost.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)
if __name__=='__main__':main()
