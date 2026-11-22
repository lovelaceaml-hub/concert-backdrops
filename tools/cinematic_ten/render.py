"""Native, deterministic cloud CPU rendering for the ten cinematic films."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from tools.concert_kit.render import COLOR_CONTRACT, digest, fonts_path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/cinematic-ten"
DURATION = 20.0
FPS = 60
SOURCE_START = 0.0
CUTS = ()
TITLES = {
    1: "Silk in Light", 2: "Petals in Motion", 3: "One World, Many Hearts",
    4: "The Written Light", 5: "Procession of Lanterns", 6: "A Garden Awakens",
    7: "Wings of Peace", 8: "Ocean of Light", 9: "Celestial Clockwork",
    10: "Together in the Light",
}


def source_hashes(film_id=None):
    common = ("__init__.py", "suite.py", "render.py")
    if film_id is None:
        paths = set((ROOT / "tools/cinematic_ten").glob("*.py"))
    else:
        group = (("dancers.py", "dancers_motion.py") if film_id in (1, 2, 4) else
                 ("cosmos.py", "cosmic_models.py") if film_id in (3, 9) else
                 ("nature.py", "nature_models.py") if film_id in (6, 7, 8) else
                 ("people_worlds.py",))
        paths = {ROOT / "tools/cinematic_ten" / p for p in (*common, *group, f"film{film_id:02d}.py")}
    paths.update((ROOT / "engine").rglob("*.py"))
    for folder in ("tools/concert_fan", "tools/concert_kit", "tools/concert_addons"):
        paths.update((ROOT / folder).glob("*.py"))
    paths.update(ROOT / name for name in (
        "assets/p3d/body_v1.npz", "assets/p3d/brand/land_2048.png", "pyproject.toml", "uv.lock"))
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}
    hashes.update({"fonts/" + p.name: digest(p) for p in sorted(fonts_path().glob("*.ttf"))})
    return hashes


def make_renderer(width=1920, height=1080, temporal_samples=2, fps=60, film_id=1):
    if sys.platform == "darwin":
        raise RuntimeError("The production renderer runs in the cloud CPU environment.")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Set PYTHONHASHSEED=0 before starting Python.")
    if fps not in (30, 60) or film_id not in TITLES:
        raise ValueError("Expected film 1..10 and explicit 30 or 60 fps.")
    if "P3D_BODY_ASSET" in os.environ:
        raise RuntimeError("Unset P3D_BODY_ASSET to use the declared original body asset.")
    if "song" in sys.modules:
        raise RuntimeError("Each film needs an isolated renderer process.")
    identity = source_hashes(film_id)
    cache_key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ.update(
        SONG="suite", CINEMATIC_FILM=str(film_id), OUT_FPS=str(fps),
        OUT_RES="4k" if width == 3840 else "1080p", LIBGL_ALWAYS_SOFTWARE="1",
        LP_NUM_THREADS=os.environ.get("LP_NUM_THREADS", "2"),
        OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
        NUMBA_CACHE_DIR=str(WORK / "numba"), MESA_SHADER_CACHE_DIR=str(WORK / "mesa"),
        P3D_CACHE=str(WORK / "p3d-cache" / cache_key))
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "engine"))
    import songs
    songs.__path__.append(str(ROOT / "tools/cinematic_ten"))
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
    renderer.cinematic_fps = fps
    renderer.cinematic_cuts = tuple(song.CUTS)
    renderer.cinematic_signature = _signature(width, height)
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
    if int(fps) != renderer.cinematic_fps:
        raise ValueError("Frame rate must match the initialized renderer.")
    t = float(global_index) / fps
    renderer.p3d._frame = None
    shutter = renderer.p3d.shutter
    if any(0 <= t - cut < shutter / fps for cut in renderer.cinematic_cuts):
        renderer.p3d.shutter = 0
    try:
        raw = renderer.out.frame(t, global_index)
    finally:
        renderer.p3d.shutter = shutter
    im = Image.frombytes("RGB", (renderer.w, renderer.h), raw).convert("RGBA")
    return Image.alpha_composite(im, renderer.cinematic_signature).convert("RGB").tobytes()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--film", type=int, required=True, choices=range(1, 11))
    parser.add_argument("--stills", help="Comma-separated seconds")
    parser.add_argument("--start-frame", type=int, default=0)
    parser.add_argument("--end-frame", type=int, default=1200)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--fps", type=int, default=60, choices=(30, 60))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    from PIL import Image
    began = time.monotonic()
    renderer = make_renderer(args.width, args.height, args.samples, args.fps, args.film)
    print(json.dumps({"event": "initialized", "film": args.film,
        "renderer": renderer.ctx.info["GL_RENDERER"],
        "seconds": round(time.monotonic() - began, 3)}), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    stamps = [round(float(t) * args.fps) for t in args.stills.split(",")] if args.stills else range(args.start_frame, args.end_frame)
    for i in stamps:
        path = args.out / (f"t{i / args.fps:06.2f}.png" if args.stills else f"{i:06d}.png")
        if path.is_file():
            continue
        began = time.monotonic()
        im = Image.frombytes("RGB", (args.width, args.height), frame(renderer, i, args.fps))
        partial = path.with_suffix(".partial.png")
        im.save(partial, compress_level=3)
        partial.replace(path)
        if args.stills or i % 30 == 0:
            print(json.dumps({"file": str(path), "seconds": round(time.monotonic() - began, 3)}), flush=True)


if __name__ == "__main__":
    main()
