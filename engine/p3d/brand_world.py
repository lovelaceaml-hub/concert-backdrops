"""The world of light, and the world that becomes the logo (engine/p3d; pure numpy). How a song uses it:
engine/UPGRADE-HOWTO.md, section Z.

  Globe(...)      a luminous Earth: an ocean painted deep (or pastel) blue, continents of warm light points
                  (Natural Earth land, assets/p3d/brand/land_2048.png), a rim of atmosphere, a slow turn; hearts
                  in the nine colours light up across the continents, spreading from Las Vegas, joined by arcs
                  of light. Looks: "night", "space", "day" (the soft pastel world of world_ref).
  Finale(...)     world to logo: the globe slows and settles, the two hearts sweep in from either side behind it,
                  its grid lines draw themselves over it, the olive branches grow, it becomes the logo; light
                  blooms from it into a soft pastel day and the logo rises into the end card's place.
  PASTEL          the pastel day look (cream, peach, sky blue, as on the official poster) for world `looks`
  land(lat, lon)  True where there is land (degrees)
"""
import math
import os

import numpy as np
from PIL import Image

from . import brand as B
from .api import hash01, lin, show

TAU = 2.0 * math.pi
HERE = os.path.dirname(os.path.abspath(__file__))
LAND_PNG = os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "p3d", "brand", "land_2048.png")
LAS_VEGAS = (36.17, -115.14)

_LAND = None


def _land_mask():
    global _LAND
    if _LAND is None:
        _LAND = np.asarray(Image.open(LAND_PNG).convert("L"), np.uint8) > 127
    return _LAND


def land(lat, lon):
    """True where there is land, for latitudes and longitudes in degrees (arrays)."""
    m = _land_mask()
    h, w = m.shape
    lat, lon = np.asarray(lat, np.float64), np.asarray(lon, np.float64)
    col = (np.mod(lon + 180.0, 360.0) / 360.0 * w).astype(np.int64) % w
    row = np.clip(((90.0 - lat) / 180.0 * h).astype(np.int64), 0, h - 1)
    return m[row, col]


def fib_sphere(n):
    """n points spread evenly over the unit sphere (a Fibonacci lattice): latitudes and longitudes in degrees."""
    i = np.arange(n) + 0.5
    lat = np.degrees(np.arcsin(1.0 - 2.0 * i / n))
    lon = np.mod(np.degrees(i * math.pi * (3.0 - math.sqrt(5.0))) + 180.0, 360.0) - 180.0
    return lat, lon


def _earth(lat, lon):
    """Unit vectors of the Earth's own frame: y the north pole, z longitude 0, x longitude 90 east."""
    la, lo = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(la) * np.sin(lo), np.sin(la), np.cos(la) * np.cos(lo)], axis=-1)


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / max(b - a, 1e-9), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _orient(pole):
    """The turn that stands the Earth's pole along `pole` (in the globe's own view frame: x right, y up, z toward
    the viewer), with longitude 0 as near the viewer as it can be: columns (x axis, pole, front)."""
    p = np.asarray(pole, np.float64)
    p = p / np.linalg.norm(p)
    ea = np.array([0.0, 0.0, 1.0]) - p * p[2]
    ea = ea / max(np.linalg.norm(ea), 1e-9)
    eb = np.cross(p, ea)
    return np.stack([eb, p, ea], axis=1)


def _slerp(a, b, u):
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    d = float(np.clip(a @ b, -1.0, 1.0))
    w = math.acos(d)
    if w < 1e-6:
        return a
    return (math.sin((1 - u) * w) * a + math.sin(u * w) * b) / math.sin(w)


def _disp(hexs):
    """A display hex as 0..1 rgb."""
    h = hexs.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float64) / 255.0


# the pastel day: cream, peach and sky blue, as on the official poster (for P3D world `looks`)
def _day(hexs, k):
    return show(hexs) * k


PASTEL = dict(base="cream", sky_top=_day("#8fc9f2", 0.92), sky_mid=_day("#dcefff", 0.86),
              sky_hor=_day("#fff0e0", 0.74), haze_color=_day("#ffeadc", 0.58), hill_color=_day("#c3cde6", 0.58),
              water=_day("#b4d6f0", 0.52), mist_color=_day("#fff1e4", 0.56), sun_color=_day("#fff4e2", 0.24),
              sun_el=46.0, sun_int=0.65, sun_disc=0.0, clouds=0.12, stars=0.0, milky=0.0, rays=0.0, haze=0.5,
              mist=0.15, dust=0.15, bokeh=0.15, dust_color="#fff6ea", dust_color2="#ffe0c8")

