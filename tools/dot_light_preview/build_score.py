"""Independent concert edit from seven owner-supplied recordings. No AI music.
Run in a folder with sources/s01.mp3 etc. Generated outputs never belong in git.
Level and beat analysis is not a musical listening approval.
"""
from pathlib import Path
import os,json,subprocess,hashlib
os.environ.setdefault('NUMBA_CACHE_DIR',str(Path(os.environ.get('DOT_MUSIC_WORK',str(Path(__file__).resolve().parents[2]/'work/dot-music')))/'numba'))
import numpy as np
import librosa
from scipy.ndimage import gaussian_filter1d
import soundfile as sf
ROOT=Path(os.environ.get('DOT_MUSIC_WORK',str(Path(__file__).resolve().parents[2]/'work/dot-music')))
ROOT.mkdir(parents=True,exist_ok=True)
RATE=48000
ORDER=['s01','s04','s08','s05','s09','s07','s03']
STARTS=[2,10,18,26,34,42,50]
OVERLAP=2.5

def decode(p,rate=RATE):
 r=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar',str(rate),'-ac','2','-f','f32le','-'])
 return np.frombuffer(r,'<f4').reshape(-1,2).copy()
def db(x):return float(20*np.log10(max(float(np.sqrt(np.mean(np.asarray(x,dtype=float)**2))),1e-12)))
def run():
 mix=np.zeros((62*RATE,2),float); rows=[]
 for i,name in enumerate(ORDER):
  p=ROOT/'sources'/f'{name}.mp3'; full=decode(p); sr=22050
  low=librosa.resample(full.mean(axis=1),orig_sr=RATE,target_sr=sr)
  if i<6:
   # Select a locally strong detected beat near a representative early phrase.
   onset=librosa.onset.onset_strength(y=low[:90*sr],sr=sr)
   tempo,beats=librosa.beat.beat_track(onset_envelope=onset,sr=sr,trim=False)
   bt=librosa.frames_to_time(beats,sr=sr)
   choices=bt[(bt>18)&(bt<48)]
   target=[28,34,26,32,30,36][i]
   source=float(choices[np.argmin(abs(choices-target))]) if len(choices) else float(target)
   # Align transition centers to a regular edit grid, with a modest beat correction.
   bpm=float(np.asarray(tempo).ravel()[0]); rate=1.0
   effective=bpm*(2/3 if bpm>145 else 1)
   if 85<effective<145:rate=float(np.clip(112/effective,.9,1.1))
  else:
   # Retain the actual recording's final decay, with no synthetic reverb.
   hop=RATE//10; env=np.array([db(full[k:k+hop]) for k in range(0,len(full),hop)])
   active=np.flatnonzero(env>-48); last=(active[-1]+1)/10 if len(active) else len(full)/RATE
   # Last audible source second sits at60.6s, leaving true quiet at the end.
   source=last-10.6;rate=1.;bpm=None
  start=STARTS[i]; end=STARTS[i+1]+OVERLAP if i<6 else 62
  count=round((end-start)*RATE)
  raw=subprocess.check_output(['ffmpeg','-v','error','-ss',f'{source:.9f}','-i',str(p),'-af',f'atempo={rate:.12f}','-t',f'{end-start:.9f}','-ar',str(RATE),'-ac','2','-f','f32le','-'])
  clip=np.frombuffer(raw,'<f4').reshape(-1,2).astype(float)
  clip=np.pad(clip,((0,max(0,count-len(clip))),(0,0)))[:count]
  gain=np.clip(-19-db(clip[:min(count,8*RATE)]),-18,14);clip*=10**(gain/20)
  t=np.arange(count)/RATE;env=np.ones(count)
  if i:env*=np.sin(np.clip(t/OVERLAP,0,1)*np.pi/2)
  else:env*=np.sin(np.clip(t/1.5,0,1)*np.pi/2)**2
  if i<6:env*=np.cos(np.clip((t-(end-start-OVERLAP))/OVERLAP,0,1)*np.pi/2)
  else:env*=np.cos(np.clip((t-8.0)/3.5,0,1)*np.pi/2)**2
  mix[round(start*RATE):round(end*RATE)]+=clip*env[:,None]
  rows.append(dict(source=name,source_start=source,film_start=start,film_end=end,tempo_bpm=bpm,effective_bpm=(effective if i<6 else None),meter_assumption=("2/3 pulse interpretation, unverified" if i<6 and bpm>145 else "detected pulse"),tempo_factor=rate,gain_db=float(gain),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 # Gently ride dynamics only near the six joins; no hard gain discontinuity.
 hop=RATE//8;tt=(np.arange(len(mix)//hop)+.5)/8
 levels=np.array([db(mix[k:k+hop]) for k in range(0,len(mix),hop)])
 target=gaussian_filter1d(levels,6);corr=gaussian_filter1d(np.clip(target-levels,-6,6),1.2)
 weight=np.zeros(len(tt))
 for start in STARTS[1:]:weight=np.maximum(weight,np.clip((3.8-abs(tt-(start+OVERLAP/2)))/1.2,0,1))
 mix*=10**(np.interp(np.arange(len(mix))/RATE,tt,corr*weight)[:,None]/20)
 # Refine join-only level rides on the resulting mixed waveform.
 for _ in range(1):
  local=np.array([db(mix[k:k+hop]) for k in range(0,len(mix),hop)])
  desired=gaussian_filter1d(local,5)
  adjustment=gaussian_filter1d(np.clip(desired-local,-12,12),.4)
  mix*=10**(np.interp(np.arange(len(mix))/RATE,tt,adjustment*weight)[:,None]/20)
 mix*=min(1.,10**(-3/20)/np.max(abs(mix)))
 sf.write(ROOT/'The-Light-We-Share-score.wav',mix,RATE,subtype='PCM_24')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'The-Light-We-Share-score.wav'),'-c:a','aac','-b:a','192k',str(ROOT/'The-Light-We-Share-score.m4a')],check=True)
 decoded=decode(ROOT/'The-Light-We-Share-score.m4a')[:62*RATE]
 q=np.array([db(decoded[k:k+RATE//4]) for k in range(0,len(decoded),RATE//4)])
 report=dict(duration=62,order=ORDER,cues=rows,overlap=OVERLAP,lead_peak=float(np.max(abs(decoded[:2*RATE]))),peak_dbfs=float(20*np.log10(np.max(abs(decoded)))),final_second_rms_dbfs=db(decoded[-RATE:]),joins=[dict(center=t+OVERLAP/2,max_quarter_second_change_db=float(np.max(abs(np.diff(q[int((t-.25)*4):int((t+OVERLAP+.25)*4)]))))) for t in STARTS[1:]],limitations=['Measured beat positions are not verified phrase boundaries.','No listening audition performed.','Tempo adjustment limited to 10 percent; sources are not all exactly tempo-matched.','Source03 actual recorded tail retained and additionally tapered; final cadence not auditioned.'])
 (ROOT/'score-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':run()
