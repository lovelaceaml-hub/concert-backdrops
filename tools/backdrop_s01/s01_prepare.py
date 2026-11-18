"""Prepare the full song 01 backdrop: the pinned engines (as for Revision 3) and the song's own audio features.

The song itself is kept in Drive only (owner decision 2026-11-18), never in the repository. Download it to
work/s01_full/s01-ensemble.mp3 (or give S01_AUDIO=<path>):

    curl -L -o work/s01_full/s01-ensemble.mp3 \\
      "https://drive.usercontent.google.com/download?id=1wmWrkUIuIU_zE1Hogp_hPUFYBH0J5YJR&export=download&confirm=t"
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools/nine_colours_minor'))
import prepare as r3  # noqa: E402  (restores the pinned Film 10 engine and Claude Final v1)

WORK = ROOT / 'work/s01_full'
AUDIO = Path(os.environ.get('S01_AUDIO', WORK / 's01-ensemble.mp3'))
AUDIO_SHA256 = '2ef650dcf9b2fab141c72a2ce9a3301265326d2b6fe2ec807dcbe3dddd177a01'
HOLD = 15.0                     # seconds of calm morning after the music


def prepare():
    r3.prepare()
    WORK.mkdir(parents=True, exist_ok=True)
    if not AUDIO.exists():
        raise SystemExit(f'Audio missing: {AUDIO}. Download it from Drive (see this file).')
    sha = hashlib.sha256(AUDIO.read_bytes()).hexdigest()
    if sha != AUDIO_SHA256:
        raise SystemExit(f'Audio checksum differs: {sha}')
    if not (WORK / 'features.npz').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(AUDIO), '-ac', '1', '-ar', '22050',
                        str(WORK / 'audio.wav')], check=True)
        env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / 'numba'))
        subprocess.run([sys.executable, str(r3.SNAPSHOT / 'engine/analyze.py'), str(WORK / 'audio.wav'),
                        str(WORK / 'features.npz')], env=env, check=True)
    if not (WORK / 'score.wav').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(AUDIO), '-ac', '2', '-ar', '48000',
                        '-af', f'apad=pad_dur={HOLD}', '-c:a', 'pcm_s24le', str(WORK / 'score.wav')], check=True)
    (WORK / 'provenance.json').write_text(json.dumps(dict(
        engine_commit=r3.ENGINE_COMMIT, claude_reference_commit=r3.CLAUDE_COMMIT,
        audio_sha256=sha, hold_seconds=HOLD), indent=2) + '\n')
    print('Song 01 full backdrop ready: engines, features and score.')


if __name__ == '__main__':
    prepare()
