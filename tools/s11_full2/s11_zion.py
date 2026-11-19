"""Song 11 v2: Mount Zion, a terraced mountain of light: the terraces filling with gold, the crown of
light, the nations standing on it, light pouring down, the column of light to heaven, rings of light over the land.

Owned by the zion thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.

The mountain: seven terraces (the core's tier_r, tier_y), each a solid feeling wall of light (dense glowing
faces, bright under the parapet and darker toward the foot, pilasters and lit niches for scale), with great
stairways up the front and gardens of light at the back of each terrace. A dark silhouette (Mask "dark") gives
the mountain its mass: what lies behind it (the far side of the terraces, the sky) is hidden. Only the lowest
terraces mirror in the sea, so the mountain stands on the water instead of doubling into a diamond.
The nations: countless people of light on the terraces (far ones a glitter of tiny standing figures, near ones,
where the camera climbs past them, true figures), filling tier by tier at each "standing firm" climb.
"""
import numpy as np

from p3d.api import Mask
from songs.s11_full2 import *  # noqa: F401,F403
import songs.s11_full2 as H

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C
ZZ = float(ZC[2])

SHOTS = [
    # C. Mount Zion across the sea at dawn: the crown of light ignites high over the city (the words between
    # the city and the crown); then the terraces fill with gold, step by step
    dict(name="zion_crown", kind="local", t0=53.78, t1=70.54, fov=46.0, aperture=0.0,
         keys=[(53.78, _v(70.0, 112.0, ZZ + 640.0), ZC + _v(0.0, Y + 34.0, 0.0)),
               (61.2, _v(52.0, 106.0, ZZ + 600.0), ZC + _v(0.0, Y + 30.0, 0.0)),
               (70.54, _v(20.0, 96.0, ZZ + 520.0), ZC + _v(0.0, Y + 12.0, 0.0))]),
    # waves of praise: the whole land ripples with light (high, so the rings roll out over the sea)
    dict(name="praise_ripples", kind="local", t0=86.70, t1=90.72, fov=50.0, aperture=0.0,
         keys=[(86.70, _v(-150.0, 190.0, ZZ + 560.0), ZC + _v(0.0, 10.0, 40.0)),
               (90.72, _v(-120.0, 176.0, ZZ + 520.0), ZC + _v(0.0, 14.0, 40.0))]),
    # first climb: Mount Zion wide across the sea, then up over the lowest terraces, the nations standing on
    # them; sacrifice, devotion (light pours down on the people); thanks (a column of light to heaven)
    dict(name="zion_wide", kind="local", t0=90.72, t1=117.0, fov=50.0, aperture=0.0,
         keys=[(90.72, _v(150.0, 52.0, ZZ + 520.0), ZC + _v(0.0, 36.0, 0.0)),
               (99.4, _v(122.0, 64.0, ZZ + 432.0), ZC + _v(0.0, 44.0, 0.0)),
               (109.8, _v(84.0, 72.0, ZZ + 304.0), ZC + _v(0.0, 58.0, 0.0)),
               (117.0, _v(64.0, 78.0, ZZ + 252.0), ZC + _v(0.0, 92.0, 0.0))]),
    # the shockwave across the land; second climb (2:51.48): higher, over the middle terraces, the whole
    # mountain full of people (from the right, so the low sun stays clear of the words)
    dict(name="zion_full", kind="local", t0=165.16, t1=185.92, fov=52.0, aperture=0.0,
         keys=[(165.16, _v(170.0, 124.0, ZZ + 540.0), ZC + _v(0.0, 24.0, 20.0)),
               (171.48, _v(150.0, 116.0, ZZ + 470.0), ZC + _v(0.0, 30.0, 10.0)),
               (179.2, _v(110.0, 108.0, ZZ + 320.0), ZC + _v(0.0, 50.0, 0.0)),
               (185.92, _v(72.0, 104.0, ZZ + 200.0), ZC + _v(0.0, 70.0, 0.0))]),
]


FILL_T = [64.2, 64.2, 64.2, 65.94, 65.94, 69.4, 69.4]     # "being fulfilled": the terraces fill with gold
FRONT = np.radians(118.0)          # the side of the mountain the cameras see (azimuth from +z): full detail
STAIRS_AZ = np.radians([0.0, -36.0, 36.0, -72.0, 72.0])    # the great stairways (azimuth from +z)


