"""Render song 02 "The Rose" full backdrop, version 2, with the pinned Revision 3 engine (cloud session only).

    python tools/nine_colours_minor/prepare.py                 # once: pinned engine and Claude Final v1
    python tools/s02_full2/render.py --stills 0,7,155 --scale .5 --outdir <dir>   # STAGE seconds (+ quarter size)
    python tools/s02_full2/render.py --range 0 600 --out <part.mp4>               # stage frames [a, b), 60 fps

The audio is never in the repository: S02_AUDIO_DIR points at a folder holding s02_22k.wav and
s02_features.npz (made by tools/s02_full2/export.py --prepare). No em dash or en dash anywhere in this file.
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
FPS = 60
SONG_NAME = "The Rose"
OPEN_END = 8.6            # the opening is whole from frame 0 to 7.0 s, then dissolves (gone by 8.6 s)
SIG_IN = (8.0, 9.6)       # the signature fades in once as the opening leaves, then stays to the last frame
DAY = (199.0, 244.0)      # the pale dawn: the signature turns navy over 3 s, and back to warm white for the night
SIG_X, SIG_Y = 0.034, 0.042   # its top left corner (fractions of 1920 x 1080)


def load():
    if not (SNAPSHOT / "engine/render.py").exists():
        raise SystemExit("Run tools/nine_colours_minor/prepare.py first.")
    os.environ.update(SONG="s02_rose_full2", OUT_FPS=str(FPS), OUT_RES="1080p",
                      FEATURES=str(AUDIO_DIR / "s02_features.npz"), AUDIO=str(AUDIO_DIR / "s02_22k.wav"),
                      LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                      OMP_NUM_THREADS="1", NUMBA_CACHE_DIR=str(WORK / "numba"),
                      MESA_SHADER_CACHE_DIR=str(WORK / "mesa"))
    sys.path.insert(0, str(SNAPSHOT / "engine"))
    import songs
    import importlib.util
    # the song module lives here; the engine finds it as songs.s02_rose_full
    spec = importlib.util.spec_from_file_location("songs.s02_rose_full2", HERE / "rose.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["songs.s02_rose_full2"] = mod
    songs.s02_rose_full2 = mod
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
    from PIL import Image, ImageDraw

    class Lockups(titles.Titles):
        """The opening lockup and the signature, on the STAGE clock (seconds of the stage video).

        Opening (DESIGN-SYSTEM 7, PHASEB 16): readable from frame 0 and held to OPEN_END: the campaign logo
        above, HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (second line italic), a gold
        hairline, and the song title large; then it dissolves into glowing dust (the approved dissolve).
        Signature (the same in all 11 songs): from the end of the opening to the last frame, small in the TOP
        LEFT: logo mark, song title, the concert title on one line, DEC 6 · 4:30 PM (brightest), HEALING
        CONCERT · LAS VEGAS. It never flashes: one constant layer, faded in once."""

        def __init__(self, renderer):
            super().__init__(renderer)
            W, H, s = self.w, self.h, self.s
            self.op = dict(t_end=OPEN_END, y=0.34, palette="day", dissolve=1.6, build=1.2)
            self.op_logo = None
            self.op_layer = self._open_layer()
            self.sig_layer = self._sig_layer("night")
            self.sig_day = self._sig_layer("day")

        def _open_layer(self):
            s, W, H = self.s, self.w, self.h
            P = titles.PALETTES["day"]          # navy on the pale morning sky (never white on a pale sky)
            col, acc = P["col"], P["acc"]
            lines = self._title_lines()
            lh = 100.0
            total = lh + 22 + 32 + 84 + 70 + 30 + 124
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            cx = W / 2.0
            top = self.op["y"] * H - total * s / 2.0
            lg = self._logo("opening", lh * s, "day")
            if lg is not None:
                im, ox, oy, lw = lg
                bx, by = cx - lw / 2.0, top + lh * s - (im.height - 2 * oy)
                L.alpha_composite(im, (int(round(bx - ox)), int(round(by - oy))))
                self.op_logo = (int(round(bx - ox)), int(round(by - oy)), im.width, im.height)
            y = top + (lh + 22) * s
            titles._tracked(d, (cx, y), "HEALING CONCERT", titles.JO(500, 28 * s), acc + (255,), 9 * s)
            y += 32 * s
            d.text((cx, y), lines[0], font=titles.CG(500, 76 * s), fill=col + (255,), anchor="ma")
            y += 84 * s
            d.text((cx, y), lines[1], font=titles.CG(500, 58 * s, it=True), fill=col + (255,), anchor="ma")
            y += 70 * s + 12 * s
            d.line((cx - 60 * s, y, cx + 60 * s, y), fill=acc + (210,), width=max(1, int(round(2 * s))))
            y += 16 * s
            d.text((cx, y), SONG_NAME, font=titles.CG(600, 118 * s), fill=col + (255,), anchor="ma")
            return self._finish(L, 14, 0.55, "day", noise=True)

        def _sig_layer(self, pal):
            s, W, H = self.s, self.w, self.h
            P = titles.PALETTES[pal]
            col, acc = P["col"], P["acc"]
            soft = tuple(int(0.86 * c + 0.14 * a) for c, a in zip(col, acc))
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            mx, my = SIG_X * 1920 * s, SIG_Y * 1080 * s
            blk = 150.0 * s
            lg = self._logo("signature", 78 * s, pal)
            gap = 18 * s
            if lg is not None:
                im, ox, oy, lw = lg
                lhh = im.height - 2 * oy
                L.alpha_composite(im, (int(round(mx - ox)), int(round(my + (blk - lhh) / 2.0 - oy))))
                gap += lw
            tx = mx + gap
            d.text((tx, my - 6 * s), SONG_NAME, font=titles.CG(600, 44 * s, it=True), fill=soft + (238,), anchor="la")
            d.text((tx, my + 46 * s), " ".join(self._title_lines()), font=titles.CG(500, 25 * s, it=True),
                   fill=soft + (225,), anchor="la")
            titles._tracked(d, (tx, my + 84 * s), "DEC 6" + titles.SEP + "4:30 PM", titles.JO(500, 32 * s),
                            col + (255,), 5 * s, align="left")
            titles._tracked(d, (tx, my + 126 * s), "HEALING CONCERT" + titles.SEP + "LAS VEGAS",
                            titles.JO(400, 20 * s), acc + (232,), 5 * s, align="left")
            return self._finish(L, 9, 0.5, pal)

        def sig_alpha(self, ts):
            return float(titles._ss(SIG_IN[0], SIG_IN[1], ts))

        def overlay(self, ts):
            ctx, mgl = self.ctx, self.mgl
            self.R.f_out.use()
            ctx.enable(mgl.BLEND)
            ctx.blend_func = (mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA)
            a, front, prog = self._op_state(ts)
            if a > 0.0 and prog < 1.0:
                L = self.op_layer
                L["t_noise"].use(location=1)
                self.p_ovl["uNoise"].value = 1
                self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=1.0,
                           uDis=(float(front) if front is not None else -1.0, 0.06, 0.38, 0.0))
                tr = self._trace(ts)
                if tr is not None:
                    img, (x, y, w, h) = tr
                    if self.tr_tex is None or self.tr_tex.size != (w, h):
                        self.tr_tex = self._tex(img)
                    else:
                        self.tr_tex.write(np.ascontiguousarray(np.clip(img * 255.0 + 0.5, 0, 255)
                                                               .astype(np.uint8)).tobytes())
                    self._quad(self.p_ovl, self.v_ovl, dict(tex=self.tr_tex, rect=(x / self.w, y / self.h,
                               w / self.w, h / self.h)), -1.0, uAlpha=1.0, uDis=(-1.0, 0.0, 0.0, 0.0))
                if front is not None:
                    self._op_dust(ts, front)
            k = self.sig_alpha(ts)
            day = float(titles._ss(DAY[0], DAY[0] + 3.0, ts) * (1.0 - titles._ss(DAY[1] - 3.0, DAY[1], ts)))
            if k * (1.0 - day) > 0.002:
                self._quad(self.p_ovl, self.v_ovl, self.sig_layer, -1.0, uAlpha=k * (1.0 - day),
                           uDis=(-1.0, 0.0, 0.0, 0.0))
            if k * day > 0.002:
                self._quad(self.p_ovl, self.v_ovl, self.sig_day, -1.0, uAlpha=k * day, uDis=(-1.0, 0.0, 0.0, 0.0))
            ctx.disable(mgl.BLEND)
            return True

        def _op_dust(self, ts, front):
            try:
                self._op_points(ts, front)
            except Exception:
                pass

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = Lockups(self)

        def stage_frame(self, ts, index=0):
            """One frame at STAGE time ts: the world runs on song seconds (ts * K)."""
            super().frame(ts * mod.K, index)
            self.cards.overlay(ts)
            return self.f_out.read(components=3)

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

    def frame(ts):
        return renderer.stage_frame(ts, int(round(ts * FPS)))

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
