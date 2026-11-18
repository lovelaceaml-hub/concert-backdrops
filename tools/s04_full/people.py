"""Song 04 full backdrop: the people of light (Claude Final v1 bodies, warm gold glitter, whole, no faces).

Two sisters (two women: every touch in this song is between them) in three segments, each a fresh pair of
bodies joined at a dissolve or a bloom of light, so a render chunk anywhere warms up quickly:

    VERSE 1 + CHORUS 1 (15.0 to 103.8)
        apart on two shores, half turned from each other; the first turns and sees (31), a hand on her heart;
        APOLOGY (40.8 to 50.4): both open hands offered toward her sister, head a little bowed; she crosses
        first (51.8); her hand offered (56.4); the other's hand comes to rest in it; she kneels (61) and
        bows; the other lays a hand on her head (64.5); chorus 1: she is helped up (75.2), they turn side by
        side toward the low sun and hold hands in the golden breath; at the drop they dissolve into sparks
    VERSE 2 (104.0 to 147.0), from the hurt sister's side
        GRATITUDE (106.2 to 115.0): the hurt sister lays a hand on her heart as her sister waits across the
        ice, then walks to her; the embrace (117.4) and INCLUSIVENESS (118 to 127.2) while they hold each other
    FINAL CHORUS (145.0 to 214.5)
        side by side, hand in hand, facing the sun; people of light gather round on the water (166 to 178):
        families, an older couple, friends, none touching; all dissolve into rising sparks (203 to 213),
        the sisters last
"""
import numpy as np

import reference  # noqa: F401
from nine_reference_p3d import master_acting  # noqa: F401
from nine_reference_p3d import pairs
from nine_reference_p3d.body import Body

import song04 as S

LOOK = dict(name="glitter", seams=0.6)
PTS = 70000


def _common(gold, seed, show, hair, **kw):
    d = dict(shape="woman", garment="dress", hair=hair, look=LOOK, color=gold[0], color2=gold[1],
             points=PTS, show=show, fade=0.5, seed=seed, bright=1.7, wind=(0.15, 0.0, -0.1))
    d.update(kw)
    return d


def _verse1():
    T = S.T
    show = (15.0, 103.8)
    eff = lambda t0: [dict(kind="form", t=t0, dur=2.2), dict(kind="dissolve", t=T["drop"] - 0.6, dur=2.2)]
    # the first sister walks from her shore and stops a respectful step from her sister
    walk_keys = [(-1e9, "stand", {}), (T["cross"], "walk", dict(speed=0.5, blend=0.7)),
                 (T["arrive"] - 0.45, "stand", dict(blend=0.9))]
    from nine_reference_p3d import actor as act
    probe = act.Actor("woman", None, at=(0.0, 0.0), facing=90.0, motion=walk_keys, start=show[0])
    walked = float(probe.travel(T["arrive"] + 1.5)[0] - probe.travel(T["cross"] - 0.05)[0])
    ax = S.MEET[0] - walked
    motion_a = walk_keys + [(T["kneel"], "kneel", dict(one=True, dur=1.6, blend=0.6)),
                            (T["rise"], "rise", dict(dur=1.8, one=True, blend=0.05))]
    facing_a = [(0.0, 235.0), (T["see"], 235.0), (T["see"] + 2.6, 90.0), (T["rise"] + 2.4, 90.0),
                (T["rise"] + 5.0, S.SUN_AZ)]
    facing_b = [(0.0, 125.0), (56.8, 125.0), (59.6, 250.0), (63.0, 270.0), (T["rise"] + 2.4, 270.0),
                (T["rise"] + 5.0, S.SUN_AZ)]
    ka = _common(S.GOLD_A, 21.0, show, "bun", at=(ax, 0.0), facing=facing_a, motion=motion_a, effects=eff(15.6))
    kb = _common(S.GOLD_B, 22.0, show, "long", at=(S.B0[0], 0.0), facing=facing_b, effects=eff(16.6))
    refs = {}
    px = dict(a=pairs._proxy(ka), b=pairs._proxy(kb))
    # the grips are worked out on the plain stand-ins (no gestures, no living hands), so no body ever aims at
    # itself (that would recurse); they stand and move exactly as the raw bodies do
    sh_a = lambda tt: px["a"].where(tt, "shoulder.R")
    sh_b = lambda tt: px["b"].where(tt, "shoulder.R")
    k = px["a"].rig.height / 1.6

    def grip(tt):
        pa, pb = sh_a(tt), sh_b(tt)
        g = 0.5 * (pa + pb)
        g[1] = 0.5 * (pa[1] + pb[1]) - 0.36 * k
        return g

    sb_l = lambda tt: px["b"].where(tt, "shoulder.L")
    crown_a = lambda tt: px["a"].where(tt, "crown")
    fwd = S.SUN_DIR

    def side_grip(tt):
        # side by side facing the sun: the inner hands meet low between them, a little forward
        pa, pb = sh_a(tt), sb_l(tt)
        g = 0.5 * (pa + pb) + 0.10 * fwd
        g[1] = 0.5 * (pa[1] + pb[1]) - 0.62 * k
        return g

    ga = [(T["see"] + 0.8, 39.6, "hand_on_heart", dict(side="L")),
          (40.0, 51.0, "open_hands", {}),
          (T["offer"], T["rise"] + 2.6, "handshake", dict(side="R", to=grip, grip=1.0, ease=0.9)),
          (T["kneel"] + 0.4, T["rise"] - 0.2, "bow", {}),
          (T["rise"] + 3.4, 104.0, "handshake", dict(side="R", to=side_grip, grip=1.0, ease=1.0, look=False,
                                                     lean=0.0))]
    gb = [(T["offer"] + 2.0, T["rise"] + 2.6, "handshake", dict(side="R", to=grip, grip=1.0, ease=1.2)),
          (T["bless"], T["rise"] - 0.4, "hand_on_shoulder", dict(side="L", to=crown_a, ease=1.4)),
          (T["rise"] + 3.4, 104.0, "handshake", dict(side="L", to=side_grip, grip=1.0, ease=1.0, look=False,
                                                     lean=0.0))]
    ka["gesture"], kb["gesture"] = ga, gb
    refs["a"] = Body(**ka)
    refs["b"] = Body(**kb)
    pairs._built(refs["a"], refs["b"])
    return refs["a"], refs["b"]


