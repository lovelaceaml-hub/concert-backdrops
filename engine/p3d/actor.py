"""An actor: one skeleton placed in the world and moved through time (no points yet; engine/p3d/body.py
dresses it in points and garments).

    Actor(shape="woman", at=(x, z), facing=0, motion=[(0, "walk"), (6, "stand")],
          gesture=[(7, 12, "reach", dict(side="R"))])

at        where the feet are at the start: (x, z) on the lake, or (x, y, z)
facing    degrees around the y axis, 0 faces +z, 90 faces +x (the API's azimuth). A number, or keys
          [(t, degrees), ...] eased between: the figure turns, and a walker follows the turn
motion    a name, or keys [(t, name), (t, name, dict(...)), ...]: from each t the figure eases into that
          motion over `blend` seconds (default 0.9). Names: engine/p3d/motion.py MOTIONS.
          Parameters: speed (metres per second, walk and run), phase (0..1, where in the stride it starts),
          blend, and the motion's own (kneel: sit, dur, hands, one).
gesture   keys [(t_on, t_off, name), (t_on, t_off, name, dict(...))]: the upper body eases into the gesture
          at t_on and out of it at t_off (ease: seconds each way, default 1.2). Names: motion.py GESTURES.
          A gesture's `to` is a point in the WORLD here (for "reach").

Everything is a pure function of t: `frame(t)` may be asked in any order.
"""
import numpy as np

from . import assets, bodymath as bm
from . import motion as mo

GRID = 1.0 / 60.0


def _keys(v, default_name=None):
    if isinstance(v, str):
        return [(-1e9, v, {})]
    out = []
    for k in v:
        k = tuple(k)
        out.append((float(k[0]), k[1], dict(k[2]) if len(k) > 2 else {}))
    out.sort(key=lambda k: k[0])
    return out


