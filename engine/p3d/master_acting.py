"""The masterpiece's own acting (engine/songs/master_peace.py): gentle key poses and eased curves written for the
nine acted moments, on top of BODY2's library (gestures.py, acting.py, pairs.py, crowd.py).

Anthony on v6: "The people movement and their expressions need to be much more refined." Every pose here keeps
the shoulders down, the elbows softly bent, the wrists and fingers relaxed; hands arrive gently; nothing locks
straight; nothing snaps. Importing this module registers the gestures and crowd kinds below with the engine (by
name, like the library's own), so Body(gesture=[...]) and Crowd(kinds=...) take them.

GESTURES
  comfort      a hand laid gently on someone's shoulder or upper back (side, to: a world point or function),
               the arm rounded (the elbow out and down), the body leaning in, the head bowed toward them
  look_to      the head lifts and turns toward a point (to), a little tilt: someone looking up at a friend
  lap          both hands resting on the thighs (kneeling or seated), soft
  dance        a dancer's arms (port de bras): from low and rounded, through a rounded first position, opening
               into a wide soft arc, rising into a high rounded V; the chest lifts and the face rises
               (lead: seconds the right arm leads; tempo)
  sway         a slow weight shift from side to side with the head following (period, amount)
  soft_clap    applause with soft elbows, the hands meeting before the chest (period, height, phase)
  soft_raise   one arm raised in joy, elbow soft, the open hand swaying a little (side, period)
  joy          both arms raised in a soft rounded V, hands open, the chest lifted (a cheer without stiffness)
  greet_bow    a slight, warm bow: the head and shoulders dip and come back up, the hands relaxed at the sides
               (amount, hold: seconds held low)

CROWD KINDS (crowd.KINDS): "joy_clap", "joy_raise", "joy_up", "joy_heart": the crowd round the dancer, each
person swaying, clapping or raising their hands at their own tempo.
"""
import numpy as np

from . import actor as _act
from . import bodymath as bm
from . import crowd as _crowd
from . import gestures as _g
from . import motion as _mo

DEG = np.pi / 180.0


def _ease(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0)


# ------------------------------------------------------------------------------------------------------ gestures
def g_comfort(self, P, w, t, age=0.0, side="R", to=None, lean=10.0, bow=10.0, stroke=0.012, **kw):
    sg = 1.0 if side == "L" else -1.0
    k = self.k
    _, Pj, _ = self.local_fk(P)
    S = Pj[self.i["upperarm01." + side]]
    if to is None:
        to = S + bm.qrot(P.rot, np.array([-sg * 0.10, -0.05, 0.36]) * k)
    to = np.asarray(to, np.float64)
    # a tender stroke: the hand moves a centimetre or so, slowly, as it rests
    to = to + bm.qrot(P.rot, np.array([0.0, stroke * np.sin(2 * np.pi * age / 2.6), 0.0]) * k)
    d = to - S
    d_body = bm.qrot(bm.qconj(P.rot), d)
    turn = float(np.clip(np.degrees(np.arctan2(d_body[0], max(abs(d_body[2]), 0.15))), -40.0, 40.0))
    self._lean(P, w, fwd=lean, twist=turn * 0.35, side=-np.sign(turn) * 2.5)
    # shoulders down: the clavicle only follows the reach a little
    self._add(P, "clavicle." + side, bm.qy(-sg * 5 * DEG * w))
    self._look_to(P, w * 0.85, to + np.array([0.0, 0.10 * k, 0.0]))
    self._head(P, w, up=-bow, tilt=-np.sign(turn) * 6.0)
    # the hand travels on a soft low arc from where it rests to the shoulder (never a straight arm thrust out):
    # it lifts close to the body, comes forward with the elbow bent and settles from just above
    start = self._hand_end(P, side, "palm")
    p = float(np.clip(w, 0.0, 1.1))
    e = p * p * (3.0 - 2.0 * p) if p < 1.0 else p
    near = 0.5 * (start + S) + bm.qrot(P.rot, np.array([0.0, -0.05, 0.12]) * k)
    mid = 0.5 * (near + to) + np.array([0.0, 0.05 * k, 0.0])
    if e < 0.5:
        u = e / 0.5
        tgt = (1 - u) ** 2 * start + 2 * (1 - u) * u * near + u * u * mid
    else:
        u = (e - 0.5) / 0.5
        tgt = (1 - u) ** 2 * mid + 2 * (1 - u) * u * (to + np.array([0.0, 0.04 * k, 0.0])) + u * u * to
    pole = bm.qrot(P.rot, [sg * 0.85, -0.75, -0.25])
    self.arm_reach(P, side, tgt, end="palm", palm=bm.qrot(P.rot, [sg * 0.15, -1.0, -0.15]),
                   w=float(np.clip(w / 0.25, 0.0, 1.0)), wrist=-4.0, pole=pole)
    self.hand_pose(P, side, ("open", "relaxed", 0.75), w=w)


