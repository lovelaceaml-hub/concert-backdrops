"""Prepare exact source audio, isolated cloth bakes and native cache checks.

Examples, from the repository root:
  .venv/bin/python -m tools.advanced_dance.prepare audio --mode all
  .venv/bin/python -m tools.advanced_dance.prepare bake --mode solo
  .venv/bin/python -m tools.advanced_dance.prepare bake --mode ensemble --role 2
  PYTHONHASHSEED=0 .venv/bin/python -m tools.advanced_dance.prepare verify-frame --mode solo --frame 891

Audio keeps original playback speed. ``bake`` evaluates only selected cast
members. Run it after freezing score and costume inputs. ``verify-frame`` runs
two fresh renderer processes, one without any cloth-cache load and one that
requires a completed cache for every performer, then compares native RGB bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DURATION = 32.0
FPS = 60
SAMPLE_RATE = 48000
GAIN = 0.630957
FADE_IN = 0.060
FADE_OUT = 0.750


def _digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.partial")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def modes(mode):
    if mode == "all":
        return ("solo", "ensemble")
    if mode not in ("solo", "ensemble"):
        raise ValueError("mode must be solo, ensemble or all")
    return (mode,)


def selected_roles(mode, role=None):
    if mode not in ("solo", "ensemble"):
        raise ValueError("A role selection requires an explicit film mode")
    available = (0,) if mode == "solo" else tuple(range(5))
    if role is None:
        return available
    if isinstance(role, bool) or type(role) is not int or role not in available:
        raise ValueError(f"Invalid {mode} role {role}; expected one of {available}")
    return (role,)


def prepare_audio(mode, *, root=ROOT, update_manifest=False):
    """Write and verify a 32-second PCM master, then install its exact pin."""
    if mode not in ("solo", "ensemble"):
        raise ValueError("Audio needs an explicit film mode")
    root = Path(root)
    clock_path = root / "tools/advanced_dance/clock.json"
    clock = json.loads(clock_path.read_text())[mode]
    source = (root / clock["audio_source"]).resolve()
    if not source.is_relative_to(root.resolve()) or not source.is_file():
        raise ValueError("The clock must identify an existing source inside this checkout")
    if _digest(source) != clock["source_sha256"]:
        raise ValueError("Source audio hash differs from the reviewed beat clock")
    manifest_path = root / f"projects/advanced-dance-{mode}/project.json"
    manifest = json.loads(manifest_path.read_text())
    output = root / f"work/advanced-dance/audio/{mode}.wav"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.stem + f".{os.getpid()}.partial.wav")
    start = float(clock["audio_start_seconds"])
    filters = (f"volume={GAIN:.6f},afade=t=in:st=0:d={FADE_IN:.3f},"
               f"afade=t=out:st={DURATION-FADE_OUT:.3f}:d={FADE_OUT:.3f}")
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-fflags", "+bitexact", "-ss", f"{start:.12f}", "-i", str(source),
               "-t", f"{DURATION:.6f}", "-vn", "-map_metadata", "-1",
               "-af", filters, "-ar", str(SAMPLE_RATE), "-ac", "2",
               "-c:a", "pcm_s24le", "-flags:a", "+bitexact", str(temporary)]
    try:
        subprocess.run(command, check=True, timeout=120)
        import soundfile as sf
        samples, rate = sf.read(temporary, dtype="float64", always_2d=True)
        if rate != SAMPLE_RATE or samples.shape != (int(DURATION*SAMPLE_RATE), 2):
            raise ValueError("Prepared audio did not decode as exactly 32 seconds of stereo 48 kHz")
        if not np.isfinite(samples).all():
            raise ValueError("Prepared audio contains nonfinite samples")
        peak = float(np.max(np.abs(samples)))
        if not 1e-4 < peak < .999:
            raise ValueError(f"Prepared audio is silent or clipped: peak {peak}")
        actual = _digest(temporary)
        pinned = manifest.get("audio", {}).get("source_sha256")
        if pinned and pinned != actual and not update_manifest:
            raise ValueError("Prepared bytes differ from the manifest pin. Review the changed tool or recipe before using --update-manifest.")
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    manifest["audio"] = dict(source=str(output.relative_to(root)), source_sha256=actual,
                             offset_seconds=0)
    _write(manifest_path, manifest)
    version = subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True,
                             text=True, timeout=10).stdout.splitlines()[0]
    receipt = dict(schema_version=1, mode=mode,
                   source=str(source.relative_to(root.resolve())), source_sha256=clock["source_sha256"],
                   clock_sha256=_digest(clock_path), source_start_seconds=start,
                   source_end_seconds=start+DURATION, playback_speed=1.0,
                   duration_seconds=DURATION, sample_rate_hz=rate, channels=2,
                   sample_count=int(samples.shape[0]), codec="pcm_s24le",
                   gain_linear=GAIN, nominal_gain_db=-4.0,
                   fade_in_seconds=FADE_IN, fade_out_seconds=FADE_OUT,
                   decoded_sample_peak=peak, decoded_peak_dbfs=float(20*np.log10(peak)),
                   channel_peaks=np.max(np.abs(samples), axis=0).tolist(),
                   output=str(output.relative_to(root)), output_sha256=actual,
                   output_bytes=output.stat().st_size, ffmpeg=version,
                   beat_clock_status="machine estimates; no live rehearsal conformance claimed")
    _write(output.with_suffix(".json"), receipt)
    return receipt


def _engine_path():
    for path in (ROOT, ROOT / "engine"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def build_one(mode, role):
    """Construct exactly one render-equivalent actor, without fans or cast peers."""
    selected_roles(mode, role)
    _engine_path()
    from .costume import make_body
    from .score import install
    from .scene import CAST_POINTS, PLACEMENTS, SOLO_PLACEMENT, SOLO_POINTS
    ensemble = mode == "ensemble"
    body = make_body(at=PLACEMENTS[role] if ensemble else SOLO_PLACEMENT,
                     role=role, ensemble=ensemble,
                     points=CAST_POINTS[role] if ensemble else SOLO_POINTS)
    install(body, ensemble=ensemble, role=role)
    return body


def bake(mode, role=None):
    """Bake the selected bodies sequentially and keep one receipt per identity."""
    _engine_path()
    from .cache import bake_cloth, motion_key
    from .render import source_hashes
    if os.environ.get("ADVANCED_DANCE_CLOTH_CACHE", "auto") != "auto":
        raise ValueError("Cloth baking requires the default auto cache policy")
    source_before = source_hashes()
    results = []
    for cast_role in selected_roles(mode, role):
        began = time.monotonic()
        print(json.dumps(dict(event="cloth_bake_started", mode=mode, role=cast_role)), flush=True)
        body = build_one(mode, cast_role)
        key = motion_key(body)
        path = Path(bake_cloth(body))
        if motion_key(body) != key or source_hashes() != source_before:
            raise RuntimeError("Authored sources changed during cloth baking; repeat after freezing the inputs")
        data = np.load(path, mmap_mode="r", allow_pickle=False)
        if not np.isfinite(data).all():
            raise ValueError("The completed cloth cache contains nonfinite positions")
        receipt = dict(schema_version=1, mode=mode, role=cast_role, motion_key=key,
                       duration_seconds=DURATION, snapshot_rate_hz=30, solver_rate_hz=120,
                       cache=str(path.relative_to(ROOT)), sha256=_digest(path),
                       bytes=path.stat().st_size, shape=list(data.shape), dtype=str(data.dtype),
                       source_sha256=source_before, elapsed_seconds=round(time.monotonic()-began, 3))
        _write(path.with_suffix(".json"), receipt)
        results.append(receipt)
        print(json.dumps(dict(event="cloth_bake_complete", mode=mode, role=cast_role,
                              key=key, seconds=receipt["elapsed_seconds"])), flush=True)
        del data, body
    return results


def _frame_worker(mode, frame_index, cache_mode, output):
    """One process per renderer keeps the engine's song module isolated."""
    _engine_path()
    from PIL import Image
    from . import scene
    from .render import frame, make_renderer, source_hashes
    if cache_mode not in ("fresh", "cached"):
        raise ValueError("Unknown comparison cache mode")
    os.environ["ADVANCED_DANCE_CLOTH_CACHE"] = "off" if cache_mode == "fresh" else "required"
    identity = source_hashes()
    original = scene.load_cloth
    observed = []

    def use_cache(body):
        loaded = original(body)
        if cache_mode == "fresh" and loaded:
            raise RuntimeError("Fresh-frame verification unexpectedly loaded a cloth cache")
        if cache_mode == "cached" and not loaded:
            raise RuntimeError("Native cache comparison requires a completed cache for every cast member")
        if not loaded:
            observed.append(dict(role=body.actor.advanced_score.role, loaded=False))
            return False
        path = Path(body.advanced_cloth_cache)
        observed.append(dict(role=body.actor.advanced_score.role, loaded=True,
                             cache=str(path.relative_to(ROOT)), sha256=_digest(path)))
        return True

    scene.load_cloth = use_cache
    print(json.dumps(dict(event="native_cache_frame_started", mode=mode,
                          cache_mode=cache_mode, frame=frame_index)), flush=True)
    began = time.monotonic()
    renderer = make_renderer(1920, 1080, temporal_samples=2, fps=FPS, mode=mode)
    raw = frame(renderer, frame_index, fps=FPS)
    if source_hashes() != identity:
        raise RuntimeError("Picture inputs changed during native cache comparison")
    expected = list(selected_roles(mode))
    if sorted(item["role"] for item in observed) != expected:
        raise RuntimeError("Native cache comparison did not observe every expected cast member")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.frombytes("RGB", (1920, 1080), raw).save(output.with_suffix(".png"), compress_level=3)
    receipt = dict(mode=mode, cache_mode=cache_mode, frame=frame_index,
                   time_seconds=frame_index/FPS, width=1920, height=1080, fps=FPS,
                   temporal_samples=2, raw_rgb_sha256=hashlib.sha256(raw).hexdigest(),
                   source_sha256=identity, cloth=observed,
                   seconds=round(time.monotonic()-began, 3),
                   renderer=renderer.ctx.info["GL_RENDERER"])
    _write(output.with_suffix(".json"), receipt)
    print(json.dumps(dict(event="native_cache_frame_complete", cache_mode=cache_mode,
                          raw_rgb_sha256=receipt["raw_rgb_sha256"], seconds=receipt["seconds"])), flush=True)


