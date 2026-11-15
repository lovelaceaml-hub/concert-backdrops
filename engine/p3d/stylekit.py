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
For the two approved looks (engine/p3d/styles.py) and their heavenly settings:
  Glow(at, ...)                   a soft ball of light (a heart light inside a body, a bloom round it)
  LightTrails(body, ...)          ribbons of light streaming off a body that stays whole (gold_glitter)
  Bloom(at, t, ...)               light blooming from a point: a swelling glow and a slow cloud of sparkles
  HandLight(body, ...)            a small light held in a hand that floats up into the sky when released
  LightRiver(path, ...)           a river of light flowing over the lake
  Aurora(...)                     curtains of an aurora far away in the sky
  CloudBank(center, ...)          a grand bank of billowing clouds glowing from within, gold, rose, violet
  GodRays(source, ...)            soft volumetric rays pouring down through gaps in clouds, motes in them
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


# ----------------------------------------------------------------------------------------- heavenly pieces
class Glow:
    """A soft ball of light (a heart light inside a crystal body, a warm aura round a gold one): many soft
    sprites in a gaussian ball round a point that may move.

    at       a point or a function of time; radius: metres; color, color2 (the core and the rim, display hex)
    alpha    the strength of each sprite (the ball's light grows with n); pulse: 0..1, a slow breathing"""

    def __init__(self, at, radius=0.12, color="#ffe2a8", color2="#ffc890", n=60, alpha=0.05, pulse=0.3, size=0.6,
                 show=None, seed=1.0):
        self.at, self.radius = at, float(radius)
        self.color, self.color2 = _col(color), _col(color2)
        self.n, self.alpha, self.pulse, self.size = int(n), float(alpha), float(pulse), float(size)
        self.show = show
        k = int(seed * 100)
        r = [hash01(self.n, k + i).astype(np.float64) for i in range(4)]
        g = np.stack([r[0], r[1], r[2]], axis=1) - 0.5
        g /= np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-6)
        self.off = g * (np.sqrt(-2.0 * np.log(np.maximum(1.0 - 0.95 * r[3], 1e-6))) * 0.45)[:, None]
        self.r = r[3]
        self.seed = float(seed)

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 0.6)) * (1.0 - float(bm.ramp(t, self.show[1] - 0.6, self.show[1])))

    def sample(self, t):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        c = _pt(self.at, t)
        br = 1.0 + self.pulse * 0.35 * np.sin(t * 1.3 + self.seed)
        p = c[None] + self.off * self.radius
        mix = np.clip(np.linalg.norm(self.off, axis=1) / 0.9, 0, 1)[:, None]
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        return [dict(pos=p, size=self.radius * self.size * (0.6 + 0.8 * self.r), color=col,
                     alpha=self.alpha * br * np.ones(self.n), kind="soft", lod=False)]


