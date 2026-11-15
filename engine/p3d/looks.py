"""Looks of the particle bodies: how the cloud of points on a body is drawn.

A look turns the body's points (with their parts, heights and seeds) into draw layers. Each layer is a share
of the points with a sprite kind, sizes, colours and settings; engine/p3d/body.py fills in the positions at
each time and hands the layers to the renderer as batches.

Looks (may be combined in a list, for example look=["rim", "glitter"]):
  "glitter"   thousands of fine glittering points, a few bright glints (ref 15, 10, 09)
  "plexus"    points joined to their neighbours by fine lines, brighter toward the light (ref 03, 12)
  "rim"       light only on the edge of the silhouette as seen from the camera, the inside dark (ref 01, 16).
              Add the body with body.add(scene, name) so that its dark shape also hides what is behind it.
  "dots"      evenly spaced flat dots in two or three colours (ref 14)
  "window"    the silhouette as a window onto a sky (ref 08): a few stars inside and a light edge; the fill
              comes from the renderer's mask pass, see Body.mask()
  "crystal"   a person of clear glass with light inside: a bright edge split into soft prismatic colours where
              the body turns away, a faint clear body, a soft inner glow, fine twinkling sparkle (no mask).
              The glass is cut in irregular facets that shimmer together, with fine light where they meet.
              Settings: prism (0..1, how strongly the edge takes the spectrum, default 0.75), clear (the clear
              body, default 1), inner (the light inside, default 1), reach (how far the warm heart light spreads,
              in body heights, default 0.18), glints (share of four-point glints, default 0.003), facet (metres
              across a facet for a 1.6 m body, default 0.075), cuts (the light of the facets' edges, default 1),
              front (0..1, how much the far side of the glass dims so the near side reads, default 0.8).
              color is the warm light inside, color2 the clear glass
  "gold"      a person of warm gold glitter with depth: deep amber, gold and champagne grains, a soft light
              within round the heart, many four-point glints. Settings: deep (the darkest gold), depth (the share
              of deep grains, default 0.3), inner, reach, glints (default 0.0022), front (how much the far side
              dims, default 0.55: the body reads solid)
A look may also be a dict: dict(name="glitter", bright=1.4, size=1.2, color="#...", color2="#...").
Settings of any look: seams (0..1, default 1: the hems, cuffs and necklines of garments glow, so cloth reads as
cloth); glitter: glints (the share of points drawn as four-point glints, default 0.0007); rim: power (how thin
the edge line is, default 5).
"""
import numpy as np

from . import bodymath as bm
from .api import lin

LOOKS = ("glitter", "plexus", "rim", "dots", "window", "crystal", "gold")

# the soft spectrum of light split by glass (rose, peach, gold, mint, sky, lilac): prismatic glints
PRISM = np.array([lin(h) for h in ("#ff9cc0", "#ffbe86", "#ffe680", "#9cf2c8", "#8cc8ff", "#c0a4ff")])


def prism(h):
    """Colours of the soft spectrum for hues h in 0..1 (wrapping)."""
    h = np.mod(np.asarray(h, np.float64), 1.0) * len(PRISM)
    i = np.floor(h).astype(np.int64) % len(PRISM)
    f = (h - np.floor(h))[:, None]
    return PRISM[i] * (1 - f) + PRISM[(i + 1) % len(PRISM)] * f

# part codes of the cloud points
SKIN, HAND, CLOTH, VEIL, HAIR, FOOT = 0, 1, 2, 3, 4, 5


def _col(c):
    return lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


def _spec(look):
    if isinstance(look, str):
        return dict(name=look)
    d = dict(look)
    if "name" not in d:
        raise ValueError("a look given as a dict needs a name")
    return d


def _noise(rest, scale, salt):
    """A smooth 0..1 field over the body (for patches of colour)."""
    f = bm.flow(rest, 0.0, scale=scale, speed=0.0, seed=salt)
    return np.clip(0.5 + 0.9 * f[:, 0] * 0.6 + 0.5 * f[:, 1] * 0.4, 0.0, 1.0)


