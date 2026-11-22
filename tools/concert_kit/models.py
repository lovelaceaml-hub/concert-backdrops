"""Deterministic models made from geometry, in metres with Y up.

These builders never read raster assets. Every output is a native p3d point set.
Seed controls design variation, while time controls authored growth and wind.
"""
from __future__ import annotations

import numpy as np
from p3d.api import lin, ribbon

GOLD = "#e8bd77"
PINK = "#ee62a6"


def smooth(a, b, t):
    u = np.clip((np.asarray(t) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def segments(curves, color=GOLD, width=0.008, alpha=0.35, **kw):
    a = np.concatenate([np.asarray(p)[:-1] for p in curves])
    b = np.concatenate([np.asarray(p)[1:] for p in curves])
    return dict(pos=a, pos2=b, kind="line", size=width,
                color=lin(color), alpha=alpha, **kw)


def ring(center, radius, n=80, height=0.0):
    u = np.linspace(0.0, 2.0 * np.pi, n)
    return np.asarray(center) + np.stack([radius * np.cos(u),
        np.full(n, height), radius * np.sin(u)], 1)


class Seat:
    """A low rounded bench, with a visible top and curved supporting legs."""
    static = True

    def __init__(self, at=(-0.89, 0.0, 1.54), width=0.8, depth=0.75,
                 height=0.48, variant="stone", seed=21):
        if variant not in ("stone","garden"):
            raise ValueError("Seat variant must be stone or garden")
        self.at = np.asarray(at, float)
        self.width, self.depth, self.height = width, depth, height
        self.variant, self.seed = variant, seed

    def sample(self, t):
        c = self.at
        u = np.linspace(0, 2 * np.pi, 80)
        loops = []
        for y in (self.height - 0.07, self.height):
            loops.append(c + np.stack([self.width * 0.5 * np.cos(u),
                         np.full(len(u), y), self.depth * 0.5 * np.sin(u)], 1))
        for z in (-0.24, 0.24):
            v = np.linspace(0, np.pi, 30)
            loops.append(c + np.stack([0.31 * np.cos(v),
                0.04 + (self.height - 0.12) * np.sin(v), np.full(len(v), z)], 1))
        if self.variant=="garden":
            for z in np.linspace(-self.depth*.36,self.depth*.36,5):
                loops.append(c+np.array([[-self.width*.48,self.height,z],[-self.width*.52,self.height+.5,z]]))
            v=np.linspace(-1,1,40)
            loops.append(c+np.stack([np.full(len(v),-self.width*.52),
                self.height+.5+.12*(1-v*v),v*self.depth*.4],1))
        rng = np.random.default_rng(self.seed)
        a = rng.uniform(0, 2 * np.pi, 1400)
        r = np.sqrt(rng.random(len(a)))
        pts = c + np.stack([self.width * 0.5 * r * np.cos(a),
            np.full(len(a), self.height), self.depth * 0.5 * r * np.sin(a)], 1)
        return [segments(loops, "#92a3bc", 0.007, 0.22),
                dict(pos=pts, size=0.013, color=lin("#8495ad"), alpha=0.22, kind="soft")]


class Path:
    """A walkable causeway or a shallow arched bridge, with geometric shore edges."""
    static = True

    def __init__(self, at=(0, 0, 0), length=21, width=3.8, variant="shore", seed=7):
        if variant not in ("shore","bridge"):
            raise ValueError("Path variant must be shore or bridge")
        self.at = np.asarray(at, float)
        self.length, self.width, self.variant, self.seed = length, width, variant, seed

    def center(self, u):
        x = 0.65 * np.sin(np.asarray(u) * 0.28)
        y = np.full_like(x, 0.013)
        if self.variant == "bridge":
            y += 0.75 * np.sin(np.pi * np.clip((np.asarray(u) + self.length / 2) / self.length, 0, 1))
        return self.at + np.stack([x, y, np.asarray(u)], -1)

    def sample(self, t):
        z = np.linspace(-self.length * 0.65, self.length * 0.35, 180)
        curves = []
        for side in (-1, 1):
            for off in (0, 0.035, 0.13):
                p = self.center(z)
                p[:, 0] += side * (self.width / 2 + off + 0.12 * np.sin(z * 1.3 + side))
                curves.append(p)
        rng = np.random.default_rng(self.seed)
        u = rng.uniform(z[0], z[-1], 5500)
        p = self.center(u)
        p[:, 0] += rng.uniform(-self.width / 2, self.width / 2, len(p))
        dots = dict(pos=p, size=rng.uniform(0.006, 0.016, len(p)), color=lin("#a1aace"),
                    alpha=0.12, kind="soft", twinkle=0.10)
        return [segments(curves, "#8796b0", 0.006, 0.11), dots]


class Reeds:
    """Curved 3D stems and leaves sharing a traveling wind field."""

    def __init__(self, at=(0, 0, 0), count=35, radius=1.4, height=1.0,
                 variant="reed", seed=2, bloom=11.4):
        if variant not in ("reed","grain"):
            raise ValueError("Reeds variant must be reed or grain")
        self.at = np.asarray(at, float)
        rng = np.random.default_rng(seed)
        self.base = self.at + np.c_[rng.uniform(-radius, radius, count),
            np.zeros(count), rng.uniform(-radius * .6, radius * .6, count)]
        self.h = height * rng.uniform(.52, 1.15, count)
        self.angle = rng.uniform(0, 2 * np.pi, count)
        self.phase = rng.uniform(0, 2 * np.pi, count)
        self.variant, self.bloom = variant, bloom

    def sample(self, t):
        curves, heads = [], []
        u = np.linspace(0, 1, 14)
        for p, h, a, phase in zip(self.base, self.h, self.angle, self.phase):
            wind = .07 * np.sin(.75 * t + phase) + .025 * np.sin(1.8 * t - p[2])
            stem = p + np.stack([(.13 * np.cos(a) + wind) * u ** 2,
                h * u, .13 * np.sin(a) * u ** 2], 1)
            curves.append(stem)
            for side, start in ((1, .38), (-1, .57)):
                leaf = stem[int(start * 13)] + np.stack([side * .22 * u,
                    .20 * np.sin(np.pi * u) + .12 * u, .09 * np.cos(a) * u], 1)
                curves.append(leaf)
            heads.append(stem[-1])
        g = .55 + .45 * smooth(self.bloom, self.bloom + 1.0, t)
        return [segments(curves, "#a8c993", .006, .26 * g),
            dict(pos=np.array(heads), size=.045 if self.variant == "reed" else .085,
                 color=lin("#f7c775"), alpha=.34 * g, kind="spark", twinkle=.18)]


class Flowers:
    """Native petal geometry that opens in a wave from a meaningful light event."""

    def __init__(self, at=(0, 0, 0), count=24, radius=1.4, height=.42,
                 variant="lotus", seed=9, bloom=11.3):
        if variant not in ("lotus","star"):
            raise ValueError("Flowers variant must be lotus or star")
        self.at = np.asarray(at, float)
        rng = np.random.default_rng(seed)
        self.base = self.at + np.c_[rng.uniform(-radius, radius, count),
            np.zeros(count), rng.uniform(-radius * .65, radius * .65, count)]
        self.h = height * rng.uniform(.6, 1.15, count)
        self.angle = rng.uniform(0, 2 * np.pi, count)
        self.phase = rng.random(count)
        self.bloom = bloom + .13 * np.linalg.norm(self.base[:, [0, 2]], axis=1) + .3 * self.phase
        self.variant = variant

    def sample(self, t):
        stems, petals, cores = [], [], []
        v = np.linspace(0, 1, 10)
        for p, h, angle, phase, born in zip(self.base, self.h, self.angle, self.phase, self.bloom):
            wind = .035 * np.sin(t * .9 + phase * 8)
            stem = p + np.stack([wind * v ** 2, h * v, .025 * np.sin(t + angle) * v ** 2], 1)
            stems.append(stem)
            head = stem[-1]
            opening = .08 + .92 * smooth(born, born + 1.1, t)
            n = 6 if self.variant == "lotus" else 8
            for j in range(n):
                a = angle + j * 2 * np.pi / n
                r = .18 * np.sin(np.pi * v) * opening
                y = .10 * np.sin(np.pi * v) + .13 * (1 - opening) * v
                petal = head + np.stack([r * np.cos(a), y, r * np.sin(a)], 1)
                petals.append(petal)
            cores.append(head)
        opened = float(smooth(float(np.min(self.bloom)), float(np.max(self.bloom)) + 1, t))
        return [segments(stems, "#a1c58a", .006, .28),
            segments(petals, "#f48cb9" if self.variant == "lotus" else "#f4c2dd", .0065, .12 + .53 * opened),
            dict(pos=np.asarray(cores), size=.034, color=lin("#ffe4a5"), alpha=.34, kind="spark")]


class Willow:
    """A branching canopy with drooping leaf chains; all strands inhabit 3D space."""

    def __init__(self, at=(0, 0, 0), height=4.6, spread=3.1, variant="willow",
                 seed=31, bloom=12.4):
        if variant not in ("willow","blossom"):
            raise ValueError("Willow variant must be willow or blossom")
        self.at = np.asarray(at, float)
        self.height, self.spread, self.variant = height, spread, variant
        self.bloom, self.seed = bloom, seed
        rng = np.random.default_rng(seed)
        self.branches = []
        self.tips = []
        self.phases = rng.uniform(0, 2 * np.pi, 18)
        for j in range(18):
            a = j * 2 * np.pi / 18 + rng.uniform(-.15, .15)
            r = spread * rng.uniform(.62, 1)
            h = height * rng.uniform(.64, .96)
            u = np.linspace(0, 1, 30)
            p = self.at + np.stack([r * np.sin(a) * u ** 1.3,
                .38 * height + (h - .38 * height) * np.sin(u * np.pi / 2),
                r * np.cos(a) * u ** 1.3], 1)
            self.branches.append(p)
            self.tips.append(p[-1])
        self.tips = np.asarray(self.tips)

    def sample(self, t):
        trunk_u = np.linspace(0, 1, 45)
        curves = []
        for side in (-1, 0, 1):
            trunk = self.at + np.stack([.12 * np.sin(trunk_u * 3) + side * .045 * (1-trunk_u),
                trunk_u * self.height * .6, .10 * np.sin(trunk_u * 4)], 1)
            curves.append(trunk)
        branches, leaves, petals = [], [], []
        u = np.linspace(0, 1, 34)
        for j, (branch, tip, phase) in enumerate(zip(self.branches, self.tips, self.phases)):
            wind = .08 * np.sin(.55 * t + phase)
            q = branch.copy()
            q[:, 0] += wind * np.linspace(0, 1, len(q)) ** 2
            curves.append(q)
            for k in range(3):
                off = np.array([.14 * np.sin(phase + k), -.04 * k, .14 * np.cos(phase + k)])
                droop=(.35+.1*(j%3)) if self.variant=="willow" else (.10+.04*(j%3))
                p = tip + off + np.stack([wind + .14 * np.sin(2 * u + t * .7 + phase) * u,
                    -u * self.height * droop, .16 * u * np.sin(phase)], 1)
                branches.append(p)
                leaves.extend(p[3::2])
                if j % 3 == 0:
                    petals.extend(p[8::8])
        g = .22 + .78 * smooth(self.bloom, self.bloom + 1.7, t)
        pp = np.asarray(petals)
        return [segments(curves, "#dbb57e", .014, .23),
                segments(branches, "#b7ca8f", .005, .22 * g),
                dict(pos=np.asarray(leaves), size=.055 if self.variant=="willow" else .095,
                     color=lin("#d6dca8" if self.variant=="willow" else "#efa1c4"), alpha=.28*g, kind="petal", rot=.4),
                dict(pos=pp, size=.075, color=lin("#f290bd"), alpha=.55*smooth(self.bloom,self.bloom+1.2,t),
                     kind="petal", rot=t*.13, twinkle=.15)]


class Lantern:
    """Geometric hanging lantern, floating cup or teardrop with an inner light."""

    def __init__(self, at=(0, 1, 0), size=.3, variant="hanging", seed=1, lit=0):
        if variant not in ("hanging","cup"):
            raise ValueError("Lantern variant must be hanging or cup")
        self.at, self.size, self.variant, self.seed, self.lit = np.asarray(at,float), size, variant, seed, lit

    def sample(self, t):
        s = self.size
        c = self.at + np.array([.025*np.sin(t*.7+self.seed), .015*np.sin(t*.9+self.seed),0])
        u = np.linspace(0,2*np.pi,25)
        top_u=.6 if self.variant=="cup" else 1.0
        top_r=s*(.42+.3*np.sin(top_u*np.pi))
        top_y=s*(-.4+1.05*top_u)
        curves = [ring(c,s*.65,height=-s*.4),ring(c,top_r,height=top_y)]
        for a in np.arange(8)*np.pi/4:
            v=np.linspace(0,1,16)
            if self.variant=="cup":
                v=v*.6
            r=s*(.42+.3*np.sin(v*np.pi))
            curves.append(c+np.stack([r*np.cos(a),s*(-.4+1.05*v),r*np.sin(a)],1))
        if self.variant=="hanging":
            curves.append(np.array([c+[0,s*.65,0],c+[0,s*1.8,0]]))
        g=.2+.8*smooth(self.lit,self.lit+.8,t)
        return [segments(curves,"#f1c581",.006,.4*g),dict(pos=c[None],size=s*.45,color=lin("#ffd491"),
            alpha=.55*g,emit=1.3,kind="soft"),dict(pos=c[None],size=s*1.5,color=lin("#e3a45a"),alpha=.035*g)]


BUILDERS = {"seat": Seat, "path": Path, "reeds": Reeds, "flowers": Flowers,
            "willow": Willow, "lantern": Lantern}


def build_model(family, **parameters):
    """Named reusable entry point. Unknown families fail rather than silently substitute."""
    return BUILDERS[family](**parameters)
