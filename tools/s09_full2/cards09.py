"""Song 09's opening lockup and signature, in the approved Revision 3 lockup style (engine/titles.py, as used by
tools/nine_colours_minor/cards.py), with the song title added (DESIGN-SYSTEM 7, brief of 2026-11-18).

Opening (readable from frame 0, held about 8 s on calm sky, then it crumbles into glowing dust): the logo,
HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (second line italic), a gold hairline, and the
song title large.
Signature (from the end of the opening to the last frame, top left, never flashing): the logo mark, the song
title, "The Words of Mother's Love That Bring Peace", DEC 6 · 4:30 PM (the brightest line, capitals about 24 px
tall at 1080p) and HEALING CONCERT · LAS VEGAS.
No em dash or en dash anywhere in this file.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import titles
from titles import CG, JO, PALETTES, SEP, _tracked

SONG = "Let’s Save the World"


class Cards09(titles.Titles):
    def _opening(self, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        lines = self._title_lines()
        lh = 120.0
        total = lh + 24 + 40 + 104 + 80 + 34 + 130
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        cx = W / 2.0
        top = self.op["y"] * H - total * s / 2.0
        lg = self._logo("opening", lh * s, pal)
        self.op_logo = None
        if lg is not None:
            im, ox, oy, lw = lg
            bx, by = cx - lw / 2.0, top + lh * s - (im.height - 2 * oy)
            L.alpha_composite(im, (int(round(bx - ox)), int(round(by - oy))))
            self.op_logo = (int(round(bx - ox)), int(round(by - oy)), im.width, im.height)
        y = top + (lh + 24) * s
        _tracked(d, (cx, y), "HEALING CONCERT", JO(500, 28 * s), acc + (255,), 9 * s)
        d.text((cx, y + 38 * s), lines[0], font=CG(500, 78 * s), fill=col + (255,), anchor="ma")
        d.text((cx, y + 122 * s), lines[1], font=CG(500, 58 * s, it=True), fill=col + (255,), anchor="ma")
        d.line((cx - 60 * s, y + 214 * s, cx + 60 * s, y + 214 * s), fill=acc + (210,), width=max(1, int(round(2 * s))))
        d.text((cx, y + 236 * s), SONG, font=CG(600, 118 * s), fill=col + (255,), anchor="ma")
        return self._finish(L, 14, 0.55, pal, noise=True, prot=getattr(self, "op_prot", (40.0, 16.0)))

    def _signature(self, corner, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        line = " ".join(self._title_lines())
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        mx, my = 64 * s, 52 * s
        blk = 140.0 * s
        lg = self._logo("signature", 92 * s, pal)
        gap = 20 * s
        if lg is not None:
            im, ox, oy, lw = lg
            lhh = im.height - 2 * oy
            L.alpha_composite(im, (int(round(mx - ox)), int(round(my + (blk - lhh) / 2.0 - oy))))
            gap = lw + 20 * s
        tx = mx + gap
        d.text((tx, my - 2 * s), SONG, font=CG(600, 36 * s), fill=col + (250,), anchor="la")
        d.text((tx, my + 42 * s), line, font=CG(500, 22 * s, it=True), fill=col + (225,), anchor="la")
        _tracked(d, (tx, my + 74 * s), "DEC 6" + SEP + "4:30 PM", JO(600, 34 * s), col + (255,), 5 * s,
                 align="left")
        _tracked(d, (tx, my + 118 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", JO(500, 18 * s), col + (240,),
                 4 * s, align="left")
        return self._finish(L, 9, 0.5, pal, prot=getattr(self, "sig_prot", (40.0, 16.0)))

    # ------------------------------------------------------------------ fragments on bright skies, in navy
    def _song(self):
        return sys.modules["songs.s09_full2"]

    def _frag_layer(self, name):
        key = ("frag", name)
        if key not in self.layers:
            S = self._song()
            x0, x1, y0, y1 = S.frag_box(name)
            text = S.FRAG_TEXT[name]
            path = os.path.join(titles.FONTS, "cormorant-garamond-latin-600-italic.ttf")
            want = (x1 - x0) * self.w * 0.97
            f = ImageFont.truetype(path, 100)
            bw = f.getbbox(text)[2] - f.getbbox(text)[0]
            f = ImageFont.truetype(path, max(int(round(100 * want / max(bw, 1))), 8))
            L = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
            ImageDraw.Draw(L).text((0.5 * (x0 + x1) * self.w, (1.0 - 0.5 * (y0 + y1)) * self.h), text, font=f,
                                   fill=PALETTES["day"]["col"] + (255,), anchor="mm")
            glow = S.FRAG_GLOW.get(name)
            pal = "day"
            if glow:
                pal = "frag_" + name
                PALETTES[pal] = dict(PALETTES["day"], glow=glow)
            self.layers[key] = self._finish(L, 12 if glow else 10, 1.1 if glow else 0.95, pal)
        return self.layers[key]

    def _enc_layer(self):
        """The Encouragement in navy (fix 1): the same layout as the particle words (p3d words.glyphs), drawn
        exactly over them, so the light letters underneath read as a soft glow round crisp navy letters."""
        key = ("enc",)
        if key not in self.layers:
            S = self._song()
            PW = S.PW
            w = [x for x in S.WORDS if x.name == "Encouragement"][0]
            t = 0.5 * (S.ENC_READ[0] + S.ENC_READ[1])
            cam = S.CAMERA.state(t)
            o, r, u, _ = w.frame(t, cam)
            k = w.metres_per_em()
            pts, _ = cam.project(np.array([o, o + r * k, o + u * k]))
            W, H = self.w, self.h
            c = np.array([pts[0][0] * W, (1.0 - pts[0][1]) * H])
            em = float(np.hypot((pts[1][0] - pts[0][0]) * W, (pts[1][1] - pts[0][1]) * H))
            f_phrase, f_label, tracked = PW._text_tools()
            fp = ImageFont.truetype(PW._font_file(w.font) or f_phrase, max(int(round(em)), 8))
            asc, _ = fp.getmetrics()
            line_h = em * 1.08
            n = len(w.lines)
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            navy = PALETTES["day"]["col"] + (255,)
            for i, line in enumerate(w.lines):
                # glyphs(): baseline of line i at top + i*line_h + 0.8*asc, block centre at top + n*line_h/2
                y = c[1] + (i * line_h + 0.80 * asc - n * line_h / 2.0)
                d.text((c[0], y), line, font=fp, fill=navy, anchor="ms")
            if w.label:
                lpx = w.label_size * em
                lf = ImageFont.truetype(f_label, max(int(round(lpx)), 6))
                g = PW.glyphs(w.label, w.lines, w.n, w.n_label, w.label_size, w.font)
                base_y = c[1] - (g["block"] / 2.0 + 0.30) * em
                tracked(d, (c[0], base_y), w.label.upper(), lf, 0.47 * lpx, navy)
            self.layers[key] = self._finish(L, 10, 0.95, "day")
        return self.layers[key]

    def overlay(self, t):
        drew = super().overlay(t)
        S = self._song()
        jobs = [(name, S.frag_alpha(name, t)) for name in S.FRAG_TEXT]
        jobs = [(n, a) for n, a in jobs if a > 0.002]
        r0, r1 = S.ENC_READ
        ea = float(S._ss(r0 - 0.4, r0 + 0.2, t) * (1.0 - S._ss(r1 + 1.0, r1 + 2.1, t)))
        if ea > 0.002:
            jobs.append(("__enc__", ea))
        if jobs:
            self.R.f_out.use()
            self.ctx.enable(self.mgl.BLEND)
            self.ctx.blend_func = (self.mgl.ONE, self.mgl.ONE_MINUS_SRC_ALPHA)
            for name, a in jobs:
                lay = self._enc_layer() if name == "__enc__" else self._frag_layer(name)
                self._quad(self.p_ovl, self.v_ovl, lay, -1.0, uAlpha=float(a),
                           uDis=(-1.0, 0.0, 0.0, 0.0))
            self.ctx.blend_func = (self.mgl.ONE, self.mgl.ONE)
            self.ctx.disable(self.mgl.BLEND)
            drew = True
        return drew
