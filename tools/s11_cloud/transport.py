"""Authenticated public-key artifact envelopes; the private key is local only."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

from . import common as c


def encrypt_directory(source, destination, certificate):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    files = sorted(path for path in source.rglob("*") if path.is_file() and path.name != "bundle.json"
                   and path.suffix in (".png", ".mp4", ".json"))
    if not files or any(path.is_symlink() or "assembling" in path.name for path in files):
        raise ValueError("Only completed, regular picture and receipt files can be packaged.")
    records = {str(path.relative_to(source)): dict(bytes=path.stat().st_size, sha256=c.digest(path))
               for path in files}
    c.write_json(source / "bundle.json", dict(schema="s11-encrypted-bundle-v1", files=records))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="s11-envelope-") as temporary:
        archive = Path(temporary) / "pictures.tar"
        with tarfile.open(archive, "w") as stream:
            for path in files + [source / "bundle.json"]:
                stream.add(path, arcname=str(path.relative_to(source)), recursive=False)
        subprocess.run(["openssl", "cms", "-encrypt", "-binary", "-aes-256-gcm", "-stream",
                        "-outform", "DER", "-in", str(archive), "-out", str(destination),
                        "-recip", str(certificate), "-keyopt", "rsa_padding_mode:oaep",
                        "-keyopt", "rsa_oaep_md:sha256"], check=True)
    return dict(schema="s11-encrypted-artifact-v1", encrypted_sha256=c.digest(destination),
                encrypted_bytes=destination.stat().st_size, files=len(records),
                encryption="AES-256-GCM authenticated CMS; RSA-OAEP SHA256",
                original_audio_included=False)


def decrypt_directory(envelope, destination, private_key, certificate):
    """Authenticate before extracting; failed decryptions never become accepted files."""
    destination = Path(destination).resolve()
    with tempfile.TemporaryDirectory(prefix="s11-decrypt-") as temporary:
        archive = Path(temporary) / "pictures.tar"
        subprocess.run(["openssl", "cms", "-decrypt", "-binary", "-inform", "DER",
                        "-in", str(envelope), "-out", str(archive), "-recip", str(certificate),
                        "-inkey", str(private_key)], check=True, capture_output=True)
        stage = Path(temporary) / "verified"
        stage.mkdir()
        with tarfile.open(archive) as stream:
            members = stream.getmembers()
            if any(not item.isfile() or Path(item.name).is_absolute()
                   or ".." in Path(item.name).parts for item in members):
                raise ValueError("Unexpected archive member.")
            if len({item.name for item in members}) != len(members):
                raise ValueError("Duplicate archive member.")
            stream.extractall(stage, filter="data")
        definition = json.loads((stage / "bundle.json").read_text())
        if definition.get("schema") != "s11-encrypted-bundle-v1":
            raise ValueError("Unknown encrypted bundle schema.")
        actual = {str(p.relative_to(stage)) for p in stage.rglob("*") if p.is_file()} - {"bundle.json"}
        if actual != set(definition["files"]):
            raise ValueError("Bundle inventory does not match its manifest.")
        for name, expected in definition["files"].items():
            path = stage / name
            if path.stat().st_size != expected["bytes"] or c.digest(path) != expected["sha256"]:
                raise ValueError("Decrypted artifact failed its byte checks: " + name)
        if destination.exists():
            raise ValueError("Select a new extraction directory; existing output is preserved.")
        destination.mkdir(parents=True)
        import shutil
        for path in stage.iterdir():
            shutil.move(str(path), destination / path.name)
    return definition
