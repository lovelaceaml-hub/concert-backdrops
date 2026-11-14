"""Paints song 06's scene plates with code (no image tool in the cloud session; the phase 1 plates painted on the Mac
never reached the repo). Run: python3 assets/plates/s06/paint_plates.py  (writes the JPEGs next to this file).

Harvest evening look (DESIGN-SYSTEM.md section 6): amber, wheat gold, deep orange, golden dust, a long low sun.
No people, no text; the bottom third stays dark and calm for the performers.
  path.jpg            narrow shore path between still water and tall glowing wheat, ember dusk (Concession)
  shore_dark.jpg      the near shore, low and close, still water, rose ember dusk, dark wheat behind, the family's
                      lantern floating dark on the water (Inclusiveness)
  shore_glow.jpg      the same shore after the lantern has been lifted out, relit: its warm light around the two
  wilderness_dry.jpg  a cracked dry wilderness in dusky gold under the low sun
  wilderness_gold.jpg the same land with living gold water running in every crack, green gold shoots
  blossom.jpg         the healed land: blossom trees along golden streams, wheat bending in a warm haze
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import cKDTree

W, H = 1920, 1080
OUT = os.path.dirname(os.path.abspath(__file__))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
V = 1.0 - yy / (H - 1)          # height from the bottom, 0..1
X = xx / (W - 1)
ASP = W / H


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0


def noise2(scale, seed, octaves=5):
    """Smooth value noise 0..1 (H x W), scale = cells across the width of the frame."""
    rng = np.random.default_rng(seed)
    acc, amp, tot = np.zeros((H, W)), 1.0, 0.0
    for o in range(octaves):
        cw = max(int(scale * 2 ** o), 2)
        ch = max(int(cw / ASP), 2)
        g = rng.random((ch + 1, cw + 1)).astype(np.float32)
        im = Image.fromarray(g, mode="F").resize((W, H), Image.BICUBIC)
        acc += amp * np.asarray(im)
        tot += amp
        amp *= 0.5
    return np.clip(acc / tot, 0, 1)


def noise1(n, scale, seed, octaves=5):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, n)
    acc, amp, tot = np.zeros(n), 1.0, 0.0
    for o in range(octaves):
        k = int(scale * 2 ** o) + 2
        r = rng.random(k)
        u = x * (k - 1.001)
        i = np.floor(u).astype(int)
        f = u - i
        f = f * f * (3 - 2 * f)
        acc += amp * (r[i] * (1 - f) + r[i + 1] * f)
        tot += amp
        amp *= 0.5
    return acc / tot


def ramp(v, stops):
    """Vertical colour ramp: stops = [(v, '#hex'), ...] with v increasing."""
    vs = np.array([s[0] for s in stops])
    cs = np.array([hexc(s[1]) for s in stops])
    out = np.zeros(v.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(v, vs, cs[:, c])
    return out


def sky(stops, sun, sun_col, sun_r=0.035, glow=0.55, rays=0.0, seed=1):
    img = ramp(V, stops)
    dx, dy = (X - sun[0]) * ASP, V - sun[1]
    r = np.sqrt(dx * dx + dy * dy)
    sc = hexc(sun_col)
    img += sc[None, None, :] * (glow * np.exp(-r / 0.10) + 0.45 * glow * np.exp(-r / 0.35))[..., None]
    if rays > 0:
        ang = np.arctan2(dy, dx)
        n = noise1(4096, 24, seed, 3)
        a = np.interp((ang + np.pi) / (2 * np.pi), np.linspace(0, 1, 4096), n)
        ray = np.clip((a - 0.45) * 2.2, 0, 1) ** 1.5 * np.exp(-r / 0.9) * (r > sun_r)
        img += sc[None, None, :] * (rays * ray)[..., None]
    disc = np.clip(0.5 - (r - sun_r) / 0.016, 0, 1) * (sun_r > 0)     # a soft edged disc
    disc = disc * disc * (3 - 2 * disc)
    img = img * (1 - disc[..., None]) + hexc("#fff0d0")[None, None, :] * disc[..., None]
    # thin warm clouds in bands
    cl = noise2(5, seed + 7, 5)
    band = np.exp(-((V - sun[1] - 0.10) / 0.12) ** 2)
    img = img * (1 - 0.18 * (cl * band)[..., None]) + sc * 0.22 * (np.clip(cl - 0.5, 0, 1) * band * np.exp(-r / 0.5))[..., None]
    return img


def hills(img, base, amp, scale, seed, col, rim=None, rim_k=0.0, haze=None, haze_k=0.0):
    """A hill silhouette filled below base + amp * noise; returns the mask (1 = hill)."""
    prof = base + amp * noise1(W, scale, seed, 5)
    mask = np.clip((prof[None, :] - V) * H / 1.5, 0, 1)
    c = hexc(col)[None, None, :]
    fill = c * np.ones_like(img)
    if haze is not None:
        depth = np.clip((prof[None, :] - V) / 0.08, 0, 1)
        fill = fill * depth[..., None] + hexc(haze) * (1 - depth[..., None]) * haze_k + fill * (1 - depth[..., None]) * (1 - haze_k)
    img = img * (1 - mask[..., None]) + fill * mask[..., None]
    if rim is not None:
        edge = np.exp(-((prof[None, :] - V) * H / 3.0) ** 2) * mask
        img += hexc(rim) * (rim_k * edge)[..., None]
    return img, mask, prof


def mirror(img, line, dark=0.55, tint="#3a1c18", streak_seed=3, strength=1.0):
    """Still water below `line`: the image above mirrored, darkened, with soft horizontal streaks."""
    out = img.copy()
    row_line = int((1 - line) * (H - 1))
    for r in range(row_line, H):
        src = 2 * row_line - r
        if src < 0:
            src = 0
        out[r] = img[src]
    st = noise2(3, streak_seed, 4)
    st = np.asarray(Image.fromarray((st * 255).astype(np.uint8)).resize((W // 40, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)) / 255.0
    below = (V < line).astype(np.float64)
    d = np.clip((line - V) / max(line, 1e-3), 0, 1)
    wat = out * (dark * (1 - 0.55 * d) * (0.85 + 0.3 * st))[..., None] + hexc(tint) * (0.25 * d)[..., None]
    return img * (1 - below[..., None]) + (wat * strength + img * (1 - strength)) * below[..., None]


def glow_layer(layer, radius, k):
    """Adds a blurred copy of an RGB float layer (0..1+) for light bloom."""
    im = Image.fromarray(np.clip(layer * 255 / 2.0, 0, 255).astype(np.uint8))
    b = np.asarray(im.filter(ImageFilter.GaussianBlur(radius))).astype(np.float64) / 255 * 2.0
    return layer + b * k


def wheat(img, region, n, seed, base_col, head_col, h_range, lean=0.0, sway=0.05, dark=0.0, glow=0.9,
          y_top=None, mask_fn=None):
    """Draws n stalks of wheat of light; region = (x0, x1, v0, v1) for the foot of each stalk (v from the bottom).
    Stalks nearer the bottom are drawn larger and darker (they sit in the calm lower third)."""
    rng = np.random.default_rng(seed)
    S = 2
    lay = Image.new("RGB", (W * S, H * S), (0, 0, 0))
    dr = ImageDraw.Draw(lay)
    x0, x1, v0, v1 = region
    feet = []
    for i in range(n):
        fx = rng.uniform(x0, x1)
        fv = v0 + (v1 - v0) * rng.random() ** 0.7
        if mask_fn is not None and not mask_fn(fx, fv):
            continue
        feet.append((fv, fx))
    feet.sort(reverse=True)    # far (high) first
    bc, hc = hexc(base_col), hexc(head_col)
    for fv, fx in feet:
        near = np.clip((v1 - fv) / max(v1 - v0, 1e-3), 0, 1)
        hgt = rng.uniform(*h_range) * (0.45 + 0.9 * near)
        bend = lean + rng.normal(0, sway)
        bright = (1.0 - dark * near ** 1.2) * rng.uniform(0.55, 1.0)
        pts = []
        for k in range(9):
            u = k / 8
            px = fx + bend * hgt * u * u / ASP
            pv = fv + hgt * u
            pts.append((px * W * S, (1 - pv) * H * S))
        wdt = max(1, int(S * (1.0 + 2.2 * near)))
        sc = tuple(int(255 * min(1, c * bright * 0.55)) for c in bc)
        dr.line(pts, fill=sc, width=wdt)
        # the head: a few grain ellipses along the top
        hx, hy = pts[-1]
        tx, ty = pts[-1][0] - pts[-3][0], pts[-1][1] - pts[-3][1]
        L = max(np.hypot(tx, ty), 1e-3)
        tx, ty = tx / L, ty / L
        gs = (1.0 + 2.4 * near) * S
        hcol = tuple(int(255 * min(1, c * bright * 0.8)) for c in hc)
        # the head: a slim tapered ear along the tip of the stalk, with a few grains on each side
        dr.line([(hx, hy), (hx - tx * gs * 5.0, hy - ty * gs * 5.0)], fill=hcol, width=max(1, int(gs * 1.2)))
        for g in range(1, 5):
            cx, cy = hx - tx * g * gs * 1.1, hy - ty * g * gs * 1.1
            for side in (-1, 1):
                ox, oy = -ty * side * gs * 0.7, tx * side * gs * 0.7
                dr.ellipse([cx + ox - gs * 0.45, cy + oy - gs * 0.45, cx + ox + gs * 0.45, cy + oy + gs * 0.45],
                           fill=hcol)
    lay = lay.resize((W, H), Image.LANCZOS)
    arr = np.asarray(lay).astype(np.float64) / 255
    a = np.clip(arr.max(axis=2) * 3.0, 0, 1)
    lit = glow_layer(arr, 5, glow * 0.6)
    lit = glow_layer(lit, 30, glow * 0.3)
    return img * (1 - a[..., None] * 0.85) + lit


def calm_bottom(img, top=0.30, k=0.55):
    """Darkens the lower third softly so performers stand on a calm floor."""
    f = 1.0 - k * np.clip((top - V) / top, 0, 1) ** 0.8
    return img * f[..., None]


def vignette(img, k=0.35):
    r = np.sqrt(((X - 0.5) * 1.2) ** 2 + (V - 0.55) ** 2)
    return img * (1 - k * np.clip(r - 0.35, 0, 1) ** 1.5 * 2)[..., None]


def dust(img, n, seed, col="#ffd27a", region=(0, 1, 0.3, 1.0)):
    rng = np.random.default_rng(seed)
    lay = np.zeros((H, W, 3))
    xs = rng.uniform(region[0], region[1], n)
    vs = rng.uniform(region[2], region[3], n)
    for x, v in zip(xs, vs):
        r, c = int((1 - v) * (H - 1)), int(x * (W - 1))
        lay[r, c] = hexc(col) * rng.uniform(0.6, 2.0)
    return img + glow_layer(lay, 1.2, 1.0) * 0.8


def save(img, name):
    # soft shoulder on the highlights: nothing clips, the brightest sun peaks at about 235 of 255
    k, top = 0.62, 0.92
    a = np.where(img > k, k + (img - k) / (1 + (img - k) / (top - k)), img)
    a = np.clip(a, 0, 1)
    Image.fromarray((a * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, name), quality=88, optimize=True)
    print("wrote", name, os.path.getsize(os.path.join(OUT, name)) // 1024, "KB")


# ------------------------------------------------------------------ plates
def plate_path():
    sun = (0.80, 0.47)
    img = sky([(0.0, "#2a1010"), (0.40, "#7a2e1c"), (0.50, "#d0642a"), (0.62, "#a24a2c"), (0.85, "#4a2236"),
               (1.0, "#22142e")], sun, "#ffb060", sun_r=0.030, glow=0.65, rays=0.35, seed=11)
    img, _, _ = hills(img, 0.495, 0.05, 3, 21, "#5a2a26", rim="#ffb070", rim_k=0.25, haze="#c86a3a", haze_k=0.6)
    img, _, _ = hills(img, 0.470, 0.035, 5, 22, "#3a1a1c", rim="#ff9a50", rim_k=0.35)
    # still water on the left, the shore path rising to the right
    line = 0.455
    img = mirror(img, line, dark=0.62, tint="#3a1612", streak_seed=4)
    # the path: a pale diagonal band from bottom centre-left to the far right
    pc = 0.36 + (X - 0.30) * 0.0
    path_center = lambda v: 0.40 + (0.455 - v) * (-0.55) * -1.0  # noqa: E731
    cx = 0.40 + (line - V) * 0.0
    # shore edge (water to the left of it, land to the right): from (0.18, 0) to (0.62, line)
    edge = 0.20 + (V / line) * 0.42
    land = np.clip((X - edge) * W / 6.0, 0, 1) * (V < line)
    ground = ramp(V, [(0.0, "#1a0c0a"), (0.25, "#3a1c14"), (line, "#6a3420")])
    gn = noise2(14, 31, 4)
    ground = ground * (0.8 + 0.4 * gn[..., None])
    img = img * (1 - land[..., None]) + ground * land[..., None]
    # the path itself: a pale ember band along the shore
    pd = np.abs(X - (edge + 0.035 + 0.06 * (1 - V / line)))
    pw = 0.012 + 0.07 * (1 - V / line)
    pathm = np.clip(1 - pd / pw, 0, 1) ** 0.6 * (V < line - 0.002)
    pcol = ramp(V, [(0.0, "#3a2016"), (0.2, "#7a4228"), (line, "#e0985a")])
    img = img * (1 - pathm[..., None] * 0.9) + pcol * (pathm[..., None] * 0.9)
    # sun glitter path on the water
    gl = np.exp(-((X - sun[0] + 0.25) / 0.05) ** 2) * (V < line) * (V > 0.25) * noise2(40, 5, 2) ** 4
    img += hexc("#ffb070") * (gl * 1.2)[..., None]
    # tall glowing wheat to the right of the path
    def right_of_path(fx, fv):
        e = 0.20 + (fv / line) * 0.42
        return fx > e + 0.035 + 0.06 * (1 - fv / line) + 0.05 * (1 - fv / line) + 0.02

    img = wheat(img, (0.30, 1.02, 0.02, line), 2600, 41, "#c06a2a", "#ffc860", (0.05, 0.12), lean=-0.25,
                sway=0.08, dark=0.65, glow=0.8, mask_fn=right_of_path)
    img = dust(img, 500, 51, "#ffc070", (0.3, 1.0, 0.38, 0.85))
    img = calm_bottom(img, 0.30, 0.6)
    img = vignette(img, 0.35)
    save(img, "path.jpg")


def plate_shore(lit):
    sun = (0.30, 0.50)
    img = sky([(0.0, "#140a10"), (0.45, "#5a1e22"), (0.52, "#b04a36"), (0.60, "#8a3a3c"), (0.80, "#3a1a34"),
               (1.0, "#160c22")], sun, "#ff8a7a", sun_r=0.0, glow=0.55, rays=0.0, seed=12)
    # far bank with dark wheat, close and low
    img, _, prof = hills(img, 0.515, 0.02, 6, 23, "#2a1218", rim="#ff9a80", rim_k=0.30)
    img = wheat(img, (-0.02, 1.02, 0.505, 0.53), 1700, 42, "#3a1418", "#c8604a", (0.025, 0.05), lean=0.15,
                sway=0.06, dark=0.0, glow=0.35)
    line = 0.505
    img = mirror(img, line, dark=0.70, tint="#2a0e14", streak_seed=6)
    # a soft rose afterglow lying on the still water
    gl = np.exp(-((X - sun[0]) / 0.10) ** 2) * np.exp(-((line - V) / 0.10)) * (V < line)
    img += hexc("#ff9a8a") * (gl * 0.35)[..., None]
    # the near shore: a dark low bank where the two kneel, across the bottom
    lip = 0.20 + 0.035 * noise1(W, 5, 24, 5)
    m = np.clip((lip[None, :] - V) * H / 2.0, 0, 1)
    gcol = ramp(V, [(0.0, "#0a0506"), (0.20, "#2a1210")])
    gcol = gcol * (0.8 + 0.4 * noise2(30, 25, 4)[..., None])
    img = img * (1 - m[..., None]) + gcol * m[..., None]
    rimm = np.exp(-((lip[None, :] - V) * H / 2.5) ** 2) * m
    img += hexc("#ff9070") * (0.18 * rimm)[..., None]
    # the family's lantern floating on the water, dark at first, relit later
    lx, lv, lw, lh = 0.66, 0.305, 0.016, 0.040
    body = np.clip(1 - np.maximum(np.abs(X - lx) * ASP / lw, np.abs(V - lv) / (lh / 2)) ** 6, 0, 1)
    cap = np.clip(1 - np.maximum(np.abs(X - lx) * ASP / (lw * 0.75), np.abs(V - (lv + lh / 2 + 0.004)) / 0.004) ** 6, 0, 1)
    handle = np.exp(-((np.hypot((X - lx) * ASP, (V - (lv + lh / 2 + 0.006)) * 1.0) - 0.009) / 0.0012) ** 2) * (V > lv + lh / 2 + 0.006)
    shape = np.clip(body + cap + handle, 0, 1)
    if lit == "glow":
        shape = shape * 0
        # the lantern has been lifted out of the water: its warm light now surrounds the two on the shore
        halo = np.exp(-np.hypot((X - 0.32) * ASP, (V - 0.52) * 1.3) / 0.13)
        img += hexc("#ffb070") * (0.30 * halo)[..., None]
    elif lit:
        core = np.exp(-(((X - lx) * ASP / 0.012) ** 2 + ((V - lv) / 0.018) ** 2))
        img = img * (1 - shape[..., None]) + hexc("#ffd890") * (shape * (0.75 + 0.5 * core))[..., None]
        halo = np.exp(-np.hypot((X - lx) * ASP, V - lv) / 0.045)
        img += hexc("#ffb060") * (0.55 * halo)[..., None]
        refl = np.exp(-((X - lx) * ASP / 0.010) ** 2) * np.clip((lv - lh / 2 - V) / 0.006, 0, 1) * np.exp(-(lv - lh / 2 - V) / 0.07)
        refl *= 0.6 + 0.4 * noise2(60, 9, 2)
        img += hexc("#ffc070") * (0.65 * refl * (V > 0.21))[..., None]
    else:
        img = img * (1 - shape[..., None]) + hexc("#2a1610") * shape[..., None]
        edge = shape * (1 - np.clip(body * 1.5 - 0.5, 0, 1))
        img += hexc("#ff9a80") * (0.12 * edge)[..., None]
    img = dust(img, 220, 52, "#ffb0a0", (0.0, 1.0, 0.40, 0.9))
    img = calm_bottom(img, 0.24, 0.45)
    img = vignette(img, 0.40)
    save(img, {"glow": "shore_glow.jpg", True: "shore_lit.jpg", False: "shore_dark.jpg"}[lit])


def _cracks(line, seed):
    """Distance to the nearest crack (F2 - F1 of a Voronoi field) on a ground plane seen in perspective."""
    rng = np.random.default_rng(seed)
    m = V < line
    d = np.clip((line - V) / line, 1e-3, 1)          # 0 at the horizon, 1 at the bottom
    gz = 1.0 / (d + 0.06)                              # depth
    gx = (X - 0.5) * gz * 2.2
    pts = np.stack([rng.uniform(-30, 30, 30000), rng.uniform(0, 18, 30000)], 1)
    tree = cKDTree(pts)
    q = np.stack([gx[m], gz[m] * 0.9], 1)
    dist, idx = tree.query(q, k=2, workers=-1)
    f = np.full((H, W), 9.0)
    f[m] = dist[:, 1] - dist[:, 0]
    # cell id for a little per-cell shading
    cid = np.zeros((H, W))
    cid[m] = (idx[:, 0] * 0.618) % 1.0
    width = 0.022 + 0.0 * gz                            # a constant width on the ground: thinner far away on screen
    return f, width, cid, d, m


def plate_wilderness(living):
    sun = (0.50, 0.49)
    img = sky([(0.0, "#2a1408"), (0.40, "#6a3418"), (0.47, "#e08a3a"), (0.56, "#b05a2c"), (0.80, "#4a2434"),
               (1.0, "#24142a")], sun, "#ffc070", sun_r=0.028, glow=0.75, rays=0.45, seed=13)
    img, _, _ = hills(img, 0.47, 0.035, 3, 25, "#6a3420", rim="#ffb060", rim_k=0.35, haze="#d0803a", haze_k=0.6)
    line = 0.465
    f, width, cid, d, m = _cracks(line, 61)
    ground = ramp(V, [(0.0, "#140a06"), (0.20, "#3a2010"), (0.38, "#7a4a24"), (line, "#b8763a")])
    gn = noise2(30, 33, 4)
    ground = ground * (0.75 + 0.35 * gn[..., None]) * (0.85 + 0.3 * cid[..., None])
    # light on the plates of dry earth facing the sun
    ground += hexc("#ffb060") * (0.25 * np.exp(-np.abs(X - 0.5) * 3.0) * (1 - d) ** 2)[..., None]
    crack = np.clip(1 - f / width, 0, 1) * m
    if living:
        gold = hexc("#ffcf6a")
        core = crack ** 0.7
        lay = gold * (core * (0.95 - 0.35 * d))[..., None]
        lay = glow_layer(lay, 4, 0.6)
        lay = glow_layer(lay, 18, 0.35)
        lay *= (1 - 0.88 * np.clip((0.36 - V) / 0.26, 0, 1) ** 0.6)[..., None]
        img = img * (1 - m[..., None]) + (ground * (1 - core[..., None] * 0.6) + lay) * m[..., None]
        # green gold shoots: small bright points along the veins
        rng = np.random.default_rng(71)
        ys, xs = np.nonzero((crack > 0.6) & (V > 0.30))
        pick = rng.choice(len(ys), size=min(900, len(ys)), replace=False)
        sh = np.zeros((H, W, 3))
        sh[ys[pick], xs[pick]] = hexc("#d8f07a") * 1.6
        img += glow_layer(sh, 2.0, 1.2) * 0.7
    else:
        dark = hexc("#1a0c06")
        img = img * (1 - m[..., None]) + (ground * (1 - crack[..., None] * 0.75) + dark * crack[..., None] * 0.2) * m[..., None]
    img = dust(img, 380, 53, "#ffc070", (0.0, 1.0, 0.40, 0.95))
    img = calm_bottom(img, 0.30, 0.55)
    img = vignette(img, 0.35)
    save(img, "wilderness_gold.jpg" if living else "wilderness_dry.jpg")


def plate_blossom():
    sun = (0.22, 0.60)
    img = sky([(0.0, "#2a1a0c"), (0.40, "#8a5a28"), (0.52, "#f2b25a"), (0.65, "#d08a4a"), (0.85, "#7a4a4a"),
               (1.0, "#3a2440")], sun, "#ffe0a0", sun_r=0.032, glow=0.70, rays=0.55, seed=14)
    img, _, _ = hills(img, 0.53, 0.06, 2, 26, "#9a6a3a", rim="#ffe0a0", rim_k=0.20, haze="#f0c080", haze_k=0.7)
    img, _, p2 = hills(img, 0.46, 0.07, 3, 27, "#6a4a22", rim="#ffd890", rim_k=0.30, haze="#e0a860", haze_k=0.5)
    img, _, p3 = hills(img, 0.36, 0.06, 4, 28, "#4a3418", rim="#ffd080", rim_k=0.25)
    tex = noise2(18, 91, 5)
    land = np.clip((0.56 - V) / 0.04, 0, 1)
    img = img * (1 - land[..., None] * (0.35 - 0.5 * tex[..., None]))
    # a winding golden stream from the far hills down to the lower left
    t = np.linspace(0, 1, 400)
    sx = 0.62 + 0.10 * np.sin(t * 7.0) - 0.40 * t
    sv = 0.44 - 0.40 * t
    lay = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(lay)
    for k in range(len(t) - 1):
        wdt = int(3 + 46 * t[k] ** 1.4)
        dr.line([(sx[k] * W, (1 - sv[k]) * H), (sx[k + 1] * W, (1 - sv[k + 1]) * H)], fill=(255, 200, 110), width=wdt)
    st = np.asarray(lay).astype(np.float64) / 255
    stm = st.max(axis=2)
    img = img * (1 - stm[..., None] * 0.9) + glow_layer(st * 0.95, 8, 0.8)
    # blossom trees along the stream: round soft canopies with white and gold flowers
    rng = np.random.default_rng(81)
    S = 1
    tl = Image.new("RGB", (W, H))
    td = ImageDraw.Draw(tl)
    trees = []
    for k in range(0, 400, 9):
        for side in (-1, 1):
            if rng.random() < 0.55:
                trees.append((sx[k] + side * (0.03 + 0.06 * t[k]) + rng.normal(0, 0.01), sv[k], t[k]))
    trees.sort(key=lambda q: -q[1])
    for tx, tv, tk in trees:
        if tv < 0.16:
            continue
        r = (0.010 + 0.040 * tk) * W
        cx, cy = tx * W, (1 - tv) * H - r * 1.2
        td.line([(cx, cy + r * 0.5), (cx, (1 - tv) * H)], fill=(60, 34, 20), width=max(1, int(r * 0.12)))
        for b in range(int(30 + 90 * tk)):
            a = rng.uniform(0, 2 * np.pi)
            rr = r * np.sqrt(rng.random())
            bx, by = cx + rr * np.cos(a), cy + rr * np.sin(a) * 0.8
            c = (255, 248, 230) if rng.random() < 0.6 else (255, 214, 140)
            s = rng.uniform(0.6, 1.0) * (1.5 + 3.5 * tk)
            lum = 0.55 + 0.45 * rng.random()
            td.ellipse([bx - s, by - s, bx + s, by + s], fill=tuple(int(v * lum) for v in c))
    ta = np.asarray(tl).astype(np.float64) / 255
    tm = np.clip(ta.max(axis=2) * 2.5, 0, 1)
    img = img * (1 - tm[..., None] * 0.8) + glow_layer(ta * 0.9, 6, 0.6)
    # wheat bending in the wind on the right
    img = wheat(img, (0.55, 1.02, 0.03, 0.34), 1500, 43, "#b07a30", "#ffe090", (0.04, 0.09), lean=0.45,
                sway=0.05, dark=0.6, glow=0.6)
    haze = np.exp(-((V - 0.47) / 0.10) ** 2)
    img = img * (1 - 0.25 * haze[..., None]) + hexc("#ffd8a0") * (0.25 * haze)[..., None]
    img = dust(img, 500, 54, "#ffe0a0", (0.0, 1.0, 0.35, 0.95))
    img = calm_bottom(img, 0.33, 0.72)
    img = vignette(img, 0.30)
    save(img, "blossom.jpg")


if __name__ == "__main__":
    plate_path()
    plate_shore(False)
    plate_shore("glow")
    plate_wilderness(False)
    plate_wilderness(True)
    plate_blossom()
