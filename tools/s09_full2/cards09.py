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
        _tracked(d, (tx, my + 118 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", JO(500, 18 * s), acc + (235,),
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

    def overlay(self, t):
        drew = super().overlay(t)
        S = self._song()
        jobs = [(name, S.frag_alpha(name, t)) for name in S.FRAG_TEXT]
        jobs = [(n, a) for n, a in jobs if a > 0.002]
        if jobs:
            self.R.f_out.use()
            self.ctx.enable(self.mgl.BLEND)
            self.ctx.blend_func = (self.mgl.ONE, self.mgl.ONE_MINUS_SRC_ALPHA)
            for name, a in jobs:
                self._quad(self.p_ovl, self.v_ovl, self._frag_layer(name), -1.0, uAlpha=float(a),
                           uDis=(-1.0, 0.0, 0.0, 0.0))
            self.ctx.blend_func = (self.mgl.ONE, self.mgl.ONE)
            self.ctx.disable(self.mgl.BLEND)
            drew = True
        return drew
