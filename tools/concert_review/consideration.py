"""Independent checks for two explicitly registered Consideration masters.

Only work/production-system/final-qa receives new files. No renderer is imported.
After the first registered preview receipt, use --freeze-only before the full
render. Run without that option after master.mp4, master.json and qa.json finish.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
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

WIDTH, HEIGHT, FPS, RATE, CHANNELS = 1920, 1080, 60, 48000, 2
CANONICAL_SAMPLES = 864000
WAV_SHA = "0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b"
PCM_SHA = "493d1fa5efeaea437edcfecb241fb536439ec832d6f899750c4282c0d6895f84"
ORIGINAL_SHA = "2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a"


@dataclass(frozen=True)
class AuditProfile:
    project: str
    scene: str
    registration: str
    seconds: int
    audio_offset_seconds: int
    shots: tuple[tuple[str, int, int], ...]
    proof_frames: tuple[int, ...]

    @property
    def frames(self):
        return self.seconds * FPS

    @property
    def samples(self):
        return self.seconds * RATE

    @property
    def cuts(self):
        return tuple(start for _, start, _ in self.shots if start)

    def metadata(self):
        return {"project": self.project, "scene": self.scene, "registration": self.registration,
                "width": WIDTH, "height": HEIGHT, "fps": FPS, "frames": self.frames,
                "seconds": self.seconds, "temporal_samples": 2,
                "audio_offset_seconds": self.audio_offset_seconds,
                "picture_source_start_frame": self.audio_offset_seconds * FPS,
                "canonical_wav_sha256": WAV_SHA, "cut_frames": list(self.cuts),
                "shots": [{"id": name, "start_frame": start, "end_frame_exclusive": end}
                          for name, start, end in self.shots]}


PROFILES = {
    "concert-kit-consideration": AuditProfile(
        "concert-kit-consideration", "tools/concert_kit/consideration.py", "consideration-v1", 18, 0,
        (("approach", 0, 180), ("help", 180, 720), ("resolve", 720, 1080)),
        (0, 180, 360, 390, 420, 570, 660, 690, 720, 900, 1050, 1079)),
    "concert-kit-consideration-v2": AuditProfile(
        "concert-kit-consideration-v2", "tools/concert_motion_revision/render.py", "consideration-v2", 15, 3,
        (("contact", 0, 234), ("rise-response", 234, 540), ("garden", 540, 900)),
        (0, 120, 180, 233, 234, 235, 390, 480, 510, 531, 539, 540, 720, 870, 899)),
}
DEFAULT_PROJECT = "concert-kit-consideration"


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


def paths(root, profile):
    project = root / "projects" / profile.project / "project.json"
    directory = root / "work/pipeline" / profile.project / "review"
    return project, directory, root / "work/concert-kit/consideration-score.wav"


def audit_directory(root, profile):
    base = root / "work/production-system/final-qa"
    return base if profile.project == DEFAULT_PROJECT else base / profile.project


def validate_profile(manifest, profile):
    """Independent expected clocks and sources, not a duration inferred from input."""
    if manifest.get("project_id") != profile.project:
        raise RuntimeError("Project identity does not match the explicitly selected audit profile.")
    if manifest.get("video") != {"width": WIDTH, "height": HEIGHT, "fps": FPS}:
        raise RuntimeError("This audit requires the registered native 1080p60 video contract.")
    if manifest.get("quality", {}).get("review") != {
            "width": WIDTH, "height": HEIGHT, "temporal_samples": 2, "image_bit_depth": 8}:
        raise RuntimeError("This audit requires the registered two-sample RGB8 review preset.")
    if manifest.get("delivery") != {"profile": "h264", "source_transfer": "legacy_display_gamma", "color_space": "rec709"}:
        raise RuntimeError("This audit requires the registered legacy H264 SDR delivery contract.")
    wanted_audio = {"source": "work/concert-kit/consideration-score.wav", "source_sha256": WAV_SHA,
                    "offset_seconds": profile.audio_offset_seconds}
    if manifest.get("audio") != wanted_audio:
        raise RuntimeError("Audio source/offset changed or extra finishing operations were added; register another audit profile.")
    shots = manifest.get("shots", [])
    actual = tuple((s.get("id"), s.get("start_frame"), s.get("end_frame_exclusive")) for s in shots)
    if actual != profile.shots or any(s.get("scene") != profile.scene or s.get("renderer") != "p3d-kit"
                                     or s.get("params") != {} for s in shots):
        raise RuntimeError("Scene, shot boundaries or parameters differ from the explicit audit profile.")
    timing = manifest.get("timing", {})
    cuts = tuple(e.get("frame") for e in timing.get("events", []) if e.get("kind") == "authored_cut")
    if timing.get("fps") != FPS or cuts != profile.cuts:
        raise RuntimeError("Authored cut times differ from the explicit audit profile.")


def preparation_contract(root, profile, source_inputs):
    path = root / "work/pipeline" / profile.project / "preparation.json"
    preparation = read(path)
    if preparation.get("scene") != profile.registration:
        raise RuntimeError("Preparation belongs to a different registered scene.")
    expected = {"id": profile.registration,
                "module": "tools/concert_kit/render.py" if profile.project == DEFAULT_PROJECT else profile.scene,
                "fps": FPS, "duration_seconds": profile.seconds, "output_frame_count": profile.frames,
                "source_start_frame": profile.audio_offset_seconds * FPS, "cut_frames": list(profile.cuts)}
    # Original historical v1 preparation predates explicit module clock records.
    # Accept that one known format only; v2 must carry the complete clock.
    if profile.project != DEFAULT_PROJECT or "clock" in preparation:
        if preparation.get("clock") != expected:
            raise RuntimeError("Preparation source clock differs from the explicit audit profile.")
    hashes = preparation.get("source_sha256", {})
    if not hashes or any(source_inputs.get(name) != digest for name, digest in hashes.items()):
        raise RuntimeError("Preparation source files are not covered by the frozen render receipt.")
    return {"path": str(path.relative_to(root)), "sha256": sha(path),
            "clock": preparation.get("clock"), "source_file_count": len(hashes)}


def program_audio(canonical, profile):
    start = profile.audio_offset_seconds * RATE
    excerpt = canonical[start:start + profile.samples]
    if len(excerpt) != profile.samples:
        raise RuntimeError("Canonical audio does not cover the explicitly registered excerpt.")
    return excerpt


def review_frames(profile, boundaries):
    random = sorted(map(int, np.random.default_rng(20261121 + profile.frames).choice(profile.frames, 8, replace=False)))
    selected = set(profile.proof_frames) | set(random)
    for boundary in boundaries:
        selected.update(f for f in (boundary - 1, boundary, boundary + 1) if 0 <= f < profile.frames)
    return sorted(selected), random


def current_hashes(root, expected):
    return {name: sha(root / name) for name in expected}


def picture_contract(root, manifest):
    related = {}
    for name in ("timing", "style"):
        value = manifest.get(name, {})
        related[name] = read(root / value) if isinstance(value, str) else value
    return {"video": manifest["video"], "quality": manifest["quality"]["review"],
            "shots": manifest["shots"], "seed": manifest["production"]["random_seed"], **related}


def freeze(root, audit, profile):
    target = audit / "frozen-inputs.json"
    project, directory, wav = paths(root, profile)
    manifest = read(project)
    validate_profile(manifest, profile)
    receipt_path = directory / "shots" / profile.shots[0][0] / "receipt.json"
    receipt = read(receipt_path)
    provenance = receipt["provenance"]
    if jsha(provenance) != receipt["fingerprint"]:
        raise RuntimeError("Initial render receipt has inconsistent provenance.")
    if current_hashes(root, provenance["inputs"]) != provenance["inputs"]:
        raise RuntimeError("A frozen picture input already differs from its rendering receipt.")
    if sha(wav) != WAV_SHA:
        raise RuntimeError("Canonical source audio differs from the expected WAV.")
    contract = picture_contract(root, manifest)
    if (provenance.get("shot") != manifest["shots"][0] or provenance.get("timing") != contract["timing"]
            or provenance.get("style") != contract["style"] or provenance.get("seed") != contract["seed"]
            or provenance.get("settings") != {"fps": FPS, **contract["quality"]} or provenance.get("audio") != {}):
        raise RuntimeError("Initial receipt does not describe the current registered picture contract.")
    preparation = preparation_contract(root, profile, provenance["inputs"])
    value = {"schema_version": 2, "recorded_at_utc": now(), "project": profile.project,
             "audit_profile": profile.metadata(), "preparation": preparation,
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
    if params != {"rate": RATE, "channels": CHANNELS, "sample_width": 3, "samples_per_channel": CANONICAL_SAMPLES}:
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


def audit_master(root, audit, profile):
    baseline = read(audit / "frozen-inputs.json")
    if baseline.get("project") != profile.project:
        raise RuntimeError("Frozen baseline belongs to a different audit project.")
    if jsha(baseline["inputs"]) != baseline["inputs_sha256"]:
        raise RuntimeError("Frozen baseline source mapping has an inconsistent identity.")
    if baseline.get("audit_profile") != profile.metadata():
        if not (profile.project == DEFAULT_PROJECT and baseline.get("schema_version") == 1
                and "audit_profile" not in baseline):
            raise RuntimeError("Frozen baseline uses a different explicit audit profile.")
    project_path, directory, wav = paths(root, profile)
    master = directory / "master.mp4"
    for required in (master, directory / "master.json", directory / "qa.json"):
        if not required.is_file():
            raise RuntimeError(f"Final delivery is not ready: {required}")
    run_dir = audit / ("run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"))
    run_dir.mkdir(parents=True, exist_ok=False)
    report = {"schema_version": 2, "started_at_utc": now(), "audit_profile": profile.metadata(),
              "auditor": {"path": str(Path(__file__).resolve()),
                          "sha256": sha(Path(__file__)), "python_version": sys.version},
              "baseline_sha256": sha(audit / "frozen-inputs.json"), "errors": [], "warnings": [],
              "scope": "Independent technical decode, timing, audio alignment, source provenance and selected RGB checks. No real-time playback or artistic approval is claimed."}
    errors, warnings = report["errors"], report["warnings"]

    def check(condition, message):
        if not condition:
            errors.append(message)

    try:
        print("Checking delivery identity and frozen source inputs", flush=True)
        manifest = read(project_path)
        validate_profile(manifest, profile)
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
        report["preparation"] = preparation_contract(root, profile, baseline["inputs"])
        if "preparation" in baseline:
            check(report["preparation"] == baseline["preparation"], "Preparation identity changed after the source freeze.")
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
        check(set(frame_sources) == set(range(profile.frames)), f"Source shot ranges do not cover the exact {profile.frames} output frames.")
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
        check(len(frames) == profile.frames, f"Decoded video has {len(frames)} frames instead of {profile.frames}.")
        check(not pts_errors, f"Video presentation timestamps differ from the exact 60 fps clock: {pts_errors[:12]}.")
        check((video.get("width"), video.get("height")) == (WIDTH, HEIGHT), "Video dimensions are not native 1920x1080.")
        check(all((f.get("width"), f.get("height")) == (WIDTH, HEIGHT) for f in frames), "Decoded frame dimensions vary.")
        check(Fraction(video["avg_frame_rate"]) == Fraction(FPS) and Fraction(video["r_frame_rate"]) == Fraction(FPS), "Video frame-rate metadata is not 60 fps.")
        check(Fraction(video["duration_ts"]) * base == profile.seconds, f"Video stream duration is not exactly {profile.seconds} seconds.")
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
        check(audio.get("codec_name") == "aac", "Audio codec is not the registered AAC delivery.")
        check(int(audio.get("sample_rate", 0)) == RATE and audio.get("channels") == CHANNELS, "Audio must be 48 kHz stereo.")
        check(audio.get("channel_layout") == "stereo", "Audio channel layout is not stereo.")
        audio_duration = Fraction(audio["duration_ts"]) * Fraction(audio["time_base"])
        check(audio_duration == profile.seconds, f"Audio stream program duration is not exactly {profile.seconds} seconds.")
        check(float(audio.get("start_time", "0")) == 0, "Audio stream does not begin at program time zero.")
        canonical, pcm_sha, wav_params = read_pcm24(wav)
        check(pcm_sha == PCM_SHA, "Canonical PCM payload differs from the verified excerpt.")
        original = program_audio(canonical, profile)
        raw = command(["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "2", "-i", str(master),
                       "-map", "0:a:0", "-vn", "-sn", "-dn", "-c:a", "pcm_f32le", "-f", "f32le", "pipe:1"])
        decoded_audio = np.frombuffer(raw, "<f4").reshape(-1, CHANNELS).astype(np.float64)
        padding = len(decoded_audio) - profile.samples
        check(0 <= padding < 1024, f"Unexpected AAC decoded sample count: {len(decoded_audio)} samples per channel.")
        check(np.all(np.isfinite(decoded_audio)), "Decoded audio contains non-finite values.")
        peak = float(np.max(np.abs(decoded_audio)))
        excess = int(np.count_nonzero(np.abs(decoded_audio) >= 1.0))
        check(excess == 0, f"Decoded AAC has {excess} samples at or above full scale.")
        alignments = []
        for third in range(3):
            low = third * profile.seconds / 3 + 0.5
            high = (third + 1) * profile.seconds / 3 - 0.5
            candidates = [round(t * RATE) for t in np.arange(low, high - 2 + 0.001, 0.25)]
            start = max(candidates, key=lambda p: float(np.mean(original[p:p + 2 * RATE] ** 2)))
            item = alignment_window(original, decoded_audio, start, start + 2 * RATE)
            item["canonical_start_seconds"] = profile.audio_offset_seconds + item["start_seconds"]
            item["original_song_start_seconds"] = 137.5 + item["canonical_start_seconds"]
            alignments.append(item)
            check(item["source_rms"] > 1e-4, "Selected alignment window is effectively silent.")
            check(item["zero_lag_correlation"] >= 0.98, "Decoded AAC does not sufficiently correlate at the intended source time.")
            check(abs(item["best_lag_samples"]) <= 1, f"Audio alignment differs by {item['best_lag_samples']} samples.")
            check(item["fitted_gain_db"] is not None and abs(item["fitted_gain_db"]) <= 0.25,
                  "Audio amplitude differs from the unchanged canonical excerpt beyond the codec allowance.")
        packets = probe(master, "-select_streams", "a:0", "-show_packets")["packets"]
        provenance = read(root / "work/concert-kit/audio-provenance.json")
        check(provenance.get("source_sha256") == ORIGINAL_SHA and provenance.get("source_start_seconds") == 137.5
              and provenance.get("source_end_seconds") == 155.5 and provenance.get("time_stretch") is False,
              "Prepared excerpt provenance does not identify the intended unchanged-speed source interval.")
        report["audio"] = {"codec": audio.get("codec_name"), "rate": int(audio["sample_rate"]),
                           "channels": audio["channels"], "stream_duration_seconds": float(audio_duration),
                           "decoded_samples_per_channel": len(decoded_audio), "logical_program_samples_per_channel": profile.samples,
                           "decoded_tail_padding_samples_per_channel": padding,
                           "decoded_peak": peak, "decoded_peak_dbfs": 20 * math.log10(peak) if peak else None,
                           "samples_at_or_above_full_scale": excess,
                           "canonical_wav_sha256": sha(wav), "canonical_pcm_s24le_sha256": pcm_sha,
                           "canonical_wav_parameters": wav_params, "source_provenance": provenance,
                           "canonical_excerpt_sample_range": [profile.audio_offset_seconds * RATE,
                                                               profile.audio_offset_seconds * RATE + profile.samples],
                           "canonical_excerpt_interval_seconds": [profile.audio_offset_seconds,
                                                                  profile.audio_offset_seconds + profile.seconds],
                           "original_song_interval_seconds": [137.5 + profile.audio_offset_seconds,
                                                              137.5 + profile.audio_offset_seconds + profile.seconds],
                           "extra_finishing_gain_fades_or_stretch": False,
                           "alignment_windows": alignments,
                           "aac_first_packet": packets[0], "aac_last_packet": packets[-1],
                           "priming_handling": "FFmpeg demuxer/decoder applies the MP4 edit list and skip-samples metadata. Correlation uses logical program time zero; possible sub-frame trailing AAC padding is recorded separately.",
                           "interpretation": "Sample alignment with the exact prepared excerpt is technical evidence, not musical or creative synchronization approval."}

        print("Comparing decoded native RGB at actual cuts and worker boundaries", flush=True)
        batches = observed_batches(directory, manifest["shots"])
        check(bool(batches), "No worker batches could be recovered from the render logs.")
        check(all(b["temporal_samples"] == [2] for b in batches),
              "Worker logs include an unexpected temporal sample count.")
        cuts = {s["start_frame"] for s in manifest["shots"] if s["start_frame"] > 0}
        check(cuts == set(profile.cuts), "Observed shot cuts differ from the explicit audit profile.")
        boundaries = sorted({b["start_frame"] for b in batches if b["start_frame"] > 0} | cuts)
        selected, random_frames = review_frames(profile, boundaries)
        select = "+".join(f"eq(n\\,{frame})" for frame in selected)
        filters = f"select={select},scale=in_color_matrix=bt709:in_range=tv:out_range=pc:flags=accurate_rnd+full_chroma_int,format=rgb24"
        argv = ["ffmpeg", "-v", "error", "-xerror", "-nostdin", "-threads", "2", "-filter_threads", "1",
                "-i", str(master), "-map", "0:v:0", "-an", "-sn", "-dn", "-vf", filters,
                "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
        small, source_small, comparisons = {}, {}, []
        evidence_frames = set(profile.proof_frames) | {f for cut in profile.cuts for f in (cut - 1, cut, cut + 1)}
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
                if frame not in small:
                    continue
                sheet.paste(small[frame], (col * 320, row * 210))
                draw.text((col * 320 + 6, row * 210 + 184), f"{kind}: frame {frame}, {frame / FPS:.3f}s", fill="white")
        sheet.save(run_dir / "cut-and-batch-boundaries.jpg", quality=94)
        report["picture_comparison"] = {"decode_transform": "Inverse limited-range BT.709 YUV matrix/range only, with full chroma interpolation. No transfer-function or gamma conversion.",
                                        "gross_mismatch_bounds": {"mae_8bit_max": 10, "psnr_db_min": 25},
                                        "bounds_scope": "Gross identity/encoding errors only, not an artistic quality threshold.",
                                        "reproducible_random_frames": random_frames,
                                        "random_seed": 20261121 + profile.frames,
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
    parser.add_argument("--project", choices=sorted(PROFILES), default=DEFAULT_PROJECT)
    parser.add_argument("--freeze-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    profile = PROFILES[args.project]
    audit = audit_directory(root, profile)
    audit.mkdir(parents=True, exist_ok=True)
    if args.freeze_only:
        freeze(root, audit, profile)
        return 0
    return audit_master(root, audit, profile)


if __name__ == "__main__":
    sys.exit(main())
