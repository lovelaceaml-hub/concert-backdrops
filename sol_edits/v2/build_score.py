"""Seven recorded songs, measured phrase spans, and Song 11's real final cadence.

Requires ffmpeg with Rubber Band. No new music is synthesized. Source 11's
full recording must be downloaded from the owner's project Drive into work.
"""
import argparse
import json
from pathlib import Path
import subprocess
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[2]
SR=48000
DURATION=62
# song, source in/out, film in/out, semitones. Overlaps last 2.31 seconds.
PLAN=[(7,6.710566893,18.181224490,2.0,13.538461538,2),
      (3,14.280272109,22.546575964,11.230769231,19.692307692,0),
      (4,12.469115646,22.476916100,17.384615385,27.384615385,0),
      (5,7.546485261,17.298866213,25.076923077,34.307692308,-2),
      (8,6.060408163,15.789569161,32.0,42.0,0),
      (1,36.548208617,45.882630385,39.692307692,49.692307692,0),
      (11,248.212925,263.026939,47.384615385,62.0,0)]


def build(out,final_source):
    out.mkdir(parents=True,exist_ok=True)
    if not final_source.is_file():
        raise FileNotFoundError('Download the original Song 11 to '+str(final_source))
    score=np.zeros((DURATION*SR,2),np.float64)
    report=[]
    for j,(n,src,end,a,b,pitch) in enumerate(PLAN):
        source=final_source if n==11 else ROOT/f'audio/promo/s{n:02}.mp3'
        rate=(end-src)/(b-a)
        filters=f'rubberband=tempo={rate:.12f}:pitch={2**(pitch/12):.12f}:formant=preserved'
        cmd=['ffmpeg','-v','error','-ss',str(src),'-i',str(source),'-af',filters,
             '-t',str(b-a),'-ar',str(SR),'-ac','2','-f','f32le','-']
        audio=np.frombuffer(subprocess.check_output(cmd),'<f4').reshape(-1,2).copy()
        i0,i1=round(a*SR),round(b*SR)
        length=i1-i0
        audio=np.pad(audio,((0,max(0,length-len(audio))),(0,0)))[:length]
        # Normalize musical material, excluding the original final release.
        active=audio[:round(9*SR)] if n==11 else audio
        rms=np.sqrt(np.mean(active.astype(np.float64)**2))
        gain=float(0.115/max(rms,1e-6))
        audio*=gain
        env=np.ones(length)
        if j==0:
            m=round(1.4*SR)
            env[:m]=np.sin(np.linspace(0,np.pi/2,m))**2
        else:
            m=round((PLAN[j-1][4]-a)*SR)
            env[:m]=np.sin(np.linspace(0,np.pi/2,m))
        if j<len(PLAN)-1:
            m=round((b-PLAN[j+1][3])*SR)
            env[-m:]=np.cos(np.linspace(0,np.pi/2,m))
        else:
            # Below the recording's room noise, prevent a final sample discontinuity.
            m=round(0.05*SR)
            env[-m:]*=np.cos(np.linspace(0,np.pi/2,m))**2
        score[i0:i1]+=audio*env[:,None]
        report.append(dict(song=n,source_in=src,source_out=end,film_in=a,film_out=b,
                           tempo_ratio=rate,pitch_semitones=pitch,gain=gain))
    peak=float(np.max(np.abs(score)))
    headroom=min(1,0.88/peak)
    score*=headroom
    sf.write(out/'sol-v2-score.wav',score,SR,subtype='PCM_24')
    report=dict(duration=DURATION,sample_rate=SR,peak_before=peak,global_gain=headroom,
                final_peak=float(np.max(np.abs(score))),plan=report)
    (out/'score-plan.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=ROOT/'work/sol2')
    p.add_argument('--final-source',type=Path,default=ROOT/'work/sol2/source11-full.mp3')
    a=p.parse_args()
    build(a.out,a.final_source)
