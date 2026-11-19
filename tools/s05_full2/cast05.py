"""Song 05 "God Bless You!", full backdrop: the people of light.

Four people in the approved Revision 3 look (Claude Final v1 bodies, commit f43f451, package nine_reference_p3d,
as tools/nine_colours_minor/respect.py uses them): warm gold glitter, whole and radiant, no faces.

    A  "the one who prays", a young man in a long coat, beside the tree of blessing
    B  the brother, a young man, alone on the far left shore, bowed under a soft grey load
    C  a young woman who joins in verse 2, beside the tree
    D  the sister, a young woman, sitting alone on the far right shore, worn out

Touch only between people of the same gender: A takes B's hand (two men), C takes D's hand (two women).
In verse 2 A and B kneel and pray with C, but do not touch the sister.

Everything is a pure function of song time t (seconds). Times are in T below (see TIMELINE.md).
Cloth is simulated from each body's start, so every person is made of a few bodies joined at still moments
(SEG), as in the song 01 people lane (branch backdrop/s01-full-people), so any frame warms up quickly.
No em dash or en dash anywhere in this file.
"""
import numpy as np

import reference  # noqa: F401  (registers nine_reference_p3d)
from nine_reference_p3d import actor as act
from nine_reference_p3d import assets
from nine_reference_p3d.body import Body

# --------------------------------------------------------------------------------------------- where
TREE = (-2.3, -0.2)                    # the tree of blessing (x, z) on the lake
HOME = dict(A=(-1.05, 0.55), B=(-6.6, -0.9), C=(0.55, 0.75), D=(6.4, -0.7))
FACE0 = dict(A=8.0, B=55.0, C=-6.0, D=-62.0)

# --------------------------------------------------------------------------------------------- when
T = dict(
    form_A=14.0, form_B=14.6, bless=(16.0, 23.0),
    turn_A=21.8, kneel_A=24.4, pray1=(25.4, 36.2), cloak=(28.5, 33.5), lift_B=32.0,
    rise_B=37.5, rise_A=55.2,
    walk1=57.6, walk1_speed=0.72, offer1=63.8, grip1=(64.6, 69.2), load_off=66.4,
    back1=69.6, back_speed=0.66, touch_tree=(76.8, 82.6),
    form_C=83.6, form_D=79.0, walkB=83.6, walkB_speed=0.9,
    kneel2=94.6, pray2=(95.6, 106.4), lift_D=103.0, listen=(108.2, 125.0), rise2=125.8,
    getup_D=135.6, riseB=135.4,
    walk2=128.2, walk2_speed=0.72, offer2=134.6, grip2=(135.4, 139.6),
    back2=139.8, back2_speed=0.70, open_arms=(146.4, 152.6), quiet=153.4,
)
SEG = (13.5, 50.0, 80.5, 106.9, 151.0, 175.0)     # still moments where a body is renewed
JOIN = 0.6
LOOK = dict(name="glitter", seams=0.9, glints=0.004, size=1.25)
STYLE = dict(
    A=dict(shape="man", hair="short", garment="coat", color="#f6b042", color2="#ffd88a", height=1.72, build=.98,
           seed=51.0),
    B=dict(shape="man", hair="cap", garment="tunic", color="#ee9c30", color2="#ffd07a", height=1.75, build=1.0,
           seed=52.0),
    C=dict(shape="woman", hair="bun", garment="dress", color="#f8b84c", color2="#ffdc90", height=1.60, build=.95,
           seed=53.0),
    D=dict(shape="woman", hair="covered", garment="robe", color="#f2a83c", color2="#ffd486", height=1.58, build=.93,
           seed=54.0),
)


# what is seen through a person's shape: a deep warm gold light, a little richer at the head and shoulders
INSIDE = dict(base="day", sky_top="#e09a3a", sky_mid="#eaae50", sky_hor="#f4c86c", sun_int=0.0, clouds=0.0,
              hills=0.0, haze=0.0, mist=0.0, rays=0.0, dust=0.0, exposure=0.8)


