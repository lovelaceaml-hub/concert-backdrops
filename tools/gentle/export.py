"""Render the A World Made Gentle film locally at native 1080p60.

Run after tools/gentle/music.py and engine/analyze.py. Four independent processes
render eight time ranges. Existing complete ranges are reusable only when the
source manifest matches. Outputs and logs stay outside version control.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out/gentle'
WORK = ROOT / 'work/gentle'
FRAMES = 3720


def frame_count(path):
    if not path.exists():
        return 0
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                        '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(path)],
                       capture_output=True, text=True)
    return int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else 0


def run(workers, parts):
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    keys = sorted((ROOT / 'engine').rglob('*.py')) + sorted((ROOT / 'tools/gentle').glob('*.py')) + [WORK / 'features.npz', WORK / 'score.wav']
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in keys}
    manifest.update(parts=parts, frames=FRAMES, resolution='1920x1080', fps=60)
    mp = WORK / 'render-manifest.json'
    old = json.loads(mp.read_text()) if mp.exists() else None
    if old and old != manifest:
        raise SystemExit('Inputs changed: move prior part files and render-manifest.json before rerendering.')
    mp.write_text(json.dumps(manifest, indent=2) + '\n')
    env = dict(os.environ, SONG='gentle_film', FEATURES=str(WORK / 'features.npz'),
               OUT_FPS='60', OUT_RES='1080p', LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', P3D_CACHE=str(WORK / 'p3d-cache'),
               MESA_SHADER_CACHE_DIR=str(WORK / 'mesa-cache'), NUMBA_CACHE_DIR=str(WORK / 'numba'))

    def part(i):
        first, last = FRAMES * i // parts, FRAMES * (i + 1) // parts
        path = OUT / f'part-{i:02d}.mp4'
        if frame_count(path) == last - first:
            print(f'part {i}: reusing {last-first} verified frames', flush=True)
            return
        start = time.monotonic()
        with (WORK / f'render-{i:02d}.log').open('w') as log:
            subprocess.run([sys.executable, str(ROOT / 'tools/gentle/render.py'), '--range', str(first), str(last),
                            '--out', str(path), '--crf', '18', '--preset', 'fast'],
                           cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        found = frame_count(path)
        if found != last - first:
            raise RuntimeError(f'part {i}: {found} frames, expected {last-first}')
        print(f'part {i}: complete {found} frames in {time.monotonic()-start:.1f}s', flush=True)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(part, range(parts)))
    listing = WORK / 'parts.txt'
    listing.write_text(''.join(f"file '{OUT / f'part-{i:02d}.mp4'}'\n" for i in range(parts)))
    master = OUT / 'A-World-Made-Gentle-1080p60.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-i', str(WORK / 'score.wav'), '-map', '0:v:0', '-map', '1:a:0',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', '62',
                    '-movflags', '+faststart', str(master)], check=True)
    if frame_count(master) != FRAMES:
        raise RuntimeError('Master frame count does not match 3720')
    review = OUT / 'A-World-Made-Gentle-review-720p60.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(master), '-vf', 'scale=1280:720',
                    '-c:v', 'libx264', '-threads', '2', '-preset', 'fast', '-crf', '24', '-maxrate', '3M', '-bufsize', '6M',
                    '-c:a', 'aac', '-b:a', '128k', '-t', '62', '-movflags', '+faststart', str(review)], check=True)
    if frame_count(review) != FRAMES:
        raise RuntimeError('Review frame count does not match 3720')
    print(str(master), flush=True)
    print(str(review), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--parts', type=int, default=8)
    args = p.parse_args()
    if not 1 <= args.workers <= 4 or not 1 <= args.parts <= 32:
        p.error('workers must be 1..4 and parts 1..32')
    run(args.workers, args.parts)
