"""Campaign symbols drawn in light: procedural bezier outlines (pure numpy, no images).

Each builder returns a list of strokes. A stroke is a dict:
  pts   (N, 2) polyline in unit coordinates (height about 1, centred on 0, y up)
  role  colour role ("coral", "orange", "sky", "olive", "gold", "goldw", "bridge")
  win   (s0, s1): when the pen draws this stroke, as fractions of the symbol's draw time
  grp   0 fixed, 1 left door, 2 right door (gate only; the doors swing open)
How a song uses them: engine/UPGRADE-HOWTO.md, section I8.
"""
import math

import numpy as np

ROLES = {
    "coral": "#F0566A",    # campaign heart
    "orange": "#F39A3A",   # campaign heart
    "sky": "#7cc6ff",      # the globe
    "olive": "#86dc6e",    # the olive sprig
    "gold": "#ffd27a",     # the gate of light
    "goldw": "#fff0c8",    # the gate's brightest lines
    "bridge": "#ffdca0",   # the bridge of light
}

# the gate's doorway in unit coordinates: half width, spring line of the arch, bottom
GATE_DOOR = (0.20, -0.04, -0.43)


def cubic(p0, p1, p2, p3, n=64):
    u = np.linspace(0.0, 1.0, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, dtype=np.float64) for p in (p0, p1, p2, p3))
    return ((1 - u) ** 3) * p0 + 3 * ((1 - u) ** 2) * u * p1 + 3 * (1 - u) * u * u * p2 + (u ** 3) * p3


def quad(p0, p1, p2, n=32):
    p0, p1, p2 = (np.asarray(p, dtype=np.float64) for p in (p0, p1, p2))
    return cubic(p0, p0 + (p1 - p0) * 2 / 3, p2 + (p1 - p2) * 2 / 3, p2, n)


def line(a, b, n=16):
    u = np.linspace(0.0, 1.0, n)[:, None]
    return np.asarray(a, dtype=np.float64) * (1 - u) + np.asarray(b, dtype=np.float64) * u


def chain(*segs):
    out = [segs[0]]
    for s in segs[1:]:
        out.append(s[1:])
    return np.vstack(out)


def ellipse(cx, cy, rx, ry, a0=0.0, a1=2 * math.pi):
    """An ellipse as four cubic beziers (the usual 0.5523 circle approximation), cut to [a0, a1]."""
    k = 0.5523
    segs = []
    for q in range(4):
        th0 = q * math.pi / 2
        c0, s0, c1, s1 = math.cos(th0), math.sin(th0), math.cos(th0 + math.pi / 2), math.sin(th0 + math.pi / 2)
        p0 = (cx + rx * c0, cy + ry * s0)
        p3 = (cx + rx * c1, cy + ry * s1)
        p1 = (p0[0] - k * rx * s0, p0[1] + k * ry * c0)
        p2 = (p3[0] + k * rx * s1, p3[1] - k * ry * c1)
        segs.append(cubic(p0, p1, p2, p3, 48))
    pts = chain(*segs)
    if a0 != 0.0 or a1 != 2 * math.pi:
        ang = np.mod(np.arctan2((pts[:, 1] - cy) / max(ry, 1e-9), (pts[:, 0] - cx) / max(rx, 1e-9)), 2 * math.pi)
        pts = pts[(ang >= a0 - 1e-6) & (ang <= a1 + 1e-6)]
        pts = pts[np.argsort(np.mod(np.arctan2((pts[:, 1] - cy) / max(ry, 1e-9),
                                               (pts[:, 0] - cx) / max(rx, 1e-9)), 2 * math.pi))]
    return pts


def xform(pts, scale=1.0, rot=0.0, off=(0.0, 0.0)):
    c, s = math.cos(rot), math.sin(rot)
    p = pts * scale
    return np.stack([p[:, 0] * c - p[:, 1] * s + off[0], p[:, 0] * s + p[:, 1] * c + off[1]], axis=1)


def heart_path():
    """One closed heart, height 1 (tip at -0.5): the pen starts at the top cusp, runs round the left lobe down to
    the tip and back up the right side."""
    l1 = cubic((0.0, 0.30), (-0.10, 0.55), (-0.55, 0.55), (-0.52, 0.20))
    l2 = cubic((-0.52, 0.20), (-0.50, -0.05), (-0.20, -0.25), (0.0, -0.50))
    left = chain(l1, l2)
    right = left[::-1] * np.array([-1.0, 1.0])
    return chain(left, right)


