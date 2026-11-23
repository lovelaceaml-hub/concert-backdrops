"""Assemble one explicitly reviewed Song 11 host cohort, with final QA pending.

The original strict cloud assembler remains unchanged. This entry point is
intentionally scoped to the two observed hosts of the frozen producing request;
it is not a generic override for arbitrary runtime or input mismatches.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess

from tools.s11_cloud import common as c
from tools.s11_cloud.assemble import probe
from tools.s11_cloud.transport import decrypt_directory

PRODUCING_COMMIT = "eec8d16519ea82309ef851975792e9dfc548da03"
RUN_ID = 45108198761
REQUEST_ID = "s11-renewed-20261123-master"
REQUEST_SHA = "cdead98a1d3d809d1803831b805636c2a7353fd7609889eb14fdec8b68ca5190"
CONTRACT_SHA = "87b19dea408188d88eef2bad616adb606ef84f1545b0259d555d8ec46509aef4"
HOST_FIELDS = ("github_image_version", "platform")
HOSTS = {
    "2188eb82bbb9c539367a3424630dbcca818f313950751afc2c72e18c0f661d7c": {
        "github_image_version": "20261116.133.1",
        "platform": "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39",
    },
    "c34e7f5bde42bb5fb5568817872b16521dcf3acfffe4ab9c2c95066a15ce8ce7": {
        "github_image_version": "20261116.376.1",
        "platform": "Linux-7.0.0-1017-azure-x86_64-with-glibc2.39",
    },
}


def git_blob(path):
    return subprocess.check_output(
        ["git", "show", f"{PRODUCING_COMMIT}:{path}"], cwd=c.ROOT)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_contract():
    """Read the producing commit, never the changing working tree or HEAD."""
    request_bytes = git_blob("tools/s11_cloud/request.json")
    if sha_bytes(request_bytes) != REQUEST_SHA:
        raise ValueError("Frozen producing request has the wrong digest.")
    requested = json.loads(request_bytes)
    if (requested.get("id"), requested.get("mode"), requested.get("parts")) != (
            REQUEST_ID, "render", 40):
        raise ValueError("This assembler accepts only the reviewed full request.")
    manifest_bytes = git_blob("tools/s11_cloud/inputs/manifest.json")
    if sha_bytes(manifest_bytes) != requested["input_manifest_sha256"]:
        raise ValueError("Frozen producing manifest differs from its request.")
    manifest = json.loads(manifest_bytes)
    names = subprocess.check_output([
        "git", "ls-tree", "-r", "--name-only", PRODUCING_COMMIT,
        "tools/s11_cloud", ".github/workflows/s11-renewed-private-pictures.yml"],
        cwd=c.ROOT, text=True).splitlines()
    names = [name for name in names if
             (Path(name).parent.as_posix() == "tools/s11_cloud" and name.endswith(".py"))
             or name == ".github/workflows/s11-renewed-private-pictures.yml"]
    adapter = {name: sha_bytes(git_blob(name)) for name in names}
    certificate = git_blob("tools/s11_cloud/recipient.pem")
    if (sha_bytes(certificate) != requested["recipient_sha256"]
            or b"PRIVATE KEY" in certificate):
        raise ValueError("Frozen producing certificate is invalid.")
    if (manifest.get("source_audio_sha256") != c.AUDIO_SHA
            or manifest.get("prepared_audio_sha256") != c.SCORE_SHA
            or manifest.get("waveform_included") is not False):
        raise ValueError("Frozen producing audio provenance is invalid.")
    return dict(request=requested, manifest=manifest, adapter=adapter,
                certificate=certificate)


def validate_policy(policy):
    expected = dict(
        schema="s11-reviewed-host-cohorts-v1", producing_commit=PRODUCING_COMMIT,
        run_id=RUN_ID, request_id=REQUEST_ID, request_sha256=REQUEST_SHA,
        normalized_contract_sha256=CONTRACT_SHA,
        normalized_runtime_fields=list(HOST_FIELDS), allowed_fingerprints=HOSTS,
        assembly_authorized=True, final_delivery_approved=False,
        byte_identical_runtimes_claimed=False)
    if any(policy.get(key) != value for key, value in expected.items()):
        raise ValueError("Policy does not exactly match the two reviewed host cohorts.")
    if not policy.get("evidence") or not policy.get("required_final_qa"):
        raise ValueError("Policy must name the evidence and pending delivery checks.")


def load_policy(path):
    policy = json.loads(path.read_text())
    validate_policy(policy)
    for item in policy["evidence"]:
        evidence = (c.ROOT / item["path"]).resolve()
        if not evidence.is_relative_to(c.ROOT) or c.digest(evidence) != item["sha256"]:
            raise ValueError("Reviewed host evidence is missing or has changed.")
    return policy


def validate_identity(frozen, contract):
    check = copy.deepcopy(frozen)
    fingerprint = check.pop("fingerprint", None)
    if c.mapping_digest(check) != fingerprint:
        raise ValueError("Artifact full fingerprint is invalid.")
    if (frozen.get("schema") != "s11-cloud-picture-v1"
            or frozen.get("request") != contract["request"]
            or frozen.get("request_sha256") != REQUEST_SHA):
        raise ValueError("Artifact differs from the exact producing request.")
    if frozen.get("sources") != contract["manifest"]["picture_sources"]:
        raise ValueError("Artifact source map differs from the producing manifest.")
    if frozen.get("adapter") != contract["adapter"]:
        raise ValueError("Artifact adapter differs from the producing commit.")
    runtime = check.get("runtime", {})
    host = {key: runtime.pop(key, None) for key in HOST_FIELDS}
    if c.mapping_digest(check) != CONTRACT_SHA:
        raise ValueError("Artifact rendering dependencies or normalized contract differ.")
    if fingerprint not in HOSTS or host != HOSTS[fingerprint]:
        raise ValueError("Artifact host fingerprint has not been reviewed.")
    return fingerprint


def validate_receipt_meta(receipt, fingerprint, requested):
    part = receipt.get("part")
    if type(part) is not int or not 0 <= part < requested["parts"]:
        raise ValueError("Invalid picture part index.")
    start = c.FRAMES * part // requested["parts"]
    end = c.FRAMES * (part + 1) // requested["parts"]
    expected = dict(schema="s11-cloud-picture-chunk-v1", fingerprint=fingerprint,
                    request_id=REQUEST_ID, part=part, parts=requested["parts"],
                    start=start, end=end, width=1920, height=1080, fps=60, samples=2,
                    waveform_included=False)
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise ValueError("Picture receipt differs from its identity or exact assigned range.")
    if receipt.get("waveform_included") is not False:
        raise ValueError("Picture receipt does not exclude a waveform.")
    return part, start, end


def validate_coverage(parts, requested):
    if len(parts) != requested["parts"] or {p["part"] for p in parts} != set(range(40)):
        raise ValueError("Exactly one of every requested picture part is required.")
    cursor = 0
    for record in sorted(parts, key=lambda item: item["part"]):
        start, end = record["start"], record["end"]
        expected = (c.FRAMES * record["part"] // 40,
                    c.FRAMES * (record["part"] + 1) // 40)
        if (start, end) != expected or start != cursor or end <= start:
            raise ValueError("Picture ranges are altered, overlapping, or have a gap.")
        cursor = end
    if cursor != c.FRAMES:
        raise ValueError("Picture ranges do not cover all 16,500 frames.")


def validate_picture(picture, receipt, fingerprint, requested):
    part, start, end = validate_receipt_meta(receipt, fingerprint, requested)
    if picture.name != f"part-{start:06d}-{end:06d}.mp4":
        raise ValueError("Picture filename differs from its assigned range.")
    if receipt.get("sha256") != c.digest(picture) or receipt.get("bytes") != picture.stat().st_size:
        raise ValueError("Picture content does not match its receipt.")
    data = probe(picture)
    if len(data["streams"]) != 1 or data["streams"][0]["codec_type"] != "video":
        raise ValueError("A picture part must contain exactly one silent video stream.")
    stream = data["streams"][0]
    expected = dict(codec_name="h264", pix_fmt="yuv420p", width=1920, height=1080,
                    avg_frame_rate="60/1", r_frame_rate="60/1", color_range="tv",
                    color_space="bt709", color_transfer="bt709", color_primaries="bt709")
    if (any(stream.get(key) != value for key, value in expected.items())
            or int(stream.get("nb_frames", -1)) != end - start):
        raise ValueError("Picture stream differs from the native delivery format.")
    if abs(float(stream.get("duration", -1)) - (end - start) / 60) > 0.00001:
        raise ValueError("Picture stream duration differs from its assigned frame range.")
    return dict(part=part, start=start, end=end, fingerprint=fingerprint,
                host=HOSTS[fingerprint], picture=picture, sha256=receipt["sha256"],
                bytes=receipt["bytes"], stream_time_base=stream["time_base"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encrypted", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    policy = load_policy(args.policy.resolve())
    contract = load_contract()
    requested = contract["request"]
    envelopes = sorted(args.encrypted.resolve().rglob("*.tar.cms"))
    if len(envelopes) != requested["parts"]:
        raise ValueError("All 40 encrypted picture artifacts are required before assembly.")
    destination = args.out.resolve()
    staging = destination.with_name(destination.name + "-verified-parts")
    temporary = destination.with_name(destination.stem + ".assembling.mp4")
    if destination.exists() or staging.exists() or temporary.exists():
        raise ValueError("Existing output is preserved; choose a new destination.")
    score = c.ROOT / "work/s11_full2/score.wav"
    if c.digest(score) != c.SCORE_SHA:
        raise ValueError("Private score differs from the verified original preparation.")
    staging.mkdir(parents=True)
    certificate = staging / "producing-recipient.pem"
    certificate.write_bytes(contract["certificate"])
    parts = []
    for index, envelope in enumerate(envelopes):
        folder = staging / f"artifact-{index:02d}"
        decrypt_directory(envelope, folder, args.key.resolve(), certificate)
        frozen = json.loads((folder / "inputs.json").read_text())
        fingerprint = validate_identity(frozen, contract)
        pictures = list(folder.glob("part-*.mp4"))
        if len(pictures) != 1:
            raise ValueError("Each artifact must contain exactly one picture part.")
        picture = pictures[0]
        expected_names = {"bundle.json", "inputs.json", picture.name,
                          picture.with_suffix(".json").name}
        if {p.name for p in folder.iterdir()} != expected_names:
            raise ValueError("Unexpected file in the authenticated full-picture bundle.")
        receipt = json.loads(picture.with_suffix(".json").read_text())
        record = validate_picture(picture, receipt, fingerprint, requested)
        record.update(encrypted_sha256=c.digest(envelope),
                      encrypted_bytes=envelope.stat().st_size)
        parts.append(record)
    validate_coverage(parts, requested)
    parts.sort(key=lambda item: item["part"])
    if len({part["stream_time_base"] for part in parts}) != 1:
        raise ValueError("Picture chunks have differing stream time bases.")
    concat = staging / "concat.txt"
    concat.write_text("".join(
        f"file '{part['picture'].relative_to(staging).as_posix()}'\n" for part in parts))
    # Identical picture stream-copy/audio encoding behavior to the strict assembler.
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
    for part in parts:
        part["picture"] = str(part["picture"].relative_to(staging))
    c.write_json(destination.with_suffix(".json"), dict(
        schema="s11-reviewed-host-assembled-v1", request=requested,
        producing_commit=PRODUCING_COMMIT, run_id=RUN_ID,
        assembly_policy_sha256=c.digest(args.policy.resolve()),
        normalized_contract_sha256=CONTRACT_SHA,
        observed_full_fingerprints=sorted({part["fingerprint"] for part in parts}),
        allowed_full_fingerprints=HOSTS, parts=parts,
        compatibility_evidence=policy["evidence"], byte_identical_runtimes_claimed=False,
        local_audio_sha256=c.SCORE_SHA, sha256=c.digest(destination),
        bytes=destination.stat().st_size, frames=c.FRAMES, duration=275, native_render=True,
        final_delivery_approved=False, full_decode_and_audio_qa="pending",
        cross_cohort_join_visual_qa="pending", story_and_costume_visual_qa="pending"))
    print(json.dumps(dict(event="reviewed_host_master_assembled", path=str(destination),
                          full_delivery_qa="pending")))


if __name__ == "__main__":
    main()
