"""The larger library of gestures and motions for the particle bodies (the base ones are in motion.py).

Everything here is posed by hand on the skeleton, in degrees and metres for a 1.6 m body, with eased blends
done by engine/p3d/actor.py. A gesture bends a pose toward itself by a weight w (0..1); gestures that reach
for something take `to`: a point in the WORLD (or a function of time), usually another body's named place:

    a = Body(..., gesture=[(4, 9, "hand_on_shoulder", dict(side="R", to=lambda t: b.where(t, "shoulder.L")))])

CONTACT. `to` is met by the palm (end="palm", the default), the fingertips or the wrist, exactly as far as
the arm can reach. For two hands to meet, give both bodies the same point; for an embrace give `to` and `to2`
(left and right hand), usually the other's "blade.R" and "blade.L".

GESTURES added here
  touch              one hand goes to `to` (side, end, palm="down" | "up" | "in" | "fwd" or a direction)
  hand_on_shoulder   touch, palm down, resting
  handshake          the hand offered forward, palm inward, fingers ready to close (grip: 0..1)
  high_five          the open hand raised forward, palm out
  embrace            both arms round someone (to, to2), the body leans in, the head to one side
  arm_round          one arm round someone at the side (a child, a friend)
  cup                both hands together before the body, palms up, cupped
  offer              an open palm held out low
  listen             the head tilted and turned toward someone, leaning in
  raise_hand         one arm raised high (joined hands raised together: give both the same `to`)
  clap               hands clapping every `period` seconds (height: 0 before the chest, 1 above the head)
  throw              a throw with the right or left arm: release at `lead` seconds after the gesture starts
  wave               a raised hand waving
  brace              braced against wind: a forearm before the face, leaning into it
  hold_thread        a hand held low before the body, thumb and index closed on a thread (place "pinch.R")

MOTIONS added here
  sit       sitting on the ground, knees drawn up, bowed (dur: seconds to sit down)
  shuffle   small steps on the spot (for turning with `facing` keys, or stepping aside with `at` keys)

HAND POSES (HAND_POSES): open, relaxed, flat, spread, cup, fist, point, pinch, offer, hold. Any gesture takes
fingers=<pose name> to shape the hand; Body(part="hand.R", hand=dict(pose=...)) uses them for close-ups.
"""
import numpy as np

from . import bodymath as bm

DEG = np.pi / 180.0

# curl in degrees per joint for (thumb, index, middle, ring, little), and the spread between the fingers
HAND_POSES = dict(
    open=dict(curl=(6, 5, 5, 6, 8), spread=4),
    relaxed=dict(curl=(14, 20, 23, 25, 27), spread=0),
    flat=dict(curl=(2, 0, 0, 0, 0), spread=0),
    spread=dict(curl=(0, 0, 0, 0, 0), spread=11),
    cup=dict(curl=(20, 32, 35, 37, 40), spread=-2),
    fist=dict(curl=(42, 84, 86, 88, 90), spread=0),
    point=dict(curl=(40, 4, 82, 86, 88), spread=0),
    pinch=dict(curl=(36, 46, 60, 64, 68), spread=0),
    offer=dict(curl=(8, 10, 12, 14, 16), spread=2),
    hold=dict(curl=(30, 55, 58, 60, 62), spread=0),
)

MORE_GESTURES = ("touch", "hand_on_shoulder", "handshake", "high_five", "embrace", "arm_round", "cup", "offer",
                 "listen", "raise_hand", "clap", "throw", "wave", "brace", "hold_thread")
MORE_MOTIONS = ("sit", "shuffle")

_PALM = dict(down=(0.0, -1.0, 0.0), up=(0.0, 1.0, 0.15), fwd=(0.0, 0.0, 1.0), back=(0.0, 0.0, -1.0))


