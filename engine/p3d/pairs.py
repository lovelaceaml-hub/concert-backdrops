"""Two people in contact (engine/p3d/body.py): an embrace, hands held (walking, or raised together), being
helped up from kneeling, a child lifted into someone's arms, and the captured pull up from a seat.

Each function makes the two Bodies and returns them (a, b); add both to the scene. The bodies take any key of
Body(...) through the dicts `a` and `b` (shape, look, colours, garment, effects, show...). Contact is exact:
each hand is solved onto the other body's place at every frame, and each body reaches for where the other
is WITHOUT its own gestures (Body.where(..., raw=True)), so the two never wait on each other.

    from p3d import pairs
    a, b = pairs.embrace(8.0, at=(0, 0), facing=90, a=dict(shape="woman"), b=dict(shape="man"), approach=2.5)
    a.add(scene, "she"); b.add(scene, "he")

Feet stay put: standing bodies do not move their feet, walking ones are held where they step
(engine/p3d/actor.py), a lifted child has no ground at all.
"""
import numpy as np

from . import actor as act
from . import bodymath as bm
from .body import Body


def _dir(deg):
    a = np.radians(deg)
    return np.array([np.sin(a), 0.0, np.cos(a)])


def _xz(p):
    p = np.asarray(p, np.float64)
    return np.array([p[0], 0.0, p[1]]) if len(p) == 2 else p.copy()


def _kw(d, **defaults):
    out = dict(defaults)
    out.update(d or {})
    return out


def _gest(kw, *extra):
    kw["gesture"] = list(kw.get("gesture", ())) + list(extra)
    return kw


def _proxy(kw, at=None):
    """A plain Actor standing in for a body that is not built yet (without its own gestures): what the other
    body's gestures aim at while the bodies are being made (an effect of the first body may ask for its pose
    then)."""
    place = kw.get("at", (0.0, 0.0)) if at is None else at
    if callable(place):
        place = (0.0, 0.0)
    start = kw["show"][0] if kw.get("show") else None
    return act.Actor(kw.get("shape", "woman"), kw.get("height"), at=place, facing=kw.get("facing", 0.0),
                     motion=kw.get("motion", "stand"), start=start)


class Stand:
    """A stand-in for a body that is not built yet: answers where(t, place) from a plain Actor."""

    def __init__(self, kw, at=None):
        self.actor = _proxy(kw, at)
        self.rig = self.actor.rig
        self.k = self.rig.height / 1.6

    def where(self, t, name, normal=False, raw=False):
        return self.actor.where(t, name, normal)


class Refs(dict):
    """The bodies of a pair by key; while one is not built yet, its stand-in answers for it."""

    def __init__(self):
        super().__init__()
        self.stand = {}

    def __missing__(self, key):
        return self.stand[key]

    def build(self, order, **kws):
        """Makes the bodies in `order` from their keys (stand-ins first), then forgets the poses worked out on
        the stand-ins; returns them as a list."""
        for key, kw in kws.items():
            self.stand[key] = Stand(kw)
        for key in order:
            self[key] = Body(**kws[key])
        _built(*[self[key] for key in order])
        return [self[key] for key in order]


def _on(refs, key, place, proxies, raw=True):
    """A function of time: where `place` is on body refs[key], or on its stand-in while it is not built yet."""
    def f(tt):
        b = refs.get(key)
        if b is not None:
            return b.where(tt, place, raw=raw)
        return proxies[key].where(tt, place)
    return f


def _built(*bodies):
    """Once every body of a pair exists: forget the poses worked out while they were being made (they aimed at
    stand-ins)."""
    for b in bodies:
        b.actor._cache.clear()
        b._pts.clear()


def _walk_in(shape, height, t_stop, approach, speed, show=None):
    """How far someone walks in `approach` seconds before stopping at t_stop (with the motion blends).
    They stand until t_stop - approach, so the walk lasts `approach` seconds whenever the Body starts; the
    distance is measured from the same start the Body counts its travel from (its show, as Body does)."""
    if approach <= 0.0:
        return 0.0, None
    keys = [(-1e9, "stand", {}), (t_stop - approach, "walk", dict(speed=speed, blend=0.6)),
            (t_stop - 0.45, "stand", dict(blend=0.9))]
    start = None if show is None else float(show[0])
    a = act.Actor(shape, height, at=(0.0, 0.0), facing=0.0, motion=keys, start=start)
    return float(a.travel(t_stop + 1.5)[0] - a.travel(t_stop - approach - 0.05)[0]), keys


def _low_back(bl, br, k, side):
    """A hand's place low on someone's back, toward their `side`, from their shoulder blades."""
    u = (bl - br) if side == "L" else (br - bl)
    return 0.5 * (bl + br) + 0.32 * u - np.array([0.0, 0.21 * k, 0.0])


