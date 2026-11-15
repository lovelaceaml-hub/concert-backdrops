"""The campaign's brand as engine pieces: the logo, the nine expression symbols drawn in light, hearts, and the
world of light that becomes the logo (engine/p3d; pure numpy and PIL, no graphics context needed).

How a song uses it: engine/UPGRADE-HOWTO.md, section Z. Working example: engine/songs/demo_brand.py.

THE LOGO (this file)
  Two overlapping hearts (the left one gold to orange, the right one rose), a globe with white meridians and
  parallels over the hearts' join, and two white olive branches. Drawn from clean vector geometry measured on
  the campaign's own logo (the reference pictures are not stored or traced):

      each heart is the classic construction: a square standing on its corner with a half circle on each upper
      side. The two hearts stand side by side, their tips one square diagonal apart, so that the right lobe of
      the left heart and the left lobe of the right heart are the same circle: that circle is the globe.
      The left heart lies in front of the right heart, parted from it by a thin white line.

  logo_image(height, ...)      a crisp 2D picture with alpha (PIL RGBA), any size, for titles and the end card
  logo_rgba(height, ...)       the same as a numpy array (H, W, 4) uint8
  Logo(...)                    the logo as a point set for the 3D layer: it forms out of light, glows, holds,
                               and leaves; each part can be animated on its own
  logo_points(n)               the plain points of the logo by part (for effects of your own)
  PARTS                        "heart_r", "heart_l", "ring", "globe", "grid", "branch_l", "branch_r"

  Logo coordinates: "logo units", the logo 1.0 high, x to the right and y up from the centre of its box;
  LOGO_ASPECT is its width over its height (about 1.55).

THE REST (re-exported here, so `from p3d import brand` gives everything)
  hearts                  engine/p3d/brand_hearts.py   heart sprites, drifting hearts, points arranged as a heart
  the nine symbols        engine/p3d/brand_symbols.py  the expression symbols as strokes of light and six recipes
  the world               engine/p3d/brand_world.py    the globe of light, hearts across it, and world to logo
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .api import lin, show  # noqa: F401  (re-exported for song files: brand.lin, brand.show)

# ------------------------------------------------------------------------------------------------- colours
# Sampled from the campaign's logo (two references: a clean render and the website's version) and settled
# between them: the left heart runs from gold at the top to orange at the tip, the right heart is one rose,
# the globe runs from the orange of the left heart to the rose of the right one. Display hex.
LOGO_PALETTES = dict(
    # the default: the website's gold to orange gradient, at the strength of the official poster
    brand=dict(gold="#F1C665", orange="#EF9038", rose="#E25F70", globe_l="#EC8E48", globe_r="#DC6865",
               white="#FFFFFF"),
    # exactly as sampled from the website's logo (softer)
    web=dict(gold="#EECF7C", orange="#E09F53", rose="#D06369", globe_l="#DE9257", globe_r="#CE6C72",
             white="#FFFFFF"),
    # exactly as on the official poster (flat, vivid)
    poster=dict(gold="#F39431", orange="#F39431", rose="#EC5C72", globe_l="#F0904A", globe_r="#E2685E",
                white="#FFFFFF"),
)
LOGO_COLORS = LOGO_PALETTES["brand"]     # gold: top of the left heart, orange: its tip, rose: the right heart,
#                                          globe_l, globe_r: the globe's two sides, white: grid, ring, lines, branches

# The nine expressions in the website's colours (UPDATE 9; these replace the older campaign colours)
EXPRESSION_COLORS = {
    "Greeting": "#EA5A5E", "Gratitude": "#F2B25E", "Apology": "#F6CE46", "Inclusiveness": "#5ABA5A",
    "Concession": "#62B2FA", "Respect": "#667AF6", "Encouragement": "#9E6AF6", "Consideration": "#EE62A6",
    "Compliment": "#364E96",
}
NINE = list(EXPRESSION_COLORS.values())
LABELS = list(EXPRESSION_COLORS.keys())

PARTS = ("heart_r", "heart_l", "ring", "globe", "grid", "branch_l", "branch_r")
_PID = {p: i for i, p in enumerate(PARTS)}

# ------------------------------------------------------------------------------------------------ geometry
# Working units "a": the side of a heart's square over the square root of two. The left heart's tip is at
# (-0.5, 0), the right heart's at (0.5, 0), the globe's centre at (0, 1.5); a lobe's radius is 1/sqrt(2).
RL = 1.0 / math.sqrt(2.0)               # radius of a heart's lobe
GC = (-0.034, 1.462)                    # the globe's centre: a touch left of and below the hearts' inner lobes
RG = 0.725                              # the globe's outer radius (its white ring), a little over a lobe's
RING_W = 0.050                          # width of the white ring round the globe
RD = RG - RING_W                        # radius of the globe's coloured disc
GAP = 0.036                             # the white line that parts the left heart from the right one
LINE_W = 0.036                          # width of a grid line
A_H = 1.5 + RL                          # height of the logo (tips to the top of the lobes)
A_W = 2.0 * (1.0 + RL)                  # width of the logo
A_YC = 0.5 * A_H                        # the centre of its box
LOGO_ASPECT = A_W / A_H

# The globe's grid is a real sphere: its pole leans toward the viewer and a little to the right, as drawn
# (fitted to the reference's lines: 84 percent of its pixels agree).
POLE = np.array([0.215, 0.75, math.sqrt(1.0 - 0.215 ** 2 - 0.75 ** 2)])
MERIDIANS = 12                          # one every 30 degrees
MERIDIAN_PHASE = 12.0                   # degrees: where the first meridian lies (0 faces the viewer)
PARALLELS = (57.75, 38.5, 19.25, 0.0, -19.25, -38.5, -57.75)
POLE_CAP = 79.0                         # the small ring round the pole; finer lines run inside it
FAR_CAP = 63.0                          # beyond the pole (its far side) the globe is white above this latitude
FAR_LON = 100.0                         # ... over the longitudes this far round from the front

# The olive branches: a stem (cubic bezier) and leaves (base, tip, width), measured on the reference.
BRANCHES = {
    "branch_l": dict(
        stem=((-0.735, 1.215), (-0.80, 1.31), (-0.865, 1.42), (-0.872, 1.565)), stem_w=(0.040, 0.020),
        leaves=[((-0.770, 1.300), (-1.150, 1.282), 0.122, 0.10),       # (base, tip, width, where on the stem)
                ((-0.800, 1.350), (-0.722, 1.672), 0.112, 0.25),       # hugs the globe
                ((-0.852, 1.462), (-1.205, 1.532), 0.112, 0.62),
                ((-0.870, 1.548), (-0.982, 1.772), 0.094, 1.00)]),
    "branch_r": dict(
        stem=((0.215, 0.725), (0.50, 0.86), (0.76, 1.00), (0.885, 1.180)), stem_w=(0.040, 0.020),
        leaves=[((0.638, 0.519), (0.187, 0.551), 0.150, 0.06),         # the lowest leaf, under the stem
                ((0.245, 0.735), (0.315, 0.995), 0.118, 0.04),         # at the join, over the ring
                ((0.851, 0.719), (0.508, 0.777), 0.122, 0.30),
                ((0.505, 0.850), (0.575, 1.100), 0.104, 0.42),         # over the ring at the lower right
                ((0.722, 0.990), (0.748, 1.258), 0.092, 0.72),
                ((0.785, 0.956), (1.073, 1.012), 0.106, 0.70),
                ((0.880, 1.172), (0.985, 1.392), 0.094, 1.00)]),
}


def _bez(p0, p1, p2, p3, n=48):
    u = np.linspace(0.0, 1.0, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, np.float64) for p in (p0, p1, p2, p3))
    return ((1 - u) ** 3) * p0 + 3 * ((1 - u) ** 2) * u * p1 + 3 * (1 - u) * u * u * p2 + (u ** 3) * p3


def _arc(c, r, a0, a1, n):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)], axis=1)


def heart_outline(tip=(0.0, 0.0), a=1.0, n=96, lobes=(True, True)):
    """The classic heart (a square on its corner with a half circle on each upper side) as a closed polygon,
    counter clockwise from the tip. `tip` is the point at the bottom; the heart is 1 + 1/sqrt(2) times `a` wide
    on each side of the tip and 1.5 + 1/sqrt(2) times `a` high. `lobes` (left, right): False leaves that half
    circle out (the logo's left heart has no right lobe: the globe stands there)."""
    tx, ty = tip
    lc = (tx - 0.5 * a, ty + 1.5 * a)
    rc = (tx + 0.5 * a, ty + 1.5 * a)
    r = RL * a
    if lobes[1]:
        right = _arc(rc, r, -45.0, 135.0, n)      # from the right corner over the top to the cusp
    else:
        right = np.array([[tx + a, ty + a], [tx, ty + 2.0 * a]])
    if lobes[0]:
        left = _arc(lc, r, 45.0, 225.0, n)        # from the cusp over the top to the left corner
    else:
        left = np.array([[tx, ty + 2.0 * a], [tx - a, ty + a]])
    return np.vstack([[tx, ty], right, left[1:], [[tx, ty]]])


def heart_shape(n=200):
    """A heart for sprites and arrangements: the classic heart scaled to 1.0 high and centred on its box,
    as a closed polygon (n, 2), y up."""
    p = heart_outline((0.0, 0.0), 1.0, n=max(n // 2, 8))
    p = p - np.array([0.0, A_H * 0.5])
    return p / A_H


def _leaf_poly(base, tip, width, n=40, bend=0.06, grow=1.0):
    """A leaf: a lens from its base to its tip, a little fuller toward the base and bent a touch."""
    b, t = np.asarray(base, np.float64), np.asarray(tip, np.float64)
    t = b + (t - b) * grow
    d = t - b
    L = float(np.hypot(*d))
    if L < 1e-6:
        return None
    ax = d / L
    nr = np.array([-ax[1], ax[0]])
    u = np.linspace(0.0, 1.0, n)
    hw = 0.5 * width * grow * np.sin(np.pi * u) ** 0.82 * (1.10 - 0.20 * u)
    mid = b[None, :] + u[:, None] * d[None, :] + (bend * L * np.sin(np.pi * u))[:, None] * nr[None, :]
    side1 = mid + hw[:, None] * nr[None, :]
    side2 = mid - hw[:, None] * nr[None, :]
    return np.vstack([side1, side2[::-1]])


def _stem_poly(spec, upto=1.0, n=48):
    """The stem as a tapering band, drawn from its base up to `upto` (0..1) of its length."""
    p = _bez(*spec["stem"], n=n)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)]) / max(seg.sum(), 1e-9)
    keep = s <= upto + 1e-9
    if upto < 1.0:
        k = int(np.searchsorted(s, upto))
        if 0 < k < len(s):
            f = (upto - s[k - 1]) / max(s[k] - s[k - 1], 1e-9)
            p = np.vstack([p[:k], p[k - 1] + (p[k] - p[k - 1]) * f])
            s = np.concatenate([s[:k], [upto]])
        else:
            p, s = p[keep], s[keep]
    if len(p) < 2:
        return None
    w0, w1 = spec["stem_w"]
    w = w0 + (w1 - w0) * s
    tg = np.gradient(p, axis=0)
    tg /= np.maximum(np.linalg.norm(tg, axis=1, keepdims=True), 1e-9)
    nr = np.stack([-tg[:, 1], tg[:, 0]], axis=1)
    return np.vstack([p + 0.5 * w[:, None] * nr, (p - 0.5 * w[:, None] * nr)[::-1]])


