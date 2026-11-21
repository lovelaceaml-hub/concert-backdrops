"""Absolute-time camera tracks. Blender coordinates are metres and Z-up."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .curves import CubicSpline
from .math3d import Vec3, finite_number, length, sub, vec3


@dataclass(frozen=True)
class CameraSample:
    position: Vec3
    target: Vec3
    velocity: Vec3
    acceleration: Vec3
    target_velocity: Vec3
    target_acceleration: Vec3
    roll_radians: float = 0.0


class CameraTrack:
    """An interpolating C2 path with one time warp across the whole shot.

    Natural cubic interpolation may overshoot its waypoints. Review clearance
    against scenery before approving a shot. It does not guarantee constant
    speed, jerk continuity, or collision avoidance.
    """

    def __init__(self, seconds, points, targets, *, easing="smootherstep", roll_degrees=(0.0, 0.0)):
        if easing not in ("linear", "smootherstep"):
            raise ValueError("camera easing must be linear or smootherstep")
        points = tuple(vec3(p, "camera point") for p in points)
        targets = tuple(vec3(p, "camera target") for p in targets)
        if len(targets) == 1:
            targets = targets * len(points)
        if len(targets) != len(points):
            raise ValueError("targets must contain one fixed target or one target per point")
        self.position_curve = CubicSpline(seconds, points)
        self.target_curve = CubicSpline(seconds, targets)
        self.seconds = self.position_curve.seconds
        self.easing = easing
        if not isinstance(roll_degrees, (tuple, list)) or len(roll_degrees) != 2:
            raise ValueError("roll_degrees must contain start and end angles")
        self.roll_degrees = tuple(finite_number(v, "roll_degrees") for v in roll_degrees)

    @classmethod
    def from_dict(cls, spec: dict[str, Any], *, duration_seconds: float | None = None) -> "CameraTrack":
        if not isinstance(spec, dict):
            raise ValueError("camera path must be an object")
        if spec.get("pacing", "waypoints") != "waypoints":
            raise ValueError("CameraTrack supports pacing=waypoints only")
        points = spec.get("points", [])
        seconds = spec.get("seconds")
        if seconds is None:
            if duration_seconds is None or finite_number(duration_seconds, "duration_seconds") <= 0 or len(points) < 2:
                raise ValueError("camera path needs seconds or a positive duration_seconds")
            seconds = [i * duration_seconds / (len(points) - 1) for i in range(len(points))]
        return cls(seconds, points, spec.get("targets", [[0.0, 0.0, 0.0]]), easing=spec.get("easing", "smootherstep"), roll_degrees=spec.get("roll_degrees", [0.0, 0.0]))

    def sample(self, seconds: float) -> CameraSample:
        t = finite_number(seconds, "sample time")
        start, end = self.seconds[0], self.seconds[-1]
        duration = end - start
        u = min(1.0, max(0.0, (t - start) / duration))
        if self.easing == "smootherstep":
            progress = u ** 3 * (10.0 + u * (-15.0 + 6.0 * u))
            speed = 30.0 * u ** 2 * (u - 1.0) ** 2
            acceleration = 60.0 * u * (2.0 * u ** 2 - 3.0 * u + 1.0) / duration
        else:
            progress, speed, acceleration = u, 1.0, 0.0
        if t < start or t > end:
            speed = acceleration = 0.0
        p = self.position_curve.sample(start + duration * progress)
        q = self.target_curve.sample(start + duration * progress)

        def warp(curve):
            return (tuple(v * speed for v in curve.velocity),
                    tuple(a * speed * speed + v * acceleration for a, v in zip(curve.acceleration, curve.velocity)))

        pv, pa = warp(p)
        qv, qa = warp(q)
        if length(sub(q.value, p.value)) < 1e-7:
            raise ValueError("camera position and target coincide at sample time")
        roll = math.radians(self.roll_degrees[0] + progress * (self.roll_degrees[1] - self.roll_degrees[0]))
        return CameraSample(p.value, q.value, pv, pa, qv, qa, roll)

    def diagnostics(self, sample_hz: float = 60.0) -> dict[str, Any]:
        """Numerical motion review; limits belong to each shot's scale and intent."""
        hz = finite_number(sample_hz, "sample_hz")
        if hz <= 0:
            raise ValueError("sample_hz must be positive")
        duration = self.seconds[-1] - self.seconds[0]
        intervals = max(2, math.ceil(duration * hz))
        if intervals > 1_000_000:
            raise ValueError("motion diagnostics are limited to one million intervals")
        dt = duration / intervals
        samples = [self.sample(self.seconds[0] + i * dt) for i in range(intervals + 1)]
        jerk = [length(sub(b.acceleration, a.acceleration)) / dt for a, b in zip(samples, samples[1:])]
        residual = {"position": 0.0, "velocity": 0.0, "acceleration": 0.0}
        epsilon = min(b - a for a, b in zip(self.seconds, self.seconds[1:])) * 1e-7
        for curve in (self.position_curve, self.target_curve):
            for knot in self.seconds[1:-1]:
                left, right = curve.sample(knot - epsilon), curve.sample(knot + epsilon)
                for key, field in (("position", "value"), ("velocity", "velocity"), ("acceleration", "acceleration")):
                    residual[key] = max(residual[key], length(sub(getattr(left, field), getattr(right, field))))
        return {"samples": len(samples), "sample_hz": intervals / duration,
                "peak_speed_m_s": max(length(s.velocity) for s in samples),
                "peak_acceleration_m_s2": max(length(s.acceleration) for s in samples),
                "peak_jerk_m_s3": max(jerk),
                "minimum_target_distance_m": min(length(sub(s.target, s.position)) for s in samples),
                "knot_continuity_residual": residual,
                "endpoint_hold_is_c2": self.easing == "smootherstep",
                "notes": ["Jerk is a finite-difference diagnostic, not a jerk-continuity guarantee.",
                          "Clearance and natural framing still require scene review."]}
