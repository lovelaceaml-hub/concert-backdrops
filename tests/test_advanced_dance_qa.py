"""Exercise real FK and intentional failure cases in the motion repair audit."""
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "engine"))

from p3d.actor import Actor
from p3d import bodymath as bm
from tools.advanced_dance.qa import (PropProbe, audit_performance, capsule_clearance,
                                     quat_distance_deg, sample_times, audit_cast_captures,
                                     _segment_distances)
from tools.advanced_dance.cast_qa import audit_cast_fans, verify_capture_bytes
from tools.advanced_dance.props import PerformanceFan


class FixturePerformance:
    """Small deterministic real-rig fixture with independently injected faults."""
    duration = .2
    name = "audit-fixture"

    def __init__(self, *, slip=False, wrist=False, backwards=False, speed=0, floating=0, ankle=False):
        self.actor = Actor("woman", height=1.66, at=(1.3, 0, -.4), facing=23, life=False)
        self.rig = self.actor.rig
        self.slip, self.wrist, self.backwards = slip, wrist, backwards
        self.speed, self.floating = speed, floating
        self.ankle = ankle
        p = self.actor.mo.identity()
        D, P, _ = self.actor.mo.local_fk(p)
        self.lift = -self.rig.lowest(self.rig.matrices(D, P))
        self.actor.base_pose = self.pose

    def pose(self, t):
        p = self.actor.mo.identity()
        p.pos[1] = self.lift + self.floating
        p.pos[0] = self.speed*t + (.12*t if self.slip else 0)
        p.ground = 0
        if self.wrist:
            p.q[self.rig.idx["wrist.L"]] = bm.qx(np.pi/2)
        if self.backwards:
            p.q[self.rig.idx["lowerleg01.R"]] = bm.qx(-.15)
        if self.ankle:
            p.q[self.rig.idx["foot.R"]] = bm.qy(np.radians(110))
        return p

    def feet(self, t):
        targets = {s: self.rig.neutral_pos[self.rig.idx["foot."+s]].copy() for s in ("L", "R")}
        for target in targets.values():
            target[0] += self.speed*t
            target[1] += self.lift + self.floating
        return targets, {s: bm.IDENT.copy() for s in targets}, None

    def contacts(self, t):
        return {"L": not bool(self.speed), "R": not bool(self.speed)}


