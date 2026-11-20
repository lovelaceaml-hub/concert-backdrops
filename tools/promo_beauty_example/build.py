"""Build the thirty-second beauty study with resumable cloud CPU chunks.

Run with --plan to inspect the exact excerpt, cuts and render commands without
starting a render. The approved production engine and its scene files are read
only. Rendering uses the isolated adapter beside this file.
"""
from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pipeline.delivery import get_profile, stream_validation_errors
from tools.promo_beauty_example.render import (
    ACCOUNT_COMMIT, DURATION, FPS, FRAMES, PICTURE_DELAY, SOURCE_START,
    atomic_json, digest, runtime_identity, source_hashes, validate_analysis,
)

CHUNK_FRAMES = 300
EXPECTED_AUDIO = "70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004"
COLOR_CONTRACT = {
    "name": "legacy_display_gamma_matrix_only",
    "source": "Native RGB8 after the original filmic curve, gamma 2.2, saturation and contrast.",
    "encode": "BT.709 RGB to YUV matrix; full RGB to limited YUV; no transfer-function conversion.",
    "decode_for_comparison": "Inverse BT.709 YUV matrix and limited to full range; no transfer-function conversion.",
    "container_tags": "BT.709 primaries, transfer and matrix; limited range.",
    "precision": "8-bit SDR H.264 4:2:0. No HDR or recovered 10-bit precision is claimed.",
}


def probe(path: Path, *, count_frames: bool = False, timeout: float = 180) -> dict:
    command = ["ffprobe", "-v", "error"]
    if count_frames:
        command += ["-count_frames"]
    command += ["-show_streams", "-show_format", "-of", "json", str(path)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:] or f"Could not inspect {path}")
    return json.loads(result.stdout)


def authored_timeline(source_start: float) -> tuple[list[dict], list[dict]]:
    """Read the authored edit literally, without importing or constructing scenes."""
    path = ROOT / "tools/s11_full2/s11_full2.py"
    tree = ast.parse(path.read_text())
    edit = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "EDIT"
                                                for target in node.targets):
            edit = ast.literal_eval(node.value)
            break
    if not edit or any(not isinstance(row, (tuple, list)) or len(row) < 2 for row in edit):
        raise RuntimeError("Could not read the original authored EDIT table.")
    events = [(float(row[0]), str(row[1])) for row in edit]
    if any(not math.isfinite(t) for t, _ in events) or events != sorted(events):
        raise RuntimeError("The authored EDIT times are not finite and ordered.")
    visual_start = source_start - PICTURE_DELAY
    owner = next((who for t, who in reversed(events) if t <= visual_start + 1e-9), events[0][1])
    cuts = []
    for cue, who in events:
        local = cue + PICTURE_DELAY - source_start
        first_frame = math.ceil(round(local * FPS, 9))
        if 0 < first_frame < FRAMES:
            cuts.append({"source_cue_seconds": cue, "source_film_seconds": cue + PICTURE_DELAY,
                         "nominal_local_seconds": local, "frame": first_frame,
                         "seconds": first_frame / FPS, "owner": who})
    starts = [(0, owner), *((item["frame"], item["owner"]) for item in cuts)]
    shots = [{"id": f"shot-{index:02d}", "owner": who, "start_frame": first,
              "end_frame_exclusive": starts[index + 1][0] if index + 1 < len(starts) else FRAMES}
             for index, (first, who) in enumerate(starts)]
    return cuts, shots


def check_preparation(source_start: float) -> dict:
    validate_analysis()
    base = ROOT / "work/s11_full2"
    provenance_path = base / "provenance.json"
    if not provenance_path.is_file():
        raise RuntimeError("Run the verified original-audio preparation first.")
    provenance = json.loads(provenance_path.read_text())
    if provenance.get("audio_sha256") != EXPECTED_AUDIO:
        raise RuntimeError("Prepared audio provenance does not match the production recording.")
    metadata = probe(base / "score.wav")
    duration = float(metadata.get("format", {}).get("duration", 0))
    if not math.isfinite(duration) or source_start + DURATION > duration + 1e-6:
        raise RuntimeError("The requested excerpt extends beyond the prepared score.")
    import numpy as np
    with np.load(base / "music_fx.npz") as music:
        if float(music["times"][-1]) < source_start + DURATION - 1 / FPS:
            raise RuntimeError("The regenerated music analysis does not cover the requested excerpt.")
    return {"original_recording_sha256": EXPECTED_AUDIO,
            "prepared_score_sha256": digest(base / "score.wav"),
            "features_sha256": digest(base / "features.npz"),
            "music_fx_sha256": digest(base / "music_fx.npz"),
            "preparation_provenance_sha256": digest(provenance_path),
            "analysis_origin": "Regenerated from the verified original recording with the project analysis scripts."}


