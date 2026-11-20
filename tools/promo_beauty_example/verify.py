"""Inspect the actual beauty-study movie without constructing or rendering a scene.

The native PNG comparison is optional and never triggers a rerender. Decoding
inverts only the original BT.709 YUV matrix and range conversion. It preserves
the legacy display gamma instead of applying an unrelated sRGB transfer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pipeline.delivery import get_profile, stream_validation_errors
from tools.promo_beauty_example.build import COLOR_CONTRACT, authored_timeline

INVERSE_COLOR = "scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24"
SCAN_WIDTH, SCAN_HEIGHT = 320, 180


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def execute(command: list[str], *, timeout: float = 240) -> bytes:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace")[-4000:] or f"Command failed: {command[0]}")
    return result.stdout


def announce(stage: str) -> None:
    print(json.dumps({"qa_stage": stage}), flush=True)


def save_report(folder: Path, report: dict, started: float) -> int:
    report["technical_passed"] = not report["errors"]
    report["creative_approval"] = "not_assessed"
    report["elapsed_seconds"] = time.monotonic() - started
    target = folder / "qa-independent.json"
    temporary = target.with_suffix(".partial.json")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    temporary.replace(target)
    print(json.dumps({"report": str(target), "technical_passed": report["technical_passed"],
                      "errors": report["errors"], "review_warnings": report["review_warnings"],
                      "creative_approval": "not_assessed", "elapsed_seconds": report["elapsed_seconds"]}), flush=True)
    return 1 if report["errors"] else 0


def timeline(args, receipt: dict, total: int) -> tuple[list[dict], list[dict]]:
    if args.cuts is not None:
        cuts = []
        for value in args.cuts.split(","):
            if not value.strip():
                continue
            seconds = float(value)
            if not math.isfinite(seconds):
                raise ValueError("Cut times must be finite.")
            index = math.ceil(round(seconds * args.fps, 9))
            cuts.append({"frame": index, "seconds": index / args.fps, "nominal_local_seconds": seconds,
                         "source_cue_seconds": args.source_start + seconds - 0.1,
                         "source_film_seconds": args.source_start + seconds, "owner": "declared"})
        initial_owner = "declared"
    elif "declared_cuts" in receipt:
        cuts = list(receipt["declared_cuts"])
        initial_owner = receipt.get("shots", [{}])[0].get("owner", "source")
    else:
        cuts, source_shots = authored_timeline(args.source_start)
        cuts = [item for item in cuts if item["frame"] < total]
        initial_owner = source_shots[0]["owner"]
    indices = [item["frame"] for item in cuts]
    if (any(type(index) is not int or not 0 < index < total for index in indices)
            or indices != sorted(set(indices))):
        raise ValueError("Declared cuts must be distinct increasing frame indices strictly inside the movie.")
    starts = [(0, initial_owner), *((item["frame"], item.get("owner", "source")) for item in cuts)]
    shots = [{"start_frame": start, "end_frame_exclusive": starts[i + 1][0] if i + 1 < len(starts) else total,
              "owner": owner} for i, (start, owner) in enumerate(starts)]
    return cuts, shots


def full_decode_scan(movie: Path, expected: int, fps: int, cuts: list[dict], timeout: float) -> dict:
    """Decode every frame once; use bounded-size RGB images for review heuristics."""
    excluded = set()
    intervals = []
    for cut in cuts:
        a, b = max(0, cut["frame"] - 2), min(expected, cut["frame"] + 3)
        excluded.update(range(a, b))
        intervals.append({"start_frame": a, "end_frame_exclusive": b, "reason": "authored_camera_cut"})
    count, longest, still_run = 0, 0, 0
    total_difference, largest_difference = 0.0, 0.0
    previous, previous_delta = None, None
    jump_candidates, reversal_candidates = [], []
    means, whites, seconds = [], [], {}
    bytes_per_frame = SCAN_WIDTH * SCAN_HEIGHT * 3
    with tempfile.TemporaryFile() as raw:
        command = ["ffmpeg", "-v", "error", "-xerror", "-err_detect", "explode", "-threads", "2",
                   "-i", str(movie), "-map", "0:v:0", "-an", "-vf",
                   f"{INVERSE_COLOR},scale={SCAN_WIDTH}:{SCAN_HEIGHT}:flags=area,format=rgb24",
                   "-fps_mode", "passthrough", "-f", "rawvideo", "-"]
        result = subprocess.run(command, stdout=raw, stderr=subprocess.PIPE, timeout=timeout)
        if result.returncode or result.stderr.strip() or raw.tell() % bytes_per_frame:
            raise RuntimeError("Full video decoding failed: " + result.stderr.decode(errors="replace")[-4000:])
        raw.seek(0)
        while chunk := raw.read(bytes_per_frame):
            image = np.frombuffer(chunk, np.uint8).reshape(SCAN_HEIGHT, SCAN_WIDTH, 3)
            luma = (image[..., 0].astype(np.float32) * 0.2126
                    + image[..., 1].astype(np.float32) * 0.7152
                    + image[..., 2].astype(np.float32) * 0.0722) / 255
            mean = float(luma.mean())
            white = float(np.mean(np.all(image >= 250, axis=2)))
            dark = float(np.mean(np.all(image <= 3, axis=2)))
            means.append(mean)
            whites.append(white)
            bucket = seconds.setdefault(count // fps, {"frames": 0, "mean_sum": 0.0, "minimum": 1.0,
                                                       "maximum": 0.0, "white_maximum": 0.0, "dark_maximum": 0.0})
            bucket["frames"] += 1
            bucket["mean_sum"] += mean
            bucket["minimum"] = min(bucket["minimum"], mean)
            bucket["maximum"] = max(bucket["maximum"], mean)
            bucket["white_maximum"] = max(bucket["white_maximum"], white)
            bucket["dark_maximum"] = max(bucket["dark_maximum"], dark)
            if previous is not None:
                delta = luma - previous
                difference = float(np.mean(np.abs(delta)))
                total_difference += difference
                largest_difference = max(largest_difference, difference)
                still_run = still_run + 1 if difference < 0.0001 and count not in excluded else 0
                longest = max(longest, still_run)
                if count not in excluded and difference > 0.18:
                    jump_candidates.append({"frame": count, "seconds": count / fps, "difference": difference})
                if previous_delta is not None:
                    first, second = float(previous_delta.mean()), float(delta.mean())
                    strength = min(abs(first), abs(second))
                    if (first * second < 0 and strength > 0.025
                            and not any(index in excluded for index in (count - 2, count - 1, count))):
                        reversal_candidates.append({"frame": count - 1, "seconds": (count - 1) / fps,
                                                    "mean_brightness_reversal": strength})
                previous_delta = delta
            previous = luma
            count += 1
    if not count:
        raise RuntimeError("The decoder returned no video frames.")

    def strongest(values: list[float], maximum: int = 3) -> list[int]:
        chosen = []
        for index in np.argsort(-np.asarray(values)):
            if all(abs(int(index) - old) >= max(1, fps // 2) for old in chosen):
                chosen.append(int(index))
                if len(chosen) == maximum:
                    break
        return chosen

    per_second = [{"start_seconds": second, "frames": values["frames"],
                   "mean_display_luma": values["mean_sum"] / values["frames"],
                   "minimum_frame_mean": values["minimum"], "maximum_frame_mean": values["maximum"],
                   "maximum_near_white_fraction": values["white_maximum"],
                   "maximum_near_black_fraction": values["dark_maximum"]}
                  for second, values in sorted(seconds.items())]
    warnings = []
    if jump_candidates:
        warnings.append("Large adjacent-frame changes occur away from declared cuts; inspect the reported candidates and musical flashes.")
    if reversal_candidates:
        warnings.append("Brightness reversals occur away from declared cuts; inspect them for intended light accents or flicker.")
    if longest / fps > 1.5:
        warnings.append(f"A nearly unchanged interval lasts {longest / fps:.2f}s; confirm that the hold is intentional.")
    if max(means) > 0.85 or max(whites) > 0.15:
        warnings.append("At least one reduced-size frame has a high brightness or near-white area; inspect the native peak frames for washed-out detail.")
    return {"scan_complete": count == expected, "decoded_frames": count,
            "decode_errors": False, "scan_dimensions": [SCAN_WIDTH, SCAN_HEIGHT],
            "mean_adjacent_frame_difference": total_difference / max(count - 1, 1),
            "maximum_adjacent_frame_difference": largest_difference,
            "longest_nearly_unchanged_seconds": longest / fps,
            "jump_candidate_count": len(jump_candidates),
            "jump_candidates": sorted(jump_candidates, key=lambda item: item["difference"], reverse=True)[:12],
            "brightness_reversal_count": len(reversal_candidates),
            "brightness_reversal_candidates": sorted(reversal_candidates, key=lambda item: item["mean_brightness_reversal"], reverse=True)[:12],
            "excluded_intervals": intervals, "brightness_per_second": per_second,
            "brightest_frames": strongest(means), "largest_near_white_frames": strongest(whites),
            "warnings": warnings,
            "interpretation": "Display-pixel heuristics only. They do not assess anatomy, natural movement, physical camera acceleration, exposure in nits or artistic quality. Near-white fractions here are measured after spatial reduction; native selected frames are measured separately."}


def native_metrics(path: Path, frame: int, fps: int) -> dict:
    with Image.open(path) as picture:
        rgb = np.asarray(picture.convert("RGB"))
    mean = rgb.mean(axis=(0, 1))
    return {"frame": frame, "seconds": frame / fps, "path": str(path),
            "dimensions": [rgb.shape[1], rgb.shape[0]], "mean_rgb_8bit": mean.tolist(),
            "mean_display_luma": float(np.dot(mean, [0.2126, 0.7152, 0.0722]) / 255),
            "near_white_fraction_all_channels_ge_250": float(np.mean(np.all(rgb >= 250, axis=2))),
            "high_channel_fraction_any_channel_ge_250": float(np.mean(np.any(rgb >= 250, axis=2))),
            "near_black_fraction_all_channels_le_3": float(np.mean(np.all(rgb <= 3, axis=2)))}


def native_comparison(reference: Path, decoded: Path) -> dict:
    with Image.open(reference) as picture:
        source = np.asarray(picture.convert("RGB"))
    with Image.open(decoded) as picture:
        actual = np.asarray(picture.convert("RGB"))
    if source.shape != actual.shape:
        raise ValueError(f"Reference shape {source.shape} differs from decoded {actual.shape}.")
    absolute_sum, square_sum = 0, 0
    histogram = np.zeros(256, dtype=np.int64)
    for first in range(0, source.shape[0], 256):
        delta = actual[first:first + 256].astype(np.int16) - source[first:first + 256]
        absolute = np.abs(delta)
        absolute_sum += int(absolute.sum(dtype=np.int64))
        square_sum += int(np.square(delta.astype(np.int32)).sum(dtype=np.int64))
        histogram += np.bincount(absolute.ravel(), minlength=256)
    count = source.size
    mse = square_sum / count
    source_mean, actual_mean = source.mean(axis=(0, 1)), actual.mean(axis=(0, 1))
    return {"status": "compared", "source_png": str(reference), "decoded_png": str(decoded),
            "source_png_sha256": digest(reference), "dimensions": [source.shape[1], source.shape[0]],
            "method": COLOR_CONTRACT["decode_for_comparison"],
            "rgb_mae_8bit_levels": absolute_sum / count, "rgb_rmse_8bit_levels": math.sqrt(mse),
            "rgb_psnr_db": 20 * math.log10(255 / math.sqrt(mse)) if mse else None,
            "absolute_error_p95_8bit_levels": int(np.searchsorted(np.cumsum(histogram), math.ceil(count * 0.95))),
            "source_rgb_mean": source_mean.tolist(), "decoded_rgb_mean": actual_mean.tolist(),
            "mean_rgb_difference": (actual_mean - source_mean).tolist(),
            "interpretation": "Lossy RGB difference after reversing the actual encoder matrix and range. Chroma subsampling can alter thin saturated edges; a low error is not artistic approval."}


def extract_native(movie: Path, folder: Path, frames: list[int], timeout: float) -> dict[int, Path]:
    folder.mkdir(parents=True, exist_ok=True)
    selection = "+".join(f"eq(n\\,{index})" for index in frames)
    pattern = folder / "selected-%03d.png"
    execute(["ffmpeg", "-v", "error", "-xerror", "-y", "-threads", "2", "-i", str(movie),
             "-map", "0:v:0", "-an", "-vf", f"select={selection},{INVERSE_COLOR}",
             "-fps_mode", "vfr", "-frames:v", str(len(frames)), "-threads", "2", str(pattern)], timeout=timeout)
    result = {}
    for index, frame in enumerate(frames, 1):
        temporary = folder / f"selected-{index:03d}.png"
        if not temporary.is_file():
            raise RuntimeError(f"Native frame extraction missed example frame {frame}.")
        path = folder / f"frame-{frame:04d}.png"
        temporary.replace(path)
        result[frame] = path
    return result


def make_contact_sheet(images: dict[int, Path], folder: Path, fps: int, source_start: float,
                       cuts: list[dict]) -> Path:
    cell_w, cell_h, columns = 480, 310, 4
    sheet = Image.new("RGB", (columns * cell_w, math.ceil(len(images) / columns) * cell_h), (16, 17, 25))
    draw = ImageDraw.Draw(sheet)
    font_path = ROOT / "fonts/jost-latin-500-normal.ttf"
    font = ImageFont.truetype(str(font_path), 16) if font_path.is_file() else ImageFont.load_default()
    cut_frames = {item["frame"] for item in cuts}
    for index, (frame, path) in enumerate(sorted(images.items())):
        x, y = (index % columns) * cell_w, (index // columns) * cell_h
        with Image.open(path) as picture:
            sheet.paste(picture.convert("RGB").resize((480, 270), Image.Resampling.LANCZOS), (x, y))
        suffix = " | CUT" if frame in cut_frames else " | before cut" if frame + 1 in cut_frames else ""
        draw.text((x + 8, y + 273), f"Frame {frame:04d} | example {frame / fps:.3f}s{suffix}", font=font, fill=(242, 235, 224))
        draw.text((x + 8, y + 291), f"Source film {source_start + frame / fps:.3f}s", font=font, fill=(176, 188, 211))
    target = folder / "contact-sheet-independent.jpg"
    sheet.save(target, quality=94)
    return target


def decoded_audio(movie: Path, stream: dict, seconds: float, timeout: float) -> tuple[dict, list[str]]:
    rate, channels = int(stream.get("sample_rate", 0)), int(stream.get("channels", 0))
    if rate != 48000 or channels != 2:
        raise RuntimeError("Expected 48 kHz stereo excerpt audio.")
    raw = execute(["ffmpeg", "-v", "error", "-xerror", "-threads", "2", "-i", str(movie),
                   "-map", "0:a:0", "-vn", "-c:a", "pcm_f32le", "-f", "f32le", "pipe:1"], timeout=timeout)
    if len(raw) % (channels * 4):
        raise RuntimeError("Decoded audio ended with a partial sample.")
    samples = np.frombuffer(raw, dtype="<f4").reshape(-1, channels)
    nominal_count = round(seconds * rate)
    if len(samples) < nominal_count or len(samples) - nominal_count > 2048:
        raise RuntimeError("Decoded audio is truncated or contains more than two AAC frames of padding.")
    nominal = samples[:nominal_count]
    if not np.isfinite(nominal).all():
        raise RuntimeError("Decoded audio contains nonfinite values.")
    peak = float(np.max(np.abs(nominal)))
    rms = float(np.sqrt(np.mean(nominal.astype(np.float64) ** 2)))
    if rms < 1e-8:
        raise RuntimeError("The delivered music excerpt is silent.")
    exceedances = int(np.count_nonzero(np.abs(nominal) >= 1.0))
    warnings = []
    if exceedances:
        warnings.append("Decoded AAC exceeds full scale in some samples; inspect the audio peak. Codec overshoot alone does not prove clipped source audio.")
    tail = nominal[-max(1, round(rate * 0.01)):]
    return ({"codec": stream.get("codec_name"), "sample_rate": rate, "channels": channels,
             "nominal_samples_per_channel": nominal_count, "decoded_samples_per_channel": len(samples),
             "extra_codec_padding_samples": len(samples) - nominal_count,
             "sample_peak_dbfs": 20 * math.log10(max(peak, 1e-12)),
             "rms_dbfs": 20 * math.log10(max(rms, 1e-12)), "full_scale_exceedance_samples": exceedances,
             "last_10ms_peak_dbfs": 20 * math.log10(max(float(np.max(np.abs(tail))), 1e-12))}, warnings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--movie", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, help="Defaults to delivery.json beside the movie when present.")
    parser.add_argument("--reference", type=Path, help="Optional previously rendered native RGB PNG; no rerender is performed.")
    parser.add_argument("--frame", type=int, help="Exact example frame index corresponding to --reference.")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, choices=(60,), default=60)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--source-start", type=float)
    parser.add_argument("--cuts", help="Optional comma-separated local cut times, overriding the receipt or authored edit.")
    args = parser.parse_args()
    if (min(args.width, args.height, args.fps) <= 0 or not math.isfinite(args.duration) or args.duration <= 0):
        parser.error("Dimensions, frame rate and duration must be positive and finite.")
    total = round(args.duration * args.fps)
    if abs(total / args.fps - args.duration) > 1e-8:
        parser.error("Duration must contain a whole number of frames.")
    if bool(args.reference) != (args.frame is not None):
        parser.error("Use --reference and its exact --frame together.")
    if args.frame is not None and not 0 <= args.frame < total:
        parser.error("The comparison frame must be inside the movie.")
    if not args.movie.is_file() or (args.reference and not args.reference.is_file()):
        parser.error("The movie and any requested native reference PNG must exist.")
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    timeout = max(240, args.duration * 12)
    report = {"movie": str(args.movie.resolve()), "bytes": args.movie.stat().st_size,
              "sha256": digest(args.movie), "errors": [], "review_warnings": [],
              "color_contract": COLOR_CONTRACT,
              "limitations": ["Automated checks do not judge beauty, anatomy, choreography, readable lettering or musical intention.",
                              "The actual completed S11 master is not a comparison source in this check.",
                              "No real-time playback or complete artistic review is claimed."]}
    stage = "preflight"
    try:
        receipt_path = args.receipt or args.movie.parent / "delivery.json"
        if args.receipt and not receipt_path.is_file():
            raise RuntimeError("The explicitly requested delivery receipt does not exist.")
        receipt = json.loads(receipt_path.read_text()) if receipt_path.is_file() else {}
        if receipt and receipt.get("sha256") != report["sha256"]:
            raise RuntimeError("The movie hash does not match its delivery receipt.")
        if receipt:
            report["delivery_receipt"] = {"path": str(receipt_path), "sha256": digest(receipt_path)}
            report["prepared_inputs"] = receipt.get("prepared_inputs", {})
            report["authored_audio_excerpt"] = receipt.get("audio", {})
            if receipt.get("color_contract", {}).get("name") != COLOR_CONTRACT["name"]:
                raise RuntimeError("The delivery receipt has a different color contract; do not apply the legacy inverse.")
        args.source_start = (args.source_start if args.source_start is not None else float(receipt.get("source_start", 97.8)))
        if not math.isfinite(args.source_start):
            raise ValueError("Source start must be finite.")
        if receipt and abs(args.source_start - float(receipt["source_start"])) > 1e-9:
            raise RuntimeError("The requested source start disagrees with the delivered excerpt receipt.")
        cuts, shots = timeline(args, receipt, total)
        report.update(source_start=args.source_start, declared_cuts=cuts, shots=shots)
        announce("container, codec, dimensions, frame rate and source receipt")
        metadata = json.loads(execute(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(args.movie)], timeout=timeout))
        videos = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"]
        audios = [s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"]
        if len(videos) != 1 or len(audios) != 1:
            raise RuntimeError("Independent checks require one video and one audio stream.")
        video, audio_stream = videos[0], audios[0]
        # This first gate uses the header count if present. The full decoder below
        # supplies the independent count used for the final result.
        video["nb_read_frames"] = video.get("nb_frames", total)
        report["errors"].extend(stream_validation_errors(metadata, get_profile("h264"), width=args.width,
                                                        height=args.height, fps=args.fps, frames=total, wanted_audio=True))
        report["video"] = {key: video.get(key) for key in ("codec_name", "profile", "width", "height", "pix_fmt",
                            "r_frame_rate", "avg_frame_rate", "nb_frames", "duration", "start_time",
                            "color_primaries", "color_transfer", "color_space", "color_range")}
        if report["errors"]:
            report["stopped_at"] = stage
            return save_report(args.output, report, started)
        stage = "complete video decode"
        announce("every video frame, brightness and cut-aware motion heuristics")
        scan = full_decode_scan(args.movie, total, args.fps, cuts, timeout)
        report["temporal_and_brightness"] = scan
        report["review_warnings"].extend(scan["warnings"])
        if not scan["scan_complete"]:
            raise RuntimeError(f"The full decoder returned {scan['decoded_frames']} frames; expected {total}.")
        video["nb_read_frames"] = scan["decoded_frames"]
        report["video"]["decoded_frames"] = scan["decoded_frames"]
        stage = "presentation clock"
        announce("every decoded presentation timestamp")
        timestamps = json.loads(execute(["ffprobe", "-v", "error", "-threads", "2", "-select_streams", "v:0",
                                         "-show_frames", "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(args.movie)], timeout=timeout))
        pts = np.asarray([float(item.get("best_effort_timestamp_time", "nan")) for item in timestamps.get("frames", [])])
        valid = len(pts) == total and bool(np.isfinite(pts).all())
        maximum_error = float(np.max(np.abs(pts - np.arange(total) / args.fps))) if valid else None
        increasing = bool(valid and (total == 1 or np.all(np.diff(pts) > 0)))
        report["timing"] = {"frame_count": len(pts), "maximum_pts_error_seconds": maximum_error,
                            "strictly_increasing": increasing, "first_pts_seconds": float(pts[0]) if valid else None,
                            "last_pts_seconds": float(pts[-1]) if valid else None}
        if not valid or not increasing or maximum_error > 1e-5:
            raise RuntimeError("Decoded timestamps do not match the complete expected frame clock.")
        stage = "audio decode"
        announce("complete excerpt audio decode")
        report["decoded_audio"], audio_warnings = decoded_audio(args.movie, audio_stream, args.duration, timeout)
        report["review_warnings"].extend(audio_warnings)
        stage = "native frame evidence"
        announce("native images covering every shot, both sides of cuts and brightness peaks")
        selections = {0, total - 1, *scan["brightest_frames"], *scan["largest_near_white_frames"]}
        for shot in shots:
            selections.add((shot["start_frame"] + shot["end_frame_exclusive"] - 1) // 2)
        for cut in cuts:
            selections.update((cut["frame"] - 1, cut["frame"]))
        if args.frame is not None:
            selections.add(args.frame)
        images = extract_native(args.movie, args.output / f"native-{report['sha256'][:12]}", sorted(selections), timeout)
        native = [native_metrics(path, index, args.fps) for index, path in sorted(images.items())]
        if any(item["dimensions"] != [args.width, args.height] for item in native):
            raise RuntimeError("An extracted evidence image is not at the expected native resolution.")
        report["native_frames"] = native
        report["contact_sheet"] = str(make_contact_sheet(images, args.output, args.fps, args.source_start, cuts))
        report["contact_frames"] = sorted(images)
        if any(item["near_white_fraction_all_channels_ge_250"] > 0.15 for item in native):
            report["review_warnings"].append("A native selected frame has over 15 percent near-white pixels; inspect whether its light event preserves detail.")
        if args.reference:
            comparison = native_comparison(args.reference, images[args.frame])
            comparison["example_frame"] = args.frame
            report["keyframe_comparison"] = comparison
            if comparison["rgb_mae_8bit_levels"] > 6:
                report["review_warnings"].append("Native frame RGB error exceeds 6/255; inspect source identity, chroma detail and color conversion.")
        else:
            report["keyframe_comparison"] = {"status": "not_run", "reason": "No separately captured reference PNG was supplied; no scene was rerendered."}
        if digest(args.movie) != report["sha256"]:
            raise RuntimeError("The movie changed while independent checks were running.")
        report["ffmpeg_version"] = execute(["ffmpeg", "-version"], timeout=15).decode().splitlines()[0]
        report["review_evidence"] = "Inspect the actual movie, native images and decoded contact sheet separately. Technical checks do not approve the design."
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        report["errors"].append(str(exc))
        report["stopped_at"] = stage
    return save_report(args.output, report, started)


if __name__ == "__main__":
    raise SystemExit(main())