class LightTrails:
    """Graceful ribbons of light streaming off a figure while it stays whole (gold glitter people): each trail
    leaves a place on the body (a wrist, a shoulder, the back of the head) and flows behind it with the air,
    rising and curling, thinning and fading to its tip; sparkles drift off along it.

    body     anything with where(t, place) (a Body)
    places   the places trails leave from (Body.where names); per: trails from each place
    length   seconds of the past each trail shows (its length follows the figure's own motion and the air)
    wind     (x, y, z) metres per second the trails drift with; rise: metres per second upward
    width    metres at the root; color, color2; bright; sparkle (sparkles per trail)"""

    def __init__(self, body, places=("wrist.L", "wrist.R", "shoulder.L", "shoulder.R", "back", "head"), per=2,
                 length=2.2, wind=(-0.35, 0.0, 0.0), rise=0.18, curl=0.12, width=0.035, color="#ffd27a",
                 color2="#fff2cc", bright=1.0, sparkle=10, steps=20, show=None, seed=1.0):
        self.body, self.places = body, list(places)
        self.per, self.length, self.steps = int(per), float(length), int(steps)
        self.wind, self.rise, self.curl = np.asarray(wind, np.float64), float(rise), float(curl)
        self.width, self.bright, self.sparkle = float(width), float(bright), int(sparkle)
        self.color, self.color2 = _col(color), _col(color2)
        self.show = show
        k = int(seed * 100)
        m = len(self.places) * self.per
        self.r = [hash01(m, k + i).astype(np.float64) for i in range(6)]
        self.seed = float(seed)
        self._memo = {}

    def gain(self, t):
        g = self.body.gain(t) if hasattr(self.body, "gain") else 1.0
        if self.show is not None:
            g *= float(bm.ramp(t, self.show[0], self.show[0] + 0.8)) * (1.0 - float(bm.ramp(t, self.show[1] - 0.6, self.show[1])))
        return g

    def sample(self, t):
        b = self.body
        sh = getattr(b, "show", None)
        if sh is not None and not (sh[0] <= t <= sh[1]):
            return []
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        # moments on a fixed grid (a pose once asked for is kept by the body), with the present at the head
        dt = self.length / max(self.steps - 1, 1)
        g0 = np.floor(t / dt) * dt
        times = np.r_[t, g0 - dt * np.arange(self.steps)] if t - g0 > 1e-6 else g0 - dt * np.arange(self.steps + 1)
        ages = t - times
        S = len(ages)
        t0 = sh[0] if sh is not None else -1e9
        # the places in the past (one Body.where per place and moment)
        # each past moment's places are asked once and kept while the trail needs them (a body's pose can be
        # costly: a body in a pair solves its contact with the other)
        P = np.zeros((len(self.places), S, 3))
        memo = self._memo
        for j, a in enumerate(ages):
            tk = round(float(max(t - a, t0)), 6)
            got = memo.get(tk)
            if got is None:
                got = np.array([b.where(tk, name) for name in self.places], np.float64)
                if j > 0:
                    memo[tk] = got
            P[:, j] = got
        for tk in [k for k in memo if k < t - self.length - 1.0 or k > t + 1.0]:
            del memo[tk]
        ages = np.minimum(ages, self.length)
        m = len(self.places) * self.per
        pid = np.repeat(np.arange(len(self.places)), self.per)
        r = self.r
        q = ages / self.length
        base = P[pid]                                                   # (m, S, 3)
        drift = np.broadcast_to(self.wind[None, None, :] * ages[None, :, None], (m, S, 3)).copy()
        drift[..., 1] += self.rise * ages[None, :] * (0.6 + 0.8 * r[0][:, None])
        side = np.stack([np.sin(r[1] * 6.28), np.zeros(m), np.cos(r[1] * 6.28)], axis=1)
        side2 = np.stack([np.cos(r[1] * 6.28), 0.4 * (r[2] - 0.5), -np.sin(r[1] * 6.28)], axis=1)
        ph = ages[None, :] * (2.2 + 1.2 * r[2][:, None]) - t * (0.9 + 0.4 * r[3][:, None]) + r[4][:, None] * 6.28
        # each ribbon winds in a slow spiral as it drifts away (graceful, never a straight streak)
        amp = (self.curl * q[None, :] ** 0.9)[..., None]
        curl = side[:, None, :] * (amp * np.sin(ph)[..., None]) + side2[:, None, :] * (amp * 0.7 * np.cos(ph)[..., None])
        off = (np.stack([r[2], r[3], r[4]], axis=1) - 0.5) * 0.05
        path = base + drift + curl + off[:, None, :] * q[None, :, None]
        p1 = path[:, :-1].reshape(-1, 3)
        p2 = path[:, 1:].reshape(-1, 3)
        qa, qb = np.tile(q[:-1], m), np.tile(q[1:], m)
        a1 = (1.0 - qa) ** 1.6 * np.clip(qa * 8.0, 0.2, 1.0)
        a2 = (1.0 - qb) ** 1.6 * np.clip(qb * 8.0, 0.2, 1.0)
        w1 = self.width * (1.0 - 0.8 * qa)
        w2 = self.width * (1.0 - 0.8 * qb)
        mix = np.repeat(r[5], S - 1)[:, None]
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        out = [dict(pos=p1, pos2=p2, size=w1, size2=w2, color=col, alpha=0.30 * self.bright * a1,
                    alpha2=0.30 * self.bright * a2, kind="ribbon"),
               dict(pos=p1, pos2=p2, size=w1 * 0.25, size2=w2 * 0.25, color=self.color2,
                    alpha=0.35 * self.bright * a1, alpha2=0.35 * self.bright * a2, kind="ribbon")]
        if self.sparkle:
            n = m * self.sparkle
            rs = hash01(n, 77).astype(np.float64)
            rs2 = hash01(n, 78).astype(np.float64)
            tr = np.repeat(np.arange(m), self.sparkle)
            u = np.mod(rs + t * (0.15 + 0.2 * rs2), 1.0)
            j = np.minimum((u * (S - 1)).astype(np.int64), S - 2)
            f = (u * (S - 1) - j)[:, None]
            pos = path[tr, j] * (1 - f) + path[tr, j + 1] * f
            pos = pos + (np.stack([rs2, rs, rs2 * rs], axis=1) - 0.5) * 0.06 * u[:, None]
            out.append(dict(pos=pos, size=0.006 + 0.008 * rs2 ** 3, color=self.color2,
                            alpha=0.8 * self.bright * (1.0 - u) ** 1.2, emit=1.0 + 2.0 * (rs2 > 0.9), kind="soft",
                            twinkle=0.9))
        return out


