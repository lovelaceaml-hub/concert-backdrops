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


def _beat_phase(t):
    """Where t sits in the march beat: the beat count plus the fraction to the next beat (each beat a step)."""
    i = int(np.searchsorted(BEATS, t, side="right")) - 1
    if i < 0 or i >= len(BEATS) - 1:
        return 0.0
    return i + (t - BEATS[i]) / max(BEATS[i + 1] - BEATS[i], 1e-3)


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
    if t0 == 134.54:      # march ahead: from low behind the multitude as they step out, the swoop up starts at
        # once (the words land on the dark sea, never over the mountain), then a slow crane high over the river
        # of people: overhead, the procession draws its path of light toward Zion along the bottom of the frame
        w = walked
        return K((t0, (2.0, 7.0, 26.0), (0.0, -9.0, -26.0)), (134.9, (4.5, 12.0, 17.0), (-1.5, -10.0, -24.0)),
                 (135.4, (10.0, 20.0, 6.0), (-4.0, -6.0, -26.0)), (136.6, (17.0, 29.0, -2.0 - w(136.6)),
                                                                   (-5.0, -3.0, -26.0 - w(136.6))),
                 (t1, (21.0, 36.0, -6.0 - w(t1)), (-6.0, -3.0, -32.0 - w(t1)))), "linear"
    if t0 == 141.5:       # a low tracking shot beside the marchers at their pace, the nations joining from the side
        return _track(t0, t1, 12, lambda t: ((18.2, 1.35, -14.0 - walked(t) - 0.3 * (t - t0)),
                                             (8.0, -0.8, -34.0 - walked(t) - 0.3 * (t - t0)))), "linear"
    if t0 == 144.4:       # fulfilled: the comets dive back through the walkers toward us, lighting hearts, while a
        # slow crane rises from among them over the whole river of people toward her light
        def crane(t):
            u = _sc(t0, t1, t)
            return ((-9.0 + 6.0 * u, 2.2 + 24.0 * u ** 1.3, _mz(t) + 66.0 - 10.0 * u),
                    (0.0, 2.0 - 4.0 * u, _mz(t) + 20.0 - 26.0 * u))
        return _track(t0, t1, 12, crane), "linear"
    if t0 == 148.6:       # from in front, low, backing away at their pace as the kings and the multitude come on;
        # then rising and swinging over them to behind for the words
        kf = _kings_front
        return K((t0, (0.8, 2.7, kf(t0) - 12.5), (0.0, 0.8, kf(t0) + 22.0)),
                 (149.7, (1.4, 3.2, kf(149.7) - 12.8), (0.0, 0.8, kf(149.7) + 20.0)),
                 (150.9, (9.0, 14.0, -62.0), (-1.0, 0.0, -66.0)), (152.2, (3.5, 17.5, -50.5), (-4.0, -6.5, -76.5)),
                 (t1, (1.0, 17.0, -53.0), (-4.5, -7.0, -78.0))), "linear"
    if t0 == 154.2:       # the kings kneel; we look up after the crowns as they rise toward Zion
        return K((t0, (6.0, 4.5, -71.0), (0.0, 0.8, -65.0)), (155.0, (5.0, 3.0, -70.0), (0.0, 1.5, -66.0)),
                 (155.6, (4.5, 1.2, -69.0), (0.0, 3.0, -68.5)), (t1, (4.5, 1.0, -69.0), (0.0, 4.5, -69.0))), "music"
    if t0 == 156.0:       # the held breath: a slow tense push; the comets drawn back into her light
        return K((t0, (4.0, 1.4, -77.0), (0.0, 30.0, -86.0)), (158.3, (3.6, 1.3, -77.5), (0.0, 32.0, -85.0)),
                 (159.4, (3.4, 1.4, -77.6), (0.0, 30.0, -84.0)), (160.1, (3.6, 3.0, -74.5), (0.0, 7.0, -83.0)),
                 (t1, (2.8, 3.6, -72.0), (0.0, 4.5, -83.0))), "music"
    if t0 == 161.7:       # (round 7, f26) past her light, the camera flies into the church of light for the slam
        return K((t0, (2.6, 4.6, -92.0), CH_FAR + _v(0.0, 1.0, 0.0)),
                 (t1, (0.6, 10.5, -128.0), CH_FAR + _v(0.0, 0.5, -4.0))), "music"
    raise ValueError(f"no procession shot planned for the block at {t0}")


