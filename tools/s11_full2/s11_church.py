"""Song 11 v2: the waiting city on the summit of Zion, its paths of light, and the church of light
modelled on the main temple in Korea (Anthony's photographs; no lettering or logos).

Owned by the church thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.
"""
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from songs.s11_full2 import *  # noqa: F401,F403
from p3d.api import Mask
import songs.s11_full2 as H

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

# The music-video edit: one shot per block the church owns (the core's EDIT; times taken from it so they
# always match). Each block a different, striking angle; the core paces every move with the music (fast on
# hits and loud passages), shakes it on the slams and punches the lens on the hits. While a phrase is on
# screen the church sits low in the frame so the words ride over calm sky.
_B = blocks_of("church")


def _shot(i, name, keys, fov=50.0, aperture=0.02, **kw):
    """Block i's shot; keys [(fraction of the block 0..1, camera, target)]."""
    if i >= len(_B):
        return None
    t0, t1, _note = _B[i]
    return dict(name=name, kind="local", t0=t0, t1=t1, fov=fov, aperture=aperture,
                keys=[(t0 + f * (t1 - t0), _v(*p), _v(*q)) for f, p, q in keys], **kw)


_STEPS_FOCUS = _v(0.0, Y + 2.2, FZ + 3.0)
SHOTS = [
    # 0:00 the title over the waiting city: wide and far, the roof under the title's last line (quiet: a drift)
    _shot(0, "city", [(0.0, (0.0, Y + 40.0, FZ + 270.0), (0.0, Y + 116.0, FZ - 13.0)),
                      (0.87, (0.0, Y + 37.0, FZ + 250.0), (0.0, Y + 111.0, FZ - 13.0)),
                      (1.0, (0.0, Y + 36.0, FZ + 246.0), (0.0, Y + 104.0, FZ - 13.0))], pace="linear"),
    # 0:11.9 the paths reach out: low over the plateau's edge, sweeping in from the left toward the city
    _shot(1, "city", [(0.0, (-75.0, Y + 14.0, FZ + 160.0), (0.0, Y + 30.0, FZ - 13.0)),
                      (1.0, (-30.0, Y + 9.0, FZ + 118.0), (0.0, Y + 28.0, FZ - 13.0))], fov=56.0),
    # 0:16.7 down the great avenue: skimming low between the lamps, looking up at the church
    _shot(2, "city", [(0.0, (0.0, Y + 2.2, FZ + 140.0), (0.0, Y + 30.0, FZ - 13.0)),
                      (1.0, (0.0, Y + 3.2, FZ + 72.0), (0.0, Y + 34.0, FZ - 13.0))], fov=54.0),
    # 0:21.52 call 1: low from the right of the steps as the choir forms out of the light, the glass above
    _shot(3, "city", [(0.0, (16.0, Y + 1.4, FZ + 32.0), (-1.0, Y + 9.0, FZ)),
                      (1.0, (7.0, Y + 2.4, FZ + 24.0), (-1.0, Y + 11.0, FZ))], fov=52.0, aperture=0.04,
          focus=_STEPS_FOCUS),
    # 0:31.11 call 2: from the choir a crane rises past the white floor bands toward the name
    _shot(4, "city", [(0.0, (-4.0, Y + 3.0, FZ + 28.0), (-1.0, Y + 6.0, FZ)),
                      (1.0, (2.0, Y + 34.0, FZ + 40.0), (6.0, Y + 46.0, FZ))], fov=48.0),
    # 0:38.24 the brightest moment: a low hero angle up the curved glass from its left end, rising with it
    _shot(5, "church_cut", [(0.0, (-21.0, Y + 1.6, FZ + 9.0), (10.0, Y + 42.0, FZ - 4.0)),
                            (1.0, (-16.0, Y + 22.0, FZ + 12.0), (8.0, Y + 82.0, FZ - 10.0))], fov=58.0),
    # 0:40.54 Father's bell-like pulse: straight down over the roof canopy, pulling away fast
    _shot(6, "church_cut", [(0.0, (4.0, Y + 78.0, FZ + 6.0), (2.0, Y + 56.0, FZ - 13.0)),
                            (1.0, (4.0, Y + 125.0, FZ + 22.0), (2.0, Y + 56.0, FZ - 13.0))], fov=56.0,
          pace="linear"),
    # 0:58.4 the church under the crown (the words between them): far, low, an arc from the right
    _shot(7, "church_cut", [(0.0, (42.0, Y + 8.0, FZ + 112.0), (0.0, Y + 86.0, FZ - 13.0)),
                            (1.0, (22.0, Y + 10.0, FZ + 102.0), (0.0, Y + 86.0, FZ - 13.0))], fov=54.0),
    # 1:14.56 streaming: the church shines out (a whip into a wide from the left)
    _shot(8, "church_cut", [(0.0, (-60.0, Y + 4.0, FZ + 124.0), (0.0, Y + 66.0, FZ - 13.0)),
                            (1.0, (-48.0, Y + 6.0, FZ + 114.0), (0.0, Y + 66.0, FZ - 13.0))], fov=52.0,
          blend=0.35),
    # 1:20.94 gathering light before the slam: a push in on the name (low in the frame, under the words)
    _shot(9, "church_cut", [(0.0, (8.0, Y + 44.0, FZ + 64.0), (8.0, Y + 60.0, FZ - 5.0)),
                            (1.0, (8.0, Y + 50.0, FZ + 42.0), (8.0, Y + 61.0, FZ - 5.0))], fov=46.0),
    # 1:37.7 the church above the nations: a sweeping arc low over the terrace below the summit
    _shot(10, "church_cut", [(0.0, (-46.0, Y - 6.0, FZ + 108.0), (0.0, Y + 34.0, FZ - 10.0)),
                             (1.0, (34.0, Y - 3.0, FZ + 110.0), (0.0, Y + 34.0, FZ - 10.0))], fov=56.0),
    # 1:48.4 the church glowing: top down over the roof canopy, drifting across it
    _shot(11, "church_cut", [(0.0, (-24.0, Y + 96.0, FZ + 24.0), (-2.0, Y + 56.0, FZ - 12.0)),
                             (1.0, (14.0, Y + 102.0, FZ + 16.0), (2.0, Y + 56.0, FZ - 12.0))], fov=54.0),
    # 1:52.1 the column of light from the church: a fast crane up the glass toward the column above
    _shot(12, "church_cut", [(0.0, (-7.0, Y + 4.0, FZ + 13.0), (0.0, Y + 60.0, FZ - 10.0)),
                             (1.0, (-7.0, Y + 52.0, FZ + 16.0), (0.0, Y + 140.0, FZ - 10.0))], fov=60.0),
    # 2:19.2 the church waiting for them: through the city's towers on the left (the words over the sky)
    _shot(13, "church_cut", [(0.0, (-66.0, Y + 12.0, FZ + 46.0), (6.0, Y + 74.0, FZ - 13.0)),
                             (1.0, (-54.0, Y + 15.0, FZ + 26.0), (6.0, Y + 76.0, FZ - 13.0))], fov=52.0),
    # 2:58.4 the church over the crowds: high and wide, an arc from the right (the words over the sky)
    _shot(14, "church_cut", [(0.0, (64.0, Y + 30.0, FZ + 104.0), (0.0, Y + 66.0, FZ - 13.0)),
                             (1.0, (22.0, Y + 36.0, FZ + 122.0), (0.0, Y + 66.0, FZ - 13.0))], fov=54.0),
    # 3:15.2 the gathering glow: low hero angle from the left, the light rising behind the church
    _shot(15, "church_cut", [(0.0, (-32.0, Y + 1.5, FZ + 62.0), (8.0, Y + 40.0, FZ - 60.0)),
                             (1.0, (-18.0, Y + 2.2, FZ + 50.0), (8.0, Y + 44.0, FZ - 60.0))], fov=56.0),
    # 3:33.8 the church in the sunrise: a sweeping arc round the front from the right
    _shot(16, "church_cut", [(0.0, (48.0, Y + 8.0, FZ + 52.0), (0.0, Y + 46.0, FZ - 8.0)),
                             (1.0, (18.0, Y + 14.0, FZ + 70.0), (0.0, Y + 48.0, FZ - 8.0))], fov=56.0),
    # 3:42 the church blazing: a fast low push in from the avenue (the words over the sky above it)
    _shot(17, "church_cut", [(0.0, (10.0, Y + 3.0, FZ + 118.0), (0.0, Y + 70.0, FZ - 13.0)),
                             (1.0, (3.0, Y + 5.0, FZ + 76.0), (0.0, Y + 76.0, FZ - 13.0))], fov=54.0),
    # 4:02.5 the church at peace: a slow drift toward the name, low in the frame under the words
    _shot(18, "church_cut", [(0.0, (8.0, Y + 46.0, FZ + 84.0), (8.0, Y + 68.0, FZ - 10.0)),
                             (1.0, (8.0, Y + 48.0, FZ + 74.0), (8.0, Y + 68.0, FZ - 10.0))], fov=46.0),
    # 4:11.7 the last swell: a great crane from the steps up over the roof, tilting down onto the canopy
    _shot(19, "church_cut", [(0.0, (0.0, Y + 6.0, FZ + 58.0), (0.0, Y + 36.0, FZ - 20.0)),
                             (1.0, (0.0, Y + 74.0, FZ + 62.0), (0.0, Y + 54.0, FZ - 30.0))], fov=56.0),
]
SHOTS = [sh for sh in SHOTS if sh is not None]


