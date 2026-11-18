"""Render song 02 "The Rose" full backdrop with the pinned Revision 3 engine (cloud session only).

    python tools/nine_colours_minor/prepare.py                 # once: pinned engine and Claude Final v1
    python tools/s02_full/render.py --stills 3,30,60 --scale .5 --outdir <dir>     # (+ quarter-size copies)
    python tools/s02_full/render.py --range 0 600 --out <part.mp4>                  # frames [a, b) at 30 fps

The audio is never in the repository: S02_AUDIO_DIR points at a folder holding s02_22k.wav and
s02_features.npz (made by tools/s02_full/export.py --prepare). No em dash or en dash anywhere in this file.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
from prepare import SNAPSHOT, WORK  # noqa: E402

AUDIO_DIR = Path(os.environ.get("S02_AUDIO_DIR", str(ROOT.parent / "media/audio")))
FPS = 30


def load():
    if not (SNAPSHOT / "engine/render.py").exists():
        raise SystemExit("Run tools/nine_colours_minor/prepare.py first.")
    os.environ.update(SONG="s02_rose_full", OUT_FPS=str(FPS), OUT_RES="1080p",
                      FEATURES=str(AUDIO_DIR / "s02_features.npz"), AUDIO=str(AUDIO_DIR / "s02_22k.wav"),
                      LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                      OMP_NUM_THREADS="1", NUMBA_CACHE_DIR=str(WORK / "numba"),
                      MESA_SHADER_CACHE_DIR=str(WORK / "mesa"))
    sys.path.insert(0, str(SNAPSHOT / "engine"))
    import songs
    import importlib.util
    # the song module lives here; the engine finds it as songs.s02_rose_full
    spec = importlib.util.spec_from_file_location("songs.s02_rose_full", HERE / "rose.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["songs.s02_rose_full"] = mod
    songs.s02_rose_full = mod
    spec.loader.exec_module(mod)
    import song
    import p3d
    p3d.__path__.append(str(ROOT / "engine/p3d"))
    spec = importlib.util.spec_from_file_location("reference_renderer", SNAPSHOT / "engine/render.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    spec = importlib.util.spec_from_file_location("titles", ROOT / "engine/titles.py")
    titles = importlib.util.module_from_spec(spec)
    sys.modules["titles"] = titles
    spec.loader.exec_module(titles)
    from cards import Cards
    from PIL import Image, ImageDraw

    class SongCards(Cards):
        """Revision 3's titles (the small signature) plus this song's own title: "The Rose" large in the upper
        third over the concert's name, then small at the top left for the rest of the song."""

        def __init__(self, renderer):
            super().__init__(renderer)
            st = song.SONG_TITLE
            self.st = st
            W, H, s = self.w, self.h, self.s
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            col = (255, 246, 232)
            d.text((W / 2, st["y"] * H), st["text"], font=titles.CG(500, 150 * s), fill=col + (255,), anchor="mm")
            titles._tracked(d, (W / 2, st["y"] * H + 100 * s), st["sub"].upper(), titles.JO(500, 30 * s),
                            (246, 211, 139, 255), 5 * s)
            self.big = self._finish(L, 14, 0.55, "night")
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            d.text((104 * s, 70 * s), st["text"], font=titles.CG(500, 54 * s, it=True), fill=col + (235,),
                   anchor="la")
            self.small = self._finish(L, 9, 0.5, "night")

        def _alphas(self, t):
            st = self.st
            big = float(titles._ss(st["t_in"], st["t_full"], t) * (1.0 - titles._ss(st["t_out0"], st["t_out1"], t)))
            small = float(titles._ss(st["small_in"][0], st["small_in"][1], t))
            return big, small

        def overlay(self, t):
            drew = super().overlay(t)
            big, small = self._alphas(t)
            ctx, mgl = self.ctx, self.mgl
            self.R.f_out.use()
            ctx.enable(mgl.BLEND)
            ctx.blend_func = (mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA)
            for L, k in ((self.big, big), (self.small, small * 0.85)):
                if k > 0.002:
                    self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=k, uDis=(-1.0, 0.0, 0.0, 0.0))
                    drew = True
            ctx.disable(mgl.BLEND)
            return drew

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = SongCards(self)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            if self.cards.overlay(t):
                return self.f_out.read(components=3)
            return data

    return Renderer, mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--outdir", type=Path, default=ROOT.parent / "media/stills")
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--raw", action="store_true", help="write raw rgb24 frames to --out instead of H.264")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--crf", default="12")
    ap.add_argument("--quarter", action="store_true", default=True)
    args = ap.parse_args()
    Renderer, mod = load()
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)

    def frame(t):
        return renderer.out.frame(t, int(round(t * FPS)))

    if args.stills:
        from PIL import Image
        args.outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(",")):
            start = time.process_time()
            img = Image.frombytes("RGB", (w, h), frame(t))
            name = f"t{t:06.1f}"
            img.save(args.outdir / f"{name}.png")
            if args.quarter:
                img.resize((480, 270), Image.LANCZOS).save(args.outdir / f"{name}-q.png")
            print(f"{t:.2f}: {time.process_time() - start:.1f} CPU s", flush=True)
        return
    if args.range is None or args.out is None:
        ap.error("Use --stills or --range A B --out file")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
           "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-threads", "1",
           "-preset", "medium", "-crf", args.crf, "-pix_fmt", "yuv420p", "-g", "30",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
           str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    a, b = args.range
    try:
        for i in range(a, b):
            ff.stdin.write(frame(i / FPS))
            if (i - a) % 60 == 0:
                print(f"frame {i}: {time.time() - start:.0f} s", flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit("Encoder failed")
    print(f"done {args.out} {b - a} frames {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
