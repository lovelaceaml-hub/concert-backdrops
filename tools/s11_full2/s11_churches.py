"""Song 11 v2 round 7: more and more churches of God established around the world, modelled in light from
public photographs of real World Mission Society Church of God buildings (silhouettes only, no signs copied).
Owned by the churches thread. Imported by the core beside the other threads (before the music effects).
No em dash or en dash anywhere in this file.

Anthony (2026-11-19): "more and more churches are being established (reference real wmscog buildings; use
different ones)". The main temple is already the church of light (s11_church.py) and is not repeated here.

THE BUILDINGS (reference only: each is a silhouette drawn in light from the church's own published photographs;
no sign, emblem, lettering or picture is copied, and no AI image is used)
  1 homaesil  Homaesil Church, Suwon, Korea (Grand Prize, religious facilities, 2026 Chosun Future Architecture
              Awards): a low white stone wing with a screen of vertical fins, a blue glass block in the middle,
              and a slim white tower whose top is rounded like an arch, a blue glass strip up its face.
              https://watv.org/?p=158263
  2 sejong    Sejong Church, Korea (dedicated May 2022): two white stone blocks with rows of tall arched windows,
              joined by a taller shaft of blue glass running the full height.
              https://watv.org/church-dedication-service-sejong/
  3 moran     Moran Church, Seongnam, Korea (dedicated August 2022): a white box crossed by a slanting band of
              glass with a gold panel at its end, beside a tall slim tower and a blade that carries a disc on top.
              https://watv.org/church-dedication-service-moran/
  4 sail      a church dedicated in Gangwon Province, Korea (2023): a slender curved tower of blue glass, like a
              sail, beside a white block of tall arched windows under a thin flat roof band.
              https://watv.org/church-dedication-service-gangwon/
  5 sydney    Sydney Church, Australia (dedicated 2024, "a bright design with gray and orange tones"): a long low
              grey hall and a taller orange entrance block with a glass front.
              https://watv.org/church-dedication-service-australia/
  6 brazil    Manaus and Brasilia Churches, Brazil (dedicated April 2026, three floors): a block of blue glass
              with a white cylinder tower standing in front of it and a low ribbed hall to one side.
              https://watv.org/church-dedication-service-brazil/
  7 goldarch  a church dedicated in Seoul and Daejeon, Korea (2023; Eungwang, Jongno, Gwanjeo): white blocks under
              grey hipped roofs with blue glass strips, either side of a golden tower with a great arched window.
              https://watv.org/?p=92800
  8 institute the training institute in the church's own introduction photograph (long low halls either side of
              a taller glass centre block; probably the Okcheon Go and Come Training Institute, not confirmed).
              https://watv.org/church-intro/
  Text sources consulted for the floors and materials: https://english.watv.org/news/print.asp?idx=38397 (New
  Jerusalem Pangyo Temple: blue glass front, marble; already the church of light, so not modelled again) and
  https://english.watv.org/news/print.asp?idx=891 (Lima, Peru, a three-storey temple; no photograph found, so the
  Lima beacon on the Earth uses another model).

WHAT IT DOES (each church ignites on a beat with a flash, draws itself up from the ground in half a second,
then keeps a soft pulse on the beat; never all at once; dimmed while a phrase reads)
  On the Earth (globe shots): beacons at real cities, each a tiny building of light with a column of light.
    Verse 1 0:41.6 to 0:53.8: Korea first (Busan, Gwangju), then East Asia and Oceania (8).
    Verse 1 1:10.5 to 1:17.5 (all nations): the Americas, Europe and Africa (10 more).
    Coda world finale 3:44 to 3:58: every land (18 more), all of them lit under the end card.
  Around Zion: on the far shores of the mirror sea, a ring of churches of light round Mount Zion, 1400 m out,
    growing from the two just behind the city's flanks outward: 8 in verse 2 (2:06 to 2:34), 7 in chorus 2
    (2:42 to 3:16), 5 in the coda (3:21 to 3:58).
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


MODELS = dict(homaesil=_homaesil, sejong=_sejong, moran=_moran, sail=_sail, sydney=_sydney, brazil=_brazil,
              goldarch=_goldarch, institute=_institute)


def _place(m, base, ex, ey, ez, k):
    """The model's points placed at base, along the axes ex (across), ey (up), ez (front), scaled by k."""
    P = m["pos"] * k
    return base[None, :] + P[:, :1] * ex[None, :] + P[:, 1:2] * ey[None, :] + P[:, 2:3] * ez[None, :]


