"""Convert pinned Fontsource WOFF2 files, optionally reproducing study TTF bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_CATALOG = ROOT / "project-docs/production-system/catalogs/study-fonts.json"


class FontSetupError(ValueError):
    """A source or reconstructed font differs from the declared reference."""


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mapping_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_files(source: Path) -> list[Path]:
    return sorted(source.glob("**/files/*-latin-*.woff2"))


def checked_relative(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise FontSetupError("Reference font paths must be repository-relative names.")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise FontSetupError(f"Reference font path escapes its source directory: {name}")
    return path


def reference_definition(path: Path) -> dict:
    definition = json.loads(path.read_text())
    if not isinstance(definition, dict) or definition.get("schema_version") != 1:
        raise FontSetupError("Unsupported reference font catalog schema.")
    records = definition.get("fonts")
    count = definition.get("expected_font_count")
    if type(count) is not int or count < 1 or not isinstance(records, list) or len(records) != count:
        raise FontSetupError("Reference font catalog count does not match its records.")
    names, sources = set(), set()
    for record in records:
        if not isinstance(record, dict):
            raise FontSetupError("Reference font records must be objects.")
        name, source = record.get("filename"), record.get("source_woff2")
        if not isinstance(name, str) or Path(name).name != name or not name.endswith(".ttf") or name in names:
            raise FontSetupError("Reference font output filenames must be unique TTF basenames.")
        if not isinstance(source, str) or source in sources:
            raise FontSetupError("Reference WOFF2 paths must be unique.")
        for field in ("source_sha256", "ttf_sha256"):
            if not isinstance(record.get(field), str) or not re.fullmatch(r"[0-9a-f]{64}", record[field]):
                raise FontSetupError(f"Invalid {field} for {name}.")
        head = record.get("head", {})
        if not isinstance(head, dict) or set(head) != {"created", "modified"} or any(
                type(value) is not int or not 0 <= value < 2**64 for value in head.values()):
            raise FontSetupError(f"Reference head timestamps must be unsigned integers for {name}.")
        names.add(name)
        sources.add(source)
    expected_mapping = {"fonts/" + record["filename"]: record["ttf_sha256"] for record in records}
    if mapping_hash(expected_mapping) != definition.get("historical_font_mapping_sha256"):
        raise FontSetupError("Reference font output mapping checksum differs from its records.")
    return definition


def convert_reference(source: Path, destination: Path, catalog: Path) -> dict:
    """Verify every staged output before publishing any reference font."""
    definition = reference_definition(catalog)
    records = definition["fonts"]
    discovered = {str(path.relative_to(source)) for path in source_files(source)}
    declared = {record["source_woff2"] for record in records}
    if discovered != declared:
        raise FontSetupError("Reference WOFF2 file set does not match the catalog; restore the pinned npm packages.")
    expected_names = {record["filename"] for record in records}
    extra_outputs = {path.name for path in destination.glob("*.ttf")} - expected_names
    if extra_outputs:
        raise FontSetupError("Unexpected fonts in reference destination; preserve them and select a clean directory: " + ", ".join(sorted(extra_outputs)))
    sources = {}
    for record in records:
        path = checked_relative(source, record["source_woff2"])
        if not path.is_file() or file_hash(path) != record["source_sha256"]:
            raise FontSetupError(f"Reference WOFF2 source checksum mismatch: {record['source_woff2']}")
        sources[record["filename"]] = path
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="concert-reference-fonts-", dir=destination.parent) as directory:
        staged = Path(directory)
        for record in records:
            output = staged / record["filename"]
            with TTFont(sources[record["filename"]], recalcTimestamp=False) as font:
                font.flavor = None
                font["head"].created = record["head"]["created"]
                font["head"].modified = record["head"]["modified"]
                font.save(output)
            if file_hash(output) != record["ttf_sha256"]:
                raise FontSetupError(f"Reconstructed reference TTF checksum mismatch: {record['filename']}; check catalog metadata and the locked converter runtime.")
        for record in records:
            if file_hash(sources[record["filename"]]) != record["source_sha256"]:
                raise FontSetupError(f"WOFF2 source changed during reconstruction: {record['source_woff2']}")
        destination.mkdir(parents=True, exist_ok=True)
        written, unchanged = 0, 0
        for record in records:
            output = destination / record["filename"]
            if output.is_file() and file_hash(output) == record["ttf_sha256"]:
                unchanged += 1
                continue
            (staged / record["filename"]).replace(output)
            written += 1
        for record in records:
            if file_hash(destination / record["filename"]) != record["ttf_sha256"]:
                raise FontSetupError(f"Installed reference TTF checksum mismatch: {record['filename']}")
    return {"mode": "reference", "count": len(records), "written": written, "unchanged": unchanged,
            "font_mapping_sha256": definition["historical_font_mapping_sha256"]}


def convert_fonts(source: Path, destination: Path, reference: Path | None = None) -> dict:
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if reference is not None:
        return convert_reference(source, destination, Path(reference))
    destination.mkdir(parents=True, exist_ok=True)
    fonts = source_files(source)
    for path in fonts:
        # Normal conversion retains the source timestamps and remains deterministic.
        with TTFont(path, recalcTimestamp=False) as font:
            font.flavor = None
            font.save(destination / (path.name[:-6] + ".ttf"))
    return {"mode": "source", "count": len(fonts)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--reference-fonts", nargs="?", const=REFERENCE_CATALOG, type=Path,
                        help="Reconstruct exact historical study TTFs using the checked-in catalog, or an explicit catalog path.")
    args = parser.parse_args()
    try:
        result = convert_fonts(args.source, args.destination, args.reference_fonts)
    except (FontSetupError, OSError, ValueError) as exc:
        parser.exit(1, f"Font setup failed: {exc}\n")
    print("fonts converted:", result["count"])
    if result["mode"] == "reference":
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
