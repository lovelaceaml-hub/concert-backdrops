"""The storm of film 08, Storm to Peace (engine/songs/ten_08_storm_to_peace.py): point sets of its own.

Pure numpy, pure functions of time (and of the camera at t), so any part of the video renders the same
frames. Every set reads one calm field, calm(x, z, t) in 0..1 (0 the open storm, 1 glass), given by the song.

  Sea        a heaving sea of points fixed in the world round the camera (a dense near lattice and a sparse
             far one, both wrapped round the camera so they never end); crests bright, troughs dark; where
             the calm is 1 the points lie flat as faint glints on the glass, and at the edge of a calm they
             burn as a line of light
  Rain       slanting streaks of cold light round the camera; where the speed falls to 0 every streak stops
             in the air and becomes a bead of light (the rain hangs); no rain falls on the glass
  Beads      a still cloud of beads of light round a place (the stopped rain a word is made of)
  Bolt       a branching bolt of lightning that flickers, or stops in the air and changes colour
  Glow       a huge soft light in the cloud that flashes with the lightning
  Drop       one slow coral drop that falls from the cloud and lands
"""
import numpy as np

from .api import lin, ribbon


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _hash(i, salt=0):
    x = (np.asarray(i, np.int64) * 374761393 + salt * 668265263) & 0xFFFFFFFF
    x = ((x ^ (x >> 13)) * 1274126177) & 0xFFFFFFFF
    x = x ^ (x >> 16)
    return (x & 0xFFFFFF) / float(0x1000000)


def _val(v, t):
    return float(v(t)) if callable(v) else float(v)


def _wrap(p, c, L):
    """Fold world positions p (N, k) into a box of size L centred on c: fixed in the world, never ending."""
    return c - 0.5 * L + np.mod(p - (c - 0.5 * L), L)


# The storm's waves: (wavelength m, amplitude m, direction degrees from +x toward +z, phase)
WAVES = [(23.0, 0.85, 8.0, 0.3), (13.0, 0.50, -26.0, 1.9), (8.3, 0.30, 38.0, 4.1), (4.6, 0.14, -55.0, 2.7),
         (2.6, 0.06, 15.0, 5.3)]
G = 9.81


def sea_height(x, z, t, amp=1.0):
    """Height (m) of the open storm sea at (x, z) and its horizontal push (Gerstner), before the calm."""
    h = np.zeros(np.broadcast(x, z).shape)
    dx = np.zeros_like(h)
    dz = np.zeros_like(h)
    for lam, a, ang, ph in WAVES:
        k = 2.0 * np.pi / lam
        w = np.sqrt(G * k)
        c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
        th = k * (c * x + s * z) - w * t + ph
        h += a * np.sin(th)
        q = 0.55 * a
        dx -= q * c * np.cos(th)
        dz -= q * s * np.cos(th)
    return h * amp, dx * amp, dz * amp