def reusable(movie: Path, expected: dict) -> bool:
    receipt = movie.with_suffix(".json")
    if not movie.is_file() or not receipt.is_file():
        return False
    try:
        previous = json.loads(receipt.read_text())
        return (all(previous.get(key) == value for key, value in expected.items())
                and previous.get("bytes") == movie.stat().st_size
                and previous.get("sha256") == digest(movie))
    except (OSError, ValueError, TypeError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, choices=(1, 2, 3, 4), default=2)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--samples", type=int, choices=(1, 2, 3, 4), default=2)
    parser.add_argument("--source-start", type=float, default=SOURCE_START)
    parser.add_argument("--fade-in", type=float, default=0.12, help="Excerpt audio entry fade in seconds; 0 disables it.")
    parser.add_argument("--fade-out", type=float, default=0.25, help="Excerpt audio exit fade in seconds; 0 disables it.")
    parser.add_argument("--keep-grain", action="store_true")
    parser.add_argument("--directory", type=Path, default=ROOT / "work/promo-beauty-rebuild/final")
    parser.add_argument("--plan", action="store_true", help="Inspect the plan without rendering or writing output files.")
    args = parser.parse_args()
    if sys.platform == "darwin":
        parser.error("Use the cloud CPU environment; Mac rendering is disabled.")
    if min(args.width, args.height) < 32 or args.width % 2 or args.height % 2:
        parser.error("Use positive even dimensions of at least 32 pixels.")
    if args.width * 9 != args.height * 16:
        parser.error("The authored world uses a 16:9 composition.")
    if not math.isfinite(args.source_start) or args.source_start < PICTURE_DELAY:
        parser.error("The excerpt must start at or after the original picture delay.")
    if any(not math.isfinite(v) or not 0 <= v <= DURATION / 2 for v in (args.fade_in, args.fade_out)):
        parser.error("Audio fades must be finite and between 0 and half the excerpt duration.")
    os.environ.update(PYTHONHASHSEED="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                      LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="2", DRAFT="0")
    started = time.monotonic()
    preparation = check_preparation(args.source_start)
    inputs, runtime = source_hashes(), runtime_identity()
    cuts, shots = authored_timeline(args.source_start)
    folder = args.directory.resolve()
    os.environ["BEAUTY_STOP_FILE"] = str(folder / "STOP")
    if (folder / "STOP").exists():
        raise RuntimeError("This round is stopped. Remove its STOP marker only when resuming the requested work.")
    parameters = {"width": args.width, "height": args.height, "fps": FPS,
                  "source_start": args.source_start, "picture_delay": PICTURE_DELAY,
                  "hdr_motion_samples": args.samples, "grain": args.keep_grain}
    expected_common = {**parameters, "source_sha256": inputs, "runtime": runtime}
    jobs = []
    for part, start in enumerate(range(0, FRAMES, CHUNK_FRAMES)):
        end = min(start + CHUNK_FRAMES, FRAMES)
        movie = folder / f"part-{part:02d}.mp4"
        command = [sys.executable, str(Path(__file__).with_name("render.py")),
                   "--width", str(args.width), "--height", str(args.height), "--samples", str(args.samples),
                   "--source-start", repr(args.source_start), "--start", str(start), "--end", str(end),
                   "--out", str(movie)]
        if args.keep_grain:
            command.append("--keep-grain")
        jobs.append({"part": part, "start": start, "end": end, "movie": movie, "command": command})
    # Longest likely jobs first: detailed live-body shots cost more than city
    # views. This changes queue order only; output and concatenation stay ordered.
    weights = {"dance": 3.0, "stage": 2.0, "proc": 2.0}
    def estimated_cost(job):
        return sum(max(0, min(job["end"], shot["end_frame_exclusive"]) - max(job["start"], shot["start_frame"]))
                   * weights.get(shot["owner"], 1.0) for shot in shots)
    schedule = sorted(jobs, key=estimated_cost, reverse=True)
    plan = {"frames": FRAMES, "duration_seconds": DURATION, "workers": args.workers,
            "render_queue": [job["part"] for job in schedule],
            "parameters": parameters, "audio_trim": [args.source_start, args.source_start + DURATION],
            "audio_fades_seconds": {"in": args.fade_in, "out": args.fade_out}, "audio_retimed": False,
            "color_contract": COLOR_CONTRACT, "declared_cuts": cuts, "shots": shots,
            "prepared_inputs": preparation,
            "source_inputs_fingerprint": hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
            "commands": [job["command"] for job in jobs]}
    print(json.dumps({"event": "plan", **plan}, indent=2), flush=True)
    if args.plan:
        return 0
    folder.mkdir(parents=True, exist_ok=True)
    atomic_json(folder / "build-plan.json", plan)
    stopped = threading.Event()
    lock = threading.Lock()
    active: dict[int, subprocess.Popen] = {}

    def render_part(job: dict) -> dict:
        movie = job["movie"]
        expected = {**expected_common, "start": job["start"], "end": job["end"]}
        if reusable(movie, expected):
            return {"part": job["part"], "reused": True, "sha256": digest(movie)}
        logpath = movie.with_suffix(".log")
        with logpath.open("w") as log:
            with lock:
                if stopped.is_set():
                    raise RuntimeError("Render round stopped after another chunk failed.")
                process = subprocess.Popen(job["command"], cwd=ROOT, env=dict(os.environ),
                                           stdout=log, stderr=subprocess.STDOUT)
                active[job["part"]] = process
            try:
                return_code = process.wait()
            finally:
                with lock:
                    active.pop(job["part"], None)
        if return_code:
            tail = "\n".join(logpath.read_text(errors="replace").splitlines()[-16:])
            raise RuntimeError(f"Chunk {job['part']} failed with exit {return_code}:\n{tail}")
        if not reusable(movie, expected):
            raise RuntimeError(f"Chunk {job['part']} finished without a matching source/runtime/parameter receipt.")
        return {"part": job["part"], "reused": False, "sha256": digest(movie)}

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(render_part, job) for job in schedule]
        try:
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(json.dumps({"event": "chunk_complete", **result}), flush=True)
        except BaseException:
            stopped.set()
            with lock:
                for process in active.values():
                    if process.poll() is None:
                        process.terminate()
            for future in futures:
                future.cancel()
            raise
    if source_hashes() != inputs:
        raise RuntimeError("Source inputs changed during the frozen render round.")
    source = ROOT / "work/s11_full2/score.wav"
    audio = folder / "score-30s.wav"
    audio_temporary = folder / "score-30s.assembling.wav"
    filters = [f"atrim=start={args.source_start:.9f}:end={args.source_start + DURATION:.9f}", "asetpts=PTS-STARTPTS"]
    if args.fade_in:
        filters.append(f"afade=t=in:st=0:d={args.fade_in:.9f}")
    if args.fade_out:
        filters.append(f"afade=t=out:st={DURATION - args.fade_out:.9f}:d={args.fade_out:.9f}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-af", ",".join(filters),
                    "-t", str(DURATION), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(audio_temporary)],
                   check=True, timeout=120)
    audio_temporary.replace(audio)
    playlist = folder / "concat.txt"
    playlist.write_text("".join(f"file '{job['movie'].name}'\n" for job in jobs))
    label = "4K60" if (args.width, args.height) == (3840, 2160) else f"{args.height}p60"
    output = folder / f"Song11-Beauty-Study-30s-{label}.mp4"
    temporary = output.with_name(output.stem + ".assembling.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(playlist),
                    "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "320k", "-ar", "48000", "-t", str(DURATION), "-movflags", "+faststart+write_colr",
                    str(temporary)], check=True, timeout=180)
    metadata = probe(temporary, count_frames=True)
    errors = stream_validation_errors(metadata, get_profile("h264"), width=args.width, height=args.height,
                                     fps=FPS, frames=FRAMES, wanted_audio=True)
    if errors:
        raise RuntimeError("Assembly validation failed: " + "; ".join(errors))
    if source_hashes() != inputs or digest(source) != preparation["prepared_score_sha256"]:
        raise RuntimeError("Source or prepared audio changed before delivery was finalized.")
    report = {"output": str(output), "filename": output.name, "sha256": digest(temporary),
              "bytes": temporary.stat().st_size, "frames": FRAMES, "duration_seconds": DURATION,
              **parameters, "native_capture": True, "upscaled_from_video": False,
              "source_sha256": inputs, "runtime": runtime, "source_account_commit": ACCOUNT_COMMIT,
              "completed_s11_master_inspected": False, "prepared_inputs": preparation,
              "audio": {"source": str(source), "source_sha256": preparation["prepared_score_sha256"],
                        "original_recording_sha256": EXPECTED_AUDIO,
                        "trim_seconds": [args.source_start, args.source_start + DURATION],
                        "entry_fade_seconds": args.fade_in, "exit_fade_seconds": args.fade_out,
                        "retimed": False, "excerpt": str(audio), "excerpt_sha256": digest(audio),
                        "codec": "aac", "bitrate": "320k", "sample_rate": 48000, "channels": 2},
              "color_contract": COLOR_CONTRACT, "declared_cuts": cuts, "shots": shots,
              "chunks": sorted(results, key=lambda item: item["part"]), "metadata": metadata,
              "technical_passed": True, "validation_scope": "Assembly stream, clock and frame-count checks only.",
              "creative_approval": "not_assessed", "elapsed_seconds": time.monotonic() - started}
    temporary.replace(output)
    atomic_json(folder / "delivery.json", report)
    print(json.dumps({"event": "complete", "output": str(output), "frames": FRAMES,
                      "native_size": [args.width, args.height], "technical_passed": True,
                      "creative_approval": "not_assessed", "elapsed_seconds": report["elapsed_seconds"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
