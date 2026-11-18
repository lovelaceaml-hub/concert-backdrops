"""Song 03 backdrop v2: everything drawn over the engine's finished frame (CPU, numpy and PIL).

- The opening lockup (Revision 3 style of tools/nine_colours_minor/cards.py and engine/titles.py): the campaign
  logo (engine/p3d/brand.py), HEALING CONCERT, The Words of Mother's Love / That Bring Peace (italic), a gold
  hairline and the song title large. Whole from frame 0 and held to OPEN_HOLD, then it fades cleanly.
- The signature, the same in all 11 songs, small in the top left from the end of the opening to the last frame:
  the logo mark, the song title, The Words of Mother's Love That Bring Peace, DEC 6 · 4:30 PM (brightest) and
  HEALING CONCERT · LAS VEGAS. Warm white and gold on the night skies, navy on the bright dawn (a slow
  crossfade of colour only: it never flashes or fades out).
- The two expressions in Claude Final v1's look (cream Cormorant serif phrase, the label in a thin capsule of the
  website colour), upper middle, written by a soft pen of light, readable for 9.4 s; then the letters let go as
  sparks that collapse into the expression's light in the arch. The scene behind the words is softened and
  calmed (nothing crosses them). Hearts in the expression's colour drift off the people after the reading; the
  expression's symbol is traced in its colour by sparks in the sky beside the moment (brand_symbols.py).
- The people of the two expressions (people.py, rendered on black) laid over the picture as light, standing on
  the far shore below the words.
- The three lyric fragments of the design, each with its own effect: "engraved deep in my heart" carved in gold
  by a pen of light under the mended moon; "Her warm hands" revealed as a frost haze melts away; "I love You
  Mother" gathered by rose petals (navy letters on the bright dawn).
- The lit lights of the arch (3, 7, 9) kept visible on the bright dawn sky.
- A soft highlight shoulder on every frame: no white-outs.
Everything is a pure function of t (no state between frames), so parallel parts match.
No em dash or en dash anywhere in this file.
"""
import importlib.util
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FONTS = os.path.join(REPO, "fonts")
WORK = os.path.join(REPO, "work", "s03_full2")
sys.path.insert(0, HERE)
from people_windows import WINDOWS as PEOPLE_WINDOWS  # noqa: E402


def _tag_p3d():
    """The approved tag's engine/p3d (brand, symbols, hearts) under its own package name, beside the pinned
    engine's p3d."""
    if "tagp3d" not in sys.modules:
        spec = importlib.util.spec_from_file_location("tagp3d", os.path.join(REPO, "engine/p3d/__init__.py"),
                                                      submodule_search_locations=[os.path.join(REPO, "engine/p3d")])
        m = importlib.util.module_from_spec(spec)
        sys.modules["tagp3d"] = m
        spec.loader.exec_module(m)
        import tagp3d.brand  # noqa: F401  (loads brand_symbols with it)
    return sys.modules["tagp3d.brand"], sys.modules["tagp3d.brand_symbols"], sys.modules["tagp3d.brand_hearts"]


# words.EXPRESSIONS (engine/p3d/words.py at the approved tag): exact wording and website colours
APOLOGY = dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"],
               color="#F6CE46", t_in=26.8, t_read0=28.6, t_read1=38.0, t_arrive=40.6, star=2, act=0,
               symbol=(0.895, 0.40))
ENCOURAGEMENT = dict(label="Encouragement",
                     lines=["“I’ll pray (or root) for you.", "Everything will go well.”"],
                     color="#9E6AF6", t_in=222.6, t_read0=224.4, t_read1=233.8, t_arrive=237.0, star=6, act=1,
                     symbol=(0.895, 0.40))
EXPRESSIONS = [APOLOGY, ENCOURAGEMENT]

NIGHT = dict(col=(255, 246, 232), acc=(246, 211, 139), glow=(255, 214, 150))
DAY = dict(col=(31, 42, 107), acc=(180, 132, 44), glow=(255, 255, 255), small=(243, 87, 99))
CREAM = (255, 244, 220)
SONG_TITLE = "I Reminisce About Your Love"
CONCERT = "The Words of Mother’s Love That Bring Peace"
SEP = "  ·  "
CENTRE_Y = 0.335            # centre of an expression block from the top (PHASEB 16: about a third down)
OPEN_HOLD, OPEN_GONE = 8.6, 10.2      # the opening lockup is whole to 8.6 s, gone by 10.2 s
SIG_IN, SIG_FULL = 10.0, 11.6         # the signature comes in as the lockup leaves, then stays to the last frame
DAWN = (240.5, 245.5)                 # the signature's colours change from night to day over the sunrise
ENGRAVE = dict(t0=116.0, t1=119.6, out=126.0, gone=127.5, y=0.455)
WARM = dict(t0=199.0, t1=203.5, out=209.5, gone=211.0, y=0.275)
LOVE = dict(t0=292.3, t1=296.0, out=312.0, gone=315.5, y=0.33)
PEOPLE_FEET = 0.705          # the far shore line, from the top
PEOPLE_SCALE = 0.52 / 0.6    # people.py renders at 0.6 of 1080p; on screen at 0.52
PEOPLE_ANCHOR = [(590.0, 572.0), (600.0, 584.0)]   # each act's foot centre in people.py's frames
ARCH_DAWN = (243.0, 247.0)   # from here the lit lights are drawn over the bright dawn sky


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + ".ttf"), max(int(round(size)), 4))


