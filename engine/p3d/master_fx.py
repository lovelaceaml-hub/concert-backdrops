"""The masterpiece's moving light (engine/songs/master_peace.py): the drop of golden light, the ring that races
to the horizon, rivers of light, rain of light, rising lights, a cathedral of falling light, motes. Pure numpy
point sets for the 3D layer; pure functions of the time t.
"""
import numpy as np

from .api import lin, ribbon
from .master_sky import TAU, sc, ss


def hsv(h, s, v):
    """Hue, saturation, value (arrays, 0..1) to linear light colours (N, 3)."""
    h = np.asarray(h, np.float64) % 1.0
    s = np.broadcast_to(np.asarray(s, np.float64), h.shape)
    v = np.broadcast_to(np.asarray(v, np.float64), h.shape)
    i = np.floor(h * 6.0)
    f = h * 6.0 - i
    p, q, r = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    i = i.astype(int) % 6
    rgb = np.select([i[:, None] == k for k in range(6)],
                    [np.stack(c, 1) for c in ((v, r, p), (q, v, p), (p, v, r), (p, q, v), (r, p, v), (v, p, q))])
    return rgb ** 2.2


# ---------------------------------------------------------------------------------------------------- the drop
class Drop:
    """The first word of love: a drop of golden light held in Mother's hands, released, falling with a soft
    tail of sparks, landing on the still sea of light. path(t) gives its place; t_land when it touches the sea."""

    def __init__(self, path, t_show=(-1.0, 6.4), t_land=6.15, color="#ffd27a", core="#fff6e2", seed=21,
                 scale=1.0):
        rng = np.random.default_rng(seed)
        self.path, self.show, self.t_land = path, t_show, t_land
        self.col, self.core = lin(color), lin(core)
        self.halo = rng.normal(size=(500, 3))
        self.halo /= np.linalg.norm(self.halo, axis=1, keepdims=True)
        self.hs = rng.random((500, 3))
        self.k = float(scale)

    def sample(self, t):
        if t < self.show[0] or t > self.show[1]:
            return None
        p = np.asarray(self.path(t), np.float64)
        gone = 1.0 - sc(self.t_land - 0.02, self.t_land + 0.10, t)
        if gone <= 0.0:
            return None
        k = self.k
        pulse = 1.0 + 0.12 * np.sin(t * 6.0) + 0.35 * np.exp(-((t - 0.25) / 0.2) ** 2)
        out = [dict(pos=p[None], size=0.07 * k * pulse, color=self.core, alpha=gone, emit=5.0, kind="spark"),
               dict(pos=p[None], size=0.55 * k * pulse, color=self.col, alpha=0.32 * gone, kind="soft"),
               dict(pos=p[None], size=2.0 * k, color=self.col, alpha=0.05 * gone, kind="soft")]
        r = k * (0.05 + 0.16 * self.hs[:, :1]) * (1.0 + 0.3 * np.sin(t * 5.0 + 6.0 * self.hs[:, 1:2]))
        out.append(dict(pos=p + self.halo * r, size=0.006 * k, color=self.core, alpha=0.6 * gone, emit=2.0,
                        kind="spark", twinkle=0.8, seed=self.hs[:, 2]))
        ts = np.linspace(max(t - 0.45, self.show[0]), t, 24)
        tail = np.array([self.path(float(x)) for x in ts])
        if np.linalg.norm(tail[-1] - tail[0]) > 0.05:
            q = np.linspace(0.0, 1.0, len(ts))
            out.append(ribbon(tail, width=0.05 * k * (0.2 + 0.8 * q), color=self.col, alpha=0.5 * q * gone,
                              emit=2.0))
            j = np.random.default_rng(int(t * 30) + 7).normal(size=(60, 3)) * 0.04 * k
            idx = np.linspace(0, len(ts) - 1, 60).astype(int)
            out.append(dict(pos=tail[idx] + j, size=0.010 * k, color=self.core, alpha=0.55 * q[idx] * gone,
                            emit=2.0, kind="spark", twinkle=0.9))
        return out


