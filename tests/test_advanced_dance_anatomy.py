"""Regressions for actual native-rig hand, wrist and fan attachment defects."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "engine"))

from p3d.actor import Actor
from p3d import bodymath as bm
from tools.advanced_dance.anatomy import AnatomyController, grip_frame, inspect_hand
from tools.cinematic_ten.dancers_motion import DanceScore


class AnatomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actor = Actor("woman", height=1.66, life=False)
        cls.control = AnatomyController(cls.actor)

    def test_historical_world_pointing_wrist_kink_is_corrected(self):
        actor, control = self.actor, self.control
        old = DanceScore(actor).pose(0.0)
        targets = {s: actor.mo._hand_end(old, s, "palm") for s in "LR"}
        for side in "LR":
            self.assertGreater(inspect_hand(actor, old, side)["wrist_rotation_deg"], 120)
            report = control.hand(old, side, targets[side])
            self.assertLess(inspect_hand(actor, old, side)["wrist_rotation_deg"], 20)
            self.assertLess(report.target_error_m, .001)

    def test_unreachable_targets_do_not_stretch_bones_or_fold_the_wrist(self):
        actor, control, rig = self.actor, self.control, self.actor.rig
        pose = actor.mo.identity()
        report = control.hand(pose, "L", (2.2, 2.4, .6), fingers=(0, -1, 0))
        _, points, _ = actor.mo.local_fk(pose)
        index = [rig.idx[n + ".L"] for n in ("upperarm01", "lowerarm01", "wrist")]
        lengths = np.linalg.norm(np.diff(points[index], axis=0), axis=1)
        neutral = np.linalg.norm(np.diff(rig.neutral_pos[index], axis=0), axis=1)
        np.testing.assert_allclose(lengths, neutral, atol=.007, rtol=0)
        self.assertGreater(report.target_error_m, 1.0)
        self.assertLessEqual(abs(report.wrist_flex_deg), 35.0 + 1e-8)
        self.assertLessEqual(abs(report.wrist_deviation_deg), 18.0 + 1e-8)
        self.assertLessEqual(abs(report.wrist_twist_deg), 10.0 + 1e-8)
        self.assertLessEqual(report.elbow_bend_deg, 145.5)
        self.assertGreaterEqual(report.elbow_bend_deg, 15.0)

    def test_forearm_normal_crossing_back_hemisphere_has_no_180_degree_snap(self):
        actor, control = self.actor, self.control
        last = None
        maximum = 0.0
        for angle in np.linspace(-np.pi, np.pi, 181):
            pose = actor.mo.identity()
            control.hand(pose, "R", (-.42, 1.14, .32),
                         normal=(np.sin(angle), 0, np.cos(angle)))
            _, _, rotation = actor.mo.local_fk(pose)
            q = rotation[actor.rig.idx["wrist.R"]]
            if last is not None:
                delta = np.degrees(2 * np.arccos(np.clip(abs(np.dot(last, q)), 0, 1)))
                maximum = max(maximum, delta)
            last = q
        self.assertLess(maximum, 15.0)

    def test_random_seek_does_not_change_solved_hands(self):
        actor, control = self.actor, self.control

        def solve(t):
            pose = actor.mo.identity()
            pose.rot = bm.qy(t * .8)
            target = actor.rig.neutral_pos[0] + bm.qrot(
                pose.rot, [.44 + .08 * np.sin(t), .27 + .13 * np.cos(t), .24])
            control.hand(pose, "L", target, flourish=np.sin(t), grip=.5+.4*np.cos(t))
            return pose.q.copy()

        times = [0.0, 1.7, 3.1, .3, 8.0, 5.2]
        first = {t: solve(t) for t in times}
        for t in reversed(times):
            np.testing.assert_array_equal(first[t], solve(t))

    def test_launch_into_chasse_has_no_pronation_flip_between_shutter_samples(self):
        # This exact phrase previously turned the left hand by 97 degrees in
        # one 1/120-second interval while its palm target moved smoothly.
        from tools.advanced_dance.score import AdvancedScore
        actor = Actor("woman", height=1.66, life=False)
        score = AdvancedScore(actor)
        previous = None
        maximum = 0.0
        for t in np.arange(14.65, 15.151, 1/120):
            _, _, rotation = actor.mo.local_fk(score.pose(float(t)))
            q = rotation[actor.rig.idx["wrist.L"]]
            if previous is not None:
                speed = np.degrees(2 * np.arccos(np.clip(abs(np.dot(previous, q)), 0, 1))) * 120
                maximum = max(maximum, speed)
            previous = q
        self.assertLess(maximum, 900.0)

    def test_thumb_opposition_reaches_index_side_and_is_mirrored(self):
        actor, control, rig = self.actor, self.control, self.actor.rig
        closed = actor.mo.identity()
        for side in "LR":
            control.shape_hand(closed, side)
            self.assertLess(control.thumb_calibration[side]["pad_target_residual_m"], .002)
        d, points, _ = actor.mo.local_fk(closed)
        tips = {}
        for side in "LR":
            tips[side] = []
            for finger in (1, 2):
                b = rig.idx[f"finger{finger}-3.{side}"]
                tips[side].append(points[b] + bm.qrot(d[b], rig.tail[b]-rig.head[b]))
            distance = np.linalg.norm(tips[side][0] - tips[side][1])
            self.assertGreater(distance, .008)
            self.assertLess(distance, .021)
        np.testing.assert_allclose(tips["L"], np.asarray(tips["R"]) * [-1, 1, 1], atol=1e-9)

    def test_fan_frame_uses_final_palm_and_is_orthonormal(self):
        actor = Actor("woman", height=1.66, at=(2, -3), facing=35, life=False)
        control = AnatomyController(actor)

        def score(t):
            pose = actor.mo.identity()
            control.hand(pose, "R", (-.45, 1.15 + .1 * np.sin(t), .28))
            pose.ground, pose.contact = 0.0, None
            return pose

        actor.base_pose = score

        class BodyProxy:
            scale = 1.0

            def __init__(self, actor):
                self.actor = actor

            def where(self, *args, **kw):
                return self.actor.where(*args, **kw)

        body = BodyProxy(actor)
        for t in (0.0, 1.0, 2.0):
            centre, across, outward, normal = grip_frame(body, t)
            palm = actor.where(t, "palm.R")
            np.testing.assert_allclose(centre, palm + .024*outward + .010*normal, atol=1e-12)
            basis = np.stack([across, outward, normal], 1)
            np.testing.assert_allclose(basis.T @ basis, np.eye(3), atol=1e-12)
            self.assertGreater(np.linalg.det(basis), .99999)

    def test_invalid_targets_fail_visibly(self):
        pose = self.actor.mo.identity()
        for kwargs in (dict(palm_at=(np.nan, 1, 0)), dict(palm_at=(0, 1, 0), normal=(0, 0, 0)),
                       dict(palm_at=(0, 1, 0), fingers=(0, 0, 0))):
            with self.assertRaises(ValueError):
                self.control.hand(pose, "L", **kwargs)


if __name__ == "__main__":
    unittest.main()
