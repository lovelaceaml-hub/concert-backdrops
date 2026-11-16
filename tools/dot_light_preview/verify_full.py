"""Focused encoded-file checks for this creative draft, not musical approval."""
import sys,json,subprocess,hashlib
from pathlib import Path
import numpy as np
path=Path(sys.argv[1])
def run(args):return subprocess.check_output(args)
def db(x):return float(20*np.log10(max(float(np.sqrt(np.mean(np.asarray(x,dtype=float)**2))),1e-12)))
info=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))
v=next(s for s in info['streams'] if s['codec_type']=='video')
pts=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(path)]))
t=np.array([float(f['best_effort_timestamp_time']) for f in pts['frames']])
raw=run(['ffmpeg','-v','error','-i',str(path),'-an','-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','-'])
f=np.frombuffer(raw,np.uint8).reshape(-1,90,160).astype(np.int16)
d=np.abs(np.diff(f,axis=0)).mean((1,2));j=np.abs(np.diff(f,n=2,axis=0)).mean((1,2))
motion=[dict(time=k/60,mean_diff=float(d[k:k+30].mean()),jitter=float(j[k:k+30].mean())) for k in range(0,len(j),30)]
a=np.frombuffer(run(['ffmpeg','-v','error','-i',str(path),'-vn','-ar','48000','-ac','2','-f','f32le','-']),'<f4').reshape(-1,2)
levels=np.array([db(a[k:k+12000]) for k in range(0,len(a),12000)])
joins=[dict(center=c,max_quarter_jump_db=float(abs(np.diff(levels[int((c-1.25)*4):int((c+1.25)*4)+1])).max())) for c in [11.25,19.25,27.25,35.25,43.25,51.25]]
report=dict(file=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),frames=len(t),width=v['width'],height=v['height'],fps=v['avg_frame_rate'],duration=v['duration'],max_pts_error=float(abs(np.diff(t)-1/60).max()),min_frame_luma=float(f.mean((1,2)).min()),max_frame_luma=float(f.mean((1,2)).max()),motion=motion,endcard_mean_diff_55_to_61=float(d[3300:3660].mean()),part_join_diff=float(d[1859]),peak_dbfs=float(20*np.log10(abs(a).max())),lead_peak_dbfs=float(20*np.log10(max(float(abs(a[:96000]).max()),1e-12))),final_second_rms=db(a[-48000:]),joins=joins)
subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True)
report['decode_pass']=True
print(json.dumps(report,indent=2))
