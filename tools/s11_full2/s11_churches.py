"""Song 11 v2 round 7: more and more churches of God established, modelled in light from public photographs of
real World Mission Society Church of God buildings (silhouettes only, no signs copied).
Owned by the churches thread. Imported by the core beside the other threads (before the music effects).
No em dash or en dash anywhere in this file.

Anthony (2026-11-19): "more and more churches are being established (reference real wmscog buildings; use
different ones)". Then: "The churches don't need to be on the earth. Many, many, many more churches should start
to appear around Zion." The main temple is already the church of light (s11_church.py) and is not repeated here.

THE BUILDINGS: every church comes from the catalogue tools/s11_full2/models/wmscog_churches.py (one source of
truth; each entry a different real building with its own published page, modelled from its photograph as a
silhouette in light: no sign, emblem, lettering or picture copied; no AI image). The catalogue's batch 0 is the
nineteen drawn by hand here first (LEGACY_SHAPES); all others are drawn from their parts by _parts. Duplicates
between the two first lists were merged (one model per building). The main temple (New Jerusalem Pangyo) is the
church of light and is not repeated.

WHAT IT DOES: around Mount Zion the churches of God are established one after another, each a different real
church, until the near shore, the sea, the far shore and the foot of the hills hold every building in the list.
  Where   rings round Zion in four bands: the near shore (rings at 430, 560, 680 m from the foot of the
          mountain; the first four flank the march route), the sea of glass (820 to 1300 m), the far shore (1450
          to 2120 m) and the foot of the hills (2450 to 3050 m), larger and drawn more simply the farther out.
          Every church stands on the ground (y = 0) and faces Zion squarely, evenly spaced along its ring (rings
          staggered), so they read as rows and arcs, never scattered or floating. No church stands on a camera path (every shot's camera is sampled every quarter
          second; a church keeps its distance from all of them), on the great avenue and march corridor, or on
          the mountain.
  When    WAVES: from the first Zion view (0:55.4) a handful in verse 1, then more and more through chorus 1,
          verse 2, chorus 2 and the coda, on the beats and hits, several at once on the big hits (3, 4 and 5 on
          the three slams). Each is born from the ground up in half a second with a small flash and a column of
          light, then keeps a soft breath on the beat.
  Calm    dimmed while a phrase reads, and hidden while it reads if it stands behind the words on screen; the columns held down where the music already blazes; hidden on the
          Earth; held to 35 percent in the choir shots (65 percent lower again under a phrase there), hidden from the orchestra on the clouds (3:26). Mount Zion hides what stands behind it: every frame each church is
          tested at three heights against the terraces as the camera sees it, so no light shows through them.
  Cost    each church is a static point set on the graphics card (born by `birth`); per frame only its strength
          (the occlusion test) and the columns of the churches being born are computed.
"""
from songs.s11_full2 import *  # noqa: F401,F403
import songs.s11_full2 as H
import os

SHOTS = []

PEARL = "#e6edff"
GLASS = "#7ab8ff"
TEAL = "#62e2d2"
WARM = "#ffd49a"
GOLDA = "#ffc664"
ROSE = "#ffb08a"


# =========================================================================================================
# Drawing in light (model metres; x across the front, y up, z toward the viewer; the front face is z = +d/2)
# =========================================================================================================
class _Pen:
    """Collects points of one building by role: edge (pearl outline), glass (blue grid), win (warm windows),
    and accent lines in their own colours."""

    def __init__(self, step):
        self.s = step
        self.P, self.C, self.R = [], [], []      # points, colour hex, role (0 edge, 1 glass, 2 window, 3 accent)

    def _put(self, p, col, role):
        p = np.asarray(p, np.float64).reshape(-1, 3)
        self.P.append(p)
        self.C += [col] * len(p)
        self.R += [role] * len(p)

    def line(self, a, b, col=PEARL, role=0, step=None):
        self._put(_seg(a, b, step or self.s), col, role)

    def poly(self, pts, col=PEARL, role=0, closed=False):
        for i in range(len(pts) - (0 if closed else 1)):
            self.line(pts[i], pts[(i + 1) % len(pts)], col, role)

    def box(self, x0, x1, y0, y1, z0, z1, col=PEARL, role=0):
        for (xa, za), (xb, zb) in (((x0, z0), (x1, z0)), ((x1, z0), (x1, z1)), ((x1, z1), (x0, z1)), ((x0, z1), (x0, z0))):
            self.line((xa, y1, za), (xb, y1, zb), col, role)
            self.line((xa, y0, za), (xb, y0, zb), col, role)
        for x, z in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
            self.line((x, y0, z), (x, y1, z), col, role)

    def grid(self, x0, x1, y0, y1, z, nx, ny, col=GLASS):
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            self.line((x, y0, z), (x, y1, z), col, 1)
        for j in range(ny + 1):
            y = y0 + (y1 - y0) * j / ny
            self.line((x0, y, z), (x1, y, z), col, 1)

    def arc(self, cx, cy, z, rx, ry, a0=0.0, a1=np.pi, col=PEARL, role=0):
        n = max(int(abs(a1 - a0) * max(rx, ry) / self.s), 4)
        a = np.linspace(a0, a1, n)
        self._put(np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a), np.full(n, z)], 1), col, role)

    def arched(self, x0, x1, y0, y1, z, n, w, col=WARM):
        """n tall arched windows across x0..x1 (each w wide, from y0 to the spring y1, a half circle above):
        a warm outline with a light in each."""
        for i in range(n):
            cx = x0 + (x1 - x0) * (i + 0.5) / n
            self.line((cx - w / 2, y0, z), (cx - w / 2, y1, z), col, 3)
            self.line((cx + w / 2, y0, z), (cx + w / 2, y1, z), col, 3)
            self.arc(cx, y1, z, w / 2, w / 2, 0.0, np.pi, col, 3)
            self._put([(cx, y0 + 0.35 * (y1 - y0), z), (cx, y0 + 0.75 * (y1 - y0), z)], col, 2)

    def windows(self, x0, x1, y0, y1, z, nx, ny, col=WARM):
        xs = x0 + (x1 - x0) * (np.arange(nx) + 0.5) / nx
        ys = y0 + (y1 - y0) * (np.arange(ny) + 0.5) / max(ny, 1)
        X, Y = np.meshgrid(xs, ys)
        self._put(np.stack([X.ravel(), Y.ravel(), np.full(X.size, z)], 1), col, 2)

    def done(self):
        P = np.concatenate(self.P)
        return dict(pos=P, col=np.array([lin(c) for c in self.C]), role=np.asarray(self.R), h=float(P[:, 1].max()))


def _homaesil(s):
    p = _Pen(s)
    p.box(-30, -4, 0, 13, -12, 12)
    for x in np.linspace(-27, -7, 11):                       # the screen of fins
        p.line((x, 1.5, 12.3), (x, 11.5, 12.3), GOLDA, 3)
    p.box(-6, 14, 0, 27, -10, 10)
    p.grid(-6, 14, 2, 27, 10.1, 6, 8)
    p.line((14, 0, 6), (14, 36, 6))                          # the tower with its rounded top
    p.line((24, 0, 6), (24, 36, 6))
    p.line((14, 0, -6), (14, 36, -6))
    p.line((24, 0, -6), (24, 36, -6))
    for z in (6, -6):
        p.arc(19, 36, z, 5, 6.5, 0.0, np.pi)
    p.line((19, 42.5, 6), (19, 42.5, -6))
    p.grid(18, 20, 3, 38, 6.1, 1, 14)
    p.windows(-28, -6, 3, 10, 12.2, 6, 1)
    return p.done()


def _sejong(s):
    p = _Pen(s)
    p.box(-28, -4, 0, 24, -10, 10)
    p.arched(-25, -7, 5, 18, 10.1, 5, 2.0)
    p.box(4, 24, 0, 22, -9, 9)
    p.arched(6, 22, 5, 16.5, 9.1, 4, 2.0)
    p.box(-4, 4, 0, 33, -6, 6)
    p.grid(-4, 4, 1, 33, 6.1, 3, 12)
    p.line((-2.5, 3.5, 8.5), (2.5, 3.5, 8.5))                # the entrance canopy
    return p.done()


