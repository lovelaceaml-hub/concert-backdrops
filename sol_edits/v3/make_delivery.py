"""Fit the 1080p60 master within the Drive connector's 100 MiB transfer limit."""
import json,resource,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/sol3/power-finale'


def main():
    started=time.time()
    source=OUT/'Sol-V3-Nine-Colors-Grand-Finale-1080p60.mp4'
    target=OUT/'Sol-V3-Nine-Colors-Grand-Finale-1080p60-download.mp4'
    common=['ffmpeg','-v','error','-y','-i',str(source),'-map','0:v:0','-map','0:a:0',
        '-c:v','libx264','-threads','2','-preset','medium','-b:v','11000k','-pix_fmt','yuv420p',
        '-fps_mode','passthrough','-passlogfile',str(OUT/'delivery-pass')]
    subprocess.run(common+['-pass','1','-an','-f','null','/dev/null'],check=True)
    subprocess.run(common+['-pass','2','-c:a','copy','-t','62','-movflags','+faststart',str(target)],check=True)
    assert target.stat().st_size<100*1024*1024
    me=resource.getrusage(resource.RUSAGE_SELF);children=resource.getrusage(resource.RUSAGE_CHILDREN)
    report=dict(seconds=time.time()-started,cpu_seconds=me.ru_utime+me.ru_stime+children.ru_utime+children.ru_stime,
                bytes=target.stat().st_size)
    (OUT/'delivery-cost.json').write_text(json.dumps(report,indent=2)+'\n');print(report)


if __name__=='__main__':main()
