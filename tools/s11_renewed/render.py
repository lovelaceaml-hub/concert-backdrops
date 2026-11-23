"""Render the renewed full Song 11 on its unchanged source recording clock.

Stills use absolute song seconds. Movies use absolute 60 fps frame ranges;
the complete film is frames 0 through 16499, including its 15 second hold.
Each chunk has a source fingerprint and can be resumed only with identical
inputs. The master is assembled by copying the encoded chunks, with one
audio encode from the prepared, verified 275 second score.
"""
from __future__ import annotations

import argparse
import contextlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.promo_beauty_example import render as beauty

FPS = 60
TOTAL = 275
FRAMES = FPS * TOTAL
HERE = Path(__file__).resolve().parent
SOURCE_AUDIO_SHA256 = "70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004"


def worker_environment():
    return dict(os.environ, PYTHONHASHSEED="0", LIBGL_ALWAYS_SOFTWARE="1",
                LP_NUM_THREADS=os.environ.get("LP_NUM_THREADS", "1"),
                OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                NUMBA_NUM_THREADS="1")


def source_hashes():
    hashes = beauty.source_hashes()
    paths = set(HERE.rglob("*.py"))
    paths.add(HERE / "requirements-render.txt")
    for path in sorted(paths):
        hashes[str(path.relative_to(ROOT))] = beauty.digest(path)
    return hashes


def validate_full_analysis():
    import numpy as np
    beauty.validate_analysis()
    work = ROOT / "work/s11_full2"
    provenance = json.loads((work / "provenance.json").read_text())
    if provenance.get("audio_sha256") != SOURCE_AUDIO_SHA256 or provenance.get("total_seconds") != TOTAL:
        raise RuntimeError("Song 11 preparation does not identify the complete verified source.")
    for name in ("features.npz", "music_fx.npz"):
        with np.load(work / name) as data:
            if float(data["times"][-1]) < TOTAL - 0.1:
                raise RuntimeError(f"{name} does not cover the complete 275 second film.")
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "json", str(work / "score.wav")],
                            check=True, capture_output=True, text=True)
    if abs(float(json.loads(result.stdout)["format"]["duration"]) - TOTAL) > 1 / 48000:
        raise RuntimeError("The prepared score must be exactly 275 seconds.")


def install_visibility_optimization(renderer):
    """Skip exactly invisible sets and wholly offscreen church point centers.

    The pinned sprite shader itself discards centers outside NDC +/-1.6,
    before adding any bokeh, glow or streak footprint. Church objects are
    immutable sprite clouds with no silhouette mask. Their mirror bounds
    include the exact shader's maximum ripple displacement. Other geometry
    is retained unchanged. The opt-out is for pixel-equivalence verification.
    """
    import numpy as np
    layer = renderer.p3d
    original = layer._batches
    layer.renewed_unoptimized_batches = original
    bounds = {}
    stats = dict(zero_gain_skips=0, offscreen_church_skips=0)
    layer.renewed_visibility_stats = stats

    def outside(corners, cam, basis):
        v = (corners - np.asarray(cam.pos)) @ basis
        x, y, z = v.T
        focal = 1.0 / np.tan(np.radians(cam.fov) * .5)
        # 1.60001 is wider than the GPU center clip; retain plane boundaries.
        edge = 1.60001
        near = min(max(float(cam.near), .02), 1.0)
        return (np.all(z < near) or
                np.all(focal * x > edge * cam.aspect * z) or
                np.all(focal * x < -edge * cam.aspect * z) or
                np.all(focal * y > edge * z) or
                np.all(focal * y < -edge * z))

    def corners(lo, hi):
        return np.array([[x, y, z] for x in (lo[0], hi[0])
                         for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])

    def batches(entry, t, cam):
        ps = entry.pointset
        # Emissive gain and opaque mask strength are independent. A dark
        # architectural/body mask can remain active when its light is zero.
        mask_source = entry.name.endswith("#mask")
        if entry.mask is None and not mask_source and hasattr(ps, "gain") and float(ps.gain(t)) == 0.0:
            stats["zero_gain_skips"] += 1
            return []
        data = original(entry, t, cam)
        if (not entry.name.startswith("church of God ") or not getattr(ps, "static", False)
                or entry.mask is not None or mask_source or getattr(ps, "dome", False) or getattr(ps, "turns", False)):
            return data
        key = entry.name
        if key not in bounds:
            if not data or any(b["pos2"] is not None for b in data):
                bounds[key] = None
            else:
                p = np.concatenate([b["pos"] for b in data])
                bounds[key] = (p.min(0).astype(float), p.max(0).astype(float))
        extent = bounds[key]
        if extent is None:
            return data
        lo, hi = extent
        basis = np.column_stack(cam.basis())
        c = corners(lo, hi)
        if not outside(c, cam, basis):
            return data
        # Reflections can appear even when the direct geometry is offscreen.
        if entry.reflect and any(b["reflect"] for b in data):
            world = layer.world.now
            calm, calm_values, count = layer.world.calm_at(t)
            ripple = abs(float(world["ripple"]))
            if count:
                ripple = max(ripple, float(np.max(np.abs(calm_values[:count, 0]))))
            if ripple > 2.0 or lo[1] < 0.0 or cam.pos[1] <= 0.0:
                return data
            reflected_lo = np.array([lo[0], -hi[1], lo[2]])
            reflected_hi = np.array([hi[0], -lo[1], hi[2]])
            reflected = corners(reflected_lo, reflected_hi)
            max_path = float(np.max(np.linalg.norm(reflected - cam.pos, axis=1)))
            # Shader rip(): sum of 0.012+0.010+0.008+0.006 waves, followed by
            # wm.xz += 2 * rip * lake_ripple * reflection_path.
            margin = 2.0 * .036 * ripple * max_path + 1e-5
            reflected_lo[[0, 2]] -= margin
            reflected_hi[[0, 2]] += margin
            if not outside(corners(reflected_lo, reflected_hi), cam, basis):
                return data
        stats["offscreen_church_skips"] += 1
        return []

    layer._batches = batches


