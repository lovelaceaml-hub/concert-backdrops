"""Cloud CPU renderer for a continuous, Blender-baked 12-second fan phrase."""
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
WORK = ROOT / "work/fluid-dance"
DURATION = 12.0
FPS = 60
SOURCE_START = 0.0
CUTS = ()


def performance_path():
    return Path(os.environ.get("FLUID_DANCE_BUNDLE", WORK / "performance")).resolve()


def source_hashes():
    paths = set((ROOT / "tools/fluid_dance").glob("*.py"))
    paths.update((ROOT / "engine").rglob("*.py"))
    for folder in ("tools/concert_kit", "tools/advanced_dance", "tools/cinematic_ten"):
        paths.update((ROOT / folder).glob("*.py"))
    paths.update(ROOT / n for n in ("assets/p3d/body_v1.npz", "assets/p3d/brand/land_2048.png", "pyproject.toml", "uv.lock"))
    bundle = performance_path()
    base = bundle if bundle.is_dir() else bundle.parent
    for name in ("performance.npz", "performance.json"):
        p = base / name
        if not p.is_file():
            raise RuntimeError("Prepare and validate the Blender performance first: " + str(p))
        paths.add(p)
    for name in ("cloth.npy", "cloth.json"):
        p = WORK / name
        if not p.is_file():
            raise RuntimeError("Bake the exact performance costume first: " + str(p))
        paths.add(p)
    result = {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}
    result.update({"fonts/" + p.name: digest(p) for p in sorted(fonts_path().glob("*.ttf"))})
    return result


def make_renderer(width=1920, height=1080, temporal_samples=2, fps=60, mode="beauty"):
    if sys.platform == "darwin":
        raise RuntimeError("This production runs in the cloud environment.")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Set PYTHONHASHSEED=0 before starting Python.")
    if fps not in (30, 60) or mode not in ("beauty", "proof"):
        raise ValueError("Use beauty/proof and 30/60 fps.")
    if "song" in sys.modules or "P3D_BODY_ASSET" in os.environ:
        raise RuntimeError("Initialize this scene in a fresh process with its declared rig.")
    identity = source_hashes()
    key = hashlib.sha256(json.dumps({"source": identity, "mode": mode},
                                   sort_keys=True).encode()).hexdigest()[:20]
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ.update(SONG="song_fluid", FLUID_DANCE_MODE=mode,
        FLUID_DANCE_BUNDLE=str(performance_path()), FLUID_DANCE_CLOTH=str(WORK / "cloth.npy"),
        OUT_FPS=str(fps), OUT_RES="4k" if width == 3840 else "1080p",
        LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS=os.environ.get("LP_NUM_THREADS", "1"),
        OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
        NUMBA_CACHE_DIR=str(WORK / "numba"), MESA_SHADER_CACHE_DIR=str(WORK / "mesa"),
        P3D_CACHE=str(WORK / "p3d-cache" / key))
    for p in (ROOT, ROOT / "engine"):
        sys.path.insert(0, str(p))
    import songs
    songs.__path__.append(str(ROOT / "tools/fluid_dance"))
    import song
    fp = fonts_path()
    song.ROOT = str(fp.parent)
    import render as legacy
    import text as typography
    typography.FONTS = str(fp)
    for key, name in {"F_PHRASE": "cormorant-garamond-latin-700-italic.ttf",
        "F_TITLE": "cormorant-garamond-latin-700-normal.ttf", "F_LABEL": "jost-latin-500-normal.ttf",
        "F_TAG": "cormorant-garamond-latin-600-italic.ttf"}.items():
        setattr(typography, key, str(fp / name))
    import shaders
    shaders.COMP_FS = shaders.COMP_FS.replace("col += (n1+n2-1.0)*(1.15/255.0);", "// Native clean performance delivery.")
    r = legacy.Renderer(width, height)
    r.p3d.samples = int(temporal_samples)
    r.p3d.draft = False
    r.fluid_fps = fps
    r.fluid_mode = mode
    from tools.cinematic_ten.render import _signature
    r.fluid_signature = _signature(width, height) if mode == "beauty" else None
    adjust = r.p3d.adjust
    def controlled_bloom(t, params):
        params = adjust(t, params)
        params["bloom_gain"] = params.get("bloom_gain", 1) * (.48 if mode == "beauty" else .12)
        return params
    r.p3d.adjust = controlled_bloom
    return r


def frame(renderer, global_index, fps=60):
    from PIL import Image
    if fps != renderer.fluid_fps:
        raise ValueError("Frame rate must match initialized renderer.")
    renderer.p3d._frame = None
    raw = renderer.out.frame(float(global_index) / fps, global_index)
    if renderer.fluid_signature is None:
        return raw
    im = Image.frombytes("RGB", (renderer.w, renderer.h), raw).convert("RGBA")
    return Image.alpha_composite(im, renderer.fluid_signature).convert("RGB").tobytes()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("beauty", "proof"), default="beauty")
    p.add_argument("--stills")
    p.add_argument("--start-frame", type=int, default=0)
    p.add_argument("--end-frame", type=int, default=720)
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--fps", type=int, choices=(30, 60), default=60)
    p.add_argument("--samples", type=int, default=2)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    from PIL import Image
    t0 = time.monotonic()
    r = make_renderer(a.width, a.height, a.samples, a.fps, a.mode)
    print(json.dumps({"event": "ready", "seconds": round(time.monotonic() - t0, 3),
                      "renderer": r.ctx.info["GL_RENDERER"]}), flush=True)
    a.out.mkdir(parents=True, exist_ok=True)
    ids = [round(float(t) * a.fps) for t in a.stills.split(",")] if a.stills else range(a.start_frame, a.end_frame)
    for idx in ids:
        target = a.out / f"{idx:06d}.png"
        if target.exists():
            continue
        started = time.monotonic()
        im = Image.frombytes("RGB", (a.width, a.height), frame(r, idx, a.fps))
        temp = target.with_suffix(".partial.png")
        im.save(temp, compress_level=3)
        temp.replace(target)
        if a.stills or idx % 30 == 0:
            print(json.dumps({"frame": idx, "seconds": round(time.monotonic() - started, 3)}), flush=True)


if __name__ == "__main__":
    main()
