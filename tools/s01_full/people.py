"""Song 01, All You Stars of Zion, full backdrop: the people of light (lane PEOPLE).

Everything here is a pure function of song time t in seconds (0 is the first sample of the ensemble audio;
the picture runs on to 3:23 after the music ends at 3:08). The people use Claude Final v1's bodies
(commit f43f451, package nine_reference_p3d, exactly as tools/nine_colours_minor/respect.py does) in the
approved Revision 3 look: warm gold glitter, whole and radiant, no faces.

USE (from the lead's render module, after tools/nine_colours_minor/reference.py is importable)

    import people
    cast = people.build(people.Stage(at=(0.0, 0.0), view=0.0))
    def setup(scene):
        ...the world, titles, words...
        cast.add(scene)                       # every body and light of this file
    WORLD["lights"] += cast.lights()          # optional: the warm light of the torches on the shore

    cast.focus(t)       a world point the camera may look at (the middle of who is acting at t)
    cast.box(t)         (lo, hi) world corners round everyone visible at t (for framing)
    cast.flames(t)      (K, 3) world places of the burning flames at t, and (K,) their strengths
    people.TIMES        every landmark below, in song seconds (change them here, not in the code)

THE STAGE (Stage)
    at      (x, z) on the lake plane in world metres: the middle of the shore line where the people stand
    view    azimuth in degrees from the stage toward the camera (0: the camera is at +z). The shore runs
            across the picture; "out on the lake" is away from the camera; Heavenly Mother's rise is at the
            far right of the picture
    y       height of the shore above the lake (default 0: the shore is at the water line)
    scale   size of everything (1 is life size; distances, bodies, torches and rings all grow with it)
    Local coordinates used below: x metres to the picture's right, z metres toward the camera.

THE MOMENTS (approved timeline)
    0:25.5 to 0:38   stars fall onto the shore and unfold into 16 young people of light
    0:38 to 0:55     COMPLIMENT, two young women: one has long served (water poured on a young tree of light,
                     two more already planted), she rises and straightens, tired; the other turns to her with
                     an open hand; both hearts glow. Nothing rises above shoulder height (words 0:42 to 0:52)
    0:58 to 1:24     torches appear; a flame passes hand to hand from Heavenly Mother (on a rise at the far
                     right, only ever seen from behind) along the line; at 1:17 the torches lift
    1:24 to 1:27     the torches steady and brighten as light falls on them
    1:27 to 1:53     they walk out on the lake into a wide arc (open toward the camera), a ring at every step
    2:20 to 2:35     they walk back to the shore (a lane choice; TIMES["back"]; set it past 3:23 to stay out)
    2:36 to 2:57     ENCOURAGEMENT, two young men: one kneels, the other lays a hand on his back, then helps
                     him rise; their torches stand planted in the sand beside them
    2:57 to 3:08     each flame lifts as a spark and drifts up; the torches fade
    3:08 to 3:23     they stand quietly along the shore, gently alive

COST. Cloth is simulated from each body's start, so every person is made of a few bodies joined at still
moments (SEGMENTS); a still or a render chunk anywhere in the song warms up in under a minute.
"""
import numpy as np

import reference  # noqa: F401  (registers nine_reference_p3d, Claude Final v1's body modules)
from nine_reference_p3d import actor as act
from nine_reference_p3d import assets
from nine_reference_p3d.body import Body
from p3d.api import lin

# ------------------------------------------------------------------------------------------- the timeline
TIMES = dict(
    land=25.5, land_last=31.2,        # the first and last star touch the shore
    comp=38.0, comp_words=(42.0, 52.0), comp_end=55.0,
    torch_in=56.6,                     # unlit torches gather in every right hand
    mother=(57.0, 89.0),               # Heavenly Mother on her rise
    first_flame=59.2,                  # her light reaches the first torch
    pass_gap=1.05,                     # seconds from one torch to the next
    lift=77.0,                         # the torches lift (staggered from the middle out)
    steady=84.0, bright=(84.0, 87.0),  # steady, then brighter as light falls on them
    lower=87.2,                        # back to chest height to walk
    walk=87.4, walk_end=113.0,         # out on the lake
    back=136.0,                        # back to the shore (all arrive by about 2:30)
    enc=156.0, enc_words=(161.0, 172.0), enc_rise=166.0, enc_end=177.0,
    sparks=177.0, sparks_end=188.0,
    quiet=188.0, end=203.0,
)
SEGMENTS = (25.0, 56.0, 86.6, 121.0, 151.5, 178.0, 205.0)   # still moments where a person's body is renewed
JOIN = 0.6                                                   # cross-fade seconds at a join

N = 16
SHORE_X = np.linspace(-5.4, 5.0, N)
COMP_A, COMP_B = 7, 9                 # the Compliment pair (young women)
ENC_K, ENC_H = 8, 6                   # the Encouragement pair (young men): K kneels, H helps
SHAPES = ["woman", "man", "woman", "man", "woman", "man", "man", "woman", "man", "woman",
          "man", "woman", "man", "woman", "man", "woman"]
HAIR = dict(woman=("bun", "tied", "bob", "long", "covered"), man=("short", "cap"))
GOLDS = [("#ffc664", "#fff0c8"), ("#f2a640", "#ffdc96"), ("#ffd27a", "#fff4d6"), ("#f6b552", "#ffe6b0")]
LOOK = dict(name="glitter", seams=0.6)
FLAME = "#ffb45a"
FLAME2 = "#fff0c8"


def _ss(a, b, x):
    if b <= a:
        return float(x >= a)
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def _dir(deg):
    a = np.radians(deg)
    return np.array([np.sin(a), 0.0, np.cos(a)])


