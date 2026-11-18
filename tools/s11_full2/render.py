"""Render song 11's full backdrop, version 2 (stills or a frame range) on the pinned Revision 3 engine, 60 fps.

    python tools/s11_full2/s11_prepare.py --audio /path/to/s11.mp3     # once: snapshots, features, soundtrack
    python tools/s11_full2/render.py --stills 5,40,60 --scale .5 --outdir out/s11_full2/stills
    python tools/s11_full2/render.py --range 0 600 --out out/s11_full2/parts/p00000.mp4

Stage video time v (frame i shows v = i / 60) runs 0 to 275.0 s: the music part is exactly the live length
(260.0 s), then a 15 s calm hold. The story is timed on the reference recording's own clock (first sound 0.60 s,
last chord rung out 262.60 s), so the song module's times are reference seconds: song time = 0.60 + v * 262 / 260
during the music, then the hold continues 1:1 after 262.60. --stills takes VIDEO seconds.
The song module is tools/s11_full2/s11v2_song.py.
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

WORK = ROOT / 'work/s11_full2'
FPS = 60
LIVE = 260.0
REF0, REF1 = 0.60, 262.60


def song_time(v):
    """Reference-clock seconds for stage video seconds v."""
    return REF0 + v * (REF1 - REF0) / LIVE if v <= LIVE else REF1 + (v - LIVE)


def load():
    if not (SNAPSHOT / 'engine/render.py').exists() or not (WORK / 'features.npz').exists():
        raise SystemExit('Run tools/s11_full2/s11_prepare.py first.')
    os.environ.update(SONG='s11v2_song', OUT_FPS='60', OUT_RES='1080p', FEATURES=str(WORK / 'features.npz'),
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
    from titles_s11v2 import make_cards
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
    ap.add_argument('--outdir', type=Path, default=ROOT / 'out/s11_full2/stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='14')
    args = ap.parse_args()
    Renderer, song = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(v):
        return renderer.out.frame(song_time(v), int(round(v * FPS)))

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            start = time.process_time()
            data = frame(t)
            Image.frombytes('RGB', (w, h), data).save(args.outdir / f'v{t:07.2f}.png')
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
    # the embrace pair's bodies ask each other where they are: deep recursion when a range starts mid-embrace
    import threading
    sys.setrecursionlimit(200000)
    threading.stack_size(1024 * 1024 * 1024)
    failed = []

    def run():
        try:
            main()
        except BaseException as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            failed.append(e)

    th = threading.Thread(target=run)
    th.start()
    th.join()
    if failed:
        sys.exit(1)
