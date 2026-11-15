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

from . import brand as B
from .api import hash01, lin, show
from .brand import _val

Image = B.Image                          # PIL, loaded on first use

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
              sun_az=0.0, sun_el=46.0, sun_int=0.65, sun_disc=0.0, clouds=0.12, stars=0.0, milky=0.0, rays=0.0, haze=0.5,
              mist=0.15, dust=0.15, bokeh=0.15, dust_color="#fff6ea", dust_color2="#ffe0c8")

LOOK_COLORS = dict(
    # night: a deep blue ocean, continents of warm golden light (a world lit by love), pale moonlit cloud
    # wisps, a soft blue atmosphere
    night=dict(ocean_c="#2563c2", ocean_e="#0f3480", land="#ffb340", land2="#fff0c4", land_base="#2a1a0c",
               rim="#8fd6ff", cloud="#d6e6ff", paint_land=False, rim_k=0.5, cloud_k=0.30, glow_k=1.0, land_k=1.0),
    space=dict(ocean_c="#1d4fa6", ocean_e="#0a2160", land="#ffb340", land2="#ffeccc", land_base="#24160a",
               rim="#7cc8ff", cloud="#c8dcff", paint_land=False, rim_k=0.65, cloud_k=0.25, glow_k=1.0, land_k=1.0),
    # day: the soft pastel clay world of world_ref, painted (it never adds light over the sky): a gentle blue
    # ocean, soft green land, a little white cloud, a thin pale air
    day=dict(ocean_c="#8cc3e3", ocean_e="#5b98cb", land="#a3d593", land2="#bfe3ad", land_base="#a3d593",
             rim="#f2fbff", cloud="#ffffff", paint_land=True, rim_k=0.12, cloud_k=0.12, glow_k=0.0, land_k=1.0),
)


