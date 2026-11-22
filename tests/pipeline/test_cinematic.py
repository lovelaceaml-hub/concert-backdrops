"""Exercise recovery and native precision, where failed renders cost real time."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from pipeline.presets import cinematic_project
from pipeline.project import PipelineError, Project, file_hash, validate, write_json
from pipeline.cli import archive, create_project
from pipeline.media import finishing_input_hashes
from pipeline.render import render, shot_directory, valid_frame, verify_complete
from test_contract import project_fixture


class CinematicTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = project_fixture(self.root)

    def test_default_project_is_native_4k_with_one_60fps_clock(self):
        data = cinematic_project("native-study", "Native study")
        project = Project(self.root, self.root / "project.json", data)
        validate(project, check_files=False)
        self.assertEqual(project.frames, 600)
        self.assertEqual(project.settings("final")["width"], 3840)
        self.assertEqual(project.settings("final")["height"], 2160)
        self.assertEqual(project.settings("final")["image_bit_depth"], 16)
        self.assertEqual({project.settings(q)["fps"] for q in data["quality"]}, {60})
        self.assertIsNone(data["production"]["cloud_gpu_provider"])
        self.assertEqual(data["production"]["render_chunk_frames"], 1)
        self.assertEqual(data["production"]["render_timeout_seconds"], 7200)

    def test_valid_rgb8_file_cannot_pass_as_rgb16(self):
        frame = self.root / "eight.png"
        Image.new("RGB", (32, 18), "gold").save(frame)
        self.assertTrue(valid_frame(frame, (32, 18), bit_depth=8))
        self.assertFalse(valid_frame(frame, (32, 18), bit_depth=16))

    def test_failed_chunk_keeps_only_verified_finished_frames_then_resumes(self):
        calls = []
        fail_once = [True]

        def worker(command, **kwargs):
            job = json.loads(Path(command[command.index("--job") + 1]).read_text())
            calls.append(job["frames"])
            for frame in job["frames"]:
                Image.new("RGB", (32, 18), (frame, 100, 150)).save(Path(job["out_dir"]) / f"frame_{frame:06d}.png")
                if fail_once[0]:
                    fail_once[0] = False
                    raise PipelineError("simulated worker interruption")

        with patch("pipeline.render.runtime_identity", return_value={"test": 1}), patch("pipeline.render.run", side_effect=worker):
            with self.assertRaisesRegex(PipelineError, "interruption"):
                render(self.project, "draft")
            receipt = json.loads((shot_directory(self.project, "draft", self.project.shots[0]) / "receipt.json").read_text())
            self.assertEqual(set(receipt["frames"]), {"0"})
            self.assertFalse(receipt["complete"])
            render(self.project, "draft")
            verify_complete(self.project, "draft")
        self.assertEqual(calls, [[0, 1], [1], [2, 3]])

    def test_chunk_limit_is_applied_without_changing_frame_clock(self):
        self.project.data["production"]["render_chunk_frames"] = 1
        calls = []

        def worker(command, **kwargs):
            job = json.loads(Path(command[command.index("--job") + 1]).read_text())
            calls.append((job["frames"], job["video"]["fps"], kwargs["timeout"]))
            for frame in job["frames"]:
                Image.new("RGB", (32, 18)).save(Path(job["out_dir"]) / f"frame_{frame:06d}.png")

        with patch("pipeline.render.runtime_identity", return_value={}), patch("pipeline.render.run", side_effect=worker):
            render(self.project, "draft")
        self.assertEqual([c[0] for c in calls], [[0], [1], [2], [3]])
        self.assertEqual({c[1:] for c in calls}, {(30, 1800)})

    def test_source_change_during_worker_cannot_receive_valid_receipt(self):
        def worker(command, **kwargs):
            job = json.loads(Path(command[command.index("--job") + 1]).read_text())
            for frame in job["frames"]:
                Image.new("RGB", (32, 18)).save(Path(job["out_dir"]) / f"frame_{frame:06d}.png")
            (self.root / "scenes/a.tsx").write_text("changed while the worker was running")

        with patch("pipeline.render.runtime_identity", return_value={}), patch("pipeline.render.run", side_effect=worker):
            with self.assertRaisesRegex(PipelineError, "Source changed"):
                render(self.project, "draft", selected=[0])
        self.assertFalse((shot_directory(self.project, "draft", self.project.shots[0]) / "receipt.json").exists())

    def test_archive_rechecks_finishing_sources_after_prior_qa_pass(self):
        source = self.root / "apps/editor/delivery.mjs"
        source.parent.mkdir(parents=True)
        source.write_text("original delivery")
        directory = self.project.output("draft")
        directory.mkdir(parents=True)
        master = directory / "master.mp4"
        master.write_bytes(b"verified prior bytes")
        write_json(directory / "qa.json", {"technical_passed": True, "master_sha256": file_hash(master)})
        write_json(directory / "master.json", {"project_identity": self.project.identity(), "editor": "remotion", "finishing_inputs": finishing_input_hashes(self.root, "remotion")})
        source.write_text("new delivery recipe")
        with self.assertRaisesRegex(PipelineError, "Finishing code changed"):
            archive(self.project, "draft", str(self.root / "archive"))
        self.assertFalse((self.root / "archive").exists())

    def test_creation_rejects_browser_clock_before_writing_files(self):
        with self.assertRaisesRegex(PipelineError, "120 fps"):
            create_project(self.root, "Too fast", 240, 2, "browser")
        self.assertFalse((self.root / "projects/too-fast").exists())

    def test_event_kind_and_browser_bounds_fail_before_render(self):
        self.project.data["timing"]["events"] = [{"frame": 0}]
        with self.assertRaisesRegex(PipelineError, "kind"):
            validate(self.project)
        self.project.data["timing"]["events"] = []
        self.project.data["video"].update(width=8, height=8)
        for preset in self.project.data["quality"].values():
            preset.update(width=8, height=8)
        with self.assertRaisesRegex(PipelineError, "Browser render presets"):
            validate(self.project)

    def test_one_frame_project_cues_remain_inside_timeline(self):
        data = cinematic_project("tiny", "Tiny", 1, 1)
        validate(Project(self.root, self.root / "tiny.json", data), check_files=False)
        self.assertTrue(all(event["frame"] == 0 for event in data["timing"]["events"]))


if __name__ == "__main__":
    unittest.main()