def _snap(t):
    """The first beat at or just after t (so each church ignites on a beat)."""
    i = int(np.searchsorted(BEATS, t - 0.06))
    return float(BEATS[min(i, len(BEATS) - 1)]) if t < LIVE else float(t)


def _reading(t):
    """1 while a phrase is on screen (as the music thread measures it), so the flashes calm under the words."""
    v = 0.0
    for ph in getattr(H, "PHRASE_LIST", []):
        ti, r0, r1, to = ph[1]
        if ti - 0.4 <= t <= to + 0.4:
            v = max(v, 0.6 * _sc(ti - 0.4, ti, t) * (1.0 - _sc(to, to + 0.4, t)) + 0.4 * _sc(ti, r0, t) * (1.0 - _sc(r1, to, t)))
    return v


def _rise(t, ti, dur=0.5):
    return _sc(ti, ti + dur, t)


# =========================================================================================================
# On the Earth: beacons at real cities, more each time the Earth is seen
# =========================================================================================================
# (lat, lon, model, the time it ignites before snapping to the beat)
CITIES = [
    # verse 1, the first Earth: Korea first, then East Asia, the Pacific and Oceania
    (35.18, 129.07, "goldarch", 42.9), (35.16, 126.85, "sejong", 44.4), (35.68, 139.69, "moran", 46.0),
    (14.60, 120.98, "sail", 47.5), (47.92, 106.92, "homaesil", 49.0), (13.75, 100.50, "brazil", 50.4),
    (-33.87, 151.21, "sydney", 51.8), (27.70, 85.32, "institute", 53.0),
    # verse 1, all nations: the Americas, Europe and Africa
    (40.98, -74.12, "homaesil", 70.9), (-12.05, -77.04, "sail", 71.5), (-26.20, 28.05, "sejong", 72.1),
    (51.50, -0.13, "goldarch", 72.7), (19.43, -99.13, "moran", 73.3), (-3.12, -60.02, "brazil", 74.56),
    (-15.79, -47.88, "brazil", 75.2), (34.05, -118.24, "sydney", 75.8), (-1.29, 36.82, "institute", 76.4),
    (28.61, 77.21, "sail", 77.0),
    # the coda's world finale: every land
    (52.52, 13.40, "sejong", 224.03), (40.42, -3.70, "moran", 224.6), (6.52, 3.38, "homaesil", 225.2),
    (4.71, -74.07, "goldarch", 225.8), (-33.45, -70.67, "sail", 226.4), (-34.60, -58.38, "sydney", 227.0),
    (43.65, -79.38, "institute", 227.6), (41.88, -87.63, "brazil", 228.6), (-36.85, 174.76, "moran", 229.2),
    (-31.95, 115.86, "sejong", 229.8), (-6.21, 106.85, "goldarch", 230.4), (55.75, 37.62, "homaesil", 231.0),
    (30.04, 31.24, "sail", 231.6), (64.15, -21.94, "sydney", 232.2), (-18.91, 47.52, "brazil", 232.8),
    (49.28, -123.12, "goldarch", 233.4), (21.31, -157.86, "moran", 234.0), (59.33, 18.07, "institute", 234.6),
]
CITIES = [(la, lo, m, _snap(t)) for la, lo, m, t in CITIES]


