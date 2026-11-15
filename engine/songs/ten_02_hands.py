"""Film 02 of ten: HANDS. A 60 second promo for the Healing Concert "The Words of Mother's Love".

Every word of Mother's love is something a hand does. Sixty seconds told with hands of light in close up
(refs 04 and 14): each touch flares, and what it releases becomes the words. Two colours meet and the touch
is white; section by section the film warms from gold against night blue to the white gold of day. At the
end Heavenly Mother appears only as two hands, seen from behind the wrists, holding the light of the world.

THE FILM (medley sections at 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, the biggest hit 42.51, 49.47)
  1 FIRST TOUCH     a gold hand and a blue hand reach; the fingertips touch on the hit at 0.97: white flare.
                    The flare writes "How are you?" (Greeting) above the hands.
  2 HIGH FIVE       a child's coral hand smacks a big blue hand on 7.56: a ring of sparks, the Compliment.
                    On 10.44 the big hand turns palm up and sweeps aside: its stream becomes the Concession.
  3 THE FLAME       a flame is set into an elder's cupped hands on 13.30; it lights her fingers and its sparks
                    stream up into the three lines of the Gratitude.
  4 MENDING         on the bass slam at 19.85 an open hand comes to rest on a clenched fist (Apology). The
                    fist opens, turns palm up and the two hands clasp: the same light becomes the
                    Inclusiveness.
  5 WATER           on 26.79 two cupped hands rise out of the lake holding glowing water; the Respect rises out
                    of the lake's mirror.
  6 THE LIFT        on 33.36 a hand from above closes round a wrist reaching up (Consideration); on 37.42 it
                    lifts, and the camera rises with it.
  7 RISE            the breath (40.21): the lifted hands become two hands pressed in prayer in a pale shaft;
                    the Encouragement comes down the shaft. On the biggest hit (42.51) the sun breaks behind the
                    hands, the lens pulls back over a forest of raised hands in all nine colours.
  8 HER HANDS       on 49.47 a white flare: two cupped hands of white gold holding a globe of light (the
                    world), seen from behind the wrists, the day breaking beyond; the end card forms above.
No faces anywhere (only hands and forearms), no lyrics, no em or en dash, frame 0 bright, no fade at the end.
"""
import numpy as np

import songs.s03_original as _base

_base.TOTAL = 60.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 59.6
_base.SONG_END = 60.0
_base.FADE = _base.Track([(0.0, 1.0), (60.0, 1.0)])          # no fade in, no fade out
_base.EXPOSURE = _base.Track([(0.0, 1.0), (60.0, 1.0)])
_ZERO = _base.Track([(0.0, 0.0), (60.0, 0.0)])
_base.RAIN = _ZERO
_base.AURORA = _ZERO
_base.PART = _ZERO
_base.LANTERNS = _ZERO
_base.PETALS = _ZERO
for _p in _base.PHRASES:                       # the flat expressions stay off: the words are particles here
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d import looks as LK  # noqa: E402
from p3d.api import lin, show  # noqa: E402
from p3d.body import Body  # noqa: E402
from p3d.camera import Rig, dolly, orbit  # noqa: E402
from p3d.effects import Flare  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FORM_DUR = 1.8

# ------------------------------------------------------------------------------ the medley (SECTION-MAP.md)
S = (0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47)
BIG = 42.51              # the biggest jump of the mix, after the breath
FINAL = 58.11            # the final hit
T_TOUCH = 0.97           # fingertips touch
T_FIVE = 7.56            # high five
T_SWEEP = 10.44          # after you
T_FLAME = 13.60          # the flame lands in the cupped hands (the camera arrives on the 13.30 hit)
T_REST = S[3]            # the open hand comes to rest on the fist
T_CLASP = 23.55          # the fist has opened: the hands clasp
T_WATER = S[4]
T_GRIP = S[5]
T_LIFT = 37.42
T_PRAY = S[6]

# ------------------------------------------------------------------------------------------ the places
# Each section has its own stage, 8 m apart along the near shore, chest high over the lake; the camera looks
# toward -z, where the sun will rise (azimuth 180).
P1 = np.array([0.0, 1.25, 0.0])
P2 = np.array([8.0, 1.30, 0.0])
P3 = np.array([16.0, 1.05, 0.0])
P4 = np.array([24.0, 1.15, 0.0])
P5 = np.array([32.0, 0.17, 0.0])
P6 = np.array([40.0, 0.95, 0.0])
P7 = np.array([40.0, 1.62, -0.25])      # above the lift: the lifted hands become the hands in prayer
P8 = np.array([60.0, 1.00, 0.0])
GLOBE = P8 + np.array([0.0, 0.085, -0.005])


def _u(v):
    v = np.asarray(v, np.float64)
    return v / max(np.linalg.norm(v), 1e-9)


def _ss(a, b, t):
    x = min(max((t - a) / (b - a), 0.0), 1.0)
    return x * x * x * (x * (6.0 * x - 15.0) + 10.0)


def _slerp(a, b, u):
    return _u(_u(a) * (1.0 - u) + _u(b) * u)


def _hash(n, salt):
    i = np.arange(n, dtype=np.float64)
    return (np.sin(i * 12.9898 + salt * 78.233) * 43758.5453) % 1.0


