"""Preserve Film 10's original medley, with two seconds of quiet before it."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'work/sol4'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'audio/promo/concert-medley.mp3';sr=48000
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-ar',str(sr),'-ac','2','-f','f32le','-'])
    y=np.frombuffer(raw,'<f4').reshape(-1,2).astype(np.float64)[:60*sr]
    assert len(y)==60*sr
    gain=.91/np.max(np.abs(y));y*=gain
    n=round(.10*sr);y[:n]*=np.sin(np.linspace(0,np.pi/2,n))[:,None]**2
    # The existing medley already releases below -90 dBFS at its end.
    sf.write(OUT/'medley-scene-clock.wav',y,sr,subtype='PCM_24')
    score=np.concatenate([np.zeros((2*sr,2)),y]);assert len(score)==62*sr
    sf.write(OUT/'Nine-Colours-original-medley.wav',score,sr,subtype='PCM_24')
    report=dict(source=str(source.relative_to(ROOT)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                gain=float(gain),duration=62,quiet_leadin=2,peak=float(np.max(np.abs(score))),
                final_20ms_db=float(20*np.log10(max(np.sqrt(np.mean(score[-960:]**2)),1e-12))))
    (OUT/'music-plan.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
