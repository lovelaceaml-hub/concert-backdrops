"""Native, deterministic design study using the actual approved visual system.

The original production modules remain unchanged. This adapter restores their
world, lens and performances and applies explicit delivery quality settings.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/promo-beauty-rebuild"
SOURCE_START = 97.8
DURATION = 30.0
FPS = 60
FRAMES = int(DURATION * FPS)
ENGINE_COMMIT = "d928ff9eafe02ac3150f0c646bdcc497fe5a7278"
PEOPLE_COMMIT = "f43f4514e4bc42dc25166e90160d98219f5a0db4"
ACCOUNT_COMMIT = "34f835206dcb26cfa0bd7e321171d3d224e3aa7d"
PICTURE_DELAY = 0.1
GRAIN_LINE = "col += (n1+n2-1.0)*(1.15/255.0);"


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def source_hashes():
    paths = set()
    for folder in ("tools/promo_beauty_example", "tools/s11_full2", "tools/nine_colours_minor", "engine/p3d",
                   "work/nine_colours_minor/render1/engine", "work/nine_colours_revision3/claude-final/engine"):
        paths.update((ROOT / folder).rglob("*.py"))
    paths.update((ROOT / "fonts").glob("*.ttf"))
    paths.update(ROOT / p for p in ("engine/titles.py", "uv.lock", "pyproject.toml"))
    paths.update((ROOT / "work/s11_full2" / name) for name in ("features.npz", "music_fx.npz", "score.wav"))
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths) if p.is_file()}


def runtime_identity():
    packages = {}
    for name in ("numpy", "scipy", "Pillow", "moderngl", "librosa", "numba"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "missing"
    return {"python": sys.version.split()[0], "packages": packages,
            "engine_commit": ENGINE_COMMIT, "people_commit": PEOPLE_COMMIT,
            "hash_seed": os.environ.get("PYTHONHASHSEED"),
            "software_threads": os.environ.get("LP_NUM_THREADS", "1"), "renderer": "cloud CPU llvmpipe"}


def validate_analysis():
    import numpy as np
    base = ROOT / "work/s11_full2"
    required = ("score.wav", "features.npz", "music_fx.npz")
    if any(not (base / name).is_file() for name in required):
        raise RuntimeError("Prepare the verified Song 11 recording and both analysis maps first.")
    with np.load(base / "music_fx.npz") as music:
        for channel in ("bass", "kick", "strings", "brass", "choir", "high", "low"):
            values = music[channel]
            if not np.isfinite(values).all() or float(np.max(values)) <= 0:
                raise RuntimeError(f"Missing or empty music response: {channel}")
        if float(music["times"][-1]) < SOURCE_START + DURATION:
            raise RuntimeError("Music analysis does not cover the example.")


def make_renderer(width=1920, height=1080, samples=2, keep_grain=False):
    if sys.platform == "darwin":
        raise RuntimeError("This example is configured for the cloud CPU workflow.")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Set PYTHONHASHSEED=0 before starting Python for reproducible word scatter.")
    validate_analysis()
    sys.path.insert(0, str(ROOT / "tools/s11_full2"))
    spec = importlib.util.spec_from_file_location("beauty_s11_renderer", ROOT / "tools/s11_full2/render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    Renderer = module.load(FPS)
    import shaders
    if not keep_grain:
        if shaders.COMP_FS.count(GRAIN_LINE) != 1:
            raise RuntimeError("Pinned composite grain anchor changed; review before rendering.")
        shaders.COMP_FS = shaders.COMP_FS.replace(GRAIN_LINE, "// Design study: no added output grain.")
    # The production loader defaults to 1080p. Native 4K also needs its legacy
    # text textures initialized at 4K, before the renderer allocates them.
    if (width, height) == (3840, 2160):
        os.environ["OUT_RES"] = "4k"
        import text as text_module
        importlib.reload(text_module)
        if (text_module.W, text_module.H) != (width, height):
            raise RuntimeError("Native 4K text dimensions were not initialized correctly.")
    import songs.s11_full2 as film
    # The original conductor compositions aim far into the ribbons and city.
    # Keep that framing but focus the lens on the person who causes the action.
    # This is an isolated study variation, not a change to the approved scene.
    hero_focus = film.S_DANCE.COND_C + film._v(0.0, 1.45, 0.0)
    for shot, move in zip(film.SHOTS, film.CAMERA.moves):
        if shot["name"].startswith("dance_"):
            move.focus = hero_focus
            move.aperture = 0.012
        elif shot["kind"] == "stage":
            move.aperture = min(float(move.aperture), 0.008)
    film.CAMERA._table = None
    renderer = Renderer(width, height)
    renderer.p3d.samples = samples
    renderer.p3d.draft = False
    original_world_state = renderer.p3d.world.state
    original_adjust = renderer.p3d.adjust

    def world_state(t):
        world = original_world_state(t)
        if film.stage_view(t):
            world["sun_int"] *= 0.65
            world["rays"] *= 0.65
            world["sun_glow"] *= 0.75
        return world

    def adjust(t, parameters):
        parameters = original_adjust(t, parameters)
        if film.stage_view(t):
            parameters["bloom_gain"] = parameters.get("bloom_gain", 1.0) * 0.75
        return parameters

    renderer.p3d.world.state = world_state
    renderer.p3d.adjust = adjust
    renderer.beauty_cuts = list(film.CUTS)
    renderer.beauty_shutter = float(renderer.p3d.shutter)
    return renderer


def frame(renderer, index, source_start=SOURCE_START):
    source_time = max(0.0, round(source_start + index / FPS - PICTURE_DELAY, 10))
    # A shutter must not span two unrelated camera shots. Retain the original
    # analytic motion blur everywhere else, plus HDR point-set time sampling.
    crosses_cut = any(0 <= source_time - cut < renderer.beauty_shutter / FPS
                      for cut in renderer.beauty_cuts)
    renderer.p3d._frame = None
    renderer.p3d.shutter = 0.0 if crosses_cut else renderer.beauty_shutter
    try:
        return renderer.out.frame(source_time, int(round(source_time * FPS)))
    finally:
        renderer.p3d.shutter = renderer.beauty_shutter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--samples", type=int, choices=(1, 2, 3, 4), default=2)
    parser.add_argument("--source-start", type=float, default=SOURCE_START)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=FRAMES)
    parser.add_argument("--stills", help="Comma separated example frame indices, instead of a movie")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--keep-grain", action="store_true")
    args = parser.parse_args()
    if args.width % 2 or args.height % 2 or min(args.width, args.height) < 32:
        parser.error("Use even, positive render dimensions.")
    if args.width * 9 != args.height * 16:
        parser.error("The authored composition requires 16:9 dimensions.")
    if not 0 <= args.start < args.end <= FRAMES:
        parser.error("Frame range must be inside the thirty-second example.")
    if not 0 <= args.source_start <= 245:
        parser.error("The source interval must fit inside the prepared 275-second score.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    stop_file = Path(os.environ["BEAUTY_STOP_FILE"]) if os.environ.get("BEAUTY_STOP_FILE") else None
    if stop_file is not None and stop_file.exists():
        raise RuntimeError("This render round has a stop marker.")
    before = source_hashes()
    started = time.monotonic()
    logpath = args.out.with_suffix(".setup.log")
    with logpath.open("w") as log, contextlib.redirect_stdout(log):
        renderer = make_renderer(args.width, args.height, args.samples, args.keep_grain)
    print(json.dumps({"event": "renderer_ready", "seconds": time.monotonic() - started,
                      "renderer": renderer.ctx.info.get("GL_RENDERER"),
                      "native_size": [args.width, args.height], "hdr_motion_samples": args.samples}), flush=True)
    if args.stills:
        from PIL import Image
        args.out.mkdir(parents=True, exist_ok=True)
        for index in map(int, args.stills.split(",")):
            tick = time.monotonic()
            data = frame(renderer, index, args.source_start)
            target = args.out / f"frame-{index:04d}.png"
            Image.frombytes("RGB", (args.width, args.height), data).save(target)
            print(json.dumps({"frame": index, "path": str(target), "seconds": time.monotonic() - tick}), flush=True)
        return
    temporary = args.out.with_name(args.out.stem + ".assembling.mp4")
    command = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{args.width}x{args.height}", "-r", str(FPS), "-i", "-",
               "-vf", "scale=out_color_matrix=bt709:out_range=tv,"
               "setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709",
               "-c:v", "libx264",
               "-threads", "1", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
               "-g", str(FPS * 2), "-color_primaries", "bt709", "-color_trc", "bt709",
               "-colorspace", "bt709", "-color_range", "tv", str(temporary)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for index in range(args.start, args.end):
            if stop_file is not None and stop_file.exists():
                raise RuntimeError("Render stopped by its coordinator.")
            encoder.stdin.write(frame(renderer, index, args.source_start))
            if (index - args.start) % 30 == 0:
                print(json.dumps({"frame": index, "elapsed_seconds": time.monotonic() - started}), flush=True)
    except BaseException:
        encoder.stdin.close()
        encoder.terminate()
        encoder.wait()
        raise
    encoder.stdin.close()
    if encoder.wait():
        raise RuntimeError("Video encoder failed.")
    if source_hashes() != before:
        raise RuntimeError("Render inputs changed during the frozen round.")
    temporary.replace(args.out)
    receipt = {"width": args.width, "height": args.height, "fps": FPS,
               "start": args.start, "end": args.end, "source_start": args.source_start,
               "picture_delay": PICTURE_DELAY, "hdr_motion_samples": args.samples,
               "conductor_focus": "chest at 1.45 m; aperture 0.012; original camera path",
               "stage_grade": {"sun_and_rays": 0.65, "sun_glow": 0.75, "bloom": 0.75,
                               "maximum_aperture": 0.008},
               "grain": args.keep_grain, "sha256": digest(args.out), "bytes": args.out.stat().st_size,
               "source_sha256": before, "runtime": runtime_identity(),
               "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
               "elapsed_seconds": time.monotonic() - started}
    atomic_json(args.out.with_suffix(".json"), receipt)
    print(json.dumps({"event": "complete", "path": str(args.out),
                      "elapsed_seconds": receipt["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