class Splash:
    """Where the drop touches the sea: a crown of golden sparks thrown up and falling back, and a soft warm bloom
    (warm and gentle: never a white flash)."""

    def __init__(self, at, t0, n=1600, color="#ffd27a", core="#fff2d6", seed=23, scale=1.0):
        rng = np.random.default_rng(seed)
        self.at = np.asarray(at, np.float64)
        self.t0 = t0
        a = rng.uniform(0.0, TAU, n)
        el = np.radians(rng.uniform(35.0, 80.0, n))
        sp = scale * rng.uniform(1.5, 5.5, n)
        self.v = np.stack([np.sin(a) * np.cos(el), np.sin(el), np.cos(a) * np.cos(el)], 1) * sp[:, None]
        self.s = rng.random(n)
        self.col, self.core = lin(color), lin(core)
        self.k = scale

    def sample(self, t):
        u = t - self.t0
        if u < 0.0 or u > 2.4:
            return None
        p = self.at + self.v * u + np.array([0.0, -4.9, 0.0]) * u * u
        p[:, 1] = np.maximum(p[:, 1], 0.02)
        al = np.exp(-u / (0.5 + 0.6 * self.s))
        bloom = np.exp(-u / 0.35)
        return [dict(pos=p, size=0.03 * self.k, color=self.core, alpha=al, emit=2.5, kind="spark", twinkle=0.6,
                     seed=self.s),
                dict(pos=self.at[None] + np.array([[0.0, 0.3, 0.0]]), size=2.6 * self.k, color=self.col,
                     alpha=0.12 * bloom, kind="soft")]


class RingWave:
    """Where the drop lands, a ring of gold races out over the sea to the horizon, and the sea it passes wakes:
    its glints light up as the ring goes by and stay, warm and twinkling."""

    def __init__(self, center, t0, speed=38.0, reach=1600.0, n_ring=2400, n_field=26000, color="#ffcf7a",
                 core="#fff2d6", until=1e9, seed=31):
        rng = np.random.default_rng(seed)
        self.c = np.asarray(center, np.float64)
        self.t0, self.v, self.reach, self.until = t0, speed, reach, until
        self.col, self.core = lin(color), lin(core)
        self.ang = np.linspace(0.0, TAU, n_ring, endpoint=False) + rng.normal(0, 0.002, n_ring)
        self.rs = rng.random(n_ring)
        r = 1.0 + (reach - 1.0) * rng.random(n_field) ** 2.2
        a = rng.uniform(0.0, TAU, n_field)
        self.fpos = self.c + np.stack([np.sin(a) * r, np.full(n_field, 0.03), np.cos(a) * r], 1)
        self.fbirth = t0 + r / self.v
        self.fsize = 0.03 + 0.0012 * r * (0.5 + rng.random(n_field))
        self.fnear = ss(25.0, 110.0, r)              # calm near the drop and the first people
        self.fseed = rng.random(n_field)
        warm = rng.random(n_field)[:, None]
        self.fcol = lin("#ffd890")[None] * (1 - warm) + lin("#ffb0a0")[None] * warm * 0.9

    def radius(self, t):
        return max(t - self.t0, 0.0) * self.v

    def sample(self, t):
        if t < self.t0 or t > self.until:
            return None
        out = []
        R = self.radius(t)
        if R < self.reach:
            # the front thins as it races away (never a white wall at the horizon)
            k = (1.0 - sc(0.25 * self.reach, 0.7 * self.reach, R)) * sc(0.0, 2.5, R) * (0.35 + 0.65 * np.exp(-R / 60.0))
            w = 0.25 + 0.004 * R
            rr = R + (self.rs - 0.5) * w
            pos = self.c + np.stack([np.sin(self.ang) * rr, np.full(len(rr), 0.05), np.cos(self.ang) * rr], 1)
            sz = 0.05 + 0.0015 * R
            out.append(dict(pos=pos, size=sz, color=self.core, alpha=0.55 * k, emit=1.8, kind="spark",
                            twinkle=0.4, seed=self.rs))
            out.append(dict(pos=pos[::4], size=sz * 5.0, color=self.col, alpha=0.05 * k, kind="soft"))
        g = 1.0 - sc(self.until - 1.0, self.until, t)
        out.append(dict(pos=self.fpos, size=self.fsize, color=self.fcol, alpha=0.40 * g * self.fnear, birth=self.fbirth,
                        fade=0.5, flash=3.0, emit=1.2, kind="spark", twinkle=0.7, seed=self.fseed))
        return out


