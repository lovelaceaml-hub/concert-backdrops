"""Artistic faces in profile, and long hair as a flowing mass (engine/p3d). Pure numpy.

Anthony allows artistic faces (never photorealistic): a profile edge with brow, nose, lips, chin and closed
eyes, made of sparks, glitter, stars or cloud (refs p06, p07). The MakeHuman body of engine/p3d/body.py has its
face smoothed to a mannequin on purpose and is too coarse for a 1080p close-up, so the faces here are drawn:

  ProfileShape   the geometry: a hand drawn profile curve (forehead, brow, nose, lips, chin, throat, neck,
                 the back of the skull and the shoulders) turned into a solid by giving every height a rounded
                 cross section, plus the lines of the features (closed eye with lashes, brow, the parting of
                 the lips, nostril, ear, jaw, a neckline). Own geometry, written for this engine; no third
                 party asset (see assets/p3d/README.md, "Profile faces").
  Profile        a point set: the head and shoulders in a look ("sparks", "glitter", "constellation",
                 "rim", "ink", "fill"), breathing, turning and lifting the chin over time.
  Hair           long hair as a mass of flowing locks for a Profile or a Body (refs p02, p04, p05): a few
                 hundred strands in locks that stream with the wind and wave, pure functions of time.

Units of the drawing are head heights (chin to crown = 1), u toward the face, v up, w to the side. A Profile
is placed by `at` (the middle of the head, between the ears, at eye height) and `height` (metres from chin to
crown; 0.23 is life size, a few metres a giant head in the sky). Faces are for ordinary people only:
Heavenly Mother is never shown with a face (only from behind or as hands).
"""
import numpy as np

from . import bodymath as bm
from .api import hash01, lin

# ----------------------------------------------------------------------------------------------- the drawing
# Control points of the outline, (u, v) in head heights, the chin's lowest point at v = 0. One closed curve,
# from the bottom of the chest up the throat, over the face and the crown, down the back to the bottom.
_FRONT = {
    "woman": [
        (0.40, -0.88), (0.37, -0.70), (0.30, -0.54), (0.205, -0.42), (0.135, -0.31), (0.115, -0.19),
        (0.120, -0.090), (0.165, -0.032), (0.245, -0.006), (0.300, 0.006), (0.333, 0.040), (0.341, 0.088),
        (0.327, 0.126), (0.350, 0.160), (0.368, 0.184), (0.353, 0.204), (0.376, 0.228), (0.374, 0.258),
        (0.354, 0.287), (0.370, 0.300), (0.410, 0.311), (0.433, 0.336), (0.424, 0.372), (0.398, 0.425),
        (0.369, 0.484), (0.346, 0.546), (0.356, 0.596), (0.352, 0.660), (0.330, 0.750), (0.290, 0.838),
        (0.220, 0.922), (0.115, 0.980), (-0.010, 1.000),
    ],
    "man": [
        (0.44, -0.88), (0.41, -0.70), (0.33, -0.53), (0.23, -0.41), (0.160, -0.30), (0.140, -0.19),
        (0.145, -0.095), (0.185, -0.040), (0.265, -0.010), (0.322, 0.002), (0.357, 0.035), (0.364, 0.085),
        (0.344, 0.124), (0.364, 0.158), (0.377, 0.184), (0.362, 0.205), (0.381, 0.229), (0.379, 0.262),
        (0.358, 0.290), (0.377, 0.301), (0.426, 0.313), (0.450, 0.341), (0.438, 0.385), (0.404, 0.438),
        (0.372, 0.494), (0.351, 0.548), (0.373, 0.597), (0.367, 0.660), (0.345, 0.752), (0.303, 0.842),
        (0.230, 0.926), (0.120, 0.982), (-0.010, 1.000),
    ],
}
_BACK = {
    "woman": [
        (-0.150, 0.994), (-0.285, 0.950), (-0.400, 0.862), (-0.475, 0.738), (-0.498, 0.600), (-0.482, 0.470),
        (-0.425, 0.360), (-0.335, 0.262), (-0.262, 0.172), (-0.228, 0.060), (-0.232, -0.070), (-0.275, -0.200),
        (-0.375, -0.330), (-0.480, -0.480), (-0.540, -0.680), (-0.555, -0.880),
    ],
    "man": [
        (-0.150, 0.994), (-0.292, 0.950), (-0.412, 0.860), (-0.488, 0.735), (-0.510, 0.598), (-0.492, 0.466),
        (-0.438, 0.352), (-0.350, 0.252), (-0.282, 0.160), (-0.258, 0.050), (-0.266, -0.080), (-0.315, -0.205),
        (-0.425, -0.325), (-0.535, -0.470), (-0.600, -0.670), (-0.620, -0.880),
    ],
}
# lines of the features: (u, v) polylines on the near side of the head. A closed eye seen from the side is
# the curve where the lids meet (with its lashes) and the crease of the upper lid above it.
_FEATURES = {
    "woman": dict(
        eye=[(0.318, 0.497), (0.300, 0.489), (0.276, 0.486), (0.252, 0.491), (0.236, 0.500)],
        lid=[(0.312, 0.512), (0.292, 0.526), (0.266, 0.529), (0.244, 0.520)],
        brow=[(0.338, 0.588), (0.312, 0.606), (0.278, 0.614), (0.240, 0.610), (0.205, 0.598)],
        lips=[(0.355, 0.205), (0.338, 0.203), (0.318, 0.199), (0.300, 0.192)],
        nostril=[(0.393, 0.320), (0.374, 0.327), (0.360, 0.342), (0.357, 0.360)],
        ear=[(-0.080, 0.548), (-0.112, 0.566), (-0.150, 0.552), (-0.170, 0.505), (-0.168, 0.440),
             (-0.150, 0.385), (-0.118, 0.348), (-0.090, 0.344)],
        jaw=[(-0.090, 0.320), (-0.040, 0.210), (0.050, 0.100), (0.160, 0.032), (0.260, 0.008)],
    ),
}
_FEATURES["man"] = {k: [(u + 0.010 * (u > 0.2), v) for u, v in line] for k, line in _FEATURES["woman"].items()}
# lashes: (u, v) roots along the eye line, each a short stroke forward and down
_LASHES = [(0.312, 0.494), (0.302, 0.490), (0.291, 0.487), (0.280, 0.486), (0.269, 0.487), (0.258, 0.489),
           (0.248, 0.493)]
# the neckline of the garment: (u, v) at the front, the side and the back (the garment covers below it)
_NECKLINE = dict(woman=((0.25, -0.50), (0.02, -0.40), (-0.22, -0.33), (-0.40, -0.36)),
                 man=((0.22, -0.42), (0.00, -0.32), (-0.26, -0.26), (-0.44, -0.30)))
