"""Song 10, Our Mother Saves the World: the full-length concert backdrop (one continuous video).

Built on the approved Nine Colours Revision 3 look (pinned Film 10 engine d928ff9 for the world, the camera and
the renderer; Claude Final v1, commit f43f451, for the cream serif words with coloured capsule labels and the warm
gold glitter people). The song's own design: "The Lamp on the Shore" (project-docs/designs/10 Our Mother Saves
the World.md). Every time here is SONG time in seconds: 0 is the first sample of the recording (211.61 s); the
picture holds 15 s after it, calm and alive, never black. Section timeline: project-docs/backdrops/s10-full/
TIMELINE.md (the numbers below are the source).

THE STORY ON THE MUSIC
  0:00     the restless night: wide, still, slightly high. The title reads from frame 0. Three small warm
           lights far out on the lake (song 09's boats); the lamp is the one small warm star at the centre of
           the horizon under the lit arch of nine lights.
  0:10.5   the camera rises slowly: the dark lake widens, scattered dim lights on it.
  0:25.3   (hit) the star swells: the lamp. The camera comes down behind Heavenly Mother, seen only from behind,
           fully robed and veiled, at the water's edge; she lifts the lamp in both hands (0:33 to 0:36).
  0:38.5   the loudest phrase: nine comets of colour leave the lamp and run out over the water; a few lights warm.
  0:52     (hit) Her words reach people, one at a time; each thread arrives, the light warms, a ring opens:
           0:57.5 GREETING (two men bow to each other), 1:14 CONSIDERATION (a man helps another to his feet),
           1:31.5 INCLUSIVENESS (two women embrace), 1:58.5 ENCOURAGEMENT (one prays for her friend).
  1:43.5   wide: lights warming all over the lake, rings spreading.
  2:07     peace across the world: the camera rises high; the nine comets weave a web across the whole lake,
           every light gold, the water calming, gold motes rising, the horizon a deep gold band.
  2:30     soft: down again toward the shore.
  2:40     the people of light gather on the water road facing the lamp (seen from behind).
  3:13.5   GRATITUDE (two women): thanks for the One who saved us.
  3:21     the comets rise into their own lights of the arch; on the last hit (3:25.1) the arch shines.
  3:29     night of peace: home view, deep indigo, stars, the lamp resting as a warm star with a faint glow,
           a calm mirror, all nine lights steady (the agreed hand-off frame to song 11). Hold to 3:46.6.

No em dash or en dash anywhere in this file.
"""
import os
import sys

import numpy as np

import songs.s03_original as _base

MUSIC_FILE_END = 211.605          # length of the recording
MUSIC_END = 209.3                 # the last chord has rung out
HOLD = 15.0
FPS_OUT = 30
NF = int(np.ceil((MUSIC_FILE_END + HOLD) * FPS_OUT))   # 6799 frames
TOTAL = NF / FPS_OUT                                     # 226.633 s
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = MUSIC_END
_base.SONG_END = MUSIC_FILE_END
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "nine_colours_minor"))
import reference  # noqa: E402,F401  (registers nine_reference_p3d: Claude Final v1 words and bodies)
from nine_reference_p3d import words as PW  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"     # not used for the picture (FEATURES are this song's)
TOTAL = NF / FPS_OUT
NFRAMES = int(round(TOTAL * FPS))
SONG_END = MUSIC_FILE_END
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE
FRAGMENTS = []
WAVES = []

# ---------------------------------------------------------------------------------------------------------
# The measured music (TIMELINE.md)
# ---------------------------------------------------------------------------------------------------------
HITS = dict(break1=22.62, lamp=25.33, return1=52.04, loud=129.2, h3=191.47, last=205.11)
LOUDEST = 38.5

LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)


def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _smoother(u):
    u = min(max(float(u), 0.0), 1.0)
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _unit(a):
    a = np.asarray(a, np.float64)
    return a / max(float(np.linalg.norm(a)), 1e-9)


# ---------------------------------------------------------------------------------------------------------
# Geography (metres, y up, the lake is y = 0; we look toward -z, where the lamp rests on the horizon)
# ---------------------------------------------------------------------------------------------------------
MOTHER = _v(0.0, 0.0, 30.0)               # Heavenly Mother at the water's edge (seen from behind)
LAMP_H = 2.12                              # the lamp in her raised hands
MOTHER_CAM = _v(0.0, 1.5, 44.0)
LAMP_EL = float(np.degrees(np.arctan2(LAMP_H - MOTHER_CAM[1], MOTHER_CAM[2] - MOTHER[2])))   # the star behind it
LAMP_PT = MOTHER + _v(0.0, LAMP_H, -0.22)

ARCH = dict(span=84.0, height=34.0, z=-70.0)

