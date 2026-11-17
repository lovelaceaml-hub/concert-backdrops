import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from scipy import ndimage
F, M, B = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = 1920, 1080
def font(n, s): return ImageFont.truetype(f"{F}/{n}.ttf", s)
CG = lambda w, s, it=False: font(f"cormorant-garamond-latin-{w}-{'italic' if it else 'normal'}", s)
JO = lambda w, s: font(f"jost-latin-{w}-normal", s)
EXPR = [("Greeting", "greeting", "#EA5A5E"), ("Gratitude", "gratitude", "#F2B25E"), ("Apology", "apology", "#F6CE46"),
        ("Inclusiveness", "inclusiveness", "#5ABA5A"), ("Concession", "concession", "#62B2FA"), ("Respect", "respect", "#667AF6"),
        ("Encouragement", "encouragement", "#9E6AF6"), ("Consideration", "consideration", "#EE62A6"), ("Compliment", "compliment", "#364E96")]
hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def bg(name): return Image.open(f"{M}/src/{name}.png").convert("RGB").resize((W, H), Image.LANCZOS)
def tracked(d, xy, text, fnt, fill, track, align="c"):
    ws = [d.textlength(c, font=fnt) for c in text]; tot = sum(ws) + track * (len(text) - 1)
    x, y = xy; x -= tot / 2 if align == "c" else (tot if align == "r" else 0)
    for c, w in zip(text, ws): d.text((x, y), c, font=fnt, fill=fill); x += w + track
    return tot
def add_glow(base, layer, radius, strength, tint=None):
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(min(255, v * strength)))
    if tint is None:
        g = layer.filter(ImageFilter.GaussianBlur(radius)); g.putalpha(a)
    else:
        g = Image.new("RGBA", layer.size, tint + (0,)); g.putalpha(a)
    out = Image.alpha_composite(base.convert("RGBA"), g); return Image.alpha_composite(out, layer)
def heart_poly(cx, cy, s, rot=0.0):
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = 16 * math.sin(t) ** 3; y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        xr = x * math.cos(rot) - y * math.sin(rot); yr = x * math.sin(rot) + y * math.cos(rot)
        pts.append((cx + xr * s / 32, cy + yr * s / 32))
    return pts
def label(img, text, x=40, y=H - 80):
    d = ImageDraw.Draw(img); f = JO(500, 30)
    d.rounded_rectangle((x, y, x + d.textlength(text, font=f) + 36, y + 52), 10, fill=(0, 0, 0)); d.text((x + 18, y + 8), text, font=f, fill=(255, 255, 255))

