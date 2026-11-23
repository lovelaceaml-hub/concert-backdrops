"""Restore public pinned assets and exact private-recording-derived analysis only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

from . import common as c


def restore_engines():
    for destination, commit in c.PINS.items():
        target = c.ROOT / destination
        if not (target / "engine/render.py").is_file():
            target.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="s11-pinned-") as temporary:
                archive = Path(temporary) / "source.tar"
                subprocess.run(["git", "archive", "--format=tar", "--output=" + str(archive),
                                commit, "engine", "assets"], cwd=c.ROOT, check=True)
                with tarfile.open(archive) as stream:
                    stream.extractall(target, filter="data")
        fonts = target / "fonts"
        if not fonts.exists() and not fonts.is_symlink():
            fonts.symlink_to(c.ROOT / "fonts", target_is_directory=True)


def restore_fonts():
    from tools.setup_fonts import convert_reference
    catalog = c.ROOT / "project-docs/production-system/catalogs/study-fonts.json"
    definition = json.loads(catalog.read_text())
    with tempfile.TemporaryDirectory(prefix="s11-fonts-") as temporary:
        source = Path(temporary)
        for name, version in definition["source_packages"].items():
            result = subprocess.run(["npm", "pack", "--json", "@fontsource/" + name + "@" + version],
                                    cwd=source, check=True, capture_output=True, text=True)
            archive = source / json.loads(result.stdout)[0]["filename"]
            stage = source / (name + "-extract")
            stage.mkdir()
            with tarfile.open(archive) as stream:
                stream.extractall(stage, filter="data")
            (stage / "package").rename(source / name)
            stage.rmdir()
        receipt = convert_reference(source, c.ROOT / "fonts", catalog)
    c.write_json(c.ROOT / "work/s11_cloud/font-reconstruction.json", receipt)


def restore_analysis():
    definition = c.manifest()
    destination = c.ROOT / "work/s11_full2"
    destination.mkdir(parents=True, exist_ok=True)
    for name, expected in definition["analysis"].items():
        data = (c.INPUTS / name).read_bytes()
        if len(data) != expected["bytes"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise ValueError("Analysis input does not match its checked source: " + name)
        target = destination / name
        if target.exists() and c.digest(target) != expected["sha256"]:
            raise ValueError("Refusing to replace different prepared analysis: " + name)
        if not target.exists():
            target.write_bytes(data)
    provenance = c.INPUTS / "provenance.json"
    target = destination / "provenance.json"
    if target.exists() and c.digest(target) != c.digest(provenance):
        raise ValueError("Refusing to replace different source provenance.")
    if not target.exists():
        shutil.copyfile(provenance, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", action="store_true", help="Recover exact fonts from pinned public Fontsource packages.")
    args = parser.parse_args()
    c.request()
    restore_engines()
    if args.fonts:
        restore_fonts()
    restore_analysis()
    c.validate_picture_analysis()
    sources = c.validate_picture_sources()
    print(json.dumps(dict(event="picture_inputs_ready", verified_sources=len(sources),
                          original_recording_uploaded=False, waveform_required=False)))


if __name__ == "__main__":
    main()
