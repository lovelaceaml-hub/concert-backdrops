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

def _at(az, r, y):
    """A place round Mount Zion: azimuth in degrees from the front (+z) toward +x, r metres from its axis."""
    a = np.radians(az)
    return ZC + _v(r * np.sin(a), y, r * np.cos(a))


def _orbit(t0, t1, az0, az1, r0, r1, y0, y1, tgt0, tgt1, n=5):
    """Keys for a helicopter move round the mountain (azimuth, radius and height eased together)."""
    out = []
    for i in range(n):
        u = i / (n - 1)
        out.append((t0 + (t1 - t0) * u, _at(az0 + (az1 - az0) * u, r0 + (r1 - r0) * u, y0 + (y1 - y0) * u),
                    tgt0 + (tgt1 - tgt0) * u))
    return out


def _shot(name, t0, t1, keys, fov=50.0, **kw):
    return dict(name=name, kind="local", t0=t0, t1=t1, fov=fov, aperture=0.0, keys=keys, **kw)


CR = ZC + _v(0.0, SUMMIT + 124.0, -10.0)      # the crown, high over the city (before it settles round it)
CH = ZC + _v(0.0, SUMMIT + 30.0, -10.0)       # the church's middle
SHOTS = [
    # the crown of light ignites as a blazing light, comets fanning out of it: from high above, banking down
    # and round until the crown sits low under the words
    _shot("zion_crown", 53.78, 58.4,
          [(53.78, ZC + _v(30.0, 560.0, 190.0), CR + _v(0.0, 0.0, -120.0)),
           (56.0, _at(34.0, 320.0, 300.0), CR + _v(0.0, 30.0, -40.0)),
           (58.4, _at(18.0, 226.0, 236.0), CR + _v(0.0, 48.0, 0.0))], fov=50.0, roll=(14.0, -3.0)),
    # as Father prophesied: a banking flight over the city as the crown comes down round it
    _shot("zion_crown", 61.3, 64.2,
          [(61.3, _at(-42.0, 320.0, 150.0), CH + _v(0.0, 40.0, 0.0)), (62.8, _at(-20.0, 250.0, 122.0), CH + _v(0.0, 24.0, 0.0)),
           (64.2, _at(4.0, 180.0, 102.0), CH + _v(0.0, 6.0, 0.0))], fov=52.0, roll=(-10.0, 6.0)),
    # fulfilled: a great banking spiral round the mountain as the comets stream up the stairways and the
    # terraces fill with gold
    _shot("zion_crown", 64.2, 69.4,
          _orbit(64.2, 69.4, -70.0, 50.0, 480.0, 360.0, 24.0, 130.0, ZC + _v(0, 28, 0), ZC + _v(0, 52, 0), 7),
          fov=52.0, roll=(12.0, -6.0)),
    # the city full of gold: pulling back fast and high
    _shot("zion_crown", 69.4, 70.54,
          [(69.4, ZC + _v(10.0, 104.0, 250.0), ZC + _v(0.0, 70.0, 0.0)),
           (70.54, ZC + _v(40.0, 190.0, 560.0), ZC + _v(0.0, 40.0, 0.0))], fov=50.0, roll=(-4.0, 4.0)),
    # waves of praise: racing low over the sea between two walls of cloud toward Zion, the rings and the
    # comets rushing under and past the camera
    _shot("praise_ripples", 86.7, 90.72,
          [(86.7, ZC + _v(0.0, 9.0, 1320.0), ZC + _v(0.0, 40.0, 0.0)), (88.7, ZC + _v(-6.0, 7.0, 900.0), ZC + _v(0.0, 44.0, 0.0)),
           (90.72, ZC + _v(10.0, 6.0, 470.0), ZC + _v(0.0, 50.0, 0.0))], fov=58.0, roll=(-6.0, 5.0)),
    # standing firm, the first climb: a huge banking spiral up the mountain, comets corkscrewing ahead
    _shot("zion_wide", 90.72, 97.7,
          _orbit(90.72, 97.7, -64.0, 58.0, 420.0, 240.0, 14.0, 112.0, ZC + _v(0, 34, 0), ZC + _v(0, 80, 0), 8),
          fov=54.0, roll=(14.0, -10.0)),
    # sacrifice: pillars of light fall from the clouds onto the people; a slow crane over the upper terraces
    _shot("zion_wide", 99.4, 103.6,
          [(99.4, ZC + _v(110.0, 150.0, 330.0), ZC + _v(0.0, 70.0, 60.0)),
           (101.5, ZC + _v(80.0, 132.0, 280.0), ZC + _v(0.0, 66.0, 70.0)),
           (103.6, ZC + _v(46.0, 118.0, 236.0), ZC + _v(0.0, 60.0, 80.0))], fov=54.0, roll=(-4.0, 3.0)),
    # devotion: diving down the great stairway with the golden waterfall
    _shot("zion_wide", 103.6, 105.14,
          [(103.6, ZC + _v(6.0, 86.0, 130.0), ZC + _v(0.0, 10.0, 340.0)),
           (105.14, ZC + _v(2.0, 52.0, 236.0), ZC + _v(0.0, -10.0, 440.0))], fov=58.0, roll=(0.0, 12.0)),
    # thanks to Father: the grandest pillar, the column to heaven, clouds parting round it, lanterns rising
    _shot("zion_wide", 109.8, 117.0,
          [(109.8, _at(45.0, 360.0, 60.0), CH + _v(-30.0, 10.0, 25.0)),
           (112.4, _at(36.0, 390.0, 96.0), CH + _v(-50.0, 96.0, 36.0)),
           (114.8, _at(20.0, 450.0, 150.0), CH + _v(-56.0, 130.0, 20.0)),
           (117.0, _at(4.0, 520.0, 210.0), CH + _v(-60.0, 130.0, 4.0))], fov=54.0, roll=(-6.0, 4.0)),
    # the shockwave across the land and sea, chased low over the water
    _shot("zion_full", 165.16, 171.48,
          [(165.16, _at(30.0, 320.0, 12.0), ZC + _v(0.0, 40.0, 0.0)), (167.5, _at(34.0, 540.0, 9.0), ZC + _v(0.0, 46.0, 0.0)),
           (169.5, _at(26.0, 800.0, 7.0), ZC + _v(0.0, 50.0, 0.0)), (171.48, _at(18.0, 900.0, 6.0), ZC + _v(0.0, 52.0, 0.0))],
          fov=50.0, roll=(8.0, -8.0)),
    # standing firm, the second climb: a bigger banking spiral, far higher than the first
    _shot("zion_full", 171.48, 178.4,
          _orbit(171.48, 178.4, -40.0, 80.0, 380.0, 230.0, 40.0, 190.0, ZC + _v(0, 40, 0), ZC + _v(0, 60, 0), 8),
          fov=54.0, roll=(-14.0, 10.0)),
    # sacrifice: the mountain blazing, a high helicopter orbit
    _shot("zion_full", 180.7, 183.0,
          _orbit(180.7, 183.0, 76.0, 48.0, 400.0, 380.0, 180.0, 168.0, ZC + _v(0, 36, 0), ZC + _v(0, 40, 0), 4),
          fov=50.0, roll=(6.0, -4.0)),
]


FILL_T = [64.2, 64.2, 64.2, 65.94, 65.94, 69.4, 69.4]     # "being fulfilled": the terraces fill with light

