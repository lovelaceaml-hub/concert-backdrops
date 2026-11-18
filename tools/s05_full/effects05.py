"""Song 05 "God Bless You!", full backdrop: the light of the story (point sets for the 3D layer).

    Tree       the tree of blessing: a seed of light on the shore that grows with the song into a young tree of
               light threads, blossoms in verse 1, line 6, swells and ripens nine fruits in the nine colours
    Island     a small low mound of golden grass light under the tree
    Seed       the small warm light handed over from song 04, drifting to the shore during the opening
    Stones     stepping stones of light that appear under the helper's feet, one on each step
    Waves      a wave of peace (one wide slow ring across the lake) each time a word is practised
    Load       the soft grey load on the brother's shoulders, thinning under the prayer, blown away as light
    Prayer     the violet light of each prayer: verse 1 from the praying hands across the water to the brother;
               verse 2 down from the arch through the praying hands to the sister
    Scatter    the brother's blessing drifting across the water to his sister (verse 2, line 1)
    Halos      the sister's tender voice as soft halos of light (verse 2, line 3; light only)
    Petals     blossom petals in the air, more in verse 2, a storm at the climax
    Shores     at the climax countless tiny lights of people along the far shores
    Road       a road of light rising from the tree toward the arch at the climax
    Drift      in the hold a few seeds of light drift from the tree to rest on the water (song 06's grain)

Every class is a pure function of song time t. No em dash or en dash anywhere in this file.
"""
import numpy as np

from p3d.api import lin

TAU = 2.0 * np.pi
NINE = ["#EA5A5E", "#F2B25E", "#F6CE46", "#5ABA5A", "#62B2FA", "#667AF6", "#9E6AF6", "#EE62A6", "#364E96"]
VIOLET = "#9E6AF6"
ROSE = "#EE62A6"
GOLD = "#ffd27a"
CREAM = "#fff3dc"


