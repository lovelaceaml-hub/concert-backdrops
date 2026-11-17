"""One sustained orchestral arc from the owner's recorded concert music."""
from pathlib import Path
import subprocess,json
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[2]
SR=48000

def main():
    source=ROOT/'work/sol3/source11-full.mp3'
    start=203.026939
    raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(source),'-t','60',
                                 '-ar',str(SR),'-ac','2','-f','f32le','-'])
    x=np.frombuffer(raw,'<f4').reshape(-1,2).astype(np.float64)
    x=np.pad(x,((0,max(0,60*SR-len(x))),(0,0)))[:60*SR]
    n=round(1.5*SR);x[:n]*=np.sin(np.linspace(0,np.pi/2,n))[:,None]**2
    n=round(.05*SR);x[-n:]*=np.cos(np.linspace(0,np.pi/2,n))[:,None]**2
    gain=min(.92/max(np.max(np.abs(x)),1e-9),.16/max(np.sqrt(np.mean(x[:54*SR]**2)),1e-9))
    y=np.concatenate([np.zeros((2*SR,2)),x*gain])
    sf.write(ROOT/'work/sol3/sol-v3-score.wav',y,SR,subtype='PCM_24')
    report=dict(source='Original concert Song 11',source_in=start,source_out=263.026939,
                leadin=2,duration=len(y)/SR,gain=float(gain),peak=float(np.max(np.abs(y))),
                final_seconds_db=[float(20*np.log10(max(1e-10,np.sqrt(np.mean(y[i*SR:(i+1)*SR]**2))))) for i in range(54,62)])
    (ROOT/'work/sol3/music-plan.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
