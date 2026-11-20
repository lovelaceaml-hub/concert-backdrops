"""Motion contracts: smooth time, planted contacts, and independent frame order."""
from __future__ import annotations

import math
import unittest

from pipeline.motion import CameraTrack, CubicSpline, DampedSpring, event_envelope, solve_two_bone
from pipeline.motion.character import HumanoidPerformance, REST_BONES
from pipeline.motion.math3d import length, sub


CAMERA_FIXTURE = {"seconds": [0, 1, 3, 6], "points": [[0, 3, 12], [2, 3.5, 10], [4, 4, 8], [7, 3, 5]],
                  "targets": [[0, 1, -2]], "easing": "smootherstep"}


class CurveTests(unittest.TestCase):
    def test_known_browser_coordinates_match(self):
        track = CameraTrack.from_dict(CAMERA_FIXTURE)
        expected = {1.5: (1.3103128948381968, 3.319630260978426, 10.689687105161804),
                    3.0: (4.0, 4.0, 8.0), 4.5: (6.315212771296501, 3.3025714680552483, 5.684787228703499)}
        for t, position in expected.items():
            for actual, wanted in zip(track.sample(t).position, position):
                self.assertAlmostEqual(actual, wanted, places=12)

    def test_velocity_acceleration_match_finite_differences(self):
        track = CameraTrack.from_dict(CAMERA_FIXTURE)
        dt = 1e-4
        for t in (0.3, 1.23, 2.67, 4.21, 5.8):
            before, at, after = track.sample(t - dt), track.sample(t), track.sample(t + dt)
            for i in range(3):
                self.assertAlmostEqual(at.velocity[i], (after.position[i] - before.position[i]) / (2 * dt), delta=2e-6)
                self.assertAlmostEqual(at.acceleration[i], (after.velocity[i] - before.velocity[i]) / (2 * dt), delta=2e-6)

    def test_spline_interpolates_nonuniform_knots_and_is_c2(self):
        curve = CubicSpline([0, 0.7, 2, 5], [(0, 1), (2, 3), (1, 4), (5, 7)])
        for t, point in zip(curve.seconds, curve.values):
            self.assertEqual(curve.sample(t).value, point)
        for t in (0.7, 2.0):
            a, b = curve.sample(t - 1e-7), curve.sample(t + 1e-7)
            for field in ("value", "velocity", "acceleration"):
                for left, right in zip(getattr(a, field), getattr(b, field)):
                    self.assertLess(abs(left - right), 5e-6)

    def test_camera_start_stop_and_out_of_order(self):
        track = CameraTrack.from_dict(CAMERA_FIXTURE)
        for time in (-1, 0, 6, 7):
            sample = track.sample(time)
            self.assertEqual(sample.velocity, (0, 0, 0))
            self.assertEqual(sample.acceleration, (0, 0, 0))
        ordered = {t: track.sample(t) for t in (0, 0.25, 3, 5.75, 6)}
        for t in (5.75, 0, 6, 0.25, 3, 0):
            self.assertEqual(track.sample(t), ordered[t])
        self.assertGreater(length(track.sample(3).velocity), 0.1)

    def test_invalid_camera_and_look_at_are_rejected(self):
        for spec in ({"points": [[0, 0, 0], [1, 0, 0]], "targets": [[0, 1, 0]]},
                     {**CAMERA_FIXTURE, "seconds": [0, 1, 1, 6]},
                     {**CAMERA_FIXTURE, "easing": "unknown"},
                     {**CAMERA_FIXTURE, "pacing": "arc-length"}):
            with self.assertRaises(ValueError):
                CameraTrack.from_dict(spec)
        coincident = CameraTrack([0, 1], [(0, 0, 0), (0, 0, 0)], [(0, 0, 0)])
        with self.assertRaisesRegex(ValueError, "coincide"):
            coincident.sample(0.5)

    def test_uniform_time_fallback_and_diagnostics(self):
        spec = dict(CAMERA_FIXTURE)
        spec.pop("seconds")
        track = CameraTrack.from_dict(spec, duration_seconds=6)
        self.assertEqual(track.seconds, (0, 2, 4, 6))
        report = track.diagnostics(60)
        self.assertTrue(report["endpoint_hold_is_c2"])
        self.assertGreater(report["peak_speed_m_s"], 0)
        self.assertLess(report["knot_continuity_residual"]["acceleration"], 1e-5)