# =========================================================================================================
# Small builders: crisp lines ("line" kind, one batch for many segments) and soft bands ("ribbon" kind)
# =========================================================================================================
class _Lines:
    """Many straight segments gathered into one "line" batch per look."""

    def __init__(self):
        self.a, self.b = [], []

    def add(self, a, b):
        self.a.append(np.asarray(a, np.float64))
        self.b.append(np.asarray(b, np.float64))

    def poly(self, P):
        P = np.asarray(P, np.float64)
        for i in range(len(P) - 1):
            self.add(P[i], P[i + 1])

    def batch(self, width, color, alpha, emit, **kw):
        if not self.a:
            return None
        A, B = np.asarray(self.a), np.asarray(self.b)
        return _batch(A, width, color, alpha, kind="line", emit=emit, pos2=B, **kw)


class _Ribbons:
    """Soft bands along polylines, gathered into one "ribbon" batch (width, alpha and colour per point,
    and a place u per point for the travelling sheen)."""

    def __init__(self):
        self.parts = []

    def add(self, P, width, color, alpha=1.0, u=None):
        P = np.asarray(P, np.float64)
        m = len(P)
        if m < 2:
            return
        w = np.broadcast_to(np.asarray(width, np.float64), (m,))
        a = np.broadcast_to(np.asarray(alpha, np.float64), (m,))
        c = np.asarray(color, np.float64)
        c = np.broadcast_to(c, (m, 3)) if c.ndim == 1 else c
        if u is None:
            u = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        u = np.broadcast_to(np.asarray(u, np.float64), (m,))
        self.parts.append((P[:-1], P[1:], w[:-1], w[1:], a[:-1], a[1:], 0.5 * (c[:-1] + c[1:]), u[:-1], u[1:]))

    def batch(self, emit=1.0, **kw):
        if not self.parts:
            return None
        cols = [np.concatenate(x) for x in zip(*self.parts)]
        p, p2, w, w2, a, a2, c, u, u2 = cols
        return _batch(p, w, c, a, kind="ribbon", emit=emit, pos2=p2, size2=w2, alpha2=a2, u=u, u2=u2, **kw)


def _box_lines(L, c, w, d, h):
    x0, x1, z0, z1, y0, y1 = c[0] - w / 2, c[0] + w / 2, c[2] - d / 2, c[2] + d / 2, c[1], c[1] + h
    P = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    for i in range(4):
        (ax, az), (bx, bz) = P[i], P[(i + 1) % 4]
        L.add((ax, y0, az), (bx, y0, bz))
        L.add((ax, y1, az), (bx, y1, bz))
        L.add((ax, y0, az), (ax, y1, az))


