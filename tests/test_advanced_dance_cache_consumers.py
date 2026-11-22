"""Audit records describe the verified loaded cloth, not a later path version."""
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "engine"))

from tools.advanced_dance import cloth_qa, prepare, render, scene


class LoadedCacheIdentityTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.path = self.root / "cache.npy"
        self.loaded_hash = hashlib.sha256(b"verified loaded states").hexdigest()
        self.body = SimpleNamespace(actor=SimpleNamespace(
            advanced_score=SimpleNamespace(role=0)))

    def load_then_change_file(self, body):
        # The loader has already installed a private copy of version A. The
        # path now contains version B before the consumer records its evidence.
        body.advanced_cloth_cache = str(self.path)
        body.advanced_cloth_receipt = {"sha256": self.loaded_hash}
        self.path.write_bytes(b"a later version of the cache path")
        return True

    def test_cloth_audit_rejects_changed_file_before_measuring_loaded_states(self):
        with patch.object(cloth_qa, "motion_key", return_value="pinned-key"), \
                patch.object(cloth_qa, "load_cloth", side_effect=self.load_then_change_file), \
                patch.object(cloth_qa, "audit_cloth") as measuring:
            with self.assertRaisesRegex(RuntimeError, "changed after verified loading"):
                cloth_qa.audit_rendered_cloth(self.body)
            measuring.assert_not_called()

    def test_native_frame_receipt_uses_actual_loaded_bytes_after_path_changes(self):
        renderer = SimpleNamespace(ctx=SimpleNamespace(info={"GL_RENDERER": "test renderer"}))

        def build_renderer(*args, **kwargs):
            self.assertTrue(scene.load_cloth(self.body))
            return renderer

        output = self.root / "frame"
        with patch.object(prepare, "ROOT", self.root), \
                patch.dict("os.environ", {}), \
                patch.object(scene, "load_cloth", side_effect=self.load_then_change_file), \
                patch.object(render, "source_hashes", return_value={"source.py": "fixed"}), \
                patch.object(render, "make_renderer", side_effect=build_renderer), \
                patch.object(render, "frame", return_value=b"test RGB bytes"), \
                patch("PIL.Image.frombytes"), \
                contextlib.redirect_stdout(io.StringIO()):
            prepare._frame_worker("solo", 0, "cached", output)

        recorded = json.loads(output.with_suffix(".json").read_text())
        self.assertEqual(recorded["cloth"][0]["sha256"], self.loaded_hash)
        self.assertNotEqual(recorded["cloth"][0]["sha256"],
                            hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(recorded["cloth"][0]["cache"], "cache.npy")


if __name__ == "__main__":
    unittest.main()
