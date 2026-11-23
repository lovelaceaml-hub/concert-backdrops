"""Song 07 "May No One Ever Feel Lonely": its own world on the song kit ("No Light Left Alone", design:
project-docs/designs/07 May No One Ever Feel Lonely.md). The kit gives the expressions, their words, the arch and
the peace rings (kit_love); this set gives the lakeside path, the village of light, the bench under the lamp
post, the traveler and the helper, the footprints of light, the lone lights, Mother's lamp, the river of
lanterns and the reunions, the hush, the kingdom in the clouds, the bridge of light and the procession home,
and the camera of every block it owns.

Places (metres, y up, the mirror lake is y = 0, the camera mostly looks toward -z): the path runs straight away
from the viewer along x = PATH_X toward the horizon star; the village is on its right; the lake on its left.
Heavenly Mother is seen only from behind, holding her lamp (design section 10). Touch rules (UPDATE 15): the
greeting and the helping hand are between men; the embrace between two women; a parent with a child.
No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.kit_film import *  # noqa: F401,F403
import songs.kit_film as H
import songs.kit_love as L

OWNER = "world"
V = H._v
PATH_X = 6.0
BENCH = V(6.7, 0.0, -36.3)          # the bench under the lamp post, at the side of the path, facing the lake
LAMP_POST = V(7.5, 0.0, -35.4)
STAR = V(PATH_X, 6.0, -900.0)       # the warm horizon star: Heavenly Mother's presence
KINGDOM = V(0.0, 170.0, -900.0)     # the kingdom of heaven above the mountains (verse 3)
GATE = V(0.0, 236.0, -880.0)
MOTHER_AT = (PATH_X - 0.8, -150.0)
SHORE = V(8.0, 0.0, -60.0)          # where everyone gathers (hush, verse 3)

GOLD_W = "#ffd9a0"
CORAL = "#ff977c"
PEARL = "#fff4e0"
LANTERN = "#ffc070"

sc, win = H._sc, H._win


# =========================================================================================================
# The camera: one designed shot per block this set owns (times from the song's edit list)
# =========================================================================================================
def _keys(t0, t1, p0, q0, p1, q1):
    return [(t0, V(*p0), V(*q0)), (t1, V(*p1), V(*q1))]


DESIGNS = {
    # down the long path at walking height, a slow steady push forward (design section 5)
    0.0: dict(name="path_dusk", fov=48.0, pace="linear",
              keys=lambda a, b: _keys(a, b, (4.6, 1.7, 2.0), (PATH_X, 3.0, -400.0), (4.9, 1.7, -9.0), (PATH_X, 2.8, -400.0))),
    13.5: dict(name="passers", fov=40.0, keys=lambda a, b: _keys(a, b, (-1.5, 1.9, -24.0), (7.0, 1.1, -42.0),
                                                                (-0.8, 1.8, -27.0), (7.0, 1.0, -40.0))),
    25.0: dict(name="footprints", fov=44.0, keys=lambda a, b: _keys(a, b, (2.0, 5.5, -18.0), (PATH_X, 0.0, -160.0),
                                                                   (2.5, 4.6, -22.0), (PATH_X, 0.6, -90.0))),
    37.0: dict(name="village", fov=42.0, keys=lambda a, b: _keys(a, b, (0.5, 3.0, -22.0), (17.0, 3.0, -70.0),
                                                                (1.5, 2.6, -24.0), (14.0, 2.4, -50.0))),
    50.5: dict(name="return", fov=38.0, keys=lambda a, b: _keys(a, b, (1.0, 1.8, -29.0), (6.2, 1.0, -37.0),
                                                               (1.4, 1.7, -30.0), (6.2, 1.0, -37.0))),
    63.0: dict(name="peace_ring1", fov=50.0, keys=lambda a, b: _keys(a, b, (-8.0, 8.0, -12.0), (6.0, 0.0, -45.0),
                                                                    (-9.0, 9.5, -10.0), (5.0, 0.0, -50.0))),
    75.0: dict(name="together", fov=40.0, keys=lambda a, b: _keys(a, b, (1.5, 1.9, -30.0), (6.0, 1.1, -40.0),
                                                                 (2.0, 1.9, -36.0), (6.0, 1.1, -46.0))),
    80.0: dict(name="lost_lights", fov=50.0, keys=lambda a, b: _keys(a, b, (-6.0, 4.0, -22.0), (-50.0, 2.0, -150.0),
                                                                    (-10.0, 5.0, -30.0), (-40.0, 1.0, -160.0))),
    96.0: dict(name="mother_lamp", fov=34.0, keys=lambda a, b: _keys(a, b, (MOTHER_AT[0] + 0.9, 1.8, MOTHER_AT[1] + 9.0),
                                                                    (MOTHER_AT[0] - 1.0, 2.2, MOTHER_AT[1] - 60.0),
                                                                    (MOTHER_AT[0] + 0.8, 1.9, MOTHER_AT[1] + 7.5),
                                                                    (MOTHER_AT[0] - 1.0, 2.4, MOTHER_AT[1] - 60.0))),
    # from above and behind the two lantern-bearers as they cross to the lost, the lit lake beyond them
    111.0: dict(name="lantern_river", fov=50.0, keys=lambda a, b: _keys(a, b, (12.0, 12.0, -27.0), (-4.0, 0.0, -54.0),
                                                                       (5.0, 6.0, -37.0), (-5.0, 0.8, -50.0))),
    124.0: dict(name="reunions", fov=40.0, keys=lambda a, b: _keys(a, b, (2.0, 1.9, -50.0), (8.5, 1.1, -60.0),
                                                                  (3.0, 1.9, -52.0), (9.0, 1.1, -61.0))),
    137.0: dict(name="hush", fov=46.0, pace="linear", keys=lambda a, b: _keys(a, b, (0.0, 1.5, -28.0), (5.0, 2.0, -400.0),
                                                                            (0.0, 1.5, -28.4), (5.0, 2.0, -400.0))),
    148.0: dict(name="kingdom", fov=52.0, keys=lambda a, b: _keys(a, b, (1.0, 2.0, -40.0), (4.0, 6.0, -400.0),
                                                                 (0.0, 3.0, -46.0), (0.0, 170.0, -900.0))),
    161.0: dict(name="dawn_faces", fov=42.0, keys=lambda a, b: _keys(a, b, (-4.0, 2.2, -44.0), (7.0, 2.2, -62.0),
                                                                    (-3.0, 2.0, -46.0), (8.0, 2.6, -64.0))),
    # facing the shore with the dawn and the kingdom behind: the current of light crossing everyone's joined hands
    174.0: dict(name="joined_hands", fov=46.0, roll=(0.0, 1.5), keys=lambda a, b: _keys(a, b, (6.0, 7.0, -46.0),
                                                                                        (9.0, 0.8, -64.0),
                                                                                        (7.0, 8.5, -49.0),
                                                                                        (9.5, 0.8, -66.0))),
    187.0: dict(name="bridge", fov=52.0, keys=lambda a, b: _keys(a, b, (-16.0, 6.0, -70.0), (0.0, 30.0, -260.0),
                                                                (-20.0, 30.0, -140.0), (0.0, 120.0, -600.0))),
    201.0: dict(name="procession_sky", fov=54.0, roll=(-3.0, 3.0), keys=lambda a, b: _keys(a, b, (-40.0, 60.0, -260.0),
                                                                                           (0.0, 150.0, -700.0),
                                                                                           (-20.0, 150.0, -560.0),
                                                                                           (0.0, 225.0, -880.0))),
    224.0: dict(name="gate", fov=50.0, keys=lambda a, b: _keys(a, b, (0.0, 200.0, -700.0), (0.0, 236.0, -880.0),
                                                              (0.0, 120.0, -400.0), (0.0, 150.0, -880.0))),
    236.0: dict(name="hold", fov=48.0, pace="linear", keys=lambda a, b: _keys(a, b, (0.0, 1.6, 12.0), (PATH_X, 4.0, -400.0),
                                                                            (0.0, 1.6, 11.0), (PATH_X, 4.0, -400.0))),
}


def _shot(b):
    t0, t1, note = b
    d = DESIGNS[min(DESIGNS, key=lambda k: abs(k - t0))]
    s = dict(name=d["name"], kind="local", t0=t0, t1=t1, fov=d["fov"], aperture=0.0, keys=d["keys"](t0, t1))
    for k in ("pace", "roll"):
        if k in d:
            s[k] = d[k]
    return s


SHOTS = [_shot(b) for b in H.blocks_of(OWNER)]
SHAFTS = []


# =========================================================================================================
# Point sets: the path, the village, the bench and lamp post, the horizon star, the footprints, the lone lights,
# the lamps, the current of joined hands, the far villages, the kingdom, the gate, the bridge, the procession
# =========================================================================================================
def _line(a, b, step):
    return H._seg(np.asarray(a, np.float64), np.asarray(b, np.float64), step)


def _path():
    z = np.arange(-6.0, -700.0, -0.35)
    x = PATH_X + 0.35 * np.sin(z * 0.05)
    P = np.stack([x, np.full_like(z, 0.04), z], 1)
    edge = np.concatenate([P + V(-0.55, 0.0, 0.0), P + V(0.55, 0.0, 0.0)])
    return [H._batch(edge, 0.05, lin(GOLD_W) * 0.55, 0.55, kind="spark", emit=1.6, twinkle=0.4, reflect=True),
            H._batch(P[::3], 0.9, lin(GOLD_W) * 0.25, 0.06, kind="soft", emit=1.0)]


HOMES = [(15.5, -48.0, 5.0, 4.0, 3.2), (14.5, -62.0, 4.0, 4.4, 3.6), (16.0, -76.0, 5.5, 4.0, 3.0),
         (13.8, -90.0, 4.2, 4.0, 3.4), (15.5, -104.0, 5.0, 4.6, 3.8), (14.0, -118.0, 4.6, 4.0, 3.2),
         (16.5, -134.0, 5.2, 4.2, 3.4)]


def _village():
    edges, wins = [], []
    for x, z, w, d, h in HOMES:
        c = V(x, 0.0, z)
        edges.append(H._box(c, w, d, h, 0.12))
        roof = [_line((x - w / 2, h, z - d / 2), (x, h + 1.6, z - d / 2), 0.12),
                _line((x + w / 2, h, z - d / 2), (x, h + 1.6, z - d / 2), 0.12),
                _line((x - w / 2, h, z + d / 2), (x, h + 1.6, z + d / 2), 0.12),
                _line((x + w / 2, h, z + d / 2), (x, h + 1.6, z + d / 2), 0.12),
                _line((x, h + 1.6, z - d / 2), (x, h + 1.6, z + d / 2), 0.12)]
        edges += roof
        wins.append(H._windows(c, w, d, h, floor=3.0, bay=1.8))
    E, W = np.concatenate(edges), np.concatenate(wins)
    return [H._batch(E, 0.045, lin("#ffd9a8") * 0.6, 0.5, kind="spark", emit=1.4, twinkle=0.3),
            H._batch(W, 0.42, lin("#ffc070"), 0.85, kind="soft", emit=2.2),
            H._batch(W, 0.10, lin("#fff0d0"), 1.0, kind="spark", emit=3.0)]


def _bench():
    """A low bench of light (seat and back along the path) and the lamp post beside it."""
    b = BENCH
    rails = [_line(b + V(dx, y, -0.8), b + V(dx, y, 0.8), 0.03) for dx, y in ((-0.18, 0.45), (0.05, 0.45), (0.2, 0.62),
                                                                                (0.22, 0.85))]
    legs = [_line(b + V(dx, 0.0, dz), b + V(dx, 0.45, dz), 0.03) for dx in (-0.18, 0.05) for dz in (-0.72, 0.72)]
    post = _line(LAMP_POST, LAMP_POST + V(0.0, 2.6, 0.0), 0.05)
    head = LAMP_POST + V(0.0, 2.7, 0.0)
    return [H._batch(np.concatenate(rails + legs), 0.03, lin("#ffd9a8") * 0.55, 0.55, kind="spark", emit=1.3),
            H._batch(post, 0.02, lin("#ffd9a8") * 0.3, 0.18, kind="spark", emit=1.0),
            H._batch(head[None], 1.6, lin(LANTERN), 0.35, kind="soft", emit=2.0),
            H._batch(head[None], 0.18, lin("#fff4dc"), 0.9, kind="spark", emit=3.0)]


def _footprints():
    """Footprints of light from far down the path toward the bench, one by one, as Mother's first wish is read."""
    n = 46
    z = np.linspace(-150.0, BENCH[2] - 1.0, n)
    side = np.where(np.arange(n) % 2 == 0, -0.16, 0.16)
    P = np.stack([PATH_X + side, np.full(n, 0.06), z], 1)
    birth = np.linspace(27.2, 34.4, n)
    return [H._batch(P, 0.22, lin(PEARL), 0.9, kind="spark", emit=3.0, birth=birth, fade=0.4, flash=1.6, twinkle=0.3),
            H._batch(P, 0.9, lin(GOLD_W), 0.18, kind="soft", emit=1.4, birth=birth, fade=0.4)]


