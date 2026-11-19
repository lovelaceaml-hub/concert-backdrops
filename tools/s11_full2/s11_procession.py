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
  148.6   twelve kings in gold, pair after pair on the beat, walk in the aisle: crowns of light, royal trains
  154.2   the kings kneel and lay their crowns down; 155.34 the crowns rise and hover over them
  156.0   the held breath: the crowns stream as nine comets over the sea into the emblem of the church of light
          on Mount Zion (2:39.2); 161.7 the camera flies to the church and its emblem for slam 2
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
from songs.s11_zion import WaveCrowd, mx  # noqa: E402  (the waves of raised arms; the music map)
import songs.s11_church as CH  # noqa: E402  (read only: the church of light and its traced emblem, ENDS thread)

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

T0, T1 = 125.92, 162.3
LAND = STRINGS[2]          # 127.64: the light touches the sea on the third strings pulse
MARCH = HIT["march"]       # 134.54: everyone steps out together
HALT = DROP2               # 156.0: the held breath, everyone stands still
MOTHER_Z0 = -55.0          # where Mother's light comes down on the sea, ahead of everyone
M_H = 4.2                  # how high her light rides over the sea
WALK = 1.3                 # metres per second toward Zion, from "march ahead"
AISLE = 5.5                # the aisle down the middle (the kings walk and kneel in it; MARCH round 1: wider,
                           # so the camera can walk in it with everyone and the kings have room for their trains)
KNEEL = HIT["kings1"]      # 154.2
RISE = HIT["kings2"]       # 155.34
K_STOP = KNEEL - 0.05      # the kings stop walking and go down
K_IN = 148.6               # the kings appear in the aisle
LAY0, LAY1 = 154.75, 155.28   # the crowns go from the heads down onto the sea before the kings
# (MARCH round 2, Anthony: "The kings part needs to be very very clear, detailed and epic to really make us feel the
# grandness of kings coming to mother.") Twelve kings in six pairs down the aisle, larger than life, each pair
# appearing on the music's eighth notes from the front back, so they keep coming.
K_ROWS, K_GAP, K_X = 6, 2.7, 1.55
KINGS_STOP = np.asarray([(sx * K_X, 0.0, -66.0 + K_GAP * r) for r in range(K_ROWS) for sx in (-1.0, 1.0)])
K_N = len(KINGS_STOP)
KING_T = np.repeat(np.asarray([148.6, 148.79, 149.03, 149.26, 149.5, 149.75]), 2)      # each pair's entrance
KING_SCALE = 1.12
KINGS_P = KINGS_STOP + np.stack([np.zeros(K_N), np.zeros(K_N), WALK * (K_STOP - KING_T)], 1)
K_COL = ["#ff5a7a", "#a77bff", "#5b8cff", "#3fd6a0", "#ffb347", "#ff86c8"]     # the royal colours of the trains


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


def king_base(i, t):
    """Where king i stands (feet, world) at t."""
    return KINGS_STOP[i] + _v(0.0, 0.0, WALK * max(K_STOP - max(t, KING_T[i]), 0.0))


# The crowns' flight to the church (2:35.34): each crown lifts from the sea before its king, then streams over the
# sea and up the mountain into the church's emblem, arriving at CROWN_HOME.
CROWN_LIFT, CROWN_FLY = 0.66, 3.2       # they rise and hover over the kings on the hit, then fly in the next shot
CROWN_HOME = RISE + CROWN_LIFT + CROWN_FLY          # 158.59: the crowns reach the emblem


def crown_ground(i):
    return KINGS_STOP[i] + _v(0.0, 0.05, -0.85)


def crown_path(i, t):
    """The centre of crown i after it rises (t >= RISE)."""
    u = max(t - RISE, 0.0)
    g = crown_ground(i) + _v(0.0, 0.75 * _ss(0.0, CROWN_LIFT, u), 0.0)
    s = _ss(0.0, 1.0, (u - CROWN_LIFT) / CROWN_FLY)
    aim = _emblem_c() + _v(0.35 * (KINGS_STOP[i, 0]), 0.0, 1.0)
    p = g * (1.0 - s) + aim * s
    fan = (i - (K_N - 1) / 2.0) / ((K_N - 1) / 2.0)      # -1 .. 1: they fan out across the view and meet in the emblem
    p[0] += 34.0 * fan * np.sin(np.pi * s)
    p[1] += (6.0 + 6.0 * abs(fan)) * np.sin(np.pi * s)    # a gentle arc into the emblem (under the words in the view)
    a = 2.0 * np.pi * i / K_N + 7.0 * s
    r = 0.9 * np.sin(np.pi * s)
    return p + _v(r * np.cos(a), 0.6 * r * np.sin(a), 0.0)