def _verse2():
    T = S.T
    show = (104.0, 147.2)
    a = _common(S.GOLD_A, 31.0, show, "bun",
                effects=[dict(kind="form", t=104.2, dur=2.0), dict(kind="dissolve", t=145.0, dur=2.0)])
    b = _common(S.GOLD_B, 32.0, show, "long",
                gesture=[(T["gratitude"][1] - 0.6, T["gratitude"][2] + 0.6, "hand_on_heart", dict(side="R"))],
                wash=dict(color=S.ROSE, amount=lambda t: 0.25 * S._sc(T["hug"], T["hug"] + 6.0, t)),
                effects=[dict(kind="form", t=104.6, dur=2.0), dict(kind="dissolve", t=145.0, dur=2.0)])
    return _embrace(T["hug"], at=(-0.15, 0.0), facing=270.0, a=a, b=b, approach=3.4, speed=0.6)


def _embrace(t, at, facing, a, b, gap=0.34, approach=0.0, speed=0.9, ease=1.1, side=0.085):
    """pairs.embrace ("mixed" hold: a's arms over b's shoulders, b's round a's back), with every contact
    point worked out on gesture-free stand-ins: the library version has each body aim at the other's live
    body, a chain that grows with time since the embrace began and overflows in a long hold."""
    c = pairs._xz(at)
    d = pairs._dir(facing)
    left = pairs._dir(facing + 90.0)
    ka = pairs._kw(a, shape="woman", facing=facing)
    kb = pairs._kw(b, shape="woman", facing=facing + 180.0)
    for kw, sgn in ((ka, -1.0), (kb, 1.0)):
        walked, keys = pairs._walk_in(kw["shape"], kw.get("height"), t - 0.15, approach, speed, kw.get("show"))
        place = c + d * sgn * (0.5 * gap + walked) - left * sgn * side
        kw.setdefault("at", (place[0], place[2]))
        if keys and "motion" not in kw:
            kw["motion"] = keys
    px = dict(a=pairs._proxy(ka), b=pairs._proxy(kb))
    on = lambda key, place: (lambda tt: px[key].where(tt, place))
    pairs._gest(ka, (t, 1e9, "embrace", dict(to=on("b", "blade.R"), to2=on("b", "blade.L"), head="L", ease=ease)))
    bl, br = on("a", "blade.L"), on("a", "blade.R")
    k = px["a"].rig.height / 1.6
    tb = (lambda tt: pairs._low_back(bl(tt), br(tt), k, "R"), lambda tt: pairs._low_back(bl(tt), br(tt), k, "L"))
    pairs._gest(kb, (t + 0.12, 1e9, "embrace", dict(to=tb[0], to2=tb[1], head="L", ease=ease)))
    ra, rb = Body(**ka), Body(**kb)
    pairs._built(ra, rb)
    return ra, rb