class Stage:
    """Where the people stand in the lead's world (see the module text)."""

    def __init__(self, at=(0.0, 0.0), view=0.0, y=0.0, scale=1.0):
        self.c = np.array([float(at[0]), float(y), float(at[1])])
        self.view, self.scale = float(view), float(scale)
        self.cam = _dir(self.view)
        self.right = np.array([np.cos(np.radians(view)), 0.0, -np.sin(np.radians(view))])

    def point(self, x=0.0, y=0.0, z=0.0):
        s = self.scale
        return self.c + self.right * x * s + self.cam * z * s + np.array([0.0, y * s, 0.0])

    def place(self, x=0.0, z=0.0, y=0.0):
        p = self.point(x, y, z)
        return (float(p[0]), float(p[1]), float(p[2]))

    def face(self, local):
        """World facing for a local one: 0 toward the camera, 90 the picture's right, 180 away."""
        return self.view + float(local)

    def local(self, p):
        d = (np.asarray(p, np.float64) - self.c) / self.scale
        return float(d @ self.right), float(d[1]), float(d @ self.cam)


# ------------------------------------------------------------------------------------------------ a person
class Person:
    """One young person for the whole song: the same keys, made of a body per segment."""

    def __init__(self, cast, i, stage, shape, place, keys):
        self.cast, self.i, self.st, self.shape = cast, i, stage, shape
        self.home = place
        self.keys = keys                     # dict(motion=[...], gesture=[...], facing=[...], walks=[...])
        self.bodies = []                     # (t0, t1, Body)
        self.proxies = []                    # (t0, t1, Actor): the same person without gestures (for aiming)

    def body(self, t):
        """The body that draws this person at t (the later one inside a join)."""
        for t0, t1, b in self.bodies:
            if t < t1 - JOIN * 0.5:
                return b
        return self.bodies[-1][2]

    def where(self, t, name, raw=True):
        return self.body(t).where(t, name, raw=raw)

    def aim(self, t, name, normal=False):
        """Where a named place is without any gesture (what other gestures aim at: never recursive)."""
        px = self.proxies[-1][2]
        for t0, t1, a in self.proxies:
            if t < t1 - JOIN * 0.5:
                px = a
                break
        return px.where(t, name, normal, True)


def _seg_keys(keys, s0, s1):
    """Motion keys for a body that lives in [s0, s1]: the state at s0 stands from the start."""
    before = [k for k in keys if k[0] <= s0]
    inside = [k for k in keys if s0 < k[0] <= s1 + 2.0]
    out = []
    if before:
        k = before[-1]
        opts = dict(k[2]) if len(k) > 2 else {}
        if k[1] in ("kneel", "rise"):
            opts["dur"] = 0.01
        opts["blend"] = 0.01
        out.append((-1e9, k[1], opts))
    return out + inside


