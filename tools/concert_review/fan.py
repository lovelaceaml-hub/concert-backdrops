"""Independent technical audit of the original 20-second fan and silk study.

Run after assembly:
    .venv/bin/python tools/concert_review/fan.py --baseline PATH
Use --inputs-only to verify a separately frozen baseline before rendering.

The coordinator creates the baseline, never this auditor. Required schema:
    {"schema_version": 1, "project": "concert-fan-trio", "quality": "review",
     "source_frozen": true, "project_manifest_sha256": "...",
     "fingerprint": "...", "provenance": {...},
     "canonical_audio_sha256": "..."}
fingerprint and the complete provenance come from pipeline.render.fingerprint.
No renderer is imported, no baseline is repaired, and no beauty or choreography
approval is inferred. New evidence is written to a new ignored work directory.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
import wave

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.concert_review.consideration import alignment_window, jsha, now, read, sha

PROJECT, SCENE = "concert-fan-trio", "tools/concert_fan/fan_trio.py"
WIDTH, HEIGHT, FPS, SECONDS = 1920, 1080, 60, 20
FRAMES, RATE, CHANNELS, SAMPLES = 1200, 48000, 2, 960000
WAV = "work/song-sources/fan-trio-score.wav"
WAV_SHA = "b26b7ec1dd00a4c91330df5c83a47afc8c40791861a722dd91408eb246f0cd0b"
SETTINGS = dict(width=WIDTH, height=HEIGHT, fps=FPS, temporal_samples=2, image_bit_depth=8)
COLOR = dict(color_primaries="bt709", color_transfer="bt709", color_space="bt709", color_range="tv")


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def local(root, name):
    path = (root / name).resolve()
    check(not Path(name).is_absolute() and path.is_relative_to(root),
          f"Source path escapes the repository: {name}")
    return path


def mapping_hashes(root, mapping):
    check(isinstance(mapping, dict) and bool(mapping), "Source mapping is empty or invalid.")
    check(all(isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) for v in mapping.values()),
          "Source mapping contains an invalid SHA256.")
    return {name: sha(local(root, name)) for name in mapping}


def run(argv, timeout):
    result = subprocess.run(argv, capture_output=True, timeout=timeout, check=False)
    check(result.returncode == 0 and not result.stderr.strip(),
          f"Decoder command failed: {argv[0]}: {result.stderr.decode(errors='replace')[-3000:]}")
    return result.stdout


def probe(movie, timeout, *args):
    return json.loads(run(["ffprobe", "-v", "error", *args, "-of", "json", str(movie)], timeout))


def verify_sources(root, baseline_path):
    baseline = read(baseline_path)
    check(all(baseline.get(k) == v for k, v in dict(schema_version=1, project=PROJECT,
          quality="review", source_frozen=True, canonical_audio_sha256=WAV_SHA).items()),
          "Baseline is not the frozen fan-trio review contract.")
    provenance = baseline["provenance"]
    check(jsha(provenance) == baseline.get("fingerprint"), "Baseline fingerprint is inconsistent.")
    mapping = provenance["inputs"]
    required = {"assets/p3d/body_v1.npz", "engine/p3d/body.py", "engine/p3d/actor.py",
                "pipeline/kit.py", "pipeline/render.py"} | {
                    f"tools/concert_fan/{name}.py" for name in
                    ("__init__", "fan_trio", "performance", "props", "render")}
    check(required <= mapping.keys(), "Baseline omits a required fan-trio picture dependency.")
    check("tools/concert_review/fan.py" not in mapping, "Auditor unexpectedly belongs to picture inputs.")
    actual = mapping_hashes(root, mapping)
    changed = [name for name in mapping if actual[name] != mapping[name]]
    check(not changed, f"Frozen picture files changed: {changed}")

    manifest_path = root / "projects" / PROJECT / "project.json"
    check(sha(manifest_path) == baseline.get("project_manifest_sha256"), "Manifest changed after freezing.")
    manifest = read(manifest_path)
    check(manifest.get("project_id") == PROJECT and manifest.get("video") ==
          dict(width=WIDTH, height=HEIGHT, fps=FPS), "Wrong project or native video clock.")
    check(manifest.get("quality", {}).get("review") ==
          {k: v for k, v in SETTINGS.items() if k != "fps"}, "Expected two-sample native RGB8 review settings.")
    check(manifest.get("delivery") == dict(profile="h264", source_transfer="legacy_display_gamma",
          color_space="rec709"), "Unexpected delivery color contract.")
    check(manifest.get("audio") == dict(source=WAV, source_sha256=WAV_SHA, offset_seconds=0),
          "Canonical audio path, SHA256, offset or finishing operations changed.")
    shots = manifest.get("shots", [])
    check(len(shots) == 1 and all(shots[0].get(k) == v for k, v in dict(id="performance",
          start_frame=0, end_frame_exclusive=FRAMES, renderer="p3d-kit", scene=SCENE, params={}).items()),
          "Expected one continuous authored shot covering exactly frames 0 through 1199.")
    related = {k: read(local(root, manifest[k])) if isinstance(manifest[k], str) else manifest[k]
               for k in ("timing", "style")}
    timing = related["timing"]
    check(timing.get("fps") == FPS and timing.get("events") == [] and
          timing.get("visual_only") is True and timing.get("manually_verified") is False,
          "The authored visual clock or music-review status changed.")
    check(provenance.get("settings") == SETTINGS and provenance.get("shot") == shots[0]
          and provenance.get("seed") == manifest["production"]["random_seed"] == 2026
          and provenance.get("audio") == {} and all(provenance.get(k) == v for k, v in related.items()),
          "Frozen provenance does not describe the current picture contract.")

    audio_path = root / WAV
    check(sha(audio_path) == WAV_SHA, "Canonical 20-second WAV differs from the pinned bytes.")
    with wave.open(str(audio_path), "rb") as source:
        params = (source.getnchannels(), source.getsampwidth(), source.getframerate(), source.getnframes())
        check(params == (CHANNELS, 2, RATE, SAMPLES) and source.getcomptype() == "NONE",
              f"Canonical WAV must be PCM16, 48 kHz stereo, 960000 samples: {params}")
        raw = source.readframes(SAMPLES)
    check(len(raw) == SAMPLES * CHANNELS * 2, "Canonical PCM payload is incomplete.")
    canonical = np.frombuffer(raw, "<i2").reshape(-1, CHANNELS).astype(np.float64) / 32768
    return baseline, manifest_path, jsha({"manifest": manifest, "related": related}), canonical, hashlib.sha256(raw).hexdigest()


def verify_receipts(root, movie, baseline, identity):
    shot_path, master_path = movie.parent / "shots/performance/receipt.json", movie.parent / "master.json"
    shot, master = read(shot_path), read(master_path)
    check(shot.get("complete") is True and shot.get("shot_id") == "performance",
          "Performance shot receipt is incomplete or names another shot.")
    check(shot.get("provenance") == baseline["provenance"] and
          shot.get("fingerprint") == baseline["fingerprint"], "Shot receipt differs from the frozen provenance.")
    frame_hashes = shot.get("frames", {})
    check(set(frame_hashes) == {str(i) for i in range(FRAMES)} and
          all(isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) for v in frame_hashes.values()),
          "Shot receipt does not contain exactly 1200 checksummed source frames.")
    check(all(shot.get(k) == SETTINGS[k] for k in ("width", "height", "fps", "image_bit_depth")),
          "Shot receipt dimensions or source precision differ.")
    check(all(master.get(k) == v for k, v in dict(project_id=PROJECT, project_identity=identity,
          quality="review", width=WIDTH, height=HEIGHT, fps=FPS, frames=FRAMES,
          audio_source_sha256=WAV_SHA, sha256=sha(movie),
          shot_fingerprints={"performance": baseline["fingerprint"]}).items()),
          "Master bytes, assembly clock, audio or shot identity differ from the frozen contract.")
    finishing = master["finishing_inputs"]
    check(mapping_hashes(root, finishing) == finishing, "Assembly source files changed.")
    return master, {p: sha(p) for p in (movie, shot_path, master_path)}


def audit_video(movie, folder, timeout):
    streams = probe(movie, timeout, "-show_streams")["streams"]
    check(len(streams) == 2 and sorted(s.get("codec_type", "") for s in streams) == ["audio", "video"],
          "Expected exactly one video stream and one audio stream.")
    video = next(s for s in streams if s["codec_type"] == "video")
    audio = next(s for s in streams if s["codec_type"] == "audio")
    check(all(video.get(k) == v for k, v in dict(width=WIDTH, height=HEIGHT, codec_name="h264",
          pix_fmt="yuv420p", **COLOR).items()), "Encoded dimensions, codec, pixel format or BT.709 tags differ.")
    check(Fraction(video["avg_frame_rate"]) == Fraction(video["r_frame_rate"]) == FPS and
          int(video["duration_ts"]) * Fraction(video["time_base"]) == SECONDS,
          "Video is not exactly 20 seconds at 60 fps.")
    frames = probe(movie, timeout, "-select_streams", "v:0", "-show_frames", "-show_entries",
                   "frame=pts,best_effort_timestamp,width,height")["frames"]
    check(len(frames) == FRAMES, f"Expected 1200 presented frames, found {len(frames)}.")
    for i, frame in enumerate(frames):
        pts = frame.get("pts", frame.get("best_effort_timestamp"))
        check(pts is not None and int(pts) * Fraction(video["time_base"]) == Fraction(i, FPS)
              and (frame.get("width"), frame.get("height")) == (WIDTH, HEIGHT),
              f"Frame {i} has a wrong presentation timestamp or native size.")
    raw = run(["ffmpeg", "-v", "error", "-xerror", "-err_detect", "explode", "-nostdin",
               "-threads", "2", "-i", str(movie), "-map", "0:v:0", "-an", "-sn", "-dn",
               "-fps_mode", "passthrough", "-c:v", "rawvideo", "-pix_fmt", "yuv420p",
               "-threads", "2", "-f", "framemd5", "pipe:1"], timeout)
    lines = [line.split(",") for line in raw.decode().splitlines() if line and not line.startswith("#")]
    check(len(lines) == FRAMES and all(len(line) == 6 and int(line[4]) == WIDTH * HEIGHT * 3 // 2
          for line in lines), "Complete FFmpeg decode has a wrong frame count or payload size.")
    log = folder / "decoded-video.framemd5"
    log.write_bytes(raw)
    return dict(width=WIDTH, height=HEIGHT, fps=FPS, frames=FRAMES, seconds=SECONDS,
                complete_decode=True, exact_presentation_timestamps=True, first_seconds=0,
                last_seconds=(FRAMES - 1) / FPS, time_base=video["time_base"], color=COLOR,
                frame_hash_log=str(log), frame_hash_log_sha256=sha(log)), audio


def audit_audio(movie, stream, canonical, timeout):
    check(stream.get("codec_name") == "aac" and int(stream.get("sample_rate", 0)) == RATE
          and stream.get("channels") == CHANNELS and stream.get("channel_layout") == "stereo",
          "Expected AAC, 48 kHz, stereo audio.")
    check(int(stream["duration_ts"]) * Fraction(stream["time_base"]) == SECONDS
          and Fraction(stream.get("start_time", "0")) == 0, "Audio program clock is not exactly 0 to 20 seconds.")
    raw = run(["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "2", "-i", str(movie),
               "-map", "0:a:0", "-vn", "-sn", "-dn", "-c:a", "pcm_f32le", "-f", "f32le", "pipe:1"], timeout)
    check(len(raw) % (CHANNELS * 4) == 0, "Decoded AAC ends with a partial sample.")
    decoded = np.frombuffer(raw, "<f4").reshape(-1, CHANNELS).astype(np.float64)
    check(SAMPLES <= len(decoded) < SAMPLES + 1024 and np.isfinite(decoded).all(),
          "Unexpected decoded AAC sample count, padding or nonfinite values.")
    a, b = canonical.reshape(-1), decoded[:SAMPLES].reshape(-1)
    gain = float(np.dot(a, b) / np.dot(a, a))
    gain_db = 20 * math.log10(gain) if gain > 0 else float("inf")
    correlation = float(np.corrcoef(a, b)[0, 1])
    check(correlation >= .98 and abs(gain_db) <= .25, "Decoded AAC differs from the pinned WAV in signal or gain.")
    windows = []
    for third in range(3):
        candidates = [round(t * RATE) for t in np.arange(third * SECONDS / 3 + .5,
                      (third + 1) * SECONDS / 3 - 2.5 + .001, .25)]
        start = max(candidates, key=lambda s: float(np.mean(canonical[s:s + 2 * RATE] ** 2)))
        window = alignment_window(canonical, decoded, start, start + 2 * RATE)
        check(window["source_rms"] > 1e-4 and window["zero_lag_correlation"] >= .98 and
              abs(window["best_lag_samples"]) <= 1 and window["fitted_gain_db"] is not None
              and abs(window["fitted_gain_db"]) <= .25, f"AAC alignment failed in third {third + 1}.")
        windows.append(window)
    return dict(rate=RATE, channels=CHANNELS, seconds=SECONDS, canonical_wav_sha256=WAV_SHA,
                logical_samples_per_channel=SAMPLES, decoded_samples_per_channel=len(decoded),
                trailing_padding_samples_per_channel=len(decoded) - SAMPLES,
                full_program_correlation=correlation, fitted_gain_db=gain_db, alignment_windows=windows,
                peak=float(np.abs(decoded).max()), samples_at_or_above_full_scale=int((np.abs(decoded) >= 1).sum()),
                priming="FFmpeg applies MP4 edit lists and skip-sample metadata; trailing AAC padding is reported separately.")


def contact_sheet(movie, folder, timeout):
    selected = list(range(0, FRAMES, FPS)) + [FRAMES - 1]
    select = "+".join(f"eq(n\\,{n})" for n in selected)
    raw = run(["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "2", "-i", str(movie),
               "-map", "0:v:0", "-an", "-vf", f"select={select},scale=320:180:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
               "-fps_mode", "vfr", "-threads", "2", "-f", "rawvideo", "pipe:1"], timeout)
    size = 320 * 180 * 3
    check(len(raw) == len(selected) * size, "Encoded contact sheet decoded the wrong sample count.")
    sheet = Image.new("RGB", (1280, math.ceil(len(selected) / 4) * 202), "#080c19")
    draw = ImageDraw.Draw(sheet)
    for i, frame in enumerate(selected):
        x, y = (i % 4) * 320, (i // 4) * 202
        sheet.paste(Image.frombytes("RGB", (320, 180), raw[i * size:(i + 1) * size]), (x, y))
        draw.text((x + 6, y + 184), f"{frame / FPS:.3f} s | frame {frame}", fill="#f1ddb6")
    path = folder / "encoded-seconds.jpg"
    sheet.save(path, quality=92)
    return dict(path=str(path), sha256=sha(path), source_frames=selected,
                scope="Decoded per-second samples and final frame; not continuous motion review or artistic approval.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--movie", type=Path, default=Path(f"work/pipeline/{PROJECT}/review/master.mp4"))
    parser.add_argument("--out-dir", type=Path, help="New directory; never overwrites an earlier audit.")
    parser.add_argument("--inputs-only", action="store_true")
    parser.add_argument("--timeout", type=float, default=240, help="Seconds per FFmpeg/FFprobe command.")
    args = parser.parse_args()
    root = args.root.resolve()
    baseline_path, movie = (root / args.baseline).resolve(), (root / args.movie).resolve()
    stamp = now().replace(":", "").replace("+0000", "Z")
    folder = (root / args.out_dir).resolve() if args.out_dir else root / f"work/production-system/final-qa/{PROJECT}/run-{stamp}"
    check(math.isfinite(args.timeout) and args.timeout > 0, "Timeout must be positive and finite.")
    folder.mkdir(parents=True, exist_ok=False)
    started, baseline, protected, finishing = time.monotonic(), None, {}, None
    report = dict(schema_version=1, project=PROJECT, started_at_utc=now(), errors=[], warnings=[],
                  scope="frozen_inputs_only" if args.inputs_only else "independent_completed_movie_audit",
                  inputs_passed=False, technical_passed=None, creative_approval="not_assessed",
                  limits="Technical source, decode, timestamp and audio evidence only. No certification of natural movement, contact, cloth, musical sync, artistic quality or a 4K movie.",
                  auditor_sha256=sha(Path(__file__)), helper_sha256=sha(ROOT / "tools/concert_review/consideration.py"))
    try:
        baseline, manifest, identity, canonical, pcm_sha = verify_sources(root, baseline_path)
        protected = {p: sha(p) for p in (baseline_path, manifest, root / WAV)}
        report.update(inputs_passed=True, sources=dict(baseline=str(baseline_path), baseline_sha256=sha(baseline_path),
                      fingerprint=baseline["fingerprint"], input_count=len(baseline["provenance"]["inputs"]),
                      mapping_sha256=jsha(baseline["provenance"]["inputs"]), project_identity=identity,
                      canonical_pcm_s16le_sha256=pcm_sha, source_commit=baseline.get("source_commit")))
        if not args.inputs_only:
            print(json.dumps({"audit_stage": "receipts_and_full_native_decode"}), flush=True)
            master, receipt_hashes = verify_receipts(root, movie, baseline, identity)
            protected.update(receipt_hashes)
            finishing = master["finishing_inputs"]
            report["movie"] = dict(path=str(movie), sha256=master["sha256"], bytes=movie.stat().st_size)
            report["receipts"] = dict(matching_frozen_provenance=True, checksummed_source_frames=FRAMES,
                                     hashes={str(p): h for p, h in receipt_hashes.items() if p != movie},
                                     scope="Receipt coverage verified; pipeline QA owns full source PNG checksum revalidation.")
            report["video"], stream = audit_video(movie, folder, args.timeout)
            print(json.dumps({"audit_stage": "canonical_audio_alignment_and_encoded_samples"}), flush=True)
            report["audio"] = audit_audio(movie, stream, canonical, args.timeout)
            report["contact_sheet"] = contact_sheet(movie, folder, args.timeout)
            if report["audio"]["samples_at_or_above_full_scale"]:
                report["warnings"].append("Decoded AAC exceeds full scale; codec overshoot alone does not establish source clipping.")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, wave.Error) as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
    if baseline is not None:
        try:
            check(mapping_hashes(root, baseline["provenance"]["inputs"]) == baseline["provenance"]["inputs"],
                  "Frozen source files changed during the audit.")
            check(finishing is None or mapping_hashes(root, finishing) == finishing, "Finishing files changed during the audit.")
            check(all(sha(p) == expected for p, expected in protected.items()), "Input, receipt or movie changed during the audit.")
            report["inputs_unchanged_during_audit"] = True
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
            report.update(inputs_passed=False, inputs_unchanged_during_audit=False)
            report["errors"].append(str(exc))
    report["technical_passed"] = None if args.inputs_only else not report["errors"]
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    target = folder / "independent-qa.json"
    target.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(report=str(target), inputs_passed=report["inputs_passed"],
                         technical_passed=report["technical_passed"], errors=report["errors"], warnings=report["warnings"])), flush=True)
    return int(bool(report["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
