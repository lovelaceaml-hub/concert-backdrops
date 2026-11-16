"""Compare the delivered soundtrack directly with the owner's Film 10 reference."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import correlate,correlation_lags
SR=12000
def decode(path):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ar',str(SR),'-ac','1','-f','f32le','-'])
    return np.frombuffer(raw,'<f4')
def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--video',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();source=decode(a.reference);delivery=decode(a.video);rows=[]
    for t in [5,10,15,20,25,30,35,40,45,50,55,58.5]:
        x=source[round(t*SR):round((t+.6)*SR)]
        y=delivery[round((t+2)*SR):round((t+2.6)*SR)]
        assert len(x)==len(y)
        c=correlate(y,x,method='fft');lags=correlation_lags(len(y),len(x));mask=np.abs(lags)<=60
        lag=int(lags[mask][np.argmax(c[mask])]);corr=float(np.corrcoef(x,y)[0,1])
        row=dict(reference_time=t,delivery_time=t+2,lag_ms=lag/SR*1000,correlation=corr)
        assert abs(lag)<=12 and corr>.98,row
        rows.append(row)
    a.out.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
