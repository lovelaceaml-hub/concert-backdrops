"""Render song 09's full backdrop in parallel ranges, join it with the soundtrack, and make the two copies.

    python tools/s09_full/export.py --workers 4 --parts 16

Parts are near-lossless intermediates in out/s09_full/parts/ (reused when already complete). The master is
encoded once from the joined parts: H.264 CRF 18, yuv420p, AAC 320k, faststart, 1920x1080, 30 fps. The share
copy is 1280x720 and kept under 25 MB. Nothing here goes into git.
No em dash or en dash anywhere in this file.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools/nine_colours_minor'))
sys.path.insert(0, str(HERE))
from setup_s09 import WORK, FRAMES, FPS, TOTAL  # noqa: E402

OUT = ROOT / 'out/s09_full'
NAME = "09 Let's Save the World - Concert Backdrop"


def frames(path):
    if not path.exists():
        return 0
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_packets', '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
    s = r.stdout.strip()
    return int(s) if r.returncode == 0 and s.isdigit() else 0


def render(workers, parts):
    (OUT / 'parts').mkdir(parents=True, exist_ok=True)

    def part(i):
        a, b = FRAMES * i // parts, FRAMES * (i + 1) // parts
        path = OUT / 'parts' / f'part-{i:02d}.mkv'
        if frames(path) == b - a:
            print(f'part {i}: reusing {b - a} frames', flush=True)
            return
        t0 = time.monotonic()
        with (OUT / 'parts' / f'part-{i:02d}.log').open('w') as log:
            subprocess.run([sys.executable, str(HERE / 'render.py'), '--range', str(a), str(b), '--out', str(path)],
                           cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        n = frames(path)
        if n != b - a:
            raise RuntimeError(f'part {i}: {n} frames, expected {b - a}')
        print(f'part {i}: {n} frames in {time.monotonic() - t0:.0f} s', flush=True)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(part, range(parts)))
    return [OUT / 'parts' / f'part-{i:02d}.mkv' for i in range(parts)]


def join(paths):
    listing = OUT / 'parts.txt'
    listing.write_text(''.join(f"file '{p}'\n" for p in paths))
    master = OUT / f'{NAME} (1080p master).mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-i', str(WORK / 'score.wav'), '-map', '0:v:0', '-map', '1:a:0',
                    '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-threads', '4', '-r', str(FPS),
                    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
                    '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', f'{TOTAL}',
                    '-movflags', '+faststart', str(master)], check=True)
    if frames(master) != FRAMES:
        raise RuntimeError(f'master has {frames(master)} frames, expected {FRAMES}')
    share = OUT / f'{NAME} (720p share).mp4'
    # about 22 MB: 290.7 s at 0.5 Mbit/s video plus 96 kbit/s audio
    for rate in ('520k', '440k', '360k'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(master), '-vf', 'scale=1280:720:flags=lanczos',
                        '-c:v', 'libx264', '-preset', 'slow', '-b:v', rate, '-maxrate', '900k', '-bufsize', '2M',
                        '-pix_fmt', 'yuv420p', '-threads', '4', '-c:a', 'aac', '-b:a', '96k',
                        '-movflags', '+faststart', str(share)], check=True)
        if share.stat().st_size < 25 * 1000 * 1000:
            break
    if frames(share) != FRAMES:
        raise RuntimeError('share copy frame count is wrong')
    print(master)
    print(share)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--parts', type=int, default=16)
    p.add_argument('--join-only', action='store_true')
    args = p.parse_args()
    paths = [OUT / 'parts' / f'part-{i:02d}.mkv' for i in range(args.parts)] if args.join_only \
        else render(args.workers, args.parts)
    join(paths)
