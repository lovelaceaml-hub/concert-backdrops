"""Song 11 v2: Mother as light alone leading everyone across the sea of glass toward Zion (2:05.9),
the march (2:14.54), hearts lighting in the walkers on fulfilled, the kings laying down their crowns, the held
breath before the second slam.

Owned by the procession thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below, one per block of the core's music-video EDIT that this thread owns (owner
"proc"), each with that block's exact t0 and t1 and its own angle. Point sets: add(scene). The scene follows
the music: brightness with intensity(t), a pulse on the beat, ripples of colour on the hits, flares on hits.
No em dash or en dash anywhere in this file.

The story (125.92 to 162.3, with cut-ins of the church and the choir owned by other threads):
  125.92  a light comes down out of the sky onto the sea of glass ahead of everyone (Mother, light alone)
  127.64  it touches the sea (the third strings pulse): a ring of light runs out over the sea, and people of
          light gather behind it from every side (sparks fly in and become people)
  134.54  "march ahead": everyone steps out together behind her light toward Mount Zion
  144.4   "fulfilled": hearts light up in every person, a wave from her light back through the procession
  148.6   kings in gold walk in the aisle, crowns of light on their heads
  154.2   the kings kneel and lay their crowns down; 155.34 the crowns rise as sparks toward Zion
  156.0   the held breath: everyone stands still, the light gathers to her, then the slam cuts away
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
from songs.s11_zion import WaveCrowd  # noqa: E402  (the waves of raised arms)

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

T0, T1 = 125.92, 162.3
LAND = STRINGS[2]          # 127.64: the light touches the sea on the third strings pulse
MARCH = HIT["march"]       # 134.54: everyone steps out together
HALT = DROP2               # 156.0: the held breath, everyone stands still
MOTHER_Z0 = -55.0          # where Mother's light comes down on the sea, ahead of everyone
M_H = 4.2                  # how high her light rides over the sea
WALK = 1.3                 # metres per second toward Zion, from "march ahead"
AISLE = 4.0                # the aisle down the middle (the kings walk and kneel in it)
KNEEL = HIT["kings1"]      # 154.2
RISE = HIT["kings2"]       # 155.34
K_STOP = KNEEL - 0.05      # the kings stop walking and go down
K_IN = 148.6               # the kings appear in the aisle
LAY0, LAY1 = 154.75, 155.28   # the crowns go from the heads down onto the sea before the kings
KINGS_STOP = np.asarray([(-2.55, 0.0, -66.0), (-0.85, 0.0, -66.3), (0.85, 0.0, -66.3), (2.55, 0.0, -66.0),
                         (-1.7, 0.0, -64.1), (0.0, 0.0, -64.3), (1.7, 0.0, -64.1)])
KINGS_P = KINGS_STOP + _v(0.0, 0.0, WALK * (K_STOP - K_IN))


def walked(t):
    """How far everyone has walked at t (metres)."""
    return WALK * float(np.clip(t - MARCH, 0.0, HALT - MARCH))


def mother_pos(t):
    e = float(np.clip((t - T0) / (LAND - T0), 0.0, 1.0))
    d = (1.0 - e) ** 2                                  # comes down fast, settles gently
    y = M_H + 72.0 * d + 0.18 * np.sin(1.3 * t) * e
    return _v(0.0, y, MOTHER_Z0 - 22.0 * d - walked(t))


def _kings_front(t):
    """z of the kings' front row while they walk (they stop at K_STOP)."""
    return float(KINGS_STOP[0, 2] + WALK * max(K_STOP - t, 0.0))


def _track(t0, t1, n, f):
    """Keys every (t1 - t0) / n seconds from f(t) -> (pos, target)."""
    out = []
    for t in np.linspace(t0, t1, n + 1):
        p, q = f(float(t))
        out.append((float(t), _v(*p), _v(*q)))
    return out


def _lin(t0, t1, p0, q0, p1, q1, mid=None):
    k = [(t0, _v(*p0), _v(*q0))]
    if mid is not None:
        k.append((mid[0], _v(*mid[1]), _v(*mid[2])))
    return k + [(t1, _v(*p1), _v(*q1))]


def _mz(t):
    return float(mother_pos(t)[2])


