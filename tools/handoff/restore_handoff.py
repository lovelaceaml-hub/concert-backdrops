#!/usr/bin/env python3
"""Restore exact files split for the Drive connection's per-file transfer limit.

Python 3 standard library only. No network, rendering, transcoding or deletion.
Existing matching outputs are retained; any nonmatching output is refused.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


def basename(value):
    if not isinstance(value, str) or not value or value in {".", ".."}:
        raise ValueError("Invalid file name")
    if Path(value).name != value or "/" in value or "\\" in value:
        raise ValueError("Manifest file names must be basenames")
    return value


def identity(path):
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            count += len(block)
            digest.update(block)
    return count, digest.hexdigest()


def expected(entry):
    size = entry["bytes"]
    sha = entry["sha256"]
    if not isinstance(size, int) or size < 0 or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ValueError("Invalid expected size or SHA-256")
    return size, sha


def restore(entry, source, destination):
    name = basename(entry["file_name"])
    target = destination / name
    wanted = expected(entry)
    if target.exists() or target.is_symlink():
        if target.is_symlink() or not target.is_file() or identity(target) != wanted:
            raise FileExistsError(f"Refusing to replace existing output: {target}")
        print(f"Already verified: {name}", flush=True)
        return
    parts = entry["parts"]
    if not parts or len({p["file_name"] for p in parts}) != len(parts):
        raise ValueError(f"Missing or repeated parts: {name}")
    if sum(expected(p)[0] for p in parts) != wanted[0]:
        raise ValueError(f"Part sizes do not sum to original size: {name}")
    # Verify every input before creating the full output.
    for part in parts:
        part_path = source / basename(part["file_name"])
        if part_path.is_symlink() or identity(part_path) != expected(part):
            raise ValueError(f"Part checksum mismatch: {part_path}")
    destination.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".restoring-", dir=destination)
    temporary = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as output:
            for part in parts:
                with (source / part["file_name"]).open("rb") as stream:
                    for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                        output.write(block)
            output.flush()
            os.fsync(output.fileno())
        if identity(temporary) != wanted:
            raise ValueError(f"Restored original checksum mismatch: {name}")
        # Hard-link installation is atomic and refuses an output created meanwhile.
        os.link(temporary, target)
        print(f"Restored and verified: {name} ({wanted[0]:,} bytes)", flush=True)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("TRANSFER-MANIFEST.json"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--only", help="Restore only this exact original filename")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "concert-drive-exact-parts-v1":
        raise ValueError("Unsupported manifest schema")
    entries = manifest["files"]
    names = [basename(e["file_name"]) for e in entries]
    if len(names) != len(set(names)):
        raise ValueError("Repeated original filenames")
    if args.only:
        entries = [e for e in entries if e["file_name"] == args.only]
        if not entries:
            raise ValueError("Requested original is not in this manifest")
    source = args.manifest.resolve().parent
    destination = args.output_dir.resolve() if args.output_dir else source
    for entry in entries:
        restore(entry, source, destination)


if __name__ == "__main__":
    main()
