"""Film 01, The Wave: the wave of light and the things it wakes (helpers for engine/songs/ten_01_the_wave.py).

Pure numpy point sets for the 3D layer (engine/p3d/api.py). Nothing here is shared engine code; it is the
film's own geometry:

  Kinematics    the wave is a ring round the drop point; its radius, height and curl are functions of time
  Wave          the crest: particles that run up the face and over the top (down the back of a swell, or out
                along the lip and down the curtain of a curling wave), a rope of sparks on the crest, spray
  Wake          glints on the water that light where the crest has passed (a static set with birth times)
  Field         any fixed points (lanterns, ridges of hills, sleepers) that light as the crest reaches them
  Ignite        wraps a body of light: cold sparse blue dust until the crest reaches it, then gold from the
                feet up
  Crowd         many people from a few baked body shapes, riding a moving frame, arms lifting in a wave

Coordinates: metres, y up, the lake is y = 0 (engine/p3d conventions). The drop point is (X0, 0, Z0). The film
rides the part of the ring that runs toward -z. A place relative to the crest is (u, b, h): u metres along the
crest from the axis, b metres behind the crest (toward the drop point; negative is ahead, in the night), h
metres above the water.
"""
import numpy as np

from .api import lin

TAU = 2.0 * np.pi


def keys_linear(keys):
    ts = np.array([k[0] for k in keys], np.float64)
    vs = np.array([k[1] for k in keys], np.float64)
    return lambda t: np.interp(t, ts, vs)


def keys_smooth(keys):
    """A function of t through (t, value) keys, eased (smoothstep) between them, flat outside."""
    ts = np.array([k[0] for k in keys], np.float64)
    vs = np.array([k[1] for k in keys], np.float64)

    def f(t):
        t = np.asarray(t, np.float64)
        i = np.clip(np.searchsorted(ts, t, side="right") - 1, 0, len(ts) - 2)
        u = np.clip((t - ts[i]) / np.maximum(ts[i + 1] - ts[i], 1e-9), 0.0, 1.0)
        u = u * u * (3.0 - 2.0 * u)
        r = vs[i] * (1.0 - u) + vs[i + 1] * u
        return float(r) if r.ndim == 0 else r
    return f


def _hash(n, seed):
    rng = np.random.default_rng(seed)
    return rng


def smoothstep(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


class Kinematics:
    """Where the wave is. speed: (t, m/s) keys (linear; the radius is its integral). height, curl: eased keys.
    t_impact: the ring is born. drop: (x, z) of the drop point."""

    def __init__(self, speed, height, curl, drop, t_impact, total=60.0):
        self.speed = keys_linear(speed)
        self.height = keys_smooth(height)
        self.curl = keys_smooth(curl)
        self.x0, self.z0 = float(drop[0]), float(drop[1])
        self.t_impact = float(t_impact)
        self.grid = np.arange(-1.0, total + 2.0 + 1e-9, 1.0 / 480.0)
        v = self.speed(self.grid) * (self.grid >= self.t_impact)
        r = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(self.grid))])
        self.r_tab = r

    def R(self, t):
        return np.interp(t, self.grid, self.r_tab)

    def t_at_radius(self, r):
        """When the crest reaches radius r (inverse of R; the radius never shrinks)."""
        rt = np.maximum.accumulate(self.r_tab + 1e-9 * np.arange(len(self.r_tab)))
        return np.interp(r, rt, self.grid)

    def crest_z(self, t):
        return self.z0 - self.R(t)

    def world(self, u, b, h, t):
        """Wave frame (u, b, h) at t to world points (N, 3) (arrays broadcast)."""
        R = max(float(self.R(t)), 1e-3)
        u, b, h = np.broadcast_arrays(np.asarray(u, np.float64), np.asarray(b, np.float64), np.asarray(h, np.float64))
        rho = np.maximum(R - b, 0.0)
        th = u / R
        return np.stack([self.x0 + rho * np.sin(th), h, self.z0 - rho * np.cos(th)], axis=-1)

    def point(self, u, b, h, t):
        return self.world(u, b, h, t).reshape(3)

    def time_at(self, x, z):
        """When the crest reaches the world place (x, z)."""
        r = np.hypot(np.asarray(x, np.float64) - self.x0, np.asarray(z, np.float64) - self.z0)
        return self.t_at_radius(r)