# Round 7 (review f26, approved by Anthony): as "to the great Church of God!" begins, the ring of the kings' light
# rises into the sky and resolves into the outline of a church of light, small and dim far below the words; for
# the cut to slam 2 the camera flies into it. Where it stands: in the held breath, high in the sky ahead (below the
# words in the upward view); after the choir's cut, on the sea ahead toward Zion (the flight into it).
CH_SKY = _v(-15.7, 62.4, -110.3)           # (low in the frame of the upward view, below the words)
CH_SKY_BASIS = (_v(0.904, 0.0, -0.428), _v(0.412, 0.271, 0.87))     # its facade turned to face that view
CH_FAR = _v(0.0, 12.0, -142.0)


# banking: the horizon tilts in the big turns and the racing flight (degrees)
ROLL = {125.92: lambda t: -6.0 * _sc(127.4, 128.6, t) * (1.0 - _sc(129.4, 130.29, t)),
        130.29: lambda t: 9.0 * np.sin(np.pi * _sc(130.29, 134.54, t)),
        134.54: lambda t: -8.0 * np.sin(np.pi * _sc(134.54, 135.5, t)),
        141.5: lambda t: 1.2 * np.sin(np.pi * _beat_phase(t)),        # the march beat: the lens sways with each step
        144.4: lambda t: -5.0 * np.sin(np.pi * _sc(144.4, 148.6, t)),
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


def _edge(z):
    """Half the width of the procession at z (in its own frame, at the moment of "march ahead")."""
    return 7.5 + 19.0 * max((z - MOTHER_Z0) / 100.0, 0.0) ** 0.8


# The nations joining from the sides (round 6): from "march ahead" streams of people of light, each nation in its
# own colour, walk in on a slant from both sides and merge into the procession (each one joins at the edge)
SLANT = np.radians(35.0)
NATIONS = [(-1.0, -40.0, 1), (-1.0, -6.0, 6), (-1.0, 26.0, 3), (1.0, -36.0, 2), (1.0, -2.0, 4), (1.0, 30.0, 7)]


def _nation_places(seed=57, groups=None, t0=None, dmax=46.0):
    """Where each nation's people start (world, at t0), their facing, colour and when they reach the procession's
    edge. Round 7: later groups (t0 after "march ahead") start beside where the procession has walked to."""
    groups = NATIONS if groups is None else groups
    t0 = MARCH if t0 is None else t0
    r = np.random.default_rng(seed)
    P, F, C, J = [], [], [], []
    for s, za, col in groups:
        back = np.array([s * np.sin(SLANT), 0.0, np.cos(SLANT)])     # out from the procession and back
        side = np.array([np.cos(SLANT), 0.0, -s * np.sin(SLANT)])
        a = np.array([s * (_edge(za) + 0.8), 0.0, za])
        for d in np.arange(1.2, dmax, 1.55):
            for w in (-1.6, 0.0, 1.6):
                if r.random() < 0.12:
                    continue
                dd = d + r.uniform(-0.35, 0.35)
                p = a + back * dd + side * (w + r.uniform(-0.3, 0.3))
                P.append(p - np.array([0.0, 0.0, walked(t0)]))
                F.append(180.0 + s * np.degrees(SLANT))
                C.append(col)
                # they walk until they reach the procession's edge (in its own frame, which walks on ahead)
                u = np.linspace(0.0, 40.0, 401)
                x = p[0] - s * np.sin(SLANT) * WALK * u
                zr = p[2] + (1.0 - np.cos(SLANT)) * WALK * u
                inside = np.abs(x) <= np.array([_edge(z) for z in zr]) - 0.3
                J.append(t0 + (u[np.argmax(inside)] if inside.any() else 40.0))
    return np.asarray(P), np.asarray(F), np.asarray(C, int), np.asarray(J)


NAT_P, NAT_F, NAT_C, NAT_J = _nation_places()

# Round 7 (Anthony: "The theme should be more and more people going to Zion"): more nations come in from both
# sides as the march goes on, a new wave on the third accent of "fulfilled" (2:21.5) and as the kings come in
# (2:28.6), and everyone who reaches the procession walks on in it at its edge, so it visibly grows.
LATE = [(141.5, [(-1.0, -22.0, 0), (1.0, -18.0, 5), (-1.0, 42.0, 8), (1.0, 46.0, 0)]),
        (148.6, [(-1.0, -54.0, 5), (1.0, -50.0, 8), (-1.0, 10.0, 2), (1.0, 14.0, 6)])]
_late = [_nation_places(59 + i, g, t0, 26.0) for i, (t0, g) in enumerate(LATE)]
LATE_P = np.concatenate([x[0] for x in _late])
LATE_F = np.concatenate([x[1] for x in _late])
LATE_C = np.concatenate([x[2] for x in _late])
LATE_J = np.concatenate([x[3] for x in _late])
LATE_T0 = np.concatenate([np.full(len(x[0]), t0) for x, (t0, _g) in zip(_late, LATE)])


def _joined(P, F, J, start):
    """Where each joiner reaches the procession's edge (world), for those who reach it before the held breath."""
    f = np.radians(np.asarray(F, np.float64))
    d = np.stack([np.sin(f), np.zeros(len(f)), np.cos(f)], 1)
    return P + d * (WALK * np.maximum(J - start, 0.0))[:, None]


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
                ("march", 134.54, 135.5, 0.8, 0.8, 0.3), ("weave", 141.5, 144.4, 1.0, 1.2, 0.05),
                ("dive", 144.4, 148.6, 1.1, 0.9, 0.05), ("kings", 148.6, 154.2, 0.35, 1.2, 0.05),
                ("rise", RISE + 0.35, 156.0, 0.7, 0.6, 0.05), ("home", 156.0, 158.9, 0.4, 1.2, 1.1)]   # (round 7, f26: they fade as the church forms)


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


