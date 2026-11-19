"""Song 05 "God Bless You!", version 2: the 2D layer drawn over every finished frame.

  1. the bottom third calmed (performers stand in front of it: no bright reflections, rings or particles)
  2. the opening card, whole and readable from frame 0 for more than 7 s: the campaign logo, HEALING CONCERT,
     "The Words of Mother's Love" / "That Bring Peace" (italic), and the song's title large; it then lifts away
     as fine gold dust (tools/nine_colours_minor/cards.py lockup style, on the bright sky palette)
  3. the signature, from the end of the opening to the last frame, small in the TOP LEFT corner: the logo mark,
     "God Bless You!", "The Words of Mother's Love That Bring Peace", "DEC 6 · 4:30 PM" (the brightest line),
     "HEALING CONCERT · LAS VEGAS". Never flashes, never covered.
  4. the words (words2d.py): navy #1f2a6b with a soft white glow, each moment with its own way in and out;
     the expressions gather into their star of the arch.

Stage time t (seconds of the video) for the opening and the signature; reference time r for the words (they
follow the music and the people). Pure functions of time: any frame can be drawn alone.
No em dash or en dash anywhere in this file.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

import words2d as W2

NAVY = W2.NAVY
GOLD = (180, 132, 44)
CORAL = (226, 74, 88)
SEP = "  ·  "
OPEN_SOLID = 7.4          # stage seconds the opening stays whole (the rule: at least 7)
OPEN_GONE = 9.0
SIG_IN = (8.4, 9.8)


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _blur(a, r):
    return gaussian_filter(a, r, mode="constant") if r > 0 else a


def _hash(n, salt):
    rng = np.random.default_rng(salt)
    return rng.random(n)


class Layer:
    """A crisp RGBA picture placed on the frame, with its soft white glow, a noise map for dissolves and
    sample points on its ink."""

    def __init__(self, rgba, x0, y0, s, glow=(9.0, 0.95), veil=(38.0, 0.40), n_pts=2400, seed=1):
        a = rgba.astype(np.float32) / 255.0
        self.x0, self.y0 = int(x0), int(y0)
        self.h, self.w = a.shape[:2]
        self.alpha = a[..., 3]
        self.rgb = a[..., :3]
        g = np.clip(_blur(self.alpha, glow[0] * s) * 2.6, 0, 1) * glow[1]
        v = np.clip(_blur(self.alpha, veil[0] * s) * 3.0, 0, 1) * veil[1]
        self.white = np.clip(np.maximum(g, v), 0, 1)
        rng = np.random.default_rng(seed)
        n = _blur(rng.random(self.alpha.shape).astype(np.float32), 1.6 * s)
        r = np.empty(n.size, np.float32)
        r[np.argsort(n.ravel(), kind="stable")] = np.linspace(0, 1, n.size, dtype=np.float32)
        self.noise = r.reshape(n.shape)
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        ys, xs = np.nonzero(self.alpha > 0.5)
        self.xn = (xx - xs.min()) / max(np.ptp(xs), 1)
        self.yn = (yy - ys.min()) / max(np.ptp(ys), 1)
        pick = rng.choice(len(xs), size=min(n_pts, len(xs)), replace=False)
        self.px = xs[pick].astype(np.float32) + self.x0
        self.py = ys[pick].astype(np.float32) + self.y0
        self.pi = (ys[pick], xs[pick])
        self.pr = rng.random((len(pick), 4)).astype(np.float32)

    def paste(self, F, mask, k=1.0, dy=0.0, white_k=1.0):
        """Composite onto frame F (float rgb 0..1): the white glow, then the letters, both times mask."""
        y0 = self.y0 + int(round(dy))
        ya, yb = max(y0, 0), min(y0 + self.h, F.shape[0])
        xa, xb = max(self.x0, 0), min(self.x0 + self.w, F.shape[1])
        if yb <= ya or xb <= xa:
            return
        sl = (slice(ya - y0, yb - y0), slice(xa - self.x0, xb - self.x0))
        m = mask[sl] * k
        reg = F[ya:yb, xa:xb]
        wg = (self.white[sl] * np.clip(m * 1.4, 0, 1) * white_k)[..., None]
        reg[:] = reg * (1 - wg) + wg
        al = (self.alpha[sl] * m)[..., None]
        reg[:] = reg * (1 - al) + self.rgb[sl] * al


class Dots:
    """Soft dots splatted onto the frame: light (screen blend) or paint (over)."""

    def __init__(self, w, h):
        self.w, self.h = w, h

    def draw(self, F, x, y, radius, color, alpha, mode="light"):
        x, y = np.asarray(x, np.float64), np.asarray(y, np.float64)
        alpha = np.broadcast_to(np.asarray(alpha, np.float64), x.shape)
        ok = (alpha > 0.003) & (x > -20) & (x < self.w + 20) & (y > -20) & (y < self.h + 20)
        if not ok.any():
            return
        x, y, alpha = x[ok], y[ok], alpha[ok]
        rad = np.broadcast_to(np.asarray(radius, np.float64), ok.shape)[ok] if np.ndim(radius) else radius
        r = float(np.max(rad)) if np.ndim(rad) else float(rad)
        pad = int(4 * r + 6)
        xa, xb = max(int(x.min()) - pad, 0), min(int(x.max()) + pad + 1, self.w)
        ya, yb = max(int(y.min()) - pad, 0), min(int(y.max()) + pad + 1, self.h)
        if xb <= xa or yb <= ya:
            return
        acc = np.zeros((yb - ya, xb - xa), np.float32)
        ix = np.clip(np.round(x).astype(int) - xa, 0, xb - xa - 1)
        iy = np.clip(np.round(y).astype(int) - ya, 0, yb - ya - 1)
        np.add.at(acc, (iy, ix), alpha * (np.asarray(rad) ** 2 if np.ndim(rad) else r * r) * 6.0)
        acc = np.clip(_blur(acc, r), 0, 1.0)[..., None]
        col = np.asarray(color, np.float32).reshape(1, 1, 3)
        reg = F[ya:yb, xa:xb]
        if mode == "light":
            reg[:] = 1 - (1 - reg) * (1 - acc * col)
        else:
            reg[:] = reg * (1 - acc) + col * acc


def _hexf(c):
    return np.array(W2._hex(c), np.float32) / 255.0


class Overlay:
    def __init__(self, w, h, mod):
        self.w, self.h, self.mod = w, h, mod
        self.s = h / 1080.0
        self.words = mod.WORDS
        self.dots = Dots(w, h)
        self.layers = {}
        self._opening()
        self._signature()

    # ------------------------------------------------------------------ helpers
    def _cam(self, r):
        cam = self.mod.CAMERA
        try:
            return cam.state(r, self.w / self.h)
        except TypeError:
            return cam.state(r)

    def _screen(self, r, p):
        xy, z = self._cam(r).project(np.asarray(p, np.float64).reshape(1, 3))
        return float(xy[0, 0] * self.w), float((1 - xy[0, 1]) * self.h)

    def _logo(self, height, glow=0.0):
        from p3d import brand
        pad = 0.06
        im = brand.logo_image(int(round(height)), pad=pad, glow=glow)
        _, (bx0, by0, bx1, by1) = brand.logo_box(int(round(height)), pad)
        return im, bx0, by0, bx1 - bx0, by1 - by0

    # ------------------------------------------------------------------ the opening card
    def _opening(self):
        s, W, H = self.s, self.w, self.h
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx = W / 2.0
        top = 0.40 * H - 262 * s
        logo, ox, oy, lw, lh = self._logo(132 * s)
        im.alpha_composite(logo, (int(round(cx - lw / 2 - ox)), int(round(top - oy))))
        y = top + lh + 24 * s
        W2.tracked(d, (cx, y), "HEALING CONCERT", W2.font("jo", 500, 28 * s), GOLD + (255,), 9 * s)
        y += 44 * s
        d.text((cx, y), "The Words of Mother’s Love", font=W2.font("cg", 500, 62 * s), fill=NAVY + (255,),
               anchor="ma")
        y += 66 * s
        d.text((cx, y), "That Bring Peace", font=W2.font("cg", 500, 54 * s, italic=True), fill=NAVY + (255,),
               anchor="ma")
        y += 80 * s
        d.line((cx - 70 * s, y, cx + 70 * s, y), fill=GOLD + (210,), width=max(1, int(round(2 * s))))
        y += 18 * s
        d.text((cx, y), "God Bless You!", font=W2.font("cg", 600, 128 * s), fill=NAVY + (255,), anchor="ma")
        a = np.asarray(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        m = int(60 * s)
        x0, x1, y0, y1 = max(xs.min() - m, 0), min(xs.max() + m, W), max(ys.min() - m, 0), min(ys.max() + m, H)
        self.op = Layer(a[y0:y1, x0:x1], x0, y0, s, glow=(10.0, 0.9), veil=(60.0, 0.55), n_pts=5000, seed=3)
        self.op_box = (xs.min(), ys.min(), xs.max(), ys.max())

    def _draw_opening(self, F, t):
        if t >= OPEN_GONE:
            return
        L = self.op
        u = float(_ss(OPEN_SOLID, OPEN_GONE - 0.2, t))
        if u <= 0.0:
            L.paste(F, np.ones_like(L.alpha))
            return
        # the whole card lifts a little and fades as one (never broken letters), shedding fine gold dust
        k = 1.0 - u
        L.paste(F, np.ones_like(L.alpha), k, dy=-24 * self.s * u)
        pr = L.pr
        sel = pr[:, 3] < 0.35
        x = L.px[sel] + (pr[sel, 0] - 0.4) * 50 * self.s * u
        y = L.py[sel] - 24 * self.s * u - (30 + 90 * pr[sel, 1]) * self.s * u
        self.dots.draw(F, x, y, 1.6 * self.s, _hexf("#e8b24a"), 0.6 * np.sin(np.pi * u) * (0.5 + 0.5 * pr[sel, 2]),
                       "paint")

    # ------------------------------------------------------------------ the signature
    def _signature(self):
        s, W, H = self.s, self.w, self.h
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        mx, my = 60 * s, 50 * s
        logo, ox, oy, lw, lh = self._logo(100 * s)
        blk = 150 * s
        im.alpha_composite(logo, (int(round(mx - ox)), int(round(my + (blk - lh) / 2 - oy))))
        tx = mx + lw + 22 * s
        d.text((tx, my - 6 * s), "God Bless You!", font=W2.font("cg", 600, 44 * s, italic=True),
               fill=NAVY + (255,))
        d.text((tx, my + 44 * s), "The Words of Mother’s Love That Bring Peace",
               font=W2.font("cg", 600, 26 * s, italic=True), fill=NAVY + (235,))
        W2.tracked(d, (tx, my + 78 * s), "DEC 6" + SEP + "4:30 PM", W2.font("jo", 600, 33 * s), NAVY + (255,),
                   4 * s, align="left")
        W2.tracked(d, (tx, my + 124 * s), "HEALING CONCERT" + SEP + "LAS VEGAS", W2.font("jo", 500, 19 * s),
                   CORAL + (255,), 4 * s, align="left")
        a = np.asarray(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        m = int(30 * s)
        x0, x1, y0, y1 = max(xs.min() - m, 0), min(xs.max() + m, W), max(ys.min() - m, 0), min(ys.max() + m, H)
        self.sig = Layer(a[y0:y1, x0:x1], x0, y0, s, glow=(6.0, 0.95), veil=(26.0, 0.45), n_pts=10, seed=4)
        self.sig_box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)

    def _draw_signature(self, F, t):
        k = float(_ss(*SIG_IN, t))
        if k > 0.0:
            self.sig.paste(F, np.ones_like(self.sig.alpha), k)

    # ------------------------------------------------------------------ the bottom third
    def _calm(self, F):
        H, W = F.shape[:2]
        y0 = int(0.58 * H)
        reg = F[y0:]
        small = Image.fromarray((np.clip(reg, 0, 1) * 255).astype(np.uint8)).resize(
            (max(W // 24, 1), max((H - y0) // 24, 1)), Image.BOX)
        soft = np.asarray(small.resize((W, H - y0), Image.BICUBIC), np.float32) / 255.0
        yy = (np.arange(y0, H, dtype=np.float32) / H)[:, None, None]
        w = 0.80 * _ss(0.685, 0.80, yy)
        out = reg * (1 - w) + soft * w
        # no bright glints: highlights above the soft water are held down
        lum = out.mean(axis=2, keepdims=True)
        slum = soft.mean(axis=2, keepdims=True)
        over = np.maximum(lum - (slum + 0.04), 0.0)
        out = out - over * (1.0 * _ss(0.68, 0.76, yy))
        # and no broad bright glow either: the water stays within a little of its row's own brightness
        row = np.median(soft.mean(axis=2), axis=1)[:, None, None]
        over2 = np.maximum(out.mean(axis=2, keepdims=True) - (row + 0.07), 0.0)
        out = out - over2 * (0.9 * _ss(0.69, 0.78, yy))
        # below two thirds of the height the water keeps only its soft colour: no reflection of a person, the
        # tree or a light reaches into the performers' third (Never 9)
        tiny = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).resize(
            (max(W // 160, 2), max((H - y0) // 6, 2)), Image.BOX)
        flat = np.asarray(tiny.resize((W, H - y0), Image.BICUBIC), np.float32) / 255.0
        lum_f = flat.mean(axis=2, keepdims=True)
        row = np.median(lum_f, axis=1, keepdims=True)
        flat = flat - np.maximum(lum_f - (row + 0.03), 0.0)
        w2 = 0.94 * _ss(0.668, 0.705, yy)
        out = out * (1 - w2) + flat * w2
        reg[:] = np.clip(out, 0, 1)

    # ------------------------------------------------------------------ the words
    def _layer(self, it):
        if it.name not in self.layers:
            rgba, x0, y0 = it.build(self.s)
            self.layers[it.name] = Layer(rgba, x0, y0, self.s, n_pts=2600 if it.kind == "expr" else 1600,
                                         seed=hash(it.name) % 1000)
        return self.layers[it.name]

    def _star_xy(self, it, r):
        return self._screen(r, self.mod.arch_point(it.star, r))

    def _draw_word(self, F, it, r):
        L = self._layer(it)
        s = self.s
        if r < it.t_read0:
            a = float(_ss(it.t_in, it.t_read0, r)) if it.t_read0 > it.t_in else 1.0
            getattr(self, "_in_" + it.arrive)(F, it, L, a, r)
        elif r <= it.t_read1:
            L.paste(F, np.ones_like(L.alpha))
        else:
            l = float(np.clip((r - it.t_read1) / max(it.t_out - it.t_read1, 1e-6), 0, 1))
            getattr(self, "_out_" + it.leave)(F, it, L, l, r)

    # arrivals ---------------------------------------------------------
    def _in_pen(self, F, it, L, a, r):
        order = L.xn
        front = -0.08 + 1.16 * a
        mask = _ss(-0.08, 0.0, front - order).astype(np.float32)
        L.paste(F, mask)
        o = order[L.pi]
        d = front - o
        live = (d > -0.01) & (d < 0.08)
        if live.any():
            k = 1.0 - d[live] / 0.08
            pr = L.pr[live]
            self.dots.draw(F, L.px[live] + (pr[:, 0] - .5) * 6 * self.s, L.py[live] - 8 * self.s * (1 - k),
                           2.2 * self.s, _hexf(it.color), 0.8 * k, "light")

    def _flyer_arrive(self, F, it, L, a, r, order, color, start, mode, radius, wobble=0.0, grow=False):
        """Particles fly from start(i) to their place on the letters; each letter appears as its own arrive."""
        o = order[L.pi]
        front = -0.1 + 1.25 * a
        land = np.clip((front - o) / 0.32, 0, 1)
        mask = np.full_like(L.alpha, float(_ss(0.45, 1.0, a)))
        L.paste(F, mask)
        on = (land > 0) & (land < 1)
        if not on.any():
            return
        pr = L.pr[on]
        e = 1 - (1 - land[on]) ** 2.2
        sx, sy = start(pr)
        x = sx + (L.px[on] - sx) * e + wobble * self.s * np.sin(r * 2.3 + pr[:, 2] * 9) * (1 - e)
        y = sy + (L.py[on] - sy) * e + wobble * 0.5 * self.s * np.cos(r * 1.9 + pr[:, 3] * 9) * (1 - e)
        al = np.where(e > 0.85, (1 - e) / 0.15, 1.0) * 0.9
        rad = radius * self.s * (0.4 + 0.6 * e if grow else 1.0)
        self.dots.draw(F, x, y, rad, color, al, mode)

    def _in_petals(self, F, it, L, a, r):
        order = 0.75 * L.xn + 0.25 * L.noise
        self._flyer_arrive(F, it, L, a, r, order, _hexf("#f3a0b8"),
                           lambda pr: (-0.05 * self.w + 0.3 * self.w * pr[:, 0], (0.05 + 0.25 * pr[:, 1]) * self.h),
                           "paint", 2.6, wobble=60.0)

    def _in_sunbeam(self, F, it, L, a, r):
        order = 0.8 * L.yn + 0.2 * L.xn
        front = -0.1 + 1.75 * a
        mask = _ss(-0.65, 0.0, front - order).astype(np.float32)        # a soft fade from the top, never a cut
        L.paste(F, mask)
        # the shaft of sun that writes it: a warm band down through the letters, brightest at the writing line
        band = np.exp(-((order - front + 0.3) / 0.25) ** 2) * (L.white > 0.02)
        k = float(np.sin(np.pi * min(a * 1.1, 1.0)))
        ya, xa = L.y0, L.x0
        reg = F[ya:ya + L.h, xa:xa + L.w]
        g = (0.7 * k * band * np.clip(L.white * 2, 0, 1))[..., None]
        reg[:] = 1 - (1 - reg) * (1 - g * _hexf("#ffd88a"))

    def _in_ripen(self, F, it, L, a, r):
        order = L.noise
        o = order[L.pi]
        front = -0.15 + 1.3 * a
        grow = np.clip((front - o) / 0.35, 0, 1)
        L.paste(F, np.full_like(L.alpha, float(_ss(0.35, 0.95, a))))
        on = (grow > 0) & (grow < 1)
        sel = on & (np.arange(len(o)) % 3 == 0)
        if sel.any():
            g = grow[sel]
            self.dots.draw(F, L.px[sel], L.py[sel], 3.6 * self.s * np.sin(np.pi * g) + 0.5, _hexf("#e9a73a"),
                           0.85 * np.sin(np.pi * g), "paint")

    def _in_seeds(self, F, it, L, a, r):
        order = 0.6 * L.noise + 0.4 * (1 - L.yn)
        tx, ty = self._screen(r, self.mod.TREE_AT + np.array([0.0, 2.2, 0.0]))
        self._flyer_arrive(F, it, L, a, r, order, _hexf("#ffd27a"),
                           lambda pr: (tx + (pr[:, 0] - .5) * 160 * self.s, ty + (pr[:, 1] - .5) * 90 * self.s),
                           "light", 2.0, wobble=40.0)

    # leavings ---------------------------------------------------------
    def _out_star(self, F, it, L, l, r):
        sx, sy = self._star_xy(it, r)
        order = L.xn
        front = -0.15 + 1.3 * min(l / 0.7, 1.0)
        mask = (1.0 - _ss(-0.15, 0.0, front - order)).astype(np.float32)
        L.paste(F, mask)
        o = order[L.pi]
        go = np.clip((l - o * 0.7) / 0.30, 0, 1)
        on = (go > 0) & (go < 1)
        col = _hexf(it.color)
        if on.any():
            pr = L.pr[on]
            e = go[on] ** 1.4 * (3 - 2 * go[on])
            e = np.clip(e / 2.0 * 2.0, 0, 1)
            x0, y0 = L.px[on], L.py[on]
            cx1 = x0 + (pr[:, 0] - .5) * 120 * self.s
            cy1 = y0 - (60 + 80 * pr[:, 1]) * self.s
            x = (1 - e) ** 2 * x0 + 2 * (1 - e) * e * cx1 + e * e * sx
            y = (1 - e) ** 2 * y0 + 2 * (1 - e) * e * cy1 + e * e * sy
            self.dots.draw(F, x, y, 3.0 * self.s, col * 0.92, 0.85 * (1 - 0.5 * e), "paint")
            self.dots.draw(F, x, y, 1.4 * self.s, np.ones(3, np.float32), 0.35 * (1 - e), "light")
        # the star flares as the last light arrives
        got = float(np.mean(go >= 1.0)) if len(go) else 0.0
        if got > 0.02:
            k = got * (1.0 - float(_ss(0.92, 1.0, l)) * 0.5)
            self.dots.draw(F, np.array([sx]), np.array([sy]), 14 * self.s, col, np.array([0.9 * k]), "light")
            self.dots.draw(F, np.array([sx]), np.array([sy]), 4 * self.s, np.ones(3, np.float32),
                           np.array([0.8 * k]), "light")

    def _out_petals_away(self, F, it, L, l, r):
        order = L.xn
        front = -0.15 + 1.3 * l
        L.paste(F, (1.0 - _ss(-0.15, 0.0, front - order)).astype(np.float32))
        o = order[L.pi]
        go = np.clip((front - o + 0.05 * L.pr[:, 3]) / 0.75, 0, 1)
        on = (go > 0) & (go < 1) & (np.arange(len(o)) % 3 == 0)
        if on.any():
            pr = L.pr[on]
            g = go[on] ** 0.8
            x = L.px[on] + (180 + 380 * pr[:, 0]) * self.s * g + 30 * self.s * np.sin(r * 3 + pr[:, 2] * 7)
            y = L.py[on] + (pr[:, 1] - 0.6) * 220 * self.s * g + 60 * self.s * g * g
            self.dots.draw(F, x, y, 2.2 * self.s, _hexf("#f3a0b8"), 0.6 * (1 - g), "paint")

    def _out_rise(self, F, it, L, l, r):
        k = 1.0 - float(_ss(0.0, 1.0, l))
        L.paste(F, np.ones_like(L.alpha), k, dy=-26 * self.s * l)
        sel = np.arange(len(L.px)) % 4 == 0
        g = l
        pr = L.pr[sel]
        self.dots.draw(F, L.px[sel] + (pr[:, 0] - .5) * 30 * self.s, L.py[sel] - (40 + 120 * pr[:, 1]) * self.s * g,
                       1.8 * self.s, _hexf("#ffd27a"), 0.7 * np.sin(np.pi * g) * (pr[:, 2] > 0.4), "light")

    def _out_fall(self, F, it, L, l, r):
        order = L.xn
        front = -0.15 + 1.3 * l
        L.paste(F, (1.0 - _ss(-0.15, 0.0, front - order)).astype(np.float32))
        o = order[L.pi]
        go = np.clip((front - o + 0.05 * L.pr[:, 3]) / 0.75, 0, 1)
        on = (go > 0) & (go < 1) & (np.arange(len(o)) % 3 == 0)
        if on.any():
            pr = L.pr[on]
            g = go[on]
            x = L.px[on] + 40 * self.s * np.sin(r * 2.2 + pr[:, 2] * 8) * g + (pr[:, 0] - 0.3) * 160 * self.s * g
            y = L.py[on] + (60 + 160 * pr[:, 1]) * self.s * g
            self.dots.draw(F, x, y, 2.2 * self.s, _hexf("#f6b6c6"), 0.6 * (1 - g), "paint")

    def _out_fade(self, F, it, L, l, r):
        L.paste(F, np.ones_like(L.alpha), 1.0 - float(_ss(0.0, 1.0, l)), dy=-14 * self.s * l)

    # ------------------------------------------------------------------ hearts
    def _heart_sprite(self, color, px):
        key = (color, px)
        if key not in self.layers:
            n = int(px * 4)
            th = np.linspace(0, 2 * np.pi, 120)
            x = 16 * np.sin(th) ** 3
            y = 13 * np.cos(th) - 5 * np.cos(2 * th) - 2 * np.cos(3 * th) - np.cos(4 * th)
            pts = list(zip(n / 2 + x * n / 36, n / 2 - y * n / 36 - n * 0.03))
            im = Image.new("L", (n, n), 0)
            ImageDraw.Draw(im).polygon(pts, fill=255)
            im = im.resize((int(px), int(px)), Image.LANCZOS)
            a = np.asarray(im, np.float32) / 255.0
            self.layers[key] = (a, _hexf(color))
        return self.layers[key]

    def _draw_hearts(self, F, r):
        for expr, (who, part), t0, t1 in getattr(self.mod, "HEARTS", []):
            if not (t0 - 0.1 <= r <= t1 + 3.6):
                continue
            color = W2.expressions()[expr]["color"]
            rate, life = 3.0, 3.4
            k = int(np.ceil((t1 - t0) * rate))
            rng = np.random.default_rng(int(t0 * 10))
            sd = rng.random((k, 5))
            birth = t0 + (np.arange(k) + 0.6 * sd[:, 0]) / rate
            boxes = [it.box(self.s) for it in self.words.on(r)]
            for i in range(k):
                age = r - birth[i]
                if age < 0 or age > life:
                    continue
                src = self.mod.CAST.where(who, birth[i] + 0.0 * age, part)
                x, y = self._screen(r, src)
                x += (sd[i, 1] - 0.5) * 50 * self.s + 14 * self.s * np.sin(age * 2.0 + sd[i, 2] * 6)
                y -= (40 + 30 * sd[i, 3]) * self.s * age
                al = float(_ss(0, 0.4, age) * (1 - _ss(life - 1.2, life, age))) * 0.9
                for bx0, by0, bx1, by1 in boxes:
                    if bx0 - 30 * self.s < x < bx1 + 30 * self.s and by0 - 30 * self.s < y < by1 + 30 * self.s:
                        al = 0.0
                if al <= 0.01:
                    continue
                px = int(round((24 + 10 * sd[i, 4]) * self.s * (0.8 + 0.2 * min(age, 1)))) | 1
                a, col = self._heart_sprite(color, px)
                xa, ya = int(round(x - px / 2)), int(round(y - px / 2))
                if xa < 0 or ya < 0 or xa + px > self.w or ya + px > int(0.66 * self.h):
                    continue
                reg = F[ya:ya + px, xa:xa + px]
                m = (a * al)[..., None]
                glow = np.clip(_blur(a, 2.0 * self.s) * 1.5, 0, 1)[..., None] * al * 0.6
                reg[:] = reg * (1 - glow) + glow
                reg[:] = reg * (1 - m) + col * m

    # ------------------------------------------------------------------ the frame
    def apply(self, data, t, r, R=None):
        F = np.frombuffer(data, np.uint8).reshape(self.h, self.w, 3).astype(np.float32) / 255.0
        self._calm(F)
        self._draw_hearts(F, r)
        for it in self.words.on(r):
            self._draw_word(F, it, r)
        self._draw_opening(F, t)
        self._draw_signature(F, t)
        return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
