"""Song 11 full backdrop: restore the pinned engines and prepare the song's audio (kept outside the repo).

    S11_AUDIO=/path/to/s11.mp3 python tools/s11_full/s11_prepare.py

The song audio is the church choir upload (youtu.be/tdiD_qDWuWI), link-shared from Anthony's Drive:
    curl -L -o s11.mp3 "https://drive.usercontent.google.com/download?id=108zDtdB4X189DOwsZn-K9p548nERubLG&export=download&confirm=t"
It is never committed. This script checks its SHA-256, writes the engine's audio features and the score
(the whole file, then HOLD seconds of silence) under work/s11_full/ (untracked).
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/nine_colours_minor'))
import prepare as r3  # noqa: E402  (restores the pinned Film 10 engine and Claude Final v1)

WORK = ROOT / 'work/s11_full'
AUDIO_SHA = '70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004'
AUDIO = Path(os.environ.get('S11_AUDIO', '/home/user/s11work/audio/s11.mp3'))
MUSIC_LEN = 268.18      # the file, seconds (music audible 0.5 to about 260.5, then quiet)
HOLD = 15.0             # calm hold after the music, owner rule
TOTAL = MUSIC_LEN + HOLD
FPS = 30


def prepare():
    r3.prepare()
    WORK.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(AUDIO.read_bytes()).hexdigest()
    if sha != AUDIO_SHA:
        raise SystemExit(f'Unexpected audio {AUDIO}: {sha}')
    if not (WORK / 'features.npz').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(AUDIO), '-ac', '1', '-ar', '22050',
                        str(WORK / 'audio.wav')], check=True)
        env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / 'numba'))
        subprocess.run(['python', str(r3.SNAPSHOT / 'engine/analyze.py'), str(WORK / 'audio.wav'),
                        str(WORK / 'features.npz')], env=env, check=True)
    if not (WORK / 'score.wav').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(AUDIO), '-ac', '2', '-ar', '48000',
                        '-af', f'apad=whole_dur={TOTAL}', '-t', f'{TOTAL}', '-c:a', 'pcm_s24le',
                        str(WORK / 'score.wav')], check=True)
    (WORK / 'provenance.json').write_text(json.dumps(dict(
        engine_commit=r3.ENGINE_COMMIT, claude_reference_commit=r3.CLAUDE_COMMIT, audio_sha256=sha,
        music_seconds=MUSIC_LEN, hold_seconds=HOLD, total_seconds=TOTAL, fps=FPS), indent=2) + '\n')
    print('Song 11 ready:', WORK)


if __name__ == '__main__':
    prepare()
