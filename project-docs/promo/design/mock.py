import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
F = sys.argv[1]; M = sys.argv[2]
def font(name, size): return ImageFont.truetype(f"{F}/{name}.ttf", size)
CG = lambda w, s, it=False: font(f"cormorant-garamond-latin-{w}-{'italic' if it else 'normal'}", s)
JO = lambda w, s: font(f"jost-latin-{w}-normal", s)
W, H = 1920, 1080
def bg(name):
    return Image.open(f"{M}/src/{name}.png").convert("RGB").resize((W, H), Image.LANCZOS)
def tracked(draw, xy, text, fnt, fill, track, anchor_center=True):
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x, y = xy
    if anchor_center: x -= total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill); x += w + track
    return total
def glow_comp(base, layer, radius=10, strength=1.0):
    a = layer.split()[3]
    g = Image.new("RGBA", layer.size, (255, 214, 150, 0)); g.putalpha(a.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * strength)))
    out = base.convert("RGBA"); out = Image.alpha_composite(out, g); out = Image.alpha_composite(out, layer)
    return out.convert("RGB")
def label(img, text, x, y):
    d = ImageDraw.Draw(img); f = JO(500, 30)
    d.rounded_rectangle((x, y, x + d.textlength(text, font=f) + 36, y + 52), 10, fill=(0, 0, 0))
    d.text((x + 18, y + 8), text, font=f, fill=(255, 255, 255))

# A: opening title moment, centred over the first image, high in the sky (lower third stays calm)
def lockup(cx, top, scale=1.0, col=(255, 246, 232), acc=(246, 211, 139)):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    tracked(d, (cx, top), "HEALING CONCERT", JO(500, int(30 * scale)), acc + (255,), 9 * scale)
    t = "The Words of Mother’s Love"; f = CG(500, int(104 * scale))
    d.text((cx, top + 46 * scale), t, font=f, fill=col + (255,), anchor="ma")
    y = top + 176 * scale
    d.line((cx - 60 * scale, y, cx + 60 * scale, y), fill=acc + (200,), width=max(1, int(2 * scale)))
    tracked(d, (cx, y + 22 * scale), "SUNDAY, DECEMBER 6  ·  4:30 PM", JO(500, int(40 * scale)), col + (255,), 6 * scale)
    tracked(d, (cx, y + 80 * scale), "LAS VEGAS", JO(400, int(26 * scale)), acc + (235,), 8 * scale)
    return L
a = glow_comp(bg("06_r1_1"), lockup(W / 2, 150), radius=14, strength=0.55)
label(a, "A  Opening: title and date over the first image, 0 to 4 s", 40, H - 80)
a.save(f"{M}/A_opening.png")

# B: discreet signature, bottom right, only in calm stretches between expressions
def signature(col=(255, 246, 232), acc=(246, 211, 139)):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    rx = W - 96; y0 = H - 196
    d.line((rx + 22, y0 + 6, rx + 22, y0 + 112), fill=acc + (220,), width=2)
    f1 = CG(500, 46, it=True); f2 = JO(500, 30); f3 = JO(400, 22)
    d.text((rx, y0), "The Words of Mother’s Love", font=f1, fill=col + (240,), anchor="ra")
    s = "DEC 6  ·  4:30 PM"
    wd = sum(d.textlength(c, font=f2) for c in s) + 5 * (len(s) - 1)
    tracked(d, (rx - wd, y0 + 58), s, f2, col + (255,), 5, anchor_center=False)
    s2 = "HEALING CONCERT  ·  LAS VEGAS"
    wd2 = sum(d.textlength(c, font=f3) for c in s2) + 5 * (len(s2) - 1)
    tracked(d, (rx - wd2, y0 + 98), s2, f3, acc + (230,), 5, anchor_center=False)
    return L
b = glow_comp(bg("06_r1_1"), signature(), radius=9, strength=0.5)
label(b, "B  Discreet signature, bottom right, only between expressions", 40, H - 80)
b.save(f"{M}/B_signature.png")

# C: the date in the world: written in points of light across the sky at the breath before the biggest hit
def dot_text(text, fnt, cx, cy, n, rng, size=(2, 5)):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m); d.text((cx, cy), text, font=fnt, fill=255, anchor="mm")
    ys, xs = np.nonzero(np.array(m) > 128)
    idx = rng.choice(len(xs), size=min(n, len(xs)), replace=False)
    return xs[idx], ys[idx]
rng = np.random.default_rng(3)
base = bg("06_r1_1").convert("RGBA")
P = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
xs, ys = dot_text("December 6", CG(600, 250, it=True), W / 2, 330, 5200, rng)
for x, y in zip(xs, ys):
    r = rng.choice([1.2, 1.6, 2.2, 3.0], p=[.45, .3, .18, .07]); c = (255, 240, 210, int(rng.uniform(170, 255)))
    d.ellipse((x - r, y - r, x + r, y + r), fill=c)
for _ in range(260):  # loose sparks drifting off the letters
    x, y = rng.uniform(560, 1360), rng.uniform(170, 520); r = rng.uniform(0.8, 2.0)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 230, 190, int(rng.uniform(60, 160))))
g = P.filter(ImageFilter.GaussianBlur(6)); out = Image.alpha_composite(base, g); out = Image.alpha_composite(out, P)
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(L)
tracked(d2, (W / 2, 500), "HEALING CONCERT  ·  4:30 PM", JO(500, 36), (255, 246, 232, 255), 8)
c = glow_comp(out.convert("RGB"), L, radius=10, strength=0.5)
label(c, "C  The date in light across the sky, at the breath before the biggest hit (about 40 s)", 40, H - 80)
c.save(f"{M}/C_date_in_sky.png")