def CG(w, s, it=False):
    return _font(f"cormorant-garamond-latin-{w}-{'italic' if it else 'normal'}", s)


def JO(w, s):
    return _font(f"jost-latin-{w}-normal", s)


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sf(a, b, x):
    return float(_ss(a, b, x))


def _tracked(draw, x, y, text, font, fill, track, align="center", anchor="ls"):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    if align == "center":
        x = x - total / 2.0
    elif align == "right":
        x = x - total
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, anchor=anchor)
        x += w + track
    return total


class Layer:
    """A drawn picture, cropped: premultiplied colour, alpha, a halo of light and a protection mask."""

    def __init__(self, rgba, s, halo_r=12.0, halo_k=0.5, glow=(255, 214, 150), prot_r=36.0, prot_k=1.0, pad=60):
        a_full = rgba[..., 3]
        ys, xs = np.nonzero(a_full > 0.004)
        H, W = a_full.shape
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, W)
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, H)
        self.box = (int(x0), int(y0), int(x1), int(y1))
        sub = rgba[y0:y1, x0:x1]
        self.a = sub[..., 3].copy()
        self.rgb = sub[..., :3] * self.a[..., None]          # premultiplied
        A = Image.fromarray((self.a * 255).astype(np.uint8))
        h1 = np.asarray(A.filter(ImageFilter.GaussianBlur(halo_r * s)), np.float32) / 255.0
        h2 = np.asarray(A.filter(ImageFilter.GaussianBlur(halo_r * 3.0 * s)), np.float32) / 255.0
        self.halo = (0.65 * h1 + 0.35 * h2)[..., None] * (np.asarray(glow, np.float32) / 255.0) * halo_k
        g = np.asarray(A.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(prot_r * s)),
                       np.float32) / 255.0
        self.prot = np.clip(g * 4.0 * prot_k, 0.0, 1.0)
        W_ = x1 - x0
        xn = (np.arange(W_, dtype=np.float32) - (xs.min() - x0)) / max(xs.max() - xs.min(), 1)
        self.xn = np.broadcast_to(xn[None, :], self.a.shape)


def _rgba(img):
    return np.asarray(img, np.float32) / 255.0