# ----------------------------------------------------------------------------------------------- hands
def hand(shape, side, at, aim, palm, pose, color, color2="#ffffff", show=None, points=50000, anchor="palm",
         shed=True, trail=(0.0, 0.0, 1.0), bright=1.0, seed=1.0, fade=0.35, shed_n=3500, look="glitter"):
    """One forearm and hand of light placed exactly: the palm (or the fingertips) at `at`, the fingers along
    `aim`, the palm facing `palm` (each a vector or a function of time). Sheds a little dust behind it."""
    fxs = [dict(kind="shed", n=shed_n, life=2.2, where=[LK.HAND], dir=tuple(trail), speed=0.35, rise=0.03,
                turb=0.22, spread=0.05)] if shed else []
    return Body(shape, part="arm." + side, look=look, color=color, color2=color2, points=points, effects=fxs,
                bright=bright, seed=seed, show=show, fade=fade,
                hand=dict(side=side, at=at, aim=aim, palm=palm, pose=pose, anchor=anchor))


# ---- 1 FIRST TOUCH: gold from the left (palm up, from below), blue from the right (palm down, from above)
_TL = np.radians(16.0)
_AIM1 = (np.array([np.cos(_TL), np.sin(_TL), 0.0]), np.array([-np.cos(_TL), -np.sin(_TL), 0.0]))


def _gap1(t):
    """Half the distance between the fingertips: closing fast to the touch, resting, parting at the end."""
    close = _ss(T_TOUCH - 1.55, T_TOUCH, t)
    part = _ss(5.3, 6.9, t)
    return 0.16 * (1.0 - close) + 0.003 + 0.22 * part


def _touch_at(j):
    def f(t):
        drift = np.array([0.0, 0.006 * np.sin(1.3 * t + j), 0.006 * np.cos(0.9 * t + 2 * j)])
        return P1 - _AIM1[j] * _gap1(t) + drift
    return f


# ---- 2 HIGH FIVE, then AFTER YOU
def _five_child(t):
    u = _ss(T_FIVE - 0.55, T_FIVE, t)
    back = _ss(T_FIVE + 0.05, T_FIVE + 0.5, t) * 0.035 + _ss(9.6, 10.6, t) * 0.25
    return P2 + np.array([-0.028 - 0.36 * (1 - u) - back, -0.06 - 0.30 * (1 - u) - back * 0.8, 0.0])


def _five_big(t):
    u = _ss(T_FIVE - 0.55, T_FIVE, t)
    back = _ss(T_FIVE + 0.05, T_FIVE + 0.5, t) * 0.035
    sweep = _ss(T_SWEEP - 0.25, T_SWEEP + 0.7, t)
    p = P2 + np.array([0.028 + 0.36 * (1 - u) + back, 0.05 + 0.26 * (1 - u), 0.0])
    return p + sweep * np.array([0.30, -0.24, 0.10])


def _five_big_aim(t):
    return _slerp((-0.25, 1.0, 0.05), (1.0, 0.12, 0.35), _ss(T_SWEEP - 0.25, T_SWEEP + 0.7, t))


def _five_big_palm(t):
    return _slerp((-1.0, 0.0, 0.05), (0.0, 1.0, 0.25), _ss(T_SWEEP - 0.25, T_SWEEP + 0.7, t))


def _sweep_palm(t):
    return _five_big(t) + np.array([0.0, 0.03, 0.0])


# ---- 3 THE FLAME in an elder's cupped hands (fingers toward the camera, palms up and tilted in)
def _cup(centre, gap, toward=1.0):
    """Two cupped hands side by side round `centre`: (at, aim, palm) for the right and the left hand."""
    out = {}
    for side, sgn in (("R", -1.0), ("L", 1.0)):
        at = centre + np.array([sgn * gap, 0.0, 0.0])
        aim = _u((sgn * 0.18, 0.22, toward))
        palm = _u((-sgn * 0.45, 1.0, 0.0))
        out[side] = (at, aim, palm)
    return out


class Flame:
    """A small living flame of sparks with a warm core; it is set down into the hands at t0."""

    def __init__(self, base, t0, t1, n=2600, color="#ffb347", core="#fff3d0", h=0.075, r=0.017):
        self.base, self.t0, self.t1, self.n, self.h, self.r = np.asarray(base, np.float64), t0, t1, n, h, r
        self.ph = _hash(n, 1.0)
        self.ang = _hash(n, 2.0) * 2 * np.pi
        self.rr = np.sqrt(_hash(n, 3.0))
        self.life = 0.35 + 0.45 * _hash(n, 4.0)
        self.c0, self.c1 = lin(core), lin(color)
        self.sz = 0.0018 + 0.0035 * _hash(n, 5.0) ** 3

    def gain(self, t):
        return _ss(self.t0 - 0.25, self.t0 + 0.1, t) * (1.0 - _ss(self.t1 - 0.5, self.t1, t))

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.001:
            return []
        drop = (1.0 - _ss(self.t0 - 0.6, self.t0, t)) * 0.30          # lowered into the hands
        a = ((t / self.life + self.ph) % 1.0)
        sway = 0.006 * np.sin(7.0 * t + 3.0 * a) + 0.004 * np.sin(13.0 * t)
        y = self.h * a ** 0.85 * (1.0 + 0.25 * np.sin(9.0 * t + self.ph * 6))
        rad = self.r * self.rr * (1.0 - a) ** 0.8 * (0.6 + 0.4 * np.sin(np.pi * np.minimum(a * 3, 1)))
        pos = np.stack([self.base[0] + rad * np.cos(self.ang) + sway * a, self.base[1] + drop + y,
                        self.base[2] + rad * np.sin(self.ang)], 1)
        k = a[:, None]
        col = self.c0[None] * (1 - k) + self.c1[None] * k
        alpha = g * np.clip(a / 0.08, 0, 1) * (1.0 - a) ** 1.2
        return [dict(pos=pos, size=self.sz, color=col, alpha=alpha, kind="soft", emit=3.2),
                dict(pos=(self.base + [0.0, drop + 0.018, 0.0])[None], size=0.05, color=lin("#ffc070"),
                     alpha=0.55 * g, kind="soft", emit=2.2, dof=0.4)]


