"""Acting: the nine expressions of the campaign, performed by people of light (engine/p3d/body.py, pairs.py and
crowd.py), callable by the expression's label as in words.EXPRESSIONS.

    from p3d import acting
    acting.add(scene, "Gratitude", 10.0, 14.0, at=(0, 0), view=0, variant="clasp",
               style=dict(look="glitter", color="#ffd29a"))
    # or take the point sets yourself:
    sets = acting.perform("Encouragement", 30.0, 34.0, at=(4, -2), view=20, variant="lights")

`perform(expression, t0, t1, ...)` returns the point sets of one performance (Bodies, and a Crowd for the crowd
performances); `add(scene, ...)` adds them (each Body with the mask its look needs). The people are there, at
rest and alive, from t0 - pre. The act begins at t0 and is acted (anticipation, overshoot, settle, the trunk
leading and the hands following); its clear pose is reached about a second later and held, alive (breathing,
living hands, a nod or a sway), until t1, when they let go of it. Start the act about a second before the
words become readable, so the pose is already there when they do.

  expression  the label as in words.EXPRESSIONS ("Greeting", "Gratitude", "Apology", "Inclusiveness",
              "Concession", "Respect", "Encouragement", "Consideration", "Compliment"; any case), its number
              there (1 to 9), or the expression's dict
  variant     one of VARIANTS[label] (default the first), or "solo", "pair" or "crowd" for the first of that
              kind (KIND says which is which)
  at          the place of the performance on the ground (x, z), metres
  view        azimuth in degrees from `at` toward the camera (0: the camera stands at +z): the performance is
              turned to read from there (pairs face each other across the picture, opened a little to it)
  style       Body keys for everyone (look, color, color2, points, garment, effects, wind...);
              style_a and style_b: for the first and the second person only (shape, garment, height...)
  crowd       Crowd keys for the crowd performances (n, people, color, points, kinds...)
  pre, post   seconds the people are there before t0 and after t1 (default 1.0 and 1.5; the release of the
              pose takes about a second after t1)
  seed        another cast (other timing, other faces of the same performance)

VARIANTS (what is acted)
  Greeting       wave       solo   a warm wave across a distance, leaning in a little
                 turn       pair   a hand on the shoulder from behind; the other turns to them and greets
                 crowd      crowd  many people waving, each starting in their own time
  Gratitude      heart      solo   a hand laid on the heart and a bow
                 clasp      pair   one clasps the other's offered hand in both hands and bows; the other lays
                                   a hand on their heart
                 gift       pair   a small light offered in cupped hands passes into the other's hands; the
                                   giver lays a hand on the heart
                 crowd      crowd  a crowd bowing, hands on hearts
  Apology        bowed      solo   head bowed, open hands held low
                 comfort    pair   one sits with head bowed; the other kneels beside them, a hand on their back
  Inclusiveness  embrace    pair   an embrace
                 arm        pair   side by side, an arm round the shoulders, heads leaning together
                 circle     crowd  a ring of people opens its arms as a child walks into the middle
  Concession     after_you  solo   a step aside, an open palm toward the way, a small bow
                 pass       pair   one steps aside and bows; the other walks past, a hand on the heart
  Respect        listen     pair   two seated on the ground: one speaks with a hand, the other leans in and
                                   nods
                 nod        pair   the same, standing
  Encouragement  pray       solo   kneeling down, hands joined in prayer, head bowed
                 shoulder   pair   a hand on the shoulder of someone kneeling in prayer, both heads bowed
                 lights     crowd  a ring of people raising lights round one who kneels (the lights rise in a
                                   wave from the middle out)
  Consideration  help_up    pair   a hand reached down; the one kneeling is pulled up to standing
                 lift_child pair   a child lifted into someone's arms
  Compliment     applause   crowd  a ring clapping and cheering round one person, who lays a hand on the heart
                 twirl      solo   a joyful twirl
                 raise      pair   two hold hands and raise them high, the other hand thrown up
                 cheer      crowd  a crowd cheering, arms thrown up
"""
import numpy as np

