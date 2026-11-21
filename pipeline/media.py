"""Frame-accurate encoding, finishing, technical QA and review evidence."""
from __future__ import annotations

import html
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .delivery import (
    PROFILES, audio_encoding_args, get_profile, require_encoder, resolve_profile,
    stream_validation_errors, validate_source_frames, video_encoding_args,
)
from .project import PipelineError, Project, file_hash, safe_path, write_json
from .render import EXCLUDED_DIRS, SOURCE_SUFFIXES, guard_render, production_lock, run, shot_directory, verify_complete
from .temporal import scan_motion


def probe(path: Path, *, timeout: float = 120) -> dict:
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(path)], capture_output=True, text=True, check=True, timeout=timeout)
        return json.loads(result.stdout)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise PipelineError(f"Cannot inspect media {path}: {exc}") from exc


def encoding_args(fps: int, profile: str = "h264") -> list[str]:
    """Compatibility entry point for the default H.264 encoder arguments."""
    return video_encoding_args(fps, get_profile(profile))


def current_master_path(project: Project, quality: str) -> Path:
    """Resolve the most recently assembled profile, including legacy receipts."""
    directory = project.output(quality)
    receipt = directory / "master.json"
    filename = "master.mp4"
    if receipt.is_file():
        try:
            metadata = json.loads(receipt.read_text())
            filename = metadata.get("filename", filename)
        except (OSError, ValueError, AttributeError) as exc:
            raise PipelineError(f"Cannot read the master receipt: {exc}") from exc
    if not isinstance(filename, str) or filename not in {profile.master_filename for profile in PROFILES.values()}:
        raise PipelineError("Master receipt contains an unsupported filename. Assemble the project again.")
    return directory / filename


def source_audio(project: Project, directory: Path) -> Path | None:
    spec = project.data.get("audio", {})
    if not spec.get("source"):
        return None
    audio = safe_path(project.root, spec["source"])
    metadata = probe(audio)
    if not any(s["codec_type"] == "audio" for s in metadata["streams"]):
        raise PipelineError("The configured audio source has no audio stream.")
    offset = float(spec.get("offset_seconds", 0))
    duration = float(metadata["format"].get("duration", 0))
    if duration - offset + 0.02 < project.seconds:
        raise PipelineError(f"Audio has {duration - offset:.3f}s after the offset, but the timeline needs {project.seconds:.3f}s. Fix the source or timeline; no silent truncation is performed.")
    if offset:
        trimmed = directory / "audio-offset.wav"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(offset), "-i", str(audio), "-t", str(project.seconds), "-vn", "-c:a", "pcm_s24le", str(trimmed)], cwd=project.root, log=directory / "assemble.log")
        return trimmed
    return audio


def git_state(root: Path) -> dict:
    def get(args: list[str]) -> str:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    return {"commit": get(["rev-parse", "HEAD"]), "branch": get(["branch", "--show-current"]), "dirty": bool(get(["status", "--porcelain"]))}


def finishing_input_hashes(root: Path, editor: str) -> dict[str, str]:
    """Track finishing code independently from the already-rendered scene inputs."""
    root = root.resolve()
    inputs = {
        root / name for name in (
            "pipeline/media.py", "pipeline/delivery.py", "pipeline/temporal.py",
            "pipeline/project.py", "pipeline/render.py", "pyproject.toml", "uv.lock",
            "package.json", "package-lock.json", "infra/toolchain.lock.json",
        ) if (root / name).is_file()
    }
    if editor == "remotion":
        browser_selector = root / "apps/browser-path.mjs"
        if browser_selector.is_file():
            inputs.add(browser_selector)
        for folder in (root / "apps/editor", root / "apps/shared"):
            for base, directories, filenames in os.walk(folder, followlinks=False):
                directories[:] = sorted(name for name in directories if name not in EXCLUDED_DIRS)
                for filename in filenames:
                    path = Path(base) / filename
                    if path.suffix in SOURCE_SUFFIXES:
                        inputs.add(path)
    result = {}
    for path in sorted(inputs):
        if not path.resolve().is_relative_to(root):
            raise PipelineError(f"Finishing input points outside the repository: {path}")
        result[path.relative_to(root).as_posix()] = file_hash(path)
    return result


