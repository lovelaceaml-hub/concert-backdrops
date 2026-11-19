"""Song 11's cards: the approved opening lockup and signature (engine/titles.py, as resized for Revision 3 in
tools/nine_colours_minor/cards.py) with the song title added, and the official end card with the closing tagline.
The three drawing methods below are the engine's own, copied with only those additions marked SONG_TITLE and
TAGLINE, and (round 7) the end card's colours turned for a night sky.

Round 7 (Anthony approved; his words for the closing: "closing should be dark, not bright"):
- the opening: the title rests a little dim over the push across the mirror sea and gently brightens on the first
  chord (0:02.32); from 0:10 it draws together into one point of light that drifts down and becomes the star on
  Zion (s11_church.py OPEN_GATHER, OPEN_POINT, OPEN_LAND), so the opening is one continuous journey;
- the closing: the emblem's flare on the last chord (where the nine comets meet, s11_church.py) carries over the
  cut, and the end card dissolves in through it over about a second, set on a deep night sky with stars (the
  Earth faintly glowing through), its text light and crisp; nothing near white over large areas."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import cards
from titles import CG, JO, OF, PALETTES, SEP, _tracked, _crop, _ss, _rgba

SONG_TITLE = "Almighty God Who Knows the Future"
TAGLINE = "Where a mother\u2019s love reaches, peace settles."


def _song():
    """The song's core and the church (loaded by the time the cards are made)."""
    import songs.s11_full2 as H
    import songs.s11_church as C
    return H, C


def _gauss(n, sx=1.0, sy=1.0, p=2.0):
    x = np.linspace(-1.0, 1.0, n, dtype=np.float32)
    return np.exp(-(np.abs(x[None, :] / sx) ** p + np.abs(x[:, None] / sy) ** p) * 4.0)


