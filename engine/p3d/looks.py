"""Looks of the particle bodies: how the cloud of points on a body is drawn.

A look turns the body's points (with their parts, heights and seeds) into draw layers. Each layer is a share
of the points with a sprite kind, sizes, colours and settings; engine/p3d/body.py fills in the positions at
each time and hands the layers to the renderer as batches.

Looks (may be combined in a list, for example look=["rim", "glitter"]):
  "glitter"   thousands of fine glittering points, a few bright glints (ref 15, 10, 09)
  "plexus"    points joined to their neighbours by fine lines, brighter toward the light (ref 03, 12)
  "rim"       light only on the edge of the silhouette as seen from the camera, the inside dark (ref 01, 16).
              Add the body with body.add(scene, name) so that its dark shape also hides what is behind it.
  "dots"      evenly spaced flat dots in two or three colours (ref 14)
  "window"    the silhouette as a window onto a sky (ref 08): a few stars inside and a light edge; the fill
              comes from the renderer's mask pass, see Body.mask()
A look may also be a dict: dict(name="glitter", bright=1.4, size=1.2, color="#...", color2="#...").
"""
import numpy as np

from . import bodymath as bm
from .api import lin

LOOKS = ("glitter", "plexus", "rim", "dots", "window")

# part codes of the cloud points
SKIN, HAND, CLOTH, VEIL, HAIR, FOOT = 0, 1, 2, 3, 4, 5


def _col(c):
    return lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


def _spec(look):
    if isinstance(look, str):
        return dict(name=look)
    d = dict(look)
    if "name" not in d:
        raise ValueError("a look given as a dict needs a name")
    return d


def _noise(rest, scale, salt):
    """A smooth 0..1 field over the body (for patches of colour)."""
    f = bm.flow(rest, 0.0, scale=scale, speed=0.0, seed=salt)
    return np.clip(0.5 + 0.9 * f[:, 0] * 0.6 + 0.5 * f[:, 1] * 0.4, 0.0, 1.0)