class Glow:
    """A soft glow of light at a point (or following a function of time) with a strength over time."""

    def __init__(self, pos, color, size, gain, core=0.0):
        self.pos, self.col, self.size, self.g, self.core = pos, lin(color), float(size), gain, float(core)

    def sample(self, t):
        g = float(self.g(t))
        if g <= 0.0:
            return None
        p = np.asarray(self.pos(t) if callable(self.pos) else self.pos, np.float64)[None]
        out = [dict(pos=p, size=self.size, color=self.col, alpha=0.5 * g, kind="soft", emit=2.4)]
        if self.core:
            out.append(dict(pos=p, size=self.size * self.core, color=self.col * 0.4 + lin(PEARL) * 0.6, alpha=g,
                            kind="spark", emit=4.0))
        return out


def _wish_k(t):
    """While one of Mother's wishes is read the horizon star glows brighter (design section 6)."""
    return max([win(t, b, c, 1.2, 1.6) for _l, (a, b, c, d), *_x in H.PHRASE_LIST[:4]] + [0.0])


LONE = [(-22.0, -70.0, 124.0), (-40.0, -95.0, 125.5), (-58.0, -120.0, 127.0), (-30.0, -140.0, 128.5),
        (-75.0, -160.0, 130.0), (-48.0, -185.0, 131.5)]