class Pool:
    """Glowing water held in two cupped hands, a few drops falling between the fingers."""

    def __init__(self, centre, t0, t1, n=5000, radius=0.05, color="#7fe6e0"):
        self.c, self.t0, self.t1, self.n, self.R = np.asarray(centre, np.float64), t0, t1, n, radius
        self.a = _hash(n, 7.0) * 2 * np.pi
        self.r = np.sqrt(_hash(n, 8.0))
        self.col = lin(color)
        self.nd = 160
        self.dph = _hash(self.nd, 9.0)
        self.dx = (_hash(self.nd, 10.0) - 0.5) * 0.12

    def gain(self, t):
        return _ss(self.t0, self.t0 + 0.5, t) * (1.0 - _ss(self.t1 - 0.6, self.t1, t))

    def sample(self, t, centre=None):
        g = self.gain(t)
        if g <= 0.001:
            return []
        c = self.c if centre is None else centre
        rr = self.r * self.R * (1.0 + 0.04 * np.sin(6 * t + self.a * 3))
        y = 0.003 * np.sin(18.0 * self.r - 5.0 * t)
        pos = np.stack([c[0] + rr * np.cos(self.a), c[1] + y, c[2] + rr * np.sin(self.a) * 0.8], 1)
        out = [dict(pos=pos, size=0.0022, color=self.col * (0.7 + 0.6 * (1 - self.r))[:, None], alpha=g * 0.9,
                    kind="soft", emit=2.0)]
        a = (t * 0.9 + self.dph) % 1.0
        dpos = np.stack([c[0] + self.dx, c[1] - 0.04 - 0.5 * a ** 2, c[2] + 0.02 + 0.0 * a], 1)
        out.append(dict(pos=dpos, size=0.003, color=self.col, alpha=g * (dpos[:, 1] > 0.0) * (1 - a), kind="spark",
                        emit=2.5))
        return out


class Globe:
    """The light of the world held in Her hands: a sphere of soft light, its continents brighter, nine coloured
    lights circling it, and sparks rising."""

    def __init__(self, centre, radius, t0, n=14000):
        self.c, self.R, self.t0, self.n = np.asarray(centre, np.float64), radius, t0, n
        u, v = _hash(n, 11.0), _hash(n, 12.0)
        th = np.arccos(1 - 2 * u)
        ph = 2 * np.pi * v
        self.d = np.stack([np.sin(th) * np.cos(ph), np.cos(th), np.sin(th) * np.sin(ph)], 1)
        land = np.sin(3.1 * self.d[:, 0] + 1.3) * np.sin(2.3 * self.d[:, 1] + 0.4) + 0.6 * np.sin(4.0 * self.d[:, 2])
        self.land = (land > 0.25).astype(np.float64)
        self.col = np.where(self.land[:, None] > 0, lin("#fff1cf")[None], lin("#9fd8ff")[None])
        self.nine = [lin(e["color"]) for e in PW.EXPRESSIONS]
        self.ns = 900
        self.sph = _hash(self.ns, 13.0)
        self.sx = (_hash(self.ns, 14.0) - 0.5)
        self.sz_ = (_hash(self.ns, 15.0) - 0.5)

    def sample(self, t):
        g = _ss(self.t0 - 0.2, self.t0 + 0.6, t)
        if g <= 0.001:
            return []
        ang = 0.35 * (t - self.t0)
        ca, sa = np.cos(ang), np.sin(ang)
        d = self.d.copy()
        d[:, 0], d[:, 2] = ca * self.d[:, 0] + sa * self.d[:, 2], -sa * self.d[:, 0] + ca * self.d[:, 2]
        pos = self.c + d * self.R
        out = [dict(pos=pos, size=0.0016 + 0.0012 * self.land, color=self.col, alpha=g * (0.55 + 0.45 * self.land),
                     kind="soft", emit=1.8),
               dict(pos=self.c[None], size=self.R * 3.2, color=lin("#ffe9c4"), alpha=0.35 * g, kind="soft",
                    emit=1.2, dof=0.3)]
        k = np.arange(9)
        a9 = 2 * np.pi * k / 9 + 0.9 * (t - self.t0)
        p9 = self.c + np.stack([np.cos(a9) * self.R * 1.45, 0.25 * self.R * np.sin(2 * a9 + t),
                                np.sin(a9) * self.R * 1.45], 1)
        out.append(dict(pos=p9, size=0.006, color=np.array(self.nine), alpha=g * np.ones(9), kind="spark", emit=5.0,
                        twinkle=0.6))
        a = (0.25 * (t - self.t0) + self.sph) % 1.0
        sp = self.c + np.stack([self.sx * self.R * 2.4 * (1 + a), self.R + a * 0.32, self.sz_ * self.R * 2.4], 1)
        out.append(dict(pos=sp, size=0.0025, color=lin("#ffe2a8"), alpha=g * np.sin(np.pi * a) ** 1.5, kind="spark",
                        emit=2.4, twinkle=0.8))
        return out


