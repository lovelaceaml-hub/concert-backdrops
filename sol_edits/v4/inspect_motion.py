"""Comparable motion triage at 15 samples/second, not a creative quality verdict."""
import argparse
import json
from pathlib import Path
import subprocess
import numpy as np


def inspect(path):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf','fps=15,scale=160:90',
                                 '-f','rawvideo','-pix_fmt','gray','-'])
    x=np.frombuffer(raw,np.uint8).reshape(-1,90,160).astype(np.float32)
    difference=np.abs(np.diff(x,axis=0)).mean(axis=(1,2))
    jitter=np.abs(np.diff(x,n=2,axis=0)).mean(axis=(1,2))
    windows=[]
    for k in range(int((len(x)-1)/7.5)):
        a,b=round(k*7.5),round((k+1)*7.5)
        windows.append(dict(time=k*.5,difference=float(np.mean(difference[a:b])),
                            jitter=float(np.mean(jitter[a:b]))))
    # Exact-looking image holds are checked separately from intentional slow easing.
    mask=difference<0.01
    changes=np.flatnonzero(np.diff(np.r_[False,mask,False]))
    frozen=[dict(start=float(a/15),duration=float((b-a)/15)) for a,b in changes.reshape(-1,2) if b-a>=23]
    return dict(file=path.name,sample_fps=15,units='mean absolute 8-bit grey level',
                p95_difference=float(np.percentile(difference,95)),p95_jitter=float(np.percentile(jitter,95)),
                frozen=frozen,windows=windows)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('files',nargs='+',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    reports=[inspect(path) for path in a.files]
    a.out.write_text(json.dumps(reports,indent=2)+'\n')
    for r in reports:
        print(r['file'],'p95 difference',r['p95_difference'],'p95 jitter',r['p95_jitter'],'holds',r['frozen'])