LOOK_COLORS = dict(
    night=dict(ocean_c="#2a68c6", ocean_e="#123a86", land="#ffd9a0", land2="#fff2d6", rim="#8fd6ff",
               paint_land=False, rim_k=0.5),
    space=dict(ocean_c="#1d4fa6", ocean_e="#0a2160", land="#ffcf8a", land2="#ffeccc", rim="#7cc8ff",
               paint_land=False, rim_k=0.65),
    day=dict(ocean_c="#6cb8e8", ocean_e="#3f8fcc", land="#8fd47c", land2="#b8e8a6", rim="#ffffff",
             paint_land=True, rim_k=0.16),
)


class Globe:
    """A luminous Earth in the 3D world.

    Place: pos (its centre), radius (metres), face ("camera" by default: it turns to the camera), camera
    (the song's Rig), or place=<brand.Place> (its size is the globe's diameter).
    look      "night" (a vivid blue ocean, continents of warm light, a cyan rim), "space" (deeper), "day" (the
              soft pastel world: light blue ocean and mint land painted in their colours, a white rim); or a
              dict of LOOK_COLORS keys; may change: look=[(t, name), ...] blends the colours over `blend` s
    scale     a size factor, a number or a function of t (the Finale shrinks the globe as it settles)
    spin      degrees a second it turns (6.0); front: the longitude that faces the camera at t=0 (-40: the
              Atlantic, the Americas on the left)
    tilt      degrees its north pole leans toward the camera (18)
    settle    dict(t0, t1, front=None, pole=None): the turn slows to a stop between t0 and t1 at the longitude
              `front` (default: where it would naturally come to rest), and the pole swings to `pole` (a
              direction in the globe's view frame, x right, y up, z toward the camera)
    t_in, t_out, fade   when it is there (it grows out of light over `fade` seconds); amount=<function t>
              overrides its strength (the Finale uses it)
    hearts    dict(t0, t1, n=42, size=0.10, start=LAS_VEGAS, colors="nine"): hearts light up across the land
              spreading from `start` (lat, lon); size in globe radii; False for none
    arcs      True: each new heart is joined to the nearest one already lit by an arc of light (dict(height=0.18,
              width=0.006, dur=0.8))
    n         land points (40000 a hemisphere and a half; more for a globe that fills the picture)
    bright    strength of the light (land, rim, hearts)
    """

    def __init__(self, pos=(0.0, 12.0, -40.0), radius=8.0, face="camera", camera=None, place=None, look="night",
                 blend=1.2, spin=6.0, front=-40.0, tilt=18.0, settle=None, t_in=0.0, t_out=None, fade=1.2,
                 amount=None, hearts=None, arcs=True, n=40000, bright=1.0, scale=None, seed=4):
        sz = (lambda t: 2.0 * radius * float(scale(t))) if callable(scale) else 2.0 * radius * float(scale or 1.0)
        self.place = place or B.Place(pos=pos, size=sz, face=face)
        self.camera = camera
        self.wants_camera = True
        self.R = float(radius)
        self.look, self.blend = look, float(blend)
        self.spin, self.front, self.tilt = float(spin), float(front), float(tilt)
        self.settle = settle
        self.t_in, self.t_out, self.fade = float(t_in), t_out, float(fade)
        self.amount = amount
        self.bright = float(bright)
        # land: an even lattice on the sphere, kept where there is land
        tot = int(n / 0.29)
        lat, lon = fib_sphere(tot)
        keep = land(lat, lon)
        self.l_lat, self.l_lon = lat[keep], lon[keep]
        self.l_v = _earth(self.l_lat, self.l_lon)
        self.l_s = hash01(len(self.l_v), seed)
        self.l_s2 = hash01(len(self.l_v), seed + 1)
        self.cell = math.sqrt(4.0 * math.pi / tot)                  # lattice spacing in radii
        # ocean: a coarser even lattice over the whole sphere, painted
        on = max(int(n * 0.5), 12000)
        olat, olon = fib_sphere(on)
        self.o_v = _earth(olat, olon)
        self.o_cell = math.sqrt(4.0 * math.pi / on)
        # rim: a ring of soft light round the edge (in the view plane)
        rn = 900
        a = np.arange(rn) / rn * TAU
        self.rim_a = a
        self.rim_s = hash01(rn, seed + 2)
        # hearts and arcs
        self.hearts = None
        if hearts:
            self._make_hearts(dict(hearts), seed)
        self.arcs = (dict(height=0.18, width=0.006, dur=0.8) if arcs is True else dict(arcs)) if (arcs and hearts) \
            else None

    # ------------------------------------------------------------------ the turn
    def _front_at(self, t):
        """The longitude facing the camera at t (degrees)."""
        st = self.settle
        if not st:
            return self.front + self.spin * t
        t0, t1 = float(st["t0"]), float(st["t1"])
        if t <= t0:
            return self.front + self.spin * t
        a0 = self.front + self.spin * t0
        d = t1 - t0
        # a natural stop: the turn eases out with the speed it had (or to the asked longitude)
        nat = a0 + 0.5 * self.spin * d
        tgt = nat if st.get("front") is None else float(st["front"])
        if st.get("front") is not None:
            k = round((nat - tgt) / 360.0)
            tgt = tgt + 360.0 * k
        u = min((t - t0) / d, 1.0)
        # hermite: starts at a0 with speed spin, ends at tgt with speed 0
        h00, h10, h01 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2
        return h00 * a0 + h10 * self.spin * d + h01 * tgt

    def _pole_at(self, t):
        a = math.radians(self.tilt)
        p0 = np.array([0.0, math.cos(a), math.sin(a)])
        st = self.settle
        if st and st.get("pole") is not None:
            return _slerp(p0, st["pole"], _sc(float(st["t0"]), float(st["t1"]), t))
        return p0

    def turn(self, t):
        """(3, 3): Earth frame to the globe's view frame at t."""
        A = _orient(self._pole_at(t))
        f = math.radians(self._front_at(t))
        c, s = math.cos(f), math.sin(f)
        Ry = np.array([[c, 0.0, -s], [0.0, 1.0, 0.0], [s, 0.0, c]])        # brings longitude f to the front
        return A @ Ry

    def strength(self, t):
        if self.amount is not None:
            return float(np.clip(self.amount(t), 0.0, 1.0))
        a = _sc(self.t_in, self.t_in + self.fade, t)
        if self.t_out is not None:
            a *= 1.0 - _sc(float(self.t_out), float(self.t_out) + self.fade, t)
        return a

    def gain(self, t):
        return 1.0 if self.strength(t) > 0.0 else 0.0

    def colors(self, t):
        """The look's colours at t (dict of display rgb and paint_land)."""
        lk = self.look
        if isinstance(lk, (list, tuple)):
            keys = sorted(lk, key=lambda k: k[0])
            cur = keys[0][1]
            out = self._look(cur)
            for tk, name in keys[1:]:
                w = _sc(tk - 0.5 * self.blend, tk + 0.5 * self.blend, t)
                if w <= 0:
                    break
                nxt = self._look(name)
                out = {k: (out[k] * (1 - w) + nxt[k] * w if k != "paint_land" else (nxt[k] if w > 0.5 else out[k]))
                       for k in out}
            return out
        return self._look(lk)

    @staticmethod
    def _look(lk):
        d = dict(LOOK_COLORS["night"])
        d.update(LOOK_COLORS[lk] if isinstance(lk, str) else lk)
        return {k: (_disp(v) if isinstance(v, str) else v) for k, v in d.items()}

    # ------------------------------------------------------------------ the hearts
    def _make_hearts(self, h, seed):
        n = int(h.get("n", 42))
        rng = np.random.default_rng(seed + 9)
        # places on land, spread apart (a few on every continent), the first at the start
        cand = rng.choice(len(self.l_lat), size=min(len(self.l_lat), 6000), replace=False)
        cl, co = self.l_lat[cand], self.l_lon[cand]
        ok = np.abs(cl) < 66.0                          # not on the ice
        cl, co = cl[ok], co[ok]
        cv = _earth(cl, co)
        start = h.get("start", LAS_VEGAS)
        pick = [_earth(np.array([start[0]]), np.array([start[1]]))[0]]
        lat_l, lon_l = [start[0]], [start[1]]
        dmin = np.full(len(cv), 9.0)
        for _ in range(n - 1):
            dmin = np.minimum(dmin, np.arccos(np.clip(cv @ pick[-1], -1, 1)))
            j = int(np.argmax(dmin * (0.6 + 0.4 * rng.random(len(cv)))))
            pick.append(cv[j])
            lat_l.append(cl[j])
            lon_l.append(co[j])
        v = np.array(pick)
        # light up in the order of the distance from the start, each joined to its nearest lit neighbour
        d0 = np.arccos(np.clip(v @ v[0], -1, 1))
        order = np.argsort(d0, kind="stable")
        v = v[order]
        t0, t1 = float(h.get("t0", 0.0)), float(h.get("t1", 4.0))
        rank = np.arange(n) / max(n - 1, 1)
        tl = t0 + (t1 - t0) * rank ** 0.85
        parent = np.full(n, -1)
        for k in range(1, n):
            parent[k] = int(np.argmin(np.arccos(np.clip(v[:k] @ v[k], -1, 1))))
        colors = h.get("colors", "nine")
        pal = B.NINE if colors == "nine" else ([colors] if isinstance(colors, str) else list(colors))
        self.hearts = dict(v=v, t=tl, parent=parent, size=float(h.get("size", 0.10)),
                           col=np.array([lin(pal[k % len(pal)]) for k in range(n)]),
                           hex=[pal[k % len(pal)] for k in range(n)], s=hash01(n, seed + 5))

    # ------------------------------------------------------------------ drawing
    def _view(self, t, cam):
        c, r, u, nrm, size = self.place.frame(t, cam)
        R = 0.5 * size
        M = np.stack([r, u, nrm], axis=1)            # view frame to world
        return c, M, R

    def _front_mask(self, wp, c, cam, R, margin=0.0):
        """Which world points on (or just above) the sphere face the camera."""
        if cam is None:
            return np.ones(len(wp), bool), np.ones(len(wp))
        cp = np.asarray(cam.pos, np.float64)
        nrm = (wp - c) / R
        to = cp - wp
        to /= np.maximum(np.linalg.norm(to, axis=1, keepdims=True), 1e-9)
        f = np.einsum("ij,ij->i", nrm, to)
        return f > margin, f

    def _occluded(self, wp, c, cam, R):
        """True for world points hidden behind the sphere from the camera."""
        if cam is None:
            return np.zeros(len(wp), bool)
        o = np.asarray(cam.pos, np.float64)
        d = wp - o
        L = np.linalg.norm(d, axis=1)
        d = d / np.maximum(L[:, None], 1e-9)
        oc = o - c
        b = d @ oc
        cc = float(oc @ oc) - (R * 0.995) ** 2
        disc = b * b - cc
        tt = -b - np.sqrt(np.maximum(disc, 0.0))
        return (disc > 0) & (tt > 0) & (tt < L - 1e-3)

    def sample(self, t, cam=None):
        k = self.strength(t)
        if k <= 0.0:
            return None
        if cam is None and self.camera is not None:
            cam = self.camera.state(t) if hasattr(self.camera, "state") else self.camera(t)
        c, M, R = self._view(t, cam)
        T = M @ self.turn(t)                         # Earth frame to world directions
        L = self.colors(t)
        out = []
        sun = np.array([-0.45, 0.55, 0.70])
        sun /= np.linalg.norm(sun)
        sun_w = M @ sun
        # the ocean: painted, a sphere seen from the front, lighter in the middle and toward the light
        ov = self.o_v @ T.T
        op = c[None, :] + R * ov
        front, f = self._front_mask(op, c, cam, R, -0.02)
        if front.any():
            sh = np.clip(ov[front] @ sun_w, -1, 1)
            mid = np.clip(f[front], 0, 1) ** 0.6
            col = L["ocean_e"] * (1 - mid[:, None]) + L["ocean_c"] * mid[:, None]
            col = col * (0.82 + 0.25 * sh[:, None])
            out.append(dict(pos=op[front], size=R * self.o_cell * 1.8, color=B.show_rgb(np.clip(col, 0, 1)),
                            alpha=np.full(int(front.sum()), 2.0), kind="disc", paint=k, paint_light=0.05,
                            dof=0.0, fog=0.0, reflect=True, streak=0.2))
        # the land: warm light (night, space) or painted mint (day)
        lv = self.l_v @ T.T
        lp = c[None, :] + R * 1.002 * lv
        front, f = self._front_mask(lp, c, cam, R, 0.0)
        if front.any():
            edge = np.clip(f[front] / 0.25, 0.0, 1.0)
            sh = np.clip(lv[front] @ sun_w, -1, 1)
            if L["paint_land"] is True or (isinstance(L["paint_land"], float) and L["paint_land"] > 0.5):
                col = L["land"] * (0.85 + 0.2 * sh[:, None])
                out.append(dict(pos=lp[front], size=R * self.cell * 1.8, color=B.show_rgb(np.clip(col, 0, 1)),
                                alpha=edge * 2.0, kind="disc", paint=k, paint_light=0.08, dof=0.0, fog=0.0, streak=0.2))
            else:
                s1 = self.l_s[front]
                col = lin("#%02x%02x%02x" % tuple(int(v * 255) for v in L["land"]))
                col2 = lin("#%02x%02x%02x" % tuple(int(v * 255) for v in L["land2"]))
                cc = np.where((s1 < 0.12)[:, None], col2[None, :], col[None, :])
                br = (0.55 + 0.45 * self.l_s2[front]) * (0.75 + 0.35 * np.clip(sh, 0, 1))
                out.append(dict(pos=lp[front], size=R * self.cell * 1.1, color=cc * 1.25 * self.bright,
                                alpha=(edge * br * k).astype(np.float32), kind="soft", twinkle=0.25,
                                seed=s1, dof=0.0, fog=0.0, streak=0.2))
                g = front & (self.l_s < 0.006)
                if g.any():
                    out.append(dict(pos=c[None, :] + R * 1.004 * lv[g], size=R * 0.02, color=col2 * 1.5,
                                    alpha=0.8 * k, emit=2.0, kind="spark", twinkle=1.0, seed=self.l_s2[g], dof=0.0))
        # the rim of air: a soft ring round the edge, facing the camera
        a = self.rim_a
        rr = 1.0 + 0.035 * self.rim_s
        ring = c[None, :] + R * rr[:, None] * (np.cos(a)[:, None] * M[:, 0][None, :] + np.sin(a)[:, None] * M[:, 1][None, :])
        rimc = lin("#%02x%02x%02x" % tuple(int(v * 255) for v in L["rim"]))
        out.append(dict(pos=ring, size=R * 0.05, color=rimc * 1.2 * self.bright, alpha=L["rim_k"] * k, kind="soft",
                        dof=0.0, fog=0.0, streak=0.0, seed=self.rim_s))
        out.append(dict(pos=ring[::3], size=R * 0.22, color=rimc * 0.8 * self.bright, alpha=0.2 * L["rim_k"] * k, kind="soft",
                        dof=1.0, fog=0.0, streak=0.0))
        # hearts and arcs
        if self.hearts is not None:
            out += self._hearts(t, cam, c, R, T, k)
        return out

    def _hearts(self, t, cam, c, R, T, k):
        H = self.hearts
        out = []
        age = t - H["t"]
        on = age > -0.05
        if self.arcs:
            dur = float(self.arcs.get("dur", 0.8))
            hgt = float(self.arcs.get("height", 0.18))
            wid = float(self.arcs.get("width", 0.006))
            segs_p0, segs_p1, segs_a, segs_c = [], [], [], []
            for j in np.nonzero(age > -dur)[0]:
                p = H["parent"][j]
                if p < 0:
                    continue
                g = float(np.clip((age[j] + dur) / dur, 0.0, 1.0))      # the arc arrives as the heart lights
                fade = 0.35 + 0.65 * math.exp(-max(age[j], 0.0) / 1.5)
                a, b = H["v"][p], H["v"][j]
                ang = math.acos(float(np.clip(a @ b, -1, 1)))
                m = 24
                us = np.linspace(0.0, g, m)
                pts = np.array([_slerp(a, b, u) for u in us]) if ang > 1e-4 else np.repeat(a[None], m, 0)
                lift = 1.0 + hgt * ang * np.sin(np.pi * us)
                wpts = c[None, :] + R * (pts * lift[:, None]) @ T.T
                ca = (H["col"][p] + H["col"][j]) * 0.5
                al = np.full(m, fade * k) * np.clip(us / max(g, 1e-6) * 4.0, 0.2, 1.0)
                al[self._occluded(wpts, c, cam, R)] = 0.0
                segs_p0.append(wpts[:-1])
                segs_p1.append(wpts[1:])
                segs_a.append(np.stack([al[:-1], al[1:]], axis=1))
                segs_c.append(np.repeat(ca[None], m - 1, 0))
            if segs_p0:
                aa = np.vstack(segs_a)
                out.append(dict(pos=np.vstack(segs_p0), pos2=np.vstack(segs_p1), size=R * wid,
                                alpha=aa[:, 0] * 0.9, alpha2=aa[:, 1] * 0.9, color=np.vstack(segs_c) * 1.6 * self.bright,
                                kind="ribbon", dof=0.0, fog=0.0, reflect=False, pulse=(R * 0.8, R * 0.25, 1.5, R * 2.0)))
        idx = np.nonzero(on)[0]
        if len(idx):
            v = H["v"][idx] @ T.T
            wp = c[None, :] + R * 1.03 * v
            front, f = self._front_mask(wp, c, cam, R, 0.02)
            if front.any():
                a_ = np.clip(age[idx] / 0.25, 0.0, 1.0) * np.clip(f / 0.2, 0.0, 1.0) * k
                pop = 1.0 + 0.6 * np.exp(-np.maximum(age[idx], 0.0) / 0.18) * (age[idx] > 0)
                size = R * H["size"] * pop
                sel = front & (a_ > 0.003)
                col = H["col"][idx]
                m = max(1, len(idx))
                deep = col / np.maximum(col.max(axis=1, keepdims=True), 1e-6)
                out.append(dict(pos=wp[sel], size=size[sel], color=(deep ** 1.2 * 1.5 * self.bright)[sel],
                                alpha=a_[sel], kind="heart", dof=0.0, fog=0.0, seed=H["s"][idx][sel]))
                out.append(dict(pos=wp[sel], size=size[sel] * 3.0, color=(deep * 0.6 * self.bright)[sel],
                                alpha=a_[sel] * 0.10, kind="soft", dof=1.0, fog=0.0, streak=0.0))
                fl = sel & (age[idx] < 0.5)
                if fl.any():
                    out.append(dict(pos=wp[fl], size=size[fl] * 0.8, color=np.array([1.0, 0.96, 0.9]) * 1.5,
                                    alpha=np.exp(-np.maximum(age[idx][fl], 0) / 0.15) * k, emit=2.5, kind="spark",
                                    dof=0.0))
                _ = m
        return out

    def where(self, t, cam=None):
        """The globe's centre and radius in the world at t."""
        if cam is None and self.camera is not None:
            cam = self.camera.state(t) if hasattr(self.camera, "state") else self.camera(t)
        c, M, R = self._view(t, cam)
        return c, R


