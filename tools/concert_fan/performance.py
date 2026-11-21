"""Original, time-addressable fan-trio choreography on the approved body rig.

This is an authored adaptation, not motion reconstructed from the three linked
videos and not a new motion-capture recording. The existing mesh, skinning and
cloth engine are unchanged. Every translation is carried by explicit alternating
steps; a supporting foot keeps both its position and its orientation.

Install before sampling a Body. Role 0 leads, role 1 answers and role 2 welcomes.
Roles 0 and 1 hold a fan in their right hand; role 2 uses two open hands.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.interpolate import PchipInterpolator

from p3d import bodymath as bm


DURATION = 20.0
BASE_PLACEMENTS = ((-1.55, 0.0, 0.40), (1.50, 0.0, -0.05), (0.0, 0.0, -1.90))
ROLE_NAMES = ("lead", "answer", "welcome")
DEG = np.pi / 180.0


def _curve(times, values):
    return PchipInterpolator(np.asarray(times, float), np.asarray(values, float), axis=0)


# The three scores share dramatic beats, but not identical poses or a repeated
# capture. Palm coordinates are metres on a 1.65 m woman, before the root turn.
_HAND_TIMES = (0, 1.4, 3.2, 5.1, 7.0, 8.8, 10.6, 12.5, 14.4, 16.3, 18.6, 20, 21)
_RIGHT = (
    ((-.37, 1.11, .24), (-.63, 1.27, .14), (-.44, 1.63, .10),
     (-.21, 1.76, .12), (.02, 1.61, .28), (-.56, 1.24, .24),
     (-.35, 1.12, .27), (-.58, 1.36, .14), (-.33, 1.71, .12),
     (-.13, 1.72, .22), (-.46, 1.31, .24), (-.33, 1.13, .27),
     (-.33, 1.13, .27)),
    ((-.35, 1.15, .28), (-.26, 1.13, .29), (-.53, 1.27, .18),
     (-.55, 1.50, .10), (-.26, 1.74, .13), (.01, 1.62, .26),
     (-.49, 1.30, .24), (-.48, 1.20, .19), (-.56, 1.40, .11),
     (-.32, 1.70, .17), (-.38, 1.37, .25), (-.33, 1.13, .27),
     (-.33, 1.13, .27)),
    ((-.28, 1.12, .30), (-.40, 1.24, .27), (-.55, 1.41, .18),
     (-.44, 1.61, .16), (-.29, 1.36, .33), (-.20, 1.12, .38),
     (-.45, 1.24, .30), (-.59, 1.47, .15), (-.36, 1.69, .15),
     (-.44, 1.52, .22), (-.49, 1.31, .25), (-.34, 1.17, .31),
     (-.34, 1.17, .31)),
)
_LEFT = (
    ((.30, 1.12, .26), (.45, 1.20, .22), (.59, 1.25, .14),
     (.57, 1.16, .16), (.42, 1.56, .19), (.52, 1.34, .20),
     (.29, 1.16, .29), (.50, 1.17, .18), (.60, 1.27, .13),
     (.49, 1.40, .20), (.38, 1.26, .25), (.30, 1.15, .32),
     (.30, 1.15, .32)),
    ((.29, 1.13, .31), (.40, 1.16, .25), (.34, 1.28, .29),
     (.53, 1.19, .20), (.58, 1.31, .13), (.31, 1.61, .20),
     (.51, 1.38, .22), (.37, 1.15, .28), (.53, 1.25, .20),
     (.51, 1.44, .16), (.36, 1.28, .28), (.30, 1.15, .32),
     (.30, 1.15, .32)),
    ((.26, 1.14, .32), (.41, 1.22, .29), (.54, 1.25, .21),
     (.53, 1.19, .20), (.47, 1.42, .23), (.33, 1.19, .34),
     (.48, 1.30, .26), (.58, 1.46, .17), (.38, 1.68, .16),
     (.46, 1.51, .22), (.50, 1.31, .25), (.34, 1.17, .31),
     (.34, 1.17, .31)),
)
_PATH_TIMES = (0, 3, 6, 9, 12, 16, 19.4, 20, 21)
_PATHS = (
    ((0, 0), (-.17, .08), (-.48, .16), (-.34, .03), (-.53, -.04),
     (-.25, .07), (-.13, .13), (-.13, .13), (-.13, .13)),
    ((0, 0), (.09, -.04), (.28, -.08), (.47, .01), (.31, .10),
     (.12, .11), (.02, .15), (.02, .15), (.02, .15)),
    ((0, 0), (.07, .04), (.04, .08), (-.03, .18), (-.08, .46),
     (.03, .79), (.02, .91), (.02, .91), (.02, .91)),
)
_YAW = (
    (-12, 15, 53, 25, -25, -4, 0, 0, 0),
    (14, 6, -22, -48, -18, 7, 0, 0, 0),
    (-12, -3, 15, 10, -8, -3, 0, 0, 0),
)
_STEPS = (
    ((.12, 1.30, "R"), (1.50, 2.65, "L"), (3.20, 4.40, "R"),
     (4.65, 5.90, "L"), (6.40, 7.65, "R"), (7.95, 9.15, "L"),
     (10.0, 11.25, "R"), (11.60, 12.85, "L"), (14.0, 15.30, "L"),
     (15.60, 16.90, "R"), (17.40, 18.45, "L"), (18.60, 19.45, "R")),
    ((.55, 1.70, "L"), (2.00, 3.10, "R"), (3.75, 4.95, "L"),
     (5.20, 6.45, "R"), (7.00, 8.25, "L"), (8.55, 9.80, "R"),
     (10.25, 11.50, "L"), (11.80, 13.05, "R"), (14.15, 15.45, "R"),
     (15.75, 17.05, "L"), (17.50, 18.50, "R"), (18.70, 19.55, "L")),
    ((.35, 1.65, "R"), (2.05, 3.30, "L"), (4.25, 5.55, "L"),
     (5.90, 7.15, "R"), (7.75, 9.05, "R"), (9.40, 10.70, "L"),
     (11.10, 12.45, "R"), (12.80, 14.10, "L"), (14.55, 15.85, "R"),
     (16.20, 17.50, "L"), (17.85, 18.65, "R"), (18.85, 19.60, "L")),
)


@dataclass(frozen=True)
class Step:
    start: float
    end: float
    side: str
    source: tuple[float, float, float]
    target: tuple[float, float, float]
    source_yaw: float
    target_yaw: float


class TrioPerformance:
    """Three complementary, grounded scores with an exact absolute-time API."""

    def __init__(self, actor, role=0, duration=DURATION):
        if isinstance(role, bool) or role not in (0, 1, 2):
            raise ValueError("role must be 0 (lead), 1 (answer) or 2 (welcome)")
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("duration must be finite and positive")
        self.actor, self.rig, self.mo = actor, actor.rig, actor.mo
        self.role, self.name, self.duration = int(role), ROLE_NAMES[role], float(duration)
        self.scale = self.rig.height / 1.65
        self._path = _curve(_PATH_TIMES, _PATHS[role])
        self._yaw = _curve(_PATH_TIMES, _YAW[role])
        self._palms = {"R": _curve(_HAND_TIMES, _RIGHT[role]),
                       "L": _curve(_HAND_TIMES, _LEFT[role])}
        self._wrist = _curve(_HAND_TIMES,
                            (20, 35, 10, -18, -28, 18, 34, 12, -20, -8, 20, 12, 12))
        self._free_wrist = _curve(_HAND_TIMES,
            ((72, 65, 78, 100, 42, 68, 82, 94, 78, 64, 75, 72, 72),
             (70, 88, 75, 95, 82, 45, 68, 94, 78, 63, 75, 72, 72),
             (80, 73, 65, 60, 75, 85, 80, 68, 55, 63, 70, 72, 72))[role])
        self._fan_bank = _curve(_HAND_TIMES,
            ((0, -8, -16, 25, 54, 8, -18, -10, 32, 5, -8, 0, 0),
             (5, 5, -10, -18, 22, 56, 5, -20, 28, 10, -5, 0, 0),
             (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))[role])
        self._head_turn = _curve(_PATH_TIMES,
            ((20, 12, -12, -22, 15, 14, 3, 3, 3),
             (-16, -12, 12, 23, -12, -15, -3, -3, -3),
             (12, -12, -16, 14, 12, -7, 0, 0, 0))[role])
        self._head_up = _curve(_HAND_TIMES,
                              (3, 6, 11, 14, 8, 0, -3, 5, 12, 10, 4, 2, 2))
        self._lean = _curve(_HAND_TIMES,
                           (2, 0, -3, -5, -2, 3, 5, 1, -4, -2, 2, 2, 2))
        neutral = self.mo.identity()
        D, P, _ = self.mo.local_fk(neutral)
        self.flat_lift = float(-self.rig.lowest(self.rig.matrices(D, P)))
        N, i = self.rig.neutral_pos, self.rig.idx
        self.neutral_feet = {s: N[i["foot." + s]].copy() for s in ("L", "R")}
        self._neutral_mid = (self.neutral_feet["L"] + self.neutral_feet["R"]) * .5
        self.initial_feet = {}
        self.initial_yaw = {}
        yaw0 = float(self._yaw(0))
        for side, sign in (("L", 1), ("R", -1)):
            offset = self.neutral_feet[side] - self._neutral_mid
            offset[0] += sign * .012 * self.scale
            point = bm.qrot(bm.qy(yaw0 * DEG), offset) + self._neutral_mid
            point[1] += self.flat_lift
            self.initial_feet[side] = point
            self.initial_yaw[side] = yaw0 + sign * 6
        latest = {s: p.copy() for s, p in self.initial_feet.items()}
        latest_yaw = self.initial_yaw.copy()
        steps = []
        for start, end, side in _STEPS[role]:
            sign = 1 if side == "L" else -1
            centre = self._path(end) * self.scale
            yaw = float(self._yaw(end))
            offset = self.neutral_feet[side] - self._neutral_mid
            offset[0] += sign * .012 * self.scale
            dest = bm.qrot(bm.qy(yaw * DEG), offset) + self._neutral_mid
            dest[[0, 2]] += centre
            dest[1] += self.flat_lift
            steps.append(Step(start, end, side, tuple(latest[side]), tuple(dest),
                              latest_yaw[side], yaw + sign * 6))
            latest[side], latest_yaw[side] = dest, yaw + sign * 6
        self.steps = tuple(steps)

    def score_time(self, t):
        return float(np.clip(float(t) * DURATION / self.duration, 0, DURATION))

    def feet(self, t):
        """Return body-frame ankle targets, flat orientations and swing progress."""
        s = self.score_time(t)
        pos = {side: p.copy() for side, p in self.initial_feet.items()}
        yaw = self.initial_yaw.copy()
        swing = None
        for step in self.steps:
            if s <= step.start:
                break
            if s >= step.end:
                pos[step.side] = np.asarray(step.target)
                yaw[step.side] = step.target_yaw
                continue
            raw = (s - step.start) / (step.end - step.start)
            u = float(bm.smoother(raw))
            arc = math.sin(np.pi * u)
            pos[step.side] = (np.asarray(step.source) * (1-u)
                              + np.asarray(step.target) * u)
            pos[step.side][1] += (.065 if self.role != 2 else .055) * self.scale * arc
            yaw[step.side] = step.source_yaw * (1-u) + step.target_yaw * u
            swing = (step.side, u)
            break
        rotations = {side: bm.qy(angle * DEG) for side, angle in yaw.items()}
        if swing:
            side, u = swing
            rotations[side] = bm.qmul(rotations[side], bm.qx(10 * DEG * math.sin(np.pi*u)))
        return pos, rotations, swing

    def pose(self, t):
        s = self.score_time(t)
        P = self.mo.identity()
        feet, foot_rot, swing = self.feet(t)
        midpoint = (feet["L"] + feet["R"]) * .5
        P.pos[[0, 2]] = (midpoint - self._neutral_mid)[[0, 2]]
        phase = 0.0 if swing is None else math.sin(np.pi * swing[1])
        if swing is not None:
            moving = swing[0]
            planted = "R" if moving == "L" else "L"
            P.pos[[0, 2]] += .22 * phase * (feet[planted] - feet[moving])[[0, 2]]
        P.pos[1] = self.flat_lift - (.045 + .018 * phase**2) * self.scale
        yaw = float(self._yaw(s))
        # The pelvis supports the phrase; small torso changes lead the hands.
        # No continually oscillating body or root translation is added on top.
        support_roll = 0 if swing is None else (1 if swing[0] == "R" else -1) * 1.8 * phase
        P.rot = bm.qmul(bm.qy(yaw * DEG), bm.qz(support_roll * DEG))
        self.mo._lean(P, 1, fwd=float(self._lean(s)),
                      twist=-.12 * yaw, side=-.20 * support_roll)
        self.mo._head(P, 1, up=float(self._head_up(s)),
                      turn=float(self._head_turn(s)), tilt=-.5 * support_roll)
        root = self.rig.neutral_pos[0] + P.pos
        yaw_q = bm.qy(yaw * DEG)
        for side, sign in (("L", 1), ("R", -1)):
            point = self._palms[side](s) * self.scale
            palm_at = root + bm.qrot(yaw_q, point - self.rig.neutral_pos[0])
            wrist_angle = float((self._wrist if side == "R" and self.role in (0, 1)
                                 else self._free_wrist)(s))
            fingers = bm.qrot(yaw_q, [sign * math.sin(wrist_angle*DEG),
                                      math.cos(wrist_angle*DEG), 0])
            palm_normal = bm.qrot(yaw_q, [0, 0, 1])
            if side == "R" and self.role in (0, 1):
                # A bank changes the fan plane through the arm's middle arc;
                # it is a bounded pronation, never a 180-degree wrist flip.
                palm_normal = bm.qrot(bm.qaxis(fingers, float(self._fan_bank(s))*DEG),
                                       palm_normal)
            pole = bm.qrot(yaw_q, [sign * .55, -.85, -.28])
            self.mo.hand_to(P, side, palm_at, fingers, palm_normal, pole=pole)
            if side == "R" and self.role in (0, 1):
                self.mo.hand_pose(P, side, dict(curl=(38, 55, 61, 65, 68), spread=1.0))
            else:
                self.mo.hand_pose(P, side, dict(curl=(20, 9, 15, 21, 29), spread=4.0))
        # Solve after upper-body acting, with fixed world-relative support
        # targets. The engine's automatic sole lift/lock must not move them.
        for side, sign in (("L", 1), ("R", -1)):
            pole = bm.qrot(yaw_q, [sign*.12, 0, 1])
            self.mo.leg_to(P, side, feet[side], knee=pole, foot=foot_rot[side])
        P.ground = 0.0
        P.contact = None
        return P

    def diagnostics(self, t):
        targets, _, swing = self.feet(t)
        return dict(role=self.name, score_time=self.score_time(t),
                    swing=None if swing is None else swing[0],
                    contact={s: swing is None or swing[0] != s for s in ("L", "R")},
                    ankle_targets={s: p.tolist() for s, p in targets.items()},
                    authored=True, reconstructed_reference_motion=False)

    def contact_report(self, samples=241):
        """Measure final FK contact error and continuity, not just target curves."""
        times = np.linspace(0, self.duration, samples)
        previous = None
        max_error, max_slip, wrist_step, root_step = 0., 0., 0., 0.
        min_sole = math.inf
        wrist_angle_step = 0.
        for t in times:
            f = self.actor.frame(float(t))
            targets, _, swing = self.feet(t)
            h = bm.qy(self.actor.heading(float(t)) * DEG)
            origin = self.actor.travel(float(t))[1]
            contact = {s: swing is None or swing[0] != s for s in ("L", "R")}
            actual = {}
            for side in ("L", "R"):
                index = self.rig.idx["foot." + side]
                actual[side] = f["P"][index]
                world_target = origin + bm.qrot(h, targets[side])
                max_error = max(max_error, float(np.linalg.norm(actual[side]-world_target)))
                vertices = self.rig.verts0[self.rig.vert_bone == index]
                M = f["M"][index]
                sole = vertices @ M[:3, :3].T + M[:3, 3]
                min_sole = min(min_sole, float(sole[:, 1].min()-origin[1]))
                if previous is not None and contact[side] and previous["contact"][side]:
                    max_slip = max(max_slip, float(np.linalg.norm(actual[side]-previous["feet"][side])))
            wrists = f["P"][[self.rig.idx["wrist.L"], self.rig.idx["wrist.R"]]]
            wrist_q = f["A"][[self.rig.idx["wrist.L"], self.rig.idx["wrist.R"]]]
            if previous is not None:
                wrist_step = max(wrist_step, float(np.linalg.norm(wrists-previous["wrists"],axis=1).max()))
                dots = np.abs(np.sum(wrist_q * previous["wrist_q"], axis=1))
                wrist_angle_step = max(wrist_angle_step, float(np.degrees(2*np.arccos(np.clip(dots,0,1))).max()))
                root_step = max(root_step, float(np.linalg.norm(f["P"][0]-previous["root"])))
            previous = dict(feet=actual, contact=contact, wrists=wrists,
                            wrist_q=wrist_q, root=f["P"][0])
        return dict(role=self.name, samples=int(samples), duration_seconds=self.duration,
                    authored_steps=len(self.steps), max_ankle_target_error_m=max_error,
                    max_planted_ankle_step_m=max_slip, minimum_foot_vertex_height_m=min_sole,
                    max_wrist_step_m=wrist_step, max_wrist_angle_step_deg=wrist_angle_step,
                    max_root_step_m=root_step, sample_interval_seconds=self.duration/(samples-1),
                    provenance="Original authored score; not reconstructed reference motion",
                    limits="Kinematic authored steps and IK, not captured dance or force-driven balance")


def install_performance(body, role=0, duration=DURATION):
    """Install once before Body.where/joint/sample or any cloth-cache sampling."""
    actor = getattr(body, "actor", body)
    if getattr(actor, "concert_fan_performance", None) is not None:
        raise ValueError("Fan performance is already installed")
    if getattr(actor, "_cache", None):
        raise ValueError("Install the fan performance before sampling the body")
    if actor.gest or getattr(actor, "hand", None):
        raise ValueError("Use no external gesture or hand override with this authored score")
    performance = TrioPerformance(actor, role=role, duration=duration)
    actor.base_pose = performance.pose
    actor.life = False
    original_frame = actor.frame

    def canonical_frame(t, lock=True, gest=True, life=True):
        return original_frame(round(float(t), 6), lock=lock, gest=gest, life=life)

    actor.frame = canonical_frame
    actor.concert_fan_performance = performance
    actor._cache.clear()
    for name in ("_sk", "_pts", "_anchors"):
        cache = getattr(body, name, None)
        if cache is not None:
            cache.clear()
    return performance
