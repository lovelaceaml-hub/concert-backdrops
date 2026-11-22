"""Render song 05's full backdrop: stills, or a range of frames to a video part (30 fps).

    python tools/nine_colours_minor/prepare.py                       # once: the pinned engine and Claude Final v1
    python tools/s05_full/render05.py --audio <s05.m4a> --stills 20,30 --scale .5 --outdir <dir>
    python tools/s05_full/render05.py --audio <s05.m4a> --range 0 300 --out part.mp4

The song audio is never committed: give its path (outside the repo). Its features are analysed once into
work/s05_full/features.npz. Cloud only. No em dash or en dash anywhere in this file.
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
sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
from prepare import SNAPSHOT  # noqa: E402

WORK = ROOT / "work/s05_full"


def features(audio):
    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / "features.npz"
    if not out.exists():
        wav = WORK / "audio.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-ac", "1", "-ar", "22050", str(wav)],
                       check=True)
        env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / "numba"))
        subprocess.run([sys.executable, str(SNAPSHOT / "engine/analyze.py"), str(wav), str(out)], env=env,
                       check=True, stdout=subprocess.DEVNULL)
    return out


def load(audio):
    if not (SNAPSHOT / "engine/render.py").exists():
        raise SystemExit("Run tools/nine_colours_minor/prepare.py first.")
    os.environ.update(SONG="s05_full", OUT_FPS="30", OUT_RES="1080p", FEATURES=str(features(audio)),
                      AUDIO=str(audio), LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1",
                      OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                      NUMBA_CACHE_DIR=str(WORK / "numba"), MESA_SHADER_CACHE_DIR=str(WORK / "mesa"))
    sys.path.insert(0, str(SNAPSHOT / "engine"))
    sys.path.insert(0, str(HERE))
    import p3d
    p3d.__path__.append(str(ROOT / "engine/p3d"))           # brand modules for the signature's logo
    import songs
    spec = importlib.util.spec_from_file_location("songs.s05_full", HERE / "song05.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["songs.s05_full"] = mod
    songs.s05_full = mod
    spec.loader.exec_module(mod)
    import song
    if not hasattr(song, "P3D"):              # imported half way through the song module: read it again
        importlib.reload(song)
    assert getattr(song, "P3D", None) is mod.P3D, "the engine did not pick up song05"
    spec = importlib.util.spec_from_file_location("reference_renderer", SNAPSHOT / "engine/render.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    spec = importlib.util.spec_from_file_location("titles", ROOT / "engine/titles.py")
    titles = importlib.util.module_from_spec(spec)
    sys.modules["titles"] = titles
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

    return Renderer, mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", type=Path, required=True)
    ap.add_argument("--stills", default="")
    ap.add_argument("--outdir", type=Path, default=ROOT / "out/s05_full/stills")
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--raw", action="store_true", help="write raw rgb24 frames instead of encoding")
    ap.add_argument("--scale", type=float, default=1)
    ap.add_argument("--crf", default="14")
    args = ap.parse_args()
    Renderer, mod = load(args.audio.resolve())
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(i):
        t = i / 30.0
        return renderer.out.frame(t, i)

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(",")):
            start = time.time()
            data = frame(int(round(t * 30)))
            Image.frombytes("RGB", (w, h), data).save(args.outdir / f"t{t:07.2f}.png")
            print(f"{t:.2f}: {time.time() - start:.1f} s", flush=True)
        return
    if args.range is None or args.out is None:
        ap.error("Use --stills or --range A B --out file.mp4")
    a, b = args.range
    b = min(b, mod.NFRAMES)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "30",
           "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-threads", "1",
           "-preset", "medium", "-crf", args.crf, "-pix_fmt", "yuv420p", "-g", "60", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    try:
        for i in range(a, b):
            ff.stdin.write(frame(i))
            if (i - a) % 30 == 0:
                print(f"frame {i}: {time.time() - start:.0f} s", flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit("Encoder failed")
    print(f"done {args.out} frames {a}..{b}: {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