def _emblem_c():
    return np.asarray(CH.EMB_C, np.float64)


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
    if t0 == 130.29:      # trust Father: an orbit from the side round to the front, a little lower than before
        # (f29), the three comets circling, her light one soft distant glow
        return K((t0, (36.0, 10.0, -30.0), (0.0, 1.5, -35.0)), (131.8, (31.0, 12.5, -60.0), (0.0, 1.5, -35.0)),
                 (133.2, (13.0, 12.0, -75.0), (0.0, 1.0, -32.0)), (t1, (5.0, 11.5, -73.0), (0.0, 1.0, -28.0))), "music"
    if t0 == 134.54:      # march ahead: from low behind the multitude as they step out, the swoop up starts at
        # once (the words land on the dark sea, never over the mountain), then a slow crane high over the river
        # of people: overhead, the procession draws its path of light toward Zion along the bottom of the frame
        w = walked
        return K((t0, (2.0, 7.0, 26.0), (0.0, -9.0, -26.0)), (134.9, (4.5, 12.0, 17.0), (-1.5, -10.0, -24.0)),
                 (135.4, (10.0, 20.0, 6.0), (-4.0, -6.0, -26.0)), (136.6, (17.0, 29.0, -2.0 - w(136.6)),
                                                                   (-5.0, -3.0, -26.0 - w(136.6))),
                 (t1, (21.0, 36.0, -6.0 - w(t1)), (-6.0, -3.0, -32.0 - w(t1)))), "linear"
    if t0 == 141.5:       # (MARCH round 1) walking with them: eye level in the aisle at their pace, a little faster
        # so we pass between the rows; everyone on both sides walks the one way we look, toward her light ahead
        # (a little above their heads, looking down the rows, so they stand out against the dark sea, not Zion's glow)
        return _track(t0, t1, 12, lambda t: ((1.1 - 0.15 * (t - t0), 3.3, _mz(t) + 30.0 - 0.45 * (t - t0)),
                                             (-0.4, 0.2, _mz(t) + 6.0))), "linear"
    if t0 == 144.4:       # fulfilled: the comets dive back through the walkers toward us, lighting hearts, while a
        # slow crane rises from among them over the whole river of people toward her light
        def crane(t):          # (MARCH round 4) rising higher and further back: the whole river, growing wider
            u = _sc(t0, t1, t)
            return ((-9.0 + 7.0 * u, 2.2 + 40.0 * u ** 1.3, _mz(t) + 66.0 + 22.0 * u ** 1.5),
                    (0.0, 2.0 - 4.0 * u, _mz(t) + 20.0 - 6.0 * u))
        return _track(t0, t1, 12, crane), "linear"
    if t0 == 148.6:       # (MARCH round 2) the kings: a low hero angle in front of them, backing away at their pace,
        # looking up at the front pair as pair after pair of kings comes on down the aisle between the multitude;
        # "All kings worship You" reads in the dark sky above their crowns
        kf = _kings_front

        def hero(t):
            u = _sc(t0, t1, t)
            # (looking up at them: the front crowns sit well under the words, the kings tower against the sky)
            return ((1.9 + 1.6 * u, 0.5 + 0.2 * u, kf(t) - 8.2 + 0.9 * u), (0.0 - 0.3 * u, 3.3 + 0.1 * u, kf(t) + 6.5))
        return _track(t0, t1, 14, hero), "linear"
    if t0 == 154.2:       # (MARCH round 2) the kings kneel (2:34.2): close behind them, their trains spread on the sea
        # toward us; the crowns are laid down before them and on 2:35.34 rise and stream away over the sea to Zion
        zb = float(KINGS_STOP[-1, 2])
        # (from a little above, looking down onto them, so Zion's bright city stays above the frame while the words
        # arrive; the crowns rise on the hit and hover glowing over the kings until the cut)
        return K((t0, (4.4, 5.2, zb + 6.5), (-0.3, 0.3, zb - 6.5)), (155.3, (4.0, 4.9, zb + 5.6), (-0.2, 0.4, zb - 7.0)),
                 (t1, (3.6, 4.8, zb + 5.0), (0.0, 0.6, zb - 7.5))), "music"
    if t0 == 156.0:       # (MARCH round 2, Anthony: "the main church from Korea should be shown and the church logo")
        # the held breath: after the crowns, a slow push over the multitude and the sea toward Zion; the church of
        # light stands centred on the summit below the words, and its emblem lights as the crowns reach it
        e = _emblem_c()
        return K((t0, (2.0, 44.0, -48.0), e + _v(0.0, 2.0, 0.0)), (158.3, (1.2, 56.0, -95.0), e + _v(0.0, 3.0, 0.0)),
                 (t1, (0.6, 66.0, -150.0), e + _v(0.0, 3.0, 0.0))), "music"
    if t0 == 161.7:       # (MARCH round 2) the camera flies to the church of light and its emblem for slam 2
        e = _emblem_c()
        return K((t0, (0.0, 64.0, -240.0), e + _v(0.0, 0.5, 0.0)),
                 (t1, (0.6, 113.0, -352.0), e)), "music"
    raise ValueError(f"no procession shot planned for the block at {t0}")


# banking: the horizon tilts in the big turns and the racing flight (degrees)
ROLL = {125.92: lambda t: -6.0 * _sc(127.4, 128.6, t) * (1.0 - _sc(129.4, 130.29, t)),
        130.29: lambda t: 9.0 * np.sin(np.pi * _sc(130.29, 134.54, t)),
        134.54: lambda t: -8.0 * np.sin(np.pi * _sc(134.54, 135.5, t)),
        141.5: lambda t: 1.2 * np.sin(np.pi * _beat_phase(t)),        # the march beat: the lens sways with each step
        144.4: lambda t: -5.0 * np.sin(np.pi * _sc(144.4, 148.6, t)),
        148.6: lambda t: 2.0 * np.sin(np.pi * _sc(148.6, 154.2, t))}


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
    return 1.0 if block_t0(t) in (125.92, 141.5, 144.4) else 0.0      # (f29: none over the gathering)


def mirror_k(t):
    """Her mirror image in the sea shows except in the views from high behind (it would sit in the words)."""
    return 0.0 if block_t0(t) in (130.29, 134.54, 148.6, 154.2, 156.0) else 1.0    # (f29: one light, not two)


def glow(t):
    """How bright the scene burns with the music: intensity, a soft pulse on the beat (not in the held breath)."""
    held = _sc(HALT, HALT + 0.6, t)
    return (0.75 + 0.4 * intensity(t)) * (1.0 + 0.16 * (1.0 - held) * beat_pulse(t))


def crowd_k(t):
    k = proc_k(t) * glow(t) * (1.0 + mx(t, choir=0.3, strings=0.15))     # (round 8) they glow with the choir
    if block_t0(t) == 154.2:                 # (MARCH) looking down on them, the words arrive over the multitude
        k *= 1.0 - 0.35 * _mfx()._reading(t)
    return k


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
# (MARCH round 1, Anthony: "The close up scene has people going in all directions. Don't do that. They should
# be going to Mother.") The nations now come in on a shallow slant, so in every view they walk the same way as
# everyone, toward her light, closing in on the procession as they go (was 35 degrees, which read as crossing).
SLANT = np.radians(16.0)
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


# (MARCH round 4, Anthony: "Also there should be more and more and more people.") On the music's accents through
# the march, new people of light flare in and take their places: new rows behind (the river grows longer) and a new
# column along both outer edges (it grows wider), each wave rolling from her light back. They walk on with
# everyone toward her light and stand with them in the held breath.
GROW_T = [135.9, 137.9, 141.5, 143.4, 145.0, 146.7, 148.6, 150.2]


def _grow_places(seed=95):
    r = np.random.default_rng(seed)
    P, S = [], []
    for w, tw in enumerate(GROW_T):
        rel = []
        for z in np.arange(100.0 + 7.6 * w, 100.0 + 7.6 * (w + 1), 1.9):          # new rows behind
            half = _edge(MOTHER_Z0 + 100.0) + 1.0 * w
            xs = np.arange(AISLE, half, 1.75) + 0.85 * (int(z / 1.9) % 2)
            for s in (-1.0, 1.0):
                for x in xs:
                    if r.random() > 0.15:
                        rel.append((s * (x + r.uniform(-0.3, 0.3)), z + r.uniform(-0.4, 0.4)))
        for z in np.arange(12.0, 100.0 + 7.6 * w, 2.4):                             # a new column on each edge
            x = _edge(MOTHER_Z0 + min(z, 100.0)) + 1.9 * (w + 1) + 0.6
            for s in (-1.0, 1.0):
                if r.random() > 0.2:
                    rel.append((s * (x + r.uniform(-0.35, 0.35)), z + r.uniform(-0.5, 0.5)))
        rel = np.asarray(rel)
        ts = tw + 0.9 * np.clip(rel[:, 1] / 140.0, 0.0, 1.0) + r.uniform(0.0, 0.25, len(rel))   # from her light back
        # where they stand when they appear (world): in formation behind her light at that moment
        world = np.stack([rel[:, 0], np.zeros(len(rel)), MOTHER_Z0 + rel[:, 1] - WALK * (ts - MARCH)], 1)
        P.append(world)
        S.append(ts)
    return np.concatenate(P), np.concatenate(S)


