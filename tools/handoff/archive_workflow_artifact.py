#!/usr/bin/env python3
"""Archive one pinned GitHub proof ZIP to one existing project Drive folder.

No rendering, ZIP extraction, overwriting, deletion or permission changes.
Only the workflow's GitHub token and existing Drive OAuth authentication are used.
Run through archive-handoff-proof.yml; all transfer identities are fixed below.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = "lovelaceaml-hub/concert-backdrops"
SOURCE_RUN_ID = 45125796332
ARTIFACT_ID = 14795673158
ARTIFACT_NAME = "tool-proofs"
EXPECTED_BYTES = 637361486
EXPECTED_SHA256 = "66099a7e4613a22d397abe74826f0b30246b5235161756157ec8d84bfee0dd8c"
EXPECTED_PROVIDER_DIGEST = "sha256:" + EXPECTED_SHA256
PROJECT_ROOT_ID = "1xyNZn4ZA6bjPcvKjGfgSWQIs9aAp2PPd"
DESTINATION_ID = "1dNAkcUesWv5RcKJ48s_W7mpDW757b0At"
DESTINATION_NAME = "Cloud_Tool_Proofs_PR116_2026-11-22.zip"
PUSH_REF = "refs/heads/maintenance/claude-handoff-20261122"
WORK = ROOT / "work/handoff-proof-archive"
RECEIPT_PATH = WORK / "receipt.json"
CHUNK_BYTES = 32 * 1024 * 1024
FILE_FIELDS = "id,name,mimeType,size,parents,modifiedTime,version,trashed,webViewLink"
FOLDER_MIME = "application/vnd.google-apps.folder"


class TransferError(Exception):
    """Messages here are deliberately safe to include in a public job log."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_receipt(receipt: dict) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    temp = WORK / "receipt.json.tmp"
    temp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    temp.replace(RECEIPT_PATH)


def stage(receipt: dict, value: str) -> None:
    receipt["stage"] = value
    save_receipt(receipt)
    print(value, flush=True)


def require_cloud_context() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise TransferError("Run this fixed transfer in the authorized repository's GitHub Actions workflow.")
    event = os.environ.get("GITHUB_EVENT_NAME")
    if event != "workflow_dispatch" and not (event == "push" and os.environ.get("GITHUB_REF") == PUSH_REF):
        raise TransferError("Only manual dispatch or the scoped maintenance-branch push is allowed.")
    for name in ("GH_TOKEN", "GOOGLE_DRIVE_OAUTH"):
        if not os.environ.get(name):
            raise TransferError(f"Required credential environment name is missing: {name}")


def gh(endpoint: str, output=None) -> bytes:
    environment = os.environ.copy()
    environment.pop("GH_DEBUG", None)
    environment.pop("GH_HOST", None)
    result = subprocess.run(
        ["gh", "api", "--hostname", "github.com", endpoint],
        stdout=output if output is not None else subprocess.PIPE,
        stderr=subprocess.DEVNULL, env=environment, timeout=1200, check=False,
    )
    if result.returncode:
        raise TransferError(f"GitHub API operation failed with exit code {result.returncode}; no raw response was logged.")
    return result.stdout if output is None else b""


