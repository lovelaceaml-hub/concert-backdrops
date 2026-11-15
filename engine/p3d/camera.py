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

Every move takes fov, roll, focus and aperture (a number, a pair (start, end), or a function of time); the
rig's own values are the defaults. focus: metres, "target" (the distance to what the camera looks at, the
default), or a world point (x, y, z). aperture: the lens opening in metres, 0 = everything sharp, 0.05 a
clear blur, 0.15 big dreamy bokeh. A move's `blend` sets the length of the blend INTO it: 0 is a hard cut
(hide it in a burst of light), 0.3 to 0.5 a whip (the engine's motion blur streaks the picture).
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
    """A move's fov, roll, focus or aperture at t: a number, a (start, end) pair or a function of time."""
    if v is None:
        return None
    if callable(v):
        return v(t)
    if isinstance(v, (tuple, list)) and len(v) == 2 and not isinstance(v[0], (tuple, list)):
        u = min(max((t - t0) / max(t1 - t0, 1e-9), 0.0), 1.0)
        u = u * u * (3.0 - 2.0 * u)
        return float(v[0]) * (1 - u) + float(v[1]) * u
    return v


class Move:
    """One camera move. pose(t) gives (pos, target); it is defined for every t (it runs on past its ends)."""

    def __init__(self, t0, t1, fov=None, roll=None, focus=None, aperture=None, blend=None, ease="linear"):
        if not t1 > t0:
            raise ValueError(f"a camera move needs t1 > t0, got {t0} and {t1}")
        self.t0, self.t1 = float(t0), float(t1)
        self.fov, self.roll, self.focus, self.aperture, self.blend, self.ease = fov, roll, focus, aperture, blend, ease

    def u(self, t):
        return _ease((t - self.t0) / (self.t1 - self.t0), self.ease)

    def pose(self, t):
        raise NotImplementedError


def _pair(v):
    if isinstance(v, (tuple, list)):
        return float(v[0]), float(v[1])
    return float(v), float(v)


class orbit(Move):
    """Revolve around `center`: radius and height (above the lake) are numbers or (start, end) pairs, the
    angle runs from a0 to a1 degrees. look: what the camera looks at (default: the centre)."""

    def __init__(self, center, radius, height, a0, a1, t0, t1, look=None, **kw):
        super().__init__(t0, t1, **kw)
        self.c = _v(center)
        self.r, self.h, self.a = _pair(radius), _pair(height), (float(a0), float(a1))
        self.look = None if look is None else _v(look)

    def pose(self, t):
        u = self.u(t)
        uc = min(max(u, 0.0), 1.0)
        us = uc * uc * (3.0 - 2.0 * uc)
        a = self.a[0] + (self.a[1] - self.a[0]) * u
        r = self.r[0] + (self.r[1] - self.r[0]) * us
        h = self.h[0] + (self.h[1] - self.h[0]) * us
        p = at(a, r, h)
        p[0] += self.c[0]
        p[2] += self.c[2]
        return p, (self.c if self.look is None else self.look)


class dolly(Move):
    """Travel in a straight line from p0 to p1. look: a point, a pair of points (the gaze travels from one
    to the other), or "ahead" (the camera looks where it flies)."""

    def __init__(self, p0, p1, t0, t1, look="ahead", **kw):
        super().__init__(t0, t1, **kw)
        self.p0, self.p1 = _v(p0), _v(p1)
        self.ahead = isinstance(look, str)
        if self.ahead:
            if look != "ahead":
                raise ValueError('dolly look is a point, a pair of points, or "ahead"')
            d = self.p1 - self.p0
            self.l0 = self.l1 = d / max(np.linalg.norm(d), 1e-9)
        else:
            lk = np.asarray(look, dtype=np.float64)
            self.l0, self.l1 = (lk[0], lk[1]) if lk.ndim == 2 else (lk, lk)

    def pose(self, t):
        u = self.u(t)
        p = self.p0 + (self.p1 - self.p0) * u
        if self.ahead:
            return p, p + self.l0 * 20.0
        uc = min(max(u, 0.0), 1.0)
        us = uc * uc * (3.0 - 2.0 * uc)
        return p, self.l0 + (self.l1 - self.l0) * us


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
    """Fly along a smooth curve through keys [(t, pos, target), ...] (at least two, times increasing)."""

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
        return self._spline(self.ts, self.P, t), self._spline(self.ts, self.T, t)


def _wobble(t, seed):
    """Three smooth numbers around zero (a handheld drift): sums of slow sines, the same on every machine."""
    out = []
    for k in range(3):
        s = seed * 7.13 + k * 3.71
        out.append(0.55 * np.sin(t * 0.61 + s) + 0.30 * np.sin(t * 1.37 + s * 2.3) + 0.15 * np.sin(t * 2.93 + s * 4.1))
    return np.array(out)


class Rig:
    def __init__(self, moves, blend=1.5, fov=45.0, roll=0.0, focus="target", aperture=0.0, handheld=0.0,
                 shutter=0.4, min_height=0.25):
        self.moves = sorted(moves, key=lambda m: m.t0)
        if not self.moves:
            raise ValueError("a camera rig needs at least one move")
        self.blend, self.fov, self.roll, self.focus, self.aperture = float(blend), fov, roll, focus, aperture
        self.handheld, self.shutter, self.min_height = float(handheld), float(shutter), float(min_height)

    def _one(self, m, t):
        pos, tgt = m.pose(t)

        def par(name):
            v = _param(getattr(m, name), t, m.t0, m.t1)
            if v is None:
                v = _param(getattr(self, name), t, self.moves[0].t0, self.moves[-1].t1)
            return v

        fov, roll, ap, foc = float(par("fov")), float(par("roll")), float(par("aperture")), par("focus")
        fwd = tgt - pos
        dist = max(float(np.linalg.norm(fwd)), 1e-6)
        if isinstance(foc, str):
            if foc != "target":
                raise ValueError('camera focus is metres, "target" or a world point')
            fd = dist
        elif isinstance(foc, (tuple, list, np.ndarray)):
            fd = max(float(np.dot(_v(foc) - pos, fwd / dist)), 0.1)     # depth of the point along the view
        else:
            fd = float(foc)
        return np.concatenate([pos, tgt, [fov, roll, max(fd, 0.05), max(ap, 0.0)]])

    def raw(self, t):
        """pos, target, fov, roll, focus, aperture at t as one array (moves blended, no handheld)."""
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

    def state(self, t, aspect=16.0 / 9.0):
        x = self.raw(t)
        pos, tgt = x[0:3].copy(), x[3:6].copy()
        if self.handheld > 0.0:
            dist = float(np.linalg.norm(tgt - pos))
            pos += self.handheld * 0.035 * _wobble(t, 1.0)
            tgt += self.handheld * 0.006 * dist * _wobble(t, 2.0)
        pos[1] = max(pos[1], self.min_height)
        if np.linalg.norm(tgt - pos) < 1e-4:
            tgt = pos + np.array([0.0, 0.0, -1.0])
        return CameraState(pos=pos, target=tgt, fov=float(min(max(x[6], 5.0), 140.0)), roll=float(x[7]),
                           focus=float(x[8]), aperture=float(x[9]), aspect=float(aspect))

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