# =========================================================================================================
# The city of light on the summit plateau: towers banded in gold and white like the church, domes, the
# great avenue (toward +z) with its lamps, the square left open before the church.
# =========================================================================================================
def _city():
    r = np.random.default_rng(11)
    E, Bd = _Lines(), _Lines()
    wins, domes = [], []
    for gx in np.arange(-84.0, 85.0, 15.0):
        for gz in np.arange(-84.0, 85.0, 15.0):
            x, z = gx + r.uniform(-2.5, 2.5), gz + r.uniform(-2.5, 2.5)
            rad = np.hypot(x, z)
            if rad > 84.0:
                continue
            if abs(x) < 16.0 and z > -12.0:                       # the avenue and the square
                continue
            if abs(x) < 46.0 and z > -50.0:                       # the church, its blade, its square, the plaza
                continue
            w, d = r.uniform(7, 11), r.uniform(7, 11)
            h = r.uniform(7, 13) + 14.0 * np.exp(-rad / 45.0) * r.random()
            c = ZC + _v(x, SUMMIT, z)
            _box_lines(E, c, w, d, h)
            # floor bands on the face toward the avenue and the camera (+z), as on the church
            for y in np.arange(c[1] + 3.4, c[1] + h - 0.5, 3.4):
                Bd.add((c[0] - w / 2, y, c[2] + d / 2), (c[0] + w / 2, y, c[2] + d / 2))
            wins.append(_windows(c, w, d, h))
            if r.random() < 0.18:
                domes.append(_dome(c + _v(0, h, 0), min(w, d) * 0.45, 0.4))
    W, D = np.concatenate(wins), np.concatenate(domes)
    # the paving: a few long faint lines (the old dotted grid was busy behind the choir)
    P = _Lines()
    for x in np.arange(-84.0, 85.0, 12.0):
        if abs(x) < 13.0:
            continue
        h = np.sqrt(max(86.0 ** 2 - x * x, 0.0))
        P.add(ZC + _v(x, SUMMIT + 0.02, -h), ZC + _v(x, SUMMIT + 0.02, h))
    for z in np.arange(-84.0, 85.0, 12.0):
        h = np.sqrt(max(86.0 ** 2 - z * z, 0.0))
        P.add(ZC + _v(-h, SUMMIT + 0.02, z), ZC + _v(h, SUMMIT + 0.02, z))
    # the avenue's edges and the square's rings
    Ed = _Lines()
    for sx in (-12.0, 12.0):
        Ed.add((sx, SUMMIT + 0.05, FACADE_Z + 30.0), (sx, SUMMIT + 0.05, ZC[2] + R_TOP))
    for rr in (24.0, 16.0):
        Ed.poly(_ring(SQUARE, rr, SUMMIT + 0.05, 1.0, -np.pi / 2, np.pi / 2))
    lamps = []
    for z in np.arange(FACADE_Z + 24.0, ZC[2] + R_TOP, 7.0):
        lamps += [(-10.0, SUMMIT + 4.2, z), (10.0, SUMMIT + 4.2, z)]
    lamps = np.asarray(lamps)
    Po = _Lines()
    for p in lamps:
        Po.add((p[0], SUMMIT, p[2]), (p[0], SUMMIT + 4.0, p[2]))
    dimk = 0.55
    dim = [
        E.batch(0.10, lin("#f2c27a") * dimk, 0.75, 1.1),
        Bd.batch(0.08, lin("#fff0d8") * dimk, 0.45, 1.1),
        _batch(W, 0.30, lin("#ffcf86") * dimk, 0.8, kind="soft", emit=0.9, twinkle=0.2),
        _batch(D, 0.16, lin("#ffe0a8") * dimk, 0.8, emit=0.8),
        _batch(lamps, 0.9, lin("#ffcf8a"), 1.0, kind="soft", emit=2.0),
        _batch(lamps, 0.25, lin("#fff2d6"), 1.0, emit=3.5),
        Po.batch(0.08, lin("#e8c08a") * 0.6, 0.8, 1.0),
        P.batch(0.06, lin("#e8b870") * 0.35, 0.6, 0.9),
        Ed.batch(0.12, lin(GOLD2) * 0.8, 0.9, 1.4),
    ]
    gold = [
        E.batch(0.14, lin(GOLD), 0.8, 1.3, birth=np.full(len(E.a), 69.4), fade=0.6, flash=3.0),
        _batch(W, 0.36, lin("#ffe6b0"), 0.8, kind="soft", emit=1.2, birth=np.full(len(W), 69.6), fade=0.8, flash=2.0),
    ]
    return [b for b in dim if b is not None], gold


# =========================================================================================================
# The church of light: the main temple in Korea (from Anthony's photographs), modelled in light.
# A tall gently curved front of deep blue reflective glass (fifteen storeys) ruled by bright white bands at
# every floor and fine mullions, paler toward the top where it mirrors the sky, with a slow sheen travelling
# across it; a teal glass base of two storeys whose top sweeps lower toward the left; a white podium; a warm
# granite entrance portal four storeys tall left of centre (glass and a grid within, a flat canopy, the doors
# lit warm) with broad steps; the tall white ladder blade at the left end, rising above the roof with its top
# slanting up to the left; short white fins in threes at both edges; a crisp white column at the right end;
# a white louvred canopy on the roof following the curve, with a mast; the plain white tower behind; Korean
# pines in front. No lettering or logos are drawn (their places stay glass or stone).
# Only what is seen from the front half (+z) is drawn: every view of it in the film is from there.
# =========================================================================================================
NF, FH = 15, 3.6                    # storeys and storey height (metres)
CH_HT = NF * FH                     # 54 m of glass
CH_Y0 = SUMMIT + 2.3                # the ground floor stands on the white podium (the top of the choir steps)
CH_W2 = 28.0                        # half the width of the curved front
CH_SAG = 5.0                        # how far the middle of the front bulges forward
CH_RC = (CH_W2 ** 2 + CH_SAG ** 2) / (2.0 * CH_SAG)
CH_DEPTH = 22.0
PORTAL_X = -5.6                     # the entrance portal stands left of centre, as on the real building
PORTAL_W2 = 5.4                     # its half width
PORTAL_H = 4.0 * FH + 1.2           # four storeys and a little
PILLAR = 1.3                        # the granite frame's width