# the expression moments: stage (where the two stand), words (in, read, read end, out), act (t0, t1)
MOMENTS = [
    dict(expr="Greeting", k=GREET, at=_v(-14.0, 0.0, 8.0), yaw=-24.0, words=(56.0, 57.5, 66.5, 67.3)),
    dict(expr="Consideration", k=CONS, at=_v(13.0, 0.0, -2.0), yaw=22.0, words=(72.6, 74.0, 83.0, 83.8)),
    dict(expr="Inclusiveness", k=INCL, at=_v(-9.0, 0.0, -16.0), yaw=-22.0, words=(90.2, 91.6, 101.0, 101.8)),
    dict(expr="Encouragement", k=ENC, at=_v(8.0, 0.0, 14.0), yaw=24.0, words=(117.0, 118.5, 127.0, 127.8)),
    dict(expr="Gratitude", k=GRAT, at=_v(-6.0, 0.0, 20.0), yaw=-22.0, words=(192.0, 193.6, 202.6, 203.4)),
]
BY = {m["expr"]: m for m in MOMENTS}
SHORE_LINE = dict(t_in=158.5, t_out=218.5)        # the people of light on the water road, facing the lamp
LINE_Z = 33.0
LINE_X = [-6.6, -4.4, -2.2, 2.2, 4.4, 6.6]

# ---------------------------------------------------------------------------------------------------------
# The camera: held shots joined by slow eased moves (performers stand in front: never fast, no orbits)
# ---------------------------------------------------------------------------------------------------------
MED_D, MED_H, MED_TY, MED_FOV = 11.0, 1.9, 1.4, 36.0


def _medium(m):
    """A steady medium shot of a moment, turned by `yaw` so the lamp sits off to the side, not behind words."""
    a = np.radians(m["yaw"])
    back = _v(np.sin(a), 0.0, np.cos(a))
    pos = m["at"] + back * MED_D + _v(0.0, MED_H, 0.0)
    tgt = m["at"] + _v(0.0, MED_TY, 0.0)
    return pos, tgt, MED_FOV


HOME = (_v(0.0, 4.2, 60.0), _v(0.0, 3.4, 0.0), 46.0)
HIGH0 = (_v(0.0, 9.0, 66.0), _v(0.0, 4.6, 0.0), 46.0)
HIGH1 = (_v(0.0, 19.0, 84.0), _v(0.0, 5.5, 0.0), 48.0)
MOTHER_A = (MOTHER_CAM, _v(0.0, 2.05, 0.0), 40.0)
MOTHER_B = (MOTHER_CAM + _v(0.0, 0.05, -2.4), _v(0.0, 2.05, 0.0), 40.0)
WIDE_MID = (_v(0.0, 11.0, 72.0), _v(0.0, 2.5, -10.0), 50.0)
PEACE = (_v(0.0, 24.0, 92.0), _v(0.0, 4.0, -20.0), 52.0)
PEACE_B = (_v(0.0, 27.0, 96.0), _v(0.0, 4.5, -24.0), 52.0)
SHORE = (_v(0.0, 2.6, 49.0), _v(0.0, 2.3, 0.0), 42.0)
SHORE_B = (_v(0.0, 2.8, 51.0), _v(0.0, 2.6, 0.0), 42.0)

# (time, pose): the camera holds a pose until the next key's move starts; a key with a move duration eases
# from the previous pose to its own over that many seconds ending at its time.
SHOTS = [
    (0.0, HIGH0, 0.0),
    (10.5, HIGH0, 0.0),
    (24.0, HIGH1, 13.5),                      # the slow rise: the night widens
    (31.0, MOTHER_A, 6.0),                    # down behind Heavenly Mother after the lamp hit
    (49.5, MOTHER_B, 18.5),                   # a slow push as she holds the lamp up
    (56.2, _medium(BY["Greeting"]), 6.0),
    (67.5, _medium(BY["Greeting"]), 0.0),
    (73.0, _medium(BY["Consideration"]), 5.5),
    (84.2, _medium(BY["Consideration"]), 0.0),
    (90.5, _medium(BY["Inclusiveness"]), 6.0),
    (102.0, _medium(BY["Inclusiveness"]), 0.0),
    (108.5, WIDE_MID, 6.5),                   # lights warming all over the lake
    (110.5, WIDE_MID, 0.0),
    (117.3, _medium(BY["Encouragement"]), 6.8),
    (127.6, _medium(BY["Encouragement"]), 0.0),
    (136.0, PEACE, 8.4),                      # peace across the world: high and wide
    (150.0, PEACE_B, 14.0),
    (159.0, SHORE, 9.0),                      # down to the water road; the people gather
    (186.0, SHORE_B, 27.0),
    (192.6, _medium(BY["Gratitude"]), 6.6),
    (203.6, _medium(BY["Gratitude"]), 0.0),
    (211.0, HOME, 7.4),                       # night of peace: the home view (hand-off to song 11)
    (TOTAL + 1.0, HOME, 0.0),
]


def _pose(t):
    prev = SHOTS[0][1]
    for i, (tk, pose, dur) in enumerate(SHOTS):
        if t < tk - dur:
            return prev, prev, 0.0
        if t < tk:
            u = _smoother((t - (tk - dur)) / max(dur, 1e-6))
            return prev, pose, u
        prev = pose
    return prev, prev, 0.0


