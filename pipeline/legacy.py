"""Use the real p3d Renderer without editing its approved source files."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from .audio import legacy_features
from .project import safe_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    args = parser.parse_args()
    job = json.loads(Path(args.job).read_text())
    root = Path(job["repo_root"])
    shot = job["shot"]
    scene = safe_path(root, shot["scene"])
    os.environ["SONG"] = scene.stem
    os.environ["OUT_FPS"] = str(job["video"]["fps"])
    os.environ["OUT_RES"] = "1080p"
    os.environ["FEATURES"] = str(legacy_features(job))
    os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
    np.random.seed(job["seed"])
    sys.path.insert(0, str(root / "engine"))
    from render import Renderer
    renderer = Renderer(job["video"]["width"], job["video"]["height"])
    out = Path(job["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    offset = float(shot.get("params", {}).get("source_time_seconds", 0))
    fps = job["video"]["fps"]
    for frame in job["frames"]:
        seconds = offset + (frame - shot["start_frame"]) / fps
        pixels = renderer.out.frame(seconds, round(seconds * fps))
        temporary = out / f"frame_{frame:06d}.partial.png"
        Image.frombytes("RGB", (renderer.w, renderer.h), pixels).save(temporary)
        temporary.replace(out / f"frame_{frame:06d}.png")
        print(f"p3d frame {frame}: source {seconds:.6f}s", flush=True)


if __name__ == "__main__":
    main()