class Cast:
    def __init__(self, stage=None, n=N, points=9000, actor_points=22000, mother_points=30000, mound=True,
                 heavenly=True):
        self.st = stage or Stage()
        self.n = n
        self.points, self.apoints, self.mpoints = points, actor_points, mother_points
        self.T = dict(TIMES)
        self.mound = mound
        self.people = []
        self.extra = []                      # (name, point set)
        self._plan()
        self._build()
        self.mother = self._mother() if heavenly else None

    # ------------------------------------------------------------------ plan: where and when, in local metres
    def _plan(self):
        T = self.T
        rng = np.random.default_rng(11)
        n = self.n
        xs = np.linspace(-5.4, 5.0, n) if n != N else SHORE_X
        self.shore = []
        for i in range(n):
            z = 0.25 * np.sin(1.7 * i) + rng.uniform(-0.15, 0.15)
            self.shore.append((float(xs[i] + rng.uniform(-0.1, 0.1)), float(z)))
        a, b = COMP_A, COMP_B
        self.shore[a] = (-0.35, 0.95)        # in front of the line, beside her young trees
        self.shore[b] = (1.05, 0.80)
        self.shore[ENC_K] = (0.25, 0.20)
        self.shore[ENC_H] = (-0.45, 0.25)
        # landing order: from the middle outward, a little shuffled
        order = np.argsort(np.abs(np.array([p[0] for p in self.shore])) + rng.uniform(0, 1.6, n))
        self.land = np.zeros(n)
        for k, i in enumerate(order):
            self.land[i] = T["land"] + (T["land_last"] - T["land"]) * k / max(n - 1, 1)
        # the arc on the lake: open toward the camera
        ang = np.linspace(-62.0, 62.0, n)
        ox = np.array([p[0] for p in self.shore])
        rank = np.argsort(np.argsort(ox))
        self.arc = [(float(10.0 * np.sin(np.radians(ang[r]))), float(3.0 - 10.0 * np.cos(np.radians(ang[r]))))
                    for r in rank]
        # the flame passes from the right end (beside Mother) leftward
        self.light_order = list(np.argsort(-ox))
        self.lit = np.zeros(n)
        for k, i in enumerate(self.light_order):
            self.lit[i] = T["first_flame"] + T["pass_gap"] * k
        mid = np.abs(ox - ox.mean())
        self.lift_t = T["lift"] + 0.12 * np.argsort(np.argsort(mid))

    # ------------------------------------------------------------------ keys of one person
    def _keys(self, i):
        T, st = self.T, self.st
        rng = np.random.default_rng(100 + i)
        sx, sz = self.shore[i]
        ax, az = self.arc[i]
        motion = [(-1e9, "stand")]
        gesture = []
        face0 = float(np.clip(-sx * 4.0, -25, 25)) + rng.uniform(-12, 12)     # toward the camera, a little in
        facing = [(-1e9, face0)]
        # torch held at the chest from torch_in, raised at lift, lowered to walk
        hold = (T["torch_in"], T["enc"] - 3.0 if i in (ENC_K, ENC_H) else T["sparks"] + 1.0)
        gesture.append((hold[0], hold[1], "touch", dict(side="R", to=self._torch_hold(i), palm="in",
                                                        fingers="hold", ease=1.0)))
        gesture.append((self.lift_t[i], T["lower"] + 0.1 * rng.random(), "raise_hand", dict(side="R", ease=1.1)))
        # the receiver leans toward the giver's flame
        k = self.light_order.index(i)
        giver = self.light_order[k - 1] if k > 0 else None
        if giver is not None:
            g = giver
            gesture.append((self.lit[i] - 0.9, self.lit[i] + 0.5, "lean_in",
                            dict(to=lambda t, g=g: self.people[g].aim(t, "head"), ease=0.6)))
        # out on the lake: turn, walk, turn round to face the camera
        d = np.array([ax - sx, az - sz])
        dist = float(np.hypot(*d))
        head = float(np.degrees(np.arctan2(d[0], d[1])))
        speed = 0.7
        t_go = T["walk"] + 0.55 * abs(self.arc_rank(i) - (self.n - 1) / 2.0) / 1.0 + rng.uniform(0, 0.4)
        t_arr = t_go + dist / speed + 0.6
        face_lake = float(np.degrees(np.arctan2(-ax, 3.0 - az)))     # toward the arc's centre (the audience)
        facing += [(t_go - 1.2, face0), (t_go - 0.1, head), (t_arr - 0.4, head), (t_arr + 1.6, face_lake)]
        motion += [(t_go - 1.2, "shuffle"), (t_go, "walk", dict(speed=speed)), (t_arr, "stand", dict(blend=0.8))]
        walks = [(t_go, t_arr)]
        # back to the shore
        bx, bz = sx, sz
        d2 = np.array([bx - ax, bz - az])
        dist2 = float(np.hypot(*d2))
        head2 = float(np.degrees(np.arctan2(d2[0], d2[1])))
        t_go2 = T["back"] + 0.2 * abs(self.arc_rank(i) - (self.n - 1) / 2.0) + rng.uniform(0, 0.3)
        t_arr2 = t_go2 + dist2 / speed + 0.6
        face_end = face0
        if i == COMP_A:
            face_end = 25.0
        facing += [(t_go2 - 1.0, face_lake), (t_go2 - 0.1, head2), (t_arr2 - 0.4, head2), (t_arr2 + 1.6, face_end)]
        motion += [(t_go2 - 1.0, "shuffle"), (t_go2, "walk", dict(speed=speed)), (t_arr2, "stand", dict(blend=0.8))]
        walks.append((t_go2, t_arr2))
        # the flames rise: everyone watches them go
        tl = T["sparks"] + 0.45 * self.light_order.index(i) * 0.6
        gesture.append((tl + 0.3, T["quiet"] + 2.0 + rng.uniform(0, 2), "look_up", dict(amount=14.0)))
        # the quiet end: hands loosely joined before them, a small breath
        gesture.append((T["quiet"] + 1.0 + rng.uniform(0, 1.5), 1e9, "cup", dict(ease=1.6)))
        self._walk_end = getattr(self, "_walk_end", {})
        self._walk_end[i] = (t_arr, t_arr2)
        return dict(motion=motion, gesture=gesture, facing=facing, walks=walks, face0=face0)

    def arc_rank(self, i):
        ox = np.array([p[0] for p in self.shore])
        return int(np.argsort(np.argsort(ox))[i])

    def _torch_hold(self, i):
        """The right hand's place for a torch carried before the chest (follows the body as it turns)."""
        def to(t, i=i):
            p = self.people[i]
            c, n = p.aim(t, "chest", normal=True)
            n = np.array([n[0], 0.0, n[2]])
            n /= max(np.linalg.norm(n), 1e-6)
            r = np.cross(n, [0.0, 1.0, 0.0])                    # the body's left; its right is -r
            k = self.st.scale * p.k
            return c + (n * 0.30 - r * 0.12 + np.array([0.0, -0.16, 0.0])) * k
        return to

    # ------------------------------------------------------------------ the two acted moments
    def _compliment(self, keys, i):
        T = self.T
        if i == COMP_A:
            # she kneels by her third young tree, pours water from cupped hands, rises, straightens, tired
            keys["facing"] = [(-1e9, -62.0), (T["comp"] + 5.6, -62.0), (T["comp"] + 6.6, 35.0),
                              (T["comp_end"] + 0.5, 35.0), (T["comp_end"] + 2.0, keys["face0"])] + \
                keys["facing"][1:]
            keys["motion"] = [(-1e9, "stand"), (self.land[i] + 3.2, "kneel", dict(one=True, dur=1.6, hands="free")),
                              (T["comp"] + 3.0, "rise", dict(one=True, dur=2.2, blend=0.08)),
                              (T["comp"] + 5.4, "stand", dict(blend=0.6))] + keys["motion"][1:]
            keys["gesture"] = [(self.land[i] + 4.0, T["comp"] + 2.6, "cup", dict(ease=0.9)),
                               (T["comp"] + 4.6, T["comp"] + 6.4, "bow", dict(amount=14.0)),
                               (T["comp"] + 7.0, T["comp_end"] - 0.2, "hand_on_heart", dict(side="R", bow=5.0))] + \
                keys["gesture"]
        if i == COMP_B:
            ta = self.people_keys_place(COMP_A)
            keys["facing"] = [(-1e9, -55.0), (T["comp"] + 4.4, -55.0), (T["comp"] + 5.4, -75.0),
                              (T["comp_end"] + 0.5, -75.0), (T["comp_end"] + 2.0, keys["face0"])] + \
                keys["facing"][1:]
            keys["motion"] = [(-1e9, "stand"), (T["comp"] + 4.4, "shuffle"), (T["comp"] + 5.8, "stand")] + \
                keys["motion"][1:]
            keys["at"] = [(-1e9, self.shore[i]), (T["comp"] + 4.4, self.shore[i]),
                          (T["comp"] + 5.8, (ta[0] + 0.95, ta[1] - 0.05))]
            keys["gesture"] = [(T["comp"] + 0.5, T["comp"] + 4.6, "lean_in",
                                dict(to=lambda t: self.people[COMP_A].aim(t, "head"), ease=0.8)),
                               (T["comp"] + 5.8, T["comp_end"] - 0.4, "offer", dict(side="L", ease=1.0))] + \
                keys["gesture"]

    def people_keys_place(self, i):
        return self.shore[i]

    def _encouragement(self, keys, i):
        T = self.T
        turn = [(T["enc"] - 2.6, keys["face0"]), (T["enc"] - 1.2, 60.0 if i == ENC_K else 72.0),
                (T["enc_end"] - 0.2, 60.0 if i == ENC_K else 72.0), (T["enc_end"] + 1.4, keys["face0"])]
        if i in (ENC_K, ENC_H):
            keys["facing"] = sorted(keys["facing"] + turn, key=lambda k: k[0])
        if i == ENC_K:
            keys["motion"] = [k for k in keys["motion"] if k[0] < T["enc"] - 3.0] + \
                [(T["enc"] - 0.6, "kneel", dict(one=True, dur=1.8, hands="free", blend=0.05)),
                 (T["enc_rise"], "rise", dict(one=True, dur=2.0, blend=0.05)),
                 (T["enc_rise"] + 2.2, "stand", dict(blend=0.6))]
            keys["gesture"] += [(T["enc"] + 0.6, T["enc_rise"] - 0.6, "bow", dict(amount=16.0)),
                                (T["enc_rise"] - 1.2, T["enc_rise"] + 2.6, "handshake",
                                 dict(side="R", to=self._grip, grip=1.0, ease=0.7))]
        if i == ENC_H:
            keys["gesture"] += [(T["enc"] + 1.0, T["enc_end"] - 0.8, "hand_on_shoulder",
                                 dict(side="L", to=lambda t: self.people[ENC_K].aim(t, "blade.R"), ease=1.0)),
                                (T["enc"] + 1.6, T["enc_rise"] - 1.0, "bow", dict(amount=10.0)),
                                (T["enc_rise"] - 1.4, T["enc_rise"] + 2.6, "handshake",
                                 dict(side="R", to=self._grip, grip=1.0, ease=0.7))]

    def _grip(self, t):
        a = self.people[ENC_H].aim(t, "shoulder.R")
        b = self.people[ENC_K].aim(t, "shoulder.R")
        g = 0.5 * (a + b)
        g[1] = 0.5 * (a[1] + b[1]) - 0.36 * self.st.scale
        return g

    # ------------------------------------------------------------------ bodies
    def _build(self):
        st, T = self.st, self.T
        plans = []
        for i in range(self.n):
            keys = self._keys(i)
            keys.setdefault("at", [(-1e9, self.shore[i])])
            self._compliment(keys, i)
            self._encouragement(keys, i)
            plans.append(keys)
        for i, keys in enumerate(plans):
            self.people.append(Person(self, i, st, SHAPES[i % len(SHAPES)], self.shore[i], keys))
        for i, keys in enumerate(plans):
            self._bodies_of(i, keys)
        self._extras()

    def _style(self, i):
        shape = SHAPES[i % len(SHAPES)]
        rng = np.random.default_rng(300 + i)
        hairs = HAIR[shape]
        c, c2 = GOLDS[i % len(GOLDS)]
        acting = i in (COMP_A, COMP_B, ENC_K, ENC_H)
        d = dict(shape=shape, hair=hairs[i % len(hairs)], look=LOOK, color=c, color2=c2,
                 garment=("dress" if i % 3 else "robe") if shape == "woman" else ("tunic" if i % 2 else "coat"),
                 height=(1.52 + 0.1 * rng.random()) if shape == "woman" else (1.66 + 0.1 * rng.random()),
                 build=0.92 + 0.12 * rng.random(), bright=1.45, seed=20.0 + 1.37 * i,
                 points=self.apoints if acting else self.points, scale=self.st.scale,
                 wind=(0.25, 0.0, -0.15))
        if acting:
            d["detail"] = dict(hand=2)
        return d

    def _bodies_of(self, i, keys):
        st = self.st
        person = self.people[i]
        style = self._style(i)
        place = keys["at"]
        segs = list(SEGMENTS)
        segs[0] = self.land[i] - 0.4
        start_pt = None
        for k in range(len(segs) - 1):
            s0, s1 = segs[k], segs[k + 1]
            if k == 0:
                at = [(t, st.place(*p) if t > -1e8 else st.place(*p)) for t, p in place]
                at = [(t, (q[0], q[1], q[2])) for t, (q) in at]
                at_arg = at if len(at) > 1 else at[0][1]
            else:
                at_arg = start_pt
            fac = [(t, st.face(d)) for t, d in keys["facing"]]
            gest = [g for g in keys["gesture"] if g[1] > s0 - 2.0 and g[0] < s1 + 2.0]
            show = (s0 - (0 if k == 0 else JOIN * 0.5), s1 + JOIN * 0.5)
            effects = []
            if k == 0:
                effects.append(dict(kind="form", t=self.land[i], dur=2.6))
            rig = assets.Rig(style["shape"], style["height"], style["build"])
            person.k = rig.height / 1.6
            person.proxies.append((s0, s1, act.Actor(style["shape"], style["height"], at=at_arg, facing=fac,
                                                     motion=_seg_keys(keys["motion"], s0, s1), seed=style["seed"],
                                                     rig=rig, start=show[0])))
            b = Body(at=at_arg, facing=fac, motion=_seg_keys(keys["motion"], s0, s1), gesture=gest,
                     show=show, fade=(0.3 if k == 0 else JOIN * 0.5), effects=effects, **style)
            person.bodies.append((s0, s1, b))
            g = person.aim(s1 - 0.01, "ground")
            start_pt = (float(g[0]), float(st.c[1]), float(g[2]))

    def _mother(self):
        st, T = self.st, self.T
        p = st.place(7.9, -1.4, 0.55)
        b = Body("woman", height=1.86, at=p, facing=[(-1e9, st.face(205.0))], motion="stand",
                 garment="robe", veil=dict(length=1.5, wide=1.15), look=LOOK, color="#ffe3a6", color2="#fffaf0",
                 bright=1.7, points=self.mpoints, seed=77.0, scale=st.scale, show=T["mother"], fade=1.4,
                 wind=(0.2, 0.0, -0.1),
                 gesture=[(T["first_flame"] - 1.6, T["first_flame"] + 1.2, "offer", dict(side="R", ease=1.2)),
                          (T["lift"] + 0.8, T["mother"][1] - 1.0, "open_arms", dict(amount=0.35, ease=2.0))],
                 effects=[dict(kind="form", t=T["mother"][0] + 0.2, dur=2.0)])
        return b

    # ------------------------------------------------------------------ the lights, trees, rings and sparks
    def _extras(self):
        self.torches = [Torch(self, i) for i in range(self.n)]
        self.extra += [("people torch %d" % i, tc) for i, tc in enumerate(self.torches)]
        self.extra.append(("people stars", FallingStars(self)))
        self.extra.append(("people trees", Saplings(self)))
        self.extra.append(("people water", Water(self)))
        self.extra.append(("people hearts", Hearts(self)))
        self.extra.append(("people rings", StepRings(self)))
        self.extra.append(("people first light", FirstLight(self)))

    # ------------------------------------------------------------------ public
    def add(self, scene, prefix="people"):
        for i, p in enumerate(self.people):
            for k, (_a, _b, b) in enumerate(p.bodies):
                b.add(scene, "%s %02d %d" % (prefix, i, k))
        if self.mother is not None:
            self.mother.add(scene, prefix + " heavenly mother")
            if self.mound:
                scene.add(prefix + " rise", Mound(self))
        for name, ps in self.extra:
            scene.add(name if prefix == "people" else name.replace("people", prefix, 1), ps)

    def flames(self, t):
        ps, ks = [], []
        for tc in self.torches:
            f = tc.flame(t)
            if f is not None:
                ps.append(f[0])
                ks.append(f[1])
        if not ps:
            return np.zeros((0, 3)), np.zeros(0)
        return np.array(ps), np.array(ks)

    def lights(self, color=FLAME, radius=6.0):
        """One warm light at the middle of the burning flames (for the lead's WORLD["lights"])."""
        def pos(t):
            p, k = self.flames(t)
            if not len(k):
                return self.st.point(0, 1.6, 0)
            return (p * k[:, None]).sum(0) / max(k.sum(), 1e-6)

        def strength(t):
            p, k = self.flames(t)
            return float(min(k.sum() / 8.0, 1.0)) * 0.7
        return [dict(pos=pos, color=color, strength=strength, radius=radius * self.st.scale)]

    def visible(self, t):
        return [p for p in self.people if p.bodies[0][2].show[0] <= t]

    def focus(self, t):
        T = self.T
        if T["comp"] - 2 <= t <= T["comp_end"]:
            a, b = self.people[COMP_A].where(t, "chest"), self.people[COMP_B].where(t, "chest")
            return 0.5 * (a + b)
        if T["enc"] - 2 <= t <= T["enc_end"]:
            a, b = self.people[ENC_K].where(t, "chest"), self.people[ENC_H].where(t, "chest")
            return 0.5 * (a + b)
        lo, hi = self.box(t)
        return 0.5 * (lo + hi)

    def box(self, t):
        pts = [p.where(t, "crown") for p in self.visible(t)] + [p.where(t, "ground") for p in self.visible(t)]
        if not pts:
            return self.st.point(-6, 0, -1), self.st.point(6, 1.8, 1)
        pts = np.array(pts)
        return pts.min(0), pts.max(0)