class LoneLights:
    """The lone lights: faint drifting lights on the dark water and in the mist (the traveler is the first one).
    Each is found in verse 2 (its time) and walks home to the shore, brightening."""

    def __init__(self):
        self.r = np.random.default_rng(707).random((len(LONE), 3))

    def sample(self, t):
        P, A, S = [], [], []
        for i, (x, z, found) in enumerate(LONE):
            ph = self.r[i]
            drift = V(1.6 * np.sin(0.13 * t + 6.0 * ph[0]), 0.0, 1.2 * np.cos(0.11 * t + 6.0 * ph[1]))
            home = H._sc(found, found + 9.0, t)
            p = V(x, 1.1, z) + drift * (1.0 - home)
            p = p + (SHORE + V(-2.0 + 0.6 * i, 1.1, -1.0 * i) - p) * home
            a = (0.25 + 0.15 * np.sin(1.3 * t + 9.0 * ph[2])) * sc(1.0, 4.0, t) * (1.0 - sc(176.0, 180.0, t))
            a = a + 0.55 * home
            P.append(p)
            A.append(a)
            S.append(0.35 + 0.35 * home)
        P = np.asarray(P)
        A = np.asarray(A)
        return [dict(pos=P, size=np.asarray(S) * 4.0, color=lin(LANTERN), alpha=0.18 * A, kind="soft", emit=1.6),
                dict(pos=P, size=np.asarray(S), color=lin("#fff0d0"), alpha=A, kind="spark", emit=3.0)]


