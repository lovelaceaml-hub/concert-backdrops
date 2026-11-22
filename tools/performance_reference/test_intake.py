"""Integration checks for real VFR decoding, source clocks and overwrite safety."""
import hashlib
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.performance_reference.intake import IntakeError, ROOT, _choose, intake


class ReferenceIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="performance-reference-test-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.folder = Path(cls.temp.name)
        cls.video = cls.folder / "vfr-nonzero.mkv"
        subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
            "testsrc2=size=96x64:rate=10:duration=1",
            "-vf", "select=eq(n\\,0)+eq(n\\,2)+eq(n\\,3)+eq(n\\,6)+eq(n\\,9),setpts=PTS+5/TB",
            "-fps_mode", "vfr", "-c:v", "ffv1", "-threads", "1", str(cls.video),
        ], check=True, capture_output=True)
        cls.output = cls.folder / "result"
        cls.manifest = intake(cls.video, "https://example.invalid/generated-pipeline-fixture",
                              "generated-vfr-fixture", ".15", ".9", cls.output,
                              samples=4, purpose="pipeline_fixture")

    def test_source_pts_vfr_and_exclusive_boundary(self):
        m = self.manifest
        self.assertEqual(m["source"]["first_video_pts_seconds"], 5.0)
        self.assertEqual(m["source"]["decoded_frame_count"], 5)
        self.assertGreater(m["source"]["observed_frame_interval_max_seconds"],
                           m["source"]["observed_frame_interval_min_seconds"])
        self.assertEqual([s["actual_video_time_seconds"] for s in m["samples"]], [.2, .3, .6])
        self.assertEqual([s["source_pts_seconds"] for s in m["samples"]], [5.2, 5.3, 5.6])
        self.assertEqual([s["decoded_source_frame_index"] for s in m["samples"]], [1, 2, 3])
        self.assertEqual(sum(len(s["requested_times_seconds"]) for s in m["samples"]), 4)
        self.assertEqual(m["sampling"]["actual_unique_count"], 3)
        self.assertFalse((self.output / "INTAKE-INCOMPLETE.txt").exists())

    def test_media_receipts_and_review_boundaries(self):
        m = json.loads((self.output / "manifest.json").read_text())
        self.assertEqual(m["purpose"], "pipeline_fixture")
        self.assertEqual(m["review"]["technical"]["status"], "passed")
        self.assertEqual(m["review"]["visual"]["status"], "not_reviewed")
        self.assertEqual(m["review"]["owner_approval"]["status"], "unrecorded")
        self.assertEqual(m["motion_reconstruction"]["status"], "not_attempted")
        self.assertFalse(m["acquisition"]["download_attempted"])
        for sample in m["samples"]:
            for path_key, hash_key in (("frame_path", "frame_sha256"), ("timecoded_path", "timecoded_sha256")):
                self.assertEqual(hashlib.sha256((self.output / sample[path_key]).read_bytes()).hexdigest(), sample[hash_key])

    def test_existing_output_is_preserved(self):
        before = (self.output / "manifest.json").read_bytes()
        with self.assertRaisesRegex(IntakeError, "Refusing to overwrite"):
            intake(self.video, "https://example.invalid/fixture", "fixture", 0, .5, self.output)
        self.assertEqual((self.output / "manifest.json").read_bytes(), before)

    def test_no_frame_in_range_does_not_seek_outside_it(self):
        output = self.folder / "empty-range"
        with self.assertRaisesRegex(IntakeError, "No decoded frame PTS"):
            intake(self.video, "https://example.invalid/fixture", "fixture", ".61", ".89", output)
        self.assertFalse(output.exists())

    def test_output_inside_code_is_rejected(self):
        with self.assertRaisesRegex(IntakeError, "must be Git-ignored"):
            intake(self.video, "https://example.invalid/fixture", "fixture", 0, .5,
                   ROOT / "tools/performance_reference/should-not-exist")

    def test_unknown_final_duration_cannot_extend_coverage(self):
        frames = [dict(index=0, pts=0, time=Fraction(0), duration=Fraction(1)),
                  dict(index=1, pts=1, time=Fraction(1), duration=None)]
        with self.assertRaisesRegex(IntakeError, "last proven timestamp"):
            _choose(frames, Fraction(0), Fraction(100), 12)
        chosen, end = _choose(frames, Fraction(0), Fraction(1), 2)
        self.assertIsNone(end)
        self.assertEqual([item["frame"]["index"] for item in chosen], [0])

    def test_playlist_dependencies_are_rejected(self):
        playlist = self.folder / "local-dependencies.m3u8"
        playlist.write_text("#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:1\n#EXTINF:1,\n"
                            + str(self.video) + "\n#EXT-X-ENDLIST\n")
        output = self.folder / "playlist-result"
        with self.assertRaisesRegex(IntakeError, "whitelist"):
            intake(playlist, "https://example.invalid/fixture", "fixture", 0, .5, output)
        self.assertFalse(output.exists())

    def test_anamorphic_body_proportions_are_not_silently_changed(self):
        anamorphic = self.folder / "anamorphic.mkv"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(self.video),
                        "-vf", "setsar=2/1", "-c:v", "ffv1", "-threads", "1", str(anamorphic)],
                       check=True, capture_output=True)
        output = self.folder / "anamorphic-result"
        with self.assertRaisesRegex(IntakeError, "Non-square sample aspect ratio"):
            intake(anamorphic, "https://example.invalid/fixture", "fixture", 0, .5, output,
                   assume_square_pixels=True)
        self.assertFalse(output.exists())

    def test_unspecified_pixel_geometry_requires_explicit_assertion(self):
        unspecified = self.folder / "unspecified-sar.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(self.video),
                        "-vf", "setsar=0", "-c:v", "libx264", "-threads", "1", str(unspecified)],
                       check=True, capture_output=True)
        output = self.folder / "unspecified-sar-result"
        with self.assertRaisesRegex(IntakeError, "SAR is unspecified"):
            intake(unspecified, "https://example.invalid/fixture", "fixture", 0, .5, output)
        m = intake(unspecified, "https://example.invalid/fixture", "fixture", 0, .5, output,
                   samples=1, assume_square_pixels=True, purpose="pipeline_fixture")
        self.assertEqual(m["source"]["pixel_geometry_policy"], "caller_asserted_square_pixels_for_unspecified_stream")


if __name__ == "__main__":
    unittest.main()