def file_digest(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        while block := stream.read(4 * 1024 * 1024):
            count += len(block)
            digest.update(block)
    return count, digest.hexdigest()


def assert_exact(count: int, digest: str, label: str) -> None:
    if count != EXPECTED_BYTES or digest != EXPECTED_SHA256:
        raise TransferError(f"{label} did not match the pinned byte count and SHA-256.")


def download_artifact(receipt: dict) -> Path:
    endpoint = f"repos/{REPOSITORY}/actions/artifacts/{ARTIFACT_ID}"
    metadata = json.loads(gh(endpoint))
    if (metadata.get("id") != ARTIFACT_ID or metadata.get("name") != ARTIFACT_NAME
            or metadata.get("size_in_bytes") != EXPECTED_BYTES
            or metadata.get("digest") != EXPECTED_PROVIDER_DIGEST
            or metadata.get("expired") is not False
            or metadata.get("workflow_run", {}).get("id") != SOURCE_RUN_ID):
        raise TransferError("GitHub artifact metadata does not match the exact authorized artifact, run, size and provider digest.")
    receipt["source"]["observed_provider_digest"] = metadata["digest"]
    receipt["source"]["observed_provider_bytes"] = metadata["size_in_bytes"]
    receipt["source"]["head_sha"] = metadata["workflow_run"].get("head_sha")
    save_receipt(receipt)
    archive = WORK / DESTINATION_NAME
    if archive.exists():
        count, digest = file_digest(archive)
        assert_exact(count, digest, "Existing local archive")
    else:
        with tempfile.NamedTemporaryFile(prefix="artifact-", suffix=".download", dir=WORK, delete=False) as stream:
            temporary = Path(stream.name)
        try:
            with temporary.open("wb") as stream:
                gh(endpoint + "/zip", stream)
            count, digest = file_digest(temporary)
            assert_exact(count, digest, "Downloaded raw GitHub ZIP")
            if archive.exists():
                raise TransferError("The local archive path appeared concurrently; refusing to replace it.")
            temporary.replace(archive)
        finally:
            temporary.unlink(missing_ok=True)
    receipt["source"]["downloaded_bytes"] = count
    receipt["source"]["downloaded_sha256"] = digest
    receipt["source"]["raw_zip_verified"] = True
    save_receipt(receipt)
    return archive


def metadata(drive, file_id: str) -> dict:
    return drive.files().get(fileId=file_id, fields=FILE_FIELDS, supportsAllDrives=True).execute(num_retries=5)


def validate_ancestry(drive) -> list[dict]:
    chain = []
    seen = set()
    current = DESTINATION_ID
    for _ in range(32):
        if current in seen:
            raise TransferError("Destination folder ancestry contains a cycle.")
        seen.add(current)
        item = metadata(drive, current)
        if item.get("id") != current or item.get("mimeType") != FOLDER_MIME or item.get("trashed"):
            raise TransferError("Destination ancestry is not an existing, untrashed folder chain.")
        chain.append({key: item.get(key) for key in ("id", "name", "parents", "modifiedTime")})
        if current == PROJECT_ROOT_ID:
            return chain
        parents = item.get("parents", [])
        if len(parents) != 1:
            raise TransferError("Destination ancestry is ambiguous or does not reach the exact project root.")
        current = parents[0]
    raise TransferError("Destination ancestry did not reach the exact project root within the bounded walk.")


def matching_files(drive) -> list[dict]:
    found = []
    token = None
    while True:
        page = drive.files().list(
            q=f"'{DESTINATION_ID}' in parents and name = '{DESTINATION_NAME}' and trashed = false",
            fields=f"nextPageToken,incompleteSearch,files({FILE_FIELDS})", pageSize=100,
            pageToken=token, spaces="drive", supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute(num_retries=5)
        if page.get("incompleteSearch"):
            raise TransferError("Drive returned an incomplete same-name search; refusing to create a file.")
        found.extend(page.get("files", []))
        token = page.get("nextPageToken")
        if not token:
            break
    if len(found) > 1:
        raise TransferError("Multiple same-name destination files exist; refusing to choose, overwrite or delete one.")
    return found


def validate_file(item: dict) -> None:
    if (not re.fullmatch(r"[A-Za-z0-9_-]+", item.get("id", ""))
            or item.get("name") != DESTINATION_NAME or item.get("mimeType") != "application/zip"
            or int(item.get("size", -1)) != EXPECTED_BYTES or item.get("trashed")
            or item.get("parents") != [DESTINATION_ID]):
        raise TransferError("The destination file metadata differs from the authorized name, type, size or parent.")


class DigestSink(io.RawIOBase):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.digest = hashlib.sha256()

    def writable(self) -> bool:
        return True

    def write(self, data) -> int:
        if self.count + len(data) > EXPECTED_BYTES:
            raise TransferError("Drive readback exceeded the pinned byte count.")
        self.digest.update(data)
        self.count += len(data)
        return len(data)

    def tell(self) -> int:
        return self.count


def readback(drive, item: dict) -> tuple[dict, dict]:
    from googleapiclient.http import MediaIoBaseDownload

    before = metadata(drive, item["id"])
    validate_file(before)
    sink = DigestSink()
    downloader = MediaIoBaseDownload(sink, drive.files().get_media(fileId=item["id"], supportsAllDrives=True), chunksize=CHUNK_BYTES)
    done = False
    while not done:
        _, done = downloader.next_chunk(num_retries=5)
    digest = sink.digest.hexdigest()
    assert_exact(sink.count, digest, "Authenticated complete Drive readback")
    after = metadata(drive, item["id"])
    validate_file(after)
    keys = ("id", "name", "mimeType", "size", "parents", "modifiedTime", "version", "trashed")
    if any(before.get(key) != after.get(key) for key in keys):
        raise TransferError("Destination file metadata changed during full readback; no stable verification is claimed.")
    return after, {"bytes": sink.count, "sha256": digest, "verified": True,
                   "metadata_unchanged_during_readback": True, "verified_utc": now()}


def archive_to_drive(receipt: dict, archive: Path) -> None:
    from googleapiclient.http import MediaFileUpload

    sys.path.insert(0, str(ROOT))
    from tools.drive_sync import service

    drive = service()
    receipt["destination"]["ancestor_chain_before"] = validate_ancestry(drive)
    found = matching_files(drive)
    # A second check immediately before create covers a file appearing during setup.
    if not found:
        found = matching_files(drive)
    if found:
        item = found[0]
        receipt["operation"] = "verified_existing_file"
        receipt["created_new_file"] = False
    else:
        stage(receipt, "resumable_upload")
        media = MediaFileUpload(str(archive), mimetype="application/zip", chunksize=CHUNK_BYTES, resumable=True)
        request = drive.files().create(
            body={"name": DESTINATION_NAME, "mimeType": "application/zip", "parents": [DESTINATION_ID]},
            media_body=media, fields=FILE_FIELDS, supportsAllDrives=True,
        )
        item = None
        while item is None:
            _, item = request.next_chunk(num_retries=5)
        receipt["operation"] = "uploaded_new_file"
        receipt["created_new_file"] = True
    file_id = item.get("id", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", file_id):
        raise TransferError("Drive did not return a usable file identity; inspect the destination before any retry.")
    receipt["drive"] = {"id": file_id, "canonical_url": f"https://drive.google.com/file/d/{file_id}/view"}
    save_receipt(receipt)  # Retain a newly created ID even if verification later fails.
    validate_file(metadata(drive, file_id))
    stage(receipt, "authenticated_stream_readback")
    after, verification = readback(drive, item)
    receipt["drive"]["metadata"] = after
    receipt["readback"] = verification
    receipt["destination"]["ancestor_chain_after"] = validate_ancestry(drive)
    final_matches = matching_files(drive)
    if len(final_matches) != 1 or final_matches[0]["id"] != file_id:
        raise TransferError("The final same-name search is ambiguous or the verified file moved; no overwrite or cleanup was attempted.")
    receipt["unique_same_name_file_confirmed"] = True
    receipt["status"] = "verified"
    receipt["finished_utc"] = now()
    stage(receipt, "complete")


def summary(receipt: dict) -> None:
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if not target:
        return
    lines = ["## Exact PR116 proof archive", "", f"Status: **{receipt['status']}**", "",
             f"Source: artifact `{ARTIFACT_ID}` from run `{SOURCE_RUN_ID}`.",
             f"Expected ZIP: {EXPECTED_BYTES:,} bytes; SHA-256 `{EXPECTED_SHA256}`."]
    if receipt.get("drive"):
        lines += ["", f"Drive: [{DESTINATION_NAME}]({receipt['drive']['canonical_url']})"]
    if receipt["status"] == "verified":
        lines += ["", "Complete authenticated readback matched. Destination ancestry and filename uniqueness passed.",
                  "Operation: " + receipt["operation"] + "."]
    else:
        lines += ["", "Verification did not finish. Read the small JSON receipt before retrying; existing files were not overwritten or deleted."]
    with Path(target).open("a") as stream:
        stream.write("\n".join(lines) + "\n")


def main() -> int:
    receipt = {
        "schema": "exact-github-proof-drive-archive-v1", "status": "in_progress", "started_utc": now(),
        "source": {"repository": REPOSITORY, "run_id": SOURCE_RUN_ID, "artifact_id": ARTIFACT_ID,
                   "artifact_name": ARTIFACT_NAME, "expected_bytes": EXPECTED_BYTES,
                   "expected_sha256": EXPECTED_SHA256, "expected_provider_digest": EXPECTED_PROVIDER_DIGEST},
        "destination": {"folder_id": DESTINATION_ID, "project_root_id": PROJECT_ROOT_ID, "file_name": DESTINATION_NAME},
        "execution": {"run_id": os.environ.get("GITHUB_RUN_ID"), "attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
                      "source_commit": os.environ.get("GITHUB_SHA")},
        "archive_extracted_or_executed": False, "permissions_changed": False,
        "overwrite_or_delete_operations": False,
    }
    try:
        stage(receipt, "validate_cloud_context")
        require_cloud_context()
        stage(receipt, "download_and_verify_exact_artifact")
        archive = download_artifact(receipt)
        stage(receipt, "validate_destination_and_existing_file")
        archive_to_drive(receipt, archive)
        print(json.dumps({"status": "verified", "drive": receipt["drive"], "readback": receipt["readback"]}))
        return 0
    except Exception as exc:
        # Google errors may contain authenticated resumable URLs or token responses.
        # Do not print exception repr, raw HTTP bodies, traceback or gh stderr.
        error = {"category": type(exc).__name__, "stage": receipt.get("stage")}
        if isinstance(exc, TransferError):
            error["message"] = str(exc)
        status = getattr(getattr(exc, "resp", None), "status", None)
        if isinstance(status, int):
            error["http_status"] = status
        receipt.update(status="failed", error=error, finished_utc=now())
        save_receipt(receipt)
        print(json.dumps({"status": "failed", "error": error}), file=sys.stderr)
        return 1
    finally:
        summary(receipt)


if __name__ == "__main__":
    raise SystemExit(main())
