"""Registered current-engine concert model study, with shared frame recovery."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path

from PIL import Image

from .project import PipelineError, Project, file_hash, read_data, safe_path, write_json


SCENE = "tools/concert_kit/consideration.py"
MODULE = "tools/concert_kit/render.py"
REGISTERED_SCENES = {SCENE: {"id": "consideration-v1", "seconds": 18, "fps": 60}}


def scene_module(root: Path):
    spec = importlib.util.spec_from_file_location("pipeline_concert_kit", root / MODULE)
    if spec is None or spec.loader is None:
        raise PipelineError("The concert kit renderer is missing.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_shot(project: Project, shot: dict) -> None:
    spec = REGISTERED_SCENES.get(shot["scene"])
    if spec is None or shot.get("params", {}):
        raise PipelineError("p3d-kit currently accepts the registered Consideration scene with empty params.")
    if project.fps != spec["fps"] or shot["end_frame_exclusive"] > spec["seconds"] * spec["fps"]:
        raise PipelineError("The registered Consideration study covers 18 seconds at native 60 fps.")
    if project.data.get("delivery", {}).get("source_transfer") != "legacy_display_gamma":
        raise PipelineError("The concert kit requires its legacy_display_gamma delivery convention.")
    for name, preset in project.data["quality"].items():
        if preset["width"] * 9 != preset["height"] * 16 or min(preset["width"], preset["height"]) < 32:
            raise PipelineError(f"quality.{name}: the concert composition requires 16:9 dimensions of at least 32 pixels.")


def source_identity(root: Path) -> dict[str, str]:
    module = scene_module(root)
    fonts = root / "fonts"
    if not fonts.is_dir() or not fonts.resolve().is_relative_to(root.resolve()):
        raise PipelineError("Install fonts inside this checkout before using the registered concert kit.")
    if module.fonts_path() != fonts.resolve():
        raise PipelineError("Unset CONCERT_KIT_FONTS or point it to this checkout's fonts directory.")
    if "P3D_BODY_ASSET" in os.environ:
        raise PipelineError("Unset P3D_BODY_ASSET to use the concert kit's declared body asset.")
    if module.COLOR_CONTRACT.get("name") != "legacy_display_gamma":
        raise PipelineError("The concert kit color convention changed; review the adapter before rendering.")
    hashes = module.source_hashes()
    for name, digest in hashes.items():
        if file_hash(safe_path(root, name)) != digest:
            raise PipelineError(f"Concert source identity disagrees with actual bytes: {name}")
    if "assets/p3d/body_v1.npz" not in hashes:
        raise PipelineError("The concert kit body asset must be present in its source identity.")
    return hashes


def prepare(project: Project) -> dict:
    for shot in project.shots:
        validate_shot(project, shot)
    identity = {"scene": REGISTERED_SCENES[SCENE]["id"], "source_sha256": source_identity(project.root),
                "music_response": "The scene uses its authored visual clock; attaching audio does not infer new musical cues."}
    write_json(project.root / "work/pipeline" / project.id / "preparation.json", identity)
    return identity


def dependency_files(project: Project) -> list[Path]:
    names = set(source_identity(project.root)) | {"pipeline/kit.py"}
    return [safe_path(project.root, name) for name in sorted(names)]


def render_job(job: dict) -> None:
    root = Path(job["repo_root"]).resolve()
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise PipelineError("Start Python workers with PYTHONHASHSEED=0.")
    if job["shot"]["scene"] not in REGISTERED_SCENES or job["video"]["fps"] != 60:
        raise PipelineError("The render job does not match a registered kit scene.")
    samples = job.get("temporal_samples")
    if type(samples) is not int or not 1 <= samples <= 4:
        raise PipelineError("temporal_samples must be an integer from 1 to 4.")
    source_identity(root)
    module = scene_module(root)
    renderer = module.make_renderer(job["video"]["width"], job["video"]["height"], temporal_samples=samples, fps=60)
    output = Path(job["out_dir"])
    output.mkdir(parents=True, exist_ok=True)
    for frame in job["frames"]:
        if Path(job["stop_file"]).exists():
            raise PipelineError("Production stopped between frames. Completed frames remain reusable.")
        data = module.frame(renderer, frame, fps=60)
        temporary = output / f"frame_{frame:06d}.partial.png"
        Image.frombytes("RGB", (renderer.w, renderer.h), data).save(temporary)
        temporary.replace(output / f"frame_{frame:06d}.png")
        print(f"concert kit frame {frame}, temporal samples {samples}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    render_job(read_data(parser.parse_args().job))


if __name__ == "__main__":
    main()
