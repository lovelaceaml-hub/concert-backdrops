"""Pieces for the style presets of engine/p3d/styles.py: small point sets that dress a figure (pure numpy).

  Dressed(pointset, **settings)   the same point set with settings put on every batch it draws (paint, dof...);
                                  every other attribute (where, frame, effect...) is passed through
  Backdrop(target, ...)           a soft glow standing behind a figure as seen from the camera, so a dark
                                  silhouette reads on a night sky (a low moon, a lit mist)
  Butterflies(around, ...)        small glowing butterflies with beating wings that leave a figure and flutter
                                  round it, each with a faint trail of dust (p02)
  Sparkles(center, ...)           four-point stars and fine dust scattered round a figure (p02, p08)
  GlitterMist(center, ...)        a wide slab of glittering mist and bokeh round a small figure (p09, ref 09)
  CloudPuffs(source, ...)         soft billows of painted cloud that spill out of a shape (p07): dark slate
                                  in shadow, the light's colour where they face it
Everything is a pure function of time.
"""
import numpy as np

from . import bodymath as bm
from .api import hash01, lin
from .api import show as _show


def _val(v, t):
    return v(t) if callable(v) else v


def _col(c):
    return lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


def _pt(v, t):
    v = _val(v, t)
    if hasattr(v, "sample") and hasattr(v, "where"):
        raise TypeError("give a point or a function of time, not a point set")
    return np.asarray(v, np.float64).reshape(3)


class Dressed:
    """A point set whose batches all get the same settings (or a function batch -> batch).

    Dressed(body, paint=0.7, paint_light=1.0)   a glitter body that is also painted: dark grains show on a
                                                bright sky. Any other attribute is the wrapped set's own.
    `ways`: a list of dicts draws every batch once per dict (a painted dark copy and a copy of light).
    `kinds`: only batches of these kinds are changed (the others pass as they are)."""

    def __init__(self, pointset, fn=None, ways=None, kinds=None, **settings):
        self.ps = pointset
        self.fn = fn
        self.ways = [dict(w) for w in ways] if ways else None
        self.kinds = None if kinds is None else set(kinds)
        self.settings = settings
        self.wants_camera = getattr(pointset, "wants_camera", False)

    def __getattr__(self, name):
        if name == "ps":
            raise AttributeError(name)
        return getattr(self.ps, name)

    def sample(self, t, cam=None):
        res = self.ps.sample(t, cam) if self.wants_camera else self.ps.sample(t)
        bs = res if isinstance(res, (list, tuple)) else [res]
        out = []
        for b in bs:
            if b is None:
                continue
            if self.kinds is not None and b.get("kind", "soft") not in self.kinds:
                out.append(b)
                continue
            b = dict(b, **self.settings)
            if self.fn is not None:
                b = self.fn(b)
                if b is None:
                    continue
            if self.ways:
                out += [dict(b, **w) for w in self.ways]
            else:
                out.append(b)
        return out