def profile(s, H, c, back=None):
    """The cross section of the wave: s in 0..1 runs from the trough in front, up the face to the crest
    (s = SF), then (c = 0) down the back of a swell or (c = 1) out along the curling lip and down its curtain.
    Returns (b, h): b behind the crest (negative ahead), h above the water."""
    SF = 0.42
    H = np.asarray(H, np.float64)
    c = np.asarray(c, np.float64)
    Lb = 2.6 * H + 0.15 if back is None else back
    wf = 0.42
    q = np.clip(s / SF, 0.0, 1.0)
    bf = -wf * H * (1.0 - q) ** 1.8
    hf = H * q
    p = np.clip((s - SF) / (1.0 - SF), 0.0, 1.0)
    # down the back
    bb = Lb * p
    hb = H * (1.0 - p) ** 2
    # out along the lip: a quarter ellipse forward and down
    psi = p * np.pi * 0.5
    A = H * (wf + (1.30 - wf) * c)
    bl = -A * np.sin(psi)
    hl = H * np.cos(psi) * (1.0 + 0.10 * np.sin(psi * 2.0) * c)
    b2 = bb * (1.0 - c) + bl * c
    h2 = hb * (1.0 - c) + hl * c
    on_face = s < SF
    return np.where(on_face, bf, b2), np.where(on_face, hf, h2)


