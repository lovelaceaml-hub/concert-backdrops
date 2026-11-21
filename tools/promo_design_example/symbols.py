"""The approved nine campaign symbols as quietly orbiting strokes of light.

The existing brand geometry supplies every stroke and campaign colour. This
module only places those shapes in the example's Z-up world, with the Earth at
the origin. Output colours are linear RGB for the additive scene renderer.
"""

from __future__ import annotations

from functools import lru_cache
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]


def _smoother(value: float) -> float:
    x = min(1.0, max(0.0, value))
    return x * x * x * (10.0 + x * (-15.0 + 6.0 * x))


def _linear(rgb) -> np.ndarray:
    colour = np.asarray(rgb, dtype=np.float64)
    return np.where(colour <= .04045, colour / 12.92,
                    ((colour + .055) / 1.055) ** 2.4)


def _rotation(rx: float, rz: float) -> np.ndarray:
    sx, cx = math.sin(rx), math.cos(rx)
    sz, cz = math.sin(rz), math.cos(rz)
    tilt = np.array(((1.0, 0.0, 0.0), (0.0, cx, -sx), (0.0, sx, cx)))
    turn = np.array(((cz, -sz, 0.0), (sz, cz, 0.0), (0.0, 0.0, 1.0)))
    return turn @ tilt


@lru_cache(maxsize=1)
def _assets():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from engine.p3d import brand, brand_symbols

    ivory = _linear((1.0, .93, .79))
    output = []
    for index, name in enumerate(brand.LABELS):
        xy = np.asarray(brand_symbols.symbol_points(name, n=320,
                                                    seed=2026 + index)["xy"],
                        dtype=np.float64)
        colour = brand.EXPRESSION_COLORS[name]
        rgb = _linear([int(colour[k:k + 2], 16) / 255.0 for k in (1, 3, 5)])
        # Keep the campaign colour while giving fine strokes a warm light core.
        rgb = rgb * .95 + ivory * .23
        output.append((xy, rgb))
    return tuple(output)


def symbol_vertices(t: float, camera_position) -> np.ndarray:
    """Return contiguous float32 Nx7: XYZ, linear RGB, point size at 1080p.

    The nine shapes occupy three inclined orbital planes around radius 2.2 m.
    Each shape faces the camera without rotating its own artwork. Its emergence
    is staggered between 3.5 and 6.5 seconds, and the entire orbit advances only
    twelve degrees over the shot. The caller's Earth depth buffer hides strokes
    on the far side. Requesting frames in any order gives the same geometry.
    """
    time = float(t)
    camera = np.asarray(camera_position, dtype=np.float64)
    if not math.isfinite(time) or camera.shape != (3,) or not np.isfinite(camera).all():
        raise ValueError("Time and camera position must be finite.")
    distance = float(np.linalg.norm(camera))
    if distance < 1e-8:
        raise ValueError("Camera cannot be at the Earth's centre.")
    forward = -camera / distance
    right = np.cross(forward, (0.0, 0.0, 1.0))
    if np.linalg.norm(right) < 1e-8:
        right = np.cross(forward, (0.0, 1.0, 0.0))
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    drift = math.radians(12) * _smoother(time / 10.0)
    inclinations = (55.0, -43.0, 82.0)
    rotations = (-13.0, 25.0, -15.0)
    phases = (10.0, 48.0, 82.0)
    vertices = []
    for index, (xy, rgb) in enumerate(_assets()):
        plane, place = index % 3, index // 3
        angle = math.radians(phases[plane] + 120.0 * place) + drift
        radius = 2.10 + .05 * plane
        centre = _rotation(math.radians(inclinations[plane]),
                           math.radians(rotations[plane])) @ np.array(
            (radius * math.cos(angle), radius * math.sin(angle), 0.0))
        height = .145 + .005 * plane
        positions = centre + height * (xy[:, :1] * right + xy[:, 1:] * up)
        presence = _smoother((time - (3.5 + .175 * index)) / 1.6)
        nearness = float(np.dot(centre / radius, camera / distance))
        depth_gain = .72 + .28 * _smoother((nearness + 1.0) * .5)
        colours = np.broadcast_to(rgb * presence * depth_gain,
                                  (len(xy), 3))
        sizes = np.full((len(xy), 1), 2.2)
        vertices.append(np.concatenate((positions, colours, sizes), axis=1))
    return np.ascontiguousarray(np.vstack(vertices), dtype=np.float32)
