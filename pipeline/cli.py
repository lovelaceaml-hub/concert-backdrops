"""One command surface for the repeatable video workflow."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .audio import analyze
from .media import assemble, qa, storyboard
from .project import PipelineError, file_hash, load_project, repo_root, write_json
from .render import blender_binary, command_version, render, verify_complete


def browser_probe(root: Path, *, launch: bool = False, allow_local: bool = False) -> dict:
    command = ["node", "apps/probe-browser.mjs"]
    if launch:
        command.append("--launch")
    if allow_local:
        command.append("--allow-local-render")
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30)
        report = json.loads(result.stdout)
        if not isinstance(report, dict):
            raise ValueError("Browser probe did not return an object.")
        return report
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return {"installed": False, "runtime_validated": False, "status": "probe_unavailable", "executable": None, "error": str(exc)}


def doctor(root: Path, *, probe_browser: bool = False, allow_local: bool = False) -> dict:
    browser = browser_probe(root, launch=probe_browser, allow_local=allow_local)
    binaries = {
        "python": sys.executable, "node": shutil.which("node"), "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"), "blender": blender_binary(root),
        "chromium": browser.get("executable"),
    }
    versions = {}
    for name, path in binaries.items():
        if path:
            versions[name] = command_version([path, "-version" if name in ("ffmpeg", "ffprobe") else "--version"])
        else:
            versions[name] = "missing"
    packages = {}
    for name in ("concert-video-pipeline", "PyYAML", "numpy", "Pillow", "scipy", "moderngl", "librosa", "fonttools", "brotli", "soundfile"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "not installed"
    errors = [f"Missing {name}." for name in ("node", "ffmpeg", "ffprobe", "blender") if versions[name] in ("missing", "unavailable")]
    warnings = []
    if not (root / "node_modules").is_dir():
        errors.append("JavaScript dependencies are missing. Run npm ci.")
    if not browser.get("installed"):
        errors.append(browser.get("error") or "The configured headless browser is missing.")
    elif probe_browser and not browser.get("runtime_validated"):
        warnings.append("The browser is installed but its runtime check did not pass: " + (browser.get("error") or browser.get("status", "unknown")))
    required_fonts = ["cormorant-garamond-latin-700-italic.ttf", "cormorant-garamond-latin-700-normal.ttf", "jost-latin-500-normal.ttf", "cormorant-garamond-latin-600-italic.ttf"]
    missing_fonts = [f for f in required_fonts if not (root / "fonts" / f).is_file()]
    if missing_fonts:
        warnings.append("Legacy p3d fonts are not ready; run the setup-fonts step before legacy rendering.")
    if packages["moderngl"] == "not installed":
        warnings.append("Legacy p3d dependencies are optional; install with uv sync --extra legacy.")
    if platform.system() == "Darwin":
        warnings.append("Local Mac rendering is disabled by default; no render was started.")
    return {"dependencies_ready": not errors, "full_pipeline_runtime_verified": False, "runtime_validation": {"browser": browser, "blender_render": "not_probed", "p3d_render": "not_probed", "remotion_finish": "not_probed"}, "platform": platform.system(), "binaries": binaries, "versions": versions, "python_packages": packages, "cloud_gpu_provider": None, "paid_dispatch": "disabled", "local_mac_render": "explicit invocation only", "errors": errors, "warnings": warnings, "checks": "Installed dependencies and optional browser launch only. A complete preview render plus QA verifies a project and its selected renderers."}


def frame_list(value: str) -> list[int]:
    result = set()
    try:
        for token in value.split(","):
            if ":" in token:
                start, end = map(int, token.split(":"))
                if start < 0 or end <= start:
                    raise ValueError()
                result.update(range(start, end))
            else:
                result.add(int(token))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use frame numbers separated by commas, or half-open ranges such as 0:30,60.") from exc
    if not result:
        raise argparse.ArgumentTypeError("Select at least one frame.")
    return sorted(result)


def create_project(root: Path, title: str, fps: int, seconds: int) -> Path:
    project_id = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:80]
    if not project_id:
        raise PipelineError("The title must contain letters or numbers.")
    target = root / "projects" / project_id / "project.json"
    if target.parent.exists():
        raise PipelineError(f"Project {project_id} already exists; it was not changed.")
    if not 1 <= fps <= 240 or seconds < 1:
        raise PipelineError("fps must be 1 to 240 and seconds must be positive.")
    data = {
        "schema_version": 1, "project_id": project_id, "title": title,
        "video": {"width": 1920, "height": 1080, "fps": fps},
        "audio": {"source": None, "offset_seconds": 0},
        "production": {"cloud_gpu_provider": None, "allow_local_gpu": False, "allow_paid_services": False, "allow_ai_generated_visuals": False, "allow_stock_footage": False, "random_seed": 2026},
        "quality": {"draft": {"width": 640, "height": 360, "samples": 8}, "review": {"width": 1920, "height": 1080, "samples": 32}, "final": {"width": 1920, "height": 1080, "samples": 64}},
        "style": "styles/zion-cinematic.json", "timing": {"fps": fps, "events": [], "manually_verified": False},
        "shots": [{"id": "opening", "name": "Opening", "renderer": "threejs", "start_frame": 0, "end_frame_exclusive": seconds * fps, "scene": "apps/scene-preview/src/scenes/Heavenly.tsx", "params": {}}],
    }
    write_json(target, data)
    return target


def archive(project, quality: str, destination: str) -> Path:
    directory = project.output(quality)
    qa_path = directory / "qa.json"
    master = directory / "master.mp4"
    if not qa_path.is_file() or not master.is_file():
        raise PipelineError("Run video finalize or video qa before archiving.")
    report = json.loads(qa_path.read_text())
    if not report.get("technical_passed") or report.get("master_sha256") != file_hash(master):
        raise PipelineError("The current master does not have a passing matching technical QA report.")
    manifest = json.loads((directory / "master.json").read_text())
    if manifest["project_identity"] != project.identity():
        raise PipelineError("Project changed after assembly. Re-render and finalize before archiving.")
    current = verify_complete(project, quality)
    if manifest.get("shot_fingerprints") != {r["shot_id"]: r["fingerprint"] for r in current}:
        raise PipelineError("Rendered shots changed after assembly. Finalize again before archiving.")
    target = Path(destination).expanduser().resolve() / (project.id + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    if target.exists():
        raise PipelineError(f"Archive target exists: {target}")
    target.mkdir(parents=True)
    filenames = ["master.mp4", "master.json", "qa.json", "contact-sheet.jpg"]
    for filename in filenames:
        if (directory / filename).is_file():
            shutil.copy2(directory / filename, target / filename)
    review_status = "not_recorded"
    notes = []
    approval_path = directory / "approval.json"
    if approval_path.is_file():
        try:
            approval = json.loads(approval_path.read_text())
        except (OSError, ValueError):
            approval = {}
        if approval.get("confirmed_viewed") is True and approval.get("master_sha256") == report["master_sha256"] and approval.get("project_identity") == project.identity():
            shutil.copy2(approval_path, target / "approval.json")
            review_status = "matching_review_record"
        else:
            review_status = "stale_review_omitted"
            notes.append("The existing approval record did not match this master and project. It remains in the working directory and was not included in this archive.")
    write_json(target / "archive-manifest.json", {"project_id": project.id, "quality": quality, "master_sha256": report["master_sha256"], "creative_review": review_status, "notes": notes})
    shutil.copy2(project.manifest, target / ("project" + project.manifest.suffix))
    write_json(target / "timing.json", project.related_data("timing"))
    write_json(target / "style.json", project.related_data("style"))
    for lock in ("uv.lock", "package-lock.json"):
        if (project.root / lock).is_file():
            shutil.copy2(project.root / lock, target / lock)
    write_json(target / "render-provenance.json", current)
    write_json(target / "SHA256.json", {p.name: file_hash(p) for p in target.iterdir() if p.is_file()})
    return target


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="video", description="Repeatable video production. Cloud GPU dispatch stays unconfigured.")
    p.add_argument("--root", type=Path, help="Repository root (otherwise discovered from the current directory)")
    sub = p.add_subparsers(dest="command", required=True)
    diagnostic = sub.add_parser("doctor", help="Distinguish installed dependencies from tested runtime capabilities")
    diagnostic.add_argument("--probe-browser", action="store_true", help="Explicitly launch the selected browser and test WebGL2, without rendering a video")
    diagnostic.add_argument("--allow-local-render", action="store_true", help="Permit the optional browser probe on this Mac")
    new = sub.add_parser("new", help="Create a project from the shared template")
    new.add_argument("title")
    new.add_argument("--fps", type=int, default=60)
    new.add_argument("--seconds", type=int, default=10)
    for command in ("validate", "analyze", "storyboard", "render", "preview", "assemble", "finalize", "qa", "review", "approve", "archive"):
        q = sub.add_parser(command)
        q.add_argument("project", help="Project id or a repository-relative manifest path")
        q.add_argument("--quality", choices=("draft", "review", "final"), default="draft" if command in ("preview", "storyboard", "review") else "final")
        if command in ("render", "preview"):
            q.add_argument("--frames", type=frame_list, help="Render selected global frames or half-open ranges")
            q.add_argument("--shot", action="append", help="Render only this shot id (repeatable)")
            q.add_argument("--force", action="store_true", help="Rerender the selected shots instead of reusing matching frames")
        if command in ("render", "preview", "assemble", "finalize", "storyboard"):
            q.add_argument("--allow-local-render", action="store_true", help="Explicitly permit rendering on this Mac for this invocation")
        if command in ("assemble", "finalize", "preview"):
            q.add_argument("--editor", choices=("ffmpeg", "remotion"), default="ffmpeg")
        if command == "storyboard":
            q.add_argument("--render", action="store_true", help="Render beginning/middle/end frames for each shot")
        if command == "approve":
            q.add_argument("--reviewer", required=True)
            q.add_argument("--note", required=True)
            q.add_argument("--confirm-viewed", action="store_true", required=True, help="Record an actual completed human review")
        if command == "archive":
            q.add_argument("--destination", required=True, help="Existing storage mount or local folder; no external upload is started")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = args.root.resolve() if args.root else repo_root()
        if args.command == "doctor":
            report = doctor(root, probe_browser=args.probe_browser, allow_local=args.allow_local_render)
            print(json.dumps(report, indent=2))
            passed = report["dependencies_ready"] and (not args.probe_browser or report["runtime_validation"]["browser"].get("runtime_validated") is True)
            return 0 if passed else 2
        if args.command == "new":
            print(create_project(root, args.title, args.fps, args.seconds))
            return 0
        project = load_project(root, args.project)
        quality = args.quality
        if args.command == "validate":
            print(json.dumps({"valid": True, "project": project.id, "frames": project.frames, "fps": project.fps, "seconds": project.seconds, "renderers": sorted({s["renderer"] for s in project.shots})}, indent=2))
        elif args.command == "analyze":
            print(analyze(project))
        elif args.command == "render":
            render(project, quality, selected=args.frames, shot_ids=args.shot, force=args.force, allow_local=args.allow_local_render)
        elif args.command in ("review", "storyboard"):
            if args.command == "storyboard" and args.render:
                selected = sorted({f for shot in project.shots for f in (shot["start_frame"], (shot["start_frame"] + shot["end_frame_exclusive"] - 1) // 2, shot["end_frame_exclusive"] - 1)})
                render(project, quality, selected=selected, allow_local=args.allow_local_render)
            print(storyboard(project, quality))
        elif args.command == "preview":
            render(project, quality, selected=args.frames, shot_ids=args.shot, force=args.force, allow_local=args.allow_local_render)
            if args.frames is None and args.shot is None:
                print(assemble(project, quality, editor=args.editor, allow_local=args.allow_local_render))
                report = qa(project, quality)
                print(json.dumps(report, indent=2))
                return 0 if report["technical_passed"] else 2
            print(storyboard(project, quality))
        elif args.command in ("assemble", "finalize"):
            print(assemble(project, quality, editor=args.editor, allow_local=args.allow_local_render))
            if args.command == "finalize":
                report = qa(project, quality)
                print(json.dumps(report, indent=2))
                return 0 if report["technical_passed"] else 2
        elif args.command == "qa":
            report = qa(project, quality)
            print(json.dumps(report, indent=2))
            return 0 if report["technical_passed"] else 2
        elif args.command == "approve":
            report = qa(project, quality)
            if not report["technical_passed"]:
                raise PipelineError("Technical QA failed; fix those errors before recording approval.")
            target = project.output(quality) / "approval.json"
            write_json(target, {"reviewer": args.reviewer, "note": args.note, "confirmed_viewed": True, "master_sha256": report["master_sha256"], "project_identity": project.identity(), "created_utc": datetime.now(timezone.utc).isoformat()})
            print(target)
        elif args.command == "archive":
            print(archive(project, quality, args.destination))
        return 0
    except (PipelineError, OSError, ValueError) as exc:
        print(f"video: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