def _cam_raw(t):
    a, b, u = _pose(t)
    p = a[0] * (1.0 - u) + b[0] * u
    # aim: blend the look direction (not the target point) so a turn stays smooth
    da, db = a[1] - a[0], b[1] - b[0]
    la, lb = float(np.linalg.norm(da)), float(np.linalg.norm(db))
    d = _unit(_unit(da) * (1.0 - u) + _unit(db) * u) * (la * (1.0 - u) + lb * u)
    fov = a[2] * (1.0 - u) + b[2] * u
    # gently alive: a very slow breathing drift (a few centimetres)
    p = p + _v(0.05 * np.sin(0.21 * t), 0.03 * np.sin(0.17 * t + 1.0), 0.0)
    return p, p + d, fov


class Path(Move):
    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q, _ = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _focus_dist(t):
    p, q, _ = _cam_raw(t)
    return float(np.linalg.norm(q - p))


CAMERA = Rig([Path(_cam_raw, -1.0, TOTAL + 2.0, blend=0.0, fov=lambda t: _cam_raw(t)[2], roll=0.0,
                   aperture=0.0, focus=_focus_dist)],
             blend=0.0, fov=46.0, aperture=0.0, handheld=0.0, min_height=0.3)
_LAYOUT = CAMERA


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


# ---------------------------------------------------------------------------------------------------------
# The words: five of the nine, exact campaign wording, Claude Final v1 type (cream serif, coloured capsule)
# ---------------------------------------------------------------------------------------------------------
DEPTH = 7.0
WIDTHS = dict(Greeting=.32, Consideration=.46, Inclusiveness=.50, Encouragement=.52, Gratitude=.56)
RIDE_Y = .615                      # block centre about .345 of the height from the top


def _width(t, depth, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _clean_leave(t, info):
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)


def _specs():
    out = []
    for m in MOMENTS:
        t_in, r0, r1, t_out = m["words"]
        out.append(dict(expr=m["expr"], ride=(.5, RIDE_Y, DEPTH), face="screen",
                        width=_width(.5 * (r0 + r1), DEPTH, WIDTHS[m["expr"]]), pill=True,
                        t_in=t_in, t_read0=r0, t_read1=r1, t_out=t_out, arrive="pen", nib=False, leave="fade"))
    return out


WORDS = PW.Words(_specs(), camera=_LAYOUT, reflect=False, drive=_clean_leave)


def word_boxes(t, cam):
    out = []
    for w in WORDS:
        if w.t_in <= t <= w.t_out:
            x0, x1, y0, y1, front, *_ = PW.screen_box(w, cam, t)
            if front:
                out.append((x0 - .03, x1 + .03, y0 - .045, y1 + .045))
    return out


# ---------------------------------------------------------------------------------------------------------
# The arch of nine lights: lit from the start; a light shines again when its word is spoken, and all nine on
# the last hit
# ---------------------------------------------------------------------------------------------------------
def _flare(t, t0, amp=0.9):
    if t < t0 - 0.4:
        return 0.0
    if t < t0:
        return amp * _sc(t0 - 0.4, t0, t)
    return amp * float(np.exp(-(t - t0) / 1.6))


ARCH_FLARE = {m["k"]: m["words"][2] + 0.6 for m in MOMENTS}


def _arch_lit(t):
    out = []
    for k in range(9):
        b = 0.62
        if k in ARCH_FLARE:
            b += _flare(t, ARCH_FLARE[k])
        b += _flare(t, HITS["last"] + 0.1, 0.7)
        out.append((b, 30.0))
    return out


ARCH_CFG = dict(lit=_arch_lit, colors=COL, span=ARCH["span"], height=ARCH["height"], z=ARCH["z"],
                line=Track([(0.0, 0.0), (9.0, 0.0), (13.0, 0.7), (TOTAL, 0.7)]))


def arch_positions(t):
    from p3d.world import Arch
    return Arch(None, **{k: v for k, v in ARCH_CFG.items() if k not in ("lit",)}).positions(t)