# Round 6 (Anthony: "so many of the same colors that it's hard to see and distinguish things since it's all gold"):
# each part of the city has its own palette. Gold only for the great stairways (and the crown).
PEARL = "#f6f0ff"          # the walls and the gates: pearl white
PEARL_LO = "#5a3f8c"       # the foot of each wall: deep violet (the light falls from the parapet down)
PEARL_RAIL = "#eef2ff"     # the parapets and their lamps: cool white
GLASS = ("#8fd0ff", "#5fe3cf", "#a9b8ff")       # the towers: sky blue, teal, periwinkle glass
GLASS_EDGE = ("#e6f6ff", "#dcfff8", "#eef0ff")
LEAF = ("#5fd27f", "#8fe6a0", "#3fbf8f")        # the gardens
BLOSSOM = ("#ffb3c4", "#c9b3ff", "#fff2fa", "#ff9fc8")
DOME = ("#ffb3c4", "#c9b3ff", "#9fd8ff")         # the pavilions' domes: rose, lavender, sky
NICHE = ("#ff9fc8", "#9fd8ff", "#c9b3ff")        # the lit niches: stained glass
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
    par, par_k, pil_a, pil_b, niche, tread = [], [], [], [], [], []
    post_a, post_b, lamp = [], [], []
    hi, lo = lin(PEARL), lin(PEARL_LO)
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
    F, FC, FA, FK, SP = (np.concatenate(v) for v in (face, face_c, face_a, face_k, spark))
    PA, PK, NI, TR = (np.concatenate(v) for v in (par, par_k, niche, tread))
    NIC = np.asarray([lin(NICHE[i % 3]) for i in range(len(NI))])
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
    # the walls (they form through the intro: a few lights and paths first, the walls coming up behind them)
    walls = [
        _batch(F[low], 2.2, FC[low] * 0.5, FA[low], kind="soft", emit=1.0),
        _batch(F[~low], 2.2, FC[~low] * 0.5, FA[~low], kind="soft", emit=1.0, reflect=False),
        _batch(SP, 0.30, lin("#f2eeff"), 0.8, emit=1.4, twinkle=0.7, reflect=False),
        dict(pos=PB_a, pos2=PB_b, size=0.35, color=lin("#d8ccff") * 0.45, alpha=0.3, alpha2=0.8, kind="line",
             emit=1.0, reflect=False),
        _batch(NI, 1.3, NIC * 0.8, 0.85, kind="soft", emit=1.6, reflect=False),
        _batch(TR, 0.6, lin("#bcdcff") * 0.30, 0.40, kind="soft", emit=0.8, reflect=False),
    ]
    # the lights and paths: parapets, their lamps, the golden stairways (there from the first frame)
    dim = [
        _batch(PA, 0.45, lin(PEARL_RAIL) * 0.75, 0.5, emit=1.0, reflect=False),
        dict(pos=PO_a, pos2=PO_b, size=0.22, color=lin(PEARL_RAIL) * 0.6, alpha=0.6, kind="line", emit=1.0,
             reflect=False),
        _batch(LP, 0.8, lin("#e6f2ff"), 0.9, emit=2.0, twinkle=0.3, reflect=False),
        _batch(ST, 0.40, lin(GOLD2) * 0.5, 0.8, emit=1.0, reflect=False),
        _batch(RA, 0.35, lin("#ffe6b8") * 0.5, 0.8, emit=1.0, reflect=False),
        _batch(LA, 0.9, lin("#ffdca0"), 0.9, emit=2.2, twinkle=0.3, reflect=False),
    ]
    # "being fulfilled": gold rises up each wall in turn (64.2, 65.94, 69.4)
    FT = np.asarray(FILL_T)
    y0s = np.asarray([tier_y(k - 1) if k else 0.0 for k in FK])
    fb = FT[FK] + 0.45 * (F[:, 1] - y0s) / 10.0
    upper = FA > 0.16
    # and the terraces' floors fill with a warm golden light, from the front edge back
    fl, fl_b = [], []
    for k in range(N_TIER - 1):
        R0, Ri = tier_r(k), tier_r(k + 1)
        m = int((R0 ** 2 - Ri ** 2) * FRONT * 0.5 / 26.0)
        a = _az(m, r, 0.92)
        rr = np.sqrt(Ri ** 2 + (R0 ** 2 - Ri ** 2) * r.random(m))
        fl.append(_xz(rr, a, tier_y(k) + 0.6))
        fl_b.append(FT[k] + 0.3 + 0.5 * (R0 - rr) / (R0 - Ri) + 0.2 * r.random(m))
    FL, FB = np.concatenate(fl), np.concatenate(fl_b)
    # (round 6) the walls fill with pearl light, the floors with a pale glass light; only the stairways are gold
    gold = [
        _batch(FL, 6.0, lin("#bfe2ff"), 0.07, kind="soft", emit=1.0, birth=FB, fade=0.7, flash=2.0, reflect=False),
        _batch(F[upper], 2.6, lin("#e2d8ff") * 0.40, FA[upper] * 0.70, kind="soft", emit=1.3, birth=fb[upper], fade=0.6,
               flash=1.5, reflect=False),
        _batch(PA, 0.55, lin(PEARL_RAIL) * 0.8, 0.45, emit=1.3, birth=FT[PK] + 0.45, fade=0.4, flash=3.0, twinkle=0.4,
               reflect=False),
        _batch(ST, 0.45, lin(GOLD), 0.7, emit=1.4, birth=FT[SK] + 0.2, fade=0.6, flash=2.0, reflect=False),
    ]
    return walls, dim, gold


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
# Round 6: the city grows (Anthony: "the mountain of Zion, a city, can start to form and continue to grow larger
# and larger"). At first only lights and paths (the parapet lamps, the golden stairways); the walls come up
# through the intro; on the glory the pearl gates light at the summit, on "fulfilled" down every stairway, and
# the gardens bloom terrace by terrace; on the first climb glass towers rise on the lower terraces, on the
# sacrifice and thanks the upper ones, pavilions on thanks to Father; on the second slam every tower grows
# taller and a new ring of the city rises out of the sea behind the shockwave; on the sacrifice and the third
# slam the towers take their spires and a second ring rises. Everything rises on the beats (static point sets
# with birth times: a tower draws itself upward with a flash at its growing top). Each part has its palette
# (pearl gates and walls, sky-blue and teal glass towers, green gardens with rose and lavender blossoms, white
# pavilions with coloured domes; gold only for the stairways and the crown); mist lies at the foot of each wall
# so the terraces stand apart in depth.
# =========================================================================================================
RISE_S = 1.1                     # how long a tower takes to draw itself up (seconds)
R_RING = (tier_r(0) + 40.0, tier_r(0) + 82.0)    # the new rings of the city on the sea (radius)
RING_T = (SLAM2 + 2.3, SLAM3)                      # when they rise: behind the shockwave (165.16), on slam 3


def _snap(t):
    """The first beat at or after t (things rise on the beat)."""
    t = np.asarray(t, np.float64)
    i = np.clip(np.searchsorted(BEATS, t - 0.02), 0, len(BEATS) - 1)
    return np.where(BEATS[i] >= t - 0.02, BEATS[i], t)


class _Parts:
    """Collects lines, soft glows and sparks with their birth times, and makes the batches."""

    def __init__(self):
        self.L, self.S, self.K = [], [], []

    def line(self, a, b, col, alpha, birth):
        a, b = np.atleast_2d(a), np.atleast_2d(b)
        n = len(a)
        self.L.append((a, b, np.broadcast_to(col, (n, 3)), np.broadcast_to(alpha, (n,)), np.broadcast_to(birth, (n,))))

    def soft(self, p, col, alpha, birth):
        p = np.atleast_2d(p)
        n = len(p)
        self.S.append((p, np.broadcast_to(col, (n, 3)), np.broadcast_to(alpha, (n,)), np.broadcast_to(birth, (n,))))

    def spark(self, p, col, birth):
        p = np.atleast_2d(p)
        n = len(p)
        self.K.append((p, np.broadcast_to(col, (n, 3)), np.broadcast_to(birth, (n,))))

    def batches(self, lsize=0.22, ssize=2.4, ksize=0.7, flash=2.5):
        out = []
        if self.L:
            A, B, C, Al, Bi = (np.concatenate(x) for x in zip(*self.L))
            out.append(dict(pos=A, pos2=B, size=lsize, color=C, alpha=Al, alpha2=Al, kind="line", emit=1.5,
                            birth=Bi, fade=0.35, flash=flash, reflect=False, seed=np.random.default_rng(1).random(len(A))))
        if self.S:
            P, C, Al, Bi = (np.concatenate(x) for x in zip(*self.S))
            out.append(_batch(P, ssize, C, Al, kind="soft", emit=1.0, birth=Bi, fade=0.6, flash=1.0, reflect=False))
        if self.K:
            P, C, Bi = (np.concatenate(x) for x in zip(*self.K))
            out.append(_batch(P, ksize, C, 0.95, emit=3.0, birth=Bi, fade=0.3, flash=3.0, twinkle=0.4, reflect=False))
        return out


def _rise_birth(y, hs, bs):
    """Birth of a point at height y of a tower that grows to heights hs (cumulative) at the times bs."""
    y = np.asarray(y, np.float64)
    out = np.full(y.shape, np.nan)
    h0 = 0.0
    for h, b in zip(hs, bs):
        sel = np.isnan(out) & (y <= h + 1e-6)
        out = np.where(sel, b + RISE_S * np.clip((y - h0) / max(h - h0, 1e-6), 0.0, 1.0), out)
        h0 = h
    return np.where(np.isnan(out), bs[-1] + RISE_S, out)


def _tower(T, c, rw, hs, bs, gi, jewel, spire=True):
    """A slender glass tower of light: six edges, floor bands, glass glowing inside, a bright band at the top of
    each growth, a spire with a jewel when it is finished. It draws itself upward at each growth."""
    H = hs[-1]
    n = 6
    ang = np.arange(n) * 2 * np.pi / n + 0.3

    def ring(y):
        rr = rw * (1.0 - 0.28 * y / max(H, 1.0))
        return np.stack([c[0] + rr * np.cos(ang), np.full(n, c[1] + y), c[2] + rr * np.sin(ang)], 1)
    glass = lin(GLASS[gi])
    edge = glass * 0.65 + lin(GLASS_EDGE[gi]) * 0.35
    ys = np.arange(0.0, H - 1e-6, 2.0)
    ys = np.append(ys, H)
    for y0, y1 in zip(ys[:-1], ys[1:]):
        T.line(ring(y0), ring(y1), edge * 0.8, 0.85, _rise_birth(np.full(n, y1), hs, bs))
    for y in np.arange(3.6, H - 0.5, 3.6):
        R = ring(y)
        T.line(R, np.roll(R, -1, 0), glass * 0.9, 0.55, _rise_birth(np.full(n, y), hs, bs))
    for h in hs:
        R = ring(h)
        T.line(R, np.roll(R, -1, 0), edge * 1.3, 1.0, _rise_birth(np.full(n, h), hs, bs))
    r = np.random.default_rng(int(abs(c[0] * 7 + c[2] * 3)) % 100000)
    m = int(H * 2.2)
    yy = H * r.random(m) ** 0.9
    aa = r.uniform(0, 2 * np.pi, m)
    rr = rw * (1.0 - 0.28 * yy / max(H, 1.0)) * 0.8
    P = np.stack([c[0] + rr * np.cos(aa), c[1] + yy, c[2] + rr * np.sin(aa)], 1)
    T.soft(P, glass * 0.8, 0.22, _rise_birth(yy, hs, bs))
    if spire:
        tip = np.asarray(c, np.float64) + np.array([0.0, H + 2.8 * rw, 0.0])
        R = ring(H)
        b = bs[-1] + RISE_S + 0.05
        T.line(R, np.repeat(tip[None], n, 0), edge, 0.95, b)
        T.spark(tip + np.array([0.0, 0.4, 0.0]), lin(jewel), b + 0.25)


