"""Check decoded motion heuristics against tiny, deliberately different movies."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from pipeline.delivery import PROFILES, video_encoding_args
from pipeline.temporal import scan_motion
from test_contract import project_fixture


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is required for temporal decoding tests")
class TemporalDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.project = project_fixture(self.root)
        self.project.data["shots"] = [self.project.shots[0]]
        self.project.data["timing"]["events"] = []
        self.frames = self.root / "frames"
        self.frames.mkdir()

    def encode(self, values):
        self.project.shots[0]["end_frame_exclusive"] = len(values)
        for frame, value in enumerate(values):
            picture = Image.fromarray(value, "RGB") if isinstance(value, np.ndarray) else Image.new("RGB", (64, 36), (value, value, value))
            picture.save(self.frames / f"frame_{frame:06d}.png")
        movie = self.root / "test.mp4"
        process = subprocess.run(["ffmpeg", "-v", "error", "-y", "-filter_threads", "1", "-framerate", str(self.project.fps), "-i", str(self.frames / "frame_%06d.png"), "-frames:v", str(len(values)), *video_encoding_args(self.project.fps, PROFILES["h264"]), "-an", str(movie)], capture_output=True, text=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stderr)
        return movie

    def test_real_alternating_brightness_is_detected(self):
        report = scan_motion(self.project, self.encode([70, 180] * 12))
        self.assertTrue(report["scan_complete"])
        self.assertEqual(report["decoded_frames"], 24)
        self.assertGreater(report["flicker_candidate_count"], 0)
        self.assertGreater(report["maximum_second_difference"], 0.1)
        self.assertEqual(len(report["half_second_windows"]), 2)

    def test_smooth_exposure_ramp_is_not_called_flicker(self):
        report = scan_motion(self.project, self.encode([70 + 3 * frame for frame in range(24)]))
        self.assertEqual(report["flicker_candidate_count"], 0)
        self.assertEqual(report["shimmer_candidate_count"], 0)

    def test_declared_flash_is_excluded_but_unmarked_flash_is_reported(self):
        values = [110] * 24
        values[12] = 230
        movie = self.encode(values)
        self.assertGreater(scan_motion(self.project, movie)["flicker_candidate_count"], 0)
        self.project.data["timing"]["events"] = [{"frame": 12, "kind": "intentional_flash"}]
        report = scan_motion(self.project, movie)
        self.assertEqual(report["flicker_candidate_count"], 0)
        self.assertEqual(report["shimmer_candidate_count"], 0)
        self.assertEqual(report["excluded_intervals"][0]["reason"], "declared_flash")

    def test_local_shimmer_is_detected_without_global_brightness_flicker(self):
        y, x = np.indices((36, 64))
        checker = ((x // 4 + y // 4) % 2) * 120 + 60
        pictures = [np.repeat((checker if frame % 2 else 240 - checker)[:, :, None], 3, axis=2).astype(np.uint8) for frame in range(24)]
        report = scan_motion(self.project, self.encode(pictures))
        self.assertGreater(report["shimmer_candidate_count"], 0)
        self.assertEqual(report["flicker_candidate_count"], 0)
        self.assertIn("not measurements of physical camera jerk", report["interpretation"])

    def test_real_frozen_movie_has_a_long_still_warning(self):
        report = scan_motion(self.project, self.encode([120] * 60))
        self.assertGreater(report["longest_still_seconds"], 1.5)
        self.assertTrue(any("Nearly frozen" in message for message in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