def stem_path(part, n=64):
    """The centre line of a branch's stem (n, 2), in working units."""
    return _bez(*BRANCHES[part]["stem"], n=n)


def _pole_frame():
    p = POLE
    ea = np.array([0.0, 0.0, 1.0]) - p * p[2]
    ea /= np.linalg.norm(ea)
    eb = np.cross(p, ea)
    return p, ea, eb


def _sphere(lat, lon):
    """Points of the globe's own sphere (unit radius, viewer at +z) at latitudes and longitudes (degrees)."""
    p, ea, eb = _pole_frame()
    la, lo = np.radians(lat), np.radians(lon)
    return (np.cos(la) * np.cos(lo))[..., None] * ea + (np.cos(la) * np.sin(lo))[..., None] * eb \
        + np.sin(la)[..., None] * p


def grid_lines():
    """The globe's grid as 2D polylines in working units, only their sides facing the viewer. Returns a list of
    dicts: pts (n, 2), w (width), kind ("meridian", "parallel", "cap", "fine"), order (the order lines are
    drawn in when the grid draws itself, 0..1), and z (n,) the sphere's bulge toward the viewer (0..1)."""
    out = []

    def add(xyz, w, kind, order):
        vis = xyz[:, 2] > 0.0
        if vis.sum() < 2:
            return
        idx = np.nonzero(vis)[0]
        # split into runs of visible points
        runs = np.split(idx, np.nonzero(np.diff(idx) > 1)[0] + 1)
        for r in runs:
            if len(r) < 2:
                continue
            q = xyz[r]
            out.append(dict(pts=np.stack([GC[0] + RD * q[:, 0], GC[1] + RD * q[:, 1]], axis=1), w=w, kind=kind,
                            order=order, z=np.clip(q[:, 2], 0.0, 1.0)))

    for j, la in enumerate(PARALLELS):
        lon = np.linspace(-180.0, 180.0, 361)
        add(_sphere(np.full_like(lon, la), lon), LINE_W, "parallel", 0.1 + 0.5 * j / len(PARALLELS))
    add(_sphere(np.full(181, POLE_CAP), np.linspace(-180.0, 180.0, 181)), LINE_W * 0.8, "cap", 0.0)
    for i in range(MERIDIANS):
        lo = MERIDIAN_PHASE + 360.0 * i / MERIDIANS
        lat = np.linspace(-90.0, POLE_CAP, 200)
        add(_sphere(lat, np.full_like(lat, lo)), LINE_W, "meridian", 0.35 + 0.5 * ((i * 5) % MERIDIANS) / MERIDIANS)
        lat = np.linspace(POLE_CAP, 89.0, 24)
        add(_sphere(lat, np.full_like(lat, lo)), LINE_W * 0.42, "fine", 0.05)
    return out


