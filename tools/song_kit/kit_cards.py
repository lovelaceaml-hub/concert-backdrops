"""The song kit's cards: the shared opening lockup and campaign end card (tools/nine_colours_minor/cards.py, as
in the approved promo) with Song 11's corner signature (tools/s11_full2/s11_cards.py): the logo alone stays in
the corner all film and the song title and the event title appear beside it now and then. The song title comes
from the song's data (song_data.TITLE). No em dash or en dash anywhere in this file.
"""
import cards
from PIL import Image, ImageDraw
from titles import CG, PALETTES


class Cards(cards.Cards):
    def _song_title(self):
        import song_data
        return song_data.TITLE

    def _signature(self, corner, pal):
        """Anthony (2026-11-19): the logo alone stays in the corner all film; the song title and the event title
        ("The Words of Mother's Love That Bring Peace") appear beside it now and then, with no date or place.
        The window's palette carries the part to draw: "night" or "night:logo" is the logo, "night:text" the two
        title lines beside it (two layers, so the logo never blinks when the words come and go)."""
        pal, _, part = pal.partition(":")
        part = part or "logo"
        # (fix, after CORE's light budget: the scene is dark at rest all film, so the corner always takes the
        # night palette, warm white with a soft glow; the "day" navy no longer reads on it)
        pal = "night"
        s, W, H = self.s * 1.1, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        right = corner[1] == "r"
        mx, my = 104 * self.s, 92 * self.s                 # margins: well inside the frame on a phone
        blk = 96.0 * s                                      # the logo's height; the two lines sit centred on it
        y0 = (H - my - blk) if corner[0] == "b" else my
        lg = self._logo("signature", 96 * s, pal)
        lw = lg[3] if lg is not None else 0.0
        if part == "logo":
            if lg is not None:
                im, ox, oy, lw = lg
                lhh = im.height - 2 * oy
                lx = (W - mx - lw) if right else mx
                L.alpha_composite(im, (int(round(lx - ox)), int(round(y0 + (blk - lhh) / 2.0 - oy))))
            else:
                hx = (W - mx) if right else mx
                d.line((hx, y0 + 6 * s, hx, y0 + blk - 6 * s), fill=acc + (220,), width=max(1, int(round(2 * self.s))))
        else:
            gap = lw + 24 * s
            tx = (W - mx - gap) if right else (mx + gap)
            an = "ra" if right else "la"
            d.text((tx, y0 + 2 * s), self._song_title(), font=CG(600, 42 * s), fill=col + (250,), anchor=an)
            d.text((tx, y0 + 50 * s), " ".join(self._title_lines()), font=CG(500, 34 * s, it=True),
                   fill=col + (235,), anchor=an)
        return self._finish(L, 9, 0.5, pal, prot=getattr(self, "sig_prot", (40.0, 16.0)))

    def _sig_alpha(self, t):
        """The logo windows fade quickly at cuts (palette changes); the title lines fade in and out slowly at the
        ends of each appearance (the window's 5th and 6th items: fade in, fade out)."""
        from titles import _ss
        out = []
        f = self.sig_fade if self.sig else 0.6
        wins = list((self.cfg.get("signature") or {}).get("windows", []))
        for i, (a, b, corner, pal, L) in enumerate(self.sig):
            w = wins[i] if i < len(wins) else ()
            fi = float(w[4]) if len(w) > 4 else f
            fo = float(w[5]) if len(w) > 5 else f
            k = float(_ss(a, a + fi, t) * (1.0 - _ss(b - fo, b, t)))
            if k > 0.002:
                out.append((L, k))
        return out