class Library:
    # ------------------------------------------------------------------ hands
    def hand_pose(self, P, side, pose="relaxed", w=1.0):
        """Shapes one hand: a pose name, a dict(curl=(thumb, index, middle, ring, little), spread=...), or
        (pose a, pose b, mix) for something between two."""
        if isinstance(pose, (tuple, list)) and len(pose) == 3 and not isinstance(pose[0], (int, float)):
            a = self._pose_spec(pose[0])
            b = self._pose_spec(pose[1])
            m = float(pose[2])
            curl = np.asarray(a["curl"], float) * (1 - m) + np.asarray(b["curl"], float) * m
            spread = a.get("spread", 0) * (1 - m) + b.get("spread", 0) * m
        else:
            sp = self._pose_spec(pose)
            curl, spread = np.asarray(sp["curl"], float), sp.get("spread", 0)
        bones, axes, share, finger, first = self._finger_table(side)
        amt = curl[np.where(finger == 1, 0, finger - 1)] * share * (DEG * 0.5)
        q = np.concatenate([np.cos(amt)[:, None], axes * np.sin(amt)[:, None]], axis=1)
        if spread:
            sg = 1.0 if side == "L" else -1.0
            m = first & (finger != 1)
            sq = bm.qaxis(np.broadcast_to(self.rig.palm_n[side], (int(m.sum()), 3)), sg * spread * (finger[m] - 3.5) * DEG)
            q[m] = bm.qmul(sq, q[m])
        P.q[bones] = q if w >= 1.0 else bm.qslerp(P.q[bones], q, w)

    @staticmethod
    def _pose_spec(p):
        if isinstance(p, str):
            if p not in HAND_POSES:
                raise ValueError("hand pose must be one of %s, got %r" % (tuple(HAND_POSES), p))
            return HAND_POSES[p]
        return p

    def _hand_end(self, P, side, end):
        """Where the palm centre, fingertips or wrist of a pose are (body frame)."""
        D, Pj, A = self.local_fk(P)
        i = self.i
        w = i["wrist." + side]
        if end == "wrist":
            return Pj[w]
        if end == "fingertips":
            tip = i["finger3-3." + side]
            return Pj[tip] + bm.qrot(D[tip], self.rig.tail[tip] - self.rig.head[tip])
        m3 = i["finger3-1." + side]
        n = bm.qrot(A[w], self.rig.palm_n[side])
        return 0.4 * Pj[w] + 0.6 * Pj[m3] + n * 0.012 * self.k

    def arm_reach(self, P, side, target, end="palm", **kw):
        """Bends one arm so that the palm centre (or the fingertips, or the wrist) is on `target`."""
        tgt = np.asarray(target, np.float64)
        goal = tgt.copy()
        if end != "wrist":
            # a first guess: the wrist stops a hand's length short
            goal = tgt - (self._hand_end(P, side, end) - self._hand_end(P, side, "wrist"))
        for _ in range(3):
            self.arm_to(P, side, goal, **kw)
            if end == "wrist":
                break
            goal = goal + (tgt - self._hand_end(P, side, end))

    def _palm_dir(self, P, side, palm):
        sg = 1.0 if side == "L" else -1.0
        if isinstance(palm, str):
            d = dict(_PALM, **{"in": (-sg, 0.15, 0.0), "out": (sg, 0.0, 0.0)})[palm]
        else:
            d = palm
        return bm.qrot(P.rot, np.asarray(d, np.float64))

    def _look_to(self, P, w, target, limit=45.0):
        """Turns the head toward a point (body frame), gently."""
        hd = self.rig.neutral_pos[self.i["head"]] + P.pos
        d = np.asarray(target, np.float64) - hd
        turn = np.degrees(np.arctan2(d[0], max(d[2], 0.05)))
        up = np.degrees(np.arctan2(d[1], max(np.hypot(d[0], d[2]), 0.05)))
        self._head(P, w, up=float(np.clip(up, -40, 35)) * 0.7, turn=float(np.clip(turn, -limit, limit)) * 0.8)

    def stoop(self, P, a):
        """An elder's posture on top of any pose: a (0..1)."""
        for b in ("spine05", "spine04", "spine03", "spine02"):
            self._add(P, b, bm.qx(5.5 * DEG * a))
        self._add(P, "spine01", bm.qx(4.0 * DEG * a))
        for b in ("neck01", "neck02", "neck03"):
            self._add(P, b, bm.qx(-1.5 * DEG * a))
        self._add(P, "head", bm.qx(-9.0 * DEG * a))
        for s, sg in (("L", 1.0), ("R", -1.0)):
            self._add(P, "clavicle." + s, bm.qy(-sg * 7 * DEG * a))
            self._add(P, "upperleg01." + s, bm.qx(-7.0 * DEG * a))
            self._add(P, "lowerleg01." + s, bm.qx(13.0 * DEG * a))
            self._add(P, "foot." + s, bm.qx(-6.0 * DEG * a))
            self._add(P, "lowerarm01." + s, bm.qx(-8.0 * DEG * a))

    # ------------------------------------------------------------------ gestures
    def g_touch(self, P, w, t, age=0.0, side="R", to=None, end="palm", palm="down", fingers="open", look=True,
                wrist=-6.0, pole=None, lean=1.0, **kw):
        sg = 1.0 if side == "L" else -1.0
        _, Pj, _ = self.local_fk(P)
        S = Pj[self.i["upperarm01." + side]]
        L = sum(self.arm_len[side])
        if to is None:
            to = S + bm.qrot(P.rot, np.array([-sg * 0.06, -0.10, 0.48]) * self.k)
        to = np.asarray(to, np.float64)
        d = to - S
        far = np.linalg.norm(d) / max(L, 1e-6)
        fwd = float(np.clip((far - 0.85) * 55.0, 0.0, 40.0)) * (1.0 if d[2] > 0 else 0.0)
        low = float(np.clip((self.rig.hip_height + P.pos[1] - to[1]) * 60.0, 0.0, 45.0)) * (1.0 if d[2] > -0.1 else 0.0)
        tw = float(np.clip(np.degrees(np.arctan2(d[0], max(abs(d[2]), 0.2))) * 0.25, -20, 20))
        self._lean(P, w * lean, fwd=max(fwd, low), twist=tw - sg * 4.0)
        self._add(P, "clavicle." + side, bm.qy(-sg * 8 * DEG * w))
        if look:
            self._look_to(P, w, to)
        self.arm_reach(P, side, to, end=end, palm=self._palm_dir(P, side, palm), w=w, wrist=wrist, pole=pole)
        self.hand_pose(P, side, fingers, w=w)

    def g_hand_on_shoulder(self, P, w, t, age=0.0, side="R", to=None, **kw):
        sg = 1.0 if side == "L" else -1.0
        if to is None:
            _, Pj, _ = self.local_fk(P)
            to = Pj[self.i["upperarm01." + side]] + bm.qrot(P.rot, np.array([-sg * 0.10, 0.02, 0.42]) * self.k)
        self.g_touch(P, w, t, age, side=side, to=to, end="palm", palm="down", fingers=("open", "relaxed", 0.6),
                     wrist=-12.0, **kw)

    def g_handshake(self, P, w, t, age=0.0, side="R", to=None, grip=0.0, **kw):
        sg = 1.0 if side == "L" else -1.0
        if to is None:
            _, Pj, _ = self.local_fk(P)
            to = Pj[self.i["upperarm01." + side]] + bm.qrot(P.rot, np.array([-sg * 0.11, -0.27, 0.46]) * self.k)
        self.g_touch(P, w, t, age, side=side, to=to, end="palm", palm="in", fingers=("offer", "hold", float(grip)),
                     wrist=-4.0, **kw)

    def g_high_five(self, P, w, t, age=0.0, side="R", to=None, **kw):
        sg = 1.0 if side == "L" else -1.0
        if to is None:
            _, Pj, _ = self.local_fk(P)
            to = Pj[self.i["upperarm01." + side]] + bm.qrot(P.rot, np.array([-sg * 0.04, 0.24, 0.40]) * self.k)
        self.g_touch(P, w, t, age, side=side, to=to, end="palm", palm="fwd", fingers="spread", wrist=-30.0,
                     pole=bm.qrot(P.rot, [sg * 0.7, -1.0, 0.0]), **kw)

    def g_embrace(self, P, w, t, age=0.0, to=None, to2=None, head="L", **kw):
        """to: where the left hand goes, to2: the right hand (defaults: round someone standing close before)."""
        _, Pj, _ = self.local_fk(P)
        c = Pj[self.i["spine02"]]
        k = self.k
        tl = c + bm.qrot(P.rot, np.array([-0.10, 0.05, 0.40]) * k) if to is None else np.asarray(to, float)
        tr = c + bm.qrot(P.rot, np.array([0.11, -0.07, 0.40]) * k) if to2 is None else np.asarray(to2, float)
        self._lean(P, w, fwd=7.0)
        hs = 1.0 if head == "L" else -1.0
        self._head(P, w, up=-8.0, turn=hs * 24.0, tilt=-hs * 6.0)
        for sd, sg, tg in (("L", 1.0, tl), ("R", -1.0, tr)):
            self._add(P, "clavicle." + sd, bm.qy(-sg * 12 * DEG * w))
            self.arm_reach(P, sd, tg, end="palm", palm=bm.qrot(P.rot, [0.0, 0.0, -1.0]), w=w, wrist=-10.0,
                           pole=bm.qrot(P.rot, [sg * 1.0, -0.7, 0.2]))
            self.hand_pose(P, sd, ("open", "relaxed", 0.5), w=w)

    def g_arm_round(self, P, w, t, age=0.0, side="L", to=None, **kw):
        sg = 1.0 if side == "L" else -1.0
        if to is None:
            _, Pj, _ = self.local_fk(P)
            to = Pj[self.i["upperarm01." + side]] + bm.qrot(P.rot, np.array([sg * 0.26, -0.30, 0.10]) * self.k)
        self._lean(P, w, side=-sg * 4.0)
        self._head(P, w, up=-10.0, turn=sg * 22.0)
        self.arm_reach(P, side, to, end="palm", palm=self._palm_dir(P, side, "in"), w=w, wrist=-8.0,
                       pole=bm.qrot(P.rot, [sg * 0.6, -0.3, -1.0]))
        self.hand_pose(P, side, ("open", "relaxed", 0.6), w=w)

    def g_cup(self, P, w, t, age=0.0, height=0.0, out=0.0, **kw):
        """Both hands together, palms up, cupped. height: metres above the waist; out: metres further forward."""
        _, Pj, _ = self.local_fk(P)
        c = Pj[self.i["spine03"]]
        k = self.k
        self._lean(P, w, fwd=4.0)
        self._head(P, w, up=-14.0)
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            tg = c + bm.qrot(P.rot, np.array([sg * 0.050, 0.02 + height, 0.25 + out]) * k)
            self._add(P, "clavicle." + sd, bm.qy(-sg * 6 * DEG * w))
            self.arm_reach(P, sd, tg, end="palm", palm=bm.qrot(P.rot, [-sg * 0.38, 1.0, 0.0]), w=w, wrist=4.0,
                           pole=bm.qrot(P.rot, [sg * 0.6, -1.0, -0.3]))
            self.hand_pose(P, sd, "cup", w=w)

    def g_offer(self, P, w, t, age=0.0, side="R", **kw):
        self.g_reach(P, w, t, age, side=side, palm="up", far=0.66, height=-0.14, lead=0.0, **kw)

    def g_listen(self, P, w, t, age=0.0, side="L", amount=1.0, **kw):
        sg = 1.0 if side == "L" else -1.0
        self._lean(P, w * amount, fwd=7.0, side=-sg * 3.0)
        self._head(P, w * amount, up=-4.0, turn=sg * 22.0, tilt=-sg * 11.0)

    def g_raise_hand(self, P, w, t, age=0.0, side="R", to=None, palm="fwd", fingers="open", **kw):
        sg = 1.0 if side == "L" else -1.0
        _, Pj, _ = self.local_fk(P)
        if to is None:
            hd = Pj[self.i["head"]]
            to = hd + bm.qrot(P.rot, np.array([sg * 0.17, 0.46, 0.05]) * self.k)
        self._add(P, "clavicle." + side, bm.qz(sg * 16 * DEG * w))
        self._head(P, w, up=10.0)
        self.arm_reach(P, side, to, end="palm", palm=self._palm_dir(P, side, palm), w=w, wrist=-6.0,
                       pole=bm.qrot(P.rot, [sg * 1.0, -0.4, -0.1]))
        self.hand_pose(P, side, fingers, w=w)

    def g_clap(self, P, w, t, age=0.0, period=0.5, height=0.0, width=0.26, **kw):
        """Hands meet at the start of the gesture and then every `period` seconds."""
        _, Pj, _ = self.local_fk(P)
        k = self.k
        c = Pj[self.i["spine02"]] * (1 - height) + (Pj[self.i["head"]] + bm.qrot(P.rot, [0.0, 0.34 * k, 0.0])) * height
        ph = (age / max(period, 1e-3)) % 1.0
        gap = width * (0.5 - 0.5 * np.cos(2 * np.pi * ph)) ** 0.7
        self._head(P, w, up=8.0 * height)
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            tg = c + bm.qrot(P.rot, np.array([sg * (0.010 + 0.5 * gap), 0.04, 0.27 - 0.1 * height]) * k)
            self._add(P, "clavicle." + sd, bm.qz(sg * 14 * DEG * w * height))
            self.arm_reach(P, sd, tg, end="palm", palm=bm.qrot(P.rot, [-sg, 0.0, 0.0]), w=w, wrist=-18.0,
                           pole=bm.qrot(P.rot, [sg * 0.9, -0.8 + 0.6 * height, -0.1]))
            self.hand_pose(P, sd, "flat", w=w)

    def g_throw(self, P, w, t, age=0.0, side="R", lead=0.6, **kw):
        sg = 1.0 if side == "L" else -1.0
        _, Pj, _ = self.local_fk(P)
        S = Pj[self.i["upperarm01." + side]]
        k = self.k
        back = np.array([sg * 0.24, 0.10, -0.26]) * k
        top = np.array([-sg * 0.04, 0.26, 0.52]) * k
        down = np.array([-sg * 0.16, -0.28, 0.44]) * k
        u2 = float(bm.ramp(age, lead - 0.05, lead + 0.22))
        u3 = float(bm.ramp(age, lead + 0.22, lead + 0.9))
        off = back * (1 - u2) + top * u2
        off = off * (1 - u3) + down * u3
        self._lean(P, w, fwd=-4.0 + 16.0 * u2, twist=sg * 22.0 * (1 - u2) - sg * 14.0 * u2)
        self.arm_reach(P, side, S + bm.qrot(P.rot, off), end="palm", palm=self._palm_dir(P, side, "fwd"), w=w,
                       wrist=-25.0 + 35.0 * u2, pole=bm.qrot(P.rot, [sg * 0.8, -0.6, -0.4]))
        self.hand_pose(P, side, ("hold", "open", u2), w=w)

    def g_wave(self, P, w, t, age=0.0, side="R", **kw):
        sg = 1.0 if side == "L" else -1.0
        _, Pj, _ = self.local_fk(P)
        hd = Pj[self.i["head"]]
        sw = 0.085 * np.sin(2 * np.pi * age / 0.62)
        to = hd + bm.qrot(P.rot, np.array([sg * (0.30 + sw), 0.20, 0.12]) * self.k)
        self.g_raise_hand(P, w, t, age, side=side, to=to, palm="fwd", fingers="open")

    def g_brace(self, P, w, t, age=0.0, side="R", **kw):
        sg = 1.0 if side == "L" else -1.0
        _, Pj, _ = self.local_fk(P)
        hd = Pj[self.i["head"]]
        k = self.k
        self._lean(P, w, fwd=15.0, twist=sg * 8.0)
        self._head(P, w, up=-14.0, turn=-sg * 8.0)
        to = hd + bm.qrot(P.rot, np.array([-sg * 0.02, 0.10, 0.24]) * k)
        self.arm_reach(P, side, to, end="wrist", palm=self._palm_dir(P, side, "fwd"), w=w, wrist=-10.0,
                       pole=bm.qrot(P.rot, [sg * 1.0, -0.2, 0.3]))
        self.hand_pose(P, side, ("open", "relaxed", 0.5), w=w)
        other = "L" if side == "R" else "R"
        self.arm(P, other, flex=-12.0, abd=22.0, twist=-10.0, elbow=28.0, w=w)

    def g_hold_thread(self, P, w, t, age=0.0, side="R", to=None, **kw):
        sg = 1.0 if side == "L" else -1.0
        if to is None:
            _, Pj, _ = self.local_fk(P)
            to = Pj[self.i["spine04"]] + bm.qrot(P.rot, np.array([sg * 0.17, 0.10, 0.30]) * self.k)
        self.g_touch(P, w, t, age, side=side, to=to, end="wrist", palm="in", fingers="pinch", look=False, wrist=-8.0,
                     lean=0.0)

    # ------------------------------------------------------------------ motions
    def m_sit(self, t, age=0.0, seed=0.0, dur=2.2, bowed=1.0, **kw):
        """Sitting on the ground with the knees drawn up, arms round them, head bowed."""
        S = self.m_stand(t, age, seed=seed)
        rig = self.rig
        i = self.i
        k = self.k
        Q = self.identity()
        hips_low = float(rig.verts0[rig.bone_region[rig.vert_bone] == 6][:, 1].min())
        Q.pos = np.array([0.0, -(hips_low - 0.012 * k), -0.10 * k])
        Q.rot = bm.qx(-14.0 * DEG)
        for b in ("spine05", "spine04", "spine03", "spine02"):
            self._set(Q, b, bm.qx((9.0 + 5.0 * bowed) * DEG))
        self._set(Q, "spine01", bm.qx(6.0 * bowed * DEG))
        for b in ("neck01", "neck02", "neck03"):
            self._set(Q, b, bm.qx(4.0 * bowed * DEG))
        self._set(Q, "head", bm.qx((6.0 + 14.0 * bowed) * DEG))
        N = rig.neutral_pos
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            ankle = np.array([sg * 0.105 * k, N[i["foot." + sd]][1], 0.36 * k])
            self.leg_to(Q, sd, ankle, knee=np.array([sg * 0.25, 1.0, 0.35]), foot=bm.qy(sg * 8 * DEG))
        _, Pj, _ = self.local_fk(Q)
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            kn = Pj[i["lowerleg01." + sd]]
            an = Pj[i["foot." + sd]]
            tg = kn * 0.62 + an * 0.38 + np.array([sg * 0.035, 0.0, 0.07]) * k
            self.arm_reach(Q, sd, tg, end="palm", palm=np.array([-sg * 0.5, 0.0, -1.0]), wrist=-6.0,
                           pole=np.array([sg * 1.0, -0.6, 0.2]))
            self.hand_pose(Q, sd, "relaxed")
        Q.ground = 0.0
        from .motion import blend
        return blend(S, Q, float(bm.smoother(age / max(dur, 1e-3))))

    def m_shuffle(self, t, age=0.0, seed=0.0, rate=1.15, amount=0.42, **kw):
        """Small steps on the spot."""
        from .motion import blend
        S = self.m_stand(t, age, seed=seed)
        W = self.clip_pose("walk", max(age, 0.0) * rate + seed * 0.37)
        W.pos[0] = W.pos[2] = 0.0
        return blend(S, W, amount)
