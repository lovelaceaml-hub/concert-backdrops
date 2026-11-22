"""Bounded, deterministic hands and arm correction for Advanced Dance.

The old hand target helper can rotate a wrist by more than 140 degrees to meet
an independent world-space finger direction. This layer solves the forearm
first, distributes palm rotation into pronation, and keeps the hand close to
the forearm line. Limits are conservative authoring choices, not a medical
range-of-motion model. Every call depends only on the supplied pose and cue.

All pose arguments use the native actor frame: metres, +Y up, +Z forward,
+X anatomical left. ``grip_frame`` alone returns final world coordinates.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

from p3d import bodymath as bm

DEG = math.pi / 180.0


def _unit(value, fallback=None):
    value = np.asarray(value, dtype=np.float64)
    if value.shape != (3,) or not np.isfinite(value).all():
        raise ValueError("Expected a finite three-dimensional direction")
    length = float(np.linalg.norm(value))
    if length <= 1e-9:
        if fallback is None:
            raise ValueError("A direction must have nonzero length")
        return _unit(fallback)
    return value / length


def _soft_positive(value, floor=0.15, width=0.035):
    """Smoothly retain a positive denominator without a branch at the pole."""
    delta = float(value) - floor
    return floor + .5 * (delta + math.sqrt(delta * delta + width * width))


def _bounded(value, limit):
    return float(limit * math.tanh(float(value) / limit))


def _basis(rig, side):
    i = rig.idx
    f = _unit(rig.neutral_pos[i["finger3-1." + side]]
              - rig.neutral_pos[i["wrist." + side]])
    n = rig.palm_n[side]
    n = _unit(n - f * np.dot(n, f))
    # x: across palm, y: finger direction, z: palm normal.
    return np.stack([_unit(np.cross(f, n)), f, n], axis=1)


@dataclass(frozen=True)
class WristLimits:
    flex_deg: float = 35.0
    deviation_deg: float = 18.0
    twist_deg: float = 10.0
    pronation_deg: float = 92.0
    minimum_elbow_deg: float = 18.0
    maximum_elbow_deg: float = 145.0


@dataclass(frozen=True)
class HandCorrection:
    side: str
    requested_palm: tuple[float, float, float]
    solved_palm: tuple[float, float, float]
    target_error_m: float
    reach_correction_m: float
    wrist_flex_deg: float
    wrist_deviation_deg: float
    wrist_twist_deg: float
    pronation_deg: float
    elbow_bend_deg: float

    def as_dict(self):
        return asdict(self)


def inspect_hand(actor, pose, side):
    """Geometric diagnostics of a supplied pose, independent of cue history."""
    if side not in ("L", "R"):
        raise ValueError("side must be L or R")
    rig, mo, i = actor.rig, actor.mo, actor.rig.idx
    _, joints, _ = mo.local_fk(pose)
    wr = i["wrist." + side]
    basis = _basis(rig, side)
    local = basis.T @ bm.qmat(pose.q[wr]) @ basis
    deviation, flex, twist = Rotation.from_matrix(local).as_euler("ZXY", degrees=True)
    upper = joints[i["lowerarm01." + side]] - joints[i["upperarm01." + side]]
    lower = joints[wr] - joints[i["lowerarm01." + side]]
    bend = math.degrees(math.acos(float(np.clip(np.dot(_unit(upper), _unit(lower)), -1, 1))))
    q = pose.q[wr]
    return dict(wrist_flex_deg=float(flex), wrist_deviation_deg=float(deviation),
                wrist_twist_deg=float(twist), elbow_bend_deg=bend,
                wrist_rotation_deg=math.degrees(2 * math.acos(min(abs(float(q[0])), 1.0))))


class AnatomyController:
    """Constrained arm, wrist and articulated fan grip on the existing rig.

    ``hand`` accepts the same palm point as ``mo.hand_to``. Desired fingers
    are optional; without them, the hand lengthens the forearm with a small
    authored flourish. Palm normal is a preference, not an unlimited wrist
    command. The solver reports any remaining target correction.

    The finger rig is authored, not captured. A calibrated thumb opposition
    closes onto the index side of a transverse fan handle. Other fingers wrap
    progressively, instead of collapsing into one tightly curled knot.
    """

    def __init__(self, actor, limits=None):
        self.actor, self.rig, self.mo = actor, actor.rig, actor.mo
        self.i = self.rig.idx
        self.limits = limits or WristLimits()
        self.scale = self.rig.height / 1.66
        self._basis = {s: _basis(self.rig, s) for s in ("L", "R")}
        self._palm_offset = {}
        self._hand_bones = {}
        self._closed = {}
        self._open = {}
        self._neutral_offsets = bm.qrot(self.rig.C[np.maximum(self.rig.parent, 0)], self.rig.offset)
        self.thumb_calibration = {}
        for side in ("L", "R"):
            wr, m3 = self.i["wrist." + side], self.i["finger3-1." + side]
            n = self.rig.palm_n[side]
            self._palm_offset[side] = (.6 * (self.rig.neutral_pos[m3] - self.rig.neutral_pos[wr])
                                      + n * .012 * self.mo.k)
            self._hand_bones[side] = np.array([self.i[f"finger{f}-{j}.{side}"]
                                             for f in range(1, 6) for j in range(1, 4)])
            self._prepare_fingers(side)

    def _prepare_fingers(self, side):
        mo, rig, i = self.mo, self.rig, self.i
        sign = 1 if side == "L" else -1
        open_pose, closed = mo.identity(), mo.identity()
        mo.hand_pose(open_pose, side, dict(curl=(10, 8, 13, 18, 24), spread=2.6))
        # The distal cascade leaves visible separation between finger groups.
        mo.hand_pose(closed, side, dict(curl=(18, 52, 56, 59, 62), spread=.45))
        basis = self._basis[side]
        wr, m3 = i["wrist." + side], i["finger3-1." + side]
        origin = (.4 * rig.neutral_pos[wr] + .6 * rig.neutral_pos[m3]
                  + rig.palm_n[side] * .012 * mo.k)
        # The thumb pad meets the side of the index pad, not its bone centre.
        target = origin + basis @ (np.array([-sign * .017, .020, .038]) * self.scale)
        thumb = [i[f"finger1-{j}.{side}"] for j in (1, 2, 3)]
        bones, axes, _, fingers, first = mo._finger_table(side)
        curl_axes = [axes[np.flatnonzero(bones == b)[0]] for b in thumb]

        def apply(parameters, destination):
            # The thumb saddle uses a combined opposition/abduction rotation;
            # independent single-axis curl leaves its tip several centimetres
            # away from the index even when the other fingers are closed.
            rotation = basis @ (parameters[:3] * DEG)
            q0 = bm.qaxis(rotation, np.linalg.norm(rotation))
            destination.q[thumb] = np.array([q0, bm.qaxis(curl_axes[1], parameters[3] * DEG),
                                             bm.qaxis(curl_axes[2], parameters[4] * DEG)])

        prior = np.array([20, sign * 10, -sign * 35, 40, 40], float)

        def residual(parameters):
            apply(parameters, closed)
            d, p, _ = mo.local_fk(closed)
            b = thumb[-1]
            tip = p[b] + bm.qrot(d[b], rig.tail[b] - rig.head[b])
            return np.concatenate([(tip - target) / self.scale,
                                   .00010 * (parameters - prior)])

        solution = least_squares(residual, prior,
                                 bounds=([-65, -65, -80, 0, 0], [65, 65, 80, 65, 80]),
                                 ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=80)
        apply(solution.x, closed)
        self._closed[side] = closed.q[self._hand_bones[side]].copy()
        self._open[side] = open_pose.q[self._hand_bones[side]].copy()
        self.thumb_calibration[side] = dict(parameters_deg=solution.x.tolist(),
                                            pad_target_residual_m=float(np.linalg.norm(residual(solution.x)[:3]) * self.scale))

    def shape_hand(self, pose, side, grip=1.0, flourish=0.0):
        grip = float(np.clip(grip, 0, 1))
        flourish = float(np.clip(flourish, -1, 1))
        bones = self._hand_bones[side]
        pose.q[bones] = bm.qslerp(self._open[side], self._closed[side], grip)
        # A controlled release ripple only affects an unheld hand. A prop grip
        # remains rigid enough to stay on the same handle throughout a flourish.
        if abs(flourish) > 1e-10 and grip < 1:
            table_bones, axes, _, finger, first = self.mo._finger_table(side)
            weight = (1 - grip) * flourish * 4 * DEG
            extra = bm.qaxis(axes, weight * np.where(finger == 1, .35, (finger - 1) / 4))
            pose.q[table_bones] = bm.qmul(pose.q[table_bones], extra)

    def _arm(self, pose, side, wrist_at, pole, normal, shoulder, shoulder_parent):
        """Solve a bent arm and smoothly bounded forearm pronation."""
        rig, i, mo = self.rig, self.i, self.mo
        ua, fa, wr = (i[n + side] for n in ("upperarm01.", "lowerarm01.", "wrist."))
        l1, l2 = mo.arm_len[side]
        direction = np.asarray(wrist_at) - shoulder
        distance = float(np.linalg.norm(direction))
        axis = _unit(direction, bm.qrot(pose.rot, [0, -1, 0]))
        lo = math.sqrt(l1*l1 + l2*l2 + 2*l1*l2*math.cos(self.limits.maximum_elbow_deg * DEG))
        hi = math.sqrt(l1*l1 + l2*l2 + 2*l1*l2*math.cos(self.limits.minimum_elbow_deg * DEG))
        # Smooth limits preserve velocity when a reach enters a correction zone.
        edge = .012 * self.scale
        d = lo + edge * np.logaddexp(0.0, (distance-lo)/edge)
        d = hi - edge * np.logaddexp(0.0, (hi-d)/edge)
        pp = pole - np.dot(pole, axis) * axis
        # Root-space backward bias keeps the elbow pole away from the front
        # hemisphere used by this score. This is an authored elbow path, not a
        # previous-frame state, so shuffled and reverse evaluation agree.
        backward = bm.qrot(pose.rot, [0, 0, -1])
        pp += .12 * (backward - np.dot(backward, axis) * axis)
        pp = _unit(pp, bm.qrot(pose.rot, [1 if side == "L" else -1, 0, 0]))
        along = (l1*l1-l2*l2+d*d)/(2*d)
        radius = math.sqrt(max(l1*l1-along*along, 1e-12))
        elbow = shoulder + along * axis + radius * pp
        u1 = _unit(elbow - shoulder)
        u2 = _unit(shoulder + axis*d - elbow)
        plane = _unit(np.cross(u1, u2))
        upper = bm.qfrommat(np.stack([-plane, -u1, np.cross(plane, u1)], 1))
        bend = math.acos(float(np.clip(np.dot(u1, u2), -1, 1)))
        pose.q[ua] = bm.qmul(bm.qconj(shoulder_parent), upper)
        pose.q[i["upperarm02." + side]] = bm.IDENT
        pose.q[fa] = bm.qx(-bend)
        lower = bm.qmul(upper, bm.qx(-bend))
        base_normal = bm.qrot(lower, rig.palm_n[side])
        a = _unit(base_normal - u2 * np.dot(base_normal, u2))
        b = normal - u2 * np.dot(normal, u2)
        # Keep the projected magnitude. Normalizing b would amplify an almost
        # parallel preference into a 180 degree pronation flip at zero length.
        # A preference parallel to the forearm instead releases to neutral.
        cosine, sine = float(np.dot(a, b)), float(np.dot(u2, np.cross(a, b)))
        # Folding the far hemisphere toward a positive denominator removes the
        # +/-180 branch that otherwise snaps an arm between twist limits.
        pronation = _bounded(math.atan2(sine, _soft_positive(cosine, floor=.65, width=.08)),
                            self.limits.pronation_deg * DEG)
        pose.q[i["lowerarm02." + side]] = bm.qaxis([0, -1, 0], pronation)
        pose.q[wr] = bm.IDENT
        # Evaluate only this unchanged-length chain during the inner solve.
        # A full-rig FK at entry and final inspection still verify the result.
        point, rotation = shoulder.copy(), upper
        for name in ("upperarm02.", "lowerarm01.", "lowerarm02.", "wrist."):
            child = i[name + side]
            point += bm.qrot(rotation, self._neutral_offsets[child])
            rotation = bm.qmul(rotation, pose.q[child])
        return abs(distance - d), math.degrees(pronation), point, rotation

    def hand(self, pose, side, palm_at, fingers=None, normal=None, pole=None,
             grip=1.0, flourish=0.0):
        if side not in ("L", "R"):
            raise ValueError("side must be L or R")
        target = np.asarray(palm_at, dtype=np.float64)
        if target.shape != (3,) or not np.isfinite(target).all():
            raise ValueError("palm_at must be a finite point")
        sign = 1 if side == "L" else -1
        normal = _unit(bm.qrot(pose.rot, [0, 0, 1]) if normal is None else normal)
        pole = _unit(bm.qrot(pose.rot, [sign * .62, -.73, -.36]) if pole is None else pole)
        fingers = None if fingers is None else _unit(fingers)
        flourish = float(np.clip(flourish, -1, 1))
        if not np.isfinite([grip, flourish]).all():
            raise ValueError("Hand weights must be finite")
        i, rig, mo = self.i, self.rig, self.mo
        wr = i["wrist." + side]
        basis = self._basis[side]
        wrist = target - bm.qrot(pose.rot, self._palm_offset[side])
        reach = 0.0
        _, entry_points, entry_rotations = mo.local_fk(pose)
        ua = i["upperarm01." + side]
        shoulder, shoulder_parent = entry_points[ua], entry_rotations[rig.parent[ua]]
        for _ in range(6):
            correction, pronation, actual_wrist, parent = self._arm(
                pose, side, wrist, pole, normal, shoulder, shoulder_parent)
            reach = correction
            base_f = bm.qrot(parent, basis[:, 1])
            base_n = bm.qrot(parent, basis[:, 2])
            base_x = bm.qrot(parent, basis[:, 0])
            if fingers is None:
                flex = -7.0 + 9.0 * flourish
                deviation = sign * (2.0 + 3.5 * flourish)
            else:
                den = _soft_positive(float(np.dot(fingers, base_f)))
                flex = math.degrees(math.atan2(float(np.dot(fingers, base_n)), den))
                deviation = -math.degrees(math.atan2(float(np.dot(fingers, base_x)), den))
            flex = _bounded(flex, self.limits.flex_deg)
            deviation = _bounded(deviation, self.limits.deviation_deg)
            residual = float(np.dot(base_f, np.cross(base_n, normal)))
            twist = _bounded(9.0 * residual, self.limits.twist_deg)
            local = Rotation.from_euler("ZXY", [deviation, flex, twist], degrees=True).as_matrix()
            pose.q[wr] = bm.qfrommat(basis @ local @ basis.T)
            # Split forearm joints are slightly off the ideal two-segment axis
            # in this mesh. Correct the *actual* final palm, not only the ideal
            # geometric wrist, so this small rig offset does not become slip.
            actual = actual_wrist + bm.qrot(bm.qmul(parent, pose.q[wr]), self._palm_offset[side])
            wrist += target - actual
        self.shape_hand(pose, side, grip, flourish)
        solved = mo._hand_end(pose, side, "palm")
        metrics = inspect_hand(self.actor, pose, side)
        return HandCorrection(side, tuple(map(float, target)), tuple(map(float, solved)),
                              float(np.linalg.norm(solved-target)), float(reach),
                              metrics["wrist_flex_deg"], metrics["wrist_deviation_deg"],
                              metrics["wrist_twist_deg"], float(pronation), metrics["elbow_bend_deg"])


def grip_frame(body, t, side="R"):
    """Final world handle centre, transverse axis, outward axis and normal.

    Use a transverse handle about 0.065 m long, scaled with the performer,
    centred at the returned point. The fan, handle, sparks and silk must all
    use this frame; none may follow a separate target track.
    """
    if side not in ("L", "R"):
        raise ValueError("side must be L or R")
    palm, normal = body.where(float(t), "palm." + side, normal=True)
    outward = body.actor.palm(float(t), side)[2]
    if hasattr(body, "_wdir"):
        outward = body._wdir(outward, float(t))
    outward = _unit(outward)
    normal = _unit(normal - outward * np.dot(normal, outward))
    across = _unit(np.cross(outward, normal))
    scale = body.actor.rig.height / 1.66 * float(getattr(body, "scale", 1.0))
    centre = np.asarray(palm) + scale * (.024 * outward + .010 * normal)
    return centre, across, outward, normal
