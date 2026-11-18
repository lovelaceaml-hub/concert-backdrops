"""Render stills or a frame range of the full song 01 backdrop (30 fps, 1920x1080).

    python tools/backdrop_s01/s01_prepare.py
    python tools/backdrop_s01/s01_render.py --stills 3,12,22 --scale 0.5 --outdir <dir>
    python tools/backdrop_s01/s01_render.py --range 0 600 --out <part.mp4>

Cloud only (AGENTS.md). Stills, frames and videos never go into the repository.
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
from s01_prepare import WORK, AUDIO  # noqa: E402

FPS = 30


def load():
    if not (SNAPSHOT / 'engine/render.py').exists() or not (WORK / 'features.npz').exists():
        raise SystemExit('Run tools/backdrop_s01/s01_prepare.py first.')
    os.environ.update(SONG='s01_full', OUT_FPS=str(FPS), OUT_RES='1080p', FEATURES=str(WORK / 'features.npz'),
                      AUDIO=str(AUDIO), LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1',
                      OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                      NUMBA_CACHE_DIR=str(WORK / 'numba'), MESA_SHADER_CACHE_DIR=str(WORK / 'mesa'))
    sys.path.insert(0, str(SNAPSHOT / 'engine'))
    import songs
    songs.__path__.append(str(HERE / 'songs'))
    import p3d
    p3d.__path__.append(str(ROOT / 'engine/p3d'))
    import song
    song.TITLES = dict(signature=dict(windows=[(21.0, 300.0, 'bl', 'night')], fade=1.2))
    spec = importlib.util.spec_from_file_location('titles', ROOT / 'engine/titles.py')
    titles = importlib.util.module_from_spec(spec)
    sys.modules['titles'] = titles
    spec.loader.exec_module(titles)
    spec = importlib.util.spec_from_file_location('reference_renderer', SNAPSHOT / 'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)

    class Small(titles.Titles):
        def _signature(self, corner, pal):
            scale = self.s
            try:
                self.s *= .65
                return super()._signature(corner, pal)
            finally:
                self.s = scale

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = Small(self)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            if self.cards.overlay(t):
                return self.f_out.read(components=3)
            return data

    return Renderer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', default='')
    ap.add_argument('--outdir', type=Path, default=ROOT / 'out/s01_full/stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='18')
    args = ap.parse_args()
    Renderer = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(t):
        return renderer.out.frame(t, int(round(t * FPS)))

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            start = time.process_time()
            Image.frombytes('RGB', (w, h), frame(t)).save(args.outdir / f't{t:07.2f}.png')
            print(f'{t:.3f}: {time.process_time() - start:.3f} CPU seconds', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file.mp4')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS),
           '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-c:v', 'libx264', '-threads', '2',
           '-preset', 'fast', '-crf', args.crf, '-pix_fmt', 'yuv420p', '-g', str(FPS), '-bf', '2',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
           '-movflags', '+faststart', str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.process_time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i / FPS))
            if (i - args.range[0]) % 150 == 0:
                print(f'frame {i}: {time.process_time() - start:.1f} CPU s', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('Encoder failed')
    print(f'done {args.out}', flush=True)


if __name__ == '__main__':
    main()
