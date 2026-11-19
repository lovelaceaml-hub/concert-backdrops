"""Song 11 v2: the conductor of light (round 7; Anthony: "Instead of a dancer, have a conductor but have it be
dramatic as if he's conducting everything"). He replaces all five dancer moments of round 5.

Owned by the dance thread (the module keeps its name, SHOTS and add(scene) so the core and the "dance" blocks keep
working). Imported by tools/s11_full2/s11_full2.py beside the other threads: the core's music, places and helpers
come in by the star import. Camera shots: SHOTS below (one per EDIT block the dance thread owns, exact times).
Point sets: add(scene). No em dash or en dash anywhere in this file.

One heroic man of light in a tailcoat of light (no facial features) stands on a disc of light on the mirror sea
in front of Mount Zion (COND_C), facing the city, and conducts everything. His right hand beats real 4/4 patterns
on the measured beat grid and downbeats (down at the bottom, in, out, up), legato or staccato as the music asks;
the baton's tip is a white-hot point that leaves a trail. The world answers him: comets leave the baton tip, the
sea ripples out from his feet on each downbeat, the constellations ripple with it, the city lights and the
clouds swell on his upbeat, and rays open when he raises both arms. The moments:
  1:37.70  THE SUMMONS (was the ring): seen low from behind against the city; four full strokes, each beat
           flings a comet in a campaign colour from the tip; they braid into one spiral climbing to the sky; on
           the last beat both arms go up and the rays open, into "sacrifice" (1:39.4).
  1:57.00  THE BREATH: hushed and slow, a small legato pattern, the left hand palm down calming the sea; light
           falls round him like snow, a breath brighter on his downbeats.
  2:01.32  THE STRINGS: quick staccato flicks; on each strings pulse (2:01.32, 2:04.18) the baton flicks up and a
           comet shoots off over the sea toward the city; the left hand cues the strings open.
  3:05.92  WONDROUS LOVE: on the big hit both arms sweep down from overhead and draw a heart; two comets (from
           the baton tip and the left fingertips) draw the same heart huge in the sky; it stays, beating, while he
           conducts the next bar.
  4:07.50  THE HELD BREATH: seen low from the front against a growing light; he holds the fermata, baton poised
           high, sparks gathering into its tip; on the final rise the baton sweeps up and a comet flies on.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403

DANCE_C = _v(0.0, 0.0, 160.0)          # his disc on the mirror sea (Zion's foot is 580 m beyond, toward -z)
COND_C = DANCE_C
LAV = PW.COLORS["Compliment"]
WINDOWS = dict(ring=(97.7, 99.4), solo=(117.0, 125.92), heart=(185.92, 188.27), held=(247.5, 249.43))
HEIGHT = 1.86
BATON = 0.52                           # the baton's length, metres
TIP_COL = "#fffaf0"


def _D(x, y, z):
    return DANCE_C + _v(x, y, z)


def _W(q):
    """A point in his own frame (x his left, y up, z forward; he faces -z, toward Zion) in the world."""
    return COND_C + _v(-q[0], q[1], -q[2])


# =========================================================================================================
# The bar grid: the measured beats and downbeats (music map), falling back to the engine's beat grid
# =========================================================================================================
_GRID = {}


def _grid():
    if _GRID:
        return _GRID
    B = D = None
    try:
        import songs.s11_music_fx as MF
        if MF._M is not None and "down_t" in MF._M:
            B, D = np.asarray(MF._M["beat_t"], np.float64), np.asarray(MF._M["down_t"], np.float64)
    except Exception:  # noqa: BLE001  (no music map: the engine's beats, bars anchored on 2:01.32)
        B = None
    if B is None or len(B) < 8 or len(D) < 2:
        B = np.asarray(BEATS, np.float64)
        i0 = int(np.argmin(np.abs(B - HIT["mother"])))
        D = B[(np.arange(len(B)) - i0) % 4 == 0]
    c = np.arange(len(B), dtype=np.float64)
    dn = np.round(np.interp(D, B, c))
    _GRID.update(B=B, c=c, dn=np.unique(dn))
    return _GRID


def bar_pos(t):
    """Where t lies in its bar, 0..4: 0 is the downbeat, 1, 2, 3 the other beats (fractional between)."""
    g = _grid()
    cb = float(np.interp(t, g["B"], g["c"]))
    k = int(np.searchsorted(g["dn"], cb, side="right")) - 1
    if k < 0:
        return cb % 4.0
    return float(min(cb - g["dn"][k], 3.999))


def beat_times(a, b):
    g = _grid()
    B = g["B"]
    return [float(x) for x in B[(B >= a) & (B < b)]]


def down_times(a, b):
    g = _grid()
    D = np.interp(g["dn"], g["c"], g["B"])
    return [float(x) for x in D[(D >= a) & (D < b)]]


def _mf(name, t):
    try:
        import songs.s11_music_fx as MF
        return float(MF.fx(name, t))
    except Exception:  # noqa: BLE001
        return 0.0


def upbeat(t):
    """The upbeat swell: rises through beat 4 into the downbeat, then falls away (city and clouds breathe in)."""
    p = bar_pos(t)
    return _sc(2.4, 3.95, p) if p >= 1.0 else float(np.exp(-p / 0.22))


def downbeat(t, fall=0.35):
    p = bar_pos(t)
    return float(np.exp(-p * 0.47 / fall)) if p < 2.0 else 0.0


# =========================================================================================================
# Shots (kind "local": the conductor on the sea, Zion before him)
# =========================================================================================================
def _shot(name, t0, t1, fov, keys, ap=0.03, **kw):
    return dict(name=name, kind="local", t0=t0, t1=t1, fov=fov, aperture=ap,
                keys=[(t0 + f * (t1 - t0), p, q) for f, p, q in keys], **kw)


SHOTS = [
    # the summons: low behind his right shoulder, looking up past him to the sky the comets braid into
    _shot("dance_ring", 97.7, 99.4, 56.0, [(0.0, _D(1.9, 0.55, 4.4), _D(-0.3, 2.3, -6.0)),
                                           (1.0, _D(1.3, 0.42, 3.6), _D(-0.2, 5.2, -9.0))], roll=(-3.0, 2.0)),
    # the breath: low behind and to his left, a slow drift round him; the city glows in the mist beyond
    _shot("dance_breath", 117.0, 121.32, 44.0, [(0.0, _D(-2.7, 0.6, 3.4), _D(0.3, 1.55, -2.0)),
                                                (1.0, _D(-1.6, 0.5, 3.9), _D(0.3, 1.6, -2.0))], pace="linear"),
    # the strings: wide and low from his right, rising; the comets fly off toward the city
    _shot("dance_strings", 121.32, 125.92, 50.0, [(0.0, _D(5.6, 0.6, 2.4), _D(-0.6, 2.0, -3.5)),
                                                  (1.0, _D(4.2, 1.3, 5.2), _D(-0.4, 2.4, -5.0))], roll=(2.0, -1.0)),
    # wondrous love: low in front of him on a long lens (between him and the city), looking up at him against
    # the dark sky over the sea and the light behind him; he stands tall at the right edge (screen x 0.86 to
    # 0.98, clear of the phrase), the phrase in the middle, the heart drawn in the sky above it
    _shot("dance_heart", 185.92, 188.27, 38.0, [(0.0, _D(3.0, 0.45, -7.5), _D(3.9, 4.0, 8.0)),
                                                (1.0, _D(2.9, 0.42, -7.1), _D(3.9, 4.1, 8.0))], pace="linear"),
    # the held breath: low in front of him, looking up against the light; tilting up as the comet flies on
    _shot("dance_held", 247.5, 249.43, 46.0, [(0.0, _D(1.6, 0.45, -4.6), _D(0.0, 1.75, 0.0)),
                                              (0.8, _D(1.3, 0.42, -4.1), _D(0.0, 1.9, 0.0)),
                                              (1.0, _D(1.25, 0.42, -4.0), _D(0.0, 2.8, 0.0))], pace="linear"),
]


def dance_k(t):
    """1 inside the conductor's blocks (he exists only then)."""
    return 1.0 if shot_name(t).startswith("dance_") else 0.0