class ChurchRise:
    """f26: the ring of the kings' light rises (2:35.3), resolves into the outline of a church of light (2:36.6
    to 2:38.2) small and dim below the words, holds calm while they read, and is flown into for slam 2. The
    outline: the hall with its gabled roof and a row of arched windows, the door, and a tower with a pointed roof
    (no cross: the Church of God's buildings carry none)."""

    T_RING, T_FORM, T_DONE = RISE, 156.6, 158.2

    def __init__(self):
        segs = [((-0.8, 0.0), (0.8, 0.0)), ((-0.8, 0.0), (-0.8, 0.6)), ((0.8, 0.0), (0.8, 0.6)),
                ((-0.85, 0.6), (0.0, 0.88)), ((0.0, 0.88), (0.85, 0.6)), ((-0.85, 0.6), (0.85, 0.6)),
                ((0.48, 0.6), (0.48, 1.25)), ((0.78, 0.6), (0.78, 1.25)), ((0.48, 1.25), (0.78, 1.25)),
                ((0.45, 1.25), (0.63, 1.62)), ((0.63, 1.62), (0.81, 1.25)),
                ((-0.12, 0.0), (-0.12, 0.26)), ((0.12, 0.0), (0.12, 0.26))]
        pts = [_seg((a[0], a[1], 0.0), (b[0], b[1], 0.0), 0.012) for a, b in segs]
        a = np.linspace(0.0, np.pi, 24)
        pts.append(np.stack([0.12 * np.cos(a), 0.26 + 0.12 * np.sin(a), 0.0 * a], 1))     # the door's arch
        for x in np.linspace(-0.62, 0.28, 5):                                              # arched windows
            pts.append(np.stack([x + 0.05 * np.cos(a), 0.38 + 0.05 * np.sin(a), 0.0 * a], 1))
            pts.append(_seg((x - 0.05, 0.2, 0.0), (x - 0.05, 0.38, 0.0), 0.012))
            pts.append(_seg((x + 0.05, 0.2, 0.0), (x + 0.05, 0.38, 0.0), 0.012))
        self.Q = np.concatenate(pts) - np.array([0.0, 0.8, 0.0])        # centred on its middle
        n = len(self.Q)
        r = np.random.default_rng(97)
        self.ang = np.arctan2(self.Q[:, 1], self.Q[:, 0]) + r.normal(0.0, 0.15, n)   # its place on the ring
        nine = np.asarray([lin(c) for c in COL9])
        self.ring_col = nine[((self.ang + np.pi) / (2 * np.pi) * 9).astype(int) % 9]
        self.s = r.random(n)

    def where(self, t):
        """(centre, size in metres, facade right and up) of the church at t."""
        if t < 160.6:
            return CH_SKY, 12.0, CH_SKY_BASIS[0], CH_SKY_BASIS[1]
        return CH_FAR, 24.0, _v(1.0, 0.0, 0.0), _v(0.0, 1.0, 0.0)

    def sample(self, t):
        if proc_k(t) <= 0.0 or not (self.T_RING <= t < 162.9):
            return None
        C, S, Rb, Ub = self.where(t)
        church = C[None, :] + S * (self.Q[:, :1] * Rb[None, :] + self.Q[:, 1:2] * Ub[None, :])
        u = _sc(self.T_RING, self.T_FORM, t)                    # the ring rising from the kings into the sky
        ring_c = _v(0.0, 1.0, -65.6) * (1.0 - u) + C * u
        rad = 3.2 + (0.55 * S - 3.2) * u
        flat = np.stack([np.cos(self.ang), 0.0 * self.ang, np.sin(self.ang)], 1)
        up = np.cos(self.ang)[:, None] * Rb[None, :] + np.sin(self.ang)[:, None] * Ub[None, :]
        ring = ring_c[None, :] + rad * (flat * (1.0 - u) + up * u)
        m = _ss(self.T_FORM, self.T_DONE, t)                    # the ring resolves into the church
        m = np.clip(m * 1.4 - 0.4 * self.s, 0.0, 1.0)[:, None]
        P = ring * (1.0 - m) + church * m
        col = self.ring_col * (1.0 - 0.7 * m) + lin("#ffe2b0") * (0.7 * m)
        fly = _sc(161.7, 162.86, t)
        a = (0.75 - 0.3 * m[:, 0]) * _sc(self.T_RING, self.T_RING + 0.4, t) * (1.0 + 0.15 * beat_pulse(t))
        a = a * (1.0 + 0.8 * fly) * (1.0 if t < 160.6 else 2.2)      # bright enough to fly into after the cut
        return [dict(pos=P, size=0.09 * S / 12.0, color=col, alpha=a.astype(np.float32), emit=2.2, kind="spark",
                     twinkle=0.25, seed=self.s, dof=0.0, reflect=False),
                dict(pos=P[::6], size=0.5 * S / 12.0, color=col[::6] * 0.8, alpha=(0.05 * a[::6]).astype(np.float32),
                     emit=1.3, kind="soft", dof=0.0, reflect=False)]