def _az(n, r, front_share=0.82):
    """n azimuths, most of them on the seen side of the mountain."""
    a = np.where(r.random(n) < front_share, r.uniform(-FRONT, FRONT, n), r.uniform(-np.pi, np.pi, n))
    return a


def _xz(rr, a, y):
    return np.stack([ZC[0] + rr * np.sin(a), np.broadcast_to(y, np.shape(a)).astype(np.float64),
                     ZC[2] + rr * np.cos(a)], 1)


def _stair_mask(p, w=9.0):
    """True where a point (x, z) lies on one of the great stairways (kept clear of people and trees)."""
    a = np.arctan2(p[:, 0] - ZC[0], p[:, 2] - ZC[2])
    rr = np.hypot(p[:, 0] - ZC[0], p[:, 2] - ZC[2])
    m = np.zeros(len(p), bool)
    for s in STAIRS_AZ:
        m |= np.abs(np.angle(np.exp(1j * (a - s)))) * rr < w
    return m


# =========================================================================================================
# The mountain
# =========================================================================================================
def _mountain():
    r = np.random.default_rng(7)
    face, face_c, face_a, face_k, spark = [], [], [], [], []
    par, par_k, pil_a, pil_b, niche, tread, trees, tree_c = [], [], [], [], [], [], [], []
    post_a, post_b, lamp = [], [], []
    hi, lo = lin("#ffd79a"), lin("#7a3f6a")
    for k in range(N_TIER):
        R0, y = tier_r(k), tier_y(k)
        y0 = tier_y(k - 1) if k > 0 else 0.0
        h = y - y0
        # the wall's face: a soft glow, bright under the parapet, darker toward its foot, with a fine glitter
        n = int(R0 * 2 * np.pi * h * 0.20)
        a = _az(n, r, 0.9)
        u = r.random(n) ** 0.7                        # more light high on the wall
        face.append(_xz(R0 + 0.05, a, y0 + h * u))
        face_c.append(lo[None, :] * (1 - u[:, None]) + hi[None, :] * u[:, None])
        face_a.append(0.06 + 0.30 * u ** 2.0)
        face_k.append(np.full(n, k))
        n = int(R0 * 2 * np.pi * h * 0.035)
        a = _az(n, r, 0.95)
        spark.append(_xz(R0 + 0.1, a, y0 + h * r.random(n) ** 0.6))
        # the parapet (a rail on posts, lamps along it)
        q = _ring(ZC, R0 + 0.1, y + 1.0, 1.4)
        par.append(q)
        par_k.append(np.full(len(q), k))
        q = _ring(ZC, R0 + 0.1, y, 4.0)
        post_a.append(q)
        post_b.append(q + np.array([0.0, 1.0, 0.0]))
        lamp.append(_ring(ZC, R0 + 0.1, y + 1.4, 12.0))
        # pilasters every 7 m on the seen side (a sense of scale), a lit niche between each pair
        m = int(2 * FRONT * R0 / 7.0)
        a = np.linspace(-FRONT, FRONT, m)
        pil_a.append(_xz(R0 + 0.3, a, y0 + 0.4))
        pil_b.append(_xz(R0 + 0.3, a, y - 1.2))
        am = 0.5 * (a[1:] + a[:-1])
        niche.append(_xz(R0 + 0.2, am, y0 + 0.62 * h))
        # the terrace's floor (faint paving) and the gardens of light at the back of it, under the next wall
        Ri = tier_r(k + 1) if k < N_TIER - 1 else 0.0
        if k < N_TIER - 1:
            m = int((R0 ** 2 - Ri ** 2) * 0.010)
            a = _az(m, r)
            rr = np.sqrt(Ri ** 2 + (R0 ** 2 - Ri ** 2) * r.random(m))
            tread.append(_xz(rr, a, y + 0.05))
            nt = int(2 * FRONT * (Ri + 4.0) / 11.0)
            a = np.linspace(-FRONT, FRONT, nt) + r.uniform(-0.004, 0.004, nt)
            c = _xz(Ri + 4.5 + r.uniform(-0.8, 0.8, nt), a, y)
            c = c[~_stair_mask(c, 11.0)]
            for j in range(len(c)):
                q = r.normal(0.0, 1.0, (13, 3)) * np.array([1.6, 1.2, 1.6]) + c[j] + np.array([0.0, 3.8, 0.0])
                trunk = _seg(c[j], c[j] + np.array([0.0, 2.6, 0.0]), 0.9)
                trees.append(np.concatenate([q, trunk]))
                g = r.random()
                col = lin("#bfe8a8") if g < 0.55 else (lin("#ffe2a8") if g < 0.85 else lin(COL9[r.integers(0, 9)]))
                tree_c.append(np.repeat(col[None, :], len(q) + len(trunk), 0))
    F, FC, FA, FK, SP = (np.concatenate(v) for v in (face, face_c, face_a, face_k, spark))
    PA, PK, NI, TR, TT, TC = (np.concatenate(v) for v in (par, par_k, niche, tread, trees, tree_c))
    PB_a, PB_b = np.concatenate(pil_a), np.concatenate(pil_b)
    PO_a, PO_b, LP = np.concatenate(post_a), np.concatenate(post_b), np.concatenate(lamp)
    # the great stairways: one flight against each wall, from the terrace (or the sea) below to the one above
    st, rail, lamps, st_k = [], [], [], []
    for s in STAIRS_AZ:
        d = np.array([np.sin(s), 0.0, np.cos(s)])
        sd = np.array([np.cos(s), 0.0, -np.sin(s)])
        hw = 8.0 if s == 0.0 else 5.0
        for k in range(N_TIER):
            R0, y = tier_r(k), tier_y(k)
            y0 = tier_y(k - 1) if k > 0 else 0.0
            L = 14.0
            for i in range(12):
                u = (i + 0.5) / 12
                c = ZC + d * (R0 + L * (1 - u)) + np.array([0.0, y0 + (y - y0) * u, 0.0])
                st.append(_seg(c - sd * hw, c + sd * hw, 0.8))
                st_k.append(np.full(len(st[-1]), k))
            for side in (-1, 1):
                a0 = ZC + d * (R0 + L) + sd * side * (hw + 0.4) + np.array([0.0, y0 + 1.0, 0.0])
                a1 = ZC + d * R0 + sd * side * (hw + 0.4) + np.array([0.0, y + 1.0, 0.0])
                rail.append(_seg(a0, a1, 0.8))
                lamps.append(np.stack([a0, 0.5 * (a0 + a1), a1]) + np.array([0.0, 0.8, 0.0]))
    ST, SK, RA, LA = np.concatenate(st), np.concatenate(st_k), np.concatenate(rail), np.concatenate(lamps)
    low = FK <= 1                                            # only the lowest walls mirror in the sea
    dim = [
        _batch(F[low], 2.2, FC[low] * 0.5, FA[low], kind="soft", emit=1.0),
        _batch(F[~low], 2.2, FC[~low] * 0.5, FA[~low], kind="soft", emit=1.0, reflect=False),
        _batch(SP, 0.30, lin("#ffe6c0"), 0.8, emit=1.4, twinkle=0.7, reflect=False),
        _batch(PA, 0.45, lin("#ffe0a8") * 0.75, 0.5, emit=1.0, reflect=False),
        dict(pos=PO_a, pos2=PO_b, size=0.22, color=lin("#ffe0a8") * 0.6, alpha=0.6, kind="line", emit=1.0,
             reflect=False),
        _batch(LP, 0.8, lin("#ffe2b0"), 0.9, emit=2.0, twinkle=0.3, reflect=False),
        dict(pos=PB_a, pos2=PB_b, size=0.35, color=lin("#ffd6a0") * 0.45, alpha=0.3, alpha2=0.8, kind="line",
             emit=1.0, reflect=False),
        _batch(NI, 1.3, lin("#ffc98a") * 0.8, 0.85, kind="soft", emit=1.6, reflect=False),
        _batch(TR, 0.6, lin("#e6b88a") * 0.35, 0.45, kind="soft", emit=0.8, reflect=False),
        _batch(TT, 0.75, TC * 0.6, 0.7, emit=1.2, twinkle=0.5, reflect=False),
        _batch(ST, 0.40, lin(GOLD2) * 0.5, 0.8, emit=1.0, reflect=False),
        _batch(RA, 0.35, lin("#ffe6b8") * 0.5, 0.8, emit=1.0, reflect=False),
        _batch(LA, 0.9, lin("#ffdca0"), 0.9, emit=2.2, twinkle=0.3, reflect=False),
    ]
    # "being fulfilled": gold rises up each wall in turn (64.2, 65.94, 69.4)
    FT = np.asarray(FILL_T)
    y0s = np.asarray([tier_y(k - 1) if k else 0.0 for k in FK])
    fb = FT[FK] + 0.45 * (F[:, 1] - y0s) / 10.0
    upper = FA > 0.16
    gold = [
        _batch(F[upper], 2.6, lin(GOLD) * 0.8, FA[upper] * 0.75, kind="soft", emit=1.3, birth=fb[upper], fade=0.6,
               flash=1.5, reflect=False),
        _batch(PA, 0.55, lin(GOLD2), 0.6, emit=1.3, birth=FT[PK] + 0.45, fade=0.4, flash=3.0, twinkle=0.4,
               reflect=False),
        _batch(ST, 0.45, lin(GOLD), 0.7, emit=1.4, birth=FT[SK] + 0.2, fade=0.6, flash=2.0, reflect=False),
    ]
    return dim, gold


