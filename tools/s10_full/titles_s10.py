"""Song 10's title card (opening) and the small signature, in the Revision 3 type (engine/titles.py).

Opening: the logo, HEALING CONCERT, the song's title "Our Mother Saves the World" large in Cormorant, a gold
hairline, then "The Words of Mother's Love" small beneath; whole from frame 0, it crumbles into glowing dust
(engine/titles.py) by TITLES opening t_end. Signature: as Revision 3 (0.65 of the engine size), bottom left.
No end card (the agreed closing frame for song 11 has none).
No em dash or en dash anywhere in this file.
"""
from PIL import Image, ImageDraw

SONG_TITLE = "Our Mother Saves the World"
CONCERT_LINE = "The Words of Mother’s Love"


def make_cards(titles):
    CG, JO, _tracked, PALETTES = titles.CG, titles.JO, titles._tracked, titles.PALETTES

    class Cards(titles.Titles):
        def _opening(self, pal):
            s, W, H = self.s, self.w, self.h
            P = PALETTES[pal]
            col, acc = P["col"], P["acc"]
            lh = 120.0
            total = lh + 24 + 300
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
            d.text((cx, y + 44 * s), SONG_TITLE, font=CG(500, 112 * s), fill=col + (255,), anchor="ma")
            d.line((cx - 70 * s, y + 196 * s, cx + 70 * s, y + 196 * s), fill=acc + (200,),
                   width=max(1, int(round(2 * s))))
            d.text((cx, y + 214 * s), CONCERT_LINE, font=CG(500, 60 * s, it=True), fill=col + (255,), anchor="ma")
            return self._finish(L, 14, 0.55, pal, noise=True, prot=getattr(self, "op_prot", (40.0, 16.0)))

        def _signature(self, corner, pal):
            scale = self.s
            try:
                self.s *= .65
                return super()._signature(corner, pal)
            finally:
                self.s = scale

    return Cards