class LightRiver:
    """A river of light flowing over the water (or the ground): glowing points streaming along a curve,
    densest in its middle, with sparkles and a soft glow; mirrored in the lake like any set.

    path     (x, z) points the river follows (a gentle curve), y: its height (just above the water)
    width    metres; n: points; speed: metres per second along the path; color, color2; bright"""

    def __init__(self, path, width=2.0, n=26000, speed=1.2, y=0.03, color="#ffd890", color2="#fff4d8", bright=1.0,
                 show=None, seed=1.0):
        pts = np.asarray(path, np.float64)
        d = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
        self.pts, self.d, self.L = pts, d, float(d[-1])
        self.width, self.n, self.speed, self.y = float(width), int(n), float(speed), float(y)
        self.color, self.color2 = _col(color), _col(color2)
        self.bright = float(bright)
        self.show = show
        k = int(seed * 100)
        self.r = [hash01(self.n, k + i).astype(np.float64) for i in range(4)]

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 0.8)) * (1.0 - float(bm.ramp(t, self.show[1] - 0.8, self.show[1])))

    def sample(self, t):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        r = self.r
        s = np.mod(r[0] * self.L + t * self.speed * (0.7 + 0.6 * r[1]), self.L)
        x = np.interp(s, self.d, self.pts[:, 0])
        z = np.interp(s, self.d, self.pts[:, 1])
        ds = 0.5
        x2 = np.interp(np.minimum(s + ds, self.L), self.d, self.pts[:, 0])
        z2 = np.interp(np.minimum(s + ds, self.L), self.d, self.pts[:, 1])
        tx, tz = x2 - x, z2 - z
        tl = np.maximum(np.hypot(tx, tz), 1e-6)
        nx, nz = -tz / tl, tx / tl
        lat = (np.sqrt(-2.0 * np.log(np.maximum(1.0 - 0.98 * r[2], 1e-6))) * np.cos(r[3] * 6.283)) * 0.30
        wob = 0.25 * np.sin(s * 0.7 - t * 0.8 + r[3] * 3.0)
        off = (lat + wob * 0.2) * self.width
        pos = np.stack([x + nx * off, self.y + 0.02 * r[1], z + nz * off], axis=1)
        edge = np.clip(1.0 - np.abs(lat) / 0.9, 0.0, 1.0)
        ends = np.clip(s / 3.0, 0, 1) * np.clip((self.L - s) / 3.0, 0, 1)
        mix = (r[1] ** 2)[:, None]
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        return [dict(pos=pos, size=0.02 + 0.04 * r[2] ** 4, color=col, alpha=0.45 * self.bright * edge * ends,
                     emit=1.0 + 2.5 * (r[0] > 0.993), kind="soft", twinkle=0.8, backlight=0.4)]