from . import pairs
from .api import lin
from .body import Body

LABELS = ("Greeting", "Gratitude", "Apology", "Inclusiveness", "Concession", "Respect", "Encouragement",
          "Consideration", "Compliment")
VARIANTS = {
    "Greeting": ("wave", "turn", "crowd"),
    "Gratitude": ("heart", "clasp", "gift", "crowd"),
    "Apology": ("bowed", "comfort"),
    "Inclusiveness": ("embrace", "arm", "circle"),
    "Concession": ("after_you", "pass"),
    "Respect": ("listen", "nod"),
    "Encouragement": ("pray", "shoulder", "lights"),
    "Consideration": ("help_up", "lift_child"),
    "Compliment": ("applause", "twirl", "raise", "cheer"),
}
KIND = dict(wave="solo", turn="pair", crowd="crowd", heart="solo", clasp="pair", bowed="solo", comfort="pair",
            embrace="pair", arm="pair", circle="crowd", after_you="solo", listen="pair", nod="pair", pray="solo",
            shoulder="pair", lights="crowd", help_up="pair", lift_child="pair", applause="crowd", twirl="solo",
            cheer="crowd")
KIND["pass"] = "pair"
KIND["gift"] = "pair"
KIND["raise"] = "pair"
HOLD_OUT = 0.9          # the gestures let go over about this long after t1


def label_of(expression):
    """The label of an expression given as a label (any case), its number (1 to 9) or its dict."""
    if isinstance(expression, dict):
        expression = expression["label"]
    if isinstance(expression, (int, np.integer)):
        return LABELS[int(expression) - 1]
    for lab in LABELS:
        if lab.lower() == str(expression).strip().lower():
            return lab
    raise ValueError("no performance for %r (labels: %s)" % (expression, ", ".join(LABELS)))


def pick(expression, variant=None):
    """(label, variant) for an expression and a variant name or kind."""
    lab = label_of(expression)
    vs = VARIANTS[lab]
    if variant is None:
        return lab, vs[0]
    if variant in ("solo", "pair", "crowd"):
        for v in vs:
            if KIND[v] == variant:
                return lab, v
        return lab, vs[0]
    if variant not in vs:
        raise ValueError("%s can be performed as %s, got %r" % (lab, ", ".join(vs), variant))
    return lab, variant


class _Stage:
    """Where the performance stands and which way the camera looks at it."""

    def __init__(self, at, view):
        self.c = np.array([float(at[0]), 0.0, float(at[1])])
        a = np.radians(view)
        self.view = float(view)
        self.cam = np.array([np.sin(a), 0.0, np.cos(a)])          # toward the camera
        self.right = np.array([np.cos(a), 0.0, -np.sin(a)])       # the picture's right

    def place(self, x=0.0, z=0.0):
        """A place x metres to the picture's right and z toward the camera, as (x, z) on the ground."""
        p = self.c + self.right * x + self.cam * z
        return (float(p[0]), float(p[2]))

    def point(self, x=0.0, y=0.0, z=0.0):
        p = self.c + self.right * x + self.cam * z
        return np.array([p[0], float(y), p[2]])

    def face(self, toward_right=0.0, open_=0.0):
        """A facing in degrees: toward_right=1 faces the picture's right, -1 its left, 0 the camera; open_ turns
        it that many degrees back toward the camera."""
        if toward_right == 0.0:
            return self.view
        return self.view + 90.0 * toward_right - open_ * np.sign(toward_right)


class _Cast:
    """Makes the Body keys of each person: the shared style, the performance's own, then the person's."""

    def __init__(self, base, seed):
        self.base, self.seed, self.k = base, float(seed), 0

    def __call__(self, own=None, **kw):
        d = dict(self.base)
        d.update(kw)
        d.update(own or {})
        d.setdefault("seed", self.seed + 1.37 * self.k)
        self.k += 1
        return d


