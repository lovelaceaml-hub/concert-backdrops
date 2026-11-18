"""Song 11's opening lockup, its small signature, the call to action and the end card, version 2, in the Revision 3 type (engine/titles.py).

Opening (DESIGN-SYSTEM 7, PHASEB update 16, brief v2): fully readable from frame 0 and held at least 7 s, on calm
night sky: the logo above, the small label HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace"
(the second line in italic), a gold hairline, then the song title large. Then it crumbles to glowing dust
(engine/titles.py).
Signature, the same in all 11 songs, from the end of the opening to the last frame, small in the TOP LEFT
corner: the logo mark, the song title, "The Words of Mother's Love That Bring Peace", "DEC 6 · 4:30 PM" (the
brightest line, capitals about 22 px tall at 1080p) and "HEALING CONCERT · LAS VEGAS". Warm white with gold
accents and a soft warm glow on the night of the opening; navy #1f2a6b with a soft white glow on the bright sky.
The call to action (DESIGN-SYSTEM 4) before the end card, navy on the bright sky. The end card: the official
campaign card (titles.py N6, as tools/nine_colours_minor/cards.py) with the closing tagline beneath it.
No em dash or en dash anywhere in this file.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SONG_TITLE = "Almighty God Who Knows the Future"


TAGLINE = "Where a mother\u2019s love reaches, peace settles."
CTA_HEAD = "We Are Peacemakers."
CTA_BODY = ["Please spread the Words of Mother\u2019s Love that bring peace", "in your own community. We are all Peacemakers",
            "who bring hope, happiness, and peace", "to every corner of our society!"]
CTA_Y = 0.20                     # the top of the call to action, as a fraction of the height
CTA_T = (247.4, 248.6, 259.6, 260.5)     # reference seconds: in, readable, read end, out (s11v2_song.CTA)


def _s(a, b, x):
    u = min(max((x - a) / max(b - a, 1e-6), 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def make_cards(titles):
    CG, JO, _tracked, PALETTES, SEP = titles.CG, titles.JO, titles._tracked, titles.PALETTES, titles.SEP

    class Cards(titles.Titles):
        def _opening(self, pal):
            s, W, H = self.s, self.w, self.h
            P = PALETTES[pal]
            col, acc = P["col"], P["acc"]
            lines = self._title_lines()                      # The Words of Mother's Love / That Bring Peace
            lh = 118.0
            total = lh + 26 + 40 + 64 + 60 + 34 + 112
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
            y = top + (lh + 26) * s
            _tracked(d, (cx, y), "HEALING CONCERT", JO(500, 30 * s), acc + (255,), 9 * s)
            d.text((cx, y + 40 * s), lines[0], font=CG(500, 58 * s), fill=col + (255,), anchor="ma")
            d.text((cx, y + 104 * s), lines[1], font=CG(500, 50 * s, it=True), fill=col + (255,), anchor="ma")
            d.line((cx - 60 * s, y + 178 * s, cx + 60 * s, y + 178 * s), fill=acc + (200,),
                   width=max(1, int(round(2 * s))))
            d.text((cx, y + 196 * s), SONG_TITLE, font=CG(600, 104 * s), fill=col + (255,), anchor="ma")
            return self._finish(L, 14, 0.55, pal, noise=True, prot=getattr(self, "op_prot", (40.0, 16.0)))

        def _signature(self, corner, pal):
            """Top left: the logo mark, then four lines aligned to its right."""
            s, W, H = self.s, self.w, self.h
            P = PALETTES[pal]
            col, acc = P["col"], P["acc"]
            concert = " ".join(self._title_lines())
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            mx, my = 64 * s, 52 * s
            blk = 150.0 * s
            lg = self._logo("signature", 104 * s, pal)
            if lg is not None:
                im, ox, oy, lw = lg
                lhh = im.height - 2 * oy
                L.alpha_composite(im, (int(round(mx - ox)), int(round(my + (blk - lhh) / 2.0 - oy))))
                gap = lw + 22 * s
            else:
                d.line((mx, my + 6 * s, mx, my + blk - 6 * s), fill=acc + (220,), width=max(1, int(round(2 * s))))
                gap = 22 * s
            tx = mx + gap
            d.text((tx, my - 4 * s), SONG_TITLE, font=CG(600, 40 * s, it=True), fill=col + (245,), anchor="la")
            d.text((tx, my + 42 * s), concert, font=CG(500, 27 * s, it=True), fill=col + (215,), anchor="la")
            _tracked(d, (tx, my + 78 * s), "DEC 6" + SEP + "4:30 PM", JO(500, 31 * s), col + (255,), 5 * s,
                     align="left")
            _tracked(d, (tx, my + 120 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", JO(400, 20 * s), acc + (235,),
                     5 * s, align="left")
            return self._finish(L, 9, 0.5, pal, prot=getattr(self, "sig_prot", (40.0, 16.0)))

        # ------------------------------------------------------------------ the end card with its tagline
        def _end_card(self):
            T, V = super()._end_card()
            k = self.s * self.ec["scale"]
            W, H = self.w, self.h
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            y = self._ec_xy(0, 946)[1]
            d.text((W / 2.0, y), TAGLINE, font=CG(600, 54 * k, it=True), fill=(39, 39, 81, 255), anchor="ma")
            self.ec_tag = self._finish(L, 10, 0.7, "day", noise=True)
            return T, V

        def protect(self, t):
            super().protect(t)
            jobs = []
            ea, ef = self._ec_state(t)
            if ea > 0.002:
                jobs.append((self.ec_tag, titles.KEEP * ea))
            for L, a in self._cta_layers(t) + self._reads(t):
                jobs.append((L, titles.KEEP * a))
            if not jobs:
                return
            ctx = self.ctx
            self.R.f_L.use()
            ctx.enable(self.mgl.BLEND)
            ctx.blend_func = (self.mgl.ZERO, self.mgl.SRC_COLOR)
            for L, kk in jobs:
                self._quad(self.p_prot, self.v_prot, L, 1.0, tex="prot", uK=float(kk))
            ctx.blend_func = (self.mgl.ONE, self.mgl.ONE)


        # ------------------------------------------------------------------ the navy reading letters
        def _song(self):
            return sys.modules["songs.s11v2_song"]

        def _read_layer(self, name):
            key = ("read", name)
            if key not in self.layers:
                S = self._song()
                x0, x1, y0, y1 = S.read_box(name)
                label, lines, lcol = S.read_text(name)
                W, H = self.w, self.h
                bw = (x1 - x0) * W
                cx, cy = 0.5 * (x0 + x1) * W, (1.0 - 0.5 * (y0 + y1)) * H
                path = os.path.join(titles.FONTS, "cormorant-garamond-latin-%s-italic.ttf"
                                    % ("700" if label else "600"))
                probe = ImageFont.truetype(path, 100)
                widest = max(probe.getlength(ln) for ln in lines)
                size = 100.0 * bw * (0.90 if label else 0.92) / max(widest, 1.0)
                f = ImageFont.truetype(path, max(int(round(size)), 8))
                lh = size * 1.12
                L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                d = ImageDraw.Draw(L)
                col = titles.PALETTES["day"]["col"]
                lab_h = 0.0
                if label:
                    lf = JO(500, size * 0.30)
                    track = size * 0.07
                    lab_h = size * 0.62
                total = lab_h + lh * len(lines)
                top = cy - total / 2.0
                if label:
                    tw = sum(lf.getlength(c) for c in label.upper()) + track * (len(label) - 1)
                    ph, pw = size * 0.46, tw + size * 0.55
                    c = tuple(int(lcol[i:i + 2], 16) for i in (1, 3, 5))
                    d.rounded_rectangle((cx - pw / 2, top, cx + pw / 2, top + ph), radius=ph / 2,
                                        fill=c + (255,))
                    _tracked(d, (cx, top + ph * 0.5 - size * 0.30 * 0.36), label.upper(), lf,
                             (255, 255, 255, 255), track)
                for i, ln in enumerate(lines):
                    d.text((cx, top + lab_h + lh * (i + 0.5)), ln, font=f, fill=col + (255,), anchor="mm")
                self.layers[key] = self._finish(L, 10, 0.95, "day")
            return self.layers[key]

        def _reads(self, t):
            S = self._song()
            out = []
            for name in S.READS:
                a = S.read_alpha(name, t)
                if a > 0.002:
                    out.append((self._read_layer(name), a))
            return out

        # ------------------------------------------------------------------ the call to action
        def _cta_build(self):
            if hasattr(self, "cta"):
                return
            s, W, H = self.s, self.w, self.h
            col = titles.PALETTES["day"]["col"]
            L1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L1)
            y0 = CTA_Y * H
            d.text((W / 2.0, y0), CTA_HEAD, font=CG(700, 92 * s), fill=col + (255,), anchor="ma")
            L2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(L2)
            for i, ln in enumerate(CTA_BODY):
                d.text((W / 2.0, y0 + (128 + 58 * i) * s), ln, font=CG(600, 46 * s, it=True), fill=col + (255,),
                       anchor="ma")
            self.cta = (self._finish(L1, 12, 0.75, "day"), self._finish(L2, 10, 0.75, "day"))

        def _cta_layers(self, t):
            a0, r0, r1, a1 = CTA_T
            if t < a0 or t > a1:
                return []
            self._cta_build()
            k1 = float(_s(a0, a0 + 1.0, t) * (1.0 - _s(r1, a1, t)))
            k2 = float(_s(a0 + 0.9, r0 + 0.6, t) * (1.0 - _s(r1, a1, t)))
            return [(self.cta[0], k1), (self.cta[1], k2)]

        def overlay(self, t):
            drew = super().overlay(t)
            mgl = self.mgl
            layers = self._cta_layers(t) + self._reads(t)
            ea, ef = self._ec_state(t)
            if not layers and ea <= 0.002:
                return drew
            self.R.f_out.use()
            self.ctx.enable(mgl.BLEND)
            self.ctx.blend_func = (mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA)
            for L, a in layers:
                self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=float(a), uDis=(-1.0, 0.0, 0.0, 0.0))
            if ea > 0.002:
                L = self.ec_tag
                L["t_noise"].use(location=1)
                self.p_ovl["uNoise"].value = 1
                self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=ea,
                           uDis=(float(ef) if ef is not None else -1.0, 0.30, 0.72, 1.0))
                self._hearts(t, ea)
            self.ctx.blend_func = (mgl.ONE, mgl.ONE)
            self.ctx.disable(mgl.BLEND)
            return True

        def _hearts(self, t, ea):
            """Hearts in the campaign's pastel colours drifting up at the card's outer edges (as the approved
            cards.py), kept clear of the text, the logo and the signature."""
            if not hasattr(self, "heart_tex"):
                self.heart_tex = []
                th = np.linspace(0, 2 * np.pi, 160)
                x = 16 * np.sin(th) ** 3
                y = 13 * np.cos(th) - 5 * np.cos(2 * th) - 2 * np.cos(3 * th) - np.cos(4 * th)
                pts = list(zip(32 + x * 1.7, 30 - y * 1.7))
                for c in ["#f6a2d5", "#9dbff2", "#c0a4ec", "#f5ce86"]:
                    im = Image.new("RGBA", (64, 64))
                    ImageDraw.Draw(im).polygon(pts, fill=c)
                    rgba = np.asarray(im, np.float32) / 255
                    rgba[..., :3] *= rgba[..., 3:]
                    self.heart_tex.append(self._tex(rgba))
            age = t - self.ec["t_in"]
            for j in range(14):
                x = (.035 + .03 * (j % 4)) if j % 2 == 0 else (.85 + .03 * (j % 4))
                x += .009 * np.sin(age * .5 + j)
                y = .40 + (j // 2) * .085 - .010 * age
                if y < .27:
                    y += .62
                size = .012 + .003 * (j % 3)
                layer = dict(tex=self.heart_tex[j % 4], rect=(x, y, size, size * self.w / self.h))
                self._quad(self.p_ovl, self.v_ovl, layer, -1.0, uAlpha=float(ea * .6), uDis=(-1., 0., 0., 0.))

    return Cards
