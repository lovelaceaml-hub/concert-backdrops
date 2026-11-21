"""Independently audit the registered eighteen-second native dance master.

Reads frozen sources and completed media; imports no renderer. It never creates
a replacement baseline, repairs media or certifies natural motion or beauty.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.concert_review.consideration import alignment_window, jsha, read_pcm24, sha

PROJECT = "concert-dance-study"
WIDTH, HEIGHT, FPS, FRAMES, SECONDS = 1920, 1080, 60, 1080, 18
RATE, CHANNELS, SAMPLES = 48000, 2, 864000
WAV_SHA = "0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b"
PCM_SHA = "493d1fa5efeaea437edcfecb241fb536439ec832d6f899750c4282c0d6895f84"
SETTINGS = {"width": WIDTH, "height": HEIGHT, "fps": FPS,
            "temporal_samples": 2, "image_bit_depth": 8}
COLOR = {"color_primaries": "bt709", "color_transfer": "bt709",
         "color_space": "bt709", "color_range": "tv"}
REFERENCE_FRAMES = (360, 480)


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def read(path):
    return json.loads(Path(path).read_text())


def path_at(root, value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def input_hashes(root, mapping):
    check(isinstance(mapping, dict) and bool(mapping), "Empty or invalid source mapping.")
    result = {}
    for name, expected in mapping.items():
        path = (root / name).resolve()
        check(not Path(name).is_absolute() and path.is_relative_to(root),
              f"Source path escapes the repository: {name}")
        check(isinstance(expected, str) and len(expected) == 64, f"Invalid source hash: {name}")
        result[name] = sha(path)
    return result


def run(command, timeout):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=timeout, check=False)
    check(result.returncode == 0 and not result.stderr.strip(),
          f"Command failed or reported decoder errors: {command[0]}: "
          + result.stderr.decode(errors="replace")[-4000:])
    return result.stdout


def probe(movie, timeout, *options):
    return json.loads(run(["ffprobe", "-v", "error", *options,
                           "-of", "json", str(movie)], timeout))


def verify_inputs(root, baseline_path, audio_path):
    baseline = read(baseline_path)
    wanted = {"project": PROJECT, "width": WIDTH, "height": HEIGHT, "fps": FPS,
              "frames": FRAMES, "temporal_samples": 2, "random_seed": 2026,
              "source_frozen": True}
    check(all(baseline.get(k) == v for k, v in wanted.items()),
          "Baseline is not the explicit eighteen-second 1080p60 dance profile.")
    mapping = baseline["source_inputs"]
    check(jsha(mapping) == baseline.get("mapping_sha256"), "Baseline mapping digest is inconsistent.")
    required = {"assets/p3d/body_v1.npz", "tools/concert_dance/__init__.py",
                "tools/concert_dance/performance.py", "tools/concert_dance/scene.py",
                "tools/concert_dance/render.py", "pipeline/render.py"}
    check(required <= mapping.keys(), "Baseline omits a required dance picture dependency.")
    check("tools/concert_review/dance.py" not in mapping
          and "tools/concert_review/README.md" not in mapping,
          "Auditor-owned files unexpectedly appear in the frozen picture mapping.")
    actual = input_hashes(root, mapping)
    changed = [name for name in mapping if actual[name] != mapping[name]]
    check(not changed, f"Frozen picture inputs changed: {changed}")

    manifest_path = root / "projects" / PROJECT / "project.json"
    manifest = read(manifest_path)
    check(manifest.get("project_id") == PROJECT, "Wrong registered project.")
    check(manifest.get("video") == {"width": WIDTH, "height": HEIGHT, "fps": FPS},
          "Project clock or dimensions changed.")
    check(manifest.get("quality", {}).get("review") == {
        k: SETTINGS[k] for k in ("width", "height", "temporal_samples", "image_bit_depth")},
        "Project review settings changed.")
    shots = manifest.get("shots", [])
    check(len(shots) == 1 and all(shots[0].get(k) == v for k, v in {
        "id": "performance", "start_frame": 0, "end_frame_exclusive": FRAMES,
        "renderer": "p3d-kit", "scene": "tools/concert_dance/scene.py", "params": {}}.items()),
        "Expected one continuous dance shot covering frames 0 through 1079.")
    timing = manifest.get("timing", {})
    check(timing.get("fps") == FPS and timing.get("visual_only") is True
          and timing.get("manually_verified") is False and timing.get("events") == [],
          "Unexpected authored dance timing contract.")
    check(manifest.get("audio", {}).get("source_sha256") == WAV_SHA
          and manifest["audio"].get("offset_seconds") == 0,
          "The dance requires the complete canonical score at offset zero.")
    check(sha(audio_path) == WAV_SHA, "Canonical eighteen-second WAV hash mismatch.")
    canonical, pcm_sha, wav_parameters = read_pcm24(audio_path)
    check(pcm_sha == PCM_SHA, "Canonical PCM payload hash mismatch.")
    related = {"timing": timing, "style": read(root / manifest["style"])}
    return baseline, manifest, jsha({"manifest": manifest, "related": related}), canonical, wav_parameters


def verify_receipts(root, movie, baseline, project_identity, shot_path, master_path):
    shot, master = read(shot_path), read(master_path)
    check(shot.get("complete") is True, "The performance shot receipt is incomplete.")
    check(shot.get("shot_id") == "performance", "Wrong shot receipt.")
    provenance = shot["provenance"]
    check(jsha(provenance) == shot.get("fingerprint"), "Shot fingerprint is internally inconsistent.")
    check(provenance.get("inputs") == baseline["source_inputs"], "Shot does not use the supplied frozen mapping.")
    check(provenance.get("settings") == SETTINGS, "Shot finishing resolution or sample settings differ.")
    check(set(shot.get("frames", {})) == {str(i) for i in range(FRAMES)},
          "Shot receipt does not cover exactly 1080 source frames.")
    check(master.get("project_id") == PROJECT and master.get("quality") == "review",
          "Master receipt is not the registered dance review output.")
    check(master.get("project_identity") == project_identity, "Master project identity differs from current registration.")
    check(all(master.get(k) == v for k, v in {
        "width": WIDTH, "height": HEIGHT, "fps": FPS, "frames": FRAMES}.items()),
        "Master receipt dimensions or clock differ.")
    check(master.get("sha256") == sha(movie), "Movie bytes differ from the assembly receipt.")
    check(master.get("audio_source_sha256") == WAV_SHA, "Assembly used a different audio source.")
    check(master.get("shot_fingerprints") == {"performance": shot["fingerprint"]},
          "Master was assembled from a different shot fingerprint.")
    finishing = master.get("finishing_inputs", {})
    check(input_hashes(root, finishing) == finishing, "Finishing inputs changed after assembly.")
    return shot, master


def validate_timestamps(video, frames):
    check(len(frames) == FRAMES, f"Expected 1080 decoded frames, received {len(frames)}.")
    base = Fraction(video["time_base"])
    pts = []
    for index, frame in enumerate(frames):
        value = frame.get("pts", frame.get("best_effort_timestamp"))
        check(value is not None, f"Missing presentation timestamp at frame {index}.")
        pts.append(int(value))
        check((frame.get("width"), frame.get("height")) == (WIDTH, HEIGHT),
              f"Decoded dimensions differ at frame {index}.")
    times = [value * base for value in pts]
    check(all(b > a for a, b in zip(times, times[1:])), "Presentation timestamps are not strictly increasing.")
    mismatches = [i for i, value in enumerate(times) if value != Fraction(i, FPS)]
    check(not mismatches, f"Presentation timestamps differ from the exact 60 fps clock: {mismatches[:12]}.")
    return {"time_base": str(base), "pts": pts, "monotonic": True, "exact_60fps": True,
            "first_seconds": float(times[0]), "last_seconds": float(times[-1])}


def audit_video(movie, folder, timeout):
    metadata = probe(movie, timeout, "-show_streams", "-show_format")
    videos = [s for s in metadata["streams"] if s.get("codec_type") == "video"]
    audios = [s for s in metadata["streams"] if s.get("codec_type") == "audio"]
    check(len(videos) == len(audios) == 1, "Expected exactly one video and one audio stream.")
    video, audio = videos[0], audios[0]
    check((video.get("width"), video.get("height")) == (WIDTH, HEIGHT), "Video must be native 1920 x 1080.")
    check(video.get("codec_name") == "h264" and video.get("pix_fmt") == "yuv420p",
          "Expected RGB8-derived SDR H.264 4:2:0 delivery.")
    check(all(video.get(k) == v for k, v in COLOR.items()), "Expected limited-range BT.709 color tags.")
    check(Fraction(video["avg_frame_rate"]) == FPS and Fraction(video["r_frame_rate"]) == FPS,
          "Video frame-rate metadata is not 60 fps.")
    check(Fraction(video["duration_ts"]) * Fraction(video["time_base"]) == SECONDS,
          "Video stream is not exactly eighteen seconds.")
    frames = probe(movie, timeout, "-select_streams", "v:0", "-show_frames", "-show_entries",
                   "frame=pts,best_effort_timestamp,width,height,pix_fmt")["frames"]
    timestamps = validate_timestamps(video, frames)
    raw = run(["ffmpeg", "-v", "error", "-xerror", "-err_detect", "explode", "-nostdin",
               "-threads", "2", "-i", str(movie), "-map", "0:v:0", "-an", "-sn", "-dn",
               "-fps_mode", "passthrough", "-c:v", "rawvideo", "-pix_fmt", "yuv420p",
               "-threads", "2", "-f", "framemd5", "pipe:1"], timeout)
    log = folder / "video-frames.framemd5"
    log.write_bytes(raw)
    decoded = [line for line in raw.decode().splitlines() if line.strip() and not line.startswith("#")]
    check(len(decoded) == FRAMES, f"Complete FFmpeg decode returned {len(decoded)} frames instead of 1080.")
    check(all(len(line.split(",")) == 6 and int(line.split(",")[4]) == WIDTH * HEIGHT * 3 // 2
              for line in decoded), "Unexpected native decoded frame payload.")
    return {"width": WIDTH, "height": HEIGHT, "fps": FPS, "frames": len(decoded), "seconds": SECONDS,
            "complete_decode": True, "decoder_errors": 0, "color": COLOR,
            "timestamps": timestamps, "frame_hash_log": str(log), "frame_hash_log_sha256": sha(log),
            "stream_metadata": video}, audio


def audit_audio(movie, stream, canonical, wav_parameters, timeout, warnings):
    check(stream.get("codec_name") == "aac", "Audio codec must be AAC.")
    check(int(stream.get("sample_rate", 0)) == RATE and stream.get("channels") == CHANNELS,
          "Audio must be 48 kHz stereo.")
    check(stream.get("channel_layout") == "stereo", "Audio channel layout is not stereo.")
    check(Fraction(stream["duration_ts"]) * Fraction(stream["time_base"]) == SECONDS,
          "AAC logical program duration is not eighteen seconds.")
    check(Fraction(stream.get("start_time", "0")) == 0, "Audio does not start at program time zero.")
    raw = run(["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "2", "-i", str(movie),
               "-map", "0:a:0", "-vn", "-sn", "-dn", "-c:a", "pcm_f32le", "-f", "f32le", "pipe:1"], timeout)
    check(len(raw) % (CHANNELS * 4) == 0, "AAC decode ended with a partial sample.")
    decoded = np.frombuffer(raw, "<f4").reshape(-1, CHANNELS).astype(np.float64)
    padding = len(decoded) - SAMPLES
    check(0 <= padding < 1024, f"Unexpected AAC decoded sample count: {len(decoded)}.")
    check(np.isfinite(decoded).all(), "AAC contains nonfinite samples.")
    original, actual = canonical.reshape(-1), decoded[:SAMPLES].reshape(-1)
    gain = float(np.dot(original, actual) / np.dot(original, original))
    correlation = float(np.corrcoef(original, actual)[0, 1])
    gain_db = 20 * math.log10(abs(gain)) if gain else None
    check(correlation >= 0.98, "Full-program AAC correlation with the canonical score is too low.")
    check(gain_db is not None and abs(gain_db) <= 0.25, "Full-program gain differs from the canonical score.")
    windows = []
    for third in range(3):
        low, high = third * SECONDS / 3 + 0.5, (third + 1) * SECONDS / 3 - 0.5
        starts = [round(t * RATE) for t in np.arange(low, high - 2 + 0.001, 0.25)]
        start = max(starts, key=lambda p: float(np.mean(canonical[p:p + 2 * RATE] ** 2)))
        item = alignment_window(canonical, decoded, start, start + 2 * RATE)
        windows.append(item)
        check(item["source_rms"] > 1e-4, "Alignment window is effectively silent.")
        check(item["zero_lag_correlation"] >= 0.98, "AAC window does not match the intended score time.")
        check(abs(item["best_lag_samples"]) <= 1, f"AAC window is shifted by {item['best_lag_samples']} samples.")
        check(item["fitted_gain_db"] is not None and abs(item["fitted_gain_db"]) <= 0.25,
              "AAC window gain differs from the canonical score.")
    peak = float(np.abs(decoded).max())
    exceedances = int(np.count_nonzero(np.abs(decoded) >= 1))
    if exceedances:
        warnings.append("Decoded AAC exceeds full scale; inspect the reported peak. Codec overshoot alone does not prove clipped source audio.")
    return {"canonical_wav_sha256": WAV_SHA, "canonical_pcm_s24le_sha256": PCM_SHA,
            "canonical_parameters": wav_parameters, "canonical_interval_seconds": [0, SECONDS],
            "decoded_samples_per_channel": len(decoded), "logical_samples_per_channel": SAMPLES,
            "tail_padding_samples_per_channel": padding, "full_program_correlation": correlation,
            "full_program_fitted_gain_db": gain_db,
            "full_program_gain_fitted_residual_rms": float(np.sqrt(np.mean((actual - original * gain) ** 2))),
            "alignment_windows": windows, "peak": peak, "samples_at_or_above_full_scale": exceedances,
            "priming_handling": "Normal FFmpeg MP4 demuxing applies edit lists and skip-sample metadata; trailing AAC padding is counted separately.",
            "interpretation": "Technical alignment to the unchanged canonical score, not ear-verified transients or choreographic sync approval."}


def compare_references(movie, directory, folder, shot, timeout, warnings):
    available = [n for n in REFERENCE_FRAMES if (directory / f"frame_{n:06d}.png").is_file()]
    missing = sorted(set(REFERENCE_FRAMES) - set(available))
    if missing:
        warnings.append(f"Native reference PNGs unavailable for frames {missing}; those comparisons were not performed.")
    if not available:
        return {"compared": [], "unavailable": missing}
    select = "+".join(f"eq(n\\,{n})" for n in available)
    transform = "scale=in_color_matrix=bt709:in_range=tv:out_range=pc:flags=accurate_rnd+full_chroma_int,format=rgb24"
    run(["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-n", "-threads", "2", "-i", str(movie),
         "-map", "0:v:0", "-an", "-vf", f"select={select},{transform}", "-fps_mode", "vfr",
         "-frames:v", str(len(available)), "-threads", "2", str(folder / "selected-%02d.png")], timeout)
    comparisons = []
    for index, frame in enumerate(available, 1):
        source = directory / f"frame_{frame:06d}.png"
        expected = shot["frames"][str(frame)]
        check(sha(source) == expected, f"Reference PNG checksum differs from receipt at frame {frame}.")
        decoded = folder / f"decoded-frame-{frame:06d}.png"
        (folder / f"selected-{index:02d}.png").rename(decoded)
        with Image.open(source) as image:
            check(image.size == (WIDTH, HEIGHT) and image.mode == "RGB", "Reference PNG is not native RGB8.")
            a = np.asarray(image, dtype=np.float32)
        with Image.open(decoded) as image:
            check(image.size == (WIDTH, HEIGHT), "Decoded reference dimensions differ.")
            b = np.asarray(image.convert("RGB"), dtype=np.float32)
        difference = b - a
        mae, mse = float(np.abs(difference).mean()), float(np.mean(difference * difference))
        psnr = 10 * math.log10(255 * 255 / mse) if mse else None
        item = {"frame": frame, "seconds": frame / FPS, "source_path": str(source),
                "source_sha256": expected, "decoded_path": str(decoded), "decoded_sha256": sha(decoded),
                "rgb_mae_8bit_levels": mae, "rgb_psnr_db": psnr}
        comparisons.append(item)
        check(mae <= 10 and (psnr is None or psnr >= 25), f"Gross source/encoded mismatch at frame {frame}.")
        check(sha(source) == expected, f"Reference PNG changed during comparison at frame {frame}.")
    return {"compared": comparisons, "unavailable": missing,
            "decode_transform": "Inverse limited-range BT.709 matrix and range only; no gamma or transfer-function conversion.",
            "limits": "Two selected source frames are rehashed. Full source PNG revalidation remains the pipeline QA responsibility; low RGB error is not artistic approval."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--movie", type=Path, default=Path(f"work/pipeline/{PROJECT}/review/master.mp4"))
    parser.add_argument("--audio", type=Path, default=Path("work/concert-kit/consideration-score.wav"))
    parser.add_argument("--baseline", type=Path,
                        default=Path("project-docs/production-system/evidence/natural-dance-frozen-inputs.json"))
    parser.add_argument("--shot-receipt", type=Path)
    parser.add_argument("--master-receipt", type=Path)
    parser.add_argument("--reference-frames-dir", type=Path)
    parser.add_argument("--out-dir", type=Path, help="New audit directory; existing directories are not overwritten.")
    parser.add_argument("--inputs-only", action="store_true", help="Check frozen inputs and score without auditing a movie.")
    parser.add_argument("--timeout", type=float, default=240, help="Seconds allowed per FFmpeg or FFprobe command.")
    args = parser.parse_args()
    root = args.root.resolve()
    movie, audio, baseline_path = [path_at(root, p) for p in (args.movie, args.audio, args.baseline)]
    shot_path = path_at(root, args.shot_receipt) if args.shot_receipt else movie.parent / "shots/performance/receipt.json"
    master_path = path_at(root, args.master_receipt) if args.master_receipt else movie.parent / "master.json"
    reference_dir = path_at(root, args.reference_frames_dir) if args.reference_frames_dir else shot_path.parent / "frames"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    folder = path_at(root, args.out_dir) if args.out_dir else root / f"work/production-system/final-qa/{PROJECT}/run-{stamp}"
    try:
        check(math.isfinite(args.timeout) and args.timeout > 0, "Timeout must be positive and finite.")
        folder.mkdir(parents=True, exist_ok=False)
    except (OSError, RuntimeError) as exc:
        print(json.dumps({"technical_passed": False, "error": str(exc)}), flush=True)
        return 1
    started, protected, baseline = time.monotonic(), {}, None
    report = {"schema_version": 1, "project": PROJECT, "created_utc": stamp,
              "scope": "inputs_only" if args.inputs_only else "completed_1080p60_movie",
              "movie": str(movie), "audio": str(audio), "baseline": str(baseline_path),
              "clock": {"seconds": SECONDS, "fps": FPS, "frames": FRAMES,
                        "source_start_seconds": 0, "authored_cut_frames": []},
              "errors": [], "warnings": [], "creative_approval": "not_assessed",
              "limits": ["No certification of natural movement, contact accuracy, cloth, fingers or artistic quality.",
                         "Stored 30 Hz poses are interpolated for 60 fps output; this is not new capture detail.",
                         "This audit does not establish a complete 4K movie, HDR or 10-bit output."]}
    try:
        print(json.dumps({"audit_stage": "frozen_sources_and_canonical_score"}), flush=True)
        baseline, manifest, identity, canonical, wav_parameters = verify_inputs(root, baseline_path, audio)
        protected = {p: sha(p) for p in (baseline_path, audio, root / "projects" / PROJECT / "project.json")}
        report["sources"] = {"source_commit": baseline["source_commit"], "input_count": len(baseline["source_inputs"]),
                             "mapping_sha256": baseline["mapping_sha256"], "baseline_sha256": sha(baseline_path),
                             "mapping_matches_current_files": True, "project_identity": identity}
        report["auditor_inputs"] = {str(p.relative_to(ROOT)): sha(p) for p in
                                    (Path(__file__).resolve(), ROOT / "tools/concert_review/consideration.py")}
        if not args.inputs_only:
            shot, master = verify_receipts(root, movie, baseline, identity, shot_path, master_path)
            protected.update({p: sha(p) for p in (movie, shot_path, master_path)})
            report["movie_sha256"] = master["sha256"]
            report["receipts"] = {"shot": str(shot_path), "shot_sha256": sha(shot_path),
                                  "master": str(master_path), "master_sha256": sha(master_path),
                                  "fingerprint": shot["fingerprint"], "complete_frame_coverage": True}
            print(json.dumps({"audit_stage": "complete_native_decode_and_presentation_timestamps"}), flush=True)
            report["video"], audio_stream = audit_video(movie, folder, args.timeout)
            print(json.dumps({"audit_stage": "full_score_and_three_window_aac_alignment"}), flush=True)
            report["audio"] = audit_audio(movie, audio_stream, canonical, wav_parameters, args.timeout, report["warnings"])
            print(json.dumps({"audit_stage": "native_reference_frames_360_and_480"}), flush=True)
            report["references"] = compare_references(movie, reference_dir, folder, shot, args.timeout, report["warnings"])
            check(input_hashes(root, master["finishing_inputs"]) == master["finishing_inputs"],
                  "Finishing inputs changed during independent QA.")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
    try:
        if baseline is not None:
            check(input_hashes(root, baseline["source_inputs"]) == baseline["source_inputs"],
                  "Frozen picture input changed during independent QA.")
        check(all(sha(path) == expected for path, expected in protected.items()),
              "An input, receipt, score or movie changed during independent QA.")
        report["inputs_unchanged_during_audit"] = True
    except (OSError, ValueError, RuntimeError) as exc:
        report["inputs_unchanged_during_audit"] = False
        report["errors"].append(str(exc))
    report["elapsed_seconds"] = time.monotonic() - started
    report["inputs_passed"] = not report["errors"]
    report["technical_passed"] = None if args.inputs_only else not report["errors"]
    report["movie_audited"] = not args.inputs_only and not report["errors"]
    target = folder / "independent-qa.json"
    target.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"report": str(target), "scope": report["scope"],
                      "technical_passed": report["technical_passed"], "inputs_passed": report["inputs_passed"],
                      "errors": report["errors"], "warnings": report["warnings"]}), flush=True)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