# ---------------------------------------------------------------------------------------------------------
# The lights on the lake: people the words have not reached yet (dim, soft) who warm to gold when reached,
# each opening a ring of still water
# ---------------------------------------------------------------------------------------------------------
class LakeLights:
    def __init__(self, n=170):
        r = np.random.default_rng(1010)
        x = (r.random(n) - 0.5) * 2.0 * (18.0 + 50.0 * r.random(n))
        z = 34.0 - 120.0 * r.random(n) ** 0.8
        self.p = np.stack([x, 0.18 + 0.05 * r.random(n), z], axis=1)
        self.s = r.random((n, 4))
        # when each one is reached
        warm = np.full(n, 1e9)
        # three boats of song 09 (far out): warm from the start
        boats = [_v(-14.0, 0.2, -36.0), _v(2.0, 0.2, -44.0), _v(17.0, 0.2, -32.0)]
        # keep the water near every close camera clear of lights (calm bottom third)
        eyes = [_medium(m)[0] for m in MOMENTS] + [MOTHER_CAM, SHORE[0]]
        for e in eyes:
            for _ in range(3):
                d = self.p[:, [0, 2]] - e[[0, 2]]
                dist = np.linalg.norm(d, axis=1)
                near = dist < 13.0
                self.p[near, 2] -= 14.0
        self.p[:3] = boats
        warm[:3] = -10.0
        d = np.linalg.norm(self.p[:, [0, 2]] - LAMP_PT[[0, 2]], axis=1)
        idx = np.arange(3, n)
        # first touches after the comets leave the lamp
        first = idx[np.argsort(d[idx])][:10]
        warm[first] = 40.0 + 9.0 * r.random(10)
        # near each moment: the ones close to the stage are reached as its words arrive
        for m in MOMENTS[:4]:
            dm = np.linalg.norm(self.p[:, [0, 2]] - m["at"][[0, 2]], axis=1)
            near = [i for i in np.argsort(dm) if warm[i] > 1e8 and i >= 3][:4]
            warm[near] = m["words"][0] + 0.8 + 1.6 * r.random(len(near))
        # the wide shot: many more
        rest = [i for i in idx if warm[i] > 1e8]
        r.shuffle(rest)
        k = len(rest) // 2
        warm[rest[:k]] = 104.0 + 13.0 * r.random(k)
        # peace across the world: all the rest, a wave from the middle out
        rr = np.array(rest[k:])
        dr = np.linalg.norm(self.p[rr][:, [0, 2]] - _v(0, 0, -20)[[0, 2]], axis=1)
        warm[rr] = 128.0 + 14.0 * dr / max(dr.max(), 1.0) + 0.6 * r.random(len(rr))
        self.warm = warm
        self.ring_n = 56
        self.ang = np.linspace(0.0, 2.0 * np.pi, self.ring_n, endpoint=False)

    def sample(self, t):
        age = t - self.warm
        lit = _ss(0.0, 1.4, age)
        dim = lin("#b8a7c4") * 0.30
        gold = lin("#ffb066")
        col = dim[None, :] * (1.0 - lit)[:, None] + gold[None, :] * lit[:, None]
        tw = 0.85 + 0.15 * np.sin(t * (0.7 + 0.8 * self.s[:, 0]) + 6.0 * self.s[:, 1])
        end = 1.0 - 0.35 * _sc(209.0, 218.0, t)
        out = [dict(pos=self.p, size=0.15 + 0.10 * lit, color=col, alpha=(0.55 + 0.45 * lit) * tw * end,
                    emit=1.0 + 1.6 * lit, kind="spark", seed=self.s[:, 2], twinkle=0.3),
               dict(pos=self.p, size=0.9 + 0.7 * lit, color=col, alpha=(0.04 + 0.07 * lit) * end, kind="soft")]
        # rings of still water: one per reached light, opening over 3.5 s
        on = (age > 0.0) & (age < 4.5) & (self.warm > 0.0)
        if np.any(on):
            a = age[on]
            rad = 0.3 + 2.4 * (1.0 - np.exp(-a / 1.3))
            al = _ss(0.0, 0.3, a) * (1.0 - _ss(1.6, 4.5, a))
            c = self.p[on]
            ring = c[:, None, :] + rad[:, None, None] * np.stack(
                [np.cos(self.ang), np.zeros(self.ring_n), np.sin(self.ang)], axis=1)[None, :, :]
            ring[:, :, 1] = 0.04
            out.append(dict(pos=ring.reshape(-1, 3), size=0.05, color=lin("#ffd38a"),
                            alpha=np.repeat(al * 0.35, self.ring_n), emit=1.2, kind="spark"))
        return out


# ---------------------------------------------------------------------------------------------------------
# The nine comets: Her words as threads of colour. Born from the lamp at the loudest phrase; one comes down to
# each moment; they weave a web across the lake at the peak; at the end they rise into their own lights.
# ---------------------------------------------------------------------------------------------------------
BIRTH = LOUDEST
RISE_T0, RISE_T1 = 196.0, HITS["last"]
WEB_T0, WEB_T1 = 128.5, 152.0


def _ring(k, t):
    a = 2.0 * np.pi * k / 9.0 + 0.035 * t * (1 if k % 2 == 0 else -1)
    r = 95.0 + 12.0 * (k % 3)
    return _v(np.sin(a) * r, 24.0 + 6.0 * ((k * 2) % 5) + 2.0 * np.sin(0.3 * t + k), -40.0 + np.cos(a) * r * 0.6)


def _fan(k, t):
    u = max(t - BIRTH, 0.0)
    ang = np.radians(-80.0 + 20.0 * k)
    d = _v(np.sin(ang), 0.0, -np.cos(ang) * 0.6 + 0.4)
    dist = 26.0 * (1.0 - np.exp(-u / 1.8)) + 2.0 * u
    return LAMP_PT + d * dist + _v(0.0, 0.8 * u + 1.2 * np.sin(1.3 * u), 0.0)


def _web(k, t):
    w = 0.23 + 0.03 * k
    ph = 1.1 * k
    x = 52.0 * np.sin(w * t + ph)
    z = -25.0 + 42.0 * np.sin(0.5 * w * t + 2.0 * ph + 0.7)
    return _v(x, 4.0 + 2.5 * np.sin(0.9 * t + k), z)