def perform(expression, t0, t1, at=(0.0, 0.0), view=0.0, variant=None, style=None, style_a=None, style_b=None,
            crowd=None, pre=1.0, post=1.5, seed=1.0):
    """The point sets of one performance (see the module text)."""
    lab, v = pick(expression, variant)
    st = _Stage(at, view)
    t0, t1 = float(t0), float(t1)
    base = dict(style or {})
    base.setdefault("show", (t0 - pre, t1 + post))
    base.setdefault("fade", 0.5)
    cast = _Cast(base, seed)
    cw = dict(crowd or {})
    cw.setdefault("seed", seed)
    for k in ("color", "color2", "bright", "size"):
        if k in base:
            cw.setdefault(k, base[k])
    cw.setdefault("start", t0 - pre)
    cw.setdefault("until", t1 + post - 0.5)
    cw.setdefault("fade", 0.5)
    cw.setdefault("flash", 0.15)
    fn = globals()["_%s_%s" % (lab.lower(), v)]
    return fn(st, t0, t1, cast, dict(style_a or {}), dict(style_b or {}), cw)


def add(scene, expression, t0, t1, name=None, **kw):
    """Adds a performance to the scene (Bodies with the masks their looks need); returns its point sets."""
    sets = perform(expression, t0, t1, **kw)
    stem = name or "act_%s_%d" % (label_of(expression).lower(), int(round(t0 * 100)))
    for i, ps in enumerate(sets):
        if isinstance(ps, Body):
            ps.add(scene, "%s_%d" % (stem, i))
        else:
            scene.add("%s_%d" % (stem, i), ps)
    return sets


class Lamp:
    """A small light carried in someone's hands, and given from hand to hand.

    keys    [(t, body, places), ...]: from t the light sits at the mean of the body's named places (for example
            ("palm.L", "palm.R") for cupped hands), `lift` above them; it moves to the next key's hands over
            `swap` seconds
    """

    def __init__(self, keys, color="#ffd08a", size=0.11, bright=1.0, show=None, lift=0.045, swap=0.45, seed=1.0):
        self.keys = sorted(keys, key=lambda k: k[0])
        self.col = lin(color) if isinstance(color, str) else np.asarray(color, np.float64)
        self.size, self.bright, self.show, self.lift, self.swap = float(size), float(bright), show, lift, swap
        rng = np.random.default_rng(int(seed * 101) + 5)
        self.motes = rng.normal(0.0, 1.0, (14, 3)) * np.array([0.035, 0.05, 0.035])
        self.mph = rng.uniform(0.0, 2 * np.pi, 14)

    def _at(self, k, t):
        _t, body, places = self.keys[k]
        p = np.mean([body.where(t, n) for n in places], axis=0)
        return p + np.array([0.0, self.lift * body.k, 0.0])

    def where(self, t):
        k = max([i for i, key in enumerate(self.keys) if key[0] <= t] or [0])
        p = self._at(k, t)
        if k > 0:
            u = float(np.clip((t - self.keys[k][0]) / max(self.swap, 1e-3), 0.0, 1.0))
            if u < 1.0:
                u = u * u * (3 - 2 * u)
                p = self._at(k - 1, t) * (1 - u) + p * u + np.array([0.0, 0.05 * np.sin(np.pi * u), 0.0])
        return p

    def sample(self, t):
        a = 1.0
        if self.show is not None:
            a = float(np.clip((t - self.show[0]) / 0.4, 0.0, 1.0) * np.clip((self.show[1] - t) / 0.4, 0.0, 1.0))
            if a <= 0.0:
                return []
        p = self.where(t)
        fl = 0.9 + 0.1 * np.sin(t * 7.3) * np.sin(t * 3.1 + 1.0)
        mo = p + self.motes * (1.0 + 0.3 * np.sin(t * 1.7 + self.mph))[:, None] + \
            np.stack([np.zeros(14), 0.02 * np.sin(t * 1.3 + self.mph), np.zeros(14)], axis=1)
        c = self.col * self.bright
        return [dict(pos=p[None], size=self.size, color=c * 0.9, alpha=0.6 * a * fl, kind="soft", backlight=0.3),
                dict(pos=p[None], size=0.02, color=c, alpha=a, kind="spark", emit=3.0 * fl),
                dict(pos=mo, size=0.006, color=c, alpha=0.7 * a, kind="spark", twinkle=1.0, emit=1.5)]