def _pavilion(T, c, i, b):
    """A round pavilion of light: eight white columns, a dome in rose, lavender or sky, a finial."""
    n, R, h = 8, 3.4, 5.0
    a = np.arange(n) * 2 * np.pi / n
    base = np.stack([c[0] + R * np.cos(a), np.full(n, c[1]), c[2] + R * np.sin(a)], 1)
    top = base + np.array([0.0, h, 0.0])
    w = lin("#f8f4ff")
    T.line(base, top, w * 0.9, 0.9, b + 0.4 * np.arange(n) / n)
    T.line(top, np.roll(top, -1, 0), w, 1.0, b + 0.45)
    T.line(base, np.roll(base, -1, 0), w * 0.6, 0.7, b)
    dc = lin(DOME[i % 3])
    for k in range(n):
        e = np.linspace(0.0, 1.0, 6)
        rr, yy = R * np.cos(e * np.pi / 2), h + 3.0 * np.sin(e * np.pi / 2)
        Q = np.stack([c[0] + rr * np.cos(a[k]), c[1] + yy, c[2] + rr * np.sin(a[k])], 1)
        T.line(Q[:-1], Q[1:], dc, 0.95, b + 0.55 + 0.25 * e[1:])
    T.soft(np.asarray(c) + np.array([0.0, h + 1.2, 0.0]), dc * 0.8, 0.22, b + 0.6)
    T.soft(np.asarray(c) + np.array([0.0, 2.2, 0.0]), lin("#fff2e0") * 0.6, 0.18, b + 0.3)
    T.spark(np.asarray(c) + np.array([0.0, h + 3.5, 0.0]), lin("#fff6e6"), b + 0.9)


def _garden(T, c, r, b):
    """A garden of light: three trees with green crowns and rose, lavender and white blossoms."""
    for j in range(3):
        a = 2 * np.pi * j / 3 + r.uniform(0, 1)
        p = np.asarray(c) + np.array([2.4 * np.cos(a), 0.0, 2.4 * np.sin(a)])
        hh = r.uniform(3.2, 4.6)
        bb = b + 0.12 * j
        T.line(p, p + np.array([0.0, hh * 0.65, 0.0]), lin("#cfe9c0") * 0.5, 0.7, bb)
        q = r.normal(0.0, 1.0, (16, 3)) * np.array([1.5, 1.1, 1.5]) + p + np.array([0.0, hh, 0.0])
        T.soft(q[:6], lin(LEAF[r.integers(0, 3)]) * 0.8, 0.30, bb + 0.1)
        T.spark(q[6:], lin(LEAF[r.integers(0, 3)]) * 0.9, bb + 0.1)
        bl = q[:9] + r.normal(0.0, 0.5, (9, 3))
        T.spark(bl, np.asarray([lin(BLOSSOM[x]) for x in r.integers(0, 4, 9)]), bb + 0.5 + 0.3 * r.random(9))


def _gate(T, c, d, hw, h, b):
    """A pearl gate over a stairway head: two pylons, a round arch, an inner arch, a jewel at the keystone,
    shimmering from rose to sky like mother-of-pearl."""
    sd = np.array([d[2], 0.0, -d[0]])
    up = np.array([0.0, 1.0, 0.0])
    w = hw + 1.6
    for s in (-1, 1):
        for o in (-0.7, 0.7):
            for f in (-0.7, 0.7):
                p = c + sd * s * (w + o) + d * f
                T.line(p, p + up * h, lin(PEARL) * 0.8, 0.9, b + 0.0)
    e = np.linspace(0.0, np.pi, 25)
    for rr, br, k in ((w, 1.0, 0.0), (w - 1.1, 0.7, 0.15)):
        A = c[None] + sd[None] * (rr * np.cos(e))[:, None] + up[None] * (h + rr * 0.55 * np.sin(e))[:, None]
        pearl = np.where((np.cos(e) > 0)[:, None], lin("#ffd6ec"), lin("#d6ecff")) * 0.5 + lin(PEARL) * 0.5
        T.line(A[:-1], A[1:], pearl[:-1] * br, 0.95, b + 0.25 + k + 0.3 * e[1:] / np.pi)
    key = c + up * (h + w * 0.55 + 0.6)
    T.soft(c + up * (h * 0.8), lin("#f0e8ff") * 0.6, 0.18, b + 0.3)
    T.spark(key, lin("#fff6ff"), b + 0.6)


def _band_slots(rb, step, y, front=FRONT):
    """Places along a ring of radius rb (a terrace's back band), clear of the stairways."""
    m = int(2 * front * rb / step)
    a = np.linspace(-front, front, m)
    p = _xz(rb, a, y)
    keep = ~_stair_mask(p, 13.0)
    return p[keep], a[keep]


def _city_parts():
    """The growing city: (gates, gardens, towers and pavilions, mist, the new rings on the sea) as batches."""
    r = np.random.default_rng(606)
    G, Gd, T, M = _Parts(), _Parts(), _Parts(), _Parts()
    # the pearl gates over every stairway head: the summit's on the glory, then down the mountain on "fulfilled"
    for s in STAIRS_AZ:
        d = np.array([np.sin(s), 0.0, np.cos(s)])
        hw = 8.0 if s == 0.0 else 5.0
        for k in range(N_TIER):
            c = ZC + d * (tier_r(k) - 3.0) + np.array([0.0, tier_y(k), 0.0])
            b = HIT["glory"] + 0.35 * (N_TIER - 1 - k) + 0.1 * abs(s) if k >= 5 else FILL_T[k] + 0.35 + 0.1 * abs(s)
            _gate(G, c, d, hw, 9.0 if s == 0.0 else 7.0, float(_snap(b)))
    # the terraces' back bands: gardens, towers and pavilions in a pattern (groups, never a uniform row)
    gen1 = {0: 90.72, 1: 91.6, 2: 92.6, 3: 99.4, 4: 101.5, 5: 109.8}
    pat = "GTGPGt"
    for k in range(N_TIER - 1):
        rb = tier_r(k + 1) + 6.0
        P, A = _band_slots(rb, 13.0, tier_y(k))
        for j, (p, a) in enumerate(zip(P, A)):
            kind = pat[(j + k) % len(pat)]
            u = abs(a) / FRONT
            p = p + r.uniform(-1.0, 1.0, 3) * np.array([1.0, 0.0, 1.0])
            if kind == "G":
                _garden(Gd, p, r, float(_snap(FILL_T[k] + 0.6 + 1.6 * u)))
            elif kind == "P":
                _pavilion(T, p, j, float(_snap(HIT["thanks"] + 0.5 * k + 2.4 * u)) if k < 5
                          else float(_snap(171.48 + 1.5 * u)))
            else:
                tall = kind == "t"
                h1 = r.uniform(9.0, 13.0)
                h2 = h1 + (r.uniform(12.0, 16.0) if tall else r.uniform(5.0, 8.0))
                h3 = h2 + (r.uniform(8.0, 12.0) if tall else 0.0)
                b1 = float(_snap(gen1[k] + 2.2 * u))
                b2 = float(_snap(SLAM2 + 2.3 + 0.6 * k + 2.4 * u))
                b3 = float(_snap((180.7 + 0.5 * k if k < 3 else SLAM3 + 0.5 * (k - 3)) + 1.6 * u))
                hs, bs = ([h1, h2, h3], [b1, b2, b3]) if tall else ([h1, h2], [b1, b2])
                _tower(T, p, r.uniform(2.2, 2.8) if tall else r.uniform(1.8, 2.3), hs, bs, (j + k) % 3,
                       COL9[(j * 4 + k) % 9], spire=True)
    # mist at the foot of each wall: the terraces stand apart in depth
    for k in range(N_TIER):
        R0, y0 = tier_r(k), (tier_y(k - 1) if k else 0.0)
        m = int(2 * FRONT * R0 / 7.0)
        a = np.linspace(-FRONT, FRONT, m) + r.uniform(-0.01, 0.01, m)
        P = _xz(R0 + 5.0 + r.uniform(0, 5, m), a, y0 + 1.0 + r.uniform(0, 1.5, m))
        M.soft(P, lin("#8f86d8") * 0.55, 0.05, 0.0)
    # the new rings of the city rising out of the sea (low pearl walls with gates, then gardens and towers)
    for ri, (R, t0) in enumerate(zip(R_RING, RING_T)):
        front = np.radians(100.0)
        m = int(2 * front * R * 4.0 * 0.35)
        a = r.uniform(-front, front, m)
        u = r.random(m) ** 0.7
        P = _xz(R, a, 4.0 * u)
        keep = ~_stair_mask(P, 7.0)
        P, u, a = P[keep], u[keep], a[keep]
        arrive = t0 + (R - tier_r(0) - 4.0) / (75.0 if ri == 0 else 90.0)
        col = lin(PEARL_LO)[None] * (1 - u[:, None]) + lin(PEARL)[None] * u[:, None]
        T.soft(P, col * 0.55, 0.10 + 0.25 * u ** 2, arrive + 0.5 * u + 0.25 * np.abs(a))
        q = _ring(ZC, R, 4.2, 1.6)
        aq = np.arctan2(q[:, 0] - ZC[0], q[:, 2] - ZC[2])
        q = q[(np.abs(aq) < front) & ~_stair_mask(q, 7.0)]
        aq = np.arctan2(q[:, 0] - ZC[0], q[:, 2] - ZC[2])
        T.spark(q[::5], lin("#e6f2ff"), arrive + 0.6 + 0.25 * np.abs(aq[::5]))
        T.soft(q[::2], lin(PEARL_RAIL) * 0.6, 0.30, arrive + 0.6 + 0.25 * np.abs(aq[::2]))
        for s in STAIRS_AZ:
            d = np.array([np.sin(s), 0.0, np.cos(s)])
            _gate(G, ZC + d * R, d, 8.0 if s == 0.0 else 5.0, 8.0 if s == 0.0 else 6.5,
                  float(_snap(arrive + 0.8 + 0.2 * abs(s))))
        P, A = _band_slots(R - 12.0, 15.0, 0.0, front)
        for j, (p, a) in enumerate(zip(P, A)):
            u = abs(a) / front
            b = float(_snap(t0 + (6.3 if ri == 0 else 4.3) + 2.2 * u))
            kind = "GTGPG"[j % 5]
            if kind == "G":
                _garden(Gd, p, r, b)
            elif kind == "P":
                _pavilion(T, p, j, b)
            else:
                h = r.uniform(10.0, 16.0)
                _tower(T, p, 2.2, [h], [b], j % 3, COL9[j % 9])
    return (G.batches(lsize=0.26, ssize=4.0, ksize=1.1), Gd.batches(lsize=0.18, ssize=2.6, ksize=0.55),
            T.batches(lsize=0.22, ssize=2.6, ksize=1.0), M.batches(ssize=10.0))