def _final():
    T = S.T
    show = (145.0, 214.5)
    a = _common(S.GOLD_A, 41.0, show, "bun", at=(-0.33, 0.1), facing=S.SUN_AZ - 8.0,
                effects=[dict(kind="form", t=145.4, dur=2.0), dict(kind="dissolve", t=T["leave"][1] - 2.4, dur=3.0)])
    b = _common(S.GOLD_B, 42.0, show, "long", at=(0.33, -0.1), facing=S.SUN_AZ - 8.0,
                wash=dict(color=S.ROSE, amount=0.25),
                effects=[dict(kind="form", t=145.8, dur=2.0), dict(kind="dissolve", t=T["leave"][1] - 2.2, dur=3.0)])
    return _hold_hands(a, b, 148.0, 1e9)


def _hold_hands(ka, kb, t0, t1):
    """a (on the left) and b side by side hold their inner hands (a's right, b's left), worked out on
    gesture-free stand-ins (the library's pairs.hands aims a body at itself and recurses here)."""
    px = dict(a=pairs._proxy(ka), b=pairs._proxy(kb))
    k = px["a"].rig.height / 1.6
    face = np.radians(float(ka["facing"]))
    fwd = np.array([np.sin(face), 0.0, np.cos(face)])

    def grip(tt):
        pa, pb = px["a"].where(tt, "shoulder.R"), px["b"].where(tt, "shoulder.L")
        g = 0.5 * (pa + pb) + 0.10 * fwd
        g[1] = 0.5 * (pa[1] + pb[1]) - 0.62 * k
        return g

    ka = dict(ka, gesture=list(ka.get("gesture", [])) + [(t0, t1, "handshake", dict(side="R", to=grip, grip=1.0,
                                                                                       ease=1.0, look=False, lean=0.0))])
    kb = dict(kb, gesture=list(kb.get("gesture", [])) + [(t0, t1, "handshake", dict(side="L", to=grip, grip=1.0,
                                                                                       ease=1.0, look=False, lean=0.0))])
    a, b = Body(**ka), Body(**kb)
    pairs._built(a, b)
    return a, b


GATHER = [  # (shape, angle from the sun line in degrees, radius m, gold, hair, extra)
    ("woman", -78.0, 6.2, ("#ffcf7a", "#fff2d0"), "covered", {}),
    ("child", -62.0, 5.6, ("#ffd890", "#fff6e0"), "bob", {}),
    ("man", -40.0, 7.0, ("#f4b45a", "#ffe2a8"), "short", {}),
    ("woman", -18.0, 7.6, ("#ffc664", "#fff0c8"), "tied", dict(stoop=0.35)),
    ("man", 16.0, 7.6, ("#f2a640", "#ffdc96"), "cap", dict(stoop=0.35)),
    ("woman", 38.0, 7.0, ("#ffd27a", "#fff4d6"), "bun", {}),
    ("man", 60.0, 5.8, ("#f6b552", "#ffe6b0"), "short", {}),
    ("child", 76.0, 5.4, ("#ffd890", "#fff6e0"), "cap", {}),
]


def _gathering():
    T = S.T
    out = {}
    base = np.degrees(np.arctan2(S.SUN_DIR[0], S.SUN_DIR[2]))
    n = len(GATHER)
    for i, (shape, ang, rad, gold, hair, extra) in enumerate(GATHER):
        a = np.radians(base + ang)
        x, z = np.sin(a) * rad, np.cos(a) * rad
        face = float(np.degrees(np.arctan2(-x, -z)))
        t_form = T["people"][0] + (T["people"][1] - T["people"][0]) * (abs(ang) / 80.0)
        t_go = T["leave"][0] + 4.0 * (1.0 - abs(ang) / 80.0)
        out[f"gather {i}"] = Body(shape, at=(float(x), float(z)), facing=face, garment=None, hair=hair, look=LOOK,
                                  color=gold[0], color2=gold[1], points=26000, bright=1.6, seed=60.0 + i,
                                  show=(T["people"][0] - 0.5, T["leave"][1] + 1.0), fade=0.4,
                                  gesture=[(t_form + 2.0, 300.0, "sway", dict(period=3.4 + 0.3 * (i % 3),
                                                                              amount=2.5, phase=0.7 * i))],
                                  effects=[dict(kind="form", t=t_form, dur=2.4),
                                           dict(kind="dissolve", t=t_go, dur=3.0)], **extra)
    return out


_CAST = {}


def cast():
    if not _CAST:
        a1, b1 = _verse1()
        a2, b2 = _verse2()
        a3, b3 = _final()
        _CAST.update({"sister a v1": a1, "sister b v1": b1, "sister a v2": a2, "sister b v2": b2,
                      "sister a end": a3, "sister b end": b3})
        _CAST.update(_gathering())
    return _CAST