# One flight per block of the edit (core EDIT, owner "proc"): (t0: keys, pace)
def _plan(t0, t1):
    K = lambda *k: [(t, _v(*p), _v(*q)) for t, p, q in k]       # noqa: E731
    if t0 == 125.92:      # follow her light down out of the sky; as it touches the sea, sweep round it
        k = _track(t0, LAND, 5, lambda t: ((11.0 - 1.8 * (t - t0), 2.6 - 0.2 * (t - t0), -20.0 - 3.5 * (t - t0)),
                                           tuple(mother_pos(t) + _v(0.0, -1.5, 0.0))))
        return k + K((128.6, (16.0, 3.0, -30.0), (0.0, 14.0, -55.0)), (129.5, (22.0, 5.0, -34.0), (0.0, 18.0, -52.0)),
                     (t1, (30.0, 9.0, -38.0), (0.0, 8.0, -48.0))), "linear"
    if t0 == 130.29:      # trust Father: an orbit from the side round to the front, high, the comets circling
        return K((t0, (40.0, 14.0, -30.0), (0.0, 2.0, -35.0)), (131.8, (34.0, 18.0, -62.0), (0.0, 2.0, -35.0)),
                 (133.2, (14.0, 17.0, -78.0), (0.0, 1.0, -32.0)), (t1, (5.0, 16.0, -76.0), (0.0, 1.0, -28.0))), "music"
    if t0 == 134.54:      # march ahead: a crane up from low in front as everyone steps out toward us
        return K((t0, (0.6, 4.2, 40.0), (0.0, 4.0, -80.0)), (135.0, (0.3, 3.8, 12.0), (-1.0, 3.5, -100.0)),
                 (135.6, (0.0, 12.0, -6.0), (0.0, -6.0, -50.0)), (136.6, (2.0, 30.0, -6.0), (-4.5, 0.0, -36.0)),
                 (t1, (0.0, 33.0, -12.0), (-5.0, 0.0, -40.0))), "music"
    if t0 == 141.5:       # among the walkers, chasing the comets weaving through them
        return _track(t0, t1, 4, lambda t: ((-2.2, 3.2, -36.5 - walked(t) - 0.6 * (t - t0)),
                                            (9.0, 0.9, -44.0 - walked(t) - 0.6 * (t - t0)))), "music"
    if t0 == 144.4:       # fulfilled: the comets dive through the walkers toward us, lighting hearts; we rise
        return _track(t0, t1, 4, lambda t: ((-5.0 - 1.7 * (t - t0), 8.0 + 2.9 * (t - t0), _mz(t) + 58.0 + 3.8 * (t - t0)),
                                            (0.0, 1.0, _mz(t) + 14.0 + 2.4 * (t - t0)))), "music"
    if t0 == 148.6:       # the kings from in front, rising and swinging over them to behind for the words
        kf = _kings_front
        return K((t0, (0.6, 3.4, kf(t0) - 7.5), (0.0, 0.7, kf(t0) + 2.0)), (149.8, (3.5, 6.0, -70.0), (0.0, 1.0, -60.0)),
                 (150.9, (9.0, 14.0, -62.0), (-1.0, 0.0, -66.0)), (152.2, (3.5, 17.5, -50.5), (-4.0, -6.5, -76.5)),
                 (t1, (1.0, 17.0, -53.0), (-4.5, -7.0, -78.0))), "music"
    if t0 == 154.2:       # the kings kneel; we look up after the crowns as they rise toward Zion
        return K((t0, (6.0, 4.5, -71.0), (0.0, 0.8, -65.0)), (155.0, (5.0, 3.0, -70.0), (0.0, 1.5, -66.0)),
                 (155.6, (4.5, 1.2, -69.0), (0.0, 3.0, -68.5)), (t1, (4.5, 1.0, -69.0), (0.0, 4.5, -69.0))), "music"
    if t0 == 156.0:       # the held breath: a slow tense push; the comets drawn back into her light
        return K((t0, (4.0, 1.4, -77.0), (0.0, 30.0, -86.0)), (158.3, (3.6, 1.3, -77.5), (0.0, 32.0, -85.0)),
                 (159.4, (3.4, 1.4, -77.6), (0.0, 30.0, -84.0)), (160.1, (3.6, 3.0, -74.5), (0.0, 7.0, -83.0)),
                 (t1, (2.8, 3.6, -72.0), (0.0, 4.5, -83.0))), "music"
    if t0 == 161.7:       # her light grows: a push in toward it, faster into the slam
        return K((t0, (1.6, 3.4, -93.0), (0.0, 8.0, -70.0)), (t1, (0.8, 3.9, -90.0), (0.0, 6.5, -70.0))), "music"
    raise ValueError(f"no procession shot planned for the block at {t0}")


# banking: the horizon tilts in the big turns and the racing flight (degrees)
ROLL = {125.92: lambda t: -6.0 * _sc(127.4, 128.6, t) * (1.0 - _sc(129.4, 130.29, t)),
        130.29: lambda t: 9.0 * np.sin(np.pi * _sc(130.29, 134.54, t)),
        134.54: lambda t: 12.0 * np.sin(2.0 * np.pi * _sc(134.54, 135.6, t)) * (1.0 - _sc(135.3, 135.9, t)),
        141.5: lambda t: 4.0 * np.sin(1.3 * (t - 141.5)),
        144.4: lambda t: -7.0 * np.sin(np.pi * _sc(144.4, 148.6, t)),
        148.6: lambda t: 8.0 * np.sin(np.pi * _sc(149.0, 151.3, t))}


def _shots():
    out = []
    for t0, t1, note in blocks_of("proc"):
        keys, pace = _plan(t0, t1)
        out.append(dict(name="procession", kind="local", t0=t0, t1=t1, fov=50.0, aperture=0.0, keys=keys,
                        pace=pace, note=note, roll=ROLL.get(t0, 0.0)))
    return out


SHOTS = _shots()
MY_T0 = [s["t0"] for s in SHOTS]


def block_t0(t):
    """The start of the procession block at t (or None)."""
    i = int(np.searchsorted(MY_T0, t, side="right")) - 1
    return MY_T0[i] if i >= 0 and t < SHOTS[i]["t1"] else None


def proc_k(t):
    return local_k(t) if block_t0(t) is not None and shot_name(t) == "procession" else 0.0


def shaft_k(t):
    """Her shaft shows in the views along the sea (not from above, where its mirror image would cross the
    words, nor looking up past her)."""
    return 1.0 if block_t0(t) in (125.92, 130.29, 141.5, 144.4) else 0.0


def mirror_k(t):
    """Her mirror image in the sea shows except in the views from high behind (it would sit in the words)."""
    return 0.0 if block_t0(t) in (134.54, 148.6, 154.2, 156.0) else 1.0


def glow(t):
    """How bright the scene burns with the music: intensity, a soft pulse on the beat (not in the held breath)."""
    held = _sc(HALT, HALT + 0.6, t)
    return (0.75 + 0.4 * intensity(t)) * (1.0 + 0.16 * (1.0 - held) * beat_pulse(t))


def crowd_k(t):
    return proc_k(t) * glow(t)


