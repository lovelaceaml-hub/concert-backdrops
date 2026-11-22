"""Frozen source identity, preparation provenance, temporal sampling and color."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from pipeline import approved
from pipeline.delivery import get_profile, video_encoding_args
from pipeline.project import PipelineError, Project, file_hash, validate, write_json
from pipeline.render import fingerprint


REPOSITORY = Path(__file__).resolve().parents[2]


class RegisteredContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        target = self.root / approved.REFERENCE_FILE
        target.parent.mkdir(parents=True)
        shutil.copy2(REPOSITORY / approved.REFERENCE_FILE, target)
        data = json.loads((REPOSITORY / "projects/approved-light-s11/project.json").read_text())
        self.project = Project(self.root, self.root / "project.json", data)

    def test_temporal_samples_are_distinct_from_blender_samples(self):
        validate(self.project, check_files=False)
        self.project.data["quality"]["review"]["samples"] = 64
        with self.assertRaisesRegex(PipelineError, "temporal_samples.*Blender samples"):
            validate(self.project, check_files=False)

    def test_temporal_budget_cannot_be_boolean_or_arbitrary_cycles_count(self):
        for count in (True, 0, 64):
            with self.subTest(count=count):
                data = copy.deepcopy(self.project.data)
                data["quality"]["review"]["temporal_samples"] = count
                with self.assertRaises(PipelineError):
                    validate(Project(self.root, self.project.manifest, data), check_files=False)

    def test_wrong_recording_or_source_module_cannot_use_approved_label(self):
        self.project.data["audio"]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(PipelineError, "original audio SHA256"):
            validate(self.project, check_files=False)
        self.project.data["audio"]["source_sha256"] = approved.reference(self.root)["audio_sha256"]
        self.project.shots[0]["scene"] = "tools/another.py"
        with self.assertRaisesRegex(PipelineError, "registered"):
            validate(self.project, check_files=False)

    def test_wrong_display_transform_and_clock_are_rejected(self):
        self.project.data["delivery"]["source_transfer"] = "srgb"
        with self.assertRaisesRegex(PipelineError, "legacy_display_gamma"):
            validate(self.project, check_files=False)
        self.project.data["delivery"]["source_transfer"] = "legacy_display_gamma"
        self.project.data["video"]["fps"] = 30
        with self.assertRaisesRegex(PipelineError, "60 fps"):
            validate(self.project, check_files=False)

    def test_modified_required_asset_is_rejected_even_if_it_is_present(self):
        asset = self.root / "assets/body.npz"
        asset.parent.mkdir()
        asset.write_bytes(b"registered body")
        write_json(self.root / approved.REFERENCE_FILE, {"source_files": {"assets/body.npz": file_hash(asset)}})
        approved.verify_reference_files(self.root)
        asset.write_bytes(b"other body")
        with self.assertRaisesRegex(PipelineError, "Registered source changed"):
            approved.verify_reference_files(self.root)
        asset.unlink()
        with self.assertRaisesRegex(PipelineError, "source is missing"):
            approved.verify_reference_files(self.root)

    def test_audio_headroom_changes_reuse_pixels_but_offset_changes_do_not(self):
        self.project.data["style"] = {}
        shot = self.project.shots[0]
        with patch("pipeline.render.dependency_files", return_value=[]):
            before = fingerprint(self.project, shot, "review", runtime={})[0]
            self.project.data["audio"]["gain_db"] = -1
            self.assertEqual(before, fingerprint(self.project, shot, "review", runtime={})[0])
            self.project.data["audio"]["offset_seconds"] += 1 / 60
            self.assertNotEqual(before, fingerprint(self.project, shot, "review", runtime={})[0])


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "audio.mp3"
        source.write_bytes(b"verified private audio fixture")
        definition = {"source_files": {}, "audio_sha256": file_hash(source), "source_commit": "source",
                      "source_account_commit": "account", "engine_commit": "engine", "people_commit": "people"}
        write_json(self.root / approved.REFERENCE_FILE, definition)
        base = self.root / "work/s11_full2"
        base.mkdir(parents=True)
        (base / "score.wav").write_bytes(b"prepared score fixture")
        np.savez(base / "features.npz", times=[0, 275])
        np.savez(base / "music_fx.npz", times=[0, 275])
        write_json(self.root / approved.PREPARATION, {"original_audio_sha256": definition["audio_sha256"],
                   "source_account_commit": "account", "analysis": {name: file_hash(base / name) for name in approved.DERIVED}})
        write_json(base / "provenance.json", {"audio_sha256": definition["audio_sha256"], "engine_commit": "engine", "claude_reference_commit": "people"})
        self.project = Project(self.root, self.root / "project.json", {"project_id": "prepared", "audio": {"source": "audio.mp3", "offset_seconds": 97.8},
                              "video": {"fps": 60}, "shots": [{"end_frame_exclusive": 1800}]})
        self.addCleanup(patch.stopall)
        patch("pipeline.approved.reference_module", return_value=SimpleNamespace(validate_analysis=lambda: None)).start()

    def test_matching_analysis_receipt_is_accepted_with_exact_provenance(self):
        result = approved.prepared_identity(self.project)
        self.assertEqual(result["picture_delay_seconds"], .1)
        self.assertEqual(result["source_commit"], "source")
        self.assertEqual(set(result["derived_sha256"]), set(approved.DERIVED))

    def test_modified_map_is_not_adopted_as_a_good_preparation(self):
        (self.root / "work/s11_full2/features.npz").write_bytes(b"wrong cache")
        with self.assertRaisesRegex(PipelineError, "features.npz is missing or changed"):
            approved.prepared_identity(self.project)

    def test_wrong_source_audio_is_rejected_before_analysis_loading(self):
        (self.root / "audio.mp3").write_bytes(b"different recording")
        with self.assertRaisesRegex(PipelineError, "recording bytes"):
            approved.prepared_identity(self.project)

    def test_missing_map_is_not_silently_replaced_by_silence(self):
        (self.root / "work/s11_full2/music_fx.npz").unlink()
        with self.assertRaisesRegex(PipelineError, "music_fx.npz is missing or changed"):
            approved.prepared_identity(self.project)


class AdapterClockTests(unittest.TestCase):
    def test_native_global_clock_and_temporal_samples_reach_reference_api(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = []
            renderer = SimpleNamespace(w=64, h=36)
            def make(width, height, **kwargs):
                calls.append((width, height, kwargs))
                return renderer
            def pixels(renderer, index, source_start):
                calls.append((index, source_start))
                return bytes([40, 60, 80]) * (64 * 36)
            module = SimpleNamespace(make_renderer=make, frame=pixels)
            job = {"repo_root": str(root), "video": {"width": 64, "height": 36, "fps": 60},
                   "shot": {"scene": approved.SCENE, "start_frame": 720, "params": {}},
                   "frames": [721], "temporal_samples": 2, "samples": 128, "audio": {"offset_seconds": 97.8},
                   "stop_file": str(root / "STOP"), "out_dir": str(root / "frames")}
            with patch.dict(os.environ, {"PYTHONHASHSEED": "0"}), patch("pipeline.approved.verify_reference_files"), patch(
                    "pipeline.approved.reference_module", return_value=module):
                approved.render_job(job)
            self.assertEqual(calls, [(64, 36, {"samples": 2, "keep_grain": False}), (721, 97.8)])
            self.assertTrue((root / "frames/frame_000721.png").is_file())
            self.assertFalse((root / "frames/frame_000721.partial.png").exists())


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is required for the real tiny color encode")
class LegacyColorTests(unittest.TestCase):
    def test_matrix_only_encode_preserves_reference_midgray(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "gray.mp4"
            command = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "32x18", "-r", "60", "-i", "-",
                       *video_encoding_args(60, get_profile("h264"), source_transfer="legacy_display_gamma"), "-an", str(output)]
            subprocess.run(command, input=bytes([128, 128, 128]) * (32 * 18 * 4), check=True, capture_output=True, timeout=30)
            raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(output), "-frames:v", "1", "-vf",
                                           "scale=in_color_matrix=bt709:in_range=tv:out_range=pc", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], timeout=30)
            self.assertLess(abs(float(np.frombuffer(raw, np.uint8).mean()) - 128), 2)
            self.assertIn("zscale", video_encoding_args(60, get_profile("h264"))[1])
            with self.assertRaisesRegex(PipelineError, "H.264"):
                video_encoding_args(60, get_profile("hevc10"), source_transfer="legacy_display_gamma")


if __name__ == "__main__":
    unittest.main()
