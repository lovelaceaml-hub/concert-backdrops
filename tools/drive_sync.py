#!/usr/bin/env python3
"""Read song files from, and save renders to, the "Concert Backdrops - Songs" Drive folder.

Used by cloud jobs (GitHub Actions). GOOGLE_DRIVE_OAUTH (Anthony's sign-in token for
the private "Concert Video Renders" app in the Drive Backups Google Cloud project) can
read and save. GOOGLE_DRIVE_SA_KEY (a service account shared only on this folder) can
read but not save: Google gives service accounts no storage in personal Drives.
Every action stays inside the Concert Backdrops - Songs folder.

    python3 tools/drive_sync.py list   [--path "Videos"]
    python3 tools/drive_sync.py get    "01 All You Stars of Zion.mp3" --to work/song-sources/
    python3 tools/drive_sync.py put    work/out/master.mp4 --path "Videos/Renders"
    python3 tools/drive_sync.py check  # read the folder and save, then remove, a small test file
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

FOLDER_ID = "1xyNZn4ZA6bjPcvKjGfgSWQIs9aAp2PPd"  # Concert Backdrops - Songs
FOLDER_MIME = "application/vnd.google-apps.folder"


def service():
    """Prefer the owner's sign-in token (can save files); fall back to the read-only service account."""
    from googleapiclient.discovery import build
    scopes = ["https://www.googleapis.com/auth/drive"]
    oauth = os.environ.get("GOOGLE_DRIVE_OAUTH")
    if oauth:
        from google.oauth2.credentials import Credentials
        info = json.loads(oauth)
        creds = Credentials(None, refresh_token=info["refresh_token"], client_id=info["client_id"],
                            client_secret=info["client_secret"], token_uri=info["token_uri"], scopes=scopes)
    else:
        from google.oauth2 import service_account
        raw = os.environ.get("GOOGLE_DRIVE_SA_KEY")
        if not raw:
            sys.exit("Set GOOGLE_DRIVE_OAUTH (saves and reads) or GOOGLE_DRIVE_SA_KEY (reads only); both are Actions secrets.")
        creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=scopes)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def children(drive, parent: str):
    q = f"'{parent}' in parents and trashed = false"
    token = None
    while True:
        page = drive.files().list(q=q, fields="nextPageToken, files(id, name, mimeType, size)",
                                  pageToken=token, pageSize=1000).execute()
        yield from page.get("files", [])
        token = page.get("nextPageToken")
        if not token:
            return


def folder(drive, path: str, create: bool = False) -> str:
    current = FOLDER_ID
    for part in [p for p in path.split("/") if p]:
        match = [f for f in children(drive, current) if f["name"] == part and f["mimeType"] == FOLDER_MIME]
        if match:
            current = match[0]["id"]
        elif create:
            current = drive.files().create(body={"name": part, "mimeType": FOLDER_MIME, "parents": [current]},
                                           fields="id").execute()["id"]
        else:
            sys.exit(f"Drive folder not found: {path}")
    return current


def get(drive, name: str, path: str, to: Path) -> Path:
    from googleapiclient.http import MediaIoBaseDownload
    match = [f for f in children(drive, folder(drive, path)) if f["name"] == name]
    if not match:
        sys.exit(f"Drive file not found: {path}/{name}")
    to.mkdir(parents=True, exist_ok=True)
    out = to / name
    with out.open("wb") as stream:
        downloader = MediaIoBaseDownload(stream, drive.files().get_media(fileId=match[0]["id"]),
                                         chunksize=32 * 1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return out


def put(drive, local: Path, path: str) -> str:
    from googleapiclient.http import MediaFileUpload
    parent = folder(drive, path, create=True)
    media = MediaFileUpload(str(local), resumable=True, chunksize=32 * 1024 * 1024)
    existing = [f for f in children(drive, parent) if f["name"] == local.name]
    if existing:
        return drive.files().update(fileId=existing[0]["id"], media_body=media, fields="id").execute()["id"]
    return drive.files().create(body={"name": local.name, "parents": [parent]}, media_body=media,
                                fields="id").execute()["id"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=("list", "get", "put", "check"))
    parser.add_argument("name", nargs="?")
    parser.add_argument("--path", default="", help="Subfolder inside Concert Backdrops - Songs")
    parser.add_argument("--to", type=Path, default=Path("work/song-sources"))
    args = parser.parse_args()
    drive = service()
    if args.action == "list":
        for f in children(drive, folder(drive, args.path)):
            print(f"{'[folder] ' if f['mimeType'] == FOLDER_MIME else ''}{f['name']}  {f.get('size', '')}")
    elif args.action == "get":
        print(get(drive, args.name, args.path, args.to))
    elif args.action == "put":
        print(put(drive, Path(args.name), args.path))
    else:
        names = [f["name"] for f in children(drive, FOLDER_ID)]
        print(json.dumps({"read_folder": True, "items_seen": len(names)}))
        import uuid
        probe = Path(f"work/drive-check-{uuid.uuid4().hex}.txt")  # unique: never touches an existing file
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("Drive write check from the concert video cloud job.\n")
        try:
            file_id = put(drive, probe, "Production System")
            drive.files().delete(fileId=file_id).execute()
            print(json.dumps({"write_folder": True}))
        except Exception as exc:  # report the exact Drive refusal
            print(json.dumps({"write_folder": False, "error": str(exc)[:400]}))
            sys.exit(1)


if __name__ == "__main__":
    main()
