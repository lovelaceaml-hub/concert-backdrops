"""Focused checks for deterministic fan posing and credible foot support.

Run with PYTHONPATH=engine:. .venv/bin/python -m unittest \
    tools.concert_fan.test_performance
"""
import unittest

import numpy as np

from p3d.actor import Actor
from tools.concert_fan.performance import BASE_PLACEMENTS, install_performance


def performer(role):
    actor = Actor("woman", height=1.65, at=BASE_PLACEMENTS[role],
                  facing=0, motion="stand", seed=901+role)
    return actor, install_performance(actor, role)


class PerformanceTests(unittest.TestCase):
    def test_random_access_matches_increasing_time(self):
        times = (0, .000001, .27, 1.6, 4.7, 8.31, 12.83, 16.2, 19.9, 20)
        for role in range(3):
            forward, _ = performer(role)
            sought, _ = performer(role)
            expected = {t: forward.frame(t)["M"].copy() for t in times}
            for index in (7, 2, 9, 0, 6, 1, 4, 3, 8, 5):
                t = times[index]
                np.testing.assert_array_equal(sought.frame(t)["M"], expected[t])

    def test_support_stays_fixed_and_soles_stay_above_floor(self):
        for role in range(3):
            _, performance = performer(role)
            report = performance.contact_report(samples=241)
            self.assertLess(report["max_ankle_target_error_m"], 2e-6)
            self.assertLess(report["max_planted_ankle_step_m"], 1e-6)
            self.assertGreater(report["minimum_foot_vertex_height_m"], -1e-6)
            self.assertLess(report["max_wrist_angle_step_deg"], 5)

    def test_opening_moves_and_ending_settles(self):
        for role in range(3):
            actor, performance = performer(role)
            wrist = actor.rig.idx["wrist.R"]
            first = actor.frame(0)["P"][wrist]
            after = actor.frame(.25)["P"][wrist]
            self.assertGreater(np.linalg.norm(after-first), .015)
            start = performance.pose(0).pos[[0, 2]]
            finish = performance.pose(20).pos[[0, 2]]
            self.assertGreater(np.linalg.norm(finish-start), .04)
            P = performance.pose(20)
            Q = performance.pose(20.25)
            np.testing.assert_array_equal(P.pos, Q.pos)
            np.testing.assert_array_equal(P.q, Q.q)
            self.assertEqual(performance.diagnostics(20)["contact"], {"L": True, "R": True})

    def test_cache_clock_uses_canonical_time(self):
        a, _ = performer(0)
        b, _ = performer(0)
        first = a.frame(5.1234561)["M"]
        second = b.frame(5.1234564)["M"]
        np.testing.assert_array_equal(first, second)


if __name__ == "__main__":
    unittest.main()
