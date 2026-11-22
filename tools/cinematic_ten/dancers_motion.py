"""Original complete performance scores on the project's native human rig.

The uploaded videos inform the order of fan sweeps, levels and ensemble canon.
The obscured source feet are not used as measured contacts. These independent
support targets are authored in metres and solved after the torso and hands.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.interpolate import PchipInterpolator

from p3d import bodymath as bm
from tools.concert_fan.performance import TrioPerformance, Step

DEG = np.pi / 180.0


def curve(times, values):
    return PchipInterpolator(np.asarray(times, float), np.asarray(values, float), axis=0)


class DanceScore(TrioPerformance):
    """Twenty seconds of support, weight shift, travel, gesture and recovery."""

    def __init__(self, actor, mode="solo", role=0, delay=0.0):
        super().__init__(actor, role=0, duration=20.0)
        self.mode, self.variant, self.delay = mode, int(role), float(delay)
        self.name = mode + str(role)
        ts = (0, 1.2, 2.6, 4.0, 5.3, 6.7, 8.0, 9.3, 10.6, 12.0,
              13.3, 14.6, 16.0, 17.3, 18.6, 19.5, 20.0, 21.0)
        # Three phrases: a rising spiral, a broad lateral opening, a resolved
        # offering. The pelvis changes height with the preparation and rebound.
        right = [(-.30, 1.02, .31), (-.62, 1.14, .15), (-.48, 1.62, .13),
                 (-.12, 1.85, .12), (-.50, 1.43, .19), (-.57, .98, .25),
                 (-.27, 1.13, .40), (-.60, 1.40, .18), (-.37, 1.77, .10),
                 (-.08, 1.83, .15), (-.51, 1.36, .20), (-.59, 1.02, .20),
                 (-.44, 1.53, .13), (-.29, 1.80, .15), (-.53, 1.39, .25),
                 (-.43, 1.29, .26), (-.43, 1.29, .26), (-.43, 1.29, .26)]
        left = [( .28, 1.10, .28), ( .52, 1.37, .17), ( .58, 1.20, .13),
                ( .45, 1.58, .10), ( .13, 1.78, .16), ( .49, 1.40, .14),
                ( .59, 1.12, .20), ( .36, 1.03, .30), ( .58, 1.32, .18),
                ( .45, 1.55, .18), ( .13, 1.78, .15), ( .51, 1.41, .18),
                ( .58, 1.19, .13), ( .37, 1.68, .15), ( .51, 1.39, .25),
                ( .43, 1.29, .26), ( .43, 1.29, .26), ( .43, 1.29, .26)]
        path_t = (0, 2.6, 5.3, 8, 10.6, 13.3, 16, 18.6, 19.5, 20, 21)
        paths = ((0, 0), (-.32, .08), (-.64, -.05), (-.30, -.34),
                 (.20, -.30), (.57, -.05), (.28, .26), (0, .30), (0, .30), (0, .30), (0, .30))
        yaws = (-12, 25, 80, 135, 60, -28, -42, -12, 0, 0, 0)
        drop = (.065, .12, .045, .035, .11, .16, .07, .12, .035,
                .045, .12, .16, .05, .025, .08, .07, .07, .07)
        lean = (3, 10, -6, -9, 2, 17, 8, 4, -7, -10, 1, 15, -3, -7, 4, 3, 3, 3)
        bank = (10, -35, -15, 20, 55, 38, -20, -35, -10, 35, 60, 22, -18, 15, 20, 10, 10, 10)
        if mode == "solo":
            # Keep a clean facial silhouette as the late orbit meets this
            # three-quarter turn: one fan high and one below the shoulder.
            left[12] = (.58, .88, .18)
            left[13] = (.51, 1.18, .18)
        if mode == "ensemble":
            side = np.sign(role - 2)
            amount = .40 + .18 * abs(role - 2)
            paths = [(0, 0), (-side * amount, .30), (-side * amount * .65, .57),
                     (side * amount * .6, .18), (side * amount, -.18),
                     (side * amount * .4, .08), (-side * amount * .6, .40),
                     (-side * amount * .45, .30), (-side * amount * .45, .30),
                     (-side * amount * .45, .30), (-side * amount * .45, .30)]
            yaws = [side * x for x in (10, 25, 50, 15, -35, -48, -12, 0, 0, 0, 0)]
            # The two wrists create complementary petals, not mirrored trails.
            for j in (3, 8, 9, 13):
                left[j] = (.29, 1.77 if j != 8 else 1.67, .14)
                right[j] = (-.29, 1.77 if j != 8 else 1.67, .14)
            for j in (14, 15, 16, 17):
                left[j] = (.44, 1.54, .17)
                right[j] = (-.44, 1.54, .17)
        if mode == "script":
            # One moving hand draws curved strokes while the other balances.
            right = [(-.30, 1.12, .42), (-.56, 1.44, .25), (-.20, 1.74, .25),
                     (.24, 1.47, .35), (-.10, 1.09, .47), (-.58, .85, .32),
                     (-.50, 1.38, .30), (-.13, 1.80, .22), (.31, 1.41, .32),
                     (-.08, 1.06, .48), (-.61, 1.24, .27), (-.36, 1.70, .25),
                     (.20, 1.57, .34), (-.12, 1.28, .48), (-.52, 1.65, .28),
                     (-.40, 1.51, .33), (-.40, 1.51, .33), (-.40, 1.51, .33)]
            left = [( .38, 1.10, .23), (.54, 1.24, .14), (.40, 1.22, .15),
                    (.59, 1.34, .12), (.49, 1.43, .12), (.40, 1.58, .12),
                    (.31, 1.12, .30), (.55, 1.24, .14), (.58, 1.36, .13),
                    (.46, 1.55, .14), (.49, 1.29, .20), (.36, 1.24, .24),
                    (.58, 1.31, .13), (.52, 1.51, .14), (.48, 1.57, .22),
                    (.45, 1.50, .25), (.45, 1.50, .25), (.45, 1.50, .25)]
            paths = [(0, 0), (-.30, .05), (-.50, .13), (-.26, -.08),
                     (.20, -.16), (.50, -.12), (.23, .06), (0, .10),
                     (0, .10), (0, .10), (0, .10)]
            yaws = (-12, 12, 35, -15, -30, 25, 30, 0, 0, 0, 0)
        self._path, self._yaw = curve(path_t, paths), curve(path_t, yaws)
        self._palms = {"R": curve(ts, right), "L": curve(ts, left)}
        self._drop, self._lean = curve(ts, drop), curve(ts, lean)
        self._fan_bank = curve(ts, bank)
        self._wrist = curve(ts, (32, 65, 12, -15, -32, 72, 50, 30, 10, -15, -40, 62, 30, -10, 50, 42, 42, 42))
        self._head_turn = curve(path_t, (12, -10, -22, -28, 20, 20, 18, 0, 0, 0, 0))
        self._head_up = curve(ts, (2, 7, 14, 19, 10, -10, 3, 7, 15, 17, 8, -6, 12, 18, 10, 8, 8, 8))
        # Twenty-four alternating, explicit supports cover nearly the entire
        # film, ending with a full double-support arrival rather than a freeze.
        self.initial_feet = {}
        self.initial_yaw = {}
        yaw0 = float(self._yaw(0))
        for side, sign in (("L", 1), ("R", -1)):
            off = self.neutral_feet[side] - self._neutral_mid
            off[0] += sign * .024 * self.scale
            p = bm.qrot(bm.qy(yaw0 * DEG), off) + self._neutral_mid
            p[1] += self.flat_lift
            self.initial_feet[side], self.initial_yaw[side] = p, yaw0 + sign * 5
        latest = {s: p.copy() for s, p in self.initial_feet.items()}
        latest_yaw = self.initial_yaw.copy()
        steps = []
        for k in range(24):
            start, end = .10 + .80 * k, .76 + .80 * k
            side, sign = ("R", -1) if k % 2 == 0 else ("L", 1)
            centre, yaw = self._path(end) * self.scale, float(self._yaw(end))
            off = self.neutral_feet[side] - self._neutral_mid
            off[0] += sign * .024 * self.scale
            p = bm.qrot(bm.qy(yaw * DEG), off) + self._neutral_mid
            p[[0, 2]] += centre
            p[1] += self.flat_lift
            steps.append(Step(start, end, side, tuple(latest[side]), tuple(p), latest_yaw[side], yaw + sign * 5))
            latest[side], latest_yaw[side] = p, yaw + sign * 5
        self.steps = tuple(steps)

    def score_time(self, t):
        return float(np.clip((float(t) - self.delay) * 20 / (20 - self.delay), 0, 20))

    def pose(self, t):
        s = self.score_time(t)
        p = self.mo.identity()
        feet, rotations, swing = self.feet(t)
        midpoint = (feet["L"] + feet["R"]) * .5
        p.pos[[0, 2]] = (midpoint - self._neutral_mid)[[0, 2]]
        phase = 0.0 if swing is None else math.sin(np.pi * swing[1])
        if swing is not None:
            planted = "R" if swing[0] == "L" else "L"
            p.pos[[0, 2]] += .28 * phase * (feet[planted] - feet[swing[0]])[[0, 2]]
        p.pos[1] = self.flat_lift - (float(self._drop(s)) + .015 * phase**2) * self.scale
        yaw = float(self._yaw(s))
        roll = 0 if swing is None else (1 if swing[0] == "R" else -1) * 3.5 * phase
        yq = bm.qy(yaw * DEG)
        p.rot = bm.qmul(yq, bm.qz(roll * DEG))
        self.mo._lean(p, 1, fwd=float(self._lean(s)), twist=-.16 * yaw, side=-.65 * roll)
        self.mo._head(p, 1, up=float(self._head_up(s)), turn=float(self._head_turn(s)), tilt=-.5 * roll)
        root = self.rig.neutral_pos[0] + p.pos
        for side, sign in (("L", 1), ("R", -1)):
            target = self._palms[side](s) * self.scale
            palm = root + bm.qrot(yq, target - self.rig.neutral_pos[0])
            angle = float(self._wrist(s)) * (1 if side == "R" else .72)
            fingers = bm.qrot(yq, [sign * math.sin(angle * DEG), math.cos(angle * DEG), .05])
            normal = bm.qrot(yq, [0, 0, 1])
            normal = bm.qrot(bm.qaxis(fingers, (float(self._fan_bank(s)) * (1 if side == "R" else -.7)) * DEG), normal)
            self.mo.hand_to(p, side, palm, fingers, normal, pole=bm.qrot(yq, [sign * .55, -.85, -.28]))
            grip = self.mode != "script"
            self.mo.hand_pose(p, side, dict(curl=(32, 45, 52, 58, 62) if grip else (18, 5, 9, 17, 25), spread=1.2 if grip else 3.5))
        for side, sign in (("L", 1), ("R", -1)):
            self.mo.leg_to(p, side, feet[side], knee=bm.qrot(yq, [sign * .12, 0, 1]), foot=rotations[side])
        p.ground, p.contact = 0.0, None
        return p


def install(body, mode="solo", role=0, delay=0.0):
    actor = body.actor
    if actor._cache:
        raise ValueError("Install choreography before any body sampling")
    score = DanceScore(actor, mode=mode, role=role, delay=delay)
    actor.base_pose, actor.life = score.pose, False
    frame = actor.frame
    actor.frame = lambda t, **kw: frame(round(float(t), 6), **kw)
    actor._cache.clear()
    actor.cinematic_score = score
    return score
