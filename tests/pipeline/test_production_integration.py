"""Production repairs: selected backends, current evidence and repeatable workers."""
from __future__ import annotations

import contextlib
import importlib.metadata
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from pipeline.cli import doctor
from pipeline.environment import worker_environment
from pipeline.media import storyboard
from pipeline.production import plan, produce
from pipeline.project import PipelineError, file_hash, write_json
from pipeline.render import render, shot_directory
from test_contract import project_fixture


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "fonts").mkdir()
        for name in ("cormorant-garamond-latin-700-italic.ttf", "cormorant-garamond-latin-700-normal.ttf",
                     "jost-latin-500-normal.ttf", "cormorant-garamond-latin-600-italic.ttf"):
            (self.root / "fonts" / name).write_bytes(b"font presence fixture")
        self.addCleanup(patch.stopall)
        patch("pipeline.cli.shutil.which", return_value="/present/tool").start()
        patch("pipeline.cli.command_version", return_value="present").start()
        patch("pipeline.cli.importlib.metadata.version", return_value="test").start()
        patch("pipeline.delivery.encoder_capabilities", return_value={"encoders": ["libx264"], "zscale": False}).start()

    def test_approved_cpu_backend_does_not_require_browser_blender_or_node(self):
        with patch("pipeline.cli.browser_probe") as browser, patch("pipeline.cli.blender_binary") as blender:
            result = doctor(self.root, renderers=["p3d-approved"], probe_browser=True)
        self.assertTrue(result["dependencies_ready"], result["errors"])
        self.assertEqual(result["runtime_validation"]["browser"]["status"], "not_required")
        self.assertNotIn("node", result["binaries"])
        browser.assert_not_called()
        blender.assert_not_called()
        self.assertFalse(result["full_pipeline_runtime_verified"])

    def test_selected_missing_blender_fails_its_backend_only(self):
        with patch("pipeline.cli.blender_binary", return_value="/absent/blender"), patch(
                "pipeline.cli.command_version", side_effect=lambda command: "unavailable" if command[0] == "/absent/blender" else "present"):
            result = doctor(self.root, renderers=["blender"])
        self.assertFalse(result["dependencies_ready"])
        self.assertIn("Missing blender.", result["errors"])

    def test_selected_missing_python_backend_dependency_is_an_error(self):
        def version(name):
            if name == "moderngl":
                raise importlib.metadata.PackageNotFoundError(name)
            return "test"
        with patch("pipeline.cli.importlib.metadata.version", side_effect=version):
            result = doctor(self.root, renderers=["p3d-approved"])
        self.assertTrue(any("moderngl" in error for error in result["errors"]))


class WorkerEnvironmentTests(unittest.TestCase):
    def test_fresh_python_workers_have_the_same_hash_seed(self):
        values = []
        for inherited in ("123", "999"):
            with patch.dict(os.environ, {"PYTHONHASHSEED": inherited}):
                env = worker_environment("p3d-approved", 4)
            output = subprocess.check_output([sys.executable, "-c", "print(hash('approved-word-scatter'))"], env=env, text=True)
            values.append(output.strip())
            self.assertEqual(env["PYTHONHASHSEED"], "0")
            self.assertEqual(env["LP_NUM_THREADS"], "1")
        self.assertEqual(values[0], values[1])


class GalleryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = project_fixture(self.root)
        self.addCleanup(patch.stopall)
        patch("pipeline.render.runtime_identity", return_value={"test": "1"}).start()
        def worker(command, **kwargs):
            self.assertEqual(kwargs["env"]["PYTHONHASHSEED"], "0")
            job = json.loads(Path(command[command.index("--job") + 1]).read_text())
            for frame in job["frames"]:
                Image.new("RGB", (32, 18), (frame, 50, 100)).save(Path(job["out_dir"]) / f"frame_{frame:06d}.png")
        patch("pipeline.render.run", side_effect=worker).start()
        with contextlib.redirect_stdout(io.StringIO()):
            render(self.project, "draft")

    def test_current_frame_is_visible_but_changed_scene_hides_its_old_pixels(self):
        self.assertIn('src="shots/a/frames/frame_000000.png"', storyboard(self.project, "draft").read_text())
        (self.root / "scenes/a.tsx").write_text("changed scene")
        page = storyboard(self.project, "draft").read_text()
        self.assertNotIn('src="shots/a/frames/frame_000000.png"', page)
        self.assertIn("Stale; render this frame", page)
        self.assertIn('src="shots/b/frames/frame_000002.png"', page)

    def test_changed_image_with_valid_dimensions_is_not_shown(self):
        directory = shot_directory(self.project, "draft", self.project.shots[0])
        Image.new("RGB", (32, 18), "red").save(directory / "frames/frame_000000.png")
        page = storyboard(self.project, "draft").read_text()
        self.assertNotIn('src="shots/a/frames/frame_000000.png"', page)
        self.assertIn("Changed or unverified", page)

    def test_unreceipted_pixels_are_not_shown(self):
        (shot_directory(self.project, "draft", self.project.shots[0]) / "receipt.json").unlink()
        page = storyboard(self.project, "draft").read_text()
        self.assertNotIn('src="shots/a/frames/frame_000000.png"', page)
        self.assertIn("Unverified; render this frame", page)

    def test_stale_master_is_not_embedded(self):
        directory = self.project.output("draft")
        master = directory / "master.mp4"
        master.write_bytes(b"old master")
        write_json(directory / "master.json", {"filename": "master.mp4", "sha256": file_hash(master), "project_identity": "old"})
        page = storyboard(self.project, "draft").read_text()
        self.assertNotIn("<video controls", page)
        self.assertIn("master is stale or unverified", page)

    def test_selected_frame_appears_even_when_it_is_not_a_default_storyboard_time(self):
        self.project.shots[0]["end_frame_exclusive"] = 60
        self.project.shots[1].update(start_frame=60, end_frame_exclusive=120)
        with contextlib.redirect_stdout(io.StringIO()):
            render(self.project, "draft", selected=[17])
        page = storyboard(self.project, "draft").read_text()
        self.assertIn('src="shots/a/frames/frame_000017.png"', page)

    def test_malformed_receipt_does_not_display_unverified_frames(self):
        receipt = shot_directory(self.project, "draft", self.project.shots[0]) / "receipt.json"
        receipt.write_text("[]")
        page = storyboard(self.project, "draft").read_text()
        self.assertNotIn('src="shots/a/frames/frame_000000.png"', page)


class ProduceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = project_fixture(self.root)

    def test_plan_does_not_prepare_render_or_write_outputs(self):
        result = plan(self.project, "draft", selected=[0])
        self.assertTrue(result["plan_only"])
        self.assertEqual(result["stages"], ["prepare", "render", "gallery"])
        self.assertFalse((self.root / "work").exists())

    def test_produce_composes_existing_stages_and_does_not_record_approval(self):
        calls = []
        def stage(name, result):
            return lambda *args, **kwargs: (calls.append(name), result)[1]
        with patch("pipeline.production.prepare", side_effect=stage("prepare", {})), \
                patch("pipeline.production.render", side_effect=stage("render", [])), \
                patch("pipeline.production.assemble", side_effect=stage("assemble", self.root / "master.mp4")), \
                patch("pipeline.production.qa", side_effect=stage("qa", {"technical_passed": True})), \
                patch("pipeline.production.storyboard", side_effect=stage("gallery", self.root / "review.html")):
            result = produce(self.project, "draft")
        self.assertEqual(calls, ["prepare", "render", "assemble", "qa", "gallery"])
        self.assertTrue(result["complete"])
        self.assertFalse((self.project.output("draft") / "approval.json").exists())

    def test_stop_marker_prevents_preparation_and_new_work(self):
        self.project.output("draft").mkdir(parents=True)
        (self.project.output("draft") / "STOP").touch()
        with patch("pipeline.production.prepare") as prepare:
            with self.assertRaisesRegex(PipelineError, "STOP"):
                produce(self.project, "draft")
        prepare.assert_not_called()


if __name__ == "__main__":
    unittest.main()