# ---------------------------------------------------------------------------------------------------- rivers
class LightRiver:
    """A river of light flowing over the sea: a band of sparks and soft glows streaming along a path (a list of
    points), meandering to the horizon. Prismatic glints ride in it. gain(t) its strength."""

    def __init__(self, path, width=3.0, n=26000, speed=9.0, gain=None, seed=41, color="#ffd89a",
                 color2="#fff4e0", prism=0.25):
        rng = np.random.default_rng(seed)
        p = np.asarray(path, np.float64)
        seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
        self.s = np.concatenate([[0.0], np.cumsum(seg)])
        self.L = float(self.s[-1])
        self.p = p
        self.u0 = rng.random(n) * self.L
        self.v = speed * (0.75 + 0.5 * rng.random(n))
        self.lat = rng.normal(0.0, 0.32, n) * width
        self.lift = 0.02 + 0.10 * rng.random(n) ** 3
        self.seed = rng.random(n)
        self.size = 0.03 + 0.08 * rng.random(n) ** 2
        hue = rng.random(n)
        pr = rng.random(n) < prism
        c = lin(color)[None] * (1 - rng.random(n)[:, None] * 0.6) + lin(color2)[None] * rng.random(n)[:, None] * 0.6
        c[pr] = hsv(hue[pr], 0.55, 1.0)
        self.col = c
        self._gain = gain
        self.width = width

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def at(self, s):
        s = np.clip(s, 0.0, self.L - 1e-6)
        i = np.searchsorted(self.s, s, side="right") - 1
        i = np.clip(i, 0, len(self.p) - 2)
        f = (s - self.s[i]) / np.maximum(self.s[i + 1] - self.s[i], 1e-9)
        a, b = self.p[i], self.p[i + 1]
        d = (b - a)
        d = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
        n = np.stack([-d[:, 2], np.zeros(len(d)), d[:, 0]], 1)
        return a + (b - a) * f[:, None], n

    wants_camera = True

    def sample(self, t, cam=None):
        g = self.gain(t)
        if g <= 0.002:
            return None
        s = np.mod(self.u0 + self.v * t, self.L)
        c, nrm = self.at(s)
        wob = 0.25 * np.sin(0.7 * s + 6.0 * self.seed + 1.3 * t)
        pos = c + nrm * (self.lat + wob * self.width * 0.1)[:, None]
        pos[:, 1] = self.lift
        edge = ss(0.0, 30.0, s) * (1.0 - ss(self.L - 30.0, self.L, s))
        al = g * edge * np.exp(-0.5 * (self.lat / (0.55 * self.width)) ** 2)
        if cam is not None:                          # nothing large or bright right at the lens
            dist = np.linalg.norm(pos - np.asarray(cam.pos, np.float64), axis=1)
            al = al * ss(0.6, 2.0, dist)
        else:
            dist = np.full(len(pos), 100.0)
        k = slice(None, None, 40)
        soft_al = 0.05 * al[k] * ss(4.0, 12.0, dist[k])
        return [dict(pos=pos, size=self.size, color=self.col, alpha=0.85 * al, emit=1.8, kind="spark",
                     twinkle=0.6, seed=self.seed),
                dict(pos=pos[k], size=self.width * 0.55, color=lin("#ffcf8a"), alpha=soft_al, kind="soft",
                     streak=0.2)]


