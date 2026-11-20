"""Quiet world geometry for the thirty-second luminous-people proposal.

Coordinates are metres, with Z up. The floor is a contact surface at Z=0,
not a large piece of foreground architecture. All apparent decoration is drawn
from numeric geometry. Animation samples absolute time without mutable state.
"""
from __future__ import annotations

from functools import lru_cache
import math

import numpy as np


CENTRE = np.array((0.8, 2.0, 0.0))
CAMPAIGN_HEX = (
    "#EA5A5E", "#F2B25E", "#F6CE46", "#5ABA5A", "#62B2FA",
    "#667AF6", "#9E6AF6", "#EE62A6", "#364E96",
)


def _linear(hex_colour):
    rgb = np.array([int(hex_colour[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
    return np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)


def _ease(value):
    x = np.clip(value, 0.0, 1.0)
    return x * x * x * (10.0 + x * (-15.0 + x * 6.0))


def _triangles(positions, normals, colours, faces):
    vertex = np.concatenate((positions, normals, colours), axis=1)
    return vertex[np.asarray(faces, dtype=np.int32).reshape(-1)]


def _torus(radius, tube, height, colour, centre=CENTRE, segments=192, sides=6):
    a, b = np.meshgrid(np.linspace(0, math.tau, segments + 1),
                       np.linspace(0, math.tau, sides + 1), indexing="ij")
    normal = np.stack((np.cos(a) * np.cos(b), np.sin(a) * np.cos(b),
                       np.sin(b)), axis=-1)
    position = np.stack((radius * np.cos(a), radius * np.sin(a),
                         np.full_like(a, height)), axis=-1) + tube * normal
    position[..., :2] += np.asarray(centre)[:2]
    shade = np.broadcast_to(np.asarray(colour), position.shape).copy()
    index = np.arange((segments + 1) * (sides + 1)).reshape(segments + 1, sides + 1)
    p, q, r, s = index[:-1, :-1], index[1:, :-1], index[1:, 1:], index[:-1, 1:]
    faces = np.stack((np.stack((p, q, r), -1), np.stack((p, r, s), -1)), -2)
    return _triangles(position.reshape(-1, 3), normal.reshape(-1, 3),
                      shade.reshape(-1, 3), faces)


def _riser():
    # The back row stands on this low curved strip. Its front is at Y=4.0 in
    # the middle and recedes gently at the ends, preserving the open stage.
    x = np.linspace(-.25, 5.25, 81)
    front = 4.0 + .035 * (x - 2.5) ** 2
    back = front + .70
    position = np.vstack((np.c_[x, front, np.full_like(x, .18)],
                          np.c_[x, back, np.full_like(x, .18)],
                          np.c_[x, front, np.zeros_like(x)],
                          np.c_[x, back, np.zeros_like(x)]))
    top_colour = np.tile((.071, .037, .104), (2 * len(x), 1))
    side_colour = np.tile((.032, .016, .052), (2 * len(x), 1))
    normals = np.tile((0.0, 0.0, 1.0), (len(position), 1))
    colours = np.vstack((top_colour, side_colour))
    faces = []
    n = len(x)
    for i in range(n - 1):
        faces.extend(((i, i + 1, n + i + 1), (i, n + i + 1, n + i),
                      (i, 2*n + i, 2*n + i + 1), (i, 2*n + i + 1, i + 1),
                      (n + i, n + i + 1, 3*n + i + 1),
                      (n + i, 3*n + i + 1, 3*n + i)))
    faces.extend(((0, n, 3*n), (0, 3*n, 2*n),
                  (n - 1, 3*n - 1, 4*n - 1), (n - 1, 4*n - 1, 2*n - 1)))
    mesh = _triangles(position, normals, colours, faces)
    # Two narrow top-edge strips supply a warm contact rim without a wall.
    rims = []
    for y in (front, back):
        left = np.c_[x, y - .014, np.full_like(x, .181)]
        right = np.c_[x, y + .014, np.full_like(x, .181)]
        points = np.vstack((left, right))
        rim_faces = []
        for i in range(n - 1):
            rim_faces.extend(((i, i + 1, n + i + 1), (i, n + i + 1, n + i)))
        rims.append(_triangles(points, np.tile((0, 0, 1), (2*n, 1)),
                               np.tile((.37, .18, .058), (2*n, 1)), rim_faces))
    return np.concatenate((mesh, *rims))


@lru_cache(maxsize=1)
def static_mesh():
    """Return contiguous float32 triangle vertices: XYZ, normal XYZ, linear RGB.

    The main contact top is exactly Z=0, radius 7 m, centre (0.8, 2.0).
    The rear choir strip is Z=.18, X in [-.25, 5.25], with a curved front
    at Y=4+.035*(X-2.5)**2 and a .70 m depth. Do not raise front-row feet.
    """
    segments, rings = 160, 12
    angle, radius = np.meshgrid(np.linspace(0, math.tau, segments + 1),
                                np.linspace(0, 7.0, rings + 1))
    position = np.stack((CENTRE[0] + radius * np.cos(angle),
                         CENTRE[1] + radius * np.sin(angle),
                         np.zeros_like(angle)), axis=-1)
    normal = np.zeros_like(position)
    normal[..., 2] = 1.0
    warm = .5 + .5 * np.sin(angle * 2.0 + radius * .42)
    centre_light = .4 + .6 * np.exp(-(radius / 4.3) ** 2)
    colour = np.stack((.038 + .021 * centre_light + .008 * warm,
                       .019 + .010 * centre_light + .003 * warm,
                       .068 + .030 * centre_light - .010 * warm), axis=-1)
    grid = np.arange((rings + 1) * (segments + 1)).reshape(rings + 1, segments + 1)
    a, b, c, d = grid[:-1, :-1], grid[1:, :-1], grid[1:, 1:], grid[:-1, 1:]
    faces = np.stack((np.stack((a, b, c), -1), np.stack((a, c, d), -1)), -2)
    disc = _triangles(position.reshape(-1, 3), normal.reshape(-1, 3),
                      colour.reshape(-1, 3), faces)
    perimeter = _torus(7.0, .019, -.002, (.62, .285, .071))
    inner = _torus(6.73, .006, .003, (.18, .105, .052))
    result = np.concatenate((disc, perimeter, inner, _riser())).astype("f4")
    return np.ascontiguousarray(result)


@lru_cache(maxsize=1)
def _point_seeds():
    rng = np.random.default_rng(20261120)
    n = 480
    angle = rng.uniform(0, math.tau, n)
    radius = rng.uniform(5.6, 7.05, n)
    rim = np.c_[CENTRE[0] + radius * np.cos(angle),
                CENTRE[1] + radius * np.sin(angle), rng.uniform(.025, .18, n)]
    back = np.c_[rng.uniform(-7.0, 8.0, 180), rng.uniform(6.0, 12.0, 180),
                 rng.uniform(1.0, 6.7, 180)]
    # Foreground motes remain at the edges, clear of the pair and conductor.
    x = rng.choice((-1.0, 1.0), 56) * rng.uniform(5.0, 8.0, 56)
    near = np.c_[x, rng.uniform(-4.0, -.5, 56), rng.uniform(.3, 2.6, 56)]
    position = np.vstack((rim, back, near))
    phase = rng.uniform(0, math.tau, len(position))
    strength = rng.uniform(.10, .45, len(position))
    size = rng.uniform(.75, 2.2, len(position))
    size[-56:] *= 1.3
    return position, phase, strength, size


def environment_points(t):
    """Return stable, gently breathing world points as float32 XYZ/RGB/size.

    RGB is linear, size is in pixels at 1080p. No particles are reseeded,
    teleported, wrapped or emitted across the principal face/hand area.
    """
    time = float(t)
    if not math.isfinite(time):
        raise ValueError("Environment time must be finite.")
    position, phase, strength, size = _point_seeds()
    position = position.copy()
    position[480:, 0] += .055 * np.sin(time * .33 + phase[480:])
    position[480:, 2] += .065 * np.sin(time * .23 + phase[480:] * .7)
    breathing = .76 + .24 * np.sin(time * .45 + phase)
    rise = 1.0 + .38 * float(_ease((time - 20.0) / 7.0))
    colour = (strength * breathing * rise)[:, None] * _linear("#FFDB9F")[None, :]
    return np.ascontiguousarray(np.c_[position, colour, size], dtype="f4")


def ribbon_paths(t):
    """Nine canopy streams, behind the choir and above the human action.

    Dictionaries contain positions (Nx3), color (linear RGB), width_metres,
    its compatibility alias width, and phase. Paths appear smoothly after
    20 seconds and finish gathering
    before the final hold. All points remain Y>5 and Z>3, away from faces.
    """
    time = float(t)
    if not math.isfinite(time):
        raise ValueError("Ribbon time must be finite.")
    growth = float(_ease((time - 20.0) / 6.6))
    if growth <= 0:
        return []
    u = np.linspace(0.0, 1.0, 176)
    progress = u * (.025 + .975 * growth)
    paths = []
    for i, hex_colour in enumerate(CAMPAIGN_HEX):
        family, strand = divmod(i, 3)
        offset = strand - 1.0
        if family == 0:
            x = -6.5 + 14.0 * progress
            y = 8.9 + .85 * np.cos(math.pi * progress)
            z = 3.3 + 4.25 * np.sin(math.pi * progress)
        elif family == 1:
            x = -6.0 + 13.3 * progress
            y = 6.8 + 1.15 * np.sin(math.pi * progress)
            z = 3.35 + 2.5 * np.sin(math.pi * progress) + .75 * progress
        else:
            x = 7.3 - 13.7 * progress
            y = 9.8 - 1.1 * np.cos(math.pi * progress)
            z = 3.6 + 3.3 * np.sin(math.pi * progress) + .25 * progress
        x += offset * .025 * np.sin(progress * math.tau)
        y += offset * (.082 + .035 * np.sin(progress * 5.0 + family))
        z += offset * (.065 + .025 * np.sin(progress * 4.0 + family))
        z += .025 * np.sin(time * .28 + progress * 3.0 + family)
        colour = _linear(hex_colour) * growth
        width = (.018, .014, .016)[family] * (.93, 1.04, .88)[strand]
        paths.append({"positions": np.ascontiguousarray(np.c_[x, y, z], dtype="f4"),
                      "color": tuple(float(v) for v in colour),
                      "width_metres": width, "width": width,
                      "phase": float(.06 + .84 * _ease((time - 20.0) / 9.7) + .006 * i)})
    return paths
