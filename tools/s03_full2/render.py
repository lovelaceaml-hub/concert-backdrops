"""Song 03 backdrop v2: render stills or a range of frames (60 fps, 1920x1080), CPU only, in this cloud session.

The pinned Film 10 engine (d928ff9, restored by tools/nine_colours_minor/prepare.py into
work/nine_colours_minor/render1) draws the world from tools/s03_full2/s03_full2.py; tools/s03_full2/overlay2.py
draws the opening lockup, the signature, the expressions, the fragments, the hearts and symbols and lays the
people of tools/s03_full2/people.py over it.

    python tools/s03_full2/render.py --stills 5,30,120 --outdir work/s03_full2/stills
    python tools/s03_full2/render.py --range 0 1500 --out work/s03_full2/parts/p00.mkv

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
WORK = ROOT / "work/s03_full2"


def load(overlay=True):
    if not (SNAPSHOT / "engine/render.py").exists():
        raise SystemExit("Run tools/nine_colours_minor/prepare.py first.")
    if not (WORK / "features.npz").exists():
        raise SystemExit("Run tools/s03_full2/prepare.py first.")
    os.environ.update(SONG="s03_full2", OUT_FPS="60", OUT_RES="1080p", FEATURES=str(WORK / "features.npz"),
                      LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                      OMP_NUM_THREADS="1", NUMBA_CACHE_DIR=str(WORK / "numba"),
                      MESA_SHADER_CACHE_DIR=str(WORK / "mesa"))
    sys.path.insert(0, str(SNAPSHOT / "engine"))
    sys.path.insert(0, str(HERE))
    import songs
    songs.__path__.append(str(HERE))          # songs.s03_full2 is this folder's song module
    import song as S
    S.TITLES = None
    spec = importlib.util.spec_from_file_location("engine_render", SNAPSHOT / "engine/render.py")
    engine_render = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_render)

    class Renderer(engine_render.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.ovl = None
            if overlay:
                from overlay2 import Overlay
                self.ovl = Overlay(w, h, S)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            return self.ovl.apply(data, t, index) if self.ovl else data

    return Renderer, S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--outdir", type=Path, default=WORK / "stills")
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--no-overlay", action="store_true")
    args = ap.parse_args()
    Renderer, S = load(not args.no_overlay)
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    R = Renderer(w, h)
    fps = 60

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
        ap.error("Use --stills or --range A B --out file.mkv")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # parts are near lossless (x264 CRF 8, 4:4:4); export.py makes the delivery encodes from the joined parts
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264rgb", "-crf", "8", "-preset", "fast", "-threads", "1", "-g", "120",
           str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    f0, f1 = args.range
    try:
        for i in range(f0, f1):
            ff.stdin.write(frame(i))
            if (i - f0) % 300 == 0:
                el = time.time() - t0
                print(f"frame {i} ({i - f0}/{f1 - f0})  {el:.0f}s  {el / max(i - f0, 1):.2f}s/frame", flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit("ffmpeg failed")
    print("done", args.out, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
