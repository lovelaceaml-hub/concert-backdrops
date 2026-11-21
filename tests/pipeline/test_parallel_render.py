"""Bounded subprocess dispatch keeps frame ownership and receipts single-writer."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from pipeline.project import PipelineError, validate, write_json
from pipeline.production import plan
from pipeline.render import fingerprint, render, shot_directory, verify_complete
from test_contract import project_fixture


class ParallelRenderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = project_fixture(self.root)
        self.project.data["shots"] = [self.project.shots[0]]
        self.project.shots[0]["end_frame_exclusive"] = 8
        self.project.data["production"].update(render_workers=2, render_chunk_frames=2)
        self.directory = shot_directory(self.project, "draft", self.project.shots[0])
        self.jobs = []
        self.logs = []
        self.record_lock = threading.Lock()
        self.main_thread = threading.get_ident()
        self.receipt_threads = []
        self.addCleanup(patch.stopall)
        patch("pipeline.render.runtime_identity", return_value={"test_runtime": "1"}).start()
        patch("pipeline.render.platform.system", return_value="Linux").start()
        stdout = contextlib.redirect_stdout(io.StringIO())
        stdout.__enter__()
        self.addCleanup(stdout.__exit__, None, None, None)

    def read_job(self, command, kwargs):
        path = Path(command[command.index("--job") + 1])
        job = json.loads(path.read_text())
        with self.record_lock:
            self.jobs.append((path, job))
            self.logs.append(kwargs["log"])
        return job

    def frame(self, job, number):
        Image.new("RGB", (32, 18), (number, 50, 80)).save(
            Path(job["out_dir"]) / f"frame_{number:06d}.png")

    def successful_worker(self, command, **kwargs):
        job = self.read_job(command, kwargs)
        for number in job["frames"]:
            self.frame(job, number)

    def receipt(self):
        return json.loads((self.directory / "receipt.json").read_text())

    def test_bounded_overlap_disjoint_outputs_and_single_receipt_writer(self):
        barrier = threading.Barrier(2, timeout=5)
        active = 0
        peak = 0

        def worker(command, **kwargs):
            nonlocal active, peak
            job = self.read_job(command, kwargs)
            with self.record_lock:
                active += 1
                peak = max(peak, active)
            barrier.wait()
            for number in job["frames"]:
                self.frame(job, number)
            with self.record_lock:
                active -= 1

        def recording_write(path, data):
            if path.name == "receipt.json":
                self.receipt_threads.append(threading.get_ident())
            write_json(path, data)

        with patch("pipeline.render.run", side_effect=worker), patch("pipeline.render.write_json", side_effect=recording_write):
            render(self.project, "draft", selected=[7, 0, 1, 1, 2, 3, 4, 5, 6])
        self.assertEqual(peak, 2)
        self.assertEqual(len({path for path, _ in self.jobs}), 4)
        self.assertEqual(len(set(self.logs)), 4)
        self.assertEqual(len({job["out_dir"] for _, job in self.jobs}), 4)
        self.assertEqual(len({job["features_dir"] for _, job in self.jobs}), 4)
        self.assertEqual(sorted(n for _, job in self.jobs for n in job["frames"]), list(range(8)))
        self.assertEqual(set(self.receipt_threads), {self.main_thread})
        self.assertTrue(self.receipt()["complete"])
        self.assertTrue(all(not list(Path(job["out_dir"]).glob("*.png")) for _, job in self.jobs))
        verify_complete(self.project, "draft")

    def test_failure_preserves_partial_and_inflight_frames_then_resumes_missing(self):
        barrier = threading.Barrier(2, timeout=5)
        checkpointed_failure = threading.Event()

        def recording_write(path, data):
            write_json(path, data)
            if path.name == "receipt.json" and "0" in data["frames"]:
                checkpointed_failure.set()

        def worker(command, **kwargs):
            job = self.read_job(command, kwargs)
            barrier.wait()
            if job["frames"][0] == 0:
                self.frame(job, 0)
                raise PipelineError("intentional worker failure")
            self.assertTrue(checkpointed_failure.wait(5))
            for number in job["frames"]:
                self.frame(job, number)

        with patch("pipeline.render.run", side_effect=worker), patch("pipeline.render.write_json", side_effect=recording_write):
            with self.assertRaisesRegex(PipelineError, "intentional worker failure"):
                render(self.project, "draft")
        self.assertEqual(len(self.jobs), 2)
        self.assertEqual(set(self.receipt()["frames"]), {"0", "2", "3"})
        self.assertFalse(self.receipt()["complete"])
        self.jobs.clear()
        with patch("pipeline.render.run", side_effect=self.successful_worker):
            render(self.project, "draft")
        self.assertEqual(sorted(n for _, job in self.jobs for n in job["frames"]), [1, 4, 5, 6, 7])
        verify_complete(self.project, "draft")

    def test_source_change_never_promotes_unverified_worker_frames(self):
        barrier = threading.Barrier(2, timeout=5)

        def worker(command, **kwargs):
            job = self.read_job(command, kwargs)
            barrier.wait()
            for number in job["frames"]:
                self.frame(job, number)
            if job["frames"][0] == 0:
                (self.root / "scenes/a.tsx").write_text("changed during render")
            barrier.wait()

        with patch("pipeline.render.run", side_effect=worker):
            with self.assertRaisesRegex(PipelineError, "Source changed"):
                render(self.project, "draft")
        self.assertEqual(len(self.jobs), 2)
        self.assertFalse((self.directory / "receipt.json").exists())
        self.assertEqual(list((self.directory / "frames").glob("*.png")), [])

    def test_stop_retains_finished_frames_without_dispatching_more(self):
        self.project.data["production"]["render_workers"] = 1

        def worker(command, **kwargs):
            job = self.read_job(command, kwargs)
            for number in job["frames"]:
                self.frame(job, number)
            Path(job["stop_file"]).touch()

        with patch("pipeline.render.run", side_effect=worker):
            with self.assertRaisesRegex(PipelineError, "STOP"):
                render(self.project, "draft")
        self.assertEqual(len(self.jobs), 1)
        self.assertEqual(set(self.receipt()["frames"]), {"0", "1"})
        (self.project.output("draft") / "STOP").unlink()
        self.jobs.clear()
        with patch("pipeline.render.run", side_effect=self.successful_worker):
            render(self.project, "draft")
        self.assertEqual(sorted(n for _, job in self.jobs for n in job["frames"]), list(range(2, 8)))

    def test_worker_count_keeps_fingerprint_and_serial_parallel_image_identity(self):
        with patch("pipeline.render.run", side_effect=self.successful_worker):
            render(self.project, "draft")
            parallel = self.receipt()
            self.project.data["production"]["render_workers"] = 1
            self.assertEqual(fingerprint(self.project, self.project.shots[0], "draft")[0], parallel["fingerprint"])
            self.jobs.clear()
            render(self.project, "draft")
            self.assertEqual(self.jobs, [])
            render(self.project, "draft", force=True)
        self.assertEqual(self.receipt()["frames"], parallel["frames"])

    def test_orphan_staging_cannot_replace_verified_canonical_frame(self):
        with patch("pipeline.render.run", side_effect=self.successful_worker):
            render(self.project, "draft")
        job = self.jobs[0][1]
        number = job["frames"][0]
        Image.new("RGB", (32, 18), "red").save(Path(job["out_dir"]) / f"frame_{number:06d}.png")
        verify_complete(self.project, "draft")
        self.jobs.clear()
        with patch("pipeline.render.run", side_effect=self.successful_worker):
            render(self.project, "draft")
        self.assertEqual(self.jobs, [])

    def test_worker_count_defaults_to_one_and_rejects_invalid_values(self):
        self.assertEqual(plan(self.project, "draft")["workers"], 2)
        self.project.data["production"].pop("render_workers")
        validate(self.project)
        self.assertEqual(plan(self.project, "draft")["workers"], 1)
        for value in (0, -1, True, 1.5, "2", 33):
            with self.subTest(value=value):
                self.project.data["production"]["render_workers"] = value
                with self.assertRaisesRegex(PipelineError, "render_workers"):
                    validate(self.project)


if __name__ == "__main__":
    unittest.main()
