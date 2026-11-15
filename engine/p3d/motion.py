"""How the particle bodies move: real walk and run cycles, and gestures posed by hand on the skeleton.

Two layers, both pure functions of time:
  MOTIONS   whole-body states a figure can be in: "stand", "walk", "run", "kneel" (and the extra clips "jump",
            "spin", "dance_a", "dance_b").
  GESTURES  what the upper body does on top of that: "look_up", "reach", "open_arms", "blow", "raise",
            "pray", "bow".
engine/p3d/body.py blends between them with eased crossfades, so a figure can walk, stop, look up and reach
without a cut. Walk and run are motion capture (the DeepMimic reference clips, see assets/p3d/README.md),
retargeted onto the MakeHuman skeleton; everything else is posed here in degrees against the neutral pose.

Sign rules in the neutral pose (body frame: x is the body's left, y up, z forward):
  bend forward: +x rotation for spine and head, -x for hip and shoulder (the limb swings forward), +x for the
  knee (the shin swings back), -x for the elbow (the forearm swings forward).
"""
import numpy as np

from . import bodymath as bm

DEG = np.pi / 180.0
DM_LEG = 0.8314          # hip to ankle of the figure the motion clips were recorded for, metres

MOTIONS = ("stand", "walk", "run", "kneel", "jump", "spin", "dance_a", "dance_b")
GESTURES = ("look_up", "reach", "open_arms", "blow", "raise", "pray", "bow")
SPINE = ("spine05", "spine04", "spine03", "spine02")
NECK = ("neck01", "neck02", "neck03")


class Pose:
    """Local rotations of every bone (in the neutral frames) and where the root joint is."""
    __slots__ = ("q", "pos", "rot", "ground")

    def __init__(self, nb):
        self.q = np.tile(bm.IDENT, (nb, 1))
        self.pos = np.zeros(3)        # root joint: offset from its neutral place, body frame, metres
        self.rot = bm.IDENT.copy()    # the whole body turned about the root joint, body frame
        self.ground = 1.0             # 1: the lowest sole or knee is set on the ground; 0: pos[1] as given

    def copy(self):
        p = Pose.__new__(Pose)
        p.q = self.q.copy()
        p.pos = self.pos.copy()
        p.rot = self.rot.copy()
        p.ground = self.ground
        return p


def blend(a, b, u):
    """The pose a share u of the way from a to b."""
    if u <= 0.0:
        return a
    if u >= 1.0:
        return b
    p = Pose.__new__(Pose)
    p.q = bm.qslerp(a.q, b.q, u)
    p.pos = a.pos * (1 - u) + b.pos * u
    p.rot = bm.qslerp(a.rot, b.rot, u)
    p.ground = a.ground * (1 - u) + b.ground * u
    return p