# The church's name in light, placed as on the real temple (Anthony's request; the only lettering drawn):
# large in two lines across the top two storeys of the curved front, upper middle right, each line inside its
# storey between the white bands; and small in one line across the top of the stone portal.
NAME_LINES = ("World Mission Society", "Church of God")
NAME_CAP = 2.0                      # cap height of the large name (metres)
NAME_RIGHT = CH_W2 - 5.0            # its right edge (clear of the fins in threes at the right edge)
NAME_STOREYS = (14, 13)             # the storey of each line (0 is the ground floor)
PORTAL_NAME = "WORLD MISSION SOCIETY CHURCH OF GOD"
PORTAL_CAP = 0.32
_FONT = "jost-latin-600-normal.ttf"

# The church's emblem: an empty slot beside the large name, kept clear for it. Anthony is sending the emblem;
# until then nothing is drawn. center (x, y) on the curved front (z is front_z(x)), size: its height and
# width in metres. To add it: make emblem_points() return (N, 2) points (x, y) inside the slot (for example
# from the emblem image: `_raster_points` maps an image's lit pixels into the slot); they are lifted onto the
# curved glass and drawn with the name's light.
EMBLEM_SLOT = ((-10.4, CH_Y0 + 14.0 * FH), 6.4)


def emblem_points():
    """The emblem's points (N, 2) in metres (x, y) on the front, or None while it is not drawn yet."""
    return None


def _font(px):
    for d in (REPO / "fonts", pathlib.Path("/home/user/work/fs/fontsource-jost-5.3.0/package/files")):
        if (d / _FONT).exists():
            return ImageFont.truetype(str(d / _FONT), px)
    raise FileNotFoundError(f"font {_FONT} (repo fonts folder)")


def _text_runs(text, cap, step):
    """The text rasterized at `step` metres per pixel, as horizontal runs of lit pixels.
    Returns (u0, u1, v, width): run ends from the left edge and depth below the cap line, in metres."""
    F = _font(max(int(round(cap / step / 0.7)), 8))
    hb = F.getbbox("H")
    tb = F.getbbox(text)
    pad = 4
    w, h = tb[2] - tb[0] + 2 * pad, tb[3] - hb[1] + 2 * pad
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).text((pad - tb[0], pad - hb[1]), text, font=F, fill=255)
    on = np.asarray(img) > 127
    u0, u1, v = [], [], []
    for r in range(h):
        row = np.concatenate([[False], on[r], [False]]).astype(np.int8)
        d = np.diff(row)
        starts, ends = np.where(d == 1)[0], np.where(d == -1)[0]
        for a, b in zip(starts, ends):
            u0.append((a - pad + 0.5) * step)
            u1.append(max((b - pad - 0.5) * step, (a - pad + 0.5) * step + 0.002))
            v.append((r - pad + 0.5) * step)
    return np.asarray(u0), np.asarray(u1), np.asarray(v), (tb[2] - tb[0]) * step


def _name_segments():
    """The name in light as short horizontal line segments (pos, pos2) on the curved front and the portal."""
    A, B = [], []
    # the large name, each line centred on the block, the block's right edge at NAME_RIGHT
    runs = [_text_runs(t, NAME_CAP, 0.05) for t in NAME_LINES]
    wmax = max(r[3] for r in runs)
    mid = NAME_RIGHT - wmax / 2.0
    for (u0, u1, v, w), k in zip(runs, NAME_STOREYS):
        top = CH_Y0 + (k + 1) * FH - 0.72
        x0, x1 = mid - w / 2.0 + u0, mid - w / 2.0 + u1
        y = top - v
        A.append(np.stack([x0, y, front_z(x0) + 0.14], 1))
        B.append(np.stack([x1, y, front_z(x1) + 0.14], 1))
    # the emblem, once it is given
    E = emblem_points()
    if E is not None and len(E):
        E = np.asarray(E, np.float64)
        e = np.stack([E[:, 0], E[:, 1], front_z(E[:, 0]) + 0.14], 1)
        A.append(e)
        B.append(e + np.array([0.002, 0.0, 0.0]))
    big = (np.concatenate(A), np.concatenate(B))
    # the small name across the top of the portal (on the granite lintel)
    u0, u1, v, w = _text_runs(PORTAL_NAME, PORTAL_CAP, 0.016)
    pz = float(front_z(PORTAL_X)) + 0.45 + 0.08
    top = CH_Y0 + PORTAL_H - PILLAR / 2.0 + PORTAL_CAP / 2.0
    x0, x1 = PORTAL_X - w / 2.0 + u0, PORTAL_X - w / 2.0 + u1
    small = (np.stack([x0, top - v, np.full(len(v), pz)], 1), np.stack([x1, top - v, np.full(len(v), pz)], 1))
    return big, small


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
    return CH_Y0 + FH * (0.95 + 1.05 * np.sin(0.5 * np.pi * u) ** 0.8)


def _in_portal(x, y):
    return (abs(x - PORTAL_X) < PORTAL_W2 + 0.2) and (y < CH_Y0 + PORTAL_H)


def _sky_in_glass(x, y):
    """How much bright sky and cloud the glass mirrors at (x, y): soft cloud shapes, stronger higher up."""
    h = np.clip((y - CH_Y0) / CH_HT, 0.0, 1.0)
    c = (0.5 + 0.5 * np.sin(0.13 * x + 0.21 * y + 0.7) * np.sin(0.061 * x - 0.11 * y + 2.1)
         + 0.25 * np.sin(0.31 * x - 0.05 * y + 4.0))
    return np.clip(0.15 + 0.85 * h ** 1.3, 0.0, 1.0), np.clip(c, 0.0, 1.0) * (0.3 + 0.7 * h)