def form_k(t):
    """The walls come up through the intro (a few lights and paths first)."""
    return 0.35 + 0.65 * _sc(HIT["call2"], HIT["glory"], t)


# =========================================================================================================
# Round 6: the people streaming to Zion (Anthony: "more scenes where the people are streaming to Zion, to
# Heavenly Mother's glory, the church of God"). Rivers of people of light walk across the sea of glass toward
# the mountain, in through the pearl gates and up every great stairway to the summit, in the nine colours so
# they stand out from the pearl and glass of the city. The longest river comes in along the great avenue from
# far over the sea (the waves-of-praise flight passes low over it).
# =========================================================================================================
def _climb_profile(r_far):
    pts = [(r_far, 0.0), (tier_r(0) + 14.0, 0.0)]
    for k in range(N_TIER):
        y0 = tier_y(k - 1) if k else 0.0
        if k:
            pts.append((tier_r(k) + 14.0, y0))
        pts.append((tier_r(k), tier_y(k)))
    pts.append((R_TOP - 10.0, SUMMIT))
    pts = np.asarray(pts)
    L = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    return L, pts


def _owner(t):
    i = int(np.searchsorted(EDIT_T, t, side="right")) - 1
    return BLOCKS[max(min(i, len(BLOCKS) - 1), 0)]["owner"]


def stream_k(t):
    """The rivers of people: from "as Father prophesied" on, wherever Zion is seen (not in the procession's and
    the dancers' own scenes, nor in the close shots of the choir); they swell with the music."""
    if local_k(t) <= 0.0 or stage_view(t) or t >= LAST_CHORD or _owner(t) in ("proc", "dance"):
        return 0.0
    return _sc(60.6, 62.0, t) * (0.85 + 0.3 * intensity(t)) * (1.0 + 0.25 * intensity(t) * beat_pulse(t, 0.12))


# Round 7 (Anthony: "The theme should be more and more people going to Zion"): how full the rivers are, section
# by section: a few thin lines of people at "as Father prophesied" (1:01), more at each section, the sea and the
# stairways full by chorus 2 and the coda. Past each step the rivers also widen (more lanes) and take on more of
# the nine colours. A step lands on its section's first hit and fills in over a few seconds.
GROW_KEYS = [(61.0, 0.07), (64.2, 0.12), (70.54, 0.2), (82.08, 0.24), (84.5, 0.38), (90.72, 0.44),
             (99.4, 0.5), (117.0, 0.56), (162.86, 0.6), (165.5, 0.8), (171.48, 0.86), (199.62, 0.9),
             (203.5, 1.0)]


def grow_k(t):
    return float(np.interp(t, [k[0] for k in GROW_KEYS], [k[1] for k in GROW_KEYS]))


class Streams:
    """Rivers of people of light walking to Zion and climbing its stairways (one stroke and a bright head each,
    a soft glow on some, so from afar they read as rivers of light). Round 7: they grow through the film
    (grow_k): each person has a place in the order of joining; the first to come walk in the middle lanes in a
    few colours, those who join later widen the rivers (on the sea most of all) and bring the other colours."""

    def __init__(self):
        r = np.random.default_rng(616)
        self.paths, sa, lat, off, v, h, col, ph, q = [], [], [], [], [], [], [], [], []
        nine = np.asarray([lin(c) for c in COL9])
        order = r.permutation(9)                 # the colours in the order they join
        for i, s in enumerate(STAIRS_AZ):
            main = s == 0.0
            L, P = _climb_profile(1500.0 if main else 760.0)
            self.paths.append((L, P))
            n = 8000 if main else 2400
            hw = 7.0 if main else 4.2
            qq = r.random(n)                       # the order of joining (0 first)
            q.append(qq)
            sa.append(np.full(n, i))
            u = np.clip((0.3 + 0.7 * qq) * r.random(n), 0.0, 1.0)
            lat.append(hw * u * np.where(r.random(n) < 0.5, -1.0, 1.0))
            off.append(r.random(n) * L[-1])
            v.append(r.uniform(3.2, 4.2, n))
            h.append(r.uniform(0.9, 1.1, n))
            # (round 7, review f23: "the rivers of people as clear coloured lines") colour by lane: each lane of a
            # river one calm colour, side by side; the first comers walk the middle lanes (few colours), the later
            # ones the outer lanes, so each new lane brings a new colour
            nl = 4 if main else 2
            lane = np.minimum(np.floor(u * nl), nl - 1).astype(int) * 2 + (lat[-1] > 0)
            c = order[(lane + 2 * i) % 9]
            w = 0.05 + 0.05 * r.random(n)
            col.append(nine[c] * (1.0 - w)[:, None] + lin(WHITE)[None, :] * w[:, None])
            ph.append(r.uniform(0, 2 * np.pi, n))
        self.sa, self.lat, self.off, self.v, self.h, self.col, self.ph, self.q = (
            np.concatenate(x) for x in (sa, lat, off, v, h, col, ph, q))
        self.seed = r.random(len(self.sa))
        self.sea0 = tier_r(0) + 14.0

    def gain(self, t):
        return float(stream_k(t))

    def sample(self, t):
        k = stream_k(t)
        if k <= 0.0:
            return None
        g = grow_k(t)
        spread = 0.6 + 3.4 * _ss(0.3, 1.0, g)      # on the sea the rivers widen as more people come
        foot, head, alpha, idx = [], [], [], []
        for i, (L, P) in enumerate(self.paths):
            sel = np.where((self.sa == i) & (self.q < g))[0]
            if len(sel) == 0:
                continue
            d = np.mod(self.off[sel] + self.v[sel] * t, L[-1])
            rr = np.interp(d, L, P[:, 0])
            yy = np.interp(d, L, P[:, 1])
            sea = _ss(self.sea0, self.sea0 + 90.0, rr)
            a = STAIRS_AZ[i] + self.lat[sel] * (1.0 + spread * sea) / rr
            p = np.stack([ZC[0] + rr * np.sin(a), yy + 0.15, ZC[2] + rr * np.cos(a)], 1)
            bob = 0.06 * np.abs(np.sin(6.0 * t + self.ph[sel]))
            foot.append(p)
            head.append(p + np.stack([np.zeros(len(sel)), 1.55 * self.h[sel] + bob, np.zeros(len(sel))], 1))
            # each newcomer fades in as the river fills (no pop)
            alpha.append(_ss(0.0, 60.0, d) * (1.0 - _ss(L[-1] - 10.0, L[-1], d))
                         * np.clip((g - self.q[sel]) / 0.03, 0.0, 1.0))
            idx.append(sel)
        if not idx:
            return None
        F, Hh, A, I = (np.concatenate(x) for x in (foot, head, alpha, idx))
        cam = np.asarray(H.CAMERA.state(t).pos, np.float64)
        A = A * _ss(30.0, 90.0, np.linalg.norm(Hh - cam[None], axis=1))     # never big strokes at the lens
        keep = A > 0.01
        F, Hh, A, I = F[keep], Hh[keep], A[keep], I[keep]
        if len(I) == 0:
            return None
        C = self.col[I]
        return [dict(pos=F, pos2=Hh, size=0.30, color=C * 0.95, alpha=0.30 * A, alpha2=0.85 * A, kind="line", emit=1.5,
                     reflect=True),
                dict(pos=Hh, size=0.55, color=C * 0.85 + lin(WHITE) * 0.15, alpha=0.9 * A, kind="spark", emit=2.6,
                     twinkle=0.3, seed=self.seed[I], reflect=False),
                dict(pos=Hh[::4], size=2.6, color=C[::4] * 0.75, alpha=0.10 * A[::4], kind="soft", emit=1.2,
                     reflect=False)]


# =========================================================================================================
# The crown of light
# =========================================================================================================
class Crown:
    """The crown of light that ignites high over the city on "The glory of Jerusalem Mother shines!" (0:53.78):
    a circlet with twelve tall points, each tipped with a jewel in the nine colours, lit from the front round."""

    def __init__(self):
        r = np.random.default_rng(31)
        c = ZC + _v(0.0, SUMMIT + 122.0, -10.0)
        R = 70.0
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
        sc = np.array([1.0 + 0.43 * dn, 1.0, 1.0 + 0.43 * dn])
        off = np.array([0.0, -88.0 * dn, 0.0])
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
NEAR = dict(zion_wide=(range(0, 3), -35.0, 160.0), zion_full=(range(3, 6), 0.0, 125.0))


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


def _place_hue(P, K):
    """Round 7: the colour (index among the nine) of a place on the terraces: one calm hue per district (about
    40 degrees round the mountain) of each terrace, so the people read as broad bands of colour, not confetti."""
    az = np.arctan2(P[:, 0] - ZC[0], P[:, 2] - ZC[2])
    return (np.floor(az / np.radians(40.0) + 0.5).astype(int) * 2 + np.asarray(K, int) * 4) % 9


