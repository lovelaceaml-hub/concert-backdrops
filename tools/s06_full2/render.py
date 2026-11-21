"""Render the song 06 backdrop v2: stills or a range of frames (native 60 fps, 1920x1080), CPU only.

    python tools/s06_full2/render.py --stills 0,12,44 --scale 0.5 --outdir work/s06_full2/stills
    python tools/s06_full2/render.py --range 0 600 --out work/s06_full2/parts/p00.mkv

Times given to --stills and frame numbers given to --range are LIVE (stage video) times: frame i is at i / 60 s
of the 152.0 s stage video. Each is mapped onto the reference clock of the song module (ref_time): the music
part is scaled to the live length, the 15 s hold runs at normal speed.

The pinned Film 10 engine (d928ff9) draws the world; Claude Final v1 (f43f451) gives the words; the song
module is tools/s06_full2/s06_full2_song.py; the opening and signature are tools/s06_full2/cards_s06v2.py.
No em dash or en dash anywhere in this file.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools/nine_colours_minor'))
from prepare import SNAPSHOT  # noqa: E402

WORK = ROOT / 'work/s06_full2'
FPS = 60


def load():
    if not (SNAPSHOT / 'engine/render.py').exists() or not (WORK / 'features.npz').exists():
        raise SystemExit('Run tools/s06_full2/prepare.py first.')
    os.environ.update(SONG='s06_full2_song', OUT_FPS='60', OUT_RES='1080p', FEATURES=str(WORK / 'features.npz'),
                      AUDIO=str(WORK / 's06.m4a'), LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1',
                      OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', NUMBA_CACHE_DIR=str(WORK / 'numba'),
                      MESA_SHADER_CACHE_DIR=str(WORK / 'mesa'))
    sys.path.insert(0, str(SNAPSHOT / 'engine'))
    sys.path.insert(1, str(HERE))
    import songs
    songs.__path__.append(str(HERE))
    import song  # noqa: F401  (imports songs.s06_full2_song)
    import p3d
    p3d.__path__.append(str(ROOT / 'engine/p3d'))          # the brand logo for the signature
    spec = importlib.util.spec_from_file_location('reference_renderer', SNAPSHOT / 'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    spec = importlib.util.spec_from_file_location('titles', ROOT / 'engine/titles.py')
    titles = importlib.util.module_from_spec(spec)
    sys.modules['titles'] = titles
    spec.loader.exec_module(titles)
    from cards_s06v2 import SongCards

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = SongCards(self)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            if self.cards.overlay(t):
                return self.f_out.read(components=3)
            return data

    return Renderer, sys.modules['songs.s06_full2_song'].ref_time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', default='')
    ap.add_argument('--outdir', type=Path, default=WORK / 'stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='12')
    ap.add_argument('--every', type=int, default=1, help='stills: also sequences A:B:step in frames')
    args = ap.parse_args()
    Renderer, ref_time = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(i):
        t = ref_time(i / FPS)
        return renderer.out.frame(t, i)

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for item in args.stills.split(','):
            if ':' in item:
                a, b, s = (float(x) for x in item.split(':'))
                frames = [int(round(x * FPS)) for x in __import__('numpy').arange(a, b, s)]
            else:
                frames = [int(round(float(item) * FPS))]
            for i in frames:
                start = time.process_time()
                data = frame(i)
                Image.frombytes('RGB', (w, h), data).save(args.outdir / f't{i / FPS:07.2f}.png')
                print(f'{i / FPS:.2f}: {time.process_time() - start:.2f} CPU s', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS),
           '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-c:v', 'libx264', '-threads', '1',
           '-preset', 'medium', '-crf', args.crf, '-pix_fmt', 'yuv420p', '-g', '60', '-color_primaries', 'bt709',
           '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.process_time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i))
            if (i - args.range[0]) % 60 == 0:
                print(f'frame {i}: {time.process_time() - start:.0f} CPU s', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('encoder failed')
    print(f'done {args.out}: {time.process_time() - start:.0f} CPU s', flush=True)


if __name__ == '__main__':
    main()
