"""Frame-accurate encoding, finishing, technical QA and review evidence."""
from __future__ import annotations

import html
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .project import PipelineError, Project, file_hash, safe_path, write_json
from .render import guard_render, production_lock, run, shot_directory, verify_complete


def probe(path: Path) -> dict:
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(path)], capture_output=True, text=True, check=True, timeout=120)
        return json.loads(result.stdout)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise PipelineError(f"Cannot inspect media {path}: {exc}") from exc


def encoding_args(fps: int) -> list[str]:
    return ["-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(fps), "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", "-movflags", "+faststart"]


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


def assemble(project: Project, quality: str, *, editor: str = "ffmpeg", allow_local: bool = False) -> Path:
    guard_render(project, allow_local)
    if editor == "ffmpeg" and project.data.get("captions"):
        raise PipelineError("This project has captions. Use --editor remotion to include them in the finished video.")
    directory = project.output(quality)
    with production_lock(directory / ".production.lock"):
        receipts = verify_complete(project, quality)
        log = directory / "assemble.log"
        clips = []
        for shot in project.shots:
            shot_dir = shot_directory(project, quality, shot)
            clip = shot_dir / "clip.mp4"
            temporary = shot_dir / "clip.partial.mp4"
            run(["ffmpeg", "-v", "error", "-y", "-framerate", str(project.fps), "-start_number", str(shot["start_frame"]), "-i", str(shot_dir / "frames/frame_%06d.png"), "-frames:v", str(shot["end_frame_exclusive"] - shot["start_frame"]), *encoding_args(project.fps), "-an", str(temporary)], cwd=project.root, log=log)
            temporary.replace(clip)
            clips.append({"src": str(clip), "start_frame": shot["start_frame"], "end_frame_exclusive": shot["end_frame_exclusive"]})
        audio = source_audio(project, directory)
        settings = project.settings(quality)
        output = directory / "master.mp4"
        temporary = directory / "master.partial.mp4"
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
                command += ["-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k"]
            else:
                command += ["-map", "0:v:0", "-c:v", "copy", "-an"]
            command += ["-t", str(project.seconds), "-movflags", "+faststart", str(temporary)]
            run(command, cwd=project.root, log=log)
        else:
            raise PipelineError("editor must be ffmpeg or remotion.")
        metadata = probe(temporary)
        video = next((s for s in metadata["streams"] if s["codec_type"] == "video"), {})
        if int(video.get("nb_read_frames", -1)) != project.frames:
            raise PipelineError("The assembled master has the wrong frame count; the previous master is preserved.")
        temporary.replace(output)
        write_json(directory / "master.json", {
            "project_id": project.id, "project_identity": project.identity(), "quality": quality,
            "sha256": file_hash(output), "width": settings["width"], "height": settings["height"],
            "fps": project.fps, "frames": project.frames, "editor": editor,
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
    video = '<video controls preload="metadata" src="master.mp4"></video>' if (directory / "master.mp4").is_file() else ""
    path.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Video review</title><style>body{margin:0;background:#f8f3eb;color:#25334e;font:16px system-ui;padding:32px;max-width:1300px;margin:auto}h1{font-size:36px}section{background:white;border-radius:16px;padding:20px;margin:20px 0}video{width:100%;max-height:70vh}.frames{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}figure{margin:0}img{width:100%;border-radius:8px}figcaption,small{display:block;padding:8px;color:#596579}.missing{aspect-ratio:16/9;display:grid;place-content:center;background:#edf0f5}a{color:#375a9a}@media(max-width:700px){.frames{grid-template-columns:1fr}body{padding:16px}}</style><h1>' + html.escape(project.data.get("title", project.id)) + '</h1><p>Technical review workspace. Creative approval is recorded separately. ' + f'{project.frames} frames at {project.fps} fps, {project.seconds:.3f}s.</p>' + video + "".join(rows) + '</html>')
    return path


def qa(project: Project, quality: str) -> dict:
    directory = project.output(quality)
    master = directory / "master.mp4"
    if not master.is_file():
        raise PipelineError("No master exists. Assemble the rendered shots first.")
    metadata = probe(master)
    errors, warnings = [], []
    settings = project.settings(quality)
    video = next((s for s in metadata["streams"] if s["codec_type"] == "video"), {})
    audio = [s for s in metadata["streams"] if s["codec_type"] == "audio"]
    for label, expected in (("width", settings["width"]), ("height", settings["height"]), ("nb_read_frames", project.frames)):
        actual = int(video.get(label, -1))
        if actual != expected:
            errors.append(f"{label}: expected {expected}, found {actual}.")
    try:
        fps = float(Fraction(video.get("avg_frame_rate", "0/1")))
    except (ValueError, ZeroDivisionError):
        fps = 0
    if abs(fps - project.fps) > 0.001:
        errors.append(f"Frame rate: expected {project.fps}, found {fps}.")
    duration = float(video.get("duration", metadata.get("format", {}).get("duration", 0)))
    if abs(duration - project.seconds) > 1 / project.fps + 0.002:
        errors.append(f"Duration: expected {project.seconds:.3f}s, found {duration:.3f}s.")
    wanted_audio = bool(project.data.get("audio", {}).get("source"))
    if len(audio) != int(wanted_audio):
        errors.append(f"Expected {int(wanted_audio)} audio stream(s), found {len(audio)}.")
    try:
        master_receipt = json.loads((directory / "master.json").read_text())
        if master_receipt.get("project_identity") != project.identity():
            errors.append("Master was assembled from a different project revision.")
        if master_receipt.get("sha256") != file_hash(master):
            errors.append("Master bytes changed since assembly.")
        current = verify_complete(project, quality)
        if master_receipt.get("shot_fingerprints") != {r["shot_id"]: r["fingerprint"] for r in current}:
            errors.append("Master does not match the current rendered shots.")
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
    report = {"project_id": project.id, "quality": quality, "technical_passed": not errors, "creative_approval": "not_assessed", "errors": errors, "warnings": warnings, "frames": project.frames, "fps": fps, "duration_seconds": duration, "audio_streams": len(audio), "image_samples": metrics, "motion": motion, "master_sha256": file_hash(master), "limitations": ["Automated checks do not assess anatomy, lettering accuracy, musical intention, or artistic quality.", "Brightness samples are warnings, not a creative approval."]}
    write_json(directory / "qa.json", report)
    storyboard(project, quality)
    return report


def scan_motion(project: Project, master: Path) -> dict:
    cut_frames = {shot["start_frame"] for shot in project.shots[1:]}
    longest, current, decoded, total, largest = 0, 0, 0, 0.0, 0.0
    unexpected = []
    # Disk-backed decoding bounds memory even for an entire concert. This file is
    # deleted automatically and never becomes an input or a delivery artifact.
    with tempfile.TemporaryFile() as raw:
        try:
            result = subprocess.run(["ffmpeg", "-v", "error", "-i", str(master), "-vf", "scale=160:90,format=gray", "-f", "rawvideo", "-"], stdout=raw, stderr=subprocess.PIPE, timeout=180)
        except (OSError, subprocess.TimeoutExpired):
            return {"warnings": ["Motion scan could not decode the full movie within its time limit."]}
        if result.returncode or raw.tell() % (160 * 90):
            return {"warnings": ["Motion scan could not decode the full movie."]}
        raw.seek(0)
        previous = None
        while chunk := raw.read(160 * 90):
            frame = np.frombuffer(chunk, np.uint8).astype(np.float32)
            if previous is not None:
                difference = float(np.mean(np.abs(frame - previous))) / 255
                total += difference
                largest = max(largest, difference)
                if difference > 0.25 and decoded not in cut_frames and len(unexpected) < 12:
                    unexpected.append(decoded)
                current = current + 1 if difference < 0.0001 and decoded not in cut_frames else 0
                longest = max(longest, current)
            previous = frame
            decoded += 1
    warnings = []
    if decoded != project.frames:
        warnings.append(f"Motion scan decoded {decoded} frames; expected {project.frames}.")
    if unexpected:
        warnings.append(f"Large changes away from declared cuts at frames {unexpected[:12]}; inspect flash or camera continuity.")
    if longest / project.fps > 1.5:
        warnings.append(f"Nearly frozen interval lasts about {longest / project.fps:.2f}s; confirm this is intentional.")
    return {"decoded_frames": decoded, "mean_frame_difference": round(total / max(1, decoded - 1), 6), "maximum_frame_difference": round(largest, 6), "longest_still_seconds": round(longest / project.fps, 3), "warnings": warnings}
