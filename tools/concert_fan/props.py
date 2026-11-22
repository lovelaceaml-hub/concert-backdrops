"""Held open fans and finite silk sheets for the original fan trio study.

The fan follows the final solved palm, including grounding and wrist rotation.
The sheet is a small, fixed-step position based cloth simulation. It has gravity,
air drag, structural/shear/bend constraints, a pinned leading edge, body capsule
proxies and floor contact. It is an art-directed cloth approximation, not a
validated aerodynamic simulation. Cloth self collision, garment collision and
collisions with other performers are not implemented here.

Install the performance before constructing this object. Call ``prebake()`` in
the coordinator before starting frame workers. Numeric caches are identified by
source, parameters and the actual sampled final hand/collider motion. No frame
depends on which other render frames were requested first.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

import numpy as np

from p3d.api import lin
from p3d.cloth import Colliders


BAKE_VERSION = 1


def _unit(a, fallback=(0.0, 1.0, 0.0)):
    a = np.asarray(a, np.float64)
    length = float(np.linalg.norm(a))
    return a / length if length > 1e-9 else np.asarray(fallback, np.float64)


def _readonly(a, dtype=np.float32):
    a = np.asarray(a, dtype=dtype)
    a.flags.writeable = False
    return a


def _segments(points, color, width, alpha):
    return dict(pos=np.asarray(points[:-1], np.float32),
                pos2=np.asarray(points[1:], np.float32), kind="line",
                size=width, alpha=alpha, color=color, emit=0.65,
                twinkle=0.0, fog=True, dof=True)


class FanSilk:
    """One held fan and broad silk sheet in metres, with random-time sampling.

    ``side`` names the held palm. ``fan_roll`` turns the fan in its own plane;
    ``fan_tilt`` tilts it relative to the palm. Both are fixed grip offsets in
    degrees, never a second animation path. ``point_count`` changes rendering
    density only. The 29 by 11 simulation lattice has 319 nodes by default.

    ``cache_dir`` is optional. The cache is a numeric NPZ containing immutable
    60 Hz cloth positions and a JSON metadata string, read with allow_pickle=False.
    A changed motion, geometry, simulation setting or module source invalidates it.
    """

    def __init__(self, body, side="R", duration=20.0, color="#df76bb",
                 cache_dir=None, *, radius=0.34, spread=150.0, length=1.45,
                 rows=29, cols=11, ribs=13, seed=31, point_count=6800,
                 fan_roll=0.0, fan_tilt=0.0, wind=(0.18, 0.04, 0.10),
                 gravity=9.81, drag=1.5, normal_drag=9.0, iterations=7, dt=1.0 / 120.0,
                 sample_hz=60, floor=0.012, preroll=1.25, alpha=0.175,
                 rim_color="#f0c98e", collide=True):
        if side not in ("R", "L"):
            raise ValueError("FanSilk side must be R or L")
        if duration <= 0 or rows < 5 or cols < 5 or length <= 0 or radius <= 0:
            raise ValueError("FanSilk needs positive dimensions and at least a 5 by 5 lattice")
        if not 20 <= spread < 179 or sample_hz <= 0 or iterations < 1 or preroll < 0:
            raise ValueError("Invalid fan spread, sample rate or solver iterations")
        stride = int(round(1.0 / (dt * sample_hz)))
        if stride < 1 or abs(stride * dt * sample_hz - 1.0) > 1e-8:
            raise ValueError("The simulation rate must be an integer multiple of sample_hz")
        self.body, self.side = body, side
        self.duration, self.radius, self.length = float(duration), float(radius), float(length)
        self.rows, self.cols, self.ribs = int(rows), int(cols), max(3, int(ribs))
        self.seed, self.point_count = int(seed), int(point_count)
        self.spread = np.radians(float(spread))
        self.fan_roll, self.fan_tilt = np.radians([fan_roll, fan_tilt])
        self.wind = np.asarray(wind, np.float64)
        self.gravity, self.drag = float(gravity), float(drag)
        self.normal_drag = float(normal_drag)
        self.iterations, self.dt, self.sample_hz = int(iterations), float(dt), int(sample_hz)
        self.stride, self.floor, self.preroll = stride, float(floor), float(preroll)
        self.alpha, self.color, self.rim_color = float(alpha), lin(color), lin(rim_color)
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.collide = bool(collide)
        self._snaps = None
        self._motion = None
        self._metadata = None
        self._cache_hit = False
        self._bake_seconds = 0.0
        self._col = Colliders(body.rig) if collide and hasattr(body, "rig") else None
        self._make_lattice()
        self._make_surface_samples()
        self._params = dict(version=BAKE_VERSION, side=side, duration=self.duration,
                            radius=radius, spread=spread, length=length, rows=rows,
                            cols=cols, seed=seed, fan_roll=fan_roll, fan_tilt=fan_tilt,
                            wind=list(wind), gravity=gravity, drag=drag, normal_drag=normal_drag,
                            iterations=iterations, dt=dt, sample_hz=sample_hz,
                            floor=floor, preroll=preroll, collide=bool(self._col))

    def _make_lattice(self):
        u = np.linspace(0.0, 1.0, self.rows)[:, None]
        v = np.linspace(0.0, 1.0, self.cols)[None, :]
        theta = (v - 0.5) * self.spread
        # Each column has a slightly different cut length. This is a real finite
        # sheet, whose free edge is neither rectangular nor an infinite trail.
        cut = 0.94 + 0.045 * np.cos(2.0 * np.pi * v) + 0.025 * np.cos(6.0 * np.pi * v + 0.5)
        x = self.radius * np.sin(theta) * (1.0 + 0.12 * u)
        y = self.radius * np.cos(theta) + self.length * u * cut
        z = 0.020 * np.sin(v * 6.0 * np.pi) * np.sin(np.pi * u * 0.5)
        self.rest = np.stack(np.broadcast_arrays(x, y, z), axis=-1).reshape(-1, 3)
        self.n = len(self.rest)
        grid = np.arange(self.n).reshape(self.rows, self.cols)
        self.pin_idx = grid[0]
        self.free = np.ones(self.n, bool)
        self.free[self.pin_idx] = False
        self._constraints = []

        def group(a, b, strength):
            a, b = np.asarray(a).ravel(), np.asarray(b).ravel()
            wa, wb = self.free[a].astype(float), self.free[b].astype(float)
            total = wa + wb
            keep = total > 0
            a, b, wa, wb, total = a[keep], b[keep], wa[keep], wb[keep], total[keep]
            lengths = np.linalg.norm(self.rest[b] - self.rest[a], axis=1)
            self._constraints.append((a, b, lengths, (wa / total)[:, None],
                                      (wb / total)[:, None], strength))

        for parity in range(2):
            r = np.arange(parity, self.rows - 1, 2)
            c = np.arange(parity, self.cols - 1, 2)
            group(grid[r], grid[r + 1], 1.0)
            group(grid[:, c], grid[:, c + 1], 1.0)
            group(grid[r, :-1], grid[r + 1, 1:], 0.82)
            group(grid[r, 1:], grid[r + 1, :-1], 0.82)
        # Gentle bending resistance keeps folds broad without turning the silk
        # into a stiff panel. Nonoverlapping batches make updates deterministic.
        for phase in range(4):
            r = np.arange(phase, self.rows - 2, 4)
            c = np.arange(phase, self.cols - 2, 4)
            group(grid[r], grid[r + 2], 0.065)
            group(grid[:, c], grid[:, c + 2], 0.065)
        down = np.linalg.norm(np.diff(self.rest.reshape(self.rows, self.cols, 3), axis=0), axis=-1)
        self._tether_length = np.concatenate([np.zeros((1, self.cols)), np.cumsum(down, axis=0)]).ravel() * 1.025
        self._tether_anchor = np.tile(self.pin_idx, self.rows)
        self._struct_a = np.concatenate([g[0] for g in self._constraints if g[-1] == 1.0])
        self._struct_b = np.concatenate([g[1] for g in self._constraints if g[-1] == 1.0])
        self._struct_l = np.concatenate([g[2] for g in self._constraints if g[-1] == 1.0])

    def _make_surface_samples(self):
        rng = np.random.default_rng(self.seed)
        n = max(300, self.point_count)
        # Stable material coordinates. No per-frame random point changes.
        cells = (np.arange(n) + rng.random(n)) / n * ((self.rows - 1) * (self.cols - 1))
        cell = cells.astype(int)
        self._sr, self._sc = cell // (self.cols - 1), cell % (self.cols - 1)
        self._su, self._sv = rng.random(n), rng.random(n)
        self._u = (self._sr + self._su) / (self.rows - 1)
        self._v = (self._sc + self._sv) / (self.cols - 1)
        self._grain = rng.uniform(0.82, 1.18, n)
        leaf_n = 1050
        self._leaf_r = self.radius * np.sqrt(rng.uniform(0.06, 1.0, leaf_n))
        self._leaf_theta = rng.uniform(-0.5, 0.5, leaf_n) * self.spread
        self._leaf_grain = rng.uniform(0.8, 1.2, leaf_n)

    def hand_frame(self, t):
        """Final world grip, fan width axis, outward axis and fan normal."""
        p, normal = self.body.where(float(t), "palm." + self.side, normal=True)
        normal = _unit(normal, (0, 0, 1))
        actor = getattr(self.body, "actor", None)
        if actor is not None and hasattr(actor, "palm"):
            forward = actor.palm(float(t), self.side)[2]
            if hasattr(self.body, "_wdir"):
                forward = self.body._wdir(forward, float(t))
        else:
            forward = self.body.where(float(t), "fingertips." + self.side) - p
        forward = _unit(forward - normal * np.dot(forward, normal))
        across = _unit(np.cross(forward, normal), (1, 0, 0))
        normal = _unit(np.cross(across, forward), (0, 0, 1))
        # The grip point stays in the palm. Tilt and roll rotate geometry about it.
        pivot = np.asarray(p, np.float64) + forward * 0.018 + normal * 0.006
        tilted = forward * np.cos(self.fan_tilt) + normal * np.sin(self.fan_tilt)
        normal = _unit(np.cross(across, tilted), (0, 0, 1))
        outward = tilted * np.cos(self.fan_roll) + across * np.sin(self.fan_roll)
        across = across * np.cos(self.fan_roll) - tilted * np.sin(self.fan_roll)
        return pivot, across, outward, normal

    def _pins_from_frame(self, frame):
        p, across, outward, normal = frame
        r = self.rest[self.pin_idx]
        return p + r[:, :1] * across + r[:, 1:2] * outward + r[:, 2:3] * normal

    def _motion_tracks(self):
        count = int(np.ceil(self.duration * self.sample_hz)) + 1
        frames = np.empty((count, 4, 3), np.float64)
        pins = np.empty((count, self.cols, 3), np.float64)
        nc = len(self._col.groups) if self._col is not None else 0
        ca, cb = np.empty((count, nc, 3)), np.empty((count, nc, 3))
        for k in range(count):
            t = min(k / self.sample_hz, self.duration)
            frame = self.hand_frame(t)
            frames[k], pins[k] = frame, self._pins_from_frame(frame)
            if self._col is not None:
                a, b = self._col.at(self.body.actor.frame(t)["M"])
                ca[k] = self.body._w(a, t) if hasattr(self.body, "_w") else a
                cb[k] = self.body._w(b, t) if hasattr(self.body, "_w") else b
        self._motion = dict(frames=frames, pins=pins, ca=ca, cb=cb)
        return self._motion

    def _identity(self, tracks):
        source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        motion_hash = hashlib.sha256()
        for key in ("frames", "pins", "ca", "cb"):
            motion_hash.update(np.asarray(tracks[key], dtype="<f8").tobytes())
        if self._col is not None:
            scale = abs(float(getattr(self.body, "scale", 1.0)))
            motion_hash.update(np.asarray([self._col.ra * scale, self._col.rb * scale], dtype="<f8").tobytes())
        params = json.dumps(self._params, sort_keys=True, separators=(",", ":"))
        identity = hashlib.sha256((source_hash + motion_hash.hexdigest() + params).encode()).hexdigest()
        return dict(identity=identity, source_sha256=source_hash,
                    motion_sha256=motion_hash.hexdigest(), parameters=self._params,
                    limitations=["no cloth self collision", "no other performer collision",
                                 "body capsules do not model the costume surface",
                                 "art-directed position based dynamics, not measured silk"])

    def prebake(self):
        """Load or compute all cloth samples once; return this object."""
        if self._snaps is not None:
            return self
        started = time.perf_counter()
        tracks = self._motion_tracks()
        meta = self._identity(tracks)
        path = self.cache_dir / ("fan-silk-" + meta["identity"] + ".npz") if self.cache_dir else None
        expected = (len(tracks["pins"]), self.n, 3)
        if path is not None and path.exists():
            try:
                with np.load(path, allow_pickle=False) as data:
                    cached_meta = json.loads(str(data["metadata"].item()))
                    snaps = data["positions"]
                    if cached_meta["identity"] != meta["identity"] or snaps.shape != expected or not np.isfinite(snaps).all():
                        raise ValueError("Invalid fan silk cache")
                    self._snaps = _readonly(snaps)
                    self._cache_hit = True
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                self._snaps = None
        if self._snaps is None:
            self._snaps = _readonly(self._simulate(tracks))
            if path is not None:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(dir=self.cache_dir, prefix=".fan-silk-", suffix=".npz", delete=False) as f:
                    temporary = Path(f.name)
                    try:
                        np.savez_compressed(f, positions=self._snaps, metadata=json.dumps(meta, sort_keys=True))
                        f.flush()
                        os.fsync(f.fileno())
                        os.replace(temporary, path)
                    finally:
                        temporary.unlink(missing_ok=True)
        self._metadata = meta
        self._bake_seconds = time.perf_counter() - started
        return self

    def _collisions(self, x, ca, cb):
        touched = self.free & (x[:, 1] < self.floor)
        x[touched, 1] = self.floor
        if not len(ca):
            return touched
        scale = abs(float(getattr(self.body, "scale", 1.0)))
        r0 = self._col.ra * scale + 0.009
        r1 = self._col.rb * scale + 0.009
        ab = cb - ca
        den = np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-12)
        rel = x[:, None] - ca[None]
        u = np.clip(np.einsum("nkj,kj->nk", rel, ab) / den[None], 0.0, 1.0)
        diff = rel - u[..., None] * ab[None]
        dist = np.linalg.norm(diff, axis=-1)
        depth = r0[None] + (r1 - r0)[None] * u - dist
        best = depth.argmax(axis=1)
        indices = np.arange(self.n)
        penetration = depth[indices, best]
        hit = self.free & (penetration > 0)
        if np.any(hit):
            j = indices[hit]
            direction = diff[j, best[hit]] / np.maximum(dist[j, best[hit]], 1e-8)[:, None]
            # Deterministic fallback for an exactly centred particle.
            zero = np.linalg.norm(direction, axis=1) < 1e-6
            direction[zero] = (0.0, 0.0, 1.0)
            x[j] += direction * penetration[hit, None]
        return touched | hit

    def _simulate(self, tr):
        p, across, outward, normal = tr["frames"][0]
        x = p + self.rest[:, :1] * across + self.rest[:, 1:2] * outward + self.rest[:, 2:3] * normal
        x = np.asarray(x, np.float64)
        previous = x.copy()
        count = len(tr["pins"])
        snapshots = np.empty((count, self.n, 3), np.float32)
        pre = max(1, int(round(self.preroll / self.dt)))
        steps = (count - 1) * self.stride
        for step in range(-pre + 1, steps + 1):
            q = max(0.0, step / self.stride)
            k = min(int(q), count - 2)
            f = min(q - k, 1.0)
            pins = tr["pins"][k] * (1 - f) + tr["pins"][k + 1] * f
            ca = tr["ca"][k] * (1 - f) + tr["ca"][k + 1] * f
            cb = tr["cb"][k] * (1 - f) + tr["cb"][k + 1] * f
            t = step * self.dt
            velocity = (x - previous) / self.dt
            # A small, spatially varying air field. Most movement comes from
            # the fan boundary and inertial lag, not decorative sine offsets.
            air = np.empty_like(x)
            air[:, 0] = self.wind[0] + 0.08 * np.sin(x[:, 2] * 2.1 + t * 0.9 + self.seed)
            air[:, 1] = self.wind[1] + 0.04 * np.sin(x[:, 0] * 2.0 - t * 1.2)
            air[:, 2] = self.wind[2] + 0.09 * np.sin(x[:, 1] * 2.4 + t * 0.7)
            relative_air = air - velocity
            acceleration = relative_air * self.drag
            # A broad surface resists air across its face more than air along
            # its threads. This bounded pressure term lets a banked fan carry
            # a fold before it falls, while keeping gravity and finite edges.
            grid = x.reshape(self.rows, self.cols, 3)
            along = np.empty_like(grid)
            across_grid = np.empty_like(grid)
            along[1:-1] = grid[2:] - grid[:-2]
            along[0], along[-1] = grid[1] - grid[0], grid[-1] - grid[-2]
            across_grid[:, 1:-1] = grid[:, 2:] - grid[:, :-2]
            across_grid[:, 0], across_grid[:, -1] = grid[:, 1] - grid[:, 0], grid[:, -1] - grid[:, -2]
            surface_normal = np.cross(across_grid, along).reshape(-1, 3)
            surface_normal /= np.maximum(np.linalg.norm(surface_normal, axis=1), 1e-9)[:, None]
            flow_normal = np.clip(np.einsum("ij,ij->i", relative_air, surface_normal), -3.0, 3.0)
            acceleration += surface_normal * (self.normal_drag * flow_normal * np.abs(flow_normal))[:, None]
            acceleration[:, 1] -= self.gravity
            xn = x + (x - previous) * 0.998 + acceleration * self.dt ** 2
            xn[self.pin_idx] = pins
            touched = np.zeros(self.n, bool)
            for it in range(self.iterations):
                for a, b, rest, wa, wb, strength in self._constraints:
                    d = xn[b] - xn[a]
                    norm = np.linalg.norm(d, axis=1)
                    correction = d * ((norm - rest) / np.maximum(norm, 1e-9) * strength)[:, None]
                    xn[a] += correction * wa
                    xn[b] -= correction * wb
                origin = xn[self._tether_anchor]
                d = xn - origin
                norm = np.linalg.norm(d, axis=1)
                over = self.free & (norm > self._tether_length)
                xn[over] = origin[over] + d[over] * (self._tether_length[over] / norm[over])[:, None]
                # Contact participates in each solve iteration, so a torso
                # correction is not an isolated final shove stretching the sheet.
                touched |= self._collisions(xn, ca, cb)
                low = self.free & (xn[:, 1] < self.floor)
                xn[low, 1] = self.floor
                touched |= low
                xn[self.pin_idx] = pins
            previous = x.copy()
            previous[touched] += (xn[touched] - previous[touched]) * 0.07
            x = xn
            if step >= 0 and step % self.stride == 0:
                snapshots[step // self.stride] = x
        return snapshots

    def positions(self, t):
        """A fresh rows by cols by 3 array; baked arrays remain immutable."""
        self.prebake()
        t = float(np.clip(t, 0.0, self.duration))
        q = t * self.sample_hz
        k = min(int(q), len(self._snaps) - 2)
        f = min(q - k, 1.0)
        p = self._snaps[k] * (1.0 - f) + self._snaps[k + 1] * f
        # Arbitrary subframe shutters use the exact solved grip too. The other
        # rows retain the saved cloth dynamics; only the attached row is pinned.
        p[self.pin_idx] = self._pins_from_frame(self.hand_frame(t))
        return p.reshape(self.rows, self.cols, 3)

    def _fan_batches(self, t):
        p, across, outward, normal = self.hand_frame(t)
        angle = np.linspace(-self.spread * 0.5, self.spread * 0.5, self.ribs)
        directions = np.sin(angle)[:, None] * across + np.cos(angle)[:, None] * outward
        root = np.broadcast_to(p, (self.ribs, 3)).copy()
        rim = p + self.radius * directions
        leaf = p + self._leaf_r[:, None] * (np.sin(self._leaf_theta)[:, None] * across
                                               + np.cos(self._leaf_theta)[:, None] * outward)
        theta = np.linspace(-self.spread * 0.5, self.spread * 0.5, 65)
        curve = p + self.radius * (np.sin(theta)[:, None] * across + np.cos(theta)[:, None] * outward)
        return [dict(pos=leaf.astype(np.float32), size=0.0105, kind="soft",
                     alpha=0.14 * self._leaf_grain, color=self.color,
                     normal=np.broadcast_to(normal, leaf.shape), emit=0.5,
                     twinkle=0.0, lit=False, fog=True, dof=True),
                dict(pos=root.astype(np.float32), pos2=rim.astype(np.float32),
                     size=0.0027, kind="line", alpha=0.52, color=self.rim_color,
                     emit=0.75, twinkle=0.0, fog=True, dof=True),
                _segments(curve, self.rim_color, 0.0030, 0.42),
                _segments(np.array([p - outward * 0.060, p + outward * 0.045]),
                          self.rim_color, 0.006, 0.55)]

    def sample(self, t):
        """Native p3d batches for the held fan, silk surface, folds and hem."""
        grid = self.positions(t)
        a, b = grid[self._sr, self._sc], grid[self._sr + 1, self._sc]
        c, d = grid[self._sr, self._sc + 1], grid[self._sr + 1, self._sc + 1]
        u, v = self._su[:, None], self._sv[:, None]
        pos = (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v
        along = (b - a) * (1 - v) + (d - c) * v
        across = (c - a) * (1 - u) + (d - b) * u
        normals = np.cross(across, along)
        normals /= np.maximum(np.linalg.norm(normals, axis=1), 1e-9)[:, None]
        # Satin-like modulation follows the actual folded surface normal. A
        # sparse surface, translucent edges and a quiet hem keep the silk airy.
        satin = 0.66 + 0.34 * np.abs(normals @ _unit((0.32, 0.70, 0.64)))
        edge = np.clip(np.minimum(self._v, 1 - self._v) / 0.07, 0.0, 1.0)
        tail = np.clip((1.0 - self._u) / 0.07, 0.0, 1.0)
        density = (0.48 + 0.52 * edge) * (0.45 + 0.55 * tail)
        shade = 0.74 + 0.26 * np.cos(self._u * np.pi * 0.9) ** 2
        color = self.color[None] * shade[:, None]
        sheet = dict(pos=pos.astype(np.float32), normal=normals.astype(np.float32),
                     size=0.021, kind="soft", color=color.astype(np.float32),
                     alpha=(self.alpha * self._grain * satin * density).astype(np.float32),
                     emit=0.45, twinkle=0.0, lit=False, fog=True, dof=True)
        hems = [grid[:, 0], grid[:, -1], grid[-1]]
        batches = self._fan_batches(t) + [sheet]
        for hem in hems:
            batches.append(_segments(hem, self.color * 0.90, 0.0018, 0.095))
        return batches

    def diagnostics(self):
        """Numeric bake evidence. These measurements do not replace viewing it."""
        self.prebake()
        distance = np.linalg.norm(self._snaps[:, self._struct_b] - self._snaps[:, self._struct_a], axis=-1)
        strain = np.abs(distance / self._struct_l[None] - 1.0)
        pin_error = np.linalg.norm(self._snaps[:, self.pin_idx] - self._motion["pins"], axis=-1)
        free_y = self._snaps[:, self.free, 1]
        return dict(identity=self._metadata["identity"], cache_hit=self._cache_hit,
                    bake_seconds=round(self._bake_seconds, 3), simulation_nodes=self.n,
                    saved_samples=len(self._snaps), simulation_hz=round(1 / self.dt),
                    saved_sample_hz=self.sample_hz, surface_points=max(300, self.point_count),
                    fan_leaf_points=len(self._leaf_r), max_pin_error_m=float(pin_error.max()),
                    p99_structural_strain=float(np.percentile(strain, 99)),
                    max_structural_strain=float(strain.max()),
                    floor_penetration_m=float(max(0.0, self.floor - free_y.min())),
                    limitations=self._metadata["limitations"])
