"""Original procedural wildlife and flowers, awaiting owner visual approval.

The public classes are native p3d point sets. Positions are metres, Y is up,
and every pose is a pure function of absolute time. No simulation history,
image asset, downloaded mesh, or random per-frame jitter is used.
"""
from __future__ import annotations

import numpy as np

from .geometry import ellipsoid, feather, lines, rx, ry, rz, smooth, surface, transform_batches, unit, wind


def _ellipsoid_batch(center, radii, count, color, size, alpha, rotation=None):
    p, n = ellipsoid(center, radii, count, rotation)
    return surface(p, color, size, alpha, n)


class Dove:
    """Articulated light dove with authored launch, glide, landing and foot locks.

    ``at`` and ``land_at`` are the centre of the two foot contacts, not the
    centre of the body. ``launch`` and ``land`` are absolute seconds. This is
    a stylized anatomical prototype, not a biomechanical flight simulation.
    """
    static = False

    def __init__(self, at=(-1.1, .9, .25), land_at=(1.35, 1.02, -1.2),
                 launch=.8, land=4.9, scale=1.4, seed=9, color="#f5efde"):
        if land <= launch + 1:
            raise ValueError("A dove flight needs more than one second between launch and landing.")
        if scale <= 0:
            raise ValueError("Scale must be positive.")
        self.at = np.asarray(at, float)
        self.land_at = np.asarray(land_at, float)
        self.launch, self.land, self.scale = float(launch), float(land), float(scale)
        self.seed, self.color = int(seed), color
        self.control = np.stack([self.at, self.at + [.20, 2.15, -.30],
                                 self.land_at + [-.45, 1.45, .38], self.land_at])
        self.phase = float(np.random.default_rng(seed).uniform(-.05, .05))
        self.body = [
            _ellipsoid_batch((0, .145, -.015), (.064, .078, .170), 1700, color, .007, .13),
            _ellipsoid_batch((0, .219, .133), (.028, .061, .035), 350, color, .0055, .12,
                             rx(.55)),
            _ellipsoid_batch((0, .269, .200), (.034, .037, .039), 420, color, .0055, .18),
            _ellipsoid_batch((0, .258, .251), (.009, .007, .026), 150, "#c5a878", .0045, .22,
                             rx(-.10)),
        ]
        self.body[0]["rim"] = (.25, 2)
        self.body[1]["rim"] = (.15, 2)

    def _path(self, t):
        u = float(smooth(self.launch, self.land, t))
        a, b, c, d = self.control
        p = (1-u)**3*a + 3*(1-u)**2*u*b + 3*(1-u)*u*u*c + u**3*d
        tangent = 3*(1-u)**2*(b-a) + 6*(1-u)*u*(c-b) + 3*u*u*(d-c)
        return p, tangent, u

    def _state(self, t):
        t = float(t)
        p, tangent, u = self._path(t)
        air = float(smooth(self.launch-.16, self.launch+.12, t) *
                    (1-smooth(self.land-.06, self.land+.52, t)))
        crouch = float(smooth(self.launch-.48, self.launch-.17, t) *
                       (1-smooth(self.launch-.17, self.launch+.05, t)))
        settle = float(smooth(self.land-.04, self.land+.10, t) *
                       (1-smooth(self.land+.10, self.land+.54, t)))
        yaw = np.arctan2(tangent[0], tangent[2])
        takeoff = float(smooth(self.launch-.18, self.launch+.18, t) *
                        (1-smooth(self.launch+.65, self.launch+1.2, t)))
        landing = float(smooth(self.land-.75, self.land-.24, t) *
                        (1-smooth(self.land+.03, self.land+.30, t)))
        pitch = -.22*takeoff - .19*landing
        bank = -.10*np.sin(np.pi*u)*air
        rotation = ry(yaw) @ rz(bank) @ rx(pitch)
        p = p.copy()
        p[1] -= self.scale*(.027*crouch + .012*settle)
        # Wing frequency slows into the glide, then opens into the landing flare.
        phase = 2*np.pi*(2.8*(t-self.launch) - .16*(t-self.launch)**2 + self.phase)
        glide = float(smooth(self.launch+1.45, self.launch+1.75, t) *
                      (1-smooth(self.land-1.25, self.land-.82, t)))
        flap = (.58*np.sin(phase) * (1-.88*glide) + .20*landing) * air
        return dict(root=p, rotation=rotation, yaw=float(yaw), air=air, flap=flap,
                    phase=phase, glide=glide, landing=landing, progress=u)

    def _wing(self, side, state):
        opened, flap, phase = state["air"], state["flap"], state["phase"]
        shoulder = np.array([side*.064, .176, .014])
        # Closed wings lie down the flanks. Leaving their feather planes
        # horizontal would make the resting bird look like separate floating plates.
        folded_roll = -1.25*(1-opened)
        upper = rz(side*(flap+folded_roll))
        lower = rz(side*(flap+folded_roll-.11*opened*np.sin(phase-.45)))
        # Folding rotates two fixed-length bones. It never scales the arm to
        # make a smaller silhouette, which would stretch the wing during launch.
        elbow = shoulder + upper @ ry(side*1.34*(1-opened)) @ [side*.145, 0, 0]
        wrist = elbow + lower @ ry(-side*1.40*(1-opened)) @ [side*.150, 0, 0]
        patches, normals, curves = [], [], []
        # The feather-bearing wing surface joins shoulder, elbow and wrist. Its
        # leading edge is continuous, so outer feathers never float off the body.
        for start, end, rotation in ((shoulder, elbow, upper), (elbow, wrist, lower)):
            u = np.linspace(0, 1, 15)
            v = np.linspace(0, 1, 9)
            edge = start*(1-u[:, None]) + end*u[:, None]
            back = rotation @ [0, 0, -.090-.025*opened]
            patch = edge[:, None, :] + v[None, :, None]*back
            patch += (np.sin(np.pi*u)[:, None]*np.sin(np.pi*v)[None, :])[:, :, None]*(rotation @ [0, .010, 0])
            patches.append(patch.reshape(-1, 3))
            normals.append(np.broadcast_to(rotation @ [0, 1, 0], (patch.size//3, 3)))
            curves.append(edge)
        # Short inner feathers cover the upper arm.
        for v in np.linspace(.05, .95, 4):
            root = shoulder*(1-v) + elbow*v
            tip = root + upper @ [side*(.009+.024*opened), -.006, -.102-.040*v]
            p, n, outlines = feather(root, tip, .010+.004*opened,
                                      normal=upper @ [0, 1, 0])
            patches.append(p); normals.append(n); curves.extend(outlines)
        # Secondaries attach to the forearm, between elbow and wrist.
        for v in np.linspace(.05, .95, 8):
            root = elbow*(1-v) + wrist*v
            tip = root + lower @ [side*.012*opened, -.006, -.140+.025*v]
            p, n, outlines = feather(root, tip, .010+.005*opened,
                                      normal=lower @ [0, 1, 0])
            patches.append(p); normals.append(n); curves.extend(outlines)
        # Each primary has its own root and direction within the articulated hand fan.
        wrist_rotation = lower @ ry(side*(-.20*opened*np.sin(phase-.7)))
        inner_points = sum(len(p) for p in patches)
        inner_segments = sum(len(c)-1 for c in curves)
        for v in np.linspace(0, 1, 10):
            angle = .22 + 1.0*v
            root = wrist + wrist_rotation @ [side*.034*v*opened, 0, -.018*v]
            tip = root + wrist_rotation @ [side*(.018+.160*opened*np.sin(angle)),
                                             -.005, -.19*(1-.58*opened*np.sin(angle))]
            p, n, outlines = feather(root, tip, .009+.005*opened,
                                      normal=wrist_rotation @ [0, 1, 0])
            patches.append(p); normals.append(n); curves.extend(outlines)
        points = np.concatenate(patches)
        opacity = np.concatenate([np.full(inner_points, .042), np.full(len(points)-inner_points, .075)])
        edge = lines(curves, "#eee2c6", .0032, .065)
        edge["alpha"] = np.concatenate([np.full(inner_segments, .032),
                                        np.full(len(edge["pos"])-inner_segments, .065)])
        batches = [surface(points, self.color, .0058, opacity,
                           np.concatenate(normals), rim=(.12, 2)), edge]
        return batches, {"shoulder": shoulder, "elbow": elbow, "wrist": wrist}

    def _feet(self, t, state):
        p, rot = state["root"], state["rotation"]
        feet = []
        for side in (-1, 1):
            _, start_tangent, _ = self._path(self.launch)
            _, end_tangent, _ = self._path(self.land)
            start_foot = self.at + ry(np.arctan2(start_tangent[0], start_tangent[2])) @ [side*.031*self.scale, 0, .01*self.scale]
            end_foot = self.land_at + ry(np.arctan2(end_tangent[0], end_tangent[2])) @ [side*.031*self.scale, 0, .01*self.scale]
            if t <= self.launch:
                foot = start_foot
            elif t >= self.land:
                foot = end_foot
            else:
                tuck = float(smooth(self.launch+.08, self.launch+.48, t) *
                             (1-smooth(self.land-.58, self.land-.12, t)))
                local = np.array([side*.031, .075*tuck, .01-.065*tuck])
                foot = p + rot @ (local*self.scale)
                release = float(smooth(self.launch, self.launch+.14, t))
                contact = float(smooth(self.land-.14, self.land, t))
                foot = (1-release)*start_foot + release*foot
                foot = (1-contact)*foot + contact*end_foot
            feet.append(foot)
        return feet

    def anchors(self, t):
        state = self._state(t)
        p, rot = state["root"], state["rotation"]
        feet = self._feet(t, state)
        joints = {}
        for side, label in ((-1, "left"), (1, "right")):
            _, wing = self._wing(side, state)
            joints[label] = {name: (p + rot @ (value*self.scale)).tolist()
                             for name, value in wing.items()}
        return {"root": p.tolist(), "feet": [q.tolist() for q in feet], "wings": joints,
                "stage": "perched" if t <= self.launch else "settled" if t >= self.land else "flying"}

    def sample(self, t):
        state = self._state(t)
        out = [self.body[0]]
        # The head reaches forward in flight and makes one small anticipatory look.
        head_shift = np.array([0, -.020, .040])*state["air"]
        head_turn = .16*float(smooth(self.launch-.75, self.launch-.50, t)*
                              (1-smooth(self.launch-.35, self.launch-.10, t)))
        pivot = np.array([0, .206, .133])
        turn = ry(head_turn)
        for batch in self.body[1:]:
            moved = dict(batch)
            moved["pos"] = (batch["pos"]-pivot) @ turn.T + pivot + head_shift
            moved["normal"] = batch["normal"] @ turn.T
            out.append(moved)
        for side in (-1, 1):
            wing, _ = self._wing(side, state)
            out.extend(wing)
        patches, normals, curves = [], [], []
        tail_open = .32 + .68*max(state["landing"], state["air"]*.25)
        for v in np.linspace(-1, 1, 9):
            root = [v*.025, .133, -.108]
            tip = [v*(.047+.060*tail_open), .11+.018*state["landing"], -.325+.025*abs(v)]
            p, n, contour = feather(root, tip, .010)
            patches.append(p); normals.append(n); curves.extend(contour)
        out.extend([surface(np.concatenate(patches), "#d8d8d1", .0058, .050, np.concatenate(normals)),
                    lines(curves, "#e9ddc5", .003, .045)])
        # Small painted eye points supply a readable anatomical landmark without
        # turning the eyes into glowing flares or a separate raster texture.
        eyes = (np.array([[-.029, .276, .216], [.029, .276, .216]])-pivot) @ turn.T+pivot+head_shift
        out.append(surface(eyes, "#211b16", .008, .90, paint=1.0, paint_light=0.0))
        out = transform_batches(out, state["root"], state["rotation"], self.scale)
        feet = self._feet(t, state)
        legs = []
        for side, foot in zip((-1, 1), feet):
            hip = state["root"] + state["rotation"] @ (np.array([side*.030, .10, -.015])*self.scale)
            knee = .52*hip+.48*foot + state["rotation"] @ [0, 0, -.014*self.scale]
            legs.append(np.stack([hip, knee, foot]))
            for angle in (-.38, .05, .42):
                toe = foot + ry(state["yaw"]+angle) @ [0, 0, .040*self.scale]
                legs.append(np.stack([foot, toe]))
        out.append(lines(legs, "#bfa887", .004*self.scale, .25))
        return out


class Rose:
    """Layered three-dimensional rose with attached petals and rooted wind.

    Variants change original petal palettes. They do not claim cultivar accuracy.
    ``bloom_at`` is the start of an authored three-second opening.
    """
    static = False
    COLORS = {"blush": ("#ee729a", "#ffc0b9"), "crimson": ("#cf4768", "#f18496"),
              "golden": ("#edbe67", "#ffe2ab")}

    def __init__(self, at=(0, 0, 0), height=.9, radius=.15, variant="blush", seed=2,
                 bloom_at=.9, wind_strength=.5):
        if variant not in self.COLORS:
            raise ValueError(f"Unknown rose variant: {variant}")
        self.at, self.height, self.radius = np.asarray(at, float), float(height), float(radius)
        self.variant, self.seed, self.bloom_at = variant, int(seed), float(bloom_at)
        self.wind_strength = float(wind_strength)
        rng = np.random.default_rng(seed)
        self.petals = [(layer, k, count, float(rng.uniform(-.12, .12)))
                       for layer, count in enumerate((5, 7, 9, 11)) for k in range(count)]

    def _bend(self, t, h):
        h = np.asarray(h)
        a = wind(t, self.at[0], self.at[2], self.wind_strength)
        b = wind(t-.6, self.at[0]+.7, self.at[2], self.wind_strength*.5)
        return np.stack([a*(h/self.height)**2, h, b*(h/self.height)**2], axis=-1)

    def anchors(self, t):
        return {"root": self.at.tolist(), "flower": (self.at+self._bend(t, self.height)).tolist()}

    def sample(self, t):
        h = np.linspace(0, self.height, 35)
        stem = self.at + self._bend(t, h)
        head = stem[-1]
        out = [lines([stem], "#b6bb7d", .008, .35)]
        leaf_points, leaf_normals, leaf_lines = [], [], []
        for k in range(4):
            root_h = self.height*(.27+.14*k)
            root = self.at+self._bend(t, root_h)
            direction = ry(k*2.4+self.seed*.1) @ [.16, .055, 0]
            p, n, contour = feather(root, root+direction, .035, normal=(0, 1, 0), samples=17)
            leaf_points.append(p); leaf_normals.append(n); leaf_lines.extend(contour)
        out.extend([surface(np.concatenate(leaf_points), "#88ab7f", .0055, .19, np.concatenate(leaf_normals)),
                    lines(leaf_lines, "#b7c79b", .0028, .23)])
        opened = float(smooth(self.bloom_at, self.bloom_at+3, t))
        inner, edge = self.COLORS[self.variant]
        patches, normals, contours = [], [], []
        # Avoid duplicating an entire row at the zero-width petal root. The
        # first row sits just above the attachment, with a valid surface normal.
        u = np.linspace(.025, 1, 18)
        v = np.linspace(-1, 1, 11)
        for layer, k, count, jitter in self.petals:
            angle = 2*np.pi*k/count + layer*2.39996 + jitter
            # The inner whorl stays upright while the older outer petals curl
            # outwards. A shared flat fan would read as a generic daisy.
            openness = .12 + opened*(.38+.17*layer)
            radial = self.radius*(.10+.12*layer)
            petal_height = self.radius*(1.25-.12*layer)
            bend = openness*(.25+.20*layer)
            along = radial + petal_height*(.15*u+.85*u*u)*bend
            height = petal_height*(u-(.10+.24*layer)*openness*u*u)
            width = self.radius*(.18+.10*layer)*np.sin(np.pi*u*.93)**.58
            x = np.broadcast_to(along[:, None], (len(u), len(v)))
            z = width[:, None]*v[None, :]
            y = height[:, None] + self.radius*.12*(v*v)[None, :]*u[:, None]
            patch = np.stack([x, y, z], -1)
            rotation = ry(angle)
            patch = patch @ rotation.T + head
            du, dv = np.gradient(patch, axis=(0, 1))
            normal = unit(np.cross(du, dv))
            contour = np.concatenate([patch[:, 0], patch[-1, 1:], patch[::-1, -1], patch[0, -2::-1]])
            patches.append(patch.reshape(-1, 3)); normals.append(normal.reshape(-1, 3)); contours.append(contour)
        out.extend([surface(np.concatenate(patches), inner, .0055, .14, np.concatenate(normals)),
                    lines(contours, edge, .0034, .21)])
        return out


class Wheat:
    """Rooted wheat clump with paired spikelets, awns, and coherent wind.

    Each grain is a world-space ellipsoid. The two palette variants are a
    stylized ripe or green study, not a specific agricultural cultivar.
    """
    static = False

    def __init__(self, at=(0, 0, 0), count=11, radius=.25, height=1.0,
                 variant="ripe", seed=6, wind_strength=1.0):
        if variant not in ("ripe", "green"):
            raise ValueError(f"Unknown wheat variant: {variant}")
        self.at, self.count, self.variant = np.asarray(at, float), int(count), variant
        self.wind_strength = float(wind_strength)
        rng = np.random.default_rng(seed)
        a = rng.uniform(0, 2*np.pi, count)
        r = radius*np.sqrt(rng.uniform(0, 1, count))
        self.roots = self.at + np.stack([r*np.cos(a), np.zeros(count), r*np.sin(a)], 1)
        self.heights = height*rng.uniform(.78, 1.16, count)
        self.rotations = rng.uniform(0, 2*np.pi, count)
        self.grain_p, self.grain_n = ellipsoid((0, 0, 0), (.013, .023, .012), 45)

    def _stem(self, t, root, height, u):
        u = np.asarray(u)
        a = wind(t, root[0], root[2], self.wind_strength)
        b = wind(t-.7, root[0]+1.5, root[2], self.wind_strength*.45)
        return root + np.stack([a*u*u, height*u, b*u*u], -1)

    def anchors(self, t):
        return {"roots": self.roots.tolist(), "heads": [self._stem(t, r, h, 1).tolist()
                                                         for r, h in zip(self.roots, self.heights)]}

    def sample(self, t):
        curves, grains, normals = [], [], []
        color, contour = ("#ceab69", "#f0d190") if self.variant=="ripe" else ("#88aa6f", "#c3d593")
        for root, height, yaw in zip(self.roots, self.heights, self.rotations):
            stem = self._stem(t, root, height, np.linspace(0, 1.16, 34))
            curves.append(stem)
            for k in range(8):
                h = .91+.030*k
                base = self._stem(t, root, height, h)
                for side in (-1, 1):
                    rotation = ry(yaw) @ rz(-side*.48)
                    center = base + ry(yaw) @ [side*.016, .007, 0]
                    grains.append(self.grain_p @ rotation.T + center)
                    normals.append(self.grain_n @ rotation.T)
                    tip = center + rotation @ [0, .023, 0]
                    awn = tip + ry(yaw) @ [side*.020, .065+.010*(7-k), 0]
                    curves.append(np.stack([tip, .6*tip+.4*awn+[0, .004, 0], awn]))
            for k in range(2):
                base = self._stem(t, root, height, .43+.24*k)
                tip = base + ry(yaw+k*2.6) @ [.13, .075, 0]
                curves.append(np.stack([base, .5*base+.5*tip+[0, .035, 0], tip]))
        return [surface(np.concatenate(grains), color, .0075, .24, np.concatenate(normals)),
                lines(curves, contour, .0034, .28)]


def build_model(family, **parameters):
    """Public constructor lookup for the three documented prototype families."""
    constructors = {"dove": Dove, "rose": Rose, "wheat": Wheat}
    try:
        cls = constructors[family]
    except KeyError as exc:
        raise ValueError(f"Unknown add-on family: {family}") from exc
    return cls(**parameters)