# ------------------------------------------------------------------------------------------- point sets
def _fade(t, a, b, fin=0.4, fout=0.4):
    return _ss(a, a + fin, t) * (1.0 - _ss(b - fout, b, t))


class Torch:
    """A torch of light in a person's right hand: a slim staff and, once lit, a flame. Planted in the sand
    beside the Encouragement pair while they act; at the end its flame lifts away as a spark."""

    def __init__(self, cast, i):
        self.c, self.i = cast, i
        T = cast.T
        self.t_in = T["torch_in"] + 0.08 * i
        self.lit = cast.lit[i]
        self.planted = None
        if i in (ENC_K, ENC_H):
            self.planted = (T["enc"] - 3.2, 1e9)
        k = cast.light_order.index(i)
        self.t_up = T["sparks"] + 0.45 * k * 0.6
        rng = np.random.default_rng(500 + i)
        self.u = np.linspace(0.0, 1.0, 46)
        self.jit = rng.normal(0, 0.006, (46, 3))
        self.motes = rng.normal(0, 1, (18, 3)) * np.array([0.03, 0.05, 0.03])
        self.mph = rng.uniform(0, 2 * np.pi, 18)
        self.sway = rng.uniform(0, 6.28, 3)
        self.k = cast.st.scale
        self._plant_at = None

    def _hand(self, t):
        p = self.c.people[self.i]
        return p.body(t).where(t, "palm.R")

    def _plant(self):
        if self._plant_at is None:
            p = self.c.people[self.i]
            t = self.planted[0]
            g = p.aim(t, "ground")
            c, n = p.aim(t, "chest", normal=True)
            n = np.array([n[0], 0.0, n[2]])
            n /= max(np.linalg.norm(n), 1e-6)
            r = -np.cross(n, [0.0, 1.0, 0.0])
            side = -1.0 if self.i == ENC_H else 1.0
            self._plant_at = g + (r * 0.55 * side + n * 0.15) * self.k
        return self._plant_at

    def base(self, t):
        """(bottom, top) of the staff at t."""
        k = self.k
        up = np.array([0.0, 1.0, 0.0])
        hand = self._hand(t)
        held = (hand - up * 0.20 * k, hand + up * 0.34 * k)
        if self.planted is None:
            return held
        g = self._plant()
        planted = (g, g + up * 0.95 * k)
        a, b = self.planted
        u = _ss(a, a + 0.9, t) * (1.0 - _ss(b - 0.9, b, t))
        if u <= 0.0:
            return held
        if u >= 1.0:
            return planted
        arc = np.array([0.0, 0.12 * np.sin(np.pi * u), 0.0]) * k
        return (held[0] * (1 - u) + planted[0] * u + arc, held[1] * (1 - u) + planted[1] * u + arc)

    def flame(self, t):
        """(place, strength) of the flame on the torch, or None."""
        T = self.c.T
        if t < self.lit or t > self.t_up + 8.0:
            return None
        b0, b1 = self.base(t)
        g = _ss(self.lit, self.lit + 0.5, t)
        g *= 1.0 + 0.6 * _ss(T["bright"][0], T["bright"][1], t) * (1.0 - _ss(T["walk"] + 4.0, T["walk"] + 10.0, t))
        p = b1 + np.array([0.0, 0.05, 0.0]) * self.k
        if t > self.t_up:
            # the flame lifts as a spark and drifts up
            u = t - self.t_up
            rise = 0.55 * u + 0.09 * u * u
            p = p + np.array([0.25 * np.sin(0.8 * u + self.sway[0]) * min(u, 1.0), rise,
                              0.2 * np.sin(0.6 * u + self.sway[1]) * min(u, 1.0)]) * self.k
            g *= 1.0 - _ss(5.5, 8.0, u)
        return p, g

    def sample(self, t):
        T = self.c.T
        a = _fade(t, self.t_in, self.t_up + 3.5, 1.2, 2.0)
        if a <= 0.0:
            return []
        out = []
        b0, b1 = self.base(t)
        # the staff gathers from its foot upward, and fades after its flame has left
        grow = _ss(self.t_in, self.t_in + 1.4, t)
        u = self.u[self.u <= grow + 1e-6] if grow < 1 else self.u
        if len(u):
            pts = b0[None] * (1 - u[:, None]) + b1[None] * u[:, None] + self.jit[:len(u)] * self.k
            col = lin("#f6c26a") * (0.7 + 0.5 * u[:, None])
            out.append(dict(pos=pts, size=0.008 * self.k, color=col, alpha=0.75 * a, kind="spark", emit=1.6,
                            twinkle=0.6))
        f = self.flame(t)
        if f is not None:
            p, g = f
            fl = 0.88 + 0.12 * np.sin(t * 7.3 + self.i) * np.sin(t * 3.1 + 1.0)
            c = lin(FLAME)
            out.append(dict(pos=p[None], size=0.16 * self.k * min(g, 1.4), color=c * 0.9, alpha=0.55 * fl * min(g, 1.0),
                            kind="soft", backlight=0.3))
            out.append(dict(pos=p[None], size=0.035 * self.k, color=lin(FLAME2), alpha=min(g, 1.0), kind="spark",
                            emit=3.2 * fl * g))
            mo = p + self.motes * (1.0 + 0.3 * np.sin(t * 1.7 + self.mph))[:, None] * self.k + \
                np.stack([np.zeros(18), (0.04 + 0.06 * ((t * 0.9 + self.mph) % 1.0)) * self.k, np.zeros(18)], axis=1)
            out.append(dict(pos=mo, size=0.006 * self.k, color=c, alpha=0.7 * min(g, 1.0), kind="spark", twinkle=1.0,
                            emit=1.5))
        return out


