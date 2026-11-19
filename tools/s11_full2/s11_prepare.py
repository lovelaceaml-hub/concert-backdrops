"""Song 11 full backdrop, version 2: restore the pinned engines and prepare the audio (kept outside the repo).

    S11_AUDIO=/path/to/s11.mp3 python tools/s11_full2/s11_prepare.py

The audio is the church choir upload, link-shared from Anthony's Drive (file id 108zDtdB4X189DOwsZn-K9p548nERubLG):
    curl -L -o s11.mp3 "https://drive.usercontent.google.com/download?id=108zDtdB4X189DOwsZn-K9p548nERubLG&export=download&confirm=t"
It is never committed. Its music runs 0.84 s to 259.95 s, within 1 s of the 4:20 live length, so it is used
unchanged: the score is the file cut at 260.0 s, then 15 s of silence (the calm hold): 275.0 s in all.
Everything written here lives under work/s11_full2/ (untracked).
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

WORK = ROOT / 'work/s11_full2'
AUDIO_SHA = '70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004'
AUDIO = Path(os.environ.get('S11_AUDIO', '/home/user/work/s11/s11.mp3'))
LIVE = 260.0            # the live length; the music part of the video
HOLD = 15.0             # calm hold after the music
TOTAL = LIVE + HOLD
FPS = 60


def prepare():
    r3.prepare()
    WORK.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(AUDIO.read_bytes()).hexdigest()
    if sha != AUDIO_SHA:
        raise SystemExit(f'Unexpected audio {AUDIO}: {sha}')
    if not (WORK / 'score.wav').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(AUDIO), '-ac', '2', '-ar', '48000',
                        '-af', f'atrim=0:{LIVE},afade=t=out:st={LIVE - 0.05}:d=0.05,apad=whole_dur={TOTAL}',
                        '-t', f'{TOTAL}', '-c:a', 'pcm_s24le', str(WORK / 'score.wav')], check=True)
    if not (WORK / 'features.npz').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(WORK / 'score.wav'), '-ac', '1', '-ar', '22050',
                        str(WORK / 'audio.wav')], check=True)
        env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / 'numba'))
        subprocess.run([sys.executable, str(r3.SNAPSHOT / 'engine/analyze.py'), str(WORK / 'audio.wav'),
                        str(WORK / 'features.npz')], env=env, check=True)
    (WORK / 'provenance.json').write_text(json.dumps(dict(
        engine_commit=r3.ENGINE_COMMIT, claude_reference_commit=r3.CLAUDE_COMMIT, audio_sha256=sha,
        live_seconds=LIVE, hold_seconds=HOLD, total_seconds=TOTAL, fps=FPS), indent=2) + '\n')
    print('Song 11 v2 ready:', WORK)


if __name__ == '__main__':
    prepare()