class Current:
    """The promise to share love: a current of light running through the joined hands along the shore line."""

    def __init__(self, a, b, t0, t1):
        self.a, self.b, self.t0, self.t1 = np.asarray(a, np.float64), np.asarray(b, np.float64), t0, t1
        self.u = np.linspace(0.0, 1.0, 400)

    def sample(self, t):
        k = win(t, self.t0, self.t1, 1.0, 2.0)
        if k <= 0.0:
            return None
        P = self.a[None] + (self.b - self.a)[None] * self.u[:, None]
        front = sc(self.t0, self.t0 + 5.0, t)
        lit = np.clip((front - self.u) * 8.0, 0.0, 1.0)
        pulse = 0.6 + 0.4 * np.sin(18.0 * self.u - 6.0 * t)
        return [dict(pos=P, size=0.10, color=lin(GOLD_W), alpha=k * lit * pulse, kind="spark", emit=2.2),
                dict(pos=P[::8], size=1.2, color=lin(LANTERN), alpha=0.12 * k * lit[::8], kind="soft", emit=1.4)]


def _far_villages():
    """Other villages light up along the far shores and beyond the mountains in answer (verse 3)."""
    r = np.random.default_rng(1717)
    P, B = [], []
    for k in range(9):
        a = np.radians(-60.0 + 120.0 * k / 8.0)
        c = V(500.0 * np.sin(a), 2.0 + 20.0 * r.random(), -700.0 + 300.0 * (1.0 - np.cos(a)))
        q = c[None] + r.normal(0.0, 1.0, (60, 3)) * np.array([14.0, 3.0, 8.0])
        P.append(q)
        B.append(np.full(60, 176.0 + 1.2 * k) + r.random(60) * 2.0)
    P, B = np.concatenate(P), np.concatenate(B)
    return [H._batch(P, 1.6, lin(LANTERN), 0.9, kind="spark", emit=2.6, birth=B, fade=1.2, twinkle=0.6),
            H._batch(P[::4], 9.0, lin(LANTERN), 0.10, kind="soft", emit=1.2, birth=B[::4], fade=1.2)]