def _glitter_people(P, K, born, seed, gain=1.0):
    """Tiny standing figures of light: one stroke each, dim at the feet and bright at the head, so from afar
    they glitter and read as countless people. The nations stand together: each block of the terraces has its
    own colour among the nine, mixed with warm white."""
    r = np.random.default_rng(seed)
    n = len(P)
    h = r.uniform(0.9, 1.1, n)
    foot = P + np.array([0.0, 0.2, 0.0])
    head = P + np.stack([np.zeros(n), 1.6 * h, np.zeros(n)], 1)
    block = _place_hue(P, K)
    nine = np.asarray([lin(c) for c in COL9])
    j = r.random(n)
    # (round 6) the people in the nine colours, so they stand out from the pearl and glass of the city; (round 7,
    # review f23: confetti close up, white from afar) one calm colour per district of each terrace
    col = np.where((j < 0.95)[:, None], nine[block] * 0.86 + lin(WHITE) * 0.14,
                   nine[r.integers(0, 9, n)] * 0.6 + lin(WHITE) * 0.4)
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
    # round 7 (more and more people going to Zion): the first few arrive with the first rivers (1:01 to 1:10),
    # more keep coming through chorus 1 (one by one, 1:39 to 1:57), and in the coda the last terraces fill to the
    # brim (from SLAM 3, 3:21.7)
    P0, K0 = _places(range(0, 3), 0.03, 65)
    Pm, Km = _places(range(0, 6), 0.04, 66)
    P4, K4 = _places(range(0, 6), 0.06, 67)
    P = np.concatenate([P1, P1b, P2, P3, P0, Pm, P4])
    K = np.concatenate([K1, K1b, K2, K3, K0, Km, K4])
    born = np.concatenate([90.4 + 1.1 * K1 + 1.2 * r.random(len(P1)),
                           93.5 + 0.9 * (K1b - 4) + 2.0 * r.random(len(P1b)),
                           171.2 + 0.5 * (K2 - 4) + 1.0 * r.random(len(P2)),
                           170.9 + 0.45 * K3 + 1.2 * r.random(len(P3)),
                           61.5 + 2.5 * K0 + 6.0 * r.random(len(P0)),
                           99.4 + 17.0 * r.random(len(Pm)),
                           201.6 + 0.5 * K4 + 2.5 * r.random(len(P4))])
    late = np.concatenate([np.zeros(len(P1) + len(P1b) + len(P2) + len(P3), bool),
                           np.ones(len(P0) + len(Pm) + len(P4), bool)])
    return P, K, born, late


def _near(P, K, shot):
    tiers, x0, x1 = NEAR[shot]
    x = P[:, 0] - ZC[0]
    return np.isin(K, list(tiers)) & (x > x0) & (x < x1) & (P[:, 2] > ZC[2])


def nations_k(t):
    return local_k(t) if t < 254.07 else 0.0


# =========================================================================================================
# Waves of raised arms: on the slams and the hits a wave of raised arms rolls from the foot of Zion up to the
# summit, terrace by terrace (each person's arms go up as it reaches them, hold, and come down softly); in the
# waves of praise and in the coda's praise the waves come again and again on the beat, like a stadium wave.
# Each hand leaves a short trail of light as it sweeps up. Used here and by the coda (the summit) and the
# procession (the gathered nations behind her light).
# =========================================================================================================
def _beats(a, b, every=4):
    s = BEATS[(BEATS >= a - 0.01) & (BEATS < b)]
    return [float(x) for x in s[::every]]


def _arm_waves():
    """(start, seconds from the foot to the summit, hold up, strength, gesture tempo for the true figures)."""
    big = [(SLAM1, 4.4, 1.6, 1.0, 1.0), (SLAM2, 4.4, 1.6, 1.0, 1.0),
           (CODA, 2.3, 3.4, 1.0, 1.1)]                     # the coda hit's wave reaches the summit on SLAM 3
    near = [SLAM1, SLAM2, CODA, SLAM3]
    hits = [(h, 3.4, 0.9, 0.85, 1.25) for h in KICKS
            if 88.0 < h < 254.0 and min(abs(h - s) for s in near) > 1.5 and not (125.0 < h < 162.0)]
    praise = [(b, 2.8, 0.25, 0.8, 2.4) for b in _beats(86.98, 96.0, 4) + _beats(205.2, 218.0, 4)]
    return sorted(big + hits + praise)


ARM_WAVES = _arm_waves()
RISE, FALL = 0.30, 0.75            # the glitter people's arms: up quickly, down softly (seconds)


def wave_u(P):
    """How far up the mountain each place lies for the waves (0 at the foot, about 1 at the church)."""
    rr = np.hypot(P[:, 0] - ZC[0], P[:, 2] - ZC[2])
    return np.clip((tier_r(0) + 4.0 - rr) / (tier_r(0) - 16.0), 0.0, 1.05)


def _bump(x, hold):
    """A person's arms through one wave: 0 down, 1 fully raised (x: seconds since the wave reached them)."""
    up = _ss(0.0, RISE, x)
    down = _ss(RISE + hold, RISE + hold + FALL, x)
    return up * (1.0 - down)


class Arms:
    """The raised arms of the glitter people (one stroke each): two strokes of light from the shoulders that
    swing out and up as each wave reaches the person, a spark at each hand and a short trail of light behind it.
    Nothing is drawn while the arms are down, so the people look as before between the waves."""

    TRAIL, TDT = 5, 0.055

    def __init__(self, P, born, seed, gain, waves=None, u=None):
        r = np.random.default_rng(seed)
        n = len(P)
        self.h = r.uniform(0.9, 1.1, n)                  # the same heights as _glitter_people(seed)
        r2 = np.random.default_rng(seed + 500)
        self.P, self.born, self.k = P, born, gain
        az = np.arctan2(P[:, 0] - ZC[0], P[:, 2] - ZC[2])
        self.side = np.stack([np.cos(az), np.zeros(n), -np.sin(az)], 1)
        self.out = np.stack([np.sin(az), np.zeros(n), np.cos(az)], 1)
        self.u = wave_u(P) if u is None else u
        self.jit = r2.uniform(-0.08, 0.14, n)
        self.reach = r2.uniform(0.75, 1.0, n)            # not everyone lifts as high
        self.waves = ARM_WAVES if waves is None else waves
        nine = np.asarray([lin(c) for c in COL9])
        self.col = nine[r2.integers(0, 9, n)] * 0.55 + lin(WHITE) * 0.45
        self.s = r2.random(n)

    def lift(self, t, ii=None):
        ii = slice(None) if ii is None else ii
        u, jit = self.u[ii], self.jit[ii]
        out = np.zeros(len(u))
        for t0, travel, hold, s, _rt in self.waves:
            if t0 > t:
                break
            if t > t0 + travel * 1.1 + hold + RISE + FALL + 0.3:
                continue
            out = np.maximum(out, s * _bump(t - (t0 + travel * u + jit), hold))
        return out * self.reach[ii]

    def _hands(self, ii, lift):
        h = self.h[ii][:, None]
        up = np.array([0.0, 1.0, 0.0])
        sh = self.P[ii] + up * (1.36 * h)
        phi = np.radians(152.0) * lift[:, None]
        out = []
        for s in (-1.0, 1.0):
            S = sh + s * 0.19 * h * self.side[ii]
            Hd = S + 0.66 * h * (np.sin(phi) * s * 0.85 * self.side[ii] - np.sin(phi) * 0.25 * self.out[ii]
                                  - np.cos(phi) * up)
            out.append((S, Hd))
        return out

    def gain(self, t):
        return float(self.k(t))

    def sample(self, t):
        if self.k(t) <= 0.0 or not self.waves or t < self.waves[0][0]:
            return None
        lift = self.lift(t)
        ii = np.where((lift > 0.03) & (t >= self.born + 0.5))[0]
        if len(ii) == 0:
            return None
        L = lift[ii]
        a = _ss(0.03, 0.35, L)
        col = self.col[ii]
        arms = self._hands(ii, L)                 # [(shoulder, hand) left, (shoulder, hand) right]
        A = np.concatenate([a, a])
        C = np.concatenate([col, col])
        out = []
        out.append(dict(pos=np.concatenate([arms[0][0], arms[1][0]]), pos2=np.concatenate([arms[0][1], arms[1][1]]),
                        size=0.22, color=C * 0.9, alpha=0.35 * A, alpha2=0.8 * A, kind="line", emit=1.4,
                        reflect=False))
        HP = np.concatenate([arms[0][1], arms[1][1]])
        sd = np.concatenate([self.s[ii], self.s[ii]])
        out.append(dict(pos=HP, size=0.6, color=C * 0.6 + lin(GOLD2) * 0.5, alpha=A, kind="spark", emit=3.2,
                        twinkle=0.3, seed=sd, reflect=False))
        # a soft glow round the raised hands: from afar the wave reads as a band of light rolling up the mountain
        out.append(dict(pos=HP[::2], size=2.4, color=C[::2] * 0.5 + lin(GOLD2) * 0.4, alpha=0.10 * A[::2] * A[::2],
                        kind="soft", emit=1.4, reflect=False))
        # the trails: where the hands were a moment ago, fading behind them (only while the arms move)
        prev = HP
        for j in range(1, self.TRAIL + 1):
            Lj = self.lift(t - j * self.TDT, ii)
            q = self._hands(ii, Lj)
            Q = np.concatenate([q[0][1], q[1][1]])
            f = (1.0 - j / (self.TRAIL + 1.0)) ** 1.3
            mv = np.linalg.norm(Q - prev, axis=1) > 0.02
            if mv.any():
                out.append(dict(pos=prev[mv], pos2=Q[mv], size=0.3 * f + 0.08, color=C[mv] * 0.75 + lin(GOLD2) * 0.3,
                                alpha=0.75 * f * A[mv], alpha2=0.75 * f * f * A[mv], kind="line", emit=2.2,
                                reflect=False))
            prev = Q
        return out


