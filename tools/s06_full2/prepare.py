"""Song 06 backdrop v2: restore the pinned engines, fetch and check the reference recording, measure it, and
build the conformed score. Output goes to work/s06_full2/ (untracked); the song audio is never committed.

    python tools/s06_full2/prepare.py [--audio /path/to/s06.m4a]

The engine is measured on the REFERENCE recording (its own clock; render.py maps live frames onto it). The
score is the reference conformed to the live length, 137.0 s, with ffmpeg atempo (pitch kept), then 15 s of
silence for the calm hold: 152.0 s in all.
No em dash or en dash anywhere in this file.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/nine_colours_minor'))
import prepare as r3  # noqa: E402  (restores the Film 10 engine and Claude Final v1 snapshots)

WORK = ROOT / 'work/s06_full2'
AUDIO_URL = ('https://drive.usercontent.google.com/download?id=1YqFkD3lQprvotC32xRfC8Dqno0I24hqs'
             '&export=download&confirm=t')
AUDIO_SHA256 = 'b0b0de6a6f29a6dfc9dbdab935f8049360f05e77896f89cb52b68365f6f61d71'
REF = 134.8467                     # the reference recording's decoded length (134.84667 s; the container says 134.89)
LIVE = 137.0                       # the live length, DESIGN-SYSTEM 4
HOLD = 15.0
TOTAL = LIVE + HOLD                # 152.0 s
FPS = 60
NFRAMES = int(round(TOTAL * FPS))  # 9120


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audio', type=Path, default=WORK / 's06.m4a')
    args = ap.parse_args()
    r3.prepare()
    WORK.mkdir(parents=True, exist_ok=True)
    if not args.audio.exists():
        subprocess.run(['curl', '-sSL', '-o', str(args.audio), AUDIO_URL], check=True)
    if sha(args.audio) != AUDIO_SHA256:
        raise SystemExit(f'{args.audio}: unexpected SHA-256; refusing to continue')
    wav = WORK / 'audio.wav'
    if not (WORK / 'features.npz').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.audio), '-ac', '1', '-ar', '22050', str(wav)],
                       check=True)
        env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / 'numba'))
        subprocess.run([sys.executable, str(r3.SNAPSHOT / 'engine/analyze.py'), str(wav), str(WORK / 'features.npz')],
                       env=env, check=True)
    tempo = REF / LIVE
    music = WORK / 'music_live.wav'
    if not music.exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.audio), '-ac', '2', '-ar', '48000',
                        '-af', f'atempo={tempo:.6f}', '-t', f'{LIVE:.6f}', '-c:a', 'pcm_s24le', str(music)], check=True)
    score = WORK / 'score.wav'
    if not score.exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(music), '-af', f'apad=whole_dur={TOTAL:.6f}',
                        '-t', f'{TOTAL:.6f}', '-c:a', 'pcm_s24le', str(score)], check=True)
    (WORK / 'provenance.json').write_text(json.dumps(dict(
        audio_sha256=AUDIO_SHA256, reference_seconds=REF, live_seconds=LIVE, atempo=round(tempo, 6),
        hold_seconds=HOLD, total_seconds=TOTAL, frames=NFRAMES, fps=FPS, engine_commit=r3.ENGINE_COMMIT,
        claude_reference_commit=r3.CLAUDE_COMMIT), indent=2) + '\n')
    print('song 06 v2 ready:', WORK)


if __name__ == '__main__':
    main()