# --- symbols redrawn in light (mockup method: trace the app icon's shapes, draw their edges as glowing lines)
def symbol_light(key, colour, size):
    ic = np.array(Image.open(f"{B}/icon_{key}.png").convert("RGB")).astype(int)
    h, w, _ = ic.shape
    fg = (np.abs(ic - np.array([243, 243, 243])).max(2) > 22)
    yy, xx = np.mgrid[0:h, 0:w]; fg &= ~(((xx - 165) ** 2 + (yy - 165) ** 2) < 34 ** 2)  # drop the check mark
    fg &= ((xx - 94) ** 2 + (yy - 94) ** 2) < 92 ** 2
    q = (ic // 40)
    lab = q[..., 0] * 100 + q[..., 1] * 10 + q[..., 2]
    edge = np.zeros_like(fg)
    for dy, dx in ((0, 1), (1, 0)):
        edge |= (np.roll(lab, (dy, dx), (0, 1)) != lab) & (fg | np.roll(fg, (dy, dx), (0, 1)))
    edge |= fg ^ ndimage.binary_erosion(fg, iterations=1)
    m = Image.fromarray((edge * 255).astype(np.uint8)).resize((size, size), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
    m = m.point(lambda v: 255 if v > 60 else int(v * 4))
    col = hexrgb(colour)
    core = Image.new("RGBA", (size, size), (255, 255, 255, 0)); core.putalpha(m.point(lambda v: int(v * 0.95)))
    tint = Image.new("RGBA", (size, size), col + (0,)); tint.putalpha(m.filter(ImageFilter.GaussianBlur(3)))
    out = Image.alpha_composite(tint, core)
    fill = Image.fromarray((fg * 255).astype(np.uint8)).resize((size, size), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6))
    wash = Image.new("RGBA", (size, size), col + (0,)); wash.putalpha(fill.point(lambda v: int(v * 0.22)))
    return Image.alpha_composite(wash, out)
def place(base, sym, cx, cy, colour, glow=18):
    L = Image.new("RGBA", base.size, (0, 0, 0, 0)); L.paste(sym, (int(cx - sym.width / 2), int(cy - sym.height / 2)), sym)
    return add_glow(base, L, glow, 1.6, hexrgb(colour))
def pill(d, cx, y, text, colour, f, track=6, pad=64):
    tw = tracked(d, (-9999, -9999), text, f, (0, 0, 0, 0), track)
    pw, ph = tw + pad, f.size + 26
    d.rounded_rectangle((cx - pw / 2, y, cx + pw / 2, y + ph), ph / 2, outline=hexrgb(colour) + (255,), width=3, fill=hexrgb(colour) + (70,))
    tracked(d, (cx, y + 9), text, f, (255, 255, 255, 255), track)
    return ph

# P0: the nine symbols in light, website colours, with hex codes
p0 = Image.new("RGB", (W, 620), (8, 12, 34)); g = np.linspace(0, 1, 620)[:, None]
p0 = Image.fromarray((np.dstack([8 + 14 * g, 12 + 18 * g, 34 + 40 * g]) * np.ones((1, W, 1))).astype(np.uint8))
for i, (name, key, colour) in enumerate(EXPR):
    cx = 110 + i * 212.5
    p0 = place(p0, symbol_light(key, colour, 170), cx, 220, colour).convert("RGB")
    L = Image.new("RGBA", p0.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    pill(d, cx, 340, name.upper(), colour, JO(500, 15), track=2, pad=30)
    tracked(d, (cx, 410), colour, JO(500, 22), hexrgb(colour) + (255,), 2)
    p0 = add_glow(p0, L, 6, 0.6).convert("RGB")
d = ImageDraw.Draw(p0); d.text((W / 2, 40), "The nine symbols, redrawn in light, in the website colours", font=CG(500, 46, True), fill=(255, 246, 232), anchor="ma")
d.text((W / 2, 530), "Mockup traced from the app icons; the real ones are redrawn by hand as clean light line art", font=JO(400, 24), fill=(190, 200, 230), anchor="ma")
p0.save(f"{M}/N0_symbols.png")

# P1: an expression moment: symbol forms first, then its colour pill and the words; small hearts drift from it
rng = np.random.default_rng(7)
name, key, colour = EXPR[6]
p1 = place(bg("06_r1_1"), symbol_light(key, colour, 300), W / 2, 250, colour, 24).convert("RGB")
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
for _ in range(26):
    x = W / 2 + rng.normal(0, 260); y = 250 + rng.normal(-40, 150); s = rng.uniform(12, 30)
    d.polygon(heart_poly(x, y, s, rng.uniform(-.4, .4)), fill=hexrgb(colour) + (int(rng.uniform(120, 230)),))
p1 = add_glow(p1, L, 8, 1.2, hexrgb(colour)).convert("RGB")
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
pill(d, W / 2, 430, "ENCOURAGEMENT", colour, JO(500, 26))
d.text((W / 2, 500), "“I’ll pray (or root) for you.", font=CG(600, 74, True), fill=(255, 248, 238, 255), anchor="ma")
d.text((W / 2, 584), "Everything will go well.”", font=CG(600, 74, True), fill=(255, 248, 238, 255), anchor="ma")
p1 = add_glow(p1, L, 12, 0.7, (200, 170, 255)).convert("RGB")
label(p1, "1  Each expression: its symbol draws itself in light, then its colour and words; hearts drift off")
p1.save(f"{M}/N1_expression.png")

# P2: the world, with hearts in the nine colours lighting up across it
sky = np.zeros((H, W, 3)); yy, xx = np.mgrid[0:H, 0:W]
sky[...] = np.dstack([6 + 10 * yy / H, 10 + 16 * yy / H, 30 + 40 * yy / H])
p2 = Image.fromarray(sky.astype(np.uint8)); d = ImageDraw.Draw(p2)
for _ in range(900):
    x, y = rng.uniform(0, W), rng.uniform(0, H); r = rng.choice([0.6, 1.0, 1.6], p=[.7, .25, .05]); v = int(rng.uniform(120, 255))
    d.ellipse((x - r, y - r, x + r, y + r), fill=(v, v, min(255, v + 20)))
cx, cy, R = 960, 560, 400
dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2); inside = dist < R
mu = np.sqrt(np.clip(1 - (dist / R) ** 2, 0, 1))
ocean = np.dstack([14 + 30 * mu, 40 + 70 * mu, 96 + 110 * mu])
arr = np.array(p2).astype(float); arr[inside] = ocean[inside]
rim = np.exp(-((dist - R) / 14) ** 2) * 0.9 + np.exp(-((dist - R) / 60) ** 2) * 0.35
arr += rim[..., None] * np.array([120, 180, 255]); p2 = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
wr = np.array(Image.open(f"{B}/world_ref.jpg").convert("RGB")).astype(int)
land = (wr[..., 1] > wr[..., 2] + 8) & (wr[..., 1] > wr[..., 0] + 20)
gy, gx = np.nonzero(land); gcx, gcy, gR = 663, 362, 292
mx = cx + (gx - gcx) * R / gR; my = cy + (gy - gcy) * R / gR
ok = (mx - cx) ** 2 + (my - cy) ** 2 < (R - 4) ** 2; mx, my = mx[ok], my[ok]
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
idx = rng.choice(len(mx), 9000, replace=False)
for x, y in zip(mx[idx], my[idx]):
    r = rng.choice([1.0, 1.5, 2.2], p=[.6, .3, .1]); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 226, 170, int(rng.uniform(90, 210))))
