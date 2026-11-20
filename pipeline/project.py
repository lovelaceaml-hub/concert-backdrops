"""Project contract, path validation and the authoritative frame clock."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class PipelineError(Exception):
    """An actionable production error."""


def repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for directory in (here, *here.parents):
        if (directory / "pyproject.toml").is_file() and (directory / "pipeline").is_dir():
            return directory
    raise PipelineError("Run video inside the concert-backdrops repository, or use --root PATH.")


def safe_path(root: Path, value: str, *, exists: bool = True) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise PipelineError(f"Expected a nonempty repository-relative path, got {value!r}.")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise PipelineError(f"Path escapes the repository: {value!r}")
    if exists and not path.exists():
        raise PipelineError(f"Required input is missing: {value}")
    return path


def positive_int(value: Any, label: str, *, zero: bool = False) -> int:
    if type(value) is not int or value < (0 if zero else 1):
        raise PipelineError(f"{label} must be {'a nonnegative' if zero else 'a positive'} integer.")
    return value


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def write_json(path: Path, data: Any) -> None:
    """Replace complete metadata atomically; a partial receipt is never valid."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def read_data(path: Path) -> dict:
    try:
        text = path.read_text()
        data = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise PipelineError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PipelineError(f"Expected an object in {path}.")
    return data


@dataclass
class Project:
    root: Path
    manifest: Path
    data: dict

    @property
    def id(self) -> str:
        return self.data["project_id"]

    @property
    def shots(self) -> list[dict]:
        return self.data["shots"]

    @property
    def frames(self) -> int:
        return self.shots[-1]["end_frame_exclusive"]

    @property
    def fps(self) -> int:
        return self.data["video"]["fps"]

    @property
    def seconds(self) -> float:
        return self.frames / self.fps

    def output(self, quality: str) -> Path:
        self.settings(quality)
        return safe_path(self.root, f"work/pipeline/{self.id}/{quality}", exists=False)

    def settings(self, quality: str) -> dict:
        presets = self.data.get("quality", {})
        if quality not in presets:
            raise PipelineError(f"Unknown quality {quality!r}; choose from {', '.join(presets)}.")
        return {**self.data["video"], **presets[quality], "fps": self.fps}

    def related_data(self, field: str) -> dict:
        value = self.data.get(field)
        if value is None:
            return {}
        return read_data(safe_path(self.root, value)) if isinstance(value, str) else value

    def identity(self) -> str:
        related = {field: self.related_data(field) for field in ("timing", "style")}
        return json_hash({"manifest": self.data, "related": related})


def load_project(root: Path, name: str, *, check_files: bool = True) -> Project:
    root = root.resolve()
    candidate = Path(name)
    if candidate.is_absolute():
        manifest = candidate.resolve()
        if not manifest.is_relative_to(root):
            raise PipelineError("Project manifest must be inside the repository.")
    elif "/" in name or candidate.suffix in (".json", ".yaml", ".yml"):
        manifest = safe_path(root, name)
    else:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", name):
            raise PipelineError("Project id must use lowercase letters, numbers, hyphens or underscores.")
        folder = root / "projects" / name
        choices = [folder / ("project" + ext) for ext in (".yaml", ".yml", ".json")]
        manifest = next((p for p in choices if p.is_file()), choices[0])
    manifest = manifest.resolve()
    if not manifest.is_relative_to(root):
        raise PipelineError("Project manifest must be inside the repository.")
    project = Project(root, manifest, read_data(manifest))
    validate(project, check_files=check_files)
    return project


