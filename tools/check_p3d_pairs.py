"""Quick check of the people in contact (engine/p3d/pairs.py and acting.py), about two minutes:

    python tools/check_p3d_pairs.py

Builds each pair the way films do (a later `show`, a moving ground, effects that look at a body's pose while it
is being made, a walk-in) and checks that nothing fails while the bodies are built, that an embrace that walks
in stops `gap` apart with the heads beside each other, and that held and helping hands meet. Exits 1 on a
failure.
"""
import os
import sys
import traceback

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
from p3d import acting, pairs  # noqa: E402

FAILS = []


def check(name, cond, detail):
    print("%-4s %s: %s" % ("ok" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def rising(y0, t_up, accel=9.0):
    return lambda t: (0.0, float(y0 + 0.5 * accel * max(t - t_up, 0.0) ** 2), 0.0)


def fx(t):
    # "birds" and "dissolve" ask for the body's pose at their time while the body is being made
    return [dict(kind="shed", t=t + 2.0, n=300), dict(kind="birds", t=t, n=4)]


def run(name, fn):
    try:
        fn()
    except Exception:
        traceback.print_exc()
        check(name, False, "raised")


def embrace():
    a, b = pairs.embrace(12.0, at=(0.0, 0.0), facing=30.0, gap=0.34, approach=1.1, speed=0.8,
                         a=dict(shape="woman", points=3000, frame=rising(2.0, 15.1), effects=fx(13.0),
                                gesture=[(9.0, 10.8, "listen", dict(side="L"))], show=(7.4, 16.4)),
                         b=dict(shape="man", points=3000, frame=rising(2.0, 15.1),
                                effects=[dict(kind="dissolve", t=13.5, dur=1.0, share=0.1)], show=(7.85, 16.4)))
    gap = np.linalg.norm((a.where(12.6, "pelvis", raw=True) - b.where(12.6, "pelvis", raw=True))[[0, 2]])
    heads = np.linalg.norm(a.where(13.5, "head") - b.where(13.5, "head"))
    still = np.linalg.norm((a.where(10.7, "pelvis", raw=True) - a.where(10.0, "pelvis", raw=True))[[0, 2]])
    a.sample(13.0)
    check("embrace walk-in", abs(gap - 0.34) < 0.05, "stops %.3f m apart (gap 0.34)" % gap)
    check("embrace stands before the walk", still < 0.03, "moved %.3f m before t - approach" % still)
    check("embrace heads", heads > 0.16, "heads %.3f m apart (beside each other, not face to face)" % heads)


def hands():
    a, b = pairs.hands(dict(shape="woman", at=(0.0, 0.0), points=3000, effects=fx(44.0), show=(42.1, 54.4),
                            frame=rising(1.0, 60.0)),
                       dict(shape="woman", at=(0.62, 0.0), points=3000, effects=fx(44.5), show=(42.15, 54.4),
                            frame=rising(1.0, 60.0)),
                       42.6, 47.35)
    g = min(np.linalg.norm(a.where(45.0, "palm." + x) - b.where(45.0, "palm." + y)) for x in "LR" for y in "LR")
    a.sample(45.0)
    check("hands held", g < 0.04, "palms %.3f m apart" % g)


def helped_up():
    a, b = pairs.helped_up(30.0, at=(9.0, 0.0), facing=90.0, a=dict(points=3000, effects=fx(30.5)),
                           b=dict(points=3000, effects=fx(31.0)))
    g = np.linalg.norm(a.where(30.6, "palm.R") - b.where(30.6, "palm.R"))
    check("helped up", g < 0.04, "the helping hands %.3f m apart" % g)


def child():
    a, c = pairs.child_into_arms(20.0, at=(5.0, 0.0), adult=dict(points=3000, effects=fx(21.0)),
                                 child=dict(points=2000, effects=fx(21.5)))
    c.sample(21.5)
    check("child into arms", True, "built")


def acted():
    for lab, v in (("Greeting", "turn"), ("Gratitude", "clasp"), ("Inclusiveness", "embrace")):
        sets = acting.perform(lab, 2.0, 5.0, variant=v, style=dict(points=3000, effects=fx(3.5)))
        sets[0].sample(3.6)
        check("acting %s %s" % (lab, v), True, "built")


for n, f in (("embrace", embrace), ("hands", hands), ("helped up", helped_up), ("child", child), ("acting", acted)):
    run(n, f)
print("FAILED: %s" % ", ".join(FAILS) if FAILS else "all passed")
sys.exit(1 if FAILS else 0)