def assemble(project: Project, quality: str, *, editor: str = "ffmpeg", allow_local: bool = False, profile: str | None = None) -> Path:
    guard_render(project, allow_local)
    if editor == "ffmpeg" and project.data.get("captions"):
        raise PipelineError("This project has captions. Use --editor remotion to include them in the finished video.")
    if editor not in ("ffmpeg", "remotion"):
        raise PipelineError("editor must be ffmpeg or remotion.")
    delivery = resolve_profile(project, quality, profile)
    if editor == "remotion" and delivery.name != "h264":
        raise PipelineError("The current Remotion compositor is an 8-bit H.264 path. Use --editor ffmpeg with rendered-in-scene titles for a real 10-bit master, or choose --profile h264 for Remotion.")
    capabilities = require_encoder(delivery)
    directory = project.output(quality)
    with production_lock(directory / ".production.lock"):
        finishing_inputs = finishing_input_hashes(project.root, editor)
        receipts = verify_complete(project, quality)
        source_frames = validate_source_frames(project, quality, delivery)
        log = directory / "assemble.log"
        clips = []
        for shot in project.shots:
            shot_dir = shot_directory(project, quality, shot)
            clip = shot_dir / f"clip-{delivery.name}.{delivery.extension}"
            temporary = shot_dir / f"clip-{delivery.name}.partial.{delivery.extension}"
            run(["ffmpeg", "-v", "error", "-y", "-filter_threads", "4", "-framerate", str(project.fps), "-start_number", str(shot["start_frame"]), "-i", str(shot_dir / "frames/frame_%06d.png"), "-frames:v", str(shot["end_frame_exclusive"] - shot["start_frame"]), *video_encoding_args(project.fps, delivery), "-an", str(temporary)], cwd=project.root, log=log)
            temporary.replace(clip)
            clips.append({"src": str(clip), "start_frame": shot["start_frame"], "end_frame_exclusive": shot["end_frame_exclusive"]})
        audio = source_audio(project, directory)
        settings = project.settings(quality)
        output = directory / delivery.master_filename
        temporary = output.with_name(output.stem + ".partial" + output.suffix)
        if editor == "remotion":
            props = {"title": project.data.get("title", project.id), "width": settings["width"], "height": settings["height"], "fps": project.fps, "durationInFrames": project.frames, "clips": clips, "captions": project.data.get("captions", [])}
            if audio:
                props["audio_src"] = str(audio)
            props_path = directory / "editor-props.json"
            write_json(props_path, props)
            command = ["node", "apps/editor/render.mjs", "--input", str(props_path), "--output", str(temporary)]
            if allow_local:
                command.append("--allow-local-render")
            run(command, cwd=project.root, log=log)
        elif editor == "ffmpeg":
            listing = directory / "concat.txt"
            listing.write_text("\n".join("file '" + c["src"].replace("'", "'\\''") + "'" for c in clips) + "\n")
            command = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing)]
            if audio:
                command += ["-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", *audio_encoding_args(delivery)]
            else:
                command += ["-map", "0:v:0", "-c:v", "copy", "-an"]
            command += ["-t", str(project.seconds), "-movflags", "+faststart+write_colr", str(temporary)]
            run(command, cwd=project.root, log=log)
        metadata = probe(temporary, timeout=max(120, project.seconds * 6))
        errors = stream_validation_errors(metadata, delivery, width=settings["width"], height=settings["height"], fps=project.fps, frames=project.frames, wanted_audio=bool(audio))
        if finishing_inputs != finishing_input_hashes(project.root, editor):
            errors.append("Finishing inputs changed during assembly. Run assembly again with stable source files.")
        if errors:
            raise PipelineError("The assembled master failed delivery validation; the previous master is preserved. " + " ".join(errors))
        temporary.replace(output)
        write_json(directory / "master.json", {
            "project_id": project.id, "project_identity": project.identity(), "quality": quality,
            "sha256": file_hash(output), "width": settings["width"], "height": settings["height"],
            "fps": project.fps, "frames": project.frames, "editor": editor,
            "filename": output.name, "delivery_profile": delivery.name,
            "source_frames": source_frames, "encoder_capabilities": capabilities,
            "finishing_inputs": finishing_inputs,
            "color": {"space": "rec709", "transfer": "bt709", "range": "limited", "hdr": False,
                      "pixel_format": delivery.pixel_format, "range_metadata": "implicit_for_prores" if delivery.name == "prores422hq" else "tv"},
            "shot_fingerprints": {r["shot_id"]: r["fingerprint"] for r in receipts},
            "source": git_state(project.root), "created_utc": datetime.now(timezone.utc).isoformat(),
            "audio_source_sha256": file_hash(safe_path(project.root, project.data["audio"]["source"])) if audio else None,
        })
        (directory / "approval.json").unlink(missing_ok=True)
    return output


