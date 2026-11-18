"""Prepare song 11's full backdrop render, version 2: the pinned engine snapshots (as Revision 3), this song's
audio features (on the reference clock, which the song module uses) and the review soundtrack.

The reference (church choir upload, 268.224 s file) has its first sound at 0.60 s and its last chord rung out by
262.60 s (silence after). That musical span, 262.0 s, is conformed to the live length, exactly 260.0 s (ffmpeg
atempo 262/260, pitch kept), then 15 s of silence: 275.0 s in all. Every section keeps its proportional place
(one common factor; an estimate until a rehearsal recording exists).
The recording is never committed: pass its path. Everything generated goes to work/s11_full2/ (ignored by git).

    python tools/s11_full2/s11_prepare.py --audio /path/to/s11.mp3

Expected recording SHA-256 70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004.
No em dash or en dash anywhere in this file.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / 'work/s11_full2'
SHA = '70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004'
FPS = 60
LIVE = 260.0
HOLD = 15.0
REF0, REF1 = 0.60, 262.60          # first sound, last chord rung out (reference seconds)
NF = int(round((LIVE + HOLD) * FPS))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audio', required=True, type=Path)
    a = ap.parse_args()
    sha = hashlib.sha256(a.audio.read_bytes()).hexdigest()
    if sha != SHA:
        print(f'warning: audio SHA-256 {sha} is not the expected recording', file=sys.stderr)
    subprocess.run([sys.executable, str(ROOT / 'tools/nine_colours_minor/prepare.py')], check=True)
    sys.path.insert(0, str(ROOT / 'tools/nine_colours_minor'))
    from prepare import SNAPSHOT
    WORK.mkdir(parents=True, exist_ok=True)
    wav = WORK / 'audio.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(a.audio), '-ac', '1', '-ar', '22050', str(wav)],
                   check=True)
    env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / 'numba'))
    if not (WORK / 'features.npz').exists():
        subprocess.run([sys.executable, str(SNAPSHOT / 'engine/analyze.py'), str(wav), str(WORK / 'features.npz')],
                       env=env, check=True)
    total = NF / FPS
    tempo = (REF1 - REF0) / LIVE
    af = f'atrim={REF0}:{REF1},asetpts=PTS-STARTPTS,atempo={tempo:.9f},atrim=0:{LIVE},apad=whole_dur={LIVE}'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(a.audio), '-af', af, '-ac', '2', '-ar', '48000',
                    '-c:a', 'pcm_s24le', str(WORK / 'music260.wav')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(WORK / 'music260.wav'), '-af',
                    f'apad=whole_dur={total:.6f}', '-c:a', 'pcm_s24le', str(WORK / 'score.wav')], check=True)
    (WORK / 'provenance.json').write_text(json.dumps(dict(audio_sha256=sha, ref_start=REF0, ref_end=REF1,
                                                          tempo=tempo, live_seconds=LIVE, frames=NF, fps=FPS,
                                                          seconds=total), indent=2) + '\n')
    print('song 11 ready:', WORK)


if __name__ == '__main__':
    main()
