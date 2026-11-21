"""The concert lockups of the version 2 backdrops, drawn over the finished picture (engine/titles.py does the
timing, the text protection and the dissolve; only the two pictures are new here).

Opening (from frame 0, held at least 7 s, on calm sky): the campaign logo above, the small label HEALING
CONCERT, "The Words of Mother's Love" / "That Bring Peace" (second line italic), a gold hairline, the song
title large, then the date line and LAS VEGAS small. The style is the approved Revision 3 lockup
(tools/nine_colours_minor/cards.py over engine/titles.py): Cormorant for the title lines, Jost for the
capitals, warm white with gold accents and a soft warm glow on a night sky.

Signature (the same in all eleven songs, from the end of the opening to the last frame, top left): the
logo mark, then the song title (Cormorant italic), "The Words of Mother's Love That Bring Peace" (Cormorant
italic, smaller), "DEC 6 · 4:30 PM" (Jost 500 capitals, the brightest line, capitals about 23 px tall at
1080p) and "HEALING CONCERT · LAS VEGAS" (Jost, gold). It never flashes: one fade in, then steady.
No em dash or en dash anywhere in this file.
"""
from PIL import Image, ImageDraw

import titles
from titles import CG, JO, PALETTES, SEP, _tracked

SONG_TITLE = "Out of Heaven, Favor From God"
# the signature block in 1080p pixels (x0, y0, x1, y1), kept for the clearance check (tools/s08_full2/check.py)
SIG_MARGIN = (96.0, 70.0)


class Lockup(titles.Titles):
    song_title = SONG_TITLE

    def _opening(self, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        lines = self._title_lines()
        lh = 120.0                                    # the logo slot (1080p pixels)
        total = lh + 24 + 44 + 92 + 76 + 30 + 104 + 24 + 50 + 34
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
        _tracked(d, (cx, y), "HEALING CONCERT", JO(500, 30 * s), acc + (255,), 9 * s)
        y += 44 * s
        d.text((cx, y), lines[0], font=CG(500, 80 * s), fill=col + (255,), anchor="ma")
        y += 92 * s
        d.text((cx, y), lines[1] if len(lines) > 1 else "", font=CG(500, 62 * s, it=True), fill=col + (255,),
               anchor="ma")
        y += 76 * s + 14 * s
        d.line((cx - 70 * s, y, cx + 70 * s, y), fill=acc + (210,), width=max(1, int(round(2 * s))))
        y += 16 * s
        d.text((cx, y), self.song_title, font=CG(600, 96 * s), fill=(255, 234, 190, 255), anchor="ma")
        y += 104 * s + 24 * s
        _tracked(d, (cx, y), "SUNDAY, DECEMBER 6" + SEP + "4:30 PM", JO(500, 34 * s), col + (255,), 6 * s)
        y += 50 * s
        _tracked(d, (cx, y), "LAS VEGAS", JO(400, 24 * s), acc + (235,), 8 * s)
        return self._finish(L, 14, 0.55, pal, noise=True, prot=getattr(self, "op_prot", (40.0, 16.0)))

    def _signature(self, corner, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        concert = " ".join(self._title_lines())
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        mx, my = SIG_MARGIN[0] * s, SIG_MARGIN[1] * s
        blk = 136.0 * s
        y0 = my
        lg = self._logo("signature", 92 * s, pal)
        if lg is not None:
            im, ox, oy, lw = lg
            lhh = im.height - 2 * oy
            L.alpha_composite(im, (int(round(mx - ox)), int(round(y0 + (blk - lhh) / 2.0 - oy))))
            gap = lw + 20 * s
        else:
            d.line((mx, y0 + 6 * s, mx, y0 + blk - 6 * s), fill=acc + (220,), width=max(1, int(round(2 * s))))
            gap = 20 * s
        tx = mx + gap
        d.text((tx, y0 - 4 * s), self.song_title, font=CG(600, 34 * s, it=True), fill=col + (245,), anchor="la")
        d.text((tx, y0 + 38 * s), concert, font=CG(500, 24 * s, it=True), fill=col + (225,), anchor="la")
        _tracked(d, (tx, y0 + 70 * s), "DEC 6" + SEP + "4:30 PM", JO(500, 33 * s), col + (255,), 5 * s, align="left")
        _tracked(d, (tx, y0 + 114 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", JO(500, 19 * s), acc + (240,), 5 * s,
                 align="left")
        return self._finish(L, 9, 0.5, pal, prot=getattr(self, "sig_prot", (40.0, 16.0)))
