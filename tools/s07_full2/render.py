"""Render song 07's full backdrop, version 2 (cloud only; never on the Mac, never the GitHub Render workflow).

    python tools/nine_colours_minor/prepare.py                       # once: the pinned engine snapshots
    python tools/s07_full2/prepare_audio.py /path/to/s07.mp3         # once: features and conformed music
    python tools/s07_full2/render.py --stills 0,7,30 --scale .5 --outdir <dir>     # LIVE seconds
    python tools/s07_full2/render.py --range 0 900 --out <part.mp4>                # LIVE frames at 60 fps

Times given here are LIVE (stage video) seconds; frame i is at i / 60 s. The scene runs on the reference clock
(clock.ref); the opening card and the signature run on the live clock. No em dash or en dash in this file.
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
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
from prepare import SNAPSHOT  # noqa: E402
import clock  # noqa: E402

WORK = ROOT / "work/s07v2"
FPS = clock.FPS


def load():
    if not (SNAPSHOT / "engine/render.py").exists():
        raise SystemExit("Run tools/nine_colours_minor/prepare.py first.")
    if not (WORK / "features.npz").exists():
        raise SystemExit("Run tools/s07_full2/prepare_audio.py first.")
    os.environ.update(SONG="s07_full2_song", OUT_FPS=str(FPS), OUT_RES="1080p",
                      FEATURES=str(WORK / "features.npz"), AUDIO=str(WORK / "audio.wav"),
                      LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                      OMP_NUM_THREADS="1", NUMBA_CACHE_DIR=str(WORK / "numba"),
                      MESA_SHADER_CACHE_DIR=str(WORK / "mesa"), P3D_CACHE=str(WORK / "p3d_cache"))
    sys.path.insert(0, str(SNAPSHOT / "engine"))
    import songs
    songs.__path__.append(str(HERE))
    import p3d
    p3d.__path__.append(str(ROOT / "engine/p3d"))
    import song  # noqa: F401  (imports songs.s07_full2_song)
    spec = importlib.util.spec_from_file_location("reference_renderer", SNAPSHOT / "engine/render.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    spec = importlib.util.spec_from_file_location("titles", ROOT / "engine/titles.py")
    titles = importlib.util.module_from_spec(spec)
    sys.modules["titles"] = titles
    spec.loader.exec_module(titles)
    from cards07 import Cards07

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = Cards07(self)

        def frame(self, t, index=0):
            # t is LIVE time: the scene on the reference clock, the cards on the live clock
            data = super().frame(clock.ref(t), index)
            if self.cards.overlay(t):
                return self.f_out.read(components=3)
            return data

    return Renderer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--outdir", type=Path, default=ROOT / "out/s07v2/stills")
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--crf", default="14")
    args = ap.parse_args()
    Renderer = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(t):
        return renderer.out.frame(t, int(round(t * FPS)))

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(",")):
            start = time.process_time()
            data = frame(t)
            Image.frombytes("RGB", (w, h), data).save(args.outdir / f"t{t:07.2f}.png")
            print(f"{t:.3f}: {time.process_time() - start:.1f} CPU seconds", flush=True)
        return
    if args.range is None or args.out is None:
        ap.error("Use --stills or --range A B --out file.mp4")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
           "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-threads", "1",
           "-preset", "medium", "-crf", args.crf, "-pix_fmt", "yuv420p", "-g", str(FPS * 2), "-bf", "2",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
           str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(i / FPS))
            if (i - args.range[0]) % 120 == 0:
                print(f"frame {i}: {time.time() - start:.0f} s", flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit("Encoder failed")
    print(f"done {args.out}: {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
