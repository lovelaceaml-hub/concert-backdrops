"""Render song 04's full backdrop on the pinned Revision 3 engine (CPU only, in this cloud session).

    python tools/s04_full/render.py --stills 20,45,85 --scale 0.5 --outdir work/s04/stills
    python tools/s04_full/render.py --range 0 900 --out work/s04/parts/p00.mp4

Needs tools/nine_colours_minor/prepare.py (the pinned engine and Claude Final v1 snapshots), fonts, and
the measured audio features at work/s04/features.npz (tools/s04_full/prepare.sh). Frame i is song time
i / 30 s. Video only; tools/s04_full/export.py joins the parts and adds the music.
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

FPS = 30
WORK = ROOT / 'work/s04'


def load():
    if not (SNAPSHOT / 'engine/render.py').exists():
        raise SystemExit('Run tools/nine_colours_minor/prepare.py first.')
    os.environ.update(SONG='song04', OUT_FPS=str(FPS), OUT_RES='1080p', FEATURES=str(WORK / 'features.npz'),
                      AUDIO=str(WORK / 's04.wav'), LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1',
                      OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', NUMBA_CACHE_DIR=str(WORK / 'numba'),
                      MESA_SHADER_CACHE_DIR=str(WORK / 'mesa'))
    sys.path.insert(0, str(SNAPSHOT / 'engine'))
    sys.path.insert(1, str(HERE))
    import songs
    songs.__path__.append(str(HERE))            # songs.song04 is this folder's song04.py
    import p3d
    p3d.__path__.append(str(ROOT / 'engine/p3d'))
    import song  # noqa: F401  (imports songs.song04)
    spec = importlib.util.spec_from_file_location('reference_renderer', SNAPSHOT / 'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
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
    ap.add_argument('--outdir', type=Path, default=WORK / 'stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--crf', default='14')
    args = ap.parse_args()
    Renderer = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(i):
        return renderer.out.frame(i / FPS, i)

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            start = time.process_time()
            data = frame(int(round(t * FPS)))
            Image.frombytes('RGB', (w, h), data).save(args.outdir / f't{t:07.2f}.png')
            print(f'{t:.3f}: {time.process_time() - start:.1f} CPU seconds', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file.mp4')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # a lossless-quality intermediate (CRF 14); the master is encoded once at CRF 18 by export.py
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS),
           '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-c:v', 'libx264', '-threads', '1',
           '-preset', 'medium', '-crf', args.crf, '-pix_fmt', 'yuv420p', '-g', '60', '-color_primaries', 'bt709',
           '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i))
            done = i - args.range[0] + 1
            if done % 30 == 0:
                el = time.time() - start
                print(f'frame {i}: {done} done, {el / done:.2f} s/frame', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('Encoder failed')
    print(f'done {args.out}: {time.time() - start:.0f} s', flush=True)


if __name__ == '__main__':
    main()