def _in(t, name, pre=0.6, post=0.6):
    a, b = WINDOWS[name]
    return a - pre <= t <= b + post


# =========================================================================================================
# The hands: a real 4/4 pattern on the beat (right hand, the baton), and what the left hand does in each moment
# =========================================================================================================
# the ictus of each beat (the bottom of each stroke, where the beat falls) and the rebound between beats, in the
# pattern's own units (x toward his left, y up); the hand leaves each ictus fast, slows at the rebound's top and
# falls fast into the next ictus
_ICT = [(0.0, -0.26), (0.32, -0.10), (-0.44, -0.10), (-0.12, 0.06)]
_REB = [(0.08, 0.10), (-0.02, 0.07), (-0.34, 0.18), (-0.04, 0.46)]
R_CEN = (-0.22, 1.30, 0.44)                 # where the pattern sits (his right, before the chest)


def _pattern(p, amp=1.0, style="legato"):
    """The right hand at bar position p (0..4), his frame."""
    k = int(np.floor(p)) % 4
    s = p - np.floor(p)
    if style == "staccato":                  # a flick away from the ictus, then still until the next
        s = 1.0 - (1.0 - min(s * 1.15, 1.0)) ** 2.2
    a, c, b = np.array(_ICT[k]), np.array(_REB[k]), np.array(_ICT[(k + 1) % 4])
    q = (1.0 - s) ** 2 * a + 2.0 * s * (1.0 - s) * c + s * s * b
    z = R_CEN[2] + 0.07 * amp * (1.0 - np.sin(np.pi * s))
    return np.array([R_CEN[0] + amp * q[0], R_CEN[1] + amp * q[1], z])


L_HUSH = np.array([0.30, 1.02, 0.42])       # the left hand low, palm down: softly
L_HOLD = np.array([0.30, 1.22, 0.36])
L_UP = np.array([0.40, 2.05, 0.22])         # both arms raised: the rays open
R_UP = np.array([-0.38, 2.08, 0.26])


def _mirror(r):
    return np.array([-r[0], r[1], r[2]])


def _heart_xy(s):
    """The heart outline from the top dip (s = 0) round one lobe to the bottom point (s = 1): x >= 0, y (units)."""
    th = np.pi * s
    x = 16.0 * np.sin(th) ** 3
    y = 13.0 * np.cos(th) - 5.0 * np.cos(2 * th) - 2.0 * np.cos(3 * th) - np.cos(4 * th)
    return x / 16.0, y / 16.0


HEART_T = (185.92, 186.97)                  # drawn from the big hit to the next downbeat
HAND_HEART_C = np.array([0.0, 1.62, 0.50])  # the heart his hands draw (his frame)
HAND_HEART_S = 0.38                         # its half width (kept narrow so he stands clear of the phrase)


def _heart_prog(t):
    u = float(np.clip((t - HEART_T[0]) / (HEART_T[1] - HEART_T[0]), 0.0, 1.0))
    return u ** 0.8 * (1.6 - 0.6 * u ** 0.8) if u < 1.0 else 1.0      # fast off the hit, easing in at the bottom


