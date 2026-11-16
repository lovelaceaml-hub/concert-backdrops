"""Check the supplied score, its release and alignment after AAC encoding."""
import argparse
import json
from pathlib import Path
import subprocess
import numpy as np
from scipy.signal import correlate,correlation_lags
import soundfile as sf

ROOT=Path(__file__).resolve().parents[2]
SR=48000


def db(x):
    return float(20*np.log10(max(1e-12,np.sqrt(np.mean(x*x)))))


def check(video,score_path,tail_seconds):
    score,sr=sf.read(score_path)
    assert sr==SR and len(score)==62*SR
    tail=round(tail_seconds*SR)
    assert tail>0
    report=dict(peak=float(np.max(np.abs(score))),quiet_leadin_db=db(score[:2*SR]),
                final_seconds_db=[db(score[i*SR:(i+1)*SR]) for i in range(54,62)],
                score=str(score_path),release_window_seconds=tail_seconds,
                release_db=db(score[-tail:]),alignment=[])
    if video:
        raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vn','-ar',str(SR),
                                     '-ac','2','-f','f32le','-'])
        decoded=np.frombuffer(raw,'<f4').reshape(-1,2).astype(np.float64)
        report.update(encoded_peak=float(np.max(np.abs(decoded))),encoded_last_second_db=db(decoded[61*SR:62*SR]),
                      encoded_samples=len(decoded),encoded_quiet_leadin_db=db(decoded[:round(1.95*SR)]))
        assert report['encoded_peak']<1,'AAC encoding clips'
        for t in [6,17,30,43,55,59]:
            a,b=round((t-.5)*SR),round((t+.5)*SR)
            x=score[a:b:12].mean(axis=1);y=decoded[a:b:12].mean(axis=1)
            c=correlate(y,x,mode='full',method='fft');lags=correlation_lags(len(y),len(x),mode='full')
            mask=np.abs(lags)<800;lag=int(lags[mask][np.argmax(c[mask])])
            row=dict(time=t,encoded_lag_ms=lag/4,correlation=float(np.corrcoef(x,y)[0,1]))
            assert abs(lag)<=4,'Soundtrack drift exceeds 1 ms'
            assert row['correlation']>.98,'Encoded audio differs from the score'
            report['alignment'].append(row)
    assert report['peak']<.99 and report['quiet_leadin_db']<-100
    assert report['release_db']<-45
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--video',type=Path)
    p.add_argument('--score',type=Path,default=ROOT/'work/sol3/sol-v3-score.wav')
    p.add_argument('--tail-seconds',type=float,default=1)
    p.add_argument('--out',type=Path,default=ROOT/'work/sol3/nine-colors/audio-check.json')
    a=p.parse_args();r=check(a.video,a.score,a.tail_seconds);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
