"""Point sets of film 05, Petals (engine/songs/ten_05_petals.py): the wind of petals, the great tree, the
water meadow, the stepping stones, a release of petals and streams of petals from a palm.

Pure numpy, every set a pure function of time (any frame in any order gives the same picture).
Conventions as engine/p3d/api.py: metres, y up, the lake is y = 0, azimuth in degrees from +z toward +x.
"""
import numpy as np

from .api import lin, show

TAU = 2.0 * np.pi


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / max(b - a, 1e-9), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _cols(hexes, n, rng, white=0.0):
    """n display colours picked from a list (as paint colours), mixed toward white by `white`."""
    base = np.array([show(h) for h in hexes], np.float64)
    pick = base[rng.integers(0, len(hexes), n)]
    w = (rng.random(n) * white)[:, None]
    return (pick * (1.0 - w) + show("#ffffff")[None] * w).astype(np.float32)


def _lights(hexes, n, rng, white=0.0):
    base = np.array([lin(h) for h in hexes], np.float64)
    pick = base[rng.integers(0, len(hexes), n)]
    w = (rng.random(n) * white)[:, None]
    return (pick * (1.0 - w) + lin("#ffffff")[None] * w).astype(np.float32)


PETAL_HEX = ("#FF977C", "#FFB79A", "#FFD9C2", "#FFF1DC", "#F7A8C4", "#FFC7D9", "#ffffff", "#FFE29A")


class PetalWind:
    """Petals on the wind round the camera, everywhere the camera goes: a box of drifting petals that travels
    with the lens (petals stay put in the air and only wrap round far away, where they fade), carried by one
    wind with gusts on the music. `amount(t)` 0..1 is the share of petals in the air."""
    wants_camera = True

    def __init__(self, wind, n=7000, box=(34.0, 14.0, 34.0), amount=None, colors=PETAL_HEX, size=(0.028, 0.05),
                 paint=0.9, seed=5):
        rng = np.random.default_rng(seed)
        self.wind, self.n = wind, int(n)
        self.B = np.asarray(box, np.float64)
        self.p0 = rng.random((self.n, 3)) * self.B
        self.s = rng.random((self.n, 8))
        self.col = _cols(colors, self.n, rng, white=0.25)
        self.light = _lights(colors, self.n, rng, white=0.35) * 0.9
        self.size = (size[0] + (size[1] - size[0]) * self.s[:, 6]).astype(np.float32)
        self.amount = amount or (lambda t: 1.0)
        self.paint = paint

    def sample(self, t, cam):
        s = self.s
        a = float(self.amount(t))
        if a <= 0.0:
            return []
        keep = s[:, 7] < a
        d = self.wind.travel(0.0, t)
        ph = s[:, 0] * TAU + t * (0.7 + 0.9 * s[:, 1])
        loc = np.stack([0.7 * np.cos(ph) * s[:, 2], 0.45 * np.sin(1.3 * ph + s[:, 3] * TAU) - 0.25 * t * s[:, 5],
                        0.7 * np.sin(ph) * s[:, 2]], axis=1)
        wp = self.p0 + d[None, :] * (0.75 + 0.5 * s[:, 4:5]) + loc
        c = np.asarray(cam.pos, np.float64)
        f = np.asarray(cam.target, np.float64) - c
        f = f / max(np.linalg.norm(f), 1e-9)
        ctr = c + f * self.B[0] * 0.28
        ctr[1] = max(ctr[1], self.B[1] * 0.5 + 0.02)
        rel = np.mod(wp - ctr + self.B * 0.5, self.B) - self.B * 0.5
        pos = ctr + rel
        e = np.min(0.5 - np.abs(rel) / self.B, axis=1) * 2.0          # 1 in the middle, 0 on the walls
        alpha = _ss(0.0, 0.35, e) * keep * (pos[:, 1] > 0.03)
        rot = np.stack([ph * 0.8 + s[:, 3] * TAU, t * (2.0 + 3.0 * s[:, 1]) + s[:, 2] * TAU], axis=1)
        sel = alpha > 0.01
        return dict(pos=pos[sel].astype(np.float32), size=self.size[sel], color=self.col[sel] if self.paint else
                    self.light[sel], alpha=alpha[sel].astype(np.float32), kind="petal",
                    rot=rot[sel].astype(np.float32), paint=self.paint, paint_light=0.35, twinkle=0.2, seed=s[sel, 0])