class Backdrop:
    """A soft glow behind a figure, as the camera sees it: it stands `behind` metres beyond `target` on the line
    from the camera, so it is always behind the figure, whatever the camera does.

    target   a point (x, y, z) or a function of time; radius: metres; color, color2 (display hex); bright
    wisps    0..1: streaks of lit mist across the glow; n: sprites (smooth glow from many medium discs)"""
    wants_camera = True

    def __init__(self, target, radius=1.4, behind=3.0, color="#ffd9a8", color2="#8fb0ff", bright=1.0, wisps=0.6,
                 n=700, show=None, flat=0.35, seed=1.0):
        self.target, self.radius, self.behind = target, radius, behind
        self.color, self.color2 = _col(color), _col(color2)
        self.bright, self.wisps, self.n, self.flat = bright, float(wisps), int(n), float(flat)
        self.show = show
        self.seed = float(seed)
        k = int(seed * 100)
        r1, r2, r3, r4 = (hash01(self.n, k + i).astype(np.float64) for i in range(4))
        # a gaussian disc of glow, a few streaks of mist through it
        rad = np.sqrt(-2.0 * np.log(np.maximum(1.0 - r1 * 0.97, 1e-6))) * 0.42
        ang = r2 * 2 * np.pi
        self.xy = np.stack([np.cos(ang) * rad, np.sin(ang) * rad * (1.0 - self.flat * 0.5)], axis=1)
        self.r3, self.r4 = r3, r4
        self.size = (0.30 + 0.35 * r3)

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 0.6)) * (1.0 - float(bm.ramp(t, self.show[1] - 0.6, self.show[1])))

    def sample(self, t, cam=None):
        if cam is None:
            return []
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        c = _pt(self.target, t)
        eye = np.asarray(cam.pos, np.float64)
        d = c - eye
        dist = np.linalg.norm(d)
        f = d / max(dist, 1e-6)
        r, u, _f = cam.basis()
        cen = c + f * self.behind
        R = float(_val(self.radius, t)) * (dist + self.behind) / max(dist, 1e-6)
        drift = np.stack([np.sin(t * 0.13 + self.r4 * 9), np.cos(t * 0.11 + self.r3 * 7)], axis=1) * 0.03
        xy = (self.xy + drift) * R
        pos = cen[None] + xy[:, :1] * np.asarray(r)[None] + xy[:, 1:] * np.asarray(u)[None]
        mix = np.clip(np.linalg.norm(self.xy, axis=1) / 0.9, 0, 1)[:, None] ** 1.5
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        a = 0.010 * self.bright * np.ones(self.n)
        out = [dict(pos=pos, size=self.size * R * 0.55, color=col, alpha=a, kind="soft", dof=0.0, fog=0.0,
                    reflect=False, lod=False)]
        if self.wisps > 0:
            m = 160
            rr = hash01(m, 90).astype(np.float64)
            rr2 = hash01(m, 91).astype(np.float64)
            x = (rr - 0.5) * 2.4 + 0.06 * np.sin(t * 0.2 + rr2 * 6)
            y = (rr2 - 0.5) * 0.6 + 0.12 * np.sin(rr * 9.0)
            pos2 = cen[None] + (x * R)[:, None] * np.asarray(r)[None] + (y * R)[:, None] * np.asarray(u)[None]
            out.append(dict(pos=pos2, size=0.16 * R, color=self.color * 0.8 + self.color2 * 0.2,
                            alpha=0.018 * self.wisps * self.bright * np.exp(-x * x * 0.8), kind="soft", dof=0.0,
                            fog=0.0, reflect=False, lod=False))
        return out


def _project_dir(cam, p, v):
    """The heading in the picture (radians, 0 = up the screen) of points p moving with velocity v."""
    r, u, f = cam.basis()
    r, u = np.asarray(r), np.asarray(u)
    return np.arctan2(-(v @ r), v @ u)