def _glass_color(x, y):
    """Deep blue low down, paler crystal blue toward the top where it mirrors the sky, with soft clouds."""
    h, cl = _sky_in_glass(x, y)
    h, cl = np.asarray(h)[:, None], np.asarray(cl)[:, None]
    deep, mid, pale, cloud = lin("#16319e"), lin("#3170ea"), lin("#b4d4ff"), lin("#eef4ff")
    c = np.where(h < 0.45, deep + (mid - deep) * (h / 0.45), mid + (pale - mid) * ((h - 0.45) / 0.55))
    cl = cl * cl * (3.0 - 2.0 * cl)
    return c + (cloud - c) * 0.5 * cl


def _church():
    r = np.random.default_rng(13)
    y0, top = CH_Y0, CH_Y0 + CH_HT
    zs = FACADE_Z - CH_SAG                      # where the sides meet the front
    zb = zs - CH_DEPTH                          # the back face
    glass, teal, pglass, warm = _Ribbons(), _Ribbons(), _Ribbons(), _Ribbons()
    glory = _Ribbons()                          # the same glass in crystal and gold, for the choruses
    bands, stoneR, plinth = _Ribbons(), _Ribbons(), _Ribbons()
    base, low = _Ribbons(), _Lines()          # the lowest band and the podium's top edge: behind the singers
    mull, white, fine, stone, side, tower = _Lines(), _Lines(), _Lines(), _Lines(), _Lines(), _Lines()
    BW = 1.4                                    # mullion bay

    # -- the curved glass: one soft vertical band per bay, coloured by height (sky reflection), the place u
    # runs diagonally so a slow sheen sweeps across the whole front
    for x in np.arange(-CH_W2 + BW / 2, CH_W2, BW):
        z = float(front_z(x)) - 0.05
        bt = float(_base_top(x))
        inside = abs(x - PORTAL_X) < PORTAL_W2 - PILLAR + 0.2
        under = abs(x - PORTAL_X) < PORTAL_W2 + 0.3
        ys = np.linspace(y0 + PORTAL_H if under else bt, top, 60)
        P = np.stack([np.full(len(ys), x), ys, np.full(len(ys), z)], 1)
        # each pane mirrors the sky a little differently (real glass is never quite flat)
        pane = 1.0 + 0.07 * np.sin(x * 12.9898 + np.floor((ys - y0) / FH) * 78.233) + 0.05 * r.standard_normal()
        col = _glass_color(np.full(len(ys), x), ys) * pane[:, None]
        # a little deeper behind the large name, so its white letters stand out as on the real glass
        nx0 = NAME_RIGHT - 30.0
        if nx0 - 1.0 < x < NAME_RIGHT + 1.0:
            col = col * (1.0 - 0.32 * np.asarray(_ss(y0 + 12.9 * FH, y0 + 13.2 * FH, ys), np.float64)[:, None])
        glass.add(P, 2.1, col, 0.62, u=x * 0.85 + (ys - y0) * 0.55)
        h = ((ys - y0) / CH_HT)[:, None]
        glory.add(P, 2.1, (lin("#ffb24a") * (1.0 - h) + lin("#fff4e2") * h) * pane[:, None], 0.30,
                  u=x * 0.85 + (ys - y0) * 0.55)
        if not under:
            ys = np.linspace(y0 + 0.1, bt, 6)
            P = np.stack([np.full(len(ys), x), ys, np.full(len(ys), z)], 1)
            k = (ys - y0) / (2 * FH)
            col = lin("#2fb8a8")[None, :] * (0.8 + 0.25 * k[:, None]) + lin("#9ff0e0")[None, :] * 0.12
            teal.add(P, 2.1, col, 0.42, u=x * 0.85 + (ys - y0) * 0.55)
        elif inside:
            # within the portal: lighter aqua glass behind the granite frame (above the doors)
            ys = np.linspace(y0 + 5.0, y0 + PORTAL_H - PILLAR, 10)
            P = np.stack([np.full(len(ys), x), ys, np.full(len(ys), z + 0.3)], 1)
            pglass.add(P, 2.0, lin("#58b8e0") * 0.9 + lin("#d8f0ff") * 0.1, 0.55)
    # mullions (fine, pale): they rule the glass into narrow panes
    for x in np.arange(-CH_W2 + BW, CH_W2 - 0.1, BW):
        z = float(front_z(x)) + 0.04
        ya = y0 + PORTAL_H if abs(x - PORTAL_X) < PORTAL_W2 + 0.1 else y0 + 0.2
        mull.add((x, ya, z), (x, top, z))
    # -- the white floor bands across the whole curved front (crisp, evenly ruled), and the sweep line where
    # the teal base meets the blue
    for k in range(NF + 1):
        y = y0 + k * FH
        P = _arc_pts(y, 0.5, out=0.10)
        if y < y0 + PORTAL_H:                    # the portal stands proud: the bands pass behind it
            left = P[P[:, 0] < PORTAL_X - PORTAL_W2]
            right = P[P[:, 0] > PORTAL_X + PORTAL_W2]
            for Q in (left, right):
                (bands if k else base).add(Q, 0.34 if k else 0.5, lin("#f6f9ff"), 1.0)
        else:
            bands.add(P, 0.34 if k < NF else 0.7, lin("#f6f9ff"), 1.0)
    xs = np.linspace(-CH_W2, CH_W2, 160)
    xs = xs[(xs < PORTAL_X - PORTAL_W2) | (xs > PORTAL_X + PORTAL_W2)]
    for seg in np.split(xs, np.where(np.diff(xs) > 1.0)[0] + 1):
        P = np.stack([seg, _base_top(seg), front_z(seg) + 0.12], 1)
        bands.add(P, 0.26, lin("#e8fff8"), 0.9)
    # -- the white podium along the foot (its face; the choir steps stand before its middle)
    for (xa, xb) in ((-CH_W2 - 9.0, -13.6), (13.6, CH_W2 + 3.0)):
        P = _arc_pts(SUMMIT + 1.15, 0.6, xa, xb, out=1.4)
        plinth.add(P, 2.0, lin("#e8eef8"), 0.14)
        low.poly(_arc_pts(y0 - 0.05, 0.6, xa, xb, out=1.4))
        fine.poly(_arc_pts(SUMMIT + 0.05, 0.6, xa, xb, out=1.4))
    low.poly(_arc_pts(y0 - 0.05, 0.6, -13.6, 13.6, out=0.9))
    # -- the crisp white column at the right end, and the slimmer edge at the left end of the glass
    edgeL = _Lines()
    edgeL.add((CH_W2 + 0.5, SUMMIT, zs + 0.3), (CH_W2 + 0.5, top + 2.4, zs + 0.3))
    edgeL.add((-CH_W2 - 0.2, y0, zs + 0.2), (-CH_W2 - 0.2, top, zs + 0.2))
    # -- the tall white ladder blade at the left end: two posts and rungs, its top slanting up to the left
    bx0, bx1, bz = -CH_W2 - 7.2, -CH_W2 - 2.2, zs - 0.6
    top0, top1 = top + 15.0, top + 5.0
    blade = _Lines()
    for dz in (-0.5, 0.5):
        blade.add((bx0, SUMMIT, bz + dz), (bx0, top0, bz + dz))
        blade.add((bx1, SUMMIT, bz + dz), (bx1, top1, bz + dz))
        blade.add((bx0, top0, bz + dz), (bx1, top1, bz + dz))
        for y in np.arange(y0 + 2.0 * FH, top1 - 1.0, 2.0 * FH):
            blade.add((bx0, y, bz + dz), (bx1, y, bz + dz))
    for y in np.arange(y0 + 2.0 * FH, top1 - 1.0, 2.0 * FH):        # the arms that tie it to the building
        fine.add((bx1, y, bz), (-CH_W2, y, zs))
    # -- short white fins in threes standing out from both edges at several storeys
    fins = _Lines()
    for sgn, floors in ((-1.0, (3, 7, 11)), (1.0, (2, 5, 8, 11, 13))):
        for f in floors:
            for j in range(3):
                y = y0 + f * FH + 0.7 + 0.75 * j
                xa, xb = sgn * (CH_W2 - 3.2), sgn * (CH_W2 + 3.2)
                za = float(front_z(xa)) + 0.35
                fins.add((xa, y, za), (xb, y, za - 0.9))
    # -- the roof: a white louvred canopy following the curve, slightly overhanging, on posts, and a mast
    yr = top + 3.4
    canopy = _Ribbons()
    canopy.add(_arc_pts(yr, 0.5, -CH_W2 - 1.2, CH_W2 + 1.2, out=1.6), 0.55, lin("#f6f9ff"), 1.0)
    canopy.add(_arc_pts(yr - 0.7, 0.5, -CH_W2 - 1.0, CH_W2 + 1.0, out=1.4), 0.25, lin("#f6f9ff"), 0.7)
    for x in np.arange(-CH_W2 - 0.6, CH_W2 + 0.7, 1.0):
        z = float(front_z(x)) + 1.6
        fine.add((x, yr, z), (x, yr - 0.4, zb + 4.0))
    for x in np.arange(-CH_W2, CH_W2 + 0.1, 7.0):
        z = float(front_z(x)) + 0.8
        fine.add((x, top, z), (x, yr - 0.7, z))
    fine.add((-CH_W2 - 1.0, yr - 0.4, zb + 4.0), (CH_W2 + 1.0, yr - 0.4, zb + 4.0))
    white.add((5.0, yr, zb + 9.0), (5.0, yr + 11.0, zb + 9.0))
    fine.add((3.6, yr + 7.5, zb + 9.0), (6.4, yr + 7.5, zb + 9.0))
    # the sides (seen only at an angle): their floor lines and the corner, no back face
    for sx in (-CH_W2, CH_W2):
        for k in range(0, NF + 1, 1):
            side.add((sx, y0 + k * FH, zs), (sx, y0 + k * FH, zb))
        side.add((sx, y0, zb), (sx, top, zb))
    # -- the granite entrance portal: a tall frame standing proud of the glass, glass and a grid within, a
    # flat canopy over the glass doors (lit warm from inside), the steps below it
    px0, px1 = PORTAL_X - PORTAL_W2, PORTAL_X + PORTAL_W2
    pz = float(front_z(PORTAL_X)) + 0.45
    ph = y0 + PORTAL_H
    sc = lin("#d9b088")
    for xx in (px0 + PILLAR / 2, px1 - PILLAR / 2):
        P = np.stack([np.full(12, xx), np.linspace(SUMMIT + 0.2, ph, 12), np.full(12, pz)], 1)
        stoneR.add(P, PILLAR * 1.25, sc, 0.9)
    P = np.stack([np.linspace(px0, px1, 12), np.full(12, ph - PILLAR / 2), np.full(12, pz)], 1)
    stoneR.add(P, PILLAR * 1.25, sc, 0.9)
    for xx in (px0, px0 + PILLAR, px1 - PILLAR, px1):
        stone.add((xx, SUMMIT + 0.2, pz + 0.05), (xx, ph if xx in (px0, px1) else ph - PILLAR, pz + 0.05))
    stone.add((px0, ph, pz + 0.05), (px1, ph, pz + 0.05))
    stone.add((px0 + PILLAR, ph - PILLAR, pz + 0.05), (px1 - PILLAR, ph - PILLAR, pz + 0.05))
    for xx in (px0, px1):                                    # its depth (it stands out from the glass)
        stone.add((xx, ph, pz), (xx, ph, pz - 1.4))
    # the grid in the portal's glass
    gx0, gx1 = px0 + PILLAR + 0.05, px1 - PILLAR - 0.05
    for xx in np.linspace(gx0, gx1, 7)[1:-1]:
        fine.add((xx, y0 + 5.2, pz - 0.4), (xx, ph - PILLAR, pz - 0.4))
    for yy in np.arange(y0 + 5.2, ph - PILLAR - 0.3, 1.8):
        fine.add((gx0, yy, pz - 0.4), (gx1, yy, pz - 0.4))
    # the flat canopy over the doors
    for dz in np.linspace(-0.4, 2.2, 6):
        white.add((gx0 - 0.3, y0 + 4.8, pz + dz), (gx1 + 0.3, y0 + 4.8, pz + dz))
    # the glass doors, lit warm from inside
    for xx in np.arange(gx0 + 0.6, gx1 - 0.3, 1.0):
        ys = np.linspace(y0 - 1.2, y0 + 4.5, 6)
        warm.add(np.stack([np.full(6, xx), ys, np.full(6, pz - 0.5)], 1), 1.5,
                 lin("#ffd8a0"), np.linspace(0.45, 0.2, 6))
    for xx in np.linspace(gx0, gx1, 6):
        fine.add((xx, y0 - 1.2, pz - 0.35), (xx, y0 + 4.6, pz - 0.35))
    # -- the broad white stone steps before the front (the choir stands on them)
    steps = _Lines()                            # kept soft: the gold choir stands on them
    for i, (yy, zz) in enumerate(CHOIR_STEPS):
        steps.add((-13.0, yy - 0.05, zz + 0.65), (13.0, yy - 0.05, zz + 0.65))
        steps.add((-13.0, yy - 0.6, zz + 0.66), (13.0, yy - 0.6, zz + 0.66))
        steps.add((-13.0, yy - 0.6, zz + 0.66), (-13.0, yy - 0.05, zz + 0.66))
        steps.add((13.0, yy - 0.6, zz + 0.66), (13.0, yy - 0.05, zz + 0.66))
        plinth.add([(-13.0, yy - 0.32, zz + 0.66), (13.0, yy - 0.32, zz + 0.66)], 0.5, lin("#e8eef8"), 0.07)
    # -- the plain white tower behind (right of middle), its window strips and a box on top; drawn where it
    # shows above the church
    tx0, tx1 = 1.0, 23.0
    tz1 = zb - 2.0
    tz0 = tz1 - 16.0
    th = top + 17.0
    ty = top + 3.0
    for (xx, zz) in ((tx0, tz1), (tx1, tz1), (tx0, tz0), (tx1, tz0)):
        tower.add((xx, ty, zz), (xx, th, zz))
    for (a, b) in (((tx0, tz1), (tx1, tz1)), ((tx0, tz0), (tx1, tz0)), ((tx0, tz0), (tx0, tz1)), ((tx1, tz0), (tx1, tz1))):
        tower.add((a[0], th, a[1]), (b[0], th, b[1]))
    strips = _Ribbons()
    for yy in np.arange(ty + 1.2, th - 0.8, 3.0):
        strips.add([(tx0 + 0.6, yy, tz1 + 0.05), (tx1 - 0.6, yy, tz1 + 0.05)], 0.9, lin("#cfe0ff"), 0.30)
        strips.add([(tx1 + 0.05, yy, tz1 - 0.6), (tx1 + 0.05, yy, tz0 + 0.6)], 0.9, lin("#cfe0ff"), 0.18)
    _box_lines(tower, _v(tx0 + 8.0, th, (tz0 + tz1) / 2.0), 8.0, 7.0, 4.0)
    # -- Korean pines of light before the building (curving trunks, flat layered crowns), clear of the
    # orchestra on the square
    trunk = _Ribbons()
    green = []
    for (px, pzz, h, lean) in ((-33.0, FACADE_Z + 6.0, 10.0, -0.30), (-25.5, FACADE_Z + 9.0, 7.5, 0.25),
                               (26.0, FACADE_Z + 8.0, 9.5, 0.30), (33.0, FACADE_Z + 5.0, 7.0, -0.25)):
        u = np.linspace(0.0, 1.0, 16)
        tx = px + lean * h * u ** 1.5 + 0.35 * np.sin(4.0 * u)
        trunk.add(np.stack([tx, SUMMIT + h * u, np.full(16, pzz)], 1), 0.45 * (1.0 - 0.6 * u), lin("#d8a874"), 0.8)
        for j, (fu, fr) in enumerate(((0.52, 2.0), (0.68, 2.9), (0.84, 2.6), (1.0, 1.8))):
            cx = px + lean * h * fu ** 1.5 + (1.3 if j % 2 else -1.1) * np.sign(lean)
            n = 320
            a = r.random(n) * 2 * np.pi
            rr = fr * np.sqrt(r.random(n))
            green.append(np.stack([cx + rr * np.cos(a), SUMMIT + h * fu + 0.45 * r.random(n) * (1 - rr / fr),
                                   pzz + 0.8 * rr * np.sin(a)], 1))
    GR = np.concatenate(green)
    nbig, nsmall = _name_segments()
    WH = lin("#f6f9ff")
    soft = [
        glass.batch(1.0, pulse=(4.0, 7.0, 0.55, 120.0)),
        teal.batch(1.0, pulse=(4.0, 7.0, 0.45, 120.0)),
        pglass.batch(1.0),
        warm.batch(1.6),
        stoneR.batch(1.0),
        strips.batch(1.0),
        trunk.batch(1.2),
        _batch(GR, 0.16, lin("#7fd8a0") * 0.6 + lin(GOLD) * 0.25, 0.7, emit=1.3, twinkle=0.4),
    ]
    crisp = [
        plinth.batch(1.2),
        bands.batch(2.4),
        canopy.batch(2.2),
        mull.batch(0.06, lin("#bcd4ff"), 0.5, 1.2),
        white.batch(0.22, WH, 1.0, 2.0),
        edgeL.batch(0.9, WH, 1.0, 2.2),
        blade.batch(0.55, WH, 1.0, 2.2),
        fins.batch(0.28, WH, 1.0, 2.2),
        fine.batch(0.08, lin("#e6eeff"), 0.8, 1.4),
        stone.batch(0.10, lin("#ffe2bc"), 0.9, 1.6),
        side.batch(0.12, lin("#cfdcff") * 0.8, 0.6, 1.2),
        tower.batch(0.25, lin("#eef3ff"), 0.85, 1.6),
        _batch(nbig[0], 0.058, lin("#f8fbff"), 1.0, kind="line", emit=2.9, pos2=nbig[1], twinkle=0.0),
        _batch(nsmall[0], 0.019, lin("#fbfcff"), 1.0, kind="line", emit=2.0, pos2=nsmall[1], twinkle=0.0),
    ]
    soft = [b for b in soft if b is not None]
    crisp = [b for b in crisp if b is not None]
    stepb = [steps.batch(0.10, lin("#eef2fa"), 0.6, 1.3), low.batch(0.22, WH, 1.0, 2.0), base.batch(2.4)]
    gloryb = [glory.batch(1.0, pulse=(6.0, 6.0, 0.8, 90.0))]
    for b in soft + crisp + stepb + gloryb:
        b["fog"] = 0.35                         # keep its blue and white clear from far away
        b["reflect"] = False                    # no stray copy of it in the sea below the mountain
    return soft, crisp, stepb, gloryb


