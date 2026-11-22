"""Deterministic three dimensional celestial models for the ten-film suite."""
from __future__ import annotations

import numpy as np

from p3d.api import lin, ribbon, show
from p3d.brand import Globe
from tools.concert_kit.models import segments, smooth


def ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def sphere(n):
    i = np.arange(n, dtype=float) + .5
    y = 1 - 2 * i / n
    a = i * np.pi * (3 - np.sqrt(5))
    r = np.sqrt(1 - y * y)
    return np.stack([r * np.cos(a), y, r * np.sin(a)], 1)


class TimedSet:
    """Fade geometry as a unit, without changing its physical motion clock."""
    def __init__(self, item, appear=0, vanish=99, fade=.5):
        self.item, self.appear, self.vanish, self.fade = item, appear, vanish, fade
        self.wants_camera = getattr(item, "wants_camera", False)
        self.static = getattr(item, "static", False)

    def gain(self, t):
        if not self.static:
            return 1.0
        return smooth(self.appear, self.appear + self.fade, t) * (
            1 - smooth(self.vanish - self.fade, self.vanish, t))

    def sample(self, t, cam=None):
        if self.static:
            return self.item.sample(t, cam) if self.wants_camera else self.item.sample(t)
        if t < self.appear or t > self.vanish:
            return None
        a = smooth(self.appear, self.appear + self.fade, t)
        a *= 1 - smooth(self.vanish - self.fade, self.vanish, t)
        batches = self.item.sample(t, cam) if self.wants_camera else self.item.sample(t)
        if batches is None:
            return None
        if isinstance(batches, dict):
            batches = [batches]
        return [dict(b, alpha=np.asarray(b.get("alpha", 1)) * a) for b in batches]


class ContinentGlobe(Globe):
    """The inherited real land geometry lights gradually from the African interior."""
    def sample(self, t, cam=None):
        batches = super().sample(t, cam)
        if not batches:
            return batches
        c, matrix, radius = self._view(t, cam)
        earth_matrix = matrix @ self.turn(t)
        # The native Globe orders ocean, lit land, sparks, halo, cloud and air.
        # Change only the illuminated land batch, keeping all inherited geometry.
        land = batches[1]
        p = (np.asarray(land["pos"]) - c) @ earth_matrix / radius
        lat = np.degrees(np.arcsin(np.clip(p[:, 1], -1, 1)))
        lon = np.degrees(np.arctan2(p[:, 0], p[:, 2]))
        africa = (lat > -36) & (lat < 37) & (lon > -19) & (lon < 52)
        red_sea_coast = np.interp(lat, [12, 18, 22, 31], [43, 39, 36, 32])
        africa &= ~((lat > 12) & (lon > red_sea_coast))
        distance = np.sqrt(((lat - 1.3) / 34) ** 2 + ((lon - 24) / 39) ** 2)
        reveal = smooth(.08, .7, t / 8 - distance * .24)
        glow = .22 + africa * (.25 + 1.05 * reveal)
        texture = .7 + .3 * np.sin(p[:, 0] * 83 + p[:, 1] * 41 + p[:, 2] * 57) ** 2
        land["alpha"] = np.asarray(land["alpha"]) * glow * texture
        return batches


class ThresholdGlow:
    """A bright world-space cloud bridges the orbital shot into the arrival."""
    wants_camera = True

    def __init__(self):
        rng = np.random.default_rng(7381)
        self.uv = rng.normal(0, 1, (650, 2))
        self.seed = rng.random(650)

    def sample(self, t, cam):
        strength = np.exp(-((t - 9) / .24) ** 2)
        if strength < .004:
            return None
        r, u, f = cam.basis()
        c = np.asarray(cam.pos) + f * 2.4
        p = c + self.uv[:, :1] * r * 1.9 + self.uv[:, 1:] * u * 1.2
        return dict(pos=p, size=.27, alpha=strength * .15,
                    color=lin("#ffdf9d"), emit=1.5, fog=0, dof=0,
                    reflect=False, streak=0, kind="soft")