# half width of the head and body at height v (head heights): skull, jaw, neck, shoulders
_WIDTH = {
    "woman": [(-0.88, 0.95), (-0.55, 0.90), (-0.38, 0.66), (-0.26, 0.30), (-0.10, 0.23), (0.05, 0.25),
              (0.20, 0.28), (0.45, 0.33), (0.70, 0.34), (0.90, 0.28), (1.00, 0.10)],
    "man": [(-0.88, 1.05), (-0.55, 1.00), (-0.38, 0.74), (-0.26, 0.34), (-0.10, 0.27), (0.05, 0.29),
            (0.20, 0.31), (0.45, 0.35), (0.70, 0.36), (0.90, 0.29), (1.00, 0.10)],
}
EYE_LEVEL = 0.50          # v of the eyes: the place `at` names is (U_CENTRE, EYE_LEVEL, 0)
U_CENTRE = -0.08


def _catmull(pts, n_per, closed=False):
    """A Catmull-Rom curve through the points (centripetal enough for these gentle drawings)."""
    p = np.asarray(pts, np.float64)
    if closed:
        p = np.concatenate([p[-1:], p, p[:2]])
    else:
        p = np.concatenate([p[:1] * 2 - p[1:2], p, p[-1:] * 2 - p[-2:-1]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        s = np.linspace(0.0, 1.0, n_per, endpoint=False)[:, None]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    if not closed:
        out.append(p[-2:-1])
    return np.concatenate(out)


def _resample(line, step):
    """Even spacing along a polyline (closed or not as given)."""
    d = np.linalg.norm(np.diff(line, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(d)])
    m = max(int(s[-1] / step), 2)
    q = np.linspace(0.0, s[-1], m)
    return np.stack([np.interp(q, s, line[:, k]) for k in range(line.shape[1])], axis=1), s[-1]


class ProfileShape:
    """The drawn profile of a "woman" or a "man" (head heights). outline: the closed curve, evenly spaced;
    features: dict of feature lines; half_width(u, v): the solid's half thickness (0 outside)."""

    def __init__(self, shape="woman"):
        if shape not in _FRONT:
            raise ValueError("a profile is a 'woman' or a 'man', got %r" % (shape,))
        self.shape = shape
        ctrl = _FRONT[shape] + _BACK[shape]
        self.ctrl = ctrl
        # the bottom edge (the bust is cut there and fades) closes the curve
        line = _catmull(ctrl, 14, closed=True)
        self.outline, self.length = _resample(line, 0.0025)
        self.features = {k: _resample(_catmull(v, 10), 0.002)[0] for k, v in _FEATURES[shape].items()}
        nl = _NECKLINE[shape]
        self.neckline = _resample(_catmull(list(nl), 12), 0.003)[0]
        self.width = np.asarray(_WIDTH[shape], np.float64)
        # the front and back of the outline at each height (for the cross sections)
        vv = np.linspace(-0.88, 1.0, 600)
        o = self.outline
        fr, bk = np.full(len(vv), np.nan), np.full(len(vv), np.nan)
        for i, v in enumerate(vv):
            a, b = o[:, 1], np.roll(o[:, 1], -1)
            cross = ((a - v) * (b - v) <= 0) & (a != b)
            if not cross.any():
                continue
            j = np.flatnonzero(cross)
            f = (v - a[j]) / (b[j] - a[j])
            us = o[j, 0] + f * (np.roll(o[:, 0], -1)[j] - o[j, 0])
            fr[i], bk[i] = us.max(), us.min()
        ok = ~np.isnan(fr)
        self._vv, self._fr, self._bk = vv[ok], fr[ok], bk[ok]

    def span(self, v):
        """(front u, back u) of the outline at heights v."""
        return np.interp(v, self._vv, self._fr), np.interp(v, self._vv, self._bk)

    def half_width(self, u, v):
        """Half thickness of the solid at (u, v): an elliptical cross section, sharper toward the face."""
        fr, bk = self.span(v)
        uc, hl = 0.5 * (fr + bk), np.maximum(0.5 * (fr - bk), 1e-4)
        x = np.clip((u - uc) / hl, -1.0, 1.0)
        wmax = np.interp(v, self.width[:, 0], self.width[:, 1])
        # the face is narrower than the skull behind it: the section leans its widest point backward
        x = np.where(x > 0, x * (1.0 + 0.25 * (v > -0.05) * (v < 0.80)), x)
        inside = 1.0 - np.minimum(x * x, 1.0)
        return wmax * np.sqrt(inside) * ((u <= fr + 1e-6) & (u >= bk - 1e-6))

    def inside(self, u, v):
        """True where (u, v) lies inside the outline (looked up in a fine raster of the drawing)."""
        if not hasattr(self, "_raster"):
            from PIL import Image, ImageDraw
            o = self.outline
            lo, hi = o.min(axis=0) - 0.01, o.max(axis=0) + 0.01
            k = 1600.0 / float((hi - lo).max())
            size = (int((hi[0] - lo[0]) * k) + 2, int((hi[1] - lo[1]) * k) + 2)
            im = Image.new("L", size, 0)
            ImageDraw.Draw(im).polygon([((x - lo[0]) * k, (y - lo[1]) * k) for x, y in o], fill=255)
            self._raster = (np.asarray(im) > 127, lo, k)
        r, lo, k = self._raster
        i = np.clip(((np.asarray(v) - lo[1]) * k).astype(np.int64), 0, r.shape[0] - 1)
        j = np.clip(((np.asarray(u) - lo[0]) * k).astype(np.int64), 0, r.shape[1] - 1)
        return r[i, j]

    def _grad(self, u, v, e=0.002):
        gu = (self.half_width(u + e, v) - self.half_width(u - e, v)) / (2 * e)
        gv = (self.half_width(u, v + e) - self.half_width(u, v - e)) / (2 * e)
        return gu, gv

    def surface(self, n, seed=0, cut=-0.86):
        """n points on the solid's surface (both sides): (u, v, w) and unit normals, denser where the surface
        turns away (toward the silhouette edge)."""
        rs = np.random.default_rng(1000 + seed)
        lo = self.outline.min(axis=0)
        hi = self.outline.max(axis=0)
        out_p, out_n = [], []
        got = 0
        while got < n:
            m = n * 3
            u = rs.uniform(lo[0], hi[0], m)
            v = rs.uniform(max(lo[1], cut), hi[1], m)
            ok = self.inside(u, v)
            u, v = u[ok], v[ok]
            gu, gv = self._grad(u, v)
            slope = np.sqrt(1.0 + gu * gu + gv * gv)
            keep = rs.uniform(0, 1, len(u)) < np.minimum(slope / 4.0, 1.0)
            u, v, gu, gv = u[keep], v[keep], gu[keep], gv[keep]
            side = np.where(rs.uniform(0, 1, len(u)) < 0.5, -1.0, 1.0)
            w = side * self.half_width(u, v)
            nrm = np.stack([-gu, -gv, side], axis=1)
            nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
            out_p.append(np.stack([u, v, w], axis=1))
            out_n.append(nrm)
            got += len(u)
        return np.concatenate(out_p)[:n], np.concatenate(out_n)[:n]

    def on_surface(self, uv, side):
        """(u, v) places on the near (side +1) or far (-1) surface: (u, v, w) and normals."""
        uv = np.asarray(uv, np.float64)
        u, v = uv[:, 0], uv[:, 1]
        gu, gv = self._grad(u, v)
        nrm = np.stack([-gu, -gv, np.full(len(u), float(side))], axis=1)
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
        return np.stack([u, v, self.half_width(u, v) * side], axis=1), nrm

    def edge(self, cut=-0.80):
        """The outline as (u, v, 0) points with their outward normals in the drawing's plane (the bottom cut
        of the bust left out)."""
        o = self.outline
        d = np.roll(o, -1, axis=0) - np.roll(o, 1, axis=0)
        nr = np.stack([d[:, 1], -d[:, 0]], axis=1)
        nr /= np.maximum(np.linalg.norm(nr, axis=1, keepdims=True), 1e-9)
        test = o + nr * 0.01
        if self.inside(test[:, 0], test[:, 1]).mean() > 0.5:
            nr = -nr
        keep = o[:, 1] > cut
        p = np.concatenate([o[keep], np.zeros((keep.sum(), 1))], axis=1)
        n = np.concatenate([nr[keep], np.zeros((keep.sum(), 1))], axis=1)
        return p, n


# ----------------------------------------------------------------------------------------------- helpers
def _val(v, t):
    if v is None:
        return None
    return v(t) if callable(v) else v


def _col(c):
    return lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


def _smooth(a, b, x):
    return bm.smooth((np.asarray(x, np.float64) - a) / (b - a))


def _basis(facing):
    f = np.radians(facing)
    F = np.array([np.sin(f), 0.0, np.cos(f)])
    U = np.array([0.0, 1.0, 0.0])
    L = np.array([np.cos(f), 0.0, -np.sin(f)])
    return F, U, L


class HeadFrame:
    """Where a head is at t: origin (the middle of the head at eye level), basis F (forward), U (up), L (its
    left), and H (metres from chin to crown). world() and dirs() turn head units (u, v, w) into the world."""

    def __init__(self, origin, F, U, L, H):
        self.origin, self.F, self.U, self.L, self.H = origin, F, U, L, H

    def world(self, p):
        p = np.asarray(p, np.float64)
        x = (p[:, 0] - U_CENTRE) * self.H
        y = (p[:, 1] - EYE_LEVEL) * self.H
        z = p[:, 2] * self.H
        return self.origin[None] + x[:, None] * self.F[None] + y[:, None] * self.U[None] + z[:, None] * self.L[None]

    def dirs(self, n):
        n = np.asarray(n, np.float64)
        return n[:, :1] * self.F[None] + n[:, 1:2] * self.U[None] + n[:, 2:3] * self.L[None]


# ----------------------------------------------------------------------------------------------- the profile
PROFILE_LOOKS = ("sparks", "glitter", "constellation", "rim", "ink", "fill")


class Profile:
    """A head and shoulders in profile, drawn (not photographed), made of light. A point set for the 3D layer.

    shape     "woman" or "man"
    at        the middle of the head at eye level (x, y, z), or a function of time
    facing    degrees the face looks toward (0: +z, 90: +x), a number or a function of time
    height    metres from chin to crown (0.23 life size; a giant head in the sky: 3 to 8)
    tilt      degrees the chin lifts (looking up; negative bows the head); a number or a function of time.
              Only the head and neck move; the shoulders stay
    turn      degrees the head turns toward its own left; a number or a function of time
    look      "sparks" (p06: the edge traced by fine sparks, embers streaming off the top, the inside dark),
              "glitter" (gold glitter skin, the features in brighter grains), "constellation" (stars joined by
              lines, the features drawn as small constellations), "rim" (a thin bright edge), "ink" (only a fine
              edge of light: give it a dark Mask, see shape_set()), "fill" (a faint edge and features over a
              window fill such as a nebula); or a list of them; each may be a dict(name=..., bright, size,
              features)
    color, color2   the main light and the highlight (display hex)
    features  0..1: how clearly the closed eye with its lashes, brow, lips, nostril, ear and jaw are drawn
    garment   True: a neckline of light; below it the shoulders are clothed (everyone is clothed)
    hair      True or dict(...) of Hair keys: long hair as a flowing mass; False: none
    stream    for "sparks" and "glitter": dict(n=2600, rate=1.0, dir=(0.25, 1.0), speed=0.35, life=3.2,
              where=(0.55, 1.0), size=1.0, spread=0.10): embers leaving the top of the head; False for none
    eye_glow  0..1: a small warm star at the closed eye (p06); 0 none
    bright, size, points   brightness, grain size multiplier, how many surface points (20 to 120 thousand)
    show, fade (t_in, t_out) and seconds of fade; breathe: 0..1, the shoulders rise and fall; seed

    Seen best within about 35 degrees of side on (it is a drawing given depth, not a sculpted head).
    """
    wants_camera = True

    def __init__(self, shape="woman", at=(0.0, 1.6, 0.0), facing=90.0, height=0.23, tilt=0.0, turn=0.0,
                 look="sparks", color="#ff9a3c", color2="#ffe2b0", bright=1.0, size=1.0, points=50000,
                 features=1.0, garment=True, hair=True, stream=None, eye_glow=0.0, show=None, fade=0.6,
                 breathe=1.0, seed=1.0):
        self.g = ProfileShape(shape)
        self.shape = shape
        self.at, self.facing, self.height = at, facing, height
        self.tilt, self.turn = tilt, turn
        looks = look if isinstance(look, (list, tuple)) else [look]
        self.looks = [dict(name=lk) if isinstance(lk, str) else dict(lk) for lk in looks]
        for lk in self.looks:
            if lk.get("name") not in PROFILE_LOOKS:
                raise ValueError("a Profile look is one of %s, got %r" % (PROFILE_LOOKS, lk.get("name")))
        self.color, self.color2 = _col(color), _col(color2)
        self.bright, self.size = float(bright), float(size)
        self.features = float(features)
        self.show = None if show is None else (float(show[0]), float(show[1]))
        self.fade = float(fade)
        self.breathe = float(breathe)
        self.seed = float(seed)
        sd = int(seed * 1000) % 100000
        g = self.g
        # ---- the points, once, in head units
        self.sp, self.sn = g.surface(int(points), seed=sd)
        self.ep, self.en = g.edge()
        fl_p, fl_n, fl_w = [], [], []
        weight = dict(eye=1.0, lid=0.5, brow=0.55, lips=0.9, nostril=0.55, ear=0.40, jaw=0.18)
        for name, line in g.features.items():
            for side in (1.0, -1.0):
                p, n = g.on_surface(line, side)
                fl_p.append(p)
                fl_n.append(n)
                fl_w.append(np.full(len(p), weight.get(name, 0.5)))
        lash = []
        for k, (u0, v0) in enumerate(_LASHES):
            s_ = np.linspace(0.0, 1.0, 9)
            ln = 0.022 + 0.010 * np.sin(k * 1.7) ** 2
            lash.append(np.stack([u0 + ln * (0.55 * s_ + 0.25 * s_ * s_), v0 - ln * (0.75 * s_ - 0.35 * s_ * s_)],
                                 axis=1))
        lash = np.concatenate(lash)
        for side in (1.0, -1.0):
            p, n = g.on_surface(lash, side)
            p[:, 2] += 0.006 * side
            fl_p.append(p)
            fl_n.append(n)
            fl_w.append(np.full(len(p), 0.8))
        if garment:
            for side in (1.0, -1.0):
                p, n = g.on_surface(g.neckline, side)
                fl_p.append(p)
                fl_n.append(n)
                fl_w.append(np.full(len(p), 0.7))
        self.fp, self.fn, self.fw = np.concatenate(fl_p), np.concatenate(fl_n), np.concatenate(fl_w)
        self.garment = bool(garment)
        nl = g.neckline
        o = np.argsort(nl[:, 0])
        lim = np.interp(self.sp[:, 0], nl[o, 0], nl[o, 1])
        self.cloth = (self.sp[:, 1] < lim) & bool(garment)
        self.seeds = hash01(len(self.sp), sd + 1)
        self.eseeds = hash01(len(self.ep), sd + 2)
        self.fseeds = hash01(len(self.fp), sd + 3)
        self.stream = None
        if stream is not False and any(lk["name"] in ("sparks", "glitter") for lk in self.looks):
            st = dict(n=2600, rate=1.0, dir=(0.25, 1.0), speed=0.35, life=3.2, where=(0.55, 1.0), size=1.0,
                      spread=0.10)
            st.update(stream or {})
            self.stream = st
        self.eye_glow = float(eye_glow)
        self._plex = None
        self.hair = None
        if hair:
            hk = dict(hair) if isinstance(hair, dict) else {}
            hk.setdefault("color", color)
            hk.setdefault("color2", color2)
            hk.setdefault("seed", seed)
            self.hair = Hair(self, **hk)

    # ------------------------------------------------------------------ pose
    def frame(self, t):
        """The head's frame at t (the shoulders' facing; the head's own tilt and turn are applied per point)."""
        F, U, L = _basis(float(_val(self.facing, t)))
        return HeadFrame(np.asarray(_val(self.at, t), np.float64), F, U, L, float(_val(self.height, t)))

    def pose(self, p, n, t):
        """Points (u, v, w) and normals in head units with the head lifted and turned and the chest breathing."""
        tl = np.radians(float(_val(self.tilt, t) or 0.0))
        tn = np.radians(float(_val(self.turn, t) or 0.0))
        p = np.array(p, np.float64)
        n = None if n is None else np.array(n, np.float64)
        a = _smooth(-0.22, 0.12, p[:, 1])
        piv = (U_CENTRE + 0.04, -0.06)
        if tl:
            ang = tl * a
            c, s_ = np.cos(ang), np.sin(ang)
            du, dv = p[:, 0] - piv[0], p[:, 1] - piv[1]
            p[:, 0], p[:, 1] = piv[0] + c * du - s_ * dv, piv[1] + s_ * du + c * dv
            if n is not None:
                nu, nv = n[:, 0].copy(), n[:, 1].copy()
                n[:, 0], n[:, 1] = c * nu - s_ * nv, s_ * nu + c * nv
        if tn:
            ang = tn * a
            c, s_ = np.cos(ang), np.sin(ang)
            du, dw = p[:, 0] - piv[0], p[:, 2].copy()
            p[:, 0], p[:, 2] = piv[0] + c * du - s_ * dw, s_ * du + c * dw
            if n is not None:
                nu, nw = n[:, 0].copy(), n[:, 2].copy()
                n[:, 0], n[:, 2] = c * nu - s_ * nw, s_ * nu + c * nw
        if self.breathe:
            b = self.breathe * (0.006 * np.sin(2 * np.pi * t / 4.6 + self.seed) + 0.002 * np.sin(2 * np.pi * t / 1.7))
            p[:, 1] += b * (1.0 - 0.6 * a)
        return p, n

    def where(self, t, name="eye"):
        """A place in the world: "eye", "nose", "lips", "chin", "forehead", "crown", "nape", "ear", "throat",
        "heart" (the middle of the chest), "head" (the middle of the head)."""
        uv = dict(eye=(0.29, 0.50), nose=(0.43, 0.34), lips=(0.37, 0.21), chin=(0.34, 0.05), forehead=(0.33, 0.78),
                  crown=(-0.02, 1.0), nape=(-0.26, 0.17), ear=(-0.12, 0.45), throat=(0.12, -0.15),
                  heart=(0.10, -0.62), head=(U_CENTRE, EYE_LEVEL))[name]
        p, _ = self.pose(np.array([[uv[0], uv[1], 0.0]]), None, t)
        return self.frame(t).world(p)[0]

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + self.fade)) * (
            1.0 - float(bm.ramp(t, self.show[1] - self.fade, self.show[1])))

    # ------------------------------------------------------------------ the point set
    def sample(self, t, cam=None):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        fr = self.frame(t)
        H = fr.H
        sp, sn = self.pose(self.sp, self.sn, t)
        pos = fr.world(sp)
        nrm = fr.dirs(sn)
        eye = None if cam is None else np.asarray(cam.pos, np.float64)

        def facing(p, n):
            if eye is None:
                return np.ones(len(p))
            vv = eye[None] - p
            vv /= np.maximum(np.linalg.norm(vv, axis=1, keepdims=True), 1e-9)
            return (n * vv).sum(1)

        vis = _smooth(-0.15, 0.20, facing(pos, nrm)) * _smooth(-0.86, -0.50, sp[:, 1])
        ep, en = self.pose(self.ep, self.en, t)
        epos, enrm = fr.world(ep), fr.dirs(en)
        fp, fn = self.pose(self.fp, self.fn, t)
        fpos, fnrm = fr.world(fp), fr.dirs(fn)
        fvis = _smooth(-0.05, 0.25, facing(fpos, fnrm))
        ebot = _smooth(-0.84, -0.45, ep[:, 1])
        ctx = dict(t=t, H=H, pos=pos, nrm=nrm, vis=vis, sp=sp, epos=epos, enrm=enrm, ep=ep, ebot=ebot, fpos=fpos,
                   fvis=fvis)
        out = []
        for lk in self.looks:
            out += getattr(self, "_look_" + lk["name"])(lk, ctx)
        if self.stream is not None:
            out += self._stream(t, fr, H)
        if self.eye_glow > 0.0:
            e = self.where(t, "eye")
            side = 1.0 if eye is None else (np.sign(np.dot(fr.L, eye - e)) or 1.0)
            e = e + fr.L * side * 0.27 * H
            out.append(dict(pos=e[None], size=0.035 * H, color=self.color * 0.5 + self.color2 * 0.5,
                            alpha=0.9 * self.eye_glow * self.bright, emit=5.0, kind="spark", twinkle=0.3))
            out.append(dict(pos=e[None], size=0.12 * H, color=self.color, alpha=0.30 * self.eye_glow * self.bright,
                            emit=1.0, kind="soft"))
        if self.hair is not None:
            out += self.hair.batches(t, cam)
        return out

    # ------------------------------------------------------------------ looks
    def _edge_weight(self, ep):
        """How bright the edge is along the outline: brightest down the face, softer over the skull and back."""
        u, v = ep[:, 0], ep[:, 1]
        face = _smooth(0.04, 0.20, u) * _smooth(-0.60, -0.25, v)
        top = _smooth(0.55, 0.85, v)
        return np.clip(np.maximum(face, np.maximum(0.75 * top, 0.35)), 0.0, 1.0)

    def _feat(self, lk, c, alpha, size, color, emit=1.0):
        fa = self.features * lk.get("features", 1.0)
        if fa <= 0.0:
            return []
        H = c["H"]
        return [dict(pos=c["fpos"], size=size * H * self.size * lk.get("size", 1.0), color=color,
                     alpha=alpha * self.bright * lk.get("bright", 1.0) * fa * self.fw * c["fvis"], emit=emit,
                     kind="soft", twinkle=0.3, seed=self.fseeds)]

    def _look_sparks(self, lk, c):
        b = self.bright * lk.get("bright", 1.0)
        sz = self.size * lk.get("size", 1.0)
        H, t = c["H"], c["t"]
        c1, c2 = self.color, self.color2
        epos, enrm = c["epos"], c["enrm"]
        w = self._edge_weight(c["ep"]) * c["ebot"]
        sd = self.eseeds
        mix = (sd ** 3)[:, None]
        col = c1[None] * (1 - mix) + c2[None] * mix
        out = [dict(pos=epos, size=(0.0030 + 0.0030 * sd ** 6) * H * sz, color=col, alpha=0.85 * b * w,
                    emit=1.0 + 2.5 * (sd > 0.97), kind="soft", twinkle=0.6, seed=sd)]
        # a dusting that frays outward from the edge (the line is crisp inside, soft outside)
        k = np.arange(len(epos) * 3) % len(epos)
        r = hash01(len(k), 77)
        r2 = hash01(len(k), 78)
        off = (r ** 2.2) * 0.045 * H
        tang = np.roll(epos, -1, axis=0) - np.roll(epos, 1, axis=0)
        tang /= np.maximum(np.linalg.norm(tang, axis=1, keepdims=True), 1e-9)
        drift = 0.010 * H * np.abs(np.sin(t * (0.6 + r2) + r * 40.0))
        p2 = epos[k] + enrm[k] * (off + drift * r)[:, None] + tang[k] * ((r2 - 0.5) * 0.004 * H)[:, None]
        out.append(dict(pos=p2, size=(0.0035 + 0.006 * r2 ** 5) * H * sz, color=c1 * 0.9 + c2 * 0.1,
                        alpha=0.55 * b * w[k] * (1.0 - r) ** 1.5, emit=1.0 + 3.0 * (r2 > 0.985), kind="soft",
                        twinkle=0.9, seed=r2))
        out += self._feat(lk, c, 0.55, 0.0028, c1 * 0.7 + c2 * 0.3)
        inner = self.seeds > 0.93
        out.append(dict(pos=c["pos"][inner], size=0.0030 * H * sz, color=c1 * 0.5 + c2 * 0.2,
                        alpha=0.06 * b * c["vis"][inner], kind="soft", twinkle=1.0, seed=self.seeds[inner]))
        return out

    def _look_rim(self, lk, c):
        b = self.bright * lk.get("bright", 1.0)
        sz = self.size * lk.get("size", 1.0)
        H = c["H"]
        sd = self.seeds
        col = self.color[None] * (1 - sd[:, None] * 0.5) + self.color2[None] * sd[:, None] * 0.5
        out = [dict(pos=c["pos"], normal=c["nrm"], size=(0.0026 + 0.003 * sd ** 4) * H * sz, color=col,
                    alpha=0.8 * b * c["vis"], kind="soft", rim=(1.0, lk.get("power", 4.0)), twinkle=0.5, seed=sd)]
        w = self._edge_weight(c["ep"]) * c["ebot"]
        out.append(dict(pos=c["epos"], size=0.0028 * H * sz, color=self.color2, alpha=0.6 * b * w, kind="soft",
                        twinkle=0.4, seed=self.eseeds))
        return out + self._feat(lk, c, 0.45, 0.0026, self.color)

    def _look_glitter(self, lk, c):
        b = self.bright * lk.get("bright", 1.0)
        sz = self.size * lk.get("size", 1.0)
        H = c["H"]
        c1, c2 = self.color, self.color2
        sd = self.seeds
        r2 = hash01(len(sd), 91)
        f = bm.flow(self.sp * 3.0, 0.0, speed=0.0, seed=self.seed)[:, 0] * 0.5 + 0.5
        mix = np.clip(0.6 * f + 0.4 * r2, 0, 1)[:, None]
        col = c1[None] * (1 - mix) + c2[None] * mix
        col[self.cloth] = col[self.cloth] * 0.8 + c2 * 0.2
        tone = np.where(hash01(len(sd), 92) < 0.25, 0.25, 0.8 + 0.4 * r2)
        glint = sd > 0.9975
        base = ~glint
        pos, nrm, vis = c["pos"], c["nrm"], c["vis"]
        out = [dict(pos=pos[base], normal=nrm[base], size=(0.0030 + 0.0060 * sd[base] ** 4) * H * sz,
                    color=col[base] * tone[base, None], alpha=0.40 * b * vis[base], kind="soft", twinkle=0.8,
                    rim=(0.45, 1.5), seed=sd[base]),
               dict(pos=pos[glint], size=0.006 * H * sz, color=c2, alpha=0.8 * b * vis[glint],
                    emit=2.0 + 2.0 * r2[glint], kind="spark", twinkle=1.0, seed=sd[glint])]
        w = self._edge_weight(c["ep"]) * c["ebot"]
        out.append(dict(pos=c["epos"], size=0.0032 * H * sz, color=c1 * 0.6 + c2 * 0.4, alpha=0.55 * b * w,
                        kind="soft", twinkle=0.7, seed=self.eseeds))
        return out + self._feat(lk, c, 0.75, 0.0030, c2, emit=1.2)

    def _look_constellation(self, lk, c):
        b = self.bright * lk.get("bright", 1.0)
        sz = self.size * lk.get("size", 1.0)
        H = c["H"]
        c1, c2 = self.color, self.color2
        share = lk.get("share", 0.035)
        if self._plex is None or self._plex[0] != share:
            from scipy.spatial import cKDTree
            nodes = np.flatnonzero(self.seeds < share)
            enodes = np.arange(0, len(self.ep), max(int(len(self.ep) / 170), 1))
            p = self.sp[nodes]
            tree = cKDTree(p)
            _d, j = tree.query(p, k=4, distance_upper_bound=0.075)
            ii = np.repeat(np.arange(len(nodes)), 3)
            jj = j[:, 1:].reshape(-1)
            ok = jj < len(nodes)
            ii, jj = ii[ok], jj[ok]
            same = np.sign(p[ii, 2]) == np.sign(p[jj, 2])
            pairs = np.unique(np.sort(np.stack([ii[same], jj[same]], axis=1), axis=1), axis=0)
            self._plex = (share, nodes, pairs, enodes, np.arange(0, len(self.fp), 5))
        _s, nodes, pairs, enodes, fsel = self._plex
        sd = self.seeds[nodes] / share
        pos, vis = c["pos"], c["vis"]
        va = vis[nodes]
        col = c1[None] * (0.7 + 0.3 * sd[:, None]) + c2[None] * 0.3 * (1 - sd[:, None])
        out = [dict(pos=pos[nodes], size=(0.0045 + 0.010 * sd ** 8) * H * sz, color=col, alpha=0.8 * b * va,
                    emit=1.2 + 2.5 * (sd > 0.95), kind="soft", twinkle=0.6, seed=sd)]
        la = np.minimum(va[pairs[:, 0]], va[pairs[:, 1]])
        keep = la > 0.05
        out.append(dict(pos=pos[nodes[pairs[keep, 0]]], pos2=pos[nodes[pairs[keep, 1]]], size=0.0016 * H * sz,
                        color=c2 * 0.55 + c1 * 0.45, alpha=0.32 * b * la[keep], kind="line"))
        w = (self._edge_weight(c["ep"]) * c["ebot"])[enodes]
        en = c["epos"][enodes]
        out.append(dict(pos=en, size=0.0065 * H * sz, color=c2, alpha=0.9 * b * w, emit=1.6, kind="spark",
                        twinkle=0.5))
        out.append(dict(pos=en[:-1], pos2=en[1:], size=0.0018 * H * sz, color=c2 * 0.7 + c1 * 0.3,
                        alpha=0.5 * b * np.minimum(w[:-1], w[1:]), kind="line"))
        fa = self.features * lk.get("features", 1.0)
        if fa > 0.0:
            fq = c["fpos"][fsel]
            fw = (self.fw * c["fvis"])[fsel]
            out.append(dict(pos=fq, size=0.0040 * H * sz, color=c2, alpha=0.8 * b * fa * fw, emit=1.3, kind="soft",
                            twinkle=0.4))
            link = np.linalg.norm(fq[1:] - fq[:-1], axis=1) < 0.03 * H
            out.append(dict(pos=fq[:-1][link], pos2=fq[1:][link], size=0.0015 * H * sz, color=c2,
                            alpha=0.45 * b * fa * np.minimum(fw[:-1], fw[1:])[link], kind="line"))
        return out

    def _look_ink(self, lk, c):
        b = self.bright * lk.get("bright", 1.0)
        sz = self.size * lk.get("size", 1.0)
        H = c["H"]
        w = self._edge_weight(c["ep"]) * c["ebot"]
        out = [dict(pos=c["epos"], size=0.0026 * H * sz, color=self.color, alpha=0.55 * b * w, kind="soft",
                    twinkle=0.3, seed=self.eseeds)]
        return out + self._feat(lk, c, 0.35, 0.0024, self.color2)

    def _look_fill(self, lk, c):
        b = self.bright * lk.get("bright", 1.0)
        sz = self.size * lk.get("size", 1.0)
        H = c["H"]
        w = self._edge_weight(c["ep"]) * c["ebot"] * _smooth(-0.30, 0.15, c["ep"][:, 0])
        out = [dict(pos=c["epos"], size=0.0024 * H * sz, color=self.color2, alpha=0.30 * b * w, kind="soft",
                    twinkle=0.3, seed=self.eseeds)]
        return out + self._feat(lk, c, 0.40, 0.0026, self.color2)

    # ------------------------------------------------------------------ embers leaving the head
    def _stream(self, t, fr, H):
        st = self.stream
        n = int(st["n"])
        k = np.arange(n)
        r1, r2, r3, r4 = hash01(n, 11), hash01(n, 12), hash01(n, 13), hash01(n, 14)
        life = st["life"] * (0.6 + 0.8 * r2)
        clock = t * st["rate"] + r1 * life * 7.0
        age = np.mod(clock, life)
        cyc = np.floor(clock / life).astype(np.int64)
        v0, v1 = st["where"]
        cand = np.flatnonzero((self.ep[:, 1] > v0) & (self.ep[:, 1] < v1))
        if len(cand) == 0:
            return []
        pick = cand[(bm.hashf(k * 977 + cyc * 131, 15) * len(cand)).astype(np.int64) % len(cand)]
        p0, _ = self.pose(self.ep[pick], None, t)
        d = np.array([st["dir"][0], st["dir"][1], 0.0])
        d /= np.linalg.norm(d)
        spd = st["speed"] * (0.5 + r3)
        side = (bm.hashf(k * 31 + cyc, 16) - 0.5) * 2.0
        drift = bm.flow(p0 * 4.0 + (cyc % 97)[:, None] * 0.37, t * 0.35, speed=1.0, seed=self.seed)
        q = p0 + d[None] * (spd * age)[:, None] + drift * (st["spread"] * age ** 1.2)[:, None]
        q[:, 2] += side * 0.12 * age
        u = age / life
        a = np.clip(age / 0.25, 0, 1) * np.clip((1.0 - u) / 0.6, 0, 1) ** 1.4
        size = (0.004 + 0.012 * r4 ** 3) * H * st["size"] * (1.0 + 1.2 * u)
        mix = (r4 ** 2)[:, None]
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        return [dict(pos=fr.world(q), size=size, color=col, alpha=0.75 * a * self.bright,
                     emit=1.0 + 2.0 * (r4 > 0.93), kind="soft", twinkle=0.8, seed=r4)]

    # ------------------------------------------------------------------ the silhouette for a mask
    def shape_set(self, hair=True, grow=1.0):
        """A point set of the whole head and shoulders (and the hair mass): the source of a Mask, so the head is
        a dark shape, a flat colour or a window onto a nebula."""
        return _ProfileSolid(self, hair, grow)