# ---------------------------------------------------------------------------------------------------- rain
class RainOfLight:
    """A soft rain of light round a place: fine falling streaks of warm white. tau(t) is the rain's own clock
    (it may slow, hang and run backward: the drops then rise as warm sparks). warm(t) 0..1 turns them gold."""

    def __init__(self, center, radius=9.0, top=14.0, n=5000, speed=4.5, tau=None, warm=None, gain=None, seed=51):
        rng = np.random.default_rng(seed)
        c = np.asarray(center, np.float64)
        a = rng.uniform(0.0, TAU, n)
        r = radius * np.sqrt(rng.random(n))
        self.xz = np.stack([c[0] + np.sin(a) * r, c[2] + np.cos(a) * r], 1)
        self.ph = rng.random(n)
        self.top, self.v = top, speed * (0.8 + 0.4 * rng.random(n))
        self.seed = rng.random(n)
        self.tau = tau or (lambda t: t)
        self.warm = warm or (lambda t: 0.0)
        self._gain = gain

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.002:
            return None
        tau = float(self.tau(t))
        dt = 1.0 / 30.0
        rate = (float(self.tau(t + dt)) - float(self.tau(t - dt))) / (2 * dt)
        y = self.top * (1.0 - np.mod(self.ph + self.v * tau / self.top, 1.0))
        p = np.stack([self.xz[:, 0], y, self.xz[:, 1]], 1)
        w = float(self.warm(t))
        col = lin("#e8eeff") * (1 - w) + lin("#ffd38a") * w
        fade = ss(0.0, 1.5, y) * (1.0 - ss(self.top - 2.0, self.top, y))
        al = g * 0.32 * fade
        if abs(rate) > 0.15:
            L = np.clip(0.16 * self.v * rate, -0.6, 0.6)[:, None] * np.array([[0.0, 1.0, 0.0]])
            return dict(pos=p, pos2=p + L, size=0.010, color=col, alpha=al, kind="line", seed=self.seed)
        return dict(pos=p, size=0.03, color=col, alpha=al * 1.5, emit=1.5, kind="spark", twinkle=0.6,
                    seed=self.seed)


# ---------------------------------------------------------------------------------------------------- lights
class RisingLights:
    """Hundreds of small warm lights round a place that wake in a wave from the middle and rise slowly into the
    sky (the prayers of many), each flickering a little."""

    def __init__(self, center, t_wake, r0=2.0, r1=40.0, n=600, speed=14.0, until=1e9, color="#ffcf7a",
                 color2="#ffb0c0", seed=61, h0=0.3, h1=4.0, rise=0.7):
        rng = np.random.default_rng(seed)
        a = rng.uniform(0.0, TAU, n)
        rad = r0 + (r1 - r0) * np.sqrt(rng.random(n))
        c = np.asarray(center, np.float64)
        self.base = c + np.stack([np.sin(a) * rad, h0 + (h1 - h0) * rng.random(n), np.cos(a) * rad], 1)
        self.wake = t_wake + rad / speed + 0.3 * rng.random(n)
        self.s = rng.random((n, 3))
        mix = rng.random(n)[:, None] < 0.25
        self.col = np.where(mix, lin(color2)[None], lin(color)[None])
        self.until = until
        self.rise = rise

    def sample(self, t):
        if t < self.wake.min() - 0.1 or t > self.until:
            return None
        age = np.maximum(t - self.wake, 0.0)
        lit = ss(0.0, 0.6, age)
        if lit.max() <= 0.0:
            return None
        pos = self.base + np.array([0.0, 1.0, 0.0])[None] * (self.rise * age + 0.05 * age * age)[:, None]
        pos[:, 0] += 0.3 * np.sin(t * 0.8 + 6.0 * self.s[:, 0])
        fl = 0.85 + 0.15 * np.sin(t * 9.0 + 20.0 * self.s[:, 1])
        g = 1.0 - sc(self.until - 1.0, self.until, t)
        al = lit * fl * g
        return [dict(pos=pos, size=0.10 + 0.06 * self.s[:, 2], color=self.col, alpha=0.9 * al, emit=2.2,
                     kind="spark", seed=self.s[:, 2], twinkle=0.3),
                dict(pos=pos, size=0.55 + 0.3 * self.s[:, 1], color=self.col, alpha=0.10 * al, kind="soft")]


