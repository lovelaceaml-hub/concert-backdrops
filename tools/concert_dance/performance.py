"""Captured whole-body dancing with continuous placement and measured support.

The original body asset and engine stay unchanged. Install this before sampling
a Body. The phrase is CMU 05_02, already retargeted in body_v1.npz; its 30 Hz
source poses are evaluated at the requested time, without a procedural dance
replacement. Foot support is an estimate from the capture, not a force solver.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from p3d import bodymath as bm
from p3d import motion


@dataclass(frozen=True)
class Support:
    """One immutable source-clock support interval and its chosen sole point."""

    side: int
    start: float
    end: float
    point: str
    anchor: tuple[float, float, float]
    source_horizontal_span: float


def _runs(mask):
    edges = np.diff(np.r_[False, mask, False].astype(np.int8))
    return zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1))


class DancePerformance:
    """One actor's captured phrase, preparation, support and closing settle.

    start is the scene time at which the captured phrase begins. clip_start and
    clip_end explicitly select source seconds, allowing reuse without pretending
    that a non-looping phrase is a seamless cycle. rate stays near real time.
    A 0.24 s acceleration/deceleration envelope adds 0.24 s to the phrase, so
    incoming and outgoing source speed both reach zero without a held last foot.
    """

    def __init__(self, actor, *, start=2.0, rate=1.0, clip_start=0.0,
                 clip_end=None, prepare_seconds=2.0, settle_seconds=2.5,
                 ease_seconds=0.24, max_foot_correction=0.075):
        self.actor = actor
        self.rig = actor.rig
        self.clip = actor.mo.clips["dance"]
        self.capture_start = float(start)
        self.rate = float(rate)
        self.clip_start = float(clip_start)
        self.clip_end = self.clip.T if clip_end is None else float(clip_end)
        self.prepare_seconds = float(prepare_seconds)
        self.settle_seconds = float(settle_seconds)
        self.ease_seconds = float(ease_seconds)
        self.max_foot_correction = float(max_foot_correction) * self.rig.height / 1.7
        values = (self.capture_start, self.rate, self.clip_start, self.clip_end,
                  self.prepare_seconds, self.settle_seconds, self.ease_seconds,
                  self.max_foot_correction)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Performance parameters must be finite")
        if not 0.75 <= self.rate <= 1.25:
            raise ValueError("Use a near-real-time capture rate between 0.75 and 1.25")
        if not 0 <= self.clip_start < self.clip_end <= self.clip.T:
            raise ValueError("Source selection must be inside the non-looping dance clip")
        if min(self.prepare_seconds, self.settle_seconds, self.ease_seconds,
               self.max_foot_correction) <= 0:
            raise ValueError("Preparation, settle, easing and correction bound must be positive")
        self.duration = (self.clip_end - self.clip_start) / self.rate + self.ease_seconds
        if self.ease_seconds * 2 >= self.duration:
            raise ValueError("Source phrase is too short for this clock envelope")
        self.capture_end = self.capture_start + self.duration
        self.prepare_start = self.capture_start - self.prepare_seconds
        self.settle_end = self.capture_end + self.settle_seconds
        self._start_xz = actor.mo.clip_pose("dance", self.clip_start).pos[[0, 2]].copy()
        self._sole = self._sole_points()
        self._foot_vectors = self._foot_vertices()
        self.supports = self._build_supports()
        # Each support event belongs to one immutable source time and body
        # placement. Compute its inverse clock and world point once, rather
        # than repeating 45 bisection steps for every planted-foot sample.
        self._support_scene_starts = {s: self.scene_time(s.start) for s in self.supports}
        self._support_world_anchors = {s: self._make_world_anchor(s) for s in self.supports}
        self._first = self._endpoint(self.capture_start)
        self._last = self._endpoint(self.capture_end)
        self._standing_in = self._standing(self._first, self.prepare_start)
        self._standing_out = self._standing(self._last, self.settle_end)

    def source_time(self, t):
        """C1 source clock: short eased edges with real-time motion between."""
        e = float(np.clip(float(t) - self.capture_start, 0.0, self.duration))
        edge = self.ease_seconds
        if e < edge:
            u = e / edge
            delta = self.rate * edge * (u**3 - 0.5 * u**4)
        elif e > self.duration - edge:
            u = (self.duration - e) / edge
            delta = self.clip_end - self.clip_start - self.rate * edge * (u**3 - 0.5 * u**4)
        else:
            delta = self.rate * (e - 0.5 * edge)
        return float(np.clip(self.clip_start + delta, self.clip_start, self.clip_end))

    def scene_time(self, source_time):
        """Deterministic inverse of the monotone source clock."""
        source_time = float(np.clip(source_time, self.clip_start, self.clip_end))
        lo, hi = self.capture_start, self.capture_end
        for _ in range(45):
            mid = (lo + hi) * 0.5
            if self.source_time(mid) < source_time:
                lo = mid
            else:
                hi = mid
        return (lo + hi) * 0.5

    def _capture_pose(self, source_time):
        p = self.actor.mo.clip_pose("dance", source_time)
        p.pos[[0, 2]] -= self._start_xz
        return p

    def _sole_points(self):
        out = []
        for side in ("L", "R"):
            foot = self.rig.idx["foot." + side]
            vv = self.rig.verts0[self.rig.vert_bone == foot].astype(np.float64)
            sole = vv[vv[:, 1] <= np.quantile(vv[:, 1], 0.20)]
            heel = sole[sole[:, 2] <= np.quantile(sole[:, 2], 0.25)].mean(axis=0)
            toe = sole[sole[:, 2] >= np.quantile(sole[:, 2], 0.75)].mean(axis=0)
            out.append({"heel": heel, "toe": toe})
        return out

    def _foot_vertices(self):
        return [self.rig.verts0[self.rig.vert_bone == self.rig.idx["foot." + side]].astype(np.float64)
                - self.rig.head[self.rig.idx["foot." + side]] for side in ("L", "R")]

    def _build_supports(self):
        """Build canonical intervals once; there is no moving look-back window.

        The old contact confidence alone accepts some travelling feet. Here a
        candidate must also be low, slow and remain within an 8 cm horizontal
        region. Heel/toe choice uses measured height and speed. Foot orientation
        is never frozen, so a supported heel or toe can remain a natural pivot.
        """
        count = max(2, int(math.ceil((self.clip_end - self.clip_start) * self.clip.fps)) + 1)
        ts = np.linspace(self.clip_start, self.clip_end, count)
        points = np.empty((count, 2, 2, 3))
        confidence = np.empty((count, 2))
        for k, t in enumerate(ts):
            p = self._capture_pose(t)
            D, P, _ = self.actor.mo.local_fk(p)
            confidence[k] = p.contact
            for side, sd in enumerate(("L", "R")):
                f = self.rig.idx["foot." + sd]
                for key, name in enumerate(("heel", "toe")):
                    points[k, side, key] = P[f] + bm.qrot(D[f], self._sole[side][name] - self.rig.head[f])
        speed = np.linalg.norm(np.gradient(points[..., [0, 2]], ts, axis=0), axis=-1)
        scale = self.rig.height / 1.7
        score = points[..., 1] + 0.08 * speed
        chosen = np.argmin(score, axis=2)
        supports = []
        dt = ts[1] - ts[0]
        for side in range(2):
            for key, name in enumerate(("heel", "toe")):
                eligible = ((chosen[:, side] == key) & (confidence[:, side] >= 0.5)
                            & (points[:, side, key, 1] <= 0.105 * scale)
                            & (speed[:, side, key] <= 0.24 * scale))
                # Bridge only a single isolated classification sample between
                # two matching samples; all decisions stay in the source clock.
                if len(eligible) > 2:
                    eligible[1:-1] |= eligible[:-2] & eligible[2:]
                for a, b in _runs(eligible):
                    if b - a < 4:
                        continue
                    cloud = points[a:b, side, key]
                    anchor = np.median(cloud[:min(4, len(cloud))], axis=0)
                    spread = float(np.linalg.norm(cloud[:, [0, 2]] - anchor[[0, 2]], axis=1).max())
                    if spread > 0.08 * scale:
                        continue
                    supports.append(Support(side, float(ts[a]), float(min(self.clip_end, ts[b-1] + dt)),
                                            name, tuple(float(x) for x in anchor), spread))
        return tuple(sorted(supports, key=lambda s: (s.side, s.start)))

    def _support(self, source_time, side):
        for support in self.supports:
            if support.side == side and support.start <= source_time <= support.end:
                return support
        return None

    def _support_weight(self, source_time, support):
        if support is None:
            return 0.0
        edge = min(0.12, (support.end - support.start) * 0.3)
        arrival = 1.0 if support.start <= self.clip_start + 1e-6 else float(bm.smoother((source_time - support.start) / edge))
        release = 1.0 if support.end >= self.clip_end - 1e-6 else float(bm.smoother((support.end - source_time) / edge))
        raw = float(self.clip.sample(source_time)[3][support.side])
        return arrival * release * float(bm.smooth(raw))

    def contact(self, t):
        if not self.capture_start <= t <= self.capture_end:
            return np.zeros(2)
        source = self.source_time(t)
        return np.array([self._support_weight(source, self._support(source, side)) for side in range(2)])

    def stance_start(self, t, side):
        support = self._support(self.source_time(t), side)
        return float(t) if support is None else self._support_scene_starts[support]

    def _make_world_anchor(self, support):
        t = self._support_scene_starts[support]
        q = bm.qy(np.radians(self.actor.heading(t)))
        origin = self.actor.base(t)
        anchor = origin + bm.qrot(q, support.anchor)
        anchor[1] = origin[1]
        return anchor

    def _world_anchor(self, support):
        return self._support_world_anchors[support].copy()

    def lock_feet(self, t, p, joints, rotations, origin, heading_q, heading, lift):
        """Bounded IK to a sole anchor, retaining the captured foot rotation."""
        if not self.capture_start <= t <= self.capture_end:
            return False
        source = self.source_time(t)
        inverse = bm.qconj(heading_q)
        changed = False
        for side, sd in enumerate(("L", "R")):
            support = self._support(source, side)
            weight = self._support_weight(source, support)
            if weight <= 1e-6:
                continue
            f = self.rig.idx["foot." + sd]
            D = bm.qmul(rotations[f], self.rig.C[f])
            offset = bm.qrot(D, self._sole[side][support.point] - self.rig.head[f])
            current_ankle = joints[f] + np.array([0.0, lift, 0.0])
            wanted = self._world_anchor(support) - offset
            # Keep the entire rigid foot above the floor while allowing its
            # selected heel/toe to rise as the captured roll changes.
            min_sole = float(bm.qrot(D, self._foot_vectors[side])[:, 1].min())
            wanted[1] = max(wanted[1], origin[1] - min_sole)
            delta = wanted - current_ankle
            length = float(np.linalg.norm(delta))
            if length > self.max_foot_correction:
                delta *= self.max_foot_correction / length
            target_world = current_ankle + weight * delta
            target = bm.qrot(inverse, target_world - origin - np.array([0.0, lift, 0.0]))
            ankle = bm.qrot(inverse, joints[f] - origin)
            hip = bm.qrot(inverse, joints[self.rig.idx["upperleg01." + sd]] - origin)
            knee = bm.qrot(inverse, joints[self.rig.idx["lowerleg01." + sd]] - origin)
            pole = knee - 0.5 * (hip + ankle)
            foot_q = bm.qmul(inverse, rotations[f])
            self.actor.mo.leg_to(p, sd, target, knee=pole if np.linalg.norm(pole) > 1e-5 else None, foot=foot_q)
            changed = True
        return changed

    def _endpoint(self, t):
        p = self._capture_pose(self.source_time(t))
        origin = self.actor.base(t)
        hd = np.radians(self.actor.heading(t))
        qh = bm.qy(hd)
        root = origin + bm.qrot(qh, self.rig.neutral_pos[0] + p.pos)
        _, joints, rotations = self.rig.fk(p.q, root, bm.qmul(qh, p.rot))
        self.lock_feet(t, p, joints, rotations, origin, qh, hd, 0.0)
        p.contact = None
        return p

    def _standing(self, endpoint, t):
        p = self.actor.mo.m_stand(t, seed=self.actor.seed, calm=0.45)
        p.pos[[0, 2]] = endpoint.pos[[0, 2]]
        forward = bm.qrot(endpoint.rot, [0.0, 0.0, 1.0])
        p.rot = bm.qy(np.arctan2(forward[0], forward[2]))
        p.contact = None
        return p

    def pose(self, t):
        t = float(t)
        if t < self.capture_start:
            u = float(np.clip((t - self.prepare_start) / self.prepare_seconds, 0.0, 1.0))
            if u <= 0:
                return self._standing_in.copy()
            # The engine blend may return an input pose at a rounded endpoint.
            # Copy both inputs so a near-boundary seek cannot mutate the recipe.
            p = self.actor.mo._step_between(self._standing_in.copy(), self._first.copy(), u, "L", arc=0.035)
            p.contact = None
            return p
        if t <= self.capture_end:
            p = self._capture_pose(self.source_time(t))
            p.contact = self.contact(t)
            return p
        u = float(np.clip((t - self.capture_end) / self.settle_seconds, 0.0, 1.0))
        if u >= 1:
            return self._standing_out.copy()
        p = self.actor.mo._step_between(self._last.copy(), self._standing_out.copy(), u, "L", arc=0.035)
        p.contact = None
        return p

    def diagnostics(self, t):
        """Actual solved skeleton and support residuals for composition and QA."""
        frame = self.actor.frame(float(t), life=False)
        source = self.source_time(t)
        feet = {}
        for side, sd in enumerate(("L", "R")):
            support = self._support(source, side) if self.capture_start <= t <= self.capture_end else None
            f = self.rig.idx["foot." + sd]
            mode = support.point if support else "heel"
            point = frame["P"][f] + bm.qrot(frame["D"][f], self._sole[side][mode] - self.rig.head[f])
            anchor = self._world_anchor(support) if support else None
            feet[sd] = {"mode": mode if support else "free", "weight": self._support_weight(source, support),
                        "point": point.tolist(), "anchor": None if anchor is None else anchor.tolist(),
                        "source_interval": None if support is None else [support.start, support.end],
                        "horizontal_residual_m": None if anchor is None else float(np.linalg.norm((point-anchor)[[0, 2]])),
                        "minimum_sole_y": float((frame["P"][f] + bm.qrot(frame["D"][f], self._foot_vectors[side]))[:, 1].min())}
        return {"time": float(t), "source_time": source, "phase": "prepare" if t < self.capture_start else "capture" if t <= self.capture_end else "settle" if t < self.settle_end else "hold",
                "pelvis": frame["P"][self.rig.idx["root"]].tolist(), "feet": feet}

    def contact_report(self, times):
        rows = [self.diagnostics(float(t)) for t in times]
        residuals = [f["horizontal_residual_m"] for row in rows for f in row["feet"].values()
                     if f["weight"] >= 0.95 and f["horizontal_residual_m"] is not None]
        return {"source": "CMU 05_02 from committed body_v1.npz", "source_fps": self.clip.fps,
                "capture_start": self.capture_start, "capture_end": self.capture_end,
                "settle_end": self.settle_end, "rate": self.rate,
                "max_correction_m": self.max_foot_correction,
                "support_intervals": [s.__dict__ for s in self.supports],
                "max_supported_horizontal_residual_m": max(residuals, default=None), "samples": rows,
                "limitation": "Kinematic support estimate with bounded IK, not balance or force simulation; pivots retain captured orientation."}


def install_dance(body, **kwargs):
    """Install an instance-local performance before Body/cloth samples exist.

    A bare Actor is also accepted for fast skeleton-only verification. Normal
    Body.where(), Body.joint() and Body.sample() interfaces remain unchanged.
    """
    actor = getattr(body, "actor", body)
    if getattr(actor, "concert_dance_performance", None) is not None:
        raise RuntimeError("A dance performance is already installed on this actor")
    if getattr(actor, "_cache", None):
        raise RuntimeError("Install dance before sampling the actor or cloth")
    performance = DancePerformance(actor, **kwargs)
    actor.base_pose = performance.pose
    actor.contact = performance.contact
    actor._stance_start = performance.stance_start
    actor._lock_feet = performance.lock_feet
    # The inherited cache keys use microseconds. Evaluate at that same time,
    # rather than letting the first of two nearby requests choose its contents.
    # This is an instance-local correction; approved engine actors stay intact.
    original_frame = actor.frame

    def canonical_frame(t, lock=True, gest=True, life=True):
        return original_frame(round(float(t), 6), lock=lock, gest=gest, life=life)

    actor.frame = canonical_frame
    actor.concert_dance_performance = performance
    actor._cache.clear()
    for name in ("_sk", "_pts", "_anchors"):
        value = getattr(body, name, None)
        if value is not None:
            value.clear()
    return performance

