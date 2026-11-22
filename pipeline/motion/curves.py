"""Natural cubic interpolation with analytic first and second derivatives.

This implementation deliberately has no NumPy/SciPy dependency: the same code
can be imported by the CLI, Blender's bundled Python, and offline tests.
"""
from __future__ import annotations

from bisect import bisect_right
from collections.abc import Sequence
from dataclasses import dataclass

from .math3d import finite_number


@dataclass(frozen=True)
class CurveSample:
    value: tuple[float, ...]
    velocity: tuple[float, ...]
    acceleration: tuple[float, ...]


class CubicSpline:
    """C2 interpolating spline, with zero endpoint second derivatives.

    Outside the knot domain, values hold and derivatives are zero. A linear
    time warp can therefore start abruptly at the domain boundary. CameraTrack
    uses a whole-shot quintic time warp by default to avoid that boundary jump.
    """

    def __init__(self, seconds: Sequence[float], values: Sequence[Sequence[float]]):
        if len(seconds) < 2 or len(seconds) != len(values):
            raise ValueError("a spline needs at least two matching times and values")
        self.seconds = tuple(finite_number(t, "seconds") for t in seconds)
        if any(b <= a for a, b in zip(self.seconds, self.seconds[1:])):
            raise ValueError("seconds must be strictly increasing")
        self.values = tuple(tuple(finite_number(v, "coordinate") for v in point) for point in values)
        dimensions = len(self.values[0])
        if dimensions < 1 or any(len(point) != dimensions for point in self.values):
            raise ValueError("spline values must have matching dimensions")
        self.dimensions = dimensions
        count = len(self.seconds)
        widths = [b - a for a, b in zip(self.seconds, self.seconds[1:])]
        seconds_by_dimension = []
        for dimension in range(dimensions):
            # The natural boundary values are fixed at zero. Solve the interior
            # tridiagonal system with Thomas elimination, one coordinate at a time.
            diagonal, upper, rhs = [], [], []
            for i in range(1, count - 1):
                diagonal.append(2.0 * (widths[i - 1] + widths[i]))
                upper.append(widths[i])
                rhs.append(6.0 * ((self.values[i + 1][dimension] - self.values[i][dimension]) / widths[i]
                                  - (self.values[i][dimension] - self.values[i - 1][dimension]) / widths[i - 1]))
            for i in range(1, len(diagonal)):
                factor = widths[i] / diagonal[i - 1]
                diagonal[i] -= factor * upper[i - 1]
                rhs[i] -= factor * rhs[i - 1]
            interior = [0.0] * len(diagonal)
            for i in reversed(range(len(diagonal))):
                interior[i] = (rhs[i] - (upper[i] * interior[i + 1] if i + 1 < len(diagonal) else 0.0)) / diagonal[i]
            seconds_by_dimension.append([0.0, *interior, 0.0])
        self.second_derivatives = tuple(tuple(seconds_by_dimension[d][i] for d in range(dimensions)) for i in range(count))

    def sample(self, seconds: float) -> CurveSample:
        t = finite_number(seconds, "sample time")
        zero = (0.0,) * self.dimensions
        if t < self.seconds[0]:
            return CurveSample(self.values[0], zero, zero)
        if t > self.seconds[-1]:
            return CurveSample(self.values[-1], zero, zero)
        i = min(len(self.seconds) - 2, max(0, bisect_right(self.seconds, t) - 1))
        width = self.seconds[i + 1] - self.seconds[i]
        left, right = (self.seconds[i + 1] - t) / width, (t - self.seconds[i]) / width
        value, velocity, acceleration = [], [], []
        for y0, y1, m0, m1 in zip(self.values[i], self.values[i + 1], self.second_derivatives[i], self.second_derivatives[i + 1]):
            value.append(left * y0 + right * y1 + ((left ** 3 - left) * m0 + (right ** 3 - right) * m1) * width ** 2 / 6.0)
            velocity.append((y1 - y0) / width + width * ((1.0 - 3.0 * left ** 2) * m0 + (3.0 * right ** 2 - 1.0) * m1) / 6.0)
            acceleration.append(left * m0 + right * m1)
        return CurveSample(tuple(value), tuple(velocity), tuple(acceleration))