class Aurora:
    """An aurora: curtains of fine vertical rays hanging in the sky, brightest at their lower edge and fading
    upward, folding and rippling slowly, bright pulses running along them. Far away, sharp (no lens blur).

    center   (x, z) on the ground plan; span: metres across; height: (lower edge, top) metres
    curtains how many curtains, one behind the other; rays: fine rays per curtain
    colors   (lower edge, middle, top) display hex; bright; folds: how deep the folds are (metres)"""

    def __init__(self, center=(0.0, -400.0), span=900.0, height=(80.0, 300.0), curtains=3, rays=1400,
                 folds=60.0, colors=("#b8ffd8", "#7cf0c0", "#c890ff"), bright=1.0, yaw=0.0, reflect=True, show=None,
                 seed=1.0):
        self.center = np.asarray(center, np.float64)
        self.span, self.h0, self.h1 = float(span), float(height[0]), float(height[1])
        self.k, self.n, self.folds, self.bright = int(curtains), int(rays), float(folds), float(bright)
        self.c = [_col(c) for c in colors]
        self.yaw = np.radians(yaw)
        self.reflect = bool(reflect)
        self.show = show
        k = int(seed * 100)
        m = self.k * self.n
        self.r = [hash01(m, k + i).astype(np.float64) for i in range(4)]

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 1.5)) * (1.0 - float(bm.ramp(t, self.show[1] - 1.0, self.show[1])))

    def sample(self, t):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        n, K = self.n, self.k
        out = []
        cy, sy = np.cos(self.yaw), np.sin(self.yaw)
        for j in range(K):
            r = [x[j * n:(j + 1) * n] for x in self.r]
            u = (np.arange(n) + r[0]) / n - 0.5                     # along the curtain, jittered
            span = self.span * (1.0 - 0.18 * j)
            x = u * span
            ph = 1.7 * j
            # the curtain folds: its foot line winds in depth, slowly moving
            fold = (np.sin(u * 6.0 + t * 0.10 + ph) * 0.55 + np.sin(u * 15.0 - t * 0.17 + 2 * ph) * 0.3
                    + np.sin(u * 37.0 + t * 0.29 + ph) * 0.15) * self.folds
            depth = -120.0 * j
            X = self.center[0] + x * cy + (fold + depth) * sy
            Z = self.center[1] - x * sy + (fold + depth) * cy
            # the lower edge rises and falls gently along the curtain
            base = self.h0 * (1.0 + 0.10 * np.sin(u * 5.0 + ph + t * 0.07) + 0.08 * j)
            top = base + (self.h1 - self.h0) * (0.55 + 0.35 * (0.5 + 0.5 * np.sin(u * 3.0 - t * 0.05 + ph))
                                                + 0.15 * r[1])
            # rays: fine striations with bright pulses running along the curtain
            ray = 0.45 + 0.55 * r[2] ** 1.5
            run = 0.5 + 0.5 * np.sin(u * 40.0 - t * 0.9 + ph) * np.sin(u * 11.0 + t * 0.35)
            sheet = 0.55 + 0.45 * np.sin(u * 4.0 + t * 0.12 + ph)
            ends = np.clip((0.5 - np.abs(u)) / 0.12, 0, 1) ** 1.5
            a = ray * (0.35 + 0.65 * run) * sheet * ends * self.bright * (0.55 if j else 1.0)
            w = span / n * 1.1
            mid = base + (top - base) * 0.12
            p0 = np.stack([X, base - 2.0, Z], axis=1)
            p1 = np.stack([X, mid, Z], axis=1)
            p2 = np.stack([X, top, Z], axis=1)
            z0 = np.zeros(n)
            cl = self.c[0][None] * np.ones((n, 1))
            cm = self.c[1][None] * 0.6 + self.c[2][None] * 0.4
            ct = self.c[2][None] * np.ones((n, 1))
            st = dict(kind="ribbon", dof=0.0, fog=0.2, reflect=self.reflect)
            # the bright lower edge (a quick rise), then the long fade upward
            out.append(dict(pos=p0, pos2=p1, size=w, size2=w, color=cl, alpha=z0, alpha2=0.30 * a, **st))
            out.append(dict(pos=p1, pos2=p2, size=w, size2=w * 1.4, color=cm * np.ones((n, 1)), alpha=0.30 * a,
                            alpha2=z0, **st))
            # a faint violet glow high above the curtain
            p3 = np.stack([X, top + (top - base) * 0.4, Z], axis=1)
            out.append(dict(pos=p2 - (p2 - p1) * 0.5, pos2=p3, size=w * 3, size2=w * 3, color=ct,
                            alpha=0.05 * a, alpha2=z0, **st))
        return out


