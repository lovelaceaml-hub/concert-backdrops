"""The dance project must retain its authored clock and declared source identity."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from pipeline import kit
from pipeline.project import PipelineError, Project, file_hash, validate


REPOSITORY = Path(__file__).resolve().parents[1]
MANIFEST = REPOSITORY / "projects/concert-dance-study/project.json"
DANCE_RENDERER = "tools/concert_dance/render.py"


class DanceRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(MANIFEST.read_text())
        self.project = Project(REPOSITORY, MANIFEST, self.data)

    def test_actual_module_matches_one_uninterrupted_1080_frame_clock(self):
        module = kit.scene_module(REPOSITORY, kit.DANCE_SCENE)
        contract = kit.module_contract(module, kit.DANCE_SCENE)
        validate(self.project, check_files=False)
        self.assertEqual(contract["id"], "natural-dance-v1")
        self.assertEqual(contract["module"], DANCE_RENDERER)
        self.assertEqual((contract["output_frame_count"], contract["source_start_frame"], contract["cut_frames"]),
                         (1080, 0, []))
        self.assertEqual(len(self.project.shots), 1)
        self.assertEqual((self.project.shots[0]["start_frame"], self.project.frames, self.project.fps),
                         (0, 1080, 60))
        self.assertEqual(self.data["timing"]["events"], [])
        self.assertFalse(self.data["timing"]["manually_verified"])
        for name, size, samples in (("draft", (960, 540), 1), ("review", (1920, 1080), 2),
                                    ("4k-check", (3840, 2160), 2), ("final", (1920, 1080), 2)):
            preset = self.project.settings(name)
            self.assertEqual((preset["width"], preset["height"]), size)
            self.assertEqual((preset["fps"], preset["temporal_samples"], preset["image_bit_depth"]),
                             (60, samples, 8))

    def test_existing_score_is_reused_at_its_original_offset_and_speed(self):
        original = json.loads((REPOSITORY / "projects/concert-kit-consideration/project.json").read_text())
        self.assertEqual(self.data["audio"], original["audio"])
        self.assertEqual(self.data["audio"]["offset_seconds"], 0)
        self.assertEqual(self.data["audio"]["source_sha256"],
                         "0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b")
        self.assertEqual(kit.scene_spec(kit.SCENE)["cut_frames"], (180, 720))
        self.assertEqual((kit.scene_spec(kit.REVISION_SCENE)["seconds"],
                          kit.scene_spec(kit.REVISION_SCENE)["source_start_frame"]), (15, 180))

    def test_changed_action_params_clock_and_unknown_scene_are_rejected(self):
        changes = (
            ("params", lambda d: d["shots"][0].update(params={"speed": 0.5}), "empty params"),
            ("fps", lambda d: d["video"].update(fps=30), "18 seconds.*60 fps"),
            ("duration", lambda d: d["shots"][0].update(end_frame_exclusive=1081), "18 seconds.*60 fps"),
            ("scene", lambda d: d["shots"][0].update(scene="tools/concert_dance/other.py"), "not registered"),
        )
        for label, change, message in changes:
            data = copy.deepcopy(self.data)
            change(data)
            with self.subTest(change=label), self.assertRaisesRegex(PipelineError, message):
                validate(Project(REPOSITORY, MANIFEST, data), check_files=False)

    def test_module_clock_drift_and_color_changes_require_explicit_review(self):
        for name, value in (("DURATION", 19.0), ("FPS", 30), ("SOURCE_START", 1.0), ("CUTS", (9.0,))):
            module = SimpleNamespace(DURATION=18.0, FPS=60, SOURCE_START=0, CUTS=(),
                                     COLOR_CONTRACT={"name": "legacy_display_gamma"})
            setattr(module, name, value)
            with self.subTest(field=name), self.assertRaisesRegex(PipelineError, "clock or cuts changed"):
                kit.module_contract(module, kit.DANCE_SCENE)
        module = SimpleNamespace(DURATION=18.0, FPS=60, SOURCE_START=0, CUTS=(),
                                 COLOR_CONTRACT={"name": "srgb"})
        with self.assertRaisesRegex(PipelineError, "color convention changed"):
            kit.module_contract(module, kit.DANCE_SCENE)


class DanceSourceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "fonts").mkdir()
        self.sources = {}
        for name in ("assets/p3d/body_v1.npz", "fonts/font.ttf", DANCE_RENDERER, kit.DANCE_SCENE):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
            self.sources[name] = file_hash(path)
        module = SimpleNamespace(DURATION=18.0, FPS=60, SOURCE_START=0, CUTS=(),
                                 COLOR_CONTRACT={"name": "legacy_display_gamma"},
                                 fonts_path=lambda: self.root / "fonts",
                                 source_hashes=lambda: dict(self.sources))
        loader = patch("pipeline.kit.scene_module", return_value=module)
        loader.start()
        self.addCleanup(loader.stop)
        environment = patch.dict(os.environ, {}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)

    def test_modified_declared_scene_or_renderer_bytes_are_not_reused(self):
        identity = kit.source_identity(self.root, kit.DANCE_SCENE)
        self.assertIn(kit.DANCE_SCENE, identity)
        self.assertIn(DANCE_RENDERER, identity)
        for name in (kit.DANCE_SCENE, DANCE_RENDERER):
            path = self.root / name
            old = path.read_bytes()
            path.write_bytes(b"changed performance source")
            with self.subTest(source=name), self.assertRaisesRegex(PipelineError, "source identity disagrees"):
                kit.source_identity(self.root, kit.DANCE_SCENE)
            path.write_bytes(old)

    def test_body_and_renderer_must_be_present_in_source_manifest(self):
        for name, message in (("assets/p3d/body_v1.npz", "body asset must be present"),
                              (DANCE_RENDERER, "renderer module must be present")):
            old = self.sources.pop(name)
            with self.subTest(source=name), self.assertRaisesRegex(PipelineError, message):
                kit.source_identity(self.root, kit.DANCE_SCENE)
            self.sources[name] = old

    def test_body_override_is_rejected_before_the_module_loader(self):
        with patch.dict(os.environ, {"P3D_BODY_ASSET": "another.npz"}), patch("pipeline.kit.scene_module") as loader:
            with self.assertRaisesRegex(PipelineError, "Unset P3D_BODY_ASSET"):
                kit.source_identity(self.root, kit.DANCE_SCENE)
        loader.assert_not_called()


if __name__ == "__main__":
    unittest.main()