def _ss(a, b, x):
    if b <= a:
        return float(x >= a)
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def _head(p, q):
    """Facing (degrees) from place p toward place q (0 faces +z, 90 faces +x)."""
    return float(np.degrees(np.arctan2(q[0] - p[0], q[1] - p[1])))


def _seg_keys(keys, s0, s1):
    """Motion keys for a body that lives in [s0, s1]: the state at s0 stands from the start (song 01 lane)."""
    before = [k for k in keys if k[0] <= s0]
    inside = [k for k in keys if s0 < k[0] <= s1 + 2.0]
    out = []
    if before:
        k = before[-1]
        opts = dict(k[2]) if len(k) > 2 else {}
        if k[1] in ("kneel", "rise", "sit", "get_up"):
            opts["dur"] = 0.01
        opts["blend"] = 0.01
        out.append((-1e9, k[1], opts))
    return out + inside


class Person:
    def __init__(self, name):
        self.name = name
        self.bodies = []          # (s0, s1, Body)
        self.proxies = []         # (s0, s1, Actor) without gestures, for aiming

    def body(self, t):
        for s0, s1, b in self.bodies:
            if t < s1 - JOIN * 0.5:
                return b
        return self.bodies[-1][2]

    def aim(self, t, name, normal=False):
        px = self.proxies[-1][2]
        for s0, s1, a in self.proxies:
            if t < s1 - JOIN * 0.5:
                px = a
                break
        return px.where(t, name, normal, True)

    def where(self, t, name):
        return self.body(t).where(t, name, raw=True)