def _crowd(cw, **kw):
    from .crowd import Crowd
    d = dict(kw)
    d.update(cw)
    return Crowd(**d)


def _field(st, n, near=3.0, far=12.0, width=10.0, seed=1.0):
    """n places spread over the ground behind the performance place, widening with distance."""
    rng = np.random.default_rng(int(seed * 977) + 3)
    out = []
    for k in range(n):
        u = (k + 0.5) / n
        d = near + (far - near) * u ** 0.8
        w = width * (0.6 + 0.4 * d / far)
        x = ((k * 0.618034) % 1.0 - 0.5) * w + rng.uniform(-0.25, 0.25)
        out.append(st.place(x, -d + rng.uniform(-0.3, 0.3)))
    return np.array(out)


def _ring(c, r, n, gap_dir=None, gap=0.0, phase=0.0):
    """n places on a circle round c (x, z); gap_dir (radians, from +z toward +x) leaves an opening of `gap`
    radians either side of it."""
    ang = phase + np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    if gap_dir is not None and gap > 0:
        d = np.abs(((ang - gap_dir + np.pi) % (2 * np.pi)) - np.pi)
        ang = ang[d > gap]
    return np.stack([c[0] + r * np.sin(ang), c[1] + r * np.cos(ang)], axis=1)


# ------------------------------------------------------------------------------------------------- Greeting
def _greeting_wave(st, t0, t1, who, sa, sb, cw):
    return [Body(**who(sa, shape="woman", at=st.place(0, 0), facing=st.face(0) - 15.0,
                       gesture=[(t0, t1 + HOLD_OUT, "wave", dict(side="R")),
                                (t0 + 0.2, t1 + HOLD_OUT, "lean_in", dict(amount=0.6))]))]


def _greeting_turn(st, t0, t1, who, sa, sb, cw):
    refs = {}
    turn0, turn1 = t0 + 0.55, t0 + 1.55

    def greet(t):
        b = refs["b"].where(t, "shoulder.L", raw=True)
        toward = refs["a"].where(t, "head", raw=True) - refs["b"].where(t, "head", raw=True)
        return b + np.array([0.0, 0.16, 0.0]) + 0.22 * toward
    kb = who(sb, shape="woman", at=st.place(0.28, 0.0),
             facing=[(turn0, st.face(1.0, 10.0)), (turn1, st.face(-1.0, 30.0))],
             motion=[(-1e9, "stand"), (turn0 - 0.05, "shuffle", dict(blend=0.3)), (turn1, "stand", dict(blend=0.5))],
             gesture=[(turn1 - 0.3, t1 + HOLD_OUT, "raise_hand", dict(side="L", palm="fwd", fingers="open", to=greet)),
                      (turn1 - 0.2, t1 + HOLD_OUT, "lean_in",
                       dict(to=lambda t: refs["a"].where(t, "head", raw=True), amount=0.7))])
    ka = who(sa, shape="man", at=st.place(-0.40, -0.12), facing=st.face(1.0, 15.0),
             gesture=[(t0 - 0.2, turn1 + 0.1, "hand_on_shoulder",
                       dict(side="R", to=lambda t: refs["b"].where(t, "shoulder.R", raw=True))),
                      (turn1 - 0.4, t1 + HOLD_OUT, "lean_in",
                       dict(to=lambda t: refs["b"].where(t, "head", raw=True), amount=0.8)),
                      (turn1, t1 + HOLD_OUT, "nod", dict(period=1.9, amount=6.0))])
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    return [refs["a"], refs["b"]]


