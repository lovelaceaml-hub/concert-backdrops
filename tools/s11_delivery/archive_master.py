#!/usr/bin/env python3
"""Preserve an exact master in ordinary ZIPs and verify a complete restoration.

Uses only Python's standard library. No video decoding or re-encoding occurs.
Each archive includes one consecutive binary chunk, a shared manifest and hash,
human instructions, and a standalone restore script that reads the ZIPs directly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

BLOCK_BYTES = 8 * 1024 * 1024
MANIFEST_NAME = "master-manifest.json"
RECEIPT_NAME = "master-archive-receipt.json"

RESTORE_BODY = r'''
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

BLOCK_BYTES = 8 * 1024 * 1024

def restore(archive_dir, output):
    archive_dir = Path(archive_dir).resolve()
    with zipfile.ZipFile(archive_dir / FIRST_ARCHIVE) as first:
        manifest_bytes = first.read("master-manifest.json")
    if hashlib.sha256(manifest_bytes).hexdigest() != EXPECTED_MANIFEST_SHA256:
        raise ValueError("Manifest hash does not match this restore script")
    manifest = json.loads(manifest_bytes)
    output = Path(output or manifest["master"]["filename"]).resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite: {output}")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    position = 0
    for chunk in manifest["chunks"]:
        if chunk["offset"] != position or chunk["bytes"] <= 0:
            raise ValueError("Invalid or nonconsecutive chunk range")
        position += chunk["bytes"]
        path = archive_dir / chunk["archive"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing archive: {path}")
        with zipfile.ZipFile(path) as archive:
            if archive.read("master-manifest.json") != manifest_bytes:
                raise ValueError(f"Mismatched manifest in {path.name}")
            info = archive.getinfo(chunk["member"])
            if info.file_size != chunk["bytes"]:
                raise ValueError(f"Wrong chunk size in {path.name}")
    if position != manifest["master"]["bytes"]:
        raise ValueError("Chunk ranges do not cover the complete master")
    owns_output = False
    complete = False
    try:
        total = 0
        master_hash = hashlib.sha256()
        with output.open("xb") as restored:
            owns_output = True
            for chunk in manifest["chunks"]:
                chunk_hash = hashlib.sha256()
                count = 0
                with zipfile.ZipFile(archive_dir / chunk["archive"]) as archive:
                    with archive.open(chunk["member"]) as source:
                        while data := source.read(BLOCK_BYTES):
                            restored.write(data)
                            chunk_hash.update(data)
                            master_hash.update(data)
                            count += len(data)
                if count != chunk["bytes"] or chunk_hash.hexdigest() != chunk["sha256"]:
                    raise ValueError(f"Chunk verification failed: {chunk['archive']}")
                total += count
        if total != manifest["master"]["bytes"] or master_hash.hexdigest() != manifest["master"]["sha256"]:
            raise ValueError("Complete restored master verification failed")
        complete = True
        result = {"output": str(output), "bytes": total, "sha256": master_hash.hexdigest(), "verified": True}
        print(json.dumps(result, indent=2))
        return result
    finally:
        if owns_output and not complete:
            output.unlink(missing_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore and verify the exact original MP4 from its ordinary ZIP archives.")
    parser.add_argument("--archive-dir", default=".", help="Folder containing every archive in this set")
    parser.add_argument("--output", help="New MP4 path; defaults to the original filename in the current folder")
    args = parser.parse_args()
    restore(args.archive_dir, args.output)
'''


def file_hash(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        while data := source.read(BLOCK_BYTES):
            result.update(data)
    return result.hexdigest()


def zip_entry(name: str, size: int = 0) -> zipfile.ZipInfo:
    """Stable metadata makes repeated packaging of the same input reproducible."""
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.file_size = size
    return info


def create_archive_set(args: argparse.Namespace) -> dict:
    master = Path(args.master).resolve()
    output_dir = Path(args.output_dir).resolve()
    size = master.stat().st_size
    if size <= 0:
        raise ValueError("The master must be nonempty")
    if args.expect_size is not None and size != args.expect_size:
        raise ValueError(f"Unexpected source size: {size}")
    if not 0 < args.chunk_bytes < args.archive_limit_bytes - 65536:
        raise ValueError("Chunk size must leave at least 65536 bytes for archive metadata")
    prefix = args.archive_prefix or master.stem
    if prefix in ("", ".", "..") or "/" in prefix or "\\" in prefix:
        raise ValueError("Archive prefix must be a plain filename prefix")
    count = (size + args.chunk_bytes - 1) // args.chunk_bytes
    chunks = []
    master_hash = hashlib.sha256()
    with master.open("rb") as source:
        offset = 0
        for index in range(count):
            length = min(args.chunk_bytes, size - offset)
            remaining = length
            chunk_hash = hashlib.sha256()
            while remaining:
                data = source.read(min(BLOCK_BYTES, remaining))
                if not data:
                    raise ValueError("Source became shorter during hashing")
                master_hash.update(data)
                chunk_hash.update(data)
                remaining -= len(data)
            chunks.append({"index": index + 1, "offset": offset, "bytes": length,
                           "sha256": chunk_hash.hexdigest(),
                           "archive": f"{prefix}_Part_{index + 1:02d}_of_{count:02d}.zip",
                           "member": f"chunks/part-{index + 1:03d}-of-{count:03d}.bin"})
            offset += length
        if source.read(1):
            raise ValueError("Source became longer during hashing")
    digest = master_hash.hexdigest()
    if args.expect_sha256 is not None and digest != args.expect_sha256.lower():
        raise ValueError(f"Unexpected source SHA-256: {digest}")
    manifest = {"schema": "exact-master-zip-chunks-v1", "compression": "ZIP_STORED",
                "master": {"filename": master.name, "bytes": size, "sha256": digest},
                "chunk_count": count, "chunk_size_limit_bytes": args.chunk_bytes,
                "archive_size_limit_bytes": args.archive_limit_bytes, "chunks": chunks}
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    restore_script = ("#!/usr/bin/env python3\n"
                      f"FIRST_ARCHIVE = {chunks[0]['archive']!r}\n"
                      f"EXPECTED_MANIFEST_SHA256 = {manifest_hash!r}\n" + RESTORE_BODY).encode()
    readme = ("EXACT ORIGINAL MASTER — RESTORATION\n\n"
              "These ordinary ZIP files preserve consecutive binary chunks of the original MP4.\n"
              "No picture or audio was re-encoded. You need every ZIP in this set.\n\n"
              "1. Put all of the following ZIP files together in one folder:\n" +
              "".join(f"   {c['archive']}\n" for c in chunks) +
              "2. Open either ZIP and extract only restore_master.py into that folder.\n"
              "   Leave the ZIP files intact; do not concatenate the ZIP files themselves.\n"
              "3. Open a terminal in that folder and run:\n"
              "   python3 restore_master.py --archive-dir .\n"
              "   On Windows, use python instead of python3 if that is your installed command.\n"
              "   Python 3.8 or newer is sufficient; no additional packages are required.\n"
              "   Use --output /path/to/new-file.mp4 to choose another destination.\n"
              "4. The script checks every chunk and the complete restored MP4. It removes its\n"
              "   own incomplete output if verification fails and refuses to overwrite existing\n"
              "   files. Wait for the final verified result. Keep enough free space for\n"
              f"   the restored {size:,}-byte MP4 in addition to the ZIP files.\n\n"
              f"Restored filename: {master.name}\n"
              f"Exact restored bytes: {size}\n"
              f"Exact restored SHA-256: {digest}\n"
              f"Manifest SHA-256: {manifest_hash}\n\n"
              "The archive payloads are binary fragments and become a playable MP4 only after\n"
              "restoration. master-manifest.json records the byte order, ranges, and hashes.\n").encode()
    output_dir.mkdir(parents=True, exist_ok=True)
    destinations = [output_dir / c["archive"] for c in chunks]
    receipt_path = output_dir / RECEIPT_NAME
    for path in [*destinations, receipt_path]:
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite: {path}")
    archives = []
    with master.open("rb") as source:
        for chunk, path in zip(chunks, destinations):
            with path.open("xb") as archive_file:
                with zipfile.ZipFile(archive_file, "w", compression=zipfile.ZIP_STORED) as archive:
                    archive.writestr(zip_entry(MANIFEST_NAME), manifest_bytes)
                    archive.writestr(zip_entry("master-manifest.sha256"), f"{manifest_hash}  {MANIFEST_NAME}\n")
                    archive.writestr(zip_entry("restore_master.py"), restore_script)
                    archive.writestr(zip_entry("README_RESTORE.txt"), readme)
                    with archive.open(zip_entry(chunk["member"], chunk["bytes"]), "w") as payload:
                        remaining = chunk["bytes"]
                        while remaining:
                            data = source.read(min(BLOCK_BYTES, remaining))
                            if not data:
                                raise ValueError("Source became shorter during packaging")
                            payload.write(data)
                            remaining -= len(data)
            archive_size = path.stat().st_size
            if archive_size >= args.archive_limit_bytes:
                raise ValueError(f"Archive exceeds the requested size limit: {path}")
            archives.append({"path": str(path), "bytes": archive_size, "sha256": file_hash(path),
                             "chunk_index": chunk["index"]})
    # Execute the actual embedded script, then independently hash its completed file.
    # TemporaryDirectory owns only this verification workspace and removes it afterward.
    with tempfile.TemporaryDirectory(prefix=".restore-check-", dir=output_dir) as check_dir:
        restored = Path(check_dir) / master.name
        result = subprocess.run([sys.executable, "-c", restore_script.decode(), "--archive-dir",
                                 str(output_dir), "--output", str(restored)],
                                check=True, capture_output=True, text=True)
        restored_result = json.loads(result.stdout)
        verified_size = restored.stat().st_size
        verified_hash = file_hash(restored)
        if verified_size != size or verified_hash != digest or not restored_result["verified"]:
            raise ValueError("Independent restored-file verification failed")
    receipt = {"schema": "exact-master-zip-archive-receipt-v1", "source_path": str(master),
               "master": manifest["master"], "manifest_sha256": manifest_hash,
               "embedded_restore_script_sha256": hashlib.sha256(restore_script).hexdigest(),
               "tool_sha256": file_hash(Path(__file__)), "archives": archives,
               "reassembly_verification": {"passed": True, "bytes": verified_size,
                   "sha256": verified_hash, "method": "Executed the embedded restore CLI against all ZIPs; independently read and hashed its complete restored MP4.",
                   "temporary_verification_output_removed": True},
               "no_video_or_audio_reencoding": True}
    with receipt_path.open("x") as destination:
        json.dump(receipt, destination, indent=2)
        destination.write("\n")
    return {**receipt, "receipt_path": str(receipt_path), "receipt_sha256": file_hash(receipt_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master", help="Exact original master file to preserve")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--archive-prefix", help="Plain filename prefix for the ZIP archives")
    parser.add_argument("--chunk-bytes", type=int, default=480_000_000)
    parser.add_argument("--archive-limit-bytes", type=int, default=500_000_000)
    parser.add_argument("--expect-sha256", help="Reject any master with a different SHA-256")
    parser.add_argument("--expect-size", type=int, help="Reject any master with a different byte size")
    print(json.dumps(create_archive_set(parser.parse_args()), indent=2))


if __name__ == "__main__":
    main()