class WaveCrowd(GCrowd):
    """True figures that raise their arms as each wave reaches them (the engine's acted gestures: from rest into
    the kind's gesture, hold it alive, back to rest), at the wave's own tempo. `delay` is each person's place
    along the wave (0..1, times the wave's travel). A wave that reaches someone still up keeps them up; one
    that reaches them while their arms are coming down passes them by (no jumps)."""

    def __init__(self, waves=None, delay=None, trails=1.0, **kw):
        kw.setdefault("act", 1e9)
        self.trails = float(trails)                 # the hands' trails of light (their width; 0: none)
        super().__init__(**kw)
        self.waves = ARM_WAVES if waves is None else waves
        self.delay = np.zeros(self.n) if delay is None else np.asarray(delay, np.float64)
        r = np.random.default_rng(int(self.seed * 1000) + 99)
        self.jit = r.uniform(-0.08, 0.16, self.n)
        self.irate0 = self.irate.copy()

    def _acts(self, t):
        n = self.n
        act, end = np.full(n, 1e9), np.full(n, 1e9)
        ir = self.irate0.copy()
        on = np.zeros(n, bool)
        from nine_reference_p3d.crowd import INTRO, OUTRO, B_BACK
        for t0, travel, hold, _s, rt in self.waves:
            if t0 > t:
                break
            if t0 < t - 40.0:
                continue
            a = t0 + travel * self.delay + self.jit
            reach = a <= t
            if not reach.any():
                continue
            irw = self.irate0 * rt
            e = a + INTRO / irw + hold
            still_up = on & (a <= end + 0.05)
            back = (~on) | (a >= end + OUTRO / ir + B_BACK)
            m_ext = reach & still_up
            m_new = reach & back & ~still_up
            end = np.where(m_ext, np.maximum(end, e), end)
            act = np.where(m_new, a, act)
            end = np.where(m_new, e, end)
            ir = np.where(m_new, irw, ir)
            on |= m_new
        return act, end, ir

    TRAIL, TDT = 5, 0.06

    def _tips(self, t, ii, acts):
        """World positions (I, 2, 3) of both hands of people ii (the body's highest points out to each side)
        and whether each is raised above the head."""
        act, end, ir = acts
        tips = np.zeros((len(ii), 2, 3))
        up = np.zeros((len(ii), 2), bool)
        for k, pr in enumerate(self.protos):
            m = self.kind[ii] == k
            if not m.any() or not pr.acted:
                continue
            jj = ii[m]
            pr.bake()
            age = np.maximum(t - self.start[jj], 0.0)
            P = pr.frames(t, age, self.rate[jj], self.phase[jj], act[jj], end[jj], ir[jj]).astype(np.float64)
            x, y = P[..., 0], P[..., 1]
            for s in (0, 1):
                sc = y + (0.45 if s else -0.45) * x
                j = np.argmax(sc, axis=1)
                q = P[np.arange(len(jj)), j]
                tips[m, s] = self._place(q[:, None, :], jj, age, pr)[:, 0]
                up[m, s] = q[:, 1] > 1.04 * pr.height
        return tips, up

    def sample(self, t):
        if self.g(t) <= 0.0:
            return []
        acts = self._acts(t)
        self.act, self.act_end, self.irate = acts
        out = super().sample(t)
        if not self.trails or not out:
            return out
        from nine_reference_p3d.crowd import OUTRO
        act, end, ir = acts
        ii = np.where((t >= act) & (t <= end + OUTRO / ir) & (t >= self.start))[0]
        if len(ii) == 0:
            return out
        tips, up = self._tips(t, ii, acts)
        hp = tips[up]
        if len(hp):
            out.append(dict(pos=hp, size=0.09 * self.trails, color=lin(GOLD2), alpha=0.9, kind="spark", emit=2.6,
                            twinkle=0.3, dof=self.dof))
        prev, pu = tips, up
        for j in range(1, self.TRAIL + 1):
            q, qu = self._tips(t - j * self.TDT, ii, acts)
            f = (1.0 - j / (self.TRAIL + 1.0)) ** 1.3
            m = pu & qu & (np.linalg.norm(q - prev, axis=2) > 0.01)
            if m.any():
                c = self.tint[ii][:, None, :].repeat(2, 1)[m] * 0.6 + lin(GOLD2) * 0.5
                out.append(dict(pos=prev[m], pos2=q[m], size=(0.07 * f + 0.02) * self.trails, color=c,
                                alpha=0.8 * f, alpha2=0.8 * f * f, kind="line", emit=2.2, dof=self.dof))
            prev, pu = q, qu
        return out


# =========================================================================================================
# Light pouring down, the column of light
# =========================================================================================================
POUR0 = 99.4          # "For Your sacrifice": light pours out of the city and down over the people


def _profile():
    """The path down the front of the mountain, from the summit's edge to the sea: (length, r, y) knots."""
    pts = [(R_TOP, SUMMIT + 2.5)]
    for k in range(N_TIER - 1, 0, -1):
        r0, y = tier_r(k), tier_y(k - 1)
        pts.append((r0 + 1.5, y + 2.5))              # down the wall (just in front of it), over the heads below
        pts.append((tier_r(k - 1), y + 2.5))         # out across the terrace
    pts.append((tier_r(0) + 1.5, 0.4))
    pts.append((tier_r(0) + 60.0, 0.4))
    pts = np.asarray(pts)
    L = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    return L, pts


def _stair_profile():
    """The same path down the great stairways (the light runs down the steps)."""
    pts = [(R_TOP - 6.0, SUMMIT + 1.5)]
    for k in range(N_TIER - 1, 0, -1):
        pts.append((tier_r(k), tier_y(k) + 1.5))
        pts.append((tier_r(k) + 14.0, tier_y(k - 1) + 1.5))
    pts.append((tier_r(0), tier_y(0) + 1.5))
    pts.append((tier_r(0) + 14.0, 1.2))
    pts.append((tier_r(0) + 60.0, 0.4))
    pts = np.asarray(pts)
    L = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    return L, pts


PROF_L, PROF_P = _profile()
STAIR_L, STAIR_P = _stair_profile()
POUR_V = 30.0                                       # how fast the front of the light runs down (m/s)


def pour_arrive(r):
    """When the pouring light reaches the people standing at radius r."""
    Lr = np.interp(-np.asarray(r, np.float64), -PROF_P[:, 0][::-1], PROF_L[::-1])
    return POUR0 + 0.6 + Lr / POUR_V


class Pour:
    """For Your sacrifice, for Your devotion (1:39.4 to 1:49.4): light pours out of the city and down Mount Zion
    like a golden waterfall, over each wall and out across each terrace, over the heads of the people, who
    shine as it reaches them, and out onto the sea. Thanks to Father (1:49.8): a column of light rises from the
    church to heaven."""

    def __init__(self):
        r = np.random.default_rng(91)
        n = 6000
        self.st = r.random(n) < 0.6                        # most of the light runs down the great stairways
        self.a = np.where(r.random(n) < 0.85, r.uniform(-1.85, 1.85, n), r.uniform(-np.pi, np.pi, n))
        self.sa = STAIRS_AZ[r.integers(0, len(STAIRS_AZ), n)]
        self.sw = r.uniform(-1.0, 1.0, n) * np.where(self.sa == 0.0, 7.5, 4.5)
        self.v = r.uniform(0.75, 1.15, n) * POUR_V
        self.o = r.random(n) * PROF_L[-1]
        self.j = r.normal(0.0, 1.0, (n, 2))
        self.s = r.random(n)
        self.c = r.random((1400, 4))

    def sample(self, t):
        if local_k(t) <= 0.0 or stage_view(t) or not (99.0 <= t < 117.0):
            return None
        out = []
        k = _env(t, POUR0 - 0.2, 110.2, 0.5, 1.8)
        if k > 0.0:
            front = (t - POUR0 - 0.2) * POUR_V
            for stair in (False, True):
                LL, PP = (STAIR_L, STAIR_P) if stair else (PROF_L, PROF_P)
                sel = self.st == stair
                L = np.mod(self.v[sel] * t + self.o[sel], LL[-1])
                on = L < front * LL[-1] / PROF_L[-1]
                if not np.any(on):
                    continue
                L, j, sd, v = L[on], self.j[sel][on], self.s[sel][on], self.v[sel][on]
                rr = np.interp(L, LL, PP[:, 0]) + (0.0 if stair else 0.8) * j[:, 0]
                yy = np.interp(L, LL, PP[:, 1]) + 0.5 * np.abs(j[:, 1])
                a = (self.sa[sel][on] + self.sw[sel][on] / rr) if stair else self.a[sel][on]
                p = np.stack([ZC[0] + rr * np.sin(a), yy, ZC[2] + rr * np.cos(a)], 1)
                r2 = np.interp(L + 1.0, LL, PP[:, 0])
                y2 = np.interp(L + 1.0, LL, PP[:, 1])
                dr, dy = r2 - np.interp(L, LL, PP[:, 0]), y2 - np.interp(L, LL, PP[:, 1])
                vel = np.stack([dr * np.sin(a), dy, dr * np.cos(a)], 1) * v[:, None] * 0.5
                lead = np.exp(-np.maximum(front * LL[-1] / PROF_L[-1] - L, 0.0) / 30.0)
                fade = 1.0 - _ss(LL[-1] - 70.0, LL[-1], L)
                out.append(dict(pos=p, vel=vel, size=0.7 if stair else 0.55, color=lin("#ffe6b4"),
                                alpha=k * (0.55 + 0.45 * lead) * fade, emit=2.2 + 1.5 * lead, kind="spark",
                                twinkle=0.5, seed=sd, reflect=False, streak=0.6))
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
            out.append(dict(pos=q, size=20.0, color=lin("#fff0d0"), alpha=0.08 * k * (ys < reach)
                            * (1.0 - 0.6 * (ys - ys[0]) / 900.0), emit=1.0, kind="soft", reflect=False))
        return out or None


