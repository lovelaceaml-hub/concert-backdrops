"""Original geometric assets for the ten-second Nine Colours design example.

Everything is generated from numeric geometry. Coordinates use Z-up, with the
Earth centred at the origin. There is no image generation, downloaded model,
simulation state, or dependency on the order in which frames are requested.
"""
from __future__ import annotations

import math

import numpy as np


CAMPAIGN_HEX = (
    "#EA5A5E", "#F2B25E", "#F6CE46", "#5ABA5A", "#62B2FA",
    "#667AF6", "#9E6AF6", "#EE62A6", "#364E96",
)

CAMPAIGN_RGB = tuple(
    tuple(int(colour[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    for colour in CAMPAIGN_HEX
)


def _smoother(value):
    """A clamped quintic ease with zero first/second endpoint derivatives."""
    x = np.clip(value, 0.0, 1.0)
    return x * x * x * (x * (6.0 * x - 15.0) + 10.0)


def _rotation(rx: float, ry: float, rz: float) -> np.ndarray:
    sx, cx = math.sin(rx), math.cos(rx)
    sy, cy = math.sin(ry), math.cos(ry)
    sz, cz = math.sin(rz), math.cos(rz)
    x = np.array(((1.0, 0.0, 0.0), (0.0, cx, -sx), (0.0, sx, cx)))
    y = np.array(((cy, 0.0, sy), (0.0, 1.0, 0.0), (-sy, 0.0, cy)))
    z = np.array(((cz, -sz, 0.0), (sz, cz, 0.0), (0.0, 0.0, 1.0)))
    return z @ y @ x


def sphere_mesh(radius: float = 1.55, segments: int = 128,
                rings: int = 64) -> np.ndarray:
    """Return outward-facing triangle vertices as contiguous float32 Nx8.

    Columns are position XYZ, outward unit normal XYZ, UV. Longitude maps
    from -180 degrees at u=0 to +180 degrees at u=1. Latitude maps from north
    at v=0 to south at v=1, matching the original rows in land_2048.png. Upload
    that image without a vertical flip when using these UVs. The longitude
    seam is duplicated so triangle interpolation never crosses the UV wrap.
    """
    radius = float(radius)
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError("sphere radius must be finite and positive")
    if isinstance(segments, bool) or int(segments) != segments or segments < 8:
        raise ValueError("sphere needs an integer count of at least 8 segments")
    if isinstance(rings, bool) or int(rings) != rings or rings < 4:
        raise ValueError("sphere needs an integer count of at least 4 rings")
    segments, rings = int(segments), int(rings)
    u = np.linspace(0.0, 1.0, segments + 1)
    v = np.linspace(0.0, 1.0, rings + 1)
    uu, vv = np.meshgrid(u, v)
    longitude = uu * math.tau - math.pi
    colatitude = vv * math.pi
    normals = np.stack((
        np.sin(colatitude) * np.cos(longitude),
        np.sin(colatitude) * np.sin(longitude),
        np.cos(colatitude),
    ), axis=-1)
    vertices = np.concatenate((normals * radius, normals,
                               uu[..., None], vv[..., None]), axis=-1)
    vertices = vertices.reshape((-1, 8))
    row, column = np.meshgrid(np.arange(rings), np.arange(segments), indexing="ij")
    a = (row * (segments + 1) + column).ravel()
    b, c, d = a + 1, a + segments + 1, a + segments + 2
    # Omit one degenerate triangle at each pole. Winding is CCW from outside.
    first = np.stack((a, c, d), axis=-1)[row.ravel() != rings - 1]
    second = np.stack((a, d, b), axis=-1)[row.ravel() != 0]
    indices = np.concatenate((first, second)).ravel()
    return np.ascontiguousarray(vertices[indices], dtype=np.float32)


def make_ribbon_paths(t: float) -> list[dict]:
    """Return nine smoothly gathering world-space paths at absolute seconds t.

    Each dictionary contains 224 float32 XYZ positions, an exact campaign
    sRGB colour tuple (0..1), a world-space width and a normalised light-packet
    phase. Colour emission/tone mapping belongs to the renderer, so dark blue
    is retained here and can receive a luminous ivory core there.

    At the beginning, the first part of each path reaches into the lower-left
    foreground. The tail contracts towards its inclined orbit between 0.4 s and
    6 s. A quintic spatial weight joins that tail to the orbit with continuous
    position, tangent and curvature. All paths are sampled from absolute time.
    Three families of three strands take different flowing spatial paths. Their
    orbit arcs continue with a very small, smooth drift after gathering.
    """
    time = float(t)
    if not math.isfinite(time):
        raise ValueError("ribbon time must be finite")
    time = min(10.0, max(0.0, time))
    u = np.linspace(0.0, 1.0, 224)
    gather = float(_smoother((time - 0.4) / 5.6))
    shot_ease = float(_smoother(time / 10.0))
    tail_weight = (1.0 - _smoother(u / 0.35))[:, None]
    lower_tail_weight = 1.0 - _smoother(u / 0.46)
    output = []
    # Warm low sweep, cool rising arch, and violet/rose counter-arc. Each family
    # is an open stream, with distinct inclination and changing curvature.
    family_specs = (
        (2.38, 224.0, 20.0, -16.0, -20.0, 1.08, 0.95, 0.0220),
        (2.65, 212.0, 67.0, 11.0, 23.0, 0.96, 1.04, 0.0210),
        (2.52, 238.0, -48.0, -20.0, -16.0, 1.04, 0.98, 0.0227),
    )
    for index, colour in enumerate(CAMPAIGN_RGB):
        family, strand = divmod(index, 3)
        spread = strand - 1.0
        base, arc, rx, ry, rz, stretch_x, stretch_y, width = family_specs[family]
        theta = (math.pi + math.radians(arc) * u + 0.023 * spread
                 + (0.15 + 0.04 * family) * shot_ease)
        # Variable spacing and curvature remove the rigid nested-hoop look.
        separation = spread * (0.054 + 0.028 * np.sin(theta * 1.4 + family))
        radius = (base + separation + 0.14 * np.sin(theta * 1.25 + family * 1.1)
                  + 0.045 * np.sin(theta * 2.7 + strand * 0.6))
        positions = np.column_stack((
            stretch_x * radius * np.cos(theta),
            stretch_y * radius * np.sin(theta),
            0.13 * np.sin(theta * 1.6 + family * 1.3)
            + spread * 0.025 * np.sin(theta * 2.2),
        ))
        transform = _rotation(math.radians(rx + spread * 0.9),
                              math.radians(ry + spread * 1.3),
                              math.radians(rz + spread * 0.75))
        positions = positions @ transform.T
        positions[:, 2] += (-0.08, 0.03, 0.02)[family]
        # Lower the foreground tails so the title's left-side reading area
        # stays calm. Their join remains a quintic spatial deformation.
        extension = np.array((-6.3 - 0.10 * family - 0.06 * spread,
                              -3.3 + 0.12 * family - 0.08 * spread,
                              0.0))
        positions += tail_weight * extension * (1.0 - gather) ** 2
        positions[:, 2] -= lower_tail_weight * (9.5 + 0.35 * family) * (1.0 - gather)
        # Packet phases are bounded, so an open path never wraps a head abruptly.
        phase = 0.075 + 0.79 * shot_ease + 0.011 * index
        output.append({
            "positions": np.ascontiguousarray(positions, dtype=np.float32),
            "colours": colour,
            "width": width * (0.92, 1.10, 0.86)[strand],
            "phase": float(phase),
        })
    return output


def star_points(count: int = 600, seed: int = 2026) -> np.ndarray:
    """Return fixed float32 Nx3 stars in an isotropic 12..30-metre shell.

    Coordinates do not depend on animation time, preventing temporal sparkle
    reseeding. The caller controls subtle brightness variation and point size.
    """
    if isinstance(count, bool) or int(count) != count or count < 0:
        raise ValueError("star count must be a nonnegative integer")
    rng = np.random.default_rng(seed)
    count = int(count)
    direction = rng.normal(size=(count, 3))
    length = np.linalg.norm(direction, axis=1)
    direction /= np.maximum(length[:, None], 1e-12)
    distance = rng.uniform(12.0, 30.0, size=(count, 1))
    return np.ascontiguousarray(direction * distance, dtype=np.float32)
