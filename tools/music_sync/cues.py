"""Export section starts from sync.json as engine/live.py CUES and 60 fps cues.csv."""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

from .align import retime
from .analyze import validate_sync_data
from .io import read_json


def seconds_to_timecode(seconds: float, fps: int = 60) -> str:
    """Convert non-negative seconds to HH:MM:SS:FF non-drop-frame timecode."""
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0.0:
        raise ValueError(f"seconds must be a finite non-negative number, got {seconds!r}.")
    if isinstance(fps, bool) or not isinstance(fps, int) or fps <= 0:
        raise ValueError(f"fps must be a positive integer, got {fps!r}.")
    total_frames = int(round(seconds * fps))
    ff = total_frames % fps
    total_seconds = total_frames // fps
    ss = total_seconds % 60
    mm = (total_seconds // 60) % 60
    hh = total_seconds // 3600
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"


def build_cues(
    sync_data: dict[str, Any],
    *,
    tempo_map: dict[str, Any] | None = None,
    loop_sections: bool = False,
) -> list[tuple[str, float, float | None]]:
    """Build an engine/live.py CUES list from validated sync.json data."""
    validate_sync_data(sync_data)
    duration = float(sync_data["duration_seconds"])
    if tempo_map is not None:
        duration = float(retime(duration, tempo_map))

    cues: list[tuple[str, float, float | None]] = []
    for section in sync_data["sections"]:
        name = str(section["name"])
        start = float(section["start"])
        end = float(section["end"])
        if tempo_map is not None:
            start = float(retime(start, tempo_map))
            end = float(retime(end, tempo_map))
        start = max(0.0, round(start, 4))
        if start >= duration:
            continue
        loop_end: float | None = None
        if loop_sections:
            candidate_end = min(round(end, 4), round(duration, 4))
            if candidate_end - start >= 1.0:
                loop_end = candidate_end
        cues.append((name, start, loop_end))

    if not cues:
        cues.append(("Start", 0.0, None))
    return cues


def format_cues_python(
    cues: list[tuple[str, float, float | None]],
    *,
    source_name: str,
    duration_seconds: float,
) -> str:
    """Format a CUES snippet ready for engine/songs/ and engine/live.py."""
    lines = [
        '"""Suggested live section cues exported from music_sync (unverified until reviewed)."""',
        f"# Source: {source_name}",
        "# Paste CUES into a song file in engine/songs/ to step through sections in engine/live.py.",
        f"TOTAL = {round(float(duration_seconds), 4)}",
        "CUES = [",
    ]
    for name, start, loop_end in cues:
        lines.append(f"    ({name!r}, {start!r}, {loop_end!r}),")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def export_cues(
    sync_path: Path,
    out_dir: Path,
    *,
    tempo_map_path: Path | None = None,
    fps: int = 60,
    loop_sections: bool = False,
) -> tuple[Path, Path]:
    """Write cues.py (for engine/live.py) and cues.csv (for QLab, ProPresenter, or Resolume)."""
    sync_path = Path(sync_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sync_data = read_json(sync_path)
    tempo_map = read_json(Path(tempo_map_path)) if tempo_map_path is not None else None
    cues = build_cues(sync_data, tempo_map=tempo_map, loop_sections=loop_sections)

    duration = float(sync_data["duration_seconds"])
    if tempo_map is not None:
        duration = float(retime(duration, tempo_map))

    cues_py = out_dir / "cues.py"
    cues_py.write_text(
        format_cues_python(
            cues,
            source_name=str(sync_data["source"]["filename"]),
            duration_seconds=duration,
        ),
        encoding="utf-8",
    )

    cues_csv = out_dir / "cues.csv"
    tc_header = f"start_timecode_{fps}fps"
    with cues_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["name", "start_seconds", tc_header])
        for name, start, _loop_end in cues:
            writer.writerow([name, f"{start:.4f}", seconds_to_timecode(start, fps=fps)])

    return cues_py, cues_csv