class Overlay:
    def __init__(self, W, H, song):
        self.W, self.H, self.S = W, H, song
        self.s = H / 1080.0
        self.B, self.BS, self.BH = _tag_p3d()
        self.open = self._opening()
        self.sig_night = self._signature(NIGHT)
        self.sig_day = self._signature(DAY)
        self.blocks = {e["label"]: self._expression(e) for e in EXPRESSIONS}
        self.engrave = self._phrase("engraved deep in my heart", ENGRAVE["y"], CG(600, 88 * self.s, True),
                                    (255, 243, 214), glow=(255, 186, 96), halo_k=0.85)
        self.warm = self._phrase("Her warm hands", WARM["y"], CG(500, 96 * self.s, True), (255, 214, 160),
                                 glow=(255, 170, 90))
        self.love = self._phrase("I love You Mother", LOVE["y"], CG(600, 116 * self.s, True), DAY["col"],
                                 glow=(255, 255, 255), halo_k=0.75)
        self.particles = {e["label"]: self._letter_points(self.blocks[e["label"]], 900, 5 + i)
                          for i, e in enumerate(EXPRESSIONS)}
        self.love_pts = self._letter_points(self.love, 260, 21)
        self.engrave_pts = self._letter_points(self.engrave, 400, 22)
        self.symbols = {e["label"]: self._symbol(e) for e in EXPRESSIONS}
        self.hearts = {}
        self.sprites = {}
        self.frost = self._frost()
        self.people_cache = (None, None)

    # ------------------------------------------------------------------ pictures (built once)
    def _opening(self):
        W, H, s = self.W, self.H, self.s
        P = NIGHT
        col, acc = P["col"], P["acc"]
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx = W / 2.0
        logo_h = 124 * s
        total = 124 + 20 + 30 + 84 + 70 + 34 + 118
        top = 0.385 * H - total * s / 2.0
        lg = self.B.logo_image(int(round(logo_h)), pad=0.10, glow=0.35)
        _, (bx0, by0, bx1, by1) = self.B.logo_box(int(round(logo_h)), 0.10)
        im.alpha_composite(lg, (int(round(cx - (bx0 + bx1) / 2.0)), int(round(top - by0))))
        y = top + (124 + 20) * s
        _tracked(d, cx, y + 26 * s, "HEALING CONCERT", JO(500, 28 * s), acc + (255,), 9 * s)
        d.text((cx, y + 112 * s), "The Words of Mother’s Love", font=CG(500, 80 * s), fill=col + (255,),
               anchor="ms")
        d.text((cx, y + 180 * s), "That Bring Peace", font=CG(500, 64 * s, True), fill=col + (255,), anchor="ms")
        d.line((cx - 70 * s, y + 210 * s, cx + 70 * s, y + 210 * s), fill=acc + (210,), width=max(1, int(2 * s)))
        d.text((cx, y + 318 * s), SONG_TITLE, font=CG(600, 112 * s, True), fill=(255, 238, 206, 255), anchor="ms")
        return Layer(_rgba(im), s, halo_r=14, halo_k=0.55, glow=P["glow"], prot_r=40)

    def _signature(self, P):
        W, H, s = self.W, self.H, self.s
        col, acc = P["col"], P["acc"]
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        mx, my = 52 * s, 40 * s
        blk = 134 * s
        logo_h = int(round(94 * s))
        glow = 0.35 if P is NIGHT else 0.0
        lg = self.B.logo_image(logo_h, pad=0.10 if glow else 0.01, glow=glow)
        _, (bx0, by0, bx1, by1) = self.B.logo_box(logo_h, 0.10 if glow else 0.01)
        im.alpha_composite(lg, (int(round(mx - bx0)), int(round(my + (blk - (by1 - by0)) / 2.0 - by0))))
        tx = mx + (bx1 - bx0) + 18 * s
        d.text((tx, my + 30 * s), SONG_TITLE, font=CG(600, 33 * s, True), fill=col + (255,), anchor="ls")
        d.text((tx, my + 60 * s), CONCERT, font=CG(500, 25 * s, True), fill=col + (235,), anchor="ls")
        _tracked(d, tx, my + 99 * s, "DEC 6" + SEP + "4:30 PM", JO(500, 31 * s), col + (255,), 4 * s,
                 align="left")
        small = P.get("small")
        _tracked(d, tx, my + 127 * s, "HEALING CONCERT" + SEP + "LAS VEGAS", JO(500 if small else 400, 19 * s),
                 (small or acc) + (255 if small else 235,), 4 * s, align="left")
        return Layer(_rgba(im), s, halo_r=8, halo_k=0.45 if P is NIGHT else 0.75, glow=P["glow"], prot_r=26,
                     prot_k=0.8, pad=30)

    def _expression(self, e):
        W, H, s = self.W, self.H, self.s
        col = _hex(e["color"])
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        f_phrase = CG(600, 92 * s, True)
        f_label = JO(500, 30 * s)
        line_h, label_h = 98 * s, 66 * s
        block_h = label_h + line_h * len(e["lines"])
        top = CENTRE_Y * H - block_h / 2.0
        label = e["label"].upper()
        lab_y = top + 38 * s
        tw = _tracked(d, W / 2.0, lab_y, label, f_label, CREAM + (255,), 7 * s)
        ph, px = 48 * s, 26 * s
        cy = lab_y - 11 * s
        box = (W / 2 - tw / 2 - px, cy - ph / 2, W / 2 + tw / 2 + px, cy + ph / 2)
        cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dc = ImageDraw.Draw(cap)
        dc.rounded_rectangle(box, radius=ph / 2, fill=col + (60,), outline=col + (255,), width=max(int(2.4 * s), 1))
        cap.alpha_composite(im)
        im = cap
        d = ImageDraw.Draw(im)
        for k, line in enumerate(e["lines"]):
            d.text((W / 2.0, top + label_h + line_h * (k + 0.80)), line, font=f_phrase, fill=CREAM + (255,),
                   anchor="ms")
        L = Layer(_rgba(im), s, halo_r=11, halo_k=0.55, glow=tuple(int(0.5 * c + 0.5 * g) for c, g in
                                                                     zip(col, (255, 214, 150))), prot_r=38)
        L.col = np.asarray(col, np.float32) / 255.0
        L.cx, L.cy = W / 2.0, CENTRE_Y * H
        return L

    def _phrase(self, text, y, font, fill, glow, halo_k=0.6):
        W, H, s = self.W, self.H, self.s
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.text((W / 2.0, y * H), text, font=font, fill=tuple(fill) + (255,), anchor="mm")
        return Layer(_rgba(im), s, halo_r=12, halo_k=halo_k, glow=glow, prot_r=34)

    def _letter_points(self, L, n, seed):
        rng = np.random.default_rng(seed)
        w = (L.a > 0.5).astype(np.float64).ravel()
        idx = rng.choice(w.size, size=n, replace=False, p=w / w.sum())
        ys, xs = np.unravel_index(idx, L.a.shape)
        x0, y0 = L.box[:2]
        pts = np.stack([xs + x0, ys + y0], 1).astype(np.float64)
        return pts, L.xn[ys, xs].astype(np.float64), rng.random(n)

    def _symbol(self, e):
        """The expression's symbol as fine light lines with the drawing order in each pixel."""
        s = self.s
        h = int(round(0.15 * self.H))
        pad = int(0.25 * h)
        size = h + 2 * pad
        order = Image.new("L", (size, size), 0)
        line = Image.new("L", (size, size), 0)
        do, dl = ImageDraw.Draw(order), ImageDraw.Draw(line)
        strokes = self.BS.strokes(e["label"])
        total = sum(len(p) for p in strokes)
        k = 0
        for p in strokes:
            q = np.asarray(p, np.float64)
            xy = [(pad + h / 2.0 + x * h, pad + h / 2.0 - y * h) for x, y in q]
            for j in range(len(xy) - 1):
                v = int(1 + 254 * (k + j) / max(total - 1, 1))
                do.line([xy[j], xy[j + 1]], fill=v, width=max(int(5 * s), 2))
                dl.line([xy[j], xy[j + 1]], fill=255, width=max(int(2.6 * s), 1))
            k += len(q)
        o = np.asarray(order, np.float32) / 255.0
        a = np.asarray(line.filter(ImageFilter.GaussianBlur(0.7 * s)), np.float32) / 255.0
        g = np.asarray(line.filter(ImageFilter.GaussianBlur(7 * s)), np.float32) / 255.0
        o = np.asarray(Image.fromarray((o * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)),
                       np.float32) / 255.0
        cx, cy = e["symbol"]
        return dict(order=o, a=a, g=g, x0=int(cx * self.W - size / 2), y0=int(cy * self.H - size / 2),
                    col=np.asarray(_hex(e["color"]), np.float32) / 255.0)

    def _heart_sprite(self, r):
        r = max(int(round(r)), 3)
        if r not in self.hearts:
            n = 4 * r
            im = Image.new("L", (n, n), 0)
            pts = self.BH.heart_points(160)
            poly = [(n / 2 + x * 2 * r * 0.95, n / 2 - y * 2 * r * 0.95) for x, y in pts]
            ImageDraw.Draw(im).polygon(poly, fill=255)
            core = np.asarray(im.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255.0
            glow = np.asarray(im.filter(ImageFilter.GaussianBlur(r * 0.5)), np.float32) / 255.0
            self.hearts[r] = (core, glow)
        return self.hearts[r]

    def _frost(self):
        L = self.warm
        h, w = L.a.shape
        rng = np.random.default_rng(31)
        n = rng.random((h // 6 + 1, w // 6 + 1)).astype(np.float32)
        n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
                       .filter(ImageFilter.GaussianBlur(6)), np.float32) / 255.0
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        shape = np.clip(1.15 - r, 0, 1) ** 0.8
        return dict(noise=n, r=r, shape=shape)

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

    def _splat(self, img, xy, w, rgb, r_core=1.6, r_glow=6.0):
        """Many points of light at once: accumulated, softened, added."""
        if len(xy) == 0:
            return
        s = self.s
        pad = int(3 * r_glow * s) + 2
        x0 = int(max(np.floor(xy[:, 0].min()) - pad, 0))
        x1 = int(min(np.ceil(xy[:, 0].max()) + pad, self.W))
        y0 = int(max(np.floor(xy[:, 1].min()) - pad, 0))
        y1 = int(min(np.ceil(xy[:, 1].max()) + pad, self.H))
        if x1 <= x0 or y1 <= y0:
            return
        acc = np.zeros((y1 - y0, x1 - x0), np.float32)
        xi = np.clip(np.round(xy[:, 0]).astype(int) - x0, 0, x1 - x0 - 1)
        yi = np.clip(np.round(xy[:, 1]).astype(int) - y0, 0, y1 - y0 - 1)
        np.add.at(acc, (yi, xi), w.astype(np.float32))
        c = gaussian_filter(acc, r_core * s, truncate=3.0)
        g = gaussian_filter(acc, r_glow * s, truncate=3.0)
        light = np.clip(c * (2.0 * np.pi * (r_core * s) ** 2) * 0.55 + g * (2.0 * np.pi * (r_glow * s) ** 2) * 0.12,
                        0, 3)
        img[y0:y1, x0:x1] += light[..., None] * np.asarray(rgb, np.float32)[None, None, :]

    # ------------------------------------------------------------------ drawing
    def _protect(self, img, L, k, dim=0.82):
        """Soften and calm the scene behind a text block (k 0..1): nothing crosses the letters."""
        if k <= 0.002:
            return
        x0, y0, x1, y1 = L.box
        reg = img[y0:y1, x0:x1]
        small = Image.fromarray(np.clip(reg * 255, 0, 255).astype(np.uint8)).reduce(4)
        small = small.filter(ImageFilter.GaussianBlur(5))
        soft = np.asarray(small.resize((x1 - x0, y1 - y0), Image.BILINEAR), np.float32) / 255.0
        m = (L.prot * k)[..., None]
        img[y0:y1, x0:x1] = reg * (1 - m) + soft * dim * m

    def _put(self, img, L, alpha, reveal=None, halo=1.0, tint=None):
        if alpha <= 0.002:
            return
        x0, y0, x1, y1 = L.box
        reg = img[y0:y1, x0:x1]
        a = L.a * alpha
        rgb = L.rgb * alpha
        hk = L.halo * (alpha * halo)
        if reveal is not None:
            g = reveal
            a = a * g
            rgb = rgb * g[..., None]
            hk = hk * g[..., None]
        reg += hk
        reg[:] = reg * (1 - a[..., None]) + (rgb if tint is None else a[..., None] * tint)
        img[y0:y1, x0:x1] = reg

    def _pen_reveal(self, L, u, soft=0.06):
        front = -soft + (1 + 2 * soft) * u
        return np.clip((front - L.xn) / soft, 0.0, 1.0)

    def _opening_draw(self, img, t):
        if t > OPEN_GONE:
            return
        a = 1.0 - _sf(OPEN_HOLD, OPEN_GONE, t)
        self._protect(img, self.open, 0.55 * a, dim=0.9)
        self._put(img, self.open, a)

    def _signature_draw(self, img, t):
        if t < SIG_IN:
            return
        a = _sf(SIG_IN, SIG_FULL, t)
        day = _sf(DAWN[0], DAWN[1], t)
        prot = 0.45 * a
        self._protect(img, self.sig_night, prot, dim=0.9 if day < 0.5 else 1.0)
        if day < 1.0:
            self._put(img, self.sig_night, a * (1 - day))
        if day > 0.0:
            self._put(img, self.sig_day, a * day)

    def _expression_draw(self, img, e, t):
        L = self.blocks[e["label"]]
        if not (e["t_in"] - 1.2 <= t <= e["t_arrive"] + 0.6):
            return
        prot = _sf(e["t_in"] - 1.2, e["t_in"] + 0.3, t) * (1 - _sf(e["t_read1"] + 0.6, e["t_read1"] + 2.2, t))
        self._protect(img, L, prot)
        write = _sf(e["t_in"], e["t_read0"] - 0.2, t)
        alpha = _sf(e["t_in"], e["t_in"] + 0.4, t) * (1 - _sf(e["t_read1"], e["t_read1"] + 0.9, t))
        if alpha > 0.002:
            rev = self._pen_reveal(L, write) if write < 1.0 else None
            self._put(img, L, alpha, reveal=rev)
            if write < 1.0:
                # the pen of light at the front of the writing
                fx = L.box[0] + np.interp(write, [0, 1], [L.xn.shape[1] * 0.08, L.xn.shape[1] * 0.92])
                self._stamp(img, fx, L.cy + 20 * self.s, 10 * self.s, 0.4 * L.col + 0.6 * np.array(CREAM) / 255.0,
                            0.55 * alpha)
        # the letters let go as sparks that collapse into the expression's light in the arch
        t0, t1 = e["t_read1"], e["t_arrive"]
        if t0 <= t <= t1 + 0.5:
            pts, xn, rnd = self.particles[e["label"]]
            sx, sy = self.S.STAR_POS[e["star"]]
            tx, ty = sx * self.W, (1.0 - sy) * self.H
            start = t0 + 0.15 + 0.55 * xn + 0.25 * rnd
            dur = (t1 - 0.15) - start
            u = np.clip((t - start) / dur, 0.0, 1.0)
            e_ = u * u * (3 - 2 * u)
            # a gentle rising arc to the light, wider for the letters far from it
            mx = 0.5 * (pts[:, 0] + tx) + (pts[:, 0] - tx) * 0.25
            my = np.minimum(pts[:, 1], ty) - 0.05 * self.H - 0.04 * self.H * rnd
            x = (1 - e_) ** 2 * pts[:, 0] + 2 * (1 - e_) * e_ * mx + e_ * e_ * tx
            y = (1 - e_) ** 2 * pts[:, 1] + 2 * (1 - e_) * e_ * my + e_ * e_ * ty
            live = (t >= start - 0.05)
            w = live * (np.minimum(u / 0.08, 1.0)) * (1 - _ss(0.92, 1.0, u)) * 0.85
            w = w * (1 - _sf(t1, t1 + 0.4, t))
            colmix = 0.45 * L.col + 0.55 * np.array(CREAM) / 255.0
            self._splat(img, np.stack([x, y], 1), w, colmix, r_core=1.4, r_glow=5.0)
            # the light gathers them: a soft bloom at the star as they arrive
            k = _sf(t1 - 1.2, t1, t) * (1 - _sf(t1, t1 + 0.5, t))
            if k > 0:
                self._stamp(img, tx, ty, 9 * self.s, colmix, 0.5 * k)

    def _hearts_draw(self, img, e, t):
        """Hearts in the expression's colour drift off the people after the reading."""
        t0 = e["t_read1"] + 0.3
        if not (t0 <= t <= t0 + 9.0):
            return
        col = np.asarray(_hex(e["color"]), np.float32) / 255.0
        rng = np.random.default_rng(100 + e["star"])
        n = 16
        births = t0 + np.sort(rng.random(n)) * 3.5
        for j in range(n):
            age = t - births[j]
            if age < 0 or age > 5.0:
                continue
            side = -1 if j % 2 == 0 else 1
            x0 = 0.5 * self.W + side * (0.03 + 0.05 * rng.random()) * self.W
            y0 = (PEOPLE_FEET - 0.10 - 0.06 * rng.random()) * self.H
            sp = (0.035 + 0.02 * rng.random()) * self.H
            x = x0 + side * 0.03 * self.W * age + 0.012 * self.W * np.sin(1.3 * age + j)
            y = y0 - sp * age
            r = (6 + 4 * rng.random()) * self.s
            a = min(age / 0.6, 1.0) * (1 - _sf(3.4, 5.0, age)) * 0.75
            core, glow = self._heart_sprite(r)
            n2 = core.shape[0] // 2
            xi, yi = int(x) - n2, int(y) - n2
            if xi < 0 or yi < 0 or xi + core.shape[1] > self.W or yi + core.shape[0] > self.H:
                continue
            reg = img[yi:yi + core.shape[0], xi:xi + core.shape[1]]
            reg += glow[..., None] * col * 0.5 * a
            reg[:] = reg * (1 - core[..., None] * a * 0.8) + core[..., None] * a * 0.8 * (0.75 * col + 0.25)

    def _symbol_draw(self, img, e, t):
        """The symbol traced by sparks in its colour in the sky beside the moment, subtle, then gone."""
        a0 = e["t_read0"] + 1.0
        a1 = a0 + 2.2
        out0, out1 = e["t_read1"] + 1.0, e["t_read1"] + 3.0
        if not (a0 <= t <= out1):
            return
        sy = self.symbols[e["label"]]
        u = _sf(a0, a1, t)
        k = (1 - _sf(out0, out1, t)) * 0.5
        o = sy["order"]
        drawn = np.clip((u * 1.02 - o) / 0.02 + 1.0, 0, 1) * (o > 0)
        line = sy["a"] * np.clip(drawn * 1.0, 0, 1)
        glow = sy["g"] * _sf(a0, a1, t)
        h, w = line.shape
        y0, x0 = sy["y0"], sy["x0"]
        reg = img[y0:y0 + h, x0:x0 + w]
        c = sy["col"]
        reg += (line[..., None] * (0.55 * c + 0.45) + glow[..., None] * c * 0.6) * k
        if u < 1.0:
            # the spark at the tip of the tracing
            ys, xs = np.nonzero((o > 0) & (np.abs(o - u) < 0.01))
            if len(xs):
                self._stamp(img, x0 + xs.mean(), y0 + ys.mean(), 6 * self.s, 0.5 * c + 0.5, 0.6 * k * 2)

    def _people_draw(self, img, t, index):
        for k, (a, b) in enumerate(PEOPLE_WINDOWS):
            if not (a <= t <= b):
                continue
            path = os.path.join(WORK, "people", f"f{index:05d}.png")
            if not os.path.exists(path):
                raise SystemExit(f"people frame missing: {path} (run people.py first)")
            p = Image.open(path).convert("RGB")
            sc = PEOPLE_SCALE * self.s / 1.0
            w, h = int(round(p.width * sc)), int(round(p.height * sc))
            p = np.asarray(p.resize((w, h), Image.LANCZOS), np.float32) / 255.0
            ax, ay = PEOPLE_ANCHOR[k]
            x0 = int(round(0.5 * self.W - ax * sc))
            y0 = int(round(PEOPLE_FEET * self.H - ay * sc))
            cx0, cy0 = max(x0, 0), max(y0, 0)
            cx1, cy1 = min(x0 + w, self.W), min(y0 + h, self.H)
            part = p[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
            reg = img[cy0:cy1, cx0:cx1]
            # light added, with a little of the scene behind the brightest light taken away so they read
            lum = part.max(axis=2, keepdims=True)
            img[cy0:cy1, cx0:cx1] = reg * (1 - 0.35 * np.clip(lum * 1.5, 0, 1)) + part * 1.0

    def _engrave_draw(self, img, t):
        c = ENGRAVE
        if not (c["t0"] - 0.6 <= t <= c["gone"]):
            return
        L = self.engrave
        self._protect(img, L, 0.6 * _sf(c["t0"] - 0.6, c["t0"], t) * (1 - _sf(c["out"], c["gone"], t)))
        u = _sf(c["t0"], c["t1"], t)
        alpha = 1 - _sf(c["out"], c["gone"], t)
        rev = self._pen_reveal(L, u, 0.03) if u < 1.0 else None
        # freshly carved gold glows brighter, then settles
        glow = 1.0 + 0.6 * (1 - _sf(c["t1"], c["t1"] + 2.0, t))
        self._put(img, L, alpha, reveal=rev, halo=glow)
        if 0.0 < u < 1.0:
            x0, y0, x1, y1 = L.box
            fx = x0 + 60 * self.s + (x1 - x0 - 120 * self.s) * u
            fy = c["y"] * self.H + 6 * self.s * np.sin(40 * t)
            self._stamp(img, fx, fy, 7 * self.s, np.array([1.0, 0.93, 0.75]), 0.9)
            # sparks thrown by the engraving tool, falling a little
            rng = np.random.default_rng(int(t * 60))
            n = 14
            age = rng.random(n) * 0.7
            vx = (rng.random(n) - 0.5) * 120 * self.s
            vy = -(60 + 80 * rng.random(n)) * self.s
            xs = fx + vx * age
            ys = fy + vy * age + 260 * self.s * age * age
            self._splat(img, np.stack([xs, ys], 1), (1 - age / 0.7) * 0.8, np.array([1.0, 0.82, 0.5]), 1.0, 3.5)

    def _warm_draw(self, img, t):
        c = WARM
        if not (c["t0"] - 0.2 <= t <= c["gone"]):
            return
        L = self.warm
        F = self.frost
        x0, y0, x1, y1 = L.box
        haze = _sf(c["t0"], c["t0"] + 1.2, t)
        melt = _sf(c["t0"] + 1.0, c["t1"], t)
        # the frost melts from the middle outward, with a ragged edge
        front = melt * 1.35
        clear = np.clip((front - F["r"] - 0.25 * (F["noise"] - 0.5)) / 0.12, 0, 1)
        fa = haze * F["shape"] * (0.30 + 0.25 * F["noise"]) * (1 - clear) * (1 - _sf(c["out"], c["gone"], t))
        reg = img[y0:y1, x0:x1]
        frost_col = np.array([0.80, 0.86, 0.98], np.float32)
        reg[:] = reg * (1 - fa[..., None] * 0.55) + fa[..., None] * 0.55 * frost_col
        img[y0:y1, x0:x1] = reg
        alpha = (1 - _sf(c["out"], c["gone"], t))
        beat = 1.0 + 0.18 * np.sin(2 * np.pi * 0.45 * t) * _sf(c["t1"], c["t1"] + 1.0, t)
        self._protect(img, L, 0.5 * melt * alpha)
        self._put(img, L, alpha, reveal=clear, halo=1.2 * beat)

    def _love_draw(self, img, t):
        c = LOVE
        if not (c["t0"] - 0.2 <= t <= c["gone"] + 1.5):
            return
        L = self.love
        pts, xn, rnd = self.love_pts
        W, H, s = self.W, self.H, self.s
        petal = np.array([1.0, 0.62, 0.70], np.float32)
        gold = np.array([1.0, 0.86, 0.62], np.float32)
        # the letters appear where the petals have arrived (left to right), and leave the same way
        u_in = _sf(c["t0"] + 0.8, c["t1"], t)
        u_out = _sf(c["out"], c["gone"] - 0.6, t)
        rev = np.clip((u_in * 1.15 - L.xn) / 0.15, 0, 1) * (1 - np.clip((u_out * 1.15 - L.xn) / 0.15, 0, 1))
        self._protect(img, L, 0.5 * _sf(c["t0"], c["t0"] + 1.0, t) * (1 - _sf(c["out"] + 1.0, c["gone"], t)),
                      dim=1.0)
        self._put(img, L, 1.0, reveal=rev, halo=1.0)
        # petals fly in from the far shore and the sides, each to its place in a letter
        rng = np.random.default_rng(77)
        n = len(pts)
        sx = (0.10 + 0.80 * rng.random(n)) * W
        sy = (PEOPLE_FEET - 0.02 - 0.10 * rng.random(n)) * H
        arrive = c["t0"] + 0.8 + (c["t1"] - c["t0"] - 0.8) * np.clip(xn * 0.9 + 0.1 * rnd, 0, 1)
        start = arrive - 2.2
        u = np.clip((t - start) / (arrive - start), 0, 1)
        e_ = 1 - (1 - u) ** 2
        x = sx + (pts[:, 0] - sx) * e_ + 30 * s * np.sin(3 * u + rnd * 6) * (1 - u)
        y = sy + (pts[:, 1] - sy) * e_ - 60 * s * np.sin(np.pi * u)
        w_in = (u > 0) * (1 - _ss(0.85, 1.0, u)) * 0.9
        # and when the words let go, petals lift off the letters and drift down to the water, fading
        leave = c["out"] + (c["gone"] - 0.6 - c["out"]) * np.clip(xn * 0.9 + 0.1 * rnd, 0, 1)
        v = np.clip((t - leave) / 3.0, 0, 1)
        x2 = pts[:, 0] + 90 * s * v + 20 * s * np.sin(4 * v + rnd * 6)
        y2 = pts[:, 1] + 0.22 * H * v * v
        w_out = (v > 0) * (1 - _ss(0.6, 1.0, v)) * 0.9
        xy = np.concatenate([np.stack([x, y], 1), np.stack([x2, y2], 1)])
        w = np.concatenate([w_in, w_out])
        keep = w > 0.01
        if keep.any():
            self._splat(img, xy[keep], w[keep] * 0.7, petal * 0.8 + gold * 0.2, r_core=2.2, r_glow=5.5)

    def _arch_dawn(self, img, t):
        """The lit lights (3, 7, 9) stay visible on the bright dawn sky: a warm gold point with a soft halo."""
        k = _sf(ARCH_DAWN[0], ARCH_DAWN[1], t)
        if k <= 0:
            return
        for i, extra in ((2, 1.15), (6, 1.0), (8, 1.0)):
            x, y = self.S.STAR_POS[i]
            X, Y = x * self.W, (1 - y) * self.H
            br = (0.85 + 0.15 * np.sin(0.9 * t + i)) * extra * k
            r = int(16 * self.s)
            yy, xx = np.mgrid[-3 * r:3 * r + 1, -3 * r:3 * r + 1].astype(np.float32)
            d2 = (xx * xx + yy * yy) / (r * r)
            core = np.exp(-d2 * 18.0)
            ring = np.exp(-d2 * 2.5) * 0.35 + np.exp(-((np.abs(xx) * 9 + np.abs(yy) * 0.6) / r) ** 2) * 0.3 \
                + np.exp(-((np.abs(yy) * 9 + np.abs(xx) * 0.6) / r) ** 2) * 0.3
            y0, x0 = int(Y) - 3 * r, int(X) - 3 * r
            reg = img[y0:y0 + 6 * r + 1, x0:x0 + 6 * r + 1]
            deep = np.array([0.80, 0.52, 0.18], np.float32)
            a = np.clip(ring * br * 0.55, 0, 1)[..., None]
            reg[:] = reg * (1 - a) + a * deep
            reg += core[..., None] * np.array([1.0, 0.95, 0.85], np.float32) * br * 0.9

    def apply(self, data, t, index=None):
        W, H = self.W, self.H
        if index is None:
            index = int(round(t * 60))
        img = np.frombuffer(data, np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
        self._arch_dawn(img, t)
        self._people_draw(img, t, index)
        for e in EXPRESSIONS:
            self._symbol_draw(img, e, t)
            self._hearts_draw(img, e, t)
            self._expression_draw(img, e, t)
        self._engrave_draw(img, t)
        self._warm_draw(img, t)
        self._love_draw(img, t)
        self._opening_draw(img, t)
        self._signature_draw(img, t)
        # the calm lower third (performers stand in front of it): bright reflections on the water are pressed
        # down smoothly below the far shore, so no glitter, rings or streaks draw the eye there
        y0 = int(0.70 * H)
        ramp = _ss(0.70, 0.80, (np.arange(y0, H) + 0.5) / H).astype(np.float32)[:, None, None]
        low = img[y0:]
        knee = 0.30
        soft = np.where(low > knee, knee + 0.45 * (low - knee) / (1 + (low - knee) / 0.35), low)
        img[y0:] = low * (1 - ramp) + soft * ramp
        # soft shoulder: keep highlights under clipping (no white-outs)
        hi = img > 0.86
        if hi.any():
            img = np.where(hi, 0.86 + 0.13 * np.tanh((img - 0.86) / 0.13), img)
        return (np.clip(img, 0, 1) * 255.0 + 0.5).astype(np.uint8).tobytes()
