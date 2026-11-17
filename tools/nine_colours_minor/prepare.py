"""Restore the exact Film 10 engine privately; prepare its original soundtrack."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work/nine_colours_revision3'
ENGINE_COMMIT = 'd928ff9eafe02ac3150f0c646bdcc497fe5a7278'
SNAPSHOT = ROOT / 'work/nine_colours_minor/render1'
CLAUDE_COMMIT = 'f43f4514e4bc42dc25166e90160d98219f5a0db4'
CLAUDE = WORK / 'claude-final'
LEAD_IN = 6
DURATION = 60 + LEAD_IN


def prepare():
    WORK.mkdir(parents=True, exist_ok=True)
    if not (CLAUDE / 'engine/p3d/words.py').exists():
        archive = WORK / 'claude-final.tar'
        subprocess.run(['git', 'archive', '--format=tar', f'--output={archive}',
                        CLAUDE_COMMIT, 'engine', 'assets'], cwd=ROOT, check=True)
        CLAUDE.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive) as stream:
            stream.extractall(CLAUDE, filter='data')
        archive.unlink()
    if not (SNAPSHOT / 'engine/render.py').exists():
        archive = WORK / 'render1.tar'
        subprocess.run(['git', 'archive', '--format=tar', f'--output={archive}', ENGINE_COMMIT],
                       cwd=ROOT, check=True)
        SNAPSHOT.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive) as stream:
            stream.extractall(SNAPSHOT, filter='data')
        archive.unlink()
    fonts = SNAPSHOT / 'fonts'
    if not fonts.exists():
        fonts.symlink_to(ROOT / 'fonts', target_is_directory=True)
    original = SNAPSHOT / 'audio/promo/concert-medley.mp3'
    if not (WORK / 'features.npz').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(original), '-ac', '1',
                        '-ar', '22050', str(WORK / 'audio.wav')], check=True)
        env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / 'numba'))
        subprocess.run(['python', str(SNAPSHOT / 'engine/analyze.py'), str(WORK / 'audio.wav'),
                        str(WORK / 'features.npz')], env=env, check=True)
    approved = ROOT / 'audio/promo/concert-medley-leadin.mp3'
    if not (WORK / 'score.wav').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(approved), '-ac', '2',
                        '-ar', '48000', '-af', 'adelay=4000|4000', '-c:a', 'pcm_s24le', str(WORK / 'score.wav')], check=True)
    report = dict(engine_commit=ENGINE_COMMIT, claude_reference_commit=CLAUDE_COMMIT,
                  lead_in_seconds=LEAD_IN,
                  duration_seconds=DURATION, approved_audio_delay_seconds=4,
                  original_audio_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                  approved_audio_sha256=hashlib.sha256(approved.read_bytes()).hexdigest())
    (WORK / 'provenance.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Original Film 10 engine, features and approved lead-in soundtrack ready.')


if __name__ == '__main__':
    prepare()