class EarthChurches:
    """Each lit city: a tiny church of light standing on the land, facing the camera, under a column of light
    that flares on its beat and settles to a soft glow that breathes with the beat."""
    wants_camera = True

    def __init__(self):
        self.m = {k: f(2.2) for k, f in MODELS.items()}

    def sample(self, t, cam=None):
        if cam is None or not globe_view(t):
            return None
        lit = [c for c in CITIES if c[3] <= t]
        if not lit:
            return None
        c, M, R = GLOBE._view(t, cam)
        T = M @ GLOBE.turn(t)
        eye = np.asarray(cam.pos, np.float64)
        quiet = 1.0 - 0.55 * _reading(t)
        bp = beat_pulse(t)
        P, C, A, S = [], [], [], []
        cols, cola, cols_s, colb = [], [], [], []
        for la, lo, mk, ti in lit:
            n = _earth(la, lo) @ T.T
            n = n / np.linalg.norm(n)
            base = c + R * 1.004 * n
            vd = eye - base
            face = float(n @ _unit(vd))
            if face < 0.2:
                continue
            fk = _sc(0.2, 0.45, face)
            # drawn as an elevation facing the lens (a flat church of light, like a pin standing on the land):
            # up is the land's normal as the camera sees it, leaning toward the screen's up so it always reads
            d = _unit(vd)
            upw = _v(0.0, 1.0, 0.0)
            ey = _unit((n - (n @ d) * d) + 0.5 * (upw - (upw @ d) * d))
            ex = np.cross(ey, d)
            ez = 0.15 * d
            m = self.m[mk]
            k = R * 0.075 / max(m["h"], 1.0)                 # each church about a thirteenth of the Earth's radius
            up = _rise(t, ti, 0.45)
            q = m["pos"]
            keep = q[:, 1] <= up * m["h"] + 1e-6
            pts = _place(m, base, ex, ey, ez, k)[keep]
            fl = hit_pulse(t, [ti], rise=0.02, fall=0.5)
            a = np.where(m["role"][keep] == 1, 0.55, 0.95) * fk * (1.0 + 0.8 * fl * quiet + 0.25 * bp)
            P.append(pts)
            C.append(m["col"][keep])
            A.append(a)
            # the column of light: a flare on the beat, then a soft standing glow
            top = 0.55 * R * (0.35 + 0.65 * _sc(ti, ti + 0.6, t))
            u = np.linspace(0.0, 1.0, 14)
            col_p = base[None, :] + (k * m["h"] * 0.6 + top * u)[:, None] * ey[None, :]
            ka = (0.22 + 0.10 * bp + 1.1 * fl * quiet) * fk
            cols.append(col_p)
            cola.append(ka * (1.0 - u) ** 1.5)
            cols_s.append(np.full(14, R * 0.035))
            colb.append(dict(base=base, k=ka, size=k * m["h"] * 2.6))
        if not P:
            return None
        out = [dict(pos=np.concatenate(P), size=R * 0.0042, color=np.concatenate(C),
                    alpha=np.clip(np.concatenate(A), 0, 1.6).astype(np.float32), kind="spark", emit=2.6, dof=0.0,
                    fog=0.0, reflect=False, twinkle=0.25),
               dict(pos=np.concatenate(cols), size=np.concatenate(cols_s), color=lin("#cfe6ff"),
                    alpha=np.clip(np.concatenate(cola), 0, 1).astype(np.float32), kind="soft", emit=1.8, dof=0.0,
                    fog=0.0, reflect=False)]
        gp = np.array([b["base"] for b in colb])
        out.append(dict(pos=gp, size=np.array([b["size"] for b in colb]), color=lin("#bfe0ff"),
                        alpha=np.array([0.16 * b["k"] for b in colb], np.float32), kind="soft", emit=1.6, dof=0.0,
                        fog=0.0, reflect=False))
        return out


# =========================================================================================================
# Around Zion: a growing ring of churches of light on the far shores of the mirror sea
# =========================================================================================================
RING_R = 1400.0
RING_K = 1.9          # model metres to world metres (the churches stand 50 to 80 m tall at 1.4 km)
# (azimuth round Zion in degrees from +z toward +x (180 is straight behind the city), model, ignite time)
RING = [
    (158.0, "sejong", 125.92), (202.0, "homaesil", 128.6), (140.0, "sail", 130.29), (220.0, "goldarch", 134.54),
    (176.0, "institute", 139.2), (122.0, "moran", 144.4), (238.0, "brazil", 146.7), (190.0, "sydney", 149.6),
    (104.0, "goldarch", 162.86), (256.0, "sail", 165.16), (168.0, "brazil", 168.0), (86.0, "homaesil", 171.48),
    (274.0, "sejong", 175.0), (131.0, "sydney", 178.4), (229.0, "moran", 180.7),
    (68.0, "institute", 188.27), (292.0, "goldarch", 195.2), (148.0, "homaesil", 201.73), (212.0, "sail", 211.6),
    (50.0, "brazil", 220.2),
]
RING = [(az, m, _snap(t)) for az, m, t in RING]


