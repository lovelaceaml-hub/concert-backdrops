"""A small authored humanoid performance with deterministic layered motion.

The figure is an original stylized stand-in, not a finished actor or a motion
capture library. Coordinates are metres, Z-up, with the figure facing -Y.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .events import DampedSpring, event_envelope
from .kinematics import solve_two_bone
from .math3d import Vec3, add, finite_number, length, mul, rotate_x, smootherstep, sub, unit

# Parent-before-child order is also the order used to apply pose matrices.
REST_BONES = {
    "pelvis": ((0.0, 0.0, 0.92), (0.0, 0.0, 1.04), None),
    "spine": ((0.0, 0.0, 1.04), (0.0, 0.0, 1.43), "pelvis"),
    "neck": ((0.0, 0.0, 1.43), (0.0, 0.0, 1.57), "spine"),
    "head": ((0.0, 0.0, 1.57), (0.0, 0.0, 1.85), "neck"),
}
for _side, _sign in (("L", 1.0), ("R", -1.0)):
    REST_BONES.update({
        f"upper_arm.{_side}": ((_sign * 0.195, 0.0, 1.43), (_sign * 0.40, -0.02, 1.18), "spine"),
        f"forearm.{_side}": ((_sign * 0.40, -0.02, 1.18), (_sign * 0.48, -0.06, 0.94), f"upper_arm.{_side}"),
        f"hand.{_side}": ((_sign * 0.48, -0.06, 0.94), (_sign * 0.50, -0.10, 0.83), f"forearm.{_side}"),
        f"thigh.{_side}": ((_sign * 0.115, 0.0, 0.98), (_sign * 0.115, -0.045, 0.54), "pelvis"),
        f"shin.{_side}": ((_sign * 0.115, -0.045, 0.54), (_sign * 0.115, 0.0, 0.10), f"thigh.{_side}"),
        f"foot.{_side}": ((_sign * 0.115, 0.0, 0.10), (_sign * 0.115, -0.20, 0.07), f"shin.{_side}"),
    })


@dataclass(frozen=True)
class HumanoidPose:
    bones: dict[str, tuple[Vec3, Vec3]]
    contacts: dict[str, Vec3]
    max_reach_error: float


def _gesture(phase, values):
    """C2 pose-to-pose transitions with intentional gesture accents."""
    phase %= 1.0
    for (a, p), (b, q) in zip(values, values[1:]):
        if phase <= b:
            u = smootherstep((phase - a) / (b - a))
            return add(mul(p, 1.0 - u), mul(q, u))
    return values[-1][1]


class HumanoidPerformance:
    """Layer authored intent, breathing, gaze, planted feet, and wrist lag.

    This is deliberately bounded and uses analytic IK. Every call is a pure
    function of seconds, seed, and configuration, including out-of-order calls.
    A contact error is returned if a configured pose exceeds its reach.
    """

    def __init__(self, *, action="conduct", strength=0.7, seed=2026, fps=60.0, events=()):
        if action not in ("idle", "conduct", "bow", "reach"):
            raise ValueError("action must be idle, conduct, bow, or reach")
        self.action = action
        self.strength = finite_number(strength, "strength")
        self.fps = finite_number(fps, "fps")
        if not 0 <= self.strength <= 1 or self.fps <= 0:
            raise ValueError("strength must be 0..1 and fps positive")
        self.events = tuple(dict(event) for event in events)
        rng = random.Random(seed)
        self.phase = rng.uniform(0.0, math.tau)
        self.period = rng.uniform(2.3, 2.7)
        self.wrist_lag = DampedSpring([(0.35, 0.035), (1.0, -0.025), (1.75, 0.02), (2.6, 0.0)], frequency_hz=1.6, damping_ratio=0.8)

    def sample(self, seconds) -> HumanoidPose:
        t = finite_number(seconds, "sample time")
        strength = self.strength
        breath = math.sin(t * 1.35 + self.phase)
        shift = (0.010 * math.sin(t * 0.57 + self.phase), 0.004 * math.sin(t * 0.73 + self.phase), 0.002 * breath)
        bow = 0.008 * breath
        if self.action == "bow":
            bow += 0.18 * strength * event_envelope(t * self.fps, [{"frame": 1.8 * self.fps, "attack_frames": 1.4 * self.fps, "release_frames": 2.0 * self.fps}])
        pelvis_head = add(REST_BONES["pelvis"][0], shift)
        pelvis_tail = add(REST_BONES["pelvis"][1], shift)
        spine_tail = add(pelvis_tail, rotate_x((0.0, 0.0, 0.39), bow))
        neck_tail = add(spine_tail, rotate_x((0.0, 0.0, 0.14), bow))
        # The head follows the torso, then a small audience gaze. There are no
        # face/eye meshes, preserving the warm abstract human-of-light style.
        gaze = 0.035 * math.sin(t * 0.43 + self.phase)
        head_direction = unit((0.018 * math.sin(t * 0.31 + self.phase), -math.sin(bow + gaze), math.cos(bow + gaze)))
        head_tail = add(neck_tail, mul(head_direction, 0.28))
        bones = {"pelvis": (pelvis_head, pelvis_tail), "spine": (pelvis_tail, spine_tail), "neck": (spine_tail, neck_tail), "head": (neck_tail, head_tail)}
        contacts, errors = {}, []
        accent = event_envelope(t * self.fps, self.events, fps=self.fps, cap=1.0) if self.events else 0.0
        for side, sign in (("L", 1.0), ("R", -1.0)):
            shoulder = add(spine_tail, (sign * 0.195, 0.0, 0.0))
            if self.action == "conduct":
                phase = t / self.period + (0.10 if side == "L" else 0.0)
                offset = _gesture(phase, [(0.0, (0.0, -0.015, 0.065)), (0.24, (0.035, -0.04, 0.13)),
                                         (0.48, (-0.015, 0.015, -0.075)), (0.78, (0.065, -0.01, 0.015)), (1.0, (0.0, -0.015, 0.065))])
                target = (sign * (0.30 + strength * offset[0]), -0.31 + strength * offset[1], 1.22 + strength * offset[2] + 0.035 * accent)
                target = add(target, shift)
            elif self.action == "reach":
                blend = event_envelope(t * self.fps, [{"frame": 2.2 * self.fps, "attack_frames": 1.6 * self.fps, "release_frames": 2.0 * self.fps}]) * strength
                rest = (sign * 0.46, -0.10, 0.96)
                offered = (sign * 0.27, -0.40, 1.23)
                target = add(add(mul(rest, 1.0 - blend), mul(offered, blend)), shift)
            else:
                target = add((sign * 0.46, -0.105 - 0.02 * breath, 0.97), shift)
            upper = length(sub(REST_BONES[f"upper_arm.{side}"][1], REST_BONES[f"upper_arm.{side}"][0]))
            lower = length(sub(REST_BONES[f"forearm.{side}"][1], REST_BONES[f"forearm.{side}"][0]))
            arm = solve_two_bone(shoulder, target, (sign * 0.85, 0.17, 1.16), upper, lower)
            bones[f"upper_arm.{side}"] = (shoulder, arm.joint)
            bones[f"forearm.{side}"] = (arm.joint, arm.end)
            lag = self.wrist_lag.sample(t).value * strength
            hand_length = length(sub(REST_BONES[f"hand.{side}"][1], REST_BONES[f"hand.{side}"][0]))
            hand_direction = unit((sign * 0.11, -0.50 - lag, -0.86 + lag))
            bones[f"hand.{side}"] = (arm.end, add(arm.end, mul(hand_direction, hand_length)))
            hip = add((sign * 0.115, 0.0, 0.98), shift)
            foot = REST_BONES[f"foot.{side}"][0]
            thigh = length(sub(REST_BONES[f"thigh.{side}"][1], REST_BONES[f"thigh.{side}"][0]))
            shin = length(sub(REST_BONES[f"shin.{side}"][1], REST_BONES[f"shin.{side}"][0]))
            leg = solve_two_bone(hip, foot, (sign * 0.115, -1.0, 0.5), thigh, shin)
            bones[f"thigh.{side}"] = (hip, leg.joint)
            bones[f"shin.{side}"] = (leg.joint, leg.end)
            bones[f"foot.{side}"] = (leg.end, add(leg.end, sub(REST_BONES[f"foot.{side}"][1], foot)))
            contacts[f"foot.{side}"] = leg.end
            errors.extend((arm.reach_error, leg.reach_error))
        return HumanoidPose(bones, contacts, max(errors, default=0.0))
