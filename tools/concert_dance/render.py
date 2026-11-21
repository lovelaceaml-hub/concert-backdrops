"""Cloud CPU renderer for the isolated, continuous natural dance study.

Planning imports do not create a graphics context. The registered pipeline
owns checkpointed frames, sound assembly and delivery validation.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import time

from tools.concert_kit.render import COLOR_CONTRACT, digest, fonts_path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/natural-performance"
DURATION = 18.0
FPS = 60
SOURCE_START = 0.0
CUTS = ()


def source_hashes():
    paths = set((ROOT / "tools/concert_dance").glob("*.py"))
    paths.update((ROOT / "engine").rglob("*.py"))
    paths.update(ROOT / name for name in (
        "tools/concert_kit/render.py", "tools/concert_kit/models.py",
        "assets/p3d/body_v1.npz", "assets/p3d/brand/land_2048.png",
        "pyproject.toml", "uv.lock"))
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}
    hashes.update({"fonts/" + p.name: digest(p) for p in sorted(fonts_path().glob("*.ttf"))})
    return hashes


def make_renderer(width=1920, height=1080, temporal_samples=2, fps=60):
    if sys.platform == "darwin":
        raise RuntimeError("This study uses the cloud CPU route.")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Set PYTHONHASHSEED=0 before starting Python.")
    if fps not in (30, 60):
        raise ValueError("The study supports explicit 30 or 60 fps sampling.")
    if "P3D_BODY_ASSET" in os.environ:
        raise RuntimeError("Unset P3D_BODY_ASSET to use the declared capture asset.")
    cache_parts = [ROOT / name for name in (
        "assets/p3d/body_v1.npz", "engine/p3d/body.py", "engine/p3d/actor.py",
        "tools/concert_dance/performance.py", "tools/concert_dance/scene.py")]
    cache = hashlib.sha256("".join(digest(p) for p in cache_parts).encode()).hexdigest()[:20]
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ.update(
        SONG="scene", OUT_FPS=str(fps), OUT_RES="4k" if width == 3840 else "1080p",
        LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS=os.environ.get("LP_NUM_THREADS", "1"),
        OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
        NUMBA_CACHE_DIR=str(WORK / "numba"), MESA_SHADER_CACHE_DIR=str(WORK / "mesa"),
        P3D_CACHE=str(WORK / "p3d-cache" / cache))
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "engine"))
    import songs
    songs.__path__.append(str(ROOT / "tools/concert_dance"))
    import song
    fp = fonts_path()
    song.ROOT = str(fp.parent)
    import render as legacy
    import text as typography
    typography.FONTS = str(fp)
    for key, name in {
        "F_PHRASE": "cormorant-garamond-latin-700-italic.ttf",
        "F_TITLE": "cormorant-garamond-latin-700-normal.ttf",
        "F_LABEL": "jost-latin-500-normal.ttf",
        "F_TAG": "cormorant-garamond-latin-600-italic.ttf",
    }.items():
        setattr(typography, key, str(fp / name))
    import shaders
    shaders.COMP_FS = shaders.COMP_FS.replace(
        "col += (n1+n2-1.0)*(1.15/255.0);", "// No added delivery grain.")
    renderer = legacy.Renderer(width, height)
    renderer.p3d.samples = int(temporal_samples)
    renderer.p3d.draft = False
    renderer.dance_fps = fps
    renderer.dance_signature = _signature(width, height)
    original = renderer.p3d.adjust

    def adjust(t, params):
        params = original(t, params)
        params["bloom_gain"] = params.get("bloom_gain", 1.0) * .64
        return params

    renderer.p3d.adjust = adjust
    return renderer


def _signature(width, height):
    from PIL import Image
    from p3d.brand import logo_image
    scale = height / 1080
    overlay = Image.new("RGBA", (width, height))
    logo = logo_image(height=max(20, round(42 * scale)))
    overlay.alpha_composite(logo, (round(28 * scale), height - round(70 * scale)))
    return overlay


def frame(renderer, global_index, fps=60):
    from PIL import Image
    if int(fps) != renderer.dance_fps:
        raise ValueError("Frame rate must match the initialized renderer.")
    renderer.p3d._frame = None
    raw = renderer.out.frame(float(global_index) / fps, global_index)
    im = Image.frombytes("RGB", (renderer.w, renderer.h), raw).convert("RGBA")
    return Image.alpha_composite(im, renderer.dance_signature).convert("RGB").tobytes()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stills", required=True, help="Comma separated seconds")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    from PIL import Image
    import json
    began = time.monotonic()
    renderer = make_renderer(args.width, args.height, args.samples)
    print(json.dumps({"event": "initialized", "renderer": renderer.ctx.info["GL_RENDERER"],
                      "seconds": round(time.monotonic() - began, 3)}), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    for t in map(float, args.stills.split(",")):
        began = time.monotonic()
        path = args.out / f"t{t:06.2f}.png"
        Image.frombytes("RGB", (args.width, args.height), frame(renderer, round(t * FPS))).save(path)
        print(json.dumps({"file": str(path), "seconds": round(time.monotonic() - began, 3)}), flush=True)


if __name__ == "__main__":
    main()
