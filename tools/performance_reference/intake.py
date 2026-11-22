"""Extract timestamp-verified local reference frames without downloading media."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont, ImageOps


VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]
# Playlists and manifests are deliberately excluded: their bytes do not identify
# the dependencies they would open. Also prohibit network protocols at demuxing.
INPUT_OPTIONS = ["-protocol_whitelist", "file", "-format_whitelist",
                 "mov,mp4,m4a,3gp,3g2,mj2,matroska,webm,avi,mpegts,mpeg,flv,ogg,asf,mxf,nut"]
MAX_SOURCE_BYTES = 2 * 1024 ** 3
MAX_SOURCE_SECONDS = 1800
MAX_DECODED_FRAMES = 120000


class IntakeError(ValueError):
    """Invalid input or evidence that cannot be verified."""


def _run(args):
    try:
        result = subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired as exc:
        raise IntakeError(f"{args[0]} exceeded the 300-second command limit; use a shorter local video") from exc
    if result.returncode:
        raise IntakeError(f"{args[0]} failed: {result.stderr[-4000:]}")
    return result


def _hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _seconds(value):
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise IntakeError(f"Not a finite time in seconds: {value!r}") from exc


def _stamp(value):
    value = float(value)
    sign = "-" if value < 0 else ""
    millis = round(abs(value) * 1000)
    hours, rest = divmod(millis, 3600000)
    minutes, rest = divmod(rest, 60000)
    seconds, ms = divmod(rest, 1000)
    return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"


def _check_output(path):
    if path.exists():
        raise IntakeError(f"Refusing to overwrite an existing output directory: {path}")
    # Keep derived media out of tracked code paths, also when this is a worktree.
    if (ROOT / ".git").exists() and path.is_relative_to(ROOT):
        result = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "--quiet", "--", str(path / "manifest.json")],
            capture_output=True, text=True)
        if result.returncode != 0:
            raise IntakeError("Output inside this checkout must be Git-ignored; use work/reference-intake/...")


def _probe(path, assume_square_pixels=False):
    metadata = json.loads(_run([
        "ffprobe", "-v", "error", *INPUT_OPTIONS, "-show_format", "-show_streams", "-of", "json", path,
    ]).stdout)
    videos = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"]
    if not videos:
        raise IntakeError("Input has no video stream")
    stream = videos[0]
    sar = stream.get("sample_aspect_ratio")
    if sar in (None, "N/A", "0:1"):
        if not assume_square_pixels:
            raise IntakeError("Source SAR is unspecified; verify square pixels and use --assume-square-pixels, or supply a corrected copy")
    elif Fraction(sar.replace(":", "/")) != 1:
        raise IntakeError(f"Non-square sample aspect ratio {sar} is unsupported; provide a square-pixel viewing copy")
    declared_duration = stream.get("duration")
    if declared_duration not in (None, "N/A") and _seconds(declared_duration) > MAX_SOURCE_SECONDS:
        raise IntakeError("Reported video duration exceeds 1800 seconds; use a shorter local video")
    time_base = Fraction(stream["time_base"])
    raw = json.loads(_run([
        "ffprobe", "-v", "error", *INPUT_OPTIONS, "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=pts,pts_time,duration,pkt_duration", "-of", "json", path,
    ]).stdout).get("frames", [])
    if not raw:
        raise IntakeError("Video stream has no decoded frames")
    if len(raw) > MAX_DECODED_FRAMES:
        raise IntakeError("Video exceeds 120000 decoded frames; use a shorter local video")
    frames = []
    for index, row in enumerate(raw):
        if row.get("pts") is None:
            raise IntakeError(f"Decoded frame {index} lacks a source PTS; exact timestamp intake is unsupported")
        pts = int(row["pts"])
        timestamp = pts * time_base
        if frames and timestamp < frames[-1]["time"]:
            raise IntakeError("Non-monotonic decoded presentation timestamps require manual inspection")
        duration = row.get("duration", row.get("pkt_duration"))
        frames.append(dict(index=index, pts=pts, time=timestamp,
                           duration=None if duration is None else int(duration) * time_base))
    if frames[-1]["time"] - frames[0]["time"] > MAX_SOURCE_SECONDS:
        raise IntakeError("Decoded video span exceeds 1800 seconds; use a shorter local video")
    return metadata, stream, time_base, frames


def _choose(frames, start, end, count):
    zero = frames[0]["time"]
    eligible = [f for f in frames if start <= f["time"] - zero < end]
    if not eligible:
        raise IntakeError("No decoded frame PTS lies in the requested [start, end) range")
    last = frames[-1]
    known_end = last["time"] - zero + last["duration"] if last["duration"] else None
    if known_end is not None and end > known_end:
        raise IntakeError(f"Requested end exceeds decoded video coverage ({float(known_end):.9f} seconds)")
    if known_end is None and end > last["time"] - zero:
        raise IntakeError("Final frame duration is unknown; requested end exceeds the last proven timestamp")
    # Uniform bin centres avoid selecting an excluded end boundary. Sparse/VFR
    # media can map several targets to one frame; retain every target, emit once.
    chosen = {}
    for i in range(count):
        target = start + (2 * i + 1) * (end - start) / (2 * count)
        frame = min(eligible, key=lambda f: (abs(f["time"] - zero - target), f["index"]))
        chosen.setdefault(frame["index"], dict(frame=frame, targets=[]))["targets"].append(target)
    return [chosen[i] for i in sorted(chosen)], known_end


def _extract(path, output, chosen):
    frames_dir = output / "frames"
    frames_dir.mkdir()
    selection = "+".join(f"eq(n\\,{item['frame']['index']})" for item in chosen)
    command = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "info", "-copyts",
        "-threads", "1", *INPUT_OPTIONS, "-i", path, "-map", "0:v:0", "-an", "-sn", "-dn",
        "-vf", f"select={selection},showinfo", "-fps_mode", "passthrough",
        "-frames:v", str(len(chosen)), "-threads", "1", "-start_number", "0",
        "-compression_level", "3", frames_dir / "frame-%04d.png",
    ]
    result = _run(command)
    (output / "decode.log").write_text(result.stderr)
    tb = re.search(r"config in time_base:\s*(\d+/\d+)", result.stderr)
    decoded = re.findall(r"\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:", result.stderr)
    files = sorted(frames_dir.glob("frame-*.png"))
    if tb is None or len(decoded) != len(chosen) or len(files) != len(chosen):
        raise IntakeError("Decoder frame count or timestamp evidence does not match the selected frames")
    decoded_base = Fraction(tb.group(1))
    for index, ((ordinal, pts), item) in enumerate(zip(decoded, chosen)):
        if int(ordinal) != index or int(pts) * decoded_base != item["frame"]["time"]:
            raise IntakeError("FFmpeg decoded PTS disagrees with the source frame selected by ffprobe")
        item["decoded_pts"] = int(pts)
        item["decoded_time_base"] = str(decoded_base)
    return files, [str(a) for a in command]


def _font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        # Pillow's scalable bundled default is available in current environments.
        try:
            return ImageFont.load_default(size=size)
        except TypeError as exc:
            raise IntakeError("Install DejaVu Sans or use Pillow >= 10.1 for readable timecode text") from exc


def _wrap(text, font, width):
    lines, line = [], ""
    for character in text:
        if line and font.getlength(line + character) > width:
            lines.append(line.rstrip())
            line = ""
        line += character
    return lines + [line]


def _pictures(output, paths, chosen, zero, reference_id, purpose, start, end, columns):
    timecoded = output / "timecoded"
    timecoded.mkdir()
    width, gap, footer = 400, 16, 32
    tile_height = 225 + 76
    columns = min(columns, len(paths))
    rows = (len(paths) + columns - 1) // columns
    sheet_width = columns * (width + gap) + gap
    title = f"{reference_id}" + (" | PIPELINE FIXTURE" if purpose == "pipeline_fixture" else " | REFERENCE INTAKE")
    headings = [(title, 22, "#f3d49b"),
                (f"Requested [{float(start):g}, {float(end):g}) seconds from first video frame", 17, "white"),
                ("Actual source PTS verified | Visual review: pending | Owner approval: unrecorded", 15, "#b8c6da")]
    heading_lines = [(line, size, color) for text, size, color in headings
                     for line in _wrap(text, _font(size), sheet_width - 2 * gap)]
    header = 28 + sum(size + 9 for _, size, _ in heading_lines)
    footer_lines = _wrap("Still samples do not establish motion quality or reconstruct a 3D performance.",
                         _font(15), sheet_width - 2 * gap)
    footer = max(footer, 10 + 20 * len(footer_lines))
    sheet = Image.new("RGB", (sheet_width, header + rows * (tile_height + gap) + footer), "#101724")
    draw = ImageDraw.Draw(sheet)
    heading_y = 14
    for line, size, color in heading_lines:
        draw.text((gap, heading_y), line, font=_font(size), fill=color)
        heading_y += size + 9
    samples = []
    for index, (path, item) in enumerate(zip(paths, chosen)):
        frame = item["frame"]
        relative = frame["time"] - zero
        targets = [float(t) for t in item["targets"]]
        caption1 = f"#{index + 1:02d}  video {_stamp(relative)}  |  source PTS {float(frame['time']):.6f} s"
        caption2 = "target " + ", ".join(f"{t:.3f}" for t in targets) + " s"
        with Image.open(path) as original:
            original.load()
            rgb = original.convert("RGB")
            canvas_width = max(rgb.width, 960)
            label_size = max(15, min(30, round(canvas_width / 65)))
            label_lines = _wrap(caption2, _font(label_size), canvas_width - 24)
            band = max(68, 18 + (len(label_lines) + 1) * (label_size + 6))
            labelled = Image.new("RGB", (canvas_width, rgb.height + band), "#101724")
            labelled.paste(rgb, ((canvas_width - rgb.width) // 2, 0))
            labels = ImageDraw.Draw(labelled)
            labels.text((12, rgb.height + 6), caption1, font=_font(label_size), fill="white")
            for line_index, line in enumerate(label_lines):
                labels.text((12, rgb.height + 12 + label_size + line_index * (label_size + 6)),
                            line, font=_font(label_size), fill="#b8c6da")
            labelled_path = timecoded / path.name
            labelled.save(labelled_path)
            x = gap + (index % columns) * (width + gap)
            y = header + (index // columns) * (tile_height + gap)
            thumb = ImageOps.contain(rgb, (width, 225), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x + (width - thumb.width) // 2, y + (225 - thumb.height) // 2))
            draw.text((x, y + 234), f"#{index + 1:02d}  video {_stamp(relative)}", font=_font(18), fill="white")
            draw.text((x, y + 258), f"source PTS {float(frame['time']):.6f} s", font=_font(16), fill="#f3d49b")
            target_text = caption2 if len(caption2) <= 43 else caption2[:40] + "..."
            draw.text((x, y + 280), target_text, font=_font(15), fill="#b8c6da")
            samples.append({
                "sample_index": index, "decoded_source_frame_index": frame["index"],
                "requested_times_seconds": targets, "actual_video_time_seconds": float(relative),
                "source_pts": frame["pts"], "source_pts_seconds": float(frame["time"]),
                "source_pts_seconds_exact": str(frame["time"]),
                "decoded_pts": item["decoded_pts"], "decoded_time_base": item["decoded_time_base"],
                "frame_path": path.relative_to(output).as_posix(), "frame_sha256": _hash(path),
                "timecoded_path": labelled_path.relative_to(output).as_posix(),
                "timecoded_sha256": _hash(labelled_path), "decoded_width": rgb.width, "decoded_height": rgb.height,
                "annotations": {"shot_id": None, "performer_ids": [], "contact_ids": [], "observations": [], "uncertainties": []},
            })
    for line_index, line in enumerate(footer_lines):
        draw.text((gap, sheet.height - footer + 2 + line_index * 20), line,
                  font=_font(15), fill="#b8c6da")
    sheet_path = output / "contact-sheet.jpg"
    sheet.save(sheet_path, quality=94, subsampling=0)
    return samples, dict(path=sheet_path.name, sha256=_hash(sheet_path), width=sheet.width, height=sheet.height)


def intake(video, source_url, reference_id, start, end, output, *, samples=12, columns=4, purpose="reference",
           assume_square_pixels=False):
    """Create a new intake directory; all requested times use the first-frame clock."""
    video, output = Path(video).resolve(), Path(output).resolve()
    if not video.is_file():
        raise IntakeError(f"Local input video is missing: {video}")
    if video.stat().st_size > MAX_SOURCE_BYTES:
        raise IntakeError("Input exceeds the 2 GiB limit; use a shorter local video")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", reference_id):
        raise IntakeError("Reference ID must be 1 to 80 letters, digits, dots, underscores or hyphens")
    parsed = urlparse(source_url)
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise IntakeError("Record an HTTP(S) source URL; the tool will not fetch it")
    start, end = _seconds(start), _seconds(end)
    if start < 0 or end <= start:
        raise IntakeError("Require 0 <= start < end")
    if not 1 <= samples <= 60 or not 1 <= columns <= 8:
        raise IntakeError("Use 1 to 60 samples and 1 to 8 columns")
    if purpose not in ("reference", "pipeline_fixture"):
        raise IntakeError("Purpose must be reference or pipeline_fixture")
    _check_output(output)
    for executable in ("ffmpeg", "ffprobe"):
        if shutil.which(executable) is None:
            raise IntakeError(f"Required executable is missing: {executable}")
    source_hash = _hash(video)
    metadata, stream, time_base, frames = _probe(video, assume_square_pixels=assume_square_pixels)
    chosen, known_end = _choose(frames, start, end, samples)
    output.mkdir(parents=True, exist_ok=False)
    marker = output / "INTAKE-INCOMPLETE.txt"
    marker.write_text("This intake has not passed technical verification.\n")
    try:
        _json(output / "source-probe.json", metadata)
        paths, command = _extract(video, output, chosen)
        zero = frames[0]["time"]
        sample_rows, sheet = _pictures(output, paths, chosen, zero, reference_id, purpose, start, end, columns)
        if _hash(video) != source_hash:
            raise IntakeError("Input media changed during intake; this result cannot be accepted")
        deltas = [b["time"] - a["time"] for a, b in zip(frames, frames[1:])]
        manifest = {
            "schema_version": 1, "tool": "performance_reference", "tool_version": VERSION,
            "created_at_utc": datetime.now(timezone.utc).isoformat(), "purpose": purpose,
            "reference": {"id": reference_id, "source_url": source_url,
                          "url_to_local_media_identity": "provided_by_caller_not_independently_verified"},
            "acquisition": {"status": "local_media_present", "download_attempted": False,
                            "input_path": str(video), "input_bytes": video.stat().st_size, "input_sha256": source_hash},
            "source": {"selected_stream_index": stream["index"], "time_base": str(time_base),
                       "sample_aspect_ratio": stream.get("sample_aspect_ratio"),
                       "effective_sample_aspect_ratio": "1:1",
                       "pixel_geometry_policy": "signalled_square_pixels" if stream.get("sample_aspect_ratio") not in (None, "N/A", "0:1") else "caller_asserted_square_pixels_for_unspecified_stream",
                       "display_rotation_policy": "normal_ffmpeg_display_rotation_applied",
                       "first_video_pts": frames[0]["pts"], "first_video_pts_seconds": float(zero),
                       "first_video_pts_seconds_exact": str(zero), "decoded_frame_count": len(frames),
                       "last_video_time_seconds": float(frames[-1]["time"] - zero),
                       "known_coverage_end_seconds": None if known_end is None else float(known_end),
                       "proven_request_end_limit_seconds": float(known_end if known_end is not None else frames[-1]["time"] - zero),
                       "observed_frame_interval_min_seconds": float(min(deltas)) if deltas else None,
                       "observed_frame_interval_max_seconds": float(max(deltas)) if deltas else None,
                       "probe_path": "source-probe.json", "probe_sha256": _hash(output / "source-probe.json")},
            "segment": {"clock": "seconds_relative_to_first_decoded_video_frame",
                        "start_seconds": float(start), "end_seconds": float(end),
                        "start_seconds_exact": str(start), "end_seconds_exact": str(end),
                        "interval": "start_inclusive_end_exclusive"},
            "sampling": {"strategy": "uniform_bin_centres_nearest_in_range_pts_ties_choose_earlier_frame",
                         "requested_count": samples, "actual_unique_count": len(sample_rows),
                         "duplicate_policy": "multiple_targets_for_one_frame_are_retained_in_that_sample",
                         "source_decode": "sequential_frame_index_selection_no_approximate_seek_no_fps_resampling"},
            "samples": sample_rows, "contact_sheet": sheet,
            "annotations": {
                "shots": [], "performers": [], "contacts": [], "uncertainties": [],
                "templates": {
                    "shot": {"id": None, "start_seconds": None, "end_seconds": None, "camera": None, "staging": None},
                    "performer": {"id": None, "role": None, "costume": None, "movement_phrase": None},
                    "contact": {"id": None, "performer_ids": [], "start_seconds": None, "end_seconds": None,
                                "body_parts": [], "target": None, "evidence_sample_indices": [], "status": "unreviewed"},
                    "uncertainty": {"sample_indices": [], "question": None, "occluded_or_unobservable": None},
                },
            },
            "review": {
                "technical": {"status": "passed", "checks": ["source_hash_unchanged", "all_samples_in_requested_range",
                              "ffprobe_pts_equal_ffmpeg_decoded_pts", "decoded_png_count_matches_unique_samples"]},
                "visual": {"status": "not_reviewed", "reviewer": None, "reviewed_at": None, "notes": []},
                "owner_approval": {"status": "unrecorded", "approved_by": None, "approved_at": None, "evidence": None},
            },
            "motion_reconstruction": {"status": "not_attempted", "note": "No 3D pose, mocap, choreography or cloth is reconstructed by this tool."},
            "reproduction": {"ffmpeg": _run(["ffmpeg", "-version"]).stdout.splitlines()[0],
                             "ffprobe": _run(["ffprobe", "-version"]).stdout.splitlines()[0],
                             "decode_command": command, "decode_log": "decode.log"},
            "input_policy": {"protocols": ["file"], "containers": INPUT_OPTIONS[-1].split(","),
                             "playlist_or_segmented_inputs": "rejected", "max_source_bytes": MAX_SOURCE_BYTES,
                             "max_source_seconds": MAX_SOURCE_SECONDS, "max_decoded_frames": MAX_DECODED_FRAMES,
                             "command_timeout_seconds": 300},
            "limitations": ["Still samples cannot establish fluid movement; inspect the full requested passage.",
                            "Source URL identity and permission are not verified by possessing a local file.",
                            "PNG and contact sheet are viewing aids, not an HDR or color-mastering reference.",
                            "Subtitle, audio and other video streams are not sampled; stream v:0 is selected."],
        }
        _json(output / "manifest.json", manifest)
        marker.unlink()
        return manifest
    except Exception as exc:
        _json(output / "failure.json", {"status": "failed", "error": str(exc)})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--reference-id", required=True)
    parser.add_argument("--start", required=True, help="Seconds from the first decoded video frame, inclusive")
    parser.add_argument("--end", required=True, help="Seconds from the first decoded video frame, exclusive")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--purpose", choices=("reference", "pipeline_fixture"), default="reference")
    parser.add_argument("--assume-square-pixels", action="store_true",
                        help="Explicitly assert square pixels only when SAR is unspecified; non-square SAR is still rejected")
    args = parser.parse_args(argv)
    try:
        manifest = intake(args.video, args.source_url, args.reference_id, args.start, args.end, args.output,
                          samples=args.samples, columns=args.columns, purpose=args.purpose,
                          assume_square_pixels=args.assume_square_pixels)
    except (IntakeError, OSError) as exc:
        parser.exit(1, f"Reference intake failed: {exc}\n")
    print(json.dumps({"manifest": str(args.output.resolve() / "manifest.json"),
                      "samples": manifest["sampling"]["actual_unique_count"],
                      "technical_status": "passed", "visual_review": "not_reviewed",
                      "owner_approval": "unrecorded"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
