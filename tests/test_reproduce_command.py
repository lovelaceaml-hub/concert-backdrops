"""Focused tests for reproducing approved films from their recorded commits."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from pipeline import approved, cli
from pipeline.project import PipelineError, file_hash, write_json


REPOSITORY = Path(__file__).resolve().parents[1]


def load_motion_revision():
    import importlib, sys
    if str(REPOSITORY) not in sys.path:
        sys.path.insert(0, str(REPOSITORY))
    return importlib.import_module("tools.concert_motion_revision.render")


class CommitLookupTests(unittest.TestCase):
    def test_finds_recorded_commits_in_deliveries_catalog(self):
        self.assertEqual(
            cli.recorded_project_commit(REPOSITORY, "concert-kit-consideration-v2"),
            "33a7d87e2848bf8a42e6d8132c34544d61259350",
        )
        self.assertEqual(
            cli.recorded_project_commit(REPOSITORY, "cinematic-ten-01"),
            "df4fc478116d3f0e34a85d2166097fbda55911bf",
        )
        self.assertEqual(
            cli.recorded_project_commit(REPOSITORY, "advanced-dance-solo"),
            "254414bc0356171f7d5ad89361c75d45fd01a407",
        )

    def test_falls_back_to_approved_reference_commit(self):
        self.assertEqual(
            cli.recorded_project_commit(REPOSITORY, "approved-light-s11"),
            "23c9307608291a99702d687933c8d2092d1fd01d",
        )

    def test_missing_project_or_commit_raises_plain_error(self):
        with self.assertRaisesRegex(PipelineError, "no recorded commit"):
            cli.recorded_project_commit(REPOSITORY, "does-not-exist")
        with self.assertRaisesRegex(PipelineError, "does not record a picture_source_commit"):
            cli.recorded_project_commit(REPOSITORY, "consideration-baseline-18s")
        with self.assertRaisesRegex(PipelineError, "hexadecimal Git SHA"):
            cli._validate_commit_sha("--upload-pack=bad")


class ReproduceCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        write_json(
            self.root / cli.DELIVERIES_CATALOG,
            {
                "schema_version": 1,
                "items": [
                    {
                        "id": "consideration-revised-15s",
                        "project_id": "concert-kit-consideration-v2",
                        "picture_source_commit": "33a7d87e2848bf8a42e6d8132c34544d61259350",
                    }
                ],
            },
        )

    def test_creates_worktree_and_runs_commit_video_produce(self):
        sha = "33a7d87e2848bf8a42e6d8132c34544d61259350"
        expected_worktree = self.root / f"work/reproduce/concert-kit-consideration-v2-{sha[:8]}"
        calls = []

        def fake_run(command, **kwargs):
            self.assertIsInstance(command, list)
            self.assertNotIn("shell", kwargs)
            calls.append((command, kwargs.get("cwd")))
            if command[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(command, 0, stdout=sha + "\n", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with patch("pipeline.cli.subprocess.run", side_effect=fake_run):
            result = cli.reproduce(self.root, "concert-kit-consideration-v2", quality="review")

        self.assertEqual(result["commit"], sha)
        self.assertFalse(result["reused_worktree"])
        self.assertEqual(result["worktree"], str(expected_worktree))
        self.assertEqual(
            result["output_dir"],
            str(expected_worktree / "work/pipeline/concert-kit-consideration-v2/review"),
        )
        self.assertEqual(
            calls,
            [
                (["git", "rev-parse", "--verify", f"{sha}^{{commit}}"], self.root),
                (["git", "cat-file", "-e", f"{sha}:projects/concert-kit-consideration-v2/project.json"], self.root),
                (["git", "worktree", "add", "--detach", str(expected_worktree), sha], self.root),
                (["./scripts/video", "produce", "concert-kit-consideration-v2", "--quality", "review"], expected_worktree),
            ],
        )

    def test_reuses_existing_worktree_without_recreating_it(self):
        sha = "33a7d87e2848bf8a42e6d8132c34544d61259350"
        worktree = self.root / f"work/reproduce/concert-kit-consideration-v2-{sha[:8]}"
        worktree.mkdir(parents=True)
        (worktree / ".git").write_text("gitdir: /fake/worktree\n")
        calls = []

        def fake_run(command, **kwargs):
            calls.append((command, kwargs.get("cwd")))
            if command[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(command, 0, stdout=sha + "\n", stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with patch("pipeline.cli.subprocess.run", side_effect=fake_run):
            result = cli.reproduce(self.root, "concert-kit-consideration-v2", quality="final")

        self.assertTrue(result["reused_worktree"])
        self.assertEqual(
            calls,
            [
                (["git", "rev-parse", "--verify", f"{sha}^{{commit}}"], self.root),
                (["git", "cat-file", "-e", f"{sha}:projects/concert-kit-consideration-v2/project.json"], self.root),
                (["git", "rev-parse", "HEAD"], worktree),
                (["git", "status", "--porcelain", "--untracked-files=no"], worktree),
                (["./scripts/video", "produce", "concert-kit-consideration-v2", "--quality", "final"], worktree),
            ],
        )

    def test_rejects_commit_without_the_project(self):
        sha = "33a7d87e2848bf8a42e6d8132c34544d61259350"

        def fake_run(command, **kwargs):
            if command[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(command, 0, stdout=sha + "\n", stderr="")
            if command[:2] == ["git", "cat-file"]:
                return subprocess.CompletedProcess(command, 128, stdout="", stderr="missing")
            if command[:2] == ["git", "log"]:
                return subprocess.CompletedProcess(command, 0, stdout="1e3ffe3aaaa\n", stderr="")
            raise AssertionError(f"unexpected command {command}")

        with patch("pipeline.cli.subprocess.run", side_effect=fake_run):
            with self.assertRaisesRegex(PipelineError, "does not contain projects/concert-kit-consideration-v2.*1e3ffe3aaaa"):
                cli.reproduce(self.root, "concert-kit-consideration-v2")

    def test_rejects_reusing_a_modified_worktree(self):
        sha = "33a7d87e2848bf8a42e6d8132c34544d61259350"
        worktree = self.root / f"work/reproduce/concert-kit-consideration-v2-{sha[:8]}"
        worktree.mkdir(parents=True)
        (worktree / ".git").write_text("gitdir: /fake/worktree\n")

        def fake_run(command, **kwargs):
            if command[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(command, 0, stdout=sha + "\n", stderr="")
            if command[:2] == ["git", "status"]:
                return subprocess.CompletedProcess(command, 0, stdout=" M engine/render.py\n", stderr="")
            if command[0] == "./scripts/video":
                raise AssertionError("must not render from a modified worktree")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with patch("pipeline.cli.subprocess.run", side_effect=fake_run):
            with self.assertRaisesRegex(PipelineError, "changed tracked files"):
                cli.reproduce(self.root, "concert-kit-consideration-v2")

    def test_commit_override_and_missing_git_commit_error(self):
        override = "abcdef1234567890abcdef1234567890abcdef12"

        def missing_commit(command, **kwargs):
            return subprocess.CompletedProcess(command, 128, stdout="", stderr="fatal: Needed a single revision")

        with patch("pipeline.cli.subprocess.run", side_effect=missing_commit):
            with self.assertRaisesRegex(PipelineError, f"Commit {override} is not available"):
                cli.reproduce(self.root, "custom-project", quality="review", commit=override)

    def test_cli_reproduce_outputs_json_and_handles_missing_project(self):
        sha = "33a7d87e2848bf8a42e6d8132c34544d61259350"

        def fake_run(command, **kwargs):
            stdout = sha + "\n" if command[:2] == ["git", "rev-parse"] else ""
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

        out = io.StringIO()
        with patch("pipeline.cli.subprocess.run", side_effect=fake_run), contextlib.redirect_stdout(out):
            code = cli.main(["--root", str(self.root), "reproduce", "concert-kit-consideration-v2"])
        self.assertEqual(code, 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["commit"], sha)
        self.assertEqual(report["quality"], "review")
        self.assertTrue(report["output_dir"].endswith("/work/pipeline/concert-kit-consideration-v2/review"))

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            missing_code = cli.main(["--root", str(self.root), "reproduce", "unknown-film"])
        self.assertEqual(missing_code, 2)
        self.assertIn("no recorded commit", err.getvalue())


class FrozenEngineErrorTests(unittest.TestCase):
    def test_approved_engine_mismatch_points_to_frozen_commit_and_reproduce(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            engine_file = root / "engine/p3d/actor.py"
            engine_file.parent.mkdir(parents=True)
            engine_file.write_text("# original\n")
            commit = "23c9307608291a99702d687933c8d2092d1fd01d"
            write_json(
                root / approved.REFERENCE_FILE,
                {
                    "source_commit": commit,
                    "source_files": {"engine/p3d/actor.py": file_hash(engine_file)},
                },
            )
            approved.verify_reference_files(root)
            engine_file.write_text("# improved engine\n")
            with self.assertRaises(PipelineError) as raised:
                approved.verify_reference_files(root)
            message = str(raised.exception)
            self.assertIn(f"frozen to commit {commit}", message)
            self.assertIn("./scripts/video reproduce approved-light-s11", message)

    def test_approved_real_checkout_reports_frozen_commit_on_changed_engine(self):
        with self.assertRaises(PipelineError) as raised:
            approved.verify_reference_files(REPOSITORY, restored=False)
        message = str(raised.exception)
        self.assertIn("frozen to commit 23c9307608291a99702d687933c8d2092d1fd01d", message)
        self.assertIn("./scripts/video reproduce approved-light-s11", message)

    def test_motion_revision_mismatch_points_to_frozen_commit_and_reproduce(self):
        module = load_motion_revision()
        with patch.object(module.base, "source_hashes", return_value={"engine/render.py": "0" * 64}):
            with self.assertRaises(RuntimeError) as raised:
                module.source_hashes()
        message = str(raised.exception)
        self.assertIn("frozen to commit 33a7d87e2848bf8a42e6d8132c34544d61259350", message)
        self.assertIn("./scripts/video reproduce concert-kit-consideration-v2", message)


if __name__ == "__main__":
    unittest.main()
