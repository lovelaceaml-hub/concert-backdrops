"""Render song 01 "All You Stars of Zion" full backdrop, version 2, with the pinned Revision 3 engine (cloud only).

    python tools/s01_full2/prepare_s01.py                                         # once: engines, features, score
    python tools/s01_full2/render.py --stills 0,7,46 --scale .5 --outdir <dir>   # stage seconds (+ quarter size)
    python tools/s01_full2/render.py --range 0 600 --out <part.mp4>              # stage frames [a, b), 60 fps

Stage time equals song time for this song: the reference recording (187.97 s) is within 1 s of the live
length (3:08 = 188.0 s), so it is used as is (DESIGN-SYSTEM 4). The audio is never in the repository.

Opening (DESIGN-SYSTEM 7, PHASEB 16): whole and readable from frame 0 to 7.0 s on the calm night sky: the
campaign logo, HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (italic), a gold hairline and
the song title large. From 7.0 s it shrinks and glides into the top left corner and becomes the signature
(whole by 8.8 s). Signature (the same layout as every song's version 2): logo mark, song title, the concert
title on one line, DEC 6 · 4:30 PM (brightest), HEALING CONCERT · LAS VEGAS; one constant layer from then to
the last frame, it never flashes. No em dash or en dash anywhere in this file.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
sys.path.insert(0, str(HERE))
from prepare import SNAPSHOT  # noqa: E402
from prepare_s01 import WORK, AUDIO  # noqa: E402

FPS = 60
SONG_NAME = "All You Stars of Zion"
OPEN_HOLD = 7.0           # the opening is whole and still from frame 0 to here
OPEN_MOVE = (7.0, 8.8)    # then it glides into the top left corner and becomes the signature
SIG_X, SIG_Y = 0.034, 0.042   # the signature's top left corner (fractions of 1920 x 1080), as song 02 v2
# fix 1 (coordinator, Never 9): the bottom third stays calm for the performers standing in front of it. A soft
# floor dims the finished picture from 0.60 of the height down (to 0.45 at the bottom edge), under the words.
FLOOR = (0.60, 0.72, 0.50, 0.45)   # start, full, dim at "full", dim at the bottom edge
FLOOR_FS = """
#version 330
out vec4 o;
uniform float uH, uTop0;
uniform vec4 uFloor;
void main(){
  float y = gl_FragCoord.y / uH;
  if(uTop0 < 0.5) y = 1.0 - y;            // y: 0 at the top of the picture, 1 at the bottom
  float k = 1.0 - (1.0 - uFloor.z) * smoothstep(uFloor.x, uFloor.y, y)
                - (uFloor.z - uFloor.w) * smoothstep(uFloor.y, 1.0, y);
  o = vec4(vec3(k), 1.0);
}
"""
TOP0 = float(os.environ.get("S01_TOP0", "1"))   # f_out rows: the first row read back is the top


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def load():
    if not (SNAPSHOT / "engine/render.py").exists() or not (WORK / "features.npz").exists():
        raise SystemExit("Run tools/s01_full2/prepare_s01.py first.")
    os.environ.update(SONG="s01_full2", OUT_FPS=str(FPS), OUT_RES="1080p", FEATURES=str(WORK / "features.npz"),
                      AUDIO=str(AUDIO), LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1",
                      OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                      NUMBA_CACHE_DIR=str(WORK / "numba"), MESA_SHADER_CACHE_DIR=str(WORK / "mesa"))
    sys.path.insert(0, str(SNAPSHOT / "engine"))
    import songs
    songs.__path__.append(str(HERE))
    import p3d
    p3d.__path__.append(str(ROOT / "engine/p3d"))
    import song  # noqa: F401
    import importlib.util
    spec = importlib.util.spec_from_file_location("titles", ROOT / "engine/titles.py")
    titles = importlib.util.module_from_spec(spec)
    sys.modules["titles"] = titles
    spec.loader.exec_module(titles)
    spec = importlib.util.spec_from_file_location("reference_renderer", SNAPSHOT / "engine/render.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    from PIL import Image, ImageDraw

    class Lockups(titles.Titles):
        """The opening lockup and the signature (see the module text)."""

        def __init__(self, renderer):
            super().__init__(renderer)
            self.op = dict(t_end=1e9, y=0.36, palette="night", dissolve=1.6, build=1.2)
            self.op_logo = None
            self.op_layer = self._open_layer()
            self.sig_layer = self._sig_layer("night")
            self.p_floor = self.ctx.program(vertex_shader=titles.FULL_VS, fragment_shader=FLOOR_FS)
            quad = self.ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
            self.v_floor = self.ctx.vertex_array(self.p_floor, [(quad, "2f", "aPos")])

        def _open_layer(self):
            s, W, H = self.s, self.w, self.h
            P = titles.PALETTES["night"]          # warm white with gold accents on the night sky
            col, acc = P["col"], P["acc"]
            lines = self._title_lines()
            lh = 100.0
            total = lh + 22 + 32 + 84 + 70 + 30 + 124
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            cx = W / 2.0
            top = self.op["y"] * H - total * s / 2.0
            lg = self._logo("opening", lh * s, "night")
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
            return self._finish(L, 14, 0.55, "night", noise=True)

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

        def _move(self, ts):
            """0 while the opening holds, 1 once it has become the signature."""
            return _ss(OPEN_MOVE[0], OPEN_MOVE[1], ts)

        def sig_alpha(self, ts):
            return _ss(OPEN_MOVE[0] + 0.45 * (OPEN_MOVE[1] - OPEN_MOVE[0]), OPEN_MOVE[1], ts)

        def _open_rect(self, ts):
            """The opening's rectangle while it glides: its top left corner goes to the signature's and its
            height shrinks to the signature's height (the shape is kept, so no letter is ever distorted)."""
            x0, y0, w0, h0 = self.op_layer["rect"]
            sx, sy, sw, sh = self.sig_layer["rect"]
            m = self._move(ts)
            k = 1.0 + (sh / h0 - 1.0) * m
            return (x0 + (sx - x0) * m, y0 + (sy - y0) * m, w0 * k, h0 * k)

        def overlay(self, ts):
            ctx, mgl = self.ctx, self.mgl
            self.R.f_out.use()
            ctx.enable(mgl.BLEND)
            ctx.blend_func = (mgl.ZERO, mgl.SRC_COLOR)          # the calm floor multiplies the picture
            self.p_floor["uFlip"].value = 1.0
            self.p_floor["uH"].value = float(self.h)
            self.p_floor["uTop0"].value = TOP0
            self.p_floor["uFloor"].value = FLOOR
            self.v_floor.render(mgl.TRIANGLE_STRIP)
            ctx.blend_func = (mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA)
            m = self._move(ts)
            if m < 1.0:
                a = 1.0 - _ss(0.45, 1.0, m)
                L = dict(self.op_layer, rect=self._open_rect(ts))
                self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=float(a), uDis=(-1.0, 0.0, 0.0, 0.0))
                tr = self._trace(ts) if m <= 0.0 else None
                if tr is not None:
                    img, (x, y, w, h) = tr
                    if self.tr_tex is None or self.tr_tex.size != (w, h):
                        self.tr_tex = self._tex(img)
                    else:
                        self.tr_tex.write(np.ascontiguousarray(np.clip(img * 255.0 + 0.5, 0, 255)
                                                               .astype(np.uint8)).tobytes())
                    self._quad(self.p_ovl, self.v_ovl, dict(tex=self.tr_tex, rect=(x / self.w, y / self.h,
                               w / self.w, h / self.h)), -1.0, uAlpha=1.0, uDis=(-1.0, 0.0, 0.0, 0.0))
            k = self.sig_alpha(ts)
            if k > 0.002:
                self._quad(self.p_ovl, self.v_ovl, self.sig_layer, -1.0, uAlpha=float(k),
                           uDis=(-1.0, 0.0, 0.0, 0.0))
            ctx.disable(mgl.BLEND)
            return True

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = Lockups(self)

        def stage_frame(self, ts, index=0):
            super().frame(ts, index)
            self.cards.overlay(ts)
            return self.f_out.read(components=3)

    return Renderer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--outdir", type=Path, default=ROOT.parent / "work/stills")
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--crf", default="12")
    ap.add_argument("--noquarter", action="store_true")
    args = ap.parse_args()
    Renderer = load()
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
            name = f"t{t:07.2f}"
            img.save(args.outdir / f"{name}.png")
            if not args.noquarter:
                img.resize((480, 270), Image.LANCZOS).save(args.outdir / f"{name}-q.png")
            print(f"{t:.2f}: {time.process_time() - start:.1f} CPU s", flush=True)
        return
    if args.range is None or args.out is None:
        ap.error("Use --stills or --range A B --out file")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
           "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-threads", "1",
           "-preset", "medium", "-crf", args.crf, "-pix_fmt", "yuv420p", "-g", "60",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
           str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    a, b = args.range
    try:
        for i in range(a, b):
            ff.stdin.write(frame(i / FPS))
            if (i - a) % 120 == 0:
                print(f"frame {i}: {time.time() - start:.0f} s", flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit("Encoder failed")
    print(f"done {args.out} {b - a} frames {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