def _body():
    """The silhouette of the mountain's body (drawn only into the dark mask, never as light): the walls set a
    little into the mountain and the floors a little under the people, so nothing on the terraces is hidden."""
    P = []
    for k in range(N_TIER):
        R0, y = tier_r(k), tier_y(k)
        y0 = tier_y(k - 1) if k > 0 else 0.0
        for yy in np.arange(y0 + 1.0, y - 1.5, 3.2):
            P.append(_ring(ZC, R0 - 2.5, yy, 3.6))
        Ri = tier_r(k + 1) if k < N_TIER - 1 else 0.0
        for rr in np.arange(max(Ri, 3.0), R0 - 2.5, 4.6):
            P.append(_ring(ZC, rr, y - 4.0, 4.6))
    P = np.concatenate(P)
    return [_batch(P, 3.4, lin("#000000"), 1.0, kind="soft", emit=0.0, reflect=False)]


def _cam():
    return H.CAMERA.state


def body_k(t):
    """How strongly the mountain's body hides what is behind it. Off when the camera is over the upper
    mountain (the city, the stage, the summit shots) or looks at the Earth."""
    if local_k(t) <= 0.0:
        return 0.0
    c = np.asarray(H.CAMERA.state(t).pos, np.float64)
    d = float(np.hypot(c[0] - ZC[0], c[2] - ZC[2]))
    return 0.82 * _sc(tier_r(3) - 5.0, tier_r(3) + 25.0, d)


