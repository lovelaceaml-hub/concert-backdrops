"""Read-only checks of completed cloth at the exact final render clock.

No missing costume is simulated. The audit inspects every stored 30 Hz state,
then reads the renderer's linear interpolation at every 60 Hz output time and
backward shutter sample, including camera cuts and score boundary probes.
Geometric authoring tolerances are separate from visual review and physical
textile validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from .cache import ROOT, load_cloth, motion_key
from .costume import audit_cloth, make_body
from .qa import _boundaries, sample_times
from .render import cut_times, source_hashes
from .scene import CAST_POINTS, PLACEMENTS, SOLO_PLACEMENT, SOLO_POINTS
from .score import install


def _digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".partial.json")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def audit_rendered_cloth(body, *, fps=60, temporal_samples=2, shutter=.35,
                         include_rows=True):
    """Inspect the complete current-source cache without advancing physics.

    The unchanged 15% p99 and 35% maximum extension limits come from the costume
    audit. Interpolation uses ClothSystem.positions itself, including its
    pre-start clamp, instead of an independent approximation of the renderer.
    """
    key = motion_key(body)
    if not load_cloth(body):
        raise FileNotFoundError("Complete the declared costume bake first: " + key)
    path = Path(body.advanced_cloth_cache)
    cache_hash = body.advanced_cloth_receipt["sha256"]
    if _digest(path) != cache_hash:
        raise RuntimeError("Cached cloth bytes changed after verified loading")
    report = audit_cloth(body)
    snapshot_status = report["status"]
    system = body.cloth
    score = body.actor.advanced_score
    cuts = cut_times(score.mode)
    times, output_times = sample_times(score.duration, fps, temporal_samples,
                                      shutter, _boundaries(score), cuts)
    original_steps, original_snapshots = system.steps, len(system.snaps)
    samples, failures = [], []
    limits = report["limits"]
    for t in times:
        positions = system.positions(float(t))
        if positions.shape != (system.n, 3) or not np.isfinite(positions).all():
            failures.append({"time_seconds": float(t),
                             "reason": "nonfinite or invalid interpolated cloth state"})
            continue
        extension = np.maximum(system._stretch(positions) - 1., 0.)
        row = {"time_seconds": float(t),
               "p99_edge_extension": float(np.percentile(extension, 99)),
               "maximum_edge_extension": float(extension.max()),
               "minimum_height_m": float(positions[:, 1].min())}
        samples.append(row)
        if (row["p99_edge_extension"] > limits["p99_edge_extension"]
                or row["maximum_edge_extension"] > limits["maximum_edge_extension"]
                or row["minimum_height_m"] < limits["minimum_height_m"]):
            failures.append(row)
    if system.steps != original_steps or len(system.snaps) != original_snapshots:
        raise RuntimeError("A read-only cloth audit must not advance the simulation")
    if motion_key(body) != key or _digest(path) != cache_hash:
        raise RuntimeError("Cloth source or cached bytes changed during the audit")

    rendered = {
        "status": "passed" if not failures else "review_required",
        "scope": "Every output frame plus the exact backward shutter clock, camera-cut clamp, endpoint and declared score boundary probes; direct cached ClothSystem.positions interpolation.",
        "sample_schedule": "tools.advanced_dance.qa.sample_times",
        "sample_count": len(times), "valid_sample_count": len(samples),
        "output_frame_count": len(output_times), "fps": int(fps),
        "temporal_samples": int(temporal_samples), "shutter_fraction": float(shutter),
        "cuts_seconds": list(cuts),
        "time_range_seconds": [float(times[0]), float(times[-1])],
        "maximum_p99_extension": max((v["p99_edge_extension"] for v in samples), default=None),
        "maximum_extension": max((v["maximum_edge_extension"] for v in samples), default=None),
        "minimum_height_m": min((v["minimum_height_m"] for v in samples), default=None),
        "failure_count": len(failures), "failures": failures,
        "new_physics_steps": 0,
    }
    if include_rows:
        rendered["samples"] = samples
    else:
        report.pop("samples", None)
    report.update(
        schema_version=1, snapshot_status=snapshot_status,
        status="passed" if snapshot_status == "passed" and not failures else "review_required",
        mode=score.mode, role=score.role, motion_key=key,
        cache_file=str(path), cache_sha256=cache_hash,
        rendered_interpolations=rendered,
        actor={"height_m": body.rig.height, "build": body.rig.build,
               "origin": body.actor.origin.tolist(), "seed": body.seed},
        costume=body.advanced_costume,
        owner_approval=False,
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("all", "solo", "ensemble"), default="all")
    parser.add_argument("--role", type=int, help="One ensemble role, 0 through 4")
    parser.add_argument("--out", type=Path, default=ROOT / "work/advanced-dance/cloth-qa/final")
    parser.add_argument("--allow-missing", action="store_true",
                        help="Report incomplete caches while bakes run; never simulate them")
    parser.add_argument("--summary-only", action="store_true", help="Omit per-time rows")
    args = parser.parse_args()
    if args.role is not None and (args.mode != "ensemble" or not 0 <= args.role < len(PLACEMENTS)):
        parser.error("--role requires --mode ensemble and a role from 0 through 4")
    selected = []
    if args.mode in ("all", "solo"):
        selected.append((False, 0))
    if args.mode in ("all", "ensemble"):
        selected.extend((True, role) for role in
                        (range(len(PLACEMENTS)) if args.role is None else (args.role,)))

    picture_sources = source_hashes()
    audit_sources = {str(path.relative_to(ROOT)): _digest(path) for path in
                     (Path(__file__).resolve(), ROOT / "tools/advanced_dance/qa.py")}
    results = []
    for ensemble, role in selected:
        mode = "ensemble" if ensemble else "solo"
        label = mode + str(role)
        body = make_body(at=PLACEMENTS[role] if ensemble else SOLO_PLACEMENT,
                         role=role, ensemble=ensemble,
                         points=CAST_POINTS[role] if ensemble else SOLO_POINTS)
        install(body, ensemble=ensemble, role=role)
        try:
            report = audit_rendered_cloth(body, include_rows=not args.summary_only)
        except FileNotFoundError as error:
            result = {"label": label, "status": "not_yet_baked", "motion_key": motion_key(body),
                      "reason": str(error)}
            results.append(result)
            print(json.dumps(result), flush=True)
            continue
        report["source_hashes"] = picture_sources
        report["audit_source_hashes"] = audit_sources
        destination = args.out / (label + ".json")
        _write_json(destination, report)
        rendered = report["rendered_interpolations"]
        result = {"label": label, "status": report["status"], "report": str(destination),
                  "cache_sha256": report["cache_sha256"],
                  "snapshot_count": report["snapshot_count"],
                  "snapshot_failure_count": report["failure_count"],
                  "snapshot_maximum_p99_extension": report["maximum_p99_extension"],
                  "snapshot_maximum_extension": report["maximum_extension"],
                  "render_sample_count": rendered["sample_count"],
                  "render_failure_count": rendered["failure_count"],
                  "render_maximum_p99_extension": rendered["maximum_p99_extension"],
                  "render_maximum_extension": rendered["maximum_extension"],
                  "minimum_height_m": min((value for value in
                       (report["minimum_height_m"], rendered["minimum_height_m"])
                       if value is not None), default=None)}
        results.append(result)
        print(json.dumps(result), flush=True)
    if source_hashes() != picture_sources or any(_digest(ROOT / name) != value
                                                for name, value in audit_sources.items()):
        raise RuntimeError("Source files changed during the completed cloth audit")
    missing = [r for r in results if r["status"] == "not_yet_baked"]
    failed = [r for r in results if r["status"] == "review_required"]
    status = "review_required" if failed else ("incomplete" if missing else "passed")
    summary = {"schema_version": 1, "status": status, "requested_performers": len(selected),
               "completed_performers": len(results) - len(missing), "performers": results,
               "source_hashes": picture_sources, "audit_source_hashes": audit_sources,
               "owner_approval": False,
               "limitations": ["Geometric authoring checks, not physical textile certification.",
                               "Cloth self-collision and interaction between performers are not simulated.",
                               "Continuous native motion and encoded-film review remain separate."]}
    _write_json(args.out / "summary.json", summary)
    print(json.dumps({"status": status, "summary": str(args.out / "summary.json")}), flush=True)
    return int(bool(failed or (missing and not args.allow_missing)))


if __name__ == "__main__":
    raise SystemExit(main())