class Wave:
    """The crest as a point set. glow(t): overall strength; mouth(t): None, or the u beyond which the curl
    eases out (the open end of the barrel); plume(t): 0..1, the crest thrown up as it breaks. centers: the
    places along the crest (u) where the particles are densest (where the camera rides)."""
    wants_camera = True

    def __init__(self, kin, n_face=150000, n_back=50000, n_rope=20000, n_spray=26000, half_len=420.0, k=4.0,
                 glow=None, mouth=None, plume=None, seed=11, colors=None, centers=(0.0,), back=0.22,
                 face=0.30, near=(0.5, 3.0), plume_h=14.0):
        self.kin = kin
        rng = np.random.default_rng(seed)
        self.half, self.k = half_len, k
        self.glow = glow or (lambda t: 1.0)
        self.mouth = mouth
        self.plume = plume
        self.plume_h = plume_h
        self.back_a, self.face_a, self.near = back, face, near
        c = dict(top="#fff3d2", face="#ffbe55", deep="#ff8a2a", back="#ff9a3c", spray="#ffe6b0", rope="#fff8e6")
        if colors:
            c.update(colors)
        self.col = {k_: lin(v) for k_, v in c.items()}
        self.centers = np.asarray(centers, np.float64)

        def vs(n):
            return rng.uniform(-1.0, 1.0, n), rng.integers(0, len(self.centers), n)
        self.f_v, self.f_c = vs(n_face)
        self.f_s, self.f_j = rng.random(n_face), rng.normal(0.0, 1.0, (n_face, 3))
        self.f_rate = rng.uniform(0.07, 0.16, n_face)
        self.f_seed = rng.random(n_face)
        self.b_v, self.b_c = vs(n_back)
        self.b_w, self.b_j = rng.random(n_back), rng.normal(0.0, 1.0, (n_back, 3))
        self.b_seed = rng.random(n_back)
        self.r_v, self.r_c = vs(n_rope)
        self.r_j, self.r_seed = rng.normal(0.0, 1.0, (n_rope, 3)), rng.random(n_rope)
        self.s_v, self.s_c = vs(n_spray)
        self.s_ph, self.s_per = rng.random(n_spray), rng.uniform(0.9, 2.2, n_spray)
        self.s_dir = rng.normal(0.0, 1.0, (n_spray, 3))
        self.s_seed = rng.random(n_spray)

    def _u(self, v, c):
        return self.centers[c] + self.half * np.sinh(self.k * v) / np.sinh(self.k)

    def _curl(self, u, t):
        c = float(self.kin.curl(t))
        if c <= 0.0:
            return np.zeros_like(u)
        if self.mouth is None:
            return np.full_like(u, c)
        m = self.mouth(t)
        if m is None:
            return np.full_like(u, c)
        return c * (1.0 - smoothstep(m - 9.0, m + 9.0, u))

    def _lens(self, pos, size, cam):
        """Near the lens the points shrink to fine sparks and fade, so the camera can ride inside the wave
        without a fog of huge discs."""
        if cam is None:
            return size, 1.0
        d = np.linalg.norm(pos - np.asarray(cam.pos, np.float64)[None], axis=1)
        return np.minimum(size, 0.0045 * d + 0.002), smoothstep(self.near[0], self.near[1], d)

    def sample(self, t, cam=None):
        kin = self.kin
        if t < kin.t_impact - 0.01:
            return []
        R = float(kin.R(t))
        H = max(float(kin.height(t)), 0.02)
        g = float(self.glow(t))
        if g <= 0.002:
            return []
        tw = t - kin.t_impact
        ring = TAU * max(R, 0.05)
        sz = 0.010 * np.sqrt(H / 0.15) ** 0.85
        out = []

        # ---- the face and the lip (or the back of a swell): particles flowing round the section
        u = self._u(self.f_v, self.f_c)
        vis = np.abs(u) < 0.5 * ring
        cu = self._curl(u, t)
        s = (self.f_s + self.f_rate * tw) % 1.0
        b, h = profile(s, H, cu)
        jit = 0.03 * H + 0.004
        b = b + self.f_j[:, 0] * jit
        h = np.maximum(h + self.f_j[:, 1] * jit * 0.6, 0.0)
        uu = u + self.f_j[:, 2] * jit
        pos = kin.world(uu, b, h, t)
        top = np.exp(-((s - 0.42) / 0.05) ** 2)                 # the crest line
        lipfront = cu * np.exp(-((s - 0.62) / 0.12) ** 2)       # the leading edge of a curling lip
        hrel = np.clip(h / H, 0.0, 1.0)
        col = (self.col["deep"][None] * (1.0 - hrel[:, None]) + self.col["face"][None] * hrel[:, None])
        col = col * (1.0 - top[:, None]) + self.col["top"][None] * top[:, None]
        ends = smoothstep(0.0, 0.05, s) * (1.0 - smoothstep(0.93, 1.0, s))
        back_fade = np.where(s > 0.42, 1.0 - (1.0 - cu) * smoothstep(0.50, 0.85, s), 1.0)
        size, nf = self._lens(pos, sz * (0.7 + 0.5 * self.f_seed), cam)
        a = (self.face_a * (0.35 + 0.65 * hrel) + 0.9 * top + 0.45 * lipfront) * ends * back_fade * vis * g * nf
        out.append(dict(pos=pos, size=size, color=col, alpha=a, kind="soft",
                        emit=1.0 + 1.2 * top, seed=self.f_seed, twinkle=0.35, streak=0.5))

        # ---- the back: light the wave leaves behind it, drifting backward and fading
        u = self._u(self.b_v, self.b_c)
        vis = np.abs(u) < 0.5 * ring
        Lb = 2.6 * H + 0.15
        w = (self.b_w + 0.05 * tw) % 1.0
        bb = Lb * (0.10 + 1.3 * w ** 1.3)
        hb = H * np.exp(-2.5 * (bb / Lb) ** 2) * 0.85 + np.abs(self.b_j[:, 1]) * 0.02 * H
        pos = kin.world(u + self.b_j[:, 2] * 0.05 * H, bb + self.b_j[:, 0] * 0.04 * H, hb, t)
        size, nf = self._lens(pos, sz * 0.7, cam)
        a = self.back_a * (1.0 - w) ** 2.0 * smoothstep(0.0, 0.06, w) * vis * g * nf
        out.append(dict(pos=pos, size=size, color=self.col["back"], alpha=a, kind="spark",
                        seed=self.b_seed, twinkle=0.8, emit=1.4))

        # ---- the rope of sparks on the crest (and on the lip's leading edge)
        u = self._u(self.r_v, self.r_c)
        vis = np.abs(u) < 0.5 * ring
        cu = self._curl(u, t)
        s_r = 0.42 + 0.22 * cu
        b, h = profile(s_r, H, cu)
        pos = kin.world(u + self.r_j[:, 2] * 0.01 * H, b + self.r_j[:, 0] * 0.015 * H,
                        h + np.abs(self.r_j[:, 1]) * 0.015 * H + 0.01, t)
        size, nf = self._lens(pos, sz * 0.7, cam)
        a = 0.85 * vis * g * (0.6 + 0.4 * self.r_seed) * nf
        out.append(dict(pos=pos, size=size, color=self.col["rope"], alpha=a, kind="spark", emit=2.6,
                        seed=self.r_seed, twinkle=0.9))

        # ---- spray thrown up off the crest, drifting back in the wind of the ride; a plume when it breaks
        u = self._u(self.s_v, self.s_c)
        vis = np.abs(u) < 0.5 * ring
        cu = self._curl(u, t)
        age = (self.s_ph + tw / self.s_per) % 1.0
        T = age * self.s_per
        up = (0.9 + 0.4 * self.s_dir[:, 1]) * np.sqrt(H) * 1.6
        bk = (1.0 + 0.5 * self.s_dir[:, 0]) * np.sqrt(H) * 1.0
        b0, h0 = profile(np.full_like(u, 0.42) + 0.15 * cu, H, cu)
        pb = b0 + bk * T
        ph = np.maximum(h0 + up * T - 0.5 * 9.8 * 0.35 * T * T, 0.0)
        pu = u + self.s_dir[:, 2] * 0.4 * np.sqrt(H) * T
        boost = 1.0
        size = sz * 0.7
        if self.plume is not None:
            pl = float(self.plume(t))
            if pl > 0.0:
                hp = np.sqrt(self.plume_h)
                ph = ph + pl * (4.0 + 7.0 * self.s_dir[:, 1] ** 2) * T * hp
                pb = pb - pl * 2.5 * T * hp
                pu = pu + pl * self.s_dir[:, 2] * 2.0 * T * hp
                boost = 1.0 + 2.0 * pl
                size = size * (1.0 + 1.5 * pl)
        pos = kin.world(pu, pb, ph, t)
        size, nf = self._lens(pos, size, cam)
        a = 0.45 * np.sin(np.pi * age) ** 1.5 * vis * g * boost * nf
        out.append(dict(pos=pos, size=size, color=self.col["spray"], alpha=a, kind="spark", emit=1.5,
                        seed=self.s_seed, twinkle=0.7))
        return out


