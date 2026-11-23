"""Stage a reviewable public request; never upload inputs or include a waveform."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

from . import common as c


def main():
    import numpy as np
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True)
    parser.add_argument("--mode", choices=("probe", "render"), default="probe")
    parser.add_argument("--parts", type=int, default=40)
    parser.add_argument("--key-dir", type=Path, default=c.ROOT / "work/s11_cloud/private")
    args = parser.parse_args()
    if c.digest(c.ROOT / "work/song-inputs/s11-original.mp3") != c.AUDIO_SHA:
        raise ValueError("Freeze requires the actual verified original recording locally.")
    if c.digest(c.ROOT / "work/s11_full2/score.wav") != c.SCORE_SHA:
        raise ValueError("Freeze requires the actual verified prepared score locally.")
    key_dir = args.key_dir.resolve()
    if not key_dir.is_relative_to((c.ROOT / "work").resolve()):
        raise ValueError("The private key must remain under ignored work/, outside the committed package.")
    key_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    key_dir.chmod(0o700)
    key = key_dir / "recipient-private.pem"
    cert = c.HERE / "recipient.pem"
    if key.exists() != cert.exists():
        raise ValueError("A partial key pair exists; preserve it and resolve explicitly before freezing.")
    if not key.exists():
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:3072", "-nodes", "-sha256",
                        "-keyout", str(key), "-out", str(cert), "-days", "30",
                        "-subj", "/CN=Song 11 private render recipient",
                        "-addext", "keyUsage=keyEncipherment"], check=True, capture_output=True)
    key.chmod(0o600)
    key_public = subprocess.check_output(["openssl", "pkey", "-in", str(key), "-pubout"])
    cert_public = subprocess.check_output(["openssl", "x509", "-in", str(cert), "-pubkey", "-noout"])
    if key_public != cert_public:
        raise ValueError("The preserved private key does not match the public recipient certificate.")
    c.INPUTS.mkdir(parents=True, exist_ok=True)
    analysis = {}
    for name in ("features.npz", "music_fx.npz"):
        source = c.ROOT / "work/s11_full2" / name
        data = source.read_bytes()
        (c.INPUTS / name).write_bytes(data)
        with np.load(source, allow_pickle=False) as arrays:
            specs = {key: dict(shape=list(arrays[key].shape), dtype=str(arrays[key].dtype))
                     for key in arrays.files}
        analysis[name] = dict(bytes=len(data), sha256=c.digest(source), arrays=specs)
    shutil.copyfile(c.ROOT / "work/s11_full2/provenance.json", c.INPUTS / "provenance.json")
    definition = dict(schema="s11-cloud-inputs-v1", source_audio_sha256=c.AUDIO_SHA,
                      prepared_audio_sha256=c.SCORE_SHA, waveform_included=False,
                      source_clock=[0, 260], final_fade_seconds=0.05, silent_hold_seconds=15,
                      total_seconds=c.TOTAL, engine_pins=c.PINS, analysis=analysis,
                      provenance_sha256=c.digest(c.INPUTS / "provenance.json"),
                      picture_sources=c.picture_sources(),
                      creative_source_commit=subprocess.check_output(
                          ["git", "rev-parse", "HEAD"], cwd=c.ROOT, text=True).strip())
    c.write_json(c.INPUTS / "manifest.json", definition)
    value = dict(schema="s11-cloud-request-v1", id=args.id, mode=args.mode, parts=args.parts,
                 repository="lovelaceaml-hub/concert-backdrops", branch="creative/s11-renewed-20261122",
                 width=1920, height=1080, fps=60, frames=16500, samples=2, crf=14,
                 picture_delay=0.1, probe_seconds=[58, 105.7, 118.8, 186, 205],
                 input_manifest_sha256=c.digest(c.INPUTS / "manifest.json"),
                 recipient_sha256=c.digest(cert),
                 encryption="CMS AES-256-GCM with RSA-OAEP SHA256; private key remains local")
    c.write_json(c.REQUEST, value)
    c.validate_picture_analysis()
    c.validate_picture_sources()
    print(json.dumps(dict(event="request_staged_not_published", request_id=args.id,
                          analysis_bytes=sum(v["bytes"] for v in analysis.values()),
                          private_key=str(key.relative_to(c.ROOT)),
                          original_recording_uploaded=False)))


if __name__ == "__main__":
    main()
