"""Song 07 v2: the opening lockup and the small signature, in the lockup style of the approved Revision 3
(engine/titles.py, tools/nine_colours_minor/cards.py), as the v2 brief asks for every song:

opening    readable from frame 0 for at least 7 s, on calm sky: the logo (p3d/brand.py), the small label
           HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (italic), a gold hairline, and the
           song title large. Then it crumbles into glowing dust (the approved dissolve).
signature  from the end of the opening to the last frame, small in the TOP LEFT: the logo mark, the song title,
           "The Words of Mother's Love That Bring Peace", "DEC 6 · 4:30 PM" (the brightest line, capitals about
           23 px tall at 1080p) and "HEALING CONCERT · LAS VEGAS". It never flashes.

Both are drawn over the finished picture, after the bloom, with the approved text protection (the scene's light
is dimmed close behind the letters, so nothing crosses them). No em dash or en dash anywhere in this file.
"""
from PIL import Image, ImageDraw

import titles
from titles import CG, JO, PALETTES, SEP, _tracked

SONG_TITLE = "May No One Ever Feel Lonely"
# the signature block in 1080p pixels (also used by the song module to keep words 40 px clear of it)
SIG = dict(x=54.0, y=40.0, logo=92.0)


def signature_box(w=1920, h=1080):
    """(x0, y0, x1, y1) of the signature in pixels, y from the top."""
    s = h / 1080.0
    return (SIG["x"] * s, SIG["y"] * s - 6 * s, 690.0 * s, (SIG["y"] + 150.0) * s)


class Cards07(titles.Titles):
    def _opening(self, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        lines = self._title_lines()
        lh = 120.0
        total = lh + 26 + 34 + 16 + 70 + 62 + 34 + 128
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
        _tracked(d, (cx, y), "HEALING CONCERT", JO(500, 28 * s), acc + (255,), 9 * s)
        y += 50 * s
        d.text((cx, y), lines[0], font=CG(500, 66 * s), fill=col + (255,), anchor="ma")
        y += 70 * s
        d.text((cx, y), lines[1], font=CG(500, 54 * s, it=True), fill=col + (255,), anchor="ma")
        y += 86 * s
        d.line((cx - 70 * s, y, cx + 70 * s, y), fill=acc + (210,), width=max(1, int(round(2 * s))))
        y += 22 * s
        d.text((cx, y), SONG_TITLE, font=CG(600, 104 * s), fill=col + (255,), anchor="ma")
        return self._finish(L, 14, 0.55, pal, noise=True, prot=getattr(self, "op_prot", (40.0, 16.0)))

    def _signature(self, corner, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        mx, y0 = SIG["x"] * s, SIG["y"] * s
        blk = 146.0 * s
        lg = self._logo("signature", SIG["logo"] * s, pal)
        gap = 20 * s
        if lg is not None:
            im, ox, oy, lw = lg
            lhh = im.height - 2 * oy
            L.alpha_composite(im, (int(round(mx - ox)), int(round(y0 + (blk - lhh) / 2.0 - oy))))
            gap = lw + 20 * s
        tx = mx + gap
        d.text((tx, y0 - 4 * s), SONG_TITLE, font=CG(600, 36 * s, it=True), fill=col + (245,), anchor="la")
        d.text((tx, y0 + 40 * s), " ".join(self._title_lines()), font=CG(500, 25 * s, it=True),
               fill=col + (225,), anchor="la")
        _tracked(d, (tx, y0 + 74 * s), "DEC 6" + SEP + "4:30 PM", JO(600, 33 * s), (255, 250, 240, 255), 4 * s,
                 align="left")
        _tracked(d, (tx, y0 + 120 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", JO(500, 20 * s), acc + (240,),
                 5 * s, align="left")
        return self._finish(L, 9, 0.5, pal, prot=getattr(self, "sig_prot", (40.0, 16.0)))