def _circle(m):
    c = m["at"]

    def f(t):
        a = 1.15 * t + m["k"]
        return c + _v(1.9 * np.sin(a), 0.55 + 0.25 * np.sin(1.7 * t), 1.9 * np.cos(a))
    return f


def _to_star(k):
    def f(t):
        u = _smoother((t - RISE_T0) / (RISE_T1 - RISE_T0))
        p0 = _ring(k, RISE_T0)
        p1 = arch_positions(t)[k]
        mid = 0.5 * (p0 + p1) + _v(0.0, 10.0, 0.0)
        return (1 - u) ** 2 * p0 + 2 * (1 - u) * u * mid + u * u * p1
    return f


class Head:
    def __init__(self, k):
        self.k = k
        self.legs = []

    def leg(self, t0, t1, f, bi=2.0, bo=2.5):
        self.legs.append((t0, t1, f, bi, bo))
        return self

    def base(self, t):
        w = _sc(BIRTH + 3.0, BIRTH + 10.0, t)
        if w <= 0.0:
            return _fan(self.k, t)
        if w >= 1.0:
            return _ring(self.k, t)
        return _fan(self.k, t) * (1.0 - w) + _ring(self.k, t) * w

    def __call__(self, t):
        p = self.base(t)
        for t0, t1, f, bi, bo in self.legs:
            if t < t0 - bi or t > t1 + bo:
                continue
            w = _smoother((t - (t0 - bi)) / bi) * (1.0 - _smoother((t - t1) / bo))
            if w > 0.0:
                p = p * (1.0 - w) + np.asarray(f(t), np.float64) * w
        return p


HEADS = [Head(k) for k in range(9)]
for _m in MOMENTS:
    HEADS[_m["k"]].leg(_m["words"][0] - 1.5, _m["words"][2] + 0.3, _circle(_m), bi=3.5, bo=3.0)
for _k in range(9):
    HEADS[_k].leg(WEB_T0, WEB_T1, lambda t, k=_k: _web(k, t), bi=5.0, bo=6.0)
    HEADS[_k].leg(RISE_T0, RISE_T1 + 30.0, _to_star(_k), bi=0.01, bo=0.01)


def deepen(hexs, k=1.35):
    c = lin(hexs)
    m = float(c.max())
    return m * (c / m) ** k