def identity(args):
    record = dict(schema="s11-renewed-render-v1", width=args.width,
                  height=args.height, fps=FPS, samples=args.samples,
                  crf=args.crf, baseline=args.baseline,
                  visibility_optimization=(not args.baseline and os.environ.get(
                      "S11_DISABLE_VISIBILITY_OPTIMIZATION") != "1"),
                  picture_delay=beauty.PICTURE_DELAY,
                  sources=source_hashes(), runtime=beauty.runtime_identity())
    record["fingerprint"] = hashlib.sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return record


def make_renderer(width=1920, height=1080, samples=2, baseline=False):
    """Reuse the Song 11 beauty setup with isolated creative installation hooks."""
    if sys.platform == "darwin":
        raise RuntimeError("This renderer is configured for the cloud environment.")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Start Python with PYTHONHASHSEED=0.")
    validate_full_analysis()
    cache = beauty.configure_asset_cache()
    sys.path.insert(0, str(ROOT / "tools/s11_full2"))
    spec = importlib.util.spec_from_file_location(
        "renewed_s11_source_renderer", ROOT / "tools/s11_full2/render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    Renderer = module.load(FPS)
    if os.environ.get("P3D_CACHE") != str(ROOT / cache["namespace"]):
        raise RuntimeError("The Song 11 loader did not retain the verified cache namespace.")
    import shaders
    if shaders.COMP_FS.count(beauty.GRAIN_LINE) != 1:
        raise RuntimeError("The pinned grain anchor changed; review the source.")
    shaders.COMP_FS = shaders.COMP_FS.replace(
        beauty.GRAIN_LINE, "// Renewed Song 11: no additional output grain.")
    if (width, height) == (3840, 2160):
        os.environ["OUT_RES"] = "4k"
        import text as text_module
        importlib.reload(text_module)
        if (text_module.W, text_module.H) != (width, height):
            raise RuntimeError("Native text dimensions do not match the render.")
    import songs.s11_full2 as film
    hero = film.S_DANCE.COND_C + film._v(0.0, 1.45, 0.0)
    for shot, move in zip(film.SHOTS, film.CAMERA.moves):
        if shot["name"].startswith("dance_"):
            move.focus = hero
            move.aperture = 0.012
        elif shot["kind"] == "stage":
            move.aperture = min(float(move.aperture), 0.008)
    film.CAMERA._table = None
    if not baseline:
        from tools.s11_renewed import scene, performance
        scene.install(film)
        performance.install(film)
    renderer = Renderer(width, height)
    renderer.p3d.samples = samples
    renderer.p3d.draft = False
    original_world = renderer.p3d.world.state
    original_adjust = renderer.p3d.adjust

    def world_state(t):
        world = original_world(t)
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
    renderer.renewed_song = film
    if not baseline:
        scene.finish_renderer(renderer, film)
        if os.environ.get("S11_DISABLE_VISIBILITY_OPTIMIZATION") != "1":
            install_visibility_optimization(renderer)
    return renderer


def frame(renderer, index):
    return beauty.frame(renderer, index, source_start=0.0)


def probe(path):
    result = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,nb_frames,codec_name",
        "-of", "json", str(path)], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)["streams"][0]