class Constellations:
    """Sparse foreground depth markers, orbiting trails and moving stardust."""
    def __init__(self, center=(0, 7, -8), seed=19, n=1600, radius=24):
        self.c = np.asarray(center)
        rng = np.random.default_rng(seed)
        self.p = rng.normal(size=(n, 3))
        self.p /= np.maximum(np.linalg.norm(self.p, axis=1)[:, None], 1e-6)
        self.p *= rng.uniform(radius * .65, radius * 1.5, n)[:, None]
        self.phase = rng.uniform(0, 6.28, n)
        self.s = rng.uniform(.009, .028, n)
        self.colors = np.array([lin(c) for c in ("#cab3ff", "#a2ddf2", "#ffdba1")])

    def sample(self, t):
        p = self.p @ ry(t * .008).T + self.c
        p[:, 1] += .12 * np.sin(t * .5 + self.phase)
        return dict(pos=p, size=self.s, alpha=.2 + .15 * np.sin(self.phase + t * .36) ** 2,
                    color=self.colors[np.arange(len(p)) % 3], kind="spark", twinkle=.3,
                    fog=0, reflect=False, dof=.45, emit=1.25)


class Colonnade:
    """Layered native stone-light arcades with visible parallax and floor inlay."""
    static = True

    def __init__(self):
        curves = []
        a = np.linspace(0, 2 * np.pi, 56)
        for z in (-3, -7, -11):
            for x in (-6.2, 6.2):
                for h, rad in ((.1, .36), (.22, .3), (4.3, .25), (4.45, .38)):
                    curves.append(np.stack([x + rad * np.cos(a),
                                           np.full(len(a), h), z + rad * np.sin(a)], 1))
                for th in np.linspace(0, 2 * np.pi, 10, endpoint=False):
                    curves.append(np.array([[x + .17 * np.cos(th), .25, z + .17 * np.sin(th)],
                                            [x + .17 * np.cos(th), 4.3, z + .17 * np.sin(th)]]))
            for off in (0, .12, .25):
                aa = np.linspace(0, np.pi, 100)
                curves.append(np.stack([(6.2 + off) * np.cos(aa),
                    4.45 + (2.3 + off) * np.sin(aa), np.full(len(aa), z)], 1))
        for k in range(5):
            rr = 2.6 + k * .23
            aa = np.linspace(0, 2 * np.pi, 240)
            curves.append(np.stack([rr * np.cos(aa), np.full(len(aa), .014),
                                   -1.8 + rr * np.sin(aa)], 1))
        self.curves = curves
        rng = np.random.default_rng(61)
        self.dots = np.stack([rng.uniform(-4.2, 4.2, 7000), np.full(7000, .008),
                             rng.uniform(-18, 4, 7000)], 1)

    def sample(self, t):
        return [segments(self.curves, "#b5bdda", .012, .24),
                dict(pos=self.dots, size=.016, color=lin("#b9a1eb"), alpha=.09, twinkle=.12)]


class GatheringLight:
    """Grounded streams connect the arrivals, then rise in a restrained canopy."""
    def sample(self, t):
        if t < 9:
            return None
        u = np.linspace(0, 1, 150)
        out = []
        palette = ("#efae6a", "#db85c2", "#88cdd6", "#bca2ed", "#b6d988")
        for i, col in enumerate(palette):
            angle = i * 2 * np.pi / 5 + t * .035
            g = smooth(11.0 + .4 * i, 16.1 + .2 * i, t)
            rad = 4.6 * (1 - u)
            y = .025 + np.sin(np.pi * u) * (1.6 + 2.3 * smooth(15, 19, t))
            p = np.stack([rad * np.cos(angle), y,
                          -1.9 + rad * np.sin(angle)], 1)
            out.append(ribbon(p, width=.028, alpha=.28 * g, color=lin(col),
                              pulse=(2.1, .6, 1.3, 3.2), twinkle=.08, emit=1.3))
        return out