class Painted:
    """Wraps a point set so that it is also painted in one warm colour over the scene (so hands of light still
    read on a bright day; p3d.api `paint`)."""
    wants_camera = True

    def __init__(self, ps, color, amount=0.8, light=0.45):
        self.ps, self.col, self.amount, self.light = ps, show(color), amount, light

    def sample(self, t, cam=None):
        out = self.ps.sample(t, cam) if getattr(self.ps, "wants_camera", False) else self.ps.sample(t)
        res = []
        for b in (out if isinstance(out, list) else [out]):
            if not b:
                continue
            b = dict(b)
            n = len(np.atleast_2d(b["pos"]))
            c = np.asarray(b.get("color", self.col), np.float64)
            c = c if c.ndim == 2 else np.repeat(c.reshape(1, 3), n, 0)
            b["color"] = 0.35 * c + 0.65 * self.col[None]
            b["paint"] = self.amount
            b["paint_light"] = self.light
            res.append(b)
        return res


# --------------------------------------------------------------------------------------------- the camera
def _look_two(a, b, t0, t1):
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    return lambda t: a + (b - a) * _ss(t0, t1, t)


def _lift(t):
    return 0.55 * _ss(T_LIFT, T_LIFT + 2.0, t)


def _rig(focus="target"):
    up = np.array([0.0, 1.0, 0.0])
    return Rig([
        # 1 first touch: the lens spirals in at the gap, snaps back on the touch, then revolves slowly
        orbit(P1, radius=(0.40, 1.0), height=(1.29, 1.38), a0=46.0, a1=8.0, t0=0.0, t1=1.75, fov=34.0,
              look=P1 + 0.13 * up, aperture=0.016, near=0.02, focus=focus,
              pace=[(0.0, 0.0), (T_TOUCH, 0.30), (1.75, 1.0)]),
        orbit(P1, radius=1.0, height=1.38, a0=8.0, a1=-26.0, t0=1.75, t1=S[1], fov=34.0,
              look=P1 + 0.13 * up, aperture=0.016, near=0.02, focus=focus, blend=0.5),
        # 2 the high five, then the sweep aside: a whip in, the look follows the palm to the right
        orbit(P2, radius=(0.66, 1.08), height=(1.30, 1.50), a0=-34.0, a1=12.0, t0=S[1], t1=S[2] + 0.15, fov=36.0,
              look=_look_two(P2 + np.array([-0.02, 0.20, 0.0]), P2 + np.array([0.16, 0.16, 0.0]), T_SWEEP - 0.4,
                             T_SWEEP + 0.9),
              aperture=0.017, near=0.02, blend=0.42, focus=focus,
              pace=[(S[1], 0.0), (T_FIVE, 0.16), (8.3, 0.36), (T_SWEEP, 0.55), (11.2, 0.76), (S[2] + 0.15, 1.0)]),
        # 3 the flame: whip in low, drift up and back as the lines rise
        orbit(P3, radius=(0.52, 1.12), height=(1.18, 1.40), a0=26.0, a1=-12.0, t0=S[2] + 0.15, t1=S[3], fov=36.0,
              look=P3 + 0.16 * up, aperture=0.016, near=0.02, blend=0.38, focus=focus,
              pace=[(S[2] + 0.15, 0.0), (14.4, 0.32), (15.4, 0.55), (S[3], 1.0)]),
        # 4 mending: a hard cut inside the flash of the bass slam
        orbit(P4, radius=(0.80, 1.06), height=(1.30, 1.42), a0=-30.0, a1=16.0, t0=S[3], t1=S[4], fov=36.0,
              look=P4 + 0.15 * up, aperture=0.017, near=0.02, blend=0.0, focus=focus,
              pace=[(S[3], 0.0), (20.43, 0.14), (T_CLASP, 0.55), (24.2, 0.70), (S[4], 1.0)]),
        # 5 water: a cut to the lake surface, rising up and back
        orbit(P5, radius=(0.50, 1.10), height=(0.24, 0.52), a0=24.0, a1=-16.0, t0=S[4], t1=S[5], fov=38.0,
              look=P5 + 0.20 * up, aperture=0.016, near=0.02, blend=0.0, focus=focus,
              pace=[(S[4], 0.0), (27.97, 0.30), (29.79, 0.55), (S[5], 1.0)]),
        # 6 the lift: the camera rises with the hands
        orbit(P6, radius=(0.95, 1.12), height=(1.12, 1.78), a0=-22.0, a1=18.0, t0=S[5], t1=S[6], fov=38.0,
              look=lambda t: P6 + np.array([-0.12, 0.16 + _lift(t), 0.0]), aperture=0.018, near=0.02,
              blend=0.0, focus=focus, pace=[(S[5], 0.0), (T_LIFT, 0.35), (39.5, 0.92), (S[6], 1.0)]),
        # 7 the breath: almost still in front of the hands in prayer; on the biggest hit the lens pulls back
        dolly(P7 + np.array([0.06, 0.06, 0.78]), P7 + np.array([0.0, 0.04, 0.60]), S[6], BIG, fov=34.0,
              look=P7 + np.array([0.0, 0.13, 0.0]), aperture=0.016, near=0.02, blend=0.9, focus=focus),
        dolly(P7 + np.array([0.0, 0.04, 0.60]), P7 + np.array([0.0, 0.42, 2.9]), BIG, S[7], fov=(34.0, 46.0),
              look=_look_two(P7 + np.array([0.0, 0.13, 0.0]), P7 + np.array([0.0, 0.75, -6.0]), BIG, BIG + 1.6),
              aperture=(0.016, 0.006), near=0.02, blend=0.12, focus=focus,
              pace=[(BIG, 0.0), (BIG + 1.3, 0.85), (S[7], 1.0)]),
        # 8 Her hands: a cut inside the white flare, close on the globe; the lens pulls back behind the wrists
        dolly(P8 + np.array([0.0, 0.16, 0.24]), P8 + np.array([0.0, 0.29, 0.66]), S[7], 54.6, fov=(40.0, 38.0),
              look=_look_two(GLOBE, P8 + np.array([0.0, -0.08, -1.0]), S[7], 53.8), aperture=(0.012, 0.008),
              near=0.02, blend=0.0, focus=lambda t: float(np.linalg.norm(_rig_pos8(t) - GLOBE)),
              pace=[(S[7], 0.0), (50.3, 0.40), (54.6, 1.0)]),
        dolly(P8 + np.array([0.0, 0.29, 0.66]), P8 + np.array([0.0, 0.31, 0.74]), 54.6, 60.0, fov=38.0,
              look=P8 + np.array([0.0, -0.08, -1.0]), aperture=0.008, near=0.02, blend=1.2,
              focus=float(np.linalg.norm(P8 + np.array([0.0, 0.30, 0.70]) - GLOBE))),
    ], handheld=0.15, min_height=0.03)