class Actor:
    def __init__(self, shape="woman", height=None, at=(0.0, 0.0), facing=0.0, motion="stand", gesture=(),
                 seed=1.0, rig=None):
        self.rig = rig or assets.Rig(shape, height)
        self.mo = mo.Motions(self.rig, assets.load())
        at = tuple(float(x) for x in at)
        self.origin = np.array([at[0], 0.0, at[1]]) if len(at) == 2 else np.array(at)
        self.seed = float(seed)
        self.keys = _keys(motion)
        for _, name, _p in self.keys:
            if name not in mo.MOTIONS:
                raise ValueError("motion must be one of %s, got %r" % (mo.MOTIONS, name))
        self.gest = []
        for g in gesture:
            g = tuple(g)
            if g[2] not in mo.GESTURES:
                raise ValueError("gesture must be one of %s, got %r" % (mo.GESTURES, g[2]))
            self.gest.append((float(g[0]), float(g[1]), g[2], dict(g[3]) if len(g) > 3 else {}))
        if isinstance(facing, (int, float)):
            self.face_keys = [(0.0, float(facing))]
        else:
            self.face_keys = sorted((float(a), float(b)) for a, b in facing)
        # the time the travel is counted from: the first key that has a real time, or 0
        times = [k[0] for k in self.keys if k[0] > -1e8]
        self.t_ref = min(times + [0.0])
        self._travel = None
        self._cache = {}

    # ------------------------------------------------------------------ timeline
    def heading(self, t):
        """Facing in degrees at t."""
        k = self.face_keys
        if t <= k[0][0]:
            return k[0][1]
        for (t0, a0), (t1, a1) in zip(k, k[1:]):
            if t < t1:
                return a0 + (a1 - a0) * float(bm.smoother((t - t0) / (t1 - t0)))
        return k[-1][1]

    def _weights(self, t):
        """Blend weights of the motion keys at t (they sum to 1)."""
        n = len(self.keys)
        u = np.zeros(n)
        u[0] = 1.0
        for i in range(1, n):
            ts, _, p = self.keys[i]
            u[i] = float(bm.smoother((t - ts) / max(p.get("blend", 0.9), 1e-3)))
        w = np.zeros(n)
        rest = 1.0
        for i in range(n - 1, -1, -1):
            w[i] = rest * u[i]
            rest *= 1.0 - u[i]
        return w

    def _speed(self, i):
        _, name, p = self.keys[i]
        if name in ("walk", "run"):
            c = self.mo.clips[name]
            return float(p.get("speed", c.speed))
        return 0.0

    def _grid(self, t):
        """Travelled distance and place on a fixed time grid from t_ref, long enough to cover t."""
        need = int(max(t - self.t_ref, 0.0) / GRID) + 3
        if self._travel is None or len(self._travel[0]) < need:
            n = max(need, 600)
            if self._travel is not None:
                n = max(n, len(self._travel[0]) * 2)
            tt = self.t_ref + np.arange(n) * GRID
            sp = np.zeros(n)
            hd = np.zeros(n)
            speeds = [self._speed(i) for i in range(len(self.keys))]
            for k in range(n):
                sp[k] = float(np.dot(self._weights(tt[k]), speeds))
                hd[k] = np.radians(self.heading(tt[k]))
            dist = np.concatenate([[0.0], np.cumsum(0.5 * (sp[1:] + sp[:-1]) * GRID)])
            vx = sp * np.sin(hd)
            vz = sp * np.cos(hd)
            px = np.concatenate([[0.0], np.cumsum(0.5 * (vx[1:] + vx[:-1]) * GRID)])
            pz = np.concatenate([[0.0], np.cumsum(0.5 * (vz[1:] + vz[:-1]) * GRID)])
            self._travel = (dist, px, pz, sp)
        return self._travel

    def travel(self, t):
        """(distance walked so far, the feet's place on the ground, speed) at t."""
        dist, px, pz, sp = self._grid(t)
        x = max(t - self.t_ref, 0.0) / GRID
        k = min(int(x), len(dist) - 2)
        f = x - k
        d = dist[k] * (1 - f) + dist[k + 1] * f
        p = self.origin + np.array([px[k] * (1 - f) + px[k + 1] * f, 0.0, pz[k] * (1 - f) + pz[k + 1] * f])
        return d, p, sp[k] * (1 - f) + sp[k + 1] * f

    def base_pose(self, t):
        w = self._weights(t)
        d_now = self.travel(t)[0]
        P = None
        for i, (ts, name, p) in enumerate(self.keys):
            if w[i] <= 1e-6:
                continue
            age = t - max(ts, self.t_ref)
            kw = {k: v for k, v in p.items() if k not in ("blend", "speed", "phase")}
            if name in ("walk", "run"):
                c = self.mo.clips[name]
                d0 = self.travel(max(ts, self.t_ref))[0]
                kw["clip_time"] = ((d_now - d0) / c.stride + p.get("phase", 0.0)) * c.T
            elif name in self.mo.clips:
                kw["clip_time"] = max(age, 0.0) * p.get("rate", 1.0) + p.get("phase", 0.0) * self.mo.clips[name].T
                kw.pop("rate", None)
            else:
                kw.setdefault("seed", self.seed)
            pose = self.mo.pose(name, t, age, **kw)
            P = pose if P is None else mo.blend(P, pose, w[i] / max(w[:i + 1].sum(), 1e-9))
        return P

    def frame(self, t):
        """The posed skeleton at t: dict(M bone matrices (world), P joint positions, D, A rotations, origin,
        heading (radians), speed)."""
        key = round(float(t), 6)
        if key in self._cache:
            return self._cache[key]
        rig = self.rig
        P = self.base_pose(t)
        self.mo.breathe(P, t, self.seed)
        _, origin, speed = self.travel(t)
        hd = np.radians(self.heading(t))
        qh = bm.qy(hd)
        active = []
        for (t0, t1, name, p) in self.gest:
            e = p.get("ease", 1.2)
            w = float(bm.ramp(t, t0, t0 + e) * (1.0 - bm.ramp(t, t1 - e, t1)))
            if w > 1e-5:
                active.append((w, t - t0, name, p))
        if active:
            D, Pj, _ = self.mo.local_fk(P)
            g0 = -rig.lowest(rig.matrices(D, Pj)) * P.ground
            for w, age, name, p in active:
                kw = {k: v for k, v in p.items() if k != "ease"}
                if kw.get("to") is not None:
                    to = np.asarray(kw["to"](t) if callable(kw["to"]) else kw["to"], np.float64)
                    kw["to"] = bm.qrot(bm.qconj(qh), to - origin) - np.array([0.0, g0, 0.0])
                self.mo.gesture(name, P, w, t, age, **kw)
        root = origin + bm.qrot(qh, rig.neutral_pos[0] + P.pos)
        D, Pj, A = rig.fk(P.q, root, bm.qmul(qh, P.rot))
        M = rig.matrices(D, Pj)
        if P.ground > 0.0:
            lift = (origin[1] - rig.lowest(M)) * P.ground
            Pj = Pj + np.array([0.0, lift, 0.0])
            M = M.copy()
            M[:, 1, 3] += lift
        out = dict(M=M, P=Pj, D=D, A=A, origin=origin, heading=hd, speed=speed)
        if len(self._cache) > 48:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = out
        return out

    def joint(self, t, bone):
        """World position of a joint (the head of a bone) at t."""
        return self.frame(t)["P"][self.rig.idx[bone]].copy()

    def palm(self, t, side="R"):
        """(centre of the palm, the direction it faces, the direction the fingers point) in the world at t."""
        rig = self.rig
        f = self.frame(t)
        w = rig.idx["wrist." + side]
        m3 = rig.idx["finger3-1." + side]
        c = 0.4 * f["P"][w] + 0.6 * f["P"][m3]
        n = bm.qrot(f["A"][w], rig.palm_n[side])
        d = f["P"][m3] - f["P"][w]
        d /= max(np.linalg.norm(d), 1e-9)
        return c + n * 0.012 * rig.height / 1.6, n, d

    def mouth(self, t):
        """(the place just before the lips, the direction the face looks) in the world at t."""
        rig = self.rig
        f = self.frame(t)
        h = rig.idx["head"]
        p = f["P"][h] + bm.qrot(f["A"][h], self.mo.mouth - rig.neutral_pos[h])
        return p, bm.qrot(f["A"][h], [0.0, 0.0, 1.0])