def _hands_raw(t):
    """(right, left) hand places in his frame at t, before smoothing (the poses the music asks for)."""
    p = bar_pos(t)
    if t < 110.0:                            # the summons: big, marcato; both arms up on the last beat
        r = _pattern(p, 1.35, "legato")
        l = _mirror(r) + np.array([0.0, -0.05, -0.04])
        up = _sc(99.0, 99.32, t)
        return r * (1 - up) + R_UP * up, l * (1 - up) + L_UP * up
    if t < 121.32:                           # the breath: small and slow, the left hand calming the sea
        r = _pattern(p, 0.55, "legato")
        sway = 0.04 * np.sin(2.0 * np.pi * (t - 117.0) / 3.6)
        return r, L_HUSH + np.array([0.0, sway, 0.0])
    if t < 140.0:                            # the strings: staccato flicks, up on each strings pulse
        r = _pattern(p, 0.85, "staccato")
        fl = hit_pulse(t, STRINGS[:2], rise=0.06, fall=0.32)
        r = r + np.array([-0.10 * fl, 0.42 * fl, 0.0])
        cue = hit_pulse(t, STRINGS[:2], rise=0.12, fall=0.9)
        l = L_HOLD + np.array([0.28, 0.30, -0.06]) * min(cue, 1.0)
        return r, l
    if t < 220.0:                            # wondrous love: overhead, the heart on the hit, then the next bar
        x0, y0 = _heart_xy(0.0)
        top = HAND_HEART_C + np.array([0.0, y0 * HAND_HEART_S, 0.0])
        if t < HEART_T[0]:                   # poised at the heart's top, lifting into the hit
            lift = _sc(HEART_T[0] - 1.2, HEART_T[0] - 0.12, t)
            return (top + np.array([-0.06, 0.10 + 0.22 * lift, -0.04]),
                    top + np.array([0.06, 0.10 + 0.22 * lift, -0.04]))
        if t <= HEART_T[1]:
            x, y = _heart_xy(_heart_prog(t))
            sc = HAND_HEART_S
            r = HAND_HEART_C + np.array([-x * sc, y * sc, 0.0])
            return r, _mirror(r)
        w = _sc(HEART_T[1], HEART_T[1] + 0.35, t)
        x, y = _heart_xy(1.0)
        bot = HAND_HEART_C + np.array([0.0, y * HAND_HEART_S, 0.0])
        r = _pattern(p, 0.62, "legato") + np.array([0.10, 0.06, 0.0])
        l = L_HOLD + np.array([-0.04, 0.30 + 0.15 * _sc(187.4, 188.2, t), -0.02])
        return bot * (1 - w) + r * w, bot * (1 - w) + l * w
    # the held breath: the fermata, poised high, barely breathing; the dip on beat 4, then up on the final rise
    breath = 0.012 * np.sin(2.0 * np.pi * (t - 247.5) / 1.9)
    poised = np.array([-0.30, 1.78 + breath, 0.42])
    lpo = np.array([0.34, 1.48 + breath, 0.36])
    dip = _sc(248.55, 248.95, t) * (1.0 - _sc(248.95, 249.12, t))
    up = _sc(249.0, 249.40, t)
    r = poised + np.array([0.04, -0.30, 0.04]) * dip
    l = lpo + np.array([0.0, -0.18, 0.0]) * dip
    return r * (1 - up) + np.array([-0.22, 2.22, 0.20]) * up, l * (1 - up) + L_UP * up


_SM_OFF = np.linspace(-2.2, 2.2, 13)
_SM_W = np.exp(-0.5 * _SM_OFF ** 2)
_SM_W = _SM_W / _SM_W.sum()


_HCACHE = {}


def _hands(t, lag=0.0):
    """Cached (many streams ask for the same moments of his hands every frame)."""
    key = (int(round(t * 2000.0)), lag)
    v = _HCACHE.get(key)
    if v is None:
        if len(_HCACHE) > 200000:
            _HCACHE.clear()
        v = _HCACHE[key] = _hands_s(t, lag)
    return v


def _hands_s(t, lag=0.0):
    """The hands, smoothed (round 8, Anthony: "the conductor's animation is so choppy"): a gaussian over the
    raw poses (0.07 s; 0.045 s in the quick strokes of the summons and the strings) taken a little in the
    past, so every stroke eases in and out, nothing snaps, and the arms follow through behind the beat."""
    sig = 0.045 if (t < 110.0 or 121.32 <= t < 140.0) else 0.07
    c = t - 0.025 - lag
    R = np.zeros(3)
    L = np.zeros(3)
    for o, w in zip(_SM_OFF, _SM_W):
        r, l = _hands_raw(c + o * sig)
        R += w * r
        L += w * l
    return R, L


def hand_R(t):
    return _W(_hands(t)[0])


def hand_L(t):
    return _W(_hands(t)[1])


_SH_R = np.array([-0.19, 1.50, 0.02])


def tip(t):
    """The baton's white-hot tip: along the arm from the shoulder through the hand, lifted forward and up."""
    h = _hands(t)[0]
    hl = _hands(t, lag=0.06)[0]              # the baton trails the hand: follow-through on every stroke
    d = _unit(h - _SH_R + np.array([0.0, 0.22, 0.30]) + 1.6 * (hl - h))
    return _W(h + d * BATON)


def tip_L(t):
    """The left fingertips (the left hand also draws the heart)."""
    h = _hands(t)[1]
    d = _unit(h - np.array([0.19, 1.50, 0.02]) + np.array([0.0, 0.1, 0.2]))
    return _W(h + d * 0.16)


# =========================================================================================================
# The conductor (p3d Body: a man in a tailcoat of light, glitter look, both arms driven to the hand places)
# =========================================================================================================
_BODIES = {}
BODY_BRIGHT = 2.4
# rim lit against the light (round 8): a bright edge round the silhouette as the camera sees it, the inside a dim
# warm glitter, so he reads as a figure standing against the light rather than a white shape
LOOK = [dict(name="rim", bright=1.25, power=2.4), dict(name="glitter", bright=0.32)]
LIGHT_AT = DANCE_C + _v(0.0, 3.5, 4.0)


def _bodies():
    if _BODIES:
        return _BODIES
    from p3d.body import Body
    c = COND_C
    g = []
    for name in ("ring", "solo", "heart", "held"):
        a, b = WINDOWS[name]
        g.append((a - 0.8, b + 0.6, "touch", dict(side="R", to=hand_R, end="palm", palm=(0.0, -0.6, 0.6),
                                                   fingers="pinch", look=False, lean=0.35, wrist=-12.0, ease=0.3)))
        g.append((a - 0.8, b + 0.6, "touch", dict(side="L", to=hand_L, end="palm",
                                                   palm="down" if name == "solo" else (0.0, 0.2, 1.0),
                                                   fingers="open", look=False, lean=0.25, ease=0.3)))
    g.append((247.0, 250.0, "look_up", dict(amount=14.0, ease=0.6)))
    g.append((185.4, 188.6, "look_up", dict(amount=10.0, ease=0.4)))
    _BODIES["cond"] = Body(
        "man", height=HEIGHT, at=(c[0], c[2]), facing=180.0, motion="stand", gesture=g,
        garment="coat", look=LOOK, color="#ffd49a", color2="#fff4e2", points=90000, bright=BODY_BRIGHT,
        size=1.35, light=LIGHT_AT, show=(97.0, 250.2), fade=0.2, seed=8.0)
    return _BODIES