class Sea:
    """The heaving sea of points. calm(x, z, t) 0..1; storm(t) the height of the open sea (0..1.3);
    flash(t) the lightning; edge_color the line of light at the edge of a calm; glass(t) how strong the
    faint glints on the glass are."""
    wants_camera = True

    def __init__(self, calm, storm, flash, glass=0.12, edge=1.0, warm=None, seed=8):
        self.calm, self.storm, self.flash, self.glass, self.edge = calm, storm, flash, glass, edge
        self.warm = warm if warm is not None else (lambda t: 0.0)
        self.layers = []
        for L, d, size, salt in ((56.0, 0.30, 0.055, 1), (260.0, 1.15, 0.17, 2)):
            n = int(round(L / d))
            i, j = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
            i, j = i.ravel(), j.ravel()
            k = i * 1000 + j
            jx, jz = _hash(k, salt), _hash(k, salt + 7)
            base = np.stack([(i + jx) * d, (j + jz) * d], axis=1)
            self.layers.append(dict(L=L, base=base, size=size * (0.7 + 0.6 * _hash(k, salt + 3)),
                                    seed=_hash(k, salt + 11)))
        self.c_trough = lin("#1d3a58") * 0.22
        self.c_crest = lin("#c6dcff") * 1.05
        self.c_foam = lin("#eef4ff") * 1.6
        self.c_edge = lin("#ffd6a0") * 2.2
        self.c_glass = lin("#ffe7c4") * 0.9
        self.c_flash = lin("#d8ccff")

    def sample(self, t, cam):
        out = []
        cp = np.asarray(cam.pos, np.float64)
        fwd = np.asarray(cam.target, np.float64) - cp
        fwd[1] = 0.0
        fwd /= max(np.linalg.norm(fwd), 1e-6)
        storm = _val(self.storm, t)
        fl = _val(self.flash, t)
        warm = _val(self.warm, t)
        for li, ly in enumerate(self.layers):
            L = ly["L"]
            c = cp[[0, 2]] + fwd[[0, 2]] * (0.32 * L)
            p = _wrap(ly["base"], c, L)
            x, z = p[:, 0], p[:, 1]
            r = np.hypot(x - cp[0], z - cp[2])
            if li == 0:
                vis = 1.0 - _ss(19.0, 27.0, r)
            else:
                vis = _ss(17.0, 25.0, r) * (1.0 - _ss(0.36 * L, 0.48 * L, np.hypot(x - c[0], z - c[1])))
            keep = vis > 0.004
            x, z, vis, r = x[keep], z[keep], vis[keep], r[keep]
            size = ly["size"][keep]
            seed = ly["seed"][keep]
            cm = np.clip(self.calm(x, z, t), 0.0, 1.0)
            h, dx, dz = sea_height(x, z, t, storm)
            open_ = 1.0 - cm
            y = h * open_ + 0.03
            px, pz = x + dx * open_, z + dz * open_
            amp = max(storm * 1.9, 1e-3)
            cr = np.clip((h / amp + 0.25) / 1.0, 0.0, 1.0) ** 2.2
            col = self.c_trough[None, :] * (1.0 - cr[:, None]) + self.c_crest[None, :] * cr[:, None]
            foam = np.clip((h / amp - 0.55) / 0.3, 0.0, 1.0) * (seed > 0.55)
            col = col + self.c_foam[None, :] * foam[:, None]
            col = col * (1.0 + 1.6 * fl) + self.c_flash[None, :] * (0.35 * fl * cr)[:, None]
            ring = np.clip(4.0 * cm * (1.0 - cm), 0.0, 1.0) ** 1.5 * self.edge * (0.25 + 0.75 * _ss(3.0, 10.0, r))
            gl = _val(self.glass, t)
            glass_col = self.c_glass * (1.0 + 0.6 * warm)
            col = col * open_[:, None] + glass_col[None, :] * (cm * (seed > 0.72))[:, None] + \
                self.c_edge[None, :] * ring[:, None]
            alpha = vis * np.clip(open_ * 0.95 + cm * gl * (seed > 0.72) * _ss(4.0, 12.0, r) + ring, 0.0, 1.0)
            pos = np.stack([px, y, pz], axis=1)
            out.append(dict(pos=pos, size=size * (1.0 + 0.8 * ring), color=col, alpha=alpha, kind="soft",
                            seed=seed, twinkle=0.35, emit=1.0 + 1.5 * ring + 1.2 * foam, reflect=False))
        return out


class Rain:
    """Slanting streaks round the camera. speed(t) 0..1 (0: every drop hangs as a bead), amount(t) 0..1,
    calm(x, z, t): no rain over the glass."""
    wants_camera = True

    def __init__(self, calm, speed, amount, n=26000, box=(34.0, 20.0, 34.0), vel=(3.4, -9.5, 0.9),
                 color="#cfe0ff", bead="#ffe6ee", length=0.75, seed=3):
        rng = np.random.default_rng(seed)
        self.calm, self.speed, self.amount = calm, speed, amount
        self.L = np.asarray(box, np.float64)
        self.p0 = rng.uniform(0.0, 1.0, (n, 3)) * self.L
        self.vel = np.asarray(vel, np.float64)
        self.vel_u = self.vel / np.linalg.norm(self.vel)
        self.seed = rng.uniform(0.0, 1.0, n)
        self.jit = 0.8 + 0.4 * rng.uniform(0.0, 1.0, n)
        self.c_rain, self.c_bead = lin(color), lin(bead)
        self.length = length
        tt = np.arange(0.0, 61.0, 1.0 / 120.0)
        sp = np.array([_val(speed, x) for x in tt])
        self._tt, self._tau = tt, np.concatenate([[0.0], np.cumsum(0.5 * (sp[1:] + sp[:-1]) * np.diff(tt))])

    def tau(self, t):
        return float(np.interp(t, self._tt, self._tau))

    def sample(self, t, cam):
        am = _val(self.amount, t)
        if am <= 0.003:
            return []
        sp = _val(self.speed, t)
        cp = np.asarray(cam.pos, np.float64)
        fwd = np.asarray(cam.target, np.float64) - cp
        fwd /= max(np.linalg.norm(fwd), 1e-6)
        c = cp + fwd * 0.3 * self.L[0]
        c[1] = 0.5 * self.L[1] - 0.5
        p = self.p0 + self.vel[None, :] * (self.tau(t) * self.jit[:, None])
        p = _wrap(p, c, self.L)
        d = np.abs(p - c) / (0.5 * self.L)
        vis = (1.0 - _ss(0.7, 1.0, d[:, 0])) * (1.0 - _ss(0.7, 1.0, d[:, 2])) * _ss(0.0, 0.6, p[:, 1])
        vis *= 1.0 - np.clip(self.calm(p[:, 0], p[:, 2], t), 0.0, 1.0) * min(sp * 2.0, 1.0)
        vis *= _ss(1.2, 5.0, np.linalg.norm(p - cp[None, :], axis=1))     # no thick bars across the lens
        out = []
        if sp > 0.02:
            ln = self.length * sp
            out.append(dict(pos=p, pos2=p - self.vel_u[None, :] * ln, size=0.006, color=self.c_rain,
                            alpha=vis * am * 0.42 * min(sp * 3.0, 1.0), kind="line", seed=self.seed, reflect=False))
        if sp < 0.98:
            k = 1.0 - sp
            near = _ss(2.5, 7.0, np.linalg.norm(p - cp[None, :], axis=1))
            sel = (self.seed < 0.55) | (near > 0.5)
            out.append(dict(pos=p[sel], size=0.02 + 0.014 * self.seed[sel], color=self.c_bead,
                            alpha=(vis * am * k * (0.25 + 0.4 * near))[sel], kind="soft", twinkle=0.5,
                            seed=self.seed[sel], emit=1.3, reflect=False))
        return out