class LightColumns:
    """A cathedral of falling light: tall columns of light standing on the sea round a place (two rows that
    meet behind it, like the nave of a cathedral), each a soft core with sparks falling down it."""

    def __init__(self, places, top=34.0, per=520, gain=None, seed=71, color="#ffe2a8", color2="#fff6e6",
                 core_w=1.1, fall=3.0, ring=0.0, core=True, spark=0.06, core_k=1.0, soft=False):
        rng = np.random.default_rng(seed)
        self.base = np.asarray(places, np.float64)
        m = len(self.base)
        self.top = np.full(m, top) * (0.85 + 0.3 * rng.random(m))
        k = m * per
        self.pi = np.repeat(np.arange(m), per)
        self.ph = rng.random(k)
        if ring > 0.0:                          # sparks falling round someone, never in front of them
            a = rng.uniform(0.0, TAU, k)
            r = ring * (1.0 + 0.35 * rng.random(k))
            self.j = np.stack([np.sin(a) * r, np.cos(a) * r], 1)
        else:
            self.j = rng.normal(size=(k, 2)) * 0.35
        self.core = core
        self.soft = soft
        self.core_k = core_k
        self.spark = spark
        self.v = fall * (0.7 + 0.6 * rng.random(k))
        self.sd = rng.random(k)
        self.col = lin(color)
        self.col2 = lin(color2)
        self.core_w = core_w
        self._gain = gain

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.002:
            return None
        pi = self.pi
        top = self.top[pi]
        y = top * (1.0 - np.mod(self.ph + self.v * t / top, 1.0))
        p = self.base[pi] + np.stack([self.j[:, 0], y, self.j[:, 1]], 1)
        al = g * 0.75 * ss(0.0, 2.0, y) * (0.4 + 0.6 * y / top)
        b = self.base
        out = [dict(pos=p, size=self.spark, color=self.col2, alpha=al, emit=1.6,
                    kind="soft" if self.soft else "spark", seed=self.sd, twinkle=0.5)]
        if self.core:
            out += [dict(pos=b, pos2=b + np.stack([np.zeros(len(b)), self.top, np.zeros(len(b))], 1),
                         size=self.core_w, color=self.col, alpha=0.16 * g * self.core_k,
                         alpha2=0.03 * g * self.core_k, kind="ribbon"),
                    dict(pos=b + np.array([0.0, 0.05, 0.0]), size=3.0, color=self.col, alpha=0.12 * g * self.core_k,
                         kind="soft")]
        return out


class Door:
    """A doorway of light standing on the sea: two posts and a round arch of bright sparks with a soft glow,
    its opening a faint warm veil of light that brightens as it opens. facing: degrees (0 faces +z)."""

    def __init__(self, at, width=1.5, height=2.7, facing=0.0, t_open=20.6, gain=None, n=2200, seed=73,
                 color="#ffe6b8", veil="#ffd9a0"):
        rng = np.random.default_rng(seed)
        a = np.radians(facing)
        self.r = np.array([np.cos(a), 0.0, -np.sin(a)])
        self.n = np.array([np.sin(a), 0.0, np.cos(a)])
        self.c = np.asarray(at, np.float64)
        w2 = width * 0.5
        hp = height - w2                       # where the posts end and the arch begins
        L = 2 * hp + np.pi * w2
        s = np.sort(rng.random(n)) * L
        x = np.where(s < hp, -w2, np.where(s > hp + np.pi * w2, w2, 0.0))
        y = np.where(s < hp, s, np.where(s > hp + np.pi * w2, L - s, 0.0))
        arc = (s >= hp) & (s <= hp + np.pi * w2)
        th = np.pi - (s[arc] - hp) / w2
        x[arc] = w2 * np.cos(th)
        y[arc] = hp + w2 * np.sin(th)
        j = rng.normal(size=(n, 3)) * 0.035
        self.frame = self.c + x[:, None] * self.r + y[:, None] * np.array([0.0, 1.0, 0.0]) + j
        self.fs = rng.random(n)
        m = 700
        vx = rng.uniform(-w2, w2, m)
        vy = rng.uniform(0.0, height, m)
        ok = (vy < hp) | ((vx ** 2 + (vy - hp) ** 2) < w2 * w2)
        self.veil = self.c + vx[ok, None] * self.r + vy[ok, None] * np.array([0.0, 1.0, 0.0])
        self.vs = rng.random(int(ok.sum()))
        self.col, self.vcol = lin(color), lin(veil)
        self.t_open = t_open
        self._gain = gain
        self.height = height

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.002:
            return None
        o = sc(self.t_open - 0.6, self.t_open + 0.8, t)
        draw = float(np.clip((t - (self.t_open - 1.4)) / 1.0, 0.0, 1.0))
        tw = 0.8 + 0.2 * np.sin(t * 6.0 + 30.0 * self.fs)
        out = [dict(pos=self.frame, size=0.026, color=self.col, alpha=0.55 * g * draw * tw, emit=1.8, kind="spark",
                    twinkle=0.5, seed=self.fs),
               dict(pos=self.frame[::8], size=0.30, color=self.col, alpha=0.05 * g * draw, kind="soft"),
               dict(pos=self.veil, size=0.30, color=self.vcol, alpha=(0.004 + 0.012 * o) * g, kind="soft",
                    seed=self.vs),
               dict(pos=self.c[None] + np.array([[0.0, 0.04, 0.0]]), size=2.2, color=self.col,
                    alpha=0.08 * g * draw, kind="soft")]
        return out