class _ProfileSolid:
    wants_camera = True

    def __init__(self, prof, hair, grow):
        self.prof, self.hair, self.grow = prof, hair, grow
        g = prof.g
        rs = np.random.default_rng(7)
        lo, hi = g.outline.min(axis=0), g.outline.max(axis=0)
        m = 40000
        u = rs.uniform(lo[0], hi[0], m)
        v = rs.uniform(-0.86, hi[1], m)
        ok = g.inside(u, v)
        self.pts = np.stack([u[ok], v[ok], np.zeros(ok.sum())], axis=1)
        self.bottom = _smooth(-0.86, -0.62, v[ok])

    def gain(self, t):
        return self.prof.gain(t)

    def sample(self, t, cam=None):
        pr = self.prof
        if pr.show is not None and not (pr.show[0] <= t <= pr.show[1]):
            return []
        fr = pr.frame(t)
        p, _ = pr.pose(self.pts, None, t)
        out = [dict(pos=fr.world(p), size=0.016 * fr.H * self.grow, alpha=self.bottom, kind="soft")]
        e, _n = pr.pose(pr.ep, None, t)
        out.append(dict(pos=fr.world(e), size=0.005 * fr.H * self.grow, alpha=1.0, kind="soft"))
        if self.hair and pr.hair is not None:
            out += pr.hair.solid(t)
        return out