class Butterflies:
    """Small glowing butterflies (p02): each leaves the figure (or is there from the start) and flutters round it
    on a wandering loop, wings beating, a faint trail of dust behind it.

    around   the middle of their flight: a point or a function of time (a Body place: lambda t: b.where(t, "chest"))
    radius   (r0, r1) metres of the loops; height: (low, high) metres about `around`
    n        how many; size: metres across the wings; speed: metres per second
    t        when they leave the figure (each a little after the last, over `spread` seconds); None: all there
    source   a function t -> (K, 3) points they leave from (a body's shape_points), or None (from `around`)
    color, color2, bright, trail (0..1), paint (0..1: also painted, for day skies)"""
    wants_camera = True

    def __init__(self, around, radius=(0.35, 0.9), height=(-0.4, 0.5), n=12, size=0.05, speed=0.45, t=None, spread=2.0,
                 source=None, color="#ffe3b0", color2="#ffb8d0", bright=1.0, trail=1.0, paint=0.0, show=None, seed=1.0):
        self.around, self.radius, self.height = around, radius, height
        self.n, self.size, self.speed = int(n), float(size), float(speed)
        self.t0, self.spread, self.source = t, float(spread), source
        self.color, self.color2 = _col(color), _col(color2)
        self.bright, self.trail, self.paint = float(bright), float(trail), float(paint)
        self.show = show
        k = int(seed * 100)
        self.r = [hash01(self.n, k + i).astype(np.float64) for i in range(8)]

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 0.5)) * (1.0 - float(bm.ramp(t, self.show[1] - 0.5, self.show[1])))

    def _pos(self, t):
        """(n, 3) places and how far each has left its start (0..1)."""
        r = self.r
        c = _pt(self.around, t)
        R = self.radius[0] + (self.radius[1] - self.radius[0]) * r[0]
        w = self.speed / np.maximum(R, 0.05) * np.where(r[1] < 0.5, -1.0, 1.0) * (0.7 + 0.6 * r[2])
        ph = r[3] * 2 * np.pi
        y = self.height[0] + (self.height[1] - self.height[0]) * r[4]
        a = ph + w * t
        wob = np.stack([np.sin(t * (1.3 + r[5]) + r[6] * 9), np.sin(t * (1.7 + r[6]) + r[7] * 7),
                        np.sin(t * (1.1 + r[7]) + r[5] * 5)], axis=1)
        loop = np.stack([np.cos(a) * R, y + 0.18 * np.sin(a * 2.0 + r[5] * 4) * R, np.sin(a) * R * 0.75], axis=1)
        p = c[None] + loop + wob * 0.10 * R[:, None]
        if self.t0 is None:
            return p, np.ones(self.n)
        tb = self.t0 + self.spread * r[2]
        u = bm.smoother((t - tb) / 1.6)
        if self.source is not None:
            src = np.asarray(self.source(min(t, float(tb.max()))), np.float64)
            p0 = src[(r[6] * len(src)).astype(np.int64) % len(src)]
        else:
            p0 = np.broadcast_to(c, p.shape)
        return p0 * (1 - u[:, None]) + p * u[:, None], u * (t >= tb)

    def sample(self, t, cam=None):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        p, out_u = self._pos(t)
        dt = 0.04
        p2, _ = self._pos(t + dt)
        v = (p2 - p) / dt
        rot = np.zeros((self.n, 2))
        if cam is not None:
            rot[:, 0] = _project_dir(cam, p, v)
        rot[:, 1] = 0.45 * np.sin(t * 1.3 + self.r[4] * 9)
        vis = np.clip(out_u * 3.0, 0, 1) if self.t0 is not None else np.ones(self.n)
        mix = (self.r[5] ** 2)[:, None]
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        size = self.size * (0.75 + 0.5 * self.r[7])
        out = [dict(pos=p, size=size, color=col, alpha=0.70 * self.bright * vis, emit=1.0, kind="butterfly", rot=rot,
                    seed=self.r[0], twinkle=0.15, paint=self.paint, paint_light=0.8)]
        # a faint glow round each and a trail of dust behind
        out.append(dict(pos=p, size=size * 2.2, color=col, alpha=0.06 * self.bright * vis, kind="soft"))
        if self.trail > 0:
            K = 26
            ages = np.linspace(0.05, 1.6, K)
            pts = np.concatenate([self._pos(t - a)[0] for a in ages])
            ag = np.repeat(ages, self.n)
            jit = bm.flow(pts * 6.0, t * 0.5, speed=1.0, seed=3.0) * (0.02 + 0.05 * ag)[:, None]
            vv = np.tile(vis, K)
            out.append(dict(pos=pts + jit + np.array([0.0, -0.05, 0.0]) * ag[:, None], size=np.tile(size, K) * 0.10,
                            color=np.tile(col, (K, 1)), alpha=0.45 * self.trail * self.bright * vv * (1.0 - ag / 1.7) ** 2,
                            emit=1.0 + 2.0 * (hash01(len(pts), 5) > 0.9), kind="soft", twinkle=0.9))
        return out