class Beads:
    """A still cloud of beads of light round `center` (radius, heights y0..y1), seen from t_in to t_out."""

    def __init__(self, center, radius, y0, y1, t_in, t_out, n=5000, color="#fff0e6", seed=5, fall=None):
        rng = np.random.default_rng(seed)
        a = rng.uniform(0.0, 2.0 * np.pi, n)
        r = radius * np.sqrt(rng.uniform(0.0, 1.0, n))
        self.p = np.stack([center[0] + r * np.cos(a), rng.uniform(y0, y1, n), center[2] + r * np.sin(a)], axis=1)
        o = np.argsort(self.p[:, 0])
        self.p = self.p[o]
        self.seed = rng.uniform(0.0, 1.0, n)
        self.t_in, self.t_out, self.c = t_in, t_out, lin(color)
        self.fall = fall

    def sample(self, t):
        a = float(_ss(self.t_in, self.t_in + 0.4, t) * (1.0 - _ss(self.t_in + 0.5, self.t_out, t)))
        p = self.p
        if self.fall is not None and t > self.fall:
            p = p.copy()
            p[:, 1] = np.maximum(p[:, 1] - (t - self.fall) * (0.6 + 0.6 * self.seed), 0.02)
        return dict(pos=p, size=0.026 + 0.016 * self.seed, color=self.c, alpha=a * 0.6, kind="soft", twinkle=0.5,
                    seed=self.seed, emit=1.2)


def _bolt_path(top, bottom, seed, n=48, jag=0.16):
    rng = np.random.default_rng(seed)
    top, bottom = np.asarray(top, np.float64), np.asarray(bottom, np.float64)
    u = np.linspace(0.0, 1.0, n)
    p = top[None, :] + (bottom - top)[None, :] * u[:, None]
    L = np.linalg.norm(bottom - top)
    off = np.zeros((n, 3))
    step = jag * L
    for octave in range(5):
        k = 2 ** (octave + 1)
        nodes = rng.normal(0.0, step / (1.6 ** octave), (k + 1, 3))
        nodes[0] = nodes[-1] = 0.0
        nodes[:, 1] *= 0.25
        off += np.stack([np.interp(u, np.linspace(0, 1, k + 1), nodes[:, c]) for c in range(3)], axis=1)
    return p + off


