"""Render song 08's full backdrop (tools/s08_full/s08_full.py) on the pinned Revision 3 engine.

    python tools/nine_colours_minor/prepare.py                  # once: the pinned engine and Claude Final v1
    python tools/s08_full/render.py --stills 20,60 --scale .5   # stills (PNG) at song seconds
    python tools/s08_full/render.py --range 0 600 --out part.mp4   # frames [a, b) at 30 fps, silent H.264

The song audio is never in the repository: S08_AUDIO points to the recording (default work/s08_full/s08.mp3)
and FEATURES to engine/analyze.py's features of it (work/s08_full/features.npz). Render in the cloud only.
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

WORK = ROOT / 'work/s08_full'
FPS = 30


def load():
    if not (SNAPSHOT / 'engine/render.py').exists():
        raise SystemExit('Run tools/nine_colours_minor/prepare.py first.')
    os.environ.update(SONG='s08_full', OUT_FPS=str(FPS), OUT_RES='1080p',
                      FEATURES=str(WORK / 'features.npz'),
                      AUDIO=os.environ.get('S08_AUDIO', str(WORK / 's08.mp3')),
                      LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1',
                      OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                      NUMBA_CACHE_DIR=str(WORK / 'numba'), MESA_SHADER_CACHE_DIR=str(WORK / 'mesa'),
                      P3D_CACHE=str(WORK / 'p3d_cache'))
    sys.path.insert(0, str(SNAPSHOT / 'engine'))
    import songs
    songs.__path__.append(str(HERE))
    import song  # noqa: F401  (imports songs.s08_full)
    import p3d
    p3d.__path__.append(str(ROOT / 'engine/p3d'))   # brand (the logo of the signature), as Revision 3 does
    spec = importlib.util.spec_from_file_location('reference_renderer', SNAPSHOT / 'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    song.TITLES = dict(signature=dict(windows=[(12.6, 1e9, 'bl', 'night')], fade=1.2))
    spec = importlib.util.spec_from_file_location('titles', ROOT / 'engine/titles.py')
    titles = importlib.util.module_from_spec(spec)
    sys.modules['titles'] = titles
    spec.loader.exec_module(titles)
    from cards import Cards

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = Cards(self)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            if self.cards.overlay(t):
                return self.f_out.read(components=3)
            return data

    return Renderer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', default='')
    ap.add_argument('--outdir', type=Path, default=ROOT / 'out/s08_full/stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='14')
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
            start = time.process_time()
            data = frame(t)
            Image.frombytes('RGB', (w, h), data).save(args.outdir / f't{t:07.2f}.png')
            print(f'{t:.3f}: {time.process_time() - start:.3f} CPU seconds', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file.mp4')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
           '-c:v', 'libx264', '-threads', '1', '-preset', 'medium', '-crf', args.crf,
           '-pix_fmt', 'yuv420p', '-g', '60', '-bf', '2', '-color_primaries', 'bt709',
           '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.process_time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i / FPS, i))
            if (i - args.range[0]) % 60 == 0:
                print(f'frame {i}: {time.process_time() - start:.1f} CPU s', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('Encoder failed')
    print(f'done {args.out}: {time.process_time() - start:.1f} CPU seconds', flush=True)


if __name__ == '__main__':
    main()
