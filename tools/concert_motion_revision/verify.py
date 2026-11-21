"""Independent encoded-media checks for the fifteen-second action comparison.

This verifier checks delivery properties and saves actual decoded review images.
It does not turn numeric checks into artistic or owner approval.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import wave

import numpy as np

from .render import ROOT, FRAME_COUNT, FPS, DURATION, AUDIO_IDENTITY, digest, identity, source_hashes, atomic_json


def run(args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def read_pcm_crop(path, start, count):
    """Read signed little-endian PCM without mistaking packed24 for int16."""
    with wave.open(str(path), "rb") as reader:
        if reader.getframerate() != 48000 or reader.getnchannels() != 2:
            raise ValueError("Expected the canonical 48 kHz stereo score")
        width = reader.getsampwidth()
        reader.setpos(start)
        raw = reader.readframes(count)
    if len(raw) != count * 2 * width:
        raise ValueError("The canonical score does not contain the complete crop")
    if width == 3:
        byte = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        values = byte[:, 0] | (byte[:, 1] << 8) | (byte[:, 2] << 16)
        values = (values ^ 0x800000) - 0x800000
        values = values.astype("f8") / 8388608.0
    elif width in (2, 4):
        values = np.frombuffer(raw, dtype=f"<i{width}").astype("f8") / float(1 << (8 * width - 1))
    else:
        raise ValueError(f"Unsupported canonical PCM sample width: {width}")
    return values.reshape(-1, 2)


def verify(movie, out):
    movie, out = movie.resolve(), out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = ROOT / "work/concert-motion-revision/freeze.json"
    freeze = json.loads(freeze_path.read_text())
    errors = []
    warnings = []
    info = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(movie)]))
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    audio = next(s for s in info["streams"] if s["codec_type"] == "audio")
    expected = {"width": 1920, "height": 1080, "r_frame_rate": "60/1", "avg_frame_rate": "60/1",
                "nb_read_frames": "900", "pix_fmt": "yuv420p", "color_space": "bt709",
                "color_transfer": "bt709", "color_primaries": "bt709", "color_range": "tv"}
    for name, value in expected.items():
        if video.get(name) != value:
            errors.append(f"Video {name}: expected {value!r}, got {video.get(name)!r}")
    for label, stream in (("video", video), ("audio", audio)):
        if abs(float(stream.get("start_time", 0))) > 1e-6:
            errors.append(f"{label} stream does not start at zero")
        if abs(float(stream["duration"]) - DURATION) > 1 / 48000:
            errors.append(f"{label} stream duration is not fifteen seconds")
    if audio.get("sample_rate") != "48000" or audio.get("channels") != 2:
        errors.append("Audio is not 48 kHz stereo")
    rows = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(movie)]))["frames"]
    pts = np.asarray([float(row["best_effort_timestamp_time"]) for row in rows])
    if len(pts) != FRAME_COUNT or not np.allclose(pts, np.arange(FRAME_COUNT) / FPS, atol=1e-6, rtol=0):
        errors.append("Decoded presentation timestamps do not match the 900-frame clock")
    # A complete decode, independent of the PNG input and render receipt.
    run(["ffmpeg", "-v", "error", "-xerror", "-threads", "2", "-i", str(movie), "-f", "null", "-"])
    decoded_audio = np.frombuffer(run(["ffmpeg", "-v", "error", "-threads", "2", "-i", str(movie),
        "-map", "0:a:0", "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "2", "-ar", "48000", "-"]), dtype="<f4").reshape(-1, 2)
    score = ROOT / "work/concert-kit/consideration-score.wav"
    expected_audio = read_pcm_crop(score, 144000, 720000)
    count = min(len(decoded_audio), len(expected_audio))
    peak = float(np.max(np.abs(decoded_audio)))
    audio_corr = float(np.corrcoef(expected_audio[:count].ravel(), decoded_audio[:count].ravel())[0, 1])
    if count < 720000:
        errors.append("Decoded audio is shorter than the authored fifteen-second score")
    if audio_corr < .99:
        errors.append("Decoded audio is not strongly aligned with the unchanged-speed prepared score")
    if peak >= 1:
        warnings.append("Decoded AAC samples reach or exceed full scale")
    if identity(source_hashes()) != freeze.get("source_identity"):
        errors.append("Current picture inputs differ from the frozen source fingerprint")
    if digest(score) != AUDIO_IDENTITY:
        errors.append("The canonical score has a different identity")

    selected = sorted(set([0, 138, 233, 234, 270, 330, 462, 510, 512, 516, 528, 539, 540, 558, 599, 690, 810, 870, 899]
                          + list(range(504, 562, 2))))
    review_dir = out / "decoded"
    review_dir.mkdir(exist_ok=True)
    select = "+".join(f"eq(n\\,{i})" for i in selected)
    run(["ffmpeg", "-v", "error", "-threads", "2", "-i", str(movie), "-vf",
         f"select='{select}',scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
         "-fps_mode", "vfr", "-threads", "2", str(review_dir / "sample-%03d.png")])
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    cols, width, height, label = 4, 480, 270, 28
    sheet = Image.new("RGB", (cols * width, ((len(selected) + cols - 1) // cols) * (height + label)), "#080c17")
    draw = ImageDraw.Draw(sheet)
    sample_records = []
    for serial, output_index in enumerate(selected, 1):
        source = review_dir / f"sample-{serial:03d}.png"
        target = review_dir / f"output-{output_index:06d}.png"
        source.replace(target)
        image = Image.open(target)
        x, y = ((serial - 1) % cols) * width, ((serial - 1) // cols) * (height + label)
        sheet.paste(image.resize((width, height), Image.Resampling.LANCZOS), (x, y))
        source_time = 3.0 + output_index / FPS
        draw.text((x + 5, y + height + 3), f"output {output_index / FPS:.3f}s | source {source_time:.3f}s", font=font, fill="white")
        sample_records.append({"output_frame": output_index, "source_frame": output_index + 180,
                               "source_seconds": source_time, "path": str(target.relative_to(ROOT)), "sha256": digest(target)})
    sheet.save(out / "decoded-contact-sheet.jpg", quality=93)
    result = {"passed": not errors, "errors": errors, "warnings": warnings,
              "movie": str(movie.relative_to(ROOT)), "movie_sha256": digest(movie),
              "source_identity": freeze["source_identity"], "freeze_manifest_sha256": digest(freeze_path), "video": video, "audio": audio,
              "clock": {"frames": len(pts), "first_pts": float(pts[0]), "last_pts": float(pts[-1]),
                        "expected_step": 1 / FPS, "maximum_error_seconds": float(np.max(np.abs(pts - np.arange(len(pts)) / FPS)))},
              "decoded_audio": {"sample_frames": len(decoded_audio), "expected_sample_frames": 720000,
                                "peak": peak, "peak_dbfs": float(20 * np.log10(max(peak, 1e-12))),
                                "correlation_to_canonical_score_crop": audio_corr},
              "complete_decode": True, "decoded_image_color": "inverse BT.709 matrix/range only; no transfer conversion",
              "samples": sample_records,
              "scope": "Technical delivery checks and sampled image evidence; not real-time playback or owner approval"}
    atomic_json(out / "verification.json", result)
    print(json.dumps({"passed": result["passed"], "errors": errors, "warnings": warnings,
                      "movie_sha256": result["movie_sha256"], "peak_dbfs": result["decoded_audio"]["peak_dbfs"],
                      "report": str(out / "verification.json")}), flush=True)
    if errors:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("movie", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify(args.movie, args.out)


if __name__ == "__main__":
    main()
