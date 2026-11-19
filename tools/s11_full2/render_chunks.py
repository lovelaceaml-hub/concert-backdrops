"""Render song 11 v2 in chunks of 300 frames (5 s), as a work queue several processes (or machines) can share.

    python tools/s11_full2/render_chunks.py --order 15-26,0-14,27-54 --parts work/s11_full2/parts

Each chunk c covers frames 300c to 300c+299 (the last chunk ends at frame 16499). A process claims a chunk by
creating the folder <parts>/locks/cNN (atomic), renders it to <parts>/cNN.mp4 (written as .tmp first, then
renamed), and moves on. A chunk whose part or lock exists is skipped, so start as many processes as there are
cores. To hand chunks to another machine, create their lock folders here first. Join the parts in order with
ffmpeg's concat demuxer (-c copy): every part starts on a keyframe.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CHUNK = 300
NFRAMES = 16500
NCHUNK = (NFRAMES + CHUNK - 1) // CHUNK


def order(spec):
    out = []
    for part in spec.split(','):
        a, _, b = part.partition('-')
        out += list(range(int(a), int(b or a) + 1))
    return [c for c in out if 0 <= c < NCHUNK]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--order', default=f'0-{NCHUNK - 1}')
    ap.add_argument('--parts', type=Path, required=True)
    ap.add_argument('--scale', default='1')
    args = ap.parse_args()
    (args.parts / 'locks').mkdir(parents=True, exist_ok=True)
    for c in order(args.order):
        part = args.parts / f'c{c:02d}.mp4'
        if part.exists():
            continue
        try:
            os.mkdir(args.parts / 'locks' / f'c{c:02d}')
        except FileExistsError:
            continue
        a, b = c * CHUNK, min((c + 1) * CHUNK, NFRAMES)
        tmp = args.parts / f'c{c:02d}.tmp.mp4'
        print(f'chunk {c}: frames {a} to {b - 1}', flush=True)
        r = subprocess.run([sys.executable, str(HERE / 'render.py'), '--range', str(a), str(b), '--out', str(tmp),
                            '--scale', args.scale])
        if r.returncode != 0:
            print(f'chunk {c} FAILED', flush=True)
            os.rmdir(args.parts / 'locks' / f'c{c:02d}')
            continue
        tmp.rename(part)
        print(f'chunk {c} done', flush=True)


if __name__ == '__main__':
    main()