class Cast:
    def __init__(self, points=80000):
        self.points = points
        self.p = {k: Person(k) for k in "ABCD"}
        self.keys = self._plan()
        for k in "ABCD":
            self._bodies(k)

    # ------------------------------------------------------------------ the plan
    def _plan(self):
        K = {}
        hA, hB, hC, hD = HOME["A"], HOME["B"], HOME["C"], HOME["D"]
        # A: forms, turns to the brother, kneels and prays, rises, crosses on the stones, takes his hand,
        #    walks back with him to the tree; kneels again for the sister; stands; opens his arms at the climax
        toB = _head(hA, hB)
        stopA = (hB[0] + 0.78, hB[1] + 0.16)
        dA = float(np.hypot(stopA[0] - hA[0], stopA[1] - hA[1]))
        arrA = T["walk1"] + dA / T["walk1_speed"]
        self.walk1 = (T["walk1"], arrA, hA, stopA)
        homeA2 = (-0.95, 0.95)
        dA2 = float(np.hypot(homeA2[0] - stopA[0], homeA2[1] - stopA[1]))
        arrA2 = T["back1"] + 0.5 + dA2 / T["back_speed"]
        homeB2 = (-3.35, 0.45)
        dB2 = float(np.hypot(homeB2[0] - hB[0], homeB2[1] - hB[1]))
        arrB2 = T["back1"] + dB2 / T["back_speed"]
        self.back1 = dict(A=(T["back1"] + 0.5, arrA2, stopA, homeA2), B=(T["back1"], arrB2, hB, homeB2))
        toD_A = _head(homeA2, hD)
        K["A"] = dict(
            at=[(-1e9, hA)],
            facing=[(-1e9, FACE0["A"]), (T["turn_A"], FACE0["A"]), (T["turn_A"] + 1.6, toB),
                    (T["walk1"] - 0.2, _head(hA, stopA)), (arrA - 0.3, _head(hA, stopA)), (arrA + 0.9, -100.0),
                    (T["back1"] + 0.1, -100.0), (T["back1"] + 0.6, _head(stopA, homeA2)),
                    (arrA2 - 0.3, _head(stopA, homeA2)), (arrA2 + 1.4, 20.0),
                    (T["kneel2"] - 2.0, 20.0), (T["kneel2"] - 0.6, toD_A), (T["rise2"] + 3.0, toD_A),
                    (T["walk2"] + 4.0, 35.0), (T["open_arms"][0], 15.0)],
            motion=[(-1e9, "stand"), (T["kneel_A"], "kneel", dict(one=True, dur=1.6, hands="free")),
                    (T["rise_A"], "rise", dict(one=True, dur=2.0, blend=0.05)), (T["rise_A"] + 2.1, "stand"),
                    (T["walk1"], "walk", dict(speed=T["walk1_speed"])), (arrA, "stand", dict(blend=0.8)),
                    (T["back1"] + 0.5, "walk", dict(speed=T["back_speed"])), (arrA2, "stand", dict(blend=0.8)),
                    (T["kneel2"], "kneel", dict(one=True, dur=1.6, hands="free")),
                    (T["rise2"], "rise", dict(one=True, dur=2.0, blend=0.05)), (T["rise2"] + 2.1, "stand")],
            gesture=[(T["kneel_A"] + 1.0, T["pray1"][1], "pray", {}),
                     (T["offer1"], T["grip1"][0] + 0.3, "offer", dict(side="R", ease=0.8)),
                     (T["grip1"][0], T["grip1"][1], "handshake", dict(side="R", to=self._grip1, grip=1.0, ease=0.7)),
                     (T["kneel2"] + 1.0, T["pray2"][1], "pray", {}),
                     (T["open_arms"][0], T["open_arms"][1], "open_arms", dict(ease=1.4)),
                     (T["quiet"], 1e9, "cup", dict(ease=1.6))],
            show=T["form_A"])
        # B: bowed and alone; lifts his head under the prayer; straightens and shines; takes the hand; walks to the
        #    tree; touches the tree; in verse 2 reaches toward his sister, kneels and prays with the others
        # B, verse 2: walks round behind the tree to his sister and kneels beside her; prays for her with the
        #    others (Encouragement); then turns to her and listens to her tender voice, leaning in (Respect);
        #    gets up as she is helped up, and walks back with them
        wp = (TREE[0], TREE[1] - 1.1)
        nearB = (hD[0] - 0.95, hD[1] - 0.75)
        d1 = float(np.hypot(wp[0] - homeB2[0], wp[1] - homeB2[1]))
        d2 = float(np.hypot(nearB[0] - wp[0], nearB[1] - wp[1]))
        t_wp = T["walkB"] + d1 / T["walkB_speed"]
        arrB = t_wp + d2 / T["walkB_speed"]
        assert arrB < T["kneel2"] + 0.2, arrB
        self.walkB = (T["walkB"], arrB, homeB2, nearB)
        self.nearB = nearB
        toD = _head(nearB, hD)
        homeB3 = (1.95, 0.35)
        dB3 = float(np.hypot(homeB3[0] - nearB[0], homeB3[1] - nearB[1]))
        backB = T["back2"] + 0.8
        arrB3 = backB + dB3 / T["back2_speed"]
        K["B"] = dict(
            at=[(-1e9, hB)],
            facing=[(-1e9, FACE0["B"]), (T["offer1"] - 1.2, FACE0["B"]), (T["offer1"] - 0.2, 80.0),
                    (T["back1"] - 0.3, 80.0), (T["back1"] + 0.3, _head(hB, homeB2)), (arrB2 - 0.3, _head(hB, homeB2)),
                    (arrB2 + 1.2, -95.0), (T["touch_tree"][1], -95.0), (T["touch_tree"][1] + 0.8, _head(homeB2, wp)),
                    (t_wp - 0.4, _head(homeB2, wp)), (t_wp + 0.5, _head(wp, nearB)), (arrB - 0.3, _head(wp, nearB)),
                    (arrB + 0.6, toD), (backB - 0.6, toD), (backB + 0.2, _head(nearB, homeB3)),
                    (arrB3 - 0.3, _head(nearB, homeB3)), (arrB3 + 1.2, 18.0)],
            motion=[(-1e9, "stand"), (T["back1"], "walk", dict(speed=T["back_speed"])),
                    (arrB2, "stand", dict(blend=0.8)),
                    (T["walkB"], "walk", dict(speed=T["walkB_speed"])), (arrB, "stand", dict(blend=0.6)),
                    (T["kneel2"] + 0.4, "kneel", dict(one=True, dur=1.6, hands="free")),
                    (T["riseB"], "rise", dict(one=True, dur=2.0, blend=0.05)), (T["riseB"] + 2.1, "stand"),
                    (backB, "walk", dict(speed=T["back2_speed"])), (arrB3, "stand", dict(blend=0.8))],
            gesture=[(-1e9, T["lift_B"], "bow", dict(amount=24.0)),
                     (T["lift_B"] + 0.5, T["rise_B"] + 1.0, "look_up", dict(amount=10.0)),
                     (T["grip1"][0], T["grip1"][1], "handshake", dict(side="R", to=self._grip1, grip=1.0, ease=0.7)),
                     (T["touch_tree"][0], T["touch_tree"][1], "touch",
                      dict(side="L", to=self._trunk, palm="in", ease=1.0)),
                     (T["kneel2"] + 1.4, T["pray2"][1], "pray", {}),
                     (T["listen"][0], T["listen"][1], "lean_in", dict(to=self._D_head, ease=1.4)),
                     (T["listen"][0] + 2.0, T["listen"][1] - 1.0, "nod", dict(period=3.2, amount=6.0)),
                     (T["open_arms"][0] + 0.3, T["open_arms"][1], "open_arms", dict(ease=1.4)),
                     (T["quiet"] + 0.4, 1e9, "cup", dict(ease=1.6))],
            show=T["form_B"])
        # C: forms beside the tree; kneels and prays for the sister; rises; crosses; takes her hand; walks back
        stopC = (hD[0] - 0.80, hD[1] + 0.25)
        dC = float(np.hypot(stopC[0] - hC[0], stopC[1] - hC[1]))
        arrC = T["walk2"] + dC / T["walk2_speed"]
        self.walk2 = (T["walk2"], arrC, hC, stopC)
        homeC2 = (0.35, 1.05)
        homeD2 = (1.35, 0.75)
        dC2 = float(np.hypot(homeC2[0] - stopC[0], homeC2[1] - stopC[1]))
        dD2 = float(np.hypot(homeD2[0] - hD[0], homeD2[1] - hD[1]))
        arrC2 = T["back2"] + dC2 / T["back2_speed"]
        arrD2 = T["back2"] + 0.4 + dD2 / T["back2_speed"]
        self.back2 = dict(C=(T["back2"], arrC2, stopC, homeC2), D=(T["back2"] + 0.4, arrD2, hD, homeD2))
        K["C"] = dict(
            at=[(-1e9, hC)],
            facing=[(-1e9, _head(hC, hD) - 10.0), (T["walk2"] - 0.3, _head(hC, stopC)), (arrC - 0.3, _head(hC, stopC)),
                    (arrC + 0.9, 100.0), (T["back2"] - 0.1, 100.0), (T["back2"] + 0.5, _head(stopC, homeC2)),
                    (arrC2 - 0.3, _head(stopC, homeC2)), (arrC2 + 1.4, -10.0)],
            motion=[(-1e9, "stand"), (T["kneel2"] + 0.2, "kneel", dict(one=True, dur=1.6, hands="free")),
                    (T["rise2"] - 0.2, "rise", dict(one=True, dur=2.0, blend=0.05)), (T["rise2"] + 1.9, "stand"),
                    (T["walk2"], "walk", dict(speed=T["walk2_speed"])), (arrC, "stand", dict(blend=0.8)),
                    (T["back2"], "walk", dict(speed=T["back2_speed"])), (arrC2, "stand", dict(blend=0.8))],
            gesture=[(T["kneel2"] + 1.2, T["pray2"][1], "pray", {}),
                     (T["offer2"], T["grip2"][0] + 0.3, "offer", dict(side="R", ease=0.8)),
                     (T["grip2"][0], T["grip2"][1], "handshake", dict(side="R", to=self._grip2, grip=1.0, ease=0.7)),
                     (T["open_arms"][0] + 0.6, T["open_arms"][1], "open_arms", dict(ease=1.4)),
                     (T["quiet"] + 0.8, 1e9, "cup", dict(ease=1.6))],
            show=T["form_C"])
        # D: sits alone, bowed; lifts her head as the prayer arrives; gets up; takes C's hand; walks to the tree
        K["D"] = dict(
            at=[(-1e9, hD)],
            facing=[(-1e9, FACE0["D"]), (T["offer2"] - 1.0, FACE0["D"]), (T["offer2"], -80.0),
                    (T["back2"] + 0.2, -80.0), (T["back2"] + 0.8, _head(hD, homeD2)),
                    (arrD2 - 0.3, _head(hD, homeD2)), (arrD2 + 1.4, -20.0)],
            motion=[(-1e9, "sit", dict(dur=0.01)), (T["getup_D"], "get_up", dict(blend=0.4)),
                    (T["getup_D"] + 3.0, "stand", dict(blend=0.9)),
                    (T["back2"] + 0.4, "walk", dict(speed=T["back2_speed"])), (arrD2, "stand", dict(blend=0.8))],
            gesture=[(T["lift_D"], T["listen"][0] + 1.0, "look_up", dict(amount=10.0)),
                     (T["listen"][0] + 1.0, T["listen"][1], "explain", dict(side="L", period=3.0)),
                     (T["grip2"][0], T["grip2"][1], "handshake", dict(side="R", to=self._grip2, grip=1.0, ease=0.7)),
                     (T["open_arms"][0] + 0.9, T["open_arms"][1], "open_arms", dict(ease=1.4)),
                     (T["quiet"] + 1.2, 1e9, "cup", dict(ease=1.6))],
            show=T["form_D"])
        return K

    # ------------------------------------------------------------------ aims (never through gestures)
    def _grip1(self, t):
        a = self.p["A"].aim(t, "shoulder.R")
        b = self.p["B"].aim(t, "shoulder.R")
        g = 0.5 * (a + b)
        g[1] = 0.5 * (a[1] + b[1]) - 0.40
        return g

    def _grip2(self, t):
        a = self.p["C"].aim(t, "shoulder.R")
        b = self.p["D"].aim(t, "shoulder.R")
        g = 0.5 * (a + b)
        g[1] = 0.5 * (a[1] + b[1]) - 0.36
        return g

    def _trunk(self, t):
        return np.array([TREE[0] + 0.08, 1.15, TREE[1] + 0.12])

    def _D_head(self, t):
        return self.p["D"].aim(t, "head")

    def _toward_D(self, t):
        a = self.p["B"].aim(t, "shoulder.R")
        d = np.array([HOME["D"][0], 1.6, HOME["D"][1]]) - a
        d /= np.linalg.norm(d)
        return a + 0.62 * d + np.array([0.0, 0.18, 0.0])

    # ------------------------------------------------------------------ bodies, one per segment
    def _bodies(self, k):
        keys = self.keys[k]
        st = STYLE[k]
        person = self.p[k]
        start = keys["show"]
        segs = [s for s in SEG if s > start]
        segs = [start - 0.3] + segs
        start_pt = None
        for i in range(len(segs) - 1):
            s0, s1 = segs[i], segs[i + 1]
            if i == 0:
                h = keys["at"][0][1]
                at_arg = (float(h[0]), 0.0, float(h[1]))
            else:
                at_arg = start_pt
            gest = [g for g in keys["gesture"] if g[1] > s0 - 2.0 and g[0] < s1 + 2.0]
            show = (s0 if i == 0 else s0 - JOIN * 0.5, s1 + JOIN * 0.5)
            effects = [dict(kind="form", t=start, dur=2.8)] if i == 0 else []
            rig = assets.Rig(st["shape"], st["height"], st["build"])
            mk = _seg_keys(keys["motion"], s0, s1)
            person.proxies.append((s0, s1, act.Actor(st["shape"], st["height"], at=at_arg, facing=keys["facing"],
                                                     motion=mk, seed=st["seed"], rig=rig, start=show[0])))
            b = Body(st["shape"], height=st["height"], at=at_arg, facing=keys["facing"], motion=mk, gesture=gest,
                     garment=st["garment"], hair=st["hair"], look=LOOK, color=st["color"], color2=st["color2"],
                     bright=4.0, points=self.points, seed=st["seed"], build=st["build"], show=show,
                     fade=(0.5 if i == 0 else JOIN * 0.5), effects=effects, wind=(0.25, 0.0, -0.1),
                     detail=dict(hand=2), wash=self._wash(k))
            person.bodies.append((s0, s1, b))
            g = person.aim(s1 - 0.01, "ground")
            start_pt = (float(g[0]), 0.0, float(g[2]))

    def _wash(self, k):
        """Colour washes: the brother pale while burdened, violet under the prayer's cloak, then bright gold; the
        sister pale until the prayer reaches her, a violet shawl, then gold."""
        if k == "B":
            def amount(t):
                pale = 1.0 - _ss(T["lift_B"], T["rise_B"] + 8.0, t)
                vio = _ss(T["cloak"][0] + 1.5, T["cloak"][1], t) * (1.0 - _ss(T["cloak"][1] + 2.0, T["rise_B"] + 6.0, t))
                return max(0.35 * pale, 0.55 * vio)
            def color_of(t):
                vio = _ss(T["cloak"][0] + 1.0, T["cloak"][0] + 2.0, t)
                return "#c9b8e8" if vio > 0.5 else "#d8d2c6"
            return dict(color="#c4b0ec", amount=amount)
        if k == "D":
            def amount(t):
                pale = 1.0 - _ss(T["lift_D"], 107.2 + 6.0, t)
                vio = _ss(T["lift_D"] - 2.0, T["lift_D"] + 1.0, t) * (1.0 - _ss(107.2, 107.2 + 6.0, t))
                return max(0.30 * pale, 0.50 * vio)
            return dict(color="#c4b0ec", amount=amount)
        return None

    # ------------------------------------------------------------------ the scene
    def add(self, scene):
        """Each body with its glitter grains also PAINTED in rich gold (the engine's paint, for bright skies): on
        the spring sky light alone would vanish, so every person stays a whole radiant figure of gold glitter,
        grain by grain, with its own light on top."""
        from nine_reference_p3d.api import Mask
        from nine_reference_p3d.body import _Shape
        for k in "ABCD":
            for i, (s0, s1, b) in enumerate(self.p[k].bodies):
                # a gentle warm glow inside the shape (light seen through glass), the painted glitter over it
                m = Mask(mode="sky", sky="world", look=INSIDE, edge=1.0, strength=0.3,
                         grow=0.008 * b.k * b.scale, source=_Shape(b))
                scene.add(f"person {k}{i}", Painted(b), mask=m)

    def where(self, k, t, name):
        return self.p[k].where(t, name)


class Painted:
    """A body whose batches are painted in gold as well as lit (paint, paint_light: engine/p3d/api.py)."""
    GOLD = None

    def __init__(self, body, paint=1.0, keep=0.45):
        self.body, self.paint, self.keep = body, paint, keep
        if Painted.GOLD is None:
            from nine_reference_p3d.api import lin
            Painted.GOLD = (np.asarray(lin("#d4801c"), np.float64), np.asarray(lin("#f4c25e"), np.float64))

    def __getattr__(self, name):
        return getattr(self.body, name)

    def sample(self, t, *a, **kw):
        got = self.body.sample(t, *a, **kw)
        if got is None:
            return None
        lo, hi = Painted.GOLD
        out = []
        for b in got if isinstance(got, (list, tuple)) else [got]:
            if b is None:
                continue
            b = dict(b)
            c = np.asarray(b.get("color", hi), np.float64)
            lum = c.mean(axis=-1, keepdims=True) if c.ndim else np.float64(c)
            rel = np.clip(lum / max(float(np.max(lum)) if np.size(lum) else 1.0, 1e-6), 0.0, 1.0)
            b["color"] = lo + (hi - lo) * rel
            b["paint"] = self.paint
            b["paint_light"] = self.keep
            out.append(b)
        return out