class KingBeams:
    """The kings' pillars of light (2:34): narrow bright beams falling from the sky beside the kneeling kings
    (two on each side of them, never over the whole view), with a small pool where each lands; they pulse
    with the beat and burst on the two kings' hits. No wide glow, so the low view stays clear."""

    BASES = np.asarray([(-4.4, -67.4), (-4.6, -63.4), (-1.2, -60.4), (2.6, -59.8)])   # clear of the lens

    def __init__(self):
        self.u = np.linspace(0.0, 1.0, 900) ** 1.8      # dense low down: a solid beam, not a dotted line
        self.col = lin("#ffe9c4")
        self.ph = np.random.default_rng(83).random(len(self.BASES))

    def gain(self, t):
        return proc_k(t) * _sc(153.95, 154.3, t) * (1.0 - _sc(154.95, 155.3, t))

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.0:
            return None
        k = g * (0.85 + 0.35 * beat_pulse(t) + 0.6 * hit_pulse(t, [KNEEL, RISE], fall=0.35))
        out = []
        top = 60.0
        for i, (x, z) in enumerate(self.BASES):
            fall = _sc(153.95 + 0.06 * i, 154.25 + 0.06 * i, t)      # each beam falls from the sky in turn
            y = top * (1.0 - fall * (1.0 - self.u))
            P = np.stack([np.full_like(y, x), y, np.full_like(y, z)], 1)
            a = k * (0.5 + 0.5 * self.u ** 0.4) * (0.9 + 0.1 * np.sin(9.0 * t + 6.0 * self.ph[i]))
            out.append(dict(pos=P, size=0.10, color=lin(WHITE), alpha=0.9 * a, kind="soft", emit=4.0, dof=0.2,
                            reflect=False))
            out.append(dict(pos=P, size=0.42, color=self.col, alpha=0.22 * a, kind="soft", emit=2.6, dof=0.2,
                            reflect=False))
            if fall > 0.95:
                out.append(dict(pos=np.array([[x, 0.08, z]]), size=1.6, color=self.col, alpha=0.35 * k, kind="soft",
                                emit=2.2, reflect=False))
        return out