def g_look_to(self, P, w, t, age=0.0, to=None, up=0.0, tilt=8.0, **kw):
    if to is None:
        self._head(P, w, up=up + 8.0, tilt=tilt)
        return
    _, Pj, _ = self.local_fk(P)
    d = np.asarray(to, np.float64) - Pj[self.i["head"]]
    d_body = bm.qrot(bm.qconj(P.rot), d)
    turn = float(np.clip(np.degrees(np.arctan2(d_body[0], max(d_body[2], 0.05))), -70, 70))
    self._lean(P, w, fwd=-2.0, twist=turn * 0.3)
    self._look_to(P, w, to, limit=65.0)
    self._head(P, w, up=up, tilt=-np.sign(turn) * tilt)


def g_lap(self, P, w, t, age=0.0, **kw):
    _, Pj, _ = self.local_fk(P)
    i = self.i
    for sd, sg in (("L", 1.0), ("R", -1.0)):
        kn = Pj[i["lowerleg01." + sd]]
        hp = Pj[i["upperleg01." + sd]]
        c = hp + (kn - hp) * 0.55 + bm.qrot(P.rot, np.array([-sg * 0.015, 0.07, 0.02]) * self.k)
        self.arm_reach(P, sd, c, end="palm", palm=(kn - hp) * 0.3 + np.array([0.0, -1.0, 0.0]), w=w, wrist=-4.0,
                       pole=bm.qrot(P.rot, [sg * 0.7, -1.0, -0.5]))
        self.hand_pose(P, sd, "relaxed", w=w)


# a dancer's arms: (seconds, (flex, abd, twist, elbow, sup, wrist)) for the left arm; the right mirrors it
DANCE = [
    (0.00, (2.0, 8.0, -8.0, 14.0, 0.0, 5.0)),          # at rest
    (0.55, (14.0, 16.0, 22.0, 34.0, 30.0, 2.0)),       # bras bas: low and rounded
    (1.15, (52.0, 24.0, 32.0, 50.0, 40.0, -6.0)),      # first: rounded before the waist
    (1.90, (28.0, 60.0, 44.0, 36.0, 44.0, 4.0)),       # opening into a wide soft arc, below the shoulders
    (2.70, (30.0, 110.0, 60.0, 40.0, 50.0, 3.0)),      # rising into a high rounded V, the wrists soft
]


def _dance_angles(a, sway=0.0):
    ts = [k[0] for k in DANCE]
    if a <= 0.0:
        return np.array(DANCE[0][1])
    if a >= ts[-1]:
        return np.array(DANCE[-1][1]) + np.array([2.0, 3.0, 0.0, 3.0, 0.0, 0.0]) * sway
    j = int(np.searchsorted(ts, a, side="right") - 1)
    u = _ease((a - ts[j]) / (ts[j + 1] - ts[j]))
    return np.array(DANCE[j][1]) * (1 - u) + np.array(DANCE[j + 1][1]) * u