def _bez(p0, p1, p2, u):
    u = u[:, None]
    return (1 - u) ** 2 * p0 + 2 * (1 - u) * u * p1 + u * u * p2


class Tree:
    """A great tree of light on a low mound in the lake: a trunk, nine boughs that wind round it like a stair,
    twigs, and blossom. Each bough blossoms in its own colour: a share of it buds when its word comes home
    (`bud` times), the rest bursts open at its `bloom` time. `crown` blossom (white and blush) opens at
    `crown_t`. Static on the graphics card (birth times do the flowering)."""
    static = True

    def __init__(self, base=(0.0, 0.0, 0.0), height=15.0, colors=(), bough_az=None, bud=None, bloom=None,
                 crown_t=None, crown_colors=("#ffffff", "#FFD9E4", "#FFE9D6"), bark="#a88466", bark_light="#ffe6c4",
                 n_bark=26000, n_bloom=3600, n_crown=14000, boughs=9, spread=1.0, seed=11, bright=1.0):
        rng = np.random.default_rng(seed)
        b = np.asarray(base, np.float64)
        k = height / 15.0
        self.k = k
        P, S, C, L, BIRTH, KIND = [], [], [], [], [], []
        # ---- the trunk: a gentle S, flared at the foot
        u = rng.random(int(n_bark * 0.35))
        hgt = u * 9.0 * k
        r = (0.55 * (1.0 - 0.55 * u) + 0.45 * np.exp(-u * 18.0)) * k
        sway = np.stack([0.35 * np.sin(u * 2.4) * k, hgt, 0.2 * np.sin(u * 3.1 + 1.0) * k], axis=1)
        a = rng.random(len(u)) * TAU
        P.append(b + sway + np.stack([np.cos(a) * r, np.zeros_like(r), np.sin(a) * r], axis=1))
        S.append(np.full(len(u), 0.045 * k))
        # ---- the boughs: a spiral stair round the trunk
        nb = int(boughs)
        if bough_az is None:
            bough_az = [30.0 + 137.5 * i for i in range(nb)]
        self.tips, self.mids = [], []
        bark_pts = int(n_bark * 0.65 / nb)
        for i in range(nb):
            az = np.radians(bough_az[i])
            hv = np.array([np.sin(az), 0.0, np.cos(az)])
            h0 = (3.6 + 0.62 * i) * k
            ln = (7.4 - 0.32 * i) * k * spread
            el = np.radians(22.0 + 3.5 * i)
            p0 = b + np.array([0.35 * np.sin(h0 / k / 9.0 * 2.4) * k, h0, 0.0])
            p2 = p0 + hv * ln * np.cos(el) + np.array([0.0, ln * np.sin(el), 0.0])
            p1 = p0 + hv * ln * 0.55 + np.array([0.0, ln * np.sin(el) * 0.15, 0.0])
            self.tips.append(p2)
            self.mids.append(_bez(p0, p1, p2, np.array([0.6]))[0])
            uu = rng.random(bark_pts)
            ax = _bez(p0, p1, p2, uu)
            rr = (0.24 * (1.0 - 0.75 * uu) + 0.03) * k
            aa = rng.random(bark_pts) * TAU
            off = np.stack([np.cos(aa), np.sin(aa) * 0.8, np.sin(aa + 1.3)], axis=1)
            P.append(ax + off * rr[:, None])
            S.append(np.full(bark_pts, 0.035 * k))
        bark_p = np.concatenate(P)
        nbk = len(bark_p)
        self.bark = dict(pos=bark_p.astype(np.float32), size=np.concatenate(S).astype(np.float32),
                         color=np.tile(show(bark), (nbk, 1)).astype(np.float32), alpha=np.full(nbk, 0.9, np.float32),
                         kind="soft", paint=0.75, paint_light=0.45, seed=rng.random(nbk).astype(np.float32),
                         twinkle=0.0, dof=1.0)
        self.bark_glow = dict(pos=bark_p.astype(np.float32), size=(np.concatenate(S) * 1.4).astype(np.float32),
                              color=np.tile(lin(bark_light) * 0.35 * bright, (nbk, 1)).astype(np.float32),
                              alpha=np.full(nbk, 1.0, np.float32), kind="soft", seed=rng.random(nbk).astype(np.float32))
        # ---- blossom: clusters along the outer half of each bough and round its twigs
        BP, BC, BL, BB, BS = [], [], [], [], []
        for i in range(nb):
            col = colors[i % len(colors)] if colors else "#ffd0e0"
            tip, mid = self.tips[i], self.mids[i]
            m = n_bloom
            uu = rng.random(m)
            centre = mid + (tip - mid) * uu[:, None] * 1.25
            # twigs: blobs
            blob = rng.normal(size=(m, 3)) * np.array([1.0, 0.6, 1.0]) * (0.55 + 0.75 * uu)[:, None] * k * spread
            p = centre + blob + np.array([0.0, 0.35 * k, 0.0])
            BP.append(p)
            mix = rng.random(m)
            BC.append(np.where((mix < 0.62)[:, None], show(col)[None], np.where((mix < 0.85)[:, None],
                      show("#ffffff")[None], (0.5 * show(col) + 0.5 * show("#ffffff"))[None])))
            BL.append(np.where((mix < 0.62)[:, None], lin(col)[None], lin("#fff6ee")[None]))
            dist = np.linalg.norm(p - mid, axis=1)
            rank = np.argsort(np.argsort(dist)) / max(m - 1, 1)
            t_bud = (bud[i] if bud is not None and bud[i] is not None else 1e6)
            t_bl = (bloom[i] if bloom is not None and bloom[i] is not None else 1e6)
            budded = rng.random(m) < 0.22
            BB.append(np.where(budded, t_bud + 0.8 * rank, t_bl + 0.55 * rank))
            BS.append(0.10 + 0.08 * rng.random(m))
        # ---- the crown: white and blush blossom over the whole tree
        if n_crown:
            m = n_crown
            ctr = b + np.array([0.0, 9.5 * k, 0.0])
            d = rng.normal(size=(m, 3))
            d /= np.linalg.norm(d, axis=1, keepdims=True)
            rad = (6.2 * k * spread) * (0.55 + 0.45 * rng.random(m) ** 0.5)
            p = ctr + d * rad[:, None] * np.array([1.0, 0.62, 1.0])
            p[:, 1] = np.maximum(p[:, 1], b[1] + 5.0 * k)
            BP.append(p)
            ci = rng.integers(0, len(crown_colors), m)
            BC.append(np.array([show(c) for c in crown_colors])[ci])
            BL.append(np.array([lin(c) for c in crown_colors])[ci])
            tc = crown_t if crown_t is not None else 1e6
            BB.append(tc + 0.9 * np.argsort(np.argsort(p[:, 1])) / max(m - 1, 1))
            BS.append(0.11 + 0.08 * rng.random(m))
        bp = np.concatenate(BP)
        nbl = len(bp)
        rot = np.stack([rng.random(nbl) * TAU, rng.random(nbl) * TAU], axis=1)
        self.bloom_pts = bp
        self.bloom = dict(pos=bp.astype(np.float32), size=(np.concatenate(BS) * k).astype(np.float32),
                          color=np.concatenate(BC).astype(np.float32), alpha=np.full(nbl, 0.95, np.float32),
                          kind="petal", rot=rot.astype(np.float32), paint=0.9, paint_light=0.4,
                          birth=np.concatenate(BB).astype(np.float32), fade=0.35, flash=2.5, twinkle=0.25,
                          seed=rng.random(nbl).astype(np.float32))
        self.bloom_light = dict(pos=bp.astype(np.float32), size=(np.concatenate(BS) * 1.6 * k).astype(np.float32),
                                color=(np.concatenate(BL) * 0.30 * bright).astype(np.float32),
                                alpha=np.full(nbl, 1.0, np.float32), kind="soft",
                                birth=np.concatenate(BB).astype(np.float32), fade=0.35, flash=4.0,
                                seed=rng.random(nbl).astype(np.float32))

    def sample(self, t):
        return [self.bark, self.bark_glow, self.bloom, self.bloom_light]