def church_glow(t):
    """The church of light: softly glowing in the waiting dawn (a little lower under the opening title),
    awake as the paths reach out (0:11.9), shining out on "to the great Church of God!" (1:14.56)."""
    return (0.5 + 0.25 * _sc(10.4, 13.0, t) + 0.1 * _sc(16.0, 21.5, t)
            + 0.8 * hit_pulse(t, [HIT["stream"]], fall=2.5) + 0.25 * hit_pulse(t, [HIT["father"]], fall=1.2)
            + 0.15 * _sc(70.0, 75.0, t) + 0.10 * beat_pulse(t))


class Church:
    """The church's glass, stone and warm light (part "soft"), its white bands, frames, blade, fins and name
    (part "crisp"), or the steps, podium edge and lowest band right behind the singers (part "steps"). In the close shots of the choir and orchestra the white lines step back further than the glass,
    so the bright bands never cut across the gold choir or the words."""
    static = True
    _parts = None

    def __init__(self, part):
        if Church._parts is None:
            Church._parts = _church()
        self.part = part
        self.b = Church._parts[{"soft": 0, "crisp": 1, "steps": 2, "glory": 3}[part]]

    def sample(self, t):
        return self.b

    def gain(self, t):
        k = city_k(t) * church_glow(t)
        if stage_view(t):
            k *= {"soft": 0.75, "crisp": 0.4, "steps": 0.12, "glory": 0.5}[self.part]
        if shot_name(t) == "church_cut":       # the church's own cut-ins: full frame of it, so less light
            k *= 0.5
        i = intensity(t)
        if self.part == "soft":                 # deeper blue in the quiet, brighter as the music grows
            k *= 0.5 + 0.3 * i
        elif self.part == "glory":              # crystal and gold in the choruses
            k *= 0.9 * max(i - 0.5, 0.0)
        else:                                   # the white bands and the name pulse on the beat
            k *= 1.0 + 0.35 * beat_pulse(t) * (0.3 + 0.7 * i)
        return k


