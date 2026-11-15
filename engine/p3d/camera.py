"""The camera of the 3D layer: moves through space as pure functions of time.

A Rig is a list of moves, each owning a stretch of time. Between two moves the rig blends from one into the
next over `blend` seconds (both keep moving while it blends, so the speed carries through and nothing jerks).

    from p3d.camera import Rig, orbit, dolly, crane, fly, hold

    CAM = Rig([
        dolly((0, 0.8, 150), (0, 1.4, 42), 0.0, 5.0, look=(0, 7, 0)),            # skim over the lake
        orbit((0, 6.5, 0), radius=30, height=(3, 11), a0=0, a1=360, t0=5.0, t1=13.0),   # rise and revolve
        dolly((0, 9, 26), (0, 4, -32), 13.0, 16.5, look="ahead"),               # fly through the arch
        crane((0, 4, -32), 46, 16.5, 21.0, look=(0, 60, -160)),                 # up into the stars
        hold((0, 9, 95), (0, 8, 0), 21.0, 25.0, blend=0.4),                     # a whip to the wide shot
    ], blend=1.6, fov=42, aperture=0.06, handheld=0.3)

EVERY MOVE takes
  fov, roll, focus, aperture, near    a number, a pair (start, end), a Track or a function of time; the rig's
                    own values are the defaults. roll is in degrees and may run past 360 (a barrel roll).
                    focus: metres, "target" (the distance to what the camera looks at, the default), or a
                    world point. aperture: the lens opening in metres, 0 = everything sharp, 0.05 a clear
                    blur, 0.15 big dreamy bokeh (a Track of both is a rack focus). near: the nearest distance
                    drawn (default 0.05 m; 0.02 for macro shots of hands).
  blend             the length of the blend INTO this move: 0 is a hard cut (hide it in a burst of light),
                    0.3 to 0.5 a whip (the motion blur streaks the picture), 2 a soft handover.
  ease              how the move runs inside its own time: "linear" (default, keeps its speed into the blends),
                    "smooth", "in" (from rest), "out" (to rest: ease into a still reading set-up).
  pace              the speed of the move, driven by the music: a list of (time, progress) keys or a function
                    of time giving progress 0..1 along the move. Fast where the keys are steep, slow where
                    they are flat: [(7.5, 0.0), (8.0, 0.45), (12.0, 0.6), (15.0, 1.0)] dives on the cut at
                    7.5 s, drifts through the breath, and finishes by 15 s. It replaces `ease`.
  up                which way is up for the camera in this move: a vector or a function of time (a loop, a
                    look straight down). Without it the rig's `up`, else the world's up.

THE RIG takes the defaults above and
  handheld          0..1, a subtle slow drift
  shake             0..1 or more, a Track or a function of time: a hard fast shake (thunder, a landing)
  free=True         the camera carries its own up along its path, so it can loop and look straight up or
                    down without ever flipping (roll then turns it about its own axis). While the view is
                    near level it rights itself toward the world's up at `right` per second (default 3;
                    0 never rights itself); a hard cut starts level. For a long upside down ride give
                    that move its own `up`
  parent            a p3d.Frame the whole rig rides (a camera carried on a wave, a runner, a ribbon)
  shutter           motion blur: the share of the frame time the shutter is open (default 0.4)
  min_height        the camera never goes lower than this over the lake (None lets it go anywhere)
Azimuth angles: degrees from +z toward +x (the arch's front faces +z).
"""
import numpy as np

from .api import CameraState, at


def _v(x):
    return np.asarray(x, dtype=np.float64)


