"""Song 03 full backdrop: render stills or a range of frames (30 fps, 1920x1080), CPU only.

The pinned Film 10 engine (d928ff9, restored by tools/nine_colours_minor/prepare.py into
work/nine_colours_minor/render1) draws the world from the song module tools/s03_full/s03_full.py; the
Revision 3 signature (engine/titles.py at the approved tag) and tools/s03_full/overlay.py are drawn over it.

    python tools/s03_full/render.py --stills 5,30,120 --scale 0.5 --outdir work/s03_full/stills
    python tools/s03_full/render.py --range 0 1500 --out work/s03_full/parts/p00.mp4

No em dash or en dash anywhere in this file.
"""
import argparse
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SNAPSHOT = ROOT / "work/nine_colours_minor/render1"
WORK = ROOT / "work/s03_full"
SIGNATURE = (19.5, 364.0)     # the small signature, bottom left, from after the title card to the hold


def load():
    if not (SNAPSHOT / "engine/render.py").exists():
        raise SystemExit("Run tools/nine_colours_minor/prepare.py first.")
    if not (WORK / "features.npz").exists():
        raise SystemExit("Run tools/s03_full/prepare.py first.")
    os.environ.update(SONG="s03_full", FEATURES=str(WORK / "features.npz"),
                      LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                      OMP_NUM_THREADS="1", NUMBA_CACHE_DIR=str(WORK / "numba"),
                      MESA_SHADER_CACHE_DIR=str(WORK / "mesa"))
    sys.path.insert(0, str(SNAPSHOT / "engine"))
    sys.path.insert(0, str(HERE))
    import songs
    songs.__path__.append(str(HERE))          # songs.s03_full is this folder's song module
    import song as S
    import p3d
    p3d.__path__.append(str(ROOT / "engine/p3d"))   # the brand logo for the signature (approved tag)
    S.TITLES = dict(signature=dict(windows=[(SIGNATURE[0], SIGNATURE[1], "bl", "night")], fade=1.2))
    spec = importlib.util.spec_from_file_location("titles", ROOT / "engine/titles.py")
    titles = importlib.util.module_from_spec(spec)
    sys.modules["titles"] = titles
    spec.loader.exec_module(titles)
    spec = importlib.util.spec_from_file_location("engine_render", SNAPSHOT / "engine/render.py")
    engine_render = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_render)
    from overlay import Overlay

    class Signature(titles.Titles):
        def _signature(self, corner, pal):
            scale = self.s
            try:
                self.s *= 0.62            # small: the performers stand in front
                return super()._signature(corner, pal)
            finally:
                self.s = scale

    class Renderer(engine_render.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.sig = Signature(self)
            self.ovl = Overlay(w, h, S)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            if self.sig.overlay(t):
                data = self.f_out.read(components=3)
            return self.ovl.apply(data, t)

    return Renderer, S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--outdir", type=Path, default=WORK / "stills")
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--crf", default="14")
    args = ap.parse_args()
    Renderer, S = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    R = Renderer(w, h)
    fps = S.FPS

    def frame(i):
        return R.out.frame(i / fps, i)

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for s in args.stills.split(","):
            t = float(s)
            i = int(round(t * fps))
            t0 = time.time()
            data = frame(i)
            Image.frombytes("RGB", (w, h), data).save(args.outdir / f"t{t:07.2f}.png")
            print(f"still {t:7.2f}s  {time.time() - t0:.2f}s", flush=True)
        return
    if args.range is None or args.out is None:
        ap.error("Use --stills or --range A B --out file.mp4")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-threads", "1",
           "-preset", "medium", "-crf", args.crf, "-pix_fmt", "yuv420p", "-g", "60", "-bf", "2",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
           str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    f0, f1 = args.range
    try:
        for i in range(f0, f1):
            ff.stdin.write(frame(i))
            if (i - f0) % 150 == 0:
                el = time.time() - t0
                print(f"frame {i} ({i - f0}/{f1 - f0})  {el:.0f}s  {el / max(i - f0, 1):.2f}s/frame", flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit("ffmpeg failed")
    print("done", args.out, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