class FirstLight:
    """The light that passes: from Heavenly Mother's hand to the first torch, then torch to torch."""

    def __init__(self, cast):
        self.c = cast

    def _src(self, k, t):
        c = self.c
        if k == 0:
            if c.mother is None:
                return c.st.point(8.0, 2.4, -1.4)
            return c.mother.where(t, "palm.R")
        prev = c.light_order[k - 1]
        f = c.torches[prev].flame(t)
        return f[0] if f is not None else c.torches[prev].base(t)[1]

    def sample(self, t):
        c = self.c
        out = []
        for k, i in enumerate(c.light_order):
            t1 = c.lit[i]
            t0 = t1 - (1.4 if k == 0 else 0.55)
            if not (t0 <= t <= t1 + 0.05):
                continue
            u = (t - t0) / (t1 - t0)
            u = u * u * (3 - 2 * u)
            a = self._src(k, t)
            b = c.torches[i].base(t)[1] + np.array([0.0, 0.05, 0.0]) * c.st.scale
            p = a * (1 - u) + b * u + np.array([0.0, (0.5 if k == 0 else 0.12) * np.sin(np.pi * u), 0.0]) * c.st.scale
            trail = np.array([a * (1 - v) + b * v + np.array([0.0, (0.5 if k == 0 else 0.12) * np.sin(np.pi * v), 0])
                              for v in np.linspace(max(u - 0.25, 0), u, 8)])
            out.append(dict(pos=p[None], size=0.05 * c.st.scale, color=lin(FLAME2), alpha=1.0, kind="spark", emit=3.0))
            out.append(dict(pos=trail, size=0.012 * c.st.scale, color=lin(FLAME), alpha=np.linspace(0.1, 0.8, 8),
                            kind="spark", emit=1.6))
        return out