class Meadow:
    """The water meadow: small flowers and leaves standing in a mirror a hand deep, round the tree."""
    static = True

    def __init__(self, n=22000, r=(9.0, 95.0), centre=(0.0, 0.0), seed=21, avoid=()):
        rng = np.random.default_rng(seed)
        rr = np.sqrt(rng.uniform(r[0] ** 2, r[1] ** 2, n))
        a = rng.random(n) * TAU
        x, z = centre[0] + rr * np.sin(a), centre[1] + rr * np.cos(a)
        y = 0.02 + 0.10 * rng.random(n) ** 2
        flower = rng.random(n) < 0.55
        col = np.where(flower[:, None], _cols(("#ffffff", "#FFE9A8", "#FFC2D4", "#FF9F86", "#E8DDFF"), n, rng),
                       _cols(("#7cc96a", "#a6dc78", "#5fb35a"), n, rng))
        pos = np.stack([x, y, z], axis=1)
        self.b = dict(pos=pos.astype(np.float32), size=np.where(flower, 0.06, 0.09).astype(np.float32) *
                      (0.7 + 0.6 * rng.random(n)).astype(np.float32), color=col.astype(np.float32),
                      alpha=np.full(n, 0.95, np.float32), kind="petal",
                      rot=np.stack([rng.random(n) * TAU, 1.3 + 0.3 * rng.random(n)], axis=1).astype(np.float32),
                      paint=0.85, paint_light=0.3, seed=rng.random(n).astype(np.float32), twinkle=0.1)

    def sample(self, t):
        return self.b


