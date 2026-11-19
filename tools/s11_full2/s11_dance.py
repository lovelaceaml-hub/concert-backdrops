"""Song 11 v2: dancers of light with ribbons of light (round 5), after the promo's dancer (Film 10, 0:19.85):
a figure of light turning on the black mirror, leading a ribbon of light from her hand like a gymnast's ribbon.

Owned by the dance thread. Imported by tools/s11_full2/s11_full2.py (the core) beside the other threads: the
core's music, places and helpers come in by the star import. Camera shots: SHOTS below (one per EDIT block the
dance thread owns, exact times). Point sets: add(scene). No em dash or en dash anywhere in this file.

The dancers' floor is the mirror sea in front of Mount Zion (DANCE_C), with the city of light behind them in
the mist. The moments:
  1:37.70  THE RING: seven dancers turn in a ring, their ribbons (the campaign colours) braid into one spiral
           that climbs to the sky, into "sacrifice" (1:39.4).
  1:57.00  THE BREATH: one dancer alone, slow and graceful, her long lavender ribbon drawing a slow spiral
           while light falls round her like snow.
  2:01.32  VERSE 2: the same dancer quickens; her ribbon flicks up on each pulse of the strings and on the beat.
  3:05.92  WONDROUS LOVE: two dancers face each other; their ribbons cross and draw a heart of light that
           stays between them, beating with the music.
  4:07.50  THE HELD BREATH: the lavender dancer again, almost still, her ribbon a slow halo round her while
           sparks gather into her; on the final rise it flies up and on like a comet.
Each dancer is whole and clothed in a dress of light (no facial features). Each ribbon has a white-hot core,
a coloured glow and sheds sparkles; its head is led by the dancer's hand.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403

DANCE_C = _v(0.0, 0.0, 160.0)          # the dancers' floor on the mirror sea (Zion's foot is 290 m beyond)
LAV = PW.COLORS["Compliment"]
WINDOWS = dict(ring=(97.7, 99.4), solo=(117.0, 125.92), heart=(185.92, 188.27), held=(247.5, 249.43))


def _bi(t):
    """The beat count at t (fractional): loops locked to the beat."""
    return float(np.interp(t, BEATS, np.arange(len(BEATS), dtype=np.float64)))


def _deep(hexs, k=1.3):
    c = lin(hexs)
    return np.clip(c * k - 0.15 * c.mean(), 0.0, 1.0)


# =========================================================================================================
# Shots (kind "local": the dancers on the sea, Zion behind them)
# =========================================================================================================
def _D(x, y, z):
    return DANCE_C + _v(x, y, z)


def _shot(name, t0, t1, fov, keys, ap=0.03, **kw):
    d = dict(name=name, kind="local", t0=t0, t1=t1, fov=fov, aperture=ap,
             keys=[(t0 + f * (t1 - t0), p, q) for f, p, q in keys], **kw)
    return d


SHOTS = [
    # the ring: low outside the ring, looking up as the braid climbs
    _shot("dance_ring", 97.7, 99.4, 54.0, [(0.0, _D(0.0, 1.2, 13.0), _D(0.0, 3.0, 0.0)),
                                           (1.0, _D(-3.0, 0.7, 10.5), _D(0.0, 7.5, 0.0))], roll=(3.0, -3.0)),
    # the breath: a slow circling drift close to her
    _shot("dance_breath", 117.0, 121.32, 40.0, [(0.0, _D(4.6, 1.5, 6.0), _D(0.0, 1.5, 0.0)),
                                                (0.5, _D(1.8, 1.25, 6.6), _D(0.0, 1.45, 0.0)),
                                                (1.0, _D(-1.4, 1.1, 6.4), _D(0.0, 1.5, 0.0))], pace="linear"),
    # verse 2: wider, rising a little, the ribbon flicking up on the strings
    _shot("dance_strings", 121.32, 125.92, 46.0, [(0.0, _D(-6.5, 0.9, 7.0), _D(0.0, 1.9, 0.0)),
                                                  (1.0, _D(-2.5, 1.6, 8.4), _D(0.0, 2.1, 0.0))], roll=(-2.0, 1.0)),
    # wondrous love: straight on, the heart between them, low (the phrase reads above)
    _shot("dance_heart", 185.92, 188.27, 44.0, [(0.0, _D(0.0, 0.8, 10.6), _D(0.0, 3.7, 0.0)),
                                                (1.0, _D(0.0, 0.9, 9.6), _D(0.0, 3.6, 0.0))]),
    # the held breath: almost still, a slow push in, tilting up as the ribbon flies off
    _shot("dance_held", 247.5, 249.43, 42.0, [(0.0, _D(-2.0, 1.2, 6.8), _D(0.0, 1.5, 0.0)),
                                              (0.8, _D(-1.5, 1.2, 6.0), _D(0.0, 1.8, 0.0)),
                                              (1.0, _D(-1.4, 1.1, 5.9), _D(0.0, 2.6, 0.0))], pace="linear"),
]


def dance_k(t):
    """1 inside the dance blocks (the dancers exist only then)."""
    return 1.0 if shot_name(t).startswith("dance_") else 0.0


# =========================================================================================================
# The dancers (p3d Body: a woman in a dress of light, glitter look, dance motions)
# =========================================================================================================
_BODIES = {}


def _bodies():
    if _BODIES:
        return _BODIES
    from p3d.body import Body
    c = DANCE_C
    # the lavender dancer: the breath, verse 2, the held breath
    _BODIES["solo"] = Body(
        "woman", at=(c[0], c[2]), facing=[(116.8, 30.0), (121.32, 150.0), (125.92, 330.0)],
        motion=[(116.6, "dance_a", dict(speed=0.42)), (121.2, "dance_a", dict(speed=1.0))],
        garment="dress", hair=True, look="glitter", color=LAV, color2="#ffffff", points=70000, bright=BODY_BRIGHT, size=1.5,
        light=LIGHT_AT, show=(116.4, 126.2), fade=0.3, seed=6.0,
        effects=[dict(kind="shed", t=117.2)])
    _BODIES["held"] = Body(
        "woman", at=(c[0], c[2]), facing=[(247.3, 20.0), (249.6, 70.0)], motion=[(247.0, "dance_b", dict(speed=0.22))],
        garment="dress", hair=True, look="glitter", color=LAV, color2="#ffffff", points=70000, bright=BODY_BRIGHT, size=1.5,
        light=LIGHT_AT, show=(247.2, 249.9), fade=0.3, seed=6.0, effects=[dict(kind="shed", t=247.4)])
    # the two of the heart: rose and gold, face to face
    _BODIES["heartL"] = Body("woman", at=(c[0] - 1.6, c[2]), facing=[(185.5, 60.0), (188.3, 100.0)],
                             motion=[(185.4, "dance_b", dict(speed=0.8))], garment="dress", hair=True, look="glitter",
                             color=PW.COLORS["Inclusiveness"], color2="#ffffff", points=50000, bright=BODY_BRIGHT, size=1.5, light=LIGHT_AT,
                             show=(185.6, 188.6), fade=0.2, seed=11.0)
    _BODIES["heartR"] = Body("woman", at=(c[0] + 1.6, c[2]), facing=[(185.5, 300.0), (188.3, 260.0)],
                             motion=[(185.4, "dance_a", dict(speed=0.8))], garment="dress", hair=True, look="glitter",
                             color=PW.COLORS["Gratitude"], color2="#ffffff", points=50000, bright=BODY_BRIGHT, size=1.5, light=LIGHT_AT,
                             show=(185.6, 188.6), fade=0.2, seed=12.0)
    # the ring of seven: spinning, facing out a little
    for i in range(RING_N):
        a = 2.0 * np.pi * i / RING_N
        x, z = c[0] + RING_R * np.sin(a), c[2] + RING_R * np.cos(a)
        _BODIES["ring%d" % i] = Body("woman", at=(x, z), facing=np.degrees(a) + 90.0,
                                     motion=[(97.2, "spin" if i % 2 == 0 else "dance_a", dict(speed=1.0))],
                                     garment="dress", hair=i % 2 == 1, look="glitter", color=RING_COL[i],
                                     color2="#ffffff", points=16000, bright=BODY_BRIGHT, size=1.8, light=LIGHT_AT, show=(97.4, 99.7), fade=0.2,
                                     seed=20.0 + i)
    return _BODIES


RING_N = 7
BODY_BRIGHT = 5.0
LIGHT_AT = DANCE_C + _v(0.0, 4.0, 5.0)
HALO_COL = dict(solo=LAV, held=LAV, heartL=PW.COLORS["Inclusiveness"], heartR=PW.COLORS["Gratitude"])
RING_R = 4.2
RING_COL = [COL9[k] for k in (0, 2, 4, 6, 8, 1, 3)]


class Gate:
    """A body seen only in the dance blocks (it may live across several of them)."""
    wants_camera = True

    def __init__(self, body):
        self.b = body

    def sample(self, t, cam=None):
        if dance_k(t) <= 0.0:
            return []
        return self.b.sample(t, cam)

    def gain(self, t):
        return self.b.gain(t) * dance_k(t)


def _hand(name, t, side="R"):
    b = _bodies()[name]
    lo, hi = b.show
    return np.asarray(b.where(min(max(t, lo + 0.01), hi - 0.01), "palm." + side), np.float64)


# =========================================================================================================
# The ribbons' heads: led by the hand, drawing loops and spirals with the beat
# =========================================================================================================
def _solo_hand(t):
    return _hand("solo" if t < 200.0 else "held", t)


def _solo_head(t):
    h = _solo_hand(t)
    if t < 140.0:
        if t < 121.32:          # the breath: a slow wide spiral (no beat: the music is still)
            a = 1.15 * (t - 117.0)
            r = 1.25 + 0.25 * np.sin(0.7 * t)
            return h + _v(r * np.sin(a), 0.35 + 0.55 * np.sin(0.5 * a), r * np.cos(a))
        # verse 2: one loop each two beats, figure-of-eight, flicking up on the strings and the beat
        a = np.pi * _bi(t)
        flick = 2.2 * hit_pulse(t, STRINGS, rise=0.06, fall=0.5) + 0.45 * beat_pulse(t, 0.12)
        r = 1.35 + 0.3 * hit_pulse(t, STRINGS, fall=0.8)
        return h + _v(r * np.sin(a), 0.3 + 0.5 * np.sin(2.0 * a) + flick, r * np.cos(a))
    # the held breath: a slow halo round her, then up and away on the final rise
    a = 0.9 * (t - 247.5) + 1.0
    away = _ss(249.0, 249.43, t) * (t - 249.0)
    halo = _D(0.0, 1.9, 0.0) + _v(1.1 * np.sin(a), 0.25 * np.sin(2.0 * a), 1.1 * np.cos(a))
    return halo * (1.0 - float(_ss(248.9, 249.3, t))) + float(_ss(248.9, 249.3, t)) * (
        halo + _v(2.0 * away, 22.0 * away * (0.3 + away), -6.0 * away))


def _heart_curve(s):
    """The heart outline, s in 0..1 from the bottom point up the left lobe to the top dip (metres, x, y)."""
    th = np.pi * (1.0 - s)                  # pi (bottom) to 0 (top dip): the left half
    x = -16.0 * np.sin(th) ** 3
    y = 13.0 * np.cos(th) - 5.0 * np.cos(2 * th) - 2.0 * np.cos(3 * th) - np.cos(4 * th)
    return x * 0.07, y * 0.07


HEART_C = DANCE_C + _v(0.0, 2.85, 0.25)
HEART_T = (186.0, 187.15)                   # the heart is drawn in this time


def _heart_point(s, side):
    x, y = _heart_curve(s)
    return HEART_C + _v(side * x, y, 0.0)


def _heart_head(side):
    name = "heartL" if side < 0 else "heartR"

    def f(t):
        h = _hand(name, t, "R" if side < 0 else "L")
        s = float(np.clip((t - HEART_T[0]) / (HEART_T[1] - HEART_T[0]), 0.0, 1.0))
        s = s * s * (3.0 - 2.0 * s)
        if t < HEART_T[0]:              # before: a loop out from the hand toward the crossing point below
            a = np.pi * _bi(t) + (0.0 if side < 0 else np.pi)
            free = h + _v(0.9 * np.sin(a), 0.4 + 0.3 * np.cos(a), 0.9 * np.cos(a))
            w = float(_ss(HEART_T[0] - 0.5, HEART_T[0], t))
            return free * (1.0 - w) + _heart_point(0.0, side) * w
        if t <= HEART_T[1] + 0.05:
            return _heart_point(s, side)
        # after: back to the hand in slow loops round it
        a = np.pi * _bi(t) + (0.0 if side < 0 else np.pi)
        free = h + _v(0.8 * np.sin(a), 0.5 + 0.25 * np.cos(a), 0.8 * np.cos(a))
        w = float(_ss(HEART_T[1], HEART_T[1] + 0.6, t))
        return _heart_point(1.0, side) * (1.0 - w) + free * w
    return f


def _ring_head(i):
    a0 = 2.0 * np.pi * i / RING_N

    def f(t):
        h = _hand("ring%d" % i, t)
        u = float(np.clip((t - 97.7) / 1.7, 0.0, 1.0))
        # the braid: round the ring's axis, climbing and closing in; all seven meet in one spiral
        y = 1.6 + 30.0 * u ** 1.6
        r = RING_R * (1.0 - 0.9 * u ** 0.7) + 0.3
        a = a0 + 2.2 * np.pi * u + 0.6 * np.pi * (_bi(t) - _bi(97.7))
        braid = DANCE_C + _v(r * np.sin(a), y, r * np.cos(a))
        w = float(_ss(97.0, 97.7, t))
        return h * (1.0 - w) + braid * w
    return f


# =========================================================================================================
# A ribbon of light: a band that follows its head back in time and stays tied to the hand
# =========================================================================================================
class Ribbon:
    def __init__(self, head, hand, color, win, trail=1.2, width=0.16, n=70, seed=0, flick=None):
        self.head, self.hand, self.color, self.win = head, hand, color, win
        self.trail, self.width, self.n = trail, width, n
        r = np.random.default_rng(300 + seed)
        self.sp = r.random((160, 4))
        self.flick = flick

    def k(self, t):
        return max(_env(t, a, b, 0.25, 0.2) for a, b in self.win) * dance_k(t)

    def points(self, t):
        u = np.linspace(0.0, 1.0, self.n)
        P = np.array([self.head(t - self.trail * x) for x in u])
        if self.hand is not None:            # tied to the hand: the band leaves her palm and flies to the head
            h = self.hand(t)
            m = 12
            g = np.linspace(0.0, 1.0, m + 2)[1:-1, None]
            sag = _v(0.0, -0.12, 0.0) * np.sin(np.pi * g)
            tie = h[None, :] * (1.0 - g) + P[0][None, :] * g + sag
            P = np.concatenate([P[::-1], tie[::-1], h[None, :]])     # the free end first, the palm last
            P = P[::-1]
            v = np.concatenate([np.zeros(m + 1), u])                # 0 at the palm and the head, 1 at the free end
        else:
            v = u
        return P, v

    def sample(self, t):
        k = self.k(t)
        if k <= 0.0:
            return None
        P, v = self.points(t)
        c = lin(self.color)
        deep = _deep(self.color)
        core = 0.5 * c + 0.5 * lin(WHITE)
        pulse = 1.0 + 0.35 * beat_pulse(t) * intensity(t) + 0.6 * hit_pulse(t, KICKS, fall=0.4)
        kk = 1.0 - v
        w = self.width
        out = [ribbon(P, width=w * 2.2 * (0.15 + 0.85 * kk), color=c, alpha=k * 0.16 * np.clip(kk * 1.4, 0, 1),
                      emit=1.4, dof=0.2),
               ribbon(P, width=w * (0.15 + 0.85 * kk), color=deep, alpha=k * 0.7 * np.clip(kk * 1.4, 0, 1),
                      emit=2.0, dof=0.2),
               ribbon(P, width=w * 0.16 * (0.15 + 0.85 * kk), color=core, alpha=k * 0.95 * np.clip(kk * 1.6, 0, 1),
                      emit=2.6 * pulse, dof=0.2)]
        head = self.head(t)[None, :]
        out.append(dict(pos=head, size=w * 0.7, color=core, alpha=k, emit=6.0 * pulse, kind="spark"))
        out.append(dict(pos=head, size=w * 5.0, color=c, alpha=k * 0.16, kind="soft", emit=2.0))
        # shed sparkles, drifting down off the band
        sp = self.sp
        m = len(P)
        f = np.mod(sp[:, 0] + t * (0.8 + 0.4 * sp[:, 1]), 1.0)
        idx = np.minimum((f * (m - 1)).astype(int), m - 1)
        drift = (sp[:, 1:4] - 0.5) * (w * 3.0) * f[:, None] - _v(0.0, 0.5 * w, 0.0) * f[:, None]
        out.append(dict(pos=P[idx] + drift, size=w * (0.09 + 0.10 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                        alpha=k * 0.9 * (1.0 - f) ** 1.2, emit=2.0, kind="spark", twinkle=0.6, seed=sp[:, 3]))
        return [b for b in out if b is not None]


# =========================================================================================================
# The heart of light that stays (drawn point by point as the ribbons pass), the snow of the breath, the
# sparks that gather into her in the held breath
# =========================================================================================================
class Heart:
    def __init__(self):
        s = np.linspace(0.0, 1.0, 260)
        L = np.array([_heart_point(x, -1.0) for x in s])
        R = np.array([_heart_point(x, 1.0) for x in s])
        self.P = np.concatenate([L, R])
        ss = s * s * (3.0 - 2.0 * s)
        tb = HEART_T[0] + np.interp(s, ss, s) * (HEART_T[1] - HEART_T[0])
        self.birth = np.concatenate([tb, tb])
        self.col = np.concatenate([np.repeat(lin(PW.COLORS["Inclusiveness"])[None, :], len(s), 0),
                                   np.repeat(lin(PW.COLORS["Gratitude"])[None, :], len(s), 0)])
        self.sd = np.random.default_rng(31).random(len(self.P))

    def sample(self, t):
        k = _env(t, HEART_T[0], 188.27, 0.05, 0.15) * dance_k(t)
        if k <= 0.0:
            return None
        on = self.birth <= t
        if not on.any():
            return None
        beat = 1.0 + 0.5 * beat_pulse(t, 0.12) + 0.6 * hit_pulse(t, [HIT["love"]], fall=0.6)
        grow = 1.0 + 0.06 * beat_pulse(t, 0.12)
        P = HEART_C + (self.P[on] - HEART_C) * grow
        age = t - self.birth[on]
        fl = 1.0 + 2.0 * np.exp(-age / 0.25)
        col = self.col[on] * 0.55 + lin(WHITE) * 0.45
        out = [dict(pos=P, size=0.045 * fl, color=col, alpha=k * np.minimum(1.0, 0.8 * fl), emit=3.0 * beat,
                    kind="spark", twinkle=0.4, seed=self.sd[on]),
               dict(pos=P[::4], size=0.5, color=self.col[on][::4], alpha=0.10 * k * beat, kind="soft", emit=1.6)]
        full = _sc(HEART_T[1] - 0.1, HEART_T[1] + 0.2, t)
        if full > 0.0:                         # the whole heart glows from within once it is closed
            out.append(dict(pos=HEART_C[None, :] + _v(0.0, -0.2, 0.0), size=3.2, color=lin(ROSE),
                            alpha=0.10 * full * k * beat, kind="soft", emit=1.5))
        return out


class Snow:
    """Light falling like snow round the dancer in the breath (1:57 to 2:01.3) and gathering into her in the
    held breath (4:07.5 to 4:09.4)."""

    def __init__(self):
        r = np.random.default_rng(77)
        self.s = r.random((900, 5))

    def sample(self, t):
        if dance_k(t) <= 0.0:
            return None
        s = self.s
        out = []
        kb = _env(t, 117.0, 121.9, 0.4, 0.6)
        if kb > 0.0:
            y = 6.0 - np.mod(t * (0.25 + 0.25 * s[:, 2]) + 6.0 * s[:, 3], 6.0)
            x = -7.0 + 14.0 * s[:, 0] + 0.3 * np.sin(t * 0.7 + 6.0 * s[:, 4])
            z = -6.0 + 12.0 * s[:, 1]
            out.append(dict(pos=DANCE_C + np.stack([x, y, z], 1), size=0.016 + 0.02 * s[:, 4], color=lin("#fff1d8"),
                            alpha=0.7 * kb, emit=1.8, kind="spark", twinkle=0.5, seed=s[:, 4], dof=0.6))
        kh = _env(t, 247.5, 249.43, 0.3, 0.1)
        if kh > 0.0:                          # sparks from all round gathering into her heart
            heart = _bodies()["held"].where(min(t, 249.8), "heart")
            u = np.clip((t - 247.5 - 1.0 * s[:, 0]) / 0.9, 0.0, 1.0)
            u = u * u * (3.0 - 2.0 * u)
            d = np.stack([s[:, 1] - 0.5, 0.6 * (s[:, 2] - 0.3), s[:, 3] - 0.5], 1)
            d = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
            P = heart[None, :] + d * (0.8 + 1.6 * s[:, 4:5]) * (1.0 - u)[:, None]
            col = np.array([lin(COL9[int(x * 9) % 9]) for x in s[:, 0]]) * 0.5 + lin(WHITE) * 0.5
            out.append(dict(pos=P, size=0.012 + 0.016 * s[:, 4], color=col, alpha=kh * (0.3 + 0.7 * (1.0 - u) ** 0.5),
                            emit=2.6, kind="spark", twinkle=0.6, seed=s[:, 4], dof=0.5))
        return out or None


class Halo:
    """A soft glow of each dancer's colour round her: she reads as a figure of light from afar."""

    def __init__(self, name, color):
        self.name, self.col = name, lin(color)

    def sample(self, t):
        b = _bodies()[self.name]
        if dance_k(t) <= 0.0 or not (b.show[0] < t < b.show[1]):
            return None
        k = b.gain(t) * (1.0 + 0.3 * beat_pulse(t) * intensity(t))
        c = b.where(t, "chest")
        p = np.stack([c, 0.5 * (c + b.where(t, "pelvis")), b.where(t, "knee.L") * 0.5 + b.where(t, "knee.R") * 0.5])
        return [dict(pos=p, size=np.array([1.6, 1.5, 1.3]), color=self.col, alpha=0.10 * k, kind="soft", emit=1.6),
                dict(pos=b.where(t, "ground")[None, :] + _v(0.0, 0.05, 0.0), size=2.6, color=self.col, alpha=0.12 * k,
                     kind="soft", emit=1.5, reflect=False)]