class Tube:
    """The inside of the barrel: streaks of light running up the face, over the lip and down the curtain,
    drawn as short line segments along the flow, dense where the camera glides (u0..u1). gain(t) fades it."""
    wants_camera = True

    def __init__(self, kin, u0, u1, n=60000, gain=None, mouth=None, seed=17, color="#ffd07a", top="#fff4dc"):
        rng = np.random.default_rng(seed)
        self.kin, self.mouth = kin, mouth
        self.u = rng.uniform(u0, u1, n)
        self.s = rng.random(n)
        self.rate = rng.uniform(0.10, 0.22, n)
        self.j = rng.normal(0.0, 1.0, (n, 3))
        self.seed = rng.random(n)
        self._gain = gain
        self.col, self.top = lin(color), lin(top)

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t, cam=None):
        kin = self.kin
        if self.gain(t) <= 0.002:
            return []
        H = max(float(kin.height(t)), 0.05)
        c = float(kin.curl(t))
        cu = np.full_like(self.u, c)
        if self.mouth is not None:
            cu = c * (1.0 - smoothstep(self.mouth(t) - 9.0, self.mouth(t) + 9.0, self.u))
        s = (self.s + self.rate * (t - kin.t_impact)) % 1.0
        ds = 0.018 + 0.02 * self.seed
        b1, h1 = profile(s, H, cu)
        b0, h0 = profile(np.maximum(s - ds, 0.0), H, cu)
        jb, jh = self.j[:, 0] * 0.025 * H, self.j[:, 1] * 0.015 * H
        p1 = kin.world(self.u + self.j[:, 2] * 0.02, b1 + jb, np.maximum(h1 + jh, 0.0), t)
        p0 = kin.world(self.u + self.j[:, 2] * 0.02, b0 + jb, np.maximum(h0 + jh, 0.0), t)
        top = np.exp(-((s - 0.42) / 0.07) ** 2)
        col = self.col[None] * (1.0 - top[:, None]) + self.top[None] * top[:, None]
        ends = smoothstep(0.02, 0.08, s) * (1.0 - smoothstep(0.9, 0.99, s))
        a = (0.35 + 0.5 * top) * ends
        if cam is not None:
            d = np.linalg.norm(p1 - np.asarray(cam.pos, np.float64)[None], axis=1)
            a = a * smoothstep(0.35, 1.5, d)
        return dict(pos=p1, pos2=p0, size=0.006, color=col, alpha=a, alpha2=a * 0.2, kind="line", seed=self.seed,
                    emit=1.3)