class Sparkles:
    """Four-point stars and fine dust scattered round a figure (p02's stars, p08's flying glitter).

    center   a point or function of time; box: (half width, half height, half depth) metres
    n        how many dust points; stars: how many four-point stars; size: metres of a star
    color, color2, bright, drift (metres per second upward), paint (0..1)"""

    def __init__(self, center, box=(1.0, 1.0, 0.6), n=900, stars=40, size=0.05, color="#fff1d0", color2="#ffc9a0",
                 bright=1.0, drift=0.03, paint=0.0, show=None, seed=1.0):
        self.center, self.box = center, np.asarray(box, np.float64)
        self.n, self.stars, self.size = int(n), int(stars), float(size)
        self.color, self.color2 = _col(color), _col(color2)
        self.bright, self.drift, self.paint = float(bright), float(drift), float(paint)
        self.show = show
        k = int(seed * 100)
        m = self.n + self.stars
        self.u = np.stack([hash01(m, k + i).astype(np.float64) for i in range(3)], axis=1) * 2.0 - 1.0
        self.r = hash01(m, k + 5).astype(np.float64)

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 0.5)) * (1.0 - float(bm.ramp(t, self.show[1] - 0.5, self.show[1])))

    def sample(self, t):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        c = _pt(self.center, t)
        q = self.u.copy()
        q[:, 1] = np.mod(q[:, 1] + 1.0 + self.drift * t / max(self.box[1], 1e-3), 2.0) - 1.0
        edge = np.clip((1.0 - np.abs(q[:, 1])) / 0.2, 0, 1)
        p = c[None] + q * self.box[None] + bm.flow(q * 2.0, t * 0.3, speed=1.0, seed=2.0) * 0.04
        n = self.n
        mix = (self.r ** 2)[:, None]
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        out = [dict(pos=p[:n], size=self.size * 0.12 * (0.5 + self.r[:n]), color=col[:n],
                    alpha=0.5 * self.bright * edge[:n], emit=1.0 + 2.0 * (self.r[:n] > 0.97), kind="soft",
                    twinkle=0.9, paint=self.paint * 0.5, paint_light=1.0)]
        if self.stars:
            s = slice(n, None)
            out.append(dict(pos=p[s], size=self.size * (0.4 + 0.9 * self.r[s] ** 2), color=col[s],
                            alpha=0.9 * self.bright * edge[s], emit=2.5 + 3.0 * self.r[s], kind="spark",
                            twinkle=0.8, paint=self.paint, paint_light=1.0))
        return out


class GlitterMist:
    """A wide slab of glittering mist round a small figure (p09, ref 09): fine sparkling points densest at the
    figure's height, thinning up and down, many out of focus, warm on one side and cool on the other.

    center   a point or function of time; size: (width, height, depth) metres of the slab
    n        points; color (warm side), color2 (cool side), toward: the direction (x, z) of the warm side;
             paint (0..1): also painted, for a bright sky"""

    def __init__(self, center, size=(14.0, 3.0, 10.0), n=26000, color="#ffd29a", color2="#bcd4ff", toward=(1.0, 0.0),
                 bright=1.0, grain=0.018, drift=0.06, show=None, paint=0.0, seed=1.0):
        self.center, self.dims = center, np.asarray(size, np.float64)
        self.n = int(n)
        self.color, self.color2 = _col(color), _col(color2)
        tw = np.asarray(toward, np.float64)
        self.toward = tw / max(np.linalg.norm(tw), 1e-6)
        self.bright, self.grain, self.drift = float(bright), float(grain), float(drift)
        self.paint = float(paint)
        self.show = show
        k = int(seed * 100)
        u = np.stack([hash01(self.n, k + i).astype(np.float64) for i in range(3)], axis=1) - 0.5
        g = hash01(self.n, k + 4).astype(np.float64)
        u[:, 1] = np.sign(u[:, 1]) * (np.abs(u[:, 1]) * 2.0) ** 2.2 * 0.5        # dense at the figure's height
        self.u, self.g = u, g

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 0.8)) * (1.0 - float(bm.ramp(t, self.show[1] - 0.8, self.show[1])))

    def sample(self, t):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        c = _pt(self.center, t)
        q = self.u.copy()
        q[:, 0] = np.mod(q[:, 0] + 0.5 + self.drift * t / self.dims[0], 1.0) - 0.5
        p = c[None] + q * self.dims[None]
        p += bm.flow(q * 3.0, t * 0.2, speed=1.0, seed=4.0) * 0.08
        side = np.clip(0.5 + 1.2 * (q[:, 0] * self.toward[0] + q[:, 2] * self.toward[1]), 0, 1)[:, None]
        col = self.color2[None] * (1 - side) + self.color[None] * side
        fade = np.clip((0.5 - np.abs(q[:, 0])) / 0.12, 0, 1) * np.clip((0.5 - np.abs(q[:, 2])) / 0.12, 0, 1)
        a = 0.16 * self.bright * fade * (0.6 + 0.8 * side[:, 0]) * np.exp(-np.abs(q[:, 1]) * 4.0)
        return [dict(pos=p, size=self.grain * (0.5 + 1.5 * self.g ** 4), color=col, alpha=a,
                     emit=1.0 + 3.0 * (self.g > 0.985), kind="soft", twinkle=0.9, backlight=0.6, dof=0.55,
                     reflect=False, paint=self.paint, paint_light=1.0)]


