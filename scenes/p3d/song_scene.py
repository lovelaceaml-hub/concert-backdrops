"""Reusable p3d scene: render any engine/songs file through the p3d-kit route.

The p3d-kit route adds frame recovery, worker chunks, temporal samples and QA.
Approved films keep their frozen registrations; this module is the open,
configurable entry for new work. Set it as a shot's scene and pass params:

    "params": {"song": "s11_finale", "start_seconds": 30,
               "bloom_scale": 0.7, "grain": false}

The project's shots set the length. Rendering is cloud CPU only (the pipeline
refuses macOS unless a GPU run is explicitly allowed).
"""
from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
FPS = 60
DURATION = None  # the project's shots define the clock
COLOR_CONTRACT = {"name": "legacy_display_gamma"}
SOURCES = ("pipeline/kit.py",)

_settings = {"song": "s11_finale", "start_seconds": 0.0, "bloom_scale": 1.0, "grain": True}


def configure(params: dict) -> None:
    unknown = set(params) - set(_settings) - {"motion_limits", "camera_path"}
    if unknown:
        raise ValueError(f"song_scene does not understand: {', '.join(sorted(unknown))}")
    song = params.get("song", _settings["song"])
    if not (ROOT / "engine/songs" / f"{song}.py").is_file():
        raise ValueError(f"engine/songs/{song}.py does not exist")
    _settings.update({k: v for k, v in params.items() if k in _settings})


def make_renderer(width=1920, height=1080, temporal_samples=1, fps=FPS):
    os.environ.update(SONG=_settings["song"], OUT_FPS=str(fps),
                      OUT_RES="4k" if width == 3840 else "1080p",
                      LIBGL_ALWAYS_SOFTWARE=os.environ.get("LIBGL_ALWAYS_SOFTWARE", "1"))
    sys.path.insert(0, str(ROOT / "engine"))
    if not _settings["grain"]:
        import shaders
        shaders.COMP_FS = shaders.COMP_FS.replace(
            "col += (n1+n2-1.0)*(1.15/255.0);", "// No added delivery grain.")
    from render import Renderer
    renderer = Renderer(width, height)
    if getattr(renderer, "p3d", None) is not None:
        renderer.p3d.samples = int(temporal_samples)
        scale = float(_settings["bloom_scale"])
        if scale != 1.0:
            original = renderer.p3d.adjust

            def adjust(t, params):
                params = original(t, params)
                params["bloom_gain"] = params.get("bloom_gain", 1.0) * scale
                return params

            renderer.p3d.adjust = adjust
    renderer.scene_fps = fps
    return renderer


def frame(renderer, global_index, fps=FPS):
    seconds = float(_settings["start_seconds"]) + float(global_index) / fps
    if getattr(renderer, "p3d", None) is not None:
        renderer.p3d._frame = None
    return renderer.out.frame(seconds, round(seconds * fps))