def _kingdom():
    """The kingdom of heaven: a vast city of light rising in terraces above the mountains, its gate shining."""
    c = KINGDOM
    parts = []
    for k in range(6):
        r = 230.0 - 32.0 * k
        y = c[1] + 14.0 * k
        parts.append(H._ring(c, r, y, 1.6))
        for a in np.linspace(0.0, 2.0 * np.pi, 10 + 4 * k, endpoint=False):
            p = V(c[0] + r * np.sin(a), y, c[2] + 0.45 * r * np.cos(a))
            parts.append(H._box(p, 6.0, 6.0, 10.0 + 6.0 * (k % 3), 1.2))
    P = np.concatenate(parts)
    P[:, 2] = c[2] + (P[:, 2] - c[2]) * 0.45                 # the city stands on a terraced mount, not a disc
    return [H._batch(P, 1.1, lin("#fff0d0") * 0.8, 0.8, kind="spark", emit=2.6, twinkle=0.5),
            H._batch(P[::6], 7.0, lin("#ffd9a8"), 0.06, kind="soft", emit=1.2)]


def _gate():
    th = np.linspace(0.0, np.pi, 200)
    arc = np.stack([GATE[0] + 26.0 * np.cos(th), GATE[1] - 30.0 + 38.0 * np.sin(th), np.full_like(th, GATE[2])], 1)
    legs = np.concatenate([_line(GATE + V(-26.0, -60.0, 0.0), GATE + V(-26.0, -30.0, 0.0), 0.8),
                           _line(GATE + V(26.0, -60.0, 0.0), GATE + V(26.0, -30.0, 0.0), 0.8)])
    P = np.concatenate([arc, legs])
    return [H._batch(P, 1.6, lin("#fff4dc"), 1.0, kind="spark", emit=3.4),
            H._batch(P[::3], 12.0, lin("#ffd9a8"), 0.12, kind="soft", emit=1.6)]


def _bridge_curve(u):
    a, b = V(PATH_X, 0.2, -60.0), GATE + V(0.0, -58.0, 6.0)
    m = V(0.0, 40.0, -420.0)
    u = np.asarray(u, np.float64)[:, None]
    return (1 - u) ** 2 * a + 2 * (1 - u) * u * m + u ** 2 * b


class Bridge:
    """The path's reflection lifts into the sky as a bridge of light from the shore to the open gate."""

    def __init__(self):
        self.u = np.linspace(0.0, 1.0, 1800)
        self.P = _bridge_curve(self.u)
        side = np.cross(np.gradient(self.P, axis=0), [0.0, 1.0, 0.0])
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-6)
        self.edges = np.concatenate([self.P + side * 3.0, self.P - side * 3.0])

    def sample(self, t):
        grow = sc(187.0, 196.0, t)
        k = grow * (1.0 - sc(232.0, 238.0, t))
        if k <= 0.0:
            return None
        m = np.concatenate([self.u, self.u]) <= grow
        E = self.edges[m]
        return [dict(pos=E, size=0.45, color=lin(GOLD_W), alpha=0.85 * k, kind="spark", emit=2.8, twinkle=0.4),
                dict(pos=self.P[self.u <= grow][::6], size=6.0, color=lin(LANTERN), alpha=0.10 * k, kind="soft",
                     emit=1.4)]