def _moran(s):
    p = _Pen(s)
    p.box(-8, 26, 0, 18, -10, 10)
    p.line((-8, 7, 10.1), (26, 12, 10.1), GLASS, 1)          # the slanting glass band
    p.line((-8, 10, 10.1), (26, 15, 10.1), GLASS, 1)
    for x in np.linspace(-6, 24, 9):
        y = 7 + 5 * (x + 8) / 34
        p.line((x, y, 10.1), (x, y + 3, 10.1), GLASS, 1)
    p.windows(19, 25, 9.5, 17, 10.2, 3, 4, GOLDA)            # the gold panel
    p.windows(-6, 18, 2, 5.5, 10.2, 8, 1)
    p.box(-17, -9, 0, 29, -5, 5, ROSE, 3)                    # the tall tower
    p.windows(-15, -11, 4, 27, 5.1, 1, 8)
    p.line((-12.5, 29, 0), (-12.5, 39, 0), TEAL, 3)          # the blade and its disc
    p.line((-11.5, 29, 0), (-11.5, 39, 0), TEAL, 3)
    p.arc(-12, 41.5, 0.0, 2.6, 2.6, 0.0, 2 * np.pi, GLASS, 3)
    return p.done()


def _sail(s):
    p = _Pen(s)
    y = np.linspace(0.0, 36.0, max(int(36.0 / s), 8))
    xr = -16.0 + 3.0 * np.sin(np.pi * y / 40.0)               # the sail's curved edge
    for z in (5, -5):
        p._put(np.stack([np.full_like(y, -27.0), y, np.full_like(y, z)], 1), PEARL, 0)
        p._put(np.stack([xr, y, np.full_like(y, z)], 1), GLASS, 1)
        p.line((-27, 36, z), (xr[-1], 36 + 3.5, z), PEARL, 0)
    for f in np.linspace(3, 33, 9):                          # its glass floors
        xx = -16.0 + 3.0 * np.sin(np.pi * f / 40.0)
        p.line((-27, f, 5.1), (xx, f, 5.1), GLASS, 1)
    p.box(-14, 26, 0, 20, -11, 11)
    p.arched(-11, 23, 5, 15, 11.1, 7, 2.0)
    p.line((-15, 21.2, 11.6), (27, 21.2, 11.6), TEAL, 3)     # the thin roof band
    return p.done()


def _sydney(s):
    p = _Pen(s)
    p.box(-32, 4, 0, 10, -14, 14, "#b9c4dc", 0)              # the long grey hall
    for x in np.linspace(-29, 1, 7):
        p.line((x, 0.5, 14.1), (x, 9.5, 14.1), "#b9c4dc", 0)
    p.box(4, 22, 0, 16, -8, 8, ROSE, 3)                      # the orange entrance block
    p.grid(8, 18, 0.5, 12, 8.1, 5, 4)
    p.line((2, 4.5, 11), (24, 4.5, 11), PEARL, 0)            # the canopy
    return p.done()


def _brazil(s):
    p = _Pen(s)
    p.box(-10, 18, 0, 22, -10, 10)
    p.grid(-10, 18, 0.5, 22, 10.1, 7, 7)
    n = max(int(2 * np.pi * 3.5 / s), 8)                    # the white cylinder in front (flat rings)
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    for yy in np.linspace(0.5, 25, 7):
        p._put(np.stack([-3 + 3.5 * np.cos(a), np.full(n, yy), 12.0 + 3.5 * np.sin(a)], 1), PEARL, 0)
    for a in np.radians([60, 120]):
        p.line((-3 + 3.5 * np.cos(a), 0, 12 + 3.5 * np.sin(a)), (-3 + 3.5 * np.cos(a), 25, 12 + 3.5 * np.sin(a)))
    p.box(-36, -10, 0, 12, -12, 12)                          # the low ribbed hall
    for x in np.linspace(-34, -12, 9):
        p.line((x, 0.5, 12.1), (x, 11.5, 12.1), PEARL, 0)
    p.windows(-8, 16, 1, 3, 10.3, 6, 1)
    return p.done()


def _goldarch(s):
    p = _Pen(s)
    for x0, x1, h in ((-26, -8, 18), (8, 22, 17)):          # the white blocks under hipped roofs
        p.box(x0, x1, 0, h, -9, 9)
        r0, r1 = x0 + 5, x1 - 5
        for x, xr in ((x0, r0), (x1, r1)):
            for z in (-9, 9):
                p.line((x, h, z), (xr, h + 5, 0), "#c6cde0", 0)
        p.line((r0, h + 5, 0), (r1, h + 5, 0), "#c6cde0", 0)
        for xs in (x0 + 3, x1 - 4):
            p.grid(xs, xs + 1.6, 2, h - 2, 9.1, 1, 6)
    p.box(-8, 8, 0, 26, -8, 8, GOLDA, 3)                    # the golden tower
    p.arc(0, 26, 8.0, 8, 6, 0.0, np.pi, GOLDA, 3)
    p.arc(0, 18, 8.1, 4, 4, 0.0, np.pi, GLASS, 1)          # its great arched window
    p.grid(-4, 4, 6, 18, 8.1, 3, 5)
    return p.done()


def _institute(s):
    p = _Pen(s)
    p.box(-14, 14, 0, 20, -12, 12)
    p.grid(-10, 10, 1, 17, 12.1, 6, 4)
    p.arc(0, 20, 12.0, 8, 3, 0.0, np.pi, TEAL, 3)          # a low crest over the centre
    for x0, x1 in ((-70, -14), (14, 70)):                    # the long halls
        p.box(x0, x1, 0, 10, -10, 10)
        p.windows(x0 + 2, x1 - 2, 2.5, 8, 10.1, 14, 2)
    return p.done()


SLATE = "#aab6d4"
SAND = "#f2dcb8"
_ROLE_OF = {GLASS: 1, TEAL: 1}