# ---------------------------------------------------------------------------------------------------------
# Where everyone walks: rows behind her light, fanning out, an aisle down the middle
# ---------------------------------------------------------------------------------------------------------
def _proc_places(seed=51):
    r = np.random.default_rng(seed)
    out = []
    z, row = MOTHER_Z0 + 5.0, 0
    while z < MOTHER_Z0 + 100.0:
        u = (z - MOTHER_Z0) / 100.0
        half = 7.5 + 19.0 * u ** 0.8
        xs = np.arange(AISLE, half, 1.75) + 0.85 * (row % 2)
        for s in (-1.0, 1.0):
            x = s * (xs + r.uniform(-0.3, 0.3, len(xs)))
            zz = z + r.uniform(-0.45, 0.45, len(xs))
            keep = r.random(len(xs)) > 0.12 + 0.25 * (np.abs(x) > half - 3.0)     # ragged edges
            out.append(np.stack([x, np.zeros(len(xs)), zz], 1)[keep])
        z += 1.9
        row += 1
    return np.concatenate(out)


PROC_P = _proc_places()
_R0 = np.random.default_rng(52)
_D0 = np.hypot(PROC_P[:, 0], PROC_P[:, 2] - MOTHER_Z0)
ARRIVE = LAND + 0.5 + 2.6 * (_D0 / _D0.max()) ** 0.85 + _R0.uniform(0.0, 0.6, len(PROC_P))


def _ahead(crowd):
    """Unit walking directions of a crowd's people (their facing, jitter included)."""
    f = crowd.facing
    return np.stack([np.sin(f), np.zeros(len(f)), np.cos(f)], 1)


def _points_of(crowd, t, ii=None):
    """The world points (I, P, 3) of people ii of a crowd at t (all of one prototype)."""
    ii = np.arange(crowd.n) if ii is None else np.asarray(ii)
    pr = crowd.protos[crowd.kind[ii[0]]]
    pr.bake()
    age = np.maximum(t - crowd.start[ii], 0.0)
    P = pr.frames(t, age, crowd.rate[ii], crowd.phase[ii], crowd.act[ii], crowd.act_end[ii],
                  crowd.irate[ii]).astype(np.float64)
    return crowd._place(P, ii, age, pr)


# ---------------------------------------------------------------------------------------------------------
# Mother as light alone
# ---------------------------------------------------------------------------------------------------------
def gather_k(t):
    """The light gathering to her in the held breath (0 to 1 just before the slam)."""
    return _sc(157.5, 162.3, t) ** 1.6


class MotherLight:
    """Mother as light alone (never a figure): a light that comes down out of the sky onto the sea, a ring of
    light running out from where it touches, a pool of light on the sea under it, and it leads everyone. It
    flares on every hit; close to the camera its glow is held small so it never whites out the frame."""
    wants_camera = True

    def __init__(self):
        r = np.random.default_rng(61)
        self.s = r.random((420, 4))
        a = np.linspace(0, 2 * np.pi, 1400, endpoint=False)
        self.cs = np.stack([np.sin(a), np.cos(a)], 1)
        self.rs = r.random(1400)

    def sample(self, t, cam=None):
        k = proc_k(t) * (0.8 + 0.3 * intensity(t))
        if k <= 0.0:
            return None
        m = mother_pos(t)
        hits = KICKS + FULFIL
        held = _sc(HALT, HALT + 1.0, t)
        g = gather_k(t)
        pulse = (1.0 + 0.8 * hit_pulse(t, hits, fall=0.6) + 0.12 * (1.0 - held) * beat_pulse(t)
                 + 0.08 * held * np.sin(2.0 * np.pi * 0.45 * t) + 1.0 * g)
        s = self.s
        ang = 2 * np.pi * s[:, 0] + 0.35 * t * (0.5 + s[:, 1])
        rad = (1.2 + 3.4 * s[:, 2]) * (1.0 - 0.45 * g)
        halo = m[None, :] + np.stack([rad * np.cos(ang), 1.3 * (s[:, 3] - 0.5) * rad, rad * np.sin(ang)], 1)
        warm = lin("#ffe2b4")
        big = 1.0 + 1.2 * (1.0 - _sc(LAND - 0.6, LAND + 0.4, t))       # coming down she is a blazing star
        out = [dict(pos=m[None, :], size=(20.0 + 6.0 * g) * big, color=warm, alpha=0.06 * k * pulse, kind="soft", emit=1.5),
               dict(pos=m[None, :], size=10.0, color=lin("#ffe8c8"), alpha=0.28 * k * pulse, kind="soft", emit=2.0),
               dict(pos=m[None, :], size=3.2, color=lin(WHITE), alpha=0.95 * k, kind="soft", emit=4.0 * pulse),
               dict(pos=m[None, :], size=0.45, color=lin(WHITE), alpha=k, kind="spark", emit=7.0 * pulse),
               dict(pos=halo, size=0.07, color=lin("#ffe6b8"), alpha=0.75 * k, kind="spark", emit=2.6, twinkle=0.8,
                    seed=s[:, 0])]
        near = 1.0 if cam is None else float(np.clip(np.linalg.norm(m - np.asarray(cam.pos)) / 30.0, 0.3, 1.0))
        out[0]["size"] *= near
        out[1]["size"] *= big * near
        out[2]["size"] *= big * near
        # her mirror image in the sea, only in the views along the sea (from high above it would sit in the words)
        rk = mirror_k(t)
        if rk > 0.0:
            for b in out[:4]:
                r = dict(b)
                r["pos"] = b["pos"] * _v(1.0, -1.0, 1.0)[None, :]
                r["alpha"] = b["alpha"] * 0.3 * rk
                out.append(r)
        # coming down: a trail of light behind it
        if t < LAND + 0.4:
            back = np.linspace(0.02, 1.2, 90)
            P = np.stack([mother_pos(t - b) for b in back])
            a = np.exp(-back / 0.45) * (1.0 - _sc(LAND - 0.1, LAND + 0.4, t))
            out.append(dict(pos=P, size=1.2 * (1.0 - 0.6 * back), color=lin("#fff0d8"), alpha=0.7 * k * a,
                            kind="soft", emit=2.5))
            out.append(dict(pos=P, size=0.12, color=lin(WHITE), alpha=k * a, kind="spark", emit=4.0))
        for b in out:
            b["reflect"] = False
        # touching the sea: rings of light run out over it (the people gather inside them)
        for t0, v, a0 in ((LAND, 16.0, 0.9), (LAND + 0.55, 11.0, 0.5)):
            u = t - t0
            if 0.0 <= u < 5.0:
                rr = 1.0 + v * u
                p = np.stack([self.cs[:, 0] * rr, np.full(len(self.cs), 0.08), MOTHER_Z0 + self.cs[:, 1] * rr], 1)
                a = a0 * np.exp(-u / 1.4) * _sc(0.0, 0.08, u) * k
                out.append(dict(pos=p, size=0.22 + 0.04 * u, color=lin("#ffe4b8"), alpha=a, emit=2.4, kind="spark",
                                twinkle=0.4, seed=self.rs, reflect=False))
        # a pool of light on the sea under her
        if t > LAND - 0.3:
            a = _sc(LAND - 0.3, LAND + 0.3, t) * k
            out.append(dict(pos=_v(m[0], 0.06, m[2])[None, :], size=7.0, color=warm, alpha=0.16 * a * pulse,
                            kind="soft", emit=1.6, reflect=False))
        return out


