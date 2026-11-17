import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage
M, B, O = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = 1920, 1080
OUT = lambda w, s: ImageFont.truetype(f"{O}/outfit-latin-{w}-normal.ttf", s)
NAVY, CORAL, BLUE1, BLUE2, YEL = (39, 39, 81), (243, 87, 99), (3, 69, 165), (3, 45, 129), (255, 228, 120)
def tr_width(f, text, track): return f.getlength(text) + track * (len(text) - 1)
def tr(d, cx, y, text, f, fill, track):
    x = cx - tr_width(f, text, track) / 2
    for i, c in enumerate(text): d.text((x + f.getlength(text[:i]) + track * i, y), c, font=f, fill=fill)
def gradient_text(size, cx, y, text, f, track, c1, c2):
    m = Image.new("L", size, 0); tr(ImageDraw.Draw(m), cx, y, text, f, 255, track)
    bb = m.getbbox(); g = np.zeros((size[1], size[0], 3))
    t = np.clip((np.arange(size[1]) - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)[:, None, None]
    g[:] = np.array(c1) * (1 - t) + np.array(c2) * t
    L = Image.fromarray(g.astype(np.uint8)).convert("RGBA"); L.putalpha(m); return L
lg = Image.open(f"{B}/logo_clean.jpg").convert("RGB"); a = np.array(lg).astype(int)
white = (a.min(2) > 200); lab, _ = ndimage.label(white)
outside = np.isin(lab, np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
logo = lg.convert("RGBA"); logo.putalpha(Image.fromarray(np.where(ndimage.binary_dilation(outside, iterations=2), 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
logo = logo.crop(logo.getbbox())

base = Image.open(f"{M}/src/10_r2_52.png").convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
# a soft veil of light behind the text block (light, never dark)
veil = Image.new("L", (W, H), 0); ImageDraw.Draw(veil).ellipse((360, 40, 1560, 1040), fill=150)
veil = veil.filter(ImageFilter.GaussianBlur(120)); wl = Image.new("RGBA", (W, H), (255, 252, 246, 0)); wl.putalpha(veil)
base = Image.alpha_composite(base, wl)
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
lgo = logo.resize((int(logo.width * 170 / logo.height), 170), Image.LANCZOS); L.paste(lgo, (W // 2 - lgo.width // 2, 48), lgo)
tr(d, W / 2, 236, "HEALING CONCERT", OUT(600, 30), CORAL + (255,), 9)
tr(d, W / 2, 278, "The Words of", OUT(500, 78), NAVY + (255,), -2)
tr(d, W / 2, 352, "Mother’s Love", OUT(800, 176), CORAL + (255,), -4)
L = Image.alpha_composite(L, gradient_text((W, H), W / 2, 540, "That Bring Peace", OUT(800, 124), -3, BLUE1, BLUE2))
d = ImageDraw.Draw(L)
# ribbon with notched ends, like the official theme banner
rx0, rx1, ry0, ry1, notch = 520, 1400, 712, 792, 34
d.polygon([(rx0 - notch, ry0), (rx1 + notch, ry0), (rx1, (ry0 + ry1) / 2), (rx1 + notch, ry1), (rx0 - notch, ry1), (rx0, (ry0 + ry1) / 2)], fill=CORAL + (255,))
f = OUT(600, 44); p1 = "Sunday, December 6"; p2 = "  ·  4:30 PM"
wtot = f.getlength(p1) + f.getlength(p2); x = W / 2 - wtot / 2
d.text((x, 728), p1, font=f, fill=YEL + (255,)); d.text((x + f.getlength(p1), 728), p2, font=f, fill=(255, 255, 255, 255))
tr(d, W / 2, 826, "World Mission Society Church of God", OUT(500, 42), NAVY + (255,), 0)
tr(d, W / 2, 878, "6720 W Sahara Ave, Las Vegas", OUT(500, 42), NAVY + (255,), 0)
glow = Image.new("RGBA", (W, H), (255, 255, 255, 0)); glow.putalpha(L.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.7)))
out = Image.alpha_composite(Image.alpha_composite(base, glow), L).convert("RGB")
out.save(f"{M}/N6_endcard_official.png")
ref = Image.open(f"{B}/official_festival.jpg").convert("RGB").resize((960, 540))
side = Image.new("RGB", (1920, 540)); side.paste(ref, (0, 0)); side.paste(out.resize((960, 540), Image.LANCZOS), (960, 0)); side.save(f"{M}/N6_side_by_side.jpg", quality=92)