def _smoother(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


def _ease(u, kind):
    """Progress 0..1 with easing inside the move; outside it runs on in a straight line at the end speed
    (zero for the eased ends), so a blend into the next move stays smooth."""
    if kind == "linear":
        return u
    c = min(max(u, 0.0), 1.0)
    if kind == "smooth":
        return c * c * (3.0 - 2.0 * c)
    if kind == "in":        # starts from rest, leaves at speed
        return c * c if u <= 1.0 else 1.0 + 2.0 * (u - 1.0)
    if kind == "out":       # arrives to rest
        return 1.0 - (1.0 - c) ** 2 if u >= 0.0 else 2.0 * u
    raise ValueError(f"unknown ease {kind!r} (linear, smooth, in, out)")


def _param(v, t, t0, t1):
    """A move's fov, roll, focus, aperture or near at t: a number, a (start, end) pair or a function of time."""
    if v is None:
        return None
    if callable(v):
        return v(t)
    if isinstance(v, (tuple, list)) and len(v) == 2 and not isinstance(v[0], (tuple, list)):
        u = min(max((t - t0) / max(t1 - t0, 1e-9), 0.0), 1.0)
        u = u * u * (3.0 - 2.0 * u)
        return float(v[0]) * (1 - u) + float(v[1]) * u
    return v


class _Pace:
    """Progress along a move from (time, progress) keys: smooth between the keys (no overshoot), and running
    on at the end speeds outside them."""

    def __init__(self, keys):
        k = sorted((float(a), float(b)) for a, b in keys)
        self.t, self.u = np.array([a for a, _ in k]), np.array([b for _, b in k])
        if len(k) < 2 or np.any(np.diff(self.t) <= 0):
            raise ValueError("pace needs two or more (time, progress) keys with increasing times")
        d = np.diff(self.u) / np.diff(self.t)
        m = np.concatenate([[d[0]], 0.5 * (d[:-1] + d[1:]), [d[-1]]])
        for i in range(len(d)):                      # keep it monotone where the keys are (Fritsch and Carlson)
            if d[i] == 0.0:
                m[i] = m[i + 1] = 0.0
            else:
                a, b = m[i] / d[i], m[i + 1] / d[i]
                if a < 0.0:
                    m[i] = 0.0
                if b < 0.0:
                    m[i + 1] = 0.0
                s = a * a + b * b
                if s > 9.0:
                    m[i], m[i + 1] = 3.0 * a / np.sqrt(s) * d[i], 3.0 * b / np.sqrt(s) * d[i]
        self.m = m

    def __call__(self, t):
        ts, us, m = self.t, self.u, self.m
        if t <= ts[0]:
            return us[0] + m[0] * (t - ts[0])
        if t >= ts[-1]:
            return us[-1] + m[-1] * (t - ts[-1])
        i = int(np.searchsorted(ts, t, side="right")) - 1
        h = ts[i + 1] - ts[i]
        x = (t - ts[i]) / h
        x2, x3 = x * x, x * x * x
        return ((2 * x3 - 3 * x2 + 1) * us[i] + (x3 - 2 * x2 + x) * h * m[i] + (-2 * x3 + 3 * x2) * us[i + 1]
                + (x3 - x2) * h * m[i + 1])


class Move:
    """One camera move. pose(t) gives (pos, target); it is defined for every t (it runs on past its ends)."""

    def __init__(self, t0, t1, fov=None, roll=None, focus=None, aperture=None, blend=None, ease="linear", pace=None,
                 up=None, near=None):
        if not t1 > t0:
            raise ValueError(f"a camera move needs t1 > t0, got {t0} and {t1}")
        self.t0, self.t1 = float(t0), float(t1)
        self.fov, self.roll, self.focus, self.aperture, self.blend, self.ease = fov, roll, focus, aperture, blend, ease
        self.up, self.near = up, near
        self.pace = None if pace is None else (pace if callable(pace) else _Pace(pace))

    def u(self, t):
        if self.pace is not None:
            return float(self.pace(t))
        return _ease((t - self.t0) / (self.t1 - self.t0), self.ease)

    def pose(self, t):
        raise NotImplementedError

    def fov_at(self, t):
        return None


def _pair(v):
    if isinstance(v, (tuple, list)):
        return float(v[0]), float(v[1])
    return float(v), float(v)


class orbit(Move):
    """Revolve around `center`: radius and height (above the lake) are numbers or (start, end) pairs, the
    angle runs from a0 to a1 degrees. look: what the camera looks at (default: the centre). center and look
    may be functions of time (revolving round someone who walks)."""

    def __init__(self, center, radius, height, a0, a1, t0, t1, look=None, **kw):
        super().__init__(t0, t1, **kw)
        self.c = center
        self.r, self.h, self.a = _pair(radius), _pair(height), (float(a0), float(a1))
        self.look = look

    def pose(self, t):
        u = self.u(t)
        uc = min(max(u, 0.0), 1.0)
        us = uc * uc * (3.0 - 2.0 * uc)
        a = self.a[0] + (self.a[1] - self.a[0]) * u
        r = self.r[0] + (self.r[1] - self.r[0]) * us
        h = self.h[0] + (self.h[1] - self.h[0]) * us
        c = _v(self.c(t) if callable(self.c) else self.c)
        p = at(a, r, h)
        p[0] += c[0]
        p[2] += c[2]
        if self.look is None:
            return p, c
        return p, _v(self.look(t) if callable(self.look) else self.look)


class dolly(Move):
    """Travel in a straight line from p0 to p1. look: a point, a pair of points (the gaze travels from one
    to the other), a function of time, or "ahead" (the camera looks where it flies).
    keep_width: a dolly zoom: the field of view follows the distance so that a subject this many metres
    wide at the look point keeps its size in the picture while the world behind it swells or shrinks."""

    def __init__(self, p0, p1, t0, t1, look="ahead", keep_width=None, **kw):
        super().__init__(t0, t1, **kw)
        self.p0, self.p1 = _v(p0), _v(p1)
        self.keep_width = keep_width
        self.ahead = isinstance(look, str)
        self.look_fn = look if callable(look) else None
        if self.ahead:
            if look != "ahead":
                raise ValueError('dolly look is a point, a pair of points, a function of time, or "ahead"')
            d = self.p1 - self.p0
            self.l0 = self.l1 = d / max(np.linalg.norm(d), 1e-9)
        elif self.look_fn is None:
            lk = np.asarray(look, dtype=np.float64)
            self.l0, self.l1 = (lk[0], lk[1]) if lk.ndim == 2 else (lk, lk)

    def pose(self, t):
        u = self.u(t)
        p = self.p0 + (self.p1 - self.p0) * u
        if self.ahead:
            return p, p + self.l0 * 20.0
        if self.look_fn is not None:
            return p, _v(self.look_fn(t))
        uc = min(max(u, 0.0), 1.0)
        us = uc * uc * (3.0 - 2.0 * uc)
        return p, self.l0 + (self.l1 - self.l0) * us

    def fov_at(self, t):
        if self.keep_width is None:
            return None
        p, tg = self.pose(t)
        return float(np.degrees(2.0 * np.arctan(0.5 * float(self.keep_width) / max(np.linalg.norm(tg - p), 1e-3))))


def crane(pos, height, t0, t1, look, **kw):
    """Rise (or sink) from pos to the given height above the lake, looking at `look` (a point or a pair)."""
    p0 = _v(pos)
    p1 = p0.copy()
    p1[1] = float(height)
    return dolly(p0, p1, t0, t1, look=look, **kw)


def hold(pos, target, t0, t1, drift=(0.0, 0.0, 0.0), **kw):
    """Stand at pos looking at target; drift (metres per second) lets the camera float a little."""
    p0 = _v(pos)
    d = _v(drift)
    return dolly(p0 - d * (t1 - t0) * 0.5, p0 + d * (t1 - t0) * 0.5, t0, t1, look=target, **kw)


class fly(Move):
    """Fly along a smooth curve through keys [(t, pos, target), ...] (at least two, times increasing). With
    `pace` the key times only shape the curve; the pace says when the camera is where along it."""

    def __init__(self, path, **kw):
        keys = sorted(path, key=lambda k: k[0])
        ts = np.array([k[0] for k in keys], dtype=np.float64)
        if len(keys) < 2 or np.any(np.diff(ts) <= 0):
            raise ValueError("fly needs two or more keys with increasing times")
        super().__init__(ts[0], ts[-1], **kw)
        self.ts = ts
        self.P = np.array([_v(k[1]) for k in keys])
        self.T = np.array([_v(k[2]) for k in keys])

    @staticmethod
    def _spline(ts, V, t):
        n = len(ts)
        if t <= ts[0]:      # run on in a straight line before the first key and after the last
            m = (V[1] - V[0]) / (ts[1] - ts[0])
            return V[0] + m * (t - ts[0])
        if t >= ts[-1]:
            m = (V[-1] - V[-2]) / (ts[-1] - ts[-2])
            return V[-1] + m * (t - ts[-1])
        i = int(np.searchsorted(ts, t, side="right")) - 1
        h = ts[i + 1] - ts[i]

        def tangent(k):
            if k == 0:
                return (V[1] - V[0]) / (ts[1] - ts[0])
            if k == n - 1:
                return (V[-1] - V[-2]) / (ts[-1] - ts[-2])
            return (V[k + 1] - V[k - 1]) / (ts[k + 1] - ts[k - 1])

        u = (t - ts[i]) / h
        m0, m1 = tangent(i) * h, tangent(i + 1) * h
        u2, u3 = u * u, u * u * u
        return ((2 * u3 - 3 * u2 + 1) * V[i] + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * V[i + 1]
                + (u3 - u2) * m1)

    def pose(self, t):
        if self.pace is not None or self.ease != "linear":
            t = self.t0 + (self.t1 - self.t0) * self.u(t)
        return self._spline(self.ts, self.P, t), self._spline(self.ts, self.T, t)


def _wobble(t, seed, rate=1.0):
    """Three smooth numbers around zero: sums of sines, the same on every machine (rate 1: a handheld drift)."""
    out = []
    for k in range(3):
        s = seed * 7.13 + k * 3.71
        out.append(0.55 * np.sin(t * 0.61 * rate + s) + 0.30 * np.sin(t * 1.37 * rate + s * 2.3)
                   + 0.15 * np.sin(t * 2.93 * rate + s * 4.1))
    return np.array(out)


WORLD_UP = np.array([0.0, 1.0, 0.0])


class Rig:
    def __init__(self, moves, blend=1.5, fov=45.0, roll=0.0, focus="target", aperture=0.0, handheld=0.0,
                 shutter=0.4, min_height=0.25, shake=0.0, parent=None, free=False, up=None, near=0.05, right=3.0):
        self.moves = sorted(moves, key=lambda m: m.t0)
        if not self.moves:
            raise ValueError("a camera rig needs at least one move")
        self.blend, self.fov, self.roll, self.focus, self.aperture = float(blend), fov, roll, focus, aperture
        self.handheld, self.shutter, self.min_height = float(handheld), float(shutter), min_height
        self.shake, self.parent, self.free, self.up, self.near = shake, parent, bool(free), up, near
        self.right = float(right)
        self._table = None

    def _one(self, m, t):
        pos, tgt = m.pose(t)
        t0, t1 = self.moves[0].t0, self.moves[-1].t1

        def par(name):
            v = _param(getattr(m, name), t, m.t0, m.t1)
            if v is None:
                v = _param(getattr(self, name), t, t0, t1)
            return v

        fov = m.fov_at(t)
        fov = float(par("fov")) if fov is None else fov
        roll, ap, foc, near = float(par("roll")), float(par("aperture")), par("focus"), float(par("near"))
        fwd = tgt - pos
        dist = max(float(np.linalg.norm(fwd)), 1e-6)
        if isinstance(foc, str):
            if foc != "target":
                raise ValueError('camera focus is metres, "target" or a world point')
            fd = dist
        elif isinstance(foc, (tuple, list, np.ndarray)):
            fd = max(float(np.dot(_v(foc) - pos, fwd / dist)), 0.02)     # depth of the point along the view
        else:
            fd = float(foc)
        up = m.up if m.up is not None else self.up
        up = WORLD_UP if up is None else _v(up(t) if callable(up) else up)
        return np.concatenate([pos, tgt, [fov, roll, max(fd, 0.02), max(ap, 0.0), near], up])

    def raw(self, t):
        """pos, target, fov, roll, focus, aperture, near, up at t as one array (moves blended; no drift)."""
        ms = self.moves
        # the last move whose blend-in has finished: everything before it no longer counts
        start = 0
        steps = [1.0]
        for j in range(1, len(ms)):
            w = self.blend if ms[j].blend is None else float(ms[j].blend)
            b = ms[j].t0
            s = (1.0 if t >= b else 0.0) if w <= 0.0 else _smoother((t - (b - 0.5 * w)) / w)
            steps.append(s)
            if s >= 1.0:
                start = j
        x = self._one(ms[start], t)
        for j in range(start + 1, len(ms)):
            if steps[j] <= 0.0:
                break
            x = x * (1.0 - steps[j]) + self._one(ms[j], t) * steps[j]
        return x

    def _carried_up(self, t):
        """free=True: the up vector carried along the path from the start (a table made once, the same in
        every part of a render), so the picture never flips when the camera loops or looks straight down."""
        if self._table is None:
            t0, t1 = self.moves[0].t0 - 1.0, self.moves[-1].t1 + 1.0
            ts = np.arange(t0, t1 + 1e-9, 1.0 / 120.0)
            ups = np.zeros((len(ts), 3))
            u = WORLD_UP.copy()
            cuts = [m.t0 for m in self.moves[1:] if m.blend is not None and float(m.blend) <= 0.0]
            for i, tt in enumerate(ts):
                x = self.raw(float(tt))
                f = x[3:6] - x[0:3]
                f /= max(np.linalg.norm(f), 1e-9)
                if any(tt - 1.0 / 120.0 < c <= tt for c in cuts):
                    u = WORLD_UP.copy()                 # a hard cut starts level again
                # carried along the path, and gently righted toward the world's up while the view is near
                # level (so after a loop or a dive the horizon comes back by itself within about a second)
                u = u + self.right * (1.0 - f[1] * f[1]) ** 2 / 120.0 * WORLD_UP
                u = u - np.dot(u, f) * f
                n = np.linalg.norm(u)
                u = u / n if n > 1e-6 else ups[i - 1] if i else np.array([0.0, 0.0, -1.0])
                ups[i] = u
            self._table = (ts, ups)
        ts, ups = self._table
        k = min(max((t - ts[0]) * 120.0, 0.0), len(ts) - 1.001)
        i = int(k)
        u = ups[i] * (1.0 - (k - i)) + ups[i + 1] * (k - i)
        return u / max(np.linalg.norm(u), 1e-9)

    def state(self, t, aspect=16.0 / 9.0):
        x = self.raw(t)
        pos, tgt = x[0:3].copy(), x[3:6].copy()
        up = self._carried_up(t) if self.free else x[11:14]
        roll = float(x[7])
        dist = float(np.linalg.norm(tgt - pos))
        if self.handheld > 0.0:
            pos += self.handheld * 0.035 * _wobble(t, 1.0)
            tgt += self.handheld * 0.006 * dist * _wobble(t, 2.0)
        sh = self.shake(t) if callable(self.shake) else self.shake
        if sh:
            pos += float(sh) * 0.04 * _wobble(t, 5.0, 31.0)
            tgt += float(sh) * 0.010 * dist * _wobble(t, 6.0, 37.0)
            roll += float(sh) * 0.7 * _wobble(t, 7.0, 29.0)[0]
        focus = float(x[8])
        if self.parent is not None:
            o, Rm, s = self.parent.at(t)
            pos, tgt, up, focus = o + (Rm @ pos) * s, o + (Rm @ tgt) * s, Rm @ up, focus * s
        if self.min_height is not None:
            pos[1] = max(pos[1], float(self.min_height))
        if np.linalg.norm(tgt - pos) < 1e-4:
            tgt = pos + np.array([0.0, 0.0, -1.0])
        return CameraState(pos=pos, target=tgt, fov=float(min(max(x[6], 3.0), 150.0)), roll=roll, focus=focus,
                           aperture=float(x[9]), aspect=float(aspect), near=float(min(max(x[10], 0.02), 1.0)), up=up)

    def speed(self, t, dt=1.0 / 30.0):
        """How fast the picture moves at t: (metres per second, degrees per second the view turns)."""
        a, b = self.state(t - dt * 0.5), self.state(t + dt * 0.5)
        fa, fb = a.basis()[2], b.basis()[2]
        ang = np.degrees(np.arccos(min(max(float(np.dot(fa, fb)), -1.0), 1.0)))
        return float(np.linalg.norm(b.pos - a.pos) / dt), float(ang / dt)


def make(spec):
    """A rig from what a song file gives as P3D["camera"]: a Rig, a list of moves, a single move, a dict
    of Rig settings with "moves", or nothing (a still wide view)."""
    if isinstance(spec, Rig):
        return spec
    if spec is None:
        return Rig([hold((0.0, 3.0, 60.0), (0.0, 6.0, 0.0), 0.0, 1.0)])
    if isinstance(spec, Move):
        return Rig([spec])
    if isinstance(spec, dict):
        kw = dict(spec)
        return Rig(kw.pop("moves"), **kw)
    return Rig(list(spec))
