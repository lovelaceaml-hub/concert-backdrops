"""Check the encoded Song 11 delivery without modifying its picture source.

The default checks the complete 275-second master. A short proof can supply
--duration and --source-offset while retaining the same technical checks.
Visual and creative approval are intentionally outside this technical receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.signal import correlate, correlation_lags


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def probe(path, *options):
    run = subprocess.run(["ffprobe", "-v", "error", *options, "-of", "json", str(path)],
                         capture_output=True, text=True, check=True)
    if run.stderr.strip():
        raise RuntimeError(run.stderr)
    return json.loads(run.stdout)


def audio(path, duration, offset=0.0):
    command = ["ffmpeg", "-v", "error", "-ss", str(offset), "-i", str(path),
               "-t", str(duration), "-map", "0:a:0", "-ac", "1", "-ar", "8000",
               "-f", "f32le", "-"]
    run = subprocess.run(command, capture_output=True, check=True)
    if run.stderr.strip():
        raise RuntimeError(run.stderr.decode(errors="replace"))
    return np.frombuffer(run.stdout, dtype="<f4").astype(np.float64)


def check_audio(video, score, duration, source_offset):
    actual = audio(video, duration)
    reference = audio(score, duration, source_offset)
    wanted = round(duration * 8000)
    if abs(len(actual) - wanted) > 1 or abs(len(reference) - wanted) > 1:
        raise RuntimeError("Decoded audio does not cover the requested interval.")
    actual, reference = actual[:wanted], reference[:wanted]
    music_seconds = min(duration, max(0.0, 260.0 - source_offset))
    window = min(10.0, max(1.0, music_seconds / 8))
    rows = []
    for fraction in (.15, .5, .85):
        start = max(.05, min(music_seconds - window - .05,
                            music_seconds * fraction - window / 2))
        lo, hi = round(start * 8000), round((start + window) * 8000)
        a, b = actual[lo:hi], reference[lo:hi]
        a, b = a - a.mean(), b - b.mean()
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom < 1e-8:
            raise RuntimeError("An intended music verification window is silent.")
        corr = correlate(a, b, mode="full", method="fft")
        lags = correlation_lags(len(a), len(b), mode="full")
        selected = np.abs(lags) <= 80
        lag = int(lags[selected][np.argmax(corr[selected])])
        similarity = float(np.dot(a, b) / denom)
        if abs(lag) > 1 or similarity < .99:
            raise RuntimeError(f"Audio timing/content differs at {start:.3f}s: lag={lag}, correlation={similarity}.")
        rows.append(dict(video_start=start, seconds=window,
                         lag_samples_at_8000_hz=lag, correlation=similarity))
    hold_start = max(0.0, 260.1 - source_offset)
    hold_peak = None
    if hold_start < duration - .1:
        tail = actual[round(hold_start * 8000):]
        hold_peak = float(np.max(np.abs(tail)))
        if hold_peak > .0001:
            raise RuntimeError("The intended silent closing hold contains audible signal.")
    return dict(decoded_samples_at_8000_hz=len(actual), source_offset=source_offset,
                original_score_sha256=digest(score), windows=rows,
                silent_hold_peak=hold_peak)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--score", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=275.0)
    parser.add_argument("--source-offset", type=float, default=0.0)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    args = parser.parse_args()
    details = probe(args.video, "-show_streams", "-show_format")
    videos = [s for s in details["streams"] if s["codec_type"] == "video"]
    audios = [s for s in details["streams"] if s["codec_type"] == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        raise RuntimeError("Expected exactly one video and one audio stream.")
    v, a = videos[0], audios[0]
    frames = round(args.duration * 60)
    requirements = dict(codec_name="h264", width=args.width, height=args.height,
                        avg_frame_rate="60/1", pix_fmt="yuv420p", color_space="bt709",
                        color_transfer="bt709", color_primaries="bt709", color_range="tv")
    for key, expected in requirements.items():
        if v.get(key) != expected:
            raise RuntimeError(f"Video {key}: {v.get(key)!r}; expected {expected!r}.")
    if int(v.get("nb_frames", -1)) != frames:
        raise RuntimeError("Encoded frame count is incorrect.")
    if a.get("codec_name") != "aac" or a.get("sample_rate") != "48000":
        raise RuntimeError("Expected the delivery's AAC audio at 48 kHz.")
    for stream in (v, a, details["format"]):
        if abs(float(stream["duration"]) - args.duration) > .001:
            raise RuntimeError("Stream or container duration is incorrect.")
    packets = probe(args.video, "-select_streams", "v:0", "-show_packets",
                    "-show_entries", "packet=pts_time,duration_time")["packets"]
    pts = np.sort(np.array([float(p["pts_time"]) for p in packets]))
    if len(pts) != frames:
        raise RuntimeError("Video packet count differs from expected frames.")
    max_error = float(np.max(np.abs(pts - np.arange(frames) / 60)))
    if max_error > .000002:
        raise RuntimeError("Video presentation timestamps contain a gap or duplicate.")
    decode = subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-err_detect", "explode",
                             "-i", str(args.video), "-map", "0:v:0", "-map", "0:a:0",
                             "-f", "null", "-"], capture_output=True, text=True)
    if decode.returncode or decode.stderr.strip():
        raise RuntimeError("Complete decode failed: " + decode.stderr[-4000:])
    audio_result = check_audio(args.video, args.score, args.duration, args.source_offset)
    record = dict(schema="s11-encoded-delivery-check-v1", status="passed",
                  filename=args.video.name, sha256=digest(args.video), bytes=args.video.stat().st_size,
                  duration=args.duration, frames=frames, fps=60, native_size=[args.width, args.height],
                  video_requirements=requirements, audio_sample_rate=48000,
                  complete_video_audio_decode=True, presentation_timestamp_max_error_seconds=max_error,
                  audio=audio_result, visual_review="Recorded separately; not inferred from technical checks.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
