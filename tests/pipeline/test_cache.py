"""A stale, incomplete, changed, or missing frame cannot be delivered as current."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from pipeline.project import PipelineError
from pipeline.render import fingerprint, render, shot_directory, verify_complete
from test_contract import project_fixture


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.project = project_fixture(self.root)
        self.jobs = []
        self.commands = []

        def fake_run(command, **kwargs):
            self.commands.append(command)
            job = json.loads(Path(command[command.index("--job") + 1]).read_text())
            self.jobs.append(job)
            for frame in job["frames"]:
                output = Path(job["out_dir"]) / f"frame_{frame:06d}.png"
                Image.new("RGB", (job["video"]["width"], job["video"]["height"]), (30 + frame, 50, 80)).save(output)

        self.addCleanup(patch.stopall)
        patch("pipeline.render.runtime_identity", return_value={"test_runtime": "1"}).start()
        patch("pipeline.render.run", side_effect=fake_run).start()
        patch("pipeline.render.platform.system", return_value="Linux").start()
        self.stdout = contextlib.redirect_stdout(io.StringIO())
        self.stdout.__enter__()
        self.addCleanup(self.stdout.__exit__, None, None, None)

    def test_completed_frames_reuse_without_rendering(self):
        render(self.project, "draft")
        self.assertEqual(len(self.jobs), 2)
        render(self.project, "draft")
        self.assertEqual(len(self.jobs), 2)
        self.assertEqual(len(verify_complete(self.project, "draft")), 2)

    def test_missing_frame_is_repaired_without_rerendering_other_frames(self):
        render(self.project, "draft")
        directory = shot_directory(self.project, "draft", self.project.shots[0])
        (directory / "frames/frame_000001.png").unlink()
        with self.assertRaisesRegex(PipelineError, "missing or changed"):
            verify_complete(self.project, "draft")
        render(self.project, "draft")
        self.assertEqual(len(self.jobs), 3)
        self.assertEqual(self.jobs[-1]["frames"], [1])
        verify_complete(self.project, "draft")

    def test_changed_valid_png_is_repaired_using_checksum(self):
        render(self.project, "draft")
        directory = shot_directory(self.project, "draft", self.project.shots[1])
        Image.new("RGB", (32, 18), "red").save(directory / "frames/frame_000003.png")
        render(self.project, "draft")
        self.assertEqual(len(self.jobs), 3)
        self.assertEqual(self.jobs[-1]["frames"], [3])

    def test_partial_sequence_is_not_a_complete_render(self):
        render(self.project, "draft", selected=[0])
        self.assertFalse(json.loads((shot_directory(self.project, "draft", self.project.shots[0]) / "receipt.json").read_text())["complete"])
        with self.assertRaisesRegex(PipelineError, "missing or changed"):
            verify_complete(self.project, "draft")

    def test_source_edit_invalidates_its_shot(self):
        render(self.project, "draft")
        (self.root / "scenes/a.tsx").write_text("export const a = 2;\n")
        with self.assertRaisesRegex(PipelineError, "stale"):
            verify_complete(self.project, "draft")
        render(self.project, "draft")
        self.assertEqual(len(self.jobs), 3)
        self.assertEqual(self.jobs[-1]["frames"], [0, 1])

    def test_timing_style_and_seed_change_invalidate_visuals(self):
        shot = self.project.shots[0]
        first = fingerprint(self.project, shot, "draft")[0]
        self.project.data["style"]["palette"]["gold"] = "#ffffff"
        second = fingerprint(self.project, shot, "draft")[0]
        self.assertNotEqual(first, second)
        self.project.data["timing"]["events"][0]["frame"] = 1
        third = fingerprint(self.project, shot, "draft")[0]
        self.assertNotEqual(second, third)
        self.project.data["production"]["random_seed"] += 1
        self.assertNotEqual(third, fingerprint(self.project, shot, "draft")[0])

    def test_external_model_dependency_is_content_hashed(self):
        asset = self.root / "model.glb"
        asset.write_bytes(b"original-model")
        shot = self.project.shots[0]
        shot["dependencies"] = ["model.glb"]
        before = fingerprint(self.project, shot, "draft")[0]
        asset.write_bytes(b"changed-model")
        self.assertNotEqual(before, fingerprint(self.project, shot, "draft")[0])

    def test_neighbor_shot_only_param_change_preserves_unchanged_shot(self):
        first = fingerprint(self.project, self.project.shots[0], "draft")[0]
        self.project.shots[1]["params"] = {"bloom": 0.5}
        self.assertEqual(first, fingerprint(self.project, self.project.shots[0], "draft")[0])

    def test_wrong_resolution_frame_never_enters_receipt(self):
        def broken_run(command, **kwargs):
            job = json.loads(Path(command[-1]).read_text())
            for frame in job["frames"]:
                Image.new("RGB", (10, 10)).save(Path(job["out_dir"]) / f"frame_{frame:06d}.png")
        with patch("pipeline.render.run", side_effect=broken_run):
            with self.assertRaisesRegex(PipelineError, "valid frames"):
                render(self.project, "draft", selected=[0])
        receipt = shot_directory(self.project, "draft", self.project.shots[0]) / "receipt.json"
        self.assertFalse(receipt.exists())

    def test_blender_python_errors_are_process_failures(self):
        self.project.shots[0]["renderer"] = "blender"
        render(self.project, "draft", selected=[0])
        command = self.commands[0]
        self.assertEqual(command[command.index("--python-exit-code") + 1], "1")
        self.assertLess(command.index("--python-exit-code"), command.index("--python"))

    def test_explicit_local_opt_in_reaches_browser_command(self):
        render(self.project, "draft", selected=[0], allow_local=True)
        self.assertIn("--allow-local-render", self.commands[0])


if __name__ == "__main__":
    unittest.main()