def far_cap_outline(n=90):
    """The white region beyond the pole (latitude above FAR_CAP on the far half) as a 2D polygon in working
    units: its hidden parts are pushed out to the globe's edge, which bounds what shows."""
    lat_up = np.linspace(FAR_CAP, 89.9, n // 3)
    loop = [_sphere(lat_up, np.full_like(lat_up, FAR_LON)),
            _sphere(lat_up[::-1], np.full_like(lat_up, -FAR_LON)),
            _sphere(np.full(n, FAR_CAP), np.linspace(-FAR_LON, FAR_LON - 360.0, n))]
    q = np.vstack(loop)
    xy = q[:, :2].copy()
    back = q[:, 2] < 0.0
    xy[back] /= np.maximum(np.linalg.norm(xy[back], axis=1, keepdims=True), 1e-9)
    return np.stack([GC[0] + RD * xy[:, 0], GC[1] + RD * xy[:, 1]], axis=1)


def _far_cap(X, Y):
    """1 where the globe's far side beyond the pole shows (white in the logo), for working-unit places."""
    u = (np.asarray(X) - GC[0]) / RD
    v = (np.asarray(Y) - GC[1]) / RD
    z = np.sqrt(np.maximum(1.0 - u * u - v * v, 0.0))
    p, ea, eb = _pole_frame()
    s = u * p[0] + v * p[1] + z * p[2]
    lo = np.degrees(np.arctan2(u * eb[0] + v * eb[1] + z * eb[2], u * ea[0] + v * ea[1] + z * ea[2]))
    la = np.degrees(np.arcsin(np.clip(s, -1.0, 1.0)))
    return ((la > FAR_CAP) & (np.abs(lo) > 90.0) & (u * u + v * v < 1.0)).astype(np.float32)


# --------------------------------------------------------------------------------------------- the raster
class _Canvas:
    """Draws shapes given in working units into coverage pictures (0..1), supersampled."""

    def __init__(self, scale, pad=0.06, ss=4):
        self.scale, self.ss = float(scale), int(ss)
        self.x0, self.y1 = -A_W * 0.5 - pad, A_H + pad
        self.w = int(math.ceil((A_W + 2 * pad) * scale))
        self.h = int(math.ceil((A_H + 2 * pad) * scale))

    def px(self, p):
        p = np.asarray(p, np.float64)
        k = self.scale * self.ss
        return [((x - self.x0) * k, (self.y1 - y) * k) for x, y in p]

    def new(self):
        img = Image.new("L", (self.w * self.ss, self.h * self.ss), 0)
        return img, ImageDraw.Draw(img)

    def done(self, img):
        return np.asarray(img.resize((self.w, self.h), Image.BOX), np.float32) / 255.0

    def poly(self, polys, value=255, img=None):
        if img is None:
            img, d = self.new()
        else:
            d = ImageDraw.Draw(img)
        for p in polys:
            if p is not None and len(p) >= 3:
                d.polygon(self.px(p), fill=value)
        return img

    def strokes(self, lines, value=255, img=None, upto=None):
        """Polylines of given widths with round ends; `upto` (a list of 0..1) draws only part of each."""
        if img is None:
            img, d = self.new()
        else:
            d = ImageDraw.Draw(img)
        k = self.scale * self.ss
        for i, ln in enumerate(lines):
            p = ln["pts"]
            if upto is not None:
                f = float(upto[i])
                if f <= 0.0:
                    continue
                if f < 1.0:
                    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
                    s = np.concatenate([[0.0], np.cumsum(seg)]) / max(seg.sum(), 1e-9)
                    m = int(np.searchsorted(s, f))
                    p = p[:max(m, 2)]
            w = max(ln["w"] * k, 1.0)
            pts = np.asarray(self.px(p), np.float64)
            d.polygon([tuple(q) for q in _stroke_poly(pts, w)], fill=value)
        return img

    def disc(self, c, r):
        img, d = self.new()
        (x, y), = self.px([c])
        R = r * self.scale * self.ss
        d.ellipse((x - R, y - R, x + R, y + R), fill=255)
        return img

    def coords(self):
        """Working-unit coordinates of every pixel centre (x, y)."""
        xs = self.x0 + (np.arange(self.w) + 0.5) / self.scale
        ys = self.y1 - (np.arange(self.h) + 0.5) / self.scale
        return np.meshgrid(xs, ys)


def _stroke_poly(pts, w, cap_n=10):
    """A polyline of width w with round ends as one polygon (smooth edges, no beads at the joints)."""
    p = np.asarray(pts, np.float64)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    keep = np.concatenate([[True], seg > 1e-6])
    p = p[keep]
    if len(p) < 2:
        p = np.vstack([p[:1], p[:1] + [1e-3, 0.0]])
    tg = np.gradient(p, axis=0)
    tg /= np.maximum(np.linalg.norm(tg, axis=1, keepdims=True), 1e-9)
    nr = np.stack([-tg[:, 1], tg[:, 0]], axis=1)
    h = 0.5 * w
    left, right = p + h * nr, p - h * nr
    a0 = math.atan2(nr[-1, 1], nr[-1, 0])
    end = [p[-1] + h * np.array([math.cos(a0 - math.pi * k / cap_n), math.sin(a0 - math.pi * k / cap_n)])
           for k in range(1, cap_n)]
    a1 = math.atan2(-nr[0, 1], -nr[0, 0])
    start = [p[0] + h * np.array([math.cos(a1 - math.pi * k / cap_n), math.sin(a1 - math.pi * k / cap_n)])
             for k in range(1, cap_n)]
    return np.vstack([left, np.array(end).reshape(-1, 2), right[::-1], np.array(start).reshape(-1, 2)])


def _hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def _branch_polys(part, grow=1.0):
    """Polygons of a branch, grown to `grow` (0..1): the stem reaches up first, each leaf opens when the stem
    passes its place."""
    spec = BRANCHES[part]
    polys = [_stem_poly(spec, upto=min(grow * 1.15, 1.0))]
    for (b, t, w, s) in spec["leaves"]:
        g = float(np.clip((grow - s * 0.70) / 0.30, 0.0, 1.0))
        if g > 0.0:
            polys.append(_leaf_poly(b, t, w, grow=g * g * (3 - 2 * g)))
    return polys


def _layers(canvas, draw=None, palette="brand", full=False):
    """Coverage of every part (own shape, before anything covers it), plus each part's colour picture.
    `draw` (dict part -> 0..1) draws the grid and the branches only partly (they draw themselves)."""
    draw = draw or {}
    X, Y = canvas.coords()
    cov = {}
    tipl, tipr = (-0.5, 0.0), (0.5, 0.0)
    cov["heart_r"] = canvas.done(canvas.poly([heart_outline(tipr, lobes=(False, True))]))
    hl = heart_outline(tipl, lobes=(True, False))
    cov["heart_l"] = canvas.done(canvas.poly([hl]))
    # the white parting line: the left heart grown by GAP, only where it lies over the right heart
    img, d = canvas.new()
    d.polygon(canvas.px(hl), fill=255)
    d.line(canvas.px(hl), fill=255, width=int(round(2 * GAP * canvas.scale * canvas.ss)), joint="curve")
    gap = canvas.done(img)
    cov["gap"] = np.clip(gap - cov["heart_l"], 0.0, 1.0) * cov["heart_r"] * (1.0 - canvas.done(canvas.disc(GC, RG - 0.01)))
    if full:
        # whole classic hearts (for the build, before the globe stands over their inner lobes)
        cov["heart_r_full"] = canvas.done(canvas.poly([heart_outline(tipr)]))
        hf = heart_outline(tipl)
        cov["heart_l_full"] = canvas.done(canvas.poly([hf]))
        img, d = canvas.new()
        d.polygon(canvas.px(hf), fill=255)
        d.line(canvas.px(hf), fill=255, width=int(round(2 * GAP * canvas.scale * canvas.ss)), joint="curve")
        cov["heart_l_grown"] = canvas.done(img)
    cov["ring"] = canvas.done(canvas.disc(GC, RG))
    cov["globe"] = canvas.done(canvas.disc(GC, RD))
    lines = grid_lines()
    g = draw.get("grid", 1.0)
    upto = None
    if g < 1.0:
        upto = [float(np.clip((g - 0.55 * ln["order"]) / 0.45, 0.0, 1.0)) for ln in lines]
    cov["grid"] = canvas.done(canvas.strokes(lines, upto=upto))
    # the far side beyond the pole is white; it draws with the first lines
    far = canvas.done(canvas.poly([far_cap_outline()])) * float(np.clip(g / 0.3, 0.0, 1.0))
    cov["grid"] = np.maximum(cov["grid"], far) * cov["globe"]
    for b in ("branch_l", "branch_r"):
        cov[b] = canvas.done(canvas.poly(_branch_polys(b, draw.get(b, 1.0))))
    # colours (display rgb, 0..1)
    c = {}
    P = LOGO_PALETTES[palette] if isinstance(palette, str) else dict(LOGO_COLORS, **palette)
    gold, orange = _hex_rgb(P["gold"]), _hex_rgb(P["orange"])
    k = np.clip(Y / A_H, 0.0, 1.0)[..., None]
    c["heart_l"] = orange * (1 - k) + gold * k
    c["heart_r"] = np.broadcast_to(_hex_rgb(P["rose"]), X.shape + (3,))
    gl, gr = _hex_rgb(P["globe_l"]), _hex_rgb(P["globe_r"])
    u = np.clip((X - GC[0]) / (2 * RD) + 0.5, 0.0, 1.0)[..., None]
    v = np.clip((Y - GC[1]) / (2 * RD), -0.5, 0.5)[..., None]
    c["globe"] = np.clip((gl * (1 - u) + gr * u) * (1.0 + 0.05 * v), 0.0, 1.0)
    white = np.broadcast_to(_hex_rgb(P["white"]), X.shape + (3,))
    for p in ("gap", "ring", "grid", "branch_l", "branch_r"):
        c[p] = white
    return cov, c


# drawn back to front; "gap" belongs to the left heart, "ring" is the white outline of the globe
_ORDER = ("heart_r", "gap", "heart_l", "ring", "globe", "grid", "branch_l", "branch_r")


def _amount(parts, name):
    if parts is None:
        return 1.0
    if isinstance(parts, dict):
        if name == "gap":
            return float(parts.get("heart_l", parts.get("gap", 1.0)))
        return float(parts.get(name, 0.0 if name not in parts else 1.0))
    key = "heart_l" if name == "gap" else name
    return 1.0 if key in parts else 0.0


_RGBA = {}


def logo_rgba(height=320, parts=None, draw=None, pad=0.06, glow=0.0, glow_color="#FFF3DA", palette="brand",
              ss=4):
    """The logo as an RGBA picture (numpy uint8, straight alpha), `height` pixels for the logo itself (the
    picture is a little larger by `pad`, in logo heights, on every side).

    parts    None for the whole logo, a list of part names to draw, or a dict part -> opacity 0..1
    draw     dict part -> 0..1: the grid ("grid") and the branches ("branch_l", "branch_r") drawn only partly,
             as they draw themselves (grid lines run along their length; a stem grows and its leaves open)
    glow     0..1: a soft halo round the logo (in the alpha), for a night sky
    palette  "brand" (default: the website's gold to orange gradient at the official poster's strength),
             "web" (the website's softer colours exactly), "poster" (the official poster's flat vivid colours),
             or a dict of LOGO_COLORS keys to change
    The last 24 pictures are kept, so asking again for the same one costs nothing.
    """
    key = repr((round(float(height), 3), parts, draw, pad, glow, glow_color, palette, ss))
    if key in _RGBA:
        return _RGBA[key]
    out = _logo_rgba(height, parts, draw, pad, glow, glow_color, palette, ss)
    if len(_RGBA) >= 24:
        _RGBA.pop(next(iter(_RGBA)))
    _RGBA[key] = out
    return out


def _logo_rgba(height, parts, draw, pad, glow, glow_color, palette, ss):
    scale = float(height) / A_H
    cv = _Canvas(scale, pad=pad * A_H, ss=ss)
    cov, col = _layers(cv, draw, palette)
    rgb = np.zeros((cv.h, cv.w, 3), np.float32)
    a = np.zeros((cv.h, cv.w), np.float32)
    for name in _ORDER:                     # "over", premultiplied
        k = cov[name] * _amount(parts, name)
        rgb = rgb * (1.0 - k[..., None]) + col[name] * k[..., None]
        a = a * (1.0 - k) + k
    if glow > 0.0:
        halo = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(height * 0.06, 1.0)))
        h = np.asarray(halo, np.float32) / 255.0 * float(glow) * 0.55
        gc = _hex_rgb(glow_color)
        rgb = rgb + gc * (h * (1.0 - a))[..., None]
        a = a + h * (1.0 - a)
    rgb = rgb / np.maximum(a[..., None], 1e-6)       # straight alpha
    out = np.dstack([np.clip(rgb, 0, 1) * 255.0, np.clip(a, 0, 1) * 255.0])
    return np.round(out).astype(np.uint8)