def _pour_sheen():
    """The light that the pouring leaves on the mountain: the walls and a veil of light over the heads of the
    people brighten as it runs down past them (born as the light reaches them)."""
    r = np.random.default_rng(97)
    W, WB, V, VB = [], [], [], []
    for k in range(N_TIER):
        R0, y = tier_r(k), tier_y(k)
        y0 = tier_y(k - 1) if k > 0 else 0.0
        n = int(R0 * 2 * FRONT * 10.0 * 0.07)
        a = r.uniform(-FRONT, FRONT, n)
        yy = y0 + 10.0 * r.random(n) ** 0.6
        W.append(_xz(R0 + 0.3, a, yy))
        WB.append(pour_arrive(R0 - 0.01) + (y - yy) / POUR_V)
        if k < N_TIER - 1:
            Ri = tier_r(k + 1)
            m = int((R0 ** 2 - Ri ** 2) * FRONT * 0.0016)
            a = r.uniform(-FRONT, FRONT, m)
            rr = np.sqrt(Ri ** 2 + (R0 ** 2 - Ri ** 2) * r.random(m))
            V.append(_xz(rr, a, y + 2.6 + r.random(m)))
            VB.append(pour_arrive(rr))
    W, WB, V, VB = (np.concatenate(x) for x in (W, WB, V, VB))
    return [_batch(W, 2.4, lin("#fff0d0"), 0.30, kind="soft", emit=1.2, birth=WB, fade=0.5, flash=2.5, reflect=False),
            _batch(V, 7.0, lin("#ffe6bc"), 0.07, kind="soft", emit=1.0, birth=VB, fade=0.8, flash=2.0, reflect=False)]


def pour_k(t):
    """The people shine brighter while the light pours down on them."""
    return local_k(t) * (not stage_view(t)) * (99.0 <= t) * (1.0 - _sc(108.6, 110.6, t))


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
    """A pulse of light running down the parapets from the summit at each ring (the land ripples), and a ring
    of light racing UP the terraces on every big hit of the music."""
    times = [t0 + 0.12 * (N_TIER - 1 - k) for t0, _, _ in RINGS]
    fill = [FILL_T[k] + 0.45]                      # and a flash along each parapet as its terrace fills with gold
    up = [h + 0.065 * k for h in KICKS]
    return lambda t: local_k(t) * (not stage_view(t)) * min(hit_pulse(t, times, rise=0.05, fall=0.7)
                                                            + 0.8 * hit_pulse(t, fill, rise=0.05, fall=0.9)
                                                            + (0.5 + 0.5 * intensity(t))
                                                            * hit_pulse(t, up, rise=0.03, fall=0.35), 1.2)


def _downbeats():
    """Each bar's downbeat in the choruses, with its colour among the nine (as the core's bursts)."""
    out = []
    for a, b in ((82.08, 117.0), (162.86, 201.73)):
        x, k = a + 2.30, 0
        while x < b - 0.3:
            out.append((x, (k * 4) % 9))
            x += 2.30
            k += 1
    return out


DOWNBEATS = _downbeats()


def reading(t):
    """1 while a phrase reads on screen (the city calms behind it so the words keep their contrast)."""
    v = 0.0
    for _lines, (a, b, c, d), *_rest in H.PHRASE_LIST:      # (the core defines it after this file loads)
        if a - 0.5 <= t <= d + 0.5:
            v = max(v, _sc(a - 0.5, b, t) * (1.0 - _sc(c, d, t)))
    return v


def glow_k(t):
    """The mountain's light follows the music: brighter as it grows; calmer behind a phrase."""
    return local_k(t) * (0.78 + 0.32 * intensity(t)) * (1.0 - 0.28 * reading(t))


def edge_k(t):
    """The terrace edges pulse on every beat (strongly when the music is strong)."""
    return local_k(t) * (not stage_view(t)) * intensity(t) * beat_pulse(t, 0.12)


def crowd_k(t):
    """The nations breathe with the music: brighter with it, a lift on every beat."""
    return nations_k(t) * (0.75 + 0.35 * intensity(t)) * (1.0 + 0.3 * intensity(t) * beat_pulse(t, 0.12))


def _flare_k(c):
    ts = [x for x, i in DOWNBEATS if i == c]
    return lambda t: nations_k(t) * (not stage_view(t)) * hit_pulse(t, ts, rise=0.03, fall=0.45)


SHAFTS = [
    # thanks to Father (1:49.8 to 1:57): a column of light rises from the church to heaven
    dict(base=(float(CHURCH[0]), float(CHURCH[2])), radius=12.0, top=2400.0, spread=-0.2, color="#fff2d8",
         strength=lambda t: local_k(t) * (not stage_view(t)) * _env(t, 109.8, 117.0, 1.6, 0.3) * 0.05),
]


# =========================================================================================================
# The nine comets at Zion, the ray sources
# =========================================================================================================
def _prof_y(r):
    """The height of the mountain's surface at radius r (the terrace floor there)."""
    if r <= R_TOP:
        return SUMMIT
    for k in range(N_TIER - 1):
        if tier_r(k + 1) < r <= tier_r(k):
            return tier_y(k)
    return 0.0


def _spiral(i, t0, dur, turns, r0, r1, lift, sign=1.0):
    """Comet i spiralling over the mountain from radius r0 to r1 in dur seconds (lift metres over the floor)."""
    a0 = 2 * np.pi * i / 9

    def head(t):
        u = float(np.clip((t - t0) / dur, -0.3, 1.3))
        a = a0 + sign * 2 * np.pi * turns * u
        r = r0 + (r1 - r0) * min(max(u, 0.0), 1.0)
        y = _prof_y(r) + lift + 3.0 * np.sin(5.0 * u + i)
        return ZC + _v(r * np.sin(a), y, r * np.cos(a))
    return head


def _crown_ring(i):
    """Comet i circling the crown, then spiralling down round the city as it settles."""
    a0 = 2 * np.pi * i / 9

    def head(t):
        dn = _sc(61.0, 64.2, t)
        r = 96.0 + 30.0 * dn + 8.0 * np.sin(1.3 * t + i)
        y = CR[1] + 10.0 * np.sin(0.9 * t + 2 * i) - 90.0 * dn
        a = a0 + 0.9 * (t - 53.78) * (1 if i % 2 else -1)
        return ZC + _v(r * np.sin(a), y, -10.0 + r * np.cos(a))
    return head


def _stair_run(i, t0):
    """Comet i streams up a great stairway from the sea to the summit, then circles the terraces."""
    s = STAIRS_AZ[i % len(STAIRS_AZ)] + (0.0 if i < 5 else (0.35 if i % 2 else -0.35))
    dur = 2.4 + 0.25 * (i % 4)

    def head(t):
        u = (t - t0) / dur
        if u <= 1.0:
            r = tier_r(0) + 40.0 - (tier_r(0) + 40.0 - R_TOP) * max(u, -0.3)
            a = s
        else:
            r = R_TOP + 20.0 + 30.0 * (i % 5)
            a = s + 0.55 * (t - t0 - dur) * (1 if i % 2 else -1)
        return ZC + _v(r * np.sin(a), _prof_y(r) + 4.0, r * np.cos(a))
    return head


def _race_out(i, t0, v):
    """Comet i races out over the sea from the foot of Zion with the rings."""
    a = 2 * np.pi * (i + 0.5) / 9 * 0.5 - np.pi * 0.5 + 0.2      # spread over the seen side

    def head(t):
        r = tier_r(0) + v * max(t - t0, -0.5) + 4.0 * np.sin(3.0 * t + i)
        return ZC + _v(r * np.sin(a), 3.0 + 2.0 * np.sin(2.0 * t + i), r * np.cos(a))
    return head


def _race_lane(i):
    """Comet i streaks low over the sea down the canyon of cloud, toward the camera and past it."""
    x = -70.0 + 140.0 * (i + 0.5) / 9

    def head(t):
        z = 300.0 + 260.0 * (t - 86.7) + 140.0 * i
        z = 300.0 + np.mod(z - 300.0, 1100.0)
        return ZC + _v(x + 6.0 * np.sin(2.0 * t + i), 2.0 + 1.5 * np.sin(3.0 * t + i), z)
    return head


def _pour_down(i):
    """Comet i pours down from heaven onto the terraces, again and again (sacrifice, devotion)."""
    a = np.radians(-70.0 + 140.0 * i / 8)

    def head(t):
        ph = np.mod(t * 0.42 + i * 0.37, 1.0)
        land = ZC + _v(tier_r(1 + i % 4) * 0.95 * np.sin(a), 0.0, tier_r(1 + i % 4) * 0.95 * np.cos(a))
        land[1] = _prof_y(tier_r(1 + i % 4) * 0.95) + 3.0
        top = land + _v(-60.0, 520.0, -120.0)
        return top + (land - top) * ph ** 1.6
    return head


def _column(i):
    """Comet i spirals up round the column of light to heaven."""
    a0 = 2 * np.pi * i / 9

    def head(t):
        u = t - 109.8
        y = SUMMIT + 20.0 + 70.0 * max(u, -0.3) + 30.0 * i
        r = 22.0 + 6.0 * np.sin(0.7 * u + i)
        a = a0 + 2.2 * u
        return CHURCH + _v(r * np.sin(a), y - CHURCH[1], r * np.cos(a))
    return head


def _fan(i):
    """Comet i bursts out of the blazing crown, fanning out and arcing down over the night."""
    a = 2 * np.pi * i / 9 + 0.3
    d = _v(np.sin(a), 0.35 + 0.25 * (i % 3), np.cos(a))

    def head(t):
        u = max(t - 53.78, -0.2)
        return CR + d * 140.0 * u + _v(0.0, -18.0 * u * u, 0.0)
    return head


def _comets():
    out = []
    plan = [  # (t0, t1, head maker, trail, width)
        (53.78, 56.4, lambda i: _fan(i), 0.9, 3.0),
        (55.6, 64.4, lambda i: _crown_ring(i), 1.0, 2.0),
        (64.2, 70.54, lambda i: _stair_run(i, 64.2 + 0.18 * i), 1.1, 2.8),
        (86.7, 90.72, lambda i: _race_lane(i), 0.8, 2.0),
        (90.72, 99.2, lambda i: _spiral(i, 90.72, 7.5, 2.2, tier_r(0) + 20.0, R_TOP, 10.0), 1.3, 3.0),
        (99.4, 109.6, lambda i: _pour_down(i), 0.9, 2.6),
        (109.8, 117.0, lambda i: _column(i), 1.4, 3.0),
        (165.16, 171.48, lambda i: _race_out(i, 165.16 + 0.1 * i, 70.0), 1.4, 3.0),
        (171.48, 183.5, lambda i: _spiral(i, 171.48, 9.0, 3.0, tier_r(0) + 30.0, R_TOP + 10.0, 18.0, -1.0), 1.3, 3.2),
    ]
    for si, (t0, t1, mk, tr, w) in enumerate(plan):
        for i in range(9):
            out.append((f"comet {si} {i}", Comet(mk(i), COL9[i], t0, t1, trail=tr, width=w, bright=1.1, fade=0.4,
                                                 light=(i in (0, 4)), n=60, seed=si * 9 + i)))
    return out


