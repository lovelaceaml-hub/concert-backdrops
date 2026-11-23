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
from .media import assemble, current_master_path, finishing_input_hashes, qa, storyboard
from .project import PipelineError, Project, file_hash, load_project, read_data, repo_root, safe_path, validate, write_json
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


def doctor(root: Path, *, probe_browser: bool = False, allow_local: bool = False,
           renderers: list[str] | None = None, editor: str = "ffmpeg") -> dict:
    """Check only the selected production backends; installation is not render proof."""
    selected = sorted(set(renderers or ("blender", "threejs", "p3d")))
    allowed = {"blender", "threejs", "p3d", "p3d-approved", "p3d-kit"}
    if set(selected) - allowed or editor not in ("ffmpeg", "remotion"):
        raise PipelineError("Select a supported renderer and finishing backend.")
    browser_needed = "threejs" in selected or editor == "remotion"
    legacy_needed = any(name.startswith("p3d") for name in selected)
    browser = (browser_probe(root, launch=probe_browser, allow_local=allow_local)
               if browser_needed else {"status": "not_required", "installed": None,
                                       "runtime_validated": False, "executable": None})
    binaries = {"python": sys.executable, "ffmpeg": shutil.which("ffmpeg"),
                "ffprobe": shutil.which("ffprobe")}
    required = {"ffmpeg", "ffprobe"}
    if "blender" in selected:
        binaries["blender"] = blender_binary(root)
        required.add("blender")
    if browser_needed:
        binaries.update(node=shutil.which("node"), chromium=browser.get("executable"))
        required.add("node")
    versions = {name: command_version([path, "-version" if name in ("ffmpeg", "ffprobe") else "--version"])
                if path else "missing" for name, path in binaries.items()}
    packages = {}
    for name in ("concert-video-pipeline", "PyYAML", "numpy", "Pillow", "scipy", "moderngl", "librosa", "fonttools", "brotli", "soundfile"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "not installed"
    errors = [f"Missing {name}." for name in sorted(required) if versions[name] in ("missing", "unavailable")]
    warnings = []
    if browser_needed:
        if not (root / "node_modules").is_dir():
            errors.append("JavaScript dependencies are missing. Run npm ci.")
        if not browser.get("installed"):
            errors.append(browser.get("error") or "The configured headless browser is missing.")
        elif probe_browser and not browser.get("runtime_validated"):
            warnings.append("The browser is installed but its runtime check did not pass: " +
                            (browser.get("error") or browser.get("status", "unknown")))
    if legacy_needed:
        required_fonts = ["cormorant-garamond-latin-700-italic.ttf", "cormorant-garamond-latin-700-normal.ttf",
                          "jost-latin-500-normal.ttf", "cormorant-garamond-latin-600-italic.ttf"]
        missing_fonts = [name for name in required_fonts if not (root / "fonts" / name).is_file()]
        if missing_fonts:
            (errors if renderers is not None else warnings).append("Legacy p3d fonts are missing. Run the setup-fonts step: " + ", ".join(missing_fonts))
        for name in ("numpy", "Pillow", "scipy", "moderngl", "librosa", "fonttools", "brotli", "soundfile"):
            if packages[name] == "not installed":
                (errors if renderers is not None else warnings).append(f"Missing legacy dependency {name}. Run uv sync --frozen --extra legacy.")
    if platform.system() == "Darwin":
        warnings.append("Local Mac rendering is disabled by default; no render was started.")
    from .delivery import encoder_capabilities
    try:
        delivery = encoder_capabilities()
        if "libx264" not in delivery.get("encoders", []):
            errors.append("FFmpeg needs libx264 for H.264 delivery.")
        if set(selected) - {"p3d-approved", "p3d-kit"} and not delivery.get("zscale"):
            errors.append("The selected sRGB delivery path needs FFmpeg zscale.")
    except PipelineError as exc:
        delivery = {"error": str(exc)}
        errors.append(str(exc))
    return {"dependencies_ready": not errors, "selected_renderers": selected, "editor": editor,
            "full_pipeline_runtime_verified": False,
            "runtime_validation": {"browser": browser, "blender_render": "not_probed" if "blender" in selected else "not_required",
                                   "p3d_render": "not_probed" if legacy_needed else "not_required",
                                   "remotion_finish": "not_probed" if editor == "remotion" else "not_required"},
            "platform": platform.system(), "binaries": binaries, "versions": versions,
            "python_packages": packages, "delivery_capabilities": delivery,
            "cloud_gpu_provider": None, "paid_dispatch": "disabled", "local_mac_render": "disabled by default",
            "errors": errors, "warnings": warnings,
            "checks": "Selected backend dependencies only. Private audio, prepared assets and actual pixels are checked during production."}


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


def create_project(root: Path, title: str, fps: int, seconds: int, template: str = "cinematic") -> Path:
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
    if template == "cinematic":
        from .presets import cinematic_project
        data = cinematic_project(project_id, title, fps, seconds)
    validate(Project(root, target, data), check_files=False)
    write_json(target, data)
    return target


def archive(project, quality: str, destination: str) -> Path:
    directory = project.output(quality)
    qa_path = directory / "qa.json"
    master = current_master_path(project, quality)
    if not qa_path.is_file() or not master.is_file():
        raise PipelineError("Run video finalize or video qa before archiving.")
    report = json.loads(qa_path.read_text())
    if not report.get("technical_passed") or report.get("master_sha256") != file_hash(master):
        raise PipelineError("The current master does not have a passing matching technical QA report.")
    manifest = json.loads((directory / "master.json").read_text())
    if manifest["project_identity"] != project.identity():
        raise PipelineError("Project changed after assembly. Re-render and finalize before archiving.")
    if "finishing_inputs" in manifest and manifest["finishing_inputs"] != finishing_input_hashes(project.root, manifest.get("editor", "ffmpeg")):
        raise PipelineError("Finishing code changed after assembly. Finalize and check the current master before archiving.")
    current = verify_complete(project, quality)
    if manifest.get("shot_fingerprints") != {r["shot_id"]: r["fingerprint"] for r in current}:
        raise PipelineError("Rendered shots changed after assembly. Finalize again before archiving.")
    target = Path(destination).expanduser().resolve() / (project.id + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    if target.exists():
        raise PipelineError(f"Archive target exists: {target}")
    target.mkdir(parents=True)
    filenames = [master.name, "master.json", "qa.json", "contact-sheet.jpg"]
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


DELIVERIES_CATALOG = "project-docs/production-system/catalogs/deliveries.json"


def _validate_commit_sha(commit: str) -> str:
    value = commit.strip() if isinstance(commit, str) else ""
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", value):
        raise PipelineError(f"Commit must be a 7 to 40 character hexadecimal Git SHA, got {commit!r}.")
    return value.lower()


def _approved_reference_commit(root: Path, project_id: str) -> str | None:
    folder = root / "projects" / project_id
    manifest = next((folder / ("project" + ext) for ext in (".yaml", ".yml", ".json") if (folder / ("project" + ext)).is_file()), None)
    if manifest is None:
        return None
    data = read_data(manifest)
    for shot in data.get("shots", ()):
        if isinstance(shot, dict) and shot.get("renderer") == "p3d-approved":
            ref_id = shot.get("params", {}).get("reference")
            if isinstance(ref_id, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", ref_id):
                ref_path = safe_path(root, f"pipeline/references/{ref_id}.json", exists=False)
                if ref_path.is_file():
                    definition = read_data(ref_path)
                    commit = definition.get("source_commit") or definition.get("engine_commit")
                    if isinstance(commit, str) and commit.strip():
                        return _validate_commit_sha(commit)
    return None


def recorded_project_commit(root: Path, project_id: str) -> str:
    """Look up a project's recorded picture_source_commit in deliveries.json."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", project_id):
        raise PipelineError("Project id must use lowercase letters, numbers, hyphens or underscores.")
    catalog_path = root / DELIVERIES_CATALOG
    matched_without_commit = False
    if catalog_path.is_file():
        catalog = read_data(catalog_path)
        items = [item for item in catalog.get("items", ()) if isinstance(item, dict)]
        for field in ("project_id", "id"):
            for item in items:
                if item.get(field) == project_id:
                    commit = item.get("picture_source_commit")
                    if isinstance(commit, str) and commit.strip():
                        return _validate_commit_sha(commit)
                    matched_without_commit = True
    fallback = _approved_reference_commit(root, project_id)
    if fallback is not None:
        return fallback
    if matched_without_commit:
        raise PipelineError(
            f"Delivery {project_id!r} in {DELIVERIES_CATALOG} does not record a picture_source_commit. "
            "Pass --commit <sha> to reproduce from a specific commit."
        )
    if not catalog_path.is_file():
        raise PipelineError(
            f"Delivery catalog is missing: {DELIVERIES_CATALOG}. "
            "Pass --commit <sha> to reproduce from a specific commit."
        )
    raise PipelineError(
        f"Project {project_id!r} has no recorded commit in {DELIVERIES_CATALOG}. "
        "Check the project id or pass --commit <sha>."
    )


def reproduce(root: Path, project_id: str, quality: str = "review", commit: str | None = None, *, allow_local: bool = False) -> dict:
    """Reproduce a frozen film from its recorded Git commit in an isolated worktree."""
    root = root.resolve()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", project_id):
        raise PipelineError("Project id must use lowercase letters, numbers, hyphens or underscores.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", quality):
        raise PipelineError(f"Invalid quality preset name: {quality!r}.")
    target_commit = _validate_commit_sha(commit) if commit is not None else recorded_project_commit(root, project_id)
    try:
        resolved = subprocess.run(
            ["git", "rev-parse", "--verify", f"{target_commit}^{{commit}}"],
            cwd=root, capture_output=True, text=True,
        )
    except FileNotFoundError as exc:
        raise PipelineError("Git is required to reproduce a film from a recorded commit.") from exc
    if resolved.returncode != 0:
        raise PipelineError(
            f"Commit {target_commit} is not available in this Git repository. "
            f"Fetch the needed history (for example, git fetch origin {target_commit}) and try again."
        )
    full_sha = _validate_commit_sha(resolved.stdout.strip() or target_commit)
    short_sha = full_sha[:8]
    worktree = safe_path(root, f"work/reproduce/{project_id}-{short_sha}", exists=False)
    reused = False
    if worktree.exists():
        if not (worktree / ".git").exists():
            raise PipelineError(f"Path {worktree} already exists and is not a Git worktree. Move or remove it before reproducing.")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=worktree, capture_output=True, text=True)
        if head.returncode != 0:
            raise PipelineError(f"Could not read the commit checked out in {worktree}. Remove that folder and try again.")
        head_sha = head.stdout.strip().lower()
        if head_sha and head_sha != full_sha:
            raise PipelineError(f"Existing worktree {worktree} is at commit {head_sha}, not {full_sha}. Remove it and try again.")
        reused = True
    else:
        worktree.parent.mkdir(parents=True, exist_ok=True)
        added = subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree), full_sha],
            cwd=root, capture_output=True, text=True,
        )
        if added.returncode != 0:
            detail = (added.stderr or added.stdout or "").strip()
            raise PipelineError(f"Could not create Git worktree at {worktree} for commit {full_sha}: {detail}")
    command = ["./scripts/video", "produce", project_id, "--quality", quality]
    if allow_local:
        command.append("--allow-local-render")
    try:
        produced = subprocess.run(command, cwd=worktree)
    except FileNotFoundError as exc:
        raise PipelineError(f"Commit {full_sha} does not provide ./scripts/video inside {worktree}.") from exc
    if produced.returncode != 0:
        raise PipelineError(
            f"Reproducing {project_id} from commit {full_sha} failed (exit {produced.returncode}). "
            f"Inspect the output above; the worktree was kept at {worktree}."
        )
    output_dir = worktree / "work/pipeline" / project_id / quality
    return {
        "project_id": project_id,
        "commit": full_sha,
        "quality": quality,
        "worktree": str(worktree),
        "reused_worktree": reused,
        "output_dir": str(output_dir),
        "master": str(output_dir / "master.mp4"),
        "command": command,
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="video", description="Repeatable video production. Cloud GPU dispatch stays unconfigured.")
    p.add_argument("--root", type=Path, help="Repository root (otherwise discovered from the current directory)")
    sub = p.add_subparsers(dest="command", required=True)
    diagnostic = sub.add_parser("doctor", help="Distinguish installed dependencies from tested runtime capabilities")
    diagnostic.add_argument("--probe-browser", action="store_true", help="Explicitly launch the selected browser and test WebGL2, without rendering a video")
    diagnostic.add_argument("--allow-local-render", action="store_true", help="Permit the optional browser probe on this Mac")
    doctor_selection = diagnostic.add_mutually_exclusive_group()
    doctor_selection.add_argument("--project", help="Check only this project's renderers; private audio need not be present")
    doctor_selection.add_argument("--backend", action="append", choices=("blender", "threejs", "p3d", "p3d-approved", "p3d-kit"), help="Check this renderer only (repeatable)")
    diagnostic.add_argument("--editor", choices=("ffmpeg", "remotion"), default="ffmpeg")
    new = sub.add_parser("new", help="Create a project from the shared template")
    new.add_argument("title")
    new.add_argument("--fps", type=int, default=60)
    new.add_argument("--seconds", type=int, default=10)
    new.add_argument("--template", choices=("cinematic", "browser"), default="cinematic", help="Cinematic creates a Blender 4K60-capable project; browser creates the original Three.js study")
    bench = sub.add_parser("benchmark", help="Measure selected native frames at review and final quality without rendering a whole film")
    bench.add_argument("project")
    bench.add_argument("--qualities", nargs="+", help="Defaults to review and 4k-check when present, otherwise review and final")
    bench.add_argument("--frames", type=frame_list)
    bench.add_argument("--allow-local-render", action="store_true")
    motion = sub.add_parser("motion-qa", help="Inspect camera speed, acceleration and sampled jerk before rendering")
    motion.add_argument("project")
    repro = sub.add_parser("reproduce", help="Render an approved film from its recorded Git commit in an isolated worktree")
    repro.add_argument("project", help="Project id recorded in deliveries.json (or any project id when --commit is given)")
    repro.add_argument("--quality", default="review", help="Quality preset passed to the recorded commit's video produce (default: review)")
    repro.add_argument("--commit", help="Git commit SHA to reproduce from instead of looking up deliveries.json")
    repro.add_argument("--allow-local-render", action="store_true", help="Forward --allow-local-render to the recorded commit's video produce")
    for command in ("validate", "analyze", "prepare", "produce", "storyboard", "render", "preview", "assemble", "finalize", "qa", "review", "approve", "archive"):
        q = sub.add_parser(command)
        q.add_argument("project", help="Project id or a repository-relative manifest path")
        q.add_argument("--quality", default="draft" if command in ("preview", "produce", "storyboard", "review") else "final", help="A quality preset from this project's manifest")
        if command in ("render", "preview", "produce"):
            q.add_argument("--frames", type=frame_list, help="Render selected global frames or half-open ranges")
            q.add_argument("--shot", action="append", help="Render only this shot id (repeatable)")
            q.add_argument("--force", action="store_true", help="Rerender the selected shots instead of reusing matching frames")
        if command in ("render", "preview", "produce", "assemble", "finalize", "storyboard"):
            q.add_argument("--allow-local-render", action="store_true", help="Explicitly permit rendering on this Mac for this invocation")
        if command in ("assemble", "finalize", "preview", "produce"):
            q.add_argument("--editor", choices=("ffmpeg", "remotion"), default="ffmpeg")
            q.add_argument("--profile", choices=("h264", "hevc10", "prores422hq"), help="Override the project's delivery profile for this output")
        if command == "storyboard":
            q.add_argument("--render", action="store_true", help="Render beginning/middle/end frames for each shot")
        if command == "produce":
            q.add_argument("--plan", action="store_true", help="Describe the production stages without preparing, rendering or writing files")
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
            renderers = args.backend
            if args.project:
                inspected = load_project(root, args.project, check_files=False)
                renderers = sorted({shot["renderer"] for shot in inspected.shots})
            report = doctor(root, probe_browser=args.probe_browser, allow_local=args.allow_local_render,
                            renderers=renderers, editor=args.editor)
            print(json.dumps(report, indent=2))
            browser = report["runtime_validation"]["browser"]
            passed = report["dependencies_ready"] and (not args.probe_browser or browser.get("status") == "not_required" or browser.get("runtime_validated") is True)
            return 0 if passed else 2
        if args.command == "new":
            print(create_project(root, args.title, args.fps, args.seconds, args.template))
            return 0
        if args.command == "reproduce":
            report = reproduce(root, args.project, quality=args.quality, commit=args.commit, allow_local=args.allow_local_render)
            print(json.dumps(report, indent=2))
            return 0
        project = load_project(root, args.project, check_files=not (args.command == "produce" and args.plan))
        if args.command == "motion-qa":
            from .motion_review import motion_review
            print(json.dumps(motion_review(project), indent=2))
            return 0
        if args.command == "benchmark":
            from .benchmark import benchmark
            qualities = args.qualities or ["review", "4k-check" if "4k-check" in project.data["quality"] else "final"]
            print(json.dumps(benchmark(project, qualities, args.frames, allow_local=args.allow_local_render), indent=2))
            return 0
        quality = args.quality
        if args.command == "validate":
            print(json.dumps({"valid": True, "project": project.id, "frames": project.frames, "fps": project.fps, "seconds": project.seconds, "renderers": sorted({s["renderer"] for s in project.shots})}, indent=2))
        elif args.command == "analyze":
            print(analyze(project))
        elif args.command == "prepare":
            from .production import prepare
            print(json.dumps(prepare(project), indent=2))
        elif args.command == "produce":
            from .production import plan, produce
            if args.plan:
                print(json.dumps(plan(project, quality, selected=args.frames, shot_ids=args.shot, editor=args.editor), indent=2))
            else:
                result = produce(project, quality, selected=args.frames, shot_ids=args.shot, force=args.force,
                                 allow_local=args.allow_local_render, editor=args.editor, profile=args.profile)
                print(json.dumps(result, indent=2))
                return 0 if result.get("qa", {}).get("technical_passed", True) else 2
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
                print(assemble(project, quality, editor=args.editor, allow_local=args.allow_local_render, profile=args.profile))
                report = qa(project, quality)
                print(json.dumps(report, indent=2))
                return 0 if report["technical_passed"] else 2
            print(storyboard(project, quality))
        elif args.command in ("assemble", "finalize"):
            print(assemble(project, quality, editor=args.editor, allow_local=args.allow_local_render, profile=args.profile))
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
