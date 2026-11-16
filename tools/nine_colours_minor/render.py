"""Film 10's original engine with only five requested additions."""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time

from prepare import ROOT, WORK, SNAPSHOT, ENGINE_COMMIT, LEAD_IN


def load(baseline=False):
    if not (SNAPSHOT/'engine/render.py').exists():
        raise SystemExit('Run tools/nine_colours_minor/prepare.py first.')
    os.environ.update(SONG='ten_10_nine_colours', OUT_FPS='60', OUT_RES='1080p',
                      FEATURES=str(WORK/'features.npz'),
                      AUDIO=str(SNAPSHOT/'audio/promo/concert-medley.mp3'),
                      LIBGL_ALWAYS_SOFTWARE='1', LP_NUM_THREADS='1',
                      OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                      NUMBA_CACHE_DIR=str(WORK/'numba'), MESA_SHADER_CACHE_DIR=str(WORK/'mesa'))
    sys.path.insert(0, str(SNAPSHOT/'engine'))
    import song
    import songs.ten_10_nine_colours as film
    import p3d
    # Only new brand modules are found here. Existing engine modules resolve
    # first to the exact reference snapshot, including words and camera.
    p3d.__path__.append(str(ROOT/'engine/p3d'))
    spec = importlib.util.spec_from_file_location('reference_renderer', SNAPSHOT/'engine/render.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    if baseline:
        return old.Renderer, film
    from additions import install
    install(film)
    song.P3D = film.P3D
    # Replace only the old 2D closing card, leaving its world and light cues.
    song.TITLE = dict(song.TITLE, form=1e9, hold=1e9, star=1e9)
    song.TAGLINE = dict(song.TAGLINE, t0=1e9, t1=1e9+1)
    song.TITLES = dict(
        opening=dict(t_end=7.45, dissolve=.45, build=0, y=.28),
        signature=dict(windows=[(7.4, 58.1, 'bl', 'night'),
                                (58.1, 58.7, 'bl', 'day')], fade=.12),
        end_card=dict(t_in=58.5, fade=.5, scale=.94, veil=.4, backdrop=False))
    spec = importlib.util.spec_from_file_location('titles', ROOT/'engine/titles.py')
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
            self.base_frame = data
            if self.cards.overlay(t+LEAD_IN):
                return self.f_out.read(components=3)
            return data

    return Renderer, film


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', action='store_true')
    ap.add_argument('--original-clock', action='store_true')
    ap.add_argument('--stills', default='')
    ap.add_argument('--outdir', type=Path, default=ROOT/'out/nine_colours_revision2/stills')
    ap.add_argument('--range', type=int, nargs=2)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--crf', default='18')
    args = ap.parse_args()
    Renderer, film = load(args.baseline)
    w, h = int(1920*args.scale)//2*2, int(1080*args.scale)//2*2
    renderer = Renderer(w, h)
    shift = 0 if args.original_clock else LEAD_IN

    def frame(t):
        clock = t-shift
        return renderer.out.frame(clock, int(round(clock*60)))

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            start = time.process_time()
            data = frame(t)
            Image.frombytes('RGB', (w, h), data).save(args.outdir/f't{t:07.2f}.png')
            print(f'{t:.3f}: {time.process_time()-start:.3f} CPU seconds', flush=True)
        return
    if args.range is None or args.out is None:
        ap.error('Use --stills or --range A B --out file.mp4')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{w}x{h}', '-r', '60', '-i', '-', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
           '-c:v', 'libx264', '-threads', '2', '-preset', 'fast', '-crf', args.crf,
           '-pix_fmt', 'yuv420p', '-g', '60', '-bf', '2', '-color_primaries', 'bt709',
           '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
           '-movflags', '+faststart', str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.process_time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i/60))
            if (i-args.range[0])%150 == 0:
                print(f'frame {i}: {time.process_time()-start:.1f} CPU s', flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit('Encoder failed')
    print(f'done {args.out}: {time.process_time()-start:.1f} CPU seconds', flush=True)


if __name__ == '__main__':
    main()
