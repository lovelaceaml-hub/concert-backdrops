"""Full render of the song 06 backdrop v2 in this cloud session: frame ranges in parallel on every CPU core,
joined losslessly, then encoded into the three deliverables.

    python tools/s06_full2/export.py [--workers 4] [--parts 16]

Outputs (untracked, never committed): work/s06_full2/out/
    06 Heavenly Mother Tells Us to Be Grains - Backdrop v2 - stage 1080p60.mp4    silent, H.264 CRF 16
    06 Heavenly Mother Tells Us to Be Grains - Backdrop v2 - review 1080p60.mp4   conformed music, CRF 20
    06 Heavenly Mother Tells Us to Be Grains - Backdrop v2 - phone 720p60.mp4     with music, under 25 MB
No em dash or en dash anywhere in this file.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / 'work/s06_full2'
FPS = 60
NFRAMES = 9120                       # 152.0 s: the live length 137.0 s plus the 15 s calm hold
NAME = '06 Heavenly Mother Tells Us to Be Grains - Backdrop v2'
COLOR = ['-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']


def run_part(k, a, b):
    out = WORK / 'parts' / f'p{k:02d}.mkv'
    ok = WORK / 'parts' / f'p{k:02d}.ok'
    if out.exists() and ok.exists():
        return out
    with open(WORK / 'parts' / f'p{k:02d}.log', 'w') as log:
        subprocess.run([sys.executable, str(HERE / 'render.py'), '--range', str(a), str(b), '--out', str(out),
                        '--crf', '10'], stdout=log, stderr=subprocess.STDOUT, check=True)
    ok.write_text(f'{a} {b}\n')
    return out


def ff(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=os.cpu_count())
    ap.add_argument('--parts', type=int, default=16)
    ap.add_argument('--encode-only', action='store_true')
    args = ap.parse_args()
    (WORK / 'parts').mkdir(parents=True, exist_ok=True)
    (WORK / 'out').mkdir(parents=True, exist_ok=True)
    edges = [round(NFRAMES * k / args.parts) for k in range(args.parts + 1)]
    if args.encode_only:
        parts = [WORK / 'parts' / f'p{k:02d}.mkv' for k in range(args.parts)]
    else:
        with ThreadPoolExecutor(args.workers) as pool:
            parts = list(pool.map(lambda k: run_part(k, edges[k], edges[k + 1]), range(args.parts)))
    lst = WORK / 'parts' / 'list.txt'
    lst.write_text(''.join(f"file '{p}'\n" for p in parts))
    joined = WORK / 'parts' / 'joined.mkv'
    ff('-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined)
    score = WORK / 'score.wav'
    stage = WORK / 'out' / f'{NAME} - stage 1080p60.mp4'
    ff('-i', joined, '-map', '0:v', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
       '-r', FPS, '-g', '120', *COLOR, '-movflags', '+faststart', stage)
    review = WORK / 'out' / f'{NAME} - review 1080p60.mp4'
    ff('-i', joined, '-i', score, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
       '-pix_fmt', 'yuv420p', '-r', FPS, '-g', '120', *COLOR, '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
       '-t', NFRAMES / FPS, '-movflags', '+faststart', review)
    phone = WORK / 'out' / f'{NAME} - phone 720p60.mp4'
    # about 23 MB for 152 s: 1.1 Mb/s video plus 96 kb/s audio, two passes
    common = ['-i', stage, '-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow',
              '-b:v', '1100k', '-pix_fmt', 'yuv420p', '-r', FPS, '-g', '120', *COLOR]
    ff(*common, '-pass', '1', '-passlogfile', WORK / 'parts/x264', '-an', '-f', 'mp4', os.devnull)
    ff(*common[:2], '-i', score, *common[2:], '-map', '0:v', '-map', '1:a', '-pass', '2',
       '-passlogfile', WORK / 'parts/x264', '-c:a', 'aac', '-b:a', '96k', '-ar', '48000', '-t', NFRAMES / FPS,
       '-movflags', '+faststart', phone)
    for f in (stage, review, phone):
        print(f, f.stat().st_size)


if __name__ == '__main__':
    main()