class Orrery:
    """Precessing engraved armillary rings and individually turning worlds."""
    wants_camera = True
    def __init__(self, center=(0, 7.1, -8)):
        self.c = np.asarray(center, float)
        self.a = np.linspace(0, 2 * np.pi, 420)
        self.v = sphere(2800)
        self.sun = sphere(7800)
        self.radii = (3.1, 4.55, 6.05, 7.6, 9.15)
        self.palette = ("#e7bb6c", "#89dded", "#c4a4ee", "#eda6b8", "#9bc7f0")

    def orient(self, i, t):
        return ry(.2 * i + t * (.018 + i * .006)) @ rz(.27 + .25 * i) @ rx(.35 + i * .33)

    def point(self, i, t):
        a = t * (.22 - .024 * i) + i * 1.53
        return np.array([self.radii[i] * np.cos(a), 0, self.radii[i] * np.sin(a)]) @ self.orient(i, t).T + self.c

    def sample(self, t, cam=None):
        out = []
        # A textured three dimensional star, with latitude-dependent flames.
        rot = ry(t * .11)
        sv = self.sun @ rot.T
        phase = 9 * sv[:, 0] + 6 * sv[:, 1] + t * 1.1
        r = 1.18 + .025 * np.sin(phase)
        view = np.asarray(cam.pos) - self.c if cam is not None else np.array([0, 0, 20])
        front = sv @ view > 0
        toward = np.clip(sv[front] @ (view / np.linalg.norm(view)), 0, 1)
        skin = (.22 + .78 * np.sqrt(toward)) * (.76 + .24 * np.sin(phase[front]) ** 2)
        out.append(dict(pos=self.c + sv[front] * r[front, None], normal=sv[front],
            size=.067, color=show("#f8c98a") * skin[:, None],
            alpha=1.4, kind="disc", paint=1, paint_light=.09,
            emit=.75, twinkle=.025, rim=(.04, 3)))
        # Fine longitudinal solar tracery reads as a form, rather than a glare blob.
        curves = []
        for k in range(16):
            a = self.a
            lon = k * np.pi / 8 + .055 * t
            p = np.stack([1.28 * np.sin(a) * np.cos(lon), 1.28 * np.cos(a),
                          1.28 * np.sin(a) * np.sin(lon)], 1)
            curves.append(p + self.c)
        out.append(segments(curves, "#fff0be", .007, .16))
        for i, (rad, hexcol) in enumerate(zip(self.radii, self.palette)):
            matrix = self.orient(i, t)
            local = np.stack([rad * np.cos(self.a), np.zeros(len(self.a)), rad * np.sin(self.a)], 1)
            # An eight-sided physical ring catches different amounts of light on
            # each face. The fine engraved rails remain visible along its edges.
            tube_angle = np.linspace(0, 2 * np.pi, 8, endpoint=False)
            tube_radius = .045 + .006 * i
            tube = np.stack([
                (rad + tube_radius * np.cos(tube_angle)[None, :]) * np.cos(self.a)[:, None],
                np.broadcast_to(tube_radius * np.sin(tube_angle), (len(self.a), 8)),
                (rad + tube_radius * np.cos(tube_angle)[None, :]) * np.sin(self.a)[:, None],
            ], -1).reshape(-1, 3)
            tone = np.broadcast_to(.40 + .25 * (1 + np.sin(tube_angle)), (len(self.a), 8)).ravel()
            out.append(dict(pos=tube @ matrix.T + self.c, size=.046,
                color=show(hexcol) * tone[:, None], alpha=.7,
                kind="soft", paint=.42, paint_light=.6, dof=.5, emit=.9))
            for delta in (-.055, 0, .055):
                p = local * ((rad + delta) / rad)
                p = p @ matrix.T + self.c
                out.append(ribbon(p, width=.018 if delta else .027, color=lin(hexcol),
                    alpha=.23 if delta else .38, emit=1.12,
                    pulse=(.42 + .13 * i, .7, 1.8, 8 + i), twinkle=.05))
            # Tick marks rotate with each armillary circle, including depth.
            a = np.linspace(0, 2 * np.pi, 120, endpoint=False)
            unit = np.stack([np.cos(a), np.zeros(len(a)), np.sin(a)], 1)
            aa = unit * (rad - .10)
            bb = unit * (rad + np.where(np.arange(len(a)) % 5 == 0, .22, .10))[:, None]
            out.append(dict(pos=aa @ matrix.T + self.c, pos2=bb @ matrix.T + self.c,
                size=.009, color=lin(hexcol), alpha=.32, kind="line"))
            # An orbiting planet with stable surface banding and one-axis rotation.
            pos = self.point(i, t)
            pr = (.43, .53, .67, .51, .81)[i]
            vec = self.v @ (ry(t * (.25 - i * .03)) @ rz(i * .26)).T
            bands = .54 + .46 * np.sin(self.v[:, 1] * (16 + i * 3) + .7 * np.sin(self.v[:, 0] * 8)) ** 2
            lighting = .07 + .93 * np.clip(-np.sum(vec * (pos - self.c) / rad, axis=1), 0, 1)
            look = np.asarray(cam.pos) - pos if cam is not None else np.array([0, 0, 20])
            front = vec @ look > 0
            out.append(dict(pos=pos + vec[front] * pr, normal=vec[front],
                size=.072 * pr / .55, alpha=1.4,
                color=show(hexcol)[None] * (bands[front] * lighting[front])[:, None],
                kind="disc", rim=(.02, 3), twinkle=.015, emit=.75,
                paint=1, paint_light=.045))
            if i == 4:
                for r in np.linspace(1.05, 1.55, 8):
                    p = np.stack([r * np.cos(self.a), np.zeros(len(self.a)),
                                  r * np.sin(self.a)], 1) @ (rz(.38) @ rx(.23)).T + pos
                    out.append(ribbon(p, width=.018, color=lin("#dfd4ba"), alpha=.2))
            # A cometlike wake reveals the planet's direction and speed.
            ages = np.linspace(2.8, 0, 100)
            trail = np.asarray([self.point(i, t - age) for age in ages])
            out.append(ribbon(trail, width=.035, color=lin(hexcol),
                alpha=np.linspace(0, .35, len(trail)), emit=1.3, twinkle=.07))
        return out


