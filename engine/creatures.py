"""Creatures of light (2026-11): doves, butterflies and fireflies that move like living things.

Everything here is optional. A song file switches a creature on by defining its setting; songs that define none
of them render exactly as before. The settings are documented in engine/UPGRADE-HOWTO.md, section M.

  DOVES        a flock (separation, alignment, cohesion) steered toward a target or along a path. Each dove has
               real wing beats (flap, then glide), banks into its turns and sheds faint sparks.
  BUTTERFLIES  a few, with fast fluttering wings, meandering flight and an occasional landing.
  FIREFLIES    soft blinking points that wander low, near the water and the grass.

Every frame must be a pure function of time, because a video renders in separate parallel parts. The butterflies
and fireflies are closed-form functions of t. The flock is simulated in fixed steps of 1/60 s from the moment it
first appears, with a fixed seed, and cached: any part that starts later simply replays the same steps from the
start, so every part and every still sees exactly the same birds.

All of it is light drawn into the glow layer before the text protection pass, so the words dim it the same way
they dim snow, beams and figures. In the calm lower third (BOTTOM_CALM) the creatures are dimmed and thinned; the
flock also steers up and out of it.
"""
import math

import numpy as np
import moderngl

import song as S
import creatures_shaders as CS

CALM_Y = 0.335      # top of the calm lower third (same as render.py)
DT = 1.0 / 60.0     # flock simulation step
TILT = 0.22         # the viewer is a little below the birds: depth shows as this much height
TAU = 2.0 * math.pi


def val(name, t, default=None):
    v = getattr(S, name, None)
    if v is None:
        return default
    return v(t) if callable(v) else v


def col(c, default):
    c = c if c is not None else default
    return S.lin(c) if isinstance(c, str) else np.asarray(c, dtype=np.float64)