def _greeting_crowd(st, t0, t1, who, sa, sb, cw):
    n = cw.pop("n", 36)
    return [_crowd(cw, places=_field(st, n, 2.0, 11.0, 9.0, seed=cw["seed"]), facing=st.view,
                   kinds=(("wave", 3.0), ("stand", 1.0)), act=dict(t=t0, dur=0.9), act_end=t1)]


# ------------------------------------------------------------------------------------------------ Gratitude
def _gratitude_heart(st, t0, t1, who, sa, sb, cw):
    return [Body(**who(sa, shape="woman", at=st.place(0, 0), facing=st.face(1.0, 48.0),
                       gesture=[(t0, t1 + HOLD_OUT, "hand_on_heart", dict(side="R", bow=12.0)),
                                (t0 + 0.3, t1 + HOLD_OUT, "bow", dict(amount=18.0))]))]


def _gratitude_clasp(st, t0, t1, who, sa, sb, cw):
    refs = {}

    def meet(t):
        a = refs["a"].where(t, "chest", raw=True)
        b = refs["b"].where(t, "chest", raw=True)
        g = 0.5 * (a + b)
        g[1] -= 0.30 * refs["a"].k
        return g
    ka = who(sa, shape="woman", at=st.place(-0.32, 0.0), facing=st.face(1.0, 18.0),
             gesture=[(t0 + 0.15, t1 + HOLD_OUT, "clasp", dict(to=meet)),
                      (t0 + 0.6, t1 + HOLD_OUT, "bow", dict(amount=14.0))])
    kb = who(sb, shape="man", at=st.place(0.32, 0.0), facing=st.face(-1.0, 18.0),
             gesture=[(t0 - 0.1, t1 + HOLD_OUT, "handshake", dict(side="R", to=meet, grip=1.0)),
                      (t0 + 0.7, t1 + HOLD_OUT, "hand_on_heart", dict(side="L", bow=6.0))])
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    return [refs["a"], refs["b"]]


def _gratitude_gift(st, t0, t1, who, sa, sb, cw):
    give = t0 + 1.0
    ka = who(sa, shape="woman", at=st.place(-0.375, 0.0), facing=st.face(1.0, 18.0),
             gesture=[(-1e9, give + 0.5, "cup", dict(out=0.03, ease_in=0.01)),
                      (t0, give + 0.6, "cup", dict(out=0.13)),
                      (give + 0.4, t1 + HOLD_OUT, "hand_on_heart", dict(side="R", bow=10.0)),
                      (give + 0.5, t1 + HOLD_OUT, "bow", dict(amount=10.0))])
    kb = who(sb, shape="man", at=st.place(0.375, 0.0), facing=st.face(-1.0, 18.0),
             gesture=[(t0 + 0.3, give + 0.9, "cup", dict(out=0.03)),
                      (give + 0.5, t1 + HOLD_OUT, "cup", dict(out=-0.06, height=0.08)),
                      (give + 0.7, t1 + HOLD_OUT, "look_up", dict(amount=-6.0))])
    a, b = Body(**ka), Body(**kb)
    hands = ("palm.L", "palm.R")
    lamp = Lamp([(-1e9, a, hands), (give, b, hands)], show=ka["show"], seed=st.view + 3.0)
    return [a, b, lamp]


def _gratitude_crowd(st, t0, t1, who, sa, sb, cw):
    n = cw.pop("n", 40)
    return [_crowd(cw, places=_field(st, n, 2.0, 12.0, 10.0, seed=cw["seed"]), facing=st.view, kinds=("heart",),
                   act=dict(t=t0, dur=1.0), act_end=t1)]


# -------------------------------------------------------------------------------------------------- Apology
def _apology_bowed(st, t0, t1, who, sa, sb, cw):
    return [Body(**who(sa, shape="man", at=st.place(0, 0), facing=st.face(-1.0, 50.0),
                       gesture=[(t0, t1 + HOLD_OUT, "open_hands", dict(bow=24.0)),
                                (t0 + 0.3, t1 + HOLD_OUT, "bow", dict(amount=16.0))]))]