def embrace(t, at=(0.0, 0.0), facing=0.0, a=None, b=None, until=None, gap=0.34, approach=0.0, speed=0.9,
            ease=1.1, side=0.085, hold="mixed"):
    """Two people meet and hold each other (from t until `until`). a faces `facing` (degrees), b faces a.
    gap: metres between the two (chest to chest when they hold). approach: seconds they walk in toward each
    other before t (0: already standing there); they stand still until then, wherever their show starts, and
    stop exactly `gap` apart. side: metres each stands to their own left of the line between them, so the
    heads pass beside each other, cheek past shoulder (0: face to face). hold: "mixed" (a's arms over b's
    shoulders, b's round a's back, lower) or "high" (both over the shoulders)."""
    c = _xz(at)
    d = _dir(facing)
    left = _dir(facing + 90.0)
    ka = _kw(a, shape="woman", facing=facing)
    kb = _kw(b, shape="man", facing=facing + 180.0)
    refs = {}
    end = 1e9 if until is None else float(until)
    for kw, sgn in ((ka, -1.0), (kb, 1.0)):
        walked, keys = _walk_in(kw["shape"], kw.get("height"), t - 0.15, approach, speed, kw.get("show"))
        place = c + d * sgn * (0.5 * gap + walked) - left * sgn * side
        kw.setdefault("at", (place[0], place[2]))
        if keys and "motion" not in kw:
            kw["motion"] = keys
    px = dict(a=_proxy(ka), b=_proxy(kb))
    _gest(ka, (t, end, "embrace", dict(to=_on(refs, "b", "blade.R", px), to2=_on(refs, "b", "blade.L", px), head="L",
                                       ease=ease)))
    if hold == "high":
        tb = (_on(refs, "a", "blade.R", px), _on(refs, "a", "blade.L", px))
    else:
        bl, br = _on(refs, "a", "blade.L", px), _on(refs, "a", "blade.R", px)
        k = px["a"].rig.height / 1.6
        tb = (lambda tt: _low_back(bl(tt), br(tt), k, "R"), lambda tt: _low_back(bl(tt), br(tt), k, "L"))
    _gest(kb, (t + 0.12, end, "embrace", dict(to=tb[0], to2=tb[1], head="L", ease=ease)))
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    _built(refs["a"], refs["b"])
    return refs["a"], refs["b"]


def hands(a, b, t0, t1, raised=False, sides=None, ease=0.8, grip=1.0, height=0.42):
    """a and b (dicts of Body keys, standing or walking side by side) hold hands from t0 to t1: their inner
    hands (or sides=(a's, b's), for example ("R", "L")) meet at one point between them. raised=True: the joined
    hands go up high together (height: metres above the shoulders). Returns the two Bodies."""
    refs = {}
    px = dict(a=_proxy(a), b=_proxy(b))
    if sides is None:
        pa = act.Actor(a.get("shape", "woman"), a.get("height"), at=a.get("at", (0.0, 0.0)), facing=a.get("facing", 0.0))
        pb = act.Actor(b.get("shape", "woman"), b.get("height"), at=b.get("at", (0.0, 0.0)), facing=b.get("facing", 0.0))
        gb = pb.where(t0, "pelvis")
        ga = pa.where(t0, "pelvis")
        sa = "L" if np.linalg.norm(pa.where(t0, "shoulder.L") - gb) < np.linalg.norm(pa.where(t0, "shoulder.R") - gb) else "R"
        sb = "L" if np.linalg.norm(pb.where(t0, "shoulder.L") - ga) < np.linalg.norm(pb.where(t0, "shoulder.R") - ga) else "R"
    else:
        sa, sb = sides

    palm_a, palm_b = _on(refs, "a", "palm." + sa, px), _on(refs, "b", "palm." + sb, px)
    sh_a, sh_b = _on(refs, "a", "shoulder." + sa, px), _on(refs, "b", "shoulder." + sb, px)
    k = px["a"].rig.height / 1.6

    def grip_point(tt):
        return 0.5 * (palm_a(tt) + palm_b(tt))

    def up_point(tt):
        return 0.5 * (sh_a(tt) + sh_b(tt)) + np.array([0.0, height * k, 0.0])

    if raised:
        ga = (t0, t1, "raise_hand", dict(side=sa, to=up_point, ease=ease, palm="in", fingers="hold"))
        gb = (t0, t1, "raise_hand", dict(side=sb, to=up_point, ease=ease, palm="in", fingers="hold"))
    else:
        ga = (t0, t1, "handshake", dict(side=sa, to=grip_point, grip=grip, ease=ease, look=False, lean=0.0))
        gb = (t0, t1, "handshake", dict(side=sb, to=grip_point, grip=grip, ease=ease, look=False, lean=0.0))
    ka = _gest(_kw(a), ga)
    kb = _gest(_kw(b), gb)
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    _built(refs["a"], refs["b"])
    return refs["a"], refs["b"]