def g_dance(self, P, w, t, age=0.0, lead=0.14, tempo=1.0, lift=1.0, **kw):
    a = max(age, 0.0) * tempo
    rise = _ease((a - 1.4) / 1.3) * lift
    self._lean(P, w, fwd=-5.0 * rise, side=2.0 * np.sin(2 * np.pi * age / 3.2) * rise)
    self._head(P, w, up=4.0 + 14.0 * rise, tilt=4.0 * np.sin(2 * np.pi * age / 3.2 + 0.6))
    for sd, sg, dl in (("L", 1.0, 0.0), ("R", -1.0, lead)):
        sw = np.sin(2 * np.pi * (age - dl) / 2.9 + sg)
        f, ab, tw, el, sp, wr = _dance_angles(a - dl, sway=sw)
        self.arm(P, sd, flex=f, abd=ab, twist=tw, elbow=el, sup=sp, wrist=wr, w=w)
        self._add(P, "clavicle." + sd, bm.qz(sg * 6 * DEG * w * rise))
        self.hand_pose(P, sd, ("relaxed", "open", 0.45 + 0.2 * _ease(a / 1.2)), w=w)


def g_sway(self, P, w, t, age=0.0, period=3.0, amount=3.0, phase=0.0, **kw):
    s = np.sin(2 * np.pi * (age / max(period, 0.3) + phase))
    self._lean(P, w, side=amount * s, twist=amount * 0.6 * np.sin(2 * np.pi * (age / period + phase) - 0.6))
    self._head(P, w, tilt=-amount * 0.8 * s, turn=amount * 0.5 * s)


def g_soft_clap(self, P, w, t, age=0.0, period=0.55, height=0.25, phase=0.0, **kw):
    _, Pj, _ = self.local_fk(P)
    k = self.k
    c = Pj[self.i["spine02"]] * (1 - height) + (Pj[self.i["head"]]) * height
    ph = (age / max(period, 1e-3) + phase) % 1.0
    gap = 0.20 * (0.5 - 0.5 * np.cos(2 * np.pi * ph)) ** 0.8
    self._lean(P, w, fwd=3.0, side=2.0 * np.sin(2 * np.pi * age / (period * 4.0)))
    self._head(P, w, up=6.0 + 4.0 * height, tilt=3.0 * np.sin(2 * np.pi * age / (period * 4.0)))
    for sd, sg in (("L", 1.0), ("R", -1.0)):
        tg = c + bm.qrot(P.rot, np.array([sg * (0.012 + 0.5 * gap), 0.03, 0.25]) * k)
        self.arm_reach(P, sd, tg, end="palm", palm=bm.qrot(P.rot, [-sg, 0.15, 0.2]), w=w, wrist=-10.0,
                       pole=bm.qrot(P.rot, [sg * 0.9, -1.0, -0.2]))
        self.hand_pose(P, sd, ("flat", "relaxed", 0.4), w=w)


def g_soft_raise(self, P, w, t, age=0.0, side="R", period=1.4, **kw):
    sg = 1.0 if side == "L" else -1.0
    _, Pj, _ = self.local_fk(P)
    hd = Pj[self.i["head"]]
    k = self.k
    sw = 0.08 * np.sin(2 * np.pi * age / max(period, 0.3))
    to = hd + bm.qrot(P.rot, np.array([sg * (0.24 + sw), 0.30, 0.10]) * k)
    self._lean(P, w, fwd=-2.0, side=-sg * 3.0)
    self._head(P, w, up=10.0, tilt=sg * 3.0)
    self._add(P, "clavicle." + side, bm.qz(sg * 10 * DEG * w))
    self.arm_reach(P, side, to, end="palm", palm=bm.qrot(P.rot, [sg * 0.2, 0.1, 1.0]), w=w, wrist=-12.0,
                   pole=bm.qrot(P.rot, [sg * 1.0, -0.5, -0.2]))
    self.hand_pose(P, side, ("open", "relaxed", 0.35), w=w)


def g_joy(self, P, w, t, age=0.0, period=2.4, **kw):
    s = np.sin(2 * np.pi * age / max(period, 0.3))
    self._lean(P, w, fwd=-4.0, side=2.0 * s)
    self._head(P, w, up=12.0, tilt=3.0 * s)
    for sd, sg in (("L", 1.0), ("R", -1.0)):
        self.arm(P, sd, flex=24.0, abd=112.0 + 4.0 * s * sg, twist=62.0, elbow=36.0 + 3.0 * s, sup=50.0, wrist=-10.0,
                 w=w)
        self._add(P, "clavicle." + sd, bm.qz(sg * 8 * DEG * w))
        self.hand_pose(P, sd, ("open", "relaxed", 0.3), w=w)


