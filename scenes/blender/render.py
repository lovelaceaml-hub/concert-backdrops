"""Blender background worker. Takes the shared JSON job after Blender's --."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time

import bpy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", type=Path, required=True)
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    job_path = parser.parse_args(arguments).job.resolve()
    job = json.loads(job_path.read_text())
    if platform.system() == "Darwin" and not job.get("allow_local_render", False):
        raise RuntimeError("Mac rendering is disabled. Use the pipeline's explicit local-render opt-in.")
    root = Path(job["repo_root"]).resolve()
    scene_path = (root / job["shot"]["scene"]).resolve()
    if not scene_path.is_relative_to(root) or scene_path.suffix != ".py" or not scene_path.is_file():
        raise ValueError("Blender scene must be an existing Python scene inside the repository.")
    output = Path(job["out_dir"]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    frames = job["frames"]
    if not frames or any(type(frame) is not int or frame < 0 for frame in frames):
        raise ValueError("frames must be a nonempty list of nonnegative integers")
    specification = importlib.util.spec_from_file_location("pipeline_blender_scene", scene_path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    update = module.build_scene(job)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.render.resolution_x = int(job["video"]["width"])
    scene.render.resolution_y = int(job["video"]["height"])
    scene.render.resolution_percentage = 100
    scene.render.fps = int(job["video"]["fps"])
    scene.render.fps_base = 1
    scene.render.threads_mode = "FIXED"
    scene.render.threads = max(1, int(job.get("threads", 4)))
    started = time.monotonic()
    for frame in frames:
        scene.frame_set(frame + 1)
        update(frame)
        temporary = output / f"frame_{frame:06d}.partial.png"
        scene.render.filepath = str(temporary)
        bpy.ops.render.render(write_still=True)
        os.replace(temporary, output / f"frame_{frame:06d}.png")
        print(json.dumps({"event": "frame", "renderer": "blender", "frame": frame}), flush=True)
    receipt = {"renderer": "blender", "version": bpy.app.version_string, "engine": "CYCLES", "device": "CPU", "frames": frames, "elapsed_seconds": round(time.monotonic() - started, 3), "view_transform": scene.view_settings.view_transform, "exposure": scene.view_settings.exposure}
    (output / "renderer.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
