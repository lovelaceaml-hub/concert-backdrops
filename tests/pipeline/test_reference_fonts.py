"""Real WOFF2 conversion and fail-closed historical TTF reconstruction."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from tools import setup_fonts


ROOT = Path(__file__).resolve().parents[2]


class ReferenceFontTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "sources"
        self.woff = self.source / "fixture/files/fixture-latin-400-normal.woff2"
        self.woff.parent.mkdir(parents=True)
        builder = FontBuilder(1024, isTTF=True)
        builder.setupGlyphOrder([".notdef", "A"])
        builder.setupCharacterMap({65: "A"})
        glyphs = {}
        for name in (".notdef", "A"):
            pen = TTGlyphPen(None)
            if name == "A":
                pen.moveTo((50, 0))
                pen.lineTo((300, 700))
                pen.lineTo((550, 0))
                pen.closePath()
            glyphs[name] = pen.glyph()
        builder.setupGlyf(glyphs)
        builder.setupHorizontalMetrics({name: (600, 0) for name in glyphs})
        builder.setupHorizontalHeader(ascent=800, descent=-200)
        builder.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
        builder.setupNameTable({"familyName": "Original Test Fixture", "styleName": "Regular",
                               "uniqueFontIdentifier": "OriginalTestFixture", "fullName": "Original Test Fixture",
                               "psName": "OriginalTestFixture-Regular"})
        builder.setupPost()
        builder.setupMaxp()
        builder.font.recalcTimestamp = False
        builder.font["head"].created = 3700000000
        builder.font["head"].modified = 3700000100
        builder.font.flavor = "woff2"
        builder.font.save(self.woff)
        self.historical = self.root / "historical.ttf"
        with TTFont(self.woff, recalcTimestamp=False) as font:
            font.flavor = None
            font["head"].created = 3700000123
            font["head"].modified = 3900000000
            font.save(self.historical)
        self.name = "fixture-latin-400-normal.ttf"
        self.definition = {"schema_version": 1, "id": "synthetic-test-fixture", "expected_font_count": 1,
                           "fonts": [{"filename": self.name, "source_woff2": str(self.woff.relative_to(self.source)),
                                      "source_sha256": setup_fonts.file_hash(self.woff),
                                      "head": {"created": 3700000123, "modified": 3900000000},
                                      "ttf_sha256": setup_fonts.file_hash(self.historical)}]}
        self.definition["historical_font_mapping_sha256"] = setup_fonts.mapping_hash(
            {"fonts/" + self.name: setup_fonts.file_hash(self.historical)})
        self.catalog = self.root / "catalog.json"
        self.write_catalog()
        self.destination = self.root / "destination"

    def write_catalog(self):
        self.catalog.write_text(json.dumps(self.definition))

    def existing_destination(self):
        self.destination.mkdir()
        existing = self.destination / self.name
        existing.write_bytes(b"Existing output must survive failed validation")
        return existing, (existing.read_bytes(), existing.stat().st_mtime_ns)

    def test_real_conversion_reconstructs_exact_historical_bytes(self):
        result = setup_fonts.convert_fonts(self.source, self.destination, self.catalog)
        self.assertEqual(result["written"], 1)
        self.assertEqual((self.destination / self.name).read_bytes(), self.historical.read_bytes())
        with TTFont(self.destination / self.name, recalcTimestamp=False) as font:
            self.assertEqual((font["head"].created, font["head"].modified), (3700000123, 3900000000))

    def test_source_tamper_fails_before_existing_output_changes(self):
        existing, before = self.existing_destination()
        self.woff.write_bytes(self.woff.read_bytes() + b"changed")
        with self.assertRaisesRegex(setup_fonts.FontSetupError, "source checksum mismatch"):
            setup_fonts.convert_fonts(self.source, self.destination, self.catalog)
        self.assertEqual((existing.read_bytes(), existing.stat().st_mtime_ns), before)

    def test_timestamp_tamper_fails_before_existing_output_changes(self):
        existing, before = self.existing_destination()
        self.definition["fonts"][0]["head"]["modified"] += 1
        self.write_catalog()
        with self.assertRaisesRegex(setup_fonts.FontSetupError, "Reconstructed reference TTF checksum mismatch"):
            setup_fonts.convert_fonts(self.source, self.destination, self.catalog)
        self.assertEqual((existing.read_bytes(), existing.stat().st_mtime_ns), before)

    def test_output_checksum_tamper_rejected_by_mapping_identity(self):
        self.definition["fonts"][0]["ttf_sha256"] = "0" * 64
        self.write_catalog()
        with self.assertRaisesRegex(setup_fonts.FontSetupError, "output mapping checksum"):
            setup_fonts.convert_fonts(self.source, self.destination, self.catalog)
        self.assertFalse(self.destination.exists())

    def test_matching_reference_font_is_not_rewritten(self):
        setup_fonts.convert_fonts(self.source, self.destination, self.catalog)
        output = self.destination / self.name
        os.utime(output, ns=(1234567890000000000, 1234567890000000000))
        before = (output.read_bytes(), output.stat().st_mtime_ns)
        result = setup_fonts.convert_fonts(self.source, self.destination, self.catalog)
        self.assertEqual((result["written"], result["unchanged"]), (0, 1))
        self.assertEqual((output.read_bytes(), output.stat().st_mtime_ns), before)

    def test_extra_destination_font_is_preserved_and_reported(self):
        self.destination.mkdir()
        extra = self.destination / "unrelated.ttf"
        extra.write_bytes(b"preserve")
        with self.assertRaisesRegex(setup_fonts.FontSetupError, "Unexpected fonts"):
            setup_fonts.convert_fonts(self.source, self.destination, self.catalog)
        self.assertEqual(extra.read_bytes(), b"preserve")
        self.assertFalse((self.destination / self.name).exists())

    def test_default_conversion_remains_deterministic_and_preserves_source_timestamps(self):
        hashes = []
        for number, now in enumerate((3900000000, 3900000900)):
            destination = self.root / f"default-{number}"
            with patch("fontTools.ttLib.tables._h_e_a_d.timestampNow", return_value=now):
                result = setup_fonts.convert_fonts(self.source, destination)
            self.assertEqual(result["mode"], "source")
            hashes.append(setup_fonts.file_hash(destination / self.name))
            with TTFont(destination / self.name, recalcTimestamp=False) as font:
                self.assertEqual((font["head"].created, font["head"].modified), (3700000000, 3700000100))
        self.assertEqual(hashes[0], hashes[1])
        self.assertNotEqual(hashes[0], setup_fonts.file_hash(self.historical))


class BootstrapReferenceFontTests(unittest.TestCase):
    def test_reference_mode_is_forwarded_without_enabling_optional_render_backends(self):
        spec = importlib.util.spec_from_file_location("reference_font_bootstrap", ROOT / "scripts/bootstrap.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.object(module, "run") as run, patch.object(module.shutil, "which", return_value="/present/tool"), patch.object(
                module.sys, "argv", ["bootstrap.py", "--p3d-only", "--reference-fonts"]):
            module.main()
        commands = [call.args for call in run.call_args_list]
        font_command = next(command for command in commands if "tools/setup_fonts.py" in command)
        self.assertEqual(font_command[-1], "--reference-fonts")
        self.assertFalse(any("scripts/install-blender.py" in command or "playwright" in command for command in commands))
        self.assertEqual(commands[-1][-3:], ("doctor", "--backend", "p3d"))


if __name__ == "__main__":
    unittest.main()