class CloudPuffs:
    """Soft billows of cloud that spill out of a shape (p07): painted, so they are darker than a pale sky,
    slate blue in shadow and the light's colour where they face a light inside.

    source   a function t -> (K, 3) points where the billows sit (the back of a head, the shoulders)
    light    a point or a function of time: the light inside; color: its colour; shade: the shadow colour
    n        how many puffs; size: metres; spread: metres they reach out from the source"""
    wants_camera = True

    def __init__(self, source, light, n=700, size=0.10, spread=0.10, color="#ff9a48", shade="#3b4560",
                 lit=1.0, paint=0.85, bright=1.0, alpha=0.4, show=None, seed=1.0):
        self.source, self.light = source, light
        self.n, self.size, self.spread = int(n), float(size), float(spread)
        self.color = _col(color)
        self.shade = _show(shade) if isinstance(shade, str) else np.asarray(shade, np.float64)
        self.lit, self.paint, self.bright, self.alpha = float(lit), float(paint), float(bright), float(alpha)
        self.show_ = show
        k = int(seed * 100)
        self.r = [hash01(self.n, k + i).astype(np.float64) for i in range(6)]

    def gain(self, t):
        if self.show_ is None:
            return 1.0
        return float(bm.ramp(t, self.show_[0], self.show_[0] + 0.8)) * (1.0 - float(bm.ramp(t, self.show_[1] - 0.8, self.show_[1])))

    def sample(self, t, cam=None):
        if self.show_ is not None and not (self.show_[0] <= t <= self.show_[1]):
            return []
        src = np.asarray(self.source(t), np.float64)
        if len(src) == 0:
            return []
        r = self.r
        p0 = src[(r[0] * len(src)).astype(np.int64) % len(src)]
        out = np.stack([r[1] - 0.5, r[2] - 0.35, r[3] - 0.5], axis=1)
        p = p0 + out * self.spread * 2.0 + bm.flow(p0 * 3.0, t * 0.25, speed=1.0, seed=5.0) * self.spread * 0.4
        L = _pt(self.light, t)
        d = p - L
        dist = np.linalg.norm(d, axis=1)
        nrm = out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-6)
        face = np.clip(-(nrm * d).sum(1) / np.maximum(dist, 1e-6) * 0.5 + 0.5, 0, 1)
        warm = self.lit * face ** 1.5 / (1.0 + (dist / (3.0 * self.size)) ** 2)
        warm = np.minimum(warm, 0.8)
        col = self.shade[None] * (0.8 + 0.4 * r[4][:, None]) + self.color[None] * warm[:, None] * 1.5
        size = self.size * (0.5 + 1.0 * r[5] ** 1.5)
        order = np.argsort(-np.linalg.norm(p - np.asarray(cam.pos)[None], axis=1)) if cam is not None else slice(None)
        return [dict(pos=p[order], size=size[order], color=col[order], alpha=(self.alpha * self.bright * np.ones(self.n))[order],
                     kind="soft", paint=self.paint, paint_light=0.25, dof=0.6)]