def _ss(a, b, x):
    x = np.asarray(x, np.float64)
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    if a.ndim == 0 and b.ndim == 0 and b <= a:
        return (x >= a).astype(np.float64)
    u = np.clip((x - a) / np.maximum(b - a, 1e-9), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _s(a, b, x):
    return float(_ss(a, b, x))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _bez(p0, p1, p2, u):
    u = np.asarray(u, np.float64)[..., None]
    return (1 - u) ** 2 * p0 + 2 * (1 - u) * u * p1 + u * u * p2


# ------------------------------------------------------------------------------------------------ the tree
GROWTH = [(0.0, 0.0), (13.6, 0.0), (16.0, 0.035), (24.0, 0.05), (36.5, 0.08), (40.0, 0.12), (52.0, 0.30),
          (56.0, 0.33), (70.0, 0.42), (76.0, 0.50), (82.0, 0.58), (95.0, 0.62), (110.0, 0.72), (125.0, 0.84),
          (139.0, 0.90), (146.0, 1.0), (999.0, 1.0)]


def growth(t):
    ts, vs = zip(*GROWTH)
    return float(np.interp(t, ts, vs))


class Tree:
    """Light threads: each branch is a line of fine points that grows out from its base in order."""

    def __init__(self, base, height=3.3, seed=5):
        self.base = np.asarray(base, np.float64)
        rng = np.random.default_rng(seed)
        segs = []                                       # (p0, p1, order0, order1, depth)

        def grow(p0, d, length, depth, o0):
            p1 = p0 + d * length
            o1 = o0 + length / height * 0.55
            segs.append((p0, p1, o0, o1, depth))
            if depth >= 5:
                return
            n = 2 if depth == 0 else (3 if depth < 3 else 2)
            for k in range(n):
                a = rng.uniform(0, TAU) if depth else (k * np.pi + rng.uniform(-0.4, 0.4))
                tilt = (0.42 + 0.25 * rng.random()) if depth else 0.50
                nd = d * np.cos(tilt) + np.array([np.cos(a), 0.0, 0.55 * np.sin(a)]) * np.sin(tilt)
                nd[1] = max(nd[1], 0.18 if depth < 3 else -0.05)
                nd /= np.linalg.norm(nd)
                grow(p1, nd, length * (0.72 + 0.12 * rng.random()), depth + 1, o1 + 0.02 * k)

        grow(self.base.copy(), _v(0.03, 1.0, 0.0) / np.linalg.norm(_v(0.03, 1.0, 0.0)), 1.15, 0, 0.0)
        self.segs = segs
        top = max(max(s[2], s[3]) for s in segs)
        pts, us, o0s, o1s, dep, sd = [], [], [], [], [], []
        for p0, p1, o0, o1, depth in segs:
            o0, o1 = o0 / top, o1 / top
            L = float(np.linalg.norm(p1 - p0))
            thick = 0.11 * 0.62 ** depth
            n = int(220 * L * (1.0 + 2.5 * thick / 0.11))
            u = rng.random(n)
            r = rng.normal(size=(n, 3)) * thick * 0.35
            pts.append(p0[None] + (p1 - p0)[None] * u[:, None] + r)
            us.append(u)
            o0s.append(np.full(n, o0))
            o1s.append(np.full(n, o1))
            dep.append(np.full(n, depth))
            sd.append(rng.random(n))
        self.p = np.concatenate(pts)
        self.u = np.concatenate(us)
        self.o0, self.o1 = np.concatenate(o0s), np.concatenate(o1s)
        self.dep = np.concatenate(dep)
        self.sd = np.concatenate(sd)
        self.size = (0.028 * 0.80 ** self.dep + 0.012 * self.sd).astype(np.float32)
        warm = lin("#ffd890")
        green = lin("#e6f0a0")
        k = np.clip(self.dep / 5.0, 0, 1)[:, None]
        self.col = (warm[None] * (1 - 0.5 * k) + green[None] * 0.5 * k)
        # tips: blossoms and fruits
        tips = [s for s in segs if s[4] >= 4]
        self.tips = np.array([s[1] for s in tips])
        rng2 = np.random.default_rng(seed + 1)
        nb = 1600
        ti = rng2.integers(0, len(self.tips), nb)
        self.bpos = self.tips[ti] + rng2.normal(size=(nb, 3)) * 0.13
        self.bseed = rng2.random(nb)
        self.btip_o = np.array([s[3] for s in tips])[ti] / top
        # nine fruits: well spread tips in the crown
        order = np.argsort(self.tips[:, 0] + 0.3 * self.tips[:, 1])
        pick = order[np.linspace(0, len(order) - 1, 9).astype(int)]
        self.fruit = self.tips[pick] + _v(0.0, -0.10, 0.0)
        hx = np.argsort(self.fruit[:, 0])
        self.fruit = self.fruit[hx]
        self.height = float(self.p[:, 1].max() - self.base[1])

    def tip_top(self):
        return self.base + _v(0.0, self.height, 0.0)

    def sample(self, t):
        g = growth(t)
        if g <= 0.0:
            return None
        out = []
        # a branch point shows once the growth front has passed it along its branch
        front = (g - self.o0) / np.maximum(self.o1 - self.o0, 1e-6)
        vis = np.clip((front - self.u) / 0.08, 0.0, 1.0)
        m = vis > 0.01
        if m.any():
            breathe = 1.0 + 0.10 * np.sin(t * 1.3 + self.sd[m] * TAU)
            pulse = 1.0 + 0.6 * _s(146.0, 147.5, t) * (1.0 - _s(150.0, 156.0, t))
            out.append(dict(pos=self.p[m], size=self.size[m], color=self.col[m] * 0.85 * pulse,
                            alpha=vis[m] * breathe, emit=1.4, kind="spark", twinkle=0.35, seed=self.sd[m]))
        # the young sprout glow at the base before the tree stands
        a0 = _s(13.4, 14.2, t)
        if a0 > 0:
            out.append(dict(pos=self.base[None] + _v(0, 0.08, 0)[None], size=0.9, color=lin("#ffe2a0"),
                            alpha=0.22 * a0, kind="soft"))
        # blossoms: open from 76 s along the crown, swell to fruit colour later, in the hold breathe softly
        b = _ss(76.0 + 4.0 * self.bseed, 79.0 + 4.0 * self.bseed, t) * (self.btip_o < g + 0.02)
        if b.max() > 0.01:
            mb = b > 0.01
            pink = lin("#ffc6d2")
            cream = lin("#fff1e2")
            c = pink[None] * self.bseed[mb, None] + cream[None] * (1 - self.bseed[mb, None])
            sway = 0.02 * np.sin(t * 0.9 + self.bseed[mb] * 9.0)[:, None]
            storm = _s(146.0, 147.0, t) * (1.0 - _s(149.0, 158.0, t))
            out.append(dict(pos=self.bpos[mb] + sway, size=0.05 + 0.04 * self.bseed[mb],
                            color=c * (0.7 + 0.5 * storm), alpha=b[mb] * 0.85, emit=1.2, kind="soft"))
        # the nine fruits: small glows from 110 s, their colours from 139 s, bright at the climax
        f = _s(110.0, 124.0, t)
        if f > 0:
            ripe = _s(139.0, 146.0, t)
            gold = lin("#ffe0a0")
            cols = np.array([gold * (1 - ripe) + lin(c) * ripe * 1.15 for c in NINE])
            br = 0.55 + 0.45 * ripe + 0.5 * _s(146.0, 147.5, t) * (1 - _s(150.0, 158.0, t))
            br = br * (1.0 + 0.08 * np.sin(t * 1.1 + np.arange(9)))
            size = 0.07 + 0.08 * f + 0.03 * ripe
            out.append(dict(pos=self.fruit, size=np.full(9, size), color=cols * br[:, None], alpha=f, emit=2.6,
                            kind="spark"))
            out.append(dict(pos=self.fruit, size=np.full(9, 0.55 * f + 0.2 * ripe), color=cols * 0.5,
                            alpha=0.22 * f, kind="soft"))
        return out


class Island:
    """A low mound of golden grass light where the tree stands."""
    static = True

    def __init__(self, base, radius=1.25, n=2600):
        rng = np.random.default_rng(8)
        a = rng.random(n) * TAU
        r = radius * np.sqrt(rng.random(n))
        h = 0.10 * (1 - (r / radius) ** 2) + 0.06 * rng.random(n) ** 3
        self.pos = np.stack([base[0] + r * np.cos(a), h, base[2] + 0.6 * r * np.sin(a)], 1)
        self.s = rng.random(n)

    def sample(self, t):
        return dict(pos=self.pos, size=0.02 + 0.02 * self.s, color=lin("#ffd98c") * 0.7, alpha=0.8,
                    kind="spark", twinkle=0.5, seed=self.s, birth=13.6 + 2.0 * self.s, fade=1.2)


class Seed:
    """The small warm light from song 04's last frame: it drifts to the shore and becomes the seed of hope."""

    def __init__(self, start, end):
        self.a, self.b = np.asarray(start, np.float64), np.asarray(end, np.float64)

    def sample(self, t):
        if t > 16.0:
            return None
        u = _s(1.5, 13.4, t)
        p = self.a + (self.b - self.a) * u + _v(0, 0.04 * np.sin(t * 1.7), 0)
        a = 1.0 - _s(13.5, 15.5, t)
        pulse = 1.0 + 0.15 * np.sin(t * 3.0)
        return [dict(pos=p[None], size=0.11 * pulse, color=lin("#fff0cc"), alpha=a, emit=5.0, kind="spark"),
                dict(pos=p[None], size=1.1, color=lin("#ffd890"), alpha=0.30 * a, kind="soft")]


class Stones:
    """Stepping stones of light under a walker: one appears on each step and glows rose gold."""

    def __init__(self, walks, n_ring=110):
        self.walks = walks                      # list of (t0, t1, p0 (x, z), p1 (x, z), linger)
        rng = np.random.default_rng(13)
        self.a = rng.random(n_ring) * TAU
        self.s = rng.random(n_ring)
        self.stones = []
        for t0, t1, p0, p1, linger in walks:
            d = float(np.hypot(p1[0] - p0[0], p1[1] - p0[1]))
            n = max(int(d / 0.55), 3)
            for k in range(n):
                f = (k + 0.5) / n
                x = p0[0] + (p1[0] - p0[0]) * f
                z = p0[1] + (p1[1] - p0[1]) * f
                self.stones.append((x, z, t0 + (t1 - t0) * f - 0.35, t1 + linger))

    def sample(self, t):
        pos, al, col, size = [], [], [], []
        glow_p, glow_a = [], []
        gold, rose = lin("#ffd890"), lin(ROSE)
        for x, z, tb, te in self.stones:
            a = _s(tb, tb + 0.35, t) * (1.0 - _s(te, te + 3.0, t))
            if a <= 0.005:
                continue
            flash = 1.0 + 1.5 * np.exp(-max(t - tb, 0.0) / 0.4) * (t > tb)
            r = 0.27 + 0.03 * np.sin(self.a * 3 + t)
            p = np.stack([x + r * np.cos(self.a), np.full_like(self.a, 0.02), z + 0.55 * r * np.sin(self.a)], 1)
            pos.append(p)
            al.append(np.full(len(p), a))
            col.append(np.tile(gold * 0.6 + rose * 0.25, (len(p), 1)) * flash)
            size.append(0.025 + 0.02 * self.s)
            glow_p.append(_v(x, 0.03, z))
            glow_a.append(a)
        if not pos:
            return None
        return [dict(pos=np.concatenate(pos), alpha=np.concatenate(al), color=np.concatenate(col),
                     size=np.concatenate(size), kind="spark", emit=1.6, twinkle=0.3),
                dict(pos=np.array(glow_p), size=0.75, color=gold * 0.5 + rose * 0.3, alpha=0.35 * np.array(glow_a),
                     kind="soft")]


class Waves:
    """Waves of peace: one wide slow ring of gold across the lake, from a centre, at each practised word."""

    def __init__(self, waves, n=1600, speed=4.2, reach=34.0):
        self.waves = waves                       # list of (t0, (x, z))
        rng = np.random.default_rng(17)
        self.a = rng.random(n) * TAU
        self.s = rng.random(n)
        self.speed, self.reach = speed, reach

    def sample(self, t):
        out = []
        for t0, (x, z) in self.waves:
            age = t - t0
            if age < 0 or age > self.reach / self.speed + 0.5:
                continue
            r = 0.4 + self.speed * age * (1.0 - 0.25 * age / (self.reach / self.speed))
            fade = (1.0 - age / (self.reach / self.speed + 0.5)) ** 1.3 * _s(0.0, 0.4, age)
            jitter = 0.08 * (self.s - 0.5) * (1 + 0.1 * r)
            p = np.stack([x + (r + jitter) * np.cos(self.a), np.full_like(self.a, 0.025),
                          z + (r + jitter) * np.sin(self.a)], 1)
            out.append(dict(pos=p, size=0.05 + 0.03 * self.s + 0.004 * r, color=lin("#ffe2a8") * 0.9,
                            alpha=fade * 0.75, emit=1.3, kind="soft", reflect=False))
        return out or None


class Load:
    """The brother's hard day: a soft pale grey haze resting on his shoulders (light, never dark). It thins under
    the prayer and, when the two lift it together, breaks into sparks that blow away as warm light."""

    def __init__(self, cast, t_thin=(30.0, 36.0), t_off=66.4):
        self.cast, self.t_thin, self.t_off = cast, t_thin, t_off
        rng = np.random.default_rng(23)
        n = 520
        self.o = rng.normal(size=(n, 3)) * np.array([0.22, 0.12, 0.16])
        self.o[:, 1] = np.abs(self.o[:, 1])
        self.s = rng.random((n, 3))

    def sample(self, t):
        if t < 14.3 or t > self.t_off + 3.0:
            return None
        neck = self.cast.where("B", t, "neck")
        base = neck + _v(0.0, 0.10, -0.05)
        k = (1.0 - 0.55 * _s(*self.t_thin, t)) * _s(14.6, 17.0, t)
        sway = 0.02 * np.sin(t * 0.8 + self.s[:, :1] * TAU)
        if t < self.t_off:
            p = base + self.o + sway
            return dict(pos=p, size=0.10 + 0.08 * self.s[:, 1], color=lin("#c9c4d6") * 0.30, alpha=0.55 * k,
                        kind="soft", seed=self.s[:, 2], twinkle=0.1)
        age = t - self.t_off
        p = base + self.o * (1 + 2.5 * age) + _v(0.4, 0.9, 0.2) * age * (0.5 + self.s[:, :1])
        col = lin("#c9c4d6") * 0.30 * (1 - _s(0, 0.6, age)) + lin("#ffe0a0") * _s(0, 0.6, age)
        return dict(pos=p, size=0.03 + 0.02 * self.s[:, 1], color=col, alpha=k * (1 - _s(1.2, 3.0, age)),
                    emit=2.0, kind="spark", twinkle=0.6, seed=self.s[:, 2])


class Stream:
    """A stream of light along a path given by three moving points (start, bend, end): its head travels from
    the start to the end over [t0, t1], then it rests around the end as a soft cloak until t2."""

    def __init__(self, start, mid, end, t0, t1, t2, color, n=700, seed=31, around=0.30):
        self.start, self.mid, self.end = start, mid, end
        self.t0, self.t1, self.t2 = t0, t1, t2
        self.color = lin(color)
        rng = np.random.default_rng(seed)
        self.s = rng.random((n, 4))
        self.jit = rng.normal(size=(n, 3))
        self.around = around

    def sample(self, t):
        if t < self.t0 or t > self.t2 + 2.0:
            return None
        p0, p1, p2 = self.start(t), self.mid(t), self.end(t)
        head = _s(self.t0, self.t1, t)
        tail = _s(self.t0 + 0.6 * (self.t1 - self.t0), self.t1 + 1.2, t)
        u = tail + (head - tail) * self.s[:, 0]
        pos = _bez(p0, p1, p2, u) + self.jit * (0.05 + 0.10 * np.sin(np.pi * u))[:, None]
        a_line = (1.0 - _s(self.t1 + 0.6, self.t1 + 1.6, t))
        out = [dict(pos=pos, size=0.03 + 0.03 * self.s[:, 1], color=self.color * 1.3, alpha=0.9 * a_line,
                    emit=2.2, kind="spark", twinkle=0.5, seed=self.s[:, 2], reflect=True)]
        # the cloak: light resting round the end point
        c = _s(self.t1 - 0.3, self.t1 + 1.0, t) * (1.0 - _s(self.t2, self.t2 + 2.0, t))
        if c > 0.01:
            ang = self.s[:, 0] * TAU + 0.3 * t
            rr = self.around * (0.7 + 0.5 * self.s[:, 1])
            q = p2 + np.stack([rr * np.cos(ang), (self.s[:, 2] - 0.7) * 0.55, 0.7 * rr * np.sin(ang)], 1)
            out.append(dict(pos=q, size=0.04 + 0.05 * self.s[:, 3], color=self.color * 0.9, alpha=0.65 * c,
                            emit=1.4, kind="soft", seed=self.s[:, 3], twinkle=0.3))
            out.append(dict(pos=p2[None], size=1.1, color=self.color * 0.6, alpha=0.18 * c, kind="soft"))
        return out


class Scatter:
    """A soft scatter of gold drifting from one moving point to another (the brother's blessing to his sister)."""

    def __init__(self, src, dst, t0, t1, n=500, seed=37):
        self.src, self.dst, self.t0, self.t1 = src, dst, t0, t1
        rng = np.random.default_rng(seed)
        self.s = rng.random((n, 4))
        self.j = rng.normal(size=(n, 3))

    def sample(self, t):
        if t < self.t0 or t > self.t1 + 2.0:
            return None
        a, b = self.src(t), self.dst(t)
        dur = self.t1 - self.t0
        born = self.t0 + 0.6 * dur * self.s[:, 0]
        u = np.clip((t - born) / (0.45 * dur), 0, 1)
        mid = 0.5 * (a + b) + _v(0, 1.2, 0)
        p = _bez(a, mid, b, u ** 0.9) + self.j * (0.08 + 0.35 * np.sin(np.pi * u))[:, None]
        al = (t > born) * (1 - _ss(0.85, 1.0, u)) * (1 - _s(self.t1, self.t1 + 2.0, t))
        return dict(pos=p, size=0.03 + 0.03 * self.s[:, 1], color=lin("#ffdc90") * 1.2, alpha=al, emit=2.0,
                    kind="spark", twinkle=0.6, seed=self.s[:, 2])


class Halos:
    """The sister's tender voice: soft rings of light breathing out from her, one every period seconds, that
    travel toward the ones who prayed for her and warm them (light only)."""

    def __init__(self, src, toward, t0, t1, period=2.3, n=260):
        self.src, self.toward, self.t0, self.t1, self.period = src, toward, t0, t1, period
        rng = np.random.default_rng(41)
        self.a = rng.random(n) * TAU
        self.s = rng.random(n)

    def sample(self, t):
        if t < self.t0 or t > self.t1 + 5.0:
            return None
        out = []
        k0 = int(np.floor((t - self.t0) / self.period))
        for k in range(max(k0 - 3, 0), k0 + 1):
            tb = self.t0 + k * self.period
            if tb > self.t1:
                continue
            age = t - tb
            if age < 0 or age > 5.0:
                continue
            a, b = self.src(tb), self.toward(tb)
            c = a + (b - a) * min(age / 5.0, 1.0) * 0.85 + _v(0, 0.3 * age, 0)
            r = 0.25 + 0.38 * age
            p = c + np.stack([r * np.cos(self.a), 0.8 * r * np.sin(self.a), 0.3 * r * np.cos(self.a)], 1)
            fade = _s(0, 0.5, age) * (1 - _s(2.5, 5.0, age))
            out.append(dict(pos=p, size=0.035 + 0.02 * self.s, color=lin("#ffe6c0") * 0.9, alpha=0.55 * fade,
                            emit=1.4, kind="soft"))
        return out or None


class Petals:
    """Blossom petals of light in the air: amount(t) 0..1 says how many; they drift slowly and tumble."""

    def __init__(self, amount, n=700, box=((-14, 14), (0.3, 9.0), (-8, 9))):
        self.amount = amount
        rng = np.random.default_rng(47)
        self.s = rng.random((n, 6))
        self.box = box

    def sample(self, t):
        a = self.amount(t)
        if a <= 0.003:
            return None
        (x0, x1), (y0, y1), (z0, z1) = self.box
        s = self.s
        x = x0 + (x1 - x0) * np.mod(s[:, 0] + 0.010 * t * (0.6 + s[:, 3]), 1.0)
        y = y0 + (y1 - y0) * np.mod(s[:, 1] - 0.012 * t * (0.5 + s[:, 4]), 1.0)
        z = z0 + (z1 - z0) * s[:, 2]
        x = x + 0.4 * np.sin(t * 0.5 + s[:, 5] * TAU)
        p = np.stack([x, y, z], 1)
        show = s[:, 5] < a
        edge = np.minimum(np.mod(s[:, 1] - 0.012 * t * (0.5 + s[:, 4]), 1.0) * 6, 1.0)
        col = np.where(s[:, 3:4] > 0.5, lin("#ffc0cc"), lin("#fff0e6")) * 0.75
        rot = np.stack([t * (0.6 + s[:, 3]) + s[:, 0] * TAU, t * (1.1 + s[:, 4]) + s[:, 1] * TAU], 1)
        return dict(pos=p[show], size=0.06 + 0.04 * s[show, 4], color=col[show], alpha=0.8 * edge[show],
                    kind="petal", rot=rot[show], emit=1.1)


class Shores:
    """At the climax the far shores fill with countless tiny lights of people, in pairs and small families, lit
    from the middle outward like a necklace; they stay softly through the hold."""
    static = True

    def __init__(self, t0=146.4, n=2400):
        rng = np.random.default_rng(53)
        groups = n // 3
        gx = rng.uniform(-1, 1, groups)
        far = 70.0 + 50.0 * rng.random(groups)
        x = gx * (far * 1.25)
        z = -far + 12.0 * np.abs(gx)
        pts, birth, sd = [], [], []
        for i in range(groups):
            m = 1 + rng.integers(1, 3)
            for j in range(m):
                pts.append((x[i] + 0.6 * j, 0.5 + 0.7 * rng.random(), z[i]))
                birth.append(t0 + 4.5 * abs(gx[i]) + 0.4 * rng.random())
                sd.append(rng.random())
        self.p = np.array(pts)
        self.b = np.array(birth)
        self.s = np.array(sd)

    def sample(self, t):
        return dict(pos=self.p, size=0.22 + 0.2 * self.s, color=lin("#ffd890") * 1.4, alpha=0.9, emit=2.0,
                    kind="spark", twinkle=0.6, seed=self.s, birth=self.b, fade=1.0, flash=1.5)

    def gain(self, t):
        return 0.0 if t < 146.0 else 1.0 - 0.35 * _s(153.0, 160.0, t)


class Road:
    """A road of light that rises gently from the tree toward the arch at the climax."""

    def __init__(self, start, end, t0=147.0, t1=151.0, n=2600):
        self.a, self.b = np.asarray(start, np.float64), np.asarray(end, np.float64)
        self.t0, self.t1 = t0, t1
        rng = np.random.default_rng(59)
        self.s = rng.random((n, 4))

    def sample(self, t):
        if t < self.t0:
            return None
        head = _s(self.t0, self.t1, t)
        u = self.s[:, 0] * head
        mid = 0.5 * (self.a + self.b) + _v(0, -3.0, 6.0)
        c = _bez(self.a, mid, self.b, u)
        w = 0.35 * (1.0 - 0.6 * u)
        side = (self.s[:, 1] - 0.5) * 2.0 * w
        p = c + np.stack([side, 0.05 * (self.s[:, 2] - 0.5), 0.3 * side], 1)
        flow = np.mod(self.s[:, 3] - 0.15 * t, 1.0)
        a = (0.55 + 0.45 * flow) * (1.0 - 0.45 * _s(153.0, 160.0, t)) * (1 - 0.7 * u)
        return dict(pos=p, size=0.04 + 0.04 * self.s[:, 2], color=lin("#ffe6b0") * 1.1, alpha=a, emit=1.8,
                    kind="spark", twinkle=0.5, seed=self.s[:, 2])


class Drift:
    """In the hold a few seeds of light leave the tree's fruits and drift down to rest on the water."""

    def __init__(self, fruits, t0=158.0):
        self.f = np.asarray(fruits)
        self.t0 = t0
        rng = np.random.default_rng(61)
        self.s = rng.random((5, 3))

    def sample(self, t):
        if t < self.t0:
            return None
        out = []
        for i in range(5):
            tb = self.t0 + 1.6 * i
            age = t - tb
            if age < 0:
                continue
            f = self.f[(2 * i + 1) % 9]
            land = f.copy()
            land[0] += 0.8 + 1.4 * self.s[i, 0]
            land[2] += 1.2 + 1.0 * self.s[i, 1]
            land[1] = 0.03
            u = _s(0, 6.0, age)
            p = f + (land - f) * u + _v(0.15 * np.sin(age * 1.3), 0, 0) * (1 - u)
            out.append(dict(pos=p[None], size=0.06, color=lin("#ffe7b0") * 1.3, alpha=_s(0, 0.6, age), emit=3.0,
                            kind="spark"))
            out.append(dict(pos=p[None], size=0.5, color=lin("#ffd890"), alpha=0.18 * _s(0, 0.6, age), kind="soft"))
        return out or None