class Gather:
    """People of light gathering behind her light from every side: a spark flies in for each person and
    becomes them (each person appears as their spark arrives)."""

    def __init__(self):
        r = np.random.default_rng(62)
        n = len(PROC_P)
        d = PROC_P - _v(0.0, 0.0, MOTHER_Z0)[None, :]
        out = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
        side = np.stack([np.sign(PROC_P[:, 0]), np.zeros(n), np.zeros(n)], 1)
        dirn = 0.55 * out + 0.45 * side + 0.35 * np.stack([r.normal(0, 1, n), np.zeros(n), r.normal(0, 1, n)], 1)
        dirn = dirn / np.maximum(np.linalg.norm(dirn, axis=1, keepdims=True), 1e-6)
        self.end = PROC_P + _v(0.0, 1.1, 0.0)
        self.beg = self.end + dirn * r.uniform(22.0, 55.0, n)[:, None] + np.stack(
            [np.zeros(n), r.uniform(2.0, 9.0, n), np.zeros(n)], 1)
        self.mid = 0.5 * (self.beg + self.end) + np.stack([np.zeros(n), r.uniform(3.0, 8.0, n), np.zeros(n)], 1)
        self.dur = r.uniform(1.3, 2.0, n)
        self.t1 = ARRIVE
        self.seed = r.random(n)

    def _at(self, u):
        u = u[:, None]
        return (1 - u) ** 2 * self.beg[self.on] + 2 * u * (1 - u) * self.mid[self.on] + u * u * self.end[self.on]

    def sample(self, t):
        if proc_k(t) <= 0.0 or t > ARRIVE.max() + 0.2:
            return None
        u = (t - (self.t1 - self.dur)) / self.dur
        self.on = (u > 0.0) & (u < 1.0)
        if not self.on.any():
            return None
        uu = u[self.on]
        e = 1.0 - (1.0 - uu) ** 1.6
        p = self._at(e)
        q = self._at(np.maximum(e - 0.07, 0.0))
        a = _sc(0.0, 0.15, uu) * (0.6 + 0.8 * uu)
        col = lin("#fff0d6")
        return [dict(pos=p, pos2=q, size=0.10, color=col, alpha=0.6 * a, emit=2.4, kind="line", reflect=False),
                dict(pos=p, size=1.2, color=col, alpha=0.25 * a, emit=1.8, kind="soft", reflect=False),
                dict(pos=p, size=0.35, color=col, alpha=a, emit=3.4, kind="spark", seed=self.seed[self.on])]