def _arc(u, v, cx, cy, half, bend):
    """Distance from (u, v) to a gentle arc: x = cx + half * a, y = cy + bend * (1 - a * a), a in -1..1."""
    a = np.clip((u - cx) / half, -1.0, 1.0)
    du = (u - cx) - half * a
    dv = v - (cy + bend * (1.0 - a * a))
    return np.sqrt(du * du + dv * dv)


def face_marks(rest, part, strength=1.0):
    """Gentle features on the smooth face of a body (the mesh's face is a soft mannequin on purpose): a
    brightness factor per point that models the face as light falls on a sculpture. Peaceful closed eyes (a
    soft crease under a lit lid, never a light in the eye), a lit brow, the bridge of the nose and soft shadows
    under it, the lips with a gentle smile, warm cheeks. 1 everywhere off the face. Head units come from the
    body itself (chin to crown), so it suits women, men and children."""
    rest = np.asarray(rest, np.float64)
    out = np.ones(len(rest))
    if strength <= 0.0:
        return out
    H = float(rest[:, 1].max())
    skin = part == SKIN
    mid = skin & (rest[:, 1] > 0.78 * H) & (np.abs(rest[:, 0]) < 0.02 * H / 1.6)
    if mid.sum() < 50:
        return out
    ys = np.arange(0.78 * H, H, 0.004 * H / 1.6)
    zf = np.array([rest[mid & (np.abs(rest[:, 1] - y) < 0.003 * H / 1.6), 2].max(initial=-1.0) for y in ys])
    ok = zf > -0.5
    if ok.sum() < 10:
        return out
    zmax = zf[ok].max()
    chin = float(ys[ok][np.argmax(zf[ok] > 0.82 * zmax)])
    hh = max(H - chin, 0.05)
    head = skin & (rest[:, 1] > chin - 0.05 * hh)
    zc = float(np.median(rest[head, 2]))
    u = rest[:, 0] / hh
    v = (rest[:, 1] - chin) / hh
    front = np.clip((rest[:, 2] - zc - 0.25 * hh) / (0.2 * hh), 0.0, 1.0) * head
    m = np.zeros(len(rest))

    def g(d, w):
        return np.exp(-(d / w) ** 2)

    for sd in (-1.0, 1.0):
        ex = sd * 0.155
        m -= 0.30 * np.exp(-(((u - ex) / 0.10) ** 2 + ((v - 0.47) / 0.06) ** 2))      # the soft hollow of the eye
        m -= 0.60 * g(_arc(u, v, ex, 0.466, 0.072, -0.018), 0.022)                      # the closed lids
        m += 0.30 * g(_arc(u, v, ex, 0.505, 0.064, -0.010), 0.024)                      # the lit lid above
        m += 0.32 * g(_arc(u, v, sd * 0.165, 0.578, 0.088, 0.024), 0.024)               # the brow
        m -= 0.40 * np.exp(-(((u - sd * 0.045) / 0.028) ** 2 + ((v - 0.300) / 0.020) ** 2))   # the nostrils
        m += 0.18 * np.exp(-(((u - sd * 0.20) / 0.08) ** 2 + ((v - 0.33) / 0.07) ** 2))      # the cheeks
    m += 0.30 * g(u, 0.022) * np.clip((v - 0.33) / 0.04, 0, 1) * np.clip((0.52 - v) / 0.04, 0, 1)   # the nose
    m -= 0.30 * g(v - 0.282, 0.018) * np.clip(1.0 - np.abs(u) / 0.06, 0, 1)             # under the nose
    m -= 0.60 * g(_arc(u, v, 0.0, 0.180, 0.088, -0.012), 0.016)                         # the parting of the lips
    m += 0.25 * g(v - 0.210, 0.020) * np.clip(1.0 - np.abs(u) / 0.08, 0, 1)             # the upper lip
    m += 0.30 * g(v - 0.148, 0.024) * np.clip(1.0 - np.abs(u) / 0.07, 0, 1)             # the lower lip
    m -= 0.22 * g(v - 0.100, 0.022) * np.clip(1.0 - np.abs(u) / 0.07, 0, 1)             # under the lip
    return np.clip(1.0 + 1.7 * strength * front * m, 0.15, 2.2)


