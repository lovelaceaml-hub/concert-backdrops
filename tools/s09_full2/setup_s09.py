"""Prepare song 09's full backdrop: the pinned engines, the audio features and the soundtrack.

The song audio is never committed (repo rule). It is downloaded from Anthony's Drive link into work/
(untracked) and checked against its SHA-256. The soundtrack is the music from 0, then 15 s of silence.
No em dash or en dash anywhere in this file.
"""
from pathlib import Path
import hashlib
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools/nine_colours_minor'))
import prepare as r3  # noqa: E402  (the approved Revision 3 preparation: engine and Claude Final v1 snapshots)

SNAPSHOT = r3.SNAPSHOT
WORK = ROOT / 'work/s09_full2'
FPS = 60
TOTAL = 291.0
FRAMES = int(round(TOTAL * FPS))            # 17460
URL = ('https://drive.usercontent.google.com/download?id=1u4LgRODeqrMaKpdMDjkAVinLjF9QW2-l'
       '&export=download&confirm=t')
SHA = '0b276d665905dfc32ef6509035246fa94f81760bf72daad299bce050ed5b7e97'


def prepare():
    r3.prepare()
    WORK.mkdir(parents=True, exist_ok=True)
    mp3 = WORK / 's09.mp3'
    if not mp3.exists():
        subprocess.run(['curl', '-sL', '-o', str(mp3), URL], check=True)
    if hashlib.sha256(mp3.read_bytes()).hexdigest() != SHA:
        raise SystemExit('s09.mp3 does not match its SHA-256')
    if not (WORK / 'audio.wav').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(mp3), '-ac', '1', '-ar', '22050',
                        str(WORK / 'audio.wav')], check=True)
    if not (WORK / 'features.npz').exists():
        env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / 'numba'))
        subprocess.run([sys.executable, str(SNAPSHOT / 'engine/analyze.py'), str(WORK / 'audio.wav'),
                        str(WORK / 'features.npz')], env=env, check=True)
    score = WORK / 'score.wav'
    if not score.exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(mp3), '-af', f'apad=whole_dur={TOTAL}',
                        '-t', f'{TOTAL}', '-ac', '2', '-ar', '48000', '-c:a', 'pcm_s24le', str(score)], check=True)
    print('song 09 ready:', WORK)


if __name__ == '__main__':
    prepare()