class Procession:
    """Thousands of walking lights following Mother over the bridge into the gate."""

    def __init__(self, n=3200):
        r = np.random.default_rng(2207)
        self.phase, self.lat, self.s = r.random(n), r.normal(0.0, 1.0, n), r.random(n)

    def sample(self, t):
        k = sc(196.0, 201.0, t) * (1.0 - sc(232.0, 238.0, t))
        if k <= 0.0:
            return None
        u = np.clip((self.phase + 0.012 * (t - 196.0)) % 1.0, 0.0, 1.0)
        u = u * sc(196.0, 230.0, t) ** 0.5
        P = _bridge_curve(u) + np.outer(self.lat, [1.4, 0.0, 0.0]) + V(0.0, 1.2, 0.0)
        a = k * (0.5 + 0.5 * self.s) * (1.0 - u ** 6)
        return [dict(pos=P, size=0.32 + 0.2 * self.s, color=lin(LANTERN) * 0.6 + lin(PEARL) * 0.4, alpha=a, kind="spark",
                     emit=2.8, twinkle=0.7, seed=self.s)]


# =========================================================================================================
# The people of light (kit_love.body): the traveler, the busy passers-by, the helper, Mother (from behind),
# the lantern-bearers, the lost, the reunions on the shore
# =========================================================================================================
def _palm(name, t, side="R"):
    return np.asarray(L._BODIES[name].where(t, "palm." + side), np.float64)


def _grip(t):
    """Where the two right hands meet as the helper pulls the traveler up (between their shoulders, a little
    lower), so neither hand waits on the other."""
    pa = np.asarray(L._BODIES["helper"].where(t, "shoulder.R", raw=True), np.float64)
    pb = np.asarray(L._BODIES["traveler"].where(t, "shoulder.R", raw=True), np.float64)
    g = 0.5 * (pa + pb)
    g[1] = 0.5 * (pa[1] + pb[1]) - 0.36
    return g