class Gate:
    """A body seen only in the conductor's blocks."""
    wants_camera = True

    def __init__(self, body):
        self.b = body

    def sample(self, t, cam=None):
        if dance_k(t) <= 0.0:
            return []
        return self.b.sample(t, cam)

    def gain(self, t):
        return self.b.gain(t) * dance_k(t)


# =========================================================================================================
# A ribbon of light (the baton's trail): a band that follows its head back in time
# =========================================================================================================
def _deep(hexs, k=1.3):
    c = lin(hexs)
    return np.clip(c * k - 0.15 * c.mean(), 0.0, 1.0)


class Ribbon:
    def __init__(self, head, hand, color, win, trail=1.2, width=0.16, n=70, seed=0, flick=None, sparks=160):
        self.head, self.hand, self.color, self.win = head, hand, color, win
        self.trail, self.width, self.n = trail, width, n
        r = np.random.default_rng(300 + seed)
        self.sp = r.random((sparks, 4))
        self.flick = flick

    def k(self, t):
        return max(_env(t, a, b, 0.25, 0.2) for a, b in self.win) * dance_k(t)

    def points(self, t):
        u = np.linspace(0.0, 1.0, self.n)
        P = np.array([self.head(t - self.trail * x) for x in u])
        if self.hand is not None:
            h = self.hand(t)
            m = 12
            g = np.linspace(0.0, 1.0, m + 2)[1:-1, None]
            sag = _v(0.0, -0.12, 0.0) * np.sin(np.pi * g)
            tie = h[None, :] * (1.0 - g) + P[0][None, :] * g + sag
            P = np.concatenate([P[::-1], tie[::-1], h[None, :]])[::-1]
            v = np.concatenate([np.zeros(m + 1), u])
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
        sp = self.sp
        m = len(P)
        f = np.mod(sp[:, 0] + t * (0.8 + 0.4 * sp[:, 1]), 1.0)
        idx = np.minimum((f * (m - 1)).astype(int), m - 1)
        drift = (sp[:, 1:4] - 0.5) * (w * 3.0) * f[:, None] - _v(0.0, 0.5 * w, 0.0) * f[:, None]
        out.append(dict(pos=P[idx] + drift, size=w * (0.09 + 0.10 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                        alpha=k * 0.9 * (1.0 - f) ** 1.2, emit=2.0, kind="spark", twinkle=0.6, seed=sp[:, 3]))
        return [b for b in out if b is not None]


# =========================================================================================================
# The baton (a line of light from the hand, the white-hot tip), its comets, the heart in the sky, the sea's
# ripples from his feet, his disc, the falling light, the sparks gathering into the tip
# =========================================================================================================
def _tip_flare(t):
    return (1.0 + 0.8 * beat_pulse(t, 0.08) + 0.9 * hit_pulse(t, KICKS, fall=0.35) + 0.8 * _mf("brass", t)
            + 1.4 * hit_pulse(t, STRINGS[:2], fall=0.3))


class Baton:
    def sample(self, t):
        k = dance_k(t)
        if k <= 0.0:
            return None
        a, b = hand_R(t), tip(t)
        fl = _tip_flare(t)
        quiet = 0.6 if 116.0 < t < 121.32 else 1.0
        return [dict(pos=a[None], pos2=b[None], size=0.010, color=lin(TIP_COL) * 1.6, alpha=1.0, emit=2.6,
                     kind="line", dof=0.3),
                dict(pos=b[None], size=0.03 + 0.012 * fl, color=lin(WHITE), alpha=1.0, emit=4.0 * min(fl, 2.5) * quiet,
                     kind="spark"),
                dict(pos=b[None], size=0.10 + 0.05 * fl, color=lin(GOLD2), alpha=0.12 * quiet, kind="soft",
                     emit=2.0)]


class CondComet(Comet):
    """A comet that leaves the baton tip at ts (before that its trail is the tip's own path)."""

    def __init__(self, ts, fly, color, t1, src=None, **kw):
        self.ts, self.fly, self.src = float(ts), fly, (src or tip)
        super().__init__(self._head, color, ts, t1, **kw)

    def _head(self, t):
        if t <= self.ts:
            return self.src(t)
        return self.fly(t - self.ts, self.src(self.ts))

    def k(self, t):
        return super().k(t) * dance_k(t)


BRAID_AXIS = _D(-0.4, 0.0, -14.0)          # the braid climbs round this upright line, before him toward the city
BRAID_TOP = (99.35, 15.0)                  # every strand reaches the rope's crown together as his arms go up


def rainbow(t):
    """The nine colours flowing one into the next along a trail, a colour every half beat (linear rgb)."""
    x = (t - 90.0) / 0.5
    k = int(np.floor(x))
    f = x - k
    return lin(COL9[k % 9]) * (1.0 - f) + lin(COL9[(k + 1) % 9]) * f


class Stream:
    """A stream of coloured light like the promo's (round 9, Anthony: "It looks like he is shooting glowing balls
    of light. I don't want that ... more dramatic like the lights of color from the promo video"): a long thin
    neon line, a white-hot core inside a coloured glow, fizzing with fine sparks along its length, that follows
    its head back in time and sweeps and curves with his gestures. No ball at the head, only a bright point.
    head(t) -> position; launch ts with fly(u, p0) as CondComet (before ts the stream is the tip's own path);
    color: a hex colour or a function of time (the colour each part of the trail had when it was drawn)."""

    def __init__(self, head, color, win, trail=1.6, width=0.16, n=160, seed=0, fly=None, ts=None, src=None,
                 fade=0.2, bright=1.0, fizz=260):
        self.src = src or head
        self.fly, self.ts = fly, ts
        self.color, self.win, self.trail, self.width, self.n = color, win, float(trail), float(width), n
        self.fade, self.bright = float(fade), float(bright)
        self.sp = np.random.default_rng(500 + seed).random((fizz, 4))

    def head(self, t):
        if self.fly is None or t <= self.ts:
            return self.src(t)
        return self.fly(t - self.ts, self.src(self.ts))

    def k(self, t):
        return max(_env(t, a, b, self.fade, self.fade) for a, b in self.win) * dance_k(t)

    def sample(self, t):
        k = self.k(t)
        if k <= 0.0:
            return None
        u = np.linspace(0.0, 1.0, self.n)
        tt = t - self.trail * u
        tt[1:] = np.round(tt[1:] * 480.0) / 480.0     # the trail on a fine time grid: shared between frames and streams
        P = np.array([self.head(x) for x in tt])
        if callable(self.color):
            C = np.array([self.color(x) for x in tt])
        else:
            C = np.repeat(lin(self.color)[None], self.n, 0)
        C = np.clip(C * 1.25 - 0.12 * C.mean(1, keepdims=True), 0.0, None)        # deep, saturated colour
        pulse = 1.0 + 0.35 * beat_pulse(t) * intensity(t) + 0.5 * hit_pulse(t, KICKS, fall=0.4)
        fall = (1.0 - u) ** 0.9
        taper = 0.25 + 0.75 * (1.0 - u) ** 0.5
        w = self.width
        core = 0.35 * C + 0.65 * lin(WHITE)
        out = [ribbon(P, width=w * 3.2 * taper, color=C, alpha=k * 0.10 * fall * self.bright, emit=1.6, dof=0.2),
               ribbon(P, width=w * taper, color=C, alpha=k * 0.55 * fall * self.bright, emit=2.2, dof=0.2),
               ribbon(P, width=w * 0.22 * taper, color=core, alpha=k * 0.95 * fall, emit=3.0 * pulse * self.bright,
                      dof=0.2)]
        sp = self.sp                                    # the fizz: fine sparks crackling off the line
        idx = np.minimum((sp[:, 0] ** 1.4 * (self.n - 1)).astype(int), self.n - 1)
        off = (sp[:, 1:4] - 0.5) * w * (1.5 + 5.0 * u[idx, None])
        out.append(dict(pos=P[idx] + off, size=w * (0.10 + 0.12 * sp[:, 2]), color=0.6 * C[idx] + 0.4 * lin(WHITE),
                        alpha=k * 0.9 * (1.0 - u[idx]) ** 1.3, emit=2.4, kind="spark", twinkle=0.9, seed=sp[:, 3]))
        out.append(dict(pos=P[:1], size=w * 0.9, color=lin(WHITE), alpha=k, emit=3.5 * pulse, kind="spark"))
        return [b for b in out if b is not None]


SWEEP_ANCHOR = R_CEN + np.array([0.0, 0.30, 0.40])     # the middle of his baton's pattern (his frame)


def _sweep(gain, lag, lift=0.35):
    """A head that draws his baton's strokes huge in the air round him: the tip's motion about the middle of
    its pattern, scaled up by gain (a 30 cm stroke becomes a 2 to 3 m arc of light), a moment behind the tip."""
    anc = _W(SWEEP_ANCHOR)

    def f(t):
        p = tip(t - lag)
        return anc + (p - anc) * gain + _v(0.0, lift * (gain - 1.0), 0.0)
    return f


def _rainbow_from(off):
    return lambda t: rainbow(t + off)


def _braid(i, n, ts):
    """The summons: comet i of n leaves the tip on its beat (ts) and joins the rope at its own strand. All the
    strands turn together round one axis (evenly spaced in angle) and the later ones climb faster, so their
    trails wind round each other into one braided rope that reaches its crown on the last beat."""
    a0 = 2.0 * np.pi * i / n
    dur = BRAID_TOP[0] - ts

    def f(u, p0):
        t = ts + u
        q = u / dur
        y = 1.2 + (BRAID_TOP[1] - 1.2) * q ** 1.25
        r = 1.6 * (1.0 - 0.45 * min(q, 1.0) ** 2) + 0.2
        a = a0 + 4.6 * (t - 97.55)
        sp = BRAID_AXIS + _v(r * np.sin(a), y, r * np.cos(a))
        w = _sc(0.0, 0.32, u)
        lead = p0 + _v(0.0, 2.5 * u, -12.0 * u)
        return lead * (1.0 - w) + sp * w
    return f


def _string_shot(side):
    """The strings: a comet flicked off the tip, out over the sea toward the city, arcing up."""
    def f(u, p0):
        return p0 + _v(side * 3.5 * u, 9.0 * u - 1.5 * u * u, -40.0 * u)
    return f


def _final_rise(u, p0):
    """The held breath: on the final rise the comet flies straight up and on into the sky."""
    return p0 + _v(-0.6 * u, 26.0 * u * (0.35 + u), 3.0 * u)


SKY_HEART_C = _D(-0.20, 17.67, 25.96)     # in the sky above the phrase (screen x 0.58 to 0.70, y 0.77 to 0.96)
SKY_HEART_S = 2.56
_HX = _unit(_v(-0.9981, 0.0, 0.0619))       # the heart's plane faces the camera of the "dance_heart" shot


def _sky_heart_point(s, side):
    x, y = _heart_xy(s)
    return SKY_HEART_C + _HX * (side * x * SKY_HEART_S) + _v(0.0, y * SKY_HEART_S, 0.0)


HEART_EYE = _D(2.95, 0.43, -7.3)          # where the "dance_heart" camera stands (the comets fly in its view)


def _azel(d):
    return np.arctan2(d[0], -d[2]), np.arctan2(d[1], np.hypot(d[0], d[2])), float(np.linalg.norm(d))


def _heart_fly(side):
    """The heart: the comet leaves the hand at the hit, rises straight up beside him (as the camera sees it),
    turns over above the phrase and draws its half of the heart huge in the sky; it never crosses the phrase."""
    def f(u, p0):
        t = HEART_T[0] + u
        hp = _sky_heart_point(_heart_prog(t), side)
        a0, e0, r0 = _azel(p0 - HEART_EYE)
        a1, e1, r1 = _azel(hp - HEART_EYE)
        wy = _sc(0.0, 0.16, u)
        wh = _sc(0.07, 0.30, u)
        a, e, r = a0 + (a1 - a0) * wh, e0 + (e1 - e0) * wy, r0 + (r1 - r0) * wh
        return HEART_EYE + r * _v(np.cos(e) * np.sin(a), np.sin(e), -np.cos(e) * np.cos(a))
    return f


class SkyHeart:
    """The heart of light that stays where the comets drew it, beating with the music."""

    def __init__(self):
        s = np.linspace(0.0, 1.0, 300)
        self.P = np.concatenate([np.array([_sky_heart_point(x, sd) for x in s]) for sd in (-1.0, 1.0)])
        tb = np.array([HEART_T[0] + self._inv(x) for x in s])
        self.birth = np.concatenate([tb, tb])
        self.col = np.concatenate([np.repeat(lin(PW.COLORS["Inclusiveness"])[None, :], len(s), 0),
                                   np.repeat(lin(PW.COLORS["Gratitude"])[None, :], len(s), 0)])
        self.sd = np.random.default_rng(31).random(len(self.P))

    @staticmethod
    def _inv(s):
        ts = np.linspace(HEART_T[0], HEART_T[1], 400)
        pr = np.array([_heart_prog(x) for x in ts])
        return float(np.interp(s, pr, ts - HEART_T[0]))

    def sample(self, t):
        k = _env(t, HEART_T[0], 188.27, 0.05, 0.15) * dance_k(t)
        if k <= 0.0:
            return None
        on = self.birth <= t
        if not on.any():
            return None
        beat = 1.0 + 0.5 * beat_pulse(t, 0.12) + 0.5 * hit_pulse(t, [HIT["love"]], fall=0.6) + 0.4 * downbeat(t)
        grow = 1.0 + 0.05 * beat_pulse(t, 0.12)
        P = SKY_HEART_C + (self.P[on] - SKY_HEART_C) * grow
        age = t - self.birth[on]
        fl = 1.0 + 2.0 * np.exp(-age / 0.25)
        col = self.col[on] * 0.55 + lin(WHITE) * 0.45
        out = [dict(pos=P, size=0.10 * fl, color=col, alpha=k * np.minimum(1.0, 0.8 * fl), emit=3.0 * beat,
                    kind="spark", twinkle=0.4, seed=self.sd[on]),
               dict(pos=P[::5], size=1.4, color=self.col[on][::5], alpha=0.08 * k * beat, kind="soft", emit=1.6)]
        full = _sc(HEART_T[1] - 0.1, HEART_T[1] + 0.25, t)
        if full > 0.0:                         # the whole heart glows from within once it is closed
            out.append(dict(pos=SKY_HEART_C[None, :] + _v(0.0, -0.6, 0.0), size=9.0, color=lin(ROSE),
                            alpha=0.07 * full * k * beat, kind="soft", emit=1.5))
        return out


def _ripple_times():
    out = []
    for name, s in (("ring", 1.0), ("solo", 0.45), ("heart", 1.0), ("held", 0.5)):
        a, b = WINDOWS[name]
        for d in down_times(a - 1.9, b):
            out.append((d, s))
    out.append((HIT["love"], 0.9))
    out += [(x, 0.7) for x in STRINGS[:2]]
    return sorted(out)


class SeaRipple:
    """Rings of light running out across the sea from his feet on each of his downbeats."""

    def __init__(self):
        self.ang = np.linspace(0.0, 2.0 * np.pi, 540, endpoint=False)
        self.sd = np.random.default_rng(91).random(540)
        self.hits = None

    def sample(self, t):
        if dance_k(t) <= 0.0:
            return None
        if self.hits is None:
            self.hits = _ripple_times()
        out = []
        for th, s in self.hits:
            u = t - th
            if not (0.0 <= u < 1.8) or shot_of(th) != shot_of(t):
                continue
            rad = 0.8 + 16.0 * (1.0 - np.exp(-u / 0.7))
            P = np.stack([COND_C[0] + rad * np.sin(self.ang), np.full(len(self.ang), 0.03),
                          COND_C[2] + rad * np.cos(self.ang)], 1)
            a = s * np.exp(-u / 0.55) * (1.0 - _sc(1.3, 1.8, u))
            out.append(dict(pos=P, size=0.05 + 0.006 * rad, color=lin(GOLD2) * 0.6 + lin(CRYSTAL) * 0.4,
                            alpha=0.55 * a, kind="spark", emit=2.4, seed=self.sd, twinkle=0.3, reflect=False))
            out.append(dict(pos=P[::6], size=0.6 + 0.05 * rad, color=lin("#c8b8ff"), alpha=0.05 * a, kind="soft",
                            emit=1.3, reflect=False))
        return out or None


class Disc:
    """The disc of light he stands on: it flares on his downbeats."""

    def __init__(self):
        r = np.random.default_rng(17)
        n = 900
        a = r.random(n) * 2.0 * np.pi
        rr = 1.05 * np.sqrt(r.random(n))
        self.P = COND_C + np.stack([rr * np.sin(a), np.full(n, 0.02), rr * np.cos(a)], 1)
        ang = np.linspace(0, 2 * np.pi, 220, endpoint=False)
        self.R = COND_C + np.stack([1.1 * np.sin(ang), np.full(220, 0.03), 1.1 * np.cos(ang)], 1)
        self.sd = r.random(n)

    def sample(self, t):
        k = dance_k(t)
        if k <= 0.0:
            return None
        d = 1.0 + 1.2 * downbeat(t) + 0.4 * beat_pulse(t)
        q = 0.6 if 116.0 < t < 121.32 else 1.0
        return [dict(pos=self.P, size=0.022, color=lin(GOLD2), alpha=0.5 * q, emit=1.6 * d, kind="spark",
                     twinkle=0.6, seed=self.sd, reflect=False),
                dict(pos=self.R, size=0.03, color=lin(WHITE), alpha=0.8 * q, emit=2.2 * d, kind="spark",
                     reflect=False),
                dict(pos=COND_C[None] + _v(0.0, 0.05, 0.0), size=3.0, color=lin(GOLD), alpha=0.10 * q * d,
                     kind="soft", emit=1.4, reflect=False)]


class Snow:
    """Light falling like snow round him in the breath (1:57 to 2:01.3), a breath brighter on his downbeats,
    and sparks gathering into the baton tip in the held breath (4:07.5 to 4:09.4)."""

    def __init__(self):
        r = np.random.default_rng(77)
        self.s = r.random((1000, 5))
        self.g = np.random.default_rng(78).random((420, 5))

    def sample(self, t):
        if dance_k(t) <= 0.0:
            return None
        s = self.s
        out = []
        kb = _env(t, 117.0, 121.9, 0.4, 0.6)
        if kb > 0.0:
            y = 7.0 - np.mod(t * (0.22 + 0.22 * s[:, 2]) + 7.0 * s[:, 3], 7.0)
            x = -8.0 + 16.0 * s[:, 0] + 0.3 * np.sin(t * 0.7 + 6.0 * s[:, 4])
            z = -9.0 + 15.0 * s[:, 1]
            g = 1.0 + 0.7 * downbeat(t, 0.5) + 0.3 * beat_pulse(t, 0.12)
            out.append(dict(pos=DANCE_C + np.stack([x, y, z], 1), size=0.016 + 0.02 * s[:, 4], color=lin("#fff1d8"),
                            alpha=0.7 * kb, emit=1.8 * g, kind="spark", twinkle=0.5, seed=s[:, 4], dof=0.6))
        kh = _env(t, 247.5, 249.1, 0.3, 0.1)
        if kh > 0.0:                          # sparks from all round gathering into the poised baton's tip
            c = tip(min(t, 248.9))
            s = self.g
            u = np.clip((t - 247.5 - 1.1 * s[:, 0]) / 0.9, 0.0, 1.0)
            u = u * u * (3.0 - 2.0 * u)
            d = np.stack([s[:, 1] - 0.5, 0.7 * (s[:, 2] - 0.4), s[:, 3] - 0.5], 1)
            d = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
            P = c[None, :] + d * (0.8 + 2.4 * s[:, 4:5]) * (1.0 - u)[:, None]
            col = np.array([lin(COL9[int(x * 9) % 9]) for x in s[:, 0]]) * 0.5 + lin(WHITE) * 0.5
            out.append(dict(pos=P, size=0.006 + 0.008 * s[:, 4], color=col, alpha=kh * 0.9 * (1.0 - u) ** 0.7,
                            emit=2.2, kind="spark", twinkle=0.6, seed=s[:, 4], dof=0.0))
        return out or None


class Halo:
    """A soft glow round him: a figure of light from afar, a silhouette against the light behind."""

    def __init__(self, name, color):
        self.name, self.col = name, lin(color)

    def sample(self, t):
        b = _bodies()[self.name]
        if dance_k(t) <= 0.0 or not (b.show[0] < t < b.show[1]):
            return None
        k = b.gain(t) * (1.0 + 0.3 * beat_pulse(t) * intensity(t) + 0.3 * _mf("choir", t))
        c = b.where(t, "chest")
        p = np.stack([c, 0.5 * (c + b.where(t, "pelvis")), b.where(t, "knee.L") * 0.5 + b.where(t, "knee.R") * 0.5])
        return [dict(pos=p, size=np.array([1.4, 1.3, 1.1]), color=self.col, alpha=0.035 * k, kind="soft", emit=1.5)]


class BackLight:
    """The blazing light he stands against (a great soft glow behind him as the camera sees him)."""

    def __init__(self, spots):
        self.spots = spots                      # (t0, t1, place, size, colour, strength fn)

    def sample(self, t):
        if dance_k(t) <= 0.0:
            return None
        out = []
        for a, b, p, sz, col, f in self.spots:
            if a <= t <= b:
                k = float(f(t))
                if k > 0.0:
                    out.append(dict(pos=p[None], size=sz, color=lin(col), alpha=0.10 * k, kind="soft", emit=1.5,
                                    reflect=False))
                    out.append(dict(pos=p[None], size=sz * 0.3, color=lin(WHITE), alpha=0.12 * k, kind="soft",
                                    emit=2.0, reflect=False))
        return out or None


RING_COL = [COL9[k] for k in (0, 2, 4, 6, 8, 1, 3)]


def _wrap(scene, name, f):
    """The world answers him: another set's gain multiplied by f(t) while he conducts (1 elsewhere)."""
    try:
        ps = scene.get(name)
    except KeyError:
        return
    g0 = ps.gain if hasattr(ps, "gain") else (lambda t: 1.0)
    ps.gain = lambda t, g0=g0: float(g0(t)) * (f(t) if dance_k(t) > 0.0 else 1.0)


def _swell_amt(t):
    return 0.25 if 116.0 < t < 121.32 or 247.0 < t < 249.0 else 0.55


def add(scene):
    b = _bodies()
    scene.add("conductor of light", Gate(b["cond"]))
    scene.add("conductor halo", Halo("cond", "#ffd9a0"))
    scene.add("conductor disc", Disc())
    scene.add("conductor baton", Baton())
    # the baton draws streams of coloured light (no balls): the nine colours flowing along a long trail in the
    # strokes, a soft lavender line in the breath and the hold, gratitude in the strings
    scene.add("conductor stream strokes", Stream(tip, rainbow, [WINDOWS["ring"], WINDOWS["heart"]], trail=1.1,
                                                 width=0.09, seed=1))
    scene.add("conductor stream left", Stream(tip_L, rainbow, [WINDOWS["heart"]], trail=0.9, width=0.07, seed=5,
                                              bright=0.8))
    scene.add("conductor stream breath", Stream(tip, LAV, [(117.0, 121.32), WINDOWS["held"]], trail=1.8,
                                                width=0.07, seed=2, bright=0.8))
    scene.add("conductor stream strings", Stream(tip, PW.COLORS["Gratitude"], [(121.32, 125.92)], trail=0.9,
                                                 width=0.08, seed=3))
    # the great sweeps: his strokes drawn huge round him in long streams of the nine colours (the promo's
    # lights of colour); kept out of the words while a phrase reads
    from songs.s11_stage import BoxGuard
    sweeps = [((97.6, 99.45), (3.6, 0.06), (5.6, 0.14), (7.4, 0.22)),
              ((121.32, 125.92), (3.5, 0.05), (5.5, 0.12), (7.5, 0.20)),
              ((185.92, 188.27), (2.6, 0.06), (3.6, 0.12), (4.6, 0.18))]
    for j, (win, *arms) in enumerate(sweeps):
        for i, (gain, lag) in enumerate(arms):
            scene.add("conductor sweep %d %d" % (j, i), BoxGuard(Stream(
                _sweep(gain, lag), _rainbow_from(1.5 * i), [win], trail=1.3 + 0.2 * i, width=0.16 + 0.06 * i,
                fade=0.25, bright=1.1, seed=600 + 10 * j + i), keep=0.0))
    # the summons: a stream off the tip on each beat, the four winding into one braided rope to the sky
    bt = beat_times(97.55, 99.2)[:4]
    for i, ts in enumerate(bt):
        scene.add("conductor stream summons %d" % i, Stream(tip, RING_COL[(2 * i) % 7], [(ts, 99.45)], trail=2.2,
                                                            width=0.26, fly=_braid(i, len(bt), ts), ts=ts,
                                                            fade=0.1, seed=400 + i))
    # the strings: a stream flicked off over the sea toward the city on each strings pulse
    for i, ts in enumerate(STRINGS[:2]):
        scene.add("conductor stream flick %d" % i, Stream(tip, COL9[(5 + 3 * i) % 9], [(ts + 0.03, ts + 2.6)],
                                                          trail=1.8, width=0.24, fly=_string_shot(1.0 - 2.0 * i),
                                                          ts=ts + 0.03, fade=0.15, seed=410 + i))
    # wondrous love: two streams (the baton tip and the left fingertips) draw the heart huge in the sky
    scene.add("conductor stream heart R", Stream(tip, PW.COLORS["Gratitude"], [(HEART_T[0], 188.4)], trail=1.4,
                                                 width=0.16, fly=_heart_fly(1.0), ts=HEART_T[0], fade=0.1,
                                                 bright=0.85, seed=420))
    scene.add("conductor stream heart L", Stream(tip_L, PW.COLORS["Inclusiveness"], [(HEART_T[0], 188.4)],
                                                 trail=1.4, width=0.16, fly=_heart_fly(-1.0), ts=HEART_T[0],
                                                 fade=0.1, bright=0.85, seed=421))
    scene.add("conductor sky heart", SkyHeart())
    # the held breath: on the final rise the comet flies up and on
    scene.add("conductor stream final", Stream(tip, rainbow, [(248.6, 249.9)], trail=2.0, width=0.26,
                                               fly=_final_rise, ts=249.12, fade=0.12, seed=430))
    scene.add("conductor ripples", SeaRipple(), reflect=False)
    scene.add("conductor snow", Snow())
    scene.add("conductor backlight", BackLight([
        (97.0, 99.6, _D(0.0, 26.0, -60.0), 30.0, "#ffe2b8", lambda t: 0.3 + 0.6 * _sc(99.0, 99.35, t)),
        (116.5, 121.4, _D(0.0, 6.0, -70.0), 34.0, "#e8d8ff", lambda t: 0.5 + 0.25 * downbeat(t, 0.5)),
        (121.3, 126.0, _D(-8.0, 10.0, -70.0), 34.0, "#ffe2b8", lambda t: 0.45 + 0.4 * upbeat(t)),
        (185.5, 188.4, _D(-22.3, 8.7, 55.3), 18.0, "#ffd8c8", lambda t: 0.4 + 0.3 * upbeat(t)),
        (247.0, 249.6, _D(-1.0, 7.0, 40.0), 34.0, "#fff0dc",
         lambda t: 0.45 + 0.35 * _sc(247.5, 249.0, t) + 0.8 * _sc(249.0, 249.4, t))]))
    # the light he carries and the rays that open when he raises both arms
    add_light(tip, TIP_COL, lambda t: 0.10 * dance_k(t) * (0.8 + 0.4 * beat_pulse(t)) * _tip_flare(t) / 2.0, radius=3.5)
    add_rays(lambda t: _D(0.0, 30.0, -70.0) if t < 150.0 else _D(-1.0, 9.0, 40.0),
             lambda t: dance_k(t) * (0.9 * _sc(99.0, 99.3, t) * (1.0 - _sc(99.5, 99.7, t))
                                     + 0.95 * _sc(249.05, 249.4, t) * (1.0 - _sc(249.6, 249.9, t))),
             color="#fff1d8", size=0.8)
    # the world answers him: the city lights and the clouds swell on his upbeat; the sea glitter and the
    # constellations ripple with his downbeats
    for name in ("city dim", "city gold", "zion dim", "zion gold", "zion gardens", "zion towers", "zion gates",
                 "church"):
        _wrap(scene, name, lambda t: 1.0 + _swell_amt(t) * upbeat(t))
    # Zion's paths of light ran as a bright white streak low across the sea through his frames: faint there
    _wrap(scene, "paths", lambda t: 0.2)
    for k in range(8):
        _wrap(scene, "horizon clouds %d" % k, lambda t: 1.0 + 0.8 * _swell_amt(t) * upbeat(t))
    _wrap(scene, "sea glitter", lambda t: 1.0 + 0.9 * downbeat(t, 0.3))
    _wrap(scene, "constellations", lambda t: 1.0 + 0.7 * downbeat(t, 0.45) + 0.4 * _mf("high", t))
