"""Song 04 full backdrop, version 2: the people of light (Claude Final v1 bodies, warm gold glitter, whole,
clothed in garments of light, faces soft glowing shapes with no features).

Two sisters (two women: every touch between adults in this song is between them; the only other touch is a
parent holding a child's hand). Each stretch is its own pair of bodies, re-formed inside a moment of light (the
warm beam, the golden breath) so a render range anywhere starts quickly:

    PAIR 1 (13.5 to 57.6)  apart on the ice, half turned from each other. 26.4 the first turns to her sister;
        APOLOGY (29.0 to 38.6): head bowed, open hands low. 39.4 she crosses first; 41.0 offers her hand, her
        sister takes it (41.9); 43.4 she kneels ("truly humbled"); 47.5 her sister turns to her and lays a hand
        on her bowed head (49.0); 52.8 a hand on her own heart ("I thank you", acted only); 54.8 lifts her up
    PAIR 2 (56.0 to 86.0)  the embrace (59.0) held while INCLUSIVENESS reads (58.8 to 67.8), swaying a little,
        through the start of chorus 1 into the golden breath
    PAIR 3 (84.0 to 128.5) side by side facing the low sun, holding hands, through chorus 1 and the interlude;
        they become rings of light (124.5)
    THE MANY (131 to 216)  people of light form one by one on the thawing lake in a wide open ring (verse 3,
        then the final section); a mother and a father each hold a child's hand; nobody else touches
    PAIR 4 (180.5 to 216)  the two sisters again, at the centre of the ring, hand in hand; they dissolve last
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
             points=PTS, show=show, fade=0.5, seed=seed, bright=3.0, wind=(0.15, 0.0, -0.1))
    d.update(kw)
    return d


def _pair1():
    T = S.T
    show = (13.5, T["swap1"][1])
    eff_a = [dict(kind="form", t=T["form"], dur=2.4), dict(kind="dissolve", t=T["swap1"][0], dur=1.6)]
    eff_b = [dict(kind="form", t=T["form"] + 0.8, dur=2.4), dict(kind="dissolve", t=T["swap1"][0], dur=1.6)]
    walk_keys = [(-1e9, "stand", {}), (T["cross"], "walk", dict(speed=0.45, blend=0.7)),
                 (T["arrive"] - 0.45, "stand", dict(blend=0.9))]
    from nine_reference_p3d import actor as act
    probe = act.Actor("woman", None, at=(0.0, 0.0), facing=90.0, motion=walk_keys, start=show[0])
    walked = float(probe.travel(T["arrive"] + 1.5)[0] - probe.travel(T["cross"] - 0.05)[0])
    ax = S.MEET[0] - walked
    motion_a = walk_keys + [(T["kneel"], "kneel", dict(one=True, dur=1.6, blend=0.6)),
                            (T["rise"], "rise", dict(dur=1.8, one=True, blend=0.05))]
    facing_a = [(0.0, 235.0), (T["see"], 235.0), (T["see"] + 2.4, 90.0), (show[1], 90.0)]
    facing_b = [(0.0, 125.0), (47.0, 125.0), (49.4, 270.0), (show[1], 270.0)]
    ka = _common(S.GOLD_A, 21.0, show, "bun", at=(ax, 0.0), facing=facing_a, motion=motion_a, effects=eff_a)
    kb = _common(S.GOLD_B, 22.0, show, "long", at=(S.B0[0], 0.0), facing=facing_b, effects=eff_b)
    px = dict(a=pairs._proxy(ka), b=pairs._proxy(kb))
    k = px["a"].rig.height / 1.6

    def grip(tt):
        pa, pb = px["a"].where(tt, "shoulder.R"), px["b"].where(tt, "shoulder.R")
        g = 0.5 * (pa + pb)
        g[1] = 0.5 * (pa[1] + pb[1]) - 0.36 * k
        return g

    crown_a = lambda tt: px["a"].where(tt, "crown")
    ga = [(T["apology"][0] + 0.4, T["apology"][2] + 0.6, "open_hands", dict(bow=24.0)),
          (T["apology"][0] + 0.7, T["apology"][2] + 0.6, "bow", dict(amount=16.0)),
          (T["offer"], T["swap1"][1], "handshake", dict(side="R", to=grip, grip=1.0, ease=0.9)),
          (T["kneel"] + 0.4, T["rise"] - 0.2, "bow", {})]
    gb = [(T["take"], T["swap1"][1], "handshake", dict(side="R", to=grip, grip=1.0, ease=1.2)),
          (T["bless"], T["thank"] - 0.2, "hand_on_shoulder", dict(side="L", to=crown_a, ease=1.4)),
          (T["thank"] + 0.2, T["rise"] + 0.6, "hand_on_heart", dict(side="L"))]
    ka["gesture"], kb["gesture"] = ga, gb
    a, b = Body(**ka), Body(**kb)
    pairs._built(a, b)
    return a, b


def _pair2():
    T = S.T
    show = (T["swap1"][0], T["swap2"][1])
    eff = [dict(kind="form", t=T["swap1"][0], dur=1.6), dict(kind="dissolve", t=T["swap2"][0], dur=2.0)]
    a = _common(S.GOLD_A, 31.0, show, "bun", effects=eff,
                gesture=[(T["hug"] + 2.5, 300.0, "sway", dict(period=4.2, amount=1.5))])
    b = _common(S.GOLD_B, 32.0, show, "long", effects=list(eff),
                wash=dict(color=S.ROSE, amount=lambda t: 0.25 * S._sc(T["hug"], T["hug"] + 6.0, t)))
    return _embrace(T["hug"], at=(S.EMB[0], S.EMB[2]), facing=90.0, a=a, b=b, approach=0.9, speed=0.35)


def _embrace(t, at, facing, a, b, gap=0.34, approach=0.0, speed=0.9, ease=1.1, side=0.085):
    """pairs.embrace ("mixed" hold: a's arms over b's shoulders, b's round a's back), with every contact
    point worked out on gesture-free stand-ins (the library version chains body on body and overflows)."""
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


def _side(center, face, gold_a, gold_b, seeds, show, eff_a, eff_b, t0, wash=0.25):
    """Two sisters side by side facing `face`, holding their inner hands from t0."""
    f = np.radians(face)
    right = np.array([np.cos(f), 0.0, -np.sin(f)])       # the right hand side of someone facing `face`
    pa = np.asarray(center) - 0.30 * right
    pb = np.asarray(center) + 0.30 * right
    a = _common(gold_a, seeds[0], show, "bun", at=(float(pa[0]), float(pa[2])), facing=face, effects=eff_a)
    b = _common(gold_b, seeds[1], show, "long", at=(float(pb[0]), float(pb[2])), facing=face, effects=eff_b,
                wash=dict(color=S.ROSE, amount=wash))
    return _hold_hands(a, b, t0, 1e9)


def _hold_hands(ka, kb, t0, t1):
    """a (on the left) and b side by side hold their inner hands (a's right, b's left), worked out on
    gesture-free stand-ins."""
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


def _pair3():
    T = S.T
    show = (T["swap2"][0], T["leave1"][1])
    eff_a = [dict(kind="form", t=T["swap2"][0] + 0.2, dur=2.0), dict(kind="dissolve", t=T["leave1"][0], dur=3.0)]
    eff_b = [dict(kind="form", t=T["swap2"][0] + 0.5, dur=2.0), dict(kind="dissolve", t=T["leave1"][0] + 0.3,
                                                                      dur=3.0)]
    return _side(S.PAIR, S.SUN_AZ - 8.0, S.GOLD_A, S.GOLD_B, (41.0, 42.0), show, eff_a, eff_b, T["swap2"][1])


def _pair4():
    T = S.T
    show = (T["final"] + 0.5, T["leave"][1])
    eff_a = [dict(kind="form", t=T["final"] + 0.5, dur=2.4), dict(kind="dissolve", t=T["leave"][1] - 3.6, dur=3.0)]
    eff_b = [dict(kind="form", t=T["final"] + 0.9, dur=2.4), dict(kind="dissolve", t=T["leave"][1] - 3.4, dur=3.0)]
    return _side(S.HUB, S.SUN_AZ - 20.0, S.GOLD_A, S.GOLD_B, (51.0, 52.0), show, eff_a, eff_b, T["final"] + 3.0)


# The many: (shape, angle round the ring from the sun line in degrees, radius m, gold, hair, extra). The front
# of the ring (toward the audience) stays open so nobody stands in the bottom third.
GATHER = [
    ("man", -80.0, 4.6, ("#f4b45a", "#ffe2a8"), "short", {}),
    ("woman", -58.0, 4.8, ("#ffd27a", "#fff4d6"), "bun", {}),
    ("child", -52.0, 4.7, ("#ffd890", "#fff6e0"), "bob", {}),
    ("man", -30.0, 5.0, ("#f2a640", "#ffdc96"), "cap", dict(stoop=0.35)),
    ("woman", -8.0, 5.0, ("#ffc664", "#fff0c8"), "tied", dict(stoop=0.35)),
    ("woman", 14.0, 5.0, ("#ffcf7a", "#fff2d0"), "long", {}),
    ("man", 36.0, 4.8, ("#f6b552", "#ffe6b0"), "short", {}),
    ("child", 42.0, 4.7, ("#ffd890", "#fff6e0"), "cap", {}),
    ("man", 62.0, 4.8, ("#f4b45a", "#ffe2a8"), "short", {}),
    ("woman", 82.0, 4.6, ("#ffd27a", "#fff4d6"), "bun", {}),
]
# a parent holds a child's hand: (parent index, child index)
FAMILIES = ((1, 2), (6, 7))


def _gathering():
    T = S.T
    out = {}
    base = float(np.degrees(np.arctan2(S.SUN_DIR[0], S.SUN_DIR[2])))
    n = len(GATHER)
    order = sorted(range(n), key=lambda i: abs(GATHER[i][1]))      # the back of the ring first, then the sides
    kw_all = {}
    for rank, i in enumerate(order):
        shape, ang, rad, gold, hair, extra = GATHER[i]
        a = np.radians(base + ang)
        x, z = S.HUB[0] + np.sin(a) * rad, S.HUB[2] + np.cos(a) * rad
        face = float(np.degrees(np.arctan2(S.HUB[0] - x, S.HUB[2] - z)))
        if rank < 5:          # verse 3: the first five
            t_form = T["people"][0] + (T["people"][1] - T["people"][0]) * rank / 5.0
        else:                 # the final section: the ring closes
            t_form = T["ring"][0] + (T["ring"][1] - T["ring"][0]) * (rank - 5) / 5.0
        t_go = T["leave"][0] + 3.0 * (abs(ang) / 110.0)
        kw_all[i] = dict(shape=shape, at=(float(x), float(z)), facing=face, garment=None, hair=hair, look=LOOK,
                         color=gold[0], color2=gold[1], points=26000, bright=3.4, seed=60.0 + i,
                         show=(t_form - 0.5, T["leave"][1] + 0.5), fade=0.4,
                         gesture=[(t_form + 2.5, 400.0, "sway", dict(period=3.6 + 0.3 * (i % 3), amount=2.0,
                                                                      phase=0.7 * i))],
                         effects=[dict(kind="form", t=t_form, dur=2.4), dict(kind="dissolve", t=t_go, dur=3.0)],
                         **extra)
    for p, c in FAMILIES:
        # the child forms with the parent; they hold hands (parent's inner hand, child's outer hand)
        kw_all[c]["effects"][0]["t"] = kw_all[p]["effects"][0]["t"] + 0.3
        kw_all[c]["show"] = (kw_all[p]["show"][0], kw_all[c]["show"][1])
        t0 = kw_all[p]["effects"][0]["t"] + 2.6
        pp, cc = pairs._proxy(kw_all[p]), pairs._proxy(kw_all[c])

        def grip(tt, pp=pp, cc=cc):
            a, b = pp.where(tt, "wrist.R"), cc.where(tt, "wrist.L")
            g = 0.5 * (a + b)
            g[1] = min(a[1], b[1]) + 0.02
            return g
        kw_all[p]["gesture"] = [(t0, 400.0, "handshake", dict(side="R", to=grip, grip=1.0, ease=1.2, look=False,
                                                               lean=0.0))]
        kw_all[c]["gesture"] = [(t0, 400.0, "handshake", dict(side="L", to=grip, grip=1.0, ease=1.2, look=False,
                                                               lean=0.0))]
    for i in range(n):
        out[f"gather {i}"] = Body(**kw_all[i])
    return out


_CAST = {}


def cast():
    if not _CAST:
        a1, b1 = _pair1()
        a2, b2 = _pair2()
        a3, b3 = _pair3()
        a4, b4 = _pair4()
        _CAST.update({"sister a v1": a1, "sister b v1": b1, "sister a hug": a2, "sister b hug": b2,
                      "sister a sun": a3, "sister b sun": b3, "sister a end": a4, "sister b end": b4})
        _CAST.update(_gathering())
    return _CAST
