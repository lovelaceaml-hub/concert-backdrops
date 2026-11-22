"""Registered Song 11 beauty source, using the existing frame checkpoint worker.

This adapter reproduces the registered authored world. It does not substitute a
new recording, reinterpret old cues, or modify the historical production tools.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import sys

from PIL import Image

from .environment import worker_environment
from .project import PipelineError, Project, file_hash, read_data, safe_path, write_json


REFERENCE = "song11-beauty-v1"
REFERENCE_FILE = "pipeline/references/song11-beauty-v1.json"
SCENE = "tools/s11_full2/s11_full2.py"
MODULE = "tools/promo_beauty_example/render.py"
PREPARATION = "work/promo-beauty-rebuild/preparation.json"
DERIVED = ("features.npz", "music_fx.npz", "score.wav")
PICTURE_DELAY = 0.1


def reference(root: Path) -> dict:
    return read_data(root / REFERENCE_FILE)


def reference_module(root: Path):
    specification = importlib.util.spec_from_file_location("pipeline_approved_reference", root / MODULE)
    if specification is None or specification.loader is None:
        raise PipelineError("The registered beauty renderer is missing.")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def validate_shot(project: Project, shot: dict) -> None:
    params = shot.get("params", {})
    if shot["scene"] != SCENE or params.get("reference") != REFERENCE:
        raise PipelineError(f"p3d-approved accepts only the registered {REFERENCE} scene.")
    if set(params) - {"reference", "keep_grain"} or type(params.get("keep_grain", False)) is not bool:
        raise PipelineError("Approved scene params accept reference and boolean keep_grain only.")
    if project.fps != 60:
        raise PipelineError("The frozen beauty source uses its authored 60 fps clock.")
    if project.data.get("delivery", {}).get("source_transfer") != "legacy_display_gamma":
        raise PipelineError("The approved beauty source requires delivery.source_transfer=legacy_display_gamma.")
    for name, preset in project.data["quality"].items():
        if preset["width"] * 9 != preset["height"] * 16 or min(preset["width"], preset["height"]) < 32:
            raise PipelineError(f"quality.{name}: the approved composition requires 16:9 dimensions of at least 32 pixels.")
        if preset.get("image_bit_depth", 8) != 8:
            raise PipelineError("The approved source emits RGB8; a 16-bit container cannot add precision.")
    audio = project.data.get("audio", {})
    if not isinstance(audio, dict) or not audio.get("source"):
        raise PipelineError("The approved scene requires the original private recording in audio.source.")
    expected = reference(project.root)["audio_sha256"]
    if audio.get("source_sha256") != expected:
        raise PipelineError("The approved scene requires the registered original audio SHA256.")
    offset = audio.get("offset_seconds", 0)
    if isinstance(offset, bool) or not isinstance(offset, (int, float)) or not math.isfinite(offset) or offset < 0:
        raise PipelineError("Approved audio offset must be finite and nonnegative.")
    if offset + shot["end_frame_exclusive"] / 60 > 275:
        raise PipelineError("The source interval extends beyond the prepared 275-second Song 11 score.")


def verify_reference_files(root: Path, *, restored: bool = True) -> dict[str, str]:
    """Reject changed approved source or snapshots rather than silently relabeling it."""
    expected = reference(root)["source_files"]
    checked = {}
    for name, digest in expected.items():
        if not restored and name.startswith("work/"):
            continue
        path = safe_path(root, name, exists=False)
        if not path.is_file():
            raise PipelineError(f"Registered source is missing: {name}. Run video prepare for this project.")
        if file_hash(path) != digest:
            raise PipelineError(f"Registered source changed: {name}. Preserve this reference and register a new scene revision.")
        checked[name] = digest
    return checked


def prepared_identity(project: Project) -> dict:
    root = project.root
    definition = reference(root)
    source = safe_path(root, project.data["audio"]["source"])
    if file_hash(source) != definition["audio_sha256"]:
        raise PipelineError("The recording bytes do not match the approved source SHA256.")
    verify_reference_files(root)
    report = read_data(root / PREPARATION)
    if report.get("original_audio_sha256") != definition["audio_sha256"]:
        raise PipelineError("Prepared audio belongs to a different recording.")
    if report.get("source_account_commit") != definition["source_account_commit"]:
        raise PipelineError("The preparation does not identify the registered source account.")
    hashes = {}
    for name in DERIVED:
        path = root / "work/s11_full2" / name
        if not path.is_file() or report.get("analysis", {}).get(name) != file_hash(path):
            raise PipelineError(f"Prepared {name} is missing or changed. Restore a matching preparation before rendering.")
        hashes[name] = file_hash(path)
    provenance = read_data(root / "work/s11_full2/provenance.json")
    if (provenance.get("audio_sha256") != definition["audio_sha256"]
            or provenance.get("engine_commit") != definition["engine_commit"]
            or provenance.get("claude_reference_commit") != definition["people_commit"]):
        raise PipelineError("The prepared score provenance does not match the registered engines and recording.")
    module = reference_module(root)
    try:
        module.validate_analysis()
        import numpy as np
        with np.load(root / "work/s11_full2/music_fx.npz", allow_pickle=False) as music:
            if float(music["times"][-1]) < project.data["audio"].get("offset_seconds", 0) + project.seconds - 1 / project.fps:
                raise PipelineError("Music analysis does not cover the requested source interval.")
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        raise PipelineError(f"Prepared analysis is invalid: {exc}") from exc
    return {"reference": REFERENCE, "source_commit": definition["source_commit"],
            "source_account_commit": definition["source_account_commit"],
            "original_audio_sha256": definition["audio_sha256"], "derived_sha256": hashes,
            "picture_delay_seconds": PICTURE_DELAY,
            "analysis_origin": "Regenerated from the verified recording; archived original map bytes were unavailable."}


def prepare(project: Project) -> dict:
    """Reuse receipted analysis, or call the untouched original preparation once."""
    from .render import production_lock, run
    for shot in project.shots:
        validate_shot(project, shot)
    root = project.root
    if sys.platform == "darwin":
        raise PipelineError("The approved renderer and preparation require the cloud Linux workspace.")
    source = safe_path(root, project.data["audio"]["source"])
    if file_hash(source) != reference(root)["audio_sha256"]:
        raise PipelineError("The recording bytes do not match the approved source SHA256.")
    verify_reference_files(root, restored=False)
    with production_lock(root / "work/pipeline/.approved-preparation.lock"):
        if not (root / PREPARATION).is_file():
            if any((root / "work/s11_full2" / name).exists() for name in DERIVED):
                raise PipelineError("Unreceipted Song 11 analysis already exists. Preserve it separately and prepare in a clean ignored work directory.")
            run([sys.executable, str(root / "tools/promo_beauty_example/prepare.py"), "--audio", str(source)],
                cwd=root, log=root / "work/pipeline" / project.id / "prepare.log",
                env=worker_environment("p3d-approved"), timeout=7200)
        identity = prepared_identity(project)
        write_json(root / "work/pipeline" / project.id / "preparation.json", identity)
        return identity


def dependency_files(project: Project) -> list[Path]:
    prepared_identity(project)
    module = reference_module(project.root)
    names = set(module.source_hashes())
    names.update(reference(project.root)["source_files"])
    names.update((REFERENCE_FILE, PREPARATION, "work/s11_full2/provenance.json", "pipeline/approved.py"))
    return [safe_path(project.root, name) for name in sorted(names)]


def runtime_identity(root: Path) -> dict:
    module = reference_module(root)
    result = module.runtime_identity()
    result.update(reference=REFERENCE, source_commit=reference(root)["source_commit"],
                  hash_seed="0", software_threads="1")
    return result


def delivery_audio(project: Project) -> Path:
    prepared_identity(project)
    return project.root / "work/s11_full2/score.wav"


def render_job(job: dict) -> None:
    root = Path(job["repo_root"]).resolve()
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise PipelineError("Start the Python worker with PYTHONHASHSEED=0.")
    if job["video"]["fps"] != 60 or job["shot"]["scene"] != SCENE:
        raise PipelineError("This job does not match the registered frozen scene clock.")
    samples = job.get("temporal_samples")
    if type(samples) is not int or not 1 <= samples <= 4:
        raise PipelineError("temporal_samples must be an integer from 1 to 4.")
    verify_reference_files(root)
    module = reference_module(root)
    renderer = module.make_renderer(job["video"]["width"], job["video"]["height"],
                                    samples=samples, keep_grain=job["shot"].get("params", {}).get("keep_grain", False))
    output = Path(job["out_dir"])
    output.mkdir(parents=True, exist_ok=True)
    source_start = float(job["audio"].get("offset_seconds", 0))
    for frame in job["frames"]:
        if Path(job["stop_file"]).exists():
            raise PipelineError("Production stopped between frames. Completed frames remain reusable.")
        data = module.frame(renderer, frame, source_start=source_start)
        temporary = output / f"frame_{frame:06d}.partial.png"
        Image.frombytes("RGB", (renderer.w, renderer.h), data).save(temporary)
        temporary.replace(output / f"frame_{frame:06d}.png")
        print(json.dumps({"frame": frame, "reference": REFERENCE,
                          "source_seconds": max(0, source_start + frame / 60 - PICTURE_DELAY),
                          "temporal_samples": samples}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    render_job(read_data(parser.parse_args().job))


if __name__ == "__main__":
    main()