def _noise_grid(seed, w=360, h=180):
    """Cloud cover over the Earth (lat, lon grid, 1 degree): wisps stretched east to west, 0..1."""
    rng = np.random.default_rng(seed)
    lat = np.radians(90.0 - (np.arange(h) + 0.5) * 180.0 / h)
    lon = np.radians(-180.0 + (np.arange(w) + 0.5) * 360.0 / w)
    LO, LA = np.meshgrid(lon, lat)
    v = np.stack([np.cos(LA) * np.sin(LO), np.sin(LA), np.cos(LA) * np.cos(LO)], axis=-1).reshape(-1, 3)
    K = 30
    d = rng.normal(size=(K, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    fr = 2.0 + 9.0 * rng.random(K) ** 1.6
    d = d * fr[:, None] * np.array([1.0, 2.6, 1.0])            # more change across latitude: long wisps
    ph = rng.random(K) * TAU
    warp = 0.25 * np.sin(v @ (rng.normal(size=(3, 3)) * 3.0))      # a little swirl
    f = (np.sin((v + warp) @ d.T + ph) / fr).sum(axis=1)
    f = (f - f.mean()) / max(f.std(), 1e-9)
    return _ss(0.35, 1.7, f).reshape(h, w)


def _grid_at(g, lat, lon):
    h, w = g.shape
    col = (np.mod(np.asarray(lon) + 180.0, 360.0) / 360.0 * w).astype(np.int64) % w
    row = np.clip(((90.0 - np.asarray(lat)) / 180.0 * h).astype(np.int64), 0, h - 1)
    return g[row, col]


def _slerp_many(a, b, us):
    """Points along the great circle from a to b at shares us (m, 3)."""
    d = float(np.clip(a @ b, -1.0, 1.0))
    w = math.acos(d)
    if w < 1e-6:
        return np.repeat(a[None], len(us), 0)
    return (np.sin((1 - us) * w)[:, None] * a[None] + np.sin(us * w)[:, None] * b[None]) / math.sin(w)


class Globe:
    """A luminous Earth in the 3D world.

    Place: pos (its centre), radius (metres), face ("camera" by default: it turns to the camera), camera
    (the song's Rig), or place=<brand.Place> (its size is the globe's diameter).
    look      "night" (a deep blue ocean, continents of warm golden light, moonlit cloud wisps, a soft blue
              atmosphere), "space" (deeper), "day" (a gentle blue ocean and soft green land painted in their
              colours, a little white cloud, a thin pale air; it adds almost no light, so it never washes out
              on a bright sky; the soft pastel clay colours of world_ref); or a dict of LOOK_COLORS keys; may
              change: look=[(t, name), ...] blends the colours over `blend` s
    scale     a size factor, a number or a function of t (the Finale shrinks the globe as it settles)
    spin      degrees a second it turns (6.0); front: the longitude that faces the camera at t=0 (-40: the
              Atlantic, the Americas on the left)
    tilt      degrees its north pole leans toward the camera (18)
    settle    dict(t0, t1, front=None, pole=None): the turn slows to a stop between t0 and t1 at the longitude
              `front` (default: where it would naturally come to rest), and the pole swings to `pole` (a
              direction in the globe's view frame, x right, y up, z toward the camera)
    t_in, t_out, fade   when it is there (it grows out of light over `fade` seconds); amount=<function t>
              overrides its strength (the Finale uses it)
    hearts    dict(t0, t1, n=42, size=0.15, start=LAS_VEGAS, colors="nine", pulse=1.0): hearts light up across
              the land spreading from `start` (lat, lon), each blooming open with a soft pulse of light in its
              colour; painted in their exact colours (they stay true over the land's light); size in globe
              radii; False for none
    arcs      True: each new heart is joined to the nearest one already lit by an arc of light that rises
              and travels with a glowing head (dict(height=0.2, width=0.009, dur=1.0, glow=1.0); height: how
              far a long arc rises above the land, in radii)
    clouds    True: drifting cloud wisps (dict(drift=2.5) degrees a second against the turn; amount from the
              look's cloud_k); False for none
    air, marks  a number or function of t: the strength of the air (rim and halo) and of the hearts and arcs
              (the Finale fades both as the logo's ring and grid draw over the Earth)
    cradle    dict(t0, t1, at=None, width=1.3, color="#ffcf8f", glow=1.0, motes=180, rise=1.5): a soft warm
              light rising from below the globe, as from hands cradling it: a pool of warm light at `at` (a
              world point or function of t; default cradle_at(t), just under the globe, where the hands go),
              motes of light drifting up in front of the globe, its lower edge warmed from below; it comes in
              over the first second after t0 and goes over the last second before t1; None for none
    n         land points (40000 a hemisphere and a half; more for a globe that fills the picture)
    bright    strength of the light (land, rim, hearts)
    """

    def __init__(self, pos=(0.0, 12.0, -40.0), radius=8.0, face="camera", camera=None, place=None, look="night",
                 blend=1.2, spin=6.0, front=-40.0, tilt=18.0, settle=None, t_in=0.0, t_out=None, fade=1.2,
                 amount=None, hearts=None, arcs=True, clouds=True, air=None, marks=None, cradle=None, n=40000,
                 bright=1.0, scale=None, seed=4):
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
        self.air, self.marks = air, marks
        self.cradle = dict(dict(at=None, width=1.3, color="#ffcf8f", glow=1.0, motes=180, rise=1.5), **cradle) \
            if cradle else None
        self.bright = float(bright)
        arc0 = dict(height=0.2, width=0.009, dur=1.0, glow=1.0)
        self.arcs = (dict(arc0, **({} if arcs is True else dict(arcs)))) if (arcs and hearts) else None
        self.clouds = (dict(drift=2.5) if clouds is True else dict(dict(drift=2.5), **clouds)) if clouds else None
        self._args = (n, hearts, seed)
        self._ready = False

    def __getattr__(self, k):
        # the land and the hearts are made on first use (not when the song file is imported)
        if k.startswith("_") or self.__dict__.get("_ready", True):
            raise AttributeError(k)
        self._build(*self._args)
        return getattr(self, k)

    def _build(self, n, hearts, seed):
        self._ready = True
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
        # how much of each ocean point's cell is land (the land's own base colour is painted there)
        rng = np.random.default_rng(seed + 12)
        half = math.degrees(self.o_cell) * 0.6
        acc = np.zeros(on)
        for _ in range(9):
            dl = (rng.random(on) - 0.5) * 2.0 * half
            dn = (rng.random(on) - 0.5) * 2.0 * half / np.maximum(np.cos(np.radians(olat)), 0.05)
            acc += land(np.clip(olat + dl, -89.9, 89.9), olon + dn)
        self.o_land = acc / 9.0
        # rim: a thin ring of soft light round the edge, and the air: a soft halo that thins outward (in the view
        # plane)
        rn = 900
        a = np.arange(rn) / rn * TAU
        self.rim_a = a
        self.rim_s = hash01(rn, seed + 2)
        an = 5000
        self.air_a = hash01(an, seed + 3) * TAU
        self.air_q = hash01(an, seed + 6) ** 1.6
        # the golden glow over the land: a few wide soft lights
        self.glow_i = np.nonzero(self.l_s < 0.05)[0]
        # clouds: wisps on an even lattice, kept where the cover is
        self.cloud_g = None
        if self.clouds:
            self.cloud_g = _noise_grid(seed + 40)
            cn = max(int(n * 0.45), 9000)
            clat, clon = fib_sphere(cn)
            cd = _grid_at(self.cloud_g, clat, clon)
            keep = cd > 0.04
            self.c_lat, self.c_lon, self.c_d = clat[keep], clon[keep], cd[keep]
            self.c_s = hash01(int(keep.sum()), seed + 7)
            self.c_cell = math.sqrt(4.0 * math.pi / cn)
        # hearts and arcs
        self.hearts = None
        if hearts:
            self._make_hearts(dict(hearts), seed)

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
        hexs = [pal[k % len(pal)] for k in range(n)]
        self.hearts = dict(v=v, t=tl, parent=parent, size=float(h.get("size", 0.15)), pulse=float(h.get("pulse", 1.0)),
                           col=np.array([lin(x) for x in hexs]),
                           paint=np.array([B.show_rgb(_disp(x)) for x in hexs]), hex=hexs, s=hash01(n, seed + 5))

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

    def _cloud_shift(self, t):
        """How far the clouds have drifted against the turn (degrees of longitude)."""
        return -float(self.clouds["drift"]) * t if self.clouds else 0.0

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
        rimd = np.asarray(L["rim"], np.float64)
        # the ocean: painted, a sphere seen from the front, lighter in the middle and toward the light; near the
        # edge it takes a little of the air's colour
        ov = self.o_v @ T.T
        op = c[None, :] + R * ov
        front, f = self._front_mask(op, c, cam, R, -0.02)
        if front.any():
            sh = np.clip(ov[front] @ sun_w, -1, 1)
            ff = np.clip(f[front], 0, 1)
            mid = ff ** 0.6
            col = L["ocean_e"] * (1 - mid[:, None]) + L["ocean_c"] * mid[:, None]
            col = col * (0.82 + 0.25 * sh[:, None])
            ol = self.o_land[front][:, None]
            col = col * (1 - ol) + L["land_base"][None, :] * ol          # under the land: its own base
            fr = ((1.0 - ff) ** 3 * 0.35 * min(L["rim_k"] * 2.0, 1.0))[:, None]
            col = col * (1 - fr) + rimd[None, :] * fr
            out.append(dict(pos=op[front], size=R * self.o_cell * 1.8, color=B.show_rgb(np.clip(col, 0, 1)),
                            alpha=np.full(int(front.sum()), 1.6 * k), kind="disc", paint=1.0, paint_light=0.05,
                            dof=0.0, fog=0.0, reflect=True, streak=0.2))
        # the land: golden light (night, space) or painted green (day); dimmer under the clouds and hidden under
        # the hearts (which are painted: light over them would pale them)
        lv = self.l_v @ T.T
        lp = c[None, :] + R * 1.002 * lv
        front, f = self._front_mask(lp, c, cam, R, 0.0)
        hearts_on = self._lit(t)
        if front.any():
            edge = np.clip(f[front] / 0.25, 0.0, 1.0)
            sh = np.clip(lv[front] @ sun_w, -1, 1)
            veil = np.ones(int(front.sum()))
            if self.cloud_g is not None:
                veil = 1.0 - 0.55 * min(L["cloud_k"] / 0.3, 1.0) * _grid_at(
                    self.cloud_g, self.l_lat[front], self.l_lon[front] - self._cloud_shift(t))
            if hearts_on is not None:
                veil = veil * (1.0 - self._heart_cover(self.l_v[front], hearts_on, t))
            if L["paint_land"] is True or (isinstance(L["paint_land"], float) and L["paint_land"] > 0.5):
                col = L["land"] * (0.85 + 0.2 * sh[:, None])
                out.append(dict(pos=lp[front], size=R * self.cell * 1.8, color=B.show_rgb(np.clip(col, 0, 1)),
                                alpha=edge * 1.6 * k, kind="disc", paint=1.0, paint_light=0.06, dof=0.0, fog=0.0,
                                streak=0.2))
            else:
                s1 = self.l_s[front]
                col = lin("#%02x%02x%02x" % tuple(int(v * 255) for v in L["land"]))
                col2 = lin("#%02x%02x%02x" % tuple(int(v * 255) for v in L["land2"]))
                cc = np.where((s1 < 0.04)[:, None], col2[None, :], col[None, :])
                br = (0.6 + 0.4 * self.l_s2[front]) * (0.7 + 0.4 * np.clip(sh, 0, 1))
                # wide soft points that run together into a smooth golden field (not a lattice of dots)
                out.append(dict(pos=lp[front], size=R * self.cell * 2.3, color=cc * 0.30 * self.bright * L["land_k"],
                                alpha=(edge * br * veil * k).astype(np.float32), kind="soft", twinkle=0.15,
                                seed=s1, dof=0.0, fog=0.0, streak=0.2))
                g = front & (self.l_s < 0.003)
                if g.any():
                    out.append(dict(pos=c[None, :] + R * 1.004 * lv[g], size=R * 0.016, color=col2 * 0.8 + col * 0.4,
                                    alpha=0.6 * k, emit=1.6, kind="spark", twinkle=1.0, seed=self.l_s2[g], dof=0.0))
                # a warm glow over the continents
                gi = self.glow_i
                gf = front[gi]
                if L["glow_k"] > 0.01 and gf.any():
                    ge = np.clip(f[gi][gf] / 0.3, 0.0, 1.0)
                    out.append(dict(pos=lp[gi][gf], size=R * self.cell * 9.0, color=col * 0.55 * self.bright,
                                    alpha=(0.05 * L["glow_k"] * ge * k).astype(np.float32), kind="soft", dof=0.0,
                                    fog=0.0, streak=0.0, seed=self.l_s2[gi][gf]))
        # clouds: soft wisps a little above the land, drifting against the turn
        if self.cloud_g is not None and L["cloud_k"] > 0.01:
            cv = _earth(self.c_lat, self.c_lon + self._cloud_shift(t)) @ T.T
            cp = c[None, :] + R * 1.012 * cv
            front, f = self._front_mask(cp, c, cam, R, 0.0)
            if front.any():
                lit = 0.55 + 0.45 * np.clip(cv[front] @ sun_w, 0, 1)
                a = self.c_d[front] * np.clip(f[front] / 0.3, 0.0, 1.0) * lit * L["cloud_k"] * k
                if hearts_on is not None and self._marks(t) > 0.0:
                    ce = _earth(self.c_lat[front], self.c_lon[front] + self._cloud_shift(t))
                    a = a * (1.0 - self._heart_cover(ce, hearts_on, t) * self._marks(t))
                cl = lin("#%02x%02x%02x" % tuple(int(v * 255) for v in L["cloud"]))
                out.append(dict(pos=cp[front], size=R * self.c_cell * 2.2, color=cl * 0.9,
                                alpha=(a * 0.55).astype(np.float32), kind="soft", dof=0.0, fog=0.0, streak=0.0,
                                seed=self.c_s[front]))
        # the air: a thin soft rim and a halo that thins outward, facing the camera
        rimc = lin("#%02x%02x%02x" % tuple(int(v * 255) for v in L["rim"]))
        e1, e2 = M[:, 0][None, :], M[:, 1][None, :]
        a = self.rim_a
        rr = 1.0 + 0.012 * self.rim_s
        ring = c[None, :] + R * rr[:, None] * (np.cos(a)[:, None] * e1 + np.sin(a)[:, None] * e2)
        ka = k * self._air(t)
        if ka > 0.0:
            out.append(dict(pos=ring, size=R * 0.03, color=rimc * self.bright, alpha=0.13 * L["rim_k"] * ka,
                            kind="soft", dof=0.0, fog=0.0, streak=0.0, seed=self.rim_s))
            q = self.air_q
            ra = 1.0 - 0.015 + 0.2 * q
            air = c[None, :] + R * ra[:, None] * (np.cos(self.air_a)[:, None] * e1 + np.sin(self.air_a)[:, None] * e2)
            out.append(dict(pos=air, size=R * 0.12, color=rimc * 0.8 * self.bright,
                            alpha=(0.018 * L["rim_k"] * ka * np.exp(-q * 2.4)).astype(np.float32), kind="soft",
                            dof=0.0, fog=0.0, streak=0.0))
        # the light rising from the hands that cradle it
        if self.cradle:
            cr = self.cradle
            kc = k * _sc(float(cr["t0"]), float(cr["t0"]) + 1.0, t) * (1.0 - _sc(float(cr["t1"]) - 1.0,
                                                                                 float(cr["t1"]), t))
            if kc > 0.0:
                out += self._cradle(t, cam, c, M, R, kc)
        # hearts and arcs
        km = k * self._marks(t)
        if self.hearts is not None and km > 0.0:
            out += self._hearts(t, cam, c, R, T, km)
        return out

    def cradle_at(self, t, cam=None):
        """The world point just under the globe at t, where hands cradling it go (the cradle's light rises
        from there unless the cradle gives its own `at`)."""
        if cam is None and self.camera is not None:
            cam = self.camera.state(t) if hasattr(self.camera, "state") else self.camera(t)
        c, M, R = self._view(t, cam)
        return c - np.array([0.0, 1.0, 0.0]) * R * 1.08

    def _cradle(self, t, cam, c, M, R, kc):
        cr = self.cradle
        at = cr["at"]
        base = np.asarray(_val(at, t), np.float64) if at is not None else c - np.array([0.0, 1.0, 0.0]) * R * 1.08
        col = lin(cr["color"])
        g = float(cr["glow"])
        right, upv, fwd = M[:, 0], np.array([0.0, 1.0, 0.0]), M[:, 2]
        wd = float(cr["width"]) * R
        out = []
        # a pool of warm light where the hands are
        xs = np.linspace(-0.5, 0.5, 9) * wd
        pool = base[None, :] + xs[:, None] * right[None, :]
        out.append(dict(pos=pool, size=R * 0.42, color=col * 0.6 * g, alpha=np.full(9, 0.07 * kc), kind="soft",
                        dof=0.0, fog=0.0, streak=0.0, reflect=False))
        # a soft column of that light rising to the globe and up its front, thinning as it goes
        h = np.linspace(0.0, 1.0, 14)
        col_p = base[None, :] + (h * 0.9 * R)[:, None] * upv[None, :] + (0.3 * R) * fwd[None, :]
        out.append(dict(pos=col_p, size=R * (0.30 + 0.25 * h), color=col * 0.55 * g,
                        alpha=(0.05 * kc * (1.0 - h) ** 1.3).astype(np.float32), kind="soft", dof=0.0, fog=0.0,
                        streak=0.0, reflect=False))
        # motes of light drifting up in front of the globe
        m = int(cr["motes"])
        s1, s2, s3 = hash01(m, 91), hash01(m, 92), hash01(m, 93)
        rise = float(cr["rise"]) * R
        speed = (0.10 + 0.08 * s2) * R
        life = np.mod(t * speed / rise + s1, 1.0)
        x = (s3 - 0.5) * wd * (1.0 - 0.35 * life) + 0.04 * R * np.sin(t * 1.3 + s2 * 20.0)
        pos = base[None, :] + x[:, None] * right[None, :] + (life * rise)[:, None] * upv[None, :] \
            + (R * (0.25 + 0.6 * s1))[:, None] * fwd[None, :]
        a = np.sin(np.pi * life) ** 1.5 * kc
        out.append(dict(pos=pos, size=R * 0.010 * (0.7 + 0.6 * s2), color=col * 1.5 * g, alpha=a * 0.8, emit=1.6,
                        kind="spark", twinkle=0.8, seed=s3, dof=0.0, fog=0.0, reflect=False))
        out.append(dict(pos=pos, size=R * 0.05, color=col * 0.5 * g, alpha=a * 0.10, kind="soft", dof=0.0, fog=0.0,
                        streak=0.0, reflect=False))
        # the globe's lower edge warmed from below
        ang = np.radians(np.linspace(200.0, 340.0, 60))
        w = np.sin((ang - ang[0]) / (ang[-1] - ang[0]) * np.pi)
        rim = c[None, :] + R * 0.985 * (np.cos(ang)[:, None] * right[None, :] + np.sin(ang)[:, None] * M[:, 1][None, :])
        out.append(dict(pos=rim, size=R * 0.16, color=col * 0.8 * g, alpha=0.11 * kc * w, kind="soft", dof=0.0,
                        fog=0.0, streak=0.0, reflect=False))
        return out

    def _air(self, t):
        return float(np.clip(_val(self.air, t), 0.0, 1.0)) if self.air is not None else 1.0

    def _marks(self, t):
        return float(np.clip(_val(self.marks, t), 0.0, 1.0)) if self.marks is not None else 1.0

    def _lit(self, t):
        """The hearts lit at t: (indices, their age, their size in radii now); None when none."""
        if self.hearts is None:
            return None
        H = self.hearts
        age = t - H["t"]
        idx = np.nonzero(age > -0.05)[0]
        if not len(idx):
            return None
        ag = np.maximum(age[idx], 0.0)
        g = np.clip(ag / 0.55, 0.0, 1.0)
        x = g - 1.0
        pop = np.clip(1.0 + 2.2 * x ** 3 + 1.2 * x ** 2, 0.0, None)          # opens with a little overshoot
        return idx, ag, H["size"] * pop

    def _heart_cover(self, v, lit, t):
        """0..1: how much of each Earth-frame direction v (n, 3) lies under a lit heart."""
        idx, ag, sz = lit
        d = np.arccos(np.clip(v @ self.hearts["v"][idx].T, -1.0, 1.0))         # (n, lit)
        cov = np.clip((sz[None, :] * 0.8 - d) / np.maximum(sz[None, :] * 0.3, 1e-4), 0.0, 1.0)
        return cov.max(axis=1)

    def _hearts(self, t, cam, c, R, T, k):
        H = self.hearts
        out = []
        age = t - H["t"]
        if self.arcs:
            dur = float(self.arcs.get("dur", 1.0))
            hgt = float(self.arcs.get("height", 0.2))
            wid = float(self.arcs.get("width", 0.009))
            glow = float(self.arcs.get("glow", 1.0))
            P0, P1, A0, A1, C, heads, head_c = [], [], [], [], [], [], []
            m = 32
            for j in np.nonzero(age > -dur)[0]:
                p = H["parent"][j]
                if p < 0:
                    continue
                g = _sc(-dur, 0.0, age[j])                      # the arc travels and arrives as the heart lights
                if g <= 0.0:
                    continue
                fade = 0.45 + 0.55 * math.exp(-max(age[j], 0.0) / 2.5)
                a, b = H["v"][p], H["v"][j]
                ang = math.acos(float(np.clip(a @ b, -1, 1)))
                us = np.linspace(0.0, g, m)
                pts = _slerp_many(a, b, us)
                lift = 1.0 + (0.04 + hgt * min(ang / 1.2, 1.0)) * np.sin(np.pi * us) ** 0.9
                wpts = c[None, :] + R * (pts * lift[:, None]) @ T.T
                um = 0.5 * (us[:-1] + us[1:])
                cc = H["col"][p][None, :] * (1 - um[:, None]) + H["col"][j][None, :] * um[:, None]
                al = np.full(m, fade * k) * np.clip((us - us[0]) / max(g, 1e-6) * 3.0, 0.15, 1.0)
                al[self._occluded(wpts, c, cam, R)] = 0.0
                P0.append(wpts[:-1])
                P1.append(wpts[1:])
                A0.append(al[:-1])
                A1.append(al[1:])
                C.append(cc)
                if g < 0.999 and al[-1] > 0.0:
                    heads.append(wpts[-1])
                    head_c.append(H["col"][j])
            if P0:
                p0, p1, a0, a1, cc = np.vstack(P0), np.vstack(P1), np.concatenate(A0), np.concatenate(A1), np.vstack(C)
                out.append(dict(pos=p0, pos2=p1, size=R * wid, alpha=a0, alpha2=a1, color=cc * 2.2 * self.bright,
                                kind="ribbon", dof=0.0, fog=0.0, reflect=False, pulse=(R * 0.8, R * 0.25, 1.5, R * 2.0)))
                if glow > 0:
                    out.append(dict(pos=p0, pos2=p1, size=R * wid * 4.0, alpha=a0 * 0.10 * glow, alpha2=a1 * 0.10 * glow,
                                    color=cc * 1.2 * self.bright, kind="ribbon", dof=0.0, fog=0.0, reflect=False))
            if heads:
                hp, hc = np.array(heads), np.array(head_c)
                out.append(dict(pos=hp, size=R * 0.022, color=hc * 0.6 + 0.9, alpha=np.full(len(hp), 0.9 * k), emit=2.5,
                                kind="spark", dof=0.0, fog=0.0, reflect=False))
                out.append(dict(pos=hp, size=R * 0.09, color=hc * 0.8, alpha=np.full(len(hp), 0.18 * k), kind="soft",
                                dof=0.0, fog=0.0, streak=0.0, reflect=False))
        lit = self._lit(t)
        if lit is not None:
            idx, ag, sz = lit
            v = H["v"][idx] @ T.T
            wp = c[None, :] + R * 1.02 * v
            front, f = self._front_mask(wp, c, cam, R, 0.0)
            a_ = np.clip(ag / 0.12, 0.0, 1.0) * np.clip(f / 0.22, 0.0, 1.0) * k * (age[idx] > -0.0)
            sel = front & (a_ > 0.003)
            if sel.any():
                size = R * sz
                col = H["col"][idx]
                deep = col / np.maximum(col.max(axis=1, keepdims=True), 1e-6)
                # the heart itself, painted in its exact colour (with a little of its own light)
                out.append(dict(pos=wp[sel], size=size[sel], color=H["paint"][idx][sel], alpha=(1.6 * a_)[sel],
                                kind="heart", paint=1.0, paint_light=0.12, dof=0.0, fog=0.0, seed=H["s"][idx][sel]))
                # a soft halo of its colour, and the pulse of light as it opens
                out.append(dict(pos=wp[sel], size=size[sel] * 2.6, color=(deep * 0.55 * self.bright)[sel],
                                alpha=a_[sel] * 0.07, kind="soft", dof=0.0, fog=0.0, streak=0.0, reflect=False))
                q = np.clip(ag / 1.1, 0.0, 1.0)
                pl = sel & (q < 1.0)
                if pl.any() and H["pulse"] > 0:
                    out.append(dict(pos=wp[pl], size=(size * (1.4 + 4.0 * q ** 0.7))[pl],
                                    color=(deep * 0.9 * self.bright)[pl],
                                    alpha=(a_ * 0.5 * H["pulse"] * (1.0 - q) ** 2)[pl], kind="soft", dof=0.0, fog=0.0,
                                    streak=0.0, reflect=False))
                fl = sel & (ag < 0.4)
                if fl.any():
                    out.append(dict(pos=wp[fl], size=size[fl] * 0.5, color=deep[fl] * 0.5 + 0.9,
                                    alpha=np.exp(-ag[fl] / 0.12) * k * 0.8, emit=2.5, kind="spark", dof=0.0))
        return out

    def where(self, t, cam=None):
        """The globe's centre and radius in the world at t."""
        if cam is None and self.camera is not None:
            cam = self.camera.state(t) if hasattr(self.camera, "state") else self.camera(t)
        c, M, R = self._view(t, cam)
        return c, R


class _Bloom:
    """A soft spreading light from a point: the globe blooming into day."""

    def __init__(self, at, t, dur, radius, color="#ffd9b4", glow=0.5):
        self.at, self.t, self.dur, self.r, self.col = at, float(t), float(dur), float(radius), lin(color) * glow / 0.5
        self.gold = lin("#ffc27a") * glow / 0.5
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
        rad = self.r * (1.05 + 2.5 * max(u, 0.0)) * (0.75 + 0.5 * self.s2)      # from the globe's edge outward
        p = c[None, :] + rad[:, None] * (self.dir[:, 0:1] * r[None, :] + self.dir[:, 1:2] * up[None, :])
        col = np.where((self.s2 < 0.5)[:, None], self.col[None, :], self.gold[None, :]) * 1.3   # peach and gold
        return [dict(pos=p, size=self.r * 0.05, color=col, alpha=0.22 * k, emit=1.6, kind="spark",
                     twinkle=1.0, seed=self.s, dof=0.0, reflect=False)]


class Finale:
    """World to logo: the globe of light settles and becomes the campaign logo, light blooms from it into a soft
    pastel day, and the logo rises into the end card's place.

    pos, radius       the globe's centre and radius (metres); camera: the song's Rig (needed)
    look              the globe's look before the bloom ("night", "space" or "day")
    t_world           when the globe forms (its light gathers over 1.2 s); spin, front, tilt as Globe
    hearts            dict(t0, t1, n=42, ...) as Globe (False for none); the hearts and arcs fade as the logo forms
    t_settle          (t0, t1): the globe slows and stops, its pole swinging to the logo's pole
    t_logo            (t0, t1): it becomes the logo; the logo is whole at t1 (54.3 to 55.0 in the films; give
                      about 2 s: (53.0, 55.0)). In order (shares of t_logo, `timing` changes any): the two hearts
                      sweep in from either side behind the Earth (0 to 0.54), the ring draws round it (0.15 to
                      0.5), the grid lines draw themselves over the Earth (0.2 to 0.65), the logo's globe spreads
                      over the Earth from its middle (0.5 to 0.78) while the Earth's lights fade (0.62 to 0.88),
                      the olive branches grow (0.58 to 1.0)
    timing            dict(part=(start, end)) in shares of t_logo, for any of heart_l, heart_r, ring, grid,
                      globe, branch_l, branch_r
    shrink            the globe draws in to this share of its size as it settles (0.6), so the whole logo fits
    bloom             dict(t=54.3, dur=1.0, strength=0.12, glow=0.5, color="#ffd9b4"): warm pastel light blooms
                      from the globe (a flash of `strength`, capped at 0.3 so it never whites out, P3D bursts, and
                      peach and gold sparks spreading, `glow`, capped at 1); the
                      world turns to the pastel day `look_after` round t (its blend `blend` seconds); None for no
                      bloom (then give the world's look yourself)
    end               dict(t=(55.0, 56.4), ride=(0.5, 0.78, 14.0), frac=0.22): the logo glides from where the globe
                      was to that place of the picture (x, y from the left and the bottom, metres ahead of the lens)
                      and size (a share of the picture's height) and stays there; None keeps it where it formed
    paint             the logo's paint over time (default 1.0: painted in its exact colours all the way, so its
                      hearts keep their true gold to orange and rose at night and on the day)
    glow              a soft halo of the hearts' own colours round the painted logo (Logo paint_glow; default
                      0: painted clean, which reads best); a number or function of t
    clouds            the Earth's cloud wisps (True)
    cradle            as Globe: a soft warm light rising from below the globe, as from hands cradling it (the
                      hands go at fin.globe.cradle_at(t), or give the cradle your own `at`)
    logo              dict of other brand.Logo keys (bright, white, glow, sparkle, palette, n, ...)

    Use: fin.add_to(scene) in the song's setup; P3D world=fin.world(dict(...)) (adds the pastel look at the bloom
    and the burst); P3D bursts=fin.bursts() (or fin.world does it for you with world_bursts=True).
    fin.globe and fin.logo are the two point sets; fin.logo_place is the logo's Place.
    """

    BLOOM = dict(t=54.3, dur=1.0, strength=0.12, color="#ffd9b4", glow=0.5)
    MAX_FLASH = 0.3            # the bloom's flash is capped: it can never white out the picture

    def __init__(self, pos=(0.0, 12.0, -40.0), radius=8.0, camera=None, look="night", t_world=49.5, spin=6.0,
                 front=-40.0, tilt=18.0, hearts=None, t_settle=(52.6, 54.0), t_logo=(53.4, 55.0), shrink=0.6,
                 bloom=None, end=None, look_after="pastel", blend=0.9, paint=None, glow=None, timing=None,
                 logo=None, clouds=True, cradle=None, n=40000):
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
        # the order of the change (shares of t_logo): the hearts sweep in behind the Earth (0 to 0.54), its ring
        # draws round it (0.15 to 0.5), the grid lines draw themselves over the Earth (0.2 to 0.65), the logo's
        # globe spreads over it from the middle (0.5 to 0.78) as the Earth's lights fade (0.62 to 0.88), the
        # branches grow (0.58 to 1.0)
        tm = dict(dict(heart_l=(0.0, 0.50), heart_r=(0.04, 0.54), ring=(0.15, 0.50), grid=(0.20, 0.65),
                       globe=(0.50, 0.78), branch_l=(0.62, 1.0), branch_r=(0.58, 0.96)), **(timing or {}))
        self.timing = tm

        def scale(t):                            # the globe draws in a little as it settles: room for the hearts
            return 1.0 - (1.0 - self.shrink) * _sc(s0 - 0.4, s1, t)

        self.scale = scale
        # the globe: strong until the logo's own globe has spread over it (from its middle out), then its lights
        # (land, clouds, air, arcs) fade over the logo's colours
        fade_a, fade_b = l0 + (tm["globe"][0] + 0.12) * w, l0 + (tm["globe"][1] + 0.10) * w
        self.globe = Globe(pos=tuple(self.pos), radius=self.R, camera=camera, look=look, spin=spin, front=front,
                           tilt=tilt, settle=dict(t0=s0, t1=s1, pole=tuple(B.POLE)), scale=scale,
                           amount=lambda t: _sc(self.t_world, self.t_world + 1.2, t) * (1.0 - _sc(fade_a, fade_b, t)),
                           hearts=hearts, clouds=clouds, cradle=cradle, n=n,
                           # the logo's ring takes the place of the air; the hearts and arcs give way to the grid
                           air=lambda t: 1.0 - _sc(l0 + tm["ring"][0] * w, l0 + tm["ring"][1] * w, t),
                           marks=lambda t: 1.0 - _sc(l0 + 0.10 * w, l0 + 0.50 * w, t))
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
        def ramp(name):
            a, b = tm[name]
            if name in ("heart_l", "heart_r", "globe"):
                return lambda t: _sc(l0 + a * w, l0 + b * w, t)
            return lambda t: float(np.clip((t - (l0 + a * w)) / max((b - a) * w, 1e-6), 0, 1))
        amt = {name: ramp(name) for name in tm}
        bt = self.bloom["t"] if self.bloom else l1
        if paint is None:
            paint = 1.0            # painted in its exact colours all the way: true on the night sky and the day
        if glow is None:
            glow = 0.0             # painted clean: any halo round them reads as a neon or burnt edge
        kw = dict(bright=0.5, white=0.45, glow=0.25, sparkle=0.06, n=90000)
        kw.update(logo or {})
        # the Earth stands where the logo's globe goes until the logo is whole: the hearts pass behind it
        self.logo = B.Logo(place=self.logo_place, camera=camera, t_in=l0, t_full=l1, arrive="build", amount=amt,
                           paint=paint, paint_glow=glow, globe_cover=lambda t: 1.0 - _sc(l1, l1 + 0.3, t), **kw)

    def add_to(self, scene, name="finale"):
        scene.add(name + " globe", self.globe)
        scene.add(name + " logo", self.logo)
        if self.bloom and self.bloom.get("glow", 0.5) > 0:
            b = self.bloom
            scene.add(name + " bloom", _Bloom(self.pos, b["t"], b["dur"], self.R * self.shrink,
                                              b.get("color", "#ffd9b4"), min(float(b.get("glow", 0.5)), 1.0)),
                      reflect=False)

    def bursts(self):
        """The bloom's flash of light (P3D bursts); empty with strength 0."""
        if not self.bloom or float(self.bloom.get("strength", 0.12)) <= 0:
            return []
        b = self.bloom
        return [dict(t=b["t"] + 0.1 * b["dur"], strength=min(float(b.get("strength", 0.12)), self.MAX_FLASH),
                     rise=0.3 * b["dur"], fall=0.55 * b["dur"], color=b.get("color", "#ffd9b4"), at=tuple(self.pos),
                     radius=0.25)]

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