def _shape(spec, s):
    """A building from its shape list (model metres; x across the front, y up, z toward the viewer). Each item is
    (op, numbers..., optional colour). The front of the last box drawn is where the facade items go.
      box x0 x1 y0 y1 d          a block (its twelve edges), d deep, centred on z = 0
      glass x0 x1 y0 y1 nx ny    a glass grid on the front          win x0 x1 y0 y1 nx ny   warm windows
      arch x0 x1 y0 y1 n w       n tall arched windows              v / h x0 x1 y0 y1 n     vertical / level lines
      hip x0 x1 y d rise         a hipped roof on a block           gable x0 x1 y d rise    a gable facing front
      archtop x0 x1 y rise       a rounded top over a block         cyl cx cz r y0 y1 n     a cylinder (n rings)
      drum cx cz r y0 y1 n       a curved glass front (half drum)   ring cx cy r            a circle on the front
      arc cx cy rx ry            a half arc on the front            ln x0 y0 x1 y1          a line on the front
      canopy x0 x1 y depth       a flat canopy                      curve x0 y0 x1 y1 bulge a curved roof line
      waves x0 x1 y0 y1 n        n wavy vertical fins on the front"""
    p = _Pen(s)
    fz, dd = 6.0, 12.0
    for it in spec:
        op, a = it[0], list(it[1:])
        col = a.pop() if a and isinstance(a[-1], str) else None
        if op == "box":
            x0, x1, y0, y1, d = a
            fz, dd = d / 2.0, d
            c = col or PEARL
            p.box(x0, x1, y0, y1, -d / 2.0, d / 2.0, c, 0 if c == PEARL else 3)
        elif op == "glass":
            x0, x1, y0, y1, nx, ny = a
            p.grid(x0, x1, y0, y1, fz + 0.1, int(nx), int(ny), col or GLASS)
        elif op == "win":
            x0, x1, y0, y1, nx, ny = a
            p.windows(x0, x1, y0, y1, fz + 0.15, int(nx), int(ny), col or WARM)
        elif op == "arch":
            x0, x1, y0, y1, n, w = a
            p.arched(x0, x1, y0, y1, fz + 0.1, int(n), w, col or WARM)
        elif op in ("v", "h"):
            x0, x1, y0, y1, n = a
            c = col or PEARL
            r = _ROLE_OF.get(c, 0 if c == PEARL else 3)
            n = int(n)
            for k in range(n):
                u = 0.5 if n == 1 else k / (n - 1)
                if op == "v":
                    x = x0 + (x1 - x0) * u
                    p.line((x, y0, fz + 0.1), (x, y1, fz + 0.1), c, r)
                else:
                    y = y0 + (y1 - y0) * (0.0 if n == 1 else u)
                    p.line((x0, y, fz + 0.1), (x1, y, fz + 0.1), c, r)
        elif op == "hip":
            x0, x1, y, d, rise = a
            c = col or SLATE
            r = min(d / 2.0, (x1 - x0) * 0.3)
            for x, xr in ((x0, x0 + r), (x1, x1 - r)):
                for z in (-d / 2.0, d / 2.0):
                    p.line((x, y, z), (xr, y + rise, 0.0), c, 3)
            p.line((x0 + r, y + rise, 0.0), (x1 - r, y + rise, 0.0), c, 3)
        elif op == "gable":
            x0, x1, y, d, rise = a
            c = col or PEARL
            xm = 0.5 * (x0 + x1)
            for z in (-d / 2.0, d / 2.0):
                p.line((x0, y, z), (xm, y + rise, z), c, 0 if c == PEARL else 3)
                p.line((xm, y + rise, z), (x1, y, z), c, 0 if c == PEARL else 3)
            p.line((xm, y + rise, -d / 2.0), (xm, y + rise, d / 2.0), c, 0 if c == PEARL else 3)
        elif op == "archtop":
            x0, x1, y, rise = a
            for z in (-dd / 2.0, dd / 2.0):
                p.arc(0.5 * (x0 + x1), y, z, 0.5 * (x1 - x0), rise, 0.0, np.pi, col or PEARL, 0)
            p.line((0.5 * (x0 + x1), y + rise, -dd / 2.0), (0.5 * (x0 + x1), y + rise, dd / 2.0))
        elif op in ("cyl", "drum"):
            cx, cz, r, y0, y1, n = a
            c = col or (GLASS if op == "drum" else PEARL)
            half = op == "drum"
            m = max(int((np.pi if half else 2 * np.pi) * r / s), 8)
            ang = np.linspace(0.0, np.pi if half else 2 * np.pi, m, endpoint=half)
            for k in range(int(n)):
                y = y0 + (y1 - y0) * k / max(int(n) - 1, 1)
                p._put(np.stack([cx + r * np.cos(ang), np.full(m, y), cz + r * np.sin(ang)], 1), c,
                       _ROLE_OF.get(c, 0 if c == PEARL else 3))
            nv = max(int((np.pi if half else 2 * np.pi) * r / 2.6), 4) if half else 4
            for g in np.linspace(0.0, np.pi if half else 2 * np.pi, nv, endpoint=half):
                p.line((cx + r * np.cos(g), y0, cz + r * np.sin(g)), (cx + r * np.cos(g), y1, cz + r * np.sin(g)),
                       c, _ROLE_OF.get(c, 0))
            fz = cz + r
        elif op == "ring":
            cx, cy, r = a
            p.arc(cx, cy, fz + 0.2, r, r, 0.0, 2 * np.pi, col or GLASS, 3)
        elif op == "arc":
            cx, cy, rx, ry = a
            p.arc(cx, cy, fz + 0.1, rx, ry, 0.0, np.pi, col or PEARL, _ROLE_OF.get(col, 0))
        elif op == "ln":
            x0, y0, x1, y1 = a
            c = col or PEARL
            p.line((x0, y0, fz + 0.05), (x1, y1, fz + 0.05), c, _ROLE_OF.get(c, 0 if c == PEARL else 3))
        elif op == "canopy":
            x0, x1, y, depth = a
            p.poly([(x0, y, fz), (x0, y, fz + depth), (x1, y, fz + depth), (x1, y, fz)], col or PEARL, 0)
        elif op == "curve":
            x0, y0, x1, y1, b = a
            c = col or PEARL
            u = np.linspace(0.0, 1.0, max(int(abs(x1 - x0) / s), 6))
            pts = np.stack([x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + 4.0 * b * u * (1 - u), np.full(len(u), fz + 0.1)], 1)
            p._put(pts, c, _ROLE_OF.get(c, 0 if c == PEARL else 3))
        elif op == "waves":
            x0, x1, y0, y1, n = a
            c = col or GLASS
            yy = np.linspace(y0, y1, max(int((y1 - y0) / s), 8))
            for k in range(int(n)):
                x = x0 + (x1 - x0) * (k + 0.5) / n
                xs = x + 1.1 * np.sin(np.pi * 1.5 * (yy - y0) / (y1 - y0))
                p._put(np.stack([xs, yy, np.full(len(yy), fz + 0.3)], 1), c, 1)
        else:
            raise ValueError(f"unknown shape item {op}")
    return p.done()


# =========================================================================================================
# THE BUILDINGS: one source of truth, the catalogue in models/wmscog_churches.py (one entry per real church, its
# page and its parts); each is used exactly once around Zion. The first nineteen drawn before the catalogue
# existed keep their hand drawings here (LEGACY_SHAPES, keyed by the catalogue id); every other church is drawn
# from its parts by _parts below, in its own materials (glass grids, warm lit windows, golden, brick, stone).
# =========================================================================================================
LEGACY_SHAPES = {
    "kr_homaesil": _homaesil,
    "kr_yuseong_daejeon": _sejong,
    "kr_moran_seongnam": _moran,
    "kr_bitgaram_naju": _sail,
    "au_sydney": _sydney,
    "br_brasilia": _brazil,
    "kr_gwanjeo_daejeon": _goldarch,
    "kr_training_institute": _institute,
    "au_adelaide": [
        ("box", -6, 14, 0, 18, 18, ROSE), ("h", -6, 14, 3, 15, 4, ROSE),
        ("box", -22, 10, 0, 7, 12, ROSE), ("hip", -24, 12, 7, 14, 3, SLATE), ("win", -18, -12, 2, 5, 2, 1),
        ("box", 14, 24, 0, 9, 10, ROSE)],
    "kr_gwanggyo_suwon": [
        ("box", -20, 10, 0, 24, 16), ("glass", -16, -2, 6, 18, 6, 2), ("glass", -20, -18, 0, 24, 1, 8),
        ("glass", 2, 6, 0, 24, 1, 8), ("win", -18, 8, 2, 4, 8, 1),
        ("box", 10, 26, 0, 14, 14), ("curve", 10, 14, 26, 14, 2.0)],
    "kr_yeongjongdo_incheon": [
        ("box", -14, 8, 0, 22, 14), ("glass", -14, 8, 1, 20, 8, 7), ("box", -18, -14, 0, 22, 14),
        ("box", 8, 16, 0, 30, 14), ("glass", 8, 10, 2, 28, 1, 8)],
    "kr_janggi_gimpo": [
        ("box", -28, -8, 0, 18, 14), ("arch", -26, -10, 3, 13, 5, 1.6),
        ("box", -8, 10, 0, 24, 16), ("glass", -8, -5, 2, 22, 1, 7),
        ("box", 10, 26, 0, 22, 14), ("gable", 10, 26, 22, 14, 3), ("arch", 12, 24, 3, 15, 4, 1.6),
        ("canopy", 12, 22, 4, 4)],
    "kr_jungang_dongducheon": [
        ("box", -24, 14, 0, 12, 16), ("v", -22, 12, 1, 11, 12), ("hip", -24, 14, 12, 16, 3, GLASS),
        ("box", -30, -24, 0, 15, 10), ("glass", -29, -25, 2, 8, 2, 2)],
    "kr_byeolgaram_namyangju": [
        ("box", -22, -14, 0, 26, 10), ("glass", -22, -14, 1, 25, 3, 10),
        ("box", -14, 4, 0, 26, 14), ("arch", -12, 0, 10, 20, 3, 2.4), ("v", -14, 4, 8, 24, 4),
        ("canopy", -8, 2, 4, 5), ("glass", 4, 8, 2, 22, 1, 7), ("box", 8, 24, 0, 22, 14)],
    "kr_cheoin_yongin": [
        ("box", -5, 5, 0, 38, 8), ("ln", -5, 38, 5, 41), ("ln", 5, 41, 5, 38), ("glass", -1, 1, 4, 34, 1, 9),
        ("box", -18, -5, 0, 20, 14), ("arch", -14, -8, 6, 16, 2, 1.8),
        ("box", 5, 18, 0, 20, 14), ("arch", 8, 14, 6, 16, 2, 1.8)],
    "kr_sejong": [
        ("box", -20, 16, 0, 26, 16), ("glass", -16, 8, 6, 24, 10, 7), ("v", 10, 15, 4, 25, 4),
        ("box", -24, -20, 0, 24, 10), ("canopy", -16, 0, 4, 4)],
    "kr_deokyang_goyang": [
        ("box", -10, 22, 0, 34, 16), ("glass", -10, 10, 1, 26, 6, 8), ("box", -18, -10, 0, 32, 10)],
    "kr_samsong_goyang": [
        ("box", -24, -4, 0, 24, 14), ("v", -22, -6, 2, 22, 5, GLASS), ("box", -4, 4, 0, 30, 12),
        ("glass", -4, 4, 1, 30, 2, 10), ("box", 4, 12, 0, 32, 12), ("glass", 6, 10, 4, 30, 1, 8),
        ("box", 12, 22, 0, 22, 12)],
    "kr_giheung_yongin": [
        ("box", -26, -8, 0, 16, 14), ("glass", -24, -10, 4, 14, 4, 3), ("box", -8, 2, 0, 24, 12),
        ("glass", -6, 0, 2, 22, 2, 7), ("box", -6, 0, 24, 28, 8), ("box", 2, 22, 0, 22, 14),
        ("glass", 2, 22, 1, 22, 6, 7, TEAL)],
}