def ss(a, b, x):
    u = np.clip((np.asarray(x, dtype=np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def calm_k(y, calm, k=0.75):
    """Light kept at height y in the calm lower third (1 above it)."""
    return 1.0 - calm * k * (1.0 - ss(CALM_Y - 0.07, CALM_Y + 0.05, y))


def hash1(n):
    return np.modf(np.abs(np.sin(np.asarray(n, dtype=np.float64) * 12.9898 + 78.233) * 43758.5453))[0]


def _norm(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


class Strokes:
    """Collects soft tapered strokes for one draw call."""

    def __init__(self):
        self.parts = []

    def add(self, a, b, wa, wb, style, c):
        """a, b: (n, 2) screen fractions; wa, wb: (n,) half widths in pixels; style: (fill, rim, halo); c: (n, 3)."""
        n = a.shape[0]
        if n == 0:
            return
        st = np.zeros((n, 4))
        st[:, :len(style)] = style
        self.parts.append(np.hstack([a, b, np.broadcast_to(np.atleast_1d(wa), (n,))[:, None],
                                     np.broadcast_to(np.atleast_1d(wb), (n,))[:, None], st, c]))

    def data(self):
        return np.vstack(self.parts).astype("f4") if self.parts else np.zeros((0, 13), "f4")


# ---------------------------------------------------------------- doves
class Flock:
    """A deterministic flock: state at any time t is replayed from the start in fixed steps (cached)."""

    def __init__(self, n, seed=4242):
        self.n, self.seed = n, seed
        rng = np.random.default_rng(seed)
        self.sf = 0.90 + 0.22 * rng.random(n)          # own cruising speed
        self.size = 0.82 + 0.36 * rng.random(n)
        self.freq = 2.8 + 0.8 * rng.random(n)          # wing beats per second
        self.orb = 0.55 + 0.75 * rng.random(n)         # own orbit radius around the target
        self.yoff = rng.random(n) - 0.5
        self.wph = rng.random((n, 3)) * TAU
        self.wfr = 0.18 + 0.42 * rng.random((n, 3))
        self.spawn = rng.normal(size=(n, 3)) * np.array([0.05, 0.035, 0.09])
        self.reveal = rng.permutation(n)               # the order in which DOVES reveals the birds
        self.glide_ph = rng.random(n) * TAU
        # the time the flock first appears
        total = float(getattr(S, "TOTAL", 60.0))
        ts = None
        for t in np.arange(0.0, total + 0.05, 0.05):
            if (val("DOVES", float(t), 0.0) or 0.0) > 0.001:
                ts = float(t)
                break
        self.ts = ts
        self.k = -1

    # -- steering inputs
    @staticmethod
    def goal(t):
        path = getattr(S, "DOVES_PATH", None)
        if path is not None:
            g = path(t) if callable(path) else _path_track(path)(t)
        else:
            g = getattr(S, "DOVES_TARGET", None)
            if callable(g):
                g = g(t)
            if g is None:
                g = (0.5, 0.80)
            elif isinstance(g, (int, np.integer)):
                g = S.STAR_POS[int(g)]
        return float(g[0]) * S.ASPECT, float(g[1])

    def _reset(self):
        n = self.n
        self.rng = np.random.default_rng(self.seed + 1)
        fr = val("DOVES_FROM", self.ts, (-0.05, 0.45))
        self.P = np.array([fr[0] * S.ASPECT, fr[1], 0.0]) + self.spawn
        gx, gy = self.goal(self.ts)
        d0 = _norm(np.array([gx, gy, 0.0]) - self.P + np.array([0.0, 0.25, 0.0]))
        s0 = 0.22 * float(val("DOVES_SPEED", self.ts, 1.0))
        self.V = d0 * (s0 * self.sf)[:, None]
        self.D = _norm(np.array([0.0, 1.0, 0.0]) - (d0[:, 1:2]) * d0)
        self.phase = self.rng.random(n) * TAU
        self.mode = np.zeros(n)                         # 0 flapping, 1 gliding
        self.beats = self.rng.integers(2, 6, n).astype(np.float64)
        self.glide = np.zeros(n)
        self.gs = np.zeros(n)
        self.H = np.zeros((4096, n, 12))
        self.k = -1
        self._store()

    def _store(self):
        self.k += 1
        if self.k >= self.H.shape[0]:
            self.H = np.concatenate([self.H, np.zeros_like(self.H)])
        climb = self.V[:, 1] / np.maximum(np.linalg.norm(self.V, axis=1), 1e-6)
        self.H[self.k] = np.hstack([self.P, self.V, self.D, self.phase[:, None], self.gs[:, None], climb[:, None]])

    def _step(self):
        n, t = self.n, self.ts + self.k * DT
        P, V = self.P, self.V
        s0 = 0.22 * float(val("DOVES_SPEED", t, 1.0))
        size = float(val("DOVES_SIZE", t, 0.03)) / 0.03
        # flocking
        diff = P[:, None, :] - P[None, :, :]
        d = np.sqrt((diff ** 2).sum(-1)) + np.eye(n) * 1e3
        rs, rn = 0.075 * size, 0.18
        near_s = (d < rs)[..., None]
        sep = (diff / d[..., None] * (rs / d - 1.0)[..., None] * near_s).sum(1) * 2.4
        nb = (d < rn).astype(np.float64)
        cnt = np.maximum(nb.sum(1), 1.0)[:, None]
        has = (nb.sum(1) > 0)[:, None]
        ali = ((nb @ V) / cnt - V) * has * 0.9
        coh = ((nb @ P) / cnt - P) * has * 0.5
        # seek the goal, then wheel round it
        gx, gy = self.goal(t)
        G = np.array([gx, gy, 0.0])
        rel = P - G
        R = float(val("DOVES_ORBIT", t, 0.14))
        aim = G + np.stack([np.zeros(n), self.yoff * 0.05, np.zeros(n)], 1)
        seek = _norm(aim - P) * (s0 * self.sf)[:, None]
        if R > 0:
            Ri = R * self.orb
            rh = np.sqrt(rel[:, 0] ** 2 + rel[:, 2] ** 2) + 1e-6
            tang = np.stack([-rel[:, 2], np.zeros(n), rel[:, 0]], 1) / rh[:, None]
            radial = np.stack([rel[:, 0], np.zeros(n), rel[:, 2]], 1) / rh[:, None]
            orbit = tang * (s0 * self.sf)[:, None] + radial * ((Ri - rh) / Ri * 0.8 * s0)[:, None]
            orbit[:, 1] += (aim[:, 1] - P[:, 1]) * 1.5
            dist = np.linalg.norm(rel * np.array([1.0, 1.6, 1.0]), axis=1)
            wo = 1.0 - ss(1.6 * Ri, 3.6 * Ri, dist)
            desired = seek * (1 - wo)[:, None] + orbit * wo[:, None]
        else:
            desired = seek
        steer = (desired - V) * 1.7
        # a little life of its own
        tw = t * self.wfr + self.wph
        wander = np.stack([np.sin(tw[:, 0]), 0.7 * np.sin(tw[:, 1]), np.sin(tw[:, 2])], 1) * 0.22 * s0 / 0.22
        # stay in the picture, out of the calm lower third, and not too deep
        bnd = np.zeros_like(P)
        A = S.ASPECT
        bnd[:, 0] = np.clip(-0.12 - P[:, 0], 0, None) - np.clip(P[:, 0] - (A + 0.12), 0, None)
        bnd[:, 1] = -np.clip(P[:, 1] - 0.95, 0, None) * 2.0
        bnd[:, 2] = np.clip(-0.28 - P[:, 2], 0, None) - np.clip(P[:, 2] - 0.28, 0, None)
        bnd *= 4.0
        calm = float(val("BOTTOM_CALM", t, 0.0) or 0.0)
        bnd[:, 1] += calm * 5.0 * np.clip(CALM_Y + 0.08 - P[:, 1], 0, None)
        acc = sep + ali + coh + steer + wander + bnd
        am = np.linalg.norm(acc, axis=1, keepdims=True)
        acc *= np.minimum(1.0, 2.2 / np.maximum(am, 1e-9))
        V = V + acc * DT
        sp = np.linalg.norm(V, axis=1)
        tgt = s0 * self.sf
        sp2 = np.clip(sp + (tgt - sp) * min(1.0, DT * 1.2), 0.5 * tgt, 1.6 * tgt)
        V = V / np.maximum(sp, 1e-9)[:, None] * sp2[:, None]
        self.P = P + V * DT
        self.V = V
        # bank: the dorsal side leans into the lift (the turn plus holding the bird up)
        f = _norm(V)
        lift = acc - (acc * f).sum(1, keepdims=True) * f + np.array([0.0, 0.55, 0.0])
        lift -= (lift * f).sum(1, keepdims=True) * f
        ln = np.linalg.norm(lift, axis=1, keepdims=True)
        Dt = np.where(ln > 1e-5, lift / np.maximum(ln, 1e-9), self.D)
        D = self.D + (Dt - self.D) * min(1.0, DT * 5.0)
        D -= (D * f).sum(1, keepdims=True) * f
        self.D = _norm(D)
        # wing beats: a few beats, then a glide; climbing birds keep flapping
        climb = np.clip(V[:, 1] / np.maximum(tgt, 1e-6), -1.0, 1.0)
        r = self.rng.random((n, 3))
        fl = self.mode == 0
        old = np.floor(self.phase / TAU)
        rate = self.freq * (1.0 + 0.35 * np.clip(climb, 0, None) - 0.25 * np.clip(-climb, 0, None))
        self.phase = np.where(fl, self.phase + TAU * rate * DT, self.phase)
        done = fl & (np.floor(self.phase / TAU) > old)
        self.beats -= done
        end = fl & (self.beats <= 0)
        keep = end & (climb > 0.45)
        self.beats = np.where(keep, 2 + np.floor(r[:, 0] * 3), self.beats)
        go = end & ~keep
        self.mode = np.where(go, 1.0, self.mode)
        self.glide = np.where(go, (0.45 + 1.1 * r[:, 1]) * np.where(climb < -0.2, 1.4, 1.0), self.glide)
        gl = self.mode == 1
        self.glide = np.where(gl, self.glide - DT, self.glide)
        back = gl & (self.glide <= 0)
        self.mode = np.where(back, 0.0, self.mode)
        self.beats = np.where(back, 2 + np.floor(r[:, 2] * 5), self.beats)
        self.gs += ((self.mode == 1) - self.gs) * min(1.0, DT / 0.14)
        self._store()

    def at(self, t):
        """Interpolated snapshot (n, 12) at time t (t >= ts), simulating forward as needed."""
        x = (t - self.ts) / DT
        k0 = int(math.floor(x))
        if self.k < 0:
            self._reset()
        need = max(k0 + 1, 0)
        while self.k < need:
            self._step()
        u = x - k0
        a, b = self.H[max(k0, 0)], self.H[max(k0 + 1, 0)]
        return a * (1 - u) + b * u

    def hist(self, te):
        """Snapshots at earlier times te (array), from the cache (te <= the latest simulated time)."""
        x = np.clip((te - self.ts) / DT, 0.0, self.k)
        k0 = np.floor(x).astype(int)
        k1 = np.minimum(k0 + 1, self.k)
        u = (x - k0)[:, None, None]
        return self.H[k0] * (1 - u) + self.H[k1] * u


_PATHS = {}


def _path_track(path):
    key = id(path)
    if key not in _PATHS:
        from track import Track
        _PATHS[key] = Track([(float(k[0]), tuple(k[1])) for k in path], "DOVES_PATH")
    return _PATHS[key]


def wing_angle(u):
    """Flap profile: 0 at the top of the stroke; the downstroke is a little faster than the upstroke."""
    uw = u + 0.07 * np.sin(TAU * u)
    return np.radians(15.0 + 50.0 * np.cos(TAU * uw)), np.sin(TAU * uw)


def project(o):
    """A 3D offset (height units; z toward the viewer) to a screen offset (fractions). The viewer is a little
    below the birds, so depth shows as a little height."""
    return np.stack([o[..., 0] / S.ASPECT, o[..., 1] + TILT * o[..., 2]], -1)


def draw_doves(fl, t, h, st, pts):
    amt = float(val("DOVES", t, 0.0) or 0.0)
    if fl.ts is None or t < fl.ts or amt <= 0.001:
        return
    n = fl.n
    s = fl.at(t)
    P, V, D = s[:, 0:3], s[:, 3:6], _norm(s[:, 6:9])
    phase, gs = s[:, 9], s[:, 10]
    f = _norm(V)
    D = _norm(D - (D * f).sum(1, keepdims=True) * f)
    Lat = np.cross(f, D)
    vis = np.clip(amt * n - fl.reveal, 0.0, 1.0)
    calm = float(val("BOTTOM_CALM", t, 0.0) or 0.0)
    ctr = np.stack([P[:, 0] / S.ASPECT, P[:, 1] + TILT * P[:, 2]], 1)
    depth = np.clip(P[:, 2], -0.3, 0.3)
    sc = 1.0 / (1.0 - 0.9 * depth)
    bright = float(val("DOVES_BRIGHT", t, 1.0)) * vis * calm_k(ctr[:, 1], calm) * (0.72 + 0.5 * (depth + 0.3) / 0.6)
    keep = bright > 0.004
    if not keep.any():
        return
    L = float(val("DOVES_SIZE", t, 0.03)) * fl.size * sc     # body length, height units
    Lpx = L * h
    c = col(val("DOVES_COLOR", t), "#fff1da")
    cw = c[None, :] * bright[:, None] * 0.55
    u = (phase / TAU) % 1.0
    th_f, sn = wing_angle(u)
    th_h, _ = wing_angle((u - 0.07) % 1.0)
    gpose = np.radians(8.0 + 4.0 * np.sin(t * 1.3 + fl.glide_ph))
    th1 = th_f * (1 - gs) + gpose * gs
    th2 = th_h * 1.15 * (1 - gs) + (gpose * 0.4) * gs
    fold = 1.0 - 0.30 * np.clip(-sn, 0, None) * (1 - gs)     # the hand folds in on the upstroke
    bob = (-0.05 * np.cos(TAU * (u + 0.07 * np.sin(TAU * u))) * (1 - gs))[:, None] * D

    def pt(a, b_, c_=0.0):
        o = (f * np.asarray(a)[..., None] + D * np.asarray(b_)[..., None] + Lat * np.asarray(c_)[..., None]) \
            * L[:, None] + bob * L[:, None]
        return ctr + project(o)

    k = keep
    # body, head and a fanned tail (style: fill, rim, halo, edge softness)
    st.add(pt(-0.30, 0.0)[k], pt(0.22, 0.02)[k], (0.08 * Lpx)[k], (0.12 * Lpx)[k], (0.85, 0.05, 0.08, 0.35), cw[k])
    hd = pt(0.36, 0.07)[k]
    st.add(hd, hd, (0.065 * Lpx)[k], (0.065 * Lpx)[k], (0.95, 0.05, 0.08, 0.35), cw[k])
    for sp in (-1.0, 0.0, 1.0):
        st.add(pt(-0.28, 0.0)[k], pt(-0.62 + 0.03 * abs(sp), -0.02 - 0.02 * abs(sp), 0.11 * sp)[k],
               (0.035 * Lpx)[k], (0.075 * Lpx)[k], (0.42, 0.04, 0.03, 0.6), cw[k] * 0.8)
    # wings: arm then hand, the hand lagging the arm so the beat ripples out to the tip; on the downstroke the
    # hand curls down further, so the wing bends like a cupped feathered wing; feathers fan along the trailing edge
    curl = np.radians(28.0) * np.clip(sn, 0, None) * (1 - gs)
    th2c = th2 - curl
    for side in (-1.0, 1.0):
        sh = np.array([0.08, 0.04, 0.0])
        arm = _norm(Lat * (side * np.cos(th1))[:, None] + D * np.sin(th1)[:, None] - 0.15 * f)
        hand = _norm(Lat * (side * np.cos(th2c))[:, None] + D * np.sin(th2c)[:, None] - 0.35 * f)
        o_sh = (f * sh[0] + D * sh[1])
        o_wr = o_sh + arm * 0.42
        o_tp = o_wr + hand * (0.62 * fold)[:, None]

        def P2(o):
            return ctr + project((o + bob) * L[:, None])

        a_, w_, tp = P2(o_sh), P2(o_wr), P2(o_tp)
        st.add(a_[k], w_[k], (0.10 * Lpx)[k], (0.14 * Lpx)[k], (0.60, 0.05, 0.05, 0.5), cw[k])
        st.add(w_[k], tp[k], (0.13 * Lpx)[k], (0.035 * Lpx)[k], (0.60, 0.06, 0.05, 0.5), cw[k])
        # feathers: from points along the wing, swept back and out, longest at the hand (the primaries)
        for j, u_ in enumerate((0.25, 0.45, 0.62, 0.78, 0.92)):
            base = o_sh + (o_tp - o_sh) * u_
            ln = 0.10 + 0.13 * u_
            tipd = _norm(-f * (1.0 - 0.55 * u_) + hand * (0.25 + 0.6 * u_ * u_))
            e = base + tipd * (ln * (0.75 + 0.25 * fold))[:, None]
            st.add(P2(base)[k], P2(e)[k], (0.045 * Lpx)[k], (0.012 * Lpx + 0.5)[k], (0.42, 0.05, 0.02, 0.7),
                   cw[k] * 0.75)
    # faint spark trail: sparks shed on a fixed time grid, so each spark lives the same life in every render part
    tr = float(val("DOVES_TRAIL", t, 1.0))
    if tr > 0.001:
        rate, K = 15.0, 14
        ke = math.floor(t * rate) - np.arange(K)
        te = ke / rate
        ok = te >= fl.ts
        if ok.any():
            ke, te = ke[ok], te[ok]
            Hh = fl.hist(te)                                         # (K, n, 12)
            Pp = Hh[..., 0:3]
            base = np.stack([Pp[..., 0] / S.ASPECT, Pp[..., 1] + TILT * Pp[..., 2]], -1)
            ids = ke[:, None] * 131.0 + np.arange(n)[None, :] * 7.31
            j1, j2, j3, j4 = hash1(ids), hash1(ids + 0.37), hash1(ids + 0.71), hash1(ids + 1.13)
            age = (t - te)[:, None]
            Ls = L[None, :]
            x = base[..., 0] + ((j1 - 0.5) * 1.1 * Ls + 0.004 * np.sin(age * 3.0 + j3 * 6.0)) / S.ASPECT
            y = base[..., 1] + (j2 - 0.5) * 0.6 * Ls - 0.018 * age
            inten = 0.55 * tr * np.exp(-age * 2.3) * (0.55 + 0.45 * np.sin(age * 9.0 + j3 * 6.28)) * bright[None, :]
            sz = (1.3 + 2.4 * j4) * (0.7 + 0.5 * sc[None, :])
            sc_col = col(val("DOVES_SPARK_COLOR", t), "#ffd9a0")
            m = (inten > 0.003).ravel()
            pts.append(np.hstack([x.reshape(-1, 1), y.reshape(-1, 1), sz.reshape(-1, 1),
                                  inten.reshape(-1, 1) * sc_col[None, :]])[m])


# ---------------------------------------------------------------- butterflies
class Butterflies:
    """Closed-form flight: a meandering path, a fast irregular flutter with short glides, and landings."""

    def __init__(self, n, seed=5150):
        rng = np.random.default_rng(seed)
        self.n = n
        self.w = TAU * (0.025 + 0.05 * rng.random((n, 4)))
        self.p = rng.random((n, 6)) * TAU
        self.loop = TAU * (0.35 + 0.35 * rng.random(n))
        self.freq = 4.4 + 1.2 * rng.random(n)
        self.size = 0.85 + 0.30 * rng.random(n)
        self.gw = TAU * (0.06 + 0.08 * rng.random((n, 2)))
        self.tilt = (rng.random(n) - 0.5) * 0.9
        self.land_ph = rng.random(n) * TAU
        total = float(getattr(S, "TOTAL", 60.0))
        self.events = []
        for i in range(n):
            ev, t = [], 3.0 + 7.0 * rng.random()
            while t < total:
                dur = 2.6 + 2.6 * rng.random()
                ev.append((t, t + dur, rng.random()))
                t += dur + 8.0 + 9.0 * rng.random()
            self.events.append(ev)

    def path(self, i, t, area):
        x0, x1, y0, y1 = area
        w, p = self.w[i], self.p[i]
        x = (x0 + x1) / 2 + (x1 - x0) / 2 * (0.62 * np.sin(w[0] * t + p[0]) + 0.38 * np.sin(w[1] * t + p[1]))
        y = (y0 + y1) / 2 + (y1 - y0) / 2 * (0.62 * np.sin(w[2] * t + p[2]) + 0.38 * np.sin(w[3] * t + p[3]))
        lp = self.loop[i] * t + p[4]
        return x + 0.018 * np.sin(lp) / S.ASPECT * 1.6, y + 0.014 * np.cos(lp)

    def landing(self, i, t, spots):
        w, spot = 0.0, None
        for (a, b, r) in self.events[i]:
            wi = float(ss(a - 1.8, a, t) * (1.0 - ss(b, b + 1.2, t)))
            if wi > w:
                w, spot = wi, spots[int(r * len(spots)) % len(spots)]
        return w, spot

    def pos(self, i, t, area, spots):
        x, y = self.path(i, t, area)
        w, spot = self.landing(i, t, spots)
        if spot is not None and w > 0:
            e = w * w * (3 - 2 * w)
            x, y = x * (1 - e) + spot[0] * e, y * (1 - e) + spot[1] * e
        return np.array([x, y]), w


def draw_butterflies(bf, t, h, st):
    amt = float(val("BUTTERFLIES", t, 0.0) or 0.0)
    if amt <= 0.001:
        return
    area = val("BUTTERFLIES_AREA", t, (0.08, 0.92, 0.40, 0.68))
    hz = S.HORIZON
    spots = val("BUTTERFLIES_LAND", t, None) or [(0.06, hz + 0.035), (0.15, hz + 0.02), (0.86, hz + 0.025),
                                                 (0.94, hz + 0.04)]
    calm = float(val("BOTTOM_CALM", t, 0.0) or 0.0)
    cols = val("BUTTERFLIES_COLOR", t, ("#ffd7ef", "#bfe3ff"))
    if isinstance(cols, str):
        cols = (cols, cols)
    ca, cb = col(cols[0], "#ffd7ef"), col(cols[1], "#bfe3ff")
    size = float(val("BUTTERFLIES_SIZE", t, 0.022))
    A = S.ASPECT
    for i in range(bf.n):
        vis = float(np.clip(amt * bf.n - i, 0.0, 1.0))
        if vis <= 0.0:
            continue
        p, w = bf.pos(i, t, area, spots)
        pa, _ = bf.pos(i, t - 0.03, area, spots)
        pb, _ = bf.pos(i, t + 0.03, area, spots)
        v = (pb - pa) * np.array([A, 1.0])
        sp = np.linalg.norm(v)
        f_fly = v / sp if sp > 1e-6 else np.array([0.0, 1.0])
        f_land = np.array([math.sin(bf.tilt[i]), math.cos(bf.tilt[i])])
        # wings: fast, slightly irregular flutter; short glides with the wings open; slow fanning when landed
        ph = TAU * bf.freq[i] * t + 0.7 * math.sin(TAU * 0.23 * t + bf.p[i, 5])
        g = float(ss(0.62, 0.92, 0.5 + 0.5 * (0.6 * math.sin(bf.gw[i, 0] * t + bf.p[i, 0])
                                                + 0.4 * math.sin(bf.gw[i, 1] * t + bf.p[i, 3]))))
        th_fly = math.radians(40.0 + 52.0 * math.cos(ph))
        th_gl = math.radians(10.0 + 5.0 * math.sin(1.7 * t))
        th_land = math.radians(70.0 + 24.0 * math.sin(TAU * 0.3 * t + bf.land_ph[i]))
        th = (th_fly * (1 - g) + th_gl * g) * (1 - w) + th_land * w
        f = f_fly * (1 - w) + f_land * w
        wob = math.radians(9.0) * math.sin(ph) * (1 - g) * (1 - w)
        f = np.array([f[0] * math.cos(wob) - f[1] * math.sin(wob), f[0] * math.sin(wob) + f[1] * math.cos(wob)])
        f /= max(np.linalg.norm(f), 1e-9)
        nrm = np.array([-f[1], f[0]])
        dor = nrm * float(np.clip(nrm[1] * 3.0, -1.0, 1.0))
        bob = 0.005 * (-math.cos(ph)) * (1 - g) * (1 - w)
        ctr = p + np.array([0.0, bob])
        Ls = size * bf.size[i]
        Lpx = Ls * h
        k = vis * float(calm_k(ctr[1], calm)) * float(val("BUTTERFLIES_BRIGHT", t, 1.0))
        if k <= 0.004:
            continue

        def P2(a, out=None):
            o = f * a if out is None else f * a + out
            return (ctr + np.array([o[0] / A, o[1]]) * Ls)[None, :]

        cbody = (S.lin("#fff0d8") * 0.9)[None, :] * k
        for side in (-1.0, 1.0):
            out = side * nrm * math.cos(th) + dor * math.sin(th)
            st.add(P2(0.06), P2(0.36, out * 0.95), 0.10 * Lpx, 0.27 * Lpx, (0.30, 0.90, 0.13), ca[None, :] * k)
            st.add(P2(-0.02), P2(-0.30, out * 0.62), 0.09 * Lpx, 0.21 * Lpx, (0.28, 0.85, 0.12), cb[None, :] * k)
            # antennae
            st.add(P2(0.38), P2(0.70, side * nrm * 0.22), 0.012 * Lpx + 0.5, 0.012 * Lpx + 0.5, (0.7, 0.0, 0.0),
                   cbody * 0.6)
        st.add(P2(-0.34), P2(0.30), 0.055 * Lpx, 0.05 * Lpx, (0.9, 0.4, 0.15), cbody)
        hd = P2(0.36)
        st.add(hd, hd, 0.06 * Lpx, 0.06 * Lpx, (0.9, 0.4, 0.15), cbody)


# ---------------------------------------------------------------- fireflies
class Fireflies:
    def __init__(self, n=160, seed=909):
        self.n = n
        self.s = np.random.default_rng(seed).random((n, 16))

    def points(self, t):
        amt = float(val("FIREFLIES", t, 0.0) or 0.0)
        if amt <= 0.001:
            return None
        s = self.s
        y0, y1 = val("FIREFLIES_Y", t, (0.05, S.HORIZON + 0.10))
        x = s[:, 0] + 0.030 * np.sin(t * (0.12 + 0.22 * s[:, 2]) + TAU * s[:, 3]) \
            + 0.012 * np.sin(t * (0.5 + 0.5 * s[:, 4]) + TAU * s[:, 5])
        y = y0 + (y1 - y0) * s[:, 1] ** 0.85 + 0.020 * np.sin(t * (0.17 + 0.25 * s[:, 6]) + TAU * s[:, 7]) \
            + 0.006 * np.sin(t * (0.8 + 0.9 * s[:, 8]) + TAU * s[:, 9])
        # blink: a soft flash every few seconds (some flash twice), a faint glow between
        per = 2.6 + 3.6 * s[:, 10]
        u = ((t + s[:, 11] * per) % per) / per
        e = np.where(u < 0.22, np.sin(np.pi * u / 0.22) ** 2, 0.0)
        e2 = np.where((s[:, 12] < 0.3) & (u > 0.22) & (u < 0.33), np.sin(np.pi * (u - 0.22) / 0.11) ** 2, 0.0)
        e = np.maximum(e, 0.8 * e2)
        b = 0.10 + 0.90 * e
        on = s[:, 13] < amt
        calm = float(val("BOTTOM_CALM", t, 0.0) or 0.0)
        low = 1.0 - ss(CALM_Y - 0.07, CALM_Y + 0.05, y)
        on &= s[:, 14] >= 0.6 * calm * low                       # sparse in the calm lower third
        b = b * (1.0 - 0.5 * calm * low) * float(val("FIREFLIES_BRIGHT", t, 1.3)) * on
        x = x % 1.0
        sz = (4.0 + 4.5 * s[:, 15]) * (0.75 + 0.35 * e)
        c = col(val("FIREFLIES_COLOR", t), "#e4ff9c")
        cc = c[None, :] * (0.85 + 0.3 * s[:, 15:16]) * b[:, None] * 2.6
        m = b > 0.002
        return np.hstack([x[:, None], y[:, None], sz[:, None], cc])[m]


# ---------------------------------------------------------------- the layer
class Creatures:
    def __init__(self, R):
        self.R = R
        self.on = any(getattr(S, k, None) is not None for k in ("DOVES", "BUTTERFLIES", "FIREFLIES"))
        if not self.on:
            return
        ctx = self.ctx = R.ctx
        self.w, self.h = R.w, R.h
        self.flock = Flock(int(getattr(S, "DOVES_COUNT", 14))) if getattr(S, "DOVES", None) is not None else None
        self.bf = Butterflies(int(getattr(S, "BUTTERFLIES_COUNT", 4))) if getattr(S, "BUTTERFLIES", None) is not None else None
        self.ff = Fireflies() if getattr(S, "FIREFLIES", None) is not None else None
        self.p_st = ctx.program(vertex_shader=CS.STROKE_VS, fragment_shader=CS.STROKE_FS)
        self.p_pt = ctx.program(vertex_shader=CS.POINT_VS, fragment_shader=CS.POINT_FS)
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        self.MAXS, self.MAXP = 6000, 8000
        self.b_st = ctx.buffer(reserve=self.MAXS * 13 * 4, dynamic=True)
        self.b_pt = ctx.buffer(reserve=self.MAXP * 6 * 4, dynamic=True)
        self.v_st = ctx.vertex_array(self.p_st, [(quad, "2f", "aCorner"),
                                                 (self.b_st, "2f 2f 2f 4f 3f/i", "aA", "aB", "aW", "aStyle", "aCol")])
        self.v_pt = ctx.vertex_array(self.p_pt, [(self.b_pt, "2f 1f 3f", "aPos", "aSize", "aCol")])

    def draw(self, t):
        if not self.on:
            return
        st, pts = Strokes(), []
        if self.ff is not None:
            p = self.ff.points(t)
            if p is not None and len(p):
                pts.append(p)
        if self.flock is not None:
            draw_doves(self.flock, t, self.h, st, pts)
        if self.bf is not None:
            draw_butterflies(self.bf, t, self.h, st)
        if pts:
            d = np.vstack(pts).astype("f4")[:self.MAXP]
            if len(d):
                self.b_pt.write(d.tobytes())
                self.p_pt["uPx"].value = self.R.px
                self.v_pt.render(moderngl.POINTS, vertices=len(d))
        d = st.data()[:self.MAXS]
        if len(d):
            self.b_st.write(d.tobytes())
            self.p_st["uRes"].value = (float(self.w), float(self.h))
            self.v_st.render(moderngl.TRIANGLE_STRIP, instances=len(d))
