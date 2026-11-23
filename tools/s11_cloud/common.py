"""Explicit source, analysis and runtime contracts for remote silent pictures."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
REQUEST = HERE / "request.json"
FRAMES, FPS, TOTAL = 16500, 60, 275
AUDIO_SHA = "70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004"
SCORE_SHA = "fa488e4805cdc43b1f0f38915d67044ef92a9e659a59ac916d4b75b4cbb6d29b"
PINS = {
    "work/nine_colours_minor/render1": "d928ff9eafe02ac3150f0c646bdcc497fe5a7278",
    "work/nine_colours_revision3/claude-final": "f43f4514e4bc42dc25166e90160d98219f5a0db4",
}


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def mapping_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def request():
    value = json.loads(REQUEST.read_text())
    fixed = dict(schema="s11-cloud-request-v1", repository="lovelaceaml-hub/concert-backdrops",
                 branch="creative/s11-renewed-20261122", width=1920, height=1080,
                 fps=FPS, frames=FRAMES, samples=2, picture_delay=0.1)
    if any(value.get(key) != expected for key, expected in fixed.items()):
        raise ValueError("The request does not match the renewed Song 11 picture contract.")
    if value.get("mode") not in ("probe", "render"):
        raise ValueError("Request mode must be probe or render.")
    if not re.fullmatch(r"[a-z0-9-]{8,80}", value.get("id", "")):
        raise ValueError("Invalid render request ID.")
    if type(value.get("parts")) is not int or not 1 <= value["parts"] <= 40:
        raise ValueError("Use 1 through 40 parts.")
    if type(value.get("crf")) is not int or not 0 <= value["crf"] <= 30:
        raise ValueError("Invalid CRF.")
    if value.get("probe_seconds") != [58, 105.7, 118.8, 186, 205]:
        raise ValueError("The review probe must retain all five selected compositions.")
    if digest(INPUTS / "manifest.json") != value["input_manifest_sha256"]:
        raise ValueError("Analysis/source manifest changed after this request was frozen.")
    cert = HERE / "recipient.pem"
    if digest(cert) != value["recipient_sha256"] or b"PRIVATE KEY" in cert.read_bytes():
        raise ValueError("The public recipient certificate does not match the request.")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        if (os.environ.get("GITHUB_REPOSITORY") != value["repository"]
                or os.environ.get("GITHUB_REF") != "refs/heads/" + value["branch"]):
            raise ValueError("This request is scoped to its recorded repository and branch.")
    return value


def manifest():
    value = json.loads((INPUTS / "manifest.json").read_text())
    if (value.get("schema") != "s11-cloud-inputs-v1"
            or value.get("source_audio_sha256") != AUDIO_SHA
            or value.get("prepared_audio_sha256") != SCORE_SHA
            or value.get("engine_pins") != PINS
            or value.get("waveform_included") is not False):
        raise ValueError("Unexpected source or private-input declaration.")
    if set(value["analysis"]) != {"features.npz", "music_fx.npz"}:
        raise ValueError("Only the two declared analysis maps are supported.")
    return value


def validate_picture_analysis():
    """A separate no-waveform contract, not a substituted or fake score.wav."""
    import numpy as np
    request()
    definition = manifest()
    for name, expected in definition["analysis"].items():
        path = ROOT / "work/s11_full2" / name
        if path.stat().st_size != expected["bytes"] or digest(path) != expected["sha256"]:
            raise ValueError(f"Analysis bytes changed: {name}")
        with np.load(path, allow_pickle=False) as data:
            if set(data.files) != set(expected["arrays"]):
                raise ValueError(f"Analysis fields changed: {name}")
            for key in data.files:
                array = data[key]
                spec = expected["arrays"][key]
                if list(array.shape) != spec["shape"] or str(array.dtype) != spec["dtype"]:
                    raise ValueError(f"Analysis shape/type changed: {name}/{key}")
                if not np.issubdtype(array.dtype, np.number) or not np.isfinite(array).all():
                    raise ValueError(f"Invalid analysis values: {name}/{key}")
            times = data["times"]
            if times[0] != 0 or times[-1] < TOTAL - 0.1 or not np.all(np.diff(times) > 0):
                raise ValueError(f"Analysis does not cover the full source clock: {name}")
    provenance_path = ROOT / "work/s11_full2/provenance.json"
    if (digest(provenance_path) != definition["provenance_sha256"]
            or digest(INPUTS / "provenance.json") != definition["provenance_sha256"]):
        raise ValueError("The exact preparation provenance bytes have changed.")
    provenance = json.loads(provenance_path.read_text())
    if (provenance.get("audio_sha256") != AUDIO_SHA
            or provenance.get("total_seconds") != TOTAL or provenance.get("fps") != FPS):
        raise ValueError("Source provenance no longer matches the picture clock.")


def picture_sources():
    from tools.s11_renewed import render as renewed
    values = renewed.source_hashes()
    values.pop("work/s11_full2/score.wav", None)
    return values


def validate_picture_sources():
    expected = manifest()["picture_sources"]
    actual = picture_sources()
    changed = sorted(key for key in set(expected) | set(actual) if expected.get(key) != actual.get(key))
    if changed:
        raise ValueError("Picture source/assets/fonts differ from the request: " + ", ".join(changed[:8]))
    return actual


def runtime():
    if sys.version.split()[0] != "3.12.14":
        raise ValueError("Use the recorded Python 3.12.14 runtime.")
    packages = {}
    for line in (ROOT / "tools/s11_renewed/requirements-render.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, expected = line.split("==")
        packages[name] = importlib.metadata.version(name)
        if packages[name] != expected:
            raise ValueError(f"Runtime mismatch for {name}: {packages[name]} != {expected}")
    expected_env = dict(PYTHONHASHSEED="0", LP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="1",
                        OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1", LIBGL_ALWAYS_SOFTWARE="1")
    if any(os.environ.get(key) != value for key, value in expected_env.items()):
        raise ValueError("Use the cloud workflow's deterministic worker environment.")
    def version(command):
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        return result.stdout.strip().splitlines()[0]
    mesa = subprocess.run(["dpkg-query", "-W", "-f=${Package}=${Version}\n",
                           "libegl-mesa0", "libgl1-mesa-dri"], capture_output=True, text=True)
    if os.environ.get("GITHUB_ACTIONS") == "true" and mesa.returncode:
        raise ValueError("The cloud runner must install both recorded Mesa packages.")
    return dict(python=sys.version.split()[0], packages=packages, environment=expected_env,
                architecture=platform.machine(), platform=platform.platform(),
                github_image=os.environ.get("ImageOS", "local"),
                github_image_version=os.environ.get("ImageVersion", "local"),
                ffmpeg=version(["ffmpeg", "-version"]), openssl=version(["openssl", "version"]),
                mesa_packages=mesa.stdout.strip(), mesa_query_status=mesa.returncode)


def identity(args=None):
    requested = request()
    validate_picture_analysis()
    sources = validate_picture_sources()
    adapter = {str(path.relative_to(ROOT)): digest(path) for path in sorted(HERE.glob("*.py"))}
    workflow = ROOT / ".github/workflows/s11-renewed-private-pictures.yml"
    adapter[str(workflow.relative_to(ROOT))] = digest(workflow)
    value = dict(schema="s11-cloud-picture-v1", request=requested,
                 request_sha256=digest(REQUEST), sources=sources, adapter=adapter,
                 runtime=runtime(), waveform_included=False,
                 width=1920, height=1080, fps=FPS, samples=2, crf=requested["crf"],
                 picture_delay=0.1, temporal_interpolation=False, spatial_upscale=False)
    value["fingerprint"] = mapping_digest(value)
    return value
