"""Native CPU proof of a revised helping action, source scene 3 to 18 seconds.

The registered adapter uses this wrapper for one bounded comparison study.
All modifications are made to this process's renderer and recipient instance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time

from tools.concert_kit import render as base
from .response import install_response

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/concert-motion-revision"
BASE_IDENTITY = "2fa9e0fce212be765d639fbb85acf8cdb755e5a92d995dae418fa66fbd7eae6e"
AUDIO_IDENTITY = "0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b"
SOURCE_START = 3.0
SOURCE_END = 18.0
DURATION = SOURCE_END - SOURCE_START
FPS = 60
FRAME_COUNT = 900
SOURCE_CUTS = (3.0, 6.9, 12.0)
CUTS = (3.9, 9.0)
COLOR_CONTRACT = dict(base.COLOR_CONTRACT)
RIG_SPEC = {
    "contact": {"times": [3.0, 12.0], "active_until": 6.9,
                "positions": [[1.6, 1.45, 5.8], [1.1, 1.55, 6.0]],
                "targets": [[-.18, 1.0, 1.52], [0.0, 1.05, 1.85]], "fov": 35, "aperture": .009},
    "action": {"times": [6.9, 12.0], "positions": [[-3.2, 1.65, 5.1], [-4.3, 1.75, 4.0]],
               "targets": [[.002, 1.02, 1.944], [.05, 1.02, 2.5]], "fov": 35, "aperture": .009},
    "reveal": {"times": [12.0, 18.0], "positions": [[-6.5, 3.0, 5.2], [-10.0, 3.8, 4.8]],
               "targets": [[-1.1, 1.5, .3], [-1.2, 2.2, -.5]], "fov": 42, "aperture": .008},
    "ease": "smooth", "blend": 0, "shutter": .30, "handheld": 0, "near": .1}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_hashes():
    files = base.source_hashes()
    actual = identity(files)
    if actual != BASE_IDENTITY:
        raise RuntimeError(f"Frozen kit identity mismatch: {actual}")
    files.update({str(p.relative_to(ROOT)): digest(p)
                  for p in sorted((ROOT / "tools/concert_motion_revision").glob("*.py"))})
    return files


def make_renderer(width=1920, height=1080, temporal_samples=2, fps=60):
    if fps != FPS:
        raise ValueError("This action comparison is authored for native 60 fps")
    sources = source_hashes()
    # Select a distinct complete cache root before the base factory sets any
    # environment paths or imports a scene. Include this revision in its path.
    base.WORK = WORK / "cache" / identity(sources)[:20]
    renderer = base.make_renderer(width, height, temporal_samples, fps)
    import songs.consideration as scene
    from p3d.camera import Rig, dolly
    renderer.revision_response = install_response(scene.pair())
    moves = []
    for name in ("contact", "action", "reveal"):
        spec = RIG_SPEC[name]
        moves.append(dolly(*spec["positions"], *spec["times"], look=spec["targets"],
                           fov=spec["fov"], aperture=spec["aperture"], ease="smooth", blend=0))
    renderer.p3d.rig = Rig(moves, blend=0, shutter=.30, handheld=0, near=.1)
    renderer.p3d._frame = None
    renderer.kit_cuts = SOURCE_CUTS
    renderer.revision_sources = sources
    renderer.revision_pair = scene.pair()
    return renderer


def source_frame(renderer, source_index):
    return base.frame(renderer, int(source_index), fps=FPS)


def fonts_path():
    return base.fonts_path()


def frame(renderer, output_index, fps=60):
    if int(fps) != FPS:
        raise ValueError("Frame rate must match the authored native 60 fps")
    if not 0 <= int(output_index) < FRAME_COUNT:
        raise ValueError("Output frame is outside the 15-second proof")
    return source_frame(renderer, round(SOURCE_START * FPS) + int(output_index))


def atomic_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(path)


def render_stills(times, out):
    from PIL import Image
    out = out.resolve()
    began = time.monotonic()
    renderer = make_renderer()
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for requested in times:
        source_index = round(requested * FPS)
        stamp = source_index / FPS
        before = time.monotonic()
        path = out / f"source-{source_index:06d}.png"
        Image.frombytes("RGB", (1920, 1080), source_frame(renderer, source_index)).save(path)
        camera = renderer.p3d.rig.state(stamp, 16 / 9)
        record = {"source_frame": source_index, "source_seconds": stamp,
                  "output_seconds": stamp - SOURCE_START, "path": str(path.relative_to(ROOT)),
                  "sha256": digest(path), "width": 1920, "height": 1080,
                  "seconds": time.monotonic() - before,
                  "camera": {"position": camera.pos.tolist(), "target": camera.target.tolist(), "fov": camera.fov}}
        records.append(record)
        print(json.dumps(record), flush=True)
    if source_hashes() != renderer.revision_sources:
        raise RuntimeError("Picture source changed during native probes")
    atomic_json(out / "receipt.json", {"source_identity": identity(renderer.revision_sources),
        "base_identity": BASE_IDENTITY, "sources": renderer.revision_sources, "color": COLOR_CONTRACT,
        "fps": FPS, "temporal_samples": 2, "records": records,
        "elapsed_seconds": time.monotonic() - began})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stills", required=True, help="Comma-separated original scene times")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    render_stills([float(t) for t in args.stills.split(",")], args.out)


if __name__ == "__main__":
    main()