class AuditTests(unittest.TestCase):
    def report(self, performance, **kw):
        return audit_performance(performance, fps=60, temporal_samples=2, shutter=.35, **kw)

    def checks(self, report):
        return {issue["check"] for issue in report["issues"]}

    def test_exact_shutter_schedule_and_boundary_probes(self):
        times, frames = sample_times(1, 60, 2, .35, (.333,))
        self.assertEqual(len(frames), 60)
        self.assertAlmostEqual(times[0], -.35/60/2)
        self.assertIn(round(1/60-.35/60/2, 10), times)
        self.assertIn(.333, times)
        self.assertIn(.33299, times)
        self.assertIn(1, times)
        self.assertEqual(len(times), 124)
        cut_times, _ = sample_times(1, 60, 2, .35, cuts=(.5,))
        self.assertIn(.5, cut_times)
        self.assertNotIn(round(.5-.35/60/2, 10), cut_times)
        with self.assertRaises(ValueError):
            sample_times(.123, 60)

    def test_healthy_fixed_rig_preserves_bones_and_foot_anchors(self):
        report = self.report(FixturePerformance())
        self.assertEqual(report["error_count"], 0, report["issues"])
        self.assertEqual(report["output_frames"], 12)
        self.assertEqual(report["finite_sample_count"], report["sample_count"])
        self.assertLess(report["metrics"]["bone_length_error"]["value"], 1e-12)
        self.assertLess(report["metrics"]["support_drift"]["value"], 1e-12)
        self.assertTrue(report["scope"]["skinned_foot_vertices"])

    def test_planted_foot_slide_is_detected_in_final_skeleton(self):
        report = self.report(FixturePerformance(slip=True))
        self.assertIn("support_drift", self.checks(report))
        self.assertIn("ankle_target_error", self.checks(report))
        self.assertEqual(report["status"], "blocked")

    def test_wrist_overbend_and_reversed_knee_are_separate_failures(self):
        report = self.report(FixturePerformance(wrist=True, backwards=True))
        self.assertIn("wrist_local_rotation", self.checks(report))
        self.assertIn("knee_flex_min", self.checks(report))
        self.assertEqual(report["status"], "blocked")

    def test_locked_foot_can_still_have_an_awkward_ankle_twist(self):
        report = self.report(FixturePerformance(ankle=True))
        self.assertLess(report["metrics"]["support_drift"]["value"], 1e-12)
        self.assertIn("ankle_axial_twist", self.checks(report))
        self.assertIn("support_pelvis_yaw_difference", self.checks(report))

    def test_broken_final_fk_is_detected_even_with_valid_source_pose(self):
        p = FixturePerformance()
        original = p.actor.frame

        def changed(t, **kwargs):
            frame = dict(original(t, **kwargs))
            frame["P"] = frame["P"].copy()
            frame["P"][p.rig.idx["wrist.L"], 0] += .03
            return frame

        p.actor.frame = changed
        report = self.report(p)
        self.assertIn("bone_length_error", self.checks(report))

    def test_real_prop_attachment_and_planted_float_are_detected(self):
        p = FixturePerformance(floating=.04)
        prop = PropProbe("detached-fan", "R", lambda t: p.actor.palm(t, "R")[0] + [.05, 0, 0])
        report = self.report(p, props=(prop,))
        self.assertIn("prop_attachment_error", self.checks(report))
        self.assertIn("support_sole_gap", self.checks(report))
        self.assertEqual(report["scope"]["prop_probes"], ["detached-fan"])

    def test_intentional_fast_motion_is_review_not_automatic_failure(self):
        report = self.report(FixturePerformance(speed=5))
        self.assertIn("palm_speed", self.checks(report))
        self.assertEqual(report["error_count"], 0, report["issues"])
        self.assertEqual(report["status"], "review_required")

    def test_quaternion_sign_and_capsule_clearance(self):
        q = bm.qx(.6)
        self.assertAlmostEqual(float(quat_distance_deg(q, -q)), 0)
        d = capsule_clearance([[2, .5, 0], [.1, .5, 0]], [[0, 0, 0]], [[0, 1, 0]], [.2], [.2])
        np.testing.assert_allclose(d[:, 0], [1.8, -.1], atol=1e-12)

    def test_crossed_finite_segments_and_separate_parallel_segments(self):
        d = _segment_distances([[-1, 0, 0]], [[1, 0, 0]], [[0, -1, 0], [-1, 2, 0]], [[0, 1, 0], [1, 2, 0]])
        np.testing.assert_allclose(d[0], [0, 2], atol=1e-12)

    def test_inter_person_overlap_uses_actual_saved_fk(self):
        first, second = FixturePerformance(), FixturePerformance()
        second.name = "second-person"
        with tempfile.TemporaryDirectory() as temp:
            paths = [Path(temp)/"first.npz", Path(temp)/"second.npz"]
            for perf, path in zip((first, second), paths):
                self.report(perf, capture_path=path)
            report = audit_cast_captures([first, second], paths)
            self.assertEqual(report["status"], "review_required")
            self.assertEqual(report["sample_count"], 13)
            self.assertLess(report["pairs"][0]["value"], -.05)

    def test_capture_receipt_rejects_changed_snapshot_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"pose.npz"
            report = self.report(FixturePerformance(), capture_path=path)
            verify_capture_bytes(path, report)
            data = bytearray(path.read_bytes())
            data[len(data)//2] ^= 1
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "hash-bound"):
                verify_capture_bytes(path, report)

    def test_cast_fan_probe_reuses_real_fk_without_resolving_or_leaking_cache(self):
        performers = [FixturePerformance(), FixturePerformance()]
        performers[1].name = "second-person"
        bodies = []
        for perf in performers:
            perf.fan_open = lambda t, side: 1.0
            perf.actor.advanced_score = perf
            bodies.append(SimpleNamespace(actor=perf.actor, rig=perf.rig, frame=None, scale=1.0,
                                          where=perf.actor.where))
        fan = PerformanceFan(bodies[0], "R", points=100)
        with tempfile.TemporaryDirectory() as temp:
            paths = [Path(temp)/f"person{i}.npz" for i in range(2)]
            for perf, path in zip(performers, paths):
                self.report(perf, capture_path=path)
            expected = [fan.geometry(float(t), diagnostic=True).copy() for t in np.arange(13)/60]
            before = [dict(perf.actor._cache) for perf in performers]
            original_geometry = fan.geometry
            seen = []

            def geometry(t, diagnostic=False):
                value = original_geometry(t, diagnostic)
                np.testing.assert_allclose(value, expected[round(t*60)], atol=1e-12)
                seen.append(t)
                return value

            fan.geometry = geometry
            for perf in performers:
                perf.actor.base_pose = lambda t: (_ for _ in ()).throw(AssertionError("FK was unnecessarily solved again"))
            report = audit_cast_fans(bodies, [fan], paths)
            self.assertEqual(report["sample_count"], 13)
            self.assertEqual(len(seen), 13)
            for perf, cache in zip(performers, before):
                self.assertEqual(list(perf.actor._cache), list(cache))


if __name__ == "__main__":
    unittest.main()
