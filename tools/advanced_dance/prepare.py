"""Prepare exact audio, cloth, captured fan trails and native review proofs.

Examples, from the repository root:
  .venv/bin/python -m tools.advanced_dance.prepare audio --mode all
  .venv/bin/python -m tools.advanced_dance.prepare bake --mode solo
  .venv/bin/python -m tools.advanced_dance.prepare bake --mode ensemble --role 2
  .venv/bin/python -m tools.advanced_dance.prepare trails --mode all --captures work/advanced-dance/qa/final
  .venv/bin/python -m tools.advanced_dance.prepare proof --mode solo
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


def _same_array(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return a.shape == b.shape and a.dtype == b.dtype and a.tobytes() == b.tobytes()


def _trail_inputs(body, capture_path, expected_times, hashes):
    """Validate a saved final-FK record before it may replace a live solve."""
    capture_path = Path(capture_path).resolve()
    report_path = capture_path.with_suffix(".json")
    report = json.loads(report_path.read_text())
    binding = report.get("final_fk_capture", {})
    capture_hash = _digest(capture_path)
    if (binding.get("sha256") != capture_hash
            or binding.get("bytes") != capture_path.stat().st_size):
        raise ValueError("The QA receipt does not bind these exact final-FK capture bytes")
    if report.get("error_count") != 0 or report.get("status") == "blocked":
        raise ValueError("Repair the blocking motion errors before preparing production trails")
    if any(report.get("source_hashes", {}).get(name) != digest for name, digest in hashes.items()):
        raise ValueError("Kinematic source changed after the supplied final-FK capture")
    score = body.actor.advanced_score
    expected_actor = dict(height_m=body.rig.height, build=body.rig.build,
                          origin=body.actor.origin.tolist(), seed=body.seed,
                          mode=score.mode, role=score.role)
    if (report.get("performance") != score.name
            or any(report.get("actor", {}).get(name) != value for name, value in expected_actor.items())):
        raise ValueError("The final-FK capture belongs to a different performer or rig")
    if body.frame is not None or body.scale != 1.0 or body.actor.life:
        raise ValueError("Trail capture reuse requires the registered unscaled, fixed-frame actor")
    with np.load(capture_path, allow_pickle=False) as saved:
        if (int(saved["fps"]) != FPS or float(saved["duration"]) != DURATION
                or list(saved["bone_names"]) != body.rig.names):
            raise ValueError("The captured bone ordering or performance clock changed")
        times = saved["times"]
        # QA stores decimal-rounded times. The registered actor canonicalizes
        # every evaluation to six places before solving, including live trails.
        canonical = lambda values: np.asarray([round(float(t), 6) for t in values])
        if (times.shape != expected_times.shape
                or not np.array_equal(canonical(times), canonical(expected_times))):
            raise ValueError("Capture must include all 1,921 canonical 60 Hz states through exact 32.0 seconds")
        data = {name: saved[name] for name in ("P", "A", "M", "origin", "heading")}
    n, bones = len(expected_times), len(body.rig.names)
    contracts = {"P": ((n, bones, 3), np.float64), "A": ((n, bones, 4), np.float64),
                 "M": ((n, bones, 3, 4), np.float32), "origin": ((n, 3), np.float64),
                 "heading": ((n,), np.float64)}
    for name, (shape, dtype) in contracts.items():
        if data[name].shape != shape or data[name].dtype != dtype or not np.isfinite(data[name]).all():
            raise ValueError(f"Invalid native final-FK capture array: {name}")
    return data, dict(capture=str(capture_path), capture_sha256=capture_hash,
                      report=str(report_path), report_sha256=_digest(report_path),
                      actor=expected_actor, status=report["status"],
                      captured_costume_sha256=report["source_hashes"].get("tools/advanced_dance/costume.py"))


def _injected_frame(body, data, index, t):
    from p3d import bodymath as bm
    frame = {name: data[name][index] for name in ("P", "A", "M", "origin")}
    frame.update(D=bm.qmul(frame["A"], body.rig.C),
                 heading=float(data["heading"][index]), speed=0.)
    body.actor._cache.clear()
    body.actor._cache[(round(float(t), 6), True, True, False)] = frame
    return frame


def _capture_tips(body, owned_fans, data, times, probe_indices):
    """Use unchanged fan geometry, and fail if fresh FK differs at probes."""
    saved_cache = dict(body.actor._cache)
    tracks = np.empty((len(owned_fans), len(times), 3), dtype=np.float64)
    checked = []
    try:
        for index, t in enumerate(times):
            t = float(t)
            injected = _injected_frame(body, data, index, t)
            for j, fan in enumerate(owned_fans):
                tracks[j, index] = fan.tip(t)
            if index not in probe_indices:
                continue
            geometry = [fan.geometry(t, diagnostic=True).copy() for fan in owned_fans]
            frames = [tuple(part.copy() for part in fan.hand_frame(t)) for fan in owned_fans]
            body.actor._cache.clear()
            fresh = body.actor.frame(t)
            for name in ("P", "A", "M", "origin", "heading"):
                if not _same_array(np.asarray(injected[name]), np.asarray(fresh[name])):
                    raise ValueError(f"Fresh final FK differs bit-for-bit from capture at {t}: {name}")
            for j, fan in enumerate(owned_fans):
                if (not _same_array(tracks[j, index], fan.tip(t))
                        or not _same_array(geometry[j], fan.geometry(t, diagnostic=True))
                        or any(not _same_array(a, b) for a, b in zip(frames[j], fan.hand_frame(t)))):
                    raise ValueError(f"Captured fan grip/surface/tip differs from the live model at {t}")
            checked.append(index)
    finally:
        body.actor._cache.clear()
        body.actor._cache.update(saved_cache)
    return tracks, checked


def _trails_worker(mode, captures):
    """Build one exact trail cache in a fresh process; never change pictures."""
    import tempfile
    from unittest.mock import patch

    _engine_path()
    from . import props
    from .cache import motion_key
    from .render import source_hashes
    from .scene import make_cast, cuts

    if mode not in ("solo", "ensemble"):
        raise ValueError("Choose an explicit trail mode")
    if "P3D_BODY_ASSET" in os.environ:
        raise ValueError("Unset P3D_BODY_ASSET before preparing registered trails")
    started = time.monotonic()
    preparer_hash = _digest(Path(__file__))
    before = source_hashes()
    names = {"tools/advanced_dance/score.py", "tools/advanced_dance/anatomy.py",
             "tools/advanced_dance/clock.json", "assets/p3d/body_v1.npz"}
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/"engine/p3d").glob("*.py"))
    hashes = {name: before[name] for name in sorted(names)}
    # The real cast factory provides all rig/prop parameters. Cloth never
    # participates in a fan grip and is deliberately not loaded or simulated.
    with patch.dict(os.environ, {"ADVANCED_DANCE_CLOTH_CACHE": "off"}):
        bodies, fans = make_cast(mode == "ensemble")
    times = np.arange(0, DURATION+1/FPS, 1/FPS)
    probes = set(range(0, len(times), 120)) | {1, 2, len(times)-2, len(times)-1, 890, 891, 892}
    for cut in cuts(mode):
        probes.update(i for i in (round(cut*FPS)-1, round(cut*FPS), round(cut*FPS)+1)
                      if 0 <= i < len(times))
    keys = {id(body): motion_key(body) for body in bodies}
    identity = dict(motion=[keys[id(fan.body)] for fan in fans],
                    side=[fan.side for fan in fans], radii=[fan.radius for fan in fans],
                    source=_digest(Path(props.__file__)))
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    path = ROOT/"work/advanced-dance/trail-cache"/(key+".npy")
    tracks = np.empty((len(fans), len(times), 3), dtype=np.float64)
    records = []
    for body in bodies:
        score = body.actor.advanced_score
        data, record = _trail_inputs(body, Path(captures)/(score.name+".npz"), times, hashes)
        indices = [j for j, fan in enumerate(fans) if fan.body is body]
        tips, checked = _capture_tips(body, [fans[j] for j in indices], data, times, probes)
        tracks[indices] = tips
        record.update(fresh_bit_exact_probe_indices=checked, motion_key=keys[id(body)])
        records.append(record)
        print(json.dumps(dict(event="trail_actor_verified", performance=score.name,
                              captured_states=len(times), live_probes=len(checked))), flush=True)
    if not np.isfinite(tracks).all():
        raise ValueError("Nonfinite fan positions cannot enter a completed trail cache")
    # Exercise the unmodified actual consumer in an isolated temporary cache
    # root. A wrong key cannot silently fall back to 8 minutes of new IK.
    with tempfile.TemporaryDirectory(prefix="advanced-trail-check-") as temporary_root:
        temporary = Path(temporary_root)/"work/advanced-dance/trail-cache"/path.name
        temporary.parent.mkdir(parents=True)
        np.save(temporary, tracks, allow_pickle=False)
        def unexpected_live_tip(*args, **kwargs):
            raise RuntimeError("The real GestureLight consumer missed the prepared cache identity")
        with patch.object(props, "ROOT", Path(temporary_root)), \
                patch.object(props.PerformanceFan, "tip", unexpected_live_tip):
            consumer = props.GestureLight(fans, duration=DURATION, ensemble=mode == "ensemble")
        if not _same_array(consumer.tracks, tracks) or not _same_array(consumer.times, times):
            raise RuntimeError("The real GestureLight consumer did not load identical track bytes")
        if (source_hashes() != before or _digest(Path(__file__)) != preparer_hash
                or any(motion_key(body) != keys[id(body)] for body in bodies)):
            raise RuntimeError("Picture sources changed during trail preparation; repeat after freezing")
        for record in records:
            if (_digest(record["capture"]) != record["capture_sha256"]
                    or _digest(record["report"]) != record["report_sha256"]):
                raise RuntimeError("A final-FK capture or QA receipt changed during trail preparation")
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if not _same_array(np.load(path, allow_pickle=False), tracks):
                raise ValueError("Existing trail cache differs; investigate rather than replace it")
        else:
            installed = path.with_name(path.stem+f".{os.getpid()}.partial.npy")
            installed.write_bytes(temporary.read_bytes())
            installed.replace(path)
    receipt = dict(schema_version=1, status="exact_capture_cache_verified", mode=mode,
                   cache=str(path.relative_to(ROOT)), sha256=_digest(path), bytes=path.stat().st_size,
                   cache_identity=identity, shape=list(tracks.shape), dtype=str(tracks.dtype),
                   duration_seconds=DURATION, trajectory_rate_hz=FPS, endpoint_included=True,
                   kinematic_source_hashes=hashes, source_sha256=before, actors=records,
                   preparer_sha256=preparer_hash,
                   scope="All canonical states use captured final FK and the unchanged real fan.tip. Fresh FK, grip and diagnostic surface match bit-for-bit at recorded probes. No resampling or geometry approximation.",
                   elapsed_seconds=round(time.monotonic()-started, 3))
    _write(path.with_suffix(".json"), receipt)
    print(json.dumps(dict(event="trail_cache_complete", mode=mode, cache=str(path),
                          sha256=receipt["sha256"], seconds=receipt["elapsed_seconds"])), flush=True)
    return receipt


def prepare_trails(mode, captures):
    captures = Path(captures).resolve()
    if not captures.is_dir():
        raise ValueError("Supply the directory containing completed motion QA JSON and NPZ files")
    env = dict(os.environ, PYTHONHASHSEED="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", LP_NUM_THREADS="1")
    subprocess.run([sys.executable, "-m", "tools.advanced_dance.prepare", "_trails",
                    "--mode", mode, "--captures", str(captures)], cwd=ROOT, env=env, check=True)


def proof(mode, output=None):
    """Encode only verified final even frames as a separate 30 fps proof."""
    import tempfile
    from fractions import Fraction
    from pipeline.delivery import (audio_encoding_args, get_profile, require_encoder,
                                   stream_validation_errors, video_encoding_args)
    from pipeline.media import probe
    from pipeline.project import load_project
    from pipeline.render import fingerprint, production_lock, shot_directory, valid_frame

    if mode not in ("solo", "ensemble"):
        raise ValueError("Choose an explicit proof mode")
    project = load_project(ROOT, f"advanced-dance-{mode}", check_files=True)
    settings = project.settings("final")
    manifest_hash = _digest(project.manifest)
    finishing_hashes = {name: _digest(ROOT/name) for name in
                       ("tools/advanced_dance/prepare.py", "pipeline/delivery.py", "pipeline/media.py")}
    if (project.frames != 1920 or project.fps != FPS or len(project.shots) != 1
            or (settings["width"], settings["height"], settings["temporal_samples"]) != (1920, 1080, 2)):
        raise ValueError("The even-frame proof requires the registered native 1080p60 final contract")
    profile = get_profile("h264")
    transfer = project.data["delivery"]["source_transfer"]
    require_encoder(profile, source_transfer=transfer)
    source = project.data["audio"]
    audio = ROOT/source["source"]
    if source.get("offset_seconds", 0) != 0 or _digest(audio) != source["source_sha256"]:
        raise ValueError("Prepare and verify the exact 32-second pinned audio first")
    shot = project.shots[0]
    directory = shot_directory(project, "final", shot)
    indices = list(range(0, 1920, 2))
    with production_lock(project.output("final")/".production.lock"):
        key, provenance = fingerprint(project, shot, "final")
        receipt_path = directory/"receipt.json"
        source_receipt = json.loads(receipt_path.read_text())
        if source_receipt.get("fingerprint") != key:
            raise ValueError("The even frames belong to a stale source or renderer fingerprint")
        target = (Path(output).resolve() if output else ROOT/"work/advanced-dance/proofs"/
                  f"{mode}-{key[:12]}"/"Even_Frame_Proof_1080p30.mp4")
        if target.suffix.lower() != ".mp4" or target.exists() or target.with_suffix(".json").exists():
            raise ValueError("Choose a new .mp4 proof output; existing reviews are preserved")
        records = []
        for frame_index in indices:
            path = directory/"frames"/f"frame_{frame_index:06d}.png"
            checksum = source_receipt.get("frames", {}).get(str(frame_index))
            if not checksum or not valid_frame(path, (1920, 1080), checksum, 8):
                raise ValueError(f"Final frame {frame_index} is missing, changed or not verified in the current receipt")
            records.append(dict(frame=frame_index, sha256=checksum))
        target.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        print(json.dumps(dict(event="even_frame_proof_started", mode=mode,
                              source_frames=960, fps=30, output=str(target))), flush=True)
        with tempfile.TemporaryDirectory(prefix="proof-build-", dir=target.parent) as temporary_root:
            temporary = Path(temporary_root)
            for output_index, source_index in enumerate(indices):
                os.link(directory/"frames"/f"frame_{source_index:06d}.png",
                        temporary/f"{output_index:06d}.png")
            movie = temporary/"proof.mp4"
            command = ["ffmpeg", "-v", "error", "-nostdin", "-filter_threads", "2",
                       "-framerate", "30", "-start_number", "0", "-i", str(temporary/"%06d.png"),
                       "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-frames:v", "960",
                       *video_encoding_args(30, profile, source_transfer=transfer),
                       *audio_encoding_args(profile), "-ac", "2", "-t", "32",
                       "-metadata", "comment=Review proof: exact even frames from native 60fps source; 60fps shutter retained",
                       str(movie)]
            subprocess.run(command, check=True)
            metadata = probe(movie)
            errors = stream_validation_errors(metadata, profile, width=1920, height=1080,
                                               fps=30, frames=960, wanted_audio=True)
            for stream in [metadata["format"], *[s for s in metadata["streams"] if s["codec_type"] == "video"]]:
                if Fraction(stream.get("duration", "0")) != 32:
                    errors.append("Proof video and container must be exactly 32 seconds")
            video = next(s for s in metadata["streams"] if s["codec_type"] == "video")
            stamps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
                "-show_entries", "frame=best_effort_timestamp", "-of", "json", str(movie)],
                capture_output=True, text=True, check=True)
            values = json.loads(stamps.stdout)["frames"]
            time_base = Fraction(video["time_base"])
            if (len(values) != 960 or any(Fraction(int(row["best_effort_timestamp"]))*time_base != Fraction(i, 30)
                                          for i, row in enumerate(values))):
                errors.append("Proof timestamps are not exactly n/30 for all 960 frames")
            decoded = subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-err_detect", "explode",
                "-threads", "2", "-i", str(movie), "-map", "0:v:0", "-map", "0:a:0",
                "-progress", "pipe:1", "-nostats", "-f", "null", "-"], capture_output=True, text=True)
            progress = dict(line.split("=", 1) for line in decoded.stdout.splitlines() if "=" in line)
            if (decoded.returncode or decoded.stderr.strip() or progress.get("frame") != "960"
                    or progress.get("progress") != "end"):
                errors.append("Complete proof video/audio decode did not finish cleanly at 960 frames")
            if errors:
                raise ValueError("Invalid proof: "+"; ".join(errors))
            if (fingerprint(project, shot, "final")[0] != key
                    or _digest(audio) != source["source_sha256"]
                    or _digest(project.manifest) != manifest_hash
                    or any(_digest(ROOT/name) != digest for name, digest in finishing_hashes.items())):
                raise RuntimeError("Picture inputs or pinned audio changed during proof encoding")
            for record in records:
                if _digest(directory/"frames"/f"frame_{record['frame']:06d}.png") != record["sha256"]:
                    raise RuntimeError("A source frame changed during proof encoding")
            movie_hash = _digest(movie)
            movie.replace(target)
        report = dict(schema_version=1, status="technical_passed", technical_passed=True,
                      mode=mode, output=str(target), sha256=movie_hash, bytes=target.stat().st_size,
                      width=1920, height=1080, duration_seconds=32, frames=960, fps=30,
                      source_fps=60, source_frame_stride=2, source_frame_indices=indices,
                      source_frame_hashes=records, source_fingerprint=key,
                      source_receipt_sha256=_digest(receipt_path), source_inputs=provenance["inputs"],
                      project_manifest_sha256=manifest_hash, finishing_source_hashes=finishing_hashes,
                      audio_source_sha256=source["source_sha256"], metadata=metadata,
                      source_temporal_samples=2, source_shutter_fraction=.35,
                      absent_cut_frames=[event["frame"] for event in project.data.get("timing", {}).get("events", [])
                                         if event.get("beat") in (16, 32, 48) and event["frame"] % 2],
                      preserved_shutter_seconds=.35/60,
                      scope="Exact final-render even frames at original song time, encoded for 30 fps continuous review. Source 60 fps shutter samples are retained; no image interpolation, rerendering or retiming. Odd source frames and any cuts on odd frames are absent. This is not the final 60 fps delivery or a record of visual approval.",
                      owner_approval=False, elapsed_seconds=round(time.monotonic()-started, 3))
        _write(target.with_suffix(".json"), report)
    print(json.dumps(dict(event="even_frame_proof_complete", mode=mode, output=str(target),
                          sha256=movie_hash, seconds=report["elapsed_seconds"])), flush=True)
    return report


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
    trails = sub.add_parser("trails", help="Prepare exact real fan-tip tracks from bound final-FK captures")
    trails.add_argument("--mode", choices=("solo", "ensemble", "all"), default="all")
    trails.add_argument("--captures", type=Path, required=True)
    proof_parser = sub.add_parser("proof", help="Encode a separate 30 fps proof from verified final even frames")
    proof_parser.add_argument("--mode", choices=("solo", "ensemble"), required=True)
    proof_parser.add_argument("--output", type=Path)
    trail_worker = sub.add_parser("_trails", help=argparse.SUPPRESS)
    trail_worker.add_argument("--mode", choices=("solo", "ensemble"), required=True)
    trail_worker.add_argument("--captures", type=Path, required=True)
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
    elif args.command == "trails":
        for mode in modes(args.mode):
            prepare_trails(mode, args.captures)
    elif args.command == "_trails":
        _trails_worker(args.mode, args.captures)
    elif args.command == "proof":
        proof(args.mode, args.output)
    else:
        _frame_worker(args.mode, args.frame, args.cache, args.output)


if __name__ == "__main__":
    main()