class Stones:
    """Stepping stones: pale flat stones in a line across the water."""
    static = True

    def __init__(self, points, size=0.55, n=500, seed=31):
        rng = np.random.default_rng(seed)
        P = []
        for p in points:
            a = rng.random(n) * TAU
            r = np.sqrt(rng.random(n)) * size * (0.85 + 0.3 * rng.random())
            P.append(np.stack([p[0] + np.cos(a) * r, 0.05 + 0.04 * rng.random(n) * (1 - r / size),
                               p[2] + np.sin(a) * r * 0.75], axis=1))
        pos = np.concatenate(P)
        m = len(pos)
        self.b = dict(pos=pos.astype(np.float32), size=np.full(m, 0.07, np.float32),
                      color=np.tile(show("#efe9df"), (m, 1)).astype(np.float32), alpha=np.full(m, 0.95, np.float32),
                      kind="soft", paint=1.0, paint_light=0.5, seed=rng.random(m).astype(np.float32))

    def sample(self, t):
        return self.b


class Release:
    """The tree lets go: petals leave the blossom at `t0` and open outward as a dome on the wind."""

    def __init__(self, starts, t0, wind, colors, n=14000, speed=9.0, rise=4.0, seed=41, life=7.0):
        rng = np.random.default_rng(seed)
        idx = rng.integers(0, len(starts), n)
        self.p0 = np.asarray(starts, np.float64)[idx]
        ctr = self.p0.mean(axis=0)
        d = self.p0 - ctr
        d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
        d[:, 1] = np.abs(d[:, 1]) * 0.8 + 0.25
        self.dir = d * (0.5 + rng.random((n, 1)))
        self.t0, self.wind, self.n = float(t0), wind, n
        self.speed, self.rise, self.life = speed, rise, life
        self.delay = rng.random(n) * 0.35
        self.col = _cols(colors, n, rng, white=0.3)
        self.s = rng.random((n, 4))
        self.size = (0.09 + 0.07 * self.s[:, 0]).astype(np.float32)

    def sample(self, t):
        a = t - self.t0 - self.delay
        if np.all(a <= 0.0) or float(np.min(a)) > self.life:
            return []
        on = a > 0.0
        aa = np.maximum(a, 0.0)
        tau = 1.1
        travel = self.speed * tau * (1.0 - np.exp(-aa / tau))
        drift = self.wind.travel(self.t0, t) * 0.6
        s = self.s
        flutter = np.stack([0.3 * np.sin(aa * 2.0 + s[:, 1] * TAU), -0.35 * aa * s[:, 2],
                            0.3 * np.cos(aa * 1.7 + s[:, 3] * TAU)], axis=1)
        pos = self.p0 + self.dir * travel[:, None] + drift[None, :] + flutter
        pos[:, 1] = np.maximum(pos[:, 1], 0.05)
        alpha = on * _ss(0.0, 0.15, aa) * (1.0 - _ss(self.life - 1.5, self.life, aa))
        rot = np.stack([aa * 1.5 + s[:, 1] * TAU, aa * (3.0 + 3.0 * s[:, 2])], axis=1)
        sel = alpha > 0.01
        return dict(pos=pos[sel].astype(np.float32), size=self.size[sel], color=self.col[sel],
                    alpha=alpha[sel].astype(np.float32), kind="petal", rot=rot[sel].astype(np.float32), paint=0.9,
                    paint_light=0.4, seed=s[sel, 0], twinkle=0.2)


