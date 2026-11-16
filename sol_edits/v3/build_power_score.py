"""A fortissimo concert coda, built entirely from the recorded final chord."""
from pathlib import Path
import json,subprocess
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfiltfilt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/sol3/power-finale'
SR=48000
HIT=55.638061
FINAL_ACCENT=60.418061


def stretch(x,seconds):
    rate=(len(x)/SR)/seconds
    effect=f'rubberband=tempo={rate}:channels=together'
    result=subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-',
        '-af',effect,'-f','f32le','-'],input=x.astype('<f4').tobytes(),stdout=subprocess.PIPE,check=True).stdout
    y=np.frombuffer(result,'<f4').reshape(-1,2).astype(np.float64)
    assert np.max(np.abs(y))<3*max(np.max(np.abs(x)),1e-8),'Time stretch produced an edge spike'
    n=round(seconds*SR)
    return np.pad(y,((0,max(0,n-len(y))),(0,0)))[:n]


def join(a,b,n):
    u=np.linspace(0,1,n)[:,None]
    return np.concatenate([a[:-n],a[-n:]*(1-u)+b[:n]*u,b[n:]])


def db(x):return float(20*np.log10(max(1e-12,np.sqrt(np.mean(x*x)))))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    base,sr=sf.read(ROOT/'work/sol3/sol-v3-score.wav');assert sr==SR
    at=lambda a,b:base[round(a*SR):round(b*SR)]
    attack=at(HIT,HIT+.4)
    sustained=stretch(at(56.0,57.55),4.5)
    # The recorded tonic is articulated again for the final, emphatic accent.
    accent=at(HIT,HIT+.65)
    tail_duration=62-HIT-(.4+4.5+.65)+.18
    release=stretch(at(57.55,62),tail_duration)
    n=round(.06*SR)
    coda=join(join(join(attack,sustained,n),accent,n),release,n)
    target=62*SR-round(HIT*SR)
    coda=np.pad(coda,((0,max(0,target-len(coda))),(0,0)))[:target]
    u=np.linspace(0,1,len(coda))
    gain=1.05+.70*np.sin(np.minimum(u/.77,1)*np.pi/2)**2
    coda*=gain[:,None]
    # Reinforce the recorded orchestra's low register, without adding instruments.
    low=sosfiltfilt(butter(2,180,fs=SR,output='sos'),coda,axis=0)
    coda+=.18*low
    peak=np.max(np.abs(coda));coda*=min(1.0,.93/max(peak,1e-12))
    # Match the unedited entrance, then open the gain into the sustained chord.
    ramp=round(.10*SR);u=np.linspace(0,1,ramp)[:,None]
    original=at(HIT,HIT+.1)
    coda[:ramp]=original*(1-u)+coda[:ramp]*u
    n=round(.025*SR);coda[-n:]*=np.cos(np.linspace(0,np.pi/2,n))[:,None]**2
    y=np.concatenate([base[:round(HIT*SR)],coda]);assert len(y)==62*SR
    sf.write(OUT/'concert-grand-finale.wav',y,SR,subtype='PCM_24')
    report=dict(duration=62,quiet_leadin_seconds=2,source='Original recorded concert Song 11 only',
        sustained_chord_source=[56.0,57.55],sustained_seconds=4.5,
        final_accent=FINAL_ACCENT,release_seconds=tail_duration,
        peak=float(np.max(np.abs(y))),last_20ms_db=db(y[-round(.02*SR):]),
        final_seconds_db=[db(y[i*SR:(i+1)*SR]) for i in range(54,62)])
    assert min(report['final_seconds_db'][2:6])>-22,'The sustained climax must remain full and loud'
    (OUT/'power-score-plan.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':main()