GROW_P, GROW_S = _grow_places()


class GrowSparks:
    """(MARCH round 4) Each newcomer streams in as a spark of light from far out over the sea (from the side they
    join, or from behind), arcing in to their place in the procession and becoming them as they flare in."""

    def __init__(self):
        r = np.random.default_rng(96)
        n = len(GROW_P)
        out = np.stack([np.sign(GROW_P[:, 0]), np.zeros(n), np.zeros(n)], 1)
        back = GROW_P[:, 2] - (MOTHER_Z0 - WALK * (GROW_S - MARCH)) > 100.0
        out[back] = _v(0.0, 0.0, 1.0)
        out = out + 0.35 * np.stack([r.normal(0, 1, n), np.zeros(n), r.normal(0, 1, n)], 1)
        out /= np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-6)
        self.end = GROW_P + _v(0.0, 1.1, 0.0)
        self.beg = self.end + out * r.uniform(28.0, 60.0, n)[:, None] + np.stack(
            [np.zeros(n), r.uniform(4.0, 12.0, n), np.zeros(n)], 1)
        self.mid = 0.5 * (self.beg + self.end) + np.stack([np.zeros(n), r.uniform(4.0, 9.0, n), np.zeros(n)], 1)
        self.dur = r.uniform(1.0, 1.6, n)
        self.seed = r.random(n)

    def sample(self, t):
        k = proc_k(t)
        if k <= 0.0 or t < GROW_S.min() - 2.0 or t > GROW_S.max() + 0.2:
            return None
        u = (t - (GROW_S - self.dur)) / self.dur
        on = (u > 0.0) & (u < 1.0)
        if not on.any():
            return None
        uu = u[on][:, None]
        e = 1.0 - (1.0 - uu) ** 1.6
        drift = _v(0.0, 0.0, -WALK)[None, :] * (t - GROW_S[on])[:, None]      # their place walks on with everyone
        b, m, d = self.beg[on], self.mid[on], self.end[on]

        def at(x):
            return (1 - x) ** 2 * b + 2 * x * (1 - x) * m + x * x * d + drift
        p, q = at(e), at(np.maximum(e - 0.04, 0.0))
        a = np.clip(uu[:, 0] / 0.15, 0.0, 1.0) * (0.5 + 0.7 * uu[:, 0]) * k * (1.0 - 0.6 * _mfx()._reading(t))
        col = lin("#fff0d6")
        return [dict(pos=p, pos2=q, size=0.06, color=col, alpha=0.3 * a, emit=2.2, kind="line", reflect=False),
                dict(pos=p, size=0.9, color=col, alpha=0.12 * a, emit=1.8, kind="soft", reflect=False),
                dict(pos=p, size=0.3, color=col, alpha=0.9 * a, emit=3.2, kind="spark", seed=self.seed[on],
                     twinkle=0.4, reflect=False)]


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
                 + mx(t, strings=0.18, choir=0.12)                  # (round 8) her light breathes with the music
                 + 0.08 * held * np.sin(2.0 * np.pi * 0.45 * t) + 1.0 * g)
        s = self.s
        ang = 2 * np.pi * s[:, 0] + 0.35 * t * (0.5 + s[:, 1])
        rad = (1.2 + 3.4 * s[:, 2]) * (1.0 - 0.45 * g)
        halo = m[None, :] + np.stack([rad * np.cos(ang), 1.3 * (s[:, 3] - 0.5) * rad, rad * np.sin(ang)], 1)
        warm = lin("#ffe2b4")
        big = 1.0 + 1.2 * (1.0 - _sc(LAND - 0.6, LAND + 0.4, t))       # coming down she is a blazing star
        # (round 8, f29) through the gathering and the march (2:10 to 2:20) one soft distant light, not a glare
        soft = 1.0 - 0.55 * _win(t, 130.29, 141.5, 0.4, 0.6)
        k = k * soft * (0.35 if block_t0(t) == 154.2 else 1.0)    # (MARCH round 2) calm beside the arriving words
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

    def kings(t):            # (MARCH round 2) round the kings' feet as they walk, low, under the words
        a = a0 + 1.1 * t
        r = 4.6 + 0.6 * np.sin(0.7 * t + j)
        return _v(r * np.sin(a), 0.45 + 0.25 * np.sin(1.3 * t + j), _kz(t) + 1.6 * r * np.cos(a))

    def rise(t):             # (MARCH round 2) the crowns become comets streaming to the church's emblem
        return crown_path((j * 4 + j // 3) % K_N, t)      # nine different crowns

    def home(t):             # the held breath: drawn back into her light, spinning faster
        q = _sc(156.0, 160.4, t)
        m = mother_pos(t)
        a = a0 + 0.4 * (t - 156.0) + 9.0 * q * q
        r = 16.0 * (1.0 - q) ** 1.5 + 0.2
        return m + _v(r * np.sin(a), (7.0 + 1.5 * np.sin(1.1 * t + j)) * (1.0 - q),
                      -4.0 * (1.0 - q) + r * np.cos(a))

    return dict(burst=burst, ring=ring, march=march, weave=weave, dive=dive, kings=kings, rise=rise,
                home=home)[phase]


# (phase, t0, t1, brightness, trail, fade out)
COMET_PHASES = [("burst", LAND, 130.29, 1.0, 1.4, 0.05), ("ring", 130.29, 134.54, 0.8, 1.6, 0.05),
                ("march", 134.54, 135.5, 0.8, 0.8, 0.3), ("weave", 141.5, 144.4, 1.0, 1.2, 0.05),
                ("dive", 144.4, 148.6, 1.1, 0.9, 0.05),
                ("rise", 156.0, CROWN_HOME + 0.1, 0.55, 0.9, 0.3)]     # (from the cut: never by the lens)   # (MARCH round 2: no "home" comets)


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
        if t > 159.0 and block_t0(t) != 156.0:          # (MARCH round 2) not over the view of the church
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
    """(MARCH round 2) Crowns of gold light on the kings' heads: a jewelled band (jewels in the nine colours), eight
    points with pearls, four arches meeting over an orb (no cross). They follow each head as the kings walk and
    kneel; as the kings go down the crowns are laid on the sea before them (2:34.75), and on 2:35.34 they rise,
    blaze, and stream away over the sea and up Mount Zion into the church's emblem (crown_path)."""

    def __init__(self, walking, kneeling):
        self.wk, self.kn = walking, kneeling
        r = np.random.default_rng(81)
        R = 0.135
        a = np.linspace(0, 2 * np.pi, 72, endpoint=False)
        ring = np.stack([R * np.cos(a), np.zeros(72), R * np.sin(a)], 1)
        parts, tips, jew, jc = [ring, ring + _v(0, 0.05, 0), 1.04 * ring + _v(0, 0.025, 0)], [], [], []
        for k in range(8):
            b = 2 * np.pi * k / 8
            base = _v(R * np.cos(b), 0.05, R * np.sin(b))
            top = _v(1.18 * R * np.cos(b), 0.15, 1.18 * R * np.sin(b))
            for c in (b - 0.2, b + 0.2):                       # each point a little gable of light
                parts.append(_seg(_v(R * np.cos(c), 0.05, R * np.sin(c)), top, 0.012))
            tips.append(top + _v(0, 0.012, 0))
            c = b + np.pi / 8                                  # a jewel on the band between the points
            jew.append(_v(1.05 * R * np.cos(c), 0.025, 1.05 * R * np.sin(c)))
            jc.append(lin(COL9[k % 9]))
        for k in range(4):                                     # the arches, meeting over the orb
            b = 2 * np.pi * k / 4 + np.pi / 8
            v = np.linspace(0.0, 1.0, 22)
            rr = R * np.cos(0.5 * np.pi * v)
            parts.append(np.stack([rr * np.cos(b), 0.05 + 0.2 * np.sin(0.5 * np.pi * v), rr * np.sin(b)], 1))
        o = r.normal(0.0, 1.0, (40, 3))
        orb = 0.028 * o / np.linalg.norm(o, axis=1, keepdims=True) + _v(0, 0.285, 0)
        self.C = np.concatenate(parts + [orb])
        self.T = np.asarray(tips)
        self.J, self.JC = np.asarray(jew), np.asarray(jc)
        self.s = r.random((K_N, len(self.C) + len(self.T) + len(self.J), 4))
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
            out.append(_v(Q[sel, 0].mean(), top - 0.07, Q[sel, 2].mean()))
        out = np.asarray(out)
        self.cache = (t, out)
        return out

    def _one(self, c, a, gold, pale, spin=0.0, grow=1.0, burst=0.0, s=None):
        cs, sn = np.cos(spin), np.sin(spin)

        def rot(X):
            X = X * grow
            return np.stack([X[:, 0] * cs + X[:, 2] * sn, X[:, 1], -X[:, 0] * sn + X[:, 2] * cs], 1)
        C, T, J = rot(self.C), rot(self.T), rot(self.J)
        if burst > 0.0 and s is not None:                      # breaking into sparks as it flies
            nC, nT = len(C), len(T)
            sp = (s[:, :3] - 0.5) * (1.6 * burst * (0.3 + s[:, 3:4]))
            C, T, J = C + sp[:nC], T + sp[nC:nC + nT], J + sp[nC + nT:]
        return [dict(pos=C + c, size=0.022, color=gold, alpha=a, emit=3.6, kind="spark", reflect=False),
                dict(pos=T + c, size=0.034, color=pale, alpha=a, emit=4.2, kind="spark", reflect=False),
                dict(pos=J + c, size=0.04, color=self.JC, alpha=a, emit=4.0, kind="spark", reflect=False),
                dict(pos=(c + _v(0, 0.12 * grow, 0))[None, :], size=0.45 * grow, color=gold, alpha=0.07 * a,
                     emit=2.0, kind="soft", reflect=False)]

    def sample(self, t):
        if proc_k(t) <= 0.0 or not (K_IN - 0.2 <= t < CROWN_HOME + 0.6):
            return None
        out = []
        gold, pale = lin(GOLD), lin("#fff1c8")
        beat = 1.0 + 0.25 * beat_pulse(t)
        if t < RISE:
            hd = self.heads(t)
            lay = _sc(LAY0, LAY1, t)
            for i, h in enumerate(hd):
                a = _sc(KING_T[i], KING_T[i] + 0.4, t) * beat * (1.0 + 0.8 * hit_pulse(t, [KNEEL], fall=0.5))
                c = h * (1 - lay) + crown_ground(i) * lay + _v(0.0, 0.35 * np.sin(np.pi * lay), 0.0)
                out += self._one(c, a, gold, pale)
            if t > RISE - 0.25:                                 # they glow on the sea just before they rise
                f = _sc(RISE - 0.25, RISE, t)
                P = np.asarray([crown_ground(i) for i in range(K_N)]) + _v(0.0, 0.08, 0.0)
                out.append(dict(pos=P, size=0.9, color=gold, alpha=0.3 * f, emit=2.2, kind="soft", reflect=False))
            return out
        u = t - RISE
        f = _sc(0.0, 0.05, u) * (1.0 - _sc(CROWN_LIFT + CROWN_FLY - 0.15, CROWN_LIFT + CROWN_FLY + 0.4, u))
        blaze = 1.0 + 1.2 * hit_pulse(t, [RISE], fall=0.5)
        q = _sc(0.6, 1.8, u)
        for i in range(K_N):
            c = crown_path(i, t)
            out += self._one(c, f * blaze, gold * (1.0 - 0.5 * q) + pale * (0.5 * q), pale, spin=3.0 * u,
                             grow=1.0 + 1.5 * _sc(0.0, 0.5, u) + 9.0 * _sc(CROWN_LIFT, CROWN_LIFT + CROWN_FLY, u),
                             burst=q, s=self.s[i])     # (larger as they fly, so they read far over the sea)
        g = np.exp(-u / 0.35)                                   # the flash where they leave the sea
        P = np.asarray([crown_ground(i) for i in range(K_N)]) + _v(0.0, 0.2, 0.0)
        out.append(dict(pos=P, size=1.0, color=gold, alpha=0.35 * g, emit=2.2, kind="soft", reflect=False))
        return out


class KingTrains:
    """(MARCH round 2) The kings' robes of state: from each king's shoulders a mantle of light falls down the back
    and spreads behind them on the sea as a long train, each in its royal colour, edged and embroidered in gold,
    rippling as they walk; when they kneel it lies spread on the sea behind them."""

    NS, NW, L = 44, 13, 3.6

    def __init__(self):
        s = np.linspace(0.0, 1.0, self.NS)
        w = np.linspace(-1.0, 1.0, self.NW)
        S, W = np.meshgrid(s, w, indexing="ij")
        self.S, self.W = S.ravel(), W.ravel()
        edge = (np.abs(self.W) > 0.95) | (self.S > 0.985)
        row = np.round(self.S * (self.NS - 1)).astype(int)
        col = np.round((self.W + 1.0) * 0.5 * (self.NW - 1)).astype(int)
        emb = (~edge) & (row % 5 == 2) & (col % 3 == 0) & (row > 8)          # a lattice of gold embroidery
        self.edge, self.emb, self.field = edge, emb, ~(edge | emb)
        self.seed = np.random.default_rng(84).random(len(self.S))
        self.col = [lin(K_COL[(i // 2 + i % 2 * 3) % len(K_COL)]) for i in range(K_N)]
        # (MARCH) the cloth's points scattered within their cells, so the train glows like cloth, not a grid of lamps
        jr = np.random.default_rng(85)
        f = self.field
        self.S = self.S + f * jr.uniform(-0.45, 0.45, len(self.S)) / (self.NS - 1)
        self.W = self.W + f * jr.uniform(-0.45, 0.45, len(self.W)) * 2.0 / (self.NW - 1)

    def _shape(self, i, t):
        """World points of king i's mantle and train."""
        base = king_base(i, t)
        kneel = _sc(KNEEL, KNEEL + 0.3, t)
        sh = KING_SCALE * (1.42 - 0.42 * kneel)                 # the shoulders (lower when kneeling)
        S, W = self.S, self.W
        d = 0.3                                                 # the drape reaches the sea at S = d
        hang = np.clip(S / d, 0.0, 1.0)
        y = sh * (1.0 - hang ** 1.6) + 0.03
        back = 0.16 + 0.32 * hang + np.clip((S - d) / (1.0 - d), 0.0, 1.0) * self.L * (1.0 + 0.12 * kneel)
        half = 0.22 + 0.4 * hang + 0.45 * np.clip((S - d) / (1.0 - d), 0.0, 1.0) * (1.0 + 0.25 * kneel)
        walking = 1.0 - kneel
        on = S > d
        y = y + on * (0.035 * walking * np.sin(9.0 * S - 7.0 * t) + 0.01)
        x = W * half + on * 0.05 * walking * np.sin(6.0 * S - 5.0 * t + i)
        return np.stack([base[0] + x, y, base[2] + back], 1)    # they walk toward -z, so the train lies at +z

    def sample(self, t):
        if proc_k(t) <= 0.0 or not (K_IN - 0.1 <= t < 160.6):
            return None
        out = []
        gold = lin(GOLD)
        beat = 1.0 + 0.2 * beat_pulse(t)
        k = proc_k(t) * beat * (1.0 + 0.5 * hit_pulse(t, [KNEEL, RISE], fall=0.5))
        for i in range(K_N):
            a = _sc(KING_T[i], KING_T[i] + 0.45, t) * k
            if a <= 0.0:
                continue
            P = self._shape(i, t)
            grow = _sc(KING_T[i], KING_T[i] + 0.6, t)            # the train unrolls behind the king as they appear
            vis = self.S <= grow + 1e-6
            f, e, m = self.field & vis, self.edge & vis, self.emb & vis
            out.append(dict(pos=P[f], size=0.11, color=self.col[i], alpha=0.3 * a, emit=1.8, kind="soft",
                            reflect=False))
            out.append(dict(pos=P[f][::3], size=0.022, color=self.col[i] * 0.6 + lin(WHITE) * 0.4, alpha=0.6 * a,
                            emit=2.4, kind="spark", twinkle=0.5, seed=self.seed[f][::3], reflect=False))
            out.append(dict(pos=P[e], size=0.03, color=gold, alpha=0.95 * a, emit=3.4, kind="spark", reflect=False))
            out.append(dict(pos=P[m], size=0.026, color=lin("#ffe6a8"), alpha=0.8 * a, emit=3.0, kind="spark",
                            twinkle=0.3, seed=self.seed[m], reflect=False))
            b = king_base(i, t)                                 # a pool of gold light under each king
            out.append(dict(pos=_v(b[0], 0.05, b[2] + 0.3)[None, :], size=1.2, color=gold, alpha=0.04 * a,
                            emit=1.8, kind="soft", reflect=False))
        return out


class EmblemArrive:
    """(MARCH round 2, Anthony: "the main church from Korea should be shown and the church logo. Not that church
    outline in the sky.") The real church of light on Mount Zion (s11_church, read only) answers the march: its
    traced emblem (emblem_batches) and white lines glow brighter as the crowns stream to it, flare as they arrive
    (2:38.6), and blaze on the beat as the camera flies into it for slam 2. Calm (no flare) while the words read
    above it."""

    def __init__(self):
        self.emb = CH.emblem_batches()
        self.crisp = CH.Church("crisp").b
        self.c = _emblem_c()[None, :] + np.array([[0.0, 0.0, 0.4]])

    def gain(self, t):
        b = block_t0(t)
        if b not in (154.2, 156.0, 161.7) or proc_k(t) <= 0.0:
            return 0.0
        calm = 1.0 - 0.5 * _win(t, 154.9, 160.3, 0.4, 0.6)       # the words read just above the church
        k = 0.35 + 0.5 * _sc(RISE, CROWN_HOME, t) + 0.9 * hit_pulse(t, [CROWN_HOME], fall=1.0) * calm
        if b == 161.7:
            k = 1.1 + 0.6 * _sc(161.7, 162.86, t) + 0.35 * beat_pulse(t)
        return k * (1.0 + 0.2 * beat_pulse(t) * calm)

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.0:
            return None
        out = []
        for b in self.emb:
            d = dict(b)
            d["alpha"] = b["alpha"] * (0.6 * g)
            d["reflect"] = False
            out.append(d)
        for b in self.crisp:
            d = dict(b)
            d["alpha"] = b["alpha"] * (0.1 * g)
            d["reflect"] = False
            out.append(d)
        out.append(dict(pos=self.c, size=CH.EMBLEM_SIZE * 2.2, color=lin("#5fb0ff"), alpha=0.10 * g, kind="soft",
                        emit=1.4, fog=0.3, reflect=False))
        return out


class KingBeams:
    """The kings' pillars of light (2:34): narrow bright beams falling from the sky beside the kneeling kings
    (two on each side of them, never over the whole view), with a small pool where each lands; they pulse
    with the beat and burst on the two kings' hits. No wide glow, so the low view stays clear."""

    BASES = np.asarray([(-4.3, -67.0), (-4.3, -60.5), (4.3, -67.0), (-4.3, -55.0)])   # beside the kings, clear of the lens

    def __init__(self):
        self.u = np.linspace(0.0, 1.0, 900) ** 1.8      # dense low down: a solid beam, not a dotted line
        self.col = lin("#ffe9c4")
        self.ph = np.random.default_rng(83).random(len(self.BASES))

    def gain(self, t):
        # (round 8) they fall only once "All kings worship You" has left (gone 154.55), so they never cross it
        return proc_k(t) * _sc(154.5, 154.75, t) * (1.0 - _sc(155.0, 155.25, t))   # gone before "to the great Church"

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.0:
            return None
        k = g * (0.85 + 0.35 * beat_pulse(t) + 0.6 * hit_pulse(t, [KNEEL, RISE], fall=0.35))
        out = []
        top = 60.0
        for i, (x, z) in enumerate(self.BASES):
            fall = _sc(154.5 + 0.06 * i, 154.75 + 0.06 * i, t)       # each beam falls from the sky in turn
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
            kk = k * (1.0 + mx(t, kick=0.6))                          # (round 8) the steps land harder on the kick
            out.append(dict(pos=P, size=0.09 + 0.05 * (1.0 - land), color=col, alpha=min(0.9 * land * kk, 1.0), emit=3.0,
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
        # (round 8, f29) from overhead the path runs straight up through "This hope was engraved" (2:14.5): it
        # calms to a faint trace while those words read
        a = a * (1.0 - 0.8 * _win(t, 134.7, 138.9, 0.4, 0.6) * (block_t0(t) == 134.54))
        a = a * (0.45 if block_t0(t) == 141.5 else 1.0)       # (MARCH round 1) walking in the aisle: a calm path
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


# ---------------------------------------------------------------------------------------------------------
# (MARCH round 3, Anthony: "add flag bearers from many different nations marching with the crowds.")
# ---------------------------------------------------------------------------------------------------------
_FW, _FH = 1.5, 1.0            # a flag's size (metres): u runs from the pole (0) to the fly (1), v from the top (0)


def _disc(u, v, cu, cv, r):
    return ((u - cu) * _FW) ** 2 + ((v - cv) * _FH) ** 2 < r * r


def _flag_korea(u, v):
    s = 0.5 + 0.06 * np.sin((u - 0.5) * _FW / 0.25 * np.pi)           # the taegeuk: red over blue in an S
    d1, d2 = (u - 0.5) * _FW + (v - 0.5) * _FH, (u - 0.5) * _FW - (v - 0.5) * _FH
    bars = ((np.abs(d1) > 0.38) & (np.abs(d1) < 0.55) & (np.abs(d2) < 0.16)) | \
           ((np.abs(d2) > 0.38) & (np.abs(d2) < 0.55) & (np.abs(d1) < 0.16))
    return np.where(_disc(u, v, 0.5, 0.5, 0.25), np.where(v < s, 0, 1), np.where(bars, -1, 2))   # trigrams dark


def _flag_usa(u, v):
    canton = (u < 0.4) & (v < 7 / 13)
    star = canton & (np.round(u * 14) % 2 == 0) & (np.round(v * 18) % 2 == 0)
    stripe = (np.floor(v * 13) % 2 == 0)
    return np.where(canton, np.where(star, 2, 1), np.where(stripe, 0, 2))


def _flag_uk(u, v):
    x, y = (u - 0.5) * 2.0, (v - 0.5) * 2.0
    diag = (np.abs(x * 0.667 - y) < 0.2) | (np.abs(x * 0.667 + y) < 0.2)
    cross_w = (np.abs(x) < 0.2) | (np.abs(y) < 0.3)
    cross_r = (np.abs(x) < 0.12) | (np.abs(y) < 0.18)
    return np.where(cross_r, 0, np.where(cross_w | diag, 2, 1))


def _flag_brazil(u, v):
    x, y = (u - 0.5) * 2.0, (v - 0.5) * 2.0
    return np.where(x * x + y * y * 2.25 < 0.25, 1, np.where(np.abs(x) * 0.85 + np.abs(y) < 0.85, 3, 4))


def _flag_philippines(u, v):
    tri = u * _FW < 0.866 * (1.0 - np.abs(v - 0.5) * 2.0) * _FH
    sun = _disc(u, v, 0.18, 0.5, 0.1)
    return np.where(sun & tri, 3, np.where(tri, 2, np.where(v < 0.5, 1, 0)))


def _flag_canada(u, v):
    leaf = _disc(u, v, 0.5, 0.52, 0.22) & ~(_disc(u, v, 0.5, 0.95, 0.2))
    return np.where((u < 0.25) | (u > 0.75) | leaf, 0, 2)


def _flag_india(u, v):
    ring = np.abs(np.sqrt(((u - 0.5) * _FW) ** 2 + ((v - 0.5) * _FH) ** 2) - 0.13) < 0.025
    return np.where(ring, 1, np.where(v < 1 / 3, 5, np.where(v < 2 / 3, 2, 4)))


def _tri(a, b, c, vertical=True):
    def f(u, v):
        w = u if vertical else v
        return np.where(w < 1 / 3, a, np.where(w < 2 / 3, b, c))
    return f


def _flag_japan(u, v):
    return np.where(_disc(u, v, 0.5, 0.5, 0.3), 0, 2)


def _flag_argentina(u, v):
    return np.where(_disc(u, v, 0.5, 0.5, 0.1), 3, np.where(np.abs(v - 0.5) < 1 / 6, 2, 6))


def _flag_colombia(u, v):
    return np.where(v < 0.5, 3, np.where(v < 0.75, 1, 0))


def _flag_spain(u, v):
    return np.where(np.abs(v - 0.5) < 0.25, 3, 0)


def _flag_ghana(u, v):
    x, y = (u - 0.5) * _FW, (v - 0.5) * _FH
    star = (np.abs(x) < 0.12) & (np.abs(y) < 0.12) & (np.abs(x) + np.abs(y) < 0.15)
    return np.where(star, -1, np.where(v < 1 / 3, 0, np.where(v < 2 / 3, 3, 4)))


# palette: 0 red, 1 blue, 2 white, 3 gold, 4 green, 5 saffron, 6 sky blue; -1 dark (no light)
FLAG_PAL = ["#ff4a5e", "#3f6dff", "#fff6ec", "#ffd24a", "#2fd47a", "#ff9a3c", "#7cc4ff"]
FLAGS = [_flag_korea, _flag_usa, _flag_brazil, _flag_philippines, _flag_india, _flag_uk, _flag_japan,
         _tri(1, 2, 0), _tri(4, 2, 0), _flag_canada, _tri(-1, 0, 3, False), _flag_argentina, _tri(4, 2, 4),
         _flag_colombia, _tri(0, 2, 1, False), _flag_spain, _flag_ghana, _tri(0, 2, 0), _tri(4, 2, 0)]
# (France, Italy, Germany, Nigeria, Netherlands, Peru, Mexico among the tricolours)


def _bearers():
    """Who carries a flag: people of the procession a row or two in from the aisle, spread from front to back,
    and the first person of each nation's stream (who leads it in)."""
    out = []
    zr = PROC_P[:, 2] - MOTHER_Z0
    for k, z in enumerate(np.arange(7.0, 98.0, 4.3)):
        for side in (-1.0, 1.0):
            want_x = side * (AISLE + 1.75 * (1 + (k + (side > 0)) % 4))
            i = int(np.argmin(np.abs(zr - z - 0.9 * side) * 2.0 + np.abs(PROC_P[:, 0] - want_x)))
            out.append(("walk", i))
    return out


class FlagBearers:
    """Flag bearers of light marching with the crowds, each flag in a nation's colours (simple, recognisable
    patterns drawn in light), on a pole of light, waving with the march beat and the strings. They step back
    near the lens while a phrase reads, so nothing bright crosses the words."""
    wants_camera = True
    NU, NV = 30, 20

    def __init__(self, walkers, nations, joined_at):
        self.w, self.nat, self.jt = walkers, nations, joined_at
        u, v = np.meshgrid(np.linspace(0.0, 1.0, self.NU), np.linspace(0.0, 1.0, self.NV), indexing="ij")
        self.u, self.v = u.ravel(), v.ravel()
        pal = np.asarray([lin(c) for c in FLAG_PAL])
        self.who = _bearers()
        # the leader of each nation's stream (the one nearest the procession) carries its flag too
        lead = []
        for c in np.unique(NAT_C):                                # each stream has its own colour
            ii = np.where(NAT_C == c)[0]
            if len(ii):
                lead.append(("nation", int(ii[np.argmin(NAT_J[ii])])))
        self.who += lead
        self.cols, self.lit = [], []
        for k in range(len(self.who)):
            idx = np.asarray(FLAGS[k % len(FLAGS)](self.u, self.v))
            idx = np.broadcast_to(idx, self.u.shape)
            self.lit.append(idx >= 0)
            self.cols.append(pal[np.maximum(idx, 0)])
        self.edge = (self.u < 0.02) | (self.u > 0.98) | (self.v < 0.03) | (self.v > 0.97)
        self.seed = np.random.default_rng(91).random(len(self.u))
        self.pole = np.linspace(0.0, 1.0, 40)

    def _where(self, kind, i, t):
        """Feet of bearer i (world) at t, and the walking direction."""
        if kind == "walk":
            w = self.w
            return w.place[i] + _ahead(w)[i] * WALK * max(min(t, HALT) - MARCH, 0.0), _ahead(w)[i]
        n = self.nat
        d = _ahead(n)[i]
        j = float(NAT_J[i])
        if t < j:
            return n.place[i] + d * WALK * max(t - MARCH + 0.1, 0.0), d
        p = n.place[i] + d * WALK * (j - MARCH + 0.1)
        return p + _v(0.0, 0.0, -1.0) * WALK * max(min(t, HALT) - j, 0.0), _v(0.0, 0.0, -1.0)

    def sample(self, t, cam=None):
        k = proc_k(t) * _sc(MARCH - 0.2, MARCH + 0.4, t)
        if k <= 0.0:
            return None
        MF = _mfx()
        read = MF._reading(t)
        wave_amp = (0.10 + 0.06 * mx(t, strings=1.0)) * (1.0 - 0.6 * _sc(HALT, HALT + 1.0, t))
        bp = _beat_phase(t)
        out = []
        for n, (kind, i) in enumerate(self.who):
            if kind == "nation" and t < MARCH - 0.1:
                continue
            p, d = self._where(kind, i, t)
            right = _v(-d[2], 0.0, d[0])
            back = -d
            bob = 0.04 * abs(np.sin(np.pi * bp))                # the pole lifts a little with each step
            base = p + right * 0.3 + _v(0.0, 0.9 + bob, 0.0)
            top = base + _v(0.0, 2.75, 0.0)
            near = 1.0
            if cam is not None and read > 0.0:                  # step back near the lens while words read
                dist = float(np.linalg.norm(top - np.asarray(cam.pos)))
                near = 1.0 - read * (1.0 - float(np.clip((dist - 7.0) / 6.0, 0.0, 1.0)))
            a = k * near * (1.0 - 0.5 * read) * (1.0 + 0.25 * beat_pulse(t))     # calm behind the words
            if a <= 0.01:
                continue
            ph = 2.0 * np.pi * (self.u * 1.1 - 1.25 * t) + n
            off = wave_amp * self.u * np.sin(ph)
            P = (top[None, :] + back[None, :] * (self.u * _FW)[:, None] - _v(0.0, 1.0, 0.0)[None, :] * (self.v * _FH)[:, None]
                 + right[None, :] * off[:, None] - _v(0.0, 1.0, 0.0)[None, :] * (0.08 * self.u ** 2)[:, None])
            lit = self.lit[n]
            col = self.cols[n]
            shade = 0.8 + 0.35 * np.cos(ph)[lit]                # the folds catch the light as it waves
            out.append(dict(pos=P[lit], size=0.075, color=col[lit] * shade[:, None], alpha=0.5 * a, emit=1.9,
                            kind="soft", reflect=False))
            sel = lit & ((np.arange(len(self.u)) % 3 == 0) | self.edge)
            out.append(dict(pos=P[sel], size=0.022, color=col[sel] * 0.6 + lin(WHITE) * 0.4, alpha=0.75 * a,
                            emit=2.6, kind="spark", twinkle=0.4, seed=self.seed[sel], reflect=False))
            pole = base[None, :] + (top - base)[None, :] * self.pole[:, None]
            out.append(dict(pos=pole, size=0.025, color=lin(GOLD), alpha=0.9 * a, emit=3.0, kind="spark",
                            reflect=False))
            out.append(dict(pos=(top + _v(0.0, 0.06, 0.0))[None, :], size=0.07, color=lin("#fff1c8"), alpha=a,
                            emit=4.0, kind="spark", reflect=False))
        return out or None


def _mfx():
    import songs.s11_music_fx as MF
    return MF


def ray_k(t):
    """How strongly her rays fan out (gentle while words are on screen, so they never burn through them)."""
    b = block_t0(t)
    if b is None:
        return 0.0
    if b == 125.92:
        return 1.8 - 0.6 * _sc(LAND, 129.0, t) + 0.9 * hit_pulse(t, [LAND], fall=1.2)
    if b == 130.29:
        return 0.25                                              # (f29) no hard beams over the gathering
    if b == 134.54:
        return 0.12 + 0.25 * hit_pulse(t, [MARCH], fall=0.5)    # (f29) the words arrive over it: barely any
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


def _toward_mother(crowd, deg=None):
    """Everyone faces exactly the way they walk, toward her light: the engine gives each person a random turn of
    up to 6 degrees, which over the march made the close views look like people walking every way."""
    f = np.full(crowd.n, 180.0) if deg is None else np.broadcast_to(np.asarray(deg, np.float64), (crowd.n,))
    crowd.facing[:] = np.radians(f)
    return crowd


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
    _toward_mother(walkers)
    wait.facing[:] = walkers.facing
    held = WaveCrowd(waves=[(159.4, 1.4, 6.0, 0.6, 0.6)], delay=back, gain=crowd_k,
                     places=PROC_P + _ahead(walkers) * walked(HALT), facing=180.0,
                     kinds=(("raise", 2.0), ("open", 1.0)), start=HALT - 0.3, fade=0.3, flash=0.0, **look)
    held.facing[:] = walkers.facing
    # the nations joining from the sides, each in its own colour (clothed in light, the same bodies as everyone)
    nations = GCrowd(gain=crowd_k, places=NAT_P, facing=NAT_F, kinds=("walk",), start=MARCH - 0.1, walk=WALK,
                     until=np.minimum(NAT_J, HALT), fade=0.45, flash=1.2, **look)
    _toward_mother(nations, NAT_F)
    _tint_nations(nations)
    gone = NAT_J < HALT                       # those still on their way at the held breath stand still there
    still = NAT_P[~gone] + _ahead(nations)[~gone] * walked(HALT)
    nat_held = WaveCrowd(waves=[(159.4, 1.4, 6.0, 0.6, 0.6)], delay=np.full(len(still), 0.5), gain=crowd_k,
                         places=still, facing=NAT_F[~gone], kinds=(("raise", 2.0), ("open", 1.0)), start=HALT - 0.3,
                         fade=0.3, flash=0.0, **look)
    _toward_mother(nat_held, NAT_F[~gone])
    _tint_nations(nat_held, NAT_C[~gone])
    scene.add("proc nations", nations, reflect=False)
    scene.add("proc nations held", nat_held, reflect=False)
    # round 7: more nations come in from both sides later in the march (each in its own colour)
    late = GCrowd(gain=crowd_k, places=LATE_P, facing=LATE_F, kinds=("walk",), start=LATE_T0 - 0.2, walk=WALK,
                  until=np.minimum(LATE_J, HALT), fade=0.6, flash=1.4, **look)
    _toward_mother(late, LATE_F)
    _tint_nations(late, LATE_C)
    lgone = LATE_J < HALT
    lstill = LATE_P[~lgone] + _ahead(late)[~lgone] * (WALK * (HALT - LATE_T0[~lgone]))[:, None]
    late_held = WaveCrowd(waves=[(159.4, 1.4, 6.0, 0.6, 0.6)], delay=np.full(len(lstill), 0.5), gain=crowd_k,
                          places=lstill, facing=LATE_F[~lgone], kinds=(("raise", 2.0), ("open", 1.0)),
                          start=HALT - 0.3, fade=0.3, flash=0.0, **look)
    _toward_mother(late_held, LATE_F[~lgone])
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
    _toward_mother(joined)
    jheld.facing[:] = joined.facing
    _tint_nations(jheld, JC)
    scene.add("proc joined", joined, reflect=False)
    scene.add("proc joined held", jheld, reflect=False)
    grow = GCrowd(gain=crowd_k, places=GROW_P, facing=180.0, kinds=("walk",), start=GROW_S, walk=WALK, until=HALT,
                  fade=0.35, flash=1.3, **dict(look, points=330))
    _toward_mother(grow)
    ghold = WaveCrowd(waves=[(159.4, 1.4, 6.0, 0.6, 0.6)], delay=np.full(len(GROW_P), 0.5), gain=crowd_k,
                      places=GROW_P + _ahead(grow) * (WALK * (HALT - GROW_S))[:, None], facing=180.0,
                      kinds=(("raise", 2.0), ("open", 1.0)), start=HALT - 0.3, fade=0.3, flash=0.0,
                      **dict(look, points=330))
    ghold.facing[:] = grow.facing
    scene.add("proc growing", grow, reflect=False)
    scene.add("proc growing held", ghold, reflect=False)
    scene.add("proc growing sparks", GrowSparks())
    scene.add("march beat", MarchBeat([walkers, nations, late, joined, grow]))
    scene.add("flag bearers", FlagBearers(walkers, nations, NAT_J))
    scene.add("procession wait", wait, reflect=False)
    scene.add("procession", walkers, reflect=False)
    scene.add("procession held", held, reflect=False)
    scene.add("fulfil hearts", FulfilHearts(walkers))
    scene.add("colour ripples", Ripples(walkers))
    # (MARCH round 2) twelve kings, larger than life and drawn in finer light, appearing pair by pair on the beat
    king = dict(people=dict(man=1.0), color="#ffd27a", color2=GOLD2, bright=4.4, points=5200, seed=31.0,
                scale=KING_SCALE, dof=0.25)
    kings_w = _robed(GCrowd(gain=crowd_k, places=KINGS_P, facing=180.0, kinds=("walk",), start=KING_T, walk=WALK,
                            until=K_STOP, fade=0.25, flash=1.0, **king))
    kings_k = _robed(GCrowd(gain=crowd_k, places=KINGS_STOP, facing=180.0, kinds=("kneel",), start=K_STOP - 0.25,
                            act=dict(t=KNEEL, dur=0.3), fade=0.25, flash=0.0, **king))
    scene.add("kings", kings_w, reflect=False)
    scene.add("kings kneel", kings_k, reflect=False)
    scene.add("crowns", Crowns(kings_w, kings_k))
    scene.add("king trains", KingTrains())
    for ph, a, b, br, tr, fo in COMET_PHASES:
        for j in range(9):
            c = Comet(_comet_head(j, ph), COL9[j], a, b, trail=tr, width=dict(march=0.7, burst=0.55, rise=1.4).get(ph, 0.32),
                      bright=br, fade=0.05,
                      light=False, seed=j + 11.0 * len(ph))
            few = 0.0 if (ph in ("ring", "march") and j not in (1, 4, 7)) else 1.0     # (f29) three loops only
            c.k = (lambda c_, a_, b_, fo_, f_: lambda t: f_ * _sc(a_, a_ + 0.05, t) * (1.0 - _sc(b_ - fo_, b_, t))
                   * (proc_k(t) > 0.0))(c, a, b, fo, few)
            scene.add(f"comet {ph} {j}", c, reflect=True)
            if j in (0, 5):
                add_light(c.head, COL9[j], (lambda c_: lambda t: 0.08 * c_.k(t))(c), radius=4.0)
    sky = lambda a_, b_: (lambda t: proc_k(t) * _sc(a_ - 0.01, a_, t) * (1.0 - _sc(b_, b_ + 0.01, t)))  # noqa: E731
    for i, c in enumerate([(-55.0, 40.0, -85.0), (55.0, 40.0, -85.0)]):     # clouds parting round her light
        scene.add(f"proc parting cloud {i}", CloudBank(c, size=(50.0, 30.0, 60.0), puffs=20, seed=40 + i,
                                                       gain=sky(125.92, 130.29), bright=0.35), reflect=True)
    # (round 6: no canyon of cloud over the march any more; it hazed the words and the low views of the walkers)
    scene.add("kings beams", KingBeams())
    scene.add("church emblem", EmblemArrive())
    add_rays(mother_pos, lambda t: proc_k(t) * ray_k(t), color="#fff1d8", size=0.6)
    add_light(mother_pos, "#ffe8c8", lambda t: 0.15 * proc_k(t) * (1.0 + 0.5 * hit_pulse(t, KICKS + FULFIL, fall=0.5)),
              radius=9.0)
