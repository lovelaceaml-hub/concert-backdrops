"""Render this request's silent pictures and expose only encrypted artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from . import common as c
from .transport import encrypt_directory


def install_picture_contract():
    # This is a deliberately separate adapter. The full renewed route remains
    # unchanged and still validates its real WAV. This route validates the exact
    # derived maps instead; it neither supplies nor invents an audio waveform.
    from tools.s11_renewed import render as renewed
    renewed.validate_full_analysis = c.validate_picture_analysis
    renewed.identity = c.identity
    return renewed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, default=0)
    args = parser.parse_args()
    requested = c.request()
    if not 0 <= args.part < requested["parts"] or (requested["mode"] == "probe" and args.part != 0):
        raise ValueError("Part is outside the frozen request.")
    frozen = c.identity()
    renewed = install_picture_contract()
    output = c.ROOT / "work/s11_cloud" / requested["id"]
    plain = output / ("plain-probe" if requested["mode"] == "probe" else f"plain-part-{args.part:02d}")
    plain.mkdir(parents=True, exist_ok=True)
    settings = argparse.Namespace(width=1920, height=1080, samples=2, crf=requested["crf"],
                                  baseline=False, stop_file=None, out=plain)
    if requested["mode"] == "probe":
        settings.stills = ",".join(map(str, requested["probe_seconds"]))
        renewed.render_stills(settings)
        suffix = "probe"
    else:
        settings.start = c.FRAMES * args.part // requested["parts"]
        settings.end = c.FRAMES * (args.part + 1) // requested["parts"]
        settings.out = plain / f"part-{settings.start:06d}-{settings.end:06d}.mp4"
        renewed.render_chunk(settings)
        streams = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "json",
            str(settings.out)], text=True))["streams"]
        if [stream["codec_type"] for stream in streams] != ["video"]:
            raise ValueError("A remote picture chunk must contain exactly one video stream and no audio.")
        receipt_path = settings.out.with_suffix(".json")
        receipt = json.loads(receipt_path.read_text())
        receipt.update(schema="s11-cloud-picture-chunk-v1", request_id=requested["id"],
                       part=args.part, parts=requested["parts"], waveform_included=False)
        c.write_json(receipt_path, receipt)
        suffix = f"part-{args.part:02d}"
    if c.identity()["fingerprint"] != frozen["fingerprint"]:
        raise ValueError("Inputs changed while producing the artifact.")
    c.write_json(plain / "inputs.json", frozen)
    encrypted = output / "encrypted" / f"{requested['id']}-{suffix}.tar.cms"
    receipt = encrypt_directory(plain, encrypted, c.HERE / "recipient.pem")
    print(json.dumps(dict(event="encrypted_artifact_ready", request_id=requested["id"],
                          part=suffix, **receipt)), flush=True)


if __name__ == "__main__":
    main()
