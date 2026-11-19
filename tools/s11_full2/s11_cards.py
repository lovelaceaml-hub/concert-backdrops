"""Song 11's cards: the approved opening lockup and signature (engine/titles.py, as resized for Revision 3 in
tools/nine_colours_minor/cards.py) with the song title added, and the official end card with the closing tagline.
The three methods below are the engine's own, copied with only those additions marked SONG_TITLE and TAGLINE."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import cards
from titles import CG, JO, OF, PALETTES, SEP, _tracked, _crop

SONG_TITLE = "Almighty God Who Knows the Future"
TAGLINE = "Where a mother\u2019s love reaches, peace settles."


class Cards(cards.Cards):
    def _opening(self, pal):
        """N4: the logo, HEALING CONCERT, the title (its second line in italic), a gold hairline, the date line,
        LAS VEGAS, all centred. The logo's slot is kept free when there is no logo, so the lockup never moves."""
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        lines = self._title_lines()
        lh = 130.0                                         # the logo slot (1080p pixels), then a gap of 28
        two = len(lines) > 1
        total = lh + 28 + 320 + 30 - (0 if two else 102) + 150
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        cx = W / 2.0
        top = self.op["y"] * H - total * s / 2.0           # the top of the logo slot
        lg = self._logo("opening", lh * s, pal)
        self.op_logo = None
        if lg is not None:
            im, ox, oy, lw = lg
            bx, by = cx - lw / 2.0, top + lh * s - (im.height - 2 * oy)
            L.alpha_composite(im, (int(round(bx - ox)), int(round(by - oy))))
            self.op_logo = (int(round(bx - ox)), int(round(by - oy)), im.width, im.height)
        y = top + (lh + 28) * s
        _tracked(d, (cx, y), "HEALING CONCERT", JO(500, 30 * s), acc + (255,), 9 * s)
        d.text((cx, y + 40 * s), lines[0], font=CG(500, 96 * s), fill=col + (255,), anchor="ma")
        if two:
            d.text((cx, y + 142 * s), lines[1], font=CG(500, 70 * s, it=True), fill=col + (255,), anchor="ma")
        else:
            y -= 102 * s
        d.line((cx - 60 * s, y + 242 * s, cx + 60 * s, y + 242 * s), fill=acc + (200,), width=max(1, int(round(2 * s))))
        d.text((cx, y + 262 * s), SONG_TITLE, font=CG(600, 112 * s), fill=col + (255,), anchor="ma")
        y += 150
        _tracked(d, (cx, y + 262 * s), "SUNDAY, DECEMBER 6" + SEP + "4:30 PM", JO(500, 40 * s), col + (255,), 6 * s)
        _tracked(d, (cx, y + 320 * s), "LAS VEGAS", JO(400, 26 * s), acc + (235,), 8 * s)
        return self._finish(L, 14, 0.55, pal, noise=True, prot=getattr(self, "op_prot", (40.0, 16.0)))
    def _signature(self, corner, pal):
        """N5: the logo mark on the outer side, then the title in italic on one line, DEC 6 · 4:30 PM, and
        HEALING CONCERT · LAS VEGAS, aligned toward the logo (left in the left corners, mirrored in the right).
        A little larger than the mockup (1.1) so the date reads on a phone. Until there is a logo a thin gold
        hairline stands in its place."""
        s, W, H = self.s * 1.1, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        line = " ".join(self._title_lines())
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        right = corner[1] == "r"
        mx, my = 104 * self.s, 92 * self.s                 # margins: well inside the frame on a phone
        blk = 156.0 * s                                     # height of the block of three lines
        y0 = (H - my - blk) if corner[0] == "b" else my
        lg = self._logo("signature", 96 * s, pal)
        if lg is not None:
            im, ox, oy, lw = lg
            lhh = im.height - 2 * oy
            lx = (W - mx - lw) if right else mx
            L.alpha_composite(im, (int(round(lx - ox)), int(round(y0 + (blk - lhh) / 2.0 - oy))))
            gap = lw + 22 * s
        else:
            hx = (W - mx) if right else mx
            d.line((hx, y0 + 6 * s, hx, y0 + blk - 6 * s), fill=acc + (220,), width=max(1, int(round(2 * self.s))))
            gap = 22 * s
        tx = (W - mx - gap) if right else (mx + gap)
        al = "right" if right else "left"
        d.text((tx, y0 - 4 * s), SONG_TITLE, font=CG(600, 40 * s), fill=col + (250,), anchor="ra" if right else "la")
        y0 += 44 * s
        d.text((tx, y0 - 4 * s), line, font=CG(500, 34 * s, it=True), fill=col + (235,), anchor="ra" if right else "la")
        _tracked(d, (tx, y0 + 44 * s), "DEC 6" + SEP + "4:30 PM", JO(500, 30 * s), col + (255,), 5 * s, align=al)
        small = P.get("small")
        _tracked(d, (tx, y0 + 88 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", JO(500 if small else 400, 22 * s),
                 (small or acc) + (255 if small else 230,), 5 * s,
                 align=al)
        return self._finish(L, 9, 0.5, pal, prot=getattr(self, "sig_prot", (40.0, 16.0)))
    def _end_card(self):
        """N6 (Anthony approved, after the official campaign poster): the logo, HEALING CONCERT (Outfit 600, coral,
        tracked), "The Words of" (Outfit 500, navy), "Mother's Love" (Outfit 800, large, coral, a little tight),
        "That Bring Peace" (Outfit 800, a deep blue gradient), a coral ribbon with notched ends holding
        "Sunday, December 6" in yellow and " · 4:30 PM" in white, then the church and the address (Outfit 500,
        navy). Returns the text layer and the veil of light behind it (two layers: the veil fades, the text
        sweeps in)."""
        W, H = self.w, self.h
        ec = self.ec
        k = self.s * ec["scale"]
        NAVY, CORAL, BLUE1, BLUE2, YEL = (39, 39, 81), (243, 87, 99), (3, 69, 165), (3, 45, 129), (255, 228, 120)
        lines = self._title_lines()
        first = lines[0]
        # "The Words of" / "Mother's Love": the official poster splits the first line before its last two words
        cut = first.rsplit(" ", 2)
        small, big = (cut[0], " ".join(cut[1:])) if len(cut) == 3 else ("", first)
        last = lines[1] if len(lines) > 1 else ""
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)

        def tr(cx, y, text, f, fill, track):
            """Tracked like the mockup: each letter at the width of the text before it (kerning kept)."""
            x = cx - (f.getlength(text) + track * (len(text) - 1)) / 2.0
            for i, c in enumerate(text):
                d.text((x + f.getlength(text[:i]) + track * i, y), c, font=f, fill=fill)

        lg = self._logo("end_card", 170.0 * k, "day")
        cx = W / 2.0
        if lg is not None:
            im, ox, oy, lw = lg
            lx, ly = self._ec_xy(960.0, 48.0)
            L.alpha_composite(im, (int(round(lx - lw / 2.0 - ox)), int(round(ly - oy))))
        tr(cx, self._ec_xy(0, 236)[1], "HEALING CONCERT", OF(600, 30 * k), CORAL + (255,), 9 * k)
        if small:
            tr(cx, self._ec_xy(0, 278)[1], small, OF(500, 78 * k), NAVY + (255,), -2 * k)
        tr(cx, self._ec_xy(0, 352)[1], big, OF(800, 176 * k), CORAL + (255,), -4 * k)
        if last:
            m = Image.new("L", (W, H), 0)
            dm = ImageDraw.Draw(m)
            f = OF(800, 124 * k)
            x = cx - (f.getlength(last) - 3 * k * (len(last) - 1)) / 2.0
            y = self._ec_xy(0, 540)[1]
            for i, c in enumerate(last):
                dm.text((x + f.getlength(last[:i]) - 3 * k * i, y), c, font=f, fill=255)
            bb = m.getbbox()
            u = np.clip((np.arange(H, dtype=np.float32) - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)[:, None, None]
            g = np.asarray(BLUE1, np.float32) * (1 - u) + np.asarray(BLUE2, np.float32) * u
            G = Image.fromarray(np.broadcast_to(g, (H, W, 3)).astype(np.uint8)).convert("RGBA")
            G.putalpha(m)
            L.alpha_composite(G)
            d = ImageDraw.Draw(L)
        # the ribbon with notched ends, like the official theme banner
        (rx0, ry0), (rx1, ry1), notch = self._ec_xy(520, 712), self._ec_xy(1400, 792), 34 * k
        d.polygon([(rx0 - notch, ry0), (rx1 + notch, ry0), (rx1, (ry0 + ry1) / 2), (rx1 + notch, ry1),
                   (rx0 - notch, ry1), (rx0, (ry0 + ry1) / 2)], fill=CORAL + (255,))
        f = OF(600, 44 * k)
        p1, p2 = ec["day"], "  \u00b7  " + ec["time"]
        x = cx - (f.getlength(p1) + f.getlength(p2)) / 2.0
        y = self._ec_xy(0, 728)[1]
        d.text((x, y), p1, font=f, fill=YEL + (255,))
        d.text((x + f.getlength(p1), y), p2, font=f, fill=(255, 255, 255, 255))
        for i, ln in enumerate(ec["place"][:2]):
            tr(cx, self._ec_xy(0, 826 + 52 * i)[1], ln, OF(500, 42 * k), NAVY + (255,), 0)
        d.text((cx, self._ec_xy(0, 948)[1]), TAGLINE, font=CG(600, 54 * k, it=True), fill=CORAL + (255,), anchor="ma")
        T = self._finish(L, 10, 0.7, "day", noise=True)
        # the soft veil of light behind the block (light, never dark)
        v = Image.new("L", (W, H), 0)
        (vx0, vy0), (vx1, vy1) = self._ec_xy(360, 40), self._ec_xy(1560, 1040)
        ImageDraw.Draw(v).ellipse((vx0, vy0, vx1, vy1), fill=int(round(150 * min(ec["veil"], 1.7))))
        va = np.asarray(v.filter(ImageFilter.GaussianBlur(120 * k)), np.float32) / 255.0
        vo = np.zeros(va.shape + (4,), np.float32)
        vo[..., :3] = (np.asarray((255, 247, 234), np.float32) / 255.0)[None, None, :] * va[..., None]
        vo[..., 3] = 0.75 * va
        (vo,), (x0, y0, x1, y1) = _crop([vo])
        V = dict(tex=self._tex(vo), rect=(x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H), box=(x0, y0, x1, y1))
        if ec["backdrop"]:
            self.ec_back = self._pastel()
        return T, V
