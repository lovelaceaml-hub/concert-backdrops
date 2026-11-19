"""Render song 11's full backdrop (version 2): stills or a range of frames, on the pinned Revision 3 engine.

    python tools/s11_full2/render.py --stills 0,53.78,201.73 --scale 0.5 --outdir work/s11_full2/stills
    python tools/s11_full2/render.py --range 0 600 --out work/s11_full2/parts/p00000.mp4

Frames are 60 fps; frame i shows song time i/60 (0 is the first sample of the recording). Everything is a pure
function of time, so ranges render in parallel in any order. Prepare first: tools/s11_full2/s11_prepare.py.
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
from s11_prepare import WORK, FPS, TOTAL  # noqa: E402
from s11_prepare import r3  # noqa: E402


def load(fps=FPS):
    snap = r3.SNAPSHOT
    if not (snap / 'engine/render.py').exists() or not (WORK / 'features.npz').exists():
        raise SystemExit('Run tools/s11_full2/s11_prepare.py first.')
    os.environ.update(SONG='s11_full2', OUT_FPS=str(fps), OUT_RES='1080p',
                      FEATURES=str(WORK / 'features.npz'), AUDIO=str(WORK / 'score.wav'),
                      LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS=os.environ.get('LP_NUM_THREADS', '1'),
                      OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                      NUMBA_CACHE_DIR=str(WORK / 'numba'), MESA_SHADER_CACHE_DIR=str(WORK / 'mesa'),
                      P3D_CACHE=os.environ.get('S11_CACHE', str(WORK / 'p3dcache')))
    sys.path.insert(0, str(snap / 'engine'))
    import songs
    songs.__path__.append(str(HERE))            # songs.s11_full2 is tools/s11_full2/s11_full2.py
    import p3d
    p3d.__path__.append(str(ROOT / 'engine/p3d'))   # the brand modules (globe, logo, hearts) of the repo
    import song  # noqa: F401  (loads the song module)
    spec = importlib.util.spec_from_file_location('reference_renderer', snap / 'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    spec = importlib.util.spec_from_file_location('titles', ROOT / 'engine/titles.py')
    titles = importlib.util.module_from_spec(spec)
    sys.modules['titles'] = titles
    spec.loader.exec_module(titles)
    from s11_cards import Cards

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
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='14')
    ap.add_argument('--fps', type=int, default=FPS, help='60 for the final, 30 for drafts')
    args = ap.parse_args()
    fps = args.fps
    Renderer = load(fps)
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(t):
        return renderer.out.frame(t, int(round(t * fps)))

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            start = time.process_time()
            data = frame(t)
            Image.frombytes('RGB', (w, h), data).save(args.outdir / f't{t:07.2f}.png')
            print(f'{t:.3f}: {time.process_time() - start:.2f} CPU s', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file.mp4')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{w}x{h}', '-r', str(fps), '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
           '-c:v', 'libx264', '-threads', '1', '-preset', 'medium', '-crf', args.crf,
           '-pix_fmt', 'yuv420p', '-g', str(fps * 2), '-color_primaries', 'bt709',
           '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i / fps))
            if (i - args.range[0]) % (5 * fps) == 0:
                print(f'frame {i}: {time.time() - start:.1f} s', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('Encoder failed')
    print(f'done {args.out}: {time.time() - start:.1f} s', flush=True)


if __name__ == '__main__':
    main()