class FallingStars:
    """Each person arrives as a star that falls to the shore, then unfolds (the body's own "form")."""

    def __init__(self, cast):
        self.c = cast
        rng = np.random.default_rng(9)
        self.off = rng.uniform(-1, 1, (cast.n, 2))

    def sample(self, t):
        c = self.c
        out = []
        for i in range(c.n):
            tl = c.land[i]
            if not (tl - 2.2 <= t <= tl + 1.6):
                continue
            g = c.st.point(*c.shore[i][:1], y=0.9, z=c.shore[i][1])
            top = g + (c.st.right * (2.5 + 1.5 * self.off[i, 0]) + c.st.cam * (-4.0 + self.off[i, 1])) * c.st.scale \
                + np.array([0, 9.0 * c.st.scale, 0])
            u = min(max((t - (tl - 2.2)) / 2.2, 0.0), 1.0)
            e = u * u * (3 - 2 * u)
            p = top * (1 - e) + g * e
            if t <= tl:
                vs = np.linspace(max(e - 0.16, 0), e, 12)
                trail = top[None] * (1 - vs[:, None]) + g[None] * vs[:, None]
                out.append(dict(pos=trail, size=0.02 * c.st.scale, color=lin("#fff4d8"),
                                alpha=np.linspace(0.05, 0.9, 12), kind="spark", emit=2.0))
                out.append(dict(pos=p[None], size=0.09 * c.st.scale, color=lin("#fff0c8"), alpha=1.0, kind="spark",
                                emit=3.5))
            else:
                a = 1.0 - _ss(tl, tl + 1.6, t)
                out.append(dict(pos=g[None], size=(0.09 + 0.25 * (1 - a)) * c.st.scale, color=lin("#ffe2a0"),
                                alpha=0.8 * a, kind="soft"))
        return out