class MarchBeat:
    """The march beat in their steps (2:14.5 to 2:36): on every beat each walker's foot lands on the sea of glass
    with a small spark of light (left, right, left), and a pulse of light runs forward up the aisle from the back
    of the procession to her light: the procession drawing its path of light toward Zion."""

    def __init__(self, crowds):
        self.cr = crowds
        self.seed = np.random.default_rng(87).random(4000)
        z = np.arange(0.0, 104.0, 0.45)
        xs = np.linspace(-2.6, 2.6, 7)
        Z, X = np.meshgrid(z, xs)
        self.zr, self.xr = Z.ravel(), X.ravel()                      # the path behind her light (her frame)
        r = np.random.default_rng(88)
        self.jit = r.uniform(-0.2, 0.2, (len(self.zr), 2))

    def sample(self, t):
        k = proc_k(t) * _sc(MARCH - 0.05, MARCH + 0.3, t) * (1.0 - _sc(HALT - 0.2, HALT + 0.4, t))
        if k <= 0.0:
            return None
        bp = _beat_phase(t)
        i, fr = int(bp), bp - int(bp)
        land = np.exp(-fr / 0.22)                                     # the foot lands on the beat
        side = 1.0 if i % 2 else -1.0
        out = []
        for cr in self.cr:
            live = t >= cr.start
            if cr.until is not None:
                live &= t <= cr.until
            if not live.any():
                continue
            ii = np.where(live)[0]
            f = cr.facing[ii]
            age = np.maximum(t - cr.start[ii], 0.0)
            ahead = np.stack([np.sin(f), np.zeros(len(f)), np.cos(f)], 1)
            right = np.stack([np.cos(f), np.zeros(len(f)), -np.sin(f)], 1)
            P = cr.place[ii] + ahead * (WALK * age)[:, None] + right * (0.11 * side) + ahead * 0.25
            P[:, 1] = 0.04
            col = cr.tint[ii] * 0.6 + lin(WHITE)[None, :] * 0.4
            sd = self.seed[ii % len(self.seed)]
            out.append(dict(pos=P, size=0.09 + 0.05 * (1.0 - land), color=col, alpha=0.9 * land * k, emit=3.0,
                            kind="spark", seed=sd, reflect=False))
            out.append(dict(pos=P, size=0.5 + 0.5 * (1.0 - land), color=col, alpha=0.10 * land * k, emit=1.6,
                            kind="soft", reflect=False))
        # the path of light up the aisle: a pulse on every beat runs forward to her light
        m = mother_pos(t)
        zr = self.zr
        front = 104.0 * (1.0 - fr / 0.6)                              # from the back to her in 0.6 s
        pulse = np.exp(-((zr - front) / 5.0) ** 2) * (fr < 0.6)
        base = 0.10 + 0.08 * np.exp(-zr / 25.0)
        a = (base + 0.45 * pulse) * k * (1.0 - _sc(K_IN - 0.3, K_IN + 0.5, t) * 0.5)
        P = np.stack([self.xr + self.jit[:, 0], np.full(len(zr), 0.05), m[2] + 3.0 + zr + self.jit[:, 1]], 1)
        warm = lin("#ffe2b0")
        out.append(dict(pos=P, size=0.55, color=warm, alpha=0.20 * a, emit=1.8, kind="soft", reflect=False))
        out.append(dict(pos=P, size=0.06, color=lin(WHITE), alpha=0.8 * a, emit=2.8, kind="spark", twinkle=0.6,
                        seed=self.seed[np.arange(len(zr)) % len(self.seed)], reflect=False))
        # a short way of light ahead of her toward Zion (dim and short, so it never reaches the words)
        ah = np.linspace(0.0, 14.0, 60)
        A = np.stack([np.zeros(60), np.full(60, 0.05), m[2] - ah], 1)
        out.append(dict(pos=A, size=1.2, color=warm, alpha=0.08 * k * np.exp(-ah / 6.0), emit=1.8, kind="soft",
                        reflect=False))
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
        return 0.35 + 0.6 * hit_pulse(t, [MARCH], fall=0.5)     # softer: the words are arriving over it
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