class BandWave:
    """On every hit a wave of light runs up the white floor bands, bottom to top (one band after another)."""

    def __init__(self):
        self.ys = np.array([CH_Y0 + k * FH for k in range(NF + 1)])
        self.P = [_arc_pts(y, 0.5, out=0.16) for y in self.ys]
        self.kicks = np.asarray(KICKS, np.float64)

    def sample(self, t):
        if local_k(t) <= 0.0:
            return None
        i = int(np.searchsorted(self.kicks, t, side="right")) - 1
        if i < 0:
            return None
        u = t - self.kicks[i]
        if u > 1.8:
            return None
        front = CH_Y0 - 6.0 + 48.0 * u                    # the wave climbs about 48 m a second
        fade = 1.0 - _sc(0.9, 1.8, u)
        rib = _Ribbons()
        for y, P in zip(self.ys, self.P):
            a = float(np.exp(-((y - front) / 4.5) ** 2)) * fade
            if a > 0.02:
                rib.add(P, 0.75, lin("#fff2d6"), a)
        b = rib.batch(3.0)
        if b is None:
            return None
        b.update(fog=0.35, reflect=False)
        return b

    def gain(self, t):
        k = city_k(t) * church_glow(t) * (0.5 + 0.7 * intensity(t))
        if shot_name(t) == "church_cut":
            k *= 0.6
        return k * (0.35 if stage_view(t) else 1.0)