def _apology_comfort(st, t0, t1, who, sa, sb, cw):
    refs = {}
    kb = who(sb, shape="woman", at=st.place(0.30, -0.08), facing=st.face(1.0, 40.0),
             motion=[(-1e9, "sit", dict(dur=0.01, bowed=1.0))])
    ka = who(sa, shape="man", at=st.place(-0.28, 0.06), facing=st.face(1.0, 0.0),
             motion=[(-1e9, "stand"), (t0 - 0.3, "kneel", dict(one=True, dur=1.4, hands="free", blend=0.05))],
             gesture=[(t0 + 0.9, t1 + HOLD_OUT, "touch",
                       dict(side="R", to=lambda t: refs["b"].where(t, "back", raw=True), palm="fwd", fingers="open",
                            lean=0.45)),
                      (t0 + 0.8, t1 + HOLD_OUT, "bow", dict(amount=8.0))])
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    return [refs["a"], refs["b"]]


# -------------------------------------------------------------------------------------------- Inclusiveness
def _inclusiveness_embrace(st, t0, t1, who, sa, sb, cw):
    a, b = pairs.embrace(t0, at=st.place(0, 0), facing=st.face(1.0, 0.0), a=who(sa, shape="woman"),
                         b=who(sb, shape="woman"), until=t1 + HOLD_OUT, approach=0.0)
    return [a, b]


def _inclusiveness_arm(st, t0, t1, who, sa, sb, cw):
    refs = {}
    ka = who(sa, shape="man", at=st.place(-0.23, 0.0), facing=st.face(0) + 10.0,
             gesture=[(t0, t1 + HOLD_OUT, "arm_round",
                       dict(side="L", to=lambda t: refs["b"].where(t, "shoulder.L", raw=True))),
                      (t0 + 0.4, t1 + HOLD_OUT, "lean_in",
                       dict(to=lambda t: refs["b"].where(t, "head", raw=True), amount=0.6))])
    kb = who(sb, shape="woman", at=st.place(0.23, 0.02), facing=st.face(0) - 10.0,
             gesture=[(t0 + 0.6, t1 + HOLD_OUT, "lean_in",
                       dict(to=lambda t: refs["a"].where(t, "head", raw=True), amount=0.8)),
                      (t0 + 0.7, t1 + HOLD_OUT, "hand_on_heart", dict(side="R", bow=4.0))])
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    return [refs["a"], refs["b"]]


def _inclusiveness_circle(st, t0, t1, who, sa, sb, cw):
    c = np.array(st.place(0.0, -1.2))
    cw.pop("n", None)
    places = _ring(c, 2.3, 13, gap_dir=np.radians(st.view), gap=0.42, phase=np.radians(st.view) + np.pi / 13)
    cr = _crowd(cw, places=places, facing="center", kinds=("open",), act=dict(t=t0, dur=0.7), act_end=t1)
    walker = Body(**who(sa, shape="child", at=st.place(0.0, 2.0), facing=st.view + 180.0,
                        motion=[(-1e9, "stand"), (t0 - 0.5, "walk", dict(speed=0.85)),
                                (t0 + 2.4, "stand", dict(blend=0.8))],
                        gesture=[(t0 + 2.2, t1 + HOLD_OUT, "look_up", dict(amount=12.0))]))
    return [cr, walker]


# ----------------------------------------------------------------------------------------------- Concession
def _concession_after_you(st, t0, t1, who, sa, sb, cw):
    way = st.point(0.55, 0.9, 0.5)
    return [Body(**who(sa, shape="man", at=[(t0 - 0.1, st.place(0.0, 0.0)), (t0 + 0.8, st.place(-0.42, -0.1))],
                       facing=[(t0 - 0.1, st.face(0) + 5.0), (t0 + 0.8, st.face(0) + 20.0)],
                       motion=[(-1e9, "stand"), (t0 - 0.15, "shuffle", dict(blend=0.25)),
                               (t0 + 0.85, "stand", dict(blend=0.4))],
                       gesture=[(t0 + 0.25, t1 + HOLD_OUT, "after_you", dict(side="L", to=way, bow=14.0))]))]