# ---------------------------------------------------------------------------------------------------------
# The nine comets: they come out of her light as it touches the sea and lead everyone toward Zion
# ---------------------------------------------------------------------------------------------------------
_order = np.argsort(PROC_P[:, 0])
LANE = np.zeros(len(PROC_P), int)
LANE[_order] = np.minimum((np.arange(len(PROC_P)) * 9) // len(PROC_P), 8)
LANE_X = np.array([np.median(PROC_P[LANE == j, 0]) for j in range(9)])
DIVE_V = 40.0                                                   # metres per second back through the procession
DIVE_T = np.array([(144.4, 145.0)[j % 2] + 0.12 * j for j in range(9)])
ZREL = PROC_P[:, 2] - MOTHER_Z0                                 # each person's place behind her light


def _kz(t):
    """The middle of the kings (z)."""
    return float(KINGS_STOP[:, 2].mean() + WALK * max(K_STOP - t, 0.0))


def _comet_head(j, phase):
    a0 = 2.0 * np.pi * j / 9.0

    def burst(t):            # 127.64: they shoot up out of the sea round her light, then fan out over everyone
        u = max(t - LAND, 0.0)
        r = 7.0 + 26.0 * (1.0 - np.exp(-max(u - 0.6, 0.0) / 1.0))
        cz = MOTHER_Z0 + 20.0 * (1.0 - np.exp(-max(u - 0.6, 0.0) / 1.5))
        a = a0 + 0.5 * max(u - 0.6, 0.0)
        up = 46.0 * (1.0 - np.exp(-u / 0.45)) * np.exp(-max(u - 0.9, 0.0) / 0.9)
        y = -0.6 + up + 8.0 * (1.0 - np.exp(-max(u - 0.6, 0.0) / 1.2)) + 1.2 * np.sin(1.7 * u + j)
        return _v(r * np.sin(a), y, cz + r * np.cos(a))

    def ring(t):             # trust Father: a ring of comets over the gathered people
        a = a0 + 0.5 * t
        r = 26.0 + 4.0 * np.sin(0.8 * t + j)
        return _v(r * np.sin(a), 7.0 + 3.0 * np.sin(0.9 * t + 2.0 * j), MOTHER_Z0 + 30.0 + r * np.cos(a))

    def march(t):            # march ahead: they streak forward past the lens over the river toward Zion
        u = t - MARCH - 0.08 * j
        x = (0.35 * LANE_X[j] + (2.5 if j % 2 else -2.5)) * (1.0 + 0.3 * max(u, 0.0))
        return _v(x + 1.5 * np.sin(1.4 * t + j), 3.0 + 1.5 * np.sin(1.1 * t + j) + 4.0 * max(u - 1.5, 0.0),
                  70.0 - 55.0 * u - 10.0 * u * abs(u))

    def weave(t):            # among the walkers, at their height
        return _v(LANE_X[j] + 1.2 * np.sin(2.2 * t + j), 1.9 + 0.9 * np.sin(1.6 * t + j),
                  MOTHER_Z0 - walked(t) + 10.0 + 35.0 * (0.5 + 0.5 * np.sin(0.7 * t + 0.8 * j)))

    def dive(t):             # fulfilled: down from over her light and back through its lane, lighting hearts
        s0, m = DIVE_T[j], MOTHER_Z0 - walked(t)
        hover = _v(0.4 * LANE_X[j] + 2.0 * np.sin(t + j), 10.0 + np.sin(1.3 * t + j), m + 2.0)
        low = _v(LANE_X[j], 1.4, m + 4.0)
        if t < s0 - 0.5:
            return hover
        if t < s0:
            e = _sc(s0 - 0.5, s0, t)
            return hover * (1.0 - e) + low * e
        zr = 4.0 + DIVE_V * (t - s0)
        up = max(zr - 104.0, 0.0) / DIVE_V
        return _v(LANE_X[j] + 0.5 * np.sin(3.0 * t + j), 1.4 + 0.3 * np.sin(5.0 * t) + 14.0 * up * up + 4.0 * up,
                  m + min(zr, 104.0) + 8.0 * up)

    def kings(t):            # round the kings as they walk
        a = a0 + 1.1 * t
        r = 5.0 + 1.0 * np.sin(0.7 * t + j)
        return _v(r * np.sin(a), 2.0 + 1.0 * np.sin(1.3 * t + j), _kz(t) + r * np.cos(a))

    def rise(t):             # the crowns rise and become comets: up in spirals, then on toward Zion
        v = max(t - RISE - 0.35, 0.0)
        c = KINGS_STOP[j % 7] + _v(0.0, 0.05 + 1.6 * 0.35 + 3.0 * 0.35 ** 2, -0.85)
        a = a0 + 4.0 * v
        r = 1.5 * v
        return c + _v(r * np.sin(a), 4.0 * v + 6.0 * v * v, r * np.cos(a) - 20.0 * v * v)

    def home(t):             # the held breath: drawn back into her light, spinning faster
        q = _sc(156.0, 160.4, t)
        m = mother_pos(t)
        a = a0 + 0.4 * (t - 156.0) + 9.0 * q * q
        r = 16.0 * (1.0 - q) ** 1.5 + 0.2
        return m + _v(r * np.sin(a), (14.0 + 2.0 * np.sin(1.1 * t + j)) * (1.0 - q),
                      -4.0 * (1.0 - q) + r * np.cos(a))

    return dict(burst=burst, ring=ring, march=march, weave=weave, dive=dive, kings=kings, rise=rise,
                home=home)[phase]


# (phase, t0, t1, brightness, trail, fade out)
COMET_PHASES = [("burst", LAND, 130.29, 1.0, 1.4, 0.05), ("ring", 130.29, 134.54, 0.8, 1.6, 0.05),
                ("march", 134.54, 139.2, 0.8, 0.8, 0.05), ("weave", 141.5, 144.4, 1.0, 1.2, 0.05),
                ("dive", 144.4, 148.6, 1.1, 0.9, 0.05), ("kings", 148.6, 154.2, 0.35, 1.2, 0.05),
                ("rise", RISE + 0.35, 156.0, 0.7, 0.6, 0.05), ("home", 156.0, 160.6, 0.4, 1.2, 0.5)]


# ---------------------------------------------------------------------------------------------------------
# Hearts lighting in everyone ("fulfilled") and the light gathering to her (the held breath)
# ---------------------------------------------------------------------------------------------------------
class FulfilHearts:
    """Verse 2 "fulfilled" (2:24.4 to 2:30.2): on each accent of the quickening heartbeat, hearts light up in
    the people walking behind Mother's light, in the nine colours: a wave from her light back through the
    procession. Each heart lights as the comet of its lane dives past, in that comet's colour. In the held
    breath they breathe together, and from 159 a spark leaves each heart for her."""

    def __init__(self, walkers):
        self.w = walkers
        r = np.random.default_rng(71)
        n = walkers.n
        self.when = DIVE_T[LANE] + (ZREL - 4.0) / DIVE_V               # as the comet of their lane passes them
        self.col = np.asarray([lin(COL9[i]) for i in LANE])
        from p3d.brand_hearts import heart_points
        self.h = np.concatenate([heart_points(26), 0.55 * heart_points(8, fill=True)])
        self.chest = None
        self.go = 159.0 + r.uniform(0.0, 2.3, n)           # sparks leave for her light
        self.fly = r.uniform(1.0, 1.6, n)
        self.bend = r.normal(0.0, 1.0, (n, 3)) * _v(2.5, 1.5, 0.0)
        self.sub = r.random(n) < 0.8

    def centres(self, t):
        w = self.w
        if self.chest is None:
            hgt = np.zeros(w.n)
            for k, pr in enumerate(w.protos):
                pr.bake()
                hgt[w.kind == k] = pr.height
            self.chest = 0.72 * hgt * w.scale
        return w.place + _ahead(w) * walked(t) + self.chest[:, None] * _v(0.0, 1.0, 0.0)[None, :]

    def sample(self, t):
        if proc_k(t) <= 0.0 or t < FULFIL[0] - 0.1:
            return None
        on = t >= self.when
        if not on.any():
            return None
        c = self.centres(t)[on]
        u = t - self.when[on]
        held = _sc(HALT, HALT + 1.0, t)
        breath = (1.0 + held * (0.18 * np.sin(2.0 * np.pi * 0.45 * t) + 0.5 * gather_k(t))) * glow(t) \
            * (1.0 + 0.6 * hit_pulse(t, FULFIL + KICKS, fall=0.35))
        a = np.clip(u / 0.12, 0.0, 1.0) * (0.75 + 0.9 * np.exp(-u / 0.45)) * breath
        hs = 0.28
        H = np.stack([self.h[:, 0] * hs, self.h[:, 1] * hs, np.zeros(len(self.h))], 1)
        P = c[:, None, :] + H[None, :, :]
        nh = len(self.h)
        cols = np.repeat(self.col[on], nh, axis=0)
        out = [dict(pos=P.reshape(-1, 3), size=0.03, color=cols, alpha=np.repeat(np.minimum(a, 1.6), nh), emit=3.0,
                    kind="spark", reflect=False),
               dict(pos=c, size=0.45, color=self.col[on], alpha=0.22 * a, emit=1.8, kind="soft")]
        # the held breath: light leaves the hearts and gathers to her
        if t > 159.0:
            m = mother_pos(t)
            sel = on & self.sub & (t > self.go)
            if sel.any():
                v = np.clip((t - self.go[sel]) / self.fly[sel], 0.0, 1.0)
                e = v * v * (3.0 - 2.0 * v)
                c0 = self.centres(t)[sel]
                mid = 0.5 * (c0 + m[None, :]) + self.bend[sel] + _v(0.0, 3.0, 0.0)
                ee = e[:, None]
                p = (1 - ee) ** 2 * c0 + 2 * ee * (1 - ee) * mid + ee * ee * m[None, :]
                live = v < 0.98
                col = 0.5 * self.col[sel] + 0.5 * lin(WHITE)[None, :]
                al = 0.9 * np.sin(np.pi * v[live]) + 0.1
                out.append(dict(pos=p[live], size=0.13, color=col[live], alpha=al, emit=3.0, kind="spark",
                                reflect=False))
                out.append(dict(pos=p[live], size=0.7, color=col[live], alpha=0.18 * al, emit=1.6, kind="soft",
                                reflect=False))
        return out


class Ripples:
    """The music runs through the procession: on each hit and each "fulfilled" accent a ripple of colour runs
    out from her light back through everyone (a glow in each person as the wave passes, a new colour each time)."""

    def __init__(self, walkers):
        self.w = walkers
        self.hits = sorted(set([h for h in KICKS if T0 <= h < T1] + list(FULFIL) + list(STRINGS[2:])))
        self.seed = np.random.default_rng(73).random(walkers.n)

    def sample(self, t):
        if proc_k(t) <= 0.0:
            return None
        live = [(i, h) for i, h in enumerate(self.hits) if 0.0 <= t - h < 3.2]
        if not live:
            return None
        w = self.w
        base = w.place + _ahead(w) * walked(t)
        m = mother_pos(t)
        d = np.hypot(base[:, 0] - m[0], base[:, 2] - m[2])
        a = np.zeros(w.n)
        col = np.zeros((w.n, 3))
        for i, h in live:
            u = t - h
            front = 4.0 + 42.0 * u
            amp = np.exp(-((d - front) / 6.0) ** 2) * np.exp(-u / 1.6) * (t >= ARRIVE)
            a += amp
            col += amp[:, None] * lin(COL9[(3 * i + 2) % 9])[None, :]
        on = a > 0.02
        if not on.any():
            return None
        c = col[on] / a[on, None]
        aa = np.minimum(a[on], 1.0) * proc_k(t)
        P = base[on] + _v(0.0, 1.1, 0.0)
        return [dict(pos=P, size=1.5, color=c, alpha=0.26 * aa, emit=1.8, kind="soft", reflect=False),
                dict(pos=P + _v(0.0, 0.55, 0.0), size=0.12, color=c, alpha=0.9 * aa, emit=3.0, kind="spark",
                     twinkle=0.5, seed=self.seed[on], reflect=False)]


# ---------------------------------------------------------------------------------------------------------
# The kings: they walk in the aisle in gold, crowns of light on their heads, kneel and lay the crowns down
# ---------------------------------------------------------------------------------------------------------


def _robed(crowd):
    """Kings wear long robes."""
    for pr in crowd.protos:
        pr.spec["garment"] = "robe"
        pr.spec["hair"] = "short"
    crowd.facing[:] = np.pi
    return crowd


class Crowns:
    """Crowns of gold light on the kings' heads (they follow each head as the kings walk and kneel); as the
    kings go down the crowns are laid on the sea before them (2:34.75), and on 2:35.34 they rise as sparks
    toward Zion."""

    def __init__(self, walking, kneeling):
        self.wk, self.kn = walking, kneeling
        r = np.random.default_rng(81)
        R = 0.14
        a = np.linspace(0, 2 * np.pi, 56, endpoint=False)
        ring = np.stack([R * np.cos(a), np.zeros(56), R * np.sin(a)], 1)
        tips, jewels = [], []
        for i in range(8):
            b = 2 * np.pi * i / 8
            base = _v(R * np.cos(b), 0.04, R * np.sin(b))
            top = _v(1.2 * R * np.cos(b), 0.19, 1.2 * R * np.sin(b))
            tips.append(_seg(base, top, 0.016))
            jewels.append(top)
        self.C = np.concatenate([ring, ring + _v(0, 0.045, 0)] + tips)
        self.J = np.asarray(jewels)
        n = len(KINGS_STOP)
        self.s = r.random((n, len(self.C) + len(self.J), 4))
        self.cache = (None, None)

    def heads(self, t):
        """The top of each king's head (x, y, z) at t."""
        if self.cache[0] == t:
            return self.cache[1]
        crowd = self.wk if t < K_STOP else self.kn
        P = _points_of(crowd, t)
        out = []
        for Q in P:
            y = Q[:, 1]
            top = y.max()
            sel = y > top - 0.09
            out.append(_v(Q[sel, 0].mean(), top - 0.06, Q[sel, 2].mean()))
        out = np.asarray(out)
        self.cache = (t, out)
        return out

    def sample(self, t):
        if proc_k(t) <= 0.0 or not (K_IN - 0.2 <= t < RISE + 6.0):
            return None
        out = []
        gold, pale = lin(GOLD), lin("#ffe6a8")
        if t < RISE:
            hd = self.heads(t)
            a = _sc(K_IN, K_IN + 0.7, t)
            lay = _sc(LAY0, LAY1, t)
            for i, h in enumerate(hd):
                ground = KINGS_STOP[i] + _v(0.0, 0.05, -0.85)
                c = h * (1 - lay) + ground * lay + _v(0.0, 0.35 * np.sin(np.pi * lay), 0.0)
                out.append(dict(pos=self.C + c, size=0.026, color=gold, alpha=a, emit=3.6, kind="spark",
                                reflect=False))
                out.append(dict(pos=self.J + c, size=0.035, color=pale, alpha=a, emit=4.0, kind="spark", reflect=False))
                out.append(dict(pos=(c + _v(0, 0.07, 0))[None, :], size=0.36, color=gold, alpha=0.06 * a, emit=2.0,
                                kind="soft", reflect=False))
            if t > RISE - 0.25:
                f = _sc(RISE - 0.25, RISE, t)
                P = KINGS_STOP + _v(0.0, 0.12, -0.85)
                out.append(dict(pos=P, size=0.8, color=gold, alpha=0.3 * f, emit=2.2, kind="soft", reflect=False))
            return out
        u = t - RISE
        aim = CHURCH + _v(0.0, 60.0, 0.0)
        CJ = np.concatenate([self.C, self.J])
        q = _sc(0.55, 1.4, u)                                    # whole crowns first, then they break into sparks
        f = _sc(0.0, 0.06, u) * (1.0 - _sc(1.2, 3.2, u))
        spin = 2.5 * u
        cs, sn = np.cos(spin), np.sin(spin)
        R = CJ * _v(1.0, 1.0, 1.0)[None, :]
        R = np.stack([R[:, 0] * cs + R[:, 2] * sn, R[:, 1], -R[:, 0] * sn + R[:, 2] * cs], 1)
        grow = 1.0 + 1.2 * _sc(0.0, 0.6, u)
        for i, p in enumerate(KINGS_STOP):
            s = self.s[i]
            c = p + _v(0.0, 0.05, -0.85) + _v(0.0, 1.6 * u + 3.0 * u * u, 0.0)
            c = c + _unit(aim - c) * 14.0 * max(u - 0.5, 0.0) ** 2
            sp = (s[:, :3] - 0.5) * (6.0 * q * (0.3 + s[:, 3:4]))
            P = c + R * grow + sp
            out.append(dict(pos=P, size=0.035 + 0.04 * q * s[:, 1], color=gold * (1.0 - q) + pale * q,
                            alpha=f, emit=3.6, kind="spark", twinkle=0.3 + 0.5 * q, seed=s[:, 3], reflect=False))
            out.append(dict(pos=c[None, :] + _v(0.0, 0.08, 0.0), size=0.7 * grow, color=gold,
                            alpha=0.10 * f * (1.0 - q), emit=2.0, kind="soft", reflect=False))
        g = np.exp(-u / 0.3)
        out.append(dict(pos=KINGS_STOP + _v(0.0, 0.2, -0.85), size=0.8, color=gold, alpha=0.3 * g, emit=2.0,
                        kind="soft", reflect=False))
        return out


def ray_k(t):
    """How strongly her rays fan out (gentle while words are on screen, so they never burn through them)."""
    b = block_t0(t)
    if b is None:
        return 0.0
    if b == 125.92:
        return 1.8 - 0.6 * _sc(LAND, 129.0, t) + 0.9 * hit_pulse(t, [LAND], fall=1.2)
    if b == 130.29:
        return 0.9
    if b == 134.54:
        return 0.45 + 1.0 * hit_pulse(t, [MARCH], fall=0.6)
    if b == 141.5:
        return 0.7
    if b == 144.4:
        return 0.8 + 0.5 * hit_pulse(t, FULFIL, fall=0.5)
    if b == 161.7:
        return 1.0 + 0.8 * _sc(161.7, 162.3, t)
    if b == 156.0:
        return 0.6 + 0.6 * gather_k(t)
    return 0.45


SHAFTS = [
    # Mother's light: a soft shaft from above onto the sea where she leads
    dict(base=lambda t: (0.0, float(mother_pos(t)[2])), radius=3.5, top=140.0, spread=-0.5, color="#ffe9c8",
         strength=lambda t: proc_k(t) * _sc(LAND - 0.5, LAND + 1.5, t) * shaft_k(t) * 0.10),
]


def add(scene):
    look = dict(color="#fff0dc", color2="#dce8ff", bright=3.2, size=1.35, points=420, seed=21.0)
    scene.add("mother", MotherLight())
    scene.add("gather", Gather())
    # the waves of raised arms: on "let's trust Father" (2:10.29) a wave of raised arms runs back through
    # everyone from her light (down again before they step out); in the held breath they stand still, then
    # lift their arms slowly toward her light as it grows into the slam
    back = _D0 / _D0.max()
    wait = WaveCrowd(waves=[(HIT["trust"], 1.3, 0.35, 1.0, 1.45)], delay=back, gain=crowd_k, places=PROC_P,
                     facing=180.0, kinds=(("raise", 2.0), ("open", 1.0)), start=ARRIVE, until=MARCH,
                     fade=0.3, flash=1.4, **look)
    walkers = GCrowd(gain=crowd_k, places=PROC_P, facing=180.0, kinds=("walk",), start=MARCH, walk=WALK,
                     until=HALT, fade=0.3, flash=0.0, **look)
    wait.facing[:] = walkers.facing
    held = WaveCrowd(waves=[(159.4, 1.4, 6.0, 0.6, 0.6)], delay=back, gain=crowd_k,
                     places=PROC_P + _ahead(walkers) * walked(HALT), facing=180.0,
                     kinds=(("raise", 2.0), ("open", 1.0)), start=HALT - 0.3, fade=0.3, flash=0.0, **look)
    held.facing[:] = walkers.facing
    scene.add("procession wait", wait, reflect=False)
    scene.add("procession", walkers, reflect=False)
    scene.add("procession held", held, reflect=False)
    scene.add("fulfil hearts", FulfilHearts(walkers))
    scene.add("colour ripples", Ripples(walkers))
    king = dict(people=dict(man=1.0), color="#ffd27a", color2=GOLD2, bright=3.0, points=1300, seed=31.0)
    kings_w = _robed(GCrowd(gain=crowd_k, places=KINGS_P, facing=180.0, kinds=("walk",), start=K_IN, walk=WALK,
                            until=K_STOP, fade=0.25, flash=1.2, **king))
    kings_k = _robed(GCrowd(gain=crowd_k, places=KINGS_STOP, facing=180.0, kinds=("kneel",), start=K_STOP - 0.25,
                            act=dict(t=KNEEL, dur=0.3), fade=0.25, flash=0.0, **king))
    scene.add("kings", kings_w, reflect=False)
    scene.add("kings kneel", kings_k, reflect=False)
    scene.add("crowns", Crowns(kings_w, kings_k))
    for ph, a, b, br, tr, fo in COMET_PHASES:
        for j in range(9):
            c = Comet(_comet_head(j, ph), COL9[j], a, b, trail=tr, width=dict(march=0.7, burst=0.55).get(ph, 0.32),
                      bright=br, fade=0.05,
                      light=False, seed=j + 11.0 * len(ph))
            c.k = (lambda c_, a_, b_, fo_: lambda t: _sc(a_, a_ + 0.05, t) * (1.0 - _sc(b_ - fo_, b_, t))
                   * (proc_k(t) > 0.0))(c, a, b, fo)
            scene.add(f"comet {ph} {j}", c, reflect=True)
            if j in (0, 5):
                add_light(c.head, COL9[j], (lambda c_: lambda t: 0.08 * c_.k(t))(c), radius=4.0)
    sky = lambda a_, b_: (lambda t: proc_k(t) * _sc(a_ - 0.01, a_, t) * (1.0 - _sc(b_, b_ + 0.01, t)))  # noqa: E731
    for i, c in enumerate([(-55.0, 40.0, -85.0), (55.0, 40.0, -85.0)]):     # clouds parting round her light
        scene.add(f"proc parting cloud {i}", CloudBank(c, size=(50.0, 30.0, 60.0), puffs=20, seed=40 + i,
                                                       gain=sky(125.92, 130.29), bright=0.35), reflect=True)
    canyon = lambda t: sky(134.54, 135.7)(t) + sky(141.5, 148.6)(t)            # noqa: E731
    for i, x in enumerate((-82.0, 82.0)):          # the canyon of cloud the procession walks through
        scene.add(f"proc canyon {i}", CloudBank((x, 0.0, -40.0), size=(40.0, 45.0, 260.0), puffs=40, seed=50 + i,
                                                gain=canyon, bright=0.35), reflect=True)
    scene.add("kings pillars", Pillars([(float(p[0]), float(p[2])) for p in KINGS_STOP], top=220.0, color="#ffe6c0",
                                       width=0.9, gain=lambda t: proc_k(t) * _sc(153.95, 154.35, t)
                                       * (1.0 - _sc(154.85, 155.25, t)) * 0.35))
    add_rays(mother_pos, lambda t: proc_k(t) * ray_k(t), color="#fff1d8", size=0.6)
    add_light(mother_pos, "#ffe8c8", lambda t: 0.15 * proc_k(t) * (1.0 + 0.5 * hit_pulse(t, KICKS + FULFIL, fall=0.5)),
              radius=9.0)
