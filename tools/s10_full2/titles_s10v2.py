"""Song 10's opening lockup and its small signature, version 2, in the Revision 3 type (engine/titles.py).

Opening (DESIGN-SYSTEM 7, PHASEB update 16, brief v2): fully readable from frame 0 and held at least 7 s, on calm
night sky: the logo above, the small label HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace"
(the second line in italic), a gold hairline, then the song title large. Then it crumbles to glowing dust
(engine/titles.py).
Signature, the same in all 11 songs, from the end of the opening to the last frame, small in the TOP LEFT
corner: the logo mark, the song title, "The Words of Mother's Love That Bring Peace", "DEC 6 · 4:30 PM" (the
brightest line, capitals about 22 px tall at 1080p) and "HEALING CONCERT · LAS VEGAS". Warm white with gold
accents and a soft warm glow (night palette). No end card (song 11 only).
No em dash or en dash anywhere in this file.
"""
from PIL import Image, ImageDraw

SONG_TITLE = "Our Mother Saves the World"


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

    return Cards
