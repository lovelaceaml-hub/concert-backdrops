"""Song 06 full backdrop: restore the pinned engines, fetch and check the song audio, analyse it, and build the
score (the music, then silence for the calm hold). Nothing here touches tracked files; all output goes to
work/s06_full/ (untracked). The song audio is never committed.

    python tools/s06_full/prepare.py [--audio /path/to/s06.m4a]
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

WORK = ROOT / 'work/s06_full'
AUDIO_URL = ('https://drive.usercontent.google.com/download?id=1YqFkD3lQprvotC32xRfC8Dqno0I24hqs'
             '&export=download&confirm=t')
AUDIO_SHA256 = 'b0b0de6a6f29a6dfc9dbdab935f8049360f05e77896f89cb52b68365f6f61d71'
MUSIC = 134.85
FPS = 30
NFRAMES = 4496                     # ceil((134.85 + 15) * 30)
TOTAL = NFRAMES / FPS


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
    score = WORK / 'score.wav'
    if not score.exists():
        # stereo 48 kHz PCM: the music exactly as recorded, then silence to the last video frame
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.audio), '-ac', '2', '-ar', '48000',
                        '-af', f'apad=whole_dur={TOTAL:.6f}', '-t', f'{TOTAL:.6f}', '-c:a', 'pcm_s24le', str(score)],
                       check=True)
    (WORK / 'provenance.json').write_text(json.dumps(dict(
        audio_sha256=AUDIO_SHA256, music_seconds=MUSIC, hold_seconds=round(TOTAL - MUSIC, 3), frames=NFRAMES,
        fps=FPS, engine_commit=r3.ENGINE_COMMIT, claude_reference_commit=r3.CLAUDE_COMMIT), indent=2) + '\n')
    print('song 06 ready:', WORK)


if __name__ == '__main__':
    main()