p2 = add_glow(p2, L, 5, 0.8, (255, 200, 120)).convert("RGB")
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
pts = []
for i in range(54):
    j = rng.integers(len(mx)); x, y = mx[j], my[j]; colour = EXPR[i % 9][2]; s = rng.uniform(16, 30)
    d.polygon(heart_poly(x, y, s), fill=hexrgb(colour) + (240,)); pts.append((x, y, colour))
for i in range(16):
    (x1, y1, c1), (x2, y2, _) = pts[rng.integers(len(pts))], pts[rng.integers(len(pts))]
    mxp, myp = (x1 + x2) / 2, (y1 + y2) / 2; lift = 1 + 0.25 * math.hypot(x2 - x1, y2 - y1) / R
    qx, qy = cx + (mxp - cx) * lift, cy + (myp - cy) * lift
    curve = [((1 - t) ** 2 * x1 + 2 * (1 - t) * t * qx + t * t * x2, (1 - t) ** 2 * y1 + 2 * (1 - t) * t * qy + t * t * y2) for t in np.linspace(0, 1, 40)]
    d.line(curve, fill=hexrgb(c1) + (150,), width=2)
p2 = add_glow(p2, L, 10, 1.3).convert("RGB")
label(p2, "2  Finale: the world, and hearts in the nine colours light up across it as the words spread")
p2.save(f"{M}/N2_world.png")

# logo with its white background removed (only the outside white, so the globe lines and branches stay)
lg = Image.open(f"{B}/logo_clean.jpg").convert("RGB"); a = np.array(lg).astype(int)
white = (a.min(2) > 200); lab, _ = ndimage.label(white)
outside = np.isin(lab, np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
alpha = np.where(ndimage.binary_dilation(outside, iterations=2), 0, 255).astype(np.uint8)
logo = lg.convert("RGBA"); logo.putalpha(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8)))
logo = logo.crop(logo.getbbox())
def logo_at(h): return logo.resize((int(logo.width * h / logo.height), h), Image.LANCZOS)