def verify_frame(mode, frame_index, output=None):
    if mode not in ("solo", "ensemble") or type(frame_index) is not int or not 0 <= frame_index < int(DURATION*FPS):
        raise ValueError("Choose a film and a frame in 0..1919")
    from .render import source_hashes
    identity = source_hashes()
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:12]
    directory = Path(output) if output else ROOT / f"work/advanced-dance/cache-verification/{mode}-{key}-{frame_index:04d}"
    directory.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONHASHSEED="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", LP_NUM_THREADS="1")
    records = {}
    # Check cached first so a missing bake fails before an expensive fresh solve.
    for cache_mode in ("cached", "fresh"):
        prefix = directory / cache_mode
        subprocess.run([sys.executable, "-m", "tools.advanced_dance.prepare", "_frame",
                        "--mode", mode, "--frame", str(frame_index), "--cache", cache_mode,
                        "--output", str(prefix)], cwd=ROOT, env=env, check=True)
        records[cache_mode] = json.loads(prefix.with_suffix(".json").read_text())
        if records[cache_mode]["source_sha256"] != identity:
            raise RuntimeError("The native comparisons used different authored picture inputs")
    passed = records["cached"]["raw_rgb_sha256"] == records["fresh"]["raw_rgb_sha256"]
    receipt = dict(schema_version=1, passed=passed, mode=mode, frame=frame_index,
                   scope="One native 1080p60 frame with two shutter samples; fresh process in each mode; same environment",
                   records=records)
    _write(directory / "comparison.json", receipt)
    if not passed:
        raise RuntimeError("Fresh and cached native RGB bytes differ; inspect both saved frames before rendering")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    audio = sub.add_parser("audio", help="Prepare and verify original-speed stereo audio")
    audio.add_argument("--mode", choices=("solo", "ensemble", "all"), default="all")
    audio.add_argument("--update-manifest", action="store_true", help="Accept reviewed output-byte changes to an existing audio pin")
    cloth = sub.add_parser("bake", help="Bake selected cast members after inputs are frozen")
    cloth.add_argument("--mode", choices=("solo", "ensemble", "all"), default="all")
    cloth.add_argument("--role", type=int)
    check = sub.add_parser("verify-frame", help="Compare fresh and required-cache native frames")
    check.add_argument("--mode", choices=("solo", "ensemble"), required=True)
    check.add_argument("--frame", type=int, default=891)
    check.add_argument("--output", type=Path)
    worker = sub.add_parser("_frame", help=argparse.SUPPRESS)
    worker.add_argument("--mode", choices=("solo", "ensemble"), required=True)
    worker.add_argument("--frame", type=int, required=True)
    worker.add_argument("--cache", choices=("fresh", "cached"), required=True)
    worker.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "audio":
        for mode in modes(args.mode):
            record = prepare_audio(mode, update_manifest=args.update_manifest)
            print(json.dumps(record), flush=True)
    elif args.command == "bake":
        if args.role is not None and args.mode == "all":
            parser.error("--role requires --mode solo or --mode ensemble")
        for mode in modes(args.mode):
            bake(mode, args.role)
    elif args.command == "verify-frame":
        record = verify_frame(args.mode, args.frame, args.output)
        print(json.dumps(dict(passed=record["passed"], mode=args.mode, frame=args.frame)), flush=True)
    else:
        _frame_worker(args.mode, args.frame, args.cache, args.output)


if __name__ == "__main__":
    main()