def g_greet_bow(self, P, w, t, age=0.0, amount=16.0, down=0.9, hold=0.7, up=1.0, **kw):
    """A slight warm bow that comes back up: down over `down` s, held `hold` s, back up to a small nod."""
    a = max(age, 0.0)
    b = _ease(a / down) * (1.0 - 0.7 * _ease((a - down - hold) / up))
    self._lean(P, w, fwd=amount * 0.55 * b)
    self._head(P, w, up=-amount * 0.75 * b - 3.0)
    for sd, sg in (("L", 1.0), ("R", -1.0)):
        # the hands relaxed at the sides, drifting a touch forward as the body bows
        self.arm(P, sd, flex=4.0 + 9.0 * b, abd=7.0, twist=-6.0, elbow=16.0 + 6.0 * b, sup=0.0, wrist=6.0, w=w)
        self.hand_pose(P, sd, "relaxed", w=w)


def m_rise_up(self, t, age=0.0, seed=0.0, dur=1.6, sit=0.85, **kw):
    """Up from sitting back on the heels to standing in one soft movement: the weight comes forward over the
    knees, then the hips rise and the legs unfold under the skirt (no step through one knee)."""
    from .motion import blend
    S = self.m_stand(t, age, seed=seed)
    K = self._kneel_pose(sit=sit, one=False)
    arms = [self.i[b] for b in self.rig.names if b.startswith(("clavicle", "shoulder", "upperarm", "lowerarm", "wrist",
                                                               "finger", "metacarpal"))]
    K.q[arms] = S.q[arms]
    u = float(np.clip(age / max(dur, 1e-3), 0.0, 1.0))
    p = _ease((u - 0.12) / 0.88)
    P = blend(K, S, p) if p > 0.0 else K.copy()
    lean = 16.0 * np.sin(np.pi * float(np.clip(u / 0.85, 0.0, 1.0))) ** 1.5
    self._lean(P, 1.0, fwd=lean)
    self._head(P, 1.0, up=-0.4 * lean)
    P.ground = 1.0
    return P


_NEW = dict(comfort=(g_comfort, (1.1, 0.9, 0.0, 0.02)), look_to=(g_look_to, (1.1, 1.0, 0.0, 0.02)),
            lap=(g_lap, (0.9, 0.9, 0.0, 0.0)), dance=(g_dance, (0.5, 1.1, 0.0, 0.0)),
            sway=(g_sway, (1.0, 1.0, 0.0, 0.0)), soft_clap=(g_soft_clap, (0.6, 0.8, 0.03, 0.02)),
            soft_raise=(g_soft_raise, (0.9, 0.9, 0.04, 0.03)), joy=(g_joy, (1.0, 1.0, 0.04, 0.03)),
            greet_bow=(g_greet_bow, (0.6, 1.0, 0.0, 0.0)))


def _register():
    for name, (fn, timing) in _NEW.items():
        setattr(_g.Library, "g_" + name, fn)
        if name not in _mo.GESTURES:
            _mo.GESTURES = tuple(_mo.GESTURES) + (name,)
        _act.TIMING[name] = timing
    setattr(_g.Library, "m_rise_up", m_rise_up)
    if "rise_up" not in _mo.MOTIONS:
        _mo.MOTIONS = tuple(_mo.MOTIONS) + ("rise_up",)
    K = _crowd.KINDS
    K.setdefault("joy_clap", dict(gest=[("soft_clap", dict(period=0.6, height=0.3)),
                                        ("sway", dict(period=2.4, amount=2.5), 0.2)], loop=2.4))
    K.setdefault("joy_raise", dict(gest=[("soft_raise", dict(side="R", period=1.2)),
                                         ("sway", dict(period=2.4, amount=3.0), 0.1)], loop=2.4))
    K.setdefault("joy_up", dict(gest=[("joy", dict(period=2.4)), ("sway", dict(period=2.4, amount=2.0))],
                                loop=2.4))
    K.setdefault("joy_heart", dict(gest=[("hand_on_heart", dict(side="R", bow=6.0)),
                                         ("soft_raise", dict(side="L", period=1.6), 0.4),
                                         ("sway", dict(period=3.2, amount=2.5))], loop=3.2))


_register()