class CloudBank:
    """A grand bank of clouds glowing with warm light from within: billowing heaps (each a round mass with
    smaller billows on top, flat underneath) at several depths, gold where they face the light and glowing
    through at their edges, rose and then violet in their shade. Light only adds: the clouds are light.

    center   (x, y, z) the middle of the bank; size (width, height, depth) metres
    billows  how many heaps; n: soft sprites in all; light: a world point the light comes from (behind and
             above the bank for light glowing through); color (lit gold), color2 (rose), shade (violet)
    bright, alpha (each sprite), gaps: (x, z) places to leave open for rays (a list), gap: their radius,
    dof (how much lens blur, default none: the billows stay crisp), reflect (in the lake; default off: the
    mirror of so many large soft points floods the water)"""

    def __init__(self, center, size=(60.0, 14.0, 20.0), billows=26, n=8000, light=None, color="#ffd894",
                 color2="#f08cac", shade="#5a3482", bright=1.0, alpha=0.014, gaps=(), gap=6.0, dof=0.0,
                 reflect=False, show=None, seed=1.0, puff=None):
        self.center = np.asarray(center, np.float64)
        self.dims = np.asarray(size, np.float64)
        self.bright, self.alpha = float(bright), float(alpha)
        self.light = light
        self.color, self.color2, self.shade = _col(color), _col(color2), _col(shade)
        self.show = show
        k = int(seed * 100)
        W, H, D = self.dims
        nb = int(billows)
        rb = [hash01(nb, k + i).astype(np.float64) for i in range(5)]
        bc = np.stack([(rb[0] - 0.5) * W, np.zeros(nb), (rb[1] - 0.5) * D], axis=1)
        R = (0.06 + 0.10 * rb[2] ** 1.5) * W
        R = np.minimum(R, 0.45 * H + 0.02 * W)
        for g in gaps:                                   # keep the gaps open: push heaps out of them
            gx = np.asarray(g, np.float64) - self.center[[0, 2]]
            d = np.hypot(bc[:, 0] - gx[0], bc[:, 2] - gx[1])
            push = np.clip(gap + R * 0.6 - d, 0, None)
            dirx = (bc[:, 0] - gx[0]) / np.maximum(d, 1e-6)
            dirz = (bc[:, 2] - gx[1]) / np.maximum(d, 1e-6)
            bc[:, 0] += dirx * push
            bc[:, 2] += dirz * push
        bc[:, 1] = -0.5 * H + R * (0.55 + 0.35 * rb[3])          # sitting on a flat floor
        # smaller billows heaped on top of each mass
        sub = []
        for i in range(nb):
            ns = 3 + int(rb[4][i] * 4)
            rs = [hash01(ns, k + 50 + 7 * i + j).astype(np.float64) for j in range(4)]
            ang = rs[0] * 6.283
            up = 0.35 + 0.5 * rs[1]
            off = np.stack([np.cos(ang) * (1 - up) * 0.8, up, np.sin(ang) * (1 - up) * 0.8], axis=1) * R[i]
            sub.append(np.c_[bc[i] + off * 0.85, R[i] * (0.35 + 0.3 * rs[2])])
        sub = np.concatenate(sub)
        cents = np.r_[np.c_[bc, R], sub]
        self.cents = cents
        m = int(n)
        rr = [hash01(m, k + 20 + i).astype(np.float64) for i in range(6)]
        w = cents[:, 3] ** 2
        cid = np.searchsorted(np.cumsum(w) / w.sum(), rr[0])
        cid = np.minimum(cid, len(cents) - 1)
        v = np.stack([rr[1] - 0.5, rr[2] - 0.5, rr[3] - 0.5], axis=1)
        v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-6)
        rad = cents[cid, 3] * (0.62 + 0.38 * rr[4] ** 0.35)
        p = cents[cid, :3] + v * rad[:, None]
        p[:, 1] = np.maximum(p[:, 1], -0.5 * H + 0.15 * cents[cid, 3])        # flat bellies
        self.p = p
        self.v = v
        self.cid = cid
        self.s = cents[cid, 3] * (0.30 + 0.28 * rr[5])
        self.r = rr[5]
        self.puff = 1.0 if puff is None else float(puff)
        self.dof, self.reflect = float(dof), bool(reflect)

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 1.0)) * (1.0 - float(bm.ramp(t, self.show[1] - 1.0, self.show[1])))

    def sample(self, t):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        drift = np.array([np.sin(t * 0.03) * 0.6, 0.0, 0.0])
        pos = self.center[None] + self.p + drift[None]
        if self.light is not None:
            L = _pt(self.light, t)
            c = self.center[None] + self.cents[self.cid, :3]
            d = L[None] - c
            d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
            s = (self.v * d).sum(1)
        else:
            s = self.v[:, 1]
        lit = np.clip((s + 0.25) / 1.25, 0.0, 1.0)
        top = np.clip(self.v[:, 1] * 0.5 + 0.5, 0, 1)
        k1 = np.clip((s + 0.8) / 0.9, 0, 1)[:, None]                      # shade to rose
        k2 = (lit ** 1.6)[:, None]                                       # rose to gold
        col = self.shade[None] * (1 - k1) + self.color2[None] * k1
        col = col * (1 - k2) + self.color[None] * k2
        # light glowing through the thin edges that face it (a gold lining)
        edge = np.clip(np.linalg.norm(self.p - self.cents[self.cid, :3], axis=1) / self.cents[self.cid, 3], 0, 1)
        glow = 1.0 + 1.2 * lit ** 3 * edge ** 2 + 0.3 * top
        a = self.alpha * self.bright * (0.35 + 0.65 * lit) * glow
        return [dict(pos=pos, size=self.s * self.puff, color=col, alpha=a, kind="soft", dof=self.dof, fog=0.4,
                     lod=False, reflect=self.reflect)]