def _rays():
    """The great lights of Zion's moments (only the strongest ray source in the film shows at a time)."""
    def crown_pos(t):
        dn = _sc(61.0, 64.2, t)
        return CR + _v(0.0, 20.0 - 90.0 * dn, 0.0)
    add_rays(crown_pos, lambda t: local_k(t) * (not stage_view(t)) * _env(t, 53.78, 70.4, 0.25, 1.0)
             * (0.75 + 0.5 * hit_pulse(t, [53.78, 64.2, 65.94, 69.4], fall=0.6)), color="#ffe9c4", size=30.0)
    add_rays(lambda t: ZC + _v(-60.0, 520.0, -120.0) + _v(0.0, 0.0, 0.0),
             lambda t: local_k(t) * (not stage_view(t)) * _env(t, 99.4, 109.4, 0.6, 1.0)
             * (0.35 + 0.2 * intensity(t) + 0.3 * hit_pulse(t, KICKS, fall=0.5)), color="#fff0d4", size=40.0)
    add_rays(lambda t: CHURCH + _v(0.0, 80.0 + 200.0 * _sc(109.8, 112.0, t), 0.0),
             lambda t: local_k(t) * (not stage_view(t)) * _env(t, 109.8, 117.0, 0.5, 0.5)
             * (1.0 + 0.4 * hit_pulse(t, KICKS, fall=0.5)), color="#fff4e0", size=50.0)
    add_rays(lambda t: ZC + _v(0.0, SUMMIT + 60.0, 0.0),
             lambda t: local_k(t) * (not stage_view(t)) * _env(t, 180.7, 183.4, 0.4, 0.6)
             * (0.35 + 0.2 * intensity(t)), color="#ffe6c0", size=40.0)


_rays()


def _grand(scene):
    """The promo's grand scenes at Zion: a canyon of cloud over the sea for the waves of praise, pillars of
    light falling from clouds onto the terraces (sacrifice, devotion), the column to heaven as the grandest
    pillar with clouds parting round it."""
    def win(a, b, fi=0.6, fo=0.6):
        return lambda t: local_k(t) * (not stage_view(t)) * _env(t, a, b, fi, fo)
    for i, x in enumerate((-150.0, 150.0)):
        scene.add(f"zion canyon {i}", CloudBank(ZC + _v(x, 0.0, 900.0), size=(90.0, 190.0, 900.0), puffs=90,
                                                seed=40 + i, gain=win(86.4, 90.9, 0.3, 0.3), bright=0.55),
                  reflect=True)
    k_pour = win(99.2, 109.8, 0.8, 1.0)
    for i, x in enumerate((-230.0, 230.0)):
        scene.add(f"zion pour clouds {i}", CloudBank(ZC + _v(x, 300.0, 120.0), size=(260.0, 80.0, 220.0), puffs=24,
                                                     seed=44 + i, gain=k_pour, bright=0.6), reflect=False)
    bases = []
    for a, k in zip((-72.0, -58.0, -44.0, -32.0, 32.0, 44.0, 58.0, 72.0), (1, 2, 0, 3, 3, 1, 2, 0)):
        rr = 0.5 * (tier_r(k) + tier_r(k + 1))
        bases.append((ZC[0] + rr * np.sin(np.radians(a)), ZC[2] + rr * np.cos(np.radians(a))))
    scene.add("zion pillars", Pillars(bases, top=300.0, color="#ffe4bc", width=4.5,
                                      gain=lambda t: k_pour(t) * (0.45 + 0.25 * intensity(t))), reflect=False)
    k_col = win(109.8, 117.0, 0.8, 0.3)
    scene.add("zion column", Pillars([(float(CHURCH[0]), float(CHURCH[2]))], top=1400.0, color="#fff4e2", width=12.0,
                                     gain=lambda t: k_col(t) * _sc(109.8, 111.0, t) * 1.2), reflect=False)
    for i, (x, z) in enumerate(((60.0, -330.0), (260.0, 40.0), (-150.0, -260.0), (140.0, -240.0))):
        scene.add(f"zion heaven {i}", CloudBank(CHURCH + _v(x, 340.0 - CHURCH[1], z), size=(300.0, 90.0, 220.0),
                                                puffs=30, seed=50 + i, gain=k_col, bright=1.0), reflect=False)


def add(scene):
    walls, dim, gold = _mountain()
    scene.add("zion body", _Off(_body()), mask=Mask("dark", strength=body_k, grow=1.9, soft=4.0), reflect=False)
    scene.add("zion walls", Static(walls, lambda t: glow_k(t) * form_k(t)))
    scene.add("zion dim", Static(dim, glow_k))
    scene.add("zion gold", Static(gold, glow_k))
    # round 6: the city grows section by section, and the rivers of people stream to it
    gates, gardens, towers, mist = _city_parts()
    calm = (lambda t: glow_k(t) * (1.0 - 0.25 * reading(t)))
    scene.add("zion gates", Static(gates, calm))
    scene.add("zion gardens", Static(gardens, calm))
    scene.add("zion towers", Static(towers, lambda t: calm(t) * (1.0 + 0.25 * intensity(t) * beat_pulse(t, 0.12))))
    scene.add("zion mist", Static(mist, lambda t: local_k(t) * (0.7 + 0.5 * intensity(t))))
    scene.add("zion streams", Streams())
    edges = np.concatenate([_ring(ZC, tier_r(k) + 0.1, tier_y(k) + 1.0, 1.4) for k in range(N_TIER)])
    scene.add("zion beat", Static([_batch(edges, 0.6, lin("#ffe8c0"), 0.8, emit=1.8, reflect=False)], edge_k))
    for k in range(N_TIER):
        ring = _ring(ZC, tier_r(k) + 0.1, tier_y(k) + 0.9, 1.0)
        scene.add(f"zion ripple {k}", Static([_batch(ring, 0.9, lin("#fff0d0"), 1.0, emit=2.5, reflect=False)],
                                             _ripple_k(k)))
    scene.add("crown", Crown())
    # the nations on Mount Zion: a glitter of countless people; true figures where the camera climbs past them
    P, K, born, late = _nations()
    nw, nf = _near(P, K, "zion_wide") & ~late, _near(P, K, "zion_full") & ~late
    rest = ~(nw | nf)
    scene.add("nations", Static(_glitter_people(P[rest], K[rest], born[rest], 3), crowd_k))
    na = Arms(P[rest], born[rest], 3, crowd_k)                            # the waves of raised arms
    na.col = np.asarray([lin(c) for c in COL9])[_place_hue(P[rest], K[rest])] * 0.6 + lin(WHITE) * 0.4
    scene.add("nations arms", na)
    # on each downbeat of the choruses the nations' lights flare in one of the nine colours (one set a colour)
    rf = np.random.default_rng(13)
    pick = np.where(rf.random(len(P)) < 0.2)[0]
    heads = P[pick] + np.array([0.0, 1.7, 0.0])
    for c in range(9):
        sel = pick % 9 == c
        scene.add(f"nations flare {c}", Static([_batch(heads[sel], 0.7, lin(COL9[c]) * 0.7 + lin(WHITE) * 0.3, 0.9,
                                                       emit=2.6, birth=born[pick][sel], twinkle=0.4, reflect=False)],
                                               _flare_k(c)))
    arrive = np.maximum(born, pour_arrive(np.hypot(P[:, 0] - ZC[0], P[:, 2] - ZC[2])))
    scene.add("nations lit", Static(_glitter_people(P[rest], K[rest], arrive[rest], 3, 0.6), pour_k))
    rng = np.random.default_rng(9)
    for shot, sel, seed, t_on in (("zion_wide", nw & ~nf, 4, 90.0), ("zion_full", nf, 5, 175.0)):
        on = (lambda s, a: (lambda t: float(shot_name(t) == s) * _sc(a, a + 1.5, t)))(shot, t_on)
        mid_k = (lambda f: (lambda t: crowd_k(t) * (1.0 - f(t))))(on)
        scene.add(f"nations mid {shot}", Static(_glitter_people(P[sel], K[sel], born[sel], seed), mid_k))
        scene.add(f"nations mid arms {shot}", Arms(P[sel], born[sel], seed, mid_k))
        i = np.where(sel)[0]
        i = i[rng.random(len(i)) < 0.26]
        crowd = WaveCrowd(
            delay=wave_u(P[i]), gain=(lambda f: (lambda t: nations_k(t) * f(t)))(on), places=P[i],
            facing=lambda x, z: float(np.degrees(np.arctan2(ZC[0] - x, ZC[2] - z))),
            kinds=(("raise", 3.0), ("open", 1.0), ("stand", 0.6)),
            people=dict(woman=1.0, man=1.0, elder=0.2, child=0.15), start=born[i], color="#ffcf7a",
            color2="#fff0d0", bright=1.35, points=48, size=10.5, flash=1.5, seed=float(seed))
        # (round 6) each true figure in one of the nine colours (they stood gold against gold before)
        nine = np.asarray([lin(c) for c in COL9])
        crowd.tint = nine[_place_hue(P[i], K[i])] * 0.8 + lin(WHITE) * 0.2     # (round 7) by district
        scene.add(f"nations near {shot}", crowd)
    for name, c in _comets():
        scene.add(name, c, reflect=False)
    _grand(scene)
    scene.add("pour", Pour())
    scene.add("pour sheen", Static(_pour_sheen(), pour_k))
    scene.add("rings", Rings())
