"""Registered scene clocks, source identity and resumed output-frame mapping."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image

from pipeline import kit
from pipeline.project import PipelineError, Project, file_hash, validate
from pipeline.render import fingerprint


REPOSITORY = Path(__file__).resolve().parents[2]


class KitRegistryTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((REPOSITORY / "projects/concert-kit-consideration-v2/project.json").read_text())
        self.project = Project(REPOSITORY, REPOSITORY / "project.json", self.data)

    def test_real_registered_modules_have_distinct_explicit_clocks(self):
        old = kit.module_contract(kit.scene_module(REPOSITORY, kit.SCENE), kit.SCENE)
        revised = kit.module_contract(kit.scene_module(REPOSITORY, kit.REVISION_SCENE), kit.REVISION_SCENE)
        self.assertEqual((old["output_frame_count"], old["source_start_frame"], old["cut_frames"]),
                         (1080, 0, [180, 720]))
        self.assertEqual((revised["output_frame_count"], revised["source_start_frame"], revised["cut_frames"]),
                         (900, 180, [234, 540]))
        validate(self.project, check_files=False)
        self.assertEqual(self.project.data["audio"]["offset_seconds"], 3)
        self.assertEqual([shot["end_frame_exclusive"] for shot in self.project.shots], [234, 540, 900])
        self.assertEqual([cue["frame"] for cue in self.data["timing"]["events"]], revised["cut_frames"])

    def test_unregistered_scene_and_mixed_clocks_are_rejected(self):
        self.project.shots[0]["scene"] = "tools/unregistered.py"
        with self.assertRaisesRegex(PipelineError, "not registered"):
            kit.validate_shot(self.project, self.project.shots[0])
        self.project.shots[0]["scene"] = kit.SCENE
        with self.assertRaisesRegex(PipelineError, "separate project.*scene clock"):
            kit.validate_shot(self.project, self.project.shots[0])

    def test_revised_clock_cannot_silently_become_the_old_duration(self):
        self.project.shots[-1]["end_frame_exclusive"] = 1080
        with self.assertRaisesRegex(PipelineError, "15 seconds.*60 fps"):
            kit.validate_shot(self.project, self.project.shots[-1])

    def test_changed_module_offset_or_cuts_require_registration_review(self):
        module = kit.scene_module(REPOSITORY, kit.REVISION_SCENE)
        for field, value in (("SOURCE_START", 0), ("DURATION", 18), ("CUTS", (9.0,)), ("FPS", 30)):
            with self.subTest(field=field), patch.object(module, field, value):
                with self.assertRaisesRegex(PipelineError, "clock or cuts changed"):
                    kit.module_contract(module, kit.REVISION_SCENE)

    def test_actual_revision_api_maps_output_indices_once_at_shot_and_batch_boundaries(self):
        module = kit.scene_module(REPOSITORY, kit.REVISION_SCENE)
        received = []
        with patch.object(module.base, "frame", side_effect=lambda renderer, index, fps: received.append((index, fps))):
            for output in (0, 119, 120, 233, 234, 539, 540, 899):
                module.frame(object(), output, fps=60)
        self.assertEqual(received, [(n + 180, 60) for n in (0, 119, 120, 233, 234, 539, 540, 899)])
        for output in (-1, 900):
            with self.assertRaises(ValueError):
                module.frame(object(), output, fps=60)
        with self.assertRaises(ValueError):
            module.frame(object(), 0, fps=30)

    def test_audio_offset_is_finishing_only_for_this_authored_visual_clock(self):
        self.project.data["style"] = {}
        with patch("pipeline.render.dependency_files", return_value=[]):
            original = fingerprint(self.project, self.project.shots[0], "review", runtime={})[0]
            self.project.data["audio"]["offset_seconds"] = 2.9
            self.assertEqual(original, fingerprint(self.project, self.project.shots[0], "review", runtime={})[0])
            self.project.shots[0]["scene"] = kit.SCENE
            self.assertNotEqual(original, fingerprint(self.project, self.project.shots[0], "review", runtime={})[0])


class KitIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "fonts").mkdir()
        self.sources = {}
        for name in ("assets/p3d/body_v1.npz", "fonts/font.ttf", kit.REVISION_SCENE):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
            self.sources[name] = file_hash(path)
        self.module = SimpleNamespace(FPS=60, DURATION=15, SOURCE_START=3.0, CUTS=(3.9, 9.0),
            COLOR_CONTRACT={"name": "legacy_display_gamma"}, fonts_path=lambda: self.root / "fonts",
            source_hashes=lambda: dict(self.sources))
        self.addCleanup(patch.stopall)
        patch("pipeline.kit.scene_module", return_value=self.module).start()

    def test_renderer_and_response_bytes_enter_only_the_selected_scene_identity(self):
        original = kit.source_identity(self.root, kit.REVISION_SCENE)
        self.assertIn(kit.REVISION_SCENE, original)
        (self.root / kit.REVISION_SCENE).write_bytes(b"changed response renderer")
        with self.assertRaisesRegex(PipelineError, "source identity disagrees"):
            kit.source_identity(self.root, kit.REVISION_SCENE)

    def test_missing_renderer_identity_and_changed_body_are_rejected(self):
        self.sources.pop(kit.REVISION_SCENE)
        with self.assertRaisesRegex(PipelineError, "renderer module must be present"):
            kit.source_identity(self.root, kit.REVISION_SCENE)
        self.sources[kit.REVISION_SCENE] = file_hash(self.root / kit.REVISION_SCENE)
        (self.root / "assets/p3d/body_v1.npz").write_bytes(b"other body")
        with self.assertRaisesRegex(PipelineError, "source identity disagrees"):
            kit.source_identity(self.root, kit.REVISION_SCENE)

    def test_override_is_rejected_before_import_or_source_loader(self):
        with patch.dict(os.environ, {"P3D_BODY_ASSET": "other.npz"}), patch("pipeline.kit.scene_module") as load:
            with self.assertRaisesRegex(PipelineError, "Unset P3D_BODY_ASSET"):
                kit.source_identity(self.root, kit.REVISION_SCENE)
        load.assert_not_called()


class KitWorkerTests(unittest.TestCase):
    def test_worker_keeps_global_index_and_actual_samples_when_resuming_late_shot(self):
        module = kit.scene_module(REPOSITORY, kit.REVISION_SCENE)
        received = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            renderer = SimpleNamespace(w=64, h=36)
            def pixels(renderer, index, fps):
                received.append((index, fps))
                return bytes((index % 256, 60, 80)) * (64 * 36)
            job = {"repo_root": str(root), "video": {"width": 64, "height": 36, "fps": 60},
                   "shot": {"scene": kit.REVISION_SCENE, "start_frame": 540, "end_frame_exclusive": 900, "params": {}},
                   "frames": [721, 899], "temporal_samples": 2, "samples": 128,
                   "stop_file": str(root / "STOP"), "out_dir": str(root / "frames")}
            with patch.dict(os.environ, {"PYTHONHASHSEED": "0"}), patch("pipeline.kit.source_identity") as verify, patch(
                    "pipeline.kit.scene_module", return_value=module), patch.object(module, "make_renderer", return_value=renderer) as make, patch.object(
                    module.base, "frame", side_effect=pixels):
                kit.render_job(job)
            verify.assert_called_once_with(root, kit.REVISION_SCENE)
            make.assert_called_once_with(64, 36, temporal_samples=2, fps=60)
            self.assertEqual(received, [(901, 60), (1079, 60)])
            for output, source in ((721, 901), (899, 1079)):
                path = root / "frames" / f"frame_{output:06d}.png"
                with Image.open(path) as image:
                    self.assertEqual(image.getpixel((0, 0)), (source % 256, 60, 80))
                self.assertFalse(path.with_name(f"frame_{output:06d}.partial.png").exists())

    def test_wrong_worker_scene_or_frame_is_rejected_before_initialization(self):
        job = {"repo_root": "/tmp", "video": {"fps": 60},
               "shot": {"scene": kit.REVISION_SCENE, "start_frame": 540, "end_frame_exclusive": 900, "params": {}},
               "frames": [900], "temporal_samples": 2}
        with patch.dict(os.environ, {"PYTHONHASHSEED": "0"}), patch("pipeline.kit.source_identity") as verify:
            with self.assertRaisesRegex(PipelineError, "outside.*shot clock"):
                kit.render_job(job)
            job["shot"]["scene"] = "tools/unregistered.py"
            with self.assertRaisesRegex(PipelineError, "not registered"):
                kit.render_job(job)
        verify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