# ----------------------------------------------------------------------------------------------- hair
class Hair:
    """Long hair as a mass of flowing locks (refs p02, p04, p05), for a Profile, a Body, or anything with
    frame(t) (a HeadFrame) and optionally pose(p, n, t).

    length     head heights from the crown to the tips (1.0 to the shoulders, 2.0 long)
    locks      how many locks; per_lock: strands in each; n: points along a strand
    wind       (u, v) in head units: where the hair streams (default back and a little up), or a function of
               time; gust: how much the wind swells and falls
    wave       how strongly the locks wave; curl: how much the tips curl (0..1)
    volume     how far the hair stands off the skull (head heights)
    look       "glow" (strands of light), "ink" (a painted dark mass with a sheen of light: day skies),
               "sparks" (dim strands that shed sparks); bright, alpha, color, color2, ink (display hex)
    """
    C = np.array([-0.10, 0.60])      # the skull as a circle in the profile drawing (head units)
    RAD = 0.43

    def __init__(self, head, length=1.5, locks=70, per_lock=14, n=40, wind=(-1.0, 0.15), gust=0.5, wave=1.0,
                 curl=0.5, volume=0.06, look="glow", color="#ffb060", color2="#ffe2b0", ink="#1a1530", bright=1.0,
                 alpha=1.0, seed=1.0):
        self.head = head
        self.length, self.locks, self.per_lock, self.n = float(length), int(locks), int(per_lock), int(n)
        self.wind, self.gust, self.wave = wind, float(gust), float(wave)
        self.curl, self.volume = float(curl), float(volume)
        self.look = look
        self.color, self.color2, self.inkc = _col(color), _col(color2), ink
        self.bright, self.alpha = float(bright), float(alpha)
        self.seed = float(seed)
        L = self.locks
        S = L * self.per_lock
        base = int(seed * 100)

        def rk(salt, m=L):
            return hash01(m, base + salt).astype(np.float64)

        self.lock_th = np.radians(36.0 + 172.0 * rk(1) ** 0.9)
        self.lock_w = (rk(2) - 0.5) * 2.0
        self.lock_len = self.length * (0.75 + 0.45 * rk(3))
        self.lock_ph = rk(4) * 2 * np.pi
        self.lock_k = 0.8 + 0.6 * rk(5)
        self.lock_curl = rk(6)
        self.lid = np.repeat(np.arange(L), self.per_lock)
        self.s_dth = (rk(7, S) - 0.5) * 0.10
        self.s_dw = (rk(8, S) - 0.5) * 0.10
        self.s_len = 0.85 + 0.25 * rk(9, S)
        self.s_off = (rk(10, S) - 0.5) * 0.025
        self.s_seed = rk(11, S)

    def strands(self, t):
        """(S, n, 3) points of every strand in head units at t."""
        n = self.n
        lid = self.lid
        th0 = self.lock_th[lid] + self.s_dth
        w0 = np.clip(self.lock_w[lid] + self.s_dw, -1.0, 1.0)
        L = self.lock_len[lid] * self.s_len
        s = np.linspace(0.0, 1.0, n)[None, :]
        wid = np.sqrt(np.clip(1.0 - w0 ** 2, 0.0, 1.0))
        # 1. lying on the skull, from the root back over the head to where the hair leaves it
        rad = self.RAD + self.volume * (0.4 + 0.6 * np.abs(w0)) + self.s_off
        th_exit = np.radians(200.0) + 0.25 * np.abs(w0)
        arc = np.maximum(th_exit - th0, 0.0) * rad
        sl = s * L[:, None]
        on = sl < arc[:, None]
        th = th0[:, None] + sl / rad[:, None]
        su, sv = 0.75 + 0.25 * wid, 0.80 + 0.20 * wid
        cu = self.C[0] + rad[:, None] * np.cos(th) * su[:, None]
        cv = self.C[1] + rad[:, None] * np.sin(th) * sv[:, None]
        cw = (w0 * (0.36 + self.volume))[:, None] * np.ones_like(s)
        # 2. falling free from the exit point, streaming with the wind and waving
        th_e = np.maximum(th_exit, th0)
        eu = self.C[0] + rad * np.cos(th_e) * su
        ev = self.C[1] + rad * np.sin(th_e) * sv
        tdir = np.stack([-np.sin(th_e), np.cos(th_e)], axis=1)
        wd = np.asarray(_val(self.wind, t), np.float64)
        g = 1.0 + self.gust * (0.5 * np.sin(t * 0.9 + self.seed) + 0.3 * np.sin(t * 2.3 + 1.1))
        fall = np.array([0.0, -1.0]) + wd * g * 0.85
        fall = fall / np.linalg.norm(fall)
        x = np.maximum(sl - arc[:, None], 0.0)
        xl = np.maximum(L - arc, 1e-3)[:, None]
        bend = 1.0 - np.exp(-x / 0.18)
        dux = tdir[:, 0:1] * (1.0 - bend) + fall[0] * bend
        dvx = tdir[:, 1:2] * (1.0 - bend) + fall[1] * bend
        dx = np.diff(np.concatenate([np.zeros((len(lid), 1)), x], axis=1), axis=1)
        fu = eu[:, None] + np.cumsum(dux * dx, axis=1)
        fv = ev[:, None] + np.cumsum(dvx * dx, axis=1)
        q = x / xl
        nrm = np.array([-fall[1], fall[0]])
        k = self.lock_k[lid][:, None]
        ph = self.lock_ph[lid][:, None]
        amp = self.wave * 0.07 * (q ** 1.2) * (0.6 + 0.4 * k)
        wv = np.sin(x * 7.0 * k - t * 2.4 * k + ph) * amp
        ww = np.cos(x * 5.0 * k - t * 1.9 * k + ph * 1.3) * amp * 0.8
        cr = self.curl * self.lock_curl[lid][:, None] * _smooth(0.70, 1.0, q)
        ang = cr * 5.0 * (q - 0.70)
        cu2 = 0.06 * cr * (np.cos(ang) - 1.0)
        cs2 = 0.06 * cr * np.sin(ang)
        fu = fu + nrm[0] * wv + cu2 * fall[0] - cs2 * nrm[0]
        fv = fv + nrm[1] * wv + cu2 * fall[1] - cs2 * nrm[1]
        fw = cw + ww + (w0 * 0.10)[:, None] * q
        return np.stack([np.where(on, cu, fu), np.where(on, cv, fv), np.where(on, cw, fw)], axis=2)

    def _world(self, t):
        P = self.strands(t)
        S, n = P.shape[:2]
        flat = P.reshape(-1, 3)
        h = self.head
        if hasattr(h, "pose"):
            flat, _ = h.pose(flat, None, t)
        fr = h.frame(t)
        return fr.world(flat).reshape(S, n, 3), fr

    # worn by a Body, the hair is its own point set: scene.add("hair", Hair(BodyHead(body), ...))
    wants_camera = True

    def gain(self, t):
        h = getattr(self.head, "body", self.head)
        return float(h.gain(t)) if hasattr(h, "gain") else 1.0

    def sample(self, t, cam=None):
        h = getattr(self.head, "body", self.head)
        sh = getattr(h, "show", None)
        if sh is not None and not (sh[0] <= t <= sh[1]):
            return []
        return self.batches(t, cam)

    def batches(self, t, cam=None):
        P, fr = self._world(t)
        S, n = P.shape[:2]
        H = fr.H
        p1 = P[:, :-1].reshape(-1, 3)
        p2 = P[:, 1:].reshape(-1, 3)
        q = np.tile(np.linspace(0.0, 1.0, n)[:-1], S)
        ss = np.repeat(self.s_seed, n - 1)
        taper = (1.0 - 0.75 * q ** 1.5) * np.clip(q * 12.0, 0.3, 1.0)
        b = self.bright * self.alpha
        mix = (ss ** 2)[:, None]
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        out = []
        if self.look in ("glow", "sparks"):
            a = (0.16 + 0.30 * (ss > 0.92)) * taper * b * (0.55 if self.look == "sparks" else 1.0)
            out.append(dict(pos=p1, pos2=p2, size=0.0022 * H, color=col, alpha=a, kind="line"))
            if self.look == "sparks":
                pts = P[:, ::3].reshape(-1, 3)
                r = hash01(len(pts), 61)
                sel = r > 0.86
                jit = bm.flow(pts[sel] * 9.0, t * 0.8, speed=1.0, seed=self.seed) * 0.012 * H
                out.append(dict(pos=pts[sel] + jit, size=0.0045 * H, color=self.color, alpha=0.7 * b,
                                emit=1.0 + 2.0 * (r[sel] > 0.97), kind="soft", twinkle=0.9, seed=r[sel]))
        elif self.look == "ink":
            from .api import show
            ink = show(self.inkc) if isinstance(self.inkc, str) else np.asarray(self.inkc)
            out.append(dict(pos=p1, pos2=p2, size=0.0075 * H * (1.0 - 0.5 * q), color=ink, alpha=0.55 * taper * b,
                            kind="line", paint=1.0, paint_light=0.0))
            sel = np.repeat(self.s_seed > 0.80, n - 1)
            out.append(dict(pos=p1[sel], pos2=p2[sel], size=0.0018 * H, color=col[sel],
                            alpha=0.30 * taper[sel] * b, kind="line"))
        return out

    def solid(self, t):
        """The hair mass as points for a mask (its silhouette)."""
        P, fr = self._world(t)
        pts = P[:, ::2].reshape(-1, 3)
        q = np.tile(np.linspace(0.0, 1.0, P.shape[1])[::2], P.shape[0])
        return [dict(pos=pts, size=0.030 * fr.H * (1.0 - 0.6 * q), alpha=1.0, kind="soft")]


class BodyHead:
    """The head of a Body (engine/p3d/body.py) as a HeadFrame, so a Hair can be worn by a full figure:
    Hair(BodyHead(body), ...). Give the Body hair=False (the flowing mass replaces its own)."""

    def __init__(self, body, size=1.0):
        self.body = body
        self.size = float(size)

    def frame(self, t):
        b = self.body
        crown = np.asarray(b.where(t, "crown"), np.float64)
        neck = np.asarray(b.where(t, "neck"), np.float64)
        head = np.asarray(b.where(t, "head"), np.float64)
        mouth = np.asarray(b.where(t, "mouth"), np.float64)
        U = crown - neck
        U /= max(np.linalg.norm(U), 1e-9)
        F = mouth - head
        F -= U * np.dot(F, U)
        F /= max(np.linalg.norm(F), 1e-9)
        L = np.cross(U, F)
        H = 0.142 * b.rig.height * b.scale * self.size
        origin = crown - U * (1.0 - EYE_LEVEL) * H - F * (-0.02 - U_CENTRE) * H
        return HeadFrame(origin, F, U, L, H)