def _ring_frame(az):
    a = np.radians(az)
    base = ZC + _v(RING_R * np.sin(a), 0.0, RING_R * np.cos(a))
    ez = _unit(_v(ZC[0] - base[0], 0.0, ZC[2] - base[2]))     # the front faces Mount Zion
    ey = _v(0.0, 1.0, 0.0)
    return base, np.cross(ey, ez), ey, ez


def _ring_gain(t):
    """How much the ring shows: only on Mount Zion's side of the film (not on the Earth), softer in the close
    shots of the choir, calmer under a phrase; a breath on every beat."""
    if t < RING[0][2] - 0.1 or globe_view(t):
        return 0.0
    k = 0.55 if stage_view(t) else 1.0
    return k * (1.0 - 0.35 * _reading(t)) * (0.85 + 0.25 * beat_pulse(t))


class _RingStatic:
    """Every ring church's outline, glass and windows in one static set: each point is born at its church's
    beat, from the ground up over half a second, with a flash."""
    static = True

    def __init__(self, roles, size, alpha, emit):
        P, C, B = [], [], []
        for az, mk, ti in RING:
            m = MODELS[mk](1.0)
            base, ex, ey, ez = _ring_frame(az)
            pts = _place(m, base, ex, ey, ez, RING_K)
            sel = np.isin(m["role"], roles)
            P.append(pts[sel])
            C.append(m["col"][sel])
            B.append(ti + 0.5 * m["pos"][sel, 1] / m["h"])
        self.b = dict(pos=np.concatenate(P), size=size, color=np.concatenate(C), alpha=alpha, kind="spark",
                      emit=emit, birth=np.concatenate(B).astype(np.float32), fade=0.25, flash=2.5, fog=0.35,
                      twinkle=0.2)

    def sample(self, t):
        return self.b

    def gain(self, t):
        return _ring_gain(t)


class RingGlow:
    """The ring churches' living light: a soft glow round each, a column of light that shoots up on its beat
    and settles to a faint standing glow, all breathing with the beat."""

    def __init__(self):
        self.base = []
        for az, mk, ti in RING:
            m = MODELS[mk](1.0)
            base, ex, ey, ez = _ring_frame(az)
            self.base.append((base, m["h"] * RING_K, ti))
        self.u = np.linspace(0.0, 1.0, 18)

    def sample(self, t):
        g = _ring_gain(t)
        if g <= 0.0:
            return None
        quiet = 1.0 - 0.6 * _reading(t)
        bp = beat_pulse(t)
        G, GS, GA, CP, CA, CS = [], [], [], [], [], []
        for base, h, ti in self.base:
            if t < ti:
                continue
            fl = hit_pulse(t, [ti], rise=0.02, fall=0.7) * quiet
            G += [base + _v(0, 0.45 * h, 0), base + _v(0, 0.1 * h, 0)]
            GS += [2.2 * h, 3.4 * h]
            GA += [(0.06 + 0.03 * bp + 0.25 * fl) * g, (0.035 + 0.12 * fl) * g]
            top = h * (1.0 + 4.5 * _sc(ti, ti + 0.5, t))
            CP.append(base[None, :] + (h + top * self.u)[:, None] * _v(0, 1, 0)[None, :])
            CA.append((0.05 + 0.03 * bp + 0.9 * fl) * g * (1.0 - self.u) ** 1.6)
            CS.append(np.full(len(self.u), 0.16 * h))
        if not G:
            return None
        return [dict(pos=np.array(G), size=np.array(GS), color=lin("#a9ccff"), alpha=np.array(GA, np.float32),
                     kind="soft", emit=1.4, fog=0.5),
                dict(pos=np.concatenate(CP), size=np.concatenate(CS), color=lin("#d6e8ff"),
                     alpha=np.clip(np.concatenate(CA), 0, 1).astype(np.float32), kind="soft", emit=1.8, fog=0.4,
                     reflect=False)]


def add(scene):
    if os.environ.get("S11_CHURCHES_OFF"):      # (for cost checks only)
        return
    scene.add("churches ring lines", _RingStatic([0, 3], 2.0, 0.85, 2.4))
    scene.add("churches ring glass", _RingStatic([1], 1.6, 0.5, 2.0))
    scene.add("churches ring windows", _RingStatic([2], 3.0, 0.95, 2.8))
    scene.add("churches ring glow", RingGlow())
    scene.add("churches earth", EarthChurches(), reflect=False)
