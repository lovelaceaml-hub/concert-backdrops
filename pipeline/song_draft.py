"""One command for a short draft of any concert song.

    ./scripts/video song-draft 5                    # Song 5, 10 seconds from 0:30, 1080p review quality
    ./scripts/video song-draft s09 --start 60 --seconds 20
    ./scripts/video song-draft "God Bless" --no-render   # only fetch the song and write the project
    ./scripts/video song-draft 5 --recording audio/promo/s05.mp3   # use another recording

It looks the song up in project-docs/production-system/catalogs/songs.json, uses
that song's chosen concert recording (fetched from the Songs Drive folder by its
recorded file id when it is not already in work/song-sources/), pairs it with the
song's existing engine scene (engine/songs/sNN_*.py) through the reusable p3d-kit
scene, and renders a short draft with the song's sound attached. The project is
written under work/song-drafts/, so nothing in projects/ changes. A draft is a
design check, not an approved film; the final show format stays 4K60 after approval.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
import subprocess
import sys

from .project import PipelineError, load_project

CATALOG = "project-docs/production-system/catalogs/songs.json"
TEMPLATE = "projects/song-scene-demo/project.json"


def find_song(root: Path, query: str) -> dict:
    songs = json.loads((root / CATALOG).read_text())["songs"]
    q = query.strip().lower()
    if q.isdigit():
        q = f"s{int(q):02d}"
    hits = [s for s in songs if s["id"].lower() == q] or [s for s in songs if q in s["title"].lower()]
    if len(hits) != 1:
        names = ", ".join(f"{s['id']} {s['title']}" for s in (hits or songs))
        raise PipelineError(f"Song '{query}' matched {len(hits)} songs. Use a number or id: {names}")
    return hits[0]


def engine_module(root: Path, song_id: str, override: str | None) -> str:
    if override:
        if not (root / "engine/songs" / f"{override}.py").is_file():
            raise PipelineError(f"engine/songs/{override}.py does not exist")
        return override
    found = sorted(p.stem for p in (root / "engine/songs").glob(f"{song_id}_*.py"))
    # Prefer the current scene over a preserved original (for example s03_original).
    found.sort(key=lambda name: name.endswith("_original"))
    if not found:
        raise PipelineError(f"No engine scene for {song_id} in engine/songs/. Author one first or pass --module.")
    return found[0]


def scene_seconds(root: Path, module: str) -> float | None:
    """Length of the scene's authored timeline (its TOTAL), when it states one."""
    import re
    match = re.search(r"^TOTAL\s*=\s*([0-9.]+)", (root / "engine/songs" / f"{module}.py").read_text(), re.M)
    return float(match.group(1)) if match else None


def recording(root: Path, song: dict) -> Path:
    source = song.get("audio", {}).get("source") or {}
    local = source.get("local_path")
    if not local:
        raise PipelineError(f"{song['id']} has no chosen recording in the song catalog.")
    path = root / local
    if path.is_file():
        return path
    if not source.get("file_id"):
        raise PipelineError(f"{local} is missing and the catalog has no Drive file id to fetch it.")
    if not (os.environ.get("GOOGLE_DRIVE_OAUTH") or os.environ.get("GOOGLE_DRIVE_SA_KEY")):
        raise PipelineError(f"{local} is missing. Put the recording there, or set GOOGLE_DRIVE_OAUTH "
                            f"(a GitHub Actions secret) so it can be fetched from Drive.")
    # The Drive helper needs google-api-python-client and google-auth (see tool-proofs.yml);
    # they live in the system Python, not the locked render environment.
    # `scripts/video` runs inside the render environment, whose python3 comes first on PATH,
    # so skip it when looking for the system interpreter.
    venv = str(root / ".venv")
    outside = os.pathsep.join(p for p in os.environ.get("PATH", "").split(os.pathsep) if not p.startswith(venv))
    helper = os.environ.get("DRIVE_PYTHON") or shutil.which("python3", path=outside) or sys.executable
    probe = subprocess.run([helper, "-c", "import googleapiclient, google.oauth2"], capture_output=True)
    if probe.returncode:
        raise PipelineError(f"{helper} cannot import the Google Drive client. Install google-api-python-client "
                            f"and google-auth there, or set DRIVE_PYTHON to an interpreter that has them.")
    subprocess.run([helper, str(root / "tools/drive_sync.py"), "get-id", source["file_id"], "--as", str(path)],
                   cwd=root, check=True)
    return path


