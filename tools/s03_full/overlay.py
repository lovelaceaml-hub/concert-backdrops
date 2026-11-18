"""Song 03 full backdrop: what is drawn over the engine's finished frame, in the Revision 3 style.

- The two expressions (Apology, Encouragement) in Claude Final v1's look: the label in Jost capitals inside a
  thin capsule of the expression's website colour, the phrase in cream Cormorant Garamond italic with a warm
  halo; written left to right by a soft pen of light, read 10 seconds, then the letters let go and a comet of
  the expression's colour carries them to their light in the arch.
- Text protection: behind the words the scene is softened (blurred) and calmed a little, so no spark, raindrop
  or ray crosses a letter, and nothing dark sits behind them.
- The song title card at the opening, born from the petal's ring, and gone before the verse.
- Nine coloured comets (words.EXPRESSIONS colours): a whole life drawn across the sky in chorus 1, and a spiral
  round the rising sun at the climax of chorus 2.

Everything is a pure function of t (no state between frames), so parallel parts match.
No em dash or en dash anywhere in this file.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FONTS = os.path.join(REPO, "fonts")

# words.EXPRESSIONS (pinned commit f43f451): exact wording and website colours
APOLOGY = dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"],
               color="#F6CE46", t_in=26.5, t_read0=28.5, t_read1=38.5, t_arrive=41.0, star=2)
ENCOURAGEMENT = dict(label="Encouragement",
                     lines=["“I’ll pray (or root) for you.", "Everything will go well.”"],
                     color="#9E6AF6", t_in=222.5, t_read0=224.5, t_read1=234.3, t_arrive=236.8, star=6)
EXPRESSIONS = [APOLOGY, ENCOURAGEMENT]
NINE = ["#EA5A5E", "#F2B25E", "#F6CE46", "#5ABA5A", "#62B2FA", "#667AF6", "#9E6AF6", "#EE62A6", "#364E96"]
NINE_GLOW = ["#EA5A5E", "#F2B25E", "#F6CE46", "#5ABA5A", "#62B2FA", "#97A5FA", "#9E6AF6", "#EE62A6", "#8C9FEA"]
CREAM = (255, 244, 220)
CENTRE_Y = 0.345           # centre of a text block, from the top of the frame
TITLE_CARD = dict(t_in=3.2, t_full=6.0, t_out=16.6, t_gone=19.0)
LOVE = dict(t_in=337.6, t_full=339.4, t_out=358.6, t_gone=360.6)   # "I love You Mother" painted over its petals
COMETS_LIFE = 134.8        # chorus 1: nine comets draw a life from the left shore to the right
COMETS_SPIRAL = (319.4, 325.7)   # chorus 2 climax: nine comets spiral round the sun, burst on the hit


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + ".ttf"), max(int(round(size)), 4))


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _tracked(draw, cx, y, text, font, fill, track):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    x = cx - total / 2.0
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, anchor="ls")
        x += w + track
    return total


class Block:
    """One pre-drawn text block: letters (alpha), halo (alpha), colours, the area it covers."""

    def __init__(self, W, H, letters, halo, rgb_letters, rgb_halo, box):
        self.letters, self.halo = letters, halo
        self.rgb_l = np.asarray(rgb_letters, np.float32) / 255.0
        self.rgb_h = np.asarray(rgb_halo, np.float32) / 255.0
        self.box = box   # x0, y0, x1, y1 in pixels
        ys, xs = np.nonzero(letters > 0.02)
        self.xn = np.zeros_like(letters)
        if len(xs):
            x0, x1 = xs.min(), xs.max()
            ramp = (np.arange(letters.shape[1], dtype=np.float32) - x0) / max(x1 - x0, 1)
            self.xn[:] = ramp[None, :]
        # protection mask: the letters' area grown and softened
        m = Image.fromarray(np.clip(halo * 4.0 * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
        m = m.filter(ImageFilter.GaussianBlur(max(int(18 * H / 1080), 2)))
        self.prot = np.asarray(m, np.float32) / 255.0


class Overlay:
    def __init__(self, W, H, song):
        self.W, self.H, self.S = W, H, song
        self.s = H / 1080.0
        self.blocks = {e["label"]: self._expression(e) for e in EXPRESSIONS}
        self.title = self._title_card()
        self.love = self._love()
        self.sprites = {}

    # ------------------------------------------------------------------ pictures (built once)
    def _crop(self, layers, pad=6):
        a = np.maximum.reduce([np.asarray(l, np.float32) for l in layers])
        ys, xs = np.nonzero(a > 1)
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, self.W)
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, self.H)
        return x0, y0, x1, y1

    def _expression(self, e):
        W, H, s = self.W, self.H, self.s
        col = _hex(e["color"])
        L = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(L)
        f_phrase = _font("cormorant-garamond-latin-600-italic", 104 * s)
        f_label = _font("jost-latin-500-normal", 34 * s)
        line_h = 112 * s
        label_h = 74 * s
        block_h = label_h + line_h * len(e["lines"])
        top = CENTRE_Y * H - block_h / 2.0
        # the label in capitals, tracked, inside a thin capsule of its colour
        label = e["label"].upper()
        lab_y = top + 44 * s
        tw = _tracked(d, W / 2.0, lab_y, label, f_label, 255, 7 * s)
        cap = Image.new("L", (W, H), 0)
        dc = ImageDraw.Draw(cap)
        px, ph = 30 * s, 54 * s
        cy = lab_y - 12 * s
        box = (W / 2 - tw / 2 - px, cy - ph / 2, W / 2 + tw / 2 + px, cy + ph / 2)
        dc.rounded_rectangle(box, radius=ph / 2, outline=255, width=max(int(round(2.6 * s)), 1))
        fill = Image.new("L", (W, H), 0)
        ImageDraw.Draw(fill).rounded_rectangle(box, radius=ph / 2, fill=255)
        for k, line in enumerate(e["lines"]):
            d.text((W / 2.0, top + label_h + line_h * (k + 0.78)), line, font=f_phrase, fill=255, anchor="ms")
        letters = np.asarray(L, np.float32) / 255.0
        halo = np.asarray(L.filter(ImageFilter.GaussianBlur(10 * s)), np.float32) / 255.0
        wide = np.asarray(L.filter(ImageFilter.GaussianBlur(34 * s)), np.float32) / 255.0
        capa = np.asarray(cap, np.float32) / 255.0
        capg = np.asarray(cap.filter(ImageFilter.GaussianBlur(8 * s)), np.float32) / 255.0
        filla = np.asarray(fill.filter(ImageFilter.GaussianBlur(2 * s)), np.float32) / 255.0
        x0, y0, x1, y1 = self._crop([L, cap.filter(ImageFilter.GaussianBlur(40 * s)),
                                     L.filter(ImageFilter.GaussianBlur(40 * s))], pad=40)
        sl = (slice(y0, y1), slice(x0, x1))
        b = Block(W, H, letters[sl], np.maximum(halo[sl], 0.6 * wide[sl]), CREAM, col, (x0, y0, x1, y1))
        b.cap, b.capg, b.fill = capa[sl], capg[sl], filla[sl]
        b.col = np.asarray(col, np.float32) / 255.0
        b.cx, b.cy = W / 2.0, CENTRE_Y * H
        return b

    def _title_card(self):
        W, H, s = self.W, self.H, self.s
        L = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(L)
        y = 0.33 * H
        d.text((W / 2, y), "I Reminisce About Your Love", font=_font("cormorant-garamond-latin-500-normal", 108 * s),
               fill=255, anchor="ms")
        _tracked(d, W / 2, y + 74 * s, "THE WORDS OF MOTHER’S LOVE", _font("jost-latin-400-normal", 30 * s),
                 235, 8 * s)
        d.text((W / 2, y + 126 * s), "Healing Concert", font=_font("cormorant-garamond-latin-500-italic", 46 * s),
               fill=235, anchor="ms")
        letters = np.asarray(L, np.float32) / 255.0
        halo = np.asarray(L.filter(ImageFilter.GaussianBlur(12 * s)), np.float32) / 255.0
        x0, y0, x1, y1 = self._crop([L.filter(ImageFilter.GaussianBlur(40 * s))], pad=40)
        sl = (slice(y0, y1), slice(x0, x1))
        b = Block(W, H, letters[sl], halo[sl], CREAM, (255, 196, 140), (x0, y0, x1, y1))
        return b

    def _love(self):
        """The closing words, painted in deep rose with a gold edge exactly over the engine's petal letters, so
        they read on the bright dawn sky (light alone would pale to white there)."""
        W, H, s = self.W, self.H, self.s
        L = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(L)
        d.text((W / 2.0, (0.392 - 0.05) * H), "I love You Mother",
               font=_font("cormorant-garamond-latin-600-italic", 120 * s), fill=255, anchor="ms")
        letters = np.asarray(L, np.float32) / 255.0
        edge = np.asarray(L.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.6 * s)), np.float32) / 255.0
        halo = np.asarray(L.filter(ImageFilter.GaussianBlur(16 * s)), np.float32) / 255.0
        x0, y0, x1, y1 = self._crop([L.filter(ImageFilter.GaussianBlur(40 * s))], pad=40)
        sl = (slice(y0, y1), slice(x0, x1))
        b = Block(W, H, letters[sl], halo[sl], (178, 62, 98), (255, 236, 200), (x0, y0, x1, y1))
        b.edge = edge[sl]
        return b

    def _sprite(self, r):
        r = max(int(round(r)), 1)
        if r not in self.sprites:
            n = 3 * r
            yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
            q = (xx * xx + yy * yy) / float(r * r)
            self.sprites[r] = (np.exp(-q * 2.2) + 0.22 * np.exp(-q * 0.35)).astype(np.float32)
        return self.sprites[r]

    def _stamp(self, img, x, y, r, rgb, k):
        sp = self._sprite(r)
        n = sp.shape[0] // 2
        xi, yi = int(round(x)), int(round(y))
        x0, y0 = xi - n, yi - n
        x1, y1 = x0 + sp.shape[1], y0 + sp.shape[0]
        cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, self.W), min(y1, self.H)
        if cx0 >= cx1 or cy0 >= cy1:
            return
        part = sp[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        img[cy0:cy1, cx0:cx1] += part[..., None] * (np.asarray(rgb, np.float32) * k)

    # ------------------------------------------------------------------ the frame
    def _protect(self, img, b, k):
        """Soften and calm the scene behind a text block (k 0..1)."""
        if k <= 0.002:
            return
        x0, y0, x1, y1 = b.box
        reg = img[y0:y1, x0:x1]
        small = Image.fromarray(np.clip(reg * 255, 0, 255).astype(np.uint8)).reduce(4)
        small = small.filter(ImageFilter.GaussianBlur(5))
        soft = np.asarray(small.resize((x1 - x0, y1 - y0), Image.BILINEAR), np.float32) / 255.0
        m = (b.prot * k)[..., None]
        calm = soft * 0.80
        img[y0:y1, x0:x1] = reg * (1 - m) + calm * m

    def _draw_block(self, img, b, reveal, alpha, pen=True):
        """reveal 0..1: the pen's progress left to right; alpha: overall strength."""
        if alpha <= 0.002:
            return
        x0, y0, x1, y1 = b.box
        reg = img[y0:y1, x0:x1]
        front = -0.08 + 1.16 * reveal
        g = np.clip((front - b.xn) / 0.08, 0.0, 1.0)
        heat = np.exp(-np.maximum(front - b.xn, 0.0) / 0.05) * (b.xn < front) if pen and reveal < 1.0 else 0.0
        la = (b.letters * g * alpha)[..., None]
        ha = (b.halo * g * alpha)[..., None]
        # warm halo of the expression's colour (light, added), then the cream letters laid over it
        reg += ha * (0.55 * b.rgb_h + 0.25)[None, None, :] * 0.55
        lc = b.rgb_l[None, None, :] * (1.0 + 0.6 * np.asarray(heat, np.float32)[..., None] if pen else 1.0)
        reg[:] = reg * (1 - la * 0.92) + la * lc
        if hasattr(b, "cap"):
            ca = (np.clip(front * 1.6, 0, 1) if pen else 1.0) * alpha
            reg += (b.capg[..., None] * 0.55 + b.fill[..., None] * 0.10) * b.col[None, None, :] * ca
            reg[:] = reg * (1 - b.cap[..., None] * ca * 0.9) + b.cap[..., None] * ca * (0.25 + 0.85 * b.col)
        img[y0:y1, x0:x1] = reg

    def _expression_state(self, e, t):
        """(protect, reveal, alpha) for an expression at t."""
        if not (e["t_in"] - 1.0 <= t <= e["t_arrive"] + 0.5):
            return 0.0, 0.0, 0.0
        prot = float(_ss(e["t_in"] - 1.0, e["t_in"] + 0.6, t) * (1 - _ss(e["t_read1"] + 0.4, e["t_read1"] + 2.0, t)))
        reveal = float(_ss(e["t_in"], e["t_read0"], t))
        alpha = float(_ss(e["t_in"], e["t_in"] + 0.5, t) * (1 - _ss(e["t_read1"], e["t_read1"] + 1.3, t)))
        return prot, reveal, alpha

    def _flight(self, img, e, b, t):
        """The letters let go: a comet of the expression's colour carries them to its light in the arch."""
        t0, t1 = e["t_read1"] + 0.4, e["t_arrive"]
        if not (t0 <= t <= t1 + 0.3):
            return
        sx, sy = self.S.STAR_POS[e["star"]]
        tx, ty = sx * self.W, (1.0 - sy) * self.H
        ox, oy = b.cx, b.cy
        col = np.asarray(_hex(e["color"]), np.float32) / 255.0
        cream = np.asarray(CREAM, np.float32) / 255.0

        def at(u):
            u = float(np.clip(u, 0, 1))
            e_ = u * u * (3 - 2 * u)
            # a gentle arc, rising
            mx, my = 0.5 * (ox + tx) + 0.10 * self.W * (1 if tx > ox else -1) * 0, min(oy, ty) - 0.06 * self.H
            x = (1 - e_) ** 2 * ox + 2 * (1 - e_) * e_ * mx + e_ * e_ * tx
            y = (1 - e_) ** 2 * oy + 2 * (1 - e_) * e_ * my + e_ * e_ * ty
            return x, y

        u = (t - t0) / (t1 - t0)
        fade = 1.0 - float(_ss(t1, t1 + 0.3, t))
        for j in range(90):
            uu = u - j * 0.005
            if uu < 0:
                break
            x, y = at(uu)
            k = (1 - j / 90.0) ** 1.6 * fade
            self._stamp(img, x, y, (7 - 5 * j / 90.0) * self.s, 0.5 * col + 0.5 * cream, 0.40 * k)
        if u <= 1.0:
            x, y = at(u)
            self._stamp(img, x, y, 9 * self.s, 0.3 * col + 0.7 * cream, 0.9 * fade)

    def _comet(self, img, path, u, col, life=60, width=6.0, k=1.0, step=0.010):
        cream = np.asarray(CREAM, np.float32) / 255.0
        c = np.asarray(_hex(col), np.float32) / 255.0
        for j in range(life):
            uu = u - j * step
            if uu < 0.0:
                break
            if uu > 1.0:
                continue
            x, y = path(uu)
            a = (1 - j / float(life)) ** 1.5
            self._stamp(img, x, y, max(width * (1 - 0.7 * j / life), 1.2) * self.s, c * 0.85 + 0.15 * cream, 0.60 * a * k)
        if 0.0 <= u <= 1.0:
            x, y = path(u)
            self._stamp(img, x, y, (width + 3) * self.s, c * 0.45 + 0.55 * cream, 0.85 * k)

    def _comets(self, img, t):
        W, H = self.W, self.H
        # chorus 1: a whole life from beginning to end, one after another, under the arch
        t0 = COMETS_LIFE
        if t0 - 0.5 <= t <= t0 + 18.0:
            for i in range(9):
                start = t0 + 0.55 * i
                dur = 9.5
                u = (t - start) / dur
                if u < 0 or u > 1.0 + 0.6:
                    continue
                apex = 0.42 - 0.026 * i     # from the top; under the arch (which sits above 0.19)
                x0, x1 = (0.05 + 0.012 * i) * W, (0.95 - 0.012 * i) * W
                y0 = (1 - 0.315) * H

                def path(v, apex=apex, x0=x0, x1=x1, y0=y0, i=i):
                    x = x0 + (x1 - x0) * v
                    y = y0 - (y0 - apex * H) * np.sin(np.pi * v) ** 0.85 - 0.01 * H * np.sin(6.0 * v + i)
                    return x, y

                k = float(_ss(0.0, 0.05, u) * (1 - _ss(1.0, 1.55, u)))
                self._comet(img, path, min(u, 1.0 + 0.6), NINE_GLOW[i], life=150, width=6.0, k=k, step=0.0035)
        # chorus 2 climax: nine comets rise from the sun in a widening spiral and burst on the hit
        a, b = COMETS_SPIRAL
        if a - 0.2 <= t <= b + 2.2:
            sx, sy = 0.30 * W, (1 - 0.40) * H
            for i in range(9):
                ph = 2 * np.pi * i / 9.0

                def path(v, ph=ph):
                    r = (0.02 + 0.30 * v) * H
                    ang = ph + 2.6 * np.pi * v
                    return sx + 1.25 * r * np.cos(ang) + 0.30 * W * v, sy - 0.65 * r * np.sin(ang) - 0.12 * H * v

                u = (t - a) / (b - a)
                k = float(_ss(0.0, 0.08, u) * (1 - _ss(1.0, 1.0 + 2.0 / (b - a), u)))
                self._comet(img, path, min(u, 1.0), NINE_GLOW[i], life=130, width=5.0, k=k, step=0.004)
            if b <= t <= b + 2.2:
                # the burst: a soft ring of the nine colours, rising sparks fading
                q = (t - b) / 2.2
                for i in range(9):
                    for m in range(5):
                        ang = 2 * np.pi * (i / 9.0 + m / 45.0)
                        r = (0.31 + 0.10 * q) * H
                        x = sx + 1.25 * r * np.cos(ang + 2.6 * np.pi) + 0.30 * W
                        y = sy - 0.65 * r * np.sin(ang + 2.6 * np.pi) - 0.12 * H - 0.04 * H * q
                        self._stamp(img, x, y, 3.0 * self.s, np.asarray(_hex(NINE_GLOW[i]), np.float32) / 255.0,
                                    0.5 * (1 - q) ** 2)

    def apply(self, data, t):
        W, H = self.W, self.H
        img = np.frombuffer(data, np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
        touched = False
        # the opening title card
        tc = TITLE_CARD
        if tc["t_in"] <= t <= tc["t_gone"]:
            b = self.title
            alpha = float(_ss(tc["t_in"], tc["t_full"], t) * (1 - _ss(tc["t_out"], tc["t_gone"], t)))
            self._protect(img, b, 0.6 * alpha)
            self._draw_block(img, b, 1.0, alpha, pen=False)
            touched = True
        lv = LOVE
        if lv["t_in"] <= t <= lv["t_gone"]:
            b = self.love
            a = float(_ss(lv["t_in"], lv["t_full"], t) * (1 - _ss(lv["t_out"], lv["t_gone"], t)))
            x0, y0, x1, y1 = b.box
            reg = img[y0:y1, x0:x1]
            reg += (b.halo * a * 0.35)[..., None] * b.rgb_h[None, None, :]       # a soft cream glow (light)
            ea = (b.edge * a * 0.95)[..., None]
            reg[:] = reg * (1 - ea) + ea * np.asarray([1.0, 0.86, 0.55], np.float32)   # sunlit gold edge
            la = (b.letters * a * 0.95)[..., None]
            reg[:] = reg * (1 - la) + la * b.rgb_l                                # deep rose letters
            img[y0:y1, x0:x1] = reg
            touched = True
        for e in EXPRESSIONS:
            prot, reveal, alpha = self._expression_state(e, t)
            b = self.blocks[e["label"]]
            if prot > 0.002 or alpha > 0.002:
                self._protect(img, b, prot)
                self._draw_block(img, b, reveal, alpha)
                touched = True
            if e["t_read1"] <= t <= e["t_arrive"] + 0.4:
                self._flight(img, e, b, t)
                touched = True
        if (COMETS_LIFE - 0.5 <= t <= COMETS_LIFE + 18.0) or (COMETS_SPIRAL[0] - 0.2 <= t <= COMETS_SPIRAL[1] + 2.3):
            self._comets(img, t)
            touched = True
        if not touched:
            return data
        # soft shoulder: keep highlights under clipping (no white-outs)
        hi = img > 0.86
        if hi.any():
            img = np.where(hi, 0.86 + 0.14 * np.tanh((img - 0.86) / 0.14), img)
        return (np.clip(img, 0, 1) * 255.0 + 0.5).astype(np.uint8).tobytes()
