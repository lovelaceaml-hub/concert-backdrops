"""Focused checks of actual captured rig motion and support, without rendering."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "engine"))

from p3d.actor import Actor
from tools.concert_dance.performance import install_dance


class DancePerformanceTests(unittest.TestCase):
    def make(self, **kwargs):
        actor = Actor("woman", height=1.7, at=(1.0, -2.0), facing=21.0, motion="stand", life=False)
        return actor, install_dance(actor, **kwargs)

    def test_random_access_matches_a_fresh_actor(self):
        actor, perf = self.make()
        times = [0.0, 1.3, 2.0, 3.77, 7.4, perf.capture_end, perf.settle_end, 17.9,
                 perf.capture_start-1e-7, perf.settle_end-1e-7]
        forward = {t: actor.frame(t, life=False)["P"].copy() for t in times}
        for t in reversed(times):
            np.testing.assert_array_equal(actor.frame(t, life=False)["P"], forward[t])
        other, _ = self.make()
        for t in [times[i] for i in [9, 6, 8, 2, 4, 0, 7, 3, 1, 5]]:
            np.testing.assert_array_equal(other.frame(t, life=False)["P"], forward[t])

    def test_capture_and_settle_preserve_root_travel(self):
        actor, perf = self.make()
        start = actor.frame(perf.capture_start, life=False)["P"][actor.rig.idx["root"]]
        end = actor.frame(perf.capture_end, life=False)["P"][actor.rig.idx["root"]]
        held = actor.frame(17.9, life=False)["P"][actor.rig.idx["root"]]
        self.assertGreater(np.linalg.norm((end - start)[[0, 2]]), 1.0)
        self.assertLess(np.linalg.norm((held - end)[[0, 2]]), 0.001)

    def test_supported_heel_does_not_reanchor_after_one_point_five_seconds(self):
        actor, perf = self.make()
        long_supports = [s for s in perf.supports if s.end-s.start > 2.0]
        self.assertTrue(long_supports)
        support = max(long_supports, key=lambda s: s.end-s.start)
        source_times = np.linspace(support.start+0.3, support.end-0.3, 16)
        times = [perf.scene_time(t) for t in source_times]
        anchors = [perf.stance_start(t, support.side) for t in times]
        self.assertLess(np.ptp(anchors), 1e-12)
        rows = [perf.diagnostics(t)["feet"]["L" if support.side == 0 else "R"] for t in times]
        self.assertLess(max(r["horizontal_residual_m"] for r in rows), 0.025)

    def test_boundaries_are_continuous_and_limb_lengths_remain_finite(self):
        actor, perf = self.make()
        for t in [perf.prepare_start, perf.capture_start, perf.capture_end, perf.settle_end]:
            before = actor.frame(t-1e-4, life=False)["P"]
            after = actor.frame(t+1e-4, life=False)["P"]
            self.assertLess(np.max(np.linalg.norm(after-before, axis=1)), 0.003, f"boundary {t}")
        for t in np.linspace(0, 18, 73):
            frame = actor.frame(t, life=False)
            unlocked = actor.frame(t, lock=False, life=False)
            self.assertTrue(np.isfinite(frame["P"]).all())
            for side in ("L", "R"):
                indices = [actor.rig.idx[n+side] for n in ("upperleg01.", "lowerleg01.", "foot.")]
                length = np.linalg.norm(np.diff(frame["P"][indices], axis=0), axis=1)
                self.assertTrue(np.all((length > 0.25) & (length < 0.6)))
                self.assertLessEqual(np.linalg.norm(frame["P"][indices[-1]]-unlocked["P"][indices[-1]]),
                                     perf.max_foot_correction+0.002)


if __name__ == "__main__":
    unittest.main()