# P3: the world settles between two hearts and becomes the logo; end card
p3 = bg("10_r2_52").convert("RGBA"); lgo = logo_at(300)
glow = Image.new("RGBA", p3.size, (0, 0, 0, 0)); glow.paste(lgo, (W // 2 - lgo.width // 2, 70), lgo)
p3 = add_glow(p3, glow, 30, 0.8, (255, 255, 255))
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
navy = (31, 42, 107, 255); rose = (211, 97, 108, 255)
tracked(d, (W / 2, 400), "HEALING CONCERT", JO(500, 30), rose, 10)
d.text((W / 2, 440), "The Words of Mother’s Love", font=CG(600, 100), fill=rose, anchor="ma")
d.text((W / 2, 548), "That Bring Peace", font=CG(600, 78, True), fill=rose, anchor="ma")
tracked(d, (W / 2, 668), "SUNDAY, DECEMBER 6  ·  4:30 PM", JO(500, 40), navy, 6)
d.text((W / 2, 736), "World Mission Society Church of God", font=CG(500, 44), fill=navy, anchor="ma")
d.text((W / 2, 788), "6720 W Sahara Ave, Las Vegas", font=CG(500, 44), fill=navy, anchor="ma")
p3 = add_glow(p3, L, 10, 0.9, (255, 255, 255)).convert("RGB")
label(p3, "3  The world settles between two hearts and becomes the logo; the end card with the full title")
p3.save(f"{M}/N3_endcard.png")

# P4: opening title with the logo and the full title
p4 = bg("06_r1_1").convert("RGBA"); lgo = logo_at(130)
G = Image.new("RGBA", p4.size, (0, 0, 0, 0)); G.paste(lgo, (W // 2 - lgo.width // 2, 70), lgo); p4 = add_glow(p4, G, 18, 0.7, (255, 210, 170))
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); cream = (255, 246, 232, 255); gold = (246, 211, 139, 255)
tracked(d, (W / 2, 228), "HEALING CONCERT", JO(500, 30), gold, 9)
d.text((W / 2, 268), "The Words of Mother’s Love", font=CG(500, 96), fill=cream, anchor="ma")
d.text((W / 2, 370), "That Bring Peace", font=CG(500, 70, True), fill=cream, anchor="ma")
d.line((W / 2 - 60, 470, W / 2 + 60, 470), fill=gold, width=2)
tracked(d, (W / 2, 490), "SUNDAY, DECEMBER 6  ·  4:30 PM", JO(500, 40), cream, 6)
tracked(d, (W / 2, 548), "LAS VEGAS", JO(400, 26), gold, 8)
p4 = add_glow(p4, L, 14, 0.55, (255, 214, 150)).convert("RGB")
label(p4, "4  Opening title (0 to 4 s): the logo above the full title and date")
p4.save(f"{M}/N4_opening.png")

# P5: discreet signature with the logo mark
p5 = bg("01_r1_41").convert("RGBA"); lgo = logo_at(96)
x0, y0 = 60, H - 250
G = Image.new("RGBA", p5.size, (0, 0, 0, 0)); G.paste(lgo, (x0, y0), lgo); p5 = add_glow(p5, G, 12, 0.6, (255, 230, 200))
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); tx = x0 + lgo.width + 22
d.text((tx, y0 - 4), "The Words of Mother’s Love That Bring Peace", font=CG(500, 40, True), fill=cream)
tracked(d, (tx, y0 + 48), "DEC 6  ·  4:30 PM", JO(500, 30), cream, 5, align="l")
tracked(d, (tx, y0 + 88), "HEALING CONCERT  ·  LAS VEGAS", JO(400, 22), gold, 5, align="l")
p5 = add_glow(p5, L, 9, 0.5, (255, 214, 150)).convert("RGB")
label(p5, "5  Discreet signature in calm moments, now with the logo mark", 1040, H - 80)
p5.save(f"{M}/N5_signature.png")