class PetalStream:
    """Petals of light streaming along a path (through a doorway, past someone's open palm): painted petals that
    turn and flash as they fly. path: points (K, 3); t0..t1 when they flow."""

    def __init__(self, path, t0, t1, n=1400, speed=4.5, spread=0.35, seed=75,
                 colors=("#ffd6e2", "#ffe6b0", "#fff2f6", "#ffc0d0")):
        rng = np.random.default_rng(seed)
        p = np.asarray(path, np.float64)
        seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
        self.cs = np.concatenate([[0.0], np.cumsum(seg)])
        self.L = float(self.cs[-1])
        self.p = p
        self.t0, self.t1 = t0, t1
        self.ph = rng.random(n)
        self.v = speed * (0.7 + 0.6 * rng.random(n))
        self.off = rng.normal(size=(n, 3)) * spread
        self.rot = rng.random((n, 2)) * TAU
        self.spin = rng.normal(size=(n, 2)) * 3.0
        self.col = np.array([lin(colors[i % len(colors)]) for i in range(n)])
        self.s = rng.random(n)

    def _at(self, s):
        s = np.clip(s, 0.0, self.L - 1e-6)
        i = np.clip(np.searchsorted(self.cs, s, side="right") - 1, 0, len(self.p) - 2)
        f = ((s - self.cs[i]) / np.maximum(self.cs[i + 1] - self.cs[i], 1e-9))[:, None]
        return self.p[i] * (1 - f) + self.p[i + 1] * f

    def sample(self, t):
        if t < self.t0 or t > self.t1 + self.L / 2.0:
            return None
        age = (t - self.t0) * self.v
        s = np.mod(self.ph * self.L + age, self.L)
        born = (t - self.t0) * self.v >= (self.L - self.ph * self.L) * 0.0
        stop = t > self.t1
        s_raw = self.ph * self.L + age
        alive = born & ((~stop) | (s_raw - (t - self.t1) * self.v < self.L))
        wob = np.stack([np.sin(t * 2.0 + 9.0 * self.s), 0.6 * np.sin(t * 1.3 + 5.0 * self.s),
                        np.cos(t * 1.7 + 7.0 * self.s)], 1) * 0.12
        pos = self._at(s) + self.off * (0.4 + 0.6 * s[:, None] / self.L) + wob
        edge = ss(0.0, 1.5, s) * (1.0 - ss(self.L - 2.0, self.L, s))
        k = sc(self.t0, self.t0 + 0.6, t) * (1.0 - sc(self.t1, self.t1 + 1.0, t))
        rot = self.rot + self.spin * t
        return dict(pos=pos, size=0.06 + 0.04 * self.s, color=self.col, alpha=0.9 * edge * k * alive, emit=1.4,
                    kind="petal", rot=rot, seed=self.s)