class Cards(cards.Cards):
    GATHER = 0.7                 # seconds the dissolve front takes to cross the title as it draws together
    LC = 254.07                  # the last chord (the core's LAST_CHORD; checked in __init__)

    def __init__(self, R):
        super().__init__(R)
        H, C = _song()
        assert abs(H.LAST_CHORD - self.LC) < 1e-6
        self.C, self.H = C, H
        if self.ec is not None:
            self.ec["fade"] = 1.1                     # the text sweeps in through the flare in about a second
        self._hide_op = False

    # ------------------------------------------------------------------ the camera, for the lights that cross
    def _screen(self, t, P):
        """Pixel position (x, y from the top) of a world point at t, and its depth."""
        st = self.H.CAMERA.state(t, aspect=self.w / self.h)
        xy, z = st.project(np.asarray(P, np.float64)[None, :])
        return float(xy[0, 0] * self.w), float((1.0 - xy[0, 1]) * self.h), float(z[0])

    # ------------------------------------------------------------------ the opening (round 7)
    def _op_state(self, t):
        """Whole until OPEN_GATHER, then the letters let go along the dissolve front (left to right through the
        noise) and fly together; gone by OPEN_LAND."""
        if self.op is None or self._hide_op or t >= self.C.OPEN_LAND + 0.3:
            return 0.0, None, 1.0
        u = (t - self.C.OPEN_GATHER) / self.GATHER
        if u <= 0.0:
            return 1.0, None, 0.0
        e = 0.06
        return 1.0, -e + (1.0 + 2.0 * e) * min(u, 1.2), float(min(u, 1.0))

    def _op_bright(self, t):
        """The title's light: resting a little dim, it brightens gently on the first chord (0:02.32)."""
        hit = 2.32
        base = 0.8 + 0.2 * float(_ss(hit - 0.05, hit + 1.4, t))
        swell = 0.16 * float(_ss(hit - 0.05, hit + 0.25, t)) * float(np.exp(-max(t - hit - 0.25, 0.0) / 1.6))
        return base, swell

    def _gather_pt(self):
        """Where the title draws together: the middle of the lockup."""
        x0, y0, x1, y1 = self.op_layer["box"]
        return 0.5 * (x0 + x1), 0.5 * (y0 + y1)

    def _star_xy(self, t):
        return self._screen(t, self.C._CROWN)[:2]

    def _light_xy(self, t):
        """The point of light: at the gathering place, then drifting down (a gentle curve) onto the star."""
        C = self.C
        gx, gy = self._gather_pt()
        v = float(_ss(C.OPEN_POINT, C.OPEN_LAND, t))
        if v <= 0.0:
            return gx, gy
        sx, sy = self._star_xy(min(t, C.OPEN_LAND))
        x = gx + (sx - gx) * v + 0.06 * self.w * np.sin(np.pi * v)
        y = gy + (sy - gy) * v ** 1.3
        return x, y

    def _op_gather_points(self, t, front):
        """The letters fly together into one point (each when the dissolve front passes it), a little swirl."""
        p = self.op_pts
        e = 0.06
        rel = self.C.OPEN_GATHER + self.GATHER * (p["d"] - 0.5 * e + e) / (1.0 + 2.0 * e)
        age = t - rel
        r = p["r"]
        T = 0.45 + 0.4 * r[:, 0]
        on = (age > 0.0) & (age < T)
        if not on.any():
            return []
        u = age[on] / T[on]
        rr = r[on]
        gx, gy = self._light_xy(t)
        dx, dy = p["x"][on] - gx, p["y"][on] - gy
        m = 1.0 - u * u * (3.0 - 2.0 * u) * (0.6 + 0.4 * u)
        th = 0.9 * (1.0 - m) * np.where(rr[:, 1] > 0.5, 1.0, -1.0)
        x = gx + m * (dx * np.cos(th) - dy * np.sin(th))
        y = gy + m * (dx * np.sin(th) + dy * np.cos(th))
        k = (0.7 + 0.5 * u) * (1.0 - _ss(0.8, 1.0, u))
        size = (1.5 + 1.8 * rr[:, 3]) * self.s * (1.0 - 0.5 * u)
        xy = np.stack([x, y], axis=1).astype(np.float32)
        glow = np.asarray(PALETTES["night"]["glow"], np.float32) / 255.0
        col = p["col"][on]
        return [((xy[::3], size[::3] * 4.5, _rgba(glow, k[::3] * 0.07, False)), True),
                ((xy, size, _rgba(col, k * 1.3, False)), True)]

    def _light_points(self, t):
        """The single point of light, growing as the letters reach it, then drifting down onto the star with a
        short glittering wake, and fading into it as the star flares (OPEN_LAND)."""
        C = self.C
        if t < C.OPEN_GATHER + 0.15 or t > C.OPEN_LAND + 0.35:
            return []
        m = float(_ss(C.OPEN_GATHER + 0.15, C.OPEN_POINT, t)) * (1.0 - float(_ss(C.OPEN_LAND - 0.1, C.OPEN_LAND + 0.3, t)))
        if m <= 0.003:
            return []
        s = self.s
        warm = np.array((1.0, 0.93, 0.80), np.float32)
        x, y = self._light_xy(t)
        sh = 1.0 - 0.3 * float(_ss(C.OPEN_POINT, C.OPEN_LAND, t))      # a little smaller as it goes far off
        xy = np.array([[x, y]] * 3, np.float32)
        out = [((xy, np.array([300.0, 90.0, 26.0], np.float32) * s * sh,
                 _rgba(warm, np.array([0.16, 0.55, 1.5]) * m, False)), True)]
        if t > C.OPEN_POINT:                                        # the wake
            js = np.arange(1, 31)
            tw = np.maximum(t - 0.02 * js, C.OPEN_POINT)
            P = np.array([self._light_xy(a) for a in tw], np.float32)
            k = m * 0.8 * (1.0 - js / 31.0) ** 1.5
            out.append(((P, (12.0 * s * sh) * (1.0 - js / 40.0), _rgba(warm, k, False)), True))
        return out

    def _draw_opening(self, t):
        a, front, prog = self._op_state(t)
        if not (a > 0.0 and prog < 1.0) and not self._light_points(t):
            return False
        ctx, mgl = self.ctx, self.mgl
        self.R.f_out.use()
        ctx.enable(mgl.BLEND)
        ctx.blend_func = mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA
        if a > 0.0 and prog < 1.0:
            # the soft dark veil behind the title (as in tools/nine_colours_minor/cards.py)
            self.veil_program['uFlip'].value = -1
            self.veil_program['uK'].value = float((.12 + .5 * np.exp(-((t - 6.45) / .65) ** 2)) * (1 - prog))
            self.veil_vao.render(mgl.TRIANGLE_STRIP)
            L = self.op_layer
            L["t_noise"].use(location=1)
            self.p_ovl["uNoise"].value = 1
            base, swell = self._op_bright(t)
            dis = (float(front) if front is not None else -1.0, 0.06, 0.38, 0.0)
            self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=base, uDis=dis)
            if swell > 0.002:                                       # the gentle brightening, added as light
                ctx.blend_func = mgl.ONE, mgl.ONE
                self._quad(self.p_ovl, self.v_ovl, L, -1.0, uAlpha=swell, uDis=dis)
                ctx.blend_func = mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA
            tr = self._trace(t)
            if tr is not None:
                img, (x, y, w, h) = tr
                if self.tr_tex is None or self.tr_tex.size != (w, h):
                    self.tr_tex = self._tex(img)
                else:
                    self.tr_tex.write(np.ascontiguousarray(np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)).tobytes())
                self._quad(self.p_ovl, self.v_ovl, dict(tex=self.tr_tex, rect=(x / self.w, y / self.h, w / self.w,
                                                                                h / self.h)),
                           -1.0, uAlpha=1.0, uDis=(-1.0, 0.0, 0.0, 0.0))
        pts = (self._op_gather_points(t, front) if front is not None else []) + self._light_points(t)
        for batch, additive in pts:
            ctx.blend_func = (mgl.ONE, mgl.ONE) if additive else (mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA)
            self._points(batch)
        ctx.blend_func = (mgl.ONE, mgl.ONE)
        ctx.disable(mgl.BLEND)
        return True

    # ------------------------------------------------------------------ the closing (round 7)
    def _flare_k(self, t):
        """The emblem's flare: it gathers as the comets close in, peaks on the last chord, and dies away in about
        a second while the end card comes in through it."""
        LC = self.LC
        if t < LC - 0.6 or t > LC + 1.5:
            return 0.0
        if t < LC:
            return float(_ss(LC - 0.6, LC, t)) ** 2
        return float(np.exp(-(t - LC) / 0.42)) * (1.0 - float(_ss(LC + 1.0, LC + 1.5, t)))

    def _flare_tex(self):
        if not hasattr(self, "fl_tex"):
            blue = np.array((0.55, 0.80, 1.0), np.float32)
            g = _gauss(256, 0.55, 0.55)                       # the great soft halo: light, and a cover over the cut
            halo = np.zeros((256, 256, 4), np.float32)
            halo[..., :3] = blue * (0.42 * g)[..., None]
            halo[..., 3] = 0.0                            # added as light (the night sky does the covering)
            c = _gauss(128, 0.35, 0.35)                       # the white heart
            core = np.zeros((128, 128, 4), np.float32)
            core[..., :3] = np.array((1.0, 0.97, 0.9), np.float32) * c[..., None]
            st = _gauss(256, 0.9, 0.06, p=1.6)               # a long thin streak across it
            streak = np.zeros((256, 256, 4), np.float32)
            streak[..., :3] = np.array((0.7, 0.86, 1.0), np.float32) * (0.6 * st)[..., None]
            self.fl_tex = [self._tex(halo), self._tex(core), self._tex(streak)]
            # where the emblem is on the screen the moment the comets meet in it
            x, y, _ = self._screen(self.LC - 1.0 / 240.0, self.C.EMB_C)
            self.fl_xy = (x / self.w, y / self.h)
        return self.fl_tex

    def _draw_flare(self, t):
        k = self._flare_k(t)
        if k <= 0.003:
            return False
        halo, core, streak = self._flare_tex()
        fx, fy = self.fl_xy
        asp = self.w / self.h
        ctx, mgl = self.ctx, self.mgl
        self.R.f_out.use()
        ctx.enable(mgl.BLEND)
        ctx.blend_func = mgl.ONE, mgl.ONE_MINUS_SRC_ALPHA

        def put(tex, size_h, wfac, alpha):
            w, h = size_h * wfac / asp, size_h
            self._quad(self.p_ovl, self.v_ovl, dict(tex=tex, rect=(fx - w / 2.0, fy - h / 2.0, w, h)), -1.0,
                       uAlpha=float(alpha), uDis=(-1.0, 0.0, 0.0, 0.0))
        put(halo, 1.5 + 0.4 * k, 1.0, k)
        put(streak, 0.5, 4.0 + 1.5 * k, k)
        put(core, 0.10 + 0.22 * k, 1.0, k)
        ctx.blend_func = mgl.ONE, mgl.ONE
        ctx.disable(mgl.BLEND)
        return True

    def _night_sky(self):
        """The end card's deep night sky (premultiplied, full frame): navy to a deep violet near the bottom, a
        faint blue glow low in the middle where the Earth shows through, and stars."""
        W, H = self.w, self.h
        y = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
        x = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
        top = np.array((5, 7, 22), np.float32) / 255.0
        low = np.array((16, 14, 44), np.float32) / 255.0
        col = top[None, None, :] * (1.0 - y[..., None]) + low[None, None, :] * y[..., None]
        glow = np.exp(-((x / 0.55) ** 2) - (((y - 1.05) / 0.32) ** 2))
        col = col + (np.array((40, 70, 140), np.float32) / 255.0)[None, None, :] * (0.35 * glow)[..., None]
        a = (0.92 - 0.14 * glow).astype(np.float32)          # the Earth's glow comes faintly through, low down
        rng = np.random.default_rng(23)
        n = int(900 * W * H / (1920.0 * 1080.0)) + 60
        sx, sy = rng.random(n) * W, rng.random(n) ** 1.2 * H
        b = (0.15 + 0.85 * rng.random(n) ** 3) * (1.0 - 0.6 * sy / H)
        st = np.zeros((H, W), np.float32)
        ix, iy = sx.astype(int).clip(0, W - 1), sy.astype(int).clip(0, H - 1)
        np.add.at(st, (iy, ix), b)
        st = np.asarray(Image.fromarray(np.clip(st * 255.0, 0, 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(max(0.7 * self.s, 0.5))), np.float32) / 255.0 * 2.2
        tint = np.array((0.86, 0.9, 1.0), np.float32)
        out = np.zeros((H, W, 4), np.float32)
        out[..., :3] = np.clip(col * a[..., None] + tint * np.clip(st, 0.0, 0.9)[..., None], 0.0, 1.0)
        out[..., 3] = a
        return dict(tex=self._tex(out), rect=(0.0, 0.0, 1.0, 1.0))

    def _backdrop_k(self, t):
        """The night sky comes in through the flare: it starts to fall over the church as the flare gathers, is
        mostly in on the cut itself (so the bright Earth view under it never shows), and whole a second later."""
        if self.ec is None or t < self.LC - 0.45:
            return 0.0
        if t < self.LC:
            return 0.3 * float(_ss(self.LC - 0.45, self.LC, t))
        return 0.9 + 0.1 * float(_ss(self.LC, self.LC + 0.9, t))

    def overlay(self, t):
        drew = self._draw_opening(t)
        self._hide_op = True                       # the opening is drawn above; the base draws the rest
        try:
            drew = super().overlay(t) or drew
        finally:
            self._hide_op = False
        return self._draw_flare(t) or drew         # over the night sky as it comes in, dying away in a second

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
        """Anthony (2026-11-19): the logo alone stays in the corner all film; the song title and the event title
        ("The Words of Mother's Love That Bring Peace") appear beside it now and then, with no date or place.
        The window's palette carries the part to draw: "night" or "night:logo" is the logo, "night:text" the two
        title lines beside it (two layers, so the logo never blinks when the words come and go)."""
        pal, _, part = pal.partition(":")
        part = part or "logo"
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
            d.text((tx, y0 + 2 * s), SONG_TITLE, font=CG(600, 42 * s), fill=col + (250,), anchor=an)
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
        # round 7: on the night sky the poster's navy turns to a soft starlight white and its deep blue to the
        # emblem's sky blue; coral, the ribbon and the yellow stay as on the poster
        NAVY, CORAL, BLUE1, BLUE2, YEL = (236, 232, 250), (247, 104, 114), (150, 206, 255), (88, 152, 240), (255, 228, 120)
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

        lg = self._logo("end_card", 170.0 * k, "night")
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
        T = self._finish(L, 8, 0.35, "night", noise=True)
        # round 7: a faint blue glow of light behind the block (never bright: the closing stays dark)
        v = Image.new("L", (W, H), 0)
        (vx0, vy0), (vx1, vy1) = self._ec_xy(360, 40), self._ec_xy(1560, 1040)
        ImageDraw.Draw(v).ellipse((vx0, vy0, vx1, vy1), fill=int(round(150 * min(ec["veil"], 1.7))))
        va = np.asarray(v.filter(ImageFilter.GaussianBlur(120 * k)), np.float32) / 255.0
        vo = np.zeros(va.shape + (4,), np.float32)
        vo[..., :3] = (np.asarray((70, 100, 190), np.float32) / 255.0)[None, None, :] * (0.35 * va)[..., None]
        vo[..., 3] = 0.0
        (_va, vo), (x0, y0, x1, y1) = _crop([va, vo])
        V = dict(tex=self._tex(vo), rect=(x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H), box=(x0, y0, x1, y1))
        self.ec_back = self._night_sky()
        return T, V
