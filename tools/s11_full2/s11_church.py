"""Song 11 v2: the waiting city on the summit of Zion, its paths of light, and the church of light
modelled on the main temple in Korea (Anthony's photographs; no lettering or logos).

Owned by the church thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

SHOTS = [
    # (t0, t1, keys [(t, pos, target)], fov, aperture)
    # A. the waiting city: wide over its edge (the title on the calm sky), down the avenue, close on the steps
    dict(name="city", kind="local", t0=0.0, t1=41.6, fov=50.0, aperture=0.02,
         keys=[(0.0, _v(0.0, Y + 16.0, FZ + 150.0), _v(0.0, Y + 34.0, CHURCH[2])),
                     (11.9, _v(0.0, Y + 11.0, FZ + 118.0), _v(0.0, Y + 22.0, CHURCH[2])),
                     (21.3, _v(0.0, Y + 3.4, FZ + 40.0), _v(0.0, Y + 6.0, FACADE_Z)),
                     (31.0, _v(-2.0, Y + 3.0, FZ + 22.0), _v(0.0, Y + 3.2, FACADE_Z)),
                     (38.8, _v(-1.0, Y + 3.2, FZ + 19.0), _v(0.0, Y + 4.0, FACADE_Z)),
                     (40.54, _v(0.0, Y + 7.0, FZ + 22.0), _v(0.0, Y + 30.0, FACADE_Z + 10.0)),
                     (41.6, _v(0.0, Y + 40.0, FZ + 50.0), _v(0.0, Y + 140.0, FZ + 10.0))]),
]


def _city():
    """Buildings of light on the summit plateau, the great avenue (toward +z) and the square left open."""
    r = np.random.default_rng(11)
    edges, wins, domes = [], [], []
    for gx in np.arange(-84.0, 85.0, 15.0):
        for gz in np.arange(-84.0, 85.0, 15.0):
            x, z = gx + r.uniform(-2.5, 2.5), gz + r.uniform(-2.5, 2.5)
            rad = np.hypot(x, z)
            if rad > 84.0:
                continue
            if abs(x) < 15.0 and z > -12.0:                       # the avenue and the square
                continue
            if abs(x) < 40.0 and -48.0 < z < 24.0:                # the church and its square
                continue
            w, d = r.uniform(7, 11), r.uniform(7, 11)
            h = r.uniform(7, 13) + 16.0 * np.exp(-rad / 45.0) * r.random()
            c = ZC + _v(x, SUMMIT, z)
            edges.append(_box(c, w, d, h, 0.35))
            wins.append(_windows(c, w, d, h))
            if r.random() < 0.18:
                domes.append(_dome(c + _v(0, h, 0), min(w, d) * 0.45, 0.4))
    E, W, D = np.concatenate(edges), np.concatenate(wins), np.concatenate(domes)
    pave = []
    for x in np.arange(-84.0, 85.0, 6.0):
        h = np.sqrt(max(86.0 ** 2 - x * x, 0.0))
        pave.append(_seg(ZC + _v(x, SUMMIT + 0.02, -h), ZC + _v(x, SUMMIT + 0.02, h), 0.6))
    for z in np.arange(-84.0, 85.0, 6.0):
        h = np.sqrt(max(86.0 ** 2 - z * z, 0.0))
        pave.append(_seg(ZC + _v(-h, SUMMIT + 0.02, z), ZC + _v(h, SUMMIT + 0.02, z), 0.6))
    PV = np.concatenate(pave)
    edge = []
    for sx in (-12.0, 12.0):
        edge.append(_seg((sx, SUMMIT + 0.05, FACADE_Z + 30.0), (sx, SUMMIT + 0.05, ZC[2] + R_TOP), 0.25))
    edge.append(_ring(SQUARE, 24.0, SUMMIT + 0.05, 0.25, -np.pi / 2, np.pi / 2))
    edge.append(_ring(SQUARE, 16.0, SUMMIT + 0.05, 0.3, -np.pi / 2, np.pi / 2))
    ED = np.concatenate(edge)
    lamps = []
    for z in np.arange(FACADE_Z + 24.0, ZC[2] + R_TOP, 7.0):
        lamps += [(-10.0, SUMMIT + 4.2, z), (10.0, SUMMIT + 4.2, z)]
    lamps = np.asarray(lamps)
    poles = np.concatenate([_seg((p[0], SUMMIT, p[2]), (p[0], SUMMIT + 4.0, p[2]), 0.2) for p in lamps])
    dimk = 0.55
    return [
        _batch(E, 0.16, lin("#f2c27a") * dimk, 0.8, emit=0.8),
        _batch(W, 0.30, lin("#ffcf86") * dimk, 0.8, kind="soft", emit=0.9, twinkle=0.2),
        _batch(D, 0.16, lin("#ffe0a8") * dimk, 0.8, emit=0.8),
        _batch(lamps, 0.9, lin("#ffcf8a"), 1.0, kind="soft", emit=2.5),
        _batch(lamps, 0.25, lin("#fff2d6"), 1.0, emit=4.0),
        _batch(poles, 0.12, lin("#e8c08a") * 0.6, 0.8, emit=1.0),
        _batch(PV, 0.10, lin("#e8b870") * 0.35, 0.7, emit=0.8),
        _batch(ED, 0.16, lin(GOLD2) * 0.8, 0.9, emit=1.6),
    ], [
        _batch(E, 0.22, lin(GOLD), 0.8, emit=1.2, birth=np.full(len(E), 69.4), fade=0.6, flash=3.0),
        _batch(W, 0.36, lin("#ffe6b0"), 0.8, kind="soft", emit=1.2, birth=np.full(len(W), 69.6), fade=0.8, flash=2.0),
    ]


# The church of light: the main temple in Korea (from Anthony's photographs), modelled in light.
# A tall curved front of blue glass (fifteen storeys) banded in white at every floor, a teal glass base that
# sweeps up toward the right, a stone entrance portal (left of centre) with steps, the tall white ladder blade
# standing at the left end with its slanted top, short white fins in threes on both edges, a white column at
# the right edge, a louvred canopy on the roof with a mast, the plain white tower behind, pines in front.
# No lettering or logos are drawn.
NF, FH = 15, 3.6                    # storeys and storey height (metres)
CH_HT = NF * FH                     # 54 m
CH_W2 = 28.0                        # half the width of the curved front
CH_SAG = 5.0                        # how far the middle of the front bulges forward
CH_RC = (CH_W2 ** 2 + CH_SAG ** 2) / (2.0 * CH_SAG)
CH_DEPTH = 22.0
PORTAL_X = -5.6                     # the entrance portal stands left of centre, as on the real building


def front_z(x):
    """z of the curved glass front at x (its middle is FACADE_Z)."""
    return FACADE_Z - CH_RC + np.sqrt(np.maximum(CH_RC ** 2 - np.asarray(x, np.float64) ** 2, 0.0))


def _arc_pts(y, step, x0=-CH_W2, x1=CH_W2, out=0.0):
    n = max(int((x1 - x0) / step), 2)
    x = np.linspace(x0, x1, n)
    return np.stack([x, np.full(n, y), front_z(x) + out], 1)


def _base_top(x):
    """Top of the teal glass base: two storeys on the right, sweeping down toward the left end."""
    u = np.clip((np.asarray(x) + CH_W2) / (2 * CH_W2), 0.0, 1.0)
    return SUMMIT + FH * (0.9 + 1.1 * np.sin(0.5 * np.pi * u) ** 0.7)


def _church():
    r = np.random.default_rng(13)
    y0 = SUMMIT
    zb = FACADE_Z - CH_SAG - CH_DEPTH           # the back face
    zs = FACADE_Z - CH_SAG                      # where the sides meet the front
    lines, white, glass, gcol, stone, warm, green, trunk = [], [], [], [], [], [], [], []
    # -- the floor bands, all round (bright white on the front)
    for k in range(NF + 1):
        y = y0 + k * FH + (1.2 if k == 0 else 0.0)
        white.append(_arc_pts(y, 0.07, out=0.08))
        for sx in (-CH_W2, CH_W2):
            lines.append(_seg((sx, y, zs), (sx, y, zb), 0.12))
        lines.append(_seg((-CH_W2, y, zb), (CH_W2, y, zb), 0.2))
    # -- mullions on the curved front and the sides
    for x in np.arange(-CH_W2, CH_W2 + 0.01, 1.4):
        z = float(front_z(x))
        lines.append(_seg((x, y0 + 1.2, z + 0.05), (x, y0 + CH_HT, z + 0.05), 0.11))
    for sx in (-CH_W2, CH_W2):
        for z in np.arange(zb, zs + 0.01, 1.4):
            lines.append(_seg((sx, y0 + 1.2, z), (sx, y0 + CH_HT, z), 0.16))
    # -- the glass: blue panes, teal at the base, a few panes lit warm from within
    for k in range(NF):
        for x in np.arange(-CH_W2 + 0.7, CH_W2, 1.4):
            for sub in range(3):
                px = x + r.uniform(-0.55, 0.55)
                py = y0 + k * FH + 0.4 + r.uniform(0.0, FH - 0.6)
                if py < y0 + 1.2:
                    continue
                glass.append((px, py, float(front_z(px)) - 0.02))
                teal = py < _base_top(px)
                hi = (py - y0) / CH_HT
                c = lin("#4fd8c8") if teal else lin("#3f7cff") * (0.75 + 0.5 * hi) + lin("#a8c8ff") * 0.25 * hi
                if not teal and r.random() < 0.07:
                    c = lin("#ffd590")
                gcol.append(c)
    # the line where the teal base meets the blue (the sweep)
    xs = np.linspace(-CH_W2, CH_W2, 500)
    white.append(np.stack([xs, _base_top(xs), front_z(xs) + 0.09], 1))
    # side glass (fewer: seen at an angle)
    for sx in (-CH_W2, CH_W2):
        for k in range(NF):
            for z in np.arange(zb + 0.7, zs, 1.4):
                py = y0 + k * FH + r.uniform(0.6, FH - 0.4)
                glass.append((sx + 0.02 * np.sign(sx), py, z + r.uniform(-0.5, 0.5)))
                gcol.append(lin("#3f6fe0") * 0.8)
    # -- the white podium along the foot
    white.append(_arc_pts(y0 + 0.6, 0.12, out=0.4))
    white.append(_arc_pts(y0 + 0.05, 0.12, out=0.6))
    # -- the white column at the right edge (and a slimmer one at the left end of the glass)
    for dx in (0.0, 0.5, 1.0):
        white.append(_seg((CH_W2 + dx, y0, zs + 0.3), (CH_W2 + dx, y0 + CH_HT + 2.0, zs + 0.3), 0.07))
    white.append(_seg((-CH_W2, y0, zs + 0.2), (-CH_W2, y0 + CH_HT, zs + 0.2), 0.07))
    # -- the tall white ladder blade at the left end, its top slanting up to the left
    bx0, bx1, bz = -CH_W2 - 7.5, -CH_W2 - 2.0, zs - 1.0
    top0, top1 = y0 + CH_HT + 14.0, y0 + CH_HT + 4.0
    for dz in (-0.7, 0.7):
        white.append(_seg((bx0, y0, bz + dz), (bx0, top0, bz + dz), 0.07))
        white.append(_seg((bx1, y0, bz + dz), (bx1, top1, bz + dz), 0.07))
        white.append(_seg((bx0, top0, bz + dz), (bx1, top1, bz + dz), 0.07))
        white.append(_seg((bx0 + 0.6, y0 + 4.0, bz + dz), (bx0 + 0.6, top0 - 2.0, bz + dz), 0.12))
        white.append(_seg((bx1 - 0.6, y0 + 4.0, bz + dz), (bx1 - 0.6, top1 - 1.0, bz + dz), 0.12))
        for y in np.arange(y0 + 2.0 * FH, top1 - 1.0, 2.0 * FH):
            white.append(_seg((bx0, y, bz + dz), (bx1, y, bz + dz), 0.07))
            white.append(_seg((bx0, y + 0.5, bz + dz), (bx1, y + 0.5, bz + dz), 0.09))
    # the blade's link to the building at each rung
    for y in np.arange(y0 + 2.0 * FH, top1 - 1.0, 2.0 * FH):
        white.append(_seg((bx1, y, bz), (-CH_W2, y, bz + 0.6), 0.1))
    # -- short white fins in threes, standing out from both edges at several storeys
    for side, floors in ((-1.0, (3, 6, 9, 12)), (1.0, (2, 5, 8, 11, 13))):
        for f in floors:
            for j in range(3):
                y = y0 + f * FH + 0.6 + 0.55 * j
                x0 = side * (CH_W2 - 3.0)
                x1 = side * (CH_W2 + 2.6)
                z = float(front_z(x0)) + 0.4
                white.append(_seg((x0, y, z), (x1, y, z - 0.6), 0.06))
    # -- the roof: a louvred white canopy following the curve, on posts, and a mast
    yr = y0 + CH_HT + 3.4
    white.append(_arc_pts(yr, 0.1, x0=-CH_W2 - 1.0, x1=CH_W2 + 1.0, out=1.2))
    white.append(_seg((-CH_W2 - 1.0, yr, zb + 3.0), (CH_W2 + 1.0, yr, zb + 3.0), 0.1))
    for x in np.arange(-CH_W2, CH_W2 + 0.1, 1.1):
        z = float(front_z(x)) + 1.2
        white.append(_seg((x, yr, z), (x, yr, zb + 3.0), 0.16))
    for x in np.arange(-CH_W2, CH_W2 + 0.1, 7.0):
        z = float(front_z(x)) + 0.6
        white.append(_seg((x, y0 + CH_HT, z), (x, yr, z), 0.1))
    lines.append(_seg((-CH_W2, y0 + CH_HT + 1.2, zs), (CH_W2, y0 + CH_HT + 1.2, zs), 0.1))
    white.append(_seg((4.0, yr, zb + 6.0), (4.0, yr + 9.0, zb + 6.0), 0.06))
    # -- the stone entrance portal: a tall frame of four storeys standing out from the glass, glass within,
    # a canopy over the doors, the doors lit warm, steps down to the square
    pw, ph = 6.2, 4.0 * FH + 0.8
    pz = float(front_z(PORTAL_X)) + 1.6
    for dx in np.linspace(-pw, pw, 34):
        for yy in np.linspace(y0, y0 + ph, 70):
            edge = abs(abs(dx) - pw) < 1.4 or yy > y0 + ph - 1.6
            if edge:
                stone.append((PORTAL_X + dx + r.uniform(-0.1, 0.1), yy + r.uniform(-0.1, 0.1), pz + r.uniform(0, 0.2)))
    for dx in (-pw, -pw + 1.4, pw - 1.4, pw):
        lines.append(_seg((PORTAL_X + dx, y0, pz + 0.25), (PORTAL_X + dx, y0 + ph, pz + 0.25), 0.08))
    lines.append(_seg((PORTAL_X - pw, y0 + ph, pz + 0.25), (PORTAL_X + pw, y0 + ph, pz + 0.25), 0.08))
    lines.append(_seg((PORTAL_X - pw + 1.4, y0 + ph - 1.6, pz + 0.25), (PORTAL_X + pw - 1.4, y0 + ph - 1.6, pz + 0.25), 0.08))
    for x in np.arange(PORTAL_X - pw + 1.4, PORTAL_X + pw - 1.3, 1.2):
        white.append(_seg((x, y0 + 5.2, pz - 0.6), (x, y0 + ph - 1.6, pz - 0.6), 0.1))
    for y in np.arange(y0 + 5.2, y0 + ph - 1.5, 1.8):
        white.append(_seg((PORTAL_X - pw + 1.4, y, pz - 0.6), (PORTAL_X + pw - 1.4, y, pz - 0.6), 0.1))
    white.append(_seg((PORTAL_X - pw + 1.0, y0 + 4.8, pz + 1.6), (PORTAL_X + pw - 1.0, y0 + 4.8, pz + 1.6), 0.06))
    white.append(_seg((PORTAL_X - pw + 1.0, y0 + 4.8, pz - 0.6), (PORTAL_X - pw + 1.0, y0 + 4.8, pz + 1.6), 0.06))
    white.append(_seg((PORTAL_X + pw - 1.0, y0 + 4.8, pz - 0.6), (PORTAL_X + pw - 1.0, y0 + 4.8, pz + 1.6), 0.06))
    for dx in np.linspace(-3.4, 3.4, 30):
        for yy in np.linspace(y0 + 0.4, y0 + 4.2, 18):
            warm.append((PORTAL_X + dx, yy, pz - 0.7))
    # -- the steps where the choir stands (broad white stone steps before the front)
    for i, (yy, zz) in enumerate(CHOIR_STEPS):
        white.append(_seg((-13.0, yy - 0.05, zz + 0.65), (13.0, yy - 0.05, zz + 0.65), 0.12))
        white.append(_seg((-13.0, yy - 0.6, zz + 0.66), (-13.0, yy - 0.05, zz + 0.66), 0.1))
        white.append(_seg((13.0, yy - 0.6, zz + 0.66), (13.0, yy - 0.05, zz + 0.66), 0.1))
    # -- the plain white tower behind, with its window strips and a box on top
    tx0, tx1, tz1 = -12.0, 15.0, zb - 1.0
    tz0 = tz1 - 15.0
    th = CH_HT + 9.0
    c = _v((tx0 + tx1) / 2.0, y0, (tz0 + tz1) / 2.0)
    lines.append(_box(c, tx1 - tx0, tz1 - tz0, th, 0.2))
    for k in range(1, 17):
        y = y0 + k * th / 17.0
        lines.append(_seg((tx0, y, tz1 + 0.05), (tx1, y, tz1 + 0.05), 0.35))
        for z in (tz0, tz1):
            pass
        for sx in (tx0, tx1):
            lines.append(_seg((sx, y, tz0), (sx, y, tz1), 0.35))
    lines.append(_box(_v(c[0] + 3.0, y0 + th, c[2]), 9.0, 7.0, 5.0, 0.2))
    # -- pines of light before the building (gently curving trunks, flat layered crowns)
    for (px, pzz, h, lean) in ((-21.0, FACADE_Z + 9.0, 9.0, -0.25), (-15.0, FACADE_Z + 12.0, 7.0, 0.2),
                               (20.0, FACADE_Z + 8.0, 10.0, 0.3), (25.0, FACADE_Z + 12.0, 7.5, -0.2)):
        u = np.linspace(0.0, 1.0, 120)
        tx = px + lean * h * u ** 1.5 + 0.4 * np.sin(3.0 * u)
        trunk.append(np.stack([tx, y0 + h * u, np.full(120, pzz)], 1))
        for j, (fu, fr) in enumerate(((0.55, 2.2), (0.72, 2.8), (0.86, 2.4), (1.0, 1.7))):
            cx = px + lean * h * fu ** 1.5 + (1.2 if j % 2 else -1.0)
            n = 260
            a = r.random(n) * 2 * np.pi
            rr = fr * np.sqrt(r.random(n))
            green.append(np.stack([cx + rr * np.cos(a), y0 + h * fu + 0.5 * r.random(n), pzz + 0.7 * rr * np.sin(a)], 1))
    W = np.concatenate(white)
    L = np.concatenate(lines)
    G = np.asarray(glass)
    GC = np.asarray(gcol)
    S = np.asarray(stone)
    WM = np.asarray(warm)
    GR = np.concatenate(green)
    TR = np.concatenate(trunk)
    return [
        _batch(W, 0.07, lin("#f4f8ff"), 1.0, emit=2.0, twinkle=0.15),
        _batch(L, 0.06, lin("#cfdcff") * 0.8, 0.9, emit=1.3),
        _batch(G, 0.85, GC, 0.33, kind="soft", emit=1.2),
        _batch(G[::2], 0.05, GC[::2] * 1.4, 0.8, emit=1.8, twinkle=0.4),
        _batch(S, 0.18, lin("#e8c49a"), 0.6, kind="soft", emit=1.2),
        _batch(WM, 0.35, lin("#ffcf80"), 0.5, kind="soft", emit=2.0),
        _batch(GR, 0.12, lin("#9fe0a0") * 0.7 + lin(GOLD) * 0.3, 0.8, emit=1.4, twinkle=0.5),
        _batch(TR, 0.08, lin("#e0b080"), 0.9, emit=1.3),
    ]


def church_glow(t):
    """The church of light: soft in the waiting dawn, shining out on "to the great Church of God!"."""
    return (0.45 + 0.2 * _sc(20.0, 24.0, t) + 0.8 * hit_pulse(t, [HIT["stream"]], fall=2.5)
            + 0.5 * _sc(70.0, 75.0, t) + 0.2 * beat_pulse(t))


class Church:
    static = True

    def __init__(self):
        self.b = _church()

    def sample(self, t):
        return self.b

    def gain(self, t):
        return city_k(t) * church_glow(t)


def _paths():
    """Paths of light reaching out from the waiting city toward every horizon (from 0:11.9)."""
    out, birth = [], []
    for k, az in enumerate(np.radians([0, 40, 80, 125, 165, 200, 240, 280, 320])):
        d = _v(np.sin(az), 0.0, np.cos(az))
        pts = []
        p = ZC + d * R_TOP + _v(0, SUMMIT, 0)
        q = ZC + d * (tier_r(0) + 6.0) + _v(0, 0.3, 0)
        pts.append(_seg(p, q, 0.45))
        p = q
        pts.append(_seg(p, p + d * 2400.0, 0.9))
        P = np.concatenate(pts)
        L = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        out.append(P)
        birth.append(11.9 + 1.2 * k / 9.0 + L / 70.0)
    P, B = np.concatenate(out), np.concatenate(birth)
    return [_batch(P, 0.30, lin(GOLD2), 0.85, emit=2.0, birth=B, fade=0.35, flash=3.0, twinkle=0.4)]


# The church of light: the main temple in Korea (from Anthony's photographs), modelled in light.
# A tall curved front of blue glass (fifteen storeys) banded in white at every floor, a teal glass base that
# sweeps up toward the right, a stone entrance portal (left of centre) with steps, the tall white ladder blade
# standing at the left end with its slanted top, short white fins in threes on both edges, a white column at
# the right edge, a louvred canopy on the roof with a mast, the plain white tower behind, pines in front.
# No lettering or logos are drawn.
NF, FH = 15, 3.6                    # storeys and storey height (metres)
CH_HT = NF * FH                     # 54 m
CH_W2 = 28.0                        # half the width of the curved front
CH_SAG = 5.0                        # how far the middle of the front bulges forward
CH_RC = (CH_W2 ** 2 + CH_SAG ** 2) / (2.0 * CH_SAG)
CH_DEPTH = 22.0
PORTAL_X = -5.6                     # the entrance portal stands left of centre, as on the real building


def front_z(x):
    """z of the curved glass front at x (its middle is FACADE_Z)."""
    return FACADE_Z - CH_RC + np.sqrt(np.maximum(CH_RC ** 2 - np.asarray(x, np.float64) ** 2, 0.0))


def _arc_pts(y, step, x0=-CH_W2, x1=CH_W2, out=0.0):
    n = max(int((x1 - x0) / step), 2)
    x = np.linspace(x0, x1, n)
    return np.stack([x, np.full(n, y), front_z(x) + out], 1)


def _base_top(x):
    """Top of the teal glass base: two storeys on the right, sweeping down toward the left end."""
    u = np.clip((np.asarray(x) + CH_W2) / (2 * CH_W2), 0.0, 1.0)
    return SUMMIT + FH * (0.9 + 1.1 * np.sin(0.5 * np.pi * u) ** 0.7)


def _church():
    r = np.random.default_rng(13)
    y0 = SUMMIT
    zb = FACADE_Z - CH_SAG - CH_DEPTH           # the back face
    zs = FACADE_Z - CH_SAG                      # where the sides meet the front
    lines, white, glass, gcol, stone, warm, green, trunk = [], [], [], [], [], [], [], []
    # -- the floor bands, all round (bright white on the front)
    for k in range(NF + 1):
        y = y0 + k * FH + (1.2 if k == 0 else 0.0)
        white.append(_arc_pts(y, 0.07, out=0.08))
        for sx in (-CH_W2, CH_W2):
            lines.append(_seg((sx, y, zs), (sx, y, zb), 0.12))
        lines.append(_seg((-CH_W2, y, zb), (CH_W2, y, zb), 0.2))
    # -- mullions on the curved front and the sides
    for x in np.arange(-CH_W2, CH_W2 + 0.01, 1.4):
        z = float(front_z(x))
        lines.append(_seg((x, y0 + 1.2, z + 0.05), (x, y0 + CH_HT, z + 0.05), 0.11))
    for sx in (-CH_W2, CH_W2):
        for z in np.arange(zb, zs + 0.01, 1.4):
            lines.append(_seg((sx, y0 + 1.2, z), (sx, y0 + CH_HT, z), 0.16))
    # -- the glass: blue panes, teal at the base, a few panes lit warm from within
    for k in range(NF):
        for x in np.arange(-CH_W2 + 0.7, CH_W2, 1.4):
            for sub in range(3):
                px = x + r.uniform(-0.55, 0.55)
                py = y0 + k * FH + 0.4 + r.uniform(0.0, FH - 0.6)
                if py < y0 + 1.2:
                    continue
                glass.append((px, py, float(front_z(px)) - 0.02))
                teal = py < _base_top(px)
                hi = (py - y0) / CH_HT
                c = lin("#4fd8c8") if teal else lin("#3f7cff") * (0.75 + 0.5 * hi) + lin("#a8c8ff") * 0.25 * hi
                if not teal and r.random() < 0.07:
                    c = lin("#ffd590")
                gcol.append(c)
    # the line where the teal base meets the blue (the sweep)
    xs = np.linspace(-CH_W2, CH_W2, 500)
    white.append(np.stack([xs, _base_top(xs), front_z(xs) + 0.09], 1))
    # side glass (fewer: seen at an angle)
    for sx in (-CH_W2, CH_W2):
        for k in range(NF):
            for z in np.arange(zb + 0.7, zs, 1.4):
                py = y0 + k * FH + r.uniform(0.6, FH - 0.4)
                glass.append((sx + 0.02 * np.sign(sx), py, z + r.uniform(-0.5, 0.5)))
                gcol.append(lin("#3f6fe0") * 0.8)
    # -- the white podium along the foot
    white.append(_arc_pts(y0 + 0.6, 0.12, out=0.4))
    white.append(_arc_pts(y0 + 0.05, 0.12, out=0.6))
    # -- the white column at the right edge (and a slimmer one at the left end of the glass)
    for dx in (0.0, 0.5, 1.0):
        white.append(_seg((CH_W2 + dx, y0, zs + 0.3), (CH_W2 + dx, y0 + CH_HT + 2.0, zs + 0.3), 0.07))
    white.append(_seg((-CH_W2, y0, zs + 0.2), (-CH_W2, y0 + CH_HT, zs + 0.2), 0.07))
    # -- the tall white ladder blade at the left end, its top slanting up to the left
    bx0, bx1, bz = -CH_W2 - 7.5, -CH_W2 - 2.0, zs - 1.0
    top0, top1 = y0 + CH_HT + 14.0, y0 + CH_HT + 4.0
    for dz in (-0.7, 0.7):
        white.append(_seg((bx0, y0, bz + dz), (bx0, top0, bz + dz), 0.07))
        white.append(_seg((bx1, y0, bz + dz), (bx1, top1, bz + dz), 0.07))
        white.append(_seg((bx0, top0, bz + dz), (bx1, top1, bz + dz), 0.07))
        white.append(_seg((bx0 + 0.6, y0 + 4.0, bz + dz), (bx0 + 0.6, top0 - 2.0, bz + dz), 0.12))
        white.append(_seg((bx1 - 0.6, y0 + 4.0, bz + dz), (bx1 - 0.6, top1 - 1.0, bz + dz), 0.12))
        for y in np.arange(y0 + 2.0 * FH, top1 - 1.0, 2.0 * FH):
            white.append(_seg((bx0, y, bz + dz), (bx1, y, bz + dz), 0.07))
            white.append(_seg((bx0, y + 0.5, bz + dz), (bx1, y + 0.5, bz + dz), 0.09))
    # the blade's link to the building at each rung
    for y in np.arange(y0 + 2.0 * FH, top1 - 1.0, 2.0 * FH):
        white.append(_seg((bx1, y, bz), (-CH_W2, y, bz + 0.6), 0.1))
    # -- short white fins in threes, standing out from both edges at several storeys
    for side, floors in ((-1.0, (3, 6, 9, 12)), (1.0, (2, 5, 8, 11, 13))):
        for f in floors:
            for j in range(3):
                y = y0 + f * FH + 0.6 + 0.55 * j
                x0 = side * (CH_W2 - 3.0)
                x1 = side * (CH_W2 + 2.6)
                z = float(front_z(x0)) + 0.4
                white.append(_seg((x0, y, z), (x1, y, z - 0.6), 0.06))
    # -- the roof: a louvred white canopy following the curve, on posts, and a mast
    yr = y0 + CH_HT + 3.4
    white.append(_arc_pts(yr, 0.1, x0=-CH_W2 - 1.0, x1=CH_W2 + 1.0, out=1.2))
    white.append(_seg((-CH_W2 - 1.0, yr, zb + 3.0), (CH_W2 + 1.0, yr, zb + 3.0), 0.1))
    for x in np.arange(-CH_W2, CH_W2 + 0.1, 1.1):
        z = float(front_z(x)) + 1.2
        white.append(_seg((x, yr, z), (x, yr, zb + 3.0), 0.16))
    for x in np.arange(-CH_W2, CH_W2 + 0.1, 7.0):
        z = float(front_z(x)) + 0.6
        white.append(_seg((x, y0 + CH_HT, z), (x, yr, z), 0.1))
    lines.append(_seg((-CH_W2, y0 + CH_HT + 1.2, zs), (CH_W2, y0 + CH_HT + 1.2, zs), 0.1))
    white.append(_seg((4.0, yr, zb + 6.0), (4.0, yr + 9.0, zb + 6.0), 0.06))
    # -- the stone entrance portal: a tall frame of four storeys standing out from the glass, glass within,
    # a canopy over the doors, the doors lit warm, steps down to the square
    pw, ph = 6.2, 4.0 * FH + 0.8
    pz = float(front_z(PORTAL_X)) + 1.6
    for dx in np.linspace(-pw, pw, 34):
        for yy in np.linspace(y0, y0 + ph, 70):
            edge = abs(abs(dx) - pw) < 1.4 or yy > y0 + ph - 1.6
            if edge:
                stone.append((PORTAL_X + dx + r.uniform(-0.1, 0.1), yy + r.uniform(-0.1, 0.1), pz + r.uniform(0, 0.2)))
    for dx in (-pw, -pw + 1.4, pw - 1.4, pw):
        lines.append(_seg((PORTAL_X + dx, y0, pz + 0.25), (PORTAL_X + dx, y0 + ph, pz + 0.25), 0.08))
    lines.append(_seg((PORTAL_X - pw, y0 + ph, pz + 0.25), (PORTAL_X + pw, y0 + ph, pz + 0.25), 0.08))
    lines.append(_seg((PORTAL_X - pw + 1.4, y0 + ph - 1.6, pz + 0.25), (PORTAL_X + pw - 1.4, y0 + ph - 1.6, pz + 0.25), 0.08))
    for x in np.arange(PORTAL_X - pw + 1.4, PORTAL_X + pw - 1.3, 1.2):
        white.append(_seg((x, y0 + 5.2, pz - 0.6), (x, y0 + ph - 1.6, pz - 0.6), 0.1))
    for y in np.arange(y0 + 5.2, y0 + ph - 1.5, 1.8):
        white.append(_seg((PORTAL_X - pw + 1.4, y, pz - 0.6), (PORTAL_X + pw - 1.4, y, pz - 0.6), 0.1))
    white.append(_seg((PORTAL_X - pw + 1.0, y0 + 4.8, pz + 1.6), (PORTAL_X + pw - 1.0, y0 + 4.8, pz + 1.6), 0.06))
    white.append(_seg((PORTAL_X - pw + 1.0, y0 + 4.8, pz - 0.6), (PORTAL_X - pw + 1.0, y0 + 4.8, pz + 1.6), 0.06))
    white.append(_seg((PORTAL_X + pw - 1.0, y0 + 4.8, pz - 0.6), (PORTAL_X + pw - 1.0, y0 + 4.8, pz + 1.6), 0.06))
    for dx in np.linspace(-3.4, 3.4, 30):
        for yy in np.linspace(y0 + 0.4, y0 + 4.2, 18):
            warm.append((PORTAL_X + dx, yy, pz - 0.7))
    # -- the steps where the choir stands (broad white stone steps before the front)
    for i, (yy, zz) in enumerate(CHOIR_STEPS):
        white.append(_seg((-13.0, yy - 0.05, zz + 0.65), (13.0, yy - 0.05, zz + 0.65), 0.12))
        white.append(_seg((-13.0, yy - 0.6, zz + 0.66), (-13.0, yy - 0.05, zz + 0.66), 0.1))
        white.append(_seg((13.0, yy - 0.6, zz + 0.66), (13.0, yy - 0.05, zz + 0.66), 0.1))
    # -- the plain white tower behind, with its window strips and a box on top
    tx0, tx1, tz1 = -12.0, 15.0, zb - 1.0
    tz0 = tz1 - 15.0
    th = CH_HT + 9.0
    c = _v((tx0 + tx1) / 2.0, y0, (tz0 + tz1) / 2.0)
    lines.append(_box(c, tx1 - tx0, tz1 - tz0, th, 0.2))
    for k in range(1, 17):
        y = y0 + k * th / 17.0
        lines.append(_seg((tx0, y, tz1 + 0.05), (tx1, y, tz1 + 0.05), 0.35))
        for z in (tz0, tz1):
            pass
        for sx in (tx0, tx1):
            lines.append(_seg((sx, y, tz0), (sx, y, tz1), 0.35))
    lines.append(_box(_v(c[0] + 3.0, y0 + th, c[2]), 9.0, 7.0, 5.0, 0.2))
    # -- pines of light before the building (gently curving trunks, flat layered crowns)
    for (px, pzz, h, lean) in ((-21.0, FACADE_Z + 9.0, 9.0, -0.25), (-15.0, FACADE_Z + 12.0, 7.0, 0.2),
                               (20.0, FACADE_Z + 8.0, 10.0, 0.3), (25.0, FACADE_Z + 12.0, 7.5, -0.2)):
        u = np.linspace(0.0, 1.0, 120)
        tx = px + lean * h * u ** 1.5 + 0.4 * np.sin(3.0 * u)
        trunk.append(np.stack([tx, y0 + h * u, np.full(120, pzz)], 1))
        for j, (fu, fr) in enumerate(((0.55, 2.2), (0.72, 2.8), (0.86, 2.4), (1.0, 1.7))):
            cx = px + lean * h * fu ** 1.5 + (1.2 if j % 2 else -1.0)
            n = 260
            a = r.random(n) * 2 * np.pi
            rr = fr * np.sqrt(r.random(n))
            green.append(np.stack([cx + rr * np.cos(a), y0 + h * fu + 0.5 * r.random(n), pzz + 0.7 * rr * np.sin(a)], 1))
    W = np.concatenate(white)
    L = np.concatenate(lines)
    G = np.asarray(glass)
    GC = np.asarray(gcol)
    S = np.asarray(stone)
    WM = np.asarray(warm)
    GR = np.concatenate(green)
    TR = np.concatenate(trunk)
    return [
        _batch(W, 0.07, lin("#f4f8ff"), 1.0, emit=2.0, twinkle=0.15),
        _batch(L, 0.06, lin("#cfdcff") * 0.8, 0.9, emit=1.3),
        _batch(G, 0.85, GC, 0.33, kind="soft", emit=1.2),
        _batch(G[::2], 0.05, GC[::2] * 1.4, 0.8, emit=1.8, twinkle=0.4),
        _batch(S, 0.18, lin("#e8c49a"), 0.6, kind="soft", emit=1.2),
        _batch(WM, 0.35, lin("#ffcf80"), 0.5, kind="soft", emit=2.0),
        _batch(GR, 0.12, lin("#9fe0a0") * 0.7 + lin(GOLD) * 0.3, 0.8, emit=1.4, twinkle=0.5),
        _batch(TR, 0.08, lin("#e0b080"), 0.9, emit=1.3),
    ]


def church_glow(t):
    """The church of light: soft in the waiting dawn, shining out on "to the great Church of God!"."""
    return (0.45 + 0.2 * _sc(20.0, 24.0, t) + 0.8 * hit_pulse(t, [HIT["stream"]], fall=2.5)
            + 0.5 * _sc(70.0, 75.0, t) + 0.2 * beat_pulse(t))


class Church:
    static = True

    def __init__(self):
        self.b = _church()

    def sample(self, t):
        return self.b

    def gain(self, t):
        return city_k(t) * church_glow(t)


def _paths():
    """Paths of light reaching out from the waiting city toward every horizon (from 0:11.9)."""
    out, birth = [], []
    for k, az in enumerate(np.radians([0, 40, 80, 125, 165, 200, 240, 280, 320])):
        d = _v(np.sin(az), 0.0, np.cos(az))
        pts = []
        p = ZC + d * R_TOP + _v(0, SUMMIT, 0)
        q = ZC + d * (tier_r(0) + 6.0) + _v(0, 0.3, 0)
        pts.append(_seg(p, q, 0.45))
        p = q
        pts.append(_seg(p, p + d * 2400.0, 0.9))
        P = np.concatenate(pts)
        L = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        out.append(P)
        birth.append(11.9 + 1.2 * k / 9.0 + L / 70.0)
    P, B = np.concatenate(out), np.concatenate(birth)
    return [_batch(P, 0.30, lin(GOLD2), 0.85, emit=2.0, birth=B, fade=0.35, flash=3.0, twinkle=0.4)]


def add(scene):
    cdim, cgold = _city()
    scene.add("city dim", Static(cdim, lambda t: city_k(t) * (0.8 + 0.3 * beat_pulse(t) * _sc(20, 22, t))))
    scene.add("city gold", Static(cgold, city_k))
    scene.add("church", Church())
    scene.add("paths", Static(_paths(), lambda t: local_k(t) * (1.0 - 0.75 * _sc(40.0, 42.0, t))))