class GodRays:
    """Rays of light pouring down from a light behind clouds: soft volumetric beams that widen as they fall
    and fade toward the ground, of varied widths and angles, slowly shimmering, with dust motes sparkling in
    them. Put the source among a CloudBank's gaps so the rays pour through them.

    source   (x, y, z) the light (high, behind or among the clouds), or a function of time
    targets  (x, z) or (x, y, z) points the rays fall toward; or n rays landing at random round `around`
             within `spread` metres
    width    (at the source, at the end) metres, each ray 0.5 to 1.6 times it; reach: how far toward its
             target a ray stays visible (0..1)
    color, color2 (the motes), bright, sprites per ray, motes per ray, shimmer (0..1), burst: the soft bright
    glow where the light breaks through (0: none), tail: the share of its length over which a ray fades out
    at its end (0.45: a long fade toward the ground; small: the ray lands bright, a beam falling on someone)"""

    def __init__(self, source, targets=None, around=(0.0, 0.0), spread=6.0, n=6, width=(0.8, 4.0), reach=0.95,
                 color="#ffe2a8", color2="#fff4dc", bright=1.0, sprites=420, motes=140, shimmer=0.3, ground=0.0,
                 burst=0.0, tail=0.45, show=None, seed=1.0):
        self.source = source
        k = int(seed * 100)
        if targets is None:
            rt = [hash01(int(n), k + 90 + i).astype(np.float64) for i in range(2)]
            ang = rt[0] * 6.283
            rad = spread * np.sqrt(rt[1])
            targets = [(around[0] + np.cos(a) * r, around[1] + np.sin(a) * r) for a, r in zip(ang, rad)]
        T = []
        for tg in targets:
            tg = np.asarray(tg, np.float64)
            T.append(np.array([tg[0], ground, tg[1]]) if len(tg) == 2 else tg)
        self.T = np.array(T)
        self.ground = float(ground)
        self.nr = len(self.T)
        self.w0, self.w1 = float(width[0]), float(width[1])
        self.reach, self.bright, self.shimmer = float(reach), float(bright), float(shimmer)
        self.ns, self.nm = int(sprites), int(motes)
        self.color, self.color2 = _col(color), _col(color2)
        self.show = show
        rr = [hash01(self.nr, k + 30 + i).astype(np.float64) for i in range(3)]
        self.wk = 0.5 + 1.1 * rr[0]
        self.bk = 0.55 + 0.45 * rr[1]
        self.ph = rr[2] * 6.283
        m = self.nr * self.ns
        self.rs = [hash01(m, k + 40 + i).astype(np.float64) for i in range(4)]
        mm = self.nr * self.nm
        self.rm = [hash01(mm, k + 60 + i).astype(np.float64) for i in range(5)]
        self.burst = float(burst)
        self.tail = max(float(tail), 0.02)
        rb = [hash01(40, k + 80 + i).astype(np.float64) for i in range(4)]
        self.boff = (np.stack([rb[0], rb[1], rb[2]], axis=1) - 0.5) * np.array([1.0, 0.5, 1.0])
        self.br = rb[3]

    def gain(self, t):
        if self.show is None:
            return 1.0
        return float(bm.ramp(t, self.show[0], self.show[0] + 1.0)) * (1.0 - float(bm.ramp(t, self.show[1] - 1.0, self.show[1])))

    def _frame(self, S):
        ax = self.T - S[None]
        ln = np.linalg.norm(ax, axis=1, keepdims=True)
        ax = ax / np.maximum(ln, 1e-6)
        e1 = np.cross(ax, np.array([0.0, 0.0, 1.0]))
        e1 /= np.maximum(np.linalg.norm(e1, axis=1, keepdims=True), 1e-6)
        e2 = np.cross(ax, e1)
        return ax, ln[:, 0], e1, e2

    def sample(self, t):
        if self.show is not None and not (self.show[0] <= t <= self.show[1]):
            return []
        S = _pt(self.source, t)
        ax, ln, e1, e2 = self._frame(S)
        out = []
        # the beams: many large soft sprites, gaussian across, widening downward
        rid = np.repeat(np.arange(self.nr), self.ns)
        r = self.rs
        u = 0.04 + (self.reach - 0.04) * r[0] ** 0.75
        w = (self.w0 + (self.w1 - self.w0) * u) * self.wk[rid]
        g1 = np.sqrt(-2.0 * np.log(np.maximum(1.0 - 0.97 * r[1], 1e-6))) * np.cos(r[2] * 6.283) * 0.30
        g2 = np.sqrt(-2.0 * np.log(np.maximum(1.0 - 0.97 * r[1], 1e-6))) * np.sin(r[2] * 6.283) * 0.30
        pos = S[None] + ax[rid] * (u * ln[rid])[:, None] + (e1[rid] * g1[:, None] + e2[rid] * g2[:, None]) * w[:, None]
        prof = np.clip(u / 0.12, 0, 1) * np.clip((self.reach - u) / (self.tail * self.reach), 0, 1) ** 1.2
        sh = 1.0 + self.shimmer * np.sin(t * 0.45 + self.ph[rid] + u * 2.0)
        core = np.exp(-(g1 ** 2 + g2 ** 2) / 0.09)
        a = 0.022 * self.bright * self.bk[rid] * prof * sh * (0.5 + 0.5 * core) * (420.0 / max(self.ns, 1))
        sz = w * (0.55 + 0.35 * r[3])
        # a soft sprite that dips into the ground is cut by it (a hard edge): fade those out
        a = a * np.clip((pos[:, 1] - self.ground) / (0.5 * sz), 0.0, 1.0)
        out.append(dict(pos=pos, size=sz, color=self.color, alpha=a, kind="soft", dof=0.3,
                        fog=0.15, lod=False, reflect=False))
        if self.burst > 0.0:
            # where the light breaks through the clouds: a soft bright source
            out.append(dict(pos=S[None] + self.boff * self.w1 * 0.8, size=self.w1 * (0.6 + 0.8 * self.br),
                            color=self.color2, alpha=0.05 * self.burst * self.bright * np.ones(len(self.br)),
                            kind="soft", dof=0.0, fog=0.1, lod=False))
        # the motes: fine dust drifting slowly inside the beams, sparkling
        q = self.rm
        mid = np.repeat(np.arange(self.nr), self.nm)
        um = np.mod(0.25 + 0.75 * q[0] + t * (0.004 + 0.006 * q[1]), 1.0) * self.reach
        wm = (self.w0 + (self.w1 - self.w0) * um) * self.wk[mid]
        rad = np.sqrt(q[2]) * 0.42
        ang = q[3] * 6.283 + t * 0.1 * (q[1] - 0.5)
        pm = S[None] + ax[mid] * (um * ln[mid])[:, None] + (e1[mid] * (np.cos(ang) * rad)[:, None]
                                                            + e2[mid] * (np.sin(ang) * rad)[:, None]) * wm[:, None]
        pm = pm + bm.flow(pm * 0.3, t * 0.2, speed=1.0, seed=4.0) * 0.15
        prm = np.clip(um / 0.25, 0, 1) * np.clip((self.reach - um) / (0.3 * self.reach), 0, 1)
        out.append(dict(pos=pm, size=0.010 + 0.022 * q[4] ** 3, color=self.color2,
                        alpha=0.85 * self.bright * self.bk[mid] * prm, emit=1.0 + 2.5 * (q[4] > 0.9), kind="soft",
                        twinkle=1.0, backlight=0.6, dof=0.8, reflect=False))
        return out


