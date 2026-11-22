"""Do not silently drop captions or attach approval to a different master."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline.cli import archive, doctor
from pipeline.media import assemble
from pipeline.project import PipelineError, file_hash, write_json
from test_contract import project_fixture


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.project = project_fixture(self.root)

    def test_ffmpeg_cannot_drop_requested_captions(self):
        self.project.data["captions"] = [{"text": "Review title", "start_frame": 0, "end_frame_exclusive": 4}]
        with patch("pipeline.media.guard_render"):
            with self.assertRaisesRegex(PipelineError, "--editor remotion"):
                assemble(self.project, "draft", editor="ffmpeg")
        self.assertFalse(self.project.output("draft").exists())

    def archive_fixture(self):
        directory = self.project.output("draft")
        directory.mkdir(parents=True)
        master = directory / "master.mp4"
        master.write_bytes(b"test-master-bytes")
        digest = file_hash(master)
        write_json(directory / "qa.json", {"technical_passed": True, "master_sha256": digest})
        receipts = [{"shot_id": "a", "fingerprint": "first"}, {"shot_id": "b", "fingerprint": "second"}]
        write_json(directory / "master.json", {"project_identity": self.project.identity(), "shot_fingerprints": {r["shot_id"]: r["fingerprint"] for r in receipts}})
        return directory, digest, receipts

    def test_stale_approval_is_preserved_but_omitted_from_archive(self):
        directory, digest, receipts = self.archive_fixture()
        write_json(directory / "approval.json", {"confirmed_viewed": True, "master_sha256": "different-master", "project_identity": self.project.identity()})
        with patch("pipeline.cli.verify_complete", return_value=receipts):
            target = archive(self.project, "draft", str(self.root / "archives"))
        self.assertTrue((directory / "approval.json").exists())
        self.assertFalse((target / "approval.json").exists())
        self.assertEqual(json.loads((target / "archive-manifest.json").read_text())["creative_review"], "stale_review_omitted")

    def test_matching_approval_is_included(self):
        directory, digest, receipts = self.archive_fixture()
        write_json(directory / "approval.json", {"confirmed_viewed": True, "master_sha256": digest, "project_identity": self.project.identity()})
        with patch("pipeline.cli.verify_complete", return_value=receipts):
            target = archive(self.project, "draft", str(self.root / "archives"))
        self.assertTrue((target / "approval.json").exists())

    def test_doctor_does_not_claim_runtime_from_installed_binaries(self):
        (self.root / "node_modules").mkdir()
        untested = {"installed": True, "runtime_validated": False, "status": "not_probed", "executable": "/selected/browser"}
        with patch("pipeline.cli.browser_probe", return_value=untested), patch("pipeline.cli.command_version", return_value="installed version"), patch("pipeline.cli.shutil.which", return_value="/installed/tool"):
            report = doctor(self.root)
        self.assertTrue(report["dependencies_ready"])
        self.assertFalse(report["full_pipeline_runtime_verified"])
        self.assertFalse(report["runtime_validation"]["browser"]["runtime_validated"])
        self.assertNotIn("ready", report)
        self.assertEqual(report["binaries"]["chromium"], "/selected/browser")


if __name__ == "__main__":
    unittest.main()