class _Off:
    """A static point set that is never drawn as light (its silhouette only)."""
    static = True

    def __init__(self, b):
        self.b = b

    def sample(self, t):
        return self.b

    def gain(self, t):
        return 0.0


# =========================================================================================================
# The crown of light
# =========================================================================================================
class Crown:
    """The crown of light that ignites high over the city on "The glory of Jerusalem Mother shines!" (0:53.78):
    a circlet with twelve tall points, each tipped with a jewel in the nine colours, lit from the front round."""

    def __init__(self):
        r = np.random.default_rng(31)
        c = ZC + _v(0.0, SUMMIT + 132.0, -10.0)
        R = 78.0
        pts, gem, gem_c = [], [], []
        for dy in (0.0, 2.2, 5.0):
            pts.append(_ring(c, R, c[1] + dy, 0.45))
        n = 24
        for k in range(n):
            a = 2 * np.pi * k / n
            b0 = 2 * np.pi * (k + 0.5) / n
            tall = k % 2 == 0
            h = 38.0 if tall else 15.0
            base = c[1] + 5.0
            tip = _v(c[0] + R * np.sin(a), base + h, c[2] + R * np.cos(a))
            for sgn in (-1, 1):
                aa = a + sgn * np.pi / n
                ee = np.linspace(0.0, 1.0, 40 if tall else 20)
                ang = a + sgn * (np.pi / n) * (1.0 - ee) ** 1.4
                yy = base + h * ee ** 0.8
                pts.append(np.stack([c[0] + R * np.sin(ang), yy, c[2] + R * np.cos(ang)], 1))
            gem.append(tip + _v(0.0, 1.6, 0.0))
            gem_c.append(lin(COL9[(k // 2) % 9]) if tall else lin("#fff2dc"))
            # a lattice in the band (diamonds)
            pts.append(_seg(_v(c[0] + R * np.sin(a), c[1], c[2] + R * np.cos(a)),
                            _v(c[0] + R * np.sin(b0), c[1] + 5.0, c[2] + R * np.cos(b0)), 0.5))
            pts.append(_seg(_v(c[0] + R * np.sin(b0), c[1], c[2] + R * np.cos(b0)),
                            _v(c[0] + R * np.sin(a), c[1] + 5.0, c[2] + R * np.cos(a)), 0.5))
        self.P = np.concatenate(pts)
        self.G, self.GC = np.asarray(gem), np.asarray(gem_c)
        az = np.abs(np.arctan2(self.P[:, 0] - c[0], self.P[:, 2] - c[2]))
        self.d = 0.55 * az / np.pi + 0.5 * (self.P[:, 1] - c[1]) / 35.0      # it lights from the front round
        gz = np.abs(np.arctan2(self.G[:, 0] - c[0], self.G[:, 2] - c[2]))
        self.gd = 0.55 * gz / np.pi + 0.5
        self.s = r.random(len(self.P))
        self.c = c

    def sample(self, t):
        if not (53.0 <= t < 71.0) or globe_view(t):
            return None
        u = t - HIT["glory"]
        if u < 0.0:
            return None
        grow = np.clip((u - self.d) / 0.35, 0.0, 1.0)
        calm = 1.0 - 0.35 * _win(t, 55.4, 60.0, 0.6, 0.8)           # calmer while the words are read
        k = (0.6 + 0.4 * np.exp(-u / 2.0)) * calm * (1.0 - _sc(69.6, 70.5, t))
        k *= 1.0 + 0.35 * hit_pulse(t, [64.2, 65.94, 69.4], fall=0.5)
        # after the words, the crown comes down and settles round the city ("as Father prophesied")
        dn = _sc(61.0, 64.2, t)
        sc = np.array([1.0 + 0.28 * dn, 1.0, 1.0 + 0.28 * dn])
        off = np.array([0.0, -98.0 * dn, 0.0])
        P = self.c + (self.P - self.c) * sc + off
        G = self.c + (self.G - self.c) * sc + off
        out = [dict(pos=P, size=0.75, color=lin("#ffe7b0"), alpha=grow * k, emit=2.4 + 3.0 * np.exp(-u / 0.6),
                    kind="spark", twinkle=0.5, seed=self.s, reflect=False),
               dict(pos=P[::6], size=5.0, color=lin("#ffcf8a"), alpha=0.05 * grow[::6] * k, emit=1.0,
                    kind="soft", reflect=False)]
        g = np.clip((u - self.gd) / 0.3, 0.0, 1.0)
        out.append(dict(pos=G, size=2.6, color=self.GC, alpha=g * k, emit=3.5, kind="spark", twinkle=0.4,
                        reflect=False))
        return out


# =========================================================================================================
# The nations on Mount Zion
# =========================================================================================================
# The climbs pass up the middle of the front: there the people are true figures (one crowd per climb, each on
# only in its own shot; a glitter stands in for them in every other view). (tiers, x from, x to)
NEAR = dict(zion_wide=(range(0, 3), -5.0, 135.0), zion_full=(range(2, 6), -15.0, 110.0))


def _places(tiers, density, seed, front_share=0.9):
    """Where people stand on the terraces (x, y, z) and their tier: between the parapet and the gardens, clear
    of the stairways."""
    r = np.random.default_rng(seed)
    out, kk = [], []
    for k in tiers:
        R0, Ri = tier_r(k) - 1.6, tier_r(k + 1) + 8.0
        n = int(np.pi * (R0 ** 2 - Ri ** 2) * density)
        a = _az(n, r, front_share)
        rr = np.sqrt(Ri ** 2 + (R0 ** 2 - Ri ** 2) * r.random(n))
        p = _xz(rr, a, tier_y(k))
        p = p[~_stair_mask(p, 9.5)]
        out.append(p)
        kk.append(np.full(len(p), k))
    return np.concatenate(out), np.concatenate(kk)


def _glitter_people(P, K, born, seed, gain=1.0):
    """Tiny standing figures of light: one stroke each, dim at the feet and bright at the head, so from afar
    they glitter and read as countless people. The nations stand together: each block of the terraces has its
    own colour among the nine, mixed with warm white."""
    r = np.random.default_rng(seed)
    n = len(P)
    h = r.uniform(0.9, 1.1, n)
    foot = P + np.array([0.0, 0.2, 0.0])
    head = P + np.stack([np.zeros(n), 1.6 * h, np.zeros(n)], 1)
    az = np.arctan2(P[:, 0] - ZC[0], P[:, 2] - ZC[2])
    block = (np.floor(az / np.radians(11.0)).astype(int) * 5 + K * 4) % 9
    nine = np.asarray([lin(c) for c in COL9])
    j = r.random(n)
    col = np.where((j < 0.62)[:, None], nine[block] * 0.65 + lin(WHITE) * 0.35,
                   np.where((j < 0.85)[:, None], lin("#ffd9a0")[None, :], lin("#fff0dc")[None, :]))
    return [dict(pos=foot, pos2=head, size=0.28, color=col * 0.85, alpha=0.18 * gain, alpha2=0.75 * gain,
                 kind="line", emit=1.3, birth=born, fade=0.7, flash=1.5, reflect=False)]


def _nations():
    """The two populations: the first climb (1:30.7) fills the lower four terraces and dots the upper ones; the
    second climb (2:51.5) fills the whole mountain. They come up from the sea, terrace after terrace."""
    r = np.random.default_rng(171)
    P1, K1 = _places(range(0, 4), 0.15, 61)
    P1b, K1b = _places(range(4, 6), 0.05, 62)
    P2, K2 = _places(range(4, 6), 0.12, 63)
    P3, K3 = _places(range(0, 6), 0.07, 64)
    P = np.concatenate([P1, P1b, P2, P3])
    K = np.concatenate([K1, K1b, K2, K3])
    born = np.concatenate([90.4 + 1.1 * K1 + 1.2 * r.random(len(P1)),
                           93.5 + 0.9 * (K1b - 4) + 2.0 * r.random(len(P1b)),
                           171.2 + 0.5 * (K2 - 4) + 1.0 * r.random(len(P2)),
                           170.9 + 0.45 * K3 + 1.2 * r.random(len(P3))])
    return P, K, born


def _near(P, K, shot):
    tiers, x0, x1 = NEAR[shot]
    x = P[:, 0] - ZC[0]
    return np.isin(K, list(tiers)) & (x > x0) & (x < x1) & (P[:, 2] > ZC[2])


def nations_k(t):
    return local_k(t) if t < 254.07 else 0.0


# =========================================================================================================
# Light pouring down, the column of light
# =========================================================================================================
class Pour:
    """For Your sacrifice, for Your devotion (1:39.4 to 1:49.4): beams of light pour down from heaven onto the
    people on the terraces (left and right of the words), one after another, gold dust drifting slowly down in
    them; the people shine brighter. Thanks to Father (1:49.8): a column of light rises from the church to heaven."""

    def __init__(self):
        r = np.random.default_rng(91)
        az = np.radians([-58.0, -44.0, -31.0, -20.0, 20.0, 31.0, 44.0, 58.0, 70.0, -70.0])
        tk = [1, 0, 2, 1, 0, 2, 1, 0, 2, 2]
        rf = [0.9, 0.95, 0.85, 0.92, 0.95, 0.85, 0.9, 0.95, 0.9, 0.9]
        self.land = np.stack([ZC + _v(tier_r(k) * f * np.sin(a), tier_y(k) + 1.0, tier_r(k) * f * np.cos(a))
                              for a, k, f in zip(az, tk, rf)])
        self.dir = _unit(_v(-0.22, 1.0, -0.30))
        self.w = np.array([12.0, 14.0, 10.0, 9.0, 11.0, 10.0, 14.0, 12.0, 10.0, 10.0])
        self.on = np.array([99.4, 100.1, 100.6, 101.3, 99.8, 100.4, 101.0, 101.6, 103.6, 104.2])
        self.f = r.random((700, 4))
        self.c = r.random((1400, 4))

    def sample(self, t):
        if local_k(t) <= 0.0 or shot_name(t) != "zion_wide":
            return None
        out = []
        k = _env(t, 99.0, 110.0, 0.4, 1.6)
        if k > 0.0:
            p = np.clip((t - self.on) / 1.6, 0.0, 1.0)            # each beam pours down from the sky
            p = p * p * (3.0 - 2.0 * p)
            top = self.land + self.dir[None, :] * 560.0
            bot = top + (self.land - top) * p[:, None]
            kb = k * (p > 0.0) * (0.85 + 0.15 * beat_pulse(t, 0.25))
            mid = 0.5 * (top + bot)
            out.append(dict(pos=np.concatenate([top, mid]), pos2=np.concatenate([mid, bot]),
                            size=np.concatenate([self.w * 0.7, self.w * 0.85]),
                            size2=np.concatenate([self.w * 0.85, self.w]),
                            alpha=np.concatenate([0.0 * kb, 0.07 * kb]), alpha2=np.concatenate([0.07 * kb, 0.24 * kb]),
                            color=lin("#ffe2b0"), emit=1.2, kind="ribbon", reflect=False, dof=0.0))
            # where a beam has landed, a pool of light on the people
            land = k * np.clip((t - self.on - 1.4) / 0.6, 0.0, 1.0)
            out.append(dict(pos=self.land, size=self.w * 2.2, color=lin("#ffd89a"), alpha=0.16 * land, emit=1.0,
                            kind="soft", reflect=False))
            # gold dust drifting slowly down in the beams
            s = self.f
            i = (s[:, 0] * len(self.land)).astype(int)
            fall = np.mod(t * (0.03 + 0.03 * s[:, 1]) + s[:, 2], 1.0)
            q = self.land[i] + self.dir[None, :] * (260.0 * (1.0 - fall))[:, None]
            q += np.stack([(s[:, 3] - 0.5) * self.w[i] * 0.8, np.zeros(len(s)), (s[:, 2] - 0.5) * self.w[i] * 0.8], 1)
            vis = np.clip((t - self.on[i] - 1.6 * (1.0 - fall)) / 0.5, 0.0, 1.0)
            out.append(dict(pos=q, size=0.6, color=lin("#ffe8c0"), alpha=0.8 * k * vis * np.sin(np.pi * fall),
                            emit=2.0, kind="spark", twinkle=0.8, seed=s[:, 3], reflect=False))
        k = _env(t, 109.8, 117.0, 0.6, 0.3)
        if k > 0.0:
            u = t - 109.8
            reach = SUMMIT + 50.0 + 900.0 * _sc(0.0, 2.2, u)       # the column rises to heaven
            s = self.c
            a = 2 * np.pi * s[:, 0]
            rr = 9.0 * np.sqrt(s[:, 1])
            y = SUMMIT + 50.0 + np.mod(u * 70.0 * (0.6 + 0.8 * s[:, 2]) + 900.0 * s[:, 3], 900.0)
            p = np.stack([CHURCH[0] + rr * np.sin(a), y, CHURCH[2] + rr * np.cos(a)], 1)
            out.append(dict(pos=p, size=0.9, color=lin("#fff4dc"), alpha=k * 0.8 * (y < reach), emit=2.6,
                            kind="spark", twinkle=0.6, seed=s[:, 3], reflect=False))
            ys = np.linspace(SUMMIT + 50.0, SUMMIT + 950.0, 120)
            q = np.stack([np.full(120, CHURCH[0]), ys, np.full(120, CHURCH[2])], 1)
            out.append(dict(pos=q, size=16.0, color=lin("#fff0d0"), alpha=0.05 * k * (ys < reach)
                            * (1.0 - 0.6 * (ys - ys[0]) / 900.0), emit=1.0, kind="soft", reflect=False))
        return out or None


def pour_k(t):
    """The people shine brighter while the light pours down on them."""
    return local_k(t) * (shot_name(t) == "zion_wide") * _env(t, 99.6, 110.0, 1.5, 1.6)


# =========================================================================================================
# Rings of light over the land
# =========================================================================================================
RINGS = [(86.70, 90.0, 0.6), (88.0, 90.0, 0.45), (89.3, 90.0, 0.35),        # waves of praise ripple the land
         (162.86, 75.0, 1.0), (165.16, 70.0, 0.7), (171.48, 70.0, 0.6)]    # the shockwave of the second slam


class Rings:
    """Rings of light rolling out over the land and the sea from the foot of Mount Zion."""

    def __init__(self):
        a = np.linspace(0, 2 * np.pi, 5000, endpoint=False)
        self.cs = np.stack([np.sin(a), np.cos(a)], 1)
        self.s = np.random.default_rng(111).random(5000)

    def sample(self, t):
        if local_k(t) <= 0.0 or stage_view(t):
            return None
        out = []
        for t0, v, k in RINGS:
            u = t - t0
            if not (0.0 <= u < 9.0):
                continue
            r = tier_r(0) + 4.0 + v * u
            p = np.stack([ZC[0] + r * self.cs[:, 0], np.full(len(self.cs), 0.35), ZC[2] + r * self.cs[:, 1]], 1)
            a = k * np.exp(-u / 3.5) * _sc(0.0, 0.2, u)
            out.append(dict(pos=p, size=0.9 + 0.08 * u, color=lin("#ffe2b0"), alpha=a, emit=2.6, kind="spark",
                            twinkle=0.4, seed=self.s))
            out.append(dict(pos=p[::5], size=6.0, color=lin("#ffcf8a"), alpha=0.10 * a, emit=1.5, kind="soft"))
        return out or None


def _ripple_k(k):
    """A pulse of light running down the parapets from the summit at each ring (the land ripples)."""
    times = [t0 + 0.12 * (N_TIER - 1 - k) for t0, _, _ in RINGS]
    return lambda t: local_k(t) * (not stage_view(t)) * min(hit_pulse(t, times, rise=0.05, fall=0.7), 1.2)


SHAFTS = [
    # thanks to Father (1:49.8 to 1:57): a column of light rises from the church to heaven
    dict(base=(float(CHURCH[0]), float(CHURCH[2])), radius=12.0, top=2400.0, spread=-0.2, color="#fff2d8",
         strength=lambda t: local_k(t) * (shot_name(t) == "zion_wide") * _env(t, 109.8, 117.0, 1.6, 0.3) * 0.05),
]


def add(scene):
    import os
    skip = os.environ.get("ZION_SKIP", "").split(",")
    _add = scene.add
    scene = type("S", (), {"add": staticmethod(lambda n, *a, **k: None if n in skip else _add(n, *a, **k))})
    dim, gold = _mountain()
    scene.add("zion body", _Off(_body()), mask=Mask("dark", strength=body_k, grow=1.9, soft=4.0), reflect=False)
    scene.add("zion dim", Static(dim, local_k))
    scene.add("zion gold", Static(gold, local_k))
    for k in range(N_TIER):
        ring = _ring(ZC, tier_r(k) + 0.1, tier_y(k) + 0.9, 1.0)
        scene.add(f"zion ripple {k}", Static([_batch(ring, 0.9, lin("#fff0d0"), 1.0, emit=2.5, reflect=False)],
                                             _ripple_k(k)))
    scene.add("crown", Crown())
    # the nations on Mount Zion: a glitter of countless people; true figures where the camera climbs past them
    P, K, born = _nations()
    nw, nf = _near(P, K, "zion_wide"), _near(P, K, "zion_full")
    rest = ~(nw | nf)
    scene.add("nations", Static(_glitter_people(P[rest], K[rest], born[rest], 3), nations_k))
    scene.add("nations lit", Static(_glitter_people(P[rest], K[rest], born[rest], 3, 0.5), pour_k))
    rng = np.random.default_rng(9)
    for shot, sel, seed in (("zion_wide", nw & ~nf, 4), ("zion_full", nf, 5)):
        on = (lambda s: (lambda t: float(shot_name(t) == s)))(shot)
        scene.add(f"nations mid {shot}", Static(_glitter_people(P[sel], K[sel], born[sel], seed),
                                                (lambda f: (lambda t: nations_k(t) * (1.0 - f(t))))(on)))
        i = np.where(sel)[0]
        i = i[rng.random(len(i)) < 0.5]
        scene.add(f"nations near {shot}", GCrowd(
            gain=(lambda f: (lambda t: nations_k(t) * f(t)))(on), places=P[i],
            facing=lambda x, z: float(np.degrees(np.arctan2(ZC[0] - x, ZC[2] - z))),
            kinds=(("stand", 3.0), ("raise", 1.2), ("open", 0.6)),
            people=dict(woman=1.0, man=1.0, elder=0.2, child=0.15), start=born[i], color="#ffcf7a",
            color2="#fff0d0", bright=1.3, points=70, size=9.0, flash=1.5, seed=float(seed)))
    scene.add("pour", Pour())
    scene.add("rings", Rings())
