"""Full render of the song 06 backdrop in this session: frame ranges in parallel on every CPU core, joined
losslessly, then muxed with the score (music, then silence for the calm hold).

    python tools/s06_full/export.py [--workers 4] [--parts 16]

Outputs (untracked, never committed): work/s06_full/out/
    06 Heavenly Mother Tells Us to Be Grains - Backdrop 1080p30.mp4   H.264 CRF 18, yuv420p, AAC 320k, faststart
    06 Heavenly Mother Tells Us to Be Grains - Backdrop share 720p.mp4   under 25 MB
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / 'work/s06_full'
NFRAMES = 4496
NAME = '06 Heavenly Mother Tells Us to Be Grains - Backdrop'


def run_part(k, a, b):
    out = WORK / 'parts' / f'p{k:02d}.mkv'
    if out.exists() and (WORK / 'parts' / f'p{k:02d}.ok').exists():
        return out
    log = open(WORK / 'parts' / f'p{k:02d}.log', 'w')
    subprocess.run([sys.executable, str(HERE / 'render.py'), '--range', str(a), str(b), '--out', str(out),
                    '--crf', '10'], stdout=log, stderr=subprocess.STDOUT, check=True)
    (WORK / 'parts' / f'p{k:02d}.ok').write_text(f'{a} {b}\n')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=os.cpu_count())
    ap.add_argument('--parts', type=int, default=16)
    args = ap.parse_args()
    (WORK / 'parts').mkdir(parents=True, exist_ok=True)
    (WORK / 'out').mkdir(parents=True, exist_ok=True)
    edges = [round(NFRAMES * k / args.parts) for k in range(args.parts + 1)]
    with ThreadPoolExecutor(args.workers) as pool:
        parts = list(pool.map(lambda k: run_part(k, edges[k], edges[k + 1]), range(args.parts)))
    lst = WORK / 'parts' / 'list.txt'
    lst.write_text(''.join(f"file '{p}'\n" for p in parts))
    joined = WORK / 'parts' / 'joined.mkv'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy',
                    str(joined)], check=True)
    master = WORK / 'out' / f'{NAME} 1080p30.mp4'
    color = ['-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(joined), '-i', str(WORK / 'score.wav'),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
                    '-pix_fmt', 'yuv420p', '-r', '30', '-g', '60', *color, '-c:a', 'aac', '-b:a', '320k',
                    '-ar', '48000', '-shortest', '-movflags', '+faststart', str(master)], check=True)
    share = WORK / 'out' / f'{NAME} share 720p.mp4'
    # about 22 MB for 150 s: 1.05 Mb/s video plus 128 kb/s audio, two passes
    vb = '1050k'
    common = ['-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-b:v', vb,
              '-pix_fmt', 'yuv420p', '-r', '30', *color]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(master), *common, '-pass', '1',
                    '-passlogfile', str(WORK / 'parts/x264'), '-an', '-f', 'mp4', os.devnull], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(master), *common, '-pass', '2',
                    '-passlogfile', str(WORK / 'parts/x264'), '-c:a', 'aac', '-b:a', '128k',
                    '-movflags', '+faststart', str(share)], check=True)
    for f in (master, share):
        print(f, f.stat().st_size)


if __name__ == '__main__':
    main()
