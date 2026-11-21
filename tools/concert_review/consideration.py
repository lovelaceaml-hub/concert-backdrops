"""Independent, read-only checks for the completed Consideration master.

Only work/production-system/final-qa receives new files. No renderer is imported.
After the first registered preview receipt, use --freeze-only before the full
render. Run without that option after master.mp4, master.json and qa.json finish.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw
from scipy.signal import correlate

PROJECT = "concert-kit-consideration"
WIDTH, HEIGHT, FPS, FRAMES, RATE, CHANNELS = 1920, 1080, 60, 1080, 48000, 2
SAMPLES = 864000
WAV_SHA = "0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b"
PCM_SHA = "493d1fa5efeaea437edcfecb241fb536439ec832d6f899750c4282c0d6895f84"
ORIGINAL_SHA = "2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def jsha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def save_new(path, value):
    with Path(path).open("x") as target:
        json.dump(value, target, indent=2, allow_nan=False)
        target.write("\n")


def command(argv):
    completed = subprocess.run(argv, capture_output=True, check=False)
    if completed.returncode or completed.stderr.strip():
        raise RuntimeError(f"Command failed or reported decoder errors: {argv[0]}: {completed.stderr.decode(errors='replace')[:3000]}")
    return completed.stdout


def probe(path, *args):
    return json.loads(command(["ffprobe", "-v", "error", *args, "-of", "json", str(path)]))


def paths(root):
    project = root / "projects" / PROJECT / "project.json"
    directory = root / "work/pipeline" / PROJECT / "review"
    return project, directory, root / "work/concert-kit/consideration-score.wav"


def current_hashes(root, expected):
    return {name: sha(root / name) for name in expected}


def picture_contract(root, manifest):
    related = {}
    for name in ("timing", "style"):
        value = manifest.get(name, {})
        related[name] = read(root / value) if isinstance(value, str) else value
    return {"video": manifest["video"], "quality": manifest["quality"]["review"],
            "shots": manifest["shots"], "seed": manifest["production"]["random_seed"], **related}


def freeze(root, audit):
    target = audit / "frozen-inputs.json"
    project, directory, wav = paths(root)
    receipt_path = directory / "shots/approach/receipt.json"
    receipt = read(receipt_path)
    provenance = receipt["provenance"]
    if jsha(provenance) != receipt["fingerprint"]:
        raise RuntimeError("Initial render receipt has inconsistent provenance.")
    if current_hashes(root, provenance["inputs"]) != provenance["inputs"]:
        raise RuntimeError("A frozen picture input already differs from its rendering receipt.")
    if sha(wav) != WAV_SHA:
        raise RuntimeError("Canonical source audio differs from the expected WAV.")
    manifest = read(project)
    value = {"schema_version": 1, "recorded_at_utc": now(), "project": PROJECT,
             "initial_receipt": str(receipt_path.relative_to(root)), "initial_receipt_sha256": sha(receipt_path),
             "initial_shot_fingerprint": receipt["fingerprint"],
             "inputs": provenance["inputs"], "inputs_sha256": jsha(provenance["inputs"]),
             "common_provenance": {key: val for key, val in provenance.items() if key != "shot"},
             "picture_contract": picture_contract(root, manifest), "project_manifest_sha256": sha(project),
             "canonical_audio_sha256": sha(wav)}
    save_new(target, value)
    print(json.dumps({"baseline": str(target), "input_count": len(value["inputs"]),
                      "inputs_sha256": value["inputs_sha256"]}), flush=True)


def read_pcm24(path):
    with wave.open(str(path), "rb") as source:
        params = {"rate": source.getframerate(), "channels": source.getnchannels(),
                  "sample_width": source.getsampwidth(), "samples_per_channel": source.getnframes()}
        raw = source.readframes(source.getnframes())
    if params != {"rate": RATE, "channels": CHANNELS, "sample_width": 3, "samples_per_channel": SAMPLES}:
        raise RuntimeError(f"Unexpected canonical WAV parameters: {params}")
    packed = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.int32)
    signed = packed[:, 0] | (packed[:, 1] << 8) | (packed[:, 2] << 16)
    signed = np.where(signed & 0x800000, signed - 0x1000000, signed)
    return signed.reshape(-1, CHANNELS).astype(np.float64) / 8388608, hashlib.sha256(raw).hexdigest(), params


def alignment_window(reference, decoded, start, end, max_lag=2400):
    x = reference[start:end].mean(axis=1)
    y = decoded[start - max_lag:end + max_lag].mean(axis=1)
    x = x - x.mean()
    sums = np.r_[0.0, np.cumsum(y)]
    squares = np.r_[0.0, np.cumsum(y * y)]
    n = len(x)
    totals = sums[n:] - sums[:-n]
    energy = np.maximum(squares[n:] - squares[:-n] - totals * totals / n, 1e-30)
    correlations = correlate(y, x, mode="valid", method="fft") / np.sqrt(np.dot(x, x) * energy)
    best = int(np.argmax(correlations))
    target = decoded[start:end].reshape(-1)
    original = reference[start:end].reshape(-1)
    gain = float(np.dot(original, target) / np.dot(original, original))
    error = target - original * gain
    return {"start_seconds": start / RATE, "end_seconds": end / RATE,
            "source_rms": float(np.sqrt(np.mean(original * original))),
            "zero_lag_correlation": float(correlations[max_lag]),
            "best_lag_samples": best - max_lag, "best_lag_seconds": (best - max_lag) / RATE,
            "best_correlation": float(correlations[best]), "fitted_gain": gain,
            "fitted_gain_db": 20 * math.log10(abs(gain)) if gain else None,
            "gain_fitted_residual_rms": float(np.sqrt(np.mean(error * error)))}


def observed_batches(directory, shots):
    batches = []
    for shot in shots:
        current = None
        log = directory / "shots" / shot["id"] / "render.log"
        for line in log.read_text().splitlines():
            if line.startswith("COMMAND "):
                current = {"shot": shot["id"], "frames": []}
                batches.append(current)
            match = re.match(r"concert kit frame (\d+), temporal samples (\d+)", line)
            if match and current is not None:
                current["frames"].append(int(match.group(1)))
                current.setdefault("temporal_samples", set()).add(int(match.group(2)))
    return [{"shot": b["shot"], "start_frame": min(b["frames"]),
             "end_frame_exclusive": max(b["frames"]) + 1, "logged_frames": len(b["frames"]),
             "contiguous": b["frames"] == list(range(min(b["frames"]), max(b["frames"]) + 1)),
             "temporal_samples": sorted(b.get("temporal_samples", set()))}
            for b in batches if b["frames"]]


def read_exact(stream, size):
    data = bytearray()
    while len(data) < size:
        block = stream.read(size - len(data))
        if not block:
            break
        data.extend(block)
    return bytes(data)


def audit_master(root, audit):
    baseline = read(audit / "frozen-inputs.json")
    project_path, directory, wav = paths(root)
    master = directory / "master.mp4"
    for required in (master, directory / "master.json", directory / "qa.json"):
        if not required.is_file():
            raise RuntimeError(f"Final delivery is not ready: {required}")
    run_dir = audit / ("run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"))
    run_dir.mkdir(parents=True, exist_ok=False)
    report = {"schema_version": 1, "started_at_utc": now(), "errors": [], "warnings": [],
              "scope": "Independent technical decode, timing, audio alignment, source provenance and selected RGB checks. No real-time playback or artistic approval is claimed."}
    errors, warnings = report["errors"], report["warnings"]

    def check(condition, message):
        if not condition:
            errors.append(message)

    try:
        print("Checking delivery identity and frozen source inputs", flush=True)
        manifest = read(project_path)
        receipt = read(directory / "master.json")
        master_sha = sha(master)
        report["master"] = {"path": str(master), "bytes": master.stat().st_size, "sha256": master_sha,
                            "receipt_sha256": sha(directory / "master.json")}
        check(receipt.get("sha256") == master_sha, "Master SHA256 differs from its assembly receipt.")
        check(sha(wav) == WAV_SHA == baseline["canonical_audio_sha256"], "Canonical WAV identity changed.")
        current = current_hashes(root, baseline["inputs"])
        changed = [name for name in current if current[name] != baseline["inputs"][name]]
        check(not changed, "Frozen picture inputs changed: " + ", ".join(changed))
        check(picture_contract(root, manifest) == baseline["picture_contract"], "The project picture contract changed since the freeze checkpoint.")
        related = {key: picture_contract(root, manifest)[key] for key in ("timing", "style")}
        check(receipt.get("project_identity") == jsha({"manifest": manifest, "related": related}), "Master project identity differs from the current manifest.")
        finishing = receipt.get("finishing_inputs", {})
        check(bool(finishing) and current_hashes(root, finishing) == finishing, "Recorded finishing inputs no longer match their source files.")
        report["source_freeze"] = {"input_count": len(current), "baseline_inputs_sha256": baseline["inputs_sha256"],
                                   "current_inputs_sha256": jsha(current), "changed_paths": changed,
                                   "baseline_picture_contract_sha256": jsha(baseline["picture_contract"]),
                                   "current_picture_contract_sha256": jsha(picture_contract(root, manifest)),
                                   "project_manifest_sha256": sha(project_path),
                                   "assembly_source": receipt.get("source"), "finishing_input_count": len(finishing)}
        shot_receipts = {}
        frame_sources = {}
        for shot in manifest["shots"]:
            shot_dir = directory / "shots" / shot["id"]
            item = read(shot_dir / "receipt.json")
            shot_receipts[shot["id"]] = item
            check(item.get("complete") is True, f"Shot {shot['id']} is not complete.")
            check(jsha(item["provenance"]) == item["fingerprint"], f"Shot {shot['id']} fingerprint is internally inconsistent.")
            check(receipt.get("shot_fingerprints", {}).get(shot["id"]) == item["fingerprint"], f"Master does not use the current {shot['id']} receipt.")
            common = {key: value for key, value in item["provenance"].items() if key != "shot"}
            check(common == baseline["common_provenance"], f"Shot {shot['id']} differs from the frozen common provenance.")
            check(item["provenance"]["shot"] == shot, f"Shot definition changed: {shot['id']}.")
            wanted = set(range(shot["start_frame"], shot["end_frame_exclusive"]))
            check(set(map(int, item["frames"])) == wanted, f"Shot {shot['id']} frame receipt is incomplete or contains extra frames.")
            for frame in wanted:
                frame_sources[frame] = (shot_dir / f"frames/frame_{frame:06d}.png", item["frames"].get(str(frame)))
        check(set(frame_sources) == set(range(FRAMES)), "Source shot ranges do not cover the exact 1080 output frames.")
        report["shot_fingerprints"] = {key: item["fingerprint"] for key, item in shot_receipts.items()}

        print("Probing all video frames and exact presentation timestamps", flush=True)
        metadata = probe(master, "-show_streams", "-show_format")
        videos = [s for s in metadata["streams"] if s["codec_type"] == "video"]
        audios = [s for s in metadata["streams"] if s["codec_type"] == "audio"]
        check(len(videos) == len(audios) == 1, "Expected exactly one video and one audio stream.")
        video, audio = videos[0], audios[0]
        decoded = probe(master, "-select_streams", "v:0", "-show_frames", "-show_entries",
                        "frame=pts,best_effort_timestamp,duration,pkt_duration,width,height,pix_fmt")
        frames = decoded["frames"]
        base = Fraction(video["time_base"])
        times = [int(f.get("pts", f["best_effort_timestamp"])) * base for f in frames]
        pts_errors = [i for i, stamp in enumerate(times) if stamp != Fraction(i, FPS)]
        check(len(frames) == FRAMES, f"Decoded video has {len(frames)} frames instead of 1080.")
        check(not pts_errors, f"Video presentation timestamps differ from the exact 60 fps clock: {pts_errors[:12]}.")
        check((video.get("width"), video.get("height")) == (WIDTH, HEIGHT), "Video dimensions are not native 1920x1080.")
        check(all((f.get("width"), f.get("height")) == (WIDTH, HEIGHT) for f in frames), "Decoded frame dimensions vary.")
        check(Fraction(video["avg_frame_rate"]) == Fraction(FPS) and Fraction(video["r_frame_rate"]) == Fraction(FPS), "Video frame-rate metadata is not 60 fps.")
        check(Fraction(video["duration_ts"]) * base == 18, "Video stream duration is not exactly 18 seconds.")
        wanted_color = {"color_primaries": "bt709", "color_transfer": "bt709", "color_space": "bt709", "color_range": "tv"}
        actual_color = {key: video.get(key) for key in wanted_color}
        check(actual_color == wanted_color, "Video color metadata is not limited-range BT.709 throughout.")
        check(video.get("codec_name") == "h264" and video.get("pix_fmt") == "yuv420p", "Unexpected video codec or pixel format.")
        report["video"] = {"decoded_frames": len(frames), "width": video["width"], "height": video["height"],
                           "average_fps": video["avg_frame_rate"], "time_base": video["time_base"],
                           "first_pts_seconds": float(times[0]), "last_pts_seconds": float(times[-1]),
                           "pts_mismatch_count": len(pts_errors), "duration_seconds": float(Fraction(video["duration_ts"]) * base),
                           "color": actual_color, "decoder_errors": 0}

        print("Checking AAC peaks, priming and alignment with canonical PCM", flush=True)
        check(int(audio.get("sample_rate", 0)) == RATE and audio.get("channels") == CHANNELS, "Audio must be 48 kHz stereo.")
        check(audio.get("channel_layout") == "stereo", "Audio channel layout is not stereo.")
        audio_duration = Fraction(audio["duration_ts"]) * Fraction(audio["time_base"])
        check(audio_duration == 18, "Audio stream program duration is not exactly 18 seconds.")
        check(float(audio.get("start_time", "0")) == 0, "Audio stream does not begin at program time zero.")
        original, pcm_sha, wav_params = read_pcm24(wav)
        check(pcm_sha == PCM_SHA, "Canonical PCM payload differs from the verified excerpt.")
        raw = command(["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "2", "-i", str(master),
                       "-map", "0:a:0", "-vn", "-sn", "-dn", "-c:a", "pcm_f32le", "-f", "f32le", "pipe:1"])
        decoded_audio = np.frombuffer(raw, "<f4").reshape(-1, CHANNELS).astype(np.float64)
        padding = len(decoded_audio) - SAMPLES
        check(0 <= padding < 1024, f"Unexpected AAC decoded sample count: {len(decoded_audio)} samples per channel.")
        check(np.all(np.isfinite(decoded_audio)), "Decoded audio contains non-finite values.")
        peak = float(np.max(np.abs(decoded_audio)))
        excess = int(np.count_nonzero(np.abs(decoded_audio) >= 1.0))
        check(excess == 0, f"Decoded AAC has {excess} samples at or above full scale.")
        alignments = []
        for low, high in ((0.5, 5.5), (6.5, 11.5), (12.5, 17.5)):
            candidates = [round(t * RATE) for t in np.arange(low, high - 2 + 0.001, 0.25)]
            start = max(candidates, key=lambda p: float(np.mean(original[p:p + 2 * RATE] ** 2)))
            item = alignment_window(original, decoded_audio, start, start + 2 * RATE)
            alignments.append(item)
            check(item["source_rms"] > 1e-4, "Selected alignment window is effectively silent.")
            check(item["zero_lag_correlation"] >= 0.98, "Decoded AAC does not sufficiently correlate at the intended source time.")
            check(abs(item["best_lag_samples"]) <= 1, f"Audio alignment differs by {item['best_lag_samples']} samples.")
        packets = probe(master, "-select_streams", "a:0", "-show_packets")["packets"]
        provenance = read(root / "work/concert-kit/audio-provenance.json")
        check(provenance.get("source_sha256") == ORIGINAL_SHA and provenance.get("source_start_seconds") == 137.5
              and provenance.get("source_end_seconds") == 155.5 and provenance.get("time_stretch") is False,
              "Prepared excerpt provenance does not identify the intended unchanged-speed source interval.")
        report["audio"] = {"codec": audio.get("codec_name"), "rate": int(audio["sample_rate"]),
                           "channels": audio["channels"], "stream_duration_seconds": float(audio_duration),
                           "decoded_samples_per_channel": len(decoded_audio), "logical_program_samples_per_channel": SAMPLES,
                           "decoded_tail_padding_samples_per_channel": padding,
                           "decoded_peak": peak, "decoded_peak_dbfs": 20 * math.log10(peak) if peak else None,
                           "samples_at_or_above_full_scale": excess,
                           "canonical_wav_sha256": sha(wav), "canonical_pcm_s24le_sha256": pcm_sha,
                           "canonical_wav_parameters": wav_params, "source_provenance": provenance,
                           "alignment_windows": alignments,
                           "aac_first_packet": packets[0], "aac_last_packet": packets[-1],
                           "priming_handling": "FFmpeg demuxer/decoder applies the MP4 edit list and skip-samples metadata. Correlation uses logical program time zero; possible sub-frame trailing AAC padding is recorded separately.",
                           "interpretation": "Sample alignment with the exact prepared excerpt is technical evidence, not musical or creative synchronization approval."}

        print("Comparing decoded native RGB at actual cuts and worker boundaries", flush=True)
        batches = observed_batches(directory, manifest["shots"])
        cuts = {s["start_frame"] for s in manifest["shots"] if s["start_frame"] > 0}
        boundaries = sorted({b["start_frame"] for b in batches if b["start_frame"] > 0} | cuts)
        selected = {0, 180, 360, 390, 420, 570, 660, 690, 720, 900, 1050, 1079}
        for boundary in boundaries:
            selected.update(f for f in (boundary - 1, boundary, boundary + 1) if 0 <= f < FRAMES)
        selected = sorted(selected)
        select = "+".join(f"eq(n\\,{frame})" for frame in selected)
        filters = f"select={select},scale=in_color_matrix=bt709:in_range=tv:out_range=pc:flags=accurate_rnd+full_chroma_int,format=rgb24"
        argv = ["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "2", "-filter_threads", "1",
                "-i", str(master), "-map", "0:v:0", "-an", "-sn", "-dn", "-vf", filters,
                "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
        small, source_small, comparisons = {}, {}, []
        evidence_frames = {0, 179, 180, 360, 390, 570, 660, 690, 719, 720, 1050, 1079}
        stderr_path = run_dir / "video-decode.stderr.txt"
        with stderr_path.open("wb") as stderr:
            worker = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=stderr)
            try:
                for frame in selected:
                    data = read_exact(worker.stdout, WIDTH * HEIGHT * 3)
                    if len(data) != WIDTH * HEIGHT * 3:
                        raise RuntimeError(f"Video decoder ended before selected frame {frame}.")
                    rgb = np.frombuffer(data, np.uint8).reshape(HEIGHT, WIDTH, 3)
                    source_path, expected_sha = frame_sources[frame]
                    check(sha(source_path) == expected_sha, f"Source PNG checksum changed at frame {frame}.")
                    with Image.open(source_path) as image:
                        native = np.asarray(image.convert("RGB"), np.float32)
                    difference = rgb.astype(np.float32) - native
                    mse = float(np.mean(difference * difference))
                    mae = float(np.mean(np.abs(difference)))
                    psnr = 10 * math.log10(255 * 255 / mse) if mse else None
                    check(mae <= 10 and (psnr is None or psnr >= 25), f"Gross source/encoded RGB mismatch at frame {frame}.")
                    comparisons.append({"frame": frame, "time_seconds": frame / FPS,
                                        "source_png_sha256": expected_sha, "decoded_rgb_sha256": hashlib.sha256(data).hexdigest(),
                                        "mean_absolute_error_8bit": mae, "psnr_db": psnr,
                                        "near_white_pixel_fraction": float(np.mean(np.min(rgb, axis=2) >= 252))})
                    picture = Image.fromarray(rgb)
                    small[frame] = picture.resize((320, 180), Image.Resampling.BOX)
                    source_small[frame] = Image.fromarray(native.astype(np.uint8)).resize((320, 180), Image.Resampling.BOX)
                    if frame in evidence_frames:
                        picture.save(run_dir / f"decoded-frame-{frame:06d}.png")
                extra = worker.stdout.read(1)
                check(not extra, "Video decoder returned more selected frames than requested.")
                returncode = worker.wait(timeout=120)
                check(returncode == 0, f"Full video decode exited with code {returncode}.")
            finally:
                if worker.poll() is None:
                    worker.kill()
                    worker.wait()
        check(not stderr_path.read_text().strip(), "Video decode reported errors; see video-decode.stderr.txt.")
        boundary_metrics = []
        sheet = Image.new("RGB", (960, 210 * len(boundaries)), "#111827")
        draw = ImageDraw.Draw(sheet)
        for row, boundary in enumerate(boundaries):
            decoded_delta = float(np.mean(np.abs(np.asarray(small[boundary], float) - np.asarray(small[boundary - 1], float))))
            source_delta = float(np.mean(np.abs(np.asarray(source_small[boundary], float) - np.asarray(source_small[boundary - 1], float))))
            kind = "authored cut" if boundary in cuts else "worker batch"
            boundary_metrics.append({"frame": boundary, "kind": kind,
                                     "decoded_adjacent_mae_320px": decoded_delta, "source_adjacent_mae_320px": source_delta})
            if boundary not in cuts and decoded_delta > 3 * max(source_delta, 0.1) and decoded_delta - source_delta > 3:
                warnings.append(f"Unexpected encoded change at worker boundary {boundary}; inspect the saved strip.")
            for col, frame in enumerate((boundary - 1, boundary, boundary + 1)):
                sheet.paste(small[frame], (col * 320, row * 210))
                draw.text((col * 320 + 6, row * 210 + 184), f"{kind}: frame {frame}, {frame / FPS:.3f}s", fill="white")
        sheet.save(run_dir / "cut-and-batch-boundaries.jpg", quality=94)
        report["picture_comparison"] = {"decode_transform": "Inverse limited-range BT.709 YUV matrix/range only, with full chroma interpolation. No transfer-function or gamma conversion.",
                                        "gross_mismatch_bounds": {"mae_8bit_max": 10, "psnr_db_min": 25},
                                        "bounds_scope": "Gross identity/encoding errors only, not an artistic quality threshold.",
                                        "selected_frames": comparisons, "observed_worker_batches": batches,
                                        "boundaries": boundary_metrics, "contact_sheet": str(run_dir / "cut-and-batch-boundaries.jpg")}

        qa = read(directory / "qa.json")
        check(qa.get("master_sha256") == master_sha, "Pipeline QA refers to a different movie.")
        check(qa.get("technical_passed") is True and not qa.get("errors"), "Pipeline technical QA did not pass.")
        report["pipeline_qa"] = {"path": str(directory / "qa.json"), "sha256": sha(directory / "qa.json"),
                                 "technical_passed": qa.get("technical_passed"), "errors": qa.get("errors"),
                                 "warnings": qa.get("warnings"), "motion": qa.get("motion")}
        warnings.extend("Pipeline QA: " + text for text in qa.get("warnings", []))
        check(current_hashes(root, baseline["inputs"]) == baseline["inputs"], "Frozen picture input changed during independent QA.")
        check(sha(master) == master_sha, "Master changed during independent QA.")
        check(sha(wav) == WAV_SHA, "Canonical audio changed during independent QA.")
    except Exception as exc:
        errors.append(f"Independent QA stopped: {type(exc).__name__}: {exc}")
    report["completed_at_utc"] = now()
    report["technical_passed"] = not errors
    report["creative_approval"] = "not_assessed"
    report_path = run_dir / "independent-qa.json"
    save_new(report_path, report)
    print(json.dumps({"report": str(report_path), "technical_passed": not errors,
                      "master": report.get("master"), "errors": errors, "warnings": warnings}, indent=2), flush=True)
    return int(bool(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--freeze-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    audit = root / "work/production-system/final-qa"
    audit.mkdir(parents=True, exist_ok=True)
    if args.freeze_only:
        freeze(root, audit)
        return 0
    return audit_master(root, audit)


if __name__ == "__main__":
    sys.exit(main())