class _Body:
    """The church's body as a silhouette only (never drawn as light): it hides the sky glow and the city
    behind the glass, so the front reads as a solid building of glowing blue glass, not a wire frame."""
    static = True

    def __init__(self):
        pts = []
        for y in np.arange(SUMMIT + 0.4, CH_Y0 + CH_HT + 0.2, 1.0):
            x = np.arange(-CH_W2 + 0.4, CH_W2 - 0.3, 1.0)
            pts.append(np.stack([x, np.full(len(x), y), front_z(x) - 1.6], 1))
        P = np.concatenate(pts)
        self.b = [dict(pos=P, size=1.1, color=(0.0, 0.0, 0.0), alpha=1.0, kind="soft", reflect=False)]

    def sample(self, t):
        return self.b

    def gain(self, t):
        return 0.0


def body_k(t):
    """How strongly the church's body hides what is behind it."""
    k = local_k(t)
    if k <= 0.0:
        return 0.0
    # the phrases ride 30 m in front of the camera: when the front is nearer than that they would fall behind
    # the silhouette and be hidden, so the body fades out in near views while a phrase is on screen
    c = np.asarray(H.CAMERA.state(t).pos, np.float64)
    near = 1.0 - _sc(34.0, 44.0, float(c[2] - FACADE_Z))
    if near > 0.0 and any(ti - 0.6 <= t <= to + 0.6 for _, (ti, _r0, _r1, to), *_ in H.PHRASE_LIST):
        k *= 1.0 - near
    return k


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
    scene.add("church", Church("soft"))
    scene.add("church lines", Church("crisp"))
    scene.add("church steps", Church("steps"))
    scene.add("church glory", Church("glory"))
    scene.add("church wave", BandWave(), reflect=False)
    scene.add("church body", _Body(), mask=Mask("dark", strength=body_k, grow=0.6, soft=2.5), reflect=False)
    scene.add("paths", Static(_paths(), lambda t: local_k(t) * (1.0 - 0.75 * _sc(40.0, 42.0, t))))