class Bolt:
    """A bolt of lightning from `top` (in the cloud) to `bottom`: it flickers at t_strike; with `freeze` it
    stops in the air from then until `fade` and turns from color to color2 (over `turn` seconds)."""

    def __init__(self, top, bottom, t_strike, seed=1, freeze=None, fade=None, color="#e6dcff", color2="#ffc58a",
                 width=0.10, turn=1.2, branches=4):
        self.paths = [_bolt_path(top, bottom, seed)]
        rng = np.random.default_rng(seed + 100)
        main = self.paths[0]
        for b in range(branches):
            i = int(rng.uniform(0.15, 0.7) * len(main))
            st = main[i]
            d = (np.asarray(bottom) - np.asarray(top)) * rng.uniform(0.25, 0.45)
            d = d + rng.normal(0.0, 0.35 * np.linalg.norm(d), 3)
            d[1] = -abs(d[1]) * 0.8
            self.paths.append(_bolt_path(st, st + d, seed + 7 * b + 3, n=24))
        self.t0, self.freeze, self.fade = t_strike, freeze, fade
        self.c1, self.c2, self.width, self.turn = lin(color), lin(color2), width, turn
        pts = np.concatenate([np.repeat(p, 1, axis=0) for p in self.paths])
        seg = []
        for p in self.paths:
            for a, b in zip(p[:-1], p[1:]):
                m = 12
                w = np.linspace(0.0, 1.0, m, endpoint=False)[:, None]
                seg.append(a[None, :] * (1 - w) + b[None, :] * w)
        self.dense = np.concatenate(seg)
        self._pts = pts

    def level(self, t):
        if t < self.t0:
            return 0.0
        dt = t - self.t0
        fl = 0.0
        for k, (o, g) in enumerate(((0.0, 1.0), (0.09, 0.7), (0.21, 0.9))):
            if dt >= o:
                fl = max(fl, g * np.exp(-(dt - o) / 0.05))
        if self.freeze is not None and t >= self.freeze:
            hold = 0.85 * float(_ss(self.freeze, self.freeze + 0.15, t))
            if self.fade is not None:
                hold *= 1.0 - float(_ss(self.fade - 0.5, self.fade, t))
            fl = max(fl, hold)
        return float(fl)

    def sample(self, t):
        lv = self.level(t)
        k = 0.0 if self.freeze is None else float(_ss(self.freeze, self.freeze + self.turn, t))
        col = self.c1 * (1 - k) + self.c2 * k
        glow = dict(pos=self.dense, size=self.width * 2.2, color=col, alpha=lv * 0.35, kind="soft", emit=2.0,
                    reflect=True, seed=_hash(np.arange(len(self.dense)), 5))
        out = [glow]
        if lv > 0.002:
            for i, p in enumerate(self.paths):
                w = self.width * (1.0 if i == 0 else 0.55)
                out.append(ribbon(p, width=w, color=col * 3.0, alpha=lv))
                out.append(ribbon(p, width=w * 7.0, color=col * 0.5, alpha=lv * 0.35))
        return out


class Glow:
    """Huge soft lights in the cloud that flash with the lightning: places [(x, y, z)], sizes in metres."""

    def __init__(self, flashes, color="#cbbcff", size=140.0):
        self.flashes = flashes          # list of (t, (x, y, z), strength)
        self.c = lin(color)
        self.size = size

    def sample(self, t):
        pos, al = [], []
        for tf, p, s in self.flashes:
            dt = t - tf
            if -0.01 < dt < 0.6:
                a = s * (np.exp(-max(dt, 0.0) / 0.06) + 0.6 * np.exp(-max(dt - 0.13, 0.0) / 0.05) * (dt > 0.13))
                pos.append(p)
                al.append(min(a, 1.5))
        if not pos:
            return []
        return dict(pos=np.asarray(pos, np.float64), size=self.size, color=self.c, alpha=np.asarray(al), kind="soft",
                    reflect=True, fog=False, lod=False)


def flash_level(flashes, t):
    """The lightning's strength at t from the same list as Glow (for the sea and the camera)."""
    v = 0.0
    for tf, _, s in flashes:
        dt = t - tf
        if 0.0 <= dt < 0.8:
            v = max(v, s * (np.exp(-dt / 0.07) + 0.6 * np.exp(-max(dt - 0.13, 0.0) / 0.06) * (dt > 0.13)))
    return float(v)


class Drop:
    """One slow drop of coral light from the cloud: from `top` at t0 to `bottom` at t1, then gone in a flash."""

    def __init__(self, top, bottom, t0, t1, color="#ff977c"):
        self.a, self.b = np.asarray(top, np.float64), np.asarray(bottom, np.float64)
        self.t0, self.t1, self.c = t0, t1, lin(color)

    def sample(self, t):
        if t < self.t0 - 0.2 or t > self.t1 + 0.5:
            return []
        u = float(np.clip((t - self.t0) / (self.t1 - self.t0), 0.0, 1.0))
        e = u * u
        p = self.a + (self.b - self.a) * e
        tail = [self.a + (self.b - self.a) * max(e - k * 0.02, 0.0) for k in range(12)]
        a = float(_ss(self.t0 - 0.2, self.t0 + 0.1, t) * (1.0 - _ss(self.t1, self.t1 + 0.35, t)))
        boom = float(np.exp(-max(t - self.t1, 0.0) / 0.12) * (t >= self.t1))
        out = [dict(pos=p[None, :], size=0.16 + 0.5 * boom, color=self.c * 3.0, alpha=a + boom, kind="soft", emit=3.0),
               dict(pos=p[None, :], size=1.4 + 6.0 * boom, color=self.c, alpha=0.25 * a + 0.4 * boom, kind="soft")]
        out.append(ribbon(np.asarray(tail), width=0.05, color=self.c * 2.0, alpha=0.6 * a))
        return out