class Flock:
    """Birds leaving a place and flying off together (p07, ref 08), for figures that are not a Body (a Profile):
    each rises from near `source`, wings beating, and flies toward `dir`, weaving.

    source   a point or a function of time; dir: (x, y, z) where they fly; n; t (the first leaves), dur (the last
             leaves after); speed m/s; size metres; spread: how far apart their headings are
    color    display hex: dark colours are painted (silhouettes on a pale sky), light ones glow"""
    wants_camera = True

    def __init__(self, source, dir=(1.0, 0.3, 0.0), n=30, t=0.0, dur=2.5, speed=1.2, size=0.06, spread=0.35,
                 color="#20222e", bright=1.0, life=8.0, scatter=0.25, seed=1.0):
        self.source = source
        d = np.asarray(dir, np.float64)
        self.dir = d / max(np.linalg.norm(d), 1e-9)
        self.n, self.t0, self.dur = int(n), float(t), float(dur)
        self.speed, self.size, self.spread = float(speed), float(size), float(spread)
        self.bright, self.life, self.scatter = float(bright), float(life), float(scatter)
        k = int(seed * 100)
        self.r = [hash01(self.n, k + i).astype(np.float64) for i in range(8)]
        c = lin(color) if isinstance(color, str) else np.asarray(color, np.float64)
        self.paint = 1.0 if float(np.mean(c)) < 0.12 else 0.0
        self.color = _show(color) if (self.paint and isinstance(color, str)) else c
        jit = np.stack([self.r[0] - 0.5, (self.r[1] - 0.5) * 0.6, self.r[2] - 0.5], axis=1) * 2.0
        dd = self.dir[None] + jit * self.spread
        self.dirs = dd / np.linalg.norm(dd, axis=1, keepdims=True)
        self.tau = self.t0 + self.dur * self.r[3]

    def _path(self, t):
        r = self.r
        age = np.maximum(t - self.tau, 0.0)
        ease = age - 0.6 * (1.0 - np.exp(-age / 0.6))
        src = _pt(self.source, min(t, self.t0 + self.dur))
        off = np.stack([r[4] - 0.5, r[5] - 0.5, r[6] - 0.5], axis=1) * self.scatter
        side = np.cross(self.dirs, np.array([0.0, 1.0, 0.0]))
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
        weave = np.sin(age * (1.1 + 0.8 * r[7]) + r[7] * 20.0) * 0.25 * np.minimum(age, 1.5)
        bob = np.sin(age * (1.9 + r[6]) + r[5] * 9.0) * 0.08 * np.minimum(age, 1.0)
        sp = self.speed * (0.75 + 0.5 * r[2])
        p = src[None] + off + self.dirs * (sp * ease)[:, None] + side * weave[:, None]
        p[:, 1] += bob
        return p, age

    def sample(self, t, cam=None):
        p, age = self._path(t)
        on = (t >= self.tau) & (age < self.life)
        if not on.any():
            return []
        p2, _ = self._path(t + 0.05)
        vel = (p2 - p) / 0.05
        if cam is not None:
            r, u, _f = cam.basis()
            rot = np.arctan2(vel @ np.asarray(u), vel @ np.asarray(r))
        else:
            rot = np.zeros(self.n)
        grow = np.clip(age / 0.8, 0.2, 1.0)
        a = np.clip(age / 0.4, 0, 1) * np.clip((self.life - age) / 1.0, 0, 1)
        return [dict(pos=p[on], size=(self.size * (0.7 + 0.6 * self.r[0]) * grow)[on], color=self.color,
                     alpha=(0.95 * self.bright * a)[on], kind="bird", rot=rot[on], seed=self.r[1][on], vel=vel[on],
                     paint=self.paint, paint_light=0.0 if self.paint else 1.0)]


class PaintedShape:
    """A silhouette painted in one exact colour from a shape set (a Body's _Shape, a Profile's shape_set()):
    flat discs of paint, so it uses no mask layer. For more dark figures in one frame than the mask pass has
    layers (one dark and two sky layers a frame). It does not hide the lights behind it as a mask does.

    source   the shape set; ink: display hex (shown exactly) or linear triple; grow: metres added to every
             disc so they close into one shape; alpha: 0..1 (a number or a function of time)"""

    def __init__(self, source, ink, grow=0.014, alpha=1.0):
        self.source = source
        self.ink = _show(ink) if isinstance(ink, str) else np.asarray(ink, np.float64)
        self.grow, self.alpha = float(grow), alpha
        self.wants_camera = getattr(source, "wants_camera", False)

    def gain(self, t):
        return float(self.source.gain(t)) if hasattr(self.source, "gain") else 1.0

    def sample(self, t, cam=None):
        res = self.source.sample(t, cam) if self.wants_camera else self.source.sample(t)
        bs = res if isinstance(res, (list, tuple)) else [res]
        a = float(_val(self.alpha, t))
        out = []
        for b in bs:
            if not b or b.get("pos") is None or len(b["pos"]) == 0:
                continue
            size = np.asarray(b.get("size", 0.02), np.float64) + self.grow
            al = np.clip(np.asarray(b.get("alpha", 1.0), np.float64) * 2.0, 0.0, 1.0) * a
            out.append(dict(pos=b["pos"], size=size, color=self.ink, alpha=al, kind="disc", paint=1.0,
                            paint_light=0.0, twinkle=0.0))
        return out


