"""Song 04 full backdrop: the opening lockup and the small signature (the brief for the version 2 backdrops).

Opening (readable from frame 0, whole until t_end - dissolve, at least 7 s): the campaign logo (brand.py) above,
the small label HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace" (second line italic), and the
song title large; the lockup style of tools/nine_colours_minor/cards.py and engine/titles.py (Cormorant
Garamond and Jost). On this song's pale morning sky it is navy with gold accents and a soft white glow.

Signature (from the end of the opening to the last frame, never flashing), small in the TOP LEFT corner: a small
logo mark, the song title, "The Words of Mother's Love That Bring Peace", "DEC 6 · 4:30 PM" (the strongest
line, capitals about 24 px tall at 1080p) and "HEALING CONCERT · LAS VEGAS".
"""
import numpy as np
from PIL import Image, ImageDraw

import titles
from titles import CG, JO, PALETTES, SEP, _tracked

import song as S


class Cards04(titles.Titles):
    def _opening(self, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        lines = self._title_lines()
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        cx = W / 2.0
        lh = 120.0
        total = lh + 24 + 34 + 76 + 64 + 30 + 120
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
        d.text((cx, y + 36 * s), lines[0], font=CG(500, 66 * s), fill=col + (255,), anchor="ma")
        d.text((cx, y + 110 * s), lines[1], font=CG(500, 54 * s, it=True), fill=col + (255,), anchor="ma")
        yl = y + 190 * s
        d.line((cx - 60 * s, yl, cx + 60 * s, yl), fill=acc + (220,), width=max(1, int(round(2 * s))))
        d.text((cx, yl + 22 * s), S.SONG_TITLE, font=CG(600, 104 * s), fill=col + (255,), anchor="ma")
        return self._finish(L, 14, 0.75, pal, noise=True, prot=getattr(self, "op_prot", (40.0, 16.0)))

    def _signature(self, corner, pal):
        s, W, H = self.s, self.w, self.h
        P = PALETTES[pal]
        col, acc = P["col"], P["acc"]
        small = P.get("small") or acc
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        mx, my = 56 * s, 46 * s
        blk = 134.0 * s
        lg = self._logo("signature", 78 * s, pal)
        gap = 18 * s
        if lg is not None:
            im, ox, oy, lw = lg
            lhh = im.height - 2 * oy
            L.alpha_composite(im, (int(round(mx - ox)), int(round(my + (blk - lhh) / 2.0 - oy))))
            gap = lw + 18 * s
        tx = mx + gap
        y0 = my
        d.text((tx, y0 - 4 * s), S.SONG_TITLE, font=CG(600, 32 * s, it=True), fill=col + (255,), anchor="la")
        d.text((tx, y0 + 34 * s), " ".join(self._title_lines()), font=CG(500, 23 * s, it=True), fill=col + (235,),
               anchor="la")
        _tracked(d, (tx, y0 + 66 * s), "DEC 6" + SEP + "4:30 PM", JO(600, 34 * s), col + (255,), 5 * s, align="left")
        _tracked(d, (tx, y0 + 110 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", JO(500, 19 * s), small + (255,),
                 4 * s, align="left")
        return self._finish(L, 9, 0.9, pal, prot=getattr(self, "sig_prot", (40.0, 16.0)))


# ------------------------------------------------------------------------------------------------ the words
# The expressions and the lyric fragments, drawn over the finished picture as crisp navy lettering with a
# soft white glow (this song's sky is pale: DESIGN-SYSTEM 7). Expressions: the coloured capsule label (the
# campaign website's colour, navy letters) above the exact words.EXPRESSIONS phrase in Cormorant Garamond
# italic; they arrive like a pen stroke from the left and, when read, crumble into sparks in their colour
# that fly into their star of the arch. Each fragment has its own effect grown from the song's imagery.
def _ssn(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class TextFX:
    def __init__(self, cards):
        self.C = cards
        self.items = []
        for spec in S.TEXTS:
            self.items.append(self._build(dict(spec)))
        S.TEXT_BOXES.clear()
        for it in self.items:
            x0, y0, x1, y1 = it["L"]["box"]
            W, H = cards.w, cards.h
            S.TEXT_BOXES[it["name"]] = (x0 / W, x1 / W, 1.0 - y1 / H, 1.0 - y0 / H)

    # ---------------------------------------------------------------- building (once)
    def _build(self, sp):
        C = self.C
        s, W, H = C.s, C.w, C.h
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        cx = W / 2.0
        navy = _hex(S.NAVY)
        cy = (1.0 - sp["y"]) * H                     # the block's centre, pixels from the top
        if sp["kind"] == "expr":
            fl = JO(600, 23 * s)
            track = 6 * s
            lab = sp["label"].upper()
            tw = sum(d.textlength(c, font=fl) for c in lab) + track * (len(lab) - 1)
            ph = CG(700, 70 * s, it=True)
            lh = 78 * s
            pill_h = 42 * s
            blk = pill_h + 18 * s + lh * len(sp["lines"])
            top = cy - blk / 2.0
            pw = tw + 2 * 26 * s
            col = _hex(sp["color"])
            d.rounded_rectangle((cx - pw / 2.0, top, cx + pw / 2.0, top + pill_h), radius=pill_h / 2.0,
                                fill=col + (255,))
            _tracked(d, (cx, top + (pill_h - 23 * s * 0.72) / 2.0 - 4 * s), lab, fl, navy + (255,), track)
            y = top + pill_h + 18 * s
            for ln in sp["lines"]:
                d.text((cx, y + lh * 0.5), ln, font=ph, fill=navy + (255,), anchor="mm")
                y += lh
        else:
            ph = CG(600, sp.get("size", 74) * s, it=True)
            d.text((cx, cy), sp["lines"][0], font=ph, fill=navy + (255,), anchor="mm")
        Lf = C._finish(L, 12, 0.95, "day", noise=True)
        # the order letters appear and leave in (0..1 over the block), by style
        a = Lf["a"]
        h, w = a.shape
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        u, v = xx / max(w - 1, 1), yy / max(h - 1, 1)
        n = Lf["noise"]
        st = sp["style"]
        if st == "pen":                  # left to right like a pen, a little irregular
            d_in = 0.80 * u + 0.20 * n
        elif st == "bow":                # from the top down: the letters bow down to the ice
            d_in = 0.75 * v + 0.25 * n
        elif st == "bloom":              # from the middle outward, like a flower opening
            r = np.hypot((u - 0.5) * (w / max(h, 1)) * 0.5, (v - 0.5))
            d_in = 0.8 * r / max(float(r.max()), 1e-6) + 0.2 * n
        elif st == "ripple":             # rings spreading from the water below the middle
            r = np.hypot((u - 0.5) * (w / max(h, 1)) * 0.35, (v - 1.6))
            r = (r - r.min()) / max(float(r.max() - r.min()), 1e-6)
            d_in = 0.85 * r + 0.15 * n
        else:                            # "gather": sparks settle everywhere at once
            d_in = n
        d_in = (d_in - d_in.min()) / max(float(d_in.max() - d_in.min()), 1e-6)
        Lf["t_order"] = C._tex(d_in.astype(np.float32), 1)
        # points on the letters for the sparks
        rng = np.random.default_rng(len(self.items) + 7)
        ys, xs = np.nonzero(a > 0.4)
        m = int(min(9000 * s * s, len(xs)))
        pick = rng.choice(len(xs), size=m, replace=False)
        x0, y0 = Lf["box"][:2]
        sp["pts"] = dict(x=(xs[pick] + x0).astype(np.float32), y=(ys[pick] + y0).astype(np.float32),
                         d=d_in[ys[pick], xs[pick]].astype(np.float32), r=rng.random((m, 5)).astype(np.float32))
        sp["L"] = Lf
        return sp

    # ---------------------------------------------------------------- each frame
    def overlay(self, t):
        C = self.C
        drew = False
        for it in self.items:
            if t < it["t_in"] - 0.1 or t > it["t_out"] + 2.5:
                continue
            L = it["L"]
            e = 0.10
            if t < it["r0"]:
                u = float(_ssn(it["t_in"], it["r0"], t))
                dis = (-e + (1.0 + 2.0 * e) * u, e, 0.0, 1.0)
            elif t <= it["r1"]:
                dis = (-1.0, 0.0, 0.0, 0.0)
            else:
                lv = float(_ssn(it["r1"], it["t_out"], t))
                dis = (-e + (1.0 + 2.0 * e) * lv, e, 0.0, 0.0)
            dy = 0.0
            if it["style"] == "bow":
                dy = -26.0 * C.s * (1.0 - float(_ssn(it["t_in"], it["r0"], t))) + 22.0 * C.s * float(
                    _ssn(it["r1"], it["t_out"], t))
            if dis[0] < 1.0 + e or dis[3] < 0.5:
                if not (dis[3] < 0.5 and dis[0] >= 1.0 + e):
                    L["t_order"].use(location=1)
                    C.p_ovl["uNoise"].value = 1
                    rect = list(L["rect"])
                    rect[1] += dy / C.h
                    C._quad(C.p_ovl, C.v_ovl, dict(L, rect=tuple(rect)), -1.0, uAlpha=1.0, uDis=dis)
                    drew = True
            for batch, additive in self._sparks(it, t, dy):
                C.ctx.blend_func = (C.mgl.ONE, C.mgl.ONE) if additive else (C.mgl.ONE, C.mgl.ONE_MINUS_SRC_ALPHA)
                C._points(batch)
                C.ctx.blend_func = (C.mgl.ONE, C.mgl.ONE_MINUS_SRC_ALPHA)
                drew = True
        return drew

    def _sparks(self, it, t, dy):
        """The light that comes with a word: glints at the arriving edge, and the leaving."""
        C = self.C
        p = it["pts"]
        s = C.s
        out = []
        r = p["r"]
        col = np.asarray(_hex(it.get("spark", it.get("color", "#ffd890"))), np.float32) / 255.0
        warm = np.asarray((1.0, 0.95, 0.85), np.float32)
        # arriving: a few glints where the letters are just appearing
        if it["t_in"] <= t < it["r0"]:
            u = float(_ssn(it["t_in"], it["r0"], t))
            near = np.abs(p["d"] - u) < 0.05
            if it["style"] == "gather":
                # sparks rise from below (the ring of people) and settle into the letters
                k = np.clip((t - it["t_in"]) / max(it["r0"] - it["t_in"], 1e-3) * 1.4 - 0.4 * r[:, 0], 0.0, 1.0)
                k = k * k * (3 - 2 * k)
                sx = p["x"] + (r[:, 1] - 0.5) * 500 * s * (1 - k)
                sy = p["y"] + (300.0 + 300.0 * r[:, 2]) * s * (1 - k)
                a = (1.0 - k) * 0.9 + 0.2
                out.append(((np.stack([sx, sy + dy], 1)[::2], (2.0 + 2.0 * r[::2, 3]) * s,
                             np.concatenate([warm[None, :] * a[::2, None] * 0.8, (a[::2] * 0.8)[:, None]], 1)), True))
            elif near.any():
                xy = np.stack([p["x"][near], p["y"][near] + dy], 1)
                k = 0.9 * (1.0 - np.abs(p["d"][near] - u) / 0.05)
                c = np.concatenate([(0.6 * warm + 0.4 * col)[None, :] * k[:, None], k[:, None]], 1)
                out.append(((xy, (1.8 + 2.0 * r[near, 3]) * s, c), True))
        # leaving
        if it["r1"] < t < it["t_out"] + 2.5:
            lv = (t - it["r1"]) / max(it["t_out"] - it["r1"], 1e-3)
            rel = it["r1"] + (it["t_out"] - it["r1"]) * p["d"]
            age = t - rel
            on = age > 0.0
            if on.any():
                ag, rr = age[on], r[on]
                x0, y0 = p["x"][on], p["y"][on] + dy
                lf = None
                if it["kind"] == "expr":
                    # every spark flies to the star: a gentle curve, arriving by t_out + 0.3
                    sx, sy = S.STAR_POS[it["star"]]
                    gx, gy = sx * C.w, (1.0 - sy) * C.h
                    dur = np.maximum(it["t_out"] + 0.3 - rel[on], 0.35)
                    k = np.clip(ag / dur, 0.0, 1.0)
                    k = k * k * (3 - 2 * k)
                    mx = 0.5 * (x0 + gx) + (rr[:, 1] - 0.5) * 240 * s
                    my = 0.5 * (y0 + gy) - (60 + 140 * rr[:, 2]) * s
                    x = (1 - k) ** 2 * x0 + 2 * (1 - k) * k * mx + k * k * gx
                    y = (1 - k) ** 2 * y0 + 2 * (1 - k) * k * my + k * k * gy
                    a = (0.95 - 0.35 * k) * (1.0 - _ssn(0.85, 1.0, ag / (dur + 0.2)))
                    size = (2.0 + 1.6 * rr[:, 3]) * s * (1.0 - 0.5 * k)
                    c = col * 0.65 + warm * 0.35
                elif it["style"] == "bow":
                    # sinking into the ice: the dust drops a little and melts away
                    life = 1.2 + 0.8 * rr[:, 0]
                    lf = ag / life
                    x = x0 + 8 * s * np.sin(ag * 3 + 6 * rr[:, 4])
                    y = y0 + (40.0 + 60.0 * rr[:, 1]) * s * ag
                    a = np.exp(-lf * 2.0) * (1 - _ssn(0.7, 1.0, lf))
                    size = (1.6 + 1.6 * rr[:, 3]) * s
                    c = np.asarray((0.85, 0.92, 1.0), np.float32)
                elif it["style"] == "bloom":
                    # petals of rose light drifting out and up
                    life = 1.6 + 1.0 * rr[:, 0]
                    lf = ag / life
                    cxm = float(np.mean(p["x"]))
                    x = x0 + np.sign(x0 - cxm) * (30 + 70 * rr[:, 1]) * s * ag + 12 * s * np.sin(ag * 2 + 6 * rr[:, 4])
                    y = y0 - (30 + 50 * rr[:, 2]) * s * ag
                    a = np.exp(-lf * 1.8) * (1 - _ssn(0.7, 1.0, lf))
                    size = (2.4 + 2.0 * rr[:, 3]) * s
                    c = np.asarray((1.0, 0.62, 0.70), np.float32)
                else:
                    # rising softly (ripple and gather)
                    life = 1.4 + 1.0 * rr[:, 0]
                    lf = ag / life
                    x = x0 + 10 * s * np.sin(ag * 2 + 6 * rr[:, 4]) * ag
                    y = y0 - (50 + 80 * rr[:, 2]) * s * ag
                    a = np.exp(-lf * 2.0) * (1 - _ssn(0.7, 1.0, lf))
                    size = (1.8 + 1.6 * rr[:, 3]) * s
                    c = warm
                a = np.clip(a, 0.0, 1.0).astype(np.float32)
                cc = np.concatenate([np.broadcast_to(np.asarray(c, np.float32), (len(a), 3)) * a[:, None],
                                     a[:, None]], 1)
                out.append(((np.stack([x, y], 1).astype(np.float32), size.astype(np.float32) * 2.2,
                             (cc * np.array([0.18, 0.18, 0.18, 0.18], np.float32))), True))
                out.append(((np.stack([x, y], 1).astype(np.float32), size.astype(np.float32), cc), True))
        return out


class Cards04Words(Cards04):
    def __init__(self, renderer):
        super().__init__(renderer)
        self.fx = TextFX(self)

    def overlay(self, t):
        drew = super().overlay(t)
        ctx = self.ctx
        self.R.f_out.use()
        ctx.enable(self.mgl.BLEND)
        ctx.blend_func = (self.mgl.ONE, self.mgl.ONE_MINUS_SRC_ALPHA)
        drew = self.fx.overlay(t) or drew
        ctx.blend_func = (self.mgl.ONE, self.mgl.ONE)
        ctx.disable(self.mgl.BLEND)
        return drew
