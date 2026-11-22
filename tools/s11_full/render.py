"""Render song 11's full backdrop (stills or a range of frames) on the pinned Revision 3 engine.

    python tools/s11_full/render.py --stills 10,60,120 --scale 0.5 --outdir work/s11_full/stills
    python tools/s11_full/render.py --range 0 900 --out work/s11_full/parts/p00.mp4

Frames are 30 fps; frame i shows song time i/30 (0 is the first sample of the audio file). Everything is a
pure function of time, so ranges can run in parallel in any order.
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
import s11_prepare as s11prep  # noqa: E402,F401
from s11_prepare import r3  # noqa: E402


def load():
    snap = r3.SNAPSHOT
    if not (snap / 'engine/render.py').exists():
        raise SystemExit('Run tools/s11_full/s11_prepare.py first.')
    os.environ.update(SONG='s11_backdrop', OUT_FPS=str(FPS), OUT_RES='1080p',
                      FEATURES=str(WORK / 'features.npz'), AUDIO=str(WORK / 'audio.wav'),
                      LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1',
                      OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                      NUMBA_CACHE_DIR=str(WORK / 'numba'), MESA_SHADER_CACHE_DIR=str(WORK / 'mesa'),
                      P3D_CACHE=str(WORK / 'p3dcache'))
    sys.path.insert(0, str(snap / 'engine'))
    import songs
    songs.__path__.append(str(HERE))            # songs.s11_backdrop is tools/s11_full/s11_backdrop.py
    import p3d
    p3d.__path__.append(str(ROOT / 'engine/p3d'))
    import song  # noqa: F401  (loads the song module)
    spec = importlib.util.spec_from_file_location('reference_renderer', snap / 'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    spec = importlib.util.spec_from_file_location('titles', ROOT / 'engine/titles.py')
    titles = importlib.util.module_from_spec(spec)
    sys.modules['titles'] = titles
    spec.loader.exec_module(titles)
    return old.Renderer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', default='')
    ap.add_argument('--outdir', type=Path, default=WORK / 'stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='14')
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
            start = time.time()
            data = frame(t)
            Image.frombytes('RGB', (w, h), data).save(args.outdir / f't{t:07.2f}.png')
            print(f'{t:.3f}: {time.time() - start:.2f} s', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file.mp4')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
           '-c:v', 'libx264', '-threads', '1', '-preset', 'medium', '-crf', args.crf,
           '-pix_fmt', 'yuv420p', '-g', str(FPS * 2), '-color_primaries', 'bt709',
           '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i / FPS))
            if (i - args.range[0]) % 150 == 0:
                print(f'frame {i}: {time.time() - start:.1f} s', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('Encoder failed')
    print(f'done {args.out}: {time.time() - start:.1f} s', flush=True)


if __name__ == '__main__':
    main()