def _rig_pos8(t):
    """Where the closing pull back stands (for its focus on the globe): the straight line of that move."""
    k = np.interp(t, [S[7], 50.3, 54.6], [0.0, 0.40, 1.0])
    return P8 + np.array([0.0, 0.16, 0.24]) + k * np.array([0.0, 0.13, 0.42])


_LAYOUT = _rig()


# ---------------------------------------------------------------------------------------------- the words
def _word(x, y, depth, px, t_in, t_read0, t_read1, t_out, **kw):
    """A word laid out by where it is read: the screen place (x, y) of its centre and the pixels of one em
    (1080p) at the middle of its reading moment, `depth` metres from the camera; its point count follows its
    size on screen so its letters stay crisp."""
    tm = 0.5 * (t_read0 + t_read1)
    n = int(np.clip(42000 * (px / 85.0) ** 2, 42000, 150000))
    return dict(pos=tuple(PW.place(_LAYOUT, tm, x, y, depth)), em=PW.em_for(_LAYOUT, tm, depth, px),
                t_in=t_in, t_read0=t_read0, t_read1=t_read1, t_out=t_out, n=n, **kw)


_SPECS = [
    _word(0.50, 0.70, 1.0, 140, 0.0, 1.85, 5.0, 6.7, expr="Greeting", arrive="touch", source=tuple(P1),
          touch_at=(T_TOUCH - 0.0) / 1.85, leave="rise"),
    _word(0.50, 0.77, 0.95, 110, 7.25, 8.0, 10.5, 11.3, expr="Compliment", arrive="touch",
          source=tuple(P2), touch_at=(T_FIVE - 7.25) / 0.75, leave="rise"),
    _word(0.56, 0.62, 1.02, 112, 10.1, 10.75, 13.25, 14.3, expr="Concession", arrive="palm", source=_sweep_palm,
          blow=(0.2, 1.0, 0.2), leave="wind", wind=(1.0, 0.3, -0.3)),
    _word(0.50, 0.72, 1.08, 84, 13.7, 15.0, 18.6, 19.85, expr="Gratitude", arrive="palm",
          source=tuple(P3 + np.array([0.0, 0.07, 0.0])), blow=(0.0, 1.0, 0.1), leave="rise"),
    _word(0.50, 0.73, 1.0, 92, 20.0, 20.9, 23.45, 23.45, expr="Apology", arrive="reveal", edge="right",
          leave="morph"),
    _word(0.50, 0.73, 1.0, 104, 23.45, 24.15, 26.75, 27.4, expr="Inclusiveness", arrive="morph",
          source="Apology", leave="wind", wind=(0.8, 0.5, -0.4)),
    _word(0.50, 0.72, 1.0, 104, 27.0, 28.5, 31.7, 33.3, expr="Respect", arrive="lake", leave="wind",
          wind=(-0.8, 0.5, -0.3)),
    _word(0.42, 0.72, 1.06, 104, 33.0, 34.4, 37.4, 38.9, expr="Consideration", arrive="touch",
          source=tuple(P6 + np.array([0.04, 0.02, 0.0])), touch_at=(T_GRIP - 33.0) / 1.4, leave="rise"),
    _word(0.50, 0.72, 10.0, 96, 40.4, 44.0, 47.6, 49.3, expr="Encouragement", arrive="shaft", leave="bokeh"),
]
WORDS = PW.Words(_SPECS, face="camera")
CAMERA = _rig()


