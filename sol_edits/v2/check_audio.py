"""Measure the source score and encoded soundtrack alignment at all six joins."""
import argparse
import json
from pathlib import Path
import subprocess
import numpy as np
from scipy.signal import correlate,correlation_lags
import soundfile as sf
from build_score import PLAN,ROOT,SR


def db(x):
    return float(20*np.log10(max(1e-12,np.sqrt(np.mean(x*x)))))


def check(video):
    score,_=sf.read(ROOT/'work/sol2/sol-v2-score.wav')
    report=dict(peak=float(np.max(np.abs(score))),quiet_leadin_db=db(score[:2*SR]),
                final_seconds_db=[db(score[i*SR:(i+1)*SR]) for i in range(54,62)],joins=[])
    decoded=None
    if video:
        raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vn','-ar',str(SR),
                                     '-ac','2','-f','f32le','-'])
        decoded=np.frombuffer(raw,'<f4').reshape(-1,2).astype(np.float64)
        report.update(encoded_peak=float(np.max(np.abs(decoded))),encoded_last_second_db=db(decoded[61*SR:62*SR]),
                      encoded_samples=len(decoded),encoded_quiet_leadin_db=db(decoded[:round(1.95*SR)]))
    for j,q in enumerate(PLAN[1:],1):
        start=q[3];end=PLAN[j-1][4];t=(start+end)/2
        before=db(score[round((t-.25)*SR):round(t*SR)])
        after=db(score[round(t*SR):round((t+.25)*SR)])
        row=dict(time=t,before_db=before,after_db=after,change_db=after-before)
        if decoded is not None:
            a,b=round((t-1)*SR),round((t+1)*SR)
            x=score[a:b:12].mean(axis=1);y=decoded[a:b:12].mean(axis=1)
            c=correlate(y,x,mode='full',method='fft');lags=correlation_lags(len(y),len(x),mode='full')
            mask=np.abs(lags)<800
            lag=int(lags[mask][np.argmax(c[mask])])
            row.update(encoded_lag_ms=lag/4,correlation=float(np.corrcoef(x,y)[0,1]))
            assert abs(lag)<=4,'Soundtrack drift exceeds 1 ms'
            assert row['correlation']>.98,'Encoded audio differs from the score'
        report['joins'].append(row)
    assert report['peak']<.99
    assert report['final_seconds_db'][-1]<-45
    assert max(abs(q['change_db']) for q in report['joins'])<3
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--video',type=Path)
    p.add_argument('--out',type=Path,default=ROOT/'work/sol2/audio-check.json')
    a=p.parse_args();r=check(a.video);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
