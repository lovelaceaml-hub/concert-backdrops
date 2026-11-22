"""Prepare song 10's full backdrop render, version 2: the pinned engine snapshots (as Revision 3), this song's
audio features (on the reference clock, which the song module uses) and the review soundtrack: the reference
conformed to the live length, exactly 211.0 s (ffmpeg atempo, pitch kept), then 15 s of silence (226.0 s).
The recording is never committed: pass its path. Everything generated goes to work/s10_full2/ (ignored by git).

    python tools/s10_full2/s10_prepare.py --audio /path/to/s10.m4a

Expected recording: 211.605 s, SHA-256 9c0ad27bfc0cabe1e1881098539649fc0d24ffc81acce3d4d4a13e061f1f991b.
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
WORK = ROOT / 'work/s10_full2'
SHA = '9c0ad27bfc0cabe1e1881098539649fc0d24ffc81acce3d4d4a13e061f1f991b'
NF = 13560
FPS = 60
LIVE = 211.0


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
    subprocess.run([sys.executable, str(SNAPSHOT / 'engine/analyze.py'), str(wav), str(WORK / 'features.npz')],
                   env=env, check=True)
    total = NF / FPS
    ref = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                str(a.audio)], check=True, capture_output=True, text=True).stdout)
    tempo = ref / LIVE
    af = f'atempo={tempo:.9f},atrim=0:{LIVE},apad=whole_dur={LIVE}' if abs(ref - LIVE) > 1e-3 else 'anull'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(a.audio), '-af', af, '-ac', '2', '-ar', '48000',
                    '-c:a', 'pcm_s24le', str(WORK / 'music211.wav')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(WORK / 'music211.wav'), '-af',
                    f'apad=whole_dur={total:.6f}', '-c:a', 'pcm_s24le', str(WORK / 'score.wav')], check=True)
    (WORK / 'provenance.json').write_text(json.dumps(dict(audio_sha256=sha, reference_seconds=ref, tempo=tempo,
                                                          live_seconds=LIVE, frames=NF, fps=FPS,
                                                          seconds=total), indent=2) + '\n')
    print('song 10 ready:', WORK)


if __name__ == '__main__':
    main()