def tag(pts, role, s0, s1, grp=0):
    return dict(pts=np.asarray(pts, dtype=np.float64), role=role, win=(float(s0), float(s1)), grp=grp)


def build_heart():
    h = heart_path()
    return [tag(h, "coral", 0.0, 0.85),
            tag(xform(h, 0.80, 0.0, (0.0, 0.02)), "coral", 0.35, 1.0)]


def build_emblem():
    """Two overlapping hearts (coral and orange) holding a globe of light, with an olive sprig below."""
    h = heart_path()
    st = []
    st.append(tag(xform(h, 0.64, 0.17, (-0.13, 0.10)), "coral", 0.00, 0.42))
    st.append(tag(xform(h, 0.64, -0.17, (0.13, 0.10)), "orange", 0.08, 0.50))
    # the globe: outline, three latitudes, two pairs of longitudes and the axis
    gc, r = (0.0, 0.13), 0.175
    st.append(tag(ellipse(gc[0], gc[1], r, r), "sky", 0.40, 0.62))
    for k, dy in enumerate((-0.085, 0.0, 0.085)):
        rx = math.sqrt(r * r - dy * dy)
        st.append(tag(ellipse(gc[0], gc[1] + dy, rx, 0.022 * rx / r), "sky", 0.52 + 0.04 * k, 0.70 + 0.04 * k))
    for k, f in enumerate((0.38, 0.76)):
        st.append(tag(ellipse(gc[0], gc[1], r * f, r), "sky", 0.56 + 0.05 * k, 0.78 + 0.05 * k))
    st.append(tag(line((gc[0], gc[1] - r), (gc[0], gc[1] + r)), "sky", 0.58, 0.76))
    # the olive sprig: a curved stem with leaves on both sides and two olives
    stem = cubic((-0.34, -0.33), (-0.14, -0.47), (0.12, -0.47), (0.36, -0.29), 120)
    st.append(tag(stem, "olive", 0.64, 0.84))
    d = np.gradient(stem, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
    for j, s in enumerate(np.linspace(0.10, 0.92, 9)):
        i = int(s * (len(stem) - 1))
        side = 1.0 if j % 2 == 0 else -1.0
        base = stem[i]
        ln = 0.085 * (1.0 - 0.25 * abs(s - 0.5))
        dirv = d[i] * 0.55 + nrm[i] * side * 0.83
        dirv /= np.linalg.norm(dirv)
        tip = base + dirv * ln
        perp = np.array([-dirv[1], dirv[0]])
        mid = base + dirv * ln * 0.5
        leaf = chain(quad(base, mid + perp * ln * 0.30, tip, 20), quad(tip, mid - perp * ln * 0.30, base, 20))
        w0 = 0.72 + 0.26 * s
        st.append(tag(leaf, "olive", w0, min(w0 + 0.10, 1.0)))
    for k, s in enumerate((0.36, 0.68)):
        i = int(s * (len(stem) - 1))
        c = stem[i] - nrm[i] * 0.030 * (1 if k == 0 else -1)
        st.append(tag(ellipse(c[0], c[1], 0.014, 0.017), "olive", 0.90, 0.98))
    return st


def build_gate():
    """A gate (temple) of light, drawn line by line from the steps up; the two doors swing open later."""
    st = []
    seq = []
    # steps
    for k, (y, w) in enumerate(((-0.50, 0.50), (-0.465, 0.45), (-0.43, 0.40))):
        seq.append((line((-w, y), (w, y), 40), "gold", 0))
    # pillars, with their capitals
    for sx in (-1.0, 1.0):
        seq.append((line((sx * 0.36, -0.43), (sx * 0.36, 0.16), 40), "gold", 0))
        seq.append((line((sx * 0.25, -0.43), (sx * 0.25, 0.16), 40), "gold", 0))
    for sx in (-1.0, 1.0):
        seq.append((line((sx * 0.385, 0.16), (sx * 0.225, 0.16), 12), "gold", 0))
    # lintel and pediment, with a light at the apex
    seq.append((line((-0.42, 0.20), (0.42, 0.20), 40), "gold", 0))
    seq.append((line((-0.44, 0.245), (0.44, 0.245), 40), "gold", 0))
    seq.append((chain(line((-0.47, 0.245), (0.0, 0.48), 40), line((0.0, 0.48), (0.47, 0.245), 40)), "goldw", 0))
    seq.append((ellipse(0.0, 0.335, 0.04, 0.04), "goldw", 0))
    # the doorway arch (stays when the doors open)
    hw, spring, bot = GATE_DOOR
    seq.append((chain(line((-hw, bot), (-hw, spring), 30), ellipse(0.0, spring, hw, hw, 0.0, math.pi)[::-1],
                      line((hw, spring), (hw, bot), 30)), "goldw", 0))
    # the doors: arched tops, a centre seam and two panels each
    for g, sx in ((1, -1.0), (2, 1.0)):
        arc = ellipse(0.0, spring, hw, hw, 0.5 * math.pi, math.pi) if sx < 0 else ellipse(0.0, spring, hw, hw, 0.0, 0.5 * math.pi)
        door = chain(line((0.0, bot), (0.0, spring + hw), 30), arc if sx < 0 else arc[::-1])
        seq.append((door, "gold", g))
        for (y0, y1) in ((-0.39, -0.18), (-0.14, 0.04)):
            a, b = sx * 0.04, sx * 0.16
            seq.append((np.vstack([line((a, y0), (b, y0), 10), line((b, y0), (b, y1), 16)[1:],
                                   line((b, y1), (a, y1), 10)[1:], line((a, y1), (a, y0), 16)[1:]]), "gold", g))
    n = len(seq)
    for k, (p, role, g) in enumerate(seq):
        s0 = k / n * 0.92
        st.append(tag(p, role, s0, min(s0 + 1.6 / n, 1.0), g))
    return st


def _y_at(curve, x):
    o = np.argsort(curve[:, 0])
    return float(np.interp(x, curve[o, 0], curve[o, 1]))


def build_bridge():
    """A bridge of light (natural width about 4 x its height): deck, railing, an arch and hangers, drawn left to right."""
    st = []
    deck = cubic((-2.0, -0.10), (-0.7, 0.15), (0.7, 0.15), (2.0, -0.10), 160)
    rail = deck + np.array([0.0, 0.13])
    arch = cubic((-1.6, -0.50), (-1.0, 0.02), (1.0, 0.02), (1.6, -0.50), 160)

    def lr(p, a, b):
        return tag(p, "bridge", a, b)

    st.append(lr(deck, 0.0, 0.55))
    st.append(lr(rail, 0.08, 0.62))
    st.append(dict(lr(arch, 0.25, 0.80), role="goldw"))
    for x in np.arange(-1.35, 1.36, 0.27):
        ya, yd = _y_at(arch, x), _y_at(deck, x)
        if yd - ya > 0.02:
            s0 = 0.55 + 0.35 * (x + 1.4) / 2.8
            st.append(lr(line((x, ya), (x, yd), 12), s0, s0 + 0.10))
    for x in np.arange(-1.875, 1.88, 0.25):
        yd = _y_at(deck, x)
        s0 = 0.05 + 0.55 * (x + 2.0) / 4.0
        st.append(lr(line((x, yd), (x, yd + 0.13), 8), s0, s0 + 0.06))
    # two shore lamps
    for sx in (-1.0, 1.0):
        st.append(dict(lr(ellipse(sx * 2.0, 0.09, 0.035, 0.035), 0.60 if sx < 0 else 0.62, 0.70 if sx < 0 else 0.72),
                       role="goldw"))
    return st


BUILDERS = {"emblem": build_emblem, "heart": build_heart, "gate": build_gate, "bridge": build_bridge}


def build(kind, size_px, spacing_px=1.25):
    """Samples a symbol's strokes into evenly spaced points: (N, 4) [x, y, order, group] and (N,) role names."""
    strokes = BUILDERS[kind]()
    unit = max(spacing_px / max(size_px, 1.0), 1e-4)
    P, R = [], []
    for s in strokes:
        p = s["pts"]
        seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
        cum = np.concatenate([[0.0], np.cumsum(seg)])
        L = cum[-1]
        if L <= 0:
            continue
        n = max(int(L / unit), 2)
        u = np.linspace(0.0, L, n)
        x, y = np.interp(u, cum, p[:, 0]), np.interp(u, cum, p[:, 1])
        s0, s1 = s["win"]
        order = s0 + (s1 - s0) * u / L
        P.append(np.stack([x, y, order, np.full(n, float(s["grp"]))], axis=1))
        R += [s["role"]] * n
    return np.vstack(P), R
