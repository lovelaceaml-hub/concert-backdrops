"""Build Sol's seven-source score. Media stays in work/sol61, never in git.

Pitch-preserving tempo maps: 156, 156, 156, 104, 104, 104, 156 bpm.
The two tempo families share a 3:2 pulse. Source offsets are on measured beats.
The opening three sources share B flat; the final four share C. Pitch shifts
are limited to three semitones and preserve formants with ffmpeg Rubber Band.
The last orchestral chord excites a deterministic hall response, with no new
attacks during its ring-out. Only the residual noise floor is tapered at 61.8 s.
"""
from pathlib import Path
import argparse
import json
import subprocess
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
import soundfile as sf

ROOT=Path(__file__).resolve().parents[2]
SR=48000
# source, source in, source bpm, target bpm, film in, film out (overlaps included)
# The source endpoints come from beat groups measured in work/sol61/sources.json.
# The last endpoint is the decay after the final chosen attack, before the next attack.
# source, source in, source out, film in, film out
PLAN=[(7,6.7105669,18.1812245,2.0,13.5384615),
      (4,12.4691156,20.9211791,11.2307692,19.6923077),
      (3,14.2802721,24.0326531,17.3846154,27.3846154),
      (5,7.5464853,17.2988662,25.0769231,34.3076923),
      (6,14.1177324,23.4289342,32.0,41.2307692),
      (11,23.0806349,34.6209524,38.9230769,50.4615385),
      (1,46.5560091,55.80,48.1538462,57.3846154)]


PITCH={7:2,4:0,3:0,5:-2,6:-3,11:0,1:0}


def decode(n,start,duration,rate):
    cmd=['ffmpeg','-v','error','-ss',str(start),'-i',str(ROOT/f'audio/promo/s{n:02}.mp3'),
         '-af',f'rubberband=tempo={rate:.9f}:pitch={2**(PITCH[n]/12):.9f}:formant=preserved','-t',str(duration),'-ar',str(SR),'-ac','2','-f','f32le','-']
    return np.frombuffer(subprocess.check_output(cmd),'<f4').reshape(-1,2).copy()


def build(out):
    out.mkdir(parents=True,exist_ok=True)
    score=np.zeros((62*SR,2),np.float64)
    report=[]
    for j,(n,src,end,a,b) in enumerate(PLAN):
        rate=(end-src)/(b-a)
        audio=decode(n,src,b-a,rate)
        length=round((b-a)*SR)
        audio=np.pad(audio,((0,max(0,length-len(audio))),(0,0)))[:length]
        rms=np.sqrt(np.mean(audio**2))
        gain=float(min(2.2,0.125/max(rms,1e-6)))
        audio*=gain
        env=np.ones(length)
        if j==0:
            m=round(1.1*SR)
            env[:m]=np.sin(np.linspace(0,np.pi/2,m))**2
        else:
            overlap=PLAN[j-1][-1]-a
            m=round(overlap*SR)
            env[:m]=np.sin(np.linspace(0,np.pi/2,m))
        if j<len(PLAN)-1:
            overlap=b-PLAN[j+1][-2]
            m=round(overlap*SR)
            env[-m:]=np.cos(np.linspace(0,np.pi/2,m))
        else:
            # A release, not a new musical cut: remove subsequent attacks and let the hall respond.
            m=round(0.16*SR)
            env[-m:]*=np.cos(np.linspace(0,np.pi/2,m))**2
        score[round(a*SR):round(b*SR)]+=audio*env[:,None]
        report.append(dict(song=n,source_in=src,source_out=end,tempo_ratio=rate,pitch_semitones=PITCH[n],film_in=a,film_out=b,gain=gain))
    # Early reflections and a smooth, dark hall. A deterministic impulse avoids a looped/frozen chord.
    rng=np.random.default_rng(6101)
    dur=4.25
    tt=np.arange(round(dur*SR))/SR
    ir=np.zeros(len(tt))
    taps=rng.integers(round(0.025*SR),len(tt),240)
    ir[taps]=rng.normal(0,1,len(taps))*np.exp(-taps/SR*1.15)
    ir=sosfilt(butter(2,4200,fs=SR,output='sos'),ir)
    ir/=np.sqrt(np.sum(ir*ir))
    for c in range(2):
        wet=fftconvolve(score[:,c],ir if c==0 else np.roll(ir,337))[:len(score)]
        score[:,c]+=0.38*wet
        for delay,k in [(0.071,0.10),(0.127,0.07),(0.229,0.04)]:
            d=round(delay*SR)
            score[d:,c]+=k*score[:-d,c].copy()
    # Preserve the exact quiet lead-in; reflections are causal, no pre-echo.
    score[:2*SR]=0
    peak=np.max(np.abs(score))
    if peak>0.88: score*=0.88/peak
    m=round(0.3*SR)
    score[-m:]*=np.linspace(1,0,m)[:,None]**2
    sf.write(out/'sol61-medley.wav',score,SR,subtype='PCM_24')
    (out/'medley-plan.json').write_text(json.dumps(report,indent=2)+'\n')
    print('wrote',out/'sol61-medley.wav','peak',np.max(np.abs(score)))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=ROOT/'work/sol61')
    build(p.parse_args().out)
