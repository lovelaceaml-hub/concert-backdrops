"""Render song 09's full backdrop in parallel ranges, join it with the soundtrack, and make the two copies.

    python tools/s09_full2/export.py --workers 4 --parts 16

Parts are near-lossless intermediates in out/s09_full2/parts/ (reused when already complete). The three
deliveries are encoded from the joined parts: the stage file (silent, H.264 CRF 16, yuv420p, faststart,
1920x1080, 60 fps), the review file (the same picture with the music, CRF 20, AAC 320k) and the phone copy
(1280x720, 60 fps, with music, under 25 MB). Nothing here goes into git.
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

OUT = ROOT / 'out/s09_full2'
NAME = "09 Let's Save the World - Backdrop v2"


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
    color = ['-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']
    vf = ['-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p']
    stage = OUT / f'{NAME} - stage 1080p60.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-map', '0:v:0',
                    *vf, '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-threads', '4', '-r', str(FPS), *color,
                    '-an', '-t', f'{TOTAL}', '-movflags', '+faststart', str(stage)], check=True)
    if frames(stage) != FRAMES:
        raise RuntimeError(f'stage file has {frames(stage)} frames, expected {FRAMES}')
    review = OUT / f'{NAME} - review 1080p60.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-i', str(WORK / 'score.wav'), '-map', '0:v:0', '-map', '1:a:0', *vf,
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-threads', '4', '-r', str(FPS), *color,
                    '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', f'{TOTAL}',
                    '-movflags', '+faststart', str(review)], check=True)
    if frames(review) != FRAMES:
        raise RuntimeError(f'review file has {frames(review)} frames, expected {FRAMES}')
    phone = OUT / f'{NAME} - phone 720p60.mp4'
    # under 25 MB: two-pass at about 0.59 Mbit/s video plus 80 kbit/s audio, tuned so the slow calm passages keep
    # their small movements (no decimated, held blocks)
    vf = ['-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '590k',
          '-x264-params', 'aq-mode=3:no-dct-decimate=1:deadzone-inter=8:deadzone-intra=8', '-pix_fmt', 'yuv420p',
          '-threads', '8', *color]
    log = OUT / 'phone2pass'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(review), *vf, '-pass', '1', '-passlogfile', str(log),
                    '-an', '-f', 'null', '/dev/null'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(review), *vf, '-pass', '2', '-passlogfile', str(log),
                    '-c:a', 'aac', '-b:a', '80k', '-movflags', '+faststart', str(phone)], check=True)
    if phone.stat().st_size >= 25 * 1000 * 1000:
        raise RuntimeError('phone copy is not under 25 MB')
    if frames(phone) != FRAMES:
        raise RuntimeError('phone copy frame count is wrong')
    for f in (stage, review, phone):
        print(f, f.stat().st_size)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--parts', type=int, default=16)
    p.add_argument('--join-only', action='store_true')
    args = p.parse_args()
    paths = [OUT / 'parts' / f'part-{i:02d}.mkv' for i in range(args.parts)] if args.join_only \
        else render(args.workers, args.parts)
    join(paths)
