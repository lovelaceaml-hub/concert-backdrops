"""Acceptance gates for evidence attached to the exact finished dance movies."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.advanced_dance import delivery_evidence as evidence


PICTURE_COMMIT = "a" * 40
FROZEN_SOURCES = {"tools/advanced_dance/score.py": "b" * 64}
MOVIES = {"solo": "c" * 64, "ensemble": "d" * 64}
FINGERPRINTS = {"solo": "e" * 64, "ensemble": "f" * 64}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    raw = path.read_bytes()
    return {"path": path.name, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def production_reports():
    """Minimal actual pipeline schemas for two distinct completed productions."""
    reports = []
    for mode in ("solo", "ensemble"):
        project = "advanced-dance-" + mode
        common = {"project_id": project, "quality": "final",
                  "filename": "master.mp4", "frames": 1920, "fps": 60}
        contents = {
            "assembly": {**common, "sha256": MOVIES[mode],
                         "shot_fingerprints": {"performance": FINGERPRINTS[mode]}},
            "pipeline_qa": {**common, "master_sha256": MOVIES[mode],
                            "technical_passed": True, "errors": []},
            "render": {
                "shot_id": "performance", "complete": True,
                "width": 1920, "height": 1080, "fps": 60,
                "fingerprint": FINGERPRINTS[mode],
                "frames": {str(frame): "0" * 64 for frame in range(1920)},
                "provenance": {"shot": {"scene": f"tools/advanced_dance/{mode}.py",
                    "start_frame": 0, "end_frame_exclusive": 1920},
                    "inputs": dict(FROZEN_SOURCES)},
            },
            "proof": {"mode": mode, "source_fingerprint": FINGERPRINTS[mode]},
        }
        reports.extend({"label": mode + "_" + kind, "content": content}
                       for kind, content in contents.items())
    return reports


def report_content(reports, label):
    return next(row["content"] for row in reports if row["label"] == label)


class EvidenceDependencyTests(unittest.TestCase):
    def test_evidence_import_needs_no_installed_media_or_numeric_packages(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "-S", "-c",
            "from tools.advanced_dance import delivery_evidence; "
            "import sys; assert 'numpy' not in sys.modules; "
            "assert 'PIL' not in sys.modules"],
            cwd=root, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


class LedgerEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.frozen = self.root / "frozen.json"
        record = write_json(self.frozen, {"source_sha256": FROZEN_SOURCES})
        self.ledger = {"picture_source": {"commit": PICTURE_COMMIT},
            "package_evidence": {"full_json_reports": ["frozen_picture_inputs"]},
            "artifacts": {"frozen_picture_inputs": record}}
        self.path = self.root / "ledger.json"
        write_json(self.path, self.ledger)

    def bind(self):
        return evidence.ledger_qa_arguments(self.path, PICTURE_COMMIT, root=self.root)

    def test_valid_ledger_preserves_exact_report_bytes_and_frozen_sources(self):
        result = self.bind()
        self.assertEqual(result["frozen_sources"], FROZEN_SOURCES)
        self.assertEqual(result["record"]["bound_report_count"], 1)
        self.assertEqual(result["arguments"], [f"validation_ledger={self.path}",
                                              f"frozen_picture_inputs={self.frozen}"])
        self.assertEqual(result["snapshots"][self.frozen],
                         hashlib.sha256(self.frozen.read_bytes()).hexdigest())

    def test_changed_source_commit_or_bound_report_is_rejected(self):
        with self.assertRaisesRegex(evidence.DeliveryError, "picture commit"):
            evidence.ledger_qa_arguments(self.path, "9" * 40, root=self.root)
        self.frozen.write_text('{"source_sha256": {}}')
        with self.assertRaisesRegex(evidence.DeliveryError, "QA bytes changed"):
            self.bind()

    def test_report_cannot_escape_checkout_even_through_symlink(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "outside.json"
            target.write_bytes(self.frozen.read_bytes())
            link = self.root / "link.json"
            link.symlink_to(target)
            self.ledger["artifacts"]["frozen_picture_inputs"]["path"] = link.name
            write_json(self.path, self.ledger)
            with self.assertRaisesRegex(evidence.DeliveryError, "outside the checkout"):
                self.bind()

    def test_duplicate_and_reserved_ledger_labels_are_rejected(self):
        for names, message in ((["frozen_picture_inputs"] * 2, "unique"),
                               (["validation_ledger"], "reserved")):
            with self.subTest(names=names):
                self.ledger["package_evidence"]["full_json_reports"] = names
                write_json(self.path, self.ledger)
                with self.assertRaisesRegex(evidence.DeliveryError, message):
                    self.bind()


class ReportEmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "review.json"

    def read(self, record, label="solo_review", snapshots=None):
        write_json(self.path, record)
        return evidence.read_qa([f"{label}={self.path}"], MOVIES,
                                {} if snapshots is None else snapshots)

    def test_intentional_review_flags_remain_visible_and_do_not_become_errors(self):
        record = {"mode": "solo", "status": "review_required", "errors": [],
                  "review_flags": [{"time": 12.5, "reason": "fast hand"}],
                  "master_sha256": MOVIES["solo"]}
        rows = self.read(record)
        self.assertEqual(rows[0]["content"], record)
        self.assertEqual(rows[0]["source_sha256"],
                         hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_blocking_reports_are_rejected_for_each_supported_gate(self):
        cases = ({"status": "blocked"}, {"status": "failed"},
                 {"error_count": 1}, {"errors": ["bad foot contact"]},
                 {"technical_passed": False}, {"blocking_visual_defects_found": True})
        for record in cases:
            with self.subTest(record=record), self.assertRaises(evidence.DeliveryError):
                self.read(record)

    def test_duplicate_labels_and_conflicting_performer_identity_are_rejected(self):
        write_json(self.path, {"mode": "solo"})
        argument = f"solo_review={self.path}"
        with self.assertRaisesRegex(evidence.DeliveryError, "Duplicate QA label"):
            evidence.read_qa([argument, argument], MOVIES, {})
        with self.assertRaisesRegex(evidence.DeliveryError, "Conflicting QA"):
            self.read({"mode": "ensemble"})

    def test_changed_bound_file_and_wrong_master_are_rejected(self):
        original = write_json(self.path, {"mode": "solo"})
        snapshots = {self.path: original["sha256"]}
        with self.assertRaisesRegex(evidence.DeliveryError, "changed before embedding"):
            self.read({"mode": "solo", "new": True}, snapshots=snapshots)
        with self.assertRaisesRegex(evidence.DeliveryError, "master hash"):
            self.read({"mode": "solo", "master_sha256": MOVIES["ensemble"]})


class FinalProductionBindingTests(unittest.TestCase):
    def verify(self, reports):
        return evidence.verify_production_bindings(reports, MOVIES, FROZEN_SOURCES)

    def test_valid_receipts_link_two_distinct_masters_and_their_proofs(self):
        result = self.verify(production_reports())
        self.assertEqual(set(result), {"solo", "ensemble"})
        for mode in result:
            self.assertEqual(result[mode]["master_sha256"], MOVIES[mode])
            self.assertEqual(result[mode]["render_fingerprint"], FINGERPRINTS[mode])
            self.assertEqual(result[mode]["recorded_frame_hash_count"], 1920)
            self.assertEqual(result[mode]["linked_proof_or_review_reports"], [mode + "_proof"])

    def test_missing_or_duplicate_pipeline_record_cannot_be_accepted(self):
        for duplicate in (False, True):
            rows = production_reports()
            if duplicate:
                rows.append(copy.deepcopy(rows[0]))
            else:
                rows.pop(0)
            with self.subTest(duplicate=duplicate), \
                    self.assertRaisesRegex(evidence.DeliveryError, "exactly one solo"):
                self.verify(rows)

    def test_mismatched_master_fingerprint_or_source_is_rejected(self):
        cases = (
            ("solo_assembly", "sha256", MOVIES["ensemble"], "exact supplied master"),
            ("solo_proof", "source_fingerprint", FINGERPRINTS["ensemble"], "different source fingerprint"),
        )
        for label, key, value, message in cases:
            rows = production_reports()
            report_content(rows, label)[key] = value
            with self.subTest(label=label), self.assertRaisesRegex(evidence.DeliveryError, message):
                self.verify(rows)
        rows = production_reports()
        report_content(rows, "solo_render")["provenance"]["inputs"] = {}
        with self.assertRaisesRegex(evidence.DeliveryError, "frozen validation ledger"):
            self.verify(rows)

    def test_render_must_be_complete_with_every_exact_frame_and_scene_interval(self):
        for defect in ("incomplete", "missing_frame", "wrong_hash", "wrong_scene", "wrong_interval"):
            rows = production_reports()
            render = report_content(rows, "ensemble_render")
            if defect == "incomplete":
                render["complete"] = False
            elif defect == "missing_frame":
                del render["frames"]["1919"]
            elif defect == "wrong_hash":
                render["frames"]["1919"] = "invalid"
            elif defect == "wrong_scene":
                render["provenance"]["shot"]["scene"] = "tools/advanced_dance/solo.py"
            else:
                render["provenance"]["shot"]["end_frame_exclusive"] = 1919
            with self.subTest(defect=defect), self.assertRaises(evidence.DeliveryError):
                self.verify(rows)


if __name__ == "__main__":
    unittest.main()