# ----------------------------------------------------------------------------------------------- the scene
GOLD, BLUE = "#ffc46b", "#6fb8ff"


def _setup(scene):
    # 1 first touch
    scene.add("t1_gold", hand("woman", "R", _touch_at(0), _AIM1[0], (0.0, 1.0, 0.15), "offer", GOLD, "#fff1d6",
                             show=(-1.0, 7.4), anchor="fingertips", trail=-_AIM1[0], seed=2.0))
    scene.add("t1_blue", hand("man", "L", _touch_at(1), _AIM1[1], (0.0, -1.0, 0.1), "open", BLUE, "#e8f4ff",
                             show=(-1.0, 7.4), anchor="fingertips", trail=-_AIM1[1], seed=3.0))
    scene.add("t1_flare", Flare(P1, T_TOUCH, color=GOLD, color2=BLUE, n=1400, strength=0.35, reach=0.55, life=2.2))
    # 2 high five, after you
    scene.add("t2_child", hand("child", "R", _five_child, (0.25, 1.0, 0.1), (1.0, 0.0, 0.05), "spread", "#ff977c",
                               "#fff0e8", show=(6.4, 10.9), trail=(-0.6, -0.8, 0.0), seed=4.0, points=40000))
    scene.add("t2_big", hand("man", "L", _five_big, _five_big_aim, _five_big_palm,
                             [(7.0, "spread"), (T_SWEEP - 0.3, "spread"), (T_SWEEP + 0.6, "offer")], "#8fc4ff",
                             "#ffffff", show=(6.4, 14.3), trail=(0.6, 0.8, 0.0), seed=5.0))
    scene.add("t2_flare", Flare(P2, T_FIVE, color="#ff977c", color2="#8fc4ff", n=1600, strength=0.4, reach=0.7,
                                life=2.0))
    # 3 the flame
    for side, (a, aim, palm) in _cup(P3, 0.042).items():
        scene.add("t3_" + side, hand("woman", side, a, aim, palm, "cup", "#ffb27a", "#ffe6c4",
                                     show=(13.1, 20.4), trail=(0.0, -0.2, -1.0), seed=6.0 + (side == "L"),
                                     shed_n=2000))
    scene.add("t3_flame", Flame(P3 + np.array([0.0, 0.035, 0.0]), T_FLAME, 20.2))
    scene.add("t3_flare", Flare(P3 + np.array([0.0, 0.05, 0.0]), T_FLAME, color="#ffd78a", color2="#ff9e3d",
                                n=900, strength=0.3, reach=0.4, life=1.8))

    # 4 mending: an open hand comes down on a fist; the fist opens and turns up; the hands clasp
    def fist_palm(t):
        u = _ss(T_CLASP - 0.75, T_CLASP + 0.05, t)
        return _slerp(_slerp((0.0, -1.0, 0.0), (0.0, 0.0, 1.0), min(2 * u, 1.0)), (0.0, 1.0, 0.0),
                      max(2 * u - 1.0, 0.0))

    def rest_at(t):
        down = _ss(T_REST - 0.55, T_REST, t)
        onto = _ss(T_CLASP - 0.6, T_CLASP + 0.1, t)
        p = P4 + np.array([-0.30 * (1 - down), 0.065 + 0.26 * (1 - down) - 0.035 * onto, 0.04 * (1 - down)])
        return p

    scene.add("t4_fist", hand("woman", "L", P4 + np.array([0.02, 0.0, 0.0]), (-1.0, 0.0, 0.18), fist_palm,
                              [(19.0, "fist"), (21.6, "fist"), (T_CLASP - 0.6, "open"), (T_CLASP + 0.3, "hold")],
                              "#ff6a4a", "#ffd0b0", show=(19.6, 27.2), trail=(1.0, 0.0, -0.3), seed=8.0))
    scene.add("t4_open", hand("man", "R", rest_at, (1.0, 0.0, 0.12), (0.0, -1.0, 0.0),
                              [(19.0, "relaxed"), (T_CLASP - 0.3, "relaxed"), (T_CLASP + 0.3, "hold")],
                              "#ffad69", "#fff0e0", show=(19.6, 27.2), trail=(-1.0, 0.0, -0.3), seed=9.0))
    scene.add("t4_flare", Flare(P4 + np.array([0.0, 0.04, 0.0]), T_CLASP, color="#f582af", color2="#fff0f6",
                                n=1200, strength=0.3, reach=0.5, life=2.0))

    # 5 water: two cupped hands rise out of the lake with glowing water
    def cup5(side):
        a, aim, palm = _cup(P5, 0.042)[side]
        return lambda t: a + np.array([0.0, -0.13 * (1.0 - _ss(T_WATER - 0.1, T_WATER + 0.8, t)), 0.0])

    for side in ("R", "L"):
        _, aim, palm = _cup(P5, 0.042)[side]
        scene.add("t5_" + side, hand("woman", side, cup5(side), aim, palm, "cup", "#7fe6e0", "#e8fffd",
                                     show=(26.6, 33.8), trail=(0.0, -0.3, -1.0), seed=10.0 + (side == "L"),
                                     shed_n=2000))
    pool = Pool(P5 + np.array([0.0, 0.03, 0.0]), T_WATER + 0.3, 33.6)

    class _PoolRide:
        def gain(self, t):
            return 1.0

        def sample(self, t):
            c = P5 + np.array([0.0, 0.03 - 0.13 * (1.0 - _ss(T_WATER - 0.1, T_WATER + 0.8, t)), 0.0])
            return pool.sample(t, c)

    scene.add("t5_pool", _PoolRide())
    scene.add("t5_flare", Flare(P5 + np.array([0.0, 0.02, 0.0]), T_WATER, color="#7fe6e0", color2="#ffffff",
                                n=1000, strength=0.3, reach=0.6, life=2.0))

    # 6 the lift: a hand from above closes round a wrist reaching up; then it lifts
    def low_at(t):
        u = _ss(T_GRIP - 0.7, T_GRIP, t)
        return P6 + np.array([0.0, 0.10 - 0.22 * (1 - u) + _lift(t), 0.0])

    def high_at(t):
        u = _ss(T_GRIP - 0.7, T_GRIP, t)
        return P6 + np.array([0.035 + 0.26 * (1 - u), 0.015 + 0.30 * (1 - u) + _lift(t), 0.02])

    scene.add("t6_low", hand("man", "R", low_at, (0.05, 1.0, 0.12), (0.0, 0.1, 1.0),
                             [(32.0, "open"), (T_GRIP - 0.2, "open"), (T_GRIP + 0.4, "relaxed")], "#b293e7",
                             "#f0e8ff", show=(33.0, 40.6), trail=(0.0, -1.0, 0.0), seed=12.0))
    scene.add("t6_high", hand("woman", "L", high_at, (-0.55, -0.80, 0.25), (-1.0, 0.15, 0.1),
                              [(32.0, "open"), (T_GRIP - 0.3, "open"), (T_GRIP + 0.2, "hold")], "#ef7a96",
                              "#ffe8ee", show=(33.0, 40.6), trail=(0.6, 0.8, 0.0), seed=13.0))
    scene.add("t6_flare", Flare(lambda t: P6 + np.array([0.02, 0.03 + _lift(t), 0.0]), T_GRIP, color="#ef7a96",
                                color2="#ffffff", n=1200, strength=0.3, reach=0.5, life=2.0))

    # 7 hands pressed in prayer (the breath), then a forest of raised hands at sunrise
    for side, sgn in (("R", -1.0), ("L", 1.0)):
        scene.add("t7_" + side, hand("woman", side, P7 + np.array([sgn * 0.013, 0.0, 0.0]), (sgn * -0.04, 1.0, 0.12),
                                     (-sgn, 0.0, 0.0), "flat", "#ffe2b0", "#ffffff", show=(39.6, 49.6),
                                     trail=(0.0, -1.0, 0.0), seed=14.0 + (side == "L"), shed_n=1500))
    nine = [e["color"] for e in PW.EXPRESSIONS]
    rng = np.random.default_rng(7)
    for i in range(18):
        z = P7[2] - 0.7 - 4.5 * (i % 6) / 5.0 - rng.uniform(0.0, 0.5)
        x = P7[0] + ((i // 6) - 1.0) * (0.7 + 0.35 * (P7[2] - z)) + rng.uniform(-0.45, 0.45) + (i % 2) * 0.3
        y = P7[1] + 0.25 + rng.uniform(-0.2, 0.35)
        t_up = BIG + 0.05 + 0.10 * (i % 6) + 0.05 * (i // 6)
        side = "R" if i % 2 else "L"

        def up_at(t, x=x, y=y, z=z, t_up=t_up):
            return np.array([x, y - 1.2 * (1.0 - _ss(t_up, t_up + 0.7, t)) + 0.04 * np.sin(2.1 * t + x), z])

        scene.add("crowd_%d" % i, hand("woman" if i % 3 else "man", side, up_at,
                                       (0.15 * np.sin(i), 1.0, -0.1), (0.0, 0.1, -1.0), "open", nine[i % 9],
                                       "#ffffff", show=(BIG - 0.2, 50.0), points=12000, shed=False,
                                       seed=20.0 + i, fade=0.3))
    # 8 Her hands, holding the light of the world, seen from behind the wrists
    for side, sgn in (("R", -1.0), ("L", 1.0)):
        a = P8 + np.array([sgn * 0.050, 0.0, 0.0])
        scene.add("t8_" + side, Painted(hand("woman", side, a, _u((sgn * 0.20, 0.25, -1.0)), _u((-sgn * 0.45, 1.0, 0.0)),
                                     "cup", "#fff0d0", "#ffd27a", show=(49.2, 60.0), points=70000,
                                     trail=(0.0, 0.3, 1.0), seed=30.0 + (side == "L"), shed_n=3000, fade=0.2), "#f2b54a"))
    scene.add("t8_globe", Globe(GLOBE, 0.048, S[7]))
    WORDS.add_to(scene)
    WORDS.check(CAMERA)


# ------------------------------------------------------------------------------------------------ the world
LOOKS = dict(
    touch=dict(base="night", sky_top="#020617", sky_mid="#081536", sky_hor="#1b2f66", haze_color="#0c1a44",
               dust_color="#ffb04a", dust_color2="#58a8ff", bokeh=1.2, dust=0.9),
    play=dict(base="night", sky_top="#04103a", sky_mid="#123070", sky_hor="#2f66b0", haze_color="#17347a",
              dust_color="#ffd27a", dust_color2="#7fd0ff", bokeh=1.2, dust=0.9, stars=0.8),
    ember=dict(base="dusk", sky_top="#0d0618", sky_mid="#2a0f24", sky_hor="#6a2a22", haze_color="#3a1418",
               sun_color="#ffb347", dust_color="#ff9e3d", dust_color2="#ffd05f", bokeh=1.3, dust=0.9, stars=0.4),
    mend=dict(base="dusk", sky_top="#120a2e", sky_mid="#3a1c5a", sky_hor="#a04a78", haze_color="#4a2460",
              sun_color="#ffb4a0", dust_color="#ffad69", dust_color2="#f582af", bokeh=1.2, dust=0.9),
    water=dict(base="night", sky_top="#04142c", sky_mid="#0c3a5a", sky_hor="#2f8a9a", haze_color="#0e4660",
               mist_color="#1a5a6a", water="#03121c", dust_color="#7fe6e0", dust_color2="#cfe8fa", bokeh=1.2,
               dust=0.9, stars=0.6, ripple=0.4),
    rise=dict(base="dawn", sun_el=1.5, sun_int=1.1, rays=0.8, sky_top="#0b1640", sky_mid="#3b3478",
              stars=0.25, dust_color="#ffd9a0", dust_color2="#ffc4e0", bokeh=1.2, dust=0.9),
    her=dict(base="day", water="#0e2c5c", mirror=0.55, mirror_min=0.2, rays=0.25),
    breath=dict(base="predawn", sky_top="#0c1430", sky_mid="#26365e", sky_hor="#8a6f8e", haze_color="#2a3458",
                dust_color="#8ea0c8", dust_color2="#ef7a96", bokeh=0.9, dust=0.6),
)
P3D = dict(
    camera=CAMERA,
    world=dict(
        looks=LOOKS,
        look=[(0.0, "touch"), (S[1], "play", 0.4), (S[2] + 0.2, "ember", 0.5), (S[3], "mend", 0.0),
              (S[4], "water", 0.0), (S[5], "predawn", 0.0), (S[6], "breath", 1.2), (BIG, "rise", 0.5),
              (S[7], "her", 0.0)],
        sun_az=180.0,
        light=dict(pos=lambda t: (P3 + np.array([0.0, 0.08, 0.0])) if t < 30.0 else GLOBE,
                   color="#ffc070",
                   strength=lambda t: (0.9 * _ss(T_FLAME - 0.2, T_FLAME + 0.3, t) * (1 - _ss(19.6, 19.85, t))
                                       + 0.35 * _ss(S[7], S[7] + 1.0, t)),
                   size=0.12, rays=1.0),
        lights=[dict(pos=tuple(P5 + np.array([0.0, 0.05, 0.0])), color="#7fe6e0",
                     strength=lambda t: 1.4 * _ss(T_WATER, T_WATER + 0.6, t) * (1 - _ss(33.0, 33.36, t)),
                     radius=1.2)],
        shafts=[dict(base=(P7[0], P7[2]), radius=0.7, top=30.0, color="#dfe8ff",
                     strength=lambda t: 0.8 * _ss(S[6] - 0.3, S[6] + 0.6, t) * (1 - _ss(BIG, BIG + 1.5, t)))],
        react=dict(beat=0.5, level=0.3),
    ),
    bursts=[dict(t=T_TOUCH, at=tuple(P1), strength=0.9, radius=0.10, color="#fff3d6", rise=0.06, fall=0.45),
            dict(t=T_FIVE, at=tuple(P2), strength=0.8, radius=0.10, color="#ffe8e0", rise=0.05, fall=0.4),
            dict(t=T_FLAME, at=tuple(P3), strength=0.6, radius=0.12, color="#ffd78a", rise=0.12, fall=0.5),
            dict(t=S[3], strength=1.6, radius=0.45, color="#fff0e6", rise=0.10, fall=0.55),
            dict(t=T_CLASP, at=tuple(P4), strength=0.6, radius=0.12, color="#fff0f6", rise=0.08, fall=0.5),
            dict(t=S[4], strength=1.6, radius=0.45, color="#e8fffd", rise=0.10, fall=0.55),
            dict(t=S[5], strength=1.6, radius=0.45, color="#fff0f6", rise=0.10, fall=0.55),
            dict(t=BIG, strength=2.0, radius=0.5, color="#fff2d8", rise=0.10, fall=0.8),
            dict(t=S[7], strength=2.2, radius=0.55, color="#ffffff", rise=0.12, fall=0.9)],
    motion_blur=0.4,
    setup=_setup,
)

# ------------------------------------------------------------------------------------------------ the end card
T_FORM = 52.3
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=53.9, t1=54.7, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
FRAGMENTS = []