def sample_frames(project: Project, quality: str, *, per_shot: int = 3) -> list[tuple[int, Path]]:
    out = []
    for shot in project.shots:
        frames = np.linspace(shot["start_frame"], shot["end_frame_exclusive"] - 1, per_shot, dtype=int)
        out.extend((int(f), shot_directory(project, quality, shot) / "frames" / f"frame_{f:06d}.png") for f in frames)
    return out


def storyboard(project: Project, quality: str) -> Path:
    directory = project.output(quality)
    directory.mkdir(parents=True, exist_ok=True)
    rows = []
    for shot in project.shots:
        images = []
        for frame in sorted({shot["start_frame"], (shot["start_frame"] + shot["end_frame_exclusive"] - 1) // 2, shot["end_frame_exclusive"] - 1}):
            relative = f"shots/{shot['id']}/frames/frame_{frame:06d}.png"
            if (directory / relative).is_file():
                images.append(f'<figure><img src="{html.escape(relative)}"><figcaption>Frame {frame} / {frame / project.fps:.3f}s</figcaption></figure>')
            else:
                images.append(f'<figure class="missing">Frame {frame}<small>Not rendered</small></figure>')
        rows.append(f'<section><h2>{html.escape(shot["id"])}: {html.escape(shot.get("name", ""))}</h2><p>{shot["renderer"]} | Frames {shot["start_frame"]} to {shot["end_frame_exclusive"] - 1}</p><div class="frames">{"".join(images)}</div></section>')
    path = directory / "review.html"
    master = current_master_path(project, quality)
    video = ""
    if master.is_file():
        link = f'<p><a href="{html.escape(master.name)}" download>Download {html.escape(master.name)}</a></p>'
        video = link + (f'<video controls preload="metadata" src="{html.escape(master.name)}"></video>' if master.name == "master.mp4" else '<p>This 10-bit master needs a compatible video player or editing application.</p>')
    path.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Video review</title><style>body{margin:0;background:#f8f3eb;color:#25334e;font:16px system-ui;padding:32px;max-width:1300px;margin:auto}h1{font-size:36px}section{background:white;border-radius:16px;padding:20px;margin:20px 0}video{width:100%;max-height:70vh}.frames{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}figure{margin:0}img{width:100%;border-radius:8px}figcaption,small{display:block;padding:8px;color:#596579}.missing{aspect-ratio:16/9;display:grid;place-content:center;background:#edf0f5}a{color:#375a9a}@media(max-width:700px){.frames{grid-template-columns:1fr}body{padding:16px}}</style><h1>' + html.escape(project.data.get("title", project.id)) + '</h1><p>Technical review workspace. Creative approval is recorded separately. ' + f'{project.frames} frames at {project.fps} fps, {project.seconds:.3f}s.</p>' + video + "".join(rows) + '</html>')
    return path


def qa(project: Project, quality: str) -> dict:
    directory = project.output(quality)
    master = current_master_path(project, quality)
    if not master.is_file():
        raise PipelineError("No master exists. Assemble the rendered shots first.")
    metadata = probe(master, timeout=max(120, project.seconds * 6))
    errors, warnings = [], []
    settings = project.settings(quality)
    video = next((s for s in metadata["streams"] if s["codec_type"] == "video"), {})
    audio = [s for s in metadata["streams"] if s["codec_type"] == "audio"]
    master_receipt = {}
    try:
        master_receipt = json.loads((directory / "master.json").read_text())
    except (OSError, ValueError) as exc:
        errors.append(f"Master receipt: {exc}")
    delivery = get_profile(master_receipt.get("delivery_profile", "h264"))
    if master.name != delivery.master_filename:
        errors.append("Master filename does not match the recorded delivery profile.")
    errors.extend(stream_validation_errors(metadata, delivery, width=settings["width"], height=settings["height"], fps=project.fps, frames=project.frames, wanted_audio=bool(project.data.get("audio", {}).get("source"))))
    try:
        fps = float(Fraction(video.get("avg_frame_rate", "0/1")))
    except (ValueError, TypeError, ZeroDivisionError):
        fps = 0
    try:
        duration = float(video.get("duration", metadata.get("format", {}).get("duration", 0)))
    except (ValueError, TypeError):
        duration = 0
    if not math.isfinite(duration):
        duration = 0
    try:
        if master_receipt.get("project_identity") != project.identity():
            errors.append("Master was assembled from a different project revision.")
        if master_receipt.get("sha256") != file_hash(master):
            errors.append("Master bytes changed since assembly.")
        if "finishing_inputs" in master_receipt and master_receipt["finishing_inputs"] != finishing_input_hashes(project.root, master_receipt.get("editor", "ffmpeg")):
            errors.append("Finishing inputs changed after assembly. Finalize again before approving or archiving this master.")
        current = verify_complete(project, quality)
        if master_receipt.get("shot_fingerprints") != {r["shot_id"]: r["fingerprint"] for r in current}:
            errors.append("Master does not match the current rendered shots.")
        if delivery.source_bits_required == 16:
            source_frames = validate_source_frames(project, quality, delivery)
            if master_receipt.get("source_frames") != source_frames:
                errors.append("High-bit-depth source evidence does not match the rendered frames.")
    except (OSError, ValueError, PipelineError) as exc:
        errors.append(f"Provenance check: {exc}")
    metrics = []
    tiles = []
    # Inspect the encoded movie as well as the source sequence. Output stays private scratch.
    qa_frames = directory / "qa-frames"
    qa_frames.mkdir(exist_ok=True)
    requested = sorted({frame for frame, _ in sample_frames(project, quality)})
    for index, frame in enumerate(requested):
        path = qa_frames / f"frame_{frame:06d}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(frame / project.fps), "-i", str(master), "-frames:v", "1", str(path)], cwd=project.root, log=directory / "qa.log")
        with Image.open(path) as picture:
            rgb = np.asarray(picture.convert("RGB"), dtype=np.float32) / 255
            clipped = float(np.mean(np.min(rgb, axis=2) >= 0.985))
            luminance = float(np.mean(rgb @ np.array([0.2126, 0.7152, 0.0722])))
            if clipped > 0.08:
                warnings.append(f"Frame {frame}: {clipped:.1%} near-white pixels; inspect possible washed-out highlights.")
            if luminance < 0.025:
                warnings.append(f"Frame {frame}: very dark frame; inspect against the warm visual brief.")
            metrics.append({"frame": frame, "mean_display_luma": round(luminance, 5), "near_white_fraction": round(clipped, 5)})
            tile = picture.convert("RGB")
            tile.thumbnail((320, 180))
            panel = Image.new("RGB", (320, 206), "#f5f1e9")
            panel.paste(tile, ((320 - tile.width) // 2, 0))
            ImageDraw.Draw(panel).text((8, 186), f"Frame {frame} | {frame / project.fps:.3f}s", fill="#25334e")
            tiles.append(panel)
    if tiles:
        sheet = Image.new("RGB", (960, 206 * ((len(tiles) + 2) // 3)), "#e9e5dd")
        for index, tile in enumerate(tiles):
            sheet.paste(tile, ((index % 3) * 320, (index // 3) * 206))
        sheet.save(directory / "contact-sheet.jpg", quality=92)
    motion = scan_motion(project, master)
    warnings.extend(motion["warnings"])
    report = {"project_id": project.id, "quality": quality, "technical_passed": not errors, "creative_approval": "not_assessed", "errors": errors, "warnings": warnings, "filename": master.name, "delivery_profile": delivery.name, "video_codec": video.get("codec_name"), "pixel_format": video.get("pix_fmt"), "color": {key: video.get(key) for key in ("color_primaries", "color_transfer", "color_space", "color_range")}, "frames": project.frames, "fps": fps, "duration_seconds": duration, "audio_streams": len(audio), "image_samples": metrics, "motion": motion, "master_sha256": file_hash(master), "limitations": ["Automated checks do not assess anatomy, lettering accuracy, musical intention, or artistic quality.", "Brightness and temporal pixel checks are review warnings, not a creative approval or physical camera measurements.", "The 10-bit profiles are Rec.709 SDR, not HDR. ProRes range is implicit when ffprobe omits its range flag."]}
    write_json(directory / "qa.json", report)
    storyboard(project, quality)
    return report