class Comets:
    def __init__(self):
        r = np.random.default_rng(10)
        self.sp = r.random((9, 120, 4)).astype(np.float64)

    def _alpha(self, k, t):
        return _sc(BIRTH - 0.1, BIRTH + 0.8, t) * (1.0 - _sc(RISE_T1 - 0.4, RISE_T1 + 0.3, t))

    def _near(self, k, t):
        n = 0.0
        for t0, t1, f, bi, bo in HEADS[k].legs[:-1]:
            n = max(n, _sc(t0 - bi, t0, t) * (1.0 - _sc(t1, t1 + bo, t)))
        return n

    def sample(self, t):
        from p3d.api import ribbon
        out = []
        web = _sc(WEB_T0 - 4.0, WEB_T0, t) * (1.0 - _sc(WEB_T1, WEB_T1 + 5.0, t))
        for k in range(9):
            a = self._alpha(k, t)
            if a <= 0.0:
                continue
            near = self._near(k, t) * (1.0 - web)
            tail = 1.3 * near + 2.4 * (1.0 - near) + 3.5 * web
            w = 0.16 * near + 1.6 * (1.0 - near) * (1.0 - web) + 0.9 * web
            if t < BIRTH + 6.0:
                w = 0.35 + 0.6 * _sc(BIRTH, BIRTH + 6.0, t)
            n = 48
            ts = np.linspace(max(t - tail, BIRTH), t, n)
            if ts[-1] - ts[0] < 1e-3:
                continue
            pts = np.array([HEADS[k](float(x)) for x in ts])
            age = (t - ts) / tail
            kk = 1.0 - age
            c = lin(COL[k])
            core = 0.40 * c + 0.60 * lin("#fff1dc")
            out.append(ribbon(pts, width=w * (0.12 + 0.88 * kk), color=deepen(COL[k]),
                              alpha=a * 0.5 * np.clip(kk * 1.4, 0, 1), emit=1.5))
            out.append(ribbon(pts, width=w * 0.2 * (0.15 + 0.85 * kk), color=core,
                              alpha=a * 0.85 * np.clip(kk * 1.6, 0, 1), emit=2.2))
            head = pts[-1:]
            out.append(dict(pos=head, size=w * 0.6, color=core, alpha=a, emit=5.0, kind="spark"))
            out.append(dict(pos=head, size=w * 4.0, color=c, alpha=a * 0.12, kind="soft"))
            sp = self.sp[k]
            f = np.mod(sp[:, 0] + t * (0.5 + 0.3 * sp[:, 1]), 1.0)
            idx = f * (n - 1)
            i0 = np.floor(idx).astype(int)
            i1 = np.minimum(i0 + 1, n - 1)
            fr = (idx - i0)[:, None]
            base = pts[i0] * (1.0 - fr) + pts[i1] * fr
            drift = (sp[:, 1:4] - 0.5) * (w * 3.0) * (1.0 - f)[:, None]
            out.append(dict(pos=base + drift, size=w * (0.08 + 0.10 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                            alpha=a * 0.8 * f ** 1.5, emit=1.8, kind="spark", twinkle=0.6, seed=sp[:, 3]))
        return out


class Lamp:
    """The lamp in Heavenly Mother's hands, and its glow (the horizon star stands exactly behind it)."""

    def sample(self, t):
        k = _sc(27.0, 29.0, t) * (1.0 - _sc(51.0, 54.0, t))
        if k <= 0.0:
            return None
        lift = _sc(33.0, 36.2, t)
        p = LAMP_PT + _v(0.0, -0.85 * (1.0 - lift), -0.12 * (1.0 - lift))
        glow = 0.75 + 0.25 * lift + 0.12 * np.sin(2.1 * t)
        return [dict(pos=p[None, :], size=0.10, color=lin("#fff1d0"), alpha=k, emit=5.0 * glow, kind="spark"),
                dict(pos=p[None, :], size=0.9, color=lin("#ffbf4f"), alpha=0.22 * k * glow, kind="soft"),
                dict(pos=p[None, :], size=2.6, color=lin("#ffb347"), alpha=0.07 * k * glow, kind="soft")]

    def where(self, t):
        lift = _sc(33.0, 36.2, t)
        return LAMP_PT + _v(0.0, -0.85 * (1.0 - lift), -0.12 * (1.0 - lift))


LAMP = Lamp()


class Clear:
    """Light dims inside the reading bounds (nothing crosses a word)."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = word_boxes(t, cam)
        if not boxes:
            return got
        out = []
        for source in got if isinstance(got, (list, tuple)) else [got]:
            if source is None:
                continue
            b = dict(source)
            p = np.asarray(b["pos"]).reshape(-1, 3)
            xy, z = cam.project(p)
            end = None
            if b.get("pos2") is not None:
                end, _ = cam.project(np.asarray(b["pos2"]).reshape(-1, 3))
            gain = np.ones(len(p))
            for u in (np.linspace(0, 1, 9) if end is not None else [0]):
                q = xy if end is None else xy * (1 - u) + end * u
                for x0, x1, y0, y1 in boxes:
                    dx = np.minimum(q[:, 0] - x0, x1 - q[:, 0])
                    dy = np.minimum(q[:, 1] - y0, y1 - q[:, 1])
                    f = np.clip(np.minimum(dx, dy) / .025 + .5, 0, 1)
                    gain = np.minimum(gain, 1 - .98 * f * (z > 0))
            b["alpha"] = np.asarray(b.get("alpha", 1)) * gain
            if "alpha2" in b:
                b["alpha2"] = np.asarray(b["alpha2"]) * gain
            out.append(b)
        return out


# ---------------------------------------------------------------------------------------------------------
# The people of light (warm gold glitter; every touch between two of the same gender)
# ---------------------------------------------------------------------------------------------------------
GOLD = dict(look="glitter", color="#f2a640", color2="#ffdc96", bright=1.45)
CRYSTAL = dict(look=dict(name="glitter", seams=0.6), color="#ffc664", color2="#fff0c8", bright=1.45)


def _view(at, cam_pos):
    d = np.asarray(cam_pos, np.float64) - np.asarray(at, np.float64)
    return float(np.degrees(np.arctan2(d[0], d[2])))


def _mother():
    """Heavenly Mother, only from behind: fully robed, veiled to the ground, facing the horizon. Her hands rest
    cupped before her, then rise and hold the lamp up over the world."""
    from nine_reference_p3d.body import Body
    lamp = LAMP.where
    return Body("woman", at=(MOTHER[0], MOTHER[2]), facing=180.0, motion="stand", garment="robe",
                veil=dict(length=1.5), look=dict(name="glitter", seams=0.3), color="#ffc458", color2="#fff2d0",
                bright=1.55, points=70000, show=(26.5, 53.5), fade=1.6, seed=3.3, wind=(0.15, 0.0, 0.05),
                gesture=[(27.0, 33.2, "cup", dict(ease_in=1.4, ease_out=0.8)),
                         (32.8, 51.0, "raise_hand", dict(side="R", to=lambda t: lamp(t) + _v(0.07, -0.02, 0.0),
                                                       palm="up", fingers="cup", ease_in=1.6, ease_out=1.6)),
                         (32.8, 51.0, "raise_hand", dict(side="L", to=lambda t: lamp(t) + _v(-0.07, -0.02, 0.0),
                                                       palm="up", fingers="cup", ease_in=1.6, ease_out=1.6))],
                effects=[dict(kind="form", t=26.5, dur=2.4)])


def _greeting(m):
    """GREETING, two men: each gives a slight, warm bow to the other (as the approved masterpiece)."""
    from nine_reference_p3d.body import Body
    o = m["at"]
    t0, t1 = m["words"][1] - 1.0, m["words"][2]
    a_ = np.radians(_view(o, _medium(m)[0]))
    right = _v(np.cos(a_), 0.0, -np.sin(a_))
    pa, pb = o - right * 0.58, o + right * 0.58
    fa = float(np.degrees(np.arctan2(right[0], right[2])))
    a = Body("man", at=(pa[0], pa[2]), facing=fa, garment="tunic", points=75000, show=(t0 - 2.0, t1 + 1.6),
             fade=0.8, seed=21.0,
             gesture=[(t0, t1 + 1.0, "greet_bow", dict(amount=17.0, down=0.95, hold=0.55, up=1.1, ease_in=0.5,
                                                       ease_out=1.0)),
                      (t0 + 2.4, t1 + 1.0, "nod", dict(period=2.6, amount=4.0, ease_in=1.0))],
             effects=[dict(kind="form", t=t0 - 2.0, dur=1.6)],
             sweeps=dict(glow=dict(t=t0 + 0.2, at="heart", speed=2.5, width=0.35, flash=1.6)), **GOLD)
    b = Body("man", at=(pb[0], pb[2]), facing=fa + 180.0, garment="coat", points=75000, show=(t0 - 2.0, t1 + 1.6),
             fade=0.8, seed=22.0,
             gesture=[(t0 + 0.4, t1 + 1.0, "greet_bow", dict(amount=15.0, down=1.0, hold=0.5, up=1.1, ease_in=0.5,
                                                             ease_out=1.0)),
                      (t0 + 2.8, t1 + 1.0, "nod", dict(period=2.9, amount=4.0, ease_in=1.0))],
             effects=[dict(kind="form", t=t0 - 1.8, dur=1.6)],
             sweeps=dict(glow=dict(t=t0 + 0.55, at="heart", speed=2.5, width=0.35, flash=1.6)), **CRYSTAL)
    return [a, b]


def _acted(m, variant, shape):
    from nine_reference_p3d import acting
    o = m["at"]
    t0, t1 = m["words"][1] - 1.0, m["words"][2]
    view = _view(o, _medium(m)[0]) % 360.0
    sa = dict(shape=shape)
    sb = dict(shape=shape)
    sa.update(CRYSTAL)
    sb.update(GOLD)
    sets = acting.perform(m["expr"], t0, t1, at=(o[0], o[2]), view=view, variant=variant,
                          style=dict(points=70000, fade=0.8), style_a=sa, style_b=sb, pre=2.0, post=1.6,
                          seed=float(m["k"]) + 1.0)
    return list(sets)


def _shore_line():
    """The people of light on the water road, seen from behind, facing the lamp; quiet, alive."""
    from nine_reference_p3d.body import Body
    out = []
    shapes = ["woman", "man", "woman", "man", "woman", "man"]
    hair = ["bun", "short", "bob", "cap", "covered", "short"]
    for i, x in enumerate(LINE_X):
        st = GOLD if i % 2 else CRYSTAL
        out.append(Body(shapes[i], at=(x, LINE_Z + 0.3 * np.sin(1.7 * i)), facing=180.0 + 4.0 * np.sin(2.3 * i),
                        motion="stand", hair=hair[i], points=36000, show=(SHORE_LINE["t_in"], SHORE_LINE["t_out"]),
                        fade=2.5, seed=40.0 + i,
                        gesture=[(SHORE_LINE["t_in"], 300.0, "sway", dict(period=4.0 + 0.4 * i, amount=0.8,
                                                                         ease_in=2.0))],
                        effects=[dict(kind="form", t=SHORE_LINE["t_in"] + 0.5 * i, dur=2.4)], **st))
    return out


_CAST = {}


def cast():
    if _CAST:
        return _CAST
    from nine_reference_p3d import master_acting  # noqa: F401  (greet_bow, sway, comfort...)
    _CAST["mother"] = [_mother()]
    _CAST["greeting"] = _greeting(BY["Greeting"])
    _CAST["consideration"] = _acted(BY["Consideration"], "help_up", "man")
    _CAST["inclusiveness"] = _acted(BY["Inclusiveness"], "embrace", "woman")
    _CAST["encouragement"] = _acted(BY["Encouragement"], "shoulder", "woman")
    _CAST["gratitude"] = _acted(BY["Gratitude"], "gift", "woman")
    _CAST["line"] = _shore_line()
    return _CAST


def _setup(scene):
    for name in ("_arch", "_floats", "_lanterns"):
        for e in scene.entries():
            if e.name == name:
                e.pointset = Clear(e.pointset)
    scene.add("lake lights", Clear(LakeLights()))
    scene.add("lamp", LAMP)
    scene.add("comets", Clear(Comets()), reflect=True)
    for group, bodies in cast().items():
        for i, b in enumerate(bodies):
            if hasattr(b, "add"):
                b.add(scene, f"{group} {i}")
            else:
                scene.add(f"{group} {i}", Clear(b))
    WORDS.add_to(scene, reflect=False)


# ---------------------------------------------------------------------------------------------------------
# The world: pre-dawn under a great lamp (midnight blue and deep gold only), then a night of peace
# ---------------------------------------------------------------------------------------------------------
LOOKS = dict(
    restless=dict(base="night", sky_top="#02040f", sky_mid="#081436", sky_hor="#1d2452", sun_az=180.0,
                  sun_el=LAMP_EL, sun_color="#ffb347", sun_int=0.30, sun_size=0.8, sun_disc=7.0, sun_glow=0.45,
                  stars=0.85, milky=0.0, clouds=0.0, hills=0.9, hill_color="#03050f", haze=0.45,
                  haze_color="#1c2350", mist=0.18, mist_color="#1c2552", water="#01030a", ripple=0.85,
                  dust=0.35, dust_color="#ffd9a0", dust_color2="#ffcf8a", bokeh=0.4, rays=0.0),
    lamp=dict(base="night", sky_top="#03050f", sky_mid="#0b1638", sky_hor="#3a2a40", sun_az=180.0,
              sun_el=LAMP_EL, sun_color="#ffbf4f", sun_int=0.38, sun_size=0.7, sun_disc=7.0, sun_glow=0.4,
              stars=0.75, milky=0.0, clouds=0.0, hills=0.9, hill_color="#05050f", haze=0.32, haze_color="#2a2240",
              mist=0.18, mist_color="#262848", water="#02030a", ripple=0.68, rays=0.06, dust=0.4,
              dust_color="#ffd9a0", dust_color2="#ffc070", bokeh=0.45),
    peace=dict(base="night", sky_top="#050818", sky_mid="#1a1c48", sky_hor="#6a4630", sun_az=180.0,
               sun_el=LAMP_EL, sun_color="#ffcd63", sun_int=0.55, sun_size=0.8, sun_disc=7.0, sun_glow=0.65,
               stars=0.6, milky=0.0, clouds=0.0, hills=0.85, hill_color="#0a0812", haze=0.42, haze_color="#46323a",
               mist=0.16, mist_color="#3a3048", water="#03030a", ripple=0.25, rays=0.1, dust=0.8,
               dust_color="#ffe0a0", dust_color2="#ffc46a", bokeh=0.6),
    gather=dict(base="night", sky_top="#03050f", sky_mid="#0d1640", sky_hor="#3e2c44", sun_az=180.0,
                sun_el=LAMP_EL, sun_color="#ffc35a", sun_int=0.45, sun_size=0.7, sun_disc=7.0, sun_glow=0.5,
                stars=0.85, milky=0.0, clouds=0.0, hills=0.9, hill_color="#05050f", haze=0.4, haze_color="#2e2644",
                mist=0.16, mist_color="#262a4a", water="#02030a", ripple=0.15, rays=0.05, dust=0.45,
                dust_color="#ffd9a0", dust_color2="#ffc070", bokeh=0.45),
    night_peace=dict(base="night", sky_top="#03051a", sky_mid="#0d1442", sky_hor="#2a2c5e", sun_az=180.0,
                     sun_el=LAMP_EL, sun_color="#ffe3a3", sun_int=0.38, sun_size=0.8, sun_disc=7.0, sun_glow=0.5,
                     stars=1.0, milky=0.0, clouds=0.0, hills=0.9, hill_color="#04050f", haze=0.45,
                     haze_color="#24285a", mist=0.15, mist_color="#22285a", water="#01030a", ripple=0.0,
                     dust=0.4, dust_color="#ffd9a0", dust_color2="#ffcf8a", bokeh=0.4, rays=0.0),
)

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "restless"), (HITS["lamp"] - 0.3, "lamp", 4.5), (WEB_T0 - 2.0, "peace", 6.0),
          (152.0, "gather", 8.0), (209.0, "night_peace", 9.0)],
    ripple=Track([(0.0, 0.85), (25.0, 0.85), (50.0, 0.68), (105.0, 0.5), (128.0, 0.4), (150.0, 0.18),
                  (190.0, 0.1), (212.0, 0.0), (TOTAL, 0.0)]),
    lights=[dict(pos=lambda t: LAMP.where(t), color="#ffbf4f",
                 strength=lambda t: 0.9 * _sc(28.0, 34.0, t) * (1.0 - _sc(50.0, 54.0, t)), radius=6.0)],
    arch=ARCH_CFG,
    react=dict(beat=0.12, level=0.12),
)

P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=[dict(t=HITS["lamp"], strength=0.28, rise=0.4, fall=1.2, color="#ffbf4f", at=tuple(LAMP_PT)),
            dict(t=BIRTH, strength=0.22, rise=0.5, fall=1.2, color="#ffd08a", at=tuple(LAMP_PT))],
    motion_blur=0.0,
)

# no closing card in the live version (the agreed hand-off frame to song 11)
TITLE = dict(_base.TITLE, form=1e9, hold=1e9, star=1e9)
TAGLINE = dict(_base.TAGLINE, t0=1e9, t1=1e9 + 1)
TITLES = dict(
    opening=dict(t_end=9.6, dissolve=1.6, build=1.2, y=.30),
    signature=dict(windows=[(9.2, TOTAL + 10.0, "bl", "night")], fade=.9),
)