class Billows:
    """A cumulus of round blobs round the back of a head (a Profile or anything with frame(t) and pose()), for
    a silhouette only: give it to a mask (Profile.shape_set(extra=[Billows(...)])), so the back of the head and
    the shoulders turn into cloud while the face keeps its edge (p07). Draws nothing itself.

    path     (u, v) places in head units the cumulus follows (default: from the crown down the back of the head
             and neck to the shoulder); size: (largest, smallest) radius in head units; n: blobs along the path;
             puffs: small blobs on each; boil: how fast they swell and drift"""
    PATH = ((-0.12, 0.98), (-0.36, 0.93), (-0.55, 0.78), (-0.63, 0.55), (-0.58, 0.30), (-0.46, 0.08),
            (-0.48, -0.20), (-0.62, -0.45), (-0.76, -0.70))

    def __init__(self, head, path=None, size=(0.12, 0.05), n=24, puffs=10, boil=1.0, seed=1.0):
        self.head = head
        pts = np.asarray(path or self.PATH, np.float64)
        d = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
        k = int(seed * 100)
        r = [hash01(n, k + i).astype(np.float64) for i in range(4)]
        s = (np.arange(n) + 0.5) / n
        c = np.stack([np.interp(s * d[-1], d, pts[:, 0]), np.interp(s * d[-1], d, pts[:, 1])], axis=1)
        rad = (size[0] + (size[1] - size[0]) * s) * (0.75 + 0.5 * r[0])
        c += (np.stack([r[1], r[2]], axis=1) - 0.5) * rad[:, None] * 0.8
        m = n * puffs
        q = [hash01(m, k + 10 + i).astype(np.float64) for i in range(3)]
        par = np.repeat(np.arange(n), puffs)
        ang = q[0] * np.pi * 1.6 + np.pi * 0.2              # on the outer (upper, back) side
        out = np.stack([np.cos(ang), np.sin(ang)], axis=1) * np.array([-1.0, 1.0])
        cc = c[par] + out * rad[par, None] * (0.80 + 0.25 * q[1][:, None])
        rr = rad[par] * (0.18 + 0.30 * q[2] ** 1.5)
        self.c = np.concatenate([c, cc])
        self.r = np.concatenate([rad, rr])
        self.n_big = n
        self.ph = hash01(len(self.r), k + 20).astype(np.float64) * 6.283
        self.boil = float(boil)

    def gain(self, t):
        h = self.head
        return float(h.gain(t)) if hasattr(h, "gain") else 1.0

    def rim(self, t):
        """World places of the small outer puffs (where soft painted cloud can blur the cumulus edge)."""
        r = self.sample(t)
        return r[0]["pos"][self.n_big:] if r else np.zeros((0, 3))

    def sample(self, t):
        h = self.head
        sh = getattr(h, "show", None)
        if sh is not None and not (sh[0] <= t <= sh[1]):
            return []
        b = self.boil
        c = self.c + np.stack([np.sin(t * 0.21 * b + self.ph), np.cos(t * 0.17 * b + self.ph * 1.3)], axis=1) * 0.02
        r = self.r * (1.0 + 0.08 * np.sin(t * 0.35 * b + self.ph * 0.7))
        p = np.concatenate([c, np.zeros((len(c), 1))], axis=1)
        if hasattr(h, "pose"):
            p, _ = h.pose(p, None, t)
        fr = h.frame(t)
        return [dict(pos=fr.world(p), size=2.0 * r * fr.H, alpha=1.0, kind="soft")]


class Nothing:
    """A point set that draws nothing (to carry a mask whose shape comes from Mask.source)."""

    def sample(self, t):
        return []