class Field:
    """Fixed points that light up when the crest reaches them (a static set: the birth times run on the
    graphics card). pos (N, 3); each lights `delay` seconds after the crest passes its (x, z)."""
    static = True

    def __init__(self, kin, pos, size, color, alpha=1.0, kind="spark", delay=0.0, flash=2.0, fade=0.35,
                 twinkle=0.6, emit=1.0, gain=None, reflect=True, seed=3):
        self.kin = kin
        pos = np.asarray(pos, np.float64)
        rng = np.random.default_rng(seed)
        birth = kin.time_at(pos[:, 0], pos[:, 2]) + delay
        self.batch = dict(pos=pos, size=size, color=color, alpha=alpha, kind=kind, birth=birth, flash=flash,
                          fade=fade, twinkle=twinkle, emit=emit, seed=rng.random(len(pos)), reflect=reflect)
        self._gain = gain

    def sample(self, t):
        return self.batch

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))


class Static:
    """Fixed points that are simply there (sleepers before the wave reaches them); gain(t) fades them."""
    static = True

    def __init__(self, batch, gain=None):
        self.batch, self._gain = batch, gain

    def sample(self, t):
        return self.batch

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))


class Ignite:
    """A body of light that sleeps until t_wake (sparse cold blue dust), then lights gold from the feet up."""

    def __init__(self, body, t_wake, cold="#7f9cff", rise=0.9, sleep_alpha=0.30, keep=0.35, height=1.7):
        self.body, self.t_wake = body, float(t_wake)
        self.cold = lin(cold)
        self.rise, self.sleep_alpha, self.keep, self.height = rise, sleep_alpha, keep, height
        self.wants_camera = bool(getattr(body, "wants_camera", False))

    def sample(self, t, cam=None):
        r = self.body.sample(t, cam) if self.wants_camera else self.body.sample(t)
        if isinstance(r, dict):
            r = [r]
        out = []
        for b in r or []:
            b = dict(b)
            p = np.asarray(b["pos"], np.float64)
            n = len(p)
            if n == 0:
                continue
            y0 = float(np.min(p[:, 1])) if n else 0.0
            front = (t - self.t_wake) / self.rise * self.height          # metres of the body already lit
            on = smoothstep(-0.25, 0.05, front - (p[:, 1] - y0))
            col = np.asarray(b.get("color", (1.0, 1.0, 1.0)), np.float64)
            if col.ndim == 1:
                col = np.broadcast_to(col, (n, 3))
            cold = np.broadcast_to(self.cold, (n, 3)) * 0.55
            b["color"] = cold * (1.0 - on[:, None]) + col * on[:, None]
            idx = (np.arange(n) * 0.6180339887) % 1.0
            sleeping = np.where(idx < self.keep, self.sleep_alpha, 0.0)
            al = np.asarray(b.get("alpha", 1.0), np.float64)
            flare = 1.0 + 2.5 * np.exp(-((front - (p[:, 1] - y0)) / 0.25) ** 2) * (front > -0.3)
            b["alpha"] = al * (sleeping * (1.0 - on) + on * flare)
            out.append(b)
        return out

    def gain(self, t):
        return self.body.gain(t) if hasattr(self.body, "gain") else 1.0