def _people():
    b = L.body
    bz = BENCH[2]
    # the elderly traveler: walks the path slowly, a little stooped, and sits on the bench facing the lake; helped
    # up (Consideration), they walk on together; later he carries a lantern in the search
    b("traveler", "man", at=(PATH_X, bz + 8.8), facing=[(0.0, 180.0), (18.0, 180.0), (19.6, 270.0), (73.0, 270.0),
                                                        (74.6, 180.0)],
      motion=[(1.5, "walk", dict(speed=0.55)), (17.6, "stand", dict(blend=1.2)), (20.2, "sit", dict(dur=1.6)),
              (67.8, "stand", dict(blend=1.6)), (75.4, "walk", dict(speed=0.42)), (92.0, "stand", dict(blend=1.5))],
      gesture=[(54.0, 61.0, "look_up", dict(amount=10.0)),
               (66.8, 71.0, "handshake", dict(side="R", to=_grip, grip=1.0, ease=0.6))],
      stoop=0.45, garment="coat", tone=1, seed=21.0, show=(0.0, 96.0), fade=2.5, points=34000)
    # two busy passers-by going the other way (not unkind, just not noticing)
    b("passer1", "man", at=(PATH_X - 0.6, bz - 26.0), facing=0.0, motion=[(13.0, "walk", dict(speed=1.2))],
      garment="coat", tone=2, seed=23.0, show=(13.0, 34.0), fade=1.5, points=22000)
    b("passer2", "man", at=(PATH_X + 0.5, bz - 30.0), facing=0.0, motion=[(14.5, "walk", dict(speed=1.25))],
      garment="tunic", tone=3, seed=24.0, show=(14.5, 36.0), fade=1.5, points=22000)
    # the helper: passes by, stops, turns back, returns to the bench, bows slightly and kneels to the traveler's
    # eye level (Greeting), offers his hand and helps him up (Consideration), walks on beside him at his pace
    b("helper", "man", at=(PATH_X - 1.55, bz - 16.0), facing=[(0.0, 0.0), (37.6, 0.0), (40.2, 180.0), (50.4, 180.0),
                                                             (51.4, 90.0), (73.0, 90.0), (74.6, 180.0)],
      motion=[(14.0, "walk", dict(speed=1.1)), (37.0, "stand", dict(blend=1.2)), (41.6, "walk", dict(speed=1.15)),
              (50.6, "stand", dict(blend=0.8)), (55.6, "kneel", dict(one=True, dur=1.6, blend=0.3)),
              (65.6, "rise", dict(dur=1.4, one=True, blend=0.05)), (75.4, "walk", dict(speed=0.42)),
              (92.0, "stand", dict(blend=1.5))],
      gesture=[(37.4, 40.6, "look_up", dict(amount=-4.0, turn=-28.0)), (53.4, 55.4, "bow", dict(amount=18.0)),
               (66.4, 71.0, "handshake", dict(side="R", to=_grip, grip=1.0, ease=0.7)),
               (71.0, 75.0, "hand_on_shoulder", dict(side="L", to=lambda t: np.asarray(
                   L._BODIES["traveler"].where(t, "shoulder.R", raw=True), np.float64), ease=0.9))],
      tone=0, seed=22.0, show=(14.0, 96.0), fade=2.5, garment="tunic", points=34000)
    # Heavenly Mother, only ever seen from behind: her lamp held up toward the misty water, then leading home
    b("mother", "woman", at=MOTHER_AT, facing=180.0,
      motion=[(0.0, "stand"), (188.0, "walk", dict(speed=0.6)), (224.0, "stand", dict(blend=2.0))],
      gesture=[(96.6, 224.0, "raise_hand", dict(side="R", palm="fwd"))],
      garment="robe", veil=dict(length=1.5, wide=1.1), color="#ffe6b0", color2="#fff6e0", seed=30.0,
      show=(95.0, 226.0), fade=2.5, points=40000, bright=1.55)
    # the two lantern-bearers at the front of the search (the male duet): men side by side, lanterns held high
    for k, x0 in enumerate((2.5, 3.6)):
        b(f"bearer{k}", "man", at=(x0, -44.0 - 0.6 * k), facing=[(0.0, 270.0), (125.5, 270.0), (127.0, 90.0)],
          motion=[(111.0 + 0.5 * k, "walk", dict(speed=0.7)), (122.6, "stand", dict(blend=1.4)),
                  (127.2 + 0.3 * k, "walk", dict(speed=0.5)), (137.0, "stand", dict(blend=1.5))],
          gesture=[(110.0, 123.0, "raise_hand", dict(side="R", palm="fwd")),
                   (123.0, 126.0, "handshake", dict(side="R", to=lambda t, k=k: _palm(f"lost{k}", t))),
                   (127.0, 188.0, "raise_hand", dict(side="R", palm="fwd"))],
          garment="tunic" if k else "coat", tone=k, seed=40.0 + k, show=(109.0, 188.0), points=24000)
    # two who were lost (men), reached by the bearers' offered hands, walking home with them
    for k, x0 in enumerate((-5.5, -4.4)):
        b(f"lost{k}", "man", at=(x0, -44.6 - 0.6 * k), facing=90.0,
          motion=[(0.0, "stand"), (127.6 + 0.3 * k, "walk", dict(speed=0.5)), (137.0, "stand", dict(blend=1.5))],
          gesture=[(123.2, 126.0, "offer", dict(side="R"))],
          garment="coat" if k else "tunic", tone=2 + k, seed=50.0 + k, show=(116.0, 188.0), fade=3.0, points=22000)
    # the shore: two women embrace (one who has come home); a mother holds her child close (parent and child)
    sx, sz = SHORE[0], SHORE[2]
    b("sister0", "woman", at=(sx, sz), facing=90.0, motion="stand", garment="dress", hair="bun", tone=0, seed=60.0,
      show=(126.0, 188.0), fade=1.6, points=22000,
      gesture=[(129.5, 137.5, "embrace", dict(to=V(sx + 0.84, 1.25, sz - 0.05), head="L"))])
    b("sister1", "woman", at=(sx + 0.72, sz - 0.05), facing=270.0, motion="stand", garment="robe", hair="bob", tone=1,
      seed=61.0, show=(126.0, 188.0), fade=1.6, points=22000,
      gesture=[(129.8, 137.5, "embrace", dict(to=V(sx - 0.12, 1.25, sz), head="L"))])
    b("parent", "woman", at=(sx + 3.4, sz + 1.5), facing=120.0, motion="stand", garment="dress", hair="bun", tone=2,
      seed=62.0, show=(126.0, 188.0), fade=1.6, points=22000,
      gesture=[(130.0, 187.0, "arm_round", dict(side="L", to=lambda t: L._BODIES["child"].where(t, "shoulder.R")))])
    b("child", "child", at=(sx + 3.88, sz + 1.72), facing=300.0, motion="stand", garment="tunic", tone=3, seed=63.0,
      show=(126.0, 188.0), fade=1.6, points=16000, gesture=[(150.5, 187.0, "look_up", dict(amount=30.0))])