def build(look, cloud, color, color2, bright=1.0, scale=1.0):
    """The draw layers of one look for a cloud. cloud: dict(n, part, seed, h, rest, strand (bool), pairs_fn).
    Returns a list of layers: dict(kind, idx, size, color, alpha, emit, seed, twinkle, rim, backlight,
    lines (optional (m, 2) pairs of cloud indices))."""
    sp = _spec(look)
    name = sp["name"]
    if name not in LOOKS:
        raise ValueError("look must be one of %s, got %r" % (LOOKS, name))
    n = cloud["n"]
    part = cloud["part"]
    seed = cloud["seed"].astype(np.float64)
    c1 = _col(sp.get("color", color))
    c2 = _col(sp.get("color2", color2))
    b = bright * sp.get("bright", 1.0)
    sz = scale * sp.get("size", 1.0)
    r2 = bm.hashf((seed * 1e6).astype(np.int64), 5)
    r3 = bm.hashf((seed * 1e6).astype(np.int64), 6)
    soft_part = np.where(part == VEIL, 0.55, np.where(part == HAIR, 0.8, 1.0))      # a veil is sheer
    layers = []
    allp = np.arange(n)

    if name == "glitter":
        mix = np.clip(_noise(cloud["rest"], 3.0, 1.0) * 0.7 + 0.3 * r2, 0, 1)
        col = c1[None] * (1 - mix)[:, None] + c2[None] * mix[:, None]
        # most grains are fine and some are dark, a few are large: the grain of glitter
        tone = np.where(r3 < 0.28, 0.22, 0.75 + 0.5 * r2)
        size = (0.0026 + 0.0075 * seed ** 4) * sz
        glint = seed > 0.9965
        base = ~glint
        layers.append(dict(kind="soft", idx=allp[base], size=size[base], color=col[base] * tone[base, None],
                           alpha=0.42 * b * soft_part[base], emit=1.0, twinkle=0.8, rim=(0.55, 1.5), backlight=0.12))
        layers.append(dict(kind="spark", idx=allp[glint], size=size[glint] * 1.2, color=col[glint] * 0.6 + 0.4 * c2,
                           alpha=0.9 * b, emit=1.6 + 2.6 * r2[glint], twinkle=1.0, rim=(0.0, 2.0), backlight=0.15))
    elif name == "rim":
        size = (0.0024 + 0.0055 * seed ** 4) * sz
        mix = r2 * 0.5
        col = c1[None] * (1 - mix)[:, None] + c2[None] * mix[:, None]
        layers.append(dict(kind="soft", idx=allp, size=size, color=col, alpha=0.9 * b * soft_part, emit=1.0,
                           twinkle=0.5, rim=(1.0, sp.get("power", 3.2)), backlight=0.1))
        inner = allp[seed > 0.93]
        layers.append(dict(kind="soft", idx=inner, size=size[inner], color=col[inner], alpha=0.10 * b, emit=1.0,
                           twinkle=0.9, rim=(0.0, 2.0), backlight=0.0))
    elif name == "dots":
        keep = allp[seed < sp.get("share", 0.26)]
        f = _noise(cloud["rest"][keep], 2.2, 2.0)
        r = r2[keep]
        t3 = np.where(r < 0.5 + 0.9 * (f - 0.5), 0.0, 1.0)
        col = c1[None] * (1 - t3)[:, None] + c2[None] * t3[:, None]
        white = r3[keep] > 0.9
        col[white] = 0.5 * col[white] + 0.5
        layers.append(dict(kind="disc", idx=keep, size=np.full(len(keep), 0.0105 * sz) * (0.8 + 0.5 * r3[keep]),
                           color=col, alpha=0.95 * b, emit=1.3, twinkle=0.15, rim=(0.0, 2.0), backlight=0.0))
    elif name == "plexus":
        nodes = allp[seed < sp.get("share", 0.07)]
        size = (0.007 + 0.012 * r2[nodes] ** 3) * sz
        col = c1[None] * (0.6 + 0.4 * r3[nodes, None]) + c2[None] * 0.4 * (1 - r3[nodes, None])
        layers.append(dict(kind="spark", idx=nodes, size=size, color=col, alpha=0.95 * b, emit=1.5 + 3.0 * (r2[nodes] > 0.9),
                           twinkle=0.6, rim=(0.25, 1.5), backlight=0.4, lit=0.7,
                           lines=cloud["pairs_fn"](nodes, sp.get("links", 3), sp.get("reach", 0.11)),
                           line_color=c2 * 0.55 + c1 * 0.45, line_alpha=0.42 * b, line_size=0.0022 * sz))
        haze = allp[(seed > 0.07) & (seed < 0.07 + sp.get("haze", 0.35))]
        layers.append(dict(kind="soft", idx=haze, size=np.full(len(haze), 0.0036 * sz), color=np.broadcast_to(c1, (len(haze), 3)),
                           alpha=0.22 * b, emit=1.0, twinkle=0.5, rim=(0.5, 1.8), backlight=0.3))
    elif name == "window":
        stars = allp[seed > 0.9]
        layers.append(dict(kind="spark", idx=stars, size=(0.006 + 0.01 * r2[stars] ** 3) * sz,
                           color=np.broadcast_to(c2, (len(stars), 3)), alpha=0.7 * b, emit=2.0 + 4.0 * (r3[stars] > 0.85),
                           twinkle=1.0, rim=(0.0, 2.0), backlight=0.0))
        edge = allp[seed < 0.6]
        layers.append(dict(kind="soft", idx=edge, size=np.full(len(edge), 0.005 * sz), color=np.broadcast_to(c1, (len(edge), 3)),
                           alpha=0.55 * b, emit=1.2, twinkle=0.3, rim=(1.0, 3.2), backlight=0.0))
    for ly in layers:
        ly.setdefault("lit", 0.0)
        ly["seed"] = cloud["seed"][ly["idx"]]
        ly["color"] = np.ascontiguousarray(ly["color"], np.float32)
        ly["size"] = np.asarray(ly["size"], np.float32)
        if np.ndim(ly["alpha"]) == 0:
            ly["alpha"] = np.full(len(ly["idx"]), ly["alpha"], np.float32)
        else:
            ly["alpha"] = np.asarray(ly["alpha"], np.float32)
        if np.ndim(ly["emit"]) == 0:
            ly["emit"] = np.full(len(ly["idx"]), ly["emit"], np.float32)
        else:
            ly["emit"] = np.asarray(ly["emit"], np.float32)
    return layers