class Bloom:
    """Light that blooms from a point (an embrace, a touch): a warm glow swells and softens, and a slow cloud of
    sparkles opens out from it, rising and fading. Never a flash: everything eases in and out.

    at       a point or a function of time; t: when it begins; dur: seconds it lasts; radius: metres it opens to
    n        sparkles; color, color2; bright"""

    def __init__(self, at, t, dur=4.0, radius=1.2, n=900, color="#fff0c8", color2="#ffc46a", bright=1.0, seed=1.0):
        self.at, self.t0, self.dur, self.radius = at, float(t), float(dur), float(radius)
        self.n, self.bright = int(n), float(bright)
        self.color, self.color2 = _col(color), _col(color2)
        k = int(seed * 100)
        r = [hash01(self.n, k + i).astype(np.float64) for i in range(6)]
        d = np.stack([r[0], r[1], r[2]], axis=1) - 0.5
        d[:, 1] *= 0.7
        self.dir = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
        self.dist = 0.35 + 0.65 * r[3] ** 0.7
        self.delay = 0.6 * r[4]
        self.r = r[5]
        self.glow = Glow(at, radius=0.16, color=color, color2=color2, n=80, alpha=0.02, pulse=0.0, size=0.9,
                         seed=seed)

    def sample(self, t):
        a = t - self.t0
        if a < 0.0 or a > self.dur + 0.8:
            return []
        c = _pt(self.at, t)
        u = np.clip((a - self.delay) / self.dur, 0.0, 1.0)
        e = 1.0 - (1.0 - u) ** 3
        p = c[None] + self.dir * (self.radius * self.dist * e)[:, None]
        p[:, 1] += 0.25 * u * self.dist
        p += bm.flow(p * 1.5, t * 0.4, speed=1.0, seed=3.0) * 0.03 * u[:, None]
        fade = np.clip(u * 6.0, 0, 1) * (1.0 - u) ** 1.3 * (a > self.delay)
        mix = (self.r ** 2)[:, None]
        col = self.color[None] * (1 - mix) + self.color2[None] * mix
        g = float(np.clip(a / 0.9, 0, 1)) * float(np.clip(1.0 - (a - self.dur * 0.6) / (self.dur * 0.6), 0, 1))
        sw = 0.5 + 1.6 * float(bm.smoother(min(a / (self.dur * 0.5), 1.0)))
        out = []
        for bt in self.glow.sample(t):
            off = (bt["pos"] - c[None]) * sw
            bt = dict(bt, pos=c[None] + off, size=bt["size"] * sw, alpha=bt["alpha"] * g * self.bright)
            out.append(bt)
        out.append(dict(pos=p, size=0.008 + 0.012 * self.r ** 3, color=col, alpha=0.75 * self.bright * fade,
                        emit=1.0 + 2.0 * (self.r > 0.92), kind="soft", twinkle=0.8))
        st = self.r > 0.96
        out.append(dict(pos=p[st], size=0.035 * (0.6 + self.r[st]), color=col[st], alpha=0.8 * self.bright * fade[st],
                        emit=2.0, kind="spark", twinkle=0.9))
        return out