class CharacterTests(unittest.TestCase):
    def test_ik_preserves_lengths_and_reports_unreachable_targets(self):
        for target in ((0.4, -0.8, 0), (0, 0, 0), (0, -5, 0)):
            solution = solve_two_bone((0, 0, 0), target, (0, 0, 1), 0.8, 0.6)
            self.assertAlmostEqual(length(sub(solution.joint, solution.root)), 0.8, places=8)
            self.assertAlmostEqual(length(sub(solution.end, solution.joint)), 0.6, places=8)
        self.assertTrue(solution.clamped)
        self.assertGreater(solution.reach_error, 3)
        with self.assertRaises(ValueError):
            solve_two_bone((0, 0, 0), (1, 0, 0), (0, 1, 0), -1, 1)

    def test_each_action_has_fixed_contacts_and_constant_bone_lengths(self):
        for action in ("idle", "conduct", "bow", "reach"):
            performance = HumanoidPerformance(action=action, seed=2026)
            for frame in range(0, 601, 3):
                pose = performance.sample(frame / 60)
                self.assertLess(pose.max_reach_error, 1e-10)
                for side in ("L", "R"):
                    self.assertLess(length(sub(pose.contacts[f"foot.{side}"], REST_BONES[f"foot.{side}"][0])), 1e-10)
                for name, (a, b) in pose.bones.items():
                    self.assertAlmostEqual(length(sub(b, a)), length(sub(REST_BONES[name][1], REST_BONES[name][0])), places=10)

    def test_frame_order_independent_and_different_seeds_are_not_identical(self):
        first = HumanoidPerformance(seed=12)
        second = HumanoidPerformance(seed=12)
        expected = {t: first.sample(t) for t in (-0.1, 0, 0.3, 1.9, 4.2, 10)}
        for t in (10, 0.3, -0.1, 4.2, 0, 1.9, 0):
            self.assertEqual(second.sample(t), expected[t])
        self.assertNotEqual(first.sample(2), HumanoidPerformance(seed=13).sample(2))


class SecondaryMotionTests(unittest.TestCase):
    def test_envelope_peaks_at_hit_with_c2_edges_and_shared_default_fps(self):
        event = {"frame": 60, "amplitude": 0.8, "attack_frames": 12, "release_frames": 24}
        self.assertEqual(event_envelope(60, [event]), 0.8)
        self.assertEqual(event_envelope(47, [event]), 0)
        self.assertEqual(event_envelope(85, [event]), 0)
        dt = 1e-3
        for t in (48, 60, 84):
            before, at, after = (event_envelope(t + offset, [event]) for offset in (-dt, 0, dt))
            self.assertLess(abs((after - before) / (2 * dt)), 1e-5)
            self.assertLess(abs((after - 2 * at + before) / (dt * dt)), 1e-3)
        default_event = {"frame": 60}
        self.assertAlmostEqual(event_envelope(52.5, [default_event], fps=60), 0.5)

    def test_soft_cap_is_bounded_and_joins_smoothly(self):
        for amplitude in (0, 0.25, 0.5, 0.75, 1, 2, 100):
            result = event_envelope(1, [{"frame": 1, "amplitude": amplitude}], cap=1)
            self.assertTrue(0 <= result <= 1)
        self.assertEqual(event_envelope(1, [{"frame": 1, "amplitude": 0.4}], cap=1), 0.4)
        self.assertEqual(event_envelope(1, [{"frame": 1, "amplitude": 0.4}], cap=None), 0.4)

    def test_spring_is_continuous_stable_and_independent_of_sampling_order(self):
        for damping in (0.4, 1.0, 1.4):
            spring = DampedSpring([(0.2, 1), (1.8, -0.5), (3.0, 0.0)], frequency_hz=2, damping_ratio=damping)
            expected = {t: spring.sample(t) for t in (0, 0.2, 0.8, 1.8, 3, 4, 8)}
            for t in (8, 0.8, 3, 0, 4, 1.8, 0.2):
                self.assertEqual(spring.sample(t), expected[t])
            for t in (0.2, 1.8, 3):
                before, after = spring.sample(t - 1e-8), spring.sample(t + 1e-8)
                self.assertLess(abs(after.value - before.value), 1e-6)
                self.assertLess(abs(after.velocity - before.velocity), 1e-4)
            self.assertLess(abs(spring.sample(8).value), 1e-6)
        with self.assertRaises(ValueError):
            DampedSpring([(1, 0), (0, 1)])


if __name__ == "__main__":
    unittest.main()