def facets(rest, cell, salt=11):
    """Cut-glass facets over a body at rest: (facet id 0..1, nearness to a facet's edge 0..1) per point. The
    facets are the cells of a jittered grid (Voronoi cells about `cell` metres across), so they are irregular."""
    rest = np.asarray(rest, np.float64)
    base = np.floor(rest / cell).astype(np.int64)
    best = np.full(len(rest), np.inf)
    second = np.full(len(rest), np.inf)
    fid = np.zeros(len(rest))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = base + np.array([dx, dy, dz])
                key = c[:, 0] * 73856093 + c[:, 1] * 19349663 + c[:, 2] * 83492791
                j = np.stack([bm.hashf(key, salt), bm.hashf(key, salt + 1), bm.hashf(key, salt + 2)], axis=1)
                d = np.linalg.norm(rest - (c + 0.15 + 0.7 * j) * cell, axis=1)
                closer = d < best
                second = np.where(closer, best, np.minimum(second, d))
                fid = np.where(closer, bm.hashf(key, salt + 3), fid)
                best = np.where(closer, d, best)
    edge = np.clip(1.0 - (second - best) / (0.16 * cell), 0.0, 1.0)
    return fid, edge


def build(look, cloud, color, color2, bright=1.0, scale=1.0):
    """The draw layers of one look for a cloud. cloud: dict(n, part, seed, h, rest, strand (bool), pairs_fn).
    Returns a list of layers: dict(kind, idx, size, color, alpha, emit, seed, twinkle, rim, backlight,
    lines (optional (m, 2) pairs of cloud indices))."""
    sp = _spec(look)
    name = sp["name"]
    if name not in LOOKS:
        raise ValueError("look must be one of %s, got %r" % (LOOKS, name))
    n = cloud["n"]
    part = cloud["part"]
    seed = cloud["seed"].astype(np.float64)
    c1 = _col(sp.get("color", color))
    c2 = _col(sp.get("color2", color2))
    b = bright * sp.get("bright", 1.0)
    sz = scale * sp.get("size", 1.0)
    r2 = bm.hashf((seed * 1e6).astype(np.int64), 5)
    r3 = bm.hashf((seed * 1e6).astype(np.int64), 6)
    soft_part = np.where(part == VEIL, 0.62, np.where(part == HAIR, 0.8, 1.0))      # a veil is sheer
    # seams of light where a garment ends (hem, cuffs, neckline): what makes cloth read as cloth
    edge = cloud.get("edge", np.zeros(n))
    seam = 1.0 + sp.get("seams", 1.0) * np.where(part == VEIL, 2.6, 1.6) * edge
    layers = []
    allp = np.arange(n)

    if name == "glitter":
        mix = np.clip(_noise(cloud["rest"], 3.0, 1.0) * 0.7 + 0.3 * r2, 0, 1)
        col = c1[None] * (1 - mix)[:, None] + c2[None] * mix[:, None]
        # skin (face, hands, feet) a little paler than the garments; a veil paler still, so it reads as its
        # own fabric over the robe
        skin = np.isin(part, (SKIN, HAND, FOOT))
        col[skin] = col[skin] * 0.75 + c2[None] * 0.25
        vl = part == VEIL
        col[vl] = (col[vl] * 0.15 + (c2[None] * 0.7 + 0.3) * 0.85) * 1.2
        # most grains are fine and some are dark, a very few are glints: the grain of glitter
        tone = np.where(r3 < 0.28, 0.22, 0.75 + 0.5 * r2)
        size = (0.0026 + 0.0075 * seed ** 4) * sz
        glint = seed > 1.0 - sp.get("glints", 0.0007)
        base = ~glint
        layers.append(dict(kind="soft", idx=allp[base], size=size[base], color=col[base] * tone[base, None],
                           alpha=0.42 * b * soft_part[base] * seam[base], emit=1.0, twinkle=0.8, rim=(0.55, 1.5),
                           backlight=0.12))
        layers.append(dict(kind="spark", idx=allp[glint], size=size[glint] * 0.9, color=col[glint] * 0.6 + 0.4 * c2,
                           alpha=0.8 * b, emit=1.1 + 1.6 * r2[glint], twinkle=1.0, rim=(0.0, 2.0), backlight=0.15))
    elif name == "rim":
        size = (0.0020 + 0.0040 * seed ** 4) * sz
        mix = r2 * 0.5
        col = c1[None] * (1 - mix)[:, None] + c2[None] * mix[:, None]
        layers.append(dict(kind="soft", idx=allp, size=size, color=col, alpha=0.9 * b * soft_part, emit=1.0,
                           twinkle=0.5, rim=(1.0, sp.get("power", 5.0)), backlight=0.1))
        # a faint glitter inside the dark body (ref 16)
        inner = allp[seed > 0.95]
        layers.append(dict(kind="soft", idx=inner, size=size[inner], color=col[inner], alpha=0.07 * b * seam[inner],
                           emit=1.0, twinkle=0.9, rim=(0.0, 2.0), backlight=0.0))
    elif name == "dots":
        keep = allp[seed < sp.get("share", 0.13)]
        f = _noise(cloud["rest"][keep], 2.2, 2.0)
        r = r2[keep]
        t3 = np.where(r < 0.5 + 0.9 * (f - 0.5), 0.0, 1.0)
        col = c1[None] * (1 - t3)[:, None] + c2[None] * t3[:, None]
        white = r3[keep] > 0.9
        col[white] = 0.5 * col[white] + 0.5
        layers.append(dict(kind="disc", idx=keep, size=np.full(len(keep), 0.0085 * sz) * (0.8 + 0.5 * r3[keep]),
                           color=col, alpha=0.62 * b, emit=1.0, twinkle=0.15, rim=(0.0, 2.0), backlight=0.0))
    elif name == "plexus":
        share = sp.get("share", 0.05)
        nodes = allp[seed < share]
        size = (0.004 + 0.008 * r2[nodes] ** 3) * sz
        col = c1[None] * (0.6 + 0.4 * r3[nodes, None]) + c2[None] * 0.4 * (1 - r3[nodes, None])
        layers.append(dict(kind="soft", idx=nodes, size=size, color=col, alpha=0.75 * b,
                           emit=1.2 + 2.2 * (r2[nodes] > 0.93), twinkle=0.6, rim=(0.25, 1.5), backlight=0.4, lit=0.7,
                           lines=cloud["pairs_fn"](nodes, sp.get("links", 3), sp.get("reach", 0.11)),
                           line_color=c2 * 0.55 + c1 * 0.45, line_alpha=0.30 * b, line_size=0.0016 * sz))
        haze = allp[(seed > share) & (seed < share + sp.get("haze", 0.25))]
        layers.append(dict(kind="soft", idx=haze, size=np.full(len(haze), 0.003 * sz), color=np.broadcast_to(c1, (len(haze), 3)),
                           alpha=0.07 * b, emit=1.0, twinkle=0.5, rim=(0.5, 1.8), backlight=0.3))
    elif name == "crystal":
        rest = cloud["rest"]
        hgt = max(float(rest[:, 1].max()), 0.3)
        # how near the heart (the light inside is strongest in the chest and fades toward the hands and feet)
        heart = np.array([0.0, 0.70 * hgt, 0.02 * hgt])
        dh = np.linalg.norm((rest - heart) * np.array([1.0, 0.75, 1.0]), axis=1) / hgt
        warm = np.exp(-(dh / sp.get("reach", 0.18)) ** 2)
        # the cut of the glass: irregular facets that catch the light each in its own way and shimmer together
        fid, fedge = facets(rest, sp.get("facet", 0.075) * hgt / 1.6)
        hue = fid * 0.8 + 0.2 * r2 + cloud["h"] * 0.3
        pr = sp.get("prism", 0.85)
        rainbow = prism(hue)
        sk = np.isin(part, (SKIN, HAND, FOOT))
        size = (0.0021 + 0.0022 * seed ** 4) * sz * np.where(sk, 0.85, 1.0)
        fseed = (fid * 0.999).astype(np.float32)
        # the edge: light where the glass turns away from the eye, in the spectrum's colours
        edge_col = np.ones(3)[None] * (1 - pr) + rainbow * pr
        edge_col = edge_col * 0.75 + c1[None] * 0.25
        fr = sp.get("front", 0.8)
        glass = soft_part * np.where(part == HAIR, 0.35, 1.0) * face_marks(rest, part, sp.get("features", 1.0))
        layers.append(dict(kind="soft", idx=allp, size=size, color=edge_col,
                           alpha=0.55 * b * glass * seam, emit=1.0, twinkle=0.45,
                           rim=(1.0, sp.get("power", 2.0)), backlight=0.35, front=fr * 0.7))
        # the facets' edges: fine lines of light where the cuts meet
        fe = allp[fedge > 0.45]
        fcol = rainbow[fe] * 0.55 + c1[None] * 0.25 + 0.2
        layers.append(dict(kind="soft", idx=fe, size=size[fe] * 0.9, color=fcol,
                           alpha=0.36 * b * sp.get("cuts", 1.0) * fedge[fe] * glass[fe], emit=1.0, twinkle=0.5,
                           rim=(0.35, 1.2), backlight=0.3, front=fr, lit=0.5))
        # the clear body: luminous glass, warm round the heart and cooler toward the limbs, each facet a little
        # brighter or darker; the face and hands warmer and fuller, so they are soft and alive, never hollow
        wk = np.clip(warm * 0.9 + np.where(sk, 0.15, 0.0), 0.0, 1.0)[:, None]
        clear = c2[None] * (1 - wk) + c1[None] * wk
        clear = clear * (0.85 + 0.3 * rainbow * 0.5)
        layers.append(dict(kind="soft", idx=allp, size=size * 1.05, color=clear,
                           alpha=0.20 * b * sp.get("clear", 1.0) * glass
                           * np.where(sk, 1.1 * (0.85 + 0.3 * fid), 0.25 + 1.5 * fid ** 1.5),
                           emit=1.0, twinkle=0.6, rim=(0.25, 1.2), backlight=0.25, seed=fseed, front=fr,
                           lit=sp.get("lit", 0.75)))
        # the light inside: larger soft points, warm, gathered round the heart
        inner = allp[(seed < 0.12) & ~((part == SKIN) & (cloud["h"] > 0.84)) & (part != HAIR)]
        layers.append(dict(kind="soft", idx=inner, size=0.020 * sz * (0.6 + 0.8 * r3[inner]),
                           color=np.broadcast_to(c1, (len(inner), 3)),
                           alpha=0.07 * b * sp.get("inner", 1.0) * soft_part[inner] * (0.12 + 0.88 * warm[inner]),
                           emit=1.0, twinkle=0.3, rim=(0.0, 2.0), backlight=0.4))
        # the face: a soft, even light over the skin of the head (luminous, never hollow), modelled by the
        # gentle features of face_marks
        fc = allp[(part == SKIN) & (cloud["h"] > 0.84)]
        layers.append(dict(kind="soft", idx=fc, size=np.full(len(fc), 0.0065 * sz),
                           color=np.broadcast_to(c1 * 0.45 + c2 * 0.25 + 0.3, (len(fc), 3)),
                           alpha=0.06 * b * sp.get("face", 1.0) * glass[fc], emit=1.0, twinkle=0.15,
                           rim=(0.0, 2.0), backlight=0.1, front=1.0, lit=0.5))
        # fine sparkle: four-point glints in the spectrum
        gl = allp[seed > 1.0 - sp.get("glints", 0.003)]
        layers.append(dict(kind="spark", idx=gl, size=0.0065 * sz * (0.7 + 0.6 * r3[gl]),
                           color=rainbow[gl] * 0.5 + 0.5, alpha=0.85 * b, emit=1.4 + 2.2 * r2[gl], twinkle=1.0,
                           rim=(0.45, 1.5), backlight=0.3, front=fr))
    elif name == "gold":
        rest = cloud["rest"]
        hgt = max(float(rest[:, 1].max()), 0.3)
        heart = np.array([0.0, 0.70 * hgt, 0.02 * hgt])
        dh = np.linalg.norm((rest - heart) * np.array([1.0, 0.75, 1.0]), axis=1) / hgt
        warm = np.exp(-(dh / sp.get("reach", 0.32)) ** 2)
        # three golds for depth: deep amber grains, gold, and pale champagne highlights
        deep = _col(sp.get("deep", "#b8741c"))
        mix = np.clip(_noise(rest, 3.0, 1.0) * 0.7 + 0.3 * r2, 0, 1)
        col = c1[None] * (1 - mix)[:, None] + c2[None] * mix[:, None]
        dk = r3 < sp.get("depth", 0.30)
        col[dk] = deep[None] * (0.7 + 0.3 * mix[dk, None])
        sk = np.isin(part, (SKIN, HAND, FOOT))
        col[sk] = col[sk] * 0.8 + c2[None] * 0.2
        tone = np.where(dk, 0.55, 0.8 + 0.45 * r2) * face_marks(rest, part, sp.get("features", 1.0))
        size = (0.0024 + 0.0060 * seed ** 4) * sz * np.where(sk, 0.85, 1.0)
        glint = seed > 1.0 - sp.get("glints", 0.0022)
        base = ~glint
        layers.append(dict(kind="soft", idx=allp[base], size=size[base], color=col[base] * tone[base, None],
                           alpha=0.46 * b * soft_part[base] * seam[base], emit=1.0, twinkle=0.85, rim=(0.40, 1.4),
                           backlight=0.2, front=sp.get("front", 0.55)))
        # a warm light within: the body glows from the heart
        inner = allp[seed < 0.10]
        layers.append(dict(kind="soft", idx=inner, size=0.018 * sz * (0.6 + 0.8 * r3[inner]),
                           color=np.broadcast_to(c1 * 0.6 + c2 * 0.4, (len(inner), 3)),
                           alpha=0.05 * b * sp.get("inner", 1.0) * soft_part[inner] * (0.25 + 0.75 * warm[inner]),
                           emit=1.0, twinkle=0.3, rim=(0.0, 2.0), backlight=0.4))
        layers.append(dict(kind="spark", idx=allp[glint], size=size[glint] * 1.1 + 0.002 * sz,
                           color=np.broadcast_to(c2 * 0.5 + 0.5, (int(glint.sum()), 3)), alpha=0.85 * b,
                           emit=1.3 + 2.0 * r2[glint], twinkle=1.0,
                           rim=(0.2, 1.5), backlight=0.3))
    elif name == "window":
        stars = allp[seed > 1.0 - sp.get("stars", 0.012)]
        layers.append(dict(kind="spark", idx=stars, size=(0.004 + 0.008 * r2[stars] ** 3) * sz,
                           color=np.broadcast_to(c2, (len(stars), 3)), alpha=0.6 * b, emit=1.5 + 2.5 * (r3[stars] > 0.85),
                           twinkle=1.0, rim=(0.0, 2.0), backlight=0.0))
        edge = allp[seed < 0.6]
        layers.append(dict(kind="soft", idx=edge, size=np.full(len(edge), 0.005 * sz), color=np.broadcast_to(c1, (len(edge), 3)),
                           alpha=0.55 * b, emit=1.2, twinkle=0.3, rim=(1.0, 3.2), backlight=0.0))
    for ly in layers:
        ly.setdefault("lit", 0.0)
        if "seed" not in ly:
            ly["seed"] = cloud["seed"][ly["idx"]]
        ly["color"] = np.ascontiguousarray(ly["color"], np.float32)
        ly["size"] = np.asarray(ly["size"], np.float32)
        if np.ndim(ly["alpha"]) == 0:
            ly["alpha"] = np.full(len(ly["idx"]), ly["alpha"], np.float32)
        else:
            ly["alpha"] = np.asarray(ly["alpha"], np.float32)
        if np.ndim(ly["emit"]) == 0:
            ly["emit"] = np.full(len(ly["idx"]), ly["emit"], np.float32)
        else:
            ly["emit"] = np.asarray(ly["emit"], np.float32)
    return layers