def _solo_strength(t):
    return 0.14 * max(_env(t, 117.0, 125.92, 0.4, 0.3), _env(t, 247.5, 249.43, 0.3, 0.1)) * dance_k(t)


def add(scene):
    b = _bodies()
    for name, body in b.items():
        scene.add("dancer " + name, Gate(body))
    solo = WINDOWS["solo"], WINDOWS["held"]
    scene.add("dance ribbon solo", Ribbon(_solo_head, _solo_hand, LAV, solo, trail=2.0, width=0.34,
                                          n=110, seed=1))
    for side, nm, col in ((-1.0, "heartL", PW.COLORS["Inclusiveness"]), (1.0, "heartR", PW.COLORS["Gratitude"])):
        scene.add("dance ribbon " + nm, Ribbon(_heart_head(side), (lambda t, nm=nm, s=side: _hand(nm, t, "R" if s < 0 else "L")),
                                               col, [WINDOWS["heart"]], trail=1.0, width=0.26, n=80, seed=2 + int(side > 0)))
    for i in range(RING_N):
        scene.add("dance ribbon ring %d" % i, Ribbon(_ring_head(i), (lambda t, i=i: _hand("ring%d" % i, t)), RING_COL[i],
                                                     [WINDOWS["ring"]], trail=0.9, width=0.34, n=70, seed=10 + i))
    for name, body in b.items():
        scene.add("dance halo " + name, Halo(name, HALO_COL.get(name) or RING_COL[int(name[4:])]))
    scene.add("dance heart", Heart())
    scene.add("dance snow", Snow())
    add_light(_solo_head, LAV, _solo_strength, radius=4.0)