class Clip:
    """One motion capture clip, converted to this engine's axes (x left, y up, z forward)."""

    def __init__(self, frames, loop, scale):
        f = np.asarray(frames, np.float64)
        self.n = len(f)
        self.dt = f[:-1, 0].copy()
        self.time = np.concatenate([[0.0], np.cumsum(self.dt)])
        self.T = float(self.time[-1])
        self.loop = bool(loop)
        self.scale = scale

        def conv(q):          # (w, x, y, z) with x forward, z right  ->  x left, z forward
            return bm.qn(np.stack([q[:, 0], -q[:, 3], q[:, 2], q[:, 1]], axis=1))

        def hinge(a):         # one angle about the old z axis (right): about -x here
            return np.stack([np.cos(a * 0.5), -np.sin(a * 0.5), np.zeros_like(a), np.zeros_like(a)], axis=1)

        self.root_pos = np.stack([-f[:, 3], f[:, 2], f[:, 1]], axis=1)
        self.j = dict(root=conv(f[:, 4:8]), chest=conv(f[:, 8:12]), neck=conv(f[:, 12:16]),
                      rhip=conv(f[:, 16:20]), rknee=hinge(f[:, 20]), rankle=conv(f[:, 21:25]),
                      rsho=conv(f[:, 25:29]), relb=hinge(f[:, 29]),
                      lhip=conv(f[:, 30:34]), lknee=hinge(f[:, 34]), lankle=conv(f[:, 35:39]),
                      lsho=conv(f[:, 39:43]), lelb=hinge(f[:, 43]))
        self.delta = self.root_pos[-1] - self.root_pos[0] if self.loop else np.zeros(3)
        self.delta[1] = 0.0
        self.stride = float(np.linalg.norm(self.delta)) * scale      # metres travelled per cycle
        self.speed = self.stride / self.T
        self.y_mean = float(self.root_pos[:, 1].mean())
        self.lift = 0.0       # set by Motions for clips with flight (run, jump)
        self._stack = None

    def sample(self, tt):
        """Joint rotations and the root's place at clip time tt (seconds; loops wrap)."""
        ph = tt % self.T if self.loop else min(max(tt, 0.0), self.T)
        k = int(np.searchsorted(self.time, ph, side="right")) - 1
        k = min(max(k, 0), self.n - 2)
        u = (ph - self.time[k]) / self.dt[k]
        if self._stack is None:
            self._names = list(self.j)
            self._stack = np.stack([self.j[n] for n in self._names], axis=1)       # (frames, joints, 4)
        q = bm.qslerp(self._stack[k], self._stack[k + 1], u)
        j = {name: q[n] for n, name in enumerate(self._names)}
        rp = self.root_pos[k] * (1 - u) + self.root_pos[k + 1] * u
        res = rp - self.root_pos[0] - self.delta * (ph / self.T)      # what is left besides steady travel
        return j, res, rp[1]


