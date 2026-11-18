"""Render song 10's full backdrop (stills or a frame range) on the pinned Revision 3 engine, 30 fps.

    python tools/s10_full/s10_prepare.py --audio /path/to/s10.m4a     # once: snapshots, features, soundtrack
    python tools/s10_full/render.py --stills 5,40,60 --scale .5 --outdir out/s10_full/stills
    python tools/s10_full/render.py --range 0 600 --out out/s10_full/parts/p000.mp4

Frame i shows song time i / 30. The song module is tools/s10_full/s10_song.py.
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
sys.path.insert(0, str(HERE))
from prepare import SNAPSHOT  # noqa: E402  (the pinned engine d928ff9, restored by the R3 prepare)

WORK = ROOT / 'work/s10_full'
FPS = 30


def load():
    if not (SNAPSHOT / 'engine/render.py').exists() or not (WORK / 'features.npz').exists():
        raise SystemExit('Run tools/s10_full/s10_prepare.py first.')
    os.environ.update(SONG='s10_song', OUT_FPS='30', OUT_RES='1080p', FEATURES=str(WORK / 'features.npz'),
                      LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                      OMP_NUM_THREADS='1', NUMBA_CACHE_DIR=str(WORK / 'numba'),
                      MESA_SHADER_CACHE_DIR=str(WORK / 'mesa'))
    sys.path.insert(0, str(SNAPSHOT / 'engine'))
    import songs
    songs.__path__.append(str(HERE))
    import p3d
    p3d.__path__.append(str(ROOT / 'engine/p3d'))
    import song
    spec = importlib.util.spec_from_file_location('reference_renderer', SNAPSHOT / 'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    spec = importlib.util.spec_from_file_location('titles', ROOT / 'engine/titles.py')
    titles = importlib.util.module_from_spec(spec)
    sys.modules['titles'] = titles
    spec.loader.exec_module(titles)
    from titles_s10 import make_cards
    Cards = make_cards(titles)

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = Cards(self)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            if self.cards.overlay(t):
                return self.f_out.read(components=3)
            return data

    return Renderer, song


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', default='')
    ap.add_argument('--outdir', type=Path, default=ROOT / 'out/s10_full/stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='14')
    args = ap.parse_args()
    Renderer, song = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(t):
        return renderer.out.frame(t, int(round(t * FPS)))

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            start = time.process_time()
            data = frame(t)
            Image.frombytes('RGB', (w, h), data).save(args.outdir / f't{t:07.2f}.png')
            print(f'{t:.3f}: {time.process_time() - start:.1f} CPU seconds', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file.mp4')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # a lossless-quality intermediate part (re-encoded once in the final join)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}',
           '-r', str(FPS), '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
           '-c:v', 'libx264', '-threads', '1', '-preset', 'medium', '-crf', args.crf, '-pix_fmt', 'yuv420p',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
           str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i / FPS))
            if (i - args.range[0]) % 60 == 0:
                print(f'frame {i}: {time.time() - start:.0f} s', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('Encoder failed')
    print(f'done {args.out}: {time.time() - start:.0f} s', flush=True)


if __name__ == '__main__':
    main()