def _concession_pass(st, t0, t1, who, sa, sb, cw):
    ka = who(sa, shape="man", at=[(t0 - 0.1, st.place(0.05, 0.1)), (t0 + 0.8, st.place(-0.5, 0.35))],
             facing=st.face(1.0, 45.0),
             motion=[(-1e9, "stand"), (t0 - 0.15, "shuffle", dict(blend=0.25)), (t0 + 0.85, "stand", dict(blend=0.4))],
             gesture=[(t0 + 0.2, t1 + HOLD_OUT, "after_you", dict(side="R", bow=16.0))])
    kb = who(sb, shape="woman", at=st.place(-1.7, -0.5), facing=st.face(1.0, 0.0),
             motion=[(-1e9, "stand"), (t0 + 0.4, "walk", dict(speed=0.8)), (t1 + 0.6, "stand", dict(blend=0.9))],
             gesture=[(t0 + 1.0, t1 + HOLD_OUT, "hand_on_heart", dict(side="L", bow=8.0))])
    return [Body(**ka), Body(**kb)]


# -------------------------------------------------------------------------------------------------- Respect
def _respect_pair(st, t0, t1, who, sa, sb, seated):
    refs = {}
    sit = [(-1e9, "sit", dict(dur=0.01, bowed=0.0))] if seated else "stand"
    x = 0.42 if seated else 0.38
    ka = who(sa, shape="woman", at=st.place(-x, 0.0), facing=st.face(1.0, 22.0), motion=sit,
             gesture=[(t0, t1 + HOLD_OUT, "lean_in", dict(to=lambda t: refs["b"].where(t, "head", raw=True))),
                      (t0 + 0.6, t1 + HOLD_OUT, "nod", dict(period=1.8, amount=8.0))])
    kb = who(sb, shape="man", at=st.place(x, 0.0), facing=st.face(-1.0, 22.0), motion=sit,
             gesture=[(t0 - 0.3, t1 + HOLD_OUT, "explain", dict(side="R", period=1.9))])
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    return [refs["a"], refs["b"]]


def _respect_listen(st, t0, t1, who, sa, sb, cw):
    return _respect_pair(st, t0, t1, who, sa, sb, True)


def _respect_nod(st, t0, t1, who, sa, sb, cw):
    return _respect_pair(st, t0, t1, who, sa, sb, False)


# -------------------------------------------------------------------------------------------- Encouragement
def _encouragement_pray(st, t0, t1, who, sa, sb, cw):
    return [Body(**who(sa, shape="woman", at=st.place(0, 0), facing=st.face(1.0, 35.0),
                       motion=[(-1e9, "stand"), (t0 - 0.5, "kneel", dict(dur=1.7, hands="pray", blend=0.05))],
                       gesture=[(t0 + 0.9, t1 + HOLD_OUT, "bow", dict(amount=12.0))]))]


def _encouragement_shoulder(st, t0, t1, who, sa, sb, cw):
    refs = {}
    kb = who(sb, shape="man", at=st.place(0.25, 0.0), facing=st.face(1.0, 30.0),
             motion=[(-1e9, "kneel", dict(dur=0.01, one=True, hands="pray"))],
             gesture=[(t0 + 0.4, t1 + HOLD_OUT, "bow", dict(amount=14.0))])
    ka = who(sa, shape="woman", at=st.place(-0.30, -0.10), facing=st.face(1.0, 10.0),
             gesture=[(t0, t1 + HOLD_OUT, "hand_on_shoulder",
                       dict(side="R", to=lambda t: refs["b"].where(t, "shoulder.R", raw=True))),
                      (t0 + 0.5, t1 + HOLD_OUT, "bow", dict(amount=12.0))])
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    return [refs["a"], refs["b"]]


