"""Small dependency-free vector operations shared by animation and Blender."""
from __future__ import annotations

import math
from collections.abc import Sequence

Vec3 = tuple[float, float, float]


def finite_number(value, name="value") -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def vec3(value: Sequence[float], name="vector") -> Vec3:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{name} must have three coordinates")
    return tuple(finite_number(v, name) for v in value)


def add(a: Vec3, b: Vec3) -> Vec3:
    return tuple(x + y for x, y in zip(a, b))


def sub(a: Vec3, b: Vec3) -> Vec3:
    return tuple(x - y for x, y in zip(a, b))


def mul(a: Vec3, scalar: float) -> Vec3:
    return tuple(x * scalar for x in a)


def dot(a: Vec3, b: Vec3) -> float:
    return sum(x * y for x, y in zip(a, b))


def cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def length(a: Vec3) -> float:
    return math.sqrt(dot(a, a))


def unit(a: Vec3, fallback: Vec3 = (1.0, 0.0, 0.0)) -> Vec3:
    norm = length(a)
    return mul(a, 1.0 / norm) if norm > 1e-12 else fallback


def rotate_x(a: Vec3, radians: float) -> Vec3:
    c, s = math.cos(radians), math.sin(radians)
    return (a[0], c * a[1] - s * a[2], s * a[1] + c * a[2])


def smootherstep(value: float) -> float:
    u = min(1.0, max(0.0, value))
    return u * u * u * (10.0 + u * (-15.0 + 6.0 * u))
