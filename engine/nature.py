"""Living nature made of light (engine-nature, 2026-11-15): FLOWERS, TREE (with BLOSSOM), WATERFALL, STREAM, WIND.

Everything here is optional and always moving. A song file switches a layer on by defining its setting (a number
or a Track, 0 = off); songs that define none of them render exactly as before (no program is even built).
The layers are drawn as light into the glow buffer before the text protection pass, so the veil behind the words
dims them like every other light, and they all honour BOTTOM_CALM. How a song uses them: engine/UPGRADE-HOWTO.md,
section I1.

  FLOWERS    a field of flowers of light: stems rise, buds form, petals open in a wave across the field, all sway
  TREE       one tree of light with procedural branches that sway in layered wind; TREE_GROW grows it from a seed;
             BLOSSOM opens blossoms on its twigs and lets petals fall
  WATERFALL  falling light-water with a bright lip, foam and rising mist
  STREAM     a flowing stream of light along STREAM_PATH, winding toward the lake
  WIND       shared wind strength for all of them (gusts travel across the screen left to right)
"""
import math

import numpy as np
import moderngl

import song as S
import nature_shaders as NS

CALM_Y = 0.335
TAU = 2.0 * math.pi
CAMPAIGN = ["#fff1d6", "#ffc8a2", "#ff8f7a", "#9fd0ff", "#ffd9b8"]   # cream, peach, coral, sky blue, soft peach
LEAF = ("#d8ec8a", "#b4dc78", "#f2e08a")                            # fresh green-gold leaves


def val(name, t, default=None):
    v = getattr(S, name, None)
    if v is None:
        return default
    return v(t) if callable(v) else v


def lin(c):
    return S.lin(c) if isinstance(c, str) else np.asarray(c, dtype=np.float64)


def colors(name, t, default):
    c = val(name, t, None)
    if c is None:
        c = default
    if isinstance(c, str):
        c = [c]
    return np.array([lin(x) for x in c])