class Observatory:
    """A monumental elliptical instrument stand under the working mechanism."""
    static = True

    def __init__(self):
        curves = []
        a = np.linspace(0, 2 * np.pi, 360)
        for rad, y in ((10.6, .03), (10.85, .06), (11.1, .12), (9.8, .03), (2.7, .3), (2.9, .33)):
            curves.append(np.stack([rad * np.cos(a), np.full(len(a), y),
                                   -8 + rad * np.sin(a)], 1))
        for i in range(36):
            th = i * np.pi / 18
            curves.append(np.stack([np.array([3.1, 9.7]) * np.cos(th), [.02, .02],
                                   -8 + np.array([3.1, 9.7]) * np.sin(th)], 1))
        u = np.linspace(0, 1, 100)
        for th in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            r = 3.2 * (1 - u) ** 1.2 + .12
            curves.append(np.stack([r * np.cos(th), .3 + 4.7 * u,
                                   -8 + r * np.sin(th)], 1))
        self.curves = curves
        rng = np.random.default_rng(1591)
        ang = rng.uniform(0, 2 * np.pi, 14000)
        r = np.sqrt(rng.random(len(ang))) * 10.65
        self.floor = np.stack([r * np.cos(ang), np.full(len(ang), .01), -8 + r * np.sin(ang)], 1)

    def sample(self, t):
        return [segments(self.curves, "#9499c5", .018, .27),
                dict(pos=self.floor, color=lin("#7e7ebc"), size=.025,
                     alpha=.12, twinkle=.06)]
