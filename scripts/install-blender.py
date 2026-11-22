#!/usr/bin/env python3
"""Install the pinned official CPU-capable Blender under .tools, without sudo."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check the installed version without downloading")
    args = parser.parse_args()
    spec = json.loads((ROOT / "infra/toolchain.lock.json").read_text())["blender"]
    target = ROOT / ".tools" / spec["archive"].removesuffix(".tar.xz")
    executable = target / "blender"
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "amd64"):
        raise SystemExit("This installer targets Linux x64 cloud workers. On another platform set BLENDER_BIN to an existing Blender; this installer does not change your Mac.")
    if executable.exists():
        version = subprocess.check_output([str(executable), "--version"], text=True).splitlines()[0]
        if version.split()[1] != spec["version"]:
            raise SystemExit(f"Version mismatch: {version}")
        print(str(executable))
        return
    if args.check:
        raise SystemExit("Pinned Blender is not installed. Run python3 scripts/install-blender.py")
    downloads = ROOT / ".tools/blender-download"
    downloads.mkdir(parents=True, exist_ok=True)
    archive = downloads / spec["archive"]
    if not archive.exists():
        partial = archive.with_suffix(archive.suffix + ".partial")
        print(f"Downloading Blender {spec['version']} into the project", flush=True)
        try:
            with urllib.request.urlopen(spec["url"], timeout=120) as response, partial.open("wb") as stream:
                shutil.copyfileobj(response, stream, 1024 * 1024)
            os.replace(partial, archive)
        finally:
            partial.unlink(missing_ok=True)
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != spec["sha256"]:
        raise SystemExit("Blender archive checksum does not match the pinned official checksum. No archive was extracted.")
    print("Archive SHA-256 verified; extracting", flush=True)
    with tarfile.open(archive) as bundle:
        bundle.extractall(ROOT / ".tools", filter="data")
    version = subprocess.check_output([str(executable), "--version"], text=True).splitlines()[0]
    if version.split()[1] != spec["version"]:
        raise SystemExit(f"Installed version mismatch: {version}")
    print(str(executable))


if __name__ == "__main__":
    main()
