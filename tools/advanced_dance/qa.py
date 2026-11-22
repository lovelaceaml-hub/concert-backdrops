"""Dense, repeatable checks of the final solved dance skeleton and held props.

The report is a kinematic repair aid, not biomechanical validation. It measures
the final FK used by the renderer, including every output frame and the exact
renderer shutter sample times. Fast intentional motion produces review flags;
nonfinite geometry, broken contacts and reversed joint hinges produce errors.

Nothing in this module changes a pose or weakens a threshold to make it pass.
Fix the authored score or anatomy layer, rerun the same audit, and inspect the
reported times in a continuous render and native-size detail views.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from pathlib import Path
from typing import Callable

import numpy as np

from p3d import bodymath as bm
from p3d.cloth import Colliders


@dataclass(frozen=True)
class Limits:
    """Project repair tolerances, not universal human range-of-motion claims."""

    ankle_error_m: float = .004
    support_drift_m: float = .001
    support_rotation_deg: float = .5
    floor_penetration_m: float = .003
    support_sole_gap_m: float = .015
    bone_length_error_m: float = .00002
    hinge_reversal_deg: float = .5
    elbow_flex_deg: float = 150.0
    knee_flex_deg: float = 155.0
    wrist_local_rotation_deg: float = 55.0
    prop_attachment_error_m: float = .002
    palm_speed_review_m_s: float = 4.5
    wrist_speed_review_deg_s: float = 900.0
    wrist_acceleration_review_deg_s2: float = 22000.0
    bend_normal_step_review_deg: float = 38.0
    capsule_penetration_review_m: float = .012
    authored_palm_error_review_m: float = .02
    ankle_axial_twist_review_deg: float = 45.0
    support_pelvis_yaw_review_deg: float = 75.0


@dataclass(frozen=True)
class PropProbe:
    """Read the real rendered attachment and optional real surface points.

    grip(t) and expected_grip(t) both return world coordinates. If the expected
    callback is absent, the actor's solved palm is used. points(t) may sample a
    fan surface, but must not return a second invented animation trajectory.
    Attachment is checked as an error. Proximity to torso/head capsules is a
    visual-review flag because the collision proxy is only approximate.
    """

    name: str
    side: str
    grip: Callable
    expected_grip: Callable | None = None
    points: Callable | None = None


def sample_times(duration, fps=60, temporal_samples=2, shutter=.35, boundaries=(), cuts=()):
    """Match p3d.layer's backward shutter samples, then add boundary probes."""
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration must be finite and positive")
    if isinstance(fps, bool) or int(fps) != fps or fps <= 0:
        raise ValueError("fps must be a positive integer")
    if int(temporal_samples) != temporal_samples or temporal_samples < 1:
        raise ValueError("temporal_samples must be a positive integer")
    if not math.isfinite(shutter) or shutter < 0:
        raise ValueError("shutter must be finite and nonnegative")
    frame_count = round(duration * fps)
    if abs(frame_count - duration * fps) > 1e-6:
        raise ValueError("duration must end on an exact output-frame boundary")
    frame_times = np.arange(frame_count, dtype=float) / fps
    count = temporal_samples if shutter else 1
    offsets = shutter / fps * np.arange(count - 1, -1, -1) / count
    cut_frame = np.zeros(len(frame_times), bool)
    for cut in cuts:
        cut_frame |= (frame_times-float(cut) >= 0) & (frame_times-float(cut) < shutter/fps)
    times = list((frame_times[~cut_frame, None] - offsets[None]).ravel())
    times.extend(frame_times[cut_frame])
    times.extend((0.0, float(duration)))
    for t in boundaries:
        if not math.isfinite(t) or not 0 <= t <= duration:
            continue
        times.extend((max(0., t - 1e-5), float(t), min(duration, t + 1e-5)))
    return np.unique(np.round(times, 10)), frame_times


