"""Prepare the original verified recording and pinned production assets."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_AUDIO = "70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True, type=Path, help="Original private Song 11 MP3")
    args = parser.parse_args()
    source = args.audio.resolve()
    if sys.platform == "darwin":
        parser.error("Use the cloud CPU environment.")
    if not source.is_file() or digest(source) != EXPECTED_AUDIO:
        parser.error("The source recording does not match the production checksum.")
    for commit in ("d928ff9eafe02ac3150f0c646bdcc497fe5a7278", "f43f4514e4bc42dc25166e90160d98219f5a0db4"):
        check = subprocess.run(["git", "cat-file", "-e", commit + "^{commit}"], cwd=ROOT, capture_output=True)
        if check.returncode:
            raise RuntimeError(f"Fetch the original commit first: git fetch origin {commit}")
    env = dict(os.environ, S11_AUDIO=str(source), PYTHONHASHSEED="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
               LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1")
    subprocess.run([sys.executable, str(ROOT / "tools/s11_full2/s11_prepare.py")], cwd=ROOT, env=env, check=True)
    music = ROOT / "work/s11_full2/music_fx.npz"
    if not music.is_file():
        analysis_env = dict(env, S11_AUDIO=str(ROOT / "work/s11_full2/score.wav"))
        subprocess.run([sys.executable, str(ROOT / "tools/s11_full2/s11_music_map.py")], cwd=ROOT,
                       env=analysis_env, check=True)
    report = {"original_audio_sha256": EXPECTED_AUDIO,
              "analysis": {name: digest(ROOT / "work/s11_full2" / name)
                           for name in ("features.npz", "music_fx.npz", "score.wav")},
              "provenance": "Analysis regenerated from the verified original recording using the pinned project scripts.",
              "source_account_commit": "34f835206dcb26cfa0bd7e321171d3d224e3aa7d",
              "completed_s11_master_inspected": False,
              "timing": "Authored absolute cue times and the original 0.1 second picture delay are retained."}
    destination = ROOT / "work/promo-beauty-rebuild"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "preparation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