class Saplings:
    """Three young trees of light beside the one who serves; the newest grows as she waters it."""

    def __init__(self, cast):
        self.c = cast
        st = cast.st
        ax, az = cast.shore[COMP_A]
        self.spots = [(ax - 1.75, az - 0.25, 0.62, 0.0), (ax - 1.2, az - 0.05, 0.5, 0.0),
                      (ax - 0.62, az + 0.18, 0.42, 1.0)]
        rng = np.random.default_rng(31)
        self.trees = []
        for sx, sz, h, grows in self.spots:
            base = st.point(sx, 0.0, sz)
            n_br = 5
            branches = []
            for b in range(n_br):
                y0 = 0.35 + 0.55 * b / n_br
                az_ = rng.uniform(0, 2 * np.pi)
                d = np.array([np.cos(az_), 0.9 + 0.4 * rng.random(), np.sin(az_)])
                d /= np.linalg.norm(d)
                branches.append((y0, d, 0.18 + 0.12 * rng.random()))
            leaves = rng.normal(0, 1, (90, 3)) * np.array([0.13, 0.09, 0.13])
            self.trees.append(dict(base=base, h=h, grows=grows, br=branches, leaves=leaves,
                                   lph=rng.uniform(0, 6.28, 90)))
        T = cast.T
        self.t_in = cast.land[COMP_A] + 1.0
        self.t_out = T["torch_in"] + 0.5
        self.g0, self.g1 = T["comp"] - 4.0, T["comp"] + 2.6

    def sample(self, t):
        a = _fade(t, self.t_in, self.t_out, 1.5, 1.5)
        if a <= 0:
            return []
        k = self.c.st.scale
        out = []
        for tr in self.trees:
            g = 1.0 if not tr["grows"] else 0.35 + 0.65 * _ss(self.g0, self.g1, t)
            h = tr["h"] * g * k
            up = np.array([0.0, 1.0, 0.0])
            sway = np.array([0.02 * np.sin(t * 0.9 + h * 10), 0, 0.015 * np.sin(t * 0.7)]) * k
            trunk = tr["base"][None] + up[None] * np.linspace(0, h, 24)[:, None] + \
                np.linspace(0, 1, 24)[:, None] ** 2 * sway[None]
            pts = [trunk]
            for y0, d, ln in tr["br"]:
                p0 = tr["base"] + up * h * y0 + sway * y0 * y0
                pts.append(p0[None] + d[None] * np.linspace(0, ln * h, 8)[:, None])
            crown = tr["base"] + up * h * 0.95 + sway
            leaves = crown[None] + tr["leaves"] * h * 2.1
            tw = 0.6 + 0.4 * np.sin(t * 2.0 + tr["lph"])
            stem = np.concatenate(pts)
            out.append(dict(pos=stem, size=0.007 * k, color=lin("#f8d27e"), alpha=0.8 * a, kind="spark", emit=1.4))
            out.append(dict(pos=leaves, size=0.012 * k, color=lin("#fff2c4"), alpha=0.75 * a * tw, kind="spark",
                            emit=1.2 + 0.8 * g, twinkle=0.8))
            out.append(dict(pos=crown[None], size=0.35 * h, color=lin("#ffd98c"), alpha=0.18 * a * g, kind="soft"))
        return out


class Water:
    """Water of light poured from her cupped hands onto the newest young tree."""

    def __init__(self, cast):
        self.c = cast
        T = cast.T
        self.pours = [(T["comp"] - 4.5, T["comp"] - 2.4), (T["comp"] - 0.6, T["comp"] + 1.9)]
        rng = np.random.default_rng(41)
        self.ph = rng.uniform(0, 1, 40)
        self.jx = rng.normal(0, 1, (40, 3))

    def sample(self, t):
        c = self.c
        out = []
        for a, b in self.pours:
            if not (a <= t <= b + 0.8):
                continue
            p = c.people[COMP_A]
            hands = 0.5 * (p.where(t, "palm.L", raw=False) + p.where(t, "palm.R", raw=False))
            sp = [e for e in c.extra if e[0] == "people trees"][0][1]
            target = sp.trees[2]["base"] + np.array([0.0, 0.05, 0.0])
            on = _fade(t, a, b + 0.8, 0.4, 0.8)
            u = (t * 0.9 + self.ph) % 1.0
            pts = hands[None] * (1 - u[:, None]) + target[None] * u[:, None] + \
                np.array([0.0, 0.12, 0.0])[None] * np.sin(np.pi * u)[:, None] + self.jx * 0.008
            out.append(dict(pos=pts, size=0.006 * c.st.scale, color=lin("#fff6dc"), alpha=0.85 * on, kind="spark",
                            emit=1.8, twinkle=0.5))
            out.append(dict(pos=hands[None], size=0.07 * c.st.scale, color=lin("#ffe6b0"), alpha=0.35 * on,
                            kind="soft"))
        return out