class Motions:
    """Everything a rig can do. `pose(name, t, age, **params)` gives a whole-body Pose; `gesture(name, pose, w,
    t, age, **params)` bends the upper body of a pose toward a gesture by weight w."""

    def __init__(self, rig, clips):
        self.rig = rig
        self.i = rig.idx
        s = rig.leg_len / DM_LEG
        self.clips = {}
        for name in ("walk", "run", "jump", "spin", "dance_a", "dance_b"):
            self.clips[name] = Clip(clips["clip_" + name], bool(clips["clip_" + name + "_loop"]), s)
        self.arm_len = {}
        P = rig.neutral_pos
        for sd in ("L", "R"):
            ua, fa, wr = self.i["upperarm01." + sd], self.i["lowerarm01." + sd], self.i["wrist." + sd]
            self.arm_len[sd] = (float(np.linalg.norm(P[fa] - P[ua])), float(np.linalg.norm(P[wr] - P[fa])))
        self.k = rig.height / 1.6          # sizes below are written for a 1.6 m body
        hc = rig.head_centre
        self.mouth = hc + np.array([0.0, -0.060, 0.082]) * self.k
        self._calibrated = set()
        self._ftab = {}

    # ------------------------------------------------------------------ small tools
    def identity(self):
        return Pose(self.rig.nb)

    def local_fk(self, P):
        return self.rig.fk(P.q, self.rig.neutral_pos[0] + P.pos, P.rot)

    def _set(self, P, bone, q, w=1.0):
        b = self.i[bone]
        P.q[b] = q if w >= 1.0 else bm.qslerp(P.q[b], q, w)

    def _add(self, P, bone, q):
        b = self.i[bone]
        P.q[b] = bm.qmul(P.q[b], q)

    def arm(self, P, side, flex=0.0, abd=0.0, twist=0.0, elbow=0.0, sup=0.0, wrist=0.0, w=1.0):
        """Sets one arm by angles (degrees): shoulder flexion (forward), abduction (sideways), twist (positive
        turns the palm forward), elbow bend, forearm supination (positive turns the palm up or forward), wrist
        flexion (negative: extension)."""
        sg = 1.0 if side == "L" else -1.0
        q = bm.qmul(bm.qx(-flex * DEG), bm.qmul(bm.qz(sg * abd * DEG), bm.qy(sg * twist * DEG)))
        self._set(P, "upperarm01." + side, q, w)
        self._set(P, "upperarm02." + side, bm.IDENT, w)
        self._set(P, "lowerarm01." + side, bm.qx(-elbow * DEG), w)
        self._set(P, "lowerarm02." + side, bm.qy(sg * sup * DEG), w)
        self._set(P, "wrist." + side, self._wrist_q(side, wrist), w)

    def _wrist_q(self, side, flex):
        b = self.i["wrist." + side]
        axis = np.cross(self.rig.neutral_dir[b], self.rig.palm_n[side])
        return bm.qaxis(axis, flex * DEG)

    def _finger_table(self, side):
        """The bones of one hand's fingers with their curl axes (found once)."""
        if side not in self._ftab:
            rig = self.rig
            pn = rig.palm_n[side]
            bones, axes, share, finger, first = [], [], [], [], []
            for f in (2, 3, 4, 5, 1):
                for k, sh in (((1, 0.9), (2, 1.15), (3, 0.75)) if f != 1 else ((1, 0.5), (2, 0.9), (3, 0.8))):
                    b = self.i["finger%d-%d.%s" % (f, k, side)]
                    ax = np.cross(rig.neutral_dir[b], pn)
                    bones.append(b)
                    axes.append(ax / max(np.linalg.norm(ax), 1e-9))
                    share.append(sh)
                    finger.append(f)
                    first.append(k == 1)
            self._ftab[side] = (np.array(bones), np.array(axes), np.array(share), np.array(finger), np.array(first))
        return self._ftab[side]

    def fingers(self, P, side, curl=22.0, thumb=14.0, spread=0.0, w=1.0, lead=0.0):
        """Curls the fingers toward the palm (degrees per joint, a natural cascade from index to little finger).
        lead > 0 keeps the index finger straighter than the rest (a reaching hand)."""
        bones, axes, share, finger, first = self._finger_table(side)
        amt = curl * (0.82 + 0.11 * (finger - 2)) * (1.0 - lead * np.where(finger == 2, 1.0, np.where(finger == 3, 0.35, 0.0)))
        amt = np.where(finger == 1, thumb, amt) * share * (DEG * 0.5)
        q = np.concatenate([np.cos(amt)[:, None], axes * np.sin(amt)[:, None]], axis=1)
        if spread:
            sg = 1.0 if side == "L" else -1.0
            m = first & (finger != 1)
            sq = bm.qaxis(np.broadcast_to(self.rig.palm_n[side], (int(m.sum()), 3)), sg * spread * (finger[m] - 3.5) * DEG)
            q[m] = bm.qmul(sq, q[m])
        P.q[bones] = q if w >= 1.0 else bm.qslerp(P.q[bones], q, w)

    def arm_to(self, P, side, target, pole=None, palm=None, w=1.0, wrist=0.0):
        """Bends one arm so that the wrist reaches `target` (a point in the body frame, metres; as far as the
        arm is long). pole: where the elbow tends (default down, a little out and back). palm: the direction
        the palm should face, as far as the forearm can turn."""
        rig = self.rig
        sg = 1.0 if side == "L" else -1.0
        ua, fa = self.i["upperarm01." + side], self.i["lowerarm01." + side]
        _, Pj, A = self.local_fk(P)
        S = Pj[ua]
        L1, L2 = self.arm_len[side]
        v = np.asarray(target, np.float64) - S
        d0 = np.linalg.norm(v)
        ax = v / max(d0, 1e-9)
        d = min(max(d0, abs(L1 - L2) + 1e-3), (L1 + L2) * 0.985)
        a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
        r = np.sqrt(max(L1 * L1 - a * a, 0.0))
        if pole is None:
            pole = bm.qrot(P.rot, np.array([sg * 0.45, -1.0, -0.45]))
        pole = np.asarray(pole, np.float64)
        pp = pole - np.dot(pole, ax) * ax
        if np.linalg.norm(pp) < 1e-6:
            pp = np.cross(ax, [0.0, 0.0, 1.0])
        pp /= np.linalg.norm(pp)
        E = S + a * ax + r * pp
        u1 = (E - S) / L1
        u2 = (S + ax * d - E) / L2
        n = np.cross(u1, u2)
        if np.linalg.norm(n) < 1e-6:
            n = np.cross(u1, pp)
        n /= np.linalg.norm(n)
        M = np.stack([-n, -u1, np.cross(n, u1)], axis=1)
        A_up = bm.qfrommat(M)
        e = np.arccos(np.clip(np.dot(u1, u2), -1.0, 1.0))
        q_up = bm.qmul(bm.qconj(A[rig.parent[ua]]), A_up)
        self._set(P, "upperarm01." + side, q_up, w)
        self._set(P, "upperarm02." + side, bm.IDENT, w)
        self._set(P, "lowerarm01." + side, bm.qx(-e), w)
        if palm is not None:
            A_fa = bm.qmul(A_up, bm.qx(-e))
            n0 = bm.qrot(A_fa, rig.palm_n[side])
            pd = np.asarray(palm, np.float64)
            a0 = n0 - np.dot(n0, u2) * u2
            b0 = pd - np.dot(pd, u2) * u2
            if np.linalg.norm(a0) > 1e-6 and np.linalg.norm(b0) > 1e-6:
                phi = np.arctan2(np.dot(u2, np.cross(a0, b0)), np.dot(a0, b0))
                phi = float(np.clip(phi, -110 * DEG, 110 * DEG))
                self._set(P, "lowerarm02." + side, bm.qaxis([0.0, -1.0, 0.0], phi), w)
        self._set(P, "wrist." + side, self._wrist_q(side, wrist), w)

    def leg_to(self, P, side, ankle, knee=None, foot=None):
        """Bends one leg so that the ankle is at `ankle` (body frame). knee: where the knee points (default
        forward). foot: the foot's own rotation in the body frame (default flat, toes a little out)."""
        rig = self.rig
        sg = 1.0 if side == "L" else -1.0
        ul, ll, ft = self.i["upperleg01." + side], self.i["lowerleg01." + side], self.i["foot." + side]
        _, Pj, A = self.local_fk(P)
        S = Pj[ul]
        N = rig.neutral_pos
        L1 = float(np.linalg.norm(N[ll] - N[ul]))
        L2 = float(np.linalg.norm(N[ft] - N[ll]))
        v = np.asarray(ankle, np.float64) - S
        d0 = np.linalg.norm(v)
        ax = v / max(d0, 1e-9)
        d = min(max(d0, abs(L1 - L2) + 1e-3), (L1 + L2) * 0.9995)
        a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
        r = np.sqrt(max(L1 * L1 - a * a, 0.0))
        pole = np.array([sg * 0.12, 0.0, 1.0]) if knee is None else np.asarray(knee, np.float64)
        pp = pole - np.dot(pole, ax) * ax
        pp /= max(np.linalg.norm(pp), 1e-9)
        E = S + a * ax + r * pp
        u1 = (E - S) / L1
        u2 = (S + ax * d - E) / L2
        n = np.cross(u1, u2)
        if np.linalg.norm(n) < 1e-6:
            n = np.cross(u1, -pp)
        n /= np.linalg.norm(n)
        M = np.stack([n, -u1, np.cross(u1, n)], axis=1)
        A_up = bm.qfrommat(M)
        e = np.arccos(np.clip(np.dot(u1, u2), -1.0, 1.0))
        P.q[ul] = bm.qmul(bm.qconj(A[rig.parent[ul]]), A_up)
        P.q[self.i["upperleg02." + side]] = bm.IDENT
        P.q[ll] = bm.qx(e)
        A_shin = bm.qmul(A_up, bm.qx(e))
        fq = bm.qy(sg * 7 * DEG) if foot is None else foot
        P.q[self.i["lowerleg02." + side]] = bm.IDENT
        P.q[ft] = bm.qmul(bm.qconj(A_shin), fq)

    def breathe(self, P, t, seed=0.0, depth=1.0):
        """Breathing and the small drift of a living body, added to any pose."""
        b = np.sin(2 * np.pi * t / (3.9 + 0.8 * bm.hashf(int(seed * 977) + 3)) + seed * 5.0)
        b = b * depth
        self._add(P, "spine03", bm.qx(-0.5 * DEG * b))
        self._add(P, "spine02", bm.qx(-0.8 * DEG * b))
        self._add(P, "neck01", bm.qx(0.5 * DEG * b))
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            self._add(P, "clavicle." + sd, bm.qz(sg * 1.3 * DEG * (b * 0.5 + 0.5)))

    # ------------------------------------------------------------------ whole-body motions
    def pose(self, name, t, age=0.0, **kw):
        if name not in MOTIONS:
            raise ValueError("motion must be one of %s, got %r" % (MOTIONS, name))
        if name in self.clips:
            return self.clip_pose(name, kw.pop("clip_time", age), **kw)
        return getattr(self, "m_" + name)(t, age, **kw)

    def clip_pose(self, name, tt, arms_out=9.0, **kw):
        """A pose from a motion capture clip at clip time tt (seconds)."""
        c = self.clips[name]
        j, res, ry = c.sample(tt)
        P = self.identity()
        i = self.i
        P.rot = j["root"]
        for b in SPINE:
            P.q[i[b]] = bm.qpow(j["chest"], 0.25)
        for b in NECK:
            P.q[i[b]] = bm.qpow(j["neck"], 1.0 / 6.0)
        P.q[i["head"]] = bm.qpow(j["neck"], 0.5)
        for sd, pre, sg in (("L", "l", 1.0), ("R", "r", -1.0)):
            P.q[i["upperleg01." + sd]] = bm.qmul(bm.qz(sg * 2.0 * DEG), j[pre + "hip"])
            P.q[i["lowerleg01." + sd]] = j[pre + "knee"]
            P.q[i["foot." + sd]] = j[pre + "ankle"]
            P.q[i["upperarm01." + sd]] = bm.qmul(bm.qz(sg * arms_out * DEG), bm.qmul(j[pre + "sho"], bm.qy(-sg * 12 * DEG)))
            P.q[i["lowerarm01." + sd]] = bm.qmul(j[pre + "elb"], bm.qx(-6 * DEG))
            self._set(P, "wrist." + sd, self._wrist_q(sd, 6.0))
            self.fingers(P, sd, curl=24.0, thumb=14.0)
        P.pos = np.array([res[0] * c.scale, 0.0, res[2] * c.scale])
        if name == "walk":
            P.ground = 1.0
        else:
            P.ground = 0.0
            P.pos[1] = (ry - c.y_mean) * c.scale + self._lift(name)
        return P

    def _lift(self, name):
        """For clips where both feet leave the ground: the root height that puts the lowest moment of the
        cycle on the ground (found once)."""
        c = self.clips[name]
        if name not in self._calibrated:
            self._calibrated.add(name)
            c.lift = 0.0
            lows = []
            for k in range(48):
                P = self.clip_pose(name, c.T * k / 48.0)
                D, Pj, _ = self.local_fk(P)
                lows.append(self.rig.lowest(self.rig.matrices(D, Pj)))
            c.lift = -float(np.percentile(lows, 4))
        return c.lift

    def m_stand(self, t, age=0.0, seed=0.0, calm=1.0, **kw):
        """Standing at ease: weight a little on one leg, breathing, small drift, relaxed hands."""
        P = self.identity()
        k = self.k
        side = 1.0 if bm.hashf(int(seed * 1000) + 17) > 0.5 else -1.0
        sh = 0.55 + 0.35 * bm.wobble(t, seed + 0.3, 0.11)
        P.pos = np.array([side * 0.020 * sh + 0.005 * bm.wobble(t, seed + 1.1, 0.33),
                          -0.004 - 0.004 * sh,
                          0.006 * bm.wobble(t, seed + 2.2, 0.21)]) * k * calm
        P.rot = bm.qmul(bm.qz(side * sh * 2.2 * DEG * calm), bm.qy(1.2 * DEG * bm.wobble(t, seed + 3.3, 0.17)))
        self._set(P, "spine04", bm.qz(-side * sh * 1.2 * DEG * calm))
        self._set(P, "spine03", bm.qz(-side * sh * 1.0 * DEG * calm))
        self._set(P, "neck02", bm.qeuler(1.0 * DEG * bm.wobble(t, seed + 4.4, 0.23),
                                         2.0 * DEG * bm.wobble(t, seed + 5.5, 0.19), 0.0))
        self._set(P, "head", bm.qeuler((2.0 + 1.5 * bm.wobble(t, seed + 6.6, 0.27)) * DEG,
                                       2.5 * DEG * bm.wobble(t, seed + 7.7, 0.15),
                                       -side * 1.0 * DEG))
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            wv = bm.wobble(t, seed + 8.8 + sg, 0.29)
            self.arm(P, sd, flex=2.0 + 1.5 * wv, abd=7.5 + 0.8 * wv, twist=-8.0, elbow=13.0 + 2.5 * wv, sup=0.0,
                     wrist=5.0)
            self.fingers(P, sd, curl=22.0 + 3.0 * wv, thumb=14.0)
        N = self.rig.neutral_pos
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            free = 1.0 if sg != side else 0.0
            ankle = N[self.i["foot." + sd]] + np.array([sg * 0.012 + sg * 0.010 * free, 0.0, 0.028 * free]) * k
            self.leg_to(P, sd, ankle, foot=bm.qy(sg * (7.0 + 5.0 * free) * DEG))
        P.ground = 1.0
        return P

    def m_walk(self, t, age=0.0, **kw):
        return self.clip_pose("walk", kw.get("clip_time", age))

    def m_run(self, t, age=0.0, **kw):
        return self.clip_pose("run", kw.get("clip_time", age))

    def m_kneel(self, t, age=0.0, seed=0.0, sit=0.3, dur=2.0, hands="lap", one=False, **kw):
        """Sinking to the knees over `dur` seconds and staying there. sit: 0 upright on the knees, 1 sitting
        back on the heels. one=True: a genuflection, one knee down, the other foot forward.
        hands: "lap" (resting on the thighs), "pray" (together before the chest) or "free" (left to gestures)."""
        S = self.m_stand(t, age, seed=seed, calm=1.0)
        p = bm.smoother(age / max(dur, 1e-3))
        pr = bm.smoother(np.clip(age / max(dur, 1e-3) * 1.25, 0, 1))             # the right leg leads
        pl = bm.smoother(np.clip(age / max(dur, 1e-3) * 1.25 - 0.25, 0, 1))
        K = self.identity()
        hipf = 8.0 + 50.0 * sit
        knee = 98.0 + 47.0 * sit
        K.rot = bm.qx((4.0 + 6.0 * sit) * DEG)
        for b in SPINE:
            self._set(K, b, bm.qx((1.0 - 1.5 * sit) * DEG))
        self._set(K, "neck02", bm.qx(5.0 * DEG))
        self._set(K, "head", bm.qx(9.0 * DEG))
        legs = {}
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            if one and sd == "L":
                legs[sd] = (bm.qmul(bm.qx(-88 * DEG), bm.qz(sg * 4 * DEG)), bm.qx(92 * DEG), bm.qx(-2 * DEG))
            else:
                legs[sd] = (bm.qmul(bm.qx(-hipf * DEG), bm.qz(sg * 3 * DEG)), bm.qx(knee * DEG),
                            bm.qx((62.0 + 12.0 * sit) * DEG))
        if one:
            K.rot = bm.qx(2.0 * DEG)
            legs["R"] = (bm.qmul(bm.qx(6 * DEG), bm.qz(-2 * DEG)), bm.qx(96 * DEG), bm.qx(58 * DEG))
        P = blend(S, K, float(p))
        i = self.i
        for sd, prog in (("L", pl), ("R", pr)):
            hq, kq, fq = legs[sd]
            # on the way down the knee bends first while the thigh stays under the body, then the thigh settles
            mid_h = bm.qx(-(34.0 if sd == "L" else -6.0) * DEG)
            u = float(prog)
            h = bm.qslerp(bm.qslerp(S.q[i["upperleg01." + sd]], mid_h, min(u * 2, 1.0)), hq, max(u * 2 - 1, 0.0))
            P.q[i["upperleg01." + sd]] = h
            P.q[i["upperleg02." + sd]] = bm.IDENT
            P.q[i["lowerleg01." + sd]] = bm.qslerp(S.q[i["lowerleg01." + sd]], kq, u)
            P.q[i["lowerleg02." + sd]] = bm.IDENT
            P.q[i["foot." + sd]] = bm.qslerp(S.q[i["foot." + sd]], fq, bm.smooth(u * 1.2 - 0.2))
        P.ground = 1.0
        if hands != "free":
            _, Pj, _ = self.local_fk(P)
            w = float(p)
            for sd, sg in (("L", 1.0), ("R", -1.0)):
                if hands == "pray":
                    c = Pj[i["spine02"]] + bm.qrot(P.rot, np.array([sg * 0.012, 0.05, 0.17]) * self.k)
                    self.arm_to(P, sd, c, palm=bm.qrot(P.rot, [-sg, 0.0, 0.0]), w=w, wrist=-28.0 * w,
                                pole=bm.qrot(P.rot, [sg * 0.8, -1.0, 0.1]))
                    self.fingers(P, sd, curl=4.0, thumb=6.0, w=w)
                else:
                    kn = Pj[i["lowerleg01." + sd]]
                    hp = Pj[i["upperleg01." + sd]]
                    c = hp + (kn - hp) * 0.62 + bm.qrot(P.rot, np.array([sg * 0.01, 0.075, 0.02]) * self.k)
                    self.arm_to(P, sd, c, palm=kn - hp + np.array([0.0, -0.6, 0.0]), w=w, wrist=-6.0 * w)
                    self.fingers(P, sd, curl=14.0, thumb=10.0, w=w)
        return P

    # ------------------------------------------------------------------ gestures (upper body)
    def gesture(self, name, P, w, t, age=0.0, **kw):
        if name not in GESTURES:
            raise ValueError("gesture must be one of %s, got %r" % (GESTURES, name))
        if w <= 0.0:
            return P
        getattr(self, "g_" + name)(P, float(w), t, age, **kw)
        return P

    def _lean(self, P, w, fwd=0.0, twist=0.0, side=0.0):
        for b in SPINE:
            self._add(P, b, bm.qeuler(fwd * DEG * w / 4, twist * DEG * w / 4, side * DEG * w / 4))

    def _head(self, P, w, up=0.0, turn=0.0, tilt=0.0):
        for b in NECK:
            self._add(P, b, bm.qeuler(-up * DEG * w * 0.17, turn * DEG * w * 0.17, tilt * DEG * w * 0.17))
        self._add(P, "head", bm.qeuler(-up * DEG * w * 0.49, turn * DEG * w * 0.49, tilt * DEG * w * 0.49))

    def g_look_up(self, P, w, t, age=0.0, amount=32.0, turn=0.0, **kw):
        """Lifts the face to the sky (amount: degrees)."""
        self._lean(P, w, fwd=-amount * 0.22)
        self._head(P, w, up=amount * 0.9, turn=turn)
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            self._add(P, "clavicle." + sd, bm.qy(sg * 4 * DEG * w))

    def g_bow(self, P, w, t, age=0.0, amount=24.0, **kw):
        """Bows the head and shoulders."""
        self._lean(P, w, fwd=amount * 0.5)
        self._head(P, w, up=-amount * 0.8)

    def g_reach(self, P, w, t, age=0.0, side="R", to=None, palm="up", height=0.0, far=0.92, lead=0.6, **kw):
        """One hand reaches forward. to: a point in the body frame to reach for (default: straight ahead at
        chest height plus `height` metres); far: how much of the arm's length is used; palm: "up", "in",
        "down" or a direction; lead: how much the index finger leads (the reaching hand of ref 04)."""
        sg = 1.0 if side == "L" else -1.0
        self._lean(P, w, fwd=5.0, twist=-sg * 9.0)
        self._head(P, w, up=-4.0 + height * 30.0, turn=-sg * 4.0)
        self._add(P, "clavicle." + side, bm.qy(-sg * 9 * DEG * w))
        if to is None:
            _, Pj, _ = self.local_fk(P)
            S = Pj[self.i["upperarm01." + side]]
            L = sum(self.arm_len[side])
            d = np.array([-sg * 0.12, -0.10 + height / max(L, 1e-6) * 1.0, 1.0])
            d = bm.qrot(P.rot, d / np.linalg.norm(d))
            to = S + d * L * far
        pd = dict(up=[0.0, 1.0, 0.15], down=[0.0, -1.0, 0.0], **{"in": [-sg, 0.2, 0.0]}).get(palm, palm) \
            if isinstance(palm, str) else palm
        self.arm_to(P, side, to, palm=bm.qrot(P.rot, pd), w=w, wrist=-8.0)
        self.fingers(P, side, curl=13.0 * w + 22.0 * (1 - w), thumb=8.0, spread=3.0 * w, lead=lead * w)

    def g_open_arms(self, P, w, t, age=0.0, lift=0.0, **kw):
        """Both arms open, palms forward: low and welcoming at lift 0, wide at 0.5, raised high at 1."""
        lf = float(np.clip(lift, 0.0, 1.0))
        self._lean(P, w, fwd=-3.0 - 5.0 * lf)
        self._head(P, w, up=3.0 + 14.0 * lf)
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            wv = bm.wobble(t, 3.1 + sg, 0.4)
            self.arm(P, sd, flex=14.0 + 10.0 * lf, abd=30.0 + 95.0 * lf + 1.5 * wv, twist=62.0 + 20.0 * lf,
                     elbow=20.0 + 8.0 * lf + 2.0 * wv, sup=52.0, wrist=-10.0, w=w)
            self.fingers(P, sd, curl=9.0 * w + 22.0 * (1 - w), thumb=5.0, spread=4.0 * w)
            self._add(P, "clavicle." + sd, bm.qz(sg * 14 * DEG * w * lf))

    def g_raise(self, P, w, t, age=0.0, **kw):
        """Both arms raised high (praise)."""
        self.g_open_arms(P, w, t, age, lift=1.0)

    def g_blow(self, P, w, t, age=0.0, side="R", **kw):
        """An open palm raised before the lips, the head bent a little toward it (the gift of ref 14)."""
        sg = 1.0 if side == "L" else -1.0
        self._lean(P, w, fwd=3.0, twist=-sg * 4.0)
        self._head(P, w, up=-7.0, turn=-sg * 2.0)
        self._add(P, "clavicle." + side, bm.qy(-sg * 6 * DEG * w))
        _, Pj, A = self.local_fk(P)
        hd = self.i["head"]
        mouth = Pj[hd] + bm.qrot(A[hd], self.mouth - self.rig.neutral_pos[hd])
        fwd = bm.qrot(A[hd], [0.0, 0.0, 1.0])
        left = bm.qrot(A[hd], [1.0, 0.0, 0.0])
        wrist = mouth + fwd * 0.185 * self.k + left * sg * 0.05 * self.k + np.array([0.0, -0.125, 0.0]) * self.k
        self.arm_to(P, side, wrist, palm=[0.0, 1.0, 0.0], w=w, wrist=-24.0,
                    pole=bm.qrot(P.rot, [sg * 0.35, -1.0, -0.2]))
        self.fingers(P, side, curl=5.0 * w + 22.0 * (1 - w), thumb=4.0, spread=2.0 * w)

    def g_pray(self, P, w, t, age=0.0, **kw):
        """Hands together before the chest, head bowed."""
        self._head(P, w, up=-10.0)
        _, Pj, _ = self.local_fk(P)
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            c = Pj[self.i["spine02"]] + bm.qrot(P.rot, np.array([sg * 0.012, 0.06, 0.17]) * self.k)
            self.arm_to(P, sd, c, palm=bm.qrot(P.rot, [-sg, 0.0, 0.0]), w=w, wrist=-30.0,
                        pole=bm.qrot(P.rot, [sg * 0.8, -1.0, 0.1]))
            self.fingers(P, sd, curl=4.0 * w + 22.0 * (1 - w), thumb=6.0)
