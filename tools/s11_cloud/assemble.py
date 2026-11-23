"""Locally decrypt one complete remote cohort and add the private verified score."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from . import common as c
from .transport import decrypt_directory


def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], text=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encrypted", type=Path, required=True, help="Directory of downloaded .tar.cms files.")
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--probe-only", action="store_true", help="Decrypt the five native review frames without assembly.")
    args = parser.parse_args()
    requested = c.request()
    envelopes = sorted(args.encrypted.resolve().rglob("*.tar.cms"))
    if not envelopes:
        raise ValueError("No encrypted artifacts found.")
    destination = args.out.resolve()
    if destination.exists():
        raise ValueError("Existing output is preserved; choose a new destination.")
    staging = destination.with_name(destination.name + "-verified-parts")
    if staging.exists():
        raise ValueError("Existing extracted parts are preserved; choose a new output name.")
    cohort, parts = None, []
    for index, envelope in enumerate(envelopes):
        folder = staging / f"artifact-{index:02d}"
        decrypt_directory(envelope, folder, args.key.resolve(), c.HERE / "recipient.pem")
        frozen = json.loads((folder / "inputs.json").read_text())
        check = dict(frozen)
        fingerprint = check.pop("fingerprint")
        if (c.mapping_digest(check) != fingerprint or frozen.get("schema") != "s11-cloud-picture-v1"
                or frozen.get("request") != requested):
            raise ValueError("Artifact is not bound to this exact remote request.")
        if cohort is None:
            cohort = fingerprint
        elif cohort != fingerprint:
            raise ValueError("Refusing to mix local chunks or different remote runtimes/inputs.")
        for picture in folder.glob("part-*.mp4"):
            receipt = json.loads(picture.with_suffix(".json").read_text())
            if (receipt.get("schema") != "s11-cloud-picture-chunk-v1"
                    or receipt.get("fingerprint") != cohort
                    or receipt.get("request_id") != requested["id"]
                    or receipt.get("sha256") != c.digest(picture)
                    or receipt.get("waveform_included") is not False):
                raise ValueError("Invalid remote part receipt.")
            data = probe(picture)
            if len(data["streams"]) != 1 or data["streams"][0]["codec_type"] != "video":
                raise ValueError("Unexpected audio or additional stream in a picture chunk.")
            stream = data["streams"][0]
            if (stream["width"], stream["height"], stream["avg_frame_rate"], int(stream["nb_frames"])) != (
                    1920, 1080, "60/1", receipt["end"] - receipt["start"]):
                raise ValueError("Remote part dimensions/frame count do not match the receipt.")
            parts.append((receipt["start"], receipt["end"], picture))
    if args.probe_only:
        if requested["mode"] != "probe" or parts or len(envelopes) != 1:
            raise ValueError("Probe extraction requires one probe artifact.")
        print(json.dumps(dict(event="probe_decrypted", path=str(staging), fingerprint=cohort)))
        return
    if requested["mode"] != "render" or len(parts) != requested["parts"]:
        raise ValueError("All parts of a full render request are required.")
    parts.sort()
    cursor = 0
    for start, end, _ in parts:
        if start != cursor or end <= start:
            raise ValueError("Picture chunks overlap or leave a gap.")
        cursor = end
    if cursor != c.FRAMES:
        raise ValueError("The remote parts do not cover all 16,500 frames.")
    score = c.ROOT / "work/s11_full2/score.wav"
    if c.digest(score) != c.SCORE_SHA:
        raise ValueError("The private local score differs from the verified original preparation.")
    concat = staging / "concat.txt"
    concat.write_text("".join(f"file '{path.relative_to(staging).as_posix()}'\n" for _, _, path in parts))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.stem + ".assembling.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "1", "-i", str(concat),
                    "-i", str(score), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "320k", "-ar", "48000", "-t", "275", "-movflags", "+faststart", str(temporary)], check=True)
    data = probe(temporary)
    video = [s for s in data["streams"] if s["codec_type"] == "video"]
    audio = [s for s in data["streams"] if s["codec_type"] == "audio"]
    if (len(video), len(audio)) != (1, 1) or int(video[0]["nb_frames"]) != c.FRAMES:
        raise ValueError("Assembled master stream/frame validation failed.")
    if abs(float(data["format"]["duration"]) - c.TOTAL) > 1 / c.FPS:
        raise ValueError("Assembled master duration differs from 275 seconds.")
    temporary.replace(destination)
    c.write_json(destination.with_suffix(".json"), dict(
        schema="s11-cloud-assembled-v1", request=requested, remote_fingerprint=cohort,
        local_audio_sha256=c.SCORE_SHA, sha256=c.digest(destination), bytes=destination.stat().st_size,
        frames=c.FRAMES, duration=275, native_render=True, full_decode_and_audio_qa="pending"))
    print(json.dumps(dict(event="remote_master_assembled", path=str(destination), full_delivery_qa="pending")))


if __name__ == "__main__":
    main()
