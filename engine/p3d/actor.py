"""An actor: one skeleton placed in the world and moved through time (no points yet; engine/p3d/body.py
dresses it in points and garments).

    Actor(shape="woman", at=(x, z), facing=0, motion=[(0, "walk"), (6, "stand")],
          gesture=[(7, 12, "reach", dict(side="R"))])

at        where the feet are at the start: (x, z) on the lake, or (x, y, z). Also keys [(t, place), ...]
          (the figure is moved between them, eased: stepping aside, with motion "shuffle") or a function of
          time (the figure is carried: a child lifted, feet on moving ground). Walking adds to it.
facing    degrees around the y axis, 0 faces +z, 90 faces +x (the API's azimuth). A number, or keys
          [(t, degrees), ...] eased between: the figure turns, and a walker follows the turn
motion    a name, or keys [(t, name), (t, name, dict(...)), ...]: from each t the figure eases into that
          motion over `blend` seconds (default 0.9). Names: engine/p3d/motion.py MOTIONS.
          Parameters: speed (metres per second, walk and run), phase (0..1, where in the stride it starts),
          blend, and the motion's own (kneel: sit, dur, hands, one).
gesture   keys [(t_on, t_off, name), (t_on, t_off, name, dict(...))]: the upper body eases into the gesture
          at t_on and out of it at t_off (ease: seconds each way, default 1.2). Names: motion.py GESTURES.
          A gesture's `to` is a point in the WORLD here (for "reach").

stoop     0..1: an elder's posture (bent back, head forward, knees a little bent)
hand      dict(side="R", at=<point or function of time>, aim=<direction the fingers point>, palm=<direction the
          palm faces>, anchor="palm" | "fingertips" | "wrist"): the whole figure is moved so that this hand is
          exactly there (for close-ups of hands and for exact contact; the rest of the body follows the hand)

Everything is a pure function of t: `frame(t)` may be asked in any order. `where(t, name)` gives named places
on the body (palm, fingertips, heart, head, shoulder...), `joint(t, bone)` any joint.
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
                 seed=1.0, rig=None, start=None, stoop=0.0, hand=None):
        self.rig = rig or assets.Rig(shape, height)
        self.mo = mo.Motions(self.rig, assets.load())
        self._at = at
        self.origin = self._place(self._origin_raw(0.0) if not callable(at) else at(0.0))
        self.seed = float(seed)
        self.keys = []
        for ts, name, p in _keys(motion):
            if name in mo.ALIASES:
                name, ph = mo.ALIASES[name]
                p = dict(p)
                p.setdefault("phase", ph)
            self.keys.append((ts, name, p))
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
        self.t_ref = min(times + [0.0]) if start is None else float(start)
        self._travel = None
        self._cache = {}
        self._anc = None
        self.stoop = float(stoop)          # an elder's posture, 0..1
        self.hand = dict(hand) if hand else None      # one hand placed exactly (see _place_hand)
        self.to_internal = None            # set by Body: world points -> this actor's own space

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

    @staticmethod
    def _place(p):
        p = [float(x) for x in p]
        return np.array([p[0], 0.0, p[1]]) if len(p) == 2 else np.array(p[:3])

    def _origin_raw(self, t):
        at = self._at
        if isinstance(at, (list, tuple)) and len(at) and isinstance(at[0], (list, tuple)):
            keys = sorted(at, key=lambda k: k[0])
            if t <= keys[0][0]:
                return keys[0][1]
            for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
                if t < t1:
                    u = float(bm.smoother((t - t0) / (t1 - t0)))
                    return self._place(p0) * (1 - u) + self._place(p1) * u
            return keys[-1][1]
        return at

    def base(self, t):
        """Where the figure's place is at t, before any walking: `at` as a point, keys or a function."""
        if callable(self._at):
            return self._place(self._at(t))
        return self._place(self._origin_raw(t))

    def travel(self, t):
        """(distance walked so far, the feet's place on the ground, speed) at t."""
        dist, px, pz, sp = self._grid(t)
        x = max(t - self.t_ref, 0.0) / GRID
        k = min(int(x), len(dist) - 2)
        f = x - k
        d = dist[k] * (1 - f) + dist[k + 1] * f
        p = self.base(t) + np.array([px[k] * (1 - f) + px[k + 1] * f, 0.0, pz[k] * (1 - f) + pz[k + 1] * f])
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

    def _clip_times(self, t):
        """(weight, clip, clip time) of every motion capture key that takes part at t."""
        w = self._weights(t)
        out = []
        d_now = None
        for i, (ts, name, p) in enumerate(self.keys):
            if w[i] <= 1e-6 or name not in self.mo.clips:
                continue
            c = self.mo.clips[name]
            if c.loop:
                if d_now is None:
                    d_now = self.travel(t)[0]
                d0 = self.travel(max(ts, self.t_ref))[0]
                ct = ((d_now - d0) / max(c.stride, 1e-6) + p.get("phase", 0.0)) * c.T
            else:
                ct = max(t - max(ts, self.t_ref), 0.0) * p.get("rate", 1.0) + p.get("phase", 0.0) * c.T
            out.append((float(w[i]), c, ct))
        return out

    def contact(self, t):
        """(2,) how planted the left and the right foot are at t (from the motion capture; 0 for posed motions)."""
        c = np.zeros(2)
        for w, clip, ct in self._clip_times(t):
            c += w * clip.sample(ct)[3]
        return c

    def _stance_start(self, t, s):
        """When the stance of foot s (0 left, 1 right) that holds at t began (searching back at most 1.5 s)."""
        step = 1.0 / 60.0
        tt = t
        for _ in range(90):
            if self.contact(tt - step)[s] < 0.5:
                return tt
            tt -= step
        return tt

    def frame(self, t, lock=True, gest=True):
        """The posed skeleton at t: dict(M bone matrices (world), P joint positions, D, A rotations, origin,
        heading (radians), speed). Feet that the motion plants stay where they were set down (lock=False:
        the motion as captured, for the lock's own reference). gest=False leaves the gestures out: the
        "raw" body another body's gestures may aim at without the two waiting on each other."""
        key = (round(float(t), 6), bool(lock), bool(gest))
        if key in self._cache:
            return self._cache[key]
        rig = self.rig
        P = self.base_pose(t)
        self.mo.breathe(P, t, self.seed)
        if self.stoop:
            self.mo.stoop(P, self.stoop)
        if self.hand is not None:
            self._hand_pose(P, t)
        _, origin, speed = self.travel(t)
        hd = np.radians(self.heading(t))
        qh = bm.qy(hd)
        active = []
        for (t0, t1, name, p) in (self.gest if gest else ()):
            e = p.get("ease", 1.2)
            w = float(bm.ramp(t, t0, t0 + e) * (1.0 - bm.ramp(t, t1 - e, t1)))
            if w > 1e-5:
                active.append((w, t - t0, name, p))
        if active:
            D, Pj, _ = self.mo.local_fk(P)
            g0 = -rig.lowest(rig.matrices(D, Pj)) * P.ground
            for w, age, name, p in active:
                kw = {k: v for k, v in p.items() if k != "ease"}
                for key_to in ("to", "to2"):
                    if kw.get(key_to) is not None:
                        to = self._world(kw[key_to], t)
                        kw[key_to] = bm.qrot(bm.qconj(qh), to - origin) - np.array([0.0, g0, 0.0])
                self.mo.gesture(name, P, w, t, age, **kw)
        root = origin + bm.qrot(qh, rig.neutral_pos[0] + P.pos)
        D, Pj, A = rig.fk(P.q, root, bm.qmul(qh, P.rot))
        M = rig.matrices(D, Pj)
        lift = (origin[1] - rig.lowest(M)) * P.ground if P.ground > 0.0 else 0.0
        if lock and P.contact is not None and self.hand is None and float(np.max(P.contact)) > 0.01:
            if self._lock_feet(t, P, Pj, A, origin, qh, hd, lift):
                D, Pj, A = rig.fk(P.q, root, bm.qmul(qh, P.rot))
                M = rig.matrices(D, Pj)
        if lift:
            Pj = Pj + np.array([0.0, lift, 0.0])
            M = M.copy()
            M[:, 1, 3] += lift
        out = dict(M=M, P=Pj, D=D, A=A, origin=origin, heading=hd, speed=speed)
        if self.hand is not None and gest:
            out = self._place_hand(out, t)
        if len(self._cache) > 64:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = out
        return out

    def _lock_feet(self, t, P, Pj, A, origin, qh, hd, lift):
        """Keeps each planted foot where it was set down: the ankle stays at its place in the world from the
        start of its stance (turning with the body only by the turn of the body since then) and the leg bends
        to reach it. Changes P; returns True when it did."""
        rig = self.rig
        i = rig.idx
        done = False
        iq = bm.qconj(qh)
        for s, sd in enumerate(("L", "R")):
            c = float(bm.smooth(P.contact[s] * 1.25))
            if c < 0.01:
                continue
            t0 = self._stance_start(t, s)
            t_set = min(t, t0 + 0.05)
            if t - t_set < 1.0 / 240.0:
                continue
            f0 = self.frame(t_set, lock=False)
            W = f0["P"][i["foot." + sd]]
            # the place in this frame's own body space (before the frame is lifted onto the ground)
            here = bm.qrot(iq, W - origin - np.array([0.0, lift, 0.0]))
            ank_now = bm.qrot(iq, Pj[i["foot." + sd]] - origin)
            target = ank_now * (1.0 - c) + here * c
            hip = bm.qrot(iq, Pj[i["upperleg01." + sd]] - origin)
            knee = bm.qrot(iq, Pj[i["lowerleg01." + sd]] - origin)
            pole = knee - 0.5 * (hip + ank_now)
            # the foot keeps its own roll from heel to toe, and its heading from when it was set down
            fq = bm.qmul(iq, A[i["foot." + sd]])
            turn = (f0["heading"] - hd + np.pi) % (2 * np.pi) - np.pi
            fq = bm.qmul(bm.qy(turn * c), fq)
            # leg_to works in the space of local_fk: undo the body's own rotation about its root (P.rot)
            self.mo.leg_to(P, sd, target, knee=pole if np.linalg.norm(pole) > 1e-4 else None, foot=fq)
            done = True
        return done

    def _hand_pose(self, P, t):
        """Shapes the placed hand: hand["pose"] is a pose name, a dict, or keys [(t, pose), ...] eased between."""
        h = self.hand
        side = h.get("side", "R")
        pose = h.get("pose", "open")
        keyed = (isinstance(pose, (list, tuple)) and len(pose) and isinstance(pose[0], (list, tuple))
                 and len(pose[0]) == 2 and isinstance(pose[0][0], (int, float)))
        if keyed:
            keys = sorted(pose, key=lambda k: k[0])
            if t <= keys[0][0]:
                pose = keys[0][1]
            elif t >= keys[-1][0]:
                pose = keys[-1][1]
            else:
                for (t0, a), (t1, b) in zip(keys, keys[1:]):
                    if t < t1:
                        pose = (a, b, float(bm.smoother((t - t0) / (t1 - t0))))
                        break
        self.mo.hand_pose(P, side, pose)
        self.mo.arm(P, side, flex=25.0, abd=10.0, elbow=h.get("elbow", 22.0), wrist=h.get("wrist", -4.0))
        self.mo.hand_pose(P, side, pose)

    def _world(self, v, t):
        """A target given by a song (a point, or a function of time) as a point in this actor's own space."""
        p = np.asarray(v(t) if callable(v) else v, np.float64)
        return p if self.to_internal is None else self.to_internal(p, t)

    def _place_hand(self, f, t):
        """Moves the whole posed skeleton rigidly so that one hand is exactly where the song puts it: the palm
        centre at hand["at"], the fingers pointing along hand["aim"], the palm facing hand["palm"]."""
        h = self.hand
        side = h.get("side", "R")
        rig = self.rig
        w = rig.idx["wrist." + side]
        m3 = rig.idx["finger3-1." + side]
        k = rig.height / 1.6
        n0 = bm.qrot(f["A"][w], rig.palm_n[side])
        d0 = f["P"][m3] - f["P"][w]
        d0 /= max(np.linalg.norm(d0), 1e-9)
        c0 = 0.4 * f["P"][w] + 0.6 * f["P"][m3] + n0 * 0.012 * k
        if h.get("anchor", "palm") == "fingertips":
            tip = rig.idx["finger3-3." + side]
            c0 = f["P"][tip] + bm.qrot(f["D"][tip], rig.tail[tip] - rig.head[tip])
        elif h.get("anchor") == "wrist":
            c0 = f["P"][w]

        def basis(d, n):
            d = np.asarray(d, np.float64)
            d = d / max(np.linalg.norm(d), 1e-9)
            n = np.asarray(n, np.float64)
            n = n - np.dot(n, d) * d
            if np.linalg.norm(n) < 1e-6:
                n = np.cross(d, [0.0, 1.0, 0.0])
                if np.linalg.norm(n) < 1e-6:
                    n = np.cross(d, [1.0, 0.0, 0.0])
            n = n / np.linalg.norm(n)
            return np.stack([d, n, np.cross(d, n)], axis=1)

        aim = h.get("aim", (0.0, 0.0, 1.0))
        palm = h.get("palm", (0.0, 1.0, 0.0))
        aim = aim(t) if callable(aim) else aim
        palm = palm(t) if callable(palm) else palm
        B0 = basis(d0, n0)
        B1 = basis(aim, palm)
        Rg = B1 @ B0.T
        at = self._world(h["at"], t)
        Tg = at - Rg @ c0
        qg = bm.qfrommat(Rg)
        M = f["M"].astype(np.float64)
        M2 = np.empty_like(M)
        M2[:, :, :3] = np.einsum("ij,bjk->bik", Rg, M[:, :, :3])
        M2[:, :, 3] = M[:, :, 3] @ Rg.T + Tg
        return dict(M=M2.astype(np.float32), P=f["P"] @ Rg.T + Tg, D=bm.qmul(qg[None], f["D"]), A=bm.qmul(qg[None], f["A"]),
                    origin=at, heading=f["heading"], speed=f["speed"])

    # ------------------------------------------------------------------ named places on the body
    def _build_anchors(self):
        rig = self.rig
        i = rig.idx
        v = rig.verts0.astype(np.float64)
        k = rig.height / 1.6
        A = {}

        def fix(name, bone, p, n=(0.0, 0.0, 1.0)):
            A[name] = (i[bone] if isinstance(bone, str) else int(bone), np.asarray(p, np.float64), np.asarray(n, np.float64))

        hc = rig.head_centre
        hv = v[rig.vert_bone == i["head"]]
        fix("head", "head", hc)
        fix("crown", "head", [0.0, hv[:, 1].max(), hc[2] - 0.01 * k], (0.0, 1.0, 0.0))
        fix("mouth", "head", self.mo.mouth)
        fix("neck", "neck01", rig.head[i["neck02"]], (0.0, 0.0, -1.0))
        torso = np.isin(rig.bone_region[rig.vert_bone], [2])
        yh = rig.head[i["spine01"]][1] - 0.035 * k
        for name, x0, sgn in (("heart", 0.035 * k, 1.0), ("chest", 0.0, 1.0), ("back", 0.0, -1.0)):
            sel = np.where(torso & (np.abs(v[:, 1] - yh) < 0.025 * k) & (np.abs(v[:, 0] - x0) < 0.035 * k))[0]
            j = sel[np.argmax(v[sel, 2] * sgn)]
            fix(name, rig.vert_bone[j], v[j], (0.0, 0.0, sgn))
        fix("pelvis", "root", rig.head[i["spine05"]], (0.0, 0.0, 1.0))
        for s, sg in (("L", 1.0), ("R", -1.0)):
            sh = rig.head[i["upperarm01." + s]]
            sel = np.where((np.abs(v[:, 0] - (sh[0] - sg * 0.035 * k)) < 0.03 * k) & (v[:, 1] > sh[1]) & (v[:, 1] < sh[1] + 0.1 * k)
                           & (np.abs(v[:, 2] - sh[2]) < 0.05 * k))[0]
            j = sel[np.argmax(v[sel, 1])]
            fix("shoulder." + s, "shoulder01." + s, v[j], (0.0, 1.0, 0.0))
            sel = np.where(torso & (np.abs(v[:, 1] - (sh[1] - 0.09 * k)) < 0.03 * k) & (np.abs(v[:, 0] - sg * 0.085 * k) < 0.035 * k))[0]
            j = sel[np.argmin(v[sel, 2])]
            fix("blade." + s, rig.vert_bone[j], v[j], (0.0, 0.0, -1.0))
            fix("elbow." + s, "lowerarm01." + s, rig.head[i["lowerarm01." + s]])
            fix("wrist." + s, "wrist." + s, rig.head[i["wrist." + s]])
            fix("fingertips." + s, "finger3-3." + s, rig.tail[i["finger3-3." + s]])
            fix("index." + s, "finger2-3." + s, rig.tail[i["finger2-3." + s]])
            fix("thumb." + s, "finger1-3." + s, rig.tail[i["finger1-3." + s]])
            fix("hip." + s, "upperleg01." + s, rig.head[i["upperleg01." + s]])
            fix("knee." + s, "lowerleg01." + s, rig.head[i["lowerleg01." + s]])
            fix("ankle." + s, "foot." + s, rig.head[i["foot." + s]])
            fv = v[rig.vert_bone == i["foot." + s]]
            fix("toe." + s, "foot." + s, fv[np.argmax(fv[:, 2])], (0.0, 0.0, 1.0))
            sel = np.where(torso & (np.abs(v[:, 1] - (sh[1] - 0.16 * k)) < 0.03 * k) & (v[:, 0] * sg > 0))[0]
            j = sel[np.argmax(v[sel, 0] * sg)]
            fix("side." + s, rig.vert_bone[j], v[j], (sg, 0.0, 0.0))        # under the arm: where a child is lifted
        return A

    ANCHORS = ("head", "crown", "mouth", "neck", "heart", "chest", "back", "pelvis", "ground",
               "shoulder", "blade", "elbow", "wrist", "palm", "fingertips", "index", "thumb", "pinch", "hip", "knee",
               "ankle", "toe", "side")

    def where(self, t, name, normal=False, raw=False):
        """A named place on the body at t, in the actor's own space: its position, or (position, direction it
        faces) with normal=True. Names: head, crown, mouth, neck, heart, chest, back, pelvis, ground, and with
        .L or .R: shoulder, blade (shoulder blade), elbow, wrist, palm, fingertips, index, thumb, pinch (between
        thumb and index: where a thread is held), hip, knee, ankle, toe, side (under the arm). Any bone name
        gives that joint."""
        if self._anc is None:
            self._anc = self._build_anchors()
        f = self.frame(t, gest=not raw)
        base = name.split(".")[0]
        if base == "palm":
            c, n, _d = self.palm(t, name[-1], raw)
            return (c, n) if normal else c
        if base == "pinch":
            a = self.where(t, "thumb." + name[-1], raw=raw)
            b = self.where(t, "index." + name[-1], raw=raw)
            p = 0.5 * (a + b)
            return (p, self.palm(t, name[-1], raw)[1]) if normal else p
        if name == "ground":
            p = f["origin"].copy()
            return (p, np.array([0.0, 1.0, 0.0])) if normal else p
        if name in self._anc:
            bone, p0, n0 = self._anc[name]
            m = f["M"][bone].astype(np.float64)
            p = m[:, :3] @ p0 + m[:, 3]
            return (p, bm.qrot(f["D"][bone], n0)) if normal else p
        if name in self.rig.idx:
            p = f["P"][self.rig.idx[name]].copy()
            return (p, np.array([0.0, 1.0, 0.0])) if normal else p
        raise KeyError("no place called %r on a body (see Actor.where)" % (name,))

    def joint(self, t, bone):
        """Position of a joint (the head of a bone) at t."""
        return self.frame(t)["P"][self.rig.idx[bone]].copy()

    def palm(self, t, side="R", raw=False):
        """(centre of the palm, the direction it faces, the direction the fingers point) at t."""
        rig = self.rig
        f = self.frame(t, gest=not raw)
        w = rig.idx["wrist." + side]
        m3 = rig.idx["finger3-1." + side]
        c = 0.4 * f["P"][w] + 0.6 * f["P"][m3]
        n = bm.qrot(f["A"][w], rig.palm_n[side])
        d = f["P"][m3] - f["P"][w]
        d /= max(np.linalg.norm(d), 1e-9)
        return c + n * 0.012 * rig.height / 1.6, n, d

    def mouth(self, t):
        """(the place just before the lips, the direction the face looks) at t."""
        rig = self.rig
        f = self.frame(t)
        h = rig.idx["head"]
        p = f["P"][h] + bm.qrot(f["A"][h], self.mo.mouth - rig.neutral_pos[h])
        return p, bm.qrot(f["A"][h], [0.0, 0.0, 1.0])