def validate_stream(path, args, frames):
    stream = probe(path)
    if (stream.get("width"), stream.get("height")) != (args.width, args.height):
        raise RuntimeError(f"Wrong native dimensions in {path}.")
    if stream.get("avg_frame_rate") != "60/1":
        raise RuntimeError(f"Wrong frame rate in {path}.")
    if int(stream.get("nb_frames", -1)) != frames:
        raise RuntimeError(f"Wrong frame count in {path}.")
    return stream


def valid_chunk(path, args, start, end, fingerprint):
    receipt_path = path.with_suffix(".json")
    if not path.is_file() or not receipt_path.is_file():
        return False
    try:
        receipt = json.loads(receipt_path.read_text())
        if (receipt["fingerprint"], receipt["start"], receipt["end"]) != (
                fingerprint, start, end):
            return False
        if receipt["sha256"] != beauty.digest(path):
            return False
        validate_stream(path, args, end - start)
        return True
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, RuntimeError):
        return False


def setup(args):
    started = time.monotonic()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.with_suffix(".setup.log").open("w") as log, contextlib.redirect_stdout(log):
        renderer = make_renderer(args.width, args.height, args.samples, args.baseline)
    print(json.dumps(dict(event="renderer_ready", seconds=time.monotonic() - started,
                          renderer=renderer.ctx.info.get("GL_RENDERER"),
                          native_size=[args.width, args.height], samples=args.samples)), flush=True)
    return renderer