class TreeOfLight:
    """A tree of light: a trunk and boughs of fine glowing lines that branch and lift, crowned with blossoms of
    light (pink, gold and white) that open from the trunk outward, petals drifting down. A static shape."""

    def __init__(self, at, height=5.2, t_bloom=23.6, gain=None, seed=77, depth=6):
        rng = np.random.default_rng(seed)
        segs, tips, order = [], [], []
        base = np.asarray(at, np.float64)

        def grow(p, d, L, lvl, o):
            q = p + d * L
            segs.append((p, q, o))
            if lvl >= depth:
                tips.append((q, o))
                return
            k = 2 if lvl < 2 else rng.integers(2, 4)
            for _ in range(int(k)):
                axis = np.cross(d, rng.normal(size=3))
                axis /= max(np.linalg.norm(axis), 1e-6)
                ang = np.radians(rng.uniform(22.0, 42.0))
                nd = d * np.cos(ang) + np.cross(axis, d) * np.sin(ang)
                nd[1] += 0.18
                nd /= np.linalg.norm(nd)
                grow(q, nd, L * rng.uniform(0.62, 0.78), lvl + 1, o + 1)
        grow(base, np.array([0.0, 1.0, 0.0]), height * 0.36, 0, 0)
        self.a = np.array([s[0] for s in segs])
        self.b = np.array([s[1] for s in segs])
        self.so = np.array([s[2] for s in segs], np.float64)
        tp = np.array([q for q, _ in tips])
        m = 28
        bl = (tp[:, None, :] + rng.normal(size=(len(tp), m, 3)) * np.array([0.32, 0.22, 0.32])).reshape(-1, 3)
        self.bl = bl
        self.bs = rng.random(len(bl))
        cols = [lin("#ff9ec4"), lin("#ffd890"), lin("#ffc0a0"), lin("#ff86b4")]
        self.bcol = np.array([cols[i % 4] for i in range(len(bl))])
        r = np.linalg.norm(bl[:, [0, 2]] - base[[0, 2]], axis=1)
        self.bbirth = t_bloom + 0.12 * r + 0.4 * self.bs
        self.t_bloom = t_bloom
        self._gain = gain
        self.base = base
        self.height = height

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.002:
            return None
        w = 0.05 * (0.62 ** self.so) + 0.006
        out = [dict(pos=self.a, pos2=self.b, size=w, size2=w * 0.75, color=lin("#ffd9a0"), alpha=0.75 * g,
                    emit=1.6, kind="line"),
               dict(pos=self.a, pos2=self.b, size=w * 6.0, color=lin("#ffb878"), alpha=0.06 * g, kind="ribbon"),
               dict(pos=self.bl, size=0.035 + 0.03 * self.bs, color=self.bcol, alpha=0.32 * g, birth=self.bbirth,
                    fade=0.5, flash=1.5, emit=1.2, kind="spark", twinkle=0.5, seed=self.bs),
               dict(pos=self.bl[::9], size=0.45, color=self.bcol[::9], alpha=0.012 * g, birth=self.bbirth[::9],
                    fade=0.6, kind="soft")]
        u = t - self.t_bloom
        if u > 0.0:                               # a few petals drift down from the crown
            k = len(self.bl) // 30
            sel = self.bl[::30][:k]
            ph = self.bs[::30][:k]
            fall = np.mod(ph * 6.0 + 0.6 * u, 6.0)
            pos = sel + np.stack([0.4 * np.sin(1.3 * t + 9 * ph) + 0.3 * fall, -fall, 0.3 * np.cos(t + 7 * ph)], 1)
            low = ss(0.05, 0.8, pos[:, 1])                  # they melt away before they reach the water
            out.append(dict(pos=pos, size=0.035, color=self.bcol[::30][:k], alpha=0.7 * g * ss(0.0, 0.8, u) * low,
                            kind="petal", rot=np.stack([t * 2 + ph * 9, t * 3 + ph * 5], 1), emit=1.3))
        return out