def logo_image(height=320, **kw):
    """The logo as a PIL RGBA image; the keys of logo_rgba."""
    return Image.fromarray(logo_rgba(height, **kw), "RGBA")


def logo_box(height=320, pad=0.06):
    """(width, height) in pixels of logo_image(height, pad=pad), and the logo's own box inside it
    (x0, y0, x1, y1), so a title can be laid out round it."""
    cv = _Canvas(float(height) / A_H, pad=pad * A_H)
    x0 = (-A_W * 0.5 - cv.x0) * cv.scale
    y0 = (cv.y1 - A_H) * cv.scale
    return (cv.w, cv.h), (x0, y0, x0 + A_W * cv.scale, y0 + A_H * cv.scale)


# ------------------------------------------------------------------------------------------ the points
_PTS = {}


def _label_image(cv):
    """For each pixel the element it belongs to inside its part: grid line index, leaf or stem index."""
    lines = grid_lines()
    lab_grid = np.full((cv.h, cv.w), -1, np.int32)
    img = Image.new("I", (cv.w * cv.ss, cv.h * cv.ss), -1)
    for i, ln in enumerate(lines):
        cv.strokes([ln], value=i, img=img)
    lab = np.asarray(img, np.int32)[cv.ss // 2::cv.ss, cv.ss // 2::cv.ss]
    lab_grid[:] = lab[:cv.h, :cv.w]
    labs = {"grid": lab_grid}
    for b in ("branch_l", "branch_r"):
        spec = BRANCHES[b]
        img = Image.new("I", (cv.w * cv.ss, cv.h * cv.ss), -1)
        cv.poly([_stem_poly(spec)], value=0, img=img)
        for j, (bb, tt, w, s) in enumerate(spec["leaves"]):
            cv.poly([_leaf_poly(bb, tt, w)], value=j + 1, img=img)
        labs[b] = np.asarray(img, np.int32)[cv.ss // 2::cv.ss, cv.ss // 2::cv.ss][:cv.h, :cv.w]
    return lines, labs


def _lattice(cov, b, rng, min_cov=0.06, jitter=0.25):
    """One point per b x b cell that holds coverage, at the centre of the coverage in the cell, weighted by it
    (the same scheme as the particle words: crisp, antialiased edges)."""
    h, w = cov.shape
    h2, w2 = h - h % b, w - w % b
    blk = cov[:h2, :w2].reshape(h2 // b, b, w2 // b, b)
    m = blk.mean(axis=(1, 3))
    off = np.arange(b, dtype=np.float32) + 0.5
    tot = np.maximum(blk.sum(axis=(1, 3)), 1e-6)
    cx = (blk.sum(axis=1) * off[None, None, :]).sum(axis=2) / tot
    cy = (blk.sum(axis=3) * off[None, :, None]).sum(axis=1) / tot
    iy, ix = np.nonzero(m > min_cov)
    k = iy.size
    x = ix * b + cx[iy, ix] + (rng.random(k) - 0.5) * b * jitter
    y = iy * b + cy[iy, ix] + (rng.random(k) - 0.5) * b * jitter
    return x, y, np.clip(m[iy, ix] * 1.10, 0.0, 1.0)


def logo_points(n=60000, seed=7, palette="brand"):
    """The logo as points, in logo units (1.0 high, centred on its box), by part. Returns a dict of arrays:

      x, y, z      position (z: the globe's points sit on its sphere, bulging toward the viewer up to `RD`)
      part         index into PARTS
      weight       0..1 (antialiased edges)
      rgb          display colour 0..1 (N, 3)
      covered      (N, len(PARTS)) how much each other part covers this point when the logo is whole
      order        0..1 within its part: when the point appears as the part draws itself (grid lines along
                   their length in a staggered order; a branch from the stem's foot outward, each leaf from
                   its base; the ring round from the bottom; the globe from its centre; hearts top down)
      elem         the element inside the part (grid line or leaf number; -1 none)
      cell         lattice spacing (logo units)
    Cached by (n, seed)."""
    key = (int(n), int(seed), str(palette))
    if key in _PTS:
        return _PTS[key]
    # resolution: about n points over the logo's inked area (about 6.9 square working units), 3 x 3 pixel cells
    area = 6.9
    b = 3
    scale = math.sqrt(n / area) * b
    cv = _Canvas(scale, pad=0.03, ss=2)
    cov, col = _layers(cv, palette=palette, full=True)
    lines, labs = _label_image(cv)
    X, Y = cv.coords()
    rng = np.random.default_rng(seed)
    # the hearts are sampled whole (classic shape); their inner lobes go when the globe arrives
    parts = {"heart_r": cov["heart_r_full"], "heart_l": np.maximum(cov["heart_l_full"], cov["gap"]),
             "ring": cov["ring"], "globe": cov["globe"], "grid": cov["grid"], "branch_l": cov["branch_l"],
             "branch_r": cov["branch_r"]}
    # what covers what when the logo is whole (later parts cover earlier ones)
    out = {k: [] for k in ("x", "y", "z", "part", "weight", "rgb", "covered", "order", "elem", "inner", "gapw")}
    for pi, name in enumerate(PARTS):
        c = parts[name]
        if name == "ring":
            c = np.clip(c - cov["globe"], 0.0, 1.0)          # the ring is the white band outside the disc
        px, py, w = _lattice(c, b, rng)
        ix = np.clip(px.astype(np.int64), 0, cv.w - 1)
        iy = np.clip(py.astype(np.int64), 0, cv.h - 1)
        x = cv.x0 + px / cv.scale
        y = cv.y1 - py / cv.scale
        # colour: the part's own (the left heart's band over the right heart is white)
        g = np.zeros(len(x))
        if name == "heart_l":
            g = np.clip(cov["gap"][iy, ix] / np.maximum(parts[name][iy, ix], 1e-6), 0.0, 1.0)
            rgb = col["heart_l"][iy, ix] * (1 - g[:, None]) + g[:, None] * 1.0
        else:
            rgb = np.asarray(col[name])[iy, ix] if np.ndim(col[name]) == 3 else np.broadcast_to(col[name], (len(x), 3))
        covered = np.zeros((len(x), len(PARTS)), np.float32)
        for qi, other in enumerate(PARTS):
            if qi <= pi:
                continue
            oc = parts[other]
            if other == "ring":
                oc = cov["ring"]
            covered[:, qi] = oc[iy, ix]
        inner = np.zeros(len(x), np.float32)
        if name == "heart_r":
            covered[:, _PID["heart_l"]] = cov["heart_l_grown"][iy, ix]
            inner = np.clip(1.0 - cov["heart_r"][iy, ix], 0.0, 1.0)
        if name == "heart_l":
            inner = np.clip(1.0 - np.maximum(cov["heart_l"][iy, ix], cov["gap"][iy, ix]), 0.0, 1.0)
        # z: the globe's parts sit on its sphere
        r = np.hypot(x - GC[0], y - GC[1])
        z = np.zeros_like(x)
        if name in ("globe", "grid"):
            z = np.sqrt(np.maximum(RD * RD - r * r, 0.0))
        elif name in ("branch_l", "branch_r"):
            z = np.full_like(x, 0.02)
        # order of drawing within the part
        elem = np.full(len(x), -1, np.int64)
        if name == "heart_l":
            elem = np.where(g > 0.5, 1, -1)                  # 1: the white parting line over the right heart
        if name == "grid":
            elem = labs["grid"][iy, ix]
            order = np.zeros(len(x))
            for li, ln in enumerate(lines):
                sel = elem == li
                if not sel.any():
                    continue
                p = ln["pts"]
                seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
                s = np.concatenate([[0.0], np.cumsum(seg)]) / max(seg.sum(), 1e-9)
                dd = (x[sel, None] - p[None, :, 0]) ** 2 + (y[sel, None] - p[None, :, 1]) ** 2
                along = s[np.argmin(dd, axis=1)]
                order[sel] = np.clip(0.55 * ln["order"] + 0.45 * along, 0.0, 1.0)
            order[elem < 0] = 0.5
        elif name in ("branch_l", "branch_r"):
            spec = BRANCHES[name]
            elem = labs[name][iy, ix]
            path = stem_path(name, 96)
            seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
            s = np.concatenate([[0.0], np.cumsum(seg)]) / max(seg.sum(), 1e-9)
            dd = (x[:, None] - path[None, :, 0]) ** 2 + (y[:, None] - path[None, :, 1]) ** 2
            order = 0.8 * s[np.argmin(dd, axis=1)]
            for j, (bb, tt, wl, sj) in enumerate(spec["leaves"]):
                sel = elem == j + 1
                if not sel.any():
                    continue
                bb, tt = np.asarray(bb), np.asarray(tt)
                ax = tt - bb
                u = ((x[sel] - bb[0]) * ax[0] + (y[sel] - bb[1]) * ax[1]) / max(float(ax @ ax), 1e-9)
                order[sel] = np.clip(sj * 0.70 + 0.30 * np.clip(u, 0.0, 1.0), 0.0, 1.0)
        elif name == "ring":
            ang = np.degrees(np.arctan2(y - GC[1], x - GC[0]))
            order = np.mod(ang + 90.0, 360.0) / 360.0       # from the bottom, round counter clockwise
        elif name == "globe":
            order = np.clip(r / RD, 0.0, 1.0)
        else:
            order = np.clip(1.0 - y / A_H, 0.0, 1.0)
        for k_, v in (("x", x), ("y", y), ("z", z), ("weight", w), ("rgb", rgb), ("covered", covered),
                      ("order", order), ("elem", elem), ("inner", inner), ("gapw", g)):
            out[k_].append(np.asarray(v))
        out["part"].append(np.full(len(x), pi, np.int64))
    res = {k: np.concatenate(v) for k, v in out.items()}
    # logo units: 1.0 high, centred on the box
    res["x"] = (res["x"] / A_H).astype(np.float32)
    res["y"] = ((res["y"] - A_YC) / A_H).astype(np.float32)
    res["z"] = (res["z"] / A_H).astype(np.float32)
    res["cell"] = float(b / cv.scale / A_H)
    res["inner"] = res["inner"].astype(np.float32)
    res["gapw"] = res["gapw"].astype(np.float32)
    # the left heart (grown by the parting line) as a picture in logo units, to test what it covers while the
    # hearts still move: value at column (x - x0) * k, row (y1 - y) * k
    res["mask_l"] = (cov["heart_l_grown"].astype(np.float32), cv.x0 / A_H, (cv.y1 - A_YC) / A_H, cv.scale * A_H)
    res["rgb"] = res["rgb"].astype(np.float32)
    res["weight"] = res["weight"].astype(np.float32)
    res["order"] = res["order"].astype(np.float32)
    res["covered"] = res["covered"].astype(np.float32)
    _PTS[key] = res
    return res


def to_logo_units(p):
    """Working units (a) to logo units."""
    p = np.asarray(p, np.float64)
    return np.stack([p[..., 0] / A_H, (p[..., 1] - A_YC) / A_H], axis=-1)


GLOBE_CENTER = tuple(to_logo_units(GC).tolist())       # the globe's centre in logo units
GLOBE_RADIUS = RG / A_H                                # the globe (with its ring) in logo units
GLOBE_DISC = RD / A_H                                  # the coloured disc in logo units


def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _val(v, t):
    return v(t) if callable(v) else v


def show_rgb(rgb):
    """Display colours (N, 3) in 0..1 as the linear light the finished picture shows as exactly those colours
    (api.show for many colours at once)."""
    y = np.clip(np.asarray(rgb, np.float64) ** 2.2, 0.0, 0.975)
    a, b, c = 2.43 * y - 2.51, 0.59 * y - 0.03, 0.14 * y
    return (-b - np.sqrt(np.maximum(b * b - 4.0 * a * c, 0.0))) / (2.0 * a)


def _unit(v):
    v = np.asarray(v, np.float64)
    return v / max(float(np.linalg.norm(v)), 1e-9)


# ------------------------------------------------------------------------------------- placing in the world
class Place:
    """Where a flat piece (the logo, a symbol, a heart) stands in the world, at any time.

    pos      centre (x, y, z) in metres, or a function of t
    size     its height in metres (a number or a function of t)
    facing   azimuth in degrees the piece faces (0 faces +z, the default camera), a number or a function of t
    face     "fixed" (use facing), "camera" (turns about the vertical to face the camera), "screen" (flat to
             the picture), "flat" (lying on the lake, read from above; facing turns it)
    tilt     degrees it leans back; roll: degrees it turns in its own plane (numbers or functions of t)
    ride     (x, y, depth): instead of pos, keep that place of the picture (0..1 from the left and the bottom)
             `depth` metres ahead of the lens, whatever the camera does; flat to the picture. Then `frac`
             gives the size as a share of the picture's height (instead of `size` in metres)
    keys     [(t, dict(any of the keys above)), ...]: the place changes over time; between two keys it glides
             (eased) from one to the other, centre, turn and size together

    place.frame(t, cam) -> (centre, right, up, normal, size): the plane in the world and the size in metres.
    Needs the camera (cam) for "camera", "screen" and ride; a set using them asks for it (wants_camera).
    """

    def __init__(self, pos=(0.0, 3.0, 0.0), size=2.0, facing=0.0, face="fixed", tilt=0.0, roll=0.0, ride=None,
                 frac=0.2, keys=None):
        self.base = dict(pos=pos, size=size, facing=facing, face=face, tilt=tilt, roll=roll, ride=ride, frac=frac)
        self.keys = sorted(keys, key=lambda k: k[0]) if keys else None

    def needs_camera(self):
        specs = [self.base] + ([dict(self.base, **k[1]) for k in self.keys] if self.keys else [])
        return any(s.get("ride") is not None or s.get("face") in ("camera", "screen") for s in specs)

    @staticmethod
    def _one(s, t, cam):
        if s.get("ride") is not None:
            if cam is None:
                raise ValueError("a ride needs the camera")
            x, y, d = (float(v) for v in _val(s["ride"], t))
            r, u, f = cam.basis()
            th = math.tan(math.radians(cam.fov) * 0.5)
            c = np.asarray(cam.pos, np.float64) + d * (f + (2 * x - 1) * th * cam.aspect * r + (2 * y - 1) * th * u)
            size = 2.0 * d * th * float(_val(s.get("frac", 0.2), t))
            return c, r, u, -f, size
        c = np.asarray(_val(s["pos"], t), np.float64)
        size = float(_val(s["size"], t))
        face = s.get("face", "fixed")
        if face == "screen":
            r, u, f = cam.basis()
            right, up, nrm = r, u, -f
        else:
            if face == "camera" and cam is not None:
                d = np.asarray(cam.pos, np.float64) - c
                az = math.degrees(math.atan2(d[0], d[2]))
            else:
                az = float(_val(s.get("facing", 0.0), t))
            a = math.radians(az)
            nrm = np.array([math.sin(a), 0.0, math.cos(a)])
            right = np.array([math.cos(a), 0.0, -math.sin(a)])
            up = np.array([0.0, 1.0, 0.0])
            if face == "flat":
                up, nrm = -nrm, np.array([0.0, 1.0, 0.0])
            tl = math.radians(float(_val(s.get("tilt", 0.0), t)))
            if tl:
                up, nrm = up * math.cos(tl) - nrm * math.sin(tl), nrm * math.cos(tl) + up * math.sin(tl)
        rl = math.radians(float(_val(s.get("roll", 0.0), t)))
        if rl:
            right, up = right * math.cos(rl) + up * math.sin(rl), up * math.cos(rl) - right * math.sin(rl)
        return c, right, up, nrm, size

    def frame(self, t, cam=None):
        if not self.keys:
            return self._one(self.base, t, cam)
        ks = self.keys
        if t <= ks[0][0]:
            return self._one(dict(self.base, **ks[0][1]), t, cam)
        if t >= ks[-1][0]:
            return self._one(dict(self.base, **ks[-1][1]), t, cam)
        for (t0, a), (t1, b) in zip(ks[:-1], ks[1:]):
            if t0 <= t <= t1:
                fa = self._one(dict(self.base, **a), t, cam)
                fb = self._one(dict(self.base, **b), t, cam)
                w = _sc(t0, t1, t)
                c = fa[0] * (1 - w) + fb[0] * w
                r = _unit(fa[1] * (1 - w) + fb[1] * w)
                u = fa[2] * (1 - w) + fb[2] * w
                u = _unit(u - r * float(u @ r))
                n = np.cross(r, u)
                return c, r, u, n, fa[4] * (1 - w) + fb[4] * w
        return self._one(self.base, t, cam)

    def world(self, t, x, y, z=None, cam=None):
        """Points given in the piece's own units (1.0 = its size; x right, y up, z toward the viewer) as world
        points (N, 3) at t."""
        c, r, u, n, s = self.frame(t, cam)
        x = np.asarray(x, np.float64)
        p = c[None, :] + s * (x[:, None] * r[None, :] + np.asarray(y, np.float64)[:, None] * u[None, :])
        if z is not None:
            p = p + s * np.asarray(z, np.float64)[:, None] * n[None, :]
        return p


def place_on_screen(camera, t, x, y, depth, frac):
    """(pos, size) of a piece seen at the picture place (x, y) (0..1 from the left and the bottom) `depth`
    metres ahead of the camera at t and `frac` of the picture's height tall. camera: a Rig, or a function
    of t giving a CameraState."""
    cam = camera.state(t) if hasattr(camera, "state") else camera(t)
    c, r, u, n, s = Place(ride=(x, y, depth), frac=frac)._one(dict(ride=(x, y, depth), frac=frac), t, cam)
    return tuple(c.tolist()), s


def _cam_of(camera, t):
    if camera is None:
        return None
    return camera.state(t) if hasattr(camera, "state") else camera(t)


# ------------------------------------------------------------------------------------- the logo in the world
# the brand build: when each part arrives, as shares of the arrival time (start, end)
BUILD = dict(heart_l=(0.00, 0.50), heart_r=(0.06, 0.56), ring=(0.36, 0.62), globe=(0.30, 0.58),
             grid=(0.50, 0.88), branch_l=(0.66, 1.00), branch_r=(0.62, 0.98))
GATHER_ORDER = dict(heart_r=0.00, heart_l=0.05, ring=0.30, globe=0.32, grid=0.45, branch_l=0.55, branch_r=0.55)


class Logo:
    """The logo as light (or paint) in the 3D world: it forms, glows, holds and leaves.

    Placing (see Place): pos, size (its height in metres), facing, face, tilt, roll, ride, frac, keys; or
    place=<a Place>. camera: the song's Rig, needed for face="camera" or "screen", ride and the keys that use them.

    Times: t_in (the first light appears), t_full (whole), t_out (it starts to leave; None: never),
    leave_dur (seconds).
    arrive   "build" (default): the brand build. The two hearts sweep in from either side and from behind,
             the globe's ring draws round and its disc fills from the middle, the grid lines draw
             themselves, the olive branches grow from the stem's foot and each leaf opens. BUILD holds
             the timing of each part (shares of t_in..t_full); `timing=dict(part=(start, end))` changes it.
             "gather": every point flies in from a loose cloud round it, the hearts first. "fade". "none"
    leave    "fade", "rise" (it lifts apart into sparks from the top), "scatter" (it bursts outward), "none"
    paint    0 (default): the logo is light (glows on a night sky; the colours are the brand colours on black);
             1: painted in its exact colours over whatever is behind it (a bright day sky) with a little of its
             own light (paint_light). A number or a function of t, so it can turn from light to paint.
    bright   brightness of the light (1.0: the exact colours on a black sky)
    white    how bright the white parts are against the coloured ones, in light (0.6; 1.0 = full white,
             which blooms over the colours)
    glow     a soft coloured halo of the logo's own light (0.35)
    sparkle  a few glints that twinkle on it (0.25)
    palette  "brand", "web", "poster" (see logo_rgba)
    parts    a list of the parts to show (default all, see PARTS)
    amount   dict part -> function t -> 0..1, to drive a part's progress yourself (it replaces the build)
    bulge    0..1: how much the globe's points bulge toward the viewer on their sphere (1.0)
    n        about how many points (70000; 40000 is enough for a logo under a third of the picture high)
    dof, fog how much of the lens blur and of the haze the settled logo takes (0: sharp and clear)
    """

    def __init__(self, pos=(0.0, 3.0, 0.0), size=2.0, facing=0.0, face="fixed", tilt=0.0, roll=0.0, ride=None,
                 frac=0.2, keys=None, place=None, camera=None, t_in=0.0, t_full=3.0, t_out=None, leave_dur=1.6,
                 arrive="build", leave="fade", paint=0.0, paint_light=0.04, bright=0.45, white=0.35, glow=0.25,
                 sparkle=0.08, palette="brand", parts=None, amount=None, timing=None, bulge=1.0, n=70000,
                 dot=2.1, dof=0.0, fog=0.0, reflect=True, seed=7):
        self.place = place or Place(pos=pos, size=size, facing=facing, face=face, tilt=tilt, roll=roll, ride=ride,
                                    frac=frac, keys=keys)
        self.camera = camera
        self.wants_camera = True
        self.t_in, self.t_full, self.t_out = float(t_in), float(t_full), t_out
        self.leave_dur = float(leave_dur)
        self.arrive, self.leave = arrive, leave
        self.paint, self.paint_light = paint, float(paint_light)
        self.bright, self.white, self.glow, self.sparkle = float(bright), float(white), float(glow), float(sparkle)
        self.amount = amount or {}
        self.timing = dict(BUILD, **(timing or {}))
        self.bulge, self.dot = float(bulge), float(dot)
        self.dof, self.fog, self.reflect = dof, fog, reflect
        P = logo_points(n, seed, palette)
        keep = np.ones(len(P["x"]), bool) if parts is None else np.isin(P["part"], [_PID[p] for p in parts])
        self.x, self.y, self.z = P["x"][keep], P["y"][keep], P["z"][keep]
        self.part, self.wt, self.order = P["part"][keep], P["weight"][keep], P["order"][keep]
        self.cov, self.elem = P["covered"][keep].copy(), P["elem"][keep]
        self.inner = P["inner"][keep]
        self.mask_l = P["mask_l"]
        self.rgb = P["rgb"][keep]
        self.cell = P["cell"]
        self.N = len(self.x)
        self.is_r = self.part == _PID["heart_r"]
        self.cov[self.is_r, _PID["heart_l"]] = 0.0           # the left heart covers the right one as it moves
        # light: the brand colours as light on black, a little deeper so that the sky and the bloom that add to
        # them do not pale them (light can only brighten what is behind it)
        # the parting line: a share of white over the left heart's own colour, shown once the right heart is there
        self.gapw = P["gapw"][keep]
        self.gap = self.gapw > 0.01
        rgb0 = self.rgb.copy()
        g = self.gapw[self.gap, None]
        rgb0[self.gap] = np.clip((self.rgb[self.gap] - g) / np.maximum(1.0 - g, 0.05), 0.0, 1.0)
        rgb0[self.gap & (self.gapw > 0.9)] = _hex_rgb(LOGO_PALETTES[palette]["orange"] if isinstance(palette, str)
                                                      else LOGO_COLORS["orange"])
        self.rgb0 = rgb0
        lc = show_rgb(rgb0)
        m = np.maximum(lc.max(axis=1, keepdims=True), 1e-6)
        self.light0 = (m * (lc / m) ** 1.15).astype(np.float32)
        self.isw = isw = (rgb0.min(axis=1) > 0.97)
        self.white_light = np.array([1.0, 0.96, 0.9], np.float32) * 2.0 * self.white
        self.white_paint = np.array([1.25, 1.25, 1.25], np.float32)      # displays close to white, blooms little
        self.light0[isw] = self.white_light
        self.paint0 = show_rgb(rgb0).astype(np.float32)
        self.paint0[isw] = self.white_paint
        rng = np.random.default_rng(seed + 101)
        self.s = rng.random((self.N, 4)).astype(np.float32)
        self.k_norm = 1.0 / (0.304 * self.dot * self.dot)
        self.i_halo = np.nonzero((self.s[:, 0] < 0.035) & ~isw)[0]          # the coloured parts glow, not the white
        self.i_spark = np.nonzero(self.s[:, 1] < 0.0012)[0]
        self.inside_l = 1.0 - self.gapw                     # how much of a left heart point is the heart itself
        # a loose cloud the points gather from (logo units): round the logo, more behind and below
        d = rng.normal(size=(self.N, 3))
        d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
        rad = 0.7 + 0.9 * rng.random(self.N) ** 0.5
        self.cloud = (d * rad[:, None] * np.array([1.4, 0.9, 1.0]) + np.array([0.0, -0.2, -0.6])).astype(np.float32)

    # ------------------------------------------------------------------ progress
    def progress(self, part, t):
        """0..1: how far a part has arrived at t (its own clock inside the arrival)."""
        if part in self.amount:
            return float(np.clip(self.amount[part](t), 0.0, 1.0))
        if self.arrive == "none":
            return 1.0
        span = max(self.t_full - self.t_in, 1e-6)
        u = (t - self.t_in) / span
        if self.arrive == "build":
            a, b = self.timing[part]
            return float(np.clip((u - a) / max(b - a, 1e-6), 0.0, 1.0))
        return float(np.clip(u, 0.0, 1.0))

    def _leave(self, t):
        if self.t_out is None or self.leave == "none":
            return 0.0
        return float(np.clip((t - float(self.t_out)) / max(self.leave_dur, 1e-6), 0.0, 1.0))

    def gain(self, t):
        if t < self.t_in - 0.05:
            return 0.0
        if self.t_out is not None and t > float(self.t_out) + self.leave_dur + 0.05:
            return 0.0
        return 1.0

    def local(self, t):
        """Positions (logo units, before placing), alpha, flash and per-part presence at t."""
        x, y, z = self.x.astype(np.float64).copy(), self.y.astype(np.float64).copy(), self.z * self.bulge
        z = z.astype(np.float64)
        alpha = np.ones(self.N)
        flash = np.zeros(self.N)
        pres = np.zeros(len(PARTS))
        off_l = np.zeros(2)
        a_l = 1.0
        for pi, name in enumerate(PARTS):
            sel = self.part == pi
            if not sel.any():
                continue
            g = self.progress(name, t)
            if self.arrive == "build" or name in self.amount:
                if name in ("heart_l", "heart_r"):
                    e = 1.0 - (1.0 - g) ** 3
                    sgn = -1.0 if name == "heart_l" else 1.0
                    dx, dy = sgn * (1.0 - e) * 0.85, -(1.0 - e) * 0.10
                    x[sel] += dx
                    y[sel] += dy
                    z[sel] -= (1.0 - e) * 0.55
                    a = _ss(0.0, 0.45, g)
                    alpha[sel] = a
                    flash[sel] = 0.0
                    pres[pi] = float(a)
                    if name == "heart_l":
                        off_l, a_l = np.array([dx, dy]), float(a)
                else:
                    o = self.order[sel]
                    age = g * 1.08 - o
                    alpha[sel] = np.clip(age / 0.07, 0.0, 1.0)
                    fk = 0.0 if name == "globe" else (0.5 if name == "ring" else 1.0)
                    flash[sel] = fk * np.where(g < 1.0, np.exp(-np.maximum(age, 0.0) / 0.05) * (age > 0), 0.0)
                    pres[pi] = g
            elif self.arrive == "gather":
                u0 = GATHER_ORDER[name]
                span = max(self.t_full - self.t_in, 1e-6)
                fly = 0.55
                delay = u0 + (1.0 - fly - u0) * 0.35 * self.s[sel, 2]
                uu = np.clip(((t - self.t_in) / span - delay) / fly, 0.0, 1.0)
                e = 1.0 - (1.0 - uu) ** 3
                c = self.cloud[sel]
                sw = np.sin(np.pi * e) * 0.25
                x[sel] = c[:, 0] * (1 - e) + x[sel] * e - sw * c[:, 2]
                y[sel] = c[:, 1] * (1 - e) + y[sel] * e
                z[sel] = c[:, 2] * (1 - e) + z[sel] * e + sw * c[:, 0]
                alpha[sel] = _ss(0.0, 0.3, uu)
                flash[sel] = np.exp(-np.abs(uu - 1.0) / 0.04) * (uu > 0.9) * 0.6
                pres[pi] = float(_ss(0.85, 1.0, float(np.clip(((t - self.t_in) / span - u0) / (1 - u0), 0, 1))))
            else:
                g2 = _sc(0.0, 1.0, g)
                alpha[sel] = g2
                pres[pi] = g2
        # the white parting line shows only over the right heart, once it is in place
        self.sg = sg = pres[_PID["heart_r"]] * _sc(0.75, 1.0, self.progress("heart_r", t))
        alpha[self.gap] *= self.inside_l[self.gap] + self.gapw[self.gap] * sg
        # the hearts' inner lobes go as the globe arrives over them
        alpha *= 1.0 - self.inner * max(pres[_PID["globe"]], pres[_PID["ring"]])
        # what of the right heart the left heart covers where it is now (light only; paint covers by order)
        self.dyn = np.ones(self.N)
        if self.is_r.any() and a_l > 0.0:
            m, x0, y1, k = self.mask_l
            col = ((x[self.is_r] - off_l[0] - x0) * k).astype(np.int64)
            row = ((y1 - (y[self.is_r] - off_l[1])) * k).astype(np.int64)
            ok = (col >= 0) & (col < m.shape[1]) & (row >= 0) & (row < m.shape[0])
            cvr = np.zeros(len(col))
            cvr[ok] = m[row[ok], col[ok]]
            self.dyn[self.is_r] = 1.0 - cvr * a_l
        lv = self._leave(t)
        if lv > 0.0:
            if self.leave == "fade":
                alpha *= 1.0 - _sc(0.0, 1.0, lv)
            elif self.leave == "rise":
                k = np.clip(lv * 1.6 - (0.5 - y) * 0.6 - 0.3 * self.s[:, 3], 0.0, 1.0)
                y += k * k * (0.9 + 0.8 * self.s[:, 0])
                x += k * k * (self.s[:, 1] - 0.5) * 0.6
                z += k * (self.s[:, 2] - 0.5) * 0.4
                alpha *= np.clip(1.0 - k * 1.1, 0.0, 1.0)
                flash += 0.3 * k * (1 - k) * 4.0 * (self.s[:, 2] < 0.25)
            elif self.leave == "scatter":
                k = _ss(0.0, 1.0, lv)
                d = np.stack([x, y, z + 0.3], axis=1)
                d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
                sp = (0.6 + 1.2 * self.s[:, 0])[:, None] * k
                x, y, z = x + d[:, 0] * sp[:, 0], y + d[:, 1] * sp[:, 0], z + d[:, 2] * sp[:, 0]
                alpha *= 1.0 - k
        return x, y, z, alpha, flash, pres

    def sample(self, t, cam=None):
        if self.gain(t) <= 0.0:
            return None
        if cam is None:
            cam = _cam_of(self.camera, t)
        x, y, z, alpha, flash, pres = self.local(t)
        c, r, u, nrm, s = self.place.frame(t, cam)
        pos = (c[None, :] + s * (x[:, None] * r[None, :] + y[:, None] * u[None, :] + z[:, None] * nrm[None, :]))
        pos = pos.astype(np.float32)
        size = np.float32(self.cell * self.dot * s)
        paint = float(np.clip(_val(self.paint, t), 0.0, 1.0))
        out = []
        sharp = dict(dof=self.dof, fog=self.fog, streak=0.3, reflect=self.reflect)
        # the parting line whitens as the right heart settles behind the left one
        light, paintc = self.light0, self.paint0
        if self.gap.any():
            k = (self.gapw[self.gap] * self.sg)[:, None]
            light = light.copy()
            paintc = paintc.copy()
            light[self.gap] = light[self.gap] * (1 - k) + self.white_light * k
            paintc[self.gap] = paintc[self.gap] * (1 - k) + self.white_paint * k
        # light: each point hidden by what covers it (the parts in front, once they are there)
        occ = np.prod(1.0 - self.cov * pres[None, :], axis=1) * self.dyn
        a_light = alpha * self.wt * occ
        vis = a_light > 0.004
        if vis.any() and paint < 0.999:
            out.append(dict(pos=pos[vis], size=size, color=light[vis] * self.bright,
                            alpha=(a_light[vis] * self.k_norm).astype(np.float32),
                            emit=(1.0 + 2.5 * flash[vis]).astype(np.float32), kind="soft", twinkle=0.0,
                            seed=self.s[vis, 0], paint=0.0, **sharp))
        if paint > 0.0:
            # a painted disc keeps its light in its skirt, so its middle covers only about two thirds: an alpha
            # of 2 (the renderer clamps the cover to 1) makes the fill solid
            a_p = alpha * np.clip(self.wt * 1.6, 0.0, 1.0) * 2.0
            vp = a_p > 0.004
            if vp.any():
                out.append(dict(pos=pos[vp], size=np.float32(self.cell * 1.75 * s), color=paintc[vp], alpha=a_p[vp].astype(np.float32),
                                kind="disc", paint=paint, paint_light=self.paint_light, seed=self.s[vp, 0],
                                **dict(sharp, streak=0.0)))
        if self.glow > 0.0:
            i = self.i_halo
            a = a_light[i] * self.glow * 0.033 * (1.0 - paint)
            sel = a > 0.0005
            if sel.any():
                out.append(dict(pos=pos[i][sel], size=size * 14.0, color=light[i][sel] * self.bright,
                                alpha=a[sel].astype(np.float32), kind="soft", seed=self.s[i][sel, 1], dof=1.0,
                                fog=self.fog, streak=0.0, reflect=self.reflect))
        if self.sparkle > 0.0:
            i = self.i_spark
            a = alpha[i] * occ[i] * self.sparkle * (0.6 + flash[i]) * (1.0 - paint)
            sel = a > 0.01
            if sel.any():
                out.append(dict(pos=pos[i][sel], size=size * 3.0, color=np.array([1.0, 0.93, 0.8]) * 1.4,
                                alpha=a[sel].astype(np.float32), emit=2.0, kind="spark", twinkle=1.0,
                                seed=self.s[i][sel, 2], **sharp))
        # the head of a line that is drawing itself: a small bright spark
        hd = flash > 0.35
        if hd.any():
            j = np.nonzero(hd)[0][:: max(int(hd.sum() // 90), 1)]
            out.append(dict(pos=pos[j], size=size * 4.0, color=np.array([1.0, 0.95, 0.85]),
                            alpha=(0.5 * flash[j]).astype(np.float32), emit=3.0, kind="spark", twinkle=0.6,
                            seed=self.s[j, 3], **sharp))
        return out

    def where(self, t, cam=None, part=None):
        """World positions of the logo's points (all, or one part) where they are at t."""
        if cam is None:
            cam = _cam_of(self.camera, t)
        x, y, z, *_ = self.local(t)
        sel = np.ones(self.N, bool) if part is None else self.part == _PID[part]
        return self.place.world(t, x[sel], y[sel], z[sel], cam)

    def home(self, part=None):
        """The settled places of the points in logo units (x, y, z), all or one part."""
        sel = np.ones(self.N, bool) if part is None else self.part == _PID[part]
        return self.x[sel], self.y[sel], self.z[sel] * self.bulge


# ---------------------------------------------------------------------------------- the rest of the brand
from .brand_hearts import HeartDrift, HeartForm, Hearts, arrange_heart, heart_places, heart_points  # noqa: E402,F401
from .brand_symbols import (RECIPES, SYMBOLS, Constellation, Flock, LightTrail, PetalShape, Ripples, Traced,  # noqa: E402,F401
                            recipe, strokes, symbol_image, symbol_points)
from .brand_world import LAS_VEGAS, LOOK_COLORS, PASTEL, Finale, Globe, land  # noqa: E402,F401