def render_chunk(args):
    frozen = identity(args)
    if valid_chunk(args.out, args, args.start, args.end, frozen["fingerprint"]):
        print(json.dumps(dict(event="chunk_reused", start=args.start, end=args.end)), flush=True)
        return
    renderer = setup(args)
    temporary = args.out.with_name(args.out.stem + ".assembling.mp4")
    command = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{args.width}x{args.height}", "-r", str(FPS), "-i", "-",
               "-vf", "scale=out_color_matrix=bt709:out_range=tv,"
               "setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709",
               "-c:v", "libx264", "-threads", "1", "-preset", "medium", "-crf", str(args.crf),
               "-pix_fmt", "yuv420p", "-g", "120", "-color_primaries", "bt709",
               "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", str(temporary)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
    started = time.monotonic()
    try:
        for index in range(args.start, args.end):
            if args.stop_file and args.stop_file.exists():
                raise RuntimeError("The render stop marker was set.")
            encoder.stdin.write(frame(renderer, index))
            if (index - args.start) % 60 == 0:
                print(json.dumps(dict(event="frame", frame=index,
                                      seconds=time.monotonic() - started)), flush=True)
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError("Video encoding failed.")
    except BaseException:
        with contextlib.suppress(Exception):
            encoder.stdin.close()
        encoder.terminate()
        encoder.wait()
        raise
    if identity(args)["fingerprint"] != frozen["fingerprint"]:
        raise RuntimeError("Render inputs changed during this chunk; it has not been accepted.")
    stream = validate_stream(temporary, args, args.end - args.start)
    temporary.replace(args.out)
    receipt = dict(fingerprint=frozen["fingerprint"], start=args.start, end=args.end,
                   width=args.width, height=args.height, fps=FPS, samples=args.samples,
                   seconds=time.monotonic() - started, sha256=beauty.digest(args.out),
                   bytes=args.out.stat().st_size, stream=stream,
                   actual_cache_namespace=str(Path(os.environ["P3D_CACHE"]).relative_to(ROOT)),
                   peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    beauty.atomic_json(args.out.with_suffix(".json"), receipt)
    print(json.dumps(dict(event="chunk_complete", **receipt)), flush=True)


def render_stills(args):
    renderer = setup(args)
    args.out.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    measurements = []
    for second in map(float, args.stills.split(",")):
        if not 0 <= second < TOTAL:
            raise ValueError("Still time must be within 0 through 275 seconds.")
        index = round(second * FPS)
        started = time.monotonic()
        path = args.out / f"song-{index / FPS:07.2f}.png"
        Image.frombytes("RGB", (args.width, args.height), frame(renderer, index)).save(path)
        row = dict(second=index / FPS, seconds_to_render=time.monotonic() - started,
                   path=str(path), peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
        measurements.append(row)
        print(json.dumps(row), flush=True)
    beauty.atomic_json(args.out / "timings.json", measurements)


def render_master(args):
    frozen = identity(args)
    parts_dir = args.out.parent / (args.out.stem + "-parts")
    parts_dir.mkdir(parents=True, exist_ok=True)
    beauty.atomic_json(parts_dir / "inputs.json", frozen)
    ranges = [(start, min(start + args.chunk_frames, args.end))
              for start in range(args.start, args.end, args.chunk_frames)]
    parts = [parts_dir / f"part-{start:06d}-{end:06d}.mp4" for start, end in ranges]

    def run_one(start, end, path):
        if valid_chunk(path, args, start, end, frozen["fingerprint"]):
            print(json.dumps(dict(event="chunk_reused", start=start, end=end)), flush=True)
            return
        command = [sys.executable, str(Path(__file__).resolve()), "--worker",
                   "--start", str(start), "--end", str(end), "--width", str(args.width),
                   "--height", str(args.height), "--samples", str(args.samples),
                   "--crf", str(args.crf), "--out", str(path)]
        if args.baseline:
            command.append("--baseline")
        if args.stop_file:
            command.extend(["--stop-file", str(args.stop_file)])
        with path.with_suffix(".log").open("w") as log:
            result = subprocess.run(command, cwd=ROOT, env=worker_environment(),
                                    stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(f"Chunk {start}:{end} failed; see {path.with_suffix('.log')}.")
        if not valid_chunk(path, args, start, end, frozen["fingerprint"]):
            raise RuntimeError(f"Chunk {start}:{end} did not produce matching verified output.")
        print(json.dumps(dict(event="chunk_complete", start=start, end=end)), flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_one, start, end, path)
                   for (start, end), path in zip(ranges, parts)]
        for future in as_completed(futures):
            future.result()
    if identity(args)["fingerprint"] != frozen["fingerprint"]:
        raise RuntimeError("Render inputs changed. Master assembly is blocked.")
    # Paths are authored filenames relative to this concat file; no shell is involved.
    concat = parts_dir / "concat.txt"
    concat.write_text("".join(f"file '{path.name}'\n" for path in parts))
    temporary = args.out.with_name(args.out.stem + ".assembling.mp4")
    duration = (args.end - args.start) / FPS
    command = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "1",
               "-i", str(concat), "-ss", f"{args.start / FPS:.9f}",
               "-i", str(ROOT / "work/s11_full2/score.wav"), "-map", "0:v:0", "-map", "1:a:0",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
               "-t", f"{duration:.9f}", "-movflags", "+faststart", str(temporary)]
    subprocess.run(command, check=True)
    validate_stream(temporary, args, args.end - args.start)
    temporary.replace(args.out)
    receipt = dict(**frozen, start=args.start, end=args.end, duration=duration,
                   native_render=True, temporal_interpolation=False, spatial_upscale=False,
                   audio="Verified score, original 0-260 second clock plus 15 second hold",
                   parts=[str(path.relative_to(args.out.parent)) for path in parts],
                   sha256=beauty.digest(args.out), bytes=args.out.stat().st_size)
    beauty.atomic_json(args.out.with_suffix(".json"), receipt)
    print(json.dumps(dict(event="master_complete", path=str(args.out),
                          duration=duration, sha256=receipt["sha256"])), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--samples", type=int, choices=(1, 2, 3, 4), default=2)
    parser.add_argument("--crf", type=int, default=14)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=FRAMES)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--chunk-frames", type=int, default=1800)
    parser.add_argument("--stills", help="Comma separated absolute song seconds")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--baseline", action="store_true", help="Render the old beauty reference for comparison")
    parser.add_argument("--stop-file", type=Path)
    args = parser.parse_args()
    args.out = args.out.resolve()
    if args.width % 2 or args.height % 2 or min(args.width, args.height) < 32 or args.width * 9 != args.height * 16:
        parser.error("Use even 16:9 native dimensions.")
    if not 0 <= args.start < args.end <= FRAMES:
        parser.error("Frame range must be inside the complete 275 second song film.")
    if not 1 <= args.workers <= 8 or args.chunk_frames < 1 or not 0 <= args.crf <= 30:
        parser.error("Use 1-8 workers, positive chunk size, and CRF 0-30.")
    if args.stop_file and args.stop_file.exists():
        raise RuntimeError("The render stop marker is already set.")
    if args.stills:
        render_stills(args)
    elif args.worker:
        render_chunk(args)
    else:
        render_master(args)


if __name__ == "__main__":
    main()
