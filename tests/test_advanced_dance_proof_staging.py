"""Proof staging keeps verified bytes across output filesystem boundaries."""
from __future__ import annotations

import errno
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.advanced_dance.prepare import _stage_proof_frame


class ProofFrameStagingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.source = root / "source.png"
        self.destination = root / "staged.png"
        self.content = b"verified frame bytes\x00\x01\xff" * 100
        self.source.write_bytes(self.content)
        self.expected = hashlib.sha256(self.content).hexdigest()

    def stage(self):
        _stage_proof_frame(self.source, self.destination, self.expected)

    def test_same_filesystem_keeps_the_fast_hardlink(self):
        self.stage()
        self.assertEqual(self.destination.read_bytes(), self.content)
        self.assertEqual(self.source.stat().st_ino, self.destination.stat().st_ino)

    def test_cross_filesystem_fallback_copies_exact_verified_bytes(self):
        with patch("tools.advanced_dance.prepare.os.link",
                   side_effect=OSError(errno.EXDEV, "different filesystem")):
            self.stage()
        self.assertEqual(self.destination.read_bytes(), self.content)
        self.assertNotEqual(self.source.stat().st_ino, self.destination.stat().st_ino)
        self.assertEqual(self.source.read_bytes(), self.content)

    def test_copy_rejects_source_changed_since_receipt_and_removes_destination(self):
        changed = b"changed after the receipt was validated"
        self.source.write_bytes(changed)
        with patch("tools.advanced_dance.prepare.os.link",
                   side_effect=OSError(errno.EXDEV, "different filesystem")):
            with self.assertRaisesRegex(ValueError, "verified receipt hash"):
                self.stage()
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.source.read_bytes(), changed)

    def test_failed_copy_removes_partial_destination_and_preserves_source(self):
        def fail_partway(original, copied, **kwargs):
            copied.write(original.read(3))
            raise OSError(errno.ENOSPC, "out of space")

        with patch("tools.advanced_dance.prepare.os.link",
                   side_effect=OSError(errno.EXDEV, "different filesystem")), \
                patch("tools.advanced_dance.prepare.shutil.copyfileobj", side_effect=fail_partway):
            with self.assertRaises(OSError) as failure:
                self.stage()
        self.assertEqual(failure.exception.errno, errno.ENOSPC)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.source.read_bytes(), self.content)

    def test_unrelated_link_failure_is_propagated_without_copying(self):
        with patch("tools.advanced_dance.prepare.os.link",
                   side_effect=PermissionError(errno.EACCES, "denied")), \
                patch("tools.advanced_dance.prepare.shutil.copyfileobj") as copying:
            with self.assertRaises(PermissionError) as failure:
                self.stage()
            copying.assert_not_called()
        self.assertEqual(failure.exception.errno, errno.EACCES)
        self.assertFalse(self.destination.exists())

    def test_cross_filesystem_fallback_does_not_replace_existing_destination(self):
        existing = b"previous staging contents"
        self.destination.write_bytes(existing)
        with patch("tools.advanced_dance.prepare.os.link",
                   side_effect=OSError(errno.EXDEV, "different filesystem")):
            with self.assertRaises(FileExistsError):
                self.stage()
        self.assertEqual(self.destination.read_bytes(), existing)
        self.assertEqual(self.source.read_bytes(), self.content)


if __name__ == "__main__":
    unittest.main()
