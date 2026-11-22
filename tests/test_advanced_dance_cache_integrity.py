"""Completed cloth is receipt-bound and never published from changed sources."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "engine"))

from tools.advanced_dance import cache, prepare


class CacheIntegrityTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.key = "a" * 64
        self.start_key = self.key
        self.states = np.arange(30, dtype=np.float32).reshape(5, 2, 3) / 100
        self.addCleanup(patch.stopall)
        patch.object(cache, "ROOT", self.root).start()
        patch.object(cache, "motion_key", side_effect=lambda body: self.key).start()
        patch.dict("os.environ", {"ADVANCED_DANCE_CLOTH_CACHE": "auto"}).start()

    def body(self, during_compute=None):
        cloth = SimpleNamespace(n=2, t_start=0., snaps=[], x=None, compute_calls=0)

        def positions(t):
            cloth.compute_calls += 1
            cloth.snaps = list(self.states.copy())
            if during_compute is not None:
                during_compute()
            return cloth.snaps[-1]

        cloth.positions = positions
        return SimpleNamespace(cloth=cloth, actor=SimpleNamespace(
            advanced_score=SimpleNamespace(mode="solo", role=0, duration=.1)))

    def completed(self):
        return Path(cache.bake_cloth(self.body()))

    def receipt(self, path):
        return json.loads(path.with_suffix(".json").read_text())

    def rebind_payload(self, path):
        receipt = self.receipt(path)
        payload = path.read_bytes()
        receipt.update(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        path.with_suffix(".json").write_text(json.dumps(receipt))

    def assert_uninstalled(self, body):
        self.assertEqual(body.cloth.snaps, [])
        self.assertIsNone(body.cloth.x)
        self.assertFalse(hasattr(body, "advanced_cloth_cache"))

    def test_direct_bake_writes_complete_receipt_and_exact_loadable_states(self):
        path = self.completed()
        receipt = self.receipt(path)
        self.assertEqual(receipt["status"], "complete")
        self.assertEqual(receipt["motion_key"], self.start_key)
        self.assertEqual(receipt["bytes"], path.stat().st_size)
        self.assertEqual(receipt["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        body = self.body()
        self.assertTrue(cache.load_cloth(body))
        np.testing.assert_array_equal(np.asarray(body.cloth.snaps), self.states)
        self.assertEqual(body.cloth.compute_calls, 0)

    def test_shape_preserving_corruption_is_rejected_before_installation(self):
        path = self.completed()
        changed = self.states.copy()
        changed[1, 0, 0] += 1
        np.save(path, changed, allow_pickle=False)
        body = self.body()
        with self.assertRaisesRegex(ValueError, "bytes do not match"):
            cache.load_cloth(body)
        self.assert_uninstalled(body)

    def test_receipt_identity_fields_are_checked(self):
        path = self.completed()
        receipt = self.receipt(path)
        for field, bad_value in (("motion_key", "b" * 64), ("mode", "ensemble"),
                                 ("role", 4), ("cache", "elsewhere.npy"),
                                 ("duration_seconds", 32), ("shape", [5, 3, 3]),
                                 ("dtype", "float64"), ("schema_version", 99)):
            with self.subTest(field=field):
                path.with_suffix(".json").write_text(json.dumps(dict(receipt, **{field: bad_value})))
                body = self.body()
                with self.assertRaisesRegex(ValueError, "receipt identity"):
                    cache.load_cloth(body)
                self.assert_uninstalled(body)

    def test_receipt_byte_count_is_checked(self):
        path = self.completed()
        receipt = self.receipt(path)
        receipt["bytes"] += 1
        path.with_suffix(".json").write_text(json.dumps(receipt))
        body = self.body()
        with self.assertRaisesRegex(ValueError, "bytes do not match"):
            cache.load_cloth(body)
        self.assert_uninstalled(body)

    def test_nonfinite_payload_is_rejected_even_with_matching_receipt_hash(self):
        path = self.completed()
        changed = self.states.copy()
        changed[1, 0, 0] = np.nan
        np.save(path, changed, allow_pickle=False)
        self.rebind_payload(path)
        body = self.body()
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            cache.load_cloth(body)
        self.assert_uninstalled(body)

    def test_actual_dtype_and_shape_are_checked_after_hash_validation(self):
        path = self.completed()
        for changed in (self.states.astype(np.float64), self.states[:, :1]):
            with self.subTest(shape=changed.shape, dtype=str(changed.dtype)):
                np.save(path, changed, allow_pickle=False)
                self.rebind_payload(path)
                body = self.body()
                with self.assertRaisesRegex(ValueError, "shape or dtype"):
                    cache.load_cloth(body)
                self.assert_uninstalled(body)

    def test_loaded_states_do_not_follow_later_changes_to_cache_file(self):
        path = self.completed()
        body = self.body()
        self.assertTrue(cache.load_cloth(body))
        np.save(path, np.zeros_like(self.states), allow_pickle=False)
        np.testing.assert_array_equal(np.asarray(body.cloth.snaps), self.states)

    def test_missing_receipt_is_a_miss_and_bake_can_repair_the_pair(self):
        path = self.completed()
        path.with_suffix(".json").unlink()
        body = self.body()
        self.assertFalse(cache.load_cloth(body))
        self.assert_uninstalled(body)
        with patch.dict("os.environ", {"ADVANCED_DANCE_CLOTH_CACHE": "required"}):
            with self.assertRaises(FileNotFoundError):
                cache.load_cloth(self.body())
        repaired = self.body()
        self.assertEqual(Path(cache.bake_cloth(repaired)), path)
        self.assertEqual(repaired.cloth.compute_calls, 1)
        self.assertTrue(cache.load_cloth(self.body()))

    def test_changed_motion_key_during_computation_never_publishes_either_key(self):
        body = self.body(lambda: setattr(self, "key", "b" * 64))
        with self.assertRaisesRegex(RuntimeError, "sources changed"):
            cache.bake_cloth(body)
        self.assertFalse(list(self.root.rglob("*.npy")))
        self.assertFalse(list(self.root.rglob("*.json")))

    def test_prepare_full_source_guard_runs_before_cache_publication(self):
        source = {"lighting.py": "before"}
        body = self.body(lambda: source.update({"lighting.py": "after"}))
        with patch("tools.advanced_dance.render.source_hashes", side_effect=lambda: dict(source)), \
                patch.object(prepare, "build_one", return_value=body), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "sources changed"):
                prepare.bake("solo")
        self.assertFalse(list(self.root.rglob("*.npy")))
        self.assertFalse(list(self.root.rglob("*.json")))

    def test_interrupted_receipt_publication_remains_incomplete_and_retry_succeeds(self):
        directory = self.root / "work/advanced-dance/cloth-cache"
        directory.mkdir(parents=True)
        unrelated = directory / "another-writer.partial.npy"
        unrelated.write_bytes(b"unrelated")
        original_replace = Path.replace

        def interrupt_complete(path, destination):
            if path.name == "complete.json":
                raise OSError("interrupted final receipt publication")
            return original_replace(path, destination)

        with patch.object(Path, "replace", interrupt_complete):
            with self.assertRaisesRegex(OSError, "interrupted"):
                cache.bake_cloth(self.body())
        path = directory / (self.start_key + ".npy")
        self.assertTrue(path.is_file())
        self.assertEqual(self.receipt(path)["status"], "incomplete")
        self.assertFalse(cache.load_cloth(self.body()))
        with patch.dict("os.environ", {"ADVANCED_DANCE_CLOTH_CACHE": "required"}):
            with self.assertRaises(FileNotFoundError):
                cache.load_cloth(self.body())
        self.assertFalse([p for p in directory.iterdir() if p.is_dir()])
        self.assertEqual(unrelated.read_bytes(), b"unrelated")
        self.assertEqual(Path(cache.bake_cloth(self.body())), path)
        self.assertEqual(self.receipt(path)["status"], "complete")
        self.assertTrue(cache.load_cloth(self.body()))

    def test_source_change_after_array_installation_blocks_completion_receipt(self):
        original_replace = Path.replace

        def change_after_array(path, destination):
            result = original_replace(path, destination)
            if path.name == "snapshots.npy":
                self.key = "b" * 64
            return result

        with patch.object(Path, "replace", change_after_array):
            with self.assertRaisesRegex(RuntimeError, "sources changed"):
                cache.bake_cloth(self.body())
        path = self.root / "work/advanced-dance/cloth-cache" / (self.start_key + ".npy")
        self.assertEqual(self.receipt(path)["status"], "incomplete")
        self.key = self.start_key
        self.assertFalse(cache.load_cloth(self.body()))

    def test_source_change_during_final_byte_verification_blocks_completion_receipt(self):
        original_read = Path.read_bytes

        def change_after_read(path):
            payload = original_read(path)
            if path.name == self.start_key + ".npy":
                self.key = "b" * 64
            return payload

        with patch.object(Path, "read_bytes", change_after_read):
            with self.assertRaisesRegex(RuntimeError, "sources changed"):
                cache.bake_cloth(self.body())
        path = self.root / "work/advanced-dance/cloth-cache" / (self.start_key + ".npy")
        self.assertEqual(self.receipt(path)["status"], "incomplete")
        self.key = self.start_key
        self.assertFalse(cache.load_cloth(self.body()))

    def test_prepare_enriches_existing_completion_without_recomputing_snapshots(self):
        path = self.completed()
        original_payload = path.read_bytes()
        body = self.body(lambda: self.fail("Existing valid cache was unnecessarily recomputed"))
        sources = {"lighting.py": "reviewed-source"}
        with patch("tools.advanced_dance.render.source_hashes", return_value=sources), \
                patch.object(prepare, "build_one", return_value=body), \
                contextlib.redirect_stdout(io.StringIO()):
            records = prepare.bake("solo")
        self.assertEqual(body.cloth.compute_calls, 0)
        self.assertEqual(path.read_bytes(), original_payload)
        self.assertEqual(records[0]["source_sha256"], sources)
        self.assertIn("elapsed_seconds", records[0])
        self.assertEqual(self.receipt(path), records[0])
        self.assertTrue(cache.load_cloth(self.body()))

    def test_audit_metadata_cannot_override_completion_identity(self):
        with self.assertRaisesRegex(ValueError, "identity fields"):
            cache.bake_cloth(self.body(), receipt_metadata={"sha256": "wrong"})
        self.assertFalse(list(self.root.rglob("*.npy")))
        self.assertFalse(list(self.root.rglob("*.json")))


if __name__ == "__main__":
    unittest.main()