def helped_up(t, at=(0.0, 0.0), facing=0.0, a=None, b=None, rise=1.7, reach=1.0, apart=0.78, side="R"):
    """b kneels on one knee; a stands before b, reaches down a hand, and pulls b up to standing (b rises from t
    over `rise` seconds; the hands meet `reach` seconds before). a faces `facing`, b faces a."""
    c = _xz(at)
    d = _dir(facing)
    ka = _kw(a, shape="man", facing=facing)
    kb = _kw(b, shape="woman", facing=facing + 180.0)
    ka.setdefault("at", tuple((c - d * 0.5 * apart)[[0, 2]]))
    kb.setdefault("at", tuple((c + d * 0.5 * apart)[[0, 2]]))
    kb.setdefault("motion", [(-1e9, "kneel", dict(one=True, dur=0.01)), (t, "rise", dict(dur=rise, one=True, blend=0.05))])
    refs = {}
    other = "L" if side == "R" else "R"
    px = dict(a=_proxy(ka), b=_proxy(kb))
    sh_a, sh_b = _on(refs, "a", "shoulder." + side, px), _on(refs, "b", "shoulder." + side, px)
    k = px["a"].rig.height / 1.6

    def grip_point(tt):
        pa, pb = sh_a(tt), sh_b(tt)
        g = 0.5 * (pa + pb)
        g[1] = 0.5 * (pa[1] + pb[1]) - 0.33 * k
        return g

    end = t + rise + 0.9
    _gest(ka, (t - reach, end, "handshake", dict(side=side, to=grip_point, grip=1.0, ease=0.7)))
    _gest(kb, (t - reach * 0.8, end, "handshake", dict(side=side, to=grip_point, grip=1.0, ease=0.6)))
    _gest(kb, (end - 0.2, end + 30.0, "hand_on_shoulder", dict(side=other, to=sh_a, ease=0.9)))
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    _built(refs["a"], refs["b"])
    return refs["a"], refs["b"]


def child_into_arms(t, at=(0.0, 0.0), facing=0.0, adult=None, child=None, lift=1.0, until=None):
    """A child stands before an adult; the adult bends, takes the child under the arms and lifts it (from t over
    `lift` seconds) into a hold before the chest, the child's arms round the adult's neck. The adult faces
    `facing`; returns (adult, child)."""
    c = _xz(at)
    d = _dir(facing)
    ka = _kw(adult, shape="woman", facing=facing, at=(c[0], c[2]))
    kc = _kw(child, shape="child", facing=facing + 180.0)
    refs = {}
    ground = c + d * 0.40
    end = 1e9 if until is None else float(until)
    px = dict(a=_proxy(ka), c=_proxy(kc, at=(ground[0], ground[2])))
    k = px["a"].rig.height / 1.6
    child_root = px["c"].rig.neutral_pos[0][1]

    def held_origin(tt):
        A = refs.get("a")
        if A is None:
            ch = px["a"].where(tt, "chest")
            fw = d.copy()
        else:
            ch = A.where(tt, "chest", raw=True)
            fw = A.where(tt, "chest", normal=True, raw=True)[1]
            fw = np.array([fw[0], 0.0, fw[2]])
            fw /= max(np.linalg.norm(fw), 1e-6)
        pelvis = ch + fw * 0.20 * k - np.array([0.0, 0.22 * k, 0.0])
        return pelvis - np.array([0.0, child_root, 0.0])

    def place(tt):
        u = float(bm.smoother((tt - t) / max(lift, 1e-3)))
        if u <= 0.0:
            return ground
        return ground * (1.0 - u) + held_origin(tt) * u

    kc["at"] = place
    kc.setdefault("motion", [(t - 1e-3, "stand"), (t, "held", dict(blend=lift))])
    # the adult bends to the child, takes it under the arms, and holds it
    _gest(ka, (t - 0.9, t + lift * 0.6, "bow", dict(amount=34.0, ease=0.7)))
    neck = _on(refs, "a", "neck", px)
    _gest(ka, (t - 0.8, end, "embrace", dict(to=_on(refs, "c", "side.R", px), to2=_on(refs, "c", "side.L", px),
                                              head="L", ease=0.7)))
    _gest(kc, (t + lift * 0.5, end, "embrace", dict(to=lambda tt: neck(tt) + np.array([0.06, -0.02, 0.0]),
                                                    to2=lambda tt: neck(tt) - np.array([0.06, 0.02, 0.0]), head="R",
                                                    ease=0.8)))
    refs["a"] = Body(**ka)
    refs["c"] = Body(**kc)
    _built(refs["a"], refs["c"])
    return refs["a"], refs["c"]


def pull_up(t, at=(0.0, 0.0), facing=0.0, a=None, b=None):
    """The captured pair (CMU 22_01 and 23_01): b sits on a low seat, a walks up, takes b's right hand and pulls
    b to standing; both from t (6.5 s). Their places are the capture's own, turned to `facing`."""
    ka = _kw(a, shape="man", facing=facing, at=at)
    kb = _kw(b, shape="man", facing=facing, at=at)
    ka.setdefault("motion", [(t, "pull_up")])
    kb.setdefault("motion", [(t, "helped_up")])
    return Body(**ka), Body(**kb)