def validate(project: Project, *, check_files: bool = True) -> None:
    data, root = project.data, project.root
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise PipelineError("schema_version must be 1.")
    if not isinstance(data.get("project_id"), str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", data["project_id"]):
        raise PipelineError("project_id must use lowercase letters, numbers, hyphens or underscores.")
    video = data.get("video")
    if not isinstance(video, dict):
        raise PipelineError("video is required.")
    for label in ("width", "height", "fps"):
        positive_int(video.get(label), f"video.{label}")
    if video["fps"] > 240:
        raise PipelineError("video.fps must be at most 240.")
    if video["width"] % 2 or video["height"] % 2:
        raise PipelineError("Video width and height must be even for H.264 delivery.")
    policy = data.get("production", {})
    if not isinstance(policy, dict):
        raise PipelineError("production must be an object.")
    if policy.get("cloud_gpu_provider") is not None:
        raise PipelineError("No cloud GPU provider is configured in this setup.")
    for field in ("allow_paid_services", "allow_ai_generated_visuals", "allow_stock_footage", "allow_local_gpu"):
        if type(policy.get(field, False)) is not bool:
            raise PipelineError(f"production.{field} must be a boolean.")
    if policy.get("allow_paid_services", False):
        raise PipelineError("This setup does not dispatch paid services.")
    positive_int(policy.get("random_seed"), "production.random_seed", zero=True)
    presets = data.get("quality")
    if not isinstance(presets, dict) or not all(q in presets for q in ("draft", "review", "final")):
        raise PipelineError("quality must define draft, review and final presets.")
    for name, preset in presets.items():
        if not isinstance(preset, dict):
            raise PipelineError(f"quality.{name} must be an object.")
        if "fps" in preset:
            raise PipelineError("Quality presets cannot change fps; the project clock stays fixed.")
        for field in ("width", "height", "samples"):
            positive_int(preset.get(field), f"quality.{name}.{field}")
        if preset["width"] % 2 or preset["height"] % 2:
            raise PipelineError(f"quality.{name} dimensions must be even.")
        if preset["width"] * video["height"] != preset["height"] * video["width"]:
            raise PipelineError(f"quality.{name} must preserve the project aspect ratio.")
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        raise PipelineError("shots must be a nonempty list.")
    cursor, ids = 0, set()

    def dependencies(value: Any, label: str) -> None:
        if not isinstance(value, list):
            raise PipelineError(f"{label} must be a list of repository-relative paths.")
        for dependency in value:
            safe_path(root, dependency, exists=check_files)

    for shot in shots:
        if not isinstance(shot, dict):
            raise PipelineError("Each shot must be an object.")
        sid = shot.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", sid):
            raise PipelineError("Shot ids must be safe alphanumeric identifiers.")
        if sid in ids:
            raise PipelineError(f"Duplicate shot id: {sid}")
        ids.add(sid)
        start = positive_int(shot.get("start_frame"), f"{sid}.start_frame", zero=True)
        end = positive_int(shot.get("end_frame_exclusive"), f"{sid}.end_frame_exclusive")
        if start != cursor or end <= start:
            raise PipelineError(f"Shot {sid} must start at frame {cursor} and end after its start; no gaps or overlaps.")
        cursor = end
        renderer = shot.get("renderer")
        if renderer not in ("blender", "threejs", "p3d"):
            raise PipelineError(f"Unsupported renderer for {sid}: {renderer!r}")
        scene = safe_path(root, shot.get("scene"), exists=check_files)
        if check_files and not scene.is_file():
            raise PipelineError(f"The scene for {sid} must be a file.")
        if renderer == "p3d":
            if scene.parent != (root / "engine/songs").resolve() or not re.fullmatch(r"[A-Za-z0-9_]+\.py", scene.name):
                raise PipelineError("p3d scenes must be Python song files directly in engine/songs/.")
            if video["fps"] not in (30, 60):
                raise PipelineError("The existing p3d engine supports 30 or 60 fps.")
        if not isinstance(shot.get("params", {}), dict):
            raise PipelineError(f"{sid}.params must be an object.")
        if renderer == "p3d" and shot.get("params", {}).get("features"):
            safe_path(root, shot["params"]["features"], exists=check_files)
        dependencies(shot.get("dependencies", []), f"{sid}.dependencies")
    dependencies(data.get("dependencies", []), "dependencies")
    for key in ("timing", "style"):
        if key in data and not isinstance(data[key], (str, dict)):
            raise PipelineError(f"{key} must be a relative file path or an object.")
        if isinstance(data.get(key), str):
            safe_path(root, data[key], exists=check_files)
    timing = project.related_data("timing") if check_files or isinstance(data.get("timing"), dict) else {}
    if "fps" in timing and (type(timing["fps"]) is not int or timing["fps"] != video["fps"]):
        raise PipelineError("timing.fps must match the fixed project video.fps.")
    events = timing.get("events", [])
    if not isinstance(events, list):
        raise PipelineError("timing.events must be a list.")
    for event in events:
        if not isinstance(event, dict):
            raise PipelineError("Each timing event must be an object.")
        frame = positive_int(event.get("frame"), "timing event frame", zero=True)
        if frame >= cursor:
            raise PipelineError(f"Timing event frame {frame} is outside the timeline.")
    audio = data.get("audio", {})
    if not isinstance(audio, dict):
        raise PipelineError("audio must be an object.")
    if audio.get("source") is not None:
        source = safe_path(root, audio["source"], exists=check_files)
        if check_files and not source.is_file():
            raise PipelineError("audio.source must be a file.")
    offset = audio.get("offset_seconds", 0)
    if isinstance(offset, bool) or not isinstance(offset, (int, float)) or not math.isfinite(offset) or offset < 0:
        raise PipelineError("audio.offset_seconds must be a finite nonnegative number.")
    json_hash(data)  # Reject nonfinite and non-JSON YAML objects before jobs are created.
