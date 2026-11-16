"""Verify delivered media and inspect all exclusive frame ranges."""
import argparse
import json
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))


def check(path):
    p=probe(path)
    v=next(s for s in p['streams'] if s['codec_type']=='video')
    a=next(s for s in p['streams'] if s['codec_type']=='audio')
    assert v['avg_frame_rate']=='60/1',v['avg_frame_rate']
    assert int(v['nb_read_frames'])==3720,v['nb_read_frames']
    assert abs(float(v['duration'])-62)<1/60
    assert abs(float(a['duration'])-62)<0.05
    stamps=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries',
        'frame=best_effort_timestamp_time','-of','csv=p=0',str(path)],text=True)
    pts=np.array([float(line.split(',')[0]) for line in stamps.splitlines() if line and line.split(',')[0]])
    assert len(pts)==3720
    assert np.max(np.abs(np.diff(pts)-1/60))<1e-5
    print('PTS cadence: all 3719 intervals are one 60 fps sample')
    print(path,json.dumps({k:v[k] for k in ['width','height','avg_frame_rate','nb_read_frames','duration']},indent=2))


def audio(path):
    y,sr=sf.read(path)
    assert np.max(np.abs(y[:sr*2]))==0
    assert np.max(np.abs(y))<0.99
    print('audio peak',float(np.max(np.abs(y))),'final 8s RMS by second',
          [round(float(20*np.log10(max(np.sqrt(np.mean(y[i*sr:(i+1)*sr]**2)),1e-9))),1) for i in range(54,62)])

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('files',nargs='+',type=Path)
    for path in p.parse_args().files:
        audio(path) if path.suffix=='.wav' else check(path)