def audio_seconds(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def write_project(root: Path, song: dict, module: str, audio: Path, start: float, seconds: float) -> Path:
    length = audio_seconds(audio)
    if start < 0 or seconds <= 0 or start + seconds > length:
        raise PipelineError(f"{song['id']} is {length:.1f}s long; --start {start} with --seconds {seconds} does not fit.")
    data = json.loads((root / TEMPLATE).read_text())
    fps = data["video"]["fps"]
    rel = str(audio.relative_to(root))
    data.update({
        "project_id": f"song-draft-{song['id']}",
        "title": f"{song['title']} (draft)",
        "description": f"Draft of {song['title']}: {seconds:g} seconds from {start:g}s, scene {module}, "
                       f"with the song's chosen recording. Generated by video song-draft; not an approved film.",
        "audio": {"source": rel, "offset_seconds": start, "fade_in_seconds": 0.5, "fade_out_seconds": 1.0},
    })
    data["timing"] = {**data["timing"], "visual_only": False}
    data["shots"] = [{
        "id": f"{song['id']}-draft", "name": f"{song['title']} draft", "renderer": "p3d-kit",
        "start_frame": 0, "end_frame_exclusive": round(seconds * fps), "scene": "scenes/p3d/song_scene.py",
        "params": {"song": module, "start_seconds": start, "audio": rel, "bloom_scale": 0.7, "grain": False},
    }]
    target = root / "work/song-drafts" / song["id"] / "project.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n")
    load_project(root, str(target.relative_to(root)))  # same checks every project gets
    return target


def song_draft(root: Path, query: str, *, start: float = 30, seconds: float = 10, quality: str = "review",
               module: str | None = None, render: bool = True, allow_local: bool = False,
               recording_path: str | None = None) -> dict:
    song = find_song(root, query)
    scene = engine_module(root, song["id"], module)
    length = scene_seconds(root, scene)
    if length is not None and start + seconds > length:
        raise PipelineError(f"{scene} is authored for {length:g} seconds, so --start {start:g} with --seconds "
                            f"{seconds:g} would run past its picture (it fades to black). Choose an excerpt "
                            f"inside 0 to {length:g} seconds, or author a full-length scene for this song.")
    if recording_path:
        audio = (root / recording_path).resolve()
        if not audio.is_file() or not audio.is_relative_to(root):
            raise PipelineError("--recording must be an existing file inside the repository.")
    else:
        audio = recording(root, song)
    manifest = write_project(root, song, scene, audio, start, seconds)
    report = {"song": song["id"], "title": song["title"], "scene": scene, "recording": str(audio.relative_to(root)),
              "scene_seconds": length, "start_seconds": start, "seconds": seconds, "quality": quality,
              "project": str(manifest.relative_to(root)), "rendered": False}
    if length is not None and length < audio_seconds(audio) - 1:
        report["note"] = (f"{scene} is a {length:g}-second scene, shorter than the recording, and its authored "
                          f"moments were timed for a promo excerpt, so they may not line up with this recording.")
    if render:
        command = [sys.executable, "-m", "pipeline.cli", "preview", report["project"], "--quality", quality]
        if allow_local:
            command.append("--allow-local-render")
        subprocess.run(command, cwd=root, check=True, env={**os.environ, "PYTHONHASHSEED": "0"})
        report.update(rendered=True, output=f"work/pipeline/song-draft-{song['id']}/{quality}/")
    return report
