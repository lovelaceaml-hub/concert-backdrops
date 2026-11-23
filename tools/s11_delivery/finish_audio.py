"""Give the reviewed Song 11 delivery 1 dB of audio headroom without changing pictures.

The pinned prepared score already contains the established trim, fade and silent
hold. This step changes gain only and encodes directly from that score once.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

SCORE_SHA256 = "fa488e4805cdc43b1f0f38915d67044ef92a9e659a59ac916d4b75b4cbb6d29b"


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(command):
    result = subprocess.run(command, capture_output=True, check=True)
    if result.stderr.strip():
        raise RuntimeError(result.stderr.decode(errors="replace")[-4000:])
    return result.stdout


def picture_packets(path):
    return json.loads(run([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_packets",
        "-show_entries", "packet=pts,dts,duration,size,data_hash",
        "-show_data_hash", "sha256", "-of", "json", str(path),
    ]))["packets"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--score", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.receipt.exists():
        raise RuntimeError("Use new output and receipt paths; existing delivery bytes are preserved.")
    if digest(args.score) != SCORE_SHA256:
        raise RuntimeError("Prepared original score differs from the frozen Song 11 identity.")
    before = picture_packets(args.video)
    if len(before) != 16500:
        raise RuntimeError("Expected the complete 16,500-frame master.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-v", "error", "-n", "-i", str(args.video), "-i", str(args.score),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
        "-af", "volume=-1dB", "-c:a", "aac", "-b:a", "320k",
        "-ar", "48000", "-ac", "2", "-t", "275", "-movflags", "+faststart", str(args.out),
    ]
    run(command)
    after = picture_packets(args.out)
    if before != after:
        raise RuntimeError("Picture packet bytes or timestamps changed during audio finalization.")
    pcm = np.frombuffer(run([
        "ffmpeg", "-v", "error", "-i", str(args.out), "-map", "0:a:0",
        "-t", "275", "-ar", "48000", "-ac", "2", "-f", "f32le", "-",
    ]), dtype="<f4").reshape(-1, 2)
    if len(pcm) != 13_200_000 or not np.isfinite(pcm).all():
        raise RuntimeError("Decoded stereo audio is incomplete or contains nonfinite samples.")
    channels = []
    for i in range(2):
        samples = np.abs(pcm[:, i])
        peak = float(samples.max())
        count = int(np.count_nonzero(samples >= 1.0))
        if peak >= 1.0:
            raise RuntimeError("The encoded audio still exceeds full scale.")
        channels.append(dict(channel=i + 1, decoded_sample_peak=peak,
                             decoded_samples_at_or_above_full_scale=count))
    record = dict(
        schema="s11-audio-headroom-finalization-v1", status="passed",
        input_video_filename=args.video.name, input_video_sha256=digest(args.video),
        original_prepared_score_sha256=SCORE_SHA256, gain_db=-1,
        output_filename=args.out.name, output_sha256=digest(args.out), bytes=args.out.stat().st_size,
        duration_seconds=275, source_clock_changed=False, fade_or_pad_reapplied=False,
        video_encoded_again=False, video_packet_count=len(after),
        all_picture_packet_hashes_and_timestamps_identical=True,
        picture_packet_inventory_sha256=hashlib.sha256(
            json.dumps(after, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        sample_rate=48000, samples_per_channel=len(pcm), channels=channels,
        audio_encoded_from="unchanged original prepared score; not prior AAC",
        peak_scope="Complete decoded stereo sample peaks, not oversampled true peaks.",
        ffmpeg=run(["ffmpeg", "-version"]).decode().splitlines()[0],
        final_decode_timing_alignment_and_visual_checks="Recorded separately.",
    )
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