def _tint_nations(crowd, cols=None):
    """Each nation in its own colour: a coloured robe of light with pale glints."""
    cols = NAT_C if cols is None else cols
    r = np.random.default_rng(58)
    for i, c in enumerate(cols):
        c1 = lin(COL9[c])
        mix = r.uniform(0.15, 0.45)
        crowd.tint[i] = c1 * (1.0 - mix) + lin(WHITE) * mix
    return crowd


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
    # the nations joining from the sides, each in its own colour (clothed in light, the same bodies as everyone)
    nations = GCrowd(gain=crowd_k, places=NAT_P, facing=NAT_F, kinds=("walk",), start=MARCH - 0.1, walk=WALK,
                     until=np.minimum(NAT_J, HALT), fade=0.45, flash=1.2, **look)
    _tint_nations(nations)
    gone = NAT_J < HALT                       # those still on their way at the held breath stand still there
    still = NAT_P[~gone] + _ahead(nations)[~gone] * walked(HALT)
    nat_held = WaveCrowd(waves=[(159.4, 1.4, 6.0, 0.6, 0.6)], delay=np.full(len(still), 0.5), gain=crowd_k,
                         places=still, facing=NAT_F[~gone], kinds=(("raise", 2.0), ("open", 1.0)), start=HALT - 0.3,
                         fade=0.3, flash=0.0, **look)
    _tint_nations(nat_held, NAT_C[~gone])
    scene.add("proc nations", nations, reflect=False)
    scene.add("proc nations held", nat_held, reflect=False)
    # round 7: more nations come in from both sides later in the march (each in its own colour)
    late = GCrowd(gain=crowd_k, places=LATE_P, facing=LATE_F, kinds=("walk",), start=LATE_T0 - 0.2, walk=WALK,
                  until=np.minimum(LATE_J, HALT), fade=0.6, flash=1.4, **look)
    _tint_nations(late, LATE_C)
    lgone = LATE_J < HALT
    lstill = LATE_P[~lgone] + _ahead(late)[~lgone] * (WALK * (HALT - LATE_T0[~lgone]))[:, None]
    late_held = WaveCrowd(waves=[(159.4, 1.4, 6.0, 0.6, 0.6)], delay=np.full(len(lstill), 0.5), gain=crowd_k,
                          places=lstill, facing=LATE_F[~lgone], kinds=(("raise", 2.0), ("open", 1.0)),
                          start=HALT - 0.3, fade=0.3, flash=0.0, **look)
    _tint_nations(late_held, LATE_C[~lgone])
    scene.add("proc nations late", late, reflect=False)
    scene.add("proc nations late held", late_held, reflect=False)
    # round 7: everyone who reaches the procession walks on in it at its edge, so it visibly grows as it marches
    # (and stands with it in the held breath)
    JP = np.concatenate([NAT_P[gone] + _ahead(nations)[gone] * (WALK * (NAT_J[gone] - MARCH + 0.1))[:, None],
                         LATE_P[lgone] + _ahead(late)[lgone] * (WALK * (LATE_J[lgone] - LATE_T0[lgone] + 0.2))[:, None]])
    JT = np.concatenate([NAT_J[gone], LATE_J[lgone]])
    JC = np.concatenate([NAT_C[gone], LATE_C[lgone]])
    joined = GCrowd(gain=crowd_k, places=JP, facing=180.0, kinds=("walk",), start=JT - 0.3, walk=WALK, until=HALT,
                    fade=0.45, flash=0.0, **look)
    _tint_nations(joined, JC)
    jheld = WaveCrowd(waves=[(159.4, 1.4, 6.0, 0.6, 0.6)], delay=np.full(len(JP), 0.5), gain=crowd_k,
                      places=JP + _ahead(joined) * (WALK * (HALT - JT + 0.3))[:, None], facing=180.0,
                      kinds=(("raise", 2.0), ("open", 1.0)), start=HALT - 0.3, fade=0.3, flash=0.0, **look)
    jheld.facing[:] = joined.facing
    _tint_nations(jheld, JC)
    scene.add("proc joined", joined, reflect=False)
    scene.add("proc joined held", jheld, reflect=False)
    scene.add("march beat", MarchBeat([walkers, nations, late, joined]))
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
    # (round 6: no canyon of cloud over the march any more; it hazed the words and the low views of the walkers)
    scene.add("kings beams", KingBeams())
    scene.add("church rise", ChurchRise())
    add_rays(mother_pos, lambda t: proc_k(t) * ray_k(t), color="#fff1d8", size=0.6)
    add_light(mother_pos, "#ffe8c8", lambda t: 0.15 * proc_k(t) * (1.0 + 0.5 * hit_pulse(t, KICKS + FULFIL, fall=0.5)),
              radius=9.0)