class Motes:
    """Fine motes of light hanging in the air round a place (or round the camera when center is None)."""
    wants_camera = True

    def __init__(self, n=1500, box=(16.0, 7.0, 16.0), center=None, gain=None, seed=81, color="#ffe8c0",
                 color2="#ffc8d8", size=0.02):
        rng = np.random.default_rng(seed)
        self.u = rng.random((n, 3))
        self.box = np.asarray(box, np.float64)
        self.center = center
        self.s = rng.random((n, 2))
        mix = rng.random(n)[:, None]
        self.col = lin(color)[None] * (1 - mix) + lin(color2)[None] * mix
        self._gain = gain
        self.size = size

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t, cam=None):
        g = self.gain(t)
        if g <= 0.002:
            return None
        if self.center is not None:
            c = np.asarray(self.center(t) if callable(self.center) else self.center, np.float64)
        else:
            c = np.asarray(cam.pos if cam is not None else (0.0, 0.0, 0.0), np.float64)
        drift = np.array([0.05, 0.08, 0.03]) * t
        q = np.mod(self.u + drift / self.box, 1.0) - 0.5
        pos = c + q * self.box
        edge = 1.0 - ss(0.35, 0.5, np.max(np.abs(q), axis=1))
        tw = 0.6 + 0.4 * np.sin(t * (1.0 + 2.0 * self.s[:, 0]) + 6.0 * self.s[:, 1])
        return dict(pos=pos, size=self.size * (0.6 + 0.8 * self.s[:, 0]), color=self.col,
                    alpha=0.8 * g * edge * tw, emit=1.4, kind="spark", seed=self.s[:, 1], twinkle=0.6)


class Fountain:
    """On a hit, thousands of sparks shoot up from a place in a great fountain, open out, and drift down slowly
    as warm light (the nine colours among the gold)."""

    def __init__(self, at, t0, n=6000, colors=None, speed=(10.0, 26.0), spread=0.35, seed=95, life=3.2):
        rng = np.random.default_rng(seed)
        self.at = np.asarray(at, np.float64)
        self.t0, self.life = t0, life
        a = rng.uniform(0.0, TAU, n)
        el = np.radians(90.0 - np.abs(rng.normal(0.0, np.degrees(spread) * 0.6, n)))
        sp = rng.uniform(*speed, n)
        self.v = np.stack([np.sin(a) * np.cos(el), np.sin(el), np.cos(a) * np.cos(el)], 1) * sp[:, None]
        self.s = rng.random(n)
        cols = [lin(c) for c in (colors or ["#ffd27a"])]
        gold = lin("#ffd890")
        self.col = np.array([cols[i % len(cols)] if rng.random() < 0.45 else gold for i in range(n)])

    def sample(self, t):
        u = t - self.t0
        if u < 0.0 or u > self.life:
            return None
        drag = (1.0 - np.exp(-u * 1.6)) / 1.6
        p = self.at + self.v * drag + np.array([0.0, -1.2, 0.0]) * u * u
        al = (1.0 - ss(0.45 * self.life, self.life, u)) * (0.6 + 0.4 * self.s)
        return dict(pos=p, size=0.05 + 0.08 * self.s, color=self.col, alpha=al, emit=2.2, kind="spark",
                    twinkle=0.6, seed=self.s, streak=1.0)


class ColorRing:
    """A ring of the nine colours racing out over the sea from a place (each colour its own arc)."""

    def __init__(self, center, t0, colors, speed=60.0, reach=1200.0, n=3600, seed=97):
        rng = np.random.default_rng(seed)
        self.c = np.asarray(center, np.float64)
        self.t0, self.v, self.reach = t0, speed, reach
        self.ang = np.linspace(0.0, TAU, n, endpoint=False)
        k = (self.ang / TAU * len(colors)).astype(int) % len(colors)
        self.col = np.array([lin(colors[i]) for i in k])
        self.s = rng.random(n)

    def sample(self, t):
        u = t - self.t0
        if u < 0.0:
            return None
        R = u * self.v
        if R > self.reach:
            return None
        k = (1.0 - ss(0.3 * self.reach, self.reach, R)) * ss(0.0, 3.0, R)
        rr = R + (self.s - 0.5) * (0.3 + 0.01 * R)
        pos = self.c + np.stack([np.sin(self.ang) * rr, np.full(len(rr), 0.06), np.cos(self.ang) * rr], 1)
        sz = 0.08 + 0.003 * R
        return [dict(pos=pos, size=sz, color=self.col, alpha=0.8 * k, emit=2.0, kind="spark", twinkle=0.3,
                     seed=self.s),
                dict(pos=pos[::4], size=sz * 6.0, color=self.col[::4], alpha=0.06 * k, kind="soft")]
