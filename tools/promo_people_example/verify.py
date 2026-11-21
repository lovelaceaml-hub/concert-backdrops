r"""Independently inspect a delivered people-example movie without importing its scene.

Example, from the repository root:
    uv run --frozen --extra legacy python tools/promo_people_example/verify.py \
        --movie work/promo-people-example/final/example.mp4 \
        --reference work/promo-people-example/stills/frame-0300.png \
        --frame 300 --output work/promo-people-example/final/qa

Add --width 3840 --height 2160 for a native 4K delivery. This decodes the whole
movie, checks every presentation timestamp, measures decoded audio, invokes the
shared temporal scanner, and compares one native frame after conversion back
to sRGB. Inspect the resulting contact sheet separately for artistic defects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pipeline.delivery import get_profile, stream_validation_errors
from pipeline.temporal import scan_motion


INVERSE_COLOR = (
    "zscale=matrixin=bt709:transferin=bt709:primariesin=bt709:rangein=limited:"
    "matrix=gbr:transfer=iec61966-2-1:primaries=bt709:range=full,format=gbrp16le,format=rgb24"
)
CONTACT_TIMES = (0.0, 2.5, 5.0, 7.5, 10.216667, 12.5,
                 15.0, 18.5, 19.483333, 23.0, 27.0, 29.983333)


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def execute(command: list[str], *, timeout: float = 240) -> bytes:
    result = subprocess.run(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace")[-4000:])
    return result.stdout


def announce(stage: str) -> None:
    print(json.dumps({"qa_stage": stage}), flush=True)


def dbfs(value: float) -> float:
    return 20 * math.log10(max(float(value), 1e-12))


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(values.astype(np.float64)))))


def native_comparison(reference: Path, decoded: Path) -> dict:
    source = np.asarray(Image.open(reference).convert("RGB"))
    actual = np.asarray(Image.open(decoded).convert("RGB"))
    if source.shape != actual.shape:
        raise ValueError(f"Reference shape {source.shape} differs from decoded {actual.shape}.")
    # Row blocks keep the native 4K comparison's additional memory bounded.
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
    source_mean = source.mean(axis=(0, 1))
    actual_mean = actual.mean(axis=(0, 1))
    return {
        "source_png": str(reference), "decoded_png": str(decoded),
        "source_png_sha256": digest(reference),
        "dimensions": [source.shape[1], source.shape[0]],
        "method": "Decode the exact native frame and invert the explicit Rec.709 conversion to display-referred sRGB.",
        "rgb_mae_8bit_levels": absolute_sum / count,
        "rgb_rmse_8bit_levels": math.sqrt(mse),
        "rgb_psnr_db": 20 * math.log10(255 / math.sqrt(mse)) if mse else None,
        "identical_pixels": not bool(absolute_sum),
        "absolute_error_p95_8bit_levels": int(np.searchsorted(np.cumsum(histogram), math.ceil(count * 0.95))),
        "source_rgb_mean": source_mean.tolist(),
        "decoded_rgb_mean": actual_mean.tolist(),
        "mean_rgb_difference": (actual_mean - source_mean).tolist(),
    }


def contact_sheet(movie: Path, folder: Path, frames: list[int], fps: int, timeout: float) -> Path:
    selection = "+".join(f"eq(n\\,{frame})" for frame in frames)
    pattern = folder / "qa-selected-%02d.png"
    execute(["ffmpeg", "-v", "error", "-y", "-threads", "2", "-i", str(movie),
             "-map", "0:v:0", "-an", "-vf",
             f"select={selection},{INVERSE_COLOR},scale=480:270:flags=lanczos",
             "-fps_mode", "vfr", "-frames:v", str(len(frames)), str(pattern)], timeout=timeout)
    sheet = Image.new("RGB", (1920, 3 * 300), (17, 16, 28))
    draw = ImageDraw.Draw(sheet)
    font_path = ROOT / "fonts/jost-latin-500-normal.ttf"
    font = ImageFont.truetype(str(font_path), 17) if font_path.is_file() else ImageFont.load_default()
    for index, frame in enumerate(frames):
        path = folder / f"qa-selected-{index + 1:02d}.png"
        x, y = (index % 4) * 480, (index // 4) * 300
        with Image.open(path) as picture:
            sheet.paste(picture.convert("RGB"), (x, y))
        draw.text((x + 9, y + 276), f"Frame {frame:04d} | {frame / fps:.3f} seconds",
                  font=font, fill=(242, 235, 224))
    destination = folder / "contact-sheet-independent.jpg"
    sheet.save(destination, quality=94)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--movie", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--frame", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--cuts", default="10.2,19.4666667",
                        help="Declared editorial cut times in seconds, comma separated.")
    args = parser.parse_args()
    if args.width <= 0 or args.height <= 0 or args.fps <= 0 or args.duration <= 0:
        parser.error("Dimensions, frame rate and duration must be positive.")
    frames = round(args.duration * args.fps)
    if abs(frames / args.fps - args.duration) > 1e-8 or not 0 <= args.frame < frames:
        parser.error("Duration must contain whole frames and --frame must be inside the movie.")
    if not args.movie.is_file() or not args.reference.is_file():
        parser.error("The completed movie and exact native reference PNG must exist.")
    try:
        cuts = sorted({round(float(value) * args.fps) for value in args.cuts.split(",") if value.strip()})
    except ValueError:
        parser.error("Cut times must be numbers.")
    if any(frame <= 0 or frame >= frames for frame in cuts):
        parser.error("Every cut must be strictly inside the movie.")
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    timeout = max(240, args.duration * 12)
    movie_digest = digest(args.movie)
    errors, warnings = [], []
    announce("streams and every presentation timestamp")
    metadata = json.loads(execute(["ffprobe", "-v", "error", "-threads", "2", "-count_frames",
                                  "-show_streams", "-show_format", "-of", "json", str(args.movie)], timeout=timeout))
    errors.extend(stream_validation_errors(metadata, get_profile("h264"), width=args.width,
                                          height=args.height, fps=args.fps, frames=frames, wanted_audio=True))
    videos = [stream for stream in metadata["streams"] if stream.get("codec_type") == "video"]
    audios = [stream for stream in metadata["streams"] if stream.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        raise RuntimeError("Independent decoding requires one video and one audio stream.")
    video, audio_stream = videos[0], audios[0]
    timing_data = json.loads(execute(["ffprobe", "-v", "error", "-threads", "2", "-select_streams", "v:0",
                                     "-show_frames", "-show_entries", "frame=best_effort_timestamp_time",
                                     "-of", "json", str(args.movie)], timeout=timeout))
    pts = np.array([float(frame.get("best_effort_timestamp_time", "nan"))
                    for frame in timing_data["frames"]], dtype=np.float64)
    finite = bool(np.isfinite(pts).all())
    regular = finite and len(pts) == frames
    maximum_error = float(np.max(np.abs(pts - np.arange(frames) / args.fps))) if regular else None
    increasing = bool(len(pts) > 1 and finite and np.all(np.diff(pts) > 0))
    if not regular or not increasing or maximum_error > 1e-5:
        errors.append("Decoded presentation timestamps do not match the complete expected frame clock.")
    for stream in (video, audio_stream):
        if abs(float(stream.get("duration", -1)) - args.duration) > 0.001:
            errors.append(f"{stream.get('codec_type')} duration is not the requested {args.duration} seconds.")
    timing = {"frame_count": len(pts), "maximum_pts_error_seconds": maximum_error,
              "first_pts_seconds": float(pts[0]) if len(pts) and finite else None,
              "last_pts_seconds": float(pts[-1]) if len(pts) and finite else None,
              "strictly_increasing": increasing}
    announce("decoded audio")
    sample_rate = int(audio_stream.get("sample_rate", 0))
    channels = int(audio_stream.get("channels", 0))
    if sample_rate != 48000 or channels != 2:
        errors.append("Expected original excerpt delivery at 48 kHz stereo.")
    raw_audio = execute(["ffmpeg", "-v", "error", "-threads", "2", "-i", str(args.movie),
                         "-map", "0:a:0", "-vn", "-c:a", "pcm_f32le", "-f", "f32le", "pipe:1"], timeout=timeout)
    samples = np.frombuffer(raw_audio, dtype="<f4").reshape(-1, channels)
    nominal_count = round(args.duration * sample_rate)
    nominal = samples[:nominal_count]
    if len(samples) < nominal_count or len(samples) - nominal_count > 2048:
        errors.append("Decoded audio is truncated or has more than two AAC frames of padding.")
    clipping = int(np.count_nonzero(np.abs(nominal) >= 1.0))
    if clipping:
        errors.append(f"Decoded audio has {clipping} clipped samples.")
    tail_rms = dbfs(rms(nominal[-max(1, round(sample_rate * 0.25)):]))
    if tail_rms > -45:
        warnings.append("Final quarter-second audio RMS is above -45 dBFS; inspect the ending.")
    audio = {"codec": audio_stream.get("codec_name"), "sample_rate": sample_rate, "channels": channels,
             "stream_duration_seconds": float(audio_stream.get("duration", 0)),
             "decoded_samples_per_channel_including_codec_padding": len(samples),
             "nominal_duration_samples_per_channel": nominal_count,
             "decoded_extra_padding_samples": len(samples) - nominal_count,
             "sample_peak_dbfs": dbfs(np.max(np.abs(nominal))),
             "clipped_sample_count_abs_ge_1": clipping, "nominal_rms_dbfs": dbfs(rms(nominal)),
             "last_250ms_rms_dbfs": tail_rms,
             "last_10ms_peak_dbfs": dbfs(np.max(np.abs(nominal[-max(1, round(sample_rate * 0.01)):])))}
    announce("complete temporal scan with declared cuts")
    project = SimpleNamespace(fps=args.fps, frames=frames, seconds=args.duration,
                              shots=[{"start_frame": frame} for frame in [0, *cuts]],
                              related_data=lambda name: {})
    temporal = scan_motion(project, args.movie)
    if not temporal.get("scan_complete"):
        errors.append("The temporal scan did not decode the whole movie.")
    warnings.extend(temporal.get("warnings", []))
    announce("native keyframe fidelity and twelve-frame contact sheet")
    native_png = args.output / f"qa-native-frame-{args.frame:04d}.png"
    execute(["ffmpeg", "-v", "error", "-y", "-threads", "2", "-i", str(args.movie),
             "-map", "0:v:0", "-an", "-vf", f"select=eq(n\\,{args.frame}),{INVERSE_COLOR}",
             "-frames:v", "1", "-fps_mode", "vfr", str(native_png)], timeout=timeout)
    comparison = native_comparison(args.reference, native_png)
    if comparison["dimensions"] != [args.width, args.height]:
        errors.append("The compared keyframe is not at the expected native resolution.")
    if comparison["rgb_mae_8bit_levels"] > 6.0:
        warnings.append("Native keyframe mean RGB error exceeds 6/255; inspect color conversion or source identity.")
    selections = sorted({min(frames - 1, max(0, round(t * args.fps))) for t in CONTACT_TIMES})
    sheet = contact_sheet(args.movie, args.output, selections, args.fps, timeout)
    if digest(args.movie) != movie_digest:
        errors.append("The movie changed while independent checks were running.")
    keep_video = ("codec_name", "profile", "width", "height", "pix_fmt", "r_frame_rate", "avg_frame_rate",
                  "nb_read_frames", "duration", "color_primaries", "color_transfer", "color_space", "color_range")
    report = {"movie": str(args.movie), "bytes": args.movie.stat().st_size, "sha256": movie_digest,
              "technical_passed": not errors, "errors": errors, "review_warnings": warnings,
              "video": {key: video.get(key) for key in keep_video}, "timing": timing, "audio": audio,
              "temporal": temporal, "declared_cuts": [{"frame": frame, "seconds": frame / args.fps} for frame in cuts],
              "keyframe_comparison": comparison, "contact_sheet": str(sheet), "contact_frames": selections,
              "visual_review": "Automated checks do not perform artistic inspection. Inspect the decoded contact sheet and native frame separately. No real-time playback is claimed.",
              "elapsed_seconds": time.monotonic() - started,
              "ffmpeg_version": execute(["ffmpeg", "-version"], timeout=15).decode().splitlines()[0]}
    destination = args.output / "qa-independent.json"
    temporary = destination.with_suffix(".partial.json")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    temporary.replace(destination)
    print(json.dumps({"report": str(destination), "technical_passed": not errors,
                      "errors": errors, "review_warnings": warnings,
                      "elapsed_seconds": report["elapsed_seconds"]}), flush=True)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
