"""Measure actual scene frames; never confuse estimates with completed movies."""
from __future__ import annotations

import json
import statistics
import time

from .project import PipelineError, Project, write_json
from .render import render, shot_directory


def benchmark(project: Project, qualities: list[str], frames: list[int] | None = None, *, allow_local: bool = False) -> dict:
    selected = frames if frames is not None else sorted({0, (project.frames - 1) // 2, project.frames - 1})
    if not selected or any(f < 0 or f >= project.frames for f in selected):
        raise PipelineError("Benchmark frames must be inside the project timeline.")
    report = {"project": project.id, "fps": project.fps, "selected_frames": selected,
        "scope": "Actual selected frames at each quality; full-film times are rough linear estimates, not completed renders.",
        "cloud_gpu_provider": None, "qualities": {}}
    for quality in qualities:
        settings = project.settings(quality)
        started = time.monotonic()
        # Force only the chosen frames? render force invalidates owned shot caches.
        # Use normal verification so an existing final render is never discarded.
        receipts = render(project, quality, selected=selected, allow_local=allow_local)
        measurements = []
        for shot in project.shots:
            metadata = shot_directory(project, quality, shot) / "frames/renderer.json"
            if metadata.is_file():
                worker = json.loads(metadata.read_text())
                measurements.extend(item["seconds"] for item in worker.get("frame_timings", []) if item["frame"] in selected)
        newly_rendered = sum(item["last_rendered_frames"] for item in receipts)
        median = statistics.median(measurements) if measurements else None
        report["qualities"][quality] = {"settings": settings, "frames_requested": len(selected),
            "frames_newly_rendered": newly_rendered, "frames_reused": len(selected) - newly_rendered,
            "invocation_seconds": round(time.monotonic() - started, 3),
            "available_worker_frame_measurements": len(measurements),
            "median_frame_render_seconds": median,
            "estimated_one_minute_render_hours": round(median * project.fps / 60, 3) if median else None,
            "estimate_note": "Excludes process startup, encoding, storage and harder frames; includes any previous matching cached frame timings."}
    target = project.root / "work/pipeline" / project.id / "benchmark.json"
    write_json(target, report)
    return report
