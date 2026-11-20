"""Exercise actual CPU codecs and fail closed on an 8-bit or mislabeled master."""
from __future__ import annotations

import copy
import json
import math
import shutil
import struct
import subprocess
import tempfile
import unittest
import wave
import zlib
from pathlib import Path
from unittest.mock import patch

from pipeline.delivery import PROFILES, resolve_profile, stream_validation_errors, validate_source_frames, video_encoding_args
from pipeline.media import assemble, current_master_path, finishing_input_hashes, probe, qa
from pipeline.project import PipelineError, file_hash, write_json
from test_contract import project_fixture


def write_png16(path: Path, width: int, height: int, frame: int = 0, *, gray: int | None = None) -> None:
    """A true RGB16 gradient: adjacent samples contain nonzero low-order bits."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    rows = []
    for y in range(height):
        row = struct.pack(">HHH", gray, gray, gray) * width if gray is not None else b"".join(struct.pack(">HHH", (x * 977 + frame * 283) % 65536, (y * 1733 + x * 181) % 65536, (x * 509 + y * 257 + 8000) % 65536) for x in range(width))
        rows.append(b"\x00" + row)
    header = struct.pack(">IIBBBBB", width, height, 16, 2, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b""))


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg and ffprobe are required for real encoding tests")
class DeliveryProfileTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.project = project_fixture(self.root)
        self.project.data["video"] = {"width": 64, "height": 36, "fps": 60}
        self.project.data["timing"]["fps"] = 60
        self.project.data["quality"] = {name: {"width": 64, "height": 36, "samples": 1, "image_bit_depth": 16} for name in ("draft", "review", "final")}
        self.project.shots[0]["end_frame_exclusive"] = 4
        self.project.shots[1]["start_frame"] = 4
        self.project.shots[1]["end_frame_exclusive"] = 8
        self.receipts = [{"shot_id": shot["id"], "fingerprint": "test-source-" + shot["id"]} for shot in self.project.shots]
        for shot in self.project.shots:
            folder = self.project.output("final") / "shots" / shot["id"] / "frames"
            for frame in range(shot["start_frame"], shot["end_frame_exclusive"]):
                write_png16(folder / f"frame_{frame:06d}.png", 64, 36, frame)

    def create_audio(self):
        path = self.root / "audio" / "test.wav"
        path.parent.mkdir()
        with wave.open(str(path), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(48000)
            audio.writeframes(b"".join(struct.pack("<h", round(3000 * math.sin(2 * math.pi * 330 * sample / 48000))) for sample in range(48000 // 2)))
        self.project.data["audio"]["source"] = "audio/test.wav"

    def test_real_cpu_codecs_preserve_clock_formats_and_audio(self):
        self.create_audio()
        for name, profile in PROFILES.items():
            with self.subTest(profile=name), patch("pipeline.media.verify_complete", return_value=self.receipts):
                master = assemble(self.project, "final", profile=name)
                metadata = probe(master)
                self.assertEqual(master.name, profile.master_filename)
                self.assertEqual(current_master_path(self.project, "final"), master)
                self.assertEqual(stream_validation_errors(metadata, profile, width=64, height=36, fps=60, frames=8, wanted_audio=True), [])
                receipt = json.loads((master.parent / "master.json").read_text())
                self.assertEqual(receipt["source_frames"]["png_bit_depths"], [16])
                self.assertFalse(receipt["color"]["hdr"])
                report = qa(self.project, "final")
                self.assertTrue(report["technical_passed"], report["errors"])
                self.assertTrue(report["motion"]["scan_complete"])
                self.assertEqual(report["delivery_profile"], name)
                self.assertEqual(report["creative_approval"], "not_assessed")
                self.assertIn(master.name, (master.parent / "review.html").read_text())

    def test_real_hevc_validation_rejects_wrong_tags_precision_or_audio(self):
        with patch("pipeline.media.verify_complete", return_value=self.receipts):
            metadata = probe(assemble(self.project, "final", profile="hevc10"))
        for field, bad_value in (("color_transfer", "smpte2084"), ("color_range", "pc"), ("pix_fmt", "yuv420p"), ("nb_read_frames", "7"), ("r_frame_rate", "30/1")):
            with self.subTest(field=field):
                broken = copy.deepcopy(metadata)
                broken["streams"][0][field] = bad_value
                errors = stream_validation_errors(broken, PROFILES["hevc10"], width=64, height=36, fps=60, frames=8, wanted_audio=False)
                self.assertTrue(any(field in message for message in errors), errors)
        errors = stream_validation_errors(metadata, PROFILES["hevc10"], width=64, height=36, fps=60, frames=8, wanted_audio=True)
        self.assertTrue(any("audio stream" in message for message in errors))

    def test_known_srgb_patch_converts_to_display_referred_rec709(self):
        source, output = self.root / "gray.png", self.root / "gray.mp4"
        write_png16(source, 64, 36, gray=32768)
        result = subprocess.run(["ffmpeg", "-v", "error", "-y", "-filter_threads", "1", "-i", str(source), "-frames:v", "1", *video_encoding_args(60, PROFILES["h264"]), "-an", str(output)], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(output), "-frames:v", "1", "-pix_fmt", "yuv420p", "-f", "rawvideo", "-"], timeout=30)
        srgb = 32768 / 65535
        linear_light = ((srgb + 0.055) / 1.055) ** 2.4
        # zimg's display-referred BT.709 uses the BT.1886 display EOTF,
        # not the scene-referred camera OETF. This should be about Y=131.
        expected_luma = 16 + 219 * linear_light ** (1 / 2.4)
        self.assertAlmostEqual(sum(raw[:64 * 36]) / (64 * 36), expected_luma, delta=1.5)

    def test_high_bit_profile_checks_every_source_frame(self):
        from PIL import Image
        path = self.project.output("final") / "shots/b/frames/frame_000007.png"
        Image.new("RGB", (64, 36), "gold").save(path)
        with self.assertRaisesRegex(PipelineError, "frame 7.*8-bit"):
            validate_source_frames(self.project, "final", PROFILES["hevc10"])
        self.assertEqual(validate_source_frames(self.project, "final", PROFILES["h264"])["png_bit_depths"], [8, 16])

    def test_no_high_bit_claim_through_browser_compositing(self):
        with self.assertRaisesRegex(PipelineError, "8-bit H.264"):
            assemble(self.project, "final", editor="remotion", profile="hevc10")

    def test_profile_precedence_keeps_drafts_compatible(self):
        self.project.data["delivery"] = {"profile": "hevc10", "profiles_by_quality": {"review": "prores422hq"}}
        self.assertEqual(resolve_profile(self.project, "draft").name, "h264")
        self.assertEqual(resolve_profile(self.project, "final").name, "hevc10")
        self.assertEqual(resolve_profile(self.project, "review").name, "prores422hq")
        self.assertEqual(resolve_profile(self.project, "final", "h264").name, "h264")

    def test_receipt_cannot_redirect_to_another_file(self):
        directory = self.project.output("final")
        (directory / "master.json").write_text(json.dumps({"filename": "../private.mp4"}))
        with self.assertRaisesRegex(PipelineError, "unsupported filename"):
            current_master_path(self.project, "final")

    def test_changed_finisher_fails_real_master_qa_and_legacy_receipt_stays_compatible(self):
        finisher = self.root / "pipeline/delivery.py"
        finisher.parent.mkdir()
        finisher.write_text("# Finisher version one.\n")
        with patch("pipeline.media.verify_complete", return_value=self.receipts):
            master = assemble(self.project, "final", profile="h264")
            receipt_path = master.parent / "master.json"
            receipt = json.loads(receipt_path.read_text())
            self.assertEqual(receipt["finishing_inputs"]["pipeline/delivery.py"], file_hash(finisher))
            finisher.write_text("# Finisher version two.\n")
            report = qa(self.project, "final")
            self.assertFalse(report["technical_passed"])
            self.assertTrue(any("Finishing inputs changed" in error for error in report["errors"]))
            del receipt["finishing_inputs"]
            write_json(receipt_path, receipt)
            legacy_report = qa(self.project, "final")
            self.assertTrue(legacy_report["technical_passed"], legacy_report["errors"])

    def test_remotion_finishing_hashes_include_editor_and_shared_code(self):
        for name in ("apps/editor/delivery.mjs", "apps/shared/motion.ts", "apps/editor/node_modules/ignored.mjs"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("export const revision = 1;\n")
        inputs = finishing_input_hashes(self.root, "remotion")
        self.assertIn("apps/editor/delivery.mjs", inputs)
        self.assertIn("apps/shared/motion.ts", inputs)
        self.assertNotIn("apps/editor/node_modules/ignored.mjs", inputs)
        self.assertNotIn("apps/editor/delivery.mjs", finishing_input_hashes(self.root, "ffmpeg"))

    def test_failed_real_master_validation_preserves_master_receipt_and_approval(self):
        with patch("pipeline.media.verify_complete", return_value=self.receipts):
            master = assemble(self.project, "final", profile="h264")
            master_bytes = master.read_bytes()
            receipt_path = master.parent / "master.json"
            receipt_bytes = receipt_path.read_bytes()
            approval_path = master.parent / "approval.json"
            write_json(approval_path, {"confirmed_viewed": True, "master_sha256": file_hash(master), "project_identity": self.project.identity()})
            approval_bytes = approval_path.read_bytes()
            # Perform a real second encode with an intentionally wrong clock.
            # Validation must reject its bytes before replacing the active master.
            with patch("pipeline.media.video_encoding_args", side_effect=lambda fps, profile: video_encoding_args(30, profile)):
                with self.assertRaisesRegex(PipelineError, "previous master is preserved"):
                    assemble(self.project, "final", profile="h264")
            self.assertEqual(master.read_bytes(), master_bytes)
            self.assertEqual(receipt_path.read_bytes(), receipt_bytes)
            self.assertEqual(approval_path.read_bytes(), approval_bytes)


if __name__ == "__main__":
    unittest.main()