def _lamp_pos(name):
    return lambda t: _palm(name, t, "R") + V(0.0, 0.18, 0.0)


def add(scene):
    _people()
    scene.add("path", Static(_path(), lambda t: 0.35 + 0.65 * sc(0.0, 4.0, t) * (1.0 - 0.7 * sc(232.0, 240.0, t))))
    scene.add("village", Static(_village(), lambda t: (0.55 + 0.45 * win(t, 38.0, 47.0, 1.5, 3.0) + 0.3 * sc(174.0, 180.0, t))
                                * (1.0 - 0.8 * sc(232.0, 240.0, t))), reflect=True)
    scene.add("bench", Static(_bench(), lambda t: 0.8 * (1.0 - sc(96.0, 100.0, t))))
    scene.add("footprints", Static(_footprints(), lambda t: 1.0 - sc(78.0, 82.0, t)), reflect=False)
    scene.add("horizon star", Glow(STAR, PEARL, 60.0, lambda t: 0.5 + 0.5 * _wish_k(t) + 0.3 * sc(148.0, 160.0, t),
                                   core=0.12))
    add_rays(STAR, lambda t: 0.25 + 0.6 * _wish_k(t), color="#fff1d8", size=0.6)
    scene.add("lone lights", LoneLights(), reflect=True)
    scene.add("mother lamp", Glow(_lamp_pos("mother"), "#ffe6b0", 1.6, lambda t: win(t, 97.0, 224.0, 1.5, 2.0), core=0.2),
              reflect=False)
    add_light(_lamp_pos("mother"), "#ffe6b0", lambda t: 0.25 * win(t, 97.0, 224.0, 1.5, 2.0), radius=8.0)
    for k in range(2):
        scene.add(f"lantern {k}", Glow(_lamp_pos(f"bearer{k}"), LANTERN, 1.1, lambda t: win(t, 110.5, 188.0, 1.0, 1.5),
                                        core=0.2), reflect=False)
        add_light(_lamp_pos(f"bearer{k}"), LANTERN, lambda t: 0.18 * win(t, 110.5, 188.0, 1.0, 1.5), radius=6.0)
    scene.add("current", Current(SHORE + V(-6.0, 1.1, -3.0), SHORE + V(10.0, 1.1, -3.0), 174.0, 187.0), reflect=False)
    crowd_k = lambda t: win(t, 136.0, 188.0, 2.0, 3.0)
    scene.add("gathered", GCrowd(gain=crowd_k, n=28, area=dict(center=(SHORE[0] + 2.0, SHORE[2] - 3.0),
                                                                radius=(3.0, 12.0)), facing=270.0, seed=7))
    scene.add("far villages", Static(_far_villages(), lambda t: sc(174.0, 182.0, t) * (1.0 - sc(232.0, 240.0, t))))
    scene.add("kingdom", Static(_kingdom(), lambda t: sc(148.0, 156.0, t) * (1.0 - sc(232.0, 238.0, t))))
    scene.add("gate", Static(_gate(), lambda t: (0.3 * sc(148.0, 156.0, t) + 0.7 * sc(209.0, 214.0, t))
                             * (1.0 - sc(232.0, 238.0, t))))
    add_rays(GATE, lambda t: 0.9 * win(t, 209.0, 230.0, 2.0, 4.0), color="#ffe6c0", size=0.8)
    for k, x in enumerate((-180.0, 180.0)):
        scene.add(f"kingdom cloud {k}", CloudBank(KINGDOM + V(x - 40.0 * np.sign(x) * 0.0, -30.0, 40.0),
                                                  size=(260.0, 80.0, 120.0), puffs=34, seed=30 + k,
                                                  gain=lambda t: 0.8 * sc(146.0, 152.0, t) * (1.0 - sc(232.0, 238.0, t))))
    scene.add("bridge", Bridge(), reflect=True)
    scene.add("procession", Procession(), reflect=True)
