"""Renderer dispatch, content-based caching, and bounded execution."""
from __future__ import annotations

import contextlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

from .environment import worker_environment
from .project import PipelineError, Project, file_hash, json_hash, safe_path, write_json


EXCLUDED_DIRS = {"node_modules", ".git", ".venv", "__pycache__", "dist", "public", "build", "out", "work"}
SOURCE_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".css", ".glsl", ".vert", ".frag", ".toml"}


def guard_render(project: Project, allow_local: bool = False) -> None:
    if platform.system() == "Darwin" and not allow_local:
        raise PipelineError("Rendering on the Mac is disabled. Use a cloud checkout, or explicitly pass --allow-local-render for this invocation.")
    if project.data["production"].get("cloud_gpu_provider") is not None:
        raise PipelineError("Cloud GPU dispatch is not configured.")


def run(command: list[str], *, cwd: Path, log: Path | None = None, env: dict | None = None, timeout: int = 3600) -> None:
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
    try:
        if log:
            with log.open("a") as stream:
                stream.write("COMMAND " + json.dumps(command) + "\n")
                stream.flush()
                result = subprocess.run(command, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
        else:
            result = subprocess.run(command, cwd=cwd, env=env, timeout=timeout)
    except FileNotFoundError as exc:
        raise PipelineError(f"Missing executable {command[0]}. Run video doctor.") from exc
    except subprocess.TimeoutExpired as exc:
        raise PipelineError(f"Process exceeded {timeout}s: {command[0]}; see {log}.") from exc
    if result.returncode:
        tail = "\n".join(log.read_text(errors="replace").splitlines()[-18:]) if log else ""
        raise PipelineError(f"Command failed with exit {result.returncode}: {command[0]}\n{tail}")


def command_version(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        return (result.stdout or result.stderr).splitlines()[0] if result.returncode == 0 else "unavailable"
    except (OSError, subprocess.TimeoutExpired, IndexError):
        return "unavailable"


def blender_binary(root: Path) -> str:
    if os.getenv("BLENDER_BIN"):
        return os.environ["BLENDER_BIN"]
    bundled = root / ".tools/blender-5.2.4-linux-x64/blender"
    return str(bundled) if bundled.is_file() else (shutil.which("blender") or "blender")


def browser_binary(root: Path) -> tuple[str | None, str | None]:
    """Use the same explicit or pinned browser selection as both JS renderers."""
    try:
        result = subprocess.run(["node", "apps/browser-path.mjs"], cwd=root, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    if result.returncode:
        return None, result.stderr.strip() or "The selected headless browser is unavailable."
    path = result.stdout.strip()
    return (path, None) if path else (None, "Browser selection returned no executable.")


def runtime_identity(renderer: str, root: Path | None = None) -> dict:
    info = {"platform": platform.system(), "machine": platform.machine(), "python": platform.python_version(), "python_hash_seed": "0"}
    for package in ("numpy", "Pillow", "moderngl"):
        try:
            info[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    if renderer == "blender":
        info["blender"] = command_version([blender_binary(root or Path.cwd()), "--version"])
    if renderer == "threejs":
        info["node"] = command_version(["node", "--version"])
        browser, error = browser_binary(root or Path.cwd())
        info["chromium"] = command_version([browser, "--version"]) if browser else "unavailable"
        info["browser_executable"] = browser
        if error:
            info["browser_selection_error"] = error
    if renderer in ("p3d", "p3d-approved", "p3d-kit"):
        info["graphics"] = "software-egl"
        info["software_threads"] = 1
    if renderer == "p3d-approved":
        from .approved import runtime_identity as reference_runtime
        info["reference"] = reference_runtime(root or Path.cwd())
    return info


def dependency_files(project: Project, shot: dict) -> list[Path]:
    root = project.root
    files: set[Path] = set()

    def add(path: Path, all_files: bool = False) -> None:
        if path.is_file():
            if not path.resolve().is_relative_to(root):
                raise PipelineError(f"Dependency points outside repository: {path}")
            files.add(path.resolve())
        elif path.is_dir():
            for base, dirs, names in os.walk(path, followlinks=False):
                dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
                for name in sorted(names):
                    child = Path(base) / name
                    if all_files or child.suffix in SOURCE_SUFFIXES:
                        add(child)

    # Finishing/review changes must not invalidate expensive 3D frames. Hash the
    # renderer's actual shared modules; additional scene imports belong in its
    # explicit dependency list. Assembly records its own finishing inputs.
    add(root / "pipeline/project.py")
    add(root / "pipeline/render.py")
    add(root / "pipeline/environment.py")
    add(safe_path(root, shot["scene"]))
    for name in ("uv.lock", "package-lock.json", "package.json", "infra/toolchain.lock.json"):
        if (root / name).is_file():
            add(root / name)
    if shot["renderer"] == "threejs":
        add(root / "apps/scene-preview")
        add(root / "apps/shared")
        add(root / "apps/motion")
        add(root / "apps/browser-path.mjs")
        add(root / "scenes/three")
    elif shot["renderer"] == "blender":
        add(root / "pipeline/motion")
        add(root / "scenes/blender")
    elif shot["renderer"] == "p3d-approved":
        from .approved import dependency_files as reference_dependencies
        for path in reference_dependencies(project):
            add(path)
    elif shot["renderer"] == "p3d-kit":
        from .kit import dependency_files as kit_dependencies
        for path in kit_dependencies(project):
            add(path)
    else:
        add(root / "pipeline/legacy.py")
        add(root / "pipeline/audio.py")
        add(root / "engine")
        add(root / "assets", all_files=True)
        add(root / "fonts", all_files=True)
        if shot.get("params", {}).get("features"):
            add(safe_path(root, shot["params"]["features"]))
    for name in project.data.get("dependencies", []) + shot.get("dependencies", []):
        add(safe_path(root, name), all_files=True)
    for field in ("timing", "style"):
        if isinstance(project.data.get(field), str):
            add(safe_path(root, project.data[field]))
    if project.data.get("audio", {}).get("source") and shot["renderer"] != "p3d-kit":
        add(safe_path(root, project.data["audio"]["source"]))
    return sorted(files)


def fingerprint(project: Project, shot: dict, quality: str, runtime: dict | None = None) -> tuple[str, dict]:
    inputs = {str(p.relative_to(project.root)): file_hash(p) for p in dependency_files(project, shot)}
    audio = project.data.get("audio", {})
    if shot["renderer"] == "p3d-approved":
        audio = {key: value for key, value in audio.items() if key in ("source", "source_sha256", "offset_seconds")}
    elif shot["renderer"] == "p3d-kit":
        # This registered scene has an authored visual clock and neutral audio
        # controls. Attached music is an assembly input, not a pose input.
        audio = {}
    value = {
        "cache_version": 1, "shot": shot, "settings": project.settings(quality),
        "seed": project.data["production"]["random_seed"],
        "timing": project.related_data("timing"), "style": project.related_data("style"),
        "audio": audio, "inputs": inputs,
        "runtime": runtime if runtime is not None else runtime_identity(shot["renderer"], project.root),
    }
    return json_hash(value), value


def valid_frame(path: Path, size: tuple[int, int], checksum: str | None = None, bit_depth: int | None = None) -> bool:
    try:
        if checksum and file_hash(path) != checksum:
            return False
        if bit_depth is not None:
            # Pillow exposes RGB16 PNGs as RGB8; read the PNG IHDR before decoding.
            with path.open("rb") as stream:
                header = stream.read(29)
            if len(header) < 29 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR" or header[24] != bit_depth:
                return False
        with Image.open(path) as frame:
            if frame.size != size:
                return False
            frame.verify()
        return True
    except (OSError, ValueError, SyntaxError):
        return False


@contextlib.contextmanager
def production_lock(path: Path):
    """OS lock automatically releases after a killed worker; no stale lock directory."""
    import fcntl
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise PipelineError("This project/quality already has an active render or assembly process.") from exc
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def shot_directory(project: Project, quality: str, shot: dict) -> Path:
    return project.output(quality) / "shots" / shot["id"]


def render_shot(project: Project, quality: str, shot: dict, frames: list[int], *, force: bool = False, allow_local: bool = False) -> dict:
    directory = shot_directory(project, quality, shot)
    output = directory / "frames"
    output.mkdir(parents=True, exist_ok=True)
    settings = project.settings(quality)
    size = (settings["width"], settings["height"])
    depth = settings.get("image_bit_depth", 8)
    key, provenance = fingerprint(project, shot, quality)
    receipt_path = directory / "receipt.json"
    try:
        receipt = json.loads(receipt_path.read_text())
    except (OSError, ValueError):
        receipt = {}
    same = not force and receipt.get("fingerprint") == key
    previous = receipt.get("frames", {}) if same else {}
    retained = {}
    for frame, checksum in previous.items():
        filename = f"frame_{int(frame):06d}.png"
        if valid_frame(output / filename, size, checksum, depth):
            retained[frame] = checksum
    if not same:
        # Only this shot's owned products are invalidated, never approved source media.
        for path in output.glob("frame_*.png"):
            path.unlink()
        receipt_path.unlink(missing_ok=True)
    pending = [f for f in frames if str(f) not in retained]
    before = time.monotonic()
    policy = project.data["production"]
    chunk_size = policy.get("render_chunk_frames", 30)
    threads = policy.get("threads", 4)
    rendered_count = 0

    def checkpoint():
        current = {
            "fingerprint": key, "provenance": provenance, "frames": retained,
            "complete": all(str(f) in retained for f in range(shot["start_frame"], shot["end_frame_exclusive"])),
            "shot_id": shot["id"], "width": size[0], "height": size[1], "fps": project.fps,
            "image_bit_depth": depth, "last_render_seconds": round(time.monotonic() - before, 3),
            "last_rendered_frames": rendered_count,
        }
        write_json(receipt_path, current)
        return current

    def check_sources():
        if any(not (project.root / name).is_file() or file_hash(project.root / name) != digest
               for name, digest in provenance["inputs"].items()):
            raise PipelineError("Source changed during rendering. Freeze the round, then run render again; earlier receipts will be checked for staleness.")

    for offset in range(0, len(pending), chunk_size):
        if (project.output(quality) / "STOP").exists():
            raise PipelineError("This production round has a STOP marker. Remove it only when intentionally resuming.")
        check_sources()
        chunk = pending[offset:offset + chunk_size]
        # Remove any unverified leftovers before starting this chunk. Partial files
        # are never adopted from a different job or an interrupted previous job.
        for frame in chunk:
            (output / f"frame_{frame:06d}.png").unlink(missing_ok=True)
        job = {
            "project_id": project.id, "shot": shot,
            "video": {k: settings[k] for k in ("width", "height", "fps")},
            "seed": policy["random_seed"], "frames": chunk,
            "out_dir": str(output), "samples": settings.get("samples", 1), "repo_root": str(project.root),
            "temporal_samples": settings.get("temporal_samples"),
            "image_bit_depth": depth, "motion_blur": settings.get("motion_blur", {"enabled": False}),
            "threads": threads, "quality": quality,
            "source_inputs": provenance["inputs"],
            "timing": project.related_data("timing"), "style": project.related_data("style"),
            "audio": project.data.get("audio", {}), "features_dir": str(directory / "audio"),
            "allow_local_render": allow_local,
            "stop_file": str(project.output(quality) / "STOP"),
        }
        job_path = directory / "job.json"
        write_json(job_path, job)
        renderer = shot["renderer"]
        if renderer == "blender":
            command = [blender_binary(project.root), "-b", "--factory-startup", "-t", str(threads), "--python-exit-code", "1", "--python", str(project.root / "scenes/blender/render.py"), "--", "--job", str(job_path)]
        elif renderer == "threejs":
            command = ["node", "apps/scene-preview/capture.mjs", "--job", str(job_path)]
            if allow_local:
                command.append("--allow-local-render")
        elif renderer == "p3d-approved":
            command = [sys.executable, "-m", "pipeline.approved", "--job", str(job_path)]
        elif renderer == "p3d-kit":
            command = [sys.executable, "-m", "pipeline.kit", "--job", str(job_path)]
        else:
            command = [sys.executable, "-m", "pipeline.legacy", "--job", str(job_path)]
        print(f"Rendering {shot['id']}: frames {chunk[0]} to {chunk[-1]} ({len(chunk)} of {len(pending)} pending) with {renderer}", flush=True)
        env = worker_environment(renderer, threads)
        try:
            run(command, cwd=project.root, log=directory / "render.log", env=env, timeout=policy.get("render_timeout_seconds", 1800))
        finally:
            check_sources()
            # Even if the worker times out, preserve frames it finished atomically.
            # Re-running verifies their checksums, then resumes the missing frames.
            for frame in chunk:
                path = output / f"frame_{frame:06d}.png"
                if valid_frame(path, size, bit_depth=depth):
                    retained[str(frame)] = file_hash(path)
                    rendered_count += 1
            if retained:
                checkpoint()
        invalid = [f for f in chunk if str(f) not in retained]
        if invalid:
            raise PipelineError(f"Renderer did not write valid frames for shot {shot['id']}: {invalid[:10]}")
    receipt = checkpoint()
    print(f"{shot['id']}: {rendered_count} rendered, {len(frames) - len(pending)} reused, complete={receipt['complete']}", flush=True)
    return receipt


def render(project: Project, quality: str, *, selected: list[int] | None = None, shot_ids: list[str] | None = None, force: bool = False, allow_local: bool = False) -> list[dict]:
    guard_render(project, allow_local)
    if (project.output(quality) / "STOP").exists():
        raise PipelineError("This production round has a STOP marker. Remove it only when intentionally resuming.")
    if selected is not None and any(f < 0 or f >= project.frames for f in selected):
        raise PipelineError(f"Selected frames must be between 0 and {project.frames - 1}.")
    if shot_ids and set(shot_ids) - {s["id"] for s in project.shots}:
        raise PipelineError("One or more selected shot ids do not exist.")
    results = []
    with production_lock(project.output(quality) / ".production.lock"):
        for shot in project.shots:
            if shot_ids and shot["id"] not in shot_ids:
                continue
            frames = [f for f in (selected if selected is not None else range(project.frames)) if shot["start_frame"] <= f < shot["end_frame_exclusive"]]
            if frames:
                results.append(render_shot(project, quality, shot, frames, force=force, allow_local=allow_local))
    return results


def verify_complete(project: Project, quality: str) -> list[dict]:
    receipts = []
    for shot in project.shots:
        directory = shot_directory(project, quality, shot)
        try:
            receipt = json.loads((directory / "receipt.json").read_text())
        except (OSError, ValueError) as exc:
            raise PipelineError(f"Shot {shot['id']} is not rendered. Run video render first.") from exc
        key, _ = fingerprint(project, shot, quality)
        if receipt.get("fingerprint") != key:
            raise PipelineError(f"Shot {shot['id']} is stale. Run video render to update it.")
        settings = project.settings(quality)
        for frame in range(shot["start_frame"], shot["end_frame_exclusive"]):
            checksum = receipt.get("frames", {}).get(str(frame))
            if not checksum or not valid_frame(directory / "frames" / f"frame_{frame:06d}.png", (settings["width"], settings["height"]), checksum, settings.get("image_bit_depth", 8)):
                raise PipelineError(f"Shot {shot['id']} frame {frame} is missing or changed. Run video render to repair it.")
        receipts.append(receipt)
    return receipts