def _encouragement_lights(st, t0, t1, who, sa, sb, cw):
    c = np.array(st.place(0.0, -2.2))
    n = cw.pop("n", 26)
    n1 = max(n // 3, 4)
    places = np.concatenate([_ring(c, 2.4, n1, phase=0.3), _ring(c, 3.6, max(n - n1, 4), phase=0.1)])
    cr = _crowd(cw, places=places, facing="center", kinds=("light",), act=dict(t=t0, center=tuple(c), speed=4.0),
                act_end=t1)
    kneeler = Body(**who(sa, shape="woman", at=tuple(c), facing=st.face(1.0, 45.0),
                         motion=[(-1e9, "kneel", dict(dur=0.01, hands="pray"))],
                         gesture=[(t0 - 0.3, t1 + HOLD_OUT, "bow", dict(amount=10.0))]))
    return [cr, kneeler]


# -------------------------------------------------------------------------------------------- Consideration
def _consideration_help_up(st, t0, t1, who, sa, sb, cw):
    a, b = pairs.helped_up(t0 + 0.5, at=st.place(0, 0), facing=st.face(1.0, 15.0), a=who(sa, shape="man"),
                           b=who(sb, shape="woman"), rise=1.6, reach=1.0, apart=0.80)
    return [a, b]


def _consideration_lift_child(st, t0, t1, who, sa, sb, cw):
    a, c = pairs.child_into_arms(t0 + 0.4, at=st.place(0, 0), facing=st.face(1.0, 25.0), adult=who(sa, shape="woman"),
                                 child=who(sb, shape="child"), lift=1.0, until=t1 + HOLD_OUT)
    return [a, c]


# ----------------------------------------------------------------------------------------------- Compliment
def _compliment_applause(st, t0, t1, who, sa, sb, cw):
    c = np.array(st.place(0.0, -1.8))
    n = cw.pop("n", 24)
    places = _ring(c, 2.6, n, gap_dir=np.radians(st.view), gap=0.5, phase=0.2)
    cr = _crowd(cw, places=places, facing="center", kinds=(("clap", 2.0), ("cheer", 1.0)),
                act=dict(t=t0 - 0.2, dur=0.8), act_end=t1)
    star = Body(**who(sa, shape="woman", at=tuple(c), facing=st.view - 15.0,
                      gesture=[(t0 + 0.3, t1 + HOLD_OUT, "hand_on_heart", dict(side="R", bow=6.0)),
                               (t0 + 0.5, t1 + HOLD_OUT, "look_up", dict(amount=10.0))]))
    return [cr, star]


def _compliment_twirl(st, t0, t1, who, sa, sb, cw):
    return [Body(**who(sa, shape="woman", garment="dress", at=st.place(0, 0), facing=st.view - 30.0,
                       motion=[(-1e9, "stand"), (t0 - 0.2, "twirl", dict(blend=0.5)),
                               (t1 + 0.3, "stand", dict(blend=0.9))]))]


def _compliment_raise(st, t0, t1, who, sa, sb, cw):
    a, b = pairs.hands(who(sa, shape="woman", at=st.place(-0.27, 0.0), facing=st.view - 8.0,
                           gesture=[(t0 + 0.5, t1 + HOLD_OUT, "look_up", dict(amount=14.0))]),
                       who(sb, shape="man", at=st.place(0.27, 0.0), facing=st.view + 8.0,
                           gesture=[(t0 + 0.25, t1 + HOLD_OUT, "raise_hand", dict(side="R", palm="fwd", fingers="spread")),
                                    (t0 + 0.4, t1 + HOLD_OUT, "look_up", dict(amount=10.0))]),
                       t0, t1 + HOLD_OUT, raised=True)
    return [a, b]


def _compliment_cheer(st, t0, t1, who, sa, sb, cw):
    n = cw.pop("n", 40)
    return [_crowd(cw, places=_field(st, n, 2.0, 12.0, 10.0, seed=cw["seed"]), facing=st.view,
                   kinds=(("cheer", 2.0), ("clap", 1.0)), act=dict(t=t0, dur=0.7), act_end=t1)]
