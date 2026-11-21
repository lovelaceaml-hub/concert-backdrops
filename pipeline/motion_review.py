"""Inspect authored camera motion in world units before spending render time."""
from __future__ import annotations

import math

from .motion import CameraTrack
from .project import Project, write_json


def magnitude(value):
    return math.sqrt(sum(component * component for component in value))


def motion_review(project: Project) -> dict:
    report = {"project_id": project.id, "fps": project.fps, "shots": [], "warnings": [],
        "scope": "Authored camera paths only. Units follow the scene, metres in the supplied Blender study. This does not approve anatomy or visual quality."}
    for shot in project.shots:
        spec = shot.get("params", {}).get("camera_path")
        if not spec:
            report["shots"].append({"shot_id": shot["id"], "status": "no_explicit_camera_path"})
            continue
        duration = (shot["end_frame_exclusive"] - shot["start_frame"]) / project.fps
        spec = dict(spec)
        count = len(spec["points"])
        spec.setdefault("seconds", [duration * i / (count - 1) for i in range(count)])
        spec.setdefault("targets", [[0, 2.2, -1.3]] if shot["renderer"] == "threejs" else [[0, 0, 0]])
        track = CameraTrack.from_dict(spec)
        # Two samples per output frame also inspect intervals between frames.
        step = 1 / (2 * project.fps)
        values = [track.sample(i * step) for i in range(round(duration / step) + 1)]
        speed = [magnitude(value.velocity) for value in values]
        acceleration = [magnitude(value.acceleration) for value in values]
        jerk = [magnitude(tuple((b - a) / step for a, b in zip(first.acceleration, second.acceleration))) for first, second in zip(values, values[1:])]
        separation = [magnitude(tuple(b - a for a, b in zip(value.position, value.target))) for value in values]
        limits = {"speed": 5.0, "acceleration": 8.0, "jerk": 80.0, **shot.get("params", {}).get("motion_limits", {})}
        maxima = {"speed": max(speed), "acceleration": max(acceleration), "jerk": max(jerk, default=0)}
        warnings = [f"{name} reaches {value:.3f}, above the review threshold {limits[name]:.3f}." for name, value in maxima.items() if value > limits[name]]
        if min(separation) < .05:
            warnings.append("Camera nearly intersects its look target; inspect orientation stability.")
        item = {"shot_id": shot["id"], "status": "sampled", "samples": len(values),
                "maximum_speed_units_per_second": maxima["speed"],
                "maximum_acceleration_units_per_second_squared": maxima["acceleration"],
                "maximum_sampled_jerk_units_per_second_cubed": maxima["jerk"],
                "endpoint_speeds": [speed[0], speed[-1]], "minimum_target_distance": min(separation),
                "easing": spec.get("easing", "linear"), "warnings": warnings}
        report["shots"].append(item)
        report["warnings"].extend(f"{shot['id']}: {warning}" for warning in warnings)
    write_json(project.root / "work/pipeline" / project.id / "motion-review.json", report)
    return report
