"""Blender background worker. Takes the shared JSON job after Blender's --."""
import argparse
import importlib.util
import hashlib
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
    sys.path.insert(0, str(root))
    def check_sources():
        for name, expected in job.get("source_inputs", {}).items():
            path = (root / name).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise RuntimeError("A render source is missing or outside this repository.")
            with path.open("rb") as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            if actual != expected:
                raise RuntimeError("Source changed during rendering. Freeze the round and restart the render command.")
    check_sources()
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
    blur = job.get("motion_blur", {})
    if blur.get("enabled", False) and not getattr(module, "SUPPORTS_BAKED_MOTION_BLUR", False):
        raise ValueError("This scene does not declare baked subframe motion. Use a compatible scene or disable motion_blur.")
    update = module.build_scene(job)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    if hasattr(scene.render, "compositor_device"):
        scene.render.compositor_device = "CPU"
    if hasattr(scene.render, "compositor_denoise_device"):
        scene.render.compositor_denoise_device = "CPU"
    scene.render.resolution_x = int(job["video"]["width"])
    scene.render.resolution_y = int(job["video"]["height"])
    scene.render.resolution_percentage = 100
    scene.render.fps = int(job["video"]["fps"])
    scene.render.fps_base = 1
    scene.render.threads_mode = "FIXED"
    scene.render.threads = max(1, int(job.get("threads", 4)))
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = str(job.get("image_bit_depth", 8))
    scene.render.use_motion_blur = bool(blur.get("enabled", False))
    scene.render.motion_blur_shutter = float(blur.get("shutter", .5))
    scene.render.motion_blur_position = "CENTER"
    if scene.render.use_motion_blur and not scene.get("pipeline_motion_baked", False):
        raise ValueError("Scene declared motion blur support but did not complete its animation bake.")
    started = time.monotonic()
    timings = []
    for frame in frames:
        frame_start = time.monotonic()
        scene.frame_set(frame + 1)
        update(frame)
        temporary = output / f"frame_{frame:06d}.partial.png"
        scene.render.filepath = str(temporary)
        bpy.ops.render.render(write_still=True)
        os.replace(temporary, output / f"frame_{frame:06d}.png")
        elapsed = round(time.monotonic() - frame_start, 4)
        timings.append({"frame": frame, "seconds": elapsed})
        print(json.dumps({"event": "frame", "renderer": "blender", "frame": frame, "seconds": elapsed}), flush=True)
    check_sources()
    receipt = {"renderer": "blender", "version": bpy.app.version_string, "engine": "CYCLES", "device": "CPU", "frames": frames, "frame_timings": timings, "elapsed_seconds": round(time.monotonic() - started, 3), "view_transform": scene.view_settings.view_transform, "exposure": scene.view_settings.exposure, "image_bit_depth": int(scene.render.image_settings.color_depth), "motion_blur": {"enabled": scene.render.use_motion_blur, "shutter": scene.render.motion_blur_shutter, "baked": bool(scene.get("pipeline_motion_baked", False))}}
    (output / "renderer.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
