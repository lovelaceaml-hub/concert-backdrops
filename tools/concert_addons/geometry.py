"""Small world-space geometry helpers implementing the native p3d batch protocol."""
from __future__ import annotations

import numpy as np


def smooth(a, b, t):
    """A quintic transition with zero velocity and acceleration at its endpoints."""
    u = np.clip((np.asarray(t, dtype=float) - a) / (b - a), 0, 1)
    return u ** 3 * (10 + u * (-15 + 6 * u))


def linear(hex_color):
    return np.array([int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]) ** 2.2


def rx(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def ellipsoid(center, radii, count=300, rotation=None):
    """Deterministic surface positions and true ellipsoid surface normals."""
    i = np.arange(count, dtype=float) + .5
    y = 1 - 2 * i / count
    a = i * (np.pi * (3 - np.sqrt(5)))
    r = np.sqrt(1 - y * y)
    sphere = np.stack([r * np.cos(a), y, r * np.sin(a)], 1)
    radii = np.asarray(radii, dtype=float)
    rotation = np.eye(3) if rotation is None else np.asarray(rotation)
    p = sphere * radii @ rotation.T + np.asarray(center)
    n = unit(sphere / radii) @ rotation.T
    return p, n


def surface(points, color="#fff0d3", size=.008, alpha=.25, normals=None, **settings):
    """A p3d Batch dictionary; all positions and widths are in metres."""
    result = dict(pos=np.asarray(points, dtype="f4"), color=linear(color), size=size,
                  alpha=alpha, kind="soft", twinkle=0.0, reflect=True, dof=1.0)
    if normals is not None:
        result["normal"] = np.asarray(normals, dtype="f4")
    result.update(settings)
    return result


class LineSet:
    """Reusable static point set of 3D curves, using p3d's line-batch contract."""
    static = True

    def __init__(self, curves, color="#efc98d", width=.006, alpha=.3, **settings):
        curves = [np.asarray(curve, dtype=float) for curve in curves if len(curve) > 1]
        self.batch = dict(pos=np.concatenate([curve[:-1] for curve in curves]).astype("f4"),
                          pos2=np.concatenate([curve[1:] for curve in curves]).astype("f4"),
                          color=linear(color), size=width, alpha=alpha, kind="line", **settings)

    def sample(self, t):
        return self.batch


def lines(curves, color="#efc98d", width=.006, alpha=.3, **settings):
    return LineSet(curves, color, width, alpha, **settings).sample(0)


def feather(root, tip, width, normal=(0, 1, 0), samples=15):
    """A narrow three-dimensional feather surface, shaft and closed contour."""
    root, tip = np.asarray(root, float), np.asarray(tip, float)
    axis = tip - root
    normal = unit(normal)
    lateral = unit(np.cross(normal, axis))
    u = np.linspace(0, 1, samples)
    span = width * np.sin(np.pi * u) ** .72
    center = root + u[:, None] * axis + np.sin(np.pi * u)[:, None] * normal * width * .32
    v = np.linspace(-1, 1, 7)
    p = center[:, None, :] + (span[:, None] * v[None, :])[:, :, None] * lateral
    p += ((1 - v * v)[None, :] * np.sin(np.pi * u)[:, None])[:, :, None] * normal * width * .10
    contour = np.concatenate([center + span[:, None] * lateral,
                              (center - span[:, None] * lateral)[::-1], center[:1]])
    return p.reshape(-1, 3), np.broadcast_to(normal, (p.size // 3, 3)).copy(), [contour, center]


def transform_batches(batches, position, rotation=None, scale=1):
    rotation = np.eye(3) if rotation is None else rotation
    out = []
    for batch in batches:
        result = dict(batch)
        result["pos"] = np.asarray(batch["pos"]) * scale @ rotation.T + position
        if "pos2" in batch:
            result["pos2"] = np.asarray(batch["pos2"]) * scale @ rotation.T + position
        if "normal" in batch:
            result["normal"] = np.asarray(batch["normal"]) @ rotation.T
        result["size"] = np.asarray(batch.get("size", .008)) * scale
        out.append(result)
    return out


def wind(t, x, z, strength=1):
    """One traveling field sampled at different spatial locations."""
    return strength * (.045 * np.sin(.75 * t - 1.25 * x - .55 * z)
                       + .015 * np.sin(1.6 * t - 2.7 * x + .7 * z))