def _load_catalogue():
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "wmscog_churches.py")
    spec = importlib.util.spec_from_file_location("s11_wmscog_churches", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.all_buildings()


# the catalogue's materials as light: (colour, role) with role 0 outline, 1 glass, 2 window, 3 accent
_MAT = {"pearl": (PEARL, 0), "white": ("#f4f6ff", 0), "glass": (GLASS, 1), "teal": (TEAL, 1), "gold": (GOLDA, 3),
        "rose": (ROSE, 3), "warm": ("#f3b98e", 3), "stone": ("#e9dfcc", 0), "grey": (SLATE, 3)}


def _parts(parts, s):
    """A building from its catalogue parts (catalogue metres: x across, y up, the front faces -z). The pen's
    front faces +z, so z is turned round (z -> -z) and x keeps its side."""
    p = _Pen(s)

    def W(x, y, z):
        return (x, y, -z)

    def L(a, b, c, r):
        p.line(W(*a), W(*b), c, r)

    for q in parts:
        k = q["kind"]
        x, z, y0 = q["x"], q["z"], q["y0"]
        w, d, h = q.get("w", 0.0), q.get("d", 0.0), q.get("h", 0.0)
        c, r = _MAT.get(q.get("col", "pearl"), (PEARL, 0))
        ang = np.radians(q.get("rot", 0.0))

        def rl(u, v):
            return x + u * np.cos(ang) - v * np.sin(ang), z + u * np.sin(ang) + v * np.cos(ang)

        if k in ("box", "canopy", "gable", "hip", "spire", "steps"):
            cs = [rl(sx * w / 2, sz * d / 2) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        if k in ("box", "canopy"):
            for i in range(4):
                (xa, za), (xb, zb) = cs[i], cs[(i + 1) % 4]
                L((xa, y0 + h, za), (xb, y0 + h, zb), c, r)
                L((xa, y0, za), (xb, y0, zb), c, r)
                if k == "box":
                    L((xa, y0, za), (xa, y0 + h, za), c, r)
            if k == "box" and r == 1:                          # a glass block shows its floors
                for yy in np.arange(y0 + 3.5, y0 + h - 0.5, 3.5):
                    L((cs[0][0], yy, cs[0][1]), (cs[1][0], yy, cs[1][1]), c, r)
        elif k in ("gable", "hip"):
            for i in range(4):
                (xa, za), (xb, zb) = cs[i], cs[(i + 1) % 4]
                L((xa, y0, za), (xb, y0, zb), c, r)
            along_x = (q.get("axis", "x") == "x") if k == "gable" else w >= d
            inset = 0.0 if k == "gable" else min(w, d) / 2.0
            if along_x:
                t1, t2 = rl(-w / 2 + inset, 0.0), rl(w / 2 - inset, 0.0)
                pairs = ((0, t1), (3, t1), (1, t2), (2, t2))
            else:
                t1, t2 = rl(0.0, -d / 2 + inset), rl(0.0, d / 2 - inset)
                pairs = ((0, t1), (1, t1), (3, t2), (2, t2))
            L((t1[0], y0 + h, t1[1]), (t2[0], y0 + h, t2[1]), c, r)
            for i, t in pairs:
                L((cs[i][0], y0, cs[i][1]), (t[0], y0 + h, t[1]), c, r)
        elif k == "spire":
            for i in range(4):
                (xa, za), (xb, zb) = cs[i], cs[(i + 1) % 4]
                L((xa, y0, za), (xb, y0, zb), c, r)
                L((xa, y0, za), (x, y0 + h, z), c, r)
        elif k == "steps":
            n = int(q.get("n", 6))
            for i in range(n + 1):
                v = -d / 2 + d * i / n
                yy = y0 + h * min(i + 1, n) / n
                a_, b_ = rl(-w / 2, v), rl(w / 2, v)
                L((a_[0], yy, a_[1]), (b_[0], yy, b_[1]), c, r)
        elif k in ("cyl", "dome"):
            rr = w / 2.0
            m = max(int(2 * np.pi * rr / s), 10)
            aa = np.linspace(0.0, 2 * np.pi, m)
            if k == "cyl":
                rings = [(y0 + h * f, rr) for f in np.linspace(0.0, 1.0, max(2, int(h / 4.0) + 1))]
            else:
                rings = [(y0 + h * np.sin(np.pi / 2 * f), rr * np.cos(np.pi / 2 * f)) for f in (0.0, 0.35, 0.7)]
                L((x - rr, y0, z), (x, y0 + h, z), c, r)
                L((x, y0 + h, z), (x + rr, y0, z), c, r)
            for yy, ra in rings:
                p._put(np.stack([x + ra * np.cos(aa), np.full(m, yy), -(z + ra * np.sin(aa))], 1), c, r)
            if k == "cyl":
                for g in np.radians([200, 250, 290, 340]):
                    L((x + rr * np.cos(g), y0, z + rr * np.sin(g)), (x + rr * np.cos(g), y0 + h, z + rr * np.sin(g)), c, r)
        elif k == "cross":
            L((x, y0, z), (x, y0 + h, z), c, r)
            L((x - w / 2, y0 + 0.7 * h, z), (x + w / 2, y0 + 0.7 * h, z), c, r)
        else:                                                  # the parts drawn on a face
            f = q.get("face", "front")
            out = {"front": -0.15, "back": 0.15}.get(f, 0.0)

            def F(u, yy, o=0.0):
                if f == "front":
                    return (x + u, yy, z + out - o)
                if f == "back":
                    return (x - u, yy, z + out + o)
                if f == "left":
                    return (x - 0.15 - o, yy, z - u)
                return (x + 0.15 + o, yy, z + u)

            if k in ("windows", "arch_windows"):
                n, rows = int(q.get("n", 1)), int(q.get("rows", 1))
                cw, ch = w / n, h / rows
                ww, wh = 0.62 * cw, 0.72 * ch
                for i in range(n):
                    for j in range(rows):
                        u0, v0 = -w / 2 + cw * (i + 0.5), y0 + ch * (j + 0.5)
                        if k == "windows":
                            pts = [(u0 - ww / 2, v0 - wh / 2), (u0 + ww / 2, v0 - wh / 2), (u0 + ww / 2, v0 + wh / 2),
                                   (u0 - ww / 2, v0 + wh / 2), (u0 - ww / 2, v0 - wh / 2)]
                        else:
                            ra = ww / 2.0
                            top = v0 + wh / 2 - ra
                            pts = [(u0 - ra, top), (u0 - ra, v0 - wh / 2), (u0 + ra, v0 - wh / 2), (u0 + ra, top)]
                            pts += [(u0 + ra * np.cos(np.pi * t / 8), top + ra * np.sin(np.pi * t / 8)) for t in range(9)]
                        wc, wr = (c, r) if r == 1 else (WARM, 3)
                        for (ua, va), (ub, vb) in zip(pts[:-1], pts[1:]):
                            L(F(ua, va), F(ub, vb), wc, wr)
                        p._put([W(*F(u0, v0))], WARM, 2)       # a warm light in every window
            elif k == "glass_band":
                sh = np.tan(np.radians(q.get("angle", 0.0))) * h
                pts = [(-w / 2, y0), (w / 2, y0), (w / 2 + sh, y0 + h), (-w / 2 + sh, y0 + h), (-w / 2, y0)]
                for (ua, va), (ub, vb) in zip(pts[:-1], pts[1:]):
                    L(F(ua, va), F(ub, vb), c, 1)
                nm = max(1, int(w / 2.5))
                for i in range(1, nm):
                    u = -w / 2 + w * i / nm
                    L(F(u, y0), F(u + sh, y0 + h), c, 1)
                for yy in np.arange(y0 + 3.5, y0 + h - 0.5, 3.5):
                    u = sh * (yy - y0) / max(h, 1e-6)
                    L(F(-w / 2 + u, yy), F(w / 2 + u, yy), c, 1)
            elif k == "fin_row":
                n = int(q.get("n", 5))
                for i in range(n):
                    u = -w / 2 + w * (i + 0.5) / n
                    L(F(u, y0, d), F(u, y0 + h, d), c, r if r else 3)
            elif k == "disc":
                ra = w / 2.0
                pts = [F(ra * np.cos(2 * np.pi * i / 20), y0 + ra * np.sin(2 * np.pi * i / 20)) for i in range(21)]
                for a_, b_ in zip(pts[:-1], pts[1:]):
                    L(a_, b_, c, 3)
            else:
                raise ValueError(f"unknown part kind {k}")
    return p.done()


def _entry(b):
    shape = LEGACY_SHAPES.get(b["id"])
    if shape is None:
        parts = b["parts"]
        shape = (lambda step, parts=parts: _parts(parts, step))
    return dict(id=b["id"], name=b["name"], city=b["city"], country=b["country"], url=b["source"], shape=shape)


BUILDINGS = [_entry(b) for b in _load_catalogue()]
assert len({b["id"] for b in BUILDINGS}) == len(BUILDINGS)
assert all(b["parts"] or b["id"] in LEGACY_SHAPES for b in _load_catalogue())


def _model(b, step):
    sh = b["shape"]
    return sh(step) if callable(sh) else _shape(sh, step)


def _place(m, base, ex, ey, ez, k):
    """The model's points placed at base, along the axes ex (across), ey (up), ez (front), scaled by k."""
    P = m["pos"] * k
    return base[None, :] + P[:, :1] * ex[None, :] + P[:, 1:2] * ey[None, :] + P[:, 2:3] * ez[None, :]


def _snap(t):
    """The first beat at or just after t (so each church ignites on a beat)."""
    i = int(np.searchsorted(BEATS, t - 0.06))
    return float(BEATS[min(i, len(BEATS) - 1)]) if t < LIVE else float(t)


def _reading(t):
    """1 while a phrase is on screen (as the music thread measures it), so the churches calm under the words."""
    v = 0.0
    for ph in getattr(H, "PHRASE_LIST", []):
        ti, r0, r1, to = ph[1]
        if ti - 0.4 <= t <= to + 0.4:
            v = max(v, 0.6 * _sc(ti - 0.4, ti, t) * (1.0 - _sc(to, to + 0.4, t)) + 0.4 * _sc(ti, r0, t) * (1.0 - _sc(r1, to, t)))
    return v


# =========================================================================================================
# WHEN: the churches are established on the music, a few at first, then waves on the big hits
# (time, how many at once); the list is cut or padded to the number of buildings
# =========================================================================================================
WAVES = [
    # verse 1: the first Zion views, a handful
    (55.4, 1), (58.4, 1), (64.2, 1), (69.4, 1),
    # chorus 1
    (82.08, 3), (86.7, 1), (90.72, 2), (97.7, 1), (99.4, 1), (105.14, 2),
    # verse 2
    (121.32, 1), (125.92, 1), (127.64, 1), (130.29, 2), (134.54, 2), (139.2, 1), (144.4, 1), (146.7, 2),
    (150.2, 1), (154.2, 1), (155.34, 1),
    # chorus 2
    (162.86, 4), (165.16, 2), (168.0, 1), (171.48, 3), (175.0, 1), (178.4, 1), (180.7, 2), (183.0, 1),
    (185.92, 1), (189.96, 1),
    # the coda
    (197.2, 1), (199.62, 1), (201.73, 5), (205.98, 1), (211.6, 3), (214.0, 1), (218.1, 1), (220.2, 1),
    (224.03, 2), (228.6, 1), (235.6, 1),
]


def _birth_times(n):
    """One birth time per church. Verse 1 keeps its handful; every later wave grows in proportion, so however
    many churches the catalogue holds, they are all established by the coda's last wave, more and more on the
    big hits (chorus 2 and the coda)."""
    head, rest = WAVES[:4], WAVES[4:]
    need = max(n - sum(c for _, c in head), 0)
    w = np.array([c * (1.6 if t >= 160.0 else 1.0) for t, c in rest], np.float64)
    want = need * w / w.sum()
    cnt = np.floor(want).astype(int)
    for i in np.argsort(-(want - cnt))[: need - cnt.sum()]:
        cnt[i] += 1
    out = []
    for t, c in head:
        out += [_snap(t)] * c
    for (t, _), c in zip(rest, cnt):
        # a big wave is spread over the beats right after its hit (at most 4 on one beat), so it reads as a
        # ripple of new churches, not one flash
        for j in range(int(c)):
            out.append(_snap(t + 0.42 * (j // 4)))
    return sorted(out)[:n]


# =========================================================================================================
# WHERE: four widening bands round Mount Zion; the order of the bands is the order of growth
# (inner radius, outer radius from the foot of the mountain, share of the churches, world scale, drawing step)
# =========================================================================================================
BANDS = [((430.0, 560.0, 680.0), 0.24, 1.3, 0.8),                   # the near shore (four flank the march)
         ((820.0, 980.0, 1140.0, 1300.0), 0.32, 1.85, 1.0),         # out on the sea of glass
         ((1450.0, 1660.0, 1880.0, 2120.0), 0.27, 2.35, 1.3),      # the far shore
         ((2450.0, 2750.0, 3050.0), 0.17, 3.0, 1.6)]               # the foot of the hills
# the five lanes of the rivers of people (azimuth round Zion from +z toward +x, how far out they reach); a clear
# corridor of about 35 m either side of each (the widened river is up to 30 m across, plus 20 m each side)
LANES = [(0.0, 1500.0), (-36.0, 760.0), (36.0, 760.0), (-72.0, 760.0), (72.0, 760.0)]
# world boxes (x0, x1, z0, z1) a low camera crosses: the shockwave chase over the sea at 2:46.5 to 2:50.5
KEEP_CLEAR = [(100.0, 300.0, -100.0, 500.0)]


def _mount_y(x, z):
    """The height of Mount Zion's terraces at (x, z) (0 off the mountain)."""
    r = np.hypot(np.asarray(x, np.float64) - ZC[0], np.asarray(z, np.float64) - ZC[2])
    k = np.clip(np.floor((tier_r(0) - r) / TIER_STEP), 0, N_TIER - 1)
    return np.where(r <= tier_r(0), SUMMIT * (k + 1) / N_TIER, -1.0)


def _camera_samples():
    pts = []
    for s in H.SHOTS:
        if s["kind"] == "globe":
            continue
        for t in np.arange(s["t0"], s["t1"], 0.25):
            pts.append(np.asarray(H.CAMERA.state(float(t)).pos, np.float64))
    return np.array(pts)


# Anthony (2026-11-19, later): "The heavenly city buildings are the real church buildings in Korea. The
# international churches should be scattered throughout, outside of the mountain."
#   The Korean churches stand on Mount Zion's terraces as the heavenly city, one on each city plot: the ZION
#   builder's CITY_SLOTS (s11_zion.py, read only) when it exposes them, else the stand-in plots below (the back
#   band of each terrace, on the seen side of the mountain, clear of the great stairways). Biggest buildings on
#   the widest plots, scaled to fit, standing on the terrace floor, facing out from the mountain. Korean churches
#   beyond the plots stand on the near shore.
#   The churches of the other nations are scattered like towns over the sea, the far shores and the hills: small
#   clusters, each church facing Zion, still on the ground, clear of the river lanes and the camera paths.
CITY_STEP = 27.0                      # stand-in plots: spacing along a terrace's back band (metres)
CITY_FRONT = np.radians(118.0)        # the seen side of the mountain (azimuth either side of the avenue)
TOWN_BANDS = (900.0, 3100.0)          # the international towns: from the sea out to the foot of the hills


def _city_slots():
    """Plots of the heavenly city: dicts (x, y, z, facing (radians, azimuth the front looks toward, from +z),
    max_w, max_d, terrace, born or None)."""
    try:
        import songs.s11_zion as S_ZION
        slots = getattr(S_ZION, "CITY_SLOTS", None)
        if slots:
            return [dict(s) for s in slots]
    except Exception:
        pass
    out = []
    for k in range(N_TIER - 1):                       # terrace k's floor runs from tier_r(k + 1) to tier_r(k)
        rb = tier_r(k + 1) + 0.55 * TIER_STEP
        m = int(2 * CITY_FRONT * rb / CITY_STEP)
        for a in np.linspace(-CITY_FRONT, CITY_FRONT, m):
            if min(abs(np.angle(np.exp(1j * (a - sa)))) for sa in np.radians([0.0, -36.0, 36.0, -72.0, 72.0])) * rb < 16.0:
                continue                                # the great stairways stay clear
            out.append(dict(x=float(ZC[0] + rb * np.sin(a)), y=float(SUMMIT * (k + 1) / N_TIER),
                            z=float(ZC[2] + rb * np.cos(a)), facing=float(a), max_w=0.85 * CITY_STEP,
                            max_d=0.6 * TIER_STEP, terrace=k, born=None))
    return out


def _layout():
    """Each building gets a place, a turn, a scale and a birth time (deterministic)."""
    rng = np.random.default_rng(1907)
    cams = _camera_samples()
    out, placed = [], []

    def free(base, fp, h, cam_r=90.0, gap=8.0):
        if base[2] > ZC[2] and abs(base[0]) < 70.0 + fp and base[1] < 1.0:     # the avenue and march corridor
            return False
        rel = base - ZC
        rr = float(np.hypot(rel[0], rel[2]))
        az = np.degrees(np.arctan2(rel[0], rel[2]))
        if base[1] < 1.0:
            for lane, reach in LANES:                               # the rivers of people walking to Zion
                da = np.radians(abs((az - lane + 180.0) % 360.0 - 180.0))
                if da < np.pi / 2 and rr * np.sin(da) < fp + 35.0 and rr * np.cos(da) < reach + fp:
                    return False
            for x0, x1, z0, z1 in KEEP_CLEAR:                       # low camera chases over the sea
                if x0 - fp < base[0] < x1 + fp and z0 - fp < base[2] < z1 + fp:
                    return False
        if any(np.linalg.norm((base - q)[[0, 2]]) < fp + qf + gap for q, qf in placed):
            return False
        d = np.hypot(cams[:, 0] - base[0], cams[:, 2] - base[2])
        return not np.any((d < fp + cam_r) & (cams[:, 1] < base[1] + h + 0.6 * cam_r))

    def put(b, m, base, face, k, bi, step, key):
        ey = _v(0.0, 1.0, 0.0)
        ex = np.cross(ey, face)
        w = float(np.ptp(m["pos"][:, 0])) * k
        out.append(dict(b=b, m=m, base=base, ex=ex, ey=ey, ez=face, k=k, h=m["h"] * k, w=w, band=bi, step=step,
                        key=key, es=float(np.clip(0.42 * w, 8.0, 30.0))))

    kr = [i for i in rng.permutation(len(BUILDINGS)) if BUILDINGS[i]["country"] == "Korea"]
    other = [i for i in rng.permutation(len(BUILDINGS)) if BUILDINGS[i]["country"] != "Korea"]
    # 1) the heavenly city: the biggest Korean churches on the widest plots, each scaled to fit its plot
    slots = sorted(_city_slots(), key=lambda q: -q["max_w"] * q["max_d"])
    mods = {i: _model(BUILDINGS[i], 0.6) for i in kr}
    size = {i: float(np.ptp(mods[i]["pos"][:, 0])) * float(np.ptp(mods[i]["pos"][:, 2])) for i in kr}
    kr_big = sorted(kr, key=lambda i: -size[i])
    left = []
    for i in kr_big:
        m = mods[i]
        w, d = float(np.ptp(m["pos"][:, 0])), float(np.ptp(m["pos"][:, 2]))
        done = False
        for q in list(slots):
            k = min(1.0, q["max_w"] / max(w, 1.0), q["max_d"] / max(d, 1.0))
            if k < 0.42:                                            # too big for this plot (kept for the shore)
                continue
            base = _v(q["x"], q["y"], q["z"])
            fp = 0.5 * max(w, d) * k
            if not free(base, 0.5 * min(w, q["max_w"]), m["h"] * k, cam_r=6.0, gap=-6.0):          # (near cameras fade it out anyway)
                continue
            slots.remove(q)
            a = q["facing"]
            face = _v(np.sin(a), 0.0, np.cos(a))
            key = (q["born"] if q.get("born") is not None else None)
            put(BUILDINGS[i], m, base, face, k, 0, 0.6,
                ("t", key) if key is not None else (0.0 + 0.12 * q["terrace"] + abs(np.angle(np.exp(1j * a))) / 30.0))
            placed.append((base, fp))
            done = True
            break
        if not done:
            left.append(i)
    # 2) Korean churches beyond the plots: on the near shore, in arcs round the foot of the mountain
    n_near = len(left)
    for j, i in enumerate(left):
        m = _model(BUILDINGS[i], 0.8)
        k = 1.3
        fp = 0.5 * float(np.ptp(m["pos"][:, 0])) * k + 6.0
        for tries in range(600):
            r = 420.0 + 260.0 * rng.random()
            a = np.radians(-150.0 + 300.0 * rng.random())
            base = ZC + _v(r * np.sin(a), 0.0, r * np.cos(a))
            if free(base, fp, m["h"] * k):
                break
        else:
            continue
        put(BUILDINGS[i], m, base, _unit(_v(ZC[0] - base[0], 0.0, ZC[2] - base[2])), k, 0, 0.8, 1.0 + j / max(n_near, 1))
        placed.append((base, fp))
    # 3) the other nations: towns scattered over the sea, the far shores and the hills
    n_town = max(8, len(other) // 4)
    towns = []
    while len(towns) < n_town:
        r = TOWN_BANDS[0] + (TOWN_BANDS[1] - TOWN_BANDS[0]) * rng.random() ** 0.8
        a = rng.uniform(-np.pi, np.pi)
        c = ZC + _v(r * np.sin(a), 0.0, r * np.cos(a))
        if all(np.linalg.norm((c - t)[[0, 2]]) > 260.0 for t in towns):
            towns.append(c)
    towns.sort(key=lambda c: np.linalg.norm((c - ZC)[[0, 2]]))
    for j, i in enumerate(other):
        tc = towns[j % len(towns)]
        rr = float(np.linalg.norm((tc - ZC)[[0, 2]]))
        bi = 1 if rr < 1350.0 else (2 if rr < 2300.0 else 3)
        step = (0.8, 1.0, 1.3, 1.6)[bi]
        k = (1.3, 1.85, 2.35, 3.0)[bi]
        m = _model(BUILDINGS[i], step)
        fp = 0.5 * float(np.ptp(m["pos"][:, 0])) * k + 6.0
        ok = False
        for tries in range(300):
            off = rng.normal(0.0, 70.0 + 25.0 * (tries // 60), 2)
            base = tc + _v(off[0], 0.0, off[1])
            if free(base, fp, m["h"] * k):
                ok = True
                break
        if not ok:
            for tries in range(600):
                r = TOWN_BANDS[0] + (TOWN_BANDS[1] - TOWN_BANDS[0]) * rng.random()
                a = rng.uniform(-np.pi, np.pi)
                base = ZC + _v(r * np.sin(a), 0.0, r * np.cos(a))
                if free(base, fp, m["h"] * k):
                    ok = True
                    break
        if not ok:
            raise RuntimeError(f"no free place for {BUILDINGS[i]['name']}")
        yaw = np.radians(rng.uniform(-30.0, 30.0))                 # towns: each turned a little its own way
        face = _unit(_v(ZC[0] - base[0], 0.0, ZC[2] - base[2]))
        face = _unit(face * np.cos(yaw) + np.cross(_v(0.0, 1.0, 0.0), face) * np.sin(yaw))
        put(BUILDINGS[i], m, base, face, k, bi, step, 2.0 + 0.6 * (j % len(towns)) / len(towns) + 0.4 * rng.random())
        placed.append((base, fp))
    # births: the city plots that carry their own time keep it; the rest in order of growth (the city terrace by
    # terrace from the front, then the near shore, then the towns)
    fixed = [c for c in out if isinstance(c["key"], tuple)]
    grow = [c for c in out if not isinstance(c["key"], tuple)]
    # the city and the nations grow together: the city from verse 1, the nations' towns joining from a quarter
    # of the way in, both spread to the end (each keeps its own order)
    city = sorted([c for c in grow if c["key"] < 2.0], key=lambda c: c["key"])
    town = sorted([c for c in grow if c["key"] >= 2.0], key=lambda c: c["key"])
    for j, c in enumerate(city):
        c["key"] = j / max(len(city), 1)
    for j, c in enumerate(town):
        c["key"] = 0.25 + 0.75 * j / max(len(town), 1)
    grow = sorted(grow, key=lambda c: c["key"])
    for c, tb in zip(grow, _birth_times(len(grow))):
        c["t"] = tb
    for c in fixed:
        c["t"] = float(_snap(c["key"][1]))
    out.sort(key=lambda c: c["t"])
    return out


# =========================================================================================================
# Seeing: shown only on Mount Zion's side of the film, calm under the words, hidden behind the mountain
# =========================================================================================================
_OCC = {"t": None, "v": None}
CHURCHES = []


def _visible(t):
    """How much of each church the camera sees past Mount Zion's terraces (0..1 each), once per frame."""
    if _OCC["t"] == t:
        return _OCC["v"]
    eye = np.asarray(H.CAMERA.state(t).pos, np.float64)
    v = np.ones(len(CHURCHES))
    u = np.linspace(0.03, 0.97, 28)
    for i, c in enumerate(CHURCHES):
        seen = 0.0
        for f in (0.15, 0.55, 0.95):
            q = c["base"] + _v(0.0, f * c["h"], 0.0)
            P = eye[None, :] + (q - eye)[None, :] * u[:, None]
            blocked = np.any(P[:, 1] < _mount_y(P[:, 0], P[:, 2]) - 0.5)
            seen += 0.0 if blocked else 1.0 / 3.0
        # never a close wireframe filling the frame: a church fades out as the camera comes within a few of
        # its own heights of it (low chases over the sea)
        dist = float(np.hypot(*(c["base"] - eye)[[0, 2]]))
        v[i] = seen * _sc(3.0 * c["h"] + 40.0, 6.0 * c["h"] + 80.0, dist)
    _OCC["t"], _OCC["v"] = t, v
    return v


_GUARD = {"t": None, "v": None}


def _phrase_guard(t):
    """Per church, 1 normally and toward 0 while a phrase reads if the church stands behind the words on
    screen (the phrases sit in the middle of the frame), so no church shows through or above a phrase."""
    if _GUARD["t"] == t:
        return _GUARD["v"]
    rd = _reading(t)
    v = np.ones(len(CHURCHES))
    if rd > 0.0 and CHURCHES:
        st = H.CAMERA.state(t)
        r, u, f = st.basis()
        eye = np.asarray(st.pos, np.float64)
        ty = np.tan(np.radians(st.fov) * 0.5)
        tx = ty * st.aspect
        for i, c in enumerate(CHURCHES):
            hit = False
            for fr in ((0.1, 0.5, 1.0, 1.0 + (1.2 * c["es"] + 2.0) / c["h"]) if _has_emblem(c) else (0.1, 0.5, 1.0)):
                q = c["base"] + _v(0.0, fr * c["h"], 0.0) - eye
                z = float(q @ f)
                if z <= 1.0:
                    continue
                x, y = float(q @ r) / (z * tx), float(q @ u) / (z * ty)
                if abs(x) < 0.62 and -0.42 < y < 0.62:
                    hit = True
                    break
            if hit:
                v[i] = 1.0 - 0.97 * min(1.0, 1.6 * rd)
    _GUARD["t"], _GUARD["v"] = t, v
    return v


def _base_gain(t):
    if globe_view(t) or shot_kind(t) == "sky":      # (from the orchestra on the clouds they read as clutter below)
        return 0.0
    rd = _reading(t)
    if stage_view(t):                  # behind the choir: held low, and lower still under a phrase (no haze on the singers)
        return 0.35 * (1.0 - 0.65 * rd) * (0.85 + 0.25 * beat_pulse(t))
    return (1.0 - 0.45 * rd) * (0.85 + 0.25 * beat_pulse(t))


def _fx(name, t):
    try:
        import songs.s11_music_fx as S_MUSIC
        return float(getattr(S_MUSIC, "fx_" + name)(t))
    except Exception:
        return 0.0


def _ripple(i, t):
    """A ring of light running outward from Zion through the churches on each big hit (the three slams and the
    strongest timpani): 0..1 for church i as the ring's front passes it (about 900 m a second)."""
    hits = _RIPPLE_HITS()
    c = CHURCHES[i]
    r = float(np.hypot(*(c["base"] - ZC)[[0, 2]]))
    v = 0.0
    for th, s in hits:
        dt = t - th
        if 0.0 <= dt < 4.0:
            v = max(v, s * float(np.exp(-((r - 900.0 * dt) / 140.0) ** 2)) * (1.0 - dt / 4.0))
    return v


_RH = []


def _RIPPLE_HITS():
    if not _RH:
        _RH.append(0)
        hits = [(float(x), 1.0) for x in SLAMS]
        try:
            import songs.s11_music_fx as S_MUSIC
            hits += [(a, 0.6 * s) for a, s in S_MUSIC.timp_hits(0.85)]
        except Exception:
            pass
        _RH.extend(sorted(hits))
    return _RH[1:]


class ChurchLight:
    """One real church in light, in two parts kept on the graphics card, each with its own life on the music
    (Anthony: "way more effects ... each different sound"):
      "frame"   its outline, glass and materials and a soft glow: a pulse on every kick, a flare on the brass for
                the towers (tall slim churches), and the ring of light that runs out from Zion on the big hits;
      "win"     its warm windows: they warm up and glow with the choir, and catch the ring too.
    Every point is born at the church's beat, from the ground up over half a second, with a small flash.
    All of it eases right down while a phrase reads."""
    static = True

    def __init__(self, i, part):
        c = CHURCHES[i]
        self.i, self.t0, self.part = i, c["t"], part
        self.tower = c["h"] > 1.15 * max(c["w"], 1.0)
        m, k, st = c["m"], c["k"], c["step"]
        role = m["role"]
        keep = (role == 2) if part == "win" else (role != 2)
        P = _place(m, c["base"], c["ex"], c["ey"], c["ez"], k)[keep]
        size = np.array([0.85 * st, 0.75 * st, 1.5, 0.95 * st])[role[keep]] * k
        alpha = np.array([0.22, 0.5, 1.0, 0.8])[role[keep]]   # outlines quiet: glass, windows, materials lead
        birth = (self.t0 + 0.5 * m["pos"][keep, 1] / m["h"]).astype(np.float32)
        fog = (0.6, 0.45, 0.35, 0.25)[c["band"]]
        h = c["h"]
        self.b = []
        if len(P):
            self.b.append(dict(pos=P, size=size, color=m["col"][keep], alpha=alpha.astype(np.float32), kind="spark",
                               emit=1.8, birth=birth, fade=0.25, flash=2.0, fog=fog, twinkle=0.2))
        if part == "frame":
            G = np.array([c["base"] + _v(0, 0.45 * h, 0), c["base"] + _v(0, 0.08 * h, 0)])
            self.b.append(dict(pos=G, size=np.array([2.2 * h, 3.4 * h]), color=lin("#a9ccff"),
                               alpha=np.array([0.035, 0.02], np.float32), kind="soft", emit=1.4,
                               birth=np.full(2, self.t0 + 0.3, np.float32), fade=0.6, fog=fog))

    def sample(self, t):
        return self.b or None

    def gain(self, t):
        if t < self.t0 - 0.05:
            return 0.0
        g = _base_gain(t)
        if g <= 0.0:
            return 0.0
        g *= float(_visible(t)[self.i]) * float(_phrase_guard(t)[self.i])
        if g <= 0.0:
            return 0.0
        rp = _ripple(self.i, t)
        if self.part == "win":
            mod = 0.65 + 0.75 * _fx("choir", t) + 0.6 * rp
        else:
            mod = 0.85 + 0.35 * _fx("kick", t) + (0.7 * _fx("brass", t) if self.tower else 0.0) + 0.8 * rp
        calm = 1.0 - 0.8 * _reading(t)
        return g * (1.0 + (mod - 1.0) * calm)


class Ignitions:
    """The moment each church is established: a column of light shoots up from it on its beat and fades into
    a faint standing glow (held down where the music already blazes and under the words)."""

    def __init__(self):
        self.u = np.linspace(0.0, 1.0, 16)

    def sample(self, t):
        g = _base_gain(t)
        if g <= 0.0:
            return None
        live = [i for i, c in enumerate(CHURCHES) if c["t"] - 0.05 <= t < c["t"] + 3.0]
        if not live:
            return None
        vis = _visible(t)
        calm = (1.0 - 0.6 * _reading(t)) * (1.0 - 0.5 * intensity(t))
        P, A, S = [], [], []
        for i in live:
            c = CHURCHES[i]
            fl = hit_pulse(t, [c["t"]], rise=0.02, fall=0.7) * calm * vis[i] * _phrase_guard(t)[i]
            if fl < 0.01:
                continue
            h = c["h"]
            top = h * (1.0 + 4.0 * _sc(c["t"], c["t"] + 0.5, t))
            P.append(c["base"][None, :] + (h + top * self.u)[:, None] * _v(0, 1, 0)[None, :])
            A.append(0.8 * fl * g * (1.0 - self.u) ** 1.6)
            S.append(np.full(len(self.u), 0.18 * h))
        if not P:
            return None
        return [dict(pos=np.concatenate(P), size=np.concatenate(S), color=lin("#d6e8ff"),
                     alpha=np.clip(np.concatenate(A), 0, 1).astype(np.float32), kind="soft", emit=1.8, fog=0.4,
                     reflect=False)]


# =========================================================================================================
# THE EMBLEM above every church (Anthony, 2026-11-19: "Have the Church of God symbol above the churches").
# The emblem is the one traced from Anthony's image in s11_church.py (emblem_mask, read only; never redrawn
# here), in the same glowing sky-blue look as on the church of light: a blue ring and globe, the white lettering
# and globe lines over them, the soft white ring between. Each floats centred above its church's roof, always
# facing the camera, about 0.42 of the building's width (at least about 3.5 percent of the frame's height, so
# far ones still read: at least about 5.5 percent of the frame height, every other one dropped past 2300 m); crisp flat dots that take no lens blur, the white lettering and globe lines brightest; near ones are drawn in full, far ones from a coarser trace (the ring, the globe and its white ring). It lights a beat after
# its church rises (a soft flash), then breathes with the choir; calmed with its church (under a phrase, in the
# stage views, behind the mountain, near the camera) and hidden behind the words like it.
# =========================================================================================================
_EMB = {}


def _emblem_sets():
    """Unit emblem points (x, y in -0.5..0.5, y up) by class, a full and a simple level, from the traced mask."""
    if _EMB:
        return _EMB
    import songs.s11_church as S_CHURCH
    m = S_CHURCH.emblem_mask()
    n = m.shape[0]

    def pts(cls, st):
        sub = m[::st, ::st]
        r, c = np.nonzero(sub == cls)
        k = sub.shape[0]
        return np.stack([(c - (k - 1) / 2.0) / k, -(r - (k - 1) / 2.0) / k], 1), st / n

    for lod, st in (("full", 2), ("far", 4)):
        _EMB[lod] = {cls: pts(cls, st) for cls in (1, 2, 3)}
    return _EMB


def _choir(t):
    try:
        import songs.s11_music_fx as S_MUSIC
        return float(S_MUSIC.fx_choir(t))
    except Exception:
        return 0.0


# Anthony (2026-11-19, later): "I want the original instructions about the emblems above the churches and on the
# earth. Only the Korean churches on the terraces don't need the emblem above them." So every church has its
# emblem except the heavenly city's (the churches standing on Zion's terraces, base above the sea).
EMBLEMS_ON = True


def _has_emblem(c):
    return EMBLEMS_ON and float(c["base"][1]) < 1.0


class Emblems:
    """Every church's emblem in light, facing the camera each frame (see the note above); none on the terraces."""
    wants_camera = True

    def sample(self, t, cam=None):
        if not EMBLEMS_ON:
            return None
        g0 = _base_gain(t)
        if g0 <= 0.0 or cam is None or not CHURCHES:
            return None
        sets = _emblem_sets()
        vis, guard = _visible(t), _phrase_guard(t)
        r, u, f = cam.basis()
        eye = np.asarray(cam.pos, np.float64)
        ty = np.tan(np.radians(cam.fov) * 0.5)
        breathe = 0.82 + 0.3 * _choir(t)
        acc = {k: ([], [], []) for k in ("blue_soft", "blue", "white", "ring")}
        shown = []
        for i, c in enumerate(CHURCHES):
            if not _has_emblem(c):
                continue
            te = c["t"] + 0.55
            if t < te:
                continue
            g = g0 * float(vis[i]) * float(guard[i])
            if g < 0.01:
                continue
            q = c["base"] + _v(0.0, c["h"], 0.0)
            dist = float(np.linalg.norm(q - eye))
            S = max(c["es"], 0.09 * ty * dist)                     # at least about 4.5 percent of the frame
            ctr = q + _v(0.0, 0.7 * S + 2.0, 0.0)
            zf = float((ctr - eye) @ f)
            if zf < 5.0:
                continue
            sx, sy, sr = float((ctr - eye) @ r) / zf, float((ctr - eye) @ u) / zf, 0.5 * S / zf
            if any((sx - ax) ** 2 + (sy - ay) ** 2 < (1.1 * (sr + ar)) ** 2 for ax, ay, ar in shown):
                continue                                           # a town's emblems never pile up: one per spot
            shown.append((sx, sy, sr))
            rise = _sc(te, te + 0.5, t)
            flash = hit_pulse(t, [te], rise=0.03, fall=0.6)
            a = g * rise * (breathe + 1.2 * flash)
            lod = "full" if dist < 900.0 else "far"
            if dist > 2300.0 and i % 2:                            # fewer, clearer emblems on the farthest rings
                continue
            for cls, key in ((1, "blue"), (2, "white"), (3, "ring")):
                P, cell = sets[lod][cls]
                W = ctr[None, :] + S * (P[:, :1] * r[None, :] + P[:, 1:2] * u[None, :])
                acc[key][0].append(W)
                acc[key][1].append(np.full(len(W), S * cell))
                acc[key][2].append(np.full(len(W), a))
                if cls == 1:
                    acc["blue_soft"][0].append(W[::3])
                    acc["blue_soft"][1].append(np.full(len(W[::3]), S * cell * 3.0))
                    acc["blue_soft"][2].append(np.full(len(W[::3]), a))
        out = []
        # crisp: the blue is flat dots (a disc with an edge, no glow); the white lettering and globe lines are the
        # brightest; none of it takes the lens blur, so it reads at half size
        look = {"blue_soft": ("#2a86ea", 0.5, 0.04, "soft", 1.0, 1.0),
                "blue": ("#1f6fd6", 0.95, 0.8, "disc", 0.75, 1.0),
                "white": ("#ffffff", 0.75, 0.75, "disc", 1.1, 1.0),
                "ring": ("#ffffff", 0.7, 0.3, "disc", 0.7, 1.0)}
        for key, (P, Sz, A) in acc.items():
            if not P:
                continue
            col, sk, al, kind, emit, cm = look[key]
            out.append(dict(pos=np.concatenate(P), size=np.concatenate(Sz) * sk, color=lin(col) * cm,
                            alpha=np.clip(np.concatenate(A) * al, 0, 1).astype(np.float32), kind=kind, emit=emit,
                            fog=0.2, reflect=False, dof=0, twinkle=0.0))
        return out or None


def add(scene):
    if os.environ.get("S11_CHURCHES_OFF"):      # (for cost checks only)
        return
    CHURCHES[:] = _layout()
    for i, c in enumerate(CHURCHES):
        scene.add(f"church of God {i:02d}", ChurchLight(i, "frame"))
        scene.add(f"church of God {i:02d} windows", ChurchLight(i, "win"))
    scene.add("churches established", Ignitions())
    if EMBLEMS_ON:
        scene.add("church emblems", Emblems())