class _Bloom:
    """A soft spreading light from a point: the globe blooming into day."""

    def __init__(self, at, t, dur, radius, color="#fff1de", glow=0.5):
        self.at, self.t, self.dur, self.r, self.col = at, float(t), float(dur), float(radius), lin(color) * glow / 0.5
        s = hash01(400, 77)
        s2 = hash01(400, 78)
        a = s * TAU
        self.dir = np.stack([np.cos(a), np.sin(a)], axis=1)
        self.s, self.s2 = s, s2
        self.wants_camera = True

    def gain(self, t):
        return 1.0 if self.t - 0.4 <= t <= self.t + self.dur + 0.2 else 0.0

    def sample(self, t, cam=None):
        if self.gain(t) <= 0 or cam is None:
            return None
        c = np.asarray(self.at(t) if callable(self.at) else self.at, np.float64)
        u = (t - self.t) / self.dur
        k = math.exp(-((u - 0.25) / 0.35) ** 2)
        r, up, f = cam.basis()
        rad = self.r * (0.2 + 2.5 * max(u, 0.0)) * (0.3 + 0.7 * self.s2)
        p = c[None, :] + rad[:, None] * (self.dir[:, 0:1] * r[None, :] + self.dir[:, 1:2] * up[None, :])
        return [dict(pos=p, size=self.r * 0.06, color=self.col * 1.6, alpha=0.5 * k, emit=2.0, kind="spark",
                     twinkle=1.0, seed=self.s, dof=0.0, reflect=False)]


