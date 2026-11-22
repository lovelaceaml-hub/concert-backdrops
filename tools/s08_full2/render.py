"""Render song 08's version 2 backdrop (tools/s08_full2/s08_full2.py) on the pinned Revision 3 engine.

    python tools/nine_colours_minor/prepare.py                       # once: the pinned engine and Claude Final v1
    python tools/s08_full2/render.py --stills 4,64,92 --scale .5     # stills (PNG) at video seconds
    python tools/s08_full2/render.py --range 0 1500 --out part.mp4   # frames [a, b) at 60 fps, silent H.264

The song audio is never in the repository: S08_AUDIO points to the reference recording (default
work/s08_full2/s08.mp3) and FEATURES to engine/analyze.py's features of it (work/s08_full2/features.npz).
Render in the cloud only, never on the Mac. No em dash or en dash anywhere in this file.
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

WORK = ROOT / 'work/s08_full2'
FPS = 60
OPEN_END = 9.0          # the opening is fully readable from frame 0 to 7.8 s, then dissolves by 9.0 s
SIG_IN = 8.4            # the signature fades in under the dissolving opening and stays to the last frame


def load():
    if not (SNAPSHOT / 'engine/render.py').exists():
        raise SystemExit('Run tools/nine_colours_minor/prepare.py first.')
    os.environ.update(SONG='s08_full2', OUT_FPS=str(FPS), OUT_RES='1080p',
                      FEATURES=str(WORK / 'features.npz'),
                      AUDIO=os.environ.get('S08_AUDIO', str(WORK / 's08.mp3')),
                      LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS=os.environ.get('LP_NUM_THREADS', '1'),
                      OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                      NUMBA_CACHE_DIR=str(WORK / 'numba'), MESA_SHADER_CACHE_DIR=str(WORK / 'mesa'),
                      P3D_CACHE=str(WORK / 'p3d_cache'))
    sys.path.insert(0, str(SNAPSHOT / 'engine'))
    sys.path.insert(0, str(HERE))
    import songs
    songs.__path__.append(str(HERE))
    import song
    import p3d
    p3d.__path__.append(str(ROOT / 'engine/p3d'))   # brand (the logo), brand_symbols, brand_hearts
    spec = importlib.util.spec_from_file_location('reference_renderer', SNAPSHOT / 'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    song.TITLES = dict(opening=dict(t_end=OPEN_END, dissolve=1.2, build=0, y=.42, palette='night'),
                       signature=dict(windows=[(SIG_IN, 1e9, 'tl', 'night')], fade=1.0))
    spec = importlib.util.spec_from_file_location('titles', ROOT / 'engine/titles.py')
    titles = importlib.util.module_from_spec(spec)
    sys.modules['titles'] = titles
    spec.loader.exec_module(titles)
    from lockup import Lockup

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = Lockup(self)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            if self.cards.overlay(t):
                return self.f_out.read(components=3)
            return data

    return Renderer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', default='')
    ap.add_argument('--outdir', type=Path, default=ROOT / 'out/s08_full2/stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='12')
    args = ap.parse_args()
    Renderer = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(t, i=None):
        return renderer.out.frame(t, int(round(t * FPS)) if i is None else i)

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            start = time.time()
            data = frame(t)
            Image.frombytes('RGB', (w, h), data).save(args.outdir / f't{t:07.2f}.png')
            print(f'{t:.3f}: {time.time() - start:.1f} s', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file.mp4')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
           '-c:v', 'libx264', '-threads', '1', '-preset', 'medium', '-crf', args.crf,
           '-pix_fmt', 'yuv420p', '-g', '120', '-bf', '2', '-color_primaries', 'bt709',
           '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i / FPS, i))
            if (i - args.range[0]) % 120 == 0:
                print(f'frame {i}: {time.time() - start:.0f} s', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('Encoder failed')
    print(f'done {args.out}: {time.time() - start:.0f} s', flush=True)


if __name__ == '__main__':
    main()
