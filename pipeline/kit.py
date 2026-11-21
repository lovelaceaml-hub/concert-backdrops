"""Explicitly registered concert studies, with shared frame recovery."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import resource
import time

from PIL import Image

from .project import PipelineError, Project, file_hash, read_data, safe_path, write_json


SCENE = "tools/concert_kit/consideration.py"
MODULE = "tools/concert_kit/render.py"
REVISION_SCENE = "tools/concert_motion_revision/render.py"
DANCE_SCENE = "tools/concert_dance/scene.py"
FAN_SCENE = "tools/concert_fan/fan_trio.py"
REGISTERED_SCENES = {
    SCENE: {"id": "consideration-v1", "module": MODULE, "seconds": 18,
            "fps": 60, "source_start_frame": 0, "cut_frames": (180, 720)},
    REVISION_SCENE: {"id": "consideration-v2", "module": REVISION_SCENE,
                     "seconds": 15, "fps": 60, "source_start_frame": 180,
                     "cut_frames": (234, 540)},
    DANCE_SCENE: {"id": "natural-dance-v1", "module": "tools/concert_dance/render.py",
                  "seconds": 18, "fps": 60, "source_start_frame": 0,
                  "cut_frames": ()},
    FAN_SCENE: {"id": "fan-silk-trio-v1", "module": "tools/concert_fan/render.py",
                "seconds": 20, "fps": 60, "source_start_frame": 0,
                "cut_frames": ()},
}


def scene_spec(scene: str) -> dict:
    try:
        return REGISTERED_SCENES[scene]
    except KeyError as exc:
        raise PipelineError(f"p3d-kit scene is not registered: {scene}") from exc


def project_scene(project: Project) -> str:
    scenes = {shot["scene"] for shot in project.shots}
    if len(scenes) != 1:
        raise PipelineError("Registered kit studies require a separate project for each authored scene clock.")
    scene = next(iter(scenes))
    scene_spec(scene)
    return scene


def scene_module(root: Path, scene: str = SCENE):
    definition = scene_spec(scene)
    spec = importlib.util.spec_from_file_location(
        definition["module"][:-3].replace("/", "."), safe_path(root, definition["module"]))
    if spec is None or spec.loader is None:
        raise PipelineError("The concert kit renderer is missing.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_shot(project: Project, shot: dict) -> None:
    spec = scene_spec(shot["scene"])
    project_scene(project)
    if shot.get("params", {}):
        raise PipelineError("Registered kit studies require empty params; author a new scene for changed action or cameras.")
    if project.fps != spec["fps"] or shot["end_frame_exclusive"] > spec["seconds"] * spec["fps"]:
        raise PipelineError(f"The registered {spec['id']} study covers {spec['seconds']} seconds at native {spec['fps']} fps.")
    if project.data.get("delivery", {}).get("source_transfer") != "legacy_display_gamma":
        raise PipelineError("The concert kit requires its legacy_display_gamma delivery convention.")
    for name, preset in project.data["quality"].items():
        if preset["width"] * 9 != preset["height"] * 16 or min(preset["width"], preset["height"]) < 32:
            raise PipelineError(f"quality.{name}: the concert composition requires 16:9 dimensions of at least 32 pixels.")


def module_contract(module, scene: str) -> dict:
    """Reject a changed clock before creating a render context or using caches."""
    spec = scene_spec(scene)
    actual_cuts = tuple(round(float(cut) * spec["fps"], 6) for cut in getattr(module, "CUTS", ()))
    if (getattr(module, "FPS", None) != spec["fps"]
            or getattr(module, "DURATION", None) != spec["seconds"]
            or getattr(module, "SOURCE_START", 0) != spec["source_start_frame"] / spec["fps"]
            or actual_cuts != spec["cut_frames"]):
        raise PipelineError(f"The {spec['id']} module clock or cuts changed; review its explicit scene registration.")
    if module.COLOR_CONTRACT.get("name") != "legacy_display_gamma":
        raise PipelineError("The concert kit color convention changed; review the adapter before rendering.")
    return {"id": spec["id"], "module": spec["module"], "fps": spec["fps"],
            "duration_seconds": spec["seconds"], "output_frame_count": spec["seconds"] * spec["fps"],
            "source_start_frame": spec["source_start_frame"], "cut_frames": list(spec["cut_frames"])}


def source_identity(root: Path, scene: str = SCENE) -> dict[str, str]:
    fonts = root / "fonts"
    if not fonts.is_dir() or not fonts.resolve().is_relative_to(root.resolve()):
        raise PipelineError("Install fonts inside this checkout before using the registered concert kit.")
    if "P3D_BODY_ASSET" in os.environ:
        raise PipelineError("Unset P3D_BODY_ASSET to use the concert kit's declared body asset.")
    module = scene_module(root, scene)
    module_contract(module, scene)
    if module.fonts_path() != fonts.resolve():
        raise PipelineError("Unset CONCERT_KIT_FONTS or point it to this checkout's fonts directory.")
    try:
        hashes = module.source_hashes()
    except (RuntimeError, OSError) as exc:
        raise PipelineError(f"Cannot verify {scene_spec(scene)['id']} source: {exc}") from exc
    for name, digest in hashes.items():
        if file_hash(safe_path(root, name)) != digest:
            raise PipelineError(f"Concert source identity disagrees with actual bytes: {name}")
    if "assets/p3d/body_v1.npz" not in hashes:
        raise PipelineError("The concert kit body asset must be present in its source identity.")
    if scene_spec(scene)["module"] not in hashes:
        raise PipelineError("The registered renderer module must be present in its source identity.")
    return hashes


def prepare(project: Project) -> dict:
    for shot in project.shots:
        validate_shot(project, shot)
    scene = project_scene(project)
    identity = {"scene": scene_spec(scene)["id"],
                "clock": module_contract(scene_module(project.root, scene), scene),
                "source_sha256": source_identity(project.root, scene),
                "music_response": "The scene uses its authored visual clock; attaching audio does not infer new musical cues."}
    write_json(project.root / "work/pipeline" / project.id / "preparation.json", identity)
    return identity


def dependency_files(project: Project) -> list[Path]:
    names = set(source_identity(project.root, project_scene(project))) | {"pipeline/kit.py"}
    return [safe_path(project.root, name) for name in sorted(names)]


def render_job(job: dict) -> None:
    root = Path(job["repo_root"]).resolve()
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise PipelineError("Start Python workers with PYTHONHASHSEED=0.")
    scene = job["shot"]["scene"]
    spec = scene_spec(scene)
    if job["video"]["fps"] != spec["fps"] or job["shot"].get("params", {}):
        raise PipelineError("The render job does not match a registered kit scene.")
    start, end = job["shot"]["start_frame"], job["shot"]["end_frame_exclusive"]
    if not 0 <= start < end <= spec["seconds"] * spec["fps"]:
        raise PipelineError("The render shot is outside its registered scene clock.")
    if any(type(frame) is not int or not start <= frame < end for frame in job["frames"]):
        raise PipelineError("The requested frame is outside its registered shot clock.")
    samples = job.get("temporal_samples")
    if type(samples) is not int or not 1 <= samples <= 4:
        raise PipelineError("temporal_samples must be an integer from 1 to 4.")
    source_identity(root, scene)
    module = scene_module(root, scene)
    began = time.monotonic()
    renderer = module.make_renderer(job["video"]["width"], job["video"]["height"], temporal_samples=samples, fps=spec["fps"])
    initialized = time.monotonic()
    output = Path(job["out_dir"])
    output.mkdir(parents=True, exist_ok=True)
    for frame in job["frames"]:
        if Path(job["stop_file"]).exists():
            raise PipelineError("Production stopped between frames. Completed frames remain reusable.")
        # The module owns its registered source offset. Pass the global output
        # index unchanged so neither a new shot nor a resumed batch resets time.
        data = module.frame(renderer, frame, fps=spec["fps"])
        temporary = output / f"frame_{frame:06d}.partial.png"
        Image.frombytes("RGB", (renderer.w, renderer.h), data).save(temporary)
        temporary.replace(output / f"frame_{frame:06d}.png")
        print(f"concert kit frame {frame}, temporal samples {samples}", flush=True)
    print(json.dumps({"event": "worker_complete", "frames": len(job["frames"]),
                      "initialization_seconds": round(initialized - began, 3),
                      "frame_seconds": round(time.monotonic() - initialized, 3),
                      "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}),
          flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    render_job(read_data(parser.parse_args().job))


if __name__ == "__main__":
    main()