class Finale:
    """World to logo: the globe of light settles and becomes the campaign logo, light blooms from it into a soft
    pastel day, and the logo rises into the end card's place.

    pos, radius       the globe's centre and radius (metres); camera: the song's Rig (needed)
    look              the globe's look before the bloom ("night", "space" or "day")
    t_world           when the globe forms (its light gathers over 1.2 s); spin, front, tilt as Globe
    hearts            dict(t0, t1, n=42, ...) as Globe (False for none); the hearts and arcs fade as the logo forms
    t_settle          (t0, t1): the globe slows and stops, its pole swinging to the logo's pole
    t_logo            (t0, t1): it becomes the logo (hearts sweep in from either side behind it, the grid draws
                      itself over it, the branches grow); the logo is whole at t1 (54.3 to 55.0 in the films)
    shrink            the globe draws in to this share of its size as it settles (0.6), so the whole logo fits
    bloom             dict(t=54.3, dur=1.0, strength=0.25, glow=0.5, color="#fff1de"): light blooms from the globe
                      (a flash of `strength`, P3D bursts, and a soft spreading light of `glow`); the
                      world turns to the pastel day `look_after` round t (its blend `blend` seconds); None for no
                      bloom (then give the world's look yourself)
    end               dict(t=(55.0, 56.4), ride=(0.5, 0.78, 14.0), frac=0.22): the logo glides from where the globe
                      was to that place of the picture (x, y from the left and the bottom, metres ahead of the lens)
                      and size (a share of the picture's height) and stays there; None keeps it where it formed
    paint             the logo's paint over time (default: light as it forms, painted in its exact colours by the
                      end of the bloom, so it is true on the bright day)
    logo              dict of other brand.Logo keys (bright, white, glow, sparkle, palette, n, ...)

    Use: fin.add_to(scene) in the song's setup; P3D world=fin.world(dict(...)) (adds the pastel look at the bloom
    and the burst); P3D bursts=fin.bursts() (or fin.world does it for you with world_bursts=True).
    fin.globe and fin.logo are the two point sets; fin.logo_place is the logo's Place.
    """

    BLOOM = dict(t=54.3, dur=1.0, strength=0.25, color="#fff1de", glow=0.5)

    def __init__(self, pos=(0.0, 12.0, -40.0), radius=8.0, camera=None, look="night", t_world=49.5, spin=6.0,
                 front=-40.0, tilt=18.0, hearts=None, t_settle=(52.6, 54.0), t_logo=(53.4, 55.0), shrink=0.6,
                 bloom=None, end=None, look_after="pastel", blend=0.9, paint=None, logo=None, n=40000):
        self.pos, self.R, self.camera = np.asarray(pos, np.float64), float(radius), camera
        self.t_world = float(t_world)
        self.t_settle, self.t_logo = tuple(t_settle), tuple(t_logo)
        self.bloom = None if bloom is False else dict(self.BLOOM, **(bloom or {}))
        self.end = dict(t=(55.0, 56.4), ride=(0.5, 0.78, 14.0), frac=0.22) if end is None else end
        self.look_after, self.blend = look_after, float(blend)
        self.shrink = float(shrink)
        l0, l1 = self.t_logo
        w = l1 - l0
        if hearts is None:
            hearts = dict(t0=self.t_world + 0.8, t1=self.t_settle[0] + 0.4, n=42)
        if hearts:
            hearts = dict(hearts)
        s0, s1 = self.t_settle

        def scale(t):                            # the globe draws in a little as it settles: room for the hearts
            return 1.0 - (1.0 - self.shrink) * _sc(s0 - 0.4, s1, t)

        self.scale = scale
        # the globe: strong until the logo's own globe takes over
        fade_a, fade_b = l0 + 0.30 * w, l0 + 0.70 * w
        self.globe = Globe(pos=tuple(self.pos), radius=self.R, camera=camera, look=look, spin=spin, front=front,
                           tilt=tilt, settle=dict(t0=s0, t1=s1, pole=tuple(B.POLE)), scale=scale,
                           amount=lambda t: _sc(self.t_world, self.t_world + 1.2, t) * (1.0 - _sc(fade_a, fade_b, t)),
                           hearts=hearts, n=n)
        # the logo: its globe sits exactly on the Earth (same centre, its disc the Earth's radius)
        gx, gy = B.GLOBE_CENTER

        def size(t):
            return self.R * scale(t) / B.GLOBE_DISC

        def logo_pos(t, cam=None):
            cam = cam or (camera.state(t) if hasattr(camera, "state") else camera(t))
            c = self.pos
            d = np.asarray(cam.pos, np.float64) - c
            az = math.atan2(d[0], d[2])
            right = np.array([math.cos(az), 0.0, -math.sin(az)])
            return c - size(t) * (gx * right + gy * np.array([0.0, 1.0, 0.0]))

        self._logo_pos = logo_pos
        keys = None
        if self.end:
            e0, e1 = self.end["t"]
            keys = [(e0, dict(pos=logo_pos, size=size, face="camera", ride=None)),
                    (e1, dict(ride=self.end["ride"], frac=self.end["frac"], face="screen"))]
        self.logo_place = B.Place(pos=logo_pos, size=size, face="camera", keys=keys)
        amt = dict(
            heart_l=lambda t: _sc(l0, l0 + 0.55 * w, t) if t < l0 + 0.55 * w else 1.0,
            heart_r=lambda t: _sc(l0 + 0.04 * w, l0 + 0.60 * w, t) if t < l0 + 0.6 * w else 1.0,
            globe=lambda t: _sc(fade_a, fade_b, t),
            ring=lambda t: float(np.clip((t - (l0 + 0.25 * w)) / (0.35 * w), 0, 1)),
            grid=lambda t: float(np.clip((t - (l0 + 0.32 * w)) / (0.45 * w), 0, 1)),
            branch_l=lambda t: float(np.clip((t - (l0 + 0.58 * w)) / (0.42 * w), 0, 1)),
            branch_r=lambda t: float(np.clip((t - (l0 + 0.54 * w)) / (0.42 * w), 0, 1)),
        )
        bt = self.bloom["t"] if self.bloom else l1
        if paint is None:
            # painted in its exact colours before the day blooms behind it, so it never pales
            def paint(t):
                return _sc(min(l0 + 0.35 * w, bt - 0.3), bt, t)
        kw = dict(bright=0.5, white=0.45, glow=0.25, sparkle=0.06, n=90000)
        kw.update(logo or {})
        self.logo = B.Logo(place=self.logo_place, camera=camera, t_in=l0, t_full=l1, arrive="build", amount=amt,
                           paint=paint, **kw)

    def add_to(self, scene, name="finale"):
        scene.add(name + " globe", self.globe)
        scene.add(name + " logo", self.logo)
        if self.bloom and self.bloom.get("glow", 0.5) > 0:
            b = self.bloom
            scene.add(name + " bloom", _Bloom(self.pos, b["t"], b["dur"], self.R * self.shrink,
                                              b.get("color", "#fff1de"), float(b.get("glow", 0.5))), reflect=False)

    def bursts(self):
        """The bloom's flash of light (P3D bursts); empty with strength 0."""
        if not self.bloom or float(self.bloom.get("strength", 0.25)) <= 0:
            return []
        b = self.bloom
        return [dict(t=b["t"] + 0.1 * b["dur"], strength=float(b.get("strength", 0.25)), rise=0.3 * b["dur"],
                     fall=0.55 * b["dur"], color=b.get("color", "#fff1de"), at=tuple(self.pos), radius=0.35)]

    def world(self, base=None):
        """The song's world settings with the bloom to the pastel day added (the look keys and the PASTEL look)."""
        w = dict(base or dict(look="night"))
        looks = dict(w.get("looks", {}))
        looks.setdefault("pastel", dict(PASTEL))
        w["looks"] = looks
        if self.bloom:
            lk = w.get("look", "night")
            keys = [(0.0, lk)] if isinstance(lk, str) else list(lk)
            keys = [k for k in keys if k[0] < self.bloom["t"]]
            keys.append((self.bloom["t"] + 0.2 * self.bloom["dur"], self.look_after, self.blend))
            w["look"] = keys
        return w

    def logo_box(self, t, cam=None):
        """Where the logo is in the picture at t: (x0, y0, x1, y1) as shares of the frame (y up)."""
        cam = cam or (self.camera.state(t) if hasattr(self.camera, "state") else self.camera(t))
        x, y, z, *_ = self.logo.local(t)
        pts = self.logo_place.world(t, np.array([-B.LOGO_ASPECT / 2, B.LOGO_ASPECT / 2]), np.array([-0.5, 0.5]),
                                    None, cam)
        xy, _ = cam.project(pts)
        return float(xy[:, 0].min()), float(xy[:, 1].min()), float(xy[:, 0].max()), float(xy[:, 1].max())