class HandLight:
    """A small light held in a hand that, at `release`, leaves it and floats up into the sky, swaying, with a
    faint trail. Before `born` there is nothing; it kindles over half a second.

    body     a Body; place: where it is held ("palm.R"); born, release: times; rise: metres per second
    color, color2, radius (metres), bright"""

    def __init__(self, body, place="palm.R", born=0.0, release=None, rise=0.55, color="#fff0c8", color2="#ffb85a",
                 radius=0.055, bright=1.0, lift=0.06, seed=1.0):
        self.body, self.place = body, place
        self.born = float(born)
        self.release = None if release is None else float(release)
        self.rise, self.lift, self.bright = float(rise), float(lift), float(bright)
        self.seed = float(seed)
        self.glow = Glow(self.pos, radius=radius, color=color, color2=color2, n=50, alpha=0.10, pulse=0.4, size=0.8,
                         seed=seed)
        self.core = _col(color)

    def pos(self, t):
        b = self.body
        if self.release is None or t <= self.release:
            p = np.asarray(b.where(t, self.place), np.float64)
            return p + np.array([0.0, self.lift, 0.0])
        p0 = np.asarray(b.where(self.release, self.place), np.float64) + np.array([0.0, self.lift, 0.0])
        a = t - self.release
        up = self.rise * (a - 0.6 * (1.0 - np.exp(-a / 0.6)))
        sway = np.array([np.sin(a * 0.9 + self.seed) * 0.25 * min(a, 1.0), 0.0,
                         np.cos(a * 0.7 + 2.0 * self.seed) * 0.15 * min(a, 1.0)])
        return p0 + np.array([0.0, up, 0.0]) + sway

    def gain(self, t):
        return float(bm.ramp(t, self.born, self.born + 0.6))

    def sample(self, t):
        if t < self.born:
            return []
        out = list(self.glow.sample(t))
        c = self.pos(t)
        out.append(dict(pos=c[None], size=0.035, color=self.core * 0.5 + 0.5, alpha=0.9 * self.bright, emit=2.2,
                        kind="spark", twinkle=0.5))
        if self.release is not None and t > self.release + 0.05:
            ts = np.linspace(t, max(self.release, t - 1.2), 12)
            pts = np.stack([self.pos(x) for x in ts])
            a = np.linspace(0.5, 0.0, 12) * self.bright
            out.append(dict(pos=pts[:-1], pos2=pts[1:], size=0.02, size2=0.012, color=self.core, alpha=a[:-1],
                            alpha2=a[1:], kind="ribbon"))
        return out
