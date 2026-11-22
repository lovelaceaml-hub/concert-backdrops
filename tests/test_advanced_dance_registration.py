"""Real clock, original-speed audio and exact cloth-reuse acceptance checks."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "engine"))

from pipeline import kit
from pipeline.project import PipelineError, Project, validate
from tools.advanced_dance import prepare


class AdvancedRegistrationTests(unittest.TestCase):
    def test_both_actual_renderers_have_exact_native_clocks_and_reviewed_cuts(self):
        for mode, cuts in (("solo", [447, 882, 1319]), ("ensemble", [456, 917, 1370])):
            with self.subTest(mode=mode):
                path = ROOT / f"projects/advanced-dance-{mode}/project.json"
                data = json.loads(path.read_text())
                project = Project(ROOT, path, data)
                validate(project, check_files=False)
                scene = data["shots"][0]["scene"]
                module = kit.scene_module(ROOT, scene)
                contract = kit.module_contract(module, scene)
                self.assertEqual(contract["output_frame_count"], 1920)
                self.assertEqual(contract["cut_frames"], cuts)
                self.assertEqual(contract["source_start_frame"], 0)
                self.assertEqual(project.seconds, 32.0)
                self.assertEqual(project.fps, 60)
                for quality in ("review", "final"):
                    preset = project.settings(quality)
                    self.assertEqual((preset["width"], preset["height"], preset["temporal_samples"]),
                                     (1920, 1080, 2))
                self.assertEqual(data["production"]["render_workers"], 3)
                self.assertFalse(data["production"]["allow_local_gpu"])
                self.assertFalse(data["production"]["allow_paid_services"])

    def test_audio_clock_cues_and_actual_renderer_camera_cuts_agree(self):
        clocks = json.loads((ROOT / "tools/advanced_dance/clock.json").read_text())
        for mode in ("solo", "ensemble"):
            data = json.loads((ROOT / f"projects/advanced-dance-{mode}/project.json").read_text())
            clock = clocks[mode]
            self.assertEqual(len(data["timing"]["events"]), 65)
            self.assertFalse(data["timing"]["manually_verified"])
            self.assertTrue(all(not row["confirmed"] for row in data["timing"]["events"]))
            frames = [row["frame"] for row in data["timing"]["events"]]
            self.assertEqual(frames, [round(t*60) for t in clock["beat_seconds"]])
            self.assertEqual([frames[b] for b in (16, 32, 48)],
                             list(kit.scene_spec(data["shots"][0]["scene"])["cut_frames"]))
            source = ROOT / clock["audio_source"]
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), clock["source_sha256"])

    def test_clock_drift_and_hidden_retiming_are_rejected(self):
        path = ROOT / "projects/advanced-dance-solo/project.json"
        original = json.loads(path.read_text())
        for change in (lambda d: d["video"].update(fps=30),
                       lambda d: d["shots"][0].update(end_frame_exclusive=1921),
                       lambda d: d["shots"][0].update(params={"speed": 1.5})):
            data = copy.deepcopy(original)
            change(data)
            with self.assertRaises(PipelineError):
                validate(Project(ROOT, path, data), check_files=False)
        module = kit.scene_module(ROOT, kit.ADVANCED_SOLO_SCENE)
        with patch.object(module, "CUTS", (7.5, 14.7, 22.0)), self.assertRaises(PipelineError):
            kit.module_contract(module, kit.ADVANCED_SOLO_SCENE)

    def test_single_role_bake_constructor_does_not_construct_the_other_four_performers(self):
        with patch("tools.advanced_dance.costume.make_body") as factory, \
                patch("tools.advanced_dance.score.install") as install:
            body = prepare.build_one("ensemble", 3)
            self.assertIs(body, factory.return_value)
            factory.assert_called_once()
            self.assertEqual(factory.call_args.kwargs["role"], 3)
            self.assertTrue(factory.call_args.kwargs["ensemble"])
            self.assertEqual(install.call_args.kwargs, {"ensemble": True, "role": 3})
        self.assertEqual(prepare.selected_roles("ensemble", 3), (3,))
        for mode, role in (("solo", 1), ("ensemble", 5), ("ensemble", -1), ("ensemble", True)):
            with self.assertRaises(ValueError):
                prepare.selected_roles(mode, role)

    def test_changed_source_audio_fails_before_output_or_ffmpeg(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tools/advanced_dance").mkdir(parents=True)
            (root / "wrong.mp3").write_bytes(b"changed source recording")
            (root / "tools/advanced_dance/clock.json").write_text(json.dumps({
                "solo": {"audio_source": "wrong.mp3", "source_sha256": "0"*64,
                         "audio_start_seconds": 0.0}}))
            with patch("tools.advanced_dance.prepare.subprocess.run") as process:
                with self.assertRaisesRegex(ValueError, "Source audio hash"):
                    prepare.prepare_audio("solo", root=root)
                process.assert_not_called()
            self.assertFalse((root / "work").exists())

    def test_prepared_audio_matches_original_speed_and_constant_interior_gain(self):
        import soundfile as sf
        clocks = json.loads((ROOT / "tools/advanced_dance/clock.json").read_text())
        for mode in ("solo", "ensemble"):
            with self.subTest(mode=mode):
                data = json.loads((ROOT / f"projects/advanced-dance-{mode}/project.json").read_text())
                output = ROOT / data["audio"]["source"]
                if not output.exists():
                    self.skipTest("Run prepare audio before this media acceptance check")
                self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(), data["audio"]["source_sha256"])
                samples, rate = sf.read(output, dtype="float64", always_2d=True)
                self.assertEqual((rate, samples.shape), (48000, (1536000, 2)))
                clock = clocks[mode]
                result = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{clock['audio_start_seconds']:.12f}",
                    "-i", str(ROOT / clock["audio_source"]), "-t", "32", "-vn", "-ar", "48000",
                    "-ac", "2", "-f", "f32le", "-"], capture_output=True, check=True, timeout=30)
                original = np.frombuffer(result.stdout, "<f4").reshape(-1, 2)
                self.assertEqual(original.shape, samples.shape)
                # Compare a long interior where neither authored fade acts.
                np.testing.assert_allclose(samples[4800:1488000], original[4800:1488000] * .630957,
                                           rtol=0, atol=2e-6)
                self.assertLess(float(np.max(np.abs(samples[:1]))), 2e-4)
                self.assertLess(float(np.max(np.abs(samples[-48:]))), .002)


class ClothReuseTests(unittest.TestCase):
    def test_real_solver_snapshots_are_reused_exactly_in_shuffled_time_order(self):
        # A bounded 0.1-second fixture exercises the actual cloth serializer and
        # interpolator without starting a full production bake or sharing its
        # cache directory. Identity hashing is checked by production separately.
        from tools.advanced_dance.costume import make_body
        from tools.advanced_dance.score import install
        from tools.advanced_dance import cache

        def fixture():
            body = make_body(at=(0, 0, .14), role=0, points=12000)
            score = install(body)
            score.duration = .1
            return body

        with tempfile.TemporaryDirectory() as directory, \
                patch.object(cache, "ROOT", Path(directory)), \
                patch.object(cache, "motion_key", return_value="bounded-test-fixture"), \
                patch.dict("os.environ", {"ADVANCED_DANCE_CLOTH_CACHE": "auto"}):
            fresh = fixture()
            path = Path(cache.bake_cloth(fresh))
            self.assertTrue(path.is_file())
            cached = fixture()
            self.assertTrue(cache.load_cloth(cached))
            for t in (.1, .025, 0.0, .075, .1):
                np.testing.assert_array_equal(fresh.cloth.positions(t), cached.cloth.positions(t))


if __name__ == "__main__":
    unittest.main()