def quat_distance_deg(a, b):
    """Shortest rotation difference, invariant to quaternion sign changes."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    a = a / np.maximum(np.linalg.norm(a, axis=-1, keepdims=True), 1e-15)
    b = b / np.maximum(np.linalg.norm(b, axis=-1, keepdims=True), 1e-15)
    dot = np.abs(np.sum(a * b, axis=-1))
    return np.degrees(2 * np.arccos(np.clip(dot, 0, 1)))


def capsule_clearance(points, a, b, ra, rb, point_radius=0.0):
    """Signed distance of point spheres to the existing tapered body proxies."""
    points = np.asarray(points, float).reshape(-1, 3)
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    u = np.clip(np.einsum("nkj,kj->nk", points[:, None] - a, ab)
                / np.maximum(np.sum(ab * ab, axis=1), 1e-15), 0, 1)
    closest = a[None] + u[:, :, None] * ab[None]
    radius = np.asarray(ra)[None] * (1-u) + np.asarray(rb)[None] * u
    return np.linalg.norm(points[:, None] - closest, axis=-1) - radius - point_radius


class _Metric:
    def __init__(self, name, units, direction="max"):
        self.name, self.units, self.direction = name, units, direction
        self.value = -math.inf if direction == "max" else math.inf
        self.time = None
        self.part = None

    def add(self, value, time, part=None):
        value = float(value)
        better = value > self.value if self.direction == "max" else value < self.value
        if better:
            self.value, self.time, self.part = value, float(time), part

    def record(self):
        return {"value": self.value if math.isfinite(self.value) else None,
                "units": self.units, "time_seconds": self.time, "part": self.part}


def _hinge_angle(q):
    q = np.asarray(q, float)
    q = q if q[0] >= 0 else -q
    return float(np.degrees(2 * np.arctan2(q[1], q[0])))


def _foot_mesh(rig, matrices, ids):
    """Skin the actual foot vertices, including weights from adjacent bones."""
    blend = np.einsum("vk,vkij->vij", rig.w_val[ids], matrices[rig.w_idx[ids]])
    return np.einsum("vij,vj->vi", blend[:, :, :3], rig.verts0[ids]) + blend[:, :, 3]


def _boundaries(performance):
    # New scores may expose boundary_times in scene seconds. Do not silently
    # interpret score-space steps as scene times when a timing map is present.
    explicit = getattr(performance, "boundary_times", None)
    if explicit is not None:
        return tuple(explicit() if callable(explicit) else explicit)
    if hasattr(performance, "scene_time"):
        return tuple(performance.scene_time(t) for step in getattr(performance, "steps", ())
                     for t in (step.start, step.end))
    if getattr(performance, "delay", 0) or getattr(performance, "score_clock_is_scene_clock", True) is False:
        return ()
    return tuple(t for step in getattr(performance, "steps", ()) for t in (step.start, step.end))


def audit_performance(performance, *, fps=60, temporal_samples=2, shutter=.35,
                      props=(), limits=None, floor_y=None, include_rows=False,
                      capture_path=None, cuts=()):
    """Audit a performance with actor, duration, feet(t) and optional contacts(t).

    feet(t) returns body-frame ankle targets, foot rotations and a swing tuple
    (side, progress), or None during double support. contacts(t), if supplied,
    returns a dict with L/R booleans and permits other support schedules.
    The floor defaults to actor origin.y at each time. Set floor_y explicitly
    for a performer whose origin moves vertically above a stationary floor.
    """
    limits = limits or Limits()
    actor, rig = performance.actor, performance.actor.rig
    duration = float(performance.duration)
    times, frames = sample_times(duration, fps, temporal_samples, shutter, _boundaries(performance), cuts)
    main_times = {round(float(t), 10): i for i, t in enumerate(frames)}
    names = (
        ("ankle_target_error", "m", "max"), ("support_drift", "m", "max"),
        ("support_rotation", "deg", "max"), ("foot_sole_height", "m", "min"),
        ("support_sole_gap", "m", "max"), ("bone_length_error", "m", "max"),
        ("ankle_axial_twist", "deg", "max"), ("support_pelvis_yaw_difference", "deg", "max"),
        ("elbow_flex_min", "deg", "min"), ("elbow_flex_max", "deg", "max"),
        ("knee_flex_min", "deg", "min"), ("knee_flex_max", "deg", "max"),
        ("wrist_local_rotation", "deg", "max"), ("prop_attachment_error", "m", "max"),
        ("authored_palm_error", "m", "max"), ("ik_wrist_goal_projection", "m", "max"),
        ("gesture_envelope_correction", "m", "max"),
        ("wrist_flex_absolute", "deg", "max"), ("wrist_deviation_absolute", "deg", "max"),
        ("wrist_twist_absolute", "deg", "max"), ("forearm_pronation_absolute", "deg", "max"),
        ("hand_body_clearance", "m", "min"), ("prop_body_clearance", "m", "min"),
        ("palm_speed", "m/s", "max"), ("wrist_rotation_speed", "deg/s", "max"),
        ("wrist_rotation_acceleration", "deg/s2", "max"),
        ("bend_normal_frame_step", "deg", "max"),
        ("knee_bend_normal_frame_step", "deg", "max"),
        ("root_speed", "m/s", "max"), ("maximum_joint_frame_step", "m", "max"))
    metrics = {name: _Metric(name, units, direction) for name, units, direction in names}
    events, rows, captured = [], [], []
    foot_ids = {s: np.flatnonzero(rig.vert_bone == rig.idx["foot."+s]) for s in ("L", "R")}
    parent_ok = np.flatnonzero(rig.parent >= 0)
    neutral_length = np.linalg.norm(rig.neutral_pos[parent_ok] - rig.neutral_pos[rig.parent[parent_ok]], axis=1)
    collider = Colliders(rig)
    obstacle = np.array([g in ("hips", "chest", "neck", "head") for g in collider.groups])
    hand_bones = {s: [rig.idx["wrist."+s]] + [rig.idx[f"finger{f}-{j}.{s}"]
                  for f in range(1, 6) for j in range(1, 4)] for s in ("L", "R")}
    contact_anchor, rotation_anchor = {}, {}
    previous_main = None
    previous_speed = None
    valid_count = 0
    for t in times:
        t = float(t)
        solved = actor.frame(t)
        P, A, M = solved["P"], solved["A"], solved["M"]
        if not (np.isfinite(P).all() and np.isfinite(A).all() and np.isfinite(M).all()):
            events.append({"severity": "error", "check": "finite_pose", "time_seconds": t,
                           "message": "The renderer's final skeleton contains nonfinite values."})
            continue
        valid_count += 1
        targets, _orientations, swing = performance.feet(t)
        contacts = (performance.contacts(t) if hasattr(performance, "contacts") else
                    {s: swing is None or swing[0] != s for s in ("L", "R")})
        origin = np.asarray(solved["origin"])
        heading = bm.qy(float(solved["heading"]))
        corrections = performance.anatomy_report(t) if hasattr(performance, "anatomy_report") else {}
        gesture_fits = performance.gesture_fit_report(t) if hasattr(performance, "gesture_fit_report") else {}
        level = float(origin[1] if floor_y is None else floor_y)
        lengths = np.linalg.norm(P[parent_ok] - P[rig.parent[parent_ok]], axis=1)
        errors = np.abs(lengths-neutral_length)
        bi = int(np.argmax(errors))
        metrics["bone_length_error"].add(errors[bi], t, rig.names[parent_ok[bi]])
        local = bm.qmul(bm.qconj(A[rig.parent[parent_ok]]), A[parent_ok])
        local_q = dict(zip(parent_ok, local))
        a, b = collider.at(M)
        obstacle_a, obstacle_b = a[obstacle], b[obstacle]
        palms, wrist_q, bends, knee_bends = [], [], [], []
        per_frame = {"time_seconds": t, "contact": contacts, "feet": {}, "hands": {}}
        for s in ("L", "R"):
            fi, wi = rig.idx["foot."+s], rig.idx["wrist."+s]
            ki = rig.idx["lowerleg01."+s]
            shin = P[fi]-P[ki]
            shin /= max(float(np.linalg.norm(shin)), 1e-12)
            shin_forward = bm.qrot(A[rig.parent[fi]], [0, 0, 1])
            foot_forward = bm.qrot(A[fi], [0, 0, 1])
            shin_forward -= shin*np.dot(shin_forward, shin)
            foot_normal_plane = foot_forward-shin*np.dot(foot_forward, shin)
            twist = np.degrees(np.arctan2(np.dot(shin, np.cross(shin_forward, foot_normal_plane)),
                                          np.dot(shin_forward, foot_normal_plane)))
            metrics["ankle_axial_twist"].add(abs(twist), t, s)
            expected = origin + bm.qrot(heading, targets[s])
            error = float(np.linalg.norm(P[fi]-expected))
            metrics["ankle_target_error"].add(error, t, s)
            sole = _foot_mesh(rig, M, foot_ids[s])
            height = float(sole[:, 1].min()-level)
            metrics["foot_sole_height"].add(height, t, s)
            if contacts[s]:
                root_forward = bm.qrot(A[0], [0, 0, 1])
                root_yaw = np.arctan2(root_forward[0], root_forward[2])
                foot_yaw = np.arctan2(foot_forward[0], foot_forward[2])
                difference = (np.degrees(root_yaw-foot_yaw)+180) % 360-180
                metrics["support_pelvis_yaw_difference"].add(abs(difference), t, s)
                if s not in contact_anchor:
                    contact_anchor[s], rotation_anchor[s] = P[fi].copy(), A[fi].copy()
                drift = float(np.linalg.norm(P[fi]-contact_anchor[s]))
                angle = float(quat_distance_deg(A[fi], rotation_anchor[s]))
                metrics["support_drift"].add(drift, t, s)
                metrics["support_rotation"].add(angle, t, s)
                metrics["support_sole_gap"].add(height, t, s)
            else:
                contact_anchor.pop(s, None)
                rotation_anchor.pop(s, None)
            ei, ki = rig.idx["lowerarm01."+s], rig.idx["lowerleg01."+s]
            elbow, knee = -_hinge_angle(local_q[ei]), _hinge_angle(local_q[ki])
            for kind, value in (("elbow", elbow), ("knee", knee)):
                metrics[kind+"_flex_min"].add(value, t, s)
                metrics[kind+"_flex_max"].add(value, t, s)
            wrist_angle = float(quat_distance_deg(local_q[wi], bm.IDENT))
            metrics["wrist_local_rotation"].add(wrist_angle, t, s)
            palm, _, _ = actor.palm(t, s)
            palms.append(palm)
            wrist_q.append(A[wi])
            if s in corrections:
                correction = corrections[s]
                correction = correction.as_dict() if hasattr(correction, "as_dict") else correction
                requested = origin + bm.qrot(heading, correction["requested_palm"])
                metrics["authored_palm_error"].add(np.linalg.norm(palm-requested), t, s)
                # This value belongs to the final inner-solver virtual goal.
                # It can grow when unreachable-target iterations accumulate;
                # it is not the displacement of the rendered hand.
                metrics["ik_wrist_goal_projection"].add(correction["reach_correction_m"], t, s)
                for metric, key in (("wrist_flex_absolute", "wrist_flex_deg"),
                                    ("wrist_deviation_absolute", "wrist_deviation_deg"),
                                    ("wrist_twist_absolute", "wrist_twist_deg"),
                                    ("forearm_pronation_absolute", "pronation_deg")):
                    metrics[metric].add(abs(correction[key]), t, s)
            if s in gesture_fits:
                metrics["gesture_envelope_correction"].add(gesture_fits[s]["correction_m"], t, s)
            hand_points = np.concatenate([P[hand_bones[s]], palm[None]])
            clearance = capsule_clearance(hand_points, obstacle_a, obstacle_b,
                                          collider.ra[obstacle], collider.rb[obstacle], .012)
            metrics["hand_body_clearance"].add(clearance.min(), t, s)
            chain = P[[rig.idx["upperarm01."+s], ei, wi]]
            normal = np.cross(chain[1]-chain[0], chain[2]-chain[1])
            normal /= max(float(np.linalg.norm(normal)), 1e-12)
            bends.append((normal, elbow))
            leg_chain = P[[rig.idx["upperleg01."+s], ki, fi]]
            knee_normal = np.cross(leg_chain[1]-leg_chain[0], leg_chain[2]-leg_chain[1])
            knee_normal /= max(float(np.linalg.norm(knee_normal)), 1e-12)
            knee_bends.append((knee_normal, knee))
            per_frame["feet"][s] = {"target_error_m": error, "sole_height_m": height}
            per_frame["hands"][s] = {"elbow_flex_deg": elbow, "wrist_local_rotation_deg": wrist_angle,
                                      "capsule_clearance_m": float(clearance.min())}
        for prop in props:
            if prop.side not in ("L", "R"):
                raise ValueError("PropProbe side must be L or R")
            actual = np.asarray(prop.grip(t), float)
            expected = np.asarray(prop.expected_grip(t) if prop.expected_grip else actor.palm(t, prop.side)[0])
            if not (np.isfinite(actual).all() and np.isfinite(expected).all()):
                events.append({"severity": "error", "check": "finite_prop", "time_seconds": t,
                               "part": prop.name, "message": "Prop attachment contains nonfinite values."})
            else:
                metrics["prop_attachment_error"].add(np.linalg.norm(actual-expected), t, prop.name)
            if prop.points is not None:
                points = np.asarray(prop.points(t), float).reshape(-1, 3)
                if len(points) and np.isfinite(points).all():
                    distance = capsule_clearance(points, obstacle_a, obstacle_b,
                                                 collider.ra[obstacle], collider.rb[obstacle])
                    metrics["prop_body_clearance"].add(distance.min(), t, prop.name)
                elif len(points):
                    events.append({"severity": "error", "check": "finite_prop", "time_seconds": t,
                                   "part": prop.name, "message": "Prop surface contains nonfinite values."})
        if capture_path is not None and (round(t, 10) in main_times or t == duration):
            captured.append((t, P.copy(), A.copy(), M.copy(), origin.copy(), float(solved["heading"])))
        if round(t, 10) in main_times:
            current = {"time": t, "palms": np.asarray(palms), "wrist_q": np.asarray(wrist_q),
                       "P": P.copy(), "bends": bends, "knee_bends": knee_bends}
            if previous_main is not None:
                dt = t-previous_main["time"]
                palm_speed = np.linalg.norm(current["palms"]-previous_main["palms"], axis=1)/dt
                angular_speed = quat_distance_deg(current["wrist_q"], previous_main["wrist_q"])/dt
                metrics["palm_speed"].add(palm_speed.max(), t, ("L", "R")[int(palm_speed.argmax())])
                metrics["wrist_rotation_speed"].add(angular_speed.max(), t, ("L", "R")[int(angular_speed.argmax())])
                if previous_speed is not None:
                    accel = np.abs(angular_speed-previous_speed)/dt
                    metrics["wrist_rotation_acceleration"].add(accel.max(), t, ("L", "R")[int(accel.argmax())])
                previous_speed = angular_speed
                joint_step = np.linalg.norm(P-previous_main["P"], axis=1)
                ji = int(joint_step.argmax())
                metrics["maximum_joint_frame_step"].add(joint_step[ji], t, rig.names[ji])
                metrics["root_speed"].add(joint_step[0]/dt, t, "root")
                for side, (now, old) in enumerate(zip(bends, previous_main["bends"])):
                    if now[1] > 18 and old[1] > 18:
                        angle = np.degrees(np.arccos(np.clip(np.dot(now[0], old[0]), -1, 1)))
                        metrics["bend_normal_frame_step"].add(angle, t, ("L", "R")[side])
                for side, (now, old) in enumerate(zip(knee_bends, previous_main["knee_bends"])):
                    if now[1] > 8 and old[1] > 8:
                        angle = np.degrees(np.arccos(np.clip(np.dot(now[0], old[0]), -1, 1)))
                        metrics["knee_bend_normal_frame_step"].add(angle, t, ("L", "R")[side])
            previous_main = current
        if include_rows:
            rows.append(per_frame)
    rules = (
        ("ankle_target_error", limits.ankle_error_m, "error", ">", "Ankle misses its authored support/swing target."),
        ("support_drift", limits.support_drift_m, "error", ">", "A planted foot moves within its support interval."),
        ("support_rotation", limits.support_rotation_deg, "error", ">", "A planted foot rotates within its support interval."),
        ("foot_sole_height", -limits.floor_penetration_m, "error", "<", "Skinned foot vertices penetrate the floor."),
        ("support_sole_gap", limits.support_sole_gap_m, "error", ">", "A declared planted foot floats above the floor."),
        ("bone_length_error", limits.bone_length_error_m, "error", ">", "FK bone length differs from the reference skeleton."),
        ("elbow_flex_min", -limits.hinge_reversal_deg, "error", "<", "Elbow hinge bends backward."),
        ("knee_flex_min", -limits.hinge_reversal_deg, "error", "<", "Knee hinge bends backward."),
        ("elbow_flex_max", limits.elbow_flex_deg, "error", ">", "Elbow exceeds the project's authored flexion range."),
        ("knee_flex_max", limits.knee_flex_deg, "error", ">", "Knee exceeds the project's authored flexion range."),
        ("wrist_local_rotation", limits.wrist_local_rotation_deg, "error", ">", "Wrist exceeds the project's combined local-rotation limit."),
        ("prop_attachment_error", limits.prop_attachment_error_m, "error", ">", "Rendered prop grip detaches from the declared solved hand anchor."),
        ("ankle_axial_twist", limits.ankle_axial_twist_review_deg, "review", ">", "Inspect foot rotation about the final shin axis for an awkward ankle twist."),
        ("support_pelvis_yaw_difference", limits.support_pelvis_yaw_review_deg, "review", ">", "Inspect a planted foot facing far away from pelvis heading during a turn."),
        ("authored_palm_error", limits.authored_palm_error_review_m, "review", ">", "Inspect a hand target that the corrected rig cannot closely reach."),
        ("palm_speed", limits.palm_speed_review_m_s, "review", ">", "Inspect the fastest hand passage at full speed."),
        ("wrist_rotation_speed", limits.wrist_speed_review_deg_s, "review", ">", "Inspect fast wrist rotation for flips or intentional fan accents."),
        ("wrist_rotation_acceleration", limits.wrist_acceleration_review_deg_s2, "review", ">", "Inspect abrupt wrist acceleration around this frame."),
        ("bend_normal_frame_step", limits.bend_normal_step_review_deg, "review", ">", "Inspect elbow pole continuity around this frame."),
        ("knee_bend_normal_frame_step", limits.bend_normal_step_review_deg, "review", ">", "Inspect knee pole continuity around this frame."),
        ("hand_body_clearance", -limits.capsule_penetration_review_m, "review", "<", "Inspect possible hand intersection with torso/head proxy."),
        ("prop_body_clearance", -limits.capsule_penetration_review_m, "review", "<", "Inspect possible prop intersection with torso/head proxy."))
    for name, threshold, severity, comparison, message in rules:
        metric = metrics[name]
        if metric.time is None:
            continue
        failed = metric.value > threshold if comparison == ">" else metric.value < threshold
        if failed:
            events.append({"severity": severity, "check": name, "time_seconds": metric.time,
                           "part": metric.part, "value": metric.value, "threshold": threshold,
                           "units": metric.units, "message": message})
    errors = [e for e in events if e["severity"] == "error"]
    warnings = [e for e in events if e["severity"] == "review"]
    review_times = sorted({round(float(e["time_seconds"]), 6) for e in events})
    report = {
        "schema_version": 1, "performance": getattr(performance, "name", type(performance).__name__),
        "status": "blocked" if errors else "review_required" if warnings else "numeric_pass",
        "duration_seconds": duration, "fps": int(fps), "output_frames": len(frames),
        "temporal_samples": int(temporal_samples), "shutter_fraction": float(shutter),
        "cuts_seconds": list(map(float, cuts)),
        "sampling": "Every frame plus backward p3d shutter samples, endpoint and declared boundary probes.",
        "sample_count": len(times), "finite_sample_count": valid_count,
        "sample_time_range_seconds": [float(times[0]), float(times[-1])],
        "limits": asdict(limits), "metrics": {name: value.record() for name, value in metrics.items()},
        "issues": events, "error_count": len(errors), "review_flag_count": len(warnings),
        "targeted_review_times_seconds": review_times,
        "scope": {
            "actual_final_fk": True, "skinned_foot_vertices": True,
            "full_frame_clock": True, "renderer_shutter_clock": True,
            "prop_probes": [p.name for p in props],
            "anatomy_correction_metrics": bool(hasattr(performance, "anatomy_report")),
            "gesture_envelope_correction": "Raw directional cue fitted to the posed shoulder reach before IK; reported separately from final hand error.",
            "ik_wrist_goal_projection": "Internal virtual-goal projection only; authored_palm_error measures the actual final hand miss.",
            "clearance": "Finger joint spheres and optional prop surface points against existing torso/head capsules.",
            "not_validated": ["physical balance or forces", "complete mesh self-collision", "cloth self-collision",
                              "all camera occlusions", "reference foot reconstruction", "owner creative approval"],
        },
        "repair_loop": ["Inspect reported time and neighboring frames in continuous motion.",
                        "Correct the score, support schedule, hand orientation or prop attachment.",
                        "Rerun the same numeric audit with unchanged thresholds.",
                        "Render a continuous proof and inspect native hand/foot details.",
                        "Freeze source, render the full movie, then inspect its encoded frames."],
    }
    if include_rows:
        report["samples"] = rows
    if capture_path is not None:
        import hashlib

        destination = Path(capture_path).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(destination, times=np.array([f[0] for f in captured]),
                            P=np.array([f[1] for f in captured]), A=np.array([f[2] for f in captured]),
                            M=np.array([f[3] for f in captured]), origin=np.array([f[4] for f in captured]),
                            heading=np.array([f[5] for f in captured]),
                            bone_names=np.asarray(rig.names), fps=int(fps), duration=duration)
        report["final_fk_capture"] = {"path": str(destination), "samples": len(captured),
                                       "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                                       "bytes": destination.stat().st_size,
                                       "scope": "Frame-grid final FK plus exact duration endpoint, no generated image or cloth cache."}
    return report


def _segment_distances(a, b, c, d):
    """Exact shortest distances for every pair of finite line segments."""
    a, b, c, d = map(lambda x: np.asarray(x, float), (a, b, c, d))
    u, v, w = (b-a)[:, None], (d-c)[None], a[:, None]-c[None]
    aa, bb, cc = np.sum(u*u, axis=-1), np.sum(u*v, axis=-1), np.sum(v*v, axis=-1)
    dd, ee = np.sum(u*w, axis=-1), np.sum(v*w, axis=-1)
    denominator = aa*cc-bb*bb
    safe = np.where(np.abs(denominator) > 1e-15, denominator, 1)
    s, t = (bb*ee-cc*dd)/safe, (aa*ee-bb*dd)/safe
    interior = (np.abs(denominator) > 1e-15) & (s >= 0) & (s <= 1) & (t >= 0) & (t <= 1)
    dist = np.where(interior, np.linalg.norm(w+s[..., None]*u-t[..., None]*v, axis=-1), np.inf)
    # If the interior stationary point is outside either segment, the minimum
    # lies on at least one endpoint's projection onto the other segment.
    for ss in (0., 1.):
        tt = np.clip((ee+ss*bb)/np.maximum(cc, 1e-15), 0, 1)
        dist = np.minimum(dist, np.linalg.norm(w+ss*u-tt[..., None]*v, axis=-1))
    for tt in (0., 1.):
        ss = np.clip((tt*bb-dd)/np.maximum(aa, 1e-15), 0, 1)
        dist = np.minimum(dist, np.linalg.norm(w+ss[..., None]*u-tt*v, axis=-1))
    return dist


def audit_cast_captures(performances, captures, *, review_penetration_m=.015):
    """Check inter-performer body capsule clearance using saved actual FK.

    Each capture comes from audit_performance(..., capture_path=...). The
    corresponding performance supplies its real rig. Maximum capsule endpoint
    radii are used conservatively. Fan-to-fan flower overlaps are outside this
    body check. Negative clearance is a visual-review flag, not a claim that
    the fully skinned bodies or fabric actually collided.
    """
    if len(performances) != len(captures) or len(performances) < 2:
        raise ValueError("Supply corresponding performances and captures for at least two people")
    loaded = [np.load(Path(p), allow_pickle=False) for p in captures]
    try:
        times = loaded[0]["times"]
        for perf, data in zip(performances, loaded):
            if not np.array_equal(data["times"], times):
                raise ValueError("Cast captures must use the same exact frame clock")
            if list(data["bone_names"]) != list(perf.actor.rig.names):
                raise ValueError("Capture bone names do not match the provided rig")
        colliders = [Colliders(perf.actor.rig) for perf in performances]
        radii = [np.maximum(c.ra, c.rb) for c in colliders]
        matrices = [data["M"] for data in loaded]
        minima = {}
        for i in range(len(performances)):
            for j in range(i+1, len(performances)):
                minima[i, j] = _Metric("body_capsule_clearance", "m", "min")
        for k, t in enumerate(times):
            caps = [col.at(matrix[k]) for col, matrix in zip(colliders, matrices)]
            for (i, j), metric in minima.items():
                distances = _segment_distances(*caps[i], *caps[j]) - radii[i][:, None] - radii[j][None]
                row, column = np.unravel_index(int(distances.argmin()), distances.shape)
                part = f"{colliders[i].groups[row]} / {colliders[j].groups[column]}"
                metric.add(distances[row, column], t, part)
        pairs, issues = [], []
        for (i, j), metric in minima.items():
            record = metric.record()
            record["performers"] = [performances[i].name, performances[j].name]
            pairs.append(record)
            if metric.value < -review_penetration_m:
                issues.append(dict(record, severity="review", check="inter_performer_capsules",
                                   message="Inspect possible inter-performer body intersection."))
        return {"schema_version": 1, "status": "review_required" if issues else "proxy_clearance_pass",
                "sample_count": len(times), "fps": int(loaded[0]["fps"]),
                "duration_seconds": float(loaded[0]["duration"]),
                "performer_count": len(performances), "pairs": pairs, "issues": issues,
                "scope": "Every captured frame, conservative body capsules, not full mesh or cloth collision.",
                "fan_to_fan_overlap_checked": False, "owner_approval": False}
    finally:
        for data in loaded:
            data.close()


def render_review_sheet(movie, times, output, *, crop=None, columns=4, tile_width=480):
    """Extract ordered evidence directly from a movie, never generated stand-ins.

    crop is an optional pixel (left, top, right, bottom) tuple. Use tile_width
    equal to crop width for a native pixel crop without resizing. The returned
    manifest records requested timestamps and extraction scope; it is not a
    statement that a human watched the entire movie.
    """
    from fractions import Fraction
    import json
    import subprocess
    import tempfile
    from PIL import Image, ImageDraw

    movie, output = Path(movie).resolve(), Path(output).resolve()
    if not movie.is_file():
        raise FileNotFoundError(movie)
    times = sorted({float(t) for t in times})
    if not times or any(not math.isfinite(t) or t < 0 for t in times):
        raise ValueError("Supply at least one nonnegative finite review timestamp")
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=avg_frame_rate,r_frame_rate,nb_frames", "-of", "json", str(movie)]))["streams"][0]
    rate = Fraction(probe["avg_frame_rate"])
    if rate <= 0 or rate != Fraction(probe["r_frame_rate"]):
        raise ValueError("Review sheets require the constant-frame-rate final output")
    count = int(probe["nb_frames"])
    indices = sorted({min(count-1, round(t*float(rate))) for t in times})
    tiles = []
    with tempfile.TemporaryDirectory(prefix="dance-review-") as temp:
        pattern = str(Path(temp)/"%05d.png")
        select = "+".join(f"eq(n\\,{n})" for n in indices)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(movie), "-vf", "select="+select,
                        "-fps_mode", "passthrough", "-frames:v", str(len(indices)), pattern], check=True)
        samples = sorted(Path(temp).glob("*.png"))
        if len(samples) != len(indices):
            raise RuntimeError("The decoder did not return every selected review frame")
        for index, path in zip(indices, samples):
            image = Image.open(path).convert("RGB")
            if crop is not None:
                left, top, right, bottom = map(int, crop)
                if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                    raise ValueError("Review crop must lie inside the decoded frame")
                image = image.crop((left, top, right, bottom))
            if image.width != tile_width:
                image = image.resize((tile_width, round(image.height * tile_width / image.width)), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (image.width, image.height+26), "#09101b")
            tile.paste(image, (0, 26))
            ImageDraw.Draw(tile).text((9, 6), f"Frame {index} | {index/float(rate):.4f} s", fill="white")
            tiles.append(tile)
    columns = min(max(int(columns), 1), len(tiles))
    sheet = Image.new("RGB", (columns*tiles[0].width, math.ceil(len(tiles)/columns)*tiles[0].height), "#09101b")
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % columns)*tile.width, (i//columns)*tile.height))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    return {"source": str(movie), "output": str(output), "requested_times_seconds": times,
            "decoded_frame_indices": indices, "decoded_times_seconds": [i/float(rate) for i in indices],
            "crop_pixels": crop, "tile_width_pixels": tile_width, "ordered": True,
            "scope": "Decoded frame samples only; continuous playback is a separate review."}


def main():
    """Run the repair audit against the actual registered cast and fan models."""
    import argparse
    import hashlib
    import json
    import time

    from .anatomy import grip_frame
    from .scene import make_cast, cuts

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("solo", "ensemble"), required=True)
    parser.add_argument("--role", type=int, help="One role; omit to audit the entire selected cast")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--fps", type=int, default=60, choices=(30, 60))
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--shutter", type=float, default=.35)
    args = parser.parse_args()
    ensemble = args.mode == "ensemble"
    if args.role is not None and not 0 <= args.role < (5 if ensemble else 1):
        parser.error("role is 0 for solo, or 0..4 for ensemble")
    root = Path(__file__).resolve().parents[2]
    inputs = set((root/"tools/advanced_dance").glob("*.py"))
    inputs.update((root/"engine/p3d").glob("*.py"))
    inputs.update((root/"tools/advanced_dance/clock.json", root/"assets/p3d/body_v1.npz"))
    source_hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)}
    bodies, fans = make_cast(ensemble)
    selected = list(range(len(bodies))) if args.role is None else [args.role]
    args.out.mkdir(parents=True, exist_ok=True)
    reports, performances, captures = [], [], []
    for role in selected:
        body = bodies[role]
        score = body.actor.advanced_score
        owned_fans = [fan for fan in fans if fan.body is body]
        probes = [PropProbe(
            fan.side+"-fan", fan.side,
            # The centroid of the actual rendered cylindrical handle, not a
            # duplicate authored target trajectory, is the measured grip.
            lambda t, fan=fan: fan.sample(t)[2]["pos"].mean(0),
            lambda t, side=fan.side: grip_frame(body, t, side)[0],
            lambda t, fan=fan: fan.geometry(t, diagnostic=True)) for fan in owned_fans]
        capture = args.out/(score.name+".npz")
        started = time.monotonic()
        print(json.dumps({"event": "audit_started", "role": score.name,
                          "score_sha256": source_hashes["tools/advanced_dance/score.py"]}), flush=True)
        report = audit_performance(score, fps=args.fps, temporal_samples=args.samples,
                                   shutter=args.shutter, cuts=cuts(args.mode), props=probes,
                                   capture_path=capture)
        report["source_hashes"] = source_hashes
        report["source_hashes_observed_when"] = "Audit startup, before cast creation; not relabeled to later files."
        report["source_scope"] = {
            "kinematic_inputs": [name for name in source_hashes
                                 if name in ("tools/advanced_dance/score.py", "tools/advanced_dance/anatomy.py",
                                             "tools/advanced_dance/clock.json", "assets/p3d/body_v1.npz")
                                 or name.startswith("engine/p3d/")],
            "costume_source": "Recorded as observed at startup; this audit does not run clothing simulation.",
            "clothing_simulation_audited": False,
        }
        rig_hash = hashlib.sha256()
        for name, array in (("neutral_pos", body.rig.neutral_pos), ("C", body.rig.C),
                            ("palm_L", body.rig.palm_n["L"]), ("palm_R", body.rig.palm_n["R"])):
            array = np.ascontiguousarray(array)
            rig_hash.update(json.dumps([name, list(array.shape), str(array.dtype)]).encode())
            rig_hash.update(array.tobytes())
        report["actor"] = {"height_m": body.rig.height, "build": body.rig.build,
                           "origin": body.actor.origin.tolist(), "seed": body.seed,
                           "mode": score.mode, "role": role, "scale": body.scale,
                           "frame_is_none": body.frame is None, "stoop": body.actor.stoop,
                           "life": body.actor.life, "rig_arrays_sha256": rig_hash.hexdigest()}
        report["elapsed_seconds"] = time.monotonic()-started
        path = args.out/(score.name+".json")
        path.write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps({"event": "audit_complete", "role": score.name,
                          "status": report["status"], "sample_count": report["sample_count"],
                          "error_count": report["error_count"], "review_flag_count": report["review_flag_count"],
                          "issues": report["issues"], "report": str(path)}), flush=True)
        reports.append(report)
        performances.append(score)
        captures.append(capture)
    if ensemble and args.role is None:
        cast = audit_cast_captures(performances, captures)
        cast["source_hashes"] = source_hashes
        (args.out/"cast.json").write_text(json.dumps(cast, indent=2)+"\n")
        print(json.dumps({"event": "cast_complete", "status": cast["status"], "issues": cast["issues"]}), flush=True)
    if any(report["error_count"] for report in reports):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