class Stream:
    """A stream of petals blown from a moving source (a palm) toward a target, between t0 and t1.
    source(t), target(t): points or functions of time. Each petal flies for `flight` seconds along a curving
    arc, then drifts on with the wind and fades."""

    def __init__(self, source, target, t0, t1, wind=None, n=2500, flight=1.6, arc=1.2, swirl=0.6,
                 colors=PETAL_HEX, size=(0.03, 0.05), seed=51, linger=1.2, paint=0.9):
        rng = np.random.default_rng(seed)
        self.src, self.tgt = source, target
        self.t0, self.t1, self.n, self.flight, self.arc, self.swirl = float(t0), float(t1), n, flight, arc, swirl
        self.wind, self.linger, self.paint = wind, linger, paint
        self.te = self.t0 + (self.t1 - self.t0) * np.sort(rng.random(n))
        self.s = rng.random((n, 5))
        self.col = _cols(colors, n, rng, white=0.2)
        self.size = (size[0] + (size[1] - size[0]) * self.s[:, 0]).astype(np.float32)

    @staticmethod
    def _p(f, t):
        return np.asarray(f(t) if callable(f) else f, np.float64)

    def sample(self, t):
        if t < self.t0 or t > self.t1 + self.flight + self.linger:
            return []
        age = t - self.te
        on = age > 0.0
        if not on.any():
            return []
        s = self.s
        u = np.clip(age / self.flight, 0.0, 1.0)
        e = u * u * (3 - 2 * u)
        tes = np.clip(self.te, self.t0, self.t1)
        # sources and targets at the moment each petal left (sampled coarsely and interpolated)
        grid = np.linspace(self.t0, self.t1, 24)
        S = np.array([self._p(self.src, g) for g in grid])
        T = np.array([self._p(self.tgt, min(g + self.flight, self.t1 + self.flight)) for g in grid])
        Si = np.stack([np.interp(tes, grid, S[:, k]) for k in range(3)], axis=1)
        Ti = np.stack([np.interp(tes, grid, T[:, k]) for k in range(3)], axis=1)
        d = Ti - Si
        L = np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
        side = np.cross(d / L, np.array([0.0, 1.0, 0.0]))
        spread = (s[:, 1:4] - 0.5) * 0.8 * L * 0.25
        arc = np.sin(np.pi * e)[:, None] * (np.array([0.0, self.arc, 0.0]) + side * (s[:, 4:5] - 0.5) * self.swirl * 2)
        pos = Si + d * e[:, None] + arc + spread * np.sin(np.pi * e)[:, None]
        late = np.maximum(age - self.flight, 0.0)
        if self.wind is not None:
            pos = pos + self.wind.travel(t - late, t) * 0.5
        pos[:, 1] = np.maximum(pos[:, 1], 0.05)
        alpha = on * _ss(0.0, 0.12, age) * (1.0 - _ss(self.flight + self.linger * 0.4, self.flight + self.linger, age))
        rot = np.stack([age * 2.0 + s[:, 2] * TAU, age * (3.0 + 2.0 * s[:, 3])], axis=1)
        sel = alpha > 0.01
        return dict(pos=pos[sel].astype(np.float32), size=self.size[sel], color=self.col[sel],
                    alpha=alpha[sel].astype(np.float32), kind="petal", rot=rot[sel].astype(np.float32),
                    paint=self.paint, paint_light=0.4, seed=s[sel, 0], twinkle=0.2)