class Hearts:
    """Both hearts glow in the Compliment."""

    def __init__(self, cast):
        self.c = cast
        T = cast.T
        self.on = (T["comp"] + 6.6, T["comp_end"] - 0.3)
        rng = np.random.default_rng(51)
        self.motes = rng.normal(0, 1, (24, 3)) * 0.05
        self.ph = rng.uniform(0, 6.28, 24)

    def sample(self, t):
        a = _fade(t, self.on[0], self.on[1], 1.4, 1.6)
        if a <= 0:
            return []
        out = []
        for j, i in enumerate((COMP_A, COMP_B)):
            if j == 1:
                a2 = _fade(t, self.on[0] + 0.4, self.on[1], 1.4, 1.6)
            else:
                a2 = a
            p = self.c.people[i]
            h, n = p.body(t).where(t, "heart", normal=True)
            h = h + n * 0.04 * self.c.st.scale
            beat = 0.85 + 0.15 * np.sin(t * 2.2 + j)
            out.append(dict(pos=h[None], size=0.22 * self.c.st.scale, color=lin("#ffcf7a"), alpha=0.5 * a2 * beat,
                            kind="soft"))
            out.append(dict(pos=h[None], size=0.03 * self.c.st.scale, color=lin("#fff4dc"), alpha=a2, kind="spark",
                            emit=2.6 * beat))
            mo = h[None] + self.motes * (1 + 0.4 * np.sin(t + self.ph))[:, None] * self.c.st.scale
            out.append(dict(pos=mo, size=0.005 * self.c.st.scale, color=lin("#ffe2a0"), alpha=0.6 * a2, kind="spark",
                            twinkle=1.0, emit=1.4))
        return out


class StepRings:
    """A small ring of light on the water at every step out on the lake."""

    LIFE = 2.2

    def __init__(self, cast):
        self.c = cast
        self.cache = {}
        self.circle = np.stack([np.cos(np.linspace(0, 2 * np.pi, 40, endpoint=False)), np.zeros(40),
                                np.sin(np.linspace(0, 2 * np.pi, 40, endpoint=False))], axis=1)

    def _steps(self, i, w):
        """Footfalls of one walk: where an ankle comes down, on a 1/30 s grid (found once, when first needed)."""
        key = (i, w)
        if key not in self.cache:
            c = self.c
            p = c.people[i]
            a, b = p.keys["walks"][w]
            ts = np.arange(a, b + 0.6, 1 / 30.0)
            out = []
            for side in ("L", "R"):
                y = np.array([p.where(tt, "ankle." + side)[1] for tt in ts])
                down = y < y.min() + 0.02 * c.st.scale
                for s in np.where(down & ~np.r_[False, down[:-1]])[0]:
                    q = p.where(ts[s], "toe." + side)
                    if c.st.local(q)[2] < -0.7:          # on the water, not the shore
                        out.append((float(ts[s]), q[0], c.st.c[1] + 0.01, q[2]))
            self.cache[key] = out
        return self.cache[key]

    def sample(self, t):
        live = []
        for i, p in enumerate(self.c.people):
            for w, (a, b) in enumerate(p.keys["walks"]):
                if a - 0.1 <= t <= b + 0.6 + self.LIFE:
                    live += [s for s in self._steps(i, w) if s[0] <= t < s[0] + self.LIFE]
        if not live:
            return []
        k = self.c.st.scale
        pts, al = [], []
        for t0, x, y, z in live:
            age = (t - t0) / self.LIFE
            r = (0.06 + 0.5 * age ** 0.7) * k
            pts.append(np.array([x, y, z])[None] + self.circle * r)
            al.append(np.full(40, 0.7 * (1 - age) ** 1.6))
        return [dict(pos=np.concatenate(pts), size=0.007 * k, color=lin("#ffe6b0"), alpha=np.concatenate(al),
                     kind="spark", emit=1.6)]


class Mound:
    """A gentle rise of faint gold light under Heavenly Mother (the lead may draw the world's own instead:
    build(..., mound=False))."""

    def __init__(self, cast):
        self.c = cast
        st = cast.st
        rng = np.random.default_rng(61)
        n = 2600
        r = np.sqrt(rng.random(n)) * 1.9
        a = rng.uniform(0, 2 * np.pi, n)
        x, z = r * np.cos(a), r * np.sin(a) * 0.8
        y = 0.55 * np.exp(-(r / 1.15) ** 2) - 0.02
        self.pts = np.array([st.point(7.9 + xx, yy, -1.4 + zz) for xx, yy, zz in zip(x, y, z)])
        self.a = 0.35 * np.exp(-(r / 1.6) ** 2) + 0.05
        self.t0, self.t1 = cast.T["mother"][0] - 1.0, cast.T["mother"][1] + 1.0

    def sample(self, t):
        a = _fade(t, self.t0, self.t1, 1.5, 2.0)
        if a <= 0:
            return []
        return [dict(pos=self.pts, size=0.012 * self.c.st.scale, color=lin("#f0c47a"), alpha=self.a * a,
                     kind="spark", emit=1.0, twinkle=0.4)]


def build(stage=None, **kw):
    """All the people of the song on `stage` (see the module text); keywords go to Cast (n, points,
    actor_points, mother_points, mound, heavenly)."""
    return Cast(stage, **kw)
