"""Bounded-memory motion and flicker inspection of the actual delivered movie.

Pixel changes are review heuristics. They do not measure a camera's physical
velocity, acceleration, anatomical correctness, or musical intention.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np

from .project import Project


def temporal_exclusions(project: Project) -> list[dict]:
    """Cuts and explicitly declared flashes must not become continuity defects."""
    intervals = [
        {"start_frame": max(0, shot["start_frame"] - 2),
         "end_frame_exclusive": min(project.frames, shot["start_frame"] + 3), "reason": "shot_cut"}
        for shot in project.shots[1:]
    ]
    for event in project.related_data("timing").get("events", []):
        if event.get("kind") not in ("flash", "intentional_flash"):
            continue
        frame = int(event["frame"])
        attack = event.get("attack_frames", 0)
        release = event.get("release_frames", 0)
        attack = attack if type(attack) is int and attack >= 0 else 0
        release = release if type(release) is int and release >= 0 else 0
        intervals.append({"start_frame": max(0, frame - attack - 2),
                          "end_frame_exclusive": min(project.frames, frame + release + 3), "reason": "declared_flash"})
    return intervals


def scan_motion(project: Project, master: Path) -> dict:
    exclusions = temporal_exclusions(project)
    excluded_frames = set()
    for interval in exclusions:
        excluded_frames.update(range(interval["start_frame"], interval["end_frame_exclusive"]))
    cut_frames = {shot["start_frame"] for shot in project.shots[1:]}
    longest, current, decoded = 0, 0, 0
    total, largest, second_total, second_largest = 0.0, 0.0, 0.0, 0.0
    unexpected, flicker, shimmer = [], [], []
    flicker_count, shimmer_count = 0, 0
    windows: dict[int, dict] = {}
    # Disk-backed decoding bounds resident memory. At 160x90, even ten minutes
    # at 60 fps occupies about 519 MB temporarily, then is removed automatically.
    with tempfile.TemporaryFile() as raw:
        try:
            result = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", str(master), "-map", "0:v:0", "-an",
                 "-vf", "scale=160:90,format=gray", "-fps_mode", "passthrough", "-f", "rawvideo", "-"],
                stdout=raw, stderr=subprocess.PIPE, timeout=max(180, project.seconds * 6),
            )
        except (OSError, subprocess.TimeoutExpired):
            return {"warnings": ["Motion scan could not decode the full movie within its time limit."], "scan_complete": False}
        if result.returncode or raw.tell() % (160 * 90):
            return {"warnings": ["Motion scan could not decode the full movie."], "scan_complete": False}
        raw.seek(0)
        previous, before_previous = None, None
        while chunk := raw.read(160 * 90):
            frame = np.frombuffer(chunk, np.uint8).astype(np.float32) / 255
            if previous is not None:
                difference = float(np.mean(np.abs(frame - previous)))
                total += difference
                largest = max(largest, difference)
                excluded = decoded in excluded_frames
                if difference > 0.25 and not excluded and len(unexpected) < 12:
                    unexpected.append(decoded)
                current = current + 1 if difference < 0.0001 and decoded not in cut_frames else 0
                longest = max(longest, current)
                window_index = int((decoded / project.fps) / 0.5)
                window = windows.setdefault(window_index, {"count": 0, "difference": 0.0, "second_difference": 0.0, "largest_difference": 0.0})
                window["count"] += 1
                window["difference"] += difference
                window["largest_difference"] = max(window["largest_difference"], difference)
                if before_previous is not None:
                    first_delta = previous - before_previous
                    second_delta = frame - previous
                    residual = float(np.mean(np.abs(second_delta - first_delta)))
                    second_total += residual
                    second_largest = max(second_largest, residual)
                    window["second_difference"] += residual
                    # A single rising or falling exposure ramp is not flicker.
                    # Require a real reversal across both adjacent frame pairs.
                    mean_first, mean_second = float(np.mean(first_delta)), float(np.mean(second_delta))
                    strength = min(abs(mean_first), abs(mean_second))
                    centered = decoded - 1
                    triplet_excluded = excluded or centered in excluded_frames or decoded - 2 in excluded_frames
                    if not triplet_excluded and mean_first * mean_second < 0 and strength > 0.025:
                        flicker_count += 1
                        flicker.append({"frame": centered, "seconds": round(centered / project.fps, 6), "luma_reversal": round(strength, 6)})
                        flicker = sorted(flicker, key=lambda item: item["luma_reversal"], reverse=True)[:12]
                    reversing = (first_delta * second_delta < 0) & (np.abs(first_delta) > 0.04) & (np.abs(second_delta) > 0.04)
                    reversing_fraction = float(np.mean(reversing))
                    spatial_strength = float(np.mean(np.minimum(np.abs(first_delta), np.abs(second_delta)) * reversing))
                    if not triplet_excluded and spatial_strength > 0.02 and reversing_fraction > 0.05:
                        shimmer_count += 1
                        shimmer.append({"frame": centered, "seconds": round(centered / project.fps, 6),
                                        "pixel_reversal": round(spatial_strength, 6), "reversing_fraction": round(reversing_fraction, 6)})
                        shimmer = sorted(shimmer, key=lambda item: item["pixel_reversal"], reverse=True)[:12]
            before_previous, previous = previous, frame
            decoded += 1
    warnings = []
    if decoded != project.frames:
        warnings.append(f"Motion scan decoded {decoded} frames; expected {project.frames}.")
    if unexpected:
        warnings.append(f"Large changes away from declared cuts/flashes at frames {unexpected}; inspect flash or camera continuity.")
    if flicker_count:
        warnings.append(f"Global brightness reversals in {flicker_count} frame triplets; inspect possible flicker at frames {[item['frame'] for item in flicker]}.")
    if shimmer_count:
        warnings.append(f"Repeated pixel reversals in {shimmer_count} frame triplets; inspect possible shimmer or strobing at frames {[item['frame'] for item in shimmer]}.")
    if longest / project.fps > 1.5:
        warnings.append(f"Nearly frozen interval lasts about {longest / project.fps:.2f}s; confirm this is intentional.")
    window_metrics = [
        {"start_seconds": index * 0.5, "sample_pairs": item["count"],
         "mean_frame_difference": round(item["difference"] / item["count"], 6),
         "maximum_frame_difference": round(item["largest_difference"], 6),
         "mean_second_difference": round(item["second_difference"] / item["count"], 6)}
        for index, item in sorted(windows.items())
    ]
    return {
        "scan_complete": decoded == project.frames, "decoded_frames": decoded,
        "mean_frame_difference": round(total / max(1, decoded - 1), 6), "maximum_frame_difference": round(largest, 6),
        "mean_second_difference": round(second_total / max(1, decoded - 2), 6), "maximum_second_difference": round(second_largest, 6),
        "longest_still_seconds": round(longest / project.fps, 3), "half_second_windows": window_metrics,
        "flicker_candidate_count": flicker_count, "flicker_candidates": flicker,
        "shimmer_candidate_count": shimmer_count, "shimmer_candidates": shimmer,
        "excluded_intervals": exclusions, "warnings": warnings,
        "interpretation": "Pixel heuristics for review, not measurements of physical camera jerk or proof of natural movement.",
    }