def ssv(a, b, x):
    u = np.clip((np.asarray(x, dtype=np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def wind(t, x, tl=None):
    """The shared wind at time t over screen position x: a steady push plus gusts that roll left to right.
    `tl` (optional, may be an array) is a delayed time for the gusts, so they reach outer branches later."""
    base = float(val("WIND", t, 0.35) or 0.0)
    g_t = t if tl is None else tl
    g = (0.62 + 0.38 * np.sin(0.42 * g_t - 3.1 * x) + 0.22 * np.sin(1.17 * g_t - 7.3 * x + 1.3)
         + 0.10 * np.sin(2.9 * g_t - 13.0 * x))
    return base * g


def calm_k(y, calm, floor=0.0):
    """1 above the lower third, falling to `floor` inside it when BOTTOM_CALM is on."""
    low = 1.0 - ssv(CALM_Y - 0.07, CALM_Y + 0.05, y)
    return 1.0 - calm * (1.0 - floor) * low


class Pts:
    """Collects soft glow points: x, y (screen fractions), size (px at 1080p), colour (linear), sharpness."""

    def __init__(self):
        self.parts = []

    def add(self, x, y, size, col, inten, sharp=3.0):
        x = np.ravel(np.asarray(x, dtype=np.float32))
        n = x.size
        if n == 0:
            return
        y = np.broadcast_to(np.ravel(np.asarray(y, dtype=np.float32)), (n,))
        size = np.broadcast_to(np.ravel(np.asarray(size, dtype=np.float32)), (n,))
        inten = np.broadcast_to(np.ravel(np.asarray(inten, dtype=np.float32)), (n,))
        col = np.asarray(col, dtype=np.float32)
        col = np.broadcast_to(col.reshape(-1, 3), (n, 3)) * inten[:, None]
        sharp = np.broadcast_to(np.ravel(np.asarray(sharp, dtype=np.float32)), (n,))
        a = np.empty((n, 7), np.float32)
        a[:, 0], a[:, 1], a[:, 2], a[:, 3:6], a[:, 6] = x, y, size, col, sharp
        keep = (inten > 0.004) & (x > -0.1) & (x < 1.1) & (y > -0.1) & (y < 1.1)
        self.parts.append(a[keep])

    def data(self):
        return np.concatenate(self.parts) if self.parts else np.zeros((0, 7), np.float32)


# ------------------------------------------------------------------------------------------------ flowers
class Flowers:
    NP = 6     # petals per flower
    NS = 10    # samples along each side of a petal outline

    def __init__(self):
        n = int(getattr(S, "FLOWERS_COUNT", 44))
        r = np.random.default_rng(int(getattr(S, "FLOWERS_SEED", 5))).random((n, 10))
        self.n, self.r = n, r
        span = getattr(S, "FLOWERS_SPAN", (0.0, 1.0))
        self.fx = span[0] + (span[1] - span[0]) * r[:, 0]
        self.d = r[:, 1] ** 0.8                     # 0 near (low, large) .. 1 far (on the line, small)
        order = np.argsort(-self.d)                 # far first
        self.r, self.fx, self.d = self.r[order], self.fx[order], self.d[order]
        self.ci = (self.r[:, 2] * 97.0).astype(int)

    def draw(self, P, t, amt, calm):
        r, fx, d = self.r, self.fx, self.d
        A = S.ASPECT
        line = float(val("FLOWERS_LINE", t, 0.34))
        band = float(val("FLOWERS_DEPTH", t, 0.16))
        bright = float(val("FLOWERS_BRIGHT", t, 1.0))
        cols = colors("FLOWERS_COLOR", t, CAMPAIGN)
        stemc, leafc, core = lin(LEAF[1]), lin(LEAF[0]), lin("#fff6e2")
        yb = line - band * (1.0 - d)
        sc = 0.55 + 0.75 * (1.0 - d)
        h = (0.060 + 0.050 * r[:, 3]) * sc
        R = (0.024 + 0.012 * r[:, 4]) * sc
        # the wave of blooming travels from FLOWERS_WAVE (an x position) across the field
        org = float(val("FLOWERS_WAVE", t, 0.0))
        delay = 0.75 * np.abs(fx - org) / max(org, 1.0 - org, 0.5) + 0.2 * r[:, 5]
        oraw = np.clip((amt * 1.3 - delay) / 0.35, 0.0, 1.0)
        grow = ssv(0.0, 0.45, oraw)
        bloom = ssv(0.40, 1.0, oraw)
        bud = ssv(0.30, 0.48, oraw)
        # calm lower third: low flowers stay soft, and the bottom-centre is left clear
        low = 1.0 - ssv(CALM_Y - 0.07, CALM_Y + 0.05, yb)
        centre = ssv(0.10, 0.26, np.abs(fx - 0.5))
        k = (1.0 - calm * low * (1.0 - 0.5 * centre)) * (0.6 + 0.4 * (1.0 - d)) * bright
        gentle = 1.0 - 0.35 * calm * low
        w = wind(t, fx)
        sway = h * (0.30 * w + 0.07 * np.sin(t * (0.9 + 0.5 * r[:, 6]) + TAU * r[:, 7])
                    + 0.03 * np.sin(t * 2.3 + TAU * r[:, 8])) * gentle
        X0 = fx * A
        # stem: a quadratic bend from the base to the head
        s = np.linspace(0.0, 1.0, 24)[None, :]
        sx = X0[:, None] + (sway * grow)[:, None] * s * s
        sy = yb[:, None] + (h * grow)[:, None] * s
        a_st = (k * grow * 0.8)[:, None] * np.ones_like(s)
        P.add(sx / A, sy, (2.4 * sc)[:, None] * np.ones_like(s), stemc, a_st, 2.5)
        hx, hy = X0 + sway * grow, yb + h * grow
        # two leaves on the stem that flutter
        for side, sl, ph in ((1.0, 0.32, 0.0), (-1.0, 0.52, 1.7)):
            bx, by = X0 + sway * grow * sl * sl, yb + h * grow * sl
            ang = math.pi / 2 - side * (0.95 + 0.18 * np.sin(t * 1.9 + TAU * r[:, 9] + ph)) - 0.4 * w
            ll = 0.38 * h * grow
            q = np.linspace(0.15, 1.0, 5)[None, :]
            lx = bx[:, None] + (ll * np.cos(ang))[:, None] * q
            ly = by[:, None] + (ll * np.sin(ang))[:, None] * q + (0.15 * ll)[:, None] * q * q
            P.add(lx / A, ly, (2.6 * sc)[:, None] * (1.2 - 0.6 * q), leafc, (k * grow * 0.6)[:, None] * np.ones_like(q), 2.5)
        # petals: closed into a bud pointing up, then unfurl into an open face seen a little from above
        tilt = -0.9 * sway / h
        kk = np.arange(self.NP)[None, :]
        rot = TAU * r[:, 2][:, None]
        closed = math.pi / 2 + (kk - (self.NP - 1) / 2.0) * 0.16
        opened = rot + kk * TAU / self.NP
        bl = bloom[:, None]
        ang = closed * (1 - bl) + opened * bl + tilt[:, None]
        squash = 1.0 - 0.38 * bl
        breathe = 1.0 + 0.06 * np.sin(1.5 * t + TAU * r[:, 6][:, None] + kk)
        L = R[:, None] * (0.38 + 0.62 * bl) * breathe
        Wd = R[:, None] * 0.42 * (0.45 + 0.55 * bl)
        dxp, dyp = np.cos(ang), np.sin(ang) * squash
        pxp, pyp = -np.sin(ang), np.cos(ang) * squash
        cidx = self.ci % len(cols)
        pc = cols[cidx]                                     # (n, 3)
        pa = k * bud
        ss_ = np.linspace(1.0 / self.NS, 1.0, self.NS)
        for side in (1.0, -1.0):
            ox = hx[:, None, None] + (L * dxp)[..., None] * ss_ + side * (Wd * pxp)[..., None] * np.sin(math.pi * ss_)
            oy = hy[:, None, None] + (L * dyp)[..., None] * ss_ + side * (Wd * pyp)[..., None] * np.sin(math.pi * ss_)
            n_pts = self.NP * self.NS
            P.add(ox.reshape(self.n, -1) / A, oy.reshape(self.n, -1), np.repeat(3.4 * sc, n_pts),
                  np.repeat(pc, n_pts, axis=0), np.repeat(pa * 1.3, n_pts), 3.2)
        # a glassy fill in each petal
        fxp = hx[:, None] + L * dxp * 0.55
        fyp = hy[:, None] + L * dyp * 0.55
        P.add(fxp / A, fyp, (L * 1080 * 1.25).ravel(), np.repeat(pc, self.NP, axis=0),
              np.repeat(pa * 0.22, self.NP), 2.0)
        # the heart of the flower
        P.add(hx / A, hy, 6.5 * sc, core, k * bud * (0.5 + 0.9 * bloom), 3.5)
        P.add(hx / A, hy, 34.0 * sc * bloom + 4.0, pc, k * bloom * 0.22, 2.2)


# ------------------------------------------------------------------------------------------------ tree
class Tree:
    def __init__(self):
        rng = np.random.default_rng(int(getattr(S, "TREE_SEED", 3)))
        depth_max = int(getattr(S, "TREE_DEPTH", 7))
        segs = []   # parent, attach u, local rest angle, length, thick0, thick1, depth

        def branch(parent, u, ang, length, thick, depth, abs_parent):
            # `abs_parent` is the parent's direction; every bend leans gently back toward the light above
            nseg = 3
            p = parent
            absa = abs_parent
            for k in range(nseg):
                if k == 0:
                    a = ang
                else:
                    a = rng.normal(0.0, 0.05 + 0.03 * depth) - (0.20 if depth > 0 else 0.6) * (absa - math.pi / 2)
                absa += a
                t0 = thick * (1.0 - 0.18 * k / nseg)
                t1 = thick * (1.0 - 0.18 * (k + 1) / nseg)
                segs.append([p, u if k == 0 else 1.0, a, length / nseg, t0, t1, depth + k / nseg])
                if k == 1 and 1 <= depth < depth_max - 1 and rng.random() < 0.35:
                    sgn = rng.choice([-1.0, 1.0])
                    branch(len(segs) - 1, rng.uniform(0.3, 0.8), sgn * rng.uniform(0.65, 1.05), length * 0.55,
                           thick * 0.55, depth + 1, absa)
                p = len(segs) - 1
                u = 1.0
            if depth < depth_max:
                spread = rng.uniform(0.34, 0.60)
                lean = rng.normal(0.0, 0.06) - 0.10 * (absa - math.pi / 2)
                for sgn in (-1.0, 1.0):
                    branch(p, 1.0, lean + sgn * spread * rng.uniform(0.8, 1.2), length * rng.uniform(0.70, 0.82),
                           thick * 0.68, depth + 1, absa)

        branch(-1, 0.0, math.pi / 2 + rng.normal(0.0, 0.03), 0.34, 1.0, 0, 0.0)
        a = np.array(segs, dtype=np.float64)
        self.parent = a[:, 0].astype(int)
        self.u, self.rest, self.len = a[:, 1], a[:, 2], a[:, 3]
        self.th0, self.th1, self.depth = a[:, 4], a[:, 5], a[:, 6]
        n = self.n = len(segs)
        self.level = np.zeros(n, int)
        for i in range(n):
            self.level[i] = 0 if self.parent[i] < 0 else self.level[self.parent[i]] + 1
        self.levels = [np.nonzero(self.level == lv)[0] for lv in range(self.level.max() + 1)]
        # path length from the seed to each segment's base (the growth front travels along it)
        self.pbase = np.zeros(n)
        for i in range(n):
            p = self.parent[i]
            if p >= 0:
                self.pbase[i] = self.pbase[p] + self.u[i] * self.len[p]
        self.pmax = float((self.pbase + self.len).max())
        self.phase = rng.random((n, 3))
        haschild = np.zeros(n, bool)
        haschild[self.parent[self.parent >= 0]] = True
        self.tips = np.nonzero(~haschild)[0]
        # balance the crown over the trunk, then normalise: the crown at rest reaches height 1
        for _ in range(3):
            bx, by, dx, dy = self._fk(self.rest, 1.0)
            ex, ey = bx + dx * self.len, by + dy * self.len
            self.rest[0] += float(np.clip(0.8 * np.mean(ex[self.tips]) / float(ey.max()), -0.3, 0.3))
        bx, by, dx, dy = self._fk(self.rest, 1.0)
        top = float((by + dy * self.len).max())
        self.scale = 1.0 / top
        self.len = self.len / top
        self.pbase, self.pmax = self.pbase / top, self.pmax / top
        # sample positions along every segment for the core line and the halo
        core = []
        halo = []
        for i in range(n):
            th = self.th0[i]
            m = int(max(3, self.len[i] * 520 / max(0.5, 0.6 + 2.2 * th)))
            core.append(np.stack([np.full(m, i), (np.arange(m) + 0.5) / m], 1))
            mh = int(max(2, self.len[i] * 520 / max(2.0, 6.0 * th + 1.0)))
            halo.append(np.stack([np.full(mh, i), (np.arange(mh) + 0.5) / mh], 1))
        core, halo = np.concatenate(core), np.concatenate(halo)
        self.c_seg, self.c_s = core[:, 0].astype(int), core[:, 1]
        self.h_seg, self.h_s = halo[:, 0].astype(int), halo[:, 1]
        # leaves on the outer twigs
        outer = np.nonzero(self.depth >= depth_max - 1.4)[0]
        nl = int(getattr(S, "TREE_LEAVES", 1100))
        self.l_seg = rng.choice(outer, nl)
        self.l_s = rng.uniform(0.2, 1.0, nl)
        self.l_ang = rng.uniform(-1.3, 1.3, nl) + np.where(rng.random(nl) < 0.5, 0.0, math.pi)
        self.l_len = rng.uniform(0.010, 0.020, nl)
        self.l_r = rng.random((nl, 4))
        # blossoms on the tips
        nb = min(int(getattr(S, "BLOSSOM_COUNT", 150)), len(self.tips) * 2)
        self.b_seg = rng.choice(self.tips, nb)
        self.b_s = rng.uniform(0.55, 1.0, nb)
        self.b_r = rng.random((nb, 4))
        # falling petals
        nf = int(getattr(S, "BLOSSOM_PETALS", 260))
        self.f_src = rng.integers(0, nb, nf)
        self.f_r = rng.random((nf, 6))
        self._rest_cache = None

    def _fk(self, local, grow_len):
        """Forward kinematics: base point and unit direction of every segment (tree units, base at 0, 0)."""
        n = self.n
        ang = np.zeros(n)
        bx, by = np.zeros(n), np.zeros(n)
        L = self.len * grow_len
        for idx in self.levels:
            p = self.parent[idx]
            root = p < 0
            pp = np.where(root, 0, p)
            ang[idx] = np.where(root, 0.0, ang[pp]) + local[idx]
            ux = np.where(root, 0.0, bx[pp] + np.cos(ang[pp]) * L[pp] * self.u[idx])
            uy = np.where(root, 0.0, by[pp] + np.sin(ang[pp]) * L[pp] * self.u[idx])
            bx[idx], by[idx] = ux, uy
        return bx, by, np.cos(ang), np.sin(ang)

    def draw(self, P, t, amt, calm):
        A = S.ASPECT
        G = float(np.clip(val("TREE_GROW", t, 1.0), 0.0, 1.0))
        x0 = float(val("TREE_X", t, 0.80))
        base_y = float(val("TREE_Y", t, 0.30))
        H = float(val("TREE_HEIGHT", t, 0.52))
        tcol = colors("TREE_COLOR", t, ["#ffdcaa"])[0]
        bright = amt * float(val("TREE_BRIGHT", t, 1.0))
        X0 = x0 * A
        # growth: the front moves out along every path from the seed at one speed
        front = G * self.pmax * 1.02
        vis = np.clip((front - self.pbase) / self.len, 0.0, 1.0)
        # layered wind: a slow gust leaning the whole tree (arriving later at the outer branches),
        # a middle sway per branch and a fast flutter in the twigs
        dep = self.depth
        # (the angles add up along each path of about 24 segments, so each one bends only a little)
        flex = 0.0026 * (1.0 + 0.6 * dep) * (0.4 + 0.6 * G)
        lag = t - 0.22 * dep
        gust = np.asarray(wind(t, x0, lag))
        ph = self.phase
        twig = 0.05 * ssv(4.5, 7.0, dep) * (0.5 + float(val("WIND", t, 0.35) or 0.0))
        local = (self.rest + flex * (-1.0 * gust + 0.8 * np.sin(lag * (0.55 + 0.25 * ph[:, 0]) + TAU * ph[:, 1]))
                 + twig * np.sin(t * (1.8 + 1.2 * ph[:, 2]) + TAU * ph[:, 0]))
        bx, by, dx, dy = self._fk(local, 1.0)
        L = self.len
        tk = (0.30 + 0.70 * G)          # trunk thickens as it grows
        hpx = H * 1080.0                # px per tree unit (at 1080p)

        def world(seg, s):
            X = X0 + (bx[seg] + dx[seg] * L[seg] * s) * H
            Y = base_y + (by[seg] + dy[seg] * L[seg] * s) * H
            return X, Y

        # branches: a bright thin core and a soft halo, drawn only up to the growth front
        X, Y = world(self.c_seg, self.c_s)
        th = (self.th0[self.c_seg] * (1 - self.c_s) + self.th1[self.c_seg] * self.c_s) * tk
        on = (self.c_s <= vis[self.c_seg]).astype(np.float64)
        ck = calm_k(Y, calm, 0.35)
        P.add(X / A, Y, 0.9 + 7.0 * th * hpx / 560.0, tcol, on * bright * ck * (0.55 + 0.25 * th), 3.0)
        X, Y = world(self.h_seg, self.h_s)
        th = (self.th0[self.h_seg] * (1 - self.h_s) + self.th1[self.h_seg] * self.h_s) * tk
        on = (self.h_s <= vis[self.h_seg]).astype(np.float64)
        P.add(X / A, Y, 5.0 + 24.0 * th * hpx / 560.0, tcol, on * bright * calm_k(Y, calm, 0.35) * 0.075, 2.0)
        # the growing tips glow like buds of light
        growing = np.nonzero((vis > 0.0) & (vis < 1.0))[0]
        if growing.size:
            X, Y = world(growing, vis[growing])
            P.add(X / A, Y, 10.0, lin("#fff4dc"), bright * 0.55, 3.5)
        # leaves: fresh green-gold, fluttering and catching the light as they turn
        lr = self.l_r
        lv = np.clip((front - (self.pbase[self.l_seg] + self.l_s * L[self.l_seg])) / (0.06 * self.pmax), 0.0, 1.0)
        lv = lv * ssv(0.55, 0.9, G)
        if lv.max() > 0.0:
            X, Y = world(self.l_seg, self.l_s)
            w = wind(t, x0)
            la = self.l_ang + 0.35 * np.sin(t * (2.2 + 1.5 * lr[:, 0]) + TAU * lr[:, 1]) * (0.5 + w) - 0.5 * w
            ll = self.l_len * H / 0.52 * lv
            turn = 0.45 + 0.55 * np.sin(t * (1.1 + 1.3 * lr[:, 2]) + TAU * lr[:, 3]) ** 2
            lc = np.array([lin(c) for c in LEAF])[(lr[:, 0] * 3).astype(int) % 3]
            ka = bright * lv * turn * calm_k(Y, calm, 0.3)
            for q in (0.25, 0.6, 0.95):
                P.add((X + np.cos(la) * ll * q) / A, Y + np.sin(la) * ll * q, 3.6 * (1.25 - 0.5 * q) * H / 0.52,
                      lc, ka * 0.42, 2.6)
        # blossoms
        B = float(np.clip(val("BLOSSOM", t, 0.0) or 0.0, 0.0, 1.0))
        if B > 0.001:
            bcols = colors("BLOSSOM_COLOR", t, ["#ffd0d8", "#ffc8a2", "#fff1d6", "#ff9f8f"])
            br = self.b_r
            bo = np.clip((B * 1.35 - 0.35 * br[:, 0]) / 0.45, 0.0, 1.0) * (vis[self.b_seg] >= 0.999)
            X, Y = world(self.b_seg, self.b_s)
            bc = bcols[(br[:, 1] * 97).astype(int) % len(bcols)]
            rad = (0.006 + 0.004 * br[:, 2]) * H / 0.52 * ssv(0.0, 1.0, bo)
            kb = bright * calm_k(Y, calm, 0.3)
            for p in range(5):
                a = TAU * (br[:, 3] + p / 5.0) + 0.3 * np.sin(t * 0.9 + TAU * br[:, 0])
                P.add((X + np.cos(a) * rad) / A, Y + np.sin(a) * rad * 0.8, 6.5 * H / 0.52 * (0.5 + 0.5 * bo), bc,
                      kb * bo * 0.42, 2.4)
            P.add(X / A, Y, 3.0, lin("#fff6e2"), kb * bo * 0.8, 3.5)
            # petals fall from the open blossoms, tumbling and carried on the wind
            fall = ssv(0.35, 0.8, B)
            if fall > 0.0:
                fr = self.f_r
                if self._rest_cache is None:
                    rbx, rby, rdx, rdy = self._fk(self.rest, 1.0)
                    self._rest_cache = (rbx, rby, rdx, rdy)
                rbx, rby, rdx, rdy = self._rest_cache
                seg, s = self.b_seg[self.f_src], self.b_s[self.f_src]
                ox = X0 + (rbx[seg] + rdx[seg] * L[seg] * s) * H
                oy = base_y + (rby[seg] + rdy[seg] * L[seg] * s) * H
                per = 7.0 + 6.0 * fr[:, 0]
                age = np.mod(t + per * fr[:, 1], per)
                w = wind(t, x0)
                fx = ox + (0.010 + 0.045 * (0.3 + w)) * age + 0.025 * np.sin(1.1 * age + TAU * fr[:, 2])
                fy = oy - (0.020 + 0.010 * fr[:, 3]) * age - 0.004 * age * age * 0.2
                life = ssv(0.0, 0.5, age) * (1.0 - ssv(per - 1.5, per, age))
                ground = ssv(base_y - 0.06, base_y - 0.01, fy)
                active = (fr[:, 4] < fall).astype(np.float64)
                tum = 0.35 + 0.65 * np.abs(np.sin(2.4 * age + TAU * fr[:, 5]))
                fc = bcols[(fr[:, 5] * 97).astype(int) % len(bcols)]
                P.add(fx / A, fy, 5.5 * tum + 1.5, fc, bright * life * ground * active * tum * 0.55 * calm_k(fy, calm, 0.25), 2.6)


# ------------------------------------------------------------------------------------------------ waterfall
class Waterfall:
    def __init__(self):
        self.r = np.random.default_rng(17).random((700, 5))

    def droplets(self, P, t, amt, calm, x, top, bot, wdt, ca, cb):
        r = self.r
        A = S.ASPECT
        H = max(top - bot, 0.02)
        rate = 0.55 + 0.4 * r[:, 0]
        f = np.mod(t * rate / (H / 0.26) + r[:, 1], 1.0)
        v = f ** 1.5
        hw = wdt * (0.5 + 0.35 * v) / A
        X = x + (r[:, 2] * 2 - 1) * hw * 0.95 + 0.004 * np.sin(t * 0.7 + v * 5.0) * v
        Y = top - v * H
        pour = ssv(amt * 1.25, amt * 1.25 - 0.12, v)
        tw = 0.4 + 0.6 * np.sin(t * 9.0 + TAU * r[:, 3]) ** 2
        k = amt * pour * tw * calm_k(Y, calm, 0.4)
        for q in (0.0, 0.010, 0.020):   # a short streak
            P.add(X, Y + q * (0.6 + v), 2.6 - 40 * q, cb, k * (0.55 - 12 * q), 3.2)
        # splashes that leap from the foot and fall back
        sp = r[:300]
        age = np.mod(t * (0.9 + 0.6 * sp[:, 0]) + sp[:, 1], 1.0)
        vx = (sp[:, 2] * 2 - 1) * 0.05
        vy = 0.05 + 0.05 * sp[:, 3]
        SX = x + vx * age / A * 1.6
        SY = bot + vy * age - 0.11 * age * age
        k2 = amt * ssv(0.85, 1.0, amt * 1.25) * (1 - age) * (SY > bot - 0.02) * calm_k(SY, calm, 0.4)
        P.add(SX, SY, 2.2, ca, k2 * 0.5, 3.0)


# ------------------------------------------------------------------------------------------------ stream
class Stream:
    def __init__(self):
        self.r = np.random.default_rng(23).random((2600, 6))
        self._key = None

    def path(self, pts):
        key = tuple(map(tuple, pts))
        if key == self._key:
            return self._path
        p = np.asarray(pts, dtype=np.float64) * np.array([S.ASPECT, 1.0])
        p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
        out = []
        for i in range(1, len(p) - 2):
            p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
            u = np.linspace(0, 1, 60, endpoint=False)[:, None]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
        out.append(p[-2][None, :])
        c = np.vstack(out)
        seg = np.linalg.norm(np.diff(c, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(seg)])
        tot = s[-1]
        su = np.linspace(0, tot, 600)
        cx, cy = np.interp(su, s, c[:, 0]), np.interp(su, s, c[:, 1])
        tx, ty = np.gradient(cx), np.gradient(cy)
        tl = np.hypot(tx, ty) + 1e-9
        self._path = (cx, cy, tx / tl, ty / tl, tot)
        self._key = key
        return self._path

    def draw(self, P, t, amt, calm):
        A = S.ASPECT
        default = [(0.20, 0.375), (0.27, 0.36), (0.22, 0.345), (0.33, 0.33), (0.42, 0.318), (0.47, 0.305)]
        cx, cy, tx, ty, tot = self.path(val("STREAM_PATH", t, default))
        nx, ny = -ty, tx
        width = float(val("STREAM_WIDTH", t, 0.010))
        speed = float(val("STREAM_SPEED", t, 1.0))
        cs = colors("STREAM_COLOR", t, ["#9fd0ff", "#fff1d6"])
        ca, cb = cs[0], cs[-1]
        m = len(cx)
        u = np.linspace(0, 1, m)
        front = amt * 1.15                       # the light flows in along the path as STREAM rises
        reach = ssv(front, front - 0.12, u)
        wv = width * (0.7 + 1.0 * u)             # wider as it nears the lake
        kc = calm_k(cy, calm, 0.4)
        # the body: soft wide light and two thin banks that shimmer
        b = np.arange(0, m, 3)
        P.add(cx[b] / A, cy[b], wv[b] * 1080 * 2.4, ca, reach[b] * kc[b] * 0.02 * amt, 1.8)
        sh = 0.6 + 0.4 * np.sin(u * 60.0 - t * 3.0)
        for side in (1.0, -1.0):
            P.add((cx + side * nx * wv) / A, cy + side * ny * wv, 1.5, ca, reach * kc * sh * 0.10 * amt, 3.0)
        # flowing glints: carried down the stream, faster in the middle
        r = self.r
        lat = (r[:, 0] * 2 - 1)
        v = speed * (0.040 + 0.03 * r[:, 1]) * (1.0 - 0.45 * lat * lat) / max(tot, 0.05)
        s = np.mod(r[:, 2] + t * v, 1.0)
        i = np.minimum((s * (m - 1)).astype(int), m - 1)
        mean = 0.25 * np.sin(t * 1.3 + TAU * r[:, 3] + s * 20.0)
        off = (lat * 0.85 + mean * 0.2) * wv[i]
        X, Y = cx[i] + nx[i] * off, cy[i] + ny[i] * off
        glint = 0.25 + 0.75 * np.sin(t * (3.0 + 4.0 * r[:, 4]) + TAU * r[:, 5]) ** 6
        k = reach[i] * kc[i] * glint * amt
        col = np.where((r[:, 4] > 0.6)[:, None], cb[None, :], ca[None, :])
        for q in (0.0, 0.006):
            P.add((X - tx[i] * q) / A, Y - ty[i] * q, 3.0 - 60 * q, col, k * (0.75 - 40 * q), 3.0)


# ------------------------------------------------------------------------------------------------ the layer
KEYS = ("FLOWERS", "TREE", "WATERFALL", "STREAM")


class Nature:
    def __init__(self, R):
        self.R = R
        self.on = any(getattr(S, k, None) is not None for k in KEYS)
        if not self.on:
            return
        ctx = self.ctx = R.ctx
        self.px = R.px
        self.p_glow = ctx.program(vertex_shader=NS.GLOW_VS, fragment_shader=NS.GLOW_FS)
        self.cap = 200000
        self.buf = ctx.buffer(reserve=self.cap * 28, dynamic=True)
        self.vao = ctx.vertex_array(self.p_glow, [(self.buf, "2f 1f 3f 1f", "aPos", "aSize", "aCol", "aSharp")])
        self.flowers = Flowers() if getattr(S, "FLOWERS", None) is not None else None
        self.tree = Tree() if getattr(S, "TREE", None) is not None else None
        self.stream = Stream() if getattr(S, "STREAM", None) is not None else None
        self.fall = None
        if getattr(S, "WATERFALL", None) is not None:
            self.fall = Waterfall()
            self.p_fall = ctx.program(vertex_shader=NS.RECT_VS, fragment_shader=NS.FALL_FS)
            quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
            self.v_fall = ctx.vertex_array(self.p_fall, [(quad, "2f", "aPos")])

    def draw(self, t):
        """Draws every nature layer that is on into the bound glow buffer (additive blending is already set)."""
        if not self.on:
            return
        calm = float(val("BOTTOM_CALM", t, 0.0) or 0.0)
        P = Pts()
        if self.stream is not None:
            a = float(val("STREAM", t, 0.0) or 0.0)
            if a > 0.001:
                self.stream.draw(P, t, a, calm)
        if self.fall is not None:
            a = float(val("WATERFALL", t, 0.0) or 0.0)
            if a > 0.001:
                x = float(val("WATERFALL_X", t, 0.20))
                top = float(val("WATERFALL_TOP", t, 0.62))
                bot = float(val("WATERFALL_BOTTOM", t, 0.375))
                wdt = float(val("WATERFALL_WIDTH", t, 0.040))
                cs = colors("WATERFALL_COLOR", t, ["#bfe3ff", "#fff4e0"])
                ca, cb = cs[0], cs[-1]
                pad = wdt * 2.2 / S.ASPECT + 0.02
                rect = (max(x - pad - 0.15, 0.0), max(bot - 0.06, 0.0), min(x + pad + 0.15, 1.0), min(top + 0.02, 1.0))
                p = self.p_fall
                for k_, v_ in dict(uRect=rect, uT=t, uAspect=S.ASPECT, uAmt=a, uX=x, uTop=top, uBot=bot, uW=wdt,
                                   uCalm=calm, uCalmY=CALM_Y, uColA=tuple(ca), uColB=tuple(cb)).items():
                    if k_ in p:
                        p[k_].value = tuple(float(z) for z in v_) if isinstance(v_, (tuple, np.ndarray)) else float(v_)
                self.v_fall.render(moderngl.TRIANGLE_STRIP)
                self.fall.droplets(P, t, a, calm, x, top, bot, wdt, ca, cb)
        if self.tree is not None:
            a = float(val("TREE", t, 0.0) or 0.0)
            if a > 0.001:
                self.tree.draw(P, t, a, calm)
        if self.flowers is not None:
            a = float(val("FLOWERS", t, 0.0) or 0.0)
            if a > 0.001:
                self.flowers.draw(P, t, a, calm)
        d = P.data()
        n = min(len(d), self.cap)
        if n == 0:
            return
        self.buf.write(d[:n].tobytes())
        self.p_glow["uPx"].value = float(self.px)
        self.vao.render(moderngl.POINTS, vertices=n)
