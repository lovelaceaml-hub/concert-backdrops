"""Analytical two-bone IK, with explicit reach and contact diagnostics."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .math3d import Vec3, add, dot, finite_number, length, mul, sub, unit, vec3


@dataclass(frozen=True)
class IKSolution:
    root: Vec3
    joint: Vec3
    end: Vec3
    target: Vec3
    clamped: bool
    reach_error: float


def solve_two_bone(root, target, pole, upper_length, lower_length) -> IKSolution:
    """Place an elbow/knee toward pole while retaining both segment lengths.

    The target is clamped to the reachable shell. Callers must check reach_error;
    an unreachable target is never reported as a successful hand/foot contact.
    """
    root, target, pole = vec3(root), vec3(target), vec3(pole)
    a, b = finite_number(upper_length), finite_number(lower_length)
    if a <= 0 or b <= 0:
        raise ValueError("bone lengths must be positive")
    delta = sub(target, root)
    distance = length(delta)
    axis = unit(delta, (0.0, -1.0, 0.0))
    reachable = max(abs(a - b) + 1e-9, min(a + b - 1e-9, distance))
    pole_delta = sub(pole, root)
    bend = sub(pole_delta, mul(axis, dot(axis, pole_delta)))
    if length(bend) < 1e-9:
        reference = min(((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), key=lambda v: abs(dot(axis, v)))
        bend = sub(reference, mul(axis, dot(axis, reference)))
    bend = unit(bend)
    along = (a * a - b * b + reachable * reachable) / (2.0 * reachable)
    height = math.sqrt(max(0.0, a * a - along * along))
    joint = add(add(root, mul(axis, along)), mul(bend, height))
    end = add(root, mul(axis, reachable))
    error = length(sub(end, target))
    return IKSolution(root, joint, end, target, error > 1e-7, error)