class Crowd:
    """Many people from a few baked shapes (each shape in two poses: arms down and arms raised), standing
    at places (u, b) on a moving frame given by place(u, b, t) -> (N, 3) world points. The arms lift in a
    wave that runs along u from t_lift at `lift_speed` metres a second."""

    def __init__(self, shapes, places, place, colors, t_lift=None, lift_speed=60.0, alpha=0.5, size=0.018,
                 gain=None, seed=5, show=(0.0, 1e9), center=0.0):
        rng = np.random.default_rng(seed)
        self.shapes = [(np.asarray(a, np.float64), np.asarray(b_, np.float64)) for a, b_ in shapes]
        self.places = np.asarray(places, np.float64)          # (M, 2): u, b
        self.place = place
        self.kind_of = rng.integers(0, len(self.shapes), len(self.places))
        self.yaw = rng.normal(0.0, 0.25, len(self.places))
        self.scale = rng.uniform(0.85, 1.12, len(self.places))
        self.delay = rng.uniform(-0.15, 0.15, len(self.places))
        self.colors = [lin(c) for c in colors]
        self.col_of = rng.integers(0, len(self.colors), len(self.places))
        self.t_lift, self.lift_speed, self.alpha, self.size = t_lift, lift_speed, alpha, size
        self._gain = gain
        self.show = show
        self.seed = seed
        self.center = float(center)

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t):
        if t < self.show[0] or t > self.show[1] or self.gain(t) <= 0.002:
            return []
        base = self.place(self.places[:, 0], self.places[:, 1], t)        # (M, 3) feet
        pos_all, col_all, seed_all = [], [], []
        for m in range(len(self.places)):
            down, up = self.shapes[self.kind_of[m]]
            if self.t_lift is not None:
                tl = self.t_lift + abs(self.places[m, 0] - self.center) / self.lift_speed + self.delay[m]
                a = float(smoothstep(tl, tl + 0.7, t))
            else:
                a = 0.0
            p = down if a <= 0.0 else (up if a >= 1.0 else down * (1.0 - a) + up * a)
            cy, sy = np.cos(self.yaw[m]), np.sin(self.yaw[m])
            x = p[:, 0] * cy + p[:, 2] * sy
            z = -p[:, 0] * sy + p[:, 2] * cy
            q = np.stack([x, p[:, 1], z], axis=1) * self.scale[m] + base[m]
            pos_all.append(q)
            col_all.append(np.broadcast_to(self.colors[self.col_of[m]], q.shape))
        pos = np.concatenate(pos_all)
        col = np.concatenate(col_all)
        n = len(pos)
        sd = (np.arange(n) * 0.754877666) % 1.0
        return dict(pos=pos, color=col, size=self.size, alpha=self.alpha, kind="spark", seed=sd, twinkle=0.6,
                    emit=1.3)


def bake_people(Body, n=2600, seed=1, poses=("stand", "raise")):
    """A few baked people (points of the whole clothed body), each in several poses: "stand" (arms down) and
    any gestures of engine/p3d (raise, open_arms, look_up, ...). Facing -z (backs to a camera that looks
    toward -z), feet at the origin. Returns a list of dicts pose -> (N, 3), the same N for every pose."""
    out = []
    specs = [("woman", "dress", dict(hair=True)), ("man", "coat", {}), ("woman", "robe", {}),
             ("man", "tunic", {}), ("child", None, {}), ("woman", "coat", dict(hair=True))]
    for k, (shape, garment, extra) in enumerate(specs):
        kw = dict(extra)
        if garment:
            kw["garment"] = garment
        d = {}
        for pose in poses:
            g = [] if pose == "stand" else [(0.0, 100.0, pose)]
            b = Body(shape, at=(0.0, 0.0), facing=180.0, look="glitter", points=n, seed=seed + k, gesture=g, **kw)
            p, _ = b.shape_points(1.6)
            d[pose] = np.asarray(p, np.float64)
        m = min(len(v) for v in d.values())
        out.append({key: v[:m] for key, v in d.items()})
    return out
